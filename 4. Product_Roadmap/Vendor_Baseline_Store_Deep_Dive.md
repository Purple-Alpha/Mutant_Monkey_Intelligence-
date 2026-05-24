# Vendor Baseline Store — Implementation Spec (Deep Dive)

**Status:** Spec-first lockdown — pending §11 signature.  
**Authors:** Matt (operator decisions) + AI scribe (capture).  
**Last reviewed:** 2026-05-23 / 2026-05-24 UTC.  
**Source-of-truth links:** `VISION.md` (Stage A/B/C arc), `think_sheet.md` (parked detectors that depend on this primitive), `PROJECT_GUARDRAILS.md` (Guardrails 11 + 12).

This document is the **specification contract** for the Vendor Baseline Store primitive. No implementation lands until the §11 Lockdown Signature is filled in by the operator. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

The Vendor Baseline Store is a per-tenant, hash-only, TTL-bounded historical record of every operationally significant signal observed from a given vendor over time. It is the **foundational primitive** for the next generation of NorthStar deterministic fraud detection — the five detectors that all want the same per-tenant baseline-state surface:

1. **Financial State Ledger / Delta Tripwire** — flags any net-new routing number, SWIFT code, IBAN, account number, or payment-portal URL observed in inbound mail from a vendor.
2. **Document Metadata Fingerprinting** — flags any net-new PDF Producer/Creator fingerprint that does not match the vendor's historical invoice tooling.
3. **Micro-Temporal Mismatches** — flags any send-time-window outside the vendor's historical pattern.
4. **Sender Provenance / Geo-Velocity** — flags any new origin ASN / country / mail-relay for the vendor.
5. **Historical Relationship Density** — flags structural deviations in who the sender normally emails inside the recipient organisation.

Without this primitive, each of those five detectors would have to invent its own one-off state-storage hack. That is exactly the cheap-but-shaky pattern explicitly refused by the operator's 2026-05-23 "I don't build cheap" position. This primitive is the **quality foundation** that makes the next five detectors possible without compromise.

The primitive is also the embodiment, at the code level, of the original `VISION.md` thesis line: *"a swarm that becomes more intelligent over time."* The baseline IS the long-term memory that lets the swarm get sharper week over week without ever storing raw client data.

---

## §1 Scope

### In scope (v1)

- Per-tenant SQLite file with closed-enum signal types.
- Hash-only storage with per-tenant salt derived from the signed policy key.
- 90-day TTL with per-tenant override.
- Three public functions: `ingest_signal`, `check_signal`, `expire_stale_signals`.
- Cross-platform file isolation (Linux `chmod` + Windows `pywin32` DACL).
- Kill switch + tenant isolation manager + audit trail integration.

### Out of scope (v1) — see §10 for deferral rationale

- Fuzzy matching (Levenshtein, locality-sensitive hashing, similarity scoring).
- ML embeddings, vector storage, neural baseline learning.
- Cross-tenant signature sharing (Guardrail 11 — sacred).
- Automatic baseline merging across multiple vendors.
- Statistical anomaly scoring on the baseline itself (the baseline answers "is this string equal to one we've seen?" — anomaly scoring belongs to the detector that consumes the answer).
- Direct ingestion from raw email payloads — that is a detector-side concern. The Vendor Baseline Store accepts already-normalised values from the calling detector.

---

## §2 Locked Architectural Decisions

Every decision below was operator-locked during the 2026-05-23 design session. Implementation must honour these decisions exactly. Changing any one of them requires re-opening this spec, not a code-level workaround.

