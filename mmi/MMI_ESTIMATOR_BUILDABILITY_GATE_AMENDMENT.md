# MMI Estimator Buildability Gate Amendment

**Document ID:** `MMI_ESTIMATOR_BUILDABILITY_GATE_AMENDMENT.md`

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Implementation landed at `0d3620f` (E12–E14, T28–T34).

**Amends:** `mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md` (§11 signed 2026-06-20; commits `c742a6c` / `42299d3`)

**Decision record:** MMI-DEC-045 — Estimator Buildability Gate Amendment accepted and implemented

**Lane:** Governance / Worth & Priority Scoring

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt Nichol §11 sign-off required before any implementation, commit, or runtime change

**Implementation:** Implemented in `scripts/mmi_estimator.py` + `tests/test_mmi_estimator.py` at `0d3620f`; parent contract patched §7/§8/§16.

---

## Redline summary (2026-06-20 merge)

| Area | Original draft | This merged draft |
|---|---|---|
| Header authority | `Authority: Mutant Monkey Intelligence (MMI)` | **Authority Domain** + **Operator Authority** (no autonomous MMI sign-off implication) |
| §2 vocabulary | "Does not change ... the two-output vocabulary" | Primary scoring outcomes unchanged; **new advisory labels, exclusion reason codes, and exclusion telemetry section** added |
| E12 closed set | `GATED`, `GOVERNED_AGENT`, `COMPLETE` | **`GATED`**, **`GOVERNED_AGENT`**, **`INFRASTRUCTURE_BUILT`**; **`COMPLETE` removed** (registry-only; E10) |
| E12/E13 match rule | Assumed exact names | **Prefix match on stripped column-2 cell** (same discipline as dispatcher) |
| E13 buildable set | "equivalent open build state" (loose) | **`SIGNED_UNBUILT*`, `AWAITING_AUDIT*` only** — locked from live scoreboard + dispatcher |
| E14 | "either excluded ... or labeled" | **Mandatory exclusion** from buildable ranking; label `BLOCKED_MISSING_CONTRACT` |
| E14 path rule | "row / roadmap reference" (ambiguous) | **Agent Design Contract path rule** with resolution order |
| §5 ALL_CLEAR | "no candidate is lifecycle-routeable as next build" | **No active dispatcher route open; comparison-only; not next-build direction** |
| §5 ALL_CLEAR source | Unspecified | **Pinned to `--verify-text` only** |
| Output | Added labels only | **`BUILDABILITY_EXCLUSIONS` telemetry block** added |
| §9 | Truncated | **Completed** |
| §10 DEC | Implied DEC-044 | **MMI-DEC-045** (DEC-044 already taken: PROJECT_DIRECTION retirement) |
| §11 | Missing | **Completed** with reconciliation checkbox |

---

## 0. Decision framing (MMI-DEC-045)

**Title:** Estimator Buildability Gate Amendment accepted and implemented

**Reason:** First Estimator live comparison (read-only, 2026-06-20) exposed a lifecycle/buildability blind spot. Built/closed agents and missing-contract candidates were ranked as next-build candidates because evidence-surface (F1/F4) was rewarded before lifecycle state and buildability were checked.

