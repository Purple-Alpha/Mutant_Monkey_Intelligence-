"""Phase 1.3 Sandbox Training Pit — Month 4 gate test suite.

Implements the seven §7 gate tests from
``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` plus
the schema + helper + decision-specific drift catchers locked in by
Matt's 2026-05-21 §11 decisions:

1. ``SyntheticEmailAttackCasePayload`` + ``SYNTHETIC_EMAIL_ATTACK_CASE``
2. In-memory ``score_one_email_payload`` helper (no Blackboard writes)
3. >= 100 cases per Red profile per battery
4. Eight-mode failure taxonomy with dynamic detail stored separately
5. Bucket E mirrored cases tagged ``bucket_e_regression_probe``

Every test runs against ``tmp_path`` so no real blackboard is touched.
"""

from __future__ import annotations

import json
import typing
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.blackboard import (
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    Phase13CaseArchetype,
    Phase13CaseTag,
    Phase13FailureDetail,
    Phase13FailureMode,
    RecordType,
    SyntheticEmailAttackCasePayload,
    WeaknessReportPayload,
    read_records,
)
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.orchestrator import RouteContext
from core.orchestrator.routes import blackboard_path
from core.sandbox.red_agents import (
    RED_PROFILE_MODULES,
    bucket_e_probes,
    fake_invoice_red,
    malicious_attachment_red,
    obfuscated_url_red,
    vendor_update_red,
)
from core.sandbox.red_battery import (
    DEFAULT_CASES_PER_PROFILE,
    PHASE_1_3_AUDIT_AGENT_ID,
    PHASE_1_3_BLUE_AGENT_ID,
    PHASE_1_3_MUTATOR_AGENT_ID,
    RedBatteryConfig,
    run_red_battery_cycle,
)
from core.scoring.email_risk_scoring_agent import (
    EmailRiskScoringInMemoryFailure,
    score_one_email_payload,
)

SANDBOX_TENANT = "sandbox_default"


def _context(tmp_path: Path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _baseline_fake_llm(system_prompt: str, user_prompt: str) -> str:
    """Naive LLM: returns "safe" analysis with no flags or indicators.

    Causes every Red battery case to fail its expectations, which is
    intentional for the gate tests: it maximises coverage of the
    eight-mode failure taxonomy without requiring a sophisticated LLM
    stub. Production scoring is exercised in
    ``test_email_risk_scoring_agent.py``.
    """

    return json.dumps(
        {
            "summary": "Test baseline analysis",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 20,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 15,
                "wire_transfer_anomaly_score": 10,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 5,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "safe",
        }
    )


def _high_risk_fake_llm(system_prompt: str, user_prompt: str) -> str:
    """LLM that emits a very high risk_score (90) for ceiling-mode tests."""

    return json.dumps(
        {
            "summary": "Test high-risk analysis",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 90,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "high",
                "vendor_fraud_score": 80,
                "wire_transfer_anomaly_score": 75,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 50,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "block",
        }
    )


def _invalid_json_fake_llm(system_prompt: str, user_prompt: str) -> str:
    return "{not valid json"


def _raising_fake_llm(system_prompt: str, user_prompt: str) -> str:
    raise RuntimeError("synthetic LLM client failure")


def _valid_inbound() -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc),
        sender="alice@vendor-test.example",
        recipient="ap@northstar-customer.example",
        subject="Hello",
        body_plain="Please process the attached invoice.",
    )


# ---------------------------------------------------------------------------
# §11 Decision 1 — Schema delta
# ---------------------------------------------------------------------------


def test_record_type_includes_synthetic_email_attack_case():
    assert RecordType.SYNTHETIC_EMAIL_ATTACK_CASE.value == "synthetic_email_attack_case"
    assert RecordType.SYNTHETIC_EMAIL_ATTACK_CASE in set(RecordType)


