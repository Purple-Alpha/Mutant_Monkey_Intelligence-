"""Smoke tests for the Phase 1.1 fraud eval harness machinery.

These tests verify the harness *plumbing* — loader, runner, report
aggregation, markdown rendering, pass-gate logic, llm-safe mode, live-
client dispatch, and CLI entry point — using deterministic fake LLM
clients. They explicitly do **not** verify scoring quality against a
real LLM; that gate is run offline per the deep dive §4.5 and landed as
an activity-log artifact (see
``4. Product_Roadmap/Live_LLM_Eval_Runbook.md``).
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import get_args

import pytest

from core.scoring.eval import (
    DEFAULT_DATASET_PATH,
    PASS_GATE_MAX_FPR_ON_LEGIT,
    PASS_GATE_MIN_PER_SUBCATEGORY_RECALL,
    PASS_GATE_MIN_PRECISION_ON_FRAUD,
    SUPPORTED_PROVIDERS,
    UNSAFE_PATTERNS,
    EvalCase,
    EvalCaseExpected,
    EvalCaseResult,
    EvalReport,
    EvalSubcategory,
    EvalSubcategoryStats,
    LLMSafeClientConfig,
    LLMSafetyError,
    LiveClientImportError,
    assert_dataset_path_is_allowlisted,
    build_live_client,
    build_llm_safe_client,
    default_usage_log_path,
    load_dataset,
    read_usage_log,
    resolve_api_key,
    run_eval,
    scan_dataset_for_unsafe_terms,
    strip_markdown_code_fences,
)
from core.scoring.eval.dataset import EvalDatasetError
from core.scoring.eval.fraud_eval_harness import main as harness_main
from core.scoring.email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
)


def _passing_client_for(case: EvalCase):
    """Build a fake LLM client whose JSON satisfies the case's expected bounds."""

    risk_score = _within(case.expected.min_risk_score, case.expected.max_risk_score, default=50)
    vendor = _within(
        case.expected.min_vendor_fraud_score,
        case.expected.max_vendor_fraud_score,
        default=50,
    )
    wire = _within(
        case.expected.min_wire_transfer_anomaly_score,
        case.expected.max_wire_transfer_anomaly_score,
        default=50,
    )
    invoice = _within(
        case.expected.min_invoice_authenticity_score,
        case.expected.max_invoice_authenticity_score,
        default=None,
    )
    action = (
        case.expected.recommended_action_in[0]
        if case.expected.recommended_action_in
        else "needs_review"
    )
    flags = list(case.expected.behavioral_deviation_flags or ())
    payload = json.dumps(
        {
            "summary": f"synthetic analysis for {case.case_id}",
            "action_items": [],
            "risk_analysis": {
                "risk_score": risk_score,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "medium",
                "vendor_fraud_score": vendor,
                "wire_transfer_anomaly_score": wire,
                "invoice_authenticity_score": invoice,
                "behavioral_deviation_flags": flags,
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 30,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": action,
        }
    )

    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        json.loads(user_prompt)
        return payload

    return _client


def _within(lo: int | None, hi: int | None, *, default: int | None) -> int | None:
    if lo is not None and hi is not None:
        return (lo + hi) // 2
    if lo is not None:
        return lo
    if hi is not None:
        return hi
    return default


def test_default_dataset_loads_and_has_all_required_shape():
    cases = load_dataset()
    assert len(cases) >= 3
    seen_labels = {c.label for c in cases}
    assert seen_labels == {"fraud", "legit"}
    for case in cases:
        assert case.case_id
        assert case.subcategory in get_args(EvalSubcategory)
        assert case.email.sender
        assert case.email.recipient


def test_load_dataset_rejects_unknown_subcategory(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        json.dumps(
            {
                "case_id": "x-1",
                "label": "fraud",
                "subcategory": "freeform_subcategory",
                "email": {
                    "received_at": "2026-01-01T00:00:00+00:00",
                    "sender": "a@b.example",
                    "recipient": "c@d.example",
                    "body_plain": "hi",
                },
                "expected": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(EvalDatasetError, match="subcategory"):
        load_dataset(bad)


def test_load_dataset_rejects_unknown_top_level_field(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        json.dumps(
            {
                "case_id": "x-1",
                "label": "fraud",
                "subcategory": "vendor_invoice_fraud",
                "email": {
                    "received_at": "2026-01-01T00:00:00+00:00",
                    "sender": "a@b.example",
                    "recipient": "c@d.example",
                    "body_plain": "hi",
                },
                "expected": {},
                "smuggled_field": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(EvalDatasetError, match="unexpected fields"):
        load_dataset(bad)


def test_load_dataset_rejects_recommended_action_outside_enum(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        json.dumps(
            {
                "case_id": "x-1",
                "label": "fraud",
                "subcategory": "vendor_invoice_fraud",
                "email": {
                    "received_at": "2026-01-01T00:00:00+00:00",
                    "sender": "a@b.example",
                    "recipient": "c@d.example",
                    "body_plain": "hi",
                },
                "expected": {"recommended_action_in": ["quarantine"]},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(EvalDatasetError, match="quarantine"):
        load_dataset(bad)


def test_load_dataset_rejects_out_of_range_bound(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        json.dumps(
            {
                "case_id": "x-1",
                "label": "fraud",
                "subcategory": "vendor_invoice_fraud",
                "email": {
                    "received_at": "2026-01-01T00:00:00+00:00",
                    "sender": "a@b.example",
                    "recipient": "c@d.example",
                    "body_plain": "hi",
                },
                "expected": {"min_risk_score": 150},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(EvalDatasetError, match=r"\[0, 100\]"):
        load_dataset(bad)


def test_run_eval_passes_when_client_satisfies_bounds():
    cases = load_dataset()
    # Use a different client per case so each case gets a tailored passing response.
    # The runner only calls the client per case, so collecting one EvalReport that
    # has one passing-result per case requires running cases one at a time.
    aggregate_results = []
    for case in cases:
        client = _passing_client_for(case)
        report = run_eval([case], llm_client=client)
        aggregate_results.extend(report.results)
        assert report.passed == report.total == 1, (
            f"case {case.case_id} did not pass under tailored client: "
            f"{report.results[0].failed_assertions or report.results[0].failure_reason}"
        )

    assert all(r.passed for r in aggregate_results)


def test_run_eval_marks_case_failed_when_score_outside_bounds():
    cases = load_dataset()
    case = next(c for c in cases if c.case_id == "vf-001")

    def _failing_client(system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "summary": "deliberate under-scoring",
                "action_items": [],
                "risk_analysis": {
                    "risk_score": 10,
                    "risk_factors": [],
                    "phishing_signals": [],
                    "urgency_signals": [],
                    "financial_risk": "low",
                    "vendor_fraud_score": 5,
                    "wire_transfer_anomaly_score": 5,
                    "invoice_authenticity_score": 90,
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

    report = run_eval([case], llm_client=_failing_client)
    assert report.passed == 0
    failed = report.results[0].failed_assertions
    assert any("risk_score" in f for f in failed)
    assert any("vendor_fraud_score" in f for f in failed)
    assert any("wire_transfer_anomaly_score" in f for f in failed)
    assert any("invoice_authenticity_score" in f for f in failed)
    assert any("recommended_action" in f for f in failed)


def test_run_eval_handles_invalid_json_as_failure():
    cases = load_dataset()
    case = cases[0]

    def _broken_client(system_prompt: str, user_prompt: str) -> str:
        return "not json {"

    report = run_eval([case], llm_client=_broken_client)
    assert report.passed == 0
    assert report.results[0].failure_reason is not None
    assert "invalid_json" in report.results[0].failure_reason


def test_run_eval_handles_schema_mismatch_as_failure():
    cases = load_dataset()
    case = cases[0]

    def _wrong_shape(system_prompt: str, user_prompt: str) -> str:
        return json.dumps({"summary": "missing required fields"})

    report = run_eval([case], llm_client=_wrong_shape)
    assert report.passed == 0
    assert report.results[0].failure_reason is not None
    assert "schema_mismatch" in report.results[0].failure_reason


def test_run_eval_handles_llm_exception_as_failure():
    cases = load_dataset()
    case = cases[0]

    def _exploding(system_prompt: str, user_prompt: str) -> str:
        raise RuntimeError("model went down")

    report = run_eval([case], llm_client=_exploding)
    assert report.passed == 0
    assert report.results[0].failure_reason is not None
    assert "llm_client_raised" in report.results[0].failure_reason


def test_eval_report_markdown_table_contains_per_subcategory_rows():
    cases = load_dataset()
    # All passing under tailored clients per case.
    results = []
    for case in cases:
        client = _passing_client_for(case)
        results.extend(run_eval([case], llm_client=client).results)

    from core.scoring.eval.runner import _aggregate

    report = _aggregate(results)
    table = report.markdown_table()
    assert "## Fraud Eval Report" in table
    assert "| Subcategory | Total | Passed | Recall |" in table
    for case in cases:
        assert case.subcategory in table


def test_harness_cli_dry_run_loads_dataset_and_exits():
    """End-to-end CLI smoke: --dry-run loads the dataset and prints a markdown table."""
    import contextlib

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = harness_main(["--dry-run"])

    output = buffer.getvalue()
    assert "## Fraud Eval Report" in output
    assert "| Subcategory |" in output
    # --dry-run uses a stub that returns risk_score=50 etc., which may not satisfy
    # every case's bounds, so exit_code may be 1 (some cases fail). We only assert
    # the harness ran end-to-end and produced output.
    assert exit_code in (0, 1)


def test_harness_cli_default_client_raises_not_implemented():
    """Without --dry-run, the default CLI client raises NotImplementedError on the
    first case, but the runner catches it as ``llm_client_raised`` so the CLI still
    exits cleanly with code 1."""
    import contextlib

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = harness_main([])

    output = buffer.getvalue()
    assert "## Fraud Eval Report" in output
    assert exit_code == 1


def test_default_dataset_path_points_at_shipped_jsonl():
    assert DEFAULT_DATASET_PATH.exists()
    assert DEFAULT_DATASET_PATH.suffix == ".jsonl"
    assert DEFAULT_DATASET_PATH.parent.name == "eval"


# ----------------------------------------------------------------------
# behavioral_deviation_flags expectation contract
# ----------------------------------------------------------------------
#
# Contract is required-subset + optional forbidden set (post-Month-2
# calibration). Prior contract used strict set equality, which the live
# Grok diagnostic showed was over-brittle: extras emitted by the model
# were not actually harmful (precision and FPR were perfect) while the
# strict-equality contract was blocking otherwise correct fraud
# detections on subtle cases. The new contract is:
#
# - ``behavioral_deviation_flags`` (required-subset): every flag listed
#   must appear in the agent's emitted set. Extras do NOT fail the case.
# - ``forbidden_behavioral_deviation_flags`` (optional explicit
#   forbidden set): if any flag here is emitted, the case fails.
# - The two tuples may not overlap on the same case (loader rejects).
#
# The Month 2 audit gap (`unusual_unicode_obfuscation` must still be
# emitted on the three Unicode cases) is preserved by the required
# subset, just not by the no-extras rule.


def _dataset_row_dict_for(case_id: str, **expected_overrides) -> dict:
    """Construct a minimal valid dataset row for the bd-flags loader tests."""

    return {
        "case_id": case_id,
        "label": "fraud",
        "subcategory": "vendor_invoice_fraud",
        "email": {
            "received_at": "2026-01-01T00:00:00+00:00",
            "sender": "a@example.test",
            "recipient": "b@example.test",
            "body_plain": "synthetic body",
        },
        "expected": dict(expected_overrides),
    }


def test_loader_accepts_missing_behavioral_deviation_flags_as_none(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(json.dumps(_dataset_row_dict_for("x-1")) + "\n", encoding="utf-8")
    cases = load_dataset(path)
    assert cases[0].expected.behavioral_deviation_flags is None


def test_loader_accepts_empty_behavioral_deviation_flags_list(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for("x-1", behavioral_deviation_flags=[])
        ) + "\n",
        encoding="utf-8",
    )
    cases = load_dataset(path)
    # Empty tuple is meaningfully different from None: the case asserts
    # the agent must emit zero flags.
    assert cases[0].expected.behavioral_deviation_flags == ()


def test_loader_accepts_valid_behavioral_deviation_flags_list(tmp_path):
    path = tmp_path / "d.jsonl"
    flags = ["unusual_unicode_obfuscation", "first_time_sender_with_financial_ask"]
    path.write_text(
        json.dumps(
            _dataset_row_dict_for("x-1", behavioral_deviation_flags=flags)
        ) + "\n",
        encoding="utf-8",
    )
    cases = load_dataset(path)
    assert cases[0].expected.behavioral_deviation_flags == tuple(flags)


def test_loader_rejects_unknown_behavioral_deviation_flag(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1", behavioral_deviation_flags=["totally_made_up_flag"]
            )
        ) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvalDatasetError, match="totally_made_up_flag"):
        load_dataset(path)


def test_loader_rejects_non_list_behavioral_deviation_flags(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1", behavioral_deviation_flags="unusual_unicode_obfuscation"
            )
        ) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvalDatasetError, match="must be a list"):
        load_dataset(path)


def test_loader_rejects_non_string_entry_in_behavioral_deviation_flags(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1", behavioral_deviation_flags=["urgency_paired_with_finance", 123]
            )
        ) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvalDatasetError, match="must be a string"):
        load_dataset(path)


def test_loader_rejects_duplicate_behavioral_deviation_flag(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1",
                behavioral_deviation_flags=[
                    "unusual_unicode_obfuscation",
                    "unusual_unicode_obfuscation",
                ],
            )
        ) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvalDatasetError, match="duplicate"):
        load_dataset(path)


def _emit_analysis_with_flags(flags: list[str], *, case_id: str):
    """Build a fake LLM client whose JSON satisfies generic bounds with the
    given behavioral_deviation_flags. The shipped scoring fields are set
    to widely-permissive midpoints so the test isolates flag-set behavior."""

    payload = json.dumps(
        {
            "summary": f"synthetic analysis for {case_id}",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 75,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "medium",
                "vendor_fraud_score": 75,
                "wire_transfer_anomaly_score": 75,
                "invoice_authenticity_score": 30,
                "behavioral_deviation_flags": flags,
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 50,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "block",
        }
    )

    def _client(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        return payload

    return _client


def _ia_003_case():
    cases = load_dataset()
    return next(c for c in cases if c.case_id == "ia-003")


def test_runner_passes_when_emitted_flags_match_expected_exactly():
    case = _ia_003_case()
    expected_flags = list(case.expected.behavioral_deviation_flags)
    client = _emit_analysis_with_flags(expected_flags, case_id=case.case_id)
    report = run_eval([case], llm_client=client)
    assert report.passed == 1
    assert report.results[0].failed_assertions == []


def test_runner_passes_when_emitted_flags_match_in_different_order():
    case = _ia_003_case()
    expected_flags = list(reversed(list(case.expected.behavioral_deviation_flags)))
    client = _emit_analysis_with_flags(expected_flags, case_id=case.case_id)
    report = run_eval([case], llm_client=client)
    assert report.passed == 1
    assert report.results[0].failed_assertions == []


def test_runner_fails_when_required_flag_is_missing():
    case = _ia_003_case()
    # Drop the Unicode flag — this is exactly the audit-gap regression.
    emitted = [
        f
        for f in case.expected.behavioral_deviation_flags
        if f != "unusual_unicode_obfuscation"
    ]
    client = _emit_analysis_with_flags(emitted, case_id=case.case_id)
    report = run_eval([case], llm_client=client)
    assert report.passed == 0
    failed = report.results[0].failed_assertions
    assert any(
        "behavioral_deviation_flags" in f
        and "missing required" in f
        and "unusual_unicode_obfuscation" in f
        for f in failed
    ), failed


def test_runner_passes_when_extra_flag_is_emitted_outside_forbidden_set():
    """Post-calibration: extras do NOT fail the case unless explicitly forbidden."""

    case = _ia_003_case()
    expected_flags = list(case.expected.behavioral_deviation_flags)
    # Add a flag the case did not expect; the new contract permits this
    # because the case has no forbidden_behavioral_deviation_flags pin.
    emitted = expected_flags + ["new_banking_instructions"]
    client = _emit_analysis_with_flags(emitted, case_id=case.case_id)
    report = run_eval([case], llm_client=client)
    assert report.passed == 1, report.results[0].failed_assertions
    for msg in report.results[0].failed_assertions:
        assert "behavioral_deviation_flags" not in msg, msg


def test_runner_skips_flag_check_when_expected_is_none(tmp_path):
    # Build a tiny dataset with no behavioral_deviation_flags field; the
    # runner must NOT assert anything about the agent's flag emission.
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(_dataset_row_dict_for("x-1")) + "\n",
        encoding="utf-8",
    )
    case = load_dataset(path)[0]
    # Agent emits two arbitrary flags; assertion should not fire.
    client = _emit_analysis_with_flags(
        ["urgency_paired_with_finance", "out_of_band_pressure"],
        case_id=case.case_id,
    )
    report = run_eval([case], llm_client=client)
    # Flag check is silent; the case may still fail on score bounds, so
    # we only assert that no failure mentions behavioral_deviation_flags.
    for result in report.results:
        for msg in result.failed_assertions:
            assert "behavioral_deviation_flags" not in msg, msg


def test_runner_emits_required_only_message_when_no_forbidden_violation():
    """Required-subset and forbidden are reported separately, not merged."""

    case = _ia_003_case()
    # Emit zero flags so we get a missing-required failure and confirm
    # the message format is the new "missing required" wording.
    client = _emit_analysis_with_flags([], case_id=case.case_id)
    report = run_eval([case], llm_client=client)
    failed = report.results[0].failed_assertions
    flag_messages = [f for f in failed if "behavioral_deviation_flags" in f]
    assert len(flag_messages) == 1, flag_messages
    msg = flag_messages[0]
    assert "missing required" in msg
    assert "emitted forbidden" not in msg


# ----------------------------------------------------------------------
# forbidden_behavioral_deviation_flags contract (post-Month-2 calibration)
# ----------------------------------------------------------------------


def test_loader_accepts_missing_forbidden_behavioral_deviation_flags_as_none(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(json.dumps(_dataset_row_dict_for("x-1")) + "\n", encoding="utf-8")
    cases = load_dataset(path)
    assert cases[0].expected.forbidden_behavioral_deviation_flags is None


def test_loader_accepts_valid_forbidden_behavioral_deviation_flags_list(tmp_path):
    path = tmp_path / "d.jsonl"
    forbidden = ["urgency_paired_with_finance", "new_banking_instructions"]
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1", forbidden_behavioral_deviation_flags=forbidden
            )
        )
        + "\n",
        encoding="utf-8",
    )
    cases = load_dataset(path)
    assert cases[0].expected.forbidden_behavioral_deviation_flags == tuple(forbidden)


def test_loader_rejects_unknown_forbidden_behavioral_deviation_flag(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1", forbidden_behavioral_deviation_flags=["totally_made_up"]
            )
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvalDatasetError, match="totally_made_up"):
        load_dataset(path)


def test_loader_rejects_overlap_between_required_and_forbidden(tmp_path):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1",
                behavioral_deviation_flags=["new_banking_instructions"],
                forbidden_behavioral_deviation_flags=["new_banking_instructions"],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        EvalDatasetError,
        match="overlap on \\['new_banking_instructions'\\]",
    ):
        load_dataset(path)


def _case_with_forbidden_flags(tmp_path: Path, forbidden: list[str]):
    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1",
                behavioral_deviation_flags=[],
                forbidden_behavioral_deviation_flags=forbidden,
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return load_dataset(path)[0]


def test_runner_fails_when_forbidden_flag_is_emitted(tmp_path):
    case = _case_with_forbidden_flags(tmp_path, ["new_banking_instructions"])
    client = _emit_analysis_with_flags(
        ["new_banking_instructions"], case_id=case.case_id
    )
    report = run_eval([case], llm_client=client)
    assert report.passed == 0
    failed = report.results[0].failed_assertions
    assert any(
        "behavioral_deviation_flags" in f
        and "emitted forbidden" in f
        and "new_banking_instructions" in f
        for f in failed
    ), failed


def test_runner_passes_when_forbidden_set_is_disjoint_from_emitted(tmp_path):
    case = _case_with_forbidden_flags(tmp_path, ["new_banking_instructions"])
    client = _emit_analysis_with_flags(
        ["urgency_paired_with_finance"], case_id=case.case_id
    )
    report = run_eval([case], llm_client=client)
    # The flag check passes (no forbidden flag emitted); other bound
    # checks may still pass or fail depending on the synthetic scores,
    # but no flag-related assertion should fire.
    for msg in report.results[0].failed_assertions:
        assert "behavioral_deviation_flags" not in msg, msg


def test_runner_emits_separate_messages_for_missing_required_and_forbidden(tmp_path):
    """Required and forbidden produce TWO distinct failure messages."""

    path = tmp_path / "d.jsonl"
    path.write_text(
        json.dumps(
            _dataset_row_dict_for(
                "x-1",
                behavioral_deviation_flags=["urgency_paired_with_finance"],
                forbidden_behavioral_deviation_flags=["new_banking_instructions"],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    case = load_dataset(path)[0]
    # Emit the forbidden flag and OMIT the required one.
    client = _emit_analysis_with_flags(
        ["new_banking_instructions"], case_id=case.case_id
    )
    report = run_eval([case], llm_client=client)
    failed = report.results[0].failed_assertions
    flag_messages = [f for f in failed if "behavioral_deviation_flags" in f]
    assert len(flag_messages) == 2, flag_messages
    joined = "\n".join(flag_messages)
    assert "missing required" in joined
    assert "urgency_paired_with_finance" in joined
    assert "emitted forbidden" in joined
    assert "new_banking_instructions" in joined


# ----------------------------------------------------------------------
# Dataset-side contract pins for the audit-gap closure
# ----------------------------------------------------------------------


def test_all_twenty_fraud_cases_pin_behavioral_deviation_flags():
    """Every fraud case in the shipped dataset must assert flag emission.

    Legit cases are intentionally left at None for now (FPR gate covers
    over-classification; flag-level legit assertions are a follow-up).
    """

    cases = load_dataset()
    fraud_cases = [c for c in cases if c.label == "fraud"]
    assert len(fraud_cases) == 20
    missing = [
        c.case_id
        for c in fraud_cases
        if c.expected.behavioral_deviation_flags is None
    ]
    assert missing == [], (
        f"the following fraud cases lack a behavioral_deviation_flags "
        f"expectation and could pass the §4.5 gate without emitting any "
        f"flag: {missing}"
    )


def test_three_unicode_cases_pin_unusual_unicode_obfuscation():
    """The Unicode-obfuscation cases (ia-003, ls-001, hi-001) MUST require
    the new schema flag the §4.5 audit gap was originally about."""

    cases = load_dataset()
    by_id = {c.case_id: c for c in cases}
    for case_id in ("ia-003", "ls-001", "hi-001"):
        expected_flags = by_id[case_id].expected.behavioral_deviation_flags
        assert expected_flags is not None, case_id
        assert "unusual_unicode_obfuscation" in expected_flags, (
            f"case {case_id} must require unusual_unicode_obfuscation; "
            f"got {expected_flags}"
        )


def test_legit_cases_intentionally_unpinned_for_now():
    """Pin the current decision: legit cases are NOT yet flag-asserted.

    This is documented in the activity log; if we later switch legit to
    behavioral_deviation_flags=[] (asserting zero flags), this test will
    correctly fail and the decision can be revisited in the same commit.
    """

    cases = load_dataset()
    legit_cases = [c for c in cases if c.label == "legit"]
    assert len(legit_cases) == 20
    for case in legit_cases:
        assert case.expected.behavioral_deviation_flags is None, (
            f"legit case {case.case_id} now has flag assertion "
            f"{case.expected.behavioral_deviation_flags}; if this was "
            "intentional, update this test in the same commit and "
            "document the decision in PROJECT_ACTIVITY_LOG.md"
        )


# ----------------------------------------------------------------------
# llm_safety module tests (workflow plan §C runtime side)
# ----------------------------------------------------------------------


def _write_minimal_dataset(path: Path, *, body: str = "synthetic body") -> None:
    """Write a single-case valid dataset at ``path`` for safety / CLI tests."""

    row = {
        "case_id": "test-001",
        "label": "fraud",
        "subcategory": "vendor_invoice_fraud",
        "email": {
            "received_at": "2026-01-01T00:00:00+00:00",
            "sender": "a@example.test",
            "recipient": "b@example.test",
            "body_plain": body,
        },
        "expected": {"min_risk_score": 0, "max_risk_score": 100},
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def test_unsafe_patterns_are_lowercase_and_synced_with_shell_hook():
    # Every entry must be lowercase so the scanner's case-insensitive
    # lower() comparison works. If a future maintainer adds an upper-
    # case pattern this test catches it before the scanner silently
    # misses hits.
    for pattern in UNSAFE_PATTERNS:
        assert pattern == pattern.lower(), pattern
    # The expected set is intentionally specified verbatim so any
    # addition or removal to the runtime tuple has to update this test
    # in the same commit, mirroring the A↔B↔C sync rule.
    assert set(UNSAFE_PATTERNS) == {
        "reverse shell",
        "keylogger",
        "botnet",
        "ddos attack",
        "ransomware payload",
        "ransomware builder",
        "exploit this server",
        "how do i hack",
    }


def test_scan_rejects_unsafe_term(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text("here is a reverse shell description\n", encoding="utf-8")
    with pytest.raises(LLMSafetyError, match="reverse shell"):
        scan_dataset_for_unsafe_terms(bad)


def test_scan_passes_clean_file(tmp_path):
    clean = tmp_path / "clean.jsonl"
    _write_minimal_dataset(clean)
    scan_dataset_for_unsafe_terms(clean)


def test_scan_missing_file_raises(tmp_path):
    with pytest.raises(LLMSafetyError, match="does not exist"):
        scan_dataset_for_unsafe_terms(tmp_path / "missing.jsonl")


def test_scan_accepts_extra_patterns(tmp_path):
    f = tmp_path / "f.jsonl"
    f.write_text("contains internal-codename-alpha here\n", encoding="utf-8")
    with pytest.raises(LLMSafetyError, match="internal-codename-alpha"):
        scan_dataset_for_unsafe_terms(f, extra_patterns=("internal-codename-alpha",))


@pytest.mark.parametrize(
    ("component", "matched_substring"),
    [
        ("customer", "customer"),
        ("Customers", "customer"),  # case-insensitive; "customer" also matches "customers"
        ("production", "production"),
        ("real_emails", "real_email"),  # "real_email" is iterated first and substrings "real_emails"
        ("tenant_data", "tenant_data"),
    ],
)
def test_path_allowlist_rejects_unsafe_component(tmp_path, component, matched_substring):
    path = tmp_path / f"{component}_dataset.jsonl"
    with pytest.raises(LLMSafetyError, match=matched_substring):
        assert_dataset_path_is_allowlisted(path)


def test_path_allowlist_allows_default_dataset_path():
    assert_dataset_path_is_allowlisted(DEFAULT_DATASET_PATH)


def test_path_allowlist_bypass_flag_skips_check(tmp_path):
    path = tmp_path / "customer_emails.jsonl"
    assert_dataset_path_is_allowlisted(path, allow_unsafe_dataset_path=True)


def test_resolve_api_key_raises_when_unset(monkeypatch):
    monkeypatch.delenv("NORTHSTAR_TEST_KEY_VAR", raising=False)
    with pytest.raises(LLMSafetyError, match="NORTHSTAR_TEST_KEY_VAR"):
        resolve_api_key("NORTHSTAR_TEST_KEY_VAR")


def test_resolve_api_key_returns_when_set(monkeypatch):
    monkeypatch.setenv("NORTHSTAR_TEST_KEY_VAR", "sk-test-value")
    assert resolve_api_key("NORTHSTAR_TEST_KEY_VAR") == "sk-test-value"


def test_resolve_api_key_returns_from_nearest_dotenv(monkeypatch, tmp_path):
    monkeypatch.delenv("NORTHSTAR_TEST_KEY_VAR", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "OTHER_KEY=ignored\nNORTHSTAR_TEST_KEY_VAR=sk-dotenv-value\n",
        encoding="utf-8",
    )

    assert resolve_api_key("NORTHSTAR_TEST_KEY_VAR") == "sk-dotenv-value"


def test_resolve_api_key_prefers_process_env_over_dotenv(monkeypatch, tmp_path):
    monkeypatch.setenv("NORTHSTAR_TEST_KEY_VAR", "sk-env-value")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "NORTHSTAR_TEST_KEY_VAR=sk-dotenv-value\n",
        encoding="utf-8",
    )

    assert resolve_api_key("NORTHSTAR_TEST_KEY_VAR") == "sk-env-value"


def test_resolve_api_key_rejects_empty_string(monkeypatch):
    monkeypatch.setenv("NORTHSTAR_TEST_KEY_VAR", "")
    with pytest.raises(LLMSafetyError, match="not set"):
        resolve_api_key("NORTHSTAR_TEST_KEY_VAR")


def test_strip_markdown_code_fences_with_json_tag():
    raw = '```json\n{"summary": "ok"}\n```'
    assert strip_markdown_code_fences(raw) == '{"summary": "ok"}'


def test_strip_markdown_code_fences_without_tag():
    raw = '```\n{"summary": "ok"}\n```'
    assert strip_markdown_code_fences(raw) == '{"summary": "ok"}'


def test_strip_markdown_code_fences_no_op_on_clean_text():
    raw = '{"summary": "ok"}'
    assert strip_markdown_code_fences(raw) == raw


def test_strip_markdown_code_fences_leaves_nested_fences_alone():
    # If the LLM emits a doubly-fenced response, do not silently flatten
    # — the eval harness should report schema_mismatch rather than try
    # to interpret nested structure.
    raw = "```json\n```\n{\"summary\": \"ok\"}\n```\n```"
    # Outer fence is stripped once; inner content keeps its nested fence.
    stripped = strip_markdown_code_fences(raw)
    assert "```" in stripped


def test_build_llm_safe_client_forwards_and_logs(tmp_path):
    log_path = tmp_path / "usage.jsonl"
    inner_calls: list[tuple[str, str]] = []

    def _inner(system_prompt: str, user_prompt: str) -> str:
        inner_calls.append((system_prompt, user_prompt))
        return '{"ok": true}'

    config = LLMSafeClientConfig(
        usage_log_path=log_path,
        required_system_prompt_prefix="NorthStar Inbox Shield",
        case_id_provider=lambda: "vf-001",
    )
    safe = build_llm_safe_client(_inner, config=config)
    result = safe("NorthStar Inbox Shield: locked", '{"sender":"x"}')

    assert result == '{"ok": true}'
    assert inner_calls == [("NorthStar Inbox Shield: locked", '{"sender":"x"}')]

    rows = read_usage_log(log_path)
    assert len(rows) == 1
    entry = rows[0]
    assert entry["case_id"] == "vf-001"
    assert entry["status"] == "ok"
    assert entry["error"] is None
    assert entry["response_bytes"] == len(result.encode("utf-8"))
    # Sha256 hex digests are 64 chars; presence + length is the round-trip pin.
    assert len(entry["system_prompt_sha256"]) == 64
    assert len(entry["user_prompt_sha256"]) == 64
    assert len(entry["response_sha256"]) == 64


def test_build_llm_safe_client_rejects_wrong_prefix(tmp_path):
    log_path = tmp_path / "usage.jsonl"

    def _inner(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        return '{"ok": true}'

    config = LLMSafeClientConfig(
        usage_log_path=log_path,
        required_system_prompt_prefix="EXPECTED-PREFIX",
    )
    safe = build_llm_safe_client(_inner, config=config)
    with pytest.raises(LLMSafetyError, match="required locked-prefix"):
        safe("WRONG-PREFIX whatever", '{"x":1}')


def test_build_llm_safe_client_logs_and_reraises_on_inner_exception(tmp_path):
    log_path = tmp_path / "usage.jsonl"

    def _inner(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        raise RuntimeError("model 503")

    config = LLMSafeClientConfig(
        usage_log_path=log_path,
        required_system_prompt_prefix="prefix",
        case_id_provider=lambda: "lv-001",
    )
    safe = build_llm_safe_client(_inner, config=config)
    with pytest.raises(RuntimeError, match="model 503"):
        safe("prefix-then-body", '{"x":1}')

    rows = read_usage_log(log_path)
    assert len(rows) == 1
    assert rows[0]["case_id"] == "lv-001"
    assert rows[0]["status"] == "error:RuntimeError"
    assert rows[0]["error"] == "model 503"
    assert rows[0]["response_sha256"] is None
    assert rows[0]["response_bytes"] is None


def test_usage_log_does_not_persist_raw_content(tmp_path):
    """Privacy pin: the on-disk log MUST NOT contain prompt or response bodies."""

    log_path = tmp_path / "usage.jsonl"
    secret_user_prompt = '{"sender":"NORTHSTAR_SECRET_MARKER_USER"}'
    secret_response = '{"summary":"NORTHSTAR_SECRET_MARKER_RESPONSE"}'

    def _inner(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        return secret_response

    config = LLMSafeClientConfig(
        usage_log_path=log_path,
        required_system_prompt_prefix="prefix",
    )
    safe = build_llm_safe_client(_inner, config=config)
    safe("prefix-and-body", secret_user_prompt)

    raw = log_path.read_text(encoding="utf-8")
    assert "NORTHSTAR_SECRET_MARKER_USER" not in raw
    assert "NORTHSTAR_SECRET_MARKER_RESPONSE" not in raw


def test_default_usage_log_path_sits_under_dataset_dir(tmp_path):
    dataset = tmp_path / "fraud_eval_dataset.jsonl"
    log = default_usage_log_path(dataset)
    assert log.name == "llm_usage.jsonl"
    assert log.parent.name == "operator_state"
    assert log.parent.parent == tmp_path


# ----------------------------------------------------------------------
# live_client module tests
# ----------------------------------------------------------------------


def test_supported_providers_contains_anthropic_openai_and_xai():
    assert set(SUPPORTED_PROVIDERS) == {"anthropic", "openai", "xai"}


def test_build_live_client_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        build_live_client("bogus", model="x", api_key="k")


def test_build_anthropic_client_raises_clearly_when_sdk_missing(monkeypatch):
    # Force the lazy import to fail by installing a sentinel that makes
    # `import anthropic` raise ImportError. Works whether or not the
    # operator machine actually has anthropic installed.
    import sys as _sys

    monkeypatch.setitem(_sys.modules, "anthropic", None)
    from core.scoring.eval import live_client as live_client_module

    with pytest.raises(LiveClientImportError, match="anthropic"):
        live_client_module.build_anthropic_client(model="x", api_key="k")


def test_build_openai_client_raises_clearly_when_sdk_missing(monkeypatch):
    import sys as _sys

    monkeypatch.setitem(_sys.modules, "openai", None)
    from core.scoring.eval import live_client as live_client_module

    with pytest.raises(LiveClientImportError, match="openai"):
        live_client_module.build_openai_client(model="x", api_key="k")


def test_build_xai_client_raises_clearly_when_sdk_missing(monkeypatch):
    import sys as _sys

    monkeypatch.setitem(_sys.modules, "openai", None)
    from core.scoring.eval import live_client as live_client_module

    with pytest.raises(LiveClientImportError, match="xAI"):
        live_client_module.build_xai_client(model="grok-4", api_key="k")


def test_build_xai_client_uses_openai_compatible_base_url(monkeypatch):
    import sys as _sys
    import types

    captured: dict[str, object] = {}

    class _FakeCompletions:
        def create(self, **kwargs):
            captured["completion_kwargs"] = kwargs
            return types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(
                            content='```json\n{"status": "ok"}\n```'
                        )
                    )
                ]
            )

    class _FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs
            self.chat = types.SimpleNamespace(completions=_FakeCompletions())

    monkeypatch.setitem(
        _sys.modules,
        "openai",
        types.SimpleNamespace(OpenAI=_FakeOpenAI),
    )
    from core.scoring.eval import live_client as live_client_module

    client = live_client_module.build_xai_client(model="grok-test", api_key="xai-key")
    assert client("system prompt", "user prompt") == '{"status": "ok"}'

    assert captured["client_kwargs"] == {
        "api_key": "xai-key",
        "base_url": live_client_module.XAI_DEFAULT_BASE_URL,
    }
    assert captured["completion_kwargs"] == {
        "model": "grok-test",
        "max_tokens": 4096,
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user prompt"},
        ],
    }


# ----------------------------------------------------------------------
# Pass-gate tests on EvalReport
# ----------------------------------------------------------------------


def _make_report(
    *,
    precision: float,
    fpr: float,
    fraud_subcategory_recalls: dict[str, float],
    legit_subcategory_recalls: dict[str, float] | None = None,
) -> EvalReport:
    """Construct a minimal EvalReport for pass-gate property testing."""

    per_sub: dict[EvalSubcategory, EvalSubcategoryStats] = {}
    total = 0
    passed = 0
    for name, recall in fraud_subcategory_recalls.items():
        n = 10
        p = int(round(recall * n))
        per_sub[name] = EvalSubcategoryStats(  # type: ignore[arg-type]
            subcategory=name,  # type: ignore[arg-type]
            total=n,
            passed=p,
        )
        total += n
        passed += p
    for name, recall in (legit_subcategory_recalls or {}).items():
        n = 10
        p = int(round(recall * n))
        per_sub[name] = EvalSubcategoryStats(  # type: ignore[arg-type]
            subcategory=name,  # type: ignore[arg-type]
            total=n,
            passed=p,
        )
        total += n
        passed += p
    return EvalReport(
        total=total,
        passed=passed,
        per_subcategory=per_sub,
        precision_on_fraud=precision,
        false_positive_rate_on_legit=fpr,
        results=[],
    )


def test_pass_gate_constants_match_deep_dive_section_4_5():
    assert PASS_GATE_MIN_PRECISION_ON_FRAUD == 0.80
    assert PASS_GATE_MAX_FPR_ON_LEGIT == 0.10
    assert PASS_GATE_MIN_PER_SUBCATEGORY_RECALL == 0.60


def test_eval_report_gate_passes_when_all_three_criteria_met():
    report = _make_report(
        precision=0.85,
        fpr=0.05,
        fraud_subcategory_recalls={
            "vendor_invoice_fraud": 0.80,
            "executive_impersonation": 0.70,
            "wire_transfer_pressure": 0.75,
            "invoice_authenticity_anomaly": 0.65,
            "lookalike_sender": 0.70,
            "header_inconsistency": 0.60,
        },
    )
    assert report.precision_gate_met is True
    assert report.fpr_gate_met is True
    assert report.per_subcategory_recall_gate_met is True
    assert report.gate_passed is True
    assert report.per_subcategory_recall_failures() == []


def test_eval_report_precision_gate_boundary_exactly_at_threshold():
    report = _make_report(
        precision=0.80,
        fpr=0.0,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    assert report.precision_gate_met is True


def test_eval_report_precision_gate_fails_just_below_threshold():
    report = _make_report(
        precision=0.799,
        fpr=0.0,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    assert report.precision_gate_met is False
    assert report.gate_passed is False


def test_eval_report_fpr_gate_boundary_exactly_at_threshold():
    report = _make_report(
        precision=1.0,
        fpr=0.10,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    assert report.fpr_gate_met is True


def test_eval_report_fpr_gate_fails_just_above_threshold():
    report = _make_report(
        precision=1.0,
        fpr=0.101,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    assert report.fpr_gate_met is False
    assert report.gate_passed is False


def test_eval_report_recall_gate_fails_when_any_fraud_subcategory_below_floor():
    report = _make_report(
        precision=1.0,
        fpr=0.0,
        fraud_subcategory_recalls={
            "vendor_invoice_fraud": 0.80,
            "executive_impersonation": 0.50,  # below 0.60 floor
        },
    )
    assert report.per_subcategory_recall_gate_met is False
    failures = report.per_subcategory_recall_failures()
    assert ("executive_impersonation", 0.5) in failures
    assert report.gate_passed is False


def test_eval_report_recall_gate_ignores_legit_subcategories():
    # A legit subcategory with low pass-rate must not flip the fraud-recall gate.
    report = _make_report(
        precision=1.0,
        fpr=0.0,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 0.80},
        legit_subcategory_recalls={"legit_newsletter": 0.10},
    )
    assert report.per_subcategory_recall_gate_met is True
    assert report.gate_passed is True


def test_eval_report_markdown_contains_pass_gate_block_and_verdict():
    report = _make_report(
        precision=0.90,
        fpr=0.05,
        fraud_subcategory_recalls={
            "vendor_invoice_fraud": 0.80,
            "executive_impersonation": 0.70,
        },
    )
    table = report.markdown_table()
    assert "### Pass Gate" in table
    assert "Phase 1.1 deep dive" in table
    assert "Precision on fraud" in table
    assert "FPR on legit" in table
    assert "Per-fraud-subcategory recall" in table
    assert "**Gate verdict:** PASS" in table


def test_eval_report_markdown_gate_verdict_fail_when_any_criterion_misses():
    report = _make_report(
        precision=0.5,  # below floor
        fpr=0.0,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    table = report.markdown_table()
    assert "**Gate verdict:** FAIL" in table
    assert "| Precision on fraud | >= 80% | 50.00% | NO |" in table


def test_eval_report_markdown_per_subcategory_breakdown_still_present():
    # Backward-compat with the original markdown_table contract.
    report = _make_report(
        precision=1.0,
        fpr=0.0,
        fraud_subcategory_recalls={"vendor_invoice_fraud": 1.0},
    )
    table = report.markdown_table()
    assert "### Per-subcategory breakdown" in table
    assert "| Subcategory | Total | Passed | Recall |" in table


# ----------------------------------------------------------------------
# CLI tests for the new --provider / --llm-safe / --report-out flags
# ----------------------------------------------------------------------


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Run harness_main with captured stdout + stderr; return (code, out, err)."""

    import contextlib

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
        try:
            exit_code = harness_main(argv)
        except SystemExit as exc:
            # argparse's error() raises SystemExit(2); capture so the test
            # can introspect both the code and the stderr message.
            exit_code = int(exc.code) if exc.code is not None else 2
    return exit_code, out_buf.getvalue(), err_buf.getvalue()


def test_harness_cli_dry_run_and_provider_mutually_exclusive():
    code, _out, err = _run_cli(["--dry-run", "--provider", "anthropic", "--model", "x"])
    assert code == 2
    assert "mutually exclusive" in err


def test_harness_cli_provider_requires_model():
    code, _out, err = _run_cli(["--provider", "anthropic"])
    assert code == 2
    assert "--model" in err


def test_harness_cli_unknown_provider_argparse_error():
    code, _out, err = _run_cli(["--provider", "bogus", "--model", "x"])
    assert code == 2
    assert "bogus" in err or "invalid choice" in err.lower()


def test_harness_cli_provider_no_api_key_exits_safety_error(monkeypatch):
    monkeypatch.setenv("NORTHSTAR_LLM_DISABLE_DOTENV", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    code, _out, err = _run_cli(
        ["--provider", "anthropic", "--model", "claude-test"]
    )
    assert code == 2
    assert "ANTHROPIC_API_KEY" in err


def test_harness_cli_xai_provider_uses_xai_api_key_env(monkeypatch):
    monkeypatch.setenv("NORTHSTAR_LLM_DISABLE_DOTENV", "1")
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    code, _out, err = _run_cli(["--provider", "xai", "--model", "grok-test"])
    assert code == 2
    assert "XAI_API_KEY" in err


def test_harness_cli_rejects_unsafe_dataset_path(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    bad_dir = tmp_path / "customer_emails"
    bad_dir.mkdir()
    dataset = bad_dir / "ds.jsonl"
    _write_minimal_dataset(dataset)
    code, _out, err = _run_cli(
        [
            "--provider", "anthropic",
            "--model", "claude-test",
            "--dataset", str(dataset),
        ]
    )
    assert code == 2
    assert "customer" in err.lower()


def test_harness_cli_unsafe_path_bypass_proceeds_to_api_key_resolution(
    monkeypatch, tmp_path
):
    """--allow-unsafe-dataset-path skips the path check; downstream API key
    resolve still gates so this run still exits 2, but for a different reason."""
    monkeypatch.setenv("NORTHSTAR_LLM_DISABLE_DOTENV", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    bad_dir = tmp_path / "customer_emails"
    bad_dir.mkdir()
    dataset = bad_dir / "ds.jsonl"
    _write_minimal_dataset(dataset)
    code, _out, err = _run_cli(
        [
            "--provider", "anthropic",
            "--model", "claude-test",
            "--dataset", str(dataset),
            "--allow-unsafe-dataset-path",
        ]
    )
    assert code == 2
    # Path check was skipped; failure is the API key resolve, not the path.
    assert "customer" not in err.lower()
    assert "ANTHROPIC_API_KEY" in err


def test_harness_cli_rejects_dataset_with_unsafe_pattern(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    dataset = tmp_path / "ds.jsonl"
    # Use a body that loader will accept but the unsafe-pattern scan will trip.
    _write_minimal_dataset(dataset, body="here is a reverse shell mention")
    code, _out, err = _run_cli(
        [
            "--provider", "anthropic",
            "--model", "claude-test",
            "--dataset", str(dataset),
        ]
    )
    assert code == 2
    assert "reverse shell" in err


def test_harness_cli_no_llm_safe_skips_safety_scan(monkeypatch, tmp_path):
    """--no-llm-safe disables the dataset scan; run proceeds past the scan
    and only fails at the live anthropic SDK import (which is forced
    missing here)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    import sys as _sys

    monkeypatch.setitem(_sys.modules, "anthropic", None)
    dataset = tmp_path / "ds.jsonl"
    _write_minimal_dataset(dataset, body="here is a reverse shell mention")
    code, _out, err = _run_cli(
        [
            "--provider", "anthropic",
            "--model", "claude-test",
            "--dataset", str(dataset),
            "--no-llm-safe",
        ]
    )
    assert code == 2
    # Scan was skipped (unsafe-term phrase did not trip the run), but the
    # downstream SDK import failed with a clear message.
    assert "reverse shell" not in err.lower()
    assert "anthropic" in err.lower()


def test_harness_cli_report_out_writes_markdown_to_disk(tmp_path):
    out_path = tmp_path / "report.md"
    code, stdout, _err = _run_cli(["--dry-run", "--report-out", str(out_path)])
    assert code in (0, 1)
    assert out_path.exists()
    on_disk = out_path.read_text(encoding="utf-8")
    assert on_disk == stdout
    assert "### Pass Gate" in on_disk


def test_harness_cli_case_id_filters_to_single_case():
    code, stdout, _err = _run_cli(["--dry-run", "--case-id", "vf-001"])
    assert code in (0, 1)
    assert "## Fraud Eval Report — 1 cases" in stdout
    assert "| vendor_invoice_fraud | 1 |" in stdout


def test_harness_cli_unknown_case_id_exits_2():
    code, _out, err = _run_cli(["--dry-run", "--case-id", "missing-case"])
    assert code == 2
    assert "missing-case" in err
    assert "not found" in err


def test_harness_cli_show_failure_details_prints_reason_for_default_client():
    code, stdout, _err = _run_cli(
        ["--case-id", "vf-001", "--show-failure-details"]
    )
    assert code == 1
    assert "### Case Failure Details" in stdout
    assert "`vf-001`: FAIL" in stdout
    assert "llm_client_raised:NotImplementedError" in stdout


def test_harness_cli_show_raw_response_prints_evaluated_raw_output():
    code, stdout, _err = _run_cli(
        ["--dry-run", "--case-id", "vf-001", "--show-raw-response"]
    )
    assert code in (0, 1)
    assert "### Raw LLM Responses" in stdout
    assert "#### vf-001" in stdout
    assert '"summary": "dry-run stub analysis"' in stdout


def test_harness_cli_dataset_load_error_exits_2(tmp_path):
    missing = tmp_path / "does_not_exist.jsonl"
    code, _out, err = _run_cli(
        ["--dataset", str(missing), "--dry-run"]
    )
    assert code == 2
    assert "failed to load dataset" in err


def test_harness_reconfigure_stdio_to_utf8_switches_supported_streams():
    """Recovery-pass harness fix: stdout / stderr are reconfigured to UTF-8
    so raw LLM responses for Unicode-obfuscation cases (`ia-003`, `ls-001`,
    `hi-001`) do not crash with ``UnicodeEncodeError`` on cp1252 Windows
    consoles. The fix is best-effort: streams without a usable
    ``reconfigure`` method must be left untouched.
    """
    import io
    import sys as _sys

    from core.scoring.eval.fraud_eval_harness import _reconfigure_stdio_to_utf8

    fake_stdout = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    fake_stderr = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    original_stdout = _sys.stdout
    original_stderr = _sys.stderr
    _sys.stdout = fake_stdout
    _sys.stderr = fake_stderr
    try:
        _reconfigure_stdio_to_utf8()
        assert fake_stdout.encoding.lower() == "utf-8"
        assert fake_stderr.encoding.lower() == "utf-8"
        fake_stdout.write("non-breaking hyphen \u2011 and zero-width space \u200b ok")
        fake_stdout.flush()
    finally:
        _sys.stdout = original_stdout
        _sys.stderr = original_stderr


def test_harness_reconfigure_stdio_to_utf8_is_safe_on_streams_without_reconfigure():
    """Streams that look like text streams but lack ``reconfigure`` (some
    captured / wrapped streams) must not raise — the helper has to be a
    silent no-op in that case so tests, pipes, and non-standard runners
    still work."""

    import sys as _sys

    from core.scoring.eval.fraud_eval_harness import _reconfigure_stdio_to_utf8

    class _NoReconfigureStream:
        encoding = "cp1252"

        def write(self, _: str) -> int:
            return 0

        def flush(self) -> None:
            return None

    stream = _NoReconfigureStream()
    original_stdout = _sys.stdout
    original_stderr = _sys.stderr
    _sys.stdout = stream
    _sys.stderr = stream
    try:
        _reconfigure_stdio_to_utf8()
    finally:
        _sys.stdout = original_stdout
        _sys.stderr = original_stderr


def test_harness_cli_locked_prompt_prefix_used_by_safe_wrapper(monkeypatch, tmp_path):
    """End-to-end pin: the CLI's llm-safe wrapper requires the locked scoring
    prompt prefix. We exercise this by running with --no-llm-safe (so the
    safe wrapper is bypassed) and confirming the inner client gets the
    locked prompt unchanged. The wrapper-prefix branch itself is covered
    by the build_llm_safe_client unit tests above."""

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    # Force the SDK import to succeed via a stub module so we can capture
    # the system prompt at the call site without a real network call.
    import types as _types
    import sys as _sys

    captured: dict[str, str] = {}

    class _FakeMessages:
        def create(self, *, model, max_tokens, temperature, system, messages):
            del model, max_tokens, temperature, messages
            captured["system"] = system
            payload = json.dumps(
                {
                    "summary": "stub",
                    "action_items": [],
                    "risk_analysis": {
                        "risk_score": 50,
                        "risk_factors": [],
                        "phishing_signals": [],
                        "urgency_signals": [],
                        "financial_risk": "medium",
                        "vendor_fraud_score": 50,
                        "wire_transfer_anomaly_score": 50,
                        "invoice_authenticity_score": None,
                        "behavioral_deviation_flags": [],
                    },
                    "impersonation_analysis": {
                        "impersonation_likelihood": 50,
                        "suspicious_elements": [],
                        "sender_legitimacy_notes": None,
                    },
                    "recommended_action": "needs_review",
                }
            )

            class _Block:
                text = payload

            class _Msg:
                content = [_Block()]

            return _Msg()

    class _FakeAnthropic:
        def __init__(self, api_key):
            del api_key
            self.messages = _FakeMessages()

    fake_module = _types.ModuleType("anthropic")
    fake_module.Anthropic = _FakeAnthropic  # type: ignore[attr-defined]
    monkeypatch.setitem(_sys.modules, "anthropic", fake_module)

    dataset = tmp_path / "ds.jsonl"
    _write_minimal_dataset(dataset)
    code, _out, _err = _run_cli(
        [
            "--provider", "anthropic",
            "--model", "claude-test",
            "--dataset", str(dataset),
            "--no-llm-safe",
        ]
    )
    # The single test case has wide bounds (0..100), so the stub response
    # satisfies its expected bounds; the gate's per-subcategory recall
    # for vendor_invoice_fraud is 100% and the FPR / precision are
    # vacuous (no legit cases in this single-case dataset). The exit
    # code should therefore be 0 (gate passed) or 1 (vacuous precision
    # treated as 0). Either is acceptable; the point of this test is the
    # prompt capture.
    assert code in (0, 1)
    assert captured["system"] == NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
