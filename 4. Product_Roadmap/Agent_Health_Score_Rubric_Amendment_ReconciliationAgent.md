# Agent Health Score Rubric — Amendment: ReconciliationAgent (Layer 4) track

**Document type:** Rubric Amendment (DRAFT — pre-§11, unsigned)
**Status:** DRAFT — UNSIGNED. No scoring authority until §11 is signed.
**Date drafted:** June 11 2026
**Drafted by:** Cursor (execution lane), transcribing the operator-settled June 11 2026 session design. Signature reserved for the operator.
**Amends:** `4. Product_Roadmap/Agent_Health_Score_Rubric.md` — §11 SIGNED 2026-06-10 (Matt Nichol).
**Required by:** Phase 4 ReconciliationAgent contract P4-D7 (`d0cc849`).

---

## §A — Purpose

The signed Agent Health Score Rubric is **detection-shaped**: its five components (Evidence Stage, Proof Depth, Governance, Boundary Safety, Integration Health) assume an agent that emits one evidence signal. The ReconciliationAgent is **not a detector** — it is a three-voter ensemble that consumes Layer 1 evidence and produces the swarm's only verdict. The standard track does not score it cleanly (there is no single "evidence type"; "proof depth" and "boundary" mean different things for a verdict producer). This amendment adds a dedicated **Layer 4 / ReconciliationAgent track** so the ensemble can be scored on what actually matters for it. **ELITE 85+ remains the target** and the composite bands are unchanged.

---

## §B — New track: ReconciliationAgent (Layer 4) — 0 to 100

Five components, weighted to 100. Applied to the ReconciliationAgent (#84) in place of the detection track. The base rubric's composite bands (ELITE 85-100, HEALTHY 70-84, MARGINAL 50-69, AT RISK 25-49, DEMOTED 0-24) apply unchanged.

### Component 1 — Ensemble Integrity (25)
| Score | Meaning |
|---|---|
| 21-25 | Three voters provably independent (none sees another's vote before casting); 2-of-3 resolution correct; minority always logged; all-disagree → ESCALATE |
| 14-20 | Independence + resolution correct; minority logging or escalate path has one documented gap |
| 6-13 | Resolution works but independence not enforced in tests |
| 0-5 | Voters not independent, or resolution incorrect |

### Component 2 — Evidence Chain Quality (20)
| Score | Meaning |
|---|---|
| 17-20 | Plain-English chain present on every verdict, complete required fields, operator-readable by a non-technical MSP operator |
| 11-16 | Chain present but technical/partial in places |
| 5-10 | Chain present only on some verdicts |
| 0-4 | No readable evidence chain |

### Component 3 — Verdict Accuracy (25)
| Score | Meaning |
|---|---|
| 21-25 | Verdict matches expected on the adversarial synthetic corpus; enum-closed; special paths correct (spam_signal_only→DELIVERY_PROBLEM; zero-day does not alter verdict) |
| 14-20 | Accurate on synthetic corpus; one special-path edge documented |
| 6-13 | Accurate on happy path only |
| 0-5 | Misclassifies, or emits a value outside the closed enum |

### Component 4 — CIRT Routing Correctness (15)
| Score | Meaning |
|---|---|
| 13-15 | ESCALATE routes to the bound named CIRT individual per tenant; freeze authority honored; deterministic lockdown (MEDIUM_RISK + Deep breath → HIGH_RISK) fires; audit trail on routing |
| 8-12 | Routing correct; one of lockdown / audit / freeze has a documented gap |
| 3-7 | Routing present but tenant binding loose |
| 0-2 | Misroutes escalation or ignores CIRT binding |

### Component 5 — Governance & Boundary (15)
| Score | Meaning |
|---|---|
| 13-15 | §11-signed contract + scoreboard row + 3 test classes + gate clean; tenant isolation on verdict write; no verdict surface leaks outside the ReconciliationAgent |
| 8-12 | Signed + row + tests, one gap documented |
| 3-7 | Row exists, contract or tests incomplete |
| 0-2 | No row / no contract / no gate |

**Composite:** sum of the five (max 100). ELITE 85+ required for Phase 4 closure (P4-D7).

---

## §C — Which track applies

- **Detection / verification agents** (Layer 1-3, e.g. #78-83) — the original five-component detection track, unchanged.
- **ReconciliationAgent (#84, Layer 4)** — this track.
- Future verdict/ensemble agents may cite this track by amendment.

---

## §D — What this amendment does NOT change

- The original five-component detection track, its scoring, or any already-recorded score (#72-83) — unchanged.
- The composite bands and the build-map gating rules — unchanged.
- The two coexisting health-score specs flagged previously (7-component Deep_Dive board vs 5-component Rubric) — not reconciled here; this only adds a Layer 4 track to the 5-component Rubric.

---

## §11 — Operator Sign-Off

**Status:** DRAFT — UNSIGNED. No scoring authority until this block is signed.

**Signed:** ____________________
**Date:** ____________________
