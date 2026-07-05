# MMI Local-First / Cloud-Hybrid Policy

Last updated: 2026-06-28  
Authority: Matt (Super)  
Status: **LOCKED** — governs all MMI work in `C:\Architectapp_clean`

---

## Policy (Matt directive)

Matt is building an agentic system (MMI) on a **local-first architecture**. Hybrid policy:

### Execution & Runtime (Local)

The source of truth for the project brain, `tasks.json`, and all agent execution is the **local Mini PC**.

**Do not propose:**

- Cloud runtimes
- Hosted databases
- API-dependent queues

### Backup Layer (Cloud-Hybrid)

The **only** cloud interaction allowed is redundant backup (e.g. git-remote or encrypted sync of the local brain).

Treat the cloud strictly as **cold storage** — a mirror, **not** a live participant in the agentic loop.

### Isolation

Keep this workspace (`Architectapp_clean`) **strictly isolated** from the NorthStar platform.

**Do not:**

- Bridge these repos
- Introduce cross-repository dependencies
- Sync or copy NorthStar content without explicit Matt authorization

### Agent / Cursor Behavior

When suggesting solutions:

1. Prioritize **local CLI tools** and **filesystem-based state management**
2. Keep **state and execution local**
3. If intelligence exceeds local inference, offload **only reasoning/analysis** to an API when absolutely necessary — never queue state or runtime to cloud

---

## Decision Record

| Question | Matt's answer |
|---|---|
| Source of truth | **Local** — `tasks.json` + `mmi/project_brain/` on Mini PC |
| NorthStar relationship | **Isolated** — no bridge, no cross-repo deps |
| Cloud role | **Cold backup only** — git-remote or encrypted sync |
| Live cloud queue / DB | **No** |
| Command center | **Local CLI** (`mmi/command_center.py`) |

---

## Allowed Cloud Work (bounded)

| Allowed | Not allowed |
|---|---|
| Private git push of `mmi/project_brain/` + `tasks.json` | Supabase/API task queue as source of truth |
| **B2 cold push via `mmi_cold_backup.py --backup-and-push`** (Matt approved 2026-06-28) | Hosted agent runtime |
| Encrypted sync of brain files to cold storage | NorthStar sync or merge |
| Offline backup verification scripts | Cloud-primary state |

Remote: `matt:mmi-cold-storage/archives/` — see `status/MMI_FIRST_B2_PUSH.md`.

---

## Implementation Sequence

1. **Phase-2 MVP (done):** local command center reads local queue
2. **Next:** backup layer spec + minimal cold-storage script (Codex)
3. **Later (Matt auth only):** encrypted sync provider choice, schedule, restore drill

---

## Hard Stops (unchanged)

- MMI only — no Social Architect Phase 1, DAX, Trades
- No npm / `web/` / `ops/run.py` unless Matt explicitly reactivates
- This policy wins over any conflicting root repo docs (`AGENTS.md`, `CLAUDE.md`, etc.)
