#!/usr/bin/env python3
"""Generate plain-English Operator Map from live routing state.

Writes mmi/MMI_OPERATOR_MAP.md — one human-readable file for "what's next"
without MMI jargon. Auto-refreshed by lane_board_sync and mmi_dispatch --sync.

Does not authorize build, select lanes, or mutate scoreboard/BOR lifecycle.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OPERATOR_MAP_REL = "mmi/MMI_OPERATOR_MAP.md"
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"
RANKED_REL = "mmi/MMI_RANKED_NEXT_ACTIONS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_module(name: str, filename: str):
    script = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _git_head(root: Path) -> str:
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
    return "unknown"


def _dispatcher_mode(root: Path) -> str:
    state = _read_text(root / "MMI_CURRENT_STATE.md")
    for line in state.splitlines():
        if line.startswith("MODE:"):
            return line.split(":", 1)[1].strip()
        if line.strip() == "":
            break
    return "UNKNOWN"


def _governed_count(scoreboard: str) -> tuple[int, int]:
    match = re.search(
        r"\*\*BREADTH RUNWAY:\*\* \*\*(\d+)\*\* of (\d+) agents",
        scoreboard,
    )
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 70


def _gated_promotion_queue(scoreboard: str) -> list[tuple[str, str]]:
    rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
    ids = rubric._gated_breadth_promotion_ids(scoreboard)
    return [
        (cid, rubric._scoreboard_spark_name(scoreboard, cid)) for cid in ids
    ]


def _matt_copy_paste(next_cid: str, name: str) -> str:
    return f'Authorize GOVERNED_AGENT promotion review {next_cid} ({name})'


def build_operator_map(root: Path) -> str:
    rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
    scoreboard = _read_text(root / SCOREBOARD_REL)
    scored = rubric.analyze(root, limit=7, board_sync=True)
    governed, total = _governed_count(scoreboard)
    promotion_queue = _gated_promotion_queue(scoreboard)
    mode = _dispatcher_mode(root)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = _git_head(root)

    lines = [
        f"generated_at: {stamp}",
        f"git_head: {head}",
        "generator: scripts/mmi_operator_map_sync.py",
        "",
        "# Operator Map — read this first",
        "",
        "**Auto-generated plain-English view.** Rubric ranks; Matt selects.",
        "Not build authorization. Refresh: "
        "`python3 scripts/mmi_operator_map_sync.py`",
        "",
        "---",
        "",
        "## Where we are",
        "",
        f"- **Dispatcher:** `{mode}` — nothing waiting to be built or audited right now",
        f"- **Governed agents:** {governed} of {total} at production-quality Stage 1 (GOVERNED_AGENT)",
        f"- **Promotion queue:** {len(promotion_queue)} built-and-audited agents waiting for your promotion review",
        "",
        "## Why it keeps stalling",
        "",
        "Each build cycle ends at **GATED** (built + audited). Moving to **GOVERNED_AGENT**",
        "or starting the next build requires **you** in one sentence. When the pre-loaded",
        "BOR feedstock list is empty, the dispatcher goes **ALL_CLEAR** and the crew stops",
        "until you name the next lane.",
        "",
        "**Fix in use:** this map auto-surfaces the promotion queue from the scoreboard",
        "(not a hardcoded short list). Work the queue top-to-bottom to keep rolling.",
        "",
        "## What's next (ranked — not authorized until you say so)",
        "",
    ]

    if not scored:
        lines.append("- No ranked candidates — hold ALL_CLEAR")
    else:
        for index, item in enumerate(scored[:5], start=1):
            lines.append(
                f"{index}. **{item.candidate.label}** — score {item.axes.total}/10"
            )

    lines.extend(["", "## Promotion queue (built, audited, needs your review)", ""])
    if not promotion_queue:
        lines.append("- *(empty — all eligible agents promoted or blocked)*")
    else:
        for index, (cid, name) in enumerate(promotion_queue[:10], start=1):
            lines.append(f"{index}. **{cid} {name}** — GATED, ready for promotion review")

    next_lane = promotion_queue[0] if promotion_queue else None
    lines.extend(["", "## What to say to unstick (copy-paste)", ""])
    if next_lane:
        cid, name = next_lane
        lines.append(f"```text")
        lines.append(_matt_copy_paste(cid, name))
        lines.append("```")
    else:
        lines.append(
            "- Pick a new agent contract, unpark BOR feedstock, or authorize a build lane "
            "from `mmi/MMI_RANKED_NEXT_ACTIONS.md`."
        )

    lines.extend(
        [
            "",
            "## What the crew can do without you",
            "",
            "- Refresh maps (`mmi_lane_board_sync`, `mmi_dispatch --sync`, this file)",
            "- Run tests and verify (`mmi_dispatch --verify`)",
            "- Draft unsigned contracts (not build, not promotion)",
            "",
            "## Machine sources (for tools — not for humans first)",
            "",
            f"- Ranked board: `{RANKED_REL}`",
            "- Handshake pin: `PROJECT_HANDSHAKE.md`",
            "- Staged milestones: `mmi/MMI_MISSION_MAP.md` (may lag — trust this file + ranked board)",
            "- Agent inventory: `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def sync(root: Path) -> Path:
    out_path = root / OPERATOR_MAP_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_operator_map(root), encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write plain-English Operator Map.")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    root = args.root or _repo_root()
    path = sync(root)
    print(f"OPERATOR_MAP_SYNC: wrote {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
