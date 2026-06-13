"""Specialisation Fission tests (Layer 6 Control Plane, scoreboard row #91)."""

from __future__ import annotations

import pytest

from core.control_plane import Ring
from core.control_plane.breaker import RECONCILIATION_AGENT_ID
from core.fission import (
    FissionError,
    FissionEventType,
    PROPOSED_EVIDENCE,
    ProposedSpecialist,
    SpecialisationFissionController,
    SpecialisationFissionProposal,
    SubTypeRegistry,
)
from core.operator_state.role_separation import OPERATOR_IDENTITY
from core.watchers import ThreatLevel


def _proposal(**overrides) -> SpecialisationFissionProposal:
    base = dict(
        triggering_watcher="W2",
        parent_id="invoice_parent",
        parent_type="invoice_fraud_agent",
        layer="detection",
        divergence_signal=0.93,
        threat_level=ThreatLevel.HIGH,
        proposed_children=(
            ProposedSpecialist(
                child_type="vendor_impersonation_invoice_agent",
                sub_space="vendor_impersonation",
            ),
        ),
        schema_id="invoice_schema_v1",
        tenant_id="tenant_a",
    )
    base.update(overrides)
    return SpecialisationFissionProposal(**base)


class TestSpecialisationFissionExpectedPass:
    def test_known_subtype_spawns_gateway_registered_specialist(self):
        registry = SubTypeRegistry()
        registry.register_existing("vendor_impersonation_invoice_agent")
        controller = SpecialisationFissionController(registry=registry)

        children = controller.propose(_proposal())

        assert len(children) == 1
        child = children[0]
        assert child.gateway_registered is True
        assert child.agent_type == "vendor_impersonation_invoice_agent"
        assert child.schema_id == "invoice_schema_v1"
        assert child.registration.ring is Ring.RING_0_SYNTHETIC
        assert child.registration.tool_scope == frozenset({"vendor_impersonation"})
        assert controller.event_log.for_type(FissionEventType.SPAWN)

    def test_net_new_type_holds_until_matt_signs_then_activates_at_ring_zero(self):
        controller = SpecialisationFissionController()
        spawned = controller.propose(
            _proposal(
                proposed_children=(
                    ProposedSpecialist(
                        child_type="compromised_internal_account_invoice_agent",
                        sub_space="compromised_internal_account",
                    ),
                )
            )
        )
        assert spawned == ()
        assert controller.children() == ()
        assert controller.held_net_new()[0].child_type == "compromised_internal_account_invoice_agent"

        child = controller.activate_signed_net_new(
            child_type="compromised_internal_account_invoice_agent",
            actor_id=OPERATOR_IDENTITY,
        )

        assert child.active is True
        assert child.registration.ring is Ring.RING_0_SYNTHETIC
        assert controller.registry.classify("compromised_internal_account_invoice_agent").value == "known"
        assert len(controller.event_log.for_type(FissionEventType.SIGN_OFF)) == 2

    def test_child_writes_proposed_evidence_only(self):
        registry = SubTypeRegistry()
        registry.register_existing("vendor_impersonation_invoice_agent")
        child = SpecialisationFissionController(registry=registry).propose(_proposal())[0]

        evidence = child.write_proposed_evidence(
            namespace=child.namespace,
            evidence_type="invoice_pattern",
            content_ref="obs://invoice/subspace/1",
        )

        assert evidence.kind == PROPOSED_EVIDENCE
        assert evidence.namespace == child.namespace

    def test_exhale_retires_active_instances_but_type_persists(self):
        registry = SubTypeRegistry()
        registry.register_existing("vendor_impersonation_invoice_agent")
        controller = SpecialisationFissionController(registry=registry)
        child = controller.propose(_proposal())[0]

        retired = controller.exhale(threat_level=ThreatLevel.ROUTINE)

        assert retired == (child.child_id,)
        assert child.active is False
        assert registry.classify("vendor_impersonation_invoice_agent").value == "known"
        assert controller.event_log.for_type(FissionEventType.EXHALE)


