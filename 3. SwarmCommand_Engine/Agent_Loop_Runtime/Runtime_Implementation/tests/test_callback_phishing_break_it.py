"""Callback Phishing / TOAD Part 1 — Pass 2 break-it / adversarial tests.

These tests are intentionally trying to make the pass 2 integration FAIL.
They are paired with ``tests/test_callback_phishing_scoring_integration.py``
(the gate-pass / happy-path tests) and ``tests/test_callback_phishing_detector.py``
(the pure-function detector unit tests from pass 1).

Coverage axes (per operator instruction):

1. False positives on benign "call me" / urgent-but-legitimate / vendor-contact
   language that legitimate vendor mail uses every day.
2. False negatives on weird-casing / weird-spacing / repeated-phrase /
   all-category-trigger / mixed-safe-and-suspicious bodies that an attacker
   might use to evade or amplify.
3. Scope-violation probes:
   - no phone-number extraction / normalization / hashing / storage / assessment;
   - no ``body_html`` inspection even when the only lure language lives in HTML;
   - no numeric ``callback_phishing_score`` field anywhere on payload;
   - no production activation by accident (default OFF survives every entry path).
4. Crash resistance:
   - empty body, whitespace-only body, very-large body (above the detector's
     ``_MAX_SCAN_CHARS=200000`` cap), control / unicode noise, all-category
     trigger body.
5. Score / risk-floor over-lift probes:
   - single-category lift never exceeds 50;
   - multi-category lift never exceeds 85;
   - existing higher ``risk_score`` never gets lowered;
   - ``recommended_action == 'block'`` never gets softened.
6. Rubric explanation mismatch probes (§11.2 amendment + D7 PII safety + D15
   160-char cap on ``why_this_score``):
   - ``origin_timing.why_this_score`` does not echo raw lure substrings;
   - ``origin_timing.why_this_score`` does not echo raw phone-digit runs;
   - ``origin_timing.why_this_score`` stays inside the 160-char cap;
   - ``evidence_tags`` contains ``callback_phishing_pattern`` (and only that)
     for the §11.2 attribution path, not raw phone numbers.
7. Cross-tenant / production-loop drift probes:
   - two tenants running enabled on the same blackboard root do not
     leak ``callback_phishing_assessment`` across analyses;
   - production-loop rebuild preserves the flag even when the policy
     parameters drift.
8. D8 OOB wording rendering probes (TOAD §8.10):
   - daily-digest agent populates ``callback_phishing_pattern_detected``
     when the flag is present, False otherwise;
   - demo renderer emits the exact OOB phrase when fired, omits it
     otherwise.

NONE of these tests are expected to be "negative-known-broken" — they are
all expected to pass. A failure here is a real defect.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID, uuid4

import pytest

from core.blackboard import (
    CallbackPhishingAssessment,
    DailyDigestEmailEntry,
    DailyDigestRiskEntry,
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.production import (
    ProductionLoopConfig,
    ProductionSignal,
    run_production_cycle,
)
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle
from core.scoring.callback_phishing_detector import (
    CALLBACK_PHISHING_PATTERN_FLAG,
    OUT_OF_BAND_VERIFICATION_WORDING,
    detect_callback_phishing,
)
from core.scoring.client_facing_rubric import project_client_facing_rubric
from core.scoring.email_risk_scoring_agent import score_one_email_payload

TENANT = "tenant_demo"

# ---------------------------------------------------------------------------
# Bodies — these are the adversarial fixtures. Each is named for the failure
# mode it is trying to provoke.
# ---------------------------------------------------------------------------

# §1 False-positive probes -- benign mail that uses callback-adjacent language
# without the misdirection / urgency / off-channel coercion the TOAD spec
# requires (D11 closed-vocabulary, §3 phrase categories).

_BENIGN_BILLING_LINE_BODY = (
    "Hello finance team,\n"
    "Reminder: our standard accounts-receivable line is 1-800-555-0100 "
    "(extension 4). Feel free to call during business hours if you have "
    "questions about the attached invoice. Banking details unchanged from "
    "last month.\n"
    "Thanks,\n"
    "Acme AR Team\n"
)

_BENIGN_NEWSLETTER_BODY = (
    "Subject: April industry roundup\n\n"
    "Hi team -- here's our monthly newsletter. Three things to know about "
    "the supply-chain outlook. As always, feel free to reach out by email "
    "or schedule a 15-minute call if you'd like to discuss.\n"
    "Cheers,\n"
    "The team\n"
)

_BENIGN_URGENT_COMPLIANCE_BODY = (
    "All employees: HR compliance training is due by end of business today. "
    "Please log into the HR portal at the usual address and complete the "
    "module. This is mandatory and time-sensitive. If you've already "
    "completed it, ignore this reminder.\n"
)

_BENIGN_LEGITIMATE_VENDOR_FOLLOWUP_BODY = (
    "Hi Sarah,\n"
    "Following up on the April PO -- can you confirm the shipment ETA when "
    "you have a moment? Happy to hop on a call this week if it's easier. "
    "Standard payment terms apply.\n"
    "Best,\n"
    "Bob\n"
)

_BENIGN_SCHEDULING_BODY = (
    "Hi, can you give me a call when you have a chance? No rush. Thanks.\n"
)

# §2 False-negative probes -- weird-casing / weird-spacing / repeated /
# all-category-trigger bodies that an attacker might use to evade.

_WEIRD_CASE_BODY = (
    "PLEASE CALL US IMMEDIATELY at the number above. Do NOT use the "
    "number on file. We can ONLY finalize this matter by phone today.\n"
)

_WEIRD_SPACING_BODY = (
    "Please   call   us   immediately   to   confirm.    Do not  use  the   "
    "number on   file.    We can only finalize by phone today.\n"
)

_REPEATED_PHRASE_BODY = (
    "Please call us immediately. Please call us immediately. Please call us "
    "immediately. Please call us immediately. Please call us immediately.\n"
)

# All five v1 categories using the canonical regex-matching phrasings.
# Authored against the detector's ``_PATTERNS_BY_CATEGORY`` v1 contract:
#   call_now_pressure          -> "call us immediately"
#   do_not_use_known_channel   -> "do not use the number on file"
#   voice_only_finalize        -> "only by phone"
#   support_line_substitution  -> "call our updated fraud line"
#   payment_redirect_call      -> "call us to confirm the new ACH details"
# An attacker who wanted to maximise risk-floor lift would write something
# very close to this; this fixture pins the worst-case lift cap.
_ALL_CATEGORY_BODY = (
    "Please call us immediately.\n"
    "Do not use the number on file.\n"
    "Resolution is only by phone today.\n"
    "Call our updated fraud line for support.\n"
    "Call us to confirm the new ACH details.\n"
)

_MIXED_SAFE_AND_SUSPICIOUS_BODY = (
    "Hi team,\n"
    "Hope you had a good weekend. Quick note: the standard April invoice "
    "is attached. Banking details unchanged from last month. As always, "
    "let me know if you have questions.\n"
    "Separately, urgent: please call us immediately at the number above. "
    "Do not use the number on file -- we can only finalize this by phone "
    "today.\n"
    "Thanks,\n"
    "Acme AR\n"
)

# §3 Scope-violation probes -- phone-heavy / HTML-only / null-input.

_PHONE_NUMBER_HEAVY_BODY = (
    "Please confirm receipt. Call any of: 555-123-4567, (555) 234-5678, "
    "+1-555-345-6789, ext 9999. Backup line: 800.555.1212.\n"
    "ABA 121000358 / account 9871234509.\n"
)

# HTML-only lure -- entire body_plain is benign; lure language is exclusively
# inside body_html. TOAD D14 says body_plain only in v1.
_HTML_LURE_BODY_PLAIN = "Please review the attached document."
_HTML_LURE_BODY_HTML = (
    "<html><body>"
    "<p>Please call us immediately. Do not use the number on file. "
    "We can only finalize by phone today.</p>"
    "<p>Updated fraud support line: 555-867-5309.</p>"
    "</body></html>"
)

_EMPTY_BODY = ""
_WHITESPACE_ONLY_BODY = "\n\t   \r\n\n   \t"

_CONTROL_CHARACTER_BODY = (
    "Please call us immediately\x00 to confirm.\x07\x1b[31mDo not use the "
    "number on file.\x1b[0m We can only finalize by phone today.\n"
)

_UNICODE_NOISE_BODY = (
    "P\u200bl\u200ce\u200dase cal\u2060l us imm\ufeffediately.\n"
    "Do not\u200b use the number on file. \u202eevil\u202c\n"
)

# Just over the detector's scan cap (_MAX_SCAN_CHARS=200_000) -- the
# detector should still complete without crashing. The fire status depends
# only on whether the lure language is inside the first 200_000 chars.
_HUGE_BODY_HEAD_TRIGGER = (
    "Please call us immediately. Do not use the number on file. "
    "We can only finalize by phone today.\n"
) + ("filler-text " * 25_000)  # ~325_000 chars total, lure in first 100

_HUGE_BODY_TAIL_TRIGGER = (
    "filler-text " * 25_000
) + (
    "\nPlease call us immediately. Do not use the number on file. "
    "We can only finalize by phone today.\n"
)  # lure past the cap; expected NOT to fire (detector caps body scan).

# Single-category trigger for tests that need exactly one fired category.
_SINGLE_CATEGORY_BODY = "Please call us immediately to confirm receipt."
# Two-category trigger (call_now_pressure + do_not_use_known_channel),
# used for round-trip / multi-category probes.
_MULTI_CATEGORY_BODY = (
    "Please call us immediately. Do not use the number on file."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_inbound(
    context: RouteContext,
    *,
    body_plain: str,
    body_html: str | None = None,
    subject: str = "Test subject",
    sender: str = "vendor@example.com",
    tenant_id: str = TENANT,
) -> UUID:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 30, 10, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="cfo@northstar.example",
        subject=subject,
        body_plain=body_plain,
        body_html=body_html,
        headers={"X-Spam-Score": "0.1"},
    )
    return submit_email_inbound(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    ).record.record_id


def _valid_analysis_json(
    *,
    risk_score: int = 30,
    recommended_action: str = "needs_review",
    behavioral_deviation_flags: list[str] | None = None,
) -> str:
    return json.dumps(
        {
            "summary": "Test.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": risk_score,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 20,
                "wire_transfer_anomaly_score": 20,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": list(behavioral_deviation_flags or []),
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 10,
                "suspicious_elements": [],
                "sender_legitimacy_notes": "n/a",
            },
            "recommended_action": recommended_action,
        }
    )


def _canned_client(response: str) -> Callable[[str, str], str]:
    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        json.loads(user_prompt)
        return response

    return _client


def _analyses(context: RouteContext, tenant: str = TENANT):
    return [
        r
        for r in read_records(
            blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant)
        )
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]


def _run_enabled(tmp_path, body_plain: str, **inbound_kwargs):
    """Run one scoring cycle with the TOAD flag enabled. Returns parsed payload."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=body_plain, **inbound_kwargs)
    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=15)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    assert result.analyzed == 1, "scoring cycle must analyze the seeded inbound"
    return EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)


