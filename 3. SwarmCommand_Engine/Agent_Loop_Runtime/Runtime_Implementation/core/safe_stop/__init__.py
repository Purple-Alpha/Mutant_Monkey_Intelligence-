"""Safe-Stop State Machine — Layer 6 Control Plane (scoreboard row #94).

Governed by ``4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md``
(§11 SIGNED 2026-06-14, Matt Nichol). The named, controlled state the organism
enters when a core safety guarantee can no longer be trusted: bounded, logged,
operator-governed shutdown over silent corruption.

The Mode Controller and Privacy Filter are separate contracts — this package
builds the safe-stop machine and its entry log, and consumes the Mode Controller
only through the ``RecoveryBroadcaster`` / ``is_dispatch_allowed`` seams.
"""

from core.safe_stop.state import (
    RECONCILIATION_GRACE_SECONDS,
    SAFE_STOP_EXIT_AUTHORITY,
    SS1_QUORUM_LOSS_TIMEOUT_SECONDS,
    SS3_DUAL_CRITICAL_WINDOW_SECONDS,
    BoundaryViolationSubtype,
    EntryCondition,
    ForbiddenAction,
    PermittedAction,
    SafeStopState,
)
from core.safe_stop.log import (
    SafeStopLog,
    SafeStopLogError,
    SafeStopRecord,
    SafeStopRecordKind,
)
from core.safe_stop.machine import (
    PERMITTED_INSIDE_SAFE_STOP,
    DefaultRecoveryBroadcaster,
    RecoveryBroadcaster,
    SafeStopAuthorityError,
    SafeStopError,
    SafeStopStateMachine,
    SafeStopViolation,
)

__all__ = [
    # state
    "SS1_QUORUM_LOSS_TIMEOUT_SECONDS",
    "SS3_DUAL_CRITICAL_WINDOW_SECONDS",
    "SAFE_STOP_EXIT_AUTHORITY",
    "RECONCILIATION_GRACE_SECONDS",
    "SafeStopState",
    "EntryCondition",
    "BoundaryViolationSubtype",
    "ForbiddenAction",
    "PermittedAction",
    # log
    "SafeStopLog",
    "SafeStopLogError",
    "SafeStopRecord",
    "SafeStopRecordKind",
    # machine
    "PERMITTED_INSIDE_SAFE_STOP",
    "DefaultRecoveryBroadcaster",
    "RecoveryBroadcaster",
    "SafeStopAuthorityError",
    "SafeStopError",
    "SafeStopStateMachine",
    "SafeStopViolation",
]
