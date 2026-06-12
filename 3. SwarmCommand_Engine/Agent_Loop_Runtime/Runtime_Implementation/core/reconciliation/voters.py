"""The three independent voters of the ReconciliationAgent ensemble — Phase 4.

Governing contract
------------------
``4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md`` — §11 SIGNED
2026-06-11 (Matt Nichol), commit ``d0cc849`` — §3 (the three-voter ensemble).

Each voter is a pure function of the Layer 1 contributions for one email. The
``vote`` method takes **only** the contributions list — there is no parameter
through which a voter could see another voter's vote (P4-D6 independence), and
no parameter through which the attacker-sophistication rubric could reach R1
(P4-D4: R1 is numbers from Layer 1 contributions only). Each returns a
``VoterVote`` carrying one of the risk-ladder verdicts (``HIGH_RISK`` /
``MEDIUM_RISK`` / ``LOW_RISK``) and a confidence in ``0.0-1.0``. The
ensemble-only verdicts (``DELIVERY_PROBLEM``, ``ESCALATE``) are produced by the
ReconciliationAgent, not by individual voters (§4, §8).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from statistics import fmean

from core.blackboard import EvidenceLedgerEntry, EvidenceType, Verdict


class LungState(str, Enum):
    """Lung dial state reaching the agent (§10). The Lung is a separate contract;
    here it is an input. Under ``DEEP_BREATH`` the P4-D3 deterministic lockdown
    applies."""

    NORMAL = "normal"
    DEEP_BREATH = "deep_breath"


@dataclass(frozen=True)
class VoterVote:
    """One voter's independent cast: a risk-ladder verdict + confidence + why."""

    voter_id: str
    verdict: Verdict
    confidence: float
    rationale: str


# Boolean detail flags that indicate an active fraud pattern. R2 reasons over
# these (the *shape* of the evidence); R3 uses them as corroboration. R1 never
# reads them (numbers only, P4-D4).
_FRAUD_FLAGS: tuple[str, ...] = (
    "bec_pattern_match",
    "wire_transfer_request",
    "ceo_impersonation_flag",
    "malicious_url_detected",
    "credential_harvest_flag",
    "redirect_chain_anomaly",
    "urgency_detected",
    "known_malicious_hash",
    "network_callback_detected",
    "file_drop_detected",
    "ai_generated_detected",
)

# Numeric detail fields R1 aggregates alongside the contribution confidences.
_NUMERIC_SIGNAL_FIELDS: tuple[str, ...] = (
    "reputation_score",
    "sentiment_score",
    "image_text_ratio",
)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _flag_present(contributions: list[EvidenceLedgerEntry], flag: str) -> bool:
    return any(bool(c.details.get(flag)) for c in contributions)


def _any_fraud_flag(contributions: list[EvidenceLedgerEntry]) -> bool:
    return any(_flag_present(contributions, flag) for flag in _FRAUD_FLAGS)


class R1SignalWeightVoter:
    """R1 — Signal Weight Voter (§3.1). Quantitative, numbers only.

    Aggregates the ``confidence`` values and numeric signal strengths of every
    contribution into one weighted score and maps it onto the risk ladder. It
    reads **no** boolean pattern flags and **no** human/sophistication input
    (P4-D4): ``vote`` accepts only the contributions list, so the rubric has no
    path in.
    """

    VOTER_ID = "R1"

    HIGH_THRESHOLD = 0.75
    MEDIUM_THRESHOLD = 0.40

    def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
        confidences = [c.confidence for c in contributions]
        mean_conf = fmean(confidences) if confidences else 0.0

        numeric_signals: list[float] = []
        for c in contributions:
            for field in _NUMERIC_SIGNAL_FIELDS:
                value = c.details.get(field)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_signals.append(float(value))
        peak_signal = max(numeric_signals) if numeric_signals else 0.0

        risk = _clamp(0.65 * mean_conf + 0.35 * peak_signal)
        if risk >= self.HIGH_THRESHOLD:
            verdict = Verdict.HIGH_RISK
        elif risk >= self.MEDIUM_THRESHOLD:
            verdict = Verdict.MEDIUM_RISK
        else:
            verdict = Verdict.LOW_RISK

        rationale = (
            f"Weighted signal score {risk:.2f} across {len(contributions)} "
            f"contributions (mean confidence {mean_conf:.2f}, peak numeric "
            f"signal {peak_signal:.2f})."
        )
        return VoterVote(self.VOTER_ID, verdict, _clamp(risk), rationale)


