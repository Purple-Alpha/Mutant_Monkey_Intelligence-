# MMI AI Lane Scope — Canonical Reference

**Status:** OPERATOR GUIDE — all new agent sessions  
**Authority:** Matt (Super)  
**Maintained by:** Cursor (file updates on Matt directive)  
**Date:** 2026-07-03  
**Supersedes:** ad-hoc handoff prose; legacy `AGENTS.md` swarm chart for active MMI work

**Authority repo:** `C:\MMI` (WSL: `/mnt/c/MMI`)  
**Forbidden default path:** `/home/socialarchitect/northstar` — different tree unless actually mounted

If this file conflicts with `MMI_ACTIVE_SCOPE.md`, follow `MMI_ACTIVE_SCOPE.md` and ask Matt.

---

## Read first (every session)

| Order | Path | Why |
|-------|------|-----|
| 1 | `mmi/project_brain/status/MMI_ACTIVE_SCOPE.md` | Current scope |
| 2 | `mmi/project_brain/status/MMI_PIPE_STAGING.json` | Pipe state, active task |
| 3 | `mmi/project_brain/status/MMI_LANE_ROUTING.md` | Queue + routing detail |
| 4 | `CODEX.md` | Authority order, hard stops |
| 5 | **This file** | Lane boundaries |

```bash
cd /mnt/c/MMI
python3 scripts/reload_mmi_pipes.py
python3 scripts/next_task.py
```

---

## Lane map (one model, one lane per hop)

| Lane | Tool | Owns | Does **not** |
|------|------|------|--------------|
| **Super** | Matt | Build authorization, GATED, scope changes, lane reactivation, product direction | — |
| **Research (primary)** | Gemini | First-pass research, threat/intel surveys, lane investigations | Spec, code, GATED |
| **Research (deep)** | ChatGPT (+ Gemini) | Adversarial research, cross-check, findings markdown | Spec, code, GATED |
| **Design / Spec** | Claude | Architecture specs, contracts, § schemas, normative handoffs | Implement code, file to repo, BUILDABLE/GATED/PERFECT claims |
| **Plan + diff review** | Codex | Pre-build: **BUILDABLE \| NOT BUILDABLE**; Post-build: **CLEAN \| NOT CLEAN** | Write repo implementation code; authorize build |
| **Implement + file** | Cursor | Code, tests, pytest, git, filing lane outputs to repo paths, staging updates | GATED alone; skip Codex gates; claim PERFECT/M4 closed |
| **Completion gate** | Gemini Paid API / `audit_tools` | Pass/fail verification vs requirements | Spec, implement |
| **GATED** | Matt only | Final gate closure after completion gate | — |

**Rule:** One model, one lane per hop. Matt relays between tools — or the tool reads repo directly (preferred over 40KB paste blocks).

---

## Who files what (repo writes)

| Output | Writer | Typical path |
|--------|--------|--------------|
| Research findings | **Cursor** (from research lane paste or ZIP filing) | `mmi/project_brain/lanes/RESEARCH_*.md` |
| Spec / architecture | **Cursor** (from Claude output) | `mmi/project_brain/architecture/*.md` |
| Codex verdict / handoff | **Cursor** (from Codex output) | `mmi/project_brain/lanes/CODEX_HANDOFF_*.md` |
| Closeout / status | **Cursor** | `mmi/project_brain/status/`, `mmi/project_brain/lanes/*CLOSEOUT*` |
| Python, tests, scripts | **Cursor** (after Matt build auth) | `scripts/`, `mmi/`, `tests/`, etc. |
| `tasks.json`, pipe staging | **Cursor** | `tasks.json`, `MMI_PIPE_STAGING.json` |

Claude, Codex, ChatGPT, Gemini: **deliver in chat** (or read/edit if repo-mounted). **Do not** assume commits unless Matt explicitly assigns filing to that lane.

---

## Evolution gate build loop (hard stops)

Applies to M4 and similar gated work:

```text
Matt auth (research/spec)
  → Research (Gemini/ChatGPT) → Cursor files findings
  → Spec (Claude) → Cursor files spec
  → STOP → Codex plan review → BUILDABLE | NOT BUILDABLE
  → Matt: authorize build
  → Cursor build (staged — not 48h-first)
  → STOP → Codex diff review → CLEAN | NOT CLEAN
  → completion gate
  → Matt GATED
```

| Stop | Meaning |
|------|---------|
| BUILDABLE | Plan approved — **not** build authorized |
| authorize build | Matt only — starts implementation |
| CLEAN | Diff approved — **not** GATED |
| GATED | Matt only — after completion gate |

