"""Sandbox Swarm Loop prototype.

The sandbox loop consumes anonymized weakness reports, generates synthetic Red
cases, runs Blue detection in sandbox only, and records mutation-evaluation
placeholders for future mutation engine work.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    DetectionResultPayload,
    Environment,
    MutantEvaluationPayload,
    RecordType,
    SyntheticAttackCasePayload,
    WeaknessReportPayload,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_audit_verdict,
    submit_detection_result,
    submit_mutant_evaluation,
    submit_synthetic_attack_case,
)
from core.orchestrator.routes import blackboard_path


@dataclass(frozen=True)
class SandboxLoopConfig:
    sandbox_tenant_id: str = "sandbox_default"
    red_agent_id: str = "red_sandbox_001"
    blue_agent_id: str = "blue_detection_001"
    mutation_evaluator_agent_id: str = "sandbox_mutator_001"
    audit_agent_id: str = "audit_001"
    detection_confidence_threshold: float = 0.70


@dataclass(frozen=True)
class SandboxLoopItemResult:
    weakness_record_id: str
    synthetic_attack: RouteResult
    blue_detection: RouteResult
    mutant_evaluation: RouteResult
    audit: RouteResult


@dataclass(frozen=True)
class SandboxLoopResult:
    processed_count: int
    item_results: list[SandboxLoopItemResult]


def _load_weakness_reports(context: RouteContext, config: SandboxLoopConfig):
    path = blackboard_path(
        context.blackboard_root,
        Environment.SANDBOX,
        config.sandbox_tenant_id,
    )
    return [
        record
        for record in read_records(path)
        if record.record_type == RecordType.WEAKNESS_REPORT
    ]


def _red_generate_case(weakness: WeaknessReportPayload, weakness_record_id) -> SyntheticAttackCasePayload:
    if "financial_lure" in weakness.anonymized_pattern or "invoice" in weakness.weakness_kind:
        subject = "Urgent invoice payment review"
        expected = ["financial_lure_language", "urgency_language", "unknown_sender_domain"]
    else:
        subject = "Immediate policy confirmation request"
        expected = ["urgency_language", "unknown_sender_domain"]

    return SyntheticAttackCasePayload(
        attack_kind=f"synthetic_{weakness.weakness_kind}",
        generated_from_weakness_id=weakness_record_id,
        synthetic_subject=subject,
        synthetic_sender_domain="sandbox-training.example",
        expected_detection_signals=expected,
        raw_tenant_data_removed=True,
    )


def _blue_detect(case: SyntheticAttackCasePayload) -> DetectionResultPayload:
    subject = case.synthetic_subject.lower()
    sender_domain = case.synthetic_sender_domain.lower()
    signals: list[str] = []

    if "invoice" in subject or "payment" in subject:
        signals.append("financial_lure_language")
    if "urgent" in subject or "immediate" in subject:
        signals.append("urgency_language")
    if sender_domain and "client" not in sender_domain and "northstar" not in sender_domain:
        signals.append("unknown_sender_domain")

    confidence = min(0.35 + (0.18 * len(signals)), 0.95)
    label = "suspicious" if signals else "no_obvious_threat"

    return DetectionResultPayload(
        detection_label=label,
        confidence=confidence,
        signals=signals,
        explanation="Sandbox Blue detector evaluated a synthetic Red case.",
    )


def _evaluate_blue(
    case: SyntheticAttackCasePayload,
    detection: DetectionResultPayload,
    config: SandboxLoopConfig,
    source_attack_case_id: UUID,
) -> MutantEvaluationPayload:
    missing_signals = [
        signal
        for signal in case.expected_detection_signals
        if signal not in detection.signals
    ]
    blue_detected = (
        detection.confidence >= config.detection_confidence_threshold
        and not missing_signals
    )
    failure_modes: list[str] = []
    if detection.confidence < config.detection_confidence_threshold:
        failure_modes.append("confidence_below_threshold")
    failure_modes.extend(f"missing_signal:{signal}" for signal in missing_signals)

    return MutantEvaluationPayload(
        baseline_agent_id=config.blue_agent_id,
        candidate_agent_id=None,
        source_attack_case_id=source_attack_case_id,
        blue_detected=blue_detected,
        baseline_confidence=detection.confidence,
        failure_modes=failure_modes,
        mutation_recommended=not blue_detected,
    )


def run_sandbox_cycle(
    context: RouteContext,
    *,
    config: SandboxLoopConfig | None = None,
) -> SandboxLoopResult:
    """Run one sandbox cycle over the current sandbox weakness queue."""

    config = config or SandboxLoopConfig()

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="SANDBOX"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    item_results: list[SandboxLoopItemResult] = []

    for weakness_record in _load_weakness_reports(context, config):
        weakness_payload = WeaknessReportPayload.model_validate(weakness_record.payload)
        synthetic_payload = _red_generate_case(
            weakness_payload,
            weakness_record.record_id,
        )
        synthetic_attack = submit_synthetic_attack_case(
            context,
            source_agent=config.red_agent_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            parent_record_id=weakness_record.record_id,
            payload=synthetic_payload,
        )

        detection_payload = _blue_detect(synthetic_payload)
        blue_detection = submit_detection_result(
            context,
            tenant_id=config.sandbox_tenant_id,
            environment=Environment.SANDBOX,
            source_agent=config.blue_agent_id,
            parent_record_id=synthetic_attack.record.record_id,
            payload=detection_payload,
        )

        evaluation_payload = _evaluate_blue(
            synthetic_payload,
            detection_payload,
            config,
            synthetic_attack.record.record_id,
        )
        mutant_evaluation = submit_mutant_evaluation(
            context,
            source_agent=config.mutation_evaluator_agent_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            parent_record_id=blue_detection.record.record_id,
            payload=evaluation_payload,
        )

        audit = submit_audit_verdict(
            context,
            tenant_id=config.sandbox_tenant_id,
            environment=Environment.SANDBOX,
            source_agent=config.audit_agent_id,
            parent_record_id=mutant_evaluation.record.record_id,
            payload=AuditVerdictPayload(
                target_record_id=mutant_evaluation.record.record_id,
                verdict=AuditStatus.APPROVED,
                findings=["sandbox cycle records validated"],
                requires_human_review=evaluation_payload.mutation_recommended,
            ),
        )

        item_results.append(
            SandboxLoopItemResult(
                weakness_record_id=str(weakness_record.record_id),
                synthetic_attack=synthetic_attack,
                blue_detection=blue_detection,
                mutant_evaluation=mutant_evaluation,
                audit=audit,
            )
        )

    return SandboxLoopResult(
        processed_count=len(item_results),
        item_results=item_results,
    )
