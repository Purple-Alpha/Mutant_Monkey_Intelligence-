# MMI War Room Spec

Last updated: 2026-06-29  
Authority: Matt (Super)  
Prepared by: Cursor PM  
Source: Matt directive — finish war room as MMI grows beyond bootstrap

---

## What the war room is (MMI local-first)

The **war room** is Matt’s **local operations dashboard** for running MMI on the Mini PC:

- **Monitor 1 (execute):** Cursor Editor — edits, terminal, `tasks.json`, scripts
- **Monitor 2 (war room):** Cursor Agents + local war room CLI in watch mode — pipe, lanes, backup, brain links

This is **not** NorthStar governance, **not** a hosted web app, **not** LangGraph/automation substrate. It is the evolution of `mmi/command_center.py` into a fuller operator panel.

---

## What exists today (Phase-2)

| Piece | Status |
|-------|--------|
| `mmi/command_center.py` | Done — pipe, task, next action, brain links |
| Auto-seed pipeline | Done — `mmi/task_pipeline.json` |
| Cold backup + B2 push | Done — `--backup-and-push` |
| War room unified panel | **Not done** |
| Dual-monitor setup doc | **This spec + `status/MMI_WAR_ROOM_SETUP.md`** |

---

## War room v1 outcome

One local command answers: **“What is happening across MMI right now?”**

```bash
python mmi/war_room.py
python mmi/war_room.py --watch --seconds 30
```

### Display sections (v1)

| Section | Source |
|---------|--------|
| **PIPE** | `tasks.json` + pipe detect (LOADED/HOLD/BLOCKED/DRY) |
| **ACTIVE TASK** | id, score, assignee, tier, instruction |
| **LANE MAP** | `MMI_LANE_ROUTING.md` summary (fixed table) |
| **BACKUP** | Last entry from `MMI_BACKUP_PUSH_LOG.json` |
| **OPERATOR** | Cheatsheet: reload, complete_task, backup-and-push |
| **PROJECT BRAIN** | Links to scope, policy, phase start, routing |

### Flags

| Flag | Behavior |
|------|----------|
| default | Full war room text panel once |
| `--json` | Machine-readable state |
| `--watch --seconds N` | Refresh panel (min 5s) — for monitor 2 |
| `--no-seed` | Skip auto-seed (read-only view) |

---

## What war room is not

- Not `web/` or npm UI
- Not `ops/run.py` Social Architect operator
- Not NorthStar `mmi_dispatch` or completion gate UI
- Not multi-agent orchestration (no auto-routing to agents)
- Not a cloud runtime

Agents on monitor 2 are **human-steered** via Cursor Agents tabs; war room CLI is **read-only state**.

---

## Implementation

| File | Owner | Notes |
|------|-------|-------|
| `mmi/war_room.py` | Codex | Can import shared logic from `command_center.py` or extract `mmi/pipe_state.py` |
| `status/MMI_WAR_ROOM_SETUP.md` | Cursor PM | Dual-monitor + agent tab roles |

Reuse:

- `detect_pipe_status`, `next_action_for`, `build_state` patterns from command center
- Add `backup_status()` reading push log tail
- Add `lane_map()` static from `MMI_ACTIVE_SCOPE.md` roles

Keep read-only — no mutation of `tasks.json` from war room (auto-seed optional via same pattern as command center).

---

## Dual-monitor operating model

| Monitor | Tool | Role |
|---------|------|------|
| 1 | Cursor Editor on `Architectapp_clean` | Execute — code, git, scripts |
| 2 | Cursor Agents + `war_room.py --watch` | Orient — pipe, lanes, backup, next action |

Agent tabs on monitor 2 (fixed roles):

| Tab | Owner | Does |
|-----|-------|------|
| PM | Cursor | Queue, routing, status |
| Backbone | Codex | Scripts, backup, war room code |
| Design | Claude | Specs when tasked |
| Research | Gemini / ChatGPT | When tasked |

War room CLI does **not** replace agent tabs — it **feeds** them with live local state.

---

## Build increment

**Task id:** `mmi-war-room-v1`  
**Owner:** Codex  
**Output:** `mmi/war_room.py`  
**Score:** 78

Depends on: command center + backup push (done).

---

## Hard stops

- MMI only (`C:\Architectapp_clean`)
- Local CLI only
- No NorthStar bridge
- No cloud queue/DB
- No npm / `web/`
