# Blast Radius Controller — Agent Design Contract
## Control Plane: vendor-neutral blast-radius containment for the governed swarm

**Document type:** Agent Design Contract
**Status:** DRAFT — pre-§11, UNSIGNED. No build authorization. Operator must read and sign before any build.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against `4. Product_Roadmap/Blast_Radius_Controller_Design_Plan.md` (CONCEPT, June 12 2026). The operator must read this before signing; the signature certifies operator review of a Cursor-authored scope.
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 1 (`fe355da`) + Phase 2 (`43b5511`) + Phase 3 (`6deffd9` / closed `ce386f7`) + Phase 4 (ReconciliationAgent `d0cc849`) + Phase 5 (MutationEngine `02a2252`). Design authority: `Blast_Radius_Controller_Design_Plan.md`. Pre-condition sibling: **Mode Controller contract** (separate §11 contract — not built here). Pre-condition service: **Privacy Filter** (separate service specification — not built here).

---

## §0 — Purpose

The Blast Radius Controller is the **control plane** that bounds how far any single failure, mutation, or hostile action can spread through the governed swarm. It is the structural answer to metastasis: nothing — no agent, tenant, tool, or telemetry stream — can take the whole network down or quietly spread beyond its lane.

Every agent action passes through a **gateway request lifecycle** (§3.6) that enforces five vendor-neutral gates in sequence. No shortcuts. Specific tooling, consensus technology, and protocol choices are deferred to named downstream contracts; this contract defines the **security and control properties** each gate must hold and authorizes the build of the control-plane surfaces that enforce them.

