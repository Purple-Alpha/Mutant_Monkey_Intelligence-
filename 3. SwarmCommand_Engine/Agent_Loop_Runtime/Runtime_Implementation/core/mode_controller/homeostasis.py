"""Global Homeostasis Index — organism-wide health score (§5, MC-D10).

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Contract.md`` — §14 SIGNED 2026-06-13
(Matt Nichol) — §5 + MC-D10 + §7 ("Homeostasis index manipulation").

The index is a continuous organism-wide health score derived from the eight
system health layers (§5). It is computed from **objective metrics only, not
agent-reported state** (§7): the only way to supply a layer score is through the
closed ``HomeostasisLayer`` set with a value the objective collectors produce.
There is deliberately no agent-reported input channel — an agent cannot raise or
lower the index, because there is no API surface through which it could.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.mode_controller.state import (
    HOMEOSTASIS_CRITICAL_THRESHOLD,
    HOMEOSTASIS_WARNING_THRESHOLD,
    HomeostasisLayer,
)


class HomeostasisError(Exception):
    """Raised on an invalid homeostasis computation (fail-safe)."""


class HomeostasisBand(str, Enum):
    """Banding of the index against the contract thresholds (§5)."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class HomeostasisReading:
    """One computed index value plus its band and the layers it was built from."""

    score: float
    band: HomeostasisBand
    layer_scores: tuple[tuple[HomeostasisLayer, float], ...]

    @property
    def warns(self) -> bool:
        return self.band in (HomeostasisBand.WARNING, HomeostasisBand.CRITICAL)

    @property
    def critical(self) -> bool:
        return self.band is HomeostasisBand.CRITICAL


def _band_for(score: float) -> HomeostasisBand:
    if score < HOMEOSTASIS_CRITICAL_THRESHOLD:
        return HomeostasisBand.CRITICAL
    if score < HOMEOSTASIS_WARNING_THRESHOLD:
        return HomeostasisBand.WARNING
    return HomeostasisBand.HEALTHY


def compute_homeostasis_index(
    layer_scores: dict[HomeostasisLayer, float],
) -> HomeostasisReading:
    """Compute the Global Homeostasis Index from the eight objective layers.

    All eight layers (§5) must be supplied, each in ``0..100`` from an objective
    collector. The index is the mean of the layer scores — equal-weight by
    design until real tenant data justifies a weighted model (Class-3 §8
    deferral: threshold/weight calibration is a signed-amendment item). Any
    missing layer, extra key, or out-of-range value is a fail-safe error, so the
    index cannot be computed from a partial or fabricated input set.
    """

    if not isinstance(layer_scores, dict):
        raise HomeostasisError("layer_scores must be a dict of HomeostasisLayer->float")

    expected = set(HomeostasisLayer)
    provided = set(layer_scores.keys())
    if not provided <= expected:
        extra = sorted(str(k) for k in provided - expected)
        raise HomeostasisError(f"unknown homeostasis layer(s): {extra}")
    missing = expected - provided
    if missing:
        names = sorted(layer.value for layer in missing)
        raise HomeostasisError(f"missing homeostasis layer(s): {names}")

    ordered: list[tuple[HomeostasisLayer, float]] = []
    for layer in HomeostasisLayer:
        value = float(layer_scores[layer])
        if not 0.0 <= value <= 100.0:
            raise HomeostasisError(
                f"layer {layer.value} score {value} out of range 0..100"
            )
        ordered.append((layer, value))

    score = sum(v for _, v in ordered) / len(ordered)
    return HomeostasisReading(
        score=score,
        band=_band_for(score),
        layer_scores=tuple(ordered),
    )


__all__ = [
    "HomeostasisError",
    "HomeostasisBand",
    "HomeostasisReading",
    "compute_homeostasis_index",
]
