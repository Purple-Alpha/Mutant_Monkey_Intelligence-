"""Case Timeline governed-agent wrapper - swarm agent #47.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Case_Timeline_Agent_Design_Contract_Deep_Dive.md`` (2026-06-20). It projects
caller-supplied ``DecisionTimestamps`` and optional caller-attested governed
#48 verification fact names into closed Layer 4 timeline facts.

Scope / governance boundary (contract D1-D12, deliberate):
- D2 read-only boundary: reads only caller-supplied timing anchors and attested
  verification fact names; no Blackboard workflow reads, no ledger append, no
  package mutation.
- D3 source restriction: no #48 invocation, no workflow writes, no external
  discovery.
- D5 facts-only Layer 4 contribution: presence/sequence/phase facts only; no
  timestamps, durations, record IDs, or client-facing timing language.
- D6 #48 composition: verification phase present only when both
  ``verification_outcome_at`` and valid attested governed #48 facts exist.
- D7 sequence rule: non-null anchors must be monotonic in canonical order.
- D7a closure: ``case_timeline_closure_missing`` only when ``expect_closure``
  is true and ``closed_at`` is absent.
- D11 Mode A: attested #48 fact names only; out-of-vocabulary names omitted.
- D12 Mode A: duration buckets forbidden (not computed or emitted).
- D7 rollout: Evidence Stage 1 - NOT registered in ``build_default_registry``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Sequence
from uuid import UUID

from core.blackboard import AgentContributionPayload, Environment, GovernanceError

from .agent_contract import (
    AgentContribution,
    ChallengeResult,
    DecisionTimestamps,
    MissionContext,
)
from .routes import RouteContext, RouteResult, submit_agent_contribution

CASE_TIMELINE_AGENT_ID = "case_timeline_001"
CASE_TIMELINE_LAYER = 4  # Evidence
CASE_TIMELINE_AUTHORITY_LEVEL = 3  # Specialist Agent

CONTROL_MAPPING = "case_timeline:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic case-timeline evidence only; "
    "not a client-facing timing or SLA claim."
)

# Closed #48 governed fact vocabulary (Verification Outcome contract Evidence emitted).
_GOVERNED_VERIFICATION_FACTS = frozenset(
    {
        "two_channel_confirmation_missing",
        "two_channel_confirmation_pending",
        "two_channel_confirmation_confirmed",
        "two_channel_confirmation_rejected",
        "two_channel_confirmation_unable_to_verify",
        "two_channel_confirmation_expired",
    }
)
_GOVERNED_VERIFICATION_PREFIXES = (
    "two_channel_detector:",
    "two_channel_channel_kind:",
)

_ANCHOR_ORDER = (
    "detected_at",
    "verification_requested_at",
    "verification_outcome_at",
    "closed_at",
)


def digest_timeline_request(
    *,
    tenant_id: str,
    case_id: UUID,
    timestamps: DecisionTimestamps,
    expect_closure: bool = False,
    attested_verification_facts: tuple[str, ...] = (),
    inputs_digest: str | None = None,
) -> str:
    """Deterministic SHA-256 digest of one explicit timeline request."""

    _require_tenant_id(tenant_id)
    _require_timestamps(timestamps)
    attested = _valid_attested_facts(attested_verification_facts)
    raw = "|".join(
        [
            tenant_id,
            str(case_id),
            timestamps.detected_at.isoformat(),
            timestamps.verification_requested_at.isoformat()
            if timestamps.verification_requested_at
            else "",
            timestamps.verification_outcome_at.isoformat()
            if timestamps.verification_outcome_at
            else "",
            timestamps.closed_at.isoformat() if timestamps.closed_at else "",
            str(expect_closure),
            ",".join(attested),
            inputs_digest or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("CaseTimelineAgent requires a valid tenant_id")
    return value


def _require_timestamps(timestamps: DecisionTimestamps) -> DecisionTimestamps:
    if timestamps.detected_at is None:
        raise GovernanceError("CaseTimelineAgent requires detected_at")
    return timestamps


def _is_governed_verification_fact(name: str) -> bool:
    if name in _GOVERNED_VERIFICATION_FACTS:
        return True
    return any(name.startswith(prefix) for prefix in _GOVERNED_VERIFICATION_PREFIXES)


def _valid_attested_facts(
    attested_verification_facts: Sequence[str],
) -> tuple[str, ...]:
    return tuple(
        name
        for name in attested_verification_facts
        if _is_governed_verification_fact(name)
    )


def _anchor_values(timestamps: DecisionTimestamps) -> list[tuple[str, datetime]]:
    values: list[tuple[str, datetime]] = []
    for key in _ANCHOR_ORDER:
        value = getattr(timestamps, key)
        if value is not None:
            values.append((key, value))
    return values


def project_timeline_facts(
    timestamps: DecisionTimestamps,
    *,
    expect_closure: bool = False,
    attested_verification_facts: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Derive closed timeline facts from caller-supplied anchors and attestation."""

    _require_timestamps(timestamps)
    facts: list[str] = ["case_timeline_detected_at_present"]

    if timestamps.verification_requested_at is not None:
        facts.append("case_timeline_verification_requested_at_present")
    if timestamps.verification_outcome_at is not None:
        facts.append("case_timeline_verification_outcome_at_present")
    if timestamps.closed_at is not None:
        facts.append("case_timeline_closed_at_present")

    anchors = _anchor_values(timestamps)
    if len(anchors) >= 2:
        monotonic = all(
            anchors[index][1] <= anchors[index + 1][1]
            for index in range(len(anchors) - 1)
        )
        facts.append(
            "case_timeline_sequence_monotonic"
            if monotonic
            else "case_timeline_sequence_invalid"
        )

    valid_attested = _valid_attested_facts(attested_verification_facts)
    if timestamps.verification_outcome_at is not None:
        if valid_attested:
            facts.append("case_timeline_verification_phase_present")
            for name in valid_attested:
                facts.append(f"case_timeline_verification_fact:{name}")
        else:
            facts.append("case_timeline_verification_phase_missing")

    if expect_closure and timestamps.closed_at is None:
        facts.append("case_timeline_closure_missing")

    return tuple(facts)


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


class CaseTimelineAgent:
    """Governed Layer 4 Evidence agent for case timeline projection."""

    agent_id: str = CASE_TIMELINE_AGENT_ID
    layer: int = CASE_TIMELINE_LAYER
    authority_level: int = CASE_TIMELINE_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        timestamps: DecisionTimestamps,
        expect_closure: bool = False,
        attested_verification_facts: tuple[str, ...] = (),
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._timestamps = _require_timestamps(timestamps)
        self._expect_closure = expect_closure
        self._attested_verification_facts = tuple(attested_verification_facts)
        self._environment = environment

    def request_digest(self, *, tenant_id: str, case_id: UUID) -> str:
        return digest_timeline_request(
            tenant_id=tenant_id,
            case_id=case_id,
            timestamps=self._timestamps,
            expect_closure=self._expect_closure,
            attested_verification_facts=self._attested_verification_facts,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        _require_tenant_id(context.tenant_id)
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=project_timeline_facts(
                self._timestamps,
                expect_closure=self._expect_closure,
                attested_verification_facts=self._attested_verification_facts,
            ),
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
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


__all__ = [
    "CASE_TIMELINE_AGENT_ID",
    "CaseTimelineAgent",
    "contribution_payload_from",
    "digest_timeline_request",
    "project_timeline_facts",
]
