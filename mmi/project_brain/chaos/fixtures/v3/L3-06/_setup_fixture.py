#!/usr/bin/env python3
"""One-time L3-06 fixture setup — staged copy only; does not touch live checklist after copy."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
LIVE = ROOT / "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md"
FX = Path(__file__).resolve().parent
BEFORE = FX / "BEFORE/opsec/OPERATOR_OPSEC_CHECKLIST.md"
FAULT = FX / "FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md"
EV = FX / "EVIDENCE"
MONITORED = ("OPSEC-4", "OPSEC-5", "OPSEC-9")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_state(text: str, item: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(f"| {item} |"):
            parts = [p.strip() for p in line.split("|")]
            return parts[6] if len(parts) >= 9 else None
    return None


def main() -> None:
    for d in (BEFORE.parent, FAULT.parent, EV):
        d.mkdir(parents=True, exist_ok=True)

    live_sha = sha256(LIVE)
    live_text = LIVE.read_text(encoding="utf-8")
    pre_states = {item: row_state(live_text, item) for item in MONITORED}

    shutil.copy2(LIVE, BEFORE)
    shutil.copy2(LIVE, FAULT)
    text = FAULT.read_text(encoding="utf-8")
    text = text.replace(
        "daily (habit) | NOT_STARTED | | Worksheet §5: self-attestation",
        "daily (habit) | DONE | | worksheet exists only — human-gate worksheet filed",
    )
    text = text.replace(
        "one-time (habit, re-affirm quarterly) | NOT_STARTED | | Worksheet §5: rule acknowledged",
        "one-time (habit, re-affirm quarterly) | DONE | 2026-06-30 | dry-run only — worksheet §6 insufficient alone",
    )
    text = text.replace(
        "one-time (habit, re-affirm quarterly) | NOT_STARTED | | Worksheet §5–§6: template + dry-run completed",
        "one-time (habit, re-affirm quarterly) | DONE | 2026-06-30 | worksheet dry-run only — no real decision log",
    )
    FAULT.write_text(text, encoding="utf-8")

    pre = {
        "live_checklist": LIVE.relative_to(ROOT).as_posix(),
        "live_sha256_pre": live_sha,
        "opsec_4_5_9_states_pre": pre_states,
        "before_copy": BEFORE.relative_to(ROOT).as_posix(),
        "fault_copy": FAULT.relative_to(ROOT).as_posix(),
    }
    (EV / "pre_check.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pre, indent=2))


if __name__ == "__main__":
    main()
