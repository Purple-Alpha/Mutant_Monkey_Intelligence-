#!/usr/bin/env python3
"""
MMI Phase 1 Stability Harness.

Runs or scores three independent canonical Chaos Lab stacks and writes an
honest Phase 1 stability summary. This is measurement only; it does not heal,
patch, or promote anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUTHORITY = Path("/mnt/c/MMI")
DEFAULT_LAB_ROOT = Path("/tmp/mmi_chaos_lab")
CANONICAL_STACK = (
    "smash-all",
    "mesh-smash",
    "iceberg-ingress",
    "purple-evasion",
    "action-integrity",
)
EVIDENCE_FILES = (
    "purple_evasion_summary.json",
    "m3_mesh_summary.json",
    "smash_all_summary.json",
    "iceberg_ingress_summary.json",
    "action_integrity_summary.json",
)


def _ensure_chaos_import(authority: Path) -> None:
    chaos_dir = authority / "mmi/project_brain/chaos"
    if str(chaos_dir) not in sys.path:
        sys.path.insert(0, str(chaos_dir))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def critic_hash(authority: Path) -> str:
    path = authority / "mmi/project_brain/chaos/mirror_dimension_router.py"
    if not path.exists():
        raise FileNotFoundError(f"critic not found: {path}")
    return sha256_file(path)


def run_lab_id(base_lab_id: str, run_number: int, total_runs: int) -> str:
    if total_runs == 1:
        return base_lab_id
    return f"{base_lab_id}__phase1_run_{run_number:02d}"


def evidence_dir(lab_root: Path, lab_id: str) -> Path:
    return lab_root / lab_id / "EVIDENCE"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_paths(lab_root: Path, lab_id: str) -> dict[str, dict[str, Any]]:
    ev = evidence_dir(lab_root, lab_id)
    return {
        name: {
            "path": (ev / name).as_posix(),
            "exists": (ev / name).exists(),
        }
        for name in EVIDENCE_FILES
    }


def invoke_provisioner(authority: Path, lab_root: Path, lab_id: str) -> list[dict[str, Any]]:
    script = authority / "scripts/chaos_lab_provisioner.py"
    if str(authority / "scripts") not in sys.path:
        sys.path.insert(0, str(authority / "scripts"))
    from chaos_lab_provisioner import snapshot_authority_fingerprint  # type: ignore

    ev = evidence_dir(lab_root, lab_id)
    snapshot_authority_fingerprint(ev, authority, operation="phase1_stack")

    results: list[dict[str, Any]] = []
    for command in CANONICAL_STACK:
        cmd = [
            sys.executable,
            script.as_posix(),
            "--authority",
            authority.as_posix(),
            "--lab-root",
            lab_root.as_posix(),
            command,
            "--lab-id",
            lab_id,
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
        results.append(
            {
                "command": command,
                "argv": cmd,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            }
        )
        if completed.returncode != 0:
            break
    return results


def score_run(authority: Path, lab_root: Path, lab_id: str, run_number: int) -> dict[str, Any]:
    _ensure_chaos_import(authority)
    from weapon_battlefield_scoring import compute_weapon_scorecard  # type: ignore

    ev_paths = evidence_paths(lab_root, lab_id)
    missing = [name for name, meta in ev_paths.items() if not meta["exists"]]
    purple = read_json(Path(ev_paths["purple_evasion_summary.json"]["path"]))
    m1 = read_json(Path(ev_paths["smash_all_summary.json"]["path"]))
    m3 = read_json(Path(ev_paths["m3_mesh_summary.json"]["path"]))
    iceberg = read_json(Path(ev_paths["iceberg_ingress_summary.json"]["path"]))
    action = read_json(Path(ev_paths["action_integrity_summary.json"]["path"]))

    row: dict[str, Any] = {
        "run_number": run_number,
        "lab_id": lab_id,
        "evidence": ev_paths,
        "missing_evidence": missing,
        "critic_hash": critic_hash(authority),
    }

    if purple is None:
        row["status"] = "UNSCORED"
        row["falsification_reason"] = "missing purple_evasion_summary.json"
        return row

    scorecard = compute_weapon_scorecard(purple, m1, lab_root, lab_id, m3, iceberg)
    row.update(
        {
            "status": "SCORED",
            "overall_weapon_tier": scorecard["overall_weapon_tier"],
            "axis_a_tier": scorecard["axis_a_containment"]["tier"],
            "axis_b_tier": scorecard["axis_b_discipline"]["tier"],
            "iceberg_ingress_pass": scorecard["axis_b_discipline"].get("iceberg_ingress_pass"),
            "evolution_gate": scorecard.get("evolution_gate"),
            "weapon_scorecard": scorecard,
            "action_integrity": {
                "available": action is not None,
                "failed_count": action.get("failed_count") if action else None,
                "failed_scenarios": action.get("failed_scenarios") if action else None,
            },
        }
    )
    return row


def critic_hash_penalty(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Matrix §7.4 applies to same-lab_id purple re-runs, not independent run lab IDs.

    Phase 1 uses distinct lab IDs per run (e.g. m2_001__phase1_run_01..03). A shared
    authority critic hash across those runs is expected and is not gaming.
    """
    by_lab: dict[str, list[str]] = {}
    for run in runs:
        lab_id = run.get("lab_id")
        digest = run.get("critic_hash")
        if lab_id and digest:
            by_lab.setdefault(str(lab_id), []).append(str(digest))

    repeated_same_hash_labs = sorted(
        lab_id
        for lab_id, hashes in by_lab.items()
        if len(hashes) > 1 and len(set(hashes)) == 1
    )
    penalty = len(repeated_same_hash_labs) > 0
    all_hashes = [run.get("critic_hash") for run in runs if run.get("critic_hash")]
    return {
        "applies": penalty,
        "scope": "same_lab_id_rerun_only",
        "unique_hashes": sorted(set(str(h) for h in all_hashes)),
        "independent_lab_ids": sorted(by_lab.keys()),
        "penalized_lab_ids": repeated_same_hash_labs,
        "reason": (
            "matrix Section 7.4: repeated scoring on the same lab_id with unchanged "
            "mirror_dimension_router.py critic hash"
            if penalty
            else None
        ),
    }


