"""Tests for PayrollDiversionAgent — ES1 detect-not-enact."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
)
from core.control_plane.enact_gate import EnactmentBlockedError
from core.orchestrator import MissionContext, RouteContext, submit_email_inbound
from core.orchestrator.payroll_diversion_agent import (
    PAYROLL_DIVERSION_AGENT_ID,
    PayrollDiversionAgent,
)
from core.orchestrator.registry import build_default_registry
from core.scoring.payroll_diversion_detector import PAYROLL_DIVERSION_PATTERN

_INGEST_AGENT_ID = "ingest_payroll_001"


def _agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=PAYROLL_DIVERSION_AGENT_ID,
        display_name="Payroll Diversion Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=2,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _ingest_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=_INGEST_AGENT_ID,
        display_name="Ingest",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.EMAIL_INBOUND},
    )


def _route_ctx(tmp_path: Path) -> RouteContext:
    registry = {e.agent_id: e for e in (_agent_entry(), _ingest_entry())}
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=registry)


def _seed_email(route_ctx: RouteContext, **kwargs) -> MissionContext:
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender=kwargs.get("sender", "ceo.personal@outlook.example"),
        recipient=kwargs.get("recipient", "payroll@northstar-customer.example"),
        subject=kwargs.get("subject", "Payroll update"),
        body_plain=kwargs.get(
            "body_plain",
            "Please update the direct deposit before the next payroll run.",
        ),
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id="tenant_payroll",
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    return MissionContext(
        tenant_id="tenant_payroll",
        inputs_digest="c" * 64,
        source_record_id=result.record.record_id,
    )


def test_agent_emits_observation_facts_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = PayrollDiversionAgent(
        blackboard_root=route_ctx.blackboard_root,
        payroll_mailbox_roster=("payroll@",),
    )
    context = _seed_email(route_ctx)
    contribution = agent.analyze(context)
    assert contribution.agent_id == PAYROLL_DIVERSION_AGENT_ID
    assert contribution.layer == 2
    forbidden = {"low_risk", "safe", "suppression_applied", "approval_recommended"}
    assert not forbidden.intersection(set(contribution.observed_facts))


def test_enactment_blocked_from_es1_agent(tmp_path):
    agent = PayrollDiversionAgent(
        blackboard_root=tmp_path / "blackboard",
        payroll_mailbox_roster=("payroll@",),
    )
    with pytest.raises(EnactmentBlockedError):
        agent.enact_block()
    with pytest.raises(EnactmentBlockedError):
        agent.enact_contain()


def test_not_in_default_registry():
    assert PAYROLL_DIVERSION_AGENT_ID not in build_default_registry()


def test_ei002_class_email_emits_pattern(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = PayrollDiversionAgent(
        blackboard_root=route_ctx.blackboard_root,
        payroll_mailbox_roster=("payroll@",),
        employee_token_roster=("jordan_lee",),
    )
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="ceo.personal@outlook.example",
        recipient="payroll@northstar-customer.example",
        subject="Payroll update before next run",
        body_plain=(
            "Please update the direct deposit for jordan_lee before the next payroll run."
        ),
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id="tenant_payroll",
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    context = MissionContext(
        tenant_id="tenant_payroll",
        inputs_digest="d" * 64,
        source_record_id=result.record.record_id,
    )
    contribution = agent.analyze(context)
    assert PAYROLL_DIVERSION_PATTERN in contribution.observed_facts


def test_lh002_class_email_emits_no_pattern(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = PayrollDiversionAgent(blackboard_root=route_ctx.blackboard_root)
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="payroll@northstar-customer.example",
        recipient="staff@northstar-customer.example",
        subject="Payroll calendar notice",
        body_plain=(
            "Payroll cutoff dates for June are attached. "
            "This is not a direct-deposit change request."
        ),
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id="tenant_payroll",
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    context = MissionContext(
        tenant_id="tenant_payroll",
        inputs_digest="e" * 64,
        source_record_id=result.record.record_id,
    )
    contribution = agent.analyze(context)
    assert PAYROLL_DIVERSION_PATTERN not in contribution.observed_facts


def test_missing_source_record_id_fails_closed(tmp_path):
    agent = PayrollDiversionAgent(blackboard_root=tmp_path / "blackboard")
    context = MissionContext(tenant_id="tenant_payroll", inputs_digest="f" * 64)
    with pytest.raises(GovernanceError):
        agent.analyze(context)
