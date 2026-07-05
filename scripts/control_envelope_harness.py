#!/usr/bin/env python3
"""
MMI Control Envelope Harness — AGI §5 step 3 smoke scenarios T1–T3.

Mirrors proof_gate_harness.py: evidence outside authority, fingerprint intact.

See: architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md §6
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_AUTHORITY = Path("/mnt/c/Architectapp_clean")
DEFAULT_STATE_ROOT = Path("/tmp/mmi_control_envelope")


def _ensure_chaos_import(authority: Path) -> None:
    chaos_dir = authority / "mmi/project_brain/chaos"
    if str(chaos_dir) not in sys.path:
        sys.path.insert(0, str(chaos_dir))


def _ensure_scripts_import(authority: Path) -> None:
    scripts = authority / "scripts"
    if scripts.exists() and str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))


def _fingerprint(authority: Path) -> dict[str, Any]:
    _ensure_scripts_import(authority)
    from chaos_lab_provisioner import authority_fingerprint  # type: ignore

    return authority_fingerprint(authority)


def _fresh_envelope(
    authority: Path,
    state_root: Path,
    run_id: str,
    *,
    per_hour_cap: int,
    per_day_cap: int,
    now_ms: int,
):
    _ensure_chaos_import(authority)
    from mmi_control_envelope import MMIControlEnvelope, human_advance_ack  # type: ignore

    env = MMIControlEnvelope.for_testing(
        now_ms=now_ms,
        state_root=state_root,
        authority_root=authority,
        run_id=run_id,
        per_hour_cap=per_hour_cap,
        per_day_cap=per_day_cap,
    )
    human_advance_ack(env, 1, last_ack_ms=now_ms)
    return env


def scenario_t1_budget_breach(authority: Path, state_root: Path, run_id: str) -> dict[str, Any]:
    now = 1_700_000_000_000
    env = _fresh_envelope(authority, state_root, run_id, per_hour_cap=100, per_day_cap=10_000, now_ms=now)

    for _ in range(101):
        env.record_spend(1)

    proceed, detail = env.pre_iteration_gate()
    latch_exists = env.stop_latch_path.exists()
    alert_path = detail.get("evidence_path") or (detail.get("budget") or {}).get("alert_path")
    alert_exists = bool(alert_path and Path(alert_path).exists())

    tamper_ok = True
    if env.ledger_path.exists():
        ledger = json.loads(env.ledger_path.read_text(encoding="utf-8"))
        ledger["lifetime_spend"] = 0
        ledger["events"] = []
        env.ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        proceed2, detail2 = env.pre_iteration_gate()
        tamper_ok = not proceed2 and detail2.get("latched") is True

    clean = (
        not proceed
        and detail.get("verdict") == "SUSPENDED"
        and latch_exists
        and alert_exists
        and tamper_ok
    )
    return {
        "scenario": "t1-budget-breach",
        "verdict": "SUSPENDED" if not proceed else detail.get("verdict"),
        "reason": (detail.get("budget") or {}).get("reason") or detail.get("reason"),
        "proceed": proceed,
        "latch_path": env.stop_latch_path.as_posix(),
        "evidence_path": alert_path,
        "overall_gate_status": "CLEAN" if clean else "BLOCKED",
        "detail": detail,
    }


def scenario_t2_stale_ack(authority: Path, state_root: Path, run_id: str) -> dict[str, Any]:
    now = 1_700_000_000_000
    _ensure_chaos_import(authority)
    from mmi_control_envelope import MMIControlEnvelope  # type: ignore

    env = MMIControlEnvelope.for_testing(
        now_ms=now,
        state_root=state_root,
        authority_root=authority,
        run_id=run_id,
        per_hour_cap=500_000,
        per_day_cap=5_000_000,
    )
    env.record_heartbeat()
    proceed, detail = env.pre_iteration_gate()

    missing_ok = False
    env2 = MMIControlEnvelope.for_testing(
        now_ms=now,
        state_root=state_root / "missing_hb",
        authority_root=authority,
        run_id=run_id + "_b",
    )
    p2, d2 = env2.pre_iteration_gate()
    missing_ok = not p2 and d2.get("verdict") == "HALTED"

    import inspect

    no_ack_arg = "ack" not in inspect.signature(env.record_heartbeat).parameters

    clean = (
        not proceed
        and detail.get("verdict") == "HALTED"
        and (detail.get("heartbeat") or {}).get("reason") == "STALE_ACK"
        and env.stop_latch_path.exists()
        and missing_ok
        and no_ack_arg
    )
    evidence = (detail.get("heartbeat") or {}).get("evidence_path") or detail.get("evidence_path")
    return {
        "scenario": "t2-deadman-stale-ack",
        "verdict": detail.get("verdict"),
        "reason": (detail.get("heartbeat") or {}).get("reason") or detail.get("reason"),
        "proceed": proceed,
        "latch_path": env.stop_latch_path.as_posix(),
        "evidence_path": evidence,
        "overall_gate_status": "CLEAN" if clean else "BLOCKED",
        "detail": detail,
    }


def scenario_t3_runaway_latch(authority: Path, state_root: Path, run_id: str) -> dict[str, Any]:
    now = 1_700_000_000_000
    _ensure_chaos_import(authority)
    from mmi_control_envelope import RESTART_MAX_COUNT, human_advance_ack  # type: ignore

    env = _fresh_envelope(authority, state_root, run_id, per_hour_cap=800_000, per_day_cap=8_000_000, now_ms=now)

    for amount in [1000, 1000, 1000, 1000, 1000]:
        env.record_spend(amount)

    env.record_spend(4001)
    proceed, detail = env.pre_iteration_gate()
    spike_halt = not proceed and detail.get("verdict") == "HALTED"
    spike_reason = (detail.get("heartbeat") or {}).get("reason") or detail.get("reason")

    human_advance_ack(env, 2, last_ack_ms=now + 1)
    env.set_test_clock_ms(now + 2_000_000)
    proceed2, detail2 = env.pre_iteration_gate()
    sticky = not proceed2 and detail2.get("latched") is True

    boundary_ok = True
    env_b = _fresh_envelope(
        authority,
        state_root / "boundary",
        run_id + "_boundary",
        per_hour_cap=800_000,
        per_day_cap=8_000_000,
        now_ms=now,
    )
    for amount in [1000, 1000, 1000, 1000, 1000]:
        env_b.record_spend(amount)
    env_b.record_spend(4000)
    env_b.record_heartbeat()
    p_b, _ = env_b.check_heartbeat()
    boundary_ok = p_b is True

    env_r = _fresh_envelope(
        authority,
        state_root / "restart",
        run_id + "_restart",
        per_hour_cap=800_000,
        per_day_cap=8_000_000,
        now_ms=now,
    )
    for _ in range(RESTART_MAX_COUNT + 1):
        env_r.record_process_start()
    p_r, d_r = env_r.check_heartbeat()
    restart_halt = not p_r and d_r.get("reason") == "RESTART_LOOP"

    env_rb = _fresh_envelope(
        authority,
        state_root / "restart_boundary",
        run_id + "_restart_boundary",
        per_hour_cap=800_000,
        per_day_cap=8_000_000,
        now_ms=now,
    )
    for _ in range(RESTART_MAX_COUNT):
        env_rb.record_process_start()
    env_rb.record_heartbeat()
    p_rb, _ = env_rb.check_heartbeat()
    restart_boundary_ok = p_rb is True

    clean = spike_halt and sticky and boundary_ok and restart_halt and restart_boundary_ok
    evidence = detail.get("evidence_path") or (detail.get("heartbeat") or {}).get("evidence_path")
    return {
        "scenario": "t3-runaway-latch",
        "verdict": detail.get("verdict"),
        "reason": spike_reason,
        "proceed": proceed,
        "latch_path": env.stop_latch_path.as_posix(),
        "evidence_path": evidence,
        "overall_gate_status": "CLEAN" if clean else "BLOCKED",
        "sticky_after_fresh_ack": sticky,
        "boundary_exclusive_ok": boundary_ok,
        "restart_loop_halt": restart_halt,
        "restart_loop_boundary_ok": restart_boundary_ok,
        "detail": detail,
    }


SCENARIOS = {
    "t1-budget-breach": scenario_t1_budget_breach,
    "t2-deadman-stale-ack": scenario_t2_stale_ack,
    "t3-runaway-latch": scenario_t3_runaway_latch,
}


def run_harness(
    authority: Path,
    state_root: Path,
    run_id: str,
    scenario: str,
) -> dict[str, Any]:
    fp_before = _fingerprint(authority)
    if scenario == "all":
        results = [fn(authority, state_root / name, f"{run_id}_{name}") for name, fn in SCENARIOS.items()]
        overall = "CLEAN" if all(r["overall_gate_status"] == "CLEAN" for r in results) else "BLOCKED"
        summary = {
            "suite": "control_envelope_harness_v1",
            "scenario": "all",
            "overall_gate_status": overall,
            "results": results,
            "authority_intact": _fingerprint(authority).get("files") == fp_before.get("files"),
        }
        return summary

    fn = SCENARIOS.get(scenario)
    if fn is None:
        raise SystemExit(f"unknown scenario: {scenario}")
    result = fn(authority, state_root / scenario, run_id)
    fp_after = _fingerprint(authority)
    result["suite"] = "control_envelope_harness_v1"
    result["authority_intact"] = fp_before.get("files") == fp_after.get("files")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Control Envelope Harness (AGI §5 step 3)")
    parser.add_argument(
        "--scenario",
        default="all",
        choices=["all", *SCENARIOS.keys()],
    )
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--run-id", default="harness_run")
    args = parser.parse_args()

    if not args.authority.exists():
        print(json.dumps({"error": f"authority root not found: {args.authority}"}), file=sys.stderr)
        return 2

    try:
        summary = run_harness(args.authority, args.state_root, args.run_id, args.scenario)
    except Exception as exc:  # harness boundary — surface setup failures
        print(json.dumps({"error": str(exc), "overall_gate_status": "BLOCKED"}), file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2))
    return 0 if summary.get("overall_gate_status") == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
