from __future__ import annotations

from datetime import date, datetime, timezone
from typing import get_args
from uuid import uuid4

import pytest
from pydantic import ValidationError

from core.blackboard import (
    NORTHSTAR_MAX_ACTION_ITEMS,
    NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS,
    NORTHSTAR_MAX_SUMMARY_CHARS,
    AgentRegistryEntry,
    AgentRole,
    AttachmentClass,
    BehavioralDeviationFlag,
    BlackboardRecord,
    DailyDigestPayload,
    EmailAnalysisActionItem,
    EmailAnalysisFailurePayload,
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailAttachmentMeta,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    append_record,
    read_records,
    validate_record_against_registry,
)
from core.orchestrator import build_default_registry


def _email_scoring_agent() -> AgentRegistryEntry:
    return build_default_registry()["email_risk_scoring_001"]


def _orchestrator_agent() -> AgentRegistryEntry:
    return build_default_registry()["orchestrator_001"]


def _digest_agent() -> AgentRegistryEntry:
    return build_default_registry()["daily_digest_001"]


def _valid_risk_analysis(**overrides) -> EmailAnalysisRiskAnalysis:
    base = dict(
        risk_score=42,
        risk_factors=["spoofed_sender_domain"],
        phishing_signals=["link_to_unknown_domain"],
        urgency_signals=["please_reply_today"],
        financial_risk="medium",
        vendor_fraud_score=40,
        wire_transfer_anomaly_score=30,
        invoice_authenticity_score=None,
        behavioral_deviation_flags=[],
    )
    base.update(overrides)
    return EmailAnalysisRiskAnalysis(**base)


def _valid_impersonation(**overrides) -> EmailAnalysisImpersonationAnalysis:
    base = dict(
        impersonation_likelihood=21,
        suspicious_elements=["display_name_does_not_match_sender"],
        sender_legitimacy_notes="sender is unknown to tenant",
    )
    base.update(overrides)
    return EmailAnalysisImpersonationAnalysis(**base)


def _valid_analysis(**overrides) -> EmailAnalysisPayload:
    base = dict(
        source_email_record_id=uuid4(),
        summary="Vendor needs a wire transfer by Friday.",
        action_items=[EmailAnalysisActionItem(task="Confirm invoice with finance")],
        risk_analysis=_valid_risk_analysis(),
        impersonation_analysis=_valid_impersonation(),
        recommended_action="needs_review",
    )
    base.update(overrides)
    return EmailAnalysisPayload(**base)


def test_email_inbound_payload_round_trips_through_blackboard_record(tmp_path):
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="cfo@northstar.example",
        subject="Outstanding invoice",
        body_plain="Please pay the attached invoice today.",
        headers={"X-Spam-Score": "0.1"},
        attachments=[
            EmailAttachmentMeta(filename="invoice.pdf", size_bytes=12345, content_type="application/pdf")
        ],
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_INBOUND,
        source_agent="orchestrator_001",
        payload=payload.model_dump(mode="json"),
    )

    validated = validate_record_against_registry(record, _orchestrator_agent())
    assert isinstance(validated, EmailInboundPayload)
    assert validated.sender == "vendor@example.com"

    path = tmp_path / "tenant_demo.jsonl"
    append_record(path, record)
    records = read_records(path)
    assert len(records) == 1
    assert records[0].payload["subject"] == "Outstanding invoice"


def test_email_analysis_payload_rejects_risk_score_out_of_range():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=120,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
        )
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=-1,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
        )


def test_email_analysis_payload_rejects_impersonation_likelihood_out_of_range():
    with pytest.raises(ValidationError):
        EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=101,
            suspicious_elements=[],
        )


def test_email_analysis_payload_rejects_invalid_financial_risk_enum():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="critical",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
        )


def test_email_analysis_payload_rejects_invalid_recommended_action():
    with pytest.raises(ValidationError):
        _valid_analysis(recommended_action="quarantine")


def test_email_analysis_payload_rejects_more_than_max_action_items():
    too_many = [
        EmailAnalysisActionItem(task=f"task {i}")
        for i in range(NORTHSTAR_MAX_ACTION_ITEMS + 1)
    ]
    with pytest.raises(ValidationError):
        _valid_analysis(action_items=too_many)


def test_email_analysis_payload_accepts_max_action_items_exactly():
    items = [
        EmailAnalysisActionItem(task=f"task {i}")
        for i in range(NORTHSTAR_MAX_ACTION_ITEMS)
    ]
    payload = _valid_analysis(action_items=items)
    assert len(payload.action_items) == NORTHSTAR_MAX_ACTION_ITEMS


def test_email_analysis_payload_enforces_summary_soft_cap():
    long_summary = "x" * (NORTHSTAR_MAX_SUMMARY_CHARS + 1)
    with pytest.raises(ValidationError, match="summary exceeds soft cap"):
        _valid_analysis(summary=long_summary)


