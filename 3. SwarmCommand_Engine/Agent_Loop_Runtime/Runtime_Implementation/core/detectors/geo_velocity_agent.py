"""GeoVelocityAgent — Phase 3 Detection Swarm (#79, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.2
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 §B (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``geo_signal`` (closed, P3-D2). Layer 0 dependency:
``GeoIntelAgent`` — **mandatory** briefing queried before any contribution
(P3-D3). Boundary: may only write ``geo_signal``; may not access body or
attachments. Lookup-only, so no ``TokenUsageTracker`` call (Amendment §C). The
``sender_domain`` is the same normalized value SenderHistoryAgent writes —
Amendment §B's join key for Phase 4 correlation. Attacker cost: strips anonymity
and burns money on clean IP infrastructure.
"""

from __future__ import annotations

import ipaddress

from core.blackboard import CanonicalEvidenceLedger, EvidenceLedgerEntry, EvidenceType
from core.knowledge import GeoIntelAgent

from ._common import DetectionError, EmailContext, require_email, write_contribution
from .sender_domain import normalize_sender_domain


def _ip_in_any_range(ip: str, ranges: tuple[str, ...]) -> bool:
    """True if ``ip`` falls inside any CIDR in ``ranges`` (safe on bad input)."""

    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for cidr in ranges:
        try:
            if addr in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue
    return False


class GeoVelocityAgent:
    """Layer 1 geographic-origin detector. Writes one ``geo_signal``."""

    AGENT_ID = "geo_velocity_agent"
    EVIDENCE_TYPE = EvidenceType.GEO_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        geo_intel: GeoIntelAgent,
    ) -> None:
        if geo_intel is None:
            raise DetectionError(
                "GeoVelocityAgent requires a GeoIntelAgent briefing source (P3-D3)"
            )
        self._ledger = ledger
        self._geo_intel = geo_intel

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Produce the geo/velocity evidence contribution for one email."""

        email = require_email(email)

        # P3-D3: query the mandatory Layer 0 briefing before producing anything.
        briefing = self._geo_intel.brief()

        sender_domain = normalize_sender_domain(email.from_domain)
        ip = email.sending_ip or ""
        ip_country = (email.ip_country or "").upper()
        home_country = (email.account_home_country or "").upper()

        high_risk_region = _ip_in_any_range(ip, briefing.high_risk_ip_ranges) or (
            bool(ip_country) and ip_country in briefing.high_risk_countries
        )
        vpn_detected = _ip_in_any_range(ip, briefing.known_vpn_exit_nodes)
        velocity_flag = bool(ip_country and home_country and ip_country != home_country)
        sender_history_match = bool(
            ip_country and home_country and ip_country == home_country
        )

        details = {
            "sender_domain": sender_domain,
            "sending_ip": ip,
            "ip_country": ip_country,
            "account_home_country": home_country,
            "velocity_flag": velocity_flag,
            "high_risk_region": high_risk_region,
            "vpn_detected": vpn_detected,
            "sender_history_match": sender_history_match,
        }

        confidence = briefing.confidence_floor
        if velocity_flag or high_risk_region or vpn_detected:
            confidence = min(1.0, confidence + 0.3)
        if sender_history_match and not (high_risk_region or vpn_detected):
            confidence = min(1.0, confidence + 0.15)

        return write_contribution(
            self._ledger,
            agent_id=self.AGENT_ID,
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            evidence_type=self.EVIDENCE_TYPE,
            details=details,
            confidence=confidence,
        )
