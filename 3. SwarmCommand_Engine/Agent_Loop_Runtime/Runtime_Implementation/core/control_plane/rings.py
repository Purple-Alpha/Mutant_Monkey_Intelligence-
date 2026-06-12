"""RingController — Phase 6 (Layer 6), Gate 3: staged deployment rings.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D6 + §3.5.

Four rings: **Ring 0 (synthetic) → Ring 1 (pilot) → Ring 2 (cohort) →
Ring 3 (full network)**. A candidate is promoted one ring at a time, and only
when promotion criteria pass **and** an **independent out-of-band verification**
is present (BRC-D6).

BRC-D6 metastasis test: an agent that **forges its own telemetry health
signals** cannot promote itself — agent-reported metrics alone are insufficient;
promotion requires the out-of-band verification token that the agent cannot
mint. Thresholds launch conservative and are amendment-tunable after real-tenant
baseline data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from core.control_plane.audit import ControlPlaneAuditTrail, ControlPlaneEvent


class Ring(IntEnum):
    RING_0_SYNTHETIC = 0
    RING_1_PILOT = 1
    RING_2_COHORT = 2
    RING_3_FULL = 3


class RingError(Exception):
    """Raised on malformed ring operations (fail-safe)."""


@dataclass(frozen=True)
class PromotionTelemetry:
    """Candidate-vs-baseline evidence for a promotion decision (BRC-D6).

    ``out_of_band_verified`` is the independent signal: it is set by the
    out-of-band verifier, NOT by the agent. ``agent_reported_healthy`` is the
    agent's own claim — necessary context, but never sufficient on its own.
    """

    regression_count: int
    anomaly_count: int
    token_cost_delta: float
    agent_reported_healthy: bool
    out_of_band_verified: bool


# Launch-conservative promotion thresholds (amendment-tunable, BRC-D6).
MAX_REGRESSIONS_FOR_PROMOTION = 0
MAX_ANOMALIES_FOR_PROMOTION = 0
MAX_TOKEN_COST_DELTA_FOR_PROMOTION = 0.10


@dataclass
class RingController:
    """Staged deployment rings with out-of-band-verified promotion (Gate 3)."""

    audit: ControlPlaneAuditTrail = field(default_factory=ControlPlaneAuditTrail)
    _ring_of: dict[str, Ring] = field(default_factory=dict)

    def assign(self, candidate_id: str, ring: Ring = Ring.RING_0_SYNTHETIC) -> Ring:
        if not candidate_id:
            raise RingError("candidate_id is required")
        self._ring_of[candidate_id] = ring
        return ring

    def ring_of(self, candidate_id: str) -> Ring:
        if candidate_id not in self._ring_of:
            raise RingError(f"unknown candidate {candidate_id!r}; assign first")
        return self._ring_of[candidate_id]

    def _criteria_pass(self, telemetry: PromotionTelemetry) -> bool:
        return (
            telemetry.regression_count <= MAX_REGRESSIONS_FOR_PROMOTION
            and telemetry.anomaly_count <= MAX_ANOMALIES_FOR_PROMOTION
            and telemetry.token_cost_delta <= MAX_TOKEN_COST_DELTA_FOR_PROMOTION
        )

    def promote(
        self, candidate_id: str, *, telemetry: PromotionTelemetry
    ) -> Ring:
        """Promote one ring up. Requires criteria to pass **and** independent
        out-of-band verification (BRC-D6). Agent-reported health alone never
        promotes — a forged telemetry signal is rejected here.
        """

        current = self.ring_of(candidate_id)
        if current is Ring.RING_3_FULL:
            raise RingError(f"candidate {candidate_id!r} is already at Ring 3")

        # BRC-D6 metastasis test: without the out-of-band signal, no promotion,
        # no matter what the agent reports about itself.
        if not telemetry.out_of_band_verified:
            self.audit.record(
                ControlPlaneEvent.RING_PROMOTION_REJECTED,
                f"candidate {candidate_id}: promotion requires independent "
                "out-of-band verification (agent-reported health insufficient)",
                agent_id=candidate_id,
            )
            raise RingError(
                f"candidate {candidate_id!r} promotion rejected: no out-of-band "
                "verification"
            )

        if not self._criteria_pass(telemetry):
            self.audit.record(
                ControlPlaneEvent.RING_PROMOTION_REJECTED,
                f"candidate {candidate_id}: promotion criteria failed "
                f"(regressions={telemetry.regression_count}, "
                f"anomalies={telemetry.anomaly_count}, "
                f"token_cost_delta={telemetry.token_cost_delta:+.3f})",
                agent_id=candidate_id,
            )
            raise RingError(
                f"candidate {candidate_id!r} promotion rejected: criteria failed"
            )

        promoted = Ring(current + 1)
        self._ring_of[candidate_id] = promoted
        self.audit.record(
            ControlPlaneEvent.RING_PROMOTED,
            f"candidate {candidate_id}: {current.name} → {promoted.name}",
            agent_id=candidate_id,
        )
        return promoted


__all__ = [
    "Ring",
    "RingError",
    "PromotionTelemetry",
    "MAX_REGRESSIONS_FOR_PROMOTION",
    "MAX_ANOMALIES_FOR_PROMOTION",
    "MAX_TOKEN_COST_DELTA_FOR_PROMOTION",
    "RingController",
]
