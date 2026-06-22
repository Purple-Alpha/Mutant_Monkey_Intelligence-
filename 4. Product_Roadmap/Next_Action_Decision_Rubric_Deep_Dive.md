# Next-Action Decision Rubric — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-04 by Matt Nichol (Zebra-Comet). **§12 REVISION SIGNED 2026-06-08 by Matt Nichol:** D13 revised for Build Sequencer adoption (Option B, `_Build_Sequencer_Adoption_Consequence_Matrix.md`). Queue ordering authority retired; scoreboard is the canonical candidate generator. D13-rev is now live authority.
**Date:** 2026-05-27
**Owner:** Matt Nichol
**Source-of-truth links:** `think_sheet.md` (existing project-idea rubric — distinct artifact), `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (existing email-explanation rubric — distinct artifact), `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §1.1 (rubrics-are-advisory supersession; this spec inherits and respects that doctrine), `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (canonical candidate generator per D13-rev / §12), `PROJECT_HANDSHAKE.md` (today's one-screen view), `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` (operating mode under which this rubric is exercised). `PROJECT_BUILD_AND_AUDIT_QUEUE.md` **retired** as ordering authority 2026-06-08 (historical read-only).

This document is the spec-first contract for a tactical-layer scoring engine that generates and ranks next-action candidates without deciding among them.

---

## §0 Purpose

The project already has two scoring rubrics:

- **`think_sheet.md` rubric** — strategic, idea-level. Scores project ideas against `Strategic Fit`, `Revenue Path`, `Foundation Fit`, `Provability`, `Anti-Drift` for promotion / parking decisions.
- **`Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`** — buyer-facing, email-level. Scores individual emails against `sender_identity`, `conversation_continuity`, `vendor_payment_history`, `document_integrity`, `origin_timing` to explain risk to MSP / SMB clients.

Neither covers the **tactical layer**: when the operator is in a session and asks *"what's the next thing to do right now?"* — there is currently no scoring discipline for that.

This rubric exists to solve one problem:

> Score and rank concrete next-action candidates inside an active session so the operator can make the next decision from numbers, not hunches — without giving the rubric authority over which action gets executed.

This is a **tactical execution layer**. It does not score project ideas (the `think_sheet.md` rubric does that). It does not score emails (the Client-Facing rubric does that). It scores **3–7 candidate actions** that exist in the immediate decision window.

---

## §1 Scope

### In scope (v1)

- A deterministic 5-axis scoring rubric for next-action candidates in an active build / planning session.
- A 10-step decision loop (OBSERVE → GENERATE OPTIONS → SCORE → RANK → PRESENT → HUMAN DECISION → EXECUTE → AUDIT → LOG → UPDATE SIGNALS) with a fixed structure.
- A bounded option-set size (3–7 candidates per cycle).
- A pre-execution expected-outcome capture so the audit step has a defined comparison baseline.
- Hard rules forbidding multi-action execution, skipping steps, mid-cycle structural changes, autonomous rule mutation, and rubric self-modification.
- A standard output format (action block + per-axis score + total).
- A defined operator-override path when the operator rejects all candidates.
- Boundary statements distinguishing this rubric from the existing strategic and email-level rubrics.

### Out of scope (v1)

- No replacement of `think_sheet.md` rubric or the Client-Facing email rubric.
- No autonomous selection of the executed action (rubric ranks; human chooses).
- No change to the canonical-authority chain (`agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` for candidate generation per D13-rev, `PROJECT_HANDSHAKE.md` for current focus, operator's current instruction overrides both). `PROJECT_BUILD_AND_AUDIT_QUEUE.md` is retired as ordering authority (historical read-only).
- No new persistence surface unless §10 Q3 resolves to add one.
- No automatic Grok-audit firing inside the loop unless §10 Q5 resolves to add one.
- No client-facing surface; this rubric is internal operator tooling.
- No production system-prompt compression in v1; that is a follow-on artifact and a §10 question (Q6).

---

## §2 Locked Design Decisions (§11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Rubric type | Tactical execution layer. Distinct artifact from `think_sheet.md` (strategic) and Client-Facing email rubric (buyer-facing). |
| D2 | Authority model | The system **does not decide**. The rubric ranks candidates; the human selects from the ranked set; reality audits the result. The rubric is a visibility tool, never an approval authority. Inherits the supersession in `Compliance_and_Trend_Watch_Process.md` §1.1. |
| D3 | Axis count and structure | Exactly five axes, 0–2 each, max total 10. Axes are: `leverage`, `risk_reduction`, `evidence_strength`, `future_cost` (inverted), `reversibility`. |
| D4 | Option-set size | Minimum 3, maximum 7 candidate actions per cycle. "Do nothing" is a valid candidate when applicable; it is scored with the same axes as any other action. |
| D5 | Naming | Canonical name is **"Next-Action Decision Rubric."** The phrase "5-axis rubric" is forbidden as a label for this artifact because it collides with two existing 5-axis rubrics already in the project. |
| D6 | Calibration scope | Calibration is restricted to **mismatch-logging only**. The operator may record disagreements between predicted and actual outcomes. The operator may not modify axis names, axis definitions, axis weights (D10 below), band thresholds (D11 below), or the 10-step loop without a new spec revision. |
| D7 | Pre-execution expectation | The Execute step (loop step 7) must capture a one-line "expected outcome" **before** the action runs. The Audit step (loop step 8) compares the actual result to this captured expectation. Without a pre-execution expectation, the audit verdict is undefined. |
| D8 | Operator override path | If the operator rejects all candidates in a cycle, the system returns to the Generate Options step (loop step 2) with an explicit operator-supplied constraint. There is no "off-protocol decision" branch. The override is itself a logged event (loop step 9). |
| D9 | One action per cycle | Multi-action execution is forbidden. If two actions appear equally necessary, they run as two separate cycles. The Execute step takes exactly one action; no bundling, no chaining. |
| D10 | Axis weighting | Equal weighting in v1. Total = sum of axis scores. Per-axis weighting is deferred to a future spec revision and gated on real calibration data showing systematic axis-level error. |
| D11 | Band interpretation | Bands are interpretive guidance, not gate thresholds. Suggested reads: `8–10` strong candidate, `5–7` reasonable / borderline, `0–4` weak / experimental. The operator selects from any band based on intent; the rubric does not block any band. |
| D12 | No autonomous rule mutation | The system may not modify §2 (locked decisions), §3 (axis definitions), §4 (loop structure), or §5 (hard rules). Changes require an explicit spec revision and a fresh §11 signature. |

---

## §3 Axis Definitions

Each axis is scored `0`, `1`, or `2`. Axis names are versioned product vocabulary (D5); renaming requires a spec revision.

### 3.1 `leverage`

Measures how much future work the action unlocks.

- **0:** Low impact. Action does not unlock or simplify anything beyond itself.
- **1:** Moderate value. Action enables one downstream lane or removes one minor blocker.
- **2:** Unlocks major future work. Action removes a structural blocker, opens a new lane, or makes multiple downstream actions possible.

### 3.2 `risk_reduction`

Measures how much risk the action removes.

- **0:** No risk impact.
- **1:** Some risk reduction. Action softens or partially mitigates a known risk.
- **2:** Removes a major risk. Action eliminates or substantially mitigates a structural risk that was actively threatening progress, revenue, audit posture, or governance.

### 3.3 `evidence_strength`

Measures how strong the case for taking the action is, based on signal quality.

- **0:** Weak / assumed. Action is hunch-driven, no repeated signal, no operator-confirmed evidence.
- **1:** Partial evidence. One credible signal or operator instinct, but not yet validated.
- **2:** Strong, repeated signal. Multiple sources agree, or operator has explicit prior evidence the action is correct.

### 3.4 `future_cost` (inverted)

Measures how the action affects future complexity. **Inverted: higher score = lower future cost.**

- **0:** Adds future complexity. Introduces tech debt, new dependency, new maintenance burden, new ongoing decision overhead.
- **1:** Neutral. No meaningful change in future complexity either way.
- **2:** Reduces future complexity. Action simplifies, consolidates, removes ongoing burden, or unifies fragmented surfaces.

### 3.5 `reversibility`

Measures how easily the action can be undone if wrong.

- **0:** Irreversible / hard to undo. Action commits to a path that cannot be cleanly rolled back.
- **1:** Partially reversible. Action can be undone with effort or partial loss.
- **2:** Fully reversible. Action can be cleanly rolled back at any point with no data, decision, or relationship loss.

### §3.6 Objective binary calibration (amendment — in force)

Prose definitions above remain authoritative for axis **meaning**. Mandatory **0–2 disk-truth scoring rules**, Estimator pool boundary, and machine-log axis keys are in `4. Product_Roadmap/Next_Action_Decision_Rubric_Binary_Calibration_Amendment_Deep_Dive.md` (§3.A), **§11 SIGNED 2026-06-21** (MMI-DEC-095; pre-build gate 0/0 `audit_outputs/next_action_rubric_binary_calibration_amendment_20260622T012415Z.md`). Session tactical scoring uses §3.A when calibrating candidates. The rubric still ranks; Matt selects (D2).

---

## §4 The Decision Loop (10 steps)

The loop is a fixed structure. Steps may not be skipped, reordered, merged, or executed in parallel.

### Step 1 — OBSERVE

Capture only **factual current state**: completed work, open tasks, known issues, system status. No interpretation, no scoring, no recommendation.

### Step 2 — GENERATE OPTIONS

Produce 3–7 candidate next actions. Rules:

- Each action is a single, executable step.
- No bundling; no compound "and then" candidates.
- "Do nothing" is a valid candidate when it makes sense for the current state.
- The source of options is governed by §10 Q1.

### Step 3 — SCORE OPTIONS

Score every candidate on each of the five §3 axes, 0–2 per axis. Compute total.

### Step 4 — RANK

Sort candidates by total score, highest to lowest. Ties are preserved as ties; the rubric does not break ties.

### Step 5 — PRESENT OUTPUT

Return the ranked candidate set with per-axis breakdown and total. No decision is made at this step. No recommendation language. The output is data, not advice.

### Step 6 — HUMAN DECISION

The operator selects one candidate from the ranked set. Selection may follow a mode (e.g. *stability* → highest score, *learning* → mid, *experiment* → low) or pure operator judgment. Mode formalization is governed by §10 Q2.

If the operator rejects all candidates: invoke the D8 override path — return to Step 2 with an explicit operator-supplied constraint. Do not proceed with any candidate.

### Step 7 — EXECUTE

Capture a one-line **expected outcome** for the selected candidate (per D7). Then execute exactly one action. No extras, no expansion, no opportunistic side actions.

### Step 8 — AUDIT

Evaluate the result against the captured expected outcome:

- **PASS** — result matched expectation.
- **PARTIAL** — result partially matched; some expectation gap.
- **FAIL** — result did not match expectation.

The audit verdict is recorded; it is not used to decide whether the next cycle starts.

### Step 9 — LOG

Record the full cycle: chosen action, per-axis scores, total, expected outcome, actual outcome, audit verdict, and any surprises or mismatch notes. Persistence surface is governed by §10 Q3.

### Step 10 — UPDATE SIGNALS (limited)

Allowed updates:

- Calibration of scoring accuracy (per D6 — mismatch-logging only).
- Interpretation of evidence-strength patterns (operator-side intuition refinement, not rubric mutation).

Forbidden updates:

- Changing rubric fields, axes, or band definitions.
- Changing the loop structure or hard rules.
- Adding new stages or removing existing stages.
- Rewriting any §2 locked decision.

Then loop back to Step 1 for the next decision.

---

## §5 Hard Rules

These rules govern every cycle. Violations are spec breaches, not calibration events.

- **No multi-action execution.** Step 7 takes exactly one action.
- **No skipping steps.** Every cycle runs all 10 steps in order.
- **No system redesign during runtime.** The structure is locked between spec revisions.
- **No changing scoring categories.** Axis names and definitions are versioned product vocabulary.
- **No autonomous rule mutation.** Every change to §2 / §3 / §4 / §5 requires an explicit spec revision and a fresh §11 signature.

---

## §6 Failure Modes

Enumerated honestly. These define what the spec text and the audit posture protect against.

### i. Authority drift

The rubric becomes treated as a decision authority — "the score said 8 so we did it" — instead of a ranking aid. This is the same failure mode that triggered the 2026-05-26 supersession in `Compliance_and_Trend_Watch_Process.md` §1.1.

**Mitigation:** D2 is the lead locked decision. Output format (§7) is data, not advice. Step 5 explicitly states "no decision is made at this step."

### ii. Calibration drift (rubric self-modification)

The operator (or an assistant) silently adjusts axis weights, band thresholds, or definitions over time, claiming "calibration." The rubric loses meaning because its scale has shifted.

**Mitigation:** D6 restricts calibration to mismatch-logging only. D12 requires explicit spec revision for any structural change.

### iii. Naming collision

Casual reference to "the 5-axis rubric" causes confusion across project artifacts because two prior 5-axis rubrics already exist.

**Mitigation:** D5 forbids the label "5-axis rubric" for this artifact. Canonical name is **"Next-Action Decision Rubric."**

### iv. Option-generation laziness

Step 2 emits only 1–2 obvious options instead of producing a 3–7 set, defeating the ranking discipline.

**Mitigation:** D4 sets the floor at 3. If fewer than 3 plausible candidates exist, "do nothing" and "regenerate with a different framing" are always valid candidates.

### v. Audit-gap

Step 8 is skipped because the result "obviously worked." Without an audit, the cycle's evidence value is lost.

**Mitigation:** D7 (pre-execution expectation) gives Step 8 a defined comparison. Hard rule "no skipping steps" makes audit non-optional.

### vi. Queue / rubric collision

The operator is unsure whether `PROJECT_BUILD_AND_AUDIT_QUEUE.md` or this rubric is the source-of-truth for "what's next."

**Mitigation:** §10 Q1 must resolve before §11. Until then, the queue's existing canonical-ordering claim is preserved; this rubric operates beside the queue, not over it.

### vii. Decision laundering

After the operator picks a candidate, the cycle log is written to imply the rubric chose it. This re-introduces authority drift through the audit trail.

**Mitigation:** Step 9 logs the selection as an explicit operator action, not as a rubric output. Log schema (§10 Q3) must capture operator-decided vs rubric-ranked separately.

### viii. Compression drift

If a compressed system-prompt block is created from this spec, the prompt drifts away from the spec text over time and becomes the de facto authority.

**Mitigation:** §10 Q6 governs whether a compressed system-prompt is built. If yes, it is generated from the signed spec, not authored fresh, and any change to the prompt requires a fresh spec revision.

---

## §7 Output Format

Each cycle's Step 5 produces output in this exact shape:

```
ACTION 1
  Leverage:      X
  Risk:          X
  Evidence:      X
  Future Cost:   X
  Reversibility: X
  TOTAL:         X

