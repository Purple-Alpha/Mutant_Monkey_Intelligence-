"""Tests for the Callback Phishing / TOAD body-language detector (Part 1).

Covers the pure-function detector
``core.scoring.callback_phishing_detector.detect_callback_phishing`` and the
schema invariants on the Pydantic
``core.blackboard.CallbackPhishingAssessment`` /
``core.blackboard.CallbackPhishingCategory`` models.

Pass 1 scope per
``4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md`` §9.3:
detector + schema + tests for §8 gate tests 1-9 and 12. The pass 2 gates
(§8.10 D8 rendering wording, §8.11 rubric integration, §8.13 activation
flag, §8.14 production-loop-rebuild flag preservation) require scoring-
agent wiring + rubric §11.1 amendment + activation flag and live in a
separate pass behind a fresh operator start-build instruction.
"""

from __future__ import annotations

import copy
import re
import typing
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.blackboard import (
    BehavioralDeviationFlag,
    CallbackPhishingAssessment,
    CallbackPhishingCategory,
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailInboundPayload,
)
from core.scoring.callback_phishing_detector import (
    CALLBACK_PHISHING_PATTERN_FLAG,
    OUT_OF_BAND_VERIFICATION_WORDING,
    detect_callback_phishing,
)


# ---------------------------------------------------------------------------
# Canonical fixtures (per spec §3 example phrase shapes)
# ---------------------------------------------------------------------------

_BENIGN_BODY = (
    "Hi Sam,\n\n"
    "Please find attached our October invoice. Payment terms remain net 30. "
    "If you have any questions about the line items, our billing team is "
    "available Monday through Friday. Thanks for your continued business.\n\n"
    "Best,\nAlex"
)

_LEGITIMATE_CALL_LINE_WITHOUT_MISDIRECTION = (
    "Hello,\n\n"
    "Attached is your monthly statement. If anything looks off, please call "
    "our billing line during normal business hours to chat with one of our "
    "associates. We are always happy to walk through the details.\n\n"
    "Regards,\nBilling Team"
)

_CALL_NOW_PRESSURE_BODY = (
    "URGENT - call us immediately to avoid having your account suspended. "
    "Do not delay - call our team right now."
)

_DO_NOT_USE_KNOWN_CHANNEL_BODY = (
    "Hi - the old number you have on file is no longer valid. Do not use "
    "the number on file or any previous contact details for this matter."
)

_VOICE_ONLY_FINALIZE_BODY = (
    "Quick note - we cannot finalize this over email. Please phone us so we "
    "can complete the change. Email will not be checked, call us at the "
    "number below."
)

_SUPPORT_LINE_SUBSTITUTION_BODY = (
    "Heads-up - please call our new fraud-prevention desk at the number "
    "below. Use the updated phone number for support going forward."
)

_PAYMENT_REDIRECT_CALL_BODY = (
    "Hi - the wire instructions changed. Please call us to confirm the new "
    "ACH instructions before sending Friday's payment."
)


# ---------------------------------------------------------------------------
# §8.1 - Benign / empty inputs do not fire
# ---------------------------------------------------------------------------


def test_no_fire_on_benign_body() -> None:
    """§8.1 - benign mail control: no flag, no overlay, no floor lift."""

    assessment = detect_callback_phishing(body_plain=_BENIGN_BODY)
    assert assessment.fired is False
    assert assessment.categories == ()
    assert assessment.recommended_risk_floor_lift == 0
    assert assessment.out_of_band_verification_required is False


def test_no_fire_on_empty_body() -> None:
    assessment = detect_callback_phishing(body_plain="")
    assert assessment.fired is False
    assert assessment.categories == ()
    assert assessment.recommended_risk_floor_lift == 0
    assert assessment.out_of_band_verification_required is False


def test_no_fire_on_whitespace_only_body() -> None:
    assessment = detect_callback_phishing(body_plain="   \n\t   \n")
    assert assessment.fired is False


def test_no_fire_on_legitimate_call_our_billing_line_without_misdirection() -> None:
    """§7 failure mode 1 - a simple 'please call our billing line' email does
    not fire. The detector requires misdirection, urgency, or off-channel
    coercion framings.
    """

    assessment = detect_callback_phishing(
        body_plain=_LEGITIMATE_CALL_LINE_WITHOUT_MISDIRECTION
    )
    assert assessment.fired is False
    assert assessment.categories == ()


