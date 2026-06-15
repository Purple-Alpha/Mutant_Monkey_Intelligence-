"""Non-invasive runtime instrumentation harness.

The harness measures existing detector and reconciliation calls. It does not
modify agent logic, does not change blackboard schemas, and does not create LLM
calls. Synthetic outputs are written only under ``instrumentation/telemetry/``.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import (
    AgentTimingRecord,
    LatencyPercentiles,
    LLMCallRecord,
    PipelineTelemetryRecord,
    TelemetryAggregateReport,
    TimelineEvent,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = (
    REPO_ROOT
    / "3. SwarmCommand_Engine"
    / "Agent_Loop_Runtime"
    / "Runtime_Implementation"
)
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.blackboard import (  # noqa: E402
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    TokenUsageTracker,
    VerdictLedger,
)
from core.detectors import (  # noqa: E402
    AttachmentInput,
    AttachmentSandbox,
    ContentAnalyzer,
    EmailContext,
    GeoVelocityAgent,
    ImageClassifier,
    SenderHistoryAgent,
    SenderHistoryStore,
    URLReceptor,
)
from core.knowledge import (  # noqa: E402
    AIGenContentIntelAgent,
    BECIntelAgent,
    GeoIntelAgent,
    PhishIntelAgent,
    RansomwareIntelAgent,
    TrojanDeliveryIntelAgent,
)
from core.orchestrator import DualLLMOrchestrator, QClassRuntime  # noqa: E402
from core.reconciliation import ReconciliationAgent  # noqa: E402


CATEGORIES = (
    "clean",
    "spam",
    "simple_phishing",
    "bec",
    "attachment_phishing",
    "unicode_obfuscation",
    "high_complexity_adversarial",
)
DEFAULT_RATE_CONFIG = REPO_ROOT / "instrumentation" / "config" / "model_rates.yaml"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "instrumentation" / "telemetry" / "runs"


@dataclass(frozen=True)
class TimedResult:
    value: object
    execution_ms: float
    error: str | None = None


class RuntimeInstrumentationError(Exception):
    """Raised when instrumentation input violates the runbook boundary."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timed_call(fn, *args, **kwargs) -> TimedResult:  # noqa: ANN001, ANN002, ANN003
    start = time.perf_counter()
    try:
        value = fn(*args, **kwargs)
    except Exception as exc:  # measurement records existing failure path
        return TimedResult(None, (time.perf_counter() - start) * 1000.0, repr(exc))
    return TimedResult(value, (time.perf_counter() - start) * 1000.0)


def parse_model_rates(path: Path = DEFAULT_RATE_CONFIG) -> dict[str, dict[str, float]]:
    """Parse the small operator-maintained YAML subset used by this runbook.

    The parser intentionally supports only:
        model_name:
          input_per_1k_usd: 0.0
          output_per_1k_usd: 0.0
    This avoids adding a dependency while keeping rates out of code.
    """

    if not path.exists():
        return {}
    rates: dict[str, dict[str, float]] = {}
    current: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1].strip()
            rates[current] = {}
            continue
        if current and ":" in line:
            key, value = line.strip().split(":", 1)
            rates[current][key.strip()] = float(value.strip())
    return rates


def estimate_cost(model: str, input_tokens: int, output_tokens: int, rates: dict[str, dict[str, float]]) -> float:
    rate = rates.get(model, {})
    return (
        (input_tokens / 1000.0) * rate.get("input_per_1k_usd", 0.0)
        + (output_tokens / 1000.0) * rate.get("output_per_1k_usd", 0.0)
    )


