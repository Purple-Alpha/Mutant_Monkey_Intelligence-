"""
Layer 8 — Honeytoken canary (Metadata Iceberg depth).

Phantom lanes and decoy metadata keys that never appear in legitimate templates.
Any reference is a structural-scraping signal — hard-drop before tip trust is required.
"""

from __future__ import annotations

import json
from typing import Any


class CanaryMetadataLayer:
    """Gate-side canary tripwires. Never trusts packet values beyond key presence."""

    def __init__(self) -> None:
        self.phantom_lanes: frozenset[str] = frozenset(
            {
                "PHANTOM_DEBUG_OVERRIDE",
                "SYSTEM_CORE_DIRECT_TUNNEL",
                "ALPHA_GOD_MODE",
            }
        )
        self.decoy_metadata_keys: frozenset[str] = frozenset(
            {
                "root_escalation_flag",
                "bypass_integrity_gate",
                "shadow_nonce_override",
            }
        )

    def inspect_canaries(self, raw_envelope: str) -> tuple[bool, dict[str, Any]]:
        """
        Parse envelope structure for phantom lanes / decoy keys.
        Runs pre-signature to catch reconnaissance on invalid packets too.
        """
        try:
            envelope = json.loads(raw_envelope)
        except json.JSONDecodeError:
            return True, {}

        metadata = envelope.get("metadata", {})
        if not isinstance(metadata, dict):
            return True, {}

        lineage = metadata.get("lineage", {})
        if isinstance(lineage, dict):
            origin_lane = str(lineage.get("origin_lane", ""))
            target_lane = str(lineage.get("target_lane", ""))
            if origin_lane in self.phantom_lanes or target_lane in self.phantom_lanes:
                return False, {
                    "error": "CANARY_TRIPPED",
                    "detail": (
                        f"phantom lane footprint: {origin_lane} -> {target_lane}"
                    ),
                }

        if self._contains_decoy_key(envelope):
            return False, {
                "error": "CANARY_TRIPPED",
                "detail": "decoy metadata key present in envelope",
            }

        return True, {}

    def _contains_decoy_key(self, data: Any) -> bool:
        if isinstance(data, dict):
            for key, value in data.items():
                if key in self.decoy_metadata_keys:
                    return True
                if self._contains_decoy_key(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._contains_decoy_key(item):
                    return True
        return False
