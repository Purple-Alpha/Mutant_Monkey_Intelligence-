"""Phase 6 — Blast Radius Controller tests (Layer 6, scoreboard row #89).

Three test classes per component per AGENTS.md §5 and
``Blast_Radius_Controller_Contract.md`` §6:
  Class 1 — expected pass
  Class 2 — adversarial / metastasis (all five metastasis tests live here)
  Class 3 — known-gap xfail (documented, with completion path)

Components under test (eight):
  1. AgentIdentityGateway        (Gate 5, BRC-D7)
  2. BreakerStore                (Gate 1, BRC-D1 / BRC-D13)
  3. SessionBudgetStore          (Gate 1, BRC-D2 / BRC-D14 / BRC-D15)
  4. LoopDetector                (Gate 1, BRC-D3)
  5. TenantSegmentationController (Gate 2, BRC-D4)
  6. PrivacyFilterInterface      (Gate 2, BRC-D5)
  7. RingController              (Gate 3, BRC-D6)
  8. GatewayController           (spine, BRC-D8 / §3.6)

The five metastasis tests (contract §6 Class 2):
  M1 — argument-mutation loop bypass    → TestLoopDetectorAdversarial
  M2 — forged tenant_id                 → TestSegmentationAdversarial + gateway
  M3 — forged telemetry health signals  → TestRingControllerAdversarial
  M4 — unilateral ISOLATED mode trigger → TestGatewayAdversarial (mode-check iface)
  M5 — cross-agent identity token       → TestIdentityAdversarial + gateway
"""

from __future__ import annotations

import pytest

