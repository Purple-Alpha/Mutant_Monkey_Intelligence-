# Consequence Matrix Process

**Status:** DRAFT (pre-§11). Created 2026-05-30 from Matt's "butterfly effect" decision discussion.
**Owner:** Matt Nichol
**Purpose:** Operator-triggered process for surfacing second-order consequences of path-setting decisions.

This file defines a lightweight consequence matrix for decisions whose effects may compound across revenue, architecture, legal / insurance posture, buyer trust, product identity, signed specs, or future autonomy.

It does not replace `think_sheet.md` or the Next-Action Decision Rubric.

---

## §0 Purpose

NorthStar now has three distinct internal decision surfaces:

| Tool | Layer | Question it answers |
|---|---|---|
| `think_sheet.md` | Strategic / idea-level | Should this idea promote, park, or drop? |
| `Next_Action_Decision_Rubric_Deep_Dive.md` | Tactical / session-level | What should we do next inside this work session? |
| Consequence Matrix | Path-setting / second-order effects | What future doors does this decision open, close, or quietly authorize? |

The Consequence Matrix exists for the "butterfly effect" layer. It is used before committing to a path, not during every normal build step.

---

## §1 Scope

### In scope

- Product-lane decisions.
- Architecture-path decisions.
- Client-facing claim or positioning decisions.
- Insurance / legal posture decisions.
- Live integration path decisions.
- Evidence-retention or redaction decisions.
- Revenue / pricing / pilot-shape decisions.
- Stage A -> Stage B -> Stage C transition decisions.
- Decisions that may affect future autonomy, operator authority, signed specs, or buyer trust.

### Out of scope

- Normal test runs.
- Fixture creation.
- Typo fixes.
- Notes-only captures.
- Bounded commits after gate-clean work.
- Routine queue execution.
- Small reversible file edits.
- Daily implementation choices that do not set a future path.

---

## §2 Trigger Rule

Use the Consequence Matrix only when at least one of these is true:

1. The decision affects revenue, architecture, legal / insurance posture, buyer trust, product identity, signed specs, or future autonomy.
2. The decision creates or changes buyer-facing language, evidence-record schema, audit artifact category, or claim-boundary surface.
3. The decision changes who decides something later: operator, agent, audit gate, external model, customer, MSP, or insurer-side reviewer.
4. Two or more high-scoring options are close enough that a rubric score does not expose the trade-off.
5. The decision may be hard to reverse within 30 days at the project level.
6. The decision touches compliance, insurance, certification, underwriter, or forbidden-language posture.

Do not use the matrix just because a decision feels important. Use it because the decision is path-setting.

---

## §3 Operating Rule

The matrix surfaces consequences. Matt decides.

Agents may flag that a decision appears to meet the trigger criteria, but agents do not run or fill the matrix unless Matt explicitly asks.

The matrix is not:

- a gate,
- an approval authority,
- a reason to defer indefinitely,
- a replacement for signed specs,
- a client-facing artifact,
- a scoring rubric,
- or a forecast.

Unknown is an allowed cell value. Unknown cells should not become fake precision.

Time-box v1 usage to 15 minutes. If a cell cannot be filled in one or two sentences, write `unknown` or `estimate` and move on.

---

## §4 Template

```markdown
# Consequence Matrix

## Decision
**Decision:**  
**Date:**  
**Owner:** Matt Nichol  
**Why this matters:**  

## Options
- Option A:
- Option B:
- Option C:

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A |  |  |  |  |  |  |
| B |  |  |  |  |  |  |
| C |  |  |  |  |  |  |

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility Impact | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A |  |  |  |  |  |  |  |  |  |
| B |  |  |  |  |  |  |  |  |  |
| C |  |  |  |  |  |  |  |  |  |

## Decision Notes

- Biggest upside:
- Biggest downside:
- Hidden dependency:
- Assumption that must be true:
- Optionality killed:
- What this implicitly authorizes:
- Reverse trigger:
- Evidence needed before committing:

## Outcome

**Operator decision:**  
**Reason:**  
**Review trigger or date:**  
```

---

## §5 Column Definitions

### Short-term columns

- **Opens:** What becomes possible in the next 0-30 days.
- **Closes:** What becomes harder, unavailable, or intentionally parked.
- **Build Surface Added:** Code, spec, fixture, gate, audit, document, or review surface added by the option.
- **Reduces Risk:** Immediate risk removed or reduced.
- **Creates Risk:** Immediate risk introduced.
- **Pipeline Signal:** Near-term signal for revenue, MSP discovery, buyer language, proof, or sales enablement. This is not the same as revenue collected.

### Long-term columns

- **Architecture Lock-In:** The path this option nudges the system toward.
- **Trust / Credibility Impact:** Effect on MSP, SMB, insurer-side reviewer, partner, or future buyer trust.
- **Legal / Insurance Exposure:** New liability, policy, contract, or underwriter question created.
- **Maintenance Burden:** Ongoing engineering, operational, support, or audit load.
- **Evidence / Data Value:** Whether the option creates durable evidence or loses useful evidence.
- **Doctrine Drift Risk:** Whether the option invites authority drift, proxy decisions, signed-spec amendment burden, or second-source-of-truth drift.
- **Claim / Forbidden-Language Risk:** Whether the option makes unsafe buyer language more likely.
- **Operator-Time Burden:** Matt's future time cost, separate from engineering maintenance.
- **Long-Term Reversibility:** Whether the path can be reversed later without data loss, trust damage, or expensive rework.

---

## §6 Failure Modes

1. **Process gravity.** The matrix starts firing on ordinary tasks and slows the build.
   - Mitigation: operator-triggered only; use §2 triggers.

2. **False precision.** A filled table looks rigorous even when cells are guesses.
   - Mitigation: label cells as `fact`, `estimate`, or `unknown` when needed.

3. **Authority creep.** The matrix output gets treated as the answer.
   - Mitigation: matrix surfaces; Matt decides.

4. **Doctrine duplication.** Matrix columns drift into second versions of rubric axes.
   - Mitigation: use this file only for second-order effects; keep rubric scoring separate.

5. **Delay tactic.** The matrix becomes a reason to avoid deciding.
   - Mitigation: 15-minute time-box; unknown cells become research items with a next step.

6. **Overweighting hypothetical risk.** Future fears freeze lab work.
   - Mitigation: use the matrix for path-setting choices, not bounded experiments.

7. **Agent over-application.** Agents propose a matrix to look careful.
   - Mitigation: agents may flag triggers but do not run the matrix without Matt's instruction.

---

## §7 Worked Example Anchor

The 2026-05-29 Cyber Insurance vendor-name redaction discussion is the example that motivated this tool:

- A lean v1 default-redaction option scored well.
- A visible redaction-annotation option also scored well.
- The rubric showed both were viable, but it did not expose the full trade-off between lean sign-off and evidence-chain visibility.
- The operator chose a hybrid: default-redact silently in v1; v1.1 may add visible redaction annotations if cheaper-proof discovery shows demand.

That is the matrix's job: reveal the doors opened and closed by options that all look strong under a score.

---

## §8 Review

At the next operating-doctrine retrospective or quarterly review, inspect how often this matrix was used:

- If it fires on ordinary work, tighten or remove it.
- If it never fires, decide whether it is unnecessary or simply waiting for a true path-setting decision.
- If it fires only on a small number of path-setting choices, keep it.

---

**End of draft. Pre-§11. No authority granted by this file.**
