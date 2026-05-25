"""Internal routing layer for approved Blackboard writes.

This is intentionally not an HTTP server yet. It is the stable contract the
future API can wrap: routes construct records, validate governance rules, and
append to the Blackboard through one controlled path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID

from core.blackboard import (
    AgentRegistryEntry,
    AuditMeta,
    AuditStatus,
    AuditVerdictPayload,
    BlackboardRecord,
    DailyDigestPayload,
    DetectionResultPayload,
    EmailAnalysisFailurePayload,
    EmailAnalysisPayload,
    EmailInboundPayload,
    EffectiveParametersReportPayload,
    Environment,
    GovernanceError,
    IngestEventPayload,
    MutantEvaluationPayload,
    PolicyUpdatePayload,
    RecordType,
    RiskScorePayload,
    SyntheticAttackCasePayload,
    SyntheticEmailAttackCasePayload,
    TwoChannelConfirmationPayload,
    VendorBaselineAuditPayload,
    WeaknessReportPayload,
    WorkflowTriggerPayload,
    append_record,
    validate_record_against_registry,
)
from .registry import build_default_registry


@dataclass(frozen=True)
class RouteContext:
    blackboard_root: Path
    registry: dict[str, AgentRegistryEntry] = field(default_factory=build_default_registry)


@dataclass(frozen=True)
class RouteResult:
    record: BlackboardRecord
    path: Path


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    if not cleaned:
        raise ValueError("tenant_id cannot resolve to an empty storage name")
    return cleaned


def blackboard_path(root: Path, environment: Environment, tenant_id: str) -> Path:
    return root / environment.value / f"{_safe_name(tenant_id)}.jsonl"


def _agent_for(context: RouteContext, agent_id: str) -> AgentRegistryEntry:
    try:
        return context.registry[agent_id]
    except KeyError as exc:
        raise GovernanceError(f"unknown agent: {agent_id}") from exc


def _write_record(context: RouteContext, record: BlackboardRecord) -> RouteResult:
    agent = _agent_for(context, record.source_agent)
    validate_record_against_registry(record, agent)
    path = blackboard_path(context.blackboard_root, record.environment, record.tenant_id)
    append_record(path, record)
    return RouteResult(record=record, path=path)


def submit_ingest_event(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: IngestEventPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.INGEST_EVENT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_detection_result(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: DetectionResultPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.DETECTION_RESULT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_risk_score(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: RiskScorePayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.RISK_SCORE,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def trigger_workflow(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: WorkflowTriggerPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.WORKFLOW_TRIGGER,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_audit_verdict(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: AuditVerdictPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.AUDIT_VERDICT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_weakness_report(
    context: RouteContext,
    *,
    source_agent: str,
    payload: WeaknessReportPayload,
    sandbox_tenant_id: str = "sandbox_default",
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=sandbox_tenant_id,
        environment=Environment.SANDBOX,
        record_type=RecordType.WEAKNESS_REPORT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_synthetic_attack_case(
    context: RouteContext,
    *,
    source_agent: str,
    payload: SyntheticAttackCasePayload,
    sandbox_tenant_id: str = "sandbox_default",
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=sandbox_tenant_id,
        environment=Environment.SANDBOX,
        record_type=RecordType.SYNTHETIC_ATTACK_CASE,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_synthetic_email_attack_case(
    context: RouteContext,
    *,
    source_agent: str,
    payload: SyntheticEmailAttackCasePayload,
    sandbox_tenant_id: str = "sandbox_default",
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    """Append one Phase 1.3 ``synthetic_email_attack_case`` record.

    Sandbox-only by construction: the underlying model validator already
    forbids real-looking domains in ``inbound.sender`` / ``inbound.recipient``
    (must end with ``.example`` / ``.test`` / ``.invalid``), and the registry
    pin (``allowed_environments={Environment.SANDBOX}``) plus the
    payload-level governance check in ``validate_record_against_registry``
    keep the record out of production blackboards.
    """

    record = BlackboardRecord(
        tenant_id=sandbox_tenant_id,
        environment=Environment.SANDBOX,
        record_type=RecordType.SYNTHETIC_EMAIL_ATTACK_CASE,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_mutant_evaluation(
    context: RouteContext,
    *,
    source_agent: str,
    payload: MutantEvaluationPayload,
    sandbox_tenant_id: str = "sandbox_default",
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=sandbox_tenant_id,
        environment=Environment.SANDBOX,
        record_type=RecordType.MUTANT_EVALUATION,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_policy_update(
    context: RouteContext,
    *,
    source_agent: str,
    payload: PolicyUpdatePayload,
    signature_id: str,
    sandbox_tenant_id: str = "sandbox_default",
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    """Append one signed sandbox ``policy_update`` record.

    The signed ``payload`` already carries ``target_production_tenant_id``
    (Pydantic default ``"tenant_demo"``). Callers wanting a non-demo target
    set that field explicitly on the payload before signing; the mutation
    engine and rollback module do this for their callers automatically.
    The promotion pipeline and Guardrail 11 gate re-verify the signature
    after reading this record back, so the field is tamper-evident.
    """

    record = BlackboardRecord(
        tenant_id=sandbox_tenant_id,
        environment=Environment.SANDBOX,
        record_type=RecordType.POLICY_UPDATE,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
        audit=AuditMeta(
            status=AuditStatus.APPROVED,
            auditor=source_agent,
            signed=True,
            signature_id=signature_id,
            reviewed_at=datetime.now().astimezone(),
        ),
    )
    return _write_record(context, record)


def submit_email_inbound(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: EmailInboundPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.EMAIL_INBOUND,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_email_analysis(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: EmailAnalysisPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.EMAIL_ANALYSIS,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_email_analysis_failure(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: EmailAnalysisFailurePayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.EMAIL_ANALYSIS_FAILURE,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_daily_digest(
    context: RouteContext,
    *,
    tenant_id: str,
    environment: Environment,
    source_agent: str,
    payload: DailyDigestPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=environment,
        record_type=RecordType.DAILY_DIGEST,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_effective_parameters_report(
    context: RouteContext,
    *,
    tenant_id: str,
    source_agent: str,
    payload: EffectiveParametersReportPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        record_type=RecordType.EFFECTIVE_PARAMETERS_REPORT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_vendor_baseline_audit(
    context: RouteContext,
    *,
    tenant_id: str,
    source_agent: str,
    payload: VendorBaselineAuditPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        record_type=RecordType.VENDOR_BASELINE_AUDIT,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)


def submit_two_channel_confirmation(
    context: RouteContext,
    *,
    tenant_id: str,
    source_agent: str,
    payload: TwoChannelConfirmationPayload,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
) -> RouteResult:
    record = BlackboardRecord(
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        record_type=RecordType.TWO_CHANNEL_CONFIRMATION,
        source_agent=source_agent,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
        payload=payload.model_dump(mode="json"),
    )
    return _write_record(context, record)
