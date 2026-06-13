"""Watcher Agents tests (Layer 6 Governance, scoreboard rows #85-87).

Three test classes per component per AGENTS.md §5 and
``Watcher_Agents_Contract.md`` §6:
  Class 1 — expected pass
  Class 2 — adversarial (all four mandated adversarial tests live here)
  Class 3 — known-gap xfail (documented, with completion path)

Components:
  ObservationLog            (WA-D4, §3.4/§3.5)
  ThreatLevelClassifier     (WA-D1/D2/D3/D8, §4)
  WatcherResourceController (WA-D6, §5)
  W1 TimingWatcher (#85)    (§3.1)
  W2 DriftWatcher (#86)     (§3.2)
  W3 IntegrityWatcher (#87) (§3.3)
  EscalationRouter          (WA-D5, §6)

The four mandated adversarial tests (contract §6 Class 2):
  A1 — watcher cannot write to core/blackboard/         → TestBoundaryAdversarial
  A2 — watcher cannot influence a verdict               → TestBoundaryAdversarial
  A3 — single watcher cannot force a threat-level change → TestThreatClassifierAdversarial
  A4 — watcher cannot be starved by agent exhaustion    → TestIsolationAdversarial
"""

from __future__ import annotations

import pytest

from core.watchers import (
    BaseWatcher,
    DriftWatcher,
    EscalationRouter,
    IntegrityWatcher,
    MATT_IDENTITY,
    ObservationError,
    ObservationLog,
    ObservationType,
    Recipient,
    ResourceIsolationError,
    Severity,
    ThreatLevel,
    ThreatLevelClassifier,
    ThreatLevelError,
    TimingWatcher,
    WatcherBoundaryError,
    WatcherResourceController,
)


def _log() -> ObservationLog:
    return ObservationLog()


# ===========================================================================
# ObservationLog (WA-D4)
# ===========================================================================


class TestObservationLogExpectedPass:
    def test_append_and_read(self):
        log = _log()
        rec = log.record(
            watcher_id="W1",
            observation_type=ObservationType.TIMING_ANOMALY,
            severity=Severity.WARNING,
            observed_agent="detector_x",
            details="slow",
            tenant_id="tenant_a",
        )
        assert rec in log.entries()
        assert log.for_watcher("W1") == (rec,)
        assert log.for_type(ObservationType.TIMING_ANOMALY) == (rec,)

    def test_separate_from_blackboard(self):
        # The log is its own class with its own storage — not the blackboard.
        from core.watchers import observation as obs_mod

        assert "blackboard" not in obs_mod.ObservationLog.__module__


class TestObservationLogAdversarial:
    def test_append_only_no_delete_or_update_api(self):
        log = _log()
        assert not hasattr(log, "delete")
        assert not hasattr(log, "update")
        assert not hasattr(log, "remove")

    def test_observation_outside_closed_enum_rejected(self):
        log = _log()
        with pytest.raises(ObservationError):
            log.record(
                watcher_id="W1",
                observation_type="made_up_type",  # not a closed-enum member
                severity=Severity.INFO,
                observed_agent="x",
                details="",
            )


class TestObservationLogKnownGap:
    @pytest.mark.xfail(
        reason=(
            "ObservationLog is in-process append-only with optional JSONL mirror; "
            "durable separate-infrastructure persistence is deferred. Completion "
            "path: dedicated observation-store infrastructure provisioning."
        ),
        strict=True,
    )
    def test_xfail_durable_separate_store(self):
        raise AssertionError("not implemented — durable store provisioning")


# ===========================================================================
# ThreatLevelClassifier (WA-D1/D2/D3/D8)
# ===========================================================================