def test_phase_13_failure_mode_literal_exact_eight_values():
    """Decision 4 — eight-mode failure taxonomy, no drift."""

    values = set(typing.get_args(Phase13FailureMode))
    assert values == {
        "analysis_failure_record_written",
        "unexpected_blue_exception",
        "risk_score_below_floor",
        "risk_score_above_ceiling",
        "missing_behavioral_flag",
        "missing_precursor_indicator",
        "recommended_action_unexpected",
        "precursor_block_missing",
    }
    assert len(values) == 8


def test_phase_13_case_tag_literal_includes_bucket_e_regression_probe():
    """Decision 5 — Bucket E mirror tag pinned in the closed enum."""

    values = set(typing.get_args(Phase13CaseTag))
    assert "bucket_e_regression_probe" in values


def test_phase_13_case_archetype_literal_pins_the_four_red_profiles():
    values = set(typing.get_args(Phase13CaseArchetype))
    assert values == {
        "fake_invoice",
        "vendor_update_pivot",
        "malicious_attachment",
        "obfuscated_url",
    }


def test_phase_13_failure_detail_separates_mode_from_dynamic_detail():
    """Decision 4 — dynamic detail lives on a sibling field, not inside the mode."""

    detail = Phase13FailureDetail(
        failure_mode="missing_behavioral_flag",
        dynamic_detail="new_banking_instructions",
    )
    assert detail.failure_mode == "missing_behavioral_flag"
    assert detail.dynamic_detail == "new_banking_instructions"
    # No colon-glued ad-hoc string sneaking back into the mode field.
    assert ":" not in detail.failure_mode

    # Dynamic detail is optional (precursor_block_missing has none).
    detail_no_dyn = Phase13FailureDetail(failure_mode="precursor_block_missing")
    assert detail_no_dyn.dynamic_detail is None


def test_synthetic_email_attack_case_rejects_non_reserved_sender_namespace():
    inbound = _valid_inbound().model_copy(update={"sender": "alice@real-domain.com"})
    with pytest.raises(ValidationError):
        SyntheticEmailAttackCasePayload(
            case_id="bad-sender",
            red_profile_id="fake_invoice_red_001",
            archetype="fake_invoice",
            attack_pattern="bad_sender_test",
            inbound=inbound,
        )


def test_synthetic_email_attack_case_rejects_non_reserved_recipient_namespace():
    inbound = _valid_inbound().model_copy(update={"recipient": "ap@northstar.com"})
    with pytest.raises(ValidationError):
        SyntheticEmailAttackCasePayload(
            case_id="bad-recipient",
            red_profile_id="fake_invoice_red_001",
            archetype="fake_invoice",
            attack_pattern="bad_recipient_test",
            inbound=inbound,
        )


def test_synthetic_email_attack_case_round_trips_through_pydantic_validation():
    case = SyntheticEmailAttackCasePayload(
        case_id="round-trip",
        red_profile_id="fake_invoice_red_001",
        archetype="fake_invoice",
        attack_pattern="round_trip_test",
        inbound=_valid_inbound(),
        case_tags=("bucket_e_regression_probe",),
        expected_min_risk_score=60,
        expected_recommended_actions=("needs_review", "block"),
        expected_behavioral_flags=("new_banking_instructions",),
        expects_precursor_block=True,
    )
    dumped = case.model_dump(mode="json")
    rebuilt = SyntheticEmailAttackCasePayload.model_validate(dumped)
    assert rebuilt == case


def test_synthetic_email_attack_case_rejects_inverted_score_bounds():
    with pytest.raises(ValidationError):
        SyntheticEmailAttackCasePayload(
            case_id="inverted-bounds",
            red_profile_id="fake_invoice_red_001",
            archetype="fake_invoice",
            attack_pattern="inverted_bounds_test",
            inbound=_valid_inbound(),
            expected_min_risk_score=80,
            expected_max_risk_score=50,
        )


# ---------------------------------------------------------------------------
# §11 Decision 2 — In-memory ``score_one_email_payload`` helper
# ---------------------------------------------------------------------------


def test_score_one_email_payload_returns_analysis_payload_on_success():
    result = score_one_email_payload(
        _valid_inbound(), llm_client=_baseline_fake_llm
    )
    assert isinstance(result, EmailAnalysisPayload)
    assert result.risk_analysis.risk_score == 20
    # Precursor overlay still applied — block must be present (empty fields).
    assert result.ransomware_precursor_analysis is not None


