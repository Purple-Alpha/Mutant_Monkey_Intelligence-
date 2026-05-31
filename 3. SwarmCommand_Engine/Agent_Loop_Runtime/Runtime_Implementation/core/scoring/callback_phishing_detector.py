"""NorthStar Inbox Shield - Callback Phishing / TOAD body-language detector (Part 1).

Pure-function deterministic body/text scanner that surfaces evidence an
inbound email is trying to move a financial fraud off email and onto a
phone call. The detector never lowers a score, never calls the network,
never extracts or stores phone-number digits, and never echoes raw lure
substrings or raw email body content back to callers.

Locked per ``4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md``
(§11 SIGNED 2026-05-30 by Matt Nichol). v1 reads ``body_plain`` only (D14);
the five v1 phrase categories are locked in D11; no numeric
``callback_phishing_score`` field is emitted (D12); no
``phone_number_assessment`` slot exists on the v1 schema (D15); the
rubric ``origin_timing`` mapping per D13 lands in a separate §11.1
amendment on the Client-Facing 5-Axis Email Scoring Rubric spec, in pass 2.

Pass 1 scope (this module + ``core/blackboard/models.py`` additions
+ ``tests/test_callback_phishing_detector.py``) covers §8 gate tests
1-9 and 12. Pass 2 (scoring-agent wiring + activation flag + rendering
integration + rubric §11.1 amendment) is gated on a separate operator
start-build instruction; it is NOT carried out by this module.

The detector returns a frozen, validator-checked
:class:`~core.blackboard.CallbackPhishingAssessment`. Downstream wiring
in pass 2 will:

- append :data:`CALLBACK_PHISHING_PATTERN_FLAG` to
  ``EmailAnalysisRiskAnalysis.behavioral_deviation_flags`` once when
  ``assessment.fired`` is True (per spec §3, §5);
- max-merge ``assessment.recommended_risk_floor_lift`` onto the
  existing ``recommended_risk_floor`` (per §4.1, D5 lift-only);
- attach the assessment to
  ``EmailAnalysisPayload.callback_phishing_assessment``;
- when rendering, emit :data:`OUT_OF_BAND_VERIFICATION_WORDING` per D8.
"""

from __future__ import annotations

import re
from typing import Final, Mapping

from core.blackboard import (
    CallbackPhishingAssessment,
    CallbackPhishingCategory,
)

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

CALLBACK_PHISHING_PATTERN_FLAG: Final[str] = "callback_phishing_pattern"
"""``BehavioralDeviationFlag`` value the scoring agent (pass 2) appends to
``EmailAnalysisRiskAnalysis.behavioral_deviation_flags`` once when this
detector fires on any of the five v1 categories. Locked in D2 of the TOAD
spec and added to the ``BehavioralDeviationFlag`` Literal in
``core/blackboard/models.py`` in the same commit as this module."""


OUT_OF_BAND_VERIFICATION_WORDING: Final[str] = (
    "verify through a previously-known channel, not via the number in this email."
)
"""Project-standard out-of-band verification wording per D8 of the TOAD spec
and the shared contract with Financial State Ledger / Two-Channel
Confirmation Enforcement. Pass 2 rendering wiring (daily-digest agent
prompt + deterministic demo renderer) MUST embed this exact string when
the detector fires; the §8 gate test 10 pins that requirement."""


# ---------------------------------------------------------------------------
# §4.1 risk-floor lift bands
# ---------------------------------------------------------------------------

_LIFT_SINGLE_CATEGORY: Final[int] = 50  # needs_review band
_LIFT_TWO_CATEGORIES_OR_PAYMENT_SINGLE: Final[int] = 70  # block-eligible
_LIFT_THREE_PLUS_OR_PAYMENT_PLUS_KNOWN_CHANNEL: Final[int] = 85  # FSL-hit floor

_PAYMENT_REDIRECT_CALL: Final[str] = "payment_redirect_call"
_DO_NOT_USE_KNOWN_CHANNEL: Final[str] = "do_not_use_known_channel"


# ---------------------------------------------------------------------------
# §3 closed phrase categories (v1, locked by D11)
# ---------------------------------------------------------------------------

# Canonical category order. The detector emits ``categories`` in this order
# regardless of which patterns matched first, so the same body always
# produces the same tuple (§8 gate test 5: determinism).
_CATEGORY_ORDER: Final[tuple[str, ...]] = (
    "call_now_pressure",
    "do_not_use_known_channel",
    "voice_only_finalize",
    "support_line_substitution",
    "payment_redirect_call",
)


