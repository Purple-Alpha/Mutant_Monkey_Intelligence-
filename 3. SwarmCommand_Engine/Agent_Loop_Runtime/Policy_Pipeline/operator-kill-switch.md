# Operator Kill Switch
Definition of Done — RSI Prereq #7

## Purpose
The runtime has no operator-grade emergency stop. Today, halting any loop requires killing the host process or commenting out the call site. That is unsafe: a misbehaving cycle, a runaway alert subscriber, or a regressing detector cannot be paused without losing in-flight evidence, and no audit record exists of the operator's intervention.

This spec defines the kill switch as a small, append-only, human-controlled surface that every loop entry point reads at the start of each cycle. It is the smallest unit of work that makes every loop already wired today (`run_production_cycle`, `run_sandbox_cycle`, `run_alert_subscriber_cycle`, `run_regression_detector_cycle`, `apply_pending_policies`, `run_email_risk_scoring_cycle`, and any future drafting / digest agents) safe to operate unattended.

It is RSI prerequisite #7 because no recursive self-improvement loop should run without an immediate human halt.

## Scope and non-goals

### In scope
1. **A new `core/operator_state/` module** that owns a frozen `OperatorControlState` dataclass, atomic JSON persistence, and the only two write functions: `engage_kill_switch(...)` and `disengage_kill_switch(...)`.
2. **A read function** `is_kill_switch_engaged(blackboard_root, *, scope) -> bool` that is cheap, side-effect-free, and safe to call from every loop entry.
3. **Halt-on-entry semantics**: every loop entry point checks the switch before doing any work. If engaged for the relevant scope, the entry function raises `KillSwitchEngaged` (a new exception type in `core/operator_state`). No partial cycles. No silent skips.
4. **Three scopes**: `ALL`, `PRODUCTION_ONLY`, `SANDBOX_ONLY`. Loops check the scope that applies to them (production loops check `ALL | PRODUCTION_ONLY`, sandbox loops check `ALL | SANDBOX_ONLY`).
5. **Append-only operator audit log** at `blackboard_root/operator_state/operator.audit.jsonl`. Every engage / disengage writes one JSON line with timestamp, scope, reason, and operator identifier.
6. **Gate enforcement**: `apply_signed_policy` raises `KillSwitchEngaged` if the production-applicable switch is engaged, even if a fully valid signed evidence chain is provided. The kill switch overrides every other governance path.
7. **Required reason**: engaging the switch requires a non-empty reason string. Disengaging requires a non-empty reason string. Both are recorded.
8. **CLI-style entry points only**: `engage_kill_switch` and `disengage_kill_switch` are not imported by any agent or loop module. They live in `core/operator_state/gate.py` and are intended to be invoked from a Python REPL, a CLI script, or a future operator dashboard. Defense by convention is sufficient for the prototype; cryptographic separation is a future hardening (see Known limitation).
9. **Tests proving each integration point**: at least one explicit test per loop entry that the cycle refuses to run when the switch is engaged for its scope.

### Out of scope (deferred)
- **Cryptographic operator authentication**. A future hardening will require operator writes to be signed with a key the agent process cannot read. For now, the only "auth" is that the write functions are not imported by agent code paths. This is documented as a known limitation, not a bug.
- **Per-tenant kill switch**. A future spec may add `tenant_scopes: dict[str, bool]` so one customer's loops can be halted without affecting others. For v1, scope is global within `ALL` / `PRODUCTION_ONLY` / `SANDBOX_ONLY`.
- **Automatic cooldown after disengage**. No warm-up period. If the operator disengages, the next cycle proceeds normally.
- **Remote / API-level kill switch**. The runtime is internal-only today. Wire-level controls come with multi-tenant API hardening.
- **Auto-engage on detector alert**. The regression detector + alert subscriber already perform automated rollback. The kill switch is operator-controlled only. Wiring it to automated triggers would defeat its purpose as a human override.

## Concrete changes

### 1. New module `core/operator_state/`
```text
core/operator_state/
    __init__.py
    state.py         # OperatorControlState (frozen) + load/save + atomic JSON
    gate.py          # engage_kill_switch, disengage_kill_switch, is_kill_switch_engaged
    audit.py         # append-only operator.audit.jsonl writer/reader
```

`OperatorControlState` (frozen dataclass) carries:

```text
kill_switch_scope: Literal["NONE", "ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"]
engaged_at: datetime | None
engaged_by: str | None       # operator identifier, e.g. "matt" or "ops-cli"
reason: str | None
```

Persistence: `blackboard_root/operator_state/operator.json`, atomic-replace pattern matching `core/production_state/state.py::save_state`. Disk load rejects unauthorized fields the same way `load_state` does.

Default on first read (no file exists): `kill_switch_scope="NONE"`, all other fields `None`.

### 2. New exception `KillSwitchEngaged`
Defined in `core/operator_state/__init__.py`. Inherits from `RuntimeError`. Carries the scope, reason, and engaged_at for the caller to log.