ACTION 2
  Leverage:      X
  Risk:          X
  Evidence:      X
  Future Cost:   X
  Reversibility: X
  TOTAL:         X

(... up to 7 actions ...)
```

The output is data only. No "recommended" markers, no "best choice" language, no narrative framing. The operator selects in Step 6.

The Step 9 log entry adds:

```
SELECTED:        ACTION N (operator-chosen, not rubric-ranked)
EXPECTED:        <one-line expected outcome>
EXECUTED AT:     <timestamp>
AUDIT VERDICT:   PASS | PARTIAL | FAIL
SURPRISES:       <free-text notes; empty if none>
```

---

## §8 Relationship to Existing Rubrics and Artifacts

| Artifact | Layer | Decides what | Relationship to this rubric |
|---|---|---|---|
| `think_sheet.md` 5-axis rubric | Strategic / idea-level | Whether a project idea promotes, parks, or retires | Distinct. This rubric does not score project ideas. |
| Client-Facing 5-Axis Email Scoring Rubric | Buyer-facing / email-level | How an email's risk is explained to MSP / SMB clients | Distinct. This rubric is internal tooling, never client-facing. |
| `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` | Operational / candidate generation | Actionable-now swarm-map nodes + dependency/blocker state for the Build Sequencer | Canonical candidate source per D13-rev (§12). Generator only — never build authority (Rule 4). |
| `PROJECT_BUILD_AND_AUDIT_QUEUE.md` | Historical / retired | Was default build order (retired 2026-06-08) | **RETIRED** as ordering authority. Read-only audit trail. Superseded by scoreboard + this rubric. |
| `PROJECT_HANDSHAKE.md` | Operational / current focus | The single active build target and resume point | Compatible. This rubric does not modify handshake state; it can be invoked while the handshake is set on any active focus. |
| `Operating_Doctrine_14_Day_Trial.md` | Governance / mode | How the operator runs the project during the trial window | This rubric is a candidate operator tool inside that doctrine. Its trial-period use is itself signal for the §10 Q4 calibration cadence. |
| `Compliance_and_Trend_Watch_Process.md` §1.1 | Governance / authority | Rubrics are advisory only | This rubric inherits the supersession verbatim. D2 ratifies it. |

---

## §9 Audit / Gate Requirements

The rubric itself does not invoke `audit_tools/complete_gate.py` on every cycle (that would tax the gate budget). Gate requirements are minimal and structural:

- **Spec gate.** This document must run through `audit_tools/complete_gate.py` before §11 sign-off, with a worker manifest naming this file as the relevant contract.
- **Spec-revision gate.** Any future change to §2, §3, §4, §5, or §7 requires a fresh `complete_gate.py` audit run plus a new operator §11 signature.
- **Cycle-log gate (conditional).** Whether individual cycle logs trigger Grok audits is governed by §10 Q5. Default until resolved: cycle logs do not auto-fire Grok audits.
- **Rubric-vs-reality cross-check.** At the 14-day Operating Doctrine retro, the operator reviews mismatch-log entries (D6) for systematic axis-level error. This is operator-led; Grok audit is optional per the trial spec §10.

---

## §10 Open Questions for Matt — CLOSED 2026-06-04

All seven questions were resolved and locked at Matt's §11 sign-off on 2026-06-04. They are now decisions D13–D19 (table in §11). The questions below are retained for historical record.

### §10.R Resolution status (LOCKED 2026-06-04 at §11 sign-off → D13–D19)

All seven questions were resolved with operator-reviewed, pre-scored recommendations and locked at Matt's §11 signature on 2026-06-04. They are now decisions D13–D19 (see §11). Any future change to these requires the §9 spec-revision cycle (fresh `complete_gate.py` audit + new §11 signature).

| Q | Proposed resolution | Becomes | One-line rationale |
|---|---|---|---|
| Q1 | (c) Hybrid — queue is default source; conversational candidates allowed when queue is stale/unfit | D13 | Keeps queue authoritative for ordering; rubric usable live; avoids queue/rubric collision (FM vi). |
| Q2 | (b) Informal operator intent — modes are labels the operator may state, not thresholds the rubric enforces | D14 | Formal modes would let a mode pick the action = authority drift (FM i), against D2. |
| Q3 | (c) New dedicated artifact `decision_cycles_log.md` | D15 | Durable + greppable for D6 calibration; keeps activity log clean; avoids decision-laundering (FM vii). |
| Q4 | (b) at the 14-day Operating Doctrine retro **plus** (d) trigger at ≥3 PARTIAL/FAIL in a row | D16 | Bundles into existing retro (no new ritual) with an early-warning safety net. |
| Q5 | (b) on FAIL audits only **plus** (c) operator-demand opt-in | D17 | Spends gate budget only on real failures; preserves learning signal; spec flags (b)/(c) as likely. |
| Q6 | (c) Defer until one trial cycle of direct spec use | D18 | Avoids baking a production prompt pre-use; does not block §11 tonight. |
| Q7 | (a) Reference scoring — worked "do nothing" example (e.g. L0 R0–1 E0 FC1 Rv2 → 3–4) | D19 | Consistency without special-casing; keeps D4 (same axes) intact. |

These are now locked in the §11 decision table below as D13–D19; the §10 questions are closed.

### Q1. Source of options

Does Step 2 generate options:

- **(a) From `PROJECT_BUILD_AND_AUDIT_QUEUE.md`** — queue items become the candidate set; rubric ranks them.
- **(b) From conversational context** — the assistant or operator surfaces 3–7 candidates from the live session state; queue is referenced but not authoritative.
- **(c) Hybrid** — default candidates pulled from the queue; conversational additions allowed when the queue is stale or doesn't fit the current session.

This is the largest open decision because it determines whether the rubric is a queue-prioritization tool or an in-the-moment session aid.

### Q2. Mode formalization

The 2026-05-26 design referenced three operator modes (`stability` → highest score, `learning` → mid, `experiment` → low). Are these:

- **(a) Formal modes** with locked band-threshold rules per mode.
- **(b) Operator-described intent** — informal labels the operator may state but the rubric does not enforce.
- **(c) Out of scope** — drop the mode language; the operator selects with no formal mode at all.

### Q3. Cycle-log persistence

Where does Step 9's cycle log live?

- **(a) Inline in the active session** — chat-only, ephemeral.
- **(b) Append to `PROJECT_ACTIVITY_LOG.md`** — durable but mixed with other activity.
- **(c) New artifact** — `decision_cycles_log.md` or similar, dedicated to this rubric.
- **(d) Per-cycle file** — one log file per cycle in a dedicated directory.

Cost / signal tradeoff: heavier persistence supports calibration review at the 14-day retro; lighter persistence avoids artifact bloat.

### Q4. Calibration cadence

When does mismatch-logging (D6) get reviewed?

- **(a) On operator demand only** — no scheduled cadence.
- **(b) At the 14-day Operating Doctrine retro** — bundled with the trial review.
- **(c) Weekly** — fixed cadence.
- **(d) Triggered by a threshold** — e.g. ≥3 PARTIAL or FAIL audits in a row.

### Q5. Grok-audit boundary

Does any cycle event auto-fire a Grok audit via `complete_gate.py`?

- **(a) Never** — this rubric stays out of the gate budget entirely.
- **(b) On FAIL audits only** — a cycle that fails the Step 8 audit triggers a follow-up Grok review of the underlying spec or artifact the action touched.
- **(c) On operator demand** — the operator may opt in for any cycle.
- **(d) Always** — every cycle ends with a Grok audit pass.

(d) is almost certainly too expensive. (a) loses learning signal. (b) or (c) are likely shapes.

### Q6. Compressed system-prompt block

The 2026-05-26 design ended with: *"If you want next, I can compress this into a single system-prompt block optimized for Cursor / agent use (ultra-tight, no explanation, production style)."*

- **(a) Yes, build it post-§11** — generate the compressed prompt from this signed spec; any change to the prompt requires a spec revision.
- **(b) No, doctrine document only** — the rubric lives as a spec the operator reads; no production system-prompt artifact is created.
- **(c) Defer** — make this decision after one trial cycle of using the spec directly.

### Q7. "Do nothing" scoring guidance

D4 allows "do nothing" as a candidate but does not specify how it scores. Should the spec include:

- **(a) Reference scoring** — a worked example of how "do nothing" typically scores (e.g. `Leverage 0, Risk 0–1, Evidence 0, Future Cost 1, Reversibility 2 → 3–4`).
- **(b) Operator discretion** — leave scoring entirely to the operator each time.
- **(c) A separate column** — flag "do nothing" with a reserved score band so it is not conflated with weak action candidates.

---

## §11 Sign-Off — SIGNED 2026-06-04

Signed by Matt Nichol (Zebra-Comet) on 2026-06-04 after a clean gate audit (grok-4, 0 blocking / 0 warnings; packet `3805524af18fe71ac1b0dc00355458cbbe106e5ccf05a96e5f252b246b6efd25`). The seven §10 open questions are now locked as D13–D19.

### Locked decisions (D13–D19)

| # | Decision | Locked value |
|---|---|---|
| D13 | Source of options (Q1) | **Scoreboard-generated hybrid.** `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (Build Sequencer) is the canonical candidate generator: rows with empty `BLOCKERS`, respecting `TRACK`, build order (Q5), and dependency gates, produce the default 3–7 candidates. Conversational or operator-supplied candidates may be added when the scoreboard does not fit the session. The rubric ranks; Matt selects (D2). `PROJECT_BUILD_AND_AUDIT_QUEUE.md` is **retired** as ordering authority (historical read-only). |
| D14 | Mode formalization (Q2) | **Informal operator intent.** `stability` / `learning` / `experiment` are labels the operator may state as context; they are NOT thresholds the rubric enforces. No mode mechanically selects an action (preserves D2). |
| D15 | Cycle-log persistence (Q3) | **New dedicated artifact** `decision_cycles_log.md`. Durable and greppable for D6 calibration review; keeps `PROJECT_ACTIVITY_LOG.md` clean; logs operator-decided vs rubric-ranked separately (mitigates FM vii). |
| D16 | Calibration cadence (Q4) | **14-day Operating Doctrine retro (baseline) plus a streak trigger** at ≥3 consecutive PARTIAL or FAIL Step-8 verdicts, which prompts an earlier mismatch-log review. |
| D17 | Grok-audit boundary (Q5) | **On FAIL audits only, plus operator-demand opt-in.** A FAIL Step-8 verdict triggers a Grok review of the artifact the action touched; the operator may also opt any cycle in. The loop does not otherwise tax the gate budget. |
| D18 | Compressed system-prompt block (Q6) | **Deferred.** No production system-prompt artifact is built until the rubric has been used directly for at least one trial cycle; the decision is revisited then. Until built, the spec text is the source of truth. |
| D19 | "Do nothing" scoring (Q7) | **Reference scoring.** A worked example is provided (e.g. Leverage 0, Risk 0–1, Evidence 0, Future Cost 1, Reversibility 2 → 3–4). "Do nothing" is scored on the same five axes as any other candidate (preserves D4); no reserved band or separate column. |

