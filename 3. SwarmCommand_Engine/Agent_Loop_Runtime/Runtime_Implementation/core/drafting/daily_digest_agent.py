"""NorthStar Inbox Shield — daily digest drafting agent.

Aggregates the ``EmailAnalysisPayload`` records produced by the scoring
agent across a rolling window, ranks them per the locked spec, asks the
pluggable LLM client for a markdown render, writes a ``DAILY_DIGEST``
record, and emits a ``send_daily_digest`` workflow trigger. Email delivery
itself (Resend / SendGrid / SES) is intentionally out of scope; downstream
infrastructure consumes the workflow trigger.

Conventions:
- Empty window emits no record (matches the alert subscriber / regression
  detector / policy consumer "no work to do" shape: return a result with
  counts at zero rather than writing a placeholder record).
- Idempotency is enforced by scanning for an existing ``DAILY_DIGEST``
  record for ``(tenant_id, digest_date)``. A second call on the same day
  is a no-op and returns the existing record's id.
- Source-record-missing for an analysis is handled gracefully: the digest
  entry still appears, with ``sender`` and ``subject`` set to ``None``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Callable
from uuid import UUID

from pydantic import ValidationError

from core.blackboard import (
    BlackboardRecord,
    DailyDigestEmailEntry,
    DailyDigestPayload,
    DailyDigestRiskEntry,
    DailyDigestTaskEntry,
    EmailAnalysisActionItem,
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    RecordType,
    WorkflowTriggerPayload,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_daily_digest,
    trigger_workflow,
)
from core.orchestrator.routes import blackboard_path

SEND_DAILY_DIGEST_WORKFLOW_NAME = "send_daily_digest"
DAILY_DIGEST_WORKFLOW_ID = "daily_digest"

LLMClient = Callable[[str, str], str]

DAILY_DIGEST_SYSTEM_PROMPT = """You are the NorthStar Inbox Shield Daily Digest agent.

NorthStar's specialization is human-layer fraud defense and ransomware precursor defense.
The digest must make that specialization obvious:
- Fraud starts in the inbox.
- Ransomware starts with a click.
- We stop the attack before it becomes an incident.

You will receive one JSON document with exactly these sections:
- digest_date: ISO date for the digest.
- important_emails: ranked list of email summaries with source ids, sender,
  subject, risk_score, and action_items.
- top_risks: highest-risk emails with source ids, sender, subject,
  risk_score, and reason.
- tasks: deduplicated action items with owner, due_date, parent email, risk
  score, and source ids.

Write a concise markdown digest for an SMB operator or MSP analyst. The reader
is busy, non-technical, and needs to know what to review before fraud or
ransomware risk becomes an incident.

Required structure:
1. Start with "# Daily Inbox Shield Digest — <digest_date>".
2. Add "## Executive Readout" with 2-4 bullets. Lead with fraud and
   ransomware-prevention risk, not generic email importance.
3. Add "## Highest-Risk Emails" when top_risks is non-empty. For each item,
   include subject, sender, risk_score, reason, and the immediate review
   action. Emphasize vendor fraud, executive impersonation, wire-transfer
   pressure, suspicious invoices, attachment risk, obfuscated URLs,
   credential harvesting, and MFA-fatigue lures when those signals are present
   in the provided data.
4. Add "## Action Queue" when tasks is non-empty. Preserve owner and due_date
   when present. Do not duplicate equivalent tasks.
5. Add "## Other Notable Emails" for important_emails that are not already
   covered under Highest-Risk Emails, keeping each item to one line.
6. End with "## Operator Guidance" containing 1-3 practical next steps.

Hard rules:
- Use only facts present in the JSON. Do not invent senders, links,
  attachments, owners, due dates, source ids, or risk reasons.
- Do not claim an attachment, URL, credential lure, invoice, vendor update,
  wire transfer, executive impersonation, or ransomware precursor exists unless
  the provided summary, reason, or action_items support it.
- Prefer clear operational language over security jargon.
- Keep the digest readable in under one minute.
- If a section's source list is empty, omit that section rather than writing a
  placeholder.
- Return only the markdown body. Do not include analysis notes, JSON, or
  commentary outside the markdown.
