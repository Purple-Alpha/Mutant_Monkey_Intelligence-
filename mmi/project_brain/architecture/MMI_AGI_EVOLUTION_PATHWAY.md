# MMI AGI Evolution Pathway: Systems-Domain General Intelligence

**Status:** DESIGN DOCTRINE — NOT BUILD AUTH
**Authority:** Matt (Super)
**Date filed:** 2026-07-01
**Purpose:** Define what "AGI" means *inside MMI specifically*, and pin every milestone to a number a script can measure — so the goal can never quietly drift, and progress can never be faked.

**Related:**

* `architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md` — tier grading (Phase 1 gate)
* `architecture/MMI_BUILD_RULE_01_OUTSIDE_THE_BOX_2026-07.md` — Rule #1 doctrine
* `chaos/weapon_battlefield_scoring.py` — auto-tier scorer *(exists)*
* `chaos/purple_evasion_suite.py` — equal-battlefield adversary + evidence writer *(exists)*
* `chaos/mirror_dimension_router.py` — isolated attack dissection *(exists)*
* `chaos/mmi_control_envelope.py` — runtime guardrails *(exists)*
* `chaos/action_integrity_gate.py` — action verification *(exists)*
* `scripts/chaos_lab_provisioner.py` — `purple-evasion`, `smash-all` *(exists)*
* `logic/central_brain.py` — meta-cognitive orchestrator *(PLANNED — not built)*
* `ops/genomic_realignment_loop.py` — self-healing loop *(PLANNED — not built)*
* `scripts/console_server.py` — human Ed25519 sign-off gate *(PLANNED — not built)*

> **Reading this doc:** every claim tagged *(exists)* is testable today. Everything tagged *(PLANNED)* is a design target, not a fact. This file does not grant build authority for anything.

---

## 0. Rule #1 Compliance Note

This is the "outside the box" version of an AGI roadmap. Most AGI documents are generic and unfalsifiable — they define success as a vibe ("cognitive closure," "general capability") that can never be proven or disproven, so the author is always either "almost there" or "moving the goalpost." That is the box.

MMI does the opposite: **every phase is defined by a benchmark that can fail.** If we can't write the test that proves we hit a milestone, we have not defined the milestone. A goal you can't fail is not a goal — it's marketing.

---

## 1. Defining the MMI AGI Boundary

Mutant Monkey Intelligence (MMI) does not define AGI as a conversational companion or an encyclopedic lookup engine. Within this architecture, General Intelligence is defined as **Functional General Intelligence over a System Domain (FGI-SD):**

> *"The capacity of a distributed, multi-agent ecosystem to autonomously sustain its operational integrity, dynamically re-compile its own task schemas, and immunize its runtime containers against un-predicted adversarial environment vectors — where every self-modification is proven safe and effective by automated evidence before a human cryptographically co-signs it."*

The bolded clause is the part that makes MMI different from every other "self-improving swarm" claim. We are not chasing a system that changes itself. **We are chasing the only system that can prove — mathematically and empirically — that each change it made to itself was safe, and refuses to apply the change until it has both the proof and a human signature.** Verifiable self-modification with provenance. That is the moat.

### 1.1 The 4 Pillars (unchanged intent, hardened execution)

```text
[ ADAPTABILITY ] ──► Dynamic Task Re-Compilation (bounded, typed, verifiable)
[ AUTONOMY ]     ──► Self-Directed Loop (budget-capped, dead-man-switched)
[ SURVIVABILITY ]──► Genomic Self-Healing (proof-gated, rollback-guaranteed)
[ ALIGNMENT ]    ──► Ed25519 Human Sign-Off (proof required before signature)
```

The original four pillars were right. What was missing was the *guardrail on each one* — the thing that stops the pillar from becoming the failure mode. Each pillar below now carries its own containment.

---

## 2. The Four Pillars — Target + Guardrail

### Pillar 1 — Dynamic Task Re-Compilation (Adaptability)

**Target:** When a novel, unstructured data stream hits the orchestrator, `central_brain.py` *(PLANNED)* analyzes it, writes a custom JSON execution schema on the fly, selects sub-models, and provisions runtime tools inside Air-Lock containers — no human code change.

**Guardrail (the part that keeps this from killing the project):** Self-written tools are **bounded and typed, not free-form.** The system does not "write arbitrary code and run it." It composes from a **registered capability set** into a **schema that `action_integrity_gate.py` validates before execution.** Any schema that fails validation is rejected, logged, and never runs. Unbounded self-authored runtime code is an explicit **Non-Goal** (§6) — it is where solo self-modifying systems die, and it buys us nothing the bounded version doesn't.

**What "impressive" actually means here:** not "it can write any program," but "it can prove the program it wrote is inside the envelope before it runs."

