#!/usr/bin/env python3
"""§17 Phase 4A — KEY_CUSTODY + stage_attestation selftest gate."""

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
from mmi.m4.key_custody import create_custodian, custody_selftest, write_custody_selftest
from mmi.m4.stage_attestation import run_attestation_selftest


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 KEY_CUSTODY + stage_attestation §17 Phase 4A")
    parser.add_argument("--authority", type=Path, default=REPO, help="Authority repo root")
    parser.add_argument("--evidence", type=Path, default=None, help="EVIDENCE_ROOT override")
    parser.add_argument("--custody-mode", default=None, help="MMI_KEY_CUSTODY_MODE override")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    authority = args.authority.resolve()
    boundary_dir = resolve_boundary_evidence_dir(args.evidence, authority)
    custodian = create_custodian(args.custody_mode)

    custody_result = custody_selftest(custodian)
    attestation_result = run_attestation_selftest(custodian)

    write_custody_selftest(boundary_dir / "key_custody_selftest.json", custodian)
    attestation_path = boundary_dir / "stage_attestation_tests.json"
    attestation_path.write_text(json.dumps(attestation_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    passed = (
        custody_result.get("sign_verify_ok") is True
        and custody_result.get("export_blocked") is True
        and attestation_result.get("stale_h0_rejected") is True
        and attestation_result.get("mixed_lineage_rejected") is True
        and attestation_result.get("forgery_rejected") is True
        and attestation_result.get("non_promoting_emit_none") is True
    )

    summary = {
        "harness": "m4_stage_attestation",
        "phase": "17_phase_4A",
        "spec_section": "§3.1, §17 Phase 4A",
        "passed": passed,
        "custody_mode": custody_result.get("custody_mode"),
        "satisfies_min_viable_exit": custody_result.get("satisfies_min_viable_exit"),
        "custody_selftest": custody_result,
        "attestation_selftest": attestation_result,
        "evidence_dir": str(boundary_dir),
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "perfect_claim": False,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"m4_stage_attestation: {'PASS' if passed else 'FAIL'}")
        print(f"  custody_mode={custody_result.get('custody_mode')}")
        print(f"  evidence={boundary_dir}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
