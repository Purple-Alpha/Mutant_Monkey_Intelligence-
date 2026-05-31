"""Deterministic projection of internal scoring onto the client-facing 5-axis rubric.

Locked per ``4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md``
§11 SIGNED 2026-05-25 (D1–D17, §3 axis definitions, §4 consistency contract,
§5 schema, §7 failure-mode guardrails, §8 gate tests).

This module is **not** a second detector stack. It is a read-only translation
of an already-validated :class:`EmailAnalysisPayload` (its
:class:`EmailAnalysisRiskAnalysis`, :class:`EmailAnalysisImpersonationAnalysis`,
optional :class:`EmailAnalysisRansomwarePrecursorAnalysis`, and
``forced_escalation_triggers``) onto five client-facing axes:

1. ``sender_identity``
2. ``conversation_continuity``
3. ``vendor_payment_history``
4. ``document_integrity``
5. ``origin_timing``

Each axis is scored ``0..2`` and the deterministic ``axis_total`` is the sum
of axis scores in the no-override case (D10). When the per-axis projection
would materially contradict the internal ``risk_score`` band (§4.1), the
mapper applies a band-floor / band-ceiling guard adjustment (§4.2), sets
``rubric_consistency_override=True``, and emits a bounded
``rubric_consistency_reason`` for audit/reporting.

The mapper does not mutate the input payload (§8.13/§8.14 invariants) and
does not write back into the core scoring path. Failure handling per D12
is the caller's responsibility (mark ``client_facing_rubric=None`` and emit
an audit marker); the mapper itself raises on invalid input.
"""

from __future__ import annotations

from typing import Literal

from core.blackboard.models import (
    BehavioralDeviationFlag,
    CallbackPhishingAssessment,
    ClientFacingRubricPayload,
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRansomwarePrecursorAnalysis,
    EmailAnalysisRiskAnalysis,
    EmailRiskAxisBreakdown,
)

# Rubric §11.2 amendment 2026-05-30 (`callback_phishing_pattern` →
# `origin_timing`). The amendment authorizes the deterministic mapping from
# the upstream Callback Phishing / TOAD detector signal into this axis. The
# string constant matches ``BehavioralDeviationFlag`` and
# ``core.scoring.callback_phishing_detector.CALLBACK_PHISHING_PATTERN_FLAG``;
# duplicating it here keeps this module's import surface narrow (no
# detector-module import), so the rubric mapper stays a pure projection over
# already-validated payload values.
_CALLBACK_PHISHING_PATTERN_FLAG: str = "callback_phishing_pattern"
_CALLBACK_PHISHING_HIGHER_BAND_LIFT: int = 70
_CALLBACK_PHISHING_HIGHER_BAND_RISK_SCORE: int = 50
_CALLBACK_PHISHING_WHY_THIS_SCORE: str = (
    "Callback-phishing body-language pattern detected; verify off-channel."
)

_RUBRIC_VERSION: Literal["v1"] = "v1"

# §4.1 band mapping: (risk_score_floor, risk_score_ceil, axis_total_floor,
# axis_total_ceil). Ordered so the first matching band wins for any
# 0..100 risk_score.
_RISK_BANDS: tuple[tuple[int, int, int, int], ...] = (
    (0, 24, 0, 2),
    (25, 49, 2, 5),
    (50, 74, 4, 8),
    (75, 100, 7, 10),
)

# Locked allowlist of substrings that can elevate ``conversation_continuity``
# to score 1 in the absence of a hard ``ghost_thread_detected`` trigger.
# Any change to this set is a D3 axis-vocabulary change and requires a spec
# revision plus a ``rubric_version`` bump.
_CONTINUITY_KEYWORDS: tuple[str, ...] = (
    "thread",
    "reply chain",
    "continuity",
    "fabricated",
    "ghost",
)