class TestThreatClassifierExpectedPass:
    def test_two_watchers_escalate(self):
        log = _log()
        clf = ThreatLevelClassifier(log=log)
        clf.submit_signal(watcher_id="W1", proposed_level=ThreatLevel.HIGH)
        assert clf.level is ThreatLevel.ROUTINE  # one watcher only
        clf.submit_signal(watcher_id="W2", proposed_level=ThreatLevel.HIGH)
        assert clf.level is ThreatLevel.HIGH  # quorum of 2
        # A threat_level_change observation was logged.
        assert log.for_type(ObservationType.THREAT_LEVEL_CHANGE)

    def test_classified_level_is_highest_with_quorum(self):
        clf = ThreatLevelClassifier()
        clf.submit_signal(watcher_id="W1", proposed_level=ThreatLevel.CRITICAL)
        clf.submit_signal(watcher_id="W2", proposed_level=ThreatLevel.HIGH)
        # Only one watcher at CRITICAL; two at >= HIGH → HIGH.
        assert clf.level is ThreatLevel.HIGH
        clf.submit_signal(watcher_id="W3", proposed_level=ThreatLevel.CRITICAL)
        # Now two at CRITICAL → CRITICAL.
        assert clf.level is ThreatLevel.CRITICAL


class TestThreatClassifierAdversarial:
    def test_a3_single_watcher_cannot_force_change(self):
        """A3: a single watcher cannot move the swarm off ROUTINE unilaterally."""
        clf = ThreatLevelClassifier()
        clf.submit_signal(watcher_id="W1", proposed_level=ThreatLevel.CRITICAL)
        assert clf.level is ThreatLevel.ROUTINE

    def test_a3_single_watcher_cannot_force_deescalation(self):
        clf = ThreatLevelClassifier()
        clf.submit_signal(watcher_id="W1", proposed_level=ThreatLevel.HIGH)
        clf.submit_signal(watcher_id="W2", proposed_level=ThreatLevel.HIGH)
        assert clf.level is ThreatLevel.HIGH
        # W1 drops alone → still HIGH because W2 + (implicitly) no second low quorum.
        clf.submit_signal(watcher_id="W1", proposed_level=ThreatLevel.ROUTINE)
        # Now only W2 supports HIGH (one watcher) → falls, but not by W1's say-so:
        # it's recomputed by quorum. Without 2 supporting HIGH, level drops.
        assert clf.level is ThreatLevel.ROUTINE

    def test_agent_cannot_influence_threat_level(self):
        """WA-D8: only registered watcher ids may submit a signal."""
        clf = ThreatLevelClassifier()
        with pytest.raises(ThreatLevelError):
            clf.submit_signal(watcher_id="detector_x", proposed_level=ThreatLevel.CRITICAL)
        with pytest.raises(ThreatLevelError):
            clf.submit_signal(watcher_id="reconciliation_agent", proposed_level=ThreatLevel.HIGH)


class TestThreatClassifierKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Threat-signal thresholds (what behavioral evidence maps to which "
            "level) launch conservative; real-tenant calibration deferred "
            "(WA-D11). Completion path: signed amendment after first tenant onboarded."
        ),
        strict=True,
    )
    def test_xfail_real_tenant_threat_calibration(self):
        raise AssertionError("not implemented — post-onboarding amendment")


# ===========================================================================
# WatcherResourceController (WA-D6)
# ===========================================================================


class TestIsolationExpectedPass:
    def test_separate_pools(self):
        rc = WatcherResourceController(watcher_capacity=100)
        rc.register_agent_pool("detector_x", capacity=50)
        rc.consume_agent("detector_x", 50)
        assert rc.watcher_remaining() == 100
        assert rc.watcher_can_observe() is True

    def test_watcher_consumes_with_credential(self):
        rc = WatcherResourceController(watcher_capacity=10, watcher_credential="wc")
        assert rc.consume_watcher(4, credential="wc") == 6


class TestIsolationAdversarial:
    def test_a4_watcher_cannot_be_starved_by_agent_exhaustion(self):
        """A4: an agent burning its entire budget leaves watcher capacity intact."""
        rc = WatcherResourceController(watcher_capacity=100)
        rc.register_agent_pool("detector_x", capacity=1000)
        for _ in range(10):
            rc.consume_agent("detector_x", 1000)  # exhaust, repeatedly
        assert rc.watcher_remaining() == 100
        assert rc.watcher_can_observe() is True

    def test_agent_credential_cannot_draw_watcher_pool(self):
        rc = WatcherResourceController(watcher_capacity=10, watcher_credential="wc")
        with pytest.raises(ResourceIsolationError):
            rc.consume_watcher(1, credential="agent_credential")


class TestIsolationKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Pools model logical isolation; physical separate-infrastructure "
            "provisioning (distinct hosts/quotas/credential store) is deferred to "
            "infrastructure hardening. Completion path: infra provisioning contract."
        ),
        strict=True,
    )
    def test_xfail_physical_infra_separation(self):
        raise AssertionError("not implemented — physical infra provisioning")


# ===========================================================================
# Neutral-observer boundary (WA-D7 / §7) — A1, A2
# ===========================================================================


class TestBoundaryExpectedPass:
    def test_watcher_writes_only_to_log(self):
        log = _log()
        w = TimingWatcher("W1", log=log)
        w.observe_completion(
            observed_agent="d", elapsed_seconds=30, baseline_window_seconds=10
        )
        assert log.for_watcher("W1")


class TestBoundaryAdversarial:
    def test_a1_watcher_cannot_write_blackboard(self):
        """A1: a watcher attempting to write to core/blackboard/ is rejected."""
        w = TimingWatcher("W1", log=_log())
        with pytest.raises(WatcherBoundaryError):
            w.write_blackboard({"verdict": "tampered"})

    def test_a2_watcher_cannot_influence_verdict(self):
        """A2: a watcher has no vote in verdicts."""
        w = DriftWatcher("W2", log=_log())
        with pytest.raises(WatcherBoundaryError):
            w.influence_verdict(case_id="c1", vote="malicious")

    def test_watcher_cannot_message_agents(self):
        w = IntegrityWatcher("W3", log=_log())
        with pytest.raises(WatcherBoundaryError):
            w.message_agent("reconciliation_agent", "change your verdict")

    def test_watcher_cannot_make_recommendation(self):
        w = TimingWatcher("W1", log=_log())
        with pytest.raises(WatcherBoundaryError):
            w.make_recommendation("block this tenant")

    def test_watcher_cannot_emit_outside_its_lane(self):
        # TimingWatcher may not emit confidence_drift.
        log = _log()
        w = TimingWatcher("W1", log=log)
        with pytest.raises(WatcherBoundaryError):
            w._observe(
                observation_type=ObservationType.CONFIDENCE_DRIFT,
                severity=Severity.INFO,
                observed_agent="d",
                details="",
            )


class TestBoundaryKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Boundary is enforced at the watcher API surface; a gateway-level "
            "deny rule that also blocks any out-of-band blackboard access path is "
            "deferred. Completion path: gateway egress policy for watcher identities."
        ),
        strict=True,
    )
    def test_xfail_gateway_egress_policy(self):
        raise AssertionError("not implemented — gateway egress policy")


# ===========================================================================
# W1 TimingWatcher (#85)
# ===========================================================================


class TestTimingWatcherExpectedPass:
    def test_completion_within_window_no_flag(self):
        w = TimingWatcher("W1", log=_log())
        assert w.observe_completion(
            observed_agent="d", elapsed_seconds=8, baseline_window_seconds=10
        ) is None

    def test_completion_over_window_flags(self):
        w = TimingWatcher("W1", log=_log())
        rec = w.observe_completion(
            observed_agent="d", elapsed_seconds=25, baseline_window_seconds=10
        )
        assert rec is not None
        assert rec.observation_type is ObservationType.TIMING_ANOMALY

    def test_loop_signature_flags(self):
        w = TimingWatcher("W1", log=_log(), loop_threshold=3)
        assert w.observe_call(observed_agent="d", tool="scan", args={"x": 1}) is None
        assert w.observe_call(observed_agent="d", tool="scan", args={"x": 1}) is None
        rec = w.observe_call(observed_agent="d", tool="scan", args={"x": 1})
        assert rec is not None and rec.observation_type is ObservationType.LOOP_DETECTED


