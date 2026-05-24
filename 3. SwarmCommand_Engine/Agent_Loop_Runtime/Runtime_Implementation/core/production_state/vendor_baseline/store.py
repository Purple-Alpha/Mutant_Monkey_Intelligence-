"""Per-tenant Vendor Baseline Store.

Implements `Vendor_Baseline_Store_Deep_Dive.md` §5: a hash-only,
TTL-bounded SQLite baseline for vendor signals.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from core.blackboard import GovernanceError, VendorBaselineAuditPayload
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import RouteContext, submit_vendor_baseline_audit
from core.policy.signing import default_signing_key
from core.production_state.tenant_overrides import resolve_effective_parameters

from .isolation import leased_connection, tenant_database_path as _tenant_database_path


SignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
    "pdf_producer_fingerprint",
    "vendor_send_time_window",
]
SignalState = Literal["new", "known", "expired"]

SIGNAL_TYPES: frozenset[str] = frozenset(
    {
        "routing_number",
        "swift_bic_code",
        "iban",
        "account_number",
        "payment_portal_url",
        "pdf_producer_fingerprint",
        "vendor_send_time_window",
    }
)
DEFAULT_TTL_DAYS = 90
VENDOR_BASELINE_AGENT_ID = "vendor_baseline_001"


class BaselineSignalTypeError(GovernanceError):
    """Raised when a caller supplies a non-closed-enum signal type."""


class BaselineNormalisationError(GovernanceError):
    """Raised when a raw signal cannot be normalized for its signal type."""


@dataclass(frozen=True)
class BaselineSignalRecord:
    vendor_domain: str
    signal_type: SignalType
    signal_hash: str
    first_seen_at: datetime
    last_seen_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class SignalLookupResult:
    state: SignalState
    record: BaselineSignalRecord | None


def ingest_signal(
    *,
    tenant_id: str,
    vendor_domain: str,
    signal_type: SignalType,
    raw_value: str,
    now: datetime,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> BaselineSignalRecord:
    root = Path(".")
    _check_kill_switch(root)
    timestamp = _require_aware_datetime(now)
    resolved_ttl_days = _effective_ttl_days(
        blackboard_root=root,
        tenant_id=tenant_id,
        explicit_ttl_days=ttl_days,
        now=timestamp,
    )
    signal = _require_signal_type(signal_type)
    vendor = _normalize_vendor_domain(vendor_domain)
    normalized = _normalize_signal_value(signal, raw_value)
    digest = _signal_hash(
        tenant_id=tenant_id,
        signal_type=signal,
        normalized_value=normalized,
    )
    expires_at = timestamp + timedelta(days=resolved_ttl_days)

    with leased_connection(tenant_id, blackboard_root=root) as conn:
        _ensure_schema(conn)
        existing = _fetch_record(
            conn,
            vendor_domain=vendor,
            signal_type=signal,
            signal_hash=digest,
        )
        if existing is None:
            record = BaselineSignalRecord(
                vendor_domain=vendor,
                signal_type=signal,
                signal_hash=digest,
                first_seen_at=timestamp,
                last_seen_at=timestamp,
                expires_at=expires_at,
            )
            conn.execute(
                """
                INSERT INTO vendor_baseline_signals
                    (vendor_domain, signal_type, signal_hash, first_seen_at, last_seen_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                _record_to_row(record),
            )
        else:
            record = BaselineSignalRecord(
                vendor_domain=existing.vendor_domain,
                signal_type=existing.signal_type,
                signal_hash=existing.signal_hash,
                first_seen_at=existing.first_seen_at,
                last_seen_at=timestamp,
                expires_at=expires_at,
            )
            conn.execute(
                """
                UPDATE vendor_baseline_signals
                SET last_seen_at = ?, expires_at = ?
                WHERE vendor_domain = ? AND signal_type = ? AND signal_hash = ?
                """,
                (
                    _datetime_to_iso(record.last_seen_at),
                    _datetime_to_iso(record.expires_at),
                    record.vendor_domain,
                    record.signal_type,
                    record.signal_hash,
                ),
            )
        conn.commit()

    _append_audit(
        blackboard_root=root,
        tenant_id=tenant_id,
        payload=VendorBaselineAuditPayload(
            event_type="vendor_baseline_signal_ingested",
            vendor_domain=vendor,
            signal_type=signal,
            signal_hash=digest,
            rows_affected=1,
            reason="vendor baseline signal ingested",
        ),
    )
    return record


