#!/usr/bin/env python3
"""Build console_evidence_v1 bundle from Gate B v2 summary."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

DEFAULT_AUTHORITY = Path("/mnt/c/MMI")


def _ensure_chaos(authority: Path) -> None:
    chaos = authority / "mmi/project_brain/chaos"
    if str(chaos) not in sys.path:
        sys.path.insert(0, str(chaos))


def build_bundle_from_summary(summary_path: Path, operator_action: str) -> dict[str, Any]:
    _ensure_chaos(Path("/mnt/c/MMI"))
    from console_evidence_gate import BUNDLE_VERSION, compute_bundle_id  # type: ignore
    from mmi_canonical_digest import file_sha256_hex  # type: ignore

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("overall_gate_status") != "CLEAN":
        blockers = summary.get("blockers") or []
        raise SystemExit(
            json.dumps(
                {
                    "error": "Gate B summary is not CLEAN — cannot build console bundle",
                    "overall_gate_status": summary.get("overall_gate_status"),
                    "blockers": blockers,
                }
            )
        )
    if "budget_telemetry_snapshot" not in summary:
        raise SystemExit(
            json.dumps(
                {
                    "error": "summary missing budget_telemetry_snapshot — re-run proof_gate with --console-bindings",
                    "overall_gate_status": summary.get("overall_gate_status"),
                }
            )
        )
    for field in ("patch", "proof_of_fix_digest", "proof_of_regression_digest", "rollback"):
        if field not in summary:
            raise SystemExit(json.dumps({"error": f"summary missing required field: {field}"}))

    patch = summary["patch"]
    proof_of_fix = summary["proof_of_fix"]
    proof_of_regression = summary["proof_of_regression"]

    bundle: dict[str, Any] = {
        "bundle_version": BUNDLE_VERSION,
        "created_at_ms": int(time.time() * 1000),
        "operator_action": operator_action,
        "fix_id": summary["fix_id"],
        "gate_b_summary_path": summary_path.as_posix(),
        "gate_b_summary_digest": file_sha256_hex(summary_path),
        "patch_hash": patch["patch_hash"],
        "proof_of_fix_ref": {
            "exploit_id": proof_of_fix.get("scenario_id")
            or proof_of_fix.get("fault")
            or proof_of_fix.get("command")
            or summary["fix_id"],
            "evidence_path": summary.get("evidence_dir", ""),
            "digest": summary["proof_of_fix_digest"],
        },
        "proof_of_regression_ref": {
            "suite": "proof_gate_v1",
            "verdict": "GREEN" if summary.get("regression_verdict") == "PASS" else "RED",
            "evidence_path": proof_of_regression.get("summary_path") or summary.get("evidence_dir", ""),
            "digest": summary["proof_of_regression_digest"],
        },
        "rollback_token_hash": summary["rollback"]["rollback_token_hash"],
        "budget_telemetry_snapshot": summary["budget_telemetry_snapshot"],
    }
    bundle["bundle_id"] = compute_bundle_id(bundle)
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Build console evidence bundle from Gate B summary")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument(
        "--operator-action",
        default="SIGN_PROMOTE",
        choices=["SIGN_PROMOTE", "SIGN_RESUME", "SIGN_ACK"],
    )
    args = parser.parse_args()
    if not args.summary.exists():
        print(json.dumps({"error": "summary not found"}), file=sys.stderr)
        return 2
    bundle = build_bundle_from_summary(args.summary, args.operator_action)
    print(json.dumps(bundle, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