"""

_TOP_IMPORTANT_EMAILS = 10
_TOP_RISKS = 5
_TOP_RISKS_MIN_SCORE = 50


@dataclass(frozen=True)
class DailyDigestConfig:
    """Configuration for one daily digest cycle.

    ``llm_client`` is the only required dependency. ``digest_date`` defaults
    to ``now_provider().date()`` (UTC). ``digest_window_hours`` selects how
    far back to look at ``EmailAnalysisPayload`` records.
    """

    llm_client: LLMClient
    production_tenant_id: str = "tenant_demo"
    drafting_agent_id: str = "daily_digest_001"
    digest_date: date | None = None
    digest_window_hours: int = 24
    now_provider: Callable[[], datetime] = field(
        default=lambda: datetime.now(timezone.utc)
    )
    send_workflow_name: str = SEND_DAILY_DIGEST_WORKFLOW_NAME
    digest_workflow_id: str = DAILY_DIGEST_WORKFLOW_ID


@dataclass(frozen=True)
class DailyDigestResult:
    digest_record_id: UUID | None
    workflow_trigger_id: UUID | None
    important_emails_count: int
    top_risks_count: int
    tasks_count: int
    digest_date: date
    skipped_reason: str | None = None


def run_daily_digest_cycle(
    context: RouteContext,
    *,
    config: DailyDigestConfig,
) -> DailyDigestResult:
    """Aggregate, rank, render, and persist one daily digest.

    See module docstring for idempotency, empty-window, and source-record
    missing semantics.
    """

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    now = config.now_provider()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    digest_date = config.digest_date or now.date()

    production_path = blackboard_path(
        context.blackboard_root,
        Environment.PRODUCTION,
        config.production_tenant_id,
    )
    records = read_records(production_path)

    existing = _existing_digest_for(records, digest_date)
    if existing is not None:
        existing_payload = DailyDigestPayload.model_validate(existing.payload)
        return DailyDigestResult(
            digest_record_id=existing.record_id,
            workflow_trigger_id=None,
            important_emails_count=len(existing_payload.important_emails),
            top_risks_count=len(existing_payload.top_risks),
            tasks_count=len(existing_payload.tasks),
            digest_date=digest_date,
            skipped_reason="digest already exists for date",
        )

    window_start = now - timedelta(hours=config.digest_window_hours)
    analyses = _analyses_in_window(records, window_start=window_start)

    if not analyses:
        return DailyDigestResult(
            digest_record_id=None,
            workflow_trigger_id=None,
            important_emails_count=0,
            top_risks_count=0,
            tasks_count=0,
            digest_date=digest_date,
            skipped_reason="no analyses in window",
        )

    inbound_by_id = _inbound_by_record_id(records)

    enriched: list[_EnrichedAnalysis] = []
    for analysis_record, analysis_payload in analyses:
        inbound = inbound_by_id.get(analysis_payload.source_email_record_id)
        enriched.append(
            _EnrichedAnalysis(
                analysis_record_id=analysis_record.record_id,
                analysis=analysis_payload,
                inbound=inbound,
            )
        )

    important_emails = _rank_important_emails(enriched)
    top_risks = _rank_top_risks(enriched)
    tasks = _flatten_tasks(enriched)

    aggregate = {
        "digest_date": digest_date.isoformat(),
        "important_emails": [entry.model_dump(mode="json") for entry in important_emails],
        "top_risks": [entry.model_dump(mode="json") for entry in top_risks],
        "tasks": [entry.model_dump(mode="json") for entry in tasks],
    }
    markdown = config.llm_client(
        DAILY_DIGEST_SYSTEM_PROMPT, json.dumps(aggregate, sort_keys=True, ensure_ascii=False)
    )

    digest_payload = DailyDigestPayload(
        digest_date=digest_date,
        important_emails=important_emails,
        top_risks=top_risks,
        tasks=tasks,
        digest_markdown=markdown if isinstance(markdown, str) else None,
    )

    digest_record = submit_daily_digest(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.drafting_agent_id,
        workflow_id=config.digest_workflow_id,
        payload=digest_payload,
    )

    trigger = _emit_send_trigger(context, config=config, digest_record=digest_record)

    return DailyDigestResult(
        digest_record_id=digest_record.record.record_id,
        workflow_trigger_id=trigger.record.record_id,
        important_emails_count=len(important_emails),
        top_risks_count=len(top_risks),
        tasks_count=len(tasks),
        digest_date=digest_date,
        skipped_reason=None,
    )


@dataclass(frozen=True)
class _EnrichedAnalysis:
    analysis_record_id: UUID
    analysis: EmailAnalysisPayload
    inbound: BlackboardRecord | None

    @property
    def subject(self) -> str | None:
        if self.inbound is None:
            return None
        try:
            return EmailInboundPayload.model_validate(self.inbound.payload).subject
        except ValidationError:
            return None

    @property
    def sender(self) -> str | None:
        if self.inbound is None:
            return None
        try:
            return EmailInboundPayload.model_validate(self.inbound.payload).sender
        except ValidationError:
            return None


def _existing_digest_for(
    records: list[BlackboardRecord], digest_date: date
) -> BlackboardRecord | None:
    for record in records:
        if record.record_type != RecordType.DAILY_DIGEST:
            continue
        payload_date = record.payload.get("digest_date")
        if payload_date == digest_date.isoformat():
            return record
    return None


def _analyses_in_window(
    records: list[BlackboardRecord], *, window_start: datetime
) -> list[tuple[BlackboardRecord, EmailAnalysisPayload]]:
    results: list[tuple[BlackboardRecord, EmailAnalysisPayload]] = []
    for record in records:
        if record.record_type != RecordType.EMAIL_ANALYSIS:
            continue
        try:
            payload = EmailAnalysisPayload.model_validate(record.payload)
        except ValidationError:
            continue
        produced_at = payload.produced_at
        if produced_at.tzinfo is None:
            produced_at = produced_at.replace(tzinfo=timezone.utc)
        if produced_at < window_start:
            continue
        results.append((record, payload))
    return results


def _inbound_by_record_id(
    records: list[BlackboardRecord],
) -> dict[UUID, BlackboardRecord]:
    return {
        record.record_id: record
        for record in records
        if record.record_type == RecordType.EMAIL_INBOUND
    }


def _rank_important_emails(
    enriched: list[_EnrichedAnalysis],
) -> list[DailyDigestEmailEntry]:
    """Top 10 by (risk_score desc, len(action_items) desc, urgency_signals count desc)."""

    ranked = sorted(
        enriched,
        key=lambda item: (
            -item.analysis.risk_analysis.risk_score,
            -len(item.analysis.action_items),
            -len(item.analysis.risk_analysis.urgency_signals),
        ),
    )
    return [
        DailyDigestEmailEntry(
            source_email_record_id=item.analysis.source_email_record_id,
            source_analysis_record_id=item.analysis_record_id,
            subject=item.subject,
            sender=item.sender,
            summary=item.analysis.summary,
            action_items=list(item.analysis.action_items),
            risk_score=item.analysis.risk_analysis.risk_score,
        )
        for item in ranked[:_TOP_IMPORTANT_EMAILS]
    ]


def _rank_top_risks(enriched: list[_EnrichedAnalysis]) -> list[DailyDigestRiskEntry]:
    """Risk score >= 50, sort desc, top 5."""

    eligible = [
        item
        for item in enriched
        if item.analysis.risk_analysis.risk_score >= _TOP_RISKS_MIN_SCORE
    ]
    eligible.sort(key=lambda item: -item.analysis.risk_analysis.risk_score)
    return [
        DailyDigestRiskEntry(
            source_email_record_id=item.analysis.source_email_record_id,
            source_analysis_record_id=item.analysis_record_id,
            subject=item.subject,
            sender=item.sender,
            risk_score=item.analysis.risk_analysis.risk_score,
            reason=(
                item.analysis.risk_analysis.risk_factors[0]
                if item.analysis.risk_analysis.risk_factors
                else None
            ),
        )
        for item in eligible[:_TOP_RISKS]
    ]


def _flatten_tasks(enriched: list[_EnrichedAnalysis]) -> list[DailyDigestTaskEntry]:
    """Flatten action_items across analyses, dedupe on lowercased task, sort.

    Sort key: (due_date asc nulls-last, owner asc nulls-last, parent risk_score desc).
    """

    rows: list[DailyDigestTaskEntry] = []
    seen: set[str] = set()
    for item in enriched:
        for action_item in item.analysis.action_items:
            key = action_item.task.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                _task_entry_for(action_item, item),
            )

    rows.sort(
        key=lambda entry: (
            entry.due_date is None,
            entry.due_date or date.max,
            entry.owner is None,
            entry.owner or "",
            -entry.parent_risk_score,
        )
    )
    return rows


def _task_entry_for(
    action_item: EmailAnalysisActionItem, enriched: _EnrichedAnalysis
) -> DailyDigestTaskEntry:
    return DailyDigestTaskEntry(
        task=action_item.task,
        owner=action_item.owner,
        due_date=action_item.due_date,
        parent_subject=enriched.subject,
        parent_sender=enriched.sender,
        parent_risk_score=enriched.analysis.risk_analysis.risk_score,
        source_email_record_id=enriched.analysis.source_email_record_id,
        source_analysis_record_id=enriched.analysis_record_id,
    )


def _emit_send_trigger(
    context: RouteContext,
    *,
    config: DailyDigestConfig,
    digest_record: RouteResult,
) -> RouteResult:
    return trigger_workflow(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.drafting_agent_id,
        parent_record_id=digest_record.record.record_id,
        workflow_id=config.send_workflow_name,
        payload=WorkflowTriggerPayload(
            workflow_name=config.send_workflow_name,
            reason=(
                f"daily digest ready for tenant {config.production_tenant_id} "
                f"on {DailyDigestPayload.model_validate(digest_record.record.payload).digest_date}"
            ),
            priority="normal",
        ),
    )
