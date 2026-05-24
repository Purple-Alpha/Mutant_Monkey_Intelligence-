# Execution Contracts

**Status:** Spec-first discipline layer.
**Purpose:** Define the mission packet attached to every agent task.
**Primary goal:** One-hour autonomous focus without drift, runaway loops, cross-tenant leakage, or production-boundary bypass.

## 1. Contract Principle

Every task dispatched by the `Swarm_Orchestrator_Agent` carries an execution contract.

The contract tells the agent:

- how long it may work
- what task it is anchored to
- how much drift is allowed
- how retries and fallback work
- what tenant and RBAC scope apply
- what resources it may use
- what conditions terminate the task

## 2. Focus Window

```json
{
  "focus_window_ms": 3600000,
  "allow_interruptions": false
}
```

The one-hour focus target is `3600000` milliseconds. A shorter focus window may be used for Essentials-tier or low-priority tasks.

## 3. Task Anchor

The task anchor is the scope-lock.

```json
{
  "task_anchor": {
    "task_description": "Audit evidence-package visibility for tenant override parameters",
    "task_anchor_id": "anchor_YYYYMMDD_HHMM",
    "task_embedding_ref": "optional-vector-ref"
  }
}
```

Runtime v1 may use a plain task description and anchor id. Vector drift scoring can be added later.

## 4. Drift Threshold

```json
{
  "allowed_drift": 0.15
}
```

If drift exceeds the threshold, the orchestrator may:

- pause the agent
- re-anchor the task
- fall back to a different agent
- quarantine the session
- stop and request operator review

## 5. Retry Logic

```json
{
  "max_retries": 3,
  "retry_backoff_ms": 5000
}
```

Retries are allowed only for the same task anchor and tenant context. Retrying may not expand scope.

## 6. Fallback Logic

```json
{
  "fallback_agent": "Trend_Orchestrator_Agent"
}
```

Fallback agents may split the task, rerun the task, or prepare a blocked report. They may not bypass approval gates.

## 7. RBAC and Tenant Boundary

```json
{
  "tenant_id": "tenant_demo",
  "rbac": {
    "allowed_actions": ["read_records", "write_audit_report"],
    "forbidden_actions": ["write_policy_update", "write_tenant_override"]
  }
}
```

Every task is tenant-scoped. Cross-tenant reads and writes are contract violations.

## 8. Resource Limits

```json
{
  "resource_limits": {
    "max_cpu_ms": 5000,
    "max_memory_mb": 256,
    "max_blackboard_reads": 500,
    "max_blackboard_writes": 50
  }
}
```

The first implementation can enforce time, record-write count, and allowed write types before adding deeper CPU or memory accounting.

## 9. Kill-Switch Conditions

```json
{
  "kill_switch": {
    "on_drift_exceeded": true,
    "on_rbac_violation": true,
    "on_tenant_mismatch": true,
    "on_timeout": true,
    "on_forbidden_write_attempt": true
  }
}
```

If a kill-switch condition fires, the orchestrator terminates the task, writes an audit event, and either falls back or requests operator review.

## 10. Full Contract Schema

```json
{
  "execution_contract": {
    "focus_window_ms": 3600000,
    "allow_interruptions": false,
    "task_anchor": {
      "task_description": "string",
      "task_anchor_id": "string",
      "task_embedding_ref": "string|null"
    },
    "allowed_drift": 0.15,
    "max_retries": 3,
    "retry_backoff_ms": 5000,
    "fallback_agent": "string",
    "tenant_id": "string",
    "rbac": {
      "allowed_actions": [],
      "forbidden_actions": []
    },
    "resource_limits": {
      "max_cpu_ms": 5000,
      "max_memory_mb": 256,
      "max_blackboard_reads": 500,
      "max_blackboard_writes": 50
    },
    "kill_switch": {
      "on_drift_exceeded": true,
      "on_rbac_violation": true,
      "on_tenant_mismatch": true,
      "on_timeout": true,
      "on_forbidden_write_attempt": true
    }
  }
}
```

## 11. Operator Approval Boundary

The contract can permit long autonomous work, but it cannot permit:

- production policy apply
- tenant override create, pause, or revoke
- rollback request outside the approved subscriber semantics
- external network call
- live paid eval run
- client-facing send
- closeout status change

Those actions must remain explicit operator decisions in v1.

