"""Evidence Stage 1 proof for swarm agent #65 Correction Evidence.

Authorized by the §11-SIGNED Correction Evidence Agent Design Contract
(2026-06-24). Synthetic tests prove sandbox-only validation path, ES1 tenant
boundary, insufficient-input refusal, four proof bars, adversarial guard,
no promote/apply language, registry exclusion, and no governance/state mutation.
"""

from __future__ import annotations

import hashlib
import inspect
import socket
import subprocess
from pathlib import Path

import pytest

from core.blackboard import GovernanceError
from core.orchestrator import Agent, MissionContext, RouteContext
from core.orchestrator.registry import build_default_registry
from core.production import ProductionLoopConfig, ProductionSignal, run_production_cycle
from core.sandbox import correction_evidence_agent as cea
from core.sandbox.correction_evidence_agent import (
    REFUSAL_ENVELOPE,
    CorrectionEvidenceAgent,
    CorrectionValidationRequest,
    EvaluationResult,
    RegressionCorpusCase,
    attach_correction_evidence_slot,
    format_packet,
    validate_correction_evidence,
)
from core.sandbox.failure_classification_agent import FailureClassification
from core.sandbox.rule_improvement_agent import RuleImprovementProposal

REPO_ROOT = Path(__file__).resolve().parents[4]
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"
FIXTURE_MANIFEST = (
    Path(__file__).resolve().parent / "fixtures" / "correction_evidence" / "manifest.json"
)

VALID_REQUEST = CorrectionValidationRequest(
    request_id="cvr-001",
    failure_ref="pytest_capture/test_miss.txt",
    proposal_ref="rip_test001",
    tenant_scope="sandbox_only",
    classification_ref="fc-001",
    corpus_refs=("ce-neg-001", "ce-neg-002", "ce-neg-003"),
    evidence_refs=("evidence-1",),
)

GOOD_PROPOSAL = RuleImprovementProposal(
    proposal_id="rip_test001",
    request_ref="req-001",
    mutation_kind="threshold_adjust",
    baseline_agent_id="blue_detection_001",
    candidate_agent_id="blue_detection_001_mut",
    baseline_confidence=0.70,
    candidate_confidence=0.85,
    sandbox_evidence_ids=("se-1", "se-2"),
    engine_retired_reason=None,
    estimated_detection_impact="bounded_medium",
    blast_radius_note="parameter keys: threshold",
    rationale=(
        "Sandbox mutation candidate threshold_adjust for failure_ref "
        "pytest_capture/test_miss.txt with confidence delta 0.70 -> 0.85"
    ),
)

GOOD_CORPUS = (
    RegressionCorpusCase("ce-neg-001", False),
    RegressionCorpusCase("ce-neg-002", False),
    RegressionCorpusCase("ce-neg-003", False),
)

GOOD_CLASSIFICATION = FailureClassification(
    id="fc-001",
    failure_ref="pytest_capture/test_miss.txt",
    category="REGRESSION",
    severity="MEDIUM",
    evidence_ref="evidence-1",
    rationale="Recorded miss in sandbox replay.",
)


def _repo_digest(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _mission_context() -> MissionContext:
    return MissionContext(
        tenant_id="tenant_correction_evidence",
        inputs_digest="d" * 64,
    )


def _seed_sandbox_context(route_context: RouteContext) -> None:
    run_production_cycle(
        route_context,
        tenant_id="tenant_demo",
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="Team lunch update",
            sender_domain="client-example.ca",
        ),
        config=ProductionLoopConfig(confidence_threshold=0.99),
    )


