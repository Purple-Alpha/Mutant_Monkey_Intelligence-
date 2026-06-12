"""AttachmentSandbox — Phase 3 Detection Swarm (#82, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.5
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 §C (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``attachment_signal`` (closed, P3-D2). Layer 0 dependency:
``TrojanDeliveryIntelAgent`` + ``RansomwareIntelAgent`` — **both mandatory**
(P3-D3). Boundary: sandbox fully isolated cloud-side (P3-D4). The
``zero_day_candidate`` flag feeds the mutation-engine tracker **only** — it never
auto-deploys a rule (§6: zero-day auto-deploy is an immediate-fail). This is a
**token-consuming** agent: per Amendment §C every detonation run records usage
against the email's own ``tenant_id``. Attacker cost — all four dimensions.
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
from core.knowledge import RansomwareIntelAgent, TrojanDeliveryIntelAgent

from ._common import DetectionError, EmailContext, require_email, write_contribution

# Synthetic per-detonation token cost (ES2). The real sandbox cost is measured at
# ES3; the per-tenant attribution path (Amendment §C) is identical either way.
_SANDBOX_TOKENS_PER_DETONATION = 256
_MACRO_EXTENSIONS = (".docm", ".xlsm", ".pptm")


class AttachmentSandbox:
    """Layer 1 attachment-detonation detector. Writes one ``attachment_signal``."""

    AGENT_ID = "attachment_sandbox"
    MODEL_ID = "mm-attachment-sandbox-v1"
    EVIDENCE_TYPE = EvidenceType.ATTACHMENT_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        trojan_intel: TrojanDeliveryIntelAgent,
        ransomware_intel: RansomwareIntelAgent,
        token_tracker: TokenUsageTracker,
    ) -> None:
        if trojan_intel is None or ransomware_intel is None:
            raise DetectionError(
                "AttachmentSandbox requires TrojanDeliveryIntelAgent + "
                "RansomwareIntelAgent briefings (P3-D3)"
            )
        if token_tracker is None:
            raise DetectionError(
                "AttachmentSandbox is a token-consuming agent and requires a "
                "TokenUsageTracker for per-tenant attribution (Amendment §C)"
            )
        self._ledger = ledger
        self._trojan_intel = trojan_intel
        self._ransomware_intel = ransomware_intel
        self._token_tracker = token_tracker

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Detonate attachment metadata cloud-side; write one contribution."""

        email = require_email(email)

        # P3-D3: both mandatory Layer 0 briefings queried before producing output.
        trojan = self._trojan_intel.brief()
        ransomware = self._ransomware_intel.brief()

        attachments = email.attachments
        attachment_present = len(attachments) > 0

        first = attachments[0] if attachment_present else None
        file_hash = first.sha256 if first else ""
        extension = (first.extension.lower() if first and first.extension else "")

        known_hashes = set(trojan.known_dropper_hashes) | set(
            ransomware.known_delivery_hashes
        )
        flagged_extensions = set(trojan.weaponised_extensions) | set(
            ransomware.file_extension_flags
        )

        known_malicious_hash = bool(file_hash) and file_hash in known_hashes
        extension_flagged = bool(extension) and extension in flagged_extensions

        # Synthetic behavioural detonation (ES2): a present attachment is executed
        # in the isolated sandbox; a known-malicious hash exhibits callback.
        execution_attempted = attachment_present
        network_callback_detected = known_malicious_hash
        callback_destination = (
            ransomware.known_c2_domains[0]
            if network_callback_detected and ransomware.known_c2_domains
            else ""
        )
        file_drop_detected = attachment_present and extension_flagged
        macro_execution = extension in _MACRO_EXTENSIONS

        # Zero-day candidate: a flagged-extension attachment whose hash is NOT in
        # any known database — unknown behaviour. This flag feeds the mutation
        # engine tracker ONLY; this agent deploys no rule (§6 immediate-fail).
        zero_day_candidate = (
            attachment_present and extension_flagged and not known_malicious_hash
        )

        details = {
            "attachment_present": attachment_present,
            "file_hash": file_hash,
            "known_malicious_hash": known_malicious_hash,
            "execution_attempted": execution_attempted,
            "network_callback_detected": network_callback_detected,
            "callback_destination": callback_destination,
            "file_drop_detected": file_drop_detected,
            "macro_execution": macro_execution,
            "zero_day_candidate": zero_day_candidate,
        }

        if known_malicious_hash:
            confidence = 0.95
        elif zero_day_candidate:
            confidence = 0.75
        elif attachment_present:
            confidence = max(trojan.confidence_floor, ransomware.confidence_floor)
        else:
            confidence = 0.5

        # Amendment §C: attribute the detonation's token cost to the email's own
        # tenant before the contribution is written.
        if attachment_present:
            self._token_tracker.record(
                TokenUsageRecord(
                    tenant_id=email.tenant_id,
                    agent_id=self.AGENT_ID,
                    model_id=self.MODEL_ID,
                    token_count=_SANDBOX_TOKENS_PER_DETONATION,
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
