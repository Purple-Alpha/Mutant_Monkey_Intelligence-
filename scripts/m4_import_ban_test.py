#!/usr/bin/env python3
"""§17 Phase 0 — H-L8-001 import ban gate for `mmi.m4.*`."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.import_ban import scan_m4_package


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 H-L8-001 L8 import ban structural test")
    parser.add_argument(
        "--authority",
        type=Path,
        default=REPO,
        help="Authority repo root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON summary to stdout",
    )
    args = parser.parse_args()

    result = scan_m4_package(args.authority.resolve())
    summary = {
        "harness": "m4_import_ban_test",
        "phase": "17_phase_0",
        "rule": "H-L8-001",
        "package_root": result.package_root,
        "files_scanned": result.files_scanned,
        "passed": result.passed,
        "violation_count": len(result.violations),
        "violations": [
            {
                "path": v.path,
                "line_no": v.line_no,
                "rule": v.rule,
                "line": v.line,
            }
            for v in result.violations
        ],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "PASS" if result.passed else "FAIL"
        print(f"m4_import_ban_test: {status} ({result.files_scanned} files scanned)")
        for v in result.violations:
            print(f"  {v.rule} {v.path}:{v.line_no} {v.line}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
