"""Automated policy-regression detector.

This module is the first automated producer of ``policy_regression_alert``
records. It watches post-apply production telemetry and calls the existing
alert helper when the current active policy appears to have caused too many
alert-like outcomes.

It deliberately does not sign rollbacks or mutate ``production_state``. The
pipeline remains:

detector -> ``policy_regression_alert`` -> alert subscriber -> signed rollback
-> promotion pipeline -> Guardrail 11 gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    BlackboardRecord,
    DetectionResultPayload,
    Environment,
    RecordType,
    RiskScorePayload,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import RouteContext, RouteResult, submit_audit_verdict
from core.orchestrator.routes import blackboard_path

from .alert_subscriber import AlertSubscriberConfig, emit_regression_alert

POLICY_APPLIED_WORKFLOW_ID = "policy_applied"
REGRESSION_CHECKED_WORKFLOW_ID = "policy_regression_detector_checked"


@dataclass(frozen=True)
class RegressionDetectorConfig:
    production_tenant_id: str = "tenant_demo"
    detector_agent_id: str = "audit_001"
    minimum_samples: int = 3
    alert_ratio_threshold: float = 0.75
    risk_score_threshold: int = 85
    detection_confidence_threshold: float = 0.85
    checked_workflow_id: str = REGRESSION_CHECKED_WORKFLOW_ID


@dataclass(frozen=True)
class RegressionDetectorResult:
    evaluated_policy_applied_id: UUID | None
    sample_count: int
    alert_like_count: int
    alert_ratio: float
    emitted_alert: RouteResult | None
    check_marker: RouteResult | None
    skipped_reason: str | None


def run_regression_detector_cycle(
    context: RouteContext,
    *,
    config: RegressionDetectorConfig | None = None,
) -> RegressionDetectorResult:
    """Evaluate the most-recent applied policy for post-apply regressions.

    The detector is idempotent per ``policy_applied`` audit verdict: once a
    checked marker exists for that apply, later runs skip it. If there are not
    enough post-apply samples, no marker is written so more telemetry can
    accumulate before the next run.
    """

    config = config or RegressionDetectorConfig()

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    records = _production_records(context, config.production_tenant_id)
    latest_applied = _latest_policy_applied(records)
    if latest_applied is None:
        return _empty_result("no policy_applied audit exists")

    if _has_checked_marker(records, latest_applied.record_id, config):
        return RegressionDetectorResult(
            evaluated_policy_applied_id=latest_applied.record_id,
            sample_count=0,
            alert_like_count=0,
            alert_ratio=0.0,
            emitted_alert=None,
            check_marker=None,
            skipped_reason="policy apply already checked",
        )

    detections = _post_apply_detections(records, latest_applied)
    if len(detections) < config.minimum_samples:
        return RegressionDetectorResult(
            evaluated_policy_applied_id=latest_applied.record_id,
            sample_count=len(detections),
            alert_like_count=0,
            alert_ratio=0.0,
            emitted_alert=None,
            check_marker=None,
            skipped_reason="insufficient post-apply samples",
        )

    risks_by_detection_id = _post_apply_risks_by_detection_id(records, latest_applied)
    alert_like_count = sum(
        1
        for detection in detections
        if _is_alert_like(detection, risks_by_detection_id.get(detection.record_id), config)
    )
    alert_ratio = alert_like_count / len(detections)

    emitted_alert: RouteResult | None = None
    if alert_ratio >= config.alert_ratio_threshold:
        # Multi-tenant isolation: the detector evaluated the configured
        # production tenant's records, so the alert must target the same
        # tenant. Without an explicit AlertSubscriberConfig the default
        # is ``tenant_demo`` and a non-demo cycle would either fail
        # ("no policy_applied audit") or — worse — write the alert into
        # the demo tenant's blackboard. Spec:
        # ``Policy_Pipeline/multi-tenant-isolation-hardening.md`` §6.
        emitted_alert = emit_regression_alert(
            context,
            reason=(
                "automated regression detector: "
                f"{alert_like_count}/{len(detections)} post-apply samples "
                f"were alert-like (ratio={alert_ratio:.2f})"
            ),
            severity="high",
            config=AlertSubscriberConfig(
                production_tenant_id=config.production_tenant_id,
            ),
        )

    marker = _write_checked_marker(
        context,
        config=config,
        latest_applied=latest_applied,
        sample_count=len(detections),
        alert_like_count=alert_like_count,
        alert_ratio=alert_ratio,
        emitted_alert_id=emitted_alert.record.record_id if emitted_alert else None,
    )
    return RegressionDetectorResult(
        evaluated_policy_applied_id=latest_applied.record_id,
        sample_count=len(detections),
        alert_like_count=alert_like_count,
        alert_ratio=alert_ratio,
        emitted_alert=emitted_alert,
        check_marker=marker,
        skipped_reason=None,
    )


def _production_records(context: RouteContext, tenant_id: str) -> list[BlackboardRecord]:
    return read_records(blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant_id))


def _empty_result(skipped_reason: str) -> RegressionDetectorResult:
    return RegressionDetectorResult(
        evaluated_policy_applied_id=None,
        sample_count=0,
        alert_like_count=0,
        alert_ratio=0.0,
        emitted_alert=None,
        check_marker=None,
        skipped_reason=skipped_reason,
    )


def _latest_policy_applied(records: list[BlackboardRecord]) -> BlackboardRecord | None:
    applied = [
        record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == POLICY_APPLIED_WORKFLOW_ID
    ]
    if not applied:
        return None
    return max(applied, key=lambda record: record.created_at)


def _has_checked_marker(
    records: list[BlackboardRecord],
    policy_applied_id: UUID,
    config: RegressionDetectorConfig,
) -> bool:
    return any(
        record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == config.checked_workflow_id
        and record.parent_record_id == policy_applied_id
        for record in records
    )


def _post_apply_detections(
    records: list[BlackboardRecord],
    latest_applied: BlackboardRecord,
) -> list[BlackboardRecord]:
    detections = [
        record
        for record in records
        if record.record_type == RecordType.DETECTION_RESULT
        and record.created_at > latest_applied.created_at
    ]
    detections.sort(key=lambda record: record.created_at)
    return detections


def _post_apply_risks_by_detection_id(
    records: list[BlackboardRecord],
    latest_applied: BlackboardRecord,
) -> dict[UUID, BlackboardRecord]:
    risks: dict[UUID, BlackboardRecord] = {}
    for record in records:
        if record.record_type != RecordType.RISK_SCORE:
            continue
        if record.parent_record_id is None:
            continue
        if record.created_at <= latest_applied.created_at:
            continue
        risks[record.parent_record_id] = record
    return risks


def _is_alert_like(
    detection_record: BlackboardRecord,
    risk_record: BlackboardRecord | None,
    config: RegressionDetectorConfig,
) -> bool:
    detection = DetectionResultPayload.model_validate(detection_record.payload)
    if detection.confidence >= config.detection_confidence_threshold:
        return True
    if risk_record is None:
        return False
    risk = RiskScorePayload.model_validate(risk_record.payload)
    return risk.score >= config.risk_score_threshold


def _write_checked_marker(
    context: RouteContext,
    *,
    config: RegressionDetectorConfig,
    latest_applied: BlackboardRecord,
    sample_count: int,
    alert_like_count: int,
    alert_ratio: float,
    emitted_alert_id: UUID | None,
) -> RouteResult:
    findings = [
        f"sample_count={sample_count}",
        f"alert_like_count={alert_like_count}",
        f"alert_ratio={alert_ratio:.4f}",
        f"threshold={config.alert_ratio_threshold:.4f}",
    ]
    if emitted_alert_id is not None:
        findings.append(f"emitted_alert_id={emitted_alert_id}")

    return submit_audit_verdict(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.detector_agent_id,
        workflow_id=config.checked_workflow_id,
        parent_record_id=latest_applied.record_id,
        payload=AuditVerdictPayload(
            target_record_id=latest_applied.record_id,
            verdict=(
                AuditStatus.REJECTED
                if emitted_alert_id is not None
                else AuditStatus.APPROVED
            ),
            findings=findings,
            requires_human_review=False,
        ),
    )
