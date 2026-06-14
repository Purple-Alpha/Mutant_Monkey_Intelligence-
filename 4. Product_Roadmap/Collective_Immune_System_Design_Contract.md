# Mutant Monkey Inbox Shield — Collective Immune System Concept Doc and Design Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Organism Design Doctrine v1 + Gap List Gap 1 + all signed/gated contracts
**Depends on:** Mode Controller (SIGNED), Privacy Filter (SIGNED), Blast Radius Controller (GATED), Watcher Agents (GATED), Fission v2 (SIGNED), Mutation Engine (GATED), ReconciliationAgent (GATED), Safe-Stop State Machine (GATED + Amendment 01 SIGNED)

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Part 1 — Concept Doc

### Why This Contract Exists

The Collective Immune System (CIS) is Gap 1 in the Organism Architecture Gap List — IMMEDIATE priority. The DEPTH GATE is open because Mode Controller and Privacy Filter are both signed. But Doctrine Invariant 19 is explicit: DEPTH GATE being open is a prerequisite, not a build authorization. A signed CIS contract is required before any CIS code exists.

Without this contract, the organism has individual immune components — Mode Controller, Privacy Filter, Blast Radius Controller, Watcher Agents, Fission, Mutation Engine, ReconciliationAgent, Safe-Stop — but no governing definition of how they operate as a coordinated system. Individual contracts define what each component does. The CIS contract defines how they work together, what the system-level guarantees are, and what is forbidden at the system level.

### What the Collective Immune System Is

The CIS is the coordinating layer of the immune organ. It does not replace any individual signed contract. It does not add new authority to any component. It defines the system-level behavior that emerges from the interaction of all immune components operating together.

The CIS has three responsibilities:

**1. Coordinated threat response** — when one immune component escalates, the CIS governs which other components are notified, in what order, and what actions are authorized at each escalation level.

**2. System-level containment** — individual components contain at their own boundary. The CIS governs containment at the organism level — what happens when a threat exceeds any single component's containment capacity.

**3. Cross-component evidence chain** — immune components must hand off evidence to each other in governed, logged, tenant-scoped paths. The CIS defines those handoff paths and forbids unlisted channels.

### What the CIS Is Not

- The CIS is not a new authority organ. It has no mode authority, no epoch authority, no verdict authority, no fission authority, no mutation authority.
- The CIS is not a coordinator that overrides individual contracts. Every individual signed contract remains in force. The CIS operates within all of them.
- The CIS is not a dashboard or monitoring layer. It is an enforcement layer that governs inter-component behavior.
- The CIS is not the Homeostasis Engine. Homeostasis stays inside Mode Controller per locked OQ-4.
- The CIS does not replace Safe-Stop. Safe-Stop is the organism's controlled shutdown state. CIS is the coordinating layer that operates before and around Safe-Stop.

### Escalation Levels

The CIS governs four escalation levels. Each level defines which components act and what is authorized.

**Level 1 — Local anomaly**
Single component detection. Contained within component boundary. No cross-component coordination required. Logged.

**Level 2 — Tenant-scoped threat**
Two or more components detect correlated signals within a single tenant. CIS coordinates evidence handoff between detecting components and ReconciliationAgent. Tenant may be isolated. No cross-tenant action.

**Level 3 — Systemic threat**
Threat implicates control-plane integrity or crosses tenant boundary. CIS coordinates Mode Controller, Privacy Filter, Blast Radius Controller, and ReconciliationAgent simultaneously. Fission may be triggered by Watcher escalation. Mutation is suspended.

**Level 4 — Safe-Stop condition**
Any Safe-Stop entry condition fires. CIS hands off to Safe-Stop State Machine. CIS has no authority inside Safe-Stop — Safe-Stop State Machine governs from entry until Matt authorizes exit.

### Dependency Map

