"""Cortex / Immune Interface boundary enforcement.

Governing contract
------------------
``4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol). Scoreboard row #96.

This module restricts existing paths. It is not a message bus, transport,
service, component implementation, or authority organ.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from core.cortex_immune_interface.log import (
    CortexImmuneInterfaceLog,
    InterfaceRecordKind,
)
from core.cortex_immune_interface.state import (
    LEGAL_CORTEX_TO_IMMUNE,
    LEGAL_IMMUNE_TO_CORTEX,
    BaselineValidationGate,
    CortexComponent,
    CortexToImmuneSignal,
    HandoffPoint,
    HiddenChannelType,
    ImmuneComponent,
    ImmuneToCortexSignal,
    InterfaceDecision,
    Organ,
)

REQUIRED_BASELINE_GATES: frozenset[BaselineValidationGate] = frozenset(
    BaselineValidationGate
)


class InterfaceError(Exception):
    """Base class for interface enforcement failures."""


class SignalRejected(InterfaceError):
    """Raised when a cross-organ signal violates the signed interface."""


class HiddenChannelRejected(InterfaceError):
    """Raised when a hidden channel is detected."""


class BaselineUpdateRejected(InterfaceError):
    """Raised when a governed baseline update misses a required gate."""


class SafeStopActiveError(InterfaceError):
    """Raised when Cortex tries to emit output while Safe-Stop is active."""


@dataclass(frozen=True)
class CortexSignal:
    workflow_id: str
    signal: CortexToImmuneSignal
    source: CortexComponent
    target: HandoffPoint
    tenant_id: str
    schema_valid: bool = True
    provenance_tagged: bool = True
    append_only: bool = True
    local_analysis_complete: bool = True
    signal_classified: bool = True
    local_threshold_exceeded: bool = True
    hypothesis_marked: bool = True
    contains_verdict: bool = False
    enforcement_request: bool = False
    cross_tenant: bool = False
    payload: Mapping[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload or {})))


@dataclass(frozen=True)
class ImmuneSignal:
    workflow_id: str
    signal: ImmuneToCortexSignal
    source: ImmuneComponent
    target: HandoffPoint
    tenant_id: str = ""
    epoch: int | None = None
    read_only: bool = True
    verdict_only: bool = True
    modifies_cortex_logic: bool = False
    enforcement_instruction: bool = False
    bypasses_handoff_point: bool = False
    cross_tenant: bool = False
    safe_stop_active: bool | None = None
    recovery_broadcast: bool = False


@dataclass(frozen=True)
class BaselineUpdateRequest:
    workflow_id: str
    tenant_id: str
    target_tenant_id: str
    gates_passed: frozenset[BaselineValidationGate]
    above_threshold: bool = False
    operator_approved: bool = False
    reversible: bool = True
    cortex_notified_of_approval_tier: bool = False


@dataclass(frozen=True)
class HiddenChannel:
    workflow_id: str
    channel_type: HiddenChannelType
    source: str
    target: str
    detail: str


@dataclass
class CortexImmuneInterface:
    """Contract-bounded cross-organ boundary guard."""

    log: CortexImmuneInterfaceLog
    safe_stop_active: bool = False

    def allow_cortex_to_immune(self, signal: CortexSignal) -> CortexSignal:
        if self.safe_stop_active:
            self._log_blocked(
                signal.workflow_id,
                "cortex output blocked while Safe-Stop is active",
                Organ.CORTEX,
                Organ.IMMUNE,
                signal.tenant_id,
                signal.source.value,
                signal.target.value,
                signal.target,
            )
            raise SafeStopActiveError("cortex cannot emit during Safe-Stop")
        self._validate_cortex_signal(signal)
        self.log.record(
            kind=InterfaceRecordKind.CORTEX_TO_IMMUNE,
            decision=InterfaceDecision.ALLOW,
            detail=f"{signal.signal.value} via {signal.target.value}",
            source_organ=Organ.CORTEX,
            target_organ=Organ.IMMUNE,
            workflow_id=signal.workflow_id,
            tenant_id=signal.tenant_id,
            source=signal.source.value,
            target=signal.target.value,
            handoff_point=signal.target,
        )
        return signal

    def allow_immune_to_cortex(self, signal: ImmuneSignal) -> ImmuneSignal:
        self._validate_immune_signal(signal)
        if signal.signal is ImmuneToCortexSignal.SAFE_STOP_STATE:
            self.safe_stop_active = bool(signal.safe_stop_active)
        elif signal.recovery_broadcast:
            self.safe_stop_active = False
        self.log.record(
            kind=(
                InterfaceRecordKind.SAFE_STOP_STATE
                if signal.signal is ImmuneToCortexSignal.SAFE_STOP_STATE
                else InterfaceRecordKind.IMMUNE_TO_CORTEX
            ),
            decision=InterfaceDecision.ALLOW,
            detail=f"{signal.signal.value} via {signal.target.value}",
            source_organ=Organ.IMMUNE,
            target_organ=Organ.CORTEX,
            workflow_id=signal.workflow_id,
            tenant_id=signal.tenant_id,
            source=signal.source.value,
            target=signal.target.value,
            handoff_point=signal.target,
        )
        return signal

    def apply_baseline_update(
        self, request: BaselineUpdateRequest
    ) -> BaselineUpdateRequest:
        missing = REQUIRED_BASELINE_GATES - request.gates_passed
        if missing:
            self._log_blocked(
                request.workflow_id,
                "baseline update missing required gates: "
                + ", ".join(sorted(g.value for g in missing)),
                Organ.IMMUNE,
                Organ.CORTEX,
                request.tenant_id,
                ImmuneComponent.GOVERNED_INGESTION_PIPELINE.value,
                HandoffPoint.TENANT_BASELINE_STORE.value,
                HandoffPoint.TENANT_BASELINE_STORE,
            )
            raise BaselineUpdateRejected("baseline update missing required gates")
        if request.tenant_id != request.target_tenant_id:
            self._log_blocked(
                request.workflow_id,
                "baseline update tenant scope mismatch",
                Organ.IMMUNE,
                Organ.CORTEX,
                request.tenant_id,
                ImmuneComponent.GOVERNED_INGESTION_PIPELINE.value,
                HandoffPoint.TENANT_BASELINE_STORE.value,
                HandoffPoint.TENANT_BASELINE_STORE,
            )
            raise BaselineUpdateRejected("baseline update must be tenant-scoped")
        if request.above_threshold and not request.operator_approved:
            self._log_blocked(
                request.workflow_id,
                "above-threshold baseline update lacks operator approval",
                Organ.IMMUNE,
                Organ.CORTEX,
                request.tenant_id,
                ImmuneComponent.GOVERNED_INGESTION_PIPELINE.value,
                HandoffPoint.TENANT_BASELINE_STORE.value,
                HandoffPoint.TENANT_BASELINE_STORE,
            )
            raise BaselineUpdateRejected("operator approval required")
        if not request.reversible or request.cortex_notified_of_approval_tier:
            self._log_blocked(
                request.workflow_id,
                "baseline update violates reversibility or approval-tier opacity",
                Organ.IMMUNE,
                Organ.CORTEX,
                request.tenant_id,
                ImmuneComponent.GOVERNED_INGESTION_PIPELINE.value,
                HandoffPoint.TENANT_BASELINE_STORE.value,
                HandoffPoint.TENANT_BASELINE_STORE,
            )
            raise BaselineUpdateRejected("baseline update boundary violated")

        self.log.record(
            kind=InterfaceRecordKind.BASELINE_UPDATE,
            decision=InterfaceDecision.ALLOW,
            detail="governed baseline update passed all gates",
            source_organ=Organ.IMMUNE,
            target_organ=Organ.CORTEX,
            workflow_id=request.workflow_id,
            tenant_id=request.tenant_id,
            source=ImmuneComponent.GOVERNED_INGESTION_PIPELINE.value,
            target=HandoffPoint.TENANT_BASELINE_STORE.value,
            handoff_point=HandoffPoint.TENANT_BASELINE_STORE,
        )
        return request

    def reject_hidden_channel(self, channel: HiddenChannel) -> None:
        self.log.record(
            kind=InterfaceRecordKind.HIDDEN_CHANNEL,
            decision=InterfaceDecision.VIOLATION,
            detail=channel.detail,
            source_organ=Organ.CORTEX,
            target_organ=Organ.IMMUNE,
            workflow_id=channel.workflow_id,
            source=channel.source,
            target=channel.target,
            hidden_channel_type=channel.channel_type,
        )
        raise HiddenChannelRejected("hidden cortex/immune channel detected")

    def _validate_cortex_signal(self, signal: CortexSignal) -> None:
        if not isinstance(signal.signal, CortexToImmuneSignal):
            raise SignalRejected("signal must be a CortexToImmuneSignal")
        allowed = any(
            rule.signal is signal.signal
            and rule.source is signal.source
            and rule.target is signal.target
            for rule in LEGAL_CORTEX_TO_IMMUNE
        )
        if not allowed:
            self._log_blocked_signal(signal, "cortex signal path is not contract-listed")
            raise SignalRejected("cortex signal path is not contract-listed")
        if not signal.tenant_id or signal.cross_tenant:
            self._log_blocked_signal(signal, "cortex signal must be tenant-scoped")
            raise SignalRejected("cortex signal must be tenant-scoped")
        if signal.contains_verdict or signal.enforcement_request:
            self._log_blocked_signal(signal, "cortex signal carried verdict/enforcement")
            raise SignalRejected("cortex cannot send verdicts or enforcement requests")
        if not (signal.schema_valid and signal.provenance_tagged and signal.append_only):
            self._log_blocked_signal(signal, "schema/provenance/append-only gate failed")
            raise SignalRejected("cortex signal failed required gates")
        if signal.signal is CortexToImmuneSignal.EVIDENCE_RECORD and not (
            signal.local_analysis_complete
        ):
            self._log_blocked_signal(signal, "evidence requires completed local analysis")
            raise SignalRejected("evidence requires completed local analysis")
        if signal.signal is CortexToImmuneSignal.OBSERVATION_RECORD and not (
            signal.signal_classified
        ):
            self._log_blocked_signal(signal, "observation requires classified signal")
            raise SignalRejected("observation requires classified signal")
        if signal.signal is CortexToImmuneSignal.ANOMALY_SIGNAL and not (
            signal.local_threshold_exceeded
        ):
            self._log_blocked_signal(signal, "anomaly requires local threshold")
            raise SignalRejected("anomaly requires local threshold")
        if signal.signal is CortexToImmuneSignal.HYPOTHESIS_RECORD and not (
            signal.hypothesis_marked
        ):
            self._log_blocked_signal(signal, "hypothesis must be marked as hypothesis")
            raise SignalRejected("hypothesis must be marked as hypothesis")

    def _validate_immune_signal(self, signal: ImmuneSignal) -> None:
        if signal.recovery_broadcast and not (
            signal.signal is ImmuneToCortexSignal.MODE_STATE_BROADCAST
            and signal.source is ImmuneComponent.MODE_CONTROLLER
            and signal.target is HandoffPoint.ALL_COMPONENTS
        ):
            self._log_blocked_immune(
                signal, "recovery broadcast must come from Mode Controller"
            )
            raise SignalRejected("recovery broadcast must come from Mode Controller")
        if self.safe_stop_active and not (
            signal.signal is ImmuneToCortexSignal.SAFE_STOP_STATE
            or signal.recovery_broadcast
        ):
            self._log_blocked_immune(signal, "immune signal blocked during Safe-Stop")
            raise SafeStopActiveError("only Safe-Stop state/recovery may cross during Safe-Stop")
        allowed = any(
            rule.signal is signal.signal
            and rule.source is signal.source
            and rule.target is signal.target
            for rule in LEGAL_IMMUNE_TO_CORTEX
        )
        if not allowed:
            self._log_blocked_immune(signal, "immune signal path is not contract-listed")
            raise SignalRejected("immune signal path is not contract-listed")
        if signal.modifies_cortex_logic or signal.enforcement_instruction:
            self._log_blocked_immune(signal, "immune signal attempted cortex reprogramming")
            raise SignalRejected("immune cannot modify cortex logic or send instructions")
        if signal.bypasses_handoff_point or signal.cross_tenant:
            self._log_blocked_immune(signal, "immune signal bypass/cross-tenant violation")
            raise SignalRejected("immune signal bypass or cross-tenant violation")
        if signal.signal is ImmuneToCortexSignal.MODE_STATE_BROADCAST and not (
            signal.epoch is not None and signal.read_only
        ):
            self._log_blocked_immune(
                signal, "mode state must be epoch-stamped and read-only"
            )
            raise SignalRejected("mode state must be epoch-stamped and read-only")
        if signal.signal is ImmuneToCortexSignal.RECONCILIATION_OUTPUT and not (
            signal.tenant_id and signal.verdict_only
        ):
            self._log_blocked_immune(
                signal, "reconciliation output must be tenant-scoped verdict only"
            )
            raise SignalRejected("reconciliation output must be tenant-scoped verdict only")
        if signal.signal is ImmuneToCortexSignal.SAFE_STOP_STATE and signal.safe_stop_active is None:
            self._log_blocked_immune(signal, "safe-stop state must declare active/inactive")
            raise SignalRejected("safe-stop state must declare active/inactive")
        if signal.signal is ImmuneToCortexSignal.GOVERNED_BASELINE_UPDATE:
            self._log_blocked_immune(signal, "baseline updates must use apply_baseline_update")
            raise SignalRejected("baseline updates must use apply_baseline_update")

    def _log_blocked_signal(self, signal: CortexSignal, detail: str) -> None:
        self._log_blocked(
            signal.workflow_id,
            detail,
            Organ.CORTEX,
            Organ.IMMUNE,
            signal.tenant_id,
            signal.source.value,
            signal.target.value,
            signal.target,
        )

    def _log_blocked_immune(self, signal: ImmuneSignal, detail: str) -> None:
        self._log_blocked(
            signal.workflow_id,
            detail,
            Organ.IMMUNE,
            Organ.CORTEX,
            signal.tenant_id,
            signal.source.value,
            signal.target.value,
            signal.target,
        )

    def _log_blocked(
        self,
        workflow_id: str,
        detail: str,
        source_organ: Organ,
        target_organ: Organ,
        tenant_id: str,
        source: str,
        target: str,
        handoff_point: HandoffPoint | None,
    ) -> None:
        self.log.record(
            kind=InterfaceRecordKind.SIGNAL_BLOCKED,
            decision=InterfaceDecision.BLOCK,
            detail=detail,
            source_organ=source_organ,
            target_organ=target_organ,
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            source=source,
            target=target,
            handoff_point=handoff_point,
        )


__all__ = [
    "REQUIRED_BASELINE_GATES",
    "InterfaceError",
    "SignalRejected",
    "HiddenChannelRejected",
    "BaselineUpdateRejected",
    "SafeStopActiveError",
    "CortexSignal",
    "ImmuneSignal",
    "BaselineUpdateRequest",
    "HiddenChannel",
    "CortexImmuneInterface",
]
