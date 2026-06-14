# Mutant Monkey Inbox Shield — Safe-Stop State Machine Design Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Safe_Stop_State_Machine_Concept_Doc.md + ChatGPT requirements research June 14 2026 + Operator Decision Record June 14 2026
**Depends on:** Mode Controller (SIGNED), Privacy Filter (SIGNED), Blast Radius Controller (GATED), Watcher Agents (GATED), Fission v2 (SIGNED), Mutation Engine (GATED), ReconciliationAgent (GATED)

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Purpose

This contract defines the Safe-Stop State Machine — the named, controlled state the Mutant Monkey Inbox Shield organism enters when core safety guarantees can no longer be trusted.

Safe-stop is not a crash. It is not an error condition. It is not a fallback mode.

Safe-stop is the organism's proof that it prefers bounded, logged, operator-governed shutdown over silent corruption, split-brain operation, or uncontrolled behavior.

This contract governs:
- The five conditions that trigger safe-stop
- The entry protocol
- The behavior permitted and forbidden inside safe-stop
- The exit protocol
- The relationship to every signed and gated component
- The testable invariants that prove this contract is respected at runtime

---

## Operator Decision Record

These three decisions were made by Matt Nichol on June 14 2026 using rubric scoring against eight criteria: safety leverage, split-brain protection, anti-flapping balance, testability, scope containment, operator control, reversibility, and signed-spec alignment.

These are provisional contract-drafting values. They are changeable only by signed amendment. They do not represent proven-optimal production values.

| Decision | Value | Rubric score | Reason |
|---|---|---|---|
| OQ-1 — Mode Controller quorum-loss timeout | **120 seconds** | 38/40 | Best balance: prevents split-brain without triggering safe-stop on transient jitter |
| OQ-2 — Two simultaneous CRITICAL watcher recovery window | **300 seconds** | 38/40 | Enough time for reconciliation/containment; not indefinite tolerance of systemic instability |
| OQ-3 — Safe-stop exit authority | **Matt Nichol only** | 40/40 | Preserves existing authority model; no unsigned CIRT governance layer introduced |

---

## State Definition

### What safe-stop is

Safe-stop is a named mode state of the Mutant Monkey Inbox Shield organism. It is distinct from ISOLATED and DEGRADED.

| State | Meaning | Epoch incremented? | New processing? | Operator exit required? |
|---|---|---|---|---|
| DEGRADED | Organism operating with reduced capacity | No | Yes, with constraints | No |
| ISOLATED | Local tenant fallback on heartbeat loss | No | Yes, locally contained | No |
| **SAFE-STOP** | **Organism halted pending operator action** | **No** | **No** | **Yes** |

Safe-stop is entered from any state. It does not require the organism to be in DEGRADED or ISOLATED first.

### What safe-stop is not

- Safe-stop is not automatic recovery. The organism does not self-exit safe-stop.
- Safe-stop is not diagnosis. The organism does not determine why the condition occurred.
- Safe-stop is not permanent shutdown. The organism is recoverable with operator action and proof of state safety.
- Safe-stop is not a verdict. Safe-stop produces no enforcement decisions on any tenant's email.

---

## Five Named Entry Conditions

Any one of the following conditions triggers safe-stop. They are not ranked. The first condition detected fires the entry protocol.

### SS-1 — Mode Controller quorum loss

**Trigger:** Mode Controller quorum is unavailable for more than **120 seconds**.

**Timer start:** The moment quorum drops below the minimum required threshold.

**During the 120-second window:** Heartbeat fallback applies per MC-D6 — local ISOLATED without epoch increment. The organism continues processing under local fallback rules. Epoch is not incremented.

**On timeout:** Safe-stop fires. Epoch is not incremented on safe-stop entry.

**Rationale:** 120 seconds is long enough to absorb transient quorum loss without false safe-stops. It is short enough to prevent prolonged split-brain operation during genuine quorum failure.

---

### SS-2 — Privacy Filter breaker unrecoverable

**Trigger:** The Privacy Filter independent breaker enters an open state and cannot recover within its own defined recovery window.

**Condition:** The breaker state itself is the trigger — not a Privacy Filter signal or log entry. If the Privacy Filter cannot prove it can validate cross-tenant broadcasts, safe-stop fires.

**Rationale:** Per Doctrine Invariant 4 — if the Privacy Filter cannot validate a cross-tenant broadcast, the broadcast must not occur. An unrecoverable breaker means the privacy boundary cannot be enforced. The organism cannot continue operating without it.

---

### SS-3 — Two simultaneous CRITICAL watcher events unresolved

**Trigger:** Two independent Watcher Agent CRITICAL classifications exist simultaneously and cannot be reconciled, downgraded, isolated, or operator-acknowledged within **300 seconds**.

**Timer start:** When the second CRITICAL watcher event is logged.

