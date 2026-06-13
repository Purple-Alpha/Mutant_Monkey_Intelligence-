"""ThreatLevelClassifier — Watcher Agents (Layer 6 Governance), Watcher authority.

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — WA-D1 / WA-D2 / WA-D3 / WA-D8 + §4.

Watchers classify the swarm threat level from behavioral signals. Four levels:
ROUTINE → ELEVATED → HIGH → CRITICAL. The classification is the **Watcher's
decision**; the Fission Controllers act on it (WA-D1). **Agents never influence
the threat level** (WA-D8) — only registered watcher ids may submit a signal.

Escalation rules (WA-D2 / WA-D3):
  - Any level **above ROUTINE requires agreement from ≥2 independent watchers.**
  - **No single watcher** forces a change unilaterally, up or down above ROUTINE.

The classified level is therefore the **highest level supported by at least two
distinct watchers**, ROUTINE otherwise. A lone signal can never move the swarm
off ROUTINE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from core.watchers.observation import (
    ObservationLog,
    ObservationType,
    Severity,
    SWARM_SCOPE,
)

# The only legitimate signal sources (WA-D8). Anything else is not a watcher and
# cannot influence the threat level.
WATCHER_IDS = ("W1", "W2", "W3")

# Minimum independent watchers required to escalate above ROUTINE (WA-D2).
ESCALATION_QUORUM = 2


class ThreatLevel(IntEnum):
    ROUTINE = 0
    ELEVATED = 1
    HIGH = 2
    CRITICAL = 3


class ThreatLevelError(Exception):
    """Raised when a non-watcher attempts to influence the threat level (WA-D8)."""


@dataclass
class ThreatLevelClassifier:
    """Two-of-N independent-agreement threat classifier (WA-D2/D3/D8)."""

    log: ObservationLog | None = None
    _signals: dict[str, ThreatLevel] = field(default_factory=dict)
    _level: ThreatLevel = ThreatLevel.ROUTINE

    @property
    def level(self) -> ThreatLevel:
        return self._level

    def submit_signal(self, *, watcher_id: str, proposed_level: ThreatLevel) -> ThreatLevel:
        """Record one watcher's proposed level and recompute the classification.

        Only registered watcher ids may submit (WA-D8). Returns the resulting
        classified level — which is recomputed by quorum, never set unilaterally.
        """

        if watcher_id not in WATCHER_IDS:
            raise ThreatLevelError(
                f"{watcher_id!r} is not a registered watcher; agents and other "
                "sources cannot influence the threat level (WA-D8)"
            )
        if not isinstance(proposed_level, ThreatLevel):
            raise ThreatLevelError("proposed_level must be a ThreatLevel")
        self._signals[watcher_id] = proposed_level
        return self._recompute()

    def _recompute(self) -> ThreatLevel:
        """Classified level = highest level supported by ≥2 distinct watchers.

        ROUTINE needs no quorum. Any level above ROUTINE requires at least
        ``ESCALATION_QUORUM`` independent watchers proposing that level or higher
        (WA-D2). This makes both escalation and de-escalation consensus-derived;
        a single watcher cannot move the level off ROUTINE (WA-D3).
        """

        new_level = ThreatLevel.ROUTINE
        for candidate in (ThreatLevel.CRITICAL, ThreatLevel.HIGH, ThreatLevel.ELEVATED):
            supporting = sum(1 for lvl in self._signals.values() if lvl >= candidate)
            if supporting >= ESCALATION_QUORUM:
                new_level = candidate
                break

        if new_level != self._level:
            previous = self._level
            self._level = new_level
            if self.log is not None:
                severity = (
                    Severity.CRITICAL
                    if new_level is ThreatLevel.CRITICAL
                    else Severity.WARNING
                )
                self.log.record(
                    watcher_id="threat_classifier",
                    observation_type=ObservationType.THREAT_LEVEL_CHANGE,
                    severity=severity,
                    observed_agent=SWARM_SCOPE,
                    details=(
                        f"threat level {previous.name} → {new_level.name} "
                        f"(quorum of {ESCALATION_QUORUM} independent watchers)"
                    ),
                    tenant_id=SWARM_SCOPE,
                )
        return self._level


__all__ = [
    "WATCHER_IDS",
    "ESCALATION_QUORUM",
    "ThreatLevel",
    "ThreatLevelError",
    "ThreatLevelClassifier",
]
