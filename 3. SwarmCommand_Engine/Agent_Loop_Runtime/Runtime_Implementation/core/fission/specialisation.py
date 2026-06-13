"""Specialisation Fission — qualitative division into narrower specialists.

Governing contract
------------------
``4. Product_Roadmap/Specialisation_Fission_Contract.md`` — §11 SIGNED
2026-06-12 (Matt Nichol) — SF-D1..SF-D14.

Specialisation Fission is the higher-risk fission trigger: a parent specialist
divides because its problem space became too complex for one specialist. Known
sub-types may spawn under the gates; net-new agent types are held inert until
Matt signs off, then activate at Ring 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from core.control_plane import Ring
from core.control_plane.breaker import RECONCILIATION_AGENT_ID
from core.fission.event_log import FissionEventLog, FissionEventType, FissionTrigger
from core.fission.load import (
    FissionChild,
    FissionError,
    GatewayRegistration,
    LOAD_FISSION_THREAT_FLOOR,
)
from core.operator_state.role_separation import (
    Capability,
    OPERATOR_IDENTITY,
    Role,
    RoleSeparationController,
    RoleSeparationError,
)
from core.watchers import ThreatLevel, WATCHER_IDS

SPECIALISATION_THREAT_FLOOR = LOAD_FISSION_THREAT_FLOOR
DEFAULT_MAX_SPECIALISATION_CHILDREN = 3


class SubTypeKind(str, Enum):
    KNOWN = "known"
    NET_NEW = "net_new"


@dataclass
class SubTypeRegistry:
    """Deterministic authority on known vs net-new agent types (SF-D6)."""

    _known_types: set[str] = field(default_factory=set)

    def register_existing(self, agent_type: str) -> None:
        if not agent_type:
            raise FissionError("agent_type is required")
        self._known_types.add(agent_type)

    def classify(self, agent_type: str) -> SubTypeKind:
        return SubTypeKind.KNOWN if agent_type in self._known_types else SubTypeKind.NET_NEW

    def register_signed_off(self, agent_type: str, *, signed_off: bool) -> None:
        if not signed_off:
            raise FissionError("registry cannot grow without signed-off fission (SF-D6)")
        self.register_existing(agent_type)

    def unsafe_register(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("registry cannot grow autonomously (SF-D6)")


@dataclass(frozen=True)
class HeldNetNewType:
    parent_id: str
    parent_type: str
    child_type: str
    sub_space: str
    schema_id: str
    tenant_id: str


@dataclass
class NetNewTypeSignOffGate:
    """OPERATOR-only sign-off gate for net-new agent types (SF-D6)."""

    role_controller: RoleSeparationController = field(default_factory=RoleSeparationController)
    event_log: FissionEventLog = field(default_factory=FissionEventLog)
    _held: dict[str, HeldNetNewType] = field(default_factory=dict)
    _signed: set[str] = field(default_factory=set)

    def hold(self, held: HeldNetNewType, *, triggering_watcher: str, threat_level: ThreatLevel) -> HeldNetNewType:
        self._held[held.child_type] = held
        self.event_log.record(
            event_type=FissionEventType.SIGN_OFF,
            trigger_type=FissionTrigger.SPECIALISATION,
            triggering_watcher=triggering_watcher,
            threat_level=threat_level.name,
            parent_id=held.parent_id,
            parent_type=held.parent_type,
            schema_id=held.schema_id,
            detail=f"net-new type {held.child_type!r} held inert pending Matt sign-off",
        )
        return held

    def sign_off(self, *, child_type: str, actor_id: str) -> HeldNetNewType:
        held = self._held.get(child_type)
        if held is None:
            raise FissionError(f"no held net-new type {child_type!r}")
        try:
            self.role_controller.authorize(
                actor_id=actor_id,
                role=Role.OPERATOR,
                capability=Capability.SIGN_SPEC,
                surface=f"specialisation_fission:{child_type}",
            )
        except RoleSeparationError as exc:
            raise FissionError("net-new type requires Matt sign-off (SF-D6)") from exc
        self._signed.add(child_type)
        self.event_log.record(
            event_type=FissionEventType.SIGN_OFF,
            trigger_type=FissionTrigger.SPECIALISATION,
            triggering_watcher="operator",
            threat_level="SIGNED",
            parent_id=held.parent_id,
            parent_type=held.parent_type,
            schema_id=held.schema_id,
            detail=f"net-new type {child_type!r} signed off by {actor_id}",
        )
        return held

    def is_signed(self, child_type: str) -> bool:
        return child_type in self._signed


@dataclass(frozen=True)
class ProposedSpecialist:
    child_type: str
    sub_space: str


@dataclass(frozen=True)
class SpecialisationFissionProposal:
    triggering_watcher: str
    parent_id: str
    parent_type: str
    layer: str
    divergence_signal: float
    threat_level: ThreatLevel
    proposed_children: tuple[ProposedSpecialist, ...]
    schema_id: str
    tenant_id: str
    parent_is_child: bool = False


@dataclass
class SpecialisationFissionController:
    """Validates specialisation proposals, holds net-new types, and spawns."""

    registry: SubTypeRegistry = field(default_factory=SubTypeRegistry)
    event_log: FissionEventLog = field(default_factory=FissionEventLog)
    sign_off_gate: NetNewTypeSignOffGate | None = None
    max_children: int = DEFAULT_MAX_SPECIALISATION_CHILDREN
    _children: dict[str, FissionChild] = field(default_factory=dict)
    _held_by_parent: dict[str, tuple[HeldNetNewType, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sign_off_gate is None:
            self.sign_off_gate = NetNewTypeSignOffGate(event_log=self.event_log)
        else:
            self.sign_off_gate.event_log = self.event_log

    def propose(self, proposal: SpecialisationFissionProposal) -> tuple[FissionChild, ...]:
        try:
            self._validate(proposal)
        except FissionError as exc:
            self._reject(proposal, str(exc))
            raise

        spawned: list[FissionChild] = []
        held: list[HeldNetNewType] = []
        for specialist in proposal.proposed_children:
            kind = self.registry.classify(specialist.child_type)
            if kind is SubTypeKind.KNOWN:
                spawned.append(self._spawn_child(proposal, specialist, kind))
            else:
                held_type = HeldNetNewType(
                    parent_id=proposal.parent_id,
                    parent_type=proposal.parent_type,
                    child_type=specialist.child_type,
                    sub_space=specialist.sub_space,
                    schema_id=proposal.schema_id,
                    tenant_id=proposal.tenant_id,
                )
                assert self.sign_off_gate is not None
                self.sign_off_gate.hold(
                    held_type,
                    triggering_watcher=proposal.triggering_watcher,
                    threat_level=proposal.threat_level,
                )
                held.append(held_type)

        if held:
            self._held_by_parent[proposal.parent_id] = tuple(held)
        if spawned:
            self._record_spawn(proposal, spawned, detail="spawned known sub-types")
        return tuple(spawned)

    def activate_signed_net_new(
        self,
        *,
        child_type: str,
        actor_id: str = OPERATOR_IDENTITY,
    ) -> FissionChild:
        assert self.sign_off_gate is not None
        held = self.sign_off_gate.sign_off(child_type=child_type, actor_id=actor_id)
        self.registry.register_signed_off(child_type, signed_off=True)
        proposal = SpecialisationFissionProposal(
            triggering_watcher="operator",
            parent_id=held.parent_id,
            parent_type=held.parent_type,
            layer="signed_net_new",
            divergence_signal=1.0,
            threat_level=ThreatLevel.HIGH,
            proposed_children=(ProposedSpecialist(child_type=held.child_type, sub_space=held.sub_space),),
            schema_id=held.schema_id,
            tenant_id=held.tenant_id,
        )
        child = self._spawn_child(proposal, proposal.proposed_children[0], SubTypeKind.NET_NEW)
        self._record_spawn(proposal, [child], detail="activated signed-off net-new type")
        return child

    def _validate(self, proposal: SpecialisationFissionProposal) -> None:
        if proposal.triggering_watcher not in WATCHER_IDS:
            raise FissionError("only Watcher Agents may trigger specialisation fission (SF-D1)")
        if proposal.threat_level < SPECIALISATION_THREAT_FLOOR:
            raise FissionError("specialisation fission requires threat Level 2 / HIGH or above (SF-D3)")
        if proposal.parent_is_child:
            raise FissionError("fission depth is capped at 1 generation; child cannot fission (SF-D2)")
        if proposal.parent_type == RECONCILIATION_AGENT_ID:
            raise FissionError("ReconciliationAgent does not fission (SF-D7)")
        if not proposal.proposed_children:
            raise FissionError("at least one proposed specialist is required")
        if len(proposal.proposed_children) > self.max_children:
            raise FissionError("proposed child count exceeds conservative cap (SF-D12)")

    def _spawn_child(
        self,
        proposal: SpecialisationFissionProposal,
        specialist: ProposedSpecialist,
        kind: SubTypeKind,
    ) -> FissionChild:
        index = len(self._children) + 1
        child_id = f"{proposal.parent_id}__{specialist.child_type}__spec_child_{index}"
        namespace = f"fission/{proposal.parent_id}/{child_id}/proposed_evidence"
        registration = GatewayRegistration(
            token=f"token::{child_id}",
            tenant_id=proposal.tenant_id,
            tool_scope=frozenset({specialist.sub_space}),
            budget_tier=self._budget_tier_for_layer(proposal.layer),
            ring=Ring.RING_0_SYNTHETIC,
            breaker_key=self._breaker_key(proposal.tenant_id, child_id),
        )
        child = FissionChild(
            child_id=child_id,
            parent_id=proposal.parent_id,
            agent_type=specialist.child_type,
            schema_id=proposal.schema_id,
            namespace=namespace,
            registration=registration,
        )
        self._children[child_id] = child
        return child

    @staticmethod
    def _budget_tier_for_layer(layer: str):
        from core.control_plane import RoleTier

        return RoleTier.DETECTION if layer != "control_plane" else RoleTier.CONTROL_PLANE

    @staticmethod
    def _breaker_key(tenant_id: str, child_id: str):
        from core.control_plane import BreakerKey

        return BreakerKey(
            tenant_id=tenant_id,
            agent_id=child_id,
            tool="specialisation_fission_child",
            session_id=f"session::{child_id}",
        )

    def _record_spawn(self, proposal: SpecialisationFissionProposal, children: list[FissionChild], *, detail: str) -> None:
        self.event_log.record(
            event_type=FissionEventType.SPAWN,
            trigger_type=FissionTrigger.SPECIALISATION,
            triggering_watcher=proposal.triggering_watcher,
            threat_level=proposal.threat_level.name,
            parent_id=proposal.parent_id,
            parent_type=proposal.parent_type,
            child_ids=tuple(c.child_id for c in children),
            schema_id=proposal.schema_id,
            namespace=",".join(c.namespace for c in children),
            detail=detail,
        )

    def _reject(self, proposal: SpecialisationFissionProposal, detail: str) -> None:
        self.event_log.record(
            event_type=FissionEventType.REJECTED,
            trigger_type=FissionTrigger.SPECIALISATION,
            triggering_watcher=proposal.triggering_watcher,
            threat_level=proposal.threat_level.name,
            parent_id=proposal.parent_id,
            parent_type=proposal.parent_type,
            schema_id=proposal.schema_id,
            detail=detail,
        )

    def exhale(self, *, threat_level: ThreatLevel, triggering_watcher: str = "control_plane") -> tuple[str, ...]:
        if threat_level >= SPECIALISATION_THREAT_FLOOR:
            return ()
        retired: list[str] = []
        for child in self._children.values():
            if child.active:
                child.active = False
                retired.append(child.child_id)
                self.event_log.record(
                    event_type=FissionEventType.EXHALE,
                    trigger_type=FissionTrigger.SPECIALISATION,
                    triggering_watcher=triggering_watcher,
                    threat_level=threat_level.name,
                    parent_id=child.parent_id,
                    parent_type=child.agent_type,
                    child_ids=(child.child_id,),
                    schema_id=child.schema_id,
                    namespace=child.namespace,
                    detail="specialisation child retired after threat dropped below Level 2",
                )
        return tuple(retired)

    def children(self) -> tuple[FissionChild, ...]:
        return tuple(self._children.values())

    def held_net_new(self) -> tuple[HeldNetNewType, ...]:
        held: list[HeldNetNewType] = []
        for group in self._held_by_parent.values():
            held.extend(group)
        return tuple(held)


__all__ = [
    "SPECIALISATION_THREAT_FLOOR",
    "DEFAULT_MAX_SPECIALISATION_CHILDREN",
    "SubTypeKind",
    "SubTypeRegistry",
    "HeldNetNewType",
    "NetNewTypeSignOffGate",
    "ProposedSpecialist",
    "SpecialisationFissionProposal",
    "SpecialisationFissionController",
]
