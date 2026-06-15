# Mutant Monkey Inbox Shield — Privacy Filter Adversarial Test Suite Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gemini adversarial red-team — 150 attack vectors + compressed summary, June 14 2026
**Amends:** Privacy Filter #93 — adds adversarial gate requirement
**Component under test:** Privacy Filter #93 (GATED 95 ELITE, hash 85b455f)

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Purpose

This contract defines the adversarial test suite for the Privacy Filter. It converts 150 red-team attack vectors into organized test families. Each family targets a specific trust assumption the Privacy Filter makes. A passing adversarial suite means every trust assumption has been attacked and held. A failing test means a real vulnerability exists.

The adversarial suite gates with the component. The Privacy Filter is not adversarially hardened until all families pass 0/0.

---

## Governing Rule

Every test in this suite must be able to fail. A test that cannot produce a failure is not a test — it is a rubber stamp. If any test family cannot be made to fail against a deliberately weakened version of the Privacy Filter, the test is invalid and must be rewritten.

---

## Test Family 1 — Trust Boundary Injection

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-1-01 | Inject spoofed `tenant_id` — false, stale, or alias value | Broadcast blocked; violation logged |
| PF-ADV-1-02 | Inject tenant data into a trial tenant with undefined boundaries | Broadcast blocked; boundary ambiguity logged |
| PF-ADV-1-03 | Exploit recently merged tenant — data from Tenant A submitted under merged Tenant B identity | Broadcast blocked |
| PF-ADV-1-04 | Exploit deleted tenant — data submitted under a tenant ID that no longer exists | Broadcast blocked; unknown tenant logged |
| PF-ADV-1-05 | Replay `sanitized=true` flag without passing filter path | Broadcast blocked; flag replay detected |
| PF-ADV-1-06 | Replay `privacy_checked=true` in header without actual filter validation | Broadcast blocked |
| PF-ADV-1-07 | MSP parent submits one client's evidence as cross-client broadcast under parent umbrella | Broadcast blocked; MSP boundary violation logged |
| PF-ADV-1-08 | Reviewer with Tenant A access approves broadcast containing Tenant B data | Broadcast blocked; cross-tenant reviewer violation logged |

---

## Test Family 2 — Encoding and Normalization Evasion

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-2-01 | Submit tenant identifier in Unicode homoglyphs | Broadcast blocked |
| PF-ADV-2-02 | Submit tenant identifier in punycode | Broadcast blocked |
| PF-ADV-2-03 | Submit tenant identifier in base64-encoded nested JSON string | Broadcast blocked |
| PF-ADV-2-04 | Submit tenant identifier in URL-encoded form | Broadcast blocked |
| PF-ADV-2-05 | Submit tenant identifier in HTML entities | Broadcast blocked |
| PF-ADV-2-06 | Submit raw tenant data in `summary`, `reason`, `category`, `feature_name`, `debug`, or `explanation` fields | Broadcast blocked |
| PF-ADV-2-07 | Submit tenant identifier as map key instead of map value | Broadcast blocked |
| PF-ADV-2-08 | Submit tenant identifier in unknown/extension fields not in core schema | Broadcast blocked |
| PF-ADV-2-09 | Submit tenant identifier using non-English text, transliteration, or code words | Broadcast blocked |
| PF-ADV-2-10 | Submit vendor identity via routing number hash, invoice format, or bank fingerprint without name | Broadcast blocked |
| PF-ADV-2-11 | Submit tenant identifier via allowlisted feature name: `vendor_acme_com_changed_bank_pdf_x9` | Broadcast blocked |
| PF-ADV-2-12 | Submit tenant identifier via numeric metrics: routing number, account suffix, exact timestamp, geo-coordinate | Broadcast blocked |
| PF-ADV-2-13 | Submit redacted identifier with local-part fragment, domain suffix, or initials remaining | Broadcast blocked |
| PF-ADV-2-14 | Submit zero-width characters, whitespace-only strings, or null bytes to trigger parser inconsistency | Broadcast blocked or error-logged; never silently passed |

---

## Test Family 3 — Payload Structure and Serialization Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-3-01 | Mutate shared object reference after validation, before broadcast serialization | Broadcast blocked; mutation detected |
| PF-ADV-3-02 | Validate shallow copy while nested payload, attachment blob, or evidence list remains unsanitized | Broadcast blocked |
| PF-ADV-3-03 | Embed tenant data inside allowlisted event types: `pattern_update`, `threat_signal`, `aggregate_stat`, `model_feedback` | Broadcast blocked |
| PF-ADV-3-04 | Place tenant data in JSON comments, escaped strings, protobuf unknown fields, or multipart sections | Broadcast blocked |
| PF-ADV-3-05 | Trigger default serializer to dump private object properties, debug attributes, or exception messages | Broadcast blocked; serializer output inspected |
| PF-ADV-3-06 | Validate under old policy version while broadcasting under current authority claims | Broadcast blocked; version mismatch detected |
| PF-ADV-3-07 | Mark parent object safe; expect child objects to inherit safe status without inspection | Broadcast blocked; child objects inspected independently |
| PF-ADV-3-08 | Place tenant data in attachment or linked file while main payload passes | Broadcast blocked; attachments inspected |
| PF-ADV-3-09 | Wrap forbidden content in compressed, encrypted, or signed blob filter cannot inspect | Broadcast blocked; opaque blobs rejected |
| PF-ADV-3-10 | Introduce new schema field after filter deployment that broadcaster emits but filter does not inspect | New field triggers validation failure; unknown fields not auto-passed |
| PF-ADV-3-11 | Split tenant evidence across many small safe-looking fragments that reconstruct downstream | Each fragment blocked; fragmented pattern detected |

