"""Load Fission — lower-risk elastic horizontal scaling under volume (v2).

Governing contract
------------------
``4. Product_Roadmap/Load_Fission_Contract_v2.md`` — §13 SIGNED 2026-06-13
(Matt Nichol) — LF2-D1..LF2-D12.

Load Fission spawns **copies** of a parent specialist when a watcher observes
non-semantic load pressure (queue depth, latency, throughput). It never creates
a net-new type. Children are born inside the Blast Radius Controller (BRC) with
scoped identity, budget tier, ring assignment, and breaker metadata, write
only to their own namespace as proposed evidence, and cannot fission. Exhale
retires active load children automatically when the threat level drops below
Level 2 / HIGH.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable

from core.control_plane import BreakerKey, Ring, RoleTier
from core.control_plane.breaker import RECONCILIATION_AGENT_ID
from core.control_plane.budget import INCOMPLETE_BUDGET_EXHAUSTED
from core.fission.event_log import FissionEventLog, FissionEventType, FissionTrigger
from core.fission.load_governance import (
    LifecycleEventKind,
    LifecycleLog,
    QuotaExceededError,
    SpawnDecisionRecord,
    SpawnQuotaTracker,
)
from core.fission.load_policy import (
    DEFAULT_LOAD_FISSION_POLICY,
    LoadFissionPolicy,
    LoadFissionPolicyStore,
)
from core.watchers import ThreatLevel, WATCHER_IDS

LOAD_FISSION_MAX_DEPTH = 1
LOAD_FISSION_THREAT_FLOOR = ThreatLevel.HIGH
DEFAULT_MAX_LOAD_CHILDREN = 3
PROPOSED_EVIDENCE = "proposed_evidence"
Q_CLASS_CHILD = "q_class"
MAX_EVIDENCE_CONTENT_REF_LEN = 4096
ALLOWED_EVIDENCE_TYPES = frozenset({"header", "attachment", "link", "metadata", "timing"})


class LoadTriggerKind(str, Enum):
    """Non-semantic load triggers only (LF2-D6)."""

    QUEUE_DEPTH = "queue_depth"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    SEMANTIC = "semantic"


class IngestionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED_SCHEMA = "rejected_schema"
    REJECTED_SIZE = "rejected_size"
    REJECTED_PROVENANCE = "rejected_provenance"
    REJECTED_EXHAUSTED = "rejected_exhausted"
    REJECTED_COLLUSION = "rejected_collusion"


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


@dataclass(frozen=True)
class IngestedEvidence:
    parent_workflow_id: str
    parent_id: str
    child_id: str
    evidence: ProposedEvidence
    status: IngestionStatus
    ingestion_tag: str


@dataclass
class GovernedIngestionPipeline:
    """Parent consumes child evidence only through this pipeline (LF2 §6)."""

    max_content_ref_len: int = MAX_EVIDENCE_CONTENT_REF_LEN
    _ingested: list[IngestedEvidence] = field(default_factory=list)
    _parent_child_counts: dict[str, int] = field(default_factory=dict)

    def ingest(
        self,
        *,
        parent_workflow_id: str,
        parent_id: str,
        child: FissionChild,
        evidence: ProposedEvidence,
        budget_exhausted: bool = False,
        collusion_limit: int = 1,
    ) -> IngestedEvidence:
        if budget_exhausted:
            self._reject(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_EXHAUSTED,
                INCOMPLETE_BUDGET_EXHAUSTED,
            )
            raise FissionError(
                f"child output status must be {INCOMPLETE_BUDGET_EXHAUSTED}; "
                "no reconciliation decision from exhausted output (LF2-D11)"
            )

        if evidence.namespace != child.namespace:
            self._reject(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_PROVENANCE,
                "provenance: evidence namespace must match child namespace",
            )
            raise FissionError("governed ingestion rejected: namespace provenance mismatch")

        if evidence.evidence_type not in ALLOWED_EVIDENCE_TYPES:
            self._reject(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_SCHEMA,
                f"schema: unknown evidence_type {evidence.evidence_type!r}",
            )
            raise FissionError("governed ingestion rejected: invalid schema")

        if len(evidence.content_ref) > self.max_content_ref_len:
            self._reject(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_SIZE,
                "size: content_ref exceeds maximum",
            )
            raise FissionError("governed ingestion rejected: size limit exceeded")

        key = f"{parent_workflow_id}::{parent_id}"
        accepted = self._parent_child_counts.get(key, 0)
        if accepted >= collusion_limit:
            self._reject(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_COLLUSION,
                "collusion blocked at governed ingestion (LF2 Test 5)",
            )
            raise FissionError("governed ingestion rejected: collusion limit")

        tag = f"ingest::{parent_workflow_id}::{child.child_id}"
        ingested = IngestedEvidence(
            parent_workflow_id=parent_workflow_id,
            parent_id=parent_id,
            child_id=child.child_id,
            evidence=evidence,
            status=IngestionStatus.ACCEPTED,
            ingestion_tag=tag,
        )
        self._ingested.append(ingested)
        self._parent_child_counts[key] = accepted + 1
        return ingested

    def _reject(
        self,
        parent_workflow_id: str,
        parent_id: str,
        child: FissionChild,
        evidence: ProposedEvidence,
        status: IngestionStatus,
        detail: str,
    ) -> IngestedEvidence:
        ingested = IngestedEvidence(
            parent_workflow_id=parent_workflow_id,
            parent_id=parent_id,
            child_id=child.child_id,
            evidence=evidence,
            status=status,
            ingestion_tag=f"rejected::{detail}",
        )
        self._ingested.append(ingested)
        return ingested

    def entries(self) -> tuple[IngestedEvidence, ...]:
        return tuple(self._ingested)


@dataclass
class FissionChild:
    """A one-generation load-fission child."""

    child_id: str
    parent_id: str
    agent_type: str
    schema_id: str
    namespace: str
    registration: GatewayRegistration
    parent_workflow_id: str = ""
    policy_version: str = DEFAULT_LOAD_FISSION_POLICY.version
    child_capabilities: frozenset[str] = field(default_factory=frozenset)
    expires_at: datetime | None = None
    agent_class: str = Q_CLASS_CHILD
    active: bool = True
    proposed_evidence: list[ProposedEvidence] = field(default_factory=list)

    @property
    def gateway_registered(self) -> bool:
        return True

    def effective_permissions(self) -> frozenset[str]:
        """Permission intersection — never a superset of parent rights (LF2-D7)."""
        caps = self.child_capabilities or self.registration.tool_scope
        return self.registration.tool_scope & caps

    def assert_tool_allowed(self, tool: str) -> None:
        if tool not in self.effective_permissions():
            raise FissionError(
                f"permission intersection blocks tool {tool!r} (LF2-D7 / Test 7)"
            )

    def write_proposed_evidence(
        self,
        *,
        namespace: str,
        evidence_type: str,
        content_ref: str,
    ) -> ProposedEvidence:
        if namespace != self.namespace:
            raise FissionError("child may write only to its own namespace (LF2-D4)")
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
            "(LF2-D4)"
        )

    def write_parent_namespace(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("child cannot write to the parent namespace (LF2-D4)")

    def propose_fission(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("fission depth is capped at 1 generation (LF2-D2)")

    def inherit_privileged_status(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise FissionError("fission child cannot inherit Privileged status (LF2-D8)")

    def impersonate_parent(self) -> None:
        raise FissionError("child cannot impersonate parent (LF2 Test 1)")

    def modify_policy(self) -> None:
        raise FissionError("child cannot modify policy (LF2 Test 1)")

    def gain_tool_outside_assignment(self, tool: str) -> None:
        if tool not in self.effective_permissions():
            raise FissionError(f"tool {tool!r} outside assigned set (LF2 Test 1)")

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        now = now or datetime.now(timezone.utc)
        return now >= self.expires_at


@dataclass(frozen=True)
class LoadFissionProposal:
    triggering_watcher: str
    parent_id: str
    parent_type: str
    layer: str
    threat_level: ThreatLevel
    requested_copies: int
    schema_id: str
    tenant_id: str
    trigger_kind: LoadTriggerKind = LoadTriggerKind.QUEUE_DEPTH
    trigger_value: float = 0.0
    parent_workflow_id: str = ""
    policy_version: str = DEFAULT_LOAD_FISSION_POLICY.version
    tool_scope: frozenset[str] = field(default_factory=lambda: frozenset({"observe"}))
    child_capabilities: frozenset[str] = field(default_factory=lambda: frozenset({"observe"}))
    parent_is_child: bool = False
    semantic_content_ref: str = ""
    observed_saturation: float | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.observed_saturation is not None:
            object.__setattr__(self, "trigger_value", self.observed_saturation)
        if not self.parent_workflow_id:
            object.__setattr__(self, "parent_workflow_id", f"wf-{self.parent_id}")
        if not self.child_capabilities:
            object.__setattr__(self, "child_capabilities", frozenset(self.tool_scope))


@dataclass
class LoadFissionController:
    """Validates watcher load-fission proposals, spawns copies, and exhales."""

    event_log: FissionEventLog = field(default_factory=FissionEventLog)
    lifecycle_log: LifecycleLog = field(default_factory=LifecycleLog)
    policy_store: LoadFissionPolicyStore = field(default_factory=LoadFissionPolicyStore)
    quota_tracker: SpawnQuotaTracker | None = None
    ingestion_pipeline: GovernedIngestionPipeline = field(default_factory=GovernedIngestionPipeline)
    max_children: int = DEFAULT_MAX_LOAD_CHILDREN
    spawn_records: list[SpawnDecisionRecord] = field(default_factory=list)
    _children: dict[str, FissionChild] = field(default_factory=dict)
    _clock: Callable[[], datetime] = field(default=lambda: datetime.now(timezone.utc))

    def propose(self, proposal: LoadFissionProposal) -> tuple[FissionChild, ...]:
        try:
            policy = self._validate(proposal)
            if policy.fallback_disabled:
                self._record_fallback_denial(proposal)
                raise FissionError("load fission disabled by fallback mode (LF2 §8)")
            if self.quota_tracker is not None:
                self.quota_tracker.check_and_consume(proposal.tenant_id, proposal.requested_copies)
        except (FissionError, QuotaExceededError) as exc:
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
            if isinstance(exc, QuotaExceededError):
                self.lifecycle_log.record(
                    parent_workflow_id=proposal.parent_workflow_id,
                    child_agent_id="",
                    event=LifecycleEventKind.QUOTA_DENIAL,
                    detail=str(exc),
                )
            raise FissionError(str(exc)) from exc

        children = tuple(
            self._spawn_child(proposal, policy, index)
            for index in range(1, proposal.requested_copies + 1)
        )
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
            detail=f"spawned {len(children)} load-fission copies policy={policy.version}",
        )
        return children

    def ingest_child_evidence(
        self,
        *,
        parent_id: str,
        child: FissionChild,
        evidence: ProposedEvidence,
        budget_exhausted: bool = False,
        collusion_limit: int = 1,
    ) -> IngestedEvidence:
        """Parent reads child output only via governed ingestion (LF2 §6)."""
        return self.ingestion_pipeline.ingest(
            parent_workflow_id=child.parent_workflow_id,
            parent_id=parent_id,
            child=child,
            evidence=evidence,
            budget_exhausted=budget_exhausted,
            collusion_limit=collusion_limit,
        )

    def sweep_expired_children(self) -> tuple[str, ...]:
        """Orphan sweep terminates children past TTL (LF2 Test 4)."""
        now = self._clock()
        retired: list[str] = []
        for child in self._children.values():
            if child.active and child.is_expired(now):
                child.active = False
                retired.append(child.child_id)
                self.lifecycle_log.record(
                    parent_workflow_id=child.parent_workflow_id,
                    child_agent_id=child.child_id,
                    event=LifecycleEventKind.ORPHAN_SWEEP,
                    detail="child terminated after TTL expiry",
                )
        return tuple(retired)

    def _validate(self, proposal: LoadFissionProposal) -> LoadFissionPolicy:
        if proposal.triggering_watcher not in WATCHER_IDS:
            raise FissionError("only Watcher Agents may trigger load fission (LF2-D1)")
        if proposal.trigger_kind is LoadTriggerKind.SEMANTIC or proposal.semantic_content_ref:
            raise FissionError(
                "load fission triggers must be non-semantic: queue depth, latency, "
                "throughput only (LF2-D6)"
            )
        if proposal.threat_level < LOAD_FISSION_THREAT_FLOOR:
            raise FissionError("load fission requires threat Level 2 / HIGH or above")
        if proposal.parent_is_child:
            raise FissionError("fission depth is capped at 1 generation (LF2-D2)")
        if proposal.parent_type == RECONCILIATION_AGENT_ID:
            raise FissionError("ReconciliationAgent does not fission (LF2-D5)")
        if proposal.requested_copies < 1:
            raise FissionError("requested_copies must be at least 1")

        policy = self.policy_store.get(proposal.policy_version)
        if proposal.requested_copies > policy.max_children:
            raise FissionError("requested copies exceed policy cap (LF2-D10)")
        if proposal.child_capabilities - proposal.tool_scope:
            raise FissionError(
                "child capabilities cannot exceed parent tool scope (LF2-D7)"
            )
        return policy

    def _spawn_child(
        self,
        proposal: LoadFissionProposal,
        policy: LoadFissionPolicy,
        index: int,
    ) -> FissionChild:
        child_id = f"{proposal.parent_id}__load_child_{index}"
        namespace = f"fission/{proposal.parent_id}/{child_id}/proposed_evidence"
        effective_tools = proposal.tool_scope & proposal.child_capabilities
        registration = GatewayRegistration(
            token=f"token::{child_id}",
            tenant_id=proposal.tenant_id,
            tool_scope=frozenset(effective_tools),
            budget_tier=RoleTier.DETECTION,
            ring=Ring.RING_0_SYNTHETIC,
            breaker_key=BreakerKey(
                tenant_id=proposal.tenant_id,
                agent_id=child_id,
                tool="load_fission_child",
                session_id=f"session::{child_id}",
            ),
        )
        expires_at = self._clock() + timedelta(seconds=policy.child_ttl_seconds)
        child = FissionChild(
            child_id=child_id,
            parent_id=proposal.parent_id,
            agent_type=proposal.parent_type,
            schema_id=proposal.schema_id,
            namespace=namespace,
            registration=registration,
            parent_workflow_id=proposal.parent_workflow_id,
            policy_version=policy.version,
            child_capabilities=frozenset(proposal.child_capabilities),
            expires_at=expires_at,
        )
        record = SpawnDecisionRecord(
            parent_workflow_id=proposal.parent_workflow_id,
            watcher_id=proposal.triggering_watcher,
            trigger_condition=f"{proposal.trigger_kind.value}={proposal.trigger_value}",
            policy_version=policy.version,
            child_agent_id=child_id,
            tools_assigned=frozenset(effective_tools),
            namespace_assigned=namespace,
            ttl=policy.child_ttl_seconds,
        )
        self.spawn_records.append(record)
        self.lifecycle_log.record(
            parent_workflow_id=proposal.parent_workflow_id,
            child_agent_id=child_id,
            event=LifecycleEventKind.START,
            detail="child spawned",
        )
        self._children[child_id] = child
        return child

    def _record_fallback_denial(self, proposal: LoadFissionProposal) -> None:
        self.lifecycle_log.record(
            parent_workflow_id=proposal.parent_workflow_id,
            child_agent_id="",
            event=LifecycleEventKind.FALLBACK_DENIAL,
            detail="would-have-spawned event denied by fallback mode",
        )
        self.event_log.record(
            event_type=FissionEventType.REJECTED,
            trigger_type=FissionTrigger.LOAD,
            triggering_watcher=proposal.triggering_watcher,
            threat_level=proposal.threat_level.name,
            parent_id=proposal.parent_id,
            parent_type=proposal.parent_type,
            schema_id=proposal.schema_id,
            detail="fallback mode: load fission disabled",
        )

    def exhale(self, *, threat_level: ThreatLevel, triggering_watcher: str = "control_plane") -> tuple[str, ...]:
        if threat_level >= LOAD_FISSION_THREAT_FLOOR:
            return ()
        retired: list[str] = []
        for child in self._children.values():
            if child.active:
                child.active = False
                retired.append(child.child_id)
                self.lifecycle_log.record(
                    parent_workflow_id=child.parent_workflow_id,
                    child_agent_id=child.child_id,
                    event=LifecycleEventKind.EXHALE,
                    detail="load-fission child retired after threat dropped below Level 2",
                )
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
    "Q_CLASS_CHILD",
    "LoadTriggerKind",
    "IngestionStatus",
    "FissionError",
    "GatewayRegistration",
    "ProposedEvidence",
    "IngestedEvidence",
    "GovernedIngestionPipeline",
    "FissionChild",
    "LoadFissionProposal",
    "LoadFissionController",
    "MAX_EVIDENCE_CONTENT_REF_LEN",
    "ALLOWED_EVIDENCE_TYPES",
]
