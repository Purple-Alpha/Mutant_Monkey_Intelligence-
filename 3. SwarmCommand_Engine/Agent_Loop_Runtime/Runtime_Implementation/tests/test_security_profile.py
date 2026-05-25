from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import get_args
from uuid import UUID

import pytest

from core.blackboard import (
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.operator_state import (
    OperatorAuditEntry,
    TenantSecurityProfileState,
    engage_kill_switch,
    load_tenant_profile_state,
    operator_audit_log_path,
    read_operator_audit_log,
    save_tenant_profile_state,
)
from core.operator_state import security_profile as sp
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle


TENANT = "tenant_demo"


def _root(tmp_path):
    return tmp_path / "blackboard"


def _resolution(
    profile: sp.SecurityProfile,
    *,
    addons=(),
    llm: int | None = 10,
    header: int | None = 0,
    ghost: int | None = 0,
    manual: bool = False,
) -> sp.ProfileResolution:
    return sp.resolve_profile_for_email(
        tenant_default=profile,
        addon_detectors=addons,
        evidence=sp.ForcedEscalationEvidence(
            llm_risk_score=llm,
            header_divergence_score=header,
            ghost_thread_score=ghost,
            manual_escalation_requested=manual,
        ),
    )


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=_root(tmp_path))


def _inbound(
    context: RouteContext,
    *,
    subject: str = "Invoice attached",
    sender: str = "vendor@example.com",
    headers: dict[str, str] | None = None,
) -> UUID:
    result = submit_email_inbound(
        context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=EmailInboundPayload(
            received_at="2026-05-24T12:00:00+00:00",
            sender=sender,
            recipient="ap@customer.example",
            subject=subject,
            body_plain="Please process attached invoice.",
            headers=headers or {},
        ),
    )
    return result.record.record_id


def _analysis_json(risk_score: int = 10) -> str:
    return json.dumps(
        {
            "summary": "Routine invoice.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": risk_score,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 0,
                "wire_transfer_anomaly_score": 0,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 0,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "safe",
        }
    )


def _client(raw_json: str):
    def _inner(system_prompt: str, user_prompt: str) -> str:
        json.loads(user_prompt)
        return raw_json

    return _inner


def _analysis_records(context: RouteContext):
    records = read_records(
        blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
    )
    return [record for record in records if record.record_type == RecordType.EMAIL_ANALYSIS]


def test_closed_enums_match_signed_spec() -> None:
    assert set(get_args(sp.SecurityProfile)) == {"low", "medium", "high"}
    assert set(get_args(sp.DetectorIdentity)) == {
        "llm_primary",
        "ransomware_precursor_overlay",
        "header_divergence",
        "ghost_thread",
        "financial_state_ledger",
    }
    assert set(get_args(sp.ForcedEscalationTrigger)) == {
        "llm_high_risk_score",
        "header_divergence_strong",
        "ghost_thread_detected",
        "manual_operator_escalation",
    }
    assert set(get_args(sp.SalesPlan)) == {"essentials", "plus", "enterprise"}


def test_rank_ordering_is_low_medium_high() -> None:
    assert sp._rank("low") < sp._rank("medium") < sp._rank("high")


def test_default_when_unset_is_medium(tmp_path) -> None:
    state = load_tenant_profile_state(_root(tmp_path), TENANT)
    assert state == TenantSecurityProfileState(tenant_id=TENANT, profile="medium")


def test_detector_min_tier_registry_is_exhaustive() -> None:
    assert set(sp.DETECTOR_MIN_TIER) == set(get_args(sp.DetectorIdentity))
    assert set(sp.DETECTOR_MIN_TIER.values()) <= set(get_args(sp.SecurityProfile))


def test_low_resolves_to_low_detectors_only() -> None:
    resolution = _resolution("low")
    assert resolution.enabled_detectors == (
        "llm_primary",
        "ransomware_precursor_overlay",
        "header_divergence",
        "ghost_thread",
    )
    assert "financial_state_ledger" not in resolution.enabled_detectors


def test_medium_resolves_to_low_plus_financial_state_ledger() -> None:
    assert "financial_state_ledger" in _resolution("medium").enabled_detectors


def test_high_resolves_to_medium_detector_set_in_v1() -> None:
    assert _resolution("high").enabled_detectors == _resolution("medium").enabled_detectors


def test_addon_lifts_financial_state_ledger_for_low_tenant() -> None:
    resolution = _resolution("low", addons=("financial_state_ledger",))
    assert "financial_state_ledger" in resolution.enabled_detectors


def test_addon_cannot_disable_tier_enabled_detectors() -> None:
    fields = set(TenantSecurityProfileState.__dataclass_fields__)
    assert "disabled_detectors" not in fields
    assert "financial_state_ledger" in _resolution("medium", addons=()).enabled_detectors


def test_forced_trigger_llm_high_score() -> None:
    resolution = _resolution("low", llm=85)
    assert resolution.effective_profile == "high"
    assert resolution.forced_escalation_triggers == ("llm_high_risk_score",)


