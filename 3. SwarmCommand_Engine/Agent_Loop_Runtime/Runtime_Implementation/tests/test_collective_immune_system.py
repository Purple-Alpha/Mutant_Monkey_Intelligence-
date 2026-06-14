"""Collective Immune System tests (Layer 6 Control Plane, scoreboard row #95).

Governing contract
------------------
``4. Product_Roadmap/Collective_Immune_System_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol).

Three test classes per AGENTS.md §5 / contract testable invariants:
  Class 1 — expected pass
  Class 2 — adversarial / scope-boundary tests
  Class 3 — known-gap xfail with completion path
"""

from __future__ import annotations

import dataclasses

import pytest

from core.collective_immune_system import (
    CISAction,
    CISComponent,
    CISLogError,
    CISRecordKind,
    CollectiveImmuneSystemCoordinator,
    CollectiveImmuneSystemLog,
    EscalationLevel,
    EscalationRejected,
    EscalationRequest,
    EvidenceHandoff,
    ForbiddenActionRejected,
    ForbiddenCISAction,
    HandoffRejected,
    SafeStopBoundaryError,
)


def _coordinator(log: CollectiveImmuneSystemLog | None = None):
    log = log or CollectiveImmuneSystemLog()
    return CollectiveImmuneSystemCoordinator(log=log), log


def _request(
    level: EscalationLevel,
    *,
    workflow_id: str = "wf-1",
    tenants: tuple[str, ...] = ("tenant-a",),
    components: tuple[CISComponent, ...] = (
        CISComponent.WATCHER_AGENT,
        CISComponent.PRIVACY_FILTER,
    ),
    trigger: str = "test escalation",
) -> EscalationRequest:
    return EscalationRequest(
        workflow_id=workflow_id,
        level=level,
        trigger=trigger,
        tenant_scope=tenants,
        evidence_refs=("obs-1", "privacy-1"),
        components_detected=components,
        brc_lifecycle_verified=True,
    )


# ---------------------------------------------------------------------------
# Class 1 — expected pass
# ---------------------------------------------------------------------------


def test_l1_local_anomaly_logs_only_local_action():
    cis, log = _coordinator()
    plan = cis.coordinate(
        _request(
            EscalationLevel.L1_LOCAL_ANOMALY,
            components=(CISComponent.WATCHER_AGENT,),
            tenants=("tenant-a",),
        )
    )

    assert plan.actions == (CISAction.LOG_LOCAL_ANOMALY,)
    assert plan.notify == ()
    assert [r.kind for r in log.entries()] == [CISRecordKind.LEVEL_TRANSITION]


def test_l2_tenant_scoped_threat_routes_evidence_without_cross_tenant_action():
    cis, log = _coordinator()
    plan = cis.coordinate(_request(EscalationLevel.L2_TENANT_SCOPED_THREAT))

    assert CISAction.ROUTE_EVIDENCE_TO_RECONCILIATION in plan.actions
    assert CISAction.HOLD_CROSS_TENANT_BROADCASTS in plan.actions
    assert plan.tenant_scope == ("tenant-a",)
    assert CISAction.SUSPEND_MUTATION_ENGINE not in plan.actions
    assert [r.kind for r in log.entries()][:2] == [
        CISRecordKind.LEVEL_TRANSITION,
        CISRecordKind.COMPONENT_NOTIFICATION,
    ]


def test_l2_allows_reconciliation_named_conflict_for_single_tenant():
    cis, _ = _coordinator()
    plan = cis.coordinate(
        EscalationRequest(
            workflow_id="wf-recon-conflict",
            level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
            trigger="ReconciliationAgent named conflict",
            tenant_scope=("tenant-a",),
            evidence_refs=("conflict-1",),
            components_detected=(CISComponent.RECONCILIATION_AGENT,),
            brc_lifecycle_verified=True,
            reconciliation_named_conflict=True,
        )
    )

    assert CISAction.ROUTE_EVIDENCE_TO_RECONCILIATION in plan.actions


def test_l2_rejects_named_conflict_flag_without_reconciliation_agent_source():
    cis, _ = _coordinator()
    with pytest.raises(EscalationRejected, match="ReconciliationAgent named conflict"):
        cis.coordinate(
            EscalationRequest(
                workflow_id="wf-forged-conflict",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                trigger="forged named conflict flag",
                tenant_scope=("tenant-a",),
                evidence_refs=("obs-1",),
                components_detected=(CISComponent.WATCHER_AGENT,),
                brc_lifecycle_verified=True,
                reconciliation_named_conflict=True,
            )
        )