| # | Decision | Locked Value | Operator Rationale |
|---|---|---|---|
| D1 | Storage backend | SQLite | "JSONL fundamentally breaks the speed requirement. As the ingestion loops scale, O(n) read times will spike execution latency and trigger Haven's resource exhaustion kill switch. SQLite delivers the necessary O(log n) index lookups, remains flat and file-based, and integrates cleanly with Dax's append-only audit requirements." |
| D2 | Storage shape | Hash-only | "Don't build a database of vendor banking information. Extract the financial routing strings, run them through a cryptographic hash (like SHA-256), and store the hash." |
| D3 | TTL default | 90 days | "Enforces a strict data posture by default. Ninety days covers standard quarterly billing cycles. If a vendor is inactive for longer, their behavioral data is stale and should be treated as a new baseline upon their next interaction." |
| D4 | TTL override | Per-tenant override key allowed | "Accommodates specific business cycles." |
| D5 | Salt source | Per-tenant, derived from the signed policy key | "Utilises the existing trust root. Guarantees cryptographic isolation per tenant without requiring the swarm to manage and rotate an entirely separate set of secrets. A global salt introduces a single point of failure." |
| D6 | Tenant isolation pattern | Per-tenant SQLite file at `production_state/{tenant_id}/vendor_baseline.sqlite` | "Physical separation at the OS file boundary prevents logic flaws from becoming cross-tenant data leaks." |
| D7 | Connection scoping | Leased dynamically from an isolation manager bound to verified `tenant_id` | Logic-error containment. |
| D8 | File isolation — Linux | `chmod 0o600` on files, `chmod 0o700` on tenant directories | POSIX native, no dependency. |
| D9 | File isolation — Windows | `pywin32` `win32security` DACL: strip inherited permissions, grant `GENERIC_READ \| GENERIC_WRITE` to the current process owner SID only | "Calling `os.chmod(0600)` on Windows is security theater… 'advisory security' is cheap." |
| D10 | Schema discipline | Flat schema, no nested JSON | Audit lookups must be millisecond-class. |
| D11 | Signal-type enum | Closed enum, 7 entries (see §3 below), no agent extensibility | "Restricting the signal types to a strict, non-agent-extensible enum forces data normalization and prevents unstructured text fields from polluting the baseline store." |
| D12 | Code-tree location | `core/production_state/vendor_baseline/` | "Binds the functional logic tightly to the physical environment that houses the isolated database files. It ensures that any engineer or agent modifying the ingestion paths is explicitly aware that they are interacting inside the state perimeter." |
| D13 | Audit integration | Every write appends a Blackboard audit record | Derived from Guardrail 11. |
| D14 | Kill switch integration | Every entry point gates on `is_kill_switch_engaged` | Derived from Guardrail 12. |

### Operational note: Linux migration plan

The operator has stated (2026-05-23) that the long-term production target is Linux and that the migration files are already downloaded; the switch has not yet been performed. Implications:

- Windows DACL handling (D9) is a **dev-only safety net**, not a production posture.
- All cross-platform tests must run on both targets; CI should include a Linux runner before any production rollout.
- The pywin32 dependency must remain `sys_platform == 'win32'`-scoped so Linux installs never pull it.

---

## §3 Schema (SQLite DDL)

The per-tenant database contains exactly one table plus its supporting indexes. There is **no `tenant_id` column** — the file path is the tenant isolation primitive. A `tenant_id` column would be a defence-in-depth duplicate, but per Matt's D6 rationale it is also a single missing `WHERE` clause away from a catastrophic leak. The file boundary is the contract.

```sql
CREATE TABLE vendor_baseline_signals (
    vendor_domain    TEXT NOT NULL,
    signal_type      TEXT NOT NULL,
    signal_hash      TEXT NOT NULL,
    first_seen_at    TEXT NOT NULL,
    last_seen_at     TEXT NOT NULL,
    expires_at       TEXT NOT NULL,
    PRIMARY KEY (vendor_domain, signal_type, signal_hash),
    CHECK (signal_type IN (
        'routing_number',
        'swift_bic_code',
        'iban',
        'account_number',
        'payment_portal_url',
        'pdf_producer_fingerprint',
        'vendor_send_time_window'
    )),
    CHECK (length(signal_hash) = 64),
    CHECK (length(vendor_domain) > 0),
    CHECK (datetime(first_seen_at) IS NOT NULL),
    CHECK (datetime(last_seen_at)  IS NOT NULL),
    CHECK (datetime(expires_at)    IS NOT NULL)
) WITHOUT ROWID;

CREATE INDEX idx_vendor_signals_lookup
    ON vendor_baseline_signals (vendor_domain, signal_type);

CREATE INDEX idx_vendor_signals_expiry
    ON vendor_baseline_signals (expires_at);
```

