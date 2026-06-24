"""Evidence Stage 1 proof for swarm agent #1 Swarm Commander.

Authorized by the §11-SIGNED Swarm Commander contract
(docs/mmi/contracts/001_swarm_commander_contract.md) and Matt build
authorization (MMI-DEC-111). Synthetic tests prove RC-AUTH route-only
dispatch, DER allowlist compliance, disposition mapping, registry exclusion,
routing-by-score rejection, and purity guards.
"""

from __future__ import annotations

import inspect
import socket
import subprocess

import pytest

from core.blackboard.models import (
    AgentRegistryEntry,
    AgentRole,
    Environment,
    GovernanceError,
    RecordType,
)
from core.command import (
    DISPOSITION_POLICY_VERSION,
    ROUTING_POLICY_VERSION,
    SCORING_POLICY_VERSION,
    SwarmCommanderAgent,
    apply_routing_policy_hints,
    assert_der_rc_auth_compliant,
    format_route_summary,
)
from core.orchestrator.agent_contract import (
    AgentContribution,
    ChallengeResult,
    DecisionEvidenceRecord,
    DecisionTimestamps,
    MissionContext,
)
from core.orchestrator.registry import build_default_registry


def _detection_entry(
    agent_id: str = "blue_detection_001",
    *,
    layer: int = 2,
    authority_level: int = 1,
) -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Test Detection Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        layer=layer,
        authority_level=authority_level,
        stage_allowed="stage_a",
    )


class _StubAgent:
    def __init__(
        self,
        agent_id: str = "blue_detection_001",
        *,
        observed_facts: tuple[str, ...] = ("sender_domain_mismatch",),
    ) -> None:
        self.agent_id = agent_id
        self.layer = 2
        self.authority_level = 1
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False
        self._observed_facts = observed_facts

    def analyze(self, context: MissionContext) -> AgentContribution:
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=self._observed_facts,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_commander", inputs_digest="a" * 64)


def test_swarm_commander_agent_carries_rc_auth_metadata():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    assert agent.agent_id == "swarm_commander_001"
    assert agent.layer == 1
    assert agent.authority_level == 4
    assert agent.autonomous_action_allowed is False
    assert agent.disposition_policy_version == DISPOSITION_POLICY_VERSION
    assert inspect.ismethod(agent.run_case)


def test_run_case_produces_der_with_contribution():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(_context(), [_StubAgent()])
    assert len(der.contributions) == 1
    assert der.disposition == "suspicious"
    assert der.audit_record_id is None


def test_human_required_maps_to_requested_human_state():
    agent = SwarmCommanderAgent({})
    der = agent.run_case(_context(), [])
    assert der.disposition == "human_required"
    assert der.human_state == "requested"


def test_empty_facts_disposition_is_clear():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(_context(), [_StubAgent(observed_facts=())])
    assert der.disposition == "clear"
    assert der.human_state == "not_required"


def test_assert_der_rc_auth_rejects_audit_fields():
    der = DecisionEvidenceRecord.model_construct(
        case_id=_context().case_id,
        inputs_digest="a" * 64,
        disposition="suspicious",
        human_state="not_required",
        timestamps=DecisionTimestamps(detected_at=_context().created_at),
        audit_record_id="forbidden",
    )
    with pytest.raises(GovernanceError, match="audit fields"):
        assert_der_rc_auth_compliant(der)


def test_assert_der_rc_auth_rejects_human_state_mismatch():
    der = DecisionEvidenceRecord.model_construct(
        case_id=_context().case_id,
        inputs_digest="a" * 64,
        disposition="clear",
        human_state="requested",
        timestamps=DecisionTimestamps(detected_at=_context().created_at),
    )
    with pytest.raises(GovernanceError, match="human_state=requested requires"):
        assert_der_rc_auth_compliant(der)


def test_assert_der_rc_auth_rejects_forbidden_scorer_tokens_in_facts():
    der = DecisionEvidenceRecord.model_construct(
        case_id=_context().case_id,
        inputs_digest="a" * 64,
        contributions=(
            AgentContribution(
                agent_id="blue_detection_001",
                layer=2,
                observed_facts=("aggregate_risk_score:72",),
            ),
        ),
        disposition="suspicious",
        human_state="not_required",
        timestamps=DecisionTimestamps(detected_at=_context().created_at),
    )
    with pytest.raises(GovernanceError, match="forbidden scorer"):
        assert_der_rc_auth_compliant(der)


def test_assert_der_rc_auth_compliant_on_success_path():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(_context(), [_StubAgent()])
    assert_der_rc_auth_compliant(der)


def test_rejects_unknown_agent_before_dispatch():
    agent = SwarmCommanderAgent({})
    with pytest.raises(GovernanceError, match="unknown agent"):
        agent.run_case(_context(), [_StubAgent()])


def test_rejects_routing_by_score_telemetry_keys():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    with pytest.raises(GovernanceError, match="routing-by-score"):
        agent.run_case(
            _context(),
            [_StubAgent()],
            risk_triage_telemetry={"auto_select_agents": True},
        )


def test_ignores_benign_score_telemetry_without_routing_keys():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent()],
        risk_triage_telemetry={
            "aggregate_risk_score": 72,
            "scoring_policy_version": SCORING_POLICY_VERSION,
        },
    )
    assert der.disposition == "suspicious"
    assert agent.last_route_policy_audit is not None
    assert agent.last_route_policy_audit.hints_applied == ()


def _telemetry(**overrides):
    payload = {
        "message_id": "msg-1",
        "tenant_id": "tenant_commander",
        "aggregate_risk_score": 0,
        "axis_scores": {},
        "scoring_reason_codes": (),
        "scoring_policy_version": SCORING_POLICY_VERSION,
    }
    payload.update(overrides)
    return payload


