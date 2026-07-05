#!/usr/bin/env python3
"""§17 Phase 4B — authority H0 seal + signed policy manifest gate."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.authority_seal import (
    WfpPolicyConfig,
    build_enforcement_manifest,
    run_authority_seal_selftest,
    seal_fingerprint,
    store_pre_provision_seal,
)
from mmi.m4.evidence_paths import resolve_boundary_evidence_dir
from mmi.m4.key_custody import create_custodian


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 authority seal + policy manifest §17 Phase 4B")
    parser.add_argument("--authority", type=Path, default=REPO, help="Authority repo root")
    parser.add_argument("--evidence", type=Path, default=None, help="EVIDENCE_ROOT override")
    parser.add_argument("--custody-mode", default=None, help="MMI_KEY_CUSTODY_MODE override")
    parser.add_argument("--store", action="store_true", help="Write pre-provision seal artifacts to EVIDENCE_ROOT")
    parser.add_argument("--clone-sid", default=None, help="Signed WFP clone SID target (policy_manifest wfp_policy)")
    parser.add_argument(
        "--probe-account",
        default=None,
        help="Local probe account name for clone-context live probes (e.g. MmiWfpProbe)",
    )
    parser.add_argument("--fingerprint-only", action="store_true", help="Print H0 fingerprint and exit")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    authority = args.authority.resolve()
    custodian = create_custodian(args.custody_mode)

    if args.fingerprint_only:
        h0 = seal_fingerprint(authority)
        if args.json:
            print(json.dumps({"h0_fingerprint": h0, "authority_root": str(authority)}, indent=2))
        else:
            print(h0)
        return 0

    selftest = run_authority_seal_selftest(authority, custodian)
    store_result: dict[str, object] | None = None
    if args.store:
        boundary_dir = resolve_boundary_evidence_dir(args.evidence, authority)
        wfp_policy: WfpPolicyConfig | None = None
        if args.clone_sid or args.probe_account:
            base = WfpPolicyConfig.default_dev()
            wfp_policy = WfpPolicyConfig(
                telemetry_egress_allowlist=base.telemetry_egress_allowlist,
                clone_sid=args.clone_sid or base.clone_sid,
                app_container_name=base.app_container_name,
                probe_account_name=args.probe_account or base.probe_account_name,
            )
        store_result = store_pre_provision_seal(
            boundary_dir,
            authority,
            custodian,
            wfp_policy=wfp_policy,
        )

    passed = (
        selftest.get("manifest_lists_fileids") is True
        and selftest.get("h0_signed_before_provision") is True
        and selftest.get("policy_sign_verify_ok") is True
        and selftest.get("hash_mismatch_refused") is True
        and selftest.get("daemon_arm_refused_on_tamper") is True
        and selftest.get("verify_fingerprint_ok") is True
    )

    summary = {
        "harness": "m4_authority_seal",
        "phase": "17_phase_4B",
        "spec_section": "§8, §17 Phase 4B",
        "passed": passed,
        "authority_root": str(authority),
        "selftest": selftest,
        "store": store_result,
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "perfect_claim": False,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        manifest = build_enforcement_manifest(authority, max_entries=5)
        print(f"m4_authority_seal: {'PASS' if passed else 'FAIL'}")
        print(f"  h0={selftest.get('h0_fingerprint')}")
        print(f"  sample_entries={len(manifest.entries)} (selftest capped at 200)")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