class TestSpecialisationFissionAdversarial:
    def test_agent_self_trigger_rejected(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="only Watcher Agents"):
            controller.propose(_proposal(triggering_watcher="invoice_parent"))
        assert controller.event_log.for_type(FissionEventType.REJECTED)

    def test_below_level_two_rejected_including_knowledge_agent(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="Level 2"):
            controller.propose(
                _proposal(
                    layer="knowledge",
                    parent_type="knowledge_agent",
                    threat_level=ThreatLevel.ELEVATED,
                )
            )

    def test_depth_two_child_fission_rejected(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="depth"):
            controller.propose(_proposal(parent_is_child=True))

    def test_reconciliation_agent_does_not_fission(self):
        controller = SpecialisationFissionController()
        with pytest.raises(FissionError, match="ReconciliationAgent"):
            controller.propose(_proposal(parent_type=RECONCILIATION_AGENT_ID))

    def test_net_new_type_cannot_activate_without_matt_signoff(self):
        controller = SpecialisationFissionController()
        controller.propose(
            _proposal(
                proposed_children=(
                    ProposedSpecialist(child_type="new_invoice_agent", sub_space="new_space"),
                )
            )
        )

        with pytest.raises(FissionError, match="Matt sign-off"):
            controller.activate_signed_net_new(child_type="new_invoice_agent", actor_id="not_matt")
        assert controller.children() == ()

    def test_registry_cannot_grow_autonomously(self):
        registry = SubTypeRegistry()
        with pytest.raises(FissionError, match="autonomously"):
            registry.unsafe_register("new_agent")
        with pytest.raises(FissionError, match="signed-off"):
            registry.register_signed_off("new_agent", signed_off=False)

    def test_net_new_type_born_at_ring_zero(self):
        controller = SpecialisationFissionController()
        controller.propose(
            _proposal(
                proposed_children=(
                    ProposedSpecialist(child_type="new_invoice_agent", sub_space="new_space"),
                )
            )
        )
        child = controller.activate_signed_net_new(
            child_type="new_invoice_agent",
            actor_id=OPERATOR_IDENTITY,
        )
        assert child.registration.ring is Ring.RING_0_SYNTHETIC

    def test_child_cannot_write_parent_namespace_or_verdict(self):
        registry = SubTypeRegistry()
        registry.register_existing("vendor_impersonation_invoice_agent")
        child = SpecialisationFissionController(registry=registry).propose(_proposal())[0]
        with pytest.raises(FissionError, match="own namespace"):
            child.write_proposed_evidence(
                namespace="parent_namespace",
                evidence_type="invoice",
                content_ref="obs://bad",
            )
        with pytest.raises(FissionError, match="proposed evidence only"):
            child.write_verdict(verdict="malicious")

    def test_child_count_cap_rejects_without_partial_spawn(self):
        controller = SpecialisationFissionController(max_children=1)
        with pytest.raises(FissionError, match="conservative cap"):
            controller.propose(
                _proposal(
                    proposed_children=(
                        ProposedSpecialist(child_type="a", sub_space="a"),
                        ProposedSpecialist(child_type="b", sub_space="b"),
                    )
                )
            )
        assert controller.children() == ()


class TestSpecialisationFissionKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Real-tenant complexity/divergence thresholds and child-count "
            "calibration are deferred to a signed amendment after onboarding (SF-D12)."
        ),
        strict=True,
    )
    def test_xfail_real_tenant_divergence_calibration(self):
        raise AssertionError("not implemented — real tenant calibration")

    @pytest.mark.xfail(
        reason=(
            "Automated divergence-signal quality (genuine bifurcation vs noise) "
            "is deferred to real-tenant calibration; launch conservative."
        ),
        strict=True,
    )
    def test_xfail_divergence_signal_quality(self):
        raise AssertionError("not implemented — divergence quality calibration")
