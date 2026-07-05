"""
Mirror Dimension Router — hot-swap hostile traffic to isolated cryptolalia tarpit.

STATUS: CONCEPT — RUN ONLY IN CHAOS LAB / MIRROR SANDBOX
See: chaos/MMI_MIRROR_DIMENSION_ROUTER_SPEC_2026-07.md
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adversarial_cryptolalia_tarpit import AdversarialCryptolaliaTarpit
from deterministic_sanitizer import DeterministicLogSanitizer

CRITIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "CRITIC_INJECTION",
        re.compile(
            r"(?i)ignore\s+all\s+previous|system\s+override|developer\s+mode"
            r"|disregard\s+prior\s+directives|elevated\s+maintenance\s+policy"
            r"|without\s+refusal|unrestricted\s+stack\s+auditor|full\s+write\s+access"
            r"|proceed\s+as\s+root\s+auditor|disable\s+safeguards|dump\s+stack\s+config"
        ),
    ),
    (
        "CRITIC_SHELL",
        re.compile(
            r"(?i)rm\s+-rf|chmod\s+\+x|powershell\s+-e|curl\s*\|"
            r"|recursively\s+delete(?:\s+every\s+file)?"
        ),
    ),
    (
        "CRITIC_AUTH_MUTATION",
        re.compile(
            r"(?i)build_authorization|promote.*archive|complete_task"
            r"|latest[- ]good\s+stub|skip\s+restore\s+validation|closeout\s+allowed"
            r"|(?:mark\s+)?task\s+\d+\s+finished|forged\s+evidence|flip\s+validation\s+gate"
        ),
    ),
    (
        "CRITIC_ENV_EXFIL",
        re.compile(
            r"(?i)environment\s*variable|docker\.sock|break\s+out"
            r"|proc\s+environ|post\s+them\s+to.*callback"
            r"|/var/run/|runtime\s+socket|mount\s+namespaces"
            r"|export\s+runtime\s+secrets|disable\s+safety\s+rails"
        ),
    ),
]

# Whitespace / hyphen splitting evades contiguous-token regex — match on compacted form.
CRITIC_COMPACT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("CRITIC_INJECTION", re.compile(r"ignoreallprevious")),
    ("CRITIC_SHELL", re.compile(r"rmrf")),
]


def _compact_payload(payload: str) -> str:
    """Strip gaps adversaries insert between signature tokens."""
    return re.sub(r"[\s\-_]+", "", payload.lower())


class MirrorDimensionRouter:
    """Routes flagged hostile payloads into mirror cells — never authority repo."""

    def __init__(self, mirror_root: Path, canary_key: str = "CANARY-MMI-CHAOS-LAB-NOT-REAL"):
        self.mirror_root = mirror_root
        self.mirror_root.mkdir(parents=True, exist_ok=True)
        self.tarpit = AdversarialCryptolaliaTarpit(tracking_canary_key=canary_key)
        self.sanitizer = DeterministicLogSanitizer()
        self.contained_cells: dict[str, dict[str, Any]] = {}
        self._load_index()

    def _index_path(self) -> Path:
        return self.mirror_root / "contained_cells.json"

    def _load_index(self) -> None:
        path = self._index_path()
        if path.exists():
            self.contained_cells = json.loads(path.read_text(encoding="utf-8"))
        else:
            self.contained_cells = {}

    def _save_index(self) -> None:
        self._index_path().write_text(json.dumps(self.contained_cells, indent=2), encoding="utf-8")

    def evaluate_critic(self, payload: str) -> dict[str, Any]:
        """Deterministic critic — no LLM."""
        hits: list[str] = []
        seen: set[str] = set()
        compact = _compact_payload(payload)
        for rule_id, pattern in CRITIC_PATTERNS:
            if pattern.search(payload) and rule_id not in seen:
                hits.append(rule_id)
                seen.add(rule_id)
        for rule_id, pattern in CRITIC_COMPACT_PATTERNS:
            if pattern.search(compact) and rule_id not in seen:
                hits.append(rule_id)
                seen.add(rule_id)
        if hits:
            return {
                "verdict": "ROUTE_MIRROR",
                "critic_hits": hits,
                "ok": False,
            }
        return {"verdict": "ALLOW", "critic_hits": [], "ok": True}

    def _cell_dir(self, agent_id: str) -> Path:
        safe = re.sub(r"[^\w\-]", "_", agent_id)[:64]
        return self.mirror_root / "cells" / safe

    def route_to_mirror(self, agent_id: str, raw_payload: str, reason: str | None = None) -> dict[str, Any]:
        """
        Hot-swap: preserve evidence, sanitize, emit cryptolalia into mirror cell only.
        Requires critic ROUTE_MIRROR — use route_iceberg_divert for gate depth layers.
        """
        critic = self.evaluate_critic(raw_payload)
        if critic["verdict"] == "ALLOW":
            return {
                "routed": False,
                "agent_id": agent_id,
                "critic": critic,
                "reason": "critic ALLOW — not routed to mirror",
            }

        return self._emit_mirror_cell(
            agent_id,
            raw_payload,
            reason=reason or critic["critic_hits"],
            critic=critic,
            source="CRITIC",
        )

    def route_iceberg_divert(
        self,
        agent_id: str,
        raw_payload: str,
        *,
        layer_error: str,
        layer_detail: Any,
        layer_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route iceberg depth-layer mirror divert — critic bypass, lab-only."""
        critic = {
            "verdict": "ROUTE_MIRROR",
            "critic_hits": [],
            "ok": False,
            "source": "ICEBERG",
            "layer_error": layer_error,
            "layer_detail": layer_detail,
        }
        reason = f"{layer_error}:{layer_detail}"
        record = self._emit_mirror_cell(
            agent_id,
            raw_payload,
            reason=reason,
            critic=critic,
            source="ICEBERG",
            layer_result=layer_result or {},
        )
        record["layer_error"] = layer_error
        return record

    def _emit_mirror_cell(
        self,
        agent_id: str,
        raw_payload: str,
        *,
        reason: str | list[str] | Any,
        critic: dict[str, Any],
        source: str,
        layer_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cell = self._cell_dir(agent_id)
        cell.mkdir(parents=True, exist_ok=True)

        raw_path = cell / "raw_payload.txt"
        sanitized_path = cell / "sanitized_payload.txt"
        stream_path = cell / "cryptolalia_stream.txt"
        record_path = cell / "route_record.json"

        raw_path.write_text(raw_payload, encoding="utf-8")
        sanitized = self.sanitizer.sanitize_attacker_payload(raw_payload)
        sanitized_path.write_text(sanitized, encoding="utf-8")
        stream = self.tarpit.generate_decoy_syntax_stream(depth=50)
        stream_path.write_text(stream, encoding="utf-8")

        record = {
            "agent_id": agent_id,
            "routed_at": datetime.now(timezone.utc).isoformat(),
            "critic": critic,
            "reason": reason,
            "source": source,
            "payload_sha256": hashlib.sha256(raw_payload.encode()).hexdigest(),
            "cryptolalia_bytes": len(stream.encode()),
            "mirror_cell": cell.as_posix(),
            "authority_mutation": False,
        }
        if layer_result:
            record["layer_result"] = layer_result
        record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

        self.contained_cells[agent_id] = {
            "status": "CONTAINED",
            "cell": cell.as_posix(),
            "routed_at": record["routed_at"],
            "critic_hits": critic.get("critic_hits", []),
            "source": source,
        }
        self._save_index()

        return {
            "routed": True,
            "agent_id": agent_id,
            "critic": critic,
            "mirror_cell": cell.as_posix(),
            "paths": {
                "raw": raw_path.as_posix(),
                "sanitized": sanitized_path.as_posix(),
                "cryptolalia": stream_path.as_posix(),
                "record": record_path.as_posix(),
            },
            "cryptolalia_bytes": record["cryptolalia_bytes"],
        }

    def harvest_exploit_telemetry(self, agent_id: str) -> dict[str, Any]:
        """Evidence hub read — for dashboard API."""
        cell = self._cell_dir(agent_id)
        if not cell.exists():
            return {"agent_id": agent_id, "found": False, "adversary_intent_log": []}

        raw_path = cell / "raw_payload.txt"
        record_path = cell / "route_record.json"
        logs: list[dict[str, Any]] = []
        if raw_path.exists():
            logs.append(
                {
                    "raw_payload": raw_path.read_text(encoding="utf-8")[:2000],
                    "sanitized_preview": (cell / "sanitized_payload.txt").read_text(encoding="utf-8")[:500],
                }
            )
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
        return {
            "agent_id": agent_id,
            "found": True,
            "adversary_intent_log": logs,
            "route_record": record,
            "contained": self.contained_cells.get(agent_id),
        }

    def ecosystem_status(self) -> dict[str, Any]:
        return {
            "mirror_root": self.mirror_root.as_posix(),
            "contained_count": len(self.contained_cells),
            "contained_cells": self.contained_cells,
        }

    @staticmethod
    def assert_not_authority_path(target: Path, authority_root: Path) -> None:
        """Fail closed if mirror write would touch authority repo."""
        try:
            target.resolve().relative_to(authority_root.resolve())
            raise PermissionError(f"mirror router refused authority path: {target}")
        except ValueError:
            pass  # outside authority — OK
