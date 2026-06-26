"""Executive Impersonation governed-agent wrapper - swarm agent #21.

Evidence Stage 1 (Synthetic) wrapper for Q5 step 3 metadata retrofit.
Wraps ``core.scoring.executive_impersonation_detector.detect_executive_impersonation``
and exposes it on the Agent protocol -> AgentContribution -> DER path.
"""

from __future__ import annotations

import hashlib
from email.utils import parseaddr
from pathlib import Path
from uuid import UUID

from core.blackboard import (
    AgentContributionPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    LookalikeDomainAssessment,
    RecordType,
    read_records,
)
from core.scoring.executive_impersonation_detector import (
    EXECUTIVE_IMPERSONATION_PATTERN_FLAG,
    PrincipalRosterEntry,
    detect_executive_impersonation,
)
from core.scoring.lookalike_domain_detector import detect_lookalike_domains

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

EXECUTIVE_IMPERSONATION_AGENT_ID = "executive_impersonation_001"
EXECUTIVE_IMPERSONATION_LAYER = 2
EXECUTIVE_IMPERSONATION_AUTHORITY_LEVEL = 3


def digest_email(payload: EmailInboundPayload) -> str:
    return hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()


def contribution_payload_from(
    contribution: AgentContribution,
    *,
    case_id: UUID,
    inputs_digest: str,
) -> AgentContributionPayload:
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


class ExecutiveImpersonationAgent:
    agent_id: str = EXECUTIVE_IMPERSONATION_AGENT_ID
    layer: int = EXECUTIVE_IMPERSONATION_LAYER
    authority_level: int = EXECUTIVE_IMPERSONATION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        principal_roster: tuple[PrincipalRosterEntry, ...] = (),
        known_good_domains: tuple[str, ...] = (),
        environment: Environment = Environment.PRODUCTION,
        consume_lookalike_cue: bool = True,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._principal_roster = tuple(principal_roster)
        self._known_good_domains = tuple(known_good_domains)
        self._environment = environment
        self._consume_lookalike_cue = consume_lookalike_cue

    def _load_email(self, context: MissionContext) -> EmailInboundPayload:
        if context.source_record_id is None:
            raise GovernanceError(
                "ExecutiveImpersonationAgent requires MissionContext.source_record_id "
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
        display_name, _ = parseaddr(email.sender)
        lookalike_assessment: LookalikeDomainAssessment | None = None
        if self._consume_lookalike_cue and self._known_good_domains:
            lookalike_assessment = detect_lookalike_domains(
                from_address=email.sender,
                headers=email.headers,
                known_good_domains=self._known_good_domains,
            )
        assessment = detect_executive_impersonation(
            display_name=display_name or email.sender,
            from_address=email.sender,
            headers=email.headers,
            body_plain=email.body_plain,
            principal_roster=self._principal_roster,
            lookalike_assessment=lookalike_assessment,
        )
        observed_facts: tuple[str, ...] = ()
        if assessment.fired:
            observed_facts = (EXECUTIVE_IMPERSONATION_PATTERN_FLAG,)
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=observed_facts,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None

    def persist_contribution(
        self,
        route_context: RouteContext,
        context: MissionContext,
        contribution: AgentContribution,
    ) -> RouteResult:
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