def _band_for_risk_score(risk_score: int) -> tuple[int, int]:
    """Return ``(axis_floor, axis_ceil)`` for the §4.1 band of ``risk_score``."""
    for floor_score, ceil_score, axis_floor, axis_ceil in _RISK_BANDS:
        if floor_score <= risk_score <= ceil_score:
            return axis_floor, axis_ceil
    # ``risk_score`` is validated 0..100 upstream by ``EmailAnalysisRiskAnalysis``;
    # this branch is defensive only. We return the highest band so the
    # consistency guard can never silently downgrade a high-risk email.
    return 7, 10


def _score_sender_identity(
    impers: EmailAnalysisImpersonationAnalysis,
    flags: set[BehavioralDeviationFlag],
    triggers: list[str],
) -> tuple[int, str, tuple[str, ...]]:
    """Project sender-identity axis (§3.1) from impersonation + header signals."""
    likelihood = impers.impersonation_likelihood
    header_divergence_strong = "header_divergence_strong" in triggers
    has_lookalike = "lookalike_sender_domain" in flags
    has_reply_diverge = "reply_to_diverges_from_from" in flags
    has_vendor_mismatch = "mismatched_invoice_vendor_name" in flags

    if header_divergence_strong:
        return (
            2,
            "Header chain shows strong divergence from claimed sender domain.",
            ("header_divergence_strong",),
        )
    if likelihood >= 70:
        return (
            2,
            f"Impersonation likelihood {likelihood}/100 indicates a strong "
            "sender-identity anomaly.",
            ("impersonation_likelihood_high",),
        )
    if has_lookalike and (likelihood >= 40 or has_vendor_mismatch):
        return (
            2,
            "Lookalike sender domain combined with corroborating impersonation "
            "cues.",
            ("lookalike_sender_domain", "impersonation_corroborating"),
        )

    if likelihood >= 40:
        return (
            1,
            f"Moderate impersonation likelihood ({likelihood}/100) without a "
            "confirmed identity break.",
            ("impersonation_likelihood_moderate",),
        )
    if has_lookalike:
        return (
            1,
            "Sender domain resembles a known brand; no other identity cues "
            "confirmed.",
            ("lookalike_sender_domain",),
        )
    if has_reply_diverge:
        return (
            1,
            "Reply-To address diverges from From; sender-identity context "
            "warrants review.",
            ("reply_to_diverges_from_from",),
        )
    if has_vendor_mismatch:
        return (
            1,
            "Vendor name on attached invoice does not match the sending sender.",
            ("mismatched_invoice_vendor_name",),
        )

    return 0, "No notable sender-identity anomaly evidence.", ()


def _score_conversation_continuity(
    risk: EmailAnalysisRiskAnalysis,
    impers: EmailAnalysisImpersonationAnalysis,
    triggers: list[str],
) -> tuple[int, str, tuple[str, ...]]:
    """Project conversation-continuity axis (§3.2) from ghost-thread evidence."""
    if "ghost_thread_detected" in triggers:
        return (
            2,
            "Ghost-thread / fabricated continuity detected by deterministic "
            "detector.",
            ("ghost_thread_detected",),
        )

    haystack = (
        risk.risk_factors + risk.phishing_signals + impers.suspicious_elements
    )
    matches = tuple(
        kw
        for kw in _CONTINUITY_KEYWORDS
        if any(kw in item.lower() for item in haystack)
    )
    if matches:
        return (
            1,
            "Mild thread-continuity uncertainty noted in analysis evidence.",
            tuple(f"continuity_keyword:{kw}" for kw in matches),
        )

    return 0, "No continuity anomaly pattern.", ()


