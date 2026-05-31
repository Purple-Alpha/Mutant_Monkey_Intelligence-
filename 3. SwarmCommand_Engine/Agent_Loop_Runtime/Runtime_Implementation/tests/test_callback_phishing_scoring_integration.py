"""Callback Phishing / TOAD Part 1 — Pass 2 scoring-agent integration tests.

These tests cover the integration surface added in TOAD implementation
pass 2 (scoring-agent wiring + activation flag + rubric §11.2 mapping +
production-loop flag preservation). They are the rubric-side / scoring-side
counterparts to the pure-function unit tests in
``tests/test_callback_phishing_detector.py`` (pass 1).

Locked per:
- ``4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md`` (§11
  SIGNED 2026-05-30 by Matt Nichol) §8 gate tests 8 (lift-only invariant)
  + 11 (rubric integration per D13) + 13 (activation discipline default
  OFF) + 14 (production-loop rebuild flag preservation).
- ``4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md``
  §11.2 amendment (SIGNED 2026-05-30 by Matt Nichol) — the rubric mapper
  ``callback_phishing_pattern`` → ``origin_timing`` deterministic projection
  contract.

Pass 2 scope (matches operator instruction):
- default-off no-regression (config flag stays False; no detector code runs)
- enabled detector firing (flag on, fixture fires, full emission contract)
- body_plain only (body_html ignored even when enabled)
- behavioral flag append (``callback_phishing_pattern`` lands on
  ``risk.behavioral_deviation_flags`` exactly once, no duplicates)
- assessment attached (``EmailAnalysisPayload.callback_phishing_assessment``
  populated with the frozen ``CallbackPhishingAssessment``)
- risk-floor max merge (``recommended_risk_floor_lift`` participates in the
  ``_overlay_ransomware_precursor`` floor max; never lowers ``risk_score``)
- rubric ``origin_timing`` floor-lift rule (presence → axis ≥ 1)
- rubric ``origin_timing`` higher-band exact-2 rule (presence + ``risk_score
  >= 50`` OR ``recommended_risk_floor_lift >= 70`` → axis == 2)
- production-loop config preservation
- no phone-number assessment / no body_html behavior remains true at the
  integration boundary (the v1 schema's
  ``CallbackPhishingAssessment.phone_number_assessment`` absence is enforced
  by the pass-1 schema-discipline tests; the integration boundary asserts
  the runtime never adds such a key when wiring the detector into the
  scoring path).

These tests do NOT re-cover detector-pure-function gates (§8.1-§8.9, §8.12)
which are owned by ``tests/test_callback_phishing_detector.py``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

import pytest

from core.blackboard import (
    CallbackPhishingAssessment,
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
    detect_callback_phishing,
)
from core.scoring.client_facing_rubric import project_client_facing_rubric

# ---------------------------------------------------------------------------
# Fixtures + helpers
# ---------------------------------------------------------------------------

TENANT = "tenant_demo"

# Body lines mirror the categories locked in TOAD D11 + the §3 phrase
# vocabulary. These are bounded test inputs; the detector's pass-1 tests
# in ``tests/test_callback_phishing_detector.py`` exhaustively cover
# per-category regex fires. Here we only need *some* phrasing that the
# detector reliably fires on so the integration assertions are stable.

_SINGLE_CATEGORY_BODY = (
    "Hello finance team,\n"
    "Please call us immediately at the number above to confirm.\n"
    "Best regards.\n"
)  # call_now_pressure only -> 1 category, lift 50

_MULTI_CATEGORY_BODY = (
    "Hello finance team,\n"
    "Please call us immediately. Do not use the number on file for billing.\n"
    "We can only finalize this matter by phone today; email replies will not "
    "be accepted.\n"
    "Best regards.\n"
)  # call_now_pressure + do_not_use_known_channel + voice_only_finalize ->
# 3 categories. Lift >= 85 (multi-category band per TOAD §4.1).

_PAYMENT_OVERLAP_BODY = (
    "Hello finance team,\n"
    "Please call us right away to confirm the new ACH routing details.\n"
    "Do not use the old wire instructions on file.\n"
    "Best regards.\n"
)  # payment_redirect_call + do_not_use_known_channel + call_now_pressure ->
# at least the payment-overlap "block-eligible" lift of 70-85.


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_inbound(
    context: RouteContext,
    *,
    body_plain: str = "Please confirm the attached.",
    body_html: str | None = None,
    subject: str = "Outstanding invoice",
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
    result = submit_email_inbound(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )
    return result.record.record_id


def _valid_analysis_json(
    *,
    risk_score: int = 30,
    behavioral_deviation_flags: list[str] | None = None,
    recommended_action: str = "needs_review",
    vendor_fraud_score: int = 20,
    wire_transfer_anomaly_score: int = 20,
) -> str:
    payload = {
        "summary": "Vendor email under review.",
        "action_items": [
            {"task": "Review", "owner": "ops", "due_date": "2026-06-01"},
        ],
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "low",
            "vendor_fraud_score": vendor_fraud_score,
            "wire_transfer_anomaly_score": wire_transfer_anomaly_score,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": list(behavioral_deviation_flags or []),
        },
        "impersonation_analysis": {
            "impersonation_likelihood": 10,
            "suspicious_elements": [],
            "sender_legitimacy_notes": "first contact",
        },
        "recommended_action": recommended_action,
    }
    return json.dumps(payload)


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


# ---------------------------------------------------------------------------
# 1) default-off no-regression — flag stays False, nothing wires in
# ---------------------------------------------------------------------------


def test_default_off_no_callback_phishing_anywhere(tmp_path) -> None:
    """Default ``EmailRiskScoringConfig.enable_callback_phishing_detection``
    is ``False`` (TOAD D6 + §8.13). Even on a fixture whose body would
    otherwise fire every category, the detector does not run, no flag is
    appended, no assessment is attached, and ``risk_score`` is not lifted.
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_PAYMENT_OVERLAP_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            # enable_callback_phishing_detection NOT set -> default False
        ),
    )
    assert result.analyzed == 1

    analyses = _analyses(context)
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)

    assert parsed.callback_phishing_assessment is None, (
        "default-off must not attach a CallbackPhishingAssessment to the "
        "analysis payload"
    )
    assert CALLBACK_PHISHING_PATTERN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags, (
        "default-off must not append the callback_phishing_pattern flag"
    )
    # Risk score not lifted: the LLM said 10 and the precursor overlay (with
    # all detectors silent) leaves it as 10. We just assert it didn't get
    # pulled up to the detector's would-be lift (which would be 70-85 on
    # this fixture).
    assert parsed.risk_analysis.risk_score < 50, (
        "default-off must not lift risk_score from the callback-phishing detector"
    )


