MODE: RESEARCH
AUTHORIZED_TASK: Research next phase requirements
ASSIGNED_TO: ChatGPT
NEXT_PROMPT_GOES_TO: ChatGPT
BLOCKED_UNTIL: ChatGPT research + Gemini cross-check returned; Claude drafts concept doc
OPERATOR_ACTION_REQUIRED: NO

INSTRUMENTATION SCOPE (strictly enforced):
  - Timing wrappers around existing agent calls
  - Token count capture from existing LLM response objects
  - Memory snapshots via tracemalloc or psutil
  - Event counters on existing exception paths only
  - PipelineTelemetryRecord written per email (separate from blackboard)
  - TelemetryAggregateReport after corpus run
  - Worst-case timeline trace for highest-latency email per category
  - CLI: run_instrumentation.py
  - Output: instrumentation/ directory (gitignored)

FORBIDDEN (build fails contract if any of these appear):
  - Modifying any existing agent logic
  - Modifying AgentContribution, EvidenceBundle, or any blackboard model
  - Adding new LLM calls
  - Touching production tenant data or production blackboard
  - New external dependencies unless no stdlib alternative exists
  - Publishing telemetry to any external service

NEXT_GATE: dual-model research packet committed, then concept doc committed

REVIEW_PENDING_ITEMS:
  - Runtime Instrumentation telemetry output and worst-case timeline trace — Matt review pending
  - Blast Radius Controller Adversarial #101 evidence — review pending; #89 hardening claim withheld

ADVERSARIAL_QUEUE (not blocked — runs in parallel):
  #101 BRC Adversarial     GATED — review pending, hardening claim withheld

NOTE: Instrumentation build takes priority. BRC Adversarial after instrumentation is
gated or if Cursor has a separate session available.

LAST_COMPLETED: Runtime Instrumentation build — focused tests 4 passed; related instrumentation / DualLLM / Reconciliation suites 31 passed / 5 xfailed; high-complexity §6 worst-case trace generated at instrumentation/telemetry/runs/high_complexity_adversarial-20260615T034529Z-5f9385d1/worst_case_traces/high_complexity_adversarial_worst_case.txt; no existing agent schema changes; no new LLM calls

LAST_COMPLETED: Blast Radius Controller Adversarial Test Suite #101 — built against §11 signed contract; all 47 BRC-ADV IDs across 12 families executed; three proven vulnerabilities patched only after failing tests (unsafe tenant routing keys, forged control-plane authority payloads, malformed/failed explicit pre-dispatch token locks); BRC adversarial + existing BRC regression 97 passed / 8 xfailed; related control-plane sweep 231 passed / 21 xfailed; split Grok gates 0/0 (`audit_outputs/blast_radius_controller_adversarial_runtime_20260615T051019Z.md`, `audit_outputs/blast_radius_controller_adversarial_gate_scope_20260615T051129Z.md`, `audit_outputs/blast_radius_controller_adversarial_tests_20260615T051227Z.md`); Blast Radius Controller #89 remains 95 ELITE but is NOT marked ADVERSARIALLY HARDENED until independent review
