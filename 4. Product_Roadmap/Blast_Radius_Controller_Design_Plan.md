# Blast Radius Controller — Control Plane Design Plan

**Document type:** Design Plan (CONCEPT — advisory lane only)
**Status:** CONCEPT — **advisory lane only. No build authorization. Contract required before build.**
**Date:** June 12, 2026
**Drafted by:** Cursor (execution lane), transcribing the operator-settled session design across the three deep dives plus the session design work. Signature reserved for the operator.
**Authority:** Matt Nichol — sole signing authority
**Relationship:** sits in front of the existing swarm (Phase 1-5 GATED) as a control plane. Adds **no** verdict surface and changes **no** signed Phase 1/2/3/4/5 surface. Vendor-neutral throughout — defines security and control *properties*, not infrastructure choices.
**Purpose of this document:** one clean design plan, ready for the **Blast Radius Controller** contract to be drafted against it.

---

## §0 — Purpose

The Blast Radius Controller is the **control plane** that bounds how far any single failure, mutation, or hostile action can spread through the swarm. It is the structural answer to metastasis: nothing — no agent, tenant, tool, or telemetry stream — can take the whole network down or quietly spread beyond its lane.

Five gates, all **vendor-neutral**, all **phased correctly**. Specific tooling, consensus technology, and protocol choices are deferred to the named downstream contracts. This plan defines the properties each gate must hold. It authorizes no code.

---

## §1 — The Five Gates

### Gate 1 — Circuit Breakers

- **BreakerStore** with `CLOSED` / `OPEN` / `HALF_OPEN` state per **tenant / agent / tool / session**.
- **Loop detection** via identical-argument runs and call-frequency only — **no embeddings**, no content inspection.
- **SessionBudgetStore** with **max tokens**, **max tool calls**, and **max wall clock** per session — enforced **at the gateway**, **opaque to agents** (an agent cannot read or negotiate its own budget).
- **Metastasis test:** simulate an agent attempting to bypass a threshold via **argument mutation** — the gateway must detect it via **behavioral metrics, not content**.

### Gate 2 — Blast Radius Segmentation

- **Tenant is a first-class fault domain.** Per-tenant **queues**, **rate limits**, and **credentials**.
- **Privacy filter as a separate service** with **its own breaker** — if the filter breaker is `OPEN`, **nothing broadcasts**.
- Two **independent** failure domains (segmentation and privacy filter fail separately; neither failure cascades into the other).
- **Metastasis test:** simulate a **forged `tenant_id`** in the payload — the **identity layer must reject** it regardless of content.

### Gate 3 — Staged Deployment Rings

- **Ring 0** synthetic → **Ring 1** pilot tenants → **Ring 2** small cohort → **Ring 3** full network.
- **Promotion** based on automated comparison of **baseline vs candidate telemetry**, **regression outcomes**, **anomaly counts**, **token-cost behavior**, and **operator-reviewed gate records**.
- Specific tooling **deferred to infrastructure selection**.
- Thresholds **launch conservative**, calibrated by **signed amendment** after real-tenant baseline data exists.
- **Metastasis test:** simulate an agent **forging telemetry health signals** — promotion must require **independent out-of-band verification**, never agent-reported metrics.

### Gate 4 — Graceful Degradation

- Four modes: `NORMAL` / `DEGRADED` / `ISOLATED` / `RECOVERING`.
- Mode transitions require **quorum-style agreement** among **independent control-plane observers**. **No single** agent, watcher, tenant, or telemetry stream forces a system-wide transition.
- `RECOVERING` is a **controlled reconciliation window** — tenants upload **pattern hashes and anomaly counts only**, **no new cross-tenant sharing** until the Mode Controller validates and **increments the epoch**.
- Specific consensus technology **deferred to the Lung contract**.
- **Metastasis test:** simulate a rogue agent attempting to trigger `ISOLATED` **unilaterally** — it must require **quorum**; a single-agent trigger must **fail**.

### Gate 5 — Zero Trust Between Agents

- Every agent action bound to **authenticated identity**, **tenant scope**, **tool scope**, and **revocable access**.
- **No agent trusts another by default.**
- Specific protocol choices **deferred to Phase 6+ infrastructure hardening**. This design defines the **security property**, not the implementation.
- **Metastasis test:** simulate an agent attempting to use **another agent's identity token** — it must be **rejected at the gateway** regardless of payload content.

---

## §2 — Gateway Request Lifecycle (the spine everything hangs off)

Every agent action passes through **every gate in sequence**. **No shortcuts.**

```
Incoming request
  → identity and tenant resolution
  → ring assignment
  → session budget check
  → breaker check
  → mode check
  → dispatch
  → telemetry emission
```

---

## §3 — Watcher Hierarchy

- **Local watcher** (per tenant) — opens breakers **for its tenant only**.
- **Regional watcher** — raises **proposals only**; **cannot** execute tool blocks unilaterally. Regional tool blocks require the **Regional Tool Block Controller** **and** **Matt sign-off**.
- **Global watcher** — **long-horizon analytics only**, **no direct blocking power**.

---

## §4 — Mode Controller

- Owns **mode** and **epoch**: `GLOBAL` / `ISOLATED` / `DEGRADED` / `RECOVERING`.
- **Highest epoch wins.**
- **No agent influences mode.**
- **Heartbeat timeout** triggers a **local `ISOLATED` transition without epoch increment**.
- **Recovery** requires the Mode Controller to **validate state before incrementing to the `GLOBAL` epoch**.

---

## §5 — Pre-conditions before the DEPTH GATE opens

Two contracts must be **signed and gated**, plus one service specified, before the Phase 6 depth gate opens:

1. **Blast Radius Controller** contract — signed and gated.
2. **Mode Controller** contract — signed and gated.
3. **Privacy Filter** — specified as a **separate service**.

---

## §6 — Status line

**CONCEPT — advisory lane only. No build authorization. Contract required before build.**

This document records the settled design so the Blast Radius Controller §11 contract session has one clean starting point. Nothing here authorizes code. All tooling, consensus technology, and protocol choices remain deferred to the named downstream contracts (infrastructure selection, the Lung contract, Phase 6+ hardening).