# ---------------------------------------------------------------------------
# §8.2 - Single-category fire produces lift 50 (needs_review band)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body, expected_category",
    [
        (_CALL_NOW_PRESSURE_BODY, "call_now_pressure"),
        (_DO_NOT_USE_KNOWN_CHANNEL_BODY, "do_not_use_known_channel"),
        (_VOICE_ONLY_FINALIZE_BODY, "voice_only_finalize"),
        (_SUPPORT_LINE_SUBSTITUTION_BODY, "support_line_substitution"),
    ],
)
def test_single_non_payment_category_fires_with_lift_50(
    body: str, expected_category: str
) -> None:
    """§8.2 - exactly one category fires; lift == 50; flag + overlay
    contract held; the OOB verification flag is set per D8."""

    assessment = detect_callback_phishing(body_plain=body)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 50
    assert assessment.out_of_band_verification_required is True
    assert len(assessment.categories) == 1
    assert assessment.categories[0].category_name == expected_category


# ---------------------------------------------------------------------------
# §4.1 row 2 - single payment_redirect_call fire lifts to 70, not 50
# ---------------------------------------------------------------------------


def test_single_payment_redirect_call_lifts_to_70_not_50() -> None:
    """§4.1 row 2: '1 category overlapping payment_redirect_call' => 70."""

    assessment = detect_callback_phishing(body_plain=_PAYMENT_REDIRECT_CALL_BODY)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 70
    assert len(assessment.categories) == 1
    assert assessment.categories[0].category_name == "payment_redirect_call"


# ---------------------------------------------------------------------------
# §8.3 - Two-or-more category (generic) fire produces lift 70
# ---------------------------------------------------------------------------


def test_two_category_generic_fire_lifts_to_70() -> None:
    """§8.3 - two non-payment-overlap categories fire; lift == 70."""

    body = (
        f"{_CALL_NOW_PRESSURE_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}"
    )
    assessment = detect_callback_phishing(body_plain=body)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 70
    assert len(assessment.categories) == 2
    fired_names = {category.category_name for category in assessment.categories}
    assert "call_now_pressure" in fired_names
    assert "voice_only_finalize" in fired_names


# ---------------------------------------------------------------------------
# §8.4 - payment_redirect_call + do_not_use_known_channel lifts to 85
# ---------------------------------------------------------------------------


def test_payment_plus_known_channel_overlap_lifts_to_85() -> None:
    """§8.4 - the named payment-overlap row from §4.1: even with only 2
    categories fired, the (payment_redirect_call + do_not_use_known_channel)
    combination lifts to 85 (matches the FSL hit floor)."""

    body = (
        f"{_PAYMENT_REDIRECT_CALL_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}"
    )
    assessment = detect_callback_phishing(body_plain=body)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 85
    fired_names = {category.category_name for category in assessment.categories}
    assert "payment_redirect_call" in fired_names
    assert "do_not_use_known_channel" in fired_names


# ---------------------------------------------------------------------------
# §4.1 row 3 - three or more categories => 85
# ---------------------------------------------------------------------------


def test_three_or_more_categories_lifts_to_85() -> None:
    """§4.1 row 3: '>=3 categories' => 85, regardless of which three."""

    body = (
        f"{_CALL_NOW_PRESSURE_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}"
    )
    assessment = detect_callback_phishing(body_plain=body)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 85
    assert len(assessment.categories) >= 3


def test_all_five_categories_fires_at_85() -> None:
    body = (
        f"{_CALL_NOW_PRESSURE_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}\n\n"
        f"{_PAYMENT_REDIRECT_CALL_BODY}"
    )
    assessment = detect_callback_phishing(body_plain=body)

    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 85
    assert len(assessment.categories) == 5


# ---------------------------------------------------------------------------
# §8.5 - Determinism
# ---------------------------------------------------------------------------