# Generic, category-level explanations. Per D7 these MUST NOT echo the
# matched lure phrase, MUST NOT contain raw phone-number digits, MUST NOT
# contain raw header content, and MUST NOT echo any email-body substring
# of length > 60 characters. Length is bounded at <= 160 characters
# (the same cap the 5-axis rubric's ``why_this_score`` field uses).
_CATEGORY_REASONS: Final[Mapping[str, str]] = {
    "call_now_pressure": (
        "urgency-paired callback phrasing detected (instruction to call the "
        "number provided in this email within a short or pressured window)"
    ),
    "do_not_use_known_channel": (
        "misdirection away from previously-known contact channels detected "
        "(instruction to ignore the on-file or published number)"
    ),
    "voice_only_finalize": (
        "phrasing forcing resolution off email onto a phone call detected "
        "(instruction that the matter cannot be completed by email)"
    ),
    "support_line_substitution": (
        "substitute or replacement support / fraud / billing phone line "
        "offered (instruction to use a new updated or backup line instead)"
    ),
    "payment_redirect_call": (
        "callback paired with a financial-channel change request detected "
        "(instruction to phone to confirm new ACH / wire / banking details)"
    ),
}


# Per-category compiled patterns. Patterns are intentionally conservative:
# they require misdirection, urgency, or off-channel coercion framings,
# not just any "please call our billing line" mention. See §7 failure
# mode 1 in the spec. Adding patterns is allowed within v1 only when the
# addition is still inside the locked category vocabulary; adding a
# brand-new category (e.g. ``mfa_bypass_call``) is a v1.1 spec addendum.
_PATTERNS_CALL_NOW_PRESSURE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\bcall\s+(?:us\s+|me\s+|our\s+team\s+|the\s+(?:number|line)\s+(?:above|below)\s+)?"
        r"(?:immediately|right\s+(?:away|now)|a\.?s\.?a\.?p\.?|asap)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bcall\s+(?:us\s+|me\s+|today\s+)?within\s+\d+\s+(?:hours?|minutes?|business\s+hours?|business\s+days?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:do\s+not|don'?t)\s+delay\b[\s\S]{0,40}\b(?:call|phone|dial)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:call|phone|dial)\s+(?:us\s+|me\s+)?(?:now|today|immediately)\s+to\s+(?:avoid|prevent|stop|halt)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:urgent(?:ly)?|time[- ]sensitive|act\s+now|act\s+immediately)\b[\s\S]{0,40}\b(?:call|phone|dial)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:last|final)\s+(?:notice|chance|warning|opportunity|reminder)\b[\s\S]{0,40}\b(?:call|phone|dial)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_DO_NOT_USE_KNOWN_CHANNEL: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:do\s+not|don'?t)\s+(?:use|dial|call|reach\s+us\s+at)\s+(?:the\s+|any\s+|our\s+)?"
        r"(?:number|phone|line|contact)\s+"
        r"(?:on\s+file|previously\s+provided|in\s+(?:our|the)\s+(?:records?|directory|system|database)|"
        r"on\s+(?:our|the)\s+(?:website|invoice|statement|account))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bignore\s+(?:the\s+|any\s+|all\s+)?(?:previous|prior|old|existing)\s+"
        r"(?:contact|phone|number|line)(?:\s+(?:info|information|details?|numbers?))?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:the\s+|our\s+)?(?:old|previous|prior|former)\s+(?:number|line|contact|phone)\s+"
        r"(?:is|are)\s+(?:no\s+longer\s+(?:valid|in\s+use|active|monitored|working)|"
        r"out\s+of\s+(?:service|date)|disconnected|deprecated)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bour\s+(?:main|primary|published|website|usual|regular|listed)\s+"
        r"(?:line|number|phone)\s+(?:is\s+|are\s+)?(?:currently\s+|temporarily\s+)?"
        r"(?:down|unavailable|inactive|out\s+of\s+service|not\s+(?:working|monitored|in\s+use))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:do\s+not|don'?t)\s+(?:reach|contact|call)\s+(?:us\s+|me\s+)?"
        r"(?:at|via|through|on)\s+(?:the\s+|our\s+)?"
        r"(?:usual|regular|published|main|primary|known|listed)\s+"
        r"(?:number|line|channel|contact|phone)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_VOICE_ONLY_FINALIZE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:we|i|our\s+team)\s+(?:can\s*not|cannot|can'?t)\s+"
        r"(?:complete|finalize|finalise|finish|resolve|process|handle|action|approve)\s+"
        r"(?:this|it|that|the\s+(?:request|transaction|payment|change|update))?\s*"
        r"(?:over|via|through|by|on)\s+(?:email|messages?|chat|text)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bemail\s+(?:will\s+not|won'?t|isn'?t|is\s+not|won'?t\s+be)\s+"
        r"(?:checked|monitored|read|reviewed|answered|responded\s+to)\b"
        r"[\s\S]{0,80}\b(?:call|phone|dial)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:call|phone|dial)\b[\s\S]{0,80}\bemail\s+"
        r"(?:will\s+not|won'?t|isn'?t|is\s+not|won'?t\s+be)\s+"
        r"(?:checked|monitored|read|reviewed|answered|responded\s+to)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:the\s+)?(?:rest|remainder|balance)\s+of\s+"
        r"(?:this|it|the\s+(?:matter|transaction|conversation|process))\s+"
        r"(?:needs\s+to|must|has\s+to|will\s+need\s+to)\s+"
        r"(?:happen|occur|take\s+place|be\s+(?:done|handled|completed|finalized|finalised|resolved))\s+"
        r"(?:by|over|via|on)\s+(?:the\s+)?phone\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bonly\s+(?:by|via|over|on)\s+(?:the\s+)?phone\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:please\s+)?(?:phone|call)\s+(?:us|me)\s+"
        r"(?:so\s+(?:we|i)\s+can|to|in\s+order\s+to)\s+"
        r"(?:complete|finalize|finalise|finish|resolve|process)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_SUPPORT_LINE_SUBSTITUTION: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:call|reach|contact|dial|phone)\s+(?:us\s+at\s+)?(?:our\s+|the\s+)?"
        r"(?:updated|new|temporary|backup|alternate|alternative|secondary|emergency|interim)\s+"
        r"(?:support|fraud|fraud[- ]prevention|fraud[- ]protection|billing|"
        r"customer\s+(?:support|service|care)|service|help|helpdesk|hotline|security)\s+"
        r"(?:line|number|desk|hotline|team|department|center|centre)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:our\s+|the\s+)?(?:new|updated|temporary|backup|alternate|interim)\s+"
        r"(?:fraud[- ]?(?:prevention|protection)|customer[- ]?(?:support|service|care)|"
        r"billing|help(?:desk)?|support|security)\s+"
        r"(?:desk|line|hotline|number|team|department|center|centre)\s+(?:at|is|will\s+be|can\s+be\s+reached)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:please\s+)?(?:use|call|dial|reach)\s+(?:our\s+|the\s+)?"
        r"(?:updated|new|temporary|backup|alternate|interim)\s+"
        r"(?:phone\s+)?(?:number|line|hotline|contact)\s+for\s+"
        r"(?:support|fraud|billing|customer\s+(?:support|service|care)|help|security)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_PAYMENT_REDIRECT_CALL: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:call|phone|dial|ring)\s+(?:us\s+|me\s+)?(?:to\s+)?"
        r"(?:confirm|authori[sz]e|verify|approve|validate|finalize|finalise|process)\s+"
        r"(?:the\s+|our\s+)?(?:new|updated|revised|changed|corrected|amended|different)\s+"
        r"(?:ACH|wire|payment|banking|bank|account|routing|deposit|transfer|payable)\s+"
        r"(?:instructions|details?|information|info|number|account|destination)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:call|phone|dial|ring)\s+(?:us\s+|me\s+)?(?:to\s+)?"
        r"(?:authori[sz]e|approve|release|finalize|finalise|process|execute|complete)\s+"
        r"(?:the\s+|our\s+)?(?:rerouted|redirected|updated|new|revised|changed)\s+"
        r"(?:wire|payment|transfer|deposit|ACH|payable)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:please\s+)?(?:call|phone|dial|ring)\s+(?:us\s+|me\s+)?(?:to\s+)?"
        r"(?:confirm|verify|authori[sz]e|approve)\s+(?:the\s+)?"
        r"(?:new|updated|revised|changed)\s+"
        r"(?:banking|bank|account|wire|payment|ACH|routing|payable)\s+"
        r"(?:details?|instructions|info|information|destination)\b",
        re.IGNORECASE,
    ),
)


