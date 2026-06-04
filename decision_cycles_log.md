# Decision Cycles Log

Dedicated persistence surface for the **Next-Action Decision Rubric** (`4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md`, §11 SIGNED 2026-06-04). This artifact exists per locked decision **D15** (Q3 resolution) and is the Step 9 log target of the rubric's 10-step loop.

Each cycle records the Step 5 output (candidates + per-axis scores + totals), the operator-selected action (operator-decided, **not** rubric-ranked — D2 / failure mode vii), the pre-execution expected outcome (D7), the Step 8 audit verdict (PASS / PARTIAL / FAIL), and any surprises or mismatch notes (D6 calibration input).

**Calibration cadence (D16):** review mismatch entries at the 14-day Operating Doctrine retro, plus an earlier review whenever **≥3 consecutive PARTIAL or FAIL** verdicts occur.

A score is never a decision. The rubric ranks; Matt selects; reality audits.

## Entry schema

```
CYCLE <n> — <UTC timestamp>
  OBSERVE: <factual current state only>
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    ACTION 1   L_ R_ E_ FC_ Rv_   TOTAL _
    ACTION 2   L_ R_ E_ FC_ Rv_   TOTAL _
    (... 3-7 candidates; "do nothing" allowed, scored on the same axes per D19 ...)
  SELECTED:      ACTION N (operator-chosen, not rubric-ranked)
  EXPECTED:      <one-line expected outcome, captured BEFORE execution per D7>
  EXECUTED AT:   <timestamp>
  AUDIT VERDICT: PASS | PARTIAL | FAIL
  SURPRISES:     <free-text notes; empty if none>
```

---

(No cycles logged yet. The first cycle is recorded here the next time the rubric is run in-session.)