### Column contracts

| Column | Type | Contract |
|---|---|---|
| `vendor_domain` | TEXT | Already lowercased eTLD+1 root domain (per the header-divergence detector's normalisation rule). Must be non-empty. |
| `signal_type` | TEXT | One of the 7 closed-enum values. CHECK constraint enforces it at DB level; the API layer rejects unknown values before they reach SQLite. |
| `signal_hash` | TEXT | 64-char hex SHA-256 digest. Length-checked at DB level. |
| `first_seen_at` | TEXT | ISO-8601 UTC, e.g. `2026-05-23T21:30:00+00:00`. Set on first ingest of this `(vendor_domain, signal_type, signal_hash)` triple. |
| `last_seen_at` | TEXT | ISO-8601 UTC. Refreshed on every re-ingest. |
| `expires_at` | TEXT | ISO-8601 UTC. Computed at write time as `last_seen_at + ttl_days`. Refreshed on every re-ingest so an actively-used signal does not expire. |

### Signal-type closed enum (v1, locked)

| Enum key | Normalisation rule (applied BEFORE hashing) |
|---|---|
| `routing_number` | 9-digit numeric string, all non-digits stripped. Reject if final length ≠ 9. |
| `swift_bic_code` | Alphanumeric uppercase, all whitespace stripped. Reject if final length ∉ {8, 11}. |
| `iban` | Alphanumeric uppercase, all whitespace stripped. Length 5–34. |
| `account_number` | Numeric string, all non-digits stripped, leading zeros removed. Reject if empty. |
| `payment_portal_url` | Host portion only, lowercased. Strip protocol, path, query, port, userinfo, trailing dots. e.g. `https://Billing.Vendor.com/pay?x=1` → `billing.vendor.com`. |
| `pdf_producer_fingerprint` | Producer-or-Creator string from PDF metadata, lowercased, runs of whitespace collapsed to single space, leading/trailing whitespace stripped. |
| `vendor_send_time_window` | Integer hour-of-day bucket (0–23) in UTC, rendered as zero-padded 2-char string (`"00".."23"`). |

Normalisation must be performed at the API layer, never inside the SQLite CHECK. The DB stores already-normalised input. Tests in §7 enforce this.

---

## §4 Salt Derivation & Hashing

### Salt derivation

The per-tenant salt is derived from the existing signed policy key (`core.policy.default_signing_key()`) using HKDF-SHA-256:

```
salt_for(tenant_id) = HKDF-SHA-256(
    ikm   = signed_policy_key_bytes,
    salt  = b"",                                    # HKDF salt; the IKM is already secret
    info  = f"vendor_baseline_v1::{tenant_id}".encode("utf-8"),
    L     = 32,                                     # 32 bytes output
)
```

Implementation note: Python stdlib's `hashlib` does not expose HKDF directly. Use `cryptography.hazmat.primitives.kdf.hkdf.HKDF` (already an indirect dependency via existing crypto surfaces) or open-code HKDF on top of `hmac.HMAC` with SHA-256.

### Hashing

```
signal_hash(tenant_id, signal_type, normalised_value) =
    sha256( salt_for(tenant_id) || signal_type.encode() || b"::" || normalised_value.encode() ).hexdigest()
```

The `signal_type` is folded into the hash input so the same numeric string (e.g. `"123456789"`) can never collide between, say, `routing_number` and `account_number` rows for the same vendor — and so that a malicious actor who somehow learned one tenant's salt cannot perform rainbow-table reversal against another tenant's data.

### Hash comparison

All hash comparisons go through `hmac.compare_digest` for constant-time equality. A timing-side-channel that leaks the first-mismatch byte position is **not** acceptable for the per-tenant secret derivation chain.

---

## §5 API Contract

Public surface — exactly three functions plus one read-only helper. Anything else is internal and unimported.

### Module: `core/production_state/vendor_baseline/__init__.py`

Re-exports (and nothing else):

```python
from core.production_state.vendor_baseline.store import (
    BaselineSignalRecord,
    SignalLookupResult,
    SignalState,
    SignalType,
    check_signal,
    expire_stale_signals,
    ingest_signal,
    tenant_database_path,
)
```

### Types

```python
SignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
    "pdf_producer_fingerprint",
    "vendor_send_time_window",
]

SignalState = Literal["new", "known", "expired"]


@dataclass(frozen=True)
class BaselineSignalRecord:
    vendor_domain: str
    signal_type: SignalType
    signal_hash: str          # 64-char hex
    first_seen_at: datetime
    last_seen_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class SignalLookupResult:
    state: SignalState        # "new" | "known" | "expired"
    record: BaselineSignalRecord | None
```

### Functions

#### `ingest_signal`

```python
def ingest_signal(
    *,
    tenant_id: str,
    vendor_domain: str,
    signal_type: SignalType,
    raw_value: str,
    now: datetime,
    ttl_days: int = 90,
) -> BaselineSignalRecord:
    """Normalise `raw_value`, hash it, upsert into the per-tenant store.

    Behaviour:
    - Normalises `raw_value` per the §3 enum-specific rule. If normalisation
      fails (e.g. routing_number that is not 9 digits after stripping), raises
      `BaselineNormalisationError` and writes nothing.
    - Computes the salted SHA-256 hash.
    - If `(vendor_domain, signal_type, signal_hash)` already exists, updates
      `last_seen_at = now` and refreshes `expires_at = now + ttl_days`.
    - Otherwise inserts a new row with `first_seen_at = last_seen_at = now`,
      `expires_at = now + ttl_days`.
    - Appends a Blackboard audit record (per §9).
    - Returns the `BaselineSignalRecord` reflecting the post-write state.
    - Refuses to operate when the kill switch is engaged
      (`KillSwitchEngaged` raised). Wraps the kill-switch check in the same
      pattern the existing 9 loop entry points use.
    """
```

#### `check_signal`

```python
def check_signal(
    *,
    tenant_id: str,
    vendor_domain: str,
    signal_type: SignalType,
    raw_value: str,
    now: datetime,
) -> SignalLookupResult:
    """Detector-side read path. Pure read — no inserts, no updates.

    Behaviour:
    - Normalises `raw_value` per the §3 rule. If normalisation fails, returns
      `SignalLookupResult(state="new", record=None)` (a malformed value is by
      definition new — but the calling detector should also raise / log).
    - Computes the salted SHA-256 hash.
    - Looks up the row; if found AND `expires_at > now`, returns
      `state="known"` with the full record.
    - If found but `expires_at <= now`, returns `state="expired"` with the
      record (the calling detector may treat expired as new, but may also
      surface the staleness in its audit reasoning).
    - If not found, returns `state="new"` with `record=None`.
    - Refuses to operate when the kill switch is engaged.
    - Does NOT append to the audit trail (reads are not audited; only writes
      and TTL cleanup are).
    """
```

#### `expire_stale_signals`

```python
def expire_stale_signals(
    *,
    tenant_id: str,
    now: datetime,
) -> int:
    """Scheduled cleanup pass. Returns the number of rows deleted.

    Behaviour:
    - `DELETE FROM vendor_baseline_signals WHERE expires_at <= ?`.
    - Appends ONE Blackboard audit record summarising the deletion count
      (not one record per row — that would flood the audit log for no
      benefit).
    - Refuses to operate when the kill switch is engaged.
    """
```

#### `tenant_database_path`

```python
def tenant_database_path(tenant_id: str) -> Path:
    """Read-only helper. Returns the resolved path under
    `production_state/{tenant_id}/vendor_baseline.sqlite`.

    Does NOT create the file; does NOT open a connection. Used by tests
    and by the isolation-manager wiring for path verification.
    """
```

### Connection management

A new isolation-manager module (`core/production_state/vendor_baseline/isolation.py`) leases connection handles bound to a verified `tenant_id`. Direct `sqlite3.connect()` calls in the rest of the codebase are forbidden — there must be exactly one place that opens vendor-baseline databases, and every caller goes through the manager. The lock-down is enforced by a `tests/test_vendor_baseline_isolation_boundary.py` test that greps the codebase for unauthorised `sqlite3.connect(.*vendor_baseline.*)` usage.

---

## §6 TTL Enforcement Strategy

**Hybrid: lazy filter + scheduled cleanup.**

- **Lazy (correctness).** Every `check_signal` filters on `expires_at > now`. This is the contract — a detector calling `check_signal` against an expired baseline will see `state="expired"` even if the cleanup pass has not yet run. Correctness does not depend on cleanup timing.
- **Scheduled (hygiene).** A daily `expire_stale_signals` call (operator-scheduled, NOT autonomous) prunes expired rows. The schedule is **not** part of v1 — v1 ships the function, operator wires it manually until autonomous scheduling is approved through the normal Guardrail-12 review.

This split means a tampered-with cleanup job cannot silently break the freshness contract; only an actively-failing `check_signal` could, and that is caught by the §7 gate tests.

### Per-tenant TTL override

The TTL is operator-tunable via a new per-tenant override key, slotted into the existing `tenant_overrides` surface:

- Key: `vendor_baseline_ttl_days`
- Default: `90`
- Allowed range: `30..365` (operator can override per tenant, but cannot disable TTL — there is no "infinite" value)
- Read site: `ingest_signal` resolves the effective TTL via the existing `tenant_override_operator` read path before computing `expires_at`.

---

## §7 Gate Tests (the contract the implementation must pass)

Every implementation receipt that claims to land §5 must pass **all** of the following tests, written under `tests/test_vendor_baseline_store.py` and `tests/test_vendor_baseline_isolation_boundary.py`. The full list:

1. **File path resolution.** `tenant_database_path("tenant_demo")` resolves to `production_state/tenant_demo/vendor_baseline.sqlite` relative to the production-state root.
2. **File creation permissions — Linux.** On Linux, after `ingest_signal` creates the file, `stat()` reports mode `0o600` for the file and `0o700` for the containing directory. Skipped on `sys.platform == 'win32'`.
3. **File creation permissions — Windows.** On Windows, after `ingest_signal` creates the file, a DACL inspection via `win32security` shows: no inherited ACEs, exactly one ACE granting `GENERIC_READ | GENERIC_WRITE` to the current process owner SID, no `SYSTEM`/`Administrators` ACEs unless they are the current user. Skipped on Linux.
4. **Cross-tenant file separation.** `ingest_signal` for `tenant_a` and `tenant_b` produces two distinct database files, and `tenant_a`'s file contains zero rows with any data derived from `tenant_b`'s inputs.
5. **Closed-enum rejection.** `ingest_signal` with `signal_type="bogus"` raises `BaselineSignalTypeError` and writes nothing.
6. **Normalisation: routing_number.** `ingest_signal` with `raw_value="123-456-789"` and `"123 456 789"` produce identical hashes; `raw_value="12345"` raises `BaselineNormalisationError`.
7. **Normalisation: each enum entry.** One test per enum entry pinning the normalisation contract from §3.
8. **Per-tenant salt isolation.** Same `(vendor_domain, signal_type, raw_value)` ingested into two different tenants produces two different `signal_hash` values. Same triple ingested into the same tenant twice produces the same hash.
9. **New vs known.** First `check_signal` on a brand-new value returns `state="new", record=None`. After `ingest_signal`, the same `check_signal` returns `state="known"`.
10. **Refresh on re-ingest.** Re-ingesting the same `(vendor_domain, signal_type, raw_value)` updates `last_seen_at` and pushes `expires_at` forward by `ttl_days` from the new `now`. `first_seen_at` is preserved.
11. **TTL expiry path.** Ingest with `now = t`, then `check_signal` with `now = t + 91 days` returns `state="expired"` with the record.
12. **Per-tenant TTL override.** Setting `vendor_baseline_ttl_days = 30` for one tenant produces 30-day expiry for that tenant only; another tenant's records still expire at 90 days.
13. **TTL override range enforcement.** A TTL override value of `0`, `29`, `366`, or non-int raises an override-validation error before the override is persisted.
14. **Cleanup pass.** `expire_stale_signals` deletes only rows with `expires_at <= now`. Returns the correct row count. Writes one audit summary.
15. **Kill switch — ingest.** With the kill switch engaged, `ingest_signal` raises `KillSwitchEngaged` and writes nothing.
16. **Kill switch — check.** With the kill switch engaged, `check_signal` raises `KillSwitchEngaged`.
17. **Kill switch — cleanup.** With the kill switch engaged, `expire_stale_signals` raises `KillSwitchEngaged` and deletes nothing.
18. **Audit trail — write.** After `ingest_signal`, a Blackboard audit record exists describing the ingest (no raw value, only hash + signal_type + vendor_domain).
19. **Audit trail — cleanup.** After `expire_stale_signals`, exactly one Blackboard audit summary record exists.
20. **Audit trail — no read leakage.** `check_signal` writes zero audit records.
21. **Connection-pool boundary.** A grep-style test asserts no module other than `core/production_state/vendor_baseline/` calls `sqlite3.connect()` against any vendor-baseline path. Any future module that needs vendor-baseline access must go through the isolation manager.
22. **Constant-time hash compare.** A unit test on the comparison helper asserts use of `hmac.compare_digest` (no `==` on raw hex strings).
23. **Schema enforcement.** Direct attempt to INSERT a `signal_type` outside the closed enum via raw SQL fails on the SQLite CHECK constraint.
24. **Path traversal hardening.** `tenant_id` values containing `..`, `/`, `\`, leading whitespace, or non-printable characters are rejected before path resolution.

If any test in this list does not pass, the implementation receipt is **not** allowed to claim §5 closed. Drift, not progress.

---

## §8 Cross-Platform File Isolation

Locked per D8 + D9. Implementation detail per platform:

### Linux / Unix (production target)

```python
import os, stat

def _harden_directory_linux(path: Path) -> None:
    os.chmod(path, stat.S_IRWXU)              # 0o700

def _harden_file_linux(path: Path) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
```

### Windows (dev-only safety net)

```python
import win32security
import ntsecuritycon as con

def _harden_path_windows(path: Path) -> None:
    sd = win32security.GetFileSecurity(
        str(path), win32security.DACL_SECURITY_INFORMATION
    )
    dacl = win32security.ACL()
    user_sid, _, _ = win32security.LookupAccountName(
        None, win32api.GetUserName()
    )
    dacl.AddAccessAllowedAce(
        win32security.ACL_REVISION,
        con.GENERIC_READ | con.GENERIC_WRITE,
        user_sid,
    )
    sd.SetSecurityDescriptorDacl(1, dacl, 0)  # 1 = present, 0 = NOT inherited
    win32security.SetFileSecurity(
        str(path), win32security.DACL_SECURITY_INFORMATION, sd
    )
```

The "no inheritance" property is critical — without it the file inherits the `production_state` parent's ACL, which may include `Users` group read. Stripping inheritance is what makes this real and not theatre.

Dependency declaration in `requirements.txt` (or equivalent):

```
pywin32 ; sys_platform == 'win32'
```

This MUST be conditional so Linux installs never pull it.

---

## §9 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Guardrail 11 (tenant isolation, sacred) | Per-tenant SQLite file (D6) + isolation-manager-leased connection (D7) + file-system ACL (D8/D9). Three independent layers. |
| Guardrail 12 (kill switch) | Every public entry point in §5 gates on `is_kill_switch_engaged` before any disk operation. Tested under §7 #15–17. |
| Audit trail | Writes append one Blackboard record per ingest; cleanup appends one summary record. Reads append zero records. The raw value is NEVER part of the audit payload — only the hash, signal_type, and vendor_domain. |
| Forbidden actions | The Vendor Baseline Store does NOT send email, write to tenant overrides directly (it READS the TTL override), perform external network calls, write to the policy pipeline, write to the sandbox, or write to any other tenant's directory. Tested by the §7 #21 boundary test. |
| Production-state perimeter | The code lives at `core/production_state/vendor_baseline/` (D12) so any engineer or agent editing it is unambiguously inside the state perimeter and subject to the production-state review discipline. |

---

## §10 V2 Deferrals & Explicit Non-Goals

The following are out of scope for v1 by design. None of them is a "later if we get to it" — each is a deliberate decision NOT to include.

| Deferral | Rationale |
|---|---|
| Fuzzy matching (e.g. Levenshtein distance on routing numbers) | Hash-only storage forbids it by construction. Fuzzy match would require raw value retention, which violates D2. Detector-side detectors can do their own pre-hash normalisation; the store only answers exact-match-after-normalisation. |
| ML embeddings / vector baselines | Out of scope for the deterministic v1 thesis. A separate primitive can be designed if/when an ML detector lane is opened. |
| Cross-tenant signature sharing | Guardrail 11 is sacred. Patterns can cross tenants only at a higher abstraction layer (e.g. signed policy-pipeline rules), never via direct store access. |
| Automatic baseline merging across vendors | A detector concern, not a store concern. The store stays single-vendor-per-row. |
| Statistical anomaly scoring on baseline contents | A detector concern. The store stays equality-only. |
| Raw payload ingestion from email bodies | A detector concern. The store receives already-extracted, already-normalised inputs from the detector. |
| Backup / DR for the per-tenant SQLite files | Listed on the Stage-Crossing Watchlist in `MILESTONE_ARC.md` ("Disaster-recovery plan for Blackboard"); the vendor-baseline store inherits whatever solution is chosen for the broader audit/state surface. |

---

## §11 Lockdown Signature

This spec is **not** locked until the operator fills in the signature block below. Until then, no implementation receipt may claim closure of §5.

```
LOCKED BY: Matt (operator)
LOCK DATE: 2026-05-23
COMMENTS:  All 14 architectural decisions (D1-D14) locked end-to-end during
           the 2026-05-23 design session, including cross-platform file
           isolation Option 1 (POSIX 0600/0700 on Linux + pywin32 DACL with
           stripped inheritance on Windows). Long-term production target is
           Linux; Windows DACL handling is a dev-only correctness safety
           net. Implementation work does NOT begin until operator gives the
           explicit "start build" signal — spec is locked, but build queue
           is not yet promoted. §7 24-test gate is the closure contract;
           partial implementations do not close §5.
```

Once signed:
- Every implementation receipt must cite this file by section number (e.g. "§5 API contract + §7 gate tests passed").
- Any deviation from a §2 locked decision requires a new spec revision, not a code-level workaround.
- The §7 gate test list is the **closure contract**. Partial implementations that pass some-but-not-all §7 tests do not close §5.

---

## Appendix A — Detector Consumption Pattern

Each of the five dependent detectors (per §0) consumes this primitive in the same shape:

```python
result = check_signal(
    tenant_id=ctx.tenant_id,
    vendor_domain=normalised_sender_root,
    signal_type="routing_number",
    raw_value=extracted_routing_number,
    now=now,
)

if result.state in ("new", "expired"):
    # Detector emits its own scored signal (e.g. Financial State Ledger
    # raises a critical-severity "Unverified Financial Delta" finding).
    ...

ingest_signal(
    tenant_id=ctx.tenant_id,
    vendor_domain=normalised_sender_root,
    signal_type="routing_number",
    raw_value=extracted_routing_number,
    now=now,
)
```

The check-then-ingest pattern is intentional: the detector sees the lookup result BEFORE writing, so a brand-new signal is flagged on its first observation. The subsequent ingest establishes the baseline so the second observation is "known".

This pattern is the integration contract every detector that consumes this primitive must follow. Variations should be pushed back through this spec, not invented per detector.