from core.control_plane import (
    AgentIdentityGateway,
    AllowAllModeCheck,
    BreakerKey,
    BreakerState,
    BreakerStore,
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
    SUSTAINED_PROBES_REQUIRED,
    TenantSegmentationController,
    TripClass,
    privacy_filter_breaker_key,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeClock:
    """Deterministic monotonic clock for breaker / loop-detector tests."""

    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _key(agent="agent_a", tool="scan", tenant="tenant_a", session="s1") -> BreakerKey:
    return BreakerKey(tenant_id=tenant, agent_id=agent, tool=tool, session_id=session)


# ===========================================================================
# Component 1 — AgentIdentityGateway (Gate 5, BRC-D7)
# ===========================================================================


class TestIdentityExpectedPass:
    def test_valid_resolution(self):
        gw = AgentIdentityGateway()
        gw.issue(token="tok_a", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
        resolved = gw.resolve(
            token="tok_a", claimed_agent_id="agent_a", tenant_id="tenant_a", tool="scan"
        )
        assert resolved.agent_id == "agent_a"
        assert resolved.tenant_id == "tenant_a"
        assert resolved.tool == "scan"


class TestIdentityAdversarial:
    def test_m5_cross_agent_token_rejected(self):
        """METASTASIS M5: a token bound to agent_a, presented as agent_b, is
        rejected regardless of payload content (BRC-D7)."""
        gw = AgentIdentityGateway()
        gw.issue(token="tok_a", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
        with pytest.raises(IdentityError, match="cross-agent token use"):
            gw.resolve(
                token="tok_a", claimed_agent_id="agent_b", tenant_id="tenant_a", tool="scan"
            )

    def test_tenant_scope_mismatch_rejected(self):
        gw = AgentIdentityGateway()
        gw.issue(token="tok_a", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
        with pytest.raises(IdentityError, match="tenant-scope mismatch"):
            gw.resolve(token="tok_a", claimed_agent_id="agent_a", tenant_id="tenant_b", tool="scan")

    def test_out_of_scope_tool_rejected(self):
        gw = AgentIdentityGateway()
        gw.issue(token="tok_a", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
        with pytest.raises(IdentityError, match="outside the token's tool scope"):
            gw.resolve(token="tok_a", claimed_agent_id="agent_a", tenant_id="tenant_a", tool="deploy")

    def test_revoked_token_rejected(self):
        gw = AgentIdentityGateway()
        gw.issue(token="tok_a", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
        gw.revoke("tok_a")
        with pytest.raises(IdentityError, match="revoked"):
            gw.resolve(token="tok_a", claimed_agent_id="agent_a", tenant_id="tenant_a", tool="scan")

    def test_unknown_token_rejected(self):
        gw = AgentIdentityGateway()
        with pytest.raises(IdentityError, match="unknown identity token"):
            gw.resolve(token="ghost", claimed_agent_id="agent_a", tenant_id="tenant_a", tool="scan")


class TestIdentityKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Identity is an opaque caller-supplied token, not a cryptographic "
            "credential. Completion path: bind to mTLS/JWT/SPIFFE in the Phase 6+ "
            "infrastructure hardening contract (BRC-D7, §3.7)."
        ),
        strict=True,
    )
    def test_xfail_cryptographic_identity(self):
        raise AssertionError("not implemented — infrastructure hardening contract")


# ===========================================================================
# Component 2 — BreakerStore (Gate 1, BRC-D1 / BRC-D13)
# ===========================================================================


class TestBreakerExpectedPass:
    def test_starts_closed(self):
        bs = BreakerStore(now=FakeClock())
        assert bs.is_closed(_key())

    def test_transient_recovery_one_probe(self):
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key()
        bs.trip(k, trip_class=TripClass.TRANSIENT)
        assert bs.state(k) is BreakerState.OPEN
        clock.advance(31)
        assert bs.attempt_probe(k) is BreakerState.HALF_OPEN
        assert bs.record_probe_result(k, success=True) is BreakerState.CLOSED

    def test_sustained_recovery_three_probes(self):
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key()
        bs.trip(k, trip_class=TripClass.SUSTAINED)
        for i in range(SUSTAINED_PROBES_REQUIRED):
            clock.advance(301)
            assert bs.attempt_probe(k) is BreakerState.HALF_OPEN
            state = bs.record_probe_result(k, success=True)
        assert state is BreakerState.CLOSED


class TestBreakerAdversarial:
    def test_probe_before_cooldown_refused(self):
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key()
        bs.trip(k, trip_class=TripClass.TRANSIENT)
        clock.advance(5)  # < 30s
        with pytest.raises(Exception):
            bs.attempt_probe(k)

    def test_transient_probe_failure_reclassifies_sustained(self):
        """BRC-D13: a failed transient probe reclassifies as sustained; the
        breaker then needs 3 successful probes, not 1."""
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key()
        bs.trip(k, trip_class=TripClass.TRANSIENT)
        clock.advance(31)
        bs.attempt_probe(k)
        assert bs.record_probe_result(k, success=False) is BreakerState.OPEN
        # Now sustained: a single success must NOT close it.
        clock.advance(301)
        bs.attempt_probe(k)
        assert bs.record_probe_result(k, success=True) is BreakerState.OPEN

    def test_sustained_probe_failure_resets_cooldown(self):
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key()
        bs.trip(k, trip_class=TripClass.SUSTAINED)
        clock.advance(301)
        bs.attempt_probe(k)
        bs.record_probe_result(k, success=False)
        # Cooldown reset: an immediate re-probe is refused.
        clock.advance(5)
        with pytest.raises(Exception):
            bs.attempt_probe(k)

    def test_reconciliation_agent_defaults_sustained(self):
        """BRC-D13: ReconciliationAgent always recovers under sustained rules,
        even when a transient trip is requested."""
        clock = FakeClock()
        bs = BreakerStore(now=clock)
        k = _key(agent=RECONCILIATION_AGENT_ID)
        bs.trip(k, trip_class=TripClass.TRANSIENT)
        clock.advance(31)  # transient cooldown elapsed, but sustained needs 300s
        with pytest.raises(Exception):
            bs.attempt_probe(k)
        clock.advance(270)  # now past 300s total
        assert bs.attempt_probe(k) is BreakerState.HALF_OPEN
        # one success is not enough under sustained
        assert bs.record_probe_result(k, success=True) is BreakerState.OPEN


class TestBreakerKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Breaker state is in-process only; it does not survive a gateway "
            "restart. Completion path: append-only persistence amendment."
        ),
        strict=True,
    )
    def test_xfail_breaker_state_persists(self):
        raise AssertionError("not implemented — persistence amendment")


# ===========================================================================
# Component 3 — SessionBudgetStore (Gate 1, BRC-D2 / BRC-D14 / BRC-D15)
# ===========================================================================


class TestBudgetExpectedPass:
    def test_within_budget_passes(self):
        store = SessionBudgetStore()
        store.open_session("s1", tier=RoleTier.DETECTION)
        assert store.charge("s1", tokens=10_000, tool_calls=5) is True
        assert store.may_issue_decision("s1") is True
        assert store.status("s1") == "ok"

    def test_role_tiers_differ(self):
        store = SessionBudgetStore()
        store.open_session("det", tier=RoleTier.DETECTION)
        store.open_session("rec", tier=RoleTier.RECONCILIATION)
        # 60K tokens exhausts detection (50K) but not reconciliation (150K).
        assert store.charge("det", tokens=60_000) is False
        assert store.charge("rec", tokens=60_000) is True


class TestBudgetAdversarial:
    def test_exhaustion_is_not_a_pass(self):
        """BRC-D15: exhaustion → incomplete_budget_exhausted, no decision."""
        store = SessionBudgetStore()
        store.open_session("s1", tier=RoleTier.DETECTION)
        assert store.charge("s1", tokens=999_999) is False
        assert store.status("s1") == INCOMPLETE_BUDGET_EXHAUSTED
        assert store.may_issue_decision("s1") is False
        # Exhaustion creates a governance record.
        assert store.audit.for_event(ControlPlaneEvent.BUDGET_EXHAUSTED)

    def test_exhaustion_is_sticky(self):
        store = SessionBudgetStore()
        store.open_session("s1", tier=RoleTier.CONTROL_PLANE)
        store.charge("s1", tokens=999_999)
        # Even a tiny later charge stays False.
        assert store.charge("s1", tokens=1) is False

    def test_voter_subbudget_no_borrow_without_approval(self):
        """BRC-D14: a voter cannot exceed its 50K sub-budget without controller
        approval."""
        store = SessionBudgetStore()
        store.open_session("rec", tier=RoleTier.RECONCILIATION)
        assert store.charge("rec", tokens=40_000, voter="R1") is True
        # R1 trying to push past 50K without approval → exhausted.
        assert store.charge("rec", tokens=20_000, voter="R1") is False
        assert store.status("rec") == INCOMPLETE_BUDGET_EXHAUSTED

    def test_voter_subbudget_borrow_with_approval(self):
        store = SessionBudgetStore()
        store.open_session("rec", tier=RoleTier.RECONCILIATION)
        store.charge("rec", tokens=40_000, voter="R1")
        assert (
            store.charge("rec", tokens=20_000, voter="R1", controller_approved_borrow=True)
            is True
        )


class TestBudgetKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Wall-clock budget is charged by caller-supplied elapsed seconds, not "
            "a live monotonic timer wired into dispatch. Completion path: live "
            "timer integration in the runtime loop."
        ),
        strict=True,
    )
    def test_xfail_live_wall_clock_timer(self):
        raise AssertionError("not implemented — live timer integration")


