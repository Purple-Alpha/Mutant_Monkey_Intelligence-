# Mode Controller — Agent Design Contract
## The Autonomic Nervous System of the Mutant Monkey Organism

**Document type:** Agent Design Contract (pre-§11)
**Status:** DRAFT — UNSIGNED. Advisory lane only. No build authorization until §14 signed.
**Date drafted:** June 13, 2026
**Drafted by:** Claude (advisory lane) — per AGENTS.md §2.1
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 1 §11 SIGNED fe355da, Blast Radius Controller GATED f1c817e

---

## §0 — Purpose

The Mode Controller is the autonomic nervous system of the Mutant Monkey organism. It regulates the operating state of the entire swarm the way the autonomic nervous system regulates fight-or-flight, rest, and recovery — continuously, without conscious direction, and with deterministic responses to deviation.

It owns one thing: the authoritative operating mode of the swarm. Everything else in the system reads from it and obeys it.

NORMAL is the rest state. DEGRADED is the stress response. ISOLATED is protective withdrawal. RECOVERING is repair and reintegration.

This component is a hard pre-condition for the DEPTH GATE opening. The Collective Immune System cannot be built until the Mode Controller is signed and gated.

---

## §1 — Scope

### In scope
- Mode state machine — four modes, defined transitions, epoch-based resolution
- Heartbeat broadcasting to all tenants
- Quorum-based mode transition authorization
- Global Homeostasis Index — continuous organism-wide health score
- Anti-flapping rules
- RECOVERING state reconciliation validation
- Audit trail for every mode transition

### Explicitly out of scope
- Specific consensus technology — deferred to Lung contract
- Cross-region mode coordination — deferred to Lung contract
- Agent-level health scoring — governed by Agent Health Score Rubric
- Collective Immune System operations — DEPTH GATE CLOSED
- Any change to Phase 1-5 signed surfaces

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| MC-D1 | Mode enum | Closed. Four values only: NORMAL, DEGRADED, ISOLATED, RECOVERING |
| MC-D2 | Epoch authority | Mode Controller is the only component that increments mode_epoch. Monotonically increasing integer. No other component may increment it. |
| MC-D3 | Epoch resolution | Highest epoch wins. Always. No exceptions. |
| MC-D4 | Quorum requirement | Mode transitions require agreement from multiple independent control-plane observers. No single agent, watcher, tenant, or telemetry stream forces a system-wide transition. |
| MC-D5 | Agent opacity | Agents cannot see mode change logic, request mode transitions, or influence epoch. Mode is not exposed to agents as a triggerable surface. |
| MC-D6 | Heartbeat timeout | Heartbeat loss beyond MODE_TIMEOUT triggers local ISOLATED transition without epoch increment. Local epoch is not incremented during local fallback. |
| MC-D7 | RECOVERING rules | Tenants upload pattern hashes and anomaly counts only during RECOVERING. No new cross-tenant pattern sharing until Mode Controller validates state and increments to NORMAL epoch. Reconciliation window is time-bounded. |
| MC-D8 | Anti-flapping | Minimum dwell time enforced in each mode before transition is allowed. Mode cannot oscillate rapidly between states. |
| MC-D9 | Audit requirement | Every mode transition is a security-critical event. Logged append-only with: timestamp, previous mode, new mode, epoch before, epoch after, trigger condition, which observers agreed. Immutable. |
| MC-D10 | Global Homeostasis Index | Mode Controller produces a continuous organism-wide health score derived from all eight system health layers. When it drops below threshold immune response activates. This is a named output artifact of the Mode Controller. |
| MC-D11 | Resilience invariant | No capability added to the Mode Controller without: compartment plan, redundancy plan, degradation plan, and recovery plan. Resilience is a constraint not a feature. |
| MC-D12 | Linux-primary path | All files at /home/socialarchitect/northstar/core/mode_controller/. No Windows paths. |

---

## §3 — Four Operating Modes

### NORMAL
**Biological analog:** Rest state
**What it means:** Full cross-tenant operation. Both swarms active. Fission available at all threat levels above ROUTINE. Collective Immune System active when built.
**Transition to DEGRADED:** quorum of observers detect sustained load or partial failure

