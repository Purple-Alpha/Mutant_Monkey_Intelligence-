"""Telemetry models for the Runtime Instrumentation runbook.

These models are instrumentation-only. They do not alter AgentContribution,
EvidenceBundle, blackboard records, detector outputs, or verdict schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentTimingRecord(BaseModel):
    agent_id: str
    layer: int
    execution_ms: float
    invoked: bool
    retry_count: int = 0
    error: str | None = None


class LLMCallRecord(BaseModel):
    call_id: str
    agent_id: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    estimated_cost_usd: float


class TimelineEvent(BaseModel):
    offset_ms: float
    label: str
    lane: str
    detail: str = ""


class PipelineTelemetryRecord(BaseModel):
    email_id: str
    run_id: str
    corpus_category: str
    timestamp_utc: str

    verdict: str
    verdict_confidence: float | None = None

    total_pipeline_ms: float
    ingest_ms: float
    evidence_assembly_ms: float
    reconciliation_ms: float
    blackboard_write_ms: float

    agents_invoked: list[str]
    agent_count: int
    agent_timings: list[AgentTimingRecord]
    fission_children_spawned: int = 0
    max_fission_depth: int = 0

    llm_calls: list[LLMCallRecord]
    total_llm_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_estimated_cost_usd: float

    peak_memory_mb: float
    cpu_time_ms: float

    schema_validation_failures: int = 0
    circuit_breaker_activations: int = 0
    tool_call_rejections: int = 0
    contract_violations: int = 0

    timeline_events: list[TimelineEvent] = Field(default_factory=list)


class LatencyPercentiles(BaseModel):
    p50_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    min_ms: float


class TelemetryAggregateReport(BaseModel):
    run_id: str
    timestamp_utc: str
    corpus_category: str
    email_count: int

    pipeline_latency: LatencyPercentiles

    avg_cost_per_email_usd: float
    total_cost_usd: float
    avg_tokens_per_email: int
    avg_llm_calls_per_email: float

    avg_agents_per_email: float
    max_agents_per_email: int
    min_agents_per_email: int

    avg_peak_memory_mb: float
    avg_cpu_time_ms: float

    total_schema_failures: int
    total_circuit_breaker_activations: int
    total_tool_call_rejections: int
    total_contract_violations: int

    worst_case_email_id: str
    worst_case_total_ms: float

