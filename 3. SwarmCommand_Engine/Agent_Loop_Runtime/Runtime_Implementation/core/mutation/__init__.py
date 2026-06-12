"""Sandbox-only mutation engine.

Month 0 / Phase 1.4: sandbox synthetic-case promotion (``engine`` legacy logic).
Phase 5 (Layer 5): the swarm-level Anomaly Detection Pipeline ensemble — six
components governed by ``4. Product_Roadmap/Phase5_MutationEngine_Contract.md``
(§11 SIGNED 2026-06-12, Matt Nichol). Scoreboard row #88.
"""

from .engine import (
    MAX_EVIDENCE_IDS_PER_PROMOTION,
    MutationCandidate,
    MutationEngineConfig,
    MutationEngineItemResult,
    MutationEngineResult,
    run_mutation_cycle,
    select_mutation_kind,
)

# -- Phase 5 (Layer 5) components ----------------------------------------------
from .audit_trail import (
    MUTATION_AUDIT_SCHEMA_VERSION,
    MutationAuditEntry,
    MutationAuditError,
    MutationAuditSchemaError,
    MutationAuditTrail,
    MutationStage,
)
from .confirmation_tracker import (
    THREE_SHOT_THRESHOLD,
    Confirmation,
    ConfirmationError,
    ThreeShotConfirmationTracker,
)
from .validation_gate import (
    DEFAULT_FP_REGRESSION_THRESHOLD,
    DEFAULT_VALIDATION_CYCLES,
    BenignStream,
    ValidationError,
    ValidationGate,
    ValidationResult,
)
from .sign_off_gate import (
    DEPLOY_SURFACE,
    HumanSignOffGate,
    MutationProposal,
    SignOffError,
    SignOffRecord,
)
from .rollback import (
    DEFAULT_AUTO_ROLLBACK_FP_DELTA,
    DeploymentState,
    RollbackError,
    RollbackMechanism,
    RollbackOutcome,
)
from .zero_day_capture import (
    ZERO_DAY_ROUTING_TARGET,
    ZeroDayCapture,
    ZeroDayCaptureError,
    ZeroDayProposal,
    ZeroDayReferral,
)
from .mutation_ensemble import (
    DEFAULT_OUTLIER_SIGMA,
    AnomalyCandidate,
    MutationEngineEnsemble,
    MutationEnsembleError,
    PipelineResult,
)

__all__ = [
    # Legacy / Phase 1.4
    "MAX_EVIDENCE_IDS_PER_PROMOTION",
    "MutationCandidate",
    "MutationEngineConfig",
    "MutationEngineItemResult",
    "MutationEngineResult",
    "run_mutation_cycle",
    "select_mutation_kind",
    # Phase 5 — audit trail
    "MUTATION_AUDIT_SCHEMA_VERSION",
    "MutationAuditEntry",
    "MutationAuditError",
    "MutationAuditSchemaError",
    "MutationAuditTrail",
    "MutationStage",
    # Phase 5 — 3-shot confirmation
    "THREE_SHOT_THRESHOLD",
    "Confirmation",
    "ConfirmationError",
    "ThreeShotConfirmationTracker",
    # Phase 5 — validation gate
    "DEFAULT_FP_REGRESSION_THRESHOLD",
    "DEFAULT_VALIDATION_CYCLES",
    "BenignStream",
    "ValidationError",
    "ValidationGate",
    "ValidationResult",
    # Phase 5 — human sign-off gate
    "DEPLOY_SURFACE",
    "HumanSignOffGate",
    "MutationProposal",
    "SignOffError",
    "SignOffRecord",
    # Phase 5 — rollback
    "DEFAULT_AUTO_ROLLBACK_FP_DELTA",
    "DeploymentState",
    "RollbackError",
    "RollbackMechanism",
    "RollbackOutcome",
    # Phase 5 — zero-day capture
    "ZERO_DAY_ROUTING_TARGET",
    "ZeroDayCapture",
    "ZeroDayCaptureError",
    "ZeroDayProposal",
    "ZeroDayReferral",
    # Phase 5 — ensemble (row #88)
    "DEFAULT_OUTLIER_SIGMA",
    "AnomalyCandidate",
    "MutationEngineEnsemble",
    "MutationEnsembleError",
    "PipelineResult",
]
