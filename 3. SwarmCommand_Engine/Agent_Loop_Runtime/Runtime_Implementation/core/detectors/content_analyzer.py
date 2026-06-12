"""ContentAnalyzer — Phase 3 Detection Swarm (#80, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.3
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 §C (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``content_signal`` (closed, P3-D2). Layer 0 dependency:
``PhishIntelAgent`` + ``BECIntelAgent`` — **both mandatory** (P3-D3). Boundary:
may read subject and body only; may not access attachments, URLs, or headers
directly. This is a **token-consuming** agent: per Amendment §C every analysis
run records usage against the email's own ``tenant_id`` via ``TokenUsageTracker``
(Attacker Cost Model — Time). Attacker cost: BEC language must be crafted to
beat a continuously updated knowledge base.
"""

from __future__ import annotations

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceType,
    TokenActionType,
    TokenUsageRecord,
    TokenUsageTracker,
)
from core.knowledge import BECIntelAgent, PhishIntelAgent

from ._common import DetectionError, EmailContext, require_email, write_contribution


def _estimate_tokens(text: str) -> int:
    """Synthetic token estimate (~4 chars/token), floored at 1 for a real run."""

    return max(1, len(text) // 4)


def _any_contains(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern.lower() in text for pattern in patterns)


class ContentAnalyzer:
    """Layer 1 NLP content detector. Writes one ``content_signal``."""

    AGENT_ID = "content_analyzer"
    MODEL_ID = "mm-content-analyzer-v1"
    EVIDENCE_TYPE = EvidenceType.CONTENT_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        phish_intel: PhishIntelAgent,
        bec_intel: BECIntelAgent,
        token_tracker: TokenUsageTracker,
    ) -> None:
        if phish_intel is None or bec_intel is None:
            raise DetectionError(
                "ContentAnalyzer requires PhishIntelAgent + BECIntelAgent briefings "
                "(P3-D3)"
            )
        if token_tracker is None:
            raise DetectionError(
                "ContentAnalyzer is a token-consuming agent and requires a "
                "TokenUsageTracker for per-tenant attribution (Amendment §C)"
            )
        self._ledger = ledger
        self._phish_intel = phish_intel
        self._bec_intel = bec_intel
        self._token_tracker = token_tracker

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Produce the content evidence contribution for one email."""

        email = require_email(email)

        # P3-D3: both mandatory Layer 0 briefings queried before producing output.
        phish = self._phish_intel.brief()
        bec = self._bec_intel.brief()

        text = f"{email.subject}\n{email.body}".lower()

        urgency_detected = _any_contains(text, phish.social_engineering_cues) or _any_contains(
            text, bec.wire_transfer_trigger_phrases
        )
        bec_pattern_match = _any_contains(text, bec.invoice_fraud_templates) or _any_contains(
            text, bec.vendor_redirect_patterns
        )
        wire_transfer_request = _any_contains(text, bec.wire_transfer_trigger_phrases)
        ceo_impersonation_flag = _any_contains(text, bec.ceo_impersonation_patterns)

        pressure_hits = sum(
            1 for cue in phish.social_engineering_cues if cue.lower() in text
        ) + sum(
            1 for phrase in bec.wire_transfer_trigger_phrases if phrase.lower() in text
        )
        sentiment_score = min(1.0, 0.25 * pressure_hits)

        policy_violation = (
            "wire_transfer_request_requires_two_channel_verification"
            if wire_transfer_request
            else ""
        )

        details = {
            "urgency_detected": urgency_detected,
            "bec_pattern_match": bec_pattern_match,
            "wire_transfer_request": wire_transfer_request,
            "ceo_impersonation_flag": ceo_impersonation_flag,
            "policy_violation": policy_violation,
            "sentiment_score": sentiment_score,
            # language-vs-sender-history baseline needs real per-tenant style data
            # (ES3); held at False at ES2 rather than emitting a fabricated signal.
            "language_anomaly": False,
        }

        confidence = max(
            phish.confidence_floor,
            bec.confidence_floor,
        )
        if bec_pattern_match or wire_transfer_request or ceo_impersonation_flag:
            confidence = min(1.0, confidence + 0.25)

        # Amendment §C: attribute the model-token cost of this run to the email's
        # own tenant BEFORE the contribution is written. Recorded against the
        # agent's tenant_id so an attacker pays for the tokens they cause.
        self._token_tracker.record(
            TokenUsageRecord(
                tenant_id=email.tenant_id,
                agent_id=self.AGENT_ID,
                model_id=self.MODEL_ID,
                token_count=_estimate_tokens(text),
                action_type=TokenActionType.DETECTION,
                session_id=email.email_id,
            )
        )

        return write_contribution(
            self._ledger,
            agent_id=self.AGENT_ID,
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            evidence_type=self.EVIDENCE_TYPE,
            details=details,
            confidence=confidence,
        )
