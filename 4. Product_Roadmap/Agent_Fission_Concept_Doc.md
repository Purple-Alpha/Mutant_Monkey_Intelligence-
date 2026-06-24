# Agent Fission — Concept Doc

> **Buyer-voice note (MMI-DEC-128):** GTM and one-screen orientation use **Lung Multiplier**, not "Agent Fission." This concept doc keeps **Agent Fission** as the internal engineering/design name for the contract session. See `mmi/MMI_MISSION_MAP.md` commercial lane and `mmi/concepts/MMI_LUNG_MULTIPLIER_VS_FISSION_GOVERNANCE_ADDENDUM.md`.

**Document type:** Concept / advisory-lane design note
**Status:** CONCEPT — advisory lane only. **No build authorization.** A §11-signed contract is required before any build.
**Date:** June 12 2026
**Author lane:** Cursor (execution lane), advisory only.

---

## §0 — What this is (and is not)

This is a **concept doc**, not a contract. It captures the Agent Fission model for a future contract session so the design is on disk and reviewable. It authorizes nothing. No code, no scoreboard row, no rubric track, and no build flow from this document. The build path is: this concept → §11 contract (with rubric amendment) → signed → build → gate → GATED.

**Agent Fission** is the controlled mechanism by which the swarm *grows new agents under pressure* — either to handle volume (elastic scaling) or because a problem space has become too complex for a single specialist to cover well. It is the counterpart to the Mutation Engine (#88, Phase 5): mutation makes existing agents *smarter*; fission changes *how many* agents there are and *how the work is divided*.

Fission is dangerous by nature — uncontrolled agent creation is exactly the failure shape the Blast Radius Controller exists to contain. So this concept is written defensively: **agents never trigger their own fission**, fission is **gated by threat level**, and **net-new agent types require Matt sign-off**.

---

## §1 — Core model: threat-level-gated fission cascade

Fission is a **cascade gated by threat level**. The swarm's current threat level is owned by the control plane (the Mode Controller / watcher hierarchy), **not** by any agent. As threat rises, progressively more of the swarm is permitted to fission. As threat falls, the swarm **exhales** (see §5).

### Threat levels and what may fission

| Level | Name | What may fission |
|---|---|---|
| 0 | **ROUTINE** | **No fission.** Steady state. |
| 1 | **ELEVATED** | **Knowledge agents** fission (Layer 2 knowledge-foundation agents — broaden coverage of the knowledge space). |
| 2 | **HIGH** | **Detection agents** fission (Layer 1 detection swarm — more detectors against a surging threat). |
| 3 | **CRITICAL** | **Full swarm** fission (all eligible layers, subject to governance). |

The cascade is **monotonic by level**: HIGH includes what ELEVATED permits; CRITICAL includes what HIGH permits. A higher level never *removes* a lower level's fission authority — it adds to it.

> **Note on the Level-2 governance floor (§4):** although ELEVATED (Level 1) names knowledge-agent fission in the cascade, the governance rule below sets the *operational* floor for fission authority at **Level 2+**. This tension is deliberate and is flagged as an open design point for the contract session — see §6 (it interacts with whether knowledge fission is treated as a distinct, lower-risk class).

---

## §2 — Two trigger types

Fission has **two distinct triggers**. Both are externally triggered (§4); they differ in *why* the swarm divides.

### §2.1 — Load Fission (elastic scaling under volume)

The well-understood case. A layer is saturated — too much inbound volume for the current agent count to handle within budget/latency. A watcher observes the saturation and triggers fission to **scale out horizontally**. Child agents are **copies of the parent specialist** working the same problem in parallel. When volume drops, the swarm exhales the extra copies.

Load fission is *quantitative*: same job, more hands.

### §2.2 — Specialisation Fission (the novel mechanism)

The new idea. An agent divides not because of volume but because **its problem space became too complex for one specialist**. A single detector covering, say, "invoice fraud" starts seeing a problem space that has bifurcated into meaningfully different sub-problems (e.g. vendor-impersonation invoices vs. compromised-internal-account invoices) that a single specialist cannot cover well. A watcher observes the *complexity / divergence* signal and triggers fission so the parent **divides into more narrowly specialised children**, each owning a sub-space.

Specialisation fission is *qualitative*: the job itself splits.

This is the mechanism that lets the swarm get **more specialised under pressure**, not just bigger. It is also the higher-risk trigger — a specialisation fission can produce a **net-new agent type** (a specialist that did not exist before), which is exactly the case that requires **Matt sign-off** (§4).

---

## §3 — Fission lifecycle (concept sketch)

```
Watcher observes pressure signal (volume OR complexity/divergence)
  → watcher proposes fission to the control plane    (agents never self-trigger)
  → control plane checks current threat level         (must be Level 2+, §4)
  → control plane checks which layer is eligible       (cascade table, §1)
  → Load fission?  → spawn parent copies (same schema, same type)
     Specialisation fission?
        → known sub-type?    → spawn specialised children (inherit parent schema)
        → net-new agent type? → HOLD for Matt sign-off before spawning
  → every fission event logged (append-only)           (§4)
  → children operate under Blast Radius Controller gates (identity, budget, rings, breakers)
  → threat level drops → automatic exhale               (§5)
```

Every child enters the world **already inside the control plane**: scoped identity, role-tiered budget, ring assignment, and breakers — fission does not create an agent that lives outside the gateway. This is the hard dependency on the Blast Radius Controller (§7).

---

## §4 — Governance rules (locked intent for the contract)

These are the non-negotiable governance properties the future contract must encode:

1. **External trigger only.** Agents **never** trigger their own fission. Only a **watcher** (via the control plane) may trigger fission. A self-replicating agent is forbidden by construction.
2. **Fission only at Level 2+.** No fission in ROUTINE; the operational floor for fission authority is **HIGH (Level 2) and above**. (See the §1/§6 note on how knowledge-agent fission at ELEVATED is reconciled with this floor.)
3. **Child agents inherit parent schema.** A child is schema-compatible with its parent — same blackboard schema, same verdict/evidence contract, same role-separation constraints. No child invents a new schema.
4. **Every fission event is logged.** Append-only fission record: trigger type, triggering watcher, threat level, parent, children, schema, timestamp. No silent fission.
5. **Net-new agent type requires Matt sign-off.** Load fission (copies) and fission into a **known** sub-type may proceed under the gates. Fission that produces an agent type **that did not previously exist** halts for **operator (Matt) sign-off** before the child becomes active — mirrors the OPERATOR-only gates in Phase 5 (mutation deploy) and the Blast Radius Controller (regional tool blocks).
6. **Exhale is automatic when threat level drops.** When the control plane lowers the threat level, the swarm automatically retires the fission-spawned agents that the lower level no longer authorizes. Exhale is **automatic** (no operator action needed to *shrink*); sign-off is only ever needed to *grow* a net-new type.

---

## §5 — Exhale (contraction)

Fission's inverse. When threat drops:
- **Load-fission copies** are retired first — they were pure elastic capacity.
- **Specialisation-fission children** are retired or re-merged per the level they were authorized at; a net-new specialist type, once signed off, persists as a concept but its *active instances* still exhale when the authorizing level drops.
- Exhale is **graceful**: children finish or hand off in-flight work through the control plane; no in-flight tenant work is dropped on contraction.
- Every exhale event is logged, symmetric with §4.4.

The breathing metaphor is exact: **inhale (fission) under pressure, exhale (retire) when pressure clears.** The swarm holds extra mass only as long as the threat justifies it.

---

## §6 — Open questions for the contract session

Four questions to resolve when this becomes a §11 contract:

1. **One contract or two?** Should **Load Fission** and **Specialisation Fission** be a single fission contract, or two separate contracts (load is well-understood elastic scaling; specialisation is the novel, higher-risk mechanism that mints net-new types)? They have different risk profiles and different sign-off surfaces.
2. **Maximum fission depth.** How many generations deep may fission go (parent → child → grandchild …)? Is there a hard cap, and does the cap differ by threat level or by trigger type? Uncapped depth is a blast-radius concern.
3. **Does the ReconciliationAgent ensemble fission?** The verdict producer (#84) is a three-voter ensemble and the **sole verdict surface**. Does it fission under load/complexity, and if so how is the single-verdict-surface guarantee preserved across fissioned voters? (Interacts with the Phase 4 lockdown and the per-voter sub-budgets in BRC-D14.)
4. **Do child agents write to the same blackboard as the parent?** Children inherit parent schema (§4.3), but do they share the parent's blackboard partition, or get their own? This determines tenant-isolation and reconciliation behaviour when many children report at once.

---

## §7 — Dependencies (must be satisfied before a build contract opens)

| Dependency | Status | Why it gates fission |
|---|---|---|
| **Phase 5 — Mutation Engine** | **GATED** (#88, 2026-06-12) | Establishes the controlled-evolution discipline (sandbox, sign-off, reversibility) that fission's net-new-type path mirrors. |
| **Watcher Agents contract** | **Required — signed** | Watchers are the *only* fission trigger (§4.1). No watcher contract → no legitimate trigger source. Currently #85-87 are RESERVED concept only. |
| **Blast Radius Controller** | **GATED** (#89, 2026-06-12) | Every fissioned child must be born inside the gateway (identity, budget, rings, breakers). Without containment, fission is uncontrolled replication. |
| **At least one real tenant onboarded** | **Required** | Threat-level thresholds and fission triggers (volume saturation, complexity/divergence) must be **calibrated on real tenant baseline data**, not synthetic — same launch-conservative, amendment-tunable discipline as BRC-D6/D14. |

Until all four are satisfied, Agent Fission stays in the advisory lane.

---

## §8 — Relationship to existing surfaces (concept only)

- **Mutation Engine (#88)** — mutation changes agent *quality*; fission changes agent *quantity / division of labour*. Complementary, not overlapping. A fissioned child may later be mutated; a mutated agent may later fission.
- **Blast Radius Controller (#89)** — the containment layer fission operates *inside*. Fission proposes growth; the control plane decides whether each child may act, under what scope, and with what budget.
- **Watcher hierarchy (#85-87, RESERVED)** — the trigger source. Local/regional/global watchers observe the pressure signals; the trigger authority follows the same bounded-blocking-power rules as BRC-D9 (regional actions require operator sign-off).
- **ReconciliationAgent (#84)** — the verdict surface whose fission behaviour is an explicit open question (§6.3).

No existing signed surface is modified by this concept. This document adds nothing to any scoreboard, rubric, or build map; it is a design note awaiting a contract.