def evaluate_phase1_stability(runs: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = [r.get("overall_weapon_tier") for r in runs if isinstance(r.get("overall_weapon_tier"), int)]
    falsification: list[dict[str, Any]] = []

    if len(tiers) != len(runs):
        for r in runs:
            if not isinstance(r.get("overall_weapon_tier"), int):
                falsification.append(
                    {
                        "run_number": r.get("run_number"),
                        "lab_id": r.get("lab_id"),
                        "reason": r.get("falsification_reason", "run could not be scored"),
                        "evidence": r.get("evidence"),
                    }
                )

    for r in runs:
        tier = r.get("overall_weapon_tier")
        if isinstance(tier, int) and tier < 4:
            falsification.append(
                {
                    "run_number": r.get("run_number"),
                    "lab_id": r.get("lab_id"),
                    "reason": f"Overall Tier {tier} below required Tier 4",
                    "axis_a_tier": r.get("axis_a_tier"),
                    "axis_b_tier": r.get("axis_b_tier"),
                    "evidence": r.get("evidence"),
                }
            )

    tier_spread = max(tiers) - min(tiers) if tiers else None
    if tier_spread is not None and tier_spread > 1:
        falsification.append(
            {
                "reason": f"tier variance {tier_spread} exceeds >1-tier stability limit",
                "tiers": tiers,
            }
        )

    hash_penalty = critic_hash_penalty(runs)
    if hash_penalty["applies"]:
        falsification.append(
            {
                "reason": hash_penalty["reason"],
                "critic_hashes": [r.get("critic_hash") for r in runs],
            }
        )

    return {
        "pass": len(falsification) == 0 and len(runs) > 0,
        "required_runs": len(runs),
        "tiers": tiers,
        "tier_spread": tier_spread,
        "all_tier_4": len(tiers) == len(runs) and all(t == 4 for t in tiers),
        "critic_hash_penalty": hash_penalty,
        "falsification_reasons": falsification,
    }


def run_harness(authority: Path, lab_root: Path, lab_id: str, runs: int, use_provisioner: bool) -> dict[str, Any]:
    per_run: list[dict[str, Any]] = []
    for i in range(1, runs + 1):
        rid = run_lab_id(lab_id, i, runs)
        provisioner_results: list[dict[str, Any]] = []
        if use_provisioner:
            provisioner_results = invoke_provisioner(authority, lab_root, rid)
            failed = [r for r in provisioner_results if r["returncode"] != 0]
            if failed:
                per_run.append(
                    {
                        "run_number": i,
                        "lab_id": rid,
                        "status": "COMMAND_FAILED",
                        "critic_hash": critic_hash(authority),
                        "provisioner": provisioner_results,
                        "falsification_reason": (
                            f"provisioner command failed: {failed[0]['command']}"
                        ),
                        "evidence": evidence_paths(lab_root, rid),
                    }
                )
                continue
        row = score_run(authority, lab_root, rid, i)
        if provisioner_results:
            row["provisioner"] = provisioner_results
        per_run.append(row)

    decision = evaluate_phase1_stability(per_run)
    summary = {
        "suite": "phase1_stability_harness_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority_root": authority.as_posix(),
        "lab_root": lab_root.as_posix(),
        "base_lab_id": lab_id,
        "runs_requested": runs,
        "canonical_stack": list(CANONICAL_STACK),
        "provisioner_executed": use_provisioner,
        "runs": per_run,
        "decision": decision,
        "verdict": "PASS" if decision["pass"] else "FAIL",
    }

    out_dir = evidence_dir(lab_root, lab_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase1_stability_summary.json"
    summary["summary_path"] = out_path.as_posix()
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_regression_check(
    authority: Path,
    lab_root: Path,
    lab_id: str = "proof_gate_regression",
    *,
    runs: int = 1,
) -> dict[str, Any]:
    """
    Programmatic Phase 1 regression for Gate B proof gate.

    Returns pass=True when the canonical stack scores Overall Tier 4 for every run.
    Default runs=1 (single full stack). Use runs=3 for full Phase 1 stability parity.
    """
    summary = run_harness(authority, lab_root, lab_id, runs, use_provisioner=True)
    return {
        "pass": summary["verdict"] == "PASS",
        "verdict": summary["verdict"],
        "runs": runs,
        "decision": summary.get("decision"),
        "summary_path": summary.get("summary_path"),
        "summary": summary,
    }


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("--runs must be >= 1")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Phase 1 stability harness")
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--lab-root", type=Path, default=DEFAULT_LAB_ROOT)
    parser.add_argument("--lab-id", default="m2_001")
    parser.add_argument("--runs", type=positive_int, default=3)
    parser.add_argument(
        "--provisioner",
        action="store_true",
        help="execute the canonical stack through scripts/chaos_lab_provisioner.py",
    )
    args = parser.parse_args()

    summary = run_harness(args.authority, args.lab_root, args.lab_id, args.runs, args.provisioner)
    print(json.dumps(summary, indent=2))
    return 0 if summary["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
