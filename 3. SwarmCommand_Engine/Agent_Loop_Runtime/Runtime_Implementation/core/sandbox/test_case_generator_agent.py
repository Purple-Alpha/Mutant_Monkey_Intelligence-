"""Test Case Generator governed-agent wrapper - swarm agent #61.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md`` (2026-06-21).
Reads one target §11-signed Agent Design Contract and emits deterministic
test cases traceable to ``CHECK:`` / required-test clauses only.

Scope / governance boundary (contract D1-D7, deliberate):
- D2 contract-only input: derives tests from target contract markdown only.
- D3 generate-only: no pytest execution, pass/fail judgment, or gate substitution.
- D4 traceability: every ``TEST_CASE`` maps to a contract clause.
- D5 refusal on thin input: ``INPUT_INSUFFICIENT_CANNOT_GENERATE``.
- D6 zero writes: no scoreboard/registry/state/governance mutation at Stage 1.
- D7 no autonomy / AUTH-5 blocked; not in ``build_default_registry``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.blackboard import GovernanceError

from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext

TEST_CASE_GENERATOR_AGENT_ID = "test_case_generator_001"
TEST_CASE_GENERATOR_LAYER = 5  # Challenge / Red-Team test-support
TEST_CASE_GENERATOR_AUTHORITY_LEVEL = 3  # Specialist Agent

REFUSAL_ENVELOPE = "INPUT_INSUFFICIENT_CANNOT_GENERATE"
CONTROL_MAPPING = "test_case_generator:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic test-case generation only; "
    "cases are not executed by #61."
)

CONTRACT_DIR_PREFIX = "4. Product_Roadmap/"
CONTRACT_FILENAME_MARKERS = ("Agent", "Design_Contract")
CONTRACT_SUFFIX = "_Agent_Design_Contract_Deep_Dive.md"

CHECK_LINE_RE = re.compile(r"^\s*-\s*CHECK:\s*(.+)$", re.MULTILINE)
REQUIRED_TEST_RE = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)

GenerationKind = Literal["success", "refusal"]
TestCaseType = Literal["functional", "edge", "negative"]


@dataclass(frozen=True)
class TestCase:
    id: str
    derives_from: str
    input: str
    expected: str
    type: TestCaseType


@dataclass(frozen=True)
class GenerationResult:
    kind: GenerationKind
    test_cases: tuple[TestCase, ...] = ()
    refusal: str | None = None
    gaps: tuple[str, ...] = ()


def _normalize_contract_rel(contract_rel: str) -> str:
    return contract_rel.replace("\\", "/").strip().lstrip("./")


def validate_contract_path(contract_rel: str) -> tuple[str, ...]:
    gaps: list[str] = []
    normalized = _normalize_contract_rel(contract_rel)
    if not normalized.startswith(CONTRACT_DIR_PREFIX):
        gaps.append("target contract path must resolve under 4. Product_Roadmap/")
    name = Path(normalized).name
    if CONTRACT_SUFFIX not in name:
        gaps.append("target contract filename must include Agent Design Contract suffix")
    for marker in CONTRACT_FILENAME_MARKERS:
        if marker not in name:
            gaps.append(f"target contract filename must include {marker!r}")
    if not normalized.endswith(".md"):
        gaps.append("target contract must be markdown (.md)")
    if ".." in Path(normalized).parts:
        gaps.append("target contract path must not contain parent traversal")
    return tuple(gaps)


def is_forbidden_read_path(path: Path) -> bool:
    normalized = str(path).replace("\\", "/")
    if normalized.endswith(".py") or normalized.endswith(".pyc"):
        return True
    forbidden_parts = (
        "/core/orchestrator/",
        "/Runtime_Implementation/core/",
        "/tests/",
    )
    return any(part in normalized for part in forbidden_parts)


def read_contract_markdown(contract_rel: str, repo_root: Path) -> str:
    path_gaps = validate_contract_path(contract_rel)
    if path_gaps:
        raise ValueError("; ".join(path_gaps))
    path = (repo_root / _normalize_contract_rel(contract_rel)).resolve()
    if is_forbidden_read_path(path):
        raise GovernanceError("TestCaseGeneratorAgent refuses to read implementation modules")
    if not path.is_file():
        raise FileNotFoundError(f"missing target contract: {contract_rel}")
    return path.read_text(encoding="utf-8")


def is_contract_signed(content: str) -> bool:
    for line in content.splitlines():
        if "**Status:**" not in line:
            continue
        upper = line.upper()
        if "UNSIGNED" in upper:
            return False
        if "SIGNED" in upper:
            return True
    return False


def extract_build_conditions_section(content: str) -> str | None:
    match = re.search(
        r"^##\s+BUILD CONDITIONS\s*$([\s\S]*?)(?=^##\s|\Z)",
        content,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def extract_required_tests_section(content: str) -> str | None:
    for pattern in (
        r"^##\s+§6 Required tests\s*$([\s\S]*?)(?=^##\s|\Z)",
        r"^##\s+Required tests\s*$([\s\S]*?)(?=^##\s|\Z)",
    ):
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1)
    return None


def parse_check_lines(section: str | None) -> tuple[str, ...]:
    if not section:
        return ()
    return tuple(match.group(1).strip() for match in CHECK_LINE_RE.finditer(section))


def parse_required_tests(section: str | None) -> tuple[str, ...]:
    if not section:
        return ()
    return tuple(match.group(1).strip() for match in REQUIRED_TEST_RE.finditer(section))


def format_insufficient_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "Target contract lacks checkable done-conditions required to derive tests.",
            "BOUNDARY:",
            "advisory only; no test cases emitted; no execution; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def _check_type(check_line: str) -> str:
    body = check_line
    if body.lower().startswith("check:"):
        body = body.split(":", 1)[1].strip()
    return body.split(":", 1)[0].strip() if ":" in body else body.strip()


def _test_case_type_for_check(check_line: str) -> TestCaseType:
    kind = _check_type(check_line)
    if kind == "sentinel_exact":
        return "negative"
    if kind in {"invariant_present", "format_exact"}:
        return "edge"
    return "functional"


def build_test_case_for_check(index: int, check_line: str) -> TestCase:
    check_kind = _check_type(check_line)
    derives = f"CHECK: {check_line}" if not check_line.lower().startswith("check:") else check_line
    return TestCase(
        id=f"tc_check_{index:03d}",
        derives_from=derives,
        input=f"contract_check_type={check_kind}; clause={check_line}",
        expected=f"target satisfies {derives}",
        type=_test_case_type_for_check(check_line),
    )


def build_test_case_for_requirement(index: int, requirement: str) -> TestCase:
    return TestCase(
        id=f"tc_req_{index:03d}",
        derives_from=requirement,
        input=f"required_test_index={index}",
        expected=f"target behavior satisfies required test: {requirement}",
        type="functional",
    )


def collect_generation_gaps(content: str, contract_rel: str) -> tuple[str, ...]:
    gaps: list[str] = list(validate_contract_path(contract_rel))
    if not is_contract_signed(content):
        gaps.append("target contract is not §11-signed")
    checks = parse_check_lines(extract_build_conditions_section(content))
    if not checks:
        gaps.append("target contract BUILD CONDITIONS has no CHECK: lines")
    requirements = parse_required_tests(extract_required_tests_section(content))
    if not requirements:
        gaps.append("target contract missing required-tests section items")
    return tuple(gaps)


def generate_test_cases_from_content(
    content: str,
    contract_rel: str,
) -> GenerationResult:
    gaps = collect_generation_gaps(content, contract_rel)
    if gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_insufficient_refusal(gaps),
            gaps=gaps,
        )

    checks = parse_check_lines(extract_build_conditions_section(content))
    requirements = parse_required_tests(extract_required_tests_section(content))
    cases: list[TestCase] = []
    for index, check_line in enumerate(checks, start=1):
        cases.append(build_test_case_for_check(index, check_line))
    for index, requirement in enumerate(requirements, start=1):
        cases.append(build_test_case_for_requirement(index, requirement))
    return GenerationResult(kind="success", test_cases=tuple(cases))


def generate_test_cases_from_contract(
    contract_rel: str,
    *,
    repo_root: Path | None = None,
) -> GenerationResult:
    root = repo_root or Path.cwd()
    path_gaps = validate_contract_path(contract_rel)
    if path_gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_insufficient_refusal(path_gaps),
            gaps=path_gaps,
        )
    try:
        content = read_contract_markdown(contract_rel, root)
    except FileNotFoundError:
        gaps = (f"target contract file not found: {contract_rel}",)
        return GenerationResult(
            kind="refusal",
            refusal=format_insufficient_refusal(gaps),
            gaps=gaps,
        )
    except (GovernanceError, ValueError) as exc:
        gaps = (str(exc),)
        return GenerationResult(
            kind="refusal",
            refusal=format_insufficient_refusal(gaps),
            gaps=gaps,
        )
    return generate_test_cases_from_content(content, contract_rel)


def format_test_case(case: TestCase) -> str:
    return "\n".join(
        [
            "TEST_CASE",
            f"id: {case.id}",
            f"derives_from: {case.derives_from}",
            f"input: {case.input}",
            f"expected: {case.expected}",
            f"type: {case.type}",
        ]
    )


class TestCaseGeneratorAgent:
    """Governed Layer 5 test-support generator — contract in, test cases out."""

    __test__ = False

    agent_id: str = TEST_CASE_GENERATOR_AGENT_ID
    layer: int = TEST_CASE_GENERATOR_LAYER
    authority_level: int = TEST_CASE_GENERATOR_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        target_contract_rel: str | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._target_contract_rel = target_contract_rel
        self._repo_root = repo_root

    def generate(
        self, target_contract_rel: str | None = None
    ) -> GenerationResult:
        rel = target_contract_rel or self._target_contract_rel
        if not rel:
            gaps = ("target_contract_rel is required",)
            return GenerationResult(
                kind="refusal",
                refusal=format_insufficient_refusal(gaps),
                gaps=gaps,
            )
        return generate_test_cases_from_contract(
            rel, repo_root=self._repo_root or Path.cwd()
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.generate()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        facts = tuple(
            f"generated_test_case:{case.id} derives_from={case.derives_from}"
            for case in result.test_cases
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=facts,
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None


__all__ = [
    "TEST_CASE_GENERATOR_AGENT_ID",
    "GenerationResult",
    "REFUSAL_ENVELOPE",
    "TestCase",
    "TestCaseGeneratorAgent",
    "build_test_case_for_check",
    "build_test_case_for_requirement",
    "collect_generation_gaps",
    "extract_build_conditions_section",
    "extract_required_tests_section",
    "format_insufficient_refusal",
    "format_test_case",
    "generate_test_cases_from_content",
    "generate_test_cases_from_contract",
    "is_contract_signed",
    "is_forbidden_read_path",
    "parse_check_lines",
    "parse_required_tests",
    "read_contract_markdown",
    "validate_contract_path",
]
