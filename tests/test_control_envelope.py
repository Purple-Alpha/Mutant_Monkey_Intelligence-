from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

CHAOS = Path(__file__).resolve().parents[1] / "mmi" / "project_brain" / "chaos"
if str(CHAOS) not in sys.path:
    sys.path.insert(0, str(CHAOS))

from mmi_control_envelope import (  # noqa: E402
    ACK_STALE_MS,
    RESTART_MAX_COUNT,
    ControlEnvelopeError,
    MMIControlEnvelope,
    RUNAWAY_SPIKE_FACTOR,
    assert_path_outside_authority,
    human_advance_ack,
    human_clear_halt_latch,
    human_clear_suspend_latch,
)


@pytest.fixture
def authority(tmp_path: Path) -> Path:
    root = tmp_path / "authority"
    root.mkdir()
    return root


@pytest.fixture
def state_root(tmp_path: Path) -> Path:
    root = tmp_path / "envelope_state"
    root.mkdir()
    return root


def _env(authority: Path, state_root: Path, now_ms: int = 1_700_000_000_000, **kwargs) -> MMIControlEnvelope:
    return MMIControlEnvelope.for_testing(
        now_ms=now_ms,
        state_root=state_root,
        authority_root=authority,
        run_id="test_run",
        **kwargs,
    )


def test_production_constructor_has_no_test_clock(authority: Path, state_root: Path) -> None:
    sig = inspect.signature(MMIControlEnvelope.__init__)
    assert "_test_now_ms" not in sig.parameters
    assert "now_ms" not in sig.parameters

    env = MMIControlEnvelope(state_root=state_root, authority_root=authority, run_id="prod")
    assert env._allow_test_clock is False
    with pytest.raises(RuntimeError, match="test clock"):
        env.set_test_clock_ms(1)


def test_enforce_boundary_v0_unchanged(authority: Path, state_root: Path) -> None:
    env = _env(authority, state_root)
    ok, out = env.enforce_boundary('{"action": "ping"}', {"action": str})
    assert ok is True
    assert "ping" in out
    bad, err = env.enforce_boundary("x" * 3000, {})
    assert bad is False


def test_path_inside_authority_rejected(authority: Path) -> None:
    inside = authority / "bad"
    inside.mkdir()
    with pytest.raises(ControlEnvelopeError):
        assert_path_outside_authority(inside, authority)


def test_t1_budget_breach_and_tamper(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now, per_hour_cap=100, per_day_cap=10_000)
    human_advance_ack(env, 1, last_ack_ms=now)

    for _ in range(101):
        env.record_spend(1)

    proceed, detail = env.pre_iteration_gate()
    assert proceed is False
    assert detail["verdict"] == "SUSPENDED"
    assert env.stop_latch_path.exists()

    ledger = json.loads(env.ledger_path.read_text(encoding="utf-8"))
    ledger["lifetime_spend"] = 0
    env.ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    proceed2, detail2 = env.pre_iteration_gate()
    assert proceed2 is False
    assert detail2["latched"] is True


def test_deleted_ledger_fail_closed(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now, per_hour_cap=100, per_day_cap=10_000)
    human_advance_ack(env, 1, last_ack_ms=now)
    env.record_spend(10)
    env.ledger_path.unlink()

    ok, detail = env.check_budget()
    assert ok is False
    assert detail["verdict"] == "SUSPENDED"
    assert detail["reason"] == "LEDGER_FAULT"


def test_t2_stale_ack_despite_liveness(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now)
    env.record_heartbeat()
    proceed, detail = env.pre_iteration_gate()
    assert proceed is False
    assert detail["verdict"] == "HALTED"
    hb = detail.get("heartbeat") or {}
    assert hb.get("reason") == "STALE_ACK"

    sig = inspect.signature(env.record_heartbeat)
    assert "ack" not in sig.parameters


def test_t2_missing_heartbeat_file_halts(authority: Path, state_root: Path) -> None:
    env = _env(authority, state_root / "fresh", 1_700_000_000_000)
    proceed, detail = env.pre_iteration_gate()
    assert proceed is False
    assert detail["verdict"] == "HALTED"


def test_t3_runaway_spike_and_sticky_latch(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now, per_hour_cap=800_000, per_day_cap=8_000_000)
    human_advance_ack(env, 1, last_ack_ms=now)

    for amount in [1000] * 5:
        env.record_spend(amount)
    env.record_spend(4001)

    proceed, detail = env.pre_iteration_gate()
    assert proceed is False
    assert detail["verdict"] == "HALTED"

    human_advance_ack(env, 2, last_ack_ms=now + 1)
    env.set_test_clock_ms(now + 2_000_000)
    proceed2, detail2 = env.pre_iteration_gate()
    assert proceed2 is False
    assert detail2["latched"] is True


def test_t3_restart_loop(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root / "restart", now)
    human_advance_ack(env, 1, last_ack_ms=now)

    for _ in range(RESTART_MAX_COUNT + 1):
        env.record_process_start()

    ok, detail = env.check_heartbeat()
    assert ok is False
    assert detail["reason"] == "RESTART_LOOP"
    assert env.stop_latch_path.exists()


def test_t3_restart_loop_boundary(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root / "restart_boundary", now)
    human_advance_ack(env, 1, last_ack_ms=now)

    for _ in range(RESTART_MAX_COUNT):
        env.record_process_start()

    env.record_heartbeat()
    ok, _ = env.check_heartbeat()
    assert ok is True


def test_t3_exclusive_boundary(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root / "boundary", now, per_hour_cap=800_000, per_day_cap=8_000_000)
    human_advance_ack(env, 1, last_ack_ms=now)
    for amount in [1000] * 5:
        env.record_spend(amount)
    env.record_spend(RUNAWAY_SPIKE_FACTOR * 1000)
    env.record_heartbeat()
    ok, _ = env.check_heartbeat()
    assert ok is True


def test_human_clear_latches(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now, per_hour_cap=10, per_day_cap=100)
    human_advance_ack(env, 1, last_ack_ms=now)
    env.record_spend(11)
    env.pre_iteration_gate()
    human_clear_suspend_latch(env)
    assert not env.stop_latch_path.exists()

    env2 = _env(authority, state_root / "halt", now + ACK_STALE_MS + 1)
    human_advance_ack(env2, 1, last_ack_ms=now)
    env2.record_heartbeat()
    env2.pre_iteration_gate()
    assert env2.stop_latch_path.exists()
    required = json.loads(env2.stop_latch_path.read_text())["required_resume_seq"]
    human_clear_halt_latch(env2, required)
    assert not env2.stop_latch_path.exists()


def test_no_kinetic_telemetry_import() -> None:
    import mmi_control_envelope as mod

    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "kinetic_telemetry" not in source


def test_stale_ack_by_age(authority: Path, state_root: Path) -> None:
    now = 1_700_000_000_000
    env = _env(authority, state_root, now + ACK_STALE_MS + 1)
    human_advance_ack(env, 1, last_ack_ms=now)
    env.record_heartbeat()
    ok, detail = env.check_heartbeat()
    assert ok is False
    assert detail["reason"] == "STALE_ACK"
