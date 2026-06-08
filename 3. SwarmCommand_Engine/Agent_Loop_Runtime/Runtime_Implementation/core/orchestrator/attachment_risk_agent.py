"""Attachment Risk governed-agent wrapper - swarm agent #30.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Attachment_Risk_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It wraps
the pure-function, sandbox-safe
``core.precursor.attachment_classifier.score_attachment_risk`` (a Layer 2
Detection signal over static attachment metadata) and exposes it as an
explicitly wired governed agent on the proven ``Agent`` protocol ->
``AgentContribution`` -> Swarm Commander -> ``DecisionEvidenceRecord`` path
already used by Header Analysis, Ghost Thread, Email Authentication, and Link
Inspection.

Scope / governance boundary (contract D1-D9, deliberate):
- D2 detector immutability: this wrapper changes no attachment classification,
  extension vocabulary, scoring band, encrypted-archive pattern, double-
  extension rule, class refinement, overlay behavior, ingest hook, or pipeline
  wiring. The detector function is called read-only.
- D3 facts-only contribution: the contribution carries only the closed
  ``PrecursorIndicator`` attachment-risk indicator names as ``observed_facts``.
  The numeric ``AttachmentRiskAssessment.risk_score``, the ``classification``,
  and every raw filename / hash / MIME / content reference are intentionally
  NOT emitted (Layer 2 emits no interpretation/score field; enforced by the
  ``AgentContribution`` layer-field validator).
- D4 input surface: reads exactly one ``EMAIL_INBOUND`` record via
  ``MissionContext.source_record_id`` and scores its ``attachments`` metadata
  list only. No raw attachment bytes are read by the wrapper.
- D5 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record (template §6.2).
- D6 Stage A / no autonomy: ``challenge`` returns ``None`` (Pass 2 is a
  Verification / Challenge-layer concern); no disposition, no block/quarantine,
  ``autonomous_action_allowed = False``.
- D8 static-only inspection: the wrapper never executes, detonates, extracts,
  fetches, or interprets raw attachment bytes; it calls the existing static
  metadata detector only.
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
from core.precursor.attachment_classifier import score_attachment_risk

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

ATTACHMENT_RISK_AGENT_ID = "attachment_risk_001"
ATTACHMENT_RISK_LAYER = 2  # Detection
ATTACHMENT_RISK_AUTHORITY_LEVEL = 3  # Specialist Agent (matches #6/#8/#10/#21/#27)


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


class AttachmentRiskAgent:
    """Governed Layer 2 Detection agent wrapping the static attachment classifier."""

    agent_id: str = ATTACHMENT_RISK_AGENT_ID
    layer: int = ATTACHMENT_RISK_LAYER
    authority_level: int = ATTACHMENT_RISK_AUTHORITY_LEVEL
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
                "AttachmentRiskAgent requires MissionContext.source_record_id "
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
        # D4/D8: score each attachment's static metadata read-only and
        # aggregate the closed indicator names in source order with dedupe.
        # The detector is the worst-per-attachment scorer; the wrapper carries
        # only the indicator names, never the numeric score or classification.
        observed_facts: list[str] = []
        seen: set[str] = set()
        for meta in email.attachments:
            assessment = score_attachment_risk(meta)
            for indicator in assessment.indicators:
                if indicator in seen:
                    continue
                seen.add(indicator)
                observed_facts.append(indicator)
        # D3 facts-only Detection contribution.
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=tuple(observed_facts),
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
