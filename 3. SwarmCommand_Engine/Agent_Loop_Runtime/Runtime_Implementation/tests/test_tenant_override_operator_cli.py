"""Operator CLI tests for Phase 2.1 tenant override tooling."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.production_state import (
    TENANT_OVERRIDE_CREATED,
    TENANT_OVERRIDE_PAUSED,
    TENANT_OVERRIDE_REVOKED,
    load_tenant_override,
    read_tenant_override_audit_events,
    save_state,
    state_path,
    tenant_override_audit_path,
    tenant_override_path,
)
from core.production_state.state import ProductionPolicyState
from core.production_state.tenant_override_operator import run

TENANT = "tenant_demo"
NOW = datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc)


def _blackboard_root(tmp_path: Path) -> Path:
    return tmp_path / "blackboard"


def _base_argv(tmp_path: Path) -> list[str]:
    return ["--blackboard-root", str(_blackboard_root(tmp_path)), "--tenant-id", TENANT]


def _seed_policy(tmp_path: Path) -> None:
    root = _blackboard_root(tmp_path)
    save_state(
        state_path(root, TENANT),
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


def test_cli_create_writes_override_and_audit(tmp_path, capsys):
    argv = [
        *_base_argv(tmp_path),
        "create",
        "--reason",
        "finance pilot",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_b",
        "--fraud-risk-floor-lift",
        "8",
    ]
    assert run(argv) == 0
    out = capsys.readouterr().out
    assert "Override saved." in out
    assert "fraud_risk_floor_lift: 8" in out

    root = _blackboard_root(tmp_path)
    loaded = load_tenant_override(tenant_override_path(root, TENANT))
    assert loaded is not None
    assert loaded.parameters == {"fraud_risk_floor_lift": 8}
    events = read_tenant_override_audit_events(tenant_override_audit_path(root, TENANT))
    assert events[-1].event_type == TENANT_OVERRIDE_CREATED
    assert events[-1].source == "tenant_override_operator"


def test_cli_create_rejects_self_approval(tmp_path, capsys):
    argv = [
        *_base_argv(tmp_path),
        "create",
        "--reason",
        "bad",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_a",
        "--fraud-risk-floor-lift",
        "5",
    ]
    assert run(argv) == 1
    assert "separate requested_by and approved_by" in capsys.readouterr().err


def test_cli_create_requires_at_least_one_lift(tmp_path, capsys):
    argv = [
        *_base_argv(tmp_path),
        "create",
        "--reason",
        "empty",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_b",
    ]
    assert run(argv) == 1
    assert "at least one" in capsys.readouterr().err.lower()


def test_cli_pause_and_revoke_transition_override(tmp_path, capsys):
    root = _blackboard_root(tmp_path)
    create_argv = [
        *_base_argv(tmp_path),
        "create",
        "--reason",
        "initial",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_b",
        "--fraud-risk-floor-lift",
        "6",
    ]
    assert run(create_argv) == 0
    capsys.readouterr()

    pause_argv = [
        *_base_argv(tmp_path),
        "pause",
        "--reason",
        "hold during review",
        "--requested-by",
        "operator_c",
        "--approved-by",
        "operator_d",
    ]
    assert run(pause_argv) == 0
    assert "Override paused." in capsys.readouterr().out
    paused = load_tenant_override(tenant_override_path(root, TENANT))
    assert paused is not None and paused.status == "paused"
    events = read_tenant_override_audit_events(tenant_override_audit_path(root, TENANT))
    assert events[-1].event_type == TENANT_OVERRIDE_PAUSED

    revoke_argv = [
        *_base_argv(tmp_path),
        "revoke",
        "--reason",
        "client offboarding",
        "--requested-by",
        "operator_e",
        "--approved-by",
        "operator_f",
    ]
    assert run(revoke_argv) == 0
    assert "Override revoked." in capsys.readouterr().out
    revoked = load_tenant_override(tenant_override_path(root, TENANT))
    assert revoked is not None and revoked.status == "revoked"
    events = read_tenant_override_audit_events(tenant_override_audit_path(root, TENANT))
    assert events[-1].event_type == TENANT_OVERRIDE_REVOKED


def test_cli_effective_reports_policy_override_and_effective(tmp_path, capsys):
    _seed_policy(tmp_path)
    create_argv = [
        *_base_argv(tmp_path),
        "create",
        "--reason",
        "pilot",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_b",
        "--fraud-risk-floor-lift",
        "9",
        "--expires-at",
        (NOW + timedelta(days=7)).isoformat(),
    ]
    assert run(create_argv) == 0
    capsys.readouterr()

    effective_argv = [
        *_base_argv(tmp_path),
        "--format",
        "json",
        "effective",
        "--at",
        NOW.isoformat(),
    ]
    assert run(effective_argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["policy_active_version"] == "v7"
    assert payload["signed_policy_lift_parameters"]["fraud_risk_floor_lift"] == 3
    assert payload["override"]["parameters"]["fraud_risk_floor_lift"] == 9
    assert payload["override_applied"] is True
    assert payload["effective_lift_parameters"]["fraud_risk_floor_lift"] == 9


def test_cli_effective_shows_not_applied_when_paused(tmp_path, capsys):
    _seed_policy(tmp_path)
    assert run(
        [
            *_base_argv(tmp_path),
            "create",
            "--reason",
            "pilot",
            "--requested-by",
            "operator_a",
            "--approved-by",
            "operator_b",
            "--fraud-risk-floor-lift",
            "9",
        ]
    ) == 0
    capsys.readouterr()
    assert run(
        [
            *_base_argv(tmp_path),
            "pause",
            "--reason",
            "hold",
            "--requested-by",
            "operator_c",
            "--approved-by",
            "operator_d",
        ]
    ) == 0
    capsys.readouterr()

    assert run([*_base_argv(tmp_path), "--format", "json", "effective"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["override_applied"] is False
    assert payload["effective_lift_parameters"]["fraud_risk_floor_lift"] == 3


def test_cli_audit_lists_events(tmp_path, capsys):
    assert run(
        [
            *_base_argv(tmp_path),
            "create",
            "--reason",
            "one",
            "--requested-by",
            "operator_a",
            "--approved-by",
            "operator_b",
            "--url-obfuscation-floor-lift",
            "4",
        ]
    ) == 0
    capsys.readouterr()

    assert run([*_base_argv(tmp_path), "audit"]) == 0
    out = capsys.readouterr().out
    assert TENANT_OVERRIDE_CREATED in out
    assert "url_obfuscation_floor_lift" in out or "parameters_after" in out

    assert run([*_base_argv(tmp_path), "--format", "json", "audit"]) == 0
    events = json.loads(capsys.readouterr().out)
    assert len(events) == 1
    assert events[0]["event_type"] == TENANT_OVERRIDE_CREATED


def test_cli_show_reports_missing_override(tmp_path, capsys):
    assert run([*_base_argv(tmp_path), "show"]) == 0
    assert "No override on disk" in capsys.readouterr().out


def test_cli_pause_without_override_fails(tmp_path, capsys):
    argv = [
        *_base_argv(tmp_path),
        "pause",
        "--reason",
        "nothing to pause",
        "--requested-by",
        "operator_a",
        "--approved-by",
        "operator_b",
    ]
    assert run(argv) == 1
    assert "does not exist" in capsys.readouterr().err
