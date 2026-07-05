"""Cryptolalia lab bridge + iceberg gate mirror wire tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cryptolalia_lab_bridge import mirror_router_for_lab, route_gate_divert_to_mirror
from metadata_ingress_gate import (
    AgentKeyring,
    AgentSigner,
    MetadataIngressGate,
    TimeWindow,
    generate_agent_keypair,
)
from mirror_dimension_router import MirrorDimensionRouter
from provenance_chain_depth_layer import ProvenanceChainDepthLayer


def test_route_iceberg_divert_emits_cryptolalia(tmp_path: Path):
    router = mirror_router_for_lab(tmp_path / "MIRROR")
    result = router.route_iceberg_divert(
        "agent_01",
        '{"probe": true}',
        layer_error="CHAIN_DEPTH_ANOMALY",
        layer_detail="UNTRUSTED_ORIGIN_PRIVILEGED_TARGET",
        layer_result={"verdict": "CHAIN_DEPTH_ANOMALY", "route": "MIRROR_DIMENSION"},
    )
    assert result["routed"] is True
    assert result["cryptolalia_bytes"] > 1000
    crypto = tmp_path / "MIRROR" / "cells" / "agent_01" / "cryptolalia_stream.txt"
    assert crypto.exists()
    record = json.loads(
        (tmp_path / "MIRROR" / "cells" / "agent_01" / "route_record.json").read_text()
    )
    assert record["source"] == "ICEBERG"


def test_gate_mirror_lab_wires_cryptolalia_on_l9_divert(tmp_path: Path):
    priv, pub_b64 = generate_agent_keypair()
    agent_id = "agent_01"
    keyring = AgentKeyring()
    keyring.register(agent_id, pub_b64)
    mirror_root = tmp_path / "MIRROR"
    state = tmp_path / "state"
    gate = MetadataIngressGate(
        keyring=keyring,
        nonce_state_path=state / "recv_nonce.json",
        chain_depth_layer=ProvenanceChainDepthLayer(state_path=state / "chain.json"),
        mirror_lab_root=mirror_root,
        window=TimeWindow(max_transit_ms=120_000, max_future_skew_ms=120_000),
    )
    signer = AgentSigner(agent_id, priv, nonce_state_path=state / "send_nonce.json")
    payload = {"case": "gate cryptolalia wire"}

    warm = dict(
        origin_lane="USER_INPUT",
        clearance_level="RESTRICTED",
        target_capability="READ_ONLY",
        target_lane="AGENT_TRUSTED",
    )
    for _ in range(2):
        assert gate.admit(signer.seal(payload, **warm))[0] is True

    ok, result = gate.admit(
        signer.seal(
            payload,
            origin_lane="SYSTEM_CORE",
            clearance_level="PRIVILEGED",
            target_capability="EXECUTE",
        )
    )
    assert ok is False
    assert result["error"] == "CHAIN_DEPTH_ANOMALY"
    assert result["cryptolalia"]["routed"] is True
    assert result["cryptolalia"]["cryptolalia_bytes"] > 1000

    crypto = mirror_root / "cells" / agent_id / "cryptolalia_stream.txt"
    assert crypto.exists()


def test_bridge_route_gate_divert(tmp_path: Path):
    router = mirror_router_for_lab(tmp_path / "MIRROR")
    layer_result = {"verdict": "CHAIN_DEPTH_ANOMALY", "route": "MIRROR_DIMENSION"}
    route = route_gate_divert_to_mirror(
        router,
        "agent_02",
        error="CHAIN_DEPTH_ANOMALY",
        detail="UNTRUSTED_ORIGIN_PRIVILEGED_TARGET",
        payload={"x": 1},
        layer_result=layer_result,
    )
    assert route["routed"] is True


def test_critic_path_still_requires_hostile_payload(tmp_path: Path):
    router = MirrorDimensionRouter(tmp_path / "MIRROR")
    benign = '{"query": "list tickets"}'
    result = router.route_to_mirror("agent_03", benign)
    assert result["routed"] is False
