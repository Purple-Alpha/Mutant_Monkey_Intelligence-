# MMI Proof Gate — Console Bindings Spec (Prerequisite)

**File:** `mmi/project_brain/architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md`  
**Upstream:** `scripts/proof_gate_harness.py` / `proof_gate_summary.json`  
**Downstream consumer:** `MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md` (r3)  
**Status:** SPEC ONLY — build NOT authorized by this document  
**Revision:** r2 — genomic episode binding §3.6 (step 5 prereq)  
**Date:** 2026-07-03

---

## 1. OPERATIONAL DEFINITION

This spec defines the **Gate B summary schema extensions** and **fingerprint ledger writer** required before `console_server.py` can enforce V7, V8, V9, V10, V13, V14, V15 without weakening cross-binding guarantees.

**Doctrine:** Console signs evidence produced by Gate B. If Gate B does not record a field, the console cannot cryptographically bind it. Bundle-builder-derived substitutes are **forbidden** for v1 console bindings.

**Suite marker:** Gate B summaries consumed by the console MUST set:

```json
"suite": "proof_gate_v2_console_bindings"
```

Summaries with `suite: "proof_gate_v1"` only are rejected by console validation (`BAD_GATE_B_SUITE`).

---

## 2. SHARED CANONICAL DIGEST (normative)

All object digests in this spec and the console spec use one function:

```text
canonical_object_digest(obj) =
  sha256(
    json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    .encode("utf-8")
  ).hexdigest()   # 64 lowercase hex chars
```

**Implementation target:** `chaos/mmi_canonical_digest.py` — `canonical_object_digest(obj: dict) -> str`

Used for: `proof_of_fix_digest`, `proof_of_regression_digest`, `budget_telemetry_snapshot` digest, manifest fields.

---

## 3. GATE B SUMMARY SCHEMA ADDITIONS

`proof_gate_harness.py` MUST emit these fields on every run (CLEAN or BLOCKED). Console validation requires them on CLEAN summaries.

### 3.1 Run identity + timestamps

| Field | Type | Rule |
|---|---|---|
| `run_id` | string | Stable for this harness invocation. Format: `pg-<fix_id>-<12 hex chars>` where hex = first 12 of sha256(`fix_id` + `evidence_dir` + `timestamp_ms`). |
| `timestamp_ms` | integer | UTC epoch milliseconds at summary write. **Authoritative for V14 age checks.** |
| `timestamp` | string | RFC3339/ISO8601 UTC display field (optional legacy; not used for age rules). |

If `run_id` or `timestamp_ms` absent → console `MISSING_FIELD`.

### 3.2 Patch artifact binding (V7)

```json
"patch": {
  "patch_path": "/tmp/.../EVIDENCE/patch.diff",
  "patch_hash": "<sha256 hex of patch_path file bytes>",
  "patch_context": "/tmp/.../patch_context_label"
}
```

**Rules:**
- `patch_path` MUST resolve under the run's `evidence_dir`, never inside authority repo.
- `patch_hash` = sha256(raw file bytes at `patch_path`).
- Harness MUST materialize `patch.diff` before proof-of-fix runs (from `proof_context.json` `patch_source` copy, or unified diff of declared patch files). If no patch file exists, summary is `BLOCKED` with blocker `patch artifact missing`.
- Console recomputes sha256(`patch_path`) and requires equality with `patch.patch_hash` AND bundle `patch_hash` AND summary `patch.patch_hash`.

### 3.3 Proof digests for cross-binding (V8, V13)

| Field | Value |
|---|---|
| `proof_of_fix_digest` | `canonical_object_digest(proof_of_fix)` |
| `proof_of_regression_digest` | `canonical_object_digest(proof_of_regression)` |

Console V13: bundle `proof_of_fix_ref.digest` == summary `proof_of_fix_digest`; same for regression.

### 3.4 Rollback lineage (V9, V15)

```json
"rollback": {
  "rollback_token_hash": "<64 hex — pre-patch known-good fingerprint digest>",
  "prior_known_good_run_id": "<run_id of prior ledger entry, or GENESIS>",
  "prior_known_good_digest": "<64 hex — digest of prior known-good state>"
}
```

**Semantics:**
- `rollback_token_hash` = `authority_hash` from this run (= digest of `fp_before` captured at proof-gate start). This is the state rolled back TO if the patch is reverted.
- `prior_known_good_digest` MUST equal an entry in `FINGERPRINT_LEDGER_PATH`.
- `prior_known_good_run_id` = `run_id` of that ledger entry, or `"GENESIS"` for bootstrap.

**Bootstrap (GENESIS):** Operator seeds ledger once via `scripts/console_fingerprint_seed.py` from Phase 1 stability `authority_fingerprint` digest. First real Gate B run chains to GENESIS.

### 3.5 Budget telemetry snapshot source (V10)

```json
"budget_telemetry_snapshot": {
  "run_id": "<same as summary run_id>",
  "budget_spent": 0,
  "budget_cap_day": 8000000,
  "budget_cap_hour": 800000,
  "deadman_armed": true,
  "captured_at_ms": "<integer ms>"
}
```

Captured from control envelope state at proof-gate run end (read-only snapshot). NOT live AFE/dashboard metrics.

