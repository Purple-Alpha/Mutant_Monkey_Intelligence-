"""Policy rollback primitive — sandbox-signed revert via the same pipeline.

A rollback is just a sandbox ``policy_update`` record with ``is_rollback=True``.
It flows through the same signing → promotion → Guardrail 11 gate → consumer
pipeline as a forward apply. The gate adds one extra check: the target
``(policy_name, parameters)`` must match a state previously applied to this
tenant per the production audit log.

This module exposes three call sites:

- ``sign_rollback_request`` — sign and submit one rollback policy_update.
- ``applied_state_history`` — derive the ordered list of previously applied
  states from the production audit chain (the source of truth).
- ``request_rollback_to_previous`` — convenience that picks the
  second-most-recent applied state and signs a rollback for it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from core.blackboard import (
    BlackboardRecord,
    Environment,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import RouteContext, RouteResult, submit_policy_update
from core.orchestrator.routes import blackboard_path

from .signing import SigningKey, default_signing_key, sign

POLICY_APPLIED_WORKFLOW_ID = "policy_applied"


@dataclass(frozen=True)
class AppliedState:
    sandbox_policy_record_id: UUID
    policy_name: str
    parameters: dict[str, Any]
    applied_audit_created_at: datetime


def sign_rollback_request(
    context: RouteContext,
    *,
    target_policy_name: str,
    target_parameters: dict[str, Any],
    alert_reason: str,
    rollback_plan: str = "Revert to previously-applied production policy on alert.",
    source_agent: str = "governance_001",
    sandbox_tenant_id: str = "sandbox_default",
    target_production_tenant_id: str = "tenant_demo",
    signing_key: SigningKey | None = None,
) -> RouteResult:
    """Sign and submit one rollback ``policy_update`` to sandbox.

    The signature is computed over the full canonical payload including
    ``is_rollback=True`` and ``target_production_tenant_id``, so any tamper
    before promotion is caught by the pipeline's signature re-verification.
    """

    payload = PolicyUpdatePayload(
        policy_name=target_policy_name,
        change_summary=(
            f"Rollback to previously-applied policy {target_policy_name!r}. "
            f"Alert reason: {alert_reason}"
        ),
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan=rollback_plan,
        parameters=dict(target_parameters),
        is_rollback=True,
        target_production_tenant_id=target_production_tenant_id,
    )
    key = signing_key or default_signing_key()
    signature_id = sign(payload.model_dump(mode="json"), source_agent, key)
    return submit_policy_update(
        context,
        source_agent=source_agent,
        payload=payload,
        signature_id=signature_id,
        sandbox_tenant_id=sandbox_tenant_id,
    )


def applied_state_history(
    context: RouteContext,
    *,
    production_tenant_id: str,
    sandbox_tenant_id: str = "sandbox_default",
) -> list[AppliedState]:
    """Return the ordered list of states applied to ``production_tenant_id``.

    Ordered by the ``created_at`` of the ``policy_applied`` audit verdict
    that consumed the apply trigger, oldest first. This is the canonical
    history view — the production audit log is the source of truth.
    """

    production_records = read_records(
        blackboard_path(context.blackboard_root, Environment.PRODUCTION, production_tenant_id)
    )
    sandbox_records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, sandbox_tenant_id)
    )
    sandbox_by_id = {record.record_id: record for record in sandbox_records}
    production_by_id = {record.record_id: record for record in production_records}

    history: list[AppliedState] = []
    for applied_audit in sorted(production_records, key=lambda r: r.created_at):
        if applied_audit.record_type != RecordType.AUDIT_VERDICT:
            continue
        if applied_audit.workflow_id != POLICY_APPLIED_WORKFLOW_ID:
            continue
        applied_state = _resolve_applied_state(
            applied_audit, production_by_id, sandbox_by_id
        )
        if applied_state is not None:
            history.append(applied_state)
    return history


def _resolve_applied_state(
    applied_audit: BlackboardRecord,
    production_by_id: dict[UUID, BlackboardRecord],
    sandbox_by_id: dict[UUID, BlackboardRecord],
) -> AppliedState | None:
    trigger_id = applied_audit.parent_record_id
    if trigger_id is None:
        return None
    trigger = production_by_id.get(trigger_id)
    if trigger is None or trigger.record_type != RecordType.WORKFLOW_TRIGGER:
        return None
    boundary_audit = (
        production_by_id.get(trigger.parent_record_id) if trigger.parent_record_id else None
    )
    if boundary_audit is None or boundary_audit.record_type != RecordType.AUDIT_VERDICT:
        return None
    target_raw = boundary_audit.payload.get("target_record_id")
    if target_raw is None:
        return None
    try:
        sandbox_id = UUID(str(target_raw))
    except ValueError:
        return None
    sandbox_policy = sandbox_by_id.get(sandbox_id)
    if sandbox_policy is None:
        return None
    try:
        payload = PolicyUpdatePayload.model_validate(sandbox_policy.payload)
    except Exception:
        return None
    return AppliedState(
        sandbox_policy_record_id=sandbox_id,
        policy_name=payload.policy_name,
        parameters=dict(payload.parameters),
        applied_audit_created_at=applied_audit.created_at,
    )


def request_rollback_to_previous(
    context: RouteContext,
    *,
    production_tenant_id: str,
    sandbox_tenant_id: str = "sandbox_default",
    alert_reason: str,
    signing_key: SigningKey | None = None,
) -> RouteResult | None:
    """Sign a rollback to the second-most-recent applied state.

    Returns ``None`` if the applied-state history has fewer than two entries
    (no "previous" to revert to). On success returns the route result for
    the newly-created sandbox rollback ``policy_update`` record, ready for
    the promotion pipeline to pick up on its next run.

    Note: repeated calls oscillate (B -> A -> B -> A). See the spec at
    ``Policy_Pipeline/policy-rollback-primitive.md``.
    """

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    history = applied_state_history(
        context,
        production_tenant_id=production_tenant_id,
        sandbox_tenant_id=sandbox_tenant_id,
    )
    if len(history) < 2:
        return None

    previous = history[-2]
    return sign_rollback_request(
        context,
        target_policy_name=previous.policy_name,
        target_parameters=previous.parameters,
        alert_reason=alert_reason,
        sandbox_tenant_id=sandbox_tenant_id,
        target_production_tenant_id=production_tenant_id,
        signing_key=signing_key,
    )
