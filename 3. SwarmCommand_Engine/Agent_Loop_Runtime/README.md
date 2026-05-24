# Agent Loop Runtime
NorthStar Agent Loop - The Organism's Heartbeat

## Purpose
This folder defines the unified runtime loop for the future SwarmCommand agent system.

It connects:
- Blackboard shared memory
- MAPE-K breathing engine
- Production swarm
- Sandbox swarm
- Red/Blue training loop
- Mutation engine
- Governance constitution
- Future 60-agent swarm

## Core Rule
Production never mutates itself.

Production may only detect, score, report, execute approved workflows, and send anonymized weakness reports to the sandbox.

Sandbox is the only place where mutation, adversarial testing, and baseline promotion are allowed.

## Runtime Phases
The loop follows MAPE-K:
1. Monitor
2. Analyze
3. Plan
4. Execute
5. Knowledge Update

## Folder Map
- `NorthStar_Agent_Loop.md` - full unified concept.
- `Blackboard_Engine/` - shared memory and event model.
- `Production_Swarm_Loop/` - tenant-bound defensive loop.
- `Sandbox_Swarm_Loop/` - Red/Blue training loop.
- `Mutation_Engine/` - sandbox-only mutation and promotion logic.
- `Autonomous_Workflows/` - bounded one-hour training-loop protocol.
- `Autonomous_Triggers/` - trigger taxonomy for defensive training, audit, and sandbox escalation.
- `Autonomous_Orchestration/` - orchestrator, execution-contract, trigger-routing, tenant-slice, and agent-enablement specs.
- `Policy_Pipeline/` - signing + cross-boundary promotion pipeline spec.
- `Governance_Constitution/` - guardrails, schemas, audit rules.
- `Runtime_Implementation/` - build roadmap and future implementation notes.

## Build Status
Prototype runtime implementation exists under `Runtime_Implementation/`.

This is still not production-deployable software, but the local runtime path is tested end-to-end.

## First Build Target
Start with `Blackboard_Engine/python-blackboard-models.md`.

This defines the first Python/Pydantic models Manus should implement before building orchestration, sandbox mutation, or policy promotion.

## Current Implementation
The first Blackboard Python scaffold now exists under:

- `Runtime_Implementation/core/blackboard/models.py`
- `Runtime_Implementation/core/blackboard/storage.py`
- `Runtime_Implementation/tests/test_blackboard_models.py`

Current test command:

`python -m pytest tests`

Latest result:

`75 passed`

## Next Build Target
Detector now wired into `run_production_cycle` end-of-cycle (default OFF). Codex audit of the detector is pending. Multi-tenant isolation DoD spec landed; implementation pending. Candidates for the next build target:

1. **Multi-tenant isolation hardening implementation** — start with the signed `target_production_tenant_id` field per the spec.
2. **Operator kill switch** — small, high-leverage RSI-safety primitive.
3. **Codex regression detector audit findings** — react when they come back.

## Current Orchestrator Implementation
The first internal routing layer now exists under:

- `Runtime_Implementation/core/orchestrator/registry.py`
- `Runtime_Implementation/core/orchestrator/routes.py`
- `Runtime_Implementation/tests/test_orchestrator_routes.py`

Latest test result:

`14 passed`

## Current Production Loop Implementation
The first Blue-only production loop now exists under:

- `Runtime_Implementation/core/production/loop.py`
- `Runtime_Implementation/tests/test_production_loop.py`

Latest full runtime test result:

`17 passed`

## Current Sandbox Loop Implementation
The first Red/Blue sandbox loop now exists under:

- `Runtime_Implementation/core/sandbox/loop.py`
- `Runtime_Implementation/tests/test_sandbox_loop.py`

Latest full runtime test result:

`22 passed`

## Current Mutation Engine Implementation
The first sandbox-only mutation engine now exists under:

- `Runtime_Implementation/core/mutation/engine.py`
- `Runtime_Implementation/tests/test_mutation_engine.py`

The engine now signs every emitted policy update with HMAC-SHA256 via `core/policy/signing.py` (replacing the earlier placeholder string).

## Current Policy Update Signing and Promotion Pipeline
The first cross-boundary policy promotion pipeline now exists under:

- `Runtime_Implementation/core/policy/signing.py` - HMAC-SHA256 sign / verify primitives
- `Runtime_Implementation/core/policy/pipeline.py` - load → verify → rollback pre-check → audit at boundary → emit `apply_policy_update` workflow trigger → idempotent on rerun
- `Runtime_Implementation/core/policy/rollback.py` - rollback primitive: `sign_rollback_request`, `applied_state_history`, `request_rollback_to_previous`
- `Runtime_Implementation/tests/test_policy_pipeline.py` - 7 tests
- `Runtime_Implementation/tests/test_policy_rollback.py` - 6 tests
- `Policy_Pipeline/policy-promotion-pipeline.md` - Definition of Done spec
- `Policy_Pipeline/policy-rollback-primitive.md` - Definition of Done spec for rollback

