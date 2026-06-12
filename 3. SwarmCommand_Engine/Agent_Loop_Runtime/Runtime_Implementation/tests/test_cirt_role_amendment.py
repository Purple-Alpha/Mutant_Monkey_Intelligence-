"""CIRT role amendment tests — RoleSeparationController Amendment §11.

Three test classes per AGENTS.md §5 and
``RoleSeparationController_Amendment_CIRT.md`` §F:
  Class 1 — expected pass
  Class 2 — adversarial
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import pytest

from core.operator_state import (
    OPERATOR_IDENTITY,
    Capability,
    CIRTAuditEntry,
    CIRTRegistry,
    Role,
    RoleSeparationController,
    RoleSeparationError,
    capabilities_for,
)


# ---------------------------------------------------------------------------
# Class 1 — Expected pass (amendment §F)
# ---------------------------------------------------------------------------


def test_cirt_role_capability_map_exactly_two():
    assert capabilities_for(Role.CIRT) == frozenset(
        {Capability.FREEZE_INCIDENT, Capability.ADJUST_DIAL}
    )


def test_cirt_bound_actor_authorized_on_own_tenant():
    controller = RoleSeparationController()
    registry = CIRTRegistry()
    registry.bind(tenant_id="tenant-a", actor_id="todd")

    entry = controller.authorize_cirt_action(
        actor_id="todd",
        tenant_id="tenant-a",
        capability=Capability.FREEZE_INCIDENT,
        registry=registry,
    )
    assert isinstance(entry, CIRTAuditEntry)
    assert entry.actor_id == "todd"
    assert entry.tenant_id == "tenant-a"
    assert entry.capability is Capability.FREEZE_INCIDENT


def test_cirt_authorized_action_emits_audit_record():
    controller = RoleSeparationController()
    registry = CIRTRegistry()
    registry.bind(tenant_id="tenant-a", actor_id="todd")

    controller.authorize_cirt_action(
        actor_id="todd",
        tenant_id="tenant-a",
        capability=Capability.ADJUST_DIAL,
        registry=registry,
    )
    log = controller.cirt_audit_log()
    assert len(log) == 1
    assert log[0].actor_id == "todd"
    assert log[0].tenant_id == "tenant-a"
    assert log[0].capability is Capability.ADJUST_DIAL


# ---------------------------------------------------------------------------
# Class 2 — Adversarial (amendment §F)
# ---------------------------------------------------------------------------


def test_cirt_denied_cross_tenant_action():
    controller = RoleSeparationController()
    registry = CIRTRegistry()
    registry.bind(tenant_id="tenant-a", actor_id="todd")

    with pytest.raises(RoleSeparationError, match="not the named individual"):
        controller.authorize_cirt_action(
            actor_id="todd",
            tenant_id="tenant-b",
            capability=Capability.FREEZE_INCIDENT,
            registry=registry,
        )


def test_cirt_denied_builder_auditor_operator_capabilities():
    controller = RoleSeparationController()
    registry = CIRTRegistry()
    registry.bind(tenant_id="tenant-a", actor_id="todd")

    for capability in (
        Capability.SIGN_SPEC,
        Capability.RUN_COMPLETE_GATE,
        Capability.WRITE_AGENT_CODE,
    ):
        with pytest.raises(RoleSeparationError):
            controller.authorize_cirt_action(
                actor_id="todd",
                tenant_id="tenant-a",
                capability=capability,
                registry=registry,
            )


def test_non_cirt_role_denied_cirt_capabilities():
    controller = RoleSeparationController()

    with pytest.raises(RoleSeparationError, match="CIRT-only"):
        controller.authorize(
            actor_id="builder-a",
            role=Role.BUILDER,
            capability=Capability.FREEZE_INCIDENT,
        )
    with pytest.raises(RoleSeparationError, match="CIRT-only"):
        controller.authorize(
            actor_id="auditor-a",
            role=Role.AUDITOR,
            capability=Capability.ADJUST_DIAL,
        )


def test_operator_remains_reserved_to_matt_nichol_not_cirt():
    controller = RoleSeparationController()
    registry = CIRTRegistry()
    registry.bind(tenant_id="tenant-a", actor_id="todd")

    # CIRT cannot assume OPERATOR authority (amendment §F).
    with pytest.raises(RoleSeparationError, match="Matt Nichol only"):
        controller.authorize(
            actor_id="todd",
            role=Role.OPERATOR,
            capability=Capability.SIGN_SPEC,
        )

    # CIRT path is separate — even a correctly-bound CIRT actor cannot sign.
    with pytest.raises(RoleSeparationError):
        controller.authorize_cirt_action(
            actor_id="todd",
            tenant_id="tenant-a",
            capability=Capability.SIGN_SPEC,
            registry=registry,
        )

    # OPERATOR still works for Matt only.
    controller.authorize(
        actor_id=OPERATOR_IDENTITY,
        role=Role.OPERATOR,
        capability=Capability.SIGN_SPEC,
    )


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (amendment §F)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Persistent onboarding-time identity binding — deferred. "
        "Component 2 has no auth infrastructure (signed boundary). "
        "Completion path: onboarding/identity contract."
    ),
    strict=True,
)
def test_xfail_persistent_onboarding_identity_binding():
    """CIRT bindings are recorded labels, not authenticated credentials.

    The amendment (§D) is explicit: there is no mint/verify path yet. After
    the onboarding/identity contract lands, bindings survive process restart and
    are backed by the identity surface.
    """

    raise AssertionError("not implemented — onboarding/identity contract required")
