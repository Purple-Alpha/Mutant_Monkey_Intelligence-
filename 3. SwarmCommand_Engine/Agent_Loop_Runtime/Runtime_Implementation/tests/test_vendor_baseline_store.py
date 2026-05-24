from __future__ import annotations

import inspect
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.blackboard import Environment, GovernanceError, RecordType, read_records
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.orchestrator.routes import blackboard_path
from core.production_state import create_or_update_tenant_override
from core.production_state.vendor_baseline import (
    check_signal,
    expire_stale_signals,
    ingest_signal,
    tenant_database_path,
)
from core.production_state.vendor_baseline import store as vendor_baseline_store
from core.production_state.vendor_baseline.store import (
    BaselineNormalisationError,
    BaselineSignalTypeError,
    _hashes_equal,
    _normalize_signal_value,
)


TENANT = "tenant_demo"


def _root(tmp_path: Path) -> Path:
    return tmp_path / "blackboard"


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = _root(tmp_path)
    root.mkdir()
    monkeypatch.chdir(root)


def _now() -> datetime:
    return datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def test_tenant_database_path_resolves_under_per_tenant_directory(tmp_path):
    assert tenant_database_path(TENANT) == (
        Path("production_state") / TENANT / "vendor_baseline.sqlite"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX mode check is Linux/Unix only")
def test_file_creation_permissions_linux(tmp_path):
    record = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123-456-789",
        now=_now(),
    )

    path = tenant_database_path(TENANT)
    assert record.signal_hash
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700


@pytest.mark.skipif(sys.platform != "win32", reason="NTFS DACL check is Windows only")
def test_file_creation_permissions_windows_dacl(tmp_path):
    import ntsecuritycon as con
    import win32api
    import win32security

    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )

    path = tenant_database_path(TENANT)
    sd = win32security.GetNamedSecurityInfo(
        str(path),
        win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION,
    )
    dacl = sd.GetSecurityDescriptorDacl()
    user_sid, _, _ = win32security.LookupAccountName(None, win32api.GetUserName())
    system_sid = win32security.CreateWellKnownSid(win32security.WinLocalSystemSid, None)
    administrators_sid = win32security.CreateWellKnownSid(
        win32security.WinBuiltinAdministratorsSid,
        None,
    )

    assert dacl is not None
    assert dacl.GetAceCount() == 1
    ace = dacl.GetAce(0)
    ace_type, ace_flags = ace[0]
    ace_mask = ace[1]
    ace_sid = ace[2]
    assert ace_type == win32security.ACCESS_ALLOWED_ACE_TYPE
    assert ace_flags & win32security.INHERITED_ACE == 0
    assert ace_mask == (con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE)
    assert ace_sid == user_sid
    assert ace_sid != system_sid
    assert ace_sid != administrators_sid


def test_cross_tenant_files_and_salts_are_separate(tmp_path):
    a = ingest_signal(
        tenant_id="tenant_a",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    b = ingest_signal(
        tenant_id="tenant_b",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )

    assert tenant_database_path("tenant_a") != tenant_database_path("tenant_b")
    assert a.signal_hash != b.signal_hash


def test_vendor_domain_is_validated_but_not_coerced_to_last_two_labels(tmp_path):
    record = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="billing.vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )

    assert record.vendor_domain == "billing.vendor.example"
    with pytest.raises(GovernanceError):
        ingest_signal(
            tenant_id=TENANT,
            vendor_domain="Billing.Vendor.Example",
            signal_type="routing_number",
            raw_value="123456789",
            now=_now(),
        )


def test_closed_enum_rejection_writes_nothing(tmp_path):
    with pytest.raises(BaselineSignalTypeError):
        ingest_signal(
            tenant_id=TENANT,
            vendor_domain="vendor.example",
            signal_type="bogus",  # type: ignore[arg-type]
            raw_value="123456789",
            now=_now(),
        )

    assert not tenant_database_path(TENANT).exists()


def test_routing_number_normalisation_and_rejection(tmp_path):
    first = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123-456-789",
        now=_now(),
    )
    second = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123 456 789",
        now=_now() + timedelta(hours=1),
    )

    assert first.signal_hash == second.signal_hash
    with pytest.raises(BaselineNormalisationError):
        ingest_signal(
            tenant_id=TENANT,
            vendor_domain="vendor.example",
            signal_type="routing_number",
            raw_value="12345",
            now=_now(),
        )


@pytest.mark.parametrize(
    ("signal_type", "raw_value", "expected"),
    [
        ("swift_bic_code", "abcd us 33 xxx", "ABCDUS33XXX"),
        ("iban", "gb82 west 1234 5698 7654 32", "GB82WEST12345698765432"),
        ("account_number", "000-00123", "123"),
        ("payment_portal_url", "https://Billing.Vendor.com:443/pay?x=1", "billing.vendor.com"),
        ("pdf_producer_fingerprint", " QuickBooks   Commercial ", "quickbooks commercial"),
        ("vendor_send_time_window", "7", "07"),
    ],
)
def test_normalisation_contract_for_each_enum(signal_type, raw_value, expected):
    assert _normalize_signal_value(signal_type, raw_value) == expected


def test_new_known_and_expired_lookup_paths(tmp_path):
    assert (
        check_signal(
            tenant_id=TENANT,
            vendor_domain="vendor.example",
            signal_type="routing_number",
            raw_value="123456789",
            now=_now(),
        ).state
        == "new"
    )
    record = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    known = check_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now() + timedelta(days=1),
    )
    expired = check_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now() + timedelta(days=91),
    )
    path = tenant_database_path(TENANT)

    assert known.state == "known"
    assert known.record == record
    assert expired.state == "expired"
    assert expired.record == record
    with sqlite3.connect(path) as conn:
        row_count = conn.execute("SELECT COUNT(*) FROM vendor_baseline_signals").fetchone()[0]
    assert row_count == 1