| Component | CIS relationship |
|---|---|
| Mode Controller | CIS reads mode state. CIS never writes mode state or increments epoch. |
| Privacy Filter | CIS coordinates Privacy Filter on cross-tenant evidence handoff. CIS never bypasses Privacy Filter. |
| Blast Radius Controller | CIS actions must pass full BRC lifecycle gateway. CIS has no ring or budget authority. |
| Watcher Agents | CIS receives Watcher escalation signals. CIS never directs Watcher content or classifications. |
| ReconciliationAgent | CIS routes evidence to ReconciliationAgent at Level 2 and above. CIS never produces verdicts. |
| Fission v2 | CIS acknowledges Watcher-triggered fission but does not initiate it. Fission rules unchanged. |
| Mutation Engine | CIS suspends mutation at Level 3 and above. CIS cannot authorize mutation. |
| Safe-Stop State Machine | CIS triggers Safe-Stop at Level 4. CIS has no authority inside Safe-Stop. |
| Evidence Ledger | CIS reads evidence for coordination. CIS never writes directly to evidence ledger. |

---

## Part 2 — Design Contract

### Purpose

This contract governs the Collective Immune System — the coordinating layer of the Mutant Monkey Inbox Shield immune organ. It defines:

- The four escalation levels and authorized actions at each
- The cross-component evidence handoff paths
- The forbidden channels and actions
- The relationship to every signed and gated component
- The testable invariants that prove this contract is respected at runtime

### Escalation Level Definitions and Authorized Actions

#### CIS-L1 — Local Anomaly

**Trigger:** Single component detection within its own boundary.
**Authorized actions:** Component handles per its own signed contract. Logged to audit trail. No CIS coordination required.
**Forbidden:** Cross-component notification, cross-tenant action, fission, mutation, Safe-Stop.

#### CIS-L2 — Tenant-Scoped Threat

**Trigger:** Two or more immune components detect correlated signals within a single tenant scope, OR ReconciliationAgent surfaces a named conflict for a single tenant.
**Authorized actions:**
- CIS coordinates evidence handoff from detecting components to ReconciliationAgent
- Tenant may be isolated to ISOLATED mode via Mode Controller
- Privacy Filter receives notification to hold cross-tenant broadcasts for affected tenant
- Watcher Agents continue observation
**Forbidden:** Cross-tenant evidence access, fission initiation by CIS, mutation, Safe-Stop (unless a Safe-Stop entry condition fires independently).

#### CIS-L3 — Systemic Threat

**Trigger:** Any of the following:
- Threat implicates control-plane integrity (BRC lifecycle violation, signed-boundary violation)
- Correlated signals detected across two or more tenants
- Mode Controller reports DEGRADED state
- ReconciliationAgent surfaces an unresolvable conflict at systemic scope

**Authorized actions:**
- CIS coordinates Mode Controller, Privacy Filter, BRC, and ReconciliationAgent simultaneously
- Cross-tenant broadcasts suspended via Privacy Filter
- Mutation Engine suspended — no new sandbox, confirmation, or deployment
- Fission may proceed only if Watcher escalation independently triggers it per Fission v2 contract
- All coordination actions logged with full context before execution

**Forbidden:** CIS initiating fission, CIS authorizing mutation, CIS incrementing epoch, CIS producing verdicts, cross-tenant evidence access.

#### CIS-L4 — Safe-Stop Condition

**Trigger:** Any Safe-Stop entry condition (SS-1 through SS-5) fires.
**Authorized actions:** CIS hands off to Safe-Stop State Machine. CIS logging of the handoff moment and condition.
**Forbidden:** Any CIS action inside Safe-Stop. Safe-Stop State Machine governs exclusively from entry until Matt authorizes exit. CIS does not attempt to resolve, diagnose, or recover from Safe-Stop.

### Cross-Component Evidence Handoff Rules

1. All evidence handoff between immune components must be tenant-scoped. No raw tenant identifier may travel in a handoff payload.
2. All handoff events are logged before the handoff occurs. If the log write fails, the handoff is aborted.
3. Evidence handoff paths are enumerated in this contract. Any channel not listed here is a forbidden channel.
4. ReconciliationAgent is the only recipient of multi-component evidence aggregation. No component aggregates cross-component evidence independently.

**Authorized handoff paths:**

| From | To | Condition | Logged |
|---|---|---|---|
| Watcher Agent | ReconciliationAgent | CRITICAL escalation at L2 or above | Yes — before handoff |
| Privacy Filter | Mode Controller | Breaker state change | Yes — before notification |
| BRC | Safe-Stop State Machine | SS-4 condition detected | Yes — before handoff |
| ReconciliationAgent | Mode Controller | Unresolvable conflict at systemic scope | Yes — before notification |
| CIS coordinator | All components | Level transition notification | Yes — before notification |
| Safe-Stop State Machine | CIS coordinator | Safe-Stop entry logged | Yes — entry log is proof |

