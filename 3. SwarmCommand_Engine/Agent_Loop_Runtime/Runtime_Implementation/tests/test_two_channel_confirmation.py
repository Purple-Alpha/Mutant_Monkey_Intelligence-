from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.blackboard import (
    Environment,
    GovernanceError,
    RecordType,
    TwoChannelConfirmationPayload,
    read_records,
)
from core.blackboard.models import PAYLOAD_MODELS
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.orchestrator.routes import blackboard_path
from core.workflows import (
    ConfirmationRecord,
    list_pending_confirmations,
    record_confirmation_outcome,
    record_confirmation_request,
    summarize_confirmation_status,
)
from core.workflows import two_channel_confirmation as tcc


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


def _request(
    *,
    tenant_id: str = TENANT,
    finding_id: str = "fsl:abc.example:routing:hash1",
    detector: str = "financial_state_ledger",
    risk_floor: int = 85,
    requested_by: str = "operator_a",
    requested_at: datetime | None = None,
) -> ConfirmationRecord:
    return record_confirmation_request(
        tenant_id=tenant_id,
        finding_id=finding_id,
        detector=detector,
        risk_floor=risk_floor,
        requested_by=requested_by,
        requested_at=requested_at or _now(),
    )


# ---------------------------------------------------------------------------
# Gate test 1: public API surface
# ---------------------------------------------------------------------------


def test_public_api_surface_is_locked() -> None:
    assert set(tcc.__all__) == {
        "ConfirmationRecord",
        "list_pending_confirmations",
        "record_confirmation_outcome",
        "record_confirmation_request",
        "summarize_confirmation_status",
    }
    assert ConfirmationRecord.__dataclass_params__.frozen


def test_record_type_registered_in_payload_models() -> None:
    assert RecordType.TWO_CHANNEL_CONFIRMATION in PAYLOAD_MODELS
    assert PAYLOAD_MODELS[RecordType.TWO_CHANNEL_CONFIRMATION] is TwoChannelConfirmationPayload


# ---------------------------------------------------------------------------
# Gate tests 2-6: record_confirmation_request
# ---------------------------------------------------------------------------


def test_record_confirmation_request_writes_one_pending_event(tmp_path) -> None:
    record = _request()

    assert record.outcome_status is None
    path = blackboard_path(_root(tmp_path), Environment.PRODUCTION, TENANT)
    records = [
        r for r in read_records(path)
        if r.record_type == RecordType.TWO_CHANNEL_CONFIRMATION
    ]
    assert len(records) == 1
    assert records[0].payload["event_type"] == "pending"
    assert records[0].payload["finding_id"] == record.finding_id
    assert records[0].payload["risk_floor"] == 85


def test_record_confirmation_request_rejects_duplicate_finding_id() -> None:
    _request()
    with pytest.raises(GovernanceError):
        _request()


@pytest.mark.parametrize(
    "finding_id",
    ["", "bad id with space", "bad/slash", "bad\\backslash", "..", "a" * 200],
)
def test_record_confirmation_request_rejects_invalid_finding_id(finding_id: str) -> None:
    with pytest.raises(GovernanceError):
        record_confirmation_request(
            tenant_id=TENANT,
            finding_id=finding_id,
            detector="financial_state_ledger",
            risk_floor=85,
            requested_by="operator_a",
            requested_at=_now(),
        )


def test_record_confirmation_request_rejects_zero_risk_floor() -> None:
    """Explicit gate test: risk_floor=0 is below the [1, 100] band and must raise."""

    with pytest.raises(GovernanceError):
        record_confirmation_request(
            tenant_id=TENANT,
            finding_id="fsl:zero:1",
            detector="financial_state_ledger",
            risk_floor=0,
            requested_by="operator_a",
            requested_at=_now(),
        )


@pytest.mark.parametrize("risk_floor", [-1, 101, 200, True])
def test_record_confirmation_request_rejects_out_of_range_risk_floor(risk_floor) -> None:
    with pytest.raises(GovernanceError):
        record_confirmation_request(
            tenant_id=TENANT,
            finding_id="fsl:bad:1",
            detector="financial_state_ledger",
            risk_floor=risk_floor,
            requested_by="operator_a",
            requested_at=_now(),
        )


def test_record_confirmation_request_kill_switch_blocks(tmp_path) -> None:
    engage_kill_switch(
        _root(tmp_path),
        scope="PRODUCTION_ONLY",
        reason="halt",
        operator="matt",
    )
    with pytest.raises(KillSwitchEngaged):
        _request()


