"""Escalation router — Watcher Agents (Layer 6 Governance).

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — WA-D5 + §6.

Three recipients only, by severity:
  - INFO     → governance audit trail only
  - WARNING  → Swarm Commander + audit trail
  - CRITICAL → Swarm Commander + **Matt directly** + audit trail

CRITICAL escalation to Matt is **direct — no queue, no delay** (WA-D5): the route
is computed and delivered synchronously, and Matt is always among the CRITICAL
recipients. ``MATT_IDENTITY`` reuses the canonical operator label from the Phase 1
role-separation surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from core.operator_state.role_separation import OPERATOR_IDENTITY
from core.watchers.observation import ObservationRecord, Severity

# Matt is the operator identity (Phase 1 role-separation, AGENTS.md §2).
MATT_IDENTITY = OPERATOR_IDENTITY


class Recipient(str, Enum):
    GOVERNANCE_AUDIT_TRAIL = "governance_audit_trail"
    SWARM_COMMANDER = "swarm_commander"
    MATT = MATT_IDENTITY


# Static, severity → recipients map (§6). Audit trail is always included.
_ROUTING: dict[Severity, frozenset[Recipient]] = {
    Severity.INFO: frozenset({Recipient.GOVERNANCE_AUDIT_TRAIL}),
    Severity.WARNING: frozenset(
        {Recipient.SWARM_COMMANDER, Recipient.GOVERNANCE_AUDIT_TRAIL}
    ),
    Severity.CRITICAL: frozenset(
        {Recipient.SWARM_COMMANDER, Recipient.MATT, Recipient.GOVERNANCE_AUDIT_TRAIL}
    ),
}


@dataclass
class EscalationDelivery:
    record: ObservationRecord
    recipients: frozenset[Recipient]
    direct_to_matt: bool


@dataclass
class EscalationRouter:
    """Routes observations to the three recipients by severity (§6, WA-D5)."""

    _deliveries: list[EscalationDelivery] = field(default_factory=list)

    @staticmethod
    def recipients_for(severity: Severity) -> frozenset[Recipient]:
        return _ROUTING[severity]

    def route(self, record: ObservationRecord) -> EscalationDelivery:
        """Compute and deliver the route synchronously. For CRITICAL, Matt is a
        recipient and delivery is direct — no queue, no delay (WA-D5)."""

        recipients = _ROUTING[record.severity]
        delivery = EscalationDelivery(
            record=record,
            recipients=recipients,
            direct_to_matt=Recipient.MATT in recipients,
        )
        # Synchronous append == delivered now; there is no deferred queue.
        self._deliveries.append(delivery)
        return delivery

    def deliveries(self) -> tuple[EscalationDelivery, ...]:
        return tuple(self._deliveries)


__all__ = [
    "MATT_IDENTITY",
    "Recipient",
    "EscalationDelivery",
    "EscalationRouter",
]
