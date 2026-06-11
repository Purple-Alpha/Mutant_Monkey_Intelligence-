"""PhishIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 PhishIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Knowledge is static at build, seeded from public
threat-intelligence frameworks (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable (frozen model + tuple fields) so a calling Layer 1
agent cannot modify it (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ES1 synthetic seed snapshot (ISO 8601). Refreshed only via the signed Phase 5
# mutation process; never updated autonomously by this agent (P2-D5).
KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class PhishBriefing(BaseModel):
    """Immutable phishing-intel briefing (§3 schema).

    ``list[str]`` fields in the signed schema are realized as ``tuple[str, ...]``
    so the briefing is deeply immutable — the contract requires a Layer 1 caller
    cannot modify the briefing, and a frozen model alone would still allow
    ``briefing.field.append(...)`` on a list. Tuples close that gap.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    known_phish_domains: tuple[str, ...] = ()
    lookalike_patterns: tuple[str, ...] = ()
    credential_harvest_urls: tuple[str, ...] = ()
    social_engineering_cues: tuple[str, ...] = ()
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. Illustrative/pattern-based knowledge derived from public
# phishing-intel frameworks (APWG patterns, common credential-harvest lures).
# Concrete indicators use RFC-2606 ``.example`` names so no real entity is named.
_KNOWN_PHISH_DOMAINS: tuple[str, ...] = (
    "secure-login-verify.example",
    "account-update-portal.example",
    "mail-quota-renew.example",
)
_LOOKALIKE_PATTERNS: tuple[str, ...] = (
    r"micr0soft",
    r"paypa1",
    r"0ffice365",
    r".*-secure-login\..*",
    r".*-account-verify\..*",
)
_CREDENTIAL_HARVEST_URLS: tuple[str, ...] = (
    "https://secure-login-verify.example/login",
    "https://account-update-portal.example/session/validate",
)
_SOCIAL_ENGINEERING_CUES: tuple[str, ...] = (
    "verify your account immediately",
    "your password will expire",
    "unusual sign-in activity detected",
    "confirm your identity to avoid suspension",
)


class PhishIntelAgent:
    """Brief-only Layer 0 phishing-intelligence agent.

    Exposes only ``brief()``. There is no detect/score/flag/verdict method and no
    blackboard write path — those omissions are the contract boundary (P2-D1/D7),
    asserted by the adversarial test class.
    """

    def brief(self) -> PhishBriefing:
        """Return the immutable phishing-intel briefing for a Layer 1 agent."""

        return PhishBriefing(
            known_phish_domains=_KNOWN_PHISH_DOMAINS,
            lookalike_patterns=_LOOKALIKE_PATTERNS,
            credential_harvest_urls=_CREDENTIAL_HARVEST_URLS,
            social_engineering_cues=_SOCIAL_ENGINEERING_CUES,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.6,
        )
