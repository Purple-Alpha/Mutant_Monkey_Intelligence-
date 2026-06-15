#!/usr/bin/env python3
"""MMI advisory preflight.

Runs the existing build-truth verifier plus the cross-artifact drift detector as
one repeatable preflight command. This is an evidence lens, not a gate:

  - it does not edit files,
  - it does not promote findings,
  - it does not call the dispatcher,
  - it always exits 0 unless this wrapper itself crashes.

Use before a build/review session to see whether committed truth and routing
inputs are aligned enough to trust the next MMI action.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_step(title: str, command: list[str]) -> int:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.stderr:
        print(proc.stderr, end="" if proc.stderr.endswith("\n") else "\n")
    print(f"[preflight] step exit code: {proc.returncode} (advisory)")
    return proc.returncode


def main() -> int:
    print("=" * 72)
    print("MMI PREFLIGHT  (advisory evidence; not a dispatcher gate)")
    print("=" * 72)
    print(f"repo: {REPO_ROOT}")
    print()
    print("Lab rule: every artifact must improve detection, evidence, governance,")
    print("insurance value, or attacker-cost economics. Preflight reports evidence;")
    print("Matt/MMI still decide direction.")

    results = [
        run_step(
            "1. BUILD TRUTH (docs vs code/git reality)",
            [sys.executable, "scripts/verify_build_truth.py"],
        ),
        run_step(
            "2. PROJECT DRIFT (cross-artifact + dispatcher-input integrity)",
            [sys.executable, "scripts/detect_drift.py", "--quiet"],
        ),
    ]

    print()
    print("=" * 72)
    print("PREFLIGHT SUMMARY")
    print("=" * 72)
    print(
        "Underlying step exit codes: "
        + ", ".join(str(code) for code in results)
        + " (reported, not enforced)"
    )
    print("Wrapper exit: 0 (advisory-only; no hard stop)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
