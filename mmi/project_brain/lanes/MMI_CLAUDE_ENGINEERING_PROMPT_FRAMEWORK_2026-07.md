# MMI Claude Engineering Prompt Framework

**Status:** CANONICAL — DESIGN DOCTRINE — prompt routing for Claude lane only  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01 · **Matt reaffirmed:** 2026-07-03  
**Maintained by:** Cursor PM (handoff packaging)  
**Purpose:** Maximize architectural accuracy and bounded code quality from Claude on MMI — not generic chatbot output.

> **DO NOT LOSE THIS FILE.** Every Claude handoff MUST be built from this framework + a `lanes/CLAUDE_HANDOFF_*.md` two-message file (MESSAGE 1 generate → MESSAGE 2 adversarial review). Cursor agents: read this before packaging any Claude payload. Never invent ad-hoc Claude prompts.

**Related:**

* `status/MMI_LANE_ROUTING.md` — Claude owns Design lane; Matt relays handoffs
* `architecture/MMI_METADATA_ICEBERG_2026-07.md` — depth-layer build order
* `architecture/MMI_AGI_EVOLUTION_PATHWAY.md` — falsifiable milestones
* `chaos/canary_metadata_layer.py` — multi-shot pattern reference (Layer 8)

> **Rule:** This file does not grant build authority. Seeded tasks and Matt `authorize build` still required before repo implementation.

---

## 0. Why this exists

To get the absolute best out of Claude (Anthropic frontier models like Claude 3.5 Sonnet) for a complex, hyper-engineered build like the MMI Self-Healing Matrix, **stop treating it like a standard chatbot.** Format inputs to exploit how Claude's transformer weights handle spatial syntax, structural hierarchy, and systemic reasoning.

Claude has a massive context window and strong reasoning traits, but **defaults to conversational fluff** unless you explicitly lock it into an advanced engineering role. MMI work is hyper-engineered, bounded, and adversarial — prompts must exploit structural syntax, not vibe.

Cursor PM uses this doc when packaging **Claude lane handoffs** for Matt to relay.

---

## 1. Exploit Claude's XML tag bias

Claude is **explicitly trained on, and biased toward, structured XML tags.** It uses them as strict attention-weight anchors. If you pass code, specs, or context inside standard markdown backticks, Claude treats it as continuous narrative text. If you wrap it in XML, Claude separates it into isolated variable spaces.

**Why it works:** This format eliminates token leakage and context drift. Claude references your actual repository items with near-zero hallucinations because it maps dependencies cleanly between the defined tags.

**Wrap every Claude payload like this:**

```xml
<system_role>
You are an uncompromised, low-level security compiler working on the MMI system.
Design lane only — produce specs, contracts, or bounded code per task. No scope expansion.
</system_role>

<production_inventory>
Relative paths and code blocks from the repo only.
Example: chaos/metadata_ingress_gate.py, chaos/canary_metadata_layer.py
</production_inventory>

<target_objective>
One bounded deliverable. Example: spec for Layer 4 behavioral fingerprint with record-only cold start.
</target_objective>
```

**Why it works:** Dependencies map cleanly between tags; Claude references declared inventory instead of inventing files.

---

## 2. Force raw code output (no explanations)

Default Claude behavior: preamble → snippet → postamble. That burns latency and context on non-shippable tokens.

**Append to every Claude payload (Invariant Directive):**

```text
Respond with the production-grade source code file payload only. Do not provide introductory remarks. Do not provide conversational closeouts or post-code explanations. If there are edge cases or structural assumptions, document them strictly inside native code comments within the file script itself.

DESIGN-LANE ADAPTATION: If architecture-only, respond with the complete markdown spec file only — same no-filler rule. Assumptions in footnotes [^n], not chat prose.
```

**Two-message workflow for Design specs:** MESSAGE 1 = generate; MESSAGE 2 = `<review_mode>` adversarial self-correction (complete revised file, not diff-only for specs). **MESSAGE 3 (isolation specs):** `MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md` — Vulnerability Ledger + remediations. See `CLAUDE_HANDOFF_L7_TEMPORAL_RHYTHM_2026-07-02.md`.

---

## 3. Multi-shot structural pattern

When asking Claude to add a new Iceberg depth layer (or any module matching an existing one), **paste the working reference implementation first** — do not describe the pattern in prose alone.

