from __future__ import annotations

from core.blackboard import (
    Environment,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_policy_update
from core.orchestrator.routes import blackboard_path
from core.policy import default_signing_key, run_policy_promotion_cycle, sign
from core.production import (
    AlertSubscriberConfig,
    PolicyConsumerConfig,
    ProductionLoopConfig,
    ProductionSignal,
    RegressionDetectorConfig,
    apply_pending_policies,
    find_unconsumed_alerts,
    run_alert_subscriber_cycle,
    run_production_cycle,
    run_regression_detector_cycle,
)
from core.production_state import load_state, state_path

TENANT = "tenant_demo"
CLEAN_SIGNAL = ProductionSignal(
    source="mailbox",
    event_kind="email_received",
    subject="Team lunch update",
    sender_domain="client-example.ca",
)


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _apply_policy(route_context: RouteContext, *, policy_name: str, parameters: dict) -> None:
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
        signal=CLEAN_SIGNAL,
        config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
    )


def _run_post_apply_samples(route_context: RouteContext, count: int) -> None:
    for _ in range(count):
        run_production_cycle(
            route_context,
            tenant_id=TENANT,
            signal=CLEAN_SIGNAL,
            config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
        )


def _production_records(route_context: RouteContext):
    return read_records(
        blackboard_path(route_context.blackboard_root, Environment.PRODUCTION, TENANT)
    )


def test_detector_no_ops_when_no_policy_has_been_applied(tmp_path):
    route_context = _context(tmp_path)

    result = run_regression_detector_cycle(route_context)

    assert result.evaluated_policy_applied_id is None
    assert result.emitted_alert is None
    assert result.check_marker is None
    assert result.skipped_reason == "no policy_applied audit exists"


def test_detector_waits_for_minimum_post_apply_samples_without_marking_checked(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 2)

    result = run_regression_detector_cycle(route_context)

    assert result.sample_count == 2
    assert result.emitted_alert is None
    assert result.check_marker is None
    assert result.skipped_reason == "insufficient post-apply samples"

    checked_markers = [
        record
        for record in _production_records(route_context)
        if record.workflow_id == "policy_regression_detector_checked"
    ]
    assert checked_markers == []


def test_detector_marks_clean_post_apply_window_without_emitting_alert(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.10},
    )
    _run_post_apply_samples(route_context, 3)

    result = run_regression_detector_cycle(route_context)

    assert result.sample_count == 3
    assert result.alert_like_count == 0
    assert result.alert_ratio == 0.0
    assert result.emitted_alert is None
    assert result.check_marker is not None
    assert result.check_marker.record.payload["verdict"] == "approved"
    assert find_unconsumed_alerts(route_context) == []


def test_detector_emits_one_alert_when_post_apply_alert_ratio_crosses_threshold(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 3)

    result = run_regression_detector_cycle(route_context)

    assert result.sample_count == 3
    assert result.alert_like_count == 3
    assert result.alert_ratio == 1.0
    assert result.emitted_alert is not None
    assert result.check_marker is not None
    assert result.check_marker.record.payload["verdict"] == "rejected"

    alerts = find_unconsumed_alerts(route_context)
    assert len(alerts) == 1
    assert alerts[0].record_id == result.emitted_alert.record.record_id


def test_detector_is_idempotent_after_checked_marker_exists(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 3)

    first = run_regression_detector_cycle(route_context)
    second = run_regression_detector_cycle(route_context)

    assert first.emitted_alert is not None
    assert second.emitted_alert is None
    assert second.check_marker is None
    assert second.skipped_reason == "policy apply already checked"
    assert len(find_unconsumed_alerts(route_context)) == 1


def test_detector_to_subscriber_to_rollback_reverts_state(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.10},
    )
    _apply_policy(
        route_context,
        policy_name="policy_beta",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 3)

    detection = run_regression_detector_cycle(route_context)
    assert detection.emitted_alert is not None

    subscriber = run_alert_subscriber_cycle(
        route_context, config=AlertSubscriberConfig(production_tenant_id=TENANT)
    )
    assert subscriber.triggered == 1

    promotion = run_policy_promotion_cycle(route_context)
    assert promotion.promoted_count == 1

    consumer = apply_pending_policies(
        route_context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
    )
    assert consumer.applied_count == 1

    state = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state.active_version == "policy_alpha"
    assert state.parameters == {"confidence_boost": 0.10}


def test_production_loop_does_not_run_detector_by_default(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 3)

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=CLEAN_SIGNAL,
    )

    assert result.regression_detector is None
    checked = [
        record
        for record in _production_records(route_context)
        if record.workflow_id == "policy_regression_detector_checked"
    ]
    assert checked == []


def test_production_loop_runs_detector_when_opted_in(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.10},
    )
    _apply_policy(
        route_context,
        policy_name="policy_beta",
        parameters={"confidence_boost": 0.50},
    )
    _run_post_apply_samples(route_context, 3)

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=CLEAN_SIGNAL,
        config=ProductionLoopConfig(
            run_alert_subscriber_at_end_of_cycle=False,
            run_regression_detector_at_end_of_cycle=True,
        ),
    )

    assert result.regression_detector is not None
    assert result.regression_detector.emitted_alert is not None
    assert result.regression_detector.check_marker is not None
    assert len(find_unconsumed_alerts(route_context)) == 1


def test_production_loop_passes_custom_regression_detector_config(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.45},
    )
    _run_post_apply_samples(route_context, 3)

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=CLEAN_SIGNAL,
        config=ProductionLoopConfig(
            run_alert_subscriber_at_end_of_cycle=False,
            run_regression_detector_at_end_of_cycle=True,
            regression_detector_config=RegressionDetectorConfig(
                production_tenant_id="wrong_tenant_overridden",
                risk_score_threshold=80,
            ),
        ),
    )

    assert result.regression_detector is not None
    assert result.regression_detector.emitted_alert is not None
    assert result.regression_detector.alert_like_count == result.regression_detector.sample_count
    assert result.regression_detector.sample_count >= 3


def test_production_loop_detector_sees_policy_applied_from_same_cycle(tmp_path):
    """Detector runs after the policy consumer, so a freshly-applied policy
    in the same cycle is the one evaluated."""
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.10},
    )

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=CLEAN_SIGNAL,
        config=ProductionLoopConfig(
            run_alert_subscriber_at_end_of_cycle=False,
            run_regression_detector_at_end_of_cycle=True,
        ),
    )

    assert result.regression_detector is not None
    assert result.regression_detector.evaluated_policy_applied_id is not None
    assert result.regression_detector.skipped_reason == "insufficient post-apply samples"


def test_detector_can_use_risk_score_threshold_when_confidence_is_below_threshold(tmp_path):
    route_context = _context(tmp_path)
    _apply_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.45},
    )
    # Confidence is 0.80, below the 0.85 confidence threshold. Risk score is
    # 80, so lowering the detector's risk threshold to 80 should still flag it.
    _run_post_apply_samples(route_context, 3)

    result = run_regression_detector_cycle(
        route_context,
        config=RegressionDetectorConfig(
            production_tenant_id=TENANT,
            risk_score_threshold=80,
        ),
    )

    assert result.alert_like_count == 3
    assert result.emitted_alert is not None
    assert any(record.record_type == RecordType.AUDIT_VERDICT for record in _production_records(route_context))
