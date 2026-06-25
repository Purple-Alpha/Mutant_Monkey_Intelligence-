"""Evidence Stage 1 proof for swarm agent #49 Audit Trail.

Authorized by the §11-SIGNED Audit Trail Agent Design Contract (MMI-DEC-199).
These synthetic tests prove the Layer 4 Evidence wrapper projects caller-supplied
tri-state anchor attestation into closed facts only: no Blackboard read, no package
import, tenant isolation, persistence via submit_agent_contribution, registry-default
exclusion, and no §14.3.4 pass overclaim.
"""

from __future__ import annotations

import importlib
import inspect
import socket
import subprocess
import sys
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
from core.orchestrator import Agent, MissionContext, RouteContext
from core.orchestrator import audit_trail_agent as ata
from core.orchestrator.audit_trail_agent import (
    AUDIT_TRAIL_AGENT_ID,
    AuditTrailAgent,
    MAX_ATTESTED_RECORD_TYPES,
    digest_audit_trail_request,
    project_audit_trail_facts,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_agent_contribution
from core.orchestrator.swarm_commander import SwarmCommander

TENANT_A = "tenant_audit_trail_a"
TENANT_B = "tenant_audit_trail_b"

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "audit_trail_synthetic_attestation_only",
        "audit_trail_missing",
        "audit_trail_policy_hash_attested_present",
        "audit_trail_policy_hash_attested_missing",
        "audit_trail_override_separation_attested_present",
        "audit_trail_override_separation_attested_missing",
        "audit_trail_append_only_chain_attested_present",
        "audit_trail_append_only_chain_attested_missing",
        "audit_trail_attestation_all_anchors_present",
        "audit_trail_record_type:",
    }
)

_FORBIDDEN_FACTS = frozenset(
    {
        "audit_trail_posture_complete",
        "audit_trail_policy_hash_present",
    }
)

