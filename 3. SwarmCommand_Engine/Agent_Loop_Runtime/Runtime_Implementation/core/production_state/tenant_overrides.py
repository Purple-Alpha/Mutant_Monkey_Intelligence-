"""Per-tenant Phase 2.1 parameter overrides.

The signed policy state remains the governed baseline for production
parameters. Phase 2.1 adds an operator-approved overlay that can tune the
three Phase 1.4 lift keys per tenant while preserving the same bounded
runtime surface:

* local JSON file per production tenant for the current override;
* append-only local JSONL audit events for every write and ignored read;
* write-time rejection for invalid keys / values / approval metadata;
* optional ``expires_at`` support in v1;
* no exposure of legacy ``confidence_boost`` through this override surface.

See
``4. Product_Roadmap/Phase_2_1_Fraud_Detection_Product_Sheet_And_Tenant_Overrides.md``
§11.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from core.blackboard import GovernanceError

TENANT_OVERRIDE_STATUS_VALUES = frozenset({"active", "paused", "revoked"})
TenantOverrideStatus = Literal["active", "paused", "revoked"]

EXPOSED_TENANT_OVERRIDE_KEYS: frozenset[str] = frozenset(
    {
        "fraud_risk_floor_lift",
        "attachment_risk_floor_lift",
        "url_obfuscation_floor_lift",
        "vendor_baseline_ttl_days",
    }
)

TENANT_OVERRIDE_CREATED = "tenant_parameter_override_created"
TENANT_OVERRIDE_UPDATED = "tenant_parameter_override_updated"
TENANT_OVERRIDE_PAUSED = "tenant_parameter_override_paused"
TENANT_OVERRIDE_REVOKED = "tenant_parameter_override_revoked"
TENANT_OVERRIDE_EXPIRED = "tenant_parameter_override_expired"
TENANT_OVERRIDE_INVALID = "tenant_parameter_override_invalid"
TENANT_OVERRIDE_IGNORED = "tenant_parameter_override_ignored"


@dataclass(frozen=True)
class TenantParameterOverride:
    tenant_id: str
    parameters: dict[str, int]
    reason: str
    requested_by: str
    approved_by: str
    created_at: datetime
    expires_at: datetime | None = None
    status: TenantOverrideStatus = "active"


@dataclass(frozen=True)
class TenantOverrideAuditEvent:
    event_type: str
    tenant_id: str
    parameters_before: dict[str, int] = field(default_factory=dict)
    parameters_after: dict[str, int] = field(default_factory=dict)
    reason: str = ""
    requested_by: str = "runtime"
    approved_by: str = "runtime"
    source: str = "runtime"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def tenant_override_path(blackboard_root: Path, tenant_id: str) -> Path:
    safe = _safe_tenant_id(tenant_id)
    return blackboard_root / "production_state" / "tenant_overrides" / f"{safe}.override.json"


def tenant_override_audit_path(blackboard_root: Path, tenant_id: str) -> Path:
    safe = _safe_tenant_id(tenant_id)
    return blackboard_root / "production_state" / "tenant_overrides" / f"{safe}.override.audit.jsonl"


def load_tenant_override(path: Path) -> TenantParameterOverride | None:
    """Load a current tenant override from disk.

    Missing files return ``None``. Corrupt or invalid files raise
    ``GovernanceError`` so callers that are writing can fail loudly.
    Runtime read paths should use ``resolve_effective_parameters`` which
    catches the error, audits it, and falls back to signed policy state.
    """

    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GovernanceError("tenant override file is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise GovernanceError("tenant override file is not a JSON object")
    allowed = {
        "tenant_id",
        "parameters",
        "reason",
        "requested_by",
        "approved_by",
        "created_at",
        "expires_at",
        "status",
    }
    unknown = set(raw.keys()) - allowed
    if unknown:
        raise GovernanceError(
            f"tenant override file contains unauthorized fields: {sorted(unknown)}"
        )
    return _validate_override(
        TenantParameterOverride(
            tenant_id=_require_string(raw.get("tenant_id"), "tenant_id"),
            parameters=_require_parameters(raw.get("parameters")),
            reason=_require_string(raw.get("reason"), "reason"),
            requested_by=_require_string(raw.get("requested_by"), "requested_by"),
            approved_by=_require_string(raw.get("approved_by"), "approved_by"),
            created_at=_parse_datetime(raw.get("created_at"), "created_at"),
            expires_at=_parse_optional_datetime(raw.get("expires_at"), "expires_at"),
            status=_require_status(raw.get("status", "active")),
        )
    )


def create_or_update_tenant_override(
    *,
    blackboard_root: Path,
    tenant_id: str,
    parameters: dict[str, int],
    reason: str,
    requested_by: str,
    approved_by: str,
    expires_at: datetime | None = None,
    source: str = "operator",
    now: datetime | None = None,
) -> TenantParameterOverride:
    """Create or replace the active override for one production tenant.

    Invalid input is rejected before any override file is written, per
    Matt's Phase 2.1 §11 decision 2. A successful write emits either
    ``tenant_parameter_override_created`` or
    ``tenant_parameter_override_updated`` to the tenant's append-only
    audit log.
    """

    timestamp = now or datetime.now(timezone.utc)
    path = tenant_override_path(blackboard_root, tenant_id)
    before = _load_for_write(path)
    override = _validate_override(
        TenantParameterOverride(
            tenant_id=tenant_id,
            parameters=dict(parameters),
            reason=reason,
            requested_by=requested_by,
            approved_by=approved_by,
            created_at=timestamp,
            expires_at=expires_at,
            status="active",
        )
    )
    _write_override(path, override)
    _append_audit_event(
        tenant_override_audit_path(blackboard_root, tenant_id),
        TenantOverrideAuditEvent(
            event_type=TENANT_OVERRIDE_UPDATED if before is not None else TENANT_OVERRIDE_CREATED,
            tenant_id=tenant_id,
            parameters_before=before.parameters if before is not None else {},
            parameters_after=override.parameters,
            reason=reason,
            requested_by=requested_by,
            approved_by=approved_by,
            source=source,
            timestamp=timestamp,
        ),
    )
    return override


def pause_tenant_override(
    *,
    blackboard_root: Path,
    tenant_id: str,
    reason: str,
    requested_by: str,
    approved_by: str,
    source: str = "operator",
    now: datetime | None = None,
) -> TenantParameterOverride:
    return _transition_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        status="paused",
        event_type=TENANT_OVERRIDE_PAUSED,
        reason=reason,
        requested_by=requested_by,
        approved_by=approved_by,
        source=source,
        now=now,
    )


def revoke_tenant_override(
    *,
    blackboard_root: Path,
    tenant_id: str,
    reason: str,
    requested_by: str,
    approved_by: str,
    source: str = "operator",
    now: datetime | None = None,
) -> TenantParameterOverride:
    return _transition_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        status="revoked",
        event_type=TENANT_OVERRIDE_REVOKED,
        reason=reason,
        requested_by=requested_by,
        approved_by=approved_by,
        source=source,
        now=now,
    )


def resolve_effective_parameters(
    *,
    blackboard_root: Path,
    tenant_id: str,
    policy_parameters: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return policy parameters overlaid with any valid active tenant override.

    Missing override files leave ``policy_parameters`` unchanged. Invalid,
    expired, paused, or revoked overrides are ignored and append one local
    audit event so operators can inspect why the override was not applied.
    """

    timestamp = now or datetime.now(timezone.utc)
    base = dict(policy_parameters)
    path = tenant_override_path(blackboard_root, tenant_id)
    try:
        override = load_tenant_override(path)
    except GovernanceError as exc:
        _append_runtime_audit(
            blackboard_root,
            tenant_id,
            event_type=TENANT_OVERRIDE_INVALID,
            parameters_before=base,
            parameters_after=base,
            reason=str(exc),
            timestamp=timestamp,
        )
        return base
    if override is None:
        return base
    if override.status != "active":
        _append_runtime_audit(
            blackboard_root,
            tenant_id,
            event_type=TENANT_OVERRIDE_IGNORED,
            parameters_before=base,
            parameters_after=base,
            reason=f"tenant override status is {override.status}",
            timestamp=timestamp,
        )
        return base
    if override.expires_at is not None and override.expires_at <= timestamp:
        _append_runtime_audit(
            blackboard_root,
            tenant_id,
            event_type=TENANT_OVERRIDE_EXPIRED,
            parameters_before=base,
            parameters_after=base,
            reason="tenant override expired",
            timestamp=timestamp,
        )
        return base
    effective = dict(base)
    effective.update(override.parameters)
    return effective


