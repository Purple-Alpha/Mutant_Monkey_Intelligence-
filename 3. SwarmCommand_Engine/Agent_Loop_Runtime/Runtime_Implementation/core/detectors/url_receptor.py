"""URLReceptor — Phase 3 Detection Swarm (#81, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.4
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``url_signal`` (closed, P3-D2). Layer 0 dependency:
``PhishIntelAgent`` — **mandatory** (P3-D3). Boundary: URL resolution cloud-side
only (P3-D4); may not access attachments or headers. Lookup-only against the
phishing briefing, so no ``TokenUsageTracker`` call (Amendment §C). Attacker
cost: burns money — every malicious URL and redirect chain is extracted and
added to the shared indicator database; the domain is worthless after first
detection.
"""

from __future__ import annotations

import re

from core.blackboard import CanonicalEvidenceLedger, EvidenceLedgerEntry, EvidenceType
from core.knowledge import PhishIntelAgent

from ._common import DetectionError, EmailContext, require_email, write_contribution


def _matches_any_pattern(value: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        try:
            if re.search(pattern, value, flags=re.IGNORECASE):
                return True
        except re.error:
            # A malformed seed pattern must not crash the detector — skip it.
            continue
    return False


class URLReceptor:
    """Layer 1 URL-reputation detector. Writes one ``url_signal``."""

    AGENT_ID = "url_receptor"
    EVIDENCE_TYPE = EvidenceType.URL_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        phish_intel: PhishIntelAgent,
    ) -> None:
        if phish_intel is None:
            raise DetectionError(
                "URLReceptor requires a PhishIntelAgent briefing source (P3-D3)"
            )
        self._ledger = ledger
        self._phish_intel = phish_intel

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Produce the URL evidence contribution for one email."""

        email = require_email(email)

        # P3-D3: query the mandatory Layer 0 briefing before producing anything.
        phish = self._phish_intel.brief()

        urls = [u for u in email.urls if isinstance(u, str)]
        lowered = [u.lower() for u in urls]

        malicious_url_detected = any(
            any(domain.lower() in url for domain in phish.known_phish_domains)
            for url in lowered
        )
        credential_harvest_flag = any(
            url in phish.credential_harvest_urls for url in lowered
        ) or any(
            ("login" in url or "verify" in url)
            and any(domain.lower() in url for domain in phish.known_phish_domains)
            for url in lowered
        )
        redirect_chain_anomaly = any(
            _matches_any_pattern(url, phish.lookalike_patterns) for url in lowered
        )
        final_destination = urls[-1] if urls else ""

        if malicious_url_detected or credential_harvest_flag:
            reputation_score = 1.0
        elif redirect_chain_anomaly:
            reputation_score = 0.6
        else:
            reputation_score = 0.0

        details = {
            "urls_found": urls,
            "malicious_url_detected": malicious_url_detected,
            "redirect_chain_anomaly": redirect_chain_anomaly,
            "final_destination": final_destination,
            "credential_harvest_flag": credential_harvest_flag,
            "reputation_score": reputation_score,
        }

        confidence = phish.confidence_floor
        if malicious_url_detected or credential_harvest_flag:
            confidence = min(1.0, confidence + 0.35)

        return write_contribution(
            self._ledger,
            agent_id=self.AGENT_ID,
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            evidence_type=self.EVIDENCE_TYPE,
            details=details,
            confidence=confidence,
        )
