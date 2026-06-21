"""Adversarial Test governed-agent wrapper - swarm agent #63.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Adversarial_Test_Agent_Design_Contract_Deep_Dive.md`` (2026-06-21).
Reads one target §11-signed contract declared boundaries and emits
adversarial harness cases with correct-refusal ``expected`` outcomes only.

Scope / governance boundary (contract D1-D9, deliberate):
- D2 contract-boundaries-only input: derives cases from target contract only.
- D3 generate-only: no pytest execution, pass/fail judgment, or gate substitution.
- D4 traceability: every ``ADVERSARIAL_CASE`` maps to a declared boundary.
- D5 refusal on thin input: ``NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL``.
- D6 correct expected: never inverted success (target-fails-as-pass).
- D7 no weaponization: harness challenge cases only.
- D8 zero writes: no scoreboard/registry/state/governance mutation at Stage 1.
- D9 no autonomy / AUTH-5 blocked; not in ``build_default_registry``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.blackboard import GovernanceError
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext
from core.sandbox.test_case_generator_agent import (
    is_contract_signed,
    is_forbidden_read_path,
    read_contract_markdown,
    validate_contract_path,
)

ADVERSARIAL_TEST_AGENT_ID = "adversarial_test_001"
ADVERSARIAL_TEST_LAYER = 5
ADVERSARIAL_TEST_AUTHORITY_LEVEL = 3

REFUSAL_ENVELOPE = "NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL"
CONTROL_MAPPING = "adversarial_test:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic adversarial-case generation only; "
    "cases are harness inputs and are not executed by #63."
)

OUT_OF_SCOPE_BLOCK_RE = re.compile(
    r"###\s+Out of scope\s*\n(.*?)(?=\n---|\n##\s|\n###\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)
FAILURE_MODES_SECTION_RE = re.compile(
    r"^##\s+§5\s+Failure modes\s*$([\s\S]*?)(?=^##\s|\Z)",
    re.MULTILINE,
)
FAILURE_MODE_TITLE_RE = re.compile(
    r"^\s*-\s*\*\*(?P<title>[^*]+)\*\*\s*—",
    re.MULTILINE,
)
BULLET_LINE_RE = re.compile(r"^\s*-\s+(.+)$", re.MULTILINE)
EXPLICIT_NON_AUTHORITIES_RE = re.compile(
    r"\|\s*Explicit non-authorities\s*\|\s*(?P<cell>[^|]+)\|",
    re.IGNORECASE,
)
BOUNDARY_LINE_RE = re.compile(r"\*\*Boundary:\*\*\s*(?P<text>[^\n|]+)", re.IGNORECASE)

GenerationKind = Literal["success", "refusal"]
AdversarialCaseType = Literal[
    "boundary-violation",
    "forbidden-output",
    "scope-escape",
    "invalid-input-handling",
]

WEAPONIZATION_MARKERS = (
    "working exploit",
    "live-system attack",
    "retaliation payload",
    "honeypot deployment",
)


@dataclass(frozen=True)
class AdversarialCase:
    id: str
    attacks: str
    hostile_input: str
    attempted_violation: str
    expected: str
    type: AdversarialCaseType


@dataclass(frozen=True)
class GenerationResult:
    kind: GenerationKind
    adversarial_cases: tuple[AdversarialCase, ...] = ()
    refusal: str | None = None
    gaps: tuple[str, ...] = ()


def _normalize_boundary(text: str) -> str:
    return " ".join(text.split()).strip()


def _parse_out_of_scope_boundaries(content: str) -> tuple[str, ...]:
    boundaries: list[str] = []
    for block in OUT_OF_SCOPE_BLOCK_RE.finditer(content):
        for match in BULLET_LINE_RE.finditer(block.group(1)):
            line = _normalize_boundary(match.group(1))
            if line:
                boundaries.append(line)
    return tuple(boundaries)


def _parse_failure_mode_boundaries(content: str) -> tuple[str, ...]:
    section = FAILURE_MODES_SECTION_RE.search(content)
    if not section:
        return ()
    body = section.group(1)
    titles = [
        _normalize_boundary(match.group("title"))
        for match in FAILURE_MODE_TITLE_RE.finditer(body)
    ]
    if titles:
        return tuple(titles)
    return tuple(
        _normalize_boundary(match.group(1))
        for match in BULLET_LINE_RE.finditer(body)
        if match.group(1).strip()
    )


def _parse_explicit_non_authorities(content: str) -> tuple[str, ...]:
    match = EXPLICIT_NON_AUTHORITIES_RE.search(content)
    if match:
        parts = [
            _normalize_boundary(part)
            for part in match.group("cell").split(";")
            if _normalize_boundary(part)
        ]
        if parts:
            return tuple(parts)
    boundary = BOUNDARY_LINE_RE.search(content)
    if boundary:
        text = _normalize_boundary(boundary.group("text"))
        if text:
            return (text,)
    return ()


def parse_declared_boundaries(content: str) -> tuple[str, ...]:
    seen: dict[str, str] = {}
    for boundary in (
        *_parse_out_of_scope_boundaries(content),
        *_parse_failure_mode_boundaries(content),
        *_parse_explicit_non_authorities(content),
    ):
        key = boundary.lower()
        if key not in seen:
            seen[key] = boundary
    return tuple(seen.values())


def classify_case_type(boundary: str) -> AdversarialCaseType:
    lowered = boundary.lower()
    if any(
        token in lowered
        for token in (
            "unsigned",
            "missing",
            "thin input",
            "insufficient",
            "invalid input",
        )
    ):
        return "invalid-input-handling"
    if any(
        token in lowered
        for token in (
            "out of scope",
            "dispatch",
            "registry",
            "production",
            "scoreboard",
            "governance",
            "write",
            "autonom",
        )
    ):
        return "scope-escape"
    if any(
        token in lowered
        for token in (
            "pass/fail",
            "judge",
            "verdict",
            "score",
            "evaluation",
            "execute",
            "execution",
            "weapon",
            "exploit",
            "live-system",
            "retaliation",
            "honeypot",
        )
    ):
        return "forbidden-output"
    return "boundary-violation"


def format_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "Target contract lacks declared boundaries / failure modes "
            "required to derive adversarial cases.",
            "BOUNDARY:",
            "advisory only; no adversarial cases emitted; no execution; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def build_adversarial_case(index: int, boundary: str) -> AdversarialCase:
    attacks = boundary
    case_type = classify_case_type(boundary)
    return AdversarialCase(
        id=f"adv_{index:03d}",
        attacks=attacks,
        hostile_input=(
            "harness_case=contract_boundary_challenge; "
            f"boundary_ref={attacks[:160]}"
        ),
        attempted_violation=(
            f"hostile input attempts to induce contract violation: {attacks[:160]}"
        ),
        expected=(
            "refuse or safe-handle within contract; uphold declared boundary — "
            f"{attacks[:160]}"
        ),
        type=case_type,
    )


def collect_generation_gaps(content: str, contract_rel: str) -> tuple[str, ...]:
    gaps: list[str] = list(validate_contract_path(contract_rel))
    if not is_contract_signed(content):
        gaps.append("target contract is not §11-signed")
    if not _parse_out_of_scope_boundaries(content):
        gaps.append("target contract §1 Scope out-of-scope section has no boundary bullets")
    if not _parse_failure_mode_boundaries(content):
        gaps.append("target contract §5 Failure modes section has no entries")
    if not _parse_explicit_non_authorities(content):
        gaps.append(
            "target contract Agent Design Contract block lacks explicit non-authorities"
        )
    if not parse_declared_boundaries(content):
        gaps.append("target contract has no attackable declared boundaries")
    return tuple(gaps)


def generate_adversarial_cases_from_content(
    content: str,
    contract_rel: str,
) -> GenerationResult:
    gaps = collect_generation_gaps(content, contract_rel)
    if gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    boundaries = parse_declared_boundaries(content)
    cases = [
        build_adversarial_case(index, boundary)
        for index, boundary in enumerate(boundaries, start=1)
    ]
    return GenerationResult(kind="success", adversarial_cases=tuple(cases))


def generate_adversarial_cases_from_contract(
    contract_rel: str,
    *,
    repo_root: Path | None = None,
) -> GenerationResult:
    root = repo_root or Path.cwd()
    path_gaps = validate_contract_path(contract_rel)
    if path_gaps:
        return GenerationResult(
            kind="refusal",
            refusal=format_refusal(path_gaps),
            gaps=path_gaps,
        )
    try:
        content = read_contract_markdown(contract_rel, root)
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
    return generate_adversarial_cases_from_content(content, contract_rel)


def format_adversarial_case(case: AdversarialCase) -> str:
    return "\n".join(
        [
            "ADVERSARIAL_CASE",
            f"id: {case.id}",
            f"attacks: {case.attacks}",
            f"hostile_input: {case.hostile_input}",
            f"attempted_violation: {case.attempted_violation}",
            f"expected: {case.expected}",
            f"type: {case.type}",
        ]
    )


class AdversarialTestAgent:
    """Governed Layer 5 adversarial generator — contract boundaries in, cases out."""

    __test__ = False

    agent_id: str = ADVERSARIAL_TEST_AGENT_ID
    layer: int = ADVERSARIAL_TEST_LAYER
    authority_level: int = ADVERSARIAL_TEST_AUTHORITY_LEVEL
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
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        return generate_adversarial_cases_from_contract(
            rel, repo_root=self._repo_root or Path.cwd()
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.generate()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        facts = tuple(
            f"generated_adversarial_case:{case.id} attacks={case.attacks[:80]}"
            for case in result.adversarial_cases
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
    "ADVERSARIAL_TEST_AGENT_ID",
    "AdversarialCase",
    "AdversarialTestAgent",
    "GenerationResult",
    "REFUSAL_ENVELOPE",
    "WEAPONIZATION_MARKERS",
    "build_adversarial_case",
    "classify_case_type",
    "collect_generation_gaps",
    "format_adversarial_case",
    "format_refusal",
    "generate_adversarial_cases_from_content",
    "generate_adversarial_cases_from_contract",
    "parse_declared_boundaries",
]
