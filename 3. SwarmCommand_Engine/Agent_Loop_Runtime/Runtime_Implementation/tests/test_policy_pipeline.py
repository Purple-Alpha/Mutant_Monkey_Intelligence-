from uuid import uuid4

from core.blackboard import (
    AuditStatus,
    Environment,
    MutantEvaluationPayload,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.mutation import MutationEngineConfig, run_mutation_cycle
from core.orchestrator import (
    RouteContext,
    submit_mutant_evaluation,
    submit_policy_update,
)
from core.orchestrator.routes import blackboard_path
from core.policy import (
    PolicyPromotionConfig,
    SigningKey,
    default_signing_key,
    run_policy_promotion_cycle,
    sign,
)
from core.production import ProductionLoopConfig, ProductionSignal, run_production_cycle

TENANT = "tenant_demo"
LOW_CONFIDENCE_SIGNAL = ProductionSignal(
    source="mailbox",
    event_kind="email_received",
    subject="Team lunch update",
    sender_domain="client-example.ca",
)


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_promoted_policy(route_context: RouteContext) -> None:
    """Seed one signed policy update by running mutation through the sandbox."""
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
    run_mutation_cycle(route_context, config=MutationEngineConfig())


def _inject_signed_policy(
    route_context: RouteContext,
    *,
    policy_name: str,
    parameters: dict,
    is_rollback: bool = False,
):
    key = default_signing_key()
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
) -> None:
    _inject_signed_policy(route_context, policy_name=policy_name, parameters=parameters)
    run_policy_promotion_cycle(route_context)
    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(),
    )


