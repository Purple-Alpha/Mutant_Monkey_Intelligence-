"""Stage 9 — Grok package audit (deep-dive §10 / impl spec §10).

This is the *separate, explicitly-invoked* audit step (operator decision
2026-06-04, Option B in `_Stage9_Grok_Package_Audit_Consequence_Matrix.md`).
It is deliberately NOT wired into ``generate_package_from_test_plan``:
generation stays offline and deterministic; the live external-model call lives
here behind an explicit invocation, mirroring ``audit_tools/complete_gate.py``.

Grok is a **negative-feedback auditor**, not an approval authority (deep-dive
§10). It receives the assembled audit packet (every file touched during
generation, §10 coverage rule) plus the contract documents, and is asked only
to identify deviations. Zero deviations on a complete packet is the compliant
state. Every deviation becomes a Drift Incident Report that must be resolved or
operator-accepted before the package is done (Done Criteria 11/12).

v1 boundary: **synthetic / test packages only.** Submitting real customer
package content to an external model is a separate controls decision with its
own spec (see the §Outcome review trigger in the stage-9 consequence matrix).

The Grok client is injected (``GrokClient`` = ``Callable[[str], str]``) so the
audit logic is fully unit-testable without a network call. ``make_xai_client``
provides a thin real adapter for live runs.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

GrokClient = Callable[[str], str]

# Grok's audit output must end with this machine-readable verdict line, mirroring
# the convention enforced by audit_tools/complete_gate.py.
GATE_SUMMARY_RE = re.compile(
    r"^GATE_SUMMARY:\s*blocking\s*=\s*(\d+)\s+warnings\s*=\s*(\d+)\s*$",
    re.MULTILINE,
)
DEVIATION_LINE_RE = re.compile(r"^(BLOCKING|WARNING):\s*(.+?)\s*$", re.MULTILINE)

PACKAGE_AUDIT_PROMPT = (
    "You are a negative-feedback auditor for a Cyber Insurance Evidence "
    "Package. You are NOT an approval authority. Do not score, approve, or "
    "assess product-market fit. Compare the package contents against the "
    "signed deep-dive, the seven VISION non-negotiables, the boundary "
    "statement, the forbidden-language list, and the vocabulary-translation "
    "list, and identify ONLY deviations. For each deviation output a line "
    "starting with `BLOCKING:` or `WARNING:` and a one-line summary. End your "
    "output with exactly one line:\n"
    "    GATE_SUMMARY: blocking=<N> warnings=<M>\n"
    "If there are no deviations on this complete packet, output "
    "`GATE_SUMMARY: blocking=0 warnings=0`."
)


class PackageAuditError(Exception):
    """Raised when the package audit cannot be completed or parsed."""


@dataclass(frozen=True)
class PackageAuditDeviation:
    severity: str  # "blocking" | "warning"
    summary: str


@dataclass(frozen=True)
class PackageAuditResult:
    package_id: str
    submitted_at: str
    grok_output_path: str
    packet_hash: str
    blocking_count: int
    warning_count: int
    deviations: tuple[PackageAuditDeviation, ...]
    drift_incident_paths: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return self.blocking_count == 0 and self.warning_count == 0


def build_audit_payload(
    *,
    audit_packet_dir: Path,
    contract_files: Sequence[Path],
) -> str:
    """Assemble the Grok audit payload from the persisted packet + contracts.

    Reads the ``audit_packet.json`` manifest and every content chunk written by
    ``audit_packet.write_audit_packet``. The coverage rule is enforced upstream
    at assembly time; this step submits the packet whole and never re-scopes it.
    """

    manifest_path = audit_packet_dir / "audit_packet.json"
    if not manifest_path.exists():
        raise PackageAuditError(
            f"audit packet manifest not found at {manifest_path}; assemble the "
            "packet (stage 8) before auditing"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    sections: list[str] = []
    sections.append("=== AUDIT PACKET MANIFEST ===")
    sections.append(json.dumps(manifest, indent=2, sort_keys=True))

    sections.append("=== AUDIT PACKET CONTENTS ===")
    for chunk_rel in manifest.get("content_chunks", []):
        chunk_path = audit_packet_dir / chunk_rel
        if not chunk_path.exists():
            raise PackageAuditError(
                f"audit packet references missing content chunk {chunk_rel}"
            )
        sections.append(f"--- chunk: {chunk_rel} ---")
        sections.append(chunk_path.read_text(encoding="utf-8", errors="replace"))

    sections.append("=== CONTRACT DOCUMENTS ===")
    for contract in contract_files:
        if not contract.exists():
            raise PackageAuditError(f"contract document not found: {contract}")
        sections.append(f"--- contract: {contract.name} ---")
        sections.append(contract.read_text(encoding="utf-8", errors="replace"))

    return "\n".join(sections)


def parse_audit_output(content: str) -> tuple[int, int, tuple[PackageAuditDeviation, ...]]:
    """Parse Grok output into (blocking_count, warning_count, deviations)."""

    matches = list(GATE_SUMMARY_RE.finditer(content))
    if not matches:
        raise PackageAuditError(
            "grok output missing the `GATE_SUMMARY: blocking=N warnings=M` line"
        )
    if len(matches) > 1:
        raise PackageAuditError(
            f"grok output has {len(matches)} GATE_SUMMARY lines; expected exactly one"
        )
    blocking = int(matches[0].group(1))
    warning = int(matches[0].group(2))

    deviations = tuple(
        PackageAuditDeviation(
            severity="blocking" if line.group(1) == "BLOCKING" else "warning",
            summary=line.group(2),
        )
        for line in DEVIATION_LINE_RE.finditer(content)
    )
    return blocking, warning, deviations


def audit_package(
    *,
    package_id: str,
    tenant_id: str,
    package_dir: Path,
    audit_packet_dir: Path,
    contract_files: Sequence[Path],
    grok_client: GrokClient,
    audit_outputs_dir: Path,
    now: datetime | None = None,
) -> PackageAuditResult:
    """Run the explicit Grok package audit and record drift incidents.

    Submits the assembled packet to ``grok_client`` (injected so tests need no
    network), saves the raw output under ``audit_outputs_dir``, parses the
    verdict, and writes one Drift Incident Report per deviation into
    ``package_dir/drift``.
    """

    submitted_at = _aware_utc(now or datetime.now(timezone.utc))
    manifest_path = audit_packet_dir / "audit_packet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    packet_hash = str(manifest.get("packet_hash", ""))

    payload = build_audit_payload(
        audit_packet_dir=audit_packet_dir,
        contract_files=contract_files,
    )
    content = grok_client(payload)
    if not isinstance(content, str) or not content.strip():
        raise PackageAuditError("grok client returned empty output")

    output_path = _save_grok_output(
        content,
        audit_outputs_dir=audit_outputs_dir,
        submitted_at=submitted_at,
    )

    blocking, warning, deviations = parse_audit_output(content)

    drift_dir = package_dir / "drift"
    drift_paths = _write_drift_incidents(
        deviations,
        drift_dir=drift_dir,
        package_id=package_id,
        tenant_id=tenant_id,
        submitted_at=submitted_at,
        grok_output_path=output_path,
    )

    return PackageAuditResult(
        package_id=package_id,
        submitted_at=submitted_at.isoformat(),
        grok_output_path=str(output_path),
        packet_hash=packet_hash,
        blocking_count=blocking,
        warning_count=warning,
        deviations=deviations,
        drift_incident_paths=tuple(str(path) for path in drift_paths),
    )


def make_xai_client(*, api_key: str, model: str = "grok-4") -> GrokClient:
    """Thin real xAI adapter (used for live runs only; tests inject a fake).

    Kept minimal and free of project-specific state so the testable core
    (``audit_package``) never depends on the network.
    """

    import urllib.request

    endpoint = "https://api.x.ai/v1/chat/completions"

    def _client(payload: str) -> str:
        body = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": PACKAGE_AUDIT_PROMPT},
                {"role": "user", "content": payload},
            ],
        }
        request = urllib.request.Request(
            url=endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        return parsed["choices"][0]["message"]["content"]

    return _client


def _write_drift_incidents(
    deviations: Sequence[PackageAuditDeviation],
    *,
    drift_dir: Path,
    package_id: str,
    tenant_id: str,
    submitted_at: datetime,
    grok_output_path: Path,
) -> list[Path]:
    paths: list[Path] = []
    for index, deviation in enumerate(deviations, start=1):
        incident = {
            "drift_id": f"drift_pkgaudit_{submitted_at.strftime('%Y%m%dT%H%M%SZ')}_{index:02d}",
            "package_id": package_id,
            "tenant_id": tenant_id,
            "source": "grok_package_audit",
            "finding_type": "package_audit_deviation",
            "severity": deviation.severity,
            "status": "open",
            "summary": deviation.summary,
            "grok_audit_output": str(grok_output_path),
            "detected_at": submitted_at.isoformat(),
            "operator_resolution_note": None,
        }
        path = drift_dir / f"{incident['drift_id']}.json"
        _atomic_write_json(path, incident)
        paths.append(path)
    return paths


def _save_grok_output(
    content: str,
    *,
    audit_outputs_dir: Path,
    submitted_at: datetime,
) -> Path:
    audit_outputs_dir.mkdir(parents=True, exist_ok=True)
    stamp = submitted_at.strftime("%Y%m%dT%H%M%SZ")
    path = audit_outputs_dir / f"cyber_insurance_evidence_package_{stamp}.md"
    path.write_text(content, encoding="utf-8")
    return path


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "wb") as handle:
        handle.write(data)
    Path(temp_name).replace(path)
