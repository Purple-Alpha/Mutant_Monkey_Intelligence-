# Governance Constitution Loop
Runtime Immune System

## Purpose
The governance loop enforces hard guardrails across production, sandbox, agents, traffic, mutation, and policy promotion.

## Loop

```text
while True:
    for packet in swarm_traffic:
        enforce_schema(packet)
        increment_hop_count(packet)
        if hop_count > 10:
            quarantine(packet)

    for agent in swarm:
        if agent_requests_clone_too_often:
            apply_cooldown(agent)

        if agent_outputs_prose:
            penalize(agent)
            strip_prose
            log_violation

    ensure:
        - Red cannot access production data
        - Blue cannot mutate in production
        - All updates are signed and audited
```

## Guardrails
- Red agents are sandbox-only.
- Production tenant data is isolated.
- Agent traffic must match schema.
- Hop counts are enforced.
- Clone requests are rate-limited.
- Prose is stripped unless explicitly allowed.
- Policy updates must be signed.
- Promotion requires audit.

## Blue Loop Write Surface (Hard Boundary)

The Blue (production) loop's **governance-level mutations** are limited to the four surfaces below. Everything else the loop touches is read-only or observational-append-only telemetry.

| # | Surface | Producer | Kind | Notes |
|---|---|---|---|---|
| 1 | `governance_001.audit_verdict` | `governance_001` | Append-only Blackboard record | The only audit verdicts that count as governance mutations. Operational `audit_001` verdicts are observational telemetry, not governance mutations. |
| 2 | `orchestrator_001.workflow_trigger` | `orchestrator_001` | Append-only Blackboard record | All production workflow triggers must flow through `orchestrator_001`. |
| 3 | `production_state.policy.active_version` | policy-apply consumer | Mutable production state | The active policy version pointer. Only changes when consuming a signed `apply_policy_update` workflow trigger. |
| 4 | `production_state.policy.parameters` | policy-apply consumer | Mutable production state | Detection thresholds / heuristic weights / etc. Only writable when explicitly authorized by the signed workflow trigger (see *"if allowed"* in the source rule). |

### What this rule means in practice

- **Observational appends** by the Blue loop (`ingest_event`, `detection_result`, `risk_score`, `audit_001.audit_verdict`, anonymized `weakness_report` to sandbox) are *not* governance mutations. They are evidence and telemetry.
- **Governance mutations** are the four surfaces above. No other in-place state may be modified in production by Blue.
- **Red agents** still cannot touch any production surface. This rule constrains Blue further, on top of the existing Red prohibition.
- **The policy-apply consumer** routes its writes through the gated `core/production_state/` module that enforces this surface mechanically. Direct edits to production state from anywhere else in code are a governance violation and must be quarantined.

### Enforcement points

| Surface | Enforcement |
|---|---|
| 1 & 2 | Already enforced by `core/orchestrator/registry.py`: `governance_001`'s `allowed_write_types` includes `AUDIT_VERDICT` and `POLICY_UPDATE`; `orchestrator_001`'s includes `WORKFLOW_TRIGGER`, `INGEST_EVENT`, `WEAKNESS_REPORT`. Production-loop writes to other types are rejected by `validate_record_against_registry`. |
| 3 & 4 | Enforced by `core/production_state/gate.py`. The `ProductionPolicyState` dataclass is frozen; mutation requires invoking the gate function with a verified signed workflow trigger record as evidence. Any other attempt raises `GovernanceError`. |

### Open question (flagged for Matt)
The rule says `production_state.policy.parameters (if allowed)`. The first version of the gate treats the signed workflow trigger as authorizing both `active_version` **and** `parameters`. A finer-grained `parameters_change_authorized` flag on the workflow trigger payload may be appropriate later.

## Rollback Primitive (Walking the Write Surface Backwards)

A rollback is the **only** approved way to mutate `production_state` to a prior value. It is intentionally constrained:

- A rollback is just a sandbox `policy_update` record with `is_rollback=True`, signed by `governance_001` with the same HMAC primitive used for forward applies.
- It flows through the **same** signing → promotion pipeline → workflow_trigger → Guardrail 11 gate → consumer path. No new write surface, no new producer agent, no special-case bypass.
- The promotion pipeline first mirrors the rollback history check at the sandbox boundary. If a signed rollback targets a `(policy_name, parameters)` tuple that was never applied to this tenant, the pipeline writes a sandbox REJECTED audit and does **not** create a production `workflow_trigger`.
- The gate keeps the same check when `is_rollback=True`: the target must match a state that was **previously applied** to this tenant per the production audit log (`policy_applied` audit verdicts → workflow_triggers → boundary audits → sandbox `policy_update` records). If a bad trigger is forged or manually introduced, the gate raises `GovernanceError` and the state is not mutated.
- The default initial state (`v0`, empty parameters) is **not** rolled-back-to-able. It was never explicitly applied, so it is not in history. Resetting to "no policy" would need a separate, signed, audited primitive that does not yet exist.

### What a rollback record cannot do
- Cannot mutate any production surface other than `policy.active_version` and `policy.parameters` — same Guardrail 11 surface as forward applies.
- Cannot promote without a valid signature — the promotion pipeline's existing signature re-verification rejects forgeries before any production write occurs.
- Cannot apply to a state that was never reached on this tenant. The normal pipeline blocks it before production; the gate blocks it again before mutation.

### Known limitation (prototype scope)
The convenience helper `request_rollback_to_previous` reverts to the second-most-recent applied state. Each rollback is itself a recorded state change, so repeated calls oscillate (`B -> A -> B -> A`). A true undo-cursor implementation would need an explicit "current index" field, which would add a new write surface and is therefore deferred.

### Enforcement point
- `core/policy/pipeline.py` :: rollback pre-check — runs after signature verification, before any production audit or workflow trigger is written.
- `core/production_state/gate.py` :: `_rollback_target_is_in_history` — runs after signature re-verification, before any state mutation.

## Violations
Violations should create:
- Quarantine record
- Agent penalty record
- Audit log entry
- Optional cooldown
- Optional manual review

## Governance Outputs
- Audit logs
- Quarantine events
- Policy approval records
- Agent cooldown records
- Promotion signatures
