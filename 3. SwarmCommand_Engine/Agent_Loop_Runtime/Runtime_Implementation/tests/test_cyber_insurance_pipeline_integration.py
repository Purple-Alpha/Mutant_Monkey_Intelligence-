"""End-to-end pipeline integration test for the Cyber Insurance generator.

Stages 8 (audit-packet assembly), 9 (Grok package audit), and 10 (done
declaration) were each built and unit-tested in isolation. This test proves
they actually *chain*: a synthetic package flows generation -> packet -> audit
-> done evaluation coherently, the criteria gaps close in the expected order,
and the package never declares "done" prematurely.

Fully synthetic, no network: the stage-9 Grok client is injected as a fake.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import (
    audit_package,
    evaluate_done_criteria,
    emit_done_declaration_if_done,
    generate_package_from_test_plan,
)

FIXED_NOW = datetime(2026, 6, 4, 19, 0, 0, tzinfo=timezone.utc)
TENANT = "bluefin-marine-supplies-demo"


def _write_source_fixtures(source_dir: Path) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "detection.json").write_text(
        json.dumps(
            {
                "record_kind": "cyber_insurance_v1_detection_record",
                "case_id": "cybins-v1-testplan-vendor-payment-redirect-001",
                "tenant_id": TENANT,
                "detectors_fired": ["payment_change_body_pattern_v1"],
                "risk_score_after_lift": 68,
                "raw_email_body_included": False,
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "verification.json").write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-testplan-vendor-payment-redirect-001",
                "tenant_id": TENANT,
                "internal_score": 72,
                "recommended_action": "review_before_payment",
                "model": "grok-4",
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "evidence.json").write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-testplan-vendor-payment-redirect-001",
                "tenant_id": TENANT,
                "policy_hash": "signed-policy-bluefin-stage-a-fictional-v1",
                "effective_parameter_report": [{"k": "v"}],
            }
        ),
        encoding="utf-8",
    )
    audit_trail_path = source_dir / "audit_trail.json"
    audit_trail_path.write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-testplan-vendor-payment-redirect-001",
                "tenant_id": TENANT,
                "policy_hash": "signed-policy-bluefin-stage-a-fictional-v1",
                "signed_by": "fictional-bluefin-security-lead",
                "signed_policy_artifact": str(audit_trail_path),
                "two_channel_record_ids": ["id-1", "id-2"],
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "outcome_documentation.md").write_text(
        "# Outcome\n\nVendor invoice review; payment change reviewed before action.\n",
        encoding="utf-8",
    )


def _stub_contracts(tmp_path: Path) -> list[Path]:
    contracts_dir = tmp_path / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, body in (
        ("VISION.md", "Seven non-negotiables (synthetic stub).\n"),
        ("deep_dive.md", "Boundary statement + claim rules (synthetic stub).\n"),
    ):
        path = contracts_dir / name
        path.write_text(body, encoding="utf-8")
        paths.append(path)
    return paths


def _clean_grok_client(_payload: str) -> str:
    return "No deviations found on the complete packet.\nGATE_SUMMARY: blocking=0 warnings=0\n"


def test_full_pipeline_chains_generation_audit_and_done_declaration(tmp_path):
    # --- Stage 1-8 + 10: generate the synthetic package -----------------
    source_dir = tmp_path / "source"
    _write_source_fixtures(source_dir)
    result = generate_package_from_test_plan(
        source_dir=source_dir,
        output_root=tmp_path / "out",
        tenant_id=TENANT,
        trigger="on_demand",
        now=FIXED_NOW,
    )

    assert result.gates_passed
    assert result.audit_packet_coverage_complete is True
    assert result.audit_packet_manifest_path.exists()
    # Pass 1: not done; the open gaps are 11/12 (Grok) and 14/15 (signature/test).
    assert result.is_done is False
    assert result.done_declaration_path is None

    # --- Stage 9: run the explicit Grok audit with a clean fake client --
    audit_packet_dir = result.audit_packet_manifest_path.parent
    audit_result = audit_package(
        package_id=result.package_id,
        tenant_id=TENANT,
        package_dir=result.package_dir,
        audit_packet_dir=audit_packet_dir,
        contract_files=_stub_contracts(tmp_path),
        grok_client=_clean_grok_client,
        audit_outputs_dir=tmp_path / "audit_outputs",
        now=FIXED_NOW,
    )
    assert audit_result.clean is True
    assert audit_result.drift_incident_paths == ()
    assert Path(audit_result.grok_output_path).exists()

    # --- Stage 10 re-evaluation: stage 9 closes 11/12, but 14/15 remain -
    drift_dir = result.package_dir / "drift"
    after_audit = evaluate_done_criteria(
        gate_results=result.gate_results,
        drift_dir=drift_dir,
        grok_audit_output=audit_result.grok_output_path,
        grok_findings_resolved=True,
        operator_signature_evidence_id=None,
        test_plan_evidence_id=None,
    )
    # The Grok gaps are now closed; the package is still not done (needs 14/15).
    assert 11 in after_audit.criteria_met
    assert 12 in after_audit.criteria_met
    assert after_audit.is_done is False
    assert set(after_audit.blocking_for_done) == {14, 15}

    # No premature declaration even though the audit ran clean.
    assert emit_done_declaration_if_done(
        after_audit,
        package_dir=result.package_dir,
        package_id=result.package_id,
        package_version="v1",
        tenant_id=TENANT,
        generated_at=FIXED_NOW,
        now=FIXED_NOW,
        grok_audit_output=audit_result.grok_output_path,
    ) is None

    # --- Supply the operator signature + test-plan evidence -> done -----
    done_eval = evaluate_done_criteria(
        gate_results=result.gate_results,
        drift_dir=drift_dir,
        grok_audit_output=audit_result.grok_output_path,
        grok_findings_resolved=True,
        operator_signature_evidence_id="evd-operator-signature-001",
        test_plan_evidence_id="cybins-v1-testplan-vendor-payment-redirect-001",
    )
    assert done_eval.is_done is True
    assert sorted(done_eval.criteria_met) == list(range(1, 16))

    declaration_path = emit_done_declaration_if_done(
        done_eval,
        package_dir=result.package_dir,
        package_id=result.package_id,
        package_version="v1",
        tenant_id=TENANT,
        generated_at=FIXED_NOW,
        now=FIXED_NOW,
        grok_audit_output=audit_result.grok_output_path,
        operator_signature_evidence_id="evd-operator-signature-001",
    )
    assert declaration_path is not None and declaration_path.exists()
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    assert declaration["criteria_met"] == list(range(1, 16))
    assert declaration["grok_audit_output"] == audit_result.grok_output_path
    assert declaration["operator_signature_evidence_id"] == "evd-operator-signature-001"


def test_pipeline_audit_with_deviation_blocks_done(tmp_path):
    """If stage 9 finds a blocking deviation, criterion 13 holds it not-done."""
    source_dir = tmp_path / "source"
    _write_source_fixtures(source_dir)
    result = generate_package_from_test_plan(
        source_dir=source_dir,
        output_root=tmp_path / "out",
        tenant_id=TENANT,
        trigger="on_demand",
        now=FIXED_NOW,
    )

    def deviation_client(_payload: str) -> str:
        return (
            "BLOCKING: boundary statement was edited\n"
            "GATE_SUMMARY: blocking=1 warnings=0\n"
        )

    audit_packet_dir = result.audit_packet_manifest_path.parent
    audit_result = audit_package(
        package_id=result.package_id,
        tenant_id=TENANT,
        package_dir=result.package_dir,
        audit_packet_dir=audit_packet_dir,
        contract_files=_stub_contracts(tmp_path),
        grok_client=deviation_client,
        audit_outputs_dir=tmp_path / "audit_outputs",
        now=FIXED_NOW,
    )
    assert audit_result.clean is False
    assert len(audit_result.drift_incident_paths) == 1

    # Even with signature + test evidence, the open blocking drift incident
    # keeps criterion 13 unmet, so the package cannot be done.
    done_eval = evaluate_done_criteria(
        gate_results=result.gate_results,
        drift_dir=result.package_dir / "drift",
        grok_audit_output=audit_result.grok_output_path,
        grok_findings_resolved=True,
        operator_signature_evidence_id="evd-operator-signature-001",
        test_plan_evidence_id="cybins-v1-testplan-vendor-payment-redirect-001",
    )
    assert done_eval.is_done is False
    assert 13 in done_eval.blocking_for_done
