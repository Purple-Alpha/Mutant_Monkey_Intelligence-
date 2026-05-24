# Policy Rollback Primitive
Sandbox-Signed, Gate-Verified, Same-Pipeline Revert

## Purpose
The rollback primitive lets the venture **revert to a previously-applied production policy** when an alert (manual or automated) indicates the current policy is harmful. It is the *only* approved way to walk production_state backwards.

Two non-negotiables drive the design:

1. **No new path into production.** A rollback flows through the *exact same* sign → promote → Guardrail 11 gate → consumer pipeline as a forward apply. This keeps the audit trail uniform and means Guardrail 11 still owns the whole production write surface.
2. **No "reverting to nothing."** A rollback target must be a `(policy_name, parameters)` tuple that was *actually applied* to this tenant at some prior point, as proven by the on-disk audit log. The promotion pipeline now rejects unknown rollback targets before production gets a workflow trigger, and the gate keeps the same check as defense in depth.

## What this is *not*
- Not an undo stack with cursor semantics. Each rollback is itself a recorded state change. Repeated calls to `request_rollback_to_previous` can oscillate (B → A → B → A). This is acceptable for the prototype and explicitly called out below.
- Not a "reset to v0". The default initial state was never explicitly applied, so it is not in history and cannot be rolled back to. A future "reset" primitive would be a separate, signed, audited path.
- Not automated alert plumbing. The signing + promotion pre-check + gate machinery is in scope. Wiring it to real alerts is the next iteration.

## Definition of Done

### What will be created
- `core/policy/rollback.py`:
  - `sign_rollback_request(context, *, target_policy_name, target_parameters, alert_reason, source_agent="governance_001", signing_key=None) -> RouteResult` — produces one signed sandbox `policy_update` record with `is_rollback=True`.
  - `applied_state_history(context, *, production_tenant_id, sandbox_tenant_id) -> list[AppliedState]` — derives the ordered list of `(policy_name, parameters, applied_at)` for this tenant from the production audit log. The source of truth, not a side store.
  - `request_rollback_to_previous(context, *, production_tenant_id, sandbox_tenant_id, alert_reason, signing_key=None) -> RouteResult | None` — convenience that picks the second-most-recent applied state and signs a rollback for it. Returns `None` if there is no "previous" (history length < 2).
- `tests/test_policy_rollback.py` — at least 5 tests covering: end-to-end revert, gate rejection of unknown target, gate signature re-verification, `request_rollback_to_previous` no-op when history < 2, and a full closed-loop test that proves the detector's `confidence_boost` walks back to the prior value.

### What will be modified
- `core/blackboard/models.py` — `PolicyUpdatePayload` gains `is_rollback: bool = False`. Signed alongside every other field; default value means existing tests and records signed at this version stay valid.
- `core/production_state/gate.py` — `apply_signed_policy` adds one check after signature re-verification: if the signed sandbox policy_update has `is_rollback=True`, the gate confirms `(policy_name, parameters)` matches some prior entry in this tenant's applied-state history; else `GovernanceError`.
- `core/policy/__init__.py` — exports.

### Behavior contract

| Scenario | Outcome |
|---|---|
| Forward apply (`is_rollback=False`) | Identical to today. No new check fires. |
| Rollback to a previously-applied state | Gate verifies history match → state mutates back. `policy_applied` audit verdict written by `governance_001` (consumption marker, identical mechanism). |
| Rollback to a state never applied to this tenant | Sandbox REJECTED audit from the promotion pipeline. No production workflow trigger. The gate keeps the same history check if a bad trigger is ever forged or manually introduced. |
| Rollback whose signature does not verify | `GovernanceError("sandbox policy_update signature failed re-verification at gate")`. Existing behavior. |
| `request_rollback_to_previous` with history length 0 or 1 | Returns `None`. No sandbox writes. |

### Hard guardrails preserved
- All production-side writes still flow through `orchestrator_001.workflow_trigger` and `governance_001.audit_verdict`. Guardrail 11 surfaces unchanged.
- `production_state.policy.*` continues to mutate only through `apply_signed_policy`. The new check is *additional* — never a relaxation.
- Append-only on the Blackboard: a rejected rollback creates a sandbox `audit_verdict` (REJECTED) via the existing pipeline rejection path; the failed signed `policy_update` record itself stays in sandbox as evidence of the attempt.
- Defense in depth: `core/policy/pipeline.py` checks rollback target history before production promotion, while `core/production_state/gate.py` repeats the check before any state mutation.

### Known limitation (prototype scope)
Repeated rollback requests oscillate because "previous" is defined relative to the most recently applied state. Concretely:

```
applied: [A, B]               -> request_rollback_to_previous -> revert to A -> applied: [A, B, A]
applied: [A, B, A]            -> request_rollback_to_previous -> revert to B -> applied: [A, B, A, B]
```

This is acceptable now. A true undo-cursor implementation would add an explicit "current index" field, which violates Guardrail 11's current write-surface list and is therefore deferred to a future iteration.

### Verification command
From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Latest verified result: **51 passed**.

## Next Step After This
Wire a production-side **alert subscriber** that, when a high-severity production audit verdict from `audit_001` flags a regression after a policy apply, calls `request_rollback_to_previous`. That is a separate build target — out of scope here.
