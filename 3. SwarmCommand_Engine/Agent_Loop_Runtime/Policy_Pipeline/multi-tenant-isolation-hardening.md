# Multi-Tenant Isolation Hardening
Definition of Done — Solo Mission

## Purpose
Today the runtime supports multiple tenants by convention only. Every tenant-bound API takes a `tenant_id` string, but nothing prevents a caller from mixing them — for example, promoting a policy that was signed inside tenant A's sandbox into tenant B's production. This spec closes that gap before the AI Phishing Essentials service onboards a second tenant.

## Scope and non-goals

### In scope
1. **Signed sandbox-to-production binding.** Each signed `policy_update` declares which production tenant it is for. The promotion pipeline and the Guardrail 11 gate reject any cross-tenant promotion.
2. **Per-tenant default sandbox routing.** Default sandbox tenant for tenant `X` is `sandbox_{X}`, not the shared `sandbox_default`. Existing demo flows keep working because the convention is the default, not a forced rename.
3. **Weakness report routing audit.** Every call site that ships a `weakness_report` from production into sandbox is verified to use the per-tenant sandbox id.
4. **Tenant-id forcing in all loop wirings.** `run_production_cycle` already forces `production_tenant_id` on `AlertSubscriberConfig` and `RegressionDetectorConfig`. Audit the remaining configs (`PolicyConsumerConfig`, etc.) and force the cycle tenant the same way.
5. **Tests proving rejection.** At least one explicit test per leak surface where the wrong tenant pair must produce a clear `GovernanceError`.

### Out of scope (deferred)
- Cross-process file locking on Blackboard JSONL appends and on `production_state` saves. The current single-process-per-tenant assumption is preserved and documented; concurrency safety is a separate later mission.
- Tenant-level RBAC, API authentication, or transport security. The runtime is internal-only for now.
- Migration tooling for existing demo state on disk. The demo will continue to use `tenant_demo` + `sandbox_default` as an explicit, allowed pair.

## Concrete changes

### 1. `PolicyUpdatePayload` extension
Add a signed field:

```text
target_production_tenant_id: str
```

This is part of the canonical payload that gets HMAC-signed. Any tamper to the field invalidates the signature.

For existing tests that submit policies without specifying a tenant, the helper defaults to `tenant_demo` so the test surface stays small.

### 2. Promotion pipeline (`core/policy/pipeline.py`)
Before writing any production audit or `apply_policy_update` workflow trigger:

- Validate `payload.target_production_tenant_id == config.production_tenant_id`.
- If mismatch: append a sandbox-side `audit_verdict` (REJECTED) on the signed `policy_update` with finding `cross_tenant_promotion_attempt={config.sandbox_tenant_id}->{config.production_tenant_id}` and skip promotion.

### 3. Guardrail 11 gate (`core/production_state/gate.py`)
At gate time, after signature re-verification and before history check:

- Validate `payload.target_production_tenant_id == production_tenant_id` (the gate's argument).
- If mismatch: raise `GovernanceError("cross-tenant promotion attempt: policy targets <X>, gate invoked with <Y>")`.

This is defense in depth. Even if the pipeline missed it, the gate must catch it.

### 4. Per-tenant sandbox default
Add a small helper:

```text
def default_sandbox_tenant_for(production_tenant_id: str) -> str:
    return f"sandbox_{production_tenant_id}"
```

Used as the default for:
- `AlertSubscriberConfig.sandbox_tenant_id`
- `request_rollback_to_previous` and `sign_rollback_request`
- `RegressionDetectorConfig` (when reading sandbox-side data, if any path does)
- `submit_weakness_report` callers in `core/production/loop.py`

Keep `sandbox_default` as a valid string, not magical, so existing tests pass when paired with `tenant_demo` explicitly. New tenants get per-tenant sandboxes by default.

### 5. Mutation engine and sandbox loop
Audit `core/mutation/engine.py` and `core/sandbox/loop.py` for any embedded `sandbox_default` / `tenant_demo` literals. Make sure both accept tenant context and propagate it.

### 6. Loop wiring audit
Already done for `AlertSubscriberConfig` and `RegressionDetectorConfig`. Apply the same pattern to `PolicyConsumerConfig` inside `run_production_cycle` and write down the rule in the spec: any config dataclass passed through the production loop must have its tenant id forced to the cycle's tenant.

## Hard guardrails preserved
- Guardrail 11 surface list unchanged: still exactly four mutable surfaces on `production_state`.
- No new producer agent.
- Signed payload coverage expands by exactly one field. The signing primitive is unchanged.
- Sandbox-only rule for Red agents unchanged.

## Behavior contract

| Scenario | Outcome |
|---|---|
| Policy signed for tenant A, promotion pipeline called with `production_tenant_id="A"` | Promotes normally. |
| Policy signed for tenant A, promotion pipeline called with `production_tenant_id="B"` | Sandbox `audit_verdict` REJECTED. No production write. |
| Policy signed for tenant A, somehow reaches gate for tenant B (pipeline bypass) | Gate raises `GovernanceError`. No state mutation. |
| Existing demo path (`tenant_demo` paired with `sandbox_default`) | Works unchanged. |
| New tenant `acme_ca` without explicit sandbox config | Uses `sandbox_acme_ca` as default. Routes weakness reports + sandbox writes there. |
| Weakness report attempted to ship to `sandbox_default` from a non-demo tenant | Helper picks the per-tenant default; explicit override still possible if a caller insists. |

## Verification

From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Target after this hardening: existing 75 tests still pass + at least 6 new = **81 or more passed**.

New coverage required:
1. `target_production_tenant_id` field is signed and tamper detection still works.
2. Promotion pipeline rejects cross-tenant policy and writes a sandbox REJECTED audit.
3. Gate raises `GovernanceError` when a policy signed for tenant A is gated for tenant B.
4. Default sandbox tenant for a new production tenant is `sandbox_{tenant_id}`.
5. End-to-end: tenant A and tenant B run in the same blackboard root, signed policies do not cross.
6. Existing demo flow (`tenant_demo` + `sandbox_default` explicit pair) still works.

## Phase plan (this mission, in order)

1. Spec (this file). Approved before any code changes.
2. Extend `PolicyUpdatePayload` and update the mutation engine and rollback module to populate `target_production_tenant_id`.
3. Update promotion pipeline rejection path.
4. Update Guardrail 11 gate rejection path.
5. Introduce `default_sandbox_tenant_for` helper and adopt it across loop wirings.
6. Audit + adjust sandbox loop and mutation engine for embedded tenant literals.
7. Add tests for items 1-6. Run full suite.
8. Update activity log + handshake + runtime README + master index.

Each phase is one focused commit. The mission is finished when all six new tests pass and the demo flow is unchanged.

## Known limitation (prototype scope)
Cross-process concurrency safety on Blackboard JSONL appends and on `production_state` saves remains a separate, deferred mission. The single-process-per-tenant assumption is documented in this spec and accepted for now.
