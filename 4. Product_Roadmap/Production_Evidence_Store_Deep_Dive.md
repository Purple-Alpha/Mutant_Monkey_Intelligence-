# Production Evidence Store — Deep Dive

**Status:** DRAFT (pre-§11). Authored 2026-06-05 by Cursor on Matt Nichol's instruction, rolling forward from the §11-signed `Real_Customer_Data_Controls_Deep_Dive.md` (D12). No infrastructure is stood up by this draft. §11 signature is blank by design.

**Owner:** Matt Nichol

**Purpose:** Spec-first contract for an operator-controlled production datastore for real (non-synthetic) Cyber Insurance Evidence Package artifacts — separate forever from the Private Test-Data Store and from synthetic/test locations.

---

## §0 Purpose

The §11-signed Real-Customer-Data Controls spec (D4, D12) requires a separate production datastore before any real customer package is generated, stored, audited, rendered, or delivered. The Private Test-Data Store is §11-signed and locked to test/lab forever (its D14). Real customer artifacts must never land there.

This spec defines that production store: operator-controlled, tenant-isolated, encrypted, auditable, and free of consumer-cloud sync or third-party processing by default. It is a production data-sovereignty boundary, not a feature build authorization by itself.

---

## §1 Scope

### In scope
- Storage for real (non-synthetic) Cyber Insurance Evidence Package artifacts: source evidence inputs, generated package bundles, audit packets, local-AI audit outputs, operator signature records, rendered PDFs (internal only until buyer delivery is separately authorized).
- Production controls: tenant isolation, encryption/key handling, backup/restore, retention, deletion, access control, audit trail, no-cloud-sync boundaries.
- Network reachability model consistent with the signed controls contract (private operator-controlled path; no public ingress).
- Relationship boundary to the Private Test-Data Store (strict separation; no widening).

