"""Load Fission governance artifacts — spawn records, lifecycle log, quotas (LF2 §4–§5).

Governing contract
------------------
``4. Product_Roadmap/Load_Fission_Contract_v2.md`` — §13 SIGNED 2026-06-13
(Matt Nichol).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LifecycleEventKind(str, Enum):
    START = "start"
    TOOL_USAGE = "tool_usage"
    EVIDENCE_WRITE = "evidence_write"
    EXHALE = "exhale"
    ORPHAN_SWEEP = "orphan_sweep"
    FALLBACK_DENIAL = "fallback_denial"
    QUOTA_DENIAL = "quota_denial"


@dataclass(frozen=True)
class SpawnDecisionRecord:
    parent_workflow_id: str
    watcher_id: str
    trigger_condition: str
    policy_version: str
    child_agent_id: str
    tools_assigned: frozenset[str]
    namespace_assigned: str
    ttl: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class LifecycleLogEntry:
    parent_workflow_id: str
    child_agent_id: str
    event: LifecycleEventKind
    detail: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LifecycleLog:
    _entries: list[LifecycleLogEntry] = field(default_factory=list)

    def record(
        self,
        *,
        parent_workflow_id: str,
        child_agent_id: str,
        event: LifecycleEventKind,
        detail: str = "",
    ) -> LifecycleLogEntry:
        entry = LifecycleLogEntry(
            parent_workflow_id=parent_workflow_id,
            child_agent_id=child_agent_id,
            event=event,
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> tuple[LifecycleLogEntry, ...]:
        return tuple(self._entries)

    def for_child(self, child_agent_id: str) -> tuple[LifecycleLogEntry, ...]:
        return tuple(e for e in self._entries if e.child_agent_id == child_agent_id)


@dataclass
class SpawnQuotaState:
    per_tenant: dict[str, int] = field(default_factory=dict)
    global_count: int = 0
    rapid_trigger_count: int = 0
    circuit_open: bool = False


@dataclass
class SpawnQuotaTracker:
    """Per-tenant + global quotas with circuit breaker (LF2 §5.1, LF2-D9)."""

    per_tenant_quota: int = 10
    global_quota: int = 100
    circuit_breaker_threshold: int = 5
    _state: SpawnQuotaState = field(default_factory=SpawnQuotaState)

    def check_and_consume(self, tenant_id: str, requested: int) -> None:
        if self._state.circuit_open:
            raise QuotaExceededError("spawn circuit breaker open (LF2 §5.1)")
        if self._state.global_count + requested > self.global_quota:
            self._trip_breaker("global quota exceeded")
            raise QuotaExceededError("global spawn quota exceeded (LF2-D9)")
        tenant_used = self._state.per_tenant.get(tenant_id, 0)
        if tenant_used + requested > self.per_tenant_quota:
            raise QuotaExceededError("per-tenant spawn quota exceeded (LF2-D9)")
        self._state.per_tenant[tenant_id] = tenant_used + requested
        self._state.global_count += requested
        self._state.rapid_trigger_count += 1
        if self._state.rapid_trigger_count >= self.circuit_breaker_threshold:
            self._trip_breaker("rapid overlapping triggers (denial of wallet)")

    def _trip_breaker(self, reason: str) -> None:
        self._state.circuit_open = True

    @property
    def circuit_open(self) -> bool:
        return self._state.circuit_open


class QuotaExceededError(Exception):
    """Graceful spawn denial under quota pressure (LF2-D9)."""


__all__ = [
    "LifecycleEventKind",
    "SpawnDecisionRecord",
    "LifecycleLogEntry",
    "LifecycleLog",
    "SpawnQuotaTracker",
    "QuotaExceededError",
]
