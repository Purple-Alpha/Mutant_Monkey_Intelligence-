"""End-to-end smoke tests for the NorthStar Inbox Shield pipeline.

Drives the full inbound -> scored -> digested sequence with deterministic
fake LLM clients:

    ingest_email
        -> EMAIL_INBOUND record on tenant blackboard
        -> run_email_risk_scoring_cycle
        -> EMAIL_ANALYSIS or EMAIL_ANALYSIS_FAILURE record + completion marker
        -> run_daily_digest_cycle
        -> DAILY_DIGEST record + send_daily_digest workflow trigger

No real LLM calls. The scoring fake routes on the inbound email's subject
to produce stable, distinguishable analyses. The digest fake echoes the
aggregate JSON so we can assert the LLM call actually happened with the
expected inputs.

ProductionLoopConfig integration is covered for the scoring agent and the
daily digest agent. Some tests still call the digest cycle directly to pin
the standalone aggregate -> markdown -> DAILY_DIGEST route.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from typing import Callable

from core.blackboard import (
    DailyDigestPayload,
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    RecordType,
    WorkflowTriggerPayload,
    read_records,
)
from core.drafting import DailyDigestConfig, run_daily_digest_cycle
from core.ingest import ingest_email
from core.orchestrator import RouteContext
from core.orchestrator.routes import blackboard_path
from core.production import (
    ProductionLoopConfig,
    ProductionSignal,
    run_production_cycle,
)
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle
from core.scoring.email_risk_scoring_agent import EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _production_records(context: RouteContext, tenant: str = TENANT):
    return read_records(
        blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant)
    )


def _fixed_now(when: datetime) -> Callable[[], datetime]:
    def _now() -> datetime:
        return when

    return _now


def _routing_scoring_client(
    *,
    garbage_for_subjects: set[str] | None = None,
) -> Callable[[str, str], str]:
    """A fake LLM that produces a deterministic analysis per inbound subject.

    Routes:
    - "invoice" -> high risk + financial_risk=high + recommended_action=needs_review
    - "newsletter" -> low risk + financial_risk=low + recommended_action=safe
    - else -> medium risk + financial_risk=medium + recommended_action=needs_review

    Optional ``garbage_for_subjects`` makes specified subjects produce
    unparseable output so the failure path can be exercised.
    """

    garbage_subjects = garbage_for_subjects or set()

    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        parsed_input = json.loads(user_prompt)
        subject = (parsed_input.get("subject") or "").lower()

        if subject in garbage_subjects:
            return "absolutely not JSON {{{"

        if "invoice" in subject:
            return json.dumps(
                {
                    "summary": f"Invoice-style email about {subject}.",
                    "action_items": [
                        {
                            "task": "Verify wire instructions out-of-band",
                            "owner": "finance",
                            "due_date": "2026-05-21",
                        },
                        {
                            "task": "Pause vendor payment",
                            "owner": "ops",
                            "due_date": None,
                        },
                    ],
                    "risk_analysis": {
                        "risk_score": 88,
                        "risk_factors": ["new banking details requested"],
                        "phishing_signals": ["sender_mismatch"],
                        "urgency_signals": ["payment_today"],
                        "financial_risk": "high",
                        "vendor_fraud_score": 85,
                        "wire_transfer_anomaly_score": 78,
                        "invoice_authenticity_score": 30,
                        "behavioral_deviation_flags": [
                            "new_banking_instructions",
                            "urgency_paired_with_finance",
                        ],
                    },
                    "impersonation_analysis": {
                        "impersonation_likelihood": 60,
                        "suspicious_elements": ["display_name_does_not_match"],
                        "sender_legitimacy_notes": "first contact from this domain",
                    },
                    "recommended_action": "needs_review",
                }
            )

        if "newsletter" in subject:
            return json.dumps(
                {
                    "summary": f"Marketing newsletter: {subject}.",
                    "action_items": [],
                    "risk_analysis": {
                        "risk_score": 5,
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

        return json.dumps(
            {
                "summary": f"General business email about {subject}.",
                "action_items": [
                    {"task": "Acknowledge sender", "owner": None, "due_date": None}
                ],
                "risk_analysis": {
                    "risk_score": 55,
                    "risk_factors": ["unknown_sender"],
                    "phishing_signals": [],
                    "urgency_signals": [],
                    "financial_risk": "medium",
                    "vendor_fraud_score": 30,
                    "wire_transfer_anomaly_score": 20,
                    "invoice_authenticity_score": None,
                    "behavioral_deviation_flags": ["first_time_sender_with_financial_ask"],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 15,
                    "suspicious_elements": [],
                    "sender_legitimacy_notes": None,
                },
                "recommended_action": "needs_review",
            }
        )

    return _client


def _digest_markdown_client(canned: str = "# Today's Inbox Shield Digest") -> Callable[[str, str], str]:
    seen: dict[str, str] = {}

    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "daily digest" in system_prompt.lower()
        parsed = json.loads(user_prompt)
        seen["aggregate"] = user_prompt
        seen["digest_date"] = parsed["digest_date"]
        return canned

    _client.seen = seen  # type: ignore[attr-defined]
    return _client


def _ingest(
    context: RouteContext,
    *,
    sender: str,
    subject: str,
    received_at: datetime | None = None,
):
    return ingest_email(
        context,
        tenant_id=TENANT,
        raw_email={
            "received_at": received_at or datetime(2026, 5, 20, 9, 0, tzinfo=timezone.utc),
            "sender": sender,
            "recipient": "ops@northstar.example",
            "subject": subject,
            "body_plain": f"Body for {subject}.",
        },
    )


def test_e2e_smoke_ingest_score_digest_one_email(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    ingested = _ingest(
        context,
        sender="vendor@example.com",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=2),
    )

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_routing_scoring_client(),
            production_tenant_id=TENANT,
        ),
    )
    assert scoring_result.analyzed == 1
    assert scoring_result.failed == 0

    digest_client = _digest_markdown_client()
    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=digest_client,
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert digest_result.digest_record_id is not None
    assert digest_result.workflow_trigger_id is not None
    assert digest_result.important_emails_count == 1
    assert digest_result.top_risks_count == 1
    assert digest_result.tasks_count == 2
    assert digest_result.digest_date == now.date()

    records = _production_records(context)
    inbound = [r for r in records if r.record_type == RecordType.EMAIL_INBOUND]
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    markers = [
        r
        for r in records
        if r.record_type == RecordType.AUDIT_VERDICT
        and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    ]
    digests = [r for r in records if r.record_type == RecordType.DAILY_DIGEST]
    triggers = [
        r
        for r in records
        if r.record_type == RecordType.WORKFLOW_TRIGGER
        and r.workflow_id == "send_daily_digest"
    ]

    assert len(inbound) == 1
    assert len(analyses) == 1
    assert len(markers) == 1
    assert len(digests) == 1
    assert len(triggers) == 1

    assert analyses[0].parent_record_id == ingested.record_id
    assert markers[0].parent_record_id == ingested.record_id
    assert triggers[0].parent_record_id == digests[0].record_id

    analysis_payload = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert analysis_payload.source_email_record_id == ingested.record_id
    assert analysis_payload.risk_analysis.risk_score == 88

    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert digest_payload.digest_markdown == "# Today's Inbox Shield Digest"
    assert digest_payload.important_emails[0].subject == "Outstanding invoice"
    assert digest_payload.important_emails[0].sender == "vendor@example.com"
    assert digest_payload.top_risks[0].risk_score == 88

    trigger_payload = WorkflowTriggerPayload.model_validate(triggers[0].payload)
    assert trigger_payload.workflow_name == "send_daily_digest"


def test_e2e_smoke_multi_email_mixed_risk_ranks_correctly(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    _ingest(
        context,
        sender="ceo@partner.example",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=3),
    )
    _ingest(
        context,
        sender="news@brand.example",
        subject="May newsletter",
        received_at=now - timedelta(hours=2),
    )
    _ingest(
        context,
        sender="hr@partner.example",
        subject="Quick check-in",
        received_at=now - timedelta(hours=1),
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_routing_scoring_client(),
            production_tenant_id=TENANT,
        ),
    )
    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_digest_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    digests = [
        r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST
    ]
    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)

    important_subjects = [entry.subject for entry in digest_payload.important_emails]
    assert important_subjects == [
        "Outstanding invoice",
        "Quick check-in",
        "May newsletter",
    ]

    top_risk_subjects = [entry.subject for entry in digest_payload.top_risks]
    assert top_risk_subjects == ["Outstanding invoice", "Quick check-in"]
    assert all(entry.risk_score >= 50 for entry in digest_payload.top_risks)

    task_titles = sorted({task.task for task in digest_payload.tasks})
    assert "Verify wire instructions out-of-band" in task_titles
    assert "Acknowledge sender" in task_titles
    assert digest_result.tasks_count == len(digest_payload.tasks)


def test_month_1_gate_five_email_digest_shows_fraud_and_ransomware_framing(tmp_path):
    """Month 1 gate: five synthetic emails produce a digest with the locked
    fraud + ransomware positioning visible in the stored markdown output.
    """

    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    subjects = [
        ("billing@vendor-pay.example", "Urgent invoice with new wire instructions"),
        ("security@identity.example", "Credential reset attachment"),
        ("news@brand.example", "May newsletter"),
        ("ops@partner.example", "Quick check-in"),
        ("ceo@lookalike.example", "Executive request before EOD"),
    ]
    for offset, (sender, subject) in enumerate(subjects, start=1):
        _ingest(
            context,
            sender=sender,
            subject=subject,
            received_at=now - timedelta(hours=offset),
        )

    def _month_1_gate_scoring_client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        parsed_input = json.loads(user_prompt)
        subject = (parsed_input.get("subject") or "").lower()

        if "invoice" in subject:
            return json.dumps(
                {
                    "summary": "Vendor invoice request includes new wire instructions and same-day pressure.",
                    "action_items": [
                        {
                            "task": "Verify wire instructions out-of-band",
                            "owner": "finance",
                            "due_date": "2026-05-21",
                        }
                    ],
                    "risk_analysis": {
                        "risk_score": 91,
                        "risk_factors": [
                            "vendor fraud",
                            "new wire instructions",
                            "same-day payment pressure",
                        ],
                        "phishing_signals": ["sender_mismatch"],
                        "urgency_signals": ["before end of day"],
                        "financial_risk": "high",
                        "vendor_fraud_score": 92,
                        "wire_transfer_anomaly_score": 88,
                        "invoice_authenticity_score": 28,
                        "behavioral_deviation_flags": [
                            "new_banking_instructions",
                            "urgency_paired_with_finance",
                        ],
                    },
                    "impersonation_analysis": {
                        "impersonation_likelihood": 65,
                        "suspicious_elements": ["vendor domain mismatch"],
                        "sender_legitimacy_notes": "Sender asks to change payment rails.",
                    },
                    "recommended_action": "block",
                }
            )

        if "credential" in subject:
            return json.dumps(
                {
                    "summary": "Credential reset lure asks the operator to open an attachment before the account is disabled.",
                    "action_items": [
                        {
                            "task": "Do not open the attachment; verify through the identity portal",
                            "owner": "ops",
                            "due_date": None,
                        }
                    ],
                    "risk_analysis": {
                        "risk_score": 86,
                        "risk_factors": [
                            "ransomware precursor",
                            "attachment risk",
                            "credential harvesting lure",
                        ],
                        "phishing_signals": ["credential_harvesting"],
                        "urgency_signals": ["account disabled warning"],
                        "financial_risk": "medium",
                        "vendor_fraud_score": 20,
                        "wire_transfer_anomaly_score": 10,
                        "invoice_authenticity_score": None,
                        "behavioral_deviation_flags": [
                            "out_of_band_pressure",
                            "first_time_sender_with_financial_ask",
                        ],
                    },
                    "impersonation_analysis": {
                        "impersonation_likelihood": 45,
                        "suspicious_elements": ["security-brand pressure"],
                        "sender_legitimacy_notes": "Credential lure uses urgent account-disabling language.",
                    },
                    "recommended_action": "block",
                }
            )

        if "executive" in subject:
            return json.dumps(
                {
                    "summary": "Executive-style request applies time pressure for an unspecified action before EOD.",
                    "action_items": [
                        {
                            "task": "Confirm the request through a known executive channel",
                            "owner": "ops",
                            "due_date": None,
                        }
                    ],
                    "risk_analysis": {
                        "risk_score": 70,
                        "risk_factors": ["executive impersonation"],
                        "phishing_signals": ["lookalike_sender"],
                        "urgency_signals": ["before EOD"],
                        "financial_risk": "medium",
                        "vendor_fraud_score": 25,
                        "wire_transfer_anomaly_score": 65,
                        "invoice_authenticity_score": None,
                        "behavioral_deviation_flags": [
                            "lookalike_sender_domain",
                            "urgency_paired_with_finance",
                        ],
                    },
                    "impersonation_analysis": {
                        "impersonation_likelihood": 80,
                        "suspicious_elements": ["lookalike executive sender"],
                        "sender_legitimacy_notes": "Sender resembles an executive workflow.",
                    },
                    "recommended_action": "needs_review",
                }
            )

        if "newsletter" in subject:
            return json.dumps(
                {
                    "summary": "Routine newsletter with no operational action required.",
                    "action_items": [],
                    "risk_analysis": {
                        "risk_score": 5,
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

        return json.dumps(
            {
                "summary": "Routine operational check-in with no severe fraud indicators.",
                "action_items": [
                    {"task": "Acknowledge sender", "owner": None, "due_date": None}
                ],
                "risk_analysis": {
                    "risk_score": 35,
                    "risk_factors": ["unknown_sender"],
                    "phishing_signals": [],
                    "urgency_signals": [],
                    "financial_risk": "low",
                    "vendor_fraud_score": 10,
                    "wire_transfer_anomaly_score": 5,
                    "invoice_authenticity_score": None,
                    "behavioral_deviation_flags": [],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 10,
                    "suspicious_elements": [],
                    "sender_legitimacy_notes": None,
                },
                "recommended_action": "safe",
            }
        )

    def _month_1_gate_digest_client(system_prompt: str, user_prompt: str) -> str:
        assert "Fraud starts in the inbox." in system_prompt
        assert "Ransomware starts with a click." in system_prompt
        parsed = json.loads(user_prompt)
        assert len(parsed["important_emails"]) == 5
        assert [risk["subject"] for risk in parsed["top_risks"]][:2] == [
            "Urgent invoice with new wire instructions",
            "Credential reset attachment",
        ]
        return """# Daily Inbox Shield Digest - 2026-05-20

