#!/usr/bin/env python3
"""MMI Estimator — Mode A read-only candidate scoring (stdout only).

Scores incomplete build candidates from a fixed manifest. Does not write files.
Does not import or subprocess the MMI dispatcher.

Weight authority: Estimator weights are owner policy locked by
``mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md`` §10.1 / §11 (MMI-DEC-038).
``WEIGHTS`` below must match the signed record. Weight changes require
operator instruction plus contract revision or MMI-DEC entry — never silent
code-only tuning.

NULL recalibration (MMI-DEC-043): measured zero stays numeric; missing or
unavailable factor sources emit ``NULL(no_data: reason)`` and are excluded from
``total_measured_score``.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ENVELOPE_SCORED = "SCORED_CANDIDATES"
ENVELOPE_SCORED_FEEDSTOCK = "SCORED_FEEDSTOCK"
ENVELOPE_INCOMPLETE = "STATE_INCOMPLETE_CANNOT_SCORE"
ENVELOPE_NO_BUILDABLE = "NO_BUILDABLE_CANDIDATES"
ENVELOPE_BUILDABILITY_EXCLUSIONS = "BUILDABILITY_EXCLUSIONS"
BOR_PATH_REL = "mmi/BLUEPRINT_OF_RECORD.md"

FEEDSTOCK_ENTRY_RE = re.compile(
    r"^feedstock_entry:\s*"
    r"priority=(?P<priority>hold|\d+)\s+"
    r"candidate_id=(?P<candidate_id>#\d+[A-Z]?)\s+"
    r"lane_type=(?P<lane_type>[A-Z_]+)\s+"
    r"name=(?P<name>.+?)"
    r"(?:\s+hold_unless_matt=(?P<hold>true|false))?\s*$"
)

ADVISORY_ONLY_ALL_CLEAR = (
    "ADVISORY_ONLY: dispatcher queue is ALL_CLEAR — no active dispatcher route is "
    "currently open; Estimator output is comparison-only and not next-build direction."
)

CLOSED_STATE_PREFIXES = ("GATED", "GOVERNED_AGENT", "INFRASTRUCTURE_BUILT")
BUILDABLE_STATE_PREFIXES = ("SIGNED_UNBUILT", "AWAITING_AUDIT")

AGENT_DESIGN_CONTRACT_PATH_RE = re.compile(
    r"4\. Product_Roadmap/[^\s`'\"]*Agent[^\s`'\"]*Design[^\s`'\"]*Contract[^\s`'\"]*\.md"
)

ARCHITECT_MANIFEST_CONTRACTS: dict[str, str] = {
    "#52": (
        "4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#61": (
        "4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#62": (
        "4. Product_Roadmap/Regression_Test_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#63": (
        "4. Product_Roadmap/Adversarial_Test_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#64": (
        "4. Product_Roadmap/Failure_Classification_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#65": (
        "4. Product_Roadmap/Correction_Evidence_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#67": (
        "4. Product_Roadmap/Rule_Improvement_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#10": (
        "4. Product_Roadmap/Lookalike_Domain_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#18": (
        "4. Product_Roadmap/Callback_Verification_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#49": (
        "4. Product_Roadmap/Audit_Trail_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#50": (
        "4. Product_Roadmap/Evidence_Strength_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#71": (
        "4. Product_Roadmap/Token_Usage_Tracker_Agent_Design_Contract_Deep_Dive.md"
    ),
    "#3": "docs/mmi/contracts/003_risk_triage_contract.md",
    "#2": "docs/mmi/contracts/002_mission_context_contract.md",
    "#1": "docs/mmi/contracts/001_swarm_commander_contract.md",
}

GOVERNANCE_FRAMEWORK_CONTRACTS: dict[str, str] = {
    "#105": (
        "4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md"
    ),
}

SIGNED_WEIGHTS_RECORD: dict[str, int] = {
    "F1": 30,
    "F2": 25,
    "F3": 20,
    "F4": 10,
    "F5": 10,
    "F6": 5,
}

WEIGHTS = dict(SIGNED_WEIGHTS_RECORD)

FACTOR_IDS = tuple(f"F{i}" for i in range(1, 7))

FORBIDDEN_TOOL_VERDICTS = frozenset(
    {
        "SELECTED",
        "AUTHORIZED",
        "APPROVED",
        "RECOMMENDED",
        "BUILD_AUTHORIZED",
        "COMPLETE",
        "SIGNED",
        "VERIFIED",
        "PASS",
        "FAIL",
        "PROMOTED",
        "NEXT_DECIDED",
    }
)

READINESS_LIFECYCLE_BASE = {
    "SIGNED_UNBUILT": 10,
    "AWAITING_AUDIT": 9,
    "DETECTOR_FUNCTION": 4,
    "SPEC_ONLY": 5,
    "NOT_STARTED": 3,
    "GOVERNANCE_DOC_ONLY": 3,
}

READINESS_REGISTRY = {
    "BUILD_AUTHORIZED": 10,
    "SIGNED_CONTRACT": 7,
    "DRAFT_CONTRACT": 4,
    "NEEDS_MMI_REVIEW": 3,
}

BLOCKER_EXCLUSIONS = (
    "NEEDS_REAL_DATA",
    "NEEDS_STAGE_B_AUTH",
    "NEEDS_BUILD_AUTH",
    "merged",
)

CODE_SURFACE_RE = re.compile(r"(?:core|tests)/[\w./_-]+")
PRODUCT_ROADMAP_RE = re.compile(r"4\. Product_Roadmap/[\w./_-]+\.md")
HEX40_RE = re.compile(r"\b[0-9a-fA-F]{40}\b")
RESEARCH_PATH_RE = re.compile(r"mmi/research/", re.IGNORECASE)

DARK_FACTOR_CAUSES = {
    "F2": "dependency graph not populated for scoreboard rows",
    "F3": "LAST_RUBRIC_SCORE empty / placeholder",
    "F6": "health board absent or row not linked",
}


@dataclass(frozen=True)
class FactorResult:
    measured: bool
    value: int | None = None
    null_reason: str = ""

    def display(self) -> str:
        if self.measured:
            return str(self.value)
        return f"NULL(no_data: {self.null_reason})"


@dataclass
class Candidate:
    candidate_id: str
    source: str
    name: str
    runtime_status: str
    blockers: str
    track: str
    depends_on: list[str] = field(default_factory=list)
    last_rubric_score: int | None = None
    has_rubric_column: bool = False
    registry_status: str = ""
    evidence_count: int = 0
    health_score: int | None = None
    code_evidence: str = ""
    layer: str = ""
    stage: str = ""
    last_updated: str = ""
    status_cell: str = ""
    excluded_by: list[str] = field(default_factory=list)


@dataclass
class BuildabilityExclusion:
    candidate: Candidate
    gates: list[str]
    reason: str
    runtime_status_prefix: str
    missing_contract: str = ""


@dataclass
class ScoredCandidate:
    candidate: Candidate
    factor_results: dict[str, FactorResult]
    weighted: dict[str, float]
    total_measured_score: float
    coverage_count: int
    coverage_status: str
    dark_factors: list[str]
    tie_break: str
    separation: str
    f2_note: str = ""

    @property
    def factors(self) -> dict[str, int]:
        return {
            key: result.value
            for key, result in self.factor_results.items()
            if result.measured and result.value is not None
        }

    @property
    def total(self) -> float:
        return self.total_measured_score


@dataclass(frozen=True)
class FeedstockEntry:
    candidate_id: str
    lane_type: str
    name: str
    priority: int
    hold_unless_matt: bool = False


@dataclass
class ScoredFeedstock:
    entry: FeedstockEntry
    scored: ScoredCandidate


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _yaml_load_no_comments(text: str) -> dict | list | None:
    if yaml is None:
        return None
    lines = [line for line in text.splitlines() if not line.strip().startswith("#")]
    try:
        return yaml.safe_load("\n".join(lines))
    except yaml.YAMLError:
        return None


def _normalized_status_cell(cell: str) -> str:
    return cell.strip().strip("`").strip()


def _cell_prefix(cell: str, prefixes: tuple[str, ...]) -> str:
    normalized = _normalized_status_cell(cell)
    for prefix in prefixes:
        if normalized.startswith(prefix):
            return prefix
    token = normalized.split()[0] if normalized else ""
    return token.rstrip("`")


def _cell_matches_prefix(cell: str, prefix: str) -> bool:
    return _normalized_status_cell(cell).startswith(prefix)


def _runtime_status_token(cell: str) -> str:
    cell = _normalized_status_cell(cell)
    if cell.startswith("GOVERNED_AGENT"):
        return "GOVERNED_AGENT"
    if cell.startswith("GATED"):
        return "GATED"
    if cell.startswith("INFRASTRUCTURE_BUILT"):
        return "INFRASTRUCTURE_BUILT"
    if cell.startswith("SIGNED_UNBUILT"):
        return "SIGNED_UNBUILT"
    if cell.startswith("AWAITING_AUDIT"):
        return "AWAITING_AUDIT"
    if cell.startswith("DETECTOR_FUNCTION"):
        return "DETECTOR_FUNCTION"
    if cell.startswith("SPEC_ONLY"):
        return "SPEC_ONLY"
    if cell.startswith("NOT_STARTED"):
        return "NOT_STARTED"
    if cell.startswith("GOVERNANCE_DOC_ONLY"):
        return "GOVERNANCE_DOC_ONLY"
    if cell.startswith("RECLASSIFY"):
        return "RECLASSIFY"
    if cell.startswith("merged"):
        return "merged"
    return cell.split()[0] if cell else ""


def _parse_rubric(cell: str) -> int | None:
    cell = cell.strip()
    if not cell or cell == "—" or cell == "-":
        return None
    try:
        return int(cell)
    except ValueError:
        return None


def _parse_health_board(scoreboard: str) -> tuple[dict[str, int], bool]:
    scores: dict[str, int] = {}
    in_board = False
    for line in scoreboard.splitlines():
        if "## Agent Health Score Board" in line:
            in_board = True
            continue
        if in_board and line.startswith("## ") and "Health Score" not in line:
            break
        if not in_board or not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 5 or parts[0] in ("#", "---"):
            continue
        agent_id = parts[0]
        try:
            scores[agent_id] = int(parts[4])
        except ValueError:
            continue
    return scores, in_board


def _governed_agent_ids(scoreboard: str) -> set[str]:
    done: set[str] = set()
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        agent_id = parts[0]
        if not re.match(r"^#?\d", agent_id):
            continue
        status = _runtime_status_token(parts[2])
        if status == "GOVERNED_AGENT":
            done.add(agent_id.lstrip("#"))
    return done


def _parse_scoreboard_rows(
    scoreboard: str,
    health: dict[str, int],
) -> list[Candidate]:
    rows: list[Candidate] = []
    governed = _governed_agent_ids(scoreboard)
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 8:
            continue
        raw_id = parts[0]
        if not re.match(r"^#?\d", raw_id):
            continue
        agent_id = raw_id.lstrip("#")
        if agent_id in governed:
            continue
        blockers = parts[6] if len(parts) > 6 else ""
        track = parts[7] if len(parts) > 7 else ""
        has_rubric_column = len(parts) > 8
        rubric = _parse_rubric(parts[8]) if has_rubric_column else None
        depends: list[str] = []
        for token in re.findall(r"DEPENDS_ON:#(\d+)", blockers):
            depends.append(token)
        rows.append(
            Candidate(
                candidate_id=f"#{agent_id}",
                source="scoreboard",
                name=parts[1],
                runtime_status=_runtime_status_token(parts[2]),
                blockers=blockers,
                track=track,
                depends_on=depends,
                last_rubric_score=rubric,
                has_rubric_column=has_rubric_column,
                health_score=health.get(raw_id) or health.get(agent_id),
                code_evidence=parts[3] if len(parts) > 3 else "",
                layer=parts[4] if len(parts) > 4 else "",
                stage=parts[5] if len(parts) > 5 else "",
                last_updated=parts[9] if len(parts) > 9 else "",
                status_cell=parts[2] if len(parts) > 2 else "",
            )
        )
    return rows


def _parse_registry_tasks(registry_text: str) -> list[Candidate]:
    data = _yaml_load_no_comments(registry_text)
    if not isinstance(data, dict):
        return []
    tasks = data.get("tasks") or []
    if not isinstance(tasks, list):
        return []
    out: list[Candidate] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        status = str(task.get("status") or "")
        if status == "COMPLETE":
            continue
        task_id = str(task.get("task_id") or "")
        if not task_id:
            continue
        ev = task.get("source_evidence") or []
        ev_count = len(ev) if isinstance(ev, list) else 0
        out.append(
            Candidate(
                candidate_id=task_id,
                source="registry",
                name=str(task.get("title") or task_id),
                runtime_status="",
                blockers="",
                track="BREADTH",
                registry_status=status,
                evidence_count=min(10, ev_count),
            )
        )
    return out


def _code_surface_count(code_evidence: str) -> int:
    if RESEARCH_PATH_RE.search(code_evidence):
        return 0
    return min(3, len(set(CODE_SURFACE_RE.findall(code_evidence))))


def _signed_surface_bonus(status_cell: str, code_evidence: str) -> int:
    blob = f"{status_cell} {code_evidence}".lower()
    if "§11" in blob or "agent design contract" in blob:
        return 2
    if "signed" in blob and any(token in blob for token in ("spec", "rubric", "contract")):
        return 2
    return 0


def _partial_penalty(status_cell: str) -> int:
    return 1 if "(partial" in status_cell.lower() else 0


def _layer_breadth_bonus(layer: str, track: str) -> int:
    if track != "BREADTH":
        return 0
    if layer.startswith("1 Command"):
        return 2
    if layer.startswith(("2 Detection", "3 Verification", "4 Evidence")):
        return 1
    return 0


def _scoreboard_evidence_count(cand: Candidate, decision_text: str) -> int:
    code = cand.code_evidence
    if RESEARCH_PATH_RE.search(code):
        return 0
    count = 0
    count += min(4, len(set(CODE_SURFACE_RE.findall(code))))
    count += len(set(PRODUCT_ROADMAP_RE.findall(code)))
    blob = f"{cand.status_cell} {code}".lower()
    if "§11" in blob or ("signed" in blob and "contract" in blob):
        count += 1
    if HEX40_RE.search(cand.last_updated):
        count += 1
    agent_id = cand.candidate_id.lstrip("#")
    count += min(2, len(re.findall(rf"#{agent_id}\b", decision_text)))
    return min(10, count)


def _row_status_by_id(scoreboard: str, agent_id: str) -> str:
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        raw_id = parts[0].lstrip("#")
        if raw_id == agent_id:
            return _runtime_status_token(parts[2])
    return ""


def _dependency_satisfied(agent_id: str, scoreboard: str) -> bool:
    return _row_status_by_id(scoreboard, agent_id) == "GOVERNED_AGENT"


def _downstream_unlock_count(agent_id: str, scoreboard: str) -> int:
    needle = f"DEPENDS_ON:#{agent_id}"
    return sum(1 for line in scoreboard.splitlines() if needle in line)


def _dependency_graph_populated(scoreboard: str) -> bool:
    return "DEPENDS_ON:" in scoreboard


def _apply_gates(
    candidates: list[Candidate],
    scoreboard: str,
    active_track: str,
) -> tuple[list[Candidate], list[Candidate]]:
    eligible: list[Candidate] = []
    excluded: list[Candidate] = []
    for cand in candidates:
        gates: list[str] = []
        if cand.source == "scoreboard":
            if cand.runtime_status == "merged":
                gates.append("E3")
            if cand.runtime_status == "RECLASSIFY":
                gates.append("E4")
            if cand.blockers.strip():
                gates.append("E5")
            for dep in cand.depends_on:
                if not _dependency_satisfied(dep, scoreboard):
                    gates.append("E6")
                    break
            if cand.track and cand.track != active_track:
                gates.append("E7")
            for token in BLOCKER_EXCLUSIONS:
                if token in cand.blockers:
                    if token == "NEEDS_REAL_DATA":
                        gates.append("E8")
                    elif token == "NEEDS_STAGE_B_AUTH":
                        gates.append("E9")
                    elif token == "NEEDS_BUILD_AUTH":
                        gates.append("E11")
        if cand.source == "registry" and cand.registry_status == "COMPLETE":
            gates.append("E10")
        cand.excluded_by = gates
        if gates:
            excluded.append(cand)
        else:
            eligible.append(cand)
    return eligible, excluded


def _extract_agent_design_contract_paths(*texts: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for match in AGENT_DESIGN_CONTRACT_PATH_RE.findall(text):
            if match not in seen:
                seen.add(match)
                paths.append(match)
    return paths


def _resolve_agent_design_contract(cand: Candidate) -> str | None:
    for path in _extract_agent_design_contract_paths(cand.status_cell, cand.code_evidence):
        return path
    governance = GOVERNANCE_FRAMEWORK_CONTRACTS.get(cand.candidate_id)
    if governance:
        return governance
    return ARCHITECT_MANIFEST_CONTRACTS.get(cand.candidate_id)


def _buildability_reason(gates: list[str]) -> str:
    if "E12" in gates:
        return "EXCLUDED_ALREADY_BUILT"
    if "E14" in gates:
        return "BLOCKED_MISSING_CONTRACT"
    return "EXCLUDED_NON_BUILDABLE_STATE"


def _evaluate_buildability_gates(cand: Candidate, root: Path) -> tuple[list[str], str]:
    gates: list[str] = []
    missing_contract = ""
    if cand.source == "scoreboard":
        if any(
            _cell_matches_prefix(cand.status_cell, prefix)
            for prefix in CLOSED_STATE_PREFIXES
        ):
            return ["E12"], ""
        if not any(
            _cell_matches_prefix(cand.status_cell, prefix)
            for prefix in BUILDABLE_STATE_PREFIXES
        ):
            gates.append("E13")
        contract_rel = _resolve_agent_design_contract(cand)
        if contract_rel is None or not (root / contract_rel).is_file():
            gates.append("E14")
            missing_contract = contract_rel or (
                ARCHITECT_MANIFEST_CONTRACTS.get(cand.candidate_id) or ""
            )
    else:
        gates.append("E13")
    return gates, missing_contract


def _runtime_status_prefix_for_candidate(cand: Candidate) -> str:
    if cand.source == "registry":
        return cand.registry_status or "registry"
    return _cell_prefix(
        cand.status_cell,
        CLOSED_STATE_PREFIXES + BUILDABLE_STATE_PREFIXES,
    ) or cand.runtime_status or "unknown"


def _apply_buildability_gates(
    candidates: list[Candidate],
    root: Path,
) -> tuple[list[Candidate], list[BuildabilityExclusion]]:
    buildable: list[Candidate] = []
    exclusions: list[BuildabilityExclusion] = []
    for cand in candidates:
        gates, missing_contract = _evaluate_buildability_gates(cand, root)
        if gates:
            exclusions.append(
                BuildabilityExclusion(
                    candidate=cand,
                    gates=gates,
                    reason=_buildability_reason(gates),
                    runtime_status_prefix=_runtime_status_prefix_for_candidate(cand),
                    missing_contract=missing_contract,
                )
            )
        else:
            buildable.append(cand)
    return buildable, exclusions


def _all_clear_from_verify_text(verify_text: str) -> bool:
    return "current task: MODE: ALL_CLEAR" in verify_text


def _f1_readiness(cand: Candidate) -> FactorResult:
    if cand.source == "registry":
        return FactorResult(True, READINESS_REGISTRY.get(cand.registry_status, 3))
    base = READINESS_LIFECYCLE_BASE.get(cand.runtime_status, 3)
    if cand.runtime_status == "SPEC_ONLY" and "NEEDS_SIGNED_CONTRACT" in cand.blockers:
        return FactorResult(True, 5)
    total = base
    total += _code_surface_count(cand.code_evidence)
    total += _signed_surface_bonus(cand.status_cell, cand.code_evidence)
    total -= _partial_penalty(cand.status_cell)
    total += _layer_breadth_bonus(cand.layer, cand.track)
    return FactorResult(True, max(0, min(10, total)))


def _f2_unlock(
    cand: Candidate,
    scoreboard: str,
    graph_populated: bool,
) -> tuple[FactorResult, str]:
    if cand.source != "scoreboard":
        return (
            FactorResult(
                False,
                null_reason="no scoreboard dependency graph for registry row",
            ),
            "downstream_deps=NULL",
        )
    if not graph_populated:
        return (
            FactorResult(
                False,
                null_reason="dependency graph not populated for scoreboard rows",
            ),
            "downstream_deps=no_graph",
        )
    agent_id = cand.candidate_id.lstrip("#")
    count = _downstream_unlock_count(agent_id, scoreboard)
    if count == 0:
        return FactorResult(True, 0), "downstream_deps=0_recorded"
    return FactorResult(True, min(10, count)), f"downstream_deps={count}"


def _f3_rubric(cand: Candidate) -> FactorResult:
    if cand.source == "registry":
        return FactorResult(
            False,
            null_reason="LAST_RUBRIC_SCORE not present on registry tasks",
        )
    if cand.last_rubric_score is not None:
        return FactorResult(True, max(0, min(10, cand.last_rubric_score)))
    if cand.has_rubric_column:
        return FactorResult(False, null_reason="LAST_RUBRIC_SCORE empty")
    return FactorResult(False, null_reason="LAST_RUBRIC_SCORE column absent")


def _f4_evidence(cand: Candidate) -> FactorResult:
    return FactorResult(True, max(0, min(10, cand.evidence_count)))


def _manifest_verify_gate(verify_text: str) -> tuple[bool, str]:
    if not verify_text.strip():
        return True, "ABSENT"
    match = re.search(r"drift:\s*(\d+)\s+BLOCK", verify_text)
    if match and int(match.group(1)) > 0:
        return False, "BLOCK_PRESENT"
    if "VERDICT:" in verify_text and "PASS" in verify_text:
        return True, "PASS"
    if "0 BLOCK" in verify_text:
        return True, "PASS"
    return False, "UNREADABLE"


def _f5_verify(manifest_verify: str) -> FactorResult:
    if manifest_verify in ("PASS", "ABSENT"):
        return FactorResult(True, 0)
    return FactorResult(True, 0)


def _f6_health(cand: Candidate, health_board_present: bool) -> FactorResult:
    if not health_board_present:
        return FactorResult(False, null_reason="health board absent")
    if cand.health_score is None:
        return FactorResult(False, null_reason="health row not linked")
    return FactorResult(True, min(10, cand.health_score // 10))


def _coverage_status(count: int) -> str:
    if count >= 6:
        return "FULL"
    if count >= 4:
        return "PARTIAL"
    return "LOW_COVERAGE_PROVISIONAL"


def _separation_note(
    cand: Candidate,
    factor_results: dict[str, FactorResult],
    f2_note: str,
) -> str:
    f3 = factor_results["F3"]
    f3_text = str(f3.value) if f3.measured else "NULL"
    if cand.source == "registry":
        return (
            f"F1=registry_status:{cand.registry_status} "
            f"F4=registry_evidence_refs:{cand.evidence_count} "
            f"F3={f3_text} {f2_note}"
        )
    return (
        f"F1=life:{cand.runtime_status}+code:{_code_surface_count(cand.code_evidence)}"
        f"+signed:{_signed_surface_bonus(cand.status_cell, cand.code_evidence)}"
        f"-partial:{_partial_penalty(cand.status_cell)}"
        f"+layer:{_layer_breadth_bonus(cand.layer, cand.track)} "
        f"F4=recorded_refs:{cand.evidence_count} "
        f"F3=rubric:{f3_text} "
        f"{f2_note}"
    )


def _score_candidate(
    cand: Candidate,
    scoreboard: str,
    manifest_verify: str,
    *,
    graph_populated: bool,
    health_board_present: bool,
) -> ScoredCandidate:
    f2, f2_note = _f2_unlock(cand, scoreboard, graph_populated)
    factor_results = {
        "F1": _f1_readiness(cand),
        "F2": f2,
        "F3": _f3_rubric(cand),
        "F4": _f4_evidence(cand),
        "F5": _f5_verify(manifest_verify),
        "F6": _f6_health(cand, health_board_present),
    }
    weighted: dict[str, float] = {}
    total = 0.0
    coverage_count = 0
    dark_factors: list[str] = []
    for idx, factor_id in enumerate(FACTOR_IDS, start=1):
        result = factor_results[factor_id]
        if result.measured and result.value is not None:
            coverage_count += 1
            contrib = result.value * WEIGHTS[factor_id] / 10
            weighted[f"W{idx}"] = contrib
            total += contrib
        else:
            dark_factors.append(factor_id)
    total_measured_score = round(total, 2)
    tie_break = (
        f"total={total_measured_score},coverage={coverage_count},"
        f"F1={factor_results['F1'].display()},F4={factor_results['F4'].display()},"
        f"F3={factor_results['F3'].display()},F2={factor_results['F2'].display()},"
        f"id={cand.candidate_id}"
    )
    separation = _separation_note(cand, factor_results, f2_note)
    return ScoredCandidate(
        candidate=cand,
        factor_results=factor_results,
        weighted=weighted,
        total_measured_score=total_measured_score,
        coverage_count=coverage_count,
        coverage_status=_coverage_status(coverage_count),
        dark_factors=dark_factors,
        tie_break=tie_break,
        separation=separation,
        f2_note=f2_note,
    )


def _factor_sort_value(result: FactorResult) -> int:
    if result.measured and result.value is not None:
        return result.value
    return -1


def _sort_scored(scored: list[ScoredCandidate]) -> list[ScoredCandidate]:
    return sorted(
        scored,
        key=lambda s: (
            -s.total_measured_score,
            -s.coverage_count,
            -_factor_sort_value(s.factor_results["F1"]),
            -_factor_sort_value(s.factor_results["F4"]),
            -_factor_sort_value(s.factor_results["F3"]),
            -_factor_sort_value(s.factor_results["F2"]),
            s.candidate.candidate_id,
        ),
    )


def _current_plan_bor_slice(bor_text: str) -> str:
    """Return only the active CURRENT_PLAN block; ignore superseded historical feedstock."""
    if "plan_status: CURRENT_PLAN" not in bor_text:
        return ""
    lines = bor_text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == "plan_status: CURRENT_PLAN":
            start = index
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## Prior") or stripped == "plan_status: SUPERSEDED_PLAN":
            end = index
            break
    return "\n".join(lines[start:end])


def _parse_bor_feedstock(bor_text: str) -> list[FeedstockEntry]:
    slice_text = _current_plan_bor_slice(bor_text)
    if not slice_text:
        return []
    entries: list[FeedstockEntry] = []
    for line in slice_text.splitlines():
        match = FEEDSTOCK_ENTRY_RE.match(line.strip())
        if not match:
            continue
        priority_raw = match.group("priority")
        hold = match.group("hold") == "true" or priority_raw == "hold"
        priority = 999 if hold else int(priority_raw)
        entries.append(
            FeedstockEntry(
                candidate_id=match.group("candidate_id"),
                lane_type=match.group("lane_type"),
                name=match.group("name").strip(),
                priority=priority,
                hold_unless_matt=hold,
            )
        )
    return entries


def _feedstock_closed_lifecycle_skip(
    candidate: Candidate, entry: FeedstockEntry
) -> bool:
    """Skip closed lifecycle rows unless per-component contract feedstock applies."""
    if not any(
        _cell_matches_prefix(candidate.status_cell, prefix)
        for prefix in CLOSED_STATE_PREFIXES
    ):
        return False
    if (
        entry.lane_type == "CONTRACT_DRAFT"
        and _cell_matches_prefix(candidate.status_cell, "INFRASTRUCTURE_BUILT")
        and "NEEDS_SIGNED_CONTRACT" in candidate.blockers
    ):
        return False
    return True


def _score_feedstock(
    candidates: list[Candidate],
    feedstock_entries: list[FeedstockEntry],
    scoreboard: str,
    manifest_verify: str,
    *,
    graph_populated: bool,
    health_board_present: bool,
) -> list[ScoredFeedstock]:
    """Score BOR feedstock against scoreboard rows (not buildability-eligible subset)."""
    by_id = {
        candidate.candidate_id: candidate
        for candidate in candidates
        if candidate.source == "scoreboard"
    }
    ranked: list[ScoredFeedstock] = []
    for entry in feedstock_entries:
        if entry.hold_unless_matt:
            continue
        candidate = by_id.get(entry.candidate_id)
        if candidate is None:
            continue
        if _feedstock_closed_lifecycle_skip(candidate, entry):
            continue
        scored = _score_candidate(
            candidate,
            scoreboard,
            manifest_verify,
            graph_populated=graph_populated,
            health_board_present=health_board_present,
        )
        ranked.append(ScoredFeedstock(entry=entry, scored=scored))
    ranked.sort(
        key=lambda item: (
            item.entry.priority,
            -item.scored.total_measured_score,
            item.entry.candidate_id,
        )
    )
    return ranked


def _factor_coverage_summary(scored: list[ScoredCandidate]) -> dict[str, tuple[int, int]]:
    summary: dict[str, tuple[int, int]] = {}
    for factor_id in FACTOR_IDS:
        measured = sum(1 for item in scored if item.factor_results[factor_id].measured)
        null_count = len(scored) - measured
        summary[factor_id] = (measured, null_count)
    return summary


def _collect_dark_causes(scored: list[ScoredCandidate]) -> dict[str, set[str]]:
    causes: dict[str, set[str]] = {factor_id: set() for factor_id in FACTOR_IDS}
    for item in scored:
        for factor_id in item.dark_factors:
            result = item.factor_results[factor_id]
            if result.null_reason:
                causes[factor_id].add(result.null_reason)
    return causes


def analyze(
    root: Path,
    *,
    active_track: str = "BREADTH",
    verify_text: str = "",
) -> tuple[
    list[ScoredCandidate],
    list[str],
    str,
    list[BuildabilityExclusion],
    list[ScoredFeedstock],
]:
    errors: list[str] = []
    scoreboard_path = root / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
    registry_path = root / "mmi" / "MMI_TASK_REGISTRY.yaml"
    decision_path = root / "mmi" / "MMI_DECISION_LOG.md"

    scoreboard = _read_text(scoreboard_path)
    registry_text = _read_text(registry_path)
    if not scoreboard:
        errors.append(f"missing_or_unreadable: {scoreboard_path}")
    if not registry_text:
        errors.append(f"missing_or_unreadable: {registry_path}")
    if errors:
        return [], errors, "UNREADABLE", [], []

    verify_ok, manifest_verify = _manifest_verify_gate(verify_text)
    if verify_text.strip() and not verify_ok:
        errors.append(f"manifest_verify_failed: {manifest_verify}")
        return [], errors, manifest_verify, [], []

    decision_text = _read_text(decision_path)
    health, health_board_present = _parse_health_board(scoreboard)
    graph_populated = _dependency_graph_populated(scoreboard)

    candidates = _parse_scoreboard_rows(scoreboard, health)
    candidates.extend(_parse_registry_tasks(registry_text))
    for cand in candidates:
        if cand.source == "scoreboard":
            cand.evidence_count = _scoreboard_evidence_count(cand, decision_text)

    ids = [c.candidate_id for c in candidates]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        errors.append(f"conflicting_candidate_id: {', '.join(dupes)}")
        return [], errors, manifest_verify, [], []

    eligible, _ = _apply_gates(candidates, scoreboard, active_track)
    buildable, buildability_exclusions = _apply_buildability_gates(eligible, root)
    scored = [
        _score_candidate(
            c,
            scoreboard,
            manifest_verify,
            graph_populated=graph_populated,
            health_board_present=health_board_present,
        )
        for c in buildable
    ]
    if buildable:
        return _sort_scored(scored), [], manifest_verify, buildability_exclusions, []

    bor_text = _read_text(root / BOR_PATH_REL)
    feedstock_entries = _parse_bor_feedstock(bor_text)
    feedstock_scored = _score_feedstock(
        candidates,
        feedstock_entries,
        scoreboard,
        manifest_verify,
        graph_populated=graph_populated,
        health_board_present=health_board_present,
    )
    return [], [], manifest_verify, buildability_exclusions, feedstock_scored


def format_buildability_exclusions(exclusions: list[BuildabilityExclusion]) -> str:
    lines = [ENVELOPE_BUILDABILITY_EXCLUSIONS, f"excluded_count: {len(exclusions)}"]
    for item in exclusions:
        lines.append("---")
        lines.append(f"candidate_id: {item.candidate.candidate_id}")
        lines.append(f"name: {item.candidate.name}")
        lines.append(f"gates: {','.join(item.gates)}")
        lines.append(f"reason: {item.reason}")
        lines.append(f"runtime_status_prefix: {item.runtime_status_prefix}")
        if item.missing_contract:
            lines.append(f"missing_contract: {item.missing_contract}")
    if exclusions:
        lines.append("---")
    return "\n".join(lines) + "\n"


def format_no_buildable_candidates() -> str:
    return f"{ENVELOPE_NO_BUILDABLE}\n"


def format_output(
    scored: list[ScoredCandidate],
    manifest_verify: str,
    *,
    verify_text: str,
    buildability_exclusions: list[BuildabilityExclusion],
    feedstock_scored: list[ScoredFeedstock] | None = None,
) -> str:
    parts: list[str] = []
    if _all_clear_from_verify_text(verify_text):
        parts.append(ADVISORY_ONLY_ALL_CLEAR)
    if buildability_exclusions:
        parts.append(format_buildability_exclusions(buildability_exclusions).rstrip("\n"))
    if scored:
        parts.append(format_scored(scored, manifest_verify).rstrip("\n"))
    elif feedstock_scored:
        parts.append(
            format_scored_feedstock(feedstock_scored, manifest_verify).rstrip("\n")
        )
    else:
        parts.append(format_no_buildable_candidates().rstrip("\n"))
    return _validate_output("\n".join(parts) + "\n")


def format_scored(scored: list[ScoredCandidate], manifest_verify: str) -> str:
    lines = [
        ENVELOPE_SCORED,
        f"candidate_count: {len(scored)}",
        "weights: F1=30 F2=25 F3=20 F4=10 F5=10 F6=5",
        f"manifest_verify: {manifest_verify}",
        "f5_policy: run_hygiene_only (F5=0 measured; non-separating)",
    ]
    summary = _factor_coverage_summary(scored)
    dark_causes = _collect_dark_causes(scored)
    has_dark = any(null_count for _, null_count in summary.values())
    if has_dark:
        lines.append("ranking computed with dark factors present")
        lines.append("factor_coverage_summary:")
        for factor_id in FACTOR_IDS:
            measured, null_count = summary[factor_id]
            lines.append(f"  {factor_id} measured: {measured} / NULL: {null_count}")
        lines.append("dark_factor_causes:")
        for factor_id in FACTOR_IDS:
            reasons = sorted(dark_causes[factor_id])
            if reasons:
                lines.append(f"  {factor_id}: {'; '.join(reasons)}")
            elif factor_id in DARK_FACTOR_CAUSES and summary[factor_id][1]:
                lines.append(f"  {factor_id}: {DARK_FACTOR_CAUSES[factor_id]}")
    lines.append("---")
    for item in scored:
        c = item.candidate
        lines.append(f"candidate_id: {c.candidate_id}")
        lines.append(f"source: {c.source}")
        lines.append(f"name: {c.name}")
        lines.append("factors:")
        for factor_id in FACTOR_IDS:
            lines.append(f"  {factor_id}={item.factor_results[factor_id].display()}")
        lines.append(f"coverage: {item.coverage_count}/6")
        lines.append(f"dark_factors: {','.join(item.dark_factors) if item.dark_factors else 'none'}")
        lines.append(
            "weighted: "
            + " ".join(f"{k}={item.weighted[k]:.2f}" for k in sorted(item.weighted))
        )
        lines.append(f"total_measured_score: {item.total_measured_score:.2f}")
        lines.append(f"coverage_status: {item.coverage_status}")
        lines.append(f"separation: {item.separation}")
        lines.append(f"tie_break: {item.tie_break}")
        lines.append("---")
    if lines[-1] == "---" and len(scored) > 0:
        lines.pop()
    return _validate_output("\n".join(lines) + "\n")


def format_scored_feedstock(
    feedstock_scored: list[ScoredFeedstock], manifest_verify: str
) -> str:
    lines = [
        ENVELOPE_SCORED_FEEDSTOCK,
        f"candidate_count: {len(feedstock_scored)}",
        "source: mmi/BLUEPRINT_OF_RECORD.md CURRENT_PLAN feedstock_entry",
        "weights: F1=30 F2=25 F3=20 F4=10 F5=10 F6=5",
        f"manifest_verify: {manifest_verify}",
        "advisory: ALL_CLEAR feedstock ranking only; not build authorization",
    ]
    lines.append("---")
    for item in feedstock_scored:
        entry = item.entry
        scored = item.scored
        candidate = scored.candidate
        lines.append(f"candidate_id: {entry.candidate_id}")
        lines.append(f"name: {entry.name or candidate.name}")
        lines.append(f"lane_type: {entry.lane_type}")
        lines.append(f"bor_priority: {entry.priority}")
        lines.append("factors:")
        for factor_id in FACTOR_IDS:
            lines.append(
                f"  {factor_id}={scored.factor_results[factor_id].display()}"
            )
        lines.append(f"total_measured_score: {scored.total_measured_score:.2f}")
        lines.append(f"coverage_status: {scored.coverage_status}")
        lines.append("---")
    if lines[-1] == "---" and len(feedstock_scored) > 0:
        lines.pop()
    return _validate_output("\n".join(lines) + "\n")


def format_incomplete(errors: list[str]) -> str:
    lines = [ENVELOPE_INCOMPLETE, "missing_or_conflicting:"]
    lines.extend(f"  - {err}" for err in errors)
    return _validate_output("\n".join(lines) + "\n")


def _validate_output(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in FORBIDDEN_TOOL_VERDICTS:
            raise RuntimeError(f"forbidden tool verdict on output line: {stripped}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on estimator output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Estimator Mode A — read-only candidate scoring (stdout only)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: repo root)",
    )
    parser.add_argument(
        "--track",
        default="BREADTH",
        help="Active TRACK gate value (default: BREADTH)",
    )
    parser.add_argument(
        "--verify-text",
        default="",
        help="Optional cached mmi_dispatch --verify text for manifest hygiene gate",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root else _repo_root()
    scored, errors, manifest_verify, buildability_exclusions, feedstock_scored = analyze(
        root, active_track=args.track, verify_text=args.verify_text
    )
    if errors:
        sys.stdout.write(format_incomplete(errors))
        return 2

    sys.stdout.write(
        format_output(
            scored,
            manifest_verify,
            verify_text=args.verify_text,
            buildability_exclusions=buildability_exclusions,
            feedstock_scored=feedstock_scored,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
