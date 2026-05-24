"""Effective parameter report for Phase 2.1 per-tenant overrides.

Read-only builder that joins signed policy state, on-disk tenant override
state, and the append-only override audit log into one structured report.
The report is intended for MSP / operator client review: it shows which
defensive parameters are active for a tenant and, for each, whether the
value came from the signed policy baseline or the tenant override overlay.

This module is read-only. It does not write to ``production_state``, does
not append audit events (the override resolver in
``tenant_overrides.resolve_effective_parameters`` does that), and is not
imported by agent or production loop code paths. The Phase 2.1 operator
CLI thin-wraps it for the ``report`` subcommand; a future Phase 2.3
evidence-package exporter can consume the same structure.

See
``4. Product_Roadmap/Phase_2_1_Fraud_Detection_Product_Sheet_And_Tenant_Overrides.md``
§9 and ``Tenant_Override_Operator_Runbook.md``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from core.blackboard import (
    EffectiveParameterProvenance,
    EffectiveParametersReportPayload,
    GovernanceError,
)

from .state import load_state, state_path
from .tenant_overrides import (
    EXPOSED_TENANT_OVERRIDE_KEYS,
    TenantOverrideAuditEvent,
    TenantParameterOverride,
    load_tenant_override,
    read_tenant_override_audit_events,
    tenant_override_audit_path,
    tenant_override_path,
)

ParameterSource = Literal["default", "signed_policy", "tenant_override"]

DEFAULT_AUDIT_LIMIT = 5


@dataclass(frozen=True)
class EffectiveParameterEntry:
    """One row in the per-tenant effective-parameter table.

    ``value`` is the resolved effective value used by scoring. ``source``
    names where that value came from. ``signed_policy_value`` and
    ``override_value`` are kept so the MSP review packet can show both
    sides of the overlay even when one is missing.
    """

    key: str
    value: int | None
    source: ParameterSource
    signed_policy_value: int | None
    override_value: int | None


@dataclass(frozen=True)
class OverrideSummary:
    """Human-readable summary of the current on-disk tenant override."""

    status: str
    reason: str
    requested_by: str
    approved_by: str
    created_at: datetime
    expires_at: datetime | None
    parameters: dict[str, int]


@dataclass(frozen=True)
class EffectiveParametersReport:
    """Structured snapshot of effective parameters for one production tenant."""

    tenant_id: str
    evaluated_at: datetime
    policy_active_version: str
    signed_policy_parameters: dict[str, Any]
    entries: list[EffectiveParameterEntry]
    override_summary: OverrideSummary | None
    override_applied: bool
    override_not_applied_reason: str | None
    recent_audit_events: list[TenantOverrideAuditEvent] = field(default_factory=list)


def build_effective_parameters_report(
    *,
    blackboard_root: Path,
    tenant_id: str,
    now: datetime | None = None,
    audit_limit: int = DEFAULT_AUDIT_LIMIT,
) -> EffectiveParametersReport:
    """Assemble an effective-parameter report for one production tenant.

    Reads signed policy state, the current override file (if any), and the
    append-only override audit log. Never writes. Override files that fail
    governance validation are surfaced as ``override_not_applied_reason``
    so the report itself can explain why the runtime is falling back to
    signed policy.
    """

    evaluated_at = now or datetime.now(timezone.utc)
    policy_state = load_state(state_path(blackboard_root, tenant_id))
    signed_policy_parameters = dict(policy_state.parameters)

    override_path = tenant_override_path(blackboard_root, tenant_id)
    override, load_error = _load_override_safe(override_path)
    applied, not_applied_reason = _classify_override(
        override,
        load_error=load_error,
        evaluated_at=evaluated_at,
    )

    entries = _build_entries(
        signed_policy_parameters=signed_policy_parameters,
        override=override if applied else None,
    )
    summary = None if override is None else _summarize_override(override)
    recent_events = _read_recent_audit_events(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        limit=audit_limit,
    )

    return EffectiveParametersReport(
        tenant_id=tenant_id,
        evaluated_at=evaluated_at,
        policy_active_version=policy_state.active_version,
        signed_policy_parameters=signed_policy_parameters,
        entries=entries,
        override_summary=summary,
        override_applied=applied,
        override_not_applied_reason=not_applied_reason,
        recent_audit_events=recent_events,
    )


def render_report_text(report: EffectiveParametersReport) -> str:
    """Render the report as terminal-friendly plain text."""

    lines: list[str] = [
        f"NorthStar Inbox Shield — Effective Parameter Report",
        f"Tenant: {report.tenant_id}",
        f"Evaluated at: {report.evaluated_at.isoformat()}",
        f"Signed policy version: {report.policy_active_version}",
        "",
        "Effective lift parameters:",
    ]
    for entry in report.entries:
        lines.append(_format_entry_text(entry))
    lines.append("")
    if report.override_summary is None:
        lines.append("Tenant override: (none on disk)")
    else:
        lines.append("Tenant override:")
        lines.extend(_format_override_summary_text(report.override_summary))
    lines.append("")
    if report.override_applied:
        lines.append("Override applied for scoring: yes")
    else:
        suffix = (
            f" — {report.override_not_applied_reason}"
            if report.override_not_applied_reason
            else ""
        )
        lines.append(f"Override applied for scoring: no{suffix}")
    lines.append("")
    lines.append(f"Recent override audit events (last {len(report.recent_audit_events)}):")
    if not report.recent_audit_events:
        lines.append("  (none)")
    else:
        for event in report.recent_audit_events:
            lines.append("  " + _format_audit_line_text(event))
    return "\n".join(lines)


def render_report_markdown(report: EffectiveParametersReport) -> str:
    """Render the report as MSP-shareable markdown."""

    lines: list[str] = [
        "# NorthStar Inbox Shield — Effective Parameter Report",
        "",
        f"**Tenant:** {report.tenant_id}",
        f"**Evaluated at:** {report.evaluated_at.isoformat()}",
        f"**Signed policy version:** {report.policy_active_version}",
        "",
        "## Effective Lift Parameters",
        "",
        "| Parameter | Effective Value | Source | Signed Policy | Tenant Override |",
        "|---|---|---|---|---|",
    ]
    for entry in report.entries:
        lines.append(_format_entry_markdown_row(entry))
    lines.append("")
    extra_policy = _extra_signed_policy_parameters(report.signed_policy_parameters)
    if extra_policy:
        lines.append("Other signed policy parameters (not tenant-tunable):")
        lines.append("")
        for key in sorted(extra_policy):
            lines.append(f"- `{key}`: `{extra_policy[key]}`")
        lines.append("")
    lines.append("## Tenant Override")
    lines.append("")
    if report.override_summary is None:
        lines.append("_No tenant override on disk. Effective values match signed policy state._")
    else:
        lines.extend(_format_override_summary_markdown(report.override_summary))
    lines.append("")
    if report.override_applied:
        lines.append("**Override applied for scoring:** yes")
    else:
        suffix = (
            f" — {report.override_not_applied_reason}"
            if report.override_not_applied_reason
            else ""
        )
        lines.append(f"**Override applied for scoring:** no{suffix}")
    lines.append("")
    lines.append(f"## Recent Override Audit Events (last {len(report.recent_audit_events)})")
    lines.append("")
    if not report.recent_audit_events:
        lines.append("_No override audit events recorded for this tenant._")
    else:
        lines.append("| Timestamp | Event | Requester | Approver | Source | Reason |")
        lines.append("|---|---|---|---|---|---|")
        for event in report.recent_audit_events:
            lines.append(_format_audit_row_markdown(event))
    lines.append("")
    return "\n".join(lines)


def render_report_json(report: EffectiveParametersReport) -> str:
    """Render the report as a stable, sort-keys JSON string."""

    return json.dumps(report_to_dict(report), indent=2, sort_keys=True)


def report_to_payload(report: EffectiveParametersReport) -> EffectiveParametersReportPayload:
    """Convert the read-only report into the Blackboard payload schema."""

    latest = report.recent_audit_events[0] if report.recent_audit_events else None
    return EffectiveParametersReportPayload(
        tenant_id=report.tenant_id,
        evaluated_at=report.evaluated_at,
        policy_active_version=report.policy_active_version,
        override_status=(
            report.override_summary.status if report.override_summary is not None else None
        ),
        override_applied=report.override_applied,
        override_reason=(
            report.override_summary.reason if report.override_summary is not None else None
        ),
        override_requested_by=(
            report.override_summary.requested_by
            if report.override_summary is not None
            else None
        ),
        override_approved_by=(
            report.override_summary.approved_by
            if report.override_summary is not None
            else None
        ),
        override_created_at=(
            report.override_summary.created_at
            if report.override_summary is not None
            else None
        ),
        override_expires_at=(
            report.override_summary.expires_at
            if report.override_summary is not None
            else None
        ),
        latest_audit_event_type=latest.event_type if latest is not None else None,
        latest_audit_event_timestamp=latest.timestamp if latest is not None else None,
        latest_audit_event_source=latest.source if latest is not None else None,
        parameter_provenance=[
            EffectiveParameterProvenance(
                parameter_name=entry.key,
                signed_policy_value=entry.signed_policy_value,
                override_value=entry.override_value,
                effective_value=entry.value,
                source=(
                    "tenant_override"
                    if entry.source == "tenant_override"
                    else "signed_policy"
                ),
            )
            for entry in report.entries
        ],
        client_summary=_client_summary(report),
    )


def report_to_dict(report: EffectiveParametersReport) -> dict[str, Any]:
    """Return a plain dict suitable for JSON serialization or record payloads."""

    return {
        "tenant_id": report.tenant_id,
        "evaluated_at": report.evaluated_at.isoformat(),
        "policy_active_version": report.policy_active_version,
        "signed_policy_parameters": report.signed_policy_parameters,
        "entries": [_entry_to_dict(entry) for entry in report.entries],
        "override_summary": (
            None
            if report.override_summary is None
            else _override_summary_to_dict(report.override_summary)
        ),
        "override_applied": report.override_applied,
        "override_not_applied_reason": report.override_not_applied_reason,
        "recent_audit_events": [
            _audit_event_to_dict(event) for event in report.recent_audit_events
        ],
    }


def _client_summary(report: EffectiveParametersReport) -> str:
    if report.override_applied:
        return (
            "This tenant has an approved sensitivity override layered on top of "
            "the signed NorthStar baseline. The effective values below are what "
            "the production scoring loop uses for this tenant."
        )
    return (
        "This tenant is using the signed NorthStar baseline for the exposed "
        "sensitivity settings. No active override is changing the effective "
        "values at this evaluation time."
    )


def _load_override_safe(
    path: Path,
) -> tuple[TenantParameterOverride | None, str | None]:
    if not path.exists():
        return None, None
    try:
        return load_tenant_override(path), None
    except GovernanceError as exc:
        return None, str(exc)


def _classify_override(
    override: TenantParameterOverride | None,
    *,
    load_error: str | None,
    evaluated_at: datetime,
) -> tuple[bool, str | None]:
    if load_error is not None:
        return False, f"override file is invalid: {load_error}"
    if override is None:
        return False, None
    if override.status == "paused":
        return False, "override is paused"
    if override.status == "revoked":
        return False, "override is revoked"
    if override.status != "active":
        return False, f"override status is {override.status!r}"
    if override.expires_at is not None and override.expires_at <= evaluated_at:
        return False, f"override expired at {override.expires_at.isoformat()}"
    return True, None


def _build_entries(
    *,
    signed_policy_parameters: dict[str, Any],
    override: TenantParameterOverride | None,
) -> list[EffectiveParameterEntry]:
    override_parameters = override.parameters if override is not None else {}
    entries: list[EffectiveParameterEntry] = []
    for key in sorted(EXPOSED_TENANT_OVERRIDE_KEYS):
        policy_value = _coerce_int(signed_policy_parameters.get(key))
        override_value = override_parameters.get(key)
        if override is not None and key in override_parameters:
            entries.append(
                EffectiveParameterEntry(
                    key=key,
                    value=int(override_value),
                    source="tenant_override",
                    signed_policy_value=policy_value,
                    override_value=int(override_value),
                )
            )
            continue
        if policy_value is not None:
            entries.append(
                EffectiveParameterEntry(
                    key=key,
                    value=policy_value,
                    source="signed_policy",
                    signed_policy_value=policy_value,
                    override_value=None,
                )
            )
            continue
        entries.append(
            EffectiveParameterEntry(
                key=key,
                value=None,
                source="default",
                signed_policy_value=None,
                override_value=None,
            )
        )
    return entries


def _summarize_override(override: TenantParameterOverride) -> OverrideSummary:
    return OverrideSummary(
        status=override.status,
        reason=override.reason,
        requested_by=override.requested_by,
        approved_by=override.approved_by,
        created_at=override.created_at,
        expires_at=override.expires_at,
        parameters=dict(override.parameters),
    )


def _read_recent_audit_events(
    *,
    blackboard_root: Path,
    tenant_id: str,
    limit: int,
) -> list[TenantOverrideAuditEvent]:
    if limit <= 0:
        return []
    path = tenant_override_audit_path(blackboard_root, tenant_id)
    try:
        events = read_tenant_override_audit_events(path)
    except (GovernanceError, json.JSONDecodeError):
        return []
    if not events:
        return []
    sorted_events = sorted(events, key=lambda event: event.timestamp, reverse=True)
    return sorted_events[:limit]


def _extra_signed_policy_parameters(
    signed_policy_parameters: dict[str, Any],
) -> dict[str, Any]:
    return {
        key: value
        for key, value in signed_policy_parameters.items()
        if key not in EXPOSED_TENANT_OVERRIDE_KEYS
    }


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _format_entry_text(entry: EffectiveParameterEntry) -> str:
    value = "(unset)" if entry.value is None else str(entry.value)
    signed = (
        "(unset)" if entry.signed_policy_value is None else str(entry.signed_policy_value)
    )
    override = "(none)" if entry.override_value is None else str(entry.override_value)
    return (
        f"  {entry.key}: value={value} source={entry.source} "
        f"signed_policy={signed} tenant_override={override}"
    )


def _format_entry_markdown_row(entry: EffectiveParameterEntry) -> str:
    value = "(unset)" if entry.value is None else str(entry.value)
    signed = (
        "(unset)"
        if entry.signed_policy_value is None
        else str(entry.signed_policy_value)
    )
    override = (
        "(none)" if entry.override_value is None else str(entry.override_value)
    )
    return (
        f"| `{entry.key}` | `{value}` | `{entry.source}` | "
        f"`{signed}` | `{override}` |"
    )


def _format_override_summary_text(summary: OverrideSummary) -> list[str]:
    lines = [
        f"  status: {summary.status}",
        f"  reason: {summary.reason}",
        f"  requested_by: {summary.requested_by}",
        f"  approved_by: {summary.approved_by}",
        f"  created_at: {summary.created_at.isoformat()}",
    ]
    if summary.expires_at is not None:
        lines.append(f"  expires_at: {summary.expires_at.isoformat()}")
    lines.append("  override parameters:")
    for key in sorted(summary.parameters):
        lines.append(f"    {key}: {summary.parameters[key]}")
    return lines


def _format_override_summary_markdown(summary: OverrideSummary) -> list[str]:
    lines = [
        f"- **Status:** `{summary.status}`",
        f"- **Reason:** {summary.reason}",
        f"- **Requested by:** `{summary.requested_by}`",
        f"- **Approved by:** `{summary.approved_by}`",
        f"- **Created at:** {summary.created_at.isoformat()}",
    ]
    if summary.expires_at is not None:
        lines.append(f"- **Expires at:** {summary.expires_at.isoformat()}")
    lines.append("- **Override parameters:**")
    for key in sorted(summary.parameters):
        lines.append(f"  - `{key}`: `{summary.parameters[key]}`")
    return lines


def _format_audit_line_text(event: TenantOverrideAuditEvent) -> str:
    return (
        f"{event.timestamp.isoformat()}  {event.event_type}  "
        f"requester={event.requested_by}  approver={event.approved_by}  "
        f"source={event.source}  reason={event.reason!r}"
    )


def _format_audit_row_markdown(event: TenantOverrideAuditEvent) -> str:
    safe_reason = event.reason.replace("|", "\\|")
    return (
        f"| {event.timestamp.isoformat()} | `{event.event_type}` | "
        f"`{event.requested_by}` | `{event.approved_by}` | "
        f"`{event.source}` | {safe_reason} |"
    )


def _entry_to_dict(entry: EffectiveParameterEntry) -> dict[str, Any]:
    return {
        "key": entry.key,
        "value": entry.value,
        "source": entry.source,
        "signed_policy_value": entry.signed_policy_value,
        "override_value": entry.override_value,
    }


def _override_summary_to_dict(summary: OverrideSummary) -> dict[str, Any]:
    return {
        "status": summary.status,
        "reason": summary.reason,
        "requested_by": summary.requested_by,
        "approved_by": summary.approved_by,
        "created_at": summary.created_at.isoformat(),
        "expires_at": (
            summary.expires_at.isoformat() if summary.expires_at is not None else None
        ),
        "parameters": dict(summary.parameters),
    }


def _audit_event_to_dict(event: TenantOverrideAuditEvent) -> dict[str, Any]:
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
    "DEFAULT_AUDIT_LIMIT",
    "EffectiveParameterEntry",
    "EffectiveParametersReport",
    "OverrideSummary",
    "ParameterSource",
    "build_effective_parameters_report",
    "render_report_json",
    "render_report_markdown",
    "render_report_text",
    "report_to_dict",
    "report_to_payload",
]