def test_correction_evidence_agent_satisfies_agent_protocol():
    agent = CorrectionEvidenceAgent(
        validation_request=VALID_REQUEST,
        proposal=GOOD_PROPOSAL,
        route_context=_context(Path("/tmp/unused")),
        corpus_cases=GOOD_CORPUS,
    )
    assert isinstance(agent, Agent)
    assert agent.layer == 6
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.validate)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_insufficient_request_emits_refusal_sentinel():
    result = validate_correction_evidence(
        CorrectionValidationRequest(
            request_id="",
            failure_ref="missing",
            proposal_ref="rip_test001",
            tenant_scope="sandbox_only",
        ),
        GOOD_PROPOSAL,
        _context(Path("/tmp/unused")),
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.packet is None


def test_t2_es1_rejects_non_sandbox_tenant_scope():
    result = validate_correction_evidence(
        CorrectionValidationRequest(
            request_id="cvr-es2-block",
            failure_ref="miss-1",
            proposal_ref="rip_test001",
            tenant_scope="tenant_real_001",
        ),
        GOOD_PROPOSAL,
        _context(Path("/tmp/unused")),
    )
    assert result.kind == "refusal"
    assert "sandbox_only" in " ".join(result.gaps)


def test_t3_all_proof_bars_emit_sufficient(tmp_path):
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        classification=GOOD_CLASSIFICATION,
        corpus_cases=GOOD_CORPUS,
    )
    assert result.kind == "success"
    packet = result.packet
    assert packet is not None
    assert packet.verdict == "SUFFICIENT"
    assert packet.gaps == ()
    assert packet.proposal_ref == GOOD_PROPOSAL.proposal_id


def test_t4_insufficient_when_fix_proof_fails(tmp_path):
    weak_proposal = RuleImprovementProposal(
        proposal_id="rip_test001",
        request_ref="req-001",
        mutation_kind="threshold_adjust",
        baseline_agent_id="blue_detection_001",
        candidate_agent_id="blue_detection_001_mut",
        baseline_confidence=0.85,
        candidate_confidence=0.70,
        sandbox_evidence_ids=(),
        engine_retired_reason=None,
        estimated_detection_impact="bounded_medium",
        blast_radius_note="parameter keys: threshold",
        rationale="No confidence improvement.",
    )
    result = validate_correction_evidence(
        VALID_REQUEST,
        weak_proposal,
        _context(tmp_path),
        corpus_cases=GOOD_CORPUS,
    )
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"
    assert "fix proof bar not satisfied" in result.packet.gaps


def test_t5_insufficient_when_regression_misses(tmp_path):
    corpus = (
        RegressionCorpusCase("ce-neg-001", False),
        RegressionCorpusCase("ce-neg-002", True),
        RegressionCorpusCase("ce-neg-003", False),
    )
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        _context(tmp_path),
        corpus_cases=corpus,
    )
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"
    assert "no-regression proof bar not satisfied" in result.packet.gaps


def test_t6_insufficient_when_blast_radius_unbounded(tmp_path):
    proposal = RuleImprovementProposal(
        proposal_id="rip_test001",
        request_ref="req-001",
        mutation_kind="threshold_adjust",
        baseline_agent_id="blue_detection_001",
        candidate_agent_id="blue_detection_001_mut",
        baseline_confidence=0.70,
        candidate_confidence=0.85,
        sandbox_evidence_ids=("se-1",),
        engine_retired_reason=None,
        estimated_detection_impact="unknown",
        blast_radius_note="unbounded",
        rationale="Candidate with unknown impact.",
    )
    result = validate_correction_evidence(
        VALID_REQUEST,
        proposal,
        _context(tmp_path),
        corpus_cases=GOOD_CORPUS,
    )
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"
    assert "blast-radius proof bar not satisfied" in result.packet.gaps


def test_t7_no_promote_language_in_packet_output(tmp_path):
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        classification=GOOD_CLASSIFICATION,
        corpus_cases=GOOD_CORPUS,
    )
    rendered = format_packet(result.packet)
    lowered = rendered.lower()
    for marker in (
        "deploy_mutation",
        "deploy to production",
        "auto-apply",
        "auto-promote",
        "apply the rule",
    ):
        assert marker not in lowered