def test_score_one_email_payload_returns_failure_on_invalid_json():
    result = score_one_email_payload(
        _valid_inbound(), llm_client=_invalid_json_fake_llm
    )
    assert isinstance(result, EmailRiskScoringInMemoryFailure)
    assert result.failure_reason == "invalid_json"
    assert result.raw_output == "{not valid json"


def test_score_one_email_payload_returns_failure_on_llm_exception():
    result = score_one_email_payload(
        _valid_inbound(), llm_client=_raising_fake_llm
    )
    assert isinstance(result, EmailRiskScoringInMemoryFailure)
    assert result.failure_reason.startswith("llm_client_raised:RuntimeError")


def test_score_one_email_payload_never_writes_to_blackboard(tmp_path):
    """§7 gate test — in-memory helper has zero side effects on disk."""

    score_one_email_payload(_valid_inbound(), llm_client=_baseline_fake_llm)
    assert not (tmp_path / "blackboard").exists()


def test_score_one_email_payload_can_disable_precursor_overlay():
    result = score_one_email_payload(
        _valid_inbound(),
        llm_client=_baseline_fake_llm,
        enable_ransomware_precursor_overlay=False,
    )
    assert isinstance(result, EmailAnalysisPayload)
    assert result.ransomware_precursor_analysis is None


# ---------------------------------------------------------------------------
# §11 Decision 3 — >= 100 cases per Red profile per battery
# ---------------------------------------------------------------------------


def test_each_red_profile_emits_at_least_100_cases_per_battery():
    for module in RED_PROFILE_MODULES:
        cases = module.generate_cases(seed=0, count=DEFAULT_CASES_PER_PROFILE)
        assert len(cases) >= 100, module.RED_PROFILE_ID
        assert module.case_universe_size() >= 100, module.RED_PROFILE_ID


def test_each_red_profile_has_unique_case_ids():
    for module in RED_PROFILE_MODULES:
        cases = module.generate_cases(seed=0, count=DEFAULT_CASES_PER_PROFILE)
        case_ids = [c.case_id for c in cases]
        assert len(case_ids) == len(set(case_ids)), module.RED_PROFILE_ID


def test_red_profile_generation_is_byte_deterministic_across_runs():
    """§7 gate test — same seed yields identical payload JSON."""

    for module in RED_PROFILE_MODULES:
        first = module.generate_cases(seed=42, count=DEFAULT_CASES_PER_PROFILE)
        second = module.generate_cases(seed=42, count=DEFAULT_CASES_PER_PROFILE)
        first_json = [c.model_dump_json() for c in first]
        second_json = [c.model_dump_json() for c in second]
        assert first_json == second_json, module.RED_PROFILE_ID


# Per-archetype enum-coverage drift catcher (§7 gate test #2).
_FAKE_INVOICE_DRIVEN_FLAGS = frozenset(
    {
        "first_time_sender_with_financial_ask",
        "new_banking_instructions",
        "urgency_paired_with_finance",
        "lookalike_sender_domain",
        "unusual_dollar_amount",
    }
)

_VENDOR_UPDATE_DRIVEN_FLAGS = frozenset(
    {
        "new_banking_instructions",
        "first_time_sender_with_financial_ask",
        "reply_to_diverges_from_from",
        "urgency_paired_with_finance",
        "out_of_band_pressure",
        "mismatched_invoice_vendor_name",
    }
)

_MALICIOUS_ATTACHMENT_DRIVEN_INDICATORS = frozenset(
    {
        "executable_attachment",
        "iso_or_disk_image_attachment",
        "macro_enabled_office_document",
        "double_extension_attachment",
        "encrypted_archive_attachment",
        "html_smuggling_attachment",
    }
)

_OBFUSCATED_URL_DRIVEN_INDICATORS = frozenset(
    {
        "punycode_url_present",
        "homoglyph_url_present",
        "url_shortener_present",
        "credential_bearing_url",
        "suspicious_tld_present",
        "ip_address_url_present",
        "login_path_url_present",
    }
)


