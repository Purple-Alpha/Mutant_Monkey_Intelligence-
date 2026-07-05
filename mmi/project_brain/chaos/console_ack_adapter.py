"""ConsoleAckAdapter — signed human ack/resume for control envelope (§5.2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from console_evidence_gate import GateConfig, load_operator_pubkey, verify_signature


class ConsoleAckAdapter:
    def __init__(self, config: GateConfig | None = None):
        self.config = config or GateConfig()

    def poll_signoff(self, action: str) -> dict[str, Any] | None:
        signoff_dir = self.config.signoff_dir
        if not signoff_dir.exists():
            return None
        for path in sorted(signoff_dir.glob("console_signoff_record_*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            manifest = record.get("manifest") or {}
            if record.get("verdict") != "ACCEPTED":
                continue
            if manifest.get("operator_action") != action:
                continue
            if self.verify(record):
                return record
        return None

    def verify(self, record: dict[str, Any]) -> bool:
        manifest = record.get("manifest")
        if not isinstance(manifest, dict):
            return False
        if not self.config.operator_pubkey_path.exists():
            return False
        pubkey = load_operator_pubkey(self.config.operator_pubkey_path)
        sig = record.get("signature_b64", "")
        return verify_signature(manifest, sig, pubkey)

    def _consumed(self, bundle_id: str, sign_seq: int) -> bool:
        path = self.config.consumed_set_path
        if not path.exists():
            return False
        key = f"{bundle_id}:{sign_seq}"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() == key:
                return True
        return False

    def consume(self, record: dict[str, Any]) -> bool:
        if not self.verify(record):
            return False
        bundle_id = record.get("bundle_id")
        sign_seq = record.get("sign_seq")
        if not bundle_id or sign_seq is None:
            return False
        if self._consumed(bundle_id, sign_seq):
            return False

        path = self.config.consumed_set_path
        path.parent.mkdir(parents=True, exist_ok=True)
        key = f"{bundle_id}:{sign_seq}"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(key + "\n")
        return True
