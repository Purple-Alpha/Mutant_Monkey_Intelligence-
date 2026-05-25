"""NorthStar Inbox Shield — Document Metadata Fingerprinting.

Compares upstream PDF Producer/Creator metadata against the per-tenant Vendor
Baseline Store ``pdf_producer_fingerprint`` signal type. v1 is metadata-only:
no PDF byte parsing, no OCR, and no network I/O.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parseaddr
from typing import Literal

from core.blackboard import EmailAttachmentMeta, EmailInboundPayload, GovernanceError
from core.production_state import vendor_baseline
from core.production_state.vendor_baseline import SignalState

MetadataField = Literal["producer", "creator"]

_RISK_FLOOR_DOCUMENT_MISMATCH = 75
_RECOMMENDED_VERIFICATION = (
    "New or stale PDF document-tooling fingerprint observed for this vendor. "
    "Review invoice authenticity before payment; verify through a "
    "previously-known vendor channel if payment details changed."
)
_MAX_REDACTED_DISPLAY_CHARS = 48


@dataclass(frozen=True)
class ExtractedDocumentFingerprint:
    field: MetadataField
    redacted_display: str
    attachment_filename: str
    attachment_index: int


@dataclass(frozen=True)
class DocumentMetadataFinding:
    field: MetadataField
    baseline_state: SignalState
    redacted_display: str
    signal_hash: str | None
    attachment_filename: str
    attachment_index: int
    explanation: str = ""
    recommended_verification: str = ""


@dataclass(frozen=True)
class DocumentMetadataAssessment:
    vendor_domain: str
    extracted_fingerprints: tuple[ExtractedDocumentFingerprint, ...]
    findings: tuple[DocumentMetadataFinding, ...]
    recommended_risk_floor: int
    recommended_action: Literal["none", "needs_review"]
    indicators: tuple[str, ...]


@dataclass(frozen=True)
class _FingerprintCandidate:
    field: MetadataField
    raw_value: str
    normalized_value: str
    redacted_display: str
    attachment_filename: str
    attachment_index: int


def assess_document_metadata_fingerprint(
    *,
    tenant_id: str,
    vendor_domain: str,
    email: EmailInboundPayload,
    now: datetime,
) -> DocumentMetadataAssessment:
    """Compare PDF metadata fingerprints against vendor memory."""

    vendor = _validate_vendor_domain(vendor_domain)
    candidates = _extract_candidates(email)
    extracted = tuple(_candidate_to_extracted(candidate) for candidate in candidates)

    findings: list[DocumentMetadataFinding] = []
    indicators: list[str] = []
    checked: dict[str, str | None] = {}

    for candidate in candidates:
        if candidate.normalized_value in checked:
            continue

        lookup = vendor_baseline.check_signal(
            tenant_id=tenant_id,
            vendor_domain=vendor,
            signal_type="pdf_producer_fingerprint",
            raw_value=candidate.raw_value,
            now=now,
        )
        should_find = lookup.state in ("new", "expired")

        record = vendor_baseline.ingest_signal(
            tenant_id=tenant_id,
            vendor_domain=vendor,
            signal_type="pdf_producer_fingerprint",
            raw_value=candidate.raw_value,
            now=now,
        )
        checked[candidate.normalized_value] = record.signal_hash

        if should_find:
            indicator = (
                "expired_pdf_producer_fingerprint"
                if lookup.state == "expired"
                else "new_pdf_producer_fingerprint"
            )
            if indicator not in indicators:
                indicators.append(indicator)
            findings.append(
                DocumentMetadataFinding(
                    field=candidate.field,
                    baseline_state=lookup.state,
                    redacted_display=candidate.redacted_display,
                    signal_hash=record.signal_hash,
                    attachment_filename=candidate.attachment_filename,
                    attachment_index=candidate.attachment_index,
                    explanation=(
                        "New or stale PDF document-tooling fingerprint observed "
                        f"for vendor {vendor}."
                    ),
                    recommended_verification=_RECOMMENDED_VERIFICATION,
                )
            )

    has_findings = bool(findings)
    return DocumentMetadataAssessment(
        vendor_domain=vendor,
        extracted_fingerprints=extracted,
        findings=tuple(findings),
        recommended_risk_floor=_RISK_FLOOR_DOCUMENT_MISMATCH if has_findings else 0,
        recommended_action="needs_review" if has_findings else "none",
        indicators=tuple(indicators),
    )


def vendor_domain_from_sender(sender: str) -> str:
    """Normalize the sender address to an eTLD+1-style vendor domain."""

    domain = _extract_address_domain(sender)
    if not domain:
        raise GovernanceError("sender address must contain a parseable domain")
    return _root_domain(domain)


def _extract_candidates(email: EmailInboundPayload) -> tuple[_FingerprintCandidate, ...]:
    candidates: list[_FingerprintCandidate] = []
    for index, attachment in enumerate(email.attachments):
        if not _is_relevant_attachment(attachment):
            continue
        metadata = attachment.pdf_metadata
        assert metadata is not None
        if metadata.producer:
            candidate = _candidate_from_raw(
                field="producer",
                raw_value=metadata.producer,
                attachment_filename=attachment.filename,
                attachment_index=index,
            )
            if candidate is not None:
                candidates.append(candidate)
        if metadata.creator:
            candidate = _candidate_from_raw(
                field="creator",
                raw_value=metadata.creator,
                attachment_filename=attachment.filename,
                attachment_index=index,
            )
            if candidate is not None:
                candidates.append(candidate)

    return tuple(candidates)


def _is_relevant_attachment(attachment: EmailAttachmentMeta) -> bool:
    metadata = attachment.pdf_metadata
    if metadata is None:
        return False
    has_producer = bool(metadata.producer and metadata.producer.strip())
    has_creator = bool(metadata.creator and metadata.creator.strip())
    if not has_producer and not has_creator:
        return False
    if attachment.attachment_class in ("invoice", "payment_request"):
        return True
    content_type = (attachment.content_type or "").lower()
    if "pdf" in content_type:
        return True
    return attachment.filename.lower().endswith(".pdf")


def _candidate_from_raw(
    *,
    field: MetadataField,
    raw_value: str,
    attachment_filename: str,
    attachment_index: int,
) -> _FingerprintCandidate | None:
    normalized = _normalize_fingerprint(raw_value)
    if normalized is None:
        return None
    return _FingerprintCandidate(
        field=field,
        raw_value=raw_value,
        normalized_value=normalized,
        redacted_display=_redact_display(normalized),
        attachment_filename=attachment_filename,
        attachment_index=attachment_index,
    )


def _normalize_fingerprint(raw_value: str) -> str | None:
    normalized = re.sub(r"\s+", " ", raw_value).strip().lower()
    if not normalized:
        return None
    return normalized


def _candidate_to_extracted(
    candidate: _FingerprintCandidate,
) -> ExtractedDocumentFingerprint:
    return ExtractedDocumentFingerprint(
        field=candidate.field,
        redacted_display=candidate.redacted_display,
        attachment_filename=candidate.attachment_filename,
        attachment_index=candidate.attachment_index,
    )


def _redact_display(normalized_value: str) -> str:
    if len(normalized_value) <= _MAX_REDACTED_DISPLAY_CHARS:
        return normalized_value
    return f"{normalized_value[:_MAX_REDACTED_DISPLAY_CHARS]}..."


def _extract_address_domain(value: str) -> str:
    if not value:
        return ""
    _, address = parseaddr(value)
    if not address or "@" not in address:
        return ""
    domain = address.rsplit("@", 1)[1].strip().lower()
    return domain or ""


def _root_domain(domain: str) -> str:
    if not domain:
        return ""
    parts = [part for part in domain.strip().lower().split(".") if part]
    if len(parts) <= 2:
        return ".".join(parts)
    return ".".join(parts[-2:])


def _validate_vendor_domain(value: str) -> str:
    if not isinstance(value, str):
        raise GovernanceError("vendor_domain must be a string")
    normalized = value.strip()
    if not normalized:
        raise GovernanceError("vendor_domain cannot be empty")
    if normalized != value:
        raise GovernanceError("vendor_domain must not contain leading or trailing whitespace")
    if normalized != normalized.lower():
        raise GovernanceError("vendor_domain must already be lowercase")
    if any(char.isspace() for char in normalized):
        raise GovernanceError("vendor_domain must not contain whitespace")
    if "/" in normalized or "\\" in normalized:
        raise GovernanceError("vendor_domain must not contain path separators")
    if normalized.startswith(".") or normalized.endswith(".") or ".." in normalized:
        raise GovernanceError("vendor_domain must be a normalized domain")
    return normalized


__all__ = [
    "DocumentMetadataAssessment",
    "DocumentMetadataFinding",
    "ExtractedDocumentFingerprint",
    "MetadataField",
    "assess_document_metadata_fingerprint",
    "vendor_domain_from_sender",
]
