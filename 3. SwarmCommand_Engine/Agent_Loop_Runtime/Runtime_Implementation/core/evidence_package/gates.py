"""Evidence-package gate library."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

BOUNDARY_STATEMENT = (
    "This package covers NorthStar Inbox Shield's email-fraud and inbox-layer MDR control "
    "surface only. Other controls in your security stack — including MFA, EDR, backups, "
    "incident response plans, and patch management — are not in this package's scope and "
    "must be evidenced by your MSP or other vendors. This package does not guarantee "
    "underwriting approval or premium reduction; it provides auditable evidence of one "
    "control surface for your underwriter's review."
)
FORBIDDEN_LANGUAGE_PHRASES = ("guaranteed", "guarantee", "bulletproof", "fully secure", "100% secure", "complete security", "compliant", "compliance", "SOC 2", "SOC2", "ISO 27001", "HIPAA", "PCI", "attestation", "prevents all", "stops all", "eliminates all", "replaces your")
VOCABULARY_TRANSLATIONS = {
    "control efficacy": "how well this control works in practice",
    "regulatory mapping": "cross-reference to specific underwriting questions",
    "compensating control": "a different control that addresses the same risk",
    "control attestation framework": "the way we record what each control does",
    "material weakness": "a meaningful gap",
}
FRESHNESS_THRESHOLDS_DAYS = {"policy_change_control": 30, "tenant_isolation": 30, "kill_switch": 30, "detection_evidence": 90, "scoring_explanation": 90, "test_evidence": 90, "independent_audit": 90, "operational_artifact": 90}
_SECRET_PATTERNS = (re.compile(r"\b(?:OPENAI|XAI|ANTHROPIC|GITHUB|AWS|AZURE|GOOGLE)_[A-Z0-9_]*KEY\s*=", re.I), re.compile(r"\bxai-[A-Za-z0-9_-]{20,}\b"), re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"), re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"))
_RAW_BODY_KEYS = {"raw_body", "raw_email_body", "body_plain", "body_html", "raw_llm_response"}

@dataclass(frozen=True)
class GateFinding:
    code: str
    message: str
    path: str | None = None
    severity: str = "blocking"

@dataclass(frozen=True)
class GateResult:
    gate: str
    findings: tuple[GateFinding, ...] = field(default_factory=tuple)
    @property
    def passed(self) -> bool:
        return not self.findings

def run_broken_link_gate(records: Iterable[Mapping[str, Any]], *, workspace_root: Path) -> GateResult:
    findings = []
    for index, record in enumerate(records):
        source = record.get("source_artifact_path"); path = _record_path(record, index)
        if not source:
            findings.append(GateFinding("missing_source_artifact_path", "Record has no source_artifact_path.", path)); continue
        if not _resolve_path(source, workspace_root).exists():
            findings.append(GateFinding("source_artifact_missing", f"source_artifact_path does not resolve: {source}", path))
    return GateResult("broken_link", tuple(findings))

def run_signed_provenance_gate(records: Iterable[Mapping[str, Any]], *, workspace_root: Path) -> GateResult:
    findings = []
    for index, record in enumerate(records):
        if not _requires_signed_provenance(record): continue
        signed_by = record.get("signed_by"); path = _record_path(record, index)
        if not signed_by:
            findings.append(GateFinding("missing_signed_by", "Policy or override record has no signed_by artifact.", path)); continue
        if not _resolve_path(signed_by, workspace_root).exists():
            findings.append(GateFinding("signed_by_missing", f"signed_by does not resolve: {signed_by}", path))
    return GateResult("signed_provenance", tuple(findings))

def run_stale_evidence_gate(records: Iterable[Mapping[str, Any]], *, now: datetime, workspace_root: Path) -> GateResult:
    findings = []; evaluated_at = _ensure_aware_utc(now)
    for index, record in enumerate(records):
        path = _record_path(record, index)
        if _has_resolving_signed_artifact(record, workspace_root):
            findings.extend(_superseded_annotation_findings(record, path)); continue
        category = record.get("evidence_category")
        if category not in FRESHNESS_THRESHOLDS_DAYS:
            findings.append(GateFinding("unknown_freshness_category", f"Unknown or missing evidence_category: {category!r}", path)); continue
        raw = record.get("last_verified_at")
        if not raw:
            findings.append(GateFinding("missing_last_verified_at", "Non-exempt record has no last_verified_at.", path)); continue
        try: verified_at = _parse_datetime(str(raw))
        except ValueError as exc:
            findings.append(GateFinding("invalid_last_verified_at", str(exc), path)); continue
        age_days = (evaluated_at - verified_at).total_seconds() / 86400; threshold = FRESHNESS_THRESHOLDS_DAYS[str(category)]
        if age_days > threshold:
            findings.append(GateFinding("stale_evidence", f"{category} evidence is {age_days:.1f} days old; threshold is {threshold} days.", path))
    return GateResult("stale_evidence", tuple(findings))

def run_claim_validation_gate(claims: Iterable[Mapping[str, Any]], records: Iterable[Mapping[str, Any]]) -> GateResult:
    records_by_id = {str(r["record_id"]): r for r in records if r.get("record_id") is not None}; findings = []
    for index, claim in enumerate(claims):
        path = _claim_path(claim, index); refs = [str(ref) for ref in claim.get("record_refs", [])]; direct = [src for src in claim.get("source_artifact_paths", []) if src]
        if not refs and not direct:
            findings.append(GateFinding("claim_has_no_source", "Claim has no record_refs or source_artifact_paths.", path)); continue
        for ref in refs:
            record = records_by_id.get(ref)
            if record is None:
                findings.append(GateFinding("claim_record_ref_missing", f"Claim references missing record_id: {ref}", path)); continue
            if not record.get("source_artifact_path"):
                findings.append(GateFinding("claim_record_has_no_source", f"Referenced record has no source_artifact_path: {ref}", path))
    return GateResult("claim_validation", tuple(findings))

def run_redaction_gate(records: Iterable[Mapping[str, Any]] = (), *, rendered_texts: Iterable[str] = (), tenant_id: str | None = None, known_tenant_ids: Iterable[str] = ()) -> GateResult:
    findings = []
    for index, record in enumerate(records): findings.extend(_scan_record_for_redaction(record, _record_path(record, index), tenant_id, known_tenant_ids))
    for index, text in enumerate(rendered_texts): findings.extend(_scan_text_for_redaction(str(text), path=f"rendered_text[{index}]", tenant_id=tenant_id, known_tenant_ids=known_tenant_ids))
    return GateResult("redaction", tuple(findings))

def run_forbidden_language_gate(surfaces: Iterable[str | Mapping[str, Any]]) -> GateResult:
    findings = []
    for index, surface in enumerate(surfaces):
        text, path, allowed = _surface_parts(surface, index)
        if allowed: continue
        for phrase in FORBIDDEN_LANGUAGE_PHRASES:
            if _phrase_present(text, phrase): findings.append(GateFinding("forbidden_language", f"Forbidden phrase used outside allowed context: {phrase}", path))
    return GateResult("forbidden_language", tuple(findings))

def run_vocabulary_translation_gate(rendered_texts: Iterable[str | Mapping[str, Any]]) -> GateResult:
    findings = []
    for index, surface in enumerate(rendered_texts):
        text, path, _ = _surface_parts(surface, index)
        for jargon, replacement in VOCABULARY_TRANSLATIONS.items():
            if _phrase_present(text, jargon): findings.append(GateFinding("untranslated_jargon", f"Carrier jargon appears in rendered text: {jargon}; use '{replacement}'.", path))
    return GateResult("vocabulary_translation", tuple(findings))

def run_scope_boundary_gate(rendered_text: str, *, boundary_statement: str = BOUNDARY_STATEMENT) -> GateResult:
    if boundary_statement in rendered_text: return GateResult("scope_boundary")
    return GateResult("scope_boundary", (GateFinding("scope_boundary_missing_or_edited", "Required §2 boundary statement is missing or edited.", "rendered_text"),))

def run_audit_packet_coverage_gate(touched_files: Iterable[str | Path], audit_packet_files: Iterable[str | Path]) -> GateResult:
    packet = {_normalize_path(path) for path in audit_packet_files}
    findings = [GateFinding("touched_file_missing_from_audit_packet", f"Touched file is not covered by audit packet: {_normalize_path(path)}", _normalize_path(path)) for path in touched_files if _normalize_path(path) not in packet]
    return GateResult("audit_packet_coverage", tuple(findings))

def _record_path(record, index): return str(record.get("record_id") or record.get("record_type") or f"record[{index}]")
def _claim_path(claim, index): return str(claim.get("claim_id") or f"claim[{index}]")
def _resolve_path(path, workspace_root):
    candidate = Path(path); return candidate if candidate.is_absolute() else workspace_root / candidate
def _requires_signed_provenance(record):
    record_type = str(record.get("record_type", "")).lower(); category = str(record.get("evidence_category", "")).lower()
    return any(token in record_type or token in category for token in ("policy", "override"))
def _has_resolving_signed_artifact(record, workspace_root):
    signed_by = record.get("signed_by"); return bool(signed_by and _resolve_path(signed_by, workspace_root).exists())
def _superseded_annotation_findings(record, path):
    if not (record.get("superseded_by") or record.get("superseded_by_spec")): return []
    if record.get("superseded_annotation"): return []
    return [GateFinding("missing_superseded_annotation", "Superseded signed artifact lacks render annotation.", path)]
def _parse_datetime(value): return _ensure_aware_utc(datetime.fromisoformat(value.strip().replace("Z", "+00:00")))
def _ensure_aware_utc(value): return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
def _scan_record_for_redaction(record, record_path, tenant_id, known_tenant_ids):
    findings = []
    for key, value in _flatten_mapping(record):
        if key.split(".")[-1] in _RAW_BODY_KEYS and value: findings.append(GateFinding("raw_body_field_present", f"Raw body field must not be exposed: {key}", record_path))
        findings.extend(_scan_text_for_redaction(str(value), path=f"{record_path}:{key}", tenant_id=tenant_id, known_tenant_ids=known_tenant_ids))
    return findings
def _scan_text_for_redaction(text, *, path, tenant_id, known_tenant_ids):
    findings = []
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS): findings.append(GateFinding("secret_or_credential_present", "Potential secret, token, credential, or private key is present.", path))
    if re.search(r"\braw (?:email|message) body\b", text, re.I): findings.append(GateFinding("raw_body_reference", "Rendered text appears to expose a raw email body.", path))
    if tenant_id:
        for known_id in known_tenant_ids:
            if known_id != tenant_id and known_id and known_id in text: findings.append(GateFinding("cross_tenant_identifier", "Text includes a different tenant identifier.", path))
    return findings
def _flatten_mapping(value, prefix=""):
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, Mapping): yield from _flatten_mapping(item, path)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            for index, child in enumerate(item):
                child_path = f"{path}[{index}]"
                if isinstance(child, Mapping): yield from _flatten_mapping(child, child_path)
                else: yield child_path, child
        else: yield path, item
def _surface_parts(surface, index):
    if isinstance(surface, Mapping): return str(surface.get("text", "")), str(surface.get("path") or surface.get("name") or f"surface[{index}]"), bool(surface.get("allowed_context"))
    return str(surface), f"surface[{index}]", False
def _phrase_present(text, phrase): return bool(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, re.I))
def _normalize_path(path): return str(path).replace("\\", "/").strip("./")