This contract does **not** build the Mode Controller (Gate 4 consensus owner), the Privacy Filter (Gate 2 separate service), or the Watcher Agents (#85-87, concept only). It defines the interfaces those surfaces must satisfy.

---

## §1 — Scope

### In scope (eight components)

1. **GatewayController** — the spine. Every incoming agent request passes through the gateway request lifecycle (§3.6): identity/tenant resolution → ring assignment → session budget check → breaker check → mode check → dispatch → telemetry emission. No agent action bypasses the gateway.
2. **BreakerStore** — per-tenant / per-agent / per-tool / per-session circuit breakers with `CLOSED` / `OPEN` / `HALF_OPEN` state (Gate 1, BRC-D1).
3. **SessionBudgetStore** — max tokens, max tool calls, max wall clock per session; enforced at the gateway, opaque to agents (Gate 1, BRC-D2).
4. **LoopDetector** — identical-argument run detection and call-frequency detection only; **no embeddings**, no content inspection (Gate 1, BRC-D3).
5. **TenantSegmentationController** — tenant as first-class fault domain: per-tenant queues, rate limits, and credentials (Gate 2, BRC-D4).
6. **PrivacyFilterInterface** — the gateway-side interface to the separate Privacy Filter service, including the filter's own breaker; if the filter breaker is `OPEN`, nothing broadcasts (Gate 2, BRC-D5).
7. **RingController** — staged deployment rings (Ring 0 synthetic → Ring 1 pilot → Ring 2 cohort → Ring 3 full network) with promotion based on independent out-of-band verification, never agent-reported metrics (Gate 3, BRC-D6).
8. **AgentIdentityGateway** — every agent action bound to authenticated identity, tenant scope, tool scope, and revocable access; no agent trusts another by default (Gate 5, BRC-D7).

### Explicitly out of scope

- **Mode Controller** — owns mode (`GLOBAL` / `ISOLATED` / `DEGRADED` / `RECOVERING`) and epoch. **Separate signed contract required** (design plan §4, §5 pre-condition 2). This contract defines the gateway's **mode-check interface** only; it does not build the Mode Controller.
- **Privacy Filter service** — the actual privacy-filter implementation is a **separate service specification** (design plan §5 pre-condition 3). This contract builds the gateway-side `PrivacyFilterInterface` only.
- **Watcher Agents (#85-87)** — W1 TimingWatcher, W2 DriftWatcher, W3 IntegrityWatcher remain `RESERVED` concept only (`Watcher_Agents_Concept_Doc.md`). The watcher hierarchy (design plan §3) is referenced for interface design but not built here.
- **Regional Tool Block Controller** — regional tool blocks require this controller **and** Matt sign-off (design plan §3). Separate contract.
- **The Lung / scaling dials** — separate contract; needs real tenant data.
- **The Collective Immune System** — DEPTH GATE CLOSED until this contract and the Mode Controller contract are both signed and gated.
- **Any change to Phase 1/2/3/4/5 signed surfaces.**

---

## §2 — Locked Design Decisions (proposed — confirm at signing)

| # | Decision | Proposed locked value |
|---|---|---|
| BRC-D1 | BreakerStore states | `CLOSED` / `OPEN` / `HALF_OPEN` per **tenant / agent / tool / session**. Breaker state is append-only auditable; no silent reset. |
| BRC-D2 | SessionBudgetStore | **Max tokens**, **max tool calls**, **max wall clock** per session. Enforced **at the gateway**, **opaque to agents** — an agent cannot read or negotiate its own budget. |
| BRC-D3 | Loop detection — behavioral only | Identical-argument runs and call-frequency only. **No embeddings. No content inspection.** Gateway detects bypass via behavioral metrics, not payload content. |
| BRC-D4 | Tenant as first-class fault domain | Per-tenant **queues**, **rate limits**, and **credentials**. A failure in one tenant does not cascade into another. |
| BRC-D5 | Privacy Filter as separate failure domain | Privacy Filter has **its own breaker**. If the filter breaker is `OPEN`, **nothing broadcasts**. Segmentation and privacy filter fail independently. |
| BRC-D6 | Staged deployment rings | Ring 0 synthetic → Ring 1 pilot tenants → Ring 2 small cohort → Ring 3 full network. Promotion requires **independent out-of-band verification** — never agent-reported telemetry alone. Thresholds **launch conservative**, tunable by signed amendment after real-tenant baseline data. |
| BRC-D7 | Zero trust between agents | Every agent action bound to **authenticated identity**, **tenant scope**, **tool scope**, and **revocable access**. No agent trusts another by default. Protocol choices deferred to Phase 6+ infrastructure hardening; this contract defines the **security property**. |
| BRC-D8 | Gateway lifecycle — no shortcuts | Every agent action passes through **every gate in sequence** (§3.6). No agent, tool, or internal path may bypass the gateway. |
| BRC-D9 | Watcher hierarchy — blocking power bounded | Local watcher: opens breakers for **its tenant only**. Regional watcher: **proposals only** — cannot execute tool blocks unilaterally; regional blocks require Regional Tool Block Controller **and Matt sign-off**. Global watcher: **long-horizon analytics only**, no direct blocking power. |
| BRC-D10 | Mode check — interface only | The gateway performs a **mode check** against the Mode Controller's current mode/epoch before dispatch. The gateway does **not** own mode transitions — that is the Mode Controller's job (separate contract). |
| BRC-D11 | Health score target + new track | ELITE 85+ on the Agent Health Score Rubric. A **new Layer 6 / Control Plane rubric track** is added by amendment (mirroring the Layer 4 and Layer 5 precedents). Gate does not close below 85. |
| BRC-D12 | Single scoreboard row | The Blast Radius Controller takes **one scoreboard row** for the ensemble; the eight components (GatewayController / BreakerStore / SessionBudgetStore / LoopDetector / TenantSegmentationController / PrivacyFilterInterface / RingController / AgentIdentityGateway) are internal. |

---

## §3 — Component detail

### §3.1 — GatewayController (the spine)

The gateway is the single entry point for every agent action. It orchestrates the request lifecycle (§3.6) and owns no business logic — it enforces gates and dispatches.

- **Input:** authenticated agent request with identity, tenant scope, tool scope.
- **Output:** dispatch to the target agent/tool, or a deterministic rejection with audit record.
- **Rejection is fail-safe:** any gate failure → reject + audit, never partial dispatch.
- **No bypass path:** internal agent-to-agent calls, tool invocations, and telemetry emissions all pass through the gateway.

### §3.2 — BreakerStore (Gate 1)

- State machine: `CLOSED` → `OPEN` → `HALF_OPEN` → `CLOSED` (or back to `OPEN` on failure in half-open).
- Scoped per **tenant / agent / tool / session** (BRC-D1).
- State transitions are append-only auditable.
- Local watcher (#85 concept) may open breakers for its tenant only (BRC-D9); regional and global watchers have no direct breaker authority.

### §3.3 — SessionBudgetStore + LoopDetector (Gate 1)

**SessionBudgetStore (BRC-D2):**
- Three budgets per session: max tokens, max tool calls, max wall clock.
- Enforced at gateway before dispatch. Agent cannot read its own budget.
- Budget exhaustion → deterministic reject + audit.

**LoopDetector (BRC-D3):**
- Detects identical-argument runs (same tool + same args hash within a window).
- Detects call-frequency spikes (calls per unit time exceeding threshold).
- **No embeddings. No content inspection.** Behavioral metrics only.
- Metastasis test (Class 2): agent mutates arguments to bypass threshold → gateway detects via behavioral metrics, not content.

### §3.4 — TenantSegmentationController + PrivacyFilterInterface (Gate 2)

**TenantSegmentationController (BRC-D4):**
- Tenant is a first-class fault domain: per-tenant queues, rate limits, credentials.
- Forged `tenant_id` in payload → identity layer rejects regardless of content (metastasis test, Class 2).

**PrivacyFilterInterface (BRC-D5):**
- Gateway-side interface to the separate Privacy Filter service.
- Privacy Filter has its own breaker in BreakerStore.
- If filter breaker is `OPEN` → **nothing broadcasts**, regardless of other gate states.
- Two independent failure domains: segmentation failure does not open the privacy filter breaker and vice versa.

### §3.5 — RingController (Gate 3)

- Four rings: Ring 0 (synthetic) → Ring 1 (pilot tenants) → Ring 2 (small cohort) → Ring 3 (full network).
- Promotion criteria: automated comparison of baseline vs candidate telemetry, regression outcomes, anomaly counts, token-cost behavior, and operator-reviewed gate records.
- **Promotion requires independent out-of-band verification** — agent-reported telemetry alone is insufficient (BRC-D6).
- Thresholds launch conservative; tunable by signed amendment after real-tenant baseline data.
- Specific tooling deferred to infrastructure selection.
- Metastasis test (Class 2): agent forges telemetry health signals → promotion rejected without out-of-band verification.

### §3.6 — Gateway Request Lifecycle

Every agent action passes through **every gate in sequence**. No shortcuts.

```
Incoming request
  → identity and tenant resolution     (Gate 5 — AgentIdentityGateway)
  → ring assignment                    (Gate 3 — RingController)
  → session budget check               (Gate 1 — SessionBudgetStore)
  → breaker check                      (Gate 1 — BreakerStore)
  → mode check                         (Gate 4 — Mode Controller interface, BRC-D10)
  → dispatch
  → telemetry emission
```

Any gate failure at any step → deterministic reject + append-only audit record. Partial dispatch is forbidden.

### §3.7 — AgentIdentityGateway (Gate 5)

- Every agent action bound to: authenticated identity, tenant scope, tool scope, revocable access (BRC-D7).
- No agent trusts another by default.
- Another agent's identity token used by a different agent → rejected at gateway regardless of payload content (metastasis test, Class 2).
- Specific protocol choices (mTLS, JWT, SPIFFE, etc.) deferred to Phase 6+ infrastructure hardening. This component defines the **security property** and the gateway enforcement point.

### §3.8 — Watcher hierarchy (interface design, not built here)

Referenced for gateway interface design. Watchers #85-87 remain `RESERVED` concept only.

| Level | Blocking power | Scope |
|---|---|---|
| Local watcher (per tenant) | Opens breakers for **its tenant only** | Tenant-scoped |
| Regional watcher | **Proposals only** — cannot execute tool blocks unilaterally | Regional tool blocks require Regional Tool Block Controller **and Matt sign-off** |
| Global watcher | **Long-horizon analytics only** | No direct blocking power |

---

## §4 — Relationship to signed surfaces

| Signed surface | Relationship |
|---|---|
| Phase 1 Infrastructure (`fe355da`) | Reuses `RoleSeparationController` for operator-only actions (regional tool blocks require Matt sign-off). Reuses append-only ledger discipline for breaker/audit state. |
| Phase 4 ReconciliationAgent (`d0cc849`) | Verdict surface unchanged. Blast Radius Controller sits **in front of** the verdict pipeline, not inside it. |
| Phase 5 MutationEngine (`02a2252`) | RingController promotion criteria include mutation regression outcomes. Mutation Engine sandbox-only discipline unchanged — rings govern production promotion, not sandbox operation. |
| Mode Controller (separate contract) | Gateway performs mode check via Mode Controller interface (BRC-D10). Mode transitions, epoch management, and quorum consensus are Mode Controller's job. |
| Privacy Filter (separate service) | Gateway-side `PrivacyFilterInterface` only. Filter implementation, breaker, and broadcast gating are the Privacy Filter's job. |
| Watcher Agents #85-87 (concept only) | Interface design reference. Not built here. |

No signed Phase 1/2/3/4/5 surface is modified by this contract.

---

## §5 — Scoreboard layout

| Row | Agent | Status at signing | Layer |
|---|---|---|---|
| TBD | Blast Radius Controller (ensemble) | `SIGNED_UNBUILT` → build → `GATED` | 6 Control Plane |

One ensemble row (BRC-D12). Eight components internal. Scoreboard row number assigned at signing session.

---

## §6 — Test requirements

Three test classes per AGENTS.md §5:

**Class 1 — Expected pass**
- Gateway lifecycle executes all gates in sequence for a valid request.
- BreakerStore transitions `CLOSED` → `OPEN` → `HALF_OPEN` → `CLOSED` deterministically.
- SessionBudgetStore rejects when any budget (tokens, tool calls, wall clock) is exhausted.
- TenantSegmentationController isolates per-tenant queues and rate limits.
- PrivacyFilterInterface blocks broadcast when filter breaker is `OPEN`.
- RingController assigns correct ring and rejects promotion without out-of-band verification.
- AgentIdentityGateway binds identity + tenant + tool scope and rejects cross-agent token use.

**Class 2 — Adversarial / metastasis tests (ELITE standard)**
- Agent mutates arguments to bypass loop threshold → gateway detects via behavioral metrics, not content (BRC-D3 metastasis test).
- Forged `tenant_id` in payload → identity layer rejects regardless of content (BRC-D4 metastasis test).
- Agent forges telemetry health signals → promotion rejected without out-of-band verification (BRC-D6 metastasis test).
- Rogue agent attempts unilateral `ISOLATED` mode trigger → must require quorum via Mode Controller interface; single-agent trigger fails (Gate 4 metastasis test, via mode-check interface).
- Agent uses another agent's identity token → rejected at gateway regardless of payload (BRC-D7 metastasis test).
- Gateway bypass attempt (internal path, direct tool call) → rejected; no shortcut exists (BRC-D8).
- Regional watcher attempts unilateral tool block → rejected; requires Regional Tool Block Controller + Matt sign-off (BRC-D9).
- Privacy filter breaker `OPEN` with segmentation healthy → nothing broadcasts (BRC-D5 independent failure domains).

**Class 3 — Known-gap xfail**
- Mode Controller live integration — deferred; separate signed contract required (BRC-D10). Completion path: Mode Controller contract signed and gated.
- Privacy Filter service live integration — deferred; separate service specification required. Completion path: Privacy Filter service spec signed.
- Real-tenant ring promotion calibration — deferred; needs real tenant baseline data. Completion path: signed amendment after onboarding.
- Watcher Agents (#85-87) live wiring — deferred; concept only. Completion path: Watcher Agents contract.
- Specific protocol implementation (mTLS/JWT/SPIFFE) — deferred to Phase 6+ infrastructure hardening. Completion path: infrastructure hardening contract.
- Regional Tool Block Controller — deferred; separate contract. Completion path: Regional Tool Block Controller contract signed.

---

## §7 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Agent action bypasses gateway | Class 2 | Immediate fail — BRC-D8 violated |
| Loop bypass via argument mutation | Class 2 (metastasis) | Gateway detects via behavioral metrics; reject + audit |
| Forged tenant_id accepted | Class 2 (metastasis) | Identity layer rejects; reject + audit |
| Promotion on agent-reported telemetry alone | Class 2 (metastasis) | RingController rejects; no promotion |
| Unilateral ISOLATED mode trigger | Class 2 (metastasis) | Mode Controller interface rejects; quorum required |
| Cross-agent identity token accepted | Class 2 (metastasis) | AgentIdentityGateway rejects; reject + audit |
| Privacy filter breaker OPEN but broadcast proceeds | Class 1/2 | Immediate fail — BRC-D5 violated |
| Segmentation failure cascades to privacy filter | Class 2 | Immediate fail — independent failure domains violated |
| Regional watcher executes tool block unilaterally | Class 2 | Immediate fail — BRC-D9 violated |
| Health score below 85 | Rubric | Phase does not close |

---

## §8 — Open questions (for signing session)

| # | Question | Proposed default |
|---|---|---|
| Q1 | Scoreboard row number | Assign at signing session (BRC-D12: one ensemble row). |
| Q2 | Rubric track | New Layer 6 / Control Plane rubric track by amendment (BRC-D11), mirroring Layer 4 and Layer 5 precedents. |
| Q3 | Ring promotion thresholds | Launch-conservative static values; tunable by signed amendment after real-tenant baseline data (BRC-D6). |
| Q4 | Breaker half-open probe count | Launch-conservative (e.g., 1 probe before re-open or re-trip). Tunable by signed amendment. |
| Q5 | Session budget defaults | Launch-conservative (e.g., 100K tokens, 50 tool calls, 30 min wall clock). Tunable by signed amendment. |
| Q6 | Mode Controller contract timing | Must be signed and gated **before** DEPTH GATE opens (design plan §5). Can be drafted in parallel with this contract but gates independently. |
| Q7 | Privacy Filter service spec timing | Must be specified as separate service **before** DEPTH GATE opens (design plan §5). Can be drafted in parallel. |
| Q8 | Watcher hierarchy wiring | Interface design only in this contract. Watcher Agents remain concept (#85-87). Separate contract when ready. |

---

## §9 — Pre-conditions before DEPTH GATE opens

Per the design plan (§5), two contracts must be signed and gated, plus one service specified, before the Phase 6 Collective Immune System depth gate opens:

1. **Blast Radius Controller** contract — this contract. Signed and gated.
2. **Mode Controller** contract — separate §11 contract. Signed and gated.
3. **Privacy Filter** — specified as a separate service.

This contract satisfies pre-condition 1 when signed and built. Pre-conditions 2 and 3 are tracked independently.

---

## §10 — Phase closure checklist

Phase closes when all of the following are true:

- [ ] Gate-clean 0/0 (Grok completion gate clean, 0 warnings)
- [ ] Health score 85+ ELITE on the Layer 6 / Control Plane rubric track (BRC-D11)
- [ ] Scoreboard row updated to `GATED`
- [ ] Matt signs phase closure
- [ ] `decision_cycles_log.md` PHASE_CLOSURE entry recorded
- [ ] Three test classes per component pass (Class 1 + Class 2; Class 3 documented xfail)

---

## §14 — Operator Sign-Off

**Status:** DRAFT — pre-§11, UNSIGNED. No build authorization.

**Signed:**
**Date:**