def test_detector_is_deterministic_for_same_input() -> None:
    """§8.5 - same fixture run twice yields equal CallbackPhishingAssessment.

    We compare by model_dump rather than by ``==`` so the deterministic
    contract holds at the serialized payload level (the level that lands on
    the blackboard) and not only at object-identity.
    """

    body = (
        f"{_PAYMENT_REDIRECT_CALL_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}"
    )

    first = detect_callback_phishing(body_plain=body)
    second = detect_callback_phishing(body_plain=body)
    third = detect_callback_phishing(body_plain=body)

    assert first.model_dump() == second.model_dump()
    assert second.model_dump() == third.model_dump()


# ---------------------------------------------------------------------------
# §8.6 - Detector does not mutate the input EmailInboundPayload
# ---------------------------------------------------------------------------


def test_detector_does_not_mutate_email_inbound_payload() -> None:
    """§8.6 - snapshot before == snapshot after.

    The detector takes ``body_plain`` directly (not the whole payload), so
    no field of the payload could plausibly change. We still snapshot the
    full payload to lock the §8.6 contract end-to-end.
    """

    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 30, 12, 0, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="ap@buyer.example",
        subject="Updated banking details",
        body_plain=_PAYMENT_REDIRECT_CALL_BODY,
    )

    before = payload.model_dump()
    detect_callback_phishing(body_plain=payload.body_plain)
    after = payload.model_dump()

    assert before == after


# ---------------------------------------------------------------------------
# §8.7 - No global state / per-tenant isolation (pass-1-level equivalent)
# ---------------------------------------------------------------------------


def test_detector_has_no_global_state_when_called_in_interleaved_order() -> None:
    """§8.7 (pass-1-level) - the detector is a pure function with no module-
    level mutable state. Running it across multiple inputs in interleaved
    order MUST produce the same per-input result as running each input in
    isolation. The full cross-tenant blackboard isolation gate test is
    §8.7's pass-2 form and lands with the scoring-agent wiring; this pass-1
    test pins the underlying invariant (no global state) that the pass-2
    test relies on.
    """

    inputs = [
        _BENIGN_BODY,
        _CALL_NOW_PRESSURE_BODY,
        _BENIGN_BODY,
        _PAYMENT_REDIRECT_CALL_BODY,
        _DO_NOT_USE_KNOWN_CHANNEL_BODY,
        _BENIGN_BODY,
        _VOICE_ONLY_FINALIZE_BODY,
    ]

    isolated = [detect_callback_phishing(body_plain=text) for text in inputs]
    interleaved = [detect_callback_phishing(body_plain=text) for text in inputs]
    reversed_run = list(
        reversed(
            [
                detect_callback_phishing(body_plain=text)
                for text in reversed(inputs)
            ]
        )
    )

    assert [item.model_dump() for item in isolated] == [
        item.model_dump() for item in interleaved
    ]
    assert [item.model_dump() for item in isolated] == [
        item.model_dump() for item in reversed_run
    ]


# ---------------------------------------------------------------------------
# §8.8 - Lift-only invariant (pass-1-level: the detector never emits a
# negative or sub-50 lift on a fire, so the pass-2 wiring's max-merge can
# never lower a floor)
# ---------------------------------------------------------------------------


def test_lift_is_non_negative_and_at_least_50_on_fire() -> None:
    """§8.8 (pass-1-level lift-only invariant) - on a fire, the lift is
    always one of {50, 70, 85} per §4.1 banding. The full max-merge /
    "does not lower an upstream risk_score of 95" test belongs to the
    pass-2 scoring-agent wiring; this pass-1 test pins the underlying
    property (the detector never emits a value that could lower a floor)."""

    bodies = [
        _CALL_NOW_PRESSURE_BODY,
        _DO_NOT_USE_KNOWN_CHANNEL_BODY,
        _VOICE_ONLY_FINALIZE_BODY,
        _SUPPORT_LINE_SUBSTITUTION_BODY,
        _PAYMENT_REDIRECT_CALL_BODY,
        f"{_PAYMENT_REDIRECT_CALL_BODY}\n\n{_DO_NOT_USE_KNOWN_CHANNEL_BODY}",
        f"{_CALL_NOW_PRESSURE_BODY}\n\n{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}",
    ]

    for body in bodies:
        assessment = detect_callback_phishing(body_plain=body)
        assert assessment.fired is True, f"expected fire on body: {body[:60]!r}"
        assert assessment.recommended_risk_floor_lift in {50, 70, 85}


