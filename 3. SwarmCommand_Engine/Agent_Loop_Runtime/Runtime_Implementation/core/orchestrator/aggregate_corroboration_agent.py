"""Aggregate Corroboration Agent - first governed Layer 5 Challenge agent.

Implements the §11-signed Section 5 Agent Design Contract:
``4. Product_Roadmap/Aggregate_Corroboration_Agent_Design_Contract_Deep_Dive.md``.

This Stage 1 (Synthetic) agent reviews the full per-case contribution tuple and
returns one case-level ``ChallengeResult``. It is explicitly wired by callers and
is intentionally not registered in ``build_default_registry``.
"""

from __future__ import annotations

from .agent_contract import AgentContribution, ChallengeResult, MissionContext

AGGREGATE_CORROBORATION_AGENT_ID = "aggregate_corroboration_001"
AGGREGATE_CORROBORATION_LAYER = 5
AGGREGATE_CORROBORATION_AUTHORITY_LEVEL = 5

_HEADER_FACTS = frozenset(
    {
        "from_reply_to_divergence",
        "from_return_path_divergence",
        "from_sender_header_divergence",
    }
)
_AUTHENTICATION_FACTS = frozenset(
    {
        "spf_fail",
        "spf_softfail",
        "dkim_fail",
        "dmarc_fail",
    }
)
_THREAD_FACTS = frozenset({"ghost_thread_subject"})
_VERIFIED_SENDER_FACTS = frozenset(
    {
        "sender_domain_verified",
        "known_good_sender_verified",
        "trusted_sender_match",
    }
)


class AggregateCorroborationAgent:
    """Governed Layer 5 Challenge agent for aggregate email-fraud evidence."""

    agent_id: str = AGGREGATE_CORROBORATION_AGENT_ID
    layer: int = AGGREGATE_CORROBORATION_LAYER
    authority_level: int = AGGREGATE_CORROBORATION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError(
            "AggregateCorroborationAgent is Pass 2 only; Commander must not call analyze()"
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        if not contributions:
            return None

        facts = frozenset(
            fact
            for contribution in contributions
            for fact in contribution.observed_facts
        )
        surfaces = _attack_surfaces_for(facts)

        if facts & _VERIFIED_SENDER_FACTS and surfaces:
            return ChallengeResult(
                agent_id=self.agent_id,
                challenge_outcome="contradicted",
                challenge_basis=(
                    "Verified sender evidence contradicts spoofing indicators; "
                    "human review required."
                ),
            )

        if len(surfaces) >= 2:
            return ChallengeResult(
                agent_id=self.agent_id,
                challenge_outcome="confirmed",
                challenge_basis=_confirmed_basis(facts, surfaces),
            )

        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="inconclusive",
            challenge_basis=(
                "Evidence does not span independent surfaces enough to corroborate."
            ),
        )


def _attack_surfaces_for(facts: frozenset[str]) -> frozenset[str]:
    surfaces: set[str] = set()
    if facts & _HEADER_FACTS:
        surfaces.add("header")
    if facts & _AUTHENTICATION_FACTS:
        surfaces.add("authentication")
    if facts & _THREAD_FACTS:
        surfaces.add("thread")
    return frozenset(surfaces)


def _confirmed_basis(facts: frozenset[str], surfaces: frozenset[str]) -> str:
    if {"header", "authentication"} <= surfaces:
        if "dmarc_fail" in facts:
            return (
                "Reply-To divergence and DMARC failure independently indicate "
                "spoofed sending domain."
            )
        return (
            "Header divergence and authentication failure independently indicate "
            "spoofed sending domain."
        )
    if {"header", "thread"} <= surfaces:
        return (
            "Header divergence and ghost-thread context align with impersonation pattern."
        )
    if {"authentication", "thread"} <= surfaces:
        return (
            "Authentication failure and ghost-thread context align with impersonation pattern."
        )
    return "Independent email surfaces corroborate the same impersonation pattern."
