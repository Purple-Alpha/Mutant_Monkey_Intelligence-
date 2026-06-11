"""AIGenContentIntelAgent — Phase 2 Layer 0 Knowledge Foundation.

Governing contract: ``Phase2_Knowledge_Foundation_Agent_Design_Contract.md``
§11 SIGNED 2026-06-10 (Matt Nichol), §3 AIGenContentIntelAgent.

Brief only (P2-D1): no detection, no scoring, no verdicts, no AgentContribution.
Read-only reference for Layer 1 (P2-D7): this module does NOT import or write
``core/blackboard``. Static seed (P2-D4); no autonomous updates (P2-D5). The
briefing object is immutable so a Layer 1 caller cannot modify it (§3).

Context: a high image-to-text ratio or AI-generated copy is a *briefing signal*
for Layer 1, never a verdict here — over-flagging legitimate AI-assisted or
image-heavy mail (e.g. newsletters) is a known false-positive trap, so these are
advisory thresholds for a downstream detector, not a block decision.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOWLEDGE_SNAPSHOT = "2026-06-10T00:00:00+00:00"


class ImageRatioThresholds(BaseModel):
    """Immutable image-to-text ratio advisory thresholds.

    Realizes the §3 ``image_ratio_thresholds: dict`` field as a closed, frozen
    structure. Values are advisory inputs for a Layer 1 detector, not verdicts.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    images_to_text_warn: float = Field(ge=0.0, le=1.0)
    images_to_text_review: float = Field(ge=0.0, le=1.0)


class AIGenContentBriefing(BaseModel):
    """Immutable AI-generated-content briefing (§3 schema). Tuple fields realize
    the contract's ``list[str]`` immutably; thresholds are a frozen sub-model."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ai_text_signatures: tuple[str, ...] = ()
    deepfake_image_markers: tuple[str, ...] = ()
    ai_phishing_templates: tuple[str, ...] = ()
    image_ratio_thresholds: ImageRatioThresholds
    last_updated: str
    confidence_floor: float = Field(ge=0.0, le=1.0)


# Static ES1 seed. Pattern-based knowledge derived from public AI-generated-content
# and deepfake-indicator research.
_AI_TEXT_SIGNATURES: tuple[str, ...] = (
    "as an ai language model",
    "i cannot fulfill that request",
    "in conclusion, it is important to note",
    "uniformly polished phrasing with no personal voice",
)
_DEEPFAKE_IMAGE_MARKERS: tuple[str, ...] = (
    "inconsistent lighting across subject and background",
    "warped or garbled text rendered inside the image",
    "asymmetric facial features or irregular teeth",
)
_AI_PHISHING_TEMPLATES: tuple[str, ...] = (
    "perfect grammar mass-mail with urgent call to action",
    "highly personalized lure with no spelling errors",
)
_IMAGE_RATIO_THRESHOLDS = ImageRatioThresholds(
    images_to_text_warn=0.6,
    images_to_text_review=0.85,
)


class AIGenContentIntelAgent:
    """Brief-only Layer 0 AI-generated-content-intelligence agent. Exposes only ``brief()``."""

    def brief(self) -> AIGenContentBriefing:
        """Return the immutable AI-gen-content briefing for a Layer 1 agent."""

        return AIGenContentBriefing(
            ai_text_signatures=_AI_TEXT_SIGNATURES,
            deepfake_image_markers=_DEEPFAKE_IMAGE_MARKERS,
            ai_phishing_templates=_AI_PHISHING_TEMPLATES,
            image_ratio_thresholds=_IMAGE_RATIO_THRESHOLDS,
            last_updated=KNOWLEDGE_SNAPSHOT,
            confidence_floor=0.5,
        )
