"""Role Separation Controller — Phase 1 Infrastructure, Component 2.

Governing contract
------------------
``4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md`` —
§11 SIGNED 2026-06-09 (Matt Nichol), commit ``fe355da`` — §3 Component 2.
Locked decision P1-D4: the agent that assembles an evidence package cannot
audit it; this constraint is structural and enforced at the role level, not by
convention.

What this is
------------
A named, documented, testable formalisation of the builder-auditor separation
already encoded structurally in ``AGENTS.md`` §2 and the #46 Evidence Package
contract (``evidence_package_agent.py`` D3: the assembler never calls the
auditor). It extends that one-off pattern into a single controller every future
agent/process can call.

What this is NOT (signed-contract boundary)
-------------------------------------------
Per §3 Component 2, this component **does not introduce new authentication
infrastructure**. ``actor_id`` is an opaque caller-supplied label; this module
does not mint, verify, sign, encrypt, or persist any credential, token, or
identity. It is a pure in-process policy check over roles and capabilities.

Any OAuth / PSA identity-token / Ghost-Agent identity binding discussed
elsewhere is NOT part of this signed component and is not built here; it would
require its own signed contract before any code lands.

The three roles and their capabilities, and the four separation rules, are
transcribed verbatim from §3 Component 2.

Amendment — named CIRT role
---------------------------
``4. Product_Roadmap/RoleSeparationController_Amendment_CIRT.md`` — §11 SIGNED
2026-06-11 (Matt Nichol). Additive only: it adds one role (``CIRT``), two
tenant-scoped capabilities (``FREEZE_INCIDENT``, ``ADJUST_DIAL``), one capability
map entry, and a tenant-binding check. The three existing roles, their
capability sets, and the four separation rules are unchanged (§G). CIRT is a
**named individual bound to a single tenant** (P4-D2): a CIRT actor for tenant A
may not act on tenant B, and every CIRT action is recorded in the audit trail
with the named actor and the bound ``tenant_id`` (§E). Consistent with the
Component 2 boundary, no auth infrastructure is introduced — ``actor_id`` and
``tenant_id`` remain opaque caller-supplied labels (§D).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.blackboard import GovernanceError


# OPERATOR is Matt Nichol only (§3 Component 2 / AGENTS.md §2). This is the
# canonical operator actor label, not a credential — see module docstring.
OPERATOR_IDENTITY = "matt_nichol"


class Role(str, Enum):
    """Closed role enum (§3 Component 2 + CIRT amendment §B)."""

    BUILDER = "builder"
    AUDITOR = "auditor"
    OPERATOR = "operator"
    # CIRT amendment §B: Computer Incident Response Team member — a named
    # individual bound to a single tenant. Sits below OPERATOR; does NOT inherit
    # BUILDER/AUDITOR/OPERATOR capabilities.
    CIRT = "cirt"


class Capability(str, Enum):
    """Closed capability enum derived from the §3 Component 2 role definitions."""

    # BUILDER
    WRITE_AGENT_CODE = "write_agent_code"
    WRITE_BLACKBOARD = "write_blackboard"
    RUN_DETECTORS = "run_detectors"
    # AUDITOR
    READ_BLACKBOARD = "read_blackboard"
    RUN_COMPLETE_GATE = "run_complete_gate"
    APPROVE_EVIDENCE_PACKAGE = "approve_evidence_package"
    APPROVE_MUTATION = "approve_mutation"  # mutation validation (AUDITOR)
    # OPERATOR
    SIGN_SPEC = "sign_spec"  # §11 sign-off
    COMMIT = "commit"
    PUSH = "push"
    OPEN_CLOSE_GATE = "open_close_gate"
    DEPLOY_MUTATION = "deploy_mutation"  # requires OPERATOR sign-off (rule 4)
    # CIRT amendment §C: both CIRT-only and tenant-scoped. No existing role
    # gains these; no existing capability changes owners.
    FREEZE_INCIDENT = "freeze_incident"  # halt the bound tenant's mail flow
    ADJUST_DIAL = "adjust_dial"  # Lung dial authority for the bound tenant


# Verbatim capability map from §3 Component 2.
_ROLE_CAPABILITIES: dict[Role, frozenset[Capability]] = {
    Role.BUILDER: frozenset(
        {
            Capability.WRITE_AGENT_CODE,
            Capability.WRITE_BLACKBOARD,
            Capability.RUN_DETECTORS,
        }
    ),
    Role.AUDITOR: frozenset(
        {
            Capability.READ_BLACKBOARD,
            Capability.RUN_COMPLETE_GATE,
            Capability.APPROVE_EVIDENCE_PACKAGE,
            Capability.APPROVE_MUTATION,
        }
    ),
    Role.OPERATOR: frozenset(
        {
            Capability.SIGN_SPEC,
            Capability.COMMIT,
            Capability.PUSH,
            Capability.OPEN_CLOSE_GATE,
            Capability.APPROVE_MUTATION,
            Capability.DEPLOY_MUTATION,
        }
    ),
    # CIRT amendment §C — exactly these two, nothing else.
    Role.CIRT: frozenset(
        {
            Capability.FREEZE_INCIDENT,
            Capability.ADJUST_DIAL,
        }
    ),
}

# CIRT-only, tenant-scoped capabilities (amendment §C/§D). Exercising either
# requires the tenant-binding check in ``authorize_cirt_action`` — plain
# ``authorize`` cannot grant them to any other role (the capability map above
# already denies that) and never carries a tenant binding.
_CIRT_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.FREEZE_INCIDENT,
        Capability.ADJUST_DIAL,
    }
)

# Audit capabilities a builder must never exercise on a surface it built
# (separation rules 1 and 3).
_AUDIT_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.RUN_COMPLETE_GATE,
        Capability.APPROVE_EVIDENCE_PACKAGE,
        Capability.APPROVE_MUTATION,
    }
)


class RoleSeparationError(GovernanceError):
    """Raised when an action violates builder-auditor-operator separation."""


@dataclass(frozen=True)
class CIRTAuditEntry:
    """One non-anonymous CIRT action record (amendment §E).

    Accountability is real: the named individual (``actor_id``) and the bound
    ``tenant_id`` are on every decision they make. This is the MSP sales story —
    "here is who is responsible for your security decisions, and here is the
    audit trail proving it."
    """

    actor_id: str
    tenant_id: str
    capability: Capability
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class CIRTRegistry:
    """Per-tenant named-CIRT bindings (amendment §B/§D).

    A single named individual is bound to a tenant at onboarding (P4-D2). The
    binding is a recorded label, not an authenticated credential (§D, no auth
    infrastructure). Binding is one-individual-per-tenant; rebinding requires an
    explicit ``bind`` call (the onboarding/identity contract owns rotation).
    """

    _bindings: dict[str, str] = field(default_factory=dict)

    def bind(self, *, tenant_id: str, actor_id: str) -> None:
        """Bind ``actor_id`` as the named CIRT individual for ``tenant_id``."""

        tenant_id = _require(tenant_id, "tenant_id")
        actor_id = _require(actor_id, "actor_id")
        self._bindings[tenant_id] = actor_id

    def bound_actor(self, tenant_id: str) -> str | None:
        """Return the named CIRT individual for ``tenant_id`` (or ``None``)."""

        if not tenant_id:
            return None
        return self._bindings.get(tenant_id)

    def is_bound(self, *, tenant_id: str, actor_id: str) -> bool:
        """True iff ``actor_id`` is the bound CIRT individual for ``tenant_id``."""

        return bool(tenant_id) and self._bindings.get(tenant_id) == actor_id


def capabilities_for(role: Role) -> frozenset[Capability]:
    """Return the closed capability set for ``role`` (§3 Component 2)."""

    if role not in _ROLE_CAPABILITIES:
        raise RoleSeparationError(f"unknown role: {role!r}")
    return _ROLE_CAPABILITIES[role]


def role_allows(role: Role, capability: Capability) -> bool:
    """True if ``role`` is permitted ``capability`` by the §3 map."""

    return capability in capabilities_for(role)


@dataclass
class RoleSeparationController:
    """In-process controller enforcing the four §3 Component 2 separation rules.

    Scope is one process/run: ``_built_surfaces`` records which ``actor_id``
    built which surface during this run so the same actor cannot then audit it
    (rules 1 and 3 — "cannot be the same process in the same run"). Construct a
    fresh controller per run; nothing is persisted (no auth infra, per the
    contract).
    """

    # (actor_id, surface) pairs recorded via record_build during this run.
    _built_surfaces: set[tuple[str, str]] = field(default_factory=set)
    # Append-only in-run CIRT action audit trail (amendment §E). In-memory only,
    # consistent with the Component 2 "no persistence / no auth infra" boundary.
    _cirt_audit_log: list[CIRTAuditEntry] = field(default_factory=list)

    def record_build(self, *, actor_id: str, surface: str) -> None:
        """Record that ``actor_id`` built ``surface`` in this run."""

        actor_id = _require(actor_id, "actor_id")
        surface = _require(surface, "surface")
        self._built_surfaces.add((actor_id, surface))

    def built_surfaces_for(self, actor_id: str) -> frozenset[str]:
        """Surfaces ``actor_id`` has built this run (read-only view)."""

        return frozenset(
            surface for (actor, surface) in self._built_surfaces if actor == actor_id
        )

    def authorize(
        self,
        *,
        actor_id: str,
        role: Role,
        capability: Capability,
        surface: str | None = None,
    ) -> None:
        """Authorize ``actor_id`` (acting as ``role``) to exercise ``capability``.

        Raises ``RoleSeparationError`` on any violation:
          - OPERATOR role held by anyone but Matt (§3 Component 2);
          - capability outside the role's §3 capability set
            (covers rule 2: complete_gate runs under AUDITOR only, and rule 4:
            DEPLOY_MUTATION is OPERATOR-only);
          - an audit capability exercised by an actor on a surface that same
            actor built this run (rules 1 and 3, builder-auditor collapse).
        """

        actor_id = _require(actor_id, "actor_id")
        if not isinstance(role, Role):
            raise RoleSeparationError(f"unknown role: {role!r}")
        if not isinstance(capability, Capability):
            raise RoleSeparationError(f"unknown capability: {capability!r}")

        if role is Role.OPERATOR and actor_id != OPERATOR_IDENTITY:
            raise RoleSeparationError(
                "OPERATOR role is reserved for Matt Nichol only "
                f"(actor_id={actor_id!r})"
            )

        # CIRT amendment §D: FREEZE_INCIDENT / ADJUST_DIAL are tenant-scoped and
        # cannot be granted through the tenant-less base path. Tenant binding is
        # mandatory, so these route exclusively through authorize_cirt_action.
        if capability in _CIRT_CAPABILITIES:
            raise RoleSeparationError(
                f"capability {capability.value!r} is CIRT-only and tenant-scoped; "
                "use authorize_cirt_action(actor_id=..., tenant_id=...) so the "
                "mandatory tenant binding (amendment §D) is enforced"
            )

        if not role_allows(role, capability):
            raise RoleSeparationError(
                f"role {role.value!r} is not permitted capability "
                f"{capability.value!r} (§3 Component 2 capability map)"
            )

        if (
            capability in _AUDIT_CAPABILITIES
            and surface is not None
            and (actor_id, surface) in self._built_surfaces
        ):
            raise RoleSeparationError(
                f"builder-auditor collapse: actor {actor_id!r} built surface "
                f"{surface!r} this run and cannot also audit it "
                f"({capability.value!r})"
            )

    def authorize_cirt_action(
        self,
        *,
        actor_id: str,
        tenant_id: str,
        capability: Capability,
        registry: CIRTRegistry,
    ) -> CIRTAuditEntry:
        """Authorize a named CIRT individual to act on its bound tenant.

        Enforces the amendment's tenant binding (§D): the action is permitted
        only when ``actor_id`` is the named CIRT individual bound to
        ``tenant_id`` in ``registry``. A CIRT member for tenant A acting on
        tenant B raises ``RoleSeparationError``. On success the action is
        recorded in the CIRT audit trail (§E) with the named actor and bound
        tenant, and that record is returned.

        Raises ``RoleSeparationError`` when:
          - ``capability`` is not a CIRT capability (§C);
          - ``actor_id`` is not the bound CIRT individual for ``tenant_id``
            (unbound, wrong person, or cross-tenant — §D).
        """

        actor_id = _require(actor_id, "actor_id")
        tenant_id = _require(tenant_id, "tenant_id")
        if not isinstance(capability, Capability):
            raise RoleSeparationError(f"unknown capability: {capability!r}")
        if not isinstance(registry, CIRTRegistry):
            raise RoleSeparationError(
                "authorize_cirt_action requires a CIRTRegistry of named "
                "per-tenant bindings (amendment §B/§D)"
            )
        if capability not in _CIRT_CAPABILITIES:
            raise RoleSeparationError(
                f"capability {capability.value!r} is not a CIRT capability; "
                "CIRT holds exactly {FREEZE_INCIDENT, ADJUST_DIAL} (amendment §C)"
            )
        if not registry.is_bound(tenant_id=tenant_id, actor_id=actor_id):
            raise RoleSeparationError(
                f"CIRT actor {actor_id!r} is not the named individual bound to "
                f"tenant {tenant_id!r}; CIRT authority is tenant-scoped and "
                "cannot cross tenants (amendment §D)"
            )

        entry = CIRTAuditEntry(
            actor_id=actor_id, tenant_id=tenant_id, capability=capability
        )
        self._cirt_audit_log.append(entry)
        return entry

    def cirt_audit_log(self) -> tuple[CIRTAuditEntry, ...]:
        """Read-only view of CIRT actions recorded this run (amendment §E)."""

        return tuple(self._cirt_audit_log)

    def assert_separate_assembler_and_auditor(
        self, *, assembler_actor: str, auditor_actor: str
    ) -> None:
        """Rule 3: evidence assembly (BUILDER) and audit (AUDITOR) must be
        different actors in the same run."""

        assembler_actor = _require(assembler_actor, "assembler_actor")
        auditor_actor = _require(auditor_actor, "auditor_actor")
        if assembler_actor == auditor_actor:
            raise RoleSeparationError(
                "evidence package assembly and audit cannot be the same actor "
                f"in the same run (actor={assembler_actor!r})"
            )


def _require(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RoleSeparationError(f"{name} must be a non-empty string")
    return value


__all__ = [
    "OPERATOR_IDENTITY",
    "Capability",
    "Role",
    "RoleSeparationController",
    "RoleSeparationError",
    "CIRTAuditEntry",
    "CIRTRegistry",
    "capabilities_for",
    "role_allows",
]