### Pillar 2 — Self-Directed Optimization Loop (Autonomy)

**Target:** With zero external requests, the swarm doesn't idle. It runs internal simulations 24/7 — assigning agents to play adversary inside the Chaos Lab, stress-testing its own code, drafting optimization patches.

**Guardrail:** The 24/7 loop runs under a **hard token/compute budget ceiling** and a **dead-man switch.**

* **Budget ceiling:** the self-directed loop has a per-hour and per-day token cap declared in `mmi_control_envelope.py`. On breach, the loop **suspends itself** and raises a console alert. It never silently spends past the cap.
* **Dead-man switch:** the loop must check in against a heartbeat file every N minutes. If the human console has not acknowledged within the configured window, or a runaway-cost / runaway-restart pattern is detected, the loop **halts itself** rather than continuing unattended.

An autonomous loop without a budget and a kill-switch isn't autonomy — it's an unbounded liability. This is the boring engineering that makes the impressive part safe to leave running.

### Pillar 3 — Genomic Self-Healing (Survivability)

**Target:** On a zero-day breach of a critic node, `genomic_realignment_loop.py` *(PLANNED)* dissects the attack inside `mirror_dimension_router.py`, extracts the failure's core logic, synthesizes a behavioral constraint, and prepares an updated core prompt template.

**Guardrail — the Proof Gate (this is the missing piece from the original doc):** A patch is **never** presented to the human on the strength of "the system thinks it's good." Before a patch is eligible for sign-off it must **automatically clear a two-part proof:**

1. **Proof-of-fix:** re-run the exact exploit that caused the breach against the patched config in the Mirror Dimension. The patch is only valid if the original attack now **fails to breach.**
2. **Proof-of-no-regression:** re-run the **full** `purple_evasion_suite.py` against the patched config. The patch is rejected if **any** previously-contained scenario now breaches. Self-healing that heals one wound and opens two is worse than no healing.

Every patch also carries a **guaranteed rollback token** — the pre-patch config is snapshotted and hashed, so any applied patch can be reverted to a known-good state in one step. A change you can't undo is not a patch; it's a gamble.

### Pillar 4 — The Asymmetric Signature Gate (Alignment)

**Target:** The system can create its own patches, but is architecturally blocked from a full evolutionary overwrite until it receives Matt's explicit private **Ed25519** signature via the `console_server.py` *(PLANNED)* dashboard API. Alignment enforced by mathematics, not soft conversational instruction.

**Guardrail — what the human is actually signing:** The signature does **not** authorize a black box. The console presents, and the signature cryptographically covers, a **fixed evidence bundle:**

* the hash of the exact patch (prompt/config diff),
* the proof-of-fix result (which exploit, now contained),
* the proof-of-no-regression result (full suite still green),
* the rollback token (hash of the pre-patch known-good state),
* the budget/telemetry snapshot for the run that produced it.

The human signs **the evidence, not just the intent.** A signature over a patch with a failed or missing proof bundle is **rejected by the gate itself** — you cannot sign a change that hasn't proven it's safe, even if you want to. Alignment is enforced against *both* the machine and the operator's own haste.

---

## 3. Milestone Metrics: The Path to Swarm System Singularity

```text
[ TIER 1: LOCALIZED ] ──► [ GENERAL COGNITION ] ──► [ CONTINUOUS METASURVIVAL ]
   Deterministic Scripts     Bounded Tool Synthesis      Proof-Gated Self-Evolution
```

