# Immune Federation Mesh — Platform Contract (Contract Review Draft)

**Draft ID:** `MMI_04_IMMUNE_FEDERATION_MESH_CONTRACT_REVIEW_DRAFT`

**Document Reference:** MMI-CTR-2026-06-24

**Status:** **CONTRACT_DRAFT** — NOT §11 SIGNED · NOT BUILD AUTHORIZED · NOT GOVERNED_AGENT · NOT AUTH-5

**Lane:** Platform architecture contract (Phase B federation mesh bus)

**Owner:** Matt Nichol

**Track:** Immune Federation Mesh — sanitized alert-propagation bus (Phase B/C)

**Authority repo:** `/home/socialarchitect/northstar`

**Promotion:** CONCEPT → **CONTRACT_DRAFT** (Stage B · b03 · MMI-DEC-134)

**Source-of-truth links:**
- `mmi/concepts/MMI_PNEUMATIC_LUNG_IMMUNE_FEDERATION_MESH_CONCEPT.md` (vision — CONCEPT ONLY)
- `mmi/concepts/MMI_IMMUNE_FEDERATION_MESH_HARDENING_ADDENDUM.md` (MMI-CON-2026-06-24-A — hardening requirements incorporated herein)
- `mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md` (research closeout — pricing/copy caps/consent/protobuf inputs)
- `mmi/research/MMI_FEDERATION_SMB_SEAT_ECONOMICS_RESEARCH_MMI-DEC-132.md` (federation pool economics — advisory; not locked MSRP)
- `mmi/research/MMI_BRAIN_IMMUNE_LUNG_PREREQ_AUDIT_MMI-DEC-133.md` (brain/immune GATED stack sufficient for contract; Lung production BLOCKED separately)
- `VISION.md` Guardrail 11 — patterns may cross tenants; customer data never does
- `MILESTONE_ARC.md` B7 — cross-tenant signature sharing protocol (Stage B/C)
- `4. Product_Roadmap/Load_Fission_Contract.md` (#90 Load Multiplier — local inflate; mesh advises only)
- `mmi/concepts/MMI_OPERATOR_LUNG_DIAL_SPEC.md` (Dial 2 scale — mesh-triggered local wake bounded by Mode Controller)

**Implementation:** **BLOCKED** until Matt §11 signature + separate operator Build Authorization. This draft authorizes **contract text review only**.

**Governing principle:**

```text
Shared threat shape.
Never shared tenant truth.
```

---

## Spine boundary (core invariant)

```text
The mesh propagates sanitized campaign-warning pulses.
It never propagates tenant evidence, inboxes, or investigation truth.
ReconciliationAgent #84 signs egress envelopes only — not raw evidence.
Mode Controller #92 governs tenant consent and local response.
Token Usage Tracker #71 accounts local compute — mesh advises; tenant decides.
```

---

## Platform contract block

| Field | Value |
|---|---|
| Component name | Immune Federation Mesh (Pathogen Signature Pulse bus) |
| Canonical layer | Cross-cutting platform bus (Phase B federation; not a single swarm agent row) |
| Authority level | **Mesh Egress Authority (ME-AUTH)** — narrowed to sanitized pulse publish after local gates |
| Stage posture | Phase B contract draft; Phase C scale economics downstream of Stage B end (MMI-DEC-140) |
| Evidence Stage (current) | **Not promoted** — contract draft / review only |
| Role | Propagate bounded, TTL'd, HMAC-fingerprinted defensive indicators across opted-in MSP federation pools so receiving tenant cells may run **local** structural matching — never cross-tenant evidence access |
| Boundary | Sanitized alert-propagation only. No shared inbox, brain, evidence store, or investigation layer |
| Explicit non-authorities | See ME-AUTH and prohibited behaviors below |
| Inputs (per origin cell) | Local threshold-passing signal families; ReconciliationAgent `#84` sanitized envelope; Mode Controller `#92` mesh consent state |
| Outputs (per pulse) | `PathogenSignaturePulse` on federation mesh bus — HMAC fingerprints, enums, TTL, trust tier, response permission |
| Evidence emitted | Pulse envelope + platform audit-plane attribution (billing/abuse) — **not** on mesh bus |

---

## ME-AUTH — Mesh Egress Authority (narrowed)

**ME-AUTH grants only (via ReconciliationAgent `#84` egress sign):**

- Validate pulse against schema version, field-class rules (§12), minimum evidence threshold (IFM-D3), and egress sanitization.
- Sign **sanitized pulse envelope only** — meaning: local sanitization, threshold, schema, and egress validation passed.
- Publish pulse to MSP-scoped federation mesh pool with TTL, key epoch, trust tier, and response permission.
- Retain real tenant attribution in **platform audit plane only** — not on shared mesh bus.

**ME-AUTH explicitly does not grant:**

| Forbidden authority | Rule |
|---|---|
| Raw evidence export | No email body, subject, vendor names, payment fields, credentials, user IDs, case timelines, analyst notes |
| Cross-tenant inspection | Receiving tenants may not query, reconstruct, or request originating tenant evidence |
| Global tenant correlating salt | No system-wide salt; `source_tenant_tag` uses rotating HMAC per MSP pool |
| Plain SHA-256 on low-entropy indicators | HMAC-SHA256 with `mesh_epoch_key` required (IFM-D2) |
| Unbounded peer compute allocation | Pulses advise; Mode Controller `#92` + local budgets decide local response |
| Autonomous mesh broadcast | No pulse without RA egress sign + local threshold + consent mode |
| Lung production authorization | Lung `#90`/`#103` wiring remains BLOCKED per MMI-DEC-133 until separate gates |
| GOVERNED_AGENT promotion | No default registry, production dispatch, or AUTH-5 from this contract |

---

## §0 Purpose

The Immune Federation Mesh is a **sanitized alert-propagation system** for opted-in MSP federation pools. It gives collective campaign warning without collective tenant exposure — preserving Guardrail 11 while enabling bounded defensive coordination across Canadian SMB tenant cells.

This draft promotes the hardened addendum (MMI-CON-2026-06-24-A) from CONCEPT to **CONTRACT_DRAFT** for Matt §11 review. It does **not** authorize mesh bus implementation, MSP pricing lock, partner APIs, or cross-tenant evidence access.

---

## §1 Scope

### In scope

- Mesh safety doctrine and prohibited field classes (IFM-D1).
- HMAC fingerprinting, key epoch rotation, and source tenant tag privacy (IFM-D2, IFM-D4).
- Anti-poisoning gates: minimum evidence threshold, RA egress sign semantics, mesh trust tiers, compute abuse guard (IFM-D3, IFM-D5).
- Replay protection, pulse expiry, clock skew rejection (IFM-D6).
- Tenant consent modes via Mode Controller `#92` (IFM-D7).
- Revised economic rule (IFM-D8) — marginal cost toward deterministic verification, not zero.
- Pathogen Signature Pulse schema patch (IFM-D9) — contract draft input for protobuf.
- Relationship to GATED brain/immune stack and downstream Lung prerequisites.

### Out of scope

- Mesh bus runtime implementation, federation pricing engine, partner APIs.
- Lung production wiring (`#90`/`#103`) — blocked per MMI-DEC-133.
- Locked MSRP, GTM claims, Todd pilot authorization.
- Legal consent artifact (counsel review at Matt §11 / contract sign — concept retained from addendum §10).
- Numeric mesh-triggered copy ceiling (TBD at §11 — research memo §5–6).
- GOVERNED_AGENT promotion, default registry, production dispatch, AUTH-5.

---

## §2 Locked Design Decisions (confirm at §11 signing)

| # | Decision | Locked value |
|---|---|---|
| IFM-D1 | Mesh is not shared truth | The mesh is a sanitized alert-propagation system — not a shared inbox, tenant brain, evidence store, or investigation layer |
| IFM-D2 | HMAC, not plain SHA-256 | All mesh-exported indicators use `HMAC-SHA256(mesh_epoch_key, canonicalized_value)`; keys rotated on schedule; scoped per MSP mesh pool; never available to tenant-local detection agents; raw values discarded before egress |
| IFM-D3 | Minimum evidence threshold | ≥2 independent signal families must agree before pulse emission (cryptographic attachment/URL fingerprint; structural DOM/layout; behavioral cadence; vendor/payment workflow; sender infrastructure drift; verification failure; Shadow Sensor campaign clustering) |
| IFM-D4 | Source tenant privacy | `source_tenant_tag = HMAC-SHA256(mesh_epoch_key, tenant_id \|\| pulse_epoch \|\| purpose_scope)` — stable only inside minimum detection window; non-linkable across long horizons; not on mesh bus as reversible ID |
| IFM-D5 | RA egress sign semantics | ReconciliationAgent `#84` signs sanitized pulse envelope only — not raw evidence; signature means local sanitization + threshold + schema + egress validation passed — **not** cross-tenant inspection authorization |
| IFM-D6 | Replay and TTL | Every pulse carries `pulse_id`, `issued_at`, `expires_at`, `schema_version`, `key_epoch`; reject expired, duplicate, and skewed pulses; default TTL: LIGHT_BREATH 6h, NORMAL_BREATH 24h, DEEP_BREATH 72h max |
| IFM-D7 | Explicit consent | Mode Controller `#92` governs `MESH_DISABLED`, `MESH_RECEIVE_ONLY`, `MESH_SEND_AND_RECEIVE`, `MESH_LOCAL_ONLY_DURING_INCIDENT`; tenant revocation without downtime; MSP grouping does not override tenant consent |
| IFM-D8 | Revised economics | Marginal cost of recognizing a previously synthesized campaign drops from deep LLM analysis toward cheap deterministic verification; first tenant pays synthesis; opted-in peers get bounded matching — never originating tenant data |
| IFM-D9 | Schema field classes | **A (mesh bus):** HMAC fingerprints, quantized metrics, enums, non-linkable tags, TTL, trust tier, response permission. **B (origin tenant only):** raw evidence, email, case timeline, vendor context, user IDs. **C (audit plane only):** real attribution, billing, key epochs, abuse trail. No B/C field may enter A |
| IFM-D10 | Mesh advises; tenant decides | Receiving tenants enforce local rate limits, budget caps, Safe-Stop `#94`, Mode Controller mesh mode, Token Usage Tracker `#71` accounting; no pulse forces peer deep inflation by itself |
| IFM-D11 | Trust tier local response | `MESH_TRUST_LOW` → log only; `MESH_TRUST_MEDIUM` → cheap deterministic matching; `MESH_TRUST_HIGH` → local lightweight verification or pre-emptive Lung inhale **only** per local Mode Controller confirmation |
| IFM-D12 | Guardrail 11 preserved | Mesh strengthens Guardrail 11 by proving coordinated defense without centralizing tenant data |

---

## §3 Mesh Safety Doctrine

The mesh may transmit only non-reversible, non-identifying, bounded defensive indicators so receiving opted-in tenant cells may ask:

> “Do I locally observe a structurally similar threat pattern?”

**Prohibited on mesh bus (non-exhaustive):** raw email body; subject lines; vendor/customer names; mailbox identifiers; unredacted domains/URLs; payment amounts; account/routing/invoice numbers; credential material; user identifiers; investigation notes; analyst comments; case timelines; evidence packages.

Receiving tenant cells use pulses for **local matching and local hardening** inside their namespace boundary only.

---

## §4 HMAC and Key Management

### Indicator fingerprints

Replace plain `SHA-256(value)` with:

```text
HMAC-SHA256(mesh_epoch_key, canonicalized_value)
```

### Source tenant tag

Replace deprecated `source_tenant_hash = SHA-256(Tenant_ID + System_Salt)` with:

```text
source_tenant_tag = HMAC-SHA256(mesh_epoch_key, tenant_id || pulse_epoch || purpose_scope)
```

### Key rules

- `mesh_epoch_key` rotated on defined schedule per MSP mesh pool.
- Keys never exposed to tenant-local detection agents.
- Raw indicator values discarded before egress.
- Fingerprints expire with pulse TTL.
- Historical keys retained only for audit and replay defense.

---

## §5 Anti-Poisoning and Abuse Controls

Every outbound pulse passes, in order:

1. **Local evidence threshold** — IFM-D3 (≥2 signal families).
2. **Sanitization + schema validation** — field-class enforcement IFM-D9.
3. **ReconciliationAgent `#84` egress sign** — sanitized envelope only IFM-D5.
4. **Mesh trust score assignment** — IFM-D11.
5. **Compute abuse guard** — IFM-D10; numeric copy cap **TBD at §11** (research input: per-tenant mesh-triggered copy ceiling).

Attackers may attempt false pulses, cost draining, pattern poisoning, or synchronized overreaction — design assumes adversarial mesh participation within opted-in pools.

---

## §6 Replay Protection and Pulse Expiry

Required pulse metadata:

```protobuf
string pulse_id = 1;
google.protobuf.Timestamp issued_at = 2;
google.protobuf.Timestamp expires_at = 3;
uint32 schema_version = 4;
uint32 key_epoch = 5;
```

Rules: reject expired; reject duplicate `pulse_id`; reject unacceptable clock skew; replayed pulses cannot re-trigger Lung inflation; archived pulses are non-operational audit artifacts only.

---

## §7 Consent, Revocation, and Tenant Boundaries

Mesh participation is explicit via Mode Controller `#92`.

| State | Behavior |
|---|---|
| `MESH_DISABLED` | No send; no receive |
| `MESH_RECEIVE_ONLY` | Inbound pulses only; no egress |
| `MESH_SEND_AND_RECEIVE` | Full opted-in participation |
| `MESH_LOCAL_ONLY_DURING_INCIDENT` | Suspend mesh I/O during local incident handling |

Revocation: tenant may leave without downtime; blocks future send/receive; historical pulses remain audit artifacts only; no reconstruction of past raw evidence by peers.

---

## §8 Economic Rule (contract framing — not locked pricing)

> As the network grows, the marginal cost of recognizing a previously synthesized campaign drops from deep LLM analysis toward cheap deterministic verification. The first tenant pays local synthesis and evidence review; subsequent opted-in tenants benefit from bounded pattern matching, local pre-hardening, and reduced redundant analysis **without receiving the originating tenant's data**.

Federation pool seat economics remain advisory per MMI-DEC-132. Mesh tier pricing is a separate commercial fork at Stage B end (b05 · MMI-DEC-140 · Matt §11).

---

## §9 Pathogen Signature Pulse Schema (contract draft input)

Add to `PathogenSignaturePulse`:

```protobuf
uint32 schema_version = 8;
google.protobuf.Timestamp expires_at = 9;
uint32 key_epoch = 10;
MeshTrustLevel mesh_trust_level = 11;
MeshResponsePermission response_permission = 12;
string source_tenant_tag = 13;
```

Enums:

```protobuf
enum MeshTrustLevel {
  MESH_TRUST_UNSPECIFIED = 0;
  MESH_TRUST_LOW = 1;
  MESH_TRUST_MEDIUM = 2;
  MESH_TRUST_HIGH = 3;
}

enum MeshResponsePermission {
  RESPONSE_UNSPECIFIED = 0;
  LOG_ONLY = 1;
  DETERMINISTIC_MATCH_ONLY = 2;
  LIGHT_LOCAL_WAKE_ALLOWED = 3;
  DEEP_LOCAL_INHALE_REQUIRES_LOCAL_CONFIRMATION = 4;
}
```

**Deprecate:** `string source_tenant_hash = 4;` → replace with `source_tenant_tag`.

Protobuf implementation is downstream of §11 + Build Authorization.

---

## §10 Relationship to signed / GATED surfaces

| Surface | Relationship |
|---|---|
| ReconciliationAgent `#84` (GATED) | Sole mesh egress signatory for sanitized envelopes; does not sign raw evidence |
| Mode Controller `#92` (GATED) | Tenant mesh consent modes; local response tier selection |
| Safe-Stop `#94` (GATED) | Local compute ceiling on mesh-triggered wake |
| Blast Radius Controller `#89` (GATED) | Child spawn namespace boundaries if local inhale triggered |
| CIS `#95` (GATED) | Immune teardown coordination |
| Token Usage Tracker `#71` | Local surge compute attribution — prevents free-riding |
| Load Multiplier `#90`/`#103` (GATED; Lung BLOCKED) | Local inflate only; mesh may recommend wake; Mode Controller decides |
| Shadow Watcher Layer 1 | Signal family input for threshold; observe-only |
| Guardrail 11 / `VISION.md` | Binding — mesh must not weaken tenant data isolation |

No signed surface is modified by this contract draft.

---

## §11 Sign-off — **AWAITING MATT §11**

**Not signed.** Matt §11 required before:

- Build Authorization for mesh bus implementation
- Legal consent artifact finalization (counsel review)
- Numeric mesh-triggered copy cap lock
- Federation pool pilot wiring (Stage C · c02)

### Sign-off line (placeholder)

> _Awaiting Matt Nichol §11 signature_

---

## §12 Build path — BLOCKED

Blocked until:

1. Matt §11 signature on this contract.
2. Separate operator Build Authorization (explicit named target).
3. Lung production prerequisites satisfied per MMI-DEC-133 (tenant calibration, Playhouse UI, signed Load Multiplier contract, `#90`/`#103` wiring) — **for mesh-triggered deep inhale paths only**; log-only and deterministic-match tiers may wire earlier per Stage C plan.

Not authorized by this draft: mesh bus code, federation pricing engine, GOVERNED_AGENT promotion, default registry, production dispatch, AUTH-5.

---

## §13 Open questions (draft — resolve at §11)

1. **Numeric copy cap** — per-tenant max concurrent mesh-triggered inflated copies by trust tier (research TBD).
2. **Legal consent artifact** — MSP pool agreement vs per-tenant addendum; counsel review scope.
3. **Key epoch rotation schedule** — default interval and emergency rotation procedure.
4. **MSP pool boundary** — single regional pool vs federated pool-of-pools; billing attribution model at b05.
5. **Pilot scope** — Stage C c02 opt-in MSP pool wiring plan vs Todd intake historical motion.
6. **Protobuf authority** — whether schema lives in authority repo or sibling runtime repo at build time.

---

## §14 Final architecture statement

The Pneumatic Lung gives each tenant elastic defensive capacity.

The Immune Federation Mesh gives opted-in tenants collective warning without collective exposure.

The mesh does not weaken Guardrail 11. It strengthens it by proving that the system can coordinate defense without centralizing tenant data, exposing inboxes, or creating cross-tenant evidence visibility.

Matt Nichol — contract draft filed Stage B b03 (MMI-DEC-134).
