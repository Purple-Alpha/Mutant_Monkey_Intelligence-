"""
Layer 9 - Provenance chain depth (Metadata Iceberg depth).

Tracks content hop depth and gate-derived origin trust. Senders may re-wrap
content, but they cannot reset lineage once the gate has observed it.
Cold-start applies to history-dependent signals only; untrusted→privileged
mirrors from observation 1. Anomalies route to Mirror Dimension — never hard-drop.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

UNTRUSTED_ORIGIN_LANES = frozenset({"USER_INPUT"})
PRIVILEGED_CAPABILITIES = frozenset({"WRITE", "EXECUTE", "ADMIN"})
PRIVILEGED_TARGET_LANES = frozenset({"SYSTEM_CORE", "BUSINESS_ACTION_GATE"})
DEFAULT_MIN_CHAIN_OBSERVATIONS = 2
MAX_TRACKED_CHAINS = 100_000
IDLE_EVICT_MS = 86_400_000
MAX_SENDER_ID_LENGTH = 256

VERDICT_OK = "CHAIN_OK"
VERDICT_ANOMALY = "CHAIN_DEPTH_ANOMALY"
ROUTE_CONTINUE = "CONTINUE"
ROUTE_MIRROR = "MIRROR_DIMENSION"
REASON_UNTRUSTED_PRIVILEGED = "UNTRUSTED_ORIGIN_PRIVILEGED_TARGET"


def _normalize_identity(raw: str, max_len: int = MAX_SENDER_ID_LENGTH) -> str:
    norm = unicodedata.normalize("NFKC", raw).casefold().strip()
    norm = "".join(ch for ch in norm if unicodedata.category(ch) != "Cf")
    return norm[:max_len]


def _canonical_payload(payload: Any) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _content_hash(payload: Any) -> str:
    return hashlib.sha256(_canonical_payload(payload)).hexdigest()


def _trust_for_lane(lane: str) -> str:
    return "UNTRUSTED" if lane in UNTRUSTED_ORIGIN_LANES else "TRUSTED"


def _min_trust(current: str, observed: str) -> str:
    if current == "UNTRUSTED" or observed == "UNTRUSTED":
        return "UNTRUSTED"
    return "TRUSTED"


def _empty_chain_row(content_hash: str, ingress_lane: str) -> dict[str, Any]:
    return {
        "content_hash": content_hash,
        "first_origin_lane": ingress_lane,
        "origin_trust": _trust_for_lane(ingress_lane),
        "observations": 0,
        "max_depth": 0,
        "last_sender_id": "",
        "last_seen_ts_ms": None,
    }


class _ChainDepthStore:
    """Atomic JSON persistence for per-content chain depth state."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._doc: dict[str, Any] = {"schema_version": 1, "chains": {}}
        if self.path and self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and int(raw.get("schema_version", 0)) == 1:
                    chains = raw.get("chains")
                    if isinstance(chains, dict):
                        self._doc = {"schema_version": 1, "chains": chains}
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                self._doc = {"schema_version": 1, "chains": {}}

    @property
    def chains(self) -> dict[str, Any]:
        return self._doc.setdefault("chains", {})

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


