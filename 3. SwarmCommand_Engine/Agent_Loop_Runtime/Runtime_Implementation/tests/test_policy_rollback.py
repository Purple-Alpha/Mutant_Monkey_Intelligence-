from __future__ import annotations

from core.blackboard import (
    Environment,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_policy_update
from core.orchestrator.routes import blackboard_path
from core.policy import (
    SigningKey,
    applied_state_history,
    default_signing_key,
    request_rollback_to_previous,
    run_policy_promotion_cycle,
    sign,
    sign_rollback_request,
)
from core.production import (
    ProductionLoopConfig,
    ProductionSignal,
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


def _inject_signed_policy(
    route_context: RouteContext,
    *,
    policy_name: str,
    parameters: dict,
    is_rollback: bool = False,
    signing_key: SigningKey | None = None,
):
    """Inject a directly-signed sandbox policy_update so the promotion pipeline
    can pick it up. Lets us drive forward-applies and rollback targets in tests
    without dragging the mutation engine in."""
    key = signing_key or default_signing_key()
    payload = PolicyUpdatePayload(
        policy_name=policy_name,
        change_summary=f"test policy {policy_name}",
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan="revert",
        parameters=parameters,
        is_rollback=is_rollback,
    )
    signature_id = sign(payload.model_dump(mode="json"), "governance_001", key)
    return submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=payload,
        signature_id=signature_id,
    )


def _apply_signed_policy_through_full_pipeline(
    route_context: RouteContext, *, policy_name: str, parameters: dict
):
    """Inject, promote, and let the next production cycle consume the new policy."""
    _inject_signed_policy(route_context, policy_name=policy_name, parameters=parameters)
    run_policy_promotion_cycle(route_context)
    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(),
    )


def test_sign_rollback_request_produces_signed_sandbox_record_with_is_rollback_true(tmp_path):
    route_context = _context(tmp_path)

    result = sign_rollback_request(
        route_context,
        target_policy_name="policy_alpha",
        target_parameters={"confidence_boost": 0.10},
        alert_reason="manual test",
    )

    record = result.record
    assert record.record_type == RecordType.POLICY_UPDATE
    assert record.audit.signed is True
    payload = PolicyUpdatePayload.model_validate(record.payload)
    assert payload.is_rollback is True
    assert payload.policy_name == "policy_alpha"
    assert payload.parameters == {"confidence_boost": 0.10}


def test_applied_state_history_returns_states_in_chronological_order(tmp_path):
    route_context = _context(tmp_path)

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    history = applied_state_history(route_context, production_tenant_id=TENANT)
    assert [state.policy_name for state in history] == ["policy_alpha", "policy_beta"]
    assert [state.parameters for state in history] == [
        {"confidence_boost": 0.10},
        {"confidence_boost": 0.20},
    ]


def test_request_rollback_to_previous_returns_none_when_history_too_short(tmp_path):
    route_context = _context(tmp_path)

    none_zero = request_rollback_to_previous(
        route_context, production_tenant_id=TENANT, alert_reason="x"
    )
    assert none_zero is None

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    none_one = request_rollback_to_previous(
        route_context, production_tenant_id=TENANT, alert_reason="x"
    )
    assert none_one is None


def test_rollback_target_not_in_history_is_rejected_at_promotion_boundary(tmp_path):
    route_context = _context(tmp_path)

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )

    _inject_signed_policy(
        route_context,
        policy_name="never_was_applied",
        parameters={"confidence_boost": 0.99},
        is_rollback=True,
    )
    promotion = run_policy_promotion_cycle(route_context)
    assert promotion.promoted_count == 0
    assert promotion.rejected_count == 1
    assert promotion.item_results[-1].sandbox_rejection_audit is not None
    assert promotion.item_results[-1].production_workflow_trigger is None

    state = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state.active_version == "policy_alpha"
    assert state.parameters == {"confidence_boost": 0.10}


def test_end_to_end_rollback_returns_state_to_previously_applied_policy(tmp_path):
    route_context = _context(tmp_path)

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    assert load_state(state_path(route_context.blackboard_root, TENANT)).parameters == {
        "confidence_boost": 0.10
    }

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )
    assert load_state(state_path(route_context.blackboard_root, TENANT)).parameters == {
        "confidence_boost": 0.20
    }

    rollback = request_rollback_to_previous(
        route_context,
        production_tenant_id=TENANT,
        alert_reason="integration test: regression after policy_beta",
    )
    assert rollback is not None
    rollback_payload = PolicyUpdatePayload.model_validate(rollback.record.payload)
    assert rollback_payload.is_rollback is True
    assert rollback_payload.policy_name == "policy_alpha"
    assert rollback_payload.parameters == {"confidence_boost": 0.10}

    run_policy_promotion_cycle(route_context)
    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
    )

    state = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state.active_version == "policy_alpha"
    assert state.parameters == {"confidence_boost": 0.10}

    history = applied_state_history(route_context, production_tenant_id=TENANT)
    assert [s.policy_name for s in history] == ["policy_alpha", "policy_beta", "policy_alpha"]


def test_rollback_request_with_wrong_signing_key_fails_promotion(tmp_path):
    """A forged rollback never reaches the gate because the promotion pipeline
    rejects the bogus signature first."""
    route_context = _context(tmp_path)

    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )

    wrong_key = SigningKey(secret=b"impostor-key-of-sufficient-length-bytes")
    sign_rollback_request(
        route_context,
        target_policy_name="policy_alpha",
        target_parameters={"confidence_boost": 0.10},
        alert_reason="should be rejected",
        signing_key=wrong_key,
    )

    promotion = run_policy_promotion_cycle(route_context)
    assert promotion.promoted_count == 0
    assert promotion.rejected_count == 1

    sandbox_path = blackboard_path(
        route_context.blackboard_root,
        Environment.SANDBOX,
        "sandbox_default",
    )
    sandbox_records = read_records(sandbox_path)
    rejection_audits = [
        record
        for record in sandbox_records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.payload["verdict"] == "rejected"
    ]
    assert any(audit.workflow_id == "policy_promotion" for audit in rejection_audits)
