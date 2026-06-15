# Runtime Instrumentation Runbook — Spec-First Contract

## Operational telemetry and performance characterization for Mutant Monkey Inbox Shield

**Document type:** Spec-First Contract (instrumentation only — no new agents, no new features)
**Status:** §11 SIGNED — Matt Nichol June 16th 2026. Build authorized.
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Drafted by:** Claude (advisory lane), against the June 14 2026 architecture review session
**Companion:** External architecture review, June 14 2026

---

## §0 — Purpose and governing constraint

This contract governs the addition of operational telemetry to the existing pipeline. Its sole goal is to make the organism **observable** so the following questions can be answered with real numbers:

```
How much does one email cost?
How long does one email take?
How many agents participate?
What is the worst-case path?
Can the platform scale economically?
```

**This contract authorizes instrumentation only.**

It does not authorize:
- New agents
- New detection logic
- New verdict surfaces
- New mutation or fission behavior
- Changes to any existing signed contract
- Changes to any existing agent boundary or output schema

If any of those appear in a build against this contract, the build has exceeded scope.

---

## §1 — What instrumentation means here

Instrumentation means adding **non-invasive measurement** to the existing pipeline:

- Timing wrappers around existing agent calls
- Token count capture from existing LLM responses
- Memory snapshots at pipeline entry and exit
- Event counters for existing circuit breaker, schema rejection, and tool-call rejection paths
- A structured telemetry record written per email processed

No agent logic changes. No schema changes to `AgentContribution`, `EvidenceBundle`, or any blackboard model. No new LLM calls. No new external dependencies unless strictly required for measurement.

---

## §2 — Metrics to capture

### §2.1 Latency

| Metric | Unit | How captured |
|---|---|---|
| Total pipeline execution time | ms | wall clock from ingest entry to verdict write |
| Per-agent execution time | ms | wrapper around each agent's collect/analyze call |
| Reconciliation time | ms | wrapper around ReconciliationAgent.analyze_bundle |
| EvidenceBundle assembly time | ms | wrapper around assemble_bundle |
| Blackboard write time | ms | wrapper around storage writes |

### §2.2 LLM metrics

| Metric | Unit | How captured |
|---|---|---|
| LLM calls per email | count | counter incremented per API call |
| Input tokens per call | count | from API response usage field |
| Output tokens per call | count | from API response usage field |
| Total tokens per email | count | sum across all calls |
| Estimated cost per email | USD | tokens × model rate at time of run |

Model rates must be captured at run time from a config file, not hardcoded. Rate config is operator-maintained.

### §2.3 Swarm metrics

| Metric | Unit | How captured |
|---|---|---|
| Agents executed per email | count | registry of invoked agent IDs |
| Fission children spawned | count | FissionEventLog read |
| Maximum fission depth reached | count | FissionEventLog read |
| Agent retry count | count | counter per agent invocation |

### §2.4 Resource metrics

| Metric | Unit | How captured |
|---|---|---|
| Peak memory usage | MB | tracemalloc or psutil snapshot |
| CPU time | ms | time.process_time() delta |
| Queue depth at processing time | count | pipeline queue size at entry |

### §2.5 Reliability metrics (existing paths — count only)

| Metric | How captured |
|---|---|
| Schema validation failures | counter on EvidenceBundle assembly rejection |
| Circuit breaker activations | counter on BRC breaker state change |
| Safe-Stop activations | counter on Safe-Stop entry log |
| Tool call rejection events | counter on QClassRuntime.request_tool raise |
| Contract violations (wrong-layer field) | counter on AgentContribution model_validator raise |

---

## §3 — Test corpus

### §3.1 Minimum corpus (V1)

Seven synthetic email categories, minimum 10 emails per category at V1 (100 per category deferred to V2 after instrumentation baseline is established):

| # | Category | What it tests |
|---|---|---|
| 1 | Clean legitimate email | Baseline — minimum agent activation |
| 2 | Spam / bulk mail | ImageClassifier / ContentAnalyzer path |
| 3 | Simple phishing | URL + credential harvest path |
| 4 | Business Email Compromise | Payment change + sender history + language pressure |
| 5 | Attachment-based phishing | AttachmentRisk + PDFFingerprint path |
| 6 | Unicode obfuscation | LinkInspection + lookalike domain path |
| 7 | High-complexity adversarial | Maximum agent activation — worst-case path |

All corpus emails must be synthetic. No real customer data. All senders, domains, URLs, attachments must use `.example` / `.test` / `.invalid` namespaces per existing sandbox discipline.

### §3.2 V2 corpus expansion

After V1 baseline is established and reviewed by Matt:
- 100 emails per category
- Additional category: vendor payment change with known-good contact mismatch
- Additional category: executive impersonation with domain lookalike

---

## §4 — Per-email telemetry record schema

Each processed email produces one `PipelineTelemetryRecord`. This record is written to a local telemetry store (separate from the blackboard — instrumentation must not contaminate production evidence).

