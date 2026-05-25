from __future__ import annotations

import inspect
import importlib.util
import sys
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailAttachmentMeta,
    EmailInboundPayload,
    GovernanceError,
    PdfAttachmentMetadata,
)
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.operator_state.security_profile import ProfileResolution
from core.production_state.vendor_baseline import ingest_signal, tenant_database_path
from core.scoring import document_metadata_detector as dmf
from core.scoring.document_metadata_detector import (
    DocumentMetadataAssessment,
    assess_document_metadata_fingerprint,
    vendor_domain_from_sender,
)
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor


TENANT = "tenant_demo"
NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "blackboard"
    root.mkdir()
    monkeypatch.chdir(root)


def _attachment(
    *,
    producer: str | None = "quickbooks commercial",
    creator: str | None = None,
    filename: str = "invoice.pdf",
    content_type: str = "application/pdf",
    attachment_class: str = "invoice",
) -> EmailAttachmentMeta:
    return EmailAttachmentMeta(
        filename=filename,
        content_type=content_type,
        attachment_class=attachment_class,
        pdf_metadata=PdfAttachmentMetadata(producer=producer, creator=creator),
    )


def _email(*, attachments: list[EmailAttachmentMeta] | None = None) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=NOW,
        sender="ap@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please process the attached invoice.",
        headers={},
        attachments=attachments or [],
    )


def _assess(
    *,
    attachments: list[EmailAttachmentMeta] | None = None,
    tenant_id: str = TENANT,
) -> DocumentMetadataAssessment:
    return assess_document_metadata_fingerprint(
        tenant_id=tenant_id,
        vendor_domain="vendor.example",
        email=_email(attachments=attachments),
        now=NOW,
    )


def _analysis_payload(risk_score: int) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=NOW,
        summary="document metadata integration test",
        action_items=[],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
            invoice_authenticity_score=None,
            behavioral_deviation_flags=[],
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0,
            suspicious_elements=[],
            sender_legitimacy_notes=None,
        ),
        recommended_action="safe",
    )


def test_public_api_surface_is_locked() -> None:
    assert set(dmf.__all__) == {
        "DocumentMetadataAssessment",
        "DocumentMetadataFinding",
        "ExtractedDocumentFingerprint",
        "MetadataField",
        "assess_document_metadata_fingerprint",
        "vendor_domain_from_sender",
    }
    assert inspect.isfunction(assess_document_metadata_fingerprint)
    assert DocumentMetadataAssessment.__dataclass_params__.frozen


def test_no_metadata_path_writes_no_baseline_rows() -> None:
    assessment = _assess(attachments=[])

    assert assessment.findings == ()
    assert assessment.extracted_fingerprints == ()
    assert assessment.recommended_risk_floor == 0
    assert assessment.recommended_action == "none"
    assert not tenant_database_path(TENANT).exists()


def test_first_seen_producer_creates_new_finding() -> None:
    assessment = _assess(attachments=[_attachment(producer="QuickBooks Commercial")])

    assert len(assessment.findings) == 1
    finding = assessment.findings[0]
    assert finding.field == "producer"
    assert finding.baseline_state == "new"
    assert finding.redacted_display == "quickbooks commercial"
    assert finding.signal_hash
    assert assessment.recommended_risk_floor == 75
    assert assessment.recommended_action == "needs_review"
    assert assessment.indicators == ("new_pdf_producer_fingerprint",)
    assert tenant_database_path(TENANT).exists()


def test_known_producer_emits_no_finding_on_second_run() -> None:
    first = _assess(attachments=[_attachment(producer="QuickBooks Commercial")])
    second = assess_document_metadata_fingerprint(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email(attachments=[_attachment(producer="quickbooks  commercial")]),
        now=NOW + timedelta(days=1),
    )

    assert len(first.findings) == 1
    assert second.findings == ()
    assert second.recommended_risk_floor == 0


def test_expired_producer_returns_expired_finding() -> None:
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="pdf_producer_fingerprint",
        raw_value="adobe acrobat web",
        now=NOW - timedelta(days=91),
    )

    assessment = _assess(attachments=[_attachment(producer="Adobe Acrobat Web")])

    assert len(assessment.findings) == 1
    assert assessment.findings[0].baseline_state == "expired"
    assert assessment.indicators == ("expired_pdf_producer_fingerprint",)
    assert assessment.recommended_risk_floor == 75


