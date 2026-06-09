"""Evidence Stage 1 proof for swarm agent #11 Known-Good Contact.

Authorized by the §11-SIGNED Known-Good Contact Agent Design Contract
(2026-06-08). These synthetic tests prove the Layer 3 Verification wrapper is a
read-only Vendor Baseline Store checker: known/new/expired outcomes, no
``ingest_signal`` learning path, tenant isolation, kill-switch inheritance,
persistence, registry-default exclusion, no network/subprocess behavior, and no
raw signal/hash/contact leakage.
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
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator import known_good_contact_agent as kgc
from core.orchestrator.known_good_contact_agent import (
    KNOWN_GOOD_CONTACT_AGENT_ID,
    KnownGoodContactAgent,
    digest_request,
)
from core.orchestrator.registry import build_default_registry
from core.production_state import vendor_baseline as vb
from core.production_state.vendor_baseline.store import SIGNAL_TYPES

TENANT = "tenant_known_good_demo"
VENDOR = "vendor.example"
NOW = datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc)

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "known_good_contact_signal_known",
        "known_good_contact_signal_new",
        "known_good_contact_signal_expired",
        "known_good_contact_signal_type:",
    }
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _known_good_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=KNOWN_GOOD_CONTACT_AGENT_ID,
        display_name="Known-Good Contact Agent",
        role=AgentRole.WORKFLOW,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=3,
        authority_level=3,
        stage_allowed="stage_a",
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
    return {e.agent_id: e for e in (_known_good_entry(), _ingest_entry())}


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _context(*, tenant_id: str = TENANT, digest: str | None = None) -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest
        or digest_request(
            vendor_domain=VENDOR,
            signal_type="routing_number",
            raw_value="123456789",
        ),
    )


def _agent(
    *,
    vendor_domain: str = VENDOR,
    signal_type: str = "routing_number",
    raw_value: str = "123456789",
    now: datetime = NOW,
    checker=vb.check_signal,
) -> KnownGoodContactAgent:
    return KnownGoodContactAgent(
        vendor_domain=vendor_domain,
        signal_type=signal_type,  # type: ignore[arg-type]
        raw_value=raw_value,
        now=now,
        environment=Environment.PRODUCTION,
        checker=checker,
    )


def _seed_known(
    *,
    tenant_id: str = TENANT,
    vendor_domain: str = VENDOR,
    signal_type: str = "routing_number",
    raw_value: str = "123456789",
    now: datetime = NOW,
) -> None:
    vb.ingest_signal(
        tenant_id=tenant_id,
        vendor_domain=vendor_domain,
        signal_type=signal_type,  # type: ignore[arg-type]
        raw_value=raw_value,
        now=now,
    )


def _run(agent: KnownGoodContactAgent, *, tenant_id: str = TENANT):
    return SwarmCommander(_registry()).run_case(_context(tenant_id=tenant_id), [agent])


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert any(
            fact == prefix or fact.startswith(prefix)
            for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_known_good_contact_agent_satisfies_agent_protocol():
    assert isinstance(_agent(), Agent)


def test_known_signal_emits_confirmed_verification_and_fact():
    _seed_known()
    der = _run(_agent())

    contribution = der.contributions[0]
    assert contribution.agent_id == KNOWN_GOOD_CONTACT_AGENT_ID
    assert contribution.layer == 3
    assert contribution.observed_facts == (
        "known_good_contact_signal_known",
        "known_good_contact_signal_type:routing_number",
    )
    assert contribution.verification_source == "vendor_baseline:routing_number"
    assert contribution.verification_outcome == "confirmed"


def test_new_signal_emits_unable_to_verify():
    der = _run(_agent())

    contribution = der.contributions[0]
    assert contribution.observed_facts == (
        "known_good_contact_signal_new",
        "known_good_contact_signal_type:routing_number",
    )
    assert contribution.verification_source == "vendor_baseline:routing_number"
    assert contribution.verification_outcome == "unable_to_verify"


def test_expired_signal_emits_unable_to_verify():
    _seed_known(now=NOW - timedelta(days=120))
    der = _run(_agent(now=NOW))

    contribution = der.contributions[0]
    assert contribution.observed_facts == (
        "known_good_contact_signal_expired",
        "known_good_contact_signal_type:routing_number",
    )
    assert contribution.verification_outcome == "unable_to_verify"


def test_wrapper_calls_check_signal_once(monkeypatch):
    _seed_known()
    calls: list[dict[str, object]] = []
    real_check = vb.check_signal

    def spy_check(**kwargs):
        calls.append(kwargs)
        return real_check(**kwargs)

    _run(_agent(checker=spy_check))

    assert len(calls) == 1
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["vendor_domain"] == VENDOR
    assert calls[0]["signal_type"] == "routing_number"
    assert calls[0]["raw_value"] == "123456789"


def test_wrapper_never_calls_ingest_or_expire(monkeypatch):
    _seed_known()

    def fail_write(*args, **kwargs):
        raise AssertionError("KnownGoodContactAgent must not write baseline state")

    monkeypatch.setattr(vb, "ingest_signal", fail_write)
    monkeypatch.setattr(vb, "expire_stale_signals", fail_write)

    der = _run(_agent())
    assert der.contributions[0].verification_outcome == "confirmed"


def test_invalid_signal_type_fails_closed():
    with pytest.raises(GovernanceError, match="unsupported_signal_type|unsupported"):
        _agent(signal_type="not_a_signal").analyze(_context())


def test_invalid_vendor_domain_fails_closed():
    with pytest.raises(GovernanceError, match="vendor_domain"):
        _agent(vendor_domain=" Vendor.example").analyze(_context())


def test_missing_raw_value_fails_closed():
    with pytest.raises(GovernanceError, match="raw_value"):
        _agent(raw_value=" ")


def test_naive_now_fails_closed():
    with pytest.raises(GovernanceError, match="timezone-aware"):
        _agent(now=datetime(2026, 6, 8, 12, 0)).analyze(_context())


def test_tenant_isolation_keeps_verification_state_separate():
    _seed_known(tenant_id="tenant_known_a")

    known = _run(_agent(), tenant_id="tenant_known_a").contributions[0]
    unknown = _run(_agent(), tenant_id="tenant_known_b").contributions[0]

    assert known.verification_outcome == "confirmed"
    assert known.observed_facts[0] == "known_good_contact_signal_known"
    assert unknown.verification_outcome == "unable_to_verify"
    assert unknown.observed_facts[0] == "known_good_contact_signal_new"


def test_kill_switch_inheritance_blocks_check():
    engage_kill_switch(
        Path("."),
        scope="PRODUCTION_ONLY",
        reason="halt known-good verification",
        operator="matt",
    )
    with pytest.raises(KillSwitchEngaged):
        _agent().analyze(_context())


def test_contribution_persists_to_blackboard_and_reads_back():
    _seed_known()
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
    assert payload_back.agent_id == KNOWN_GOOD_CONTACT_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.verification_source == "vendor_baseline:routing_number"
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
        observed_facts=["known_good_contact_signal_known"],
        verification_source="vendor_baseline:routing_number",
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
    left = digest_request(
        vendor_domain=VENDOR,
        signal_type="routing_number",
        raw_value="123456789",
    )
    right = digest_request(
        vendor_domain=VENDOR,
        signal_type="routing_number",
        raw_value="123456789",
    )
    assert left == right
    assert len(left) == 64


def test_known_good_contact_not_in_default_registry():
    assert KNOWN_GOOD_CONTACT_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_raw_value_hash_contact_or_action():
    _seed_known(raw_value="123-456-789")
    facts = _run(_agent(raw_value="123-456-789")).contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()

    for forbidden in (
        "123",
        "456",
        "789",
        "vendor.example",
        "sha256",
        "email",
        "phone",
        "alice",
        "billing@",
        "risk",
        "recommended",
        "action",
    ):
        assert forbidden not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    _seed_known()

    def no_network(*args, **kwargs):
        raise AssertionError("KnownGoodContactAgent must not open a socket")

    def no_subprocess(*args, **kwargs):
        raise AssertionError("KnownGoodContactAgent must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    monkeypatch.setattr(subprocess, "run", no_subprocess)

    der = _run(_agent())
    assert der.contributions[0].verification_outcome == "confirmed"

    source = inspect.getsource(kgc.KnownGoodContactAgent)
    lowered = source.lower()
    for forbidden in ("socket", "subprocess", "requests", "http", "dns", "whois", "crm"):
        assert forbidden not in lowered


def test_wrapper_does_not_change_vendor_baseline_or_scoring_behavior():
    wrapper_source = inspect.getsource(kgc.KnownGoodContactAgent)
    assert "ingest_signal" not in wrapper_source
    assert "expire_stale_signals" not in wrapper_source
    assert "recommended_action" not in wrapper_source
    assert "recommended_risk_floor" not in wrapper_source

    assert SIGNAL_TYPES == {
        "routing_number",
        "swift_bic_code",
        "iban",
        "account_number",
        "payment_portal_url",
        "pdf_producer_fingerprint",
        "vendor_send_time_window",
    }