def read_tenant_override_audit_events(path: Path) -> list[TenantOverrideAuditEvent]:
    if not path.exists():
        return []
    events: list[TenantOverrideAuditEvent] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        events.append(
            TenantOverrideAuditEvent(
                event_type=_require_string(raw.get("event_type"), "event_type"),
                tenant_id=_require_string(raw.get("tenant_id"), "tenant_id"),
                parameters_before=_require_parameters(raw.get("parameters_before", {})),
                parameters_after=_require_parameters(raw.get("parameters_after", {})),
                reason=_require_string(raw.get("reason"), "reason"),
                requested_by=_require_string(raw.get("requested_by"), "requested_by"),
                approved_by=_require_string(raw.get("approved_by"), "approved_by"),
                source=_require_string(raw.get("source"), "source"),
                timestamp=_parse_datetime(raw.get("timestamp"), "timestamp"),
            )
        )
    return events


def _transition_override(
    *,
    blackboard_root: Path,
    tenant_id: str,
    status: TenantOverrideStatus,
    event_type: str,
    reason: str,
    requested_by: str,
    approved_by: str,
    source: str,
    now: datetime | None,
) -> TenantParameterOverride:
    timestamp = now or datetime.now(timezone.utc)
    _validate_approval(reason=reason, requested_by=requested_by, approved_by=approved_by)
    path = tenant_override_path(blackboard_root, tenant_id)
    before = _load_for_write(path)
    if before is None:
        raise GovernanceError("tenant override does not exist")
    after = _validate_override(
        TenantParameterOverride(
            tenant_id=before.tenant_id,
            parameters=before.parameters,
            reason=reason,
            requested_by=requested_by,
            approved_by=approved_by,
            created_at=before.created_at,
            expires_at=before.expires_at,
            status=status,
        )
    )
    _write_override(path, after)
    _append_audit_event(
        tenant_override_audit_path(blackboard_root, tenant_id),
        TenantOverrideAuditEvent(
            event_type=event_type,
            tenant_id=tenant_id,
            parameters_before=before.parameters,
            parameters_after={} if status in {"paused", "revoked"} else after.parameters,
            reason=reason,
            requested_by=requested_by,
            approved_by=approved_by,
            source=source,
            timestamp=timestamp,
        ),
    )
    return after


