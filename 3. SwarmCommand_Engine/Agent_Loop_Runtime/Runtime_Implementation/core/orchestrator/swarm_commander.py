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

    def run_case(
        self,
        context: MissionContext,
        agents: Iterable[Agent],
        *,
        stage: str = "stage_a",
        anchor_provider: Callable[[], str | None] | None = None,
    ) -> DecisionEvidenceRecord:
        """Dispatch Stage A agents and assemble one in-memory DER.

        ``anchor_provider`` is an optional injection point for the future
        Evidence Package Agent; when absent, ``evidence_anchor`` stays ``None``
        (no sealing happens in this slice).
        """

        contributions: list[AgentContribution] = []
        for agent in agents:
            entry = self._entry_for(agent)
            self._assert_metadata_match(agent, entry)
            # Router guard runs before invocation: stage + autonomy gating. An
            # agent claiming autonomous action is rejected here in Stage A.
            validate_agent_dispatch(
                entry,
                stage=stage,
                requests_autonomous_action=agent.autonomous_action_allowed,
            )
            contribution = agent.analyze(context)
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

        # Challenge pass (Pass 2) is wired in a later slice; Stage A analyze-only
        # here, so challenge_pass is empty.
        challenge_pass: tuple[ChallengeResult, ...] = ()
        contributions_tuple = tuple(contributions)
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
