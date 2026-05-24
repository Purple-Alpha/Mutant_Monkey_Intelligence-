from core.blackboard import RecordType, WeaknessReportPayload, read_records
from core.orchestrator import RouteContext, submit_weakness_report
from core.sandbox import SandboxLoopConfig, run_sandbox_cycle


def context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def seed_weakness(route_context: RouteContext):
    return submit_weakness_report(
        route_context,
        source_agent="blue_detection_001",
        payload=WeaknessReportPayload(
            weakness_kind="low_confidence_detection",
            anonymized_pattern="financial_lure:sender_domain_present:suspicious",
            confidence_gap=0.47,
        ),
    )


def test_sandbox_loop_processes_weakness_into_red_blue_training_records(tmp_path):
    route_context = context(tmp_path)
    weakness = seed_weakness(route_context)

    result = run_sandbox_cycle(context=route_context)

    assert result.processed_count == 1
    assert result.item_results[0].weakness_record_id == str(weakness.record.record_id)

    records = read_records(weakness.path)
    assert [record.record_type for record in records] == [
        RecordType.WEAKNESS_REPORT,
        RecordType.SYNTHETIC_ATTACK_CASE,
        RecordType.DETECTION_RESULT,
        RecordType.MUTANT_EVALUATION,
        RecordType.AUDIT_VERDICT,
    ]


def test_sandbox_loop_stays_in_sandbox(tmp_path):
    route_context = context(tmp_path)
    seed_weakness(route_context)

    result = run_sandbox_cycle(context=route_context)

    for item in result.item_results:
        assert "sandbox" in str(item.synthetic_attack.path)
        assert "sandbox" in str(item.blue_detection.path)
        assert "sandbox" in str(item.mutant_evaluation.path)
        assert "sandbox" in str(item.audit.path)


def test_sandbox_loop_recommends_mutation_when_confidence_threshold_is_high(tmp_path):
    route_context = context(tmp_path)
    seed_weakness(route_context)

    result = run_sandbox_cycle(
        context=route_context,
        config=SandboxLoopConfig(detection_confidence_threshold=0.99),
    )

    evaluation = result.item_results[0].mutant_evaluation.record
    assert evaluation.payload["blue_detected"] is False
    assert evaluation.payload["mutation_recommended"] is True
    assert "confidence_below_threshold" in evaluation.payload["failure_modes"]


def test_sandbox_loop_returns_empty_result_when_no_weaknesses_exist(tmp_path):
    result = run_sandbox_cycle(context=context(tmp_path))

    assert result.processed_count == 0
    assert result.item_results == []
