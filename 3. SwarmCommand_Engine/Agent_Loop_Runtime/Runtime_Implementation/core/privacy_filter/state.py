"""Privacy Filter — enums, policy schema, and locked constants.

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Contract.md`` — §15 SIGNED 2026-06-14
(Matt Nichol). Scoreboard row #93 (Layer 6 Control Plane).

The Privacy Filter is a separate service (PF-D1) that sits between the swarm and
any cross-tenant broadcast. Its governing property is **isolation by
construction**: no raw tenant identifier may ever cross a tenant boundary
(PF-D5), and if the filter is unhealthy nothing broadcasts (PF-D2, fail closed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PipelineStage(int, Enum):
    """The five mandatory pipeline stages, in order (PF-D4, §3). No stage is
    skippable and no shortcut path exists."""

    ENTITY_DETECTION = 1
    POLICY_LOOKUP = 2
    TRANSFORMATION = 3
    VALIDATION = 4
    AUDIT_RECORD = 5


class SharingScope(str, Enum):
    """Per-tenant sharing scope (§5). Absence resolves fail-closed (PF-D6)."""

    ALL_TENANTS = "ALL_TENANTS"
    COHORT = "COHORT"
    NONE = "NONE"


class Granularity(str, Enum):
    """Transformation granularity the resolved policy permits (§5)."""

    FULL = "FULL"
    GENERALIZED = "GENERALIZED"
    HASH_ONLY = "HASH_ONLY"
    BLOCKED = "BLOCKED"


class EligibleSignalType(str, Enum):
    """The only signal types eligible for cross-tenant broadcast (§6).

    Consistent with Mode Controller MC-D10 / PF-D10: the RECOVERING-mode upload
    restriction (pattern hashes + anomaly counts) is the same class of constraint
    this filter enforces on the NORMAL-mode broadcast path.
    """

    PATTERN_HASH = "pattern_hash"
    ANOMALY_COUNT = "anomaly_count"
    GENERALIZED_INDICATOR = "generalized_indicator"
    INFRASTRUCTURE_FINGERPRINT = "infrastructure_fingerprint"


class EntityKind(str, Enum):
    """Tenant-identifying / sensitive entity kinds detected in stage 1 (§3.1)."""

    TENANT_ID = "tenant_id"
    EMAIL = "email"
    IP_ADDRESS = "ip_address"
    ACCOUNT_NUMBER = "account_number"
    NAME = "name"
    ADDRESS = "address"
    INFRA_FINGERPRINT = "infra_fingerprint"
    RAW_EMAIL_CONTENT = "raw_email_content"


# Entity kinds that may NEVER appear in raw form in broadcast output, regardless
# of policy (§6 "Never eligible regardless of policy"; PF-D5 invariant). These
# must be stripped or hashed by transformation and proven absent by validation.
NEVER_RAW_IN_OUTPUT: frozenset[EntityKind] = frozenset(
    {
        EntityKind.TENANT_ID,
        EntityKind.EMAIL,
        EntityKind.IP_ADDRESS,
        EntityKind.ACCOUNT_NUMBER,
        EntityKind.NAME,
        EntityKind.ADDRESS,
        EntityKind.RAW_EMAIL_CONTENT,
    }
)


class BlockReason(str, Enum):
    """Why an operation was blocked (PF-D9 — refusal is a governance event)."""

    BREAKER_OPEN = "breaker_open"
    POLICY_ABSENT = "policy_absent"
    POLICY_AMBIGUOUS = "policy_ambiguous"
    PIPEDA_CONSENT_ABSENT = "pipeda_consent_absent"
    GRANULARITY_BLOCKED = "granularity_blocked"
    SCOPE_NONE = "scope_none"
    INELIGIBLE_SIGNAL_TYPE = "ineligible_signal_type"
    VALIDATION_RAW_IDENTIFIER = "validation_raw_identifier"
    VALIDATION_POLICY_MISMATCH = "validation_policy_mismatch"
    AUDIT_WRITE_FAILED = "audit_write_failed"


class BroadcastDecision(str, Enum):
    BROADCAST = "broadcast"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SharingPolicy:
    """Per-tenant sharing policy (§5). Any absent dimension fails closed (PF-D6).

    ``is_complete`` is the conservative completeness check: a policy missing any
    governing field is treated as ambiguous and must not broadcast.
    """

    tenant_id: str
    policy_version: str
    effective_date: str
    sharing_scope: SharingScope
    allowed_signals: tuple[EligibleSignalType, ...]
    granularity: Granularity
    pipeda_consent: bool
    retention_limit: str
    policy_owner: str
    last_reviewed: str

    def is_complete(self) -> bool:
        return bool(
            self.tenant_id
            and self.policy_version
            and self.effective_date
            and isinstance(self.sharing_scope, SharingScope)
            and isinstance(self.granularity, Granularity)
            and self.retention_limit
            and self.policy_owner
            and self.last_reviewed
        )


@dataclass(frozen=True)
class DetectedEntity:
    """One entity flagged by stage 1 (§3.1)."""

    kind: EntityKind
    field_name: str
    raw_value: str


@dataclass(frozen=True)
class BroadcastCandidate:
    """A candidate item bound for cross-tenant broadcast (pipeline input)."""

    workflow_id: str
    tenant_id: str
    signal_type: EligibleSignalType
    content: dict[str, str] = field(default_factory=dict)


__all__ = [
    "PipelineStage",
    "SharingScope",
    "Granularity",
    "EligibleSignalType",
    "EntityKind",
    "NEVER_RAW_IN_OUTPUT",
    "BlockReason",
    "BroadcastDecision",
    "SharingPolicy",
    "DetectedEntity",
    "BroadcastCandidate",
]