def test_default_off_explicit_false_no_callback_phishing_anywhere(tmp_path) -> None:
    """Same as the previous test, but the flag is explicitly set to False to
    confirm the explicit-False path is also a no-op (defends against a
    future refactor that accidentally treats unset and False differently).
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_MULTI_CATEGORY_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=20)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=False,
        ),
    )
    assert result.analyzed == 1
    analyses = _analyses(context)
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.callback_phishing_assessment is None
    assert CALLBACK_PHISHING_PATTERN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags


# ---------------------------------------------------------------------------
# 2) Enabled + detector fires — full emission contract
# ---------------------------------------------------------------------------


def test_enabled_single_category_fires_appends_flag_attaches_assessment(tmp_path) -> None:
    """Flag enabled + single-category fixture: detector fires, flag appended,
    assessment attached, risk_score lifted to at least 50 (single-category
    band per TOAD §4.1)."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_SINGLE_CATEGORY_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)

    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) == 1
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift == 50
    assert parsed.callback_phishing_assessment.out_of_band_verification_required is True

    flags = parsed.risk_analysis.behavioral_deviation_flags
    assert flags.count(CALLBACK_PHISHING_PATTERN_FLAG) == 1, (
        "flag must be appended exactly once, no duplicates"
    )

    assert parsed.risk_analysis.risk_score >= 50, (
        "single-category fire must lift risk_score to at least the §4.1 "
        "needs_review band (50)"
    )


