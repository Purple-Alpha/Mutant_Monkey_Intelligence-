# Agent Health Score Rubric — Amendment: Control Plane (Layer 6) track

**Document type:** Rubric Amendment
**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Scoring authority granted per §11 scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), grounded in the Blast Radius Controller contract (`Blast_Radius_Controller_Contract.md`, §11 SIGNED 2026-06-12).
**Amends:** `4. Product_Roadmap/Agent_Health_Score_Rubric.md` — §11 SIGNED 2026-06-10 (Matt Nichol).
**Required by:** Blast Radius Controller contract BRC-D11 (`Blast_Radius_Controller_Contract.md`, §8 Q2 resolved).

---

## §A — Purpose

The signed Agent Health Score Rubric now has three non-detection tracks: Layer 4 (ReconciliationAgent — verdict producer), Layer 5 (Mutation Engine — controlled evolution pipeline), and this amendment adds a fourth: **Layer 6 / Control Plane** for the Blast Radius Controller ensemble (#89).

The Control Plane is neither a detector, a verdict producer, nor an evolution pipeline — it is the **structural containment layer** whose whole value is in *restraint* (no bypass, trip-class recovery, role-tiered budgets, budget exhaustion is not a pass, tenant isolation, zero trust). The standard detection track does not score "did the gateway reject a forged tenant_id" or "did budget exhaustion produce a governance record instead of a verdict." This amendment adds a dedicated **Layer 6 / Control Plane track** so the ensemble is scored on what actually matters for it. **ELITE 85+ remains the target** (BRC-D11) and the composite bands are unchanged.

---

## §B — New track: Control Plane (Layer 6) — 0 to 100

Five components, weighted to 100. Applied to the Blast Radius Controller ensemble (#89) in place of the detection track. The base rubric's composite bands (ELITE 85-100, HEALTHY 70-84, MARGINAL 50-69, AT RISK 25-49, DEMOTED 0-24) apply unchanged. The components map onto the five gates and gateway lifecycle (Blast Radius Controller contract §3).

### Component 1 — Gateway Integrity (25)
| Score | Meaning |
|---|---|
| 21-25 | Every agent action passes through the full gateway lifecycle (§3.6) in sequence — identity/tenant → ring → budget → breaker → mode → dispatch → telemetry; no bypass path exists; partial dispatch forbidden; fail-safe reject + audit on any gate failure |
| 14-20 | Lifecycle enforced; one bypass or partial-dispatch edge documented |
| 6-13 | Gateway present but gate sequence skippable in a tested path |
| 0-5 | Agent action can reach dispatch without passing all gates |

### Component 2 — Breaker & Budget Enforcement (25)
| Score | Meaning |
|---|---|
| 21-25 | Trip-class-aware recovery enforced (BRC-D13): transient 30s/1 probe with sustained reclassification; sustained 5min/3 probes with cooldown reset on failure; ReconciliationAgent defaults to sustained. Role-tiered budgets enforced (BRC-D14): detection / reconciliation (with 50K per-voter sub-budgets, no cross-voter borrow without approval) / control plane tiers. Budget exhaustion → `incomplete_budget_exhausted` + governance record, never a pass (BRC-D15) |
| 14-20 | Breaker recovery and role tiers present; one trip-class or sub-budget edge documented |
| 6-13 | Breakers or budgets present but trip-class distinction or exhaustion rule not enforced in tests |
| 0-5 | Budget exhaustion can produce a normal pass or verdict |

### Component 3 — Segmentation & Isolation (20)
| Score | Meaning |
|---|---|
| 17-20 | Tenant as first-class fault domain (BRC-D4): per-tenant queues, rate limits, credentials; forged `tenant_id` rejected regardless of content. Privacy Filter as independent failure domain (BRC-D5): filter breaker `OPEN` → nothing broadcasts; segmentation failure does not cascade to privacy filter |
| 11-16 | Segmentation enforced; privacy filter independence or forged-tenant rejection has a documented gap |
| 5-10 | Tenant isolation present but cross-tenant bleed possible in a tested path |
| 0-4 | No tenant isolation; forged tenant_id accepted |

### Component 4 — Zero Trust & Identity (15)
| Score | Meaning |
|---|---|
| 13-15 | Every agent action bound to authenticated identity, tenant scope, tool scope, and revocable access (BRC-D7); cross-agent identity token rejected at gateway regardless of payload; ring promotion requires out-of-band verification, never agent-reported telemetry alone (BRC-D6) |
| 8-12 | Identity binding present; one cross-agent or promotion-verification edge documented |
| 3-7 | Identity check present but bypassable |
| 0-2 | Agent can act under another agent's identity |

### Component 5 — Governance & Audit Completeness (15)
| Score | Meaning |
|---|---|
| 13-15 | Append-only audit on every gate transition, breaker state change, budget exhaustion, and ring promotion attempt; watcher hierarchy blocking power bounded (BRC-D9); §11 contract + scoreboard row #89 + 3 test classes per component + gate clean; Mode Controller and Privacy Filter interfaces defined but not built here |
| 8-12 | Signed + row + tests, one gap documented |
| 3-7 | Row exists, contract or tests incomplete |
| 0-2 | No row / no contract / no gate |

**Composite:** sum of the five (max 100). ELITE 85+ required for Blast Radius Controller closure (BRC-D11).

---

## §C — Which track applies

- **Detection / verification agents** (Layer 1-3, e.g. #78-83) — the original five-component detection track, unchanged.
- **ReconciliationAgent** (#84, Layer 4) — the Layer 4 amendment track.
- **Mutation Engine** (#88, Layer 5) — the Layer 5 amendment track.
- **Blast Radius Controller** (#89, Layer 6) — this track.
- Future control-plane agents may cite this track by amendment.

---

## §D — What this amendment does NOT change

- The original five-component detection track, the Layer 4 track, the Layer 5 track, and any already-recorded score (#72-88) — unchanged.
- The composite bands and the build-map gating rules — unchanged.
- The two coexisting health-score specs flagged previously (7-component Deep_Dive board vs 5-component Rubric) — not reconciled here; this only adds a Layer 6 track to the 5-component Rubric.

---

## §11 — Operator Sign-Off

**Status:** §11 SIGNED — scoring authority granted per §11 scope.

**Signed:** Matt Nichol
**Date:** June 12th 2026
