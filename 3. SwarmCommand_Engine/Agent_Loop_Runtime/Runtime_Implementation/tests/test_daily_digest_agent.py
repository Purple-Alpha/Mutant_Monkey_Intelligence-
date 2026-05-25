from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Callable
from uuid import UUID, uuid4

import pytest

from core.blackboard import (
    DailyDigestPayload,
    EmailAnalysisActionItem,
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailInboundPayload,
    Environment,
    RecordType,
    WorkflowTriggerPayload,
    read_records,
)
from core.drafting import (
    DAILY_DIGEST_SYSTEM_PROMPT,
    DailyDigestConfig,
    run_daily_digest_cycle,
)
from core.orchestrator import (
    RouteContext,
    submit_email_analysis,
    submit_email_inbound,
)
from core.orchestrator.routes import blackboard_path
from core.production import (
    ProductionLoopConfig,
    ProductionSignal,
    run_production_cycle,
)
from core.scoring import EmailRiskScoringConfig

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_inbound(
    context: RouteContext,
    *,
    sender: str,
    subject: str,
) -> UUID:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="cfo@northstar.example",
        subject=subject,
        body_plain="body",
    )
    result = submit_email_inbound(
        context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )
    return result.record.record_id


def _seed_analysis(
    context: RouteContext,
    *,
    source_email_record_id: UUID,
    risk_score: int,
    action_items: list[EmailAnalysisActionItem] | None = None,
    urgency_signals: list[str] | None = None,
    risk_factors: list[str] | None = None,
    recommended_action: str = "needs_review",
    produced_at: datetime | None = None,
    summary: str | None = "summary",
    tenant_default_profile: str | None = None,
    effective_profile: str | None = None,
    forced_escalation_triggers: list[str] | None = None,
) -> UUID:
    payload = EmailAnalysisPayload(
        source_email_record_id=source_email_record_id,
        produced_at=produced_at or datetime.now(timezone.utc),
        summary=summary,
        action_items=action_items or [],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=risk_factors or [],
            phishing_signals=[],
            urgency_signals=urgency_signals or [],
            financial_risk="medium",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0,
            suspicious_elements=[],
        ),
        recommended_action=recommended_action,
        tenant_default_profile=tenant_default_profile,
        effective_profile=effective_profile,
        forced_escalation_triggers=forced_escalation_triggers or [],
    )
    result = submit_email_analysis(
        context,
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        source_agent="email_risk_scoring_001",
        parent_record_id=source_email_record_id,
        payload=payload,
    )
    return result.record.record_id


def _markdown_client(canned: str = "# digest") -> Callable[[str, str], str]:
    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "daily digest" in system_prompt.lower()
        return canned

    return _client


def test_daily_digest_prompt_is_locked_to_specialization_pillars():
    prompt = DAILY_DIGEST_SYSTEM_PROMPT

    assert "PROMPT NOT YET LOCKED" not in prompt
    assert "Fraud starts in the inbox." in prompt
    assert "Ransomware starts with a click." in prompt
    assert "We stop the attack before it becomes an incident." in prompt
    assert "human-layer fraud defense" in prompt
    assert "ransomware precursor defense" in prompt
    assert "Return only the markdown body" in prompt


def test_digest_passes_locked_specialization_prompt_to_llm(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(
        context,
        sender="vendor-update@example.com",
        subject="Updated banking details",
    )
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=92,
        risk_factors=["vendor impersonation and wire-transfer pressure"],
        action_items=[EmailAnalysisActionItem(task="Verify vendor by phone", owner="ops")],
        produced_at=now - timedelta(hours=1),
    )

    captured: dict[str, str] = {}

    def _client(system_prompt: str, user_prompt: str) -> str:
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return "# Daily Inbox Shield Digest — 2026-05-20"

    run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_client,
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert captured["system_prompt"] == DAILY_DIGEST_SYSTEM_PROMPT
    assert "Fraud starts in the inbox." in captured["system_prompt"]
    assert "Ransomware starts with a click." in captured["system_prompt"]
    assert "vendor impersonation and wire-transfer pressure" in captured["user_prompt"]