def test_l3_systemic_threat_suspends_mutation_and_only_acknowledges_watcher_fission():
    cis, log = _coordinator()
    plan = cis.coordinate(
        _request(
            EscalationLevel.L3_SYSTEMIC_THREAT,
            tenants=("tenant-a", "tenant-b"),
            trigger="cross-tenant correlated signals",
        )
    )

    assert CISAction.SUSPEND_MUTATION_ENGINE in plan.actions
    assert CISAction.ACKNOWLEDGE_WATCHER_TRIGGERED_FISSION not in plan.actions
    assert log.for_kind(CISRecordKind.MUTATION_SUSPENDED)


def test_l3_acknowledges_fission_only_when_watcher_trigger_is_present():
    cis, _ = _coordinator()
    plan = cis.coordinate(
        EscalationRequest(
            workflow_id="wf-3",
            level=EscalationLevel.L3_SYSTEMIC_THREAT,
            trigger="watcher escalation independently triggered fission",
            tenant_scope=("tenant-a", "tenant-b"),
            evidence_refs=("obs-critical",),
            components_detected=(CISComponent.WATCHER_AGENT,),
            brc_lifecycle_verified=True,
            watcher_fission_triggered=True,
        )
    )

    assert CISAction.ACKNOWLEDGE_WATCHER_TRIGGERED_FISSION in plan.actions


def test_l3_does_not_acknowledge_fission_without_watcher_source():
    cis, _ = _coordinator()
    plan = cis.coordinate(
        EscalationRequest(
            workflow_id="wf-fission-forged",
            level=EscalationLevel.L3_SYSTEMIC_THREAT,
            trigger="control-plane risk with forged watcher fission flag",
            tenant_scope=("tenant-a",),
            evidence_refs=("brc-risk",),
            components_detected=(CISComponent.BLAST_RADIUS_CONTROLLER,),
            brc_lifecycle_verified=True,
            control_plane_integrity_risk=True,
            watcher_fission_triggered=True,
        )
    )

    assert CISAction.ACKNOWLEDGE_WATCHER_TRIGGERED_FISSION not in plan.actions


def test_l3_allows_control_plane_integrity_risk_for_single_tenant():
    cis, _ = _coordinator()
    plan = cis.coordinate(
        EscalationRequest(
            workflow_id="wf-cp-risk",
            level=EscalationLevel.L3_SYSTEMIC_THREAT,
            trigger="BRC lifecycle violation",
            tenant_scope=("tenant-a",),
            evidence_refs=("brc-violation",),
            components_detected=(CISComponent.BLAST_RADIUS_CONTROLLER,),
            brc_lifecycle_verified=True,
            control_plane_integrity_risk=True,
        )
    )

    assert CISAction.SUSPEND_MUTATION_ENGINE in plan.actions


def test_authorized_handoff_is_logged_before_returning_handoff():
    cis, log = _coordinator()
    payload = {"signal_hash": "h:abc123"}
    handoff = EvidenceHandoff(
        workflow_id="wf-handoff",
        level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
        source=CISComponent.WATCHER_AGENT,
        target=CISComponent.RECONCILIATION_AGENT,
        tenant_scope=("tenant-a",),
        evidence_ref="obs-critical-1",
        payload=payload,
        brc_lifecycle_verified=True,
    )
    payload["tenant-a"] = "raw after construction"

    returned = cis.handoff(handoff)

    assert returned is handoff
    assert "tenant-a" not in returned.payload
    with pytest.raises(TypeError):
        returned.payload["tenant-a"] = "raw after validation"  # type: ignore[index]
    assert log.entries()[-1].kind is CISRecordKind.HANDOFF
    assert log.entries()[-1].source is CISComponent.WATCHER_AGENT
    assert log.entries()[-1].target is CISComponent.RECONCILIATION_AGENT


