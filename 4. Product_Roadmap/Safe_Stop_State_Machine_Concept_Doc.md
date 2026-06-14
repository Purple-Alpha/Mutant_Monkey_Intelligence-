# Mutant Monkey Inbox Shield — Safe-Stop State Machine Concept Doc

**Status:** CONCEPT — advisory lane only. No build authorization. Requires §11 signature before design contract drafted.
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** ChatGPT requirements research June 14 2026 + Organism Design Doctrine v1 + Gap List gap #2.
**Next step:** Matt reviews, answers open questions, authorizes design contract drafting.

---

## Why This Contract Exists

The Organism Design Doctrine names controlled safe-stop as the organism's response to conditions where core safety guarantees can no longer be trusted. Invariant 20 requires safe-stop to fire under three explicit conditions. The doctrine lists five total entry conditions across sections.

None of those conditions are governed by a signed contract today.

Safe-stop is referenced across Mode Controller, Privacy Filter, Watcher Agents, and the Doctrine itself — but no single document defines: what safe-stop actually is as a state, how it is entered, what is permitted while inside it, how it is exited, and what proof is required before exit.

That gap means the organism can be said to "enter safe-stop" without any enforceable definition of what that means.

This concept doc closes that gap by defining the minimum viable Safe-Stop State Machine contract scope, the invariants it must produce, and the operator decisions required before a contract can be drafted.

---

## What Safe-Stop Is

Safe-stop is a named, controlled state. It is not an error condition. It is not a crash. It is not a fallback.

Safe-stop is the organism's proof that it prefers bounded, logged, operator-governed shutdown over silent corruption or uncontrolled behavior.

When the organism is in safe-stop:
- No new email processing begins
- No fission is permitted
- No mutation is permitted
- No cross-tenant broadcasts occur
- All existing in-flight actions complete under existing ring and privacy constraints or are aborted
- The state is logged immediately with full context on entry
- Operator action is required to exit

Safe-stop is recoverable. It is not permanent shutdown. But recovery requires proof, not just a signal.

---

## Five Named Entry Conditions

These are taken directly from Doctrine Section "Failure and Safe-Stop Model." All five must be contractually defined. A contract that defines only three is incomplete.

| # | Entry Condition | Source |
|---|---|---|
| SS-1 | Mode Controller quorum loss exceeds defined timeout | Doctrine Invariant 20, Open Question OQ-1 |
| SS-2 | Privacy Filter breaker cannot recover | Doctrine Invariant 20 |
| SS-3 | Two simultaneous CRITICAL watcher events remain unresolved within defined window | Doctrine Invariant 20, Open Question OQ-2 |
| SS-4 | A fission, mutation, or dispatch path violates its signed boundary and containment cannot be proven | Doctrine failure model |
| SS-5 | Named evidence conflicts cannot be resolved by ReconciliationAgent | Doctrine failure model |

**Note:** SS-1 requires a timeout value. SS-3 requires a recovery window value. Both are currently open questions for Matt. The contract cannot be finalized until both values are set.

---

## Relationship to Existing Signed Components

Safe-stop does not replace or override any signed contract. It governs the state that results when signed contracts cannot fulfill their guarantees.

| Component | Relationship to Safe-Stop |
|---|---|
| Mode Controller | SS-1 trigger source. Mode Controller must broadcast safe-stop state. Epoch is NOT incremented on safe-stop entry. |
| Privacy Filter | SS-2 trigger source. Privacy Filter breaker state is the condition — not a Privacy Filter signal. |
| Watcher Agents | SS-3 trigger source. Two independent CRITICAL classifications within the unresolved window trigger safe-stop. |
| Blast Radius Controller | Gateway lifecycle continues in safe-stop — no new dispatches permitted, in-flight actions complete or abort under ring constraints. |
| ReconciliationAgent | SS-5 trigger source. Unresolvable named conflict triggers safe-stop. ReconciliationAgent does not self-authorize safe-stop — it surfaces the unresolvable condition. |
| Fission v2 | All fission activity halts on safe-stop entry. No children may be spawned. Existing children complete their current action or abort. |
| Mutation Engine | All mutation activity halts on safe-stop entry. No sandbox, no confirmation, no deployment. |

**Critical rule:** Safe-stop entry does not increment epoch. Safe-stop is a mode state within the existing epoch. Epoch increment belongs only to Mode Controller on recovery broadcast, as per Doctrine Invariant 2 and Invariant 1.

---

## What Happens Inside Safe-Stop

The Safe-Stop State Machine defines behavior inside the state, not just entry conditions.

### Permitted inside safe-stop
- Read-only audit access to existing evidence ledger
- Operator telemetry and status reporting
- Logging of any new events that occur while in safe-stop state
- Graceful completion of in-flight reconciliation already in progress at entry moment (with strict time bound)

### Forbidden inside safe-stop
- New email ingestion or processing
- New fission requests of any kind
- New mutation requests of any kind
- New cross-tenant broadcasts
- Any new evidence produced after safe-stop entry being promoted to tenant baseline
- Mode transition initiated by any component other than the exit protocol

### What is not safe-stop's job
- Safe-stop does not diagnose why the condition occurred
- Safe-stop does not attempt automatic recovery
- Safe-stop does not notify external systems (telemetry only — no outbound enforcement actions)
- Safe-stop does not modify any signed contract, agent configuration, or confidence baseline

---

## Minimum Viable Contract Scope

The smallest useful contract that closes this gap contains exactly these sections:

