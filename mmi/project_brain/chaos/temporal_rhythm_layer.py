"""
Layer 7 — Temporal rhythm (Metadata Iceberg depth).

Gate-side inter-arrival cadence baseline per sender. Cold-start record-only;
established anomalies route to Mirror Dimension — never hard-drop.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

K_STDEV = 4
CV_FLOOR = 0.01
WARMUP_INTERVALS = 20
SESSION_GAP_MS = 300_000
STDEV_CLAMP_MS = 5.0
EPOCH_LENGTH = 512
MAX_SENDER_ID_LENGTH = 256
MAX_TRACKED_SENDERS = 100_000
IDLE_EVICT_MS = 86_400_000

VERDICT_OK = "RHYTHM_OK"
VERDICT_ANOMALY = "RHYTHM_ANOMALY"
ROUTE_CONTINUE = "CONTINUE"
ROUTE_MIRROR = "MIRROR_DIMENSION"


def _normalize_identity(raw: str, max_len: int) -> str:
    norm = unicodedata.normalize("NFKC", raw).casefold().strip()
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Cf")
    return norm[:max_len]


def _empty_sender_row() -> dict[str, Any]:
    return {
        "epoch": 0,
        "interval_count": 0,
        "last_arrival_ts_ms": None,
        "mean_ms": 0.0,
        "m2": 0.0,
        "clock_discard_count": 0,
    }


def _stdev(m2: float, count: int) -> float:
    if count <= 1:
        return 0.0
    return math.sqrt(max(m2 / count, 0.0))


def _welford_update(mean: float, m2: float, count: int, value: float) -> tuple[float, float, int]:
    new_count = count + 1
    if count == 0:
        return value, 0.0, new_count
    delta = value - mean
    mean += delta / new_count
    m2 += delta * (value - mean)
    return mean, m2, new_count


class _RhythmStore:
    """Atomic JSON persistence for per-sender Welford rhythm state."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._doc: dict[str, Any] = {"schema_version": 2, "senders": {}}
        if self.path and self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and int(raw.get("schema_version", 0)) == 2:
                    senders = raw.get("senders")
                    if isinstance(senders, dict):
                        self._doc = {"schema_version": 2, "senders": senders}
            except (json.JSONDecodeError, ValueError, OSError, TypeError):
                self._doc = {"schema_version": 2, "senders": {}}

    @property
    def senders(self) -> dict[str, Any]:
        return self._doc.setdefault("senders", {})

    def commit(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._doc, fh, sort_keys=True)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


