# Mutant Monkey Inbox Shield — Cortex / Immune Interface Concept Doc and Design Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Organism Design Doctrine v1 + Gap List Gap 3 + all signed/gated contracts
**Depends on:** Mode Controller (SIGNED), Privacy Filter (SIGNED), Blast Radius Controller (GATED), Watcher Agents (GATED), ReconciliationAgent (GATED), Safe-Stop State Machine (GATED + Amendment 01 SIGNED), Collective Immune System (SIGNED)

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

The Organism Design Doctrine defines two organs: the Cortex (interpretation) and the Immune System (stabilization). Seven Cortex-Immune interface rules exist in the Doctrine. They are not enforced by any signed contract today.

Without this contract, the boundary between organs is advisory only. Any component can communicate with any other component through any channel, and no test can prove otherwise.

This contract closes Gap 3 by making the interface rules enforceable and testable. It defines exactly which signals may cross the organ boundary, in which direction, under which conditions, and what is forbidden. It does not implement either organ. It governs only the channel between them.

### What the Interface Is

The Cortex/Immune Interface is the complete set of legal communication paths between the Cortex organ and the Immune organ. It is not a component. It is not a service. It is a governance contract that defines what is allowed to cross the boundary and what constitutes a violation.

**Cortex-to-Immune direction:** Cortex produces tenant-scoped evidence, observations, and signals. It hands these to the immune organ through governed paths only.

**Immune-to-Cortex direction:** The immune organ communicates back to the cortex through exactly four channels: mode state, reconciliation output, safe-stop state, and governed baseline updates. No other immune-to-cortex channel exists.

### What the Interface Is Not

- The interface is not a new component, service, or agent.
- The interface is not a message bus or event system — it governs what may travel on existing paths, not the transport itself.
- The interface does not implement any organ.
- The interface does not add new authority to any component.
- The interface does not create a new communication layer — it restricts existing ones.

---

## Part 2 — Design Contract

### Purpose

This contract defines the legal signals between the Cortex organ and the Immune organ, the forbidden channels, the evidence handoff rules, the reconciliation feedback rules, the baseline update boundary, and the no-hidden-channel invariant.

### Organ Definitions

For the purpose of this contract:

**Cortex** includes: Layer 0 Knowledge Agents, Layer 1 Detection Swarm, and any future cortex-lane agents defined by signed contract.

**Immune System** includes: Mode Controller, Privacy Filter, Blast Radius Controller, Watcher Agents, Fission v2, Mutation Engine, ReconciliationAgent, Safe-Stop State Machine, and Collective Immune System coordinator.

### Legal Cortex-to-Immune Signals

The following are the only signals a Cortex component may send toward the Immune organ. All other cortex-to-immune communication is forbidden.

| Signal | From | To | Condition | Must be |
|---|---|---|---|---|
| Evidence record | Detection agent | Evidence Ledger | After local analysis complete | Tenant-scoped, schema-valid, provenance-tagged, append-only |
| Observation record | Detection agent | ObservationLog | After signal classified | Tenant-scoped, no verdict fields, append-only |
| Anomaly signal | Detection agent | Watcher Agent | When local threshold exceeded | Tenant-scoped, no enforcement request, no verdict |
| Hypothesis record | Cortex process | Evidence Ledger | When hypothesis formed | Tenant-scoped, marked as hypothesis not verdict, append-only |

**Cortex components may not:**
- Write directly to verdict ledger
- Send signals to Mode Controller
- Send signals to Privacy Filter
- Send signals to Blast Radius Controller
- Send signals to Fission components
- Send signals to Mutation Engine
- Send signals to Safe-Stop State Machine
- Send signals to CIS coordinator
- Send any signal containing cross-tenant data

### Legal Immune-to-Cortex Signals

The following are the only signals the Immune organ may send toward the Cortex. All other immune-to-cortex communication is forbidden.

| Signal | From | To | Condition | Must be |
|---|---|---|---|---|
| Mode state broadcast | Mode Controller | All components including Cortex | On mode transition | Global, read-only for Cortex, epoch-stamped |
| Reconciliation output | ReconciliationAgent | Evidence Ledger | On verdict produced | Tenant-scoped, verdict only, no cortex logic modification |
| Safe-Stop state | Safe-Stop State Machine | All components including Cortex | On safe-stop entry or exit | Global, read-only for Cortex, halts cortex processing |
| Governed baseline update | Governed ingestion pipeline | Tenant baseline store | After full ingestion validation passes | Tenant-scoped, schema-valid, provenance-tagged, reversible, operator-approved if above threshold |

**Immune components may not:**
- Modify cortex agent logic, weights, or configuration at runtime
- Send enforcement instructions directly to cortex components
- Send signals that bypass the Evidence Ledger or ObservationLog as the handoff point
- Send cross-tenant evidence to any cortex component
- Create hidden feedback loops that alter cortex behavior without a logged, governed signal

### No-Hidden-Channel Invariant

No communication path between a Cortex component and an Immune component may exist that is not listed in this contract.

A hidden channel is defined as any of the following:
- Shared mutable state that both organs read and write without a logged handoff
- Direct function calls between organ components that bypass the Evidence Ledger or ObservationLog
- Side-channel signals embedded in log records that alter component behavior
- Implicit configuration sharing between cortex and immune components

If a hidden channel is detected, it is a contract violation. The channel must be closed. The violation is logged. No component may self-authorize a hidden channel.