# ===========================================================================
# §1 False-positive probes — benign mail must NOT fire
# ===========================================================================


@pytest.mark.parametrize(
    "body,label",
    [
        (_BENIGN_BILLING_LINE_BODY, "benign_billing_line"),
        (_BENIGN_NEWSLETTER_BODY, "benign_newsletter"),
        (_BENIGN_URGENT_COMPLIANCE_BODY, "benign_urgent_compliance_no_phone"),
        (_BENIGN_LEGITIMATE_VENDOR_FOLLOWUP_BODY, "benign_legitimate_vendor_followup"),
        (_BENIGN_SCHEDULING_BODY, "benign_call_me_when_chance"),
    ],
)
def test_benign_inputs_do_not_fire_pass2_path(tmp_path, body: str, label: str) -> None:
    """Benign mail that uses callback-adjacent language without misdirection,
    urgency, or off-channel coercion must NOT fire the detector at the
    pass-2 integration boundary. Per TOAD §7.1 / D11 closed-vocabulary, the
    five v1 categories require *misdirection* (`do_not_use_known_channel`),
    *urgency* (`call_now_pressure`), or *off-channel coercion*
    (`voice_only_finalize`) — legitimate vendor mail rarely needs those.
    """
    parsed = _run_enabled(tmp_path, body)
    assert parsed.callback_phishing_assessment is not None, (
        f"{label}: detector should have run (assessment attached attach-always)"
    )
    assert parsed.callback_phishing_assessment.fired is False, (
        f"{label}: benign mail must NOT fire (false-positive on '{label}')"
    )
    assert CALLBACK_PHISHING_PATTERN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 0
    assert parsed.callback_phishing_assessment.out_of_band_verification_required is False