def test_lift_is_zero_when_not_fired() -> None:
    assessment = detect_callback_phishing(body_plain=_BENIGN_BODY)
    assert assessment.recommended_risk_floor_lift == 0


# ---------------------------------------------------------------------------
# §8.9 - D7 PII / lure-text safety on why_this_category strings
# ---------------------------------------------------------------------------


_DIGIT_RUN_RE = re.compile(r"\d{7,}")
_LONG_ECHO_RE = re.compile(r"\S{61,}")


def test_why_this_category_strings_satisfy_d7_pii_safety() -> None:
    """§8.9 - assertion on ``why_this_category`` strings: no ``@`` symbol,
    no raw digit sequences >= 7 characters, no raw ``Received:`` header
    content, and no echoed substring of length > 60 characters."""

    body = (
        f"{_CALL_NOW_PRESSURE_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}\n\n"
        f"{_PAYMENT_REDIRECT_CALL_BODY}\n\n"
        "Received: from mta.attacker.example (mta.attacker.example "
        "[203.0.113.42])\n"
        "by mx.victim.example (Postfix) with ESMTPS id 1A2B3C4D5E6F\n"
        "for <ap@victim.example>; Sat, 30 May 2026 12:00:00 +0000\n"
        "Please call 555-867-5309 immediately."
    )
    assessment = detect_callback_phishing(body_plain=body)
    assert assessment.fired is True

    for category in assessment.categories:
        text = category.why_this_category
        assert "@" not in text, f"@-symbol leaked into why_this_category: {text!r}"
        assert _DIGIT_RUN_RE.search(text) is None, (
            f"raw digit run leaked into why_this_category: {text!r}"
        )
        assert "Received:" not in text
        assert _LONG_ECHO_RE.search(text) is None
        assert len(text) <= 160


def test_why_this_category_strings_do_not_echo_email_body_substrings() -> None:
    """Direct check against the lure text: the rendered explanation MUST NOT
    contain the matched phrase from the body."""

    body = (
        "URGENT - call us immediately to avoid having your account suspended. "
        "The old number you have on file is no longer valid. Wire instructions "
        "changed - please call us to confirm the new ACH instructions."
    )
    assessment = detect_callback_phishing(body_plain=body)
    assert assessment.fired is True

    forbidden_substrings = (
        "URGENT",
        "old number you have on file",
        "Wire instructions changed",
        "please call us to confirm the new ACH instructions",
        "account suspended",
    )
    for category in assessment.categories:
        for forbidden in forbidden_substrings:
            assert forbidden not in category.why_this_category, (
                f"forbidden lure substring {forbidden!r} leaked into "
                f"why_this_category: {category.why_this_category!r}"
            )


# ---------------------------------------------------------------------------
# §8.12 - Schema discipline (StrictModel + no phone_number_assessment slot)
# ---------------------------------------------------------------------------


def test_assessment_rejects_extra_keys() -> None:
    """§8.12 part 1 - ``CallbackPhishingAssessment`` is a strict /
    extra-keys-forbidden model. Any unexpected key raises ValidationError."""

    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=False,
            categories=(),
            recommended_risk_floor_lift=0,
            out_of_band_verification_required=False,
            unauthorized_extra_field="this should not validate",  # type: ignore[call-arg]
        )


def test_assessment_rejects_phone_number_assessment_key() -> None:
    """§8.12 part 2 (per D15) - the v1 schema has NO ``phone_number_assessment``
    slot. Any attempt to construct or deserialize the model with that key
    must raise ValidationError, proving v1 stayed additive-only and that
    any future Part 2 phone-number slot must arrive through its own §11-
    signed spec, not as a silent v1 patch."""

    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=False,
            categories=(),
            recommended_risk_floor_lift=0,
            out_of_band_verification_required=False,
            phone_number_assessment=None,  # type: ignore[call-arg]
        )

    with pytest.raises(ValidationError):
        CallbackPhishingAssessment.model_validate(
            {
                "fired": False,
                "categories": [],
                "recommended_risk_floor_lift": 0,
                "out_of_band_verification_required": False,
                "phone_number_assessment": {"any": "shape"},
            }
        )


