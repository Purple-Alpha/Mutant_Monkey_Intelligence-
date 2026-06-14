"""Cortex / Immune Interface tests (Layer 6 Control Plane, scoreboard row #96).

Governing contract
------------------
``4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol).
"""

from __future__ import annotations

import dataclasses

import pytest

from core.cortex_immune_interface import (
    REQUIRED_BASELINE_GATES,
    BaselineUpdateRejected,
    BaselineUpdateRequest,
    BaselineValidationGate,
    CortexComponent,
    CortexImmuneInterface,
    CortexImmuneInterfaceLog,
    CortexSignal,
    CortexToImmuneSignal,
    HandoffPoint,
    HiddenChannel,
    HiddenChannelRejected,
    HiddenChannelType,
    ImmuneComponent,
    ImmuneSignal,
    ImmuneToCortexSignal,
    InterfaceDecision,
    InterfaceRecordKind,
    SafeStopActiveError,
    SignalRejected,
)


def _interface():
    log = CortexImmuneInterfaceLog()
    return CortexImmuneInterface(log=log), log


def _cortex_signal(
    signal: CortexToImmuneSignal = CortexToImmuneSignal.EVIDENCE_RECORD,
    *,
    target: HandoffPoint = HandoffPoint.EVIDENCE_LEDGER,
    source: CortexComponent = CortexComponent.DETECTION_AGENT,
    tenant_id: str = "tenant-a",
    **kwargs,
) -> CortexSignal:
    return CortexSignal(
        workflow_id=kwargs.pop("workflow_id", "wf-cortex"),
        signal=signal,
        source=source,
        target=target,
        tenant_id=tenant_id,
        **kwargs,
    )


def _immune_signal(
    signal: ImmuneToCortexSignal = ImmuneToCortexSignal.MODE_STATE_BROADCAST,
    *,
    source: ImmuneComponent = ImmuneComponent.MODE_CONTROLLER,
    target: HandoffPoint = HandoffPoint.ALL_COMPONENTS,
    **kwargs,
) -> ImmuneSignal:
    return ImmuneSignal(
        workflow_id=kwargs.pop("workflow_id", "wf-immune"),
        signal=signal,
        source=source,
        target=target,
        **kwargs,
    )


