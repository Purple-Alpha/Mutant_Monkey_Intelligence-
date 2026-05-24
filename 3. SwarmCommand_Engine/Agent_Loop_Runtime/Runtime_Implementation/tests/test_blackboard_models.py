from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    AuditMeta,
    BlackboardRecord,
    DetectionResultPayload,
    Environment,
    GovernanceError,
    IngestEventPayload,
    PolicyUpdatePayload,
    RecordType,
    append_record,
    read_records,
    validate_record_against_registry,
)


def detection_agent() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="blue_detection_001",
        display_name="Blue Detection Agent 001",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={
            RecordType.DETECTION_RESULT,
            RecordType.WEAKNESS_REPORT,
        },
        can_access_production_data=True,
    )


def red_agent() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="red_sandbox_001",
        display_name="Sandbox Red Agent 001",
        role=AgentRole.RED,
        allowed_environments={Environment.SANDBOX},
        allowed_write_types={RecordType.INGEST_EVENT},
    )


def mutation_agent() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="sandbox_mutator_001",
        display_name="Sandbox Mutator 001",
        role=AgentRole.BLUE,
        allowed_environments={Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        can_mutate=True,
    )


def test_valid_production_detection_record_round_trips_to_jsonl(tmp_path):
    payload = DetectionResultPayload(
        detection_label="suspicious_invoice",
        confidence=0.86,
        signals=["sender_domain_mismatch", "urgent_payment_language"],
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.DETECTION_RESULT,
        source_agent="blue_detection_001",
        payload=payload.model_dump(mode="json"),
    )

    validated_payload = validate_record_against_registry(record, detection_agent())

    assert validated_payload.detection_label == "suspicious_invoice"

    path = tmp_path / "tenant_demo.jsonl"
    append_record(path, record)
    records = read_records(path)

    assert len(records) == 1
    assert records[0].record_id == record.record_id
    assert records[0].payload["confidence"] == 0.86


def test_red_agent_cannot_write_to_production():
    payload = IngestEventPayload(
        source="sandbox_generator",
        event_kind="synthetic_attack",
        received_at=datetime.now(timezone.utc),
    )
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.INGEST_EVENT,
        source_agent="red_sandbox_001",
        payload=payload.model_dump(mode="json"),
    )

    with pytest.raises(GovernanceError, match="environment"):
        validate_record_against_registry(record, red_agent())


def test_mutation_agent_cannot_be_registered_for_production():
    with pytest.raises(ValidationError, match="Mutation-capable agents are sandbox-only"):
        AgentRegistryEntry(
            agent_id="bad_mutator",
            display_name="Bad Mutator",
            role=AgentRole.BLUE,
            allowed_environments={Environment.PRODUCTION},
            allowed_write_types={RecordType.DETECTION_RESULT},
            can_mutate=True,
        )


def test_record_rejects_hop_count_greater_than_ten():
    with pytest.raises(ValidationError):
        BlackboardRecord(
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            record_type=RecordType.DETECTION_RESULT,
            source_agent="blue_detection_001",
            hop_count=11,
            payload={"detection_label": "x", "confidence": 0.5},
        )


def test_unauthorized_record_type_is_rejected():
    payload = {"score": 75, "risk_level": "medium"}
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.RISK_SCORE,
        source_agent="blue_detection_001",
        payload=payload,
    )

    with pytest.raises(GovernanceError, match="record type"):
        validate_record_against_registry(record, detection_agent())


def test_policy_update_requires_signed_sandbox_record():
    payload = PolicyUpdatePayload(
        policy_name="invoice_detection_threshold",
        change_summary="Increase confidence requirement for invoice spoof detection.",
        rollback_plan="Restore previous threshold from policy snapshot.",
    )
    record = BlackboardRecord(
        tenant_id="sandbox_default",
        environment=Environment.SANDBOX,
        record_type=RecordType.POLICY_UPDATE,
        source_agent="governance_001",
        payload=payload.model_dump(mode="json"),
        audit=AuditMeta(signed=False),
    )
    agent = AgentRegistryEntry(
        agent_id="governance_001",
        display_name="Governance Constitution Agent",
        role=AgentRole.GOVERNANCE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AUDIT_VERDICT, RecordType.POLICY_UPDATE},
        can_access_production_data=True,
    )

    with pytest.raises(GovernanceError, match="signed"):
        validate_record_against_registry(record, agent)
