"""ReconciliationAgent — Phase 4 (Layer 4), the swarm's only verdict producer.

Governing contract
------------------
``4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md`` — §11 SIGNED
2026-06-11 (Matt Nichol), commit ``d0cc849``.
Pre-build amendments (§11 SIGNED 2026-06-11, ``f2219e3``):
  - ``RoleSeparationController_Amendment_CIRT.md`` — named CIRT role (P4-D2).
  - ``Agent_Health_Score_Rubric_Amendment_ReconciliationAgent.md`` — Layer 4
    scoring track.

What this is
------------
The ReconciliationAgent consumes every Layer 1 contribution for a single
``email_id`` (read tenant-isolated from the Phase 1 ``CanonicalEvidenceLedger``,
P4-D8), runs the three-voter ensemble (R1/R2/R3) **independently** (P4-D6), and
issues exactly one verdict (P4-D5) onto the Phase 4 ``VerdictLedger`` with a
plain-English evidence chain (§7). It does not re-inspect the raw email
(out of scope, §1).

Resolution (§4):
  - all three agree → ``UNANIMOUS`` at highest confidence;
  - 2-of-3 → ``MAJORITY``, dissenting vote always logged;
  - all three disagree → ``ESCALATE``, routed to the tenant's named CIRT
    individual (P4-D2); no automated verdict.

Special paths (§8):
  - ``spam_signal_only`` (ImageClassifier) routes to ``DELIVERY_PROBLEM``, never
    ``HIGH_RISK`` — surface/delivery signal, not fraud.
  - ``zero_day_candidate`` (AttachmentSandbox) is referred to the mutation
    engine separately and recorded (``zero_day_referred``); it does **not**
    change the verdict.

Deterministic lockdown (P4-D3): a resolved ``MEDIUM_RISK`` under Lung
``DEEP_BREATH`` is automatically promoted to ``HIGH_RISK``.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceType,
    EnsembleOutcome,
    ReconciliationVerdict,
    Verdict,
    VerdictLedger,
)
from core.operator_state import CIRTRegistry

from .voters import (
    LungState,
    R1SignalWeightVoter,
    R2PatternMatchVoter,
    R3ConflictResolutionVoter,
    VoterVote,
)

if TYPE_CHECKING:
    from core.orchestrator.dual_llm import EvidenceBundle

# Verdicts a voter may cast (the risk ladder). DELIVERY_PROBLEM / ESCALATE are
# ensemble-only outcomes (§4, §8), never an individual voter's cast.
_RISK_LADDER = (Verdict.HIGH_RISK, Verdict.MEDIUM_RISK, Verdict.LOW_RISK)


class ReconciliationError(Exception):
    """Raised on a malformed/empty contribution set — fails safe, never crashes."""


class ReconciliationAgent:
    """Layer 4 verdict agent. Three voters, best 2-of-3, one verdict surface."""

    AGENT_ID = "reconciliation_agent"

    def __init__(
        self,
        evidence_ledger: CanonicalEvidenceLedger,
        verdict_ledger: VerdictLedger,
        cirt_registry: CIRTRegistry | None = None,
    ) -> None:
        self._evidence_ledger = evidence_ledger
        self._verdict_ledger = verdict_ledger
        self._cirt_registry = cirt_registry
        # The three voters are independent objects; none holds a reference to
        # another, so no voter can observe another's vote (P4-D6).
        self._r1 = R1SignalWeightVoter()
        self._r2 = R2PatternMatchVoter()
        self._r3 = R3ConflictResolutionVoter()

    def analyze(
        self,
        *,
        tenant_id: str,
        email_id: str,
        lung_state: LungState = LungState.NORMAL,
    ) -> ReconciliationVerdict:
        """Reconcile all Layer 1 contributions for one email into one verdict.

        ``lung_state`` is the Lung dial input (§10); it reaches only the
        deterministic-lockdown step (P4-D3) and is never forwarded to any voter
        (P4-D4: R1 is isolated from human input).
        """

        if not tenant_id:
            raise ReconciliationError("tenant_id is required")
        if not email_id:
            raise ReconciliationError("email_id is required")

        # P4-D8: tenant-isolated read; cross-tenant contributions are never seen.
        tenant_entries = self._evidence_ledger.read_for_tenant(tenant_id)
        contributions = [c for c in tenant_entries if c.email_id == email_id]
        if not contributions:
            raise ReconciliationError(
                f"no Layer 1 contributions for tenant {tenant_id!r} email "
                f"{email_id!r}; cannot reconcile a verdict"
            )

        # --- Special paths (§8), evaluated independently of the verdict ---
        delivery_problem_path = self._has_flag(contributions, "spam_signal_only")
        zero_day_referred = self._has_flag(contributions, "zero_day_candidate")

        # --- Independent ensemble cast (P4-D6) — voters get contributions only ---
        r1 = self._r1.vote(contributions)
        r2 = self._r2.vote(contributions)
        r3 = self._r3.vote(contributions)

        outcome, resolved, overall_conf, minority = self._resolve(r1, r2, r3)

        lockdown_applied = False
        if delivery_problem_path:
            # §8: spam_signal_only is a delivery problem, never a fraud verdict.
            # This guarantees it can never route to HIGH_RISK (§12 immediate-fail).
            final_verdict = Verdict.DELIVERY_PROBLEM
        else:
            final_verdict = resolved
            # P4-D3 deterministic lockdown: MEDIUM_RISK + Deep breath = HIGH_RISK.
            if (
                final_verdict == Verdict.MEDIUM_RISK
                and lung_state == LungState.DEEP_BREATH
            ):
                final_verdict = Verdict.HIGH_RISK
                lockdown_applied = True

        cirt_individual = ""
        if self._cirt_registry is not None:
            cirt_individual = self._cirt_registry.bound_actor(tenant_id) or ""

        chain = self._plain_english_chain(
            final_verdict=final_verdict,
            outcome=outcome,
            contributions=contributions,
            votes=(r1, r2, r3),
            lockdown_applied=lockdown_applied,
            delivery_problem_path=delivery_problem_path,
            zero_day_referred=zero_day_referred,
            cirt_individual=cirt_individual,
        )

        verdict = ReconciliationVerdict(
            email_id=email_id,
            tenant_id=tenant_id,
            verdict=final_verdict,
            ensemble_outcome=outcome,
            overall_confidence=overall_conf,
            r1_vote=r1.verdict,
            r1_confidence=r1.confidence,
            r2_vote=r2.verdict,
            r2_confidence=r2.confidence,
            r3_vote=r3.verdict,
            r3_confidence=r3.confidence,
            minority_opinion=minority,
            contributing_evidence=[
                f"{c.evidence_type.value}:{c.entry_id}" for c in contributions
            ],
            plain_english_chain=chain,
            cirt_individual=cirt_individual,
            lockdown_applied=lockdown_applied,
            delivery_problem_path=delivery_problem_path,
            zero_day_referred=zero_day_referred,
        )
        return self._verdict_ledger.append(verdict)

    def analyze_bundle(
        self,
        *,
        bundle: "EvidenceBundle",
        lung_state: LungState = LungState.NORMAL,
    ) -> ReconciliationVerdict:
        """P-class Dual LLM entry point.

        The ReconciliationAgent receives only the deterministic
        ``EvidenceBundle`` assembled by the orchestrator: structured
        ``EvidenceLedgerEntry`` objects plus content hashes. It does not accept
        or inspect raw email text here (Dual LLM Rule 1).
        """

        if bundle.raw_text_present:
            raise ReconciliationError("EvidenceBundle may not contain raw email text")
        if not bundle.evidence_entries:
            raise ReconciliationError("EvidenceBundle has no evidence entries")

        ledger_entries = self._evidence_ledger.read_for_tenant(bundle.tenant_id)
        existing_ids = {entry.entry_id for entry in ledger_entries}
        for entry in bundle.evidence_entries:
            if entry.tenant_id != bundle.tenant_id or entry.email_id != bundle.email_id:
                raise ReconciliationError("EvidenceBundle evidence identity mismatch")
            if entry.entry_id not in existing_ids:
                self._evidence_ledger.append(entry)

        return self.analyze(
            tenant_id=bundle.tenant_id,
            email_id=bundle.email_id,
            lung_state=lung_state,
        )

    # ------------------------------------------------------------------ #

    @staticmethod
    def _has_flag(contributions: list[EvidenceLedgerEntry], flag: str) -> bool:
        return any(bool(c.details.get(flag)) for c in contributions)

    def _resolve(
        self, r1: VoterVote, r2: VoterVote, r3: VoterVote
    ) -> tuple[EnsembleOutcome, Verdict, float, str]:
        """Resolve three independent casts into (outcome, verdict, confidence, minority).

        - unanimous → that verdict at the mean (highest) confidence;
        - 2-of-3 → the majority verdict, dissenter logged as minority (§4);
        - all three distinct → ESCALATE, no verdict (§4); minority logs all.
        """

        votes = (r1, r2, r3)
        counts = Counter(v.verdict for v in votes)
        distinct = len(counts)

        if distinct == 1:
            verdict = r1.verdict
            confidence = self._mean_confidence(votes)
            return EnsembleOutcome.UNANIMOUS, verdict, confidence, ""

        if distinct == 2:
            majority_verdict, _ = counts.most_common(1)[0]
            majority = [v for v in votes if v.verdict == majority_verdict]
            dissent = [v for v in votes if v.verdict != majority_verdict]
            confidence = self._mean_confidence(majority)
            minority = "; ".join(
                f"{v.voter_id} dissented {v.verdict.value} "
                f"(confidence {v.confidence:.2f}): {v.rationale}"
                for v in dissent
            )
            return EnsembleOutcome.MAJORITY, majority_verdict, confidence, minority

        # All three disagree → ESCALATE (§4): no automated verdict.
        confidence = self._mean_confidence(votes)
        minority = "; ".join(
            f"{v.voter_id} voted {v.verdict.value} (confidence {v.confidence:.2f})"
            for v in votes
        )
        return EnsembleOutcome.ESCALATE, Verdict.ESCALATE, confidence, minority

    @staticmethod
    def _mean_confidence(votes: list[VoterVote] | tuple[VoterVote, ...]) -> float:
        if not votes:
            return 0.0
        return max(0.0, min(1.0, sum(v.confidence for v in votes) / len(votes)))

    def _plain_english_chain(
        self,
        *,
        final_verdict: Verdict,
        outcome: EnsembleOutcome,
        contributions: list[EvidenceLedgerEntry],
        votes: tuple[VoterVote, VoterVote, VoterVote],
        lockdown_applied: bool,
        delivery_problem_path: bool,
        zero_day_referred: bool,
        cirt_individual: str,
    ) -> str:
        """Operator-readable narrative (§7) — not a raw signal dump."""

        present_types = sorted({c.evidence_type.value for c in contributions})
        lines: list[str] = []

        if delivery_problem_path:
            lines.append(
                "This email looks like a bulk/spam delivery issue, not a fraud "
                "attempt: the image classifier raised a spam-only signal with no "
                "fraud indicators, so it is routed as a DELIVERY PROBLEM, not a "
                "risk verdict."
            )
        elif outcome == EnsembleOutcome.ESCALATE:
            who = cirt_individual or "the tenant's named incident responder"
            lines.append(
                "The three reviewers each reached a different conclusion, so no "
                f"automated verdict was issued. This has been escalated to {who} "
                "for human review."
            )
        elif outcome == EnsembleOutcome.UNANIMOUS:
            lines.append(
                f"All three independent reviewers agreed this email is "
                f"{final_verdict.value.replace('_', ' ').lower()}."
            )
        else:
            lines.append(
                "Two of the three independent reviewers agreed this email is "
                f"{final_verdict.value.replace('_', ' ').lower()}; the dissenting "
                "view is recorded below."
            )

        lines.append(
            "Evidence considered: " + ", ".join(present_types) + "."
        )
        for v in votes:
            lines.append(f"- {v.voter_id}: {v.rationale}")

        if lockdown_applied:
            lines.append(
                "Heightened-alert (Deep breath) was active, so a medium-risk "
                "result was automatically raised to HIGH RISK."
            )
        if zero_day_referred:
            lines.append(
                "An unknown (possible zero-day) attachment was referred to the "
                "mutation engine for separate analysis; this did not change the "
                "verdict above."
            )

        return "\n".join(lines)
