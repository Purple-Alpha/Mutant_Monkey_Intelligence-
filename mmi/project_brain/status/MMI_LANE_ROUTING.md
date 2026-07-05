# MMI Lane Routing

Last updated: 2026-07-01  
Authority: Matt (Super)  
Maintained by: Cursor PM  
Source: `MMI_ACTIVE_SCOPE.md` and Matt directives 2026-06-28

## Purpose

This file tells Cursor PM **who owns what** and **when to route work** to another lane. Cursor PM owns the queue — it does not implement every task itself.

**New agent sessions:** start with `mmi/project_brain/lanes/MMI_AI_LANE_SCOPE_2026-07-03.md` (canonical lane map + build loop + filing rules).

If this file conflicts with `MMI_ACTIVE_SCOPE.md`, follow `MMI_ACTIVE_SCOPE.md` and ask Matt.

---

## Lane Owners

| Lane | Owner | Owns |
|---|---|---|
| Super | Matt | Final authority, scope changes, build authorization, GATED decisions, reactivating paused lanes |
| PM | Cursor | Task queue, scope hygiene, routing, `tasks.json` updates, deployer pipe health |
| Backbone / runtime | Codex | Scripts, diagnostics, deployer support, repo plumbing, folder structure, runtime fixes |
| Design | Claude | Architecture docs, contracts, design specs, interface definitions |
| Audit | Gemini Paid API | Audit passes, completion gate, verification against requirements |
| Main research | Gemini | Primary research lanes, competitive intel, first-pass investigation |
| Deep / secondary research | ChatGPT | Secondary research, deep dives, cross-check of Gemini findings |

---

## Cursor PM — Default Behavior

Cursor PM **always**:

- Runs `python3 scripts/next_task.py` to read the active task
- Completes PM-owned tasks (scope, queue, routing docs)
- Updates `tasks.json` on completion with `completed_at`, `completed_by`, `result_summary`, `output_files`
- Seeds the next bounded MMI pending task or runs `keep_task_queue_warm.py`
- Keeps work inside `/mnt/c/Architectapp_clean/mmi` unless a task explicitly requires deployer files

Cursor PM **does not** (unless Matt explicitly assigns that lane for a specific task):

- Act as auditor (Gemini Paid API lane)
- Act as researcher (Gemini or ChatGPT lane)
- Act as designer (Claude lane)
- Act as backbone implementer for Codex-scoped repo work
- Act as Super (product direction, GATED, build auth)
- Deploy, call external services, scrape, spend money, or contact people

**Rule:** If the task assignee is not Cursor PM, Cursor PM **routes and monitors** — it does **not** perform the assigned lane's work unless Matt explicitly reroutes the task.

**Hard rule (2026-07-01):** Seeded/pending status is **not** build authorization. Backbone tasks (e.g. P1 closeout gate) remain **blocked for implementation** until Matt gives explicit build auth.

| If assignee is… | Cursor PM does… | Cursor PM does NOT… |
|-----------------|-----------------|---------------------|
| Cursor PM | Execute bounded PM work + queue hygiene | Absorb Codex/Claude/research lanes |
| Codex | Handoff, queue state, status, closeout after review | Implement scripts by default |
| Claude | Handoff, monitor | Write design specs by default |
| Matt | Hold queue, document `NEEDS MATT` | Decide product direction |
| Gemini / ChatGPT / Gemini Paid | Handoff per task | Run research or audit by default |

---

## Routing Decision Tree

Use this order when a new task or request arrives:

### 1. Is it MMI-only?

| Answer | Action |
|---|---|
| No (Phase 1, DAX, Trades, other project) | **STOP.** Do not queue. Keep existing non-MMI tasks paused/completed. Ask Matt if scope changed. |
| Yes | Continue |

### 2. Who is the assignee in `tasks.json`?

| Assignee | Action |
|---|---|
| Cursor PM | Cursor PM executes (if bounded PM work) or breaks into smaller routed subtasks |
| Codex | Route to Codex — scripts, repo structure, diagnostics, deployer plumbing |
| Claude | Route to Claude — design, contracts, architecture docs |
| Gemini Paid API | Route to Gemini Paid API — audit / gate |
| Gemini | Route to Gemini — main research |
| ChatGPT | Route to ChatGPT — deep/secondary research |
| Matt | Hold for Matt decision — mark blocked or `NEEDS MATT` |

### 3. What kind of work is it?

| Work type | Route to | Examples |
|---|---|---|
| Queue / scope / routing docs | Cursor PM | `tasks.json`, `MMI_*` status files, work packets |
| Scripts, deployer, folder skeleton, runtime | Codex | `next_task.py`, `keep_task_queue_warm.py`, `mmi/project_brain/` structure |
| Design specs, contracts, architecture | Claude | Build scopes, interface contracts, purple-layer docs |
| Pass/fail audit, gate checks | Gemini Paid API | Completion gate, requirement verification |
| First research pass, lane surveys | Gemini | Competitive intel, threat research, intake classification |
| Deep dive, second opinion, long-form research | ChatGPT | Cross-check Gemini, historical intake, deep analysis |
| Product direction, build auth, lane reactivation | Matt | Mission content, GATED, scope expansion |

---

## When to Route vs When PM Does It

