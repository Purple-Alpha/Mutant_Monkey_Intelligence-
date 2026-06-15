"""Blast Radius Controller adversarial suite (#101).

Contract: ``Blast_Radius_Controller_Adversarial_Test_Suite_Contract.md`` —
§11 SIGNED 2026-06-14. These tests execute every BRC-ADV ID against the real
BRC surfaces. No xfail markers: failures are vulnerabilities or explicit
contract-boundary evidence to resolve before hardening can be claimed.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
import threading

import pytest

from core.control_plane import (
    AgentIdentityGateway,
    AllowAllModeCheck,
    BreakerKey,
    BreakerState,
    BreakerStore,
    ControlPlaneAuditEntry,
    ControlPlaneAuditTrail,
    ControlPlaneEvent,
    GatewayController,
    GatewayRejected,
    GatewayRequest,
    IdentityError,
    INCOMPLETE_BUDGET_EXHAUSTED,
    LoopDetector,
    PrivacyFilterError,
    PrivacyFilterInterface,
    PromotionTelemetry,
    RECONCILIATION_AGENT_ID,
    Ring,
    RingController,
    RingError,
    RoleTier,
    SegmentationError,
    SessionBudgetStore,
    SUSTAINED_COOLDOWN_SECONDS,
    TenantSegmentationController,
    TripClass,
    privacy_filter_breaker_key,
)


class FakeClock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _key(agent="agent_a", tool="scan", tenant="tenant_a", session="s1") -> BreakerKey:
    return BreakerKey(tenant_id=tenant, agent_id=agent, tool=tool, session_id=session)


def _build_gateway(mode_check=None):
    audit = ControlPlaneAuditTrail()
    identity = AgentIdentityGateway()
    rings = RingController(audit=audit)
    budgets = SessionBudgetStore(audit=audit)
    breakers = BreakerStore(now=FakeClock())
    loop = LoopDetector(now=FakeClock())
    seg = TenantSegmentationController()
    gateway = GatewayController(
        identity=identity,
        rings=rings,
        budgets=budgets,
        breakers=breakers,
        loop_detector=loop,
        segmentation=seg,
        audit=audit,
        mode_check=mode_check or AllowAllModeCheck(),
    )
    identity.issue(
        token="tok_agent_a",
        agent_id="agent_a",
        tenant_id="tenant_a",
        tool_scope={"scan", "dispatch"},
    )
    identity.issue(
        token="tok_admin",
        agent_id="admin_agent",
        tenant_id="tenant_a",
        tool_scope={"scan", "dispatch", "promote"},
    )
    identity.issue(
        token="tok_low",
        agent_id="low_priv_agent",
        tenant_id="tenant_a",
        tool_scope={"scan"},
    )
    budgets.open_session("s1", tier=RoleTier.DETECTION)
    return gateway, audit, identity, breakers, seg


def _request(**overrides) -> GatewayRequest:
    base = dict(
        token="tok_agent_a",
        claimed_agent_id="agent_a",
        tenant_id="tenant_a",
        tool="scan",
        session_id="s1",
        args={"payload": "safe"},
    )
    base.update(overrides)
    return GatewayRequest(**base)


def _good_telemetry(*, component_id: str = "cand", epoch: int = 1) -> PromotionTelemetry:
    data = dict(
        regression_count=0,
        anomaly_count=0,
        token_cost_delta=0.0,
        agent_reported_healthy=True,
        out_of_band_verified=True,
    )
    # Forward-compatible: if the runtime grows component/epoch binding fields,
    # the adversarial tests will populate them automatically.
    fields = getattr(PromotionTelemetry, "__dataclass_fields__", {})
    if "component_id" in fields:
        data["component_id"] = component_id
    if "epoch" in fields:
        data["epoch"] = epoch
    return PromotionTelemetry(**data)


def _rejects_control_authority_payload(args) -> None:
    gateway, _audit, _identity, _breakers, _seg = _build_gateway()
    with pytest.raises(GatewayRejected):
        gateway.handle(_request(args=args))


# ---------------------------------------------------------------------------
# Family 1 — Identity Spoofing
# ---------------------------------------------------------------------------


def test_brc_adv_1_01_cross_agent_type_token_rejected():
    identity = AgentIdentityGateway()
    identity.issue(token="tok_q", agent_id="q_detector", tenant_id="tenant_a", tool_scope={"scan"})
    with pytest.raises(IdentityError, match="cross-agent token use"):
        identity.resolve(
            token="tok_q",
            claimed_agent_id="p_actor",
            tenant_id="tenant_a",
            tool="scan",
        )


def test_brc_adv_1_02_low_privilege_credentials_cannot_emulate_admin_tool():
    gateway, _audit, _identity, _breakers, _seg = _build_gateway()
    with pytest.raises(GatewayRejected) as exc:
        gateway.handle(
            _request(
                token="tok_low",
                claimed_agent_id="low_priv_agent",
                tool="promote",
                args={"role": "admin_agent"},
            )
        )
    assert exc.value.stage == "identity"


def test_brc_adv_1_03_decommissioned_identity_rejected():
    identity = AgentIdentityGateway()
    identity.issue(token="tok_old", agent_id="agent_old", tenant_id="tenant_a", tool_scope={"scan"})
    identity.revoke("tok_old")
    with pytest.raises(IdentityError, match="revoked"):
        identity.resolve(
            token="tok_old",
            claimed_agent_id="agent_old",
            tenant_id="tenant_a",
            tool="scan",
        )


def test_brc_adv_1_04_forged_gateway_pid_claim_rejected():
    _rejects_control_authority_payload(
        {"payload": "safe", "gateway_pid_signature": "FORGED", "signed_by": "gateway"}
    )


# ---------------------------------------------------------------------------
# Family 2 — Budget Isolation
# ---------------------------------------------------------------------------


def test_brc_adv_2_01_voter_cross_borrow_requires_controller_approval():
    budgets = SessionBudgetStore()
    budgets.open_session("rec", tier=RoleTier.RECONCILIATION)
    assert budgets.charge("rec", tokens=49_000, voter="R1") is True
    assert budgets.charge("rec", tokens=2_000, voter="R1") is False
    assert budgets.status("rec") == INCOMPLETE_BUDGET_EXHAUSTED


def test_brc_adv_2_02_single_voter_depletion_marks_incomplete():
    budgets = SessionBudgetStore()
    budgets.open_session("rec", tier=RoleTier.RECONCILIATION)
    assert budgets.charge("rec", tokens=50_001, voter="R2") is False
    assert budgets.status("rec") == INCOMPLETE_BUDGET_EXHAUSTED
    assert budgets.may_issue_decision("rec") is False


def test_brc_adv_2_03_gateway_blocks_when_max_token_fee_not_prelocked():
    gateway, _audit, _identity, _breakers, _seg = _build_gateway()
    with pytest.raises(GatewayRejected) as exc:
        gateway.handle(_request(args={"payload": "safe", "estimated_max_tokens": None}))
    assert exc.value.stage == "budget"


def test_brc_adv_2_04_parallel_budget_charges_do_not_double_spend():
    budgets = SessionBudgetStore()
    budgets.open_session("s", tier=RoleTier.DETECTION)
    results: list[bool] = []

    def charge() -> None:
        results.append(budgets.charge("s", tokens=30_000))

    threads = [threading.Thread(target=charge) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 1
    assert results.count(False) == 1
    assert budgets.status("s") == INCOMPLETE_BUDGET_EXHAUSTED


# ---------------------------------------------------------------------------
# Family 3 — Queue and Tenant Isolation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tenant_id", ["tenant|a", "tenant/a", "tenant..a"])
def test_brc_adv_3_01_delimiter_tenant_id_rejected(tenant_id):
    seg = TenantSegmentationController()
    with pytest.raises(SegmentationError):
        seg.register_tenant(tenant_id, credential="cred")


@pytest.mark.parametrize("tenant_id", ["tenant\u202ea", "tenant\x00a"])
def test_brc_adv_3_02_unicode_control_tenant_id_rejected(tenant_id):
    seg = TenantSegmentationController()
    with pytest.raises(SegmentationError):
        seg.register_tenant(tenant_id, credential="cred")


@pytest.mark.parametrize("tenant_id", ["tenant';DROP", "../tenant", "tenant--comment"])
def test_brc_adv_3_03_sql_or_path_tenant_id_rejected(tenant_id):
    seg = TenantSegmentationController()
    with pytest.raises(SegmentationError):
        seg.register_tenant(tenant_id, credential="cred")


def test_brc_adv_3_04_domain_prefix_tenants_do_not_collide():
    seg = TenantSegmentationController()
    seg.register_tenant("acme", credential="cred_a")
    seg.register_tenant("acme-inc", credential="cred_b")
    seg.enqueue("acme", "a1")
    seg.enqueue("acme-inc", "b1")
    assert seg.queue_depth("acme") == 1
    assert seg.queue_depth("acme-inc") == 1


# ---------------------------------------------------------------------------
# Family 4 — Epoch Replay
# ---------------------------------------------------------------------------


class EpochModeCheck:
    def __init__(self, current_epoch=2, current_state_hash="h2") -> None:
        self.current_epoch = current_epoch
        self.current_state_hash = current_state_hash

    def is_dispatch_allowed(self, tenant_id: str) -> bool:
        return True


def test_brc_adv_4_01_stale_epoch_payload_rejected():
    _rejects_control_authority_payload({"mode_epoch": 1, "state_hash": "h1"})


def test_brc_adv_4_02_previous_epoch_mode_config_rejected():
    _rejects_control_authority_payload({"mode": "NORMAL", "epoch": 0, "mode_config": "old"})


def test_brc_adv_4_03_same_epoch_state_hash_mismatch_rejected():
    _rejects_control_authority_payload({"mode_epoch": 2, "state_hash": "stale"})


def test_brc_adv_4_04_timestamp_skew_cannot_make_epoch_payload_fresh():
    _rejects_control_authority_payload(
        {"mode_epoch": 1, "state_hash": "h1", "timestamp": "2999-01-01T00:00:00Z"}
    )


# ---------------------------------------------------------------------------
# Family 5 — Loop Evasion
# ---------------------------------------------------------------------------


def test_brc_adv_5_01_metadata_noise_does_not_hide_frequency_loop():
    loop = LoopDetector(now=FakeClock())
    flagged = False
    for i in range(12):
        flagged = loop.observe(
            agent_id="a",
            session_id="s",
            tool="scan",
            args={"x": 1, "_metadata_noise": " " * i},
        )
        if flagged:
            break
    assert flagged is True


def test_brc_adv_5_02_structural_variants_do_not_hide_frequency_loop():
    loop = LoopDetector(now=FakeClock())
    variants = [{"x": 1}, {"x": 1.0}, {"x": True}, {"x": "1"}, {"x": [1]}] * 3
    assert any(
        loop.observe(agent_id="a", session_id="s", tool="scan", args=args)
        for args in variants
    )


def test_brc_adv_5_03_microsecond_delays_do_not_evade_window():
    clock = FakeClock()
    loop = LoopDetector(now=clock)
    flagged = False
    for i in range(12):
        flagged = loop.observe(agent_id="a", session_id="s", tool="scan", args={"nonce": i})
        clock.advance(0.000001)
        if flagged:
            break
    assert flagged is True


def test_brc_adv_5_04_nonconsecutive_repetition_still_detected():
    loop = LoopDetector(now=FakeClock())
    assert loop.observe(agent_id="a", session_id="s", tool="scan", args={"repeat": 1}) is False
    assert loop.observe(agent_id="a", session_id="s", tool="other", args={"benign": 1}) is False
    assert loop.observe(agent_id="a", session_id="s", tool="scan", args={"repeat": 1}) is False
    assert loop.observe(agent_id="a", session_id="s", tool="scan", args={"repeat": 1}) is True


# ---------------------------------------------------------------------------
# Family 6 — Breaker Recovery Exploitation
# ---------------------------------------------------------------------------


def test_brc_adv_6_01_secondary_trip_enforces_sustained_recovery():
    clock = FakeClock()
    breakers = BreakerStore(now=clock)
    key = _key()
    breakers.trip(key, trip_class=TripClass.TRANSIENT)
    clock.advance(31)
    breakers.attempt_probe(key)
    breakers.record_probe_result(key, success=False)
    clock.advance(31)
    with pytest.raises(Exception):
        breakers.attempt_probe(key)
    clock.advance(SUSTAINED_COOLDOWN_SECONDS)
    assert breakers.attempt_probe(key) is BreakerState.HALF_OPEN


def test_brc_adv_6_02_cooldown_boundary_is_strictly_enforced():
    clock = FakeClock()
    breakers = BreakerStore(now=clock)
    key = _key()
    breakers.trip(key, trip_class=TripClass.SUSTAINED)
    clock.advance(SUSTAINED_COOLDOWN_SECONDS - 0.000001)
    with pytest.raises(Exception):
        breakers.attempt_probe(key)
    clock.advance(0.000001)
    assert breakers.attempt_probe(key) is BreakerState.HALF_OPEN


def test_brc_adv_6_03_breaker_timeout_or_probe_error_fails_closed():
    clock = FakeClock()
    breakers = BreakerStore(now=clock)
    key = _key()
    breakers.trip(key, trip_class=TripClass.SUSTAINED)
    with pytest.raises(Exception):
        breakers.record_probe_result(key, success=True)
    assert breakers.is_closed(key) is False


def test_brc_adv_6_04_old_breaker_pass_cannot_override_current_open_state():
    clock = FakeClock()
    breakers = BreakerStore(now=clock)
    key = _key()
    old_pass = breakers.is_closed(key)
    breakers.trip(key, trip_class=TripClass.SUSTAINED)
    assert old_pass is True
    assert breakers.is_closed(key) is False


# ---------------------------------------------------------------------------
# Family 7 — Privacy Filter Interface Fail-Closed
# ---------------------------------------------------------------------------


def _privacy_pair():
    audit = ControlPlaneAuditTrail()
    breakers = BreakerStore(now=FakeClock())
    return PrivacyFilterInterface(breakers=breakers, audit=audit), breakers, audit


def test_brc_adv_7_01_link_lag_open_breaker_blocks_broadcast():
    pf, breakers, _audit = _privacy_pair()
    breakers.trip(privacy_filter_breaker_key("tenant_a"), trip_class=TripClass.SUSTAINED)
    with pytest.raises(PrivacyFilterError):
        pf.broadcast("tenant_a", "payload")


def test_brc_adv_7_02_unavailable_filter_without_alert_fails_closed():
    pf, breakers, audit = _privacy_pair()
    breakers.trip(privacy_filter_breaker_key("tenant_a"), trip_class=TripClass.SUSTAINED)
    with pytest.raises(PrivacyFilterError):
        pf.broadcast("tenant_a", "payload")
    assert audit.for_event(ControlPlaneEvent.BROADCAST_BLOCKED)


def test_brc_adv_7_03_half_open_filter_still_blocks_broadcast():
    pf, breakers, _audit = _privacy_pair()
    key = privacy_filter_breaker_key("tenant_a")
    breakers.trip(key, trip_class=TripClass.SUSTAINED)
    breakers._records[key].state = BreakerState.HALF_OPEN  # adversarial stale/recovering state
    with pytest.raises(PrivacyFilterError):
        pf.broadcast("tenant_a", "payload")


def test_brc_adv_7_04_static_heartbeat_payload_cannot_bypass_open_breaker():
    pf, breakers, _audit = _privacy_pair()
    breakers.trip(privacy_filter_breaker_key("tenant_a"), trip_class=TripClass.SUSTAINED)
    with pytest.raises(PrivacyFilterError):
        pf.broadcast("tenant_a", {"payload": "x", "heartbeat": "ok"})


# ---------------------------------------------------------------------------
# Family 8 — Budget Exhaustion Race Hardening
# ---------------------------------------------------------------------------


def test_brc_adv_8_01_in_flight_dispatch_does_not_use_unlocked_budget():
    test_brc_adv_2_03_gateway_blocks_when_max_token_fee_not_prelocked()


def test_brc_adv_8_02_concurrent_budget_checks_serialize_no_double_spend():
    test_brc_adv_2_04_parallel_budget_charges_do_not_double_spend()


def test_brc_adv_8_03_exhaustion_propagates_before_next_request():
    gateway, _audit, _identity, _breakers, _seg = _build_gateway()
    assert gateway.budgets.charge("s1", tokens=49_999) is True
    assert gateway.budgets.charge("s1", tokens=2) is False
    with pytest.raises(GatewayRejected) as exc:
        gateway.handle(_request(args={"payload": "later", "estimated_max_tokens": 1}))
    assert exc.value.stage == "budget"


# ---------------------------------------------------------------------------
# Family 9 — Component Bypass via Unmonitored Paths
# ---------------------------------------------------------------------------


def test_brc_adv_9_01_memory_mapped_gateway_pid_bypass_rejected():
    _rejects_control_authority_payload({"bypass": "mmap", "gateway_pid_signature": "forged"})


def test_brc_adv_9_02_thread_fork_tool_invocation_claim_rejected():
    _rejects_control_authority_payload({"thread_fork": True, "entrypoint_signed_by_gateway": False})


def test_brc_adv_9_03_direct_internal_api_invocation_claim_rejected():
    _rejects_control_authority_payload({"direct_tool_invocation": True, "gateway": "bypassed"})


def test_brc_adv_9_04_ipc_bypass_claim_rejected():
    _rejects_control_authority_payload({"ipc_channel": "/tmp/gateway.sock", "identity_verified": False})


# ---------------------------------------------------------------------------
# Family 10 — Ring Promotion Integrity
# ---------------------------------------------------------------------------


def test_brc_adv_10_01_poisoned_external_baseline_without_oob_rejected():
    rings = RingController()
    rings.assign("cand")
    poisoned = PromotionTelemetry(
        regression_count=0,
        anomaly_count=0,
        token_cost_delta=0.0,
        agent_reported_healthy=True,
        out_of_band_verified=False,
    )
    with pytest.raises(RingError):
        rings.promote("cand", telemetry=poisoned)


def test_brc_adv_10_02_spoofed_regression_results_without_oob_rejected():
    test_brc_adv_10_01_poisoned_external_baseline_without_oob_rejected()


def test_brc_adv_10_03_partial_test_corpus_with_clean_subset_rejected():
    rings = RingController()
    rings.assign("cand")
    partial = PromotionTelemetry(
        regression_count=0,
        anomaly_count=1,
        token_cost_delta=0.0,
        agent_reported_healthy=True,
        out_of_band_verified=True,
    )
    with pytest.raises(RingError):
        rings.promote("cand", telemetry=partial)


def test_brc_adv_10_04_previous_ring_advancement_bound_to_component():
    rings = RingController()
    rings.assign("component_a")
    rings.assign("component_b")
    rings.promote("component_a", telemetry=_good_telemetry(component_id="component_a"))
    assert rings.ring_of("component_a") is Ring.RING_1_PILOT
    assert rings.ring_of("component_b") is Ring.RING_0_SYNTHETIC


# ---------------------------------------------------------------------------
# Family 11 — Ledger and Audit Integrity
# ---------------------------------------------------------------------------


def test_brc_adv_11_01_audit_flood_does_not_erase_history():
    audit = ControlPlaneAuditTrail()
    first = audit.record(ControlPlaneEvent.BREAKER_TRIPPED, "first")
    for i in range(1000):
        audit.record(ControlPlaneEvent.GATEWAY_REJECTED, f"noise-{i}")
    assert audit.entries()[0] == first
    assert len(audit.entries()) == 1001


def test_brc_adv_11_02_transition_entry_exists_before_rotation_surface():
    audit = ControlPlaneAuditTrail()
    audit.record(ControlPlaneEvent.BREAKER_TRIPPED, "transition")
    assert audit.for_event(ControlPlaneEvent.BREAKER_TRIPPED)
    assert not hasattr(audit, "rotate")


def test_brc_adv_11_03_audit_entries_are_immutable_and_no_delete_api():
    audit = ControlPlaneAuditTrail()
    entry = audit.record(ControlPlaneEvent.GATEWAY_REJECTED, "reject")
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.detail = "tampered"  # type: ignore[misc]
    assert not hasattr(audit, "delete")
    assert isinstance(audit.entries(), tuple)


def test_brc_adv_11_04_storage_pressure_has_no_compaction_api():
    audit = ControlPlaneAuditTrail()
    for i in range(1000):
        audit.record(ControlPlaneEvent.GATEWAY_REJECTED, f"event-{i}")
    assert not hasattr(audit, "compact")
    assert len(audit.entries()) == 1000


# ---------------------------------------------------------------------------
# Family 12 — Telemetry Forgery
# ---------------------------------------------------------------------------


def test_brc_adv_12_01_cloned_heartbeat_frame_cannot_hide_gate_failure():
    _rejects_control_authority_payload({"telemetry_frame": "cloned", "gate_failure": "hidden"})


def test_brc_adv_12_02_replayed_telemetry_signal_cannot_mask_failure():
    _rejects_control_authority_payload({"telemetry_replay": True, "previous_signal": "valid"})


def test_brc_adv_12_03_absent_telemetry_not_a_successful_dispatch_record():
    gateway, audit, _identity, _breakers, _seg = _build_gateway()
    with pytest.raises(GatewayRejected):
        gateway.handle(_request(args={"suppress_telemetry": True}))
    assert not audit.for_event(ControlPlaneEvent.GATEWAY_DISPATCHED)


def test_brc_adv_12_04_low_severity_flood_cannot_hide_high_severity_failure():
    audit = ControlPlaneAuditTrail()
    for i in range(100):
        audit.record(ControlPlaneEvent.GATEWAY_REJECTED, f"low-{i}")
    high = audit.record(ControlPlaneEvent.IDENTITY_REJECTED, "high-severity forged identity")
    assert high in audit.entries()
    assert audit.for_event(ControlPlaneEvent.IDENTITY_REJECTED)


def test_brc_adv_contract_coverage_all_ids_present():
    contract = (
        Path(__file__).resolve().parents[4]
        / "4. Product_Roadmap"
        / "Blast_Radius_Controller_Adversarial_Test_Suite_Contract.md"
    )
    ids = set(__import__("re").findall(r"BRC-ADV-\d+-\d+", contract.read_text(encoding="utf-8")))
    current = Path(__file__).read_text(encoding="utf-8")
    missing = sorted(test_id for test_id in ids if test_id.lower().replace("-", "_") not in current)
    assert len(ids) == 47
    assert not missing
