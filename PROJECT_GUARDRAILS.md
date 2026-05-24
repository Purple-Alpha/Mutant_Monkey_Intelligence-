# Project Guardrails
NorthStar + SwarmCommand Venture

## Purpose
These guardrails keep the project sane, traceable, and easy to resume.

They apply to humans, AI agents, contractors, and future developers working inside this workspace.

## Guardrail 1 - Always Update the Activity Log
Whenever a file or folder is created, changed, moved, or meaningfully reviewed, update:

`PROJECT_ACTIVITY_LOG.md`

The log entry should include:
- date
- actor
- action
- files changed
- reason
- next recommended step

## Guardrail 2 - Keep the Handshake Current
Update `PROJECT_HANDSHAKE.md` whenever:
- the active build target changes
- a phase is completed
- a new top-level system is added
- the next step changes
- a major decision is made

## Guardrail 3 - Keep the Master Index Navigable
Update `MASTER_INDEX.md` whenever:
- a new major folder is created
- a major document is added
- the project map changes
- a new operating guide becomes important

## Guardrail 4 - Use Local README Files
Every major folder should have a README or overview file explaining:
- purpose
- what belongs there
- what does not belong there
- current priority
- related files

## Guardrail 5 - One Source of Truth Per Topic
Avoid duplicating the same decision in many places.

Use:
- `PROJECT_HANDSHAKE.md` for current state and resume point
- `PROJECT_ACTIVITY_LOG.md` for change history
- `MASTER_INDEX.md` for navigation
- local README files for folder-specific context
- specialized docs for detailed specifications

## Guardrail 6 - Production vs Sandbox Safety
For SwarmCommand runtime work:
- production is Blue-only
- sandbox is the only place mutation is allowed
- Red agents never access production data
- policy updates require audit and signing
- tenant data stays isolated

## Guardrail 7 - Append-Only Thinking
For logs, audit trails, and Blackboard records:
- append new records
- do not silently rewrite history
- corrections should be added as a new note

## Guardrail 8 - No Untracked Expansion
Do not add a new subsystem unless it supports one of:
- one offer
- one buyer
- one outreach motion
- one delivery workflow
- first paying clients
- SwarmCommand runtime foundation

## Guardrail 9 - Every Build Target Needs Definition of Done
Every implementation spec should include:
- what will be created
- what success means
- what tests or checks prove it works
- what the next step is

## Guardrail 10 - End Every Work Session With a Next Step
Before stopping work, make sure the next step is written in:
- `PROJECT_HANDSHAKE.md`
- latest entry of `PROJECT_ACTIVITY_LOG.md`

## Guardrail 11 - Blue Loop Write Surface (Hard Boundary)
The Blue (production) loop's governance-level mutations are limited to:

1. `governance_001.audit_verdict` (append-only Blackboard record).
2. `orchestrator_001.workflow_trigger` (append-only Blackboard record).
3. `production_state.policy.active_version` (mutable production state).
4. `production_state.policy.parameters` (mutable production state, only when explicitly authorized).

Everything else the Blue loop touches in production is read-only or observational-append-only telemetry (`ingest_event`, `detection_result`, `risk_score`, operational `audit_001.audit_verdict`, anonymized `weakness_report` to sandbox).

Enforcement:
- Surfaces 1 and 2 are enforced by `core/orchestrator/registry.py` (agent registry + `validate_record_against_registry`).
- Surfaces 3 and 4 must be enforced by `core/production_state/` (gated dataclass + write function requiring a signed workflow-trigger record as evidence). Direct in-process edits to production state from anywhere else are a governance violation.

Full rule, table, and open questions live in `3. SwarmCommand_Engine/Agent_Loop_Runtime/Governance_Constitution/governance-constitution-loop.md` under "Blue Loop Write Surface (Hard Boundary)".

## Guardrail 12 - Operator Kill Switch (Separate Surface)
The runtime ships an operator-controlled kill switch as a SEPARATE surface from the four mutable production surfaces listed in Guardrail 11. The kill switch must not be added to that list.

Rules:
- The kill switch lives at `core/operator_state/` (state file `blackboard_root/operator_state/operator.json`, append-only audit log `blackboard_root/operator_state/operator.audit.jsonl`).
- `engage_kill_switch` and `disengage_kill_switch` are the ONLY write functions. They are operator-initiated (CLI / REPL / future operator dashboard) and must not be imported by any agent or loop module. Defense by convention is sufficient for the prototype.
- Every loop entry calls `is_kill_switch_engaged(...)` at the top and raises `KillSwitchEngaged` (a `RuntimeError`) when the switch covers its scope. `apply_signed_policy` does the same check as the FIRST line of its body — the kill switch is the outermost gate, before signature verification and rollback history checks.
- Three scopes: `ALL`, `PRODUCTION_ONLY`, `SANDBOX_ONLY`. Production-side loops check `ALL | PRODUCTION_ONLY`; sandbox-side loops check `ALL | SANDBOX_ONLY`.
- The operator audit log is the single source of truth for kill-switch events. Tenant Blackboards stay clean.

Full spec, behavior contract, and resolved decisions live in `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/operator-kill-switch.md`.
