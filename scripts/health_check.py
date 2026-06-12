#!/usr/bin/env python3
"""Build health snapshot — read-only terminal report.

Run from the repo root:

    python3 scripts/health_check.py

Prints four sections:
  1. Agent Health Scores — governed agents, current status, health score if
     available; flags any agent scoring below 70.
  1b. Reserved / concept rows — scoreboard labels held for concept work with no
     contract and no build authorization (e.g. the Watcher Agents #85-87).
     Surfaced for visibility; never counted as governed, never health-flagged.
  2. Phase Gate Status — phases 1-9, current status (GATED / SIGNED / DRAFT /
     SIGNED_UNBUILT / BLOCKED) and the authorizing commit hash if applicable.
  3. Test baseline — the most recent recorded passing/skipped/xfailed counts.

This is a passive snapshot. It reads governed artifacts only — it does not run
the test suite, does not touch the blackboard, and authorizes nothing. Phase
status is derived from the signed contract files + the decision-cycles closure
log (not the build-map phase table, which is a hand-maintained summary and can
lag), so the snapshot reflects the actual signed/closed state.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCOREBOARD = REPO_ROOT / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
DECISION_LOG = REPO_ROOT / "decision_cycles_log.md"
ROADMAP = REPO_ROOT / "4. Product_Roadmap"

HEALTH_FLOOR = 70

STATUS_TOKENS = (
    "GOVERNED_AGENT",
    "GATED",
    "SIGNED_UNBUILT",
    "NEEDS_REAL_DATA",
    "NEEDS_STAGE_B_AUTH",
    "RECLASSIFY",
    "RESERVED",
    "BLOCKED",
    "GOVERNED",
)
GOVERNED_STATUSES = {"GOVERNED_AGENT", "GATED", "GOVERNED"}
# Reserved = a scoreboard label held for concept work with no contract and no
# build authorization. Surfaced for visibility, never counted as governed and
# never health-flagged (concept rows carry no score).
RESERVED_STATUSES = {"RESERVED"}
BAND_RE = re.compile(r"(\d{1,3})\s+(ELITE|HEALTHY|MARGINAL|AT RISK|DEMOTED)")
AGENT_ROW_RE = re.compile(r"^\|\s*(\d+[A-Z]?)\s*\|")

# Phase -> (name, contract filename or None if not yet drafted).
PHASES = [
    (1, "Infrastructure", "Phase1_Infrastructure_Agent_Design_Contract.md"),
    (2, "Knowledge Foundation", "Phase2_Knowledge_Foundation_Agent_Design_Contract.md"),
    (3, "Detection Swarm", "Phase3_Detection_Swarm_Agent_Design_Contract.md"),
    (4, "Reconciliation", "Phase4_ReconciliationAgent_Contract.md"),
    (5, "Mutation Engine", "Phase5_MutationEngine_Contract.md"),
    (6, "Collective Immune System", None),
    (7, "The Lung", None),
    (8, "Governance Completion", None),
    (9, "The Playhouse", None),
]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _git_short_hash(path: Path) -> str:
    """Most recent commit hash touching ``path``; '?' if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() or "—"
    except (OSError, subprocess.SubprocessError):
        return "?"


# --------------------------------------------------------------------------
# Section 1 — Agent Health Scores
# --------------------------------------------------------------------------


def _parse_manual_board(text: str) -> dict[str, int]:
    """Map agent id -> score from the manual Agent Health Score Board table.

    That table's header is ``| # | Agent | Layer | Stage | SCORE | ... |`` with a
    bare integer SCORE column (no ELITE/HEALTHY band word), so it is parsed
    positionally rather than via the band regex.
    """
    scores: dict[str, int] = {}
    in_board = False
    score_idx: int | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and "SCORE" in stripped and "Stage" in stripped:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            score_idx = cells.index("SCORE") if "SCORE" in cells else None
            in_board = True
            continue
        if in_board:
            if not stripped.startswith("|"):
                in_board = False
                score_idx = None
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not cells or set(cells[0]) <= set("-: "):
                continue  # separator row
            agent_id = cells[0]
            if score_idx is not None and score_idx < len(cells):
                m = re.search(r"\d{1,3}", cells[score_idx])
                if agent_id and m:
                    scores[agent_id] = int(m.group())
    return scores


def _parse_agent_rows(text: str) -> list[dict]:
    """Parse main scoreboard agent rows that carry a status token.

    Manual-board rows have no status token, so they are skipped here and handled
    by ``_parse_manual_board`` — this avoids double-counting an agent.
    """
    rows: list[dict] = []
    for line in text.splitlines():
        m = AGENT_ROW_RE.match(line)
        if not m:
            continue
        status = next((t for t in STATUS_TOKENS if t in line), None)
        if status is None:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        name = cells[1] if len(cells) > 1 else ""
        # First sentence/clause of the name cell keeps the table readable.
        name = re.split(r"\s+\(|\s+—", name)[0].strip()
        band = BAND_RE.search(line)
        rows.append(
            {
                "id": m.group(1),
                "name": name,
                "status": status,
                "score": int(band.group(1)) if band else None,
                "band": band.group(2) if band else None,
            }
        )
    return rows


def _sort_key(agent_id: str):
    m = re.match(r"(\d+)([A-Z]?)", agent_id)
    return (int(m.group(1)), m.group(2)) if m else (9999, agent_id)


