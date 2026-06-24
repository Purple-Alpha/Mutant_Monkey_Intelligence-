# MMI Federation Mesh Pilot Wiring Plan — Opt-In MSP Pool (Stage C · c02 · MMI-DEC-142)

**Classification:** `WIRING_PLAN` · `ADVISORY_MEMO` · `NOT_BUILD_AUTHORIZATION`

**Document Reference:** MMI-PLN-2026-06-24

**Date:** 2026-06-24

**Authority anchor:** `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (§11 SIGNED MMI-DEC-140 · IFM-D1–D12)

**Boundary:** Plan only. Does **not** authorize mesh bus implementation, production dispatch, GOVERNED_AGENT, AUTH-5, live third-party mail, or cross-tenant evidence access.

**Governing principle:**

```text
Shared threat shape.
Never shared tenant truth.
```

---

## 1. Executive summary

This plan defines how an **opted-in MSP federation pool** would wire the Immune Federation Mesh when Matt separately authorizes build — starting with **detect-only, sanitized pulse propagation** across synthetic and then real SMB tenant cells under explicit consent.

**Not** the Todd/CMIT buyer-proof pilot (MMI-DEC-129 remains historical VERIFY). **Not** Lung production (MMI-DEC-133 / MMI-DEC-141 PARK). **Not** locked MSRP (MMI-DEC-132 advisory).

---

## 2. Pilot scope

### 2.1 In scope (wiring plan)

| Item | Description |
|---|---|
| MSP federation pool | Regional opt-in pool (example: Western Canada MSP cohort); pool boundary per MSP mesh pool in IFM-D2/D4 |
| Consent model | Mode Controller `#92` mesh states: `MESH_DISABLED` → `MESH_RECEIVE_ONLY` → `MESH_SEND_AND_RECEIVE` |
| Pulse egress | ReconciliationAgent `#84` sanitized envelope sign → MSP-scoped bus publish |
| Pulse ingress | Local deterministic matching only in pilot Phase 1–2; no peer deep inhale until Lung gates clear |
| Key management | Rotating `mesh_epoch_key` per MSP pool; `source_tenant_tag` HMAC egress |
| Audit plane | Platform attribution, billing linkages, abuse trail — **not** on mesh bus (IFM-D9 class C) |
| Synthetic-first | Phase 0–1 uses fixture/synthetic tenants before any live MSP client mail |

### 2.2 Out of scope (explicit)

| Item | Reason |
|---|---|
| Cross-tenant raw email / evidence | Guardrail 11 · IFM-D1 |
| Autonomous mesh broadcast | Requires RA egress + threshold + consent — no bypass |
| Todd pilot as mesh gate | Commercial detect-only lane separate (INTAKE-2026-06-24-003) |
| Lung Dial production / deep inhale on peers | MMI-DEC-133 · MMI-DEC-141 PARK |
| Locked federation pricing / MSRP | Operator direction only (MMI-DEC-132) |
| GOVERNED_AGENT / default registry / AUTH-5 | System-wide blocks |
| Legal consent artifact finalization | Counsel + Matt §11 at build authorization |

---

## 3. Relationship to Todd intake (contract §13 Q5 resolution)

| Lane | Role |
|---|---|
| **Todd / CMIT intake** (MMI-DEC-129) | Historical commercial detect-only pilot motion — validator feedback, triage time saved, evidence packets. **Does not gate mesh wiring.** |
| **This plan** (MMI-DEC-142) | Technical federation mesh pilot wiring for **opted-in MSP pool** — sanitized pulses, consent, HMAC egress. |

An MSP in the federation pool may later include Todd's clients **only** after separate legal/consent gates and explicit tenant opt-in per IFM-D7 — not implied by either intake alone.

---

## 4. Wiring topology (logical — not built)

```text
┌──────────────── Tenant A (origin) ─────────────────┐
│ Shadow sensors + detection limbs → local threshold   │
│ ReconciliationAgent #84 → sanitized pulse envelope   │
│ Mode Controller #92 → MESH_SEND_AND_RECEIVE check    │
│ Privacy Filter #93 + BRC #89 → egress validation     │
└────────────────────────┬─────────────────────────────┘
                         │ PathogenSignaturePulse (HMAC, TTL, trust tier)
                         ▼
              ┌──────────────────────┐
              │ MSP Federation Pool   │  ← mesh_epoch_key scoped here
              │ (opt-in bus — planned)│
              └──────────┬───────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   Tenant B          Tenant C          Tenant D
   (receive)         (receive)         (send+recv)
   local match       local match       ...
   Mode #92          Mode #92          Mode #92
   Token #71         Token #71         Token #71
```

**No tenant reads another tenant's evidence.** Receiving cells run **local** structural matching inside namespace boundary only.

---

## 5. Component wiring map (GATED substrate → planned mesh)

| Component | Scoreboard | Pilot wiring role | Build status |
|---|---|---|---|
| ReconciliationAgent `#84` | GATED | Sole ME-AUTH egress signatory for sanitized pulses | Exists — mesh egress adapter **not wired** |
| Mode Controller `#92` | GATED + #99 adv. | Mesh consent states IFM-D7; local response tier | Exists — mesh mode enum **not wired** |
| Privacy Filter `#93` | GATED + #98 adv. | Pre-egress sanitization enforcement | Exists |
| Blast Radius Controller `#89` | GATED + #101 adv. | Namespace bounds if local wake triggered | Exists |
| Safe-Stop `#94` | GATED + #102 adv. | Swarm-wide kill; overrides mesh-advised wake | Exists |
| CIS `#95` | GATED | Immune teardown coordination | Exists — not Lung-wired |
| Token Usage Tracker `#71` | INFRASTRUCTURE_BUILT | Local surge attribution IFM-D10 | Exists — reporting only |
| Collective Immune `#95` | GATED | Coordination-only; no cross-tenant visibility | Exists |
| Load Multiplier `#90`/`#103` | GATED | **Pilot: advise only** — log-only / deterministic-match tiers | Exists — **no dial wiring** (MMI-DEC-141) |
| Mesh bus / pulse transport | — | MSP-scoped publish/subscribe | **NOT BUILT** |
| HMAC key epoch service | — | `mesh_epoch_key` rotation per pool | **NOT BUILT** |
| Pulse replay guard | — | `pulse_id` dedup, TTL, clock skew | **NOT BUILT** |