**Never in one pass:** plan + code + gate + GATED.

**Forbidden claims (all lanes unless Matt GATED):** PERFECT tier achieved, M4 closed, M4 met, build authorized in spec runs.

---

## Per-lane detail

### Matt (Super)

- `authorize research …`, `authorize spec …`, `authorize build …`
- Final **GATED** after completion gate
- Resolves scope conflicts; reactivates paused lanes (DAX, Trades, Phase 1)

### Gemini + ChatGPT (Research)

- Output: findings markdown, adversarial critique, falsifier maps
- **Do not:** write specs, edit `ops/`, run harnesses, close gates
- Adversarial template: `lanes/MMI_CHATGPT_ADVERSARIAL_RESEARCH_PROMPT_FRAMEWORK_2026-07.md`
- Integration guide: `lanes/CHATGPT_MMI_LANE_INTEGRATION_2026-07-03.md`

### Claude (Design)

**Do:**

- Read repo before writing (research, filed spec, staging, prior Codex handoffs)
- Normative specs: constants, FSM, falsifiers, § schemas, revision logs
- Adversarial self-review on **filed** spec — inline fixes, not scratchpad duplicates
- One grounded pass > five MESSAGE loops without repo access

**Do not:**

- Implement Python, run pytest, git commit (unless Matt explicitly overrides)
- File to repo by default — Cursor files
- Verdict **BUILDABLE**, **GATED**, **PERFECT**, **M4 closed**
- Re-derive specs when `architecture/` already has a newer filing

**Prompt framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

### Codex (Plan + diff review; backbone when assigned)

**Plan review:** spec vs research → BUILDABLE \| NOT BUILDABLE + numbered blockers  
**Diff review:** post-build patch → CLEAN \| NOT CLEAN  
**Backbone** (when `tasks.json` assignee = Codex): scripts, deployer, repo plumbing per `MMI_LANE_ROUTING.md`

**Do not:** authorize build; claim GATED/PERFECT/M4 closed

### Cursor (Implement + file + queue)

**Always (PM):** queue hygiene, routing docs, handoff packets for Matt  
**When authorized:** implement, test, commit (Matt asks)  
**Filing:** all lane outputs land on disk here

**Do not:**

- Absorb Claude/Codex/research lanes by default
- Skip Codex BUILDABLE / CLEAN stops
- Start 48h M4 runner before §17 prior phases
- Close GATED without completion gate + Matt

### Completion gate (audit)

- Verifies deliverable vs spec/requirements
- **Not** a substitute for Codex diff review

---

## Minimal session start (paste for any new agent)

```text
PROJECT: MMI
REPO: C:\MMI
READ: mmi/project_brain/lanes/MMI_AI_LANE_SCOPE_2026-07-03.md
      mmi/project_brain/status/MMI_PIPE_STAGING.json
LANE: <Design|Research|Codex review|Cursor implement> — ONE ONLY
TASK: <one sentence>
OUTPUT: <path or verdict format>
HARD STOPS: no GATED; no PERFECT; no northstar; BUILDABLE ≠ build auth
```

---

## Anti-patterns (learned 2026-07-03)

| Bad | Good |
|-----|------|
| 40KB handoff every hop | Read paths on disk |
| Claude MESSAGE 1→2→3→R2 without repo | One grounded read + one revision pass |
| Claude files repo / returns BUILDABLE | Claude spec only; Cursor files; Codex verdict |
| Codex BUILDABLE → start coding | Matt `authorize build` → Cursor Phase 0 |
| Review spec Claude can't read | Mount repo or paste findings as plain text first |
| Straight-to-48h M4 | §17 staged ladder; Phase 11 last |

---

## Current snapshot — M4 evolution gate (2026-07-03)

| Field | Value |
|-------|--------|
| Spec | `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.2) |
| Research | `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` (v2.1) |
| Codex R2 | **BUILDABLE (STAGED)** — `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R2_2026-07-03.md` |
| Phases 0–10 | Clear to build after Matt auth |
| Phase 11 (48h FINAL) | Gated on §13.1 draft-patch evidence (built, not just spec'd) |
| `evolution_gate` | OUTSTANDING |
| Build | **NOT AUTHORIZED** until Matt: `authorize build M4 evolution gate` |
| First build tranche | §17 Phase 0 — `mmi/m4/` scaffold + `m4_import_ban_test.py` |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | Canonical lane scope for all new agents; M4 loop + filing matrix |

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
