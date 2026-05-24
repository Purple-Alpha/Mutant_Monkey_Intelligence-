from __future__ import annotations

import pytest

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    Environment,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_audit_verdict, submit_policy_update
from core.orchestrator.routes import blackboard_path
from core.policy import (
    SigningKey,
    default_signing_key,
    run_policy_promotion_cycle,
    sign,
)
from core.production import (
    AlertSubscriberConfig,
    PolicyConsumerConfig,
    ProductionLoopConfig,
    ProductionSignal,
    apply_pending_policies,
    emit_regression_alert,
    find_unconsumed_alerts,
    run_alert_subscriber_cycle,
    run_production_cycle,
)
from core.production_state import load_state, state_path

TENANT = "tenant_demo"
LOW_CONFIDENCE_SIGNAL = ProductionSignal(
    source="mailbox",
    event_kind="email_received",
    subject="Team lunch update",
    sender_domain="client-example.ca",
)


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _policy_applied_audits(route_context: RouteContext) -> list:
    records = read_records(
        blackboard_path(route_context.blackboard_root, Environment.PRODUCTION, TENANT)
    )
    return [
        record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == "policy_applied"
    ]


def _inject_raw_alert(
    route_context: RouteContext,
    *,
    source_agent: str = "audit_001",
    verdict: AuditStatus = AuditStatus.REJECTED,
    target_record_id,
    workflow_id: str = "policy_regression_alert",
):
    return submit_audit_verdict(
        route_context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent=source_agent,
        workflow_id=workflow_id,
        payload=AuditVerdictPayload(
            target_record_id=target_record_id,
            verdict=verdict,
            findings=["injected test alert"],
            requires_human_review=False,
        ),
    )


def _apply_policy_through_full_pipeline(
    route_context: RouteContext, *, policy_name: str, parameters: dict
):
    """Inject, promote, then run one production cycle with the subscriber OFF
    so the consumer applies the new policy without the subscriber firing on
    any unrelated alerts that may have been emitted earlier in the test."""

    key = default_signing_key()
    payload = PolicyUpdatePayload(
        policy_name=policy_name,
        change_summary=f"test policy {policy_name}",
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan="revert",
        parameters=parameters,
    )
    signature_id = sign(payload.model_dump(mode="json"), "governance_001", key)
    submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=payload,
        signature_id=signature_id,
    )
    run_policy_promotion_cycle(route_context)
    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
    )


def test_emit_regression_alert_raises_when_no_policy_was_ever_applied(tmp_path):
    route_context = _context(tmp_path)
    with pytest.raises(ValueError, match="no policy_applied audit"):
        emit_regression_alert(route_context, reason="false positive spike")


def test_emit_regression_alert_targets_most_recent_policy_applied_audit(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    alert_result = emit_regression_alert(
        route_context, reason="false positives spiked", severity="high"
    )
    alert = alert_result.record

    assert alert.workflow_id == "policy_regression_alert"
    assert alert.source_agent == "audit_001"
    assert alert.payload["verdict"] == AuditStatus.REJECTED.value

    production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, TENANT
    )
    records = read_records(production_path)
    policy_applied_audits = [
        record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == "policy_applied"
    ]
    latest = max(policy_applied_audits, key=lambda record: record.created_at)
    assert str(alert.payload["target_record_id"]) == str(latest.record_id)


def test_run_alert_subscriber_with_no_alerts_is_a_no_op(tmp_path):
    route_context = _context(tmp_path)

    result = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert result.scanned == 0
    assert result.triggered == 0
    assert result.skipped == 0
    assert result.items == []


def test_run_alert_subscriber_with_insufficient_history_writes_skip_marker(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    emit_regression_alert(route_context, reason="false positives spiked")

    result = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )

    assert result.scanned == 1
    assert result.triggered == 0
    assert result.skipped == 1
    item = result.items[0]
    assert item.triggered_rollback is False
    assert item.rollback_record_id is None
    assert item.skip_reason == "no previous applied state"

    production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, TENANT
    )
    records = read_records(production_path)
    consumption_markers = [
        record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == "regression_alert_consumed"
    ]
    assert len(consumption_markers) == 1
    assert consumption_markers[0].payload["requires_human_review"] is True

    second_result = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert second_result.scanned == 0


