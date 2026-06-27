# DriftWatcher Handoff — Window B

**Updated:** 2026-06-27  
**Role:** Cold-lane operator agent (Window B). **Not** scoreboard #86 W2 DriftWatcher.  
**Authority:** Research and feedstock only. Does **not** authorize build, §11, promotion, or production dispatch.

**Charter:** `mmi/project_brain/status/agent_team_charter.md`  
**Builder (Window A):** `mmi/project_brain/status/handoff.md` — **stand by**; do not edit hot-lane files.

---

## Identity

| Field | Value |
|-------|-------|
| **Project** | Mutant Monkey Security |
| **Your worktree** | `/home/socialarchitect/northstar-driftwatch` |
| **Your branch** | `feedstock/driftwatch` |
| **Hot tree (read-only)** | `/home/socialarchitect/northstar` on `safety/queue-drift-cleanup-20260528` |
| **Do not open/build in** | Hot tree Runtime_Implementation while #70 AUDIT is active |

---

## Session open (every DriftWatcher session)

```bash
cd /home/socialarchitect/northstar-driftwatch

# Sync feedstock with hot before work (cold may be behind)
git fetch github 2>/dev/null || true
git merge github/safety/queue-drift-cleanup-20260528 -m "feedstock: sync from hot" || git rebase github/safety/queue-drift-cleanup-20260528

python3 scripts/mmi_pm_voice.py      # read-only context from cold tree
python3 scripts/mmi_dispatch.py --verify
```

**Ignore hot `MODE: AUDIT` (#70)** unless Matt parks the hot lane. Your lane is `active_task.md` → **RESEARCH**.

---

## Your active task

From `mmi/project_brain/status/active_task.md`:

| Field | Value |
|-------|-------|
| **Row** | #43 Geo-Context |
| **Lane** | `RESEARCH` |
| **Score** | 4/10 → close out remaining items |
| **For** | Matt — confirm Lane 1 scope before contract draft |
| **Status** | **Not** build authorization |

### Done When (your closeout checklist)

- [x] Relationship #43 ↔ #79 / #76 documented
- [x] Research artifact under `mmi/project_brain/architecture/`
- [x] v2 geo-fence Reality Anchor doctrine cross-linked (`448315a`+)
- [ ] **Matt confirms Lane 1 scope** → contract draft or extended hold
- [x] `mmi_dispatch.py --verify` PASS after your commits

**You own the unchecked item's feedstock:** prepare everything Matt needs to say yes/no on Lane 1 without touching hot-lane authority files.

---

## Primary artifact (read + extend)

`mmi/project_brain/architecture/geo_context_43_research_lanes.md`

**Preferred direction (Matt framing):** #43 = **Lane 1 legit geo-context** — tenant service area + jurisdiction facts; reconciled against governed **#79 GeoVelocityAgent** / **#76 GeoIntelAgent**.

**Lane 4 deception:** **PARK** — `geo_fence_manager.md` is reference only; do not import into #43 ES1.

---

## Your deliverables (complete the last task)

### 1. Lane 1 scope confirmation packet (for Matt)

Add a short section to the research artifact (or new cold file) titled **`## Superintendent action — Lane 1 scope`:**

- One-paragraph product surface: what #43 would *do* in Lane 1 only
- Explicit **out of scope** list (Lane 4, person-level tracking, blocking, payment)
- **Yes/No question** for Matt: "Is tenant service area + jurisdiction context the intended #43 surface?"
- If extended hold: what evidence is still missing

### 2. Contract draft prep (only after Matt confirms — or mark DRAFT clearly)

If scope is confirmed, create **new file only:**

`4. Product_Roadmap/Geo_Context_Agent_Design_Contract_Deep_Dive_DRAFT.md`

Scope: **Lanes 1–2 + Lane 3 privacy bar**. Explicitly exclude Lane 4 by reference to `reality_controller/README.md`.

**Do not** sign §11. **Do not** change scoreboard status.

### 3. Reconciliation appendix

One page in the research artifact or draft contract:

| Agent | Emits | #43 must not duplicate |
|-------|-------|------------------------|
| #76 GeoIntelAgent | `GeoBriefing` (Layer 0 brief-only) | Raw geo intel re-emission |
| #79 GeoVelocityAgent | `geo_signal` (Layer 1 velocity anomalies) | Velocity detection logic |
| #43 (proposed Lane 1) | Tenant-declared context facts | Any decoy / tarpit / trap logic |

### 4. Closeout commit on `feedstock/driftwatch`

```bash
cd /home/socialarchitect/northstar-driftwatch
git add mmi/project_brain/architecture/ 4. Product_Roadmap/*DRAFT* 2>/dev/null
git status   # confirm: NO scoreboard, NO MMI_DECISION_LOG, NO active_task.md
python3 scripts/mmi_dispatch.py --verify
git commit -m "feedstock: #43 geo-context Lane 1 scope packet + reconciliation"
```

Tell Matt: **ready to merge** `feedstock/driftwatch` → hot.

---

## Files you MAY touch (cold lane)

- `mmi/project_brain/architecture/**` (research, appendices)
- `mmi/project_brain/status/driftwatcher.md` (this file)
- `4. Product_Roadmap/*_DRAFT*.md` (new contract drafts only)
- `mmi/project_brain/status/*_boundary.md`, `*_research*.md` (new)

## Files you MUST NOT touch

- `mmi/MMI_DECISION_LOG.md`
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`
- `mmi/project_brain/status/active_task.md` ← **Matt only**
- `mmi/MMI_CURRENT_STATE.md`
- `mmi/project_brain/status/handoff.md` ← Builder owns
- `3. SwarmCommand_Engine/.../Runtime_Implementation/core/**` ← Builder hot lane (#70)

If you need a scoreboard or DEC change, add `## Superintendent action` in your artifact — Matt applies on merge.

---

## Scoreboard context (read-only)

| Row | Status | Notes |
|-----|--------|-------|
| **#43** | `SPEC_ONLY` / `NEEDS_SIGNED_CONTRACT` | Your research row — do not advance lifecycle |
| **#76** | `GOVERNED_AGENT` ES1 | Layer 0 brief-only |
| **#79** | `GOVERNED_AGENT` ES2 | Layer 1 velocity detection |
| **#70** | `AWAITING_AUDIT` | Builder hot lane — stay out |
| **#86** | `GATED` | Runtime DriftWatcher — unrelated to your role |

---

## Hot lane awareness (do not act on)

Builder (Window A) will run **#70 Final Review** completion gate after you close and Matt merges:

- `core/orchestrator/final_review_agent.py` (`aa38ca3`)
- Console: `MODE: AUDIT` — Run completion gate for Final Review Agent

---

## Boundaries (repeat)

- Research / contract **DRAFT** only  
- No build authorization  
- No §11 signing  
- No scoreboard lifecycle change  
- No production dispatch / AUTH-5  
- No person-level tracking  
- Lane 4 stays **PARK**

---

## One-line mission

**Close #43 RESEARCH on cold worktree: Lane 1 scope packet for Matt, reconciliation vs #76/#79, optional DRAFT contract — commit on `feedstock/driftwatch`, then hand merge back to Matt.**
