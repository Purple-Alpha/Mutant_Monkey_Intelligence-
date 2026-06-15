"""TenantSegmentationController — Phase 6 (Layer 6), Gate 2: blast-radius segmentation.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D4 + §3.4.

**Tenant is a first-class fault domain.** Each registered tenant gets its own
**queue**, **rate limit**, and **credential**. A failure (or rate-limit breach)
in one tenant does not cascade into another.

BRC-D4 metastasis test: a **forged `tenant_id`** in a payload is rejected by the
identity layer regardless of content. This controller enforces the second half
of that property — an action whose resolved identity tenant does not match the
tenant whose segment it is trying to use is rejected here, so a payload cannot
smuggle itself into another tenant's fault domain.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import re


class SegmentationError(Exception):
    """Raised on a cross-tenant violation or unknown tenant (fail-safe)."""


_TENANT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _validate_tenant_id(tenant_id: str) -> None:
    """Reject routing-key delimiters/control/path syntax at ingress.

    Tenant IDs are routing keys, not free text. Hyphen/underscore are retained
    for the repo's existing tenant naming convention; delimiter/path/control
    characters are fail-closed rather than normalized.
    """

    if not isinstance(tenant_id, str) or not tenant_id:
        raise SegmentationError("tenant_id is required")
    if not _TENANT_ID_RE.fullmatch(tenant_id):
        raise SegmentationError(f"invalid tenant_id routing key {tenant_id!r}")
    if "--" in tenant_id:
        raise SegmentationError(f"invalid tenant_id routing key {tenant_id!r}")


@dataclass
class _TenantSegment:
    credential: str
    rate_limit_per_window: int
    queue: deque[str] = field(default_factory=deque)
    window_count: int = 0


@dataclass
class TenantSegmentationController:
    """Per-tenant queues, rate limits, and credentials (Gate 2, BRC-D4)."""

    _segments: dict[str, _TenantSegment] = field(default_factory=dict)

    def register_tenant(
        self, tenant_id: str, *, credential: str, rate_limit_per_window: int = 100
    ) -> None:
        _validate_tenant_id(tenant_id)
        if not credential:
            raise SegmentationError("tenant registration requires tenant_id + credential")
        self._segments[tenant_id] = _TenantSegment(
            credential=credential,
            rate_limit_per_window=rate_limit_per_window,
        )

    def _segment(self, tenant_id: str) -> _TenantSegment:
        _validate_tenant_id(tenant_id)
        seg = self._segments.get(tenant_id)
        if seg is None:
            raise SegmentationError(f"unknown tenant segment {tenant_id!r}")
        return seg

    def verify_tenant_binding(
        self, *, resolved_tenant_id: str, claimed_tenant_id: str, credential: str
    ) -> None:
        """Reject a forged tenant binding (BRC-D4 metastasis test). The resolved
        identity tenant, the claimed payload tenant, and the segment credential
        must all agree — content is never consulted.
        """

        _validate_tenant_id(resolved_tenant_id)
        _validate_tenant_id(claimed_tenant_id)
        if resolved_tenant_id != claimed_tenant_id:
            raise SegmentationError(
                f"forged tenant_id: identity resolved {resolved_tenant_id!r} but "
                f"payload claims {claimed_tenant_id!r}"
            )
        seg = self._segment(claimed_tenant_id)
        if seg.credential != credential:
            raise SegmentationError(
                f"tenant credential mismatch for {claimed_tenant_id!r}"
            )

    def enqueue(self, tenant_id: str, item: str) -> None:
        """Enqueue work into a tenant's own queue. Enforces the per-tenant rate
        limit; a breach raises for that tenant only and never touches another
        tenant's segment.
        """

        seg = self._segment(tenant_id)
        if seg.window_count >= seg.rate_limit_per_window:
            raise SegmentationError(
                f"tenant {tenant_id!r} rate limit reached "
                f"({seg.rate_limit_per_window}/window)"
            )
        seg.window_count += 1
        seg.queue.append(item)

    def queue_depth(self, tenant_id: str) -> int:
        return len(self._segment(tenant_id).queue)

    def reset_window(self, tenant_id: str) -> None:
        self._segment(tenant_id).window_count = 0


__all__ = [
    "SegmentationError",
    "TenantSegmentationController",
]
