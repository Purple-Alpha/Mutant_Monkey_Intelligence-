"""Internal Cyber Insurance Evidence Package generator.

Pass 1 is Markdown-first and internal-only. It assembles the already-executed
section 14 test-plan artifacts into a package directory, renders a Markdown
companion, writes a manifest, creates a deterministic zip bundle, and runs the
local gate library. It does not render PDF, call Grok, emit a done declaration,
or change runtime detection/scoring behavior.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from . import audit_packet as audit_packet_mod
from . import done_declaration as done_declaration_mod
from . import gates

CONTRACT_DOCUMENTS: tuple[str, ...] = (
    "VISION.md",
    "4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md",
    "4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Implementation_Deep_Dive.md",
)

PACKAGE_VERSION = "v1"
DEFAULT_MODEL_IDENTITY = "grok-4"
DEFAULT_MODEL_TEMPERATURE = 0
DEFAULT_RENDER_TOOLCHAIN = "markdown-bundle-v1"
DEFAULT_FRAUD_CONTRAST_ID = "vf-001"
DEFAULT_LEGIT_CONTRAST_ID = "legit-vendor-contrast"

RECORD_SPECS: Mapping[str, tuple[str, str, str]] = {
    "detection": ("detection.json", "detection_evidence", "cybins-v1-detection-001"),
    "verification": ("verification.json", "scoring_explanation", "cybins-v1-verification-001"),
    "evidence": ("evidence.json", "operational_artifact", "cybins-v1-evidence-001"),
    "audit_trail": ("audit_trail.json", "policy_change_control", "cybins-v1-audit-001"),
    "outcome_documentation": (
        "outcome_documentation.md",
        "operational_artifact",
        "cybins-v1-outcome-001",
    ),
}


@dataclass(frozen=True)
class EvidencePackageResult:
    package_id: str
    package_dir: Path
    markdown_bundle_path: Path
    manifest_path: Path
    package_markdown_path: Path
    gate_results: tuple[gates.GateResult, ...]
    audit_packet_dir: Path
    audit_packet_manifest_path: Path
    audit_packet_coverage_complete: bool
    is_done: bool
    done_declaration_path: Path | None

    @property
    def gates_passed(self) -> bool:
        return all(result.passed for result in self.gate_results)


def generate_package_from_test_plan(
    *,
    source_dir: Path,
    output_root: Path,
    tenant_id: str,
    trigger: Literal["quarterly", "on_demand", "annual"] = "on_demand",
    now: datetime | None = None,
    model_identity: str = DEFAULT_MODEL_IDENTITY,
    model_temperature: int = DEFAULT_MODEL_TEMPERATURE,
    render_toolchain: str = DEFAULT_RENDER_TOOLCHAIN,
    fraud_contrast_id: str = DEFAULT_FRAUD_CONTRAST_ID,
    legit_contrast_id: str = DEFAULT_LEGIT_CONTRAST_ID,
) -> EvidencePackageResult:
    """Generate a deterministic internal Markdown package from section 14 artifacts."""

    generated_at = _aware_utc(now)
    source_dir = source_dir.resolve()
    output_root = output_root.resolve()
    package_id = f"{_slug(tenant_id)}-{generated_at.strftime('%Y%m%dT%H%M%SZ')}"
    package_dir = output_root / package_id
    if package_dir.exists():
        shutil.rmtree(package_dir)
    records_dir = package_dir / "records"
    rendered_dir = package_dir / "rendered"
    gates_dir = package_dir / "gates"
    for directory in (records_dir, rendered_dir, gates_dir):
        directory.mkdir(parents=True, exist_ok=True)

    touched_files: set[Path] = set()
    records: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []

    for stage, (filename, evidence_category, record_id) in RECORD_SPECS.items():
        source_path = source_dir / filename
        touched_files.add(source_path)
        record = _build_record(
            stage=stage,
            record_id=record_id,
            evidence_category=evidence_category,
            source_path=source_path,
            tenant_id=tenant_id,
            verified_at=generated_at,
        )
        records.append(record)
        claims.append(
            {
                "claim_id": f"claim-{stage}",
                "record_refs": [record_id],
                "source_artifact_paths": [record["source_artifact_path"]],
            }
        )
        record_path = records_dir / f"{stage}.json"
        _atomic_write_json(record_path, record)
        touched_files.add(record_path)

    package_markdown = _render_markdown(
        package_id=package_id,
        tenant_id=tenant_id,
        trigger=trigger,
        generated_at=generated_at,
        records=records,
        model_identity=model_identity,
        model_temperature=model_temperature,
        fraud_contrast_id=fraud_contrast_id,
        legit_contrast_id=legit_contrast_id,
    )
    package_markdown_path = rendered_dir / "package.md"
    readme_path = rendered_dir / "README.md"
    _atomic_write_text(package_markdown_path, package_markdown)
    _atomic_write_text(readme_path, _render_readme())
    touched_files.update({package_markdown_path, readme_path})

    gate_results = run_package_gates(
        package_dir=package_dir,
        workspace_root=_repo_root(),
        records=records,
        claims=claims,
        rendered_markdown=package_markdown,
        audit_packet_files=tuple(touched_files) + tuple(record["source_artifact_path"] for record in records),
        now=generated_at,
    )
    for result in gate_results:
        gate_path = gates_dir / f"gate_{result.gate}.json"
        _atomic_write_json(gate_path, _gate_result_to_dict(result))
        touched_files.add(gate_path)

    # Stage 8 (spec section 3 / section 10): assemble the coverage-complete Grok
    # audit packet from every file touched during stages 1-7 (reads + writes)
    # plus the contract documents. Pass 1 assembles and persists; it does not
    # submit to Grok.
    read_files = [source_dir / filename for filename, _category, _record_id in RECORD_SPECS.values()]
    read_set = {path.resolve() for path in read_files}
    written_files = sorted(
        (path for path in touched_files if path.resolve() not in read_set),
        key=lambda path: path.as_posix(),
    )
    contract_files = [_repo_root() / relative for relative in CONTRACT_DOCUMENTS]
    audit_packet = audit_packet_mod.assemble_audit_packet(
        package_id=package_id,
        read_files=read_files,
        written_files=written_files,
        contract_files=contract_files,
        workspace_root=_repo_root(),
    )
    audit_packet_dir = output_root / f"{package_id}__audit_packet"
    audit_packet_summary = audit_packet_mod.write_audit_packet(
        audit_packet,
        audit_dir=audit_packet_dir,
        workspace_root=_repo_root(),
    )

    # Stage 10 (spec §11 / deep-dive §11): evaluate the 15 Done Criteria. Pass 1
    # has no live Grok package audit (criteria 11/12) and no operator signature
    # (criterion 14), so a Pass-1 package correctly evaluates to NOT done and no
    # done_declaration.json is emitted.
    drift_dir = package_dir / "drift"
    done_evaluation = done_declaration_mod.evaluate_done_criteria(
        gate_results=gate_results,
        drift_dir=drift_dir,
        grok_audit_output=None,
        operator_signature_evidence_id=None,
        test_plan_evidence_id=None,
    )
    done_evaluation_record = done_declaration_mod.build_done_evaluation_record(
        done_evaluation,
        package_id=package_id,
        package_version=PACKAGE_VERSION,
        tenant_id=tenant_id,
        generated_at=generated_at,
    )

    manifest_path = package_dir / "manifest.json"
    manifest = _build_manifest(
        package_id=package_id,
        tenant_id=tenant_id,
        trigger=trigger,
        generated_at=generated_at,
        package_dir=package_dir,
        model_identity=model_identity,
        model_temperature=model_temperature,
        render_toolchain=render_toolchain,
        fraud_contrast_id=fraud_contrast_id,
        legit_contrast_id=legit_contrast_id,
        audit_packet_files=touched_files | {manifest_path},
        audit_packet=audit_packet,
        audit_packet_manifest_path=audit_packet_summary["manifest_path"],
        done_evaluation_record=done_evaluation_record,
    )
    _atomic_write_json(manifest_path, manifest)
    touched_files.add(manifest_path)

    done_declaration_path = done_declaration_mod.emit_done_declaration_if_done(
        done_evaluation,
        package_dir=package_dir,
        package_id=package_id,
        package_version=PACKAGE_VERSION,
        tenant_id=tenant_id,
        generated_at=generated_at,
        now=generated_at,
        grok_audit_output=None,
    )
    if done_declaration_path is not None:
        touched_files.add(done_declaration_path)

    markdown_bundle_path = package_dir / f"{package_id}_markdown_bundle.zip"
    _write_bundle(
        package_dir=package_dir,
        bundle_path=markdown_bundle_path,
        include_paths=[
            manifest_path,
            readme_path,
            package_markdown_path,
            *(records_dir / f"{stage}.json" for stage in RECORD_SPECS),
            *(gates_dir / f"gate_{result.gate}.json" for result in gate_results),
        ],
    )

    return EvidencePackageResult(
        package_id=package_id,
        package_dir=package_dir,
        markdown_bundle_path=markdown_bundle_path,
        manifest_path=manifest_path,
        package_markdown_path=package_markdown_path,
        gate_results=gate_results,
        audit_packet_dir=audit_packet_dir,
        audit_packet_manifest_path=audit_packet_summary["manifest_path"],
        audit_packet_coverage_complete=audit_packet.coverage_complete,
        is_done=done_evaluation.is_done,
        done_declaration_path=done_declaration_path,
    )


def run_package_gates(
    *,
    package_dir: Path,
    workspace_root: Path,
    records: Sequence[Mapping[str, Any]] | None = None,
    claims: Sequence[Mapping[str, Any]] | None = None,
    rendered_markdown: str | None = None,
    audit_packet_files: Sequence[str | Path] = (),
    now: datetime | None = None,
) -> tuple[gates.GateResult, ...]:
    """Run the nine section 7 gates against one generated package."""

    package_records = list(records) if records is not None else _load_records(package_dir)
    package_claims = list(claims) if claims is not None else _claims_from_records(package_records)
    markdown = (
        rendered_markdown
        if rendered_markdown is not None
        else (package_dir / "rendered" / "package.md").read_text(encoding="utf-8")
    )
    touched = [str(path) for path in package_dir.rglob("*") if path.is_file()]
    touched.extend(str(record.get("source_artifact_path", "")) for record in package_records)
    packet_files = list(audit_packet_files) if audit_packet_files else touched

    return (
        gates.run_broken_link_gate(package_records, workspace_root=workspace_root),
        gates.run_signed_provenance_gate(package_records, workspace_root=workspace_root),
        gates.run_stale_evidence_gate(
            package_records,
            now=_aware_utc(now),
            workspace_root=workspace_root,
        ),
        gates.run_claim_validation_gate(package_claims, package_records),
        gates.run_redaction_gate(
            package_records,
            rendered_texts=[markdown],
            tenant_id=_tenant_id(package_records),
            known_tenant_ids=sorted({str(record.get("tenant_id")) for record in package_records}),
        ),
        gates.run_forbidden_language_gate(_forbidden_surfaces(markdown)),
        gates.run_vocabulary_translation_gate([{"path": "rendered/package.md", "text": markdown}]),
        gates.run_scope_boundary_gate(markdown),
        gates.run_audit_packet_coverage_gate(touched, packet_files),
    )


def _forbidden_surfaces(markdown: str) -> list[dict[str, Any]]:
    return [
        {
            "path": f"rendered/package.md:{index}",
            "text": line,
            "allowed_context": gates.BOUNDARY_STATEMENT in line,
        }
        for index, line in enumerate(markdown.splitlines(), start=1)
        if line.strip()
    ]


def _build_record(
    *,
    stage: str,
    record_id: str,
    evidence_category: str,
    source_path: Path,
    tenant_id: str,
    verified_at: datetime,
) -> dict[str, Any]:
    if not source_path.exists():
        raise FileNotFoundError(f"source artifact missing: {source_path}")
    source_payload = _load_source_payload(source_path)
    source_artifact_path = _repo_relative(source_path)
    record: dict[str, Any] = {
        "record_id": record_id,
        "record_type": f"cyber_insurance_v1_{stage}_record",
        "tenant_id": tenant_id,
        "evidence_category": evidence_category,
        "source_artifact_path": source_artifact_path,
        "verification_command": f"verify_source_artifact_exists:{source_artifact_path}",
        "last_verified_at": verified_at.isoformat(),
        "result": "pass",
        "content_hash": f"sha256:{_file_sha256(source_path)}",
        "scope_limitations": (
            "Email-fraud and inbox-layer MDR controls only. Does not cover MFA, "
            "EDR, backups, IR, patch management."
        ),
        "source_summary": _source_summary(stage, source_payload),
    }
    if stage == "audit_trail":
        signed_artifact = _signed_artifact_path(source_payload, source_path)
        record["signed_by"] = _repo_relative(signed_artifact)
        if isinstance(source_payload, Mapping) and source_payload.get("signed_by"):
            record["signed_by_label"] = source_payload["signed_by"]
    if stage == "outcome_documentation":
        record["rendered_outcome_heading"] = (
            "Vendor invoice review — payment change reviewed before action."
        )
    return record


def _render_markdown(
    *,
    package_id: str,
    tenant_id: str,
    trigger: str,
    generated_at: datetime,
    records: Sequence[Mapping[str, Any]],
    model_identity: str,
    model_temperature: int,
    fraud_contrast_id: str,
    legit_contrast_id: str,
) -> str:
    lines = [
        "# Cyber Insurance Evidence Package - Internal Markdown Bundle",
        "",
        f"Package ID: `{package_id}`",
        f"Tenant: `{tenant_id}`",
        f"Generated at: `{generated_at.isoformat()}`",
        f"Trigger: `{trigger}`",
        "",
        f"> {gates.BOUNDARY_STATEMENT}",
        "",
        "## Evidence Records",
        "",
        "| Record | Category | Source | Result |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `{record['record_id']}` | `{record['evidence_category']}` | "
            f"`{record['source_artifact_path']}` | `{record['result']}` |"
        )
    lines.extend(
        [
            "",
            "## Two-Shot Evidence-Explanation Format",
            "",
            (
                "Rendered explanations use the signed implementation spec's two-shot "
                "evidence-explanation format with contrast rows "
                f"`{fraud_contrast_id}` and `{legit_contrast_id}`."
            ),
            f"Model pin: `{model_identity}` at temperature `{model_temperature}`.",
            "",
            "## Result Boundary",
            "",
            (
                "This internal package records traceability for a fictional Stage A "
                "test-plan fixture. It does not claim external approval, coverage "
                "impact, loss avoidance, or real-world attack prevention."
            ),
            "",
            "## MSP Retainer Summary",
            "",
            (
                "NorthStar provides an auditable evidence bundle for the email-fraud "
                "and inbox-layer MDR control surface only; the MSP remains responsible "
                "for evidencing all other security controls."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _render_readme() -> str:
    return "\n".join(
        [
            "# Cyber Insurance Evidence Package Bundle",
            "",
            "This Markdown bundle is an internal Pass 1 artifact.",
            "",
            "- `records/` contains the structured evidence records.",
            "- `rendered/package.md` is the Markdown companion surface.",
            "- `manifest.json` pins hashes, model settings, and audit-packet coverage.",
            "- `gates/` contains local section 7 gate results.",
            "",
            "No PDF, live Grok package audit, or package done declaration is emitted by Pass 1.",
            "",
        ]
    )


def _build_manifest(
    *,
    package_id: str,
    tenant_id: str,
    trigger: str,
    generated_at: datetime,
    package_dir: Path,
    model_identity: str,
    model_temperature: int,
    render_toolchain: str,
    fraud_contrast_id: str,
    legit_contrast_id: str,
    audit_packet_files: Sequence[str | Path],
    audit_packet: audit_packet_mod.AssembledAuditPacket,
    audit_packet_manifest_path: Path,
    done_evaluation_record: Mapping[str, Any],
) -> dict[str, Any]:
    file_hashes = _package_file_hashes(package_dir)
    package_hash = sha256(
        json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "package_id": package_id,
        "package_version": PACKAGE_VERSION,
        "tenant_id": tenant_id,
        "trigger": trigger,
        "generated_at": generated_at.isoformat(),
        "render_toolchain": render_toolchain,
        "model_identity": model_identity,
        "model_temperature": model_temperature,
        "two_shot_contrast_pair": {
            "fraud_row_id": fraud_contrast_id,
            "legit_row_id": legit_contrast_id,
        },
        "file_hashes": file_hashes,
        "package_hash": f"sha256:{package_hash}",
        "audit_packet_files": [_repo_relative(Path(path)) for path in audit_packet_files],
        "audit_packet": {
            "artifact_path": _repo_relative(audit_packet_manifest_path),
            "packet_hash": audit_packet.packet_hash,
            "coverage_complete": audit_packet.coverage_complete,
            "file_count": audit_packet.file_count,
            "missing_paths": list(audit_packet.missing_paths),
            "grok_submitted": audit_packet.grok_submitted,
        },
        "done_evaluation": dict(done_evaluation_record),
        "pdf_rendered": False,
        "grok_audit_submitted": False,
        "done_declaration_emitted": bool(done_evaluation_record.get("done_declaration_emitted", False)),
    }


def _gate_result_to_dict(result: gates.GateResult) -> dict[str, Any]:
    return {
        "gate": result.gate,
        "passed": result.passed,
        "findings": [
            {
                "code": finding.code,
                "message": finding.message,
                "path": finding.path,
                "severity": finding.severity,
            }
            for finding in result.findings
        ],
    }


def _load_records(package_dir: Path) -> list[dict[str, Any]]:
    records = []
    for stage in RECORD_SPECS:
        path = package_dir / "records" / f"{stage}.json"
        if path.exists():
            records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _claims_from_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "claim_id": f"claim-{record['record_id']}",
            "record_refs": [record["record_id"]],
            "source_artifact_paths": [record["source_artifact_path"]],
        }
        for record in records
    ]


def _load_source_payload(path: Path) -> Any:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return {"rendered_markdown": path.read_text(encoding="utf-8")}


def _source_summary(stage: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {"stage": stage}
    if stage == "detection":
        return {
            "case_id": payload.get("case_id"),
            "detectors_fired": payload.get("detectors_fired", []),
            "risk_score_after_lift": payload.get("risk_score_after_lift"),
        }
    if stage == "verification":
        return {
            "case_id": payload.get("case_id"),
            "internal_score": payload.get("internal_score"),
            "recommended_action": payload.get("recommended_action"),
            "model": payload.get("model"),
        }
    if stage == "evidence":
        return {
            "case_id": payload.get("case_id"),
            "policy_hash": payload.get("policy_hash"),
            "effective_parameter_count": len(payload.get("effective_parameter_report", [])),
        }
    if stage == "audit_trail":
        return {
            "case_id": payload.get("case_id"),
            "policy_hash": payload.get("policy_hash"),
            "signed_by": payload.get("signed_by"),
            "two_channel_record_count": len(payload.get("two_channel_record_ids", [])),
        }
    return {"case_id": payload.get("case_id"), "stage": stage}


def _signed_artifact_path(payload: Any, source_path: Path) -> Path:
    if isinstance(payload, Mapping):
        raw = payload.get("signed_policy_artifact")
        if raw:
            candidate = Path(str(raw))
            return candidate if candidate.is_absolute() else _repo_root() / candidate
    return source_path


def _package_file_hashes(package_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    if not package_dir.exists():
        return hashes
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name.endswith(".zip") or path.name == "manifest.json":
            continue
        hashes[path.relative_to(package_dir).as_posix()] = f"sha256:{_file_sha256(path)}"
    return hashes


def _write_bundle(*, package_dir: Path, bundle_path: Path, include_paths: Sequence[Path]) -> None:
    temp_fd, temp_name = tempfile.mkstemp(
        prefix=f".{bundle_path.name}.", suffix=".tmp", dir=bundle_path.parent
    )
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(include_paths, key=lambda item: item.relative_to(package_dir).as_posix()):
                info = zipfile.ZipInfo(path.relative_to(package_dir).as_posix())
                info.date_time = (1980, 1, 1, 0, 0, 0)
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, path.read_bytes())
        temp_path.replace(bundle_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    Path(temp_name).replace(path)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aware_utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _tenant_id(records: Sequence[Mapping[str, Any]]) -> str | None:
    for record in records:
        tenant_id = record.get("tenant_id")
        if tenant_id:
            return str(tenant_id)
    return None


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-")
    return slug or "tenant"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(_repo_root()).as_posix()
    except ValueError:
        return resolved.as_posix()