class TemporalRhythmLayer:
    """Derived-only inter-arrival rhythm — suspicion routes, never hard-drops."""

    def __init__(self, state_path: Path | None = None) -> None:
        self._store = _RhythmStore(state_path)
        self._memory: dict[str, dict[str, Any]] | None = None
        if state_path is None:
            self._memory = dict(self._store.senders)

    def _senders(self) -> dict[str, Any]:
        return self._memory if self._memory is not None else self._store.senders

    def _row(self, sender_id: str) -> dict[str, Any]:
        senders = self._senders()
        if sender_id not in senders:
            senders[sender_id] = _empty_sender_row()
        return senders[sender_id]

    def _persist(self) -> None:
        if self._memory is not None:
            self._store.senders.clear()
            self._store.senders.update(self._memory)
        self._store.commit()

    def _sweep_idle(self, now_ms: int) -> None:
        cutoff = now_ms - IDLE_EVICT_MS
        senders = self._senders()
        stale = [
            sid
            for sid, row in list(senders.items())
            if not isinstance(row, dict)
            or row.get("last_arrival_ts_ms") is None
            or int(row["last_arrival_ts_ms"]) <= cutoff
        ]
        for sid in stale:
            senders.pop(sid, None)

    @staticmethod
    def _roll_epoch(row: dict[str, Any]) -> None:
        row["epoch"] = int(row.get("epoch", 0)) + 1
        row["interval_count"] = 0
        row["mean_ms"] = 0.0
        row["m2"] = 0.0

    def _anomaly(
        self,
        reason: str,
        *,
        sender_id: str = "",
        row: dict[str, Any] | None = None,
        observed_delta_ms: int = 0,
    ) -> dict[str, Any]:
        detail: dict[str, Any] = {
            "reason": reason,
            "sender_id": sender_id,
            "observed_delta_ms": observed_delta_ms,
            "k": K_STDEV,
            "cv_floor": CV_FLOOR,
        }
        if row is not None:
            count = int(row.get("interval_count", 0))
            mean = float(row.get("mean_ms", 0.0))
            m2 = float(row.get("m2", 0.0))
            detail.update(
                {
                    "interval_count": count,
                    "epoch": int(row.get("epoch", 0)),
                    "baseline_mean_ms": round(mean, 4),
                    "baseline_stdev_ms": round(_stdev(m2, count), 4),
                }
            )
        return {
            "verdict": VERDICT_ANOMALY,
            "route": ROUTE_MIRROR,
            "detail": detail,
        }

    def _ok_detail(self, mode: str, row: dict[str, Any], sender_id: str) -> dict[str, Any]:
        return {
            "verdict": VERDICT_OK,
            "route": ROUTE_CONTINUE,
            "detail": {
                "mode": mode,
                "sender_id": sender_id,
                "interval_count": int(row.get("interval_count", 0)),
                "epoch": int(row.get("epoch", 0)),
                "warmup_threshold": WARMUP_INTERVALS,
            },
        }

    def analyze_rhythm(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: Any,
        arrival_ts_ms: int,
    ) -> tuple[bool, dict[str, Any]]:
        del payload  # L7 consumes arrival_ts_ms only — API uniformity with L4/L5/L6.

        if not isinstance(metadata, dict):
            return True, self._anomaly("MALFORMED_METADATA")
        if not isinstance(sender_id, str) or not sender_id:
            return True, self._anomaly("MALFORMED_SENDER_ID")

        sender_id = _normalize_identity(sender_id, MAX_SENDER_ID_LENGTH)
        if not sender_id:
            return True, self._anomaly("MALFORMED_SENDER_ID")

        try:
            now_ms = int(arrival_ts_ms)
        except (TypeError, ValueError):
            return True, self._anomaly("MALFORMED_TIMESTAMP")
        if now_ms < 0:
            return True, self._anomaly("MALFORMED_TIMESTAMP")

        senders = self._senders()
        if sender_id not in senders and len(senders) >= MAX_TRACKED_SENDERS:
            self._sweep_idle(now_ms)
        if sender_id not in senders and len(senders) >= MAX_TRACKED_SENDERS:
            return True, self._anomaly("SENDER_TABLE_SATURATED", sender_id=sender_id)

        row = self._row(sender_id)
        last = row.get("last_arrival_ts_ms")

        if last is None:
            row["last_arrival_ts_ms"] = now_ms
            self._persist()
            return True, self._ok_detail("FIRST_CONTACT", row, sender_id)

        delta_ms = now_ms - int(last)

        if delta_ms <= 0:
            row["clock_discard_count"] = int(row.get("clock_discard_count", 0)) + 1
            row["last_arrival_ts_ms"] = now_ms
            self._persist()
            return True, self._ok_detail("CLOCK_DISCARD", row, sender_id)

        if delta_ms > SESSION_GAP_MS:
            row["last_arrival_ts_ms"] = now_ms
            self._persist()
            return True, self._ok_detail("SESSION_RESET", row, sender_id)

        interval_count = int(row.get("interval_count", 0))
        mean = float(row.get("mean_ms", 0.0))
        m2 = float(row.get("m2", 0.0))

        if interval_count >= WARMUP_INTERVALS:
            stdev_dev = max(_stdev(m2, interval_count), STDEV_CLAMP_MS)
            lower = mean - K_STDEV * stdev_dev
            if delta_ms < lower:
                self._persist()
                return True, self._anomaly(
                    "RHYTHM_DEVIATION",
                    sender_id=sender_id,
                    row=row,
                    observed_delta_ms=delta_ms,
                )

        mean, m2, welford_count = _welford_update(mean, m2, interval_count, float(delta_ms))
        row["mean_ms"] = mean
        row["m2"] = m2
        row["interval_count"] = welford_count
        row["last_arrival_ts_ms"] = now_ms

        if welford_count > WARMUP_INTERVALS and mean > 0:
            stdev_raw = _stdev(m2, welford_count)
            if stdev_raw / mean < CV_FLOOR:
                self._persist()
                return True, self._anomaly(
                    "MACHINE_CADENCE",
                    sender_id=sender_id,
                    row=row,
                    observed_delta_ms=delta_ms,
                )

        if welford_count >= EPOCH_LENGTH:
            self._roll_epoch(row)
            row["last_arrival_ts_ms"] = now_ms

        self._persist()

        if welford_count <= WARMUP_INTERVALS:
            return True, self._ok_detail("WARMUP_RECORD_ONLY", row, sender_id)

        return True, {
            "verdict": VERDICT_OK,
            "route": ROUTE_CONTINUE,
            "detail": {
                "sender_id": sender_id,
                "interval_count": welford_count,
                "epoch": int(row.get("epoch", 0)),
                "baseline_mean_ms": round(mean, 4),
                "baseline_stdev_ms": round(_stdev(m2, welford_count), 4),
            },
        }
