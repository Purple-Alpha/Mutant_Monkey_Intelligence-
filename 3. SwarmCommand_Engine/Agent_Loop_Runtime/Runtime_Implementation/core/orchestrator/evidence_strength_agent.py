"""Evidence Strength governed-agent wrapper — swarm agent #50.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Evidence_Strength_Agent_Design_Contract_Deep_Dive.md`` (MMI-DEC-206). It projects
caller-supplied tri-state discipline anchor booleans and optional attested category
statuses into closed Layer 4 evidence-strength attestation facts.

Scope / governance boundary (contract D1-D11, deliberate):
- D2/D9: no eval-harness or pre-ship audit invocation; no metric computation.
- D3: no Blackboard reads or direct ledger writes; persistence only via
  ``submit_agent_contribution`` -> ``AGENT_CONTRIBUTION``.
- D4/D5: tri-state caller attestation only; no framework-pass overclaim facts.
- D7 rollout: Evidence Stage 1 — NOT registered in ``build_default_registry``.
"""

from __future__ import annotations

import hashlib
from typing import Sequence
from uuid import UUID

from core.blackboard import AgentContributionPayload, Environment, GovernanceError

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

EVIDENCE_STRENGTH_AGENT_ID = "evidence_strength_001"
EVIDENCE_STRENGTH_LAYER = 4  # Evidence
EVIDENCE_STRENGTH_AUTHORITY_LEVEL = 3  # Specialist Agent

CONTROL_MAPPING = "evidence_strength:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic evidence-strength attestation only; "
    "not eval-harness pass, accuracy certification, or framework compliance."
)
MAX_ATTESTED_CATEGORY_STATUSES = 8
MAX_UNDERWRITER_NOTE_CHARS = 160

_ALLOWED_CATEGORY_STATUSES = frozenset(
    {
        "supported",
        "not_supported_yet",
        "not_present_in_sample",
        "evidence_missing",
    }
)

_ANCHOR_SPECS = (
    (
        "capability_registry_discipline_attested_present",
        "evidence_strength_capability_registry_attested_present",
        "evidence_strength_capability_registry_attested_missing",
    ),
    (
        "supported_only_denominator_attested_present",
        "evidence_strength_supported_denominator_attested_present",
        "evidence_strength_supported_denominator_attested_missing",
    ),
    (
        "evidence_required_per_score_attested_present",
        "evidence_strength_evidence_bundle_attested_present",
        "evidence_strength_evidence_bundle_attested_missing",
    ),
    (
        "no_chain_of_thought_attested_present",
        "evidence_strength_no_cot_attested_present",
        "evidence_strength_no_cot_attested_missing",
    ),
    (
        "synthetic_fixtures_only_attested_present",
        "evidence_strength_synthetic_fixtures_attested_present",
        "evidence_strength_synthetic_fixtures_attested_missing",
    ),
)

_FORBIDDEN_FACTS = frozenset(
    {
        "evidence_strength_posture_complete",
        "evidence_strength_framework_compliant",
        "evidence_strength_accuracy_certified",
    }
)


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("EvidenceStrengthAgent requires a valid tenant_id")
    return value


def _valid_category_statuses(attested_category_statuses: Sequence[str]) -> tuple[str, ...]:
    accepted: list[str] = []
    for name in attested_category_statuses:
        if name not in _ALLOWED_CATEGORY_STATUSES:
            continue
        accepted.append(name)
    if len(accepted) > MAX_ATTESTED_CATEGORY_STATUSES:
        raise GovernanceError(
            f"attested_category_statuses exceeds max {MAX_ATTESTED_CATEGORY_STATUSES}"
        )
    return tuple(accepted)