def test_fake_invoice_red_covers_every_locked_flag_it_drives():
    cases = fake_invoice_red.generate_cases(seed=0, count=DEFAULT_CASES_PER_PROFILE)
    surfaced: set[str] = set()
    for c in cases:
        surfaced.update(c.expected_behavioral_flags)
    assert _FAKE_INVOICE_DRIVEN_FLAGS <= surfaced


def test_vendor_update_red_covers_every_locked_flag_it_drives():
    cases = vendor_update_red.generate_cases(seed=0, count=DEFAULT_CASES_PER_PROFILE)
    surfaced: set[str] = set()
    for c in cases:
        surfaced.update(c.expected_behavioral_flags)
    assert _VENDOR_UPDATE_DRIVEN_FLAGS <= surfaced


def test_malicious_attachment_red_covers_every_locked_indicator_it_drives():
    cases = malicious_attachment_red.generate_cases(
        seed=0, count=DEFAULT_CASES_PER_PROFILE
    )
    surfaced: set[str] = set()
    for c in cases:
        surfaced.update(c.expected_precursor_indicators)
    assert _MALICIOUS_ATTACHMENT_DRIVEN_INDICATORS <= surfaced


def test_obfuscated_url_red_covers_every_locked_indicator_it_drives():
    cases = obfuscated_url_red.generate_cases(seed=0, count=DEFAULT_CASES_PER_PROFILE)
    surfaced: set[str] = set()
    for c in cases:
        surfaced.update(c.expected_precursor_indicators)
    assert _OBFUSCATED_URL_DRIVEN_INDICATORS <= surfaced


# ---------------------------------------------------------------------------
# §11 Decision 5 — Bucket E mirror cases tagged ``bucket_e_regression_probe``
# ---------------------------------------------------------------------------


def test_bucket_e_probes_are_all_tagged_bucket_e_regression_probe():
    probes = bucket_e_probes.generate_bucket_e_probes()
    assert len(probes) == 4
    for probe in probes:
        assert "bucket_e_regression_probe" in probe.case_tags


def test_bucket_e_probes_distribute_across_red_profiles():
    probes = bucket_e_probes.generate_bucket_e_probes()
    profile_ids = {p.red_profile_id for p in probes}
    assert profile_ids == {"fake_invoice_red_001", "vendor_update_red_001"}


def test_bucket_e_probes_match_original_case_ids():
    probes = bucket_e_probes.generate_bucket_e_probes()
    case_ids = {p.case_id for p in probes}
    assert case_ids == {
        "bucket-e-vf-002-mirror",
        "bucket-e-vf-005-mirror",
        "bucket-e-ei-005-mirror",
        "bucket-e-wt-004-mirror",
    }


# ---------------------------------------------------------------------------
# §7 gate tests — Red battery cycle end-to-end
# ---------------------------------------------------------------------------


def _small_battery_config(llm_client) -> RedBatteryConfig:
    """Five cases per profile keeps tests fast; full counts are covered above."""

    return RedBatteryConfig(
        llm_client=llm_client,
        sandbox_tenant_id=SANDBOX_TENANT,
        cases_per_profile=5,
        seed=0,
        include_bucket_e_probes=True,
    )


def test_red_battery_writes_synthetic_cases_mutant_eval_audit_and_weakness_per_profile(
    tmp_path,
):
    """§7 gate test #1 — every profile produces the full four-record signature."""

    context = _context(tmp_path)
    result = run_red_battery_cycle(
        context, config=_small_battery_config(_baseline_fake_llm)
    )

    assert [p.red_profile_id for p in result.profile_results] == [
        "fake_invoice_red_001",
        "vendor_update_red_001",
        "malicious_attachment_red_001",
        "obfuscated_url_red_001",
    ]

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    type_counts: Counter[str] = Counter(r.record_type.value for r in records)
    expected_cases = 5 * 4 + 4  # 5 per profile + 4 Bucket E probes
    assert type_counts["synthetic_email_attack_case"] == expected_cases
    assert type_counts["mutant_evaluation"] == expected_cases
    assert type_counts["audit_verdict"] == expected_cases
    assert type_counts["weakness_report"] == 4


