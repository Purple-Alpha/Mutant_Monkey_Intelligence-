"""ValidationGate — Phase 5 (Layer 5), benign-stream false-positive guard.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D3 + P5-D10 + §3.3 (stage 4 + the conservative-threshold
stage 6 of the Anomaly Detection Pipeline).

A candidate mutation is run against a benign stream across a **defined cycle
count** (``VALIDATION_CYCLES``). The gate computes the false-positive delta vs
the current signed baseline on each cycle and **rejects** any candidate whose
regression exceeds the launch-conservative threshold on **any** cycle. The
threshold and cycle count launch conservative and are tunable only by signed
amendment (P5-D10) — never autonomously.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# Launch-conservative defaults (P5-D10). Not locked permanently; tuned by signed
# amendment once real-tenant data exists. Conservative = small tolerance, many
# cycles, so a candidate must be clean and stable to pass.
DEFAULT_FP_REGRESSION_THRESHOLD = 0.01  # max allowed FP-rate increase vs baseline
DEFAULT_VALIDATION_CYCLES = 5

# A benign stream is any callable that, given a candidate id and a cycle index,
# returns the measured false-positive rate (0.0-1.0) for that cycle.
BenignStream = Callable[[str, int], float]


class ValidationError(Exception):
    """Raised on malformed validation input (fails safe)."""


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a benign-stream validation run."""

    candidate_id: str
    passed: bool
    baseline_fp_rate: float
    per_cycle_fp_rates: tuple[float, ...]
    per_cycle_deltas: tuple[float, ...]
    max_delta: float
    threshold: float
    cycles: int
    reason: str


@dataclass(frozen=True)
class ValidationGate:
    """Benign-stream FP regression gate across a defined, conservative cycle count."""

    fp_regression_threshold: float = DEFAULT_FP_REGRESSION_THRESHOLD
    cycles: int = DEFAULT_VALIDATION_CYCLES

    def __post_init__(self) -> None:
        if self.cycles < 1:
            raise ValidationError("ValidationGate requires at least one cycle")
        if not (0.0 <= self.fp_regression_threshold <= 1.0):
            raise ValidationError("fp_regression_threshold must be in 0.0-1.0")

    def validate(
        self,
        candidate_id: str,
        *,
        baseline_fp_rate: float,
        benign_stream: BenignStream,
    ) -> ValidationResult:
        """Run the candidate against the benign stream for every cycle.

        Rejects if the FP-rate increase over baseline exceeds the conservative
        threshold on ANY cycle (P5-D3). A candidate that improves or holds the
        FP rate passes.
        """

        if not candidate_id:
            raise ValidationError("candidate_id is required")
        if not (0.0 <= baseline_fp_rate <= 1.0):
            raise ValidationError("baseline_fp_rate must be in 0.0-1.0")

        rates: list[float] = []
        deltas: list[float] = []
        for cycle in range(self.cycles):
            rate = benign_stream(candidate_id, cycle)
            if not isinstance(rate, (int, float)) or isinstance(rate, bool):
                raise ValidationError(
                    f"benign_stream must return a numeric FP rate (cycle {cycle})"
                )
            rate = float(rate)
            if not (0.0 <= rate <= 1.0):
                raise ValidationError(
                    f"benign_stream FP rate must be in 0.0-1.0 (cycle {cycle})"
                )
            rates.append(rate)
            deltas.append(rate - baseline_fp_rate)

        max_delta = max(deltas) if deltas else 0.0
        passed = max_delta <= self.fp_regression_threshold
        if passed:
            reason = (
                f"benign-stream FP regression {max_delta:+.4f} within conservative "
                f"threshold {self.fp_regression_threshold:.4f} across {self.cycles} cycles"
            )
        else:
            reason = (
                f"REJECTED: benign-stream FP regression {max_delta:+.4f} exceeds "
                f"conservative threshold {self.fp_regression_threshold:.4f} on at "
                f"least one of {self.cycles} cycles"
            )

        return ValidationResult(
            candidate_id=candidate_id,
            passed=passed,
            baseline_fp_rate=baseline_fp_rate,
            per_cycle_fp_rates=tuple(rates),
            per_cycle_deltas=tuple(deltas),
            max_delta=max_delta,
            threshold=self.fp_regression_threshold,
            cycles=self.cycles,
            reason=reason,
        )
