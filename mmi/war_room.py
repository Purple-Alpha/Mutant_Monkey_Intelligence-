#!/usr/bin/env python3
"""Read-only local MMI war room panel for monitor 2."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import command_center


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"
BACKUP_LOG_FILE = ROOT / "mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json"
LATEST_GOOD_FILE = ROOT / "mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md"
LATEST_GOOD_VALIDATION_FILE = ROOT / "mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md"
OPSEC_CHECKLIST_FILE = ROOT / "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md"
L3_04_REPORT = ROOT / "mmi/project_brain/chaos/MMI_CHAOS_L3-04_INTEL_HEADLINE_LAUNDERING_2026-07.md"
L3_06_REPORT = ROOT / "mmi/project_brain/chaos/MMI_CHAOS_L3-06_OPSEC_FALSE_DONE_2026-07.md"
LEVEL3_PLAN = ROOT / "mmi/project_brain/chaos/MMI_CHAOS_LEVEL3_PLAN_2026-07.md"

SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mmi_verify import verify_all_intel_briefs  # noqa: E402

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
    ("Path authority", "mmi/project_brain/status/MMI_PATH_AUTHORITY.md"),
    ("Scoring matrix (v2)", "mmi/project_brain/intel/WAR_ROOM_SCORING_MATRIX_v2.md"),
    ("Research rigor", "mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md"),
    ("Local/cloud policy", "mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md"),
    ("War room spec", "mmi/project_brain/architecture/MMI_WAR_ROOM_SPEC.md"),
    ("War room setup", "mmi/project_brain/status/MMI_WAR_ROOM_SETUP.md"),
    ("Canadian IR fit", "mmi/project_brain/status/MMI_CANADIAN_IR_FIT.md"),
    ("Routing", "mmi/project_brain/status/MMI_LANE_ROUTING.md"),
]

CHEATSHEET = [
    ("Reload pipe", "python scripts/reload_mmi_pipes.py"),
    ("War room watch", "python mmi/war_room.py --watch --seconds 30"),
    (
        "Complete task",
        'python scripts/complete_task.py TASK_ID --by "Codex" --summary "..." --output path/to/file --report-card path/to/report_card.md',
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


def read_text_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def archive_name(value: str | None) -> str:
    if not value:
        return "unknown"
    return Path(value).name


def task_build_authorization(active_task: dict[str, Any] | None) -> str:
    if not active_task:
        return "NONE"
    active_id = str(active_task.get("id", ""))
    tasks, error = read_json_file(TASK_FILE)
    if error or not isinstance(tasks, list):
        return "UNKNOWN"
    for task in tasks:
        if isinstance(task, dict) and str(task.get("id", "")) == active_id:
            return str(task.get("build_authorization", "NOT_AUTHORIZED"))
    return "UNKNOWN"


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
            "archive_name": archive_name(last.get("archive") or last.get("push_file")),
            "archive_bytes": last.get("archive_bytes"),
            "push_remote": last.get("push_remote"),
            "push_file": last.get("push_file"),
            "remote_bytes": last.get("remote_bytes"),
            "push_errors": last.get("push_errors", []),
        },
    }


def restore_status() -> dict[str, str]:
    latest_good = read_text_file(LATEST_GOOD_FILE)
    validation = read_text_file(LATEST_GOOD_VALIDATION_FILE)

    archive = "unknown"
    archive_match = re.search(r"\|\s+\*\*Archive name\*\*\s+\|\s+`([^`]+)`\s+\|", latest_good)
    if archive_match:
        archive = archive_match.group(1)

    validation_target = "unknown"
    target_match = re.search(r"\*\*Target archive:\*\*\s+`([^`]+)`", validation)
    if target_match:
        validation_target = target_match.group(1)

    status = "UNKNOWN"
    if re.search(r"\*\*PASS\*\*", validation):
        suffix = validation_target.removeprefix("mmi_backup_").removesuffix(".tar.gz")
        suffix = suffix.split("_")[-1] if "_" in suffix else suffix
        status = f"PASS for {suffix}"

    return {
        "restore_proven": archive if archive != "unknown" else validation_target,
        "restore_check": status,
    }


def opsec_known_risk() -> dict[str, Any]:
    content = read_text_file(OPSEC_CHECKLIST_FILE)
    states: dict[str, str] = {}
    for item_id in ("OPSEC-4", "OPSEC-5", "OPSEC-9"):
        prefix = f"| {item_id} |"
        state = "UNKNOWN"
        for line in content.splitlines():
            if line.startswith(prefix):
                parts = [part.strip() for part in line.split("|")]
                if len(parts) >= 7:
                    state = parts[6]
                break
        states[item_id] = state

    all_not_started = all(state == "NOT_STARTED" for state in states.values())
    return {
        "summary": "OPSEC-4/5/9 NOT_STARTED" if all_not_started else f"OPSEC-4/5/9 states {states}",
        "known_operator_risk": all_not_started,
        "states": states,
    }


def intel_gate_status() -> dict[str, Any]:
    result = verify_all_intel_briefs()
    clean = bool(result.get("ok"))
    scanned = result.get("briefs_scanned", 0)
    return {
        "summary": "P2 / G-INTEL active; live briefs clean" if clean else "P2 / G-INTEL active; live briefs need review",
        "ok": clean,
        "briefs_scanned": scanned,
        "failed": result.get("failed", 0),
    }


def chaos_status() -> dict[str, str]:
    l3_04 = "complete" if L3_04_REPORT.exists() else "missing"
    l3_06 = "complete" if L3_06_REPORT.exists() else "missing"
    plan = read_text_file(LEVEL3_PLAN)
    l3_05 = "paused" if "Level 3 execution NOT authorized" in plan or "L3-05" in plan else "unknown"
    level4 = "prohibited" if "Level 4 PROHIBITED" in plan or "Level 4" in plan else "unknown"
    if l3_04 == "complete" and l3_06 == "complete":
        summary = "L3-06 + L3-04 complete + mirrored; L3-05 paused; Level 4 prohibited"
    else:
        summary = f"L3-06 {l3_06}; L3-04 {l3_04}; L3-05 {l3_05}; Level 4 {level4}"
    return {
        "summary": summary,
        "l3_06": l3_06,
        "l3_04": l3_04,
        "l3_05": l3_05,
        "level4": level4,
    }


def lane_map() -> list[dict[str, str]]:
    return [{"lane": lane, "owner": owner, "does": does} for lane, owner, does in LANE_MAP]


def operator_cheatsheet() -> list[dict[str, str]]:
    return [{"label": label, "command": command} for label, command in CHEATSHEET]


def brain_links() -> list[dict[str, str]]:
    return [{"label": label, "path": path} for label, path in BRAIN_LINKS]


def build_state(auto_seed: bool = False) -> dict[str, Any]:
    pipe = command_center.build_state(auto_seed=auto_seed)
    active = pipe.get("active_task")
    build_auth = task_build_authorization(active)
    pipe["build_authorization"] = build_auth
    if active:
        active["build_authorization"] = build_auth
        if build_auth == "NOT_AUTHORIZED" and str(active.get("assignee")) == "Codex":
            pipe["next_action"] = "Awaiting Matt build authorization for Codex."
    return {
        "panel": "MMI WAR ROOM",
        "read_only": True,
        "auto_seed": auto_seed,
        "pipe": pipe,
        "lane_map": lane_map(),
        "backup": backup_status(),
        "restore": restore_status(),
        "opsec": opsec_known_risk(),
        "intel": intel_gate_status(),
        "chaos": chaos_status(),
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
                f"  BUILD AUTH: {active.get('build_authorization', pipe.get('build_authorization', 'UNKNOWN'))}",
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

    latest = state["backup"].get("last_push") or {}
    restore = state["restore"]
    lines.extend(
        [
            "TRUTH SURFACE",
            f"  BUILD AUTH:        {pipe.get('build_authorization', 'UNKNOWN')}",
            f"  LATEST B2 MIRROR:  {latest.get('archive_name', 'unknown')}",
            f"  RESTORE-PROVEN:    {restore.get('restore_proven', 'unknown')}",
            f"  RESTORE-CHECK:     {restore.get('restore_check', 'UNKNOWN')}",
            f"  OPSEC KNOWN RISK:  {state['opsec']['summary']}",
            f"  INTEL GATES:       {state['intel']['summary']}",
            f"  CHAOS:             {state['chaos']['summary']}",
            "  NOTE: Latest B2 mirror != restore-validated archive unless restore-check passed.",
            "  NOTE: Seeded/pending != build authorization.",
            "",
        ]
    )

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
