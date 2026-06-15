#!/usr/bin/env python3
"""Runtime instrumentation CLI.

Examples:
    python instrumentation/run_instrumentation.py --category bec --count 10
    python instrumentation/run_instrumentation.py --all-categories --count 10
    python instrumentation/run_instrumentation.py --report <run_id>
    python instrumentation/run_instrumentation.py --email-id bec-001 --trace
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from instrumentation.runtime import (
    CATEGORIES,
    DEFAULT_OUTPUT_ROOT,
    load_report,
    render_report,
    run_corpus,
)


def _latest_trace_for_email(email_id: str, output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    matches = sorted(
        output_root.glob(f"*/per_email/{email_id}_telemetry.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise SystemExit(f"no telemetry found for email_id={email_id!r}")
    run_dir = matches[0].parents[1]
    traces = sorted((run_dir / "worst_case_traces").glob("*_worst_case.txt"))
    if not traces:
        raise SystemExit(f"no worst-case trace found for run {run_dir.name}")
    return traces[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local-only runtime instrumentation")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--category", choices=CATEGORIES)
    mode.add_argument("--all-categories", action="store_true")
    mode.add_argument("--report")
    mode.add_argument("--email-id")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    if args.count < 1:
        raise SystemExit("--count must be >= 1")

    if args.report:
        print(render_report(load_report(args.report, args.output_root)))
        return 0

    if args.email_id:
        if not args.trace:
            raise SystemExit("--email-id currently requires --trace")
        print(_latest_trace_for_email(args.email_id, args.output_root).read_text(encoding="utf-8"))
        return 0

    categories = CATEGORIES if args.all_categories else (args.category,)
    for category in categories:
        report, output_dir = run_corpus(
            category=category,
            count=args.count,
            output_root=args.output_root,
        )
        trace_path = output_dir / "worst_case_traces" / f"{category}_worst_case.txt"
        print(f"run_id={report.run_id}")
        print(f"category={category}")
        print(f"aggregate_report={output_dir / 'aggregate_report.json'}")
        print(f"worst_case_trace={trace_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