**Evidence-backed failure (today's run):**

- Estimator ranked **#72, #78, #79, #80** (among others) in top 5 — all **`GATED` (built and closed)** on the scoreboard.
- Estimator ranked **#52 at #1** while Architect returns **`INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT`** — Plain-English Agent Design Contract absent on disk.
- Proven dispatcher correctly emitted **`ALL_CLEAR`** (0 `SIGNED_UNBUILT`, 0 `AWAITING_AUDIT`); Estimator still pointed at done or unbuildable targets.

**Decision:** Add pre-scoring buildability gates **E12–E14** after live scoreboard reconciliation; add ALL_CLEAR advisory pin; add `BUILDABILITY_EXCLUSIONS` telemetry. No formula, weight, NULL, authority, write, routing, selection, or AUTH-5 changes.

**Status:** §11 signed 2026-06-20; implementation complete at `0d3620f`.

---

## 1. Why this amendment exists

First real use of the Estimator (read-only comparison, 2026-06-20) produced **DISAGREE** against the proven scoreboard-lifecycle engine.

Root cause: Estimator **F1 rewards evidence-surface** (signed markers + code + commits). A **finished** agent has maximum evidence-surface. The formula reads completeness as readiness. **Completeness and readiness are opposites for a "what to build next" tool.** The Estimator had no buildability gate reading true lifecycle state.

This amendment adds buildability filtering **before scoring**, so the Estimator stops ranking done and unbuildable work as next-build candidates. It still **ranks only** — it does not select, authorize, route, or build.

---

## 2. Scope of this amendment

### Adds (only)

- Living-state **buildability gates E12–E14** in eligibility phase, **before** scoring.
- **Buildable-now requirement** for next-build ranking membership.
- **ALL_CLEAR advisory flag** (Section 6) when dispatcher queue is empty.
- **`BUILDABILITY_EXCLUSIONS` telemetry** (Section 7) listing excluded candidates and reason codes.
- Acceptance tests **T28–T34** (Section 8).

### Does not change

- Weighted-sum formula.
- Locked weights **30 / 25 / 20 / 10 / 10 / 5** (MMI-DEC-039).
- NULL semantics and coverage reporting (MMI-DEC-043).
- Read-only discipline (stdout only; zero runtime writes).
- Dispatcher routing, registry-fed routing, scoreboard mutation, AUTH-5.
- Estimator authority: **still ranks only; never selects, authorizes, routes, or implies build approval.**

### Output vocabulary

**Does not change the two primary scoring outcomes:**

1. `SCORED_CANDIDATES`
2. `STATE_INCOMPLETE_CANNOT_SCORE`

**This amendment adds** advisory/buildability labels, exclusion reason codes, and exclusion telemetry only. These additions do **not** grant selection, routing, or authorization power.

---

## 3. Living-state buildability gates (E12–E14)

Added to eligibility phase **E1–E11**, applied **before** scoring. A candidate failing any gate is **excluded from the next-build ranking** — not scored low, **excluded** — same discipline as E1–E11.

### E12 — Not already built (closed lifecycle)

Exclude when scoreboard column-2 runtime status **prefix-matches** any **closed-state prefix** in Section 4.

A finished/closed agent cannot be "next."

**Live reconciliation (2026-06-20):** this gate removes today's failure set **#72–#83** (`GATED`) and would also exclude **`GOVERNED_AGENT`** (14 rows) and **`INFRASTRUCTURE_BUILT`** (1 row, #71) if they entered the candidate pool.

**Reason code:** `EXCLUDED_ALREADY_BUILT`

### E13 — Buildable lifecycle state required

To appear in the **next-build ranking**, column-2 runtime status must **prefix-match** a **buildable-state prefix** in Section 4 — the same states the proven dispatcher treats as routeable.

All other runtime statuses are excluded from next-build ranking, including but not limited to:

- `DETECTOR_FUNCTION` (including #52 — partial code, no open build lane)
- `SPEC_ONLY`, `NOT_STARTED`, `GOVERNANCE_DOC_ONLY`
- `RECLASSIFY`, `merged`
- Any E12 closed prefix

**Live reconciliation (2026-06-20):** buildable prefixes **`SIGNED_UNBUILT`**, **`AWAITING_AUDIT`** — **0 rows each** on live scoreboard; dispatcher lists both empty.

**Reason code:** `EXCLUDED_NON_BUILDABLE_STATE`

### E14 — Agent Design Contract resolvable on disk (mandatory exclusion)

A candidate **must not** appear in the next-build ranking unless its required **per-agent Agent Design Contract** resolves to an **existing file** on disk.

**If the required contract path is absent:** label **`BLOCKED_MISSING_CONTRACT`** and **exclude from the buildable ranking.** No either/or. No ranked membership. No exception for high F1/F4.

**Agent Design Contract path rule (locked resolution order):**

1. **Explicit path in scoreboard row text** (column 2 or column 3): first match for  
   `4. Product_Roadmap/*Agent*Design*Contract*.md`  
   or `4. Product_Roadmap/*Agent*Design*Contract*/*.md` in backtick-quoted paths.
2. **Shared Estimator/Architect manifest entry** for that `candidate_id` (if present).
3. **Fail E14** — no inference from rubric-only, phase-level contract-only, or code-evidence paths alone.

**#52 rule (evidence from first-use run):** row cites `core/scoring/client_facing_rubric.py` and signed 5-axis rubric markers. That does **not** satisfy E14. Required missing file:  
`4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md`

**Reason code:** `BLOCKED_MISSING_CONTRACT`

---

## 4. What the gate reads (reconciled from disk — §11 blocker if edited without re-reconcile)

**§11 sign-off is blocked** until the operator confirms this section matches a fresh scoreboard read. Any scoreboard vocabulary change requires amendment revision before implementation.

### 4.1 Source file

`agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`

### 4.2 Column map (Build Sequencer table)

| Col | Field name | Gate use |
|---:|---|---|
| 0 | Agent ID | Candidate identity |
| 1 | Name | Display only |
| 2 | **Runtime status** | **E12 / E13 primary input** |
| 3 | Code evidence | E14 path extraction (secondary); not sufficient alone |
| 4 | Layer | Unchanged (F1 layer bonus) |
| 5 | Stage | Unchanged |
| 6 | **BLOCKERS** | Existing E5–E11 |
| 7 | **TRACK** | Existing E7 |
| 8 | LAST_RUBRIC_SCORE | F3 |
| 9 | LAST_UPDATED | F4 |

### 4.3 Prefix-match rule (mandatory)

Parse column 2 by:

1. Strip whitespace and outer backticks from cell text.
2. Test **prefix match** (`startswith`) against closed/buildable prefix sets — **same discipline as** `scripts/mmi_dispatch.py` (`get_signed_unbuilt`, `get_awaiting_audit`, GATED checks).

**Do not** use exact token equality. Known parser quirk: GATED cells may tokenize as `GATED` plus trailing punctuation; prefix match prevents false negatives.

### 4.4 Closed-state prefix set (E12) — locked 2026-06-20

| Prefix | Live row count | Notes |
|---|---:|---|
| `GATED` | 33 | Phase/control-plane closed rows; includes #72–#83 failure set |
| `GOVERNED_AGENT` | 14 | ES1 built agents; already pre-filtered at Estimator parse today — E12 still applies for contract parity |
| `INFRASTRUCTURE_BUILT` | 1 | #71 Token Usage Tracker — built infra, not next-build |

**Not in E12:** `COMPLETE` — registry/external lane status; handled by existing **E10**.

### 4.5 Buildable-state prefix set (E13) — locked 2026-06-20

| Prefix | Live row count | Dispatcher route |
|---|---:|---|
| `SIGNED_UNBUILT` | 0 | `get_signed_unbuilt()` → MODE: BUILD when non-empty |
| `AWAITING_AUDIT` | 0 | `get_awaiting_audit()` → MODE: AUDIT when non-empty |

When both counts are zero, proven dispatcher emits **`ALL_CLEAR`** (as in first-use run).

### 4.6 Expected post-gate behavior on today's scoreboard

After E12–E14 on live data (2026-06-20):

- Current Estimator eligible pool (E1–E11): **19** candidates.
- After E12–E14: **0** next-build candidates.
- Expected envelope: **`NO_BUILDABLE_CANDIDATES`** + ALL_CLEAR advisory (Section 6) + **`BUILDABILITY_EXCLUSIONS`** listing all dropped rows (Section 7).

This **agrees** with dispatcher ALL_CLEAR; it does not contradict it.

### 4.7 Non-opinion discipline

Gates add **no new weight**, **no semantic quality judgment**, and **no new opinion axis**. They read recorded lifecycle and on-disk contract facts only.

---

## 5. ALL_CLEAR advisory flag

### 5.1 Trigger (pinned source)

When **`--verify-text`** from `python3 scripts/mmi_dispatch.py --verify` contains:

```text
current task: MODE: ALL_CLEAR
```

the Estimator **must** prepend:

```text
ADVISORY_ONLY: dispatcher queue is ALL_CLEAR — no active dispatcher route is currently open; Estimator output is comparison-only and not next-build direction.
```

**Do not** independently re-derive ALL_CLEAR from scoreboard row counts. **Verify-text is the only ALL_CLEAR source** for this flag.

### 5.2 Behavior when triggered

- If any candidates remain in the **next-build ranking** after E12–E14: still emit `SCORED_CANDIDATES` **with** the advisory prefix.
- If E12–E14 exclude **all** candidates: emit **`NO_BUILDABLE_CANDIDATES`** (Section 7) **with** the advisory prefix — **not** a ranking of built/blocked rows.

### 5.3 Authority boundary (unchanged)

Advisory text is **not** authorization, selection, routing, or build approval. Matt selects; dispatcher routes; Estimator ranks eligible buildable candidates only.

---

## 6. Output vocabulary (additions)

### 6.1 Primary scoring outcomes (unchanged)

- `SCORED_CANDIDATES`
- `STATE_INCOMPLETE_CANNOT_SCORE`

### 6.2 Added advisory / buildability outcomes

| Label | When emitted |
|---|---|
| `ADVISORY_ONLY: ...` | Prefix when verify-text shows `MODE: ALL_CLEAR` |
| `NO_BUILDABLE_CANDIDATES` | E12–E14 exclude every candidate from next-build ranking |

### 6.3 Exclusion reason codes (per candidate)

| Code | Gate |
|---|---|
| `EXCLUDED_ALREADY_BUILT` | E12 |
| `EXCLUDED_NON_BUILDABLE_STATE` | E13 |
| `BLOCKED_MISSING_CONTRACT` | E14 |

### 6.4 Forbidden tokens (unchanged from parent contract §9)

Never emit as Estimator conclusions:

`SELECTED`, `AUTHORIZED`, `APPROVED`, `RECOMMENDED`, `BUILD_AUTHORIZED`, `COMPLETE`, `SIGNED`, `VERIFIED`, `PASS`, `FAIL`, `PROMOTED`, `NEXT_DECIDED`

Evidence bodies may quote input sources verbatim. Exclusion reason codes above are **not** forbidden — they are exclusion telemetry, not authorization verdicts.

---

## 7. BUILDABILITY_EXCLUSIONS telemetry (new)

When any candidate is excluded by E12–E14, Estimator **must** emit a read-only stdout section:

```text
BUILDABILITY_EXCLUSIONS
excluded_count: N
---
candidate_id: #72
name: PhishIntelAgent
gates: E12
reason: EXCLUDED_ALREADY_BUILT
runtime_status_prefix: GATED
---
candidate_id: #52
name: Plain-English Explanation
gates: E13,E14
reason: BLOCKED_MISSING_CONTRACT
runtime_status_prefix: DETECTOR_FUNCTION
missing_contract: 4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md
```

**Rules:**

- Emit **before** `SCORED_CANDIDATES` or `NO_BUILDABLE_CANDIDATES`.
- Emit even when `NO_BUILDABLE_CANDIDATES` (so exclusions are auditable without re-derivation).
- Stdout only. No file writes. No scoreboard/registry mutation.

---

## 8. Falsifiable acceptance tests (added to Estimator suite)

Implementation admissible for operator review **only if T1–T34 all pass.**

| ID | Test | Pass condition |
|---|---|---|
| T28 | Built excluded | No `GATED` / `GOVERNED_AGENT` / `INFRASTRUCTURE_BUILT` row appears in next-build ranking |
| T29 | Non-buildable state excluded | `DETECTOR_FUNCTION` (and other non-buildable prefixes) excluded with `EXCLUDED_NON_BUILDABLE_STATE` |
| T30 | Missing contract caught | #52 fixture: `BLOCKED_MISSING_CONTRACT`; not rank #1 in buildable set |
| T31 | ALL_CLEAR advisory | Verify-text with `MODE: ALL_CLEAR` → output carries `ADVISORY_ONLY` prefix |
| T32 | No buildable candidates | When gates exclude all → `NO_BUILDABLE_CANDIDATES`; no ranked built/blocked rows |
| T33 | Agreement check | Estimator buildable set contains no row whose runtime status prefix is in E12 closed set; buildable set ⊆ E13 prefix set |
| T34 | Worth unchanged within buildable | Among buildable candidates, weighted-sum order matches pre-gate scoring order (gate filters only) |

**First-use regression (live scoreboard fixture or frozen 2026-06-20 snapshot):**

- **#72, #78, #79, #80 must not** appear in next-build ranking.
- **#52 must not** be buildable rank #1.
- Re-running today's comparison must yield **DISAGREE → AGREE or honest empty** (ALL_CLEAR + `NO_BUILDABLE_CANDIDATES`), not a false next-build pointer.

**Prior tests T1–T27 must still pass** (determinism, weights, NULL semantics, zero-writes, forbidden tokens).

---

## 9. What this amendment must not do

- Must **not** change the weighted-sum formula or locked weights (MMI-DEC-039).
- Must **not** add semantic/quality judgment — gates read lifecycle and on-disk contract facts only.
- Must **not** give the Estimator selection, authorization, routing, or build approval power — **ranks only.**
- Must **not** write state, scoreboard, registry, dispatcher output, or any file — **stdout only.**
- Must **not** feed dispatcher routing or enable registry-fed routing.
- Must **not** unlock AUTH-5 or autonomous selection.
- Must **not** soften E12–E14 into score penalties — **exclude only.**

---

## 10. Relationship to the proven engine

This amendment makes the Estimator **agree with scoreboard-lifecycle routing on facts** (done vs open, buildable vs blocked) while keeping independence on **worth** (which open, buildable item scores highest).

| Engine | Role |
|---|---|
| Proven dispatcher | Authority on **whether** a route is open (`BUILD` / `AUDIT` / `ALL_CLEAR`) |
| Estimator (after amendment) | Ranks **within** E13 buildable set only; flags advisory under ALL_CLEAR |
| Architect Mode A | Separate buildability check for blueprint emission (contract + flow) |
| Matt | Selects; authorizes build; signs contracts |

Disagreement between Estimator and dispatcher after this amendment should mean **worth-ordering among genuinely buildable work**, not noise (done-vs-not-done, missing-contract mirage).

**Accountability return-path:** If the gate proves too strict (excludes genuinely buildable work) or too loose (lets a closed row through), record failure evidence and revise **this amendment** or scoreboard vocabulary — same evidence-driven loop.

---

## 11. Sign-off

**§11 SIGNED — Matt Nichol, June 20 2026.**

- [x] I approve this amendment as written.
- [x] I separately authorize implementation in `scripts/mmi_estimator.py` and tests only.

Confirmed: gates E12–E14 read living scoreboard lifecycle state and on-disk Agent Design Contract paths; filter only; no formula change; no weight change; no NULL semantics change; no Estimator authority expansion; no writes; no routing; no selection; no build authorization; no AUTH-5 unlock; no registry-fed routing.

Closed-state set and buildable-state set reconciled against live scoreboard and locked in Section 4.4–4.5: **yes**

First-use regression (2026-06-20 failure set) addressed in acceptance tests: **yes** (T28–T34 pass at `0d3620f`)

---

## 12. File placement

**Signed location:** `mmi/MMI_ESTIMATOR_BUILDABILITY_GATE_AMENDMENT.md`

**Superseded draft pointer:** `mmi/MMI_ESTIMATOR_BUILDABILITY_GATE_AMENDMENT_DRAFT.md` (retained for history; do not treat as authority)

---

**End. §11 SIGNED. Implemented at `0d3620f`.**
