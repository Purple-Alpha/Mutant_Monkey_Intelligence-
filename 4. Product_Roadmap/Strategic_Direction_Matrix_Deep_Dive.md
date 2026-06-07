# Strategic Direction Matrix - Deep Dive

**Status:** PRE-§11 DRAFT. Authored 2026-06-07; three §10 open questions resolved by the operator the same day (logging surface, Consequence-Matrix ordering, Target-Completeness weighting - folded in below). Operator instinct by Matt Nichol; design pressure-tested in the Claude advisory lane (per AGENTS §2.1.2); drafted into spec form by Cursor (execution lane). NOT signed, NOT authority until Matt signs §11. Builds nothing, authorizes nothing. Does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec.

**Owner:** Matt Nichol

---

## §0 Purpose

A scoring matrix for **path-setting / "which direction do we go" forks** - the strategic decisions that change where the project is heading, not how a single task gets done.

When a fork affects build direction, architecture, revenue path, time horizon, scope, or governance, we do not decide by vibe and we do not argue it out. We put the options through this matrix so the trade-off is visible and ranked before anything is built. The matrix **ranks**; Matt **selects** (§6).

This is the strategic counterpart to the tactical `Next_Action_Decision_Rubric_Deep_Dive.md`. The two are deliberately separate (§1, §8).

---

## §1 Scope

**In scope (this matrix governs):** ranking 2+ candidate *directions* for a path-setting fork, on the five axes in §3, to surface the least-friction / best-future-fit option for Matt's selection.

**Out of scope:**
- Tactical "what is the next move / how do I do this task" decisions - those use the Next-Action Decision Rubric.
- Surfacing second-order ripple effects of a butterfly decision - that is the job of `Consequence_Matrix_Process.md`. The two are **parallel tools for different decision types, not sequential passes** (operator call, 2026-06-07): the Strategic Matrix runs first on strategic triggers; the tactical rubric runs first on tactical triggers; the Consequence Matrix runs on butterfly triggers. The Consequence Matrix is **NOT** a mandatory first pass before this matrix - making it one would add process weight without signal, because consequence scoring is already embedded in the **Friction Cost** and **Architecture Fit** axes (§3). Do not run it twice. (The Consequence Matrix asks *what does this decision ripple into?*; this matrix asks *which of these options scores best?*)
- Build authorization, §11 sign-off, or any operator-authority decision (§7, §8).

---

## §2 Locked design decisions

1. **Separate from the tactical rubric.** Different file, different name, different scale. Merging would corrupt both - the tactical rubric would be gamed by strategic concerns; the strategic matrix would be trivialized by task-level thinking.
2. **0-3 per axis, five axes.** 0-2 is too coarse for strategic differentiation; 0-5 / 0-10 invite false precision and score inflation. 0-3 forces a real call: bad / acceptable / good / clearly best.
3. **Target Completeness is weighted x2; ceiling is 18** (operator call, 2026-06-07). The scale stays 0-3 for every axis - no decimals, no percentages - but the **Target Completeness** score is multiplied by 2 in the total. This structurally enforces that no option wins if it does not move toward the full 70-agent governed swarm: an option scoring 3 on all four other axes but 0 on Target Completeness maxes at 12, which lands in "Matt reviews," not "build it." Max total: 18.
4. **Logging is one shared surface** (operator call, 2026-06-07). Strategic runs are logged in the existing `decision_cycles_log.md`, the same file the tactical rubric uses, tagged with a `type: STRATEGIC` field (`type: TACTICAL` for rubric entries). One place to reconstruct any direction change; no second log to reconcile.
5. **The matrix ranks; Matt selects.** It is an input to Matt's decision, never a replacement (§6).
6. **A score is never an authorization** (§8).

---

## §3 Axes and scoring definitions

Each axis scores 0-3. **Target Completeness is multiplied by 2** in the total (§2.3). Maximum total: 18.

| Axis | What it measures | 0 | 1 | 2 | 3 |
|------|------------------|---|---|---|---|
| **Friction Cost** | Pain and rework created right now | Breaks something / major rework | Significant friction but contained | Minor friction, manageable | Smooth, no downstream disruption |
| **Architecture Fit** | Reduces or increases future rework | Creates structural debt | Neutral, no lasting impact | Fits cleanly, minor future benefit | Actively reduces future rework |
| **Revenue Path Support** | Moves toward an MSP-sellable product without forcing premature selling | No connection to revenue | Weak indirect connection | Supports revenue path, not urgent | Directly enables a buyer conversation |
| **Time-to-Value Ratio** | Time required relative to what it unlocks | High time cost, low unlock | High time, moderate unlock | Moderate time, good unlock | Low time, high unlock |
| **Target Completeness (x2)** | Moves toward the full 70-agent governed swarm, not a shortcut or scope reduction | Moves away from target | Neutral, no progress | Incremental progress toward target | Significant progress toward target |

Total = Friction Cost + Architecture Fit + Revenue Path Support + Time-to-Value Ratio + (Target Completeness x 2). Range 0-18.

---

## §4 Trigger rules - this matrix vs the tactical rubric

