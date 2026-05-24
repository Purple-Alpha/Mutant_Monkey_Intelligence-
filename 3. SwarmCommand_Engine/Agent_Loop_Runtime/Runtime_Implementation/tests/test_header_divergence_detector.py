"""Tests for the From / Reply-To / Return-Path header divergence detector.

Covers the pure-function detector ``score_header_divergence`` itself plus
the integration into ``_overlay_ransomware_precursor`` so that divergence
correctly lifts the final ``risk_score`` end-to-end.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailInboundPayload,
)
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor
from core.scoring.header_divergence_detector import (
    HeaderDivergenceAssessment,
    score_header_divergence,
)


# ---------------------------------------------------------------------------
# Pure-function detector tests
# ---------------------------------------------------------------------------


def test_empty_sender_returns_zero_score() -> None:
    result = score_header_divergence(sender="", headers={"Reply-To": "x@y.com"})
    assert result == HeaderDivergenceAssessment(score=0, indicators=())


def test_no_headers_returns_zero_score() -> None:
    result = score_header_divergence(sender="vendor@example.com", headers={})
    assert result == HeaderDivergenceAssessment(score=0, indicators=())


def test_none_headers_returns_zero_score() -> None:
    result = score_header_divergence(sender="vendor@example.com", headers=None)
    assert result == HeaderDivergenceAssessment(score=0, indicators=())


def test_identical_from_and_reply_to_returns_zero() -> None:
    result = score_header_divergence(
        sender="vendor@example.com",
        headers={"Reply-To": "support@example.com"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_from_subdomain_against_root_reply_to_is_not_divergence() -> None:
    """Legit subdomain mail (m.vendor.com -> vendor.com) is not divergence."""

    result = score_header_divergence(
        sender="news@m.vendor.example",
        headers={"Reply-To": "support@vendor.example"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_from_root_against_subdomain_reply_to_is_not_divergence() -> None:
    """The reverse direction (vendor.com -> m.vendor.com) is also fine."""

    result = score_header_divergence(
        sender="support@vendor.example",
        headers={"Reply-To": "noreply@m.vendor.example"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_from_reply_to_different_roots_is_divergence() -> None:
    result = score_header_divergence(
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@attacker.example"},
    )
    assert result.indicators == ("from_reply_to_divergence",)
    assert result.score == 65


def test_lookalike_tld_is_divergence() -> None:
    """Classic BEC: vendor.com vs vendor.co — same name, different TLD."""

    result = score_header_divergence(
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@vendor.exampleco"},
    )
    assert "from_reply_to_divergence" in result.indicators
    assert result.score >= 65


def test_return_path_divergence_alone_is_moderate() -> None:
    result = score_header_divergence(
        sender="news@vendor.example",
        headers={"Return-Path": "<bounce@esp.example>"},
    )
    assert result.indicators == ("from_return_path_divergence",)
    assert result.score == 45


def test_sender_header_divergence_alone_is_lowest() -> None:
    result = score_header_divergence(
        sender="ceo@vendor.example",
        headers={"Sender": "assistant@attacker.example"},
    )
    assert result.indicators == ("from_sender_header_divergence",)
    assert result.score == 35


def test_reply_to_and_return_path_divergence_combines() -> None:
    result = score_header_divergence(
        sender="billing@vendor.example",
        headers={
            "Reply-To": "billing@attacker.example",
            "Return-Path": "<bounce@attacker.example>",
        },
    )
    assert "from_reply_to_divergence" in result.indicators
    assert "from_return_path_divergence" in result.indicators
    # Reply-To (65) is the max contributor, +10 combination bonus = 75
    assert result.score == 75


def test_all_three_divergences_combine_with_cap() -> None:
    result = score_header_divergence(
        sender="ceo@vendor.example",
        headers={
            "Reply-To": "reply@attacker-one.example",
            "Return-Path": "<bounce@attacker-two.example>",
            "Sender": "helper@attacker-three.example",
        },
    )
    assert len(result.indicators) == 3
    # max contributor is Reply-To at 65, +10 bonus -> 75 (still under 90 cap)
    assert result.score == 75


def test_score_is_capped_at_max() -> None:
    """Even with multiple high-scoring divergences, score stays <= 90."""

    result = score_header_divergence(
        sender="ceo@vendor.example",
        headers={
            "Reply-To": "reply@attacker-one.example",
            "Return-Path": "<bounce@attacker-two.example>",
            "Sender": "helper@attacker-three.example",
        },
    )
    assert result.score <= 90


def test_case_insensitive_header_keys() -> None:
    """Header dict casing should not matter (RFC 5322 case-insensitive)."""

    result_lower = score_header_divergence(
        sender="billing@vendor.example",
        headers={"reply-to": "billing@attacker.example"},
    )
    result_upper = score_header_divergence(
        sender="billing@vendor.example",
        headers={"REPLY-TO": "billing@attacker.example"},
    )
    result_mixed = score_header_divergence(
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@attacker.example"},
    )
    assert result_lower == result_upper == result_mixed
    assert result_lower.score == 65


def test_case_insensitive_domains() -> None:
    """Domain comparison should be case-insensitive."""

    result = score_header_divergence(
        sender="billing@VENDOR.example",
        headers={"Reply-To": "support@vendor.EXAMPLE"},
    )
    assert result.score == 0


def test_display_name_form_is_parsed() -> None:
    """RFC 5322 display-name addresses should parse correctly."""

    result = score_header_divergence(
        sender='"Vendor Billing" <billing@vendor.example>',
        headers={
            "Reply-To": '"Attacker" <billing@attacker.example>',
        },
    )
    assert "from_reply_to_divergence" in result.indicators
    assert result.score == 65


def test_bracketed_return_path_is_parsed() -> None:
    """Return-Path values commonly appear as <addr@host> with brackets."""

    result = score_header_divergence(
        sender="vendor@vendor.example",
        headers={"Return-Path": "<bounce@esp.example>"},
    )
    assert "from_return_path_divergence" in result.indicators


def test_malformed_sender_returns_zero() -> None:
    result = score_header_divergence(
        sender="not-an-email",
        headers={"Reply-To": "x@y.example"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_malformed_reply_to_is_ignored_not_treated_as_divergence() -> None:
    """An unparseable Reply-To value should not trigger a false positive."""

    result = score_header_divergence(
        sender="vendor@vendor.example",
        headers={"Reply-To": "garbage"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_empty_reply_to_value_is_ignored() -> None:
    result = score_header_divergence(
        sender="vendor@vendor.example",
        headers={"Reply-To": ""},
    )
    assert result.score == 0
    assert result.indicators == ()


# ---------------------------------------------------------------------------
# Integration with the scoring agent overlay
# ---------------------------------------------------------------------------


def _build_payload(
    *,
    risk_score: int = 10,
    vendor_fraud_score: int = 0,
    wire_transfer_anomaly_score: int = 0,
) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        summary="header divergence integration test",
        action_items=[],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=vendor_fraud_score,
            wire_transfer_anomaly_score=wire_transfer_anomaly_score,
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


def _build_inbound(
    *,
    sender: str = "vendor@vendor.example",
    headers: dict[str, str] | None = None,
) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please process the attached invoice.",
        headers=headers or {},
    )


def test_overlay_lifts_risk_when_reply_to_diverges() -> None:
    """End-to-end: a divergent Reply-To lifts the LLM's risk_score floor."""

    analysis = _build_payload(risk_score=10)
    inbound = _build_inbound(
        headers={"Reply-To": "billing@attacker.example"},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score >= 65
    assert result.risk_analysis.risk_score >= analysis.risk_analysis.risk_score


def test_overlay_preserves_higher_llm_risk_against_lower_divergence_score() -> None:
    """An LLM-confident high score is preserved when divergence is lower."""

    analysis = _build_payload(risk_score=95)
    inbound = _build_inbound(
        headers={"Reply-To": "billing@attacker.example"},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score == 95


def test_overlay_does_not_lift_when_no_divergence() -> None:
    """An email with no divergent headers should not be lifted by the detector."""

    analysis = _build_payload(risk_score=20)
    inbound = _build_inbound(
        headers={"Reply-To": "support@vendor.example"},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score == 20


def test_overlay_lift_only_invariant_holds_under_divergence() -> None:
    """The lift-only invariant must hold even when divergence is present."""

    for baseline in (0, 25, 50, 75, 100):
        analysis = _build_payload(risk_score=baseline)
        inbound = _build_inbound(
            headers={
                "Reply-To": "reply@attacker-one.example",
                "Return-Path": "<bounce@attacker-two.example>",
            },
        )
        result = _overlay_ransomware_precursor(analysis, inbound)
        assert result.risk_analysis.risk_score >= baseline
        assert 0 <= result.risk_analysis.risk_score <= 100
