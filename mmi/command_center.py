#!/usr/bin/env python3
"""Read-only local MMI command center."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"
ACTIVE_STATUSES = {"pending", "queued", "todo", "in-progress", "in_progress"}

PROJECT_BRAIN_LINKS = [
    "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md",
    "mmi/project_brain/status/MMI_PHASE2_START.md",
    "mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md",
    "mmi/project_brain/status/MMI_LANE_ROUTING.md",
    "mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md",
]


def load_tasks(path: Path = TASK_FILE) -> tuple[list[dict[str, Any]], str | None]:
    """Load tasks.json without mutating it."""
    if not path.exists():
        return [], f"{path} does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], f"{path} is invalid JSON: {exc}"
    if not isinstance(data, list):
        return [], f"{path} must contain a JSON list"
    return data, None


def active_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        task
        for task in tasks
        if str(task.get("status", "")).lower() in ACTIVE_STATUSES
    ]


def is_mmi_task(task: dict[str, Any]) -> bool:
    task_id = str(task.get("id", ""))
    instruction = str(task.get("instruction", ""))
    return task_id.startswith("mmi-") or instruction.startswith("PROJECT: MMI.")


def hold_blocker(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next(
        (
            task
            for task in tasks
            if str(task.get("id")) == "mmi-await-matt-phase2"
            and str(task.get("status", "")).lower() == "paused"
        ),
        None,
    )


def task_summary(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": task.get("id", "unknown"),
        "score": task.get("score", "NO SCORE"),
        "assignee": task.get("assignee", "UNASSIGNED"),
        "tier": task.get("tier", "UNKNOWN TIER"),
        "status": task.get("status", "unknown"),
        "instruction": task.get("instruction", ""),
    }


def detect_pipe_status(tasks: list[dict[str, Any]], load_error: str | None = None) -> dict[str, Any]:
    if load_error:
        return {
            "pipe_status": "BLOCKED",
            "active_task": None,
            "blockers": [load_error],
        }

    active = active_tasks(tasks)
    if len(active) > 1:
        return {
            "pipe_status": "BLOCKED",
            "active_task": None,
            "blockers": [
                "multiple active tasks found",
                *[str(task.get("id", "unknown")) for task in active],
            ],
        }

    if active:
        task = active[0]
        if not is_mmi_task(task):
            return {
                "pipe_status": "BLOCKED",
                "active_task": task_summary(task),
                "blockers": [f"non-MMI active task found: {task.get('id', 'unknown')}"],
            }
        return {
            "pipe_status": "LOADED",
            "active_task": task_summary(task),
            "blockers": [],
        }

    blocker = hold_blocker(tasks)
    if blocker:
        return {
            "pipe_status": "HOLD",
            "active_task": task_summary(blocker),
            "blockers": [str(blocker.get("id", "mmi-await-matt-phase2"))],
        }

    return {
        "pipe_status": "DRY",
        "active_task": None,
        "blockers": [],
    }


def next_action_for(active_task: dict[str, Any] | None, pipe_status: str) -> str:
    if pipe_status == "BLOCKED":
        return "Fix the blocker before continuing. Do not execute non-MMI work."
    if pipe_status == "HOLD":
        return "Matt provides directive or approval before work continues."
    if pipe_status == "DRY":
        return "Run python scripts/reload_mmi_pipes.py or python mmi/command_center.py to auto-seed from mmi/task_pipeline.json."
    if not active_task:
        return "No active task available."

    assignee = str(active_task.get("assignee", "UNASSIGNED"))
    if assignee == "Codex":
        return "Codex executes the required output, then marks task complete or reports blocker."
    if assignee == "Cursor PM":
        return "Cursor PM completes PM-owned queue/status work."
    if assignee == "Matt":
        return "Matt provides directive or approval before work continues."
    if assignee == "Claude":
        return "Route design/spec work to Claude."
    if assignee == "Gemini Paid API":
        return "Route audit/check work to Gemini Paid API."
    if assignee == "Gemini":
        return "Route primary research to Gemini."
    if assignee == "ChatGPT":
        return "Route deep/secondary research to ChatGPT."
    return f"{assignee} owns the next action."


def project_brain_links() -> list[str]:
    return list(PROJECT_BRAIN_LINKS)


def build_state(auto_seed: bool = True) -> dict[str, Any]:
    if auto_seed:
        import sys

        scripts_dir = str(ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from keep_task_queue_warm import seed_if_dry

        seed_if_dry()

    tasks, load_error = load_tasks()
    state = detect_pipe_status(tasks, load_error)
    state["next_action"] = next_action_for(state["active_task"], state["pipe_status"])
    state["project_brain_links"] = project_brain_links()
    return state


def render_text(state: dict[str, Any]) -> str:
    active = state.get("active_task")
    lines = [
        "MMI COMMAND CENTER",
        f"PIPE STATUS: {state['pipe_status']}",
        "",
    ]

    if active:
        lines.extend(
            [
                "ACTIVE TASK",
                f"  ID:       {active.get('id', 'unknown')}",
                f"  SCORE:    {active.get('score', 'NO SCORE')}",
                f"  OWNER:    {active.get('assignee', 'UNASSIGNED')}",
                f"  TIER:     {active.get('tier', 'UNKNOWN TIER')}",
                f"  STATUS:   {active.get('status', 'unknown')}",
                "",
            ]
        )
        instruction = str(active.get("instruction", "")).strip()
        if instruction:
            lines.extend(["WORK", f"  {instruction}", ""])
    else:
        lines.extend(["ACTIVE TASK", "  None", ""])

    blockers = state.get("blockers") or []
    if blockers:
        lines.append("BLOCKERS")
        lines.extend(f"  {blocker}" for blocker in blockers)
        lines.append("")

    lines.extend(["NEXT ACTION", f"  {state['next_action']}", ""])
    lines.append("PROJECT BRAIN")
    for link in state["project_brain_links"]:
        label = Path(link).stem.replace("_", " ").title()
        lines.append(f"  {label}: {link}")

    return "\n".join(lines)


def render_json(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2)


def print_once(as_json: bool) -> None:
    state = build_state()
    print(render_json(state) if as_json else render_text(state))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable state")
    parser.add_argument("--watch", action="store_true", help="reprint state on an interval")
    parser.add_argument("--seconds", type=int, default=60, help="watch interval in seconds")
    args = parser.parse_args()

    if not args.watch:
        print_once(args.json)
        return 0

    interval = max(args.seconds, 5)
    while True:
        print_once(args.json)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