---

## Test Family 4 — Async, Race, and Pipeline Ordering Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-4-01 | Insert tenant-specific data after filter runs but before broadcast serialization | Broadcast blocked; post-filter injection detected |
| PF-ADV-4-02 | Enqueue broadcast before validation completes; rely on delayed denial | Broadcast blocked; pre-validation enqueue rejected |
| PF-ADV-4-03 | Cause denial to arrive after broadcast dispatch due to async event ordering | Broadcast blocked; ordering enforced synchronously |
| PF-ADV-4-04 | Submit two broadcasts where safe payload validates while unsafe payload with same ID overwrites before send | Broadcast blocked; ID collision detected |
| PF-ADV-4-05 | Exploit lag between validation store, broadcast queue, audit log, and breaker decision store | All stores consistent before broadcast permitted |
| PF-ADV-4-06 | Switch payload policy labels between validation and broadcast | Broadcast blocked; label change detected |
| PF-ADV-4-07 | Send near-duplicate events that evade deduplication and raise confidence enough for broadcast | Broadcast blocked; near-duplicate pattern detected |

---

## Test Family 5 — Breaker Fail-Closed Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-5-01 | Cause breaker timeout — verify pipeline does not continue as fail-open | Broadcast blocked; timeout treated as deny |
| PF-ADV-5-02 | Cause breaker dependency failure — verify pipeline fails closed | Broadcast blocked |
| PF-ADV-5-03 | Share config, cache, service account, or code path between pipeline and breaker — trigger simultaneous failure | Both failing simultaneously still blocks broadcast |
| PF-ADV-5-04 | Race broadcast during breaker restart, config reload, or stale-cache window | Broadcast blocked during all transition states |
| PF-ADV-5-05 | Replay old `breaker_pass` decision for new payload with different contents | Broadcast blocked; token not reusable across payloads |
| PF-ADV-5-06 | Return malformed breaker response that parses as pass due to truthy string, enum coercion, or default boolean | Broadcast blocked; malformed response treated as deny |
| PF-ADV-5-07 | Require both pipeline AND breaker deny instead of either one deny to block | Either deny alone blocks broadcast |
| PF-ADV-5-08 | Force validator into `warning`, `degraded`, `audit_only`, `shadow`, or `monitor` state; verify broadcaster still sends | Broadcast blocked in all degraded filter states |
| PF-ADV-5-09 | Spoof breaker heartbeat/health signals while breaker is bypassed or unreachable | Broadcast blocked; spoofed health signals do not satisfy breaker requirement |
| PF-ADV-5-10 | Find any code path that treats breaker timeout, unreachable, malformed response, or invalid signature as unknown-but-proceed | No such path exists; all must treat unknown as deny |

---

## Test Family 6 — Aggregate and Statistical Re-identification Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-6-01 | Broadcast small-cohort aggregate where one tenant dominates the sample | Broadcast blocked; cohort size enforcement triggered |
| PF-ADV-6-02 | Flood synthetic events to push tenant pattern past minimum-count gates | Broadcast blocked; synthetic flood detected |
| PF-ADV-6-03 | Execute differential privacy differencing across sequential broadcasts | Sequential broadcasts produce insufficient delta for inference |
| PF-ADV-6-04 | Create sparse histogram buckets where outlier values identify single tenant | Broadcast blocked; sparse bucket detection triggered |
| PF-ADV-6-05 | Broadcast deterministic hashes of tenant/vendor/user identifiers | Broadcast blocked; deterministic identifier hashes not permitted |
| PF-ADV-6-06 | Broadcast embeddings derived from tenant mailbox content | Broadcast blocked; embeddings inspected for membership leakage |
| PF-ADV-6-07 | Place tenant-specific embeddings in shared vector index without namespace partition | Broadcast blocked; shared index isolation enforced |
| PF-ADV-6-08 | Force tenant-specific vendor behavior into shared global baseline | Broadcast blocked; baseline promotion inspected for tenant specificity |

---

