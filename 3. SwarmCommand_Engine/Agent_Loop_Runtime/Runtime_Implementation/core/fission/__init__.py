"""Agent Fission — controlled specialist release (Layer 6 Control Plane).

Load Fission is governed by ``4. Product_Roadmap/Load_Fission_Contract.md``
(§11 SIGNED 2026-06-12, Matt Nichol) and lands first per the Specialisation
Fission advisory ordering note: shared event log and child lifecycle wiring are
built under the lower-risk load contract before the net-new-type machinery.
"""

from .event_log import (
    FissionEvent,
    FissionEventLog,
    FissionEventType,
    FissionTrigger,
)
from .load import (
    DEFAULT_MAX_LOAD_CHILDREN,
    LOAD_FISSION_MAX_DEPTH,
    LOAD_FISSION_THREAT_FLOOR,
    PROPOSED_EVIDENCE,
    FissionChild,
    FissionError,
    GatewayRegistration,
    LoadFissionController,
    LoadFissionProposal,
    ProposedEvidence,
)

__all__ = [
    "FissionEvent",
    "FissionEventLog",
    "FissionEventType",
    "FissionTrigger",
    "DEFAULT_MAX_LOAD_CHILDREN",
    "LOAD_FISSION_MAX_DEPTH",
    "LOAD_FISSION_THREAT_FLOOR",
    "PROPOSED_EVIDENCE",
    "FissionChild",
    "FissionError",
    "GatewayRegistration",
    "LoadFissionController",
    "LoadFissionProposal",
    "ProposedEvidence",
]
