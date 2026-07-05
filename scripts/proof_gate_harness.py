#!/usr/bin/env python3
"""
MMI Proof Gate Harness — Gate B quality control.

A patch is promotable only when it passes proof-of-fix AND proof-of-no-regression
with authority repo read-only throughout.

See: architecture/MMI_AGI_EVOLUTION_PATHWAY.md §5 step 2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUTHORITY = Path("/mnt/c/Architectapp_clean")
DEFAULT_LAB_ROOT = Path("/tmp/mmi_chaos_lab")

SMASH_FAULT_IDS = frozenset(
    {
        "corrupt_tasks_json",
        "stale_pipe_confusion",
        "false_opsec_done",
        "headline_launder",
        "promotion_without_restore",
    }
)


def _ensure_scripts_import(authority: Path) -> None:
    scripts = authority / "scripts"
    if scripts.exists() and str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))


def _ensure_chaos_import(authority: Path) -> None:
    chaos_dir = authority / "mmi/project_brain/chaos"
    if str(chaos_dir) not in sys.path:
        sys.path.insert(0, str(chaos_dir))


def assert_patch_context_outside_authority(patch_context: Path, authority: Path) -> None:
    """Gate B evidence must never be written inside the authority repo."""
    authority_root = authority.resolve()
    paths_to_check = [patch_context.resolve()]
    if patch_context.is_file():
        paths_to_check.append(patch_context.resolve().parent)
    for path in paths_to_check:
        try:
            path.relative_to(authority_root)
        except ValueError:
            continue
        raise SystemExit(
            f"patch-context must not be inside authority repo: {path.as_posix()} "
            f"(authority: {authority_root.as_posix()})"
        )


def normalize_patch_context(patch_context: Path) -> tuple[Path, Path, Path]:
    """
    Return (context_source, evidence_dir, patch_context_label).

    context_source is a proof_context.json path or directory used for optional overrides.
    evidence_dir is always outside authority (caller must assert first).
    """
    if patch_context.is_file():
        base = patch_context.parent
        if base.name == "EVIDENCE":
            evidence = base
            label = base.parent
        else:
            evidence = base / "EVIDENCE"
            label = base
        return patch_context, evidence, label

    if patch_context.name == "EVIDENCE":
        return patch_context.parent, patch_context, patch_context.parent

    return patch_context, patch_context / "EVIDENCE", patch_context


def resolve_evidence_dir(patch_context: Path) -> Path:
    _, evidence, _ = normalize_patch_context(patch_context)
    return evidence


def load_patch_context(context_source: Path, fix_id: str) -> dict[str, Any]:
    if context_source.is_file():
        ctx = json.loads(context_source.read_text(encoding="utf-8"))
    else:
        candidate = context_source / "proof_context.json"
        if candidate.exists():
            ctx = json.loads(candidate.read_text(encoding="utf-8"))
        else:
            ctx = {}
    ctx.setdefault("fix_id", fix_id)
    if ctx["fix_id"] != fix_id:
        raise SystemExit(
            f"proof_context fix_id {ctx['fix_id']!r} does not match --fix-id {fix_id!r}"
        )
    return ctx


def _auto_proof_target(fix_id: str) -> dict[str, Any]:
    if fix_id in {s["id"] for s in _list_purple_scenarios()}:
        return {"proof_type": "purple_scenario", "scenario_id": fix_id}
    if fix_id in SMASH_FAULT_IDS:
        return {"proof_type": "smash_fault", "fault": fix_id}
    if fix_id in {"iceberg_ingress", "iceberg-mirror-smash", "iceberg-ingress"}:
        return {"proof_type": "provisioner", "command": "iceberg-ingress"}
    if fix_id in {"mesh_smash", "mesh-smash"}:
        return {"proof_type": "provisioner", "command": "mesh-smash", "expect_verdict": "PASSED"}
    raise SystemExit(
        f"unknown fix-id {fix_id!r} — provide proof_context.json with proof_type or use a "
        "known purple scenario / smash fault id"
    )


def _assert_context_matches_fix_id(fix_id: str, auto: dict[str, Any], ctx: dict[str, Any]) -> None:
    """Reject proof_context targets that do not match the requested fix-id."""
    proof_type = ctx.get("proof_type")
    if proof_type != auto["proof_type"]:
        raise SystemExit(
            f"proof_context proof_type {proof_type!r} does not match --fix-id {fix_id!r} "
            f"(expected {auto['proof_type']!r})"
        )

    if proof_type == "purple_scenario":
        scenario_id = ctx.get("scenario_id")
        if scenario_id != fix_id:
            raise SystemExit(
                f"proof_context scenario_id {scenario_id!r} must equal --fix-id {fix_id!r}"
            )
    elif proof_type == "smash_fault":
        fault = ctx.get("fault")
        if fault != fix_id:
            raise SystemExit(
                f"proof_context fault {fault!r} must equal --fix-id {fix_id!r}"
            )
    elif proof_type == "provisioner":
        command = ctx.get("command")
        if command != auto["command"]:
            raise SystemExit(
                f"proof_context command {command!r} does not match --fix-id {fix_id!r} "
                f"(expected {auto['command']!r})"
            )
    else:
        raise SystemExit(f"unsupported proof_context proof_type: {proof_type!r}")


def resolve_proof_target(fix_id: str, ctx: dict[str, Any]) -> dict[str, Any]:
    if "expect_verdict" in ctx:
        raise SystemExit(
            "proof_context may not override expect_verdict — pass criteria are fixed by --fix-id"
        )
    auto = _auto_proof_target(fix_id)
    if ctx.get("proof_type"):
        _assert_context_matches_fix_id(fix_id, auto, ctx)
    target = dict(auto)
    if ctx.get("lab_id"):
        target["lab_id"] = ctx["lab_id"]
    return target


def _list_purple_scenarios() -> list[dict[str, Any]]:
    from purple_evasion_suite import list_scenarios  # type: ignore

    return list_scenarios()


def run_proof_of_fix(
    authority: Path,
    lab_root: Path,
    target: dict[str, Any],
) -> dict[str, Any]:
    _ensure_scripts_import(authority)
    _ensure_chaos_import(authority)
    from chaos_lab_provisioner import (  # type: ignore
        detect_only,
        iceberg_ingress_run,
        mesh_smash_m3,
        mirror_root,
        provision,
        smash,
    )
    from mirror_dimension_router import MirrorDimensionRouter  # type: ignore
    from purple_evasion_suite import list_scenarios, run_scenario  # type: ignore

    proof_type = target["proof_type"]
    lab_id = target.get("lab_id", f"proof_fix_{target.get('scenario_id') or target.get('fault') or 'run'}")

    if proof_type == "purple_scenario":
        scenario_id = target["scenario_id"]
        scenarios = [s for s in list_scenarios() if s["id"] == scenario_id]
        if not scenarios:
            raise SystemExit(f"purple scenario not found: {scenario_id}")
        provision(authority, lab_root, lab_id)
        router = MirrorDimensionRouter(mirror_root(lab_root, lab_id))
        result = run_scenario(router, scenarios[0])
        contained = result.get("contained") is True
        return {
            "proof_type": proof_type,
            "scenario_id": scenario_id,
            "verdict": "CONTAINED" if contained else "MISSED",
            "contained": contained,
            "detail": result,
        }

    if proof_type == "smash_fault":
        fault = target["fault"]
        fault_lab = f"{lab_id}__{fault}"
        provision(authority, lab_root, fault_lab)
        smash(authority, lab_root, fault_lab, fault, wire_detection=True)
        detection = detect_only(authority, lab_root, fault_lab, fault)
        detected = detection.get("detected") is True
        return {
            "proof_type": proof_type,
            "fault": fault,
            "verdict": "CONTAINED" if detected else "MISSED",
            "contained": detected,
            "detail": detection,
        }

    if proof_type == "provisioner":
        command = target["command"]
        provision(authority, lab_root, lab_id)
        if command == "iceberg-ingress":
            summary = iceberg_ingress_run(authority, lab_root, lab_id, fresh=False)
            ok = summary.get("verdict") == "PASSED"
        elif command == "mesh-smash":
            summary = mesh_smash_m3(authority, lab_root, lab_id)
            ok = summary.get("verdict") == "PASSED"
        else:
            raise SystemExit(f"unsupported provisioner proof command: {command}")
        return {
            "proof_type": proof_type,
            "command": command,
            "verdict": "CONTAINED" if ok else "MISSED",
            "contained": ok,
            "detail": summary,
        }

    raise SystemExit(f"unsupported proof_type: {proof_type}")


def materialize_patch_diff(evidence: Path, ctx: dict[str, Any]) -> Path | None:
    """Materialize patch.diff under evidence dir; no placeholder synthesis."""
    patch_path = evidence / "patch.diff"
    if ctx.get("patch_source"):
        src = Path(ctx["patch_source"])
        if src.is_file():
            shutil.copyfile(src, patch_path)
            return patch_path
    if ctx.get("patch_content") is not None:
        patch_path.write_text(str(ctx["patch_content"]), encoding="utf-8")
        return patch_path
    if ctx.get("patch_files"):
        parts: list[str] = []
        for rel in ctx["patch_files"]:
            fp = Path(rel)
            if fp.is_file():
                parts.append(fp.read_text(encoding="utf-8"))
        if parts:
            patch_path.write_text("\n".join(parts), encoding="utf-8")
            return patch_path
    return None


def _file_sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_run_id(fix_id: str, evidence_dir: Path, timestamp_ms: int) -> str:
    payload = f"{fix_id}:{evidence_dir.as_posix()}:{timestamp_ms}"
    return f"pg-{fix_id}-{hashlib.sha256(payload.encode()).hexdigest()[:12]}"


def capture_budget_snapshot(run_id: str, timestamp_ms: int) -> dict[str, Any] | None:
    """Read control envelope caps + spend. Zero spend when ledger not yet created."""
    _ensure_chaos_import(DEFAULT_AUTHORITY)
    from mmi_control_envelope import MMIControlEnvelope  # type: ignore

    env = MMIControlEnvelope()
    budget_spent = 0
    if env.ledger_path.exists():
        try:
            ledger = json.loads(env.ledger_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if not isinstance(ledger, dict):
            return None
        budget_spent = int(ledger.get("lifetime_spend", 0))

    deadman_armed = True
    if env.stop_latch_path.exists():
        try:
            latch = json.loads(env.stop_latch_path.read_text(encoding="utf-8"))
            deadman_armed = latch.get("state") in {None, "CLEAR", "SUSPENDED", "HALT"}
        except (json.JSONDecodeError, OSError):
            return None

    return {
        "run_id": run_id,
        "budget_spent": budget_spent,
        "budget_cap_day": env.per_day_cap,
        "budget_cap_hour": env.per_hour_cap,
        "deadman_armed": deadman_armed,
        "captured_at_ms": timestamp_ms,
    }


def apply_console_bindings(
    summary_data: dict[str, Any],
    *,
    evidence: Path,
    patch_label: Path,
    ctx: dict[str, Any],
    fix_id: str,
    overall: str,
    genomic_episode: dict[str, str] | None = None,
) -> dict[str, Any]:
    _ensure_chaos_import(DEFAULT_AUTHORITY)
    from console_fingerprint_ledger import (  # type: ignore
        GENESIS_RUN_ID,
        append_known_good,
        ledger_tail,
    )
    from mmi_canonical_digest import canonical_object_digest  # type: ignore

    timestamp_ms = int(time.time() * 1000)
    run_id = _make_run_id(fix_id, evidence, timestamp_ms)

    patch_path = materialize_patch_diff(evidence, ctx)
    if patch_path is None:
        summary_data["overall_gate_status"] = "BLOCKED"
        summary_data.setdefault("blockers", []).append("patch artifact missing")
        overall = "BLOCKED"

    patch_block: dict[str, Any] = {}
    if patch_path is not None and patch_path.exists():
        patch_block = {
            "patch_path": patch_path.as_posix(),
            "patch_hash": _file_sha256_hex(patch_path),
            "patch_context": patch_label.as_posix(),
        }

    proof_of_fix = summary_data.get("proof_of_fix") or {}
    proof_of_regression = summary_data.get("proof_of_regression") or {}

    tail = ledger_tail()
    if tail:
        prior_digest = tail["fingerprint_digest"]
        prior_run_id = tail["run_id"]
    else:
        prior_digest = None
        prior_run_id = GENESIS_RUN_ID

    authority_hash = summary_data.get("authority_hash", "")
    rollback = {
        "rollback_token_hash": authority_hash,
        "prior_known_good_run_id": prior_run_id,
        "prior_known_good_digest": prior_digest or "",
    }

    budget = capture_budget_snapshot(run_id, timestamp_ms)
    if budget is None and overall == "CLEAN":
        summary_data["overall_gate_status"] = "BLOCKED"
        summary_data.setdefault("blockers", []).append("budget telemetry snapshot unavailable")
        overall = "BLOCKED"

    if prior_digest is None and overall == "CLEAN":
        summary_data["overall_gate_status"] = "BLOCKED"
        summary_data.setdefault("blockers", []).append("fingerprint ledger not seeded")
        overall = "BLOCKED"

    enriched = {
        **summary_data,
        "suite": "proof_gate_v2_console_bindings",
        "run_id": run_id,
        "timestamp_ms": timestamp_ms,
        "patch": patch_block,
        "proof_of_fix_digest": canonical_object_digest(proof_of_fix),
        "proof_of_regression_digest": canonical_object_digest(proof_of_regression),
        "rollback": rollback,
    }
    if budget is not None:
        enriched["budget_telemetry_snapshot"] = budget

    if genomic_episode:
        enriched["genomic_episode"] = genomic_episode

    if overall == "CLEAN" and authority_hash:
        append_known_good(run_id, authority_hash, "proof_gate", timestamp_ms)

    return enriched


def run_proof_gate(
    authority: Path,
    lab_root: Path,
    fix_id: str,
    patch_context: Path,
    *,
    regression_runs: int = 1,
    console_bindings: bool = False,
    constraint_id: str | None = None,
    episode_id: str | None = None,
    patch_context_digest: str | None = None,
) -> dict[str, Any]:
    _ensure_scripts_import(authority)
    _ensure_chaos_import(authority)
    from chaos_lab_provisioner import authority_fingerprint, snapshot_authority_fingerprint  # type: ignore
    from phase1_stability_harness import run_regression_check  # type: ignore
    from weapon_battlefield_scoring import fingerprint_digest, generate_proof_bundle  # type: ignore

    assert_patch_context_outside_authority(patch_context, authority)
    context_source, evidence, patch_label = normalize_patch_context(patch_context)
    ctx = load_patch_context(context_source, fix_id)
    target = resolve_proof_target(fix_id, ctx)
    evidence.mkdir(parents=True, exist_ok=True)

    fp_before = snapshot_authority_fingerprint(evidence, authority, operation="proof_gate")
    authority_hash = fingerprint_digest(fp_before)
    timestamp = datetime.now(timezone.utc).isoformat()

    blockers: list[str] = []
    fix_result = run_proof_of_fix(authority, lab_root, target)
    fix_verdict = fix_result["verdict"]
    if fix_verdict != "CONTAINED":
        blockers.append(f"proof-of-fix failed for {fix_id}: {fix_verdict}")

    regression = run_regression_check(
        authority,
        lab_root,
        lab_id=f"proof_gate_regression_{fix_id}",
        runs=regression_runs,
    )
    regression_verdict = "PASS" if regression["pass"] else "FAIL"
    if regression_verdict != "PASS":
        blockers.append(f"proof-of-no-regression failed: {regression_verdict}")

    fp_after = authority_fingerprint(authority)
    authority_intact = fp_before.get("files") == fp_after.get("files")
    if not authority_intact:
        blockers.append("authority repo fingerprint diverged during proof gate")

    overall = "CLEAN" if not blockers else "BLOCKED"
    summary_data = {
        "fix_id": fix_id,
        "timestamp": timestamp,
        "authority_hash": authority_hash,
        "authority_intact": authority_intact,
        "regression_verdict": regression_verdict,
        "regression_runs": regression_runs,
        "fix_verdict": fix_verdict,
        "overall_gate_status": overall,
        "blockers": blockers,
        "proof_of_fix": fix_result,
        "proof_of_regression": {
            "verdict": regression_verdict,
            "runs": regression_runs,
            "summary_path": regression.get("summary_path"),
            "decision": regression.get("decision"),
        },
        "patch_context": patch_label.as_posix(),
        "evidence_dir": evidence.as_posix(),
        "authority_fingerprint_after_digest": fingerprint_digest(fp_after),
    }
    if console_bindings:
        genomic_episode = None
        if constraint_id or episode_id or patch_context_digest:
            from mmi_canonical_digest import patch_context_tree_digest  # type: ignore

            digest = patch_context_digest or patch_context_tree_digest(patch_label)
            genomic_episode = {
                "constraint_id": constraint_id or "",
                "patch_context_digest": digest,
            }
            if episode_id:
                genomic_episode["episode_id"] = episode_id
            if not constraint_id:
                summary_data["overall_gate_status"] = "BLOCKED"
                summary_data.setdefault("blockers", []).append("genomic episode missing constraint_id")
                overall = "BLOCKED"
        summary_data = apply_console_bindings(
            summary_data,
            evidence=evidence,
            patch_label=patch_label,
            ctx=ctx,
            fix_id=fix_id,
            overall=overall,
            genomic_episode=genomic_episode,
        )
        overall = summary_data.get("overall_gate_status", overall)
    return generate_proof_bundle(summary_data, evidence)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Proof Gate Harness (Gate B)")
    parser.add_argument("--fix-id", required=True, help="heal target id (scenario, fault, or named fix)")
    parser.add_argument(
        "--patch-context",
        type=Path,
        required=True,
        help="directory for EVIDENCE/, or path to proof_context.json file",
    )
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--lab-root", type=Path, default=DEFAULT_LAB_ROOT)
    parser.add_argument(
        "--regression-runs",
        type=positive_int,
        default=1,
        help="canonical stack regression runs (1=Gate B default; 3=Phase 1 parity)",
    )
    parser.add_argument(
        "--console-bindings",
        action="store_true",
        help="emit proof_gate_v2_console_bindings summary fields",
    )
    parser.add_argument(
        "--constraint-id",
        default=None,
        help="genomic episode constraint_id for H14 binding (requires --console-bindings)",
    )
    parser.add_argument(
        "--episode-id",
        default=None,
        help="optional genomic episode_id audit cross-ref",
    )
    parser.add_argument(
        "--patch-context-digest",
        default=None,
        help="optional patch context tree digest; computed from --patch-context if omitted",
    )
    args = parser.parse_args()

    if not args.authority.exists():
        print(json.dumps({"error": f"authority root not found: {args.authority}"}), file=sys.stderr)
        return 2

    try:
        assert_patch_context_outside_authority(args.patch_context, args.authority)
    except SystemExit as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    _, evidence_dir, _ = normalize_patch_context(args.patch_context)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    if not args.patch_context.is_file():
        args.patch_context.mkdir(parents=True, exist_ok=True)

    bundle = run_proof_gate(
        args.authority,
        args.lab_root,
        args.fix_id,
        args.patch_context,
        regression_runs=args.regression_runs,
        console_bindings=args.console_bindings,
        constraint_id=args.constraint_id,
        episode_id=args.episode_id,
        patch_context_digest=args.patch_context_digest,
    )
    print(json.dumps(bundle, indent=2))
    return 0 if bundle["overall_gate_status"] == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