## Current production_state Gate (Guardrail 11)
The Blue-loop write surface for production state mutations now exists under:

- `Runtime_Implementation/core/production_state/state.py` - frozen `ProductionPolicyState` + atomic JSON persistence
- `Runtime_Implementation/core/production_state/gate.py` - `apply_signed_policy` (the only function authorized to mutate production_state; requires a full evidence chain and re-verifies the HMAC signature at the gate)
- `Runtime_Implementation/tests/test_production_state.py` - 9 tests
- `Governance_Constitution/governance-constitution-loop.md` - "Blue Loop Write Surface (Hard Boundary)" section
- `PROJECT_GUARDRAILS.md` - Guardrail 11

## Closed Production Policy Loop
The production loop now reads `production_state.policy.parameters` into its detector each cycle and consumes pending `apply_policy_update` triggers at the end of each cycle through the Guardrail 11 gate:

- `Runtime_Implementation/core/production/policy_consumer.py` - `apply_pending_policies` + `find_unconsumed_apply_triggers`; only emits `governance_001.audit_verdict` (workflow_id `policy_applied`) as the consumption marker
- `Runtime_Implementation/core/production/loop.py` - detector reads `confidence_boost` from `production_state.policy.parameters`; cycle ends with `apply_pending_policies` (configurable)
- `Runtime_Implementation/core/blackboard/models.py` - `PolicyUpdatePayload` now carries a signed `parameters` field
- `Runtime_Implementation/core/mutation/engine.py` - mutation engine fills `parameters` based on `mutation_kind`
- `Runtime_Implementation/tests/test_production_loop_integration.py` - 3 integration tests including the closed-loop end-to-end

End-to-end loop (proven by `test_end_to_end_signed_policy_changes_next_cycle_detector_confidence`):

```text
signal -> Blue detection (cycle 1, default params)
       -> weakness report to sandbox
       -> sandbox Red/Blue training
       -> mutation candidate
       -> mutation engine signs policy_update with parameters={"confidence_boost": X}
       -> policy promotion pipeline verifies signature, writes APPROVED governance_001 audit + orchestrator_001 apply_policy_update workflow_trigger in production
       -> next production cycle (cycle 2) ends by consuming the trigger:
            * Guardrail 11 gate re-verifies signature, mutates production_state
            * governance_001 writes policy_applied audit verdict
       -> next production cycle (cycle 3) loads new production_state
       -> Blue detector now applies confidence_boost
       -> same low-confidence signal now scores X higher
```

Latest full runtime test result:

`75 passed`

## Rollback Primitive
A sandbox-signed "revert to previous policy" path that flows through the same Guardrail 11 gate as a forward apply. The promotion pipeline now also mirrors the gate's history check before writing a production `workflow_trigger`: when the signed `policy_update` has `is_rollback=True`, the target `(policy_name, parameters)` must match a state previously applied to this tenant per the production audit log. Bad rollback targets are rejected in sandbox before they reach production; the gate retains the same check as defense in depth.

- `Runtime_Implementation/core/policy/rollback.py` - `sign_rollback_request`, `applied_state_history`, `request_rollback_to_previous`
- `Runtime_Implementation/core/policy/pipeline.py` - rollback target pre-check before production promotion
- `Runtime_Implementation/core/production_state/gate.py` - history check (`_rollback_target_is_in_history`) added after signature re-verification, before any state mutation
- `Runtime_Implementation/core/blackboard/models.py` - `PolicyUpdatePayload.is_rollback: bool = False`, signed alongside the rest of the payload
- `Runtime_Implementation/tests/test_policy_rollback.py` - 6 tests including end-to-end "apply A → apply B → rollback → state == A"
- `Policy_Pipeline/policy-rollback-primitive.md` - Definition of Done spec
- `Governance_Constitution/governance-constitution-loop.md` - rollback semantics + known oscillation limitation

## Policy Regression Alert Subscriber
The trigger side of the rollback story. Operators (or, later, an automated detector) call `emit_regression_alert(context, reason=..., severity=...)`, which writes one `audit_001.audit_verdict` in production with `workflow_id="policy_regression_alert"` targeting the most-recent `policy_applied` audit. At end of each production cycle (default ON), the subscriber scans for unconsumed alerts, signs a rollback via `request_rollback_to_previous`, and writes a `regression_alert_consumed` marker so each alert fires exactly once. The signed sandbox rollback then flows through the unchanged promotion pipeline + Guardrail 11 gate. State reverts.