**Example (Layer 4 from Layer 8 pattern):**

```xml
<existing_implementation_pattern>
[Paste full contents of chaos/canary_metadata_layer.py]
</existing_implementation_pattern>

<instruction>
Using the identical return-type signatures (ok, {"error": CODE, "detail": ...}),
error-handling shape, and gate-side derivation rule ("never trust packet values"),
produce the design spec OR bounded module for Layer 4: behavioral_fingerprint_layer.py.
Cold start MUST degrade to record-only per MMI_METADATA_ICEBERG_2026-07.md §6.
</instruction>
```

Reference layers currently in repo:

| Layer | File | Status |
|-------|------|--------|
| Tip | `chaos/metadata_ingress_gate.py` | Built |
| L8 | `chaos/canary_metadata_layer.py` | Built |
| L6 | `chaos/graph_topology_layer.py` | Built |
| L4 | `chaos/behavioral_fingerprint_layer.py` | Planned |
| L5 | cross-packet correlation | Planned |

---

## 4. Ruthless self-review loop (before commit)

Separate **generation** from **critique**. Never skip the adversarial pass for security-boundary code.

**Takedown prompt (second message or second block):**

```xml
<review_mode>
Act as a hostile purple-team penetration tester reviewing your own prior output.
Identify: hidden security flaws, unhandled exceptions, unicode/byte-length mismatches,
logic gaps, packet-trust violations, and fake-pass paths.
Return a unified git-diff patch fixing those weaknesses only — no prose outside the diff.
</review_mode>
```

Cursor PM / Matt: do not treat Claude output as landed until review pass or explicit `PASS WITH REVISIONS` sign-off.

---

## 5. Operational prompt template (copy-paste)

Fill this blueprint for every Claude task relay:

```xml
<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — systems-domain AGI matrix
Doctrine: Bounded autonomy, deterministic rules over soft prompts, un-fakeable metrics
</system_role>

<current_state_inventory>
Repo root: /mnt/c/MMI
Active task id: [from scripts/next_task.py]
Relevant files:
  - [path]
  - [path]
Active code (if amending):
  [paste block or cite path + line range]
</current_state_inventory>

<task_definition>
[Precisely what to generate or amend — one file or one spec]
Required output path: [mmi/project_brain/... or chaos/...]
</task_definition>

<execution_constraints>
1. Deliver raw code OR raw spec inside a single fenced block — filename as first line comment if code.
2. No conversational filler, summaries, or post-processing text.
3. Every exception explicitly typed; no broad except Exception.
4. Text-handling: enforce true UTF-8 byte counts where volumetric limits apply.
5. MMI hard stops: no unbounded self-modification, no fake pass rates, no scope outside task_definition.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade file payload only. Assumptions go in code comments or spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## 6. Cursor PM handoff wrapper (Matt → Claude)

When routing a Design-lane task, Cursor PM prepends:

```text
PROJECT: MMI
TASK ID: [id]
ASSIGNEE: Claude (Design)
SCORE: [n]
BUILD AUTHORIZATION: [NOT_AUTHORIZED until Matt says authorize build]
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

[Paste filled XML template from §5]
```

---

## 7. Active Claude payload (derived — not a menu)

Current macro winner per `status/MMI_MACRO_BUILD_DECISION_2026-07-03.md`:

| Priority | Payload | Handoff file |
|----------|---------|--------------|
| **NOW** | AGI §5 step 4 — console_server Ed25519 evidence-gate spec | `lanes/CLAUDE_HANDOFF_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_2026-07-03.md` |

Closed (do not re-seed): Proof Gate (AGI step 2), control envelope budget/dead-man (step 3).

---

## 8. Non-goals

* This framework is **not** for Codex (use deployer handoffs + `complete_task.py` closeout).
* Not for ChatGPT/Gemini research lanes (use `MMI_RESEARCH_RIGOR_PROTOCOL.md`).
* Not a substitute for Matt sign-off, completion gate, or `authorize build`.
* Claude must not be asked to skip falsification criteria in `MMI_AGI_EVOLUTION_PATHWAY.md`.

---

## Sign-off

**PASS** — Filed for Claude lane prompt routing. Execute payloads only after Matt seeds task + build auth where implementation is required.
