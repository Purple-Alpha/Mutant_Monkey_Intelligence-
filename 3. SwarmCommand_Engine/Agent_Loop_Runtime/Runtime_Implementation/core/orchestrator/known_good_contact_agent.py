"""Known-Good Contact governed-agent wrapper - swarm agent #11.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Known_Good_Contact_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It
wraps the existing Vendor Baseline Store ``check_signal`` primitive as a
read-only Layer 3 Verification agent.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 read-only verification: the wrapper calls ``check_signal`` only. It never
  calls ``ingest_signal``, ``expire_stale_signals``, private store helpers, or
  any write path.
- D3 source restriction: the candidate signal is supplied by an explicit caller.
  The wrapper does not extract raw email, does not learn from the suspicious
  event, and does not create a contact registry.
- D5 facts-only verification contribution: the contribution carries only closed
  known-good facts plus the Layer 3 ``verification_source`` and
  ``verification_outcome`` fields. Raw values, signal hashes, contact details,
  timestamps, explanations, risk floors, and recommended actions are not emitted.
- D7 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record.
- D8/D9 Stage A / no autonomy: ``challenge`` returns ``None``; no contact
  workflow, no network, no disposition, no block/quarantine/payment decision,
  ``autonomous_action_allowed = False``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Callable
from uuid import UUID

from core.blackboard import AgentContributionPayload, Environment, GovernanceError
from core.production_state import vendor_baseline
from core.production_state.vendor_baseline import SignalLookupResult, SignalType

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

KNOWN_GOOD_CONTACT_AGENT_ID = "known_good_contact_001"
KNOWN_GOOD_CONTACT_LAYER = 3  # Verification
KNOWN_GOOD_CONTACT_AUTHORITY_LEVEL = 3  # Specialist Agent

_FACT_BY_STATE = {
    "known": "known_good_contact_signal_known",
    "new": "known_good_contact_signal_new",
    "expired": "known_good_contact_signal_expired",
}
_OUTCOME_BY_STATE = {
    "known": "confirmed",
    "new": "unable_to_verify",
    "expired": "unable_to_verify",
}

SignalChecker = Callable[..., SignalLookupResult]


def digest_request(
    *,
    vendor_domain: str,
    signal_type: str,
    raw_value: str,
) -> str:
    """Deterministic SHA-256 digest of one explicit verification request."""

    raw = "|".join([vendor_domain, signal_type, raw_value])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require_raw_value(value: str) -> str:
    if not isinstance(value, str):
        raise GovernanceError("raw_value must be a string")
    if not value.strip():
        raise GovernanceError("raw_value cannot be empty")
    return value


def _verification_source(signal_type: str) -> str:
    return f"vendor_baseline:{signal_type}"


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


class KnownGoodContactAgent:
    """Governed Layer 3 Verification agent for known vendor-baseline signals."""

    agent_id: str = KNOWN_GOOD_CONTACT_AGENT_ID
    layer: int = KNOWN_GOOD_CONTACT_LAYER
    authority_level: int = KNOWN_GOOD_CONTACT_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        vendor_domain: str,
        signal_type: SignalType,
        raw_value: str,
        now: datetime,
        environment: Environment = Environment.PRODUCTION,
        checker: SignalChecker = vendor_baseline.check_signal,
    ) -> None:
        self._vendor_domain = vendor_domain
        self._signal_type = signal_type
        self._raw_value = _require_raw_value(raw_value)
        self._now = now
        self._environment = environment
        # Injected so tests can prove this wrapper calls check_signal and no
        # write/learning path.
        self._checker = checker

    def request_digest(self) -> str:
        return digest_request(
            vendor_domain=self._vendor_domain,
            signal_type=self._signal_type,
            raw_value=self._raw_value,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        lookup = self._checker(
            tenant_id=context.tenant_id,
            vendor_domain=self._vendor_domain,
            signal_type=self._signal_type,
            raw_value=self._raw_value,
            now=self._now,
        )
        fact = _FACT_BY_STATE[lookup.state]
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=(fact, f"known_good_contact_signal_type:{self._signal_type}"),
            verification_source=_verification_source(self._signal_type),
            verification_outcome=_OUTCOME_BY_STATE[lookup.state],
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
