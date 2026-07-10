#!/usr/bin/env python3
"""Validate MMI report-card grade math before task closeout."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


GRADE_PATTERN = re.compile(
    r"^\s*-\s*(?:target_artifact_grade_label|grade_label|LETTER_GRADE|letter_grade)\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
LETTER_MARK_PATTERN = re.compile(
    r"^\s*-\s*(?:letter_grade_mark|LETTER_GRADE_MARK)\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
RUBRIC_PATTERN = re.compile(r"rubric_scores\s*:\s*\[(.*?)\]", re.IGNORECASE | re.DOTALL)
CRITICAL_PATTERN = re.compile(
    r"^\s*-\s*critical_criteria_results\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
LOWEST_RULE_PATTERN = re.compile(
    r"^\s*-\s*lowest_score_rule_applied\s*:\s*(YES|NO)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
AVERAGING_PATTERN = re.compile(
    r"^\s*-\s*averaging_used\s*:\s*(YES|NO)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
REQUIRED_FIELD_PATTERNS = {
    "criterion_feedback": re.compile(r"^\s*-\s*criterion_feedback\s*:", re.IGNORECASE | re.MULTILINE),
    "improvement_targets": re.compile(r"improvement_targets?\s*:", re.IGNORECASE),
    "reviewer_identity": re.compile(r"^\s*-\s*(?:grader_id|reviewer_id|auditor_id|producer_id)\s*:", re.IGNORECASE | re.MULTILINE),
    "target_artifact": re.compile(r"^\s*-\s*target_artifact\s*:", re.IGNORECASE | re.MULTILINE),
    "acceptance_status": re.compile(
        r"^\s*-\s*(?:review_artifact_acceptance_status|acceptance_status)\s*:",
        re.IGNORECASE | re.MULTILINE,
    ),
    "verification_mode": re.compile(
        r"^\s*-\s*(?:hash_verification_mode|verification_mode|hash_recomputation_status)\s*:",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def normalize_grade(raw: str | None) -> str | None:
    if raw is None:
        return None
    value = raw.strip().strip("`").upper()
    value = re.sub(r"\s+", "_", value)
    value = value.replace("/", "_").replace("-", "_")
    value = re.sub(r"_+", "_", value).strip("_")
    if value.startswith("F"):
        return "F_BLOCKED"
    if value in {"A", "B", "C", "D"}:
        return value
    return value


def _parse_score_pairs(blob: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for name, score in re.findall(r"([A-Za-z0-9_ /-]+?)\s*(?:[:=])\s*([0-3])\b", blob):
        normalized_name = re.sub(r"\s+", " ", name.strip(" -")).lower()
        if normalized_name:
            scores[normalized_name] = int(score)
    return scores


def parse_report_card(text: str) -> dict[str, Any]:
    grade_match = GRADE_PATTERN.search(text)
    letter_mark_match = LETTER_MARK_PATTERN.search(text)
    rubric_match = RUBRIC_PATTERN.search(text)
    critical_match = CRITICAL_PATTERN.search(text)
    lowest_rule_match = LOWEST_RULE_PATTERN.search(text)
    averaging_match = AVERAGING_PATTERN.search(text)

    return {
        "actual_grade": normalize_grade(grade_match.group(1)) if grade_match else None,
        "letter_grade_mark": normalize_grade(letter_mark_match.group(1)) if letter_mark_match else None,
        "rubric_scores": _parse_score_pairs(rubric_match.group(1)) if rubric_match else {},
        "critical_scores": _parse_score_pairs(critical_match.group(1)) if critical_match else {},
        "lowest_score_rule_applied": lowest_rule_match.group(1).upper() if lowest_rule_match else None,
        "averaging_used": averaging_match.group(1).upper() if averaging_match else None,
        "required_fields": {
            name: pattern.search(text) is not None for name, pattern in REQUIRED_FIELD_PATTERNS.items()
        },
    }


def expected_grade(rubric_scores: dict[str, int], critical_scores: dict[str, int]) -> str | None:
    if critical_scores and any(score < 3 for score in critical_scores.values()):
        return "F_BLOCKED"
    if rubric_scores and any(score == 0 for score in rubric_scores.values()):
        return "F_BLOCKED"
    if not rubric_scores:
        return None
    if all(score == 3 for score in rubric_scores.values()):
        return "A"
    if all(score >= 2 for score in rubric_scores.values()):
        return "B"
    if all(score >= 1 for score in rubric_scores.values()):
        return "C"
    return "F_BLOCKED"


def validate_report_card_text(text: str, path: str | None = None) -> dict[str, Any]:
    parsed = parse_report_card(text)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    required_grade = expected_grade(parsed["rubric_scores"], parsed["critical_scores"])

    if parsed["actual_grade"] is None:
        errors.append({"code": "MISSING_LETTER_GRADE", "message": "No target_artifact_grade_label or grade_label found."})
    if parsed["letter_grade_mark"] is None:
        errors.append({"code": "MISSING_LETTER_GRADE_MARK", "message": "No visible letter_grade_mark found."})
    if not parsed["rubric_scores"]:
        errors.append({"code": "MISSING_RUBRIC_SCORES", "message": "No parseable rubric_scores list found."})
    if not parsed["critical_scores"]:
        errors.append(
            {
                "code": "MISSING_CRITICAL_CRITERIA_RESULTS",
                "message": "No parseable critical_criteria_results line found.",
            }
        )
    if parsed["lowest_score_rule_applied"] != "YES":
        errors.append(
            {
                "code": "LOWEST_SCORE_RULE_NOT_CONFIRMED",
                "message": "lowest_score_rule_applied must be YES.",
            }
        )
    if parsed["averaging_used"] != "NO":
        errors.append({"code": "AVERAGING_NOT_FORBIDDEN", "message": "averaging_used must be NO."})

    for field, present in parsed["required_fields"].items():
        if not present:
            errors.append({"code": f"MISSING_{field.upper()}", "message": f"Required report-card field missing: {field}."})

    if required_grade and parsed["actual_grade"] and parsed["actual_grade"] != required_grade:
        errors.append(
            {
                "code": "GRADE_MATH_CONFLICT",
                "message": "Report-card letter grade contradicts deterministic score law.",
                "actual_grade": parsed["actual_grade"],
                "required_grade": required_grade,
                "critical_scores": parsed["critical_scores"],
                "rubric_scores": parsed["rubric_scores"],
            }
        )

    if parsed["letter_grade_mark"] and parsed["actual_grade"] and parsed["letter_grade_mark"] != parsed["actual_grade"]:
        warnings.append(
            {
                "code": "LETTER_MARK_MISMATCH",
                "message": "letter_grade_mark differs from target_artifact_grade_label after normalization.",
                "actual_grade": parsed["actual_grade"],
                "letter_grade_mark": parsed["letter_grade_mark"],
            }
        )

    return {
        "check": "MMI_REPORT_CARD_GRADE_MATH",
        "path": path,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "actual_grade": parsed["actual_grade"],
        "required_grade": required_grade,
        "rubric_scores": parsed["rubric_scores"],
        "critical_scores": parsed["critical_scores"],
        "lowest_score_rule_applied": parsed["lowest_score_rule_applied"],
        "averaging_used": parsed["averaging_used"],
        "required_fields": parsed["required_fields"],
    }


def validate_report_card_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "check": "MMI_REPORT_CARD_GRADE_MATH",
            "path": path.as_posix(),
            "ok": False,
            "errors": [{"code": "REPORT_CARD_NOT_FOUND", "message": "Report-card file not found."}],
            "warnings": [],
        }
    if not path.is_file():
        return {
            "check": "MMI_REPORT_CARD_GRADE_MATH",
            "path": path.as_posix(),
            "ok": False,
            "errors": [{"code": "REPORT_CARD_NOT_FILE", "message": "Report-card path is not a file."}],
            "warnings": [],
        }
    return validate_report_card_text(path.read_text(encoding="utf-8"), path.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="report-card Markdown path")
    args = parser.parse_args()

    result = validate_report_card_file(Path(args.path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
