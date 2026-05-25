"""Orchestrator routing primitives for approved Blackboard writes."""

from .registry import build_default_registry
from .routes import (
    RouteContext,
    RouteResult,
    submit_audit_verdict,
    submit_daily_digest,
    submit_detection_result,
    submit_email_analysis,
    submit_email_analysis_failure,
    submit_email_inbound,
    submit_effective_parameters_report,
    submit_ingest_event,
    submit_mutant_evaluation,
    submit_policy_update,
    submit_risk_score,
    submit_synthetic_attack_case,
    submit_synthetic_email_attack_case,
    submit_two_channel_confirmation,
    submit_vendor_baseline_audit,
    submit_weakness_report,
    trigger_workflow,
)
from .tenants import default_sandbox_tenant_for

__all__ = [
    "RouteContext",
    "RouteResult",
    "build_default_registry",
    "default_sandbox_tenant_for",
    "submit_audit_verdict",
    "submit_daily_digest",
    "submit_detection_result",
    "submit_email_analysis",
    "submit_email_analysis_failure",
    "submit_email_inbound",
    "submit_effective_parameters_report",
    "submit_ingest_event",
    "submit_mutant_evaluation",
    "submit_policy_update",
    "submit_risk_score",
    "submit_synthetic_attack_case",
    "submit_synthetic_email_attack_case",
    "submit_two_channel_confirmation",
    "submit_vendor_baseline_audit",
    "submit_weakness_report",
    "trigger_workflow",
]
