"""Section 5 tests for the first real Layer 5 Challenge agent.

The signed Agent Design Contract for ``AggregateCorroborationAgent`` requires
three classes of tests:

  Class 1 - Expected pass.
  Class 2 - Adversarial / break-it.
  Class 3 - Known-gap xfail.

These tests cover the agent behavior only. The Section 2/6 spine tests continue
to prove aggregate invocation and Commander disposition ownership.
"""

from __future__ import annotations

import pytest

from core.blackboard.models import AgentRegistryEntry, AgentRole, Environment, GovernanceError, RecordType
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext
from core.orchestrator.aggregate_corroboration_agent import (
    AGGREGATE_CORROBORATION_AGENT_ID,
    AggregateCorroborationAgent,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.swarm_commander import SwarmCommander


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)


def _detection_entry(agent_id: str = "blue_detection_001") -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Section 5 Detection Stub",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        layer=2,
        authority_level=1,
        stage_allowed="stage_a",
    )


def _challenge_entry(
    *,
    authority_level: int = 5,
) -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=AGGREGATE_CORROBORATION_AGENT_ID,
        display_name="Aggregate Corroboration Agent",
        role=AgentRole.BLUE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types=set(),
        layer=5,
        authority_level=authority_level,
        stage_allowed="stage_a",
    )


class _DetectionStub:
    def __init__(
        self,
        agent_id: str = "blue_detection_001",
        *,
        observed_facts: tuple[str, ...],
    ) -> None:
        self.agent_id = agent_id
        self.layer = 2
        self.authority_level = 1
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False
        self._observed_facts = observed_facts

    def analyze(self, context: MissionContext) -> AgentContribution:
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=self._observed_facts,
        )

    def challenge(self, contributions: tuple[AgentContribution, ...]):  # pragma: no cover
        raise AssertionError("challenge() must not be invoked on a Detection agent")


def _contribution(
    observed_facts: tuple[str, ...],
    *,
    agent_id: str = "blue_detection_001",
) -> AgentContribution:
    return AgentContribution(agent_id=agent_id, layer=2, observed_facts=observed_facts)


def _basis_for(result: ChallengeResult | None) -> str:
    assert result is not None
    return result.challenge_basis


# ===========================================================================
# Class 1 - Expected pass
# ===========================================================================


def test_two_independent_surfaces_confirm_with_surface_naming_basis():
    agent = AggregateCorroborationAgent()
    result = agent.challenge(
        (
            _contribution(("from_reply_to_divergence",), agent_id="header_divergence_001"),
            _contribution(("dmarc_fail",), agent_id="email_authentication_001"),
        )
    )

    assert result == ChallengeResult(
        agent_id=AGGREGATE_CORROBORATION_AGENT_ID,
        challenge_outcome="confirmed",
        challenge_basis=(
            "Reply-To divergence and DMARC failure independently indicate "
            "spoofed sending domain."
        ),
    )
    assert "Reply-To divergence" in result.challenge_basis
    assert "DMARC failure" in result.challenge_basis


def test_single_weak_contribution_with_benign_context_is_inconclusive():
    result = AggregateCorroborationAgent().challenge(
        (
            _contribution(
                (
                    "generic_greeting",
                    "benign_vendor_context",
                )
            ),
        )
    )

    assert result is not None
    assert result.challenge_outcome == "inconclusive"


def test_empty_contributions_returns_none():
    assert AggregateCorroborationAgent().challenge(()) is None


def test_verified_sender_fact_contradicts_spoofing_indicators():
    result = AggregateCorroborationAgent().challenge(
        (
            _contribution(("from_reply_to_divergence",), agent_id="header_divergence_001"),
            _contribution(("sender_domain_verified",), agent_id="verification_001"),
        )
    )

    assert result is not None
    assert result.challenge_outcome == "contradicted"
    assert "contradicts spoofing indicators" in result.challenge_basis


def test_contract_identity_and_static_safety_fields():
    agent = AggregateCorroborationAgent()

    assert agent.agent_id == AGGREGATE_CORROBORATION_AGENT_ID
    assert agent.layer == 5
    assert agent.authority_level == 5
    assert agent.stage_allowed == "stage_a"
    assert agent.autonomous_action_allowed is False
    with pytest.raises(AssertionError, match="Pass 2 only"):
        agent.analyze(_context())


