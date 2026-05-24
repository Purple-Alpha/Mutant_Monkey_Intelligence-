from uuid import uuid4

from core.blackboard import (
    MutantEvaluationPayload,
    RecordType,
    read_records,
)
from core.mutation import MutationEngineConfig, run_mutation_cycle
from core.orchestrator import RouteContext, submit_mutant_evaluation
from core.production import ProductionSignal, run_production_cycle
from core.sandbox import SandboxLoopConfig, run_sandbox_cycle


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def test_mutation_engine_promotes_recommended_candidate_from_sandbox_loop(tmp_path):
    route_context = context(tmp_path)
    run_production_cycle(
        route_context,
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Team lunch update",
            sender_domain="client-example.ca",
        ),
    )
    run_sandbox_cycle(
        route_context,
        config=SandboxLoopConfig(detection_confidence_threshold=0.99),
    )

    result = run_mutation_cycle(context=route_context)

    assert result.processed_count == 1
    assert result.promoted_count == 1
    assert result.retired_count == 0
    item = result.item_results[0]
    assert item.candidate.promoted is True
    assert item.policy_update is not None
    assert item.policy_update.record.record_type == RecordType.POLICY_UPDATE
    assert item.policy_update.record.audit.signed is True
    assert "sandbox" in str(item.policy_update.path)


def test_mutation_engine_retires_when_mutation_not_recommended(tmp_path):
    route_context = context(tmp_path)
    evaluation = submit_mutant_evaluation(
        route_context,
        source_agent="sandbox_mutator_001",
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=uuid4(),
            blue_detected=True,
            baseline_confidence=0.91,
            failure_modes=[],
            mutation_recommended=False,
        ),
    )

    result = run_mutation_cycle(context=route_context)

    assert result.processed_count == 1
    assert result.promoted_count == 0
    assert result.retired_count == 1
    assert result.item_results[0].policy_update is None
    assert result.item_results[0].evaluation_record_id == str(evaluation.record.record_id)


def test_mutation_engine_does_not_write_without_evaluations(tmp_path):
    route_context = context(tmp_path)

    result = run_mutation_cycle(context=route_context)

    assert result.processed_count == 0
    assert result.promoted_count == 0
    assert result.retired_count == 0


def test_mutation_engine_policy_updates_remain_sandbox_only(tmp_path):
    route_context = context(tmp_path)
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

    result = run_mutation_cycle(context=route_context)
    policy_path = result.item_results[0].policy_update.path
    records = read_records(policy_path)

    assert all(record.tenant_id == "sandbox_default" for record in records)
    assert RecordType.POLICY_UPDATE in [record.record_type for record in records]