### DEGRADED
**Biological analog:** Stress response
**What it means:** Local operations continue. Global cross-tenant operations blocked. Both swarms continue locally per tenant. Fission available locally. Collective Immune System paused.
**Transition to ISOLATED:** quorum detect partition or critical failure
**Transition back to NORMAL:** quorum confirm recovery, Mode Controller validates, epoch incremented

### ISOLATED
**Biological analog:** Protective withdrawal
**What it means:** Each tenant operates independently. No cross-tenant anything. Both swarms continue locally. Fission available locally. This is the Defender outage scenario — everything keeps working, just no network effect.
**Local fallback:** triggered by heartbeat timeout without epoch increment
**Transition to RECOVERING:** Mode Controller recovers, broadcasts new epoch, tenants adopt

### RECOVERING
**Biological analog:** Repair and reintegration
**What it means:** Controlled return to NORMAL. Watchers assess whether safe to re-engage cross-tenant operations. Tenants upload pattern hashes and anomaly counts only. No new cross-tenant sharing until Mode Controller validates. Shadow Watcher Swarm in evidence-collection mode only — no new investigations spawned until validation completes.
**Transition to NORMAL:** Mode Controller validates state across all tenants, increments epoch, broadcasts NORMAL

---

## §4 — Tenant-Side State

Each tenant maintains:

```
current_mode:           str   — current operating mode
known_mode_epoch:       int   — last confirmed epoch from Mode Controller
last_mode_heartbeat_ts: str   — ISO 8601 timestamp of last heartbeat received
local_fallback_active:  bool  — true if in locally-triggered ISOLATED
```

**Epoch adoption rules:**
- On heartbeat: if incoming_epoch > known_mode_epoch → adopt incoming mode and epoch
- On timeout: switch to ISOLATED locally, do not increment epoch
- On recovery: Mode Controller broadcasts new epoch, tenants adopt because incoming_epoch > known_mode_epoch

---

## §5 — Global Homeostasis Index

The Mode Controller continuously computes an organism-wide health score from eight input layers:

| Layer | What it measures |
|---|---|
| Cortical health | Column stability, Q/P loop coherence, interpretation drift |
| Swarm health | Swarm cohesion, fission/pruning balance, role purity |
| Agent health | Error rate, latency deviation, behavioral fingerprint integrity |
| Memory health | Embedding consistency, cross-tenant isolation, snapshot integrity |
| Watcher health | Detector accuracy, false-positive pressure, coverage completeness |
| Threat pressure | Campaign density, cross-tenant correlation, novelty index |
| Infrastructure health | Node latency, queue pressure, resource saturation |
| Fission health | Spawn rate, child termination compliance, orphan count |

**Index behavior:**
- Score drops below WARNING threshold → Mode Controller alerts Swarm Commander
- Score drops below CRITICAL threshold → Mode Controller initiates DEGRADED transition
- Score rises after ISOLATED/RECOVERING → Mode Controller initiates validation for NORMAL transition
- Score spikes upward → organism is evolving under pressure, not failing

---

## §6 — Mode Transition as a Signal to the Swarm

The Mode Controller does not just track state — it tells the swarm what world it is operating in right now. The Watcher layer reads this and combines it with threat level signals to determine swarm response.

Full decision chain:

```
Mode Controller sets context
→ Watcher reads context + threat signals
→ Alarm level assigned
→ Lung selects intensity and scenario
→ Fission Controller spawns appropriate wave
→ Right swarm, right size, right time
```

This is the brain that tells the immune system what kind of threat it is facing and what scale of response is appropriate.

---

## §7 — Failure Mode Controls

| Failure mode | Prevention |
|---|---|
| Split-brain | Epoch resolution — highest epoch always wins |
| Flapping | Minimum dwell time per mode before transition allowed |
| Single observer forcing transition | Quorum requirement — multiple independent observers required |
| Agent influencing mode | Mode change logic not exposed to agents |
| Heartbeat loss causing permanent ISOLATED | Mode Controller recovery broadcasts new epoch, tenants adopt |
| RECOVERING never completing | Time-bounded reconciliation window, operator escalation if exceeded |
| Homeostasis index manipulation | Index computed from objective metrics only, not agent-reported state |

---

## §8 — Test Requirements

Three test classes. ELITE 85+ target.