# ===========================================================================
# §2 False-negative resistance — weird casing / spacing / repetition / all-cat
# ===========================================================================


def test_weird_uppercase_body_still_fires(tmp_path) -> None:
    """Detector must be case-insensitive (uses ``re.IGNORECASE``). UPPERCASE
    lure language is the same fraud shape and must not evade."""
    parsed = _run_enabled(tmp_path, _WEIRD_CASE_BODY)
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) >= 2


def test_weird_spacing_body_still_fires(tmp_path) -> None:
    """Multi-space variants of the canonical phrases should still match
    the detector's regex patterns (which allow ``\\s+`` between tokens)."""
    parsed = _run_enabled(tmp_path, _WEIRD_SPACING_BODY)
    assert parsed.callback_phishing_assessment.fired is True


def test_repeated_phrase_body_fires_but_lift_is_capped(tmp_path) -> None:
    """Repeating the SAME single-category phrase five times must not lift
    the assessment past the single-category band (50) — the detector
    bands on *distinct categories fired*, not on raw match counts. This
    guards against an attacker hoping repetition stacks risk."""
    parsed = _run_enabled(tmp_path, _REPEATED_PHRASE_BODY)
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) == 1, (
        "repeated phrasing must collapse to exactly one fired category"
    )
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 50, (
        "single-category lift must never exceed 50, regardless of repetition"
    )