---

## 6. Phased pilot plan

| Phase | Name | Tenants | Mesh I/O | Local response | Gate to advance |
|---|---|---|---|---|---|
| **P0** | Design + fixtures | Synthetic only | None | N/A | This plan filed (MMI-DEC-142) |
| **P1** | Sandbox bus | Synthetic multi-tenant fixtures | Send/receive pulses in isolated sandbox | `LOG_ONLY` + `DETERMINISTIC_MATCH_ONLY` | Matt Build Authorization + pre-build gate 0/0 |
| **P2** | Opt-in MSP pool pilot | 2+ real SMB cells, explicit consent | `MESH_RECEIVE_ONLY` or `MESH_SEND_AND_RECEIVE` per tenant | Trust tier caps; **no deep inhale** | Legal consent artifact + Matt §11 amendment if needed |
| **P3** | Federation scale | Pool growth | Full consent modes incl. incident-local | `LIGHT_LOCAL_WAKE` per Mode Controller | Lung prerequisites (MMI-DEC-133) + numeric copy cap lock |

**Rule:** Phase N+1 does not open until Phase N evidence is logged in `MMI_DECISION_LOG.md` and Matt authorizes explicitly.

---

## 7. Pulse lifecycle (pilot wiring spec)

### 7.1 Origin egress (send path)

1. Local detection produces ≥2 independent signal families (IFM-D3).
2. Sanitization strips all class-B/C fields (IFM-D9).
3. HMAC fingerprints + `source_tenant_tag` generated with pool `mesh_epoch_key` (IFM-D2/D4).
4. ReconciliationAgent `#84` signs sanitized envelope only (IFM-D5).
5. Mode Controller confirms `MESH_SEND_AND_RECEIVE` or `MESH_LOCAL_ONLY_DURING_INCIDENT` not blocking send.
6. Privacy Filter + BRC validate egress boundary.
7. Pulse published with `pulse_id`, `issued_at`, `expires_at`, `schema_version`, `key_epoch`, trust tier, response permission (IFM-D6/D9).

### 7.2 Receive path (pilot default)

1. Mode Controller confirms tenant `MESH_RECEIVE_ONLY` or `MESH_SEND_AND_RECEIVE`.
2. Reject expired, duplicate, or skewed pulses.
3. Map trust tier → local action: `LOG_ONLY` or `DETERMINISTIC_MATCH_ONLY` (pilot Phases 1–2).
4. Token Usage Tracker `#71` accounts any local compute.
5. **No** fetch of origin tenant evidence. **No** cross-namespace read.

### 7.3 Blocked in pilot (until gates clear)

- `LIGHT_LOCAL_WAKE_ALLOWED` / deep inhale on peers (IFM-D11 high tier + Lung wiring)
- Mesh-triggered Load Multiplier copy spawn without numeric cap (contract §13 Q1)
- Autonomous broadcast without RA sign

---

## 8. Consent and legal (pilot inputs — not finalized)

| Artifact | Pilot requirement | Owner |
|---|---|---|
| Per-tenant mesh opt-in | Mode Controller state + audit log | Operator + MSP |
| MSP pool agreement | Pool boundary + key epoch + billing attribution | Matt §11 + counsel |
| Revocation | IFM-D7 — leave pool without downtime | Tenant boundary |
| PIPEDA / cross-border | Privacy Filter + tenant policy | Existing PF-D6 posture |

Legal consent artifact remains **open** at mesh contract §13 Q2 — pilot Phase 2 blocked until resolved.

---

## 9. Build authorization checklist (future — not implied)

Before any P1 sandbox code:

1. Matt explicit Build Authorization naming mesh bus target.
2. Codex pre-build gate 0/0 on wiring slice.
3. Fixture-based pulse round-trip tests (synthetic tenants only).
4. Authority probe: no AUTH-5 path; no cross-tenant evidence in pulse schema.
5. Completion gate + GATED reconcile — **not** default registry.

---

## 10. Success criteria (pilot evidence — not GTM claims)

| Metric | Evidence type |
|---|---|
| Pulse egress carries zero class-B fields | Automated schema scan on fixtures |
| Replay rejected | Duplicate `pulse_id` test |
| Consent honored | Mode state flip → send/receive stops |
| Local match only | No cross-tenant blackboard read in integration test |
| Trust tier respected | LOW pulse never triggers copy spawn |
| Revocation clean | Tenant leaves pool; no new I/O; audit retained |

---

## 11. Explicit non-authorization

This wiring plan does **not** authorize:

- Mesh bus production code or partner APIs
- Live Todd/CMIT mail integration as mesh pilot gate
- Lung production or Operator Lung Dial promotion
- Federation pricing lock or buyer-facing GTM claims
- GOVERNED_AGENT promotion, default registry, production dispatch, AUTH-5

---

## 12. Next chain step

**c03** — Stage C end: governed production organism loop (MMI-DEC-150 · Matt §11).

Matt Nichol — federation mesh pilot wiring plan filed Stage C c02 (MMI-DEC-142).
