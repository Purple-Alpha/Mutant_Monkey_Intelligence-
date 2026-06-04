from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import (
    evaluate_done_criteria,
    load_operator_signature_evidence_id,
    record_operator_signature,
)
from core.evidence_package.operator_signature import OperatorSignatureError

FIXED_NOW = datetime(2026, 6, 4, 20, 0, 0, tzinfo=timezone.utc)

GATE_NAMES = (
    "broken_link",
    "signed_provenance",
    "stale_evidence",
    "claim_validation",
    "redaction",
    "forbidden_language",
    "vocabulary_translation",
    "scope_boundary",
    "audit_packet_coverage",
)


@dataclass(frozen=True)
class _StubGate:
    gate: str
    passed: bool


def _all_passing() -> list[_StubGate]:
    return [_StubGate(name, True) for name in GATE_NAMES]


def _rendered_package(tmp_path: Path) -> Path:
    rendered = tmp_path / "rendered" / "package.md"
    rendered.parent.mkdir(parents=True, exist_ok=True)
    rendered.write_text("Rendered package for operator review.\n", encoding="utf-8")
    return rendered


def test_records_operator_signature_evidence_without_generating_wording(tmp_path):
    package_dir = tmp_path / "package"
    rendered = _rendered_package(package_dir)

    record = record_operator_signature(
        package_dir=package_dir,
        package_id="pkg-1",
        package_version="v1",
        tenant_id="tenant-1",
        rendered_package_path=rendered,
        operator_wording="Matt-authored sign-off wording for this synthetic package.",
        scope_acknowledgment="I reviewed the rendered package and understand the v1 scope boundary.",
        signed_at=FIXED_NOW,
    )

    assert record.evidence_id.startswith("evd-operator-signature-")
    assert record.path == package_dir / "records" / "signed_by_operator.json"
    payload = json.loads(record.path.read_text(encoding="utf-8"))
    assert payload["record_kind"] == "signed_by_operator"
    assert payload["operator_wording"] == "Matt-authored sign-off wording for this synthetic package."
    assert payload["scope_acknowledgment"].startswith("I reviewed")
    assert payload["authorship_rule"] == (
        "Operator wording is supplied by Matt; AI-authored sign-off text is forbidden."
    )
    assert load_operator_signature_evidence_id(package_dir) == record.evidence_id


def test_signature_evidence_id_satisfies_criterion_14(tmp_path):
    package_dir = tmp_path / "package"
    rendered = _rendered_package(package_dir)
    signature = record_operator_signature(
        package_dir=package_dir,
        package_id="pkg-1",
        package_version="v1",
        tenant_id="tenant-1",
        rendered_package_path=rendered,
        operator_wording="Matt-authored sign-off wording.",
        scope_acknowledgment="Scope boundary reviewed and accepted for this package.",
        signed_at=FIXED_NOW,
    )

    evaluation = evaluate_done_criteria(
        gate_results=_all_passing(),
        grok_audit_output="audit_outputs/pkg.md",
        grok_findings_resolved=True,
        operator_signature_evidence_id=signature.evidence_id,
        test_plan_evidence_id="test-plan-001",
    )

    assert evaluation.is_done is True
    assert 14 in evaluation.criteria_met


@pytest.mark.parametrize(
    ("operator_wording", "scope_acknowledgment", "field"),
    [
        ("", "scope reviewed", "operator_wording"),
        ("Matt wording", "", "scope_acknowledgment"),
    ],
)
def test_rejects_missing_required_signature_fields(
    tmp_path: Path,
    operator_wording: str,
    scope_acknowledgment: str,
    field: str,
):
    package_dir = tmp_path / "package"
    rendered = _rendered_package(package_dir)

    with pytest.raises(OperatorSignatureError, match=field):
        record_operator_signature(
            package_dir=package_dir,
            package_id="pkg-1",
            package_version="v1",
            tenant_id="tenant-1",
            rendered_package_path=rendered,
            operator_wording=operator_wording,
            scope_acknowledgment=scope_acknowledgment,
            signed_at=FIXED_NOW,
        )


def test_rejects_missing_reviewed_rendered_package(tmp_path):
    with pytest.raises(OperatorSignatureError, match="rendered_package_path"):
        record_operator_signature(
            package_dir=tmp_path / "package",
            package_id="pkg-1",
            package_version="v1",
            tenant_id="tenant-1",
            rendered_package_path=tmp_path / "missing.md",
            operator_wording="Matt wording",
            scope_acknowledgment="Scope reviewed",
            signed_at=FIXED_NOW,
        )


def test_loader_fails_closed_for_malformed_signature_record(tmp_path):
    records_dir = tmp_path / "package" / "records"
    records_dir.mkdir(parents=True)
    (records_dir / "signed_by_operator.json").write_text(
        json.dumps({"record_kind": "signed_by_operator", "evidence_id": ""}),
        encoding="utf-8",
    )

    assert load_operator_signature_evidence_id(tmp_path / "package") is None