Console V10: bundle `budget_telemetry_snapshot.run_id` == summary `run_id`.

---

## 4. FINGERPRINT LEDGER WRITER

### 4.1 Path

`/tmp/mmi_console_server/state/fingerprint_ledger.jsonl` (`FINGERPRINT_LEDGER_PATH` per console spec)

### 4.2 Ledger entry schema

```json
{
  "ledger_version": "fingerprint_ledger_v1",
  "run_id": "pg-fix-abc123",
  "fingerprint_digest": "<64 hex>",
  "source": "proof_gate|genesis_seed|operator_seed",
  "written_at_ms": 1782000000000,
  "prev_entry_hash": "<sha256 of previous line bytes, genesis = 64 zeros>"
}
```

Append-only, hash-chained JSONL (same pattern as console audit log H8).

### 4.3 Writers (who may append)

| Writer | When | Digest recorded |
|---|---|---|
| `scripts/console_fingerprint_seed.py` | Operator bootstrap (once per lab) | Phase 1 baseline fingerprint |
| `proof_gate_harness.py` | On **CLEAN** summary write, before returning | `authority_hash` (`fp_before`) of this run |
| Evolution loop | **NEVER** | — |

**Implementation target:** `chaos/console_fingerprint_ledger.py`

```text
append_known_good(run_id, fingerprint_digest, source, written_at_ms) -> None
  atomic append to FINGERPRINT_LEDGER_PATH
  fail-closed if path outside /tmp/mmi_console_server/state/

ledger_contains(digest: str) -> bool
  linear scan for V15
```

### 4.4 Proof gate harness integration

On `overall_gate_status == "CLEAN"`:
1. Write all §3 fields to summary.
2. Call `append_known_good(run_id, authority_hash, "proof_gate", timestamp_ms)`.
3. Set `rollback.prior_known_good_digest` from ledger tail (or GENESIS entry).
4. Set `rollback.prior_known_good_run_id` accordingly.

On BLOCKED: still emit §3 fields where computable; do NOT append ledger.

---

## 5. IMPLEMENTATION TARGETS (bindings build)

| File | Change |
|---|---|
| `chaos/mmi_canonical_digest.py` | NEW — shared digest helper |
| `chaos/console_fingerprint_ledger.py` | NEW — append + contains |
| `scripts/console_fingerprint_seed.py` | NEW — genesis seed CLI |
| `scripts/proof_gate_harness.py` | EXTEND — v2 summary fields + patch.diff materialization |
| `tests/test_proof_gate_console_bindings.py` | NEW — schema + digest + ledger tests |

**Regression rule:** Existing Gate B behavior for v1 summaries unchanged when `suite` remains `proof_gate_v1`. v2 fields required only when harness invoked with `--console-bindings` (default **off** until Matt authorizes; after authorize, default **on** for new runs).

### 3.6 Genomic episode binding (H14 — step 5 prereq)

When `proof_gate_harness.py` is invoked with `--console-bindings` **and** `--constraint-id`, the summary MUST include:

```json
"genomic_episode": {
  "constraint_id": "grc-...",
  "patch_context_digest": "<64 hex sha256 of patch context tree>",
  "episode_id": "gre-..." 
}
```

| Field | Rule |
|---|---|
| `constraint_id` | Required when any genomic episode flag is set. From `genomic_constraint_v1.constraint_id`. |
| `patch_context_digest` | Required. `patch_context_tree_digest(patch_context_root)` from `mmi_canonical_digest.py`. |
| `episode_id` | Optional audit cross-ref. |

Digest algorithm: sorted walk of all files under patch context root; each line `relative_path:file_sha256_hex`; outer sha256 of joined lines (UTF-8, `\n` separated).

CLI flags: `--constraint-id`, `--episode-id`, `--patch-context-digest` (digest auto-computed from `--patch-context` when omitted).

Non-genomic Gate B runs omit `genomic_episode` entirely (backward compatible).

---

## 6. PASS / FAIL LINES

| Check | Pass | Fail |
|---|---|---|
| CLEAN v2 summary | All §3 fields present + ledger append | BLOCKED + blockers |
| patch.diff exists | sha256 matches `patch.patch_hash` | BLOCKED `patch artifact missing` |
| Ledger append | New line hash-chained | IOError → harness exit 1 |
| Genesis seed | One GENESIS entry queryable | Console V15 fails until seeded |

---

## 7. NON-GOALS

- Weakening console V7/V13 to bundle-only derivation
- Writing ledger from evolution loop or genomic realignment
- Authority repo writes

---

## 8. BUILD ORDER RELATIVE TO CONSOLE

```text
Bindings build (this spec) ──► Console build (r3 spec)
         │                              │
         └─ Codex BUILDABLE ────────────┴─ Codex BUILDABLE (only after bindings merged OR same PR)
```

Matt may authorize as **one build** (`mmi-console-server-step4-package`) covering bindings + console, or **two sequential builds**. Console-only build remains NOT BUILDABLE until bindings land.

---

**SIGN-OFF:** `[x] PASS WITH REVISIONS  [ ] PASS  [ ] FAIL` — r1 resolves Codex blockers 1–6 via upstream schema + ledger writer; no console weakening.