def _baseline_update(**kwargs) -> BaselineUpdateRequest:
    return BaselineUpdateRequest(
        workflow_id=kwargs.pop("workflow_id", "wf-baseline"),
        tenant_id=kwargs.pop("tenant_id", "tenant-a"),
        target_tenant_id=kwargs.pop("target_tenant_id", "tenant-a"),
        gates_passed=kwargs.pop("gates_passed", REQUIRED_BASELINE_GATES),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Expected legal paths
# ---------------------------------------------------------------------------


def test_legal_cortex_evidence_goes_to_evidence_ledger_only():
    boundary, log = _interface()
    signal = _cortex_signal()

    returned = boundary.allow_cortex_to_immune(signal)

    assert returned is signal
    record = log.entries()[-1]
    assert record.kind is InterfaceRecordKind.CORTEX_TO_IMMUNE
    assert record.decision is InterfaceDecision.ALLOW
    assert record.handoff_point is HandoffPoint.EVIDENCE_LEDGER


def test_legal_observation_and_anomaly_go_to_observation_log():
    boundary, log = _interface()

    boundary.allow_cortex_to_immune(
        _cortex_signal(
            CortexToImmuneSignal.OBSERVATION_RECORD,
            target=HandoffPoint.OBSERVATION_LOG,
        )
    )
    boundary.allow_cortex_to_immune(
        _cortex_signal(
            CortexToImmuneSignal.ANOMALY_SIGNAL,
            target=HandoffPoint.OBSERVATION_LOG,
        )
    )

    assert [r.handoff_point for r in log.entries()] == [
        HandoffPoint.OBSERVATION_LOG,
        HandoffPoint.OBSERVATION_LOG,
    ]


def test_legal_immune_mode_state_is_read_only_and_epoch_stamped():
    boundary, log = _interface()
    signal = _immune_signal(epoch=7, read_only=True)

    assert boundary.allow_immune_to_cortex(signal) is signal
    assert log.entries()[-1].handoff_point is HandoffPoint.ALL_COMPONENTS


def test_legal_reconciliation_output_is_verdict_only_to_evidence_ledger():
    boundary, log = _interface()
    signal = _immune_signal(
        ImmuneToCortexSignal.RECONCILIATION_OUTPUT,
        source=ImmuneComponent.RECONCILIATION_AGENT,
        target=HandoffPoint.EVIDENCE_LEDGER,
        tenant_id="tenant-a",
        verdict_only=True,
    )

    boundary.allow_immune_to_cortex(signal)

    assert log.entries()[-1].source == ImmuneComponent.RECONCILIATION_AGENT.value
    assert log.entries()[-1].handoff_point is HandoffPoint.EVIDENCE_LEDGER


def test_governed_baseline_update_passes_all_gates():
    boundary, log = _interface()
    update = _baseline_update()

    assert boundary.apply_baseline_update(update) is update
    assert log.entries()[-1].kind is InterfaceRecordKind.BASELINE_UPDATE


# ---------------------------------------------------------------------------
# Signed invariants
# ---------------------------------------------------------------------------


def test_ci_inv_1_cortex_write_to_verdict_ledger_is_rejected():
    boundary, log = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_cortex_to_immune(
            _cortex_signal(target=HandoffPoint.VERDICT_LEDGER)
        )

    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED


def test_ci_inv_2_cortex_direct_signal_to_immune_component_is_rejected():
    boundary, log = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_cortex_to_immune(
            _cortex_signal(
                CortexToImmuneSignal.ANOMALY_SIGNAL,
                target=HandoffPoint.IMMUNE_COMPONENT,
                enforcement_request=True,
            )
        )

    assert log.entries()[-1].decision is InterfaceDecision.BLOCK


def test_ci_inv_3_immune_runtime_cortex_reconfiguration_is_rejected():
    boundary, log = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_immune_to_cortex(
            _immune_signal(
                ImmuneToCortexSignal.MODE_STATE_BROADCAST,
                epoch=1,
                modifies_cortex_logic=True,
            )
        )

    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED


def test_ci_inv_4_direct_evidence_bypass_is_rejected():
    boundary, _ = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_cortex_to_immune(
            _cortex_signal(target=HandoffPoint.IMMUNE_COMPONENT)
        )


def test_ci_inv_5_anomaly_bypass_of_observation_log_is_rejected():
    boundary, _ = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_cortex_to_immune(
            _cortex_signal(
                CortexToImmuneSignal.ANOMALY_SIGNAL,
                target=HandoffPoint.EVIDENCE_LEDGER,
            )
        )


def test_ci_inv_6_hidden_channels_are_logged_and_rejected():
    boundary, log = _interface()

    with pytest.raises(HiddenChannelRejected):
        boundary.reject_hidden_channel(
            HiddenChannel(
                workflow_id="wf-hidden",
                channel_type=HiddenChannelType.DIRECT_FUNCTION_CALL,
                source="detection_agent",
                target="mode_controller",
                detail="direct function call bypasses ledger/log",
            )
        )

    record = log.entries()[-1]
    assert record.kind is InterfaceRecordKind.HIDDEN_CHANNEL
    assert record.decision is InterfaceDecision.VIOLATION
    assert record.hidden_channel_type is HiddenChannelType.DIRECT_FUNCTION_CALL


def test_ci_inv_7_cortex_output_halts_during_safe_stop():
    boundary, log = _interface()
    boundary.allow_immune_to_cortex(
        _immune_signal(
            ImmuneToCortexSignal.SAFE_STOP_STATE,
            source=ImmuneComponent.SAFE_STOP_STATE_MACHINE,
            safe_stop_active=True,
        )
    )

    with pytest.raises(SafeStopActiveError):
        boundary.allow_cortex_to_immune(_cortex_signal(workflow_id="wf-after-stop"))

    assert boundary.safe_stop_active is True
    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED


def test_ci_inv_8_baseline_update_is_tenant_scoped():
    boundary, _ = _interface()

    with pytest.raises(BaselineUpdateRejected):
        boundary.apply_baseline_update(
            _baseline_update(tenant_id="tenant-a", target_tenant_id="tenant-b")
        )


def test_ci_inv_9_cortex_read_from_verdict_ledger_path_is_absent():
    boundary, _ = _interface()

    assert not hasattr(boundary, "read_verdicts_for_cortex")
    assert not hasattr(boundary, "poll_verdict_ledger")


def test_ci_inv_10_reconciliation_verdict_cannot_reprogram_cortex_behavior():
    boundary, _ = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_immune_to_cortex(
            _immune_signal(
                ImmuneToCortexSignal.RECONCILIATION_OUTPUT,
                source=ImmuneComponent.RECONCILIATION_AGENT,
                target=HandoffPoint.EVIDENCE_LEDGER,
                tenant_id="tenant-a",
                verdict_only=True,
                modifies_cortex_logic=True,
            )
        )


def test_ci_inv_11_interface_log_is_append_only_and_records_are_immutable():
    boundary, log = _interface()
    boundary.allow_cortex_to_immune(_cortex_signal())
    record = log.entries()[0]

    assert not hasattr(log, "update")
    assert not hasattr(log, "delete")
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.detail = "changed"  # type: ignore[misc]


def test_ci_inv_12_above_threshold_baseline_update_requires_operator_approval():
    boundary, _ = _interface()

    with pytest.raises(BaselineUpdateRejected, match="operator approval"):
        boundary.apply_baseline_update(
            _baseline_update(above_threshold=True, operator_approved=False)
        )

    approved = _baseline_update(above_threshold=True, operator_approved=True)
    assert boundary.apply_baseline_update(approved) is approved


def test_baseline_update_requires_all_validation_gates_and_opacity():
    boundary, _ = _interface()
    missing_gate_set = REQUIRED_BASELINE_GATES - {BaselineValidationGate.ROLLBACK_EVIDENCE}

    with pytest.raises(BaselineUpdateRejected, match="required gates"):
        boundary.apply_baseline_update(_baseline_update(gates_passed=missing_gate_set))
    with pytest.raises(BaselineUpdateRejected):
        boundary.apply_baseline_update(_baseline_update(reversible=False))
    with pytest.raises(BaselineUpdateRejected):
        boundary.apply_baseline_update(
            _baseline_update(cortex_notified_of_approval_tier=True)
        )


def test_safe_stop_allows_only_safe_stop_state_or_recovery_broadcast_to_cross():
    boundary, _ = _interface()
    boundary.allow_immune_to_cortex(
        _immune_signal(
            ImmuneToCortexSignal.SAFE_STOP_STATE,
            source=ImmuneComponent.SAFE_STOP_STATE_MACHINE,
            safe_stop_active=True,
        )
    )

    with pytest.raises(SafeStopActiveError):
        boundary.allow_immune_to_cortex(
            _immune_signal(
                ImmuneToCortexSignal.RECONCILIATION_OUTPUT,
                source=ImmuneComponent.RECONCILIATION_AGENT,
                target=HandoffPoint.EVIDENCE_LEDGER,
                tenant_id="tenant-a",
            )
        )

    recovery = _immune_signal(
        ImmuneToCortexSignal.MODE_STATE_BROADCAST,
        epoch=8,
        recovery_broadcast=True,
    )
    assert boundary.allow_immune_to_cortex(recovery) is recovery
    assert boundary.safe_stop_active is False
    assert boundary.allow_cortex_to_immune(_cortex_signal(workflow_id="wf-resumed"))


def test_codex_recovery_broadcast_must_come_from_mode_controller():
    boundary, log = _interface()
    boundary.allow_immune_to_cortex(
        _immune_signal(
            ImmuneToCortexSignal.SAFE_STOP_STATE,
            source=ImmuneComponent.SAFE_STOP_STATE_MACHINE,
            safe_stop_active=True,
        )
    )

    with pytest.raises(SignalRejected, match="Mode Controller"):
        boundary.allow_immune_to_cortex(
            _immune_signal(
                ImmuneToCortexSignal.RECONCILIATION_OUTPUT,
                source=ImmuneComponent.RECONCILIATION_AGENT,
                target=HandoffPoint.EVIDENCE_LEDGER,
                tenant_id="tenant-a",
                recovery_broadcast=True,
            )
        )

    assert boundary.safe_stop_active is True
    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED


def test_codex_condition_based_cortex_rejection_is_logged():
    boundary, log = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_cortex_to_immune(
            _cortex_signal(local_analysis_complete=False)
        )

    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED
    assert "local analysis" in log.entries()[-1].detail


def test_codex_condition_based_immune_rejection_is_logged():
    boundary, log = _interface()

    with pytest.raises(SignalRejected):
        boundary.allow_immune_to_cortex(_immune_signal(epoch=None))

    assert log.entries()[-1].kind is InterfaceRecordKind.SIGNAL_BLOCKED
    assert "epoch-stamped" in log.entries()[-1].detail


@pytest.mark.xfail(
    reason=(
        "Hidden-channel audit is caller-supplied static evidence, not whole-repo "
        "call-graph enforcement. Completion path: signed static-analysis receipt "
        "contract for cross-organ direct-call scanning."
    ),
    strict=True,
)
def test_xfail_whole_repo_hidden_channel_static_analysis_receipt():
    raise AssertionError("not implemented — separate static-analysis receipt contract")
