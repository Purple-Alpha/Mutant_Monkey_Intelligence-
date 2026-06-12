"""ZeroDayCapture — Phase 5 (Layer 5), the novel-threat side channel.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D11 + §3.6.

A ``zero_day_candidate`` referred from the Layer 1 AttachmentSandbox (and never
folded into a Layer 4 verdict — that boundary is owned by the signed Phase 4
ReconciliationAgent) lands here. ZeroDayCapture packages the novel pattern and
routes the proposal to **Matt only** (``OPERATOR_IDENTITY``) — no tenant
operator, no auto-fan-out. A genuinely new threat is reviewed by one person
before it is allowed anywhere near the mutation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.operator_state.role_separation import OPERATOR_IDENTITY

# P5-D11: zero-day proposals route to Matt only.
ZERO_DAY_ROUTING_TARGET = OPERATOR_IDENTITY


class ZeroDayCaptureError(Exception):
    """Raised on a malformed zero-day referral (fails safe)."""


@dataclass(frozen=True)
class ZeroDayReferral:
    """A zero_day_candidate handed off from the AttachmentSandbox (Layer 1)."""

    candidate_id: str
    email_id: str
    tenant_id: str
    novelty_summary: str
    evidence_ref: str = ""


@dataclass(frozen=True)
class ZeroDayProposal:
    """A packaged novel-threat proposal addressed to Matt only (P5-D11)."""

    candidate_id: str
    routed_to: str
    novelty_summary: str
    referrals: tuple[ZeroDayReferral, ...]
    created_at: datetime


@dataclass
class ZeroDayCapture:
    """Collects zero-day referrals and routes proposals to Matt only."""

    _referrals: dict[str, list[ZeroDayReferral]] = field(default_factory=dict)

    def capture(self, referral: ZeroDayReferral) -> ZeroDayProposal:
        """Record a referral and return the Matt-only proposal for it."""

        if not referral.candidate_id:
            raise ZeroDayCaptureError("zero-day referral requires a candidate_id")
        if not referral.email_id or not referral.tenant_id:
            raise ZeroDayCaptureError(
                "zero-day referral requires both email_id and tenant_id"
            )

        bucket = self._referrals.setdefault(referral.candidate_id, [])
        bucket.append(referral)
        return self._proposal(referral.candidate_id)

    def proposal_for(self, candidate_id: str) -> ZeroDayProposal:
        if candidate_id not in self._referrals:
            raise ZeroDayCaptureError(
                f"no zero-day referrals captured for {candidate_id!r}"
            )
        return self._proposal(candidate_id)

    def _proposal(self, candidate_id: str) -> ZeroDayProposal:
        referrals = tuple(self._referrals[candidate_id])
        summary = referrals[-1].novelty_summary if referrals else ""
        return ZeroDayProposal(
            candidate_id=candidate_id,
            routed_to=ZERO_DAY_ROUTING_TARGET,
            novelty_summary=summary,
            referrals=referrals,
            created_at=datetime.now(timezone.utc),
        )