def test_category_rejects_unknown_category_name() -> None:
    """``CallbackPhishingCategory.category_name`` is a closed Literal of the
    five v1 categories (D11). Adding ``mfa_bypass_call`` would have to go
    through a v1.1 spec addendum + schema bump, not a silent code change."""

    with pytest.raises(ValidationError):
        CallbackPhishingCategory(
            category_name="mfa_bypass_call",  # type: ignore[arg-type]
            why_this_category="invalid category name should fail validation",
        )


def test_category_rejects_empty_why_string() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingCategory(
            category_name="call_now_pressure",
            why_this_category="",
        )


def test_category_rejects_overlong_why_string() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingCategory(
            category_name="call_now_pressure",
            why_this_category="x" * 161,
        )


# ---------------------------------------------------------------------------
# Schema invariants when fired=False / fired=True (spec §5)
# ---------------------------------------------------------------------------


def test_fired_false_must_have_empty_categories() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=False,
            categories=(
                CallbackPhishingCategory(
                    category_name="call_now_pressure",
                    why_this_category="contradiction with fired=False",
                ),
            ),
            recommended_risk_floor_lift=0,
            out_of_band_verification_required=False,
        )


def test_fired_false_must_have_zero_lift() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=False,
            categories=(),
            recommended_risk_floor_lift=50,
            out_of_band_verification_required=False,
        )


def test_fired_false_must_have_oob_false() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=False,
            categories=(),
            recommended_risk_floor_lift=0,
            out_of_band_verification_required=True,
        )


def test_fired_true_must_have_non_empty_categories() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=True,
            categories=(),
            recommended_risk_floor_lift=50,
            out_of_band_verification_required=True,
        )


def test_fired_true_must_have_lift_at_least_50() -> None:
    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=True,
            categories=(
                CallbackPhishingCategory(
                    category_name="call_now_pressure",
                    why_this_category="single-category fire",
                ),
            ),
            recommended_risk_floor_lift=49,
            out_of_band_verification_required=True,
        )


def test_fired_true_must_have_oob_true() -> None:
    """D8 contract: whenever the detector fires, the OOB verification flag
    MUST be set so downstream rendering wiring (pass 2) emits the project-
    standard wording."""

    with pytest.raises(ValidationError):
        CallbackPhishingAssessment(
            fired=True,
            categories=(
                CallbackPhishingCategory(
                    category_name="call_now_pressure",
                    why_this_category="single-category fire",
                ),
            ),
            recommended_risk_floor_lift=50,
            out_of_band_verification_required=False,
        )


def test_detector_version_pinned_to_v1() -> None:
    assessment = detect_callback_phishing(body_plain=_BENIGN_BODY)
    assert assessment.detector_version == "v1"


# ---------------------------------------------------------------------------
# BehavioralDeviationFlag Literal extension lock
# ---------------------------------------------------------------------------


def test_behavioral_deviation_flag_literal_includes_callback_phishing_pattern() -> None:
    """Pin: the schema-versioned BehavioralDeviationFlag Literal MUST contain
    'callback_phishing_pattern' so the scoring-agent wiring (pass 2) can
    append it to ``EmailAnalysisRiskAnalysis.behavioral_deviation_flags``
    without inventing a freeform flag string. D2 of the TOAD spec."""

    allowed_values = typing.get_args(BehavioralDeviationFlag)
    assert CALLBACK_PHISHING_PATTERN_FLAG in allowed_values
    assert CALLBACK_PHISHING_PATTERN_FLAG == "callback_phishing_pattern"


def test_callback_phishing_pattern_flag_constant_matches_literal_value() -> None:
    assert isinstance(CALLBACK_PHISHING_PATTERN_FLAG, str)
    assert CALLBACK_PHISHING_PATTERN_FLAG == "callback_phishing_pattern"


# ---------------------------------------------------------------------------
# EmailAnalysisPayload optional carry of CallbackPhishingAssessment
# ---------------------------------------------------------------------------


