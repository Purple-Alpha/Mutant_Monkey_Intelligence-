"""RansomwareIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 RansomwareIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Static seed (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable so a Layer 1 caller cannot modify it (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class RansomwareBriefing(BaseModel):
    """Immutable ransomware-intel briefing (§3 schema). Tuple fields realize the
    contract's ``list[str]`` immutably (see PhishBriefing for rationale)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    known_delivery_hashes: tuple[str, ...] = ()
    lure_language_patterns: tuple[str, ...] = ()
    known_c2_domains: tuple[str, ...] = ()
    file_extension_flags: tuple[str, ...] = ()
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. Pattern-based knowledge derived from public ransomware-delivery
# intel (common lure language, high-risk delivery extensions). Hashes are clearly
# synthetic placeholders pending a signed Phase 5 refresh with real indicators.
_KNOWN_DELIVERY_HASHES: tuple[str, ...] = (
    "SYNTHETIC-SEED-0000000000000000000000000000000000000000000000000000000001",
    "SYNTHETIC-SEED-0000000000000000000000000000000000000000000000000000000002",
)
_LURE_LANGUAGE_PATTERNS: tuple[str, ...] = (
    "your invoice is attached",
    "encrypted document enclosed",
    "enable content to view this file",
    "secure document — open to decrypt",
)
_KNOWN_C2_DOMAINS: tuple[str, ...] = (
    "payload-delivery.example",
    "update-checkin.example",
)
_FILE_EXTENSION_FLAGS: tuple[str, ...] = (
    ".js",
    ".vbs",
    ".scr",
    ".iso",
    ".lnk",
    ".hta",
)


class RansomwareIntelAgent:
    """Brief-only Layer 0 ransomware-intelligence agent. Exposes only ``brief()``."""

    def brief(self) -> RansomwareBriefing:
        """Return the immutable ransomware-intel briefing for a Layer 1 agent."""

        return RansomwareBriefing(
            known_delivery_hashes=_KNOWN_DELIVERY_HASHES,
            lure_language_patterns=_LURE_LANGUAGE_PATTERNS,
            known_c2_domains=_KNOWN_C2_DOMAINS,
            file_extension_flags=_FILE_EXTENSION_FLAGS,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.65,
        )
