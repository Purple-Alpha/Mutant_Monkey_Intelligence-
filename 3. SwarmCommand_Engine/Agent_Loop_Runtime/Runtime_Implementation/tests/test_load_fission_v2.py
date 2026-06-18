"""Load Fission v2 Class 2 adversarial tests (scoreboard row #103).

Seven required tests per ``Load_Fission_Contract_v2.md`` §11.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.control_plane.budget import INCOMPLETE_BUDGET_EXHAUSTED
from core.fission import (
    FissionError,
    FissionEventType,
    LifecycleEventKind,
    LoadFissionController,
    LoadFissionPolicy,
    LoadFissionPolicyStore,
    LoadFissionProposal,
    LoadTriggerKind,
    SpawnQuotaTracker,
)
from core.watchers import ThreatLevel


def _proposal(**overrides) -> LoadFissionProposal:
    base = dict(
        triggering_watcher="W1",
        parent_id="detector_parent",
        parent_type="header_analysis_agent",
        layer="detection",
        trigger_kind=LoadTriggerKind.QUEUE_DEPTH,
        trigger_value=0.91,
        threat_level=ThreatLevel.HIGH,
        requested_copies=1,
        schema_id="header_schema_v1",
        tenant_id="tenant_a",
        parent_workflow_id="wf-v2-001",
        tool_scope=frozenset({"observe", "scan"}),
        child_capabilities=frozenset({"observe"}),
    )
    base.update(overrides)
    return LoadFissionProposal(**base)


class TestLoadFissionV2Adversarial:
    def test_1_privilege_escalation_blocked_and_logged(self):
        child = LoadFissionController().propose(_proposal())[0]
        with pytest.raises(FissionError, match="outside assigned"):
            child.gain_tool_outside_assignment("admin_override")
        with pytest.raises(FissionError, match="impersonate"):
            child.impersonate_parent()
        with pytest.raises(FissionError, match="modify policy"):
            child.modify_policy()

    def test_2_spawn_injection_semantic_trigger_rejected(self):
        controller = LoadFissionController()
        with pytest.raises(FissionError, match="non-semantic"):
            controller.propose(
                _proposal(
                    trigger_kind=LoadTriggerKind.SEMANTIC,
                    semantic_content_ref="malicious email body triggers spawn",
                )
            )
        assert controller.event_log.for_type(FissionEventType.REJECTED)

    def test_3_namespace_contamination_rejected(self):
        child = LoadFissionController().propose(_proposal())[0]
        with pytest.raises(FissionError, match="own namespace"):
            child.write_proposed_evidence(
                namespace="parent/global",
                evidence_type="header",
                content_ref="obs://bad",
            )

    def test_4_orphan_persistence_sweep_after_ttl(self):
        store = LoadFissionPolicyStore()
        store.register(
            LoadFissionPolicy(version="lf2-ttl-test", max_children=3, child_ttl_seconds=1.0)
        )
        fixed = datetime(2026, 6, 18, 12, 0, 0, tzinfo=timezone.utc)
        controller = LoadFissionController(
            policy_store=store,
            _clock=lambda: fixed,
        )
        child = controller.propose(_proposal(policy_version="lf2-ttl-test"))[0]
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
        controller = LoadFissionController()
        children = controller.propose(_proposal(requested_copies=2))
        ev0 = children[0].write_proposed_evidence(
            namespace=children[0].namespace,
            evidence_type="header",
            content_ref="obs://a",
        )
        controller.ingest_child_evidence(
            parent_id="detector_parent",
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
                parent_id="detector_parent",
                child=children[1],
                evidence=ev1,
                collusion_limit=1,
            )

    def test_6_denial_of_wallet_quotas_and_circuit_breaker(self):
        tracker = SpawnQuotaTracker(
            per_tenant_quota=2,
            global_quota=10,
            circuit_breaker_threshold=2,
        )
        controller = LoadFissionController(quota_tracker=tracker)
        controller.propose(_proposal(requested_copies=1))
        controller.propose(_proposal(requested_copies=1))
        with pytest.raises(FissionError, match="circuit breaker"):
            controller.propose(_proposal(requested_copies=1))
        assert tracker.circuit_open

    def test_7_confused_deputy_permission_intersection_blocks_privileged_action(self):
        child = LoadFissionController().propose(_proposal())[0]
        with pytest.raises(FissionError, match="permission intersection"):
            child.assert_tool_allowed("scan")


class TestLoadFissionV2Governance:
    def test_fallback_mode_denies_spawn_with_log(self):
        store = LoadFissionPolicyStore()
        disabled = store.get("lf2-v1.0.0").with_fallback_disabled()
        store.register(disabled)
        controller = LoadFissionController(policy_store=store)
        with pytest.raises(FissionError, match="fallback mode"):
            controller.propose(_proposal(policy_version=disabled.version))
        assert any(
            e.event is LifecycleEventKind.FALLBACK_DENIAL
            for e in controller.lifecycle_log.entries()
        )

    def test_spawn_decision_record_created_per_child(self):
        controller = LoadFissionController()
        controller.propose(_proposal(requested_copies=2))
        assert len(controller.spawn_records) == 2
        assert controller.spawn_records[0].policy_version == "lf2-v1.0.0"
        assert controller.spawn_records[0].watcher_id == "W1"

    def test_budget_exhaustion_rejected_at_ingestion(self):
        controller = LoadFissionController()
        child = controller.propose(_proposal())[0]
        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="header",
            content_ref="obs://x",
        )
        with pytest.raises(FissionError, match=INCOMPLETE_BUDGET_EXHAUSTED):
            controller.ingest_child_evidence(
                parent_id="detector_parent",
                child=child,
                evidence=evidence,
                budget_exhausted=True,
            )