def test_forced_trigger_header_divergence_strong() -> None:
    resolution = _resolution("low", header=85)
    assert resolution.effective_profile == "high"
    assert resolution.forced_escalation_triggers == ("header_divergence_strong",)


def test_forced_trigger_ghost_thread_detected() -> None:
    resolution = _resolution("low", ghost=10)
    assert resolution.effective_profile == "high"
    assert resolution.forced_escalation_triggers == ("ghost_thread_detected",)


def test_forced_trigger_manual_operator_escalation() -> None:
    resolution = _resolution("low", manual=True)
    assert resolution.effective_profile == "high"
    assert resolution.forced_escalation_triggers == ("manual_operator_escalation",)


def test_multiple_triggers_are_stable_and_deduplicated() -> None:
    resolution = _resolution("low", llm=85, header=85, ghost=10, manual=True)
    assert resolution.effective_profile == "high"
    assert resolution.forced_escalation_triggers == (
        "llm_high_risk_score",
        "header_divergence_strong",
        "ghost_thread_detected",
        "manual_operator_escalation",
    )


def test_lift_only_invariant_for_all_trigger_combinations() -> None:
    for profile in get_args(sp.SecurityProfile):
        for llm, header, ghost, manual in product((False, True), repeat=4):
            resolution = _resolution(
                profile,
                llm=85 if llm else 10,
                header=85 if header else 0,
                ghost=10 if ghost else 0,
                manual=manual,
            )
            assert sp._rank(resolution.effective_profile) >= sp._rank(profile)


def test_tenant_isolation_for_profile_files(tmp_path) -> None:
    root = _root(tmp_path)
    save_tenant_profile_state(
        root,
        TenantSecurityProfileState(tenant_id="tenant_a", profile="low"),
        actor="matt",
        reason="low exposure",
    )
    assert load_tenant_profile_state(root, "tenant_a").profile == "low"
    assert load_tenant_profile_state(root, "tenant_b").profile == "medium"


def test_profile_change_appends_operator_audit_row(tmp_path) -> None:
    root = _root(tmp_path)
    save_tenant_profile_state(
        root,
        TenantSecurityProfileState(
            tenant_id=TENANT,
            profile="low",
            addon_detectors=("financial_state_ledger",),
        ),
        actor="matt",
        reason="demo tenant",
    )

    entries = read_operator_audit_log(operator_audit_log_path(root))
    assert len(entries) == 1
    entry = entries[0]
    assert entry.action == "PROFILE_CHANGE"
    assert entry.scope == "NONE"
    assert entry.previous_scope == "NONE"
    assert entry.operator == "matt"
    assert entry.reason == "demo tenant"
    assert entry.tenant_id == TENANT
    assert entry.security_profile == "low"
    assert entry.previous_security_profile == "medium"
    assert entry.addon_detectors == ("financial_state_ledger",)


def test_forced_escalation_visible_on_analysis_payload(tmp_path) -> None:
    context = _context(tmp_path)
    _inbound(context)
    save_tenant_profile_state(
        context.blackboard_root,
        TenantSecurityProfileState(tenant_id=TENANT, profile="low"),
        actor="matt",
        reason="essentials",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_client(_analysis_json(risk_score=85)),
            production_tenant_id=TENANT,
        ),
    )

    payload = EmailAnalysisPayload.model_validate(_analysis_records(context)[0].payload)
    assert payload.tenant_default_profile == "low"
    assert payload.effective_profile == "high"
    assert payload.forced_escalation_triggers == ["llm_high_risk_score"]


def test_sales_plan_mapping_is_locked() -> None:
    assert sp.default_profile_for_sales_plan("essentials") == "low"
    assert sp.default_profile_for_sales_plan("plus") == "medium"
    assert sp.default_profile_for_sales_plan("enterprise") == "high"
    with pytest.raises(GovernanceError, match="sales plan"):
        sp.default_profile_for_sales_plan("starter")  # type: ignore[arg-type]


def test_kill_switch_precedence_skips_profile_load(tmp_path, monkeypatch) -> None:
    from core.scoring import email_risk_scoring_agent as agent

    context = _context(tmp_path)
    _inbound(context)
    engage_kill_switch(
        context.blackboard_root,
        scope="PRODUCTION_ONLY",
        reason="halt prod",
        operator="matt",
    )

    def boom(*args, **kwargs):
        raise AssertionError("profile state must not be read before kill switch")

    monkeypatch.setattr(agent, "load_tenant_profile_state", boom)
    with pytest.raises(Exception, match="kill switch engaged"):
        run_email_risk_scoring_cycle(
            context,
            config=EmailRiskScoringConfig(
                llm_client=_client(_analysis_json()),
                production_tenant_id=TENANT,
            ),
        )


def test_overlay_off_keeps_profile_resolution_unset(tmp_path, monkeypatch) -> None:
    from core.scoring import email_risk_scoring_agent as agent

    context = _context(tmp_path)
    _inbound(context)

    def boom(*args, **kwargs):
        raise AssertionError("profile resolver must not run when overlay is disabled")

    monkeypatch.setattr(agent, "_resolve_profile_for_inbound", boom)
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_client(_analysis_json()),
            production_tenant_id=TENANT,
            enable_ransomware_precursor_overlay=False,
        ),
    )
    payload = EmailAnalysisPayload.model_validate(_analysis_records(context)[0].payload)
    assert payload.ransomware_precursor_analysis is None
    assert payload.tenant_default_profile is None
    assert payload.effective_profile is None
    assert payload.forced_escalation_triggers == []


