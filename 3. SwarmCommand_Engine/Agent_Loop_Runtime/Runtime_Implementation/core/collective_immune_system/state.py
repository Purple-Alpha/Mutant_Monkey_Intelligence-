"""Closed CIS state vocabulary — Layer 6 Control Plane, scoreboard row #95.

Governing contract
------------------
``4. Product_Roadmap/Collective_Immune_System_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol).

The Collective Immune System is a coordination layer only. These enums define
the escalation levels, component names, authorized handoff paths, and forbidden
actions without creating any new authority surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EscalationLevel(str, Enum):
    """The four contract-defined CIS escalation levels."""

    L1_LOCAL_ANOMALY = "CIS-L1"
    L2_TENANT_SCOPED_THREAT = "CIS-L2"
    L3_SYSTEMIC_THREAT = "CIS-L3"
    L4_SAFE_STOP_CONDITION = "CIS-L4"


class CISComponent(str, Enum):
    """Immune-organ components the CIS may coordinate by contract."""

    WATCHER_AGENT = "watcher_agent"
    PRIVACY_FILTER = "privacy_filter"
    BLAST_RADIUS_CONTROLLER = "blast_radius_controller"
    RECONCILIATION_AGENT = "reconciliation_agent"
    MODE_CONTROLLER = "mode_controller"
    FISSION_CONTROLLER = "fission_controller"
    MUTATION_ENGINE = "mutation_engine"
    SAFE_STOP_STATE_MACHINE = "safe_stop_state_machine"
    CIS_COORDINATOR = "cis_coordinator"
    ALL_COMPONENTS = "all_components"


class CISAction(str, Enum):
    """Authorized coordination actions. None grants component authority."""

    LOG_LOCAL_ANOMALY = "log_local_anomaly"
    ROUTE_EVIDENCE_TO_RECONCILIATION = "route_evidence_to_reconciliation"
    NOTIFY_MODE_CONTROLLER = "notify_mode_controller"
    HOLD_CROSS_TENANT_BROADCASTS = "hold_cross_tenant_broadcasts"
    NOTIFY_WATCHERS_CONTINUE_OBSERVATION = "notify_watchers_continue_observation"
    NOTIFY_COMPONENTS_OF_LEVEL = "notify_components_of_level"
    SUSPEND_MUTATION_ENGINE = "suspend_mutation_engine"
    ACKNOWLEDGE_WATCHER_TRIGGERED_FISSION = "acknowledge_watcher_triggered_fission"
    HAND_OFF_TO_SAFE_STOP = "hand_off_to_safe_stop"


class ForbiddenCISAction(str, Enum):
    """Actions explicitly forbidden by the signed CIS contract."""

    WRITE_MODE_STATE = "write_mode_state"
    INCREMENT_EPOCH = "increment_epoch"
    PRODUCE_VERDICT = "produce_verdict"
    INITIATE_FISSION = "initiate_fission"
    AUTHORIZE_MUTATION = "authorize_mutation"
    ACCESS_RAW_TENANT_IDENTIFIERS = "access_raw_tenant_identifiers"
    BYPASS_PRIVACY_FILTER = "bypass_privacy_filter"
    BYPASS_BRC_LIFECYCLE = "bypass_brc_lifecycle"
    OPERATE_INSIDE_SAFE_STOP = "operate_inside_safe_stop"
    CREATE_AGENT_TYPE = "create_agent_type"
    EXPAND_COMPONENT_PERMISSIONS = "expand_component_permissions"
    SELF_AUTHORIZE_SCOPE = "self_authorize_scope"


@dataclass(frozen=True)
class HandoffPath:
    """One authorized cross-component evidence or notification channel."""

    source: CISComponent
    target: CISComponent
    condition: str
    levels: tuple[EscalationLevel, ...]


AUTHORIZED_HANDOFF_PATHS: frozenset[HandoffPath] = frozenset(
    {
        HandoffPath(
            CISComponent.WATCHER_AGENT,
            CISComponent.RECONCILIATION_AGENT,
            "CRITICAL escalation at L2 or above",
            (
                EscalationLevel.L2_TENANT_SCOPED_THREAT,
                EscalationLevel.L3_SYSTEMIC_THREAT,
                EscalationLevel.L4_SAFE_STOP_CONDITION,
            ),
        ),
        HandoffPath(
            CISComponent.PRIVACY_FILTER,
            CISComponent.MODE_CONTROLLER,
            "Privacy Filter breaker state change",
            (
                EscalationLevel.L2_TENANT_SCOPED_THREAT,
                EscalationLevel.L3_SYSTEMIC_THREAT,
                EscalationLevel.L4_SAFE_STOP_CONDITION,
            ),
        ),
        HandoffPath(
            CISComponent.BLAST_RADIUS_CONTROLLER,
            CISComponent.SAFE_STOP_STATE_MACHINE,
            "SS-4 condition detected",
            (EscalationLevel.L4_SAFE_STOP_CONDITION,),
        ),
        HandoffPath(
            CISComponent.RECONCILIATION_AGENT,
            CISComponent.MODE_CONTROLLER,
            "Unresolvable conflict at systemic scope",
            (
                EscalationLevel.L3_SYSTEMIC_THREAT,
                EscalationLevel.L4_SAFE_STOP_CONDITION,
            ),
        ),
        HandoffPath(
            CISComponent.CIS_COORDINATOR,
            CISComponent.ALL_COMPONENTS,
            "Level transition notification",
            (
                EscalationLevel.L2_TENANT_SCOPED_THREAT,
                EscalationLevel.L3_SYSTEMIC_THREAT,
                EscalationLevel.L4_SAFE_STOP_CONDITION,
            ),
        ),
        HandoffPath(
            CISComponent.SAFE_STOP_STATE_MACHINE,
            CISComponent.CIS_COORDINATOR,
            "Safe-Stop entry logged",
            (EscalationLevel.L4_SAFE_STOP_CONDITION,),
        ),
    }
)


def is_authorized_handoff(
    source: CISComponent, target: CISComponent, level: EscalationLevel
) -> bool:
    """Return True when source, target, and level match the contract path."""

    return any(
        path.source is source and path.target is target and level in path.levels
        for path in AUTHORIZED_HANDOFF_PATHS
    )


__all__ = [
    "EscalationLevel",
    "CISComponent",
    "CISAction",
    "ForbiddenCISAction",
    "HandoffPath",
    "AUTHORIZED_HANDOFF_PATHS",
    "is_authorized_handoff",
]