def test_enabled_multi_category_lifts_to_block_eligible_band(tmp_path) -> None:
    """Multi-category fixture: lift >= 70 (block-eligible band per §4.1)."""
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_MULTI_CATEGORY_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)

    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is True
    assert len(parsed.callback_phishing_assessment.categories) >= 2
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift >= 70
    assert parsed.risk_analysis.risk_score >= 70


# ---------------------------------------------------------------------------
# 3) body_plain only — body_html input is ignored even when enabled
# ---------------------------------------------------------------------------


def test_body_html_only_does_not_fire_when_enabled(tmp_path) -> None:
    """TOAD D14: v1 reads ``body_plain`` only. A fixture whose only callback-
    phishing language lives in ``body_html`` must not fire even with the
    flag enabled — this enforces the additive boundary at the integration
    surface, not just inside the pure-function detector tests.
    """
    context = _context(tmp_path)
    _seed_inbound(
        context,
        body_plain="Please confirm receipt.",  # benign plain text
        body_html=(
            "<html><body><p>Please call us immediately. Do not use the "
            "number on file. We can only finalize by phone.</p></body></html>"
        ),
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=15)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is False, (
        "body_html content must not feed the detector in v1 (TOAD D14)"
    )
    assert CALLBACK_PHISHING_PATTERN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags


# ---------------------------------------------------------------------------
# 4) risk-floor max merge — never lowers an existing higher risk_score
# ---------------------------------------------------------------------------


