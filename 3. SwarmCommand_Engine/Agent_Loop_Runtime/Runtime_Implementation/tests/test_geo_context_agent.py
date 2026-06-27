"""Evidence Stage 1 proof for swarm agent #43 Geo-Context (Lane 1)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import GovernanceError
from core.knowledge.geo_intel_agent import GeoBriefing, GeoIntelAgent
from core.orchestrator.agent_contract import AgentContribution, MissionContext
from core.orchestrator.geo_context_agent import (
    CLOSED_GEO_CONTEXT_FACTS,
    DECLARED_JURISDICTION_FRAME,
    DECLARED_SERVICE_AREA,
    DECLARED_VS_OBSERVED_MISMATCH,
    EXPECTED_LOCALE,
    GEO_CONTEXT_AGENT_ID,
    POLICY_PACK_REF,
    GeoContextAgent,
    TenantGeoContextRosterV1,
    digest_roster,
)
from core.orchestrator.registry import build_default_registry

TENANT_A = "tenant_geo_a"
TENANT_B = "tenant_geo_b"


def _roster(
    *,
    tenant_id: str = TENANT_A,
    service_areas: tuple[str, ...] = ("CA", "US"),
    jurisdiction_frames: tuple[str, ...] = ("ca-msp-frame",),
    locales: tuple[str, ...] = ("en-CA",),
    policy_refs: tuple[str, ...] = ("policy-pack-001",),
) -> TenantGeoContextRosterV1:
    return TenantGeoContextRosterV1(
        tenant_id=tenant_id,
        declared_service_areas=service_areas,
        declared_jurisdiction_frames=jurisdiction_frames,
        expected_locales=locales,
        compliance_policy_pack_refs=policy_refs,
    )


def _context(
    *,
    tenant_id: str = TENANT_A,
    roster: TenantGeoContextRosterV1 | None = None,
) -> MissionContext:
    roster = roster or _roster(tenant_id=tenant_id)
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest_roster(roster),
        case_id=uuid4(),
        source_record_id=uuid4(),
    )


def _agent(
    tmp_path: Path,
    roster: TenantGeoContextRosterV1,
) -> GeoContextAgent:
    return GeoContextAgent(
        blackboard_root=tmp_path / "blackboard",
        roster=roster,
    )


class TestDeclaredFacts:
    def test_roster_declared_facts_emit(self, tmp_path: Path) -> None:
        roster = _roster()
        agent = _agent(tmp_path, roster)
        contribution = agent.analyze(_context(roster=roster))
        assert contribution.agent_id == GEO_CONTEXT_AGENT_ID
        assert contribution.layer == 2
        assert set(contribution.observed_facts) == {
            DECLARED_SERVICE_AREA,
            DECLARED_JURISDICTION_FRAME,
            EXPECTED_LOCALE,
            POLICY_PACK_REF,
        }

    def test_empty_roster_emits_no_facts(self, tmp_path: Path) -> None:
        roster = TenantGeoContextRosterV1(
            tenant_id=TENANT_A,
        )
        agent = _agent(tmp_path, roster)
        contribution = agent.analyze(_context(roster=roster))
        assert contribution.observed_facts == ()


class TestMismatchObservation:
    def test_mismatch_when_observed_country_not_in_declared_areas(
        self, tmp_path: Path
    ) -> None:
        roster = _roster(service_areas=("CA", "US"))
        agent = _agent(tmp_path, roster)
        brief = GeoIntelAgent().brief()
        contribution = agent.analyze(
            _context(roster=roster),
            geo_briefing=brief,
            observed_country_class="DE",
        )
        assert DECLARED_VS_OBSERVED_MISMATCH in contribution.observed_facts
        assert DECLARED_SERVICE_AREA in contribution.observed_facts

    def test_no_mismatch_when_observed_country_in_declared_areas(
        self, tmp_path: Path
    ) -> None:
        roster = _roster(service_areas=("CA", "US"))
        agent = _agent(tmp_path, roster)
        contribution = agent.analyze(
            _context(roster=roster),
            observed_country_class="ca",
        )
        assert DECLARED_VS_OBSERVED_MISMATCH not in contribution.observed_facts


class TestBoundaries:
    def test_challenge_returns_none(self, tmp_path: Path) -> None:
        agent = _agent(tmp_path, _roster())
        assert agent.challenge(()) is None

    def test_tenant_isolation_rejects_mismatched_context(
        self, tmp_path: Path
    ) -> None:
        roster = _roster(tenant_id=TENANT_A)
        agent = _agent(tmp_path, roster)
        with pytest.raises(GovernanceError, match="does not match"):
            agent.analyze(_context(tenant_id=TENANT_B, roster=roster))

    def test_facts_only_closed_vocabulary(self, tmp_path: Path) -> None:
        roster = _roster()
        agent = _agent(tmp_path, roster)
        contribution = agent.analyze(
            _context(roster=roster),
            geo_briefing=GeoIntelAgent().brief(),
            observed_country_class="DE",
        )
        assert all(fact in CLOSED_GEO_CONTEXT_FACTS for fact in contribution.observed_facts)
        forbidden = (
            "geo_signal",
            "geo_velocity_anomaly",
            "entrapment_score",
            "Reality Anchor",
            "tarpit",
            "shadow-serving",
            "Hack-Bot",
        )
        serialized = " ".join(contribution.observed_facts)
        for token in forbidden:
            assert token not in serialized

    def test_not_in_build_default_registry(self) -> None:
        registry = build_default_registry()
        assert GEO_CONTEXT_AGENT_ID not in registry

    def test_autonomous_action_disallowed(self, tmp_path: Path) -> None:
        agent = _agent(tmp_path, _roster())
        assert agent.autonomous_action_allowed is False

    def test_contribution_is_agent_contribution_type(self, tmp_path: Path) -> None:
        agent = _agent(tmp_path, _roster())
        contribution = agent.analyze(_context())
        assert isinstance(contribution, AgentContribution)
