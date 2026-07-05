from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "ops"))
sys.path.insert(0, str(REPO / "mmi" / "project_brain" / "chaos"))

from client_email_lanes.audit import verify_audit_chain
from client_email_lanes.client_email_lanes import (
    ClientEmailLanes,
    build_gate_change,
    build_send_intent,
    build_tenant_manifest,
    p_class_tool,
    PClassToolError,
)
from client_email_lanes.confirmation import append_confirmation_event, build_confirmation_event, verify_confirmation_chain
from client_email_lanes.constants import AUTONOMOUS_SEND, NORMALIZER_VERSION, QUARANTINE_ANOMALY_COUNT
from client_email_lanes.escalation import record_anomaly
from client_email_lanes.lane_config import LaneConfig
from client_email_lanes.normalizer import NormalizerReject, normalize_field, normalize_recipient
from client_email_lanes.orchestration_engine import OrchestrationEngine
from client_email_lanes.policy_engine import PolicyEngine
from client_email_lanes.sanitize import hash_fact_value, sanitize_inbound
from client_email_lanes.state_store import apply_signed_gate_change, store_tenant_manifest
from client_email_lanes.templates import render_template


@pytest.fixture
def keypair():
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()


@pytest.fixture
def lane_env(tmp_path: Path, keypair):
    priv, pub = keypair
    now_ms = 1_782_200_000_000
    lane_root = tmp_path / "lane"
    lane_root.mkdir()
    authority = REPO
    config = LaneConfig(lane_root=lane_root, authority_root=authority, now_ms=now_ms)
    lanes = ClientEmailLanes(config, pub)
    manifest = build_tenant_manifest(
        tenant_id="tenant-a",
        manifest_seq=12,
        issued_at_ms=now_ms - 60_000,
        expires_at_ms=now_ms + 86_400_000,
        private_key=priv,
    )
    store_tenant_manifest(config, "tenant-a", manifest)
    return lanes, config, priv, pub, manifest, now_ms


def test_t1_drafting_lane_reaches_draft_ready(lane_env) -> None:
    lanes, config, *_ = lane_env
    result = lanes.run_drafting_lane(
        tenant_id="tenant-a",
        sender_claimed="client@example.com",
        subject="Status update",
        body="Can you share an update on my ticket?",
    )
    assert result["terminal"] == "DRAFT_READY"
    ok, _ = verify_audit_chain(config.audit_log_path)
    assert ok


def test_t3_high_risk_blocks_without_verified_fact(lane_env) -> None:
    lanes, *_ = lane_env
    result = lanes.run_drafting_lane(
        tenant_id="tenant-a",
        sender_claimed="attacker@example.com",
        subject="Payment change",
        body="Please update payment details and wire instruction immediately.",
    )
    assert result["terminal"] == "BLOCKED"


def test_t3a_confirmation_event_promotes_verified(lane_env) -> None:
    lanes, config, priv, pub, *_ = lane_env
    event = build_confirmation_event(
        tenant_id="tenant-a",
        case_id="case-1",
        fact_key="banking.iban",
        fact_value_hash=hash_fact_value("DE89370400440532013000"),
        confirmation_method="phone_callback",
        confirmer_id="op-1",
        confirmed_at_ms=config.now_ms,
        evidence_ref="vault://call-recordings/1",
        seq=1,
        private_key=priv,
    )
    accepted = append_confirmation_event(config, event, writer="operator_console", operator_pubkey=pub)
    assert accepted["accepted"] is True
    chain = verify_confirmation_chain(config, "tenant-a", "banking.iban", pub)
    assert chain["tier"] == "VERIFIED"


