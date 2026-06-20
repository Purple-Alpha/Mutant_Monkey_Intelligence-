"""Evidence Stage 1 proof for swarm agent #47 Case Timeline.

Authorized by the §11-SIGNED Case Timeline Agent Design Contract (2026-06-20).
These synthetic tests prove the Layer 4 Evidence wrapper projects caller-supplied
timing anchors and attested governed #48 facts into closed presence/sequence
facts only: no #48 invocation, no ledger/package mutation, tenant isolation,
persistence, registry-default exclusion, and no timestamp/duration/record leakage.
"""

from __future__ import annotations

import inspect
import socket
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.blackboard.models import AgentContributionPayload
from core.orchestrator import Agent, DecisionTimestamps, MissionContext, RouteContext
from core.orchestrator import case_timeline_agent as cta
from core.orchestrator.case_timeline_agent import (
    CASE_TIMELINE_AGENT_ID,
    CaseTimelineAgent,
    digest_timeline_request,
    project_timeline_facts,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_agent_contribution
from core.orchestrator.swarm_commander import SwarmCommander

TENANT_A = "tenant_case_timeline_a"
TENANT_B = "tenant_case_timeline_b"
T0 = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "case_timeline_detected_at_present",
        "case_timeline_verification_requested_at_present",
        "case_timeline_verification_outcome_at_present",
        "case_timeline_closed_at_present",
        "case_timeline_sequence_monotonic",
        "case_timeline_sequence_invalid",
        "case_timeline_verification_phase_missing",
        "case_timeline_verification_phase_present",
        "case_timeline_closure_missing",
        "case_timeline_verification_fact:",
    }
)