def test_digest_carries_security_profile_and_escalation_fields(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(
        context,
        sender="risk@example.com",
        subject="Escalated invoice",
    )
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=88,
        risk_factors=["forced high scrutiny"],
        produced_at=now - timedelta(minutes=30),
        tenant_default_profile="low",
        effective_profile="high",
        forced_escalation_triggers=["llm_high_risk_score"],
    )

    captured: dict[str, str] = {}

    def _client(system_prompt: str, user_prompt: str) -> str:
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return "# Daily Inbox Shield Digest — 2026-05-20"

    run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_client,
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    digest_records = [
        r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST
    ]
    payload = DailyDigestPayload.model_validate(digest_records[0].payload)
    assert payload.important_emails[0].tenant_default_profile == "low"
    assert payload.important_emails[0].effective_profile == "high"
    assert payload.important_emails[0].forced_escalation_triggers == [
        "llm_high_risk_score"
    ]
    assert payload.top_risks[0].tenant_default_profile == "low"
    assert payload.top_risks[0].effective_profile == "high"
    assert payload.top_risks[0].forced_escalation_triggers == [
        "llm_high_risk_score"
    ]
    assert "Profile: <effective_profile>" in captured["system_prompt"]
    assert '"effective_profile": "high"' in captured["user_prompt"]
    assert '"tenant_default_profile": "low"' in captured["user_prompt"]
    assert '"llm_high_risk_score"' in captured["user_prompt"]


def _production_records(context: RouteContext):
    return read_records(
        blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
    )


def _fixed_now(when: datetime) -> Callable[[], datetime]:
    def _now() -> datetime:
        return when

    return _now


def test_empty_window_emits_no_digest_and_no_trigger(tmp_path):
    context = _context(tmp_path)

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)),
        ),
    )

    assert result.digest_record_id is None
    assert result.workflow_trigger_id is None
    assert result.important_emails_count == 0
    assert result.skipped_reason == "no analyses in window"

    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    assert digests == []


def test_digest_ranks_important_emails_by_risk_score_then_action_count(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)

    high_id = _seed_inbound(context, sender="big@example.com", subject="high risk")
    low_id = _seed_inbound(context, sender="small@example.com", subject="low risk")
    tied_id = _seed_inbound(context, sender="tied@example.com", subject="tied risk")

    _seed_analysis(
        context,
        source_email_record_id=low_id,
        risk_score=20,
        produced_at=now - timedelta(hours=1),
    )
    _seed_analysis(
        context,
        source_email_record_id=high_id,
        risk_score=95,
        produced_at=now - timedelta(hours=2),
    )
    _seed_analysis(
        context,
        source_email_record_id=tied_id,
        risk_score=95,
        action_items=[
            EmailAnalysisActionItem(task="approve"),
            EmailAnalysisActionItem(task="archive"),
        ],
        produced_at=now - timedelta(hours=3),
    )

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert result.digest_record_id is not None
    digest_records = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    assert len(digest_records) == 1

    payload = DailyDigestPayload.model_validate(digest_records[0].payload)
    assert [entry.subject for entry in payload.important_emails] == [
        "tied risk",
        "high risk",
        "low risk",
    ]
    assert payload.important_emails[0].risk_score == 95
    assert payload.important_emails[0].sender == "tied@example.com"


