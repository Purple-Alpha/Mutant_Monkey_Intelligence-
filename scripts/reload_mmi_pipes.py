#!/usr/bin/env python3
"""Reload the local MMI task pipe.

Use this when you want one concrete command that:
- keeps tasks.json from going dry
- refuses to bless a non-MMI active task
- prints the next task, score, and assignee

It does not execute the task. It only keeps the pipe loaded and visible.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from keep_task_queue_warm import seed_if_dry


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"
ACTIVE_STATUSES = {"pending", "queued", "todo", "in-progress", "in_progress"}


def load_tasks() -> list[dict[str, Any]]:
    if not TASK_FILE.exists() or not TASK_FILE.read_text(encoding="utf-8").strip():
        return []
    data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("tasks.json must contain a JSON list")
    return data


def active_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next(
        (
            task
            for task in tasks
            if str(task.get("status", "")).lower() in ACTIVE_STATUSES
        ),
        None,
    )


def is_mmi_task(task: dict[str, Any]) -> bool:
    instruction = str(task.get("instruction", ""))
    task_id = str(task.get("id", ""))
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


def reload_once() -> int:
    seed_if_dry()
    tasks = load_tasks()
    task = active_task(tasks)

    if not task:
        blocker = hold_blocker(tasks)
        if blocker:
            print("PIPE STATUS: HOLD")
            print(f"BLOCKED BY: {blocker.get('id', 'unknown')}")
            print(f"SCORE: {blocker.get('score', 'NO SCORE')}")
            print(f"GOES TO: {blocker.get('assignee', 'Matt')} ({blocker.get('tier', 'Super')})")
            print(f"WORK: {blocker.get('instruction', '')}")
            print("Bootstrap complete. Increment loop stopped. Provide phase-2 directive to seed new tasks.")
            return 0

        print("PIPE STATUS: DRY")
        print("No active task after reload. Append the next task to mmi/task_pipeline.json, then rerun.")
        return 1

    if not is_mmi_task(task):
        print("PIPE STATUS: BLOCKED")
        print(f"Non-MMI active task found: {task.get('id', 'unknown')}")
        print("Fix tasks.json before running the deployer.")
        return 2

    print("PIPE STATUS: LOADED")
    print(f"TASK: {task.get('id', 'unknown')}")
    print(f"SCORE: {task.get('score', 'NO SCORE')}")
    print(f"GOES TO: {task.get('assignee', 'UNASSIGNED')} ({task.get('tier', 'UNKNOWN TIER')})")
    print(f"WORK: {task.get('instruction', '')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--watch",
        action="store_true",
        help="keep reloading and printing the active MMI task",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=60,
        help="watch interval in seconds",
    )
    args = parser.parse_args()

    if not args.watch:
        return reload_once()

    while True:
        code = reload_once()
        if code:
            return code
        time.sleep(max(args.seconds, 5))


if __name__ == "__main__":
    raise SystemExit(main())