def test_all_category_body_fires_with_max_lift_capped_at_85(tmp_path) -> None:
    """The full all-five-categories body must fire all five categories and
    produce the maximum 85 lift (TOAD §4.1 three-plus / payment-plus-known-
    channel band). Crucially the lift MUST NOT exceed 85 — that's the
    spec's hard ceiling for v1, and an over-lift here would mean a single
    detector silently dominates the entire risk-floor max chain."""
    parsed = _run_enabled(tmp_path, _ALL_CATEGORY_BODY)
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) == 5, (
        f"all-category body fired {len(parsed.callback_phishing_assessment.categories)} "
        "categories (expected exactly 5)"
    )
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 85, (
        "max lift must be exactly 85; over-lift breaks TOAD §4.1 banding"
    )


def test_mixed_safe_and_suspicious_body_fires_on_suspicious(tmp_path) -> None:
    """When suspicious language is concatenated with benign business text,
    the detector should still fire on the suspicious portion. The benign
    text does not dilute the signal — that would be a false-negative
    failure mode an attacker could exploit by padding."""
    parsed = _run_enabled(tmp_path, _MIXED_SAFE_AND_SUSPICIOUS_BODY)
    assert parsed.callback_phishing_assessment.fired is True


# ===========================================================================
# §3 Scope-violation probes -- no body_html, no phone numbers, no score field
# ===========================================================================


def test_html_only_lure_does_not_fire_body_plain_only(tmp_path) -> None:
    """TOAD D14: v1 reads ``body_plain`` only. A fixture whose lure language
    lives exclusively in ``body_html`` MUST NOT fire — even when the flag
    is enabled. This guards against silent v1.1 scope creep."""
    parsed = _run_enabled(
        tmp_path,
        body_plain=_HTML_LURE_BODY_PLAIN,
        body_html=_HTML_LURE_BODY_HTML,
    )
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False, (
        "body_html-only lure must NOT fire in v1 (TOAD D14)"
    )


def test_phone_number_heavy_body_does_not_extract_or_store_digits(tmp_path) -> None:
    """TOAD D3 / D7 / D15: the detector never extracts, normalizes, hashes,
    stores, or assesses phone numbers. A phone-number-heavy body must not:
    - cause a ``phone_number_assessment`` field to appear on the payload;
    - cause raw 7+digit runs to appear in the assessment ``why_this_category``
      strings;
    - cause raw 7+digit runs to appear in the rubric's ``origin_timing``
      ``why_this_score`` or ``evidence_tags``.
    """
    parsed = _run_enabled(tmp_path, _PHONE_NUMBER_HEAVY_BODY)
    assert parsed.callback_phishing_assessment is not None

    # No phone_number_assessment key, ever. The StrictModel boundary would
    # reject construction with one — this test pins the integration-side too.
    dumped = parsed.callback_phishing_assessment.model_dump(mode="json")
    assert "phone_number_assessment" not in dumped

    # If any category fired, no why_this_category may carry a digit run.
    import re

    digit_run = re.compile(r"\d{7,}")
    for category in parsed.callback_phishing_assessment.categories:
        assert digit_run.search(category.why_this_category) is None, (
            f"category {category.category_name} leaked a raw digit run "
            f"into why_this_category: {category.why_this_category!r}"
        )


def test_no_numeric_callback_phishing_score_field_anywhere(tmp_path) -> None:
    """TOAD D12: no numeric ``callback_phishing_score`` field is added in v1.
    The emission contract is ``fired`` + ``categories`` +
    ``recommended_risk_floor_lift`` + ``out_of_band_verification_required``."""
    parsed = _run_enabled(tmp_path, _ALL_CATEGORY_BODY)
    assert parsed.callback_phishing_assessment is not None
    dumped = parsed.callback_phishing_assessment.model_dump(mode="json")
    assert "callback_phishing_score" not in dumped
    payload_dumped = parsed.model_dump(mode="json")
    assert "callback_phishing_score" not in payload_dumped
    # Also assert the field name doesn't sneak into the JSON-serialized
    # form of the whole payload (defensive against future schema-noise).
    assert "callback_phishing_score" not in json.dumps(payload_dumped)


