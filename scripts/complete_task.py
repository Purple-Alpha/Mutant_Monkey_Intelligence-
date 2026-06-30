#!/usr/bin/env python3
"""Mark an MMI task completed and auto-seed the next pipeline task if dry."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from keep_task_queue_warm import seed_if_dry


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"


def load_tasks() -> list[dict[str, Any]]:
    data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("tasks.json must contain a JSON list")
    return data


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    TASK_FILE.write_text(json.dumps(tasks, indent=4) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id", help="task id to mark completed")
    parser.add_argument("--by", required=True, help="completed_by value")
    parser.add_argument("--summary", required=True, help="result_summary")
    parser.add_argument(
        "--output",
        action="append",
        default=[],
        dest="outputs",
        help="output file path (repeatable)",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="do not auto-seed next pipeline task after completion",
    )
    args = parser.parse_args()

    tasks = load_tasks()
    task = next((item for item in tasks if str(item.get("id")) == args.task_id), None)
    if task is None:
        print(f"Task not found: {args.task_id}")
        return 1

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    task["status"] = "completed"
    task["completed_at"] = now
    task["completed_by"] = args.by
    task["result_summary"] = args.summary
    if args.outputs:
        task["output_files"] = args.outputs

    save_tasks(tasks)
    print(f"Completed: {args.task_id}")

    if args.no_seed:
        return 0

    result = seed_if_dry()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