def test_l4_hands_off_to_safe_stop_and_authority_ends():
    cis, log = _coordinator()
    plan = cis.coordinate(
        EscalationRequest(
            workflow_id="wf-safe-stop-entry",
            level=EscalationLevel.L4_SAFE_STOP_CONDITION,
            trigger="SS-4D dispatch containment failure",
            tenant_scope=("tenant-a",),
            evidence_refs=("ss-4d",),
            brc_lifecycle_verified=True,
            safe_stop_condition="SS-4",
        )
    )

    assert plan.actions == (
        CISAction.HAND_OFF_TO_SAFE_STOP,
        CISAction.SUSPEND_MUTATION_ENGINE,
    )
    assert log.for_kind(CISRecordKind.SAFE_STOP_HANDOFF)
    before = len(log.entries())
    with pytest.raises(SafeStopBoundaryError):
        cis.coordinate(_request(EscalationLevel.L2_TENANT_SCOPED_THREAT, workflow_id="wf-after"))
    assert len(log.entries()) == before


# ---------------------------------------------------------------------------
# Class 2 — adversarial / scope-boundary tests
# ---------------------------------------------------------------------------


def test_cis_inv_1_rejects_mode_write_and_epoch_increment_attempts():
    cis, log = _coordinator()

    with pytest.raises(ForbiddenActionRejected):
        cis.reject_forbidden_action(ForbiddenCISAction.WRITE_MODE_STATE, workflow_id="wf-mode")
    with pytest.raises(ForbiddenActionRejected):
        cis.reject_forbidden_action(ForbiddenCISAction.INCREMENT_EPOCH, workflow_id="wf-epoch")

    blocked = log.for_kind(CISRecordKind.ACTION_BLOCKED)
    assert {b.evidence_refs[0] for b in blocked} == {
        ForbiddenCISAction.WRITE_MODE_STATE.value,
        ForbiddenCISAction.INCREMENT_EPOCH.value,
    }
    assert not hasattr(cis, "request_transition")
    assert not hasattr(cis, "broadcast_recovery")


def test_cis_inv_2_never_produces_verdict_or_enforcement_decision():
    cis, _ = _coordinator()
    plan = cis.coordinate(
        _request(EscalationLevel.L3_SYSTEMIC_THREAT, tenants=("tenant-a", "tenant-b"))
    )

    assert not hasattr(cis, "produce_verdict")
    assert not hasattr(cis, "enforce_verdict")
    assert all(action is not ForbiddenCISAction.PRODUCE_VERDICT for action in plan.actions)


def test_cis_inv_3_rejects_fission_initiation():
    cis, _ = _coordinator()
    with pytest.raises(ForbiddenActionRejected):
        cis.reject_forbidden_action(ForbiddenCISAction.INITIATE_FISSION, workflow_id="wf-fission")
    assert not hasattr(cis, "initiate_fission")


def test_cis_inv_4_blocks_raw_tenant_identifier_in_handoff_payload():
    cis, log = _coordinator()
    with pytest.raises(HandoffRejected, match="raw tenant identifiers"):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-raw",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                source=CISComponent.WATCHER_AGENT,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=("tenant-a",),
                evidence_ref="obs-raw",
                payload={"raw": "tenant-a appeared in payload"},
                brc_lifecycle_verified=True,
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.HANDOFF_BLOCKED


def test_cis_inv_4_blocks_raw_tenant_identifier_in_payload_key():
    cis, log = _coordinator()
    with pytest.raises(HandoffRejected, match="raw tenant identifiers"):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-raw-key",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                source=CISComponent.WATCHER_AGENT,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=("tenant-a",),
                evidence_ref="obs-raw-key",
                payload={"tenant-a": "h:abc123"},
                brc_lifecycle_verified=True,
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.HANDOFF_BLOCKED


def test_cis_inv_5_rejects_missing_brc_lifecycle_verification():
    cis, log = _coordinator()
    with pytest.raises(ForbiddenActionRejected, match="BRC lifecycle"):
        cis.coordinate(
            EscalationRequest(
                workflow_id="wf-brc",
                level=EscalationLevel.L3_SYSTEMIC_THREAT,
                trigger="systemic threat",
                tenant_scope=("tenant-a", "tenant-b"),
                brc_lifecycle_verified=False,
            )
        )

    assert log.entries()[-1].evidence_refs == (ForbiddenCISAction.BYPASS_BRC_LIFECYCLE.value,)