# ===========================================================================
# Component 4 — LoopDetector (Gate 1, BRC-D3)
# ===========================================================================


class TestLoopDetectorExpectedPass:
    def test_normal_traffic_no_loop(self):
        ld = LoopDetector(now=FakeClock())
        for i in range(3):
            assert ld.observe(agent_id="a", session_id="s", tool="scan", args={"i": i}) is False

    def test_identical_run_flags(self):
        ld = LoopDetector(now=FakeClock())
        ld.observe(agent_id="a", session_id="s", tool="scan", args={"x": 1})
        ld.observe(agent_id="a", session_id="s", tool="scan", args={"x": 1})
        # third identical run hits the threshold
        assert ld.observe(agent_id="a", session_id="s", tool="scan", args={"x": 1}) is True


class TestLoopDetectorAdversarial:
    def test_m1_argument_mutation_bypass_caught_by_frequency(self):
        """METASTASIS M1: an agent mutates its arguments every call to dodge the
        identical-run check, but the call-frequency signal still catches it —
        detection is behavioral, not content-based (BRC-D3)."""
        clock = FakeClock()
        ld = LoopDetector(now=clock)
        flagged = False
        for i in range(20):  # all distinct args, no time advance → frequency spike
            if ld.observe(agent_id="a", session_id="s", tool="scan", args={"nonce": i}):
                flagged = True
                break
        assert flagged is True

    def test_frequency_window_slides(self):
        clock = FakeClock()
        ld = LoopDetector(now=clock)
        # spread calls out so the window never fills
        for i in range(20):
            assert ld.observe(agent_id="a", session_id="s", tool="scan", args={"n": i}) is False
            clock.advance(2)  # 2s apart, window 10s, threshold 10 → never exceeds


