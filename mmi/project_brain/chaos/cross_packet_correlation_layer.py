"""
Layer 5 — Cross-packet correlation (Metadata Iceberg depth).

Gate-side rolling-window stream analysis per sender. Cold-start record-only;
established anomalies route to Mirror Dimension — never hard-drop.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

WINDOW_MS = 60_000
WARMUP_PACKET_THRESHOLD = 10
MAX_VELOCITY_RPM = 120
MAX_NONCE_VELOCITY = 120
MAX_LANE_DIVERSITY = 3
MAX_TRACKED_SENDERS = 100_000
MAX_SENDER_ID_LENGTH = 256
MAX_LANE_LENGTH = 128
_WINDOW_MAXLEN = MAX_VELOCITY_RPM + 1

VERDICT_OK = "STREAM_OK"
VERDICT_ANOMALY = "STREAM_ANOMALY"
ROUTE_CONTINUE = "CONTINUE"
ROUTE_MIRROR = "MIRROR_DIMENSION"


def _nonce_hash(nonce: int) -> str:
    digest = hashlib.sha256(str(nonce).encode("utf-8")).hexdigest()
    return f"sha256:{digest[:16]}"


def _normalize_identity(raw: str, max_len: int) -> str:
    norm = unicodedata.normalize("NFKC", raw).casefold().strip()
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Cf")
    return norm[:max_len]


def _empty_sender_row() -> dict[str, Any]:
    return {"lifetime_packets": 0, "window": []}


class _StreamStore:
    """Atomic JSON persistence for per-sender stream windows."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._doc: dict[str, Any] = {"schema_version": 1, "senders": {}}
        if self.path and self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and int(raw.get("schema_version", 0)) == 1:
                    senders = raw.get("senders")
                    if isinstance(senders, dict):
                        self._doc = {"schema_version": 1, "senders": senders}
            except (json.JSONDecodeError, ValueError, OSError, TypeError):
                self._doc = {"schema_version": 1, "senders": {}}

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


