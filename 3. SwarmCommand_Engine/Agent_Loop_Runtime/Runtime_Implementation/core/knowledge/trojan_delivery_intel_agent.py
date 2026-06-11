"""TrojanDeliveryIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 TrojanDeliveryIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Static seed (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable so a Layer 1 caller cannot modify it (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class TrojanDeliveryBriefing(BaseModel):
    """Immutable Trojan-delivery briefing (§3 schema). Tuple fields realize the
    contract's ``list[str]`` immutably."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    weaponised_extensions: tuple[str, ...] = ()
    macro_trigger_patterns: tuple[str, ...] = ()
    delayed_payload_markers: tuple[str, ...] = ()
    known_dropper_hashes: tuple[str, ...] = ()
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. Pattern-based knowledge derived from public weaponised-document
# / dropper intel (macro-enabled office types, staged-payload markers). Hashes are
# clearly synthetic placeholders pending a signed Phase 5 refresh.
_WEAPONISED_EXTENSIONS: tuple[str, ...] = (
    ".docm",
    ".xlsm",
    ".pptm",
    ".iso",
    ".img",
    ".one",
)
_MACRO_TRIGGER_PATTERNS: tuple[str, ...] = (
    "enable macros to view this document",
    "enable editing to unlock content",
    "this content is protected — click enable",
)
_DELAYED_PAYLOAD_MARKERS: tuple[str, ...] = (
    "scheduled task creation",
    "staged download after open",
    "sleep timer before execution",
)
_KNOWN_DROPPER_HASHES: tuple[str, ...] = (
    "SYNTHETIC-SEED-000000000000000000000000000000000000000000000000000000000A",
    "SYNTHETIC-SEED-000000000000000000000000000000000000000000000000000000000B",
)


class TrojanDeliveryIntelAgent:
    """Brief-only Layer 0 Trojan-delivery-intelligence agent. Exposes only ``brief()``."""

    def brief(self) -> TrojanDeliveryBriefing:
        """Return the immutable Trojan-delivery briefing for a Layer 1 agent."""

        return TrojanDeliveryBriefing(
            weaponised_extensions=_WEAPONISED_EXTENSIONS,
            macro_trigger_patterns=_MACRO_TRIGGER_PATTERNS,
            delayed_payload_markers=_DELAYED_PAYLOAD_MARKERS,
            known_dropper_hashes=_KNOWN_DROPPER_HASHES,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.65,
        )