class TestLoopDetectorKnownGap:
    @pytest.mark.xfail(
        reason=(
            "LoopDetector uses behavioral metrics only by design (BRC-D3, no "
            "embeddings). Semantic near-duplicate detection is intentionally out "
            "of scope. Completion path: none — this is a design boundary, tracked "
            "as a known gap so the boundary is explicit."
        ),
        strict=True,
    )
    def test_xfail_semantic_near_duplicate_detection(self):
        raise AssertionError("out of scope by design — no embeddings (BRC-D3)")


# ===========================================================================
# Component 5 — TenantSegmentationController (Gate 2, BRC-D4)
# ===========================================================================


class TestSegmentationExpectedPass:
    def test_per_tenant_queues_isolated(self):
        seg = TenantSegmentationController()
        seg.register_tenant("tenant_a", credential="cred_a")
        seg.register_tenant("tenant_b", credential="cred_b")
        seg.enqueue("tenant_a", "item1")
        assert seg.queue_depth("tenant_a") == 1
        assert seg.queue_depth("tenant_b") == 0

    def test_valid_binding_passes(self):
        seg = TenantSegmentationController()
        seg.register_tenant("tenant_a", credential="cred_a")
        seg.verify_tenant_binding(
            resolved_tenant_id="tenant_a", claimed_tenant_id="tenant_a", credential="cred_a"
        )


class TestSegmentationAdversarial:
    def test_m2_forged_tenant_id_rejected(self):
        """METASTASIS M2: a forged tenant_id (identity resolved to A, payload
        claims B) is rejected regardless of content (BRC-D4)."""
        seg = TenantSegmentationController()
        seg.register_tenant("tenant_b", credential="cred_b")
        with pytest.raises(SegmentationError, match="forged tenant_id"):
            seg.verify_tenant_binding(
                resolved_tenant_id="tenant_a", claimed_tenant_id="tenant_b", credential="cred_b"
            )

    def test_credential_mismatch_rejected(self):
        seg = TenantSegmentationController()
        seg.register_tenant("tenant_a", credential="cred_a")
        with pytest.raises(SegmentationError, match="credential mismatch"):
            seg.verify_tenant_binding(
                resolved_tenant_id="tenant_a", claimed_tenant_id="tenant_a", credential="wrong"
            )

    def test_rate_limit_is_per_tenant_no_cascade(self):
        seg = TenantSegmentationController()
        seg.register_tenant("tenant_a", credential="c", rate_limit_per_window=2)
        seg.register_tenant("tenant_b", credential="c", rate_limit_per_window=2)
        seg.enqueue("tenant_a", "1")
        seg.enqueue("tenant_a", "2")
        with pytest.raises(SegmentationError, match="rate limit"):
            seg.enqueue("tenant_a", "3")
        # tenant_b is unaffected — no cascade.
        seg.enqueue("tenant_b", "1")
        assert seg.queue_depth("tenant_b") == 1


class TestSegmentationKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Per-tenant credentials are opaque labels, not vault-managed secrets. "
            "Completion path: secrets-manager integration in Phase 6+ hardening."
        ),
        strict=True,
    )
    def test_xfail_vault_managed_credentials(self):
        raise AssertionError("not implemented — secrets-manager integration")


# ===========================================================================
# Component 6 — PrivacyFilterInterface (Gate 2, BRC-D5)
# ===========================================================================


def _privacy_pair():
    audit = ControlPlaneAuditTrail()
    breakers = BreakerStore(now=FakeClock())
    pf = PrivacyFilterInterface(breakers=breakers, audit=audit)
    return pf, breakers, audit


class TestPrivacyFilterExpectedPass:
    def test_broadcast_when_closed(self):
        pf, _breakers, _audit = _privacy_pair()
        assert pf.can_broadcast("tenant_a") is True
        assert pf.broadcast("tenant_a", "payload_ref") == "payload_ref"


class TestPrivacyFilterAdversarial:
    def test_open_filter_breaker_blocks_all_broadcast(self):
        pf, breakers, audit = _privacy_pair()
        breakers.trip(privacy_filter_breaker_key("tenant_a"), trip_class=TripClass.SUSTAINED)
        assert pf.can_broadcast("tenant_a") is False
        with pytest.raises(PrivacyFilterError):
            pf.broadcast("tenant_a", "payload_ref")
        assert audit.for_event(ControlPlaneEvent.BROADCAST_BLOCKED)

    def test_independent_failure_domains(self):
        """BRC-D5: a normal tenant/agent/tool breaker tripping does NOT block the
        privacy filter broadcast — independent domains (separate breaker keys)."""
        pf, breakers, _audit = _privacy_pair()
        # Trip an ordinary agent breaker for the same tenant.
        breakers.trip(_key(tenant="tenant_a"), trip_class=TripClass.SUSTAINED)
        # Privacy filter breaker is untouched → broadcast still allowed.
        assert pf.can_broadcast("tenant_a") is True