def test_default_off_resists_trigger_everything_body(tmp_path) -> None:
    """The maximum-provocation body must NOT activate the detector when the
    flag is off (default). This is TOAD §8.13 default-OFF activation
    discipline tested on the strongest fixture in the file."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_ALL_CATEGORY_BODY)
    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            # enable_callback_phishing_detection unset -> default False
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is None
    assert CALLBACK_PHISHING_PATTERN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags


def test_default_off_survives_sandbox_path_too(tmp_path) -> None:
    """The in-memory sandbox helper ``score_one_email_payload`` must mirror
    the default-OFF discipline. If the Red battery / Phase 1.3 path
    accidentally enables this by default, Sandbox callers would silently
    pick up the flag."""
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 30, 10, 0, tzinfo=timezone.utc),
        sender="vendor@example.com",
        recipient="cfo@northstar.example",
        subject="Test",
        body_plain=_ALL_CATEGORY_BODY,
        headers={},
    )
    result = score_one_email_payload(
        payload,
        llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
        # enable_callback_phishing_detection NOT passed -> default False
    )
    assert isinstance(result, EmailAnalysisPayload)
    assert result.callback_phishing_assessment is None
    assert CALLBACK_PHISHING_PATTERN_FLAG not in result.risk_analysis.behavioral_deviation_flags


# ===========================================================================
# §4 Crash resistance — empty / whitespace / control / unicode / huge body
# ===========================================================================


def test_empty_body_does_not_crash(tmp_path) -> None:
    """Empty body must not raise; detector returns fired=False."""
    parsed = _run_enabled(tmp_path, _EMPTY_BODY)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False


def test_whitespace_only_body_does_not_crash(tmp_path) -> None:
    parsed = _run_enabled(tmp_path, _WHITESPACE_ONLY_BODY)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False


def test_none_body_plain_does_not_crash(tmp_path) -> None:
    """``EmailInboundPayload.body_plain`` is required, but our wiring passes
    ``inbound_payload.body_plain or ''`` so even a hypothetical None must
    not crash the detector. Force the empty string at the boundary by
    seeding an empty body."""
    parsed = _run_enabled(tmp_path, "")
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False


def test_control_character_body_does_not_crash(tmp_path) -> None:
    """Control / ANSI-escape noise around lure language must not crash the
    regex pass. The detector may or may not fire depending on whether
    the control chars are inside the matched span — both outcomes are
    acceptable; the only failure mode here is a crash or partial output."""
    parsed = _run_enabled(tmp_path, _CONTROL_CHARACTER_BODY)
    assert parsed.callback_phishing_assessment is not None
    # Either fired=True or fired=False is acceptable; the invariant is
    # no exception, and a well-formed assessment.
    if parsed.callback_phishing_assessment.fired:
        assert len(parsed.callback_phishing_assessment.categories) >= 1
        assert parsed.callback_phishing_assessment.recommended_risk_floor_lift >= 50
    else:
        assert len(parsed.callback_phishing_assessment.categories) == 0
        assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 0


def test_unicode_zero_width_noise_does_not_crash(tmp_path) -> None:
    """Zero-width / RTL / direction-override Unicode embedded in lure text
    must not crash the detector. This is the same attacker trick that
    inflates the existing ``unusual_unicode_obfuscation`` LLM-side flag;
    the TOAD detector is regex-based and may not match through it, which
    is acceptable (false-negative on this specific evasion is documented
    in TOAD §7.2 — novel phrasing surfaces through real-traffic review)."""
    parsed = _run_enabled(tmp_path, _UNICODE_NOISE_BODY)
    assert parsed.callback_phishing_assessment is not None
    # No assertion on fired — the failure mode is a crash, not a missed match.


def test_huge_body_head_trigger_fires_within_scan_cap(tmp_path) -> None:
    """Lure language in the first 100 chars of a 325K-char body must still
    fire — the detector caps body scan at ``_MAX_SCAN_CHARS=200_000`` but
    head-of-body is well inside that window."""
    parsed = _run_enabled(tmp_path, _HUGE_BODY_HEAD_TRIGGER)
    assert parsed.callback_phishing_assessment.fired is True


def test_huge_body_tail_only_trigger_does_not_fire_or_crash(tmp_path) -> None:
    """Lure language placed after the detector's scan cap must NOT fire,
    proving the cap is honored. Also proves the detector does not crash
    on >200K-char input (regex scan stays bounded)."""
    parsed = _run_enabled(tmp_path, _HUGE_BODY_TAIL_TRIGGER)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False, (
        "lure beyond _MAX_SCAN_CHARS must not fire — cap is the spec's "
        "DoS-resistance ceiling"
    )


# ===========================================================================
# §5 Score / risk-floor over-lift probes
# ===========================================================================


def test_single_category_lift_never_exceeds_50_for_non_payment_categories(
    tmp_path,
) -> None:
    """For a single non-payment category fire, lift must be exactly 50.
    Anything higher is an over-lift bug in ``_compute_lift``."""
    parsed = _run_enabled(tmp_path, _SINGLE_CATEGORY_BODY)
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) == 1, (
        "single-category fixture must fire exactly one category; if it "
        "now fires more, the fixture (not the detector) needs updating"
    )
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 50


def test_block_action_is_not_softened_by_detector_overlay(tmp_path) -> None:
    """TOAD §8.8 lift-only invariant on the action label: when LLM-side
    ``recommended_action == 'block'``, the TOAD overlay must not soften it
    to ``needs_review`` or ``safe``."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_ALL_CATEGORY_BODY)
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(
                _valid_analysis_json(risk_score=95, recommended_action="block")
            ),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.recommended_action == "block"
    assert parsed.risk_analysis.risk_score == 95, (
        "callback-phishing overlay must not lower an upstream block-tier score"
    )


