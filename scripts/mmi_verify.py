#!/usr/bin/env python3
"""Read-only MMI verification checks (chaos hardening H1–H2, Level 3 read-only).

H1: closeout output_files must exist on disk.
H2: intel brief §1 + ATT&CK smb_relevance must not launder global/vendor stats.
L3: staged OPSEC checklist false-DONE audit (read-only).
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "mmi/project_brain/intel/briefs"
LIVE_OPSEC_CHECKLIST = ROOT / "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md"
MONITORED_OPSEC_ITEMS = ("OPSEC-4", "OPSEC-5", "OPSEC-9")

# Headline-facing vendor/global indicators (not exhaustive — catches laundering patterns)
VENDOR_STAT_PATTERNS = [
    re.compile(r"\b\d+\s*(?:\.\d+)?\s*%"),
    re.compile(r"\bVerizon\b", re.I),
    re.compile(r"\bVeeam\b", re.I),
    re.compile(r"\bSophos\b", re.I),
    re.compile(r"\bCrowdStrike\b", re.I),
    re.compile(r"\bMicrosoft\b.*\d+\s*%", re.I),
]

GLOBAL_DATA_TAG = re.compile(r"\[Global Data", re.I)
SECTION_HEADING = re.compile(r"^##\s+\d+\.", re.M)


def verify_closeout_outputs(root: Path, output_paths: list[str]) -> dict[str, Any]:
    """H1 — every listed output path must exist under repo root."""
    missing: list[str] = []
    present: list[str] = []
    for rel in output_paths:
        target = root / rel.replace("\\", "/")
        if target.is_file():
            present.append(rel)
        else:
            missing.append(rel)
    return {
        "check": "H1_closeout_output_files",
        "ok": len(missing) == 0,
        "missing": missing,
        "present": present,
        "count": len(output_paths),
    }


def _section_text(content: str, section_num: int) -> str:
    """Extract markdown body of ## N. section until next ## or EOF."""
    marker = re.compile(rf"^##\s+{section_num}\.\s+", re.M)
    m = marker.search(content)
    if not m:
        return ""
    start = m.end()
    rest = content[start:]
    nxt = SECTION_HEADING.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _smb_relevance_cells(content: str) -> list[str]:
    """Extract smb_relevance cell values from ATT&CK tables in §3."""
    values: list[str] = []
    in_s3 = _section_text(content, 3)
    if not in_s3:
        return values
    for line in in_s3.splitlines():
        if "| `smb_relevance` |" in line or "| smb_relevance |" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                values.append(parts[-1])
    return values


def _scan_text_for_violations(text: str, context: str) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if GLOBAL_DATA_TAG.search(stripped):
            continue
        for pat in VENDOR_STAT_PATTERNS:
            if pat.search(stripped):
                violations.append(
                    {
                        "context": context,
                        "line": stripped[:200],
                        "pattern": pat.pattern,
                    }
                )
                break
    return violations


def verify_intel_brief(path: Path) -> dict[str, Any]:
    """H2 — flag global/vendor stats in §1 and smb_relevance without quarantine tag."""
    content = path.read_text(encoding="utf-8")
    violations: list[dict[str, str]] = []

    sec1 = _section_text(content, 1)
    violations.extend(_scan_text_for_violations(sec1, "section_1_threat_summary"))

    for idx, cell in enumerate(_smb_relevance_cells(content), start=1):
        violations.extend(_scan_text_for_violations(cell, f"att&ck_smb_relevance_{idx}"))

    # §5 claims table and later: intentionally not scanned (quarantined stats allowed)
    claims_start = content.find("## 5.")
    if claims_start == -1:
        claims_start = len(content)

    return {
        "check": "H2_intel_brief_headline",
        "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
        "ok": len(violations) == 0,
        "violations": violations,
    }


def _parse_opsec_row(content: str, item_id: str) -> dict[str, str] | None:
    prefix = f"| {item_id} |"
    for line in content.splitlines():
        if line.startswith(prefix):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 9:
                return {
                    "cadence": parts[5],
                    "state": parts[6],
                    "last_done": parts[7],
                    "verify_method": parts[8],
                }
    return None