def _make_minimal_risk_analysis() -> EmailAnalysisRiskAnalysis:
    return EmailAnalysisRiskAnalysis(
        risk_score=10,
        risk_factors=[],
        phishing_signals=[],
        urgency_signals=[],
        financial_risk="low",
        vendor_fraud_score=0,
        wire_transfer_anomaly_score=0,
    )


def test_email_analysis_payload_defaults_callback_phishing_assessment_to_none() -> None:
    """Backward compatibility: existing fixtures that construct an
    EmailAnalysisPayload without the new field must still validate."""

    from uuid import uuid4

    payload = EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        risk_analysis=_make_minimal_risk_analysis(),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0
        ),
        recommended_action="safe",
    )
    assert payload.callback_phishing_assessment is None


def test_email_analysis_payload_accepts_optional_callback_phishing_assessment() -> None:
    from uuid import uuid4

    detector_assessment = detect_callback_phishing(body_plain=_PAYMENT_REDIRECT_CALL_BODY)
    payload = EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        risk_analysis=_make_minimal_risk_analysis(),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0
        ),
        recommended_action="safe",
        callback_phishing_assessment=detector_assessment,
    )
    assert payload.callback_phishing_assessment is not None
    assert payload.callback_phishing_assessment.fired is True


# ---------------------------------------------------------------------------
# Canonical-order discipline + closed vocabulary
# ---------------------------------------------------------------------------


_CANONICAL_ORDER = (
    "call_now_pressure",
    "do_not_use_known_channel",
    "voice_only_finalize",
    "support_line_substitution",
    "payment_redirect_call",
)


def test_categories_emit_in_canonical_order_regardless_of_match_order_in_body() -> None:
    """The detector emits categories in canonical
    ``_CATEGORY_ORDER`` order, not in the order they appear in the body.
    This is a determinism property that downstream consumers (rubric
    mapper, daily-digest renderer) can rely on."""

    body_reverse = (
        f"{_PAYMENT_REDIRECT_CALL_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}\n\n"
        f"{_CALL_NOW_PRESSURE_BODY}"
    )
    body_forward = (
        f"{_CALL_NOW_PRESSURE_BODY}\n\n"
        f"{_DO_NOT_USE_KNOWN_CHANNEL_BODY}\n\n"
        f"{_VOICE_ONLY_FINALIZE_BODY}\n\n"
        f"{_SUPPORT_LINE_SUBSTITUTION_BODY}\n\n"
        f"{_PAYMENT_REDIRECT_CALL_BODY}"
    )

    reverse_assessment = detect_callback_phishing(body_plain=body_reverse)
    forward_assessment = detect_callback_phishing(body_plain=body_forward)

    reverse_names = tuple(c.category_name for c in reverse_assessment.categories)
    forward_names = tuple(c.category_name for c in forward_assessment.categories)

    assert reverse_names == _CANONICAL_ORDER
    assert forward_names == _CANONICAL_ORDER
    assert reverse_names == forward_names


def test_categories_tuple_is_immutable_attempt() -> None:
    """``CallbackPhishingAssessment.categories`` is typed as a ``tuple``
    rather than a ``list`` so consumers cannot mutate it in place. This
    test pins the type at the schema level."""

    assessment = detect_callback_phishing(body_plain=_CALL_NOW_PRESSURE_BODY)
    assert isinstance(assessment.categories, tuple)


# ---------------------------------------------------------------------------
# OOB verification wording constant
# ---------------------------------------------------------------------------


def test_out_of_band_verification_wording_matches_d8_contract() -> None:
    """The shared project-standard out-of-band verification wording is the
    same string used by Financial State Ledger and Two-Channel Confirmation
    Enforcement. Pinning it here ensures pass 2 rendering wiring (daily-
    digest agent prompt + deterministic demo renderer) embeds the exact
    string the §8 gate test 10 will assert in pass 2."""

    expected = (
        "verify through a previously-known channel, "
        "not via the number in this email."
    )
    assert OUT_OF_BAND_VERIFICATION_WORDING == expected


# ---------------------------------------------------------------------------
# Phone-number safety (D3)
# ---------------------------------------------------------------------------


