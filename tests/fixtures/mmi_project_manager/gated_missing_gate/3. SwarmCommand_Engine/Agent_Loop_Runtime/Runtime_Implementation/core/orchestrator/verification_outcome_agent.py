"""Verification Outcome governed-agent wrapper - swarm agent #48.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Verification_Outcome_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It
wraps the existing two-channel-confirmation ``summarize_confirmation_status``
primitive as a read-only Layer 3 Verification agent.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 read-only workflow boundary: the wrapper calls
  ``summarize_confirmation_status`` only. It never calls
  ``record_confirmation_request``, ``record_confirmation_outcome``,
  ``submit_two_channel_confirmation``, private workflow helpers, or any write
  path.
- D3 source restriction: the ``finding_id`` is supplied by an explicit caller.
  The wrapper does not discover findings, create pending tasks, or infer
  outcomes from raw email or payment data.
- D5 facts-only verification contribution: the contribution carries only closed
  two-channel facts plus the Layer 3 ``verification_source`` and
  ``verification_outcome`` fields. Operator labels, channel descriptions,
  reasons, timestamps, risk floors, payment values, and recommended actions are
  not emitted.
- D7 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record.
- D8/D9 Stage A / no autonomy: ``challenge`` returns ``None``; no contact
  workflow, no network, no disposition, no payment decision,
  ``autonomous_action_allowed = False``.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Callable
from uuid import UUID

from core.blackboard import AgentContributionPayload, Environment, GovernanceError
from core.workflows import two_channel_confirmation as tcc
from core.workflows.two_channel_confirmation import ConfirmationRecord

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

VERIFICATION_OUTCOME_AGENT_ID = "verification_outcome_001"
VERIFICATION_OUTCOME_LAYER = 3  # Verification
VERIFICATION_OUTCOME_AUTHORITY_LEVEL = 3  # Specialist Agent

_FINDING_ID_RE = re.compile(r"^[A-Za-z0-9_\-:.]+$")
_MAX_FINDING_ID_LENGTH = 128

_FACT_BY_STATUS = {
    None: "two_channel_confirmation_pending",
    "confirmed": "two_channel_confirmation_confirmed",
    "rejected": "two_channel_confirmation_rejected",
    "unable_to_verify": "two_channel_confirmation_unable_to_verify",
    "expired": "two_channel_confirmation_expired",
}
_OUTCOME_BY_STATUS = {
    None: "unable_to_verify",
    "confirmed": "confirmed",
    "rejected": "contradicted",
    "unable_to_verify": "unable_to_verify",
    "expired": "unable_to_verify",
}

SummaryReader = Callable[..., ConfirmationRecord | None]


def digest_request(*, tenant_id: str, finding_id: str) -> str:
    """Deterministic SHA-256 digest of one explicit verification request."""

    _require_tenant_id(tenant_id)
    _require_finding_id(finding_id)
    raw = "|".join([tenant_id, finding_id])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("VerificationOutcomeAgent requires a valid tenant_id")
    return value


def _require_finding_id(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise GovernanceError("VerificationOutcomeAgent requires a non-empty finding_id")
    if len(value) > _MAX_FINDING_ID_LENGTH:
        raise GovernanceError(
            f"VerificationOutcomeAgent finding_id must be <= {_MAX_FINDING_ID_LENGTH} characters"
        )
    if not _FINDING_ID_RE.match(value):
        raise GovernanceError(
            "VerificationOutcomeAgent finding_id may only contain [A-Za-z0-9_-:.] characters"
        )
    if value in {".", ".."} or value.startswith(".") or value.endswith("."):
        raise GovernanceError(
            "VerificationOutcomeAgent finding_id must not be a relative path token"
        )
    return value


def _verification_source(finding_id: str) -> str:
    return f"two_channel_confirmation:{finding_id}"


def _facts_for(record: ConfirmationRecord | None) -> tuple[str, ...]:
    if record is None:
        return ("two_channel_confirmation_missing",)

    facts = [_FACT_BY_STATUS[record.outcome_status]]
    if record.detector:
        facts.append(f"two_channel_detector:{record.detector}")
    if record.channel_kind:
        facts.append(f"two_channel_channel_kind:{record.channel_kind}")
    return tuple(facts)


def _outcome_for(record: ConfirmationRecord | None) -> str:
    if record is None:
        return "unable_to_verify"
    return _OUTCOME_BY_STATUS[record.outcome_status]


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


class VerificationOutcomeAgent:
    """Governed Layer 3 Verification agent for two-channel workflow outcomes."""

    agent_id: str = VERIFICATION_OUTCOME_AGENT_ID
    layer: int = VERIFICATION_OUTCOME_LAYER
    authority_level: int = VERIFICATION_OUTCOME_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        finding_id: str,
        blackboard_root: Path,
        environment: Environment = Environment.PRODUCTION,
        summarizer: SummaryReader = tcc.summarize_confirmation_status,
    ) -> None:
        self._finding_id = _require_finding_id(finding_id)
        self._blackboard_root = blackboard_root
        self._environment = environment
        # Injected so tests can prove this wrapper calls the summary read once
        # and no workflow write/contact path.
        self._summarizer = summarizer

    def request_digest(self, *, tenant_id: str) -> str:
        return digest_request(tenant_id=tenant_id, finding_id=self._finding_id)

    def analyze(self, context: MissionContext) -> AgentContribution:
        tenant_id = _require_tenant_id(context.tenant_id)
        record = self._summarizer(
            tenant_id=tenant_id,
            finding_id=self._finding_id,
            blackboard_root=self._blackboard_root,
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=_facts_for(record),
            verification_source=_verification_source(self._finding_id),
            verification_outcome=_outcome_for(record),
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


__all__ = [
    "VERIFICATION_OUTCOME_AGENT_ID",
    "VerificationOutcomeAgent",
    "contribution_payload_from",
    "digest_request",
]
