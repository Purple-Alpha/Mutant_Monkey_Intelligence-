"""Evidence Stage 1 proof that the governed-agent contract holds on the Pass 1
package assembler (swarm agent #46 Evidence Package).

Authorized by the §11-SIGNED Evidence Package Agent Design Contract
(2026-06-08), the first Layer 4 Evidence agent selected by the LIVE Build Map.
These are the synthetic-fixture tests that constitute the Stage 1 evidence:
protocol conformance, synthetic package assembly, facts-only Layer 4
contribution, builder/auditor separation (no Grok / PDF / done declaration),
persistence round-trip, guardrails, registry-default exclusion, purity (no
network / no subprocess / no runtime-detector import), deterministic request
digest, and no package-content / vendor-name / source-content leakage.
"""

import inspect
import json
import socket
import subprocess
from datetime import datetime, timezone
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
from core.orchestrator import evidence_package_agent as epa
from core.orchestrator.evidence_package_agent import (
    CONTROL_MAPPING,
    EVIDENCE_PACKAGE_AGENT_ID,
    EvidencePackageAgent,
    digest_package_request,
)
from core.orchestrator.registry import build_default_registry

TENANT = "synthetic-demo-tenant"
FIXED_NOW = datetime(2026, 6, 8, 1, 10, 0, tzinfo=timezone.utc)

# Closed allowlist of fact keys the Layer 4 contribution may emit (D5).
_ALLOWED_FACT_KEYS = frozenset(
    {
        "package_id",
        "package_version",
        "gates_passed",
        "gate_count",
        "audit_packet_coverage_complete",
        "markdown_bundle_present",
        "is_done",
        "record_count",
    }
)

# Fixture content strings that must NEVER leak into a contribution (D5 / §5
# package-content leakage). Drawn from the synthetic source artifacts below.
_FORBIDDEN_LEAK_STRINGS = (
    "Vendor invoice review",
    "payment change reviewed before action",
    "signed-policy",
    "fictional-security-lead",
    "review_before_payment",
    "effective_parameter_report",
)


def _write_source_fixtures(source_dir) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "detection.json").write_text(
        json.dumps(
            {
                "record_kind": "cyber_insurance_v1_detection_record",
                "case_id": "cybins-v1-synthetic-001",
                "tenant_id": TENANT,
                "detectors_fired": ["payment_change_body_pattern_v1"],
                "risk_score_after_lift": 68,
                "raw_email_body_included": False,
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "verification.json").write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-synthetic-001",
                "tenant_id": TENANT,
                "internal_score": 72,
                "recommended_action": "review_before_payment",
                "model": "grok-4",
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "evidence.json").write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-synthetic-001",
                "tenant_id": TENANT,
                "policy_hash": "signed-policy-synthetic-stage-a-v1",
                "effective_parameter_report": [{"k": "v"}],
            }
        ),
        encoding="utf-8",
    )
    audit_trail_path = source_dir / "audit_trail.json"
    audit_trail_path.write_text(
        json.dumps(
            {
                "case_id": "cybins-v1-synthetic-001",
                "tenant_id": TENANT,
                "policy_hash": "signed-policy-synthetic-stage-a-v1",
                "signed_by": "fictional-security-lead",
                "signed_policy_artifact": str(audit_trail_path),
                "two_channel_record_ids": ["id-1", "id-2"],
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "outcome_documentation.md").write_text(
        "# Outcome\n\nVendor invoice review; payment change reviewed before action.\n",
        encoding="utf-8",
    )


def _agent(tmp_path, **overrides) -> EvidencePackageAgent:
    source_dir = tmp_path / "source"
    _write_source_fixtures(source_dir)
    kwargs = dict(
        source_dir=source_dir,
        output_root=tmp_path / "out",
        tenant_id=TENANT,
        trigger="on_demand",
        now=FIXED_NOW,
    )
    kwargs.update(overrides)
    return EvidencePackageAgent(**kwargs)


def _evidence_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=EVIDENCE_PACKAGE_AGENT_ID,
        display_name="Evidence Package Agent",
        role=AgentRole.DRAFTING,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=4,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {EVIDENCE_PACKAGE_AGENT_ID: _evidence_entry()}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _mission_context(agent: EvidencePackageAgent) -> MissionContext:
    return MissionContext(tenant_id=TENANT, inputs_digest=agent.request_digest())


# 1 — protocol conformance
def test_evidence_package_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(tmp_path), Agent)
    assert _agent(tmp_path).layer == 4
    assert _agent(tmp_path).autonomous_action_allowed is False


# 2 / 3 — synthetic assembly produces a Layer 4 facts-only contribution
def test_synthetic_source_produces_layer4_contribution(tmp_path):
    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))

    assert contribution.agent_id == EVIDENCE_PACKAGE_AGENT_ID
    assert contribution.layer == 4
    assert contribution.control_mapping == CONTROL_MAPPING
    assert contribution.underwriter_note is not None
    # Facts are a closed key set; gates passed and coverage complete on the
    # synthetic five-record fixture; never "done" at Stage 1.
    facts = dict(fact.split("=", 1) for fact in contribution.observed_facts)
    assert set(facts) == _ALLOWED_FACT_KEYS
    assert facts["gates_passed"] == "true"
    assert facts["audit_packet_coverage_complete"] == "true"
    assert facts["markdown_bundle_present"] == "true"
    assert facts["is_done"] == "false"
    assert facts["record_count"] == "5"
    assert facts["package_version"] == "v1"


