# Next-Action Decision Rubric — Binary Calibration Amendment

**Document ID:** `NEXT_ACTION_RUBRIC_BINARY_CALIBRATION_AMENDMENT`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Pre-build gate clean 0/0 (`audit_outputs/next_action_rubric_binary_calibration_amendment_20260622T012415Z.md`; packet SHA256 `bb35585e8de3fb46d4507304d06ab8b23737a00150ab9052c4ac94dc07f5bdc6`). Locks D20–D24 and §3.A binary calibration. Authorizes mandatory §3.A use in session + **drafting** read-only `scripts/mmi_next_action_rubric.py` only. Authorizes **no** script build without separate build authorization, **no** routing, **no** PM Voice selection language, **no** Estimator weight changes, **no** AUTH-5.

**Amends:** `4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md` (§11 signed 2026-06-04; §12 D13-rev signed 2026-06-08; §3.6 pointer updated 2026-06-21)

**Related (does not amend by signature here):** `mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md` (§11 signed; F1–F6 weights locked MMI-DEC-038/039); `mmi/MMI_ESTIMATOR_BUILDABILITY_GATE_AMENDMENT.md` (E12–E14, MMI-DEC-045)

**Owner:** Matt Nichol

**Lane:** Governance / tactical ranking calibration

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** `scripts/mmi_next_action_rubric.py` **BLOCKED** until separate operator build authorization (MMI-DEC-095 §11 locks spec + §4 script contract only).

---

## §0 Purpose

The parent Next-Action Decision Rubric (§3) defines five axes in prose. Prose scoring invites session variance and assistant score inflation. This amendment adds **§3.A Objective binary calibration (0–2)** under the **existing signed axis names**. Each point level is earned only when **disk-truth predicates** pass. If predicates conflict or evidence is missing, the axis scores **0** and records an **`UNMEASURED`** reason — never guessed.

This amendment also locks the **Estimator pool boundary**: what Layer 2 may supply vs what Layer 4 may score. The rubric still **ranks**; Matt **selects** (parent D2). No amendment language changes that.

---

## §1 Scope

### In scope

- Additive §3.A binary rules for: `leverage`, `risk_reduction`, `evidence_strength`, `future_cost`, `reversibility`.
- Estimator ↔ rubric boundary (candidate pool, exclusions, ALL_CLEAR behavior).
- Ambiguity / tie rules for machine and human scoring.
- Optional future read-only script contract shape (stdout envelope only).
- Minor §7 output label clarification (axis keys for machine logs).

### Out of scope

- Estimator F1–F6 weight or formula changes (separate Estimator contract path).
- PM Voice “strongest match”, “accept lane”, or auto-posture (forbidden by PM Voice contract).
- Replacing scoreboard candidate generation (D13-rev stands).
- Client-facing or email rubrics.
- Cryptographic decision-log formats or git-hash drift probes.
- §11 signature on parent spec retroactively — this is a **revision amendment**, not a rewrite of parent §2–§5.

---

## §2 Locked amendment decisions (§11 signed 2026-06-21)

| # | Decision | Locked value |
|---|---|---|
| D20 | Calibration method | **Binary disk-truth only.** Each axis is 0, 1, or 2. No half-points, no “usually”, no assistant judgment fill-in. |
| D21 | Axis vocabulary | **Parent §3 names unchanged:** `leverage`, `risk_reduction`, `evidence_strength`, `future_cost`, `reversibility`. No rename to “execution risk” or “evidence density”. |
| D22 | `future_cost` polarity | **Parent inversion preserved.** Higher score = **lower** future cost **after the action completes**. Rules below score the action’s debt effect, not “how bad skipping feels”. |
| D23 | Estimator boundary | Estimator = **structural readiness + buildability telemetry**. Rubric = **tactical rank among Step-2 candidates**. Estimator rank is **not** selection. `NO_BUILDABLE_CANDIDATES` does **not** empty the rubric option set. |
| D24 | Machine scoring | Future `scripts/mmi_next_action_rubric.py` (if built) must be **read-only**, reuse parent §7 envelope, emit **`UNMEASURED(axis: reason)`** on ambiguity, and forbid `RECOMMENDED`, `SELECTED`, `NEXT_DECIDED`. |

