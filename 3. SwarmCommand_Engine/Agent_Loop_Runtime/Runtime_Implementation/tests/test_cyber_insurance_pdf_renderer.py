from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pytest

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import (
    BOUNDARY_STATEMENT,
    RENDER_ENGINE_IDENTITY,
    generate_package_from_test_plan,
    render_engine_version,
    render_package_pdf,
)

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


def test_renders_valid_pdf_and_sidecar(tmp_path):
    package = _generate(tmp_path)
    result = render_package_pdf(package.package_dir)

    assert result.pdf_path.exists()
    pdf_bytes = result.pdf_path.read_bytes()
    assert pdf_bytes.startswith(b"%PDF")
    assert result.pdf_sha256 == f"sha256:{sha256(pdf_bytes).hexdigest()}"
    assert result.page_count >= 1
    assert result.engine_identity == RENDER_ENGINE_IDENTITY
    assert result.boundary_statement_present is True

    sidecar = json.loads(result.sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["engine_identity"] == RENDER_ENGINE_IDENTITY
    assert sidecar["engine_version"] == render_engine_version()
    assert sidecar["engine_pinned"] is True
    assert sidecar["boundary_statement"] == BOUNDARY_STATEMENT
    assert sidecar["buyer_delivery"] is False
    assert sidecar["pdf_sha256"] == result.pdf_sha256


def test_render_is_byte_deterministic(tmp_path):
    package = _generate(tmp_path)
    first = render_package_pdf(package.package_dir)
    first_bytes = first.pdf_path.read_bytes()
    second = render_package_pdf(package.package_dir)
    second_bytes = second.pdf_path.read_bytes()

    assert first_bytes == second_bytes
    assert first.pdf_sha256 == second.pdf_sha256


def test_engine_identity_mismatch_fails_closed(tmp_path):
    package = _generate(tmp_path)
    with pytest.raises(ValueError, match="engine identity mismatch"):
        render_package_pdf(package.package_dir, expected_engine_identity="weasyprint")


def test_empty_boundary_statement_rejected(tmp_path):
    package = _generate(tmp_path)
    with pytest.raises(ValueError, match="boundary_statement"):
        render_package_pdf(package.package_dir, boundary_statement="   ")


def test_missing_manifest_raises(tmp_path):
    missing = tmp_path / "no_such_package"
    missing.mkdir()
    with pytest.raises(FileNotFoundError):
        render_package_pdf(missing)


def test_generation_does_not_auto_render_pdf(tmp_path):
    package = _generate(tmp_path)
    # PDF render is an explicit, separate step; generation must not emit one.
    assert not (package.package_dir / "rendered" / "package.pdf").exists()
    manifest = json.loads(package.manifest_path.read_text(encoding="utf-8"))
    assert manifest["pdf_rendered"] is False