def check_signal(
    *,
    tenant_id: str,
    vendor_domain: str,
    signal_type: SignalType,
    raw_value: str,
    now: datetime,
) -> SignalLookupResult:
    root = Path(".")
    _check_kill_switch(root)
    timestamp = _require_aware_datetime(now)
    signal = _require_signal_type(signal_type)
    vendor = _normalize_vendor_domain(vendor_domain)
    try:
        normalized = _normalize_signal_value(signal, raw_value)
    except BaselineNormalisationError:
        return SignalLookupResult(state="new", record=None)
    digest = _signal_hash(
        tenant_id=tenant_id,
        signal_type=signal,
        normalized_value=normalized,
    )

    with leased_connection(tenant_id, blackboard_root=root) as conn:
        _ensure_schema(conn)
        record = _fetch_record(
            conn,
            vendor_domain=vendor,
            signal_type=signal,
            signal_hash=digest,
        )
    if record is None:
        return SignalLookupResult(state="new", record=None)
    if record.expires_at <= timestamp:
        return SignalLookupResult(state="expired", record=record)
    return SignalLookupResult(state="known", record=record)


def expire_stale_signals(
    *,
    tenant_id: str,
    now: datetime,
) -> int:
    root = Path(".")
    _check_kill_switch(root)
    timestamp = _require_aware_datetime(now)
    with leased_connection(tenant_id, blackboard_root=root) as conn:
        _ensure_schema(conn)
        cursor = conn.execute(
            "DELETE FROM vendor_baseline_signals WHERE expires_at <= ?",
            (_datetime_to_iso(timestamp),),
        )
        deleted = cursor.rowcount if cursor.rowcount is not None else 0
        conn.commit()

    _append_audit(
        blackboard_root=root,
        tenant_id=tenant_id,
        payload=VendorBaselineAuditPayload(
            event_type="vendor_baseline_cleanup",
            rows_affected=deleted,
            reason="expired vendor baseline signals removed",
        ),
    )
    return deleted


def tenant_database_path(tenant_id: str) -> Path:
    return _tenant_database_path(tenant_id, blackboard_root=Path("."))


def _normalize_signal_value(signal_type: SignalType, raw_value: str) -> str:
    signal = _require_signal_type(signal_type)
    if not isinstance(raw_value, str):
        raise BaselineNormalisationError("raw_value must be a string")
    if signal == "routing_number":
        digits = re.sub(r"\D+", "", raw_value)
        if len(digits) != 9:
            raise BaselineNormalisationError("routing_number must normalize to 9 digits")
        return digits
    if signal == "swift_bic_code":
        normalized = re.sub(r"\s+", "", raw_value).upper()
        if not normalized.isalnum() or len(normalized) not in {8, 11}:
            raise BaselineNormalisationError(
                "swift_bic_code must normalize to 8 or 11 alphanumeric characters"
            )
        return normalized
    if signal == "iban":
        normalized = re.sub(r"\s+", "", raw_value).upper()
        if not normalized.isalnum() or not 5 <= len(normalized) <= 34:
            raise BaselineNormalisationError(
                "iban must normalize to 5-34 alphanumeric characters"
            )
        return normalized
    if signal == "account_number":
        digits = re.sub(r"\D+", "", raw_value).lstrip("0")
        if not digits:
            raise BaselineNormalisationError("account_number must contain digits")
        return digits
    if signal == "payment_portal_url":
        return _normalize_host(raw_value)
    if signal == "pdf_producer_fingerprint":
        normalized = re.sub(r"\s+", " ", raw_value).strip().lower()
        if not normalized:
            raise BaselineNormalisationError("pdf_producer_fingerprint cannot be empty")
        return normalized
    if signal == "vendor_send_time_window":
        try:
            hour = int(raw_value)
        except ValueError as exc:
            raise BaselineNormalisationError(
                "vendor_send_time_window must be an integer hour"
            ) from exc
        if hour < 0 or hour > 23:
            raise BaselineNormalisationError(
                "vendor_send_time_window must be between 0 and 23"
            )
        return f"{hour:02d}"
    raise BaselineSignalTypeError(f"unsupported signal_type: {signal_type!r}")


