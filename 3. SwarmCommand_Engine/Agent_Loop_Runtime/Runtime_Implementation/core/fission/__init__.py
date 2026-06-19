"""Agent Fission — controlled specialist release (Layer 6 Control Plane).

Load Fission is governed by ``4. Product_Roadmap/Load_Fission_Contract_v2.md``
(§13 SIGNED 2026-06-13, Matt Nichol) and lands first per the Specialisation
Fission advisory ordering note: shared event log and child lifecycle wiring are
built under the lower-risk load contract before the net-new-type machinery.

Specialisation Fission is governed by
``4. Product_Roadmap/Specialisation_Fission_Contract_v2.md`` (§18 SIGNED
2026-06-13, Matt Nichol).
"""

from .event_log import (
    FissionEvent,
    FissionEventLog,
    FissionEventType,
    FissionTrigger,
)
from .load import (
    ALLOWED_EVIDENCE_TYPES,
    DEFAULT_MAX_LOAD_CHILDREN,
    LOAD_FISSION_MAX_DEPTH,
    LOAD_FISSION_THREAT_FLOOR,
    MAX_EVIDENCE_CONTENT_REF_LEN,
    PROPOSED_EVIDENCE,
    Q_CLASS_CHILD,
    GovernedIngestionPipeline,
    IngestedEvidence,
    IngestionStatus,
    LoadTriggerKind,
    FissionChild,
    FissionError,
    GatewayRegistration,
    LoadFissionController,
    LoadFissionProposal,
    ProposedEvidence,
)
from .load_governance import (
    LifecycleEventKind,
    LifecycleLog,
    QuotaExceededError,
    SpawnDecisionRecord,
    SpawnQuotaTracker,
)
from .load_policy import (
    DEFAULT_LOAD_FISSION_POLICY,
    LoadFissionPolicy,
    LoadFissionPolicyStore,
)
from .specialisation import (
    CURRICULUM_BY_SPECIALIST,
    DEFAULT_MAX_SPECIALISATION_CHILDREN,
    DEFAULT_SPECIALISATION_FISSION_POLICY,
    FIXED_SCHEMA_ALLOWED_FIELDS,
    INCOMPLETE_BUDGET_EXHAUSTED,
    PROHIBITED_OUTPUT_FIELDS,
    PURPLE_FISSION_CURRICULUM,
    SPECIALISATION_THREAT_FLOOR,
    CurriculumPair,
    HeldNetNewType,
    IntensityLevel,
    NetNewTypeSignOffGate,
    ProposedSpecialist,
    SpecialisationFissionChild,
    SpecialisationFissionController,
    SpecialisationFissionPolicy,
    SpecialisationFissionPolicyStore,
    SpecialisationFissionProposal,
    SpecialisationGovernedIngestionPipeline,
    SpecialisationSpawnDecisionRecord,
    SpecializationRole,
    SubTypeKind,
    SubTypeRegistry,
)

__all__ = [
    "FissionEvent",
    "FissionEventLog",
    "FissionEventType",
    "FissionTrigger",
    "ALLOWED_EVIDENCE_TYPES",
    "DEFAULT_MAX_LOAD_CHILDREN",
    "LOAD_FISSION_MAX_DEPTH",
    "LOAD_FISSION_THREAT_FLOOR",
    "MAX_EVIDENCE_CONTENT_REF_LEN",
    "PROPOSED_EVIDENCE",
    "Q_CLASS_CHILD",
    "GovernedIngestionPipeline",
    "IngestedEvidence",
    "IngestionStatus",
    "LoadTriggerKind",
    "FissionChild",
    "FissionError",
    "GatewayRegistration",
    "LoadFissionController",
    "LoadFissionProposal",
    "ProposedEvidence",
    "LifecycleEventKind",
    "LifecycleLog",
    "QuotaExceededError",
    "SpawnDecisionRecord",
    "SpawnQuotaTracker",
    "DEFAULT_LOAD_FISSION_POLICY",
    "LoadFissionPolicy",
    "LoadFissionPolicyStore",
    "CURRICULUM_BY_SPECIALIST",
    "DEFAULT_MAX_SPECIALISATION_CHILDREN",
    "DEFAULT_SPECIALISATION_FISSION_POLICY",
    "FIXED_SCHEMA_ALLOWED_FIELDS",
    "INCOMPLETE_BUDGET_EXHAUSTED",
    "PROHIBITED_OUTPUT_FIELDS",
    "PURPLE_FISSION_CURRICULUM",
    "SPECIALISATION_THREAT_FLOOR",
    "CurriculumPair",
    "HeldNetNewType",
    "IntensityLevel",
    "NetNewTypeSignOffGate",
    "ProposedSpecialist",
    "SpecialisationFissionChild",
    "SpecialisationFissionController",
    "SpecialisationFissionPolicy",
    "SpecialisationFissionPolicyStore",
    "SpecialisationFissionProposal",
    "SpecialisationGovernedIngestionPipeline",
    "SpecialisationSpawnDecisionRecord",
    "SpecializationRole",
    "SubTypeKind",
    "SubTypeRegistry",
]
