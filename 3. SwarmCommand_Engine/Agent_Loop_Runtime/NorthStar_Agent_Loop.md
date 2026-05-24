# The NorthStar Agent Loop
The Organism's Heartbeat

## Purpose
The NorthStar Agent Loop is the single continuous loop that every agent, orchestrator, and subsystem participates in.

It is designed to make the swarm:
- Adaptive
- Defensive
- Self-healing
- Self-improving
- Safe
- Predictable
- Auditable

## Two Parallel Universes

### Production Swarm
Blue-only. Tenant-bound. Defensive-only.

Production protects real clients and never mutates itself.

### Sandbox Swarm
Red and Blue training environment.

Sandbox learns from anonymized weakness reports, threat intel, and historical patterns.

## MAPE-K Runtime Phases

### 1. Monitor
Agents ingest new events, signals, weakness reports, telemetry, alerts, and historical context.

### 2. Analyze
Detection and scoring agents write structured results to the Blackboard.

### 3. Plan
The orchestrator decides which workflows should run based on risk, confidence, policy, and tenant constraints.

### 4. Execute
Workflow agents perform approved tasks. Drafting agents generate summaries. Auditor agents validate outputs.

### 5. Knowledge Update
The system updates structured memory, vector memory, policies, evidence logs, and sandbox queues.

## Unified Loop Pseudocode

```text
while True:

    # Production loop
    ingest_live_data()
    orchestrate_detection()
    write_results_to_blackboard()
    auditors_validate()
    if weakness_detected:
        send_anonymized_weakness_to_sandbox()

    # Sandbox loop
    pull_weaknesses()
    red_generate_synthetic_attacks()
    blue_attempt_detection()
    if blue_fails:
        mutate_blue_agent()
        evaluate_mutant()
        if mutant_better:
            create_policy_update()

    # Governance loop
    enforce_schema()
    enforce_hop_limits()
    enforce_cooldowns()
    isolate_red_from_production()
    audit_all_updates()

    # Blackboard loop
    append_records()
    fire_triggers()
    lock_rows_for_audit()
    update_vector_memory()

    sleep(10ms)
```

## Non-Negotiable Safety Boundaries
- Red agents never access production data.
- Production Blue agents never self-mutate.
- Sandbox may test mutants, but promotion requires audit and signed policy update.
- All agent traffic must use structured schemas.
- Prose output is allowed only at approved drafting boundaries.
- Tenant data must remain isolated.
