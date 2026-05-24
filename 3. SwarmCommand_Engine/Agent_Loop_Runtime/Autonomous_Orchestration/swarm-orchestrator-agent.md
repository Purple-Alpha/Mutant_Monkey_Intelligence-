# Swarm Orchestrator Agent

**Status:** Spec-first orchestration contract. No new runtime autonomy implemented by this document.
**Purpose:** Define the master supervisor for trigger-driven, drift-resistant, multi-tenant swarm work.
**Safety rule:** The orchestrator may dispatch defensive training, audit, sandbox, and reporting work. It may not bypass production policy, tenant override, rollback, external-call, or client-send approval boundaries.

## 1. Role

The `Swarm_Orchestrator_Agent` is the governor, referee, traffic controller, and immune-system coordinator for the 60-agent organism.

It is not a generic scheduler. Its job is to:

1. Receive triggers.
2. Route work to the right agents.
3. Attach and enforce execution contracts.
4. Handle drift, fallback, escalation, and guardrail violations.

## 2. Core Responsibilities

### 2.1 Trigger Routing

The orchestrator listens for system, analytics, threat, policy, and project-control triggers.

Initial trigger families:

- `DATA_INGESTED`
- `EVENT_NORMALIZED`
- `FEATURES_READY`
- `WINDOW_CLOSED`
- `ANOMALY_DETECTED`
- `DRIFT_DETECTED`
- `RISK_SPIKE`
- `POLICY_CHANGED`
- `MODEL_UPDATED`
- `PROJECT_DRIFT_DETECTED`
- `SANDBOX_WEAKNESS_SPIKE`
- `REGRESSION_ALERT_EMITTED`

For each trigger, the orchestrator consults the trigger routing table, checks tenant slice rules, and dispatches only the agents that are enabled for the tenant and tier.

### 2.2 Execution Contract Enforcement

Every dispatched task carries an execution contract. The orchestrator enforces:

- focus-window duration
- allowed interruption policy
- retry count
- drift threshold
- tenant boundary
- RBAC action boundary
- resource limits
- fallback path
- kill-switch conditions

This is the control layer for the first one-hour autonomy goal.

### 2.3 Drift and Behavior Monitoring

The orchestrator monitors:

- task-anchor drift
- repeated failure loops
- unexpected tool or write attempts
- tenant mismatch
- abnormal resource use
- output format violations
- missing audit evidence

If drift exceeds the configured threshold, the orchestrator may re-anchor, retry, fallback, quarantine, or stop the session.

### 2.4 Guardrail Enforcement

The orchestrator enforces the same project boundaries already used by the runtime:

- tenant isolation
- RBAC
- append-only evidence records
- operator kill switch
- sandbox-only mutation
- production policy signing and promotion boundary
- no autonomous external calls unless explicitly allowed
- no autonomous client-facing sends

Production-impacting actions remain operator-approved.

## 3. Inputs and Outputs

### Inputs

- trigger events
- Blackboard record changes
- agent status updates
- drift alerts
- policy changes
- tenant override changes
- regression alerts
- sandbox weakness summaries

### Outputs

- task dispatch messages
- execution contracts
- escalation events
- quarantine events
- kill-switch recommendations
- policy-enforcement decisions
- health metrics
- one-hour mission envelopes

## 4. Internal State

The orchestrator maintains:

| State Area | Contents |
|---|---|
| Global swarm state | Active tasks, agent availability, task backlog, resource use |
| Tenant slice state | Tier, enabled agents, enabled triggers, quotas, contract defaults |
| Routing state | Trigger-to-agent mappings, fallback paths, escalation paths |
| Policy state | RBAC rules, tenant isolation rules, approval boundaries |
| Drift baselines | Per-task anchors, drift thresholds, last re-anchor events |

## 5. Decision Loop

The orchestrator runs a continuous three-stage loop:

1. **Observe:** triggers, telemetry, drift, resource usage, tenant context.
2. **Evaluate:** target agents, enabled tier, RBAC, tenant boundary, quota, contract fit.
3. **Act:** dispatch, retry, fallback, quarantine, stop, or escalate.

## 6. Escalation Logic

| Escalation Type | Condition | Default Response |
|---|---|---|
| Error escalation | Agent failure or invalid output | Retry, then fallback |
| Drift escalation | Drift threshold exceeded | Re-anchor, then fallback or quarantine |
| Policy escalation | RBAC or tenant violation | Terminate task, quarantine, log |
| Resource escalation | Quota exceeded | Pause or defer lower-priority work |
| Approval escalation | Production-impacting action requested | Stop and request operator approval |

## 7. Canonical Message Envelope

```json
{
  "origin_agent": "Swarm_Orchestrator_Agent",
  "confidence_score": 1.0,
  "tenant_id": "tenant_demo",
  "evidence_payload": {
    "trigger_type": "string",
    "target_agents": [],
    "execution_contract": {
      "focus_window_ms": 3600000,
      "allow_interruptions": false,
      "max_retries": 3,
      "allowed_drift": 0.15,
      "fallback_agent": "string"
    },
    "routing_decision": "string",
    "policy_checks": {
      "rbac_valid": true,
      "tenant_isolation_valid": true
    }
  },
  "next_required_action": "dispatch_task"
}
```

## 8. Definition of Done

The orchestrator spec is ready for runtime implementation when:

- execution contracts are schema-locked
- trigger routing is tier-aware
- tenant slice descriptors are defined
- agent enablement is mapped per tier
- operator-approval boundaries are explicit
- tests can prove the orchestrator cannot dispatch forbidden writes