def test_existing_email_analysis_payload_schema_accepts_absent_profile_fields() -> None:
    raw = json.loads(_analysis_json())
    raw["source_email_record_id"] = "00000000-0000-0000-0000-000000000001"
    payload = EmailAnalysisPayload.model_validate(raw)
    assert payload.tenant_default_profile is None
    assert payload.effective_profile is None
    assert payload.forced_escalation_triggers == []


def test_cost_monotonicity_by_enabled_detector_count() -> None:
    low = len(_resolution("low").enabled_detectors)
    medium = len(_resolution("medium").enabled_detectors)
    high = len(_resolution("high").enabled_detectors)
    assert low <= medium <= high
    assert (low, medium, high) == (4, 5, 5)


def test_cost_ceiling_under_escalation() -> None:
    low_escalated = len(_resolution("low", llm=85).enabled_detectors)
    high_steady_state = len(_resolution("high").enabled_detectors)
    assert low_escalated <= high_steady_state


def test_profile_fields_do_not_leak_raw_email_or_financial_values(tmp_path) -> None:
    context = _context(tmp_path)
    _inbound(context)
    save_tenant_profile_state(
        context.blackboard_root,
        TenantSecurityProfileState(tenant_id=TENANT, profile="low"),
        actor="matt",
        reason="essentials",
    )
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_client(_analysis_json(risk_score=85)),
            production_tenant_id=TENANT,
        ),
    )
    payload = EmailAnalysisPayload.model_validate(_analysis_records(context)[0].payload)
    profile_blob = json.dumps(
        {
            "effective_profile": payload.effective_profile,
            "tenant_default_profile": payload.tenant_default_profile,
            "forced_escalation_triggers": payload.forced_escalation_triggers,
        },
        sort_keys=True,
    )
    assert "Please process attached invoice" not in profile_blob
    assert "123456789" not in profile_blob


@pytest.mark.parametrize("tenant_id", ["", " Tenant", "tenant/evil", "tenant\\evil", ".tenant"])
def test_tenant_id_validation_on_load_and_save(tmp_path, tenant_id: str) -> None:
    root = _root(tmp_path)
    with pytest.raises(GovernanceError, match="tenant_id"):
        load_tenant_profile_state(root, tenant_id)
    with pytest.raises(GovernanceError, match="tenant_id"):
        save_tenant_profile_state(
            root,
            TenantSecurityProfileState(tenant_id=tenant_id, profile="medium"),
            actor="matt",
            reason="invalid",
        )


def test_strict_disk_load_rejects_tampered_profile_file(tmp_path) -> None:
    root = _root(tmp_path)
    path = sp.tenant_profile_state_path(root, TENANT)
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "tenant_id": TENANT,
                "profile": "medium",
                "rogue_field": "evil",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(GovernanceError, match="unauthorized fields"):
        load_tenant_profile_state(root, TENANT)


def test_strict_disk_load_wraps_malformed_json_as_governance_error(tmp_path) -> None:
    root = _root(tmp_path)
    path = sp.tenant_profile_state_path(root, TENANT)
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(GovernanceError, match="not valid JSON"):
        load_tenant_profile_state(root, TENANT)


def test_profile_module_does_not_call_orchestrator_routes() -> None:
    source = inspect.getsource(sp)
    assert "submit_" not in source
    assert "RouteContext" not in source


def test_profile_module_persistent_state_is_confined_to_operator_state() -> None:
    source = inspect.getsource(sp)
    assert "operator_state" in source
    assert "security_profiles" in source
    assert ".sqlite" not in source
    assert '"production_state"' not in source


def test_operator_audit_log_accepts_profile_change_entries(tmp_path) -> None:
    path = operator_audit_log_path(_root(tmp_path))
    from core.operator_state import append_operator_audit_entry

    append_operator_audit_entry(
        path,
        OperatorAuditEntry(
            action="PROFILE_CHANGE",
            scope="NONE",
            previous_scope="NONE",
            operator="matt",
            reason="tier update",
            at=datetime.now(timezone.utc),
            tenant_id=TENANT,
            security_profile="high",
            previous_security_profile="medium",
        ),
    )
    assert read_operator_audit_log(path)[0].action == "PROFILE_CHANGE"


def test_grok_audit_runner_has_tiered_detection_intensity_target() -> None:
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "grok_audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("grok_audit_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    package = module.AUDIT_PACKAGES["tiered_detection_intensity"]
    included_paths = {entry.relative_path for entry in package.files}
    assert "4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md" in included_paths
    assert any(path.endswith("core/operator_state/security_profile.py") for path in included_paths)
    assert any(path.endswith("core/scoring/email_risk_scoring_agent.py") for path in included_paths)
    assert any(path.endswith("tests/test_security_profile.py") for path in included_paths)