def test_digest_top_risks_filters_and_limits(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    for i in range(7):
        inbound_id = _seed_inbound(context, sender=f"s{i}@example.com", subject=f"e{i}")
        _seed_analysis(
            context,
            source_email_record_id=inbound_id,
            risk_score=40 + i * 10,
            risk_factors=[f"factor_{i}"],
            produced_at=now - timedelta(minutes=i),
        )

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    digest_records = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    payload = DailyDigestPayload.model_validate(digest_records[0].payload)

    assert all(entry.risk_score >= 50 for entry in payload.top_risks)
    assert len(payload.top_risks) == 5
    assert [entry.risk_score for entry in payload.top_risks] == [100, 90, 80, 70, 60]
    assert payload.top_risks[0].reason == "factor_6"
    assert result.top_risks_count == 5


def test_digest_tasks_dedupe_and_sort(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)

    a_id = _seed_inbound(context, sender="a@x", subject="A")
    b_id = _seed_inbound(context, sender="b@x", subject="B")
    c_id = _seed_inbound(context, sender="c@x", subject="C")

    _seed_analysis(
        context,
        source_email_record_id=a_id,
        risk_score=70,
        action_items=[
            EmailAnalysisActionItem(task="Pay invoice", owner="ops", due_date=date(2026, 6, 1)),
            EmailAnalysisActionItem(task="Follow up", owner="ops"),
        ],
        produced_at=now - timedelta(hours=1),
    )
    _seed_analysis(
        context,
        source_email_record_id=b_id,
        risk_score=90,
        action_items=[
            EmailAnalysisActionItem(task="pay invoice", owner="finance"),
            EmailAnalysisActionItem(task="Archive", due_date=date(2026, 5, 25)),
        ],
        produced_at=now - timedelta(hours=2),
    )
    _seed_analysis(
        context,
        source_email_record_id=c_id,
        risk_score=10,
        action_items=[
            EmailAnalysisActionItem(task="Verify wire", owner="cfo", due_date=date(2026, 5, 22)),
        ],
        produced_at=now - timedelta(hours=3),
    )

    run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    digest_records = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    payload = DailyDigestPayload.model_validate(digest_records[0].payload)

    task_names = [task.task for task in payload.tasks]
    lowered = [t.lower() for t in task_names]
    assert len(lowered) == len(set(lowered))

    due_dates = [task.due_date for task in payload.tasks]
    none_started = False
    for due in due_dates:
        if due is None:
            none_started = True
        elif none_started:
            pytest.fail("nulls must come after non-null due_dates")

    first_due_task = next(task for task in payload.tasks if task.due_date is not None)
    assert first_due_task.due_date == date(2026, 5, 22)


def test_digest_is_idempotent_for_same_date(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="a@x", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=80,
        produced_at=now - timedelta(hours=1),
    )

    config = DailyDigestConfig(
        llm_client=_markdown_client(),
        production_tenant_id=TENANT,
        now_provider=_fixed_now(now),
    )

    first = run_daily_digest_cycle(context, config=config)
    second = run_daily_digest_cycle(context, config=config)

    assert first.digest_record_id is not None
    assert second.digest_record_id == first.digest_record_id
    assert second.skipped_reason == "digest already exists for date"
    assert second.workflow_trigger_id is None

    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    assert len(digests) == 1


def test_digest_handles_source_record_missing_gracefully(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)

    orphan_source_id = uuid4()
    _seed_analysis(
        context,
        source_email_record_id=orphan_source_id,
        risk_score=88,
        risk_factors=["needs review"],
        action_items=[EmailAnalysisActionItem(task="orphan task")],
        produced_at=now - timedelta(hours=1),
    )

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert result.digest_record_id is not None
    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    payload = DailyDigestPayload.model_validate(digests[0].payload)

    assert payload.important_emails[0].sender is None
    assert payload.important_emails[0].subject is None
    assert payload.top_risks[0].sender is None
    assert payload.tasks[0].parent_sender is None
    assert payload.tasks[0].task == "orphan task"


def test_digest_writes_send_workflow_trigger(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="a@x", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=80,
        produced_at=now - timedelta(hours=1),
    )

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    assert result.workflow_trigger_id is not None
    triggers = [
        r
        for r in _production_records(context)
        if r.record_type == RecordType.WORKFLOW_TRIGGER
        and r.workflow_id == "send_daily_digest"
    ]
    assert len(triggers) == 1
    trigger_payload = WorkflowTriggerPayload.model_validate(triggers[0].payload)
    assert trigger_payload.workflow_name == "send_daily_digest"


def test_digest_window_excludes_old_analyses(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="a@x", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=80,
        produced_at=now - timedelta(hours=48),
    )

    result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client(),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
            digest_window_hours=24,
        ),
    )

    assert result.digest_record_id is None
    assert result.skipped_reason == "no analyses in window"


def test_digest_stores_llm_markdown(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="a@x", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=80,
        produced_at=now - timedelta(hours=1),
    )

    run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=_markdown_client("# Today's Digest\n\n- something"),
            production_tenant_id=TENANT,
            now_provider=_fixed_now(now),
        ),
    )

    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert payload.digest_markdown == "# Today's Digest\n\n- something"
    assert payload.digest_date == now.date()


# ---------------------------------------------------------------------------
# ProductionLoopConfig wiring — digest runs end-of-cycle, default OFF.
# Mirrors the pattern proven by run_email_risk_scoring_at_end_of_cycle.
# ---------------------------------------------------------------------------


