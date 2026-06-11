"""GeoIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 GeoIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Static seed (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable so a Layer 1 caller cannot modify it (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class TimeAnomalyWindow(BaseModel):
    """One immutable time window where a geo/time anomaly is significant.

    Realizes the §3 ``time_anomaly_windows: list[dict]`` field as a closed,
    frozen structure (hours in UTC, 0-23) rather than a free-form dict, so the
    briefing stays schema-validated and immutable.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    start_hour_utc: int = Field(ge=0, le=23)
    end_hour_utc: int = Field(ge=0, le=23)
    note: str


class GeoBriefing(BaseModel):
    """Immutable geo-intel briefing (§3 schema). Tuple fields realize the
    contract's ``list`` types immutably."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    high_risk_ip_ranges: tuple[str, ...] = ()
    high_risk_countries: tuple[str, ...] = ()
    time_anomaly_windows: tuple[TimeAnomalyWindow, ...] = ()
    known_vpn_exit_nodes: tuple[str, ...] = ()
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. IP ranges use RFC-5737 documentation blocks (TEST-NET) so no
# real network is named. ``high_risk_countries`` is intentionally left empty at
# ES1: country-level risk is operator/threat-intel-populated on refresh (P2-D4),
# not hardcoded here, to avoid baking geopolitical bias into the product.
_HIGH_RISK_IP_RANGES: tuple[str, ...] = (
    "192.0.2.0/24",
    "198.51.100.0/24",
    "203.0.113.0/24",
)
_HIGH_RISK_COUNTRIES: tuple[str, ...] = ()
_TIME_ANOMALY_WINDOWS: tuple[TimeAnomalyWindow, ...] = (
    TimeAnomalyWindow(start_hour_utc=0, end_hour_utc=5, note="off-hours send burst"),
    TimeAnomalyWindow(
        start_hour_utc=22, end_hour_utc=23, note="late-night first-contact spike"
    ),
)
_KNOWN_VPN_EXIT_NODES: tuple[str, ...] = (
    "192.0.2.128/25",
    "198.51.100.128/25",
)


class GeoIntelAgent:
    """Brief-only Layer 0 geo-intelligence agent. Exposes only ``brief()``."""

    def brief(self) -> GeoBriefing:
        """Return the immutable geo-intel briefing for a Layer 1 agent."""

        return GeoBriefing(
            high_risk_ip_ranges=_HIGH_RISK_IP_RANGES,
            high_risk_countries=_HIGH_RISK_COUNTRIES,
            time_anomaly_windows=_TIME_ANOMALY_WINDOWS,
            known_vpn_exit_nodes=_KNOWN_VPN_EXIT_NODES,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.55,
        )
