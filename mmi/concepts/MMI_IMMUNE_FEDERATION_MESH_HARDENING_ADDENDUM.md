# MMI CONCEPT ADDENDUM: IMMUNE FEDERATION MESH HARDENING REQUIREMENTS

**Document Reference:** MMI-CON-2026-06-24-A

**Status:** CONCEPT ONLY / NOT AUTHORIZED FOR BUILD

**Parent concept:** `mmi/concepts/MMI_PNEUMATIC_LUNG_IMMUNE_FEDERATION_MESH_CONCEPT.md`

**Filed by:** Matt Nichol (operator hardening session)

**Purpose:** Strengthen Phase B/C federation architecture against privacy leakage, dictionary attacks, replay, poisoning, cost-draining abuse, and misinterpretation as cross-tenant data sharing. **Required reading before any signed mesh contract.**

**Boundary:** Hardening requirements only. Does not authorize implementation.

---

## ADDENDUM: IMMUNE MESH HARDENING REQUIREMENTS

### 5. Mesh Safety Doctrine

The Immune Federation Mesh is not a shared inbox, shared tenant brain, shared evidence store, or shared investigation layer.

It is a **sanitized alert-propagation system**.

The mesh may transmit only non-reversible, non-identifying, bounded defensive indicators that allow other opted-in tenant cells to ask:

> “Do I locally observe a structurally similar threat pattern?”

The mesh may not transmit:

* raw email body text;
* subject lines;
* vendor names;
* customer names;
* mailbox identifiers;
* unredacted domains;
* unredacted URLs;
* payment amounts;
* account numbers;
* routing numbers;
* invoice numbers;
* credential material;
* user identifiers;
* tenant-readable investigation notes;
* analyst comments;
* case timelines;
* evidence packages.

The receiving tenant cell may only use the pulse to run local matching and local hardening inside its own namespace boundary.

No receiving tenant may query, inspect, reconstruct, or request the originating tenant’s evidence.

---

### 6. Hashing Correction: HMAC, Not Plain SHA-256

Plain SHA-256 is not sufficient for all pathogen pulse fields.

Many candidate indicators have low entropy and can be guessed through dictionary attacks. Examples include known domains, public relay IPs, invoice template filenames, common URLs, brand impersonation layouts, vendor portal paths, and recurring attacker infrastructure.

Therefore, all mesh-exported indicators must use **keyed HMAC fingerprints**, not raw hashes.

Required replacement:

```text
SHA-256(value)
```

must become:

```text
HMAC-SHA256(mesh_epoch_key, canonicalized_value)
```

Where:

* `mesh_epoch_key` is rotated on a defined schedule;
* keys are scoped by MSP mesh pool, not globally shared across the full platform;
* keys are never available to tenant-local detection agents;
* raw values are discarded before egress;
* fingerprints expire with the pulse TTL;
* historical keys are retained only as long as needed for audit and replay defense.

This prevents an observer from brute-forcing common values and mapping mesh traffic back to tenants, vendors, domains, or active campaigns.

---

### 7. Source Tenant Privacy Correction

The original `source_tenant_hash = SHA-256(Tenant_ID + System_Salt)` must be replaced.

A system-wide salt creates unacceptable blast radius. If exposed, all historical tenant hashes become correlatable.

Required replacement:

```text
source_tenant_tag = HMAC-SHA256(mesh_epoch_key, tenant_id || pulse_epoch || purpose_scope)
```

Properties:

* stable only inside the minimum required detection window;
* non-linkable across long time horizons;
* scoped to the MSP mesh or explicit federation pool;
* not reversible by receiving tenants;
* not globally useful if one mesh pool is compromised.

The system may preserve attribution internally for billing, abuse review, and operator audit, but that attribution must not ride on the shared mesh bus.

---

### 8. Anti-Poisoning and Abuse Controls

The mesh must assume that attackers may attempt to trigger false pulses, inflate compute costs, poison pattern memory, or cause synchronized overreaction across MSP tenants.

Every outbound Pathogen Signature Pulse must pass the following gates before broadcast:

#### A. Local Evidence Threshold

A pulse may not be emitted from a single weak signal.

Minimum emission requirement:

```text
At least two independent signal families must agree.
```

Valid signal families include:

* cryptographic attachment or URL fingerprint;
* structural DOM or document-layout match;
* behavioral cadence anomaly;
* vendor/payment workflow anomaly;
* sender infrastructure drift;
* verification failure or hold outcome;
* Shadow Sensor campaign clustering.

#### B. ReconciliationAgent Signature

ReconciliationAgent `#84` signs only the sanitized pulse envelope.

It does not sign raw evidence into the mesh.

It does not authorize cross-tenant inspection.

It does not create global tenant visibility.

Its signature means only:

```text
The pulse passed local sanitization, threshold, schema, and egress validation.
```

#### C. Mesh Trust Score

Each pulse receives a bounded trust score:

```text
MESH_TRUST_LOW
MESH_TRUST_MEDIUM
MESH_TRUST_HIGH
```

Receiving tenants may use this score to decide whether to:

* log only;
* run cheap deterministic matching;
* wake local lightweight verification;
* trigger local pre-emptive Lung inhale.

No pulse may force another tenant into deep inflation by itself.

#### D. Compute Abuse Guard

A mesh pulse may recommend local hardening, but it may not directly allocate unbounded compute.

Each receiving tenant must enforce:

