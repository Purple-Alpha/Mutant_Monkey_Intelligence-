"""End-to-end proof that the governed-agent contract holds on email-authentication output."""

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
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult
from core.orchestrator.email_authentication_agent import (
    EMAIL_AUTHENTICATION_AGENT_ID,
    EmailAuthenticationAgent,
    digest_email,
)
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"
_CHALLENGE_AGENT_ID = "email_authentication_challenge_001"

# All three mechanisms fail: the strongest gateway-authentication spoof signal.
_ALL_FAIL_AUTH = "mx.google.com; spf=fail; dkim=fail; dmarc=fail"
# Clean delivery: everything passes, so the lift-only detector emits nothing.
_ALL_PASS_AUTH = "mx.google.com; spf=pass; dkim=pass; dmarc=pass"


def _auth_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=EMAIL_AUTHENTICATION_AGENT_ID,
        display_name="Email Authentication Agent",
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


def _challenge_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=_CHALLENGE_AGENT_ID,
        display_name="Email Authentication Challenge Agent",
        role=AgentRole.BLUE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types=set(),
        layer=5,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {
        e.agent_id: e
        for e in (_auth_agent_entry(), _ingest_entry(), _challenge_entry())
    }


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    headers: dict[str, str] | None = None,
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="Vendor invoice approval",
        body_plain="Please process the attached invoice.",
        headers=headers or {},
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


def _agent(route_ctx: RouteContext) -> EmailAuthenticationAgent:
    return EmailAuthenticationAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


class _ChallengeAgent:
    agent_id = _CHALLENGE_AGENT_ID
    layer = 5
    authority_level = 3
    stage_allowed = "stage_a"
    autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("challenge agent should not run analyze()")

    def challenge(self, contribution: AgentContribution) -> ChallengeResult | None:
        if "dmarc_fail" not in contribution.observed_facts:
            return None
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="confirmed",
            challenge_basis="DMARC failure fact is structurally present.",
        )


def test_email_authentication_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_email_produces_authentication_failure_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        headers={"Authentication-Results": _ALL_FAIL_AUTH},
    )
    commander = SwarmCommander(_registry())
    der = commander.run_case(_mission_context(record_id, payload), [_agent(route_ctx)])

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == EMAIL_AUTHENTICATION_AGENT_ID
    assert contribution.layer == 2
    # Facts only, in detector order; no numeric score surfaced.
    assert contribution.observed_facts == ("spf_fail", "dkim_fail", "dmarc_fail")
    assert der.disposition == "suspicious"
    assert der.inputs_digest == digest_email(payload)
    assert len(der.inputs_digest) == 64


def test_all_pass_authentication_produces_empty_facts_and_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        headers={"Authentication-Results": _ALL_PASS_AUTH},
    )
    commander = SwarmCommander(_registry())
    der = commander.run_case(_mission_context(record_id, payload), [_agent(route_ctx)])

    # Lift-only: a clean pass never lowers risk and emits no fact.
    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_missing_authentication_header_produces_empty_facts_and_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, headers={})
    commander = SwarmCommander(_registry())
    der = commander.run_case(_mission_context(record_id, payload), [_agent(route_ctx)])

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        headers={"Authentication-Results": _ALL_FAIL_AUTH},
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == EMAIL_AUTHENTICATION_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == EMAIL_AUTHENTICATION_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.observed_facts == ["spf_fail", "dkim_fail", "dmarc_fail"]


def test_layer5_challenge_pass_runs_against_authentication_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        headers={"Authentication-Results": _ALL_FAIL_AUTH},
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload),
        [_agent(route_ctx)],
        challenge_agents=[_ChallengeAgent()],
    )

    assert "dmarc_fail" in der.contributions[0].observed_facts
    assert len(der.challenge_pass) == 1
    assert der.challenge_pass[0].agent_id == _CHALLENGE_AGENT_ID
    assert der.challenge_pass[0].challenge_outcome == "confirmed"
    assert der.disposition == "suspicious"


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(None) is None  # type: ignore[arg-type]


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(route_ctx, headers={"Authentication-Results": _ALL_FAIL_AUTH})
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        headers={"Authentication-Results": _ALL_FAIL_AUTH},
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
    route_ctx = _route_ctx(tmp_path)
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id=_INGEST_AGENT_ID,
        layer=2,
        observed_facts=["dmarc_fail"],
    )
    with pytest.raises(GovernanceError, match="cannot write this record type"):
        submit_agent_contribution(
            route_ctx,
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            source_agent=_INGEST_AGENT_ID,
            payload=payload,
        )


def test_digest_email_is_deterministic():
    payload = EmailInboundPayload(
        received_at=datetime(2026, 6, 7, tzinfo=timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="invoice",
        body_plain="hello",
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_agent_contribution_payload_round_trips_via_payload_models():
    record = BlackboardRecord(
        tenant_id="tenant_demo",
        environment=Environment.PRODUCTION,
        record_type=RecordType.AGENT_CONTRIBUTION,
        source_agent=EMAIL_AUTHENTICATION_AGENT_ID,
        payload=AgentContributionPayload(
            case_id=uuid4(),
            inputs_digest="a" * 64,
            agent_id=EMAIL_AUTHENTICATION_AGENT_ID,
            layer=2,
            observed_facts=["dmarc_fail"],
        ).model_dump(mode="json"),
    )
    parsed = validate_record_payload(record)
    assert isinstance(parsed, AgentContributionPayload)
    assert parsed.observed_facts == ["dmarc_fail"]
