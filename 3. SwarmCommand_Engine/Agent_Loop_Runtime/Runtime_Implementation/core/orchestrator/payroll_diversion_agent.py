"""Payroll Diversion governed-agent wrapper — swarm agent #22."""

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
from core.control_plane.enact_gate import enact_block, enact_contain
from core.scoring.payroll_diversion_detector import detect_payroll_diversion

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

PAYROLL_DIVERSION_AGENT_ID = "payroll_diversion_001"
PAYROLL_DIVERSION_LAYER = 2
PAYROLL_DIVERSION_AUTHORITY_LEVEL = 3


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


class PayrollDiversionAgent:
    agent_id: str = PAYROLL_DIVERSION_AGENT_ID
    layer: int = PAYROLL_DIVERSION_LAYER
    authority_level: int = PAYROLL_DIVERSION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        payroll_mailbox_roster: tuple[str, ...] = (),
        employee_token_roster: tuple[str, ...] = (),
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._payroll_mailbox_roster = tuple(
            mailbox.strip() for mailbox in payroll_mailbox_roster
        )
        self._employee_token_roster = tuple(
            token.strip() for token in employee_token_roster
        )
        self._environment = environment

    def _load_email(self, context: MissionContext) -> EmailInboundPayload:
        if context.source_record_id is None:
            raise GovernanceError(
                "PayrollDiversionAgent requires MissionContext.source_record_id"
            )
        path = blackboard_path(
            self._blackboard_root, self._environment, context.tenant_id
        )
        for record in read_records(path):
            if record.record_id == context.source_record_id:
                if record.record_type != RecordType.EMAIL_INBOUND:
                    raise GovernanceError("source record is not email_inbound")
                return EmailInboundPayload.model_validate(record.payload)
        raise GovernanceError("email_inbound record not found")

    def analyze(self, context: MissionContext) -> AgentContribution:
        email = self._load_email(context)
        attachment_texts = tuple(
            attachment.extracted_text or ""
            for attachment in email.attachments
            if attachment.extracted_text
        )
        assessment = detect_payroll_diversion(
            body_plain=email.body_plain,
            subject=email.subject,
            attachment_extracted_texts=attachment_texts,
            recipient=email.recipient,
            payroll_mailbox_roster=self._payroll_mailbox_roster,
            employee_token_roster=self._employee_token_roster,
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=assessment.observation_facts(),
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None

    def enact_block(self, *_args, **_kwargs) -> None:
        enact_block()

    def enact_contain(self, *_args, **_kwargs) -> None:
        enact_contain()

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


__all__ = [
    "PAYROLL_DIVERSION_AGENT_ID",
    "PayrollDiversionAgent",
    "contribution_payload_from",
    "digest_email",
]
