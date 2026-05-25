from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailInboundPayload,
)
from core.operator_state.security_profile import (
    ForcedEscalationEvidence,
    resolve_profile_for_email,
)
from core.scoring.email_authentication_detector import (
    EmailAuthenticationAssessment,
    score_email_authentication,
)
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor


def test_missing_authentication_results_returns_zero() -> None:
    result = score_email_authentication(
        sender="billing@vendor.example",
        headers={},
    )

    assert result == EmailAuthenticationAssessment(
        score=0,
        from_domain="vendor.example",
        spf_result=None,
        dkim_result=None,
        dmarc_result=None,
        indicators=(),
    )


def test_google_style_authentication_results_passes_without_lift() -> None:
    result = score_email_authentication(
        sender='"Vendor AP" <billing@vendor.example>',
        headers={
            "Authentication-Results": (
                "mx.google.com; dkim=pass header.i=@vendor.example; "
                "spf=pass smtp.mailfrom=vendor.example; "
                "dmarc=pass (p=reject sp=reject dis=none) header.from=vendor.example"
            )
        },
    )

    assert result.score == 0
    assert result.from_domain == "vendor.example"
    assert result.spf_result == "pass"
    assert result.dkim_result == "pass"
    assert result.dmarc_result == "pass"
    assert result.indicators == ()


def test_microsoft_bestguesspass_normalizes_to_pass() -> None:
    result = score_email_authentication(
        sender="billing@vendor.example",
        headers={
            "Authentication-Results": (
                "spf=pass smtp.mailfrom=vendor.example; "
                "dkim=pass (signature was verified) header.d=vendor.example; "
                "dmarc=bestguesspass action=none header.from=vendor.example; "
                "compauth=pass reason=100"
            )
        },
    )

    assert result.score == 0
    assert result.dmarc_result == "pass"


def test_proofpoint_style_dmarc_fail_is_high_confidence_signal() -> None:
    result = score_email_authentication(
        sender="billing@vendor.example",
        headers={
            "Authentication-Results": (
                "spf=softfail smtp.mailfrom=vendor.example; "
                "dkim=fail (body hash did not verify) header.d=vendor.example; "
                "dmarc=fail action=quarantine header.from=vendor.example"
            )
        },
    )

    assert result.score == 85
    assert result.indicators == ("spf_softfail", "dkim_fail", "dmarc_fail")


def test_mimecast_style_dmarc_none_is_unknown_not_safe() -> None:
    result = score_email_authentication(
        sender="billing@vendor.example",
        headers={
            "authentication-results": (
                "spf=pass smtp.mailfrom=vendor.example; "
                "dkim=none; dmarc=none header.from=vendor.example"
            )
        },
    )

    assert result.score == 30
    assert result.indicators == ("dkim_none", "dmarc_none")


def test_case_insensitive_authentication_results_header_name() -> None:
    result = score_email_authentication(
        sender="billing@vendor.example",
        headers={"AUTHENTICATION-RESULTS": "spf=fail; dkim=pass; dmarc=pass"},
    )

    assert result.score == 45
    assert result.indicators == ("spf_fail",)


def _analysis_payload(*, risk_score: int = 10) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        summary="email authentication integration test",
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


def _inbound(headers: dict[str, str]) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please process the attached invoice.",
        headers=headers,
    )


def _profile(profile: str):
    return resolve_profile_for_email(
        tenant_default=profile,  # type: ignore[arg-type]
        addon_detectors=(),
        evidence=ForcedEscalationEvidence(llm_risk_score=10),
    )


def test_overlay_lifts_risk_on_dmarc_fail_for_medium_profile() -> None:
    result = _overlay_ransomware_precursor(
        _analysis_payload(risk_score=10),
        _inbound({"Authentication-Results": "spf=pass; dkim=pass; dmarc=fail"}),
        profile_resolution=_profile("medium"),
    )

    assert result.risk_analysis.risk_score == 75
    assert "email_authentication:dmarc_fail" in result.risk_analysis.risk_factors
    assert "email_authentication:dmarc_fail" in result.risk_analysis.phishing_signals


def test_overlay_skips_email_authentication_for_low_profile() -> None:
    result = _overlay_ransomware_precursor(
        _analysis_payload(risk_score=10),
        _inbound({"Authentication-Results": "spf=pass; dkim=pass; dmarc=fail"}),
        profile_resolution=_profile("low"),
    )

    assert result.risk_analysis.risk_score == 10
    assert result.risk_analysis.risk_factors == []
    assert result.risk_analysis.phishing_signals == []


def test_overlay_uses_stricter_floor_for_high_profile() -> None:
    result = _overlay_ransomware_precursor(
        _analysis_payload(risk_score=10),
        _inbound({"Authentication-Results": "spf=pass; dkim=pass; dmarc=fail"}),
        profile_resolution=_profile("high"),
    )

    assert result.risk_analysis.risk_score == 85


def test_overlay_preserves_higher_llm_score_and_lift_only_invariant() -> None:
    result = _overlay_ransomware_precursor(
        _analysis_payload(risk_score=95),
        _inbound({"Authentication-Results": "spf=fail; dkim=fail; dmarc=fail"}),
        profile_resolution=_profile("medium"),
    )

    assert result.risk_analysis.risk_score == 95
    assert 0 <= result.risk_analysis.risk_score <= 100