def test_check_before_ingest_ordering_is_enforced(monkeypatch) -> None:
    calls: list[str] = []

    def fake_check_signal(**kwargs):
        calls.append("check")
        return SimpleNamespace(state="new", record=None)

    def fake_ingest_signal(**kwargs):
        calls.append("ingest")
        return SimpleNamespace(signal_hash="b" * 64)

    monkeypatch.setattr(dmf.vendor_baseline, "check_signal", fake_check_signal)
    monkeypatch.setattr(dmf.vendor_baseline, "ingest_signal", fake_ingest_signal)

    assessment = _assess(attachments=[_attachment(producer="Adobe Acrobat")])

    assert assessment.findings[0].signal_hash == "b" * 64
    assert calls == ["check", "ingest"]


def test_creator_only_attachment_path_works() -> None:
    assessment = _assess(
        attachments=[_attachment(producer=None, creator="Microsoft Print To PDF")]
    )

    assert len(assessment.findings) == 1
    assert assessment.findings[0].field == "creator"
    assert assessment.findings[0].redacted_display == "microsoft print to pdf"


def test_non_pdf_attachment_without_invoice_class_is_ignored() -> None:
    attachment = EmailAttachmentMeta(
        filename="notes.txt",
        content_type="text/plain",
        attachment_class="unknown",
        pdf_metadata=PdfAttachmentMetadata(producer="Adobe Acrobat"),
    )
    assessment = _assess(attachments=[attachment])

    assert assessment.findings == ()
    assert not tenant_database_path(TENANT).exists()


def test_malformed_metadata_is_suppressed_without_crashing() -> None:
    attachment = EmailAttachmentMeta(
        filename="invoice.pdf",
        content_type="application/pdf",
        attachment_class="invoice",
        pdf_metadata=PdfAttachmentMetadata(producer="   ", creator=""),
    )
    assessment = _assess(attachments=[attachment])

    assert assessment.findings == ()


def test_no_raw_metadata_leakage_in_repr_or_dict() -> None:
    raw_producer = "SuperSecret PDF Producer Toolchain v9"
    assessment = _assess(attachments=[_attachment(producer=raw_producer)])

    dumped = str(asdict(assessment))
    assert raw_producer not in dumped
    assert "SuperSecret" not in dumped
    assert assessment.findings[0].redacted_display == (
        "supersecret pdf producer toolchain v9"
    )


@pytest.mark.parametrize(
    "vendor_domain",
    [
        "Vendor.EXAMPLE",
        " vendor.example",
        "",
        "vendor..example",
        "vendor/example",
    ],
)
def test_vendor_domain_validation_raises(vendor_domain: str) -> None:
    with pytest.raises(GovernanceError):
        assess_document_metadata_fingerprint(
            tenant_id=TENANT,
            vendor_domain=vendor_domain,
            email=_email(attachments=[_attachment()]),
            now=NOW,
        )


def test_kill_switch_inheritance_blocks_baseline_writes() -> None:
    engage_kill_switch(
        Path("."),
        scope="PRODUCTION_ONLY",
        reason="halt document metadata baseline",
        operator="matt",
    )

    with pytest.raises(KillSwitchEngaged):
        _assess(attachments=[_attachment()])

    assert not tenant_database_path(TENANT).exists()


def test_tenant_isolation_keeps_baselines_separate() -> None:
    tenant_a = "tenant_a_docmeta"
    tenant_b = "tenant_b_docmeta"

    first_a = assess_document_metadata_fingerprint(
        tenant_id=tenant_a,
        vendor_domain="vendor.example",
        email=_email(attachments=[_attachment(producer="QuickBooks")]),
        now=NOW,
    )
    second_b = assess_document_metadata_fingerprint(
        tenant_id=tenant_b,
        vendor_domain="vendor.example",
        email=_email(attachments=[_attachment(producer="QuickBooks")]),
        now=NOW,
    )

    assert len(first_a.findings) == 1
    assert len(second_b.findings) == 1
    assert tenant_database_path(tenant_a) != tenant_database_path(tenant_b)


