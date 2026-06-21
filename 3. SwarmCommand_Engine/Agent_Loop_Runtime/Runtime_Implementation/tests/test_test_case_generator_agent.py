"""Evidence Stage 1 proof for swarm agent #61 Test Case Generator.

Authorized by the §11-SIGNED Test Case Generator Agent Design Contract
(2026-06-21). Synthetic tests prove contract-only traceable generation,
refusal on thin input, no execution path, consumable output structure,
registry-default exclusion, and no governance/state mutation at Stage 1.
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
from core.sandbox import test_case_generator_agent as tcg
from core.sandbox.test_case_generator_agent import (
    REFUSAL_ENVELOPE,
    TestCaseGeneratorAgent,
    format_test_case,
    generate_test_cases_from_content,
    generate_test_cases_from_contract,
    parse_check_lines,
    read_contract_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PLAIN_ENGLISH_CONTRACT = (
    "4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md"
)
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"


def _repo_digest(rel: str) -> str:
    path = REPO_ROOT / rel
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _agent(contract_rel: str | None = None) -> TestCaseGeneratorAgent:
    return TestCaseGeneratorAgent(
        target_contract_rel=contract_rel,
        repo_root=REPO_ROOT,
    )


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_test_case_generator", inputs_digest="a" * 64)


def _minimal_signed_contract(*, checks: str, requirements: str) -> str:
    return f"""# Minimal Agent Design Contract

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol

## BUILD CONDITIONS

{checks}

## §6 Required tests

{requirements}
"""


def test_test_case_generator_agent_satisfies_agent_protocol():
    agent = _agent(PLAIN_ENGLISH_CONTRACT)
    assert isinstance(agent, Agent)
    assert agent.layer == 5
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.generate)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_traceable_generation_maps_to_named_contract_clauses():
    result = generate_test_cases_from_contract(
        PLAIN_ENGLISH_CONTRACT, repo_root=REPO_ROOT
    )
    assert result.kind == "success"
    content = read_contract_markdown(PLAIN_ENGLISH_CONTRACT, REPO_ROOT)
    check_lines = parse_check_lines(
        tcg.extract_build_conditions_section(content)
    )
    req_lines = tcg.parse_required_tests(
        tcg.extract_required_tests_section(content)
    )
    allowed = {f"CHECK: {line}" for line in check_lines}
    allowed.update(req_lines)
    for case in result.test_cases:
        assert case.derives_from in allowed or case.derives_from.startswith("CHECK:")


def test_t2_no_invention_beyond_contract_clauses():
    content = _minimal_signed_contract(
        checks="- CHECK: sentinel_exact: INPUT_INSUFFICIENT_CANNOT_EXPLAIN",
        requirements="1. Missing input emits refusal only.",
    )
    result = generate_test_cases_from_content(
        content, "4. Product_Roadmap/Minimal_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "success"
    assert len(result.test_cases) == 2
    derives = {case.derives_from for case in result.test_cases}
    assert derives == {
        "CHECK: sentinel_exact: INPUT_INSUFFICIENT_CANNOT_EXPLAIN",
        "Missing input emits refusal only.",
    }


def test_t3_contract_only_never_reads_implementation_modules(monkeypatch):
    read_paths: list[str] = []

    original_read_text = Path.read_text

    def _tracking_read_text(self, *args, **kwargs):
        read_paths.append(str(self))
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _tracking_read_text)
    result = generate_test_cases_from_contract(
        PLAIN_ENGLISH_CONTRACT, repo_root=REPO_ROOT
    )
    assert result.kind == "success"
    assert read_paths
    for path in read_paths:
        normalized = path.replace("\\", "/")
        assert normalized.endswith(".md")
        assert "Agent_Design_Contract" in normalized
        assert "/core/orchestrator/" not in normalized
        assert not normalized.endswith(".py")


def test_t4_insufficient_input_emits_refusal_sentinel():
    unsigned = """# Draft

**Status:** DRAFT — UNSIGNED

## BUILD CONDITIONS

- CHECK: file_exists: foo.md

## §6 Required tests

