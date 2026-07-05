# MMI ChatGPT Adversarial Research Prompt Framework

**Status:** CANONICAL — RESEARCH DOCTRINE — prompt routing for ChatGPT research lane only  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-03  
**Maintained by:** Cursor PM (handoff packaging)  
**Purpose:** Force ruthless adversarial critique of research findings before spec lane — not validation theater.

> **DO NOT LOSE THIS FILE.** Every ChatGPT research **review pass** (post-findings or post-ZIP) MUST append this framework after the research packet or pasted findings. Cursor agents: read this before packaging any ChatGPT research payload. Never ship findings to spec lane without at least one adversarial pass using this template.

**Related:**

* `lanes/CHATGPT_MMI_LANE_INTEGRATION_2026-07-03.md` — lane map + ZIP upload workflow
* `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — external stats / Crucible (complementary)
* `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` — Claude spec lane (downstream)
* `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` — v2.1 example incorporating adversarial output

> **Rule:** This file does not grant spec, build, or GATED authority. Matt `authorize spec` still required after findings + adversarial revision accepted.

---

## 0. When to use

| Pass | Tool | Prompt |
|------|------|--------|
| **Pass 1 — Ground findings** | ChatGPT + ZIP | `CHATGPT_MMI_LANE_INTEGRATION_2026-07-03.md` § prompt template |
| **Pass 2 — Adversarial critique** | ChatGPT | **This file — SINGLE PASTE below** |
| **Pass 3 — File revision** | Cursor | Incorporate accepted critique into `RESEARCH_*_FINDINGS_*.md` |

Run Pass 2 on **every** research findings doc before `authorize spec`.

---

## 1. SINGLE PASTE — Adversarial research review (copy all)

Replace `{TASK_ID}`, `{FINDINGS_FILENAME}`, and paste the full findings body at the bottom.

```
PROJECT: MMI
TASK: {TASK_ID}-adversarial-review
LANE: Research critique only — NOT spec, NOT build, NOT GATED
AUTHORITY REPO: C:\Architectapp_clean

ROLE:
Act as a cynical, top-tier Distributed Systems Architect and Red Team Auditor.

Your task is to ruthlessly critique the provided "{FINDINGS_FILENAME}" document. Play devil's advocate. Challenge the assumption that this proposed approach is the "only way" or the "best way" forward.

Analyze the document and answer the following questions with zero fluff:

1. ALTERNATIVE PATHS
Is there a simpler, safer, or more efficient way to achieve the stated proof tier without the most complex proposed mechanism (e.g. long-duration un-throttled chaos assault)?
Can the goal be achieved via formal verification, aggressive deterministic fuzzing, or modular sandboxing instead?
Is the proposed duration/endurance test a final ceremony or a reckless first milestone?

2. HIDDEN COUPLING
Where does the document leave dependency ambiguity (parallel vs sequential tracks)?
What are the architectural risks of parallel proof vs sequential proof?
Is the current dependency structure optimal, or is it a bottleneck?
Propose typed gates if missing (e.g. REQUIRED_FOR_DRY_RUN / REQUIRED_FOR_ENDURANCE / REQUIRED_FOR_FINAL_CLAIM).

3. CANARY BLIND SPOTS
Review any draft closed enum of alert/canary rules.
What critical evasion tactics or host escape vectors are completely missed?
How would an attacker bypass the boundary without triggering the listed telemetry flags?
Cover: host escape, repo integrity without direct writes, evidence tampering, budget attribution games, slow-path exfiltration.

4. CLOCK HONESTY FLUSH
Address any open policy on failure reset (full clock vs scoped window).
What are the mathematical and statistical risks of scoped-window reset allowing multi-hour exploit chains to slip through?
Does scoped reset create survivorship laundering or classification incentives?

5. COMPLIANCE & SAFETY RATING
Rate readiness on a 0–10 scale for jumping to the most demanding proof step.
Based strictly on documented facts (what is unbuilt, unfiled, unresolved), is the top-tier proof realistic now?
What interim milestones are missing (e.g. dry-run loops, fuzz harness, invariant suite)?

CRITICAL CONSTRAINTS:
- Adopt a critical, analytical tone. Do not validate the plan unless it survives your absolute worst-case architectural counter-arguments.
- Focus strictly on structural flaws, blind spots, and missing variables in the provided text.
- Do NOT authorize spec, build, or gate closure.
- Do NOT claim PERFECT or final tier achieved.
- Cite exact repo paths from the findings or attached ZIP when grounding counter-arguments.
- Mark anything you cannot verify from supplied text as [UNVERIFIED].

