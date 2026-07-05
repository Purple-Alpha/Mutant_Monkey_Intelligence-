"""Spec T1-T3 for provenance_chain_depth_layer.py (REV A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metadata_ingress_gate import (
    AgentKeyring,
    AgentSigner,
    MetadataIngressGate,
    generate_agent_keypair,
)
from provenance_chain_depth_layer import (
    REASON_UNTRUSTED_PRIVILEGED,
    ProvenanceChainDepthLayer,
    _content_hash,
)


@pytest.fixture
def layer(tmp_path: Path) -> ProvenanceChainDepthLayer:
    return ProvenanceChainDepthLayer(
        state_path=tmp_path / "chain_depth.json",
        min_chain_observations=2,
    )


def _chain(
    layer: ProvenanceChainDepthLayer,
    sender_id: str,
    payload: dict,
    *,
    ingress_lane: str,
    routing_capability: str,
    routing_target_lane: str = "",
):
    return layer.analyze_chain(
        sender_id,
        {},
        payload,
        ingress_lane=ingress_lane,
        routing_capability=routing_capability,
        routing_target_lane=routing_target_lane,
    )


def test_t1_first_contact_laundering_routes_to_mirror(layer: ProvenanceChainDepthLayer):
    """T1 - untrusted ingress + privileged routing on observation 1 mirrors immediately."""
    ok, result = _chain(
        layer,
        "agent_01",
        {"case": "launder"},
        ingress_lane="USER_INPUT",
        routing_capability="EXECUTE",
        routing_target_lane="SYSTEM_CORE",
    )
    assert ok is True
    assert result["route"] == "MIRROR_DIMENSION"
    assert result["detail"]["reason"] == REASON_UNTRUSTED_PRIVILEGED
    assert result["detail"]["observations"] == 1
    assert result["detail"]["max_depth"] == 0
    assert result["detail"]["origin_trust"] == "UNTRUSTED"


def test_untrusted_non_privileged_still_record_only(layer: ProvenanceChainDepthLayer):
    """Untrusted non-privileged contacts remain record-only during warm-up."""
    payload = {"case": "same content"}
    for _ in range(2):
        ok, result = _chain(
            layer,
            "agent_01",
            payload,
            ingress_lane="USER_INPUT",
            routing_capability="READ_ONLY",
            routing_target_lane="AGENT_TRUSTED",
        )
        assert ok is True
        assert result["verdict"] == "CHAIN_OK"
        assert result["route"] != "MIRROR_DIMENSION"
        assert result["detail"]["mode"] == "WARMUP_RECORD_ONLY"


def test_t2_trusted_chain_deep_rewrap_no_false_positive(layer: ProvenanceChainDepthLayer):
    """T2 - trusted origin with sender changes does not false-positive."""
    payload = {"case": "trusted content"}
    senders = ["s1", "s2", "s3", "s4"]

    for sender in senders:
        ok, result = _chain(
            layer,
            sender,
            payload,
            ingress_lane="SYSTEM_CORE",
            routing_capability="EXECUTE",
            routing_target_lane="SYSTEM_CORE",
        )
        assert ok is True
        assert result["route"] != "MIRROR_DIMENSION"

    row = layer._chains()[_content_hash(payload)]
    assert row["max_depth"] == 3
    assert row["first_origin_lane"] == "SYSTEM_CORE"
    assert row["origin_trust"] == "TRUSTED"


def test_t3_leaked_key_rewrap_and_trust_downgrade(layer: ProvenanceChainDepthLayer):
    """T3 - untrusted origin cannot reach privilege; trust only decreases."""
    payload = {"case": "rewrapped user content"}

    for _ in range(2):
        ok, result = _chain(
            layer,
            "agent_01",
            payload,
            ingress_lane="USER_INPUT",
            routing_capability="READ_ONLY",
            routing_target_lane="AGENT_TRUSTED",
        )
        assert ok is True
        assert result["route"] != "MIRROR_DIMENSION"

    ok, result = _chain(
        layer,
        "core_agent",
        payload,
        ingress_lane="SYSTEM_CORE",
        routing_capability="EXECUTE",
        routing_target_lane="SYSTEM_CORE",
    )
    assert ok is True
    assert result["route"] == "MIRROR_DIMENSION"
    assert result["detail"]["reason"] == REASON_UNTRUSTED_PRIVILEGED
    assert result["detail"]["max_depth"] == 1

    trusted_payload = {"case": "trust downgrade"}
    ok, _ = _chain(
        layer,
        "core_agent",
        trusted_payload,
        ingress_lane="SYSTEM_CORE",
        routing_capability="READ_ONLY",
    )
    assert ok is True

    ok, result = _chain(
        layer,
        "agent_01",
        trusted_payload,
        ingress_lane="USER_INPUT",
        routing_capability="READ_ONLY",
        routing_target_lane="AGENT_TRUSTED",
    )
    assert ok is True
    assert result["detail"]["origin_trust"] == "UNTRUSTED"

    ok, result = _chain(
        layer,
        "core_agent",
        trusted_payload,
        ingress_lane="SYSTEM_CORE",
        routing_capability="EXECUTE",
    )
    assert ok is True
    assert result["route"] == "MIRROR_DIMENSION"


def test_l9_gate_wire_routes_to_mirror_before_nonce_commit(tmp_path: Path):
    """Gate integration - L9 runs after L7 and before nonce commit."""
    priv, pub_b64 = generate_agent_keypair()
    signer = AgentSigner("agent_01", priv, nonce_state_path=tmp_path / "send_nonce.json")
    keyring = AgentKeyring()
    keyring.register("agent_01", pub_b64)
    chain_depth = ProvenanceChainDepthLayer(
        state_path=tmp_path / "chain_depth.json",
        min_chain_observations=2,
    )
    gate = MetadataIngressGate(
        keyring=keyring,
        nonce_state_path=tmp_path / "recv_nonce.json",
        chain_depth_layer=chain_depth,
    )
    payload = {"case": "same content through chain"}

    for _ in range(2):
        ok, result = gate.admit(
            signer.seal(
                payload,
                origin_lane="USER_INPUT",
                clearance_level="RESTRICTED",
                target_capability="READ_ONLY",
                target_lane="AGENT_TRUSTED",
            )
        )
        assert ok is True
        assert result == payload

    env = signer.seal(
        payload,
        origin_lane="SYSTEM_CORE",
        clearance_level="PRIVILEGED",
        target_capability="EXECUTE",
    )
    nonce = json.loads(env)["metadata"]["provenance"]["nonce"]
    prev = gate._nonces.last("agent_01")
    ok, result = gate.admit(env)

    assert ok is False
    assert result["error"] == "CHAIN_DEPTH_ANOMALY"
    assert result["route"] == "MIRROR_DIMENSION"
    assert result["detail"] == REASON_UNTRUSTED_PRIVILEGED
    assert nonce > prev
    assert gate._nonces.last("agent_01") == prev
