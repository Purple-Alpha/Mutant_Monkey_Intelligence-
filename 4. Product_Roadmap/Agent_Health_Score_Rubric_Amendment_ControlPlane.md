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

## §B.1 — Achieved score (Blast Radius Controller #89, 2026-06-12)

Scored against this track on closure. Full suite **1658 passed / 1 skipped / 31 xfailed**; gate-clean 0/0; 3 test classes per component; all five metastasis tests pass.

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | `GatewayController.handle()` walks the full §3.6 lifecycle in sequence; rejection at any gate raises before dispatch (`test_no_partial_dispatch_on_rejection`); fail-safe reject + audit on every gate. −1: live Mode Controller quorum is interface-only here (BRC-D10 xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Trip-class recovery proven (transient→sustained reclassification, sustained cooldown reset, ReconciliationAgent sustained default); role-tiered budgets + 50K per-voter sub-budget no-borrow; `incomplete_budget_exhausted` + governance record, sticky, blocks `may_issue_decision`. −1: wall-clock charged by caller-supplied elapsed, live timer deferred (xfail). |
| 3 — Segmentation & Isolation (20) | 19 | Per-tenant queues/rate-limits/credentials with no cascade; forged `tenant_id` rejected; privacy filter independent failure domain (own breaker key, ordinary breaker trip does not block broadcast). −1: vault-managed credentials deferred (xfail). |
| 4 — Zero Trust & Identity (15) | 14 | Cross-agent token, tenant-scope, tool-scope, and revocation all rejected at gateway regardless of payload; ring promotion requires out-of-band verification (forged telemetry refused). −1: cryptographic identity (mTLS/JWT/SPIFFE) deferred to hardening (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only `ControlPlaneAuditTrail` on every gate transition, breaker trip, budget exhaustion, broadcast block, and ring promotion attempt; §11 contract + row #89 + 3 test classes/component + gate-clean; Mode Controller / Privacy Filter interfaces defined not built. −1: audit is in-process, persistence deferred (xfail). |
| **Composite** | **95** | **ELITE** — clears the BRC-D11 85+ bar. |

---

## §B.2 — Achieved score (Watcher Agents #85-87, 2026-06-12)

The three Watchers are scored as one Layer 6 Governance ensemble against this track (the control-plane track covers governance observers; the components map onto observation integrity, threat-classification consensus, isolation, and audit completeness). Full suite **1699 passed / 1 skipped / 39 xfailed**; gate-clean 0/0; 3 test classes per component; all four mandated adversarial tests pass.

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | Watchers write only to the `ObservationLog`; the neutral-observer boundary is enforced actively (`write_blackboard` / `influence_verdict` / `message_agent` / `make_recommendation` all raise `WatcherBoundaryError`) and per-lane (a watcher cannot emit outside its allowed observation types). −1: gateway egress policy for watcher identities deferred (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | `WatcherResourceController` holds disjoint watcher/agent quota pools with separate credentials; an agent exhausting its budget leaves watcher capacity intact (WA-D6 A4 test); agent credentials cannot draw the watcher pool. −1: physical separate-infrastructure provisioning deferred (xfail). |
| 3 — Segmentation & Isolation (20) | 19 | IntegrityWatcher reports cross-tenant reads CRITICAL and writes-outside-assigned-type as schema violations; observes and reports only, never blocks or mutates the ledger. −1: deep N-cycle ledger-graph analysis deferred (xfail). |
| 4 — Zero Trust & Identity (15) | 14 | `ThreatLevelClassifier` requires ≥2 independent watchers to escalate above ROUTINE (WA-D2), no single watcher forces a change (WA-D3), and only registered watcher ids may submit — agents have zero influence (WA-D8). −1: real-tenant threat-signal calibration deferred (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only immutable `ObservationLog` separate from `core/blackboard/` (WA-D4, no update/delete API); closed observation enum; `EscalationRouter` routes INFO/WARNING/CRITICAL with CRITICAL direct to Matt, no queue/delay (WA-D5); §11 contract + rows #85-87 + 3 test classes/component + gate-clean. −1: live notification transport + durable store deferred (xfail). |
| **Composite** | **95** | **ELITE** — clears the WA-D9 85+ bar. |

---

## §B.3 — Achieved score (Load Fission Controller #90, 2026-06-12)

Scored against this track on closure. Full suite **1709 passed / 1 skipped / 41 xfailed**; gate-clean 0/0; 3 test classes; lower-risk Load Fission lands the shared event log and child lifecycle wiring first.

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | `LoadFissionController.propose()` validates in order and fails safe: watcher-only trigger, Level 2/HIGH floor, max depth 1, ReconciliationAgent exclusion, conservative copy cap; failure logs `REJECTED` and spawns nothing. −1: live Mode Controller threat feed deferred (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Every child is born with BRC registration metadata: scoped token/tenant/tool scope, `RoleTier.DETECTION`, Ring 0, and per-child `BreakerKey`; children cannot fission. −1: registration is metadata-level, not live BRC service mutation (by design, no BRC surface modified). |
| 3 — Segmentation & Isolation (20) | 19 | Each child receives a separate namespace and can write only proposed evidence to that namespace; attempts to write parent namespace, verdict surface, or blocking recommendation are rejected. −1: live blackboard namespace provisioning deferred (xfail-equivalent integration boundary). |
| 4 — Zero Trust & Identity (15) | 14 | Only registered watcher ids may trigger fission (WA-D1); agent self-trigger rejected; Level 2 floor applies to all layers including knowledge agents. −1: real-tenant saturation/copy-cap calibration deferred (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Shared append-only `FissionEventLog` records spawn, exhale, proposed-evidence, and rejection events; automatic exhale below Level 2 records each retired child; §11 contract + row #90 + 3 test classes + gate-clean. −1: durable shared event-log persistence deferred. |
| **Composite** | **95** | **ELITE** — clears the LF-D12 85+ bar. |

---

## §C — Which track applies

- **Detection / verification agents** (Layer 1-3, e.g. #78-83) — the original five-component detection track, unchanged.
- **ReconciliationAgent** (#84, Layer 4) — the Layer 4 amendment track.
- **Mutation Engine** (#88, Layer 5) — the Layer 5 amendment track.
- **Blast Radius Controller** (#89, Layer 6) — this track.
- **Watcher Agents** (#85-87, Layer 6 Governance) — this track (scored as one governance-observer ensemble, §B.2).
- **Load Fission Controller** (#90, Layer 6 Control Plane) — this track (§B.3).
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