### 3. Read helper
```text
def is_kill_switch_engaged(
    blackboard_root: Path,
    *,
    scope: Literal["PRODUCTION", "SANDBOX"],
) -> OperatorControlState | None:
    """Return the active state iff a kill switch covers ``scope``, else None."""
```

This function is cheap (one JSON read), side-effect-free, and safe to call at the top of every loop entry. It returns the full state object so the caller can include `reason` and `engaged_at` in the `KillSwitchEngaged` exception.

### 4. Loop entry checks
Every loop entry function adds one line at the top:

```text
state = is_kill_switch_engaged(context.blackboard_root, scope="PRODUCTION")
if state is not None:
    raise KillSwitchEngaged(state)
```

Affected entry points:

| File | Function | Scope |
|---|---|---|
| `core/production/loop.py` | `run_production_cycle` | PRODUCTION |
| `core/sandbox/loop.py` | `run_sandbox_cycle` | SANDBOX |
| `core/production/alert_subscriber.py` | `run_alert_subscriber_cycle` | PRODUCTION |
| `core/production/regression_detector.py` | `run_regression_detector_cycle` | PRODUCTION |
| `core/production/policy_consumer.py` | `apply_pending_policies` | PRODUCTION |
| `core/scoring/email_risk_scoring_agent.py` | `run_email_risk_scoring_cycle` | PRODUCTION |
| `core/drafting/daily_digest_agent.py` | `run_daily_digest_cycle` | PRODUCTION |
| `core/policy/rollback.py` | `request_rollback_to_previous` | PRODUCTION |
| `core/production_state/gate.py` | `apply_signed_policy` | PRODUCTION |

The gate check at `apply_signed_policy` is the last line of defense: even if a loop entry was bypassed, no state mutation can happen while the production-applicable kill switch is engaged.

### 5. Engage / disengage entry points
```text
def engage_kill_switch(
    blackboard_root: Path,
    *,
    scope: Literal["ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"],
    reason: str,
    operator: str,
) -> OperatorControlState: ...

def disengage_kill_switch(
    blackboard_root: Path,
    *,
    reason: str,
    operator: str,
) -> OperatorControlState: ...
```

Both functions:
- Refuse empty `reason` and empty `operator` with `ValueError`.
- Atomically write the new `OperatorControlState` to `operator.json`.
- Append one record to `operator.audit.jsonl`:
  ```json
  {"action": "engage" | "disengage", "scope": "...", "operator": "...",
   "reason": "...", "at": "2026-05-20T19:43:11Z",
   "previous_scope": "..."}
  ```
- Are **not** imported by any module under `core/production`, `core/sandbox`, `core/scoring`, `core/drafting`, or `core/orchestrator`. They are intended for CLI / REPL / operator-tooling use only.

### 6. CLI wrapper — deferred
A `scripts/kill_switch.py` argparse wrapper would be a thin layer over `engage_kill_switch` / `disengage_kill_switch` / `load_operator_state`. Deferred for v1 per resolved decision below. The gate functions are sufficient for REPL / scripted use. CLI added later when an operator workflow needs it.

## Hard guardrails preserved
- **Guardrail 11 surface list is unchanged.** The four mutable production surfaces stay exactly as defined. `operator_state` is a *separate* surface from `production_state`. It is owned by the operator, not by any agent, and no agent code path writes to it.
- **Append-only operator audit log.** Guardrail 7 (Append-Only Thinking) applies to the operator audit log as well as the Blackboard.
- **No new producer agent.** The operator is not an agent. Engage / disengage are CLI / REPL operations, not Blackboard records.
- **Red agents are still sandbox-only.** Nothing about the kill switch changes the Red/Blue boundary.

## Behavior contract

| Scenario | Outcome |
|---|---|
| Default state, no kill switch file on disk | All loops run normally. `is_kill_switch_engaged` returns `None` for every scope. |
| Engage scope=ALL | Both production and sandbox cycles immediately raise `KillSwitchEngaged` on next entry. Gate refuses signed-policy applies. |
| Engage scope=PRODUCTION_ONLY | Production cycle, alert subscriber, regression detector, policy consumer, scoring agent, digest agent, rollback request, and gate all halt. Sandbox cycle continues. |
| Engage scope=SANDBOX_ONLY | Sandbox cycle halts. Production cycle continues. |
| Engage with empty reason | `ValueError`. State unchanged. No audit record. |
| Engage without operator | `ValueError`. State unchanged. No audit record. |
| Disengage when already disengaged | State unchanged. One disengage audit record written anyway (operator intent recorded). |
| Disengage during in-flight cycle | The in-flight cycle (already past its entry check) runs to completion. The next cycle proceeds normally. |
| Process restart while engaged | Next loop start reads `operator.json`, finds `kill_switch_scope != "NONE"`, raises `KillSwitchEngaged`. Restart does not silently clear the switch. |
| Operator audit log read | Returns full chronological list of engage / disengage records, including stale entries from prior days. |
| Gate invoked with valid signed evidence while kill switch engaged | `KillSwitchEngaged` raised before any signature verification or state mutation. |

