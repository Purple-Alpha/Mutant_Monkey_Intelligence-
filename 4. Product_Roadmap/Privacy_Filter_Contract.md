# Privacy Filter — Agent Design Contract
## Separate Service: Cross-Tenant Broadcast Safety Gate

**Document type:** Agent Design Contract — Service Specification (pre-§11)
**Status:** §15 SIGNED — Matt Nichol June 14th 2026. Build authorization granted per this contract's scope (see §15).
**Date drafted:** June 13, 2026
**Drafted by:** Claude (advisory lane) — per AGENTS.md §2.1
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Blast Radius Controller GATED #89 f1c817e
**Concept doc:** 4. Product_Roadmap/Privacy_Filter_Concept_Doc.md

---

## §0 — Purpose

The Privacy Filter is a separate service that sits between the swarm and any cross-tenant broadcast. It is the boundary control for the one path that is deliberately meant to cross tenants — and it ensures that path never carries raw tenant-identifying information.

The governing property is isolation by construction. Cross-tenant intelligence sharing makes the product stronger. But no raw tenant identifier may ever cross a tenant boundary. The filter is built so that if it is unhealthy, nothing broadcasts — not a filtered version, not a degraded version, nothing.

This component must be specified as a separate service before the Phase 6 DEPTH GATE opens. It may be built in parallel with Mode Controller work. It is a hard pre-condition for the Collective Immune System.

---

## §1 — Scope

### In scope
- Five-stage filter pipeline — entity detection, policy lookup, transformation, validation, audit record
- Per-tenant sharing policy resolution
- No-raw-identifier invariant enforcement
- Independent circuit breaker — own breaker key, never shared
- Append-only audit trail for every filter operation
- PIPEDA compliance as a hard design constraint
- Fail-closed behavior on all failure conditions

