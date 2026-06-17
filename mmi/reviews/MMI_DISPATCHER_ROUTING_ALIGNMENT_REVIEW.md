# MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW.md

> **REVIEW ONLY — DOES NOT AUTHORIZE IMPLEMENTATION.**
> Compares golden routing doctrine in `mmi/history_intake/MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md`
> against **committed** repo behavior. Matt must explicitly authorize any dispatcher/routing patch
> after reviewing findings.

**Review ID:** `MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW`  
**Date:** 2026-06-16  
**Authority:** Matt Nichol — review lane only  
**Scope:** Gap analysis. No code, routing rules, authority matrix, handshake, or scoreboard changes.

**Evidence base (committed at review time):**
- `scripts/mmi_dispatch.py` (HEAD `724e668`)
- `mmi/MMI_ROUTING_RULES.md`
- `mmi/MMI_AUTHORITY_MATRIX.md`
- `MMI_CURRENT_STATE.md`
- `PROJECT_HANDSHAKE.md`
- `AGENTS.md` §2.1.2 / §2.2 (standing doctrine — cross-reference only)
- Live runs: `python3 scripts/mmi_dispatch.py`, `python3 scripts/mmi_dispatch.py --verify`

**Golden doctrine under test (from intake — `NEEDS_MMI_REVIEW`, not promoted):**
1. Matt picks phase / authority; MMI picks the lane.
2. BUILD = Cursor (plan) → Codex (pre-build review) → Cursor (build).
3. Independent review → Codex; `OPERATOR_ACTION_REQUIRED: NO` for normal review routing.
4. ALL_CLEAR = queue empty; does not authorize next phase; Matt names next target.

---

## Executive summary

| Area | Verdict |
|---|---|
| Scoreboard-derived routing (Stage 1 dispatcher) | **ALIGNED** — script runs, derives `MODE: ALL_CLEAR` from scoreboard |
| ALL_CLEAR authority semantics | **ALIGNED** — Matt must name next phase; no auto-authorization |
| ALL_CLEAR next-direction candidates | **GAP** — categories only, no concrete candidate list |
| Matt target vs MMI lane split | **GAP** — `AGENTS.md` §2.2 aligned; `mmi/` governance files and dispatcher do not codify Codex or lane-selection doctrine |
| BUILD → Codex pre-build | **GAP** — committed dispatcher routes BUILD straight to Cursor |
| Independent review → Codex | **GAP** — routes to Matt; operator action required |
| `--verify` vs routing doctrine | **GAP** — verify checks consistency only, not doctrine |
| `PROJECT_HANDSHAKE.md` vs dispatcher | **CONTRADICTION** — handshake says dispatcher integration NOT active |
| Codex in routing rules / authority matrix | **GAP** — Codex absent from both committed `mmi/` files |

**Bottom line:** Golden doctrine is partially reflected in live ALL_CLEAR behavior and in `AGENTS.md`, but **not** in committed `mmi/MMI_ROUTING_RULES.md`, `mmi/MMI_AUTHORITY_MATRIX.md`, or `scripts/mmi_dispatch.py` BUILD/REVIEW branches. Implementation patches remain **`DO_NOT_PATCH_WITHOUT_AUTHORIZATION`**.

---

## Required questions

### Q1. Does ALL_CLEAR output provide valid next-direction candidates?

**Finding:** **GAP**

**Committed behavior** (`build_route_lines()` ALL_CLEAR branch):
```
MODE: ALL_CLEAR
BLOCKED_UNTIL: Matt names the next phase target (build, research, or design)
OPERATOR_ACTION_REQUIRED: YES — choose the next MMI task
```

**Aligned:**
- Correctly states queue is empty and next phase is not auto-authorized.
- Names three **phase categories** (build / research / design).

**Gap:**
- Does **not** emit concrete next-direction **candidates** (e.g. signed-unbuilt contracts, parked design lanes, research items from scoreboard tail, untracked concept docs flagged in intake).
- Matt must supply the target from memory or other docs; dispatcher does not surface a scored candidate list.