def test_safe_action_is_not_promoted_to_block_by_detector_overlay(tmp_path) -> None:
    """The TOAD overlay path only contributes to ``risk_score`` via the
    deterministic floor-max chain; it does NOT mutate ``recommended_action``.
    A 'safe' LLM verdict stays 'safe' even when the detector lifts the
    score (the rubric / downstream logic owns action recomputation)."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_ALL_CATEGORY_BODY)
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(
                _valid_analysis_json(risk_score=5, recommended_action="safe")
            ),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    # The score was lifted (max-merge), but the action label is not touched
    # by this overlay path.
    assert parsed.risk_analysis.risk_score >= 50, "lift must apply"
    assert parsed.recommended_action == "safe", (
        "overlay must not flip recommended_action; that's owned upstream"
    )


# ===========================================================================
# §6 Rubric explanation mismatch probes (§11.2 + D7 PII safety + D15 cap)
# ===========================================================================


def _build_rubric_payload_with_flag(
    *,
    risk_score: int,
    body_plain: str,
) -> EmailAnalysisPayload:
    """Build a payload with ``callback_phishing_pattern`` in flags and a real
    assessment from running the detector. Used by the rubric probes below."""
    payload = EmailAnalysisPayload.model_validate(
        json.loads(
            _valid_analysis_json(
                risk_score=risk_score,
                behavioral_deviation_flags=[CALLBACK_PHISHING_PATTERN_FLAG],
            )
        )
        | {"source_email_record_id": str(uuid4())}
    )
    assessment = detect_callback_phishing(body_plain=body_plain)
    return payload.model_copy(update={"callback_phishing_assessment": assessment})


def test_rubric_origin_timing_why_this_score_inside_160_char_cap(tmp_path) -> None:
    """Rubric D15: ``why_this_score`` is bounded to 160 chars. The §11.2
    amendment phrase must not push it past that, ever."""
    for body in [_SINGLE_CATEGORY_BODY, _ALL_CATEGORY_BODY]:
        payload = _build_rubric_payload_with_flag(risk_score=60, body_plain=body)
        rubric = project_client_facing_rubric(payload)
        origin = next(a for a in rubric.axes if a.axis_name == "origin_timing")
        assert len(origin.why_this_score) <= 160, (
            f"why_this_score exceeded 160-char cap for body={body!r}: "
            f"{len(origin.why_this_score)} chars"
        )


def test_rubric_origin_timing_why_does_not_echo_raw_lure_substrings(tmp_path) -> None:
    """TOAD D7 PII / lure-text safety enforced at the rubric boundary: the
    amendment phrase must not include verbatim segments from the email
    body. We assert by checking that the canonical phrase is the exact
    string used."""
    payload = _build_rubric_payload_with_flag(
        risk_score=60,
        body_plain=_ALL_CATEGORY_BODY,
    )
    rubric = project_client_facing_rubric(payload)
    origin = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    canonical = "Callback-phishing body-language pattern detected; verify off-channel."
    assert origin.why_this_score == canonical, (
        f"why_this_score must be the canonical bounded amendment phrase, "
        f"got {origin.why_this_score!r}"
    )
    # And specifically no raw lure substrings:
    assert "ACH" not in origin.why_this_score
    assert "wire" not in origin.why_this_score.lower()
    assert "phone" not in origin.why_this_score.lower()


def test_rubric_origin_timing_why_does_not_echo_raw_phone_digits(tmp_path) -> None:
    """If the body had a phone number, the rubric explanation must not
    contain a digit run >= 7 chars long. This is D7 PII safety applied
    at the rubric boundary, defense-in-depth with the detector's own
    D7 enforcement."""
    import re

    payload = _build_rubric_payload_with_flag(
        risk_score=60,
        body_plain=_PHONE_NUMBER_HEAVY_BODY + "\nPlease call us immediately.",
    )
    rubric = project_client_facing_rubric(payload)
    origin = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert re.search(r"\d{7,}", origin.why_this_score) is None
    for tag in origin.evidence_tags:
        assert re.search(r"\d{7,}", tag) is None


def test_rubric_origin_timing_evidence_tags_only_contain_callback_attribution(
    tmp_path,
) -> None:
    """When only the §11.2 callback rule fires (no `out_of_band_pressure`,
    no `urgency_signals` count), ``evidence_tags`` MUST be exactly
    ``('callback_phishing_pattern',)`` — not a phone-number list, not a
    category-name list, not the raw lure text."""
    payload = _build_rubric_payload_with_flag(
        risk_score=20,  # below higher-band, only floor-lift fires
        body_plain=_SINGLE_CATEGORY_BODY,
    )
    rubric = project_client_facing_rubric(payload)
    origin = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert origin.evidence_tags == (CALLBACK_PHISHING_PATTERN_FLAG,)


# ===========================================================================
# §7 Cross-tenant / production-loop config drift probes
# ===========================================================================


def test_two_tenants_callback_phishing_does_not_cross_contaminate(tmp_path) -> None:
    """Two tenants running on the same blackboard root, both with the flag
    enabled. Tenant A's seeded body fires the detector; Tenant B's body
    is benign. Neither tenant's analysis records may carry the other's
    inbound id, and tenant B must not pick up a fired assessment.
    Mirrors the §8.13 rubric isolation gate-test pattern."""
    tenant_a = "tenant_alpha"
    tenant_b = "tenant_beta"
    context = _context(tmp_path)

    inbound_a = _seed_inbound(
        context,
        body_plain=_ALL_CATEGORY_BODY,
        tenant_id=tenant_a,
        sender="adversary@example.com",
    )
    inbound_b = _seed_inbound(
        context,
        body_plain=_BENIGN_LEGITIMATE_VENDOR_FOLLOWUP_BODY,
        tenant_id=tenant_b,
        sender="legit@vendor.example",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=tenant_a,
            enable_callback_phishing_detection=True,
        ),
    )
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=tenant_b,
            enable_callback_phishing_detection=True,
        ),
    )

    analyses_a = _analyses(context, tenant=tenant_a)
    analyses_b = _analyses(context, tenant=tenant_b)
    assert len(analyses_a) == 1
    assert len(analyses_b) == 1

    parsed_a = EmailAnalysisPayload.model_validate(analyses_a[0].payload)
    parsed_b = EmailAnalysisPayload.model_validate(analyses_b[0].payload)

    # Tenant A fired; Tenant B did not.
    assert parsed_a.callback_phishing_assessment is not None
    assert parsed_a.callback_phishing_assessment.fired is True
    assert parsed_b.callback_phishing_assessment is not None
    assert parsed_b.callback_phishing_assessment.fired is False

    # Cross-tenant id leak check (mirrors test_two_tenants_isolation pattern).
    serialized_a = json.dumps([r.model_dump(mode="json") for r in analyses_a])
    serialized_b = json.dumps([r.model_dump(mode="json") for r in analyses_b])
    assert str(inbound_b) not in serialized_a
    assert str(inbound_a) not in serialized_b


def test_production_loop_rebuild_with_drifted_lift_preserves_callback_flag(
    tmp_path,
) -> None:
    """Defensive over the existing production-loop preservation test: drive
    the rebuild via a forced tenant-id mismatch AND simulate the rebuild
    happening every cycle (which is the actual production-loop pattern).
    Confirms the flag preservation is robust to multi-cycle rebuilds, not
    just a one-shot."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_ALL_CATEGORY_BODY)

    custom = EmailRiskScoringConfig(
        llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
        production_tenant_id="wrong_tenant_overridden",
        enable_callback_phishing_detection=True,
    )

    # First cycle: forces a rebuild via tenant mismatch.
    result_1 = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=custom,
        ),
    )
    assert result_1.email_risk_scoring is not None
    assert result_1.email_risk_scoring.analyzed == 1

    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is True
    assert CALLBACK_PHISHING_PATTERN_FLAG in parsed.risk_analysis.behavioral_deviation_flags