### Evidence Handoff Rules

1. Cortex components write evidence to the Evidence Ledger. They do not hand evidence directly to any immune component.
2. Immune components read evidence from the Evidence Ledger. They do not receive evidence directly from cortex components.
3. The Evidence Ledger is the sole governed handoff point between cortex and immune for evidence.
4. The ObservationLog is the sole governed handoff point between cortex and immune for observations and anomaly signals.
5. All writes to Evidence Ledger and ObservationLog are append-only and immutable after commit.
6. No cortex component may read from the verdict ledger. Verdicts are immune outputs, not cortex inputs.
7. Governed baseline updates flow from the ingestion pipeline to the tenant baseline store. Cortex components read from the tenant baseline store. They do not write to it.

### Reconciliation Feedback Rules

1. ReconciliationAgent verdicts are written to the verdict ledger. They are not pushed to cortex components.
2. Cortex components do not poll the verdict ledger for instructions. Verdicts close events — they do not reprogram cortex behavior.
3. A reconciliation verdict may authorize governed baseline ingestion. The ingestion pipeline handles the update. The cortex agent reads the updated baseline on its next cycle. The cortex agent does not receive a direct signal that its baseline changed.
4. Named conflicts surfaced by ReconciliationAgent are written to the Evidence Ledger as conflict records. Cortex components may read these as evidence. They may not act on them as instructions.

### Baseline Update Boundary

1. Tenant baseline updates are the only permanent immune-to-cortex state change.
2. All baseline updates must pass: schema validation, provenance validation, tenant scope validation, reconciliation closure confirmation, audit log write, and rollback evidence creation.
3. Baseline updates above the defined risk threshold (OQ-5 seven triggers) require Matt Nichol operator approval before the update is written.
4. Below-threshold baseline updates pass through governed ingestion automatically if all validation gates pass.
5. No cortex component may detect or react to the fact that a baseline update required operator approval. The update arrives through the same governed path regardless of approval tier.
6. Baseline updates are tenant-scoped. A baseline update for Tenant A may not alter the baseline of Tenant B.

### Safe-Stop Interface Behavior

1. On Safe-Stop entry, the Safe-Stop state broadcast halts all cortex processing.
2. Cortex components do not produce new evidence, observations, or anomaly signals while Safe-Stop state is active.
3. Cortex components do not receive any immune signal during Safe-Stop other than the Safe-Stop state itself and the recovery broadcast on exit.
4. On Safe-Stop exit (Mode Controller recovery broadcast), cortex components resume normal processing under existing baseline and configuration. No cortex reconfiguration occurs as part of Safe-Stop recovery.

### Testable Invariants

All invariants are falsifiable.

| # | Invariant | Falsifiable test |
|---|---|---|
| CI-INV-1 | No cortex component writes to the verdict ledger. | Scan all cortex component outputs — verify no verdict ledger writes |
| CI-INV-2 | No cortex component sends signals directly to Mode Controller, Privacy Filter, BRC, Fission, Mutation Engine, Safe-Stop, or CIS. | Instrument all cortex-to-immune signal paths — verify only Evidence Ledger and ObservationLog writes |
| CI-INV-3 | No immune component modifies cortex agent logic, weights, or configuration at runtime. | Run full immune escalation cycle — verify no cortex agent config change |
| CI-INV-4 | Evidence Ledger is the sole governed handoff point for evidence between cortex and immune. | Attempt direct cortex-to-immune evidence pass bypassing ledger — verify blocked |
| CI-INV-5 | ObservationLog is the sole governed handoff point for observations and anomaly signals. | Attempt direct cortex-to-watcher signal bypassing ObservationLog — verify blocked |
| CI-INV-6 | No hidden channel exists between cortex and immune. | Audit all shared state, direct calls, and log side-channels — verify none present |
| CI-INV-7 | Cortex components halt new output on Safe-Stop entry. | Trigger Safe-Stop — verify no new Evidence Ledger or ObservationLog writes from cortex after entry log |
| CI-INV-8 | Governed baseline updates are tenant-scoped. A Tenant A update does not alter Tenant B baseline. | Apply baseline update to Tenant A — verify Tenant B baseline unchanged |
| CI-INV-9 | Cortex components do not read from the verdict ledger. | Instrument cortex component read paths — verify no verdict ledger reads |
| CI-INV-10 | Reconciliation verdicts do not directly reprogram cortex component behavior. | Produce a verdict — verify no cortex agent config or weight change results |
| CI-INV-11 | All Evidence Ledger and ObservationLog writes are append-only and immutable after commit. | Attempt modification of a committed record — verify rejected |
| CI-INV-12 | Above-threshold baseline updates require operator approval before write. | Trigger a high-impact baseline update — verify write blocked until Matt approval logged |

### Out of Scope

If any of the following appear in an interface build, the build has exceeded contract scope:

- Implementation of any cortex component
- Implementation of any immune component
- A new message bus, event system, or transport layer
- New authority structures of any kind
- Homeostasis Engine logic
- Memory consolidation logic beyond the baseline update boundary defined here
- Cross-tenant evidence aggregation
- Runtime cortex reconfiguration by any immune signal

### Non-Authorizations

- Signing this contract authorizes Cursor to implement interface enforcement only — the governed handoff points, the hidden-channel detection, and the invariant tests — within the scope defined above.
- This contract does not amend any existing signed or gated contract.
- This contract does not implement any cortex or immune component.