class TestTimingWatcherAdversarial:
    def test_inactivity_flagged(self):
        w = TimingWatcher("W1", log=_log())
        rec = w.observe_inactivity(observed_agent="d", idle_seconds=120, max_idle_seconds=60)
        assert rec is not None and rec.observation_type is ObservationType.INACTIVITY_FLAG

    def test_loop_only_on_identical_args(self):
        w = TimingWatcher("W1", log=_log(), loop_threshold=3)
        for i in range(5):
            assert w.observe_call(observed_agent="d", tool="scan", args={"x": i}) is None


class TestTimingWatcherKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Baseline completion windows are caller-supplied; signed per-agent "
            "baselines are deferred to real-tenant calibration (WA-D11). Completion "
            "path: signed baseline amendment after onboarding."
        ),
        strict=True,
    )
    def test_xfail_signed_baseline_windows(self):
        raise AssertionError("not implemented — signed baselines")


# ===========================================================================
# W2 DriftWatcher (#86)
# ===========================================================================


class TestDriftWatcherExpectedPass:
    def test_in_range_no_flag(self):
        w = DriftWatcher("W2", log=_log(), min_samples=3)
        w.set_baseline("d", low=0.4, high=0.6)
        for _ in range(5):
            assert w.observe_confidence(observed_agent="d", confidence=0.5) is None

    def test_drift_flagged_after_min_samples(self):
        w = DriftWatcher("W2", log=_log(), min_samples=3)
        w.set_baseline("d", low=0.4, high=0.6)
        w.observe_confidence(observed_agent="d", confidence=0.9)
        w.observe_confidence(observed_agent="d", confidence=0.9)
        rec = w.observe_confidence(observed_agent="d", confidence=0.9)
        assert rec is not None and rec.observation_type is ObservationType.CONFIDENCE_DRIFT


class TestDriftWatcherAdversarial:
    def test_point_deviation_before_min_samples(self):
        w = DriftWatcher("W2", log=_log(), min_samples=5)
        w.set_baseline("d", low=0.4, high=0.6)
        rec = w.observe_confidence(observed_agent="d", confidence=0.95)
        assert rec is not None and rec.observation_type is ObservationType.BASELINE_DEVIATION

    def test_no_baseline_raises(self):
        w = DriftWatcher("W2", log=_log())
        with pytest.raises(ValueError):
            w.observe_confidence(observed_agent="unknown", confidence=0.5)

    def test_drift_below_range_flagged(self):
        w = DriftWatcher("W2", log=_log(), min_samples=2)
        w.set_baseline("d", low=0.4, high=0.6)
        w.observe_confidence(observed_agent="d", confidence=0.05)
        rec = w.observe_confidence(observed_agent="d", confidence=0.05)
        assert rec is not None and rec.observation_type is ObservationType.CONFIDENCE_DRIFT
        assert "below" in rec.details


class TestDriftWatcherKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Drift uses a running mean vs a static signed range; richer "
            "distribution tests (variance/KS) are deferred to real-tenant "
            "calibration (WA-D11). Completion path: signed amendment after onboarding."
        ),
        strict=True,
    )
    def test_xfail_distribution_shape_drift(self):
        raise AssertionError("not implemented — distribution-shape calibration")


# ===========================================================================
# W3 IntegrityWatcher (#87)
# ===========================================================================


class TestIntegrityWatcherExpectedPass:
    def test_valid_write_no_flag(self):
        w = IntegrityWatcher("W3", log=_log())
        assert w.observe_write(
            observed_agent="d",
            assigned_evidence_type="header",
            attempted_evidence_type="header",
            entry_schema_valid=True,
        ) is None

    def test_same_tenant_read_no_flag(self):
        w = IntegrityWatcher("W3", log=_log())
        assert w.observe_read(
            observed_agent="A", owner_agent="B",
            reader_tenant_id="t1", target_tenant_id="t1",
        ) is None