def test_record_confirmation_request_naive_datetime_rejected() -> None:
    with pytest.raises(GovernanceError):
        record_confirmation_request(
            tenant_id=TENANT,
            finding_id="fsl:naive:1",
            detector="financial_state_ledger",
            risk_floor=85,
            requested_by="operator_a",
            requested_at=datetime(2026, 5, 24, 12, 0),
        )


# ---------------------------------------------------------------------------
# Gate tests 7-13: record_confirmation_outcome
# ---------------------------------------------------------------------------


def test_record_confirmation_outcome_writes_one_outcome_event(tmp_path) -> None:
    pending = _request()
    record = record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="previously_known_phone",
        channel_description="Matt's personal mobile from 2024 onboarding",
    )

    assert record.outcome_status == "confirmed"
    assert record.channel_kind == "previously_known_phone"
    assert record.detector == pending.detector

    path = blackboard_path(_root(tmp_path), Environment.PRODUCTION, TENANT)
    payloads = [
        r.payload for r in read_records(path)
        if r.record_type == RecordType.TWO_CHANNEL_CONFIRMATION
    ]
    assert len(payloads) == 2
    assert [p["event_type"] for p in payloads] == ["pending", "outcome"]


def test_outcome_requires_prior_pending() -> None:
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id="fsl:nope:1",
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=_now(),
            channel_kind="previously_known_phone",
        )


def test_outcome_rejects_second_outcome() -> None:
    pending = _request()
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="rejected",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
    )
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_c",
            outcome_at=_now() + timedelta(hours=2),
            channel_kind="previously_known_phone",
        )


def test_outcome_confirmed_requires_channel_kind() -> None:
    pending = _request()
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=_now() + timedelta(hours=1),
        )


def test_outcome_other_documented_requires_reason() -> None:
    pending = _request()
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=_now() + timedelta(hours=1),
            channel_kind="other_documented",
        )


def test_outcome_other_documented_with_reason_accepted() -> None:
    pending = _request()
    record = record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="other_documented",
        reason="Verified via secure internal procurement chat history.",
    )
    assert record.channel_kind == "other_documented"
    assert record.reason


def test_outcome_at_before_requested_at_rejected() -> None:
    pending = _request(requested_at=_now())
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=_now() - timedelta(hours=1),
            channel_kind="previously_known_phone",
        )


# ---------------------------------------------------------------------------
# Timezone-edge-case pinning (Grok approve-with-notes follow-up)
#
# `_require_aware_datetime` and `_parse_payload_datetime` both convert to UTC
# before the `outcome_at < requested_at` comparison runs. The following tests
# pin that invariant against the specific TZ-handling concerns Grok flagged:
# different timezones representing the same UTC instant, wall-clock-later but
# UTC-earlier timestamps, equality, and sub-second ordering across zones.
# ---------------------------------------------------------------------------


_PDT = timezone(timedelta(hours=-7))
_EST = timezone(timedelta(hours=-5))
_JST = timezone(timedelta(hours=+9))
_NEPAL = timezone(timedelta(hours=+5, minutes=45))


def test_outcome_at_in_different_timezone_same_utc_instant_accepted() -> None:
    """outcome_at in a different named timezone but representing the same
    UTC instant as requested_at is accepted (the comparison is on UTC
    instants, not wall-clock times)."""

    pending = _request(
        finding_id="fsl:tz:same-instant",
        requested_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
    )
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=datetime(2026, 5, 24, 5, 0, tzinfo=_PDT),
        channel_kind="previously_known_phone",
    )


def test_outcome_at_wall_clock_later_but_utc_earlier_rejected() -> None:
    """outcome_at whose wall-clock LOOKS later (20:00 JST) but whose UTC
    instant is EARLIER (11:00 UTC) than the recorded requested_at
    (12:00 UTC) must still be rejected by the < requested_at rule."""

    pending = _request(
        finding_id="fsl:tz:wall-later-utc-earlier",
        requested_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=datetime(2026, 5, 24, 20, 0, tzinfo=_JST),
            channel_kind="previously_known_phone",
        )


def test_outcome_at_wall_clock_earlier_but_utc_later_accepted() -> None:
    """outcome_at whose wall-clock LOOKS earlier (08:00 EST) but whose UTC
    instant is LATER (13:00 UTC) than the recorded requested_at
    (12:00 UTC) is accepted, because the comparison is on UTC instants."""

    pending = _request(
        finding_id="fsl:tz:wall-earlier-utc-later",
        requested_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
    )
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=datetime(2026, 5, 24, 8, 0, tzinfo=_EST),
        channel_kind="previously_known_phone",
    )


