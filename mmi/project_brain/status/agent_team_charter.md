# Agent Team Charter — Builder + DriftWatcher (Git Worktree)

**Updated:** 2026-06-27  
**Authority:** Operating model for parallel Cursor agents. Does **not** authorize build, promotion, or production dispatch. Live queue truth: `python3 scripts/mmi_pm_voice.py` + `python3 scripts/mmi_dispatch.py --verify`.

---

## Team (three roles)

| Role | Who | Worktree | Lane |
|------|-----|----------|------|
| **Superintendent** | Matt | Either (merge authority) | DEC IDs, `MODE: BUILD`, merge, `--sync` + `--verify` |
| **Builder** | One Cursor agent | **Hot** (`northstar`) | One scoreboard row: implement → pytest → `AWAITING_AUDIT` |
| **DriftWatcher** | One Cursor agent | **Cold** (`northstar-driftwatch`) | Queue drift, research, contract drafts, gate prep — **no hot-lane writes** |

**Naming:** *DriftWatcher operator role* (this charter) is **not** scoreboard **#86 W2 DriftWatcher** (runtime confidence observer, GATED). Do not conflate.

---

## Why worktrees

Parallel agents on one working tree caused DEC collisions, scoreboard overwrites, and stale `handoff.md`. Git worktrees give **separate checkouts, one `.git`**, so Builder and DriftWatcher can commit locally without stepping on each other's files until Matt merges.

---

## Worktree layout

| Worktree | Path | Branch (default) | Owns |
|----------|------|------------------|------|
| **Hot (Builder)** | `/home/socialarchitect/northstar` | `safety/queue-drift-cleanup-20260528` | `3. SwarmCommand_Engine/.../Runtime_Implementation/` builds, hot-lane gate runs, scoreboard row under build |
| **Cold (DriftWatcher)** | `/home/socialarchitect/northstar-driftwatch` | `feedstock/driftwatch` (branch off hot HEAD) | New research artifacts, contract **DRAFT** files, boundary docs — append-only cold paths |

### One-time setup (DriftWatcher cold tree)

```bash
cd /home/socialarchitect/northstar
git worktree add -b feedstock/driftwatch ../northstar-driftwatch HEAD
```

Git does not allow two worktrees on the same branch; cold lane uses `feedstock/driftwatch` and merges to hot via Matt.

Open **two Cursor windows**: one rooted at `northstar`, one at `northstar-driftwatch`. Run `mmi_pm_voice.py` + `mmi_dispatch.py --verify` in the **hot** tree first every session.

### Teardown (when done)

```bash
cd /home/socialarchitect/northstar
git worktree remove ../northstar-driftwatch
```

---

## File ownership (collision guard)

### Hot lane only (Builder + Superintendent at merge)

- `mmi/MMI_DECISION_LOG.md`
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`
- `mmi/project_brain/status/active_task.md`
- `mmi/MMI_CURRENT_STATE.md`
- `mmi/MMI_OPERATOR_MAP.md` (when routing changes)
- `core/**` under Runtime_Implementation for the **active build row**

### Cold lane only (DriftWatcher)

- `mmi/project_brain/architecture/**` (new or topic-specific research)
- `mmi/project_brain/status/*_boundary.md`, `*_re_triage.md`, `*_research*.md`
- `4. Product_Roadmap/*_DRAFT*.md` or new contract files **before** §11
- `mmi/project_brain/status/agent_team_charter.md` (this file)

### Shared read, single writer at merge

- `mmi/project_brain/status/handoff.md` — **Superintendent** refreshes after merge; agents read, do not fight over it

**Rule:** If DriftWatcher needs a scoreboard or DEC change, leave a note in the cold artifact (`## Superintendent action`) — Matt applies on merge.

---

## Session open (every agent)

```bash
cd /home/socialarchitect/northstar   # or northstar-driftwatch for cold
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --verify
```

| Agent | Follows |
|-------|---------|
| **Builder** | Console `MODE: BUILD` or `MODE: AUDIT` on **one** hot row |
| **DriftWatcher** | `active_task.md` RESEARCH lane; **ignore** hot `MODE: AUDIT` unless Matt parks hot lane |
| **Matt** | Resolves hot vs cold conflict; only Matt emits `MODE: BUILD` |

---

## Hot lane protocol (Builder)

1. Matt authorizes build → MMI-DEC with explicit quote.
2. Implement + focused pytest in Runtime_Implementation.
3. Scoreboard row → `AWAITING_AUDIT`; append DEC; **no** `build_default_registry` / AUTH-5 unless contract says so.
4. Run completion gate 0 blocking → Superintendent or Builder reconciles `GATED`.
5. `mmi_dispatch.py --sync` + `--verify` on **hot** tree; commit routing files.

**One hot row at a time.** Do not start a second build row until the current row is `GATED` or explicitly parked by Matt.

---

## Cold lane protocol (DriftWatcher)

1. Research, boundary review, contract drafts in **new or cold-owned paths** only.
2. No edits to hot-lane files in the cold worktree (or stage locally and **do not push** — prefer zero touch).
3. Reconcile against scoreboard **read-only**; document gaps in the research artifact.
4. Pre-build gate prep: manifest + claim text in artifact; **Grok/Codex gate runs on hot tree** after Matt moves row to `SIGNED_UNBUILT`.
5. When research is ready: `## Done When` checklist + `for: Matt` in artifact; Matt updates `active_task.md`.

---

## Merge protocol (Superintendent)

1. Pull/rebase cold worktree commits onto hot branch (or merge feedstock branch).
2. Assign **next** MMI-DEC ID before appending log.
3. Refresh `handoff.md`, `active_task.md`, `MMI_CURRENT_STATE.md` as needed.
4. `--sync` + `--verify` → PASS before declaring lane closed.

---

## Current snapshot (2026-06-27)

| Lane | Row | Status | Owner |
|------|-----|--------|-------|
| **Hot** | #70 Final Review Agent | `AWAITING_AUDIT` — completion gate pending (`aa38ca3`) | Builder |
| **Cold** | #43 Geo-Context | RESEARCH 4/10 — Lane 1 scope confirmation | DriftWatcher |

Matt must **park** one lane or accept sequential merge if both agents need superintendent files in the same session.

---

## One-line mission

**Builder closes one hot row at a time; DriftWatcher feeds the queue from a cold worktree; Matt merges and owns DEC truth.**