## Verification

From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Target after this work: existing test count + at least 10 new tests. (Existing count is currently 75 before Inbox Shield trio lands; after Inbox Shield + kill switch, target is ~95-100+ depending on Inbox Shield's final test delta.)

New coverage required:
1. Default `OperatorControlState` is "NONE" when no file exists.
2. `engage_kill_switch` with empty reason / operator raises `ValueError`.
3. `engage_kill_switch` writes both `operator.json` and one `operator.audit.jsonl` line.
4. `disengage_kill_switch` writes both files and records `previous_scope`.
5. Disk load rejects unauthorized fields on `operator.json` (matches `production_state/state.py` pattern).
6. `is_kill_switch_engaged(scope="PRODUCTION")` returns the state when scope is `ALL` or `PRODUCTION_ONLY`, `None` otherwise.
7. `run_production_cycle` raises `KillSwitchEngaged` when engaged with `ALL` or `PRODUCTION_ONLY`.
8. `run_sandbox_cycle` raises `KillSwitchEngaged` when engaged with `ALL` or `SANDBOX_ONLY`.
9. `run_sandbox_cycle` runs normally when engaged with `PRODUCTION_ONLY` (and vice versa).
10. `apply_signed_policy` raises `KillSwitchEngaged` even when given a fully valid signed evidence chain; state file is not mutated.
11. End-to-end: engage → confirm both cycles refuse → disengage → confirm both cycles run again.
12. Audit log is chronological, append-only, and survives multiple flips.

## Phase plan (this mission, in order)

1. **Spec (this file).** Approved before any code changes.
2. Build `core/operator_state/state.py` with `OperatorControlState`, `load_operator_state`, `save_operator_state`. Tests for items 1, 5.
3. Build `core/operator_state/audit.py` with the append-only `operator.audit.jsonl` writer/reader. Tests for items 3, 4, 12.
4. Build `core/operator_state/gate.py` with `engage_kill_switch`, `disengage_kill_switch`, `is_kill_switch_engaged`. Tests for items 2, 6.
5. Wire the entry-point check into every loop in the table above (one one-liner per file). Tests for items 7, 8, 9.
6. Wire the gate check into `apply_signed_policy`. Test for item 10.
7. End-to-end test (item 11).
8. Update activity log + handshake + runtime README + master index. Update `PROJECT_GUARDRAILS.md` to document the operator-state surface and its separation from Guardrail 11.

Each step is one focused commit. The mission is finished when all new tests pass, the existing test count is unchanged, and engaging the switch demonstrably halts every wired loop.

## Known limitation (prototype scope)
**No cryptographic operator authentication.** The current design relies on defense by convention: `engage_kill_switch` / `disengage_kill_switch` are not imported by any agent or loop module, and operators invoke them from CLI / REPL / future operator dashboards. A malicious agent that gained arbitrary code execution could call these functions. Hardening this is a future mission and will require:
- A separate operator signing key loaded from a path the agent process cannot read.
- Signed engage / disengage records that are re-verified on every read.
- Process-level isolation between the agent runtime and the operator CLI.

This limitation is acceptable for the internal prototype because (a) all code paths are reviewed Python with no third-party plugin loading, and (b) the kill switch is additive safety — even an unauthenticated kill switch is strictly better than today's "no kill switch at all."

## Resolved decisions (2026-05-20)

The four open questions were resolved at spec-review time:

1. **No per-tenant Blackboard audit record on kill-switch flip.** The operator audit log (`blackboard_root/operator_state/operator.audit.jsonl`) is the single source of truth for kill-switch events. Tenant Blackboards stay clean — operator actions do not pollute per-tenant audit trails. If a future customer-facing audit report needs to surface "loop halted at T+N", it should read from the operator audit log and join, not have the data duplicated into tenant logs.
2. **Kill-switch check is the outermost gate in `apply_signed_policy`.** It runs *before* signature verification and *before* the rollback-history check. No wasted work, no "halted but evidence verified" intermediate state.
3. **No CLI wrapper for v1.** Ship `engage_kill_switch` / `disengage_kill_switch` / `is_kill_switch_engaged` / `load_operator_state` as importable Python functions. REPL / scripted use is sufficient until an operator workflow demands a CLI.
4. **Minimal state schema for v1.** `OperatorControlState` carries only `kill_switch_scope`, `engaged_at`, `engaged_by`, and `reason`. No `expected_duration`, no `severity`, no dashboard-display fields. The disk-load unauthorized-fields check stays strict; if a later mission needs new fields, the schema gets a versioned bump rather than a quiet relaxation.

## Status
**Spec approved 2026-05-20.** Ready for Phase 2 (code) after the Inbox Shield trio fully lands in tree, to avoid a merge collision in `core/production/loop.py` and the new `core/scoring/` + `core/drafting/` entry points.