def test_red_battery_failure_details_carry_typed_mode_and_dynamic_detail_separately(
    tmp_path,
):
    """§7 gate test #2 + Decision 4 — eight-mode taxonomy with dynamic detail split."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    mutant_evals = [
        r for r in records if r.record_type == RecordType.MUTANT_EVALUATION
    ]
    assert mutant_evals

    seen_modes: set[str] = set()
    for record in mutant_evals:
        details_payload = record.payload["phase_1_3_failure_details"]
        for entry in details_payload:
            seen_modes.add(entry["failure_mode"])
            # Mode is one of the eight Literal values, never colon-glued.
            assert ":" not in entry["failure_mode"]
            # Dynamic detail is either None or a stable string.
            assert (
                entry["dynamic_detail"] is None
                or isinstance(entry["dynamic_detail"], str)
            )

    # The naive baseline LLM should at minimum surface these three modes
    # (risk_score below floor, missing behavioral flag, recommended action
    # unexpected — every fake_invoice / vendor_update case fails all three).
    assert {
        "risk_score_below_floor",
        "missing_behavioral_flag",
        "recommended_action_unexpected",
    } <= seen_modes


def test_red_battery_risk_score_above_ceiling_fires_for_high_risk_llm(tmp_path):
    """High-risk LLM on the wt-004 mirror case (max=75) trips the ceiling mode."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_high_risk_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    seen_modes: set[str] = set()
    for record in records:
        if record.record_type != RecordType.MUTANT_EVALUATION:
            continue
        for entry in record.payload["phase_1_3_failure_details"]:
            seen_modes.add(entry["failure_mode"])
    assert "risk_score_above_ceiling" in seen_modes


def test_red_battery_precursor_block_missing_fires_when_overlay_disabled(tmp_path):
    """``precursor_block_missing`` mode is exercised when the overlay is off."""

    context = _context(tmp_path)
    config = RedBatteryConfig(
        llm_client=_baseline_fake_llm,
        sandbox_tenant_id=SANDBOX_TENANT,
        cases_per_profile=3,
        seed=0,
        include_bucket_e_probes=False,
        enable_ransomware_precursor_overlay=False,
    )
    run_red_battery_cycle(context, config=config)

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    seen_modes: set[str] = set()
    for record in records:
        if record.record_type != RecordType.MUTANT_EVALUATION:
            continue
        for entry in record.payload["phase_1_3_failure_details"]:
            seen_modes.add(entry["failure_mode"])
    assert "precursor_block_missing" in seen_modes


def test_red_battery_analysis_failure_record_written_fires_on_invalid_json(tmp_path):
    context = _context(tmp_path)
    run_red_battery_cycle(
        context, config=_small_battery_config(_invalid_json_fake_llm)
    )

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    seen_modes: set[str] = set()
    for record in records:
        if record.record_type != RecordType.MUTANT_EVALUATION:
            continue
        for entry in record.payload["phase_1_3_failure_details"]:
            seen_modes.add(entry["failure_mode"])
    assert "analysis_failure_record_written" in seen_modes


def test_red_battery_kill_switch_aborts_before_writing_any_record(tmp_path):
    """§7 gate test #4 — sandbox kill-switch is honored at the boundary."""

    context = _context(tmp_path)
    engage_kill_switch(
        context.blackboard_root,
        scope="SANDBOX_ONLY",
        reason="halt phase 1.3",
        operator="matt",
    )

    with pytest.raises(KillSwitchEngaged):
        run_red_battery_cycle(
            context, config=_small_battery_config(_baseline_fake_llm)
        )

    sandbox_path = blackboard_path(
        context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT
    )
    if sandbox_path.exists():
        records = read_records(sandbox_path)
        assert all(r.record_type != RecordType.SYNTHETIC_EMAIL_ATTACK_CASE for r in records)


