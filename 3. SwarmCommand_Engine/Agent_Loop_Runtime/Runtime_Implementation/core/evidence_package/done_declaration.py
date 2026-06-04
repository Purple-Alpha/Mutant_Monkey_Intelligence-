"""Done-declaration evaluation for the Cyber Insurance Evidence Package.

Implements the ``declaration`` component: evaluate the 15 Done Criteria
(deep-dive §11) against a generated package and emit ``done_declaration.json``
**only when all 15 hold**.

Pass 1 boundary: there is no live Grok package audit and no operator signature
yet, so criteria 11 (Grok audit run), 12 (Grok findings resolved), and 14
(operator signature) are structurally unmet. A Pass-1 package therefore
evaluates to **not done** and no ``done_declaration.json`` is written — which
is the correct, honest state. This component makes that explicit and records
exactly which criteria a future Grok-audit + operator-signature step must close.

Criteria 1-10 are read from the §7 gate results; 13 from the package drift
directory; 15 from supplied test-plan evidence. A package is done iff every one
of the 15 is met (the criteria fail closed).
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

# Criterion number -> the §7 gate whose pass satisfies it. Criteria 6 and 9
# both rely on the redaction gate (no secrets/raw bodies; no cross-tenant ids).
GATE_BACKED_CRITERIA: Mapping[int, str] = {
    1: "scope_boundary",
    2: "claim_validation",
    3: "broken_link",
    4: "stale_evidence",
    5: "forbidden_language",
    6: "redaction",
    7: "vocabulary_translation",
    8: "signed_provenance",
    9: "redaction",
    10: "audit_packet_coverage",
}

CRITERION_LABELS: Mapping[int, str] = {
    1: "boundary statement present",
    2: "every claim has evidence",
    3: "every source path resolves",
    4: "no stale evidence",
    5: "no forbidden language",
    6: "redaction sweep passes",
    7: "vocabulary translation applied",
    8: "signed provenance complete",
    9: "tenant isolation invariants hold",
    10: "audit packet covers touched files",
    11: "Grok audit run (after generation, on the full packet)",
    12: "Grok findings resolved",
    13: "no blocking drift incidents open",
    14: "operator signature",
    15: "v1 test plan executed end to end",
}

ALL_CRITERIA = tuple(range(1, 16))


@dataclass(frozen=True)
class DoneEvaluation:
    """Result of evaluating the 15 Done Criteria against one package."""

    criteria_met: tuple[int, ...]
    criteria_unmet: tuple[tuple[int, str], ...]

    @property
    def is_done(self) -> bool:
        return set(self.criteria_met) == set(ALL_CRITERIA)

    @property
    def blocking_for_done(self) -> tuple[int, ...]:
        return tuple(number for number, _reason in self.criteria_unmet)


def evaluate_done_criteria(
    *,
    gate_results: Sequence[Any],
    drift_dir: Path | None = None,
    grok_audit_output: str | None = None,
    grok_findings_resolved: bool = False,
    operator_signature_evidence_id: str | None = None,
    test_plan_evidence_id: str | None = None,
) -> DoneEvaluation:
    """Evaluate all 15 Done Criteria. Fails closed: anything unproven is unmet."""

    by_gate = {result.gate: result for result in gate_results}
    met: list[int] = []
    unmet: list[tuple[int, str]] = []

    for number in ALL_CRITERIA:
        ok, reason = _evaluate_one(
            number,
            by_gate=by_gate,
            drift_dir=drift_dir,
            grok_audit_output=grok_audit_output,
            grok_findings_resolved=grok_findings_resolved,
            operator_signature_evidence_id=operator_signature_evidence_id,
            test_plan_evidence_id=test_plan_evidence_id,
        )
        if ok:
            met.append(number)
        else:
            unmet.append((number, reason))

    return DoneEvaluation(criteria_met=tuple(met), criteria_unmet=tuple(unmet))


def _evaluate_one(
    number: int,
    *,
    by_gate: Mapping[str, Any],
    drift_dir: Path | None,
    grok_audit_output: str | None,
    grok_findings_resolved: bool,
    operator_signature_evidence_id: str | None,
    test_plan_evidence_id: str | None,
) -> tuple[bool, str]:
    if number in GATE_BACKED_CRITERIA:
        gate_name = GATE_BACKED_CRITERIA[number]
        result = by_gate.get(gate_name)
        if result is None:
            return False, f"gate '{gate_name}' did not run"
        if not result.passed:
            return False, f"gate '{gate_name}' failed"
        return True, ""
    if number == 11:
        if not grok_audit_output:
            return False, "no Grok package-audit output (Pass 1 defers the live Grok audit)"
        return True, ""
    if number == 12:
        if not grok_audit_output:
            return False, "Grok audit not run, so findings cannot be resolved"
        if not grok_findings_resolved:
            return False, "Grok findings not all resolved/accepted"
        return True, ""
    if number == 13:
        blocking = _open_blocking_incidents(drift_dir)
        if blocking:
            return False, f"{len(blocking)} blocking drift incident(s) open"
        return True, ""
    if number == 14:
        if not operator_signature_evidence_id:
            return False, "no operator signature evidence record (Pass 1 has no signature)"
        return True, ""
    if number == 15:
        if not test_plan_evidence_id:
            return False, "no v1 test-plan evidence supplied"
        return True, ""
    return False, "unknown criterion"


def _open_blocking_incidents(drift_dir: Path | None) -> list[str]:
    if drift_dir is None or not drift_dir.exists():
        return []
    blocking: list[str] = []
    for path in sorted(drift_dir.glob("drift_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            blocking.append(path.name)
            continue
        severity = str(payload.get("severity", "")).lower()
        status = str(payload.get("status", "")).lower()
        if severity == "blocking" and status not in {"resolved", "accepted"}:
            blocking.append(path.name)
    return blocking


def build_done_evaluation_record(
    evaluation: DoneEvaluation,
    *,
    package_id: str,
    package_version: str,
    tenant_id: str,
    generated_at: datetime,
) -> dict[str, Any]:
    """Build the manifest-embeddable done-evaluation block (always written)."""

    return {
        "is_done": evaluation.is_done,
        "done_declaration_emitted": evaluation.is_done,
        "criteria_met": list(evaluation.criteria_met),
        "criteria_unmet": [
            {"criterion": number, "label": CRITERION_LABELS.get(number, ""), "reason": reason}
            for number, reason in evaluation.criteria_unmet
        ],
        "blocking_for_done": list(evaluation.blocking_for_done),
    }


def emit_done_declaration_if_done(
    evaluation: DoneEvaluation,
    *,
    package_dir: Path,
    package_id: str,
    package_version: str,
    tenant_id: str,
    generated_at: datetime,
    now: datetime,
    grok_audit_output: str | None,
    drift_incidents_resolved: Sequence[str] = (),
    operator_signature_evidence_id: str | None = None,
) -> Path | None:
    """Write ``done_declaration.json`` only when all 15 criteria hold.

    Returns the path when written, or None (the Pass-1 case: not done, so no
    declaration is emitted — a missing/partial declaration means not done).
    """

    if not evaluation.is_done:
        return None

    declaration = {
        "package_id": package_id,
        "package_version": package_version,
        "tenant_id": tenant_id,
        "generated_at": generated_at.isoformat(),
        "done_at": _aware_utc(now).isoformat(),
        "criteria_met": list(evaluation.criteria_met),
        "grok_audit_output": grok_audit_output,
        "drift_incidents_resolved": list(drift_incidents_resolved),
        "operator_signature_evidence_id": operator_signature_evidence_id,
    }
    declaration_path = package_dir / "done_declaration.json"
    _atomic_write_json(declaration_path, declaration)
    return declaration_path


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "wb") as handle:
        handle.write(content)
    Path(temp_name).replace(path)
