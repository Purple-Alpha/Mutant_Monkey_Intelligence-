#!/usr/bin/env python3
"""Next-Action Decision Rubric — read-only tactical scorer (stdout only).

Generates 3-7 candidate actions from scoreboard + BOR + ALL_CLEAR posture,
scores per §3.A binary calibration (MMI-DEC-095). Ranks only — Matt selects.

Does not write files, authorize build, or mutate scoreboard/BOR/registry.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE = "SCORED_NEXT_ACTIONS"
FORBIDDEN_TOKENS = frozenset(
    {
        "RECOMMENDED",
        "SELECTED",
        "NEXT_DECIDED",
        "AUTHORIZED",
        "BUILD_AUTHORIZED",
        "AUTONOMOUSLY_SELECTED",
    }
)

BOR_PATH_REL = "mmi/BLUEPRINT_OF_RECORD.md"
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"
FEEDSTOCK_ENTRY_RE = re.compile(
    r"^feedstock_entry:\s*"
    r"priority=(?P<priority>hold|\d+)\s+"
    r"candidate_id=(?P<candidate_id>#\d+[A-Z]?)\s+"
    r"lane_type=(?P<lane_type>[A-Z_]+)\s+"
    r"name=(?P<name>.+?)"
    r"(?:\s+hold_unless_matt=(?P<hold>true|false))?\s*$"
)

CONTRACT_REVIEW_ON_DISK = {
    "#1": "docs/mmi/contracts/001_swarm_commander_contract.md",
    "#2": "docs/mmi/contracts/002_mission_context_contract.md",
    "#3": "docs/mmi/contracts/003_risk_triage_contract.md",
}
ROUTING_POLICY_ANNEX_REL = (
    "docs/mmi/contracts/001_swarm_commander_routing_policy_annex.md"
)
ROUTING_POLICY_ANNEX_GATE_GLOB = "routing_policy_annex_pre_build_gate_*.md"
RANKED_ACTIONS_REL = "mmi/MMI_RANKED_NEXT_ACTIONS.md"
COMMAND_SPINE_IDS = ("#1", "#2", "#3")
CLOSED_LIFECYCLE_PREFIXES = ("GATED", "GOVERNED_AGENT", "INFRASTRUCTURE_BUILT")


def _spine_contract_signed(root: Path, candidate_id: str) -> bool:
    rel = CONTRACT_REVIEW_ON_DISK.get(candidate_id)
    if not rel:
        return False
    path = root / rel
    return path.is_file() and _is_contract_signed(_read_text(path))


@dataclass
class RubricCandidate:
    action_id: str
    label: str
    primary_scope: str
    kind: str
    edit_path_count: int = 1
    requires_section11: bool = False
    lifecycle_promotion: bool = False
    downstream_ids: list[str] = field(default_factory=list)


@dataclass
class AxisScores:
    leverage: int
    risk_reduction: int
    evidence_strength: int
    future_cost: int
    reversibility: int
    unmeasured: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (
            self.leverage
            + self.risk_reduction
            + self.evidence_strength
            + self.future_cost
            + self.reversibility
        )


@dataclass
class ScoredAction:
    candidate: RubricCandidate
    axes: AxisScores


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_estimator_module():
    script = Path(__file__).resolve().parent / "mmi_estimator.py"
    spec = importlib.util.spec_from_file_location("mmi_estimator", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_estimator"] = module
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _current_plan_block(bor_text: str) -> str:
    if "CURRENT_PLAN" not in bor_text:
        return bor_text
    start = bor_text.index("CURRENT_PLAN")
    end = bor_text.find("SUPERSEDED_PLAN", start)
    if end == -1:
        end = len(bor_text)
    return bor_text[start:end]


def _parse_bor_hold_entries(bor_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for line in _current_plan_block(bor_text).splitlines():
        match = FEEDSTOCK_ENTRY_RE.match(line.strip())
        if not match:
            continue
        priority = match.group("priority")
        hold = match.group("hold") == "true" or priority == "hold"
        if not hold:
            continue
        entries.append(
            {
                "candidate_id": match.group("candidate_id"),
                "lane_type": match.group("lane_type"),
                "name": match.group("name").strip(),
            }
        )
    return entries


def _downstream_count(agent_id: str, scoreboard: str) -> int:
    needle = f"DEPENDS_ON:#{agent_id.lstrip('#')}"
    return sum(1 for line in scoreboard.splitlines() if needle in line)


def _is_contract_signed(content: str) -> bool:
    for line in content.splitlines():
        if "**Status:**" not in line:
            continue
        if "UNSIGNED" in line or "DRAFT - unsigned" in line:
            continue
        if "SIGNED" in line:
            return True
    return False


def _gate_clean_for_scope(root: Path, candidate_id: str) -> bool:
    audit_dir = root / "audit_outputs"
    if not audit_dir.is_dir():
        return False
    num = candidate_id.lstrip("#")
    patterns = (f"*{num}*gate*.md", f"mmi_{num}*.md")
    for pattern in patterns:
        for path in sorted(audit_dir.glob(pattern), reverse=True):
            text = _read_text(path)
            if "blocking=0 warnings=0" in text or "**Blocking deviations:** `0`" in text:
                return True
    return False


def _routing_policy_annex_gate_clean(root: Path) -> bool:
    audit_dir = root / "audit_outputs"
    if not audit_dir.is_dir():
        return False
    for path in sorted(audit_dir.glob(ROUTING_POLICY_ANNEX_GATE_GLOB), reverse=True):
        text = _read_text(path)
        if not text:
            continue
        if "**Blocking deviations:** `0`" in text and "**Warnings:** `0`" in text:
            return True
        if "GATE_SUMMARY: blocking=0 warnings=0" in text:
            return True
    return False


def _scoreboard_row_blockers(scoreboard: str, candidate_id: str) -> str:
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 7:
            continue
        raw_id = parts[0]
        if raw_id.lstrip("#") == candidate_id.lstrip("#"):
            return parts[6]
    return ""


def _scoreboard_runtime_prefix(scoreboard: str, candidate_id: str) -> str:
    num = candidate_id.lstrip("#")
    for line in scoreboard.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        if parts[0].lstrip("#") != num:
            continue
        cell = parts[2]
        head = cell.split("—")[0].strip("` ")
        for prefix in CLOSED_LIFECYCLE_PREFIXES + (
            "SIGNED_UNBUILT",
            "AWAITING_AUDIT",
            "SIGNED_CONTRACT",
            "DETECTOR_FUNCTION",
        ):
            if head.startswith(prefix) or f"`{prefix}`" in cell:
                return prefix
        token = head.split()[0] if head else ""
        return token.strip("`")
    return ""


def _is_closed_lifecycle(scoreboard: str, candidate_id: str) -> bool:
    prefix = _scoreboard_runtime_prefix(scoreboard, candidate_id)
    return prefix.startswith(CLOSED_LIFECYCLE_PREFIXES)


def command_spine_wrappers_gated(scoreboard: str) -> bool:
    for candidate_id in COMMAND_SPINE_IDS:
        if not _scoreboard_runtime_prefix(scoreboard, candidate_id).startswith("GATED"):
            return False
    return True


def _git_head_short(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except OSError:
        pass
    return ""


def _ranked_board_stale(root: Path) -> bool:
    ranked_path = root / RANKED_ACTIONS_REL
    if not ranked_path.is_file():
        return True
    text = _read_text(ranked_path)
    match = re.search(r"^git_head:\s*(\S+)", text, re.MULTILINE)
    if not match:
        return True
    pinned = match.group(1)
    current = _git_head_short(root)
    return bool(current) and pinned != current


def generate_candidates(root: Path) -> list[RubricCandidate]:
    scoreboard = _read_text(root / SCOREBOARD_REL)
    bor = _read_text(root / BOR_PATH_REL)
    out: list[RubricCandidate] = []
    seen: set[str] = set()

    def add(candidate: RubricCandidate) -> None:
        if candidate.action_id in seen:
            return
        seen.add(candidate.action_id)
        out.append(candidate)

    spine_gated = command_spine_wrappers_gated(scoreboard)

    for entry in _parse_bor_hold_entries(bor):
        cid = entry["candidate_id"]
        if _is_closed_lifecycle(scoreboard, cid):
            continue
        add(
            RubricCandidate(
                action_id=f"bor_unpark_{cid}",
                label=(
                    f"Unpark BOR feedstock {cid} {entry['name']} "
                    f"({entry['lane_type']})"
                ),
                primary_scope=cid,
                kind="bor_unpark",
                edit_path_count=1,
            )
        )

    if _scoreboard_row_blockers(scoreboard, "#2") and not _spine_contract_signed(
        root, "#2"
    ):
        add(
            RubricCandidate(
                action_id="draft_contract_2",
                label="Draft #2 Mission Context Agent Design Contract",
                primary_scope="#2",
                kind="contract_draft",
                edit_path_count=1,
            )
        )

    for cid, rel in CONTRACT_REVIEW_ON_DISK.items():
        path = root / rel
        if path.is_file() and _is_contract_signed(_read_text(path)):
            if _is_closed_lifecycle(scoreboard, cid):
                continue
            add(
                RubricCandidate(
                    action_id=f"build_auth_{cid}",
                    label=(
                        f"Authorize {cid} wrapper build lane "
                        f"(SIGNED_UNBUILT scoreboard reconcile)"
                    ),
                    primary_scope=cid,
                    kind="build_auth",
                    requires_section11=False,
                    lifecycle_promotion=True,
                    edit_path_count=2,
                )
            )

    for cid in ("#47", "#52"):
        if not _scoreboard_runtime_prefix(scoreboard, cid).startswith("GATED"):
            continue
        if f"| {cid.lstrip('#')} " in scoreboard or f"| {cid} " in scoreboard:
            add(
                RubricCandidate(
                    action_id=f"promotion_{cid}",
                    label=f"Promotion review {cid} (GATED -> GOVERNED_AGENT when authorized)",
                    primary_scope=cid,
                    kind="promotion",
                    lifecycle_promotion=True,
                    edit_path_count=2,
                )
            )

    annex_path = root / ROUTING_POLICY_ANNEX_REL
    if spine_gated and not annex_path.is_file():
        add(
            RubricCandidate(
                action_id="routing_policy_annex_draft",
                label=(
                    "Draft #1 routing-policy annex (Command spine GATED; "
                    "read-only #3 telemetry wiring)"
                ),
                primary_scope="#1",
                kind="routing_annex",
                edit_path_count=1,
            )
        )
    elif spine_gated and annex_path.is_file() and not _is_contract_signed(
        _read_text(annex_path)
    ):
        if _routing_policy_annex_gate_clean(root):
            add(
                RubricCandidate(
                    action_id="routing_policy_annex_sign",
                    label=(
                        "Optional Matt §11 sign on #1 routing-policy annex "
                        "(pre-build gate clean 0/0)"
                    ),
                    primary_scope="#1",
                    kind="contract_sign",
                    edit_path_count=1,
                    requires_section11=True,
                )
            )
        else:
            add(
                RubricCandidate(
                    action_id="routing_policy_annex_gate",
                    label=(
                        "Run Grok pre-build gate on #1 routing-policy annex "
                        "(draft on disk; §11 UNSIGNED)"
                    ),
                    primary_scope="#1",
                    kind="contract_gate",
                    edit_path_count=1,
                )
            )

    if _ranked_board_stale(root):
        add(
            RubricCandidate(
                action_id="admin_lane_board_sync",
                label="Refresh ranked lane board (mmi_lane_board_sync + handshake pin)",
                primary_scope="admin",
                kind="admin",
                edit_path_count=2,
            )
        )

    add(
        RubricCandidate(
            action_id="hold_all_clear",
            label="Hold ALL_CLEAR — no new lane this cycle",
            primary_scope="hold",
            kind="hold",
            edit_path_count=0,
        )
    )

    return out


def _score_leverage(candidate: RubricCandidate, scoreboard: str) -> int:
    if candidate.kind in ("routing_annex", "contract_gate"):
        return 2
    if candidate.kind in ("hold", "admin"):
        return 0
    if candidate.downstream_ids:
        count = len(candidate.downstream_ids)
    else:
        scope = candidate.primary_scope.lstrip("#")
        if not scope.isdigit():
            return 0
        count = _downstream_count(scope, scoreboard)
    if count >= 2:
        return 2
    if count == 1:
        return 1
    return 0


def _score_risk_reduction(candidate: RubricCandidate, root: Path) -> int:
    if candidate.kind in ("routing_annex", "contract_gate"):
        return 2
    if candidate.kind == "admin":
        return 1
    if candidate.kind == "hold":
        return 0
    scope = candidate.primary_scope
    if scope.startswith("#") and _gate_clean_for_scope(root, scope):
        return 1
    return 0


def _score_evidence(candidate: RubricCandidate, root: Path) -> int:
    scope = candidate.primary_scope
    if candidate.kind in ("routing_annex", "contract_gate"):
        return 2
    if candidate.kind == "hold":
        return 0
    if scope.startswith("#"):
        rel = CONTRACT_REVIEW_ON_DISK.get(scope)
        if rel and (root / rel).is_file():
            content = _read_text(root / rel)
            if _is_contract_signed(content):
                return 2
            if content.strip():
                return 1
        if _gate_clean_for_scope(root, scope):
            return 2
    if candidate.kind == "admin":
        return 1
    return 0


def _score_future_cost(candidate: RubricCandidate) -> int:
    if candidate.kind == "admin":
        return 2
    if candidate.kind == "bor_unpark":
        return 1
    if candidate.kind == "hold":
        return 1
    if candidate.lifecycle_promotion:
        return 0
    return 1


def _score_reversibility(candidate: RubricCandidate) -> int:
    if candidate.requires_section11 or candidate.lifecycle_promotion:
        return 0
    if candidate.edit_path_count >= 3:
        return 0
    if candidate.edit_path_count >= 2:
        return 1
    return 2


def score_candidate(
    candidate: RubricCandidate, root: Path, scoreboard: str
) -> ScoredAction:
    if candidate.kind == "hold":
        axes = AxisScores(
            leverage=0,
            risk_reduction=0,
            evidence_strength=0,
            future_cost=1,
            reversibility=2,
        )
    else:
        axes = AxisScores(
            leverage=_score_leverage(candidate, scoreboard),
            risk_reduction=_score_risk_reduction(candidate, root),
            evidence_strength=_score_evidence(candidate, root),
            future_cost=_score_future_cost(candidate),
            reversibility=_score_reversibility(candidate),
        )
    return ScoredAction(candidate=candidate, axes=axes)


def analyze(root: Path, limit: int = 7) -> list[ScoredAction]:
    scoreboard = _read_text(root / SCOREBOARD_REL)
    candidates = generate_candidates(root)
    scored = [score_candidate(c, root, scoreboard) for c in candidates]
    scored.sort(key=lambda item: (-item.axes.total, item.candidate.action_id))
    hold = [item for item in scored if item.candidate.action_id == "hold_all_clear"]
    rest = [item for item in scored if item.candidate.action_id != "hold_all_clear"]
    cap = max(3, min(7, limit))
    merged = rest[: max(0, cap - len(hold))] + hold[:1]
    return merged[:cap]


def format_stdout(scored: list[ScoredAction], dispatcher_mode: str = "ALL_CLEAR") -> str:
    lines = [
        ENVELOPE,
        f"dispatcher_mode: {dispatcher_mode}",
        "authority_boundary: rubric ranks; Matt selects; not authorization",
        f"candidate_count: {len(scored)}",
    ]
    for index, item in enumerate(scored, start=1):
        c = item.candidate
        a = item.axes
        lines.append(f"ACTION: {index}")
        lines.append(f"action_id: {c.action_id}")
        lines.append(f"label: {c.label}")
        lines.append(f"primary_scope: {c.primary_scope}")
        lines.append(f"leverage: {a.leverage}")
        lines.append(f"risk_reduction: {a.risk_reduction}")
        lines.append(f"evidence_strength: {a.evidence_strength}")
        lines.append(f"future_cost: {a.future_cost}")
        lines.append(f"reversibility: {a.reversibility}")
        lines.append(f"TOTAL: {a.total}")
        if a.unmeasured:
            lines.append(f"UNMEASURED: {', '.join(a.unmeasured)}")
        else:
            lines.append("UNMEASURED: none")
        lines.append("---")
    if lines[-1] == "---":
        lines.pop()
    text = "\n".join(lines) + "\n"
    for token in FORBIDDEN_TOKENS:
        if token in text:
            raise RuntimeError(f"forbidden token in rubric output: {token}")
    return text


def format_markdown(scored: list[ScoredAction], dispatcher_mode: str) -> str:
    lines = [
        "# MMI Ranked Next Actions",
        "",
        "**Auto-generated.** Rubric ranks; Matt selects. Not build authorization.",
        "",
        f"dispatcher_mode: {dispatcher_mode}",
        f"candidate_count: {len(scored)}",
        "",
        "Refresh: `python3 scripts/mmi_lane_board_sync.py`",
        "",
        "---",
        "",
    ]
    for index, item in enumerate(scored, start=1):
        c = item.candidate
        a = item.axes
        lines.append(f"## ACTION {index} — TOTAL {a.total}/10")
        lines.append("")
        lines.append(f"**{c.label}**")
        lines.append("")
        lines.append(f"- action_id: `{c.action_id}`")
        lines.append(f"- primary_scope: `{c.primary_scope}`")
        lines.append(f"- leverage: {a.leverage}")
        lines.append(f"- risk_reduction: {a.risk_reduction}")
        lines.append(f"- evidence_strength: {a.evidence_strength}")
        lines.append(f"- future_cost: {a.future_cost}")
        lines.append(f"- reversibility: {a.reversibility}")
        lines.append(f"- **TOTAL: {a.total}**")
        lines.append("")
    return "\n".join(lines) + "\n"


def parse_ranked_markdown(text: str) -> list[dict[str, str]]:
    """Parse mmi/MMI_RANKED_NEXT_ACTIONS.md into summary rows."""
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## ACTION "):
            if current.get("label"):
                rows.append(current)
            match = re.match(r"## ACTION (\d+) — TOTAL (\d+)/10", line)
            current = {
                "rank": match.group(1) if match else str(len(rows) + 1),
                "total": match.group(2) if match else "?",
            }
            continue
        if line.startswith("**") and line.endswith("**") and "ACTION" not in line:
            current["label"] = line.strip("*")
        if line.startswith("- action_id:"):
            match = re.search(r"`([^`]+)`", line)
            if match:
                current["action_id"] = match.group(1)
        if line.startswith("- **TOTAL:"):
            current["total"] = line.split(":")[-1].strip().strip("*")
    if current.get("label"):
        rows.append(current)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Next-Action Rubric — read-only tactical scorer."
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=7)
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else _repo_root()
    scored = analyze(root, limit=max(3, min(7, args.limit)))
    sys.stdout.write(format_stdout(scored))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