class ProvenanceChainDepthLayer:
    """Derived-only chain depth tracking - suspicion routes, never hard-drops."""

    def __init__(
        self,
        state_path: Path | None = None,
        min_chain_observations: int = DEFAULT_MIN_CHAIN_OBSERVATIONS,
        privileged_capabilities: frozenset[str] = PRIVILEGED_CAPABILITIES,
        privileged_target_lanes: frozenset[str] = PRIVILEGED_TARGET_LANES,
    ) -> None:
        self.min_chain_observations = min_chain_observations
        self.privileged_capabilities = privileged_capabilities
        self.privileged_target_lanes = privileged_target_lanes
        self._store = _ChainDepthStore(state_path)
        self._memory: dict[str, Any] | None = None
        if state_path is None:
            self._memory = dict(self._store.chains)

    def _chains(self) -> dict[str, Any]:
        return self._memory if self._memory is not None else self._store.chains

    def _persist(self) -> None:
        if self._memory is not None:
            self._store.chains.clear()
            self._store.chains.update(self._memory)
        self._store.commit()

    def _sweep_idle(self, now_ms: int) -> None:
        cutoff = now_ms - IDLE_EVICT_MS
        chains = self._chains()
        stale = [
            key
            for key, row in list(chains.items())
            if not isinstance(row, dict)
            or row.get("last_seen_ts_ms") is None
            or int(row["last_seen_ts_ms"]) <= cutoff
        ]
        for key in stale:
            chains.pop(key, None)

    def _ok(self, mode: str, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "verdict": VERDICT_OK,
            "route": ROUTE_CONTINUE,
            "detail": {
                "mode": mode,
                "content_hash": row["content_hash"],
                "origin_trust": row["origin_trust"],
                "first_origin_lane": row["first_origin_lane"],
                "observations": int(row["observations"]),
                "max_depth": int(row["max_depth"]),
                "warmup_threshold": self.min_chain_observations,
            },
        }

    def _anomaly(
        self,
        reason: str,
        row: dict[str, Any],
        routing_capability: str,
        routing_target_lane: str,
    ) -> dict[str, Any]:
        target = routing_target_lane or routing_capability
        return {
            "verdict": VERDICT_ANOMALY,
            "route": ROUTE_MIRROR,
            "detail": {
                "reason": reason,
                "content_hash": row["content_hash"],
                "origin_trust": row["origin_trust"],
                "first_origin_lane": row["first_origin_lane"],
                "observations": int(row["observations"]),
                "max_depth": int(row["max_depth"]),
                "target": target,
                "routing_capability": routing_capability,
                "routing_target_lane": routing_target_lane,
            },
        }

    def analyze_chain(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: Any,
        *,
        ingress_lane: str,
        routing_capability: str,
        routing_target_lane: str = "",
        arrival_ts_ms: int | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        del metadata  # REV A input-trust: L9 ignores packet metadata entirely.

        if not isinstance(sender_id, str) or not sender_id:
            return True, {
                "verdict": VERDICT_ANOMALY,
                "route": ROUTE_MIRROR,
                "detail": {"reason": "MALFORMED_SENDER_ID"},
            }

        sender_id = _normalize_identity(sender_id)
        if not sender_id:
            return True, {
                "verdict": VERDICT_ANOMALY,
                "route": ROUTE_MIRROR,
                "detail": {"reason": "MALFORMED_SENDER_ID"},
            }

        try:
            content_hash = _content_hash(payload)
        except (TypeError, ValueError):
            return True, {
                "verdict": VERDICT_ANOMALY,
                "route": ROUTE_MIRROR,
                "detail": {"reason": "MALFORMED_PAYLOAD"},
            }

        now_ms = int(arrival_ts_ms) if arrival_ts_ms is not None else None
        chains = self._chains()
        if content_hash not in chains and len(chains) >= MAX_TRACKED_CHAINS:
            if now_ms is not None:
                self._sweep_idle(now_ms)
        if content_hash not in chains and len(chains) >= MAX_TRACKED_CHAINS:
            return True, {
                "verdict": VERDICT_ANOMALY,
                "route": ROUTE_MIRROR,
                "detail": {"reason": "CHAIN_TABLE_SATURATED"},
            }

        row = chains.get(content_hash)
        if not isinstance(row, dict):
            row = _empty_chain_row(content_hash, ingress_lane)
            chains[content_hash] = row

        prior_observations = int(row.get("observations", 0))
        observed_trust = _trust_for_lane(ingress_lane)

        if prior_observations == 0:
            row["first_origin_lane"] = ingress_lane
            row["origin_trust"] = observed_trust
        else:
            row["origin_trust"] = _min_trust(str(row.get("origin_trust", "TRUSTED")), observed_trust)

        prior_sender = str(row.get("last_sender_id", ""))
        if prior_observations > 0 and sender_id != prior_sender:
            row["max_depth"] = int(row.get("max_depth", 0)) + 1

        row["observations"] = prior_observations + 1
        row["last_sender_id"] = sender_id
        if now_ms is not None:
            row["last_seen_ts_ms"] = now_ms

        privileged_target = (
            routing_capability in self.privileged_capabilities
            or routing_target_lane in self.privileged_target_lanes
        )
        untrusted_origin = row.get("origin_trust") == "UNTRUSTED"

        self._persist()

        if untrusted_origin and privileged_target:
            return True, self._anomaly(
                REASON_UNTRUSTED_PRIVILEGED,
                row,
                routing_capability,
                routing_target_lane,
            )

        if prior_observations < self.min_chain_observations:
            return True, self._ok("WARMUP_RECORD_ONLY", row)

        return True, self._ok("CHAIN_TRACKED", row)

    def analyze_chain_depth(
        self,
        sender_id: str,
        metadata: dict[str, Any],
        payload: Any,
        arrival_ts_ms: int | None = None,
        *,
        ingress_lane: str | None = None,
        routing_capability: str | None = None,
        routing_target_lane: str = "",
    ) -> tuple[bool, dict[str, Any]]:
        """Backward-compatible alias; gate must supply routing via explicit kwargs."""
        if ingress_lane is None or routing_capability is None:
            lineage = metadata.get("lineage", {}) if isinstance(metadata, dict) else {}
            ingress_lane = ingress_lane or str(lineage.get("origin_lane", ""))
            routing_capability = routing_capability or str(
                lineage.get("target_capability", "")
            )
            routing_target_lane = routing_target_lane or str(
                lineage.get("target_lane", "")
            )
        return self.analyze_chain(
            sender_id,
            metadata,
            payload,
            ingress_lane=ingress_lane,
            routing_capability=routing_capability,
            routing_target_lane=routing_target_lane,
            arrival_ts_ms=arrival_ts_ms,
        )


__all__ = [
    "ProvenanceChainDepthLayer",
    "DEFAULT_MIN_CHAIN_OBSERVATIONS",
    "PRIVILEGED_CAPABILITIES",
    "PRIVILEGED_TARGET_LANES",
    "UNTRUSTED_ORIGIN_LANES",
    "REASON_UNTRUSTED_PRIVILEGED",
]
