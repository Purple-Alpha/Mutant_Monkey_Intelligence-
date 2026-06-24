# MMI Research Closeout — Mesh Hardening (Stage A · a05 · MMI-DEC-131)

**Classification:** `RESEARCH_INPUT` · `ADVISORY_MEMO` · `ZERO_ROUTING_INFLUENCE` · `NOT_BUILD_AUTHORIZATION`

**Status:** Research lane **CLOSED** for mesh hardening open items (pricing, copy caps, legal consent, protobuf). Parent addendum remains **CONCEPT ONLY**.

**Authority anchor:** `mmi/concepts/MMI_IMMUNE_FEDERATION_MESH_HARDENING_ADDENDUM.md` (MMI-CON-2026-06-24-A)

**Source:** Research lane handover (Gemini+ChatGPT advisory) → Cursor execution filing

**Date:** 2026-06-24

**Boundary:** No production mesh code in authority repo. No `GOVERNED_AGENT`. No AUTH-5. Simulation throughput figures below are **research advisory** until Stage B signed contract + gated implementation.

---

## 1. Executive summary

Stage A waypoint **a05** closes the pre-contract research gaps on Immune Federation Mesh hardening. Findings reconcile to the signed-operator hardening addendum (Guardrail 11, HMAC egress, anti-poisoning, replay/TTL, consent modes, revised economics). **Next chain step:** Stage B **`b01`** mesh contract draft — not production deployment.

---

## 2. Open-item closeout register

| Pre-a05 gap | Disposition | Where locked |
|---|---|---|
| **Pricing / economics** | CLOSED | Addendum §11 + §8D; this memo §5 |
| **Copy caps** | CLOSED (contract input) | Addendum §8D compute abuse guard; memo §5–6 — explicit numeric copy cap deferred to signed mesh contract |
| **Legal consent** | CLOSED (concept) | Addendum §10 tenant mesh states; live legal artifact still **Matt §11 / counsel** at contract time |
| **Protobuf / schema** | CLOSED (draft input) | Addendum §9 replay fields + §13 schema patch |

---

## 3. Guardrail 11 and schema (research validation)

Research confirms alignment with addendum §5–§7, §12–§13:

- **Strict isolation:** Pulse egress carries HMAC fingerprints, enums, TTL, trust tier — never raw email, vendor names, payment fields, or investigation notes.
- **Keyed HMAC:** Replace plain SHA-256 on low-entropy indicators; rotate `mesh_epoch_key` per MSP pool; `source_tenant_tag` not globally stable.
- **ReconciliationAgent `#84`:** Signs **sanitized envelope only** — not raw evidence, not cross-tenant visibility authorization.
- **Schema enforcement:** Egress JSON/protobuf omits PII-class fields; gateway + RA validation before bus publish.

Industry framing (NIST CTI anonymization, webhook replay hygiene) supports the addendum direction — **research citation only**, not new authority.

---

## 4. Anti-poisoning, replay, TTL (research validation)

| Control | Addendum rule | Research note |
|---|---|---|
| Minimum evidence | ≥2 independent signal families (§8A) | Trust tier LOW/MEDIUM/HIGH gates local response |
| RA signature | Sanitized pulse only (§8B) | No global tenant visibility |
| Compute abuse | Local rate limits, budgets, Safe-Stop (§8D) | Pulses advise; Mode Controller `#92` decides |
| Replay | `pulse_id`, `issued_at`, `expires_at`, `key_epoch` (§9) | Reject expired, duplicate, skewed clocks |
| TTL defaults | 6h / 24h / 72h by breath tier (§9) | Matches webhook-style freshness windows |

---

## 5. Economic model and token accounting (pricing closeout)

**Revised thesis (addendum §11 — retained):**

> Marginal cost of recognizing a previously synthesized campaign drops from deep LLM analysis toward cheap deterministic verification. First tenant pays synthesis; opted-in peers get bounded matching — **never** originating tenant data.

**Tiered volume economics (research input):**

- First deep analysis (“one breath”) bears full LLM cost on origin tenant.
- Subsequent peers incur primarily deterministic matching cost — volume discounts at MSP-pool scale are a **commercial design input**, not locked pricing.
- **Token Usage Tracker `#71`** must attribute surge compute to the tenant that inhaled — prevents free-riding on mesh coordination.

**Copy caps (research closeout):**

- Mesh pulses must not force unbounded Lung inflation on peers (addendum §8D).
- Research recommends explicit **per-tenant mesh-triggered copy ceiling** in signed contract (numeric cap **TBD at b01** — e.g. max concurrent inflated copies per pulse tier).
- Mode Controller enforces local quotas + Safe-Stop timers regardless of mesh trust tier.

---

## 6. Simulation findings (advisory — not authority-repo artifacts)

Research lane reported simulation outcomes for topology hardening (Alpha/Beta/Gamma). **No mesh simulation code or logs are filed in `/home/socialarchitect/northstar` at this closeout.** Treat as design pressure-test input only:

| Finding (advisory) | Use |
|---|---|
| Baseline ~14% degradation under extreme concurrency stress | Informed redundancy discussion |
| Gamma-style full redundancy → <1.2% degradation in sim | Candidate topology for contract appendix |
| ~8 ms crypto/handshake overhead per pulse | Within acceptable band for async mesh bus |
| Automated multi-path failover — no single-node cascade in sim | Failover requirements for b01 spec |

**Operational risks (carry to Stage B contract):**

- Hardware throttling under sustained GPU/CPU load — monitor frequency/temp; Safe-Stop under degraded hardware.
- Dependency drift (proto schema, TLS, event bus) — contract tests + RA signature failure alerts.
- Rate limits + emergency mesh disable drill — Mode Controller + Matt revocation path.

---

## 7. Legal consent (research closeout)

Addendum §10 remains canonical for tenant mesh participation states:

```text
MESH_DISABLED | MESH_RECEIVE_ONLY | MESH_SEND_AND_RECEIVE | MESH_LOCAL_ONLY_DURING_INCIDENT
```

Research closeout: **no separate legal consent doc on disk** — MSP offer + tenant boundary consent language is a **Stage B contract / counsel** deliverable. Federation mesh build remains blocked until `b01` signed contract + Matt §11.

---

## 8. Explicit non-authorization

This closeout does **not** authorize:

- Production mesh implementation or bus deployment
- Registry promotion or GOVERNED_AGENT
- AUTH-5 or autonomous mesh-triggered inflation without local confirmation
- Treating simulation figures as verified production SLAs
- Stage A end (MMI-DEC-130) — separate Matt milestone (**a06**)

---

## 9. Handoff to implementation path (Stage B — not started)

When Matt unparks Stage B:

1. **`b01`** — draft Immune Federation Mesh signed contract using addendum §5–§14 + this memo as feedstock.
2. Pre-build gate → §11 → separate build authorization → gated implementation.

Matt Nichol — research closeout filed by Cursor (MMI-DEC-131).
