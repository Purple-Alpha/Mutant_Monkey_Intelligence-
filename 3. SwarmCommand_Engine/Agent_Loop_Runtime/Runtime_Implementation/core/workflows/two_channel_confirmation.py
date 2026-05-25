"""NorthStar Inbox Shield - Two-Channel Confirmation Enforcement v1.

Stage-A workflow / audit layer that converts a deterministic finding which
requires out-of-band verification into an append-only Blackboard audit trail.
No portal, no cryptographic vendor identity, no scoring effect.

See ``4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from core.blackboard import (
    Environment,
    GovernanceError,
    RecordType,
    TwoChannelChannelKind,
    TwoChannelConfirmationPayload,
    TwoChannelEventType,
    TwoChannelOutcomeStatus,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import (
    RouteContext,
    submit_two_channel_confirmation,
)
from core.orchestrator.routes import blackboard_path


_SOURCE_AGENT = "two_channel_confirmation_001"
_FINDING_ID_RE = re.compile(r"^[A-Za-z0-9_\-:.]+$")
_MAX_FINDING_ID_LENGTH = 128
_MAX_TENANT_ID_LENGTH = 128
_MAX_DETECTOR_LENGTH = 128
_MAX_OPERATOR_LENGTH = 128
_MAX_CHANNEL_DESCRIPTION_LENGTH = 256
_MAX_REASON_LENGTH = 512


@dataclass(frozen=True)
class ConfirmationRecord:
    """One vendor-verification confirmation, projected from Blackboard events."""

    finding_id: str
    tenant_id: str
    detector: str
    recommended_action: Literal["needs_review"]
    risk_floor: int
    requested_at: datetime
    requested_by: str
    outcome_at: datetime | None = None
    outcome_by: str | None = None
    outcome_status: TwoChannelOutcomeStatus | None = None
    channel_kind: TwoChannelChannelKind | None = None
    channel_description: str | None = None
    reason: str | None = None


def record_confirmation_request(
    *,
    tenant_id: str,
    finding_id: str,
    detector: str,
    risk_floor: int,
    requested_by: str,
    requested_at: datetime,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord:
    """Append a `pending` two-channel-confirmation event to the Blackboard.

    Raises:
        KillSwitchEngaged: if the production kill switch is engaged.
        GovernanceError: if any argument violates the spec contract or if a
            prior event for this `finding_id` already exists for this tenant.
    """

    root = blackboard_root or Path(".")
    _check_kill_switch(root)
    _validate_tenant_id(tenant_id)
    _validate_finding_id(finding_id)
    _validate_detector(detector)
    _validate_request_risk_floor(risk_floor)
    _validate_operator_label(requested_by, field_name="requested_by")
    requested_at_aware = _require_aware_datetime(requested_at)

    existing = _read_events_for_finding(root, tenant_id, finding_id)
    if existing:
        raise GovernanceError(
            f"two_channel_confirmation: finding_id {finding_id!r} already has "
            "a prior event for this tenant; requests cannot be duplicated"
        )

    payload = TwoChannelConfirmationPayload(
        event_type="pending",
        finding_id=finding_id,
        tenant_id=tenant_id,
        detector=detector,
        recommended_action="needs_review",
        risk_floor=risk_floor,
        requested_at=requested_at_aware,
        requested_by=requested_by,
    )
    submit_two_channel_confirmation(
        RouteContext(blackboard_root=root),
        tenant_id=tenant_id,
        source_agent=_SOURCE_AGENT,
        payload=payload,
    )
    return ConfirmationRecord(
        finding_id=finding_id,
        tenant_id=tenant_id,
        detector=detector,
        recommended_action="needs_review",
        risk_floor=risk_floor,
        requested_at=requested_at_aware,
        requested_by=requested_by,
    )


def record_confirmation_outcome(
    *,
    tenant_id: str,
    finding_id: str,
    outcome_status: TwoChannelOutcomeStatus,
    outcome_by: str,
    outcome_at: datetime,
    channel_kind: TwoChannelChannelKind | None = None,
    channel_description: str | None = None,
    reason: str | None = None,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord:
    """Append an `outcome` two-channel-confirmation event to the Blackboard.

    Raises:
        KillSwitchEngaged: if the production kill switch is engaged.
        GovernanceError: if there is no prior `pending` event, or there is
            already an `outcome` event, or the contract is otherwise violated.
    """

    root = blackboard_root or Path(".")
    _check_kill_switch(root)
    _validate_tenant_id(tenant_id)
    _validate_finding_id(finding_id)
    _validate_outcome_status(outcome_status)
    _validate_operator_label(outcome_by, field_name="outcome_by")
    outcome_at_aware = _require_aware_datetime(outcome_at)

    if outcome_status == "confirmed" and channel_kind is None:
        raise GovernanceError(
            "two_channel_confirmation: outcome_status='confirmed' requires a "
            "channel_kind (which previously-known channel was used)"
        )
    if channel_kind == "other_documented" and not (reason or "").strip():
        raise GovernanceError(
            "two_channel_confirmation: channel_kind='other_documented' "
            "requires a non-empty reason describing the channel"
        )
    if channel_description is not None and len(channel_description) > _MAX_CHANNEL_DESCRIPTION_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: channel_description must be "
            f"<= {_MAX_CHANNEL_DESCRIPTION_LENGTH} characters"
        )
    if reason is not None and len(reason) > _MAX_REASON_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: reason must be <= {_MAX_REASON_LENGTH} characters"
        )

    events = _read_events_for_finding(root, tenant_id, finding_id)
    pending = _first_event(events, "pending")
    if pending is None:
        raise GovernanceError(
            f"two_channel_confirmation: outcome rejected because no prior "
            f"`pending` event exists for finding_id {finding_id!r}"
        )
    if _first_event(events, "outcome") is not None:
        raise GovernanceError(
            f"two_channel_confirmation: outcome rejected because finding_id "
            f"{finding_id!r} already has a recorded outcome"
        )
    requested_at = _parse_payload_datetime(pending.get("requested_at"))
    if outcome_at_aware < requested_at:
        raise GovernanceError(
            "two_channel_confirmation: outcome_at must not be earlier than "
            "the pending requested_at"
        )

    detector = pending["detector"]
    risk_floor = int(pending["risk_floor"])
    payload = TwoChannelConfirmationPayload(
        event_type="outcome",
        finding_id=finding_id,
        tenant_id=tenant_id,
        detector=detector,
        recommended_action="needs_review",
        risk_floor=risk_floor,
        outcome_at=outcome_at_aware,
        outcome_by=outcome_by,
        outcome_status=outcome_status,
        channel_kind=channel_kind,
        channel_description=channel_description,
        reason=reason,
    )
    submit_two_channel_confirmation(
        RouteContext(blackboard_root=root),
        tenant_id=tenant_id,
        source_agent=_SOURCE_AGENT,
        payload=payload,
    )
    return ConfirmationRecord(
        finding_id=finding_id,
        tenant_id=tenant_id,
        detector=detector,
        recommended_action="needs_review",
        risk_floor=risk_floor,
        requested_at=requested_at,
        requested_by=pending["requested_by"],
        outcome_at=outcome_at_aware,
        outcome_by=outcome_by,
        outcome_status=outcome_status,
        channel_kind=channel_kind,
        channel_description=channel_description,
        reason=reason,
    )


def list_pending_confirmations(
    *,
    tenant_id: str,
    blackboard_root: Path | None = None,
) -> tuple[ConfirmationRecord, ...]:
    """Return `pending` requests with no recorded outcome, sorted by requested_at."""

    root = blackboard_root or Path(".")
    _validate_tenant_id(tenant_id)
    pendings: dict[str, dict] = {}
    outcomes: set[str] = set()
    for event in _read_all_events(root, tenant_id):
        finding_id = event["finding_id"]
        if event["event_type"] == "pending":
            pendings.setdefault(finding_id, event)
        elif event["event_type"] == "outcome":
            outcomes.add(finding_id)
    records: list[ConfirmationRecord] = []
    for finding_id, pending in pendings.items():
        if finding_id in outcomes:
            continue
        records.append(_pending_to_record(pending))
    records.sort(key=lambda r: r.requested_at)
    return tuple(records)


def summarize_confirmation_status(
    *,
    tenant_id: str,
    finding_id: str,
    blackboard_root: Path | None = None,
) -> ConfirmationRecord | None:
    """Return the most informative single record for one `finding_id` or None."""

    root = blackboard_root or Path(".")
    _validate_tenant_id(tenant_id)
    _validate_finding_id(finding_id)
    events = _read_events_for_finding(root, tenant_id, finding_id)
    if not events:
        return None
    pending = _first_event(events, "pending")
    outcome = _first_event(events, "outcome")
    if pending is None:
        return None
    if outcome is None:
        return _pending_to_record(pending)
    return _merge_pending_and_outcome(pending, outcome)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _check_kill_switch(blackboard_root: Path) -> None:
    state = is_kill_switch_engaged(blackboard_root, scope="PRODUCTION")
    if state is not None:
        raise KillSwitchEngaged(state)


def _validate_tenant_id(value: str) -> None:
    if not isinstance(value, str) or not value or len(value) > _MAX_TENANT_ID_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: tenant_id must be a non-empty string "
            f"<= {_MAX_TENANT_ID_LENGTH} chars"
        )


def _validate_finding_id(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise GovernanceError(
            "two_channel_confirmation: finding_id must be a non-empty string"
        )
    if len(value) > _MAX_FINDING_ID_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: finding_id must be "
            f"<= {_MAX_FINDING_ID_LENGTH} characters"
        )
    if not _FINDING_ID_RE.match(value):
        raise GovernanceError(
            "two_channel_confirmation: finding_id may only contain "
            "[A-Za-z0-9_-:.] characters"
        )
    if value in {".", ".."} or value.startswith(".") or value.endswith("."):
        raise GovernanceError(
            "two_channel_confirmation: finding_id must not be a relative "
            "path token or start/end with '.'"
        )


def _validate_detector(value: str) -> None:
    if not isinstance(value, str) or not value or len(value) > _MAX_DETECTOR_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: detector must be a non-empty string "
            f"<= {_MAX_DETECTOR_LENGTH} chars"
        )


def _validate_request_risk_floor(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GovernanceError(
            "two_channel_confirmation: risk_floor must be an int"
        )
    if value < 1 or value > 100:
        raise GovernanceError(
            "two_channel_confirmation: risk_floor must be in [1, 100] "
            "(only positive floors trigger needs_review)"
        )


def _validate_operator_label(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value or len(value) > _MAX_OPERATOR_LENGTH:
        raise GovernanceError(
            f"two_channel_confirmation: {field_name} must be a non-empty "
            f"string <= {_MAX_OPERATOR_LENGTH} chars"
        )


def _validate_outcome_status(value: TwoChannelOutcomeStatus) -> None:
    if value not in ("confirmed", "rejected", "unable_to_verify", "expired"):
        raise GovernanceError(
            "two_channel_confirmation: outcome_status must be one of "
            "{confirmed, rejected, unable_to_verify, expired}"
        )


def _require_aware_datetime(value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise GovernanceError(
            "two_channel_confirmation: timestamps must be aware datetimes"
        )
    if value.tzinfo is None:
        raise GovernanceError(
            "two_channel_confirmation: timestamps must be timezone-aware"
        )
    return value.astimezone(timezone.utc)


def _read_all_events(root: Path, tenant_id: str) -> list[dict]:
    path = blackboard_path(root, Environment.PRODUCTION, tenant_id)
    if not path.exists():
        return []
    events: list[dict] = []
    for record in read_records(path):
        if record.record_type != RecordType.TWO_CHANNEL_CONFIRMATION:
            continue
        if record.tenant_id != tenant_id:
            continue
        events.append(record.payload)
    return events


def _read_events_for_finding(
    root: Path, tenant_id: str, finding_id: str
) -> list[dict]:
    return [
        event
        for event in _read_all_events(root, tenant_id)
        if event.get("finding_id") == finding_id
    ]


def _first_event(events: list[dict], event_type: TwoChannelEventType) -> dict | None:
    for event in events:
        if event["event_type"] == event_type:
            return event
    return None


def _parse_payload_datetime(value: str | None) -> datetime:
    if value is None:
        raise GovernanceError(
            "two_channel_confirmation: missing requested_at on prior pending event"
        )
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise GovernanceError(
            "two_channel_confirmation: stored timestamps must be timezone-aware"
        )
    return parsed.astimezone(timezone.utc)


def _pending_to_record(pending: dict) -> ConfirmationRecord:
    return ConfirmationRecord(
        finding_id=pending["finding_id"],
        tenant_id=pending["tenant_id"],
        detector=pending["detector"],
        recommended_action="needs_review",
        risk_floor=int(pending["risk_floor"]),
        requested_at=_parse_payload_datetime(pending.get("requested_at")),
        requested_by=pending["requested_by"],
    )


def _merge_pending_and_outcome(pending: dict, outcome: dict) -> ConfirmationRecord:
    return ConfirmationRecord(
        finding_id=pending["finding_id"],
        tenant_id=pending["tenant_id"],
        detector=pending["detector"],
        recommended_action="needs_review",
        risk_floor=int(pending["risk_floor"]),
        requested_at=_parse_payload_datetime(pending.get("requested_at")),
        requested_by=pending["requested_by"],
        outcome_at=_parse_payload_datetime(outcome.get("outcome_at")),
        outcome_by=outcome.get("outcome_by"),
        outcome_status=outcome.get("outcome_status"),
        channel_kind=outcome.get("channel_kind"),
        channel_description=outcome.get("channel_description"),
        reason=outcome.get("reason"),
    )


__all__ = [
    "ConfirmationRecord",
    "list_pending_confirmations",
    "record_confirmation_outcome",
    "record_confirmation_request",
    "summarize_confirmation_status",
]