def _production_record_count(
    route_context: RouteContext, record_type: RecordType
) -> int:
    config = PolicyPromotionConfig()
    production_path = blackboard_path(
        route_context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    return sum(
        1 for record in read_records(production_path) if record.record_type == record_type
    )


def test_promotion_pipeline_happy_path_writes_audit_and_workflow_in_production(tmp_path):
    route_context = context(tmp_path)
    _seed_promoted_policy(route_context)

    result = run_policy_promotion_cycle(route_context)

    assert result.processed_count == 1
    assert result.promoted_count == 1
    assert result.rejected_count == 0
    assert result.skipped_count == 0

    item = result.item_results[0]
    assert item.verification_passed is True
    assert item.production_audit is not None
    assert item.production_workflow_trigger is not None
    assert item.sandbox_rejection_audit is None

    config = PolicyPromotionConfig()
    production_path = blackboard_path(
        route_context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    production_records = read_records(production_path)
    types = [record.record_type for record in production_records]
    assert RecordType.AUDIT_VERDICT in types
    assert RecordType.WORKFLOW_TRIGGER in types

    audit_record = next(
        record for record in production_records if record.record_type == RecordType.AUDIT_VERDICT
    )
    workflow_record = next(
        record for record in production_records if record.record_type == RecordType.WORKFLOW_TRIGGER
    )
    assert audit_record.payload["verdict"] == AuditStatus.APPROVED.value
    assert audit_record.payload["target_record_id"] == item.policy_update_record_id
    assert audit_record.workflow_id == "policy_promotion"
    assert workflow_record.payload["workflow_name"] == "apply_policy_update"
    assert workflow_record.workflow_id == "policy_promotion"


def test_promotion_pipeline_rejects_tampered_signatures_without_touching_production(tmp_path):
    route_context = context(tmp_path)

    real_key = default_signing_key()
    real_payload = PolicyUpdatePayload(
        policy_name="blue_detection_001:add_missing_signal_heuristic",
        change_summary="legit",
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan="revert",
    )
    bad_signature = sign(
        {"policy_name": "tampered"},
        "governance_001",
        real_key,
    )
    submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=real_payload,
        signature_id=bad_signature,
    )

    result = run_policy_promotion_cycle(route_context)

    assert result.processed_count == 1
    assert result.promoted_count == 0
    assert result.rejected_count == 1
    assert result.skipped_count == 0
    item = result.item_results[0]
    assert item.verification_passed is False
    assert item.sandbox_rejection_audit is not None
    assert item.production_audit is None
    assert item.production_workflow_trigger is None

    config = PolicyPromotionConfig()
    production_path = blackboard_path(
        route_context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    assert read_records(production_path) == []

    sandbox_path = blackboard_path(
        route_context.blackboard_root,
        Environment.SANDBOX,
        config.sandbox_tenant_id,
    )
    sandbox_records = read_records(sandbox_path)
    rejection_audits = [
        record
        for record in sandbox_records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.payload["verdict"] == AuditStatus.REJECTED.value
    ]
    assert len(rejection_audits) == 1
    assert rejection_audits[0].workflow_id == "policy_promotion"


def test_promotion_pipeline_is_idempotent_on_rerun(tmp_path):
    route_context = context(tmp_path)
    _seed_promoted_policy(route_context)

    first = run_policy_promotion_cycle(route_context)
    second = run_policy_promotion_cycle(route_context)

    assert first.promoted_count == 1
    assert second.processed_count == 1
    assert second.promoted_count == 0
    assert second.skipped_count == 1
    assert second.item_results[0].skipped_already_promoted is True

    config = PolicyPromotionConfig()
    production_path = blackboard_path(
        route_context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    production_records = read_records(production_path)
    audit_count = sum(
        1 for record in production_records if record.record_type == RecordType.AUDIT_VERDICT
    )
    workflow_count = sum(
        1 for record in production_records if record.record_type == RecordType.WORKFLOW_TRIGGER
    )
    assert audit_count == 1
    assert workflow_count == 1


def test_promotion_pipeline_is_noop_on_empty_sandbox(tmp_path):
    result = run_policy_promotion_cycle(context(tmp_path))

    assert result.processed_count == 0
    assert result.promoted_count == 0
    assert result.rejected_count == 0
    assert result.skipped_count == 0
    assert result.item_results == []


def test_promotion_pipeline_rejects_when_key_does_not_match(tmp_path):
    route_context = context(tmp_path)
    _seed_promoted_policy(route_context)

    wrong_key = SigningKey(secret=b"a-different-key-of-sufficient-length")
    result = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(signing_key=wrong_key),
    )

    assert result.processed_count == 1
    assert result.promoted_count == 0
    assert result.rejected_count == 1
    item = result.item_results[0]
    assert item.verification_passed is False
    assert item.sandbox_rejection_audit is not None
    assert item.production_audit is None


def test_promotion_pipeline_rejects_unknown_rollback_target_before_production_trigger(
    tmp_path,
):
    route_context = context(tmp_path)
    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    workflow_count_before = _production_record_count(
        route_context, RecordType.WORKFLOW_TRIGGER
    )

    _inject_signed_policy(
        route_context,
        policy_name="never_was_applied",
        parameters={"confidence_boost": 0.99},
        is_rollback=True,
    )

    result = run_policy_promotion_cycle(route_context)

    assert result.processed_count == 2
    assert result.promoted_count == 0
    assert result.rejected_count == 1
    assert result.skipped_count == 1

    rollback_item = next(
        item
        for item in result.item_results
        if item.sandbox_rejection_audit is not None
    )
    assert rollback_item.verification_passed is True
    assert rollback_item.production_audit is None
    assert rollback_item.production_workflow_trigger is None
    assert _production_record_count(route_context, RecordType.WORKFLOW_TRIGGER) == (
        workflow_count_before
    )

    rejection = rollback_item.sandbox_rejection_audit.record
    assert rejection.payload["verdict"] == AuditStatus.REJECTED.value
    assert rejection.workflow_id == "policy_promotion"
    assert rejection.payload["findings"] == [
        "rollback target not in applied-state history for this tenant"
    ]


def test_promotion_pipeline_allows_known_rollback_target(tmp_path):
    route_context = context(tmp_path)
    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_alpha", parameters={"confidence_boost": 0.10}
    )
    _apply_signed_policy_through_full_pipeline(
        route_context, policy_name="policy_beta", parameters={"confidence_boost": 0.20}
    )

    _inject_signed_policy(
        route_context,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.10},
        is_rollback=True,
    )

    result = run_policy_promotion_cycle(route_context)

    assert result.processed_count == 3
    assert result.promoted_count == 1
    assert result.rejected_count == 0
    assert result.skipped_count == 2
    rollback_item = next(
        item
        for item in result.item_results
        if item.production_workflow_trigger is not None
    )
    assert rollback_item.verification_passed is True
    assert rollback_item.sandbox_rejection_audit is None
    assert rollback_item.production_audit is not None
