"""Ghost Thread governed-agent wrapper - second real detector on the
Blue-Team Swarm contract.

This is the second runtime proof that the governed-agent contract
(``Agent`` protocol -> ``AgentContribution`` -> Swarm Commander ->
``DecisionEvidenceRecord``) holds when real detector output flows through it.
It wraps the pure-function
``core.scoring.ghost_thread_detector.score_ghost_thread`` (a Layer 2 Detection
signal) and exposes it as an explicitly-wired governed agent.

Scope / governance boundary (deliberate):
- Build authorization for this runtime proof is Matt's explicit 2026-06-07
  instruction to proceed with the "second existing detector wrapper" after the
  Header Analysis contract was signed. That instruction authorizes this proof
  slice only: wrapper + focused tests over the existing detector output.
- This is a proof of the contract, NOT a formal promotion. Reply-To Mismatch /
  Ghost Thread stays ``DETECTOR_FUNCTION`` on the 70-agent scoreboard until its
  Agent Design Contract wrapper spec is signed (the L2 promotion bar: signed
  contract + known-input tests + declared DER contribution). Because of that,
  this agent is intentionally NOT registered in ``build_default_registry``;
  callers wire it with an explicit registry entry until the wrapper is signed.
- Layer 2 Detection is facts-only: the contribution carries the detector's
  ghost-thread indicator as ``observed_facts`` and emits NO interpretation /
  score / risk field (the promotion-bar rule, enforced by the
  ``AgentContribution`` layer-field validator).
- Stage A only: analyze / recommend / evidence. ``challenge`` returns ``None``
  (Pass 2 is a Verification / Challenge-layer concern).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import UUID

from core.blackboard import (
    AgentContributionPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.scoring.ghost_thread_detector import score_ghost_thread

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

GHOST_THREAD_AGENT_ID = "ghost_thread_001"
GHOST_THREAD_LAYER = 2  # Detection
GHOST_THREAD_AUTHORITY_LEVEL = 3  # Specialist Agent (matches #6/#10/#21)


def digest_email(payload: EmailInboundPayload) -> str:
    """SHA-256 hex digest of one inbound email for ``MissionContext``."""

    return hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()


def contribution_payload_from(
    contribution: AgentContribution,
    *,
    case_id: UUID,
    inputs_digest: str,
) -> AgentContributionPayload:
    """Map an already-validated ``AgentContribution`` to its persistence payload."""

    return AgentContributionPayload(
        case_id=case_id,
        inputs_digest=inputs_digest,
        agent_id=contribution.agent_id,
        layer=contribution.layer,
        observed_facts=list(contribution.observed_facts),
        verification_source=contribution.verification_source,
        verification_outcome=contribution.verification_outcome,
        challenge_result=contribution.challenge_result,
        challenge_rationale=contribution.challenge_rationale,
        control_mapping=contribution.control_mapping,
        underwriter_note=contribution.underwriter_note,
    )


class GhostThreadAgent:
    """Governed Layer 2 Detection agent wrapping the ghost-thread detector."""

    agent_id: str = GHOST_THREAD_AGENT_ID
    layer: int = GHOST_THREAD_LAYER
    authority_level: int = GHOST_THREAD_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._environment = environment

    def _load_email(self, context: MissionContext) -> EmailInboundPayload:
        # Agents read the case's record from the Blackboard (MissionContext
        # carries the pointer, not the duplicated email body).
        if context.source_record_id is None:
            raise GovernanceError(
                "GhostThreadAgent requires MissionContext.source_record_id "
                "to locate the email_inbound record"
            )
        path = blackboard_path(self._blackboard_root, self._environment, context.tenant_id)
        for record in read_records(path):
            if record.record_id == context.source_record_id:
                if record.record_type != RecordType.EMAIL_INBOUND:
                    raise GovernanceError(
                        f"source record {context.source_record_id} is "
                        f"{record.record_type.value!r}, not an email_inbound record"
                    )
                return EmailInboundPayload.model_validate(record.payload)
        raise GovernanceError(
            f"email_inbound record {context.source_record_id} not found for "
            f"tenant {context.tenant_id!r}"
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        email = self._load_email(context)
        assessment = score_ghost_thread(subject=email.subject, headers=email.headers)
        # Facts-only Detection contribution: the ghost-thread indicator, not the
        # numeric score (no interpretation at Layer 2).
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=assessment.indicators,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        # Detection layer does not run Pass 2.
        return None

    def persist_contribution(
        self,
        route_context: RouteContext,
        context: MissionContext,
        contribution: AgentContribution,
    ) -> RouteResult:
        """Write this agent's contribution via the approved registry-gated route."""

        payload = contribution_payload_from(
            contribution,
            case_id=context.case_id,
            inputs_digest=context.inputs_digest,
        )
        return submit_agent_contribution(
            route_context,
            tenant_id=context.tenant_id,
            environment=self._environment,
            source_agent=self.agent_id,
            payload=payload,
            parent_record_id=context.source_record_id,
        )
