"""Tests for the ghost-thread continuity detector.

Covers the pure-function detector ``score_ghost_thread`` itself plus the
integration into ``_overlay_ransomware_precursor`` so a detected ghost
thread correctly lifts the final ``risk_score`` end-to-end.
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
from core.scoring.ghost_thread_detector import (
    GhostThreadAssessment,
    score_ghost_thread,
)


# ---------------------------------------------------------------------------
# Pure-function detector tests
# ---------------------------------------------------------------------------


def test_none_subject_returns_zero() -> None:
    result = score_ghost_thread(subject=None, headers={})
    assert result == GhostThreadAssessment(score=0, indicators=())


def test_empty_subject_returns_zero() -> None:
    result = score_ghost_thread(subject="", headers={})
    assert result == GhostThreadAssessment(score=0, indicators=())


def test_non_threading_subject_returns_zero() -> None:
    """Subjects without a Re:/Fwd: prefix never fire ghost-thread."""

    result = score_ghost_thread(
        subject="Vendor invoice attached",
        headers={},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_re_prefix_with_no_threading_headers_is_ghost_thread() -> None:
    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={},
    )
    assert result.score == 55
    assert result.indicators == ("ghost_thread_subject",)


def test_fwd_prefix_with_no_threading_headers_is_ghost_thread() -> None:
    result = score_ghost_thread(
        subject="Fwd: Payment instructions",
        headers={},
    )
    assert result.score == 55
    assert result.indicators == ("ghost_thread_subject",)


def test_fw_short_prefix_with_no_threading_headers_is_ghost_thread() -> None:
    result = score_ghost_thread(
        subject="Fw: Payment instructions",
        headers={},
    )
    assert result.score == 55


def test_lowercase_re_prefix_fires() -> None:
    result = score_ghost_thread(
        subject="re: invoice",
        headers={},
    )
    assert result.score == 55


def test_uppercase_re_prefix_fires() -> None:
    result = score_ghost_thread(
        subject="RE: invoice",
        headers={},
    )
    assert result.score == 55


def test_bracketed_counter_re_prefix_fires() -> None:
    """Outlook-style ``Re[2]:`` prefix should also count."""

    result = score_ghost_thread(
        subject="Re[2]: invoice",
        headers={},
    )
    assert result.score == 55


def test_re_in_middle_of_subject_does_not_fire() -> None:
    """``Vendor reminder: Re: invoice`` does not start with Re:."""

    result = score_ghost_thread(
        subject="Vendor reminder: Re: invoice",
        headers={},
    )
    assert result.score == 0


def test_in_reply_to_present_disables_ghost_thread() -> None:
    """Legitimate threaded replies must not be flagged."""

    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={"In-Reply-To": "<abc123@vendor.example>"},
    )
    assert result.score == 0
    assert result.indicators == ()


def test_references_present_disables_ghost_thread() -> None:
    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={"References": "<abc123@vendor.example>"},
    )
    assert result.score == 0


def test_both_threading_headers_present_disables_ghost_thread() -> None:
    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={
            "In-Reply-To": "<abc123@vendor.example>",
            "References": "<abc123@vendor.example> <def456@vendor.example>",
        },
    )
    assert result.score == 0


def test_empty_in_reply_to_value_is_treated_as_missing() -> None:
    """An empty header value is not real threading."""

    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={"In-Reply-To": ""},
    )
    assert result.score == 55


def test_whitespace_only_in_reply_to_is_treated_as_missing() -> None:
    result = score_ghost_thread(
        subject="Re: Vendor invoice approval",
        headers={"In-Reply-To": "   "},
    )
    assert result.score == 55


def test_case_insensitive_header_keys() -> None:
    """Header key casing should not change the result."""

    lower = score_ghost_thread(
        subject="Re: invoice",
        headers={"in-reply-to": "<abc@vendor.example>"},
    )
    upper = score_ghost_thread(
        subject="Re: invoice",
        headers={"IN-REPLY-TO": "<abc@vendor.example>"},
    )
    assert lower == upper
    assert lower.score == 0


def test_headers_none_with_threading_subject_still_fires() -> None:
    result = score_ghost_thread(
        subject="Re: invoice",
        headers=None,
    )
    assert result.score == 55


# ---------------------------------------------------------------------------
# Integration with the scoring agent overlay
# ---------------------------------------------------------------------------


def _build_payload(*, risk_score: int = 10) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        summary="ghost thread integration test",
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


def _build_inbound(
    *,
    subject: str | None = "Re: Vendor invoice approval",
    headers: dict[str, str] | None = None,
) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender="vendor@vendor.example",
        recipient="ap@northstar-customer.example",
        subject=subject,
        body_plain="Please process the attached invoice.",
        headers=headers or {},
    )


def test_overlay_lifts_risk_on_ghost_thread() -> None:
    """End-to-end: a ghost-thread subject lifts the LLM's risk_score floor."""

    analysis = _build_payload(risk_score=10)
    inbound = _build_inbound(
        subject="Re: Vendor invoice approval",
        headers={},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score >= 55


def test_overlay_does_not_lift_when_threading_headers_present() -> None:
    """Legitimate threaded replies must not be lifted by ghost-thread."""

    analysis = _build_payload(risk_score=20)
    inbound = _build_inbound(
        subject="Re: Vendor invoice approval",
        headers={"In-Reply-To": "<abc123@vendor.example>"},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score == 20


def test_overlay_preserves_higher_llm_risk_against_lower_ghost_score() -> None:
    analysis = _build_payload(risk_score=80)
    inbound = _build_inbound(
        subject="Re: Vendor invoice approval",
        headers={},
    )
    result = _overlay_ransomware_precursor(analysis, inbound)
    assert result.risk_analysis.risk_score == 80


def test_overlay_lift_only_invariant_holds_with_ghost_thread() -> None:
    for baseline in (0, 30, 55, 70, 100):
        analysis = _build_payload(risk_score=baseline)
        inbound = _build_inbound(
            subject="Re: Vendor invoice approval",
            headers={},
        )
        result = _overlay_ransomware_precursor(analysis, inbound)
        assert result.risk_analysis.risk_score >= baseline
        assert 0 <= result.risk_analysis.risk_score <= 100
