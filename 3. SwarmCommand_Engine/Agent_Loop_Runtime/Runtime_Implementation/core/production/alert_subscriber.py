"""Policy regression alert subscriber.

Closes the loop from "operator/detector raises an alert" to "sandbox-signed
rollback flows through the same Guardrail 11 gate as any other apply."

The subscriber is intentionally not a regression *detector*. It is the
consumer of a specific record type: an ``audit_001.audit_verdict`` with
``workflow_id="policy_regression_alert"``, ``verdict=REJECTED``, and
``target_record_id`` pointing at the **most-recent** ``policy_applied`` audit
verdict for the tenant.

Wiring:

- ``emit_regression_alert`` is the operator/automation-facing helper that
  produces one alert verdict.
- ``find_unconsumed_alerts`` scans production for **valid** unconsumed alerts.
- ``run_alert_subscriber_cycle`` processes each unconsumed alert: validates
  provenance and target integrity, signs a rollback to the previous applied
  state via the existing rollback primitive, then writes a consumption marker
  (``workflow_id="regression_alert_consumed"``) so the same alert is never
  reprocessed. Invalid alerts are dead-lettered with a skip marker.

This module touches only the existing allowed surfaces (operational
``audit_001`` telemetry + the sandbox ``policy_update`` produced by
``request_rollback_to_previous``). Guardrail 11's write-surface list is
unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    BlackboardRecord,
    Environment,
    RecordType,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import RouteContext, RouteResult, submit_audit_verdict
from core.orchestrator.routes import blackboard_path
from core.policy import SigningKey, request_rollback_to_previous

POLICY_APPLIED_WORKFLOW_ID = "policy_applied"


@dataclass(frozen=True)
class AlertSubscriberConfig:
    production_tenant_id: str = "tenant_demo"
    sandbox_tenant_id: str = "sandbox_default"
    alert_workflow_id: str = "policy_regression_alert"
    consumed_workflow_id: str = "regression_alert_consumed"
    alert_agent_id: str = "audit_001"
    signing_key: SigningKey | None = None


@dataclass(frozen=True)
class AlertSubscriptionItem:
    alert_record_id: UUID
    triggered_rollback: bool
    rollback_record_id: UUID | None
    consumption_marker_id: UUID
    skip_reason: str | None


@dataclass(frozen=True)
class AlertSubscriptionResult:
    scanned: int
    triggered: int
    skipped: int
    items: list[AlertSubscriptionItem]


def _latest_policy_applied_audit(
    records: list[BlackboardRecord],
) -> BlackboardRecord | None:
    candidates = [
        record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == POLICY_APPLIED_WORKFLOW_ID
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda record: record.created_at)


def _policy_applied_by_id(records: list[BlackboardRecord]) -> dict[UUID, BlackboardRecord]:
    return {
        record.record_id: record
        for record in records
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.workflow_id == POLICY_APPLIED_WORKFLOW_ID
    }


def _classify_alert(
    alert: BlackboardRecord,
    *,
    records: list[BlackboardRecord],
    config: AlertSubscriberConfig,
) -> tuple[bool, str | None]:
    """Return (is_valid, skip_reason). Valid alerts have skip_reason None."""

    if alert.source_agent != config.alert_agent_id:
        return False, f"invalid alert source_agent: {alert.source_agent}"

    try:
        payload = AuditVerdictPayload.model_validate(alert.payload)
    except Exception:
        return False, "invalid alert payload"

    if payload.verdict != AuditStatus.REJECTED:
        return False, f"invalid alert verdict: {payload.verdict.value}"

    policy_applied_by_id = _policy_applied_by_id(records)
    if payload.target_record_id not in policy_applied_by_id:
        return False, "alert target is not a policy_applied audit"

    latest_applied = _latest_policy_applied_audit(records)
    if latest_applied is None:
        return False, "no policy_applied audit exists"

    if payload.target_record_id != latest_applied.record_id:
        return False, "stale policy_applied target (not most recent apply)"

    return True, None


def emit_regression_alert(
    context: RouteContext,
    *,
    reason: str,
    severity: str = "high",
    config: AlertSubscriberConfig | None = None,
) -> RouteResult:
    """Write one ``policy_regression_alert`` audit verdict targeting the
    most-recent ``policy_applied`` audit for this tenant.

    Raises ``ValueError`` if no policy was ever applied (there is nothing
    to flag as regressive).
    """

    config = config or AlertSubscriberConfig()
    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, config.production_tenant_id
    )
    records = read_records(production_path)
    latest_applied = _latest_policy_applied_audit(records)
    if latest_applied is None:
        raise ValueError(
            "no policy_applied audit to flag - cannot emit a regression alert "
            "before any policy has been applied"
        )

    return submit_audit_verdict(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.alert_agent_id,
        workflow_id=config.alert_workflow_id,
        parent_record_id=latest_applied.record_id,
        payload=AuditVerdictPayload(
            target_record_id=latest_applied.record_id,
            verdict=AuditStatus.REJECTED,
            findings=[f"severity={severity}", f"reason={reason}"],
            requires_human_review=False,
        ),
    )


def find_unconsumed_alerts(
    context: RouteContext,
    *,
    config: AlertSubscriberConfig | None = None,
) -> list[BlackboardRecord]:
    """Return valid unconsumed alerts, oldest first.

    Only alerts that pass provenance and target-integrity checks are returned.
    Invalid alerts are not actionable and are excluded from this list.
    """

    config = config or AlertSubscriberConfig()
    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, config.production_tenant_id
    )
    records = read_records(production_path)

    alerts: list[BlackboardRecord] = []
    consumed: set[UUID] = set()
    for record in records:
        if record.record_type != RecordType.AUDIT_VERDICT:
            continue
        if record.workflow_id == config.alert_workflow_id:
            alerts.append(record)
        elif record.workflow_id == config.consumed_workflow_id:
            if record.parent_record_id is not None:
                consumed.add(record.parent_record_id)

    valid_unconsumed: list[BlackboardRecord] = []
    for alert in alerts:
        if alert.record_id in consumed:
            continue
        is_valid, _ = _classify_alert(alert, records=records, config=config)
        if is_valid:
            valid_unconsumed.append(alert)

    valid_unconsumed.sort(key=lambda alert: alert.created_at)
    return valid_unconsumed


def run_alert_subscriber_cycle(
    context: RouteContext,
    *,
    config: AlertSubscriberConfig | None = None,
) -> AlertSubscriptionResult:
    """Process every unconsumed alert workflow record.

    Valid alerts (``audit_001``, ``REJECTED``, target is the most-recent
    ``policy_applied`` audit) may trigger ``request_rollback_to_previous``.
    Invalid alerts are dead-lettered with a consumption marker and never
    trigger rollback.
    """

    config = config or AlertSubscriberConfig()

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, config.production_tenant_id
    )
    records = read_records(production_path)

    alerts: list[BlackboardRecord] = []
    consumed: set[UUID] = set()
    for record in records:
        if record.record_type != RecordType.AUDIT_VERDICT:
            continue
        if record.workflow_id == config.alert_workflow_id:
            alerts.append(record)
        elif record.workflow_id == config.consumed_workflow_id:
            if record.parent_record_id is not None:
                consumed.add(record.parent_record_id)

    items: list[AlertSubscriptionItem] = []
    for alert in sorted(alerts, key=lambda record: record.created_at):
        if alert.record_id in consumed:
            continue

        is_valid, skip_reason = _classify_alert(alert, records=records, config=config)
        if not is_valid:
            marker = _write_consumption_marker(
                context,
                config=config,
                alert=alert,
                rollback_record_id=None,
                skip_reason=skip_reason,
            )
            items.append(
                AlertSubscriptionItem(
                    alert_record_id=alert.record_id,
                    triggered_rollback=False,
                    rollback_record_id=None,
                    consumption_marker_id=marker.record.record_id,
                    skip_reason=skip_reason,
                )
            )
            continue

        rollback_result = request_rollback_to_previous(
            context,
            production_tenant_id=config.production_tenant_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            alert_reason=f"regression alert {alert.record_id}",
            signing_key=config.signing_key,
        )

        if rollback_result is None:
            marker = _write_consumption_marker(
                context,
                config=config,
                alert=alert,
                rollback_record_id=None,
                skip_reason="no previous applied state",
            )
            items.append(
                AlertSubscriptionItem(
                    alert_record_id=alert.record_id,
                    triggered_rollback=False,
                    rollback_record_id=None,
                    consumption_marker_id=marker.record.record_id,
                    skip_reason="no previous applied state",
                )
            )
            continue

        marker = _write_consumption_marker(
            context,
            config=config,
            alert=alert,
            rollback_record_id=rollback_result.record.record_id,
            skip_reason=None,
        )
        items.append(
            AlertSubscriptionItem(
                alert_record_id=alert.record_id,
                triggered_rollback=True,
                rollback_record_id=rollback_result.record.record_id,
                consumption_marker_id=marker.record.record_id,
                skip_reason=None,
            )
        )

    triggered = sum(1 for item in items if item.triggered_rollback)
    skipped = len(items) - triggered
    return AlertSubscriptionResult(
        scanned=len(items),
        triggered=triggered,
        skipped=skipped,
        items=items,
    )


def _write_consumption_marker(
    context: RouteContext,
    *,
    config: AlertSubscriberConfig,
    alert: BlackboardRecord,
    rollback_record_id: UUID | None,
    skip_reason: str | None,
) -> RouteResult:
    findings: list[str] = []
    if rollback_record_id is not None:
        findings.append(f"rollback_signed_in_sandbox={rollback_record_id}")
    if skip_reason is not None:
        findings.append(f"skip_reason={skip_reason}")
    if not findings:
        findings.append("regression_alert_consumed")

    return submit_audit_verdict(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.alert_agent_id,
        workflow_id=config.consumed_workflow_id,
        parent_record_id=alert.record_id,
        payload=AuditVerdictPayload(
            target_record_id=rollback_record_id or alert.record_id,
            verdict=AuditStatus.APPROVED,
            findings=findings,
            requires_human_review=skip_reason is not None,
        ),
    )