def _scoring_llm_client():
    """Canned scoring-agent LLM client returning a single valid analysis JSON.

    Kept inline (not factored into a shared module) because the scoring agent
    is only exercised here for the same-cycle ordering test.
    """

    import json as _json

    response = _json.dumps(
        {
            "summary": "Vendor pushed an unexpected wire transfer with urgency.",
            "action_items": [
                {"task": "Confirm wire details with the CFO", "owner": "ops"}
            ],
            "risk_analysis": {
                "risk_score": 78,
                "risk_factors": ["vendor_impersonation_signal"],
                "phishing_signals": [],
                "urgency_signals": ["pay_today"],
                "financial_risk": "high",
                "vendor_fraud_score": 75,
                "wire_transfer_anomaly_score": 80,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": ["urgency_paired_with_finance"],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 60,
                "suspicious_elements": ["display_name_does_not_match_sender"],
            },
            "recommended_action": "needs_review",
        }
    )

    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        return response

    return _client


def test_production_loop_does_not_run_digest_by_default(tmp_path):
    context = _context(tmp_path)

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
    )

    assert result.daily_digest is None
    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    assert digests == []


def test_production_loop_runs_digest_when_opted_in(tmp_path):
    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="vendor@example.com", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=82,
        produced_at=now - timedelta(hours=1),
    )

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_daily_digest_at_end_of_cycle=True,
            daily_digest_config=DailyDigestConfig(
                llm_client=_markdown_client(),
                production_tenant_id=TENANT,
                now_provider=_fixed_now(now),
            ),
        ),
    )

    assert result.daily_digest is not None
    assert result.daily_digest.digest_record_id is not None
    digests = [r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST]
    assert len(digests) == 1


def test_production_loop_digest_flag_without_config_raises(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(ValueError, match="daily_digest_config"):
        run_production_cycle(
            context,
            tenant_id=TENANT,
            signal=ProductionSignal(source="mailbox", event_kind="email_received"),
            config=ProductionLoopConfig(
                run_daily_digest_at_end_of_cycle=True,
                daily_digest_config=None,
            ),
        )


def test_production_loop_forces_tenant_id_on_custom_digest_config(tmp_path):
    """Cycle tenant must override a misconfigured custom config's
    ``production_tenant_id``, mirroring the scoring / alert subscriber /
    consumer / regression-detector overrides.
    """

    context = _context(tmp_path)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    inbound_id = _seed_inbound(context, sender="vendor@example.com", subject="A")
    _seed_analysis(
        context,
        source_email_record_id=inbound_id,
        risk_score=82,
        produced_at=now - timedelta(hours=1),
    )

    custom = DailyDigestConfig(
        llm_client=_markdown_client(),
        production_tenant_id="wrong_tenant_overridden",
        now_provider=_fixed_now(now),
    )

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_daily_digest_at_end_of_cycle=True,
            daily_digest_config=custom,
        ),
    )

    assert result.daily_digest is not None
    assert result.daily_digest.digest_record_id is not None

    wrong_tenant_records = read_records(
        blackboard_path(
            context.blackboard_root, Environment.PRODUCTION, "wrong_tenant_overridden"
        )
    )
    assert wrong_tenant_records == []

    correct_digests = [
        r for r in _production_records(context) if r.record_type == RecordType.DAILY_DIGEST
    ]
    assert len(correct_digests) == 1


def test_production_loop_digest_sees_email_analysis_from_same_cycle(tmp_path):
    """Ordering pin: scoring runs before digest in run_production_cycle.
    Seed one EMAIL_INBOUND, enable both scoring and digest, and verify that
    the digest produced in the same cycle includes the analysis the scoring
    agent just wrote — i.e. the digest sees same-cycle scoring output.
    """

    context = _context(tmp_path)
    inbound_id = _seed_inbound(
        context, sender="vendor@example.com", subject="Outstanding invoice"
    )

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=EmailRiskScoringConfig(
                llm_client=_scoring_llm_client(),
                production_tenant_id=TENANT,
            ),
            run_daily_digest_at_end_of_cycle=True,
            daily_digest_config=DailyDigestConfig(
                llm_client=_markdown_client(),
                production_tenant_id=TENANT,
            ),
        ),
    )

    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1
    assert result.daily_digest is not None
    assert result.daily_digest.digest_record_id is not None
    assert result.daily_digest.important_emails_count == 1

    records = _production_records(context)
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    digests = [r for r in records if r.record_type == RecordType.DAILY_DIGEST]
    assert len(analyses) == 1
    assert len(digests) == 1

    digest_payload = DailyDigestPayload.model_validate(digests[0].payload)
    assert digest_payload.important_emails[0].source_email_record_id == inbound_id
    assert (
        digest_payload.important_emails[0].source_analysis_record_id
        == analyses[0].record_id
    )