def test_outcome_at_equal_to_requested_at_in_utc_accepted() -> None:
    """Equality is accepted: only strictly-less-than triggers the rule."""

    pending = _request(
        finding_id="fsl:tz:equal",
        requested_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
    )
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        channel_kind="previously_known_phone",
    )


def test_outcome_at_microsecond_earlier_in_utc_rejected_even_in_other_zone() -> None:
    """A 1-microsecond-earlier UTC instant expressed in any timezone is still
    rejected. Pins ordering precision below seconds."""

    pending = _request(
        finding_id="fsl:tz:microsecond",
        requested_at=datetime(2026, 5, 24, 12, 0, 0, 500_000, tzinfo=timezone.utc),
    )
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=datetime(2026, 5, 24, 12, 0, 0, 499_999, tzinfo=_NEPAL),
            channel_kind="previously_known_phone",
        )


def test_outcome_at_dst_aware_zone_handled_via_utc_instant() -> None:
    """Even across a DST boundary the comparison runs on UTC instants. The
    requested_at is recorded just before US DST ends on 2026-11-01 02:00
    local; the outcome_at is recorded in EST (UTC-5, post-DST) but its UTC
    instant is later, so it must be accepted."""

    pre_dst_pdt = timezone(timedelta(hours=-7))
    post_dst_pst = timezone(timedelta(hours=-8))
    pending = _request(
        finding_id="fsl:tz:dst-boundary",
        requested_at=datetime(2026, 11, 1, 1, 30, tzinfo=pre_dst_pdt),
    )
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=datetime(2026, 11, 1, 2, 30, tzinfo=post_dst_pst),
        channel_kind="previously_known_phone",
    )


def test_outcome_at_naive_datetime_rejected_even_when_value_would_be_later() -> None:
    """A naive datetime (no tzinfo) is rejected regardless of its numeric
    value - the policy is `aware or reject`, not `try to interpret`."""

    pending = _request(
        finding_id="fsl:tz:naive",
        requested_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="confirmed",
            outcome_by="operator_b",
            outcome_at=datetime(2030, 1, 1, 0, 0),
            channel_kind="previously_known_phone",
        )


def test_outcome_kill_switch_blocks(tmp_path) -> None:
    pending = _request()
    engage_kill_switch(
        _root(tmp_path),
        scope="PRODUCTION_ONLY",
        reason="halt",
        operator="matt",
    )
    with pytest.raises(KillSwitchEngaged):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="rejected",
            outcome_by="operator_b",
            outcome_at=_now() + timedelta(hours=1),
        )


@pytest.mark.parametrize(
    "status", ["confirmed", "rejected", "unable_to_verify", "expired"]
)
def test_outcome_status_closed_enum(status: str) -> None:
    pending = _request()
    record = record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status=status,  # type: ignore[arg-type]
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="previously_known_phone" if status == "confirmed" else None,
    )
    assert record.outcome_status == status


def test_outcome_bad_status_raises() -> None:
    pending = _request()
    with pytest.raises(GovernanceError):
        record_confirmation_outcome(
            tenant_id=TENANT,
            finding_id=pending.finding_id,
            outcome_status="bogus",  # type: ignore[arg-type]
            outcome_by="operator_b",
            outcome_at=_now() + timedelta(hours=1),
        )


# ---------------------------------------------------------------------------
# Gate tests 14-15: list_pending_confirmations
# ---------------------------------------------------------------------------


def test_list_pending_confirmations_excludes_resolved_findings() -> None:
    a = _request(finding_id="fsl:a:1", requested_at=_now())
    b = _request(finding_id="fsl:b:1", requested_at=_now() + timedelta(minutes=1))
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=a.finding_id,
        outcome_status="rejected",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
    )
    pendings = list_pending_confirmations(tenant_id=TENANT)
    assert [p.finding_id for p in pendings] == [b.finding_id]


def test_list_pending_confirmations_sorted_by_requested_at() -> None:
    _request(finding_id="fsl:later:1", requested_at=_now() + timedelta(minutes=10))
    _request(finding_id="fsl:earlier:1", requested_at=_now())
    pendings = list_pending_confirmations(tenant_id=TENANT)
    assert [p.finding_id for p in pendings] == ["fsl:earlier:1", "fsl:later:1"]


