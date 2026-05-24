"""Policy Update Signing and Promotion Pipeline.

The pipeline is the only path by which a sandbox-issued, signed
``policy_update`` reaches production. It does three things and nothing else:

1. Verifies each sandbox policy update's HMAC-SHA256 signature.
2. Writes a re-audit ``audit_verdict`` at the boundary
   (REJECTED in sandbox if verification fails; APPROVED in production if it
   passes) so the audit trail crosses environments.
3. Emits one production ``workflow_trigger`` per approved promotion so the
   production loop can act on it on its next cycle.

The pipeline never mutates an agent, never edits an existing record, and is
idempotent: re-running with the same inputs is a no-op.
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
    WorkflowTriggerPayload,
    read_records,
)
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_audit_verdict,
    trigger_workflow,
)
from core.orchestrator.routes import blackboard_path
from core.production_state.parameter_keys import unauthorized_parameter_keys

from .signing import SigningKey, default_signing_key, verify
from .rollback import applied_state_history


@dataclass(frozen=True)
class PolicyPromotionConfig:
    sandbox_tenant_id: str = "sandbox_default"
    production_tenant_id: str = "tenant_demo"
    governance_agent_id: str = "governance_001"
    orchestrator_agent_id: str = "orchestrator_001"
    apply_workflow_name: str = "apply_policy_update"
    signing_key: SigningKey | None = None


@dataclass(frozen=True)
class PolicyPromotionItemResult:
    policy_update_record_id: str
    verification_passed: bool
    production_audit: RouteResult | None
    production_workflow_trigger: RouteResult | None
    sandbox_rejection_audit: RouteResult | None
    skipped_already_promoted: bool


@dataclass(frozen=True)
class PolicyPromotionResult:
    processed_count: int
    promoted_count: int
    rejected_count: int
    skipped_count: int
    item_results: list[PolicyPromotionItemResult]


def _load_signed_policy_updates(
    context: RouteContext, config: PolicyPromotionConfig
) -> list[BlackboardRecord]:
    path = blackboard_path(
        context.blackboard_root,
        Environment.SANDBOX,
        config.sandbox_tenant_id,
    )
    return [
        record
        for record in read_records(path)
        if record.record_type == RecordType.POLICY_UPDATE and record.audit.signed
    ]


def _already_promoted_ids(
    context: RouteContext, config: PolicyPromotionConfig
) -> set[UUID]:
    """Return the set of sandbox policy_update record_ids that already have a
    production-side promotion audit."""

    path = blackboard_path(
        context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    promoted: set[UUID] = set()
    for record in read_records(path):
        if record.record_type != RecordType.AUDIT_VERDICT:
            continue
        if record.workflow_id != "policy_promotion":
            continue
        target_raw = record.payload.get("target_record_id")
        if target_raw is None:
            continue
        try:
            promoted.add(UUID(str(target_raw)))
        except ValueError:
            continue
    return promoted


def _unauthorized_parameter_key_finding(unauthorized: tuple[str, ...]) -> str:
    """Audit-trail identifier for an unauthorized-parameter-key promotion attempt.

    Format mirrors the cross-tenant finding's machine-friendly shape so a
    log scraper can match on ``unauthorized_parameter_key=`` and recover the
    sorted offending keys. Per Matt's 2026-05-21 §11 decision 2 (defense
    in depth), the promotion pipeline rejects the same key class the
    Guardrail 11 gate would reject downstream, so the unauthorized key
    never crosses the production boundary.
    """

    return "unauthorized_parameter_key=" + ",".join(unauthorized)


def _cross_tenant_finding(config: PolicyPromotionConfig) -> str:
    """Audit-trail identifier for a cross-tenant promotion attempt.

    Format is spec-mandated (see
    ``Policy_Pipeline/multi-tenant-isolation-hardening.md`` section 2):

    ``cross_tenant_promotion_attempt={sandbox_tenant_id}->{production_tenant_id}``

    The tenant pair is the sandbox-side audit-log identifier of the
    rejected attempt; the policy's ``target_production_tenant_id`` is
    preserved verbatim in the signed payload for forensic recovery.
    """

    return (
        f"cross_tenant_promotion_attempt="
        f"{config.sandbox_tenant_id}->{config.production_tenant_id}"
    )


def _reject_in_sandbox(
    context: RouteContext,
    config: PolicyPromotionConfig,
    policy_update_record: BlackboardRecord,
    reason: str,
) -> RouteResult:
    return submit_audit_verdict(
        context,
        tenant_id=config.sandbox_tenant_id,
        environment=Environment.SANDBOX,
        source_agent=config.governance_agent_id,
        parent_record_id=policy_update_record.record_id,
        workflow_id="policy_promotion",
        payload=AuditVerdictPayload(
            target_record_id=policy_update_record.record_id,
            verdict=AuditStatus.REJECTED,
            findings=[reason],
            requires_human_review=True,
        ),
    )


def _approve_in_production(
    context: RouteContext,
    config: PolicyPromotionConfig,
    policy_update_record: BlackboardRecord,
    policy_payload: PolicyUpdatePayload,
) -> tuple[RouteResult, RouteResult]:
    audit = submit_audit_verdict(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.governance_agent_id,
        parent_record_id=policy_update_record.record_id,
        workflow_id="policy_promotion",
        payload=AuditVerdictPayload(
            target_record_id=policy_update_record.record_id,
            verdict=AuditStatus.APPROVED,
            findings=[
                "hmac_sha256 signature verified",
                f"policy_name={policy_payload.policy_name}",
                f"rollout_scope={policy_payload.rollout_scope}",
            ],
            requires_human_review=policy_payload.rollout_scope == "manual_review",
        ),
    )

    workflow = trigger_workflow(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.orchestrator_agent_id,
        parent_record_id=audit.record.record_id,
        workflow_id="policy_promotion",
        payload=WorkflowTriggerPayload(
            workflow_name=config.apply_workflow_name,
            reason=(
                f"signed sandbox policy {policy_payload.policy_name} "
                f"(record {policy_update_record.record_id}) verified and approved"
            ),
            priority="high"
            if policy_payload.rollout_scope == "manual_review"
            else "normal",
        ),
    )
    return audit, workflow


def _rollback_target_is_known(
    context: RouteContext,
    config: PolicyPromotionConfig,
    policy_payload: PolicyUpdatePayload,
) -> bool:
    if not policy_payload.is_rollback:
        return True

    history = applied_state_history(
        context,
        production_tenant_id=config.production_tenant_id,
        sandbox_tenant_id=config.sandbox_tenant_id,
    )
    target_parameters = dict(policy_payload.parameters)
    return any(
        state.policy_name == policy_payload.policy_name
        and dict(state.parameters) == target_parameters
        for state in history
    )


def run_policy_promotion_cycle(
    context: RouteContext,
    *,
    config: PolicyPromotionConfig | None = None,
) -> PolicyPromotionResult:
    """Promote signed sandbox policy updates across the production boundary."""

    config = config or PolicyPromotionConfig()
    signing_key = config.signing_key or default_signing_key()

    signed_policies = _load_signed_policy_updates(context, config)
    already_promoted = _already_promoted_ids(context, config)

    item_results: list[PolicyPromotionItemResult] = []
    for policy_record in signed_policies:
        record_id_str = str(policy_record.record_id)

        if policy_record.record_id in already_promoted:
            item_results.append(
                PolicyPromotionItemResult(
                    policy_update_record_id=record_id_str,
                    verification_passed=True,
                    production_audit=None,
                    production_workflow_trigger=None,
                    sandbox_rejection_audit=None,
                    skipped_already_promoted=True,
                )
            )
            continue

        signature_id = policy_record.audit.signature_id or ""
        signer_id = policy_record.source_agent
        verification_passed = verify(
            policy_record.payload, signer_id, signature_id, signing_key
        )

        if not verification_passed:
            rejection = _reject_in_sandbox(
                context,
                config,
                policy_record,
                reason="hmac_sha256 signature verification failed",
            )
            item_results.append(
                PolicyPromotionItemResult(
                    policy_update_record_id=record_id_str,
                    verification_passed=False,
                    production_audit=None,
                    production_workflow_trigger=None,
                    sandbox_rejection_audit=rejection,
                    skipped_already_promoted=False,
                )
            )
            continue

        policy_payload = PolicyUpdatePayload.model_validate(policy_record.payload)
        if policy_payload.target_production_tenant_id != config.production_tenant_id:
            rejection = _reject_in_sandbox(
                context,
                config,
                policy_record,
                reason=_cross_tenant_finding(config),
            )
            item_results.append(
                PolicyPromotionItemResult(
                    policy_update_record_id=record_id_str,
                    verification_passed=True,
                    production_audit=None,
                    production_workflow_trigger=None,
                    sandbox_rejection_audit=rejection,
                    skipped_already_promoted=False,
                )
            )
            continue

        # Phase 1.4 §11 decision 2 — sandbox-side parameter-key reservation
        # check. Stops a signed POLICY_UPDATE whose ``parameters`` dict
        # carries any key outside ``RESERVED_PARAMETER_KEYS`` BEFORE it
        # crosses the production boundary. The Guardrail 11 gate is the
        # mirror check at apply time (defense in depth). Placed AFTER
        # cross-tenant rejection so the existing reject-ladder order is
        # preserved: signature -> tenant -> parameter keys -> rollback
        # history.
        unauthorized = unauthorized_parameter_keys(policy_payload.parameters)
        if unauthorized:
            rejection = _reject_in_sandbox(
                context,
                config,
                policy_record,
                reason=_unauthorized_parameter_key_finding(unauthorized),
            )
            item_results.append(
                PolicyPromotionItemResult(
                    policy_update_record_id=record_id_str,
                    verification_passed=True,
                    production_audit=None,
                    production_workflow_trigger=None,
                    sandbox_rejection_audit=rejection,
                    skipped_already_promoted=False,
                )
            )
            continue

        if not _rollback_target_is_known(context, config, policy_payload):
            rejection = _reject_in_sandbox(
                context,
                config,
                policy_record,
                reason="rollback target not in applied-state history for this tenant",
            )
            item_results.append(
                PolicyPromotionItemResult(
                    policy_update_record_id=record_id_str,
                    verification_passed=True,
                    production_audit=None,
                    production_workflow_trigger=None,
                    sandbox_rejection_audit=rejection,
                    skipped_already_promoted=False,
                )
            )
            continue

        audit, workflow = _approve_in_production(
            context, config, policy_record, policy_payload
        )
        item_results.append(
            PolicyPromotionItemResult(
                policy_update_record_id=record_id_str,
                verification_passed=True,
                production_audit=audit,
                production_workflow_trigger=workflow,
                sandbox_rejection_audit=None,
                skipped_already_promoted=False,
            )
        )

    promoted = sum(
        1 for item in item_results if item.production_workflow_trigger is not None
    )
    rejected = sum(1 for item in item_results if item.sandbox_rejection_audit is not None)
    skipped = sum(1 for item in item_results if item.skipped_already_promoted)

    return PolicyPromotionResult(
        processed_count=len(item_results),
        promoted_count=promoted,
        rejected_count=rejected,
        skipped_count=skipped,
        item_results=item_results,
    )
