"""Evidence Stage 1 proof for swarm agent #62 Regression Test.

Authorized by the §11-SIGNED Regression Test Agent Design Contract
(2026-06-21). Synthetic tests prove baseline-traced generation, refusal on
missing baseline, no current-code baseline, no execution or regression verdict,
consumable output structure, registry-default exclusion, and no governance
writes at Stage 1.
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
from core.sandbox import regression_test_agent as rta
from core.sandbox.regression_test_agent import (
    REFUSAL_ENVELOPE,
    RegressionTestAgent,
    format_regression_case,
    generate_regression_cases,
    generate_regression_cases_from_inputs,
    read_baseline_markdown,
)
from core.sandbox.test_case_generator_agent import (
    extract_build_conditions_section,
    parse_check_lines,
    read_contract_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
TCG_CONTRACT = (
    "4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md"
)
TCG_BASELINE = "audit_outputs/test_case_generator_20260621T080345Z.md"
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"


def _repo_digest(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _agent(
    contract_rel: str | None = None,
    baseline_rel: str | None = None,
) -> RegressionTestAgent:
    return RegressionTestAgent(
        target_contract_rel=contract_rel,
        baseline_rel=baseline_rel,
        repo_root=REPO_ROOT,
    )


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_regression_test", inputs_digest="b" * 64)


def _minimal_signed_contract(checks: str) -> str:
    return f"""# Minimal Agent Design Contract

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol

## BUILD CONDITIONS

{checks}
"""


def _clean_baseline() -> str:
    return """# Grok Completion Audit — sample

- **Blocking deviations:** `0`
- **Warnings:** `0`

GATE_SUMMARY: blocking=0 warnings=0
"""


def test_regression_test_agent_satisfies_agent_protocol():
    agent = _agent(TCG_CONTRACT, TCG_BASELINE)
    assert isinstance(agent, Agent)
    assert agent.layer == 5
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.generate)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_baseline_traced_every_case_has_baseline_ref():
    result = generate_regression_cases(TCG_CONTRACT, TCG_BASELINE, repo_root=REPO_ROOT)
    assert result.kind == "success"
    for case in result.regression_cases:
        assert case.baseline_ref == TCG_BASELINE
        assert case.baseline_ref.startswith("audit_outputs/")


def test_t2_no_invented_baseline_refuses():
    result = generate_regression_cases(
        TCG_CONTRACT,
        "audit_outputs/missing_baseline_20260101T000000Z.md",
        repo_root=REPO_ROOT,
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.regression_cases == ()


def test_t2b_non_clean_gate_refuses():
    contract = _minimal_signed_contract(
        checks="- CHECK: sentinel_exact: NO_BASELINE_CANNOT_GENERATE_REGRESSION"
    )
    dirty = """# Grok Completion Audit

GATE_SUMMARY: blocking=1 warnings=0
"""
    result = generate_regression_cases_from_inputs(
        contract,
        "4. Product_Roadmap/Minimal_Agent_Design_Contract_Deep_Dive.md",
        dirty,
        "audit_outputs/dirty_gate.md",
    )
    assert result.kind == "refusal"
    assert "not clean 0/0" in " ".join(result.gaps)


def test_t3_not_self_certifying_never_reads_implementation_baseline(monkeypatch):
    read_paths: list[str] = []
    original_read_text = Path.read_text

    def _tracking_read_text(self, *args, **kwargs):
        read_paths.append(str(self))
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _tracking_read_text)
    result = generate_regression_cases(TCG_CONTRACT, TCG_BASELINE, repo_root=REPO_ROOT)
    assert result.kind == "success"
    for path in read_paths:
        normalized = path.replace("\\", "/")
        assert not normalized.endswith(".py")
        assert "/core/orchestrator/" not in normalized
        assert "/core/sandbox/test_case_generator_agent.py" not in normalized


def test_t4_no_execution_subprocess_or_network(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("regression wrapper must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("regression wrapper must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    result = _agent(TCG_CONTRACT, TCG_BASELINE).generate()
    assert result.kind == "success"


def test_t5_no_regression_verdict_in_output():
    result = _agent(TCG_CONTRACT, TCG_BASELINE).generate()
    assert result.kind == "success"
    rendered = "\n".join(format_regression_case(c) for c in result.regression_cases)
    lowered = rendered.lower()
    assert "regression confirmed" not in lowered
    assert "intended change" not in lowered
    assert "verdict" not in lowered


def test_t6_consumable_output_structure():
    result = _agent(TCG_CONTRACT, TCG_BASELINE).generate()
    assert result.kind == "success"
    for case in result.regression_cases:
        rendered = format_regression_case(case)
        assert rendered.startswith("REGRESSION_CASE\n")
        assert f"id: {case.id}" in rendered
        assert "protects:" in rendered
        assert "baseline_ref:" in rendered
        assert case.type in {"behavior-preservation", "invariant-hold"}


def test_t7_zero_governance_state_writes():
    before = _repo_digest(SCOREBOARD_REL)
    result = _agent(TCG_CONTRACT, TCG_BASELINE).generate()
    after = _repo_digest(SCOREBOARD_REL)
    assert result.kind == "success"
    assert before == after


def test_t8_each_check_line_yields_regression_case():
    contract_content = read_contract_markdown(TCG_CONTRACT, REPO_ROOT)
    baseline_content = read_baseline_markdown(TCG_BASELINE, REPO_ROOT)
    checks = parse_check_lines(extract_build_conditions_section(contract_content))
    result = generate_regression_cases_from_inputs(
        contract_content,
        TCG_CONTRACT,
        baseline_content,
        TCG_BASELINE,
    )
    assert result.kind == "success"
    assert len(result.regression_cases) == len(checks)


def test_refusal_on_unsigned_contract():
    unsigned = """# Draft

**Status:** DRAFT — UNSIGNED

## BUILD CONDITIONS

- CHECK: consumer_named: complete_gate.py
"""
    result = generate_regression_cases_from_inputs(
        unsigned,
        "4. Product_Roadmap/Unsigned_Agent_Design_Contract_Deep_Dive.md",
        _clean_baseline(),
        "audit_outputs/clean_gate.md",
    )
    assert result.kind == "refusal"
    assert "§11-signed" in " ".join(result.gaps)


def test_refusal_on_implementation_baseline_path():
    result = generate_regression_cases(
        TCG_CONTRACT,
        "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
        "core/sandbox/test_case_generator_agent.py",
        repo_root=REPO_ROOT,
    )
    assert result.kind == "refusal"


def test_default_registry_exclusion():
    registry = build_default_registry()
    assert rta.REGRESSION_TEST_AGENT_ID not in registry


def test_analyze_raises_on_refusal():
    agent = RegressionTestAgent(repo_root=REPO_ROOT)
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_context())


def test_generate_without_inputs_refuses():
    result = RegressionTestAgent(repo_root=REPO_ROOT).generate()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")


def test_invariant_check_maps_to_invariant_hold_type():
    contract = _minimal_signed_contract(
        checks="- CHECK: invariant_present: every case traces to baseline"
    )
    result = generate_regression_cases_from_inputs(
        contract,
        "4. Product_Roadmap/Invariant_Agent_Design_Contract_Deep_Dive.md",
        _clean_baseline(),
        "audit_outputs/clean_gate.md",
    )
    assert result.kind == "success"
    assert all(c.type == "invariant-hold" for c in result.regression_cases)
