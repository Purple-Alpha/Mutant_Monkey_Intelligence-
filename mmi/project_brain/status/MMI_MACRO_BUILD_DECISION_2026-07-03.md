# MMI Macro Build Decision Worksheet

**Authority:** Matt (Super)  
**Generated:** 2026-07-03  
**Purpose:** Evidence-backed single next step — not an option menu.  
**Scoring doctrine:** `architecture/MMI_AGI_EVOLUTION_PATHWAY.md` §5 (dependency order) + §6 (non-goals) + `MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md` §6 (evolution blockers).

---

## Current record (verified)

| Metric | Value | Source |
|--------|-------|--------|
| Phase 1 stability | PASS — tiers `[4,4,4]`, spread 0 | `/tmp/mmi_chaos_lab/m2_001/EVIDENCE/phase1_stability_summary.json` |
| Gate B proof gate | BUILT, Codex CLEAN | `status/MMI_PIPE_STAGING.json` |
| Evolution gate | OUTSTANDING (not PERFECT) | Matrix §6 — 48h proof not built |
| AGI §5 steps 1–3 | CLOSED | Pathway §5 + Codex CLEAN |
| `mmi_control_envelope.py` budget/dead-man | **BUILT, Codex CLEAN** | harness T1–T3 CLEAN, pytest 14/14 |

---

## Scoring rubric (macro AGI ladder)

Each candidate scored 0–4 on four axes. **Maximum 16.** A candidate with dependency clearance **< 4** is **INELIGIBLE** regardless of total.

| Axis | Weight | Meaning |
|------|--------|---------|
| **A — Dependency clearance** | Gate | 4 = all prior AGI §5 steps done; 0 = blocked by multiple unbuilt prereqs |
| **B — Safety gate** | Gate | 4 = AGI §6 lists as explicit non-goal without this; 0 = optional |
| **C — Downstream unblock** | Rank | Count of future steps that require this (0–4) |
| **D — Evolution tier lift** | Tiebreak only | 1 if advances matrix evolution tier; 0 if not |

**Selection rule:** Highest score among **eligible** (A = 4) candidates. Tiebreak: lowest AGI §5 step number wins.

---

## Candidate scorecard

| Candidate | AGI §5 step | A Dep | B Safety | C Unblock | D Evolution | Total | Eligible | Verdict |
|-----------|-------------|-------|----------|-----------|-------------|-------|----------|---------|
| **Budget ceiling + dead-man** | **3** | **4** | **4** | **4** | 0 | **16** | **YES** | **WINNER** |
| console_server Ed25519 gate | 4 | 2 | 3 | 2 | 0 | 7 | NO | Blocked — step 3 not built |
| genomic_realignment_loop | 5 | 0 | 4 | 1 | 0 | 5 | NO | Blocked — steps 3–4 not built |
| central_brain Phase 2 synthesis | 6 | 0 | 3 | 0 | 0 | 3 | NO | Blocked — steps 3–5 not built |
| Gate C 15-min soak harness (impl) | — | 1 | 3 | 1 | 0 | 5 | NO | Blocked — unsafe without step 3 |
| M4 48h continuous assault | M4 | 0 | 0 | 0 | 1 | 1 | NO | Blocked — matrix §6 + canary + host boundary |
| Host boundary Go daemon | — | 0 | 2 | 1 | 0 | 3 | NO | Runtime blocker — not AGI §5 next |
| Iceberg L9 provenance spec | micro | 4 | 0 | 0 | 0 | 4 | YES | Parallel micro track — loses macro tiebreak (step 3 = lower step #) |

---

## Derived decision (single output)

```text
NEXT MACRO BUILD: AGI §5 step 4 — console_server.py Ed25519 evidence-gate
LANE NOW: Claude spec (MESSAGE 1 → MESSAGE 2 review)
THEN: Codex plan review → BUILDABLE → Matt authorize build → Cursor implement
```

**Prior step closed:** AGI §5 step 3 — `mmi_control_envelope.py` budget/dead-man — **Codex CLEAN** (2026-07-03).

**Why step 3 beats L9 spec (the only other eligible candidate):**  
Macro AGI §5 step 3 scores 16 vs micro L9 at 4. AGI pathway explicitly states step 3 *"makes 24/7 safe to leave running"* before any self-directed loop, soak harness, or M4. L9 completes ingress depth (micro) but does not satisfy AGI §6 non-goal *"Autonomy without a budget or a kill-switch."*

**Why not Gate C or M4:**  
Gate C implementation scores A=1 (requires step 3 for safe unattended measurement). M4 scores A=0 (48h proof, canary rules, host boundary all unbuilt per matrix §6).

---

## Falsification (what would change this decision)

| If this becomes true | Decision changes to |
|---------------------|---------------------|
| Step 4 spec + build CLOSED + Codex CLEAN | Step 5 — genomic_realignment_loop |
| Phase 1 stability FAIL on re-run | Re-stabilize Phase 1 before any AGI step |
| Gate B regresses on code change | Re-close Gate B before downstream builds |

---

## Operator action (no menu)

1. Relay Codex re-review prompt from `lanes/CODEX_HANDOFF_CONSOLE_SERVER_STEP4_PACKAGE_PLAN_REVIEW_2026-07-03.md`
2. Matt: `authorize build step4 package` when Codex returns BUILDABLE
3. Cursor implements bindings → console → Codex diff review
