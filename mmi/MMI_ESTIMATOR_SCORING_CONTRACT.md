# MMI Estimator — Scoring Contract

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Build authorized for `scripts/mmi_estimator.py` only (Mode A stdout-only). Does **not** authorize Architect, PM, Superintendent builds, or Blueprint authoring.

**Classification:** `SIGNED_CONTRACT` · Crew role: Estimator (foundation)

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent model:** Five-role crew operating model (Estimator / Architect / Superintendent / PM / Blueprint of Record)

**Date:** 2026-06-20

---

## 1. Purpose

The **Estimator** is a read-only arithmetic engine that scores incomplete build candidates from a fixed input manifest. It ranks by pure weighted sum. It does **not** select, authorize, recommend, or route.

**Two outputs only:**

1. `SCORED_CANDIDATES` — ordered list with per-factor breakdown, weights, total, tie-break trace
2. `STATE_INCOMPLETE_CANNOT_SCORE` — missing or conflicting inputs named; no semantic fallback

---

## 2. Scope

### In scope (this build slice)

- **Step 1 (crew adoption recording):** Place and §11-sign all five crew contract artifacts if absent on disk (operator dispatch 2026-06-20)
- `scripts/mmi_estimator.py` Mode A (stdout only, zero file writes at runtime)
- Acceptance tests T1–T13 (§16); fixtures are static inputs under `tests/fixtures/mmi_estimator/` only

### Out of scope

- Superintendent verification role (separate contract)
- Architect / PM / Blueprint builds
- Dispatcher edits, registry-fed routing, scoreboard writes
- AUTH-5 autonomous selection
- Mode B persistence

---

## 3. Locked design decisions

| ID | Decision |
|---|---|
| E-D1 | Scoring policy: **PURE WEIGHTED SUM over measured factors only** |
| E-D2 | Measured factors are **0–10** integers; missing/unavailable sources emit **`NULL(no_data: reason)`** — never numeric |
| E-D3 | **Locked weights (§11):** W1=30, W2=25, W3=20, W4=10, W5=10, W6=5 (sum 100) — owner policy; not code-only tunables |
| E-D4 | `total_measured_score = sum(measured_Fi * Wi) / 10` — NULL factors excluded; maximum 100 when all six factors measured at 10 |
| E-D4a | **Measured zero ≠ NULL:** a factor that reads real input and computes zero emits `0`; absent/empty/unresolved source emits `NULL` |
| E-D4b | NULL is never converted to `0`, never a negative penalty, never hidden in weighted output |
| E-D4c | Coverage reported separately: `coverage: N/6`, `coverage_status`, `dark_factors`, top-level dark-factor summary |
| E-D5 | Eligibility gates E1–E11 **exclude** candidates; never score-low |
| E-D6 | Agent Health Score is factor F6 only; **does not** dominate (W6=5 cap) |
| E-D7 | Forbidden tool verdict tokens per §9 — never emitted |
| E-D8 | Refresh = re-read manifest; no learning between runs |

---

## 4. Factor definitions

| Factor | Name | Source | 0–10 rule |
|---|---|---|---|
| F1 | Readiness | Lifecycle + recorded scoreboard maturity fields | §5.1 formula (cap 10) |
| F2 | Dependency unlock | Scoreboard `DEPENDS_ON` graph | **Measured** when dependency graph populated: `min(10, downstream_count)`; measured `0` when graph populated and count=0; **NULL** when graph not populated or registry row |
| F3 | Rubric | `LAST_RUBRIC_SCORE` | **Measured** numeric 0–10 when recorded; **NULL** when column absent, empty, or `—` |
| F4 | Evidence completeness | Scoreboard row refs + DEC/INTAKE/indexed artifacts | §5.2 formula (cap 10); **excludes** `mmi/research/`; always measured for eligible rows |
| F5 | Verify cleanliness | Manifest verify snapshot | **Run-hygiene gate only:** BLOCK present → cannot score run; PASS/ABSENT → measured `0` (non-separating) |
| F6 | Health (capped) | Agent Health Score Board | **Measured** `min(10, health_score // 10)` when board present and row linked; **NULL** when board absent or row not linked |

---

## 5. Scoring tables

### 5.1 F1 Readiness — scoreboard rows (cap 10)

Formula: `min(10, max(0, lifecycle_base + code_surface + signed_surface - partial_penalty + layer_breadth))`

| Component | Rule |
|---|---|
| `lifecycle_base` | `SIGNED_UNBUILT`=10, `AWAITING_AUDIT`=9, `DETECTOR_FUNCTION`=4, `SPEC_ONLY`=5, `NOT_STARTED`=3, `GOVERNANCE_DOC_ONLY`=3 |
| `code_surface` | `min(3, distinct (core\|tests)/ path tokens in Code evidence)`; 0 if research path present |
| `signed_surface` | +2 if row cites §11, Agent Design Contract, or signed spec/rubric/contract markers |
| `partial_penalty` | -1 if runtime status cell contains `(partial` |
| `layer_breadth` | BREADTH track only: Layer 1 Command +2; Layers 2–4 +1; else 0 |

