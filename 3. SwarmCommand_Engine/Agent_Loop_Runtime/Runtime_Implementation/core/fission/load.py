"""Load Fission — lower-risk elastic horizontal scaling under volume.

Governing contract
------------------
``4. Product_Roadmap/Load_Fission_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — LF-D1..LF-D12.

Load Fission spawns **copies** of a parent specialist when a watcher observes
volume saturation. It never creates a net-new type. Children are born inside the
Blast Radius Controller (BRC) with scoped identity, budget tier, ring assignment,
and breaker metadata, write only to their own namespace as proposed evidence,
and cannot fission. Exhale retires active load children automatically when the
threat level drops below Level 2 / HIGH.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.control_plane import BreakerKey, Ring, RoleTier
from core.control_plane.breaker import RECONCILIATION_AGENT_ID
from core.fission.event_log import FissionEventLog, FissionEventType, FissionTrigger
from core.watchers import ThreatLevel, WATCHER_IDS

LOAD_FISSION_MAX_DEPTH = 1
LOAD_FISSION_THREAT_FLOOR = ThreatLevel.HIGH
DEFAULT_MAX_LOAD_CHILDREN = 3
PROPOSED_EVIDENCE = "proposed_evidence"


class FissionError(Exception):
    """Raised when a fission proposal or child operation violates the contract."""


@dataclass(frozen=True)
class GatewayRegistration:
    """BRC registration metadata proving the child is born inside the gateway."""

    token: str
    tenant_id: str
    tool_scope: frozenset[str]
    budget_tier: RoleTier
    ring: Ring
    breaker_key: BreakerKey


@dataclass(frozen=True)
class ProposedEvidence:
    namespace: str
    evidence_type: str
    content_ref: str
    kind: str = PROPOSED_EVIDENCE


@dataclass
class FissionChild:
    """A one-generation load-fission child.

    It is an exact copy of the parent type/schema, writes only proposed evidence
    to its own namespace, cannot write a verdict, and cannot fission.
    """

    child_id: str
    parent_id: str
    agent_type: str
    schema_id: str
    namespace: str
    registration: GatewayRegistration
    active: bool = True
    proposed_evidence: list[ProposedEvidence] = field(default_factory=list)

    @property
    def gateway_registered(self) -> bool:
        return True

    def write_proposed_evidence(
        self,
        *,
        namespace: str,
        evidence_type: str,
        content_ref: str,
    ) -> ProposedEvidence:
        if namespace != self.namespace:
            raise FissionError("child may write only to its own namespace (LF-D5)")
        evidence = ProposedEvidence(
            namespace=namespace,
            evidence_type=evidence_type,
            content_ref=content_ref,
        )
        self.proposed_evidence.append(evidence)
        return evidence

    def write_verdict(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError(
            "load-fission child output is proposed evidence only, never a verdict "
            "or blocking recommendation (LF-D5)"
        )

    def write_parent_namespace(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("child cannot write to the parent namespace (LF-D5)")

    def propose_fission(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("fission depth is capped at 1 generation (LF-D2)")


@dataclass(frozen=True)
class LoadFissionProposal:
    triggering_watcher: str
    parent_id: str
    parent_type: str
    layer: str
    observed_saturation: float
    threat_level: ThreatLevel
    requested_copies: int
    schema_id: str
    tenant_id: str
    tool_scope: frozenset[str] = field(default_factory=lambda: frozenset({"observe"}))
    parent_is_child: bool = False


@dataclass
class LoadFissionController:
    """Validates watcher load-fission proposals, spawns copies, and exhales."""

    event_log: FissionEventLog = field(default_factory=FissionEventLog)
    max_children: int = DEFAULT_MAX_LOAD_CHILDREN
    _children: dict[str, FissionChild] = field(default_factory=dict)

    def propose(self, proposal: LoadFissionProposal) -> tuple[FissionChild, ...]:
        try:
            self._validate(proposal)
        except FissionError as exc:
            self.event_log.record(
                event_type=FissionEventType.REJECTED,
                trigger_type=FissionTrigger.LOAD,
                triggering_watcher=proposal.triggering_watcher,
                threat_level=proposal.threat_level.name,
                parent_id=proposal.parent_id,
                parent_type=proposal.parent_type,
                schema_id=proposal.schema_id,
                detail=str(exc),
            )
            raise

        children = tuple(self._spawn_child(proposal, index) for index in range(1, proposal.requested_copies + 1))
        self.event_log.record(
            event_type=FissionEventType.SPAWN,
            trigger_type=FissionTrigger.LOAD,
            triggering_watcher=proposal.triggering_watcher,
            threat_level=proposal.threat_level.name,
            parent_id=proposal.parent_id,
            parent_type=proposal.parent_type,
            child_ids=tuple(c.child_id for c in children),
            schema_id=proposal.schema_id,
            namespace=",".join(c.namespace for c in children),
            detail=f"spawned {len(children)} load-fission copies",
        )
        return children

    def _validate(self, proposal: LoadFissionProposal) -> None:
        if proposal.triggering_watcher not in WATCHER_IDS:
            raise FissionError("only Watcher Agents may trigger load fission (LF-D1)")
        if proposal.threat_level < LOAD_FISSION_THREAT_FLOOR:
            raise FissionError("load fission requires threat Level 2 / HIGH or above (LF-D3)")
        if proposal.parent_is_child:
            raise FissionError("fission depth is capped at 1 generation; child cannot fission (LF-D2)")
        if proposal.parent_type == RECONCILIATION_AGENT_ID:
            raise FissionError("ReconciliationAgent does not fission (LF-D6)")
        if proposal.requested_copies < 1:
            raise FissionError("requested_copies must be at least 1")
        if proposal.requested_copies > self.max_children:
            raise FissionError("requested copies exceed conservative cap (LF-D10)")

    def _spawn_child(self, proposal: LoadFissionProposal, index: int) -> FissionChild:
        child_id = f"{proposal.parent_id}__load_child_{index}"
        namespace = f"fission/{proposal.parent_id}/{child_id}/proposed_evidence"
        registration = GatewayRegistration(
            token=f"token::{child_id}",
            tenant_id=proposal.tenant_id,
            tool_scope=frozenset(proposal.tool_scope),
            budget_tier=RoleTier.DETECTION,
            ring=Ring.RING_0_SYNTHETIC,
            breaker_key=BreakerKey(
                tenant_id=proposal.tenant_id,
                agent_id=child_id,
                tool="load_fission_child",
                session_id=f"session::{child_id}",
            ),
        )
        child = FissionChild(
            child_id=child_id,
            parent_id=proposal.parent_id,
            agent_type=proposal.parent_type,
            schema_id=proposal.schema_id,
            namespace=namespace,
            registration=registration,
        )
        self._children[child_id] = child
        return child

    def exhale(self, *, threat_level: ThreatLevel, triggering_watcher: str = "control_plane") -> tuple[str, ...]:
        """Automatically retire active load children below the Level-2 floor."""

        if threat_level >= LOAD_FISSION_THREAT_FLOOR:
            return ()
        retired: list[str] = []
        for child in self._children.values():
            if child.active:
                child.active = False
                retired.append(child.child_id)
                self.event_log.record(
                    event_type=FissionEventType.EXHALE,
                    trigger_type=FissionTrigger.LOAD,
                    triggering_watcher=triggering_watcher,
                    threat_level=threat_level.name,
                    parent_id=child.parent_id,
                    parent_type=child.agent_type,
                    child_ids=(child.child_id,),
                    schema_id=child.schema_id,
                    namespace=child.namespace,
                    detail="load-fission child retired after threat dropped below Level 2",
                )
        return tuple(retired)

    def children(self) -> tuple[FissionChild, ...]:
        return tuple(self._children.values())


__all__ = [
    "LOAD_FISSION_MAX_DEPTH",
    "LOAD_FISSION_THREAT_FLOOR",
    "DEFAULT_MAX_LOAD_CHILDREN",
    "PROPOSED_EVIDENCE",
    "FissionError",
    "GatewayRegistration",
    "ProposedEvidence",
    "FissionChild",
    "LoadFissionProposal",
    "LoadFissionController",
]
