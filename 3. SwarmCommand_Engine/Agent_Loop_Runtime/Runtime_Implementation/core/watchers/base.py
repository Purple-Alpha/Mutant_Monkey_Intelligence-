"""BaseWatcher — Watcher Agents (Layer 6 Governance), neutral-observer base.

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — WA-D7 + §0 / §7.

A watcher is a **neutral observer**: no vote in verdicts, no access to the
evidence chain, no write to ``core/blackboard/``, no recommendations beyond
threat-level classification. It reports **facts only**.

These prohibitions are enforced structurally and actively. Structurally: a
watcher is constructed with only an ``ObservationLog`` and a
``ThreatLevelClassifier`` — it is never handed a blackboard or a verdict surface.
Actively: the boundary methods below **always raise** ``WatcherBoundaryError`` so
an attempt to cross the line is a tested, deterministic rejection (§7), not
merely an absent capability. Each watcher also declares the closed set of
observation types it is allowed to emit, so a watcher cannot write outside its
lane.
"""

from __future__ import annotations

from core.watchers.observation import (
    ObservationLog,
    ObservationRecord,
    ObservationType,
    Severity,
    SWARM_SCOPE,
)
from core.watchers.threat import ThreatLevel, ThreatLevelClassifier


class WatcherBoundaryError(Exception):
    """Raised when a watcher attempts an action outside its neutral-observer role.

    Covers: writing to the core blackboard, influencing a verdict, communicating
    with detection agents / the ReconciliationAgent, or emitting an observation
    type outside the watcher's allowed lane (WA-D7 / §7).
    """


class BaseWatcher:
    """Neutral observer base. Writes only to the ObservationLog; never to the
    blackboard, never to a verdict."""

    #: Closed set of observation types this watcher may emit. Subclasses override.
    ALLOWED_TYPES: frozenset[ObservationType] = frozenset()

    def __init__(
        self,
        watcher_id: str,
        *,
        log: ObservationLog,
        classifier: ThreatLevelClassifier | None = None,
    ) -> None:
        self.watcher_id = watcher_id
        self._log = log
        self._classifier = classifier

    # -- the only legitimate output surface ---------------------------------

    def _observe(
        self,
        *,
        observation_type: ObservationType,
        severity: Severity,
        observed_agent: str,
        details: str,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord:
        """Write one observation to the log. Rejects any type outside this
        watcher's allowed lane (WA-D7)."""

        if observation_type not in self.ALLOWED_TYPES:
            raise WatcherBoundaryError(
                f"{self.watcher_id} may not emit {observation_type.value!r}; "
                f"allowed: {sorted(t.value for t in self.ALLOWED_TYPES)}"
            )
        return self._log.record(
            watcher_id=self.watcher_id,
            observation_type=observation_type,
            severity=severity,
            observed_agent=observed_agent,
            details=details,
            tenant_id=tenant_id,
        )

    def propose_threat_level(self, level: ThreatLevel) -> None:
        """Submit this watcher's threat-level signal. The classifier decides by
        quorum; a single watcher cannot force a change (WA-D2/D3)."""

        if self._classifier is None:
            raise WatcherBoundaryError("no threat-level classifier wired to this watcher")
        self._classifier.submit_signal(watcher_id=self.watcher_id, proposed_level=level)

    # -- hard boundaries: always reject (WA-D7 / §7) ------------------------

    def write_blackboard(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise WatcherBoundaryError(
            f"{self.watcher_id} may never write to core/blackboard/ (WA-D4/WA-D7)"
        )

    def influence_verdict(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise WatcherBoundaryError(
            f"{self.watcher_id} has no vote in verdicts and no evidence-chain "
            "access (WA-D7)"
        )

    def message_agent(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise WatcherBoundaryError(
            f"{self.watcher_id} may never communicate with detection agents or "
            "the ReconciliationAgent (§1 out of scope / §7)"
        )

    def make_recommendation(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise WatcherBoundaryError(
            f"{self.watcher_id} makes no recommendation beyond threat-level "
            "classification; observations are facts only (WA-D7)"
        )


__all__ = [
    "WatcherBoundaryError",
    "BaseWatcher",
]