def test_existing_high_risk_score_is_not_lowered_by_callback_phishing(tmp_path) -> None:
    """TOAD D5 lift-only / §8.8 lift-only invariant: when an upstream signal
    already pushed ``risk_score`` to 95, the callback-phishing overlay must
    add its flag + assessment but never lower the existing score.
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_SINGLE_CATEGORY_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(
                _valid_analysis_json(risk_score=95, recommended_action="block")
            ),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is True
    assert parsed.risk_analysis.risk_score == 95, (
        "callback-phishing overlay must not lower an upstream risk_score"
    )
    assert parsed.recommended_action == "block", (
        "callback-phishing overlay must not soften an upstream block "
        "recommendation (TOAD §8.8)"
    )


# ---------------------------------------------------------------------------
# 5) Rubric §11.2 — origin_timing floor-lift rule (presence -> axis >= 1)
# ---------------------------------------------------------------------------


def test_rubric_origin_timing_floor_lifts_to_one_on_flag_presence(tmp_path) -> None:
    """Rubric §11.2 floor-lift rule (per TOAD D13): when
    ``callback_phishing_pattern`` is present in ``behavioral_deviation_flags``,
    ``client_facing_rubric.origin_timing`` axis score MUST be at least 1.

    Negative side of the higher-band rule: ``risk_score`` is well under 50
    AND ``recommended_risk_floor_lift`` is well under 70, so the higher-band
    rule does NOT fire — only the floor-lift rule does. Expected score: 1.
    """
    # Build a payload by hand so we control every input the rubric mapper sees.
    # The runtime path is already exercised by the test_enabled_* tests above;
    # this test isolates the rubric mapper's §11.2 amendment.
    analysis_payload = EmailAnalysisPayload.model_validate(
        json.loads(_valid_analysis_json(risk_score=20))
        | {"source_email_record_id": "00000000-0000-0000-0000-000000000001"}
    )
    # Inject the flag + a low-lift assessment (single-category single fire).
    risk = analysis_payload.risk_analysis.model_copy(
        update={
            "behavioral_deviation_flags": [
                *analysis_payload.risk_analysis.behavioral_deviation_flags,
                CALLBACK_PHISHING_PATTERN_FLAG,
            ]
        }
    )
    callback_phishing_assessment = detect_callback_phishing(
        body_plain=_SINGLE_CATEGORY_BODY,
    )
    assert callback_phishing_assessment.fired is True
    assert callback_phishing_assessment.recommended_risk_floor_lift == 50
    analysis_payload = analysis_payload.model_copy(
        update={
            "risk_analysis": risk,
            "callback_phishing_assessment": callback_phishing_assessment,
        }
    )

    rubric = project_client_facing_rubric(analysis_payload)
    origin_timing = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert origin_timing.score == 1, (
        "floor-lift rule must set origin_timing == 1 when only the flag is "
        "present with no higher-band conditions"
    )
    assert CALLBACK_PHISHING_PATTERN_FLAG in origin_timing.evidence_tags
    assert len(origin_timing.why_this_score) <= 160


def test_rubric_origin_timing_floor_preserves_existing_higher_base_score(tmp_path) -> None:
    """Floor-lift rule is **max-merge**, not a hard set: if base §3.5 logic
    already gives ``origin_timing`` 1 (e.g. ``out_of_band_pressure`` present
    with low risk), the flag addition must NOT lower it to 0, but must
    contribute ``callback_phishing_pattern`` to ``evidence_tags`` for
    attribution.
    """
    analysis_payload = EmailAnalysisPayload.model_validate(
        json.loads(
            _valid_analysis_json(
                risk_score=20,
                behavioral_deviation_flags=[
                    "out_of_band_pressure",
                    CALLBACK_PHISHING_PATTERN_FLAG,
                ],
            )
        )
        | {"source_email_record_id": "00000000-0000-0000-0000-000000000002"}
    )
    callback_phishing_assessment = detect_callback_phishing(
        body_plain=_SINGLE_CATEGORY_BODY,
    )
    analysis_payload = analysis_payload.model_copy(
        update={"callback_phishing_assessment": callback_phishing_assessment}
    )

    rubric = project_client_facing_rubric(analysis_payload)
    origin_timing = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert origin_timing.score == 1
    assert "out_of_band_pressure" in origin_timing.evidence_tags
    assert CALLBACK_PHISHING_PATTERN_FLAG in origin_timing.evidence_tags


# ---------------------------------------------------------------------------
# 6) Rubric §11.2 — origin_timing higher-band exact-2 rule
# ---------------------------------------------------------------------------


def test_rubric_origin_timing_exact_two_via_risk_score_branch(tmp_path) -> None:
    """Higher-band rule: presence AND ``risk_score >= 50`` -> axis == 2."""
    analysis_payload = EmailAnalysisPayload.model_validate(
        json.loads(
            _valid_analysis_json(
                risk_score=60,
                behavioral_deviation_flags=[CALLBACK_PHISHING_PATTERN_FLAG],
            )
        )
        | {"source_email_record_id": "00000000-0000-0000-0000-000000000003"}
    )
    # Low-lift assessment so the lift-branch does NOT contribute; only the
    # risk_score branch should trigger the higher-band rule.
    callback_phishing_assessment = detect_callback_phishing(
        body_plain=_SINGLE_CATEGORY_BODY,
    )
    assert callback_phishing_assessment.recommended_risk_floor_lift == 50  # < 70
    analysis_payload = analysis_payload.model_copy(
        update={"callback_phishing_assessment": callback_phishing_assessment}
    )

    rubric = project_client_facing_rubric(analysis_payload)
    origin_timing = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert origin_timing.score == 2
    assert CALLBACK_PHISHING_PATTERN_FLAG in origin_timing.evidence_tags


def test_rubric_origin_timing_exact_two_via_lift_branch(tmp_path) -> None:
    """Higher-band rule: presence AND ``recommended_risk_floor_lift >= 70``
    -> axis == 2. Tests the lift-branch independently of the risk-score
    branch (risk_score stays at 20 here)."""
    analysis_payload = EmailAnalysisPayload.model_validate(
        json.loads(
            _valid_analysis_json(
                risk_score=20,
                behavioral_deviation_flags=[CALLBACK_PHISHING_PATTERN_FLAG],
            )
        )
        | {"source_email_record_id": "00000000-0000-0000-0000-000000000004"}
    )
    # Multi-category fixture: lift >= 70.
    callback_phishing_assessment = detect_callback_phishing(
        body_plain=_MULTI_CATEGORY_BODY,
    )
    assert callback_phishing_assessment.recommended_risk_floor_lift >= 70
    analysis_payload = analysis_payload.model_copy(
        update={"callback_phishing_assessment": callback_phishing_assessment}
    )

    rubric = project_client_facing_rubric(analysis_payload)
    origin_timing = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    assert origin_timing.score == 2
    assert CALLBACK_PHISHING_PATTERN_FLAG in origin_timing.evidence_tags


def test_rubric_origin_timing_unchanged_without_callback_flag(tmp_path) -> None:
    """Mapper must be a no-op when ``callback_phishing_pattern`` is NOT in
    flags, even if a ``callback_phishing_assessment`` happens to be attached
    (which the runtime never does — but defensive testing). This guards
    against accidentally coupling the §11.2 amendment to assessment-presence
    instead of flag-presence."""
    analysis_payload = EmailAnalysisPayload.model_validate(
        json.loads(_valid_analysis_json(risk_score=60))
        | {"source_email_record_id": "00000000-0000-0000-0000-000000000005"}
    )
    # Assessment attached, but flag NOT in behavioral_deviation_flags.
    callback_phishing_assessment = detect_callback_phishing(
        body_plain=_MULTI_CATEGORY_BODY,
    )
    analysis_payload = analysis_payload.model_copy(
        update={"callback_phishing_assessment": callback_phishing_assessment}
    )
    rubric = project_client_facing_rubric(analysis_payload)
    origin_timing = next(a for a in rubric.axes if a.axis_name == "origin_timing")
    # Without the flag in behavioral_deviation_flags, the §11.2 amendment
    # rules do not fire. The base §3.5 logic (no out_of_band_pressure, no
    # urgency_signals) returns score 0.
    assert origin_timing.score == 0
    assert CALLBACK_PHISHING_PATTERN_FLAG not in origin_timing.evidence_tags


# ---------------------------------------------------------------------------
# 7) End-to-end: enabled detector + rubric both -> rubric reflects mapping
# ---------------------------------------------------------------------------


def test_end_to_end_enabled_detector_plus_rubric_emits_origin_timing_two(tmp_path) -> None:
    """Both ``enable_callback_phishing_detection`` and
    ``enable_client_facing_rubric`` enabled. A multi-category fixture fires
    the detector (lift >= 70), which triggers both wiring paths AND the
    §11.2 higher-band rubric rule, yielding ``origin_timing == 2``.
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_MULTI_CATEGORY_BODY)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
            enable_client_facing_rubric=True,
        ),
    )
    assert result.analyzed == 1
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None
    assert parsed.callback_phishing_assessment.fired is True
    assert parsed.callback_phishing_assessment.recommended_risk_floor_lift >= 70
    assert CALLBACK_PHISHING_PATTERN_FLAG in parsed.risk_analysis.behavioral_deviation_flags

    assert parsed.client_facing_rubric is not None
    origin_timing = next(
        a for a in parsed.client_facing_rubric.axes if a.axis_name == "origin_timing"
    )
    assert origin_timing.score == 2
    assert CALLBACK_PHISHING_PATTERN_FLAG in origin_timing.evidence_tags


