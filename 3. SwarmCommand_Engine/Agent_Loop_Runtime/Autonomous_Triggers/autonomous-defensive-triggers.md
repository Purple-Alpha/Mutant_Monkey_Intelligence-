# Autonomous Defensive Triggers

**Status:** Spec-first trigger layer. No autonomous runtime trigger is active yet.
**Purpose:** Define which system changes may start a bounded defensive agent loop without waiting for a human go-time prompt.
**Safety rule:** Triggers may start training, audit, or sandbox evaluation. They may not start offensive activity or mutate production without operator approval.

## 1. Trigger Principle

NorthStar should eventually respond to important signals without waiting for Matt to notice every change.

The v1 rule:

> A high-confidence system or threat signal may trigger a one-hour defensive training loop. The loop may analyze, audit, test, and recommend. It may not apply production changes on its own.

This keeps the system responsive without making it reckless.

## 2. Trigger Classes

| Trigger Class | Example | Default Response |
|---|---|---|
| Runtime baseline changed | Test count changes from 443 to 452 | Training loop: verify tests + tracking drift |
| Test failure | Full suite fails or test count drops | Audit loop: identify failure class; no closeout |
| Core runtime file changed | `core/production/loop.py`, `core/policy/pipeline.py`, `core/blackboard/models.py` | Audit loop: governance-sensitive diff review |
| Governance file changed | guardrails, LLM policy, policy pipeline specs | Audit loop: check docs/code alignment |
| Tenant override changed | override JSON or audit history updated | Evidence loop: verify effective params + audit trail |
| Sandbox weakness spike | Red battery weakness report crosses threshold | Training loop: mutation recommendation only |
| Regression alert emitted | `policy_regression_alert` appears | Audit loop: validate alert; rollback requires approval unless existing approved subscriber path applies |
| Spec/code contradiction | Spec says paused but runtime files changed | Drift loop: report contradiction |

## 3. Threat-Detected Trigger

Threat detection can trigger a defensive loop when any of these are true:

- Risk score crosses a configured threshold.
- Ransomware precursor overlay recommends a high floor.
- Multiple high-risk signals appear in a short window.
- Regression detector emits an accepted alert.
- Sandbox Red battery produces a profile weakness report above threshold.

Default action:

1. Start one-hour training loop.
2. Freeze trigger evidence.
3. Assign Builder / Auditor / Scribe / Judge roles.
4. Produce recommended defensive action.
5. Require operator approval for production impact.

## 4. No Autonomous Production Mutation

Even when a threat is detected, the trigger layer must not directly:

- Apply a policy update.
- Create a tenant override.
- Revoke a tenant override.
- Trigger rollback outside already-approved rollback subscriber semantics.
- Send client-facing communications.
- Run live LLM evals with paid API budget.

The trigger may prepare the exact command or patch for human approval.

## 5. Trigger Severity

| Severity | Meaning | Allowed Autonomous Response |
|---|---|---|
| `info` | Routine project change | Scribe summary only |
| `review` | Change may need docs/tests | Audit checklist |
| `training` | Evidence suggests a useful sandbox exercise | One-hour training loop |
| `urgent_review` | Regression or governance-sensitive issue | Audit loop + operator notification |
| `halt_recommended` | Possible unsafe production impact | Recommend kill switch / pause; operator decides |

## 6. Trigger Packet

```json
{
  "trigger_id": "trigger_YYYYMMDD_HHMMSS",
  "trigger_class": "test_failure|runtime_baseline_changed|threat_detected|sandbox_weakness_spike|governance_change|drift",
  "severity": "info|review|training|urgent_review|halt_recommended",
  "tenant_id": "tenant_demo",
  "evidence_record_ids": [],
  "changed_paths": [],
  "recommended_loop": "one_hour_training",
  "allowed_paths": [],
  "forbidden_actions": [
    "production_policy_apply",
    "tenant_override_write",
    "rollback_request",
    "client_facing_send",
    "external_network_call"
  ],
  "requires_operator_approval": true
}
```

## 7. First Trigger Profiles

### Profile A — Test Baseline Change

Starts when:

- Full suite result differs from last recorded baseline.

Response:

- Verify targeted tests.
- Update suggested tracking text.
- Flag if test count drops or full suite fails.

### Profile B — Tenant Override Change

Starts when:

- Override JSON or override audit JSONL changes.

Response:

- Run effective-parameter review.
- Verify signed baseline vs override overlay.
- Recommend evidence-package update if client-facing reporting is affected.

### Profile C — Sandbox Weakness Spike

Starts when:

- A per-profile `WEAKNESS_REPORT` exceeds configured failure-rate threshold.

Response:

- Start one-hour training loop in sandbox mode.
- Recommend mutation kind, but do not promote or apply policy.

### Profile D — Governance Drift

Starts when:

- Spec says implementation paused but runtime files changed.
- Tracking baseline and test output disagree.
- MASTER_INDEX is missing a new major artifact.

Response:

- Produce drift report.
- Do not edit runtime unless explicitly approved.

## 8. Training-Only Default

Until Matt explicitly approves production autonomy, every trigger starts in:

```text
mode = training
production_writes = blocked
external_network = blocked
client_send = blocked
operator_approval_required = true
```

## 9. Implementation Plan — Deferred

Expected first runtime script:

```text
3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/project_trigger_scan.py
```

Expected behavior:

- Read latest pytest summary if available.
- Compare project files against known trigger profiles.
- Emit a trigger packet JSON.
- Optionally create a one-hour loop mission envelope.
- Never modify runtime state in v1.

## 10. Definition Of Done For v1

- Trigger docs are indexed.
- Trigger packet schema is test-pinned.
- Project trigger scan can run locally.
- Scan can detect at least test-baseline drift and missing tracking references.
- Scan cannot write production policy, tenant override, or rollback state.