Registry rows: fixed table — `BUILD_AUTHORIZED`=10, `SIGNED_CONTRACT`=7, `DRAFT_CONTRACT`=4, else 3.

Legacy one-line table (superseded by formula for scoreboard rows):

| Signal | F1 |
|---|---|
| `SIGNED_UNBUILT` | 10 |
| `AWAITING_AUDIT` | 9 |
| Registry `BUILD_AUTHORIZED` | 10 |
| Registry `SIGNED_CONTRACT` | 7 |
| `DETECTOR_FUNCTION` + empty blockers | see formula |
| `SPEC_ONLY` + `NEEDS_SIGNED_CONTRACT` | 5 |
| Other eligible incomplete | 3 |

### 5.2 F4 Evidence — scoreboard rows (cap 10)

Deterministic count from recorded refs only:

| Source | Count rule |
|---|---|
| Code paths | `min(4, distinct core/ or tests/ tokens)` — **excluded** if code evidence cites `mmi/research/` |
| Product roadmap | +1 per distinct `4. Product_Roadmap/*.md` token |
| Signed markers | +1 if §11 or signed contract markers in row |
| Commit hash | +1 if `LAST_UPDATED` contains 40-char hex |
| Decision log | +1 per `#N` agent id mention in `MMI_DECISION_LOG.md` (max +2) |

Registry rows: count `source_evidence` list entries (cap 10).

### 5.3 NULL semantics and coverage (2026-06-20 recalibration)

| Rule | Requirement |
|---|---|
| N-1 | Measured zero is not missing data |
| N-2 | NULL is not numeric; never coerced to `0` or negative penalty |
| N-3 | NULL excluded from `total_measured_score` and per-candidate `weighted:` lines |
| N-4 | Each NULL factor must name reason: `NULL(no_data: ...)` |
| N-5 | Per candidate: `coverage: N/6`, `dark_factors:`, `coverage_status:` |
| N-6 | Rankings with dark factors are provisional; output includes top-level dark-factor summary |
| N-7 | Research-sourced-only inputs remain excluded; never scored as numeric |

**Coverage status thresholds:**

| Status | Rule |
|---|---|
| `FULL` | 6/6 factors measured |
| `PARTIAL` | 4–5/6 factors measured |
| `LOW_COVERAGE_PROVISIONAL` | ≤3/6 factors measured |

NULL does not raise or lower score; it prevents silent full-measurement appearance.

### 5.4 Tie-breakers (fixed order after total)

1. Higher `total_measured_score`
2. Higher `coverage_count` (measured factor count)
3. Higher measured F1 (NULL sorts below any measured value)
4. Higher measured F4
5. Higher measured F3
6. Higher measured F2
7. Lower lexicographic `candidate_id`

Output must include `separation:` line naming recorded inputs used.

---

## 6. Input manifest (reconciled 2026-06-20)

**Manifest reconciled:** YES

Verified on disk at `/home/socialarchitect/northstar`:

| Input | Path | Role |
|---|---|---|
| Task registry | `mmi/MMI_TASK_REGISTRY.yaml` | Registry-sourced candidates |
| Scoreboard | `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` | Agent-row candidates, blockers, deps, health |
| Gate registry | `mmi/MMI_GATE_REGISTRY.md` | Context; gate inventory reference |
| Decision log | `mmi/MMI_DECISION_LOG.md` | F4 evidence refs |
| Intake records | `mmi/MMI_INTAKE_RECORDS.md` | F4 evidence refs |
| Contradiction report | `scripts/mmi_contradiction_report.py` stdout | Advisory envelope only; not routing |
| Verify output | `scripts/mmi_dispatch.py --verify` | **Reference only** — human snapshot or cached text; tool does not subprocess dispatcher |
| Git | `git rev-parse HEAD` + `git status --porcelain` | Evidence hash / dirty-tree signal for F4 |
| Health source | Scoreboard § Agent Health Score Board | F6 only |
| Current state | `MMI_CURRENT_STATE.md` | Context only — **not** scoring authority |

**Substitutions / notes:**

- Both task registry **and** scoreboard are used (both exist; not either/or).
- Worker completion packets: no fixed directory; evidence via DEC/INTAKE/commit refs in decision log.
- `4. Product_Roadmap/*Contract*.md` scan deferred to Superintendent contract; Estimator uses scoreboard row state only.

**Global cannot-score triggers:**