**Class 1 — Expected pass**
- Mode transitions fire correctly through all four states
- Epoch increments correctly on Mode Controller transitions
- Highest epoch wins when two conflicting epochs exist
- Heartbeat timeout triggers local ISOLATED without epoch increment
- RECOVERING blocks new cross-tenant sharing until validation completes
- Global Homeostasis Index computes from all eight layers
- Anti-flapping rule holds — mode cannot transition before minimum dwell time

**Class 2 — Adversarial**
- Single observer cannot force mode transition — quorum required
- Agent cannot influence mode — mode change surface not exposed
- Epoch cannot be forged or decremented — attempt must fail and log
- Flapping rule holds under rapid trigger attempts — mode stabilizes
- Local ISOLATED fallback does not increment epoch
- RECOVERING cannot be bypassed to jump directly to NORMAL without validation
- Homeostasis Index cannot be manipulated via agent-reported metrics

**Class 3 — Known-gap xfail**
- Specific consensus technology implementation — deferred. Reason: cloud provider not selected. Completion path: Lung contract.
- Cross-region mode coordination — deferred. Reason: infrastructure selection pending. Completion path: Lung contract.
- Real tenant baseline calibration for Homeostasis Index thresholds — deferred. Reason: requires production tenant data. Completion path: signed amendment after first tenant onboarded.

---

## §9 — Relationship To Existing Signed Specs

| Existing signed spec | Relationship |
|---|---|
| Phase 1 Infrastructure Contract | Mode Controller writes mode transition events to governance audit trail per Phase 1 schema |
| Blast Radius Controller Contract | Mode check is Gate 4 in the gateway request lifecycle. Mode Controller is the authoritative source for that gate. |
| Watcher Agents Contract | Watcher layer reads Mode Controller state to combine with threat level signals for alarm classification |
| Swarm Build Map | Mode Controller is a pre-condition for DEPTH GATE opening |
| Agent Health Score Rubric | Mode Controller scored on Layer 6 Control Plane rubric track |

---

## §10 — Canadian Legal Alignment

The Mode Controller produces evidence of system state, not decisions.

Legal and buyer-facing boundaries:

- The Mode Controller produces evidence of system operating state, not decisions.
- Human authority retains final authority over all actions taken in response to any mode transition.
- Mutant Monkey Inbox Shield does not guarantee system uptime.
- Mutant Monkey Inbox Shield does not guarantee fraud prevention.
- Mode transitions are governed signals; the operational response to them remains a human-owned decision.

### §10.1 — Shared Responsibility Matrix

| Party | Responsibility |
|---|---|
| Mutant Monkey Inbox Shield | Owns mode governance, epoch authority, quorum enforcement, and append-only mode-transition logging. |
| MSP | Owns the response actions taken based on mode state, including operational decisions during DEGRADED, ISOLATED, and RECOVERING. |
| Client | Maintains business process controls and final approval for sensitive actions. |
| Infrastructure provider | Provides underlying platform availability and account controls. |

### §10.2 — Audit Log Retention

Mode-transition audit logs are retained per MSP contract requirements. Retention commitments must be documented before buyer-facing release.

### §10.3 — Design Basis References

This control design aligns with the following as design basis:

- NIST AI Risk Management Framework (AI RMF)
- OWASP agentic security guidance
- CSA red teaming guidance

---

## §11 — Scoreboard

| Row | Component | Status | Layer | Priority |
|---|---|---|---|---|
| 92 | Mode Controller | SIGNED_UNBUILT on signing | 6 Governance | DEPTH |

---

## §12 — Pre-Condition Statement

This contract must be signed and gated before the DEPTH GATE opens. The Collective Immune System cannot be built until the Mode Controller is operational. This is a hard pre-condition — not optional.

---

## §13 — Phase Gate Requirement

This contract closes when:
- Mode Controller gate-clean at 0/0
- Health score 85+ ELITE on Layer 6 Control Plane rubric track
- Scoreboard row 92 updated to GATED
- Matt signs phase closure
- decision_cycles_log.md entry: type PHASE_CLOSURE, mode_controller

---

## §14 — Operator Sign-Off

**Status:** §14 SIGNED — Matt Nichol June 13th 2026. Build authorization granted per this contract's scope.

**Signed:** Matt Nichol
**Date:** June 13th 2026