class R2PatternMatchVoter:
    """R2 — Pattern Match Voter (§3.2). Does the combination match a known profile?

    Reasons over the *shape* of the combined evidence against the Layer 0 threat
    profiles (phish / BEC / ransomware / trojan delivery), not the raw numbers.
    A full known-threat profile is ``HIGH_RISK``; a single fraud indicator is
    ``MEDIUM_RISK``; nothing matching is ``LOW_RISK``.
    """

    VOTER_ID = "R2"

    def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
        def present(flag: str) -> bool:
            return _flag_present(contributions, flag)

        # Known full threat profiles (combinations that match a Layer 0 pattern).
        high_profiles = {
            "known_malicious_payload": present("known_malicious_hash"),
            "credential_phishing": present("malicious_url_detected")
            and present("credential_harvest_flag"),
            "bec_wire_fraud": present("bec_pattern_match")
            and present("wire_transfer_request"),
            "ceo_impersonation_wire": present("ceo_impersonation_flag")
            and present("wire_transfer_request"),
        }
        matched_high = [name for name, hit in high_profiles.items() if hit]

        any_single = _any_fraud_flag(contributions)

        if matched_high:
            verdict = Verdict.HIGH_RISK
            confidence = 0.9
            rationale = (
                "Evidence combination matches known threat profile(s): "
                + ", ".join(sorted(matched_high))
                + "."
            )
        elif any_single:
            verdict = Verdict.MEDIUM_RISK
            confidence = 0.65
            present_flags = sorted(f for f in _FRAUD_FLAGS if present(f))
            rationale = (
                "Partial pattern match — isolated fraud indicator(s) without a "
                "full known-threat profile: " + ", ".join(present_flags) + "."
            )
        else:
            verdict = Verdict.LOW_RISK
            confidence = 0.55
            rationale = "No combination matches a known Layer 0 threat profile."

        return VoterVote(self.VOTER_ID, verdict, _clamp(confidence), rationale)


class R3ConflictResolutionVoter:
    """R3 — Conflict Resolution Voter (§3.3). Disagreement is signal, not noise.

    Targets the case where Layer 1 agents *contradict* one another — the
    Ukraine-IP-vs-40-prior-emails scenario: a high-risk geo origin that
    contradicts a long established sender history. A conflict corroborated by an
    active fraud indicator is ``HIGH_RISK``; a bare conflict (risky origin from an
    otherwise trusted sender) is ``MEDIUM_RISK`` and warrants review; with no
    conflict R3 defers to a moderate stance (``MEDIUM_RISK`` if fraud signal,
    else ``LOW_RISK``).
    """

    VOTER_ID = "R3"

    def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
        geo = [c for c in contributions if c.evidence_type == EvidenceType.GEO_SIGNAL]
        sender = [
            c for c in contributions if c.evidence_type == EvidenceType.SENDER_SIGNAL
        ]

        geo_risky = any(
            bool(c.details.get("high_risk_region"))
            or bool(c.details.get("velocity_flag"))
            or bool(c.details.get("vpn_detected"))
            for c in geo
        )
        sender_established = any(
            bool(c.details.get("known_contact"))
            or bool(c.details.get("established_vendor"))
            or int(c.details.get("prior_interaction_count", 0) or 0) > 0
            for c in sender
        )
        conflict = geo_risky and sender_established
        corroborating_fraud = _any_fraud_flag(contributions)

        if conflict and corroborating_fraud:
            verdict = Verdict.HIGH_RISK
            confidence = 0.85
            rationale = (
                "Risky origin contradicts an established sender history AND an "
                "active fraud indicator corroborates the conflict — the "
                "contradiction is itself strong signal."
            )
        elif conflict:
            verdict = Verdict.MEDIUM_RISK
            confidence = 0.7
            rationale = (
                "Risky/anomalous origin from an otherwise established sender "
                "(geo-vs-history conflict) with no corroborating fraud "
                "indicator — flagged for review, not auto-condemned."
            )
        elif corroborating_fraud:
            verdict = Verdict.MEDIUM_RISK
            confidence = 0.6
            rationale = (
                "Fraud indicators present but Layer 1 agents do not contradict "
                "one another — no conflict to adjudicate; moderate stance."
            )
        else:
            verdict = Verdict.LOW_RISK
            confidence = 0.55
            rationale = "No inter-agent conflict and no fraud indicators."

        return VoterVote(self.VOTER_ID, verdict, _clamp(confidence), rationale)