# 4 — persistence round-trip
def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    agent = _agent(tmp_path)
    context = _mission_context(agent)
    contribution = agent.analyze(context)

    write = agent.persist_contribution(route_ctx, context, contribution)
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == EVIDENCE_PACKAGE_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == EVIDENCE_PACKAGE_AGENT_ID
    assert payload_back.layer == 4
    assert payload_back.case_id == context.case_id
    assert payload_back.control_mapping == CONTROL_MAPPING
    assert payload_back.observed_facts == list(contribution.observed_facts)


# 5 — challenge returns None
def test_challenge_returns_none(tmp_path):
    assert _agent(tmp_path).challenge(()) is None


# 6 — missing source artifact fails closed, no misleading contribution
def test_missing_source_artifact_fails_closed(tmp_path):
    agent = _agent(tmp_path)
    (tmp_path / "source" / "detection.json").unlink()
    with pytest.raises(FileNotFoundError):
        agent.analyze(_mission_context(agent))


# 7 — wrapper never calls audit_package / make_xai_client / render_package_pdf,
# and emits no done_declaration.json
def test_wrapper_does_not_audit_render_or_declare_done(tmp_path, monkeypatch):
    import core.evidence_package.package_auditor as auditor_mod
    import core.evidence_package.pdf_renderer as pdf_mod

    def _boom(*args, **kwargs):
        raise AssertionError("evidence package wrapper must not call this path")

    monkeypatch.setattr(auditor_mod, "audit_package", _boom)
    monkeypatch.setattr(auditor_mod, "make_xai_client", _boom)
    monkeypatch.setattr(pdf_mod, "render_package_pdf", _boom)

    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))
    assert contribution.layer == 4

    result = agent.assemble_package()
    assert result.is_done is False
    assert result.done_declaration_path is None
    assert not (result.package_dir / "done_declaration.json").exists()


# 8 — Stage 1 result is never done
def test_stage1_result_is_not_done(tmp_path):
    result = _agent(tmp_path).assemble_package()
    assert result.is_done is False
    assert result.done_declaration_path is None


# 8b — done-state leakage guard: if a (fake) generator claims done, fail closed
def test_done_claim_is_rejected(tmp_path):
    real = _agent(tmp_path)
    real_result = real.assemble_package()

    class _DoneResult:
        package_id = real_result.package_id
        package_dir = real_result.package_dir
        markdown_bundle_path = real_result.markdown_bundle_path
        gate_results = real_result.gate_results
        audit_packet_coverage_complete = True
        is_done = True
        done_declaration_path = real_result.package_dir / "done_declaration.json"

        @property
        def gates_passed(self):
            return True

    agent = _agent(tmp_path, generator=lambda **kwargs: _DoneResult())
    with pytest.raises(GovernanceError, match="done declaration"):
        agent.analyze(_mission_context(agent))


# 9 — not in default registry (Evidence Stage 1)
def test_evidence_package_not_in_default_registry():
    assert EVIDENCE_PACKAGE_AGENT_ID not in build_default_registry()


# 10 — unauthorized agent cannot write the contribution
def test_unauthorized_agent_cannot_write_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id="ingest_001",
        layer=4,
        observed_facts=["package_id=x"],
    )
    with pytest.raises(GovernanceError, match="unknown agent|cannot write"):
        epa.submit_agent_contribution(
            route_ctx,
            tenant_id=TENANT,
            environment=Environment.PRODUCTION,
            source_agent="ingest_001",
            payload=payload,
        )


# 11 — deterministic request digest
def test_request_digest_is_deterministic(tmp_path):
    agent = _agent(tmp_path)
    assert agent.request_digest() == agent.request_digest()
    assert len(agent.request_digest()) == 64
    assert agent.request_digest() == digest_package_request(
        source_dir=tmp_path / "source",
        output_root=tmp_path / "out",
        tenant_id=TENANT,
        trigger="on_demand",
    )


# 12 — no package-content / vendor-name / source-content leakage
def test_contribution_carries_no_package_content_or_source_leak(tmp_path):
    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))

    surfaces = [*contribution.observed_facts, contribution.control_mapping, contribution.underwriter_note]
    for surface in surfaces:
        assert "\n" not in surface
        for leak in _FORBIDDEN_LEAK_STRINGS:
            assert leak not in surface
    # Every fact is a closed key=value with no nested JSON / file bytes.
    for fact in contribution.observed_facts:
        key, _, value = fact.partition("=")
        assert key in _ALLOWED_FACT_KEYS
        assert "{" not in value and "}" not in value


# 13 — purity: no network / no subprocess during assembly
def test_wrapper_does_no_network_or_subprocess(tmp_path, monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("evidence package wrapper must not open a socket")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("evidence package wrapper must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))
    assert contribution.layer == 4


# 14 — wrapper does not import or mutate runtime detector/scoring modules
def test_wrapper_imports_no_runtime_detector_or_scoring_module():
    src = inspect.getsource(epa)
    assert "core.scoring" not in src
    assert "core.precursor" not in src


# 15 — audit-packet coverage is surfaced as metadata only, not a done declaration
def test_coverage_complete_is_metadata_not_done(tmp_path):
    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))
    facts = dict(fact.split("=", 1) for fact in contribution.observed_facts)
    assert facts["audit_packet_coverage_complete"] == "true"
    assert facts["is_done"] == "false"
    assert agent.assemble_package().done_declaration_path is None


# 16 — builder/auditor separation: analyze succeeds even if the auditor path
# is wired to fail when invoked (proves the wrapper never invokes it)
def test_builder_auditor_separation(tmp_path, monkeypatch):
    import core.evidence_package.package_auditor as auditor_mod

    monkeypatch.setattr(
        auditor_mod,
        "audit_package",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("auditor must not be invoked by the assembler agent")
        ),
    )
    agent = _agent(tmp_path)
    contribution = agent.analyze(_mission_context(agent))
    assert contribution.agent_id == EVIDENCE_PACKAGE_AGENT_ID
