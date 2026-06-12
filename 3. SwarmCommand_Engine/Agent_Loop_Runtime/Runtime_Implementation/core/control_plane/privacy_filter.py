"""PrivacyFilterInterface — Phase 6 (Layer 6), Gate 2: broadcast guard.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D5 + §3.4.

This is the **gateway-side interface** to the separate Privacy Filter service
(the service implementation is a separate spec, out of scope here). The filter
has **its own breaker** in the BreakerStore. If that breaker is `OPEN`,
**nothing broadcasts** — regardless of every other gate's state.

BRC-D5: segmentation and the privacy filter are **two independent failure
domains**. A segmentation failure does not open the privacy-filter breaker and
vice versa — that independence is enforced by giving the filter its own breaker
key, never shared with tenant/agent/tool breakers.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.control_plane.audit import ControlPlaneAuditTrail, ControlPlaneEvent
from core.control_plane.breaker import BreakerKey, BreakerState, BreakerStore

# Reserved identity for the privacy filter's own breaker (independent domain).
PRIVACY_FILTER_AGENT_ID = "__privacy_filter__"
PRIVACY_FILTER_TOOL = "broadcast"
PRIVACY_FILTER_SESSION = "__privacy_filter_session__"


class PrivacyFilterError(Exception):
    """Raised when a broadcast is attempted while the filter breaker is OPEN."""


def privacy_filter_breaker_key(tenant_id: str) -> BreakerKey:
    """The privacy filter's own breaker key — never shares a tenant/agent/tool
    breaker, so the two failure domains stay independent (BRC-D5).
    """

    return BreakerKey(
        tenant_id=tenant_id,
        agent_id=PRIVACY_FILTER_AGENT_ID,
        tool=PRIVACY_FILTER_TOOL,
        session_id=PRIVACY_FILTER_SESSION,
    )


@dataclass
class PrivacyFilterInterface:
    """Gateway-side broadcast guard fronting the separate Privacy Filter (BRC-D5)."""

    breakers: BreakerStore
    audit: ControlPlaneAuditTrail

    def can_broadcast(self, tenant_id: str) -> bool:
        """True only if the filter breaker is not OPEN/HALF_OPEN for this tenant."""

        return self.breakers.state(privacy_filter_breaker_key(tenant_id)) is (
            BreakerState.CLOSED
        )

    def broadcast(self, tenant_id: str, payload_ref: str) -> str:
        """Attempt a broadcast. If the filter breaker is not CLOSED, nothing
        broadcasts (BRC-D5) — raises and writes a governance record.
        """

        if not self.can_broadcast(tenant_id):
            self.audit.record(
                ControlPlaneEvent.BROADCAST_BLOCKED,
                f"privacy filter breaker not CLOSED for tenant {tenant_id}; "
                "nothing broadcasts",
                tenant_id=tenant_id,
            )
            raise PrivacyFilterError(
                f"privacy filter breaker is OPEN for tenant {tenant_id!r}; "
                "broadcast refused"
            )
        return payload_ref


__all__ = [
    "PRIVACY_FILTER_AGENT_ID",
    "PRIVACY_FILTER_TOOL",
    "PRIVACY_FILTER_SESSION",
    "PrivacyFilterError",
    "privacy_filter_breaker_key",
    "PrivacyFilterInterface",
]