**Classification:** `GAP` — authority semantics OK; candidate surfacing missing.  
**Patch implication:** `DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — adding candidate enumeration is a product decision (what to include, how to rank).

---

### Q2. Does MMI distinguish Matt choosing the target from MMI choosing the lane?

**Finding:** **GAP** (partial **ALIGNED** at ALL_CLEAR only)

**Aligned:**
- At ALL_CLEAR, Matt is correctly assigned (`ASSIGNED_TO: Matt`, `NEXT_PROMPT_GOES_TO: Matt`) for **target/phase** selection.
- `AGENTS.md` §2.2 explicitly states: "MMI selects the lane" / "Matt is asked to choose a worker only when routing affects authority, signed scope, live/customer data, or material project risk."

**Gap:**
- Committed `mmi/MMI_ROUTING_RULES.md` has **no** Matt-vs-MMI split, no Codex row, no auto-routing table.
- Committed `scripts/mmi_dispatch.py` does not encode lane-selection doctrine in prose fields (no `LANE_REASON`, no explicit "Matt names target" vs "MMI assigns lane" framing outside ALL_CLEAR).
- For non-ALL_CLEAR modes, lane assignment exists (Cursor/Gemini/Claude/ChatGPT/Grok/Matt) but **Codex is never assigned** despite `AGENTS.md` §2.2 routing table.
- `MMI_AUTHORITY_MATRIX.md` has no Codex column — lane doctrine not mirrored in MMI governance files.

**Classification:** `GAP` between golden doctrine + `AGENTS.md` vs committed `mmi/` + dispatcher Codex absence.  
**Patch implication:** `DO_NOT_PATCH_WITHOUT_AUTHORIZATION`.

---

### Q3. Does BUILD routing correctly model Cursor → Codex pre-build review → Cursor build?

**Finding:** **GAP**

**Committed behavior** (`build_route_lines()` BUILD branch, `get_signed_unbuilt()`):
```python
("MODE", "BUILD"),
("ASSIGNED_TO", "Cursor"),
("NEXT_PROMPT_GOES_TO", "Cursor"),
("BLOCKED_UNTIL", "NONE"),
("OPERATOR_ACTION_REQUIRED", "NO"),
```

**Golden doctrine / `AGENTS.md` §2.1.2:**
- Pre-build Codex review required before implementation starts.
- Intake models: `Cursor (draft plan) → Codex (review) → Cursor (build)`.

**Also note:** `MMI_THREAD_HANDOFF.md` documents post-build Codex only (`Cursor builds → Codex reviews`), not pre-build — internal doc tension with `AGENTS.md` §2.1.2 and golden intake.

**Classification:** `GAP` — committed dispatcher skips Codex pre-build entirely.  
**Patch implication:** `DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — requires explicit implementation authorization and alignment with `MMI_THREAD_HANDOFF.md` vs `AGENTS.md`.

---

### Q4. Does independent review route to Codex without requiring Matt to pick the reviewer?

**Finding:** **GAP**

**Committed behavior** (`get_independent_review_pending_task()` branch):
```python
("ASSIGNED_TO", "Matt / independent reviewer"),
("NEXT_PROMPT_GOES_TO", "Matt"),
("OPERATOR_ACTION_REQUIRED", "YES — choose reviewer or accept/return the evidence"),
```

**Golden doctrine:**
- Independent review → Codex
- `OPERATOR_ACTION_REQUIRED: NO` for normal independent-review routing

**Note:** No scoreboard row currently triggers this branch (queue ALL_CLEAR), so this is **latent** behavior — but committed code path contradicts doctrine when review-pending rows exist.

**Classification:** `GAP`  
**Patch implication:** `DO_NOT_PATCH_WITHOUT_AUTHORIZATION`

---

### Q5. Does `--verify` check the routing doctrine or only file consistency?

**Finding:** **GAP** (verify behavior is **ALIGNED** with its own narrow scope; **GAP** vs golden expectation)

**Committed `run_verify()` checks:**
1. `MMI_CURRENT_STATE.md` routing block in sync with derived state
2. Routing-authority files committed (`MMI_CURRENT_STATE.md`, scoreboard, `scripts/mmi_dispatch.py`)
3. `scripts/verify_build_truth.py` PASS
4. `scripts/detect_drift.py` — BLOCK count must be 0

**Live result (2026-06-16, committed tree):** `VERDICT: PASS`

**What verify does NOT check:**
- Codex presence in BUILD/REVIEW lanes
- Matt-vs-MMI lane-selection split
- Alignment with `mmi/MMI_ROUTING_RULES.md` or `AGENTS.md` §2.2
- `PROJECT_HANDSHAKE.md` dispatcher status consistency
- ALL_CLEAR candidate surfacing

**Classification:** `ALIGNED` with verify's documented purpose (consistency/evidence gate); `GAP` if doctrine compliance is expected from `--verify`.  
**Patch implication:** `NEEDS_OPERATOR_DECISION` — should verify grow doctrine checks, or remain consistency-only?

---

### Q6. Does `PROJECT_HANDSHAKE.md` contradict current dispatcher status?

**Finding:** **CONTRADICTION**

**Handshake (committed):**
```
MMI status: ACTIVE for documentation/governance only.
Runtime authority: NOT active.
Dispatcher integration: NOT active.
Automation: NOT active.
```

**Live repo:**
- `scripts/mmi_dispatch.py` runs, derives routing from scoreboard, supports `--sync` and `--verify`.
- `MMI_CURRENT_STATE.md` routing block is derived and verify PASS.
- Branch tracks `github/safety/queue-drift-cleanup-20260528`; handshake HEAD block still cites `50b58a8` (2026-06-13).

