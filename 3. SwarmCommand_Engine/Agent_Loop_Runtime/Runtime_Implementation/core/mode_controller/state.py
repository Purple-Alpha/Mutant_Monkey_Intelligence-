"""Mode Controller — modes, observer sources, and locked design constants.

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Contract.md`` — §14 SIGNED 2026-06-13
(Matt Nichol). Scoreboard row #92 (Layer 6 Control Plane).

The Mode Controller is the autonomic nervous system of the organism: it owns the
one authoritative operating mode of the swarm and the monotonic ``mode_epoch``
(MC-D1, MC-D2). Everything else reads from it and obeys it (§0).

Tunable values below are **provisional contract-drafting values**, changeable
only by signed amendment (Class-3 §8: real tenant baseline calibration is
deferred to a signed amendment after the first tenant is onboarded). They are
not proven-optimal production values.
"""

from __future__ import annotations

from enum import Enum

# --- Provisional, signed-amendment-only tunables -----------------------------
# MC-D4 — a transition needs agreement from multiple independent control-plane
# observers; "multiple" is enforced as at least this many distinct sources.
QUORUM_MIN_OBSERVERS = 2
# MC-D6 — heartbeat loss beyond this triggers a local ISOLATED fallback with no
# epoch increment.
MODE_HEARTBEAT_TIMEOUT_SECONDS = 30.0
# MC-D8 — minimum dwell time in a mode before any transition out of it is
# permitted (anti-flapping). Per-mode so recovery paths are not over-throttled.
MIN_DWELL_SECONDS: dict[str, float] = {
    "normal": 10.0,
    "degraded": 10.0,
    "isolated": 10.0,
    "recovering": 10.0,
}
# MC-D7 — RECOVERING is time-bounded; exceeding it requires operator escalation
# (§7 "RECOVERING never completing").
RECONCILIATION_WINDOW_SECONDS = 300.0
# MC-D10 / §5 — Global Homeostasis Index thresholds on a 0..100 scale.
HOMEOSTASIS_WARNING_THRESHOLD = 70.0
HOMEOSTASIS_CRITICAL_THRESHOLD = 50.0


class Mode(str, Enum):
    """The four operating modes — closed set, four values only (MC-D1)."""

    NORMAL = "normal"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    RECOVERING = "recovering"


class ObserverSource(str, Enum):
    """Independent control-plane observer sources eligible to vote in quorum.

    Agents are deliberately **not** members of this set (MC-D5): mode-change
    logic is not exposed to agents, and an agent can neither request a transition
    nor be counted toward quorum. ``AGENT`` exists only so an agent-sourced vote
    can be explicitly rejected rather than silently ignored.
    """

    WATCHER = "watcher"
    BREAKER = "breaker"
    HOMEOSTASIS = "homeostasis"
    SEGMENTATION = "segmentation"
    BUDGET = "budget"
    RECONCILIATION = "reconciliation"
    INFRASTRUCTURE = "infrastructure"
    # Forbidden voter — present only to be rejected (MC-D5).
    AGENT = "agent"


# The control-plane sources that may be counted toward quorum (MC-D4/MC-D5).
QUORUM_ELIGIBLE_SOURCES: frozenset[ObserverSource] = frozenset(
    s for s in ObserverSource if s is not ObserverSource.AGENT
)


class HomeostasisLayer(str, Enum):
    """The eight input layers of the Global Homeostasis Index (§5, MC-D10)."""

    CORTICAL = "cortical"
    SWARM = "swarm"
    AGENT = "agent"
    MEMORY = "memory"
    WATCHER = "watcher"
    THREAT_PRESSURE = "threat_pressure"
    INFRASTRUCTURE = "infrastructure"
    FISSION = "fission"


# Allowed mode transitions (§3). Local heartbeat-timeout fallback to ISOLATED is
# tenant-side and is NOT in this controller-authored set (MC-D6).
ALLOWED_TRANSITIONS: frozenset[tuple[Mode, Mode]] = frozenset(
    {
        (Mode.NORMAL, Mode.DEGRADED),
        (Mode.DEGRADED, Mode.ISOLATED),
        (Mode.DEGRADED, Mode.NORMAL),
        (Mode.ISOLATED, Mode.RECOVERING),
        (Mode.RECOVERING, Mode.NORMAL),
        # Recovery broadcast after a safe-stop / isolation can move ISOLATED
        # straight into RECOVERING; NORMAL is only reached through validation.
        (Mode.ISOLATED, Mode.DEGRADED),
    }
)


__all__ = [
    "QUORUM_MIN_OBSERVERS",
    "MODE_HEARTBEAT_TIMEOUT_SECONDS",
    "MIN_DWELL_SECONDS",
    "RECONCILIATION_WINDOW_SECONDS",
    "HOMEOSTASIS_WARNING_THRESHOLD",
    "HOMEOSTASIS_CRITICAL_THRESHOLD",
    "Mode",
    "ObserverSource",
    "QUORUM_ELIGIBLE_SOURCES",
    "HomeostasisLayer",
    "ALLOWED_TRANSITIONS",
]
