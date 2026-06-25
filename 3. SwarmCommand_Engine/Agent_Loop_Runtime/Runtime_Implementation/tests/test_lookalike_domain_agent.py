"""End-to-end proof that the governed-agent contract holds on lookalike output."""

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
)
from core.blackboard.models import AgentContributionPayload
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_email_inbound,
)
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult
from core.orchestrator.lookalike_domain_agent import (
    LOOKALIKE_DOMAIN_AGENT_ID,
    LookalikeDomainAgent,
    digest_email,
)
from core.scoring.lookalike_domain_detector import LOOKALIKE_SENDER_DOMAIN_FLAG

_INGEST_AGENT_ID = "ingest_001"
_CHALLENGE_AGENT_ID = "lookalike_challenge_001"
_KNOWN_GOOD = ("harborline.example",)


def _lookalike_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=LOOKALIKE_DOMAIN_AGENT_ID,
        display_name="Lookalike Domain Agent",
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
        display_name="Lookalike Challenge Agent",
        role=AgentRole.BLUE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types=set(),
        layer=5,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {e.agent_id: e for e in (_lookalike_agent_entry(), _ingest_entry(), _challenge_entry())}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    sender: str,
    headers: dict[str, str] | None = None,
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender=sender,
        recipient="ap@buyer.example",
        subject="Invoice attached",
        body_plain="Please review the attached invoice.",
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


def _agent(route_ctx: RouteContext, *, known_good_domains=_KNOWN_GOOD) -> LookalikeDomainAgent:
    return LookalikeDomainAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
        known_good_domains=known_good_domains,
    )


class _ChallengeAgent:
    agent_id = _CHALLENGE_AGENT_ID
    layer = 5
    authority_level = 3
    stage_allowed = "stage_a"
    autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:
        raise AssertionError("challenge agent should not run analyze()")

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        if not any(LOOKALIKE_SENDER_DOMAIN_FLAG in c.observed_facts for c in contributions):
            return None
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="confirmed",
            challenge_basis="Lookalike sender-domain fact is structurally present.",
        )


def test_lookalike_domain_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_typosquat_produces_lookalike_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )
    contribution = der.contributions[0]
    assert contribution.agent_id == LOOKALIKE_DOMAIN_AGENT_ID
    assert contribution.layer == 2
    assert contribution.observed_facts == (LOOKALIKE_SENDER_DOMAIN_FLAG,)
    assert contribution.verification_source is None
    assert contribution.verification_outcome is None
    assert der.disposition == "suspicious"


def test_exact_match_known_good_produces_empty_facts_and_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="ap@harborline.example")
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )
    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_reply_to_identity_domain_is_scored(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        sender="ap@harborline.example",
        headers={"Reply-To": "billing@harborllne.example"},
    )
    contribution = _agent(route_ctx).analyze(_mission_context(record_id, payload))
    assert contribution.observed_facts == (LOOKALIKE_SENDER_DOMAIN_FLAG,)


def test_empty_known_good_domains_produce_no_fact(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    contribution = _agent(route_ctx, known_good_domains=()).analyze(
        _mission_context(record_id, payload)
    )
    assert contribution.observed_facts == ()


def test_contribution_persists_to_blackboard(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])
    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    persisted = [
        r for r in read_records(write.path) if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.observed_facts == [LOOKALIKE_SENDER_DOMAIN_FLAG]


def test_layer5_challenge_pass_runs_against_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload),
        [_agent(route_ctx)],
        challenge_agents=[_ChallengeAgent()],
    )
    assert len(der.challenge_pass) == 1
    assert der.challenge_pass[0].challenge_outcome == "confirmed"


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(()) is None


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(route_ctx, sender="billing@harborllne.example")
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])
    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    bad_context = MissionContext(
        tenant_id="tenant_demo",
        inputs_digest=digest_email(payload),
        source_record_id=write.record.record_id,
    )
    with pytest.raises(GovernanceError, match="not an email_inbound"):
        agent.analyze(bad_context)


def test_tenant_scoped_reads_do_not_cross_tenants(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx, sender="billing@harborllne.example", tenant_id="tenant_a"
    )
    context = _mission_context(record_id, payload, tenant_id="tenant_b")
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_caller_owned_known_good_domains_are_per_agent_instance(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, sender="billing@harborllne.example")
    context = _mission_context(record_id, payload)
    no_fire = _agent(route_ctx, known_good_domains=("harborllne.example",)).analyze(context)
    assert no_fire.observed_facts == ()
    fire = _agent(route_ctx, known_good_domains=_KNOWN_GOOD).analyze(context)
    assert fire.observed_facts == (LOOKALIKE_SENDER_DOMAIN_FLAG,)
