# Agent Health Score Rubric — Amendment: Mutation Engine (Layer 5) track

**Document type:** Rubric Amendment
**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Scoring authority granted per §11 scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), grounded in the §11-signed Phase 5 Mutation Engine contract. Signature reserved for the operator.
**Amends:** `4. Product_Roadmap/Agent_Health_Score_Rubric.md` — §11 SIGNED 2026-06-10 (Matt Nichol).
**Required by:** Phase 5 Mutation Engine contract P5-D9 (`Phase5_MutationEngine_Contract.md`, §11 SIGNED 2026-06-12).

---

## §A — Purpose

The signed Agent Health Score Rubric is **detection-shaped** (Evidence Stage, Proof Depth, Governance, Boundary Safety, Integration Health — an agent that emits one evidence signal). The Layer 4 amendment already added a **ReconciliationAgent track** for a verdict producer. The Mutation Engine is a third shape again: it is **neither a detector nor a verdict producer** — it is a controlled, human-signed evolution pipeline whose whole value is in *restraint* (3-shot before eligible, benign-stream proof, operator sign-off, full rollback). The standard track does not score "did the engine refuse to mutate when it should have" or "is every deployment reversible." This amendment adds a dedicated **Layer 5 / Mutation Engine track** so the ensemble is scored on what actually matters for it. **ELITE 85+ remains the target** (P5-D9) and the composite bands are unchanged.

---

## §B — New track: Mutation Engine (Layer 5) — 0 to 100

Five components, weighted to 100. Applied to the Mutation Engine ensemble (#88) in place of the detection track. The base rubric's composite bands (ELITE 85-100, HEALTHY 70-84, MARGINAL 50-69, AT RISK 25-49, DEMOTED 0-24) apply unchanged. The components map onto the named Anomaly Detection Pipeline (Phase 5 contract §3.3.1).

### Component 1 — Confirmation Integrity (25)
| Score | Meaning |
|---|---|
| 21-25 | 3-shot enforced across **distinct `email_id` AND distinct `tenant_id`** (P5-D2); duplicate `email_id` and single-tenant repeats provably do not advance the count; one incident can never mutate the swarm |
| 14-20 | 3-shot enforced; one independence-edge case documented |
| 6-13 | Confirmation counted but independence not enforced in tests |
| 0-5 | A single confirmation can advance a candidate |

### Component 2 — Validation Rigor (20)
| Score | Meaning |
|---|---|
| 17-20 | Laws-of-average baseline comparison + benign-stream FP check across the defined cycle count; conservative threshold rejects any regressing candidate on any cycle; per-cycle delta recorded |
| 11-16 | Benign-stream check present; baseline comparison or per-cycle recording partial |
| 5-10 | Single-cycle validation only |
| 0-4 | No benign-stream false-positive guard |

### Component 3 — Sign-Off Enforcement (25)
| Score | Meaning |
|---|---|
| 21-25 | No deployment without `DEPLOY_MUTATION` (OPERATOR-only); no timeout auto-approves; ZeroDayCapture routes to Matt only (P5-D12); proposal-not-deployment boundary provably held |
| 14-20 | Sign-off enforced; one routing/timeout edge documented |
| 6-13 | Sign-off present but bypassable in a tested path |
| 0-5 | A mutation can reach production without operator signature |

### Component 4 — Rollback Safety (15)
| Score | Meaning |
|---|---|
| 13-15 | Prior signed state recorded before every deploy; deterministic revert; auto-rollback fires on a post-deploy FP spike above the conservative threshold within the observation window |
| 8-12 | Rollback present; auto-trigger or window has a documented gap |
| 3-7 | Manual rollback only |
| 0-2 | No rollback path for a deployed mutation |

### Component 5 — Governance & Audit Completeness (15)
| Score | Meaning |
|---|---|
| 13-15 | Append-only `MutationAuditTrail` on every proposed + deployed mutation (timestamp, evidence chain, signer, outcome); sandbox-only until signed; no net-new `MutationKind`/evidence type without amendment; tenant isolation (P5-D8); §11 contract + scoreboard row + 3 test classes + gate clean |
| 8-12 | Signed + row + tests, one gap documented |
| 3-7 | Row exists, contract or tests incomplete |
| 0-2 | No row / no contract / no gate |

**Composite:** sum of the five (max 100). ELITE 85+ required for Phase 5 closure (P5-D9).

---

## §C — Which track applies

- **Detection / verification agents** (Layer 1-3, e.g. #78-83) — the original five-component detection track, unchanged.
- **ReconciliationAgent** (#84, Layer 4) — the Layer 4 amendment track.
- **Mutation Engine** (#88, Layer 5) — this track.
- Future evolution/pipeline agents may cite this track by amendment.

---

## §D — What this amendment does NOT change

- The original five-component detection track, the Layer 4 track, and any already-recorded score (#72-84) — unchanged.
- The composite bands and the build-map gating rules — unchanged.
- The two coexisting health-score specs flagged previously (7-component Deep_Dive board vs 5-component Rubric) — not reconciled here; this only adds a Layer 5 track to the 5-component Rubric.

---

## §11 — Operator Sign-Off

**Status:** §11 SIGNED — scoring authority granted per §11 scope.

**Signed:** Matt Nichol
**Date:** June 12th 2026