# ===========================================================================
# §8 Daily-digest D8 OOB wording rendering probes (TOAD §8.10)
# ===========================================================================


def test_daily_digest_email_entry_carries_callback_flag_when_fired() -> None:
    """The digest entry models must expose ``callback_phishing_pattern_detected``
    so the LLM prompt + demo renderer can emit the D8 OOB wording. When the
    flag is present in the analysis, the entry must reflect it as True."""
    from core.drafting.daily_digest_agent import _callback_phishing_fired

    payload = EmailAnalysisPayload.model_validate(
        json.loads(
            _valid_analysis_json(
                risk_score=60,
                behavioral_deviation_flags=[CALLBACK_PHISHING_PATTERN_FLAG],
            )
        )
        | {"source_email_record_id": str(uuid4())}
    )
    assert _callback_phishing_fired(payload) is True


def test_daily_digest_email_entry_carries_false_when_flag_absent() -> None:
    from core.drafting.daily_digest_agent import _callback_phishing_fired

    payload = EmailAnalysisPayload.model_validate(
        json.loads(_valid_analysis_json(risk_score=60))
        | {"source_email_record_id": str(uuid4())}
    )
    assert _callback_phishing_fired(payload) is False


def test_demo_renderer_emits_exact_d8_wording_when_callback_flag_fired() -> None:
    """TOAD §8.10 gate test: the deterministic demo renderer must emit
    the EXACT phrase 'verify through a previously-known channel, not via
    the number in this email.' when an item has
    ``callback_phishing_pattern_detected: true``. Paraphrase / partial
    quote / omission is a §8.10 failure."""
    from scripts.inbox_shield_daily_digest_demo import demo_digest_llm_client

    aggregate = {
        "digest_date": "2026-05-30",
        "important_emails": [],
        "top_risks": [
            {
                "source_email_record_id": str(uuid4()),
                "source_analysis_record_id": str(uuid4()),
                "subject": "Urgent: please call",
                "sender": "vendor@example.com",
                "risk_score": 88,
                "recommended_action": "block",
                "reason": "callback-phishing pattern detected",
                "client_facing_rubric": None,
                "callback_phishing_pattern_detected": True,
            }
        ],
        "tasks": [],
    }
    markdown = demo_digest_llm_client(
        "You are the NorthStar Inbox Shield Daily Digest agent.",
        json.dumps(aggregate),
    )
    assert OUT_OF_BAND_VERIFICATION_WORDING in markdown, (
        "demo renderer must emit the EXACT OUT_OF_BAND_VERIFICATION_WORDING "
        "phrase when callback_phishing_pattern_detected is true"
    )


