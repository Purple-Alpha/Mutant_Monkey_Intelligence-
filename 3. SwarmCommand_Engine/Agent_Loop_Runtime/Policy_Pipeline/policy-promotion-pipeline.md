# Policy Update Signing and Promotion Pipeline
Sandbox-Signed, Re-Audited, Production-Promoted

## Purpose
The pipeline is the **only** path by which a defensive change matured inside the sandbox can reach production. It enforces three guardrails simultaneously:

1. **Cryptographic signing** of every sandbox `policy_update` (HMAC-SHA256 over the canonical payload).
2. **Re-audit at the boundary** before any production-side artifact is written.
3. **Rollback target pre-check** so a rollback to a never-applied state is rejected in sandbox before production gets a workflow trigger.
4. **Idempotent promotion** so re-running the pipeline never double-applies a policy.

This pipeline does *not* mutate. Mutation belongs to the sandbox mutation engine. The pipeline only verifies, audits, and emits production-side workflow triggers that approved policies be applied on the next production cycle.

## Where It Sits

```text
Sandbox:
    mutant_evaluation
        -> mutation engine creates candidate
        -> policy_update (signed)               <-- sign() lives here
                |
                | Policy Update Signing & Promotion Pipeline
                v
Production (NEW writes):
    audit_verdict (target = policy_update record_id, signed verification recorded)
    workflow_trigger (workflow_name = "apply_policy_update")
```

## Definition of Done

### What will be created
- `core/policy/signing.py` — HMAC-SHA256 signing primitives:
  - `SigningKey(secret: bytes)` — opaque key holder
  - `default_signing_key() -> SigningKey` — deterministic dev key (env override later)
  - `canonical_payload(payload: dict, signer_id: str) -> bytes` — sorted, separator-stable JSON
  - `sign(payload, signer_id, key) -> str` — returns a hex signature id (`hmac_sha256:<digest>`)
  - `verify(payload, signer_id, signature_id, key) -> bool` — constant-time comparison
- `core/policy/pipeline.py` — promotion pipeline:
  - `PolicyPromotionConfig` — sandbox tenant, production tenant, governance/orchestrator agent ids, workflow name, signing key
  - `PolicyPromotionItemResult` — per-record outcome (`policy_update_record_id`, `verification_passed`, `production_audit`, `production_workflow_trigger`, `sandbox_rejection_audit`, `skipped_already_promoted`)
  - `PolicyPromotionResult` — counts + items
  - `run_policy_promotion_cycle(context, *, config) -> PolicyPromotionResult`
- `core/policy/__init__.py` — public exports
- `tests/test_policy_pipeline.py` — at least 4 tests (see below)

### What will be modified (minimal Codex-code surface change)
- `core/mutation/engine.py` — swap the placeholder `signature_id=f"sig_{candidate.candidate_agent_id}"` for `sign(policy_payload.model_dump(mode="json"), governance_agent_id, key)`. **No behavioral change to existing tests** — `audit.signed` stays `True`, signature is now real and verifiable.

### Behavior contract

| Input on the sandbox blackboard | Pipeline action | Production-side write |
|---|---|---|
| `policy_update` with valid signature, not yet promoted | verify ✓, write audit verdict APPROVED + workflow_trigger `apply_policy_update` | 2 records |
| rollback `policy_update` with valid signature but unknown target | write REJECTED audit verdict in sandbox; do NOT touch production | 0 records |
| `policy_update` with invalid signature | write REJECTED audit verdict in sandbox; do NOT touch production | 0 records |
| `policy_update` already referenced by a previous production audit verdict | skip (idempotent) | 0 records |
| No `policy_update` records | no-op | 0 records |

### Hard guardrails preserved
- `policy_update` records remain sandbox-only (governance model enforces this — we do not relax it).
- Production-side writes are `audit_verdict` and `workflow_trigger` only — both write types already allowed to `governance_001` and `orchestrator_001` per registry.
- No mutation occurs in production. The workflow trigger is consumed downstream; the pipeline never edits a production agent in place.
- Append-only: rejections create a new audit verdict; they never rewrite the original signed record.

### Tests (definition of success)
1. **Happy path** — sandbox emits one signed policy update; pipeline writes one APPROVED `audit_verdict` and one `workflow_trigger` (`apply_policy_update`) in production, both with `parent_record_id` chained to the sandbox policy update.
2. **Bad signature** — pipeline tampers payload before verification; pipeline records a REJECTED `audit_verdict` in sandbox; **no** production-side records.
3. **Idempotency** — happy path runs, then pipeline runs a second time; second run reports 0 new promotions and writes 0 production records.
4. **Empty queue** — no policy updates anywhere → `processed_count == 0`, no writes.
5. **Unknown rollback target** — valid signed rollback to a never-applied `(policy_name, parameters)` creates a sandbox REJECTED audit and writes no new production workflow trigger.
6. **Known rollback target** — valid signed rollback to a previously-applied `(policy_name, parameters)` still promotes normally.

### Verification command
From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Current verification target: full runtime suite passes.

Latest verified result: **51 passed**.

## Next Step After This
Promotion records now exist in production, and the production loop consumes `apply_policy_update` workflow triggers through the Guardrail 11 production-state gate.

Next missing safety feature: production-side alert subscriber that calls `request_rollback_to_previous` when a post-apply regression verdict appears.