def _last_done_stale_reason(cadence: str, last_done: str, today: date) -> str | None:
    try:
        done_date = date.fromisoformat(last_done)
    except ValueError:
        return "DONE with invalid last_done date"
    if done_date > today:
        return "DONE with future last_done date"

    cadence_lower = cadence.lower()
    age_days = (today - done_date).days
    if "daily" in cadence_lower and age_days > 7:
        return "DONE with stale daily-habit last_done"
    if "quarterly" in cadence_lower and age_days > 120:
        return "DONE with stale quarterly-habit last_done"
    return None


def audit_opsec_false_done(content: str, today: date | None = None) -> list[dict[str, str]]:
    """Flag OPSEC-4/5/9 rows falsely marked DONE (T06 / L3-06 rules)."""
    today = today or date.today()
    violations: list[dict[str, str]] = []
    for item in MONITORED_OPSEC_ITEMS:
        row = _parse_opsec_row(content, item)
        if row is None:
            violations.append({"item": item, "reason": "row not found"})
            continue
        if row["state"] != "DONE":
            continue
        if not row["last_done"].strip():
            violations.append({"item": item, "reason": "DONE without last_done"})
        else:
            stale_reason = _last_done_stale_reason(row.get("cadence", ""), row["last_done"], today)
            if stale_reason:
                violations.append({"item": item, "reason": stale_reason})
        verify = row["verify_method"].lower()
        if "dry-run" in verify:
            violations.append({"item": item, "reason": "DONE with dry-run-only verify_method"})
        elif "template" in verify:
            violations.append({"item": item, "reason": "DONE with template-only verify_method"})
        elif item in ("OPSEC-4", "OPSEC-9") and "worksheet" in verify:
            violations.append({"item": item, "reason": "DONE with worksheet-only verify_method"})
    return violations


def verify_opsec_checklist(path: Path, live_path: Path | None = None) -> dict[str, Any]:
    """L3-06 — read-only false-DONE audit on a checklist copy; optional live truth compare."""
    content = path.read_text(encoding="utf-8")
    violations = audit_opsec_false_done(content)
    monitored: dict[str, dict[str, str]] = {}
    for item in MONITORED_OPSEC_ITEMS:
        row = _parse_opsec_row(content, item)
        if row:
            monitored[item] = row

    live_truth: dict[str, str | None] = {}
    live_unchanged_ok: bool | None = None
    if live_path is not None:
        live_content = live_path.read_text(encoding="utf-8")
        live_unchanged_ok = True
        for item in MONITORED_OPSEC_ITEMS:
            row = _parse_opsec_row(live_content, item)
            state = row["state"] if row else None
            live_truth[item] = state
            if state != "NOT_STARTED":
                live_unchanged_ok = False

    rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    return {
        "check": "L3_opsec_false_done",
        "path": rel,
        "ok": len(violations) == 0,
        "fault_detected": len(violations) > 0,
        "violations": violations,
        "monitored_items": monitored,
        "live_truth": live_truth,
        "live_unchanged_ok": live_unchanged_ok,
    }


def opsec_amend_helper(path: Path, live_path: Path | None = LIVE_OPSEC_CHECKLIST) -> dict[str, Any]:
    """G-OPSEC-1 — pre-amend helper for Matt's manual checklist edits."""
    audit = verify_opsec_checklist(path, live_path)
    blocked = bool(audit.get("violations"))
    return {
        "check": "G_OPSEC_1_amend_helper",
        "decision": "BLOCK_AMEND" if blocked else "ALLOW_AMEND",
        "ok": not blocked,
        "path": audit.get("path"),
        "violations": audit.get("violations", []),
        "monitored_items": audit.get("monitored_items", {}),
        "live_truth": audit.get("live_truth", {}),
        "live_unchanged_ok": audit.get("live_unchanged_ok"),
        "mutated_files": [],
        "human_gated_sop": [
            "1. Copy OPERATOR_OPSEC_CHECKLIST.md to a draft/staged path before editing.",
            "2. Matt manually edits the draft row only when real evidence exists.",
            "3. Run this helper against the draft before replacing the live checklist.",
            "4. If decision is BLOCK_AMEND, do not promote rows to DONE; fix evidence or keep NOT_STARTED.",
            "5. If decision is ALLOW_AMEND, Matt may manually apply the reviewed checklist change.",
        ],
        "hard_rule": "Worksheet/dry-run/template evidence never auto-promotes OPSEC rows to DONE.",
    }


