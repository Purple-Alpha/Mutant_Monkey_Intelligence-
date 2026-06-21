#!/usr/bin/env python3
"""MMI handoff log writer — append-only handoff lines.

Each model/worker appends exactly one line per call. No edits. No deletes.

Authority: MMI handoff signal loop (Matt §11 2026-06-20).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

HANDOFF_LOG_REL = "mmi/MMI_HANDOFF_LOG.md"
OPEN_STATE_PREFIX = "DONE_AWAITING_"
VALID_STATES = frozenset(
    {
        "DONE_AWAITING_CLOSEOUT",
        "DONE_AWAITING_GATE",
        "DONE_AWAITING_SIGN",
        "DONE_AWAITING_REVIEW",
        "DONE_AWAITING_MATT",
        "DONE_CLOSED",
    }
)
FIELD_ORDER = ("ts", "task", "by", "did", "state", "next_step", "evidence")
LINE_PREFIX = "ts="
DATA_LINE_RE = re.compile(
    r"^ts=(?P<ts>\S+)\s*\|\s*task=(?P<task>[^|]+)\s*\|\s*by=(?P<by>[^|]+)"
    r"\s*\|\s*did=(?P<did>[^|]+)\s*\|\s*state=(?P<state>[^|]+)"
    r"\s*\|\s*next_step=(?P<next_step>[^|]+)\s*\|\s*evidence=(?P<evidence>.+)\s*$"
)


@dataclass(frozen=True)
class HandoffEntry:
    ts: str
    task: str
    by: str
    did: str
    state: str
    next_step: str
    evidence: str

    @property
    def is_open(self) -> bool:
        return self.state.startswith(OPEN_STATE_PREFIX)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def handoff_log_path(root: Path) -> Path:
    return root / HANDOFF_LOG_REL


def _sanitize_field(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    if "|" in cleaned:
        raise ValueError(f"{field_name} must not contain '|'")
    if field_name == "state" and cleaned not in VALID_STATES:
        raise ValueError(f"invalid state: {cleaned}")
    return cleaned


def format_line(
    task: str,
    by: str,
    did: str,
    state: str,
    next_step: str,
    evidence: str,
    ts: str | None = None,
) -> str:
    payload = {
        "ts": ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": _sanitize_field(task, "task"),
        "by": _sanitize_field(by, "by"),
        "did": _sanitize_field(did, "did"),
        "state": _sanitize_field(state, "state"),
        "next_step": _sanitize_field(next_step, "next_step"),
        "evidence": _sanitize_field(evidence, "evidence"),
    }
    return " | ".join(f"{key}={payload[key]}" for key in FIELD_ORDER)


def parse_line(line: str) -> HandoffEntry | None:
    stripped = line.strip()
    if not stripped.startswith(LINE_PREFIX):
        return None
    match = DATA_LINE_RE.match(stripped)
    if not match:
        return None
    groups = match.groupdict()
    return HandoffEntry(
        ts=groups["ts"].strip(),
        task=groups["task"].strip(),
        by=groups["by"].strip(),
        did=groups["did"].strip(),
        state=groups["state"].strip(),
        next_step=groups["next_step"].strip(),
        evidence=groups["evidence"].strip(),
    )


def read_entries(root: Path) -> list[HandoffEntry]:
    path = handoff_log_path(root)
    if not path.is_file():
        return []
    entries: list[HandoffEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_line(line)
        if parsed is not None:
            entries.append(parsed)
    return entries


def latest_open_handoff(root: Path) -> HandoffEntry | None:
    entries = read_entries(root)
    if not entries:
        return None
    latest_by_task: dict[str, HandoffEntry] = {}
    for entry in entries:
        latest_by_task[entry.task] = entry
    last_open: HandoffEntry | None = None
    for entry in entries:
        latest = latest_by_task[entry.task]
        if latest.is_open and latest is entry:
            last_open = entry
    return last_open


def append_handoff(
    root: Path,
    task: str,
    by: str,
    did: str,
    state: str,
    next_step: str,
    evidence: str,
    ts: str | None = None,
) -> str:
    path = handoff_log_path(root)
    if not path.is_file():
        raise FileNotFoundError(f"missing handoff log: {HANDOFF_LOG_REL}")
    line = format_line(task, by, did, state, next_step, evidence, ts=ts)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return line


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append one handoff line to mmi/MMI_HANDOFF_LOG.md (append-only)."
    )
    parser.add_argument("--append", action="store_true", help="Append one handoff line")
    parser.add_argument("--task", required=True)
    parser.add_argument("--by", required=True)
    parser.add_argument("--did", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--next-step", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--ts", default=None, help="Optional ISO-8601 timestamp")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.append:
        parser.error("--append is required")

    root = args.root.resolve() if args.root else _repo_root()
    line = append_handoff(
        root,
        task=args.task,
        by=args.by,
        did=args.did,
        state=args.state,
        next_step=args.next_step,
        evidence=args.evidence,
        ts=args.ts,
    )
    sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