**Use the Strategic Direction Matrix when the decision affects any of:**
- Build direction - starting a new layer, changing agent sequencing, reordering the spine.
- Architecture - new module, new data type, new integration pattern.
- Scope - adding agents, parking agents, splitting or merging SPARK entries.
- Revenue path - pricing model, MSP feature prioritization, what gets built before launch.
- Time horizon - anything that shifts the launch estimate by more than one week.
- Governance - new spec type, new sign-off requirement, new lane rule.

**Use the tactical Next-Action Decision Rubric when the decision is:**
- Which file to edit next.
- Which implementation approach to use for a defined task.
- How to resolve a code-level fork inside a signed spec.
- Anything that changes method, not direction.

**The clean test:** if the decision could appear in `PROJECT_HANDSHAKE.md` as a direction change, it is strategic (this matrix). If it would only appear in a commit message, it is tactical (the rubric). If a decision meets no §4 trigger, it goes straight to the tactical rubric - no matrix.

---

## §5 Scoring bands

- **14-18 - Strong pick.** Default is to build it; do not deliberate further unless Matt overrides.
- **9-13 - Viable.** Matt reviews before proceeding.
- **0-8 - Do not build now.** Redefine the option or park it.

The band exists so the matrix produces a ranking *and* a default action, instead of producing a ranking that then needs a second decision about what to do with it. Bands are scaled to the ceiling of 18 (Target Completeness x2): an option that ignores the target cannot reach the "build it" band on the other four axes alone.

---

## §6 Output format

Every run produces, in order:
1. One scored table - the 2+ options, each axis 0-3, totals out of 15.
2. A single `recommended_next_step` sentence.
3. A closing line: `Recommended: [option]. Matt's call.`

The matrix never uses the words "approved," "authorized," or "ready to build" - those are reserved for §11 signatures and explicit operator authorization. The matrix is an input to Matt's decision (§2.5).

**Persistence:** every run is logged in `decision_cycles_log.md` with `type: STRATEGIC` (§2.4), recording the scored options, totals (out of 18), the operator-selected option, and the `recommended_next_step`.

---

## §7 Anti-delay rules (mandatory)

These keep the matrix from becoming a delay tool or an avoid-building tool:
1. **Time cap.** A run must be completable in under 10 minutes. If scoring an option takes longer, the option is not defined well enough to build - redefine it, then score.
2. **Minimum two options.** If there is only one option, you do not need the matrix - build it.
3. **Score threshold default.** Any option scoring 14+ (out of 18) is the pick unless Matt explicitly overrides.
4. **No re-scoring loops.** Run once per fork. Do not re-score the same fork unless the decision has materially changed; re-scoring the same fork is a delay signal, not a governance signal.
5. **Mandatory output.** A run must end with a `recommended_next_step` sentence and the "Matt's call" line, or it did not do its job.

---

## §8 What this matrix cannot do

- It cannot authorize a build. A score is not authorization.
- It cannot replace a §11 signature.
- It cannot override a lane rule (§2.1.2), the seven non-negotiables, or any signed spec.
- It cannot decide. Matt decides; the matrix only ranks.

---

## §9 Failure modes to recognize by name

- **Score inflation** - giving every option high marks to dodge a hard call. Fix: if three options all score 14+, they are not differentiated enough; redefine before scoring.
- **Matrix laundering** - treating a high matrix score as implicit build authorization. Fix: §8. Score is not authorization.
- **Delay by design** - running the matrix on decisions that should use the tactical rubric, manufacturing a longer process for simple calls. Fix: the §4 trigger rules are the gate.
- **Naming collision** - confusing this with the Consequence Matrix or the several existing 5-axis rubrics. Fix: §1 relationship text; this tool is named "Strategic Direction Matrix," scores 0-3 across five axes to a ceiling of 15, and ranks direction options (it does not enumerate ripple effects - that is the Consequence Matrix).

---

## §10 Open questions

1. **OPEN.** File home: this draft lives in `4. Product_Roadmap/` alongside the tactical rubric; confirm or relocate to a `governance/` folder if one is established.
2. **RESOLVED 2026-06-07 (operator):** one shared log. Strategic runs go in `decision_cycles_log.md` with a `type` field (`STRATEGIC` / `TACTICAL`), not a separate file. Folded into §2.4 / §6.
3. **RESOLVED 2026-06-07 (operator):** the Consequence Matrix is NOT a mandatory first pass. The two are parallel tools for different triggers; consequence scoring is already embedded in Friction Cost + Architecture Fit, so running it first would double-count. Folded into §1.
4. **RESOLVED 2026-06-07 (operator):** Target Completeness is weighted x2 (ceiling 18, bands rescaled to 14 / 9 / 0); the 0-3 scale is unchanged. Folded into §2.3 / §3 / §5 / §7.

Only Q1 (file home) remains open. All else is resolved; §11 can be signed once Q1 is settled.

---

## §11 Sign-off

Operator-authored signature line. Matt signs here to promote this draft to a §11-locked spec. Until signed, this matrix may be used informally but never claimed as signed, and never cited as authority.

Signed: ______________________  Date: __________