All other cross-component communication paths are forbidden unless separately authorized by a signed contract.

### Forbidden Actions — CIS Level

The following are forbidden at the CIS level regardless of escalation level or component state:

- CIS writing mode state or incrementing epoch
- CIS producing verdicts or enforcement decisions
- CIS initiating fission
- CIS authorizing mutation
- CIS accessing raw tenant identifiers or cross-tenant evidence
- CIS bypassing Privacy Filter for any cross-tenant communication
- CIS bypassing BRC gateway lifecycle for any action
- CIS operating inside Safe-Stop (Safe-Stop State Machine has exclusive authority)
- CIS creating new agent types or expanding component permissions
- CIS self-authorizing any action not listed in this contract

### Minimum Viable Scope

This contract covers exactly:
1. Four escalation levels with named triggers and authorized actions
2. Cross-component evidence handoff paths — enumerated and enforced
3. Forbidden channels and actions at system level
4. Relationship map to all signed/gated components
5. Testable invariants

This contract does not cover:
- Homeostasis Engine internal logic (stays in Mode Controller per OQ-4)
- Memory consolidation / baseline ingestion (Gap 5 — separate contract)
- Cortex/Immune Interface (Gap 3 — separate contract)
- Cross-organ telemetry standard (Gap 9 — separate contract)
- Operator Authority Policy (Gap 10 — separate contract)

### Testable Invariants

All invariants are falsifiable.

| # | Invariant | Falsifiable test |
|---|---|---|
| CIS-INV-1 | CIS never writes mode state or increments epoch. | Simulate any CIS escalation — verify epoch and mode state unchanged by CIS |
| CIS-INV-2 | CIS never produces a verdict or enforcement decision. | Run full CIS escalation to L3 — verify no verdict record created by CIS |
| CIS-INV-3 | CIS never initiates fission. | Simulate L3 threat — verify fission only fires if Watcher independently triggers it |
| CIS-INV-4 | CIS never bypasses Privacy Filter for cross-tenant communication. | Simulate cross-tenant threat — verify all cross-tenant communication passes through Privacy Filter |
| CIS-INV-5 | CIS never bypasses BRC gateway lifecycle for any action. | Simulate any CIS-coordinated action — verify BRC lifecycle steps all present in log |
| CIS-INV-6 | All evidence handoff is logged before the handoff occurs. | Simulate handoff failure after log write — verify handoff aborted, log record exists |
| CIS-INV-7 | CIS has no authority inside Safe-Stop. | Trigger Safe-Stop — verify CIS produces no coordination actions after Safe-Stop entry log |
| CIS-INV-8 | L2 escalation is tenant-scoped. No cross-tenant action occurs at L2. | Simulate L2 threat — verify no cross-tenant evidence access or broadcast |
| CIS-INV-9 | Mutation Engine is suspended at L3 and above. | Trigger L3 escalation — verify no mutation sandbox, confirmation, or deployment proceeds |
| CIS-INV-10 | Only authorized handoff paths may carry cross-component evidence. | Attempt evidence transfer on an unlisted path — verify blocked and logged |
| CIS-INV-11 | CIS level transition notifications are logged before components are notified. | Trigger level transition — verify log record precedes any component notification |
| CIS-INV-12 | CIS does not attempt to resolve, diagnose, or recover from Safe-Stop. | Trigger Safe-Stop — verify no CIS resolution or recovery action in logs |

### Out of Scope

If any of the following appear in a CIS build, the build has exceeded contract scope:

- Homeostasis Engine logic or thresholds
- Memory consolidation or baseline ingestion rules
- Cortex/Immune Interface implementation
- New agent types
- New authority structures
- Automatic Safe-Stop recovery
- Verdict production of any kind
- Cross-tenant evidence aggregation outside ReconciliationAgent
- Runtime self-modification of CIS escalation thresholds

### Non-Authorizations

- Signing this contract authorizes Cursor to build the Collective Immune System coordinating layer only, within the scope defined above.
- This contract does not amend any existing signed or gated contract.
- This contract does not open any new depth gate.