def _load_for_write(path: Path) -> TenantParameterOverride | None:
    try:
        return load_tenant_override(path)
    except GovernanceError:
        # Writes must not build on top of corrupt state. Reject loudly
        # rather than silently replacing the file and losing forensic value.
        raise


def _write_override(path: Path, override: TenantParameterOverride) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _override_to_json(override)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    tmp.replace(path)


def _append_audit_event(path: Path, event: TenantOverrideAuditEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_audit_event_to_json(event), sort_keys=True) + "\n")


def _append_runtime_audit(
    blackboard_root: Path,
    tenant_id: str,
    *,
    event_type: str,
    parameters_before: dict[str, Any],
    parameters_after: dict[str, Any],
    reason: str,
    timestamp: datetime,
) -> None:
    _append_audit_event(
        tenant_override_audit_path(blackboard_root, tenant_id),
        TenantOverrideAuditEvent(
            event_type=event_type,
            tenant_id=tenant_id,
            parameters_before=_int_parameters_only(parameters_before),
            parameters_after=_int_parameters_only(parameters_after),
            reason=reason,
            requested_by="runtime",
            approved_by="runtime",
            source="runtime",
            timestamp=timestamp,
        ),
    )


def _validate_override(override: TenantParameterOverride) -> TenantParameterOverride:
    _safe_tenant_id(override.tenant_id)
    _validate_approval(
        reason=override.reason,
        requested_by=override.requested_by,
        approved_by=override.approved_by,
    )
    _require_parameters(override.parameters)
    if override.status not in TENANT_OVERRIDE_STATUS_VALUES:
        raise GovernanceError(f"invalid tenant override status: {override.status}")
    if override.created_at.tzinfo is None:
        raise GovernanceError("created_at must be timezone-aware")
    if override.expires_at is not None and override.expires_at.tzinfo is None:
        raise GovernanceError("expires_at must be timezone-aware")
    return override


