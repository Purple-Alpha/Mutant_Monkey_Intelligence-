"""ObservationLog — Watcher Agents (Layer 6 Governance), append-only fact store.

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — WA-D4 + §3.4 / §3.5.

Every watcher observation is one append-only, immutable record. The log lives in
**separate infrastructure from ``core/blackboard/``** (WA-D4): it is its own
class with its own storage, never the core blackboard. There is no update or
delete API, so immutability holds structurally, not by convention — the same
discipline as the Phase 1 ``CanonicalEvidenceLedger`` and the Phase 5
``MutationAuditTrail``.

Watchers report **facts only** (WA-D7): a record carries what was observed, never
a recommendation or a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

# Swarm-wide sentinel for observations that are not about a single tenant
# (e.g. a threat_level_change spanning the whole swarm).
SWARM_SCOPE = "__swarm__"


class ObservationType(str, Enum):
    """Closed enum of observation types (WA-D4 / §3.5). No type outside this set."""

    TIMING_ANOMALY = "timing_anomaly"
    CONFIDENCE_DRIFT = "confidence_drift"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    LOOP_DETECTED = "loop_detected"
    SCHEMA_VIOLATION = "schema_violation"
    BASELINE_DEVIATION = "baseline_deviation"
    INACTIVITY_FLAG = "inactivity_flag"
    THREAT_LEVEL_CHANGE = "threat_level_change"


class Severity(str, Enum):
    """Observation severity → routing recipients (§6)."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ObservationError(Exception):
    """Raised on a malformed observation write (fail-safe)."""


@dataclass(frozen=True)
class ObservationRecord:
    """One append-only, immutable observation (§3.4). Facts only (WA-D7)."""

    watcher_id: str
    observation_type: ObservationType
    severity: Severity
    observed_agent: str
    details: str
    tenant_id: str = SWARM_SCOPE
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ObservationLog:
    """Append-only, immutable observation store — separate infra from the
    blackboard (WA-D4). No update/delete API. Optionally mirrors to a JSONL
    file for durability, but the in-process list is itself append-only.
    """

    jsonl_path: Path | None = None
    _records: list[ObservationRecord] = field(default_factory=list)

    def record(
        self,
        *,
        watcher_id: str,
        observation_type: ObservationType,
        severity: Severity,
        observed_agent: str,
        details: str,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord:
        """Append one observation. The ``observation_type`` and ``severity`` are
        closed enums, so a write outside the closed set fails at construction.
        """

        if not isinstance(observation_type, ObservationType):
            raise ObservationError("observation_type must be a closed-enum member")
        if not isinstance(severity, Severity):
            raise ObservationError("severity must be a closed-enum member")
        if not watcher_id or not observed_agent:
            raise ObservationError("watcher_id and observed_agent are required")

        entry = ObservationRecord(
            watcher_id=watcher_id,
            observation_type=observation_type,
            severity=severity,
            observed_agent=observed_agent,
            details=details,
            tenant_id=tenant_id or SWARM_SCOPE,
        )
        self._records.append(entry)
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        return entry

    def _append_jsonl(self, entry: ObservationRecord) -> None:
        import json

        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "watcher_id": entry.watcher_id,
                        "observation_type": entry.observation_type.value,
                        "severity": entry.severity.value,
                        "observed_agent": entry.observed_agent,
                        "details": entry.details,
                        "tenant_id": entry.tenant_id,
                        "timestamp": entry.timestamp.isoformat(),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[ObservationRecord, ...]:
        return tuple(self._records)

    def for_type(self, observation_type: ObservationType) -> tuple[ObservationRecord, ...]:
        return tuple(e for e in self._records if e.observation_type is observation_type)

    def for_watcher(self, watcher_id: str) -> tuple[ObservationRecord, ...]:
        return tuple(e for e in self._records if e.watcher_id == watcher_id)

    def for_severity(self, severity: Severity) -> tuple[ObservationRecord, ...]:
        return tuple(e for e in self._records if e.severity is severity)


__all__ = [
    "SWARM_SCOPE",
    "ObservationType",
    "Severity",
    "ObservationError",
    "ObservationRecord",
    "ObservationLog",
]
