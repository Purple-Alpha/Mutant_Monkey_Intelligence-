"""Phase 2.1 per-tenant parameter override tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.blackboard import (
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.production import ProductionLoopConfig, ProductionSignal, run_production_cycle
from core.production_state import (
    EXPOSED_TENANT_OVERRIDE_KEYS,
    TENANT_OVERRIDE_CREATED,
    TENANT_OVERRIDE_EXPIRED,
    TENANT_OVERRIDE_IGNORED,
    TENANT_OVERRIDE_INVALID,
    TENANT_OVERRIDE_REVOKED,
    create_or_update_tenant_override,
    load_tenant_override,
    read_tenant_override_audit_events,
    resolve_effective_parameters,
    revoke_tenant_override,
    tenant_override_audit_path,
    tenant_override_path,
)
from core.scoring import EmailRiskScoringConfig

TENANT = "tenant_demo"


def _context(tmp_path: Path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _now() -> datetime:
    return datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc)


def _moderate_fraud_llm(system_prompt: str, user_prompt: str) -> str:
    return json.dumps(
        {
            "summary": "moderate fraud",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 55,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "medium",
                "vendor_fraud_score": 55,
                "wire_transfer_anomaly_score": 10,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 10,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "needs_review",
        }
    )


def _inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=_now(),
        sender="billing@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please review this vendor invoice.",
    )


def test_exposed_tenant_override_keys_are_only_approved_runtime_overrides():
    assert EXPOSED_TENANT_OVERRIDE_KEYS == frozenset(
        {
            "fraud_risk_floor_lift",
            "attachment_risk_floor_lift",
            "url_obfuscation_floor_lift",
            "vendor_baseline_ttl_days",
        }
    )
    assert "confidence_boost" not in EXPOSED_TENANT_OVERRIDE_KEYS


def test_create_override_writes_local_json_and_append_only_audit(tmp_path):
    route_context = _context(tmp_path)

    override = create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 8},
        reason="finance-heavy pilot",
        requested_by="operator_a",
        approved_by="operator_b",
        expires_at=_now() + timedelta(days=30),
        now=_now(),
    )

    assert override.parameters == {"fraud_risk_floor_lift": 8}
    loaded = load_tenant_override(tenant_override_path(route_context.blackboard_root, TENANT))
    assert loaded == override

    events = read_tenant_override_audit_events(
        tenant_override_audit_path(route_context.blackboard_root, TENANT)
    )
    assert [event.event_type for event in events] == [TENANT_OVERRIDE_CREATED]
    assert events[0].parameters_before == {}
    assert events[0].parameters_after == {"fraud_risk_floor_lift": 8}
    assert events[0].requested_by == "operator_a"
    assert events[0].approved_by == "operator_b"


def test_update_override_appends_updated_audit_event(tmp_path):
    route_context = _context(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 8},
        reason="initial",
        requested_by="operator_a",
        approved_by="operator_b",
        now=_now(),
    )

    updated = create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 10, "url_obfuscation_floor_lift": 5},
        reason="url pilot",
        requested_by="operator_c",
        approved_by="operator_d",
        now=_now() + timedelta(hours=1),
    )

    assert updated.parameters == {
        "fraud_risk_floor_lift": 10,
        "url_obfuscation_floor_lift": 5,
    }
    events = read_tenant_override_audit_events(
        tenant_override_audit_path(route_context.blackboard_root, TENANT)
    )
    assert [event.event_type for event in events] == [
        TENANT_OVERRIDE_CREATED,
        "tenant_parameter_override_updated",
    ]
    assert events[-1].parameters_before == {"fraud_risk_floor_lift": 8}
    assert events[-1].parameters_after == {
        "fraud_risk_floor_lift": 10,
        "url_obfuscation_floor_lift": 5,
    }


@pytest.mark.parametrize(
    "parameters",
    [
        {"confidence_boost": 0.1},
        {"fraud_risk_floor_lift": -1},
        {"fraud_risk_floor_lift": 26},
        {"fraud_risk_floor_lift": 1.5},
        {"fraud_risk_floor_lift": True},
    ],
)
def test_invalid_values_are_rejected_at_write_time_not_clamped(tmp_path, parameters):
    route_context = _context(tmp_path)

    with pytest.raises(GovernanceError):
        create_or_update_tenant_override(
            blackboard_root=route_context.blackboard_root,
            tenant_id=TENANT,
            parameters=parameters,
            reason="bad write",
            requested_by="operator_a",
            approved_by="operator_b",
            now=_now(),
        )

    assert not tenant_override_path(route_context.blackboard_root, TENANT).exists()


def test_override_write_requires_separate_requester_and_approver(tmp_path):
    route_context = _context(tmp_path)

    with pytest.raises(GovernanceError, match="separate requested_by and approved_by"):
        create_or_update_tenant_override(
            blackboard_root=route_context.blackboard_root,
            tenant_id=TENANT,
            parameters={"fraud_risk_floor_lift": 8},
            reason="self approval should fail",
            requested_by="operator_a",
            approved_by="operator_a",
            now=_now(),
        )


def test_effective_parameters_overlay_policy_state_per_tenant(tmp_path):
    route_context = _context(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id="tenant_a",
        parameters={"fraud_risk_floor_lift": 9},
        reason="tenant A tuning",
        requested_by="operator_a",
        approved_by="operator_b",
        now=_now(),
    )

    tenant_a = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id="tenant_a",
        policy_parameters={
            "confidence_boost": 0.2,
            "fraud_risk_floor_lift": 3,
            "attachment_risk_floor_lift": 4,
        },
        now=_now(),
    )
    tenant_b = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id="tenant_b",
        policy_parameters={"fraud_risk_floor_lift": 3},
        now=_now(),
    )

    assert tenant_a == {
        "confidence_boost": 0.2,
        "fraud_risk_floor_lift": 9,
        "attachment_risk_floor_lift": 4,
    }
    assert tenant_b == {"fraud_risk_floor_lift": 3}


def test_expired_override_is_ignored_and_audited(tmp_path):
    route_context = _context(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 9},
        reason="temporary tuning",
        requested_by="operator_a",
        approved_by="operator_b",
        expires_at=_now() - timedelta(seconds=1),
        now=_now() - timedelta(days=1),
    )

    effective = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        policy_parameters={"fraud_risk_floor_lift": 3},
        now=_now(),
    )

    assert effective == {"fraud_risk_floor_lift": 3}
    events = read_tenant_override_audit_events(
        tenant_override_audit_path(route_context.blackboard_root, TENANT)
    )
    assert events[-1].event_type == TENANT_OVERRIDE_EXPIRED


def test_revoked_override_is_ignored_and_audited(tmp_path):
    route_context = _context(tmp_path)
    create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 9},
        reason="initial",
        requested_by="operator_a",
        approved_by="operator_b",
        now=_now(),
    )
    revoke_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        reason="pilot ended",
        requested_by="operator_c",
        approved_by="operator_d",
        now=_now() + timedelta(hours=1),
    )

    effective = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        policy_parameters={"fraud_risk_floor_lift": 3},
        now=_now() + timedelta(hours=2),
    )

    assert effective == {"fraud_risk_floor_lift": 3}
    events = read_tenant_override_audit_events(
        tenant_override_audit_path(route_context.blackboard_root, TENANT)
    )
    assert [event.event_type for event in events] == [
        TENANT_OVERRIDE_CREATED,
        TENANT_OVERRIDE_REVOKED,
        TENANT_OVERRIDE_IGNORED,
    ]


def test_invalid_on_disk_override_is_ignored_and_audited(tmp_path):
    route_context = _context(tmp_path)
    path = tenant_override_path(route_context.blackboard_root, TENANT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not-json", encoding="utf-8")

    effective = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        policy_parameters={"fraud_risk_floor_lift": 3},
        now=_now(),
    )

    assert effective == {"fraud_risk_floor_lift": 3}
    events = read_tenant_override_audit_events(
        tenant_override_audit_path(route_context.blackboard_root, TENANT)
    )
    assert events[-1].event_type == TENANT_OVERRIDE_INVALID


def test_no_override_keeps_effective_parameters_byte_equal_to_policy_state(tmp_path):
    route_context = _context(tmp_path)
    policy = {
        "confidence_boost": 0.1,
        "fraud_risk_floor_lift": 3,
        "attachment_risk_floor_lift": 4,
    }

    effective = resolve_effective_parameters(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        policy_parameters=policy,
        now=_now(),
    )

    assert effective == policy
    assert effective is not policy


def test_production_loop_reads_tenant_override_for_scoring_lift(tmp_path):
    route_context = _context(tmp_path)
    submit_email_inbound(
        route_context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="email_ingest_001",
        payload=_inbound(),
    )
    create_or_update_tenant_override(
        blackboard_root=route_context.blackboard_root,
        tenant_id=TENANT,
        parameters={"fraud_risk_floor_lift": 8},
        reason="finance-heavy client",
        requested_by="operator_a",
        approved_by="operator_b",
        now=_now(),
    )

    result = run_production_cycle(
        route_context,
        tenant_id=TENANT,
        signal=ProductionSignal(
            source="mailbox",
            event_kind="email_received",
            subject="routine",
            sender_domain="client-example.ca",
        ),
        config=ProductionLoopConfig(
            apply_pending_policies_at_end_of_cycle=False,
            run_alert_subscriber_at_end_of_cycle=False,
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=EmailRiskScoringConfig(
                llm_client=_moderate_fraud_llm,
                production_tenant_id=TENANT,
            ),
        ),
    )

    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1
    production_records = read_records(
        blackboard_path(route_context.blackboard_root, Environment.PRODUCTION, TENANT)
    )
    analyses = [
        record
        for record in production_records
        if record.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    assert analyses[0].payload["risk_analysis"]["risk_score"] == 63
