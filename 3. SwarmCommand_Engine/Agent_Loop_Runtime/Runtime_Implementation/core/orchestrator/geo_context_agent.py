"""Geo-Context governed-agent wrapper — swarm agent #43 (Lane 1).

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Geo_Context_Agent_Design_Contract_Deep_Dive.md`` (MMI-DEC-252).

Emits tenant-declared legitimate geo-context facts and closed
``declared_vs_observed_mismatch`` observations. Does **not** emit
``geo_signal``, re-assemble #76 ``GeoBriefing``, or import Lane 4 deception.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import ConfigDict, Field

from core.blackboard import Environment, GovernanceError
from core.blackboard.models import StrictModel
from core.knowledge.geo_intel_agent import GeoBriefing

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, submit_agent_contribution

GEO_CONTEXT_AGENT_ID = "geo_context_001"
GEO_CONTEXT_LAYER = 2
GEO_CONTEXT_AUTHORITY_LEVEL = 3

DECLARED_SERVICE_AREA = "declared_service_area"
DECLARED_JURISDICTION_FRAME = "declared_jurisdiction_frame"
EXPECTED_LOCALE = "expected_locale"
POLICY_PACK_REF = "policy_pack_ref"
DECLARED_VS_OBSERVED_MISMATCH = "declared_vs_observed_mismatch"

CLOSED_GEO_CONTEXT_FACTS = frozenset(
    {
        DECLARED_SERVICE_AREA,
        DECLARED_JURISDICTION_FRAME,
        EXPECTED_LOCALE,
        POLICY_PACK_REF,
        DECLARED_VS_OBSERVED_MISMATCH,
    }
)



class TenantGeoContextRosterV1(StrictModel):
    """Frozen caller-owned roster (contract §3)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: str = Field(min_length=1)
    declared_service_areas: tuple[str, ...] = ()
    declared_jurisdiction_frames: tuple[str, ...] = ()
    expected_locales: tuple[str, ...] = ()
    compliance_policy_pack_refs: tuple[str, ...] = ()


def digest_roster(roster: TenantGeoContextRosterV1) -> str:
    payload = roster.model_dump(mode="json")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _normalized_tokens(tokens: tuple[str, ...]) -> set[str]:
    return {token.strip().upper() for token in tokens if token.strip()}


class GeoContextAgent:
    agent_id: str = GEO_CONTEXT_AGENT_ID
    layer: int = GEO_CONTEXT_LAYER
    authority_level: int = GEO_CONTEXT_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        roster: TenantGeoContextRosterV1,
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._roster = roster
        self._environment = environment

    def _validate_tenant(self, context: MissionContext) -> None:
        if context.tenant_id != self._roster.tenant_id:
            raise GovernanceError(
                f"GeoContextAgent roster tenant {self._roster.tenant_id!r} "
                f"does not match MissionContext tenant {context.tenant_id!r}"
            )

    def analyze(
        self,
        context: MissionContext,
        *,
        geo_briefing: GeoBriefing | None = None,
        observed_country_class: str | None = None,
    ) -> AgentContribution:
        """Emit Lane 1 closed facts from roster and optional comparison surface."""

        self._validate_tenant(context)
        _ = geo_briefing  # optional read-only context for future ES2 wiring
        facts: list[str] = []
        roster = self._roster

        if roster.declared_service_areas:
            facts.append(DECLARED_SERVICE_AREA)
        if roster.declared_jurisdiction_frames:
            facts.append(DECLARED_JURISDICTION_FRAME)
        if roster.expected_locales:
            facts.append(EXPECTED_LOCALE)
        if roster.compliance_policy_pack_refs:
            facts.append(POLICY_PACK_REF)

        observed = (observed_country_class or "").strip().upper()
        declared_areas = _normalized_tokens(roster.declared_service_areas)
        if observed and declared_areas and observed not in declared_areas:
            facts.append(DECLARED_VS_OBSERVED_MISMATCH)

        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=tuple(facts),
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
        from core.blackboard.models import AgentContributionPayload

        payload = AgentContributionPayload(
            case_id=context.case_id,
            inputs_digest=context.inputs_digest,
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
        return submit_agent_contribution(
            route_context,
            tenant_id=context.tenant_id,
            environment=self._environment,
            source_agent=self.agent_id,
            payload=payload,
            parent_record_id=context.source_record_id,
        )