def test_reingest_refreshes_last_seen_and_expiry_but_preserves_first_seen(tmp_path):
    first = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    refreshed = ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now() + timedelta(days=2),
    )

    assert refreshed.first_seen_at == first.first_seen_at
    assert refreshed.last_seen_at == _now() + timedelta(days=2)
    assert refreshed.expires_at == _now() + timedelta(days=92)


def test_per_tenant_ttl_override_applies_to_one_tenant_only(tmp_path):
    create_or_update_tenant_override(
        blackboard_root=_root(tmp_path),
        tenant_id="tenant_a",
        parameters={"vendor_baseline_ttl_days": 30},
        reason="short baseline window",
        requested_by="operator_a",
        approved_by="operator_b",
        now=_now(),
    )

    tenant_a = ingest_signal(
        tenant_id="tenant_a",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    tenant_b = ingest_signal(
        tenant_id="tenant_b",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )

    assert tenant_a.expires_at == _now() + timedelta(days=30)
    assert tenant_b.expires_at == _now() + timedelta(days=90)


@pytest.mark.parametrize("value", [0, 29, 366, 1.5, True])
def test_ttl_override_range_enforced_before_persist(tmp_path, value):
    with pytest.raises(GovernanceError):
        create_or_update_tenant_override(
            blackboard_root=_root(tmp_path),
            tenant_id=TENANT,
            parameters={"vendor_baseline_ttl_days": value},
            reason="bad ttl",
            requested_by="operator_a",
            approved_by="operator_b",
            now=_now(),
        )


def test_cleanup_deletes_only_expired_rows_and_writes_one_audit(tmp_path):
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now() - timedelta(days=91),
    )
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="987654321",
        now=_now(),
    )

    assert expire_stale_signals(tenant_id=TENANT, now=_now()) == 1
    records = read_records(blackboard_path(_root(tmp_path), Environment.PRODUCTION, TENANT))
    cleanup = [
        record for record in records
        if record.record_type == RecordType.VENDOR_BASELINE_AUDIT
        and record.payload["event_type"] == "vendor_baseline_cleanup"
    ]
    assert len(cleanup) == 1
    assert cleanup[0].payload["rows_affected"] == 1


@pytest.mark.parametrize("operation", ["ingest", "check", "cleanup"])
def test_kill_switch_blocks_every_entry_point(tmp_path, operation):
    engage_kill_switch(
        _root(tmp_path),
        scope="PRODUCTION_ONLY",
        reason="halt baseline",
        operator="matt",
    )

    with pytest.raises(KillSwitchEngaged):
        if operation == "ingest":
            ingest_signal(
                tenant_id=TENANT,
                vendor_domain="vendor.example",
                signal_type="routing_number",
                raw_value="123456789",
                now=_now(),
            )
        elif operation == "check":
            check_signal(
                tenant_id=TENANT,
                vendor_domain="vendor.example",
                signal_type="routing_number",
                raw_value="123456789",
                now=_now(),
            )
        else:
            expire_stale_signals(tenant_id=TENANT, now=_now())


def test_write_audit_has_no_raw_value_and_reads_write_no_audit(tmp_path):
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    check_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )

    records = read_records(blackboard_path(_root(tmp_path), Environment.PRODUCTION, TENANT))
    audits = [
        record for record in records
        if record.record_type == RecordType.VENDOR_BASELINE_AUDIT
    ]
    assert len(audits) == 1
    payload = audits[0].payload
    assert payload["event_type"] == "vendor_baseline_signal_ingested"
    assert payload["signal_hash"]
    assert "123456789" not in str(payload)


def test_constant_time_hash_compare_helper_uses_hmac_compare_digest():
    source = inspect.getsource(_hashes_equal)
    assert "hmac.compare_digest" in source
    assert _hashes_equal("a" * 64, "a" * 64)
    assert not _hashes_equal("a" * 64, "b" * 64)


def test_lookup_path_uses_constant_time_hash_compare(monkeypatch, tmp_path):
    calls: list[tuple[str, str]] = []
    original = vendor_baseline_store._hashes_equal

    def spy(left: str, right: str) -> bool:
        calls.append((left, right))
        return original(left, right)

    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    monkeypatch.setattr(vendor_baseline_store, "_hashes_equal", spy)

    result = check_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now() + timedelta(days=1),
    )

    assert result.state == "known"
    assert calls


def test_schema_enforces_closed_enum_via_raw_sql(tmp_path):
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=_now(),
    )
    path = tenant_database_path(TENANT)
    with sqlite3.connect(path) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO vendor_baseline_signals
                    (vendor_domain, signal_type, signal_hash, first_seen_at, last_seen_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "vendor.example",
                    "bogus",
                    "a" * 64,
                    _now().isoformat(),
                    _now().isoformat(),
                    (_now() + timedelta(days=1)).isoformat(),
                ),
            )


@pytest.mark.parametrize(
    "tenant_id",
    ["../tenant", "tenant/name", "tenant\\name", " tenant", "tenant\n", ".", ".tenant", "tenant."],
)
def test_path_traversal_hardening_rejects_bad_tenant_ids(tmp_path, tenant_id):
    with pytest.raises(GovernanceError):
        tenant_database_path(tenant_id)

