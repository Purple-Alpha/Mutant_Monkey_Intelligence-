"""Audit Trail governed-agent wrapper — swarm agent #49.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Audit_Trail_Agent_Design_Contract_Deep_Dive.md`` (MMI-DEC-199). It projects
caller-supplied tri-state anchor booleans and optional attested record types
into closed Layer 4 audit-trail attestation facts.

Scope / governance boundary (contract D1-D10, deliberate):
- D2/D7: no Blackboard reads or direct ledger writes; persistence only via
  ``submit_agent_contribution`` -> ``AGENT_CONTRIBUTION``.
- D3: no ``core/evidence_package/`` import or package/audit-packet calls.
- D4: tri-state caller attestation only; no filesystem or ledger discovery.
- D5: attestation semantics only; never §14.3.4 pass or posture-complete facts.
- D7 rollout: Evidence Stage 1 — NOT registered in ``build_default_registry``.
"""

from __future__ import annotations

import hashlib
from typing import Sequence
from uuid import UUID

from core.blackboard import AgentContributionPayload, Environment, GovernanceError
from core.blackboard.models import RecordType

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

AUDIT_TRAIL_AGENT_ID = "audit_trail_001"
AUDIT_TRAIL_LAYER = 4  # Evidence
AUDIT_TRAIL_AUTHORITY_LEVEL = 3  # Specialist Agent

CONTROL_MAPPING = "audit_trail:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic audit-trail attestation only; "
    "not a Cyber §14.3.4 stage pass or insurer approval."
)
MAX_ATTESTED_RECORD_TYPES = 8
MAX_UNDERWRITER_NOTE_CHARS = 160

_ALLOWED_RECORD_TYPES = frozenset(member.name for member in RecordType)

_ANCHOR_SPECS = (
    ("policy_hash_attested_present", "audit_trail_policy_hash_attested_present", "audit_trail_policy_hash_attested_missing"),
    (
        "override_separation_attested_valid",
        "audit_trail_override_separation_attested_present",
        "audit_trail_override_separation_attested_missing",
    ),
    (
        "append_only_chain_attested_present",
        "audit_trail_append_only_chain_attested_present",
        "audit_trail_append_only_chain_attested_missing",
    ),
)

_FORBIDDEN_FACTS = frozenset(
    {
        "audit_trail_posture_complete",
        "audit_trail_policy_hash_present",
        "audit_trail_policy_hash_missing",
        "audit_trail_override_separation_present",
        "audit_trail_override_separation_missing",
        "audit_trail_append_only_chain_present",
        "audit_trail_append_only_chain_missing",
    }
)


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("AuditTrailAgent requires a valid tenant_id")
    return value


def _valid_record_types(attested_record_types: Sequence[str]) -> tuple[str, ...]:
    accepted: list[str] = []
    for name in attested_record_types:
        if name not in _ALLOWED_RECORD_TYPES:
            continue
        accepted.append(name)
    if len(accepted) > MAX_ATTESTED_RECORD_TYPES:
        raise GovernanceError(
            f"attested_record_types exceeds max {MAX_ATTESTED_RECORD_TYPES}"
        )
    return tuple(accepted)


def digest_audit_trail_request(
    *,
    tenant_id: str,
    case_id: UUID,
    policy_hash_attested_present: bool | None = None,
    override_separation_attested_valid: bool | None = None,
    append_only_chain_attested_present: bool | None = None,
    attested_record_types: tuple[str, ...] = (),
    inputs_digest: str | None = None,
) -> str:
    """Deterministic SHA-256 digest of one explicit audit-trail request."""

    _require_tenant_id(tenant_id)
    valid_types = _valid_record_types(attested_record_types)
    raw = "|".join(
        [
            tenant_id,
            str(case_id),
            "" if policy_hash_attested_present is None else str(policy_hash_attested_present),
            "" if override_separation_attested_valid is None else str(override_separation_attested_valid),
            "" if append_only_chain_attested_present is None else str(append_only_chain_attested_present),
            ",".join(valid_types),
            inputs_digest or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def project_audit_trail_facts(
    *,
    policy_hash_attested_present: bool | None = None,
    override_separation_attested_valid: bool | None = None,
    append_only_chain_attested_present: bool | None = None,
    attested_record_types: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Derive closed audit-trail attestation facts from caller-supplied inputs."""

    facts: list[str] = ["audit_trail_synthetic_attestation_only"]
    anchor_values = (
        policy_hash_attested_present,
        override_separation_attested_valid,
        append_only_chain_attested_present,
    )
    valid_types = _valid_record_types(attested_record_types)

    if all(value is None for value in anchor_values) and not valid_types:
        facts.append("audit_trail_missing")
        return tuple(facts)

    all_explicitly_present = True
    for value, (_input_name, present_fact, missing_fact) in zip(
        anchor_values, _ANCHOR_SPECS, strict=True
    ):
        if value is True:
            facts.append(present_fact)
        else:
            facts.append(missing_fact)
            all_explicitly_present = False

    if all(value is True for value in anchor_values):
        facts.append("audit_trail_attestation_all_anchors_present")

    for record_type in valid_types:
        facts.append(f"audit_trail_record_type:{record_type}")

    for fact in facts:
        if fact in _FORBIDDEN_FACTS or fact.startswith("audit_trail_posture"):
            raise GovernanceError(f"forbidden audit-trail fact: {fact}")

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


class AuditTrailAgent:
    """Governed Layer 4 Evidence agent for audit-trail attestation projection."""

    agent_id: str = AUDIT_TRAIL_AGENT_ID
    layer: int = AUDIT_TRAIL_LAYER
    authority_level: int = AUDIT_TRAIL_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        policy_hash_attested_present: bool | None = None,
        override_separation_attested_valid: bool | None = None,
        append_only_chain_attested_present: bool | None = None,
        attested_record_types: tuple[str, ...] = (),
        environment: Environment = Environment.PRODUCTION,
        underwriter_note: str | None = STAGE1_UNDERWRITER_NOTE,
    ) -> None:
        self._policy_hash_attested_present = policy_hash_attested_present
        self._override_separation_attested_valid = override_separation_attested_valid
        self._append_only_chain_attested_present = append_only_chain_attested_present
        self._attested_record_types = _valid_record_types(attested_record_types)
        self._environment = environment
        if underwriter_note is not None and len(underwriter_note) > MAX_UNDERWRITER_NOTE_CHARS:
            raise GovernanceError("underwriter_note exceeds 160-char Stage 1 cap")
        self._underwriter_note = underwriter_note

    def request_digest(self, *, tenant_id: str, case_id: UUID) -> str:
        return digest_audit_trail_request(
            tenant_id=tenant_id,
            case_id=case_id,
            policy_hash_attested_present=self._policy_hash_attested_present,
            override_separation_attested_valid=self._override_separation_attested_valid,
            append_only_chain_attested_present=self._append_only_chain_attested_present,
            attested_record_types=self._attested_record_types,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        _require_tenant_id(context.tenant_id)
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=project_audit_trail_facts(
                policy_hash_attested_present=self._policy_hash_attested_present,
                override_separation_attested_valid=self._override_separation_attested_valid,
                append_only_chain_attested_present=self._append_only_chain_attested_present,
                attested_record_types=self._attested_record_types,
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
    "AUDIT_TRAIL_AGENT_ID",
    "AuditTrailAgent",
    "CONTROL_MAPPING",
    "MAX_ATTESTED_RECORD_TYPES",
    "MAX_UNDERWRITER_NOTE_CHARS",
    "contribution_payload_from",
    "digest_audit_trail_request",
    "project_audit_trail_facts",
]