def test_challenge_basis_length_limit_holds_for_all_non_none_paths():
    agent = AggregateCorroborationAgent()
    cases = [
        (
            _contribution(("from_reply_to_divergence",), agent_id="header_divergence_001"),
            _contribution(("dmarc_fail",), agent_id="email_authentication_001"),
        ),
        (_contribution(("generic_greeting",)),),
        (
            _contribution(("from_reply_to_divergence",), agent_id="header_divergence_001"),
            _contribution(("sender_domain_verified",), agent_id="verification_001"),
        ),
    ]

    for contributions in cases:
        result = agent.challenge(contributions)
        assert result is not None
        assert 1 <= len(result.challenge_basis) <= 160


def test_commander_accepts_authority_level_5_registry_entry():
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            AGGREGATE_CORROBORATION_AGENT_ID: _challenge_entry(authority_level=5),
        }
    )

    der = commander.run_case(
        _context(),
        [_DetectionStub(observed_facts=("from_reply_to_divergence",))],
        challenge_agents=[AggregateCorroborationAgent()],
    )

    assert der.challenge_pass[0].agent_id == AGGREGATE_CORROBORATION_AGENT_ID
    assert der.challenge_pass[0].challenge_outcome == "inconclusive"


def test_agent_is_not_registered_in_default_registry_at_stage_1():
    assert AGGREGATE_CORROBORATION_AGENT_ID not in build_default_registry()


# ===========================================================================
# Class 2 - Adversarial / break-it
# ===========================================================================


def test_vote_counting_probe_does_not_confirm_weak_non_overlapping_facts():
    result = AggregateCorroborationAgent().challenge(
        (
            _contribution(("generic_greeting",), agent_id="det_001"),
            _contribution(("new_vendor_request",), agent_id="det_002"),
            _contribution(("urgency_language",), agent_id="det_003"),
        )
    )

    assert result is not None
    assert result.challenge_outcome != "confirmed"


def test_confirmed_basis_is_not_count_language_and_names_surfaces():
    result = AggregateCorroborationAgent().challenge(
        (
            _contribution(("from_reply_to_divergence",), agent_id="header_divergence_001"),
            _contribution(("dmarc_fail",), agent_id="email_authentication_001"),
        )
    )
    basis = _basis_for(result)
    lower_basis = basis.lower()

    assert result is not None
    assert result.challenge_outcome == "confirmed"
    assert "reply-to divergence" in lower_basis
    assert "dmarc failure" in lower_basis
    for count_phrase in ("signals", "detectors", "majority", "count="):
        assert count_phrase not in lower_basis


def test_agent_never_returns_empty_basis_on_non_none_paths():
    agent = AggregateCorroborationAgent()
    cases = [
        (_contribution(("from_reply_to_divergence",)), _contribution(("dmarc_fail",))),
        (_contribution(("generic_greeting",)),),
        (_contribution(("from_reply_to_divergence",)), _contribution(("sender_domain_verified",))),
    ]

    for contributions in cases:
        result = agent.challenge(contributions)
        assert result is not None
        assert result.challenge_basis.strip()


def test_single_weak_signal_does_not_over_contradict():
    result = AggregateCorroborationAgent().challenge(
        (_contribution(("generic_greeting",)),)
    )

    assert result is not None
    assert result.challenge_outcome != "contradicted"
    assert result.challenge_outcome == "inconclusive"


def test_authority_level_3_registry_mismatch_is_blocked_before_invocation():
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            AGGREGATE_CORROBORATION_AGENT_ID: _challenge_entry(authority_level=3),
        }
    )

    with pytest.raises(GovernanceError, match="metadata diverges"):
        commander.run_case(
            _context(),
            [_DetectionStub(observed_facts=("from_reply_to_divergence",))],
            challenge_agents=[AggregateCorroborationAgent()],
        )


# ===========================================================================
# Class 3 - Known-gap xfail
# ===========================================================================


@pytest.mark.xfail(
    reason=(
        "KG-001: real-email verdict quality is blocked until Stage 2 real "
        "contribution sets exist. Completion: Stage 2 real-sample data intake gate."
    ),
    strict=False,
)
def test_known_gap_real_email_verdict_quality():
    real_stage2_samples_available = False
    assert real_stage2_samples_available, "KG-001 requires Stage 2 real samples"


@pytest.mark.xfail(
    reason=(
        "KG-002: second-Challenge-agent conflict is deferred per §10.A Q1 Option B. "
        "Completion: resolve in the second Challenge agent contract."
    ),
    strict=False,
)
def test_known_gap_second_challenge_agent_cross_arbitration():
    second_challenge_agent_contract_exists = False
    assert second_challenge_agent_contract_exists, (
        "KG-002 requires a second Challenge agent contract"
    )