- Scoreboard file missing or unparseable
- Task registry missing or unparseable
- Duplicate `candidate_id` in merged candidate set

---

## 7. Eligibility gates E1–E11

Candidates failing any gate are **excluded** (not scored).

| Gate | Rule |
|---|---|
| E1 | Global manifest minimum readable (scoreboard + task registry) |
| E2 | `candidate_id` present |
| E3 | Runtime status not `merged` |
| E4 | Runtime status not `RECLASSIFY` |
| E5 | Scoreboard `BLOCKERS` empty |
| E6 | All `DEPENDS_ON:#N` satisfied on scoreboard |
| E7 | `TRACK` equals active track (default `BREADTH`) |
| E8 | No `NEEDS_REAL_DATA` in blockers |
| E9 | No `NEEDS_STAGE_B_AUTH` in blockers |
| E10 | Registry tasks: status not `COMPLETE` |
| E11 | No `NEEDS_BUILD_AUTH` in blockers |
| E12 | Not already built — column-2 prefix in closed set (`GATED`, `GOVERNED_AGENT`, `INFRASTRUCTURE_BUILT`) |
| E13 | Buildable lifecycle required — column-2 prefix in buildable set (`SIGNED_UNBUILT`, `AWAITING_AUDIT`) only |
| E14 | Agent Design Contract resolvable on disk — mandatory exclude if absent (`BLOCKED_MISSING_CONTRACT`) |

Buildability gates E12–E14 are defined in `mmi/MMI_ESTIMATOR_BUILDABILITY_GATE_AMENDMENT.md` (§11 signed 2026-06-20, MMI-DEC-045). Applied before scoring; excluded candidates are not scored low — they are excluded.

---

## 8. Output envelope

### SCORED_CANDIDATES

```text
SCORED_CANDIDATES
candidate_count: N
weights: F1=30 F2=25 F3=20 F4=10 F5=10 F6=5
ranking computed with dark factors present
factor_coverage_summary:
  F1 measured: N / NULL: N
  ...
dark_factor_causes:
  F2: dependency graph not populated for scoreboard rows
  F3: LAST_RUBRIC_SCORE empty / placeholder
  F6: health board absent or row not linked
---
candidate_id: ...
source: scoreboard|registry
factors:
  F1=8
  F2=NULL(no_data: dependency graph not populated for scoreboard rows)
  F3=NULL(no_data: LAST_RUBRIC_SCORE empty)
  F4=1
  F5=0
  F6=NULL(no_data: health row not linked)
coverage: 3/6
dark_factors: F2,F3,F6
weighted: W1=24.00 W4=1.00 W5=0.00
total_measured_score: 25.00
coverage_status: LOW_COVERAGE_PROVISIONAL
separation: ...
tie_break: ...
```

Top-level dark-factor summary appears when any candidate has NULL factors.

### STATE_INCOMPLETE_CANNOT_SCORE

```text
STATE_INCOMPLETE_CANNOT_SCORE
missing_or_conflicting:
  - ...
```

### Buildability additions (MMI-DEC-045)

| Label | When emitted |
|---|---|
| `ADVISORY_ONLY: ...` | Prefix when verify-text shows `MODE: ALL_CLEAR` |
| `NO_BUILDABLE_CANDIDATES` | E12–E14 exclude every candidate from next-build ranking |
| `BUILDABILITY_EXCLUSIONS` | Telemetry block listing excluded candidates and reason codes |

Exclusion reason codes: `EXCLUDED_ALREADY_BUILT` (E12), `EXCLUDED_NON_BUILDABLE_STATE` (E13), `BLOCKED_MISSING_CONTRACT` (E14).

Primary scoring outcomes (`SCORED_CANDIDATES`, `STATE_INCOMPLETE_CANNOT_SCORE`) unchanged.

---

## 9. Forbidden tokens (tool output)

Never emit as Estimator conclusions: `SELECTED`, `AUTHORIZED`, `APPROVED`, `RECOMMENDED`, `BUILD_AUTHORIZED`, `COMPLETE`, `SIGNED`, `VERIFIED`, `PASS`, `FAIL`, `PROMOTED`, `NEXT_DECIDED`.

Evidence bodies may quote these verbatim when citing inputs.

---

## 10. Authority boundaries

- Matt selects; Estimator ranks
- AUTH-5 remains BLOCKED
- Registry-fed routing remains FORBIDDEN
- No dispatcher import or subprocess
- No scoreboard / registry / gate / decision-log writes

### 10.1 Weight policy (owner authority)

Estimator weights are **owner-defined scoring policy**, not implementation convenience constants.

