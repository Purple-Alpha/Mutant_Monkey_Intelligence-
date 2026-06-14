"""Mode Controller package — Layer 6 Control Plane, scoreboard row #92.

Governing contract: ``4. Product_Roadmap/Mode_Controller_Contract.md`` —
§14 SIGNED 2026-06-13 (Matt Nichol).

The autonomic nervous system of the organism: the single authoritative operating
mode of the swarm and the monotonic ``mode_epoch``.
"""

from __future__ import annotations

from core.mode_controller.controller import (
    AgentInfluenceError,
    EpochError,
    FlappingError,
    Heartbeat,
    ModeController,
    ModeControllerError,
    ObserverVote,
    QuorumError,
    RecoveryError,
    TenantModeView,
    TransitionError,
)
from core.mode_controller.homeostasis import (
    HomeostasisBand,
    HomeostasisError,
    HomeostasisReading,
    compute_homeostasis_index,
)
from core.mode_controller.log import (
    ModeLogError,
    ModeRecordKind,
    ModeTransitionLog,
    ModeTransitionRecord,
)
from core.mode_controller.state import (
    ALLOWED_TRANSITIONS,
    HOMEOSTASIS_CRITICAL_THRESHOLD,
    HOMEOSTASIS_WARNING_THRESHOLD,
    MIN_DWELL_SECONDS,
    MODE_HEARTBEAT_TIMEOUT_SECONDS,
    QUORUM_ELIGIBLE_SOURCES,
    QUORUM_MIN_OBSERVERS,
    RECONCILIATION_WINDOW_SECONDS,
    HomeostasisLayer,
    Mode,
    ObserverSource,
)

__all__ = [
    # state
    "Mode",
    "ObserverSource",
    "HomeostasisLayer",
    "QUORUM_ELIGIBLE_SOURCES",
    "QUORUM_MIN_OBSERVERS",
    "MODE_HEARTBEAT_TIMEOUT_SECONDS",
    "MIN_DWELL_SECONDS",
    "RECONCILIATION_WINDOW_SECONDS",
    "HOMEOSTASIS_WARNING_THRESHOLD",
    "HOMEOSTASIS_CRITICAL_THRESHOLD",
    "ALLOWED_TRANSITIONS",
    # log
    "ModeRecordKind",
    "ModeLogError",
    "ModeTransitionRecord",
    "ModeTransitionLog",
    # homeostasis
    "HomeostasisError",
    "HomeostasisBand",
    "HomeostasisReading",
    "compute_homeostasis_index",
    # controller
    "ModeControllerError",
    "QuorumError",
    "AgentInfluenceError",
    "FlappingError",
    "TransitionError",
    "RecoveryError",
    "EpochError",
    "ObserverVote",
    "Heartbeat",
    "ModeController",
    "TenantModeView",
]
