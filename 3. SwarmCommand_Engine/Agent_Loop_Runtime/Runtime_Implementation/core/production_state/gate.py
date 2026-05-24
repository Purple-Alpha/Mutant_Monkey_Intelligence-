"""Governance gate for ``production_state`` writes.

Implements Guardrail 11: the Blue loop's only governance-level mutations to
``production_state`` are ``policy.active_version`` and ``policy.parameters``,
and only when authorized by a signed ``apply_policy_update`` workflow
trigger that was emitted by ``orchestrator_001`` and chained from a
``governance_001`` policy-promotion audit.

Any other path into the state object is a governance violation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from core.blackboard import (
    AuditStatus,
    BlackboardRecord,
    Environment,
    GovernanceError,
    PolicyUpdatePayload,
    RecordType,
    WorkflowTriggerPayload,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator.routes import blackboard_path
from core.policy.signing import SigningKey, default_signing_key, verify

from .parameter_keys import unauthorized_parameter_keys
from .state import ProductionPolicyState, load_state, save_state, state_path, with_changes

POLICY_PROMOTION_WORKFLOW_ID = "policy_promotion"
APPLY_POLICY_WORKFLOW_NAME = "apply_policy_update"
ALLOWED_GOVERNANCE_AGENTS = frozenset({"governance_001"})
ALLOWED_ORCHESTRATOR_AGENTS = frozenset({"orchestrator_001"})


@dataclass(frozen=True)
class PolicyApplyEvidence:
    """The records that justify one production_state mutation."""

    workflow_trigger: BlackboardRecord
    production_audit_verdict: BlackboardRecord
    sandbox_policy_update: BlackboardRecord


@dataclass(frozen=True)
class PolicyApplyResult:
    previous_state: ProductionPolicyState
    new_state: ProductionPolicyState
    evidence: PolicyApplyEvidence
    changed: bool


def _find_workflow_trigger(records: list[BlackboardRecord], record_id: UUID) -> BlackboardRecord:
    for record in records:
        if record.record_id == record_id and record.record_type == RecordType.WORKFLOW_TRIGGER:
            return record
    raise GovernanceError(f"workflow_trigger {record_id} not found in production blackboard")


def _find_audit_verdict(records: list[BlackboardRecord], record_id: UUID) -> BlackboardRecord:
    for record in records:
        if record.record_id == record_id and record.record_type == RecordType.AUDIT_VERDICT:
            return record
    raise GovernanceError(f"audit_verdict {record_id} not found in production blackboard")


def _find_sandbox_policy(records: list[BlackboardRecord], record_id: UUID) -> BlackboardRecord:
    for record in records:
        if record.record_id == record_id and record.record_type == RecordType.POLICY_UPDATE:
            return record
    raise GovernanceError(f"policy_update {record_id} not found in sandbox blackboard")


def gather_evidence(
    *,
    blackboard_root,
    production_tenant_id: str,
    sandbox_tenant_id: str,
    workflow_trigger_id: UUID,
) -> PolicyApplyEvidence:
    """Walk the audit chain backwards from the workflow_trigger to the sandbox policy.

    This is the *only* way the gate accepts an apply request: the caller hands
    in the production workflow_trigger record id, and the gate proves the chain
    by reading the blackboard itself.
    """

    production_records = read_records(
        blackboard_path(blackboard_root, Environment.PRODUCTION, production_tenant_id)
    )
    workflow = _find_workflow_trigger(production_records, workflow_trigger_id)

    if workflow.source_agent not in ALLOWED_ORCHESTRATOR_AGENTS:
        raise GovernanceError(
            f"workflow_trigger must come from {sorted(ALLOWED_ORCHESTRATOR_AGENTS)}, "
            f"got {workflow.source_agent}"
        )
    if workflow.workflow_id != POLICY_PROMOTION_WORKFLOW_ID:
        raise GovernanceError(
            f"workflow_trigger.workflow_id must be {POLICY_PROMOTION_WORKFLOW_ID!r}"
        )
    if workflow.payload.get("workflow_name") != APPLY_POLICY_WORKFLOW_NAME:
        raise GovernanceError(
            f"workflow_trigger must be a {APPLY_POLICY_WORKFLOW_NAME!r} trigger"
        )
    if workflow.parent_record_id is None:
        raise GovernanceError("workflow_trigger has no parent audit_verdict")

    audit = _find_audit_verdict(production_records, workflow.parent_record_id)
    if audit.source_agent not in ALLOWED_GOVERNANCE_AGENTS:
        raise GovernanceError(
            f"audit_verdict must come from {sorted(ALLOWED_GOVERNANCE_AGENTS)}, "
            f"got {audit.source_agent}"
        )
    if audit.payload.get("verdict") != AuditStatus.APPROVED.value:
        raise GovernanceError("audit_verdict must be APPROVED")
    target_raw = audit.payload.get("target_record_id")
    if target_raw is None:
        raise GovernanceError("audit_verdict has no target_record_id")
    sandbox_policy_id = UUID(str(target_raw))

    sandbox_records = read_records(
        blackboard_path(blackboard_root, Environment.SANDBOX, sandbox_tenant_id)
    )
    sandbox_policy = _find_sandbox_policy(sandbox_records, sandbox_policy_id)
    if not sandbox_policy.audit.signed:
        raise GovernanceError("sandbox policy_update is not signed")

    return PolicyApplyEvidence(
        workflow_trigger=workflow,
        production_audit_verdict=audit,
        sandbox_policy_update=sandbox_policy,
    )


def _next_state(
    current: ProductionPolicyState,
    policy_payload: PolicyUpdatePayload,
    requested_parameters: dict[str, Any] | None,
) -> ProductionPolicyState:
    new_version = policy_payload.policy_name
    if requested_parameters is None:
        return with_changes(current, active_version=new_version)
    return with_changes(
        current, active_version=new_version, parameters=requested_parameters
    )


def apply_signed_policy(
    *,
    blackboard_root,
    production_tenant_id: str = "tenant_demo",
    sandbox_tenant_id: str = "sandbox_default",
    workflow_trigger_id: UUID,
    requested_parameters: dict[str, Any] | None = None,
    signing_key: SigningKey | None = None,
) -> PolicyApplyResult:
    """Apply a signed sandbox policy to ``production_state`` (Guardrail 11).

    This is the *only* function authorized to mutate ``production_state``.
    It re-verifies the HMAC signature on the sandbox policy_update record
    before mutating, so a forged audit chain cannot promote an unsigned
    candidate.
    """

    kill_switch_state = is_kill_switch_engaged(
        blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    evidence = gather_evidence(
        blackboard_root=blackboard_root,
        production_tenant_id=production_tenant_id,
        sandbox_tenant_id=sandbox_tenant_id,
        workflow_trigger_id=workflow_trigger_id,
    )

    key = signing_key or default_signing_key()
    sandbox_policy = evidence.sandbox_policy_update
    if not verify(
        sandbox_policy.payload,
        sandbox_policy.source_agent,
        sandbox_policy.audit.signature_id or "",
        key,
    ):
        raise GovernanceError("sandbox policy_update signature failed re-verification at gate")

    policy_payload = PolicyUpdatePayload.model_validate(sandbox_policy.payload)
    WorkflowTriggerPayload.model_validate(evidence.workflow_trigger.payload)

    # Phase 1.4 §11 decision 2 — defense-in-depth parameter-key reservation.
    # Reject any unauthorized key BOTH on the signed payload's
    # ``parameters`` dict AND on the caller's ``requested_parameters``
    # kwarg. Placed AFTER signature re-verification (a tampered key
    # already gets caught there) and BEFORE the cross-tenant defense so
    # an unauthorized key never gets compared to the tenant. Mirrors the
    # spec's "BOTH boundaries" lockdown: the promotion pipeline rejects
    # the same key class sandbox-side before it ever crosses into
    # production; this gate is the final inner check.
    payload_unauthorized = unauthorized_parameter_keys(policy_payload.parameters)
    if payload_unauthorized:
        raise GovernanceError(
            "unauthorized parameter key: "
            + ", ".join(payload_unauthorized)
            + " (signed payload)"
        )
    if requested_parameters is not None:
        requested_unauthorized = unauthorized_parameter_keys(requested_parameters)
        if requested_unauthorized:
            raise GovernanceError(
                "unauthorized parameter key: "
                + ", ".join(requested_unauthorized)
                + " (requested_parameters)"
            )

    # Cross-tenant defense in depth (spec section 3). Even if the promotion
    # pipeline missed it, the gate refuses any signed policy whose
    # ``target_production_tenant_id`` does not match the production tenant
    # the gate was invoked with. Placed AFTER signature re-verification and
    # BEFORE the rollback-history check per the multi-tenant hardening
    # spec; the outer kill-switch check still runs first.
    if policy_payload.target_production_tenant_id != production_tenant_id:
        raise GovernanceError(
            "cross-tenant promotion attempt: policy targets "
            f"{policy_payload.target_production_tenant_id}, "
            f"gate invoked with {production_tenant_id}"
        )

    if policy_payload.is_rollback:
        target_parameters = (
            requested_parameters
            if requested_parameters is not None
            else policy_payload.parameters
        )
        if not _rollback_target_is_in_history(
            blackboard_root=blackboard_root,
            production_tenant_id=production_tenant_id,
            sandbox_tenant_id=sandbox_tenant_id,
            target_policy_name=policy_payload.policy_name,
            target_parameters=target_parameters,
        ):
            raise GovernanceError(
                "rollback target not in applied-state history for this tenant"
            )

    path = state_path(blackboard_root, production_tenant_id)
    previous = load_state(path)

    if previous.active_version == policy_payload.policy_name and requested_parameters is None:
        return PolicyApplyResult(
            previous_state=previous,
            new_state=previous,
            evidence=evidence,
            changed=False,
        )

    new_state = _next_state(previous, policy_payload, requested_parameters)
    save_state(path, new_state)
    return PolicyApplyResult(
        previous_state=previous,
        new_state=new_state,
        evidence=evidence,
        changed=True,
    )


POLICY_APPLIED_WORKFLOW_ID = "policy_applied"


def _rollback_target_is_in_history(
    *,
    blackboard_root,
    production_tenant_id: str,
    sandbox_tenant_id: str,
    target_policy_name: str,
    target_parameters: dict[str, Any],
) -> bool:
    """Return True iff (target_policy_name, target_parameters) matches a state
    that was previously applied to ``production_tenant_id`` per the audit chain.

    The chain is, for each ``policy_applied`` audit verdict in the production
    log: audit_verdict -> workflow_trigger (parent) -> boundary audit_verdict
    (parent of trigger) -> sandbox policy_update (boundary's target_record_id).
    """

    production_records = read_records(
        blackboard_path(blackboard_root, Environment.PRODUCTION, production_tenant_id)
    )
    sandbox_records = read_records(
        blackboard_path(blackboard_root, Environment.SANDBOX, sandbox_tenant_id)
    )
    sandbox_by_id = {record.record_id: record for record in sandbox_records}
    production_by_id = {record.record_id: record for record in production_records}

    for applied_audit in production_records:
        if applied_audit.record_type != RecordType.AUDIT_VERDICT:
            continue
        if applied_audit.workflow_id != POLICY_APPLIED_WORKFLOW_ID:
            continue
        trigger_id = applied_audit.parent_record_id
        if trigger_id is None:
            continue
        trigger = production_by_id.get(trigger_id)
        if trigger is None or trigger.record_type != RecordType.WORKFLOW_TRIGGER:
            continue
        boundary_audit = production_by_id.get(trigger.parent_record_id) if trigger.parent_record_id else None
        if boundary_audit is None or boundary_audit.record_type != RecordType.AUDIT_VERDICT:
            continue
        target_raw = boundary_audit.payload.get("target_record_id")
        if target_raw is None:
            continue
        try:
            sandbox_id = UUID(str(target_raw))
        except ValueError:
            continue
        sandbox_policy = sandbox_by_id.get(sandbox_id)
        if sandbox_policy is None:
            continue
        try:
            applied = PolicyUpdatePayload.model_validate(sandbox_policy.payload)
        except Exception:
            continue
        if applied.policy_name == target_policy_name and dict(applied.parameters) == dict(
            target_parameters
        ):
            return True
    return False
