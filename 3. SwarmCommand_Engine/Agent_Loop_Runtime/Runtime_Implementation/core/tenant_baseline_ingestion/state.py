"""Closed state vocabulary for Tenant Baseline Ingestion (Gap 5).

Governing contract
------------------
``4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md``
— §11 SIGNED 2026-06-14 (Matt Nichol). Scoreboard row #97.

This package governs evidence-to-baseline promotion only. It is not detection,
reconciliation, immune authority, adaptive memory, or cross-tenant aggregation.
"""

from __future__ import annotations

from enum import Enum


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PromotionDecision(str, Enum):
    PROMOTED = "promoted"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    ROLLED_BACK = "rolled_back"


class CandidateStatus(str, Enum):
    PROPOSED = "proposed"
    OPERATOR_REVIEW = "operator_review"
    PROMOTED = "promoted"
    REJECTED = "rejected"
    QUARANTINED_DUE_TO_PARENT_ROLLBACK = "quarantined_due_to_parent_rollback"


class ApprovalPolicy(str, Enum):
    NONE_AUTO = "none_auto"
    SINGLE_OPERATOR = "single_operator"
    DUAL_OPERATOR = "dual_operator"
    DUAL_OR_TENANT_ADMIN = "dual_or_tenant_admin"


class ActorType(str, Enum):
    AGENT = "agent"
    OPERATOR = "operator"
    TENANT_ADMIN = "tenant_admin"
    SYSTEM = "system"


class BaselineStatus(str, Enum):
    ACTIVE = "active"
    FROZEN_PENDING_RECONCILIATION = "frozen_pending_reconciliation"


class AuditEventType(str, Enum):
    PROMOTION = "promotion"
    REJECTION = "rejection"
    QUARANTINE = "quarantine"
    ROLLBACK = "rollback"
    REPLAY = "replay"
    APPROVAL = "approval"
    SEPARATION_OF_DUTIES_FAILURE = "separation_of_duties_failure"


class RollbackOutcome(str, Enum):
    UNCHANGED_AFTER_REPLAY = "unchanged_after_replay"
    RISK_INCREASED_AFTER_REPLAY = "risk_increased_after_replay"
    RISK_DECREASED_AFTER_REPLAY = "risk_decreased_after_replay"
    ALERT_SHOULD_HAVE_FIRED = "alert_should_have_fired"
    ALERT_WAS_CORRECTLY_SUPPRESSED = "alert_was_correctly_suppressed"
    ALERT_WAS_INCORRECTLY_SUPPRESSED = "alert_was_incorrectly_suppressed"
    CASE_REQUIRES_OPERATOR_REVIEW = "case_requires_operator_review"
    REPORT_REQUIRES_AMENDMENT = "report_requires_amendment"
    DOWNSTREAM_BASELINE_CANDIDATE_INVALIDATED = (
        "downstream_baseline_candidate_invalidated"
    )


RISK_TIER_CAPS: dict[RiskTier, float] = {
    RiskTier.LOW: 1.00,
    RiskTier.MEDIUM: 0.90,
    RiskTier.HIGH: 0.75,
    RiskTier.CRITICAL: 0.60,
}

PROMOTION_THRESHOLDS: dict[RiskTier, float] = {
    RiskTier.LOW: 0.95,
    RiskTier.MEDIUM: 0.90,
    RiskTier.HIGH: 0.75,
    RiskTier.CRITICAL: 0.60,
}

PERMANENT_LOCKOUT_PREFIXES: tuple[str, ...] = (
    "vendor.payment_accounts.",
    "vendor.routing_number_hash",
    "vendor.bank_account_hash",
    "vendor.payment_instruction_change_pattern",
    "vendor.known_good_callback_number",
    "vendor.approved_payment_channel",
    "employee.privileged_access_pattern",
    "employee.admin_role_assignment",
    "executive.payment_authority_pattern",
    "identity_provider.privileged_group_membership",
    "identity_provider.mfa_exception",
    "identity_provider.conditional_access_exception",
    "detector.alert_suppression_rule",
    "detector.allowlist_entry",
    "detector.threshold_reduction",
    "security_policy.exfiltration_baseline",
    "security_policy.login_geo_baseline_for_privileged_user",
)


def is_permanent_lockout_key(baseline_key: str) -> bool:
    return any(baseline_key.startswith(prefix) for prefix in PERMANENT_LOCKOUT_PREFIXES)


def approval_policy_for(risk_tier: RiskTier, locked_key: bool = False) -> ApprovalPolicy:
    if locked_key or risk_tier is RiskTier.HIGH:
        return ApprovalPolicy.DUAL_OPERATOR
    if risk_tier is RiskTier.CRITICAL:
        return ApprovalPolicy.DUAL_OR_TENANT_ADMIN
    if risk_tier is RiskTier.MEDIUM:
        return ApprovalPolicy.SINGLE_OPERATOR
    return ApprovalPolicy.NONE_AUTO


__all__ = [
    "RiskTier",
    "PromotionDecision",
    "CandidateStatus",
    "ApprovalPolicy",
    "ActorType",
    "BaselineStatus",
    "AuditEventType",
    "RollbackOutcome",
    "RISK_TIER_CAPS",
    "PROMOTION_THRESHOLDS",
    "PERMANENT_LOCKOUT_PREFIXES",
    "is_permanent_lockout_key",
    "approval_policy_for",
]