---

## §3 Estimator pool boundary (Layer 2 ↔ Layer 4)

### 3.1 What Estimator owns

Per `mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md` and buildability amendment (E12–E14):

| Estimator output | Meaning for rubric |
|---|---|
| `SCORED_CANDIDATES` | Buildable-now rows (`SIGNED_UNBUILT*`, `AWAITING_AUDIT*`) with F1–F6 scores — **one input slice** for rubric when operator session is build-focused |
| `BUILDABILITY_EXCLUSIONS` | Rows excluded with reason codes — rubric **must respect hard exclusions** in §3.3 |
| `NO_BUILDABLE_CANDIDATES` | No buildable-now rows — **does not** mean “no tactical options” |
| `SCORED_FEEDSTOCK` / BOR feedstock | ALL_CLEAR advisory ranking — **not** build authorization; rubric may consume as candidate hints when operator authorizes unpark |
| F3 `LAST_RUBRIC_SCORE` on scoreboard | **Optional prior cycle signal** — rubric may write scores back to scoreboard only via **operator** update, never via script auto-write |

### 3.2 What rubric owns (parent D13-rev)

Default Step-2 candidates (3–7) come from:

1. **Scoreboard-generated hybrid** — `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`: empty `BLOCKERS`, `TRACK` match, dependency gates satisfied, build-order respect.
2. **Operator/session additions** — explicit single-action candidates (including **`do nothing`**, **hold**, **admin reconcile**, **contract draft**) when scoreboard alone does not fit.
3. **NOT** from Estimator total score alone — Estimator orders buildable telemetry; rubric orders **tactical fit** among named actions.

### 3.3 Hard rubric pool exclusions (disk-enforced)

A candidate **must not** enter the rubric scored set if:

| Condition | Reason code | Notes |
|---|---|---|
| Estimator E12 `EXCLUDED_ALREADY_BUILT` (`GATED`, `GOVERNED_AGENT`, `INFRASTRUCTURE_BUILT`) | `RUBRIC_EXCLUDE_E12_CLOSED` | Exception: operator explicitly adds **`do nothing`** or **audit-only review** as its own Step-2 row (parent D19) |
| Candidate has no **single executable action string** | `RUBRIC_EXCLUDE_NON_ACTION` | “Fix everything” is not one candidate |
| Candidate action references files outside repo root without path on disk | `RUBRIC_EXCLUDE_PHANTOM_PATH` | No speculative surfaces |
| More than 7 candidates after merge | `RUBRIC_EXCLUDE_TRIM` | Operator trims to 7 before score (parent D4) |

A candidate **may** enter the rubric scored set even when Estimator buildability excludes it, if:

| Condition | Example |
|---|---|
| Operator unparked feedstock or named lane | `#1` / `#3` contract draft while `BLOCKED_MISSING_CONTRACT` |
| Admin / drift task with explicit action | BOR reconcile, handshake block update |
| Session constraint candidate | “Hold ALL_CLEAR; no lane” per D19 |

### 3.4 ALL_CLEAR interaction (critical)

When `scripts/mmi_dispatch.py --verify` reports **`MODE: ALL_CLEAR`** and Estimator emits **`NO_BUILDABLE_CANDIDATES`**:

- Estimator advisory stands: **no lifecycle-routeable build row**.
- Rubric **still runs** if Step 2 has ≥3 candidates (contract draft, hold, cleanup, research intake, unpark).
- Rubric **must not** treat highest Estimator F1/F4 as “next build” when E12/E13 excluded the row.

