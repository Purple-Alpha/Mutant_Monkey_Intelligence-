#!/usr/bin/env python3
"""§17 Phase 4D — minifilter policy T1/T2 contract + optional live probe gate."""

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
from mmi.m4.minifilter_policy import run_minifilter_selftest


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 minifilter policy suite §17 Phase 4D")
    parser.add_argument("--authority", type=Path, default=REPO)
    parser.add_argument("--evidence", type=Path, default=None)
    parser.add_argument(
        "--authority-manifest",
        type=Path,
        default=None,
        help="authority_manifest.json (default: EVIDENCE_ROOT/boundary/)",
    )
    parser.add_argument(
        "--scratch",
        type=Path,
        default=Path(r"C:\mmi_boundary_scratch"),
        help="positive-control scratch root (outside authority)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="attempt live writes (requires kernel minifilter loaded for T1 block)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    authority = args.authority.resolve()
    evidence_dir = resolve_boundary_evidence_dir(args.evidence, authority)
    manifest_path = args.authority_manifest or (evidence_dir / "authority_manifest.json")

    if not manifest_path.exists():
        print(
            f"missing {manifest_path} — run m4_authority_seal.py --store first",
            file=sys.stderr,
        )
        return 2

    h0_path = evidence_dir / "h0_pre_provision_seal.json"
    h0_fp = None
    if h0_path.exists():
        h0_fp = json.loads(h0_path.read_text(encoding="utf-8")).get("h0_fingerprint")

    selftest = run_minifilter_selftest(
        evidence_dir,
        manifest_path,
        scratch_root=args.scratch,
        h0_fingerprint=str(h0_fp) if h0_fp else None,
        live=args.live,
    )

    passed = selftest.get("contract_pass") is True and selftest.get("verify_fingerprint_ok") is True
    if args.live:
        passed = passed and selftest.get("min_viable_live") is True

    summary = {
        "harness": "m4_minifilter_suite",
        "phase": "17_phase_4D",
        "spec_section": "§8, §14 T1/T2",
        "passed": passed,
        "selftest": selftest,
        "evidence_dir": str(evidence_dir),
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "perfect_claim": False,
        "note": "contract mode proves policy engine; live min-viable requires loaded minifilter driver",
    }

    out_path = evidence_dir / "minifilter_suite_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"m4_minifilter_suite: {'PASS' if passed else 'FAIL'} mode={selftest.get('mode')}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
