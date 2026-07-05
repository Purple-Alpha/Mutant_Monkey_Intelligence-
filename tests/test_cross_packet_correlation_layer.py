"""Spec T1-T3 for cross_packet_correlation_layer.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from cross_packet_correlation_layer import CrossPacketCorrelationLayer


def _meta(nonce: int, lane: str) -> dict:
    return {
        "provenance": {"nonce": nonce},
        "lineage": {"origin_lane": lane},
    }


@pytest.fixture
def layer(tmp_path: Path) -> CrossPacketCorrelationLayer:
    return CrossPacketCorrelationLayer(
        state_path=tmp_path / "stream.json",
        warmup_threshold=10,
    )


def test_t1_cold_start_never_flags(layer: CrossPacketCorrelationLayer):
    """T1 — 9 packets across 4 lanes stay warm-up; no mirror route."""
    lanes = ["LANE_A", "LANE_B", "LANE_C", "LANE_D"]
    base = 1_000_000_000_000
    for idx in range(9):
        ok, result = layer.analyze_stream(
            "agent_01",
            _meta(idx + 1, lanes[idx % 4]),
            {"x": 1},
            base + idx * 500,
        )
        assert ok is True
        assert result["verdict"] == "STREAM_OK"
        assert result["detail"]["mode"] == "WARMUP_RECORD_ONLY"
        assert result.get("route") != "MIRROR_DIMENSION"


def test_t2_normal_stream_no_false_positives(layer: CrossPacketCorrelationLayer):
    """T2 — established sender, 100 packets / 2 lanes, zero mirror routes."""
    base = 2_000_000_000_000
    for idx in range(100):
        ok, result = layer.analyze_stream(
            "agent_01",
            _meta(idx + 1, "LANE_A" if idx % 2 == 0 else "LANE_B"),
            {"i": idx},
            base + idx * 600,
        )
        assert ok is True
        assert result["verdict"] == "STREAM_OK"
        assert result.get("route") != "MIRROR_DIMENSION"


def test_t3_burst_then_window_roll(layer: CrossPacketCorrelationLayer):
    """T3 — 121st packet breaches velocity; 61s gap clears window."""
    base = 3_000_000_000_000
    for idx in range(10):
        layer.analyze_stream(
            "agent_01", _meta(idx + 1, "LANE_A"), {"w": idx}, base + idx * 10
        )

    breach_at = None
    for idx in range(10, 131):
        ok, result = layer.analyze_stream(
            "agent_01",
            _meta(idx + 1, "LANE_A"),
            {"b": idx},
            base + (idx - 10) * 10,
        )
        assert ok is True
        if result.get("route") == "MIRROR_DIMENSION":
            breach_at = idx
            assert "VELOCITY_CEILING_EXCEEDED" in result["detail"]["reason"]
            break
    assert breach_at == 120

    ok, result = layer.analyze_stream(
        "agent_01",
        _meta(200, "LANE_A"),
        {"after_gap": 1},
        base + 61_000,
    )
    assert ok is True
    assert result["verdict"] == "STREAM_OK"
    assert result.get("route") != "MIRROR_DIMENSION"


def test_lane_diversity_breach(layer: CrossPacketCorrelationLayer):
    """4th lane in window routes to mirror after warm-up."""
    base = 4_000_000_000_000
    lanes = ["LANE_A", "LANE_B", "LANE_C", "LANE_D"]
    for idx in range(13):
        ok, result = layer.analyze_stream(
            "agent_01",
            _meta(idx + 1, lanes[min(idx, 3)]),
            {"x": idx},
            base + idx * 1000,
        )
        if idx < 9:
            assert result["detail"]["mode"] == "WARMUP_RECORD_ONLY"
        elif idx == 12:
            assert ok is True
            assert result["route"] == "MIRROR_DIMENSION"
            assert "LANE_DIVERSITY_EXCEEDED" in result["detail"]["reason"]
