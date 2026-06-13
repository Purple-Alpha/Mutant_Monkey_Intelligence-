"""Shadow Watcher Layer 1 observation models.

Governing contract:
``4. Product_Roadmap/Shadow_Watcher_Swarm_Contract.md`` §11 SIGNED
2026-06-12 (Matt Nichol), Layer 1 Watch Layer.

Layer 1 watches suspicious events and emits alarm-input facts only. It is
separate from ``core/watchers/`` (Layer 6 governance watchers) and separate from
``core/blackboard/``: Shadow Watchers observe, they do not write the evidence
chain or decide fraud.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from core.blackboard.models import StrictModel


class ShadowWatcherError(Exception):
    """Raised when a Shadow Watcher boundary or schema rule is violated."""


class ShadowWatcherKind(str, Enum):
    SENDER = "sender"
    PAYMENT = "payment"
    LANGUAGE = "language"
    ATTACHMENT = "attachment"
    GEO = "geo"
    VENDOR_HISTORY = "vendor_history"


class CandidateAlarmFact(str, Enum):
    SENDER_DOMAIN_OBSERVED = "sender_domain_observed"
    REPLY_TO_DOMAIN_DRIFT = "reply_to_domain_drift"
    PAYMENT_DESTINATION_PRESENT = "payment_destination_present"
    INVOICE_TEMPLATE_PRESENT = "invoice_template_present"
    URGENCY_PRESSURE_LANGUAGE = "urgency_pressure_language"
    SECRECY_PRESSURE_LANGUAGE = "secrecy_pressure_language"
    ATTACHMENT_HASH_PRESENT = "attachment_hash_present"
    PDF_FINGERPRINT_PRESENT = "pdf_fingerprint_present"
    GEO_COUNTRY_DRIFT = "geo_country_drift"
    ASN_OBSERVED = "asn_observed"
    VENDOR_KNOWN = "vendor_known"
    VENDOR_NEW_OR_THIN_HISTORY = "vendor_new_or_thin_history"
    VERIFICATION_FAILURE_HISTORY = "verification_failure_history"


class ObservedFact(StrictModel):
    name: str = Field(min_length=1)
    value: str | int | float | bool
    source_field: str = Field(min_length=1)


class ShadowInference(StrictModel):
    label: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class ShadowAttachment(StrictModel):
    filename: str = ""
    sha256: str = ""
    extension: str = ""
    pdf_fingerprint: str = ""


class ShadowEmailEvent(StrictModel):
    """Q-class input. May carry raw text, but emitted observations never do."""

    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    sender_domain: str = ""
    reply_to_domain: str = ""
    payment_destinations: tuple[str, ...] = ()
    invoice_template_id: str = ""
    body_text: str = ""
    attachments: tuple[ShadowAttachment, ...] = ()
    ip_country: str = ""
    account_home_country: str = ""
    asn: str = ""
    vendor_domain: str = ""
    vendor_known: bool = False
    prior_vendor_interactions: int = Field(default=0, ge=0)
    verification_failures: int = Field(default=0, ge=0)


class ShadowObservationRecord(StrictModel):
    """One append-only Layer 1 output: facts, inferences, and alarm inputs."""

    record_id: UUID = Field(default_factory=uuid4)
    watcher_id: str = Field(min_length=1)
    watcher_kind: ShadowWatcherKind
    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    observed_facts: tuple[ObservedFact, ...] = ()
    inferences: tuple[ShadowInference, ...] = ()
    evidence_used: tuple[str, ...] = ()
    candidate_alarm_facts: tuple[CandidateAlarmFact, ...] = ()
    confidence: float = Field(ge=0.0, le=1.0)
    raw_text_present: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def enforce_layer1_boundaries(self) -> "ShadowObservationRecord":
        if self.raw_text_present:
            raise ValueError("Shadow Watcher observations may not contain raw text")

        forbidden = (
            "fraud",
            "malicious",
            "block",
            "quarantine",
            "retaliat",
            "punish",
            "dox",
            "recommended_action",
            "verdict",
        )
        blob = " ".join(
            [
                *(f.name for f in self.observed_facts),
                *(str(f.value) for f in self.observed_facts),
                *(i.label for i in self.inferences),
                *(i.rationale for i in self.inferences),
                *self.evidence_used,
            ]
        ).lower()
        if any(term in blob for term in forbidden):
            raise ValueError("Shadow Watcher observation contains forbidden action/verdict language")
        return self


class ShadowObservationLog:
    """Append-only Shadow Watcher fact store. No update/delete API."""

    def __init__(self, jsonl_path: Path | None = None) -> None:
        self.jsonl_path = Path(jsonl_path) if jsonl_path is not None else None
        self._records: list[ShadowObservationRecord] = []

    def append(self, record: ShadowObservationRecord) -> ShadowObservationRecord:
        self._records.append(record)
        if self.jsonl_path is not None:
            self._append_jsonl(record)
        return record

    def _append_jsonl(self, record: ShadowObservationRecord) -> None:
        assert self.jsonl_path is not None
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")

    def entries(self) -> tuple[ShadowObservationRecord, ...]:
        return tuple(self._records)

    def for_watcher(self, watcher_id: str) -> tuple[ShadowObservationRecord, ...]:
        return tuple(record for record in self._records if record.watcher_id == watcher_id)

    def for_kind(self, kind: ShadowWatcherKind) -> tuple[ShadowObservationRecord, ...]:
        return tuple(record for record in self._records if record.watcher_kind is kind)


def fact(name: str, value: Any, source_field: str) -> ObservedFact:
    return ObservedFact(name=name, value=value, source_field=source_field)


def inference(label: str, rationale: str) -> ShadowInference:
    return ShadowInference(label=label, rationale=rationale)


__all__ = [
    "CandidateAlarmFact",
    "ObservedFact",
    "ShadowAttachment",
    "ShadowEmailEvent",
    "ShadowInference",
    "ShadowObservationLog",
    "ShadowObservationRecord",
    "ShadowWatcherError",
    "ShadowWatcherKind",
    "fact",
    "inference",
]
