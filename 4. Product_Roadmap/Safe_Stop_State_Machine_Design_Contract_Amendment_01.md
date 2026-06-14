# Safe-Stop State Machine — Signed Amendment 01

**Amends:** Safe_Stop_State_Machine_Design_Contract.md (§11 signed June 14th 2026)
**Status:** SIGNED — §11 authorized
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Purpose:** Lock OQ-A, OQ-B, OQ-C before #94 is treated as complete and gated.

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## What This Amendment Changes

This amendment tightens three entry conditions in the original contract. It does not change the five-condition structure, the operator decision values (120s, 300s, Matt only), the entry protocol, the exit protocol, the testable invariants, or any other section.

---

## Amendment A — SS-4 Redefined as Bounded Control-Plane Boundary Violation

**Replaces:** SS-4 — Signed boundary violation with unproven containment

**New SS-4 wording:**

### SS-4 — Signed Control-Plane Boundary Violation

SAFE-STOP review is triggered when a signed control-plane boundary is violated or cannot be verified, including:

**SS-4A — Blast Radius lifecycle violation**
A required lifecycle step cannot be verified:
identity → ring → budget → breaker → mode → dispatch → telemetry.

**SS-4B — Fission boundary violation**
A fission path violates watcher-trigger source, max-depth 1, fresh child identity, permission intersection, or sign-off requirement for specialisation fission.

**SS-4C — Mutation boundary violation**
A mutation path attempts non-sandbox execution, lacks 3-shot confirmation, lacks operator sign-off, or cannot prove reversibility.

**SS-4D — Dispatch containment violation**
A dispatch path exceeds tenant, ring, budget, breaker, or mode authority.

**In all SS-4 cases:** Both elements must be present — the boundary violation AND the inability to prove containment. A boundary violation with proven containment does not trigger SAFE-STOP; it triggers the component's own violation logging and alert path.

---

## Amendment B — SS-3 Locked to Correlated Dual-CRITICAL Watcher Events

**Replaces:** SS-3 — Two simultaneous CRITICAL watcher events unresolved

**New SS-3 wording:**

### SS-3 — Correlated Dual-CRITICAL Watcher Condition

SAFE-STOP is triggered when two or more CRITICAL watcher events remain unresolved for **300 seconds** and are correlated by at least one of the following:

1. Same tenant
2. Same subsystem
3. Same ring
4. Same control-plane path
5. Same failure signature

**Timer start:** When the second correlated CRITICAL watcher event is logged.

**Resolution paths that stop the timer (any one is sufficient):**
- ReconciliationAgent closes both events
- One or both events are downgraded below CRITICAL
- One or both events are contained to an ISOLATED tenant context
- Matt Nichol explicitly operator-acknowledges the unresolved state in writing

Uncorrelated global CRITICAL events do not automatically trigger SAFE-STOP. They must be logged for operator review.

---

## Amendment C — SS-2 Threshold Confirmed

**Replaces:** SS-2 — Privacy Filter breaker unrecoverable

**New SS-2 wording:**

### SS-2 — Unrecoverable Privacy Boundary Failure

SAFE-STOP is triggered only when all three of the following are true simultaneously:

1. The Privacy Filter breaker enters unrecoverable failure or exceeds its defined recovery window
2. Cross-tenant safety cannot be proven
3. The affected communication path cannot be safely isolated without broader organism risk

Recoverable Privacy Filter breaker trips must fail closed and block the affected communication path. They do not automatically trigger SAFE-STOP.

---

## Updated Testable Invariants

These replace the SS-2, SS-3, and SS-4 rows in the original invariant table. All others are unchanged.

| # | Invariant | Falsifiable test |
|---|---|---|
| SS-INV-3A | No fission of any kind is permitted after SAFE-STOP entry. | Attempt fission dispatch after SAFE-STOP fires — verify blocked and logged |
| SS-INV-3B | SS-4B fires when a fission path violates max-depth 1 and containment cannot be proven. | Attempt depth-2 fission — verify SS-4B review evidence created |
| SS-INV-3C | SS-4C fires when a mutation path is non-sandbox, irreversible, or unsigned and containment cannot be proven. | Attempt non-sandbox mutation — verify SS-4C review evidence created |
| SS-INV-3D | SS-4A fires when a Blast Radius lifecycle step cannot be verified. | Skip a required lifecycle step — verify SS-4A review evidence created |
| SS-INV-10 | SS-3 timer starts when the second **correlated** CRITICAL watcher event is logged and fires SAFE-STOP at exactly 300 seconds with no resolution. | Simulate two correlated CRITICAL events with no resolution — verify SAFE-STOP fires at 300 seconds |
| SS-INV-10B | Two uncorrelated global CRITICAL watcher events do not trigger SAFE-STOP. | Simulate two unrelated CRITICAL events — verify SAFE-STOP does not fire, events logged for review |
| SS-INV-SS2 | SS-2 does not fire on a recoverable Privacy Filter breaker trip. | Simulate recoverable breaker trip — verify communication blocked locally, SAFE-STOP does not fire |
| SS-INV-SS2B | SS-2 fires only when breaker is unrecoverable AND cross-tenant safety is unprovable AND path cannot be safely isolated. | Simulate all three conditions simultaneously — verify SAFE-STOP fires |

---

## Non-Authorizations

- This amendment does not authorize any new build activity beyond what the original contract authorized.
- This amendment does not change the five-condition structure of SAFE-STOP.
- This amendment does not change operator decision values OQ-1 (120s), OQ-2 (300s), or OQ-3 (Matt only).
- This amendment does not open the DEPTH GATE.
- This amendment does not authorize CIS work.
- Signing this amendment authorizes Cursor to update #94 to match the tightened SS-2, SS-3, and SS-4 definitions only.
- #94 is now authorized to be treated as complete and gated pending Cursor implementation of these tightened definitions.