- `Runtime_Implementation/core/production/alert_subscriber.py` - `emit_regression_alert`, `find_unconsumed_alerts`, `run_alert_subscriber_cycle`
- `Runtime_Implementation/core/production/loop.py` - `ProductionLoopConfig.run_alert_subscriber_at_end_of_cycle: bool = True`; `ProductionLoopResult.alert_subscriber: AlertSubscriptionResult | None`
- `Runtime_Implementation/tests/test_alert_subscriber.py` - 8 tests including end-to-end "apply A -> apply B -> emit alert -> subscriber + promote + consume -> state == A"
- `Policy_Pipeline/policy-regression-alert-subscriber.md` - Definition of Done spec

Properties:
- Uses only existing allowed write surfaces (`audit_001.audit_verdict` operational telemetry + the sandbox `policy_update` produced by `request_rollback_to_previous`). Guardrail 11 surface list unchanged.
- Insufficient-history alerts (history < 2 applied policies) are dead-lettered with `requires_human_review=True` rather than retried forever.
- Idempotent: re-running the subscriber after a successful run is a no-op.

## Policy Regression Detector
The first automated producer of `policy_regression_alert` verdicts. It evaluates post-apply production telemetry for the most recent `policy_applied` audit, waits for a configurable sample floor, counts alert-like samples using detection confidence and paired risk scores, and emits a subscriber-compatible alert when the ratio crosses threshold. It also writes a `policy_regression_detector_checked` marker so the same applied policy is not evaluated twice.

- `Runtime_Implementation/core/production/regression_detector.py` - `run_regression_detector_cycle`, `RegressionDetectorConfig`, `RegressionDetectorResult`
- `Runtime_Implementation/tests/test_regression_detector.py` - 7 tests including detector -> subscriber -> promotion -> consumer rollback -> state reverts
- `Policy_Pipeline/policy-regression-detector.md` - Definition of Done spec

Properties:
- Existing surfaces only: writes `audit_001.audit_verdict` records for alerts and checked markers.
- Conservative sampling: insufficient post-apply samples create no marker, allowing future telemetry to complete the evaluation window.
- Standalone for now: not yet wired into `run_production_cycle`, so Codex's alert-subscriber audit stays stable.

## Multi-Tenant Isolation Hardening
Each signed `policy_update` is bound to a specific production tenant by a new `target_production_tenant_id` field. The HMAC-SHA256 signature covers the field; any tamper invalidates the signature. Two defenses run on every promotion:

1. The promotion pipeline rejects a signed update whose `target_production_tenant_id` does not match `PolicyPromotionConfig.production_tenant_id` and writes a sandbox-side REJECTED `audit_verdict` with finding `cross_tenant_promotion_attempt={sandbox_tenant_id}->{production_tenant_id}`. No production write happens.
2. The Guardrail 11 gate (`apply_signed_policy`) independently checks the same constraint between signature re-verification and the rollback-history check, raising `GovernanceError("cross-tenant promotion attempt: policy targets <X>, gate invoked with <Y>")` if the pipeline ever misses. The kill-switch outer check is unchanged; it remains the outermost gate.

A helper `default_sandbox_tenant_for(production_tenant_id) -> str` (in `core/orchestrator/tenants.py`) returns `f"sandbox_{X}"` for new tenants and is applied by `run_production_cycle` when forcing `AlertSubscriberConfig` and `PolicyConsumerConfig` for a cycle whose tenant differs from the config's `production_tenant_id`.

The long-standing demo flow (`tenant_demo` + `sandbox_default` explicit pair) is unchanged: the legacy class-level defaults stay, and `PolicyUpdatePayload.target_production_tenant_id` defaults to `"tenant_demo"` so existing fixtures keep working.

- `Runtime_Implementation/core/blackboard/models.py` - signed `PolicyUpdatePayload.target_production_tenant_id`
- `Runtime_Implementation/core/orchestrator/tenants.py` - `default_sandbox_tenant_for`
- `Runtime_Implementation/core/mutation/engine.py` - `MutationEngineConfig.production_tenant_id` populates the signed field
- `Runtime_Implementation/core/policy/pipeline.py` - cross-tenant rejection at the sandbox-to-production boundary
- `Runtime_Implementation/core/policy/rollback.py` - rollback module propagates the target production tenant id
- `Runtime_Implementation/core/production_state/gate.py` - gate-level defense in depth
- `Runtime_Implementation/core/production/loop.py` - `policy_consumer_config` wiring + per-tenant sandbox forcing
- `Runtime_Implementation/tests/test_multi_tenant_isolation.py` - 11 tests
- `Policy_Pipeline/multi-tenant-isolation-hardening.md` - Definition of Done spec

Properties:
- Guardrail 11 surface list unchanged: still exactly four mutable surfaces on `production_state`.
- HMAC signing primitive in `core/policy/signing.py` is unchanged; the canonical payload grew by exactly one field.
- Latest full runtime test result: **178 passed**.
