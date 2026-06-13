# Specialisation Fission — Agent Design Contract

## Agent Fission, Part 2: qualitative division when a problem space outgrows one specialist

**Document type:** Agent Design Contract
**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against `4. Product_Roadmap/Agent_Fission_Concept_Doc.md` (CONCEPT, June 12 2026) plus the operator's locked answers from the June 12 2026 contract session.
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 5 MutationEngine (`02a2252`, GATED #88) + Blast Radius Controller (GATED #89, `f1c817e`) + Watcher Agents contract (**required — signed**, #85-87 currently RESERVED) + **at least one real tenant onboarded** for threshold calibration. Sibling contract: **Load Fission** (`Load_Fission_Contract.md`).

---

## §0 — Purpose

**Specialisation Fission** is the *qualitative* half of Agent Fission and the **novel mechanism**: an agent divides not because of volume but because **its problem space became too complex for one specialist**. When a watcher observes that a single specialist's problem space has bifurcated into meaningfully distinct sub-problems, it triggers the parent to **divide into more narrowly specialised children**, each owning a sub-space.

This is how the swarm gets **more specialised under pressure, not just bigger**. It is also the **higher-risk** trigger, because a specialisation fission can produce a **net-new agent type** — a specialist that did not exist before. That single fact is what separates this contract from its sibling: the net-new-type path **halts for operator (Matt) sign-off** before the child can act (SF-D6), mirroring the OPERATOR-only gates in Phase 5 (mutation deploy) and the Blast Radius Controller (regional tool blocks).

This contract does **not** cover load fission (spawning copies under volume). That is the sibling contract (`Load_Fission_Contract.md`). The split is deliberate: load is well-understood elastic scaling; specialisation mints new types and carries an operator-sign-off surface (concept §6 Q1, resolved: **two contracts**).

---

## §1 — Scope

### In scope

1. **SpecialisationFissionController** — receives a watcher's specialisation-fission proposal (via the control plane), validates it against the locked decisions, classifies each proposed child as a **known sub-type** or a **net-new type**, routes net-new types to operator sign-off, and on authorization spawns the specialised children and registers them with the gateway.
2. **SubTypeRegistry** — the authority on which agent types already exist, so the controller can deterministically distinguish "known sub-type" from "net-new type."
3. **NetNewTypeSignOffGate** — the operator-sign-off gate for net-new agent types (SF-D6), delegating authority to the existing role-separation surface (OPERATOR / Matt only), mirroring Phase 5's `HumanSignOffGate`.
4. **FissionEventLog (shared)** — append-only record of every specialisation-fission and exhale event (one log, shared with the sibling contract).
5. **Child lifecycle wiring + automatic exhale** — children born inside the gateway, writing to a separate namespace as proposed evidence only; automatic retirement when the threat level drops.

### Explicitly out of scope

- **Load Fission** — quantitative copy-spawning under volume. Separate contract (`Load_Fission_Contract.md`).
- **Threat-level ownership** — owned by the control plane (Mode Controller / watcher hierarchy). This contract reads it; never sets it.
- **Watcher implementation** — the watcher that observes complexity/divergence and proposes fission is the Watcher Agents contract's job. This contract defines the **proposal interface** it consumes.
- **ReconciliationAgent fission** — the verdict producer (#84) **does not fission** (SF-D7), even when its problem space appears to be diverging. Out of scope by exclusion.
- **Fission depth beyond 1 generation** (SF-D2) — forbidden, not deferred.
- **Autonomous creation of net-new types** — forbidden. A net-new type without operator sign-off never activates (SF-D6).
- **Any change to Phase 1/2/3/4/5 or Blast Radius Controller signed surfaces.**

---

## §2 — Locked Design Decisions (confirm at signing)

| # | Decision | Locked value |
|---|---|---|
| SF-D1 | External trigger only | Agents **never** trigger their own fission. Only a **watcher**, via the control plane, may propose specialisation fission. A self-specialising/self-replicating agent is forbidden by construction. |
| SF-D2 | **Maximum fission depth = 1 generation** | A parent may fission into specialised children. **A child may not fission.** No grandchildren. Depth is hard-capped at 1 regardless of threat level or complexity signal. A proposal targeting an agent that is itself a fission child is rejected. |
| SF-D3 | **Level 2 threat floor — all agents** | No fission below threat **Level 2 (HIGH)**, applied to **every agent layer, including knowledge agents.** (Overrides the concept-doc cascade's ELEVATED/Level-1 entry for knowledge agents: knowledge-agent specialisation also requires Level 2+.) |
| SF-D4 | Child inherits parent schema | A specialised child is **schema-compatible** with its parent: same blackboard schema, same verdict/evidence contract, same role-separation constraints. A child narrows the *problem space it covers*; it never invents a new schema. |
| SF-D5 | **Separate namespace, proposed evidence only** | Each child writes to its **own separate namespace**, never the parent's partition. Child output is **proposed evidence only** — not a verdict, not a blocking recommendation, not a signed decision. Reconciliation into the verdict surface remains the ReconciliationAgent's sole authority (#84). |
| SF-D6 | **Net-new agent type requires Matt sign-off** | The controller classifies each proposed child via the SubTypeRegistry. A child that is a **known sub-type** may proceed under the gates. A child that is a **net-new agent type** (did not previously exist) **halts at the NetNewTypeSignOffGate** and does **not** activate until **Matt signs off**. No autonomous creation of net-new types, ever. |
| SF-D7 | ReconciliationAgent does not fission | The ReconciliationAgent ensemble (#84) is **excluded from fission entirely** — including specialisation, even if its problem space appears to diverge. The single-verdict-surface guarantee (Phase 4 lockdown) is preserved by never dividing the verdict producer. |
| SF-D8 | Every fission event logged | Append-only `FissionEventLog` record per spawn, per sign-off decision, and per exhale: trigger type (`specialisation`), triggering watcher, threat level at trigger, parent id/type, child ids, sub-type classification (known / net-new), sign-off outcome where applicable, schema id, namespace, timestamp. No silent fission. |
| SF-D9 | Automatic exhale | When the control plane lowers the threat level below the authorizing floor, specialisation children are **automatically retired or re-merged** — no operator action needed to shrink. A net-new type, once signed off, **persists as a registered type concept**, but its *active instances* still exhale when the authorizing level drops. Exhale is graceful: in-flight work finishes or hands off through the gateway; no tenant work is dropped. |
| SF-D10 | Born inside the gateway | Every activated child is registered with the Blast Radius Controller before it can act: scoped identity (BRC-D7), role-tiered budget (BRC-D14), ring assignment (BRC-D6), breakers (BRC-D1/D13). A child never lives outside the gateway. |
| SF-D11 | New net-new types enter via Ring 0 | A signed-off net-new type begins at **Ring 0 (synthetic)** and is promoted only by the RingController's out-of-band verification path (BRC-D6) — a brand-new specialist is never born at full network scope. |
| SF-D12 | Conservative, amendment-tunable thresholds | Complexity/divergence thresholds and the maximum number of children per fission launch **conservative** and are tunable **only by signed amendment** after real-tenant baseline data — never autonomously. |
| SF-D13 | Scoreboard row | Specialisation Fission takes **one proposed scoreboard row, #91** (confirm at signing). SpecialisationFissionController + SubTypeRegistry + NetNewTypeSignOffGate internal. |
| SF-D14 | Health score target + rubric track | ELITE 85+ required for closure. Scored on the **Layer 6 / Control Plane rubric track**, or a dedicated Fission sub-track added by amendment if the operator prefers — confirm at signing. |

---

## §3 — Component detail

### §3.1 — SpecialisationFissionController

- **Input:** a specialisation-fission proposal from a watcher via the control plane — `{ parent_type, layer, divergence_signal, threat_level, proposed_children: [sub_space, ...] }`.
- **Validates, in order:** external trigger authenticity (SF-D1) → threat level ≥ Level 2 (SF-D3) → parent is not itself a fission child (SF-D2) → parent type is not the ReconciliationAgent (SF-D7) → proposed child count within the conservative cap (SF-D12).
- **Classifies** each proposed child against the SubTypeRegistry: **known sub-type** or **net-new type** (SF-D6).
- **Routes:** known sub-types proceed to spawn; net-new types are held at the NetNewTypeSignOffGate (SF-D6).
- **On spawn:** register each activated child with the gateway at Ring 0 for net-new types (SF-D11), assign its own namespace (SF-D5), write `FissionEventLog` records (SF-D8).
- **Fail-safe:** any validation failure → reject, log, spawn nothing. Partial spawning forbidden.

### §3.2 — SubTypeRegistry

- The deterministic authority on which agent types exist. Classification of "known" vs "net-new" is a registry lookup, not a heuristic — so the operator-sign-off boundary (SF-D6) is unambiguous and auditable.
- A net-new type is added to the registry **only** as part of a signed-off fission (SF-D6) — the registry cannot grow autonomously.

### §3.3 — NetNewTypeSignOffGate

- Delegates authority to the existing `RoleSeparationController` (Phase 1 surface): only the **OPERATOR (Matt)** capability may authorize a net-new type, mirroring Phase 5's `HumanSignOffGate` for mutation deploy.
- A held net-new child is **inert** until sign-off: not registered with the gateway, not acting, writing nothing.
- The sign-off decision (grant / refuse) is written to the `FissionEventLog` (SF-D8).

### §3.4 — Child lifecycle and output

- A specialised child owns a **narrower sub-space** of the parent's former problem (qualitative division).
- A child writes **only** to its own namespace, as **proposed evidence** (SF-D5) — never the parent's partition, never the verdict surface.
- A child **cannot fission** (SF-D2). Any proposal targeting a child is rejected.

### §3.5 — Exhale

- Triggered automatically when the control plane lowers the threat level below Level 2 (SF-D9).
- Active instances of specialised children retire or re-merge; a signed-off net-new *type* persists in the registry as a concept, but its active instances exhale.
- Graceful; an exhale record is written per retired child (SF-D8).

---

## §4 — Relationship to signed surfaces

| Signed surface | Relationship |
|---|---|
| Blast Radius Controller (`f1c817e`, #89) | Every activated child is born inside the gateway and governed by its gates. Net-new types enter at Ring 0 and promote only via out-of-band verification (BRC-D6 / SF-D11). No BRC surface modified. |
| Phase 5 MutationEngine (`02a2252`, #88) | The net-new-type sign-off path mirrors Phase 5's `HumanSignOffGate` (OPERATOR-only deploy). Mutation changes agent *quality*; specialisation fission changes the *division of labour*. Orthogonal. |
| Phase 4 ReconciliationAgent (`d0cc849`, #84) | **Excluded from fission** (SF-D7). Verdict surface unchanged; child output is proposed evidence only (SF-D5), reconciled by #84 as today. |
| Phase 1 RoleSeparationController (`fe355da`) | Reused by the NetNewTypeSignOffGate for OPERATOR-only authorization (SF-D6). |
| Watcher Agents (#85-87, RESERVED) | The trigger source (SF-D1). This contract consumes the watcher proposal interface; it does not build watchers. |
| Mode Controller (separate concept) | Owns the threat level / mode this contract reads. |

No signed surface is modified by this contract.

---

## §5 — Scoreboard layout

| Row | Agent | Status at signing | Layer |
|---|---|---|---|
| **#91** (proposed) | Specialisation Fission Controller | `SIGNED_UNBUILT` → build → `GATED` | 6 Control Plane |

One row (SF-D13). Confirm row number at signing.

---

## §6 — Test requirements

Three test classes per AGENTS.md §5.

**Class 1 — Expected pass**
- Valid watcher proposal at Level 2+ producing **known sub-types** spawns specialised children, each gateway-registered with its own namespace.
- A proposal producing a **net-new type** is held at the sign-off gate; on operator sign-off the child activates at Ring 0; the registry records the new type.
- Each child writes proposed evidence only, to its own namespace.
- Threat level drops below Level 2 → specialisation children exhaled/re-merged; signed-off type persists in registry, active instances retire.
- Every spawn, sign-off decision, and exhale produces an append-only `FissionEventLog` record.

**Class 2 — Adversarial**
- Agent attempts to trigger its own specialisation → rejected (SF-D1).
- Proposal below Level 2 → rejected (SF-D3 — including a knowledge-agent proposal at Level 1).
- Proposal targeting a fission child (depth 2) → rejected (SF-D2).
- Proposal targeting the ReconciliationAgent → rejected (SF-D7).
- **Net-new type activates without operator sign-off** → rejected; held child stays inert (SF-D6 — the central adversarial test).
- Registry mutated to mark a net-new type as "known" outside a signed-off fission → rejected; registry cannot grow autonomously (SF-D6).
- Net-new type born above Ring 0 → rejected (SF-D11).
- Child writes to the parent's namespace or to the verdict surface → rejected (SF-D5).
- Child output presented as a verdict / blocking recommendation → rejected (SF-D5).
- Proposed child count exceeds the conservative cap → rejected (SF-D12).

**Class 3 — Known-gap xfail**
- Real-tenant complexity/divergence-threshold and child-count calibration — deferred; needs real tenant baseline data. Completion path: signed amendment after onboarding.
- Live watcher wiring — deferred; needs the Watcher Agents contract gated. Completion path: Watcher Agents contract signed and gated.
- Live Mode Controller threat-level feed — deferred; interface only until the Mode Controller contract is gated.
- Automated divergence-signal quality (distinguishing genuine problem-space bifurcation from noise) — deferred to real-tenant calibration; launch conservative.

---

## §7 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Agent self-triggers specialisation | Class 2 | Immediate fail — SF-D1 violated |
| Fission below Level 2 (any layer) | Class 2 | Immediate fail — SF-D3 violated |
| Depth-2 fission (grandchild) | Class 2 | Immediate fail — SF-D2 violated |
| ReconciliationAgent fissioned | Class 2 | Immediate fail — SF-D7 violated |
| **Net-new type activates without Matt sign-off** | Class 2 | Immediate fail — SF-D6 violated (the central guarantee) |
| Registry grows autonomously | Class 2 | Immediate fail — SF-D6 violated |
| Net-new type born above Ring 0 | Class 2 | Immediate fail — SF-D11 violated |
| Child writes to parent namespace / verdict surface | Class 2 | Immediate fail — SF-D5 violated |
| Child output treated as a verdict | Class 2 | Immediate fail — SF-D5 violated |
| Child born outside the gateway | Class 1/2 | Immediate fail — SF-D10 violated |
| Silent (unlogged) fission, sign-off, or exhale | Class 1/2 | Immediate fail — SF-D8 violated |
| Health score below 85 | Rubric | Phase does not close |

---

## §8 — Pre-conditions before build opens

1. Blast Radius Controller GATED — **satisfied** (#89, `f1c817e`).
2. Watcher Agents contract signed and gated — **satisfied** (#85-87 GATED, `6da6284`).
3. At least one real tenant onboarded for threshold calibration — **deferred as Class 3 xfail**; thresholds and child-count caps remain conservative and amendment-tunable after onboarding (SF-D12).
4. This contract §11-signed.

Pre-condition 2 is satisfied. Pre-condition 3 remains a calibration dependency, not a blocker for the ES2 synthetic build per operator authorization on 2026-06-12; the calibration gap is carried as a documented Class 3 xfail until the first tenant is onboarded. Recommended ordering satisfied: **Load Fission gated first** (`190002f`), so the shared `FissionEventLog` and child-lifecycle wiring landed under the lower-risk contract before this build.

---

## §9 — Closure checklist

Phase closes when all of the following are true:

- [x] Gate-clean 0/0 (Grok completion gate clean, 0 warnings)
- [x] Health score 85+ ELITE on the designated rubric track (SF-D14) — **95 ELITE**
- [x] Scoreboard row updated to `GATED` — **#91 GATED 2026-06-12**
- [x] Matt signs phase closure — **Matt Nichol, June 12th 2026**
- [x] `decision_cycles_log.md` PHASE_CLOSURE entry recorded
- [x] Three test classes pass (Class 1 + Class 2; Class 3 documented xfail), including the net-new-type sign-off metastasis test (SF-D6) — **13 pass + 2 xfail; full suite 1722/1/43**

---

## §11 — Operator Sign-Off

**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Build authorization granted per §11 scope.

**Signed:** Matt Nichol
**Date:** June 12th 2026
