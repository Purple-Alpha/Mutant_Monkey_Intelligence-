"""Tamper-evident append-only evidence chain (§11 / §6 evidence rollup target)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


class ChainError(ValueError):
    """Chain integrity violation — fail-closed."""


def _hash_link(payload: dict, prev_hash: str) -> str:
    body = json.dumps({"prev_hash": prev_hash, "payload": payload}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


@dataclass
class EvidenceChain:
    stage_id: str
    run_nonce: str
    links: list[dict] = field(default_factory=list)
    sealed: bool = False

    def __post_init__(self) -> None:
        genesis = {
            "type": "genesis",
            "stage_id": self.stage_id,
            "run_nonce": self.run_nonce,
        }
        tip = _hash_link(genesis, "GENESIS")
        self.links.append({"index": 0, "interval_id": None, "payload": genesis, "hash": tip, "prev_hash": "GENESIS"})

    @property
    def tip(self) -> str:
        return self.links[-1]["hash"]

    def append(self, interval_id: int, payload: dict) -> None:
        if self.sealed:
            raise ChainError("chain sealed")
        if not isinstance(interval_id, int) or interval_id < 0:
            raise ChainError("interval_id must be non-negative int")
        expected = len(self.links) - 1
        if interval_id != expected:
            raise ChainError(f"interval_id gap or reorder: expected {expected}, got {interval_id}")
        prev = self.tip
        record = {"type": "interval", **payload}
        link_hash = _hash_link(record, prev)
        self.links.append(
            {
                "index": len(self.links),
                "interval_id": interval_id,
                "payload": record,
                "hash": link_hash,
                "prev_hash": prev,
            }
        )

    def verify(self) -> bool:
        if not self.links:
            return False
        prev = "GENESIS"
        for idx, link in enumerate(self.links):
            if link["prev_hash"] != prev:
                return False
            expected = _hash_link(link["payload"], prev)
            if link["hash"] != expected:
                return False
            if idx > 0:
                if link["interval_id"] != idx - 1:
                    return False
            prev = link["hash"]
        return True

    def seal(self) -> None:
        self.sealed = True
