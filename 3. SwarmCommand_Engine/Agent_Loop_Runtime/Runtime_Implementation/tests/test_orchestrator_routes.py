from datetime import datetime, timezone

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    AuditStatus,
    AuditVerdictPayload,
    DetectionResultPayload,
    Environment,
    GovernanceError,
    IngestEventPayload,
    PolicyUpdatePayload,
    RecordType,
    RiskScorePayload,
    SyntheticAttackCasePayload,
    MutantEvaluationPayload,
    WeaknessReportPayload,
    WorkflowTriggerPayload,
    read_records,
)
from core.orchestrator import (
    RouteContext,
    submit_audit_verdict,
    submit_detection_result,
    submit_ingest_event,
    submit_policy_update,
    submit_risk_score,
    submit_synthetic_attack_case,
    submit_mutant_evaluation,
    submit_weakness_report,
    trigger_workflow,
)
from core.orchestrator.routes import validate_agent_dispatch


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _stage_a_agent(stage_allowed: str = "stage_a") -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="dispatch_test_001",
        display_name="Dispatch Test Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        stage_allowed=stage_allowed,
    )


def test_validate_agent_dispatch_allows_stage_a_for_stage_a_agent():
    # No exception means the dispatch is permitted.
    validate_agent_dispatch(_stage_a_agent(), stage="stage_a")


def test_validate_agent_dispatch_rejects_out_of_stage():
    with pytest.raises(GovernanceError, match="cannot be dispatched"):
        validate_agent_dispatch(_stage_a_agent("stage_a"), stage="stage_b")


def test_validate_agent_dispatch_rejects_stage_b_c_only_agent_in_stage_a():
    with pytest.raises(GovernanceError, match="cannot be dispatched"):
        validate_agent_dispatch(_stage_a_agent("stage_b_c_only"), stage="stage_a")


def test_validate_agent_dispatch_rejects_autonomous_action_in_stage_a():
    with pytest.raises(GovernanceError, match="never permitted in Stage A"):
        validate_agent_dispatch(
            _stage_a_agent(), stage="stage_a", requests_autonomous_action=True
        )


def test_validate_agent_dispatch_rejects_unknown_stage():
    with pytest.raises(GovernanceError, match="unknown dispatch stage"):
        validate_agent_dispatch(_stage_a_agent(), stage="stage_z")


def test_ingest_route_writes_production_record(tmp_path):
    result = submit_ingest_event(
        context(tmp_path),
        tenant_id="tenant a",
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=IngestEventPayload(
            source="mailbox",
            event_kind="email_received",
            subject="Invoice review",
            received_at=datetime.now(timezone.utc),
        ),
    )

    assert result.path.name == "tenant_a.jsonl"
    records = read_records(result.path)
    assert records[0].record_type == RecordType.INGEST_EVENT


def test_detection_and_scoring_routes_append_to_same_tenant_log(tmp_path):
    route_context = context(tmp_path)
    detection = submit_detection_result(
        route_context,
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        source_agent="blue_detection_001",
        payload=DetectionResultPayload(
            detection_label="suspicious_invoice",
            confidence=0.82,
            signals=["sender_domain_mismatch"],
        ),
    )
    submit_risk_score(
        route_context,
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        source_agent="risk_scoring_001",
        parent_record_id=detection.record.record_id,
        payload=RiskScorePayload(
            score=72,
            risk_level="medium",
            factors=["sender_domain_mismatch"],
        ),
    )

    records = read_records(detection.path)
    assert [record.record_type for record in records] == [
        RecordType.DETECTION_RESULT,
        RecordType.RISK_SCORE,
    ]


def test_workflow_and_audit_routes_write_approved_records(tmp_path):
    route_context = context(tmp_path)
    workflow = trigger_workflow(
        route_context,
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=WorkflowTriggerPayload(
            workflow_name="monthly_training_assignment",
            reason="risk score exceeded threshold",
        ),
    )
    submit_audit_verdict(
        route_context,
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        source_agent="audit_001",
        parent_record_id=workflow.record.record_id,
        payload=AuditVerdictPayload(
            target_record_id=workflow.record.record_id,
            verdict=AuditStatus.APPROVED,
        ),
    )

    records = read_records(workflow.path)
    assert records[-1].record_type == RecordType.AUDIT_VERDICT