This boundary prevents the “what is next?” nightmare where evidence-rich **GATED** rows outrank unparked spine work.

---

## §3.A Objective binary calibration (amends parent §3)

**Scoring unit:** one **candidate action** tied to a **primary artifact scope** (scoreboard `#NN`, named file set, or operator-declared admin task id).

**Evidence sources (allowlist):**

- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`
- `4. Product_Roadmap/*Agent*Design*Contract*.md` and `docs/mmi/contracts/*.md` (contract review drafts)
- `audit_outputs/*.md` (gate receipts)
- `tests/test_*` and `tests/fixtures/**` (committed)
- `scripts/mmi_*.py`, `mmi/*.md`, `PROJECT_HANDSHAKE.md`, `mmi/BLUEPRINT_OF_RECORD.md`
- `mmi/MMI_DECISION_LOG.md`, `decision_cycles_log.md`
- Dispatcher verify text (`scripts/mmi_dispatch.py --verify`) when captured in session OBSERVE step

**Global ambiguity rule:** If two predicates for the same axis disagree, score **0** and log `UNMEASURED(<axis>: conflicting_disk_truth)`.

---

### §3.A.1 `leverage` — systemic unlock

Measures how much **future scoreboard work** the action unlocks. Count **downstream** rows only (same mechanical rule as Estimator `_downstream_unlock_count`: scoreboard rows whose `BLOCKERS` cell contains `DEPENDS_ON:#<id>` for this candidate’s numeric id).

| Score | Disk-truth predicate |
|---|---|
| **0** | Downstream count = **0** |
| **1** | Downstream count = **1** |
| **2** | Downstream count ≥ **2** |

**Non-scoreboard actions** (admin task, hold, do nothing): downstream count = 0 → **leverage 0** unless operator attaches a **written dependency list** in Step 2 OBSERVE citing exact scoreboard `#` ids — then count applies to that list only.

---

### §3.A.2 `risk_reduction` — recorded risk removed

Measures **risk removed** by completing the action — **not** “risk of executing the action”. Parent §3.2 semantics preserved.

**Recorded risk artifact** (any one qualifies as “signal present”):

- `audit_outputs/*` with `VERDICT: FAIL` or blocking lines naming the scope
- Dispatcher verify output with `drift: N BLOCK` where N > 0 and BLOCK text references the scope
- `tests/test_mmi_authority_escalation_probe.py` failure or probe stdout `AUTHORITY_INVARIANT_BREACH` referencing the scope
- Open `MMI-DEC-*` **Required follow-up** line naming the scope (grep decision log)

| Score | Disk-truth predicate |
|---|---|
| **0** | **No** recorded risk artifact references this action’s primary scope |
| **1** | Exactly **one** recorded risk artifact references the scope (warning-only gate counts as 1 if `warnings=` > 0 and blocking = 0) |
| **2** | **Two or more** distinct recorded risk artifacts reference the scope **OR** one artifact with **blocking > 0** on the scope **OR** verify `drift: N BLOCK` with N > 0 tied to scope |

**Control-plane edit actions** (`scripts/mmi_*.py`): if action completes with probe path documented (`tests/test_mmi_authority_escalation_probe.py` exists on disk) and verify returns PASS after change, risk_reduction may be **1** when fixing a recorded PMV/Estimator/dispatcher mismatch in `MMI_DECISION_LOG.md` — **2** only if multiple BLOCK-class artifacts existed pre-fix.

---

### §3.A.3 `evidence_strength` — verification blueprint on disk

Measures **strength of the case** from **committed verification artifacts**, not operator instinct (parent §3.3).

Let **contract path** = resolved Agent Design Contract path (Estimator order: scoreboard cell → governance map → architect manifest → `docs/mmi/contracts/` review draft if operator declared in OBSERVE).

| Score | Disk-truth predicate |
|---|---|
| **0** | No contract file on disk for scope **and** no committed `tests/test_*` whose path or docstring references `#NN` or primary module **and** no `audit_outputs/*gate*` receipt for scope |
| **1** | **Exactly one** of: (a) contract/review draft file exists (`**Status:**` contains `DRAFT` or `UNSIGNED`), (b) unsigned contract with §0–§2 structure present, (c) committed test file references scope but no gate receipt |
| **2** | **Any** of: (a) parent §11-signed contract on disk (`**Status:**` contains `SIGNED`, not `UNSIGNED`), (b) `audit_outputs/*` gate receipt with `0 blocking` / `0 warnings` (or project-standard 0/0 verdict) naming scope, (c) committed pytest file **and** passing test run recorded in session OBSERVE for that file |

**Forbidden:** assistant confidence, chat history, or “we ran it last week” without artifact path in OBSERVE.

---

### §3.A.4 `future_cost` — inverted (debt after action)

**Polarity:** **2 = action reduces future cost/complexity**; **0 = action increases ongoing cost**.

| Score | Disk-truth predicate (effect **after** action completes) |
|---|---|
| **0** | Action adds a **new** manual tracking surface not in `MASTER_INDEX.md` / decision log template **or** leaves duplicate truth (two handshake blocks both “live”) **or** adds unsigned spec with no closeout path |
| **1** | Action edits **one** tracking file (`PROJECT_HANDSHAKE.md`, `mmi/MMI_CURRENT_STATE.md`, `mmi/BLUEPRINT_OF_RECORD.md`, or one scoreboard row) with **no** new artifact class |
| **2** | Action closes a **documented open drift** entry: verify PASS after fix **or** MMI-DEC required follow-up marked done in same cycle **or** removes stale feedstock/BOR line that caused Estimator/PMV mismatch (cite DEC id in OBSERVE) |

**Leaving work unbuilt** is not scored on this axis — score the **candidate action** (e.g. “reconcile BOR v6 hold-only feedstock”), not the counterfactual.

---

### §3.A.5 `reversibility` — blast radius on disk

| Score | Disk-truth predicate |
|---|---|
| **0** | Action requires **§11 signature** on a spec **or** scoreboard lifecycle promotion (`SIGNED_UNBUILT`, `GATED`, `GOVERNED_AGENT`, `SIGNED_CONTRACT`) **or** edits **≥3** distinct paths under `scripts/` in one action |
| **1** | Action edits **2–3** repo files total **or** one shared `mmi/*.md` + one `scripts/mmi_*.py` **without** lifecycle promotion |
| **2** | Action is **net-new single file** under `tests/` or `docs/mmi/contracts/` (review draft only) **or** **single-file** edit with no scoreboard/registry/decision-log lifecycle change |

**Git rollback test (documentation only):** reversibility **2** requires operator OBSERVE note that `git checkout -- <paths>` restores pre-action state without orphan registry/scoreboard references.

---

### §3.A.6 Special candidate: `do nothing` (parent D19)

When Step 2 includes **do nothing** / **hold ALL_CLEAR**:

| Axis | Default disk-truth scores |
|---|---|
| `leverage` | 0 |
| `risk_reduction` | 0 if no new BLOCK artifacts since last OBSERVE; 1 if verify BLOCK present and hold defers fix |
| `evidence_strength` | 0 |
| `future_cost` | 1 (neutral hold) |
| `reversibility` | 2 |

Worked total example remains valid: **0 + 0 + 0 + 1 + 2 = 3** (parent D19 range 3–4 when risk_reduction = 1).

---

## §4 Machine scoring contract (future script — not authorized until §11)

If Matt authorizes implementation after this amendment signs:

| Property | Requirement |
|---|---|
| Script | `scripts/mmi_next_action_rubric.py` (read-only, stdout only) |
| Input | Step-2 candidate list (JSON stdin or CLI flags) + repo root |
| Parsers | Reuse or import Estimator scoreboard/contract path resolution; do not duplicate ad-hoc regex |
| Output envelope | `SCORED_NEXT_ACTIONS` + per-candidate axis integers + `TOTAL` + `UNMEASURED` lines |
| Forbidden stdout tokens | Same class as Estimator: `RECOMMENDED`, `SELECTED`, `NEXT_DECIDED`, `AUTHORIZED`, `BUILD_AUTHORIZED` |
| Writes | **None** — no scoreboard, registry, BOR, or decision log mutation |

PM Voice may **relay** rubric stdout as cited engine output; PM Voice must **not** label any row “strongest match” or prompt accept/execute.

---

## §5 Amended §7 output format (machine keys)

Parent §7 human labels remain. Machine logs **should** use canonical axis keys:

```text
ACTION: Authorize contract review draft #3 Risk Triage
  leverage:          0
  risk_reduction:    1
  evidence_strength: 1
  future_cost:       2
  reversibility:     2
  TOTAL:             6
  UNMEASURED:        none
```

Parent shorthand `Risk:` in prose output maps to **`risk_reduction`** in logs (not “execution risk”).

---

## §6 Failure modes (amendment-specific)

| Failure mode | Mitigation |
|---|---|
| **Estimator ↔ rubric collapse** | Treating Estimator rank #1 as Matt’s action — forbidden by §3.4 and parent D2 |
| **Execution risk mis-axis** | Scoring “danger of editing mmi_pm_voice.py” on `risk_reduction` — wrong axis; use `reversibility` + recorded-risk rules on `risk_reduction` |
| **GATED leverage inflation** | E12 rows excluded from build pool but scored high leverage — §3.3 hard exclude unless audit-only candidate |
| **Phantom evidence 2** | Gate receipt exists but for different `#` — ambiguity rule → 0 + UNMEASURED |
| **Decision laundering** | Logging “rubric chose 8/10” — Step 9 still `SELECTED: operator-chosen` |

---

## §7 Audit / gate requirements

- This amendment file runs through `audit_tools/complete_gate.py` before §11 signature (worker manifest names this file + parent spec read).
- Implementation of `mmi_next_action_rubric.py` requires **separate** build authorization after amendment §11 — not implied by amendment signature alone.
- No change to parent §9 cycle-log gate policy (D17).

---

## §8 Open questions (remaining at §11 signature)

1. Should `docs/mmi/contracts/*.md` review drafts enter Estimator E14 resolution order automatically, or remain operator-declared in OBSERVE only?
2. Should rubric scores feed scoreboard `LAST_RUBRIC_SCORE` column via manual operator edit template only, or stay in `decision_cycles_log.md` exclusively (D15)?
3. Minimum OBSERVE capture for admin tasks (handshake/BOR reconcile) — one-line file list sufficient?

---

## §9 Sign-off — SIGNED 2026-06-21

Signed by Matt Nichol on 2026-06-21 after pre-build gate clean 0/0 (`audit_outputs/next_action_rubric_binary_calibration_amendment_20260622T012415Z.md`). Locks D20–D24 and §3.A. Makes §3.A the mandatory calibration method for tactical rubric use in session. Parent §3 prose remains authoritative for axis **meaning**; §3.A adds disk-truth rules without deleting parent definitions.

### What §11 signature authorizes

1. Lock D20–D24.
2. Mandatory §3.A binary calibration for session tactical scoring.
3. Drafting (not auto-building) read-only rubric script per §4 when Matt authorizes build lane separately.

### What §11 signature does **not** authorize

- Matt selection by total score (parent D2 stands)
- Estimator F1–F6 weight changes
- PM Voice accept/execute prompts
- Scoreboard or BOR auto-mutation
- Replacing D13-rev candidate generation
- Building `scripts/mmi_next_action_rubric.py` without separate build authorization

### Sign-off line

> Matt Nichol June 21st 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

---

**End of amendment. §11 in force as of 2026-06-21 (MMI-DEC-095).**
