# Strategic Direction Matrix - Deep Dive

**Status:** PRE-§11 DRAFT. Authored 2026-06-07. Operator instinct by Matt Nichol; design pressure-tested in the Claude advisory lane (per AGENTS §2.1.2); drafted into spec form by Cursor (execution lane). NOT signed, NOT authority until Matt signs §11. Builds nothing, authorizes nothing. Does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec.

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
- Surfacing second-order ripple effects of a butterfly decision - that is the job of `Consequence_Matrix_Process.md`. The two are complementary, not duplicates: the **Consequence Matrix** asks *what does this decision ripple into?*; the **Strategic Direction Matrix** asks *which of these options scores best?* A genuine butterfly fork may run the Consequence Matrix first (effects) and this matrix second (ranking).
- Build authorization, §11 sign-off, or any operator-authority decision (§7, §8).

---

## §2 Locked design decisions

1. **Separate from the tactical rubric.** Different file, different name, different scale. Merging would corrupt both - the tactical rubric would be gamed by strategic concerns; the strategic matrix would be trivialized by task-level thinking.
2. **0-3 per axis, five axes, ceiling 15.** 0-2 is too coarse for strategic differentiation; 0-5 / 0-10 invite false precision and score inflation. 0-3 forces a real call: bad / acceptable / good / clearly best.
3. **The matrix ranks; Matt selects.** It is an input to Matt's decision, never a replacement (§6).
4. **A score is never an authorization** (§8).

---

## §3 Axes and scoring definitions

Each axis scores 0-3. Maximum total: 15.

| Axis | What it measures | 0 | 1 | 2 | 3 |
|------|------------------|---|---|---|---|
| **Friction Cost** | Pain and rework created right now | Breaks something / major rework | Significant friction but contained | Minor friction, manageable | Smooth, no downstream disruption |
| **Architecture Fit** | Reduces or increases future rework | Creates structural debt | Neutral, no lasting impact | Fits cleanly, minor future benefit | Actively reduces future rework |
| **Revenue Path Support** | Moves toward an MSP-sellable product without forcing premature selling | No connection to revenue | Weak indirect connection | Supports revenue path, not urgent | Directly enables a buyer conversation |
| **Time-to-Value Ratio** | Time required relative to what it unlocks | High time cost, low unlock | High time, moderate unlock | Moderate time, good unlock | Low time, high unlock |
| **Target Completeness** | Moves toward the full 70-agent governed swarm, not a shortcut or scope reduction | Moves away from target | Neutral, no progress | Incremental progress toward target | Significant progress toward target |

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

- **11-15 - Strong pick.** Default is to build it; do not deliberate further unless Matt overrides.
- **7-10 - Viable.** Matt reviews before proceeding.
- **0-6 - Do not build now.** Redefine the option or park it.

The band exists so the matrix produces a ranking *and* a default action, instead of producing a ranking that then needs a second decision about what to do with it.

---

## §6 Output format

Every run produces, in order:
1. One scored table - the 2+ options, each axis 0-3, totals out of 15.
2. A single `recommended_next_step` sentence.
3. A closing line: `Recommended: [option]. Matt's call.`

The matrix never uses the words "approved," "authorized," or "ready to build" - those are reserved for §11 signatures and explicit operator authorization. The matrix is an input to Matt's decision (§2.3).

---

## §7 Anti-delay rules (mandatory)

These keep the matrix from becoming a delay tool or an avoid-building tool:
1. **Time cap.** A run must be completable in under 10 minutes. If scoring an option takes longer, the option is not defined well enough to build - redefine it, then score.
2. **Minimum two options.** If there is only one option, you do not need the matrix - build it.
3. **Score threshold default.** Any option scoring 11+ is the pick unless Matt explicitly overrides.
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

- **Score inflation** - giving every option high marks to dodge a hard call. Fix: if three options all score 11+, they are not differentiated enough; redefine before scoring.
- **Matrix laundering** - treating a high matrix score as implicit build authorization. Fix: §8. Score is not authorization.
- **Delay by design** - running the matrix on decisions that should use the tactical rubric, manufacturing a longer process for simple calls. Fix: the §4 trigger rules are the gate.
- **Naming collision** - confusing this with the Consequence Matrix or the several existing 5-axis rubrics. Fix: §1 relationship text; this tool is named "Strategic Direction Matrix," scores 0-3 across five axes to a ceiling of 15, and ranks direction options (it does not enumerate ripple effects - that is the Consequence Matrix).

---

## §10 Open questions

1. File home: this draft lives in `4. Product_Roadmap/` alongside the tactical rubric; confirm or relocate to a `governance/` folder if one is established.
2. Logging: should strategic-matrix runs be logged in `decision_cycles_log.md` (shared with the tactical rubric) or a separate `strategic_cycles_log.md`?
3. Consequence Matrix ordering: when a butterfly fork triggers both, is the Consequence Matrix always run first, or only when second-order effects are non-obvious?
4. Per-axis weighting: all five axes are currently equal-weight; does any axis (e.g. Target Completeness, given it is the #1 operator target) warrant a heavier weight, or does equal-weight stay to prevent calibration drift?

---

## §11 Sign-off

Operator-authored signature line. Matt signs here to promote this draft to a §11-locked spec. Until signed, this matrix may be used informally but never claimed as signed, and never cited as authority.

Signed: ______________________  Date: __________
