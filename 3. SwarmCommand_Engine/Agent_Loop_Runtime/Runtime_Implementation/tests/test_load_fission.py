"""Load Fission tests (Layer 6 Control Plane, scoreboard row #90).

Three classes per ``Load_Fission_Contract.md`` §6:
  Class 1 — expected pass
  Class 2 — adversarial
  Class 3 — known-gap xfail
"""

from __future__ import annotations

import pytest

from core.control_plane import Ring, RoleTier
from core.control_plane.breaker import RECONCILIATION_AGENT_ID
from core.fission import (
    FissionError,
    FissionEventLog,
    FissionEventType,
    LifecycleEventKind,
    LoadFissionController,
    LoadFissionPolicy,
    LoadFissionPolicyStore,
    LoadFissionProposal,
    LoadTriggerKind,
    PROPOSED_EVIDENCE,
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
        requested_copies=2,
        schema_id="header_schema_v1",
        tenant_id="tenant_a",
        parent_workflow_id="wf-detector-001",
        tool_scope=frozenset({"scan"}),
        child_capabilities=frozenset({"scan"}),
    )
    base.update(overrides)
    return LoadFissionProposal(**base)


class TestLoadFissionExpectedPass:
    def test_valid_watcher_proposal_spawns_gateway_registered_copies(self):
        controller = LoadFissionController()
        children = controller.propose(_proposal())

        assert len(children) == 2
        for child in children:
            assert child.gateway_registered is True
            assert child.agent_type == "header_analysis_agent"
            assert child.schema_id == "header_schema_v1"
            assert child.registration.tenant_id == "tenant_a"
            assert child.registration.budget_tier is RoleTier.DETECTION
            assert child.registration.ring is Ring.RING_0_SYNTHETIC
            assert child.registration.breaker_key.agent_id == child.child_id
            assert child.namespace.startswith("fission/detector_parent/")

        spawn_events = controller.event_log.for_type(FissionEventType.SPAWN)
        assert len(spawn_events) == 1
        assert spawn_events[0].child_ids == tuple(c.child_id for c in children)

    def test_child_writes_proposed_evidence_only_to_own_namespace(self):
        child = LoadFissionController().propose(_proposal(requested_copies=1))[0]

        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="header",
            content_ref="obs://candidate/header/1",
        )

        assert evidence.kind == PROPOSED_EVIDENCE
        assert evidence.namespace == child.namespace
        assert child.proposed_evidence == [evidence]

    def test_threat_drop_exhales_children_and_logs_each_exhale(self):
        controller = LoadFissionController()
        children = controller.propose(_proposal(requested_copies=2))

        retired = controller.exhale(threat_level=ThreatLevel.ELEVATED)

        assert retired == tuple(c.child_id for c in children)
        assert all(not c.active for c in children)
        assert len(controller.event_log.for_type(FissionEventType.EXHALE)) == 2

    def test_event_log_append_only_surface(self):
        log = FissionEventLog()
        assert not hasattr(log, "delete")
        assert not hasattr(log, "update")
        assert not hasattr(log, "remove")


class TestLoadFissionAdversarial:
    def test_agent_self_trigger_rejected(self):
        controller = LoadFissionController()
        with pytest.raises(FissionError, match="only Watcher Agents"):
            controller.propose(_proposal(triggering_watcher="detector_parent"))
        assert controller.event_log.for_type(FissionEventType.REJECTED)

    def test_level_below_two_rejected_including_knowledge_agents(self):
        controller = LoadFissionController()
        with pytest.raises(FissionError, match="Level 2"):
            controller.propose(
                _proposal(
                    layer="knowledge",
                    parent_type="knowledge_agent",
                    threat_level=ThreatLevel.ELEVATED,
                )
            )

    def test_depth_two_child_fission_rejected(self):
        controller = LoadFissionController()
        with pytest.raises(FissionError, match="depth"):
            controller.propose(_proposal(parent_is_child=True))

        child = LoadFissionController().propose(_proposal(requested_copies=1))[0]
        with pytest.raises(FissionError, match="depth"):
            child.propose_fission()

    def test_reconciliation_agent_does_not_fission(self):
        controller = LoadFissionController()
        with pytest.raises(FissionError, match="ReconciliationAgent"):
            controller.propose(_proposal(parent_type=RECONCILIATION_AGENT_ID))

    def test_child_cannot_write_parent_namespace_or_verdict_surface(self):
        child = LoadFissionController().propose(_proposal(requested_copies=1))[0]
        with pytest.raises(FissionError, match="own namespace"):
            child.write_proposed_evidence(
                namespace="parent_namespace",
                evidence_type="header",
                content_ref="obs://bad",
            )
        with pytest.raises(FissionError, match="proposed evidence only"):
            child.write_verdict(verdict="malicious")
        with pytest.raises(FissionError, match="parent namespace"):
            child.write_parent_namespace()

    def test_requested_copies_above_cap_rejected_without_partial_spawn(self):
        store = LoadFissionPolicyStore()
        store.register(LoadFissionPolicy(version="lf2-cap-2", max_children=2))
        controller = LoadFissionController(policy_store=store)
        with pytest.raises(FissionError, match="policy cap"):
            controller.propose(_proposal(requested_copies=3, policy_version="lf2-cap-2"))
        assert controller.children() == ()
        assert controller.event_log.for_type(FissionEventType.REJECTED)


class TestLoadFissionKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Real-tenant saturation thresholds and max-copy calibration are "
            "deferred to a signed amendment after tenant onboarding (LF-D10)."
        ),
        strict=True,
    )
    def test_xfail_real_tenant_saturation_calibration(self):
        raise AssertionError("not implemented — real tenant calibration")

    @pytest.mark.xfail(
        reason=(
            "Live Mode Controller threat-level feed is deferred; tests use the "
            "signed ThreatLevel enum/interface until the Mode Controller is gated."
        ),
        strict=True,
    )
    def test_xfail_live_mode_controller_feed(self):
        raise AssertionError("not implemented — Mode Controller integration")