def digest_evidence_strength_request(
    *,
    tenant_id: str,
    case_id: UUID,
    capability_registry_discipline_attested_present: bool | None = None,
    supported_only_denominator_attested_present: bool | None = None,
    evidence_required_per_score_attested_present: bool | None = None,
    no_chain_of_thought_attested_present: bool | None = None,
    synthetic_fixtures_only_attested_present: bool | None = None,
    attested_category_statuses: tuple[str, ...] = (),
    eval_run_id: str | None = None,
    inputs_digest: str | None = None,
) -> str:
    """Deterministic SHA-256 digest of one explicit evidence-strength request."""

    _require_tenant_id(tenant_id)
    valid_statuses = _valid_category_statuses(attested_category_statuses)
    raw = "|".join(
        [
            tenant_id,
            str(case_id),
            eval_run_id or "",
            "" if capability_registry_discipline_attested_present is None else str(capability_registry_discipline_attested_present),
            "" if supported_only_denominator_attested_present is None else str(supported_only_denominator_attested_present),
            "" if evidence_required_per_score_attested_present is None else str(evidence_required_per_score_attested_present),
            "" if no_chain_of_thought_attested_present is None else str(no_chain_of_thought_attested_present),
            "" if synthetic_fixtures_only_attested_present is None else str(synthetic_fixtures_only_attested_present),
            ",".join(valid_statuses),
            inputs_digest or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def project_evidence_strength_facts(
    *,
    capability_registry_discipline_attested_present: bool | None = None,
    supported_only_denominator_attested_present: bool | None = None,
    evidence_required_per_score_attested_present: bool | None = None,
    no_chain_of_thought_attested_present: bool | None = None,
    synthetic_fixtures_only_attested_present: bool | None = None,
    attested_category_statuses: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Derive closed evidence-strength attestation facts from caller inputs."""

    facts: list[str] = ["evidence_strength_synthetic_attestation_only"]
    anchor_values = (
        capability_registry_discipline_attested_present,
        supported_only_denominator_attested_present,
        evidence_required_per_score_attested_present,
        no_chain_of_thought_attested_present,
        synthetic_fixtures_only_attested_present,
    )
    valid_statuses = _valid_category_statuses(attested_category_statuses)

    if all(value is None for value in anchor_values) and not valid_statuses:
        facts.append("evidence_strength_missing")
        return tuple(facts)

    for value, (_input_name, present_fact, missing_fact) in zip(
        anchor_values, _ANCHOR_SPECS, strict=True
    ):
        if value is True:
            facts.append(present_fact)
        else:
            facts.append(missing_fact)

    if all(value is True for value in anchor_values):
        facts.append("evidence_strength_attestation_all_anchors_present")

    for status in valid_statuses:
        facts.append(f"evidence_strength_category_status:{status}")

    for fact in facts:
        if fact in _FORBIDDEN_FACTS or fact.startswith("evidence_strength_posture"):
            raise GovernanceError(f"forbidden evidence-strength fact: {fact}")

    return tuple(facts)


def contribution_payload_from(
    contribution: AgentContribution,
    *,
    case_id: UUID,
    inputs_digest: str,
) -> AgentContributionPayload:
    """Map an already-validated ``AgentContribution`` to its persistence payload."""

    note = contribution.underwriter_note
    if note is not None and len(note) > MAX_UNDERWRITER_NOTE_CHARS:
        raise GovernanceError("underwriter_note exceeds 160-char Stage 1 cap")

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


class EvidenceStrengthAgent:
    """Governed Layer 4 Evidence agent for evidence-strength attestation projection."""

    agent_id: str = EVIDENCE_STRENGTH_AGENT_ID
    layer: int = EVIDENCE_STRENGTH_LAYER
    authority_level: int = EVIDENCE_STRENGTH_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        capability_registry_discipline_attested_present: bool | None = None,
        supported_only_denominator_attested_present: bool | None = None,
        evidence_required_per_score_attested_present: bool | None = None,
        no_chain_of_thought_attested_present: bool | None = None,
        synthetic_fixtures_only_attested_present: bool | None = None,
        attested_category_statuses: tuple[str, ...] = (),
        environment: Environment = Environment.PRODUCTION,
        underwriter_note: str | None = STAGE1_UNDERWRITER_NOTE,
    ) -> None:
        self._capability_registry_discipline_attested_present = (
            capability_registry_discipline_attested_present
        )
        self._supported_only_denominator_attested_present = (
            supported_only_denominator_attested_present
        )
        self._evidence_required_per_score_attested_present = (
            evidence_required_per_score_attested_present
        )
        self._no_chain_of_thought_attested_present = no_chain_of_thought_attested_present
        self._synthetic_fixtures_only_attested_present = (
            synthetic_fixtures_only_attested_present
        )
        self._attested_category_statuses = _valid_category_statuses(attested_category_statuses)
        self._environment = environment
        if underwriter_note is not None and len(underwriter_note) > MAX_UNDERWRITER_NOTE_CHARS:
            raise GovernanceError("underwriter_note exceeds 160-char Stage 1 cap")
        self._underwriter_note = underwriter_note

    def request_digest(self, *, tenant_id: str, case_id: UUID) -> str:
        return digest_evidence_strength_request(
            tenant_id=tenant_id,
            case_id=case_id,
            capability_registry_discipline_attested_present=self._capability_registry_discipline_attested_present,
            supported_only_denominator_attested_present=self._supported_only_denominator_attested_present,
            evidence_required_per_score_attested_present=self._evidence_required_per_score_attested_present,
            no_chain_of_thought_attested_present=self._no_chain_of_thought_attested_present,
            synthetic_fixtures_only_attested_present=self._synthetic_fixtures_only_attested_present,
            attested_category_statuses=self._attested_category_statuses,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        _require_tenant_id(context.tenant_id)
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=project_evidence_strength_facts(
                capability_registry_discipline_attested_present=self._capability_registry_discipline_attested_present,
                supported_only_denominator_attested_present=self._supported_only_denominator_attested_present,
                evidence_required_per_score_attested_present=self._evidence_required_per_score_attested_present,
                no_chain_of_thought_attested_present=self._no_chain_of_thought_attested_present,
                synthetic_fixtures_only_attested_present=self._synthetic_fixtures_only_attested_present,
                attested_category_statuses=self._attested_category_statuses,
            ),
            control_mapping=CONTROL_MAPPING,
            underwriter_note=self._underwriter_note,
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
    "EVIDENCE_STRENGTH_AGENT_ID",
    "EvidenceStrengthAgent",
    "CONTROL_MAPPING",
    "MAX_ATTESTED_CATEGORY_STATUSES",
    "MAX_UNDERWRITER_NOTE_CHARS",
    "contribution_payload_from",
    "digest_evidence_strength_request",
    "project_evidence_strength_facts",
]
