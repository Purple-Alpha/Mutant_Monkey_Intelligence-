# Private Test-Data Store — Deep Dive

**Status:** §11 SIGNED 2026-06-05 by Matt Nichol. Authored 2026-06-04 by Cursor (Claude Opus 4.8) on Matt Nichol's instruction (milestone C); all seven §10 questions resolved 2026-06-04/05 and promoted to locked decisions D9-D15 (Q3/mesh via Consequence Matrix `_Private_Test_Data_Store_Q3_Mesh_Consequence_Matrix.md` -> Option B / self-hosted WireGuard, full sovereignty). Decisions D1-D15 are locked. No infrastructure stood up; per the locked terms, implementation requires a separate explicit operator start-build instruction.
**Owner:** Matt Nichol
**Purpose:** Spec-first contract for an operator-controlled, self-hosted store for NorthStar test data and generated evidence artifacts, so that sensitive test material never transits third-party AI or consumer-cloud services.

---

## §0 Purpose

NorthStar is local-first (`VISION.md`). Today, test fixtures, generated evidence packages, audit packets, and reaction-timing artifacts live on the WSL2 primary and the Windows mirror. As the volume and sensitivity of this material grows — synthetic phishing `.eml` corpora, fictional-tenant evidence packages, audit packets containing rendered claim surfaces — there is a real risk of it drifting onto consumer-cloud sync (Drive/Dropbox/OneDrive), into ad-profiling surfaces, or through third-party model context windows.

This spec defines a **private, self-hosted, operator-controlled store** for that material. It is a data-sovereignty boundary: the operator owns the keys, the host, and the network path. It is for **test / lab data and generated evidence artifacts**, not a production customer datastore (see §1 out-of-scope and §10 Q7).

It does not replace git. Git remains the source of truth for code and specs. This store holds large, binary, or regenerable artifacts that do not belong in git.

---

## §1 Scope

### In scope
- A self-hosted object store for: synthetic test fixtures (`.eml`, attachments, corpora), generated evidence packages, audit packets, eval-harness inputs/outputs, reaction-timing evidence artifacts.
- The access interface (S3-compatible API) the eval harness and evidence-package generator can read/write against.
- The network reachability model (private mesh only, no public ingress).
- Encryption, key-handling, and backup/durability requirements.
- Bucket / namespace layout and tenant-isolation mirroring for fictional test tenants.

### Out of scope
- Production customer email or production customer evidence packages (v1 is test/lab only; revisit in §10 Q7 if a production datastore is ever needed — that requires its own spec with production controls).
- Live malware or live phishing samples (inherits the Email Security Testing framework synthetic-only boundary).
- Replacing git as the source of truth for code/specs.
- A human file-sharing UI / collaboration surface (this is programmatic artifact storage, not Nextcloud-style sharing).
- Any auto-sync to a third-party cloud or AI service.

---

## §2 Locked Design Decisions (proposed; lock at §11)

- **D1 — Self-hosted and operator-controlled.** The store runs on hardware/OS the operator controls. No consumer cloud, no third-party managed object store, for test data.
- **D2 — S3-compatible object store (MinIO) as the interface.** Rationale: the eval harness and evidence-package generator already think in artifacts/paths; an S3 API is vendor-neutral, scriptable, and gives a clean local→NAS migration path without rewriting callers. Chosen over Nextcloud because the workload is programmatic object storage, not human file-sharing.
- **D3 — Private mesh only; no public ingress.** Reachability via a private overlay network (self-hosted WireGuard per D15, which resolves Q3). No port-forwarding, no public S3 endpoint, no internet-facing console.
- **D4 — Purpose- and tenant-scoped buckets.** Separate buckets/prefixes per artifact class (`test-fixtures`, `evidence-packages`, `audit-packets`, `reaction-timing`). Fictional-tenant isolation mirrors the runtime tenant-isolation invariant: no cross-tenant artifact bleed.
- **D5 — Synthetic / lab data only.** Inherits the Email Security Testing framework boundary: `.example` domains, fake vendors, inert attachments, synthetic `.eml`, lab mailbox. No live malware, no real customer PII.
- **D6 — Encryption at rest and in transit; secrets never in the repo.** Access keys live outside git (env / OS keychain / secrets file gitignored). Inherits the gate redaction discipline — a committed key is a hard fail.
- **D7 — Versioning on; documented restore path.** Object versioning enabled; a written, tested restore procedure. Durability is a first-class requirement, not an afterthought.
- **D8 — No third-party processing by default.** The store does not sync or hand artifacts to any external service on its own. If an artifact must go to an external model (e.g., the Grok gate), that is an explicit, separately-logged operator/agent action; the store itself is inert.
- **D9 — Host target: WSL2 primary now; NAS durable copy when hardware exists (resolves Q1).** v1 runs on the WSL2 primary. A dedicated NAS/Proxmox durable mirror is a documented follow-on, not a v1 blocker, mirroring the existing Linux-primary + Windows-backup pattern. Acceptable because D5 keeps all stored data synthetic/regenerable. (Operator-accepted 2026-06-04.)
- **D10 — Topology: single-node MinIO, ~250GB expandable (resolves Q2).** Single-node is right-sized for one operator + lab-scale corpora and evidence packages; distributed HA is out of scope for v1 and revisitable later. (Operator-accepted 2026-06-04.)
- **D11 — Retention (resolves Q4).** Evidence packages and audit packets are kept indefinitely (small, audit-relevant project evidence). Bulky regenerable test corpora auto-expire at 90 days unless tagged `keep`. (Operator-accepted 2026-06-04.)
- **D12 — Integration surface: local-first + explicit sync (resolves Q5; confirms §4 path 2).** Callers keep writing to local disk; a separate explicit sync step pushes to MinIO. Zero runtime coupling in v1; the store stays optional. A future move to direct S3 writes is its own gated slice. (Operator-accepted 2026-06-04.)
- **D13 — Key management (resolves Q6).** MinIO access keys live in the OS keychain primary, with a gitignored secrets file for headless/scripted access. Never in the repo (inherits D6). (Operator-accepted 2026-06-04.)
- **D14 — Production boundary: strictly test/lab forever for THIS store (resolves Q7).** This store never holds real customer evidence packages. Real customer data requires a separate production-datastore spec with production controls — tracked as the deferred real-customer-data controls decision. (Operator-accepted 2026-06-04.)
- **D15 — Mesh: self-hosted WireGuard (resolves Q3).** Reachability via self-hosted WireGuard — no third-party control plane; operator owns key generation, peer config, and the network path end to end (full sovereignty, consistent with D1 and VISION local-first). Chosen via Consequence Matrix (`_Private_Test_Data_Store_Q3_Mesh_Consequence_Matrix.md`); the operator overrode an initial Tailscale lean in favor of the safest fully-sovereign path and explicitly accepts the steeper setup/learning curve. Watch-item: a hand-rolled config is the likeliest public-exposure failure mode — mitigated by D3 (no public ingress) plus an external reachability check before the store holds artifacts. Headscale (self-hosted control plane) is the documented fallback only if raw WireGuard config-management proves operationally unsustainable. (Operator-decided 2026-06-05.)

