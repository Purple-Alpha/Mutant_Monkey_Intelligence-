# Production Swarm Loop
Tenant-Bound, Defensive-Only

## Purpose
The production loop protects real clients. It is Blue-only and does not mutate, clone, or experiment on live tenant data.

## Loop

```text
while True:
    # 1. Monitor
    ingest new emails, alerts, and telemetry
    write to Blackboard append-only

    # 2. Analyze
    orchestrator assigns tasks to detection agents
    detection agents write structured JSON results to Blackboard
    scoring agents compute risk

    # 3. Plan
    if risk > threshold:
        orchestrator triggers workflow agents

    # 4. Execute
    workflow agents perform tasks
    drafting agents generate summaries
    auditor agents validate outputs

    # 5. Knowledge Update
    if detection confidence < policy threshold:
        flag pattern as weakness
        send anonymized pattern to Sandbox Training Queue
```

## Allowed Actions
- Detect
- Score
- Report
- Trigger approved training workflows
- Trigger approved evidence workflows
- Send anonymized weakness reports to sandbox

## Disallowed Actions
- No mutation
- No Red agent activity
- No offensive generation
- No tenant data leakage
- No direct policy promotion

## Outputs
- Detection records
- Risk scores
- Training triggers
- Reporting triggers
- Evidence records
- Weakness reports
