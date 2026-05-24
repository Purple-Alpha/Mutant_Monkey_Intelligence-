from core.blackboard import Environment, RecordType, read_records
from core.orchestrator import RouteContext
from core.production import ProductionLoopConfig, ProductionSignal, run_production_cycle


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def test_production_loop_runs_high_risk_signal_end_to_end(tmp_path):
    route_context = context(tmp_path)

    result = run_production_cycle(
        route_context,
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Urgent invoice payment required",
            sender_domain="unknown-vendor.ru",
        ),
    )

    production_records = read_records(result.ingest.path)
    assert [record.record_type for record in production_records] == [
        RecordType.INGEST_EVENT,
        RecordType.DETECTION_RESULT,
        RecordType.RISK_SCORE,
        RecordType.WORKFLOW_TRIGGER,
        RecordType.AUDIT_VERDICT,
    ]
    assert result.workflow_trigger is not None
    assert result.weakness_report is None
    assert all(record.environment == Environment.PRODUCTION for record in production_records)


def test_low_confidence_detection_sends_anonymized_weakness_to_sandbox(tmp_path):
    result = run_production_cycle(
        context(tmp_path),
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Team lunch update",
            sender_domain="client-example.ca",
        ),
    )

    assert result.workflow_trigger is None
    assert result.weakness_report is not None
    assert result.weakness_report.record.environment == Environment.SANDBOX
    assert result.weakness_report.record.tenant_id == "sandbox_default"
    assert "Team lunch" not in result.weakness_report.record.payload["anonymized_pattern"]


def test_custom_threshold_can_suppress_workflow_trigger(tmp_path):
    result = run_production_cycle(
        context(tmp_path),
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Urgent invoice payment required",
            sender_domain="unknown-vendor.ru",
        ),
        config=ProductionLoopConfig(risk_threshold=100),
    )

    records = read_records(result.ingest.path)
    assert result.workflow_trigger is None
    assert [record.record_type for record in records] == [
        RecordType.INGEST_EVENT,
        RecordType.DETECTION_RESULT,
        RecordType.RISK_SCORE,
        RecordType.AUDIT_VERDICT,
    ]