def test_list_pending_confirmations_filters_by_tenant() -> None:
    _request(tenant_id="tenant_a", finding_id="fsl:a:1")
    _request(tenant_id="tenant_b", finding_id="fsl:b:1")
    pendings_a = list_pending_confirmations(tenant_id="tenant_a")
    pendings_b = list_pending_confirmations(tenant_id="tenant_b")
    assert {p.finding_id for p in pendings_a} == {"fsl:a:1"}
    assert {p.finding_id for p in pendings_b} == {"fsl:b:1"}


# ---------------------------------------------------------------------------
# Gate tests 16-17: summarize_confirmation_status
# ---------------------------------------------------------------------------


def test_summarize_returns_none_for_unknown_finding() -> None:
    assert summarize_confirmation_status(tenant_id=TENANT, finding_id="fsl:none:1") is None


def test_summarize_returns_pending_then_outcome() -> None:
    pending = _request()
    summary = summarize_confirmation_status(tenant_id=TENANT, finding_id=pending.finding_id)
    assert summary is not None
    assert summary.outcome_status is None

    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="previously_known_phone",
    )
    summary = summarize_confirmation_status(tenant_id=TENANT, finding_id=pending.finding_id)
    assert summary is not None
    assert summary.outcome_status == "confirmed"
    assert summary.requested_by == pending.requested_by


# ---------------------------------------------------------------------------
# Gate tests 18-19: lift-only and data-minimization
# ---------------------------------------------------------------------------


def test_confirmed_outcome_does_not_change_risk_floor(tmp_path) -> None:
    pending = _request(risk_floor=85)
    record = record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=pending.finding_id,
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="previously_known_phone",
    )
    assert record.risk_floor == 85
    summary = summarize_confirmation_status(
        tenant_id=TENANT, finding_id=pending.finding_id
    )
    assert summary is not None
    assert summary.risk_floor == 85


def test_list_pending_confirmations_preserves_risk_floor_before_outcome() -> None:
    _request(finding_id="fsl:lift:1", risk_floor=85, requested_at=_now())
    pendings = list_pending_confirmations(tenant_id=TENANT)
    assert len(pendings) == 1
    assert pendings[0].risk_floor == 85
    assert pendings[0].outcome_status is None


def test_no_raw_finding_content_in_payload(tmp_path) -> None:
    _request(
        finding_id="fsl:acme.example:routing:abcdef1234",
        detector="financial_state_ledger",
    )
    record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id="fsl:acme.example:routing:abcdef1234",
        outcome_status="confirmed",
        outcome_by="operator_b",
        outcome_at=_now() + timedelta(hours=1),
        channel_kind="previously_known_phone",
        channel_description="Verified via known phone from onboarding doc",
    )
    path = blackboard_path(_root(tmp_path), Environment.PRODUCTION, TENANT)
    payloads = [
        r.payload for r in read_records(path)
        if r.record_type == RecordType.TWO_CHANNEL_CONFIRMATION
    ]
    serialized = str(payloads)
    for forbidden in ("123456789", "routing_number 123", "@acme.example", "wire transfer"):
        assert forbidden not in serialized


# ---------------------------------------------------------------------------
# Gate test 20: scoring agent does not import this workflow (lift-only)
# ---------------------------------------------------------------------------


def test_scoring_agent_does_not_import_two_channel_confirmation() -> None:
    workspace_root = Path(__file__).resolve().parents[1]
    scoring_path = workspace_root / "core" / "scoring" / "email_risk_scoring_agent.py"
    source = scoring_path.read_text(encoding="utf-8")
    assert "two_channel_confirmation" not in source
    assert "from core.workflows" not in source


# ---------------------------------------------------------------------------
# Gate test 21: audit target
# ---------------------------------------------------------------------------


def test_grok_audit_runner_has_two_channel_confirmation_target() -> None:
    workspace_root = Path(__file__).resolve().parents[4]
    runner_path = workspace_root / "audit_tools" / "grok_audit_runner.py"
    spec = importlib.util.spec_from_file_location("grok_audit_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["grok_audit_runner"] = module
    spec.loader.exec_module(module)

    package = module.AUDIT_PACKAGES["two_channel_confirmation"]
    assert package.name == "two_channel_confirmation"
    assert any(
        "Two_Channel_Confirmation_Enforcement_Deep_Dive.md" in file.relative_path
        for file in package.files
    )
    assert any(
        "two_channel_confirmation.py" in file.relative_path for file in package.files
    )
