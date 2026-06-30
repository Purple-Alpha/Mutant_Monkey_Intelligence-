# MMI War Room Setup

Date: 2026-06-29  
Authority: Matt (Super)  
Repo: `C:\Architectapp_clean` / `/mnt/c/Architectapp_clean`

---

## What you are setting up

A **two-surface war room** on one Mini PC:

1. **Execute** — Cursor Editor (monitor 1)
2. **Orient** — Cursor Agents + local war room CLI (monitor 2)

No cloud war room. No NorthStar. Local state only.

---

## One-time: dual monitor in Cursor

### Monitor 1 — Editor

- Open folder: `C:\Architectapp_clean`
- Terminal (WSL): `/mnt/c/Architectapp_clean`
- This is where you edit, run scripts, commit

### Monitor 2 — Agents war room

1. `Ctrl+Shift+P` → **Open Agents Window**
2. Drag that window to monitor 2
3. Open **2–3 agent tabs** with fixed roles (see below)

---

## War room CLI (after `mmi-war-room-v1` ships)

On monitor 2 terminal (or a split pane):

```bash
cd /mnt/c/Architectapp_clean
python mmi/war_room.py --watch --seconds 30
```

Until `war_room.py` exists, use:

```bash
python mmi/command_center.py --watch --seconds 30
```

---

## Agent tab roles (monitor 2)

Paste once per new tab:

**Cursor PM tab**

```text
MMI PM lane only. Repo: /mnt/c/Architectapp_clean.
Read mmi/project_brain/status/MMI_ACTIVE_SCOPE.md and war room output.
Queue/routing only. No Social Architect, DAX, Trades, NorthStar.
```

**Codex tab**

```text
MMI Backbone only. Repo: /mnt/c/Architectapp_clean.
Read CODEX.md first. Run complete_task.py after every task.
No npm, web/, ops/run.py.
```

**Claude tab (when design task active)**

```text
MMI Design lane. Read assigned spec in mmi/project_brain/architecture/.
Do not implement code unless tasked.
```

---

## Daily operator loop

| Step | Command / action |
|------|------------------|
| 1 | `python mmi/command_center.py` (or war_room when built) |
| 2 | Execute active task on monitor 1 |
| 3 | `python scripts/complete_task.py TASK_ID --by ...` |
| 4 | After meaningful changes: `python scripts/mmi_cold_backup.py --backup-and-push` |

---

## What is parked (not this war room)

- NorthStar monitor-2 handoff blocks
- LangGraph / automation substrate
- Social Architect `web/` command center
- Live cloud agent runtime

See `architecture/MMI_WAR_ROOM_SPEC.md`.