1. One test.
"""
    result = generate_test_cases_from_content(
        unsigned, "4. Product_Roadmap/Unsigned_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.test_cases == ()
    assert "§11-signed" in result.gaps[0]

    missing_checks = """# Signed

**Status:** §11 SIGNED

## BUILD CONDITIONS

(none)

## §6 Required tests

1. Only requirement.
"""
    result2 = generate_test_cases_from_content(
        missing_checks,
        "4. Product_Roadmap/Thin_Agent_Design_Contract_Deep_Dive.md",
    )
    assert result2.kind == "refusal"
    assert "no CHECK: lines" in " ".join(result2.gaps)


def test_t5_no_execution_subprocess_or_network(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("test case generator must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("test case generator must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    result = _agent(PLAIN_ENGLISH_CONTRACT).generate()
    assert result.kind == "success"


def test_t6_consumable_output_structure_for_pytest_harness():
    result = _agent(PLAIN_ENGLISH_CONTRACT).generate()
    assert result.kind == "success"
    for case in result.test_cases:
        rendered = format_test_case(case)
        assert rendered.startswith("TEST_CASE\n")
        assert f"id: {case.id}" in rendered
        assert "derives_from:" in rendered
        assert "input:" in rendered
        assert "expected:" in rendered
        assert f"type: {case.type}" in rendered
        assert case.type in {"functional", "edge", "negative"}


def test_t7_zero_governance_state_writes():
    before = _repo_digest(SCOREBOARD_REL)
    result = _agent(PLAIN_ENGLISH_CONTRACT).generate()
    after = _repo_digest(SCOREBOARD_REL)
    assert result.kind == "success"
    assert before == after


def test_t8_each_check_line_yields_at_least_one_case():
    content = read_contract_markdown(PLAIN_ENGLISH_CONTRACT, REPO_ROOT)
    check_lines = parse_check_lines(tcg.extract_build_conditions_section(content))
    result = generate_test_cases_from_content(content, PLAIN_ENGLISH_CONTRACT)
    assert result.kind == "success"
    check_cases = [c for c in result.test_cases if c.id.startswith("tc_check_")]
    assert len(check_cases) == len(check_lines)


def test_refusal_on_invalid_contract_path():
    result = generate_test_cases_from_contract(
        "core/orchestrator/plain_english_explanation_agent.py",
        repo_root=REPO_ROOT,
    )
    assert result.kind == "refusal"
    assert result.test_cases == ()


def test_refusal_on_missing_contract_file():
    result = generate_test_cases_from_contract(
        "4. Product_Roadmap/Missing_Agent_Design_Contract_Deep_Dive.md",
        repo_root=REPO_ROOT,
    )
    assert result.kind == "refusal"
    assert "not found" in " ".join(result.gaps)


def test_default_registry_exclusion():
    registry = build_default_registry()
    assert tcg.TEST_CASE_GENERATOR_AGENT_ID not in registry


def test_analyze_raises_on_refusal():
    agent = TestCaseGeneratorAgent(repo_root=REPO_ROOT)
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_context())


def test_sentinel_exact_maps_to_negative_case_type():
    content = _minimal_signed_contract(
        checks="- CHECK: sentinel_exact: INPUT_INSUFFICIENT_CANNOT_GENERATE",
        requirements="1. Refusal only when thin.",
    )
    result = generate_test_cases_from_content(
        content, "4. Product_Roadmap/Sentinel_Agent_Design_Contract_Deep_Dive.md"
    )
    negative = [c for c in result.test_cases if c.type == "negative"]
    assert len(negative) == 1
    assert "sentinel_exact" in negative[0].derives_from


def test_forbidden_read_path_helper_blocks_implementation_modules():
    assert tcg.is_forbidden_read_path(
        Path(
            "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
            "core/orchestrator/plain_english_explanation_agent.py"
        )
    )
    assert not tcg.is_forbidden_read_path(
        Path("4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md")
    )


def test_generate_without_target_contract_ref_refuses():
    result = TestCaseGeneratorAgent(repo_root=REPO_ROOT).generate()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