_FORBIDDEN_LEAK_PATTERNS = (
    "2026-06-20T",
    "T10:00:00",
    "milliseconds",
    "record_id=",
    "blackboard_record",
    "respond in",
    "sla",
    "performance guarantee",
    "payment",
    "compliant",
    "certified",
    "insurance policy",
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _timeline_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=CASE_TIMELINE_AGENT_ID,
        display_name="Case Timeline Agent",
        role=AgentRole.DRAFTING,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=4,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {CASE_TIMELINE_AGENT_ID: _timeline_entry()}


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _timestamps(
    *,
    detected_at: datetime = T0,
    verification_requested_at: datetime | None = None,
    verification_outcome_at: datetime | None = None,
    closed_at: datetime | None = None,
) -> DecisionTimestamps:
    return DecisionTimestamps(
        detected_at=detected_at,
        verification_requested_at=verification_requested_at,
        verification_outcome_at=verification_outcome_at,
        closed_at=closed_at,
    )


def _context(
    *,
    tenant_id: str = TENANT_A,
    case_id=None,
    digest: str | None = None,
) -> MissionContext:
    case_id = case_id or uuid4()
    timestamps = _timestamps()
    return MissionContext(
        case_id=case_id,
        tenant_id=tenant_id,
        inputs_digest=digest or digest_timeline_request(
            tenant_id=tenant_id,
            case_id=case_id,
            timestamps=timestamps,
        ),
    )


def _agent(
    timestamps: DecisionTimestamps | None = None,
    *,
    expect_closure: bool = False,
    attested_verification_facts: tuple[str, ...] = (),
) -> CaseTimelineAgent:
    return CaseTimelineAgent(
        timestamps=timestamps or _timestamps(),
        expect_closure=expect_closure,
        attested_verification_facts=attested_verification_facts,
    )


def _run(agent: CaseTimelineAgent, *, tenant_id: str = TENANT_A):
    return SwarmCommander(_registry()).run_case(_context(tenant_id=tenant_id), [agent])


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert any(
            fact == prefix or fact.startswith(prefix) for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_case_timeline_agent_satisfies_agent_protocol():
    assert isinstance(_agent(), Agent)


def test_missing_detected_at_fails_closed():
    broken = DecisionTimestamps.model_construct(detected_at=None)
    with pytest.raises(GovernanceError, match="detected_at"):
        CaseTimelineAgent(timestamps=broken)


def test_only_detected_at_emits_detected_present_only():
    facts = project_timeline_facts(_timestamps())
    assert facts == ("case_timeline_detected_at_present",)


def test_full_monotonic_anchor_set_emits_present_and_monotonic():
    timestamps = _timestamps(
        verification_requested_at=T0 + timedelta(minutes=1),
        verification_outcome_at=T0 + timedelta(minutes=2),
        closed_at=T0 + timedelta(minutes=3),
    )
    facts = project_timeline_facts(timestamps)
    assert "case_timeline_detected_at_present" in facts
    assert "case_timeline_verification_requested_at_present" in facts
    assert "case_timeline_verification_outcome_at_present" in facts
    assert "case_timeline_closed_at_present" in facts
    assert "case_timeline_sequence_monotonic" in facts
    assert "case_timeline_sequence_invalid" not in facts


def test_non_monotonic_order_emits_sequence_invalid_not_monotonic():
    timestamps = _timestamps(
        verification_requested_at=T0 + timedelta(minutes=5),
        verification_outcome_at=T0 + timedelta(minutes=1),
    )
    facts = project_timeline_facts(timestamps)
    assert "case_timeline_sequence_invalid" in facts
    assert "case_timeline_sequence_monotonic" not in facts


def test_verification_outcome_without_attested_facts_emits_phase_missing():
    timestamps = _timestamps(verification_outcome_at=T0 + timedelta(minutes=1))
    facts = project_timeline_facts(timestamps)
    assert "case_timeline_verification_phase_missing" in facts
    assert "case_timeline_verification_phase_present" not in facts


def test_verification_outcome_with_attested_fact_emits_phase_present_and_fact():
    timestamps = _timestamps(verification_outcome_at=T0 + timedelta(minutes=1))
    facts = project_timeline_facts(
        timestamps,
        attested_verification_facts=(
            "two_channel_confirmation_confirmed",
        ),
    )
    assert "case_timeline_verification_phase_present" in facts
    assert "case_timeline_verification_fact:two_channel_confirmation_confirmed" in facts
    assert "case_timeline_verification_phase_missing" not in facts


def test_closure_missing_only_when_expect_closure_true():
    timestamps = _timestamps(
        verification_requested_at=T0 + timedelta(minutes=1),
    )
    without_flag = project_timeline_facts(timestamps)
    assert "case_timeline_closure_missing" not in without_flag

    with_flag = project_timeline_facts(timestamps, expect_closure=True)
    assert "case_timeline_closure_missing" in with_flag


def test_wrapper_never_appends_reaction_timing_log_or_mutates_package_files(tmp_path):
    ledger = tmp_path / "REACTION_TIMING_TEST_LOG.md"
    ledger.write_text("# ledger\n", encoding="utf-8")
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    audit_trail = package_dir / "audit_trail.json"
    audit_trail.write_text("{}", encoding="utf-8")
    before_ledger = ledger.read_text(encoding="utf-8")
    before_audit = audit_trail.read_text(encoding="utf-8")

    _run(_agent())

    assert ledger.read_text(encoding="utf-8") == before_ledger
    assert audit_trail.read_text(encoding="utf-8") == before_audit


def test_wrapper_never_calls_verification_outcome_or_workflow_writes():
    source = inspect.getsource(cta.CaseTimelineAgent)
    module_source = inspect.getsource(cta)
    for forbidden in (
        "VerificationOutcomeAgent",
        "verification_outcome_agent",
        "summarize_confirmation_status",
        "record_confirmation_request",
        "record_confirmation_outcome",
        "submit_two_channel_confirmation",
    ):
        assert forbidden not in source
        assert forbidden not in module_source


def test_invalid_tenant_context_fails_closed():
    agent = _agent()
    with pytest.raises(GovernanceError, match="tenant_id"):
        agent.analyze(MissionContext(tenant_id="   ", inputs_digest="a" * 64))


def test_tenant_isolation_preserves_separate_attested_facts():
    timestamps = _timestamps(verification_outcome_at=T0 + timedelta(minutes=1))
    agent_a = CaseTimelineAgent(
        timestamps=timestamps,
        attested_verification_facts=("two_channel_confirmation_confirmed",),
    )
    agent_b = CaseTimelineAgent(
        timestamps=timestamps,
        attested_verification_facts=("two_channel_confirmation_rejected",),
    )
    facts_a = _run(agent_a, tenant_id=TENANT_A).contributions[0].observed_facts
    facts_b = _run(agent_b, tenant_id=TENANT_B).contributions[0].observed_facts

    assert "case_timeline_verification_fact:two_channel_confirmation_confirmed" in facts_a
    assert "case_timeline_verification_fact:two_channel_confirmation_rejected" in facts_b
    assert "case_timeline_verification_fact:two_channel_confirmation_rejected" not in facts_a
    assert "case_timeline_verification_fact:two_channel_confirmation_confirmed" not in facts_b


def test_contribution_persistence_round_trips_through_payload():
    agent = _agent(
        _timestamps(
            verification_requested_at=T0 + timedelta(minutes=1),
            verification_outcome_at=T0 + timedelta(minutes=2),
        ),
        attested_verification_facts=("two_channel_confirmation_confirmed",),
    )
    context = _context()
    route_ctx = _route_ctx()
    contribution = agent.analyze(context)
    write = agent.persist_contribution(route_ctx, context, contribution)

    persisted = [
        record
        for record in read_records(write.path)
        if record.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == CASE_TIMELINE_AGENT_ID
    assert payload_back.layer == 4
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert "case_timeline_verification_phase_present" in payload_back.observed_facts
    assert write.record is not None


def test_challenge_returns_none():
    assert _agent().challenge(()) is None


def test_unauthorized_agent_cannot_write_contribution():
    route_ctx = _route_ctx()
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id="ingest_001",
        layer=4,
        observed_facts=["case_timeline_detected_at_present"],
        control_mapping="case_timeline:stage_a_synthetic",
    )
    with pytest.raises(GovernanceError, match="unknown agent|cannot write"):
        submit_agent_contribution(
            route_ctx,
            tenant_id=TENANT_A,
            environment=Environment.PRODUCTION,
            source_agent="ingest_001",
            payload=payload,
        )


def test_digest_timeline_request_is_deterministic():
    case_id = uuid4()
    timestamps = _timestamps()
    left = digest_timeline_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        timestamps=timestamps,
    )
    right = digest_timeline_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        timestamps=timestamps,
    )
    different = digest_timeline_request(
        tenant_id=TENANT_B,
        case_id=case_id,
        timestamps=timestamps,
    )
    assert left == right
    assert left != different
    assert len(left) == 64