def test_cis_inv_5_omitted_brc_lifecycle_proof_fails_closed():
    cis, log = _coordinator()
    with pytest.raises(ForbiddenActionRejected, match="BRC lifecycle"):
        cis.coordinate(
            EscalationRequest(
                workflow_id="wf-brc-default",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                trigger="tenant scoped threat",
                tenant_scope=("tenant-a",),
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.ACTION_BLOCKED


def test_cis_inv_6_log_write_failure_aborts_handoff():
    log = CollectiveImmuneSystemLog(failing=True)
    cis = CollectiveImmuneSystemCoordinator(log=log)

    with pytest.raises(CISLogError):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-log-fail",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                source=CISComponent.WATCHER_AGENT,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=("tenant-a",),
                evidence_ref="obs-1",
                brc_lifecycle_verified=True,
            )
        )
    assert log.entries() == ()


def test_cis_inv_6_durable_jsonl_failure_leaves_no_false_memory_record(tmp_path):
    bad_jsonl_path = tmp_path / "directory-not-file"
    bad_jsonl_path.mkdir()
    log = CollectiveImmuneSystemLog(jsonl_path=bad_jsonl_path)

    with pytest.raises(IsADirectoryError):
        log.record(
            kind=CISRecordKind.HANDOFF,
            detail="will fail before in-memory append",
            level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
            workflow_id="wf-durable-fail",
            source=CISComponent.WATCHER_AGENT,
            target=CISComponent.RECONCILIATION_AGENT,
            tenant_scope=("tenant-a",),
            evidence_refs=("obs-1",),
        )

    assert log.entries() == ()


def test_cis_inv_8_l2_rejects_multi_tenant_scope():
    cis, _ = _coordinator()
    with pytest.raises(EscalationRejected, match="exactly one tenant"):
        cis.coordinate(
            _request(
                EscalationLevel.L2_TENANT_SCOPED_THREAT,
                tenants=("tenant-a", "tenant-b"),
            )
        )


def test_cis_inv_8_l2_rejects_single_component_without_reconciliation_conflict():
    cis, _ = _coordinator()
    with pytest.raises(EscalationRejected, match="two correlated components"):
        cis.coordinate(
            _request(
                EscalationLevel.L2_TENANT_SCOPED_THREAT,
                components=(CISComponent.WATCHER_AGENT,),
            )
        )


def test_cis_inv_9_mutation_authorization_rejected_even_at_l3():
    cis, log = _coordinator()
    cis.coordinate(
        _request(EscalationLevel.L3_SYSTEMIC_THREAT, tenants=("tenant-a", "tenant-b"))
    )
    with pytest.raises(ForbiddenActionRejected):
        cis.reject_forbidden_action(
            ForbiddenCISAction.AUTHORIZE_MUTATION,
            workflow_id="wf-mutation",
            level=EscalationLevel.L3_SYSTEMIC_THREAT,
        )

    assert log.for_kind(CISRecordKind.MUTATION_SUSPENDED)
    assert log.for_kind(CISRecordKind.ACTION_BLOCKED)[-1].evidence_refs == (
        ForbiddenCISAction.AUTHORIZE_MUTATION.value,
    )


def test_cis_inv_9_l3_rejects_non_systemic_single_tenant_request():
    cis, _ = _coordinator()
    with pytest.raises(EscalationRejected, match="L3 requires"):
        cis.coordinate(
            EscalationRequest(
                workflow_id="wf-l3-bad",
                level=EscalationLevel.L3_SYSTEMIC_THREAT,
                trigger="single tenant local anomaly",
                tenant_scope=("tenant-a",),
                evidence_refs=("obs-local",),
                components_detected=(CISComponent.WATCHER_AGENT,),
                brc_lifecycle_verified=True,
            )
        )


def test_cis_inv_10_blocks_unlisted_handoff_path():
    cis, log = _coordinator()
    with pytest.raises(HandoffRejected, match="not authorized"):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-bad-path",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                source=CISComponent.PRIVACY_FILTER,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=("tenant-a",),
                evidence_ref="privacy-1",
                brc_lifecycle_verified=True,
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.HANDOFF_BLOCKED


def test_cis_inv_10_blocks_unscoped_handoff_even_on_authorized_path():
    cis, log = _coordinator()
    with pytest.raises(HandoffRejected, match="tenant scope"):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-unscoped",
                level=EscalationLevel.L2_TENANT_SCOPED_THREAT,
                source=CISComponent.WATCHER_AGENT,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=(),
                evidence_ref="obs-unscoped",
                brc_lifecycle_verified=True,
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.HANDOFF_BLOCKED