def print_agent_health(text: str) -> None:
    print("=" * 72)
    print("1. AGENT HEALTH SCORES (governed agents)")
    print("=" * 72)

    manual = _parse_manual_board(text)
    rows = _parse_agent_rows(text)
    governed = [r for r in rows if r["status"] in GOVERNED_STATUSES]
    governed.sort(key=lambda r: _sort_key(r["id"]))

    if not governed:
        print("  (no governed agents found)")
        print()
        return

    flagged: list[str] = []
    print(f"  {'#':<5}{'AGENT':<34}{'STATUS':<16}{'SCORE':<14}")
    print(f"  {'-'*4:<5}{'-'*33:<34}{'-'*15:<16}{'-'*13:<14}")
    for r in governed:
        score = r["score"] if r["score"] is not None else manual.get(r["id"])
        band = r["band"] or ""
        if score is None:
            score_str = "—"
        else:
            score_str = f"{score} {band}".strip()
            if score < HEALTH_FLOOR:
                score_str += "  <-- BELOW 70"
                flagged.append(f"#{r['id']} {r['name']} ({score})")
        name = r["name"][:33]
        print(f"  {r['id']:<5}{name:<34}{r['status']:<16}{score_str:<14}")

    print()
    print(f"  Governed agents: {len(governed)}")
    if flagged:
        print(f"  FLAGGED below {HEALTH_FLOOR}: {', '.join(flagged)}")
    else:
        print(f"  FLAGGED below {HEALTH_FLOOR}: none")
    print()


# --------------------------------------------------------------------------
# Section 1b — Reserved / concept rows (no contract, no build authorization)
# --------------------------------------------------------------------------


def print_reserved_concepts(text: str) -> None:
    rows = [r for r in _parse_agent_rows(text) if r["status"] in RESERVED_STATUSES]
    rows.sort(key=lambda r: _sort_key(r["id"]))
    if not rows:
        return

    print("=" * 72)
    print("1b. RESERVED / CONCEPT (no contract — not governed, not built)")
    print("=" * 72)
    print(f"  {'#':<5}{'AGENT':<34}{'STATUS':<12}{'NOTE':<19}")
    print(f"  {'-'*4:<5}{'-'*33:<34}{'-'*11:<12}{'-'*18:<19}")
    for r in rows:
        name = r["name"][:33]
        print(f"  {r['id']:<5}{name:<34}{r['status']:<12}{'concept doc only':<19}")
    print()
    print(f"  Reserved rows: {len(rows)} (advisory; contract required before build)")
    print()


# --------------------------------------------------------------------------
# Section 2 — Phase Gate Status
# --------------------------------------------------------------------------


def _phase_closed(log_text: str, phase_num: int) -> bool:
    return bool(
        re.search(rf"PHASE {phase_num}\b.*PHASE_CLOSURE", log_text)
        or re.search(rf"PHASE {phase_num} .*CLOSURE", log_text)
    )


def _contract_status(contract_text: str) -> str:
    m = re.search(r"\*\*Status:\*\*\s*(.+)", contract_text)
    if not m:
        return "UNKNOWN"
    line = m.group(1)
    if "§11 SIGNED" in line or "11 SIGNED" in line:
        return "SIGNED"
    if "DRAFT" in line.upper():
        return "DRAFT"
    return "UNKNOWN"


def print_phase_gates() -> None:
    print("=" * 72)
    print("2. PHASE GATE STATUS")
    print("=" * 72)
    print(f"  {'PHASE':<6}{'NAME':<28}{'STATUS':<23}{'COMMIT':<10}")
    print(f"  {'-'*5:<6}{'-'*27:<28}{'-'*22:<23}{'-'*9:<10}")

    log_text = _read(DECISION_LOG)
    for num, name, contract in PHASES:
        commit = "—"
        if contract is None:
            status = "BLOCKED (no contract)"
        else:
            path = ROADMAP / contract
            if not path.exists():
                status = "BLOCKED (no contract)"
            else:
                status = _contract_status(_read(path))
                commit = _git_short_hash(path)
                if _phase_closed(log_text, num):
                    status = "GATED"
        print(f"  {num:<6}{name:<28}{status:<23}{commit:<10}")
    print()


# --------------------------------------------------------------------------
# Section 3 — Test baseline
# --------------------------------------------------------------------------


def print_test_baseline() -> None:
    print("=" * 72)
    print("3. TEST BASELINE (most recent recorded gate run)")
    print("=" * 72)

    log_text = _read(DECISION_LOG)
    triples = re.findall(
        r"(\d+)\s+passed,\s*(\d+)\s+skipped,\s*(\d+)\s+xfailed", log_text
    )
    if not triples:
        print("  (no recorded passed/skipped/xfailed baseline found)")
        print()
        return
    # Most recent baseline = the largest passing count recorded (suite grows
    # over time); robust to entry ordering in the log.
    passed, skipped, xfailed = max(triples, key=lambda t: int(t[0]))
    print(f"  passed:  {passed}")
    print(f"  skipped: {skipped}")
    print(f"  xfailed: {xfailed}")
    print()


def main() -> None:
    print()
    print("MUTANT MONKEY — BUILD HEALTH SNAPSHOT")
    print(f"repo: {REPO_ROOT}")
    print()
    scoreboard_text = _read(SCOREBOARD)
    if not scoreboard_text:
        print(f"WARNING: scoreboard not readable at {SCOREBOARD}")
        print()
    print_agent_health(scoreboard_text)
    print_reserved_concepts(scoreboard_text)
    print_phase_gates()
    print_test_baseline()


if __name__ == "__main__":
    main()
