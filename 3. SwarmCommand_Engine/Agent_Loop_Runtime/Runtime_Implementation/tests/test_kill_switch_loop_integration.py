"""Loop-level integration tests for the operator kill switch.

Each loop entry point listed in ``Policy_Pipeline/operator-kill-switch.md``
gets at least one explicit test that the cycle refuses to run when the
switch is engaged for its scope. The critical case is ``apply_signed_policy``:
even with a fully valid signed evidence chain, the gate must raise
``KillSwitchEngaged`` and leave ``production_state`` untouched.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    Environment,
    MutantEvaluationPayload,
    RecordType,
    WeaknessReportPayload,
    read_records,
)
from core.drafting import DailyDigestConfig, run_daily_digest_cycle
from core.mutation import run_mutation_cycle
from core.operator_state import (
    KillSwitchEngaged,
    disengage_kill_switch,
    engage_kill_switch,
)
from core.orchestrator import (
    RouteContext,
    submit_email_inbound,
    submit_mutant_evaluation,
    submit_weakness_report,
)
from core.orchestrator.routes import blackboard_path
from core.policy import (
    request_rollback_to_previous,
    run_policy_promotion_cycle,
)
from core.production import (
    AlertSubscriberConfig,
    PolicyConsumerConfig,
    ProductionLoopConfig,
    ProductionSignal,
    RegressionDetectorConfig,
    apply_pending_policies,
    emit_regression_alert,
    run_alert_subscriber_cycle,
    run_production_cycle,
    run_regression_detector_cycle,
)
from core.production_state import (
    ProductionPolicyState,
    apply_signed_policy,
    load_state,
    state_path,
)
from core.sandbox import SandboxLoopConfig, run_sandbox_cycle
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _high_risk_signal() -> ProductionSignal:
    return ProductionSignal(
        source="mailbox",
        event_kind="email_received",
        subject="Urgent invoice payment required",
        sender_domain="unknown-vendor.ru",
    )


def _seed_weakness(context: RouteContext) -> None:
    submit_weakness_report(
        context,
        source_agent="blue_detection_001",
        payload=WeaknessReportPayload(
            weakness_kind="low_confidence_detection",
            anonymized_pattern="financial_lure:sender_domain_present:suspicious",
            confidence_gap=0.47,
        ),
    )


def _seed_signed_promotion(context: RouteContext):
    """Drive sandbox -> sign -> promote so a valid signed evidence chain exists."""

    submit_mutant_evaluation(
        context,
        source_agent="sandbox_mutator_001",
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=uuid4(),
            blue_detected=False,
            baseline_confidence=0.53,
            failure_modes=["missing_signal:unknown_sender_domain"],
            mutation_recommended=True,
        ),
    )
    run_mutation_cycle(context)
    return run_policy_promotion_cycle(context)


def _seed_inbound(
    context: RouteContext,
    *,
    subject: str = "Outstanding invoice",
    sender: str = "vendor@example.com",
):
    from core.blackboard import EmailInboundPayload

    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="ops@northstar.example",
        subject=subject,
        body_plain="Body text.",
    )
    return submit_email_inbound(
        context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )


def _fake_scoring_client(system_prompt: str, user_prompt: str) -> str:
    assert "NorthStar Inbox Shield" in system_prompt
    json.loads(user_prompt)
    return json.dumps(
        {
            "summary": "Vendor email.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 60,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "medium",
                "vendor_fraud_score": 40,
                "wire_transfer_anomaly_score": 30,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 0,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "needs_review",
        }
    )


def _fake_digest_client(system_prompt: str, user_prompt: str) -> str:
    return "# Digest"


# -- run_production_cycle -----------------------------------------------------


def test_run_production_cycle_refuses_when_kill_switch_all_is_engaged(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt all", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged) as excinfo:
        run_production_cycle(
            context, tenant_id=TENANT, signal=_high_risk_signal()
        )
    assert excinfo.value.scope == "ALL"

    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, TENANT
    )
    assert not production_path.exists()


def test_run_production_cycle_refuses_when_kill_switch_production_only_is_engaged(
    tmp_path,
):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root,
        scope="PRODUCTION_ONLY",
        reason="halt prod only",
        operator="matt",
    )

    with pytest.raises(KillSwitchEngaged) as excinfo:
        run_production_cycle(
            context, tenant_id=TENANT, signal=_high_risk_signal()
        )
    assert excinfo.value.scope == "PRODUCTION_ONLY"


def test_run_production_cycle_runs_normally_when_only_sandbox_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root,
        scope="SANDBOX_ONLY",
        reason="halt sandbox only",
        operator="matt",
    )

    result = run_production_cycle(
        context, tenant_id=TENANT, signal=_high_risk_signal()
    )
    assert result.workflow_trigger is not None


# -- run_sandbox_cycle --------------------------------------------------------


@pytest.mark.parametrize("scope", ["ALL", "SANDBOX_ONLY"])
def test_run_sandbox_cycle_refuses_when_sandbox_applicable_scope_is_engaged(
    tmp_path, scope
):
    context = _context(tmp_path)
    _seed_weakness(context)
    engage_kill_switch(
        context.blackboard_root, scope=scope, reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_sandbox_cycle(context=context)


def test_run_sandbox_cycle_runs_normally_when_only_production_is_halted(tmp_path):
    context = _context(tmp_path)
    _seed_weakness(context)
    engage_kill_switch(
        context.blackboard_root,
        scope="PRODUCTION_ONLY",
        reason="halt prod only",
        operator="matt",
    )

    result = run_sandbox_cycle(
        context=context,
        config=SandboxLoopConfig(detection_confidence_threshold=0.99),
    )
    assert result.processed_count == 1


# -- the remaining production-side entry points ------------------------------


def test_run_alert_subscriber_cycle_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_alert_subscriber_cycle(context, config=AlertSubscriberConfig())


def test_run_regression_detector_cycle_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_regression_detector_cycle(
            context, config=RegressionDetectorConfig(production_tenant_id=TENANT)
        )


def test_apply_pending_policies_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        apply_pending_policies(
            context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
        )


def test_run_email_risk_scoring_cycle_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)
    engage_kill_switch(
        context.blackboard_root, scope="PRODUCTION_ONLY", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_email_risk_scoring_cycle(
            context,
            config=EmailRiskScoringConfig(
                llm_client=_fake_scoring_client,
                production_tenant_id=TENANT,
            ),
        )


def test_run_daily_digest_cycle_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_daily_digest_cycle(
            context,
            config=DailyDigestConfig(
                llm_client=_fake_digest_client,
                production_tenant_id=TENANT,
            ),
        )


def test_request_rollback_to_previous_refuses_when_production_is_halted(tmp_path):
    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        request_rollback_to_previous(
            context, production_tenant_id=TENANT, alert_reason="post-halt rollback"
        )


# -- apply_signed_policy is the outermost gate -------------------------------


def test_apply_signed_policy_refuses_even_with_valid_signed_chain_when_halted(
    tmp_path,
):
    """The critical case: even a perfect signed evidence chain cannot
    mutate production_state while the production kill switch is engaged.
    """

    context = _context(tmp_path)
    promotion = _seed_signed_promotion(context)
    workflow_trigger_id = promotion.item_results[
        0
    ].production_workflow_trigger.record.record_id

    production_state_path = state_path(context.blackboard_root, TENANT)
    assert not production_state_path.exists()
    state_before = load_state(production_state_path)
    assert state_before == ProductionPolicyState()

    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged) as excinfo:
        apply_signed_policy(
            blackboard_root=context.blackboard_root,
            workflow_trigger_id=workflow_trigger_id,
        )
    assert excinfo.value.scope == "ALL"

    assert not production_state_path.exists()
    assert load_state(production_state_path) == ProductionPolicyState()


def test_apply_signed_policy_runs_normally_after_disengage(tmp_path):
    """A halt is reversible. After disengage, the same signed chain promotes
    cleanly through the gate.
    """

    context = _context(tmp_path)
    promotion = _seed_signed_promotion(context)
    workflow_trigger_id = promotion.item_results[
        0
    ].production_workflow_trigger.record.record_id

    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="halt", operator="matt"
    )
    with pytest.raises(KillSwitchEngaged):
        apply_signed_policy(
            blackboard_root=context.blackboard_root,
            workflow_trigger_id=workflow_trigger_id,
        )

    disengage_kill_switch(
        context.blackboard_root, reason="resume", operator="matt"
    )

    result = apply_signed_policy(
        blackboard_root=context.blackboard_root,
        workflow_trigger_id=workflow_trigger_id,
    )
    assert result.changed is True
    assert result.new_state.active_version != "v0"


# -- default (no switch file on disk) ----------------------------------------


def test_no_kill_switch_file_means_every_loop_runs_normally(tmp_path):
    """Pin the default behaviour: with no operator_state file on disk, every
    loop runs normally and no ``KillSwitchEngaged`` is ever raised.
    """

    context = _context(tmp_path)
    operator_state_dir = context.blackboard_root / "operator_state"
    assert not operator_state_dir.exists()

    _seed_weakness(context)
    sandbox_result = run_sandbox_cycle(
        context=context,
        config=SandboxLoopConfig(detection_confidence_threshold=0.99),
    )
    assert sandbox_result.processed_count == 1

    cycle = run_production_cycle(
        context, tenant_id=TENANT, signal=_high_risk_signal()
    )
    assert cycle.workflow_trigger is not None

    apply_pending_policies(
        context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
    )
    run_regression_detector_cycle(
        context, config=RegressionDetectorConfig(production_tenant_id=TENANT)
    )
    run_alert_subscriber_cycle(context, config=AlertSubscriberConfig())

    _seed_inbound(context)
    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_fake_scoring_client, production_tenant_id=TENANT
        ),
    )
    assert scoring_result.analyzed + scoring_result.failed >= 1

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_fake_digest_client, production_tenant_id=TENANT
        ),
    )
    assert digest_result.digest_record_id is not None or digest_result.skipped_reason

    assert not operator_state_dir.exists()
