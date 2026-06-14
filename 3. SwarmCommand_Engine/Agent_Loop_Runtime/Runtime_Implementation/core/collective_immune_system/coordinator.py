"""CollectiveImmuneSystemCoordinator — coordination only, no new authority.

Governing contract
------------------
``4. Product_Roadmap/Collective_Immune_System_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol). Scoreboard row #95 (Layer 6 Control Plane).

The CIS coordinates immune-organ handoffs and escalation notifications. It does
not write mode state, increment epoch, produce verdicts, initiate fission,
authorize mutation, bypass Privacy Filter, bypass the BRC lifecycle, or operate
inside Safe-Stop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from core.collective_immune_system.log import (
    CISRecordKind,
    CollectiveImmuneSystemLog,
)
from core.collective_immune_system.state import (
    CISAction,
    CISComponent,
    EscalationLevel,
    ForbiddenCISAction,
    is_authorized_handoff,
)

SAFE_STOP_ENTRY_CONDITIONS: frozenset[str] = frozenset(
    {"SS-1", "SS-2", "SS-3", "SS-4", "SS-5"}
)


class CISError(Exception):
    """Base class for CIS coordination failures (fail-safe)."""


class HandoffRejected(CISError):
    """Raised when a handoff path or payload violates the signed contract."""


class EscalationRejected(CISError):
    """Raised when an escalation request exceeds the level's authority."""


class ForbiddenActionRejected(CISError):
    """Raised when a caller attempts a forbidden CIS action."""


class SafeStopBoundaryError(CISError):
    """Raised when CIS is asked to operate after Safe-Stop handoff."""


@dataclass(frozen=True)
class EscalationRequest:
    """Inputs for one CIS escalation decision.

    ``tenant_scope`` carries tenant boundaries separately from payloads so handoff
    payloads never need raw tenant identifiers.
    """

    workflow_id: str
    level: EscalationLevel
    trigger: str
    tenant_scope: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    components_detected: tuple[CISComponent, ...] = ()
    brc_lifecycle_verified: bool = False
    reconciliation_named_conflict: bool = False
    control_plane_integrity_risk: bool = False
    mode_degraded: bool = False
    systemic_reconciliation_conflict: bool = False
    safe_stop_condition: str | None = None
    watcher_fission_triggered: bool = False


@dataclass(frozen=True)
class EvidenceHandoff:
    """One contract-enumerated evidence transfer request."""

    workflow_id: str
    level: EscalationLevel
    source: CISComponent
    target: CISComponent
    tenant_scope: tuple[str, ...]
    evidence_ref: str
    payload: Mapping[str, str] = field(default_factory=dict)
    brc_lifecycle_verified: bool = False

    def __post_init__(self) -> None:
        # A frozen dataclass does not freeze nested dicts. Copy + proxy here so
        # the payload validated by CIS cannot be changed before forwarding.
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True)
class CoordinationPlan:
    """A logged, authority-free plan returned by the CIS coordinator."""

    workflow_id: str
    level: EscalationLevel
    actions: tuple[CISAction, ...]
    notify: tuple[CISComponent, ...]
    tenant_scope: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass
