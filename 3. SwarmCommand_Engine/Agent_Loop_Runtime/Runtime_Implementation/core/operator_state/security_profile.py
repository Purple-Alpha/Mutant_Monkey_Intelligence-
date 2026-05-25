"""Tenant security-intensity profiles for NorthStar Inbox Shield.

This module implements the §11-signed Tiered Detection Intensity contract.
It is operator-controlled tenant policy, not production policy state: profile
files live under ``blackboard_root/operator_state/security_profiles/`` and
profile writes append to the existing operator audit log.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Iterable, Literal, TypeAlias, get_args

from core.blackboard import GovernanceError
from core.production_state.vendor_baseline.isolation import harden_path, validate_tenant_id

from .audit import (
    OperatorAuditEntry,
    append_operator_audit_entry,
    operator_audit_log_path,
)

SecurityProfile: TypeAlias = Literal["low", "medium", "high"]
DetectorIdentity: TypeAlias = Literal[
    "llm_primary",
    "ransomware_precursor_overlay",
    "header_divergence",
    "ghost_thread",
    "financial_state_ledger",
]
ForcedEscalationTrigger: TypeAlias = Literal[
    "llm_high_risk_score",
    "header_divergence_strong",
    "ghost_thread_detected",
    "manual_operator_escalation",
]
SalesPlan: TypeAlias = Literal["essentials", "plus", "enterprise"]


class _SecurityProfileRank(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


DEFAULT_SECURITY_PROFILE: SecurityProfile = "medium"

DETECTOR_MIN_TIER: dict[DetectorIdentity, SecurityProfile] = {
    "llm_primary": "low",
    "ransomware_precursor_overlay": "low",
    "header_divergence": "low",
    "ghost_thread": "low",
    "financial_state_ledger": "medium",
}

_VALID_PROFILES = frozenset(get_args(SecurityProfile))
_VALID_DETECTORS = frozenset(get_args(DetectorIdentity))
_VALID_TRIGGERS = frozenset(get_args(ForcedEscalationTrigger))
_VALID_SALES_PLANS = frozenset(get_args(SalesPlan))
_ALLOWED_STATE_FIELDS = frozenset(
    {
        "tenant_id",
        "profile",
        "addon_detectors",
        "updated_at",
        "updated_by",
        "reason",
    }
)
_TRIGGER_ORDER: tuple[ForcedEscalationTrigger, ...] = (
    "llm_high_risk_score",
    "header_divergence_strong",
    "ghost_thread_detected",
    "manual_operator_escalation",
)


@dataclass(frozen=True)
class TenantSecurityProfileState:
    tenant_id: str
    profile: SecurityProfile
    addon_detectors: tuple[DetectorIdentity, ...] = ()
    updated_at: datetime | None = None
    updated_by: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ProfileResolution:
    tenant_default: SecurityProfile
    effective_profile: SecurityProfile
    forced_escalation_triggers: tuple[ForcedEscalationTrigger, ...]
    enabled_detectors: tuple[DetectorIdentity, ...]


@dataclass(frozen=True)
class ForcedEscalationEvidence:
    """Inputs to the forced-escalation evaluator for one email."""

    llm_risk_score: int | None = None
    header_divergence_score: int | None = None
    ghost_thread_score: int | None = None
    manual_escalation_requested: bool = False


def resolve_profile_for_email(
    *,
    tenant_default: SecurityProfile,
    addon_detectors: Iterable[DetectorIdentity],
    evidence: ForcedEscalationEvidence,
) -> ProfileResolution:
    """Resolve one email's effective security profile.

    Pure function. The effective profile rank is always greater than or equal
    to the tenant default rank; forced escalation can only lift to ``high``.
    """

    tenant_default = _validate_profile(tenant_default)
    addons = _normalize_addon_detectors(addon_detectors)
    triggers = _forced_triggers_from_evidence(evidence)
    effective_profile: SecurityProfile = "high" if triggers else tenant_default
    enabled = _enabled_detectors(effective_profile, addons)
    return ProfileResolution(
        tenant_default=tenant_default,
        effective_profile=effective_profile,
        forced_escalation_triggers=triggers,
        enabled_detectors=enabled,
    )


def default_profile_for_sales_plan(plan: SalesPlan) -> SecurityProfile:
    """Return the locked Option-C sales-plan default profile."""

    if plan == "essentials":
        return "low"
    if plan == "plus":
        return "medium"
    if plan == "enterprise":
        return "high"
    raise GovernanceError(
        f"sales plan must be one of {sorted(_VALID_SALES_PLANS)}, got {plan!r}"
    )


def tenant_profile_state_path(blackboard_root: Path, tenant_id: str) -> Path:
    """Return the per-tenant operator-state profile file path."""

    return (
        Path(blackboard_root)
        / "operator_state"
        / "security_profiles"
        / f"{validate_tenant_id(tenant_id)}.json"
    )


def load_tenant_profile_state(
    blackboard_root: Path, tenant_id: str
) -> TenantSecurityProfileState:
    """Strict-load a tenant profile, defaulting to MEDIUM when absent."""

    safe_tenant_id = validate_tenant_id(tenant_id)
    path = tenant_profile_state_path(blackboard_root, safe_tenant_id)
    if not path.exists():
        return TenantSecurityProfileState(
            tenant_id=safe_tenant_id,
            profile=DEFAULT_SECURITY_PROFILE,
        )

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GovernanceError("tenant security profile file is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise GovernanceError("tenant security profile file is not a JSON object")
    unknown = set(raw.keys()) - _ALLOWED_STATE_FIELDS
    if unknown:
        raise GovernanceError(
            f"tenant security profile contains unauthorized fields: {sorted(unknown)}"
        )

    raw_tenant = raw.get("tenant_id")
    if raw_tenant != safe_tenant_id:
        raise GovernanceError(
            "tenant security profile tenant_id does not match requested tenant"
        )

    profile = raw.get("profile")
    if not isinstance(profile, str) or profile not in _VALID_PROFILES:
        raise GovernanceError(
            f"profile must be one of {sorted(_VALID_PROFILES)}, got {profile!r}"
        )

    addon_detectors = _parse_addon_detectors(raw.get("addon_detectors", []))
    updated_at = _parse_optional_datetime(raw.get("updated_at"), field_name="updated_at")
    updated_by = raw.get("updated_by")
    if updated_by is not None and not isinstance(updated_by, str):
        raise GovernanceError("updated_by must be a string or null")
    reason = raw.get("reason")
    if reason is not None and not isinstance(reason, str):
        raise GovernanceError("reason must be a string or null")

    return TenantSecurityProfileState(
        tenant_id=safe_tenant_id,
        profile=profile,  # type: ignore[arg-type]
        addon_detectors=addon_detectors,
        updated_at=updated_at,
        updated_by=updated_by,
        reason=reason,
    )


def save_tenant_profile_state(
    blackboard_root: Path,
    state: TenantSecurityProfileState,
    *,
    actor: str,
    reason: str,
) -> None:
    """Persist a tenant profile and append one operator audit row."""

    if not actor.strip():
        raise ValueError("actor must not be empty")
    if not reason.strip():
        raise ValueError("reason must not be empty")

    safe_tenant_id = validate_tenant_id(state.tenant_id)
    profile = _validate_profile(state.profile)
    addon_detectors = _normalize_addon_detectors(state.addon_detectors)
    previous = load_tenant_profile_state(blackboard_root, safe_tenant_id)
    now = datetime.now(timezone.utc)
    stamped = replace(
        state,
        tenant_id=safe_tenant_id,
        profile=profile,
        addon_detectors=addon_detectors,
        updated_at=now,
        updated_by=actor,
        reason=reason,
    )
    path = tenant_profile_state_path(blackboard_root, safe_tenant_id)
    _save_profile_state_file(path, stamped)
    append_operator_audit_entry(
        operator_audit_log_path(blackboard_root),
        OperatorAuditEntry(
            action="PROFILE_CHANGE",
            scope="NONE",
            previous_scope="NONE",
            operator=actor,
            reason=reason,
            at=now,
            tenant_id=safe_tenant_id,
            security_profile=profile,
            previous_security_profile=previous.profile,
            addon_detectors=addon_detectors,
        ),
    )


def _rank(profile: SecurityProfile) -> _SecurityProfileRank:
    if profile == "low":
        return _SecurityProfileRank.LOW
    if profile == "medium":
        return _SecurityProfileRank.MEDIUM
    if profile == "high":
        return _SecurityProfileRank.HIGH
    raise GovernanceError(
        f"profile must be one of {sorted(_VALID_PROFILES)}, got {profile!r}"
    )


def _validate_profile(profile: str) -> SecurityProfile:
    if profile not in _VALID_PROFILES:
        raise GovernanceError(
            f"profile must be one of {sorted(_VALID_PROFILES)}, got {profile!r}"
        )
    return profile  # type: ignore[return-value]


def _normalize_addon_detectors(
    addon_detectors: Iterable[DetectorIdentity],
) -> tuple[DetectorIdentity, ...]:
    seen: set[str] = set()
    normalized: list[DetectorIdentity] = []
    for detector in addon_detectors:
        if detector not in _VALID_DETECTORS:
            raise GovernanceError(
                f"addon detector must be one of {sorted(_VALID_DETECTORS)}, "
                f"got {detector!r}"
            )
        if detector not in seen:
            normalized.append(detector)
            seen.add(detector)
    return tuple(normalized)


def _parse_addon_detectors(value: object) -> tuple[DetectorIdentity, ...]:
    if not isinstance(value, list):
        raise GovernanceError("addon_detectors must be a list")
    if not all(isinstance(item, str) for item in value):
        raise GovernanceError("addon_detectors must be a list of strings")
    return _normalize_addon_detectors(value)  # type: ignore[arg-type]


def _forced_triggers_from_evidence(
    evidence: ForcedEscalationEvidence,
) -> tuple[ForcedEscalationTrigger, ...]:
    fired: list[ForcedEscalationTrigger] = []
    if evidence.llm_risk_score is not None and evidence.llm_risk_score >= 80:
        fired.append("llm_high_risk_score")
    if (
        evidence.header_divergence_score is not None
        and evidence.header_divergence_score >= 80
    ):
        fired.append("header_divergence_strong")
    if evidence.ghost_thread_score is not None and evidence.ghost_thread_score > 0:
        fired.append("ghost_thread_detected")
    if evidence.manual_escalation_requested:
        fired.append("manual_operator_escalation")
    return tuple(trigger for trigger in _TRIGGER_ORDER if trigger in fired)


def _enabled_detectors(
    effective_profile: SecurityProfile,
    addon_detectors: tuple[DetectorIdentity, ...],
) -> tuple[DetectorIdentity, ...]:
    profile_rank = _rank(effective_profile)
    enabled: list[DetectorIdentity] = []
    for detector, min_tier in DETECTOR_MIN_TIER.items():
        if _rank(min_tier) <= profile_rank or detector in addon_detectors:
            enabled.append(detector)
    return tuple(enabled)


def _save_profile_state_file(path: Path, state: TenantSecurityProfileState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    harden_path(path.parent, is_directory=True)
    payload = {
        "addon_detectors": list(state.addon_detectors),
        "profile": state.profile,
        "reason": state.reason,
        "tenant_id": state.tenant_id,
        "updated_at": (
            state.updated_at.isoformat() if state.updated_at is not None else None
        ),
        "updated_by": state.updated_by,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    tmp.replace(path)
    harden_path(path, is_directory=False)


def _parse_optional_datetime(value: object, *, field_name: str) -> datetime | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise GovernanceError(f"{field_name} must be an ISO-8601 string or null")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise GovernanceError(
            f"{field_name} is not a valid ISO-8601 datetime: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


__all__ = [
    "DEFAULT_SECURITY_PROFILE",
    "DETECTOR_MIN_TIER",
    "DetectorIdentity",
    "ForcedEscalationEvidence",
    "ForcedEscalationTrigger",
    "ProfileResolution",
    "SalesPlan",
    "SecurityProfile",
    "TenantSecurityProfileState",
    "_SecurityProfileRank",
    "_rank",
    "default_profile_for_sales_plan",
    "load_tenant_profile_state",
    "resolve_profile_for_email",
    "save_tenant_profile_state",
    "tenant_profile_state_path",
]
