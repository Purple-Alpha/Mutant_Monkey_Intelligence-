#!/usr/bin/env python3
"""Print the next active task with assignment and priority score."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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


def main() -> int:
    tasks = load_tasks()
    task = next(
        (
            item
            for item in tasks
            if str(item.get("status", "")).lower() in ACTIVE_STATUSES
        ),
        None,
    )
    if not task:
        print("No active task in tasks.json")
        return 0

    task_id = task.get("id", "unknown")
    assignee = task.get("assignee", "UNASSIGNED")
    tier = task.get("tier", "UNKNOWN TIER")
    score = task.get("score", "NO SCORE")
    instruction = task.get("instruction", "")

    print(f"TASK: {task_id}")
    print(f"SCORE: {score}")
    print(f"GOES TO: {assignee} ({tier})")
    print(f"WORK: {instruction}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
