# MMI IFM §13 Resolution — Key Epoch Rotation Schedule (Item #3)

**Classification:** `RESEARCH_INPUT` · `ADVISORY_MEMO` · `DESIGN_RESOLUTION_DRAFT` · `EXPLICITLY_NOT_DOCTRINE` · `ZERO_ROUTING_INFLUENCE` · `NOT_BUILD_AUTHORIZATION`

**Subject:** §13 open item #3 — default key epoch rotation schedule and emergency rotation procedure

**Reference:** `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (§11 MMI-DEC-140) · IFM-D2 · IFM-D4 · IFM-D6 · addendum MMI-CON-2026-06-24-A §6–§9

**Operator acceptance:** Matt Nichol — **90 / 14 / 90 defaults** (2026-06-25)

**Date:** 2026-06-25

**Boundary:** Resolves a §13 design fork only. Does not amend the signed contract on disk unless Matt authorizes a formal contract amendment. Does not authorize mesh bus build, key management service implementation, GOVERNED_AGENT promotion, or AUTH-5. Emergency revoke remains **Matt-only** operator authority — not agent quorum.

---

## 1. Resolution summary

Matt accepts the following defaults for Immune Federation Mesh `mesh_epoch_key` / `key_epoch` handling per MSP federation pool:

| Parameter | Accepted default |
|-----------|------------------|
| Scheduled rotation interval | **90 days** per MSP mesh pool |
| Dual-verify overlap after new epoch live | **14 days** (superseded epoch still verifies in-flight pulses) |
| Retired-key audit retention after overlap | **90 days**, then hard delete subject to counsel hold if any |
| Minimum epoch lifetime | **7 days** (anti-thrash) |
| Clock skew tolerance (pairs with IFM-D6 replay) | **±300 seconds** on `issued_at` |

---

## 2. Definitions

- **`mesh_epoch_key`** — HMAC secret scoped to one MSP mesh pool; audit-plane only; never exposed to tenant-local detection agents (IFM-D2).
- **`key_epoch`** — Monotonic public integer on each pulse; receivers select verification key material by epoch (IFM-D6, §9 schema).
- **Rotation** — Mint new `mesh_epoch_key`, increment `key_epoch`, retain superseded epoch in verify-only mode for overlap window.

Pulse TTL (LIGHT 6h / NORMAL 24h / DEEP 72h max) operates independently of epoch schedule. Epoch rotation is a longer-layer key-management control.

---

## 3. Scheduled rotation procedure (normal)

1. **T−7d:** Platform audit-plane notice — upcoming epoch bump for `pool_id`.
2. **T0:** Publish new `mesh_epoch_key` to pool key service; `key_epoch += 1`. New egress pulses use new epoch only.
3. **T0 → T+14d (overlap):** Receivers accept pulses signed with **current or immediately prior** epoch.
4. **T+14d:** Prior epoch moves to **verify-only** (audit/replay checks); no new operational accept from prior epoch.
5. **T+14d → T+104d:** Retired epoch material retained in audit plane for investigation.
6. **T+104d:** Hard delete retired key material unless legal/counsel hold applies.

---

## 4. Emergency rotation procedure (revoke)

**Authority:** **Matt Nichol only** (operator emergency order). Not agent quorum. Not autonomous Mode Controller hardening.

**Triggers (any one):**

- Suspected `mesh_epoch_key` leak for a pool
- Compromised operator credential with pool key access
- Sustained poison-pulse campaign attributed to active epoch
- Explicit Matt operator order

**Steps:**

1. Matt declares `EMERGENCY_EPOCH_REVOKE` for `pool_id` with reason code (logged append-only).
2. Platform mints new `mesh_epoch_key` immediately; `key_epoch += 1`.
3. Superseded epoch: **24-hour verify-only sunset** — then reject for all new operational accept (shorter than normal 14d overlap).
4. Optional pool tighten (Matt decision): affected pool defaults to `MESH_RECEIVE_ONLY` until Matt clears send path.
5. Audit log records: `pool_id`, `old_epoch`, `new_epoch`, actor, reason, timestamp, affected pulse count estimate if available.
6. Receiving tenants remain under local Mode Controller `#92` consent — no cross-tenant inspection, no forced peer deep inflation.

---

## 5. Compliance cross-check (#105 LAW 1–9)

| Law | Check |
|-----|-------|
| LAW 1–2 | Key service observes authority; does not self-grant mesh egress |
| LAW 7 | PM Voice / operator feed must not imply build authorized by this memo |
| LAW 9 | Drift-defense scope — typed operator acceptance; not cryptographic §11 amendment by itself |

---

## 6. Remaining §13 open items (unchanged)

This memo closes **§13 #3 only**. Still open on IFM contract:

1. Numeric copy cap (anti-abuse)
2. Legal consent artifact
4. MSP pool boundary / billing
5. Pilot scope
6. Protobuf authority repo location

---

## 7. Next steps (not authorization)

| Lane | Suggested work |
|------|----------------|
| **DESIGN** | Optional formal contract amendment incorporating 90/14/90 if Matt wants numbers on the signed surface |
| **AUDIT** | Adversarial checklist: epoch overlap edge cases, emergency revoke, skew rejection, replay with retired epoch |
| **BUILD** | Blocked — no key management service until separate build authorization |

---

**Status:** Operator design resolution filed as advisory input. Holds no execution authority.

> Matt Nichol — accepts 90-day rotation, 14-day overlap, 90-day retired-key retention for IFM §13 #3 (2026-06-25).