class CollectiveImmuneSystemCoordinator:
    """Contract-bounded CIS coordinator.

    The coordinator only emits logged plans and handoff approvals. It has no
    references to mode, verdict, fission, mutation, or Safe-Stop internals, which
    keeps those authorities structurally out of scope.
    """

    log: CollectiveImmuneSystemLog
    _current_level: EscalationLevel = EscalationLevel.L1_LOCAL_ANOMALY
    _safe_stop_handed_off: bool = False

    @property
    def current_level(self) -> EscalationLevel:
        return self._current_level

    def coordinate(self, request: EscalationRequest) -> CoordinationPlan:
        """Return a logged coordination plan for the requested escalation level."""

        if self._safe_stop_handed_off:
            raise SafeStopBoundaryError("CIS cannot coordinate inside Safe-Stop")

        if not isinstance(request.level, EscalationLevel):
            raise EscalationRejected("level must be an EscalationLevel")
        if not request.brc_lifecycle_verified:
            self._block_action(
                request.workflow_id,
                request.level,
                ForbiddenCISAction.BYPASS_BRC_LIFECYCLE,
                "BRC lifecycle verification missing",
            )
            raise ForbiddenActionRejected("CIS cannot bypass BRC lifecycle")

        actions = self._actions_for(request)
        notify = self._notify_for(request.level)

        transition_record = self.log.record(
            kind=CISRecordKind.LEVEL_TRANSITION,
            detail=request.trigger,
            level=request.level,
            workflow_id=request.workflow_id,
            source=CISComponent.CIS_COORDINATOR,
            target=CISComponent.ALL_COMPONENTS,
            tenant_scope=request.tenant_scope,
            evidence_refs=request.evidence_refs,
        )
        if notify:
            self.log.record(
                kind=CISRecordKind.COMPONENT_NOTIFICATION,
                detail=f"components notified after {transition_record.kind.value}",
                level=request.level,
                workflow_id=request.workflow_id,
                source=CISComponent.CIS_COORDINATOR,
                target=CISComponent.ALL_COMPONENTS,
                tenant_scope=request.tenant_scope,
                evidence_refs=request.evidence_refs,
            )

        if CISAction.SUSPEND_MUTATION_ENGINE in actions:
            self.log.record(
                kind=CISRecordKind.MUTATION_SUSPENDED,
                detail="mutation suspended at CIS-L3 or above",
                level=request.level,
                workflow_id=request.workflow_id,
                source=CISComponent.CIS_COORDINATOR,
                target=CISComponent.MUTATION_ENGINE,
                tenant_scope=request.tenant_scope,
                evidence_refs=request.evidence_refs,
            )

        if request.level is EscalationLevel.L4_SAFE_STOP_CONDITION:
            self.log.record(
                kind=CISRecordKind.SAFE_STOP_HANDOFF,
                detail="handoff to Safe-Stop State Machine; CIS authority ends",
                level=request.level,
                workflow_id=request.workflow_id,
                source=CISComponent.CIS_COORDINATOR,
                target=CISComponent.SAFE_STOP_STATE_MACHINE,
                tenant_scope=request.tenant_scope,
                evidence_refs=request.evidence_refs,
            )
            self._safe_stop_handed_off = True

        self._current_level = request.level
        return CoordinationPlan(
            workflow_id=request.workflow_id,
            level=request.level,
            actions=actions,
            notify=notify,
            tenant_scope=request.tenant_scope,
            evidence_refs=request.evidence_refs,
        )

    def handoff(self, handoff: EvidenceHandoff) -> EvidenceHandoff:
        """Approve a contract-enumerated handoff after writing its log record."""

        if self._safe_stop_handed_off:
            raise SafeStopBoundaryError("CIS cannot perform handoffs inside Safe-Stop")

        if not handoff.brc_lifecycle_verified:
            self._block_action(
                handoff.workflow_id,
                handoff.level,
                ForbiddenCISAction.BYPASS_BRC_LIFECYCLE,
                "BRC lifecycle verification missing",
            )
            raise ForbiddenActionRejected("CIS cannot bypass BRC lifecycle")
        if not handoff.tenant_scope:
            self.log.record(
                kind=CISRecordKind.HANDOFF_BLOCKED,
                detail="tenant scope is required for every CIS evidence handoff",
                level=handoff.level,
                workflow_id=handoff.workflow_id,
                source=handoff.source,
                target=handoff.target,
                tenant_scope=handoff.tenant_scope,
                evidence_refs=(handoff.evidence_ref,),
            )
            raise HandoffRejected("tenant scope is required for CIS handoff")
        if not is_authorized_handoff(handoff.source, handoff.target, handoff.level):
            self.log.record(
                kind=CISRecordKind.HANDOFF_BLOCKED,
                detail=f"unauthorized handoff {handoff.source.value}->{handoff.target.value}",
                level=handoff.level,
                workflow_id=handoff.workflow_id,
                source=handoff.source,
                target=handoff.target,
                tenant_scope=handoff.tenant_scope,
                evidence_refs=(handoff.evidence_ref,),
            )
            raise HandoffRejected("handoff path is not authorized by CIS contract")
        self._reject_raw_tenant_identifier_payload(handoff)

        self.log.record(
            kind=CISRecordKind.HANDOFF,
            detail=f"authorized handoff {handoff.source.value}->{handoff.target.value}",
            level=handoff.level,
            workflow_id=handoff.workflow_id,
            source=handoff.source,
            target=handoff.target,
            tenant_scope=handoff.tenant_scope,
            evidence_refs=(handoff.evidence_ref,),
        )
        return handoff

    def reject_forbidden_action(
        self,
        action: ForbiddenCISAction,
        *,
        workflow_id: str,
        level: EscalationLevel | None = None,
    ) -> None:
        """Public proof hook for contract-forbidden actions."""

        if self._safe_stop_handed_off:
            raise SafeStopBoundaryError("CIS cannot log forbidden-action probes inside Safe-Stop")
        level = level or self._current_level
        self._block_action(
            workflow_id,
            level,
            action,
            f"forbidden CIS action rejected: {action.value}",
        )
        raise ForbiddenActionRejected(action.value)

    def _actions_for(self, request: EscalationRequest) -> tuple[CISAction, ...]:
        level = request.level
        if level is EscalationLevel.L1_LOCAL_ANOMALY:
            if len(request.components_detected) > 1:
                raise EscalationRejected("L1 is single-component only")
            return (CISAction.LOG_LOCAL_ANOMALY,)

        if level is EscalationLevel.L2_TENANT_SCOPED_THREAT:
            if len(request.tenant_scope) != 1:
                raise EscalationRejected("L2 must be scoped to exactly one tenant")
            recon_conflict = (
                request.reconciliation_named_conflict
                and CISComponent.RECONCILIATION_AGENT in request.components_detected
            )
            if (
                len(set(request.components_detected)) < 2
                and not recon_conflict
            ):
                raise EscalationRejected(
                    "L2 requires two correlated components or a ReconciliationAgent named conflict"
                )
            return (
                CISAction.ROUTE_EVIDENCE_TO_RECONCILIATION,
                CISAction.NOTIFY_MODE_CONTROLLER,
                CISAction.HOLD_CROSS_TENANT_BROADCASTS,
                CISAction.NOTIFY_WATCHERS_CONTINUE_OBSERVATION,
                CISAction.NOTIFY_COMPONENTS_OF_LEVEL,
            )

        if level is EscalationLevel.L3_SYSTEMIC_THREAT:
            if not (
                len(set(request.tenant_scope)) >= 2
                or request.control_plane_integrity_risk
                or request.mode_degraded
                or request.systemic_reconciliation_conflict
            ):
                raise EscalationRejected(
                    "L3 requires cross-tenant correlation, control-plane integrity risk, "
                    "DEGRADED mode, or systemic Reconciliation conflict"
                )
            actions = [
                CISAction.ROUTE_EVIDENCE_TO_RECONCILIATION,
                CISAction.NOTIFY_MODE_CONTROLLER,
                CISAction.HOLD_CROSS_TENANT_BROADCASTS,
                CISAction.SUSPEND_MUTATION_ENGINE,
                CISAction.NOTIFY_COMPONENTS_OF_LEVEL,
            ]
            if (
                request.watcher_fission_triggered
                and CISComponent.WATCHER_AGENT in request.components_detected
            ):
                actions.append(CISAction.ACKNOWLEDGE_WATCHER_TRIGGERED_FISSION)
            return tuple(actions)

        if level is EscalationLevel.L4_SAFE_STOP_CONDITION:
            if request.safe_stop_condition not in SAFE_STOP_ENTRY_CONDITIONS:
                raise EscalationRejected("L4 requires a real SS-1 through SS-5 Safe-Stop condition")
            return (
                CISAction.HAND_OFF_TO_SAFE_STOP,
                CISAction.SUSPEND_MUTATION_ENGINE,
            )

        raise EscalationRejected("unknown escalation level")

    @staticmethod
    def _notify_for(level: EscalationLevel) -> tuple[CISComponent, ...]:
        if level is EscalationLevel.L1_LOCAL_ANOMALY:
            return ()
        if level is EscalationLevel.L2_TENANT_SCOPED_THREAT:
            return (
                CISComponent.RECONCILIATION_AGENT,
                CISComponent.MODE_CONTROLLER,
                CISComponent.PRIVACY_FILTER,
                CISComponent.WATCHER_AGENT,
            )
        if level is EscalationLevel.L3_SYSTEMIC_THREAT:
            return (
                CISComponent.MODE_CONTROLLER,
                CISComponent.PRIVACY_FILTER,
                CISComponent.BLAST_RADIUS_CONTROLLER,
                CISComponent.RECONCILIATION_AGENT,
                CISComponent.MUTATION_ENGINE,
            )
        return (CISComponent.SAFE_STOP_STATE_MACHINE,)

    def _reject_raw_tenant_identifier_payload(self, handoff: EvidenceHandoff) -> None:
        payload_values = tuple(
            str(part) for item in handoff.payload.items() for part in item
        )
        for tenant_id in handoff.tenant_scope:
            if any(tenant_id and tenant_id in value for value in payload_values):
                self.log.record(
                    kind=CISRecordKind.HANDOFF_BLOCKED,
                    detail="raw tenant identifier found in handoff payload",
                    level=handoff.level,
                    workflow_id=handoff.workflow_id,
                    source=handoff.source,
                    target=handoff.target,
                    tenant_scope=handoff.tenant_scope,
                    evidence_refs=(handoff.evidence_ref,),
                )
                raise HandoffRejected("raw tenant identifiers are forbidden in payload")

    def _block_action(
        self,
        workflow_id: str,
        level: EscalationLevel,
        action: ForbiddenCISAction,
        detail: str,
    ) -> None:
        self.log.record(
            kind=CISRecordKind.ACTION_BLOCKED,
            detail=detail,
            level=level,
            workflow_id=workflow_id,
            source=CISComponent.CIS_COORDINATOR,
            tenant_scope=(),
            evidence_refs=(action.value,),
        )


__all__ = [
    "CISError",
    "HandoffRejected",
    "EscalationRejected",
    "ForbiddenActionRejected",
    "SafeStopBoundaryError",
    "EscalationRequest",
    "EvidenceHandoff",
    "CoordinationPlan",
    "CollectiveImmuneSystemCoordinator",
]