**Resolution paths that stop the timer (any one is sufficient):**
- ReconciliationAgent closes both events
- One or both events are downgraded below CRITICAL by Watcher Agent re-classification
- One or both events are contained to an ISOLATED tenant context
- Matt Nichol explicitly operator-acknowledges the unresolved state in writing

**On timeout:** Safe-stop fires.

**Rationale:** One CRITICAL event can be local and containable. Two simultaneous CRITICAL events suggest possible systemic instability. 300 seconds gives the reconciliation and containment layer enough time to act without allowing unresolved systemic risk to continue indefinitely.

---

### SS-4 — Signed boundary violation with unproven containment

**Trigger:** A fission, mutation, or dispatch path produces an action that violates its signed contract boundary AND containment of that violation cannot be proven within the current control plane cycle.

**Condition:** Both elements must be present — the boundary violation AND the inability to prove containment. A boundary violation with proven containment does not trigger safe-stop; it triggers the component's own violation logging and alert path.

**Rationale:** The organism depends on signed contract boundaries for authority and containment. A violation that cannot be contained means a component is operating outside its signed scope with no recovery proof. The organism cannot trust its own behavior in that state.

---

### SS-5 — ReconciliationAgent unresolvable named conflict

**Trigger:** ReconciliationAgent surfaces a named evidence conflict that cannot be resolved by the R3 Conflict Resolution Voter and no resolution path remains available.

**Condition:** ReconciliationAgent does not self-authorize safe-stop. It surfaces the unresolvable condition. The safe-stop entry is triggered by the conflict state, not by ReconciliationAgent as an authority.

**Rationale:** Per Doctrine Invariant 14 — conflicts must be named and resolved, not hidden. An unresolvable conflict means the organism cannot produce a trusted verdict for the affected event. Operating without resolution risks silent false negatives or false positives propagating to tenant baselines.

---

## Entry Protocol

When any entry condition fires, the following steps occur in order before any other action:

1. **Log entry record** — written immediately with:
   - Condition name (SS-1 through SS-5)
   - Timestamp of detection
   - Epoch at moment of entry (not incremented)
   - Component that detected the condition
   - All active tenant IDs at moment of entry
   - Summary of the triggering state

2. **Halt new email ingestion** — no new email enters processing pipelines

3. **Halt new fission** — no new fission requests are dispatched

4. **Halt new mutation** — no mutation sandbox, confirmation, or deployment proceeds

5. **Halt new cross-tenant broadcasts** — Privacy Filter receives halt signal

6. **In-flight reconciliation** — any ReconciliationAgent ensemble already in active deliberation at the moment of entry may complete, subject to a maximum 60-second grace window. After 60 seconds, in-flight reconciliation is aborted and logged.

7. **In-flight fission children** — existing children complete their current atomic action or are aborted. No new child spawning permitted.

8. **Operator notification** — safe-stop state and entry log are made available to Matt Nichol via telemetry output

**The entry log is the proof of entry. If no entry log exists, safe-stop did not fire correctly.**

---

## Behavior Inside Safe-Stop

### Permitted

| Action | Condition |
|---|---|
| Read-only access to evidence ledger | Audit access only — no writes |
| Operator telemetry and status reporting | Matt-facing output only |
| Logging of events that occur during safe-stop | Append-only to audit log |
| Graceful completion of in-flight reconciliation | 60-second grace window only |
| Graceful completion of in-flight child actions | Current atomic action only, no new spawning |

### Forbidden

| Action | Reason |
|---|---|
| New email ingestion or processing | No new tenant data enters organism |
| New fission of any kind | No new children, no load fission, no specialisation fission |
| New mutation of any kind | No sandbox, no confirmation, no deployment |
| New cross-tenant broadcasts | Privacy boundary enforcement cannot be extended during safe-stop |
| Baseline updates from any source | No evidence-to-baseline promotion during safe-stop |
| Mode transition by any component other than the exit protocol | Mode Controller is the only authority to exit safe-stop on operator instruction |
| Epoch increment | Epoch is frozen at entry value until operator exit and recovery broadcast |
| Automatic recovery | No component may self-authorize exit from safe-stop |

---

## Exit Protocol

Safe-stop exit requires all of the following in order:

### Step 1 — Operator action

Matt Nichol must explicitly authorize exit from safe-stop. Authorization must be:
- In writing (log entry, commit message, or signed statement)
- Named to the specific safe-stop instance (entry log timestamp)
- Accompanied by a statement that the entry condition has been resolved or accepted

No automated signal, no component health report, and no elapsed time alone constitutes operator authorization.

### Step 2 — Proof of state safety

Before Mode Controller may broadcast recovery, the following must be demonstrated:

| Condition | Proof required |
|---|---|
| SS-1 was the trigger | Mode Controller quorum is restored and stable |
| SS-2 was the trigger | Privacy Filter breaker is closed and validated |
| SS-3 was the trigger | Both CRITICAL watcher events are resolved, downgraded, or operator-acknowledged |
| SS-4 was the trigger | Boundary violation is contained and logged; component contract is confirmed valid |
| SS-5 was the trigger | Named conflict is resolved or operator has accepted the unresolvable state with explicit acknowledgment |