class TestPrivacyFilterKnownGap:
    @pytest.mark.xfail(
        reason=(
            "PrivacyFilterInterface is the gateway-side stub; the actual Privacy "
            "Filter service is a separate spec. Completion path: Privacy Filter "
            "service specification signed (contract §1 out-of-scope, §9 pre-cond 3)."
        ),
        strict=True,
    )
    def test_xfail_privacy_filter_service_live(self):
        raise AssertionError("not implemented — Privacy Filter service spec")


# ===========================================================================
# Component 7 — RingController (Gate 3, BRC-D6)
# ===========================================================================


def _good_telemetry(out_of_band=True):
    return PromotionTelemetry(
        regression_count=0,
        anomaly_count=0,
        token_cost_delta=0.0,
        agent_reported_healthy=True,
        out_of_band_verified=out_of_band,
    )


class TestRingControllerExpectedPass:
    def test_assign_and_promote(self):
        rc = RingController()
        rc.assign("cand", Ring.RING_0_SYNTHETIC)
        assert rc.promote("cand", telemetry=_good_telemetry()) is Ring.RING_1_PILOT

    def test_promote_all_the_way(self):
        rc = RingController()
        rc.assign("cand")
        rc.promote("cand", telemetry=_good_telemetry())
        rc.promote("cand", telemetry=_good_telemetry())
        assert rc.promote("cand", telemetry=_good_telemetry()) is Ring.RING_3_FULL


class TestRingControllerAdversarial:
    def test_m3_forged_telemetry_rejected(self):
        """METASTASIS M3: an agent forges healthy telemetry but has no out-of-band
        verification → promotion rejected (BRC-D6)."""
        rc = RingController()
        rc.assign("cand")
        forged = PromotionTelemetry(
            regression_count=0,
            anomaly_count=0,
            token_cost_delta=0.0,
            agent_reported_healthy=True,   # agent says it's fine
            out_of_band_verified=False,    # but no independent verification
        )
        with pytest.raises(RingError, match="out-of-band"):
            rc.promote("cand", telemetry=forged)
        assert rc.audit.for_event(ControlPlaneEvent.RING_PROMOTION_REJECTED)
        assert rc.ring_of("cand") is Ring.RING_0_SYNTHETIC

    def test_regression_blocks_promotion(self):
        rc = RingController()
        rc.assign("cand")
        bad = PromotionTelemetry(
            regression_count=2, anomaly_count=0, token_cost_delta=0.0,
            agent_reported_healthy=True, out_of_band_verified=True,
        )
        with pytest.raises(RingError, match="criteria failed"):
            rc.promote("cand", telemetry=bad)

    def test_cannot_promote_past_ring_3(self):
        rc = RingController()
        rc.assign("cand", Ring.RING_3_FULL)
        with pytest.raises(RingError, match="already at Ring 3"):
            rc.promote("cand", telemetry=_good_telemetry())


class TestRingControllerKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Ring promotion thresholds are launch-conservative static values; "
            "real-tenant calibration is deferred (BRC-D6, contract §6 Class 3). "
            "Completion path: signed amendment after Ring 0 + Ring 1 baseline data."
        ),
        strict=True,
    )
    def test_xfail_real_tenant_threshold_calibration(self):
        raise AssertionError("not implemented — post-onboarding signed amendment")


# ===========================================================================
# Component 8 — GatewayController (spine, BRC-D8 / §3.6)
# ===========================================================================


def _build_gateway(mode_check=None):
    audit = ControlPlaneAuditTrail()
    identity = AgentIdentityGateway()
    rings = RingController(audit=audit)
    budgets = SessionBudgetStore(audit=audit)
    breakers = BreakerStore(now=FakeClock())
    loop = LoopDetector(now=FakeClock())
    seg = TenantSegmentationController()
    gw = GatewayController(
        identity=identity,
        rings=rings,
        budgets=budgets,
        breakers=breakers,
        loop_detector=loop,
        segmentation=seg,
        audit=audit,
        mode_check=mode_check or AllowAllModeCheck(),
    )
    # Seed a valid identity + session.
    identity.issue(token="tok", agent_id="agent_a", tenant_id="tenant_a", tool_scope={"scan"})
    budgets.open_session("s1", tier=RoleTier.DETECTION)
    return gw, audit, identity, breakers, seg