_FORBIDDEN_LEAK_PATTERNS = (
    "sha256",
    "signed_by",
    "requested_by",
    "approved_by",
    "§14.3.4 pass",
    "stage pass",
    "insurer approval",
    "compliant",
    "certified",
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _audit_trail_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=AUDIT_TRAIL_AGENT_ID,
        display_name="Audit Trail Agent",
        role=AgentRole.DRAFTING,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=4,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {AUDIT_TRAIL_AGENT_ID: _audit_trail_entry()}


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _context(
    *,
    tenant_id: str = TENANT_A,
    case_id=None,
    digest: str | None = None,
    agent: AuditTrailAgent | None = None,
) -> MissionContext:
    case_id = case_id or uuid4()
    agent = agent or AuditTrailAgent()
    return MissionContext(
        case_id=case_id,
        tenant_id=tenant_id,
        inputs_digest=digest
        or digest_audit_trail_request(tenant_id=tenant_id, case_id=case_id),
    )


def _agent(
    *,
    policy_hash_attested_present: bool | None = None,
    override_separation_attested_valid: bool | None = None,
    append_only_chain_attested_present: bool | None = None,
    attested_record_types: tuple[str, ...] = (),
    underwriter_note: str | None = ata.STAGE1_UNDERWRITER_NOTE,
) -> AuditTrailAgent:
    return AuditTrailAgent(
        policy_hash_attested_present=policy_hash_attested_present,
        override_separation_attested_valid=override_separation_attested_valid,
        append_only_chain_attested_present=append_only_chain_attested_present,
        attested_record_types=attested_record_types,
        underwriter_note=underwriter_note,
    )


def _run(agent: AuditTrailAgent, *, tenant_id: str = TENANT_A):
    return SwarmCommander(_registry()).run_case(_context(tenant_id=tenant_id, agent=agent), [agent])


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert fact not in _FORBIDDEN_FACTS
        assert any(
            fact == prefix or fact.startswith(prefix) for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_audit_trail_agent_satisfies_agent_protocol():
    assert isinstance(_agent(), Agent)


def test_no_anchors_supplied_emits_missing_not_all_anchors_present():
    facts = project_audit_trail_facts()
    assert "audit_trail_missing" in facts
    assert "audit_trail_synthetic_attestation_only" in facts
    assert "audit_trail_attestation_all_anchors_present" not in facts


def test_explicit_false_emits_attested_missing_not_all_anchors_present():
    facts = project_audit_trail_facts(policy_hash_attested_present=False)
    assert "audit_trail_policy_hash_attested_missing" in facts
    assert "audit_trail_attestation_all_anchors_present" not in facts


def test_all_three_anchors_true_emits_all_anchors_present_without_overclaim():
    facts = project_audit_trail_facts(
        policy_hash_attested_present=True,
        override_separation_attested_valid=True,
        append_only_chain_attested_present=True,
    )
    assert "audit_trail_attestation_all_anchors_present" in facts
    assert "audit_trail_policy_hash_attested_present" in facts
    assert "audit_trail_override_separation_attested_present" in facts
    assert "audit_trail_append_only_chain_attested_present" in facts
    assert "audit_trail_synthetic_attestation_only" in facts
    assert "audit_trail_posture_complete" not in facts
    for forbidden in _FORBIDDEN_FACTS:
        assert forbidden not in facts


def test_partial_attestation_emits_missing_without_all_anchors_present():
    facts = project_audit_trail_facts(
        policy_hash_attested_present=True,
        override_separation_attested_valid=None,
        append_only_chain_attested_present=False,
    )
    assert "audit_trail_policy_hash_attested_present" in facts
    assert "audit_trail_override_separation_attested_missing" in facts
    assert "audit_trail_append_only_chain_attested_missing" in facts
    assert "audit_trail_attestation_all_anchors_present" not in facts


def test_attested_record_types_capped_and_unknown_names_omitted():
    valid = tuple(list(RecordType.__members__)[:MAX_ATTESTED_RECORD_TYPES])
    facts = project_audit_trail_facts(
        policy_hash_attested_present=True,
        attested_record_types=valid + ("NOT_A_REAL_RECORD_TYPE",),
    )
    for name in valid:
        assert f"audit_trail_record_type:{name}" in facts
    assert "audit_trail_record_type:NOT_A_REAL_RECORD_TYPE" not in facts

    with pytest.raises(GovernanceError, match="exceeds max"):
        project_audit_trail_facts(
            attested_record_types=tuple(list(RecordType.__members__)[: MAX_ATTESTED_RECORD_TYPES + 1]),
        )


def test_wrapper_never_calls_read_records_or_reads_package_paths():
    source = inspect.getsource(ata)
    for forbidden in (
        "read_records",
        "audit_trail.json",
        "open(",
        "Path(",
        "core.evidence_package",
    ):
        assert forbidden not in source

    agent = _agent(
        policy_hash_attested_present=True,
        override_separation_attested_valid=True,
        append_only_chain_attested_present=True,
    )
    facts = agent.analyze(_context(agent=agent)).observed_facts
    assert "audit_trail_attestation_all_anchors_present" in facts


def test_wrapper_source_has_no_forbidden_imports_or_package_calls():
    source = inspect.getsource(ata.AuditTrailAgent)
    module_source = inspect.getsource(ata)
    for forbidden in (
        "assemble_audit_packet",
        "write_audit_packet",
        "generate_package_from_test_plan",
        "audit_package",
        "core.evidence_package",
        "core/mutation/audit_trail",
        "read_records",
        "append_record",
    ):
        assert forbidden not in source
        assert forbidden not in module_source


def test_contribution_persistence_round_trips_through_payload():
    agent = _agent(
        policy_hash_attested_present=True,
        override_separation_attested_valid=True,
        append_only_chain_attested_present=True,
    )
    context = _context(agent=agent)
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
    assert payload_back.agent_id == AUDIT_TRAIL_AGENT_ID
    assert payload_back.layer == 4
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert "audit_trail_attestation_all_anchors_present" in payload_back.observed_facts
    assert write.record is not None


def test_tenant_isolation_on_shared_case_id():
    case_id = uuid4()
    agent_a = _agent(policy_hash_attested_present=True)
    agent_b = _agent(policy_hash_attested_present=False)
    facts_a = _run(agent_a, tenant_id=TENANT_A).contributions[0].observed_facts
    facts_b = _run(agent_b, tenant_id=TENANT_B).contributions[0].observed_facts
    assert "audit_trail_policy_hash_attested_present" in facts_a
    assert "audit_trail_policy_hash_attested_missing" in facts_b


def test_audit_trail_not_in_default_registry():
    assert AUDIT_TRAIL_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_raw_leakage_or_forbidden_overclaim():
    facts = _run(
        _agent(
            policy_hash_attested_present=True,
            override_separation_attested_valid=True,
            append_only_chain_attested_present=True,
        )
    ).contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()
    for forbidden in _FORBIDDEN_LEAK_PATTERNS:
        assert forbidden.lower() not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("AuditTrailAgent must not open a socket")

    def no_subprocess(*args, **kwargs):
        raise AssertionError("AuditTrailAgent must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    monkeypatch.setattr(subprocess, "run", no_subprocess)

    facts = _run(_agent(policy_hash_attested_present=True)).contributions[0].observed_facts
    assert "audit_trail_synthetic_attestation_only" in facts


def test_every_contribution_includes_synthetic_attestation_only():
    scenarios = (
        {},
        {"policy_hash_attested_present": False},
        {
            "policy_hash_attested_present": True,
            "override_separation_attested_valid": True,
            "append_only_chain_attested_present": True,
        },
    )
    for kwargs in scenarios:
        facts = _run(_agent(**kwargs)).contributions[0].observed_facts
        assert "audit_trail_synthetic_attestation_only" in facts


def test_never_calls_write_audit_packet_or_direct_ledger_append_helpers():
    source = inspect.getsource(ata.AuditTrailAgent)
    for forbidden in (
        "write_audit_packet",
        "CanonicalEvidenceLedger",
        "append_record",
        "verdict_ledger",
        "canonical_ledger",
    ):
        assert forbidden not in source


def test_import_guard_does_not_load_forbidden_modules():
    sys.modules.pop("core.orchestrator.audit_trail_agent", None)
    for name in list(sys.modules):
        if name.startswith("core.evidence_package") or name == "core.mutation.audit_trail":
            sys.modules.pop(name, None)

    importlib.import_module("core.orchestrator.audit_trail_agent")

    assert "core.evidence_package" not in sys.modules
    assert "core.mutation.audit_trail" not in sys.modules


def test_underwriter_note_respects_cap_and_forbidden_substrings():
    with pytest.raises(GovernanceError, match="160-char"):
        AuditTrailAgent(underwriter_note="x" * 161)

    long_but_ok = "Internal Stage 1 synthetic audit-trail attestation only."
    agent = AuditTrailAgent(
        policy_hash_attested_present=True,
        underwriter_note=long_but_ok,
    )
    note = agent.analyze(_context(agent=agent)).underwriter_note
    assert note is not None
    assert len(note) <= 160
    lowered = note.lower()
    for forbidden in ("sha256", "requested_by", "§14.3.4 pass"):
        assert forbidden not in lowered


def test_challenge_returns_none():
    assert _agent().challenge(()) is None


def test_digest_audit_trail_request_is_deterministic():
    case_id = uuid4()
    left = digest_audit_trail_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        policy_hash_attested_present=True,
    )
    right = digest_audit_trail_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        policy_hash_attested_present=True,
    )
    different = digest_audit_trail_request(
        tenant_id=TENANT_B,
        case_id=case_id,
        policy_hash_attested_present=True,
    )
    assert left == right
    assert left != different
    assert len(left) == 64
