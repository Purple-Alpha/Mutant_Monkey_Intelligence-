#!/usr/bin/env python3
"""MMI Estimator — Mode A read-only candidate scoring (stdout only).

Scores incomplete build candidates from a fixed manifest. Does not write files.
Does not import or subprocess the MMI dispatcher.

Weight authority: Estimator weights are owner policy locked by
``mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md`` §10.1 / §11 (MMI-DEC-038).
``WEIGHTS`` below must match the signed record. Weight changes require
operator instruction plus contract revision or MMI-DEC entry — never silent
code-only tuning.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ENVELOPE_SCORED = "SCORED_CANDIDATES"
ENVELOPE_INCOMPLETE = "STATE_INCOMPLETE_CANNOT_SCORE"

SIGNED_WEIGHTS_RECORD: dict[str, int] = {
    "F1": 30,
    "F2": 25,
    "F3": 20,
    "F4": 10,
    "F5": 10,
    "F6": 5,
}

WEIGHTS = dict(SIGNED_WEIGHTS_RECORD)

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
class ScoredCandidate:
    candidate: Candidate
    factors: dict[str, int]
    weighted: dict[str, float]
    total: float
    tie_break: str
    separation: str
    f2_note: str = ""


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


def _runtime_status_token(cell: str) -> str:
    cell = cell.strip().strip("`")
    if cell.startswith("GOVERNED_AGENT"):
        return "GOVERNED_AGENT"
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


def _parse_health_board(scoreboard: str) -> dict[str, int]:
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
    return scores


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


def _parse_scoreboard_rows(scoreboard: str, health: dict[str, int]) -> list[Candidate]:
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
        rubric = _parse_rubric(parts[8]) if len(parts) > 8 else None
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


def _f1_readiness(cand: Candidate) -> int:
    if cand.source == "registry":
        return READINESS_REGISTRY.get(cand.registry_status, 3)
    base = READINESS_LIFECYCLE_BASE.get(cand.runtime_status, 3)
    if cand.runtime_status == "SPEC_ONLY" and "NEEDS_SIGNED_CONTRACT" in cand.blockers:
        return 5
    if cand.source != "scoreboard":
        return min(10, base)
    total = base
    total += _code_surface_count(cand.code_evidence)
    total += _signed_surface_bonus(cand.status_cell, cand.code_evidence)
    total -= _partial_penalty(cand.status_cell)
    total += _layer_breadth_bonus(cand.layer, cand.track)
    return max(0, min(10, total))


def _f2_unlock(cand: Candidate, scoreboard: str) -> tuple[int, str]:
    if cand.source != "scoreboard":
        return 0, "downstream_deps=0_no_scoreboard_row"
    agent_id = cand.candidate_id.lstrip("#")
    count = _downstream_unlock_count(agent_id, scoreboard)
    if count == 0:
        return 0, "downstream_deps=0_recorded"
    return min(10, count), f"downstream_deps={count}"


def _f3_rubric(cand: Candidate) -> int:
    if cand.last_rubric_score is not None:
        return max(0, min(10, cand.last_rubric_score))
    return 0


def _f4_evidence(cand: Candidate) -> int:
    return max(0, min(10, cand.evidence_count))


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


def _f5_verify(manifest_verify: str) -> int:
    """Run-hygiene only. Non-separating: 0 when manifest verify PASS/ABSENT."""
    if manifest_verify in ("PASS", "ABSENT"):
        return 0
    return 0


def _f6_health(cand: Candidate) -> int:
    if cand.health_score is None:
        return 0
    return min(10, cand.health_score // 10)


def _separation_note(cand: Candidate, factors: dict[str, int], f2_note: str) -> str:
    if cand.source == "registry":
        return (
            f"F1=registry_status:{cand.registry_status} "
            f"F4=registry_evidence_refs:{cand.evidence_count} "
            f"{f2_note}"
        )
    return (
        f"F1=life:{cand.runtime_status}+code:{_code_surface_count(cand.code_evidence)}"
        f"+signed:{_signed_surface_bonus(cand.status_cell, cand.code_evidence)}"
        f"-partial:{_partial_penalty(cand.status_cell)}"
        f"+layer:{_layer_breadth_bonus(cand.layer, cand.track)} "
        f"F4=recorded_refs:{cand.evidence_count} "
        f"F3=rubric:{cand.last_rubric_score if cand.last_rubric_score is not None else 'none'} "
        f"{f2_note}"
    )


def _score_candidate(
    cand: Candidate,
    scoreboard: str,
    manifest_verify: str,
) -> ScoredCandidate:
    f2, f2_note = _f2_unlock(cand, scoreboard)
    factors = {
        "F1": _f1_readiness(cand),
        "F2": f2,
        "F3": _f3_rubric(cand),
        "F4": _f4_evidence(cand),
        "F5": _f5_verify(manifest_verify),
        "F6": _f6_health(cand),
    }
    weighted = {f"W{i}": factors[f"F{i}"] * WEIGHTS[f"F{i}"] / 10 for i in range(1, 7)}
    total = round(sum(weighted.values()), 2)
    tie_break = (
        f"F1={factors['F1']},F4={factors['F4']},F3={factors['F3']},"
        f"F2={factors['F2']},id={cand.candidate_id}"
    )
    separation = _separation_note(cand, factors, f2_note)
    return ScoredCandidate(cand, factors, weighted, total, tie_break, separation, f2_note)


def _sort_scored(scored: list[ScoredCandidate]) -> list[ScoredCandidate]:
    return sorted(
        scored,
        key=lambda s: (
            -s.total,
            -s.factors["F1"],
            -s.factors["F4"],
            -s.factors["F3"],
            -s.factors["F2"],
            s.candidate.candidate_id,
        ),
    )


def analyze(
    root: Path,
    *,
    active_track: str = "BREADTH",
    verify_text: str = "",
) -> tuple[list[ScoredCandidate], list[str], str]:
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
        return [], errors, "UNREADABLE"

    verify_ok, manifest_verify = _manifest_verify_gate(verify_text)
    if verify_text.strip() and not verify_ok:
        errors.append(f"manifest_verify_failed: {manifest_verify}")
        return [], errors, manifest_verify

    decision_text = _read_text(decision_path)
    health = _parse_health_board(scoreboard)

    candidates = _parse_scoreboard_rows(scoreboard, health)
    candidates.extend(_parse_registry_tasks(registry_text))
    for cand in candidates:
        if cand.source == "scoreboard":
            cand.evidence_count = _scoreboard_evidence_count(cand, decision_text)

    ids = [c.candidate_id for c in candidates]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        errors.append(f"conflicting_candidate_id: {', '.join(dupes)}")
        return [], errors, manifest_verify

    eligible, _ = _apply_gates(candidates, scoreboard, active_track)
    scored = [_score_candidate(c, scoreboard, manifest_verify) for c in eligible]
    return _sort_scored(scored), [], manifest_verify


def format_scored(scored: list[ScoredCandidate], manifest_verify: str) -> str:
    lines = [
        ENVELOPE_SCORED,
        f"candidate_count: {len(scored)}",
        "weights: F1=30 F2=25 F3=20 F4=10 F5=10 F6=5",
        f"manifest_verify: {manifest_verify}",
        "f5_policy: run_hygiene_only (F5=0; non-separating)",
        "---",
    ]
    for item in scored:
        c = item.candidate
        lines.append(f"candidate_id: {c.candidate_id}")
        lines.append(f"source: {c.source}")
        lines.append(f"name: {c.name}")
        lines.append(
            "factors: "
            + " ".join(f"{k}={v}" for k, v in sorted(item.factors.items()))
        )
        lines.append(
            "weighted: "
            + " ".join(f"{k}={item.weighted[k]:.2f}" for k in sorted(item.weighted))
        )
        lines.append(f"total: {item.total:.2f}")
        lines.append(f"separation: {item.separation}")
        lines.append(f"tie_break: {item.tie_break}")
        lines.append("---")
    if lines[-1] == "---" and len(scored) > 0:
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
    scored, errors, manifest_verify = analyze(
        root, active_track=args.track, verify_text=args.verify_text
    )
    if errors:
        sys.stdout.write(format_incomplete(errors))
        return 2

    sys.stdout.write(format_scored(scored, manifest_verify))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
