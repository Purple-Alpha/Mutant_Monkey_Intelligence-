"""Evidence Stage 1 proof for swarm agent #64 Failure Classification.

Authorized by the §11-SIGNED Failure Classification Agent Design Contract
(2026-06-21). Synthetic tests prove evidence-traced labels, taxonomy bounds,
grounded severity, insufficient-input refusal, no response language, no
remediation/re-execution, no implementation reads, consumable output, registry
exclusion, authority-failure handling, and no governance/state mutation.
"""

from __future__ import annotations

import hashlib
import inspect
import socket
import subprocess
from pathlib import Path

import pytest

from core.blackboard import GovernanceError
from core.orchestrator import Agent, MissionContext
from core.orchestrator.registry import build_default_registry
from core.sandbox import failure_classification_agent as fca
from core.sandbox.failure_classification_agent import (
    CATEGORY_SEVERITY,
    REFUSAL_ENVELOPE,
    FailureClassificationAgent,
    FailureRecord,
    classify_failure_record,
    format_classification,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"

AUTHORITY_PROBE_RECORD = FailureRecord(
    failure_ref="audit_outputs/authority_probe_run.txt",
    source_kind="authority_probe",
    body=(
        "AUTHORITY_INVARIANT_BREACH\n"
        "fixture_id: advisory_actionable_no_signature\n"
        "breach_reasons: unexpected_authorization_without_signature_rule\n"
    ),
)

GATE_FAIL_RECORD = FailureRecord(
    failure_ref="audit_outputs/sample_gate.md",
    source_kind="gate",
    body=(
        "GATE_SUMMARY: blocking=2 warnings=0\n"
        "VERDICT: FAIL — resolve blocking deviations before advancing.\n"
        "BLOCKED_MISSING_CONTRACT for candidate #64\n"
    ),
)

PYTEST_FAIL_RECORD = FailureRecord(
    failure_ref="pytest_capture/test_sample_capture.txt",
    source_kind="pytest",
    body=(
        "FAILED tests/test_sample.py::test_example - AssertionError: expected True\n"
        "E       assert False == True\n"
    ),
)

DRIFT_RECORD = FailureRecord(
    failure_ref="scripts/mmi_contradiction_report_stdout.txt",
    source_kind="contradiction_report",
    body="REPORT_ONLY_FINDINGS\ncandidate_id: #52 contradicts scoreboard lifecycle\n",
)


def _repo_digest(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _agent(record: FailureRecord | None = None) -> FailureClassificationAgent:
    return FailureClassificationAgent(failure_record=record, repo_root=REPO_ROOT)


def _context() -> MissionContext:
    return MissionContext(
        tenant_id="tenant_failure_classification",
        inputs_digest="d" * 64,
    )


def test_failure_classification_agent_satisfies_agent_protocol():
    agent = _agent(AUTHORITY_PROBE_RECORD)
    assert isinstance(agent, Agent)
    assert agent.layer == 5
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.classify)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_evidence_traced_classification_carries_evidence_ref():
    result = classify_failure_record(AUTHORITY_PROBE_RECORD)
    assert result.kind == "success"
    item = result.classification
    assert item is not None
    assert item.evidence_ref
    assert "authority_invariant_breach" in item.evidence_ref.lower()


def test_t2_taxonomy_bound_no_invented_category():
    result = classify_failure_record(PYTEST_FAIL_RECORD)
    assert result.kind == "success"
    item = result.classification
    assert item is not None
    assert item.category in CATEGORY_SEVERITY


def test_t3_grounded_severity_authority_is_critical():
    result = classify_failure_record(AUTHORITY_PROBE_RECORD)
    item = result.classification
    assert item is not None
    assert item.category == "AUTHORITY_BOUNDARY"
    assert item.severity == "CRITICAL"


def test_t4_insufficient_input_emits_refusal_sentinel():
    result = classify_failure_record(
        FailureRecord(failure_ref="missing_body.txt", body="   ")
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.classification is None


def test_t5_no_response_language_in_output():
    for record in (AUTHORITY_PROBE_RECORD, GATE_FAIL_RECORD, PYTEST_FAIL_RECORD):
        result = classify_failure_record(record)
        assert result.kind == "success"
        rendered = format_classification(result.classification)
        lowered = rendered.lower()
        for marker in ("recommend", "should fix", "retry", "escalate", "route to"):
            assert marker not in lowered


def test_t6_no_remediation_or_reexecution(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("classifier must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("classifier must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    result = _agent(PYTEST_FAIL_RECORD).classify()
    assert result.kind == "success"


def test_t7_no_implementation_module_reads():
    result = classify_failure_record(
        FailureRecord(
            failure_ref="core/sandbox/failure_classification_agent.py",
            body="AUTHORITY_INVARIANT_BREACH detected",
        )
    )
    assert result.kind == "refusal"
    assert "implementation modules" in " ".join(result.gaps)


def test_t8_consumable_output_structure():
    result = classify_failure_record(DRIFT_RECORD)
    assert result.kind == "success"
    rendered = format_classification(result.classification)
    assert rendered.startswith("FAILURE_CLASSIFICATION\n")
    assert "failure_ref:" in rendered
    assert "category:" in rendered
    assert "severity:" in rendered
    assert "evidence_ref:" in rendered
    assert "rationale:" in rendered


def test_t9_zero_governance_state_writes():
    before = _repo_digest(SCOREBOARD_REL)
    result = _agent(GATE_FAIL_RECORD).classify()
    after = _repo_digest(SCOREBOARD_REL)
    assert result.kind == "success"
    assert before == after


def test_t10_authority_failure_critical_without_resolution_hint():
    result = classify_failure_record(AUTHORITY_PROBE_RECORD)
    item = result.classification
    assert item is not None
    assert item.severity == "CRITICAL"
    lowered = item.rationale.lower()
    assert "resolve" not in lowered
    assert "should" not in lowered


def test_contract_alignment_from_gate_record():
    result = classify_failure_record(GATE_FAIL_RECORD)
    item = result.classification
    assert item is not None
    assert item.category == "CONTRACT_ALIGNMENT"


def test_epistemic_drift_from_contradiction_record():
    result = classify_failure_record(DRIFT_RECORD)
    item = result.classification
    assert item is not None
    assert item.category == "EPISTEMIC_DRIFT"
    assert item.severity == "HIGH"


def test_default_registry_exclusion():
    registry = build_default_registry()
    assert fca.FAILURE_CLASSIFICATION_AGENT_ID not in registry


def test_analyze_raises_on_refusal():
    agent = FailureClassificationAgent(repo_root=REPO_ROOT)
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_context())


def test_classify_without_failure_record_refuses():
    result = FailureClassificationAgent(repo_root=REPO_ROOT).classify()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
