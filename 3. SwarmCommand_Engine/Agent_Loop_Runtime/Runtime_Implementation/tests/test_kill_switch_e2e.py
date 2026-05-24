"""End-to-end smoke test for the operator kill switch.

ingest -> engage(ALL) -> confirm scoring + digest both refuse -> disengage
-> confirm the full Inbox Shield pipeline runs again.

Keeps the e2e surface intentionally narrow; the unit and loop-integration
tests do most of the work. This test just pins the operator workflow.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from core.blackboard import (
    DailyDigestPayload,
    Environment,
    RecordType,
    read_records,
)
from core.drafting import DailyDigestConfig, run_daily_digest_cycle
from core.ingest import ingest_email
from core.operator_state import (
    KillSwitchEngaged,
    disengage_kill_switch,
    engage_kill_switch,
    read_operator_audit_log,
    operator_audit_log_path,
)
from core.orchestrator import RouteContext
from core.orchestrator.routes import blackboard_path
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle

import pytest

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _scoring_client(system_prompt: str, user_prompt: str) -> str:
    assert "NorthStar Inbox Shield" in system_prompt
    json.loads(user_prompt)
    return json.dumps(
        {
            "summary": "Invoice-style email.",
            "action_items": [
                {
                    "task": "Verify wire instructions out-of-band",
                    "owner": "finance",
                    "due_date": "2026-05-21",
                }
            ],
            "risk_analysis": {
                "risk_score": 80,
                "risk_factors": ["new banking details"],
                "phishing_signals": ["sender_mismatch"],
                "urgency_signals": ["payment_today"],
                "financial_risk": "high",
                "vendor_fraud_score": 75,
                "wire_transfer_anomaly_score": 70,
                "invoice_authenticity_score": 35,
                "behavioral_deviation_flags": ["new_banking_instructions"],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 50,
                "suspicious_elements": ["display_name_does_not_match"],
                "sender_legitimacy_notes": "first contact",
            },
            "recommended_action": "needs_review",
        }
    )


def _digest_client(system_prompt: str, user_prompt: str) -> str:
    return "# Today's digest"


def test_e2e_kill_switch_halts_then_resumes_the_inbox_shield_pipeline(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email={
            "received_at": now - timedelta(hours=2),
            "sender": "vendor@example.com",
            "recipient": "ops@northstar.example",
            "subject": "Outstanding invoice",
            "body_plain": "Please confirm wire details.",
        },
    )

    engage_kill_switch(
        context.blackboard_root, scope="ALL", reason="operator halt", operator="matt"
    )

    with pytest.raises(KillSwitchEngaged):
        run_email_risk_scoring_cycle(
            context,
            config=EmailRiskScoringConfig(
                llm_client=_scoring_client, production_tenant_id=TENANT
            ),
        )
    with pytest.raises(KillSwitchEngaged):
        run_daily_digest_cycle(
            context,
            config=DailyDigestConfig(
                llm_client=_digest_client,
                production_tenant_id=TENANT,
                now_provider=lambda: now,
            ),
        )

    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, TENANT
    )
    records_during_halt = read_records(production_path)
    assert all(
        record.record_type != RecordType.EMAIL_ANALYSIS
        for record in records_during_halt
    )
    assert all(
        record.record_type != RecordType.DAILY_DIGEST
        for record in records_during_halt
    )

    disengage_kill_switch(
        context.blackboard_root, reason="incident resolved", operator="matt"
    )

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_scoring_client, production_tenant_id=TENANT
        ),
    )
    assert scoring_result.analyzed == 1
    assert scoring_result.failed == 0

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_digest_client,
            production_tenant_id=TENANT,
            now_provider=lambda: now,
        ),
    )
    assert digest_result.digest_record_id is not None
    assert digest_result.important_emails_count == 1

    records_after_resume = read_records(production_path)
    digests = [
        record
        for record in records_after_resume
        if record.record_type == RecordType.DAILY_DIGEST
    ]
    assert len(digests) == 1
    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert digest_payload.important_emails[0].subject == "Outstanding invoice"

    audit_entries = read_operator_audit_log(
        operator_audit_log_path(context.blackboard_root)
    )
    assert [entry.action for entry in audit_entries] == ["engage", "disengage"]
    assert audit_entries[0].scope == "ALL"
    assert audit_entries[0].reason == "operator halt"
    assert audit_entries[1].previous_scope == "ALL"
    assert audit_entries[1].reason == "incident resolved"