**Classification:** `CONTRADICTION` — "dispatcher integration NOT active" vs executable Stage 1 file-based dispatcher.  
**Patch implication:** `DO_NOT_PATCH_WITHOUT_AUTHORIZATION` for handshake — separate doc-reconciliation lane per intake closure record.

---

### Q7. What exact implementation gaps remain?

| # | Gap | Classification | Patch |
|---|---|---|---|
| 1 | Codex absent from `mmi/MMI_ROUTING_RULES.md` | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 2 | Codex absent from `mmi/MMI_AUTHORITY_MATRIX.md` | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 3 | BUILD branch: no pre-build Codex step / `PRE_BUILD_REVIEW` field | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 4 | REVIEW branch: Matt reviewer + operator YES vs Codex + operator NO | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 5 | No auto-routing table in committed routing rules (Matt vs MMI split) | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 6 | Default sync requires `--sync` flag; no auto-sync on run | GAP | NEEDS_OPERATOR_DECISION (intake golden candidate; not in AGENTS.md as hard rule) |
| 7 | `--verify` does not validate routing doctrine | GAP | NEEDS_OPERATOR_DECISION |
| 8 | ALL_CLEAR does not surface concrete next-direction candidates | GAP | NEEDS_OPERATOR_DECISION |
| 9 | `PROJECT_HANDSHAKE.md` dispatcher/runtime lines stale | CONTRADICTION | DO_NOT_PATCH_WITHOUT_AUTHORIZATION (separate handshake pass) |
| 10 | `MMI_THREAD_HANDOFF.md` post-build Codex only vs pre-build in `AGENTS.md` §2.1.2 | CONTRADICTION | NEEDS_OPERATOR_DECISION (doc alignment before code patch) |
| 11 | `AGENTS.md` §2.2 Codex routing vs committed dispatcher | GAP | DO_NOT_PATCH_WITHOUT_AUTHORIZATION |
| 12 | Golden doctrine in intake marked `NEEDS_MMI_REVIEW` — not promoted to `mmi/MMI_PROTOCOL.md` | ALIGNED (correct governance posture) | Promotion requires Matt authorization |

---

## Cross-artifact alignment matrix

| Doctrine element | Intake golden | AGENTS.md | MMI_ROUTING_RULES | MMI_AUTHORITY_MATRIX | mmi_dispatch.py |
|---|---|---|---|---|---|
| Matt = phase/authority | Yes | §2.2 | Not stated | Not stated | ALL_CLEAR only |
| MMI = lane | Yes | §2.2 | Not stated | Not stated | Partial (per-mode) |
| Codex in BUILD pre-review | Yes | §2.1.2 | No Codex | No Codex | Cursor only |
| Codex independent review | Yes | §2.2 table | No Codex | No Codex | Matt reviewer |
| ALL_CLEAR ≠ next auth | Yes | Implied | N/A | N/A | **ALIGNED** |
| Scoreboard-derived route | Yes | Implied | N/A | N/A | **ALIGNED** |

---

## What is already aligned (do not break)

| Item | Classification |
|---|---|
| Scoreboard-derived routing (`SOURCE: derived from scoreboard`) | ALIGNED |
| ALL_CLEAR terminal state when queue empty | ALIGNED |
| ALL_CLEAR requires Matt for next phase target | ALIGNED |
| `--verify` consistency gate passes on committed tree | ALIGNED |
| Intake captures doctrine without promoting it to authority | ALIGNED |
| Dispatcher/routing files clean post-intake (no stray local patches) | ALIGNED |

---

## Recommended operator decisions (not authorized by this review)

1. **Promote golden doctrine?** — From intake `NEEDS_MMI_REVIEW` into `mmi/MMI_PROTOCOL.md` and/or routing rules.
2. **Pre-build vs post-build Codex?** — Reconcile `AGENTS.md` §2.1.2, `MMI_THREAD_HANDOFF.md`, and proposed BUILD lane.
3. **Verify scope?** — Keep consistency-only or add doctrine-compliance checks.
4. **ALL_CLEAR candidates?** — Whether dispatcher should enumerate next targets from scoreboard/parked items.
5. **Auto-sync default?** — Opt-in `--sync` (committed) vs auto-sync on every run (intake golden candidate).
6. **Handshake reconciliation?** — Separate authorized doc pass.

---

## Final rule

This review **does not authorize**:
- dispatcher implementation
- routing rules or authority matrix patches
- handshake or scoreboard changes
- build / research / design
- automation
- choosing the next build/research/design target

Matt must explicitly authorize a follow-on lane (e.g. `MMI_DISPATCHER_ROUTING_IMPLEMENTATION`) after reviewing these findings.

---

## Authority footer

Current routing authority remains committed `scripts/mmi_dispatch.py`, `mmi/MMI_GATE_REGISTRY.md`,
and `mmi/MMI_DECISION_LOG.md` — **not** this review file and **not** intake golden doctrine
until separately promoted and implemented.
