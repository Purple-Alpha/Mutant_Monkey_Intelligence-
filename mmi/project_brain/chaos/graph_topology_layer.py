"""
Layer 6 — Lane-transition graph (Metadata Iceberg depth).

Enforces directed swarm topology after the tip signature passes. Capability
policy alone cannot authorize a hop that is not an edge in the graph.
"""

from __future__ import annotations

from typing import Any

# Aligns with DEFAULT_LANE_POLICY lanes in metadata_ingress_gate.py plus lab routers.
DEFAULT_LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "USER_INPUT": frozenset({"AGENT_TRUSTED"}),
    "AGENT_TRUSTED": frozenset({"SYSTEM_CORE", "MIRROR_DIMENSION", "USER_INPUT"}),
    "SYSTEM_CORE": frozenset({"AGENT_TRUSTED"}),
    "MIRROR_DIMENSION": frozenset({"AGENT_TRUSTED", "CRITIC_RING_EVALUATOR"}),
    "CRITIC_RING_EVALUATOR": frozenset(
        {"MIRROR_DIMENSION", "BUSINESS_ACTION_GATE"}
    ),
    "BUSINESS_ACTION_GATE": frozenset({"SYSTEM_CORE"}),
}


class LaneTransitionGraphLayer:
    """Gate-side topology enforcement — never trusts hop claims without graph match."""

    def __init__(
        self,
        legal_transitions: dict[str, frozenset[str]] | None = None,
    ) -> None:
        self.legal_topology = legal_transitions or DEFAULT_LEGAL_TRANSITIONS

    def verify_transition_edge(self, metadata: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        lineage = metadata.get("lineage", {})
        if not isinstance(lineage, dict):
            return True, {}

        origin_lane = str(lineage.get("origin_lane", ""))
        target_lane = str(lineage.get("target_lane", ""))

        # No hop claimed — tip-only traffic (legacy seal() default).
        if not target_lane:
            return True, {}

        if origin_lane not in self.legal_topology:
            return False, {
                "error": "TOPOLOGY_VIOLATION",
                "detail": f"source lane '{origin_lane}' is not in authoritative graph",
            }

        allowed_hops = self.legal_topology[origin_lane]
        if target_lane not in allowed_hops:
            return False, {
                "error": "ILLEGAL_LANE_TRANSITION",
                "detail": (
                    f"forbidden hop from '{origin_lane}' to '{target_lane}'"
                ),
            }

        return True, {}
