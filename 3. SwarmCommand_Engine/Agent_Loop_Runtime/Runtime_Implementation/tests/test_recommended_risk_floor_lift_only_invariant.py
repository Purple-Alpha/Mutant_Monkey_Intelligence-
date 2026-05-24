"""Lift-only invariant property test for the ransomware-precursor overlay.

The most important runtime invariant in NorthStar Inbox Shield is that the
deterministic precursor overlay applied by
``_overlay_ransomware_precursor`` can ONLY raise the LLM-derived
``risk_score`` — never lower it. The overlay sits on every email's analysis
payload after LLM validation, so a regression here would silently downgrade
real fraud or ransomware-precursor signals.

The invariant in plain terms:

    For any inbound email, any LLM-produced analysis payload, and any
    (clamped or out-of-contract) policy-state lift parameters, the final
    ``risk_score`` returned by ``_overlay_ransomware_precursor`` satisfies:

        result.risk_analysis.risk_score >= input.risk_analysis.risk_score
        0 <= result.risk_analysis.risk_score <= 100

It is verified two ways here:

1. Hand-written edge-case tests pinning the corners of the parameter
   space (zero / max LLM risk, zero / max lifts, benign / dangerous
   inbound shapes, fraud-lift gate on / off, negative lifts).
2. A randomized property loop seeded for reproducibility that hits the
   interior of the parameter space across 500 generated cases.

If this test suite ever fails, the runtime baseline contract is broken —
do not paper over it, find the regression.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from uuid import uuid4

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailAttachmentMeta,
    EmailInboundPayload,
)
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor


# ---------------------------------------------------------------------------
# Shared builders
# ---------------------------------------------------------------------------


def _build_analysis(
    *,
    risk_score: int,
    vendor_fraud_score: int = 0,
    wire_transfer_anomaly_score: int = 0,
) -> EmailAnalysisPayload:
    """Build a minimal valid ``EmailAnalysisPayload`` with controllable scores."""

    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        summary="lift-only invariant property test",
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


def _benign_inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender="ap@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Routine partner check-in",
        body_plain="Hi, just checking in on Q2 status. Thanks!",
    )


def _dangerous_attachment_inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender="ap@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please open the attached invoice.",
        attachments=[
            EmailAttachmentMeta(
                filename="invoice.exe",
                content_type="application/octet-stream",
            )
        ],
    )


def _suspicious_url_inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender="security@bank.example",
        recipient="ap@northstar-customer.example",
        subject="Verify your account",
        body_plain=(
            "Click here to verify: http://secure-login.bank.example.attacker.ru/"
            "?u=AP&token=xyz%2E%2E%2F%2E%2E"
        ),
    )


def _credential_lure_inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc),
        sender="it-support@example.com",
        recipient="ap@northstar-customer.example",
        subject="Your password is expiring today",
        body_plain=(
            "Your account password is expiring today. Sign in immediately "
            "to reset your password and verify your credentials or your "
            "account will be locked."
        ),
    )


_INBOUND_SHAPES = (
    _benign_inbound,
    _dangerous_attachment_inbound,
    _suspicious_url_inbound,
    _credential_lure_inbound,
)


# ---------------------------------------------------------------------------
# Edge-case pins
# ---------------------------------------------------------------------------


def test_zero_llm_risk_benign_email_with_zero_lifts_stays_zero() -> None:
    """LLM says risk=0 on a benign email with no lifts -> result stays 0."""

    analysis = _build_analysis(risk_score=0)
    result = _overlay_ransomware_precursor(analysis, _benign_inbound())
    assert result.risk_analysis.risk_score == 0


def test_max_llm_risk_benign_email_with_zero_lifts_is_preserved() -> None:
    """LLM says risk=100 on a benign email -> floor cannot lower it."""

    analysis = _build_analysis(risk_score=100)
    result = _overlay_ransomware_precursor(analysis, _benign_inbound())
    assert result.risk_analysis.risk_score == 100


def test_low_llm_risk_dangerous_attachment_is_lifted() -> None:
    """LLM rated low but a dangerous attachment exists -> precursor floor lifts."""

    analysis = _build_analysis(risk_score=5)
    result = _overlay_ransomware_precursor(
        analysis, _dangerous_attachment_inbound()
    )
    assert result.risk_analysis.risk_score >= analysis.risk_analysis.risk_score
    assert result.risk_analysis.risk_score > 0


def test_fraud_lift_does_not_apply_when_no_fraud_signal() -> None:
    """fraud_risk_floor_lift > 0 but LLM has no fraud signal -> no lift."""

    analysis = _build_analysis(
        risk_score=10,
        vendor_fraud_score=5,
        wire_transfer_anomaly_score=5,
    )
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=25,
    )
    assert result.risk_analysis.risk_score == 10


def test_fraud_lift_applies_when_vendor_fraud_signal_present() -> None:
    """fraud_risk_floor_lift > 0 AND vendor_fraud_score >= 40 -> lift applies."""

    analysis = _build_analysis(
        risk_score=50,
        vendor_fraud_score=60,
        wire_transfer_anomaly_score=0,
    )
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=20,
    )
    assert result.risk_analysis.risk_score == 70
    assert result.risk_analysis.risk_score > analysis.risk_analysis.risk_score


def test_fraud_lift_applies_when_wire_transfer_signal_present() -> None:
    """fraud_risk_floor_lift > 0 AND wire_transfer_anomaly_score >= 40 -> lift."""

    analysis = _build_analysis(
        risk_score=45,
        vendor_fraud_score=0,
        wire_transfer_anomaly_score=55,
    )
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=15,
    )
    assert result.risk_analysis.risk_score == 60
    assert result.risk_analysis.risk_score > analysis.risk_analysis.risk_score


def test_fraud_lift_is_clamped_above_100() -> None:
    """fraud_risk_floor_lift cannot push the final risk above 100."""

    analysis = _build_analysis(
        risk_score=95,
        vendor_fraud_score=60,
        wire_transfer_anomaly_score=0,
    )
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=25,
    )
    assert result.risk_analysis.risk_score == 100


def test_negative_lifts_are_clamped_to_zero_and_cannot_lower_risk() -> None:
    """A misconfigured policy with negative lifts cannot lower the score."""

    analysis = _build_analysis(risk_score=42)
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=-50,
        attachment_risk_floor_lift=-50,
        url_obfuscation_floor_lift=-50,
    )
    assert result.risk_analysis.risk_score == 42


def test_oversized_lifts_are_clamped_and_still_lift_only() -> None:
    """Out-of-contract lifts (above the 25 cap) are clamped, still lift-only."""

    analysis = _build_analysis(
        risk_score=10,
        vendor_fraud_score=60,
    )
    result = _overlay_ransomware_precursor(
        analysis,
        _benign_inbound(),
        fraud_risk_floor_lift=999,
        attachment_risk_floor_lift=999,
        url_obfuscation_floor_lift=999,
    )
    assert result.risk_analysis.risk_score >= analysis.risk_analysis.risk_score
    assert 0 <= result.risk_analysis.risk_score <= 100


def test_precursor_sub_score_never_exceeds_final_risk_floor() -> None:
    """Each precursor sub-score must be <= the final risk_score the agent enforces."""

    analysis = _build_analysis(risk_score=0)
    result = _overlay_ransomware_precursor(
        analysis, _dangerous_attachment_inbound()
    )
    block = result.ransomware_precursor_analysis
    assert block is not None
    for sub_score in (
        block.attachment_risk_score,
        block.url_obfuscation_score,
        block.credential_harvesting_score,
        block.mfa_fatigue_score,
    ):
        assert sub_score <= result.risk_analysis.risk_score


# ---------------------------------------------------------------------------
# Randomized property loop
# ---------------------------------------------------------------------------


_LIFT_VALUES = (0, 0, 0, 1, 5, 10, 15, 20, 25, 30, 50, -1, -25, 999)


def _random_inbound(rng: random.Random) -> EmailInboundPayload:
    return rng.choice(_INBOUND_SHAPES)()


def _random_analysis(rng: random.Random) -> EmailAnalysisPayload:
    return _build_analysis(
        risk_score=rng.randint(0, 100),
        vendor_fraud_score=rng.randint(0, 100),
        wire_transfer_anomaly_score=rng.randint(0, 100),
    )


def _random_lifts(rng: random.Random) -> dict[str, int]:
    return {
        "fraud_risk_floor_lift": rng.choice(_LIFT_VALUES),
        "attachment_risk_floor_lift": rng.choice(_LIFT_VALUES),
        "url_obfuscation_floor_lift": rng.choice(_LIFT_VALUES),
    }


def test_lift_only_invariant_random_property_500_cases() -> None:
    """Property: across 500 random (inbound, analysis, lifts) combinations,
    the overlay's final risk_score is always >= the input LLM risk_score
    and always within [0, 100]. Seeded for full reproducibility — if this
    ever fails, the seed in the failure message reproduces the exact case.
    """

    seed = 20260523
    rng = random.Random(seed)

    for case_idx in range(500):
        inbound = _random_inbound(rng)
        analysis = _random_analysis(rng)
        lifts = _random_lifts(rng)

        result = _overlay_ransomware_precursor(analysis, inbound, **lifts)

        baseline = analysis.risk_analysis.risk_score
        final = result.risk_analysis.risk_score

        assert final >= baseline, (
            f"LIFT-ONLY INVARIANT BROKEN at case {case_idx} "
            f"(seed={seed}): baseline_risk={baseline}, final_risk={final}, "
            f"inbound_subject={inbound.subject!r}, "
            f"vendor_fraud_score={analysis.risk_analysis.vendor_fraud_score}, "
            f"wire_transfer_anomaly_score="
            f"{analysis.risk_analysis.wire_transfer_anomaly_score}, "
            f"lifts={lifts}"
        )
        assert 0 <= final <= 100, (
            f"SCHEMA INVARIANT BROKEN at case {case_idx} "
            f"(seed={seed}): final_risk={final} outside [0, 100]"
        )
