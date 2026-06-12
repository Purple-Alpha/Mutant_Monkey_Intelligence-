"""Blast Radius Controller — control plane (Phase 6, Layer 6).

Eight components governed by ``4. Product_Roadmap/Blast_Radius_Controller_Contract.md``
(§11 SIGNED 2026-06-12, Matt Nichol). Scoreboard row #89. Vendor-neutral: defines
control and security properties, not infrastructure choices. The Mode Controller
(BRC-D10) and Privacy Filter service are separate contracts — this package builds
the gateway-side interfaces only.
"""

from .audit import (
    ControlPlaneAuditEntry,
    ControlPlaneAuditTrail,
    ControlPlaneEvent,
)
from .identity import (
    AgentIdentity,
    AgentIdentityGateway,
    IdentityError,
    ResolvedIdentity,
)
from .breaker import (
    RECONCILIATION_AGENT_ID,
    SUSTAINED_COOLDOWN_SECONDS,
    SUSTAINED_PROBES_REQUIRED,
    TRANSIENT_COOLDOWN_SECONDS,
    TRANSIENT_PROBES_REQUIRED,
    BreakerError,
    BreakerKey,
    BreakerState,
    BreakerStore,
    TripClass,
)
from .budget import (
    INCOMPLETE_BUDGET_EXHAUSTED,
    RECONCILIATION_VOTER_TOKEN_SUBBUDGET,
    RECONCILIATION_VOTERS,
    TIER_BUDGETS,
    Budget,
    BudgetError,
    RoleTier,
    SessionBudgetStore,
)
from .loop_detector import (
    FREQUENCY_THRESHOLD,
    FREQUENCY_WINDOW_SECONDS,
    IDENTICAL_RUN_THRESHOLD,
    LoopDetector,
)
from .segmentation import SegmentationError, TenantSegmentationController
from .privacy_filter import (
    PRIVACY_FILTER_AGENT_ID,
    PrivacyFilterError,
    PrivacyFilterInterface,
    privacy_filter_breaker_key,
)
from .rings import (
    MAX_ANOMALIES_FOR_PROMOTION,
    MAX_REGRESSIONS_FOR_PROMOTION,
    MAX_TOKEN_COST_DELTA_FOR_PROMOTION,
    PromotionTelemetry,
    Ring,
    RingController,
    RingError,
)
from .gateway import (
    AllowAllModeCheck,
    GatewayController,
    GatewayDecision,
    GatewayRejected,
    GatewayRequest,
    ModeCheck,
)

__all__ = [
    # audit
    "ControlPlaneAuditEntry",
    "ControlPlaneAuditTrail",
    "ControlPlaneEvent",
    # identity (Gate 5)
    "AgentIdentity",
    "AgentIdentityGateway",
    "IdentityError",
    "ResolvedIdentity",
    # breaker (Gate 1)
    "RECONCILIATION_AGENT_ID",
    "SUSTAINED_COOLDOWN_SECONDS",
    "SUSTAINED_PROBES_REQUIRED",
    "TRANSIENT_COOLDOWN_SECONDS",
    "TRANSIENT_PROBES_REQUIRED",
    "BreakerError",
    "BreakerKey",
    "BreakerState",
    "BreakerStore",
    "TripClass",
    # budget (Gate 1)
    "INCOMPLETE_BUDGET_EXHAUSTED",
    "RECONCILIATION_VOTER_TOKEN_SUBBUDGET",
    "RECONCILIATION_VOTERS",
    "TIER_BUDGETS",
    "Budget",
    "BudgetError",
    "RoleTier",
    "SessionBudgetStore",
    # loop detector (Gate 1)
    "FREQUENCY_THRESHOLD",
    "FREQUENCY_WINDOW_SECONDS",
    "IDENTICAL_RUN_THRESHOLD",
    "LoopDetector",
    # segmentation (Gate 2)
    "SegmentationError",
    "TenantSegmentationController",
    # privacy filter (Gate 2)
    "PRIVACY_FILTER_AGENT_ID",
    "PrivacyFilterError",
    "PrivacyFilterInterface",
    "privacy_filter_breaker_key",
    # rings (Gate 3)
    "MAX_ANOMALIES_FOR_PROMOTION",
    "MAX_REGRESSIONS_FOR_PROMOTION",
    "MAX_TOKEN_COST_DELTA_FOR_PROMOTION",
    "PromotionTelemetry",
    "Ring",
    "RingController",
    "RingError",
    # gateway (spine, row #89)
    "AllowAllModeCheck",
    "GatewayController",
    "GatewayDecision",
    "GatewayRejected",
    "GatewayRequest",
    "ModeCheck",
]
