"""Operator-controlled kill switch (RSI prereq #7).

The kill switch is a SEPARATE surface from ``production_state`` — Guardrail
11's four mutable production surfaces are unchanged. This module owns:

- ``OperatorControlState``: frozen snapshot persisted to
  ``blackboard_root/operator_state/operator.json``.
- ``engage_kill_switch`` / ``disengage_kill_switch``: the only two write
  functions. Defense-by-convention: not imported by any agent or loop.
- ``is_kill_switch_engaged``: the cheap read every loop entry calls.
- ``OperatorAuditEntry`` + append-only ``operator.audit.jsonl``: the single
  source of truth for kill-switch events (per resolved decision #1 in the
  spec).
- ``KillSwitchEngaged``: the ``RuntimeError`` subclass raised by every
  loop entry when the switch covers its scope.

See ``Policy_Pipeline/operator-kill-switch.md`` for the full spec.
"""

from .audit import (
    OperatorAuditAction,
    OperatorAuditEntry,
    append_operator_audit_entry,
    operator_audit_log_path,
    read_operator_audit_log,
)
from .gate import (
    disengage_kill_switch,
    engage_kill_switch,
    is_kill_switch_engaged,
)
from .state import (
    KillSwitchEngaged,
    KillSwitchScope,
    OperatorControlState,
    load_operator_state,
    operator_state_path,
    save_operator_state,
)
from .security_profile import (
    DEFAULT_SECURITY_PROFILE,
    DETECTOR_MIN_TIER,
    DetectorIdentity,
    ForcedEscalationEvidence,
    ForcedEscalationTrigger,
    ProfileResolution,
    SalesPlan,
    SecurityProfile,
    TenantSecurityProfileState,
    default_profile_for_sales_plan,
    load_tenant_profile_state,
    resolve_profile_for_email,
    save_tenant_profile_state,
    tenant_profile_state_path,
)

__all__ = [
    "KillSwitchEngaged",
    "KillSwitchScope",
    "DEFAULT_SECURITY_PROFILE",
    "DETECTOR_MIN_TIER",
    "DetectorIdentity",
    "ForcedEscalationEvidence",
    "ForcedEscalationTrigger",
    "OperatorAuditAction",
    "OperatorAuditEntry",
    "OperatorControlState",
    "ProfileResolution",
    "SalesPlan",
    "SecurityProfile",
    "TenantSecurityProfileState",
    "append_operator_audit_entry",
    "default_profile_for_sales_plan",
    "disengage_kill_switch",
    "engage_kill_switch",
    "is_kill_switch_engaged",
    "load_operator_state",
    "load_tenant_profile_state",
    "operator_audit_log_path",
    "operator_state_path",
    "read_operator_audit_log",
    "resolve_profile_for_email",
    "save_operator_state",
    "save_tenant_profile_state",
    "tenant_profile_state_path",
]