| Rule | Requirement |
|---|---|
| W-1 | Current weights are **locked** by §11 sign-off and `MMI-DEC-038` crew adoption |
| W-2 | `scripts/mmi_estimator.py` `WEIGHTS` must **match** the signed record exactly |
| W-3 | **Forbidden:** silent code-only weight changes, gut calibration, or treating `WEIGHTS` as a normal refactor knob |
| W-4 | Weight changes require **explicit operator instruction** plus **either** (a) contract revision re-signing §11 weights, **or** (b) `MMI-DEC-*` entry recording new weights, rationale, and operator acceptance |
| W-5 | After W-4, code `WEIGHTS` may be updated to match the new signed record only |
| W-6 | Weight changes alter the build-order spine; they are **not** minor implementation tweaks |

**Signed weight record (2026-06-20):** F1=30, F2=25, F3=20, F4=10, F5=10, F6=5.

---

## 11. Sign-off

**§11 SIGNED — Matt Nichol, June 20 2026.**

- Scoring policy: **PURE WEIGHTED SUM**
- Weights: W1=30, W2=25, W3=20, W4=10, W5=10, W6=5 — **locked owner policy** (see §10.1)
- Manifest reconciled: **YES** (§6 locked 2026-06-20)
- Build authorization: **`scripts/mmi_estimator.py` Mode A only** this session
- Architect / PM / Superintendent / Blueprint: signed elsewhere; **not build-authorized** here

---

## 16. Acceptance tests

| Test | Name | Pass condition |
|---|---|---|
| T1 | Determinism | Same fixture root → identical stdout (two runs) |
| T2 | Merged excluded | `merged` row absent from scored set |
| T3 | Reclassify excluded | `RECLASSIFY` row absent |
| T4 | Blockers excluded | Non-empty `BLOCKERS` row absent |
| T5 | Depends excluded | Unsatisfied `DEPENDS_ON` row absent |
| T6 | Cannot-score missing | Missing scoreboard → `STATE_INCOMPLETE_CANNOT_SCORE` |
| T7 | Cannot-score conflict | Duplicate candidate_id → `STATE_INCOMPLETE_CANNOT_SCORE` |
| T8 | Health capped | F6 max contribution ≤ W6×10/10 = 5 points to total at F6=10 |
| T9 | Readiness ordering | Higher F1 sorts above lower when totals tie |
| T10 | Weighted sum | Documented formula matches implementation |
| T11 | Zero writes | Live repo immutable path digests unchanged after run (fixtures are static test inputs only) |
| T12 | No forbidden token | No forbidden verdict as tool output line |
| T13 | Refresh | Input change → different top candidate or total |
| T14 | Signed weights match | Code `WEIGHTS` equals §10.1 / §11 signed record |
| T15 | Top-row separation | Live/fixture detector rows do not collapse solely on old F1=6/F5=10 pattern |
| T16 | Scoreboard F4 wired | Deterministic evidence count from scoreboard row fields |
| T17 | Research excluded | `mmi/research/` paths contribute 0 to F1 code_surface and F4 |
| T18 | Equivalent tie explained | Tied rows include `separation:` showing identical recorded inputs |
| T19 | Measured zero preserved | Populated dependency graph with zero downstream deps → F2=`0`, not NULL |
| T20 | Absent source → NULL | Missing dependency graph / rubric / health source → `NULL(no_data: ...)` |
| T21 | NULL excluded from total | NULL factor contributes exactly 0 to `total_measured_score` |
| T22 | Dark-factor report | Output names every NULL factor and reason; top-level summary when dark |
| T23 | Coverage shown | Each candidate includes `coverage: N/6` |
| T24 | Low-coverage provisional | ≤3/6 measured → `coverage_status: LOW_COVERAGE_PROVISIONAL` |
| T25 | Locked weights unchanged | Code `WEIGHTS` equals §10.1 / §11 signed record |
| T26 | No negative missing-data penalty | Missing data never emits negative numeric factor values |
| T27 | Deterministic NULL output | Same inputs → identical NULL/coverage/score/rank output |
| T28 | Built excluded | No E12 closed-prefix row in next-build ranking |
| T29 | Non-buildable state excluded | Non-buildable prefixes excluded with `EXCLUDED_NON_BUILDABLE_STATE` |
| T30 | Missing contract caught | Missing Agent Design Contract → `BLOCKED_MISSING_CONTRACT`; not rank #1 |
| T31 | ALL_CLEAR advisory | Verify-text with `MODE: ALL_CLEAR` → `ADVISORY_ONLY` prefix |
| T32 | No buildable candidates | All excluded → `NO_BUILDABLE_CANDIDATES`; no ranked built/blocked rows |
| T33 | Agreement check | Buildable set ⊆ E13 prefixes; no E12 closed prefix in buildable set |
| T34 | Worth unchanged within buildable | Pre-gate weighted-sum order preserved among buildable candidates |
