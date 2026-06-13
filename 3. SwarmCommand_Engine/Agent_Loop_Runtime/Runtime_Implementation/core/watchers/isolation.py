"""Watcher infrastructure isolation — Watcher Agents (Layer 6 Governance).

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — WA-D6 + §5. **Non-negotiable.**

Watchers run in **separate infrastructure** from the agents they observe:
**separate resource quotas** and **separate credentials**. A watcher **cannot be
starved by agent resource exhaustion** — an agent (or tenant) burning its whole
budget must not degrade a watcher's ability to observe, precisely when the swarm
is under the most pressure and observation matters most.

This module models that as two **disjoint quota pools**. Watcher capacity is
drawn only from the watcher pool; agent consumption is drawn only from agent
pools. There is no API by which agent consumption touches the watcher pool.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ResourceIsolationError(Exception):
    """Raised on a cross-pool draw — the isolation boundary violated (fail-safe)."""


@dataclass
class _Pool:
    name: str
    capacity: int
    consumed: int = 0

    def remaining(self) -> int:
        return self.capacity - self.consumed


@dataclass
class WatcherResourceController:
    """Disjoint watcher / agent quota pools with separate credentials (WA-D6).

    The watcher pool and each agent pool are independent. ``consume_agent`` can
    never draw from the watcher pool, so exhausting agent budget leaves watcher
    capacity untouched.
    """

    watcher_capacity: int = 100
    watcher_credential: str = "__watcher_credential__"
    _watcher: _Pool = field(init=False)
    _agents: dict[str, _Pool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._watcher = _Pool(name="watcher", capacity=self.watcher_capacity)

    def register_agent_pool(self, agent_id: str, capacity: int) -> None:
        self._agents[agent_id] = _Pool(name=agent_id, capacity=capacity)

    def consume_agent(self, agent_id: str, units: int) -> int:
        """Consume from an agent's own pool. Never touches the watcher pool."""

        pool = self._agents.get(agent_id)
        if pool is None:
            raise ResourceIsolationError(f"unknown agent pool {agent_id!r}")
        pool.consumed = min(pool.capacity, pool.consumed + units)
        return pool.remaining()

    def consume_watcher(self, units: int, *, credential: str) -> int:
        """Consume from the watcher pool. Requires the watcher credential —
        separate credentials (WA-D6); an agent credential cannot spend here.
        """

        if credential != self.watcher_credential:
            raise ResourceIsolationError(
                "watcher pool requires the watcher credential; agent credentials "
                "cannot draw watcher capacity (WA-D6)"
            )
        self._watcher.consumed = min(
            self._watcher.capacity, self._watcher.consumed + units
        )
        return self._watcher.remaining()

    def watcher_remaining(self) -> int:
        return self._watcher.remaining()

    def watcher_can_observe(self) -> bool:
        """True while the watcher pool has capacity — by construction unaffected
        by any amount of agent consumption (WA-D6)."""

        return self._watcher.remaining() > 0


__all__ = [
    "ResourceIsolationError",
    "WatcherResourceController",
]
