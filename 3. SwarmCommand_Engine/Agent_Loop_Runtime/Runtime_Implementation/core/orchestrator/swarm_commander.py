"""Swarm Commander case loop - build-order step 2 of the Blue-Team Swarm spine.

A thin orchestration layer on top of the locked contract types
(``agent_contract.py``), the registry dispatch metadata
(``AgentRegistryEntry``), and the router guard
(``routes.validate_agent_dispatch``). The Commander receives a case
``MissionContext``, dispatches Stage A agents through the shared ``Agent``
interface, collects their ``AgentContribution`` records, and assembles one
in-memory ``DecisionEvidenceRecord``.

Hard boundaries (Stage A only):
- No Blackboard persistence of the DER (the locked DER is a thin aggregation
  type, not a sealed record).
- No package generation / sealing (that is the Evidence Package Agent's slice);
  ``evidence_anchor`` stays ``None`` unless a caller injects an
  ``anchor_provider``.
- No autonomous action under any path; enforcement is in the Commander/router
  before invocation, never in the agent.
- The Commander never sets ``audit_record_id`` (Final Review Agent only, schema
  enforced).
- The optional Layer 5 challenge pass below is orchestration support only: this
  slice does not create, register, or promote any Challenge agent. A supplied
  challenge agent must already be passed in explicitly by the caller and still
  clears the same registry + Stage A/autonomy dispatch guard before invocation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone

from core.blackboard.models import AgentRegistryEntry, GovernanceError

from .agent_contract import (
    Agent,
    AgentContribution,
    ChallengeResult,
    DecisionEvidenceRecord,
    DecisionTimestamps,
    MissionContext,
    SwarmDisposition,
    slice_mission_context_for_agent,
)
from .routes import validate_agent_dispatch


def _determine_disposition(
    contributions: tuple[AgentContribution, ...],
    challenge_pass: tuple[ChallengeResult, ...],
) -> SwarmDisposition:
    """Deterministic, conservative v1 disposition rule (no risk arithmetic).

    Precedence (most cautious first):
    1. no contributions                          -> human_required
    2. any contradicted challenge                -> human_required
    3. any inconclusive challenge                -> hold
    4. any contribution verification contradicted -> hold
    5. all contribution facts empty              -> clear
    6. otherwise                                 -> suspicious
    """

    if not contributions:
        return "human_required"
    if any(result.challenge_outcome == "contradicted" for result in challenge_pass):
        return "human_required"
    if any(result.challenge_outcome == "inconclusive" for result in challenge_pass):
        return "hold"
    if any(
        contribution.verification_outcome == "contradicted"
        for contribution in contributions
    ):
        return "hold"
    if all(not contribution.observed_facts for contribution in contributions):
        return "clear"
    return "suspicious"


class SwarmCommander:
    """Stage A case-loop orchestrator over the shared agent interface."""

    def __init__(self, registry: dict[str, AgentRegistryEntry]) -> None:
        self._registry = registry

    def _entry_for(self, agent: Agent) -> AgentRegistryEntry:
        entry = self._registry.get(agent.agent_id)
        if entry is None:
            raise GovernanceError(f"unknown agent: {agent.agent_id}")
        return entry

    @staticmethod
    def _assert_metadata_match(agent: Agent, entry: AgentRegistryEntry) -> None:
        # A runtime agent must not claim authority that diverges from its signed
        # registry entry. Mismatch is rejected before any invocation.
        mismatches = [
            name
            for name in ("layer", "authority_level", "stage_allowed", "autonomous_action_allowed")
            if getattr(agent, name) != getattr(entry, name)
        ]
        if mismatches:
            raise GovernanceError(
                f"agent {agent.agent_id!r} metadata diverges from registry: "
                f"{', '.join(mismatches)}"
            )

    def _validate_agent_for_dispatch(
        self,
        agent: Agent,
        *,
        stage: str,
    ) -> AgentRegistryEntry:
        entry = self._entry_for(agent)
        self._assert_metadata_match(agent, entry)
        # Router guard runs before invocation: stage + autonomy gating. An
        # agent claiming autonomous action is rejected here in Stage A.
        validate_agent_dispatch(
            entry,
            stage=stage,
            requests_autonomous_action=agent.autonomous_action_allowed,
        )
        return entry

    def run_case(
        self,
        context: MissionContext,
        agents: Iterable[Agent],
        *,
        stage: str = "stage_a",
        challenge_agents: Iterable[Agent] = (),
        anchor_provider: Callable[[], str | None] | None = None,
    ) -> DecisionEvidenceRecord:
        """Dispatch Stage A agents and assemble one in-memory DER.

        ``anchor_provider`` is an optional injection point for the future
        Evidence Package Agent; when absent, ``evidence_anchor`` stays ``None``
        (no sealing happens in this slice).

        ``challenge_agents`` is the Pass-2 injection point for signed future
        Layer 5 agents. Supplying this iterable is explicit; the Commander does
        not discover, register, or promote Challenge agents on its own. Each
        Layer 5 agent is invoked once per case over the full per-case
        contribution set (aggregate review; Layer 5 spec D1/D2), returning one
        case-level verdict or ``None``.
        """

        contributions: list[AgentContribution] = []
        for agent in agents:
            self._validate_agent_for_dispatch(agent, stage=stage)
            agent_context = slice_mission_context_for_agent(
                context, agent.agent_id
            )
            contribution = agent.analyze(agent_context)
            if contribution.agent_id != agent.agent_id:
                raise GovernanceError(
                    f"contribution agent_id {contribution.agent_id!r} does not "
                    f"match dispatched agent {agent.agent_id!r}"
                )
            if contribution.layer != agent.layer:
                raise GovernanceError(
                    f"contribution layer {contribution.layer} does not match "
                    f"agent {agent.agent_id!r} layer {agent.layer}"
                )
            contributions.append(contribution)

        contributions_tuple = tuple(contributions)
        challenge_results: list[ChallengeResult] = []
        for challenge_agent in challenge_agents:
            self._validate_agent_for_dispatch(challenge_agent, stage=stage)
            if challenge_agent.layer != 5:
                raise GovernanceError(
                    f"challenge agent {challenge_agent.agent_id!r} must be "
                    "Layer 5 (Challenge/Red-Team)"
                )
            # Aggregate review (Layer 5 spec D1/D2): invoke each Layer 5 agent
            # once per case over the FULL contribution set, not once per
            # contribution. The agent returns one case-level verdict (or None).
            result = challenge_agent.challenge(contributions_tuple)
            if result is None:
                continue
            if result.agent_id != challenge_agent.agent_id:
                raise GovernanceError(
                    f"challenge result agent_id {result.agent_id!r} does not "
                    f"match challenge agent {challenge_agent.agent_id!r}"
                )
            challenge_results.append(result)

        challenge_pass = tuple(challenge_results)
        disposition = _determine_disposition(contributions_tuple, challenge_pass)
        human_state = "requested" if disposition == "human_required" else "not_required"
        evidence_anchor = anchor_provider() if anchor_provider is not None else None

        return DecisionEvidenceRecord(
            case_id=context.case_id,
            inputs_digest=context.inputs_digest,
            contributions=contributions_tuple,
            challenge_pass=challenge_pass,
            disposition=disposition,
            human_state=human_state,
            timestamps=DecisionTimestamps(detected_at=datetime.now(timezone.utc)),
            evidence_anchor=evidence_anchor,
        )