Proof is logged before recovery broadcast.

### Step 3 — Recovery broadcast

Mode Controller broadcasts recovery state. Epoch is incremented only at this point, following the standard Mode Controller recovery broadcast path per MC-D6 and Doctrine Invariant 1.

### Step 4 — Resume

Normal processing resumes under existing signed contract constraints. No safe-stop exit creates new build authority, new agent permissions, or new baseline values.

---

## Relationship to Signed and Gated Components

| Component | Role in safe-stop |
|---|---|
| Mode Controller | SS-1 trigger source. Sole authority to broadcast recovery on exit. Epoch frozen during safe-stop. |
| Privacy Filter | SS-2 trigger source. Receives halt signal on entry. Breaker state proof required on SS-2 exit. |
| Blast Radius Controller | Gateway lifecycle gates remain active during safe-stop. No new dispatches. In-flight actions complete under ring/budget/breaker constraints or abort. |
| Watcher Agents | SS-3 trigger source. Continue observation during safe-stop. Cannot trigger new fission during safe-stop. |
| ReconciliationAgent | SS-5 trigger source. In-flight reconciliation may complete in 60-second grace window. No new reconciliation begins during safe-stop. |
| Fission v2 (Load and Specialisation) | All fission halted on entry. Existing children complete current atomic action or abort. No new children spawned. |
| Mutation Engine | All mutation halted on entry. No sandbox, no 3-shot, no deployment. |
| Evidence Ledger | Read-only during safe-stop. No baseline updates. |

---

## Testable Invariants

All invariants are falsifiable. Each names the triggering test.

| # | Invariant | Falsifiable test |
|---|---|---|
| SS-INV-1 | Safe-stop entry is logged immediately with condition name, timestamp, epoch at entry, detecting component, and all active tenant IDs — before any other action. | Trigger any entry condition — verify log record exists before any halt action completes |
| SS-INV-2 | No new email is ingested or processed after safe-stop entry. | Inject email after safe-stop fires — verify it is not processed and injection is logged |
| SS-INV-3 | No fission of any kind is permitted after safe-stop entry. | Attempt fission dispatch after safe-stop fires — verify blocked and logged |
| SS-INV-4 | No mutation of any kind is permitted after safe-stop entry. | Attempt mutation after safe-stop fires — verify blocked and logged |
| SS-INV-5 | No cross-tenant broadcast occurs after safe-stop entry. | Attempt broadcast after safe-stop fires — verify blocked |
| SS-INV-6 | Epoch is not incremented on safe-stop entry. | Trigger safe-stop — verify epoch value unchanged at entry and during safe-stop |
| SS-INV-7 | Safe-stop cannot be exited without explicit operator action from Matt Nichol. | Simulate full condition recovery without operator action — verify organism remains in safe-stop |
| SS-INV-8 | Exit from safe-stop requires proof of state safety before Mode Controller broadcasts recovery. | Attempt recovery broadcast without safety proof logged — verify broadcast blocked |
| SS-INV-9 | SS-1 timer starts when Mode Controller quorum drops below threshold and fires safe-stop at exactly 120 seconds. | Simulate quorum loss — verify safe-stop fires at 120 seconds, not before, not after |
| SS-INV-10 | SS-3 timer starts when the second CRITICAL watcher event is logged and fires safe-stop at exactly 300 seconds with no resolution. | Simulate two simultaneous CRITICAL events with no resolution — verify safe-stop fires at 300 seconds |
| SS-INV-11 | No baseline update occurs during safe-stop. | Simulate closed threat event during safe-stop — verify no baseline write occurs |
| SS-INV-12 | In-flight reconciliation grace window does not exceed 60 seconds after safe-stop entry. | Trigger safe-stop during active reconciliation — verify ensemble aborted at 60 seconds |

---

## Out of Scope

The following are explicitly excluded from this contract. If any appear in a build, the build exceeds contract scope.

- Automatic safe-stop recovery of any kind
- Diagnosis or root cause analysis inside safe-stop
- New agent types to manage or monitor safe-stop
- Homeostasis Engine definition or logic
- CIS build authorization
- Changes to any existing signed contract
- Network-level isolation or firewall rules
- Safe-stop as a verdicting mechanism
- CIRT role definition or rotating authority model
- Any new organ, component, or authority not named in this contract

---

## Non-Authorizations

- Signing this contract authorizes Cursor to build the Safe-Stop State Machine only.
- This contract does not amend Mode Controller, Privacy Filter, Blast Radius Controller, Watcher Agents, Fission v2, Mutation Engine, or ReconciliationAgent.
- This contract does not open the DEPTH GATE.
- This contract does not authorize CIS work.
- This contract does not define the Cortex/Immune Interface contract.
- This contract does not define the Homeostasis Engine contract.
