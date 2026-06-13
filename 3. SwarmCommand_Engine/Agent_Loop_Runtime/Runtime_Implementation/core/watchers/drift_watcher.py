"""W2 DriftWatcher (#86) — Watcher Agents (Layer 6 Governance).

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — §3.2.

Monitors each agent's **confidence distribution over time** against its
established baseline. If an agent's scoring pattern shifts **outside its baseline
range** — too high or too low — it flags it, catching gradual drift that
individual test runs miss. Emits ``confidence_drift`` and ``baseline_deviation``
only.

Facts only (WA-D7): confidence values are reported to the watcher; the watcher
holds a running mean per observed agent and compares it to the signed baseline.
It never reaches into the scoring agents themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.watchers.base import BaseWatcher
from core.watchers.observation import ObservationRecord, ObservationType, Severity, SWARM_SCOPE

# Launch-conservative default sample floor before drift is assessed (WA-D11).
DEFAULT_MIN_SAMPLES = 5


@dataclass
class _RunningStats:
    count: int = 0
    total: float = 0.0

    def add(self, value: float) -> None:
        self.count += 1
        self.total += value

    @property
    def mean(self) -> float:
        return self.total / self.count if self.count else 0.0


@dataclass
class _Baseline:
    low: float
    high: float


class DriftWatcher(BaseWatcher):
    """#86 — confidence-distribution drift observer."""

    ALLOWED_TYPES = frozenset(
        {
            ObservationType.CONFIDENCE_DRIFT,
            ObservationType.BASELINE_DEVIATION,
        }
    )

    def __init__(self, *args, min_samples: int = DEFAULT_MIN_SAMPLES, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_samples = min_samples
        self._baselines: dict[str, _Baseline] = {}
        self._stats: dict[str, _RunningStats] = {}

    def set_baseline(self, observed_agent: str, *, low: float, high: float) -> None:
        """Register an agent's signed baseline confidence range."""

        if low > high:
            raise ValueError("baseline low must be <= high")
        self._baselines[observed_agent] = _Baseline(low=low, high=high)
        self._stats.setdefault(observed_agent, _RunningStats())

    def observe_confidence(
        self, *, observed_agent: str, confidence: float, tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord | None:
        """Add a confidence sample; flag drift once enough samples accumulate and
        the running mean leaves the agent's baseline range (too high or too low)."""

        baseline = self._baselines.get(observed_agent)
        if baseline is None:
            raise ValueError(f"no baseline set for {observed_agent!r}")
        stats = self._stats.setdefault(observed_agent, _RunningStats())
        stats.add(confidence)

        # A single out-of-range reading is a point deviation; a sustained shift of
        # the running mean is drift. We need enough samples to call drift.
        if stats.count < self.min_samples:
            if not (baseline.low <= confidence <= baseline.high):
                return self._observe(
                    observation_type=ObservationType.BASELINE_DEVIATION,
                    severity=Severity.INFO,
                    observed_agent=observed_agent,
                    details=(
                        f"confidence {confidence:.3f} outside baseline "
                        f"[{baseline.low:.3f}, {baseline.high:.3f}] "
                        f"(sample {stats.count}/{self.min_samples})"
                    ),
                    tenant_id=tenant_id,
                )
            return None

        mean = stats.mean
        if baseline.low <= mean <= baseline.high:
            return None
        direction = "above" if mean > baseline.high else "below"
        return self._observe(
            observation_type=ObservationType.CONFIDENCE_DRIFT,
            severity=Severity.WARNING,
            observed_agent=observed_agent,
            details=(
                f"running-mean confidence {mean:.3f} drifted {direction} baseline "
                f"[{baseline.low:.3f}, {baseline.high:.3f}] over {stats.count} samples"
            ),
            tenant_id=tenant_id,
        )


__all__ = ["DEFAULT_MIN_SAMPLES", "DriftWatcher"]