class CrossPacketCorrelationLayer:
    """Derived-only stream correlator — suspicion routes, never hard-drops."""

    def __init__(
        self,
        state_path: Path | None = None,
        warmup_threshold: int = WARMUP_PACKET_THRESHOLD,
    ) -> None:
        self.warmup_threshold = warmup_threshold
        self._store = _StreamStore(state_path)
        self._memory: dict[str, dict[str, Any]] | None = None
        if state_path is None:
            self._memory = dict(self._store.senders)

    def _sender_row(self, sender_id: str) -> dict[str, Any]:
        if self._memory is not None:
            if sender_id not in self._memory:
                self._memory[sender_id] = _empty_sender_row()
            return self._memory[sender_id]
        senders = self._store.senders
        if sender_id not in senders:
            senders[sender_id] = _empty_sender_row()
        return senders[sender_id]

    def _persist(self) -> None:
        if self._memory is not None:
            self._store.senders.clear()
            self._store.senders.update(self._memory)
        self._store.commit()

    def _sweep_idle(self, now_ms: int) -> None:
        stale_cutoff = now_ms - WINDOW_MS
        senders = self._memory if self._memory is not None else self._store.senders
        stale = [
            sid
            for sid, row in list(senders.items())
            if not isinstance(row, dict)
            or not row.get("window")
            or int(row["window"][-1]["ts_ms"]) <= stale_cutoff
        ]
        for sid in stale:
            senders.pop(sid, None)

    @staticmethod
    def _extract_lane(metadata: dict[str, Any]) -> str:
        lineage = metadata.get("lineage", {})
        if not isinstance(lineage, dict):
            return "LANE_UNKNOWN"
        raw = lineage.get("origin_lane")
        if isinstance(raw, str) and raw:
            lane = _normalize_identity(raw, MAX_LANE_LENGTH)
            if lane:
                return lane
        return "LANE_UNKNOWN"

    @staticmethod
    def _extract_nonce(metadata: dict[str, Any]) -> int | None:
        provenance = metadata.get("provenance", {})
        if not isinstance(provenance, dict):
            return None
        raw = provenance.get("nonce")
        if isinstance(raw, bool):
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def _anomaly(
        self,
        reason: str,
        *,
        sender_id: str = "",
        window_count: int = 0,
        lanes: tuple[str, ...] = (),
        distinct_nonces: int = 0,
        observed_ts_ms: int = 0,
    ) -> dict[str, Any]:
        return {
            "verdict": VERDICT_ANOMALY,
            "route": ROUTE_MIRROR,
            "detail": {
                "reason": reason,
                "sender_id": sender_id,
                "window_packet_count": window_count,
                "window_distinct_nonces": distinct_nonces,
                "window_lanes": list(lanes),
                "velocity_ceiling_rpm": MAX_VELOCITY_RPM,
                "nonce_velocity_ceiling": MAX_NONCE_VELOCITY,
                "lane_diversity_ceiling": MAX_LANE_DIVERSITY,
                "window_ms": WINDOW_MS,
                "observed_ts_ms": observed_ts_ms,
            },
        }

    def analyze_stream(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: Any,
        arrival_ts_ms: int,
    ) -> tuple[bool, dict[str, Any]]:
        del payload

        if not isinstance(sender_id, str) or not sender_id:
            return True, self._anomaly("MALFORMED_SENDER_ID")
        if not isinstance(metadata, dict):
            return True, self._anomaly("MALFORMED_METADATA")

        sender_id = _normalize_identity(sender_id, MAX_SENDER_ID_LENGTH)
        if not sender_id:
            return True, self._anomaly("MALFORMED_SENDER_ID")

        try:
            now_ms = int(arrival_ts_ms)
        except (TypeError, ValueError):
            return True, self._anomaly("MALFORMED_TIMESTAMP")

        if now_ms < 0:
            return True, self._anomaly("MALFORMED_TIMESTAMP")

        lane = self._extract_lane(metadata)
        nonce = self._extract_nonce(metadata)
        nonce_h = _nonce_hash(nonce) if nonce is not None else "sha256:missing"

        senders = self._memory if self._memory is not None else self._store.senders
        if sender_id not in senders and len(senders) >= MAX_TRACKED_SENDERS:
            self._sweep_idle(now_ms)
        if sender_id not in senders and len(senders) >= MAX_TRACKED_SENDERS:
            return True, self._anomaly(
                "SENDER_TABLE_SATURATED",
                sender_id=sender_id,
                observed_ts_ms=now_ms,
            )

        row = self._sender_row(sender_id)
        window: list[dict[str, Any]] = row.setdefault("window", [])

        if window and now_ms < int(window[-1]["ts_ms"]):
            now_ms = int(window[-1]["ts_ms"])

        cutoff = now_ms - WINDOW_MS
        row["window"] = [
            entry
            for entry in window
            if isinstance(entry, dict) and int(entry.get("ts_ms", 0)) > cutoff
        ][-_WINDOW_MAXLEN:]

        row["window"].append({"ts_ms": now_ms, "lane": lane, "nonce_h": nonce_h})
        row["lifetime_packets"] = int(row.get("lifetime_packets", 0)) + 1
        lifetime = int(row["lifetime_packets"])

        window_count = len(row["window"])
        unique_lanes = tuple(sorted({str(e.get("lane", "LANE_UNKNOWN")) for e in row["window"]}))
        distinct_nonces = len({str(e.get("nonce_h", "")) for e in row["window"]})

        if lifetime < self.warmup_threshold:
            self._persist()
            return True, {
                "verdict": VERDICT_OK,
                "route": ROUTE_CONTINUE,
                "detail": {
                    "mode": "WARMUP_RECORD_ONLY",
                    "sender_id": sender_id,
                    "lifetime_packets": lifetime,
                    "warmup_threshold": self.warmup_threshold,
                },
            }

        breaches: list[str] = []
        if window_count > MAX_VELOCITY_RPM:
            breaches.append("VELOCITY_CEILING_EXCEEDED")
        if distinct_nonces > MAX_NONCE_VELOCITY:
            breaches.append("NONCE_VELOCITY_CEILING_EXCEEDED")
        if len(unique_lanes) > MAX_LANE_DIVERSITY:
            breaches.append("LANE_DIVERSITY_EXCEEDED")

        self._persist()

        if breaches:
            return True, self._anomaly(
                ",".join(breaches),
                sender_id=sender_id,
                window_count=window_count,
                lanes=unique_lanes,
                distinct_nonces=distinct_nonces,
                observed_ts_ms=now_ms,
            )

        return True, {
            "verdict": VERDICT_OK,
            "route": ROUTE_CONTINUE,
            "detail": {
                "sender_id": sender_id,
                "window_packet_count": window_count,
                "window_distinct_nonces": distinct_nonces,
                "window_lane_count": len(unique_lanes),
            },
        }
