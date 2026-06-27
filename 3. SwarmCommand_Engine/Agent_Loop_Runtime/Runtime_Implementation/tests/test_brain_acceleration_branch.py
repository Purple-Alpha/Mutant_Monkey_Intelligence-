"""Brain Acceleration Branch — tiered orchestration wiring tests."""

from __future__ import annotations

import pytest

from core.blackboard.models import (
    AgentRegistryEntry,
    AgentRole,
    Environment,
    GovernanceError,
    RecordType,
)
from core.command.risk_triage_agent import (
    DetectorEvidenceRecord,
    RiskTriageAgent,
    SCORING_POLICY_VERSION,
)
from core.control_plane.triage_prefilter import RiskTriageGatewayPreFilter
from core.control_plane import (
    AgentIdentityGateway,
    ControlPlaneAuditTrail,
    ControlPlaneEvent,
    GatewayController,
    GatewayRejected,
    GatewayRequest,
    LoopDetector,
    ReasoningTier,
    RoleTier,
    SessionBudgetStore,
    enact_block,
    resolve_reasoning_tier,
    reasoning_token_cap,
    BreakerStore,
    TenantSegmentationController,
    RingController,
)
from core.orchestrator.agent_contract import MissionContext, slice_mission_context_for_agent
from core.orchestrator.swarm_commander import SwarmCommander
from core.orchestrator.agent_contract import AgentContribution


class _StubAgent:
    agent_id = "blue_detection_001"
    layer = 2
    authority_level = 1
    stage_allowed = "stage_a"
    autonomous_action_allowed = False
    last_context: MissionContext | None = None

    def analyze(self, context: MissionContext) -> AgentContribution:
        self.last_context = context
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=("fact:ok",),
        )

    def challenge(self, contributions):
        return None


def _gateway() -> GatewayController:
    audit = ControlPlaneAuditTrail()
    identity = AgentIdentityGateway()
    gw = GatewayController(
        identity=identity,
        rings=RingController(audit=audit),
        budgets=SessionBudgetStore(audit=audit),
        breakers=BreakerStore(),
        loop_detector=LoopDetector(),
        segmentation=TenantSegmentationController(),
        audit=audit,
        triage_prefilter=RiskTriageGatewayPreFilter(),
    )
    identity.issue(
        token="tok",
        agent_id="blue_detection_001",
        tenant_id="tenant_a",
        tool_scope={"scan"},
    )
    gw.budgets.open_session("s1", tier=RoleTier.DETECTION)
    return gw


def test_slice_mission_context_sets_dispatch_agent_id():
    base = MissionContext(tenant_id="t1", inputs_digest="a" * 64)
    sliced = slice_mission_context_for_agent(base, "blue_detection_001")
    assert sliced.dispatch_agent_id == "blue_detection_001"
    assert sliced.case_id == base.case_id


def _detection_entry(agent_id: str = "blue_detection_001") -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Test Detection Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        layer=2,
        authority_level=1,
        stage_allowed="stage_a",
    )


def test_run_case_injects_per_agent_context_slice():
    agent = _StubAgent()
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    ctx = MissionContext(tenant_id="t1", inputs_digest="b" * 64)
    commander.run_case(ctx, [agent])
    assert agent.last_context is not None
    assert agent.last_context.dispatch_agent_id == agent.agent_id
    assert agent.last_context.tenant_id == "t1"


def test_reasoning_tier_verdict_path_is_high():
    assert resolve_reasoning_tier("reconciliation_agent", "analyze") == ReasoningTier.HIGH
    assert resolve_reasoning_tier("geo_velocity_agent", "scan") == ReasoningTier.LOW
    assert reasoning_token_cap(ReasoningTier.HIGH) > reasoning_token_cap(ReasoningTier.LOW)


def test_enact_block_requires_section11_gate():
    with pytest.raises(RuntimeError, match="REQUIRES_§11_GATE"):
        enact_block()


def test_gateway_triage_scores_without_rejecting():
    gw = _gateway()
    record = DetectorEvidenceRecord(
        detector_id="credential_phishing",
        detector_contract_version="v1",
        evidence_ref="ev-1",
        emitted_at="2026-06-27T00:00:00+00:00",
        signal_tags=("credential_phishing",),
    )
    req = GatewayRequest(
        token="tok",
        claimed_agent_id="blue_detection_001",
        tenant_id="tenant_a",
        tool="scan",
        session_id="s1",
        args={
            "risk_triage_prefilter": {
                "message_id": "msg-1",
                "detector_outputs": [record],
                "scoring_policy_version": SCORING_POLICY_VERSION,
            }
        },
    )
    decision = gw.handle(req)
    assert decision.dispatched
    triage_events = [
        e for e in gw.audit.entries() if e.event == ControlPlaneEvent.TRIAGE_SCORED
    ]
    assert len(triage_events) == 1
