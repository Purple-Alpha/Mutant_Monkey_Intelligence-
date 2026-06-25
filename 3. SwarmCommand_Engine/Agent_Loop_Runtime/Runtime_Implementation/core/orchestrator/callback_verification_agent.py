"""Callback Verification governed-agent wrapper - swarm agent #18.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Callback_Verification_Agent_Design_Contract_Deep_Dive.md`` (2026-06-25).
It wraps the existing two-channel-confirmation ``summarize_confirmation_status``
primitive as a read-only Layer 3 Verification agent scoped to callback-phishing
out-of-band verification posture.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 TOAD immutability: the wrapper never imports or calls
  ``detect_callback_phishing`` or reads inbound email bodies.
- D3 workflow read-only: the wrapper calls ``summarize_confirmation_status``
  only. It never calls workflow write paths.
- D4 caller-supplied finding: ``finding_id`` and ``verification_class`` come
  from explicit governed caller context.
- D5/D6 callback-scoped facts: closed ``callback_oob_verification_*`` facts
  plus Layer 3 ``verification_source`` / ``verification_outcome`` only.
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

CALLBACK_VERIFICATION_AGENT_ID = "callback_verification_001"
CALLBACK_VERIFICATION_LAYER = 3  # Verification
CALLBACK_VERIFICATION_AUTHORITY_LEVEL = 3  # Specialist Agent
CALLBACK_PHISHING_OOB_CLASS = "callback_phishing_oob"

_FINDING_ID_RE = re.compile(r"^[A-Za-z0-9_\-:.]+$")
_MAX_FINDING_ID_LENGTH = 128

_FACT_BY_STATUS = {
    None: "callback_oob_verification_pending",
    "confirmed": "callback_oob_verification_confirmed",
    "rejected": "callback_oob_verification_rejected",
    "unable_to_verify": "callback_oob_verification_unable_to_verify",
    "expired": "callback_oob_verification_expired",
}
_OUTCOME_BY_STATUS = {
    None: "unable_to_verify",
    "confirmed": "confirmed",
    "rejected": "contradicted",
    "unable_to_verify": "unable_to_verify",
    "expired": "unable_to_verify",
}

SummaryReader = Callable[..., ConfirmationRecord | None]


def digest_request(
    *, tenant_id: str, finding_id: str, verification_class: str = CALLBACK_PHISHING_OOB_CLASS
) -> str:
    """Deterministic SHA-256 digest of one explicit callback verification request."""

    _require_tenant_id(tenant_id)
    _require_finding_id(finding_id)
    _require_verification_class(verification_class)
    raw = "|".join([tenant_id, finding_id, verification_class])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("CallbackVerificationAgent requires a valid tenant_id")
    return value


def _require_finding_id(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise GovernanceError("CallbackVerificationAgent requires a non-empty finding_id")
    if len(value) > _MAX_FINDING_ID_LENGTH:
        raise GovernanceError(
            f"CallbackVerificationAgent finding_id must be <= {_MAX_FINDING_ID_LENGTH} characters"
        )
    if not _FINDING_ID_RE.match(value):
        raise GovernanceError(
            "CallbackVerificationAgent finding_id may only contain [A-Za-z0-9_-:.] characters"
        )
    if value in {".", ".."} or value.startswith(".") or value.endswith("."):
        raise GovernanceError(
            "CallbackVerificationAgent finding_id must not be a relative path token"
        )
    return value


def _require_verification_class(value: str) -> str:
    if value != CALLBACK_PHISHING_OOB_CLASS:
        raise GovernanceError(
            "CallbackVerificationAgent requires "
            f"verification_class={CALLBACK_PHISHING_OOB_CLASS!r}"
        )
    return value


def _verification_source(finding_id: str, verification_class: str) -> str:
    return f"{verification_class}:{finding_id}"


def _facts_for(record: ConfirmationRecord | None) -> tuple[str, ...]:
    if record is None:
        return ("callback_oob_verification_missing",)

    facts = [_FACT_BY_STATUS[record.outcome_status]]
    if record.detector:
        facts.append(f"callback_verification_detector:{record.detector}")
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


class CallbackVerificationAgent:
    """Governed Layer 3 Verification agent for callback-phishing OOB posture."""

    agent_id: str = CALLBACK_VERIFICATION_AGENT_ID
    layer: int = CALLBACK_VERIFICATION_LAYER
    authority_level: int = CALLBACK_VERIFICATION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        finding_id: str,
        blackboard_root: Path,
        verification_class: str = CALLBACK_PHISHING_OOB_CLASS,
        environment: Environment = Environment.PRODUCTION,
        summarizer: SummaryReader = tcc.summarize_confirmation_status,
    ) -> None:
        self._finding_id = _require_finding_id(finding_id)
        self._verification_class = _require_verification_class(verification_class)
        self._blackboard_root = blackboard_root
        self._environment = environment
        self._summarizer = summarizer

    def request_digest(self, *, tenant_id: str) -> str:
        return digest_request(
            tenant_id=tenant_id,
            finding_id=self._finding_id,
            verification_class=self._verification_class,
        )

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
            verification_source=_verification_source(
                self._finding_id, self._verification_class
            ),
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
    "CALLBACK_PHISHING_OOB_CLASS",
    "CALLBACK_VERIFICATION_AGENT_ID",
    "CallbackVerificationAgent",
    "contribution_payload_from",
    "digest_request",
]
