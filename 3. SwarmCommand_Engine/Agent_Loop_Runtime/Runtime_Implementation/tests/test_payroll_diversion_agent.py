"""Tests for PayrollDiversionAgent — ES1 detect-not-enact."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from core.blackboard import (
    AgentContributionPayload,
    AgentRegistryEntry,
    AgentRole,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.orchestrator import Agent, MissionContext, RouteContext, submit_email_inbound
from core.orchestrator.agent_contract import AgentContribution
from core.orchestrator.payroll_diversion_agent import (
    PAYROLL_DIVERSION_AGENT_ID,
    PayrollDiversionAgent,
)
from core.orchestrator.registry import build_default_registry
from core.scoring.executive_impersonation_detector import (
    EXECUTIVE_IMPERSONATION_PATTERN_FLAG,
)
from core.scoring.payroll_diversion_detector import PAYROLL_DIVERSION_PATTERN

_INGEST_AGENT_ID = "ingest_payroll_001"
TENANT_A = "tenant_payroll_a"
TENANT_B = "tenant_payroll_b"


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


def _agent(
    route_ctx: RouteContext,
    *,
    tenant_id: str = TENANT_A,
    payroll_mailbox_roster: tuple[str, ...] = ("payroll@",),
    employee_token_roster: tuple[str, ...] = (),
) -> PayrollDiversionAgent:
    return PayrollDiversionAgent(
        blackboard_root=route_ctx.blackboard_root,
        payroll_mailbox_roster=payroll_mailbox_roster,
        employee_token_roster=employee_token_roster,
        tenant_id=tenant_id,
    )


def _seed_email(
    route_ctx: RouteContext,
    *,
    tenant_id: str = TENANT_A,
    **kwargs,
) -> MissionContext:
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
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest="c" * 64,
        source_record_id=result.record.record_id,
    )


def test_agent_satisfies_agent_protocol(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    assert isinstance(agent, Agent)


def test_agent_emits_observation_facts_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    context = _seed_email(route_ctx)
    contribution = agent.analyze(context)
    assert contribution.agent_id == PAYROLL_DIVERSION_AGENT_ID
    assert contribution.layer == 2
    forbidden = {"low_risk", "safe", "suppression_applied", "approval_recommended"}
    assert not forbidden.intersection(set(contribution.observed_facts))


def test_not_in_default_registry():
    assert PAYROLL_DIVERSION_AGENT_ID not in build_default_registry()


def test_challenge_returns_none(tmp_path):
    agent = _agent(_route_ctx(tmp_path))
    assert agent.challenge(()) is None


def test_ei002_class_email_emits_pattern(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx, employee_token_roster=("jordan_lee",))
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
        tenant_id=TENANT_A,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    context = MissionContext(
        tenant_id=TENANT_A,
        inputs_digest="d" * 64,
        source_record_id=result.record.record_id,
    )
    contribution = agent.analyze(context)
    assert PAYROLL_DIVERSION_PATTERN in contribution.observed_facts


def test_lh002_class_email_emits_no_pattern(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx, payroll_mailbox_roster=())
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
        tenant_id=TENANT_A,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    context = MissionContext(
        tenant_id=TENANT_A,
        inputs_digest="e" * 64,
        source_record_id=result.record.record_id,
    )
    contribution = agent.analyze(context)
    assert PAYROLL_DIVERSION_PATTERN not in contribution.observed_facts


def test_missing_source_record_id_fails_closed(tmp_path):
    agent = PayrollDiversionAgent(blackboard_root=tmp_path / "blackboard")
    context = MissionContext(tenant_id=TENANT_A, inputs_digest="f" * 64)
    with pytest.raises(GovernanceError):
        agent.analyze(context)


def test_tenant_isolation_rejects_mismatched_context(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx, tenant_id=TENANT_A)
    context = _seed_email(route_ctx, tenant_id=TENANT_B)
    with pytest.raises(GovernanceError, match="does not match"):
        agent.analyze(context)


def test_no_vendor_baseline_store_calls(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    context = _seed_email(route_ctx)
    with patch(
        "core.scoring.financial_state_ledger.assess_financial_state_delta"
    ) as mock_assess:
        agent.analyze(context)
        mock_assess.assert_not_called()


def test_no_executive_impersonation_pattern_emission(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    context = _seed_email(
        route_ctx,
        body_plain=(
            "Please update the direct deposit for jordan_lee before the next payroll run."
        ),
    )
    contribution = agent.analyze(context)
    assert EXECUTIVE_IMPERSONATION_PATTERN_FLAG not in contribution.observed_facts


def test_contribution_persists_to_blackboard(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    context = _seed_email(
        route_ctx,
        body_plain="Please update direct deposit before the next payroll run.",
    )
    contribution = agent.analyze(context)
    write = agent.persist_contribution(route_ctx, context, contribution)
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    persisted = [
        record
        for record in read_records(write.path)
        if record.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.observed_facts == list(contribution.observed_facts)


def test_contribution_is_agent_contribution_type(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(route_ctx)
    contribution = agent.analyze(_seed_email(route_ctx))
    assert isinstance(contribution, AgentContribution)