def test_case_timeline_not_in_default_registry():
    assert CASE_TIMELINE_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_timestamps_durations_record_ids_or_client_timing():
    timestamps = _timestamps(
        verification_requested_at=T0 + timedelta(minutes=1),
        verification_outcome_at=T0 + timedelta(minutes=2),
        closed_at=T0 + timedelta(minutes=3),
    )
    facts = _run(
        _agent(
            timestamps,
            attested_verification_facts=("two_channel_confirmation_confirmed",),
        )
    ).contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()
    for forbidden in _FORBIDDEN_LEAK_PATTERNS:
        assert forbidden.lower() not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("CaseTimelineAgent must not open a socket")

    def no_subprocess(*args, **kwargs):
        raise AssertionError("CaseTimelineAgent must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    monkeypatch.setattr(subprocess, "run", no_subprocess)

    der = _run(_agent())
    assert "case_timeline_detected_at_present" in der.contributions[0].observed_facts

    source = inspect.getsource(cta.CaseTimelineAgent).lower()
    for forbidden in (
        "socket",
        "subprocess",
        "requests",
        "http",
        "whois",
        "crm",
    ):
        assert forbidden not in source


def test_wrapper_does_not_audit_packages_or_mutate_detectors():
    source = inspect.getsource(cta.CaseTimelineAgent)
    for forbidden in (
        "audit_package",
        "audit_record_id",
        "generate_package_from_test_plan",
        "client_facing_rubric",
        "risk_score",
    ):
        assert forbidden not in source


def test_out_of_vocabulary_attested_facts_are_omitted_not_emitted():
    timestamps = _timestamps(verification_outcome_at=T0 + timedelta(minutes=1))
    facts = project_timeline_facts(
        timestamps,
        attested_verification_facts=(
            "two_channel_confirmation_confirmed",
            "bogus_verification_fact_not_in_vocabulary",
            "case_timeline_verification_fact:evil",
        ),
    )
    assert "case_timeline_verification_fact:two_channel_confirmation_confirmed" in facts
    assert "case_timeline_verification_fact:bogus_verification_fact_not_in_vocabulary" not in facts
    assert "case_timeline_verification_fact:evil" not in facts
    assert "case_timeline_verification_phase_present" in facts


def test_bounded_prefix_attested_facts_are_accepted():
    timestamps = _timestamps(verification_outcome_at=T0 + timedelta(minutes=1))
    facts = project_timeline_facts(
        timestamps,
        attested_verification_facts=("two_channel_detector:payment_change_v1",),
    )
    assert (
        "case_timeline_verification_fact:two_channel_detector:payment_change_v1" in facts
    )