| Situation | Cursor PM | Route elsewhere |
|---|---|---|
| Write routing/scope/status doc | Yes | — |
| Update `tasks.json` completion | Yes | — |
| Create `mmi/project_brain/` folder tree | No | Codex |
| Fix `scripts/next_task.py` | No | Codex |
| Draft architecture contract | No | Claude |
| Run audit gate | No | Gemini Paid API |
| Research a threat model | No | Gemini (main), ChatGPT (deep) |
| Decide next MMI product feature | No | Matt |
| Invent mission without Matt input | **Never** | Mark `NEEDS MATT` |

---

## Hard Stops

These apply to **every lane**, including Cursor PM:

1. **MMI only** — no active work on Social Architect Phase 1, DAX, or Trades.
2. **No lane reactivation** — DAX/Trades/Phase 1 stay paused until Matt explicitly reactivates.
3. **No non-MMI seeds** — do not add non-MMI tasks to `tasks.json`.
4. **No rogue hats** — Cursor PM does not absorb auditor, researcher, designer, or backbone work by default.
5. **No product decisions** — PM does not decide mission, features, or build targets beyond the current bounded task.
6. **No external spend or deploy** — unless Matt explicitly approves for that task.
7. **No overwriting** — read user/Codex changes before editing shared files.
8. **Conflicting docs** — if old role docs conflict with `MMI_ACTIVE_SCOPE.md`, treat scope file as current.

---

## Task Queue Conventions (PM)

Every new pending task in `tasks.json` must include:

- `id` — short MMI task id (e.g. `mmi-lane-routing-doc`)
- `instruction` — starts with `PROJECT: MMI.`
- `status` — `pending`
- `source` — Matt directive or local MMI file
- `created_at`, `created_by`, `assignee`, `tier`, `score`, `score_reason`

On completion, add: `completed_at`, `completed_by`, `result_summary`, `output_files`.

After completion: verify `python3 scripts/next_task.py` shows the next MMI-only task.

---

## Handoff Format (PM → Other Lane)

When routing to Codex, Claude, Gemini, or ChatGPT, Cursor PM gives Matt a copy-paste handoff:

```
PROJECT: MMI
TASK ID: <id>
ASSIGNEE: <lane owner>
SCORE: <n>
WORK: <instruction>
REQUIRED OUTPUT: <path(s)>
HARD STOPS: MMI only; no Phase 1/DAX/Trades; no scope expansion
```

**Claude (Design lane):** Also attach `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` — use XML-wrapped template (§5), multi-shot pattern (§3), and no-explanations directive (§2) for code/spec generation tasks.

Matt relays to the target lane. Cursor PM does not impersonate other lanes.

---

## Active task routing — Claude L4 spec (2026-07-02)

| Field | Value |
|-------|--------|
| **Task id** | `mmi-iceberg-l4-behavioral-fingerprint-spec` |
| **Assignee** | **Claude** (Design) |
| **Build auth** | **NOT_AUTHORIZED** — spec only |
| **Handoff** | `lanes/CLAUDE_HANDOFF_L4_BEHAVIORAL_FINGERPRINT_2026-07-02.md` |
| **Phase 1** | **PASS** (recorded) |

Matt → Claude: paste XML block from handoff file. Cursor PM closeout when spec lands.

**Codex:** idle until Matt authorizes L4 implementation after spec review.

---

## Archived — P1 closeout gate routing (2026-07-01, complete)

| Field | Value |
|-------|--------|
| **Task id** | `mmi-quality-slice-p1-closeout-gate` |
| **Status** | **COMPLETE** (P1–P8 quality ladder done) |

<details>
<summary>Original P1 handoff (historical)</summary>

PROJECT: MMI
TASK ID: mmi-quality-slice-p1-closeout-gate
ASSIGNEE: Codex
LANE: Backbone / runtime support
SCORE: 88
BUILD AUTHORIZATION: [Matt fills when authorizing]
WORK: Implement Slice P1 only per MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md §13 Slice 1.
      Extend complete_task.py — mandatory H1 for artifact tiers; block on missing outputs.
      Optional --verify-json artifact path. Do not implement P2/P3/L3-05.
REQUIRED OUTPUT: scripts/complete_task.py (+ tests/verification notes as appropriate)
HARD STOPS: MMI only; local-first; no Level 3; no OPSEC-4/5/9 changes; no scope expansion
```

</details>

---

## Current queue snapshot (2026-07-01)

| Field | Value |
|-------|--------|
| **Active** | `mmi-weapon-phase1-stability-harness` → Codex (pending build auth) |
| **Quality ladder** | P1–P8 **COMPLETE** |
| **P9 / L3** | **HOLD** |
| **Latest B2 mirror** | `mmi_backup_20260701_110548.tar.gz` |
| **Restore-proven / latest-good** | `mmi_backup_20260701_110548.tar.gz` |

---

## Archived — initial seed order (2026-06-28)

After lane routing doc was first written, seed order was:

| # | Task id | Assignee | Score |
|---|---|---|---|
| 1 | `mmi-project-brain-skeleton` | Codex | 76 |
| 2 | `mmi-task-registry-local` | Cursor PM | 72 |
| 3 | `mmi-mission-stub` | Matt + Cursor PM | 70 (blocked) |

---

## Quick Reference

```
Request arrives
    → MMI only? ──no──→ STOP (ask Matt)
         │
        yes
         → Check assignee + work type
         → PM task? ──yes──→ Cursor PM executes + updates queue
         → Else ──→ Hand off to lane owner via Matt; do not self-implement
```