def _score_vendor_payment_history(
    risk: EmailAnalysisRiskAnalysis,
    flags: set[BehavioralDeviationFlag],
) -> tuple[int, str, tuple[str, ...]]:
    """Project vendor-payment-history axis (§3.3) from financial overlay state."""
    has_new_banking = "new_banking_instructions" in flags
    has_unusual_amount = "unusual_dollar_amount" in flags
    has_first_time_finance = "first_time_sender_with_financial_ask" in flags
    has_urgency_finance = "urgency_paired_with_finance" in flags

    if has_new_banking:
        return (
            2,
            "New banking instructions requested; verify via known channel "
            "before action.",
            ("new_banking_instructions",),
        )
    if risk.vendor_fraud_score >= 60:
        return (
            2,
            f"Vendor fraud score {risk.vendor_fraud_score}/100 indicates "
            "strong payment-destination anomaly.",
            ("vendor_fraud_score_high",),
        )
    if risk.wire_transfer_anomaly_score >= 60:
        return (
            2,
            f"Wire transfer anomaly score {risk.wire_transfer_anomaly_score}/100 "
            "indicates strong payment-destination anomaly.",
            ("wire_transfer_anomaly_high",),
        )

    if has_first_time_finance:
        return (
            1,
            "First-time sender attached a financial ask; vendor-history "
            "context unverified.",
            ("first_time_sender_with_financial_ask",),
        )
    if has_urgency_finance:
        return (
            1,
            "Urgency paired with finance ask; vendor-payment context "
            "warrants review.",
            ("urgency_paired_with_finance",),
        )
    if has_unusual_amount:
        return (
            1,
            "Unusual dollar amount relative to vendor history.",
            ("unusual_dollar_amount",),
        )
    if risk.vendor_fraud_score >= 30 or risk.wire_transfer_anomaly_score >= 30:
        return (
            1,
            f"Moderate vendor-payment risk indicators "
            f"(vendor={risk.vendor_fraud_score}, "
            f"wire={risk.wire_transfer_anomaly_score}).",
            ("vendor_fraud_score_moderate",),
        )

    return 0, "No payment-change anomaly context.", ()


def _score_document_integrity(
    risk: EmailAnalysisRiskAnalysis,
    flags: set[BehavioralDeviationFlag],
    overlay: EmailAnalysisRansomwarePrecursorAnalysis | None,
) -> tuple[int, str, tuple[str, ...]]:
    """Project document-integrity axis (§3.4) from invoice + attachment evidence."""
    auth = risk.invoice_authenticity_score
    has_vendor_mismatch = "mismatched_invoice_vendor_name" in flags
    attachment_risk = overlay.attachment_risk_score if overlay is not None else 0

    if auth is not None and auth <= 30:
        return (
            2,
            f"Invoice authenticity {auth}/100 indicates strong "
            "document-integrity concern.",
            ("invoice_authenticity_low",),
        )
    if attachment_risk >= 60:
        return (
            2,
            f"Attachment risk overlay {attachment_risk}/100 indicates strong "
            "document-integrity concern.",
            ("attachment_risk_high",),
        )
    if has_vendor_mismatch and (auth is None or auth <= 60):
        return (
            2,
            "Vendor name mismatch on attached invoice combined with weak "
            "authenticity evidence.",
            ("mismatched_invoice_vendor_name", "authenticity_weak"),
        )

    if auth is not None and auth <= 60:
        return (
            1,
            f"Invoice authenticity {auth}/100 leaves moderate "
            "document-integrity concern.",
            ("invoice_authenticity_moderate",),
        )
    if attachment_risk >= 30:
        return (
            1,
            f"Attachment risk overlay {attachment_risk}/100 indicates "
            "moderate document-integrity concern.",
            ("attachment_risk_moderate",),
        )
    if has_vendor_mismatch:
        return (
            1,
            "Vendor name on attached invoice does not match sender; warrants "
            "review.",
            ("mismatched_invoice_vendor_name",),
        )

    return 0, "No meaningful document-integrity concerns.", ()


