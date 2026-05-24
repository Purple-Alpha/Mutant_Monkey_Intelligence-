"""Phase 1.3 Sandbox Training Pit — Red battery cycle.

Single entry point ``run_red_battery_cycle`` per the deep dive §4:

1. Kill-switch check at the sandbox boundary (cheap read; raise on
   engaged).
2. For each configured Red profile, generate ``≥ 100`` cases (Decision
   3 floor) and write each as a sandbox-only
   ``SYNTHETIC_EMAIL_ATTACK_CASE`` record under the profile's agent id.
3. For each case, invoke Blue in-memory via
   ``score_one_email_payload`` (Decision 2 path) and evaluate the
   result against the case's expected subset.
4. Translate each per-case verdict into one
   ``Phase13FailureDetail`` list (Decision 4 typed taxonomy with
   ``dynamic_detail`` carrying the per-case specifics) plus a
   companion freeform ``failure_modes`` list (Month 0 legacy view).
5. Append one ``MUTANT_EVALUATION`` per case under
   ``phase_1_3_sandbox_mutator_001``; append one
   ``AUDIT_VERDICT`` per case under ``audit_001`` flagged for human
   review when Blue missed anything.
6. After every profile, aggregate the failure-mode bucket counts into
   one ``WEAKNESS_REPORT`` under ``phase_1_3_sandbox_mutator_001`` with
   the controlled bucket-count payload (raw tenant data is removed
   by construction — sandbox cases are synthetic).

Promotion boundary: this module never writes ``POLICY_UPDATE``
records. Promotion stays in the Month 5 mutation engine; Phase 1.3
only produces the diagnostic substrate.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    MutantEvaluationPayload,
    Phase13FailureDetail,
    Phase13FailureMode,
    SyntheticEmailAttackCasePayload,
    WeaknessReportPayload,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_audit_verdict,
    submit_mutant_evaluation,
    submit_synthetic_email_attack_case,
    submit_weakness_report,
)
from core.scoring.email_risk_scoring_agent import (
    EmailRiskScoringInMemoryFailure,
    LLMClient,
    score_one_email_payload,
)

from .red_agents import RED_PROFILE_MODULES, bucket_e_probes

PHASE_1_3_MUTATOR_AGENT_ID = "phase_1_3_sandbox_mutator_001"
PHASE_1_3_AUDIT_AGENT_ID = "audit_001"
PHASE_1_3_BLUE_AGENT_ID = "email_risk_scoring_001"

# Default per-profile case count. Floor set by Matt's §11 decision 3.
DEFAULT_CASES_PER_PROFILE = 100


@dataclass(frozen=True)
class RedBatteryConfig:
    """Configuration for one Phase 1.3 Red battery cycle."""

    llm_client: LLMClient
    sandbox_tenant_id: str = "sandbox_default"
    cases_per_profile: int = DEFAULT_CASES_PER_PROFILE
    seed: int = 0
    include_bucket_e_probes: bool = True
    enable_ransomware_precursor_overlay: bool = True


@dataclass(frozen=True)
class RedBatteryProfileResult:
    red_profile_id: str
    archetype: str
    cases_generated: int
    cases_with_failures: int
    failure_mode_counts: dict[str, int]
    case_record_ids: list[UUID]
    mutant_evaluation_record_ids: list[UUID]
    audit_record_ids: list[UUID]
    weakness_report_record_id: UUID


@dataclass(frozen=True)
class RedBatteryResult:
    """Aggregate of every Red profile run in this battery."""

    profile_results: list[RedBatteryProfileResult] = field(default_factory=list)
    bucket_e_case_ids: list[str] = field(default_factory=list)

    @property
    def total_cases(self) -> int:
        return sum(p.cases_generated for p in self.profile_results)

    @property
    def total_failures(self) -> int:
        return sum(p.cases_with_failures for p in self.profile_results)


def run_red_battery_cycle(
    context: RouteContext,
    *,
    config: RedBatteryConfig,
) -> RedBatteryResult:
    """Run every registered Red profile once against the in-memory Blue.

    Kill-switch boundary: a sandbox-scoped engagement aborts the entire
    cycle before any record is written. Production-only kill switches
    do not affect this loop because it never writes to production.
    """

    state = is_kill_switch_engaged(context.blackboard_root, scope="SANDBOX")
    if state is not None:
        raise KillSwitchEngaged(state)

    profile_results: list[RedBatteryProfileResult] = []
    bucket_e_case_ids: list[str] = []

    for module in RED_PROFILE_MODULES:
        red_profile_id: str = module.RED_PROFILE_ID
        archetype: str = module.ARCHETYPE

        cases = module.generate_cases(
            seed=config.seed, count=config.cases_per_profile
        )

        if config.include_bucket_e_probes:
            for probe in bucket_e_probes.generate_bucket_e_probes():
                if probe.red_profile_id == red_profile_id:
                    cases.append(probe)
                    bucket_e_case_ids.append(probe.case_id)

        profile_results.append(
            _run_one_profile(
                context,
                config=config,
                red_profile_id=red_profile_id,
                archetype=archetype,
                cases=cases,
            )
        )

    return RedBatteryResult(
        profile_results=profile_results,
        bucket_e_case_ids=bucket_e_case_ids,
    )


def _run_one_profile(
    context: RouteContext,
    *,
    config: RedBatteryConfig,
    red_profile_id: str,
    archetype: str,
    cases: list[SyntheticEmailAttackCasePayload],
) -> RedBatteryProfileResult:
    case_record_ids: list[UUID] = []
    mutant_evaluation_record_ids: list[UUID] = []
    audit_record_ids: list[UUID] = []
    failure_mode_counter: Counter[str] = Counter()
    cases_with_failures = 0

    for case in cases:
        case_route = submit_synthetic_email_attack_case(
            context,
            source_agent=red_profile_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            payload=case,
        )
        case_record_ids.append(case_route.record.record_id)

        blue_result = _invoke_blue(
            inbound_payload=case.inbound,
            llm_client=config.llm_client,
            enable_overlay=config.enable_ransomware_precursor_overlay,
        )

        failure_details, blue_detected, baseline_confidence = _evaluate_case(
            case=case, blue_result=blue_result
        )
        if failure_details:
            cases_with_failures += 1
        for detail in failure_details:
            failure_mode_counter[detail.failure_mode] += 1

        mutant_payload = MutantEvaluationPayload(
            baseline_agent_id=PHASE_1_3_BLUE_AGENT_ID,
            candidate_agent_id=None,
            source_attack_case_id=case_route.record.record_id,
            blue_detected=blue_detected,
            baseline_confidence=baseline_confidence,
            failure_modes=[d.failure_mode for d in failure_details],
            mutation_recommended=bool(failure_details),
            phase_1_3_failure_details=failure_details,
        )
        mutant_route = submit_mutant_evaluation(
            context,
            source_agent=PHASE_1_3_MUTATOR_AGENT_ID,
            sandbox_tenant_id=config.sandbox_tenant_id,
            parent_record_id=case_route.record.record_id,
            payload=mutant_payload,
        )
        mutant_evaluation_record_ids.append(mutant_route.record.record_id)

        audit_route = _write_per_case_audit(
            context,
            config=config,
            case_record_id=case_route.record.record_id,
            failure_details=failure_details,
        )
        audit_record_ids.append(audit_route.record.record_id)

    weakness_record_id = _write_weakness_report(
        context,
        config=config,
        red_profile_id=red_profile_id,
        archetype=archetype,
        cases_generated=len(cases),
        cases_with_failures=cases_with_failures,
        failure_mode_counter=failure_mode_counter,
        case_record_ids=case_record_ids,
    )

    return RedBatteryProfileResult(
        red_profile_id=red_profile_id,
        archetype=archetype,
        cases_generated=len(cases),
        cases_with_failures=cases_with_failures,
        failure_mode_counts=dict(failure_mode_counter),
        case_record_ids=case_record_ids,
        mutant_evaluation_record_ids=mutant_evaluation_record_ids,
        audit_record_ids=audit_record_ids,
        weakness_report_record_id=weakness_record_id,
    )


def _invoke_blue(
    *,
    inbound_payload: EmailInboundPayload,
    llm_client: LLMClient,
    enable_overlay: bool,
) -> EmailAnalysisPayload | EmailRiskScoringInMemoryFailure | _BlueException:
    """Wrap ``score_one_email_payload`` and catch unhandled exceptions.

    The in-memory helper already catches LLM client exceptions and JSON
    parse / schema errors into ``EmailRiskScoringInMemoryFailure``. Any
    other unhandled exception (defensive — should not happen in
    practice) is surfaced as ``_BlueException`` so the evaluator can
    record the ``unexpected_blue_exception`` failure mode rather than
    blowing up the battery.
    """

    try:
        return score_one_email_payload(
            inbound_payload,
            llm_client=llm_client,
            enable_ransomware_precursor_overlay=enable_overlay,
        )
    except Exception as exc:
        return _BlueException(exception_name=type(exc).__name__)


@dataclass(frozen=True)
class _BlueException:
    exception_name: str


def _evaluate_case(
    *,
    case: SyntheticEmailAttackCasePayload,
    blue_result: EmailAnalysisPayload | EmailRiskScoringInMemoryFailure | _BlueException,
) -> tuple[list[Phase13FailureDetail], bool, float]:
    """Translate one Blue result into a typed failure-detail list.

    Returns ``(failure_details, blue_detected, baseline_confidence)``.

    - ``blue_detected`` is True when Blue produced a non-failure
      ``EmailAnalysisPayload`` AND raised the risk_score above safe.
    - ``baseline_confidence`` is the ``risk_score / 100`` for the
      success path, ``0.0`` for both failure paths.
    """

    if isinstance(blue_result, _BlueException):
        return (
            [
                Phase13FailureDetail(
                    failure_mode="unexpected_blue_exception",
                    dynamic_detail=blue_result.exception_name,
                )
            ],
            False,
            0.0,
        )

    if isinstance(blue_result, EmailRiskScoringInMemoryFailure):
        return (
            [
                Phase13FailureDetail(
                    failure_mode="analysis_failure_record_written",
                    dynamic_detail=blue_result.failure_reason,
                )
            ],
            False,
            0.0,
        )

    failures = _diff_against_expectations(case=case, analysis=blue_result)
    risk_score = blue_result.risk_analysis.risk_score
    blue_detected = (
        not failures and blue_result.recommended_action != "safe"
    )
    return failures, blue_detected, risk_score / 100.0


_FailureModeTag = Phase13FailureMode  # readability alias


def _diff_against_expectations(
    *,
    case: SyntheticEmailAttackCasePayload,
    analysis: EmailAnalysisPayload,
) -> list[Phase13FailureDetail]:
    """Apply the eight-mode taxonomy to one Blue analysis."""

    failures: list[Phase13FailureDetail] = []

    actual_risk = analysis.risk_analysis.risk_score
    if (
        case.expected_min_risk_score is not None
        and actual_risk < case.expected_min_risk_score
    ):
        failures.append(
            Phase13FailureDetail(
                failure_mode="risk_score_below_floor",
                dynamic_detail=f"{actual_risk}<{case.expected_min_risk_score}",
            )
        )
    if (
        case.expected_max_risk_score is not None
        and actual_risk > case.expected_max_risk_score
    ):
        failures.append(
            Phase13FailureDetail(
                failure_mode="risk_score_above_ceiling",
                dynamic_detail=f"{actual_risk}>{case.expected_max_risk_score}",
            )
        )

    emitted_flags = set(analysis.risk_analysis.behavioral_deviation_flags)
    for required_flag in case.expected_behavioral_flags:
        if required_flag not in emitted_flags:
            failures.append(
                Phase13FailureDetail(
                    failure_mode="missing_behavioral_flag",
                    dynamic_detail=required_flag,
                )
            )

    if case.expected_recommended_actions and (
        analysis.recommended_action not in case.expected_recommended_actions
    ):
        failures.append(
            Phase13FailureDetail(
                failure_mode="recommended_action_unexpected",
                dynamic_detail=analysis.recommended_action,
            )
        )

    if case.expects_precursor_block and analysis.ransomware_precursor_analysis is None:
        failures.append(
            Phase13FailureDetail(
                failure_mode="precursor_block_missing",
                dynamic_detail=None,
            )
        )

    emitted_indicators: set[str]
    if analysis.ransomware_precursor_analysis is None:
        emitted_indicators = set()
    else:
        emitted_indicators = set(
            analysis.ransomware_precursor_analysis.precursor_indicators
        )
    for required_indicator in case.expected_precursor_indicators:
        if required_indicator not in emitted_indicators:
            failures.append(
                Phase13FailureDetail(
                    failure_mode="missing_precursor_indicator",
                    dynamic_detail=required_indicator,
                )
            )

    return failures


def _write_per_case_audit(
    context: RouteContext,
    *,
    config: RedBatteryConfig,
    case_record_id: UUID,
    failure_details: list[Phase13FailureDetail],
) -> RouteResult:
    findings = [
        f"failure_mode={d.failure_mode}|detail={d.dynamic_detail or '-'}"
        for d in failure_details
    ]
    return submit_audit_verdict(
        context,
        tenant_id=config.sandbox_tenant_id,
        environment=Environment.SANDBOX,
        source_agent=PHASE_1_3_AUDIT_AGENT_ID,
        parent_record_id=case_record_id,
        payload=AuditVerdictPayload(
            target_record_id=case_record_id,
            verdict=(
                AuditStatus.QUARANTINED if failure_details else AuditStatus.APPROVED
            ),
            findings=findings,
            requires_human_review=bool(failure_details),
        ),
    )


def _write_weakness_report(
    context: RouteContext,
    *,
    config: RedBatteryConfig,
    red_profile_id: str,
    archetype: str,
    cases_generated: int,
    cases_with_failures: int,
    failure_mode_counter: Counter[str],
    case_record_ids: list[UUID],
) -> UUID:
    sorted_buckets = sorted(failure_mode_counter.items())
    bucket_summary = ",".join(f"{mode}={count}" for mode, count in sorted_buckets)
    anonymized_pattern = (
        f"phase_1_3:{archetype}:cases={cases_generated}:"
        f"failures={cases_with_failures}:buckets=[{bucket_summary}]"
    )

    confidence_gap = 0.0
    if cases_generated > 0:
        confidence_gap = round(cases_with_failures / cases_generated, 4)

    payload = WeaknessReportPayload(
        weakness_kind=f"phase_1_3_red_profile:{red_profile_id}",
        anonymized_pattern=anonymized_pattern,
        confidence_gap=confidence_gap,
        source_record_ids=case_record_ids,
        raw_tenant_data_removed=True,
    )
    route = submit_weakness_report(
        context,
        source_agent=PHASE_1_3_MUTATOR_AGENT_ID,
        sandbox_tenant_id=config.sandbox_tenant_id,
        payload=payload,
    )
    return route.record.record_id


__all__ = [
    "DEFAULT_CASES_PER_PROFILE",
    "PHASE_1_3_AUDIT_AGENT_ID",
    "PHASE_1_3_BLUE_AGENT_ID",
    "PHASE_1_3_MUTATOR_AGENT_ID",
    "RedBatteryConfig",
    "RedBatteryProfileResult",
    "RedBatteryResult",
    "run_red_battery_cycle",
]