def synthetic_email(category: str, index: int) -> EmailContext:
    if category not in CATEGORIES:
        raise RuntimeInstrumentationError(f"unknown category: {category}")
    email_id = f"{category}-{index:03d}"
    base = {
        "email_id": email_id,
        "tenant_id": "tenant_instrumentation",
        "from_domain": "vendor.example",
        "sending_ip": "198.51.100.10",
        "ip_country": "CA",
        "account_home_country": "CA",
        "subject": "Project update",
        "body": "Hello, here is the synthetic status update for the week.",
        "urls": (),
        "attachments": (),
        "image_count": 0,
    }
    if category == "spam":
        base.update(subject="Newsletter", body="Bulk image mail with safe promo.", image_count=8)
    elif category == "simple_phishing":
        base.update(
            subject="Verify your account immediately",
            body="Your password will expire. Confirm your identity to avoid suspension.",
            urls=("https://secure-login-verify.example/login",),
        )
    elif category == "bec":
        base.update(
            subject="Urgent wire transfer needed",
            body=(
                "Please remit to the new account below. This must be completed "
                "today and kept confidential."
            ),
            from_domain="accounts-payable.example",
        )
    elif category == "attachment_phishing":
        base.update(
            subject="Invoice attached",
            body="Please review the attached invoice.",
            attachments=(
                AttachmentInput(
                    filename="invoice.docm",
                    sha256="unknown-synthetic-hash",
                    extension=".docm",
                ),
            ),
        )
    elif category == "unicode_obfuscation":
        base.update(
            subject="Micr0soft account verify",
            body="Unusual sign-in activity detected.",
            urls=("https://micr0soft-secure-login.example/verify",),
        )
    elif category == "high_complexity_adversarial":
        base.update(
            subject="Urgent wire transfer and account verification",
            body=(
                "Updated banking details for your next payment. Verify your "
                "account immediately and process a payment today."
            ),
            from_domain="executive-payments.example",
            sending_ip="203.0.113.55",
            ip_country="RU",
            account_home_country="CA",
            urls=("https://secure-login-verify.example/login",),
            attachments=(
                AttachmentInput(
                    filename="payment_update.docm",
                    sha256="unknown-synthetic-hash",
                    extension=".docm",
                ),
            ),
            image_count=6,
        )
    return EmailContext(**base)


def build_q_agents(
    *,
    evidence_ledger: CanonicalEvidenceLedger,
    token_tracker: TokenUsageTracker,
) -> tuple[QClassRuntime, ...]:
    store = SenderHistoryStore(
        {
            ("tenant_instrumentation", "vendor.example"): {
                "prior_interaction_count": 42,
                "last_contact_date": "2026-06-01",
                "established_vendor": True,
            }
        }
    )
    detectors = (
        SenderHistoryAgent(evidence_ledger, store=store),
        GeoVelocityAgent(evidence_ledger, GeoIntelAgent()),
        ContentAnalyzer(evidence_ledger, PhishIntelAgent(), BECIntelAgent(), token_tracker),
        URLReceptor(evidence_ledger, PhishIntelAgent()),
        AttachmentSandbox(
            evidence_ledger,
            TrojanDeliveryIntelAgent(),
            RansomwareIntelAgent(),
            token_tracker,
        ),
        ImageClassifier(evidence_ledger, AIGenContentIntelAgent()),
    )
    return tuple(
        QClassRuntime(agent_id=detector.AGENT_ID, collect=detector.analyze)
        for detector in detectors
    )


