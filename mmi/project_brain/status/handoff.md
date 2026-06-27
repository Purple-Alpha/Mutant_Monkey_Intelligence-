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

**Expected at handoff (hot lane):**

```text
MMI_OPERATOR_CONSOLE
status: ACTION
task: Run completion gate for Final Review Agent
for: completion gate auditor (complete_gate.py)

MODE: AUDIT
```

**Cold lane (`active_task.md`):** #43 Geo-Context RESEARCH 4/10 — Matt confirms Lane 1 scope. DriftWatcher only; does not override hot `MODE: AUDIT` unless Matt parks #70.

---

## Hot lane — #70 Final Review Agent (`AWAITING_AUDIT`)

| Item | Detail |
|------|--------|
| Contract | `4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md` (§11 MMI-DEC-244) |
| Build | `core/orchestrator/final_review_agent.py` (`aa38ca3`, MMI-DEC-248) |
| Tests | `tests/test_final_review_agent.py` — 15 pass |
| Slice A | `audit_tools/complete_gate.py` + `core/evidence_package/package_auditor.py` (not absorbed) |
| Boundaries | Not in `build_default_registry`; no production dispatch; never sign/promote/authorize |

### Next job (Builder — immediate)

**Lane: AUDIT** — completion gate 0 blocking → `GATED` reconcile.

```bash
cd /home/socialarchitect/northstar
python3 audit_tools/complete_gate.py --pre-commit \
  --task final_review \
  --claim "#70 FinalReviewAgent built aa38ca3 + 15 tests; FR-DER + FR-GOV; ready for audit"
```

On 0 blocking: scoreboard #70 → `GATED`; append MMI-DEC; update `MMI_CURRENT_STATE.md`; `--sync` + `--verify`; commit routing files.

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
| #70 Final Review | `AWAITING_AUDIT` | Hot — Builder |
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

240–248 (#70 boundary → contract → gate → §11 → build). Latest build: **MMI-DEC-248** (`aa38ca3`).

---

## One-line mission

**Builder:** completion gate 0/0 on #70 → `GATED`, sync routing, verify PASS. **DriftWatcher:** #43 research in cold worktree only. **Matt:** merge + DEC truth.
