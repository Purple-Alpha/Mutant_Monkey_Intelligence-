"""Gate tests for the deterministic 5-axis client-facing rubric mapper.

These tests enforce ``Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md``
§8 gate tests 1–14 (§11 SIGNED 2026-05-25). Each test names the §8 row it
covers in its docstring so an audit can trace coverage end-to-end.

§8.12 (report renderer) is a Pass-2 deliverable per spec §9 and is marked
``pytest.skip`` here; the renderer test will land alongside the renderer
implementation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from core.blackboard.models import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRansomwarePrecursorAnalysis,
    EmailAnalysisRiskAnalysis,
)
from core.scoring.client_facing_rubric import project_client_facing_rubric
from scripts.inbox_shield_daily_digest_demo import demo_digest_llm_client

# Locked axis order from spec §3 / models._CLIENT_FACING_RUBRIC_AXIS_ORDER (D14).
_LOCKED_AXIS_ORDER: tuple[str, ...] = (
    "sender_identity",
    "conversation_continuity",
    "vendor_payment_history",
    "document_integrity",
    "origin_timing",
)


def _payload(
    *,
    risk_score: int = 50,
    risk_factors: list[str] | None = None,
    phishing_signals: list[str] | None = None,
    urgency_signals: list[str] | None = None,
    financial_risk: str = "medium",
    vendor_fraud_score: int = 30,
    wire_transfer_anomaly_score: int = 20,
    invoice_authenticity_score: int | None = None,
    behavioral_deviation_flags: list[str] | None = None,
    impersonation_likelihood: int = 20,
    suspicious_elements: list[str] | None = None,
    forced_escalation_triggers: list[str] | None = None,
    recommended_action: str = "needs_review",
    ransomware_attachment_risk_score: int | None = None,
) -> EmailAnalysisPayload:
    """Construct a minimal valid ``EmailAnalysisPayload`` for the mapper."""
    overlay: EmailAnalysisRansomwarePrecursorAnalysis | None = None
    if ransomware_attachment_risk_score is not None:
        overlay = EmailAnalysisRansomwarePrecursorAnalysis(
            attachment_risk_score=ransomware_attachment_risk_score,
            url_obfuscation_score=0,
            credential_harvesting_score=0,
            mfa_fatigue_score=0,
            precursor_indicators=[],
        )

    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime.now(timezone.utc),
        summary=None,
        action_items=[],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=risk_factors or [],
            phishing_signals=phishing_signals or [],
            urgency_signals=urgency_signals or [],
            financial_risk=financial_risk,
            vendor_fraud_score=vendor_fraud_score,
            wire_transfer_anomaly_score=wire_transfer_anomaly_score,
            invoice_authenticity_score=invoice_authenticity_score,
            behavioral_deviation_flags=behavioral_deviation_flags or [],
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=impersonation_likelihood,
            suspicious_elements=suspicious_elements or [],
            sender_legitimacy_notes=None,
        ),
        recommended_action=recommended_action,
        ransomware_precursor_analysis=overlay,
        forced_escalation_triggers=forced_escalation_triggers or [],
    )


# §8.1 — Exactly five axes emitted in fixed order with fixed names.
def test_exactly_five_axes_in_fixed_order() -> None:
    rubric = project_client_facing_rubric(_payload())
    assert len(rubric.axes) == 5
    assert tuple(a.axis_name for a in rubric.axes) == _LOCKED_AXIS_ORDER


# §8.2 — Each axis score constrained to 0..2; total constrained to 0..10.
def test_axis_score_and_total_bounds() -> None:
    rubric = project_client_facing_rubric(
        _payload(
            risk_score=95,
            vendor_fraud_score=90,
            wire_transfer_anomaly_score=90,
            invoice_authenticity_score=10,
            behavioral_deviation_flags=[
                "new_banking_instructions",
                "lookalike_sender_domain",
                "out_of_band_pressure",
            ],
            impersonation_likelihood=85,
            forced_escalation_triggers=[
                "header_divergence_strong",
                "ghost_thread_detected",
            ],
            ransomware_attachment_risk_score=80,
        )
    )
    assert all(0 <= a.score <= 2 for a in rubric.axes)
    assert 0 <= rubric.axis_total <= 10


# §8.3 — Projection deterministic for same input payload.
def test_projection_is_deterministic() -> None:
    p = _payload(
        risk_score=60,
        behavioral_deviation_flags=["new_banking_instructions"],
        impersonation_likelihood=40,
    )
    a = project_client_facing_rubric(p)
    b = project_client_facing_rubric(p)
    assert a.model_dump() == b.model_dump()


# §8.4 — Known high-risk fixture (risk_score >= 75) cannot emit low rubric
# (axis_total <= 5) unless override fires and is labeled.
def test_high_risk_cannot_emit_low_rubric_without_labeled_override() -> None:
    p = _payload(
        risk_score=85,
        impersonation_likelihood=10,
        vendor_fraud_score=10,
        wire_transfer_anomaly_score=10,
        invoice_authenticity_score=None,
        behavioral_deviation_flags=[],
        forced_escalation_triggers=[],
        recommended_action="block",
    )
    rubric = project_client_facing_rubric(p)
    if rubric.axis_total <= 5:
        assert rubric.rubric_consistency_override is True
        assert rubric.rubric_consistency_reason is not None
        assert len(rubric.rubric_consistency_reason) > 0


# §8.5 — Known benign fixture (risk_score <= 20, recommended_action="safe")
# cannot emit high rubric (axis_total >= 6).
def test_benign_fixture_cannot_emit_high_rubric() -> None:
    p = _payload(
        risk_score=15,
        impersonation_likelihood=5,
        vendor_fraud_score=5,
        wire_transfer_anomaly_score=5,
        invoice_authenticity_score=95,
        behavioral_deviation_flags=[],
        recommended_action="safe",
    )
    rubric = project_client_facing_rubric(p)
    # Internal band ceiling for risk_score 0..24 is axis_total 2 (§4.1).
    # Either the per-axis sum falls within the band naturally, or the §4.2
    # guard trims it down to the ceiling and labels the override.
    if rubric.axis_total >= 6:
        assert rubric.rubric_consistency_override is True
        assert rubric.axis_total <= 2
    else:
        assert rubric.axis_total <= 2


# §8.6 — Ghost-thread fixture elevates conversation_continuity.
def test_ghost_thread_elevates_conversation_continuity() -> None:
    p = _payload(forced_escalation_triggers=["ghost_thread_detected"])
    rubric = project_client_facing_rubric(p)
    continuity = next(
        a for a in rubric.axes if a.axis_name == "conversation_continuity"
    )
    assert continuity.score == 2


# §8.7 — Banking-change fixture elevates vendor_payment_history.
def test_banking_change_elevates_vendor_payment_history() -> None:
    p = _payload(behavioral_deviation_flags=["new_banking_instructions"])
    rubric = project_client_facing_rubric(p)
    vph = next(a for a in rubric.axes if a.axis_name == "vendor_payment_history")
    assert vph.score == 2


# §8.8 — Invoice-authenticity anomaly fixture elevates document_integrity.
def test_invoice_authenticity_anomaly_elevates_document_integrity() -> None:
    p = _payload(invoice_authenticity_score=15)
    rubric = project_client_facing_rubric(p)
    di = next(a for a in rubric.axes if a.axis_name == "document_integrity")
    assert di.score == 2


# §8.9 — Lookalike/header-divergence fixture elevates sender_identity.
def test_header_divergence_elevates_sender_identity() -> None:
    p = _payload(forced_escalation_triggers=["header_divergence_strong"])
    rubric = project_client_facing_rubric(p)
    si = next(a for a in rubric.axes if a.axis_name == "sender_identity")
    assert si.score == 2


def test_lookalike_with_impersonation_cues_elevates_sender_identity() -> None:
    p = _payload(
        behavioral_deviation_flags=[
            "lookalike_sender_domain",
            "mismatched_invoice_vendor_name",
        ],
        impersonation_likelihood=45,
    )
    rubric = project_client_facing_rubric(p)
    si = next(a for a in rubric.axes if a.axis_name == "sender_identity")
    assert si.score == 2


# §8.10 — Date/timing anomaly fixture elevates origin_timing.
def test_origin_timing_elevates_on_oob_pressure_with_elevated_risk() -> None:
    p = _payload(
        risk_score=70,
        behavioral_deviation_flags=["out_of_band_pressure"],
    )
    rubric = project_client_facing_rubric(p)
    ot = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert ot.score == 2


# §8.11 — No raw header/body/account/routing leakage into why_this_score.
def test_no_pii_or_raw_header_leakage_in_why_strings() -> None:
    """``why_this_score`` strings come from numeric scores and flag categories
    only; even when the input payload's free-text fields contain header-like
    strings, account numbers, or email addresses, those substrings must never
    appear in the projected rubric output (D7 data minimization).
    """
    p = _payload(
        risk_score=95,
        impersonation_likelihood=90,
        vendor_fraud_score=85,
        wire_transfer_anomaly_score=80,
        invoice_authenticity_score=10,
        behavioral_deviation_flags=[
            "new_banking_instructions",
            "lookalike_sender_domain",
            "out_of_band_pressure",
        ],
        risk_factors=["acct 12345 routing 98765 thread fabricated"],
        phishing_signals=["password reset link http://evil.example.com"],
        suspicious_elements=[
            "From: bob@evil.example.com Reply-To: c@d.example.org"
        ],
        forced_escalation_triggers=[
            "header_divergence_strong",
            "ghost_thread_detected",
        ],
    )
    rubric = project_client_facing_rubric(p)
    forbidden_substrings = (
        "@",
        "12345",
        "98765",
        "Received:",
        "From:",
        "Reply-To:",
        "http://",
        "https://",
    )
    for axis in rubric.axes:
        for needle in forbidden_substrings:
            assert needle not in axis.why_this_score, (
                f"why_this_score for {axis.axis_name!r} contains forbidden "
                f"substring {needle!r}: {axis.why_this_score!r}"
            )


def test_why_this_score_within_160_char_cap() -> None:
    """D11/D15 — every ``why_this_score`` is ≤ 160 chars (validator-enforced;
    this test asserts the mapper itself never produces a string that would
    fail validation in the first place).
    """
    payloads = [
        _payload(),  # benign
        _payload(
            risk_score=95,
            vendor_fraud_score=99,
            wire_transfer_anomaly_score=99,
            invoice_authenticity_score=0,
            behavioral_deviation_flags=[
                "new_banking_instructions",
                "lookalike_sender_domain",
                "out_of_band_pressure",
                "first_time_sender_with_financial_ask",
                "urgency_paired_with_finance",
                "mismatched_invoice_vendor_name",
                "reply_to_diverges_from_from",
                "unusual_dollar_amount",
                "unusual_unicode_obfuscation",
            ],
            impersonation_likelihood=99,
            forced_escalation_triggers=[
                "header_divergence_strong",
                "ghost_thread_detected",
            ],
            ransomware_attachment_risk_score=99,
            urgency_signals=["a", "b", "c", "d"],
        ),
    ]
    for p in payloads:
        rubric = project_client_facing_rubric(p)
        for axis in rubric.axes:
            assert 1 <= len(axis.why_this_score) <= 160


# §8.12 — Report renderer displays both rubric and internal recommended_action.
def test_report_renderer_shows_rubric_and_recommended_action() -> None:
    rubric = project_client_facing_rubric(
        _payload(
            risk_score=90,
            behavioral_deviation_flags=["new_banking_instructions"],
            impersonation_likelihood=80,
            invoice_authenticity_score=20,
            forced_escalation_triggers=["ghost_thread_detected"],
            recommended_action="block",
        )
    )
    aggregate = {
        "digest_date": "2026-05-25",
        "important_emails": [
            {
                "source_email_record_id": str(uuid4()),
                "source_analysis_record_id": "analysis-1",
                "subject": "Urgent invoice with new banking instructions",
                "sender": "billing@vendor.example",
                "risk_score": 90,
                "recommended_action": "block",
                "client_facing_rubric": rubric.model_dump(mode="json"),
            }
        ],
        "top_risks": [
            {
                "source_email_record_id": str(uuid4()),
                "source_analysis_record_id": "analysis-1",
                "subject": "Urgent invoice with new banking instructions",
                "sender": "billing@vendor.example",
                "risk_score": 90,
                "recommended_action": "block",
                "reason": "vendor invoice fraud",
                "client_facing_rubric": rubric.model_dump(mode="json"),
            }
        ],
        "tasks": [],
    }

    rendered = demo_digest_llm_client("daily digest prompt", json.dumps(aggregate))

    assert "Action: `block`" in rendered
    assert f"Rubric: {rubric.axis_total}/10" in rendered
    assert "Order is fixed for stability, not priority." in rendered
    for axis in rubric.axes:
        assert f"{axis.axis_name}: {axis.score}/2 - {axis.why_this_score}" in rendered


# §8.13 — Tenant isolation: mapper has no global state and does not mutate
# the input payload. Asserted structurally — see also §8.14.
def test_mapper_is_pure_no_payload_mutation() -> None:
    base = _payload(
        risk_score=60,
        behavioral_deviation_flags=["new_banking_instructions"],
    )
    snapshot_before = base.model_dump(mode="json")
    rubric_a = project_client_facing_rubric(base)
    snapshot_after = base.model_dump(mode="json")
    assert snapshot_before == snapshot_after, (
        "project_client_facing_rubric must not mutate the input payload"
    )
    rubric_b = project_client_facing_rubric(base)
    assert rubric_a.model_dump() == rubric_b.model_dump()


# §8.14 — Kill-switch invariant: mapper does not change recommended_action
# or risk_analysis on the existing scoring path.
def test_mapper_does_not_alter_recommended_action_or_risk_analysis() -> None:
    p = _payload(
        risk_score=85,
        recommended_action="block",
        forced_escalation_triggers=["header_divergence_strong"],
    )
    before_action = p.recommended_action
    before_risk_score = p.risk_analysis.risk_score
    before_flags = list(p.risk_analysis.behavioral_deviation_flags)
    project_client_facing_rubric(p)
    assert p.recommended_action == before_action
    assert p.risk_analysis.risk_score == before_risk_score
    assert list(p.risk_analysis.behavioral_deviation_flags) == before_flags


# §4.2 specific — guard fires and is labeled when per-axis sum is far below
# the internal band. This is the explicit "internal high, rubric mild" case.
def test_consistency_guard_lifts_to_band_floor_with_label() -> None:
    p = _payload(
        risk_score=90,
        impersonation_likelihood=10,
        vendor_fraud_score=10,
        wire_transfer_anomaly_score=10,
        invoice_authenticity_score=None,
        behavioral_deviation_flags=[],
        forced_escalation_triggers=[],
        recommended_action="block",
    )
    rubric = project_client_facing_rubric(p)
    # Internal band for risk_score 75..100 is axis_total 7..10. Per-axis
    # sum is 0 here, so guard must lift to the band floor (7) and label
    # the override.
    assert rubric.rubric_consistency_override is True
    assert rubric.axis_total == 7
    assert rubric.rubric_consistency_reason is not None
    assert "internal" in rubric.rubric_consistency_reason.lower()


# §4.2 symmetric — guard fires and is labeled when per-axis sum is far
# above the internal band. This is the explicit "internal low, rubric
# inflated" case the previous audit flagged as missing coverage.
def test_consistency_guard_trims_to_band_ceiling_with_label() -> None:
    # risk_score in band 0..24 → axis_total band 0..2. Force the per-axis
    # projection well above the ceiling by combining a high
    # impersonation_likelihood (sender_identity=2) with the
    # ``new_banking_instructions`` flag (vendor_payment_history=2). Sum
    # would be ≥ 4, which is > band_ceil (2) + 1 = 3, so the trim path
    # in ``project_client_facing_rubric`` must engage.
    p = _payload(
        risk_score=10,
        impersonation_likelihood=80,
        vendor_fraud_score=10,
        wire_transfer_anomaly_score=10,
        invoice_authenticity_score=None,
        behavioral_deviation_flags=["new_banking_instructions"],
        forced_escalation_triggers=[],
        recommended_action="safe",
    )
    rubric = project_client_facing_rubric(p)

    raw_axis_sum = sum(axis.score for axis in rubric.axes)
    assert raw_axis_sum >= 4, (
        "test fixture must drive per-axis sum above the band ceiling+1; "
        f"got {raw_axis_sum}"
    )
    # Band ceiling for risk_score 10 is 2, so trim must clamp to 2 and
    # label the override.
    assert rubric.rubric_consistency_override is True
    assert rubric.axis_total == 2
    assert rubric.rubric_consistency_reason is not None
    reason = rubric.rubric_consistency_reason.lower()
    assert "ceiling" in reason or "trimmed" in reason, (
        f"trim-side reason must say it was trimmed to the band ceiling; "
        f"got: {rubric.rubric_consistency_reason}"
    )
