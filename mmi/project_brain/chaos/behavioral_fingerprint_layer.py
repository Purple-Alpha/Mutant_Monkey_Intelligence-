"""
Layer 4 — Behavioral fingerprint (Metadata Iceberg depth).

Gate-side per-sender baseline from signed metadata. Cold-start record-only;
established anomalies route to Mirror Dimension — never hard-drop.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_COLD_START_N = 20
DEFAULT_K_STDEV = 4.0
DEFAULT_MIN_CAPABILITY_FREQ = 0.02


class _FingerprintStore:
    """Atomic JSON persistence for per-sender Welch moments + capability mix."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._state: dict[str, dict[str, Any]] = {}
        if self.path and self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._state = raw
            except (json.JSONDecodeError, ValueError, OSError):
                self._state = {}

    def get(self, sender_id: str) -> dict[str, Any] | None:
        row = self._state.get(sender_id)
        return dict(row) if isinstance(row, dict) else None

    def commit_all(self, state: dict[str, dict[str, Any]]) -> None:
        self._state = state
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._state, fh, sort_keys=True)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


def _empty_sender_row() -> dict[str, Any]:
    return {
        "count": 0,
        "byte_size": {"mean": 0.0, "m2": 0.0},
        "key_count": {"mean": 0.0, "m2": 0.0},
        "capability_mix": {},
    }


def _welford_update(stats: dict[str, float], value: float, prior_count: int) -> None:
    mean = float(stats.get("mean", 0.0))
    m2 = float(stats.get("m2", 0.0))
    new_count = prior_count + 1
    if prior_count == 0:
        stats["mean"] = value
        stats["m2"] = 0.0
        return
    delta = value - mean
    mean += delta / new_count
    m2 += delta * (value - mean)
    stats["mean"] = mean
    stats["m2"] = m2


def _stdev(stats: dict[str, float], count: int) -> float:
    if count <= 1:
        return 0.0
    m2 = float(stats.get("m2", 0.0))
    return math.sqrt(max(m2 / count, 0.0))


def _extract_signals(metadata: dict[str, Any]) -> tuple[int, int, str]:
    volumetric = metadata.get("volumetric", {})
    lineage = metadata.get("lineage", {})
    if not isinstance(volumetric, dict) or not isinstance(lineage, dict):
        raise TypeError("metadata volumetric/lineage must be dicts")
    byte_size = int(volumetric["payload_byte_size"])
    key_count = int(volumetric["payload_key_count"])
    capability = str(lineage["target_capability"])
    return byte_size, key_count, capability


class BehavioralFingerprintLayer:
    """Derived-only sender fingerprint — suspicion routes, never hard-drops."""

    def __init__(
        self,
        state_path: Path | None = None,
        cold_start_n: int = DEFAULT_COLD_START_N,
        k_stdev: float = DEFAULT_K_STDEV,
        min_capability_freq: float = DEFAULT_MIN_CAPABILITY_FREQ,
    ) -> None:
        self.cold_start_n = cold_start_n
        self.k_stdev = k_stdev
        self.min_capability_freq = min_capability_freq
        self._store = _FingerprintStore(state_path)
        self._memory: dict[str, dict[str, Any]] = {}
        if state_path is None:
            self._memory = dict(self._store._state)

    def _row(self, sender_id: str) -> dict[str, Any]:
        if sender_id in self._memory:
            return self._memory[sender_id]
        loaded = self._store.get(sender_id)
        if loaded is not None:
            self._memory[sender_id] = loaded
            return loaded
        row = _empty_sender_row()
        self._memory[sender_id] = row
        return row

    def _persist(self) -> None:
        if self._store.path is None:
            return
        self._store.commit_all(self._memory)

    def _capability_anomaly(self, row: dict[str, Any], capability: str) -> bool:
        mix: dict[str, Any] = row.get("capability_mix", {})
        total = int(row.get("count", 0))
        if total <= 0:
            return False
        freq = float(mix.get(capability, 0)) / total
        return freq < self.min_capability_freq

    def _numeric_anomaly(
        self,
        stats: dict[str, float],
        count: int,
        value: float,
        label: str,
    ) -> str | None:
        if count < self.cold_start_n:
            return None
        mean = float(stats.get("mean", 0.0))
        stdev = _stdev(stats, count)
        band = self.k_stdev * stdev
        if value > mean + band or value < mean - band:
            return (
                f"{label} out-of-band: value={value} mean={mean:.2f} "
                f"stdev={stdev:.2f} band={band:.2f}"
            )
        return None

    def _apply_observation(
        self,
        row: dict[str, Any],
        byte_size: int,
        key_count: int,
        capability: str,
    ) -> None:
        prior = int(row.get("count", 0))
        byte_stats: dict[str, float] = row["byte_size"]
        key_stats: dict[str, float] = row["key_count"]
        _welford_update(byte_stats, float(byte_size), prior)
        _welford_update(key_stats, float(key_count), prior)
        mix: dict[str, int] = row.setdefault("capability_mix", {})
        mix[capability] = int(mix.get(capability, 0)) + 1
        row["count"] = prior + 1

    def analyze_fingerprint(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
        del payload  # bound via metadata hash at gate; not read directly
        if not sender_id:
            return False, {
                "verdict": "REJECTED",
                "error": "FINGERPRINT_REJECTED",
                "detail": "missing sender_id",
            }

        try:
            byte_size, key_count, capability = _extract_signals(metadata)
        except (KeyError, TypeError, ValueError) as exc:
            return False, {
                "verdict": "REJECTED",
                "error": "FINGERPRINT_FIELD_MISSING",
                "detail": str(exc),
            }

        row = self._row(sender_id)
        count = int(row.get("count", 0))

        if count < self.cold_start_n:
            self._apply_observation(row, byte_size, key_count, capability)
            self._persist()
            return True, {
                "verdict": "COLD_START",
                "detail": f"record-only warm-up {row['count']}/{self.cold_start_n}",
            }

        anomalies: list[str] = []
        byte_issue = self._numeric_anomaly(row["byte_size"], count, float(byte_size), "payload_byte_size")
        if byte_issue:
            anomalies.append(byte_issue)
        key_issue = self._numeric_anomaly(row["key_count"], count, float(key_count), "payload_key_count")
        if key_issue:
            anomalies.append(key_issue)
        if self._capability_anomaly(row, capability):
            anomalies.append(f"target_capability out-of-band: {capability}")

        self._apply_observation(row, byte_size, key_count, capability)
        self._persist()

        if anomalies:
            return True, {
                "verdict": "ANOMALY",
                "route": "MIRROR_DIMENSION",
                "error": "FINGERPRINT_ANOMALY",
                "detail": "; ".join(anomalies),
            }

        return True, {
            "verdict": "MATCH",
            "detail": "within sender baseline",
        }