def _score_origin_timing_base(
    risk: EmailAnalysisRiskAnalysis,
    flags: set[BehavioralDeviationFlag],
) -> tuple[int, str, tuple[str, ...]]:
    """Project origin-timing axis (§3.5) from urgency + out-of-band signals.

    Per §3.5 boundary, this axis must **not** imply that geo-velocity is
    implemented. v1 derives only from existing ``urgency_signals`` and the
    ``out_of_band_pressure`` behavioral flag. Sender-provenance / geo-velocity
    is a separate gated detector and lifts this axis only when that detector
    ships.

    Callers must run the §11.2 amendment overlay (``_score_origin_timing``)
    on top of this base result. The base function alone does not satisfy
    the signed rubric contract once the §11.2 amendment is in scope.
    """
    has_oob_pressure = "out_of_band_pressure" in flags
    urgency_count = len(risk.urgency_signals)

    if has_oob_pressure and risk.risk_score >= 50:
        return (
            2,
            "Out-of-band pressure pattern with elevated overall risk indicates "
            "strong origin/timing anomaly.",
            ("out_of_band_pressure", "elevated_risk_score"),
        )

    if has_oob_pressure:
        return (
            1,
            "Out-of-band pressure noted in analysis evidence.",
            ("out_of_band_pressure",),
        )
    if urgency_count >= 2 and risk.risk_score >= 30:
        return (
            1,
            f"Multiple urgency signals ({urgency_count}) suggest a moderate "
            "timing anomaly.",
            ("urgency_signals_multiple",),
        )

    return 0, "No notable origin/timing anomaly.", ()


def _score_origin_timing(
    risk: EmailAnalysisRiskAnalysis,
    flags: set[BehavioralDeviationFlag],
    callback_phishing_assessment: CallbackPhishingAssessment | None,
) -> tuple[int, str, tuple[str, ...]]:
    """Project ``origin_timing`` per §3.5 base + signed §11.2 amendment.

    The base projection (``_score_origin_timing_base``) covers the original
    §3.5 evidence sources (``out_of_band_pressure`` flag + ``urgency_signals``
    count). The §11.2 amendment (SIGNED 2026-05-30 by Matt Nichol, authorized
    by the §11-SIGNED Callback Phishing / TOAD spec D13) layers two
    additional rules on top:

    1. **Floor-lift rule.** When ``callback_phishing_pattern`` is present in
       ``risk.behavioral_deviation_flags``, the projected score MUST be at
       least 1. If the base projection already returned 1 or 2 from an
       independent evidence source, the higher base score is preserved
       (max-merge semantics, mirroring how the
       ``EmailAnalysisRiskAnalysis.recommended_risk_floor_lift`` overlay
       max-merges into the final ``risk_score``). The amendment never lowers
       an existing axis score; this is a one-directional lift.

    2. **Higher-band rule.** When ``callback_phishing_pattern`` is present
       AND either ``risk.risk_score >= 50`` or
       ``callback_phishing_assessment.recommended_risk_floor_lift >= 70``
       (the §4.1 block-eligible band of the TOAD spec — produced when the
       detector fires on two-or-more categories OR a single
       ``payment_redirect_call`` category), the projected score MUST be
       exactly 2. The amendment explicitly authorizes this as the headline
       reason this axis exists when both conditions hold simultaneously.

    Evidence tagging: when either rule fires, ``callback_phishing_pattern``
    is added to ``evidence_tags`` so downstream consumers (rendering,
    monthly digest, audit-marker stream) can attribute the lift to the
    TOAD signal without re-running the rule. Per §3.5 amendment + D15 of
    the rubric spec, the ``why_this_score`` text stays inside the 160-char
    cap and never echoes raw phone digits or raw lure-phrase substrings
    (TOAD D7 PII safety is enforced upstream by the detector; the rubric
    just emits the bounded amendment phrase).
    """
    base_score, base_why, base_tags = _score_origin_timing_base(risk, flags)
    if _CALLBACK_PHISHING_PATTERN_FLAG not in flags:
        return base_score, base_why, base_tags

    higher_band_lift = (
        callback_phishing_assessment is not None
        and callback_phishing_assessment.recommended_risk_floor_lift
        >= _CALLBACK_PHISHING_HIGHER_BAND_LIFT
    )
    higher_band_risk = risk.risk_score >= _CALLBACK_PHISHING_HIGHER_BAND_RISK_SCORE
    higher_band = higher_band_lift or higher_band_risk

    if higher_band:
        return (
            2,
            _CALLBACK_PHISHING_WHY_THIS_SCORE,
            _dedup_tags(base_tags + (_CALLBACK_PHISHING_PATTERN_FLAG,)),
        )

    if base_score == 0:
        return (
            1,
            _CALLBACK_PHISHING_WHY_THIS_SCORE,
            (_CALLBACK_PHISHING_PATTERN_FLAG,),
        )

    return (
        base_score,
        base_why,
        _dedup_tags(base_tags + (_CALLBACK_PHISHING_PATTERN_FLAG,)),
    )


