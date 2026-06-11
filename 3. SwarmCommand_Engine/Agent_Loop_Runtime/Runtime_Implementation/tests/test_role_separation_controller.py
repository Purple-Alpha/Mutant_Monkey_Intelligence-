"""Phase 1 Infrastructure — Component 2 (Role Separation Controller) tests.

Three test classes per AGENTS.md §5 and Phase1_Infrastructure_Agent_Design_Contract §5:
  Class 1 — expected pass
  Class 2 — adversarial / break-it
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import pytest

from core.operator_state import (
    OPERATOR_IDENTITY,
    Capability,
    Role,
    RoleSeparationController,
    RoleSeparationError,
    capabilities_for,
    role_allows,
)


# ---------------------------------------------------------------------------
# Class 1 — Expected pass
# ---------------------------------------------------------------------------


def test_role_capability_map_matches_contract():
    assert capabilities_for(Role.BUILDER) == frozenset(
        {
            Capability.WRITE_AGENT_CODE,
            Capability.WRITE_BLACKBOARD,
            Capability.RUN_DETECTORS,
        }
    )
    assert capabilities_for(Role.AUDITOR) == frozenset(
        {
            Capability.READ_BLACKBOARD,
            Capability.RUN_COMPLETE_GATE,
            Capability.APPROVE_EVIDENCE_PACKAGE,
            Capability.APPROVE_MUTATION,
        }
    )
    assert capabilities_for(Role.OPERATOR) == frozenset(
        {
            Capability.SIGN_SPEC,
            Capability.COMMIT,
            Capability.PUSH,
            Capability.OPEN_CLOSE_GATE,
            Capability.APPROVE_MUTATION,
            Capability.DEPLOY_MUTATION,
        }
    )


def test_builder_may_write_blackboard_and_run_detectors():
    ctl = RoleSeparationController()
    ctl.authorize(
        actor_id="builder_1", role=Role.BUILDER, capability=Capability.WRITE_BLACKBOARD
    )
    ctl.authorize(
        actor_id="builder_1", role=Role.BUILDER, capability=Capability.RUN_DETECTORS
    )
    assert role_allows(Role.BUILDER, Capability.WRITE_AGENT_CODE)


def test_auditor_may_run_gate_and_approve():
    ctl = RoleSeparationController()
    ctl.authorize(
        actor_id="auditor_1", role=Role.AUDITOR, capability=Capability.RUN_COMPLETE_GATE
    )
    ctl.authorize(
        actor_id="auditor_1",
        role=Role.AUDITOR,
        capability=Capability.APPROVE_EVIDENCE_PACKAGE,
    )


def test_operator_matt_may_sign_commit_push():
    ctl = RoleSeparationController()
    for cap in (Capability.SIGN_SPEC, Capability.COMMIT, Capability.PUSH,
                Capability.DEPLOY_MUTATION):
        ctl.authorize(actor_id=OPERATOR_IDENTITY, role=Role.OPERATOR, capability=cap)


def test_distinct_actors_audit_a_built_surface_is_allowed():
    # A different auditor auditing a surface a builder built is fine; only the
    # *same* actor is blocked.
    ctl = RoleSeparationController()
    ctl.record_build(actor_id="builder_1", surface="evidence_package")
    ctl.authorize(
        actor_id="auditor_1",
        role=Role.AUDITOR,
        capability=Capability.RUN_COMPLETE_GATE,
        surface="evidence_package",
    )
    ctl.assert_separate_assembler_and_auditor(
        assembler_actor="builder_1", auditor_actor="auditor_1"
    )


# ---------------------------------------------------------------------------
# Class 2 — Adversarial / break-it
# ---------------------------------------------------------------------------


def test_builder_cannot_run_complete_gate():
    # Separation rule 2: complete_gate.py runs under AUDITOR credentials only.
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="builder_1",
            role=Role.BUILDER,
            capability=Capability.RUN_COMPLETE_GATE,
        )


def test_auditor_cannot_write_blackboard():
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="auditor_1",
            role=Role.AUDITOR,
            capability=Capability.WRITE_BLACKBOARD,
        )


def test_builder_cannot_audit_surface_it_built():
    # Separation rules 1 and 3: builder-auditor collapse on the same surface.
    ctl = RoleSeparationController()
    ctl.record_build(actor_id="actor_x", surface="evidence_package")
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="actor_x",
            role=Role.AUDITOR,
            capability=Capability.APPROVE_EVIDENCE_PACKAGE,
            surface="evidence_package",
        )


def test_assembler_and_auditor_cannot_be_same_actor():
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.assert_separate_assembler_and_auditor(
            assembler_actor="actor_x", auditor_actor="actor_x"
        )


def test_non_matt_cannot_hold_operator_role():
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="builder_1", role=Role.OPERATOR, capability=Capability.COMMIT
        )


def test_auditor_cannot_deploy_mutation():
    # Separation rule 4: mutation validation is AUDITOR; deployment needs OPERATOR.
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="auditor_1",
            role=Role.AUDITOR,
            capability=Capability.DEPLOY_MUTATION,
        )


def test_auditor_may_validate_mutation_but_only_operator_deploys():
    ctl = RoleSeparationController()
    # validation (approve) is allowed for AUDITOR
    ctl.authorize(
        actor_id="auditor_1", role=Role.AUDITOR, capability=Capability.APPROVE_MUTATION
    )
    # deployment requires OPERATOR (Matt)
    ctl.authorize(
        actor_id=OPERATOR_IDENTITY,
        role=Role.OPERATOR,
        capability=Capability.DEPLOY_MUTATION,
    )


def test_empty_actor_id_rejected():
    ctl = RoleSeparationController()
    with pytest.raises(RoleSeparationError):
        ctl.authorize(
            actor_id="  ", role=Role.BUILDER, capability=Capability.WRITE_BLACKBOARD
        )


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (documented; completion path in the contract)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Cross-process / credential-backed enforcement is out of scope: §3 "
        "Component 2 states this component 'does not introduce new "
        "authentication infrastructure'. The controller is in-process policy "
        "only; verifying that an OS/credential-level actor identity cannot be "
        "spoofed across processes requires real auth infra. Completion path: a "
        "future signed authentication-infrastructure contract."
    ),
    strict=True,
)
def test_cross_process_credential_spoof_resistance():
    # In-process role labels cannot, by design, prove an actor's identity
    # across process boundaries. This xfail keeps that boundary visible.
    raise AssertionError(
        "credential-backed cross-process identity enforcement not implemented "
        "(no auth infra in this signed component)"
    )