def verify_all_intel_briefs(briefs_dir: Path = BRIEFS_DIR) -> dict[str, Any]:
    results = []
    for brief in sorted(briefs_dir.glob("INTEL_*.md")):
        results.append(verify_intel_brief(brief))
    failed = [r for r in results if not r["ok"]]
    return {
        "check": "H2_intel_briefs_batch",
        "ok": len(failed) == 0,
        "briefs_scanned": len(results),
        "failed": len(failed),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_closeout = sub.add_parser("closeout", help="H1 — verify output file paths exist")
    p_closeout.add_argument("paths", nargs="+", help="repo-relative output paths")

    sub.add_parser("intel-briefs", help="H2 — scan filed intel briefs for headline laundering")

    p_brief = sub.add_parser("intel-brief", help="H2 — scan one or more brief files")
    p_brief.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="path(s) to brief markdown (shell globs OK)",
    )

    p_opsec = sub.add_parser("opsec-checklist", help="L3-06 — audit staged OPSEC checklist for false DONE")
    p_opsec.add_argument("path", type=Path, help="checklist markdown to audit")
    p_opsec.add_argument(
        "--live-compare",
        action="store_true",
        help="compare live checklist truth for OPSEC-4/5/9 (read-only)",
    )
    p_opsec.add_argument(
        "--expect-fault",
        action="store_true",
        help="exit 0 when fault_detected and live_unchanged_ok (L3 staged test mode)",
    )

    p_opsec_amend = sub.add_parser(
        "opsec-amend-check",
        help="G-OPSEC-1 — pre-amend helper before Matt manually edits OPSEC checklist",
    )
    p_opsec_amend.add_argument("path", type=Path, help="draft/staged checklist markdown to audit")
    p_opsec_amend.add_argument(
        "--no-live-compare",
        action="store_true",
        help="omit live checklist comparison (still read-only)",
    )

    args = parser.parse_args()

    if args.command == "closeout":
        result = verify_closeout_outputs(ROOT, args.paths)
        ok = result.get("ok", False)
    elif args.command == "intel-briefs":
        result = verify_all_intel_briefs()
        ok = result.get("ok", False)
    elif args.command == "opsec-checklist":
        path = args.path if args.path.is_absolute() else ROOT / args.path
        live = LIVE_OPSEC_CHECKLIST if args.live_compare else None
        result = verify_opsec_checklist(path, live)
        if args.expect_fault:
            ok = bool(result.get("fault_detected")) and bool(result.get("live_unchanged_ok"))
        else:
            ok = result.get("ok", False)
    elif args.command == "opsec-amend-check":
        path = args.path if args.path.is_absolute() else ROOT / args.path
        live = None if args.no_live_compare else LIVE_OPSEC_CHECKLIST
        result = opsec_amend_helper(path, live)
        ok = result.get("ok", False)
    elif len(args.paths) == 1:
        path = args.paths[0]
        path = path if path.is_absolute() else ROOT / path
        result = verify_intel_brief(path)
        ok = result.get("ok", False)
    else:
        results = []
        for raw in args.paths:
            path = raw if raw.is_absolute() else ROOT / raw
            results.append(verify_intel_brief(path))
        failed = [r for r in results if not r["ok"]]
        result = {
            "check": "H2_intel_brief_batch",
            "ok": len(failed) == 0,
            "briefs_scanned": len(results),
            "failed": len(failed),
            "results": results,
        }
        ok = result.get("ok", False)

    print(json.dumps(result, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