def _validate_approval(*, reason: str, requested_by: str, approved_by: str) -> None:
    if not reason.strip():
        raise GovernanceError("tenant override reason is required")
    if not requested_by.strip():
        raise GovernanceError("tenant override requested_by is required")
    if not approved_by.strip():
        raise GovernanceError("tenant override approved_by is required")
    if requested_by.strip() == approved_by.strip():
        raise GovernanceError("tenant override requires separate requested_by and approved_by")


def _require_parameters(raw: object) -> dict[str, int]:
    if not isinstance(raw, dict):
        raise GovernanceError("tenant override parameters must be a JSON object")
    keys = set(raw.keys())
    unauthorized = keys - EXPOSED_TENANT_OVERRIDE_KEYS
    if unauthorized:
        raise GovernanceError(
            f"unauthorized tenant override parameter key: {sorted(unauthorized)}"
        )
    out: dict[str, int] = {}
    for key, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise GovernanceError(f"tenant override parameter {key!r} must be an int")
        if key == "vendor_baseline_ttl_days":
            if value < 30 or value > 365:
                raise GovernanceError(
                    "tenant override parameter 'vendor_baseline_ttl_days' "
                    "must be between 30 and 365"
                )
        elif value < 0 or value > 25:
            raise GovernanceError(
                f"tenant override parameter {key!r} must be between 0 and 25"
            )
        out[key] = value
    return out


def _int_parameters_only(parameters: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, value in parameters.items():
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        out[key] = value
    return out


def _safe_tenant_id(tenant_id: str) -> str:
    safe = "".join(c if c.isalnum() or c in "_.-" else "_" for c in tenant_id.strip())
    if not safe:
        raise GovernanceError("tenant_id resolves to empty override filename")
    return safe


def _require_string(raw: object, field_name: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise GovernanceError(f"{field_name} must be a non-empty string")
    return raw


def _require_status(raw: object) -> TenantOverrideStatus:
    if raw not in TENANT_OVERRIDE_STATUS_VALUES:
        raise GovernanceError(f"invalid tenant override status: {raw!r}")
    return raw  # type: ignore[return-value]


def _parse_datetime(raw: object, field_name: str) -> datetime:
    if not isinstance(raw, str):
        raise GovernanceError(f"{field_name} must be an ISO datetime string")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise GovernanceError(f"{field_name} must be an ISO datetime string") from exc
    if parsed.tzinfo is None:
        raise GovernanceError(f"{field_name} must be timezone-aware")
    return parsed


def _parse_optional_datetime(raw: object, field_name: str) -> datetime | None:
    if raw is None:
        return None
    return _parse_datetime(raw, field_name)


def _override_to_json(override: TenantParameterOverride) -> dict[str, Any]:
    return {
        "tenant_id": override.tenant_id,
        "parameters": override.parameters,
        "reason": override.reason,
        "requested_by": override.requested_by,
        "approved_by": override.approved_by,
        "created_at": override.created_at.isoformat(),
        "expires_at": override.expires_at.isoformat() if override.expires_at else None,
        "status": override.status,
    }


def _audit_event_to_json(event: TenantOverrideAuditEvent) -> dict[str, Any]:
    return {
        "event_type": event.event_type,
        "tenant_id": event.tenant_id,
        "parameters_before": event.parameters_before,
        "parameters_after": event.parameters_after,
        "reason": event.reason,
        "requested_by": event.requested_by,
        "approved_by": event.approved_by,
        "source": event.source,
        "timestamp": event.timestamp.isoformat(),
    }


__all__ = [
    "EXPOSED_TENANT_OVERRIDE_KEYS",
    "TENANT_OVERRIDE_CREATED",
    "TENANT_OVERRIDE_EXPIRED",
    "TENANT_OVERRIDE_IGNORED",
    "TENANT_OVERRIDE_INVALID",
    "TENANT_OVERRIDE_PAUSED",
    "TENANT_OVERRIDE_REVOKED",
    "TENANT_OVERRIDE_UPDATED",
    "TenantOverrideAuditEvent",
    "TenantParameterOverride",
    "create_or_update_tenant_override",
    "load_tenant_override",
    "pause_tenant_override",
    "read_tenant_override_audit_events",
    "resolve_effective_parameters",
    "revoke_tenant_override",
    "tenant_override_audit_path",
    "tenant_override_path",
]