_PATTERNS_BY_CATEGORY: Final[Mapping[str, tuple[re.Pattern[str], ...]]] = {
    "call_now_pressure": _PATTERNS_CALL_NOW_PRESSURE,
    "do_not_use_known_channel": _PATTERNS_DO_NOT_USE_KNOWN_CHANNEL,
    "voice_only_finalize": _PATTERNS_VOICE_ONLY_FINALIZE,
    "support_line_substitution": _PATTERNS_SUPPORT_LINE_SUBSTITUTION,
    "payment_redirect_call": _PATTERNS_PAYMENT_REDIRECT_CALL,
}


# Soft cap on the body region the detector scans. Mirrors the prompt
# injection detector's _MAX_SCAN_CHARS. Above this, a pathological input
# cannot inflate detector runtime; the categories that fire on the head
# of the body are sufficient signal.
_MAX_SCAN_CHARS: Final[int] = 200_000


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def detect_callback_phishing(*, body_plain: str) -> CallbackPhishingAssessment:
    """Scan an inbound email body for callback-phishing / TOAD body language.

    Pure-function deterministic detector. Single input: the inbound
    ``EmailInboundPayload.body_plain`` string (per D14 — ``body_html`` is
    deferred to v1.1+). No network, no LLM, no file I/O, no global
    mutable state, no phone-number extraction or storage of any kind.

    Returns a frozen, validator-checked
    :class:`~core.blackboard.CallbackPhishingAssessment`.

    Empty or missing ``body_plain`` yields a no-fire assessment
    (``fired=False`` and lift 0) and no flag emission. This matches §8
    gate test 1 (benign-mail control) and aligns with the header /
    prompt-injection detectors' empty-input behaviour.

    For the closed v1 categories and their lift banding, see
    ``§3`` and ``§4.1`` of the signed TOAD spec.
    """

    text = body_plain or ""
    scan_region = text[:_MAX_SCAN_CHARS]

    fired_category_names: list[str] = []
    for category_name in _CATEGORY_ORDER:
        patterns = _PATTERNS_BY_CATEGORY[category_name]
        if any(pattern.search(scan_region) for pattern in patterns):
            fired_category_names.append(category_name)

    if not fired_category_names:
        return CallbackPhishingAssessment(
            fired=False,
            categories=(),
            recommended_risk_floor_lift=0,
            out_of_band_verification_required=False,
        )

    lift = _compute_lift(fired_category_names)
    categories = tuple(
        CallbackPhishingCategory(
            category_name=name,  # type: ignore[arg-type]
            why_this_category=_CATEGORY_REASONS[name],
        )
        for name in fired_category_names
    )

    return CallbackPhishingAssessment(
        fired=True,
        categories=categories,
        recommended_risk_floor_lift=lift,
        out_of_band_verification_required=True,
    )


