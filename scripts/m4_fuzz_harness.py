#!/usr/bin/env python3
"""§17 Phase 2 — deterministic M4 fuzz harness (§6)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.evidence_paths import EvidencePathError, resolve_fuzz_evidence_dir
from mmi.m4.fuzz_runner import FUZZ_TARGETS, _TARGET_RUNNERS, run_all_targets, run_fuzz_target
from mmi.m4.invariants import run_static_suite, suite_passed


def _write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _summary_for(target: str, seed: int, iters: int, failures: list) -> dict:
    return {
        "target": target,
        "seed": seed,
        "iters": iters,
        "failures": [
            {
                "target": getattr(f, "target", target),
                "iteration": f.iteration,
                "seed": f.seed,
                "detail": f.detail,
            }
            for f in failures
        ],
        "overall": "PASS" if not failures else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 deterministic fuzz harness §6")
    parser.add_argument(
        "--target",
        choices=FUZZ_TARGETS,
        default="all",
        help="fuzz target surface",
    )
    parser.add_argument("--seed", type=int, default=1, help="deterministic seed (recorded in evidence)")
    parser.add_argument("--iters", type=int, default=100, help="iterations per target")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=None,
        help="EVIDENCE_ROOT/fuzz/ output directory (default: $MMI_EVIDENCE_ROOT/fuzz or host default outside authority)",
    )
    parser.add_argument(
        "--authority",
        type=Path,
        default=REPO,
        help="Authority repo root (INV static re-check after fuzz)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    args = parser.parse_args()

    authority = args.authority.resolve()
    try:
        evidence_dir = resolve_fuzz_evidence_dir(args.evidence, authority)
    except EvidencePathError as exc:
        print(f"m4_fuzz_harness: FAIL — {exc}", file=sys.stderr)
        return 2

    per_target: dict[str, dict] = {}
    if args.target == "all":
        all_failures = run_all_targets(args.seed, args.iters)
        for name in _TARGET_RUNNERS:
            tf = [f for f in all_failures if f.target == name]
            summary = _summary_for(name, args.seed, args.iters, tf)
            per_target[name] = summary
            _write_summary(evidence_dir / f"fuzz_summary_{name}.json", summary)
        combined = {
            "target": "all",
            "seed": args.seed,
            "iters": args.iters,
            "failures": [
                {"target": f.target, "iteration": f.iteration, "seed": f.seed, "detail": f.detail}
                for f in all_failures
            ],
            "overall": "PASS" if not all_failures else "FAIL",
            "targets": per_target,
        }
    else:
        all_failures = run_fuzz_target(args.target, args.seed, args.iters)
        combined = _summary_for(args.target, args.seed, args.iters, all_failures)
        per_target[args.target] = combined

    _write_summary(evidence_dir / "fuzz_summary.json", combined)
    overall = combined["overall"]

    inv_pass = suite_passed(run_static_suite(authority))
    passed = overall == "PASS" and inv_pass

    gate = {
        "harness": "m4_fuzz_harness",
        "phase": "17_phase_2",
        "spec_section": "§6",
        "passed": passed,
        "fuzz_overall": overall,
        "invariants_static_pass": inv_pass,
        "seed": args.seed,
        "iters": args.iters,
        "target": args.target,
        "evidence_dir": evidence_dir.as_posix(),
        "evidence_root": evidence_dir.parent.as_posix(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.json:
        print(json.dumps({**gate, "fuzz_summary": combined}, indent=2))
    else:
        status = "PASS" if passed else "FAIL"
        print(f"m4_fuzz_harness ({args.target}): {status}")
        print(f"  fuzz: {overall}; INV static: {'PASS' if inv_pass else 'FAIL'}")
        for f in all_failures[:10]:
            print(f"  [{f.target}] iter={f.iteration} {f.detail}")
        if len(all_failures) > 10:
            print(f"  ... {len(all_failures) - 10} more")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