def _dedup_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
    """Preserve order, drop duplicates. Pure helper for §11.2 evidence merging."""
    seen: set[str] = set()
    deduped: list[str] = []
    for tag in tags:
        if tag in seen:
            continue
        seen.add(tag)
        deduped.append(tag)
    return tuple(deduped)


def project_client_facing_rubric(
    payload: EmailAnalysisPayload,
) -> ClientFacingRubricPayload:
    """Project an :class:`EmailAnalysisPayload` onto the §5 5-axis rubric.

    The mapper is a pure read-only function: it does not mutate ``payload``
    (§8.14 kill-switch invariant) and depends on no global state (§8.13
    tenant-isolation invariant). It runs §4 consistency checks and applies
    the band-floor / band-ceiling guard when needed, in which case
    ``rubric_consistency_override=True`` and a bounded reason are set.
    """
    risk = payload.risk_analysis
    impers = payload.impersonation_analysis
    overlay = payload.ransomware_precursor_analysis
    callback_phishing_assessment = payload.callback_phishing_assessment
    triggers = list(payload.forced_escalation_triggers)
    flags: set[BehavioralDeviationFlag] = set(risk.behavioral_deviation_flags)

    s1, why1, tags1 = _score_sender_identity(impers, flags, triggers)
    s2, why2, tags2 = _score_conversation_continuity(risk, impers, triggers)
    s3, why3, tags3 = _score_vendor_payment_history(risk, flags)
    s4, why4, tags4 = _score_document_integrity(risk, flags, overlay)
    s5, why5, tags5 = _score_origin_timing(risk, flags, callback_phishing_assessment)

    axes = (
        EmailRiskAxisBreakdown(
            axis_name="sender_identity",
            score=s1,
            why_this_score=why1,
            evidence_tags=tags1,
        ),
        EmailRiskAxisBreakdown(
            axis_name="conversation_continuity",
            score=s2,
            why_this_score=why2,
            evidence_tags=tags2,
        ),
        EmailRiskAxisBreakdown(
            axis_name="vendor_payment_history",
            score=s3,
            why_this_score=why3,
            evidence_tags=tags3,
        ),
        EmailRiskAxisBreakdown(
            axis_name="document_integrity",
            score=s4,
            why_this_score=why4,
            evidence_tags=tags4,
        ),
        EmailRiskAxisBreakdown(
            axis_name="origin_timing",
            score=s5,
            why_this_score=why5,
            evidence_tags=tags5,
        ),
    )

    sum_axes = sum(axis.score for axis in axes)
    band_floor, band_ceil = _band_for_risk_score(risk.risk_score)

    override = False
    reason: str | None = None
    if sum_axes < band_floor - 1:
        axis_total = band_floor
        override = True
        reason = (
            "Rubric raised to internal band floor "
            f"(risk_score={risk.risk_score}, band={band_floor}-{band_ceil}); "
            "internal evidence outweighs per-axis projection."
        )
    elif sum_axes > band_ceil + 1:
        axis_total = band_ceil
        override = True
        reason = (
            "Rubric trimmed to internal band ceiling "
            f"(risk_score={risk.risk_score}, band={band_floor}-{band_ceil}); "
            "per-axis projection exceeds internal calibration."
        )
    else:
        axis_total = sum_axes

    return ClientFacingRubricPayload(
        rubric_version=_RUBRIC_VERSION,
        axis_total=axis_total,
        axes=axes,
        rubric_consistency_override=override,
        rubric_consistency_reason=reason,
    )


__all__ = ["project_client_facing_rubric"]