def test_find_unconsumed_alerts_skips_already_consumed_alerts(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    first_alert = emit_regression_alert(route_context, reason="first")
    second_alert = emit_regression_alert(route_context, reason="second")

    run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )

    unconsumed = find_unconsumed_alerts(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert unconsumed == []

    assert first_alert.record.record_id != second_alert.record.record_id


def test_end_to_end_alert_triggers_rollback_and_state_reverts(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )
    assert load_state(state_path(route_context.blackboard_root, TENANT)).parameters == {
        "confidence_boost": 0.20
    }

    emit_regression_alert(
        route_context, reason="post-policy_beta detection regression detected"
    )

    subscriber_result = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert subscriber_result.triggered == 1
    item = subscriber_result.items[0]
    assert item.rollback_record_id is not None

    promotion = run_policy_promotion_cycle(route_context)
    assert promotion.promoted_count == 1

    apply_result = apply_pending_policies(
        route_context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
    )
    assert apply_result.applied_count == 1

    state = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state.active_version == "policy_alpha"
    assert state.parameters == {"confidence_boost": 0.10}


def test_production_loop_runs_subscriber_at_end_of_cycle_by_default(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    emit_regression_alert(route_context, reason="loop wiring test")

    result = run_production_cycle(
        route_context, tenant_id=TENANT, signal=LOW_CONFIDENCE_SIGNAL
    )

    assert result.alert_subscriber is not None
    assert result.alert_subscriber.scanned == 1
    assert result.alert_subscriber.triggered == 1

    second_result = run_production_cycle(
        route_context, tenant_id=TENANT, signal=LOW_CONFIDENCE_SIGNAL
    )
    assert second_result.alert_subscriber is not None
    assert second_result.alert_subscriber.scanned == 0


def test_production_loop_does_not_run_subscriber_when_disabled(tmp_path):
    route_context = _context(tmp_path)

    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )
    emit_regression_alert(route_context, reason="should not be processed by loop")

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
    )
    assert result.alert_subscriber is None

    unconsumed = find_unconsumed_alerts(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert len(unconsumed) == 1


def test_subscriber_rejects_alert_from_non_audit_001_source(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )
    latest = max(_policy_applied_audits(route_context), key=lambda record: record.created_at)
    _inject_raw_alert(
        route_context,
        source_agent="governance_001",
        target_record_id=latest.record_id,
    )

    assert find_unconsumed_alerts(route_context) == []

    result = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert result.scanned == 1
    assert result.triggered == 0
    assert result.items[0].skip_reason.startswith("invalid alert source_agent")


def test_subscriber_rejects_alert_with_non_rejected_verdict(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )
    latest = max(_policy_applied_audits(route_context), key=lambda record: record.created_at)
    _inject_raw_alert(
        route_context,
        verdict=AuditStatus.APPROVED,
        target_record_id=latest.record_id,
    )

    assert find_unconsumed_alerts(route_context) == []

    result = run_alert_subscriber_cycle(route_context)
    assert result.triggered == 0
    assert "invalid alert verdict" in (result.items[0].skip_reason or "")


def test_subscriber_rejects_alert_targeting_non_policy_applied_record(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    cycle = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
    )
    _inject_raw_alert(
        route_context,
        target_record_id=cycle.ingest.record.record_id,
    )

    result = run_alert_subscriber_cycle(route_context)
    assert result.triggered == 0
    assert result.items[0].skip_reason == "alert target is not a policy_applied audit"


def test_subscriber_rejects_stale_policy_applied_target(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    applied = sorted(_policy_applied_audits(route_context), key=lambda record: record.created_at)
    stale_target = applied[0]
    _inject_raw_alert(route_context, target_record_id=stale_target.record_id)

    result = run_alert_subscriber_cycle(route_context)
    assert result.triggered == 0
    assert result.items[0].skip_reason == "stale policy_applied target (not most recent apply)"

    state = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state.active_version == "policy_beta"


def test_production_loop_passes_custom_alert_subscriber_config(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    custom_key = SigningKey(secret=b"custom-subscriber-signing-key-32b!")
    custom_config = AlertSubscriberConfig(
        production_tenant_id=TENANT,
        sandbox_tenant_id="sandbox_default",
        signing_key=custom_key,
    )
    emit_regression_alert(route_context, reason="custom config path")

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(alert_subscriber_config=custom_config),
    )

    assert result.alert_subscriber is not None
    assert result.alert_subscriber.triggered == 1

    sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, "sandbox_default"
    )
    sandbox_records = read_records(sandbox_path)
    rollback_updates = [
        record
        for record in sandbox_records
        if record.record_type == RecordType.POLICY_UPDATE
        and record.payload.get("is_rollback") is True
    ]
    assert len(rollback_updates) == 1
    assert rollback_updates[0].audit.signature_id is not None
