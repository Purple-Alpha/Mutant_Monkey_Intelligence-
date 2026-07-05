#!/usr/bin/env python3
"""§17 Phase 3 — modular sandbox escape suite (§7)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.evidence_paths import EvidencePathError, resolve_sandbox_evidence_dir
from mmi.m4.invariants import run_static_suite, suite_passed as invariants_passed
from mmi.m4.sandbox_escape import (
    SANDBOX_MODULES,
    SandboxBoundaryPolicy,
    SandboxContext,
    run_all_modules,
    run_module,
    suite_passed,
)


def _write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _serialize_results(results) -> list[dict]:
    rows = []
    for mod in results:
        rows.append(
            {
                "module": mod.module,
                "result": mod.result.value,
                "canaries": mod.canaries,
                "vectors": [
                    {
                        "vector_id": v.vector_id,
                        "result": v.result.value,
                        "canary": v.canary,
                        "detail": v.detail,
                    }
                    for v in mod.vectors
                ],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 modular sandbox escape suite §7")
    parser.add_argument(
        "--module",
        choices=SANDBOX_MODULES,
        default=None,
        help="run single module (default: all)",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=None,
        help="EVIDENCE_ROOT/sandbox/ output directory",
    )
    parser.add_argument(
        "--authority",
        type=Path,
        default=REPO,
        help="Authority repo root",
    )
    parser.add_argument(
        "--lab-root",
        type=Path,
        default=None,
        help="Simulated LAB_ROOT (default: /tmp/mmi_chaos_lab/sim)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    args = parser.parse_args()

    authority = args.authority.resolve()
    try:
        evidence_dir = resolve_sandbox_evidence_dir(args.evidence, authority)
    except EvidencePathError as exc:
        print(f"m4_sandbox_escape_suite: FAIL — {exc}", file=sys.stderr)
        return 2

    lab_root = (args.lab_root or Path("/tmp/mmi_chaos_lab/sim")).expanduser()
    ctx = SandboxContext(
        authority_root=authority,
        lab_root=lab_root,
        evidence_root=evidence_dir.parent,
    )
    policy = SandboxBoundaryPolicy()

    if args.module:
        results = [run_module(args.module, ctx, policy)]
    else:
        results = run_all_modules(ctx, policy)

    escape_pass = suite_passed(results)
    inv_pass = invariants_passed(run_static_suite(authority))
    passed = escape_pass and inv_pass

    summary = {
        "harness": "m4_sandbox_escape_suite",
        "phase": "17_phase_3",
        "spec_section": "§7",
        "passed": passed,
        "escape_overall": "PASS" if escape_pass else "FAIL",
        "invariants_static_pass": inv_pass,
        "modules": _serialize_results(results),
        "overall": "PASS" if escape_pass else "FAIL",
        "evidence_dir": evidence_dir.as_posix(),
        "evidence_root": evidence_dir.parent.as_posix(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_summary(evidence_dir / "sandbox_escape_summary.json", summary)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "PASS" if passed else "FAIL"
        print(f"m4_sandbox_escape_suite: {status}")
        print(f"  escape: {summary['escape_overall']}; INV static: {'PASS' if inv_pass else 'FAIL'}")
        for row in summary["modules"]:
            print(f"  {row['module']}: {row['result']}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