def test_cis_inv_10_blocks_authorized_endpoint_pair_at_wrong_level():
    cis, log = _coordinator()
    with pytest.raises(HandoffRejected, match="not authorized"):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-wrong-level",
                level=EscalationLevel.L1_LOCAL_ANOMALY,
                source=CISComponent.WATCHER_AGENT,
                target=CISComponent.RECONCILIATION_AGENT,
                tenant_scope=("tenant-a",),
                evidence_ref="obs-l1",
                brc_lifecycle_verified=True,
            )
        )

    assert log.entries()[-1].kind is CISRecordKind.HANDOFF_BLOCKED


def test_cis_inv_11_transition_notification_logged_after_transition_record():
    cis, log = _coordinator()
    cis.coordinate(
        _request(EscalationLevel.L3_SYSTEMIC_THREAT, tenants=("tenant-a", "tenant-b"))
    )

    kinds = [r.kind for r in log.entries()]
    assert kinds.index(CISRecordKind.LEVEL_TRANSITION) < kinds.index(
        CISRecordKind.COMPONENT_NOTIFICATION
    )


def test_cis_inv_12_no_resolution_or_recovery_surface_inside_safe_stop():
    cis, log = _coordinator()
    cis.coordinate(
        EscalationRequest(
            workflow_id="wf-safe-stop",
            level=EscalationLevel.L4_SAFE_STOP_CONDITION,
            trigger="SS-5 unresolvable conflict",
            tenant_scope=("tenant-a",),
            evidence_refs=("ss-5",),
            brc_lifecycle_verified=True,
            safe_stop_condition="SS-5",
        )
    )

    assert not hasattr(cis, "resolve_safe_stop")
    assert not hasattr(cis, "recover_from_safe_stop")
    before = len(log.entries())
    with pytest.raises(SafeStopBoundaryError):
        cis.handoff(
            EvidenceHandoff(
                workflow_id="wf-safe-stop",
                level=EscalationLevel.L4_SAFE_STOP_CONDITION,
                source=CISComponent.SAFE_STOP_STATE_MACHINE,
                target=CISComponent.CIS_COORDINATOR,
                tenant_scope=("tenant-a",),
                evidence_ref="safe-stop-entry",
                brc_lifecycle_verified=True,
            )
        )
    assert len(log.entries()) == before


def test_cis_inv_12_forbidden_action_hook_does_not_log_inside_safe_stop():
    cis, log = _coordinator()
    cis.coordinate(
        EscalationRequest(
            workflow_id="wf-safe-stop-hook",
            level=EscalationLevel.L4_SAFE_STOP_CONDITION,
            trigger="SS-1 quorum loss",
            tenant_scope=("tenant-a",),
            evidence_refs=("ss-1",),
            brc_lifecycle_verified=True,
            safe_stop_condition="SS-1",
        )
    )
    before = len(log.entries())

    with pytest.raises(SafeStopBoundaryError):
        cis.reject_forbidden_action(
            ForbiddenCISAction.WRITE_MODE_STATE,
            workflow_id="wf-after-safe-stop",
        )

    assert len(log.entries()) == before


def test_cis_inv_12_l4_rejects_request_without_ss_condition():
    cis, _ = _coordinator()
    with pytest.raises(EscalationRejected, match="SS-1 through SS-5"):
        cis.coordinate(
            EscalationRequest(
                workflow_id="wf-l4-bad",
                level=EscalationLevel.L4_SAFE_STOP_CONDITION,
                trigger="operator typo, no safe-stop condition",
                tenant_scope=("tenant-a",),
                evidence_refs=("bad-l4",),
                brc_lifecycle_verified=True,
            )
        )


def test_append_only_records_are_immutable_and_log_has_no_update_delete_api():
    cis, log = _coordinator()
    cis.coordinate(_request(EscalationLevel.L2_TENANT_SCOPED_THREAT))
    record = log.entries()[0]

    assert not hasattr(log, "delete")
    assert not hasattr(log, "update")
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.detail = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Class 3 — known gap
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "CIS currently proves BRC lifecycle by caller-supplied boolean, not by "
        "cryptographic gateway receipt. Completion path: signed cross-organ "
        "telemetry/receipt standard (Gap 9) supplies verifiable BRC proof."
    ),
    strict=True,
)
def test_xfail_cryptographic_brc_lifecycle_receipt_required():
    raise AssertionError("not implemented — separate telemetry receipt contract")
