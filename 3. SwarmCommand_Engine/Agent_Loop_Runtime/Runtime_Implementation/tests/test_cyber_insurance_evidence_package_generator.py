from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import generate_package_from_test_plan

FIXED_NOW = datetime(2026, 6, 4, 1, 10, 0, tzinfo=timezone.utc)
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


def _generate(tmp_path: Path):
    source_dir = tmp_path / "source"
    _write_source_fixtures(source_dir)
    return generate_package_from_test_plan(
        source_dir=source_dir,
        output_root=tmp_path / "out",
        tenant_id=TENANT,
        trigger="on_demand",
        now=FIXED_NOW,
    )


def test_generator_emits_bundle_records_and_passes_all_gates(tmp_path):
    result = _generate(tmp_path)

    assert result.gates_passed
    assert len(result.gate_results) == 9
    assert result.package_dir.exists()
    assert result.markdown_bundle_path.exists()
    assert result.manifest_path.exists()
    assert result.package_markdown_path.exists()

    records_dir = result.package_dir / "records"
    assert sorted(p.name for p in records_dir.glob("*.json")) == [
        "audit_trail.json",
        "detection.json",
        "evidence.json",
        "outcome_documentation.json",
        "verification.json",
    ]


def test_generator_markdown_carries_boundary_statement(tmp_path):
    result = _generate(tmp_path)
    markdown = result.package_markdown_path.read_text(encoding="utf-8")

    from core.evidence_package import BOUNDARY_STATEMENT

    assert BOUNDARY_STATEMENT in markdown


def test_generator_manifest_pins_model_and_marks_pass1_deferrals(tmp_path):
    result = _generate(tmp_path)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert manifest["tenant_id"] == TENANT
    assert manifest["model_identity"] == "grok-4"
    assert manifest["model_temperature"] == 0
    assert manifest["package_hash"].startswith("sha256:")
    assert manifest["pdf_rendered"] is False
    assert manifest["grok_audit_submitted"] is False
    assert manifest["done_declaration_emitted"] is False


def test_generator_is_deterministic_for_same_inputs(tmp_path):
    first = _generate(tmp_path)
    first_manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    first_names = zipfile.ZipFile(first.markdown_bundle_path).namelist()

    second = _generate(tmp_path)
    second_manifest = json.loads(second.manifest_path.read_text(encoding="utf-8"))
    second_names = zipfile.ZipFile(second.markdown_bundle_path).namelist()

    assert first.package_id == second.package_id
    assert first_manifest["package_hash"] == second_manifest["package_hash"]
    assert first_names == second_names


def test_generator_fails_closed_when_source_artifact_missing(tmp_path):
    source_dir = tmp_path / "source"
    _write_source_fixtures(source_dir)
    (source_dir / "detection.json").unlink()

    import pytest

    with pytest.raises(FileNotFoundError):
        generate_package_from_test_plan(
            source_dir=source_dir,
            output_root=tmp_path / "out",
            tenant_id=TENANT,
            now=FIXED_NOW,
        )
