# RoleSeparationController — Amendment: named CIRT role

**Document type:** Contract Amendment (DRAFT — pre-§11, unsigned)
**Status:** DRAFT — UNSIGNED. No build authorization until §11 is signed.
**Date drafted:** June 11 2026
**Drafted by:** Cursor (execution lane), transcribing the operator-settled June 11 2026 session design. Signature reserved for the operator.
**Amends:** `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md` — §3 Component 2 (RoleSeparationController), §11 SIGNED 2026-06-09 (`fe355da`). Implementation surface: `core/operator_state/role_separation.py`.
**Authority:** Matt Nichol — sole signing authority
**Required by:** Phase 4 ReconciliationAgent contract P4-D2 (`d0cc849`).

---

## §A — Purpose

The Phase 4 ReconciliationAgent introduces a **named CIRT individual per tenant** (P4-D2) who holds freeze authority on active incidents and dial authority for that tenant. The signed RoleSeparationController has a closed three-role model — `BUILDER`, `AUDITOR`, `OPERATOR` — with no role for an incident responder. This amendment adds **CIRT** as a new permission level. It is **an amendment to the existing signed surface, not a rebuild** — the three existing roles, their capabilities, and the four separation rules are unchanged.

---

## §B — New role (amends the Role enum)

Add one role to the closed `Role` enum (§3 Component 2):

- **`CIRT`** — Computer Incident Response Team member. A **named individual bound to a single tenant**, set at onboarding. Not a generic or rotating role. The named person is recorded in the contract at onboarding and appears in the audit trail on every action they take.

CIRT is a distinct level: it does **not** inherit BUILDER, AUDITOR, or OPERATOR capabilities, and OPERATOR (Matt Nichol, `matt_nichol`) remains the sole holder of `SIGN_SPEC` / `PUSH` / `OPEN_CLOSE_GATE` / mutation authority. CIRT sits below OPERATOR and is scoped to incident response for its one tenant.

---

## §C — New capabilities (amends the Capability enum)

Add two capabilities, both CIRT-only and tenant-scoped:

- **`FREEZE_INCIDENT`** — freeze authority on an active incident for the CIRT member's bound tenant (halts dispatch / holds the tenant's mail flow pending review).
- **`ADJUST_DIAL`** — Lung dial authority for the CIRT member's bound tenant (the per-tenant breathing/sensitivity setting).

Capability map addition:

```
Role.CIRT: { FREEZE_INCIDENT, ADJUST_DIAL }
```

No existing role gains these capabilities. No existing capability changes owners.

---

## §D — Tenant binding & separation rules

- **Tenant binding is mandatory.** A CIRT actor is authorized only for the `tenant_id` it was bound to at onboarding. A CIRT member for tenant A **cannot** `FREEZE_INCIDENT` or `ADJUST_DIAL` on tenant B. Cross-tenant CIRT action raises `RoleSeparationError`.
- **The four existing separation rules are unchanged.** CIRT does not hold any audit capability and cannot build, so the builder-auditor collapse rules are unaffected.
- **No new auth infrastructure.** Consistent with the signed Component 2 boundary, the CIRT `actor_id` and bound `tenant_id` are opaque caller-supplied labels; this amendment mints/verifies no credential. Onboarding-time identity binding is recorded, not authenticated here.

---

## §E — Audit trail

Every CIRT action (`FREEZE_INCIDENT`, `ADJUST_DIAL`) is recorded in the audit trail with the **named individual** and the **bound tenant_id**. Accountability is real and non-anonymous: the named person is on every decision they make. (This is the MSP sales story — "here is who is responsible for your security decisions, and here is the audit trail proving it.")

---

## §F — Test requirements (three classes)

**Class 1 — Expected pass**
- CIRT role exists; `capabilities_for(Role.CIRT)` returns exactly `{FREEZE_INCIDENT, ADJUST_DIAL}`.
- A CIRT actor bound to tenant A is authorized to `FREEZE_INCIDENT` / `ADJUST_DIAL` on tenant A.
- Each authorized CIRT action emits an audit record carrying the named actor_id and tenant_id.

**Class 2 — Adversarial**
- CIRT actor for tenant A is denied `FREEZE_INCIDENT` / `ADJUST_DIAL` on tenant B (`RoleSeparationError`).
- CIRT is denied any BUILDER/AUDITOR/OPERATOR capability (e.g. `SIGN_SPEC`, `RUN_COMPLETE_GATE`, `WRITE_AGENT_CODE`).
- A non-CIRT role is denied `FREEZE_INCIDENT` / `ADJUST_DIAL`.
- OPERATOR role remains reserved to `matt_nichol`; CIRT cannot assume OPERATOR.

**Class 3 — Known-gap xfail**
- Persistent onboarding-time identity binding — deferred. Reason: no auth infrastructure in Component 2 (signed boundary). Completion path: onboarding/identity contract.

---

## §G — What this amendment does NOT change

- The three existing roles (BUILDER, AUDITOR, OPERATOR) and their capability sets — unchanged.
- The four separation rules — unchanged.
- The "no auth infrastructure" boundary of Component 2 — unchanged.
- No rebuild of `role_separation.py`; this is an additive amendment (one role, two capabilities, one map entry, tenant-binding check).

---

## §11 — Operator Sign-Off

**Status:** DRAFT — UNSIGNED. No build authorization until this block is signed.

**Signed:** ____________________
**Date:** ____________________