1. **State definition** — what safe-stop is, what it is not, and how it differs from ISOLATED and DEGRADED
2. **Five named entry conditions** — with exact trigger logic for each (requires open questions answered for SS-1 and SS-3)
3. **Entry protocol** — who fires safe-stop, how it is logged, what the log must contain
4. **Behavior inside safe-stop** — permitted and forbidden actions, enumerated
5. **Exit protocol** — operator action required, proof of state safety required, recovery broadcast path
6. **Relationship map** — how safe-stop interacts with Mode Controller, Privacy Filter, Watchers, BRC, Reconciliation, Fission, Mutation
7. **Testable invariants** — minimum six falsifiable rules

The contract must NOT include:
- Homeostasis Engine logic
- Automatic recovery logic of any kind
- Changes to any existing signed contract
- CIS build authority
- New verdict authority
- Any new organ or component not already named in this concept doc

---

## Testable Invariants (Draft)

These are candidates for the signed contract. All are falsifiable.

| # | Invariant | Falsifiable test |
|---|---|---|
| SS-INV-1 | Safe-stop entry is logged immediately with: condition name, timestamp, epoch at entry, component that detected the condition, and all active tenant IDs. | Trigger any entry condition — verify log record created before any other action |
| SS-INV-2 | No new email is ingested or processed after safe-stop entry. | Inject email after safe-stop fires — verify it is not processed |
| SS-INV-3 | No fission of any kind is permitted after safe-stop entry. | Attempt fission dispatch after safe-stop fires — verify blocked and logged |
| SS-INV-4 | No mutation of any kind is permitted after safe-stop entry. | Attempt mutation after safe-stop fires — verify blocked and logged |
| SS-INV-5 | No cross-tenant broadcast occurs after safe-stop entry. | Attempt broadcast after safe-stop fires — verify blocked |
| SS-INV-6 | Epoch is not incremented on safe-stop entry. | Trigger safe-stop — verify epoch unchanged |
| SS-INV-7 | Safe-stop cannot be exited without explicit operator action. | Simulate condition recovery without operator action — verify organism remains in safe-stop |
| SS-INV-8 | Exit from safe-stop requires proof of state safety before Mode Controller broadcasts recovery. | Attempt exit without safety proof — verify recovery broadcast blocked |

---

## Relationship to Other Gap Contracts

| Gap | Relationship |
|---|---|
| Gap 3 — Cortex/Immune Interface | Safe-stop state is communicated immune-to-cortex through mode state only. Interface contract will formalize this channel. Safe-stop comes first because the channel's most critical message is safe-stop. |
| Gap 4 — Homeostasis Engine Policy | Homeostasis Engine computes health inputs used by Mode Controller. Safe-stop is triggered by Mode Controller quorum loss — not by homeostasis directly. Homeostasis contract can follow safe-stop. |
| Gap 5 — Memory Ingestion | No baseline updates permitted during safe-stop. Memory Ingestion contract must reference safe-stop as a blocking condition. Safe-stop comes first. |
| Gap 1 — Collective Immune System | CIS must not be built until safe-stop is contracted. CIS must know how to enter and exit safe-stop. Safe-stop comes first. |

---

## Overengineering Warnings

The following are explicitly out of scope for this contract. If any of these appear in a draft, the draft has scope-crept.

- Automatic safe-stop recovery logic
- Diagnosis or root cause analysis inside safe-stop
- New agent types spawned to "manage" safe-stop
- Homeostasis Engine definition
- CIS build authorization
- Changes to any existing signed contract
- Network-level isolation or firewall rules (control plane concern, not this contract)
- Safe-stop as a verdicting mechanism

---

## Open Questions for Matt — Required Before Contract Is Drafted

These five questions are inherited from the Handoff doc. All five must be answered before a design contract can be written. A contract with placeholder values is not signable.

| # | Question | Why it blocks the contract |
|---|---|---|
| OQ-1 | What is the safe-stop timeout for Mode Controller quorum loss? | SS-1 entry condition requires an exact value. No value = untestable invariant. |
| OQ-2 | What is the recovery window for two simultaneous CRITICAL watcher events? | SS-3 entry condition requires an exact value. No value = untestable invariant. |
| OQ-3 | Who exits safe-stop — Matt only or a rotating CIRT role? | Exit protocol section cannot be written without this. |
| OQ-4 | Does Homeostasis stay inside Mode Controller or become a separate contract? | Affects which components are named as safe-stop trigger sources. If Homeostasis Engine is separate, it must be listed. |
| OQ-5 | Does baseline ingestion after a closed threat event require operator approval every time, or only above a defined risk threshold? | Affects Gap 5 contract, but also affects what "proof of state safety" means at safe-stop exit. |

---

## Recommended Next Step

1. Matt reviews this concept doc and confirms it matches intent.
2. Matt answers OQ-1, OQ-2, OQ-3 at minimum (OQ-4 and OQ-5 can be deferred to their own gap contracts).
3. Claude drafts the Safe-Stop State Machine Design Contract against this concept doc and Matt's answers.
4. Matt signs (§11).
5. Contract committed to repo.
6. Cursor builds against the signed contract.

---

## Explicit Non-Authorizations

- This concept doc does not authorize any build activity.
- This concept doc does not amend any signed contract.
- This concept doc does not open the DEPTH GATE or authorize CIS work.
- This concept doc does not define the Cortex/Immune Interface contract.
- This concept doc does not define the Homeostasis Engine contract.
- No build authorization is implied by this research or this concept doc.
