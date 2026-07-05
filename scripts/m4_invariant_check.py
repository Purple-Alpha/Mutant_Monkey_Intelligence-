#!/usr/bin/env python3
"""§17 Phase 1 — formal invariant static/live checks (INV-1..7)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.invariants import run_live_suite, run_static_suite, suite_passed


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 formal invariant suite §5")
    parser.add_argument(
        "--phase",
        choices=("static", "live"),
        default="static",
        help="static = Phase 1 gate; live = Phase 4+ (stub until boundary exists)",
    )
    parser.add_argument(
        "--authority",
        type=Path,
        default=REPO,
        help="Authority repo root",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    authority = args.authority.resolve()
    if args.phase == "static":
        results = run_static_suite(authority)
    else:
        results = run_live_suite(authority)

    summary = {
        "harness": "m4_invariant_check",
        "phase": f"17_phase_1_{args.phase}",
        "spec_section": "§5",
        "passed": suite_passed(results),
        "results": [
            {
                "invariant_id": r.invariant_id,
                "phase": r.phase,
                "passed": r.passed,
                "violation_count": len(r.violations),
                "note": r.note,
                "violations": [
                    {
                        "path": v.path,
                        "line_no": v.line_no,
                        "detail": v.detail,
                    }
                    for v in r.violations
                ],
            }
            for r in results
        ],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "PASS" if summary["passed"] else "FAIL"
        print(f"m4_invariant_check ({args.phase}): {status}")
        for r in results:
            mark = "PASS" if r.passed else "FAIL"
            print(f"  {r.invariant_id}: {mark}")
            for v in r.violations:
                print(f"    {v.path}:{v.line_no} {v.detail}")

    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
