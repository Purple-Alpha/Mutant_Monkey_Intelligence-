"""Regression Test governed-agent wrapper - swarm agent #62.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Regression_Test_Agent_Design_Contract_Deep_Dive.md`` (2026-06-21).
Reads target §11-signed contract plus recorded prior-verified gate baseline
and emits regression cases traceable to real baseline evidence only.

Scope / governance boundary (contract D1-D8, deliberate):
- D2 recorded baseline only: gate artifacts / MMI records — never current code.
- D3 generate-only: no pytest execution, pass/fail judgment, or regression verdict.
- D4 traceability: every ``REGRESSION_CASE`` maps to a ``baseline_ref``.
- D5 refusal on missing baseline: ``NO_BASELINE_CANNOT_GENERATE_REGRESSION``.
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
from core.sandbox.test_case_generator_agent import (
    extract_build_conditions_section,
    is_contract_signed,
    is_forbidden_read_path,
    parse_check_lines,
    read_contract_markdown,
    validate_contract_path,
)

REGRESSION_TEST_AGENT_ID = "regression_test_001"
REGRESSION_TEST_LAYER = 5
REGRESSION_TEST_AUTHORITY_LEVEL = 3

REFUSAL_ENVELOPE = "NO_BASELINE_CANNOT_GENERATE_REGRESSION"
CONTROL_MAPPING = "regression_test:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic regression-case generation only; "
    "cases are not executed by #62 and carry no regression verdict."
)

BASELINE_DIR_PREFIX = "audit_outputs/"
MMI_DECISION_LOG_REL = "mmi/MMI_DECISION_LOG.md"

GATE_SUMMARY_RE = re.compile(
    r"GATE_SUMMARY:\s*blocking=(\d+)\s+warnings=(\d+)", re.IGNORECASE
)
GATE_HEADER_BLOCKING_RE = re.compile(
    r"\*\*Blocking deviations:\*\*\s*`(\d+)`", re.IGNORECASE
)
GATE_HEADER_WARNINGS_RE = re.compile(
    r"\*\*Warnings:\*\*\s*`(\d+)`", re.IGNORECASE
)

GenerationKind = Literal["success", "refusal"]
RegressionCaseType = Literal["behavior-preservation", "invariant-hold"]


@dataclass(frozen=True)
class RegressionCase:
    id: str
    protects: str
    baseline_ref: str
    input: str
    expected: str
    type: RegressionCaseType


@dataclass(frozen=True)
class GenerationResult:
    kind: GenerationKind
    regression_cases: tuple[RegressionCase, ...] = ()
    refusal: str | None = None
    gaps: tuple[str, ...] = ()


def _normalize_rel(path_rel: str) -> str:
    return path_rel.replace("\\", "/").strip().lstrip("./")


def validate_baseline_path(baseline_rel: str) -> tuple[str, ...]:
    gaps: list[str] = []
    normalized = _normalize_rel(baseline_rel)
    if normalized == MMI_DECISION_LOG_REL:
        return ()
    if not normalized.startswith(BASELINE_DIR_PREFIX):
        gaps.append(
            "baseline path must resolve under audit_outputs/ or mmi/MMI_DECISION_LOG.md"
        )
    if not normalized.endswith(".md"):
        gaps.append("baseline artifact must be markdown (.md)")
    if ".." in Path(normalized).parts:
        gaps.append("baseline path must not contain parent traversal")
    return tuple(gaps)


def read_baseline_markdown(baseline_rel: str, repo_root: Path) -> str:
    path_gaps = validate_baseline_path(baseline_rel)
    if path_gaps:
        raise ValueError("; ".join(path_gaps))
    path = (repo_root / _normalize_rel(baseline_rel)).resolve()
    if is_forbidden_read_path(path):
        raise GovernanceError(
            "RegressionTestAgent refuses to read implementation modules as baseline"
        )
    if not path.is_file():
        raise FileNotFoundError(f"missing baseline artifact: {baseline_rel}")
    return path.read_text(encoding="utf-8")


def parse_gate_counts(content: str) -> tuple[int, int] | None:
    summary = GATE_SUMMARY_RE.search(content)
    if summary:
        return int(summary.group(1)), int(summary.group(2))
    blocking = GATE_HEADER_BLOCKING_RE.search(content)
    warnings = GATE_HEADER_WARNINGS_RE.search(content)
    if blocking and warnings:
        return int(blocking.group(1)), int(warnings.group(2))
    return None


def is_clean_gate_baseline(content: str) -> bool:
    counts = parse_gate_counts(content)
    return counts == (0, 0)


def format_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "No recorded prior-verified behavior exists to protect; "
            "regression cases cannot be invented.",
            "BOUNDARY:",
            "advisory only; no regression cases emitted; no execution; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def _case_type_for_check(check_line: str) -> RegressionCaseType:
    body = check_line.lower()
    if "invariant_present" in body:
        return "invariant-hold"
    return "behavior-preservation"


def build_regression_case_for_check(
    index: int,
    check_line: str,
    *,
    baseline_ref: str,
) -> RegressionCase:
    protects = (
        f"CHECK: {check_line}"
        if not check_line.lower().startswith("check:")
        else check_line
    )
    return RegressionCase(
        id=f"rc_check_{index:03d}",
        protects=protects,
        baseline_ref=baseline_ref,
        input=f"prior_verified_behavior={protects}",
        expected=f"behavior continues to hold per {baseline_ref}",
        type=_case_type_for_check(check_line),
    )


def collect_generation_gaps(
    contract_content: str,
    contract_rel: str,
    baseline_content: str | None,
    baseline_rel: str,
) -> tuple[str, ...]:
    gaps: list[str] = list(validate_contract_path(contract_rel))
    gaps.extend(validate_baseline_path(baseline_rel))
    if not is_contract_signed(contract_content):
        gaps.append("target contract is not §11-signed")
    checks = parse_check_lines(extract_build_conditions_section(contract_content))
    if not checks:
        gaps.append("target contract BUILD CONDITIONS has no CHECK: lines")
    if baseline_content is None:
        gaps.append(f"baseline artifact not found: {baseline_rel}")
    elif not is_clean_gate_baseline(baseline_content):
        gaps.append("baseline gate artifact is not clean 0/0")
    return tuple(gaps)


def generate_regression_cases_from_inputs(
    contract_content: str,
    contract_rel: str,
    baseline_content: str,
    baseline_rel: str,
) -> GenerationResult:
    gaps = collect_generation_gaps(
        contract_content, contract_rel, baseline_content, baseline_rel
    )
    if gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    checks = parse_check_lines(extract_build_conditions_section(contract_content))
    cases = [
        build_regression_case_for_check(index, check_line, baseline_ref=baseline_rel)
        for index, check_line in enumerate(checks, start=1)
    ]
    return GenerationResult(kind="success", regression_cases=tuple(cases))


def generate_regression_cases(
    contract_rel: str,
    baseline_rel: str,
    *,
    repo_root: Path | None = None,
) -> GenerationResult:
    root = repo_root or Path.cwd()
    path_gaps = tuple(validate_contract_path(contract_rel)) + tuple(
        validate_baseline_path(baseline_rel)
    )
    if path_gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(path_gaps),
            gaps=path_gaps,
        )

    baseline_content: str | None
    try:
        baseline_content = read_baseline_markdown(baseline_rel, root)
    except FileNotFoundError:
        gaps = (f"baseline artifact not found: {baseline_rel}",)
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )
    except (GovernanceError, ValueError) as exc:
        gaps = (str(exc),)
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    try:
        contract_content = read_contract_markdown(contract_rel, root)
    except FileNotFoundError:
        gaps = (f"target contract file not found: {contract_rel}",)
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )
    except (GovernanceError, ValueError) as exc:
        gaps = (str(exc),)
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    return generate_regression_cases_from_inputs(
        contract_content, contract_rel, baseline_content, baseline_rel
    )


def format_regression_case(case: RegressionCase) -> str:
    return "\n".join(
        [
            "REGRESSION_CASE",
            f"id: {case.id}",
            f"protects: {case.protects}",
            f"baseline_ref: {case.baseline_ref}",
            f"input: {case.input}",
            f"expected: {case.expected}",
            f"type: {case.type}",
        ]
    )


class RegressionTestAgent:
    """Governed Layer 5 regression generator — recorded baseline in, cases out."""

    __test__ = False

    agent_id: str = REGRESSION_TEST_AGENT_ID
    layer: int = REGRESSION_TEST_LAYER
    authority_level: int = REGRESSION_TEST_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        target_contract_rel: str | None = None,
        baseline_rel: str | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._target_contract_rel = target_contract_rel
        self._baseline_rel = baseline_rel
        self._repo_root = repo_root

    def generate(
        self,
        target_contract_rel: str | None = None,
        baseline_rel: str | None = None,
    ) -> GenerationResult:
        contract_rel = target_contract_rel or self._target_contract_rel
        baseline = baseline_rel or self._baseline_rel
        if not contract_rel or not baseline:
            gaps = ("target_contract_rel and baseline_rel are required",)
            return GenerationResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        return generate_regression_cases(
            contract_rel,
            baseline,
            repo_root=self._repo_root or Path.cwd(),
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.generate()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        facts = tuple(
            f"generated_regression_case:{case.id} baseline_ref={case.baseline_ref}"
            for case in result.regression_cases
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
    "REGRESSION_TEST_AGENT_ID",
    "GenerationResult",
    "REFUSAL_ENVELOPE",
    "RegressionCase",
    "RegressionTestAgent",
    "build_regression_case_for_check",
    "collect_generation_gaps",
    "format_refusal",
    "format_regression_case",
    "generate_regression_cases",
    "generate_regression_cases_from_inputs",
    "is_clean_gate_baseline",
    "parse_gate_counts",
    "read_baseline_markdown",
    "validate_baseline_path",
]
