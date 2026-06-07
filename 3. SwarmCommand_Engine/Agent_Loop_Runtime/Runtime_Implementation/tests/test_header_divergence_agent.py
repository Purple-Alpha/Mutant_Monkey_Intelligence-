"""End-to-end proof that the governed-agent contract holds on a REAL detector.

Wraps ``score_header_divergence`` as ``HeaderDivergenceAgent`` and runs the full
contract: seed an email on the Blackboard -> Commander dispatches the agent ->
``analyze`` reads the email and returns a real ``AgentContribution`` ->
contribution persists to the Blackboard via the registry-gated route -> the
Commander assembles a real ``DecisionEvidenceRecord`` with a real
``inputs_digest``.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
    validate_record_payload,
)
from core.blackboard.models import AgentContributionPayload, BlackboardRecord
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator.header_divergence_agent import (
    HEADER_DIVERGENCE_AGENT_ID,
    HeaderDivergenceAgent,
    digest_email,
)
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"


def _header_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=HEADER_DIVERGENCE_AGENT_ID,
        display_name="Header Divergence Agent",
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


def _registry() -> dict[str, AgentRegistryEntry]:
    return {e.agent_id: e for e in (_header_agent_entry(), _ingest_entry())}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    sender: str,
    headers: dict[str, str],
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender=sender,
        recipient="ap@buyer.example",
        subject="Invoice 8841 - updated remittance",
        body_plain="Please use the updated banking details for this invoice.",
        headers=headers,
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    return result.record.record_id, payload


def _mission_context(record_id, payload, *, tenant_id: str = "tenant_demo") -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest_email(payload),
        source_record_id=record_id,
    )


def _agent(route_ctx: RouteContext) -> HeaderDivergenceAgent:
    return HeaderDivergenceAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


def test_header_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_email_produces_divergence_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@attacker.example"},
    )
    commander = SwarmCommander(_registry())
    der = commander.run_case(_mission_context(record_id, payload), [_agent(route_ctx)])

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == HEADER_DIVERGENCE_AGENT_ID
    assert contribution.layer == 2
    assert contribution.observed_facts == ("from_reply_to_divergence",)
    assert der.disposition == "suspicious"
    # Real inputs_digest carried into the DER, not a placeholder.
    assert der.inputs_digest == digest_email(payload)
    assert len(der.inputs_digest) == 64


def test_known_good_email_produces_empty_facts_and_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        sender="news@m.vendor.example",
        headers={"Reply-To": "support@vendor.example"},  # subdomain vs root: not divergence
    )
    commander = SwarmCommander(_registry())
    der = commander.run_case(_mission_context(record_id, payload), [_agent(route_ctx)])

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        sender="billing@vendor.example",
        headers={
            "Reply-To": "billing@attacker.example",
            "Return-Path": "<bounce@attacker.example>",
        },
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    commander = SwarmCommander(_registry())
    der = commander.run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == HEADER_DIVERGENCE_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == HEADER_DIVERGENCE_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert "from_reply_to_divergence" in payload_back.observed_facts
    assert "from_return_path_divergence" in payload_back.observed_facts


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(None) is None  # type: ignore[arg-type]


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(
        route_ctx,
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@attacker.example"},
    )
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    # Seed an email, then point the context at a NON-email record (the email's
    # own contribution record) to prove the type guard fires.
    record_id, payload = _seed_email(
        route_ctx,
        sender="billing@vendor.example",
        headers={"Reply-To": "billing@attacker.example"},
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])
    contribution_write = agent.persist_contribution(route_ctx, context, der.contributions[0])

    misdirected = MissionContext(
        tenant_id="tenant_demo",
        inputs_digest="a" * 64,
        source_record_id=contribution_write.record.record_id,
    )
    with pytest.raises(GovernanceError, match="not an email_inbound record"):
        agent.analyze(misdirected)


def test_unauthorized_agent_cannot_write_contribution(tmp_path):
    # The ingest agent is only permitted EMAIL_INBOUND, so a contribution write
    # under its id is rejected by the registry gate.
    route_ctx = _route_ctx(tmp_path)
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id=_INGEST_AGENT_ID,
        layer=2,
        observed_facts=["from_reply_to_divergence"],
    )
    with pytest.raises(GovernanceError, match="cannot write this record type"):
        submit_agent_contribution(
            route_ctx,
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            source_agent=_INGEST_AGENT_ID,
            payload=payload,
        )


def test_digest_email_is_deterministic(tmp_path):
    payload = EmailInboundPayload(
        received_at=datetime(2026, 6, 7, tzinfo=timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        body_plain="hello",
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_agent_contribution_payload_round_trips_via_payload_models(tmp_path):
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.AGENT_CONTRIBUTION,
        source_agent=HEADER_DIVERGENCE_AGENT_ID,
        payload=AgentContributionPayload(
            case_id=uuid4(),
            inputs_digest="a" * 64,
            agent_id=HEADER_DIVERGENCE_AGENT_ID,
            layer=2,
            observed_facts=["from_reply_to_divergence"],
        ).model_dump(mode="json"),
    )
    parsed = validate_record_payload(record)
    assert isinstance(parsed, AgentContributionPayload)
    assert parsed.observed_facts == ["from_reply_to_divergence"]