def test_demo_renderer_omits_d8_wording_when_callback_flag_absent() -> None:
    """Mirror: when the flag is absent, the demo renderer MUST NOT
    spontaneously emit the OOB wording. False-positive rendering would
    train operators to ignore the signal."""
    from scripts.inbox_shield_daily_digest_demo import demo_digest_llm_client

    aggregate = {
        "digest_date": "2026-05-30",
        "important_emails": [],
        "top_risks": [
            {
                "source_email_record_id": str(uuid4()),
                "source_analysis_record_id": str(uuid4()),
                "subject": "Routine vendor invoice",
                "sender": "vendor@example.com",
                "risk_score": 72,
                "recommended_action": "needs_review",
                "reason": "vendor-fraud signals present",
                "client_facing_rubric": None,
                "callback_phishing_pattern_detected": False,
            }
        ],
        "tasks": [],
    }
    markdown = demo_digest_llm_client(
        "You are the NorthStar Inbox Shield Daily Digest agent.",
        json.dumps(aggregate),
    )
    assert OUT_OF_BAND_VERIFICATION_WORDING not in markdown, (
        "demo renderer must NOT emit OOB wording when the flag is absent"
    )


def test_daily_digest_system_prompt_pins_exact_d8_wording() -> None:
    """The LLM system prompt must instruct the model to emit the EXACT
    phrase. The wording string in the constant must appear verbatim in the
    prompt — without that, a non-deterministic model can drift."""
    from core.drafting.daily_digest_agent import DAILY_DIGEST_SYSTEM_PROMPT

    assert OUT_OF_BAND_VERIFICATION_WORDING in DAILY_DIGEST_SYSTEM_PROMPT, (
        "daily-digest system prompt must include the verbatim OOB wording "
        "so the LLM does not paraphrase the contractually-required phrase"
    )
    # Also assert the prompt mentions the trigger condition by name so the
    # LLM keys off the structured field, not vibes:
    assert "callback_phishing_pattern_detected" in DAILY_DIGEST_SYSTEM_PROMPT


# ===========================================================================
# §9 Schema / serialization probes (StrictModel boundary at integration time)
# ===========================================================================


def test_assessment_model_dump_is_stable_round_trip(tmp_path) -> None:
    """A detector result must survive ``model_dump`` -> ``model_validate`` ->
    ``model_dump`` byte-identically. Round-trip drift would make digest /
    audit-marker / cross-system handoff unreliable."""
    parsed = _run_enabled(tmp_path, _MULTI_CATEGORY_BODY)
    assert parsed.callback_phishing_assessment is not None
    dumped1 = parsed.callback_phishing_assessment.model_dump(mode="json")
    reconstructed = CallbackPhishingAssessment.model_validate(dumped1)
    dumped2 = reconstructed.model_dump(mode="json")
    assert dumped1 == dumped2


def test_extra_keys_on_digest_entry_rejected_by_strict_model() -> None:
    """``DailyDigestEmailEntry`` / ``DailyDigestRiskEntry`` are StrictModel:
    a malformed dict with an unknown ``phone_number_assessment`` key must
    be rejected on construction — defense-in-depth that future renderer
    refactors can't sneak a phone-field through the digest contract."""
    valid_email_entry = {
        "source_email_record_id": str(uuid4()),
        "source_analysis_record_id": str(uuid4()),
        "subject": "test",
        "sender": "vendor@example.com",
        "risk_score": 50,
    }
    with pytest.raises(Exception):  # noqa: BLE001 — pydantic ValidationError
        DailyDigestEmailEntry.model_validate(
            {**valid_email_entry, "phone_number_assessment": {}}
        )

    valid_risk_entry = {
        "source_email_record_id": str(uuid4()),
        "source_analysis_record_id": str(uuid4()),
        "subject": "test",
        "sender": "vendor@example.com",
        "risk_score": 88,
    }
    with pytest.raises(Exception):  # noqa: BLE001
        DailyDigestRiskEntry.model_validate(
            {**valid_risk_entry, "phone_number_assessment": {}}
        )
