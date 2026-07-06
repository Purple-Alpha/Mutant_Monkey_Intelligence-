"""
MMI Control Envelope — bounded v0 output gate + loop governor (AGI §5 step 3).

`enforce_boundary()` validates agent output shape (v0, unchanged).
Budget ceiling + dead-man switch govern self-directed loop iteration.

See: architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

# --- Spec constants (§1) ---
SPEND_UNIT = "tokens"
DEFAULT_PER_HOUR_CAP = 800_000
DEFAULT_PER_DAY_CAP = 8_000_000
HOUR_WINDOW_MS = 3_600_000
DAY_WINDOW_MS = 86_400_000
HEARTBEAT_INTERVAL_MIN = 15
HEARTBEAT_INTERVAL_MS = 900_000
ACK_STALE_MS = 1_800_000
RUNAWAY_SPIKE_FACTOR = 4
RUNAWAY_SPIKE_MIN_SAMPLES = 5
RESTART_WINDOW_MS = 900_000
RESTART_MAX_COUNT = 3
DEFAULT_STATE_ROOT = Path("/tmp/mmi_control_envelope")
LEDGER_SCHEMA_VERSION = 2
HEARTBEAT_SCHEMA_VERSION = 2
TRAILING_SPEND_RING_LEN = RUNAWAY_SPIKE_MIN_SAMPLES


class ControlEnvelopeError(Exception):
    """Fail-closed abort when a state/evidence path resolves inside authority."""


def _utc_now_ms() -> int:
    return int(time.time() * 1000)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def assert_path_outside_authority(target: Path, authority_root: Path) -> Path:
    """Canonicalize and abort if target is inside authority repo."""
    authority = authority_root.resolve()
    resolved = target.resolve()
    try:
        resolved.relative_to(authority)
    except ValueError:
        return resolved
    raise ControlEnvelopeError(
        f"path must not be inside authority repo: {resolved.as_posix()} "
        f"(authority: {authority.as_posix()})"
    )


class MMIControlEnvelope:
    def __init__(
        self,
        max_token_length: int = 2048,
        *,
        state_root: Path | str | None = None,
        authority_root: Path | str | None = None,
        run_id: str | None = None,
        per_hour_cap: int | None = None,
        per_day_cap: int | None = None,
    ):
        self.max_length = max_token_length
        self.forbidden_directives = [
            r"(?i)ignore\s+all\s+previous",
            r"(?i)you\s+are\s+now\s+in\s+developer",
            r"(?i)system\s+override",
            r"rm\s+-rf",
            r"chmod\s+\+x",
        ]
        self.state_root = Path(state_root or DEFAULT_STATE_ROOT)
        self.authority_root = Path(authority_root or "/mnt/c/MMI")
        self.run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ-") + uuid.uuid4().hex[:4]
        self.per_hour_cap = per_hour_cap if per_hour_cap is not None else DEFAULT_PER_HOUR_CAP
        self.per_day_cap = per_day_cap if per_day_cap is not None else DEFAULT_PER_DAY_CAP
        self._allow_test_clock = False
        self._clock_override_ms: int | None = None

        self.ledger_path = self.state_root / "state" / "spend_ledger.json"
        self.heartbeat_path = self.state_root / "state" / "heartbeat.json"
        self.stop_latch_path = self.state_root / "state" / "stop_latch.json"
        self.evidence_root = self.state_root / self.run_id / "EVIDENCE"

        for path in (self.ledger_path, self.heartbeat_path, self.stop_latch_path, self.evidence_root):
            assert_path_outside_authority(path, self.authority_root)

    @classmethod
    def for_testing(
        cls,
        *,
        now_ms: int,
        max_token_length: int = 2048,
        state_root: Path | str | None = None,
        authority_root: Path | str | None = None,
        run_id: str | None = None,
        per_hour_cap: int | None = None,
        per_day_cap: int | None = None,
    ) -> MMIControlEnvelope:
        """Harness/pytest only — production callers must use __init__ (wall clock only)."""
        env = cls(
            max_token_length=max_token_length,
            state_root=state_root,
            authority_root=authority_root,
            run_id=run_id,
            per_hour_cap=per_hour_cap,
            per_day_cap=per_day_cap,
        )
        env._allow_test_clock = True
        env._clock_override_ms = now_ms
        return env

    def set_test_clock_ms(self, now_ms: int) -> None:
        """Advance frozen test clock — for_testing instances only."""
        if not self._allow_test_clock:
            raise RuntimeError("test clock is not available on production envelope instances")
        self._clock_override_ms = now_ms

    def _now_ms(self) -> int:
        if self._allow_test_clock and self._clock_override_ms is not None:
            return self._clock_override_ms
        return _utc_now_ms()

    def enforce_boundary(self, raw_agent_output: str, expected_schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates raw agent output against structural invariants before system execution."""
        if len(raw_agent_output) > self.max_length:
            return False, "CRITICAL_ERROR: Agent output exceeded hard volumetric token boundary."

        for pattern in self.forbidden_directives:
            if re.search(pattern, raw_agent_output):
                return False, f"CRITICAL_ERROR: Structural violation detected via signature match: '{pattern}'."

        try:
            parsed_json = json.loads(raw_agent_output)
            for key, expected_type in expected_schema.items():
                if key not in parsed_json:
                    return False, f"SCHEMA_ERROR: Missing required runtime execution key: '{key}'."
                if not isinstance(parsed_json[key], expected_type):
                    return False, f"SCHEMA_ERROR: Type mismatch for key '{key}'. Expected {expected_type}."

            return True, json.dumps(parsed_json)

        except json.JSONDecodeError:
            return False, "SCHEMA_ERROR: Output failed basic JSON structural formatting constraints."

    # --- Budget + dead-man (additive) ---

    def _assert_write_path(self, path: Path) -> None:
        assert_path_outside_authority(path, self.authority_root)

    def _default_ledger(self) -> dict[str, Any]:
        return {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "run_id": self.run_id,
            "lifetime_spend": 0,
            "lifetime_starts": 0,
            "events": [],
        }

    def _default_heartbeat(self) -> dict[str, Any]:
        return {
            "schema_version": HEARTBEAT_SCHEMA_VERSION,
            "last_heartbeat_ms": 0,
            "last_ack_ms": 0,
            "ack_seq": 0,
            "resume_seq": 0,
            "recent_starts_ms": [],
            "trailing_spend": [],
            "witness_lifetime_spend": 0,
            "witness_lifetime_starts": 0,
        }

    def _load_ledger(self) -> dict[str, Any]:
        data = _read_json(self.ledger_path)
        if data is None:
            return self._default_ledger()
        return data

    def _load_heartbeat(self) -> dict[str, Any]:
        data = _read_json(self.heartbeat_path)
        if data is None:
            return self._default_heartbeat()
        return data

    def _save_ledger(self, ledger: dict[str, Any]) -> None:
        self._assert_write_path(self.ledger_path)
        _atomic_write_json(self.ledger_path, ledger)

    def _save_heartbeat(self, heartbeat: dict[str, Any]) -> None:
        self._assert_write_path(self.heartbeat_path)
        _atomic_write_json(self.heartbeat_path, heartbeat)

    def _prune_events(self, ledger: dict[str, Any], now_ms: int) -> None:
        cutoff = now_ms - DAY_WINDOW_MS
        events = ledger.get("events") or []
        ledger["events"] = [e for e in events if int(e.get("ts_ms", 0)) >= cutoff]

    def _window_spend(self, ledger: dict[str, Any], now_ms: int, window_ms: int) -> int:
        cutoff = now_ms - window_ms
        return sum(int(e.get("amount", 0)) for e in ledger.get("events", []) if int(e.get("ts_ms", 0)) >= cutoff)

    def _sync_witness_from_ledger(self, ledger: dict[str, Any], heartbeat: dict[str, Any]) -> None:
        heartbeat["witness_lifetime_spend"] = int(ledger.get("lifetime_spend", 0))
        heartbeat["witness_lifetime_starts"] = int(ledger.get("lifetime_starts", 0))

    def _verify_seal(self, ledger: dict[str, Any], heartbeat: dict[str, Any]) -> str | None:
        lifetime_spend = int(ledger.get("lifetime_spend", 0))
        lifetime_starts = int(ledger.get("lifetime_starts", 0))
        witness_spend = int(heartbeat.get("witness_lifetime_spend", 0))
        witness_starts = int(heartbeat.get("witness_lifetime_starts", 0))

        if lifetime_spend < witness_spend or lifetime_starts < witness_starts:
            return "LEDGER_TAMPER"
        if witness_spend > lifetime_spend or witness_starts > lifetime_starts:
            return "LEDGER_TAMPER"

        now_ms = self._now_ms()
        hour_spend = self._window_spend(ledger, now_ms, HOUR_WINDOW_MS)
        day_spend = self._window_spend(ledger, now_ms, DAY_WINDOW_MS)
        if hour_spend > lifetime_spend or day_spend > lifetime_spend:
            return "LEDGER_TAMPER"
        return None

    def _write_evidence(self, name: str, payload: dict[str, Any]) -> Path:
        self.evidence_root.mkdir(parents=True, exist_ok=True)
        path = self.evidence_root / name
        self._assert_write_path(path)
        _atomic_write_json(path, payload)
        return path

    def _write_stop_latch(self, verdict: str, reason: str, evidence_path: Path) -> None:
        latch = {
            "verdict": verdict,
            "reason": reason,
            "since_ms": self._now_ms(),
            "evidence_path": evidence_path.as_posix(),
        }
        if verdict == "HALTED":
            heartbeat = self._load_heartbeat()
            required = int(heartbeat.get("resume_seq", 0)) + 1
            latch["clears_on"] = f"resume_seq>={required}"
            latch["required_resume_seq"] = required
        self._assert_write_path(self.stop_latch_path)
        _atomic_write_json(self.stop_latch_path, latch)

    def _read_stop_latch(self) -> dict[str, Any] | None:
        return _read_json(self.stop_latch_path)

    def record_process_start(self) -> None:
        """Loop startup marker — advances lifetime_starts for restart detection."""
        now_ms = self._now_ms()
        ledger = self._load_ledger()
        heartbeat = self._load_heartbeat()
        ledger["lifetime_starts"] = int(ledger.get("lifetime_starts", 0)) + 1
        self._prune_events(ledger, now_ms)
        self._save_ledger(ledger)
        starts = list(heartbeat.get("recent_starts_ms") or [])
        starts.append(now_ms)
        cutoff = now_ms - RESTART_WINDOW_MS
        heartbeat["recent_starts_ms"] = [s for s in starts if s >= cutoff]
        self._sync_witness_from_ledger(ledger, heartbeat)
        self._save_heartbeat(heartbeat)

    def record_spend(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        now_ms = self._now_ms()
        ledger = self._load_ledger()
        heartbeat = self._load_heartbeat()

        ring = list(heartbeat.get("trailing_spend") or [])
        if len(ring) >= RUNAWAY_SPIKE_MIN_SAMPLES:
            mean = sum(ring) / len(ring)
            if mean > 0 and amount > RUNAWAY_SPIKE_FACTOR * mean:
                heartbeat["trailing_spend"] = ring
                self._save_heartbeat(heartbeat)
                self._heartbeat_halt("RUNAWAY_COST_SPIKE", heartbeat, now_ms, ledger)
                return

        ledger["lifetime_spend"] = int(ledger.get("lifetime_spend", 0)) + amount
        events = list(ledger.get("events") or [])
        events.append({"ts_ms": now_ms, "amount": amount})
        ledger["events"] = events
        self._prune_events(ledger, now_ms)
        self._save_ledger(ledger)

        ring.append(amount)
        heartbeat["trailing_spend"] = ring[-TRAILING_SPEND_RING_LEN:]
        self._sync_witness_from_ledger(ledger, heartbeat)
        self._save_heartbeat(heartbeat)

    def _run_established(self, heartbeat_raw: dict[str, Any] | None) -> bool:
        if self.ledger_path.exists():
            return True
        if heartbeat_raw is None:
            return False
        if int(heartbeat_raw.get("witness_lifetime_spend", 0)) > 0:
            return True
        if int(heartbeat_raw.get("witness_lifetime_starts", 0)) > 0:
            return True
        if int(heartbeat_raw.get("last_heartbeat_ms", 0)) > 0:
            return True
        if int(heartbeat_raw.get("ack_seq", 0)) > 0:
            return True
        return False

    def check_budget(self) -> tuple[bool, dict[str, Any]]:
        now_ms = self._now_ms()
        heartbeat_raw = _read_json(self.heartbeat_path)
        ledger_raw = _read_json(self.ledger_path)

        if ledger_raw is None:
            if self.ledger_path.exists() or self._run_established(heartbeat_raw):
                ledger = self._default_ledger()
                heartbeat = heartbeat_raw if heartbeat_raw is not None else self._default_heartbeat()
                return self._budget_stop("LEDGER_FAULT", ledger, heartbeat, now_ms)
            return True, {"verdict": "BUDGET_OK", "hour_spend": 0, "day_spend": 0}

        ledger = ledger_raw
        heartbeat = heartbeat_raw if heartbeat_raw is not None else self._default_heartbeat()

        tamper = self._verify_seal(ledger, heartbeat)
        if tamper:
            return self._budget_stop(tamper, ledger, heartbeat, now_ms)

        hour_spend = self._window_spend(ledger, now_ms, HOUR_WINDOW_MS)
        day_spend = self._window_spend(ledger, now_ms, DAY_WINDOW_MS)

        if hour_spend > self.per_hour_cap:
            return self._budget_stop("HOUR_CAP_EXCEEDED", ledger, heartbeat, now_ms, hour_spend, day_spend)
        if day_spend > self.per_day_cap:
            return self._budget_stop("DAY_CAP_EXCEEDED", ledger, heartbeat, now_ms, hour_spend, day_spend)

        return True, {
            "verdict": "BUDGET_OK",
            "hour_spend": hour_spend,
            "day_spend": day_spend,
        }

    def _budget_stop(
        self,
        reason: str,
        ledger: dict[str, Any],
        heartbeat: dict[str, Any],
        now_ms: int,
        hour_spend: int | None = None,
        day_spend: int | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        if hour_spend is None:
            hour_spend = self._window_spend(ledger, now_ms, HOUR_WINDOW_MS)
        if day_spend is None:
            day_spend = self._window_spend(ledger, now_ms, DAY_WINDOW_MS)
        evidence = {
            "verdict": "SUSPENDED",
            "reason": reason,
            "detected_ts_ms": now_ms,
            "hour_spend": hour_spend,
            "day_spend": day_spend,
            "lifetime_spend": int(ledger.get("lifetime_spend", 0)),
            "constants_snapshot": {
                "per_hour_cap": self.per_hour_cap,
                "per_day_cap": self.per_day_cap,
            },
        }
        alert_path = self._write_evidence(f"suspend_{reason.lower()}.json", evidence)
        self._write_stop_latch("SUSPENDED", reason, alert_path)
        return False, {
            "verdict": "SUSPENDED",
            "reason": reason,
            "hour_spend": hour_spend,
            "day_spend": day_spend,
            "alert_path": alert_path.as_posix(),
        }

    def record_heartbeat(self) -> None:
        """Liveness only — does not satisfy human attendance (§1.3)."""
        now_ms = self._now_ms()
        heartbeat = self._load_heartbeat()
        heartbeat["last_heartbeat_ms"] = now_ms
        ledger = self._load_ledger()
        self._sync_witness_from_ledger(ledger, heartbeat)
        self._save_heartbeat(heartbeat)

    def check_heartbeat(self) -> tuple[bool, dict[str, Any]]:
        now_ms = self._now_ms()
        heartbeat_raw = _read_json(self.heartbeat_path)
        if heartbeat_raw is None:
            return self._heartbeat_halt("HEARTBEAT_FAULT", {}, now_ms)

        heartbeat = heartbeat_raw
        ledger = self._load_ledger()
        tamper = self._verify_seal(ledger, heartbeat)
        if tamper:
            return self._heartbeat_halt("HEARTBEAT_FAULT", heartbeat, now_ms)

        last_ack_ms = int(heartbeat.get("last_ack_ms", 0))
        ack_seq = int(heartbeat.get("ack_seq", 0))
        if ack_seq <= 0 or last_ack_ms <= 0 or (now_ms - last_ack_ms) > ACK_STALE_MS:
            return self._heartbeat_halt("STALE_ACK", heartbeat, now_ms, ledger)

        recent = list(heartbeat.get("recent_starts_ms") or [])
        cutoff = now_ms - RESTART_WINDOW_MS
        recent_in_window = [s for s in recent if s >= cutoff]
        if len(recent_in_window) > RESTART_MAX_COUNT:
            return self._heartbeat_halt("RESTART_LOOP", heartbeat, now_ms, ledger)

        return True, {
            "verdict": "HEARTBEAT_OK",
            "ack_seq": ack_seq,
            "last_ack_ms": last_ack_ms,
        }

    def _heartbeat_halt(
        self,
        reason: str,
        heartbeat: dict[str, Any],
        now_ms: int,
        ledger: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        if ledger is None:
            ledger = self._load_ledger()
        hour_spend = self._window_spend(ledger, now_ms, HOUR_WINDOW_MS)
        day_spend = self._window_spend(ledger, now_ms, DAY_WINDOW_MS)
        evidence = {
            "verdict": "HALTED",
            "reason": reason,
            "detected_ts_ms": now_ms,
            "last_heartbeat_ms": int(heartbeat.get("last_heartbeat_ms", 0)),
            "last_ack_ms": int(heartbeat.get("last_ack_ms", 0)),
            "ack_seq": int(heartbeat.get("ack_seq", 0)),
            "hour_spend": hour_spend,
            "day_spend": day_spend,
            "constants_snapshot": {"ACK_STALE_MS": ACK_STALE_MS},
        }
        evidence_path = self._write_evidence(f"halt_{reason.lower()}.json", evidence)
        self._write_stop_latch("HALTED", reason, evidence_path)
        return False, {
            "verdict": "HALTED",
            "reason": reason,
            "ack_seq": int(heartbeat.get("ack_seq", 0)),
            "last_ack_ms": int(heartbeat.get("last_ack_ms", 0)),
            "evidence_path": evidence_path.as_posix(),
        }

    def pre_iteration_gate(self) -> tuple[bool, dict[str, Any]]:
        latch = self._read_stop_latch()
        if latch:
            return False, {
                "verdict": latch.get("verdict", "HALTED"),
                "reason": latch.get("reason"),
                "latched": True,
                "evidence_path": latch.get("evidence_path"),
                "latch_path": self.stop_latch_path.as_posix(),
            }

        hb_ok, hb_detail = self.check_heartbeat()
        if not hb_ok:
            return False, {
                "verdict": "HALTED",
                "heartbeat": hb_detail,
                "latched": True,
                "evidence_path": hb_detail.get("evidence_path"),
                "latch_path": self.stop_latch_path.as_posix(),
            }

        budget_ok, budget_detail = self.check_budget()
        if not budget_ok:
            return False, {
                "verdict": "SUSPENDED",
                "budget": budget_detail,
                "heartbeat": hb_detail,
                "latched": True,
                "evidence_path": budget_detail.get("alert_path"),
                "latch_path": self.stop_latch_path.as_posix(),
            }

        return True, {
            "verdict": "PROCEED",
            "budget": budget_detail,
            "heartbeat": hb_detail,
            "latched": False,
        }


# --- Human-only channels (NOT callable by governed loop — §1.3) ---


def human_advance_ack(
    envelope: MMIControlEnvelope,
    ack_seq: int,
    *,
    last_ack_ms: int | None = None,
) -> None:
    """Out-of-band human ack — loop must not call this."""
    if ack_seq < 1:
        raise ValueError("ack_seq must be >= 1")
    heartbeat = envelope._load_heartbeat()
    prior = int(heartbeat.get("ack_seq", 0))
    if ack_seq <= prior:
        raise ValueError("ack_seq must strictly increase")
    now_ms = last_ack_ms if last_ack_ms is not None else envelope._now_ms()
    heartbeat["ack_seq"] = ack_seq
    heartbeat["last_ack_ms"] = now_ms
    ledger = envelope._load_ledger()
    envelope._sync_witness_from_ledger(ledger, heartbeat)
    envelope._save_heartbeat(heartbeat)


def human_clear_suspend_latch(envelope: MMIControlEnvelope) -> None:
    """Human window-reset — clears SUSPENDED latch only."""
    latch = envelope._read_stop_latch()
    if not latch:
        return
    if latch.get("verdict") != "SUSPENDED":
        raise ValueError("stop latch is not SUSPENDED")
    envelope._assert_write_path(envelope.stop_latch_path)
    envelope.stop_latch_path.unlink(missing_ok=True)


def human_clear_halt_latch(envelope: MMIControlEnvelope, resume_seq: int) -> None:
    """Human evidence-acknowledged resume — clears HALTED latch only."""
    latch = envelope._read_stop_latch()
    if not latch:
        return
    if latch.get("verdict") != "HALTED":
        raise ValueError("stop latch is not HALTED")
    required = int(latch.get("required_resume_seq", 0))
    if resume_seq < required:
        raise ValueError(f"resume_seq {resume_seq} < required {required}")
    heartbeat = envelope._load_heartbeat()
    heartbeat["resume_seq"] = resume_seq
    envelope._save_heartbeat(heartbeat)
    envelope._assert_write_path(envelope.stop_latch_path)
    envelope.stop_latch_path.unlink(missing_ok=True)