## Test Family 7 — Output Spoofing and Silence Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-7-01 | Suppress filter logs, breaker logs, metrics, or alerts | Absence of validation record treated as deny, not pass |
| PF-ADV-7-02 | Flood privacy alerts until real denial alerts are rate-limited or dropped | Critical denial alerts are never rate-limited |
| PF-ADV-7-03 | Forge downstream broadcast-accepted acknowledgement without actual filter decision | Forged acknowledgement does not authorize broadcast |
| PF-ADV-7-04 | Write fake audit entries claiming validation occurred | Fake entries detected via chain validation |
| PF-ADV-7-05 | Delete audit entries showing denial | Deletion detected via broken chain |
| PF-ADV-7-06 | Target audit log compaction, retention expiry, or trace sampling to remove denial records | Denial records exempt from compaction and sampling |
| PF-ADV-7-07 | Reuse valid validation token across payloads, tenants, event types, or time windows | Token bound to exact canonical payload — reuse rejected |
| PF-ADV-7-08 | Validate one canonical form while broadcasting semantically different serialized form | Canonical form verified at broadcast point |
| PF-ADV-7-09 | Spoof filter output artifact, signature, log entry, metric, or audit receipt | Spoofed artifact rejected; verification requires origin proof |

---

## Test Family 8 — Transport and Observability Leakage Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-8-01 | Leak tenant identifiers in topic names, partition keys, correlation IDs, trace IDs, or queue names | Tenant identifiers not permitted in transport metadata |
| PF-ADV-8-02 | Leak raw payloads through tracing spans, metrics labels, Sentry breadcrumbs, or APM tags | Observability tooling sanitized before export |
| PF-ADV-8-03 | Embed tenant identifiers in shared cache keys | Cache keys sanitized; tenant identifiers not permitted |
| PF-ADV-8-04 | Put tenant/vendor/user identifiers into shared artifact filenames, blob paths, or report IDs | Storage paths sanitized |
| PF-ADV-8-05 | Leak tenant identifiers in notification summaries triggered by cross-tenant broadcasts | Notifications sanitized before delivery |
| PF-ADV-8-06 | Deliver safe payload body with unsafe headers, URL parameters, or retry metadata | All message components inspected, not body only |
| PF-ADV-8-07 | Leak tenant data in UI tooltips, alt text, data attributes, hidden columns, or export-only fields | UI rendering does not receive unsanitized tenant data |
| PF-ADV-8-08 | Make forbidden evidence searchable even if not visible in default broadcast view | Search indexes sanitized; forbidden evidence not indexed |

---

## Test Family 9 — Infrastructure and Deployment Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-9-01 | Route production tenant data through staging/dev/test broadcast paths | Environment separation enforced |
| PF-ADV-9-02 | Leave real tenant data in test fixtures, golden files, or snapshot corpora | Test fixtures contain no real tenant data |
| PF-ADV-9-03 | Ship build where tests pass against mock privacy components but production uses different path | Production path verified in CI against real filter |
| PF-ADV-9-04 | Spoof CI status to mark component verified without running privacy tests | CI privacy tests cannot be bypassed or spoofed |
| PF-ADV-9-05 | Deploy worker with filter disabled, pointed at mock breaker, or in permissive mode | Deployment validation rejects permissive configuration |
| PF-ADV-9-06 | Deliver raw messages through legacy endpoints, admin routes, bulk import, or debug routes | All ingress paths route through Privacy Filter |
| PF-ADV-9-07 | Publish directly to internal broker topics using compromised service credentials | Broker ACLs prevent direct publish without filter |
| PF-ADV-9-08 | Trigger DR/failover mode where privacy validation is bypassed | Failover mode does not bypass privacy validation |
| PF-ADV-9-09 | Run historical replay/backfill job publishing old tenant-specific evidence through cross-tenant channels | Backfill jobs subject to same Privacy Filter rules |
| PF-ADV-9-10 | Cause partial dependency failure where sanitizer succeeds but breaker validation is skipped | Partial dependency failure treats as full deny |

---

## Test Family 10 — Model and Baseline Leakage Attacks

| Test ID | Attack | Pass condition |
|---|---|---|
| PF-ADV-10-01 | Poison upstream LLM summarizer to include raw mailbox/vendor details in safe summary | Summarizer output inspected by filter before broadcast |
| PF-ADV-10-02 | Use ambiguous identifiers or context-dependent references that LLM redaction misses | Filter does not rely solely on LLM redaction |
| PF-ADV-10-03 | Embed raw tenant telemetry into globally shared model training, embeddings, or baseline updates | Tenant data not permitted in shared model update channels |
| PF-ADV-10-04 | Broadcast embeddings derived from tenant mailbox content that can be reversed | Embedding broadcasts inspected for leakage risk |
| PF-ADV-10-05 | Force tenant-specific vendor behavior into shared system baseline influencing other tenants | Baseline promotion inspected for cross-tenant influence |
| PF-ADV-10-06 | Mix real tenant evidence with public threat intel so combined payload inherits public-safe status | Blended payloads inspected at item level, not only payload level |

---

## Gate Requirement

```
All 10 test families: 0 failures
Every test ID above: executed and logged
No test skipped without signed waiver from Matt Nichol
```

A component with any adversarial test failure is VULNERABLE, not GATED. Cursor patches. Codex re-reviews. Suite reruns. Gate closes only on 0/0.

---

## Non-Authorizations

- This contract authorizes Cursor to implement the adversarial test suite only.
- This contract does not authorize build of new Privacy Filter features.
- This contract does not amend the Privacy Filter #93 signed contract.