def test_aggregate_score_85_elevates_clear_or_suspicious_to_hold():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent()],
        risk_triage_telemetry=_telemetry(aggregate_risk_score=85),
    )
    assert der.disposition == "hold"
    assert der.human_state == "not_required"
    assert "aggregate_risk_score>=85->hold" in agent.last_route_policy_audit.hints_applied


def test_aggregate_score_95_elevates_to_human_required():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent()],
        risk_triage_telemetry=_telemetry(aggregate_risk_score=95),
    )
    assert der.disposition == "human_required"
    assert der.human_state == "requested"


def test_axis_score_90_steps_up_one_caution_level():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent(observed_facts=())],
        risk_triage_telemetry=_telemetry(
            aggregate_risk_score=10,
            axis_scores={"vendor_fraud": 90},
        ),
    )
    assert der.disposition == "suspicious"


def test_policy_version_mismatch_skips_hints():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent()],
        risk_triage_telemetry=_telemetry(
            aggregate_risk_score=99,
            scoring_policy_version="mmi_rt_v0",
        ),
    )
    assert der.disposition == "suspicious"
    assert agent.last_route_policy_audit.hints_applied == ()


def test_hints_never_lower_caution():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [],
        risk_triage_telemetry=_telemetry(aggregate_risk_score=0),
    )
    assert der.disposition == "human_required"


def test_rejects_risk_triage_forbidden_routing_key_on_telemetry():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    with pytest.raises(GovernanceError, match="routing-by-score"):
        agent.run_case(
            _context(),
            [_StubAgent()],
            risk_triage_telemetry=_telemetry(route_to="blue_detection_001"),
        )


def test_route_policy_audit_records_base_and_final_disposition():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    agent.run_case(
        _context(),
        [_StubAgent()],
        risk_triage_telemetry=_telemetry(aggregate_risk_score=85),
    )
    audit = agent.last_route_policy_audit
    assert audit.routing_policy_version == ROUTING_POLICY_VERSION
    assert audit.base_disposition == "suspicious"
    assert audit.final_disposition == "hold"
    assert audit.hints_applied


def test_apply_routing_policy_hints_combines_rules_with_max_caution():
    final, hints = apply_routing_policy_hints(
        "suspicious",
        _telemetry(aggregate_risk_score=96, axis_scores={"vendor_fraud": 91}),
    )
    assert final == "human_required"
    assert "aggregate_risk_score>=95->human_required" in hints
    assert "axis_score>=90->step_up" in hints


def test_format_route_summary_is_machine_readable():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(_context(), [_StubAgent()])
    text = format_route_summary(der)
    assert "disposition=suspicious" in text
    assert f"policy={DISPOSITION_POLICY_VERSION}" in text


def test_not_in_build_default_registry():
    registry = build_default_registry()
    assert "swarm_commander_001" not in registry


def test_anchor_provider_seam_sets_evidence_anchor():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(
        _context(),
        [_StubAgent()],
        anchor_provider=lambda: "sha256:" + "c" * 64,
    )
    assert der.evidence_anchor == "sha256:" + "c" * 64


def test_purity_guard_no_network_or_subprocess(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("SwarmCommanderAgent must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("SwarmCommanderAgent must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    agent.run_case(_context(), [_StubAgent()])
    source = inspect.getsource(SwarmCommanderAgent)
    assert "socket" not in source
    assert "subprocess" not in source


def test_der_serialized_form_excludes_scorer_tokens():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    der = agent.run_case(_context(), [_StubAgent()])
    payload = der.model_dump_json()
    for forbidden in (
        "aggregate_risk_score",
        "recommended_action",
        "plain_english_summary",
    ):
        assert forbidden not in payload


def test_deterministic_disposition_for_same_inputs():
    agent = SwarmCommanderAgent({"blue_detection_001": _detection_entry()})
    first = agent.run_case(_context(), [_StubAgent(observed_facts=("dmarc_fail",))])
    second = agent.run_case(_context(), [_StubAgent(observed_facts=("dmarc_fail",))])
    assert first.disposition == second.disposition
    assert first.human_state == second.human_state


def test_contradicted_challenge_forces_human_required():
    challenge_entry = AgentRegistryEntry(
        agent_id="challenge_001",
        display_name="Test Challenge Agent",
        role=AgentRole.BLUE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types=set(),
        layer=5,
        authority_level=3,
        stage_allowed="stage_a",
    )

    class _ChallengeAgent:
        agent_id = "challenge_001"
        layer = 5
        authority_level = 3
        stage_allowed = "stage_a"
        autonomous_action_allowed = False

        def analyze(self, context: MissionContext) -> AgentContribution:
            raise AssertionError("analyze must not run for challenge agents")

        def challenge(
            self, contributions: tuple[AgentContribution, ...]
        ) -> ChallengeResult:
            return ChallengeResult(
                agent_id=self.agent_id,
                challenge_outcome="contradicted",
                challenge_basis="Second pass could not reproduce fact.",
            )

    agent = SwarmCommanderAgent(
        {
            "blue_detection_001": _detection_entry(),
            "challenge_001": challenge_entry,
        }
    )
    der = agent.run_case(
        _context(),
        [_StubAgent(observed_facts=("from_reply_to_divergence",))],
        challenge_agents=[_ChallengeAgent()],
    )
    assert der.disposition == "human_required"
    assert der.human_state == "requested"


def test_wrapper_delegates_to_legacy_spine_and_applies_annex_hints():
    assert "SwarmCommander" in inspect.getsource(SwarmCommanderAgent)
    assert "apply_routing_policy_hints" in inspect.getsource(SwarmCommanderAgent.run_case)
