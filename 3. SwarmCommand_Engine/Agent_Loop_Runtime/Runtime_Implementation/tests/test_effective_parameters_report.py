"""Phase 2.1 effective-parameter report tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.production_state import (
    EXPOSED_TENANT_OVERRIDE_KEYS,
    EffectiveParametersReport,
    ProductionPolicyState,
    build_effective_parameters_report,
    create_or_update_tenant_override,
    pause_tenant_override,
    render_report_json,
    render_report_markdown,
    render_report_text,
    revoke_tenant_override,
    save_state,
    state_path,
    tenant_override_path,
)
from core.production_state.tenant_override_operator import run

TENANT = "tenant_demo"
NOW = datetime(2026, 5, 22, 12, 0, tzinfo=timezone.utc)


def _blackboard_root(tmp_path: Path) -> Path:
    return tmp_path / "blackboard"


def _base_argv(tmp_path: Path) -> list[str]:
    return ["--blackboard-root", str(_blackboard_root(tmp_path)), "--tenant-id", TENANT]


def _seed_policy(tmp_path: Path) -> None:
    save_state(
        state_path(_blackboard_root(tmp_path), TENANT),
        ProductionPolicyState(
            active_version="v7",
            parameters={
                "confidence_boost": 0.2,
                "fraud_risk_floor_lift": 3,
                "attachment_risk_floor_lift": 4,
                "url_obfuscation_floor_lift": 2,
            },
        ),
    )


def _seed_active_override(tmp_path: Path) -> None:
    create_or_update_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 9},
        reason="finance-heavy pilot",
        requested_by="operator_a",
        approved_by="operator_b",
        now=NOW,
    )


def _entry(report: EffectiveParametersReport, key: str):
    return next(entry for entry in report.entries if entry.key == key)


def test_report_with_no_override_uses_signed_policy_provenance(tmp_path):
    _seed_policy(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    assert report.tenant_id == TENANT
    assert report.policy_active_version == "v7"
    assert report.override_summary is None
    assert report.override_applied is False
    assert report.override_not_applied_reason is None
    assert {entry.key for entry in report.entries} == set(EXPOSED_TENANT_OVERRIDE_KEYS)
    for entry in report.entries:
        if entry.key == "vendor_baseline_ttl_days":
            assert entry.source == "default"
            assert entry.value is None
        else:
            assert entry.source == "signed_policy"
        assert entry.override_value is None
    assert _entry(report, "fraud_risk_floor_lift").value == 3
    assert _entry(report, "fraud_risk_floor_lift").signed_policy_value == 3


def test_report_with_active_override_marks_overlay_keys_as_tenant_override(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    assert report.override_applied is True
    assert report.override_not_applied_reason is None
    fraud_entry = _entry(report, "fraud_risk_floor_lift")
    assert fraud_entry.source == "tenant_override"
    assert fraud_entry.value == 9
    assert fraud_entry.signed_policy_value == 3
    assert fraud_entry.override_value == 9
    attachment_entry = _entry(report, "attachment_risk_floor_lift")
    assert attachment_entry.source == "signed_policy"
    assert attachment_entry.value == 4
    assert attachment_entry.override_value is None


def test_report_with_paused_override_includes_not_applied_reason(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    pause_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        reason="hold during review",
        requested_by="operator_c",
        approved_by="operator_d",
        now=NOW + timedelta(hours=1),
    )
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW + timedelta(hours=2),
    )
    assert report.override_applied is False
    assert report.override_not_applied_reason == "override is paused"
    assert report.override_summary is not None
    assert report.override_summary.status == "paused"
    assert _entry(report, "fraud_risk_floor_lift").source == "signed_policy"
    assert _entry(report, "fraud_risk_floor_lift").value == 3


def test_report_with_revoked_override_includes_not_applied_reason(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    revoke_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        reason="pilot ended",
        requested_by="operator_c",
        approved_by="operator_d",
        now=NOW + timedelta(hours=1),
    )
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW + timedelta(hours=2),
    )
    assert report.override_applied is False
    assert report.override_not_applied_reason == "override is revoked"


def test_report_with_expired_override_includes_not_applied_reason(tmp_path):
    _seed_policy(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 9},
        reason="short pilot",
        requested_by="operator_a",
        approved_by="operator_b",
        expires_at=NOW + timedelta(hours=1),
        now=NOW,
    )
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW + timedelta(hours=2),
    )
    assert report.override_applied is False
    assert report.override_not_applied_reason is not None
    assert "expired" in report.override_not_applied_reason
    assert _entry(report, "fraud_risk_floor_lift").source == "signed_policy"


def test_report_with_invalid_override_file_falls_back_and_explains(tmp_path):
    _seed_policy(tmp_path)
    path = tenant_override_path(_blackboard_root(tmp_path), TENANT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json at all", encoding="utf-8")
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    assert report.override_applied is False
    assert report.override_not_applied_reason is not None
    assert "override file is invalid" in report.override_not_applied_reason
    assert _entry(report, "fraud_risk_floor_lift").source == "signed_policy"


def test_report_recent_audit_events_are_reverse_chronological_and_limited(tmp_path):
    _seed_policy(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 6},
        reason="first",
        requested_by="operator_a",
        approved_by="operator_b",
        now=NOW,
    )
    create_or_update_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 9},
        reason="second",
        requested_by="operator_c",
        approved_by="operator_d",
        now=NOW + timedelta(hours=1),
    )
    pause_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        reason="hold",
        requested_by="operator_e",
        approved_by="operator_f",
        now=NOW + timedelta(hours=2),
    )
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW + timedelta(hours=3),
        audit_limit=2,
    )
    assert len(report.recent_audit_events) == 2
    timestamps = [event.timestamp for event in report.recent_audit_events]
    assert timestamps[0] > timestamps[1]
    assert report.recent_audit_events[0].event_type == "tenant_parameter_override_paused"


def test_report_audit_limit_zero_omits_events(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
        audit_limit=0,
    )
    assert report.recent_audit_events == []


def test_report_with_no_policy_and_no_override_returns_default_provenance(tmp_path):
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    assert report.policy_active_version == "v0"
    for entry in report.entries:
        assert entry.source == "default"
        assert entry.value is None
        assert entry.signed_policy_value is None
        assert entry.override_value is None
    assert report.override_summary is None
    assert report.override_applied is False


def test_render_report_text_contains_provenance_per_key(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    text = render_report_text(report)
    assert "Effective Parameter Report" in text
    assert "fraud_risk_floor_lift" in text
    assert "source=tenant_override" in text
    assert "source=signed_policy" in text
    assert "Override applied for scoring: yes" in text


def test_render_report_markdown_has_table_and_audit_section(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    md = render_report_markdown(report)
    assert md.startswith("# NorthStar Inbox Shield — Effective Parameter Report")
    assert "| Parameter | Effective Value | Source |" in md
    assert "`fraud_risk_floor_lift`" in md
    assert "`tenant_override`" in md
    assert "## Tenant Override" in md
    assert "## Recent Override Audit Events" in md
    assert "Override applied for scoring:** yes" in md
    assert "Other signed policy parameters" in md
    assert "`confidence_boost`" in md


def test_render_report_markdown_notes_when_override_not_applied(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    pause_tenant_override(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        reason="hold",
        requested_by="operator_c",
        approved_by="operator_d",
        now=NOW + timedelta(hours=1),
    )
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW + timedelta(hours=2),
    )
    md = render_report_markdown(report)
    assert "Override applied for scoring:** no — override is paused" in md


def test_render_report_json_is_stable_and_round_trips(tmp_path):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    report = build_effective_parameters_report(
        blackboard_root=_blackboard_root(tmp_path),
        tenant_id=TENANT,
        now=NOW,
    )
    rendered = render_report_json(report)
    payload = json.loads(rendered)
    assert payload["tenant_id"] == TENANT
    assert payload["policy_active_version"] == "v7"
    assert payload["override_applied"] is True
    assert {entry["key"] for entry in payload["entries"]} == set(EXPOSED_TENANT_OVERRIDE_KEYS)
    fraud_entry = next(
        entry for entry in payload["entries"] if entry["key"] == "fraud_risk_floor_lift"
    )
    assert fraud_entry["source"] == "tenant_override"
    assert fraud_entry["value"] == 9
    assert fraud_entry["signed_policy_value"] == 3
    assert payload["recent_audit_events"][0]["event_type"] == "tenant_parameter_override_created"


def test_cli_report_subcommand_text_output(tmp_path, capsys):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    rc = run([*_base_argv(tmp_path), "report", "--at", NOW.isoformat()])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Effective Parameter Report" in out
    assert "source=tenant_override" in out


def test_cli_report_subcommand_markdown_output(tmp_path, capsys):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    rc = run(
        [
            *_base_argv(tmp_path),
            "--format",
            "markdown",
            "report",
            "--at",
            NOW.isoformat(),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert out.startswith("# NorthStar Inbox Shield — Effective Parameter Report")
    assert "| Parameter | Effective Value | Source |" in out


def test_cli_report_subcommand_json_output(tmp_path, capsys):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    rc = run(
        [
            *_base_argv(tmp_path),
            "--format",
            "json",
            "report",
            "--at",
            NOW.isoformat(),
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tenant_id"] == TENANT
    assert payload["override_applied"] is True


def test_cli_report_subcommand_writes_to_out_file(tmp_path, capsys):
    _seed_policy(tmp_path)
    _seed_active_override(tmp_path)
    out_path = tmp_path / "exports" / "tenant_demo_effective_report.md"
    rc = run(
        [
            *_base_argv(tmp_path),
            "--format",
            "markdown",
            "report",
            "--at",
            NOW.isoformat(),
            "--out",
            str(out_path),
        ]
    )
    assert rc == 0
    capsys.readouterr()
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# NorthStar Inbox Shield — Effective Parameter Report")
    assert content.endswith("\n")


def test_cli_report_rejects_negative_audit_limit(tmp_path, capsys):
    _seed_policy(tmp_path)
    rc = run(
        [
            *_base_argv(tmp_path),
            "report",
            "--audit-limit",
            "-1",
        ]
    )
    assert rc == 1
    assert "audit-limit" in capsys.readouterr().err
