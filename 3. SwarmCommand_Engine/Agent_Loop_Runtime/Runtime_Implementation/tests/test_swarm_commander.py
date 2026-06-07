from uuid import uuid4

import pytest

from core.blackboard.models import (
    AgentRegistryEntry,
    AgentRole,
    Environment,
    GovernanceError,
    RecordType,
)
from core.orchestrator.agent_contract import (
    AgentContribution,
    ChallengeResult,
    MissionContext,
)
from core.orchestrator.swarm_commander import SwarmCommander, _determine_disposition


def _detection_entry(
    agent_id: str = "blue_detection_001",
    *,
    layer: int = 2,
    authority_level: int = 1,
    stage_allowed: str = "stage_a",
) -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Test Detection Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        layer=layer,
        authority_level=authority_level,
        stage_allowed=stage_allowed,
    )


class _StubAgent:
    """Minimal runtime Agent that satisfies the Agent Protocol."""

    def __init__(
        self,
        agent_id: str = "blue_detection_001",
        *,
        layer: int = 2,
        authority_level: int = 1,
        stage_allowed: str = "stage_a",
        autonomous_action_allowed: bool = False,
        observed_facts: tuple[str, ...] = ("sender_domain_mismatch",),
        verification_outcome: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.layer = layer
        self.authority_level = authority_level
        self.stage_allowed = stage_allowed
        self.autonomous_action_allowed = autonomous_action_allowed
        self._observed_facts = observed_facts
        self._verification_outcome = verification_outcome

    def analyze(self, context: MissionContext) -> AgentContribution:
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=self._observed_facts,
            verification_outcome=self._verification_outcome,
        )

    def challenge(self, contribution: AgentContribution):  # pragma: no cover
        raise AssertionError("challenge() must not be invoked in the Stage A case loop")


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)


def test_valid_detection_agent_produces_der_with_contribution():
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(_context(), [_StubAgent()])
    assert len(der.contributions) == 1
    assert der.contributions[0].agent_id == "blue_detection_001"
    assert der.disposition == "suspicious"


def test_der_never_carries_audit_record_id():
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(_context(), [_StubAgent()])
    assert der.audit_record_id is None
    assert der.audit_writer_agent_id is None
    assert der.evidence_anchor is None


def test_detection_agent_challenge_is_not_invoked():
    # _StubAgent.challenge raises; reaching here without error proves it was
    # never called by the Stage A case loop.
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(_context(), [_StubAgent()])
    assert der.challenge_pass == ()


def test_stage_ineligible_agent_is_rejected_before_analyze():
    entry = _detection_entry(stage_allowed="stage_b_c_only")
    agent = _StubAgent(stage_allowed="stage_b_c_only")
    commander = SwarmCommander({"blue_detection_001": entry})
    with pytest.raises(GovernanceError, match="cannot be dispatched"):
        commander.run_case(_context(), [agent])


def test_autonomous_action_agent_is_rejected_in_stage_a():
    # Registry entry cannot itself hold autonomous_action_allowed=True (model
    # forbids it), so a runtime agent claiming autonomy diverges from the
    # registry and is rejected as a metadata mismatch before invocation.
    entry = _detection_entry()
    agent = _StubAgent(autonomous_action_allowed=True)
    commander = SwarmCommander({"blue_detection_001": entry})
    with pytest.raises(GovernanceError, match="metadata diverges"):
        commander.run_case(_context(), [agent])


def test_contribution_layer_mismatch_is_rejected():
    # Registry says layer 2, runtime agent claims layer 2 (metadata matches) but
    # the analyze() output claims a different layer -> rejected.
    class _LyingAgent(_StubAgent):
        def analyze(self, context: MissionContext) -> AgentContribution:
            return AgentContribution(agent_id=self.agent_id, layer=3)

    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    with pytest.raises(GovernanceError, match="contribution layer"):
        commander.run_case(_context(), [_LyingAgent()])


def test_unknown_agent_is_rejected():
    commander = SwarmCommander({})
    with pytest.raises(GovernanceError, match="unknown agent"):
        commander.run_case(_context(), [_StubAgent()])


def test_anchor_provider_injection_sets_evidence_anchor():
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(
        _context(),
        [_StubAgent()],
        anchor_provider=lambda: "sha256:" + "b" * 64,
    )
    assert der.evidence_anchor == "sha256:" + "b" * 64


def test_no_contributions_disposition_is_human_required():
    commander = SwarmCommander({})
    der = commander.run_case(_context(), [])
    assert der.disposition == "human_required"
    assert der.human_state == "requested"


def test_empty_facts_disposition_is_clear():
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(_context(), [_StubAgent(observed_facts=())])
    assert der.disposition == "clear"


def test_determine_disposition_branches():
    facts = (AgentContribution(agent_id="a", layer=2, observed_facts=("x",)),)
    contradicted_challenge = (
        ChallengeResult(agent_id="c", challenge_outcome="contradicted", challenge_basis="x"),
    )
    inconclusive_challenge = (
        ChallengeResult(agent_id="c", challenge_outcome="inconclusive", challenge_basis="x"),
    )
    verification_contradicted = (
        AgentContribution(
            agent_id="v",
            layer=3,
            verification_outcome="contradicted",
        ),
    )
    assert _determine_disposition((), ()) == "human_required"
    assert _determine_disposition(facts, contradicted_challenge) == "human_required"
    assert _determine_disposition(facts, inconclusive_challenge) == "hold"
    assert _determine_disposition(verification_contradicted, ()) == "hold"
    assert _determine_disposition(facts, ()) == "suspicious"
