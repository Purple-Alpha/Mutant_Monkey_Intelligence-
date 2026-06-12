"""SenderHistoryAgent — Phase 3 Detection Swarm (#78, Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §3.1
(§11 SIGNED 2026-06-10, ``c522292``) + Amendment 1 §B (§11 SIGNED 2026-06-11,
``56e8b33``).

Evidence type: ``sender_signal`` (closed, P3-D2). Layer 0 dependency: none —
reads from an internal sender-history store (§3.1). Boundary: may only write
``sender_signal``; may not access body, attachments, or URLs. This agent is a
lookup, not a token consumer, so it does NOT call ``TokenUsageTracker``
(Amendment §C). Attacker cost: strips anonymity — a first-time sender
impersonating a known vendor surfaces immediately.
"""

from __future__ import annotations

from core.blackboard import CanonicalEvidenceLedger, EvidenceLedgerEntry, EvidenceType

from ._common import EmailContext, require_email, write_contribution
from .sender_domain import normalize_sender_domain


class SenderHistoryStore:
    """Minimal, injectable prior-contact store (tenant-isolated lookup).

    Keyed by ``(tenant_id, sender_domain)`` so a lookup never crosses tenants
    (P3-D5). At ES2 this is seeded with synthetic history; the ES3 path swaps in
    real per-tenant contact history without changing the agent surface.
    """

    def __init__(self, records: dict | None = None) -> None:
        self._records: dict[tuple[str, str], dict] = dict(records or {})

    def lookup(self, tenant_id: str, sender_domain: str) -> dict | None:
        if not tenant_id or not sender_domain:
            return None
        return self._records.get((tenant_id, sender_domain))


class SenderHistoryAgent:
    """Layer 1 sender-relationship detector. Writes one ``sender_signal``."""

    AGENT_ID = "sender_history_agent"
    EVIDENCE_TYPE = EvidenceType.SENDER_SIGNAL

    def __init__(
        self,
        ledger: CanonicalEvidenceLedger,
        store: SenderHistoryStore | None = None,
    ) -> None:
        self._ledger = ledger
        self._store = store if store is not None else SenderHistoryStore()

    def analyze(self, email: EmailContext) -> EvidenceLedgerEntry:
        """Produce the sender-history evidence contribution for one email."""

        email = require_email(email)

        sender_domain = normalize_sender_domain(email.from_domain)
        record = self._store.lookup(email.tenant_id, sender_domain)
        known = record is not None

        details = {
            "sender_domain": sender_domain,
            "known_contact": known,
            "first_time_sender": not known,
            "prior_interaction_count": int(record["prior_interaction_count"])
            if record and "prior_interaction_count" in record
            else 0,
            "last_contact_date": str(record.get("last_contact_date", ""))
            if record
            else "",
            "established_vendor": bool(record.get("established_vendor", False))
            if record
            else False,
        }

        # Higher confidence when we have a concrete prior-contact record to stand
        # on; a first-time sender is a weaker (but still real) signal.
        confidence = 0.9 if known else 0.6

        return write_contribution(
            self._ledger,
            agent_id=self.AGENT_ID,
            tenant_id=email.tenant_id,
            email_id=email.email_id,
            evidence_type=self.EVIDENCE_TYPE,
            details=details,
            confidence=confidence,
        )
