#!/usr/bin/env python3
"""Read-only local MMI war room panel for monitor 2."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import command_center


ROOT = Path(__file__).resolve().parents[1]
BACKUP_LOG_FILE = ROOT / "mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json"

LANE_MAP = [
    ("Super", "Matt", "Product direction, build auth, GATED decisions"),
    ("PM", "Cursor", "Queue, routing, status, task hygiene"),
    ("Backbone / runtime", "Codex", "Scripts, diagnostics, backup, war room code"),
    ("Design", "Claude", "Architecture/spec tasks when assigned"),
    ("Audit", "Gemini Paid API", "Audit/gate checks when assigned"),
    ("Main research", "Gemini", "Primary research when assigned"),
    ("Deep research", "ChatGPT", "Source verification and deeper research when assigned"),
]

BRAIN_LINKS = [
    ("Scope", "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md"),
    ("Local/cloud policy", "mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md"),
    ("Phase start", "mmi/project_brain/status/MMI_PHASE2_START.md"),
    ("Routing", "mmi/project_brain/status/MMI_LANE_ROUTING.md"),
    ("War room spec", "mmi/project_brain/architecture/MMI_WAR_ROOM_SPEC.md"),
    ("War room setup", "mmi/project_brain/status/MMI_WAR_ROOM_SETUP.md"),
]

CHEATSHEET = [
    ("Reload pipe", "python scripts/reload_mmi_pipes.py"),
    ("War room watch", "python mmi/war_room.py --watch --seconds 30"),
    (
        "Complete task",
        'python scripts/complete_task.py TASK_ID --by "Codex" --summary "..." --output path/to/file',
    ),
    ("Cold backup push", "python scripts/mmi_cold_backup.py --backup-and-push"),
    ("Command center fallback", "python mmi/command_center.py --watch --seconds 30"),
]


def read_json_file(path: Path) -> tuple[Any | None, str | None]:
    if not path.exists():
        return None, f"{path.relative_to(ROOT)} not found"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path.relative_to(ROOT)} invalid JSON: {exc}"


def backup_status() -> dict[str, Any]:
    data, error = read_json_file(BACKUP_LOG_FILE)
    if error:
        return {"status": "UNKNOWN", "error": error, "last_push": None}
    if not isinstance(data, list) or not data:
        return {"status": "NONE", "error": None, "last_push": None}

    last = data[-1]
    if not isinstance(last, dict):
        return {"status": "BLOCKED", "error": "last backup log entry is not an object", "last_push": None}

    return {
        "status": str(last.get("push_status", "UNKNOWN")),
        "error": None,
        "last_push": {
            "created_at": last.get("created_at"),
            "archive": last.get("archive"),
            "archive_bytes": last.get("archive_bytes"),
            "push_remote": last.get("push_remote"),
            "push_file": last.get("push_file"),
            "remote_bytes": last.get("remote_bytes"),
            "push_errors": last.get("push_errors", []),
        },
    }


def lane_map() -> list[dict[str, str]]:
    return [{"lane": lane, "owner": owner, "does": does} for lane, owner, does in LANE_MAP]


def operator_cheatsheet() -> list[dict[str, str]]:
    return [{"label": label, "command": command} for label, command in CHEATSHEET]


def brain_links() -> list[dict[str, str]]:
    return [{"label": label, "path": path} for label, path in BRAIN_LINKS]


def build_state(auto_seed: bool = False) -> dict[str, Any]:
    pipe = command_center.build_state(auto_seed=auto_seed)
    return {
        "panel": "MMI WAR ROOM",
        "read_only": True,
        "auto_seed": auto_seed,
        "pipe": pipe,
        "lane_map": lane_map(),
        "backup": backup_status(),
        "operator": operator_cheatsheet(),
        "project_brain": brain_links(),
    }


def render_backup(backup: dict[str, Any]) -> list[str]:
    lines = ["BACKUP"]
    last = backup.get("last_push")
    if not last:
        lines.append(f"  STATUS: {backup.get('status', 'UNKNOWN')}")
        if backup.get("error"):
            lines.append(f"  ERROR:  {backup['error']}")
        return lines

    lines.extend(
        [
            f"  STATUS:       {backup.get('status', 'UNKNOWN')}",
            f"  LAST PUSH:    {last.get('created_at', 'unknown')}",
            f"  ARCHIVE:      {last.get('archive', 'unknown')}",
            f"  LOCAL BYTES:  {last.get('archive_bytes', 'unknown')}",
            f"  REMOTE:       {last.get('push_remote', 'unknown')}{last.get('push_file', '')}",
            f"  REMOTE BYTES: {last.get('remote_bytes', 'unknown')}",
        ]
    )
    errors = last.get("push_errors") or []
    if errors:
        lines.append(f"  ERRORS:       {errors}")
    return lines


def render_text(state: dict[str, Any]) -> str:
    pipe = state["pipe"]
    active = pipe.get("active_task")
    lines = [
        "MMI WAR ROOM",
        f"PIPE STATUS: {pipe['pipe_status']}",
        f"READ ONLY:   {state['read_only']}",
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

    blockers = pipe.get("blockers") or []
    if blockers:
        lines.append("BLOCKERS")
        lines.extend(f"  {blocker}" for blocker in blockers)
        lines.append("")

    lines.extend(["NEXT ACTION", f"  {pipe['next_action']}", ""])

    lines.append("LANE MAP")
    for lane in state["lane_map"]:
        lines.append(f"  {lane['lane']}: {lane['owner']} — {lane['does']}")
    lines.append("")

    lines.extend(render_backup(state["backup"]))
    lines.append("")

    lines.append("OPERATOR")
    for item in state["operator"]:
        lines.append(f"  {item['label']}: {item['command']}")
    lines.append("")

    lines.append("PROJECT BRAIN")
    for link in state["project_brain"]:
        lines.append(f"  {link['label']}: {link['path']}")

    return "\n".join(lines)


def render_json(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2)


def print_once(as_json: bool, auto_seed: bool) -> None:
    state = build_state(auto_seed=auto_seed)
    print(render_json(state) if as_json else render_text(state), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable state")
    parser.add_argument("--watch", action="store_true", help="refresh panel on an interval")
    parser.add_argument("--seconds", type=int, default=30, help="watch interval in seconds")
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="compatibility flag; war room is read-only and does not seed by default",
    )
    args = parser.parse_args()

    auto_seed = False
    if not args.watch:
        print_once(args.json, auto_seed=auto_seed)
        return 0

    interval = max(args.seconds, 5)
    while True:
        print_once(args.json, auto_seed=auto_seed)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