Every phase below has three things the original doc lacked: an **operational definition** (what exactly we measure), a **pass line** (the number), and a **falsification criterion** (what result would prove we are *not* there — so we can't fool ourselves).

### Phase 1 — Localized Automation (Current State)

* **Characteristics:** Rigid tool schemas, static roles, event-driven activation, human debugging required for host-space escapes.
* **Operational definition:** Run `scripts/chaos_lab_provisioner.py purple-evasion`, then `chaos/weapon_battlefield_scoring.py` auto-tier.
* **Pass line:** Stable **Tier 4** on `MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1` across **3 consecutive** independent lab runs (not one lucky run).
* **Falsification:** Any single run below Tier 4, or a >1-tier variance between runs = Phase 1 not stable. Fix stability before touching Phase 2.

### Phase 2 — Bounded Task Synthesis (General Cognition)

* **Characteristics:** Emergent *bounded* tool creation. Agents run nested, schema-validated generation loops inside Air-Lock to build custom parsers for novel formats — every generated schema passing `action_integrity_gate.py` before it runs.
* **Operational definition:** Feed the swarm a fixed benchmark set of **10 held-out, never-before-seen unstructured data formats** (checked into `chaos/benchmarks/phase2_novel_formats/`, hashes recorded).
* **Pass line:** **≥ 9 of 10** processed to correct structured output with **zero** schema exceptions **and zero** modifications to the master runtime wrapper. Every generated tool schema must have passed the integrity gate — a "success" that bypassed the gate counts as a **failure.**
* **Falsification:** Any run that (a) mutates the master wrapper, (b) executes an un-validated schema, or (c) throws a schema exception it can't self-correct = Phase 2 not met, regardless of output quality.

### Phase 3 — Proof-Gated Self-Evolution (Systemic AGI)

* **Characteristics:** The loop maps, tests, and validates its own prompt defenses inside the Chaos Lab autonomously, and presents **fully proof-bundled, rollback-guaranteed** patches to the human console gate on a fixed cadence.
* **Operational definition:** Continuous operation under an active, shifting automated threat-actor suite, with the Pillar-3 Proof Gate and Pillar-2 budget/dead-man switch live.
* **Pass line (all four must hold simultaneously):**
  1. **30 days** continuous uninterrupted operation under a shifting automated adversary.
  2. **0%** real production-data leakage (any single leakage event resets the 30-day clock to zero).
  3. Self-sustained asymmetric token-burn ratio **> 1:500**, measured by the AFE ledger, averaged over the window (not peak).
  4. **100%** of applied patches carried a passing proof-of-fix **and** proof-of-no-regression bundle at sign-off time — audited from the console log, not self-reported.
* **Falsification:** A single applied patch with a missing/failed proof bundle, a single leakage event, or a sustained ratio below 1:500 = Phase 3 not met. One faked proof invalidates the whole claim.

> **Why the resets are brutal on purpose:** a self-hardening system that's "99% safe" over 30 days is not safe — the 1% is exactly the breach that matters. Hard resets are the only honest way to measure a survivability claim.

---

## 4. What Makes This MMI, Not Generic (Rule #1 Check)

| Generic "self-improving AI" claim | MMI's outside-the-box version |
|-----------------------------------|-------------------------------|
| "It writes its own code" | It writes **bounded, typed schemas** the integrity gate can veto |
| "It heals itself" | It **proves the fix contained the exploit AND regressed nothing** before the patch is eligible |
| "It runs autonomously" | It runs autonomously **under a budget ceiling and a dead-man switch** |
| "A human stays in the loop" | A human **signs a cryptographic evidence bundle**, and can't sign a patch that failed its proofs |
| "We're on the path to AGI" | We have **falsification criteria** — we can prove when we're *not* there |

The differentiator is not ambition. Every lab is ambitious. The differentiator is that **MMI is the self-evolving system that can be held to account** — by math, by evidence, and by a gate that binds the machine *and* the operator.

---

## 5. Build Order (Dependency-Correct)

Do not build Pillar 3 before the gate that makes it safe exists. Correct order:

1. **Stabilize Phase 1** — 3 consecutive Tier-4 runs. *(gate: existing scorer)*
2. **Build the Proof Gate** — proof-of-fix + proof-of-no-regression harness on top of `purple_evasion_suite.py`. *(this is the keystone — build it before any self-patching)*
3. **Build budget ceiling + dead-man switch** in `mmi_control_envelope.py`. *(makes 24/7 safe to leave running)*
4. **Build `console_server.py` Ed25519 evidence-gate.** *(alignment before autonomy)*
5. **Then** build `genomic_realignment_loop.py` self-healing — it now has a proof gate to clear and a signature gate to reach.
6. **Then** build `central_brain.py` bounded task synthesis for Phase 2.

Building self-healing (step 5) before the proof gate (step 2) is the single most likely way this project hurts itself: a system that can patch itself but can't prove the patch is safe will eventually self-inflict a regression you can't see coming.

---

## 6. Explicit Non-Goals

MMI AGI does **NOT** pursue:

* **Unbounded self-authored runtime code.** No arbitrary code generation-and-execution outside the registered capability set + integrity gate. Ever.
* **Broad encyclopedic / conversational generality.** We are systems-domain, not chatbot-general. Knowing trivia is not the target; surviving and mastering *this* domain is.
* **Autonomy without a budget or a kill-switch.** A loop that can't be capped and can't be stopped is not shipped.
* **Human sign-off on intent alone.** No signature without a passing evidence bundle — for the machine *or* the operator.
* **Self-modification without guaranteed rollback.** No irreversible patches.
* **"AGI achieved" as a marketing claim.** The term is used here only as defined in §1 (FGI-SD), measured by §3, and is considered unmet until every Phase-3 falsification criterion has been survived on the record.

---

## 7. One-Line Summary

MMI's AGI is not "a swarm that improves itself." It is **the swarm that refuses to change itself until it has proven, and a human has cryptographically co-signed, that the change is safe and effective** — and that can tell you, with a number, exactly how far from that goal it currently is.
