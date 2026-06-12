# Mode Controller — Concept Doc

**Document type:** Concept / advisory-lane design note
**Status:** CONCEPT — advisory lane only. **No build authorization.** A §11-signed contract is required before any build.
**Date:** June 12 2026
**Author lane:** Cursor (execution lane), advisory only.

---

## §0 — What this is (and is not)

This is a **concept doc**, not a contract. It captures the Mode Controller model for a future contract session so the design is on disk and reviewable. It authorizes nothing — no code, no scoreboard row, no rubric track. The build path is: this concept → §11 contract (with rubric amendment) → signed → build → gate → GATED.

The **Mode Controller** owns the swarm's operating **mode** and its **epoch**. It is the Graceful Degradation gate (Gate 4) of the Blast Radius Controller, factored out into its own component because mode transition is a consensus problem with its own failure modes. The Blast Radius Controller already performs a *mode check* at the gateway via an interface (BRC-D10); the Mode Controller is the thing behind that interface.

The governing property is **restraint through consensus**: the system as a whole can change how it operates, but **no single agent, watcher, or tenant can force that change.**

---

## §1 — The four modes

| Mode | Meaning | Cross-tenant sharing |
|---|---|---|
| **NORMAL** | Steady state. All gates green, full operation. | Permitted (under Privacy Filter + segmentation). |
| **DEGRADED** | Partial impairment detected. Reduced operation; conservative thresholds; non-essential work shed. | Restricted. |
| **ISOLATED** | Containment. A tenant (or the system) is sealed into its own fault domain — no cross-tenant flow. | **Forbidden.** |
| **RECOVERING** | Controlled reconciliation window after isolation/degradation, on the path back to NORMAL. | **Forbidden until validated** (see §4). |

Mode is a property of the **control plane**, surfaced to the gateway. It is **not a property any agent owns, sets, reads, or negotiates** (§5).

---

## §2 — Epoch-based resolution

Mode is versioned by a monotonically increasing **epoch**.

- **Highest epoch wins.** When observers hold differing views of the current mode, the view carrying the **highest epoch** is authoritative. This makes mode resolution deterministic and partition-tolerant: a stale observer cannot override a newer decision.
- **The Mode Controller is the only component that increments the epoch.** No agent, no watcher, no tenant, and no gateway may increment it. Epoch monotonicity is the single source of truth for "which mode decision is current," and concentrating increment authority in one component is what prevents split-brain.
- An epoch increment accompanies every **Mode-Controller-validated** transition (notably the return to NORMAL, §4). A local ISOLATED transition triggered by heartbeat timeout is the deliberate exception — it does **not** increment the epoch (§3).

---

## §3 — Heartbeat broadcasting and local ISOLATED

The Mode Controller **broadcasts a heartbeat to all tenants** carrying the current (mode, epoch).

- **Heartbeat received** → the tenant's local view tracks the broadcast (mode, epoch); highest epoch wins (§2).
- **Heartbeat timeout** → the tenant **transitions itself to local ISOLATED** as a fail-safe — it seals its own fault domain rather than continuing to act on a possibly-stale global view. Critically, **a heartbeat-timeout ISOLATED transition does NOT increment the epoch.** It is a *local, defensive* containment, not a global mode decision. The global epoch stays where the Mode Controller last set it.

This split is the heart of the design: **going dark is allowed unilaterally and locally** (fail safe, seal yourself), but **coming back, or moving the whole system, is a consensus + epoch event** that only the Mode Controller can ratify. A tenant that lost contact contains itself; it cannot drag the swarm's global mode with it.

---

## §4 — Quorum transitions and the RECOVERING window

### Quorum-style agreement

A **global** mode transition (e.g. NORMAL → DEGRADED, DEGRADED → ISOLATED, or any path back toward NORMAL) requires **quorum-style agreement from multiple independent control-plane observers.** No single agent, watcher, or tenant can force a transition.

