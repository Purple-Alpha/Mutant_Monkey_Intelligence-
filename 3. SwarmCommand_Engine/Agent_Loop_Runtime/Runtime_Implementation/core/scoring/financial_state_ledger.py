"""NorthStar Inbox Shield — Financial State Ledger / Delta Tripwire.

Stateful deterministic detector for one narrow BEC control: a known vendor
email introduced a payment-destination signal the tenant has not seen before,
or one that has gone stale in the Vendor Baseline Store.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit

from core.blackboard import EmailInboundPayload, GovernanceError
from core.production_state import vendor_baseline
from core.production_state.vendor_baseline import SignalState


FinancialSignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
]
SignalSource = Literal["body_plain", "attachment_extracted_text"]

_FINANCIAL_SIGNAL_TYPES: frozenset[str] = frozenset(
    {
        "routing_number",
        "swift_bic_code",
        "iban",
        "account_number",
        "payment_portal_url",
    }
)
_RISK_FLOOR_DELTA_TRIPWIRE = 85
_RECOMMENDED_VERIFICATION = (
    "New or stale payment-destination signal observed for this vendor. "
    "Verify through a previously-known vendor channel before payment. "
    "Do not use phone numbers, links, or payment instructions from this email "
    "to verify the change."
)

_ROUTING_RE = re.compile(
    r"\b(?:routing(?:\s+(?:number|no\.?))?|aba)\b[\s:#-]{0,20}"
    r"([0-9][0-9\s-]{7,24}[0-9])",
    re.IGNORECASE,
)
_SWIFT_RE = re.compile(
    r"\b(?:swift(?:\s*/\s*bic)?|bic)\b[\s:#-]{0,20}"
    r"([A-Z0-9]{4}\s*[A-Z]{2}\s*[A-Z0-9]{2}(?:\s*[A-Z0-9]{3})?)\b",
    re.IGNORECASE,
)
_IBAN_RE = re.compile(
    r"\biban\b[\s:#-]{0,20}([A-Z]{2}\s*[0-9A-Z][0-9A-Z\s-]{2,42})\b",
    re.IGNORECASE,
)
_ACCOUNT_RE = re.compile(
    r"\b(?:account|acct)(?:\s*(?:number|no\.?|#))?\b[\s:#-]{0,20}"
    r"([0-9][0-9\s-]{2,30}[0-9])",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"\bhttps?://[^\s<>)\"']+|\b[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s<>)\"']*)?", re.IGNORECASE)
_PAYMENT_CONTEXT_RE = re.compile(r"\b(?:pay|payment|remit|portal|invoice|billing)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ExtractedFinancialSignal:
    signal_type: FinancialSignalType
    source: SignalSource
    redacted_display: str
    attachment_filename: str | None = None
    attachment_index: int | None = None


@dataclass(frozen=True)
class DeltaTripwireFinding:
    signal_type: FinancialSignalType
    baseline_state: SignalState
    redacted_display: str
    source: SignalSource
    signal_hash: str | None
    attachment_filename: str | None = None
    attachment_index: int | None = None
    explanation: str = ""
    recommended_verification: str = ""


@dataclass(frozen=True)
class FinancialStateLedgerAssessment:
    vendor_domain: str
    extracted_signals: tuple[ExtractedFinancialSignal, ...]
    findings: tuple[DeltaTripwireFinding, ...]
    recommended_risk_floor: int
    recommended_action: Literal["none", "needs_review"]
    requires_out_of_band_verification: bool


@dataclass(frozen=True)
class _FinancialSignalCandidate:
    signal_type: FinancialSignalType
    raw_value: str
    normalized_value: str
    source: SignalSource
    redacted_display: str
    attachment_filename: str | None = None
    attachment_index: int | None = None


def assess_financial_state_delta(
    *,
    tenant_id: str,
    vendor_domain: str,
    email: EmailInboundPayload,
    now: datetime,
) -> FinancialStateLedgerAssessment:
    """Extract payment-destination signals and compare them to vendor memory.

    Raw candidate values remain private to this call. The returned assessment
    contains only signal type, state, source metadata, redacted display values,
    and Vendor Baseline Store hashes.
    """

    vendor = _validate_vendor_domain(vendor_domain)
    candidates = _extract_candidates(email)
    extracted = tuple(_candidate_to_extracted(candidate) for candidate in candidates)

    findings: list[DeltaTripwireFinding] = []
    checked: dict[tuple[FinancialSignalType, str], str | None] = {}

    for candidate in candidates:
        key = (candidate.signal_type, candidate.normalized_value)
        if key in checked:
            continue

        lookup = vendor_baseline.check_signal(
            tenant_id=tenant_id,
            vendor_domain=vendor,
            signal_type=candidate.signal_type,
            raw_value=candidate.raw_value,
            now=now,
        )
        should_find = lookup.state in ("new", "expired")

        record = vendor_baseline.ingest_signal(
            tenant_id=tenant_id,
            vendor_domain=vendor,
            signal_type=candidate.signal_type,
            raw_value=candidate.raw_value,
            now=now,
        )
        checked[key] = record.signal_hash

        if should_find:
            findings.append(
                DeltaTripwireFinding(
                    signal_type=candidate.signal_type,
                    baseline_state=lookup.state,
                    redacted_display=candidate.redacted_display,
                    source=candidate.source,
                    signal_hash=record.signal_hash,
                    attachment_filename=candidate.attachment_filename,
                    attachment_index=candidate.attachment_index,
                    explanation=(
                        "New or stale payment-destination signal observed "
                        f"for vendor {vendor}."
                    ),
                    recommended_verification=_RECOMMENDED_VERIFICATION,
                )
            )

    has_findings = bool(findings)
    return FinancialStateLedgerAssessment(
        vendor_domain=vendor,
        extracted_signals=extracted,
        findings=tuple(findings),
        recommended_risk_floor=_RISK_FLOOR_DELTA_TRIPWIRE if has_findings else 0,
        recommended_action="needs_review" if has_findings else "none",
        requires_out_of_band_verification=has_findings,
    )


def _extract_candidates(email: EmailInboundPayload) -> tuple[_FinancialSignalCandidate, ...]:
    candidates: list[_FinancialSignalCandidate] = []
    candidates.extend(_extract_from_text(email.body_plain, source="body_plain"))

    for index, attachment in enumerate(email.attachments):
        if attachment.extracted_text is None:
            continue
        candidates.extend(
            _extract_from_text(
                attachment.extracted_text,
                source="attachment_extracted_text",
                attachment_filename=attachment.filename,
                attachment_index=index,
            )
        )

    return _dedupe_source_candidates(candidates)


def _extract_from_text(
    text: str,
    *,
    source: SignalSource,
    attachment_filename: str | None = None,
    attachment_index: int | None = None,
) -> list[_FinancialSignalCandidate]:
    candidates: list[_FinancialSignalCandidate] = []
    for regex, signal_type in (
        (_ROUTING_RE, "routing_number"),
        (_SWIFT_RE, "swift_bic_code"),
        (_IBAN_RE, "iban"),
        (_ACCOUNT_RE, "account_number"),
    ):
        for match in regex.finditer(text):
            candidate = _candidate_from_raw(
                signal_type=signal_type,
                raw_value=match.group(1),
                source=source,
                attachment_filename=attachment_filename,
                attachment_index=attachment_index,
            )
            if candidate is not None:
                candidates.append(candidate)

    for match in _URL_RE.finditer(text):
        if not _has_payment_context(text, match.start(), match.end()):
            continue
        candidate = _candidate_from_raw(
            signal_type="payment_portal_url",
            raw_value=match.group(0),
            source=source,
            attachment_filename=attachment_filename,
            attachment_index=attachment_index,
        )
        if candidate is not None:
            candidates.append(candidate)

    return candidates


def _candidate_from_raw(
    *,
    signal_type: FinancialSignalType,
    raw_value: str,
    source: SignalSource,
    attachment_filename: str | None,
    attachment_index: int | None,
) -> _FinancialSignalCandidate | None:
    normalized = _normalize_candidate(signal_type, raw_value)
    if normalized is None:
        return None
    return _FinancialSignalCandidate(
        signal_type=signal_type,
        raw_value=raw_value,
        normalized_value=normalized,
        source=source,
        redacted_display=_redact(signal_type, normalized),
        attachment_filename=attachment_filename,
        attachment_index=attachment_index,
    )


def _dedupe_source_candidates(
    candidates: list[_FinancialSignalCandidate],
) -> tuple[_FinancialSignalCandidate, ...]:
    seen: set[tuple[FinancialSignalType, str, SignalSource]] = set()
    deduped: list[_FinancialSignalCandidate] = []
    for candidate in candidates:
        key = (candidate.signal_type, candidate.normalized_value, candidate.source)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return tuple(deduped)


def _candidate_to_extracted(candidate: _FinancialSignalCandidate) -> ExtractedFinancialSignal:
    return ExtractedFinancialSignal(
        signal_type=candidate.signal_type,
        source=candidate.source,
        redacted_display=candidate.redacted_display,
        attachment_filename=candidate.attachment_filename,
        attachment_index=candidate.attachment_index,
    )


def _normalize_candidate(
    signal_type: FinancialSignalType,
    raw_value: str,
) -> str | None:
    if signal_type == "routing_number":
        digits = re.sub(r"\D+", "", raw_value)
        return digits if len(digits) == 9 else None
    if signal_type == "swift_bic_code":
        normalized = re.sub(r"\s+", "", raw_value).upper()
        return normalized if normalized.isalnum() and len(normalized) in {8, 11} else None
    if signal_type == "iban":
        normalized = re.sub(r"[\s-]+", "", raw_value).upper()
        if not normalized.isalnum() or not 5 <= len(normalized) <= 34:
            return None
        if not re.match(r"^[A-Z]{2}[0-9A-Z]+$", normalized):
            return None
        return normalized
    if signal_type == "account_number":
        digits = re.sub(r"\D+", "", raw_value).lstrip("0")
        return digits if digits else None
    if signal_type == "payment_portal_url":
        return _normalize_host(raw_value)
    return None


def _normalize_host(value: str) -> str | None:
    candidate = value.strip().rstrip(".,;:")
    if not candidate:
        return None
    parsed = urlsplit(candidate if "://" in candidate else f"//{candidate}")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host or "." not in host:
        return None
    return host


def _redact(signal_type: FinancialSignalType, normalized_value: str) -> str:
    if signal_type in ("routing_number", "account_number"):
        return f"***{normalized_value[-4:]}"
    if signal_type == "iban":
        if len(normalized_value) <= 8:
            return f"{normalized_value[:2]}...{normalized_value[-2:]}"
        return f"{normalized_value[:4]}...{normalized_value[-4:]}"
    if signal_type == "swift_bic_code":
        return f"{normalized_value[:4]}..."
    if signal_type == "payment_portal_url":
        return normalized_value
    return "***"


def _has_payment_context(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 80) : min(len(text), end + 80)]
    return _PAYMENT_CONTEXT_RE.search(window) is not None


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
    "DeltaTripwireFinding",
    "ExtractedFinancialSignal",
    "FinancialSignalType",
    "FinancialStateLedgerAssessment",
    "SignalSource",
    "assess_financial_state_delta",
]