def test_email_analysis_payload_round_trips_through_blackboard(tmp_path):
    payload = _valid_analysis()
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_ANALYSIS,
        source_agent="email_risk_scoring_001",
        payload=payload.model_dump(mode="json"),
    )

    validated = validate_record_against_registry(record, _email_scoring_agent())
    assert isinstance(validated, EmailAnalysisPayload)
    assert validated.recommended_action == "needs_review"

    path = tmp_path / "tenant_demo.jsonl"
    append_record(path, record)
    records = read_records(path)
    assert len(records) == 1
    assert records[0].payload["risk_analysis"]["risk_score"] == 42


def test_email_inbound_payload_disk_load_rejects_unauthorized_fields(tmp_path):
    raw = {
        "received_at": datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc).isoformat(),
        "sender": "vendor@example.com",
        "recipient": "cfo@northstar.example",
        "subject": "Outstanding invoice",
        "body_plain": "Hi",
        "headers": {},
        "attachments": [],
        "unauthorized_extra_field": "should_be_rejected",
    }
    with pytest.raises(ValidationError):
        EmailInboundPayload.model_validate(raw)


def test_email_analysis_failure_payload_preserves_raw_output():
    payload = EmailAnalysisFailurePayload(
        source_email_record_id=uuid4(),
        raw_output="not even close to JSON {{{",
        failure_reason="invalid_json",
    )
    assert payload.failure_reason == "invalid_json"
    assert "not even close to JSON" in payload.raw_output


def test_daily_digest_payload_minimum_construction():
    payload = DailyDigestPayload(digest_date=date(2026, 5, 20))
    assert payload.digest_date == date(2026, 5, 20)
    assert payload.important_emails == []
    assert payload.top_risks == []
    assert payload.tasks == []
    assert payload.digest_markdown is None


def test_action_item_due_date_iso_format_round_trip():
    item = EmailAnalysisActionItem(task="Pay invoice", due_date=date(2026, 6, 1))
    dumped = item.model_dump(mode="json")
    assert dumped["due_date"] == "2026-06-01"
    rehydrated = EmailAnalysisActionItem.model_validate(dumped)
    assert rehydrated.due_date == date(2026, 6, 1)


def test_email_scoring_agent_cannot_write_email_inbound():
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="cfo@northstar.example",
        body_plain="Hi",
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_INBOUND,
        source_agent="email_risk_scoring_001",
        payload=payload.model_dump(mode="json"),
    )

    with pytest.raises(GovernanceError, match="record type"):
        validate_record_against_registry(record, _email_scoring_agent())


def test_daily_digest_agent_can_write_workflow_triggers():
    agent = _digest_agent()
    assert RecordType.WORKFLOW_TRIGGER in agent.allowed_write_types
    assert RecordType.DAILY_DIGEST in agent.allowed_write_types


def test_email_attachment_meta_defaults_to_unknown_class_and_no_extracted_text():
    meta = EmailAttachmentMeta(filename="invoice.pdf")
    assert meta.attachment_class == "unknown"
    assert meta.extracted_text is None
    assert meta.content_type is None
    assert meta.size_bytes is None
    assert meta.sha256 is None


def test_email_attachment_meta_accepts_all_declared_attachment_classes():
    declared = get_args(AttachmentClass)
    # If the Literal grows or shrinks, this test catches it before any agent
    # starts emitting a class the schema does not actually allow.
    assert set(declared) == {
        "invoice",
        "payment_request",
        "credential_lure",
        "payload_carrier",
        "executable_doc",
        "unknown",
    }
    for cls in declared:
        meta = EmailAttachmentMeta(filename=f"{cls}.bin", attachment_class=cls)
        assert meta.attachment_class == cls


def test_email_attachment_meta_rejects_invalid_attachment_class():
    with pytest.raises(ValidationError):
        EmailAttachmentMeta(filename="ransom.zip", attachment_class="malware")


def test_email_attachment_meta_enforces_extracted_text_soft_cap():
    over = "x" * (NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS + 1)
    with pytest.raises(ValidationError, match="extracted_text exceeds soft cap"):
        EmailAttachmentMeta(filename="huge.pdf", extracted_text=over)


def test_email_attachment_meta_accepts_extracted_text_exactly_at_soft_cap():
    at_cap = "y" * NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS
    meta = EmailAttachmentMeta(filename="exactly_at_cap.pdf", extracted_text=at_cap)
    assert len(meta.extracted_text) == NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS


def test_email_attachment_meta_rejects_unauthorized_fields():
    with pytest.raises(ValidationError):
        EmailAttachmentMeta.model_validate(
            {
                "filename": "invoice.pdf",
                "attachment_class": "invoice",
                "extracted_text": "Total due: $12,345",
                "smuggled_field": "should_be_rejected",
            }
        )