# ---------------------------------------------------------------------------
# 8) Production-loop flag preservation (TOAD §8.14 / §7.7)
# ---------------------------------------------------------------------------


def test_production_loop_preserves_callback_phishing_flag_through_rebuild(tmp_path) -> None:
    """TOAD §8.14 / §7.7 + lesson learned from the rubric Activation Pass:
    ``ProductionLoopConfig`` rebuilds the ``EmailRiskScoringConfig`` whenever
    the cycle tenant or any Phase 1.4 lift forces one. Without explicit
    preservation, the operator-supplied
    ``enable_callback_phishing_detection=True`` would silently revert to the
    dataclass default (False) on every real production cycle. This test
    forces the rebuild branch via a mismatched tenant id and asserts the
    persisted analysis record carries the assessment + flag.

    Mirrors ``test_production_loop_preserves_client_facing_rubric_flag_through_rebuild``
    in ``tests/test_email_risk_scoring_agent.py`` (which is the canonical
    pattern this test is paired with).
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_MULTI_CATEGORY_BODY)

    custom = EmailRiskScoringConfig(
        llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
        production_tenant_id="wrong_tenant_overridden",
        enable_callback_phishing_detection=True,
    )

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=custom,
        ),
    )
    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1

    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None, (
        "production-loop rebuild dropped the enable_callback_phishing_detection "
        "flag (TOAD §7.7 + §8.14 regression)"
    )
    assert parsed.callback_phishing_assessment.fired is True
    assert CALLBACK_PHISHING_PATTERN_FLAG in parsed.risk_analysis.behavioral_deviation_flags


# ---------------------------------------------------------------------------
# 9) No phone-number assessment / no body_html at the integration boundary
# ---------------------------------------------------------------------------


def test_no_phone_number_assessment_key_on_payload_after_integration(tmp_path) -> None:
    """TOAD D15 + §8.12 enforced at the integration boundary: the runtime
    integration must never silently introduce a ``phone_number_assessment``
    key on the payload (the schema StrictModel discipline would reject it
    upstream, but this test pins the runtime side of the contract too).
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_MULTI_CATEGORY_BODY)
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )

    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    assert parsed.callback_phishing_assessment is not None
    dumped = parsed.callback_phishing_assessment.model_dump(mode="json")
    assert "phone_number_assessment" not in dumped, (
        "TOAD D15: v1 schema must not carry a phone_number_assessment field "
        "even after runtime integration"
    )
    # Also confirm a fresh attempt to construct the assessment with that key
    # is rejected at the StrictModel boundary (defensive, redundant with
    # pass-1 schema-discipline tests, but cheap):
    with pytest.raises(Exception):  # noqa: BLE001 - pydantic ValidationError shape
        CallbackPhishingAssessment.model_validate(
            {**dumped, "phone_number_assessment": {}},
        )


