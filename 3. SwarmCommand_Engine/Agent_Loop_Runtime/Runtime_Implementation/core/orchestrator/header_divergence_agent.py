"""Header Divergence governed-agent wrapper - first real detector on the
Blue-Team Swarm contract.

This is the runtime PROOF that the governed-agent contract
(``Agent`` protocol -> ``AgentContribution`` -> Swarm Commander ->
``DecisionEvidenceRecord``) holds when a real detector's output flows through
it, not a stub. It wraps the pure-function
``core.scoring.header_divergence_detector.score_header_divergence`` (a Layer 2
Detection signal) and exposes it as a governed agent.

Scope / governance boundary (deliberate):
- This is a proof of the contract, NOT a formal promotion. Header Analysis
  stays ``DETECTOR_FUNCTION`` on the 70-agent scoreboard until its Agent Design
  Contract wrapper spec is signed (the L2 promotion bar: signed contract +
  known-input tests + declared DER contribution). Because of that, this agent
  is intentionally NOT registered in ``build_default_registry``; callers wire it
  with an explicit registry entry until the wrapper is signed.
- Layer 2 Detection is facts-only: the contribution carries the detector's
  divergence indicators as ``observed_facts`` and emits NO interpretation /
  score / risk field (the promotion-bar rule, already enforced by the
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
from core.scoring.header_divergence_detector import score_header_divergence

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

HEADER_DIVERGENCE_AGENT_ID = "header_divergence_001"
HEADER_DIVERGENCE_LAYER = 2  # Detection
HEADER_DIVERGENCE_AUTHORITY_LEVEL = 3  # Specialist Agent (matches #10 / #21 wrappers)


def digest_email(payload: EmailInboundPayload) -> str:
    """SHA-256 hex digest of one inbound email, for ``MissionContext.inputs_digest``.

    Deterministic over the canonical JSON serialization of the payload; this is
    the ``inputs_digest`` of the material under review (raw hex, no prefix - the
    ``sha256:`` prefix convention is reserved for the DER ``evidence_anchor``).
    """

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


class HeaderDivergenceAgent:
    """Governed Layer 2 Detection agent wrapping the header-divergence detector."""

    agent_id: str = HEADER_DIVERGENCE_AGENT_ID
    layer: int = HEADER_DIVERGENCE_LAYER
    authority_level: int = HEADER_DIVERGENCE_AUTHORITY_LEVEL
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
        # carries the pointer, not the duplicated email body - see the
        # MissionContext docstring).
        if context.source_record_id is None:
            raise GovernanceError(
                "HeaderDivergenceAgent requires MissionContext.source_record_id "
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
        assessment = score_header_divergence(sender=email.sender, headers=email.headers)
        # Facts-only Detection contribution: the divergence indicators, not the
        # numeric score (no interpretation at Layer 2).
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=assessment.indicators,
        )

    def challenge(self, contribution: AgentContribution) -> ChallengeResult | None:
        # Detection layer does not run Pass 2.
        return None

    def persist_contribution(
        self,
        route_context: RouteContext,
        context: MissionContext,
        contribution: AgentContribution,
    ) -> RouteResult:
        """Write this agent's contribution to the Blackboard via the approved,
        registry-gated route (``source_agent`` must be this agent and its entry
        must allow ``RecordType.AGENT_CONTRIBUTION``)."""

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