# ---------------------------------------------------------------------------
# §4.1 lift computation
# ---------------------------------------------------------------------------


def _compute_lift(fired_category_names: list[str]) -> int:
    """Compute the §4.1 risk-floor lift from the set of fired category names.

    Banding (per spec §4.1):

    - 3 or more categories fired                                     -> 85
    - ``payment_redirect_call`` AND ``do_not_use_known_channel`` both
      fired (the named payment-overlap row), regardless of total     -> 85
    - 2 or more categories fired (generic)                           -> 70
    - 1 category fired AND that category is ``payment_redirect_call``
      (the single-category payment-overlap row)                      -> 70
    - 1 category fired, not ``payment_redirect_call``                -> 50

    The function is total over non-empty inputs. The empty-input case is
    handled by the caller, which returns the no-fire assessment before
    calling this helper.
    """

    fired_set = set(fired_category_names)
    count = len(fired_category_names)

    if count >= 3:
        return _LIFT_THREE_PLUS_OR_PAYMENT_PLUS_KNOWN_CHANNEL
    if _PAYMENT_REDIRECT_CALL in fired_set and _DO_NOT_USE_KNOWN_CHANNEL in fired_set:
        return _LIFT_THREE_PLUS_OR_PAYMENT_PLUS_KNOWN_CHANNEL
    if count >= 2:
        return _LIFT_TWO_CATEGORIES_OR_PAYMENT_SINGLE
    if _PAYMENT_REDIRECT_CALL in fired_set:
        return _LIFT_TWO_CATEGORIES_OR_PAYMENT_SINGLE
    return _LIFT_SINGLE_CATEGORY


__all__ = [
    "CALLBACK_PHISHING_PATTERN_FLAG",
    "OUT_OF_BAND_VERIFICATION_WORDING",
    "detect_callback_phishing",
]
