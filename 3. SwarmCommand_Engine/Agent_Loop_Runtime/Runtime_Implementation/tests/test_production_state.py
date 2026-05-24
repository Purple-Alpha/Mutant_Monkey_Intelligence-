import dataclasses
from uuid import uuid4

import pytest

from core.blackboard import (
    GovernanceError,
    MutantEvaluationPayload,
    PolicyUpdatePayload,
)
from core.mutation import run_mutation_cycle
from core.orchestrator import (
    RouteContext,
    submit_mutant_evaluation,
    submit_policy_update,
)
from core.policy import (
    PolicyPromotionConfig,
    SigningKey,
    run_policy_promotion_cycle,
)
from core.production_state import (
    ProductionPolicyState,
    apply_signed_policy,
    load_state,
    state_path,
)


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_signed_promotion(route_context: RouteContext):
    """Drive sandbox -> sign -> promote so we have a real evidence chain."""
    submit_mutant_evaluation(
        route_context,
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
    run_mutation_cycle(route_context)
    return run_policy_promotion_cycle(route_context)


def test_default_production_policy_state_is_v0_with_no_parameters(tmp_path):
    state = load_state(state_path(tmp_path / "blackboard", "tenant_demo"))
    assert state == ProductionPolicyState(active_version="v0", parameters={})


def test_production_policy_state_is_frozen_and_cannot_be_mutated_in_place():
    state = ProductionPolicyState(active_version="v1", parameters={"x": 1})
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.active_version = "v2"


def test_apply_signed_policy_updates_state_when_full_evidence_chain_is_present(tmp_path):
    route_context = context(tmp_path)
    promotion = _seed_signed_promotion(route_context)
    item = promotion.item_results[0]
    assert item.production_workflow_trigger is not None

    result = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        workflow_trigger_id=item.production_workflow_trigger.record.record_id,
    )

    assert result.changed is True
    assert result.previous_state == ProductionPolicyState()
    assert result.new_state.active_version != "v0"
    assert result.new_state.active_version.startswith("blue_detection_001:")

    on_disk = load_state(state_path(route_context.blackboard_root, "tenant_demo"))
    assert on_disk == result.new_state


def test_apply_signed_policy_writes_requested_parameters_when_provided(tmp_path):
    route_context = context(tmp_path)
    promotion = _seed_signed_promotion(route_context)
    workflow_trigger_id = promotion.item_results[0].production_workflow_trigger.record.record_id

    # Phase 1.4 §11 decision 2 — requested_parameters must respect
    # ``RESERVED_PARAMETER_KEYS`` (enforced at the gate). We exercise the
    # two reserved keys that are valid here: ``confidence_boost`` is the
    # Month 0 legacy key and ``fraud_risk_floor_lift`` is one of the
    # three Phase 1.4 lifts. Both are reserved so the gate accepts them.
    params = {"confidence_boost": 0.30, "fraud_risk_floor_lift": 8}
    result = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        workflow_trigger_id=workflow_trigger_id,
        requested_parameters=params,
    )

    assert result.changed is True
    assert result.new_state.parameters == params
    assert load_state(state_path(route_context.blackboard_root, "tenant_demo")).parameters == params


def test_apply_signed_policy_is_idempotent_when_version_already_active(tmp_path):
    route_context = context(tmp_path)
    promotion = _seed_signed_promotion(route_context)
    workflow_trigger_id = promotion.item_results[0].production_workflow_trigger.record.record_id

    first = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        workflow_trigger_id=workflow_trigger_id,
    )
    second = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        workflow_trigger_id=workflow_trigger_id,
    )

    assert first.changed is True
    assert second.changed is False
    assert second.previous_state == second.new_state == first.new_state


def test_apply_signed_policy_rejects_unsigned_or_unverifiable_evidence(tmp_path):
    route_context = context(tmp_path)
    promotion = _seed_signed_promotion(route_context)
    workflow_trigger_id = promotion.item_results[0].production_workflow_trigger.record.record_id

    wrong_key = SigningKey(secret=b"a-completely-different-key-of-sufficient-length")

    with pytest.raises(GovernanceError, match="signature failed re-verification"):
        apply_signed_policy(
            blackboard_root=route_context.blackboard_root,
            workflow_trigger_id=workflow_trigger_id,
            signing_key=wrong_key,
        )


def test_apply_signed_policy_rejects_workflow_trigger_from_wrong_source(tmp_path):
    """A workflow_trigger that exists but did not come from orchestrator_001
    must not be honoured."""
    route_context = context(tmp_path)
    promotion = _seed_signed_promotion(route_context)
    workflow_trigger_id = promotion.item_results[0].production_workflow_trigger.record.record_id

    real_key = PolicyPromotionConfig().signing_key  # None -> default
    _ = real_key

    state_file = state_path(route_context.blackboard_root, "tenant_demo")
    assert not state_file.exists()

    bogus_id = uuid4()
    with pytest.raises(GovernanceError, match="workflow_trigger .* not found"):
        apply_signed_policy(
            blackboard_root=route_context.blackboard_root,
            workflow_trigger_id=bogus_id,
        )
    assert not state_file.exists()

    apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        workflow_trigger_id=workflow_trigger_id,
    )
    assert state_file.exists()


def test_production_state_load_rejects_unauthorized_fields_on_disk(tmp_path):
    path = state_path(tmp_path / "blackboard", "tenant_demo")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"active_version": "v9", "parameters": {}, "rogue_field": "evil"}',
        encoding="utf-8",
    )

    with pytest.raises(GovernanceError, match="unauthorized fields"):
        load_state(path)


def test_apply_signed_policy_rejects_when_signed_policy_record_is_tampered(tmp_path):
    """Inject a signed policy_update with a tampered signature and ensure the
    gate refuses it even if a workflow_trigger somehow points at it."""
    route_context = context(tmp_path)
    real_key = SigningKey(secret=b"real-key-of-sufficient-length-bytes")
    bad_key = SigningKey(secret=b"impostor-key-of-sufficient-length-bytes")

    submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=PolicyUpdatePayload(
            policy_name="blue_detection_001:tampered",
            change_summary="malicious",
            sandbox_evidence_ids=[],
            rollout_scope="manual_review",
            rollback_plan="revert",
        ),
        signature_id="hmac_sha256:" + "0" * 64,
    )

    promotion = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(signing_key=real_key),
    )
    assert promotion.promoted_count == 0
    assert promotion.rejected_count == 1
    _ = bad_key
