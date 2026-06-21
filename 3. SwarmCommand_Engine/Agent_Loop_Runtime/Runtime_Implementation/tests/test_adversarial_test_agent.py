"""Evidence Stage 1 proof for swarm agent #63 Adversarial Test.

Authorized by the §11-SIGNED Adversarial Test Agent Design Contract
(2026-06-21). Synthetic tests prove boundary-traced generation, correct-expected
outcomes, contract-only input, refusal on missing boundaries, no execution,
no weaponization path, consumable output structure, registry-default exclusion,
and no governance/state mutation at Stage 1.
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
from core.sandbox import adversarial_test_agent as ata
from core.sandbox.adversarial_test_agent import (
    REFUSAL_ENVELOPE,
    WEAPONIZATION_MARKERS,
    AdversarialTestAgent,
    format_adversarial_case,
    generate_adversarial_cases_from_content,
    generate_adversarial_cases_from_contract,
    parse_declared_boundaries,
)
from core.sandbox.test_case_generator_agent import read_contract_markdown

REPO_ROOT = Path(__file__).resolve().parents[4]
TCG_CONTRACT = (
    "4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md"
)
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"


def _repo_digest(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _agent(contract_rel: str | None = None) -> AdversarialTestAgent:
    return AdversarialTestAgent(
        target_contract_rel=contract_rel,
        repo_root=REPO_ROOT,
    )


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_adversarial_test", inputs_digest="c" * 64)


def _minimal_signed_contract(
    *,
    out_of_scope: str,
    failure_modes: str,
    non_authorities: str = "No execution; no pass/fail judgment; no writes",
) -> str:
    return f"""# Minimal Agent Design Contract

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol

## Agent Design Contract block

| Explicit non-authorities | {non_authorities} |

## §1 Scope

### Out of scope
{out_of_scope}

## §5 Failure modes

{failure_modes}
"""


def test_adversarial_test_agent_satisfies_agent_protocol():
    agent = _agent(TCG_CONTRACT)
    assert isinstance(agent, Agent)
    assert agent.layer == 5
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.generate)
    assert inspect.ismethod(agent.analyze)
    assert inspect.ismethod(agent.challenge)


def test_t1_boundary_traced_every_case_maps_to_declared_boundary():
    content = read_contract_markdown(TCG_CONTRACT, REPO_ROOT)
    allowed = set(parse_declared_boundaries(content))
    result = generate_adversarial_cases_from_contract(TCG_CONTRACT, repo_root=REPO_ROOT)
    assert result.kind == "success"
    assert result.adversarial_cases
    for case in result.adversarial_cases:
        assert case.attacks in allowed


def test_t2_correct_expected_is_refusal_not_target_failure():
    result = _agent(TCG_CONTRACT).generate()
    assert result.kind == "success"
    for case in result.adversarial_cases:
        assert case.expected.startswith("refuse or safe-handle")
        assert "target fails" not in case.expected.lower()
        assert "target failure" not in case.expected.lower()


def test_t3_contract_only_never_reads_implementation_modules(monkeypatch):
    read_paths: list[str] = []
    original_read_text = Path.read_text

    def _tracking_read_text(self, *args, **kwargs):
        read_paths.append(str(self))
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _tracking_read_text)
    result = generate_adversarial_cases_from_contract(TCG_CONTRACT, repo_root=REPO_ROOT)
    assert result.kind == "success"
    for path in read_paths:
        normalized = path.replace("\\", "/")
        assert normalized.endswith(".md")
        assert not normalized.endswith(".py")
        assert "/core/orchestrator/" not in normalized


def test_t4_no_boundaries_emits_refusal_sentinel():
    thin = """# Thin

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol

## §1 Scope

### In scope
- only in scope
"""
    result = generate_adversarial_cases_from_content(
        thin, "4. Product_Roadmap/Thin_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")
    assert result.adversarial_cases == ()


def test_t5_no_execution_subprocess_or_network(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("adversarial wrapper must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("adversarial wrapper must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    result = _agent(TCG_CONTRACT).generate()
    assert result.kind == "success"


def test_t6_no_weaponization_markers_in_output():
    result = _agent(TCG_CONTRACT).generate()
    assert result.kind == "success"
    rendered = "\n".join(format_adversarial_case(c) for c in result.adversarial_cases)
    lowered = rendered.lower()
    for marker in WEAPONIZATION_MARKERS:
        assert marker not in lowered
    assert "deploy exploit against production" not in lowered


def test_t7_consumable_output_structure():
    result = _agent(TCG_CONTRACT).generate()
    assert result.kind == "success"
    for case in result.adversarial_cases:
        rendered = format_adversarial_case(case)
        assert rendered.startswith("ADVERSARIAL_CASE\n")
        assert f"id: {case.id}" in rendered
        assert "attacks:" in rendered
        assert "hostile_input:" in rendered
        assert "attempted_violation:" in rendered
        assert "expected:" in rendered
        assert case.type in {
            "boundary-violation",
            "forbidden-output",
            "scope-escape",
            "invalid-input-handling",
        }


def test_t8_zero_governance_state_writes():
    before = _repo_digest(SCOREBOARD_REL)
    result = _agent(TCG_CONTRACT).generate()
    after = _repo_digest(SCOREBOARD_REL)
    assert result.kind == "success"
    assert before == after


def test_t9_each_failure_mode_yields_adversarial_case():
    content = _minimal_signed_contract(
        out_of_scope="- Running tests.",
        failure_modes="- **Execution creep** — agent runs tests it generates.",
    )
    result = generate_adversarial_cases_from_content(
        content, "4. Product_Roadmap/Minimal_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "success"
    attacks = {case.attacks for case in result.adversarial_cases}
    assert "Execution creep" in attacks


def test_refusal_on_unsigned_contract():
    unsigned = """# Draft

**Status:** DRAFT — UNSIGNED

## Agent Design Contract block

| Explicit non-authorities | No execution |

## §1 Scope

### Out of scope
- No writes.

## §5 Failure modes

- **Drift** — bad.
"""
    result = generate_adversarial_cases_from_content(
        unsigned, "4. Product_Roadmap/Unsigned_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "refusal"
    assert "§11-signed" in " ".join(result.gaps)


def test_refusal_on_invalid_contract_path():
    result = generate_adversarial_cases_from_contract(
        "core/sandbox/test_case_generator_agent.py",
        repo_root=REPO_ROOT,
    )
    assert result.kind == "refusal"
    assert result.adversarial_cases == ()


def test_default_registry_exclusion():
    registry = build_default_registry()
    assert ata.ADVERSARIAL_TEST_AGENT_ID not in registry


def test_analyze_raises_on_refusal():
    agent = AdversarialTestAgent(repo_root=REPO_ROOT)
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_context())


def test_generate_without_target_contract_refuses():
    result = AdversarialTestAgent(repo_root=REPO_ROOT).generate()
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in (result.refusal or "")


def test_scope_escape_type_for_registry_boundary():
    content = _minimal_signed_contract(
        out_of_scope="- Registering the agent in build_default_registry.",
        failure_modes="- **Registry creep** — adds default dispatch.",
    )
    result = generate_adversarial_cases_from_content(
        content, "4. Product_Roadmap/Registry_Agent_Design_Contract_Deep_Dive.md"
    )
    assert result.kind == "success"
    types = {case.type for case in result.adversarial_cases}
    assert "scope-escape" in types