def test_red_battery_never_writes_outside_sandbox_environment(tmp_path):
    """§7 gate test #5 — no production-side blackboard touched."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    production_dir = context.blackboard_root / Environment.PRODUCTION.value
    assert not production_dir.exists()

    sandbox_path = blackboard_path(
        context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT
    )
    records = read_records(sandbox_path)
    for record in records:
        assert record.environment == Environment.SANDBOX


def test_red_battery_does_not_emit_policy_update_records(tmp_path):
    """§7 gate test #6 — promotion boundary stays in Month 5."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    for record in records:
        assert record.record_type != RecordType.POLICY_UPDATE


def test_red_battery_weakness_reports_have_raw_tenant_data_removed_true(tmp_path):
    """§7 gate test #7 — weakness-report payload preserves anonymisation."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    weakness_records = [
        r for r in records if r.record_type == RecordType.WEAKNESS_REPORT
    ]
    assert len(weakness_records) == 4
    for record in weakness_records:
        payload = WeaknessReportPayload.model_validate(record.payload)
        assert payload.raw_tenant_data_removed is True
        assert payload.weakness_kind.startswith("phase_1_3_red_profile:")
        assert "phase_1_3:" in payload.anonymized_pattern


def test_red_battery_never_writes_email_inbound_records(tmp_path):
    """Decision 2 — in-memory Blue invocation; no EMAIL_INBOUND noise."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    for record in records:
        assert record.record_type != RecordType.EMAIL_INBOUND
        assert record.record_type != RecordType.EMAIL_ANALYSIS
        assert record.record_type != RecordType.EMAIL_ANALYSIS_FAILURE


def test_red_battery_routes_each_record_under_correct_agent_id(tmp_path):
    """Synthetic cases under the Red profile id; eval / weakness under mutator."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    red_profile_ids = {m.RED_PROFILE_ID for m in RED_PROFILE_MODULES}
    for record in records:
        if record.record_type == RecordType.SYNTHETIC_EMAIL_ATTACK_CASE:
            assert record.source_agent in red_profile_ids
        elif record.record_type == RecordType.MUTANT_EVALUATION:
            assert record.source_agent == PHASE_1_3_MUTATOR_AGENT_ID
        elif record.record_type == RecordType.WEAKNESS_REPORT:
            assert record.source_agent == PHASE_1_3_MUTATOR_AGENT_ID
        elif record.record_type == RecordType.AUDIT_VERDICT:
            assert record.source_agent == PHASE_1_3_AUDIT_AGENT_ID


def test_red_battery_includes_bucket_e_probes_when_enabled(tmp_path):
    """Decision 5 — Bucket E probes flow through when the flag is on."""

    context = _context(tmp_path)
    result = run_red_battery_cycle(
        context, config=_small_battery_config(_baseline_fake_llm)
    )
    assert set(result.bucket_e_case_ids) == {
        "bucket-e-vf-002-mirror",
        "bucket-e-vf-005-mirror",
        "bucket-e-ei-005-mirror",
        "bucket-e-wt-004-mirror",
    }


def test_red_battery_excludes_bucket_e_probes_when_disabled(tmp_path):
    context = _context(tmp_path)
    config = RedBatteryConfig(
        llm_client=_baseline_fake_llm,
        sandbox_tenant_id=SANDBOX_TENANT,
        cases_per_profile=3,
        seed=0,
        include_bucket_e_probes=False,
    )
    result = run_red_battery_cycle(context, config=config)
    assert result.bucket_e_case_ids == []


def test_red_battery_baseline_agent_id_is_pinned_to_production_scoring_agent(tmp_path):
    """Mutant evaluations reference the production scoring agent id as baseline."""

    context = _context(tmp_path)
    run_red_battery_cycle(context, config=_small_battery_config(_baseline_fake_llm))

    records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, SANDBOX_TENANT)
    )
    for record in records:
        if record.record_type != RecordType.MUTANT_EVALUATION:
            continue
        assert record.payload["baseline_agent_id"] == PHASE_1_3_BLUE_AGENT_ID
