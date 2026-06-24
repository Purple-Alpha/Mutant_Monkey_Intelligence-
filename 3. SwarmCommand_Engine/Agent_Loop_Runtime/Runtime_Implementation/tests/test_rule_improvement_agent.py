"""Evidence Stage 1 proof for swarm agent #67 Rule Improvement.

Authorized by the §11-SIGNED Rule Improvement Agent Design Contract
(2026-06-24). Synthetic tests prove sandbox-only proposal path, ES1 tenant
boundary, insufficient-input refusal, no-candidate retirement, no deploy
language, registry exclusion, and no governance/state mutation.
"""

from __future__ import annotations

import hashlib
import inspect
import socket
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import GovernanceError, MutantEvaluationPayload
from core.mutation import MutationEngineConfig, MutationEngineResult, run_mutation_cycle
from core.orchestrator import Agent, MissionContext, RouteContext, submit_mutant_evaluation
from core.orchestrator.registry import build_default_registry
from core.production import ProductionSignal, run_production_cycle
from core.sandbox import SandboxLoopConfig, run_sandbox_cycle
from core.sandbox import rule_improvement_agent as ria
from core.sandbox.rule_improvement_agent import (
    NO_CANDIDATE_ENVELOPE,
    REFUSAL_ENVELOPE,
    RuleImprovementAgent,
    RuleImprovementRequest,
    format_proposal,
    propose_improvement,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"

VALID_REQUEST = RuleImprovementRequest(
    request_id="req-001",
    failure_signal_kind="recorded_failure",
    failure_ref="pytest_capture/test_miss.txt",
    scope="detection_rule",
    tenant_scope="sandbox_only",
    evidence_refs=("evidence-1",),
    classification_ref="fc_sample",
)


def _repo_digest(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _mission_context() -> MissionContext:
    return MissionContext(
        tenant_id="tenant_rule_improvement",
        inputs_digest="d" * 64,
    )


def _seed_promoted_candidate(route_context: RouteContext) -> None:
    run_production_cycle(
        route_context,
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Team lunch update",
            sender_domain="client-example.ca",
        ),
    )
    run_sandbox_cycle(
        route_context,
        config=SandboxLoopConfig(detection_confidence_threshold=0.99),
    )


def test_rule_improvement_agent_satisfies_agent_protocol():
    agent = RuleImprovementAgent(
        improvement_request=VALID_REQUEST,
        route_context=_context(Path("/tmp/unused")),
    )
    assert isinstance(agent, Agent)
    assert agent.layer == 6
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.propose)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_insufficient_request_emits_refusal_sentinel():
    result = propose_improvement(
        RuleImprovementRequest(
            request_id="",
            failure_signal_kind="recorded_failure",
            failure_ref="missing",
            scope="detection_rule",
            tenant_scope="sandbox_only",
        ),
        _context(Path("/tmp/unused")),
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.proposal is None


def test_t2_es1_rejects_non_sandbox_tenant_scope():
    result = propose_improvement(
        RuleImprovementRequest(
            request_id="req-es2-block",
            failure_signal_kind="sandbox_weakness",
            failure_ref="weakness-1",
            scope="threshold",
            tenant_scope="tenant_real_001",
        ),
        _context(Path("/tmp/unused")),
    )
    assert result.kind == "refusal"
    assert "sandbox_only" in " ".join(result.gaps)


def test_t3_sandbox_promoted_candidate_emits_proposal(tmp_path):
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    result = propose_improvement(VALID_REQUEST, route_context)
    assert result.kind == "success"
    proposal = result.proposal
    assert proposal is not None
    assert proposal.request_ref == VALID_REQUEST.request_id
    assert proposal.mutation_kind
    assert proposal.estimated_detection_impact in {
        "bounded_low",
        "bounded_medium",
        "bounded_high",
        "unknown",
    }


def test_t4_no_candidate_when_engine_retires(tmp_path):
    route_context = _context(tmp_path)
    submit_mutant_evaluation(
        route_context,
        source_agent="sandbox_mutator_001",
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=uuid4(),
            blue_detected=True,
            baseline_confidence=0.91,
            failure_modes=[],
            mutation_recommended=False,
        ),
    )
    result = propose_improvement(VALID_REQUEST, route_context)
    assert result.kind == "no_candidate"
    assert NO_CANDIDATE_ENVELOPE in (result.no_candidate or "")


