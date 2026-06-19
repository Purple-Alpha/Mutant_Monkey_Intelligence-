"""Evidence Stage 1 proof for swarm agent #48 Verification Outcome.

Authorized by the §11-SIGNED Verification Outcome Agent Design Contract
(2026-06-08). These synthetic tests prove the Layer 3 Verification wrapper is a
read-only two-channel-confirmation projector: workflow-state mapping, no
workflow writes, tenant isolation, kill-switch-compatible read summaries,
persistence, registry-default exclusion, no network/subprocess behavior, and no
raw/operator/channel/reason/risk leakage.
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
from core.operator_state import engage_kill_switch
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator import verification_outcome_agent as voa
from core.orchestrator.registry import build_default_registry
from core.orchestrator.verification_outcome_agent import (
    VERIFICATION_OUTCOME_AGENT_ID,
    VerificationOutcomeAgent,
    digest_request,
)
from core.workflows import two_channel_confirmation as tcc

TENANT = "tenant_verification_outcome_demo"
FINDING_ID = "payment_change:case-001"
DETECTOR = "verification_detector_001"
NOW = datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc)

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "two_channel_confirmation_missing",
        "two_channel_confirmation_pending",
        "two_channel_confirmation_confirmed",
        "two_channel_confirmation_rejected",
        "two_channel_confirmation_unable_to_verify",
        "two_channel_confirmation_expired",
        "two_channel_detector:",
        "two_channel_channel_kind:",
    }
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _verification_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=VERIFICATION_OUTCOME_AGENT_ID,
        display_name="Verification Outcome Agent",
        role=AgentRole.WORKFLOW,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=3,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _two_channel_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="two_channel_confirmation_001",
        display_name="Two-Channel Confirmation Workflow",
        role=AgentRole.WORKFLOW,
        allowed_environments={Environment.PRODUCTION},
        allowed_write_types={RecordType.TWO_CHANNEL_CONFIRMATION},
    )


def _ingest_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id="ingest_001",
        display_name="Ingest",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.EMAIL_INBOUND},
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {
        e.agent_id: e
        for e in (_verification_entry(), _two_channel_entry(), _ingest_entry())
    }


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _context(*, tenant_id: str = TENANT, digest: str | None = None) -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest or digest_request(tenant_id=tenant_id, finding_id=FINDING_ID),
    )


def _agent(
    *,
    finding_id: str = FINDING_ID,
    root: Path = Path("blackboard"),
    summarizer=tcc.summarize_confirmation_status,
) -> VerificationOutcomeAgent:
    return VerificationOutcomeAgent(
        finding_id=finding_id,
        blackboard_root=root,
        environment=Environment.PRODUCTION,
        summarizer=summarizer,
    )


def _seed_pending(
    *,
    tenant_id: str = TENANT,
    finding_id: str = FINDING_ID,
    detector: str = DETECTOR,
    requested_at: datetime = NOW,
    root: Path = Path("blackboard"),
) -> None:
    tcc.record_confirmation_request(
        tenant_id=tenant_id,
        finding_id=finding_id,
        detector=detector,
        risk_floor=70,
        requested_by="operator_label_not_for_agent_output",
        requested_at=requested_at,
        blackboard_root=root,
    )


def _seed_outcome(
    outcome_status: str,
    *,
    tenant_id: str = TENANT,
    finding_id: str = FINDING_ID,
    channel_kind: str | None = None,
    root: Path = Path("blackboard"),
) -> None:
    _seed_pending(tenant_id=tenant_id, finding_id=finding_id, root=root)
    if outcome_status == "confirmed" and channel_kind is None:
        channel_kind = "previously_known_internal_system"
    tcc.record_confirmation_outcome(
        tenant_id=tenant_id,
        finding_id=finding_id,
        outcome_status=outcome_status,  # type: ignore[arg-type]
        outcome_by="operator_label_not_for_agent_output",
        outcome_at=NOW + timedelta(minutes=5),
        channel_kind=channel_kind,
        channel_description="raw phone 555-111-2222 must not leak",
        reason="reason text must not leak",
        blackboard_root=root,
    )


def _run(agent: VerificationOutcomeAgent, *, tenant_id: str = TENANT):
    return SwarmCommander(_registry()).run_case(_context(tenant_id=tenant_id), [agent])


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert any(
            fact == prefix or fact.startswith(prefix)
            for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_verification_outcome_agent_satisfies_agent_protocol():
    assert isinstance(_agent(), Agent)


def test_missing_workflow_record_emits_unable_to_verify():
    der = _run(_agent())

    contribution = der.contributions[0]
    assert contribution.agent_id == VERIFICATION_OUTCOME_AGENT_ID
    assert contribution.layer == 3
    assert contribution.observed_facts == ("two_channel_confirmation_missing",)
    assert contribution.verification_source == f"two_channel_confirmation:{FINDING_ID}"
    assert contribution.verification_outcome == "unable_to_verify"


def test_pending_confirmation_emits_unable_to_verify():
    _seed_pending()
    contribution = _run(_agent()).contributions[0]

    assert contribution.observed_facts == (
        "two_channel_confirmation_pending",
        f"two_channel_detector:{DETECTOR}",
    )
    assert contribution.verification_outcome == "unable_to_verify"


def test_confirmed_confirmation_emits_confirmed():
    _seed_outcome("confirmed", channel_kind="previously_known_phone")
    contribution = _run(_agent()).contributions[0]

    assert contribution.observed_facts == (
        "two_channel_confirmation_confirmed",
        f"two_channel_detector:{DETECTOR}",
        "two_channel_channel_kind:previously_known_phone",
    )
    assert contribution.verification_outcome == "confirmed"


def test_rejected_confirmation_emits_contradicted():
    _seed_outcome("rejected")
    contribution = _run(_agent()).contributions[0]

    assert contribution.observed_facts == (
        "two_channel_confirmation_rejected",
        f"two_channel_detector:{DETECTOR}",
    )
    assert contribution.verification_outcome == "contradicted"


def test_unable_to_verify_confirmation_emits_unable_to_verify():
    _seed_outcome("unable_to_verify")
    contribution = _run(_agent()).contributions[0]

    assert contribution.observed_facts == (
        "two_channel_confirmation_unable_to_verify",
        f"two_channel_detector:{DETECTOR}",
    )
    assert contribution.verification_outcome == "unable_to_verify"


def test_expired_confirmation_emits_unable_to_verify():
    _seed_outcome("expired")
    contribution = _run(_agent()).contributions[0]

    assert contribution.observed_facts == (
        "two_channel_confirmation_expired",
        f"two_channel_detector:{DETECTOR}",
    )
    assert contribution.verification_outcome == "unable_to_verify"


def test_wrapper_calls_summary_once():
    _seed_pending()
    calls: list[dict[str, object]] = []
    real_summary = tcc.summarize_confirmation_status

    def spy_summary(**kwargs):
        calls.append(kwargs)
        return real_summary(**kwargs)

    _run(_agent(summarizer=spy_summary))

    assert len(calls) == 1
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["finding_id"] == FINDING_ID
    assert calls[0]["blackboard_root"] == Path("blackboard")


def test_wrapper_never_calls_workflow_write_paths(monkeypatch):
    _seed_pending()

    def fail_write(*args, **kwargs):
        raise AssertionError("VerificationOutcomeAgent must not write workflow state")

    monkeypatch.setattr(tcc, "record_confirmation_request", fail_write)
    monkeypatch.setattr(tcc, "record_confirmation_outcome", fail_write)
    monkeypatch.setattr(tcc, "submit_two_channel_confirmation", fail_write, raising=False)

    contribution = _run(_agent()).contributions[0]
    assert contribution.verification_outcome == "unable_to_verify"


def test_invalid_finding_id_fails_closed():
    with pytest.raises(GovernanceError, match="finding_id"):
        _agent(finding_id="../escape").analyze(_context())


def test_missing_tenant_context_fails_closed():
    with pytest.raises(GovernanceError, match="tenant_id"):
        _agent().analyze(MissionContext(tenant_id=" ", inputs_digest="a" * 64))


def test_tenant_isolation_keeps_confirmation_state_separate():
    _seed_outcome("confirmed", tenant_id="tenant_verification_a")

    confirmed = _run(_agent(), tenant_id="tenant_verification_a").contributions[0]
    missing = _run(_agent(), tenant_id="tenant_verification_b").contributions[0]

    assert confirmed.verification_outcome == "confirmed"
    assert confirmed.observed_facts[0] == "two_channel_confirmation_confirmed"
    assert missing.verification_outcome == "unable_to_verify"
    assert missing.observed_facts == ("two_channel_confirmation_missing",)


def test_read_only_summary_remains_available_under_production_kill_switch():
    _seed_pending()
    engage_kill_switch(
        Path("blackboard"),
        scope="PRODUCTION_ONLY",
        reason="halt workflow writes",
        operator="operator_label_not_for_agent_output",
    )

    contribution = _run(_agent()).contributions[0]
    assert contribution.observed_facts[0] == "two_channel_confirmation_pending"
    assert contribution.verification_outcome == "unable_to_verify"


def test_contribution_persists_to_blackboard_and_reads_back():
    _seed_outcome("confirmed", channel_kind="previously_known_internal_system")
    route_ctx = _route_ctx()
    context = _context()
    agent = _agent()
    contribution = _run(agent).contributions[0]

    write = agent.persist_contribution(route_ctx, context, contribution)
    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]

    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == VERIFICATION_OUTCOME_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.verification_source == f"two_channel_confirmation:{FINDING_ID}"
    assert payload_back.verification_outcome == "confirmed"


def test_challenge_returns_none():
    assert _agent().challenge(()) is None


def test_unauthorized_agent_cannot_write_contribution():
    route_ctx = _route_ctx()
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id="ingest_001",
        layer=3,
        observed_facts=["two_channel_confirmation_confirmed"],
        verification_source=f"two_channel_confirmation:{FINDING_ID}",
        verification_outcome="confirmed",
    )
    with pytest.raises(GovernanceError, match="cannot write this record type"):
        submit_agent_contribution(
            route_ctx,
            tenant_id=TENANT,
            environment=Environment.PRODUCTION,
            source_agent="ingest_001",
            payload=payload,
        )


def test_digest_request_is_deterministic():
    left = digest_request(tenant_id=TENANT, finding_id=FINDING_ID)
    right = digest_request(tenant_id=TENANT, finding_id=FINDING_ID)
    different = digest_request(tenant_id=TENANT, finding_id="different-finding")

    assert left == right
    assert left != different
    assert len(left) == 64


def test_verification_outcome_not_in_default_registry():
    assert VERIFICATION_OUTCOME_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_raw_operator_channel_reason_risk_or_action():
    _seed_outcome("confirmed", channel_kind="other_documented")
    facts = _run(_agent()).contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()

    for forbidden in (
        "operator_label",
        "raw phone",
        "555",
        "111",
        "2222",
        "reason",
        "risk",
        "70",
        "needs_review",
        "recommended",
        "action",
        "payment",
        "account",
        "routing",
        "iban",
        "swift",
        "vendor.example",
        "email",
        "phone",
        "file",
    ):
        assert forbidden not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    _seed_pending()

    def no_network(*args, **kwargs):
        raise AssertionError("VerificationOutcomeAgent must not open a socket")

    def no_subprocess(*args, **kwargs):
        raise AssertionError("VerificationOutcomeAgent must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    monkeypatch.setattr(subprocess, "run", no_subprocess)

    der = _run(_agent())
    assert der.contributions[0].verification_outcome == "unable_to_verify"

    source = inspect.getsource(voa.VerificationOutcomeAgent)
    lowered = source.lower()
    for forbidden in (
        "socket",
        "subprocess",
        "requests",
        "http",
        "dns",
        "whois",
        "crm",
        "email",
        "sms",
        "phone",
    ):
        assert forbidden not in lowered


def test_wrapper_does_not_change_two_channel_or_scoring_behavior():
    wrapper_source = inspect.getsource(voa.VerificationOutcomeAgent)
    assert "record_confirmation_request" not in wrapper_source
    assert "record_confirmation_outcome" not in wrapper_source
    assert "submit_two_channel_confirmation" not in wrapper_source
    assert "risk_floor" not in wrapper_source
    assert "recommended_action" not in wrapper_source

    assert tcc.TwoChannelOutcomeStatus == tcc.TwoChannelOutcomeStatus
    assert tcc.TwoChannelChannelKind == tcc.TwoChannelChannelKind