### Sign-off line

> Matt Nichol (Zebra-Comet) June 4th. 2026

Per the Authorship Rule (2026-05-25 / 26 discussion, cross-reference to the deleted `Human_Written_Communication_Policy.md` failure mode): the sign-off text is operator-authored. AI may help structure, may proofread, may flag inconsistencies — AI does not draft the operator's signature wording or attribute decisions to the operator without explicit operator authorship.

### What sign-off does

Signing this spec:

1. Locks D13–D19 from the §10 question resolution.
2. Authorizes the rubric to be used inside the active project session as the tactical-layer scoring engine.
3. Per D18 (Q6 = defer), does NOT yet authorize a compressed system-prompt block; that is revisited after one trial cycle of direct use, and if built later it is generated from this signed source-of-truth via a spec revision.

Signing does **not**:

- Authorize the rubric to make decisions on its own. D2 stands regardless of signature.
- Retain `PROJECT_BUILD_AND_AUDIT_QUEUE.md` as canonical ordering authority. Per D13-rev (§12), the queue is retired; the scoreboard generates candidates; this rubric ranks them.
- Reduce or modify the seven non-negotiables in `VISION.md`.

---

## Cross-references

- `VISION.md` — seven non-negotiables that govern this spec.
- `think_sheet.md` — sibling rubric, strategic / idea-level. Distinct.
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` — sibling rubric, buyer-facing / email-level. Distinct.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §1.1 — supersession that this rubric inherits.
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` — canonical candidate generator (Build Sequencer); D13-rev.
- `PROJECT_BUILD_AND_AUDIT_QUEUE.md` — **RETIRED** historical ordering record (superseded 2026-06-08).
- `PROJECT_HANDSHAKE.md` — canonical for current focus; compatible.
- `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` — operating mode under which this rubric is exercised.
- `audit_tools/complete_gate.py` — gate that audits this spec at §11 sign-off and on any future structural revision.

---

## §12 Spec Revision — Build Sequencer Adoption (2026-06-08, SIGNED)

**Trigger:** Butterfly Hard-Stop (AGENTS.md §7.1) — changes canonical next-action authority chain and D13 substance. Consequence Matrix: `4. Product_Roadmap/_Build_Sequencer_Adoption_Consequence_Matrix.md`. Operator selected **Option B** (2026-06-08).

### Revised locked decision

| # | Decision | Revised locked value |
|---|---|---|
| D13-rev | Source of options | Replaces D13 (2026-06-04) in full. Scoreboard-generated hybrid per the D13 row in §11 above. Queue retired as ordering authority. |

### What re-sign authorizes

1. Makes D13-rev live authority (scoreboard generates, rubric ranks, Matt selects).
2. Retires queue ordering claim across project artifacts that reference D13.
3. Does **not** authorize individual agent builds (scoreboard Rule 4 stands).
4. Does **not** authorize gate automation for scoreboard freshness (doctrine Steps 0.5 / 6.5 only until a separate gate-code slice).

### §12 re-sign

> Matt Nichol June 8th 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

---

**End of spec. D13 revision SIGNED 2026-06-08 — live authority.**
