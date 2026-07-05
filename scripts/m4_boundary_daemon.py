#!/usr/bin/env python3
"""§17 Phase 4C — boundary daemon skeleton selftest gate."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.boundary_daemon import run_daemon_selftest
from mmi.m4.evidence_paths import resolve_boundary_evidence_dir


def _go_selftest(policy: Path, authority_manifest: Path, evidence: Path) -> tuple[bool, str]:
    go_dir = REPO / "host_boundary" / "mmi_boundary_daemon"
    if shutil.which("go") is None:
        return False, "go_not_installed"
    result = subprocess.run(
        [
            "go",
            "run",
            ".",
            "--selftest",
            "--policy",
            str(policy),
            "--authority-manifest",
            str(authority_manifest),
            "--evidence",
            str(evidence),
        ],
        cwd=go_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, "go_selftest_pass"
    return False, (result.stderr or result.stdout or "go_selftest_fail").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="M4 boundary daemon skeleton §17 Phase 4C")
    parser.add_argument("--authority", type=Path, default=REPO)
    parser.add_argument("--evidence", type=Path, default=None)
    parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="policy_manifest.json (default: EVIDENCE_ROOT/boundary/policy_manifest.json)",
    )
    parser.add_argument(
        "--authority-manifest",
        type=Path,
        default=None,
        help="authority_manifest.json (default: EVIDENCE_ROOT/boundary/authority_manifest.json)",
    )
    parser.add_argument("--try-go", action="store_true", help="Also run Go skeleton if go is installed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    authority = args.authority.resolve()
    evidence_dir = resolve_boundary_evidence_dir(args.evidence, authority)
    policy_path = args.policy or (evidence_dir / "policy_manifest.json")
    authority_manifest_path = args.authority_manifest or (evidence_dir / "authority_manifest.json")

    if not policy_path.exists() or not authority_manifest_path.exists():
        print(
            "missing policy or authority manifest — run m4_authority_seal.py --store first "
            f"(looked in {evidence_dir})",
            file=sys.stderr,
        )
        return 2

    from mmi.m4.key_custody import create_custodian, dev_stub_key_path

    custodian = create_custodian(evidence_boundary_dir=evidence_dir)
    if dev_stub_key_path(evidence_dir) is None:
        print(
            "warning: no dev stub key at "
            f"{evidence_dir / '.mmi_dev_custody_stub.key'} — re-run m4_authority_seal.py --store "
            "so policy signatures verify",
            file=sys.stderr,
        )

    selftest = run_daemon_selftest(
        evidence_dir, policy_path, authority_manifest_path, custodian=custodian
    )
    go_result: dict[str, object] | None = None
    if args.try_go:
        ok, note = _go_selftest(policy_path, authority_manifest_path, evidence_dir)
        go_result = {"attempted": True, "passed": ok, "note": note}

    passed = (
        selftest.get("armed_on_valid_policy") is True
        and selftest.get("bad_manifest_refused") is True
        and selftest.get("heartbeat_visible") is True
        and selftest.get("daemon_log_visible") is True
    )

    summary = {
        "harness": "m4_boundary_daemon",
        "phase": "17_phase_4C",
        "spec_section": "§8, §17 Phase 4C",
        "passed": passed,
        "selftest": selftest,
        "go_selftest": go_result,
        "evidence_dir": str(evidence_dir),
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "perfect_claim": False,
    }

    out_path = evidence_dir / "boundary_daemon_selftest.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"m4_boundary_daemon: {'PASS' if passed else 'FAIL'}")
        print(f"  evidence={evidence_dir}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
