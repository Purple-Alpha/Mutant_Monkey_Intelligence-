# One-Hour Agent Training Loop

**Status:** Spec-first control protocol. No runtime autonomy implemented yet.
**Purpose:** Define the first safe one-hour multi-agent work session for NorthStar.
**Mode:** Training / sandbox-first. Production-impacting actions require operator approval.

## 1. Goal

The first autonomy goal is not "agents run forever." The first goal is:

> A bounded one-hour agent session can accept a mission, work through checkpoints, debate findings, produce an auditable result, and stop cleanly without relying on the human to continually re-prompt it.

The system may start from an approved operator mission or from a high-confidence defensive trigger. In both cases, v1 is a **training loop**: agents can analyze, draft, test, audit, and recommend. They may not silently promote policy, apply overrides, mutate production, or mark closeout complete.

## 2. Language Boundary

Use:

- Swarm defensive response.
- Defensive training loop.
- Threat-triggered evaluation.
- Sandbox escalation.
- Operator approval required.

Avoid:

- Swarm attack.
- Autonomous retaliation.
- Real-world targeting.
- Self-directed offensive activity.

NorthStar is a defensive security system. Triggers activate defensive review and evaluation, not offensive action.

## 3. Session Roles

| Role | Purpose | Writes |
|---|---|---|
| Mission Controller | Reads the trigger or operator mission and freezes the scope | Session plan only |
| Builder | Performs the allowed implementation or analysis task | Allowed files only |
| Auditor | Reviews for bugs, governance violations, drift, and missing tests | Audit report |
| Scribe | Updates handshake, activity log, and index if needed | Tracking files only |
| Judge | Decides approved / not approved against the definition of done | Final verdict |

For v1, these roles may still be simulated by one agent or manually split across Codex / Cursor / Manus. The protocol is the important part.

## 4. One-Hour Timeline

| Minute | Checkpoint | Required Output |
|---:|---|---|
| 0 | Mission lock | Target, allowed files, forbidden files, definition of done |
| 10 | Context checkpoint | Files read, assumptions, first risk scan |
| 20 | First work checkpoint | Work completed or candidate plan |
| 30 | Drift checkpoint | Confirm no scope expansion, no forbidden files |
| 40 | Audit checkpoint | Auditor findings, test/audit plan |
| 50 | Finalization checkpoint | Remaining blockers, docs/tracking status |
| 60 | Stop checkpoint | Final report, changed files, verification, next step |

If the session hits a governance blocker, kill switch, forbidden file, missing secret, or unclear production-impacting decision, it stops and writes a blocked verdict.

## 5. Mission Envelope

Every one-hour loop starts with a mission envelope:

```json
{
  "session_id": "one_hour_training_YYYYMMDD_HHMM",
  "mode": "training",
  "trigger_source": "operator|autonomous_trigger",
  "objective": "plain English objective",
  "allowed_paths": [],
  "forbidden_paths": [],
  "definition_of_done": [],
  "max_duration_minutes": 60,
  "requires_operator_approval_for": [
    "production_policy_apply",
    "tenant_override_write",
    "rollback_request",
    "external_network_call",
    "client_facing_send",
    "closeout_status_change"
  ]
}
```

## 6. Allowed Training Actions

In training mode, the loop may:

- Read project docs and runtime files.
- Draft specs and implementation plans.
- Create sandbox-only test cases.
- Run local tests when allowed.
- Produce audit findings.
- Draft tracking entries.
- Recommend operator actions.

## 7. Forbidden Autonomous Actions

The loop may not, without explicit operator approval:

- Apply signed production policies.
- Create, pause, or revoke tenant overrides.
- Trigger rollback.
- Send messages to clients or MSPs.
- Use real customer data.
- Fetch external URLs for threat testing.
- Execute attachments.
- Change LLM provider keys or secrets.
- Mark a project phase "closed" without verification.

## 8. Debate Contract

At minimum, the Builder and Auditor must disagree-check the result:

1. Builder states what was done and why it satisfies the mission.
2. Auditor lists bugs, drift, missing tests, and governance concerns.
3. Builder responds with fixes or explicit deferrals.
4. Judge returns one verdict:
   - `approved`
   - `approved_with_deferred_risks`
   - `not_approved`
   - `blocked`

No one-hour loop is considered complete without the verdict.

## 9. Triggered Training Loop

An autonomous trigger may start this loop only when:

- The trigger maps to a known defensive category.
- The session mode is `training`.
- The allowed paths are pre-defined by the trigger profile.
- Production-impacting actions are blocked by default.
- The output includes a final report and activity-log-ready summary.

## 10. First Training Target

Recommended first one-hour exercise:

**Mission:** Evidence-package visibility design pass.

Allowed paths:

- `4. Product_Roadmap/`
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/`
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production/`
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/`
- project tracking files

Forbidden:

- Live LLM eval calls.
- Tenant override writes outside test fixtures.
- Production policy application outside tests.
- Client-facing sends.

Gate:

- One spec or implementation plan.
- Audit findings.
- Tracking update.
- No runtime code unless explicitly approved for that session.

## 11. Implementation Receipt

Deferred. First implementation should create a local session-runner script or CLI that builds the mission envelope, starts a timer, writes checkpoint artifacts, and refuses production-impacting commands by default.