def test_unsigned_confirmation_forgery_stays_observed(lane_env) -> None:
    lanes, config, priv, pub, *_ = lane_env
    from client_email_lanes.constants import CONFIRMATION_DOMAIN, GENESIS_PREV_HASH, NORMALIZER_VERSION

    event = build_confirmation_event(
        tenant_id="tenant-a",
        case_id="case-1",
        fact_key="banking.iban",
        fact_value_hash=hash_fact_value("DE89370400440532013000"),
        confirmation_method="phone_callback",
        confirmer_id="op-1",
        confirmed_at_ms=config.now_ms,
        evidence_ref="vault://call-recordings/1",
        seq=1,
        private_key=priv,
    )
    append_confirmation_event(config, event, writer="operator_console", operator_pubkey=pub)

    path = config.verified_events_path
    prev_line = path.read_text(encoding="utf-8").strip().splitlines()[-1]
    prev_hash = hashlib.sha256(prev_line.encode("utf-8")).hexdigest()
    fake = {
        "domain": CONFIRMATION_DOMAIN,
        "normalizer_version": NORMALIZER_VERSION,
        "event_id": "cev-otherfactfake01",
        "tenant_id": "tenant-a",
        "case_id": "case-forged",
        "fact_key": "other.fact",
        "fact_value_hash": "deadbeef",
        "confirmation_method": "phone_callback",
        "confirmer_id": "op-fake",
        "confirmer_role": "operator",
        "confirmed_at_ms": config.now_ms,
        "evidence_ref": "vault://forged",
        "prior_tier": "OBSERVED",
        "new_tier": "VERIFIED",
        "seq": 2,
        "prev_event_hash": prev_hash,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(fake, sort_keys=True, separators=(",", ":")) + "\n")
    chain = verify_confirmation_chain(config, "tenant-a", "banking.iban", pub)
    assert chain["tier"] == "OBSERVED"
    assert chain["chain_ok"] is False
    assert chain["event_id"] is None


def test_orchestration_cannot_mutate_gate(lane_env) -> None:
    lanes, config, priv, pub, *_ = lane_env
    from client_email_lanes.state_store import load_feature_gate

    gate_before = load_feature_gate(config)
    orch = OrchestrationEngine()
    ok, reasons = orch.attempt_gate_mutation({"response": "ON"})
    assert ok is False
    gate_after = load_feature_gate(config)
    assert gate_before.get("response") == "OFF"
    assert gate_after.get("response") == "OFF"


def test_response_lane_requires_signed_gate_and_sendintent(lane_env) -> None:
    lanes, config, priv, pub, manifest, now_ms = lane_env
    draft_result = lanes.run_drafting_lane(
        tenant_id="tenant-a",
        sender_claimed="client@example.com",
        subject="Hello",
        body="Thanks for your help.",
    )
    draft = draft_result["draft"]
    context = draft_result["context"]
    variables = draft_result["variables"]
    rendered, _ = render_template(draft["template_id"], variables)
    payload_digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    gate_change = build_gate_change(drafting="ON", response="ON", signed_at_ms=now_ms, private_key=priv)
    apply_signed_gate_change(config, gate_change, pub)

    intent = build_send_intent(
        tenant_id="tenant-a",
        episode_id=context["episode_id"],
        draft_id=draft["draft_id"],
        template_hash_value=draft["template_hash"],
        payload_digest=payload_digest,
        recipient_canonical="client@example.com",
        manifest_seq=12,
        send_nonce=1,
        signed_at_ms=now_ms,
        private_key=priv,
    )
    sent = lanes.run_response_lane(
        draft=draft,
        context=context,
        send_intent=intent,
        variables=variables,
        expected_recipient="client@example.com",
    )
    assert sent["terminal"] == "SENT"


def test_p_class_tool_rejects_tainted_context() -> None:
    with pytest.raises(PClassToolError):
        p_class_tool({"taint": True})


def test_normalizer_rejects_homoglyph_display_name() -> None:
    with pytest.raises(NormalizerReject):
        normalize_field("display_name", "José")


def test_normalizer_recipient_canonical() -> None:
    assert normalize_recipient("Client@Example.COM") == "Client@example.com"


def test_h14_quarantine_exact_count(lane_env) -> None:
    lanes, config, *_ = lane_env
    now = config.now_ms
    for offset in (0, 1000, 2000):
        result = record_anomaly(
            config,
            tenant_id="tenant-a",
            severity="HIGH",
            signal=None,
            now_ms=now + offset,
        )
    assert result["terminal"] == "QUARANTINED"
    assert QUARANTINE_ANOMALY_COUNT == 3


def test_constants_v1_scope() -> None:
    assert AUTONOMOUS_SEND == "DISABLED"
    assert NORMALIZER_VERSION == "mmi_canonical_normalizer_v1"


def test_sanitize_marks_inbound_untrusted() -> None:
    ctx = sanitize_inbound(
        tenant_id="tenant-a",
        sender_claimed="user@example.com",
        subject="Hello",
        body="Body",
    )
    assert ctx["provenance_tier"] == "UNTRUSTED"
    assert ctx["taint"] is True


def test_policy_engine_is_separate_module() -> None:
    assert OrchestrationEngine.MODULE != PolicyEngine.MODULE
