"""Privacy Filter package — Layer 6 Control Plane, scoreboard row #93.

Governing contract: ``4. Product_Roadmap/Privacy_Filter_Contract.md`` —
§15 SIGNED 2026-06-14 (Matt Nichol).

A separate service (PF-D1) that sits between the swarm and any cross-tenant
broadcast and ensures that path never carries raw tenant-identifying
information (PF-D5). Fail closed (PF-D2): if it is unhealthy, nothing broadcasts.
"""

from __future__ import annotations

from core.privacy_filter.log import (
    AuditWriteError,
    PrivacyAuditRecord,
    PrivacyFilterAuditLog,
)
from core.privacy_filter.pipeline import (
    GEN_PREFIX,
    HASH_PREFIX,
    FilterResult,
    PrivacyFilterPipeline,
    Transformer,
    default_transform,
    detect_entities,
)
from core.privacy_filter.policy import PolicyResolutionError, PolicyStore
from core.privacy_filter.state import (
    NEVER_RAW_IN_OUTPUT,
    BlockReason,
    BroadcastCandidate,
    BroadcastDecision,
    DetectedEntity,
    EligibleSignalType,
    EntityKind,
    Granularity,
    PipelineStage,
    SharingPolicy,
    SharingScope,
)

__all__ = [
    # state
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
    # policy
    "PolicyResolutionError",
    "PolicyStore",
    # log
    "AuditWriteError",
    "PrivacyAuditRecord",
    "PrivacyFilterAuditLog",
    # pipeline
    "HASH_PREFIX",
    "GEN_PREFIX",
    "detect_entities",
    "default_transform",
    "FilterResult",
    "Transformer",
    "PrivacyFilterPipeline",
]