def run_email(
    *,
    email: EmailContext,
    category: str,
    run_id: str,
    output_dir: Path,
    rates: dict[str, dict[str, float]],
) -> PipelineTelemetryRecord:
    work_dir = output_dir / "_work" / email.email_id
    evidence_ledger = CanonicalEvidenceLedger(work_dir / "evidence.jsonl")
    verdict_ledger = VerdictLedger(work_dir / "verdicts.jsonl")
    token_tracker = TokenUsageTracker(work_dir / "token_usage.jsonl")
    reconciliation = ReconciliationAgent(evidence_ledger, verdict_ledger)
    q_agents = build_q_agents(evidence_ledger=evidence_ledger, token_tracker=token_tracker)
    orchestrator = DualLLMOrchestrator(q_agents=q_agents, reconciliation_agent=reconciliation)

    tracemalloc.start()
    cpu_start = time.process_time()
    pipeline_start = time.perf_counter()
    timeline: list[TimelineEvent] = [
        TimelineEvent(offset_ms=0.0, label="email_ingest", lane="ingest")
    ]
    agent_timings: list[AgentTimingRecord] = []
    schema_failures = 0

    q_outputs: list[EvidenceLedgerEntry] = []
    for q_agent in q_agents:
        result = timed_call(q_agent.collect, email)
        offset = (time.perf_counter() - pipeline_start) * 1000.0
        error = result.error
        if error:
            schema_failures += 1
        else:
            q_outputs.append(result.value)  # type: ignore[arg-type]
        agent_timings.append(
            AgentTimingRecord(
                agent_id=q_agent.agent_id,
                layer=1,
                execution_ms=result.execution_ms,
                invoked=True,
                error=error,
            )
        )
        timeline.append(
            TimelineEvent(
                offset_ms=offset,
                label=q_agent.agent_id,
                lane="layer 1",
                detail=error or "evidence_written",
            )
        )

    assembly = timed_call(orchestrator.assemble_bundle, email, q_outputs)
    assembly_offset = (time.perf_counter() - pipeline_start) * 1000.0
    timeline.append(
        TimelineEvent(
            offset_ms=assembly_offset,
            label="evidence_bundle_assembly",
            lane="orchestrator",
            detail=assembly.error or "bundle_ready",
        )
    )
    if assembly.error:
        schema_failures += 1
        raise RuntimeInstrumentationError(assembly.error)

    reconciliation_result = timed_call(
        reconciliation.analyze_bundle,
        bundle=assembly.value,
    )
    reconciliation_offset = (time.perf_counter() - pipeline_start) * 1000.0
    timeline.append(
        TimelineEvent(
            offset_ms=reconciliation_offset,
            label="reconciliation_agent",
            lane="p-class",
            detail=reconciliation_result.error or "verdict_written",
        )
    )
    if reconciliation_result.error:
        raise RuntimeInstrumentationError(reconciliation_result.error)
    verdict = reconciliation_result.value

    cpu_time_ms = (time.process_time() - cpu_start) * 1000.0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    total_pipeline_ms = (time.perf_counter() - pipeline_start) * 1000.0
    timeline.append(
        TimelineEvent(
            offset_ms=total_pipeline_ms,
            label="verdict_written",
            lane="storage",
            detail=verdict.verdict.value,
        )
    )

    llm_calls: list[LLMCallRecord] = []
    for idx, token_record in enumerate(token_tracker.read_for_tenant(email.tenant_id), start=1):
        input_tokens = token_record.token_count
        llm_calls.append(
            LLMCallRecord(
                call_id=f"{email.email_id}-token-{idx}",
                agent_id=token_record.agent_id,
                model=token_record.model_id,
                input_tokens=input_tokens,
                output_tokens=0,
                latency_ms=0.0,
                estimated_cost_usd=estimate_cost(token_record.model_id, input_tokens, 0, rates),
            )
        )

    record = PipelineTelemetryRecord(
        email_id=email.email_id,
        run_id=run_id,
        corpus_category=category,
        timestamp_utc=utc_now(),
        verdict=verdict.verdict.value,
        verdict_confidence=verdict.overall_confidence,
        total_pipeline_ms=total_pipeline_ms,
        ingest_ms=0.0,
        evidence_assembly_ms=assembly.execution_ms,
        reconciliation_ms=reconciliation_result.execution_ms,
        blackboard_write_ms=sum(t.execution_ms for t in agent_timings)
        + reconciliation_result.execution_ms,
        agents_invoked=[t.agent_id for t in agent_timings],
        agent_count=len(agent_timings),
        agent_timings=agent_timings,
        fission_children_spawned=0,
        max_fission_depth=0,
        llm_calls=llm_calls,
        total_llm_calls=len(llm_calls),
        total_input_tokens=sum(call.input_tokens for call in llm_calls),
        total_output_tokens=sum(call.output_tokens for call in llm_calls),
        total_estimated_cost_usd=sum(call.estimated_cost_usd for call in llm_calls),
        peak_memory_mb=peak / (1024 * 1024),
        cpu_time_ms=cpu_time_ms,
        schema_validation_failures=schema_failures,
        timeline_events=timeline,
    )
    write_json(output_dir / "per_email" / f"{email.email_id}_telemetry.json", record.model_dump())
    return record


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    lower = int(k)
    upper = min(lower + 1, len(ordered) - 1)
    weight = k - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def aggregate(records: list[PipelineTelemetryRecord], *, run_id: str, category: str) -> TelemetryAggregateReport:
    latencies = [r.total_pipeline_ms for r in records]
    costs = [r.total_estimated_cost_usd for r in records]
    tokens = [r.total_input_tokens + r.total_output_tokens for r in records]
    llm_calls = [r.total_llm_calls for r in records]
    agent_counts = [r.agent_count for r in records]
    worst = max(records, key=lambda r: r.total_pipeline_ms)
    return TelemetryAggregateReport(
        run_id=run_id,
        timestamp_utc=utc_now(),
        corpus_category=category,
        email_count=len(records),
        pipeline_latency=LatencyPercentiles(
            p50_ms=percentile(latencies, 0.50),
            p95_ms=percentile(latencies, 0.95),
            p99_ms=percentile(latencies, 0.99),
            max_ms=max(latencies),
            min_ms=min(latencies),
        ),
        avg_cost_per_email_usd=statistics.fmean(costs) if costs else 0.0,
        total_cost_usd=sum(costs),
        avg_tokens_per_email=int(statistics.fmean(tokens)) if tokens else 0,
        avg_llm_calls_per_email=statistics.fmean(llm_calls) if llm_calls else 0.0,
        avg_agents_per_email=statistics.fmean(agent_counts) if agent_counts else 0.0,
        max_agents_per_email=max(agent_counts) if agent_counts else 0,
        min_agents_per_email=min(agent_counts) if agent_counts else 0,
        avg_peak_memory_mb=statistics.fmean(r.peak_memory_mb for r in records),
        avg_cpu_time_ms=statistics.fmean(r.cpu_time_ms for r in records),
        total_schema_failures=sum(r.schema_validation_failures for r in records),
        total_circuit_breaker_activations=sum(r.circuit_breaker_activations for r in records),
        total_tool_call_rejections=sum(r.tool_call_rejections for r in records),
        total_contract_violations=sum(r.contract_violations for r in records),
        worst_case_email_id=worst.email_id,
        worst_case_total_ms=worst.total_pipeline_ms,
    )