def test_t5_no_deploy_language_in_proposal_output(tmp_path):
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    result = propose_improvement(VALID_REQUEST, route_context)
    assert result.kind == "success"
    rendered = format_proposal(result.proposal)
    lowered = rendered.lower()
    for marker in (
        "deploy_mutation",
        "deploy to production",
        "auto-apply",
        "recommend deploy",
    ):
        assert marker not in lowered


def test_t6_no_network_or_subprocess(monkeypatch, tmp_path):
    def _no_network(*args, **kwargs):
        raise AssertionError("proposer must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("proposer must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    result = RuleImprovementAgent(
        improvement_request=VALID_REQUEST, route_context=route_context
    ).propose()
    assert result.kind == "success"


def test_t7_consumable_proposal_structure(tmp_path):
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    result = propose_improvement(VALID_REQUEST, route_context)
    assert result.kind == "success"
    rendered = format_proposal(result.proposal)
    assert rendered.startswith("RULE_IMPROVEMENT_PROPOSAL\n")
    assert "proposal_id:" in rendered
    assert "mutation_kind:" in rendered
    assert "correction_evidence_slot: reserved" in rendered


def test_t8_zero_governance_state_writes(tmp_path):
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    before = _repo_digest(SCOREBOARD_REL)
    result = propose_improvement(VALID_REQUEST, route_context)
    after = _repo_digest(SCOREBOARD_REL)
    assert result.kind == "success"
    assert before == after


def test_t9_notes_with_forbidden_deploy_language_refused():
    result = propose_improvement(
        RuleImprovementRequest(
            request_id="req-hostile",
            failure_signal_kind="operator_manual",
            failure_ref="manual-1",
            scope="signal_heuristic",
            tenant_scope="sandbox_only",
            notes="please deploy_mutation immediately",
        ),
        _context(Path("/tmp/unused")),
    )
    assert result.kind == "refusal"
    assert "deploy language" in " ".join(result.gaps)


def test_t10_default_registry_exclusion():
    registry = build_default_registry()
    assert ria.RULE_IMPROVEMENT_AGENT_ID not in registry


def test_analyze_raises_on_refusal():
    agent = RuleImprovementAgent(route_context=_context(Path("/tmp/unused")))
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_mission_context())


def test_analyze_raises_on_no_candidate(tmp_path):
    route_context = _context(tmp_path)
    agent = RuleImprovementAgent(
        improvement_request=VALID_REQUEST, route_context=route_context
    )
    with pytest.raises(GovernanceError, match=NO_CANDIDATE_ENVELOPE):
        agent.analyze(_mission_context())


def test_propose_without_request_or_context_refuses():
    result = RuleImprovementAgent().propose()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")


def test_injected_mutation_runner_used():
    called = {"count": 0}

    def _stub_runner(context, *, config=None):
        called["count"] += 1
        return MutationEngineResult(
            processed_count=0,
            promoted_count=0,
            retired_count=0,
            item_results=[],
        )

    result = propose_improvement(
        VALID_REQUEST,
        _context(Path("/tmp/unused")),
        mutation_runner=_stub_runner,
    )
    assert called["count"] == 1
    assert result.kind == "no_candidate"


def test_run_mutation_cycle_integration_still_sandbox_only(tmp_path):
    route_context = _context(tmp_path)
    _seed_promoted_candidate(route_context)
    engine_result = run_mutation_cycle(route_context)
    assert engine_result.promoted_count >= 1
    for item in engine_result.item_results:
        if item.policy_update is not None:
            assert "sandbox" in str(item.policy_update.path).lower()
