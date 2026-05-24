"""Batch-test Inbox Shield against a folder of saved emails.

Usage:
    python run_against_folder.py samples

Outputs:
    outputs/inbox_shield_results.csv
    outputs/inbox_shield_results.jsonl
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from inbox_shield_langgraph import analyze_email


SUPPORTED_EXTENSIONS = {".txt", ".eml"}


def iter_email_files(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def compact_list(values: list[str]) -> str:
    return "; ".join(values)


def row_for_result(source_file: Path, result: dict[str, Any]) -> dict[str, Any]:
    risk = result["risk_analysis"]
    impersonation = result["impersonation_analysis"]
    return {
        "source_file": source_file.name,
        "recommended_action": result["recommended_action"],
        "risk_score": risk["risk_score"],
        "financial_risk": risk["financial_risk"],
        "impersonation_likelihood": impersonation["impersonation_likelihood"],
        "risk_factors": compact_list(risk["risk_factors"]),
        "phishing_signals": compact_list(risk["phishing_signals"]),
        "urgency_signals": compact_list(risk["urgency_signals"]),
        "suspicious_elements": compact_list(impersonation["suspicious_elements"]),
        "summary": result["summary"],
    }


def empty_file_result() -> dict[str, Any]:
    return {
        "summary": "No email content provided for analysis.",
        "action_items": [],
        "risk_analysis": {
            "risk_score": 0,
            "risk_factors": ["empty_sample_file"],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "low",
        },
        "impersonation_analysis": {
            "impersonation_likelihood": 0,
            "suspicious_elements": [],
            "sender_legitimacy_notes": "No email content to analyze.",
        },
        "recommended_action": "needs_review",
    }


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python run_against_folder.py path\\to\\email_folder", file=sys.stderr)
        sys.exit(2)

    input_dir = Path(sys.argv[1])
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input folder does not exist: {input_dir}", file=sys.stderr)
        sys.exit(2)

    email_files = iter_email_files(input_dir)
    if not email_files:
        print(f"No .txt or .eml files found in: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "inbox_shield_results.csv"
    jsonl_path = output_dir / "inbox_shield_results.jsonl"

    rows: list[dict[str, Any]] = []
    started_at = datetime.now(timezone.utc).isoformat()

    with jsonl_path.open("w", encoding="utf-8") as jsonl:
        for index, email_path in enumerate(email_files, start=1):
            print(f"[{index}/{len(email_files)}] analyzing {email_path.name}")
            email_text = email_path.read_text(encoding="utf-8")
            result = empty_file_result() if not email_text.strip() else analyze_email(email_text)
            rows.append(row_for_result(email_path, result))
            jsonl.write(
                json.dumps(
                    {
                        "source_file": email_path.name,
                        "started_at": started_at,
                        "result": result,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    fieldnames = [
        "source_file",
        "recommended_action",
        "risk_score",
        "financial_risk",
        "impersonation_likelihood",
        "risk_factors",
        "phishing_signals",
        "urgency_signals",
        "suspicious_elements",
        "summary",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} result(s):")
    print(f"- {csv_path}")
    print(f"- {jsonl_path}")


if __name__ == "__main__":
    main()
