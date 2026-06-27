"""ControlPlaneAuditTrail — Phase 6 (Layer 6), append-only control-plane history.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D1 / BRC-D15 / §3 (every gate transition, breaker state
change, budget exhaustion, and ring promotion attempt is recorded).

Consistent with the Phase 1 Component-2 boundary (``role_separation.py``): no
auth infrastructure and no persistence layer is introduced here. The trail is
an in-process, append-only list — there is no update or delete API, so history
holds structurally, not by convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ControlPlaneEvent(str, Enum):
    """Closed set of auditable control-plane events."""

    IDENTITY_REJECTED = "identity_rejected"
    BREAKER_TRIPPED = "breaker_tripped"
    BREAKER_PROBE = "breaker_probe"
    BREAKER_CLOSED = "breaker_closed"
    BUDGET_EXHAUSTED = "budget_exhausted"
    SEGMENTATION_REJECTED = "segmentation_rejected"
    BROADCAST_BLOCKED = "broadcast_blocked"
    RING_PROMOTION_REJECTED = "ring_promotion_rejected"
    RING_PROMOTED = "ring_promoted"
    GATEWAY_REJECTED = "gateway_rejected"
    TRIAGE_SCORED = "triage_scored"
    GATEWAY_DISPATCHED = "gateway_dispatched"


@dataclass(frozen=True)
class ControlPlaneAuditEntry:
    """One append-only control-plane record."""

    event: ControlPlaneEvent
    detail: str
    tenant_id: str = ""
    agent_id: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class ControlPlaneAuditTrail:
    """In-process append-only control-plane audit log. No update/delete API."""

    _entries: list[ControlPlaneAuditEntry] = field(default_factory=list)

    def record(
        self,
        event: ControlPlaneEvent,
        detail: str,
        *,
        tenant_id: str = "",
        agent_id: str = "",
    ) -> ControlPlaneAuditEntry:
        entry = ControlPlaneAuditEntry(
            event=event,
            detail=detail,
            tenant_id=tenant_id,
            agent_id=agent_id,
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> tuple[ControlPlaneAuditEntry, ...]:
        return tuple(self._entries)

    def for_event(
        self, event: ControlPlaneEvent
    ) -> tuple[ControlPlaneAuditEntry, ...]:
        return tuple(e for e in self._entries if e.event is event)


__all__ = [
    "ControlPlaneEvent",
    "ControlPlaneAuditEntry",
    "ControlPlaneAuditTrail",
]
