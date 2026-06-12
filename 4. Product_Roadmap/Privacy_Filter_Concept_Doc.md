# Privacy Filter — Concept Doc

**Document type:** Concept / advisory-lane design note
**Status:** CONCEPT — advisory lane only. **No build authorization.** A §11-signed contract is required before any build.
**Date:** June 12 2026
**Author lane:** Cursor (execution lane), advisory only.

---

## §0 — What this is (and is not)

This is a **concept doc**, not a contract. It captures the Privacy Filter model for a future contract session so the design is on disk and reviewable. It authorizes nothing — no code, no scoreboard row, no rubric track. The build path is: this concept → service specification / §11 contract → signed → build → gate → GATED.

The **Privacy Filter** is a **separate service** that sits between the swarm and any cross-tenant broadcast. The Blast Radius Controller already fronts it with a gateway-side `PrivacyFilterInterface` whose breaker, when OPEN, blocks all broadcast (BRC-D5). This document specifies the service behind that interface.

The governing property is **isolation by construction**: cross-tenant intelligence sharing is valuable, but **no raw tenant identifier may ever cross a tenant boundary**, and the filter is built so that if it is unhealthy, **nothing broadcasts** rather than leaking.

---

## §1 — Separate service, own circuit breaker

- The Privacy Filter is a **separate service**, **completely independent from the broadcast engine.** It is not a function call inside the broadcaster; it is its own service with its own lifecycle and its own circuit breaker.
- **If the Privacy Filter breaker is OPEN, nothing broadcasts.** No fallback path, no "broadcast raw and filter later," no degraded mode that lets unfiltered content out. OPEN means silence.
- **Two independent failure domains.** The Privacy Filter and the broadcast engine fail independently: a broadcast-engine failure does not open the Privacy Filter breaker, and a Privacy Filter failure does not open the broadcast-engine breaker. This independence is what the Blast Radius Controller enforces by giving the filter its own breaker key (BRC-D5) — the filter breaker is never shared with any tenant/agent/tool breaker.

The design bias is deliberate and one-directional: **fail closed.** A filter that is uncertain, overloaded, or down produces *no broadcast*, never an unfiltered one.

---

## §2 — Pipeline

Every item bound for cross-tenant broadcast passes through the full pipeline, in order. No stage is skippable.

```
entity detection → policy lookup → transformation → validation → audit record
```

1. **Entity detection** — identify tenant-identifying entities and any sensitive content in the candidate item (raw identifiers, names, addresses, account numbers, anything that could re-identify a tenant).
2. **Policy lookup** — resolve the applicable **per-tenant sharing policy** (§3) for the originating tenant: what this tenant permits to be shared, at what granularity, with whom.
3. **Transformation** — apply the policy: strip / hash / generalize identifiers so the shareable signal survives but the tenant-identifying content does not. **No raw tenant identifiers may cross tenant boundaries** (§4).
4. **Validation** — verify the transformed output actually satisfies the policy and the no-raw-identifier invariant **before** anything leaves. Validation failure → fail closed (no broadcast), same as an OPEN breaker.
5. **Audit record** — write an append-only record of the operation (§5). The audit record is part of the pipeline, not an afterthought: an operation that cannot be audited does not complete.

---

## §3 — Per-tenant sharing policy

- Each tenant has its **own sharing policy** governing what may be shared across the boundary and in what form.
- Policy is resolved at **policy lookup** (pipeline stage 2) per originating tenant — there is no global "share everything" default.
- A tenant's policy is the authority for the transformation stage; the filter never shares more than the originating tenant's policy permits.
- Absence/ambiguity of policy resolves conservatively (fail closed — do not broadcast) rather than permissively.

---

## §4 — Hard invariant: no raw tenant identifiers cross boundaries

- **No raw tenant identifiers may cross tenant boundaries.** This is an invariant, not a tunable. The transformation stage exists to enforce it and the validation stage exists to prove it before release.
- What crosses a boundary is **derived, privacy-safe signal** (e.g. pattern hashes, anomaly counts, generalized indicators) — never raw identifiers.
- This invariant aligns with the Mode Controller's RECOVERING window, which already restricts cross-tenant uploads to **pattern hashes and anomaly counts only** — the Privacy Filter enforces the same class of constraint on the steady-state broadcast path.

---

## §5 — Every filter operation logged

- **Every filter operation is logged** in an append-only audit record (pipeline stage 5): input reference, originating tenant, policy applied, transformation result, validation outcome, broadcast/blocked decision, timestamp.
- Blocked operations (breaker OPEN, validation failure, policy-conservative refusal) are logged with the same rigor as permitted ones — a refusal to broadcast is a governance event worth recording.
- The audit trail is the evidence that the no-raw-identifier invariant (§4) held on every operation.

---

## §6 — Canadian PIPEDA compliance is a hard requirement

- **Canadian PIPEDA compliance is a hard requirement, not a best practice.** The filter's policies, transformations, and audit records must satisfy PIPEDA obligations as a binding constraint on the design — not as a nice-to-have layered on later.
- This shapes §3 (per-tenant policy must be able to encode PIPEDA-compliant sharing limits), §4 (the no-raw-identifier invariant is a compliance floor, not just a hygiene preference), and §5 (the audit trail must be sufficient to demonstrate compliance).
- The future contract must treat any conflict between "share more signal" and "PIPEDA compliance" as resolved in favour of compliance, every time.

> Scope note (advisory): naming PIPEDA as a hard design constraint is a statement about how this service is built. It is **not** a public compliance claim about NorthStar as a product. Any external-facing compliance statement remains governed by the existing forbidden-language / scope-boundary rules and is out of scope for this concept.

---

## §7 — Dependencies (must be satisfied before a build contract opens)

| Dependency | Status | Why it gates the Privacy Filter |
|---|---|---|
| **Blast Radius Controller** | **GATED** (#89, 2026-06-12) | The filter lives behind the gateway-side `PrivacyFilterInterface` and relies on its own breaker key for the independent-failure-domain guarantee (BRC-D5). The gateway must exist first. |

**The Privacy Filter must be specified as a separate service before the Phase 6 DEPTH GATE opens** (Blast Radius Controller contract §9, pre-condition 3). It may be drafted in parallel with other Phase 6 work.

---

## §8 — Relationship to existing surfaces (concept only)

- **Blast Radius Controller (#89)** — `PrivacyFilterInterface` (BRC-D5) is the gateway-side stub; this service is the implementation behind it. The independent-failure-domain property (own breaker key, never shared) is already enforced at the gateway; this contract must honour it on the service side.
- **Mode Controller (separate concept)** — during RECOVERING, cross-tenant sharing is forbidden until validated, and is then restricted to pattern hashes + anomaly counts. The Privacy Filter enforces the same no-raw-identifier discipline on the NORMAL-mode broadcast path. Together: nothing leaks during containment, and only privacy-safe signal leaks during normal operation.
- **Tenant segmentation (BRC-D4)** — tenant is a first-class fault domain at the gateway; the Privacy Filter is the boundary control for the one path that is *meant* to cross tenants (broadcast), making the no-raw-identifier invariant the cross-boundary counterpart to segmentation's intra-boundary isolation.

No existing signed surface is modified by this concept. This is a design note awaiting a contract / service specification.