def test_email_inbound_payload_round_trips_inspected_attachment_through_blackboard(tmp_path):
    inspected = EmailAttachmentMeta(
        filename="invoice_2026_05_20.pdf",
        content_type="application/pdf",
        size_bytes=18432,
        sha256="a" * 64,
        extracted_text="Invoice #1234. Total due: $48,920. Wire to ACH 0123.",
        attachment_class="invoice",
    )
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="cfo@northstar.example",
        subject="Q2 invoice",
        body_plain="See attached.",
        attachments=[inspected],
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_INBOUND,
        source_agent="orchestrator_001",
        payload=payload.model_dump(mode="json"),
    )
    validated = validate_record_against_registry(record, _orchestrator_agent())
    assert isinstance(validated, EmailInboundPayload)
    assert validated.attachments[0].attachment_class == "invoice"
    assert "Total due: $48,920" in validated.attachments[0].extracted_text

    path = tmp_path / "tenant_demo.jsonl"
    append_record(path, record)
    records = read_records(path)
    assert records[0].payload["attachments"][0]["attachment_class"] == "invoice"
    assert records[0].payload["attachments"][0]["sha256"] == "a" * 64


# ---------------------------------------------------------------------------
# Month 2 — Phase 1.1 Vendor / Invoice Fraud Detection schema extension.
# Tests below pin the four new EmailAnalysisRiskAnalysis fields, the
# BehavioralDeviationFlag Literal membership, and the score bounds.
# ---------------------------------------------------------------------------


def test_email_analysis_risk_analysis_requires_two_new_score_fields():
    """vendor_fraud_score and wire_transfer_anomaly_score are required per
    Phase_1_1_Fraud_Prevention_Deep_Dive.md §2.5."""
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
        )


def test_email_analysis_risk_analysis_defaults_optional_fields_to_safe_values():
    risk = EmailAnalysisRiskAnalysis(
        risk_score=10,
        risk_factors=[],
        phishing_signals=[],
        urgency_signals=[],
        financial_risk="low",
        vendor_fraud_score=0,
        wire_transfer_anomaly_score=0,
    )
    assert risk.invoice_authenticity_score is None
    assert risk.behavioral_deviation_flags == []


def test_email_analysis_risk_analysis_rejects_vendor_fraud_score_out_of_range():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=101,
            wire_transfer_anomaly_score=0,
        )


def test_email_analysis_risk_analysis_rejects_wire_transfer_anomaly_score_out_of_range():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=-1,
        )


def test_email_analysis_risk_analysis_rejects_invoice_authenticity_score_out_of_range():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
            invoice_authenticity_score=200,
        )


def test_email_analysis_risk_analysis_accepts_full_new_field_set():
    risk = EmailAnalysisRiskAnalysis(
        risk_score=88,
        risk_factors=["new_banking_instructions"],
        phishing_signals=["lookalike_sender_domain"],
        urgency_signals=["payment_today"],
        financial_risk="high",
        vendor_fraud_score=88,
        wire_transfer_anomaly_score=72,
        invoice_authenticity_score=25,
        behavioral_deviation_flags=[
            "new_banking_instructions",
            "urgency_paired_with_finance",
            "lookalike_sender_domain",
        ],
    )
    assert risk.vendor_fraud_score == 88
    assert risk.wire_transfer_anomaly_score == 72
    assert risk.invoice_authenticity_score == 25
    assert len(risk.behavioral_deviation_flags) == 3


def test_behavioral_deviation_flag_literal_pins_exactly_nine_values():
    """Catches schema drift before any agent starts emitting a flag the schema
    does not actually allow (same governance pattern as AttachmentClass)."""
    declared = get_args(BehavioralDeviationFlag)
    assert set(declared) == {
        "new_banking_instructions",
        "out_of_band_pressure",
        "unusual_dollar_amount",
        "lookalike_sender_domain",
        "reply_to_diverges_from_from",
        "mismatched_invoice_vendor_name",
        "first_time_sender_with_financial_ask",
        "urgency_paired_with_finance",
        "unusual_unicode_obfuscation",
    }


def test_email_analysis_risk_analysis_rejects_unknown_behavioral_deviation_flag():
    with pytest.raises(ValidationError):
        EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
            behavioral_deviation_flags=["invented_freeform_flag"],
        )


def test_email_analysis_payload_round_trips_new_scoring_fields_through_blackboard(tmp_path):
    payload = _valid_analysis(
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=88,
            risk_factors=["new_banking_instructions"],
            phishing_signals=["lookalike_sender_domain"],
            urgency_signals=["payment_today"],
            financial_risk="high",
            vendor_fraud_score=88,
            wire_transfer_anomaly_score=72,
            invoice_authenticity_score=25,
            behavioral_deviation_flags=[
                "new_banking_instructions",
                "urgency_paired_with_finance",
            ],
        ),
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_ANALYSIS,
        source_agent="email_risk_scoring_001",
        payload=payload.model_dump(mode="json"),
    )

    path = tmp_path / "tenant_demo.jsonl"
    append_record(path, record)
    records = read_records(path)
    assert records[0].payload["risk_analysis"]["vendor_fraud_score"] == 88
    assert records[0].payload["risk_analysis"]["wire_transfer_anomaly_score"] == 72
    assert records[0].payload["risk_analysis"]["invoice_authenticity_score"] == 25
    assert records[0].payload["risk_analysis"]["behavioral_deviation_flags"] == [
        "new_banking_instructions",
        "urgency_paired_with_finance",
    ]
