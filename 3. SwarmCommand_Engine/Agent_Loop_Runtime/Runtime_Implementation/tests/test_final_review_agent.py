"""Evidence Stage 1 proof for swarm agent #70 Final Review (Slice B)."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import GovernanceError
from core.orchestrator.agent_contract import (
    FINAL_REVIEW_AGENT_ID,
    AgentContribution,
    ChallengeResult,
    DecisionEvidenceRecord,
    DecisionTimestamps,
    MissionContext,
)
from core.orchestrator.final_review_agent import (
    AGENT_VERSION,
    FinalReviewAgent,
    GovCheckResult,
    GovernanceFinalizationCandidate,
    ManifestEntry,
    assemble_final_review_packet,
    derive_audit_record_id,
    readiness_from_checks,
)
from core.orchestrator.registry import build_default_registry

TENANT = "tenant_final_review_demo"
DIGEST = "a" * 64
ANCHOR = "sha256:" + "b" * 64


def _context(**overrides) -> MissionContext:
    kwargs = dict(
        tenant_id=TENANT,
        inputs_digest=DIGEST,
        case_id=uuid4(),
        source_record_id=uuid4(),
    )
    kwargs.update(overrides)
    return MissionContext(**kwargs)


def _der(**overrides) -> DecisionEvidenceRecord:
    case_id = overrides.pop("case_id", uuid4())
    kwargs = dict(
        case_id=case_id,
        inputs_digest=DIGEST,
        disposition="suspicious",
        contributions=(
            AgentContribution(
                agent_id="blue_detection_001",
                layer=2,
                observed_facts=("lookalike_sender_domain",),
            ),
        ),
        timestamps=DecisionTimestamps(detected_at=datetime.now(timezone.utc)),
        evidence_anchor=ANCHOR,
    )
    kwargs.update(overrides)
    return DecisionEvidenceRecord(**kwargs)


def _coherent_agent(context: MissionContext | None = None) -> FinalReviewAgent:
    ctx = context or _context()
    der = _der(case_id=ctx.case_id, inputs_digest=ctx.inputs_digest)
    return FinalReviewAgent(der=der)


def test_der_coherence_ok_sets_audit_record_id():
    ctx = _context()
    agent = _coherent_agent(ctx)
    contribution = agent.analyze(ctx)
    assert "coherence_ok" in contribution.observed_facts
    assert contribution.layer == 6
    assert contribution.agent_id == FINAL_REVIEW_AGENT_ID

    audited = agent.audited_der()
    assert audited is not None
    assert audited.audit_writer_agent_id == FINAL_REVIEW_AGENT_ID
    assert audited.audit_record_id == derive_audit_record_id(audited.decision_id)


def test_der_inputs_digest_mismatch_blocks_audit():
    ctx = _context()
    der = _der(case_id=ctx.case_id, inputs_digest="c" * 64)
    agent = FinalReviewAgent(der=der)
    contribution = agent.analyze(ctx)
    assert "coherence_gap" in contribution.observed_facts
    assert agent.audited_der() is None


def test_der_missing_contributions_blocks_audit():
    ctx = _context()
    der = _der(
        case_id=ctx.case_id,
        inputs_digest=ctx.inputs_digest,
        contributions=(),
        disposition="escalate",
    )
    agent = FinalReviewAgent(der=der)
    agent.analyze(ctx)
    assert agent.audited_der() is None


def test_der_pre_set_audit_record_blocks_audit():
    ctx = _context()
    der = _der(
        case_id=ctx.case_id,
        inputs_digest=ctx.inputs_digest,
        audit_record_id="preexisting",
        audit_writer_agent_id=FINAL_REVIEW_AGENT_ID,
    )
    agent = FinalReviewAgent(der=der)
    agent.analyze(ctx)
    assert agent.audited_der() is None


def test_gov_packet_ready_when_all_checks_pass():
    candidate = GovernanceFinalizationCandidate(
        candidate_kind="contract_sign",
        candidate_id="mmi_70_contract",
        manifest=(
            ManifestEntry(
                path="4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md",
                sha256="abc",
                attested_present=True,
            ),
        ),
        check_results=(
            GovCheckResult("C1", "PASS", "contract_path"),
            GovCheckResult("C2", "PASS", "gate_artifact"),
            GovCheckResult("C3", "N/A", ""),
        ),
    )
    agent = FinalReviewAgent(gov_candidate=candidate)
    packet = agent.assemble_gov_packet()
    assert packet.readiness_verdict == "READY-FOR-§11"
    assert packet.schema_version == "FINAL_REVIEW_PACKET_v1"
    assert packet.blocking_check_ids == ()
    assert "APPROVED" not in packet.packet_hash


def test_gov_false_ready_rejected_on_fail_check():
    candidate = GovernanceFinalizationCandidate(
        candidate_kind="gated_reconcile",
        candidate_id="agent_99",
        check_results=(
            GovCheckResult("C4", "FAIL", "missing_completion_gate"),
            GovCheckResult("C1", "PASS", "contract"),
        ),
    )
    packet = assemble_final_review_packet(candidate)
    assert packet.readiness_verdict == "NOT-READY"
    assert "C4" in packet.blocking_check_ids


def test_gov_manifest_missing_yields_not_ready():
    candidate = GovernanceFinalizationCandidate(
        candidate_kind="agent_build",
        candidate_id="build_70",
        manifest=(
            ManifestEntry(path="tests/test_final_review_agent.py", attested_present=False),
        ),
        check_results=(GovCheckResult("C1", "PASS", "contract"),),
    )
    packet = assemble_final_review_packet(candidate)
    assert packet.readiness_verdict == "NOT-READY"
    assert packet.could_not_verify


def test_readiness_requires_applicable_pass():
    verdict, blocking = readiness_from_checks(
        (GovCheckResult("C1", "N/A", ""), GovCheckResult("C2", "N/A", "")),
        blind_spots=(),
    )
    assert verdict == "NOT-READY"
    assert blocking == ("no_applicable_checks",)


def test_analyze_raises_in_gov_mode():
    candidate = GovernanceFinalizationCandidate(
        candidate_kind="contract_sign",
        candidate_id="x",
        check_results=(GovCheckResult("C1", "PASS", "ref"),),
    )
    agent = FinalReviewAgent(gov_candidate=candidate)
    with pytest.raises(GovernanceError, match="FR-GOV"):
        agent.analyze(_context())


def test_dual_mode_constructor_rejected():
    with pytest.raises(GovernanceError, match="exactly one"):
        FinalReviewAgent(der=_der(), gov_candidate=GovernanceFinalizationCandidate(
            candidate_kind="contract_sign", candidate_id="x"
        ))


def test_not_in_default_registry():
    assert FINAL_REVIEW_AGENT_ID not in build_default_registry()


def test_challenge_returns_none():
    ctx = _context()
    agent = _coherent_agent(ctx)
    contribution = agent.analyze(ctx)
    assert agent.challenge((contribution,)) is None
    assert not isinstance(agent.challenge((contribution,)), ChallengeResult)


def test_no_slice_a_conflation_in_wrapper():
    source = Path(__file__).parents[1] / "core/orchestrator/final_review_agent.py"
    text = source.read_text(encoding="utf-8")
    assert "from audit_tools" not in text
    assert "import audit_tools" not in text
    assert "from core.evidence_package.package_auditor" not in text
    assert "audit_package" not in text


def test_no_network_in_wrapper():
    source = Path(__file__).parents[1] / "core/orchestrator/final_review_agent.py"
    text = source.read_text(encoding="utf-8")
    assert "socket" not in text
    assert "subprocess" not in text
    assert "requests" not in text
    assert "subprocess" not in inspect.getsource(FinalReviewAgent)


def test_agent_version_constant():
    ctx = _context()
    agent = _coherent_agent(ctx)
    packet = FinalReviewAgent(
        gov_candidate=GovernanceFinalizationCandidate(
            candidate_kind="contract_sign",
            candidate_id="v",
            check_results=(GovCheckResult("C1", "PASS", "r"),),
        )
    ).assemble_gov_packet()
    assert packet.agent_version == AGENT_VERSION
