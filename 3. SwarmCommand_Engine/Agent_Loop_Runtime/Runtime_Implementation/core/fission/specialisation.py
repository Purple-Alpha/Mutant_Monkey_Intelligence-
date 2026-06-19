"""Specialisation Fission — qualitative division into narrower specialists (v2).

Governing contract
------------------
``4. Product_Roadmap/Specialisation_Fission_Contract_v2.md`` — §18 SIGNED
2026-06-13 (Matt Nichol) — SF2-D1..SF2-D12.

Specialisation Fission is the higher-risk fission trigger: a parent specialist
divides because its problem space became too complex for one specialist. Known
sub-types may spawn under the gates; net-new agent types are held inert until
Matt signs off, then activate at Ring 0.

v2 incorporates all Load Fission v2 locked decisions (watcher-only, depth 1,
governed ingestion, quotas, fallback, anti-semantic triggers) plus the Purple
Fission Curriculum, Light/Normal/Deep intensity, twelve fixed child schemas,
and Red/Blue boundary enforcement.
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
from core.fission.load import (
    ALLOWED_EVIDENCE_TYPES,
    FissionChild,
    FissionError,
    GatewayRegistration,
    GovernedIngestionPipeline,
    IngestedEvidence,
    IngestionStatus,
    LOAD_FISSION_THREAT_FLOOR,
    MAX_EVIDENCE_CONTENT_REF_LEN,
    PROPOSED_EVIDENCE,
    ProposedEvidence,
    Q_CLASS_CHILD,
)
from core.fission.load_governance import (
    LifecycleEventKind,
    LifecycleLog,
    QuotaExceededError,
    SpawnDecisionRecord,
    SpawnQuotaTracker,
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

# Global schema prohibitions (SF2 §7).
PROHIBITED_OUTPUT_FIELDS = frozenset(
    {
        "verdict",
        "risk_score",
        "allow",
        "block",
        "fraud_label",
        "recommendation",
        "mutation_instruction",
        "client_facing_claim",
    }
)


class IntensityLevel(str, Enum):
    LIGHT = "light"
    NORMAL = "normal"
    DEEP = "deep"


class SpecializationRole(str, Enum):
    RED = "red"
    BLUE = "blue"


class SubTypeKind(str, Enum):
    KNOWN = "known"
    NET_NEW = "net_new"


@dataclass(frozen=True)
class CurriculumPair:
    pair_id: str
    red_id: str
    blue_id: str
    red_schema_id: str
    blue_schema_id: str


PURPLE_FISSION_CURRICULUM: tuple[CurriculumPair, ...] = (
    CurriculumPair("header", "red_header_injection_sim", "blue_header_forensics", "sf2_red_header_v1", "sf2_blue_header_v1"),
    CurriculumPair("linguistic", "red_linguistic_impersonation_sim", "blue_linguistic_decomposition", "sf2_red_linguistic_v1", "sf2_blue_linguistic_v1"),
    CurriculumPair("payload", "red_payload_obfuscation_sim", "blue_payload_deobfuscation", "sf2_red_payload_v1", "sf2_blue_payload_v1"),
    CurriculumPair("financial", "red_financial_fraud_pattern_sim", "blue_financial_pattern_extraction", "sf2_red_financial_v1", "sf2_blue_financial_v1"),
    CurriculumPair("attachment", "red_attachment_threat_sim", "blue_attachment_deep_scan", "sf2_red_attachment_v1", "sf2_blue_attachment_v1"),
    CurriculumPair("narrative", "red_lateral_narrative_sim", "blue_narrative_reconstruction", "sf2_red_narrative_v1", "sf2_blue_narrative_v1"),
)

CURRICULUM_BY_SPECIALIST: dict[str, tuple[CurriculumPair, SpecializationRole]] = {}
for _pair in PURPLE_FISSION_CURRICULUM:
    CURRICULUM_BY_SPECIALIST[_pair.red_id] = (_pair, SpecializationRole.RED)
    CURRICULUM_BY_SPECIALIST[_pair.blue_id] = (_pair, SpecializationRole.BLUE)

FIXED_SCHEMA_ALLOWED_FIELDS: dict[str, frozenset[str]] = {
    "sf2_red_header_v1": frozenset({"scenario_output", "pressure_vector"}),
    "sf2_blue_header_v1": frozenset({"header_facts", "observed_headers"}),
    "sf2_red_linguistic_v1": frozenset({"pressure_scenario", "linguistic_vector"}),
    "sf2_blue_linguistic_v1": frozenset({"linguistic_features", "phrase_categories"}),
    "sf2_red_payload_v1": frozenset({"obfuscation_scenario", "payload_vector"}),
    "sf2_blue_payload_v1": frozenset({"payload_features", "encoding_observations"}),
    "sf2_red_financial_v1": frozenset({"pressure_pattern", "financial_vector"}),
    "sf2_blue_financial_v1": frozenset({"financial_features", "payment_indicators"}),
    "sf2_red_attachment_v1": frozenset({"attachment_pressure", "threat_vector"}),
    "sf2_blue_attachment_v1": frozenset({"attachment_features", "scan_observations"}),
    "sf2_red_narrative_v1": frozenset({"narrative_pressure", "thread_vector"}),
    "sf2_blue_narrative_v1": frozenset({"narrative_features", "thread_observations"}),
}


@dataclass(frozen=True)
class SpecialisationFissionPolicy:
    version: str
    max_children: int
    max_depth: int = 1
    fallback_disabled: bool = False
    per_tenant_spawn_quota: int = 10
    global_spawn_quota: int = 100
    circuit_breaker_threshold: int = 5
    child_ttl_seconds: float = 300.0
    deep_requires_approval: bool = True

    def with_fallback_disabled(self) -> SpecialisationFissionPolicy:
        return SpecialisationFissionPolicy(
            version=f"{self.version}+fallback_disabled",
            max_children=self.max_children,
            max_depth=self.max_depth,
            fallback_disabled=True,
            per_tenant_spawn_quota=self.per_tenant_spawn_quota,
            global_spawn_quota=self.global_spawn_quota,
            circuit_breaker_threshold=self.circuit_breaker_threshold,
            child_ttl_seconds=self.child_ttl_seconds,
            deep_requires_approval=self.deep_requires_approval,
        )


DEFAULT_SPECIALISATION_FISSION_POLICY = SpecialisationFissionPolicy(
    version="sf2-v1.0.0", max_children=3
)


class SpecialisationFissionPolicyStore:
    def __init__(self, policies: dict[str, SpecialisationFissionPolicy] | None = None) -> None:
        self._policies: dict[str, SpecialisationFissionPolicy] = dict(policies or {})
        if DEFAULT_SPECIALISATION_FISSION_POLICY.version not in self._policies:
            self._policies[DEFAULT_SPECIALISATION_FISSION_POLICY.version] = (
                DEFAULT_SPECIALISATION_FISSION_POLICY
            )

    def get(self, version: str) -> SpecialisationFissionPolicy:
        if version not in self._policies:
            raise KeyError(f"unknown specialisation fission policy version: {version}")
        return self._policies[version]

    def register(self, policy: SpecialisationFissionPolicy) -> SpecialisationFissionPolicy:
        if policy.version in self._policies:
            raise ValueError(f"policy version already registered: {policy.version}")
        self._policies[policy.version] = policy
        return policy


@dataclass(frozen=True)
class SpecialisationSpawnDecisionRecord:
    parent_workflow_id: str
    watcher_id: str
    trigger_condition: str
    policy_version: str
    child_agent_id: str
    tools_assigned: frozenset[str]
    namespace_assigned: str
    ttl: float
    intensity_level: str
    scenario_id: str
    scenario_version: str
    specialization_role: str
    known_or_net_new: str
    subtype_registry_result: str
    ring_assignment: str
    approval_reference: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SpecialisationGovernedIngestionPipeline(GovernedIngestionPipeline):
    """Governed ingestion with scenario lock and Red/Blue boundary checks (SF2 §11)."""

    _locked_scenarios: dict[str, str] = field(default_factory=dict)

    def lock_scenario(self, parent_workflow_id: str, scenario_id: str) -> None:
        self._locked_scenarios[parent_workflow_id] = scenario_id

    def locked_scenario(self, parent_workflow_id: str) -> str | None:
        return self._locked_scenarios.get(parent_workflow_id)

    def ingest_specialisation(
        self,
        *,
        parent_workflow_id: str,
        parent_id: str,
        child: SpecialisationFissionChild,
        evidence: ProposedEvidence,
        structured_payload: dict[str, object] | None = None,
        budget_exhausted: bool = False,
        collusion_limit: int = 1,
        scenario_id: str = "",
    ) -> IngestedEvidence:
        locked = self._locked_scenarios.get(parent_workflow_id)
        if locked and scenario_id and scenario_id != locked:
            self._reject_specialisation(
                parent_workflow_id,
                parent_id,
                child,
                evidence,
                IngestionStatus.REJECTED_SCHEMA,
                "scenario lock: active scenario cannot change mid-workflow (SF2 Test 8)",
            )
            raise FissionError("governed ingestion rejected: scenario injection blocked")

        if structured_payload is not None:
            self._validate_structured_payload(child, structured_payload)

        if child.specialization_role is SpecializationRole.RED:
            if evidence.evidence_type == "cross_child_transfer":
                self._reject_specialisation(
                    parent_workflow_id,
                    parent_id,
                    child,
                    evidence,
                    IngestionStatus.REJECTED_COLLUSION,
                    "red-blue collusion blocked at governed ingestion (SF2 Test 7)",
                )
                raise FissionError("governed ingestion rejected: red-blue collusion")

        return self.ingest(
            parent_workflow_id=parent_workflow_id,
            parent_id=parent_id,
            child=child,
            evidence=evidence,
            budget_exhausted=budget_exhausted,
            collusion_limit=collusion_limit,
        )

    def _validate_structured_payload(
        self,
        child: SpecialisationFissionChild,
        payload: dict[str, object],
    ) -> None:
        prohibited = PROHIBITED_OUTPUT_FIELDS & payload.keys()
        if prohibited:
            raise FissionError(
                f"schema violation: prohibited fields {sorted(prohibited)!r} (SF2 §7)"
            )
        allowed = FIXED_SCHEMA_ALLOWED_FIELDS.get(child.schema_id)
        if allowed is None:
            return
        extra = set(payload) - allowed
        if extra:
            raise FissionError(
                f"schema violation: fields {sorted(extra)!r} not in fixed schema "
                f"{child.schema_id!r}"
            )

    def _reject_specialisation(
        self,
        parent_workflow_id: str,
        parent_id: str,
        child: SpecialisationFissionChild,
        evidence: ProposedEvidence,
        status: IngestionStatus,
        detail: str,
    ) -> IngestedEvidence:
        return IngestedEvidence(
            parent_workflow_id=parent_workflow_id,
            parent_id=parent_id,
            child_id=child.child_id,
            evidence=evidence,
            status=status,
            ingestion_tag=f"rejected::{detail}",
        )


@dataclass
class SpecialisationFissionChild(FissionChild):
    specialization_role: SpecializationRole = SpecializationRole.BLUE
    scenario_id: str = ""
    scenario_version: str = "1.0.0"
    curriculum_pair_id: str = ""
    intensity_level: IntensityLevel = IntensityLevel.NORMAL
    known_or_net_new: str = "known"

    def write_tenant_data(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
        if self.specialization_role is SpecializationRole.RED:
            raise FissionError("red child has zero write access to tenant data (SF2 §8)")

    def influence_blue_child(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
        if self.specialization_role is SpecializationRole.RED:
            raise FissionError(
                "red child cannot influence blue children (SF2 §8 / Test 7)"
            )

    def pass_to_blue_namespace(self, *, target_namespace: str, content_ref: str) -> ProposedEvidence:
        if self.specialization_role is not SpecializationRole.RED:
            raise FissionError("only red children attempt cross-child transfer in Test 7")
        raise FissionError(
            "namespace isolation blocks red-to-blue transfer (SF2 Test 7)"
        )

    def read_parent_raw_namespace(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
        if self.specialization_role is SpecializationRole.BLUE:
            raise FissionError(
                "blue child cannot read parent raw namespace directly (SF2 §9)"
            )

    def mutate_active_scenario(self, *, new_scenario_id: str) -> None:
        raise FissionError(
            "scenario is locked per workflow; mutation blocked (SF2 Test 8)"
        )

    def emit_prohibited_field(self, field_name: str, value: object) -> None:
        if field_name in PROHIBITED_OUTPUT_FIELDS:
            raise FissionError(
                f"prohibited output field {field_name!r} (SF2 §7)"
            )


@dataclass
class SubTypeRegistry:
    """Deterministic authority on known vs net-new agent types (SF-D6)."""

    _known_types: set[str] = field(default_factory=set)

    def register_existing(self, agent_type: str) -> None:
        if not agent_type:
            raise FissionError("agent_type is required")
        self._known_types.add(agent_type)

    def classify(self, agent_type: str) -> SubTypeKind:
        if agent_type in CURRICULUM_BY_SPECIALIST:
            return SubTypeKind.KNOWN
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
    parent_workflow_id: str = ""
    policy_version: str = DEFAULT_SPECIALISATION_FISSION_POLICY.version
    intensity_level: IntensityLevel | None = None
    scenario_id: str = ""
    scenario_version: str = "1.0.0"
    semantic_content_ref: str = ""
    approval_reference: str = ""
    tool_scope: frozenset[str] = field(default_factory=lambda: frozenset({"observe"}))
    child_capabilities: frozenset[str] = field(default_factory=lambda: frozenset({"observe"}))

    def __post_init__(self) -> None:
        if not self.parent_workflow_id:
            object.__setattr__(self, "parent_workflow_id", f"wf-{self.parent_id}")
        if not self.scenario_id and self.intensity_level is not None:
            object.__setattr__(self, "scenario_id", f"scenario::{self.parent_workflow_id}")
        if not self.child_capabilities:
            object.__setattr__(self, "child_capabilities", frozenset(self.tool_scope))


@dataclass
class SpecialisationFissionController:
    """Validates specialisation proposals, holds net-new types, and spawns."""

    registry: SubTypeRegistry = field(default_factory=SubTypeRegistry)
    event_log: FissionEventLog = field(default_factory=FissionEventLog)
    lifecycle_log: LifecycleLog = field(default_factory=LifecycleLog)
    policy_store: SpecialisationFissionPolicyStore = field(
        default_factory=SpecialisationFissionPolicyStore
    )
    quota_tracker: SpawnQuotaTracker | None = None
    ingestion_pipeline: SpecialisationGovernedIngestionPipeline = field(
        default_factory=SpecialisationGovernedIngestionPipeline
    )
    sign_off_gate: NetNewTypeSignOffGate | None = None
    max_children: int = DEFAULT_MAX_SPECIALISATION_CHILDREN
    spawn_records: list[SpecialisationSpawnDecisionRecord] = field(default_factory=list)
    _children: dict[str, SpecialisationFissionChild] = field(default_factory=dict)
    _held_by_parent: dict[str, tuple[HeldNetNewType, ...]] = field(default_factory=dict)
    _clock: Callable[[], datetime] = field(default=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.sign_off_gate is None:
            self.sign_off_gate = NetNewTypeSignOffGate(event_log=self.event_log)
        else:
            self.sign_off_gate.event_log = self.event_log

    def propose(self, proposal: SpecialisationFissionProposal) -> tuple[SpecialisationFissionChild, ...]:
        try:
            policy = self._validate(proposal)
            if policy.fallback_disabled:
                self._record_fallback_denial(proposal)
                raise FissionError(
                    "specialisation fission disabled by fallback mode (SF2 §13)"
                )
            if self.quota_tracker is not None:
                self.quota_tracker.check_and_consume(
                    proposal.tenant_id, len(proposal.proposed_children)
                )
            if proposal.intensity_level is not None and proposal.scenario_id:
                self.ingestion_pipeline.lock_scenario(
                    proposal.parent_workflow_id, proposal.scenario_id
                )
        except (FissionError, QuotaExceededError) as exc:
            self._reject(proposal, str(exc))
            if isinstance(exc, QuotaExceededError):
                raise FissionError(str(exc)) from exc
            raise

        spawned: list[SpecialisationFissionChild] = []
        held: list[HeldNetNewType] = []
        for specialist in proposal.proposed_children:
            kind = self.registry.classify(specialist.child_type)
            if kind is SubTypeKind.KNOWN:
                spawned.append(self._spawn_child(proposal, specialist, kind, policy))
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
    ) -> SpecialisationFissionChild:
        assert self.sign_off_gate is not None
        held = self.sign_off_gate.sign_off(child_type=child_type, actor_id=actor_id)
        self.registry.register_signed_off(child_type, signed_off=True)
        policy = self.policy_store.get(DEFAULT_SPECIALISATION_FISSION_POLICY.version)
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
        child = self._spawn_child(
            proposal, proposal.proposed_children[0], SubTypeKind.NET_NEW, policy
        )
        self._record_spawn(proposal, [child], detail="activated signed-off net-new type")
        return child

    def ingest_child_evidence(
        self,
        *,
        parent_id: str,
        child: SpecialisationFissionChild,
        evidence: ProposedEvidence,
        structured_payload: dict[str, object] | None = None,
        budget_exhausted: bool = False,
        collusion_limit: int = 1,
        scenario_id: str = "",
    ) -> IngestedEvidence:
        return self.ingestion_pipeline.ingest_specialisation(
            parent_workflow_id=child.parent_workflow_id,
            parent_id=parent_id,
            child=child,
            evidence=evidence,
            structured_payload=structured_payload,
            budget_exhausted=budget_exhausted,
            collusion_limit=collusion_limit,
            scenario_id=scenario_id or child.scenario_id,
        )

    def sweep_expired_children(self) -> tuple[str, ...]:
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
                    detail="specialisation child terminated after TTL expiry",
                )
        return tuple(retired)

    def _validate(self, proposal: SpecialisationFissionProposal) -> SpecialisationFissionPolicy:
        if proposal.triggering_watcher not in WATCHER_IDS:
            raise FissionError("only Watcher Agents may trigger specialisation fission (SF-D1)")
        if proposal.semantic_content_ref:
            raise FissionError(
                "fission triggers must be non-semantic; email content cannot trigger "
                "fission (SF2 §6 / Test 2)"
            )
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

        policy = self.policy_store.get(proposal.policy_version)
        if len(proposal.proposed_children) > policy.max_children:
            raise FissionError("proposed child count exceeds policy cap (SF2)")
        if proposal.child_capabilities - proposal.tool_scope:
            raise FissionError("child capabilities cannot exceed parent tool scope (SF2)")

        if proposal.intensity_level is not None:
            self._validate_intensity(proposal, policy)
        return policy

    def _validate_intensity(
        self,
        proposal: SpecialisationFissionProposal,
        policy: SpecialisationFissionPolicy,
    ) -> None:
        children = proposal.proposed_children
        roles = [
            CURRICULUM_BY_SPECIALIST.get(s.child_type, (None, None))[1]
            for s in children
        ]
        if proposal.intensity_level is IntensityLevel.LIGHT:
            if any(r is SpecializationRole.RED for r in roles if r):
                raise FissionError("Light intensity allows Blue children only (SF2 §4)")
            if len(children) > 1:
                raise FissionError("Light intensity allows max 1 Blue child per workflow (SF2 §4)")
        elif proposal.intensity_level is IntensityLevel.NORMAL:
            reds = [r for r in roles if r is SpecializationRole.RED]
            blues = [r for r in roles if r is SpecializationRole.BLUE]
            if len(reds) != 1 or len(blues) != 1:
                raise FissionError("Normal intensity requires one Red plus one matching Blue (SF2 §4)")
        elif proposal.intensity_level is IntensityLevel.DEEP:
            reds = [r for r in roles if r is SpecializationRole.RED]
            if len(reds) != 1:
                raise FissionError("Deep intensity requires exactly one Red child (SF2 §4)")
            if policy.deep_requires_approval and not proposal.approval_reference:
                raise FissionError("Deep intensity requires SOC/governance approval_reference (SF2 §4)")

    def _spawn_child(
        self,
        proposal: SpecialisationFissionProposal,
        specialist: ProposedSpecialist,
        kind: SubTypeKind,
        policy: SpecialisationFissionPolicy,
    ) -> SpecialisationFissionChild:
        index = len(self._children) + 1
        child_id = f"{proposal.parent_id}__{specialist.child_type}__spec_child_{index}"
        namespace = f"fission/{proposal.parent_id}/{child_id}/proposed_evidence"
        curriculum = CURRICULUM_BY_SPECIALIST.get(specialist.child_type)
        if curriculum:
            pair, role = curriculum
            schema_id = pair.red_schema_id if role is SpecializationRole.RED else pair.blue_schema_id
            curriculum_pair_id = pair.pair_id
            effective_tools = proposal.tool_scope & proposal.child_capabilities
        else:
            role = SpecializationRole.BLUE
            schema_id = proposal.schema_id
            curriculum_pair_id = ""
            # v1 legacy path: sub_space is the child's tool scope (SF-D4).
            effective_tools = frozenset({specialist.sub_space})

        registration = GatewayRegistration(
            token=f"token::{child_id}",
            tenant_id=proposal.tenant_id,
            tool_scope=frozenset(effective_tools),
            budget_tier=self._budget_tier_for_layer(proposal.layer),
            ring=Ring.RING_0_SYNTHETIC,
            breaker_key=BreakerKey(
                tenant_id=proposal.tenant_id,
                agent_id=child_id,
                tool="specialisation_fission_child",
                session_id=f"session::{child_id}",
            ),
        )
        expires_at = self._clock() + timedelta(seconds=policy.child_ttl_seconds)
        child = SpecialisationFissionChild(
            child_id=child_id,
            parent_id=proposal.parent_id,
            agent_type=specialist.child_type,
            schema_id=schema_id,
            namespace=namespace,
            registration=registration,
            parent_workflow_id=proposal.parent_workflow_id,
            policy_version=policy.version,
            child_capabilities=frozenset(proposal.child_capabilities),
            expires_at=expires_at,
            specialization_role=role,
            scenario_id=proposal.scenario_id,
            scenario_version=proposal.scenario_version,
            curriculum_pair_id=curriculum_pair_id,
            intensity_level=proposal.intensity_level or IntensityLevel.NORMAL,
            known_or_net_new=kind.value,
        )
        record = SpecialisationSpawnDecisionRecord(
            parent_workflow_id=proposal.parent_workflow_id,
            watcher_id=proposal.triggering_watcher,
            trigger_condition=f"divergence={proposal.divergence_signal}",
            policy_version=policy.version,
            child_agent_id=child_id,
            tools_assigned=frozenset(effective_tools),
            namespace_assigned=namespace,
            ttl=policy.child_ttl_seconds,
            intensity_level=(proposal.intensity_level or IntensityLevel.NORMAL).value,
            scenario_id=proposal.scenario_id,
            scenario_version=proposal.scenario_version,
            specialization_role=role.value,
            known_or_net_new=kind.value,
            subtype_registry_result=kind.value,
            ring_assignment=Ring.RING_0_SYNTHETIC.name,
            approval_reference=proposal.approval_reference,
        )
        self.spawn_records.append(record)
        self.lifecycle_log.record(
            parent_workflow_id=proposal.parent_workflow_id,
            child_agent_id=child_id,
            event=LifecycleEventKind.START,
            detail="specialisation child spawned",
        )
        self._children[child_id] = child
        return child

    @staticmethod
    def _budget_tier_for_layer(layer: str) -> RoleTier:
        return RoleTier.DETECTION if layer != "control_plane" else RoleTier.CONTROL_PLANE

    def _record_spawn(
        self,
        proposal: SpecialisationFissionProposal,
        children: list[SpecialisationFissionChild],
        *,
        detail: str,
    ) -> None:
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

    def _record_fallback_denial(self, proposal: SpecialisationFissionProposal) -> None:
        self.lifecycle_log.record(
            parent_workflow_id=proposal.parent_workflow_id,
            child_agent_id="",
            event=LifecycleEventKind.FALLBACK_DENIAL,
            detail="would-have-fissioned event denied by fallback mode",
        )

    def exhale(self, *, threat_level: ThreatLevel, triggering_watcher: str = "control_plane") -> tuple[str, ...]:
        if threat_level >= SPECIALISATION_THREAT_FLOOR:
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
                    detail="specialisation child retired after threat dropped below Level 2",
                )
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

    def children(self) -> tuple[SpecialisationFissionChild, ...]:
        return tuple(self._children.values())

    def held_net_new(self) -> tuple[HeldNetNewType, ...]:
        held: list[HeldNetNewType] = []
        for group in self._held_by_parent.values():
            held.extend(group)
        return tuple(held)


__all__ = [
    "SPECIALISATION_THREAT_FLOOR",
    "DEFAULT_MAX_SPECIALISATION_CHILDREN",
    "PROHIBITED_OUTPUT_FIELDS",
    "IntensityLevel",
    "SpecializationRole",
    "SubTypeKind",
    "CurriculumPair",
    "PURPLE_FISSION_CURRICULUM",
    "CURRICULUM_BY_SPECIALIST",
    "FIXED_SCHEMA_ALLOWED_FIELDS",
    "SpecialisationFissionPolicy",
    "DEFAULT_SPECIALISATION_FISSION_POLICY",
    "SpecialisationFissionPolicyStore",
    "SpecialisationSpawnDecisionRecord",
    "SpecialisationGovernedIngestionPipeline",
    "SpecialisationFissionChild",
    "SubTypeRegistry",
    "HeldNetNewType",
    "NetNewTypeSignOffGate",
    "ProposedSpecialist",
    "SpecialisationFissionProposal",
    "SpecialisationFissionController",
    "INCOMPLETE_BUDGET_EXHAUSTED",
    "ALLOWED_EVIDENCE_TYPES",
    "MAX_EVIDENCE_CONTENT_REF_LEN",
    "PROPOSED_EVIDENCE",
    "Q_CLASS_CHILD",
]
