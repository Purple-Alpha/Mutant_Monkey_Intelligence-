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

## §B.4 — Achieved score (Specialisation Fission Controller #91, 2026-06-12)

Scored against this track on closure. Full suite **1722 passed / 1 skipped / 43 xfailed**; gate-clean 0/0; 3 test classes; net-new-type sign-off metastasis path passes.

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | `SpecialisationFissionController.propose()` validates in order and fails safe: watcher-only trigger, Level 2/HIGH floor, max depth 1, ReconciliationAgent exclusion, and child-count cap; failure logs `REJECTED` and spawns nothing. −1: live Mode Controller threat feed deferred (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Every activated child is born with BRC registration metadata: scoped token/tenant/tool scope, Ring 0, role-tiered budget, and per-child breaker key; children cannot fission. −1: live BRC service registration remains deferred integration. |
| 3 — Segmentation & Isolation (20) | 19 | Each specialised child gets a separate namespace and can write only proposed evidence there; attempts to write parent namespace, verdict surface, or blocking recommendation are rejected. −1: live blackboard namespace provisioning deferred. |
| 4 — Zero Trust & Identity (15) | 14 | Known sub-types spawn under gates; net-new types are held inert until Matt/OPERATOR sign-off via RoleSeparation, then activate at Ring 0 and enter the registry; registry cannot grow autonomously. −1: real-tenant divergence/cap calibration deferred (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Reuses shared append-only `FissionEventLog`; records spawn, sign-off hold/grant, exhale, and rejection; §11 contract + row #91 + 3 test classes + gate-clean. −1: durable shared event-log persistence deferred. |
| **Composite** | **95** | **ELITE** — clears the SF-D14 85+ bar. |

---

## §B.5 — Achieved score (Safe-Stop State Machine #94, 2026-06-14)

Scored against this track on closure. Full suite **1776 passed / 1 skipped / 54 xfailed** at its gate; Grok completion gate-clean 0/0 (comprehensive); 3 test classes; SS-INV-1..SS-INV-12 each have a named falsifiable test (36 passed, 5 documented strict xfail).

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | Entry protocol writes the entry record **before** any halt action (proof-of-entry); epoch is frozen, never incremented, on entry; halts dispatch through the gateway `ModeCheck` seam (`is_dispatch_allowed`) with no bypass. −1: live gateway wiring of the seam deferred (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Restraint enforced inside safe-stop: forbidden vs permitted action sets are disjoint by construction; SS-1 120s / SS-3 300s timers and the 60s reconciliation grace are bounded and logged; no new processing occurs. −1: durable separate-infra log store deferred (xfail). |
| 3 — Segmentation & Isolation (20) | 19 | All active tenant ids captured at entry; cross-tenant broadcast is a forbidden action inside safe-stop; SS-4 fires only on uncontained boundary violation. −1: gateway-wide egress enforcement deferred (xfail). |
| 4 — Zero Trust & Identity (15) | 14 | Exit requires operator authorization (Matt only, OQ-3); a non-operator exit attempt raises `SafeStopAuthorityError`; recovery/epoch increment delegated to the Mode Controller seam, never self-authorized. −1: automated per-condition proof verification deferred (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only immutable `SafeStopLog` (no update/delete API), entry record = proof of entry; §11 contract + row #94 + 3 test classes + gate-clean 0/0. −1: durable persistence deferred (xfail). |
| **Composite** | **95** | **ELITE** — clears the 85+ bar. |

---

## §B.6 — Achieved score (Mode Controller #92, 2026-06-14)

Scored against this track on closure. Full suite **1796 passed / 1 skipped / 57 xfailed** at its gate; Grok completion gate-clean 0/0 (comprehensive); 3 test classes (20 passed, 3 documented strict xfail).

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | `ModeController.request_transition()` is the single mode-change path; only defined §3 transitions are allowed; satisfies the gateway `ModeCheck` seam (local dispatch continues in every mode by design). −1: live cross-region consensus deferred to Lung (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Transitions require a quorum of ≥2 distinct independent control-plane observers (MC-D4); minimum per-mode dwell prevents flapping (MC-D8); the epoch is monotonic and incremented only by the controller (MC-D2/MC-D3). −1: threshold/quorum calibration deferred to signed amendment (xfail). |
| 3 — Segmentation & Isolation (20) | 19 | Tenant-side `TenantModeView` falls back to local ISOLATED on heartbeat loss **without** epoch increment (MC-D6); cross-tenant operations are NORMAL-only; RECOVERING blocks new sharing until validated (MC-D7). −1: live multi-tenant heartbeat transport deferred. |
| 4 — Zero Trust & Identity (15) | 14 | Agent opacity (MC-D5): an agent-sourced vote is rejected and logged, never counted; the epoch cannot be forged or decremented (no external setter; forge attempt raises + logs). −1: real-tenant homeostasis calibration deferred (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only immutable `ModeTransitionLog` records every transition with prev/new mode, epoch before/after, trigger, and agreeing observers (MC-D9); §14 contract + row #92 + 3 test classes + gate-clean 0/0. −1: durable persistence deferred. |
| **Composite** | **95** | **ELITE** — clears the §13 85+ bar. |

---

## §B.7 — Achieved score (Privacy Filter #93, 2026-06-14)

Scored against this track on closure. Full suite **1813 passed / 1 skipped / 60 xfailed** at its gate; Grok completion gate-clean 0/0; 3 test classes (17 passed, 3 documented strict xfail).

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | The mandatory five-stage pipeline runs in order with no skippable stage and no shortcut (PF-D4); `filter()` is the single entry; every failure condition fails closed (PF-D2). −1: broadcast-engine integration is interface-level (the engine is a separate component, §1). |
| 2 — Breaker & Budget Enforcement (25) | 24 | Own breaker key via `privacy_filter_breaker_key` (PF-D3/BRC-D5); OPEN means silence with no fallback path (PF-D2); an audit-write failure trips the filter's own breaker (§4). −1: live health-check/latency breaker triggers deferred. |
| 3 — Segmentation & Isolation (20) | 19 | Two independent failure domains proven (a broadcast-engine breaker trip does not open the filter breaker and vice versa); the no-raw-identifier invariant (PF-D5) is enforced by transformation and proven by validation re-scan. −1: cross-region coordination deferred to Lung (xfail). |
| 4 — Zero Trust & Identity (15) | 14 | Per-tenant policy is authoritative with no global permissive default; absent/ambiguous policy, missing PIPEDA consent, scope NONE, and ineligible signal types all fail closed (PF-D6/PF-D8/§6). −1: tenant consent-management workflow deferred to Playhouse (xfail). |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only immutable audit as pipeline stage 5 — an operation that cannot be audited does not complete (PF-D7); blocked operations logged with equal rigor (PF-D9); §15 contract + row #93 + 3 test classes + gate-clean 0/0. −1: full PIPEDA legal-review audit deferred (xfail). |
| **Composite** | **95** | **ELITE** — clears the §14 85+ bar. |

---

## §B.8 — Achieved score (Collective Immune System #95, 2026-06-14)

Scored against this track on closure. Related control-plane suites **156 passed / 20 xfailed** before Grok gate; CIS focused suite **32 passed / 1 xfailed**; Codex post-build review found no discrete correctness issue after the review loop fixes.

| Component | Score | Evidence |
|---|---:|---|
| 1 — Gateway Integrity (25) | 24 | `CollectiveImmuneSystemCoordinator.coordinate()` enforces the four signed escalation levels and their trigger preconditions; L1 has no cross-component notification; L2 requires two correlated components or a ReconciliationAgent named conflict; L3 requires cross-tenant/systemic/control-plane/degraded-mode proof; L4 requires SS-1..SS-5. −1: live BRC receipt proof is caller-supplied, deferred to the cross-organ telemetry standard (xfail). |
| 2 — Breaker & Budget Enforcement (25) | 24 | CIS cannot initiate fission, authorize mutation, increment epoch, or produce verdicts; mutation suspension is emitted only at L3+ as a coordination action; watcher-triggered fission is acknowledged only with Watcher evidence. −1: live component calls are not wired by this contract. |
| 3 — Segmentation & Isolation (20) | 19 | Every evidence handoff requires non-empty tenant scope; payloads are immutable copies; raw tenant identifiers are rejected in payload keys and values; L2 rejects multi-tenant scope. −1: tenant-scope proof is structural in the request, not cryptographic. |
| 4 — Zero Trust & Identity (15) | 14 | Authorized handoff paths are closed over source, target, and escalation level; unlisted paths and wrong-level endpoint pairs are blocked and logged; BRC lifecycle verification is opt-in and missing proof fails closed. −1: signed component identities are enum-level, not mTLS/JWT-backed. |
| 5 — Governance & Audit Completeness (15) | 14 | Append-only immutable `CollectiveImmuneSystemLog`; level transition logs precede component notifications; durable JSONL write succeeds before in-memory append; after Safe-Stop handoff CIS produces no further records. §11 contract + row #95 + 3 test classes. −1: durable cross-process log store deferred. |
| **Composite** | **95** | **ELITE** — clears the 85+ bar. |

---

## §C — Which track applies

- **Detection / verification agents** (Layer 1-3, e.g. #78-83) — the original five-component detection track, unchanged.
- **ReconciliationAgent** (#84, Layer 4) — the Layer 4 amendment track.
- **Mutation Engine** (#88, Layer 5) — the Layer 5 amendment track.
- **Blast Radius Controller** (#89, Layer 6) — this track.
- **Watcher Agents** (#85-87, Layer 6 Governance) — this track (scored as one governance-observer ensemble, §B.2).
- **Load Fission Controller** (#90, Layer 6 Control Plane) — this track (§B.3).
- **Specialisation Fission Controller** (#91, Layer 6 Control Plane) — this track (§B.4).
- **Safe-Stop State Machine** (#94, Layer 6 Control Plane) — this track (§B.5).
- **Mode Controller** (#92, Layer 6 Control Plane) — this track (§B.6).
- **Privacy Filter** (#93, Layer 6 Control Plane) — this track (§B.7).
- **Collective Immune System** (#95, Layer 6 Control Plane) — this track (§B.8).
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