* local rate limits;
* local budget caps;
* local Safe-Stop timers;
* local operator-configured mesh mode;
* local Token Usage Tracker `#71` accounting.

The mesh advises. The tenant-local Mode Controller decides.

---

### 9. Replay Protection and Pulse Expiry

Every pulse must include:

```protobuf
string pulse_id = 1;
google.protobuf.Timestamp issued_at = 2;
google.protobuf.Timestamp expires_at = 3;
uint32 schema_version = 4;
uint32 key_epoch = 5;
```

Rules:

* expired pulses are rejected;
* duplicate `pulse_id` values are rejected;
* pulses outside acceptable clock skew are rejected;
* replayed pulses cannot re-trigger Lung inflation;
* old pulse fingerprints are archived only as non-operational audit artifacts.

Default TTL:

```text
LIGHT_BREATH: 6 hours
NORMAL_BREATH: 24 hours
DEEP_BREATH: 72 hours maximum
```

Longer retention requires explicit operator-approved research or evidence preservation outside the live mesh bus.

---

### 10. Consent, Revocation, and Tenant Boundary Controls

Mesh participation must be explicit.

Consent is controlled through Mode Controller `#92`.

Required tenant states:

```text
MESH_DISABLED
MESH_RECEIVE_ONLY
MESH_SEND_AND_RECEIVE
MESH_LOCAL_ONLY_DURING_INCIDENT
```

Revocation rules:

* tenant can leave the mesh without downtime;
* tenant revocation prevents future pulse emission;
* tenant revocation prevents future pulse receipt;
* historical pulses remain audit artifacts only;
* revocation does not delete legally required security audit logs;
* revocation does not allow reconstruction of past raw evidence by other tenants.

MSP-level grouping does not override tenant-level consent.

The MSP can offer the mesh. The tenant boundary still governs participation.

---

### 11. Revised Economic Rule

Replace:

> As the network grows, the cost to defend a single unique campaign drops toward zero.

With:

> As the network grows, the marginal cost of recognizing a previously synthesized campaign drops from deep LLM analysis toward cheap deterministic verification. The first tenant pays the cost of local synthesis and evidence review; subsequent opted-in tenants benefit from bounded pattern matching, local pre-hardening, and reduced redundant analysis without receiving the originating tenant’s data.

This preserves the economic thesis while avoiding an absolute claim.

---

### 12. Revised Pathogen Pulse Schema Notes

The schema must distinguish between three classes of fields:

#### A. Allowed on Mesh Bus

* HMAC fingerprints;
* quantized structural metrics;
* bounded enums;
* non-linkable source tags;
* TTL;
* schema version;
* confidence tier;
* recommended local response tier.

#### B. Allowed Only Inside Origin Tenant

* raw evidence;
* raw email;
* extracted text;
* case timeline;
* vendor/payment context;
* user/account identifiers;
* analyst notes;
* customer-specific scoring rationale.

#### C. Allowed Only in Platform Audit Plane

* real tenant attribution;
* billing/accounting linkages;
* key epoch records;
* pulse signing logs;
* abuse investigation trail.

No field may move from B or C into A.

---

### 13. Recommended Schema Patch

Add these required fields to `PathogenSignaturePulse`:

```protobuf
uint32 schema_version = 8;
google.protobuf.Timestamp expires_at = 9;
uint32 key_epoch = 10;
MeshTrustLevel mesh_trust_level = 11;
MeshResponsePermission response_permission = 12;
string source_tenant_tag = 13;
```

Add enums:

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

Deprecate:

```protobuf
string source_tenant_hash = 4;
```

Replace with:

```protobuf
string source_tenant_tag = 13;
```

The source tag must be generated using rotating HMAC keys and must not be globally stable.

---

### 14. Final Architecture Statement

The Pneumatic Lung gives each tenant elastic defensive capacity.

The Immune Federation Mesh gives opted-in tenants collective warning without collective exposure.

The mesh does not weaken Guardrail 11.

It strengthens it by proving that the system can coordinate defense without centralizing tenant data, exposing inboxes, or creating cross-tenant evidence visibility.

The governing principle is:

```text
Shared threat shape.
Never shared tenant truth.
```

---

## Usage note

Keep **`MMI_PNEUMATIC_LUNG_IMMUNE_FEDERATION_MESH_CONCEPT.md`** as the **vision document**. This file is the **hardening addendum** required before anyone turns federation into a signed contract.

Matt Nichol — 2026-06-24.

---

## Research closeout (MMI-DEC-131)

**Status:** Pre-contract research lane **CLOSED** for pricing, copy caps, legal consent, and protobuf schema inputs.

**Record:** `mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md`

| Open item (pre-a05) | Closeout |
|---|---|
| Pricing / economics | §11 + research memo §5 (token accounting, tiered marginal cost) |
| Copy caps | §8D + research memo §5–6 (numeric cap **TBD at Stage B contract**) |
| Legal consent | §10 retained; counsel/§11 at mesh contract — no new legal doc at a05 |
| Protobuf / schema | §9 + §13 retained as contract draft input |

**Contract draft filed.** Stage B **`b03`** promoted hardening requirements to `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (MMI-DEC-134 · §11 MMI-DEC-140). Pilot wiring plan: `mmi/research/MMI_FEDERATION_MESH_PILOT_WIRING_PLAN_MMI-DEC-142.md`. No mesh bus implementation.

Matt Nichol — research closeout register 2026-06-24; contract draft pointer updated b03 closeout.
