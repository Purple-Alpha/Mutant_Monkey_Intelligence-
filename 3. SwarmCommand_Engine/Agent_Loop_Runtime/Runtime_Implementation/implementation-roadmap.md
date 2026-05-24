# Agent Loop Runtime Implementation Roadmap

## Purpose
This roadmap turns the Agent Loop Runtime concept into buildable implementation stages.

## Phase 1 - Blackboard Engine Models
Build the core data models:
- Record envelope
- Record types
- Append-only storage
- Audit fields
- Tenant and environment isolation

**Status:** Initial Python/Pydantic scaffold complete.

Implemented under:
- `Runtime_Implementation/core/blackboard/models.py`
- `Runtime_Implementation/core/blackboard/storage.py`
- `Runtime_Implementation/tests/test_blackboard_models.py`

Verification:
- `python -m pytest tests`
- Result: 6 passed

## Phase 2 - Orchestrator API Routing Layer
Build routing primitives:
- Ingest route
- Detection route
- Scoring route
- Workflow trigger route
- Audit route
- Sandbox weakness route
- Policy update route

**Status:** Initial internal routing layer complete.

Implemented under:
- `Runtime_Implementation/core/orchestrator/registry.py`
- `Runtime_Implementation/core/orchestrator/routes.py`
- `Runtime_Implementation/tests/test_orchestrator_routes.py`

Verification:
- `python -m pytest tests`
- Result: 14 passed

## Phase 3 - Production Swarm Loop
Implement Blue-only production loop:
- Ingest
- Detection
- Scoring
- Workflow triggers
- Audit
- Weakness report generation

**Status:** Initial Blue-only production loop complete.

Implemented under:
- `Runtime_Implementation/core/production/loop.py`
- `Runtime_Implementation/tests/test_production_loop.py`

Verification:
- `python -m pytest tests`
- Result: 17 passed

## Phase 4 - Sandbox Swarm Loop
Implement Red/Blue training loop:
- Pull weakness reports
- Generate synthetic cases
- Run Blue detection
- Capture failure modes
- Trigger mutation evaluation

**Status:** Initial Red/Blue sandbox loop complete.

Implemented under:
- `Runtime_Implementation/core/sandbox/loop.py`
- `Runtime_Implementation/tests/test_sandbox_loop.py`

Verification:
- `python -m pytest tests`
- Result: 22 passed

## Phase 5 - Mutation Engine
Implement controlled sandbox mutation:
- Clone
- Mutate
- A/B test
- Evaluate
- Retire or promote

**Status:** Initial sandbox-only mutation engine complete.

Implemented under:
- `Runtime_Implementation/core/mutation/engine.py`
- `Runtime_Implementation/tests/test_mutation_engine.py`

Verification:
- `python -m pytest tests`
- Result: 26 passed

## Phase 6 - Policy Update Signing and Promotion Pipeline
Implement production-safe promotion:
- Signed policy update
- Audit approval
- Queue for production review
- Rollout tracking
- Rollback record

**Status:** Signing, promotion, production-state apply, and closed-loop consumption are complete. Rollback is not implemented yet.

Implemented under:
- `Runtime_Implementation/core/policy/signing.py`
- `Runtime_Implementation/core/policy/pipeline.py`
- `Runtime_Implementation/core/production_state/state.py`
- `Runtime_Implementation/core/production_state/gate.py`
- `Runtime_Implementation/core/production/policy_consumer.py`
- `Runtime_Implementation/tests/test_policy_pipeline.py`
- `Runtime_Implementation/tests/test_production_state.py`
- `Runtime_Implementation/tests/test_production_loop_integration.py`

Verification:
- `python -m pytest tests`
- Result: 43 passed

## Phase 7 - Governance Constitution Runtime
Implement always-on guardrails:
- Schema enforcement
- Hop count limits
- Cooldowns
- Quarantine
- Red/production isolation
- Audit logs

**Status:** Partially implemented through registry validation, sandbox-only record enforcement, policy signing, production-state gate, and Guardrail 11. Full runtime monitor/cooldown/quarantine service remains future work.

## Immediate Next Build Choice
Choose one:
- Rollback primitive for signed revert policies through the same Guardrail 11 gate.
- Business_Operations ghost sweep to canonicalize Notion-style `# *.md` files.

Reason:
The closed policy loop is proven. The main engineering gap before scaling beyond one tenant is rollback; the main operational cleanup gap is commercial-side filename debt.
