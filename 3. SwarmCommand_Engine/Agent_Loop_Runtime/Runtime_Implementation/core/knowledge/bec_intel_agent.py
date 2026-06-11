"""BECIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 BECIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Static seed (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable so a Layer 1 caller cannot modify it (§3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class BECBriefing(BaseModel):
    """Immutable business-email-compromise briefing (§3 schema). Tuple fields
    realize the contract's ``list[str]`` immutably."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ceo_impersonation_patterns: tuple[str, ...] = ()
    invoice_fraud_templates: tuple[str, ...] = ()
    wire_transfer_trigger_phrases: tuple[str, ...] = ()
    vendor_redirect_patterns: tuple[str, ...] = ()
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. Pattern-based knowledge derived from public BEC/invoice-fraud
# intel (display-name spoofing, payment-redirect language).
_CEO_IMPERSONATION_PATTERNS: tuple[str, ...] = (
    r"display name matches an executive but reply-to is free webmail",
    r"sent from my (iphone|mobile)",
    r"are you at your desk\??",
)
_INVOICE_FRAUD_TEMPLATES: tuple[str, ...] = (
    "updated banking details for your next payment",
    "please remit to the new account below",
    "our accounts receivable information has changed",
)
_WIRE_TRANSFER_TRIGGER_PHRASES: tuple[str, ...] = (
    "urgent wire transfer needed",
    "are you available to process a payment",
    "this must be completed today and kept confidential",
)
_VENDOR_REDIRECT_PATTERNS: tuple[str, ...] = (
    "our bank has changed, use the following account going forward",
    "disregard previous invoice, updated payment details attached",
)


class BECIntelAgent:
    """Brief-only Layer 0 BEC-intelligence agent. Exposes only ``brief()``."""

    def brief(self) -> BECBriefing:
        """Return the immutable BEC-intel briefing for a Layer 1 agent."""

        return BECBriefing(
            ceo_impersonation_patterns=_CEO_IMPERSONATION_PATTERNS,
            invoice_fraud_templates=_INVOICE_FRAUD_TEMPLATES,
            wire_transfer_trigger_phrases=_WIRE_TRANSFER_TRIGGER_PHRASES,
            vendor_redirect_patterns=_VENDOR_REDIRECT_PATTERNS,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.6,
        )