---

## §3 Bucket / namespace layout (draft)

```text
s3://nst-test-fixtures/<tenant_or_lab>/<corpus>/...
s3://nst-evidence-packages/<tenant>/<package_id>/...
s3://nst-audit-packets/<tenant>/<package_id>__audit_packet/...
s3://nst-reaction-timing/<test_id>/...
```

Naming mirrors the existing on-disk evidence-package layout so migration is a copy, not a restructure.

---

## §4 Integration surface (draft)

Two candidate paths (resolved in §10 Q5):

1. **Direct S3 writes** — the evidence-package generator and eval harness write artifacts straight to MinIO via an S3 client, with local disk as cache only.
2. **Local-first + sync** — callers keep writing to local disk (today's behavior); a separate, explicit sync step pushes to MinIO. Lower coupling; preserves current code unchanged in v1.

Default recommendation for v1: path 2 (local-first + explicit sync), because it adds zero coupling to the runtime and keeps the store optional. Operator confirms at §11.

---

## §5 Failure Modes

1. **Public exposure.** A misconfigured MinIO console/endpoint reachable from the internet. Mitigation: D3 private-mesh-only; no public ingress; verify with an external reachability check.
2. **Secret leakage.** Access keys committed to git or pasted into an artifact. Mitigation: D6; gitignore; gate redaction sweep.
3. **Scope creep to production data.** The test store quietly starts holding real customer PII without production controls. Mitigation: D5 synthetic-only; §10 Q7 forces an explicit decision + separate spec before any production use.
4. **Second source of truth.** The store drifts from git and becomes an un-audited authority. Mitigation: git stays source of truth for code/specs; the store holds only regenerable/binary artifacts.
5. **Sovereignty theater.** A "private" setup that still routes through a third-party control plane or phones home. Mitigation: §10 Q3 weighs managed mesh (Tailscale) vs self-hosted WireGuard explicitly; document what each trusts.
6. **Durability assumed, never tested.** Versioning on but restore never exercised. Mitigation: D7 requires a tested restore procedure, not just enabled versioning.

---

## §6 Audit / Evidence Requirements

- Standing up the store is an infrastructure change; the setup runbook and its verification (reachability check, restore test) are logged through the project's normal evidence surfaces.
- No NorthStar runtime code changes are required by this spec on its own; if §10 Q5 resolves to direct S3 writes, that runtime change runs the normal `complete_gate.py` audit in its own slice.
- The store must never appear as a path that exfiltrates artifacts to a third party; any external hand-off stays an explicit, logged action (D8).

---

## §10 Open Questions (operator-only)

All seven original questions were resolved by operator on 2026-06-04 and promoted to locked decisions (Q1->D9, Q2->D10, Q3->D15, Q4->D11, Q5->D12, Q6->D13, Q7->D14).

- **Q1 — Host target.** RESOLVED -> D9.
- **Q2 — MinIO topology + capacity.** RESOLVED -> D10.
- **Q3 — Mesh choice (sovereignty tradeoff).** RESOLVED -> D15 (Option B / self-hosted WireGuard, via Consequence Matrix `_Private_Test_Data_Store_Q3_Mesh_Consequence_Matrix.md`).
- **Q4 — Retention / lifecycle.** RESOLVED -> D11.
- **Q5 — Integration surface.** RESOLVED -> D12.
- **Q6 — Key management.** RESOLVED -> D13.
- **Q7 — Production boundary.** RESOLVED -> D14.

No §10 questions remain open. The spec is now §11-signable (operator-authored signature).

---

## §11 Sign-off

_§11 SIGNED 2026-06-05. Decisions D1-D15 are locked. All seven §10 questions resolved (D9-D15). This signature locks the design contract only; per the locked terms, implementation does not begin until a separate explicit operator start-build instruction is issued (no infrastructure is stood up by this signature)._

**Operator signature:** Matt Nichol (zebra-comet) June 5th, 2026
