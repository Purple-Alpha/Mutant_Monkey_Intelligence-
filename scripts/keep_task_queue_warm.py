#!/usr/bin/env python3
"""Keep the local task queue from going dry.

This script is intentionally deterministic. It does not call an LLM or any
external service; it only seeds bounded MMI tasks for the current active scope.

Seed order:
1. Bootstrap BACKLOG (one-time PM bootstrap tasks)
2. mmi/task_pipeline.json (ordered Phase-2+ pipeline)
3. Nothing — pipe reports DRY until pipeline file is extended
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"
PIPELINE_FILE = ROOT / "mmi" / "task_pipeline.json"

ACTIVE_STATUSES = {"pending", "queued", "todo", "in-progress", "in_progress"}
DONE_STATUSES = {"completed", "done", "cancelled", "canceled", "skipped", "paused"}

BACKLOG = [
    {
        "id": "mmi-active-scope-lock",
        "assignee": "Cursor PM",
        "tier": "Project Manager",
        "score": 100,
        "score_reason": "Highest priority because Matt clarified the active project is strictly MMI.",
        "instruction": (
            "PROJECT: MMI. Lock the current operating scope to MMI only. Update "
            "the local MMI project-brain status so Cursor PM has the task, Matt "
            "remains Super, Codex stays backbone/runtime support, Claude stays "
            "design, Gemini Paid API stays audit, Gemini stays main research, "
            "and ChatGPT stays deep/secondary research. Do not work on Social "
            "Architect Phase 1, DAX, Trades, or non-MMI lanes. Required output: "
            "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md."
        ),
        "source": "Matt directive 2026-06-28",
    },
    {
        "id": "mmi-queue-deployer-check",
        "assignee": "Cursor PM",
        "tier": "Project Manager",
        "score": 92,
        "score_reason": "High priority because the deployer must show task, score, and owner for MMI only.",
        "instruction": (
            "PROJECT: MMI. Verify the local deployer and next-task command only "
            "emit MMI tasks with task id, score, and assignee. Do not reactivate "
            "Social Architect, DAX, Trades, or old Phase 1 queue seeds. Required "
            "output: mmi/project_brain/status/MMI_DEPLOYER_QUEUE_CHECK.md."
        ),
        "source": "Matt directive 2026-06-28",
    },
    {
        "id": "mmi-next-work-packet",
        "assignee": "Cursor PM",
        "tier": "Project Manager",
        "score": 85,
        "score_reason": "Next planning task after MMI scope and queue are locked.",
        "instruction": (
            "PROJECT: MMI. Create the next MMI work packet for Cursor PM using "
            "only local MMI project-brain files and Matt directives. Keep Codex "
            "as backbone/runtime support. Required output: "
            "mmi/project_brain/status/MMI_NEXT_WORK_PACKET.md."
        ),
        "source": "Matt directive 2026-06-28",
    },
]


def load_tasks() -> list[dict[str, Any]]:
    if not TASK_FILE.exists() or not TASK_FILE.read_text(encoding="utf-8").strip():
        return []
    data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("tasks.json must contain a JSON list")
    return data


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    TASK_FILE.write_text(json.dumps(tasks, indent=4) + "\n", encoding="utf-8")


def has_active_task(tasks: list[dict[str, Any]]) -> bool:
    return any(str(task.get("status", "")).lower() in ACTIVE_STATUSES for task in tasks)


def find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any] | None:
    return next((task for task in tasks if str(task.get("id")) == task_id), None)


def already_seen(tasks: list[dict[str, Any]], task_id: str) -> bool:
    return find_task(tasks, task_id) is not None


def queue_on_hold(tasks: list[dict[str, Any]]) -> bool:
    """True when phase-2 is blocked on Matt — do not seed increment loops."""
    return any(
        str(task.get("id")) == "mmi-await-matt-phase2"
        and str(task.get("status", "")).lower() == "paused"
        for task in tasks
    )


def load_pipeline() -> list[dict[str, Any]]:
    if not PIPELINE_FILE.exists():
        return []
    data = json.loads(PIPELINE_FILE.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("mmi/task_pipeline.json must contain a tasks list")
    return tasks


def make_pending_task(item: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    return {
        "id": item["id"],
        "instruction": item["instruction"],
        "status": "pending",
        "assignee": item["assignee"],
        "tier": item["tier"],
        "score": item["score"],
        "score_reason": item.get("score_reason", "Seeded from mmi/task_pipeline.json."),
        "source": item.get("source", "mmi/task_pipeline.json"),
        "created_at": now,
        "created_by": "scripts/keep_task_queue_warm.py",
    }


def next_pipeline_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first pipeline entry that is not yet completed."""
    for item in load_pipeline():
        task_id = str(item.get("id", ""))
        if not task_id:
            continue
        existing = find_task(tasks, task_id)
        if existing is None:
            return make_pending_task(item)
        status = str(existing.get("status", "")).lower()
        if status in ACTIVE_STATUSES:
            return None
        if status in {"completed", "done"}:
            continue
        if status == "paused":
            return None
    return None


def next_backlog_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in BACKLOG:
        if not already_seen(tasks, item["id"]):
            return make_pending_task(item)

    if queue_on_hold(tasks):
        return None

    pipeline_task = next_pipeline_task(tasks)
    if pipeline_task is not None:
        return pipeline_task

    return None


def seed_if_dry() -> dict[str, Any]:
    tasks = load_tasks()
    if has_active_task(tasks):
        active = next(
            task
            for task in tasks
            if str(task.get("status", "")).lower() in ACTIVE_STATUSES
        )
        return {"changed": False, "reason": "active task exists", "task": active}

    task = next_backlog_task(tasks)
    if task is None:
        return {"changed": False, "reason": "no eligible backlog or pipeline task", "task": None}

    tasks.append(task)
    save_tasks(tasks)
    return {"changed": True, "reason": "queue was dry; seeded from pipeline", "task": task}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--peek",
        action="store_true",
        help="show the current active task or next seed without writing",
    )
    args = parser.parse_args()

    tasks = load_tasks()
    if args.peek:
        if has_active_task(tasks):
            result = {
                "changed": False,
                "reason": "active task exists",
                "task": next(
                    task
                    for task in tasks
                    if str(task.get("status", "")).lower() in ACTIVE_STATUSES
                ),
            }
        else:
            result = {
                "changed": False,
                "reason": "queue is dry; next seed preview",
                "task": next_backlog_task(tasks),
            }
    else:
        result = seed_if_dry()

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
