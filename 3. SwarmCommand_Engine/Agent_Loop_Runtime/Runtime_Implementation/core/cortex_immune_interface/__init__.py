"""Cortex / Immune Interface — Layer 6 Control Plane, scoreboard row #96.

Governed by ``4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md``
(§11 SIGNED 2026-06-14, Matt Nichol).

This package enforces the signed cross-organ boundary. It restricts legal
signals and handoff points; it does not implement Cortex, Immune, transport,
message bus, or new authority.
"""

from core.cortex_immune_interface.boundary import (
    REQUIRED_BASELINE_GATES,
    BaselineUpdateRejected,
    BaselineUpdateRequest,
    CortexImmuneInterface,
    CortexSignal,
    HiddenChannel,
    HiddenChannelRejected,
    ImmuneSignal,
    InterfaceError,
    SafeStopActiveError,
    SignalRejected,
)
from core.cortex_immune_interface.log import (
    CortexImmuneInterfaceLog,
    InterfaceLogError,
    InterfaceRecord,
    InterfaceRecordKind,
)
from core.cortex_immune_interface.state import (
    LEGAL_CORTEX_TO_IMMUNE,
    LEGAL_IMMUNE_TO_CORTEX,
    BaselineValidationGate,
    CortexComponent,
    CortexToImmuneSignal,
    HandoffPoint,
    HiddenChannelType,
    ImmuneComponent,
    ImmuneToCortexSignal,
    InterfaceDecision,
    LegalCortexSignalRule,
    LegalImmuneSignalRule,
    Organ,
)

__all__ = [
    # state
    "Organ",
    "CortexComponent",
    "ImmuneComponent",
    "HandoffPoint",
    "CortexToImmuneSignal",
    "ImmuneToCortexSignal",
    "BaselineValidationGate",
    "HiddenChannelType",
    "InterfaceDecision",
    "LegalCortexSignalRule",
    "LegalImmuneSignalRule",
    "LEGAL_CORTEX_TO_IMMUNE",
    "LEGAL_IMMUNE_TO_CORTEX",
    # log
    "InterfaceRecordKind",
    "InterfaceLogError",
    "InterfaceRecord",
    "CortexImmuneInterfaceLog",
    # boundary
    "REQUIRED_BASELINE_GATES",
    "InterfaceError",
    "SignalRejected",
    "HiddenChannelRejected",
    "BaselineUpdateRejected",
    "SafeStopActiveError",
    "CortexSignal",
    "ImmuneSignal",
    "BaselineUpdateRequest",
    "HiddenChannel",
    "CortexImmuneInterface",
]
