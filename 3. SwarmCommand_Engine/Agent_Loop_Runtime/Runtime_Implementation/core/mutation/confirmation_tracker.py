"""ThreeShotConfirmationTracker — Phase 5 (Layer 5).

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D2 + §3.2 (stage 3 of the Anomaly Detection Pipeline).

A candidate pattern is ``validation_eligible`` only at the **3rd confirmation
that is distinct on BOTH ``email_id`` AND ``tenant_id``** (P5-D2). The counting
rule is deterministic and append-only:

- A confirmation **advances** the count only if its ``email_id`` is new AND its
  ``tenant_id`` is new for that candidate.
- A repeat ``email_id``, or a hit from an already-counted ``tenant_id``, does
  **not** advance — this blocks a single noisy tenant or a replayed case from
  mutating the swarm. One incident never mutates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

THREE_SHOT_THRESHOLD = 3


class ConfirmationError(Exception):
    """Raised on a malformed confirmation (fails safe)."""


@dataclass(frozen=True)
class Confirmation:
    """One independent confirmation of a candidate pattern."""

    candidate_id: str
    email_id: str
    tenant_id: str
    evidence_ref: str = ""


@dataclass
class _CandidateState:
    # Append-only log of every confirmation seen for this candidate.
    confirmations: list[Confirmation] = field(default_factory=list)
    # Sets of values that have already ADVANCED the count (P5-D2 independence).
    counted_emails: set[str] = field(default_factory=set)
    counted_tenants: set[str] = field(default_factory=set)
    independent_count: int = 0


@dataclass
class ThreeShotConfirmationTracker:
    """Append-only tracker enforcing distinct-email AND distinct-tenant 3-shot."""

    _state: dict[str, _CandidateState] = field(default_factory=dict)

    def record_confirmation(self, confirmation: Confirmation) -> int:
        """Record one confirmation; return the candidate's independent count.

        Advances the independent count only when BOTH ``email_id`` and
        ``tenant_id`` are new for this candidate (P5-D2). Always logs the
        confirmation (append-only), whether or not it advances.
        """

        if not confirmation.candidate_id:
            raise ConfirmationError("confirmation requires a candidate_id")
        if not confirmation.email_id or not confirmation.tenant_id:
            raise ConfirmationError(
                "confirmation requires both email_id and tenant_id (P5-D2)"
            )

        state = self._state.setdefault(confirmation.candidate_id, _CandidateState())
        state.confirmations.append(confirmation)

        email_is_new = confirmation.email_id not in state.counted_emails
        tenant_is_new = confirmation.tenant_id not in state.counted_tenants
        if email_is_new and tenant_is_new:
            state.counted_emails.add(confirmation.email_id)
            state.counted_tenants.add(confirmation.tenant_id)
            state.independent_count += 1

        return state.independent_count

    def independent_count(self, candidate_id: str) -> int:
        state = self._state.get(candidate_id)
        return state.independent_count if state else 0

    def is_validation_eligible(self, candidate_id: str) -> bool:
        """True once ``candidate_id`` has 3 distinct-email AND distinct-tenant hits."""

        return self.independent_count(candidate_id) >= THREE_SHOT_THRESHOLD

    def confirmations_for(self, candidate_id: str) -> tuple[Confirmation, ...]:
        state = self._state.get(candidate_id)
        return tuple(state.confirmations) if state else ()

    def evidence_chain(self, candidate_id: str) -> list[str]:
        """References (email_id@tenant_id[:evidence]) that advanced the count."""

        state = self._state.get(candidate_id)
        if not state:
            return []
        chain: list[str] = []
        seen_e: set[str] = set()
        seen_t: set[str] = set()
        for c in state.confirmations:
            if c.email_id not in seen_e and c.tenant_id not in seen_t:
                seen_e.add(c.email_id)
                seen_t.add(c.tenant_id)
                ref = f"{c.email_id}@{c.tenant_id}"
                if c.evidence_ref:
                    ref += f":{c.evidence_ref}"
                chain.append(ref)
        return chain
