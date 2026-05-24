"""End-to-end integration tests for the closed production policy loop.

Drives the full sequence:

    production signal
        -> Blue detection / weakness report
        -> sandbox loop generates Red case + Blue eval
        -> mutation engine signs a policy update
        -> policy promotion pipeline emits apply_policy_update trigger
        -> next production cycle consumes the trigger
        -> production_state mutates through the Guardrail 11 gate
        -> subsequent production cycle uses the new parameters

Asserts that every governance hop happened and that the detector's
confidence on the same signal increases by exactly the signed
``confidence_boost`` after the policy is applied.
"""

from __future__ import annotations

from core.blackboard import RecordType, read_records
from core.mutation import run_mutation_cycle
from core.orchestrator import RouteContext
from core.orchestrator.routes import blackboard_path
from core.policy import run_policy_promotion_cycle
from core.production import (
    PolicyConsumerConfig,
    ProductionLoopConfig,
    ProductionSignal,
    apply_pending_policies,
    find_unconsumed_apply_triggers,
    run_production_cycle,
)
from core.production_state import (
    ProductionPolicyState,
    load_state,
    state_path,
)
from core.sandbox import SandboxLoopConfig, run_sandbox_cycle


TENANT = "tenant_demo"

LOW_CONFIDENCE_SIGNAL = ProductionSignal(
    source="mailbox",
    event_kind="email_received",
    subject="Team lunch update",
    sender_domain="client-example.ca",
)


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def test_policy_consumer_finds_unconsumed_apply_trigger_then_marks_it_consumed(tmp_path):
    """Unit-level: consumer's find/skip logic works without running the full loop."""
    route_context = _context(tmp_path)

    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(apply_pending_policies_at_end_of_cycle=False),
    )
    run_sandbox_cycle(
        route_context, config=SandboxLoopConfig(detection_confidence_threshold=0.99)
    )
    run_mutation_cycle(route_context)
    run_policy_promotion_cycle(route_context)

    pending = find_unconsumed_apply_triggers(route_context, tenant_id=TENANT)
    assert len(pending) == 1

    first = apply_pending_policies(
        route_context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
    )
    assert first.processed_count == 1
    assert first.applied_count == 1
    assert first.skipped_count == 0

    pending_after = find_unconsumed_apply_triggers(route_context, tenant_id=TENANT)
    assert pending_after == []

    second = apply_pending_policies(
        route_context, config=PolicyConsumerConfig(production_tenant_id=TENANT)
    )
    assert second.processed_count == 0


def test_end_to_end_signed_policy_changes_next_cycle_detector_confidence(tmp_path):
    """The whole loop: signal -> sandbox -> sign -> promote -> apply -> next cycle uses new params."""
    route_context = _context(tmp_path)

    cycle1 = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
    )
    assert cycle1.active_policy_state == ProductionPolicyState()
    assert cycle1.weakness_report is not None
    assert cycle1.policy_apply is not None
    assert cycle1.policy_apply.applied_count == 0
    cycle1_confidence = cycle1.detection.record.payload["confidence"]
    assert cycle1_confidence < 0.70

    run_sandbox_cycle(
        route_context, config=SandboxLoopConfig(detection_confidence_threshold=0.99)
    )
    mutation = run_mutation_cycle(route_context)
    assert mutation.promoted_count == 1
    signed_policy_update = mutation.item_results[0].policy_update
    assert signed_policy_update is not None
    expected_boost = signed_policy_update.record.payload["parameters"]["confidence_boost"]
    assert expected_boost > 0

    promotion = run_policy_promotion_cycle(route_context)
    assert promotion.promoted_count == 1

    state_before_cycle2 = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state_before_cycle2 == ProductionPolicyState()

    cycle2 = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
    )
    assert cycle2.active_policy_state == ProductionPolicyState()
    assert cycle2.policy_apply is not None
    assert cycle2.policy_apply.applied_count == 1
    state_after_cycle2 = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state_after_cycle2.active_version.startswith("blue_detection_001:")
    assert state_after_cycle2.parameters == {"confidence_boost": expected_boost}

    production_path = blackboard_path(
        route_context.blackboard_root, cycle2.ingest.record.environment, TENANT
    )
    production_records = read_records(production_path)
    policy_applied_audits = [
        record
        for record in production_records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == "policy_applied"
    ]
    assert len(policy_applied_audits) == 1
    assert policy_applied_audits[0].source_agent == "governance_001"

    cycle3 = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
    )
    assert cycle3.active_policy_state == state_after_cycle2
    assert cycle3.policy_apply is not None
    assert cycle3.policy_apply.applied_count == 0

    cycle3_confidence = cycle3.detection.record.payload["confidence"]
    assert cycle3_confidence > cycle1_confidence
    assert abs((cycle3_confidence - cycle1_confidence) - expected_boost) < 1e-9


def test_production_loop_does_not_consume_when_disabled_by_config(tmp_path):
    """``apply_pending_policies_at_end_of_cycle=False`` skips the consumer cleanly."""
    route_context = _context(tmp_path)

    run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(apply_pending_policies_at_end_of_cycle=False),
    )
    run_sandbox_cycle(
        route_context, config=SandboxLoopConfig(detection_confidence_threshold=0.99)
    )
    run_mutation_cycle(route_context)
    run_policy_promotion_cycle(route_context)

    cycle = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(apply_pending_policies_at_end_of_cycle=False),
    )
    assert cycle.policy_apply is None
    state_after = load_state(state_path(route_context.blackboard_root, TENANT))
    assert state_after == ProductionPolicyState()
    assert find_unconsumed_apply_triggers(route_context, tenant_id=TENANT)