## Executive Readout
- Fraud starts in the inbox: review the urgent vendor invoice before any payment moves.
- Ransomware starts with a click: block the credential reset attachment before it becomes an incident.

## Operator Guidance
- Verify payment instructions out-of-band.
- Do not open the credential reset attachment.
"""

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_month_1_gate_scoring_client,
            production_tenant_id=TENANT,
        ),
    )
    assert scoring_result.analyzed == 5
    assert scoring_result.failed == 0

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_month_1_gate_digest_client,
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )
    assert digest_result.digest_record_id is not None
    assert digest_result.important_emails_count == 5
    assert digest_result.top_risks_count == 3

    records = _production_records(context)
    assert len([r for r in records if r.record_type == RecordType.EMAIL_INBOUND]) == 5
    assert len([r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]) == 5
    digest = next(r for r in records if r.record_type == RecordType.DAILY_DIGEST)
    payload = DailyDigestPayload.model_validate(digest.payload)
    assert payload.digest_markdown is not None
    assert "Fraud starts in the inbox" in payload.digest_markdown
    assert "Ransomware starts with a click" in payload.digest_markdown
    assert "before it becomes an incident" in payload.digest_markdown

    triggers = [
        r
        for r in records
        if r.record_type == RecordType.WORKFLOW_TRIGGER
        and r.workflow_id == "send_daily_digest"
    ]
    assert len(triggers) == 1


def test_e2e_smoke_failure_isolation_does_not_block_digest(tmp_path):
    """One scoring failure must not prevent the digest from being produced
    from the surviving analyses, and the failure must be recorded.
    """
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    _ingest(
        context,
        sender="vendor@example.com",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=2),
    )
    _ingest(
        context,
        sender="news@brand.example",
        subject="Broken response",
        received_at=now - timedelta(hours=1),
    )

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_routing_scoring_client(
                garbage_for_subjects={"broken response"}
            ),
            production_tenant_id=TENANT,
        ),
    )
    assert scoring_result.analyzed == 1
    assert scoring_result.failed == 1
    assert scoring_result.failures[0].failure_reason == "invalid_json"

    records = _production_records(context)
    failures = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS_FAILURE]
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    assert len(failures) == 1
    assert len(analyses) == 1

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_digest_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert digest_result.digest_record_id is not None
    assert digest_result.important_emails_count == 1

    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert digest_payload.important_emails[0].subject == "Outstanding invoice"


def test_e2e_smoke_idempotency_across_full_pipeline(tmp_path):
    """Re-running every stage produces no duplicates."""
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    _ingest(
        context,
        sender="vendor@example.com",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=2),
    )

    scoring_config = EmailRiskScoringConfig(
        llm_client=_routing_scoring_client(),
        production_tenant_id=TENANT,
    )
    first_scoring = run_email_risk_scoring_cycle(context, config=scoring_config)
    second_scoring = run_email_risk_scoring_cycle(context, config=scoring_config)
    assert first_scoring.analyzed == 1
    assert second_scoring.analyzed == 0
    assert second_scoring.skipped == 1

    digest_config = DailyDigestConfig(
        llm_client=_digest_markdown_client(),
        production_tenant_id=TENANT,
        now_provider=_fixed_now(now),
    )
    first_digest = run_daily_digest_cycle(context, config=digest_config)
    second_digest = run_daily_digest_cycle(context, config=digest_config)
    assert first_digest.digest_record_id is not None
    assert second_digest.digest_record_id == first_digest.digest_record_id
    assert second_digest.skipped_reason == "digest already exists for date"

    records = _production_records(context)
    assert len([r for r in records if r.record_type == RecordType.EMAIL_INBOUND]) == 1
    assert len([r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]) == 1
    assert len([r for r in records if r.record_type == RecordType.DAILY_DIGEST]) == 1
    assert (
        len(
            [
                r
                for r in records
                if r.record_type == RecordType.WORKFLOW_TRIGGER
                and r.workflow_id == "send_daily_digest"
            ]
        )
        == 1
    )


def test_e2e_smoke_production_loop_runs_scoring_then_manual_digest(tmp_path):
    """Production loop with scoring enabled; digest is called separately.

    The production loop can now run the digest agent, but this E2E smoke still
    pins the standalone route: a single production cycle runs the scoring
    agent end-of-cycle and a follow-up direct call produces the digest from
    the resulting analyses.
    """
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    _ingest(
        context,
        sender="ceo@partner.example",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=3),
    )
    _ingest(
        context,
        sender="hr@partner.example",
        subject="Quick check-in",
        received_at=now - timedelta(hours=2),
    )

    cycle = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=EmailRiskScoringConfig(
                llm_client=_routing_scoring_client(),
                production_tenant_id=TENANT,
            ),
        ),
    )

    assert cycle.email_risk_scoring is not None
    assert cycle.email_risk_scoring.analyzed == 2

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_digest_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert digest_result.digest_record_id is not None
    assert digest_result.important_emails_count == 2
    digests = [
        r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST
    ]
    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert digest_payload.digest_date == date(2026, 5, 20)


def test_e2e_smoke_audit_chain_intact_from_inbound_to_digest_entries(tmp_path):
    """Sanity check that the parent_record_id graph is what consumers expect.

    EMAIL_INBOUND.record_id == EMAIL_ANALYSIS.parent_record_id
                            == completion marker.parent_record_id
    EMAIL_ANALYSIS.record_id appears as DailyDigestEmailEntry.source_analysis_record_id
    DAILY_DIGEST.record_id  == send_daily_digest WORKFLOW_TRIGGER.parent_record_id
    """
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)

    ingested = _ingest(
        context,
        sender="vendor@example.com",
        subject="Outstanding invoice",
        received_at=now - timedelta(hours=2),
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_routing_scoring_client(),
            production_tenant_id=TENANT,
        ),
    )
    run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_digest_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    records = _production_records(context)
    analysis = next(r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS)
    marker = next(
        r
        for r in records
        if r.record_type == RecordType.AUDIT_VERDICT
        and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    )
    digest = next(r for r in records if r.record_type == RecordType.DAILY_DIGEST)
    trigger = next(
        r
        for r in records
        if r.record_type == RecordType.WORKFLOW_TRIGGER
        and r.workflow_id == "send_daily_digest"
    )

    assert analysis.parent_record_id == ingested.record_id
    assert marker.parent_record_id == ingested.record_id
    assert trigger.parent_record_id == digest.record_id

    digest_payload = DailyDigestPayload.model_validate(digest.payload)
    entry = digest_payload.important_emails[0]
    assert entry.source_email_record_id == ingested.record_id
    assert entry.source_analysis_record_id == analysis.record_id

    inbound = next(r for r in records if r.record_type == RecordType.EMAIL_INBOUND)
    EmailInboundPayload.model_validate(inbound.payload)
