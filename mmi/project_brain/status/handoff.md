# Cursor Agent Handoff

**Updated:** 2026-06-27  
**Authority:** Session handoff for worker agents. Does not authorize build, promotion, or production dispatch. Live queue truth: `python3 scripts/mmi_pm_voice.py` + `python3 scripts/mmi_dispatch.py --verify`.

**Team model:** `mmi/project_brain/status/agent_team_charter.md` — **one Builder (hot worktree) + one DriftWatcher (cold worktree) + Matt (merge)**.

---

## Identity

| Field | Value |
|-------|-------|
| **Project** | Mutant Monkey Security (not "NorthStar" in operator prose) |
| **Authority repo** | `/home/socialarchitect/northstar` (WSL — Builder hot tree) |
| **Cold worktree** | `/home/socialarchitect/northstar-driftwatch` (DriftWatcher — create per charter if missing) |
| **Branch** | `safety/queue-drift-cleanup-20260528` |
| **HEAD at handoff** | `448315a`+ (post #70 build MMI-DEC-248 `aa38ca3`) |
| **Windows venture path** | Secondary/reference only — do not treat as authority |

---

## Operator console (run first every session — hot tree)

```bash
cd /home/socialarchitect/northstar
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --verify
```

**Expected at handoff (hot lane):** run `mmi_pm_voice.py` — queue empty or next ranked lane per dispatcher.

**Cold lane (`active_task.md`):** #43 Geo-Context RESEARCH — Matt confirms Lane 1 scope.

---

## Hot lane — #70 Final Review Agent (`GATED` — MMI-DEC-249)

| Item | Detail |
|------|--------|
| Contract | `4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md` (§11 MMI-DEC-244) |
| Build | `core/orchestrator/final_review_agent.py` (`aa38ca3`, MMI-DEC-248) |
| Tests | `tests/test_final_review_agent.py` — 15 pass |
| Gate | `audit_outputs/final_review_agent_20260627T054814Z.md` — 0 blocking / 0 warnings |
| Boundaries | Not in `build_default_registry`; no production dispatch; **not GOVERNED_AGENT** |

---

## Cold lane — #43 Geo-Context (DriftWatcher)

| Item | Detail |
|------|--------|
| Artifact | `mmi/project_brain/architecture/geo_context_43_research_lanes.md` |
| Reference | `mmi/project_brain/architecture/reality_controller/geo_fence_manager.md` (Lane 4 deception PARK) |
| Reconcile | #79 GeoVelocityAgent, #76 GeoIntelAgent |
| Status | **Not** build authorization; Matt confirms Lane 1 scope before contract draft |

Work in `northstar-driftwatch` if hot lane is active. Do not edit scoreboard / DEC log / `active_task.md` from cold tree.

---

## Queue snapshot

| Row | Status | Lane |
|-----|--------|------|
| #70 Final Review | `GATED` (MMI-DEC-249) | Hot — closed |
| #10 Lookalike | `GOVERNED_AGENT` (MMI-DEC-245, breadth 42/70) | Closed |
| #43 Geo-Context | RESEARCH 4/10 | Cold — DriftWatcher |

---

## Environment

- Work in WSL; PowerShell breaks heredocs — use `wsl git -C /path commit -m "..."`
- `complete_gate.py` packet cap 200KB — trim `files_read` in manifests if needed
- Do not build in Architectapp repos
- Parallel agents: **separate worktrees** per `agent_team_charter.md`

---

## DEC sequence (relevant)

240–249 (#70 boundary → contract → gate → §11 → build → GATED). Latest: **MMI-DEC-249** (#70 GATED).

---

## One-line mission

**#70 GATED closed.** **DriftWatcher:** #43 research in cold worktree. **Matt:** Lane 1 scope confirmation or next ranked lane.
