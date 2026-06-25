"""Evidence Stage 1 proof for swarm agent #50 Evidence Strength.

Authorized by the §11-SIGNED Evidence Strength Agent Design Contract (MMI-DEC-206).
These synthetic tests prove the Layer 4 Evidence wrapper projects caller-supplied
tri-state discipline attestation into closed facts only: no eval-harness import,
no pre-ship audit import, tenant isolation, persistence via submit_agent_contribution,
registry-default exclusion, and no framework-pass overclaim.
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
from core.orchestrator import evidence_strength_agent as esa
from core.orchestrator.evidence_strength_agent import (
    EVIDENCE_STRENGTH_AGENT_ID,
    EvidenceStrengthAgent,
    MAX_ATTESTED_CATEGORY_STATUSES,
    digest_evidence_strength_request,
    project_evidence_strength_facts,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.swarm_commander import SwarmCommander

TENANT_A = "tenant_evidence_strength_a"
TENANT_B = "tenant_evidence_strength_b"

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "evidence_strength_synthetic_attestation_only",
        "evidence_strength_missing",
        "evidence_strength_capability_registry_attested_present",
        "evidence_strength_capability_registry_attested_missing",
        "evidence_strength_supported_denominator_attested_present",
        "evidence_strength_supported_denominator_attested_missing",
        "evidence_strength_evidence_bundle_attested_present",
        "evidence_strength_evidence_bundle_attested_missing",
        "evidence_strength_no_cot_attested_present",
        "evidence_strength_no_cot_attested_missing",
        "evidence_strength_synthetic_fixtures_attested_present",
        "evidence_strength_synthetic_fixtures_attested_missing",
        "evidence_strength_attestation_all_anchors_present",
        "evidence_strength_category_status:",
    }
)

_FORBIDDEN_FACTS = frozenset(
    {
        "evidence_strength_posture_complete",
        "evidence_strength_framework_compliant",
        "evidence_strength_accuracy_certified",
    }
)

_FORBIDDEN_LEAK_PATTERNS = (
    "accuracy",
    "precision",
    "recall",
    "fpr",
    "fnr",
    "jsonl",
    "chain-of-thought",
    "framework compliant",
    "framework pass",
    "certified",
    "compliant",
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=EVIDENCE_STRENGTH_AGENT_ID,
        display_name="Evidence Strength Agent",
        role=AgentRole.DRAFTING,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=4,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {EVIDENCE_STRENGTH_AGENT_ID: _entry()}


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _context(
    *,
    tenant_id: str = TENANT_A,
    case_id=None,
    digest: str | None = None,
    agent: EvidenceStrengthAgent | None = None,
) -> MissionContext:
    case_id = case_id or uuid4()
    agent = agent or EvidenceStrengthAgent()
    return MissionContext(
        case_id=case_id,
        tenant_id=tenant_id,
        inputs_digest=digest
        or digest_evidence_strength_request(tenant_id=tenant_id, case_id=case_id),
    )


def _agent(
    *,
    capability_registry_discipline_attested_present: bool | None = None,
    supported_only_denominator_attested_present: bool | None = None,
    evidence_required_per_score_attested_present: bool | None = None,
    no_chain_of_thought_attested_present: bool | None = None,
    synthetic_fixtures_only_attested_present: bool | None = None,
    attested_category_statuses: tuple[str, ...] = (),
    underwriter_note: str | None = esa.STAGE1_UNDERWRITER_NOTE,
) -> EvidenceStrengthAgent:
    return EvidenceStrengthAgent(
        capability_registry_discipline_attested_present=capability_registry_discipline_attested_present,
        supported_only_denominator_attested_present=supported_only_denominator_attested_present,
        evidence_required_per_score_attested_present=evidence_required_per_score_attested_present,
        no_chain_of_thought_attested_present=no_chain_of_thought_attested_present,
        synthetic_fixtures_only_attested_present=synthetic_fixtures_only_attested_present,
        attested_category_statuses=attested_category_statuses,
        underwriter_note=underwriter_note,
    )


def _run(agent: EvidenceStrengthAgent, *, tenant_id: str = TENANT_A):
    return SwarmCommander(_registry()).run_case(_context(tenant_id=tenant_id, agent=agent), [agent])


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert fact not in _FORBIDDEN_FACTS
        assert any(
            fact == prefix or fact.startswith(prefix) for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_evidence_strength_agent_satisfies_agent_protocol():
    assert isinstance(_agent(), Agent)


def test_no_anchors_supplied_emits_missing_not_all_anchors_present():
    facts = project_evidence_strength_facts()
    assert "evidence_strength_missing" in facts
    assert "evidence_strength_synthetic_attestation_only" in facts
    assert "evidence_strength_attestation_all_anchors_present" not in facts


def test_explicit_false_emits_attested_missing_not_all_anchors_present():
    facts = project_evidence_strength_facts(
        capability_registry_discipline_attested_present=False
    )
    assert "evidence_strength_capability_registry_attested_missing" in facts
    assert "evidence_strength_attestation_all_anchors_present" not in facts


def test_all_five_anchors_true_emits_all_anchors_present_without_overclaim():
    facts = project_evidence_strength_facts(
        capability_registry_discipline_attested_present=True,
        supported_only_denominator_attested_present=True,
        evidence_required_per_score_attested_present=True,
        no_chain_of_thought_attested_present=True,
        synthetic_fixtures_only_attested_present=True,
    )
    assert "evidence_strength_attestation_all_anchors_present" in facts
    assert "evidence_strength_capability_registry_attested_present" in facts
    assert "evidence_strength_supported_denominator_attested_present" in facts
    assert "evidence_strength_evidence_bundle_attested_present" in facts
    assert "evidence_strength_no_cot_attested_present" in facts
    assert "evidence_strength_synthetic_fixtures_attested_present" in facts
    assert "evidence_strength_synthetic_attestation_only" in facts
    for forbidden in _FORBIDDEN_FACTS:
        assert forbidden not in facts


def test_partial_attestation_emits_missing_without_all_anchors_present():
    facts = project_evidence_strength_facts(
        capability_registry_discipline_attested_present=True,
        supported_only_denominator_attested_present=None,
        evidence_required_per_score_attested_present=False,
        no_chain_of_thought_attested_present=True,
        synthetic_fixtures_only_attested_present=None,
    )
    assert "evidence_strength_capability_registry_attested_present" in facts
    assert "evidence_strength_supported_denominator_attested_missing" in facts
    assert "evidence_strength_evidence_bundle_attested_missing" in facts
    assert "evidence_strength_attestation_all_anchors_present" not in facts


def test_attested_category_statuses_capped_and_unknown_names_omitted():
    valid = ("supported", "not_supported_yet", "evidence_missing")
    facts = project_evidence_strength_facts(
        capability_registry_discipline_attested_present=True,
        attested_category_statuses=valid + ("bogus_status",),
    )
    for name in valid:
        assert f"evidence_strength_category_status:{name}" in facts
    assert "evidence_strength_category_status:bogus_status" not in facts

    overflow = tuple(f"supported" if i % 2 == 0 else "evidence_missing" for i in range(MAX_ATTESTED_CATEGORY_STATUSES + 1))
    with pytest.raises(GovernanceError, match="exceeds max"):
        project_evidence_strength_facts(attested_category_statuses=overflow)


def test_wrapper_source_has_no_forbidden_imports_or_harness_calls():
    source = inspect.getsource(esa.EvidenceStrengthAgent)
    module_source = inspect.getsource(esa)
    for forbidden in (
        "fraud_eval_harness",
        "pre_ship_audit",
        "core.scoring.eval",
        "core/evidence_package",
        "assemble_audit_packet",
        "read_records",
        "append_record",
        "open(",
    ):
        assert forbidden not in source
        assert forbidden not in module_source


def test_contribution_persistence_round_trips_through_payload():
    agent = _agent(
        capability_registry_discipline_attested_present=True,
        supported_only_denominator_attested_present=True,
        evidence_required_per_score_attested_present=True,
        no_chain_of_thought_attested_present=True,
        synthetic_fixtures_only_attested_present=True,
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
    assert payload_back.agent_id == EVIDENCE_STRENGTH_AGENT_ID
    assert payload_back.layer == 4
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert "evidence_strength_attestation_all_anchors_present" in payload_back.observed_facts
    assert write.record is not None


def test_tenant_isolation_on_shared_case_id():
    case_id = uuid4()
    agent_a = _agent(capability_registry_discipline_attested_present=True)
    agent_b = _agent(capability_registry_discipline_attested_present=False)
    facts_a = _run(agent_a, tenant_id=TENANT_A).contributions[0].observed_facts
    facts_b = _run(agent_b, tenant_id=TENANT_B).contributions[0].observed_facts
    assert "evidence_strength_capability_registry_attested_present" in facts_a
    assert "evidence_strength_capability_registry_attested_missing" in facts_b


def test_evidence_strength_not_in_default_registry():
    assert EVIDENCE_STRENGTH_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_raw_leakage_or_forbidden_overclaim():
    facts = _run(
        _agent(
            capability_registry_discipline_attested_present=True,
            supported_only_denominator_attested_present=True,
            evidence_required_per_score_attested_present=True,
            no_chain_of_thought_attested_present=True,
            synthetic_fixtures_only_attested_present=True,
        )
    ).contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()
    for forbidden in _FORBIDDEN_LEAK_PATTERNS:
        assert forbidden not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("EvidenceStrengthAgent must not open a socket")

    def no_subprocess(*args, **kwargs):
        raise AssertionError("EvidenceStrengthAgent must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    monkeypatch.setattr(subprocess, "run", no_subprocess)

    facts = _run(_agent(capability_registry_discipline_attested_present=True)).contributions[0].observed_facts
    assert "evidence_strength_synthetic_attestation_only" in facts


def test_every_contribution_includes_synthetic_attestation_only():
    scenarios = (
        {},
        {"capability_registry_discipline_attested_present": False},
        {
            "capability_registry_discipline_attested_present": True,
            "supported_only_denominator_attested_present": True,
            "evidence_required_per_score_attested_present": True,
            "no_chain_of_thought_attested_present": True,
            "synthetic_fixtures_only_attested_present": True,
        },
    )
    for kwargs in scenarios:
        facts = _run(_agent(**kwargs)).contributions[0].observed_facts
        assert "evidence_strength_synthetic_attestation_only" in facts


def test_import_guard_does_not_load_forbidden_modules():
    sys.modules.pop("core.orchestrator.evidence_strength_agent", None)
    for name in list(sys.modules):
        if name.startswith("core.scoring.eval") or name.startswith("audit_tools.pre_ship_audit"):
            sys.modules.pop(name, None)

    importlib.import_module("core.orchestrator.evidence_strength_agent")

    assert "core.scoring.eval" not in sys.modules
    assert "audit_tools.pre_ship_audit" not in sys.modules


def test_underwriter_note_respects_cap_and_forbidden_substrings():
    with pytest.raises(GovernanceError, match="160-char"):
        EvidenceStrengthAgent(underwriter_note="x" * 161)

    note_ok = "Internal Stage 1 synthetic evidence-strength attestation only."
    agent = EvidenceStrengthAgent(
        capability_registry_discipline_attested_present=True,
        underwriter_note=note_ok,
    )
    note = agent.analyze(_context(agent=agent)).underwriter_note
    assert note is not None
    assert len(note) <= 160
    lowered = note.lower()
    for forbidden in ("accuracy", "framework compliant", "certified"):
        assert forbidden not in lowered


def test_challenge_returns_none():
    assert _agent().challenge(()) is None


def test_digest_evidence_strength_request_is_deterministic():
    case_id = uuid4()
    left = digest_evidence_strength_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        capability_registry_discipline_attested_present=True,
    )
    right = digest_evidence_strength_request(
        tenant_id=TENANT_A,
        case_id=case_id,
        capability_registry_discipline_attested_present=True,
    )
    different = digest_evidence_strength_request(
        tenant_id=TENANT_B,
        case_id=case_id,
        capability_registry_discipline_attested_present=True,
    )
    assert left == right
    assert left != different
    assert len(left) == 64


def test_control_mapping_is_stage_a_synthetic():
    contribution = _agent(capability_registry_discipline_attested_present=True).analyze(
        _context(agent=_agent(capability_registry_discipline_attested_present=True))
    )
    assert contribution.control_mapping == "evidence_strength:stage_a_synthetic"
