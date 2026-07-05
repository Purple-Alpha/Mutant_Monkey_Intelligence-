"""Spec T1-T3 for temporal_rhythm_layer.py (REV A)."""

from __future__ import annotations

from pathlib import Path

import pytest

from temporal_rhythm_layer import (
    EPOCH_LENGTH,
    SESSION_GAP_MS,
    TemporalRhythmLayer,
    WARMUP_INTERVALS,
)


@pytest.fixture
def layer(tmp_path: Path) -> TemporalRhythmLayer:
    return TemporalRhythmLayer(state_path=tmp_path / "rhythm.json")


def test_t1_cold_start_metronomic_never_flags(layer: TemporalRhythmLayer):
    """T1 — 21 packets at 1000 ms spacing: FIRST_CONTACT then warm-up only."""
    base = 1_000_000_000_000
    for idx in range(21):
        ok, result = layer.analyze_rhythm("agent_01", {}, {"x": idx}, base + idx * 1000)
        assert ok is True
        assert result["verdict"] == "RHYTHM_OK"
        assert result.get("route") != "MIRROR_DIMENSION"
        if idx == 0:
            assert result["detail"]["mode"] == "FIRST_CONTACT"
        else:
            assert result["detail"]["mode"] == "WARMUP_RECORD_ONLY"


def test_t2_normal_cadence_and_session_gap_hygiene(layer: TemporalRhythmLayer):
    """T2 — jittered cadence + 20 min gap does not contaminate baseline."""
    base = 2_000_000_000_000
    ts = base
    # Warm-up + establish: 25 packets ~2000 ms apart with jitter.
    for idx in range(25):
        jitter = (idx % 5) * 200 - 400
        ts += 2000 + jitter
        ok, result = layer.analyze_rhythm("agent_01", {}, {"w": idx}, ts)
        assert ok and result["verdict"] == "RHYTHM_OK"

    # 20-minute session gap.
    ts += 20 * 60 * 1000
    ok, result = layer.analyze_rhythm("agent_01", {}, {"gap": 1}, ts)
    assert ok and result["detail"]["mode"] == "SESSION_RESET"

    mean_before_gap = layer._row("agent_01")["mean_ms"]

    # Continue jittered traffic — 175 more packets (total 200 after gap packet).
    for idx in range(175):
        jitter = (idx % 7) * 150 - 450
        ts += 2000 + jitter
        ok, result = layer.analyze_rhythm("agent_01", {}, {"n": idx}, ts)
        assert ok is True
        assert result.get("route") != "MIRROR_DIMENSION"

    row = layer._row("agent_01")
    assert 1200 <= row["mean_ms"] <= 2800
    assert mean_before_gap > 0


def test_t3_machine_cadence_and_deviation(layer: TemporalRhythmLayer):
    """T3 — machine cadence flags; burst deviation flags."""
    base = 3_000_000_000_000
    ts = base
    # Warm-up with exact 2000 ms spacing (21 packets -> 20 intervals, still warm-up).
    for idx in range(21):
        if idx > 0:
            ts += 2000
        ok, result = layer.analyze_rhythm("agent_01", {}, {"w": idx}, ts)
        assert ok is True
        assert result.get("route") != "MIRROR_DIMENSION"

    # Packet 22 / interval 21: count becomes 21, CV triggers machine cadence.
    ts += 2000
    ok, result = layer.analyze_rhythm("agent_01", {}, {"m": 0}, ts)
    assert ok is True
    assert result["route"] == "MIRROR_DIMENSION"
    assert result["detail"]["reason"] == "MACHINE_CADENCE"

    # Re-establish jittered baseline for deviation test.
    layer2 = TemporalRhythmLayer()
    ts2 = 5_000_000_000_000
    for idx in range(WARMUP_INTERVALS + 5):
        jitter = (idx % 5) * 200 - 400
        ts2 += 2000 + jitter
        layer2.analyze_rhythm("agent_02", {}, {"e": idx}, ts2)

    ok, result = layer2.analyze_rhythm("agent_02", {}, {"burst": 1}, ts2 + 5)
    assert ok is True
    assert result["route"] == "MIRROR_DIMENSION"
    assert result["detail"]["reason"] == "RHYTHM_DEVIATION"


def test_epoch_roll_resets_warmup(layer: TemporalRhythmLayer):
    """Anti-latch: epoch roll after 512 intervals resets interval_count."""
    base = 4_000_000_000_000
    ts = base
    for idx in range(EPOCH_LENGTH + 1):
        ts += 2000 + (idx % 9) * 50
        layer.analyze_rhythm("agent_01", {}, {"i": idx}, ts)
    row = layer._row("agent_01")
    assert row["epoch"] >= 1
    assert row["interval_count"] <= WARMUP_INTERVALS
