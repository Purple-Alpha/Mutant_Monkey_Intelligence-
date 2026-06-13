"""Watcher Agents — Layer 6 Governance (scoreboard rows #85-87).

Three neutral observers governed by ``4. Product_Roadmap/Watcher_Agents_Contract.md``
(§11 SIGNED 2026-06-12, Matt Nichol):

  - W1 TimingWatcher (#85)    — completion windows + loop signatures
  - W2 DriftWatcher (#86)     — confidence-distribution drift
  - W3 IntegrityWatcher (#87) — ledger schema / circular reads / cross-tenant reads

Watchers watch the swarm, not the emails. They report facts only — no verdict
vote, no evidence-chain access, no blackboard writes, no recommendations beyond
threat-level classification. They are the only legitimate fission trigger source
(WA-D1): the ThreatLevelClassifier requires ≥2 independent watchers to escalate
above ROUTINE (WA-D2/D3), and the Fission Controllers act on that classification.
"""

from .observation import (
    ObservationError,
    ObservationLog,
    ObservationRecord,
    ObservationType,
    Severity,
    SWARM_SCOPE,
)
from .threat import (
    ESCALATION_QUORUM,
    WATCHER_IDS,
    ThreatLevel,
    ThreatLevelClassifier,
    ThreatLevelError,
)
from .isolation import ResourceIsolationError, WatcherResourceController
from .base import BaseWatcher, WatcherBoundaryError
from .timing_watcher import DEFAULT_LOOP_THRESHOLD, TimingWatcher
from .drift_watcher import DEFAULT_MIN_SAMPLES, DriftWatcher
from .integrity_watcher import IntegrityWatcher
from .escalation import (
    MATT_IDENTITY,
    EscalationDelivery,
    EscalationRouter,
    Recipient,
)

__all__ = [
    # observation log
    "SWARM_SCOPE",
    "ObservationError",
    "ObservationLog",
    "ObservationRecord",
    "ObservationType",
    "Severity",
    # threat classification
    "ESCALATION_QUORUM",
    "WATCHER_IDS",
    "ThreatLevel",
    "ThreatLevelClassifier",
    "ThreatLevelError",
    # infrastructure isolation
    "ResourceIsolationError",
    "WatcherResourceController",
    # watcher base + boundary
    "BaseWatcher",
    "WatcherBoundaryError",
    # the three watchers
    "DEFAULT_LOOP_THRESHOLD",
    "TimingWatcher",
    "DEFAULT_MIN_SAMPLES",
    "DriftWatcher",
    "IntegrityWatcher",
    # escalation routing
    "MATT_IDENTITY",
    "EscalationDelivery",
    "EscalationRouter",
    "Recipient",
]
