#!/usr/bin/env python3
"""Persist ranked next-action lanes to disk and pin handshake.

Runs the read-only Next-Action Rubric, writes mmi/MMI_RANKED_NEXT_ACTIONS.md,
and updates PROJECT_HANDSHAKE.md CURRENT NEXT ACTION block so cold sessions
read ranked lanes without re-asking in chat.

Does not select a lane, authorize build, or mutate scoreboard/BOR lifecycle.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RANKED_REL = "mmi/MMI_RANKED_NEXT_ACTIONS.md"
HANDSHAKE_REL = "PROJECT_HANDSHAKE.md"


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
    return path.read_text(encoding="utf-8")


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
    state_path = root / "MMI_CURRENT_STATE.md"
    if not state_path.is_file():
        return "UNKNOWN"
    for line in _read_text(state_path).splitlines():
        if line.startswith("MODE:"):
            return line.split(":", 1)[1].strip()
        if line.strip() == "":
            break
    return "UNKNOWN"


def build_ranked_board(root: Path, limit: int = 7) -> str:
    rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
    scored = rubric.analyze(root, limit=limit)
    mode = _dispatcher_mode(root)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = _git_head(root)
    body = rubric.format_markdown(scored, mode)
    header = (
        f"generated_at: {stamp}\n"
        f"git_head: {head}\n"
        f"generator: scripts/mmi_lane_board_sync.py\n"
    )
    return header + "\n" + body


def _patch_handshake(handshake_text: str, top_label: str, top_total: str) -> str:
    replacement = (
        "NEXT ACTION: Read ranked lanes on disk — rubric ranks; Matt selects one. "
        f"Top ranked ({top_total}/10): {top_label}. "
        f"Full list: `{RANKED_REL}` (refresh: `python3 scripts/mmi_lane_board_sync.py`)."
    )
    next_action_re = re.compile(r"^NEXT ACTION:.*$", re.MULTILINE)
    if next_action_re.search(handshake_text):
        return next_action_re.sub(replacement, handshake_text, count=1)
    return handshake_text


def sync(root: Path, limit: int = 7, handshake: bool = True) -> tuple[Path, str, str]:
    ranked_path = root / RANKED_REL
    ranked_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_ranked_board(root, limit=limit)
    ranked_path.write_text(content, encoding="utf-8")

    rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
    rows = rubric.parse_ranked_markdown(content)
    top_label = rows[0]["label"] if rows else "Hold ALL_CLEAR"
    top_total = rows[0].get("total", "?") if rows else "3"

    if handshake:
        hs_path = root / HANDSHAKE_REL
        if hs_path.is_file():
            updated = _patch_handshake(_read_text(hs_path), top_label, top_total)
            hs_path.write_text(updated, encoding="utf-8")

    return ranked_path, top_label, top_total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write ranked next-action board + optional handshake pin."
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=7)
    parser.add_argument(
        "--no-handshake",
        action="store_true",
        help="Write ranked board only; do not patch PROJECT_HANDSHAKE.md",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else _repo_root()
    ranked_path, top_label, top_total = sync(
        root, limit=args.limit, handshake=not args.no_handshake
    )
    print(f"LANE_BOARD_SYNC: wrote {ranked_path.relative_to(root)}")
    print(f"top_ranked_total: {top_total}")
    print(f"top_ranked_label: {top_label}")
    print("authority: rubric ranks; Matt selects; not authorization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
