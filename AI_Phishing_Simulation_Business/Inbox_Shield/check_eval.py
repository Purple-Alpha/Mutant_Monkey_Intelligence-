"""Compare Inbox Shield batch results against expected outcomes.

Reads:
    outputs/inbox_shield_results.jsonl  (produced by run_against_folder.py)
    samples/expected_results.csv        (one row per labelled sample)

Prints per-sample pass/fail, totals, false positives, missed fraud, and exits
with a non-zero status if any expectation is unmet so this can also gate CI.

Usage:
    python check_eval.py
    python check_eval.py --results outputs/inbox_shield_results.jsonl --expected samples/expected_results.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("outputs/inbox_shield_results.jsonl"),
        help="Path to JSONL output from run_against_folder.py.",
    )
    parser.add_argument(
        "--expected",
        type=Path,
        default=Path("samples/expected_results.csv"),
        help="Path to expected_results.csv contract.",
    )
    return parser.parse_args()


def load_results(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        print(f"Results file not found: {path}", file=sys.stderr)
        sys.exit(2)

    results: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            source = record["source_file"]
            results[source] = record["result"]
    return results


def load_expected(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        print(f"Expected file not found: {path}", file=sys.stderr)
        sys.exit(2)

    expected: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            expected.append(
                {
                    "sample": row["sample"].strip(),
                    "risk_min": int(row["risk_min"].strip()),
                    "allowed_actions": {
                        action.strip()
                        for action in row["allowed_actions"].split("|")
                        if action.strip()
                    },
                    "is_fraud": row["is_fraud"].strip().lower() == "true",
                }
            )
    return expected


def evaluate(
    expected: list[dict[str, Any]],
    results: dict[str, dict[str, Any]],
) -> tuple[bool, dict[str, int]]:
    overall_pass = True
    counts = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "missing_result": 0,
        "false_positives": 0,
        "missed_fraud": 0,
    }

    print(f"{'sample':40} {'expected':28} {'actual':22} {'risk':4} {'verdict':8}")
    print("-" * 110)

    for row in expected:
        sample = row["sample"]
        counts["total"] += 1
        result = results.get(sample)
        if result is None:
            counts["missing_result"] += 1
            counts["failed"] += 1
            overall_pass = False
            print(
                f"{sample:40} "
                f"{'(any of) ' + '|'.join(sorted(row['allowed_actions'])):28} "
                f"{'<missing>':22} {'?':>4} {'FAIL':8}"
            )
            continue

        actual_action = result["recommended_action"]
        actual_risk = int(result["risk_analysis"]["risk_score"])
        action_ok = actual_action in row["allowed_actions"]
        risk_ok = actual_risk >= row["risk_min"]
        sample_ok = action_ok and risk_ok

        if not sample_ok:
            overall_pass = False
            counts["failed"] += 1
            if row["is_fraud"] and actual_action == "safe":
                counts["missed_fraud"] += 1
            if not row["is_fraud"] and actual_action == "block":
                counts["false_positives"] += 1
        else:
            counts["passed"] += 1

        verdict = "PASS" if sample_ok else "FAIL"
        print(
            f"{sample:40} "
            f"{'>=' + str(row['risk_min']) + ', ' + '|'.join(sorted(row['allowed_actions'])):28} "
            f"{actual_action:22} {actual_risk:>4} {verdict:8}"
        )

    return overall_pass, counts


def main() -> None:
    args = parse_args()
    expected = load_expected(args.expected)
    results = load_results(args.results)
    overall_pass, counts = evaluate(expected, results)

    print()
    print("Summary")
    print(f"  total           : {counts['total']}")
    print(f"  passed          : {counts['passed']}")
    print(f"  failed          : {counts['failed']}")
    print(f"  missing results : {counts['missing_result']}")
    print(f"  false positives : {counts['false_positives']}")
    print(f"  missed fraud    : {counts['missed_fraud']}")
    print()
    print("RESULT:", "ALL EXPECTATIONS MET" if overall_pass else "EXPECTATIONS NOT MET")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