def render_trace(record: PipelineTelemetryRecord) -> str:
    lines = [
        f"RUN: {record.email_id}  VERDICT: {record.verdict}  TOTAL: {record.total_pipeline_ms:.0f}ms",
        "",
    ]
    for event in sorted(record.timeline_events, key=lambda e: e.offset_ms):
        suffix = f" {event.detail}" if event.detail else ""
        lines.append(
            f"  {event.offset_ms:06.1f}ms  {event.label:<28} [{event.lane}]{suffix}"
        )
    return "\n".join(lines) + "\n"


def render_report(report: TelemetryAggregateReport) -> str:
    return "\n".join(
        [
            f"# Telemetry Aggregate Report — {report.run_id}",
            "",
            f"- Category: {report.corpus_category}",
            f"- Emails: {report.email_count}",
            f"- Latency p50/p95/p99/max: {report.pipeline_latency.p50_ms:.1f} / "
            f"{report.pipeline_latency.p95_ms:.1f} / {report.pipeline_latency.p99_ms:.1f} / "
            f"{report.pipeline_latency.max_ms:.1f} ms",
            f"- Average cost/email: ${report.avg_cost_per_email_usd:.6f}",
            f"- Average tokens/email: {report.avg_tokens_per_email}",
            f"- Average LLM calls/email: {report.avg_llm_calls_per_email:.2f}",
            f"- Average agents/email: {report.avg_agents_per_email:.2f}",
            f"- Worst-case email: {report.worst_case_email_id} ({report.worst_case_total_ms:.1f} ms)",
            "",
        ]
    )


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")


def run_corpus(
    *,
    category: str,
    count: int,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    rates_path: Path = DEFAULT_RATE_CONFIG,
) -> tuple[TelemetryAggregateReport, Path]:
    run_id = f"{category}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    output_dir = output_root / run_id
    rates = parse_model_rates(rates_path)
    records = [
        run_email(
            email=synthetic_email(category, i + 1),
            category=category,
            run_id=run_id,
            output_dir=output_dir,
            rates=rates,
        )
        for i in range(count)
    ]
    report = aggregate(records, run_id=run_id, category=category)
    write_json(output_dir / "aggregate_report.json", report.model_dump())
    (output_dir / "aggregate_report.md").write_text(render_report(report), encoding="utf-8")
    worst = max(records, key=lambda r: r.total_pipeline_ms)
    trace_path = output_dir / "worst_case_traces" / f"{category}_worst_case.txt"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(render_trace(worst), encoding="utf-8")
    return report, output_dir


def load_report(run_id: str, output_root: Path = DEFAULT_OUTPUT_ROOT) -> TelemetryAggregateReport:
    path = output_root / run_id / "aggregate_report.json"
    return TelemetryAggregateReport.model_validate_json(path.read_text(encoding="utf-8"))