def test_duplicate_producer_across_attachments_dedupes_floor() -> None:
    attachments = [
        _attachment(producer="Adobe Acrobat", filename="invoice-a.pdf"),
        _attachment(producer="adobe   acrobat", filename="invoice-b.pdf"),
    ]
    assessment = _assess(attachments=attachments)

    assert len(assessment.extracted_fingerprints) == 2
    assert len(assessment.findings) == 1
    assert assessment.recommended_risk_floor == 75


def test_overlay_lift_only_invariant() -> None:
    assessment = DocumentMetadataAssessment(
        vendor_domain="vendor.example",
        extracted_fingerprints=(),
        findings=(),
        recommended_risk_floor=75,
        recommended_action="needs_review",
        indicators=("new_pdf_producer_fingerprint",),
    )
    inbound = _email(attachments=[_attachment()])
    analysis = _analysis_payload(10)
    medium_resolution = ProfileResolution(
        tenant_default="medium",
        effective_profile="medium",
        enabled_detectors=("llm_primary",),
        forced_escalation_triggers=(),
    )

    lifted = _overlay_ransomware_precursor(
        analysis,
        inbound,
        profile_resolution=medium_resolution,
        document_metadata_assessment=assessment,
    )
    preserved = _overlay_ransomware_precursor(
        analysis,
        inbound,
        profile_resolution=medium_resolution,
        document_metadata_assessment=DocumentMetadataAssessment(
            vendor_domain="vendor.example",
            extracted_fingerprints=(),
            findings=(),
            recommended_risk_floor=0,
            recommended_action="none",
            indicators=(),
        ),
    )

    assert lifted.risk_analysis.risk_score == 75
    assert preserved.risk_analysis.risk_score == 10


def test_overlay_skips_on_low_profile() -> None:
    assessment = DocumentMetadataAssessment(
        vendor_domain="vendor.example",
        extracted_fingerprints=(),
        findings=(),
        recommended_risk_floor=75,
        recommended_action="needs_review",
        indicators=("new_pdf_producer_fingerprint",),
    )
    inbound = _email(attachments=[_attachment()])
    analysis = _analysis_payload(10)
    resolution = ProfileResolution(
        tenant_default="low",
        effective_profile="low",
        enabled_detectors=("llm_primary",),
        forced_escalation_triggers=(),
    )

    result = _overlay_ransomware_precursor(
        analysis,
        inbound,
        profile_resolution=resolution,
        document_metadata_assessment=assessment,
    )

    assert result.risk_analysis.risk_score == 10
    assert "document_metadata:" not in str(result.risk_analysis.risk_factors)


def test_overlay_high_profile_applies_stricter_floor() -> None:
    assessment = DocumentMetadataAssessment(
        vendor_domain="vendor.example",
        extracted_fingerprints=(),
        findings=(),
        recommended_risk_floor=75,
        recommended_action="needs_review",
        indicators=("new_pdf_producer_fingerprint",),
    )
    inbound = _email(attachments=[_attachment()])
    analysis = _analysis_payload(10)
    resolution = ProfileResolution(
        tenant_default="high",
        effective_profile="high",
        enabled_detectors=("llm_primary",),
        forced_escalation_triggers=(),
    )

    result = _overlay_ransomware_precursor(
        analysis,
        inbound,
        profile_resolution=resolution,
        document_metadata_assessment=assessment,
    )

    assert result.risk_analysis.risk_score == 85


def test_vendor_domain_from_sender_normalizes_root_domain() -> None:
    assert vendor_domain_from_sender("Vendor Billing <ap@mail.vendor.example>") == (
        "vendor.example"
    )


def test_grok_audit_runner_has_document_metadata_target() -> None:
    workspace_root = Path(__file__).resolve().parents[4]
    runner_path = workspace_root / "audit_tools" / "grok_audit_runner.py"
    spec = importlib.util.spec_from_file_location("grok_audit_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["grok_audit_runner"] = module
    spec.loader.exec_module(module)

    package = module.AUDIT_PACKAGES["document_metadata_fingerprinting"]
    assert package.name == "document_metadata_fingerprinting"
    assert any(
        "Document_Metadata_Fingerprinting_Deep_Dive.md" in file.relative_path
        for file in package.files
    )
    assert any(
        "document_metadata_detector.py" in file.relative_path for file in package.files
    )
