"""Stage A precursor-chain demo runner against the cyber-insurance v1 fictional fixture.

PRE-SPEC RESEARCH-INPUT RUNNER. NOT IMPLEMENTATION. NOT A §14-CONFORMANT RUN.
NOT INVOKED BY ANY AGENT LOOP. NOT PART OF THE PYTEST SUITE.

Read ``README.md`` and ``RUN_INSTRUCTIONS.md`` in this directory before invoking.

Invocation (from the repo root, with the runtime venv active)::

    python "Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/runner.py" \\
        --scoring-mode live-xai \\
        --model grok-4

Pass ``--scoring-mode fake`` to skip the live XAI call entirely (zero spend).
The default is ``live-xai`` so an accidental copy-paste run does not silently
skip the call you authorized; you must opt down to fake.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# Path bootstrap: this script lives at Research/v1_test_plan_runners/<case>/runner.py.
# The runtime's `core.*` packages live under Runtime_Implementation/.
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parents[3]
RUNTIME_ROOT = (
    REPO_ROOT
    / "3. SwarmCommand_Engine"
    / "Agent_Loop_Runtime"
    / "Runtime_Implementation"
)
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.drafting import DailyDigestConfig, run_daily_digest_cycle  # noqa: E402
from core.ingest import ingest_email, sha256_attachment_inspector  # noqa: E402
from core.orchestrator import RouteContext  # noqa: E402
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle  # noqa: E402
from core.scoring.eval.live_client import build_xai_client  # noqa: E402
from core.workflows.two_channel_confirmation import (  # noqa: E402
    record_confirmation_outcome,
    record_confirmation_request,
)


LLMClient = Callable[[str, str], str]

FIXTURE_PATH = (
    RUNTIME_ROOT
    / "tests"
    / "fixtures"
    / "cyber_insurance_v1_test_plan"
    / "stage_a_vendor_payment_redirect_001.json"
)
DEMO_OUT_DIR = (
    RUNTIME_ROOT
    / "demo_outputs"
    / "cyber_insurance_v1_test_plan"
    / "stage_a_vendor_payment_redirect_001"
)
DEMO_BLACKBOARD = DEMO_OUT_DIR / "blackboard"
SUMMARY_PATH = DEMO_OUT_DIR / "run_summary.md"
RAW_SCORING_PATH = DEMO_OUT_DIR / "scoring_raw_response.json"

# Operator-authored §14.3.5 outcome heading; only used as descriptive metadata in
# the channel_description field, never as a runtime enum value.
OPERATOR_AUTHORED_OUTCOME_HEADING = (
    "Vendor invoice review — payment change reviewed before action."
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not FIXTURE_PATH.exists():
        _err(f"fixture missing at {FIXTURE_PATH}")
        return 2
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    scoring_client, captured_responses = _build_scoring_client(
        scoring_mode=args.scoring_mode,
        model=args.model,
    )
    if scoring_client is None:
        return 2

    if DEMO_BLACKBOARD.exists():
        shutil.rmtree(DEMO_BLACKBOARD)
    DEMO_OUT_DIR.mkdir(parents=True, exist_ok=True)

    context = RouteContext(blackboard_root=DEMO_BLACKBOARD)
    tenant_id = fixture["tenant_id"]

    received_at = _parse_iso8601_z(fixture["received_at"])
    raw_email = _build_raw_email(fixture, received_at)
    ingest_email(
        context,
        tenant_id=tenant_id,
        raw_email=raw_email,
        attachment_inspector=sha256_attachment_inspector,
    )

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=scoring_client,
            production_tenant_id=tenant_id,
            enable_client_facing_rubric=True,
        ),
    )
    if scoring_result.failed:
        _err(f"scoring failed for {scoring_result.failed} email(s)")
        return 3

    finding_id = _build_finding_id(fixture["case_id"])
    requested_at = received_at
    record_confirmation_request(
        tenant_id=tenant_id,
        finding_id=finding_id,
        detector="payment_change_review",
        risk_floor=60,  # mirrors the fixture's tenant override on content_risk_review_threshold
        requested_by="bluefin_ap_reviewer",
        requested_at=requested_at,
        blackboard_root=DEMO_BLACKBOARD,
    )

    outcome_at = datetime(2026, 5, 31, 14, 0, tzinfo=timezone.utc)
    record_confirmation_outcome(
        tenant_id=tenant_id,
        finding_id=finding_id,
        outcome_status="confirmed",
        outcome_by="bluefin_ap_reviewer",
        outcome_at=outcome_at,
        channel_kind="previously_known_phone",
        channel_description=(
            "Callback to previously-validated vendor phone number; "
            "outcome maps to the operator-authored §14.3.5 heading: "
            f"{OPERATOR_AUTHORED_OUTCOME_HEADING}"
        ),
        reason=(
            "Stage A precursor-chain demo only; runtime TwoChannelOutcomeStatus "
            "does not include the §14.3.5 heading verbatim."
        ),
        blackboard_root=DEMO_BLACKBOARD,
    )

    digest_now = datetime(2026, 5, 31, 23, 0, tzinfo=timezone.utc)
    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_fake_digest_client,
            production_tenant_id=tenant_id,
            now_provider=lambda: digest_now,
        ),
    )

    _write_summary(
        scoring_mode=args.scoring_mode,
        model=args.model if args.scoring_mode == "live-xai" else None,
        fixture=fixture,
        scoring_analyzed=scoring_result.analyzed,
        scoring_failed=scoring_result.failed,
        digest_record_id=str(digest_result.digest_record_id) if digest_result.digest_record_id else "(none)",
        workflow_trigger_id=str(digest_result.workflow_trigger_id) if digest_result.workflow_trigger_id else "(none)",
        top_risks_count=digest_result.top_risks_count,
        tasks_count=digest_result.tasks_count,
        finding_id=finding_id,
        captured_responses=captured_responses,
    )

    if captured_responses:
        RAW_SCORING_PATH.write_text(
            json.dumps(captured_responses, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"OK: demo run complete.")
    print(f"     Summary:          {SUMMARY_PATH}")
    if captured_responses:
        print(f"     Raw scoring JSON: {RAW_SCORING_PATH}")
    print(f"     Demo blackboard:  {DEMO_BLACKBOARD}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="stage_a_vendor_payment_redirect_001_runner",
        description=(
            "Run the Stage A precursor chain against the §14 fictional Bluefin "
            "vendor-payment-redirect fixture. Research-input demo only."
        ),
    )
    parser.add_argument(
        "--scoring-mode",
        choices=["live-xai", "fake"],
        default="live-xai",
        help=(
            "Scoring LLM mode. 'live-xai' (default) calls real grok-4 once. "
            "'fake' uses a deterministic stub for zero-spend route verification."
        ),
    )
    parser.add_argument(
        "--model",
        default="grok-4",
        help="xAI model id (default: grok-4). Ignored when --scoring-mode=fake.",
    )
    return parser.parse_args(argv)


def _build_scoring_client(
    *, scoring_mode: str, model: str
) -> tuple[LLMClient | None, list[dict]]:
    captured: list[dict] = []
    if scoring_mode == "fake":
        def fake_client(system_prompt: str, user_prompt: str) -> str:
            return _fake_scoring_response()
        return fake_client, captured

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        _err(
            "XAI_API_KEY is not set. Either export the key in this shell or "
            "rerun with --scoring-mode fake to skip the live XAI call."
        )
        return None, captured

    inner = build_xai_client(model=model, api_key=api_key)

    def captured_client(system_prompt: str, user_prompt: str) -> str:
        raw = inner(system_prompt, user_prompt)
        captured.append(
            {
                "system_prompt_chars": len(system_prompt),
                "user_prompt_chars": len(user_prompt),
                "raw_response": raw,
                "model": model,
                "provider": "xai",
            }
        )
        return raw

    return captured_client, captured


def _build_raw_email(fixture: dict, received_at: datetime) -> dict:
    attachments: list[dict] = []
    for a in fixture.get("attachments", []):
        extracted_text = a.get("extracted_text", "") or ""
        attachments.append(
            {
                "filename": a["filename"],
                "content_type": a["content_type"],
                "size_bytes": a["size_bytes"],
                "attachment_class": a.get("attachment_class", "other"),
                "extracted_text": extracted_text,
                # Placeholder body_bytes: the fixture is synthetic and the real
                # PDF bytes are not part of the fixture; the scorer only needs
                # the extracted text. This is a research-input demo, not a
                # real-PDF parser test.
                "body_bytes": extracted_text.encode("utf-8"),
            }
        )
    return {
        "received_at": received_at,
        "sender": fixture["sender"],
        "recipient": fixture["recipient"],
        "subject": fixture["subject"],
        "body_plain": fixture["body_plain"],
        "attachments": attachments,
    }


def _build_finding_id(case_id: str) -> str:
    # finding_id allowed chars: [A-Za-z0-9_-:.] per
    # core/workflows/two_channel_confirmation.py::_FINDING_ID_RE.
    safe = "".join(c if (c.isalnum() or c in "_-:.") else "-" for c in case_id)
    return f"stage-a:{safe}"


def _parse_iso8601_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _fake_scoring_response() -> str:
    return json.dumps(
        {
            "summary": (
                "Vendor invoice with updated remittance instructions; SPF/DKIM/"
                "DMARC pass but content carries payment-change risk."
            ),
            "action_items": [
                {
                    "task": (
                        "Verify the new ACH instructions by callback to a known-good "
                        "vendor phone number before any payment is released."
                    ),
                    "owner": "ap",
                    "due_date": None,
                },
                {
                    "task": "Pause payment until callback confirms.",
                    "owner": "ap",
                    "due_date": None,
                },
            ],
            "risk_analysis": {
                "risk_score": 78,
                "risk_factors": [
                    "new_banking_instructions",
                    "urgency_paired_with_finance",
                ],
                "phishing_signals": [],
                "urgency_signals": ["end of the week"],
                "financial_risk": "high",
                "vendor_fraud_score": 72,
                "wire_transfer_anomaly_score": 55,
                "invoice_authenticity_score": 40,
                "behavioral_deviation_flags": [
                    "new_banking_instructions",
                    "urgency_paired_with_finance",
                ],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 30,
                "suspicious_elements": [
                    "new ACH details in body and attachment",
                    "end-of-week urgency",
                ],
                "sender_legitimacy_notes": (
                    "SPF/DKIM/DMARC pass; auth posture is clean but content "
                    "carries payment-change risk."
                ),
            },
            "recommended_action": "needs_review",
        }
    )


def _fake_digest_client(system_prompt: str, user_prompt: str) -> str:
    return json.dumps(
        {
            "executive_summary": (
                "One vendor invoice review surfaced today; payment change "
                "pending callback confirmation."
            ),
            "top_risks": [
                {
                    "subject": "Harborline invoice 8841 - updated remittance details",
                    "sender": "accounts@billing.harborline-marine-services.example",
                    "headline": "Vendor remittance change with updated ACH details",
                    "why": (
                        "Auth pass but new banking instructions paired with "
                        "end-of-week urgency."
                    ),
                    "recommended_action": "needs_review",
                }
            ],
            "action_queue": [
                {
                    "task": (
                        "Verify the new ACH instructions by callback to a "
                        "known-good vendor phone number."
                    ),
                    "owner": "ap",
                    "subject_ref": "Harborline invoice 8841",
                }
            ],
            "other_notable_emails": [],
            "operator_guidance": (
                "Pause payment on invoice 8841 until the callback to a "
                "known-good vendor phone number confirms the remittance change."
            ),
        }
    )


def _write_summary(
    *,
    scoring_mode: str,
    model: str | None,
    fixture: dict,
    scoring_analyzed: int,
    scoring_failed: int,
    digest_record_id: str,
    workflow_trigger_id: str,
    top_risks_count: int,
    tasks_count: int,
    finding_id: str,
    captured_responses: list[dict],
) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    rel_fixture = FIXTURE_PATH.relative_to(REPO_ROOT)
    rel_blackboard = DEMO_BLACKBOARD.relative_to(REPO_ROOT)
    rel_summary = SUMMARY_PATH.relative_to(REPO_ROOT)
    rel_raw = RAW_SCORING_PATH.relative_to(REPO_ROOT)

    lines: list[str] = [
        "# Stage A Precursor-Chain Demo Run — §14 Fictional Case",
        "",
        "**Status:** Pre-spec research-input demo run. **Not** a §14-conformant "
        "test-plan run. **Not** a §14.4 pass/fail verdict. **No** D10 progress. "
        "**No** §13 sign-off. **No** implementation. **No** client-facing copy.",
        "",
        "## Run inputs",
        "",
        f"- Fixture: `{rel_fixture}`",
        f"- Case ID: `{fixture['case_id']}`",
        f"- Tenant: `{fixture['tenant_id']}` (fictional `.example` TLD)",
        f"- Sender: `{fixture['sender']}` (fictional)",
        f"- Auth posture (from fixture): SPF / DKIM / DMARC all pass.",
        f"- Scoring mode: `{scoring_mode}`"
        + (f" (model `{model}`)" if scoring_mode == "live-xai" else ""),
        f"- Digest mode: deterministic fake (cost-cap).",
        f"- Demo blackboard: `{rel_blackboard}`",
        f"- Runtime finding_id: `{finding_id}`",
        "",
        "## Run outputs",
        "",
        f"- Emails analyzed: {scoring_analyzed}",
        f"- Emails failed: {scoring_failed}",
        f"- Digest record id: `{digest_record_id}`",
        f"- Workflow trigger id: `{workflow_trigger_id}` (demo blackboard only; no external send)",
        f"- Digest top-risks count: {top_risks_count}",
        f"- Digest tasks count: {tasks_count}",
        "",
        "## Truthful mappings",
        "",
        "- The runtime `TwoChannelOutcomeStatus` enum is `confirmed | rejected "
        "| unable_to_verify | expired`. The §14.3.5 operator-authored heading "
        "*\"Vendor invoice review — payment change reviewed before action.\"* "
        "is **not** a runtime enum value. The outcome was recorded as "
        "`outcome_status=\"confirmed\"` with `channel_kind=\"previously_known_phone\"`; "
        "the `channel_description` field carries the §14.3.5 heading verbatim.",
        "- The five `cyber_insurance_v1_*` §14.3 record types (Detection / "
        "Verification / Evidence / Audit Trail / Outcome Documentation) are "
        "**not** produced by this run. They are not implemented in "
        "`core/blackboard/models.py::RecordType` today.",
        "",
        "## What this run DOES prove (dated / scoped)",
        "",
        "- The locked production scoring prompt runs end-to-end against the §14 "
        "fictional case.",
        "- The Stage A precursor chain (ingest → score → two-channel "
        "confirmation request + outcome → daily digest) is exercisable against "
        "the fixture.",
        "- The runtime path produces durable, on-disk records in an isolated "
        "demo blackboard.",
        "",
        "## What this run does NOT prove",
        "",
        "- Does NOT produce the five §14.3 `cyber_insurance_v1_*` record types.",
        "- Does NOT execute a §14.4 pass/fail verdict.",
        "- Does NOT advance D10, §13 sign-off, or implementation authorization.",
        "- Does NOT validate detection accuracy beyond what the saved scoring "
        "JSON shows. A single case is not a recall claim.",
        "- Does NOT support any claim of compliance, certification, insurer "
        "approval, premium reduction, coverage qualification, or fraud "
        "prevention.",
        "",
        "## Files produced",
        "",
        f"- Run summary (this file): `{rel_summary}`",
    ]
    if captured_responses:
        lines.append(f"- Raw scoring response(s): `{rel_raw}` ({len(captured_responses)} call(s))")
    lines.append(f"- Demo blackboard (records on disk): `{rel_blackboard}`")
    lines += [
        "",
        "## Suggested PROJECT_ACTIVITY_LOG.md entry shape",
        "",
        "```text",
        "## 2026-MM-DD - Stage A precursor-chain demo run against §14 fictional case",
        "",
        "**Actor:** operator-Matt (live run authorized).",
        "",
        f"**Files produced:** {rel_summary}, {rel_blackboard}/...",
        "",
        f"**Scoring mode:** {scoring_mode}"
        + (f" (model {model})" if scoring_mode == "live-xai" else ""),
        "",
        "**Boundary:** Research-input demo only. Not §14-conformant. Not a §14.4 verdict. No D10 progress.",
        "",
        "**Next:** operator decides whether to promote the saved scoring response "
        "into the internal correction-evidence record set (per "
        "`Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` §4 schema) "
        "or leave as a one-off precursor demo.",
        "```",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def _err(msg: str) -> None:
    print(f"runner: ERROR: {msg}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
