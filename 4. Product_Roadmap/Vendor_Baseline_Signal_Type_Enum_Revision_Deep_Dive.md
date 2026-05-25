# Vendor Baseline Store — Signal-Type Enum Revision (Deep Dive)

**Status:** Spec-first draft — pending §11 signature  
**Authors:** Matt (operator decisions) + AI scribe (capture)  
**Date:** 2026-05-24  
**Source spec:** `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md`  
**Runtime target:** `core/production_state/vendor_baseline/store.py`

This document is a proposed addendum to the signed Vendor Baseline Store contract.
It does **not** authorize implementation until §11 is signed by Matt.

---

## §0 Purpose

The original Vendor Baseline Store shipped with a closed seven-entry
`SignalType` enum:

1. `routing_number`
2. `swift_bic_code`
3. `iban`
4. `account_number`
5. `payment_portal_url`
6. `pdf_producer_fingerprint`
7. `vendor_send_time_window`

That closed enum was the correct v1 posture. It prevented agents from turning
the baseline into an unstructured dumping ground.

Two downstream promoted detector ideas now need explicitly-governed baseline
slots before they can be implemented:

- **Sender-provenance / geo-velocity** — compare observed sender-origin
  metadata against a vendor's historical origin metadata.
- **Callback phishing / TOAD phone baselining (Part 2)** — compare phone
  numbers included in callback-payment / fake-support emails against known
  vendor phone numbers.

This addendum defines the smallest safe enum expansion to support those future
detectors without shipping either detector yet.

---

## §1 Non-Goals

This spec does **not** implement:

- Sender-provenance / geo-velocity scoring.
- Callback phishing / TOAD scoring.
- GeoIP, ASN, DNS, WHOIS, RDAP, or reputation lookups inside runtime scoring.
- A new storage backend.
- Cross-tenant sharing.
- Raw `Received:` header storage.
- Raw phone-number storage.
- Automatic vendor trust decisions.

The baseline remains hash-only, per-tenant, TTL-bounded, and detector-owned.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Revision style | Additive enum expansion only | Existing seven signal types keep exact names and normalization contracts. No migration may rename, reinterpret, or delete existing rows. |
| D2 | New sender-origin signal types | Add `sender_origin_provider`, `sender_origin_asn`, `sender_origin_country` | Covers the stable classes a future sender-provenance detector can use without storing raw `Received:` chains. |
| D3 | New callback-phone signal type | Add `vendor_callback_phone_number` | Gives future TOAD Part 2 a baseline slot for known vendor phone numbers without inventing a separate store. |
| D4 | Runtime lookup boundary | No live DNS / GeoIP / ASN / phone reputation lookup inside Vendor Baseline Store | The store accepts already-normalized detector inputs only. Enrichment, if ever used, belongs in a separately-signed detector/operator workflow. |
| D5 | No detector activation | Adding enum values does not activate sender-provenance or TOAD scoring | The store can learn/check a value only when a future signed detector calls it. This addendum is prerequisite plumbing, not detection policy. |
| D6 | Sender-origin proof gate | Sender-provenance detector remains blocked until `Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md` records a positive proof run | The enum expansion can be prepared, but scoring must still honor the already-recorded cheaper-proof gate. |
| D7 | Hash-only continuity | New signal values are normalized then hashed using the existing salt/hash scheme | No raw ASN, country, provider label, relay host, or phone number persists in SQLite. |
| D8 | Audit continuity | Writes / cleanup still append `vendor_baseline_audit`; reads still do not audit | Same behavior as the original spec. |
| D9 | SQLite migration | Existing per-tenant DBs with the seven-value CHECK constraint must be migrated by rebuilding the table in a transaction | SQLite cannot widen a CHECK constraint in place. Migration must preserve rows and indexes. |
| D10 | Failure posture | Unknown / invalid new signal values fail closed with `BaselineSignalTypeError` or `BaselineNormalisationError` before SQLite | Same API-layer rejection discipline as v1. |

---

## §3 Expanded Signal-Type Enum

After this spec is signed and implemented, the closed enum becomes:

```python
SignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
    "pdf_producer_fingerprint",
    "vendor_send_time_window",
    "sender_origin_provider",
    "sender_origin_asn",
    "sender_origin_country",
    "vendor_callback_phone_number",
]
```

The corresponding SQLite `CHECK (signal_type IN (...))` must include exactly
those eleven values.

---

## §4 New Normalization Contracts

All normalization still happens in the API layer before hashing.

| Enum key | Normalization rule (applied BEFORE hashing) |
|---|---|
| `sender_origin_provider` | Lowercase ASCII provider class label. Trim leading/trailing whitespace. Collapse internal whitespace / underscores / hyphens to a single hyphen. Allowed characters after normalization: `a-z`, `0-9`, `.`, and `-`. Reject if empty or >128 chars. Examples: `Microsoft 365` -> `microsoft-365`, `Google Workspace` -> `google-workspace`, `aws-ses` -> `aws-ses`. |
| `sender_origin_asn` | Accept `AS12345`, `asn 12345`, or `12345`; normalize to `AS` + integer with no leading zeros (except `AS0` is rejected). Reject if not numeric after optional prefix stripping or outside `1..4294967295`. |
| `sender_origin_country` | ISO 3166-1 alpha-2 country code only. Uppercase and trim. Reject if final value does not match `^[A-Z]{2}$`. Unknown / cloud-normalized / global provider cases must not be coerced to fake country labels. |
| `vendor_callback_phone_number` | Conservative E.164-style number. Strip spaces, hyphens, parentheses, and dots. If the result starts with `+`, require `+` followed by 8-15 digits. If the result has no `+`, require 10-15 digits and prefix `+` only when a future signed detector explicitly supplies a default country rule. Until then, implementation should reject ambiguous no-plus numbers instead of guessing. |

