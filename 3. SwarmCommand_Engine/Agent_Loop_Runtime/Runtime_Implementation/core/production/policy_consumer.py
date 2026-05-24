"""End-of-cycle consumer for ``apply_policy_update`` workflow triggers.

This module is the Blue loop's only point of contact with the Guardrail 11
gate. It scans for unconsumed ``apply_policy_update`` workflow triggers in
production, applies each through ``core.production_state.apply_signed_policy``,
and writes a ``policy_applied`` audit verdict via ``governance_001`` as the
consumption marker so the next cycle does not re-apply.

The only writes this module emits to production are:
- ``governance_001.audit_verdict``  (Guardrail 11 surface #1)

Mutations to ``production_state.policy.*`` happen exclusively through the
gate (surfaces #3 and #4).
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    BlackboardRecord,
    Environment,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import RouteContext, RouteResult, submit_audit_verdict
from core.orchestrator.routes import blackboard_path
from core.policy.signing import SigningKey
from core.production_state import (
    PolicyApplyResult,
    apply_signed_policy,
)

POLICY_PROMOTION_WORKFLOW_ID = "policy_promotion"
POLICY_APPLIED_WORKFLOW_ID = "policy_applied"
APPLY_POLICY_WORKFLOW_NAME = "apply_policy_update"


@dataclass(frozen=True)
class PolicyConsumerConfig:
    production_tenant_id: str = "tenant_demo"
    sandbox_tenant_id: str = "sandbox_default"
    governance_agent_id: str = "governance_001"
    signing_key: SigningKey | None = None


@dataclass(frozen=True)
class PolicyApplyItemResult:
    workflow_trigger_id: str
    apply_result: PolicyApplyResult
    applied_audit: RouteResult


@dataclass(frozen=True)
class PolicyConsumerResult:
    processed_count: int
    applied_count: int
    skipped_count: int
    item_results: list[PolicyApplyItemResult]


def _is_apply_trigger(record: BlackboardRecord) -> bool:
    return (
        record.record_type == RecordType.WORKFLOW_TRIGGER
        and record.workflow_id == POLICY_PROMOTION_WORKFLOW_ID
        and record.payload.get("workflow_name") == APPLY_POLICY_WORKFLOW_NAME
    )


def _already_applied_trigger_ids(records: list[BlackboardRecord]) -> set[UUID]:
    applied: set[UUID] = set()
    for record in records:
        if record.record_type != RecordType.AUDIT_VERDICT:
            continue
        if record.workflow_id != POLICY_APPLIED_WORKFLOW_ID:
            continue
        target = record.payload.get("target_record_id")
        if target is None:
            continue
        try:
            applied.add(UUID(str(target)))
        except ValueError:
            continue
    return applied


def find_unconsumed_apply_triggers(
    context: RouteContext, *, tenant_id: str
) -> list[BlackboardRecord]:
    """Return the production ``apply_policy_update`` triggers not yet applied."""

    path = blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant_id)
    records = read_records(path)
    applied = _already_applied_trigger_ids(records)
    return [
        record
        for record in records
        if _is_apply_trigger(record) and record.record_id not in applied
    ]


def apply_pending_policies(
    context: RouteContext,
    *,
    config: PolicyConsumerConfig | None = None,
) -> PolicyConsumerResult:
    """Consume all unconsumed apply triggers in this tenant's production log."""

    config = config or PolicyConsumerConfig()

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    pending = find_unconsumed_apply_triggers(
        context, tenant_id=config.production_tenant_id
    )

    item_results: list[PolicyApplyItemResult] = []
    applied = 0
    skipped = 0

    for trigger in pending:
        policy_record_target = _resolve_target_policy_id(context, config, trigger)
        requested_parameters = _resolve_requested_parameters(
            context, config, policy_record_target
        )

        apply_result = apply_signed_policy(
            blackboard_root=context.blackboard_root,
            production_tenant_id=config.production_tenant_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            workflow_trigger_id=trigger.record_id,
            requested_parameters=requested_parameters,
            signing_key=config.signing_key,
        )

        applied_audit = submit_audit_verdict(
            context,
            tenant_id=config.production_tenant_id,
            environment=Environment.PRODUCTION,
            source_agent=config.governance_agent_id,
            parent_record_id=trigger.record_id,
            workflow_id=POLICY_APPLIED_WORKFLOW_ID,
            payload=AuditVerdictPayload(
                target_record_id=trigger.record_id,
                verdict=AuditStatus.APPROVED,
                findings=[
                    f"applied policy {apply_result.new_state.active_version}",
                    f"state_changed={apply_result.changed}",
                ],
                requires_human_review=False,
            ),
        )

        item_results.append(
            PolicyApplyItemResult(
                workflow_trigger_id=str(trigger.record_id),
                apply_result=apply_result,
                applied_audit=applied_audit,
            )
        )

        if apply_result.changed:
            applied += 1
        else:
            skipped += 1

    return PolicyConsumerResult(
        processed_count=len(item_results),
        applied_count=applied,
        skipped_count=skipped,
        item_results=item_results,
    )


def _resolve_target_policy_id(
    context: RouteContext,
    config: PolicyConsumerConfig,
    trigger: BlackboardRecord,
) -> UUID:
    """Resolve the sandbox policy_update record id this trigger promotes.

    The trigger's parent is the production audit_verdict, whose
    ``target_record_id`` payload field is the sandbox policy_update id.
    """

    production_path = blackboard_path(
        context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    production_records = read_records(production_path)
    audit = next(
        (
            record
            for record in production_records
            if record.record_id == trigger.parent_record_id
            and record.record_type == RecordType.AUDIT_VERDICT
        ),
        None,
    )
    if audit is None or audit.payload.get("target_record_id") is None:
        raise ValueError("apply trigger does not reference a known audit verdict")
    return UUID(str(audit.payload["target_record_id"]))


def _resolve_requested_parameters(
    context: RouteContext,
    config: PolicyConsumerConfig,
    policy_record_id: UUID,
) -> dict | None:
    """Read the signed policy's `parameters` and forward them to the gate.

    Returning ``None`` lets the gate leave existing parameters untouched.
    Returning an empty dict explicitly resets them.
    """

    sandbox_path = blackboard_path(
        context.blackboard_root,
        Environment.SANDBOX,
        config.sandbox_tenant_id,
    )
    for record in read_records(sandbox_path):
        if record.record_id != policy_record_id:
            continue
        payload = PolicyUpdatePayload.model_validate(record.payload)
        return payload.parameters if payload.parameters else None
    return None