OUTPUT FORMAT:
- Use numbered sections matching questions 1–5.
- End with: BOTTOM LINE (3–5 bullets) + RECOMMENDED FINDINGS REVISIONS (concrete edits to the research doc, not a spec).

---

[PASTE ENTIRE FINDINGS DOCUMENT BELOW THIS LINE]

```

---

## 2. M4 instance (filled example — 2026-07-03)

Use when reviewing `RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` without retyping placeholders:

```
PROJECT: MMI
TASK: mmi-m4-evolution-gate-research-v2-adversarial-review
LANE: Research critique only — NOT spec, NOT build, NOT GATED
AUTHORITY REPO: C:\Architectapp_clean

ROLE:
Act as a cynical, top-tier Distributed Systems Architect and Red Team Auditor.

Your task is to ruthlessly critique the provided "RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07" document. Play devil's advocate. Challenge the assumption that this proposed approach is the "only way" or the "best way" forward.

Analyze the document and answer the following questions with zero fluff:

1. ALTERNATIVE PATHS
Is there a simpler, safer, or more efficient way to achieve the "PERFECT-tier evolution proof" without spinning up a complex, 48-hour un-throttled automated chaos clone assault runner?
Can this be achieved via formal verification, aggressive deterministic fuzzing, or modular sandboxing instead?

2. HIDDEN COUPLING
The document notes that the repo doesn't resolve whether M3 mesh inflation is a hard prerequisite or a parallel track to M4.
Logically, what are the architectural risks of running M4 in parallel vs. sequentially?
Is the current dependency structure optimal, or is it a bottleneck?

3. CANARY BLIND SPOTS
Review the draft Closed Enum for M4-CANARY-001 through 006.
What critical evasion tactics or host escape vectors are completely missed by these 6 rules?
How would an attacker bypass this boundary without triggering these specific telemetry flags?

4. CLOCK HONESTY FLUSH
Address the open spec decision regarding "clock-reset honesty" (whether a failure resets the full 48h clock or just a scoped window).
What are the mathematical and statistical risks of a "scoped window" reset policy allowing subtle, multi-hour exploit chains to slip through undetected?

5. COMPLIANCE & SAFETY RATING
Rate the current "OUTSTANDING" posture.
Based strictly on the facts that the host boundary is unbuilt, canary rules are unfiled, and the harness is unbuilt, is a 48-hour continuous assault realistic, or is the team missing a critical interim milestone (like a Gate C dry-run loop)?

CRITICAL CONSTRAINTS:
- Adopt a critical, analytical tone. Do not validate my current plan unless it survives your absolute worst-case architectural counter-arguments.
- Focus strictly on structural flaws, blind spots, and missing variables in the provided text.
- Do NOT authorize spec, build, or gate closure.
- Do NOT claim PERFECT or M4 closed.

OUTPUT FORMAT:
Numbered sections 1–5 + BOTTOM LINE + RECOMMENDED FINDINGS REVISIONS.

---

[PASTE ENTIRE "RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07" TEXT HERE]
```

**Note:** M4 findings v2.1 already incorporates the 2026-07-03 adversarial read (staged ladder, typed M3 gates, canary blind spots, full clock reset, 2/10 readiness). Re-run this prompt after the next findings revision or when validating a new research lane.

---

## 3. Workflow with ZIP + adversarial pass

```text
Matt: authorize research {topic}
        ↓
Cursor: RESEARCH brief + ZIP packet
        ↓
ChatGPT Pass 1: ZIP attached → draft FINDINGS markdown
        ↓
Matt: paste findings (or attach findings .md)
        ↓
ChatGPT Pass 2: SINGLE PASTE from §1 or §2 (adversarial framework)
        ↓
Matt: paste adversarial output → Cursor
        ↓
Cursor: revise FINDINGS (e.g. v2.1) — research filing only
        ↓
Matt: authorize spec {topic} → Claude
```

---

## 4. What not to do

- Do not skip Pass 2 because Pass 1 "looks complete"
- Do not ask ChatGPT to implement code or write Claude specs in this prompt
- Do not treat adversarial output as spec — it feeds findings revision only
- Do not remove `[UNVERIFIED]` in Pass 2 unless source text was read from ZIP or pasted findings

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | Canonical adversarial research prompt — paired with M4 v2.1 critique |