- Observers are **independent** — they do not share a failure mode, and one compromised or faulty observer cannot manufacture quorum.
- The Mode Controller collects observer agreement, and only on quorum does it ratify the transition and **increment the epoch** (§2).
- This is the structural defense behind the BRC Gate-4 metastasis test: a **rogue agent attempting to trigger ISOLATED unilaterally must fail** — it has no quorum, and agents have no mode authority at all (§5).

### RECOVERING is a controlled reconciliation window

RECOVERING is **not** a free-for-all return to normal. It is a bounded window in which the system rebuilds trust before reopening cross-tenant flow:

- During RECOVERING, tenants may upload **pattern hashes and anomaly counts only** — compact, privacy-safe signals.
- **No new cross-tenant sharing occurs during RECOVERING.** Nothing crosses a tenant boundary until the Mode Controller has validated the reconciled state.
- When the Mode Controller validates the reconciled state, it **increments the epoch to the NORMAL epoch** and broadcasts it. Only then does cross-tenant sharing resume.

RECOVERING converts "we think it's fine now" into "the Mode Controller validated it and stamped a new epoch." The increment is the proof.

---

## §5 — Agents have zero influence on mode

Stated explicitly because it is non-negotiable:

- **Agents have zero influence on mode.** No agent triggers, votes on, proposes, or accelerates a mode transition.
- **Mode is not exposed to agents.** Agents do not read the mode. The gateway reads the mode (via the Mode Controller interface, BRC-D10) and simply allows or refuses dispatch. An agent experiences mode only as "my action was dispatched" or "my action was refused at the gateway" — never as a value it can branch on or manipulate.

This keeps the entire mode machinery in the control plane, out of reach of anything an adversarial or buggy agent could touch.

---

## §6 — Concept lifecycle sketch

```
Independent observers report health signals to the Mode Controller
  → Mode Controller evaluates quorum
  → quorum reached for a transition?
       → ratify new mode, INCREMENT EPOCH, broadcast heartbeat(mode, epoch)
  → heartbeat to all tenants on every cycle
       → tenant receives → adopt (highest epoch wins)
       → tenant times out → LOCAL ISOLATED (no epoch increment)
  → RECOVERING window:
       tenants upload pattern hashes + anomaly counts only
       no cross-tenant sharing
       → Mode Controller validates → increment to NORMAL epoch → resume sharing
  → gateway performs mode CHECK only (BRC-D10); agents never see mode
```

---

## §7 — Dependencies (must be satisfied before a build contract opens)

| Dependency | Status | Why it gates the Mode Controller |
|---|---|---|
| **Blast Radius Controller** | **GATED** (#89, 2026-06-12) | The Mode Controller is the component behind the gateway's mode-check interface (BRC-D10). The gateway must exist first. |
| **Watcher hierarchy operational** | **Required** | The independent control-plane observers that form quorum draw on the watcher hierarchy (#85-87, currently RESERVED). Without operational watchers there is no independent quorum source. |

**The Mode Controller contract must be signed and gated before the Phase 6 DEPTH GATE opens** (Blast Radius Controller contract §9, pre-condition 2). It may be drafted and built in parallel with other Phase 6 work but it gates independently.

---

## §8 — Relationship to existing surfaces (concept only)

- **Blast Radius Controller (#89)** — Gate 4 (Graceful Degradation) is realized by this component. BRC-D10 defines the gateway-side `ModeCheck` interface (`is_dispatch_allowed(tenant_id)`); the default `AllowAllModeCheck` is the placeholder this contract replaces with a real, quorum-driven, epoch-versioned Mode Controller.
- **Watcher hierarchy (#85-87, RESERVED)** — the source of the independent observers used for quorum, under the same bounded-power discipline (BRC-D9: regional/global watchers cannot act unilaterally).
- **Privacy Filter (separate concept)** — RECOVERING explicitly forbids cross-tenant sharing until validated; when sharing resumes, it still flows through the Privacy Filter's independent breaker. The two components enforce complementary halves of "nothing leaks during containment."

No existing signed surface is modified by this concept. This is a design note awaiting a contract.
