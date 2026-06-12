"""RollbackMechanism — Phase 5 (Layer 5), every deployment is reversible.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D5 + §3.5.

Before any mutation is deployed, the prior signed state is recorded. A
deterministic ``revert`` restores exactly that state. A live false-positive
spike above the conservative auto-rollback threshold trips an automatic revert —
the swarm protects the tenant before it protects the experiment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Launch-conservative auto-rollback trigger (P5-D10): if the post-deploy FP rate
# rises this far above the recorded baseline, auto-revert immediately.
DEFAULT_AUTO_ROLLBACK_FP_DELTA = 0.02


class RollbackError(Exception):
    """Raised when rollback is requested for an unknown/!deployed candidate."""


@dataclass(frozen=True)
class DeploymentState:
    """Immutable snapshot of the signed state a deployment replaced."""

    candidate_id: str
    tenant_scope: str
    prior_state: dict[str, Any]
    baseline_fp_rate: float
    recorded_at: datetime


@dataclass(frozen=True)
class RollbackOutcome:
    """Result of a revert — what state was restored and why."""

    candidate_id: str
    restored_state: dict[str, Any]
    reason: str
    automatic: bool
    reverted_at: datetime


@dataclass
class RollbackMechanism:
    """Records prior state per deployment and reverts deterministically (P5-D5)."""

    auto_rollback_fp_delta: float = DEFAULT_AUTO_ROLLBACK_FP_DELTA
    _active: dict[str, DeploymentState] = field(default_factory=dict)
    _reverted: dict[str, RollbackOutcome] = field(default_factory=dict)

    def record_deployment(
        self,
        *,
        candidate_id: str,
        tenant_scope: str,
        prior_state: dict[str, Any],
        baseline_fp_rate: float,
    ) -> DeploymentState:
        """Capture the prior signed state BEFORE the mutation goes live."""

        if not candidate_id:
            raise RollbackError("record_deployment requires a candidate_id")
        state = DeploymentState(
            candidate_id=candidate_id,
            tenant_scope=tenant_scope,
            # Defensive copy so later mutation of the caller's dict cannot
            # corrupt the recorded prior state.
            prior_state=dict(prior_state),
            baseline_fp_rate=baseline_fp_rate,
            recorded_at=datetime.now(timezone.utc),
        )
        self._active[candidate_id] = state
        return state

    def is_active(self, candidate_id: str) -> bool:
        return candidate_id in self._active

    def revert(self, candidate_id: str, *, reason: str = "manual revert") -> RollbackOutcome:
        """Deterministically restore the recorded prior state for a deployment."""

        return self._revert(candidate_id, reason=reason, automatic=False)

    def observe_false_positive_rate(
        self, candidate_id: str, *, observed_fp_rate: float
    ) -> RollbackOutcome | None:
        """Feed a live FP measurement; auto-revert if it spikes past threshold.

        Returns the ``RollbackOutcome`` if an automatic rollback fired, else
        ``None``. The swarm reverts to protect the tenant, not the experiment.
        """

        state = self._active.get(candidate_id)
        if state is None:
            raise RollbackError(
                f"no active deployment for candidate {candidate_id!r}"
            )
        delta = observed_fp_rate - state.baseline_fp_rate
        if delta > self.auto_rollback_fp_delta:
            reason = (
                f"auto-rollback: live FP rate {observed_fp_rate:.4f} is "
                f"{delta:+.4f} over baseline {state.baseline_fp_rate:.4f} "
                f"(threshold {self.auto_rollback_fp_delta:.4f})"
            )
            return self._revert(candidate_id, reason=reason, automatic=True)
        return None

    def _revert(
        self, candidate_id: str, *, reason: str, automatic: bool
    ) -> RollbackOutcome:
        state = self._active.pop(candidate_id, None)
        if state is None:
            raise RollbackError(
                f"cannot revert candidate {candidate_id!r}: no active deployment"
            )
        outcome = RollbackOutcome(
            candidate_id=candidate_id,
            restored_state=dict(state.prior_state),
            reason=reason,
            automatic=automatic,
            reverted_at=datetime.now(timezone.utc),
        )
        self._reverted[candidate_id] = outcome
        return outcome

    def last_rollback(self, candidate_id: str) -> RollbackOutcome | None:
        return self._reverted.get(candidate_id)
