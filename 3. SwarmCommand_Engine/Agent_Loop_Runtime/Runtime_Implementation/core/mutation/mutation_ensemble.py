"""MutationEngineEnsemble — Phase 5 (Layer 5), the swarm-level evolution surface.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol).

This is scoreboard row #88 — one ensemble (P5-D9, single row) wiring the six
Phase 5 components together and walking the named **Anomaly Detection Pipeline**
(§3.3.1). Nothing is stamped "Mutant Monkey standard" until it clears every
gate. The pipeline is sandbox-only until the human sign-off stage; production
deployment is reversible by construction (RollbackMechanism).

The seven pipeline stages (§3.3.1):

  1. Anomaly detected — flagged, not acted on.
  2. Laws-of-average baseline comparison — genuine outlier vs edge-case variation.
  3. 3-shot confirmation — distinct ``email_id`` AND distinct ``tenant_id``.
  4. ValidationGate benign-stream test — false-positive risk check.
  5. Human sign-off — Matt approves before deployment.
  6. Conservative threshold testing — defined cycle count before a threshold locks
     (carried inside the ValidationGate's cycle config — P5-D10).
  7. Amendment path — thresholds adjust from real data via signed amendment, never
     autonomously (a governance discipline, not a per-candidate gate).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.mutation.audit_trail import (
    MutationAuditEntry,
    MutationAuditTrail,
    MutationStage,
)
from core.mutation.confirmation_tracker import (
    Confirmation,
    ThreeShotConfirmationTracker,
)
from core.mutation.rollback import RollbackMechanism, RollbackOutcome
from core.mutation.sign_off_gate import (
    HumanSignOffGate,
    MutationProposal,
    SignOffError,
)
from core.mutation.validation_gate import BenignStream, ValidationGate
from core.mutation.zero_day_capture import ZeroDayCapture, ZeroDayReferral

# Stage 2 — laws-of-average outlier sensitivity. A candidate is a "genuine
# outlier" worth pursuing only when its observed signal sits this many standard
# deviations off the running baseline mean. Launch-conservative (P5-D10): a high
# bar so normal edge-case variation is filtered out, not mutated on.
DEFAULT_OUTLIER_SIGMA = 3.0


class MutationEnsembleError(Exception):
    """Raised on malformed pipeline input (fails safe — no mutation)."""


@dataclass(frozen=True)
class AnomalyCandidate:
    """A flagged anomaly entering the pipeline at stage 1."""

    candidate_id: str
    tenant_scope: str
    anomaly_summary: str
    observed_signal: float
    baseline_mean: float
    baseline_stddev: float
    baseline_fp_rate: float
    prior_state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    """Outcome of one pipeline walk for a candidate."""

    candidate_id: str
    stage_reached: MutationStage
    stamped: bool          # cleared every gate → eligible for sign-off + deploy
    rejected: bool         # tripped a hard safety gate (validation)
    reason: str
    evidence_chain: tuple[str, ...]


def _is_genuine_outlier(
    candidate: AnomalyCandidate, *, sigma: float
) -> bool:
    """Laws-of-average test (stage 2): outlier vs normal edge-case variation."""

    if candidate.baseline_stddev <= 0.0:
        # No spread recorded — treat any nonzero deviation as an outlier so a
        # flat/empty baseline cannot silently swallow a real novel signal.
        return candidate.observed_signal != candidate.baseline_mean
    deviation = abs(candidate.observed_signal - candidate.baseline_mean)
    return deviation >= sigma * candidate.baseline_stddev


@dataclass
class MutationEngineEnsemble:
    """Row #88 — the six-component Phase 5 mutation ensemble (P5-D9)."""

    audit_trail: MutationAuditTrail
    sign_off_gate: HumanSignOffGate
    tracker: ThreeShotConfirmationTracker = field(
        default_factory=ThreeShotConfirmationTracker
    )
    validation_gate: ValidationGate = field(default_factory=ValidationGate)
    rollback: RollbackMechanism = field(default_factory=RollbackMechanism)
    zero_day_capture: ZeroDayCapture = field(default_factory=ZeroDayCapture)
    outlier_sigma: float = DEFAULT_OUTLIER_SIGMA

    # -- confirmation intake -------------------------------------------------

    def record_confirmation(self, confirmation: Confirmation) -> int:
        """Forward an independent confirmation to the 3-shot tracker."""

        return self.tracker.record_confirmation(confirmation)

    def capture_zero_day(self, referral: ZeroDayReferral):
        """Route a zero_day_candidate to Matt only (P5-D11). Side channel."""

        return self.zero_day_capture.capture(referral)

    # -- the named Anomaly Detection Pipeline (§3.3.1) -----------------------

    def run_pipeline(
        self,
        candidate: AnomalyCandidate,
        *,
        benign_stream: BenignStream,
    ) -> PipelineResult:
        """Walk a candidate through stages 1-4, recording audit at each step.

        Stage 5 (human sign-off) is a separate, operator-initiated action; a
        stamped result here means the candidate is *eligible* for sign-off, not
        that it has been deployed. Returns at the first stage that does not
        advance, with the audit trail reflecting exactly how far it got.
        """

        if not candidate.candidate_id:
            raise MutationEnsembleError("candidate requires a candidate_id")

        evidence = self.tracker.evidence_chain(candidate.candidate_id)

        # Stage 1 — anomaly flagged, NOT acted on.
        self._audit(
            candidate,
            MutationStage.ANOMALY_FLAGGED,
            detail=candidate.anomaly_summary,
            evidence=evidence,
            outcome="flagged",
        )

        # Stage 2 — laws-of-average baseline comparison.
        if not _is_genuine_outlier(candidate, sigma=self.outlier_sigma):
            reason = (
                "stage 2: within normal variation (not a genuine outlier at "
                f"{self.outlier_sigma}σ) — filtered, no mutation"
            )
            self._audit(
                candidate,
                MutationStage.BASELINE_COMPARED,
                detail=reason,
                evidence=evidence,
                outcome="filtered",
            )
            return PipelineResult(
                candidate_id=candidate.candidate_id,
                stage_reached=MutationStage.BASELINE_COMPARED,
                stamped=False,
                rejected=False,
                reason=reason,
                evidence_chain=tuple(evidence),
            )
        self._audit(
            candidate,
            MutationStage.BASELINE_COMPARED,
            detail="genuine outlier confirmed vs laws-of-average baseline",
            evidence=evidence,
            outcome="outlier",
        )

        # Stage 3 — 3-shot confirmation (distinct email_id AND tenant_id).
        if not self.tracker.is_validation_eligible(candidate.candidate_id):
            count = self.tracker.independent_count(candidate.candidate_id)
            reason = (
                f"stage 3: only {count}/3 independent confirmations "
                "(distinct email_id AND tenant_id) — awaiting confirmation"
            )
            return PipelineResult(
                candidate_id=candidate.candidate_id,
                stage_reached=MutationStage.BASELINE_COMPARED,
                stamped=False,
                rejected=False,
                reason=reason,
                evidence_chain=tuple(evidence),
            )
        self._audit(
            candidate,
            MutationStage.THREE_SHOT_CONFIRMED,
            detail="3 independent confirmations across distinct email_id AND tenant_id",
            evidence=evidence,
            outcome="confirmed",
        )

        # Stage 4 — ValidationGate benign-stream FP check (+ stage 6 cycle count).
        result = self.validation_gate.validate(
            candidate.candidate_id,
            baseline_fp_rate=candidate.baseline_fp_rate,
            benign_stream=benign_stream,
        )
        if not result.passed:
            self._audit(
                candidate,
                MutationStage.REJECTED,
                detail=result.reason,
                evidence=evidence,
                outcome="rejected",
            )
            return PipelineResult(
                candidate_id=candidate.candidate_id,
                stage_reached=MutationStage.REJECTED,
                stamped=False,
                rejected=True,
                reason=result.reason,
                evidence_chain=tuple(evidence),
            )
        self._audit(
            candidate,
            MutationStage.VALIDATION_PASSED,
            detail=result.reason,
            evidence=evidence,
            outcome="validated",
        )

        # Cleared every automatic gate → eligible for human sign-off (stage 5).
        return PipelineResult(
            candidate_id=candidate.candidate_id,
            stage_reached=MutationStage.VALIDATION_PASSED,
            stamped=True,
            rejected=False,
            reason="cleared stages 1-4; eligible for human sign-off (stage 5)",
            evidence_chain=tuple(evidence),
        )

    # -- stage 5 + deployment ------------------------------------------------

    def deploy(
        self,
        candidate: AnomalyCandidate,
        *,
        actor_id: str,
    ) -> RollbackOutcome | None:
        """Deploy a signed-off candidate. Requires stage-5 sign-off (P5-D4).

        Records the prior signed state with the RollbackMechanism BEFORE going
        live (P5-D5), then writes the DEPLOYED audit entry naming the signer.
        Returns ``None`` (deployment active); the rollback handle lives on
        ``self.rollback``.
        """

        record = self.sign_off_gate.require_sign_off(candidate.candidate_id)
        self.rollback.record_deployment(
            candidate_id=candidate.candidate_id,
            tenant_scope=candidate.tenant_scope,
            prior_state=candidate.prior_state,
            baseline_fp_rate=candidate.baseline_fp_rate,
        )
        self._audit(
            candidate,
            MutationStage.DEPLOYED,
            detail="deployed to production with reversible prior-state record",
            evidence=self.tracker.evidence_chain(candidate.candidate_id),
            signer=record.signer_id,
            outcome="deployed",
        )
        return None

    def observe_post_deploy_fp(
        self, candidate: AnomalyCandidate, *, observed_fp_rate: float
    ) -> RollbackOutcome | None:
        """Feed a live FP measurement; auto-rollback on a conservative spike."""

        outcome = self.rollback.observe_false_positive_rate(
            candidate.candidate_id, observed_fp_rate=observed_fp_rate
        )
        if outcome is not None:
            self._audit(
                candidate,
                MutationStage.ROLLED_BACK,
                detail=outcome.reason,
                evidence=(),
                outcome="rolled_back",
            )
        return outcome

    # -- internal ------------------------------------------------------------

    def _audit(
        self,
        candidate: AnomalyCandidate,
        stage: MutationStage,
        *,
        detail: str,
        evidence,
        outcome: str,
        signer: str = "",
    ) -> MutationAuditEntry:
        return self.audit_trail.append(
            MutationAuditEntry(
                candidate_id=candidate.candidate_id,
                tenant_scope=candidate.tenant_scope or "sandbox",
                stage=stage,
                detail=detail,
                evidence_chain=list(evidence),
                signer=signer,
                outcome=outcome,
            )
        )


__all__ = [
    "AnomalyCandidate",
    "DEFAULT_OUTLIER_SIGMA",
    "MutationEngineEnsemble",
    "MutationEnsembleError",
    "PipelineResult",
]