### Explicitly out of scope
- The broadcast engine itself — separate component
- Cross-tenant pattern sharing logic — Collective Immune System contract
- Specific database or storage technology — deferred to Lung contract
- Any change to Phase 1-5 signed surfaces
- Any change to Blast Radius Controller signed surfaces

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| PF-D1 | Separate service | Privacy Filter is a completely independent service from the broadcast engine. Not a function call inside the broadcaster. Own lifecycle, own deployment, own circuit breaker. |
| PF-D2 | Fail closed | If Privacy Filter breaker is OPEN, nothing broadcasts. No fallback path. No degraded broadcast mode. No "broadcast raw and filter later." OPEN means silence. |
| PF-D3 | Two independent failure domains | Privacy Filter and broadcast engine fail independently. A broadcast-engine failure does not open the Privacy Filter breaker. A Privacy Filter failure does not open the broadcast-engine breaker. Own breaker key per BRC-D5. Never shared. |
| PF-D4 | Pipeline is mandatory | Every item bound for cross-tenant broadcast passes through all five pipeline stages in order. No stage is skippable. No shortcut path exists. |
| PF-D5 | No raw tenant identifiers | No raw tenant identifiers may cross tenant boundaries. This is an invariant not a tunable. Transformation exists to enforce it. Validation exists to prove it before release. |
| PF-D6 | Per-tenant policy | Each tenant has its own sharing policy. No global "share everything" default exists. Absence or ambiguity of policy resolves conservatively — do not broadcast. |
| PF-D7 | Audit is part of the pipeline | An operation that cannot be audited does not complete. The audit record is pipeline stage 5, not an afterthought. |
| PF-D8 | PIPEDA compliance | Canadian PIPEDA compliance is a hard design constraint not a best practice. Any conflict between "share more signal" and "PIPEDA compliance" resolves in favour of compliance every time. |
| PF-D9 | Blocked operations are logged | Blocked operations — breaker OPEN, validation failure, policy-conservative refusal — are logged with the same rigor as permitted operations. A refusal to broadcast is a governance event. |
| PF-D10 | Consistency with Mode Controller | During RECOVERING the Mode Controller restricts cross-tenant uploads to pattern hashes and anomaly counts only. The Privacy Filter enforces the same class of constraint on the NORMAL-mode broadcast path. Same rule, two enforcement points. |
| PF-D11 | Linux-primary path | All files under the Linux-primary runtime core package `core/privacy_filter/` — repo path `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/privacy_filter/`, the established home for every Layer 6 control-plane component (Blast Radius `core/control_plane/`, Safe-Stop #94 `core/safe_stop/`, Mode Controller #92 `core/mode_controller/`). No Windows paths. |

---

## §3 — The Five-Stage Pipeline

Every item bound for cross-tenant broadcast passes through every stage in order.

### Stage 1 — Entity Detection
**What it does:** Identifies all tenant-identifying entities and sensitive content in the candidate broadcast item.

Detects:
- Raw tenant identifiers — tenant_id, account numbers, names, addresses
- Email addresses and domains that could re-identify a tenant
- IP addresses and infrastructure fingerprints linked to a specific tenant
- Any content that could be used to reverse-engineer which tenant the signal originated from

**Output:** annotated candidate item with detected entities flagged
**On failure:** fail closed — do not proceed to stage 2, log and block

### Stage 2 — Policy Lookup
**What it does:** Resolves the applicable per-tenant sharing policy for the originating tenant.

Resolves:
- What this tenant permits to be shared
- At what granularity — full signal, generalized signal, hash only, blocked entirely
- With what scope — all tenants, cohort, none

**Policy resolution rules:**
- Tenant-specific policy is authoritative
- Absence of policy → fail closed, do not broadcast
- Ambiguous policy → fail closed, do not broadcast
- No global permissive default exists

**Output:** resolved policy for transformation stage
**On failure:** fail closed

### Stage 3 — Transformation
**What it does:** Applies the resolved policy to strip, hash, or generalize the candidate item so the shareable signal survives but tenant-identifying content does not.

Transformations allowed:
- Strip — remove the entity entirely
- Hash — replace with a deterministic one-way hash that preserves correlation without revealing content
- Generalize — replace specific value with a less specific category (country instead of city, domain category instead of domain)

What transformation must never produce:
- Any raw tenant identifier in the output
- Any value that could be reverse-engineered to identify the originating tenant
- Any content outside what the resolved policy permits

**Output:** transformed candidate item
**On failure:** fail closed

### Stage 4 — Validation
**What it does:** Verifies the transformed output actually satisfies the policy and the no-raw-identifier invariant before anything leaves.

Validates:
- No raw tenant identifiers remain in the transformed output
- Transformation matches the resolved policy
- Output schema conforms to the broadcast schema
- No entity detected in stage 1 survived transformation in a raw form

**Validation rule:** if any check fails, fail closed — no broadcast, log the failure with full detail

**Output:** validated broadcast-ready item, or blocked with reason
**On failure:** fail closed

### Stage 5 — Audit Record
**What it does:** Writes an append-only, immutable audit record of the complete operation.

Record must contain:
- input reference — hash of input item, not the item itself
- originating tenant_id
- pipeline entry timestamp
- entity detection findings — what was found
- policy applied — which policy version, what it permitted
- transformation applied — what was stripped, hashed, generalized
- validation outcome — passed or failed with reason
- broadcast decision — broadcast or blocked
- exit timestamp

**Audit record properties:**
- Append-only — no modification after write
- Immutable — no deletion
- Correlated via workflow_id
- Retained per MSP contract requirements
- Exportable for insurer and regulator review

**The audit trail is the evidence that the no-raw-identifier invariant held on every operation.**

---

## §4 — Circuit Breaker Behavior

The Privacy Filter has its own circuit breaker entry in the BreakerStore per BRC-D5.

**Breaker key:** {privacy_filter_service_id}

**When breaker is CLOSED:** pipeline runs normally
**When breaker is OPEN:** nothing broadcasts. The Blast Radius Controller gateway's PrivacyFilterInterface returns "privacy filter unavailable" to the broadcast engine. The broadcast engine does not proceed. No fallback path.
**When breaker is HALF_OPEN:** one trial broadcast is allowed per BRC-D4 transition rules. If trial passes, breaker closes. If trial fails, breaker reopens.

**What opens the breaker:**
- Pipeline stage failure rate exceeds threshold
- Validation failure rate exceeds threshold
- Audit write failure
- Service health check failure
- Latency exceeding timeout threshold

**The breaker is never shared with any tenant, agent, or tool breaker. The independent failure domain guarantee is structural.**

---

## §5 — Per-Tenant Sharing Policy Schema

Each tenant's sharing policy must declare:

```
tenant_id:           str   — tenant this policy governs
policy_version:      str   — version identifier
effective_date:      str   — ISO 8601
sharing_scope:       str   — enum: ALL_TENANTS / COHORT / NONE
allowed_signals:     list  — what signal types may be shared
granularity:         str   — enum: FULL / GENERALIZED / HASH_ONLY / BLOCKED
pipeda_consent:      bool  — tenant has provided PIPEDA-compliant consent
retention_limit:     str   — how long shared signals may be retained by recipients
policy_owner:        str   — MSP operator who set this policy
last_reviewed:       str   — ISO 8601
```

**Policy defaults when field is absent:** fail closed on that dimension

---

## §6 — What May Cross Tenant Boundaries

Only these signal types are eligible for cross-tenant broadcast under any policy:

- Pattern hashes — one-way hashes of attack patterns, no raw content
- Anomaly counts — numeric aggregates, no identifiers
- Generalized indicators — attack category, not specific artifact
- Infrastructure fingerprints — hashed, not raw

Never eligible regardless of policy:
- Raw email content or headers
- Raw tenant identifiers
- IP addresses linked to a specific tenant
- Account numbers, names, addresses
- Any content that could reverse-identify the originating tenant

---

## §7 — PIPEDA Compliance Requirements

PIPEDA compliance is a hard design constraint on every component of this service.

**Consent:** per-tenant sharing policy must encode that the tenant has provided PIPEDA-compliant consent before any cross-tenant sharing occurs.

**Purpose limitation:** signals shared cross-tenant may only be used for fraud defense purposes. No secondary use.

**Data minimization:** only the minimum signal necessary for the defensive purpose crosses the boundary. The transformation stage enforces this.

**Retention limits:** per-tenant policy must declare how long shared signals may be retained by recipient tenants. The audit record documents this.

**Audit rights:** the audit trail in stage 5 must be sufficient to demonstrate PIPEDA compliance on any specific operation if required by a regulator.

**Scope note:** PIPEDA compliance as a design constraint means this service is built to be compliant. It is not a public external compliance claim about the product as a whole. Any external-facing compliance statement remains out of scope for this contract.

---

## §8 — Canadian Legal Alignment

The Privacy Filter produces privacy-safe derived signals not decisions. It does not determine whether an attack occurred. It determines whether a signal is safe to share across tenant boundaries.

Human retains final authority over cross-tenant intelligence sharing policies. The per-tenant policy is set by the MSP operator, not the system.

No guarantee of complete tenant anonymization is implied. The service enforces the no-raw-identifier invariant and the policies as configured. Misconfigured policies produce misconfigured output — the MSP operator owns policy configuration.

Shared responsibility matrix: Mutant Monkey owns pipeline integrity, invariant enforcement, audit trail, and PIPEDA-aligned design. MSP operator owns per-tenant policy configuration, tenant consent management, and response actions taken based on shared intelligence.

Audit log retention commitments are per MSP contract requirements and must be agreed in the MSP service agreement before cross-tenant sharing is enabled for any tenant.

---

## §9 — Failure Mode Controls

| Failure mode | Prevention |
|---|---|
| Raw tenant identifier crosses boundary | Stage 4 validation catches it, fails closed before broadcast |
| Policy absent or ambiguous | Stage 2 resolves conservatively — no broadcast |
| Audit write failure | Pipeline fails closed — no broadcast without audit record |
| Privacy Filter service down | Breaker opens, PrivacyFilterInterface returns unavailable, broadcast engine halts |
| Broadcast engine failure opens Privacy Filter breaker | Two independent failure domains — cross-breaker contamination is structurally impossible |
| Validation bypass attempt | Stage 4 is not skippable — pipeline is mandatory per PF-D4 |
| Policy misconfiguration sharing too much | Transformation applies policy exactly — if policy permits too much, that is an operator configuration issue not a filter failure |

---

## §10 — Test Requirements

Three test classes. ELITE 85+ target.

**Class 1 — Expected pass**
- All five pipeline stages execute in order for a compliant broadcast item
- Raw tenant identifier detected in stage 1 is stripped in stage 3 and absent from stage 4 output
- Absent policy in stage 2 produces fail-closed result — no broadcast
- Audit record writes correctly for both broadcast and blocked operations
- Breaker OPEN produces no broadcast with PrivacyFilterInterface returning unavailable
- PIPEDA consent absent in policy produces fail-closed result
- Pattern hash passes through correctly as eligible signal type

**Class 2 — Adversarial**
- Inject raw tenant identifier into transformation output — stage 4 validation must catch and block
- Attempt to skip stage 4 validation — pipeline must not permit
- Attempt to broadcast without audit record — pipeline must fail closed
- Inject raw email content as candidate broadcast item — entity detection must flag, transformation must block
- Simulate Privacy Filter service failure — breaker opens, broadcast engine halts, no fallback broadcast
- Simulate broadcast engine failure — Privacy Filter breaker must remain unaffected — two independent failure domains confirmed
- Attempt policy lookup with ambiguous policy — must resolve fail-closed
- Inject candidate item that partially passes validation — full item must be blocked, not partial broadcast

**Class 3 — Known-gap xfail**
- Full PIPEDA compliance audit — deferred. Reason: requires legal review of tenant policy templates against PIPEDA regulations. Completion path: legal review before first production tenant onboarded.
- Cross-region privacy filter coordination — deferred. Reason: infrastructure selection pending. Completion path: Lung contract.
- Tenant consent management workflow — deferred. Reason: Playhouse contract. Completion path: Phase 9.

---

## §11 — Relationship To Existing Signed Specs

| Existing signed spec | Relationship |
|---|---|
| Blast Radius Controller Contract BRC-D5 | Privacy Filter lives behind the gateway-side PrivacyFilterInterface. This contract specifies the service behind that interface. Independent-failure-domain property already enforced at gateway — this contract honours it on the service side. |
| Mode Controller Contract MC-D10 | During RECOVERING the Mode Controller restricts cross-tenant uploads to pattern hashes and anomaly counts only. Privacy Filter enforces the same class of constraint on NORMAL-mode broadcast path. Same rule, two enforcement points. |
| Agent Health Score Rubric | Privacy Filter scored on Layer 6 Control Plane rubric track. ELITE 85+ required. |
| Swarm Build Map | Privacy Filter is a pre-condition for DEPTH GATE opening. Must be signed and gated. |

---

## §12 — Scoreboard

| Row | Component | Status | Layer | Priority |
|---|---|---|---|---|
| 93 | Privacy Filter Service | SIGNED_UNBUILT on signing | 6 Governance | DEPTH |

---

## §13 — Pre-Condition Statement

This contract must be signed and gated before the DEPTH GATE opens. The Collective Immune System cannot safely broadcast cross-tenant intelligence until the Privacy Filter is operational. This is a hard pre-condition — not optional.

---

## §14 — Phase Gate Requirement

This contract closes when:
- Privacy Filter service gate-clean at 0/0
- Health score 85+ ELITE on Layer 6 Control Plane rubric track
- Scoreboard row 93 updated to GATED
- Matt signs phase closure
- decision_cycles_log.md entry: type PHASE_CLOSURE, privacy_filter

---

## §15 — Operator Sign-Off

**Status:** §15 SIGNED — Matt Nichol June 14th 2026. Build authorization granted per this contract's scope.

**Signed:** Matt Nichol
**Date:** June 14th 2026
