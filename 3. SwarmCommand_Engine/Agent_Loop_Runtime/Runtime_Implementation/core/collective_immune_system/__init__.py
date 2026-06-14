"""Collective Immune System package — Layer 6 Control Plane, scoreboard row #95.

Governed by ``4. Product_Roadmap/Collective_Immune_System_Design_Contract.md``
(§11 SIGNED 2026-06-14, Matt Nichol).

The CIS is a coordination layer only: it governs escalation-level plans and
contract-enumerated handoff paths without owning mode, epoch, verdict, fission,
mutation, Privacy Filter, BRC, or Safe-Stop authority.
"""

from core.collective_immune_system.coordinator import (
    CISError,
    CollectiveImmuneSystemCoordinator,
    CoordinationPlan,
    EscalationRejected,
    EscalationRequest,
    EvidenceHandoff,
    ForbiddenActionRejected,
    HandoffRejected,
    SafeStopBoundaryError,
)
from core.collective_immune_system.log import (
    CISLogError,
    CISRecord,
    CISRecordKind,
    CollectiveImmuneSystemLog,
)
from core.collective_immune_system.state import (
    AUTHORIZED_HANDOFF_PATHS,
    CISAction,
    CISComponent,
    EscalationLevel,
    ForbiddenCISAction,
    HandoffPath,
    is_authorized_handoff,
)

__all__ = [
    # state
    "EscalationLevel",
    "CISComponent",
    "CISAction",
    "ForbiddenCISAction",
    "HandoffPath",
    "AUTHORIZED_HANDOFF_PATHS",
    "is_authorized_handoff",
    # log
    "CISRecordKind",
    "CISLogError",
    "CISRecord",
    "CollectiveImmuneSystemLog",
    # coordinator
    "CISError",
    "HandoffRejected",
    "EscalationRejected",
    "ForbiddenActionRejected",
    "SafeStopBoundaryError",
    "EscalationRequest",
    "EvidenceHandoff",
    "CoordinationPlan",
    "CollectiveImmuneSystemCoordinator",
]
