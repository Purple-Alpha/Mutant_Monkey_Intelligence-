"""Specialisation Fission v2 Class 2 adversarial tests (scoreboard row #104).

Eight required tests per ``Specialisation_Fission_Contract_v2.md`` §16
(tests 1-6 from Load Fission v2 + tests 7-8 specialisation-specific).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.control_plane.budget import INCOMPLETE_BUDGET_EXHAUSTED
from core.fission import (
    FissionError,
    FissionEventType,
    IntensityLevel,
    LifecycleEventKind,
    ProposedEvidence,
    ProposedSpecialist,
    SpecialisationFissionController,
    SpecialisationFissionPolicy,
    SpecialisationFissionPolicyStore,
    SpecialisationFissionProposal,
    SpawnQuotaTracker,
)
from core.watchers import ThreatLevel


def _v2_proposal(**overrides) -> SpecialisationFissionProposal:
    base = dict(
        triggering_watcher="W2",
        parent_id="header_parent",
        parent_type="header_analysis_agent",
        layer="detection",
        divergence_signal=0.91,
        threat_level=ThreatLevel.HIGH,
        proposed_children=(
            ProposedSpecialist(
                child_type="red_header_injection_sim",
                sub_space="red_header_pressure",
            ),
            ProposedSpecialist(
                child_type="blue_header_forensics",
                sub_space="blue_header_facts",
            ),
        ),
        schema_id="sf2_blue_header_v1",
        tenant_id="tenant_a",
        parent_workflow_id="wf-sf2-001",
        intensity_level=IntensityLevel.NORMAL,
        scenario_id="scenario::header",
        scenario_version="1.0.0",
        tool_scope=frozenset({"observe", "scan"}),
        child_capabilities=frozenset({"observe"}),
    )
    base.update(overrides)
    return SpecialisationFissionProposal(**base)


class TestSpecialisationFissionV2Adversarial:
    def test_1_privilege_escalation_blocked_and_logged(self):
        child = SpecialisationFissionController().propose(_v2_proposal())[0]
        with pytest.raises(FissionError, match="outside assigned"):
            child.gain_tool_outside_assignment("admin_override")
        with pytest.raises(FissionError, match="impersonate"):
            child.impersonate_parent()
        with pytest.raises(FissionError, match="modify policy"):
            child.modify_policy()
        with pytest.raises(FissionError, match="tenant data"):
            child.write_tenant_data()

    def test_2_spawn_injection_semantic_trigger_rejected(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="non-semantic"):
            controller.propose(
                _v2_proposal(
                    semantic_content_ref="malicious email body triggers specialisation fission",
                )
            )
        assert controller.event_log.for_type(FissionEventType.REJECTED)

    def test_3_namespace_contamination_rejected(self):
        child = SpecialisationFissionController().propose(_v2_proposal())[0]
        with pytest.raises(FissionError, match="own namespace"):
            child.write_proposed_evidence(
                namespace="parent/global",
                evidence_type="header",
                content_ref="obs://bad",
            )

    def test_4_orphan_persistence_sweep_after_ttl(self):
        store = SpecialisationFissionPolicyStore()
        store.register(
            SpecialisationFissionPolicy(version="sf2-ttl-test", max_children=3, child_ttl_seconds=1.0)
        )
        fixed = datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)
        controller = SpecialisationFissionController(
            policy_store=store,
            _clock=lambda: fixed,
        )
        child = controller.propose(_v2_proposal(policy_version="sf2-ttl-test"))[0]
        child.expires_at = fixed - timedelta(seconds=1)
        assert child.active
        retired = controller.sweep_expired_children()
        assert child.child_id in retired
        assert not child.active
        assert any(
            e.event is LifecycleEventKind.ORPHAN_SWEEP
            for e in controller.lifecycle_log.entries()
        )

    def test_5_collusion_blocked_at_governed_ingestion(self):
        controller = SpecialisationFissionController()
        children = controller.propose(_v2_proposal())
        ev0 = children[0].write_proposed_evidence(
            namespace=children[0].namespace,
            evidence_type="header",
            content_ref="obs://a",
        )
        controller.ingest_child_evidence(
            parent_id="header_parent",
            child=children[0],
            evidence=ev0,
            collusion_limit=1,
        )
        ev1 = children[1].write_proposed_evidence(
            namespace=children[1].namespace,
            evidence_type="header",
            content_ref="obs://b",
        )
        with pytest.raises(FissionError, match="collusion"):
            controller.ingest_child_evidence(
                parent_id="header_parent",
                child=children[1],
                evidence=ev1,
                collusion_limit=1,
            )

    def test_6_denial_of_wallet_quotas_and_circuit_breaker(self):
        tracker = SpawnQuotaTracker(
            per_tenant_quota=10,
            global_quota=10,
            circuit_breaker_threshold=2,
        )
        controller = SpecialisationFissionController(quota_tracker=tracker)
        controller.propose(_v2_proposal())
        controller.propose(_v2_proposal())
        with pytest.raises(FissionError, match="circuit breaker"):
            controller.propose(_v2_proposal())
        assert tracker.circuit_open

    def test_7_red_blue_collusion_namespace_isolation(self):
        controller = SpecialisationFissionController()
        children = controller.propose(_v2_proposal())
        red = next(c for c in children if c.specialization_role.value == "red")
        blue = next(c for c in children if c.specialization_role.value == "blue")
        with pytest.raises(FissionError, match="influence blue"):
            red.influence_blue_child()
        with pytest.raises(FissionError, match="red-to-blue"):
            red.pass_to_blue_namespace(
                target_namespace=blue.namespace,
                content_ref="adversarial pressure payload",
            )
        cross_evidence = ProposedEvidence(
            namespace=red.namespace,
            evidence_type="cross_child_transfer",
            content_ref="obs://red-to-blue",
        )
        with pytest.raises(FissionError, match="red-blue collusion"):
            controller.ingest_child_evidence(
                parent_id="header_parent",
                child=red,
                evidence=cross_evidence,
            )

    def test_8_scenario_injection_locked_per_workflow(self):
        controller = SpecialisationFissionController()
        child = controller.propose(_v2_proposal())[0]
        with pytest.raises(FissionError, match="scenario"):
            child.mutate_active_scenario(new_scenario_id="injected_scenario")
        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="header",
            content_ref="obs://x",
        )
        with pytest.raises(FissionError, match="scenario injection"):
            controller.ingest_child_evidence(
                parent_id="header_parent",
                child=child,
                evidence=evidence,
                scenario_id="different_scenario",
            )


class TestSpecialisationFissionV2Governance:
    def test_fallback_mode_denies_spawn_with_log(self):
        store = SpecialisationFissionPolicyStore()
        disabled = store.get("sf2-v1.0.0").with_fallback_disabled()
        store.register(disabled)
        controller = SpecialisationFissionController(policy_store=store)
        with pytest.raises(FissionError, match="fallback mode"):
            controller.propose(_v2_proposal(policy_version=disabled.version))
        assert any(
            e.event is LifecycleEventKind.FALLBACK_DENIAL
            for e in controller.lifecycle_log.entries()
        )

    def test_spawn_decision_record_includes_v2_fields(self):
        controller = SpecialisationFissionController()
        controller.propose(_v2_proposal())
        assert len(controller.spawn_records) == 2
        record = controller.spawn_records[0]
        assert record.intensity_level == "normal"
        assert record.scenario_id == "scenario::header"
        assert record.specialization_role in {"red", "blue"}

    def test_light_intensity_blue_only_max_one(self):
        controller = SpecialisationFissionController()
        child = controller.propose(
            _v2_proposal(
                intensity_level=IntensityLevel.LIGHT,
                proposed_children=(
                    ProposedSpecialist(
                        child_type="blue_header_forensics",
                        sub_space="blue_header_facts",
                    ),
                ),
            )
        )[0]
        assert child.specialization_role.value == "blue"
        with pytest.raises(FissionError, match="Blue children only"):
            controller.propose(
                _v2_proposal(
                    intensity_level=IntensityLevel.LIGHT,
                    proposed_children=(
                        ProposedSpecialist(
                            child_type="red_header_injection_sim",
                            sub_space="red",
                        ),
                    ),
                )
            )

    def test_deep_intensity_requires_approval_reference(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="approval_reference"):
            controller.propose(
                _v2_proposal(
                    intensity_level=IntensityLevel.DEEP,
                    proposed_children=(
                        ProposedSpecialist(
                            child_type="red_header_injection_sim",
                            sub_space="red",
                        ),
                        ProposedSpecialist(
                            child_type="blue_header_forensics",
                            sub_space="blue",
                        ),
                        ProposedSpecialist(
                            child_type="blue_linguistic_decomposition",
                            sub_space="blue2",
                        ),
                    ),
                )
            )

    def test_budget_exhaustion_rejected_at_ingestion(self):
        controller = SpecialisationFissionController()
        child = controller.propose(_v2_proposal())[0]
        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="header",
            content_ref="obs://x",
        )
        with pytest.raises(FissionError, match=INCOMPLETE_BUDGET_EXHAUSTED):
            controller.ingest_child_evidence(
                parent_id="header_parent",
                child=child,
                evidence=evidence,
                budget_exhausted=True,
            )

    def test_schema_prohibits_verdict_fields(self):
        controller = SpecialisationFissionController()
        child = controller.propose(_v2_proposal())[0]
        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="header",
            content_ref="obs://x",
        )
        with pytest.raises(FissionError, match="schema violation"):
            controller.ingest_child_evidence(
                parent_id="header_parent",
                child=child,
                evidence=evidence,
                structured_payload={"verdict": "malicious"},
            )
