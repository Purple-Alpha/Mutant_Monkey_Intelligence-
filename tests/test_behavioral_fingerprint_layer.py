"""Spec T1-T3 for behavioral_fingerprint_layer.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from behavioral_fingerprint_layer import BehavioralFingerprintLayer


def _meta(byte_size: int, key_count: int, capability: str) -> dict:
    return {
        "volumetric": {
            "payload_byte_size": byte_size,
            "payload_key_count": key_count,
        },
        "lineage": {"target_capability": capability},
    }


@pytest.fixture
def layer(tmp_path: Path) -> BehavioralFingerprintLayer:
    return BehavioralFingerprintLayer(
        state_path=tmp_path / "fp.json",
        cold_start_n=5,
        k_stdev=4.0,
        min_capability_freq=0.02,
    )


def test_t1_cold_start_never_flags(layer: BehavioralFingerprintLayer):
    """T1 — N-1 wildly varying packets stay COLD_START, no mirror route."""
    sizes = [50, 9000, 120, 5000, 300]
    caps = ["READ_ONLY", "WRITE", "READ_ONLY", "WRITE", "READ_ONLY"]
    for idx, (size, cap) in enumerate(zip(sizes, caps, strict=True)):
        ok, result = layer.analyze_fingerprint(
            "agent_01", _meta(size, idx + 1, cap), {"x": 1}
        )
        assert ok is True
        assert result["verdict"] == "COLD_START"
        assert result.get("route") != "MIRROR_DIMENSION"


def test_t2_established_baseline_catches_byte_outlier(layer: BehavioralFingerprintLayer):
    """T2 — stable baseline then 50x byte-size outlier routes to mirror."""
    for _ in range(5):
        ok, result = layer.analyze_fingerprint(
            "agent_01", _meta(500, 2, "READ_ONLY"), {"a": 1, "b": 2}
        )
        assert ok and result["verdict"] == "COLD_START"

    ok, result = layer.analyze_fingerprint(
        "agent_01", _meta(25_000, 2, "READ_ONLY"), {"a": 1, "b": 2}
    )
    assert ok is True
    assert result["verdict"] == "ANOMALY"
    assert result["route"] == "MIRROR_DIMENSION"
    assert "payload_byte_size" in result["detail"]


def test_t3_capability_novelty_routes_not_hard_drop(layer: BehavioralFingerprintLayer):
    """T3 — READ_ONLY-trained sender flags novel WRITE capability."""
    for _ in range(5):
        ok, result = layer.analyze_fingerprint(
            "agent_01", _meta(500, 2, "READ_ONLY"), {"k": "v"}
        )
        assert ok and result["verdict"] == "COLD_START"

    ok, result = layer.analyze_fingerprint(
        "agent_01", _meta(500, 2, "WRITE"), {"k": "v"}
    )
    assert ok is True
    assert result["verdict"] == "ANOMALY"
    assert result["route"] == "MIRROR_DIMENSION"
    assert "target_capability" in result["detail"]
