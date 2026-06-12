"""ImageClassifier — Phase 3 Detection Swarm (#83, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.6
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``image_signal`` (closed, P3-D2). Layer 0 dependency:
``AIGenContentIntelAgent`` — **mandatory** (P3-D3). Lookup-only against the
briefing, so no ``TokenUsageTracker`` call (Amendment §C). The ``spam_signal_only``
field is critical: when true it tells ReconciliationAgent this is a delivery
problem, NOT a fraud problem — a different action path. This agent never routes
to a fraud path itself (§6: spam_signal_only routing to fraud is immediate-fail).
Attacker cost: AI-generated phishing imagery is pattern-matched against a
continuously updated signature library.
"""

from __future__ import annotations

from core.blackboard import CanonicalEvidenceLedger, EvidenceLedgerEntry, EvidenceType
from core.knowledge import AIGenContentIntelAgent

from ._common import DetectionError, EmailContext, require_email, write_contribution


def _any_contains(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern.lower() in text for pattern in patterns)


class ImageClassifier:
    """Layer 1 image-ratio / AI-content detector. Writes one ``image_signal``."""

    AGENT_ID = "image_classifier"
    EVIDENCE_TYPE = EvidenceType.IMAGE_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        aigen_intel: AIGenContentIntelAgent,
    ) -> None:
        if aigen_intel is None:
            raise DetectionError(
                "ImageClassifier requires an AIGenContentIntelAgent briefing source "
                "(P3-D3)"
            )
        self._ledger = ledger
        self._aigen_intel = aigen_intel

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Produce the image evidence contribution for one email."""

        email = require_email(email)

        # P3-D3: query the mandatory Layer 0 briefing before producing anything.
        briefing = self._aigen_intel.brief()
        thresholds = briefing.image_ratio_thresholds

        image_count = email.image_count
        images_present = image_count > 0

        # Synthetic image-to-text ratio (ES2): images relative to body word count.
        word_count = len(email.body.split())
        denominator = image_count + word_count
        image_text_ratio = (image_count / denominator) if denominator else 0.0

        text = f"{email.subject}\n{email.body}".lower()
        ai_generated_detected = _any_contains(text, briefing.ai_text_signatures) or _any_contains(
            text, briefing.ai_phishing_templates
        )
        # Deepfake markers describe image-pixel artifacts that need real image
        # bytes (ES3); held False at ES2 rather than emitting a fabricated signal.
        deepfake_indicator = False

        bulk_content_flag = images_present and image_text_ratio >= thresholds.images_to_text_warn

        # spam_signal_only: surface signals look like bulk/spam but NO fraud
        # indicators present. This is the false-positive protection the contract
        # calls out — never a fraud route.
        spam_signal_only = (
            bulk_content_flag and not ai_generated_detected and not deepfake_indicator
        )

        details = {
            "images_present": images_present,
            "image_count": image_count,
            "image_text_ratio": image_text_ratio,
            "ai_generated_detected": ai_generated_detected,
            "deepfake_indicator": deepfake_indicator,
            "bulk_content_flag": bulk_content_flag,
            "spam_signal_only": spam_signal_only,
        }

        confidence = briefing.confidence_floor
        if ai_generated_detected:
            confidence = min(1.0, confidence + 0.25)

        return write_contribution(
            self._ledger,
            agent_id=self.AGENT_ID,
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            evidence_type=self.EVIDENCE_TYPE,
            details=details,
            confidence=confidence,
        )