def test_t8_no_network_or_subprocess(monkeypatch, tmp_path):
    def _no_network(*args, **kwargs):
        raise AssertionError("validator must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("validator must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = CorrectionEvidenceAgent(
        validation_request=VALID_REQUEST,
        proposal=GOOD_PROPOSAL,
        route_context=route_context,
        corpus_cases=GOOD_CORPUS,
    ).validate()
    assert result.packet is not None
    assert result.packet.verdict == "SUFFICIENT"


def test_t9_consumable_packet_structure(tmp_path):
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        classification=GOOD_CLASSIFICATION,
        corpus_cases=GOOD_CORPUS,
    )
    rendered = format_packet(result.packet)
    assert rendered.startswith("CORRECTION_EVIDENCE_PACKET\n")
    assert "packet_id:" in rendered
    assert "verdict: SUFFICIENT" in rendered
    assert "reproducibility:" in rendered


def test_t10_zero_governance_state_writes(tmp_path):
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    before = _repo_digest(SCOREBOARD_REL)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        corpus_cases=GOOD_CORPUS,
    )
    after = _repo_digest(SCOREBOARD_REL)
    assert result.packet is not None
    assert before == after


def test_t11_adversarial_proposal_cannot_force_sufficient_without_proof_bars(tmp_path):
    crafted = RuleImprovementProposal(
        proposal_id="rip_test001",
        request_ref="req-001",
        mutation_kind="crafted",
        baseline_agent_id="blue_detection_001",
        candidate_agent_id="blue_detection_001_mut",
        baseline_confidence=0.70,
        candidate_confidence=0.99,
        sandbox_evidence_ids=(),
        engine_retired_reason=None,
        estimated_detection_impact="bounded_high",
        blast_radius_note="parameter keys: threshold",
        rationale="Crafted high-confidence proposal without evidence ids.",
    )
    result = validate_correction_evidence(
        VALID_REQUEST,
        crafted,
        _context(tmp_path),
        corpus_cases=GOOD_CORPUS,
    )
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"


def test_t12_sufficient_populates_correction_evidence_slot(tmp_path):
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        classification=GOOD_CLASSIFICATION,
        corpus_cases=GOOD_CORPUS,
    )
    attached = attach_correction_evidence_slot(GOOD_PROPOSAL, result.packet)
    assert attached.correction_evidence_slot == result.packet.packet_id


def test_t13_classification_promotion_path_gap(tmp_path):
    classification = FailureClassification(
        id="fc-flake",
        failure_ref="pytest_capture/test_miss.txt",
        category="FLAKE",
        severity="LOW",
        evidence_ref="evidence-1",
        rationale="Flaky signal only.",
    )
    route_context = _context(tmp_path)
    _seed_sandbox_context(route_context)
    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        route_context,
        classification=classification,
        corpus_cases=GOOD_CORPUS,
    )
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"
    assert any("promotion path" in gap or "severity" in gap for gap in result.packet.gaps)


def test_t14_default_registry_exclusion():
    registry = build_default_registry()
    assert cea.CORRECTION_EVIDENCE_AGENT_ID not in registry


def test_t15_injected_evaluation_runner_used():
    called = {"count": 0}

    def _stub_runner(request, proposal, route_context, corpus_cases):
        del request, proposal, route_context, corpus_cases
        called["count"] += 1
        return EvaluationResult(
            fix_passed=False,
            fix_proof="stub",
            no_regression_passed=False,
            no_regression_proof="stub",
            regression_new_misses=("case-1",),
            blast_radius_passed=False,
            blast_radius_estimate="stub",
            sandbox_evidence_ids=(),
        )

    result = validate_correction_evidence(
        VALID_REQUEST,
        GOOD_PROPOSAL,
        _context(Path("/tmp/unused")),
        corpus_cases=GOOD_CORPUS,
        evaluation_runner=_stub_runner,
    )
    assert called["count"] == 1
    assert result.packet is not None
    assert result.packet.verdict == "INSUFFICIENT"


def test_fixture_manifest_present_for_es1_corpus():
    assert FIXTURE_MANIFEST.is_file()
    assert "correction_evidence_es1_v1" in FIXTURE_MANIFEST.read_text()


def test_analyze_raises_on_refusal():
    agent = CorrectionEvidenceAgent(route_context=_context(Path("/tmp/unused")))
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_mission_context())


def test_validate_without_request_or_context_refuses():
    result = CorrectionEvidenceAgent().validate()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