### Phone-number ambiguity rule

No implementation may silently assume North America, Canada, or the tenant's
country for `vendor_callback_phone_number` unless a future signed detector spec
defines that default. Phone-number baselines are high-impact; false confidence is
worse than no signal.

---

## §5 SQLite Migration Contract

Because the existing schema pins the seven-value enum in a `CHECK` constraint,
implementation must migrate existing tenant databases by rebuilding the table.

Required migration shape:

1. Open the per-tenant DB through the existing isolation manager only.
2. Start a transaction.
3. Create a replacement table with the expanded eleven-value `CHECK`.
4. Copy all existing rows unchanged.
5. Recreate `idx_vendor_signals_lookup`.
6. Recreate `idx_vendor_signals_expiry`.
7. Drop the old table.
8. Rename replacement table to `vendor_baseline_signals`.
9. Commit.

Safety requirements:

- Existing rows must keep exact `vendor_domain`, `signal_type`, `signal_hash`,
  `first_seen_at`, `last_seen_at`, and `expires_at`.
- Migration must be idempotent.
- Migration must not write Blackboard audit rows by itself unless it deletes or
  rewrites semantic data. Pure schema widening is not a detector observation.
- If migration fails, the original table must remain intact.

---

## §6 Implementation Gate Tests

Implementation is not closed until all tests below pass.

1. `SignalType` includes exactly the original seven values plus the four new values.
2. SQLite schema CHECK accepts all eleven values.
3. SQLite schema CHECK rejects an unknown value by direct SQL insert.
4. Existing seven signal-type normalization tests still pass unchanged.
5. `sender_origin_provider` normalizes `Microsoft 365` -> `microsoft-365`.
6. `sender_origin_provider` rejects empty / punctuation-only labels.
7. `sender_origin_asn` normalizes `AS001234` -> `AS1234`.
8. `sender_origin_asn` rejects `AS0`, negative values, non-numeric values, and >`4294967295`.
9. `sender_origin_country` normalizes `ca` -> `CA`.
10. `sender_origin_country` rejects `ZZZ`, `1A`, empty, and cloud-placeholder strings like `global`.
11. `vendor_callback_phone_number` accepts unambiguous E.164 input like `+12505550199`.
12. `vendor_callback_phone_number` rejects ambiguous local/national numbers until a future signed detector defines a country-default rule.
13. New signal types store only hashes; raw provider / ASN / country / phone input does not appear in SQLite rows or audit payloads.
14. New signal types participate in `check_signal` / `ingest_signal` / `expire_stale_signals` with the same `new` / `known` / `expired` behavior as existing types.
15. Existing seven-value tenant databases migrate without losing rows.
16. Migration is idempotent across repeated connection leases.
17. Reads still produce no `vendor_baseline_audit` rows.
18. Writes for new signal types append the same data-minimized audit payload shape as existing signal types.
19. Kill switch still blocks every public entry point before disk work.
20. No runtime sender-provenance or TOAD detector is activated by this enum expansion.
21. `audit_tools/grok_audit_runner.py` gains an audit target for this enum revision package if implementation begins.
22. Full runtime suite passes with zero regressions.

---

## §7 Deferred Decisions

The following remain explicitly deferred:

- Which sender-origin field is trusted when a `Received:` chain has multiple hops.
- Whether provider class is operator-supplied, connector-supplied, or derived
  from an offline local database.
- Whether ASN/country enrichment is allowed outside runtime scoring.
- Whether phone-number normalization may use a tenant default country.
- What risk floor a future `new sender origin` or `new callback phone number`
  finding should recommend.
- Which Tiered Detection profile enables each future detector.

Each deferred item belongs in the detector-specific spec, not in the Vendor
Baseline Store primitive.

---

## §8 Stop Conditions

Do not implement this enum revision if:

- The sender-provenance cheaper proof fails.
- The only immediate use case is speculative.
- Implementation would require runtime network lookups.
- The migration cannot be made idempotent and lossless.
- Phone normalization would require guessing country context.
- The proposed detector would emit raw `Received:` chains or phone numbers in
  client-visible analysis.

---

## §9 Handoff

If Matt signs this addendum, the next implementation lane is:

1. Widen the closed `SignalType` enum and `SIGNAL_TYPES`.
2. Add the four normalization branches.
3. Implement idempotent schema widening for existing tenant DBs.
4. Add the §6 gate tests.
5. Add a Grok audit target for the enum revision.
6. Run focused tests, full suite, Grok audit, and pre-ship gate.

This still does **not** authorize sender-provenance or TOAD detector code.

---

## §11 Lockdown Signature

**Operator:** Matt Nichol  
**Decision:** Pending  
**Signature:**  
**Date:**  

Implementation may not begin until this section is filled in.
