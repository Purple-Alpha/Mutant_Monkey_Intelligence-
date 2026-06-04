from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import (
    evaluate_done_criteria,
    emit_done_declaration_if_done,
)
from core.evidence_package.done_declaration import build_done_evaluation_record

FIXED_NOW = datetime(2026, 6, 4, 17, 0, 0, tzinfo=timezone.utc)

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


def test_pass1_package_is_not_done_with_expected_gaps():
    evaluation = evaluate_done_criteria(gate_results=_all_passing())

    assert evaluation.is_done is False
    # Gate-backed criteria + criterion 13 (no drift dir) are met.
    assert set(evaluation.criteria_met) == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13}
    # The Pass-1 structural gaps are exactly 11, 12, 14, 15.
    assert set(evaluation.blocking_for_done) == {11, 12, 14, 15}


def test_full_done_when_all_inputs_present():
    evaluation = evaluate_done_criteria(
        gate_results=_all_passing(),
        grok_audit_output="audit_outputs/pkg_grok.md",
        grok_findings_resolved=True,
        operator_signature_evidence_id="evd-sig-1",
        test_plan_evidence_id="testplan-001",
    )

    assert evaluation.is_done is True
    assert set(evaluation.criteria_met) == set(range(1, 16))


def test_failing_gate_unmets_its_criterion():
    gates = [g if g.gate != "redaction" else _StubGate("redaction", False) for g in _all_passing()]
    evaluation = evaluate_done_criteria(gate_results=gates)

    unmet = dict(evaluation.criteria_unmet)
    # Redaction backs both criterion 6 and criterion 9.
    assert 6 in unmet and 9 in unmet
    assert "redaction" in unmet[6]


def test_open_blocking_drift_incident_unmets_criterion_13(tmp_path):
    drift_dir = tmp_path / "drift"
    drift_dir.mkdir()
    (drift_dir / "drift_001.json").write_text(
        json.dumps({"severity": "blocking", "status": "open"}), encoding="utf-8"
    )

    evaluation = evaluate_done_criteria(gate_results=_all_passing(), drift_dir=drift_dir)
    unmet = dict(evaluation.criteria_unmet)
    assert 13 in unmet


def test_resolved_blocking_drift_incident_meets_criterion_13(tmp_path):
    drift_dir = tmp_path / "drift"
    drift_dir.mkdir()
    (drift_dir / "drift_001.json").write_text(
        json.dumps({"severity": "blocking", "status": "resolved"}), encoding="utf-8"
    )

    evaluation = evaluate_done_criteria(gate_results=_all_passing(), drift_dir=drift_dir)
    assert 13 in set(evaluation.criteria_met)


def test_emit_writes_nothing_when_not_done(tmp_path):
    evaluation = evaluate_done_criteria(gate_results=_all_passing())
    result = emit_done_declaration_if_done(
        evaluation,
        package_dir=tmp_path,
        package_id="pkg-1",
        package_version="v1",
        tenant_id="t-1",
        generated_at=FIXED_NOW,
        now=FIXED_NOW,
        grok_audit_output=None,
    )

    assert result is None
    assert not (tmp_path / "done_declaration.json").exists()


def test_emit_writes_declaration_when_done(tmp_path):
    evaluation = evaluate_done_criteria(
        gate_results=_all_passing(),
        grok_audit_output="audit_outputs/pkg_grok.md",
        grok_findings_resolved=True,
        operator_signature_evidence_id="evd-sig-1",
        test_plan_evidence_id="testplan-001",
    )
    path = emit_done_declaration_if_done(
        evaluation,
        package_dir=tmp_path,
        package_id="pkg-1",
        package_version="v1",
        tenant_id="t-1",
        generated_at=FIXED_NOW,
        now=FIXED_NOW,
        grok_audit_output="audit_outputs/pkg_grok.md",
        operator_signature_evidence_id="evd-sig-1",
    )

    assert path is not None and path.exists()
    declaration = json.loads(path.read_text(encoding="utf-8"))
    assert declaration["criteria_met"] == list(range(1, 16))
    assert declaration["operator_signature_evidence_id"] == "evd-sig-1"


def test_done_evaluation_record_shape():
    evaluation = evaluate_done_criteria(gate_results=_all_passing())
    record = build_done_evaluation_record(
        evaluation,
        package_id="pkg-1",
        package_version="v1",
        tenant_id="t-1",
        generated_at=FIXED_NOW,
    )

    assert record["is_done"] is False
    assert record["done_declaration_emitted"] is False
    assert sorted(record["criteria_met"]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13]
    reasons = {item["criterion"] for item in record["criteria_unmet"]}
    assert reasons == {11, 12, 14, 15}
