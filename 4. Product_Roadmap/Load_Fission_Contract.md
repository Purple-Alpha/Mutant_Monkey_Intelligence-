# Load Fission — Agent Design Contract

## Agent Fission, Part 1: elastic horizontal scaling under volume

**Document type:** Agent Design Contract
**Status:** DRAFT — UNSIGNED. No build authorization until §11 is signed. Matt must read this before signing; the signature certifies operator review of a Cursor-authored scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against `4. Product_Roadmap/Agent_Fission_Concept_Doc.md` (CONCEPT, June 12 2026) plus the operator's locked answers from the June 12 2026 contract session.
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 5 MutationEngine (`02a2252`, GATED #88) + Blast Radius Controller (GATED #89, `f1c817e`) + Watcher Agents contract (**required — signed**, #85-87 currently RESERVED) + **at least one real tenant onboarded** for threshold calibration. Sibling contract: **Specialisation Fission** (`Specialisation_Fission_Contract.md`).

---

## §0 — Purpose

**Load Fission** is the *quantitative* half of Agent Fission: when a layer is saturated by inbound volume, a watcher triggers the swarm to **scale out horizontally** by spawning **copies of the parent specialist** that work the same problem in parallel. When volume drops, the swarm exhales the copies.

Load Fission is the **well-understood, lower-risk** trigger. A load-fission child is, by construction, an **exact copy** of an existing agent type — it never mints a new agent type, so it never reaches the operator-sign-off path. Its entire risk surface is "how many copies, born where, for how long" — and that surface is bounded by the Blast Radius Controller gates plus the locked decisions below.

This contract does **not** cover specialisation (an agent dividing because its problem space split). That is the sibling contract. The two are split precisely because they carry different risk profiles and different sign-off surfaces (concept §6 Q1, resolved: **two contracts**).

---

## §1 — Scope

### In scope

1. **LoadFissionController** — the component that receives a watcher's load-fission proposal (via the control plane), validates it against the locked decisions, spawns parent copies, and registers each child with the Blast Radius Controller gateway.
2. **FissionEventLog** — append-only record of every load-fission and load-exhale event (shared schema with the sibling contract; one log, two writers).
3. **Child lifecycle wiring** — every spawned copy is born inside the gateway (scoped identity, role-tiered budget, ring assignment, breakers) and writes only to its own namespace as proposed evidence (LF-D5).
4. **Automatic exhale** — retirement of load-fission copies when the threat level drops below the authorizing floor.

### Explicitly out of scope

- **Specialisation Fission** — an agent dividing into more narrowly specialised children, including any net-new agent type. Separate contract (`Specialisation_Fission_Contract.md`).
- **Threat-level ownership** — the control plane (Mode Controller / watcher hierarchy) owns the threat level. This contract *reads* it; it never sets it.
- **Watcher implementation** — the watcher that observes saturation and proposes fission is the Watcher Agents contract's job. This contract defines the **proposal interface** it consumes.
- **ReconciliationAgent fission** — the verdict producer (#84) **does not fission** (LF-D6). Out of scope by exclusion.
- **Fission depth beyond 1 generation** (LF-D2) — forbidden, not deferred.
- **Any change to Phase 1/2/3/4/5 or Blast Radius Controller signed surfaces.**

---

## §2 — Locked Design Decisions (confirm at signing)

| # | Decision | Locked value |
|---|---|---|
| LF-D1 | External trigger only | Agents **never** trigger their own fission. Only a **watcher**, via the control plane, may propose load fission. A self-replicating agent is forbidden by construction. |
| LF-D2 | **Maximum fission depth = 1 generation** | A parent may fission into children. **A child may not fission.** No grandchildren. Depth is hard-capped at 1 regardless of threat level or volume. A fission proposal targeting an agent that is itself a fission child is rejected. |
| LF-D3 | **Level 2 threat floor — all agents** | No fission below threat **Level 2 (HIGH)**. This floor applies to **every agent layer, including knowledge agents.** (This overrides the concept-doc cascade's ELEVATED/Level-1 entry for knowledge agents: knowledge-agent load fission also requires Level 2+.) |
| LF-D4 | Child inherits parent schema and type | A load-fission child is an **exact copy** of the parent: same agent type, same blackboard schema, same verdict/evidence contract, same role-separation constraints. A copy is **never a net-new type** and therefore never reaches the operator-sign-off path. |
| LF-D5 | **Separate namespace, proposed evidence only** | Each child writes to its **own separate namespace**, never the parent's partition. Child output is **proposed evidence only** — it is not a verdict, not a blocking recommendation, and not a signed decision. Reconciliation of child output into the verdict surface remains the ReconciliationAgent's sole authority (#84). |
| LF-D6 | ReconciliationAgent does not fission | The ReconciliationAgent ensemble (#84) is **excluded from fission entirely** — load or otherwise. The single-verdict-surface guarantee (Phase 4 lockdown) is preserved by never duplicating the verdict producer. |
| LF-D7 | Every fission event logged | Append-only `FissionEventLog` record per spawn and per exhale: trigger type (`load`), triggering watcher, threat level at trigger, parent id/type, child ids, schema id, namespace, timestamp. No silent fission. |
| LF-D8 | Automatic exhale | When the control plane lowers the threat level below the authorizing floor, load-fission copies are **automatically retired** — no operator action needed to shrink. Exhale is graceful: in-flight work finishes or hands off through the gateway; no tenant work is dropped. |
| LF-D9 | Born inside the gateway | Every child is registered with the Blast Radius Controller before it can act: scoped identity (BRC-D7), role-tiered budget (BRC-D14), ring assignment (BRC-D6), breakers (BRC-D1/D13). A child never lives outside the gateway. |
| LF-D10 | Conservative, amendment-tunable thresholds | Saturation thresholds and maximum copy counts launch **conservative** and are tunable **only by signed amendment** after real-tenant baseline data — never autonomously. |
| LF-D11 | Scoreboard row | Load Fission takes **one proposed scoreboard row, #90** (confirm at signing). LoadFissionController + FissionEventLog internal. |
| LF-D12 | Health score target + rubric track | ELITE 85+ required for closure. Scored on the **Layer 6 / Control Plane rubric track** (the fission mechanisms are control-plane surfaces), or a dedicated Fission sub-track added by amendment if the operator prefers — confirm at signing. |

---

## §3 — Component detail

### §3.1 — LoadFissionController

- **Input:** a load-fission proposal from a watcher via the control plane — `{ parent_type, layer, observed_saturation, threat_level, requested_copies }`.
- **Validates, in order:** external trigger authenticity (LF-D1) → threat level ≥ Level 2 (LF-D3) → parent is not itself a fission child (LF-D2) → parent type is not the ReconciliationAgent (LF-D6) → requested copies within the conservative cap (LF-D10).
- **On pass:** spawn N exact copies (LF-D4), register each with the gateway (LF-D9), assign each its own namespace (LF-D5), write a `FissionEventLog` spawn record (LF-D7).
- **On any failure:** reject the proposal, write a rejection record, spawn nothing. Fail-safe — partial spawning is forbidden.

### §3.2 — Child lifecycle and output

- A child works the **same problem as its parent in parallel** (quantitative scale-out).
- A child writes **only** to its own namespace, as **proposed evidence** (LF-D5). It cannot write to the parent's partition or to the verdict surface.
- A child **cannot fission** (LF-D2). Any proposal targeting a child is rejected at validation.

### §3.3 — Exhale

- Triggered automatically when the control plane lowers the threat level below Level 2 (LF-D8).
- Load-fission copies are retired first (they are pure elastic capacity).
- Graceful: in-flight work finishes or hands off through the gateway; an exhale record is written per retired child (LF-D7, symmetric).

### §3.4 — Relationship to the threat-level cascade

Load Fission reads the control-plane threat level; it never sets it. The Level-2 floor (LF-D3) is uniform across all agent layers, including knowledge agents — the concept doc's per-layer cascade still governs *which layers* may fission at each level above the floor, but **nothing fissions below Level 2.**

---

## §4 — Relationship to signed surfaces

| Signed surface | Relationship |
|---|---|
| Blast Radius Controller (`f1c817e`, #89) | Every child is born inside the gateway and governed by its gates. Fission proposes growth; the control plane decides whether each child may act, under what scope and budget. No BRC surface modified. |
| Phase 5 MutationEngine (`02a2252`, #88) | Mutation changes agent *quality*; load fission changes agent *quantity*. A fissioned copy may later be mutated; orthogonal mechanisms. |
| Phase 4 ReconciliationAgent (`d0cc849`, #84) | **Excluded from fission** (LF-D6). Verdict surface unchanged; child output is proposed evidence only (LF-D5), reconciled by #84 as today. |
| Watcher Agents (#85-87, RESERVED) | The trigger source (LF-D1). This contract consumes the watcher proposal interface; it does not build watchers. |
| Mode Controller (separate concept) | Owns the threat level / mode this contract reads. |

No signed surface is modified by this contract.

---

## §5 — Scoreboard layout

| Row | Agent | Status at signing | Layer |
|---|---|---|---|
| **#90** (proposed) | Load Fission Controller | `SIGNED_UNBUILT` → build → `GATED` | 6 Control Plane |

One row (LF-D11). Confirm row number at signing.

---

## §6 — Test requirements

Three test classes per AGENTS.md §5.

**Class 1 — Expected pass**
- Valid watcher proposal at Level 2+ spawns the requested copies, each gateway-registered with its own namespace.
- Each child writes proposed evidence only, to its own namespace.
- Threat level drops below Level 2 → all load-fission copies automatically exhaled; exhale records written.
- Every spawn and exhale produces an append-only `FissionEventLog` record.

**Class 2 — Adversarial**
- Agent attempts to trigger its own fission → rejected (LF-D1 — external trigger only).
- Fission proposal below Level 2 → rejected (LF-D3 — floor applies to knowledge agents too: a knowledge-agent proposal at Level 1 is rejected).
- Proposal targeting a fission child (depth 2) → rejected (LF-D2 — depth capped at 1).
- Proposal targeting the ReconciliationAgent → rejected (LF-D6).
- Child attempts to write to the parent's namespace or to the verdict surface → rejected (LF-D5).
- Child output presented as a verdict / blocking recommendation → rejected; proposed-evidence-only enforced (LF-D5).
- Requested copies exceed the conservative cap → rejected (LF-D10).

**Class 3 — Known-gap xfail**
- Real-tenant saturation-threshold and copy-cap calibration — deferred; needs real tenant baseline data. Completion path: signed amendment after onboarding.
- Live watcher wiring — deferred; needs the Watcher Agents contract gated. Completion path: Watcher Agents contract signed and gated.
- Live Mode Controller threat-level feed — deferred; interface only until the Mode Controller contract is gated.

---

## §7 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Agent self-triggers fission | Class 2 | Immediate fail — LF-D1 violated |
| Fission below Level 2 (any layer) | Class 2 | Immediate fail — LF-D3 violated |
| Depth-2 fission (grandchild) | Class 2 | Immediate fail — LF-D2 violated |
| ReconciliationAgent fissioned | Class 2 | Immediate fail — LF-D6 violated |
| Child writes to parent namespace / verdict surface | Class 2 | Immediate fail — LF-D5 violated |
| Child output treated as a verdict | Class 2 | Immediate fail — LF-D5 violated |
| Child born outside the gateway | Class 1/2 | Immediate fail — LF-D9 violated |
| Silent (unlogged) fission or exhale | Class 1/2 | Immediate fail — LF-D7 violated |
| Health score below 85 | Rubric | Phase does not close |

---

## §8 — Pre-conditions before build opens

1. Blast Radius Controller GATED — **satisfied** (#89, `f1c817e`).
2. Watcher Agents contract signed and gated — **open** (#85-87 RESERVED).
3. At least one real tenant onboarded for threshold calibration — **open**.
4. This contract §11-signed.

Pre-conditions 2 and 3 are tracked independently; the build does not open until all four hold.

---

## §9 — Closure checklist

Phase closes when all of the following are true:

- [ ] Gate-clean 0/0 (Grok completion gate clean, 0 warnings)
- [ ] Health score 85+ ELITE on the designated rubric track (LF-D12)
- [ ] Scoreboard row updated to `GATED`
- [ ] Matt signs phase closure
- [ ] `decision_cycles_log.md` PHASE_CLOSURE entry recorded
- [ ] Three test classes pass (Class 1 + Class 2; Class 3 documented xfail)

---

## §11 — Operator Sign-Off

**Status:** UNSIGNED DRAFT. Awaiting operator review and signature.

**Signed:** ____________________
**Date:** ____________________
