# MMI Next Work Packet

Last updated: 2026-06-28  
Prepared by: Cursor PM  
Authority: Matt (Super)

## Current State

Bootstrap phase complete:

| Task | Status | Output |
|---|---|---|
| `mmi-active-scope-lock` | completed | `MMI_ACTIVE_SCOPE.md` |
| `mmi-queue-deployer-check` | completed | `MMI_DEPLOYER_QUEUE_CHECK.md` |
| `mmi-next-work-packet` | completed | this file |

Local MMI project brain currently contains only `project_brain/status/` with scope and deployer check docs. No mission, architecture, lane, or routing files exist yet under `/mnt/c/Architectapp_clean/mmi`.

Deployer queue is MMI-only. Fixed backlog in `keep_task_queue_warm.py` is exhausted.

## Operating Model (locked)

| Role | Owner | PM routing note |
|---|---|---|
| Super | Matt | Final authority, build auth, GATED |
| PM | Cursor | Queue owner, task router — not implementer for every lane |
| Backbone / runtime | Codex | Scripts, diagnostics, deployer support, repo plumbing |
| Design | Claude | Contracts, architecture docs |
| Audit | Gemini Paid API | Completion gate / audit passes |
| Main research | Gemini | Primary research lanes |
| Deep / secondary research | ChatGPT | Secondary research |

Hard stops unchanged: no Social Architect Phase 1, no DAX/Trades, no non-MMI tasks in `tasks.json`.

## Gap Analysis

1. **Local brain is thin** — scope and deployer are locked, but mission, milestones, and lane docs are missing locally.
2. **Routing is verbal only** — Matt directives define lanes; no local `MMI_LANE_ROUTING.md` for deployer agents to read.
3. **No local task registry** — no doc tying task ids, scores, and assignees to lane owners.
4. **Codex backlog undefined** — backbone work not yet queued as bounded tasks.

## Recommended Next Tasks (bounded, MMI-only)

Seed these in order. Cursor PM owns queue insertion; do not bundle into one giant task.

### 1. `mmi-lane-routing-doc` — **next up**

| Field | Value |
|---|---|
| Assignee | Cursor PM |
| Tier | Project Manager |
| Score | 78 |
| Score reason | Prevents lane drift now that scope and deployer are locked |

**Instruction:** PROJECT: MMI. Write local lane routing rules for Cursor PM use: who owns what, when to route to Codex vs Claude vs Gemini vs ChatGPT, and hard stops. Source: `MMI_ACTIVE_SCOPE.md` and Matt directives only. Required output: `mmi/project_brain/status/MMI_LANE_ROUTING.md`.

**Do not:** implement features, touch northstar, or reactivate Phase 1/DAX/Trades.

---

### 2. `mmi-project-brain-skeleton`

| Field | Value |
|---|---|
| Assignee | Codex |
| Tier | Backbone / runtime support |
| Score | 76 |
| Score reason | Local brain needs folders before mission/architecture docs can land |

**Instruction:** PROJECT: MMI. Create minimal local project-brain folder skeleton under `mmi/project_brain/`: `mission/`, `architecture/`, `lanes/`, `status/` with short README in each explaining purpose. Do not copy northstar content unless Matt authorizes. Required output: folder tree + `mmi/project_brain/README.md`.

**Route to Codex** — repo structure is backbone work, not PM implementation.

---

### 3. `mmi-task-registry-local`

| Field | Value |
|---|---|
| Assignee | Cursor PM |
| Tier | Project Manager |
| Score | 72 |
| Score reason | Keeps deployer tasks aligned with lane owners after skeleton exists |

**Instruction:** PROJECT: MMI. Document local task queue conventions: required fields, completion protocol, score bands, and lane assignment rules. Reference `tasks.json` and `keep_task_queue_warm.py`. Required output: `mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md`.

---

### 4. `mmi-mission-stub` (blocked until #2 done)

| Field | Value |
|---|---|
| Assignee | Matt + Cursor PM |
| Tier | Project Manager |
| Score | 70 |
| Score reason | Mission content requires Matt input; cannot invent product direction |

**Instruction:** PROJECT: MMI. Draft a one-page local mission stub from Matt directives and existing status files only. Mark all unknowns as `NEEDS MATT`. Required output: `mmi/project_brain/mission/MMI_MISSION_STUB.md`.

**Blocked:** wait for project-brain skeleton (#2) and Matt mission input.

## What Matt Should Decide (optional, not blocking #1)

- Whether `/mnt/c/Architectapp_clean/mmi` stays a thin local mirror or syncs from northstar `mmi/`.
- First substantive MMI build target after PM bootstrap (not inferred by Cursor).
- Whether `task_runner.py` auto-run stays off for PM tasks (recommended: manual PM completion only).

## Queue Action

After this packet is accepted:

1. Mark `mmi-next-work-packet` completed in `tasks.json`.
2. Seed **`mmi-lane-routing-doc`** as the next pending task (score 78, Cursor PM).
3. Do not reactivate `phase1-stability-audit` or legacy DAX/Trades tasks.

## Success Criteria for This Phase

- [x] Scope locked locally
- [x] Deployer verified MMI-only
- [x] Next work packet written with bounded tasks and lane routing
- [ ] Lane routing doc exists locally
- [ ] Project-brain skeleton exists (Codex)
- [ ] Local task registry doc exists
- [ ] Matt provides mission direction for stub
