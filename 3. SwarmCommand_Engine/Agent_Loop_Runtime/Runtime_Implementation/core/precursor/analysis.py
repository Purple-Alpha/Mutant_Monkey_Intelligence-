"""NorthStar Inbox Shield — Phase 1.2 precursor analysis overlay.

Glues the three deterministic detectors (attachment, URL, body-language) into
the single ``EmailAnalysisRansomwarePrecursorAnalysis`` block that the
scoring agent overlays onto its LLM-validated ``EmailAnalysisPayload``.

Per the Phase 1.2 deep dive and the 12-month roadmap Month 3 gate:
- the four sub-scores (``attachment_risk_score``, ``url_obfuscation_score``,
  ``credential_harvesting_score``, ``mfa_fatigue_score``) are ALWAYS produced
  (zero when no signal — not ``None``);
- ``precursor_indicators`` aggregates every indicator that fired across the
  three detectors, deduplicated and source-order stable;
- ``recommended_risk_floor`` is the *minimum* ``risk_score`` the scoring agent
  must enforce on the final payload (i.e. ``risk_score = max(llm_risk,
  precursor_floor)``). Computed as the max of the four sub-scores so a single
  strong precursor signal (e.g. an executable attachment) cannot be diluted
  by a confident-but-wrong LLM risk score.

Pure functions everywhere. No I/O. No LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.blackboard import (
    EmailAnalysisRansomwarePrecursorAnalysis,
    EmailInboundPayload,
    PrecursorIndicator,
)

from core.precursor.attachment_classifier import score_attachment_risk
from core.precursor.body_signal_detector import (
    score_credential_harvesting,
    score_mfa_fatigue,
)
from core.precursor.url_obfuscation_detector import score_url_obfuscation


@dataclass(frozen=True)
class PrecursorOverlay:
    """Bundled overlay output for the scoring agent.

    ``block`` is the schema-shaped overlay that gets attached to
    ``EmailAnalysisPayload.ransomware_precursor_analysis``.

    ``recommended_risk_floor`` is the minimum ``risk_score`` the agent must
    enforce on the final payload. The scoring agent computes
    ``final_risk = max(llm_risk, recommended_risk_floor)``. Setting a floor
    rather than overwriting the LLM score is intentional: a confident LLM that
    rates a fraud case at 95 stays at 95, while a low LLM score on an obvious
    ransomware-precursor email is lifted to the deterministic floor.
    """

    block: EmailAnalysisRansomwarePrecursorAnalysis
    recommended_risk_floor: int


def build_precursor_overlay(
    payload: EmailInboundPayload,
    *,
    attachment_floor_lift: int = 0,
    url_obfuscation_floor_lift: int = 0,
) -> PrecursorOverlay:
    """Compute the deterministic ransomware-precursor overlay for one email.

    Inputs are taken straight from the inbound payload — no I/O, no network,
    no LLM call. Safe to run unconditionally on every scored email; benign
    emails get an all-zeros block and a floor of 0.

    Phase 1.4 (Month 5) parameters:

    - ``attachment_floor_lift`` (0–25; clamped): additive lift applied to
      ``attachment_risk_score`` BEFORE the ``recommended_risk_floor``
      computation. Comes from the
      ``attachment_classifier_boost`` mutation kind's
      ``attachment_risk_floor_lift`` parameter, threaded through the
      scoring-agent overlay on cycle entry. Default 0 keeps the
      pre-Phase-1.4 behaviour byte-identical (Month 2 PASS gate
      protection).
    - ``url_obfuscation_floor_lift`` (0–25; clamped): same shape for
      ``url_obfuscation_score`` from the
      ``url_obfuscation_sensitivity`` mutation kind's
      ``url_obfuscation_floor_lift`` parameter.

    Both lifts are clamped to 0 from below and to 100 from above on the
    resulting sub-score so the schema's ``ge=0/le=100`` invariants stay
    honoured no matter what the policy state contains. The lifts only
    affect ``recommended_risk_floor``; the LLM-derived ``risk_score`` is
    never directly touched here — that overlay is applied in
    ``core/scoring/email_risk_scoring_agent.py``.
    """

    attachment_assessments = [
        score_attachment_risk(meta) for meta in payload.attachments
    ]
    attachment_score_raw = max(
        (a.risk_score for a in attachment_assessments), default=0
    )
    attachment_score = _clamp_score(
        attachment_score_raw + _clamp_lift(attachment_floor_lift)
    )
    attachment_indicators: tuple[PrecursorIndicator, ...] = tuple(
        _dedupe_in_order(
            indicator
            for assessment in attachment_assessments
            for indicator in assessment.indicators
        )
    )

    url_assessment = score_url_obfuscation(payload.body_plain, payload.body_html)
    url_score = _clamp_score(
        url_assessment.score + _clamp_lift(url_obfuscation_floor_lift)
    )

    body_texts: tuple[str | None, ...] = (
        payload.body_plain,
        payload.body_html,
        payload.subject,
    )
    credential_assessment = score_credential_harvesting(*body_texts)
    mfa_assessment = score_mfa_fatigue(*body_texts)

    indicators = tuple(
        _dedupe_in_order(
            (
                *attachment_indicators,
                *url_assessment.indicators,
                *credential_assessment.indicators,
                *mfa_assessment.indicators,
            )
        )
    )

    block = EmailAnalysisRansomwarePrecursorAnalysis(
        attachment_risk_score=attachment_score,
        url_obfuscation_score=url_score,
        credential_harvesting_score=credential_assessment.score,
        mfa_fatigue_score=mfa_assessment.score,
        precursor_indicators=list(indicators),
    )

    recommended_risk_floor = max(
        attachment_score,
        url_score,
        credential_assessment.score,
        mfa_assessment.score,
    )

    return PrecursorOverlay(
        block=block,
        recommended_risk_floor=recommended_risk_floor,
    )


def _clamp_lift(value: int) -> int:
    """Clamp the Phase 1.4 lift parameter to its contracted 0..25 range.

    Defensive: a misconfigured policy state could in theory carry a
    negative or out-of-range int. The mutation engine never emits
    such a value (``_phase14_floor_lift_for`` already clamps), but the
    overlay applies the same clamp at the read site so a tampered
    state file can never exceed the contracted lift.
    """

    if value <= 0:
        return 0
    if value >= 25:
        return 25
    return value


def _clamp_score(value: int) -> int:
    if value <= 0:
        return 0
    if value >= 100:
        return 100
    return value


def _dedupe_in_order(
    items: Iterable[PrecursorIndicator],
) -> list[PrecursorIndicator]:
    seen: set[PrecursorIndicator] = set()
    ordered: list[PrecursorIndicator] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered
