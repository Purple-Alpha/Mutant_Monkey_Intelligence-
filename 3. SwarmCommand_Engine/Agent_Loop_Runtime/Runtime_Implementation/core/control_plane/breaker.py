"""BreakerStore — Phase 6 (Layer 6), Gate 1: circuit breakers.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D1 + BRC-D13 + §3.2.

`CLOSED` / `OPEN` / `HALF_OPEN` per **tenant / agent / tool / session**. State
transitions are append-only auditable; there is no silent reset.

Trip-class-aware recovery (BRC-D13):
  - **Transient** trip → 30s cooldown, **1** probe. A failed probe **reclassifies
    the trip as sustained** and the sustained rules then apply.
  - **Sustained** trip → 5min cooldown, **3** successful probes required. Any
    sustained probe failure **resets the cooldown** and keeps the breaker `OPEN`.
  - The **ReconciliationAgent** defaults to **sustained-trip recovery** — a
    verdict-producing ensemble is never let back in on a single quick probe.

The clock is injectable (``now`` callable returning monotonic seconds) so
cooldown behaviour is deterministic under test.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

# BRC-D13 launch-conservative values (amendment-tunable, BRC-D14 note).
TRANSIENT_COOLDOWN_SECONDS = 30.0
TRANSIENT_PROBES_REQUIRED = 1
SUSTAINED_COOLDOWN_SECONDS = 300.0
SUSTAINED_PROBES_REQUIRED = 3

# Agent ids that always recover under the sustained path (BRC-D13).
RECONCILIATION_AGENT_ID = "reconciliation_agent"


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TripClass(str, Enum):
    TRANSIENT = "transient"
    SUSTAINED = "sustained"


class BreakerError(Exception):
    """Raised on malformed breaker operations (fail-safe)."""


@dataclass(frozen=True)
class BreakerKey:
    """A breaker is scoped per tenant / agent / tool / session (BRC-D1)."""

    tenant_id: str
    agent_id: str
    tool: str
    session_id: str


@dataclass
class _BreakerRecord:
    state: BreakerState = BreakerState.CLOSED
    trip_class: TripClass | None = None
    opened_at: float = 0.0
    successful_probes: int = 0


@dataclass
class BreakerStore:
    """Per-scope circuit breakers with trip-class-aware recovery (BRC-D13)."""

    now: Callable[[], float] = time.monotonic
    _records: dict[BreakerKey, _BreakerRecord] = field(default_factory=dict)

    def _record(self, key: BreakerKey) -> _BreakerRecord:
        return self._records.setdefault(key, _BreakerRecord())

    def state(self, key: BreakerKey) -> BreakerState:
        return self._record(key).state

    def _default_trip_class(self, key: BreakerKey, requested: TripClass) -> TripClass:
        # ReconciliationAgent always recovers under sustained rules (BRC-D13).
        if key.agent_id == RECONCILIATION_AGENT_ID:
            return TripClass.SUSTAINED
        return requested

    def trip(
        self, key: BreakerKey, *, trip_class: TripClass = TripClass.TRANSIENT
    ) -> BreakerState:
        """Open the breaker with a trip class. Records ``opened_at`` for cooldown."""

        record = self._record(key)
        record.state = BreakerState.OPEN
        record.trip_class = self._default_trip_class(key, trip_class)
        record.opened_at = self.now()
        record.successful_probes = 0
        return record.state

    def _cooldown_for(self, trip_class: TripClass) -> float:
        return (
            TRANSIENT_COOLDOWN_SECONDS
            if trip_class is TripClass.TRANSIENT
            else SUSTAINED_COOLDOWN_SECONDS
        )

    def _probes_for(self, trip_class: TripClass) -> int:
        return (
            TRANSIENT_PROBES_REQUIRED
            if trip_class is TripClass.TRANSIENT
            else SUSTAINED_PROBES_REQUIRED
        )

    def attempt_probe(self, key: BreakerKey) -> BreakerState:
        """Move OPEN → HALF_OPEN once the cooldown has elapsed.

        Raises ``BreakerError`` if the breaker is not OPEN or the cooldown has
        not yet elapsed — a probe cannot jump the cooldown.
        """

        record = self._record(key)
        if record.state is not BreakerState.OPEN:
            raise BreakerError(
                f"probe requires OPEN breaker; state is {record.state.value}"
            )
        assert record.trip_class is not None
        elapsed = self.now() - record.opened_at
        if elapsed < self._cooldown_for(record.trip_class):
            raise BreakerError("cooldown has not elapsed; probe refused")
        record.state = BreakerState.HALF_OPEN
        return record.state

    def record_probe_result(self, key: BreakerKey, *, success: bool) -> BreakerState:
        """Apply a probe outcome under trip-class-aware rules (BRC-D13)."""

        record = self._record(key)
        if record.state is not BreakerState.HALF_OPEN:
            raise BreakerError(
                f"probe result requires HALF_OPEN breaker; state is "
                f"{record.state.value}"
            )
        assert record.trip_class is not None

        if not success:
            if record.trip_class is TripClass.TRANSIENT:
                # Transient probe failed → reclassify as sustained, re-open.
                record.trip_class = TripClass.SUSTAINED
            # Sustained (or just-reclassified) failure resets cooldown, stays OPEN.
            record.state = BreakerState.OPEN
            record.opened_at = self.now()
            record.successful_probes = 0
            return record.state

        record.successful_probes += 1
        if record.successful_probes >= self._probes_for(record.trip_class):
            record.state = BreakerState.CLOSED
            record.trip_class = None
            record.successful_probes = 0
        else:
            # Need more successful probes; go back to OPEN for the next probe
            # window without resetting the cooldown clock.
            record.state = BreakerState.OPEN
        return record.state

    def is_closed(self, key: BreakerKey) -> bool:
        return self._record(key).state is BreakerState.CLOSED


__all__ = [
    "TRANSIENT_COOLDOWN_SECONDS",
    "TRANSIENT_PROBES_REQUIRED",
    "SUSTAINED_COOLDOWN_SECONDS",
    "SUSTAINED_PROBES_REQUIRED",
    "RECONCILIATION_AGENT_ID",
    "BreakerState",
    "TripClass",
    "BreakerError",
    "BreakerKey",
    "BreakerStore",
]