def test_detector_does_not_extract_or_echo_phone_numbers_in_assessment() -> None:
    """D3 - v1 must not extract, normalise, hash, or store phone-number
    digits in any form. The assessment object exposes no phone-number field,
    and even when the body contains an obvious phone-number-shaped pattern,
    the rendered ``why_this_category`` strings carry no raw digits."""

    body_with_phone = (
        "URGENT - call us at 1-555-867-5309 immediately to avoid losing access. "
        "Do not use the number on file. Wire instructions changed - please call "
        "us to confirm the new ACH instructions at +1 (555) 867-5309."
    )
    assessment = detect_callback_phishing(body_plain=body_with_phone)
    assert assessment.fired is True

    digit_re = re.compile(r"\d")
    for category in assessment.categories:
        assert digit_re.search(category.why_this_category) is None, (
            f"phone-number digit leaked into why_this_category: "
            f"{category.why_this_category!r}"
        )

    serialized = assessment.model_dump()
    assert "phone_number" not in serialized
    assert "phone_number_assessment" not in serialized


# ---------------------------------------------------------------------------
# Body-plain only (D14) - the detector ignores anything outside body_plain
# ---------------------------------------------------------------------------


def test_detector_reads_only_body_plain_and_not_payload_html() -> None:
    """D14 - v1 reads ``body_plain`` only. The detector function signature
    accepts only the body_plain string, so even if a payload carries
    body_html with TOAD lure language, passing only body_plain proves
    the detector cannot accidentally read HTML."""

    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 30, 12, 0, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="ap@buyer.example",
        body_plain=_BENIGN_BODY,
        body_html=(
            "<html><body>URGENT - call us immediately to avoid having your "
            "account suspended. Do not delay - call our team right now.</body></html>"
        ),
    )

    assessment = detect_callback_phishing(body_plain=payload.body_plain)
    assert assessment.fired is False, (
        "detector must read body_plain only (D14); HTML body lure language "
        "must NOT leak into the v1 fire path"
    )


# ---------------------------------------------------------------------------
# Categories deep-equality with model_dump (locks the assessment shape)
# ---------------------------------------------------------------------------


def test_assessment_model_dump_shape_for_a_single_fire() -> None:
    """Lock the serialized shape of the assessment so consumers (rubric,
    digest, blackboard storage) can rely on the exact field set."""

    assessment = detect_callback_phishing(body_plain=_CALL_NOW_PRESSURE_BODY)
    dumped = assessment.model_dump()

    assert set(dumped.keys()) == {
        "detector_version",
        "fired",
        "categories",
        "recommended_risk_floor_lift",
        "out_of_band_verification_required",
    }
    assert dumped["detector_version"] == "v1"
    assert dumped["fired"] is True
    assert dumped["recommended_risk_floor_lift"] == 50
    assert dumped["out_of_band_verification_required"] is True
    # Pydantic v2 preserves the declared ``tuple[CallbackPhishingCategory, ...]``
    # type through ``model_dump()`` rather than coercing to ``list``. The
    # important property for downstream consumers is "iterable of dict rows
    # with the expected key set" — that's what we assert here.
    assert len(dumped["categories"]) == 1
    assert set(dumped["categories"][0].keys()) == {
        "category_name",
        "why_this_category",
    }


def test_assessment_model_dump_shape_for_a_no_fire() -> None:
    assessment = detect_callback_phishing(body_plain=_BENIGN_BODY)
    dumped = assessment.model_dump()

    assert dumped == {
        "detector_version": "v1",
        "fired": False,
        "categories": (),
        "recommended_risk_floor_lift": 0,
        "out_of_band_verification_required": False,
    }


# ---------------------------------------------------------------------------
# Deep copy safety - assessments are independent across calls
# ---------------------------------------------------------------------------


def test_assessments_returned_by_separate_calls_are_independent() -> None:
    """Pure-function contract: two calls return independent objects whose
    field values do not share mutable state."""

    first = detect_callback_phishing(body_plain=_CALL_NOW_PRESSURE_BODY)
    second = detect_callback_phishing(body_plain=_CALL_NOW_PRESSURE_BODY)

    assert first is not second
    assert first.model_dump() == second.model_dump()
    assert copy.deepcopy(first).model_dump() == first.model_dump()
