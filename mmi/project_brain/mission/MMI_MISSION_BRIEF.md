# MMI Mission Brief

Last updated: 2026-06-28  
Prepared by: Cursor PM  
Authority: Matt (Super)  
Sources: local `mmi/project_brain/` status files and Matt directives only

---

## What MMI Is (locally known)

**MMI is the sole active project.** All current work, task queue entries, and agent routing are scoped to MMI only inside `/mnt/c/MMI/mmi`.

**NEEDS MATT:** Product definition — what MMI builds, for whom, and the long-term outcome. This brief does not infer product scope from NorthStar or other repos.

---

## Current Phase

**PM bootstrap — COMPLETE.** Queue is on hold awaiting Matt phase-2 directive.

| Done | Output |
|---|---|
| Scope lock | `status/MMI_ACTIVE_SCOPE.md` |
| Deployer check | `status/MMI_DEPLOYER_QUEUE_CHECK.md` |
| Work packet | `status/MMI_NEXT_WORK_PACKET.md` |
| Lane routing | `status/MMI_LANE_ROUTING.md` |
| Project-brain skeleton | `project_brain/README.md` + folder READMEs |
| Mission brief | this file |
| Task registry | `status/MMI_TASK_REGISTRY_LOCAL.md` |
| Bootstrap closeout | `status/MMI_BOOTSTRAP_CLOSEOUT.md` |
| Queue hold | `status/MMI_NEXT_SAFE_TASK.md` |

**NEEDS MATT:** Product definition and first substantive MMI build target.

---

## Operating Mission (now)

Keep MMI work **bounded, routed, and queue-driven**:

1. **Scope locked** — MMI only; no Social Architect Phase 1, DAX, or Trades unless Matt reactivates.
2. **Queue healthy** — `tasks.json` shows one clear next task with id, score, and assignee.
3. **Lanes respected** — each task goes to the correct owner; Cursor PM routes, not absorbs every lane.
4. **Local brain grounded** — mission, architecture, lanes, and status live under `mmi/project_brain/` from Matt-approved sources.

---

## Team

| Role | Owner | Responsibility |
|---|---|---|
| Super | Matt | Final authority, build auth, GATED, scope changes |
| PM | Cursor | Task queue, routing, scope hygiene |
| Backbone | Codex | Scripts, deployer, repo plumbing, runtime |
| Design | Claude | Contracts, architecture docs, design specs |
| Audit | Gemini Paid API | Audit passes, completion gate |
| Research | Gemini | Main research lanes |
| Deep research | ChatGPT | Secondary / deep research |

---

## In Scope (current)

- MMI project-brain docs under `/mnt/c/MMI/mmi`
- Deployer queue files (`tasks.json`, `scripts/next_task.py`, `keep_task_queue_warm.py`) when a task requires it
- Bounded PM tasks: scope, routing, registry, status reports
- Routing backbone/design/research/audit work to the correct lane via Matt

## Out of Scope (hard stops)

- Social Architect Phase 1 (paused)
- DAX / Trades (paused unless Matt reactivates)
- Non-MMI tasks in `tasks.json`
- Copying NorthStar content without Matt authorization
- Product decisions, feature invention, or deploy/spend without Matt approval

---

## Success Looks Like (bootstrap phase)

- [x] Active scope documented and locked
- [x] Deployer emits MMI-only tasks
- [x] Lane routing rules exist locally
- [x] Project-brain folder skeleton exists
- [x] Mission brief exists (this file)
- [x] Local task registry documented
- [ ] Matt defines product mission and first build target

---

## Open Questions for Matt

1. **Product mission** — What is MMI in one sentence for external stakeholders?
2. **NorthStar relationship** — Does local `mmi/` stay thin, or sync from northstar `mmi/`?
3. **First build target** — What is the next smallest verified MMI build after PM bootstrap?
4. **task_runner.py** — Keep auto-run off for PM tasks? (Recommended: manual PM completion only.)

---

## Document Index (local)

| File | Purpose |
|---|---|
| `status/MMI_ACTIVE_SCOPE.md` | Scope lock and hard stops |
| `status/MMI_LANE_ROUTING.md` | Who owns what; routing rules |
| `status/MMI_DEPLOYER_QUEUE_CHECK.md` | Deployer verification |
| `status/MMI_NEXT_WORK_PACKET.md` | Planned next bounded tasks |
| `status/MMI_TASK_REGISTRY_LOCAL.md` | Task queue conventions |
| `status/MMI_BOOTSTRAP_CLOSEOUT.md` | Bootstrap closeout |
| `status/MMI_NEXT_SAFE_TASK.md` | Queue hold status |
| `mission/MMI_MISSION_BRIEF.md` | This brief |
