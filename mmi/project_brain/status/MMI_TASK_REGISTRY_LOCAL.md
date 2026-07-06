# MMI Local Task Registry

Last updated: 2026-06-28  
Maintained by: Cursor PM  
Authority: Matt (Super)  
References: `tasks.json`, `scripts/keep_task_queue_warm.py`, `scripts/next_task.py`, `MMI_LANE_ROUTING.md`

---

## Purpose

This document defines how local MMI tasks are created, prioritized, assigned, completed, and seeded in the deployer queue at `/mnt/c/MMI/tasks.json`.

---

## Queue Files

| File | Role |
|---|---|
| `tasks.json` | Source of truth for all tasks |
| `scripts/next_task.py` | Prints the next active task (id, score, assignee, instruction) |
| `scripts/keep_task_queue_warm.py` | Seeds a pending task when the queue goes dry |
| `task_runner.py` | Legacy auto-runner — PM tasks should be completed manually with full metadata |

---

## Task Status Values

| Status | Meaning | Surfaced by `next_task.py`? |
|---|---|---|
| `pending` | Active, ready to work | Yes |
| `queued`, `todo`, `in-progress`, `in_progress` | Active variants | Yes |
| `completed`, `done` | Finished | No |
| `paused` | Intentionally held (e.g. non-MMI scope) | No |
| `cancelled`, `canceled`, `skipped` | Abandoned | No |

**Rule:** Only one `pending` task should exist at a time for clarity. Cursor PM seeds the next task immediately after completing the current one.

**Non-MMI tasks** (`phase1-stability-audit`, legacy DAX entries) must stay `paused` or `completed` — never `pending`.

---

## Required Fields — New Pending Task

Every new MMI pending task must include:

| Field | Type | Rule |
|---|---|---|
| `id` | string | Short kebab-case, prefixed `mmi-` (e.g. `mmi-lane-routing-doc`) |
| `instruction` | string | Must start with `PROJECT: MMI.`; include required output path(s) |
| `status` | string | `"pending"` |
| `source` | string | `"Matt directive YYYY-MM-DD"` or local MMI file (e.g. `MMI_NEXT_WORK_PACKET.md`) |
| `created_at` | string | ISO 8601 timestamp |
| `created_by` | string | `"Cursor PM"` or `"scripts/keep_task_queue_warm.py"` |
| `assignee` | string | Lane owner (see Lane Assignment below) |
| `tier` | string | Lane tier label |
| `score` | number | 1–100 priority |
| `score_reason` | string | One sentence explaining priority |

### Example — pending task

```json
{
    "id": "mmi-task-registry-local",
    "instruction": "PROJECT: MMI. Document local task queue conventions... Required output: mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md.",
    "status": "pending",
    "source": "MMI_NEXT_WORK_PACKET.md",
    "created_at": "2026-06-28T11:45:27-07:00",
    "created_by": "Cursor PM",
    "assignee": "Cursor PM",
    "tier": "Project Manager",
    "score": 72,
    "score_reason": "Keeps deployer tasks aligned with lane owners after skeleton and mission brief exist."
}
```

---

## Required Fields — Task Completion

When marking a task `completed`, add:

| Field | Type | Rule |
|---|---|---|
| `completed_at` | string | ISO 8601 timestamp |
| `completed_by` | string | Lane that did the work (e.g. `"Cursor PM"`, `"Codex"`) |
| `result_summary` | string | One–two plain-English sentences |
| `output_files` | array | Every file written or changed for this task |

Change `status` from `"pending"` to `"completed"`.

### Example — completed task

```json
{
    "id": "mmi-mission-brief",
    "status": "completed",
    "completed_at": "2026-06-28T11:45:27-07:00",
    "completed_by": "Cursor PM",
    "result_summary": "Created short mission brief covering operating mission, team lanes, and NEEDS MATT items.",
    "output_files": ["mmi/project_brain/mission/MMI_MISSION_BRIEF.md"]
}
```

---

## Completion Protocol (Cursor PM)

1. Run `python3 scripts/next_task.py` — confirm task id and assignee.
2. If assignee is **not** Cursor PM → route via Matt; do not self-complete.
3. Execute bounded work; write required output file(s).
4. Update `tasks.json`: set `completed`, add completion fields.
5. Seed the next bounded MMI `pending` task **or** run `python3 scripts/keep_task_queue_warm.py`.
6. Verify: `python3 scripts/next_task.py` shows the next MMI-only task with TASK, SCORE, GOES TO, WORK.

**Do not** use `task_runner.py` auto-completion for PM tasks — it skips `completed_by`, `result_summary`, and `output_files`.

---

## Score Bands

| Score | Band | Use for |
|---|---|---|
| 95–100 | Critical | Scope lock, Matt directive, blocking bootstrap |
| 85–94 | High | Deployer health, work packets, queue integrity |
| 75–84 | Medium-high | Routing docs, mission brief, backbone setup |
| 65–74 | Medium | Registry, status reports, planning increments |
| 50–64 | Low | Nice-to-have docs, cleanup |
| 1–49 | Deferred | Blocked or low-urgency until Matt unblocks |

