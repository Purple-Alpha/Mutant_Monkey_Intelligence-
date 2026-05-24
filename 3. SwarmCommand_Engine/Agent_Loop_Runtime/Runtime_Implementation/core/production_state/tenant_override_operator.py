"""Operator CLI for Phase 2.1 per-tenant parameter overrides.

Run with::

    python -m core.production_state.tenant_override_operator --help

This module is operator tooling only. It must not be imported by agent or
production loop code paths. It wraps the write and read APIs in
``tenant_overrides.py`` with a small argparse surface for day-to-day MSP /
operator work:

* create — create or replace an active override
* pause — pause an existing override
* revoke — revoke an existing override
* effective — review signed policy vs override overlay vs effective params
* audit — inspect append-only override audit history
* report — MSP-shareable effective-parameter report (text / json / markdown)
* show — show current on-disk override record

See ``4. Product_Roadmap/Phase_2_1_Fraud_Detection_Product_Sheet_And_Tenant_Overrides.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from core.blackboard import GovernanceError

from .effective_parameters_report import (
    DEFAULT_AUDIT_LIMIT,
    build_effective_parameters_report,
    render_report_json,
    render_report_markdown,
    render_report_text,
)
from .state import load_state, state_path
from .tenant_overrides import (
    EXPOSED_TENANT_OVERRIDE_KEYS,
    TenantOverrideAuditEvent,
    TenantParameterOverride,
    create_or_update_tenant_override,
    load_tenant_override,
    pause_tenant_override,
    read_tenant_override_audit_events,
    resolve_effective_parameters,
    revoke_tenant_override,
    tenant_override_audit_path,
    tenant_override_path,
)

_LIFT_CLI_FLAGS: tuple[tuple[str, str], ...] = (
    ("--fraud-risk-floor-lift", "fraud_risk_floor_lift"),
    ("--attachment-risk-floor-lift", "attachment_risk_floor_lift"),
    ("--url-obfuscation-floor-lift", "url_obfuscation_floor_lift"),
)


def _approval_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--reason",
        required=True,
        help="Human-readable reason recorded in the override and audit trail.",
    )
    parser.add_argument(
        "--requested-by",
        required=True,
        help="Operator id requesting the change (must differ from --approved-by).",
    )
    parser.add_argument(
        "--approved-by",
        required=True,
        help="Operator id approving the change (must differ from --requested-by).",
    )


def _add_lift_arguments(parser: argparse.ArgumentParser) -> None:
    for flag, dest in _LIFT_CLI_FLAGS:
        parser.add_argument(
            flag,
            dest=dest,
            type=int,
            default=None,
            metavar="N",
            help=f"Override value for {dest} (integer 0–25). At least one lift required.",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tenant_override_operator",
        description=(
            "Operator tooling for per-tenant Phase 1.4 sensitivity lift overrides."
        ),
    )
    parser.add_argument(
        "--blackboard-root",
        type=Path,
        required=True,
        help="Blackboard root directory (contains production_state/ for the tenant).",
    )
    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Production tenant id (for example tenant_demo).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help=(
            "Output format for read commands (default: text). "
            "`markdown` is a dedicated client-shareable format for the "
            "`report` subcommand; other read subcommands treat it as `text`."
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser(
        "create",
        help="Create or replace the active override for one tenant.",
    )
    _approval_arguments(create)
    _add_lift_arguments(create)
    create.add_argument(
        "--expires-at",
        type=str,
        default=None,
        help="Optional ISO-8601 expiry timestamp (timezone-aware).",
    )

    for name, help_text, handler in (
        ("pause", "Pause an existing override without deleting audit history.", None),
        ("revoke", "Revoke an existing override.", None),
    ):
        cmd = subparsers.add_parser(name, help=help_text)
        _approval_arguments(cmd)

    effective = subparsers.add_parser(
        "effective",
        help="Review signed policy parameters, override state, and effective values.",
    )
    effective.add_argument(
        "--at",
        type=str,
        default=None,
        help="Optional ISO-8601 evaluation time for expiry checks (default: now UTC).",
    )

    subparsers.add_parser(
        "audit",
        help="Inspect append-only override audit events for one tenant.",
    )

    subparsers.add_parser(
        "show",
        help="Show the current on-disk override record (if any).",
    )

    report = subparsers.add_parser(
        "report",
        help=(
            "Build an MSP-shareable effective-parameter report (signed policy + "
            "tenant override + provenance + recent audit events)."
        ),
    )
    report.add_argument(
        "--at",
        type=str,
        default=None,
        help="Optional ISO-8601 evaluation time for expiry checks (default: now UTC).",
    )
    report.add_argument(
        "--audit-limit",
        type=int,
        default=DEFAULT_AUDIT_LIMIT,
        help=(
            f"Number of most-recent audit events to include "
            f"(default: {DEFAULT_AUDIT_LIMIT}; 0 to omit)."
        ),
    )
    report.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional file path to write the rendered report to (in addition to stdout).",
    )

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    blackboard_root: Path = args.blackboard_root
    tenant_id: str = args.tenant_id

    try:
        if args.command == "create":
            return _cmd_create(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "pause":
            return _cmd_pause(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "revoke":
            return _cmd_revoke(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "effective":
            return _cmd_effective(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "audit":
            return _cmd_audit(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "show":
            return _cmd_show(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
        if args.command == "report":
            return _cmd_report(args, blackboard_root=blackboard_root, tenant_id=tenant_id)
    except GovernanceError as exc:
        _emit_error(str(exc), fmt=args.format)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


def _cmd_create(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    parameters = _collect_lift_parameters(args)
    if not parameters:
        raise GovernanceError(
            "at least one Phase 1.4 lift override is required "
            f"({', '.join(sorted(EXPOSED_TENANT_OVERRIDE_KEYS))})"
        )
    expires_at = _parse_optional_at(args.expires_at, field_name="expires_at")
    override = create_or_update_tenant_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        parameters=parameters,
        reason=args.reason,
        requested_by=args.requested_by,
        approved_by=args.approved_by,
        expires_at=expires_at,
        source="tenant_override_operator",
    )
    _print_create_result(override, fmt=args.format)
    return 0


def _cmd_pause(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    override = pause_tenant_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        reason=args.reason,
        requested_by=args.requested_by,
        approved_by=args.approved_by,
        source="tenant_override_operator",
    )
    _print_transition_result("paused", override, fmt=args.format)
    return 0


def _cmd_revoke(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    override = revoke_tenant_override(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        reason=args.reason,
        requested_by=args.requested_by,
        approved_by=args.approved_by,
        source="tenant_override_operator",
    )
    _print_transition_result("revoked", override, fmt=args.format)
    return 0


def _cmd_effective(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    now = _parse_optional_at(args.at, field_name="at") or datetime.now(timezone.utc)
    policy_state = load_state(state_path(blackboard_root, tenant_id))
    policy_parameters = dict(policy_state.parameters)
    override_path = tenant_override_path(blackboard_root, tenant_id)
    override = _safe_load_override(override_path)
    effective = resolve_effective_parameters(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        policy_parameters=policy_parameters,
        now=now,
    )
    payload = _effective_payload(
        tenant_id=tenant_id,
        evaluated_at=now,
        policy_version=policy_state.active_version,
        policy_parameters=policy_parameters,
        override=override,
        effective_parameters=effective,
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_effective_text(payload))
    return 0


def _cmd_audit(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    path = tenant_override_audit_path(blackboard_root, tenant_id)
    events = read_tenant_override_audit_events(path)
    if args.format == "json":
        print(
            json.dumps(
                [_audit_event_dict(event) for event in events],
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not events:
        print(f"No override audit events for tenant {tenant_id!r}.")
        return 0
    for event in events:
        print(_format_audit_line(event))
    return 0


def _cmd_show(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    path = tenant_override_path(blackboard_root, tenant_id)
    override = _safe_load_override(path)
    if override is None:
        if args.format == "json":
            print(json.dumps({"tenant_id": tenant_id, "override": None}, indent=2))
        else:
            print(f"No override on disk for tenant {tenant_id!r}.")
        return 0
    if args.format == "json":
        print(json.dumps(_override_dict(override), indent=2, sort_keys=True))
    else:
        print(_format_override_text(override))
    return 0


def _cmd_report(
    args: argparse.Namespace,
    *,
    blackboard_root: Path,
    tenant_id: str,
) -> int:
    now = _parse_optional_at(args.at, field_name="at") or datetime.now(timezone.utc)
    if args.audit_limit < 0:
        raise GovernanceError("--audit-limit must be non-negative")
    report = build_effective_parameters_report(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        now=now,
        audit_limit=args.audit_limit,
    )
    if args.format == "json":
        rendered = render_report_json(report)
    elif args.format == "markdown":
        rendered = render_report_markdown(report)
    else:
        rendered = render_report_text(report)
    print(rendered)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    return 0


def _collect_lift_parameters(args: argparse.Namespace) -> dict[str, int]:
    out: dict[str, int] = {}
    for _, dest in _LIFT_CLI_FLAGS:
        value = getattr(args, dest, None)
        if value is not None:
            out[dest] = value
    return out


def _parse_optional_at(raw: str | None, *, field_name: str) -> datetime | None:
    if raw is None:
        return None
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise GovernanceError(f"{field_name} must be an ISO datetime string") from exc
    if parsed.tzinfo is None:
        raise GovernanceError(f"{field_name} must be timezone-aware")
    return parsed


def _safe_load_override(path: Path) -> TenantParameterOverride | None:
    if not path.exists():
        return None
    try:
        return load_tenant_override(path)
    except GovernanceError:
        return None


def _effective_payload(
    *,
    tenant_id: str,
    evaluated_at: datetime,
    policy_version: str,
    policy_parameters: dict[str, Any],
    override: TenantParameterOverride | None,
    effective_parameters: dict[str, Any],
) -> dict[str, Any]:
    lift_slice = {key: policy_parameters.get(key) for key in sorted(EXPOSED_TENANT_OVERRIDE_KEYS)}
    effective_slice = {
        key: effective_parameters.get(key) for key in sorted(EXPOSED_TENANT_OVERRIDE_KEYS)
    }
    return {
        "tenant_id": tenant_id,
        "evaluated_at": evaluated_at.isoformat(),
        "policy_active_version": policy_version,
        "signed_policy_lift_parameters": lift_slice,
        "override": None if override is None else _override_dict(override),
        "override_applied": _override_is_applied(override, evaluated_at=evaluated_at),
        "effective_lift_parameters": effective_slice,
    }


def _override_is_applied(
    override: TenantParameterOverride | None,
    *,
    evaluated_at: datetime,
) -> bool:
    if override is None:
        return False
    if override.status != "active":
        return False
    if override.expires_at is not None and override.expires_at <= evaluated_at:
        return False
    return True


def _override_dict(override: TenantParameterOverride) -> dict[str, Any]:
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


def _audit_event_dict(event: TenantOverrideAuditEvent) -> dict[str, Any]:
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


def _format_effective_text(payload: dict[str, Any]) -> str:
    lines = [
        f"Tenant: {payload['tenant_id']}",
        f"Evaluated at: {payload['evaluated_at']}",
        f"Policy version: {payload['policy_active_version']}",
        "",
        "Signed policy lift parameters:",
    ]
    lines.extend(_format_lift_lines(payload["signed_policy_lift_parameters"]))
    lines.append("")
    override = payload["override"]
    if override is None:
        lines.append("Override: (none on disk)")
    else:
        lines.append(f"Override status: {override['status']}")
        lines.append(f"Override reason: {override['reason']}")
        lines.append("Override lift parameters:")
        lines.extend(_format_lift_lines(override["parameters"]))
        if override["expires_at"]:
            lines.append(f"Override expires at: {override['expires_at']}")
    lines.append("")
    lines.append(
        f"Override applied for scoring: {'yes' if payload['override_applied'] else 'no'}"
    )
    lines.append("Effective lift parameters:")
    lines.extend(_format_lift_lines(payload["effective_lift_parameters"]))
    return "\n".join(lines)


def _format_lift_lines(parameters: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in sorted(EXPOSED_TENANT_OVERRIDE_KEYS):
        value = parameters.get(key)
        if value is None:
            lines.append(f"  {key}: (unset)")
        else:
            lines.append(f"  {key}: {value}")
    return lines


def _format_override_text(override: TenantParameterOverride) -> str:
    payload = _override_dict(override)
    lines = [
        f"Tenant: {payload['tenant_id']}",
        f"Status: {payload['status']}",
        f"Reason: {payload['reason']}",
        f"Requested by: {payload['requested_by']}",
        f"Approved by: {payload['approved_by']}",
        f"Created at: {payload['created_at']}",
    ]
    if payload["expires_at"]:
        lines.append(f"Expires at: {payload['expires_at']}")
    lines.append("Parameters:")
    lines.extend(_format_lift_lines(payload["parameters"]))
    return "\n".join(lines)


def _format_audit_line(event: TenantOverrideAuditEvent) -> str:
    return (
        f"{event.timestamp.isoformat()}  {event.event_type}  "
        f"source={event.source}  "
        f"requester={event.requested_by}  approver={event.approved_by}  "
        f"before={event.parameters_before}  after={event.parameters_after}  "
        f"reason={event.reason!r}"
    )


def _print_create_result(override: TenantParameterOverride, *, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(_override_dict(override), indent=2, sort_keys=True))
        return
    print("Override saved.")
    print(_format_override_text(override))


def _print_transition_result(
    verb: str,
    override: TenantParameterOverride,
    *,
    fmt: str,
) -> None:
    if fmt == "json":
        print(json.dumps({"status": verb, "override": _override_dict(override)}, indent=2))
        return
    print(f"Override {verb}.")
    print(_format_override_text(override))


def _emit_error(message: str, *, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps({"error": message}, indent=2), file=sys.stderr)
    else:
        print(f"error: {message}", file=sys.stderr)


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