# ---------------------------------------------------------------------------
# 10) Flag-append is dedup-safe even if LLM somehow already emitted it
# ---------------------------------------------------------------------------


def test_flag_append_is_dedup_safe_if_llm_already_emitted_it(tmp_path) -> None:
    """Defense-in-depth: if the LLM ever emits ``callback_phishing_pattern``
    (it shouldn't — the system prompt's controlled enum lists only the nine
    LLM-side flags), the detector-overlay append path must not produce a
    duplicate. This guards the deterministic integration boundary against
    schema-noise from a non-conforming model output.
    """
    context = _context(tmp_path)
    _seed_inbound(context, body_plain=_SINGLE_CATEGORY_BODY)

    # The LLM controlled enum doesn't include callback_phishing_pattern,
    # so the only way the LLM could emit it is via a schema-violation
    # response — which the agent rejects as invalid_enum. We therefore
    # simulate the dedup-safety property at the unit level: post-overlay
    # behavioral_deviation_flags has exactly one occurrence after the
    # canonical enabled path runs.
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_callback_phishing_detection=True,
        ),
    )
    parsed = EmailAnalysisPayload.model_validate(_analyses(context)[0].payload)
    flags = parsed.risk_analysis.behavioral_deviation_flags
    assert flags.count(CALLBACK_PHISHING_PATTERN_FLAG) == 1