Score does **not** affect `next_task.py` selection order — it picks the **first** active-status task in array order. Cursor PM must place the intended next task last among active entries, or ensure only one pending task exists.

---

## Lane Assignment Rules

| Assignee | Tier | Task types |
|---|---|---|
| Cursor PM | Project Manager | Scope docs, routing, registry, work packets, queue updates, status reports |
| Codex | Backbone / runtime support | Scripts, deployer plumbing, folder skeleton, diagnostics, runtime fixes |
| Claude | Design | Architecture docs, contracts, design specs |
| Gemini Paid API | Audit | Audit passes, completion gate |
| Gemini | Main research | Primary research lanes |
| ChatGPT | Deep / secondary research | Secondary research, deep dives |
| Matt | Super | Product direction, build auth, GATED, lane reactivation |

**Instruction prefix:** all MMI tasks start with `PROJECT: MMI.`

**Id prefix:** all MMI task ids start with `mmi-` (fallback warmer uses `phase1-next-safe-increment-*` id but instruction is still MMI-only — legacy naming only).

See `MMI_LANE_ROUTING.md` for full routing decision tree.

---

## Queue Seeding — `keep_task_queue_warm.py`

Behavior:

1. If any active-status task exists → no change (`"reason": "active task exists"`).
2. If queue is dry → seed next item from fixed `BACKLOG` (ids not already in `tasks.json`).
3. If backlog exhausted and no unfinished tasks → seed fallback planning task (`MMI_NEXT_SAFE_TASK.md`).

### Fixed backlog (historical seeds)

| id | score | assignee |
|---|---|---|
| `mmi-active-scope-lock` | 100 | Cursor PM |
| `mmi-queue-deployer-check` | 92 | Cursor PM |
| `mmi-next-work-packet` | 85 | Cursor PM |

These are one-time bootstrap seeds. After all three exist in `tasks.json`, backlog is exhausted.

### Fallback seed (queue fully done)

```
id: phase1-next-safe-increment-<timestamp>   # legacy id prefix; content is MMI-only
score: 75
assignee: Cursor PM
output: mmi/project_brain/status/MMI_NEXT_SAFE_TASK.md
```

**Preferred:** Cursor PM manually seeds the next bounded task instead of relying on fallback.

---

## `next_task.py` Output Format

```
TASK: <id>
SCORE: <score>
GOES TO: <assignee> (<tier>)
WORK: <instruction>
```

Health check after every completion: all four lines present; task is MMI-only; assignee matches lane owner.

---

## Completed Bootstrap Registry (local)

| id | score | assignee | completed_by | output |
|---|---|---|---|---|
| `mmi-active-scope-lock` | 100 | Cursor PM | Cursor PM | `MMI_ACTIVE_SCOPE.md` |
| `mmi-queue-deployer-check` | 92 | Cursor PM | Cursor PM | `MMI_DEPLOYER_QUEUE_CHECK.md` |
| `mmi-next-work-packet` | 85 | Cursor PM | Cursor PM | `MMI_NEXT_WORK_PACKET.md` |
| `mmi-lane-routing-doc` | 78 | Cursor PM | Cursor PM | `MMI_LANE_ROUTING.md` |
| `mmi-project-brain-skeleton` | 76 | Codex | Codex | `project_brain/README.md` + folder READMEs |
| `mmi-mission-brief` | 82 | Cursor PM | Cursor PM | `MMI_MISSION_BRIEF.md` |
| `mmi-task-registry-local` | 72 | Cursor PM | Cursor PM | this file |

### Paused (do not reactivate)

| id | status | reason |
|---|---|---|
| `phase1-stability-audit` | paused | MMI-only scope; Social Architect Phase 1 |

---

## Rules for Creating New Tasks

1. **Bounded** — one clear output, completable in one lane pass.
2. **MMI-only** — instruction starts with `PROJECT: MMI.`; no Phase 1/DAX/Trades.
3. **Routed** — assignee matches work type; PM does not queue Codex work to itself.
4. **Scored** — include `score` and `score_reason`.
5. **Sourced** — cite Matt directive or local MMI file.
6. **No vague giants** — split large work into sequenced tasks.

---

## Anti-Patterns

| Do not | Why |
|---|---|
| Seed non-MMI pending tasks | Breaks scope lock |
| Set `phase1-stability-audit` to pending | Reactivates Phase 1 |
| Let queue go dry without seeding | Deployer has nothing to show |
| PM completes Codex-assigned tasks | Lane violation |
| Auto-complete via `task_runner.py` | Missing completion metadata |
| Invent product scope in task instructions | Requires Matt (Super) |

---

## Quick Reference

```
New task needed
  → MMI only? assignee? score? required output?
  → Append to tasks.json as pending
  → Verify next_task.py

Task done
  → completed + completed_at + completed_by + result_summary + output_files
  → Seed next pending OR keep_task_queue_warm.py
  → Verify next_task.py
```
