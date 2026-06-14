"""Safe-Stop State Machine — shared state, conditions, and locked constants.

Governing contract
------------------
``4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md`` — §11 SIGNED
2026-06-14 (Matt Nichol). Scoreboard row #94 (Layer 6 Control Plane).

Safe-stop is a **named, controlled mode state** the organism enters when a core
safety guarantee can no longer be trusted. It is distinct from DEGRADED and
ISOLATED (§ State Definition): epoch is NOT incremented on entry, no new
processing occurs, and operator action is required to exit.

The three Operator Decision Record values (§ Operator Decision Record) are
contract-locked here. They are provisional contract-drafting values, changeable
only by signed amendment (they are not proven-optimal production values).
"""

from __future__ import annotations

from enum import Enum

# --- Operator Decision Record (signed, contract-locked) ----------------------
# OQ-1 — Mode Controller quorum-loss timeout before SS-1 fires.
SS1_QUORUM_LOSS_TIMEOUT_SECONDS = 120.0
# OQ-2 — recovery window for two simultaneous CRITICAL watcher events (SS-3).
SS3_DUAL_CRITICAL_WINDOW_SECONDS = 300.0
# OQ-3 — sole authority permitted to exit safe-stop.
SAFE_STOP_EXIT_AUTHORITY = "Matt Nichol"

# Entry-protocol step 6: in-flight reconciliation may complete within a strict
# grace window, then it is aborted and logged (§ Entry Protocol / SS-INV-12).
RECONCILIATION_GRACE_SECONDS = 60.0


class SafeStopState(str, Enum):
    """The machine's own mode state. SAFE-STOP is entered from any state."""

    RUNNING = "running"
    SAFE_STOP = "safe_stop"


class EntryCondition(str, Enum):
    """The five named entry conditions (§ Five Named Entry Conditions).

    They are not ranked — the first condition detected fires the entry protocol.
    """

    SS1_QUORUM_LOSS = "SS-1"
    SS2_PRIVACY_BREAKER = "SS-2"
    SS3_DUAL_CRITICAL = "SS-3"
    SS4_BOUNDARY_VIOLATION = "SS-4"
    SS5_UNRESOLVABLE_CONFLICT = "SS-5"


class ForbiddenAction(str, Enum):
    """Actions forbidden inside safe-stop (§ Behavior Inside Safe-Stop)."""

    EMAIL_INGESTION = "email_ingestion"
    FISSION = "fission"
    MUTATION = "mutation"
    CROSS_TENANT_BROADCAST = "cross_tenant_broadcast"
    BASELINE_UPDATE = "baseline_update"
    EPOCH_INCREMENT = "epoch_increment"
    MODE_TRANSITION = "mode_transition"
    AUTOMATIC_RECOVERY = "automatic_recovery"


class PermittedAction(str, Enum):
    """Actions permitted inside safe-stop (§ Behavior Inside Safe-Stop)."""

    READ_ONLY_EVIDENCE_AUDIT = "read_only_evidence_audit"
    OPERATOR_TELEMETRY = "operator_telemetry"
    SAFE_STOP_EVENT_LOGGING = "safe_stop_event_logging"
    INFLIGHT_RECONCILIATION_COMPLETION = "inflight_reconciliation_completion"
    INFLIGHT_CHILD_COMPLETION = "inflight_child_completion"


__all__ = [
    "SS1_QUORUM_LOSS_TIMEOUT_SECONDS",
    "SS3_DUAL_CRITICAL_WINDOW_SECONDS",
    "SAFE_STOP_EXIT_AUTHORITY",
    "RECONCILIATION_GRACE_SECONDS",
    "SafeStopState",
    "EntryCondition",
    "ForbiddenAction",
    "PermittedAction",
]