### Out of scope
- Synthetic/test artifacts (Private Test-Data Store only).
- Standing up infrastructure in this draft.
- Authorizing real-customer-data handling by itself (the signed controls contract plus this spec's eventual §11 sign-off are prerequisites; a separate explicit operator start-build instruction is still required before infrastructure).
- Buyer PDF delivery authorization (separate gate per Real-Customer-Data Controls D8/D15).
- §13/IQ3 revision or local-AI substrate build (separate gated slices per D7/D9/D11).
- Any new external/compliance/insurance claim.

---

## §2 Locked Design Decisions (proposed; lock at §11)

- **D1 — Separate forever from the test store.** Real customer artifacts never use the Private Test-Data Store buckets, paths, credentials, or sync jobs. The two stores may share operator hardware or mesh later, but they remain logically and operationally separate stores with separate credentials and bucket namespaces.
- **D2 — Operator-controlled and self-hosted.** The production store runs on hardware/OS the operator controls. No consumer cloud, no third-party managed object store, for real customer artifacts.
- **D3 — S3-compatible object store interface (MinIO-class).** Same interface family as the test store for migration and scriptability, but isolated deployment/credentials/namespaces. Chosen for vendor-neutral programmatic storage, not human file-sharing.
- **D4 — Private mesh only; no public ingress.** Reachability via the operator's private overlay (self-hosted WireGuard, consistent with the signed test-store D15 posture). No port-forwarding, no public endpoint, no internet-facing console.
- **D5 — Tenant isolation is sacred.** Buckets/prefixes are tenant-scoped. No cross-tenant reads, writes, listings, restores, or deletion operations. Mirrors Guardrail 11 and the controls contract D5.
- **D6 — Encryption at rest and in transit; secrets never in repo.** Production keys live outside git (OS keychain / gitignored secrets file). A committed production key is a hard fail.
- **D7 — Versioning on; tested restore path required.** Object versioning enabled; restore procedure is written and exercised before the store is declared operational for real artifacts.
- **D8 — No third-party processing by default.** The store does not sync or hand artifacts to external models/services on its own. External hand-off (if ever allowed) is explicit, logged, and governed by the signed controls contract (real path = no external egress).
- **D9 — Access control: operator-only in v1.** Only the operator (Matt) has read/write/delete access in v1. MSP-scoped or delegated access is deferred to a later spec revision with its own gate.
- **D10 — Audit trail for every mutating action.** Put, delete, restore, credential rotation, and cross-tenant-denied attempts produce durable audit events with actor, tenant, object key, timestamp, and action.
- **D11 — Retention and deletion are explicit policies, not defaults.** Real artifacts follow a named retention class per artifact type; deletion requires an explicit operator action or a pre-declared retention rule — no silent auto-delete of unaudited production evidence.
- **D12 — No cloud-sync folders for production artifacts.** Real artifacts are never stored under OneDrive/Dropbox/Google Drive/iCloud sync paths. Local working copies on the locked machine must obey the same rule during audit/render operations (controls D10).
- **D13 — Local-first + explicit sync in v1.** Callers keep writing to local disk first; a separate explicit sync step pushes to the production store. Zero runtime auto-coupling until a later gated slice authorizes direct writes.
- **D14 — Buyer-rendered PDFs stay internal until separately authorized.** The store may hold rendered PDFs for operator review, but buyer delivery remains gated by the signed controls contract D8/D15.

---

## §3 Bucket / namespace layout (draft)

```text
s3://mms-prod-evidence/<tenant_id>/packages/<package_id>/...
s3://mms-prod-audit-packets/<tenant_id>/<package_id>__audit_packet/...
s3://mms-prod-audit-outputs/<tenant_id>/<package_id>/local_audit/...
s3://mms-prod-signatures/<tenant_id>/<package_id>/operator_signature/...
s3://mms-prod-rendered/<tenant_id>/<package_id>/rendered/...
```

Prefix `mms-` distinguishes production namespaces from the test store's `nst-` prefixes. No shared bucket between test and production.

---

## §5 Failure Modes

1. **Test/production bleed.** Real artifacts land in the test store or synthetic paths. Mitigation: D1 hard separation; separate credentials and namespaces; classification gate before write.
2. **Public exposure.** Misconfigured endpoint reachable from the internet. Mitigation: D4 private-mesh-only; external reachability check before first real artifact.
3. **Tenant bleed.** Cross-tenant access via mis-keyed prefix or shared credentials. Mitigation: D5 tenant-scoped buckets; per-tenant credential option evaluated in §10 Q2.
4. **Secret leakage.** Production keys committed or echoed in artifacts. Mitigation: D6; gate redaction; separate key rotation runbook.
5. **Silent deletion.** Evidence destroyed without audit trail. Mitigation: D10 audit trail; D11 explicit retention/deletion policy.
6. **Cloud-sync exfiltration.** Sync folder mirrors real artifacts to consumer cloud. Mitigation: D12 no-cloud-sync rule; locked-machine checklist from controls D10.
7. **Buyer delivery by side effect.** A stored rendered PDF is treated as authorized for delivery. Mitigation: D14; controls D8/D15 remain the delivery gate.

---

## §6 Audit / Evidence Requirements

- Standing up the production store is infrastructure; setup runbook + reachability check + restore test are logged through normal evidence surfaces.
- No runtime code changes are required by this draft alone; direct S3 writes (if ever adopted) are a separate gated slice.
- The store must never become an implicit external-egress path; real-path no-egress from the signed controls contract applies.

---

## §10 Open Questions (operator-only)

- **Q1 — Host topology.** Same physical host as the test store with isolated MinIO instance/credentials, or a dedicated production host from day one?
- **Q2 — Credential model.** Single operator credential for all tenants in v1, or per-tenant credentials from day one?
- **Q3 — Retention classes.** Exact retention/deletion schedule per artifact class (source inputs, package bundle, audit packet, local audit output, operator signature record, rendered PDF).
- **Q4 — Off-site durability.** Whether production backups mirror only to operator-controlled off-site media (never consumer cloud) and on what cadence.
- **Q5 — Locked-machine coupling.** Whether production artifact access during local-AI audit is read-only from the locked machine with a fixed egress-deny checklist, or a dedicated air-gapped copy workflow.

---

## §11 Sign-off

_§11 signature blank by design. This draft iterates freely (pre-§11). Infrastructure does not begin until every §10 question is resolved, the spec is §11-signed by Matt, and a separate explicit operator start-build instruction is issued._

**Operator signature:** _(blank — operator-authored at §11)_