```python
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

class PipelineTelemetryRecord(BaseModel):
    # Identity
    email_id: str
    run_id: str
    corpus_category: str
    timestamp_utc: str

    # Verdict
    verdict: str
    verdict_confidence: float | None = None

    # Latency
    total_pipeline_ms: float
    ingest_ms: float
    evidence_assembly_ms: float
    reconciliation_ms: float
    blackboard_write_ms: float

    # Agents
    agents_invoked: list[str]
    agent_count: int
    agent_timings: list[AgentTimingRecord]
    fission_children_spawned: int = 0
    max_fission_depth: int = 0

    # LLM
    llm_calls: list[LLMCallRecord]
    total_llm_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_estimated_cost_usd: float

    # Resources
    peak_memory_mb: float
    cpu_time_ms: float

    # Reliability
    schema_validation_failures: int = 0
    circuit_breaker_activations: int = 0
    tool_call_rejections: int = 0
    contract_violations: int = 0
```

---

## §5 — Aggregate report schema

After a corpus run, one `TelemetryAggregateReport` is produced:

```python
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

    # Latency
    pipeline_latency: LatencyPercentiles

    # Cost
    avg_cost_per_email_usd: float
    total_cost_usd: float
    avg_tokens_per_email: int
    avg_llm_calls_per_email: float

    # Agents
    avg_agents_per_email: float
    max_agents_per_email: int
    min_agents_per_email: int

    # Resources
    avg_peak_memory_mb: float
    avg_cpu_time_ms: float

    # Reliability
    total_schema_failures: int
    total_circuit_breaker_activations: int
    total_tool_call_rejections: int
    total_contract_violations: int

    # Worst-case trace reference
    worst_case_email_id: str
    worst_case_total_ms: float
```

---

## §6 — Worst-case timeline trace

The single highest-latency email from each corpus run must produce a human-readable timeline trace:

```
Example output format:

RUN: adversarial-001  VERDICT: HIGH_RISK  TOTAL: 812ms

  000ms  email_ingest_agent          [ingest]
  012ms  header_divergence_agent     [layer 2]
  034ms  email_authentication_agent  [layer 2]
  058ms  credential_phishing_agent   [layer 2]
  071ms  payment_change_agent        [layer 2]
  089ms  link_inspection_agent       [layer 2]
  103ms  attachment_risk_agent       [layer 2]
  118ms  pdf_fingerprint_agent       [layer 2]
  134ms  mfa_manipulation_agent      [layer 2]
  149ms  language_pressure_agent     [layer 2]
  167ms  known_good_contact_agent    [layer 3]
  198ms  evidence_package_agent      [layer 4]
  234ms  aggregate_corroboration     [layer 5]
  312ms  evidence_bundle_assembly    [orchestrator]
  445ms  reconciliation_agent        [p-class]
  788ms  blackboard_write            [storage]
  812ms  verdict_written             HIGH_RISK
```

This trace is the artifact that reveals actual organism behavior vs intended behavior.

---

## §7 — Output paths

```
instrumentation/
├── telemetry/
│   ├── runs/
│   │   └── {run_id}/
│   │       ├── per_email/
│   │       │   └── {email_id}_telemetry.json
│   │       ├── aggregate_report.json
│   │       ├── aggregate_report.md
│   │       └── worst_case_traces/
│   │           └── {category}_worst_case.txt
│   └── corpus/
│       └── synthetic/
│           └── {category}/
│               └── {email_id}.json
├── config/
│   └── model_rates.yaml
└── run_instrumentation.py
```

All output paths are gitignored. Telemetry is local-only — it never leaves the machine, it never goes to an external service, and it never touches production tenant data.

---

## §8 — Runner CLI

```bash
# Single category run
python run_instrumentation.py --category bec --count 10

# Full corpus run
python run_instrumentation.py --all-categories --count 10

# Single email trace
python run_instrumentation.py --email-id adversarial-001 --trace

# View aggregate report
python run_instrumentation.py --report {run_id}
```

---

## §9 — Instrumentation boundaries

**Allowed:**
- Timing wrappers (non-invasive, add no logic)
- Token count reading from existing API response objects
- Memory snapshots via `tracemalloc` or `psutil`
- Reading existing `FissionEventLog`
- Counting existing exception paths (schema rejections, tool-call raises, breaker activations)
- Writing to a separate `instrumentation/` directory

**Forbidden:**
- Modifying any existing agent logic
- Modifying `AgentContribution`, `EvidenceBundle`, or any blackboard model
- Adding new LLM calls
- Touching production tenant data or the production blackboard
- Adding external dependencies for measurement unless no stdlib alternative exists
- Publishing telemetry to any external service

---

## §10 — Success criteria

The build is complete when the operator can run a single command and get answers to:

```
1. How much does one email cost?        → avg_cost_per_email_usd
2. How long does one email take?        → p50 / p95 / p99 latency
3. How many agents participate?         → avg_agents_per_email
4. What is the worst-case path?         → worst_case trace
5. Can the platform scale economically? → operator judgment on cost × volume
```

A result is valid whether the answer is good or bad. The goal is truth, not validation.

---

## §11 — Operator Sign-Off

**Status:** SIGNED. Build authorized.

**Signed:** Matt Nichol
**Date:** June 16th 2026