def test_weakness_report_is_forced_to_sandbox(tmp_path):
    result = submit_weakness_report(
        context(tmp_path),
        source_agent="blue_detection_001",
        payload=WeaknessReportPayload(
            weakness_kind="low_confidence_invoice_spoof",
            anonymized_pattern="invoice request with mismatched sender domain",
            confidence_gap=0.24,
        ),
    )

    assert result.record.environment == Environment.SANDBOX
    assert "sandbox" in str(result.path)


def test_policy_update_route_creates_signed_sandbox_record(tmp_path):
    result = submit_policy_update(
        context(tmp_path),
        source_agent="governance_001",
        signature_id="sig_policy_001",
        payload=PolicyUpdatePayload(
            policy_name="invoice_detection_threshold",
            change_summary="Raise confidence threshold after sandbox evaluation.",
            rollback_plan="Restore previous threshold.",
        ),
    )

    assert result.record.audit.signed is True
    assert result.record.audit.signature_id == "sig_policy_001"
    assert result.record.environment == Environment.SANDBOX


def test_synthetic_attack_and_mutant_evaluation_routes_are_sandbox_only(tmp_path):
    route_context = context(tmp_path)
    weakness = submit_weakness_report(
        route_context,
        source_agent="blue_detection_001",
        payload=WeaknessReportPayload(
            weakness_kind="low_confidence_detection",
            anonymized_pattern="financial_lure:sender_domain_present:suspicious",
            confidence_gap=0.4,
        ),
    )
    synthetic = submit_synthetic_attack_case(
        route_context,
        source_agent="red_sandbox_001",
        parent_record_id=weakness.record.record_id,
        payload=SyntheticAttackCasePayload(
            attack_kind="synthetic_low_confidence_detection",
            generated_from_weakness_id=weakness.record.record_id,
            synthetic_subject="Urgent invoice payment review",
            synthetic_sender_domain="sandbox-training.example",
        ),
    )
    evaluation = submit_mutant_evaluation(
        route_context,
        source_agent="sandbox_mutator_001",
        parent_record_id=synthetic.record.record_id,
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=synthetic.record.record_id,
            blue_detected=False,
            baseline_confidence=0.53,
            failure_modes=["confidence_below_threshold"],
            mutation_recommended=True,
        ),
    )

    assert synthetic.record.environment == Environment.SANDBOX
    assert evaluation.record.environment == Environment.SANDBOX
    assert evaluation.record.record_type == RecordType.MUTANT_EVALUATION


def test_unknown_agent_is_rejected(tmp_path):
    with pytest.raises(GovernanceError, match="unknown agent"):
        submit_detection_result(
            context(tmp_path),
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            source_agent="missing_agent",
            payload=DetectionResultPayload(
                detection_label="suspicious",
                confidence=0.5,
            ),
        )


def test_red_agent_cannot_use_route_to_write_production_ingest(tmp_path):
    with pytest.raises(GovernanceError, match="environment"):
        submit_ingest_event(
            context(tmp_path),
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            source_agent="red_sandbox_001",
            payload=IngestEventPayload(
                source="red_generator",
                event_kind="synthetic_attack",
                received_at=datetime.now(timezone.utc),
            ),
        )


def test_route_context_can_use_custom_registry(tmp_path):
    registry = {
        "custom_scoring": AgentRegistryEntry(
            agent_id="custom_scoring",
            display_name="Custom Scoring Agent",
            role=AgentRole.SCORING,
            allowed_environments={Environment.SANDBOX},
            allowed_write_types={RecordType.RISK_SCORE},
        )
    }
    route_context = RouteContext(
        blackboard_root=tmp_path / "blackboard",
        registry=registry,
    )

    result = submit_risk_score(
        route_context,
        tenant_id="sandbox_default",
        environment=Environment.SANDBOX,
        source_agent="custom_scoring",
        payload=RiskScorePayload(score=44, risk_level="low"),
    )

    assert result.record.source_agent == "custom_scoring"
