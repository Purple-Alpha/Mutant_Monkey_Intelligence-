#!/usr/bin/env python3
"""§17 Phase 4E — WFP default-deny egress T7 contract + optional live gate."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.evidence_paths import resolve_boundary_evidence_dir
from mmi.m4.wfp_policy import run_wfp_selftest


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 WFP policy suite §17 Phase 4E")
    parser.add_argument("--authority", type=Path, default=REPO)
    parser.add_argument("--evidence", type=Path, default=None)
    parser.add_argument(
        "--policy-manifest",
        type=Path,
        default=None,
        help="policy_manifest.json (default: EVIDENCE_ROOT/boundary/)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="attempt live TCP probes (requires WFP engine installed for T7 block)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    authority = args.authority.resolve()
    evidence_dir = resolve_boundary_evidence_dir(args.evidence, authority)
    manifest_path = args.policy_manifest or (evidence_dir / "policy_manifest.json")

    if not manifest_path.exists():
        print(
            f"missing {manifest_path} — run m4_authority_seal.py --store first",
            file=sys.stderr,
        )
        return 2

    selftest = run_wfp_selftest(
        evidence_dir,
        manifest_path,
        live=args.live,
    )

    passed = selftest.get("contract_pass") is True
    if args.live:
        passed = passed and selftest.get("min_viable_live_t7") is True

    summary = {
        "harness": "m4_wfp_suite",
        "phase": "17_phase_4E",
        "spec_section": "§8, §14 T7",
        "passed": passed,
        "selftest": selftest,
        "evidence_dir": str(evidence_dir),
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "perfect_claim": False,
        "note": "contract mode proves policy engine; live min-viable requires loaded WFP engine",
    }

    out_path = evidence_dir / "wfp_suite_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    falsifier_dir = evidence_dir / "falsifiers"
    falsifier_dir.mkdir(parents=True, exist_ok=True)
    t7_summary = {
        "schema_v": selftest.get("schema_v"),
        "passed": passed,
        "live": args.live,
        "min_viable_live_t7": selftest.get("min_viable_live_t7"),
        "policy_hash": selftest.get("policy_hash"),
        "sealed_at_utc": summary["sealed_at_utc"],
    }
    (falsifier_dir / "T7_summary.json").write_text(
        json.dumps(t7_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"m4_wfp_suite: {'PASS' if passed else 'FAIL'} mode={selftest.get('mode')}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