def _signal_hash(*, tenant_id: str, signal_type: SignalType, normalized_value: str) -> str:
    signal = _require_signal_type(signal_type)
    salt = _salt_for_tenant(tenant_id)
    material = salt + signal.encode("utf-8") + b"::" + normalized_value.encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _hashes_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def _salt_for_tenant(tenant_id: str) -> bytes:
    ikm = default_signing_key().secret
    info = f"vendor_baseline_v1::{tenant_id}".encode("utf-8")
    prk = hmac.new(b"", ikm, hashlib.sha256).digest()
    okm = b""
    previous = b""
    counter = 1
    while len(okm) < 32:
        previous = hmac.new(prk, previous + info + bytes([counter]), hashlib.sha256).digest()
        okm += previous
        counter += 1
    return okm[:32]


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS vendor_baseline_signals (
            vendor_domain    TEXT NOT NULL,
            signal_type      TEXT NOT NULL,
            signal_hash      TEXT NOT NULL,
            first_seen_at    TEXT NOT NULL,
            last_seen_at     TEXT NOT NULL,
            expires_at       TEXT NOT NULL,
            PRIMARY KEY (vendor_domain, signal_type, signal_hash),
            CHECK (signal_type IN (
                'routing_number',
                'swift_bic_code',
                'iban',
                'account_number',
                'payment_portal_url',
                'pdf_producer_fingerprint',
                'vendor_send_time_window'
            )),
            CHECK (length(signal_hash) = 64),
            CHECK (length(vendor_domain) > 0),
            CHECK (datetime(first_seen_at) IS NOT NULL),
            CHECK (datetime(last_seen_at)  IS NOT NULL),
            CHECK (datetime(expires_at)    IS NOT NULL)
        ) WITHOUT ROWID;

        CREATE INDEX IF NOT EXISTS idx_vendor_signals_lookup
            ON vendor_baseline_signals (vendor_domain, signal_type);

        CREATE INDEX IF NOT EXISTS idx_vendor_signals_expiry
            ON vendor_baseline_signals (expires_at);
        """
    )


def _fetch_record(
    conn: sqlite3.Connection,
    *,
    vendor_domain: str,
    signal_type: SignalType,
    signal_hash: str,
) -> BaselineSignalRecord | None:
    cursor = conn.execute(
        """
        SELECT vendor_domain, signal_type, signal_hash, first_seen_at, last_seen_at, expires_at
        FROM vendor_baseline_signals
        WHERE vendor_domain = ? AND signal_type = ?
        """,
        (vendor_domain, signal_type),
    )
    for row in cursor.fetchall():
        if _hashes_equal(row[2], signal_hash):
            return _row_to_record(row)
    return None


def _row_to_record(row: tuple[str, str, str, str, str, str]) -> BaselineSignalRecord:
    return BaselineSignalRecord(
        vendor_domain=row[0],
        signal_type=_require_signal_type(row[1]),
        signal_hash=row[2],
        first_seen_at=_parse_iso_datetime(row[3]),
        last_seen_at=_parse_iso_datetime(row[4]),
        expires_at=_parse_iso_datetime(row[5]),
    )


def _record_to_row(record: BaselineSignalRecord) -> tuple[str, str, str, str, str, str]:
    return (
        record.vendor_domain,
        record.signal_type,
        record.signal_hash,
        _datetime_to_iso(record.first_seen_at),
        _datetime_to_iso(record.last_seen_at),
        _datetime_to_iso(record.expires_at),
    )


def _append_audit(
    *,
    blackboard_root: Path,
    tenant_id: str,
    payload: VendorBaselineAuditPayload,
) -> None:
    context = RouteContext(blackboard_root=blackboard_root)
    submit_vendor_baseline_audit(
        context,
        tenant_id=tenant_id,
        source_agent=VENDOR_BASELINE_AGENT_ID,
        payload=payload,
        workflow_id="vendor_baseline_store",
    )


def _effective_ttl_days(
    *,
    blackboard_root: Path,
    tenant_id: str,
    explicit_ttl_days: int,
    now: datetime,
) -> int:
    _validate_ttl_days(explicit_ttl_days)
    effective = resolve_effective_parameters(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        policy_parameters={"vendor_baseline_ttl_days": explicit_ttl_days},
        now=now,
    )
    value = effective.get("vendor_baseline_ttl_days", explicit_ttl_days)
    if isinstance(value, bool) or not isinstance(value, int):
        raise GovernanceError("vendor_baseline_ttl_days must be an int")
    _validate_ttl_days(value)
    return value


def _validate_ttl_days(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GovernanceError("vendor_baseline_ttl_days must be an int")
    if value < 30 or value > 365:
        raise GovernanceError("vendor_baseline_ttl_days must be between 30 and 365")


def _check_kill_switch(blackboard_root: Path) -> None:
    state = is_kill_switch_engaged(blackboard_root, scope="PRODUCTION")
    if state is not None:
        raise KillSwitchEngaged(state)


def _require_signal_type(raw: str) -> SignalType:
    if raw not in SIGNAL_TYPES:
        raise BaselineSignalTypeError(f"unsupported signal_type: {raw!r}")
    return raw  # type: ignore[return-value]


def _normalize_vendor_domain(value: str) -> str:
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


def _normalize_host(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise BaselineNormalisationError("payment_portal_url cannot be empty")
    parsed = urlsplit(candidate if "://" in candidate else f"//{candidate}")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise BaselineNormalisationError("payment_portal_url must contain a host")
    return host


def _require_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise GovernanceError("datetime values must be timezone-aware")
    return value.astimezone(timezone.utc)


def _datetime_to_iso(value: datetime) -> str:
    return _require_aware_datetime(value).isoformat()


def _parse_iso_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

