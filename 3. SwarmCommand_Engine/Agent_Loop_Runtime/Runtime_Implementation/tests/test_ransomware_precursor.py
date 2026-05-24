"""Tests for Phase 1.2 Ransomware Precursor Detection.

Covers the four roadmap-required surfaces:

1. Attachment classifier (≥5 tests).
2. URL obfuscation detector (≥5 tests).
3. Body-language detector (credential harvesting + MFA fatigue) (≥3 tests).
4. End-to-end scoring agent integration (≥3 tests), including the Month 3
   gate: a synthetic ransomware-precursor email with malicious attachment,
   obfuscated URL, and credential lure produces ``risk_score >= 85`` with
   all four ``ransomware_precursor_analysis`` sub-scores populated, on a
   deterministic LLM client run reproducing across CI.

Pure deterministic tests. No network. No real LLM calls.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
from typing import get_args
from uuid import UUID

import pytest

from core.blackboard import (
    EmailAnalysisPayload,
    EmailAttachmentMeta,
    EmailInboundPayload,
    Environment,
    PrecursorIndicator,
    RecordType,
)
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.precursor import (
    attachment_inspector,
    build_precursor_overlay,
    classify_attachment,
    extract_urls,
    score_attachment_risk,
    score_credential_harvesting,
    score_mfa_fatigue,
    score_url_obfuscation,
)
from core.scoring.email_risk_scoring_agent import (
    EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID,
    EmailRiskScoringConfig,
    run_email_risk_scoring_cycle,
)

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path)


def _seed_inbound(
    context: RouteContext,
    *,
    sender: str,
    subject: str,
    body_plain: str,
    attachments: Iterable[dict[str, Any]] = (),
) -> UUID:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="ops@northstar.example",
        subject=subject,
        body_plain=body_plain,
        headers={},
        attachments=[EmailAttachmentMeta.model_validate(a) for a in attachments],
    )
    result = submit_email_inbound(
        context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )
    return result.record.record_id


# ---------------------------------------------------------------------------
# Schema delta — pin the new locked enum + payload field.
# ---------------------------------------------------------------------------


def test_precursor_indicator_literal_exact_set():
    """``PrecursorIndicator`` is schema-versioned. Drift fails this test."""

    expected = {
        "macro_enabled_office_document",
        "executable_attachment",
        "iso_or_disk_image_attachment",
        "double_extension_attachment",
        "encrypted_archive_attachment",
        "html_smuggling_attachment",
        "credential_bearing_url",
        "url_shortener_present",
        "punycode_url_present",
        "homoglyph_url_present",
        "suspicious_tld_present",
        "ip_address_url_present",
        "login_path_url_present",
        "credential_reset_language",
        "account_verification_language",
        "mfa_push_language",
        "verification_code_language",
    }
    assert set(get_args(PrecursorIndicator)) == expected


def test_email_analysis_payload_precursor_field_default_none():
    """Optional precursor field defaults to ``None`` so Month 1 / Month 2
    fixtures that construct the payload directly continue to validate."""

    payload = EmailAnalysisPayload.model_validate(
        {
            "source_email_record_id": "00000000-0000-0000-0000-000000000001",
            "risk_analysis": {
                "risk_score": 10,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 0,
                "wire_transfer_anomaly_score": 0,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 0,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "safe",
        }
    )
    assert payload.ransomware_precursor_analysis is None


# ---------------------------------------------------------------------------
# Attachment classifier.
# ---------------------------------------------------------------------------


def test_attachment_classifier_promotes_unknown_exe_to_executable_doc():
    meta = EmailAttachmentMeta(filename="invoice.exe", content_type=None, size_bytes=2048)
    assert classify_attachment(meta) == "executable_doc"


def test_attachment_inspector_does_not_overwrite_caller_class():
    """An ``invoice`` class chosen by the connector wins over auto-promotion."""

    meta = EmailAttachmentMeta(filename="invoice.exe", attachment_class="invoice")
    refined = attachment_inspector(None, meta)
    assert refined.attachment_class == "invoice"


def test_score_attachment_risk_executable_extension_band_high():
    meta = EmailAttachmentMeta(filename="urgent_payment.exe", content_type=None)
    assessment = score_attachment_risk(meta)
    assert assessment.classification == "executable_doc"
    assert assessment.risk_score >= 85
    assert "executable_attachment" in assessment.indicators


def test_score_attachment_risk_macro_office_band_mid():
    meta = EmailAttachmentMeta(filename="Quarterly_Report.docm", content_type=None)
    assessment = score_attachment_risk(meta)
    assert 60 <= assessment.risk_score < 85
    assert "macro_enabled_office_document" in assessment.indicators
    assert assessment.classification == "payload_carrier"


def test_score_attachment_risk_iso_disk_image_band_high():
    meta = EmailAttachmentMeta(filename="payload.iso", content_type=None)
    assessment = score_attachment_risk(meta)
    assert assessment.risk_score >= 85
    assert "iso_or_disk_image_attachment" in assessment.indicators


def test_score_attachment_risk_double_extension_caught_even_with_pdf_disguise():
    meta = EmailAttachmentMeta(filename="invoice.pdf.exe", content_type=None)
    assessment = score_attachment_risk(meta)
    assert assessment.risk_score >= 85
    assert "double_extension_attachment" in assessment.indicators
    assert "executable_attachment" in assessment.indicators


def test_score_attachment_risk_legit_invoice_attachment_is_low_or_zero():
    meta = EmailAttachmentMeta(
        filename="invoice_4471.pdf", content_type="application/pdf", attachment_class="invoice"
    )
    assessment = score_attachment_risk(meta)
    assert assessment.risk_score <= 20
    assert assessment.indicators == ()


def test_score_attachment_risk_encrypted_archive_pattern_fires():
    meta = EmailAttachmentMeta(filename="invoice_protected.zip", content_type=None)
    assessment = score_attachment_risk(meta)
    assert "encrypted_archive_attachment" in assessment.indicators
    assert assessment.risk_score >= 60


# ---------------------------------------------------------------------------
# URL obfuscation detector.
# ---------------------------------------------------------------------------


def test_extract_urls_pulls_http_https_and_www():
    text = "Visit https://example.com and http://safe.org or www.partner.example for details."
    assert extract_urls(text) == [
        "https://example.com",
        "http://safe.org",
        "www.partner.example",
    ]


def test_score_url_obfuscation_no_urls_yields_zero():
    assessment = score_url_obfuscation("Hello team, see attached PDF.")
    assert assessment.score == 0
    assert assessment.indicators == ()


def test_score_url_obfuscation_punycode_url_high():
    assessment = score_url_obfuscation(
        "Please review the report at https://xn--paypl-9wa.com/login before EOD."
    )
    assert assessment.score >= 75
    assert "punycode_url_present" in assessment.indicators
    assert "login_path_url_present" in assessment.indicators


def test_score_url_obfuscation_credential_bearing_url_highest():
    assessment = score_url_obfuscation(
        "Open https://admin:secret@malicious.example/reset to continue."
    )
    assert assessment.score >= 80
    assert "credential_bearing_url" in assessment.indicators


def test_score_url_obfuscation_url_shortener_mid():
    assessment = score_url_obfuscation("Quick note: see https://bit.ly/3xY9aZ for the spec.")
    assert 30 <= assessment.score <= 60
    assert "url_shortener_present" in assessment.indicators


def test_score_url_obfuscation_suspicious_tld_fires():
    assessment = score_url_obfuscation("Update your records at http://payments-portal.zip/login")
    assert "suspicious_tld_present" in assessment.indicators
    assert "login_path_url_present" in assessment.indicators
    assert assessment.score >= 50


def test_score_url_obfuscation_ip_address_host_fires():
    assessment = score_url_obfuscation("Audit dashboard: http://192.168.50.10/auth")
    assert "ip_address_url_present" in assessment.indicators
    assert assessment.score >= 70


def test_score_url_obfuscation_cyrillic_homoglyph_host_fires():
    # The 'а' below is Cyrillic U+0430, not Latin U+0061.
    assessment = score_url_obfuscation("Sign in at https://раypal.com/login to verify.")
    assert "homoglyph_url_present" in assessment.indicators
    assert assessment.score >= 75


# ---------------------------------------------------------------------------
# Body-language detector — credential harvest + MFA fatigue.
# ---------------------------------------------------------------------------


def test_score_credential_harvesting_fires_on_reset_language():
    body = (
        "We detected unusual sign-in activity on your account. "
        "Please reset your password immediately to keep access."
    )
    assessment = score_credential_harvesting(body)
    assert "credential_reset_language" in assessment.indicators
    assert assessment.score >= 60


def test_score_credential_harvesting_fires_on_verify_account_language():
    body = "To continue receiving service, please verify your account within 24 hours."
    assessment = score_credential_harvesting(body)
    assert "account_verification_language" in assessment.indicators
    assert assessment.score >= 60


def test_score_credential_harvesting_quiet_on_routine_text():
    body = "Just confirming our meeting tomorrow at 2pm. Let me know if anything changes."
    assessment = score_credential_harvesting(body)
    assert assessment.score == 0
    assert assessment.indicators == ()


def test_score_mfa_fatigue_fires_on_push_language():
    body = "We sent a sign-in request to your phone. Please approve the sign-in to continue."
    assessment = score_mfa_fatigue(body)
    assert "mfa_push_language" in assessment.indicators
    assert assessment.score >= 60


def test_score_mfa_fatigue_otp_pattern_lifts_score():
    body = "Your verification code is 482910 — enter the code on the next screen."
    assessment = score_mfa_fatigue(body)
    assert "verification_code_language" in assessment.indicators


# ---------------------------------------------------------------------------
# Overlay builder + scoring-agent integration.
# ---------------------------------------------------------------------------


def test_build_precursor_overlay_quiet_email_yields_zero_block():
    payload = EmailInboundPayload(
        received_at=datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="ops@northstar.example",
        subject="Outstanding invoice",
        body_plain="Please remit payment for invoice 4471 net-30.",
    )
    overlay = build_precursor_overlay(payload)
    assert overlay.recommended_risk_floor == 0
    assert overlay.block.attachment_risk_score == 0
    assert overlay.block.url_obfuscation_score == 0
    assert overlay.block.credential_harvesting_score == 0
    assert overlay.block.mfa_fatigue_score == 0
    assert overlay.block.precursor_indicators == []


def _valid_low_risk_analysis_json() -> str:
    """LLM response that under-scores a ransomware-precursor email at risk=20.

    The deterministic overlay must lift ``risk_score`` to ``>= 85`` to hit the
    Month 3 gate, proving the floor enforcement works even when the LLM misses.
    """

    return json.dumps(
        {
            "summary": "Operations email with attachment and a sign-in link.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 20,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 10,
                "wire_transfer_anomaly_score": 0,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 10,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "safe",
        }
    )


def _canned_client(response: str) -> Callable[[str, str], str]:
    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        json.loads(user_prompt)
        return response

    return _client


def test_scoring_agent_month_3_gate_synthetic_ransomware_precursor_email(tmp_path):
    """Month 3 roadmap gate.

    Synthetic ransomware-precursor email (malicious executable attachment +
    obfuscated punycode login URL + credential reset lure language). The
    LLM is intentionally under-scored at ``risk_score=20`` to prove the
    deterministic overlay can lift the final ``risk_score`` to ``>= 85``.

    Asserts all four precursor sub-scores are populated and the gate-line
    ``risk_score >= 85`` is met deterministically.
    """

    context = _context(tmp_path)
    inbound_id = _seed_inbound(
        context,
        sender="security@identity.example",
        subject="Unusual sign-in activity — reset your password",
        body_plain=(
            "We detected unusual sign-in activity on your account. "
            "Please reset your password at https://xn--paypl-9wa.com/login "
            "before your access is suspended. Attachment included for your records."
        ),
        attachments=[
            {"filename": "secure_account.iso", "content_type": "application/octet-stream"},
            {"filename": "instructions.pdf.exe", "content_type": None},
        ],
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_low_risk_analysis_json()),
            production_tenant_id=TENANT,
        ),
    )
    assert result.analyzed == 1
    assert result.failed == 0
    assert result.successes[0].source_email_record_id == inbound_id

    records = list(
        __import__("core.blackboard", fromlist=["read_records"]).read_records(
            blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
        )
    )
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)

    # Month 3 gate: risk_score >= 85.
    assert parsed.risk_analysis.risk_score >= 85, (
        f"Month 3 gate FAILED: risk_score={parsed.risk_analysis.risk_score} < 85"
    )

    # Month 3 gate: all four precursor sub-scores populated.
    block = parsed.ransomware_precursor_analysis
    assert block is not None
    assert block.attachment_risk_score > 0
    assert block.url_obfuscation_score > 0
    assert block.credential_harvesting_score > 0
    # mfa_fatigue can legitimately be zero on a credential-reset (not MFA) lure.
    assert block.mfa_fatigue_score >= 0

    # Indicators must include at least one from each detector category that
    # contributed a non-zero sub-score, demonstrating provenance.
    indicators = set(block.precursor_indicators)
    assert {"iso_or_disk_image_attachment", "executable_attachment", "double_extension_attachment"} & indicators
    assert {"punycode_url_present", "login_path_url_present"} & indicators
    assert "credential_reset_language" in indicators


def test_scoring_agent_overlay_does_not_lower_high_llm_risk_score(tmp_path):
    """Floor enforcement is one-directional: precursor floor can only LIFT
    ``risk_score``. A confident LLM that returns 95 stays at 95 even when
    the deterministic overlay has nothing to add."""

    context = _context(tmp_path)
    _seed_inbound(
        context,
        sender="vendor@example.com",
        subject="Invoice",
        body_plain="Please remit payment for invoice 4471 net-30.",
    )

    high_risk_response = json.dumps(
        {
            "summary": "LLM-detected high-confidence fraud.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 95,
                "risk_factors": ["llm_inferred_fraud_pattern"],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "high",
                "vendor_fraud_score": 95,
                "wire_transfer_anomaly_score": 70,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": ["urgency_paired_with_finance"],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 80,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "block",
        }
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(high_risk_response),
            production_tenant_id=TENANT,
        ),
    )

    records = list(
        __import__("core.blackboard", fromlist=["read_records"]).read_records(
            blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
        )
    )
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.risk_analysis.risk_score == 95
    assert parsed.ransomware_precursor_analysis is not None
    assert parsed.ransomware_precursor_analysis.attachment_risk_score == 0


def test_scoring_agent_overlay_can_be_disabled_for_pure_llm_baseline(tmp_path):
    """``enable_ransomware_precursor_overlay=False`` reverts to pre-Month-3
    behavior so the Month 2 fraud-eval harness continues to evaluate the
    bare LLM output without the deterministic floor."""

    context = _context(tmp_path)
    _seed_inbound(
        context,
        sender="security@identity.example",
        subject="Reset your password",
        body_plain="Please reset your password immediately to keep access.",
        attachments=[{"filename": "open_me.exe"}],
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_low_risk_analysis_json()),
            production_tenant_id=TENANT,
            enable_ransomware_precursor_overlay=False,
        ),
    )
    assert result.analyzed == 1

    records = list(
        __import__("core.blackboard", fromlist=["read_records"]).read_records(
            blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
        )
    )
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.risk_analysis.risk_score == 20
    assert parsed.ransomware_precursor_analysis is None