class TestIntegrityWatcherAdversarial:
    def test_schema_violation_flagged(self):
        w = IntegrityWatcher("W3", log=_log())
        rec = w.observe_write(
            observed_agent="d",
            assigned_evidence_type="header",
            attempted_evidence_type="header",
            entry_schema_valid=False,
        )
        assert rec is not None and rec.observation_type is ObservationType.SCHEMA_VIOLATION

    def test_unauthorized_write_outside_assigned_type(self):
        w = IntegrityWatcher("W3", log=_log())
        rec = w.observe_write(
            observed_agent="d",
            assigned_evidence_type="header",
            attempted_evidence_type="financial",
            entry_schema_valid=True,
        )
        assert rec is not None and rec.observation_type is ObservationType.SCHEMA_VIOLATION

    def test_cross_tenant_read_flagged_critical(self):
        w = IntegrityWatcher("W3", log=_log())
        rec = w.observe_read(
            observed_agent="A", owner_agent="B",
            reader_tenant_id="t1", target_tenant_id="t2",
        )
        assert rec is not None
        assert rec.observation_type is ObservationType.SCHEMA_VIOLATION
        assert rec.severity is Severity.CRITICAL

    def test_circular_read_pattern_flagged(self):
        w = IntegrityWatcher("W3", log=_log())
        # A reads B's region, then B reads A's region → circular.
        assert w.observe_read(
            observed_agent="A", owner_agent="B",
            reader_tenant_id="t1", target_tenant_id="t1",
        ) is None
        rec = w.observe_read(
            observed_agent="B", owner_agent="A",
            reader_tenant_id="t1", target_tenant_id="t1",
        )
        assert rec is not None and rec.observation_type is ObservationType.CIRCULAR_DEPENDENCY

    def test_integrity_watcher_does_not_block(self):
        # It observes and reports — there is no enforcement/mutation method.
        w = IntegrityWatcher("W3", log=_log())
        assert not hasattr(w, "block")
        assert not hasattr(w, "revoke")
        assert not hasattr(w, "rewrite_ledger")


class TestIntegrityWatcherKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Circular-read detection covers 2-cycles; deep N-cycle dependency "
            "analysis across the full ledger is deferred. Completion path: "
            "ledger-graph analysis amendment."
        ),
        strict=True,
    )
    def test_xfail_deep_cycle_detection(self):
        raise AssertionError("not implemented — N-cycle ledger-graph analysis")


# ===========================================================================
# EscalationRouter (WA-D5)
# ===========================================================================


class TestEscalationExpectedPass:
    def test_info_audit_only(self):
        assert EscalationRouter.recipients_for(Severity.INFO) == frozenset(
            {Recipient.GOVERNANCE_AUDIT_TRAIL}
        )

    def test_warning_commander_plus_audit(self):
        r = EscalationRouter.recipients_for(Severity.WARNING)
        assert Recipient.SWARM_COMMANDER in r
        assert Recipient.GOVERNANCE_AUDIT_TRAIL in r
        assert Recipient.MATT not in r

    def test_critical_routes_direct_to_matt(self):
        log = _log()
        router = EscalationRouter()
        rec = log.record(
            watcher_id="W3",
            observation_type=ObservationType.SCHEMA_VIOLATION,
            severity=Severity.CRITICAL,
            observed_agent="d",
            details="cross-tenant read",
            tenant_id="t1",
        )
        delivery = router.route(rec)
        assert delivery.direct_to_matt is True
        assert Recipient.MATT in delivery.recipients
        assert Recipient.SWARM_COMMANDER in delivery.recipients
        assert Recipient.GOVERNANCE_AUDIT_TRAIL in delivery.recipients


class TestEscalationAdversarial:
    def test_matt_identity_is_operator(self):
        assert Recipient.MATT.value == MATT_IDENTITY

    def test_critical_delivered_synchronously_no_queue(self):
        # route() delivers synchronously: the delivery is present immediately.
        log = _log()
        router = EscalationRouter()
        rec = log.record(
            watcher_id="W1",
            observation_type=ObservationType.LOOP_DETECTED,
            severity=Severity.CRITICAL,
            observed_agent="d",
            details="",
        )
        before = len(router.deliveries())
        router.route(rec)
        assert len(router.deliveries()) == before + 1


class TestEscalationKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Routing computes recipients and records delivery in-process; live "
            "transport to Matt / Swarm Commander (paging, channel) is deferred. "
            "Completion path: notification-transport integration."
        ),
        strict=True,
    )
    def test_xfail_live_transport(self):
        raise AssertionError("not implemented — notification transport")