def _request(**overrides):
    base = dict(
        token="tok",
        claimed_agent_id="agent_a",
        tenant_id="tenant_a",
        tool="scan",
        session_id="s1",
        args={"x": 1},
    )
    base.update(overrides)
    return GatewayRequest(**base)


class TestGatewayExpectedPass:
    def test_full_lifecycle_dispatch(self):
        gw, audit, _id, _bs, _seg = _build_gateway()
        decision = gw.handle(_request())
        assert decision.dispatched is True
        assert decision.stage_reached == "dispatch"
        assert audit.for_event(ControlPlaneEvent.GATEWAY_DISPATCHED)


class TestGatewayAdversarial:
    def test_m5_cross_agent_token_rejected_at_gateway(self):
        """METASTASIS M5 (end-to-end): cross-agent token rejected at identity gate."""
        gw, _audit, _id, _bs, _seg = _build_gateway()
        with pytest.raises(GatewayRejected) as exc:
            gw.handle(_request(claimed_agent_id="agent_b"))
        assert exc.value.stage == "identity"

    def test_m2_forged_tenant_rejected_at_gateway(self):
        """METASTASIS M2 (end-to-end): forged tenant binding rejected at segmentation."""
        gw, _audit, identity, _bs, seg = _build_gateway()
        # Issue an identity scoped to tenant_a but register segment tenant_a,
        # then claim tenant_a with a wrong credential to force the forged-binding path.
        seg.register_tenant("tenant_a", credential="cred_a")
        with pytest.raises(GatewayRejected) as exc:
            gw.handle(_request(credential="WRONG_CRED"))
        assert exc.value.stage == "segmentation"

    def test_m4_unilateral_mode_trigger_cannot_bypass(self):
        """METASTASIS M4: a request has no path to flip the mode; a denying mode
        check (owned by the Mode Controller, not the agent) blocks dispatch. A
        single agent cannot unilaterally force a system-wide transition."""

        class DenyMode:
            def is_dispatch_allowed(self, tenant_id: str) -> bool:
                return False

        gw, _audit, _id, _bs, _seg = _build_gateway(mode_check=DenyMode())
        # The request object exposes no mode field — an agent cannot set mode.
        assert not hasattr(_request(), "mode")
        with pytest.raises(GatewayRejected) as exc:
            gw.handle(_request())
        assert exc.value.stage == "mode"

    def test_budget_exhausted_blocks_dispatch(self):
        gw, _audit, _id, _bs, _seg = _build_gateway()
        gw.budgets.charge("s1", tokens=999_999)  # exhaust
        with pytest.raises(GatewayRejected) as exc:
            gw.handle(_request())
        assert exc.value.stage == "budget"

    def test_open_breaker_blocks_dispatch(self):
        gw, _audit, _id, breakers, _seg = _build_gateway()
        breakers.trip(_key(), trip_class=TripClass.SUSTAINED)
        with pytest.raises(GatewayRejected) as exc:
            gw.handle(_request())
        assert exc.value.stage == "breaker"

    def test_loop_trips_breaker_and_rejects(self):
        gw, _audit, _id, _bs, _seg = _build_gateway()
        # Hammer identical calls past the identical-run threshold.
        with pytest.raises(GatewayRejected) as exc:
            for _ in range(5):
                gw.handle(_request(args={"same": "args"}))
        assert exc.value.stage == "breaker"

    def test_no_partial_dispatch_on_rejection(self):
        """BRC-D8: a rejected request never emits a GATEWAY_DISPATCHED record."""
        gw, audit, _id, _bs, _seg = _build_gateway()
        with pytest.raises(GatewayRejected):
            gw.handle(_request(claimed_agent_id="agent_b"))
        assert not audit.for_event(ControlPlaneEvent.GATEWAY_DISPATCHED)


class TestGatewayKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Gateway performs a mode CHECK only (BRC-D10); live Mode Controller "
            "quorum/epoch consensus is a separate signed contract. Completion "
            "path: Mode Controller contract signed and gated (contract §9 pre-cond 2)."
        ),
        strict=True,
    )
    def test_xfail_mode_controller_quorum_live(self):
        raise AssertionError("not implemented — Mode Controller contract")
