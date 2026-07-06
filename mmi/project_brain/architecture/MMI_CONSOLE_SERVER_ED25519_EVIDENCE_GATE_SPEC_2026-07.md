# MMI CONSOLE SERVER — ED25519 EVIDENCE GATE SPEC
**File:** `mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md`
**Target:** `scripts/console_server.py` (NOT BUILT — this spec is the build contract)
**Doctrine anchor:** `MMI_AGI_EVOLUTION_PATHWAY.md` §2 Pillar 4 (Asymmetric Signature Gate), §5 step 4; `MMI_DIFFERENTIATOR_2026-07.md` §2 (proof before signature)
**Status:** SPEC ONLY — build NOT authorized by this document  
**Revision:** r3 — Codex plan-review blocker resolution (see REVISION LOG)  
**Prerequisite:** `architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md` (r1) — MUST be built first or in same authorized package  
**Date:** 2026-07-03

---

## 1. OPERATIONAL DEFINITION

The console server is the **human evidence-signoff gate** for AGI §5 step 4. It does exactly three things:

1. **Ingest + validate** a candidate evidence bundle derived from Gate B output (`proof_gate_summary.json`). Validation is deterministic, rule-based, and runs BEFORE any signature is accepted. A bundle that fails validation cannot enter the sign path at all.
2. **Present** the validated bundle to the operator (Matt) for review — patch hash, proofs, rollback token, budget snapshot — as structured data, never as free-text summary. The review response includes the exact `manifest_hash` the operator's client must sign, so the operator can compare displayed vs signed material out-of-band.
3. **Verify** an operator-supplied Ed25519 signature over the **canonical manifest bytes** (domain-separated, server-recomputed) of that exact bundle, and on success emit an append-only `console_signoff_record.json` outside the authority repo.

**Core doctrine — the operator signs evidence, not intent.** The signable object is never "I approve this change." It is the canonical manifest, machine-derived from the five Pillar 4 evidence elements and recomputed independently by the server at verify time. If the proofs are failed, missing, tampered, substituted, or stale, there is no valid manifest to sign, and a cryptographically valid signature over anything else is rejected. The gate makes it impossible to sign an unsafe change even when the operator wants to.¹

**Trust model:**
- Server holds the operator **public key only** (verify-only). The private key never touches the server process, its filesystem, its config, or any request field the server parses (§3.3 H6, H10).
- Signing happens client-side (browser WebCrypto/CLI signer on the operator machine) as an isolated operator step.
- Server is local chaos-lab tooling: binds `CONSOLE_BIND` loopback only, is not a production deploy authority, and cannot write into the authority repo.
- **Downstream tooling never trusts the console by file existence alone.** Any consumer of a signoff record MUST independently re-verify the Ed25519 signature against the manifest reconstructed from the record (§3.3 H5). A forged or copied record file authorizes nothing.

### 1.1 Constants table (all thresholds named — no soft values)

| Constant | Value | Meaning |
|---|---|---|
| `CONSOLE_BIND` | `127.0.0.1` | Bind address. Never `0.0.0.0`. |
| `CONSOLE_PORT` | `8767` | Distinct from kinetic war room server port.² |
| `BUNDLE_VERSION` | `"console_evidence_v1"` | Only accepted bundle schema version. |
| `MANIFEST_DOMAIN` | `"mmi_console_signoff_v1"` | Domain-separation string baked into every manifest. |
| `MANIFEST_HASH_ALGO` | `sha256` | Digest used for manifest identification and audit chaining. |
| `SIG_ALGO` | `Ed25519` | Only accepted signature algorithm. |
| `REPLAY_WINDOW_MS` | `300000` | Max age (5 min) of `signed_at_ms` vs server clock at verify. |
| `MAX_CLOCK_SKEW_MS` | `30000` | Max future skew tolerated on `signed_at_ms`. |
| `MAX_BUNDLE_BYTES` | `1048576` | Max serialized bundle size (1 MiB). Oversize → `BUNDLE_TOO_LARGE`. |
| `MAX_SIG_B64_BYTES` | `128` | Max length of `signature_b64` field (Ed25519 sig = 88 b64 chars). Oversize → `SIG_INVALID`. |
| `VALIDATE_TTL_MS` | `900000` | Max age (15 min) of a VALID verdict before sign requires revalidation. |
| `GATE_B_MAX_AGE_MS` | `86400000` | Max age (24 h) of the Gate B summary at validate time. Older → `GATE_B_STALE`. |
| `AUDIT_ROOT` | `/tmp/mmi_console_server/` | All console state/evidence. Outside authority repo. |
| `SIGNOFF_DIR` | `/tmp/mmi_console_server/signoff/` | `console_signoff_record.json` per bundle. |
| `AUDIT_LOG_PATH` | `/tmp/mmi_console_server/audit/console_audit.jsonl` | Append-only, hash-chained JSONL audit log. |
| `SIGN_SEQ_PATH` | `/tmp/mmi_console_server/state/sign_seq.json` | Monotonic sign counter, atomic write. |
| `CONSUMED_SET_PATH` | `/tmp/mmi_console_server/state/consumed.jsonl` | Single-use ledger of consumed signoff records. |
| `FINGERPRINT_LEDGER_PATH` | `/tmp/mmi_console_server/state/fingerprint_ledger.jsonl` | Known-good authority fingerprints, written by control envelope path — never by the loop.³ |
| `OPERATOR_PUBKEY_PATH` | `/tmp/mmi_console_server/keys/operator_ed25519.pub` | Verify-only public key (raw 32 bytes).⁴ |
| `HARNESS_EVIDENCE_DIR` | `/tmp/mmi_console_server/harness/` | Harness output root. |

All timestamps are **integer epoch milliseconds** (`*_ms`). No floats anywhere in signed material (§4.2).

---

## 2. BOUNDARY VS ADJACENT SYSTEMS

| System | Relationship | Boundary rule |
|---|---|---|
| `scripts/proof_gate_harness.py` (Gate B) | **Upstream producer.** Its `proof_gate_summary.json` (`suite: proof_gate_v2_console_bindings`) is the sole proof source. See `MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md`. | Console never re-runs exploits or regression suites. `overall_gate_status != "CLEAN"` or `suite != proof_gate_v2_console_bindings` → reject. Bundle fields MUST equal summary-recorded `patch`, `proof_of_fix_digest`, `proof_of_regression_digest`, `run_id`, `rollback`, and `timestamp_ms` (V0, V7–V10, V13–V15). |
| `chaos/weapon_battlefield_scoring.py` | Provides `generate_proof_bundle()` / `fingerprint_digest()` patterns the bundle builder mirrors. | Console does not import scoring logic; it verifies hashes only. |
| `chaos/mmi_control_envelope.py` | **Downstream consumer.** Signed `SIGN_ACK` / `SIGN_RESUME` records replace interim file-based `human_advance_ack` writes (§1.3 ack channel, step 4). Budget snapshot read at Gate B run time (bindings §3.5). | Adapter interface only in this spec (§5.2). Fingerprint ledger writer is `chaos/console_fingerprint_ledger.py` per bindings spec §4 — NOT the evolution loop. |
| `scripts/kinetic_war_room_server.py` | **Sibling, separate process.** Structure mirrored (FastAPI, loopback bind, `/tmp` evidence). | **Decision: separate process, not an extension.** Justification: the war room is an unauthenticated read-only telemetry display; the console holds signoff authority. Merging them puts a signature-verifying trust boundary inside a websocket broadcast surface. Separate process = separate port, separate audit root, smaller attack surface, and the telemetry server can crash/restart without invalidating sign state. The dashboard's `[EXECUTE IMMUNIZATION]` button becomes a link-out to the console UI, not an in-process endpoint. **The war room holds no operator pubkey, no sign_seq state, and no route that writes to `SIGNOFF_DIR`; because downstream re-verifies signatures (H5), a record minted by anything other than the operator's private key is inert.** |
| AFE / telemetry display metrics | **Display only — zero authority.** | Telemetry values (AFE scores, dashboard health badges, websocket feeds) never appear in the bundle, the manifest, or any validate/sign rule (H9). A green dashboard is not evidence; only Gate B artifacts are. The console UI sign panel renders Gate B proof data exclusively and MUST NOT render telemetry-derived status in or adjacent to the sign control. |
| `chaos/metadata_ingress_gate.py` | **Pattern source only.** Ed25519 verify idiom (`Ed25519PublicKey.from_public_bytes` → `verify`, fail-closed on `InvalidSignature`) is reused. | Console does NOT replace agent packet signing. Different key, different `MANIFEST_DOMAIN` — a signature valid in one domain is structurally invalid in the other (cross-protocol replay dead). |
| Authority repo (`/mnt/c/MMI`) | Read-only input. | Console never writes into the authority repo. All writes path-prefix-checked against `AUDIT_ROOT`. No promote/apply occurs in-process, ever. |

---

## 3. PASS / FAIL LINES + HARD RULES

### 3.1 Validate verdict — `VALID` requires ALL of:

| # | Rule | Reject code on failure |
|---|---|---|
| V0 | Gate B summary `suite == "proof_gate_v2_console_bindings"` | `BAD_GATE_B_SUITE` |
| V1 | `bundle_version == BUNDLE_VERSION` | `BAD_VERSION` |
| V2 | Serialized size ≤ `MAX_BUNDLE_BYTES` | `BUNDLE_TOO_LARGE` |
| V3 | Every required field present, correct type, integers only (§4.1) | `MISSING_FIELD` |
| V4 | Referenced `proof_gate_summary.json` exists, parses, and `overall_gate_status == "CLEAN"` | `GATE_NOT_CLEAN` |
| V5 | `authority_intact == true` in Gate B summary | `AUTHORITY_COMPROMISED` |
| V6 | `blockers` in Gate B summary is empty | `GATE_NOT_CLEAN` |
| V7 | `patch_hash` == summary `patch.patch_hash` == sha256(bytes at summary `patch.patch_path`) == bundle `patch_hash` | `HASH_MISMATCH` |
| V8 | `proof_of_fix_ref.digest` == summary `proof_of_fix_digest`; `proof_of_regression_ref.digest` == summary `proof_of_regression_digest` (canonical object digests per bindings §2) | `HASH_MISMATCH` |
| V9 | `rollback_token_hash` == summary `rollback.rollback_token_hash` == summary `authority_hash`; summary `rollback.prior_known_good_digest` exists in `FINGERPRINT_LEDGER_PATH` | `HASH_MISMATCH` / `FINGERPRINT_UNKNOWN` |
| V10 | Bundle `budget_telemetry_snapshot` equals summary `budget_telemetry_snapshot` field-for-field; `run_id` == summary `run_id` | `MISSING_FIELD` / `CROSS_BIND_FAIL` |
| V11 | `operator_action` ∈ {`SIGN_PROMOTE`, `SIGN_RESUME`, `SIGN_ACK`} | `UNKNOWN_OPERATOR_ACTION` |
| V12 | `bundle_id` recomputes: `"ceb-" + sha256(canonical(bundle minus bundle_id))[:16]` equals the claimed `bundle_id` | `BUNDLE_ID_MISMATCH` |
| V13 | **Cross-binding:** bundle `fix_id` == summary `fix_id`; bundle digests == summary `proof_of_fix_digest` / `proof_of_regression_digest`; `gate_b_summary_digest` == sha256(summary file bytes); bundle `patch_hash` == summary `patch.patch_hash` | `CROSS_BIND_FAIL` |
| V14 | Gate B summary `timestamp_ms` (integer UTC epoch ms) within `GATE_B_MAX_AGE_MS` of server clock. Timezone-naive ISO `timestamp` string ignored for age. | `GATE_B_STALE` / `MISSING_FIELD` |
| V15 | `rollback_token_hash` AND `rollback.prior_known_good_digest` each exist in `FINGERPRINT_LEDGER_PATH` | `FINGERPRINT_UNKNOWN` |
| V16 | **Staging immutability:** if `bundle_id` already staged, submitted bytes must be identical to staged bytes | `BUNDLE_ID_CONFLICT` |

Any single failure → verdict `REJECTED` with full `reasons[]` (all failures reported, not first-only). No partial credit. V7+V13 together kill the "omit the failed regression / cite an older green run" attack: the only proofs a bundle may reference are the exact ones the CLEAN summary itself recorded, and the summary must be fresh (V14) and chained to a ledger-known fingerprint (V15).

### 3.2 Sign verdict — `ACCEPTED` requires ALL of:

| # | Rule | Reject code on failure |
|---|---|---|
| S1 | Bundle previously `VALID` and **revalidated inline at sign time** (TOCTOU guard — V1–V16 re-run against the staged immutable copy AND the on-disk evidence) | inherits validate code |
| S2 | Prior VALID verdict age ≤ `VALIDATE_TTL_MS` | `VALIDATION_EXPIRED` |
| S3 | `manifest_hash` in sign request == server-recomputed `sha256(canonical_manifest_bytes)` for that `bundle_id`, where the server rebuilds the manifest itself from the staged bundle + submitted `sign_seq`/`signed_at_ms` | `MANIFEST_MISMATCH` |
| S4 | Ed25519 `verify(signature, canonical_manifest_bytes)` passes against `OPERATOR_PUBKEY_PATH` key — **signature is over the full canonical manifest bytes (domain string included), not over a hash string** | `SIG_INVALID` |
| S5 | `signed_at_ms` within `[now − REPLAY_WINDOW_MS, now + MAX_CLOCK_SKEW_MS]` | `REPLAY_STALE` |
| S6 | `sign_seq` == persisted counter + 1 (strictly monotonic, persisted at `SIGN_SEQ_PATH`, atomic write) | `SEQ_NON_MONOTONIC` |
| S7 | No existing signoff record for this `bundle_id` (one signature per bundle) | `ALREADY_SIGNED` |
| S8 | `signature_b64` length ≤ `MAX_SIG_B64_BYTES` and decodes to exactly 64 bytes | `SIG_INVALID` |

Because S4 verifies over the server-rebuilt manifest bytes, every field-swap variant fails structurally: reordering is neutralized by canonical serialization; substituting `operator_action`, `patch_hash`, or any digest after signing changes the server-side bytes and the verify fails; a valid signature over a *different* manifest than the one displayed in the UI fails S3/S4 because the server never verifies against client-supplied manifest content — only against what it rebuilt from immutable staging (V16).

### 3.3 Hard rules (non-negotiable, enforced in code not prose)

- **H1 — Fail closed.** Any missing proof, unreadable file, parse error, or unexpected exception in validate/sign → `REJECTED`. There is no warn-and-continue path.
- **H2 — Signature covers the canonical manifest only.** No endpoint accepts, stores, or acts on free-text approval. Signed material is machine-derived; operator prose fields do not exist in the manifest schema at all.
- **H3 — Sign-intent attack rejection.** A signature is only meaningful over the exact manifest bytes the server independently rebuilds from the staged, revalidated bundle (S1+S3+S4). Consequences: (a) operator haste — signing a summary blob or stale hash fails S3; (b) machine bypass — the loop cannot forge signatures (no private key server-side) and cannot replay old ones (S5+S6+S7); (c) valid signature over the wrong manifest — cryptographically valid but fails S3/S4 → refused (test T2).
- **H4 — Authority repo read-only** during validate/sign flows. Console opens authority-repo paths read-only; all writes path-prefix-checked against `AUDIT_ROOT`.
- **H5 — No promote/apply without a re-verified, unconsumed signoff record.** Downstream promotion tooling MUST: (1) load `console_signoff_record.json`; (2) rebuild the canonical manifest from the record's embedded manifest fields; (3) re-verify the Ed25519 signature against the operator public key itself; (4) check `patch_hash` equality with the patch it is about to apply; (5) check `(bundle_id, sign_seq)` absent from `CONSUMED_SET_PATH`, then append it atomically before applying. File existence alone authorizes nothing; a copied or replayed record fails step 5; a forged record fails step 3. The console itself never applies patches.
- **H6 — Private key never on server.** No key-loading code path for private material exists in `console_server.py`. Presence of private key material under `AUDIT_ROOT` is a harness failure.
- **H7 — Replay state outside authority.** `sign_seq` and `CONSUMED_SET_PATH` persist under `AUDIT_ROOT` with atomic write (temp file + rename), never inside the repo the loop can influence.
- **H8 — Hash-chained audit.** Every validate/sign attempt (accepted AND rejected) appends one JSONL line to `AUDIT_LOG_PATH` **before** the HTTP response is returned. Each line carries `prev_line_hash = sha256(previous line bytes)` (genesis: 64 zeros), making silent truncation or mid-log deletion detectable by a single linear scan.
- **H9 — Telemetry has zero signoff authority.** No AFE score, dashboard metric, websocket feed, or war-room-derived value may appear in the bundle schema, the manifest, or any V/S rule. Harness statically checks the manifest schema against a telemetry-field denylist. UI requirement: the sign panel renders Gate B evidence only.
- **H10 — No private-key code in the server.** `console_server.py` MUST NOT import `Ed25519PrivateKey` or any signing primitive; verify-only imports permitted. Enforced by harness static scan of the module source (lint check H10 in §7).

---

## 4. DATA SCHEMA

### 4.1 Evidence bundle (`console_evidence_v1`) — maps 1:1 to Pillar 4's five elements

```json
{
  "bundle_version": "console_evidence_v1",
  "bundle_id": "ceb-<sha256(canonical bundle minus bundle_id)[:16]>",
  "created_at_ms": 1782000000000,
  "operator_action": "SIGN_PROMOTE",
  "fix_id": "<from Gate B summary — must match (V13)>",
  "gate_b_summary_path": "/tmp/.../proof_gate_summary.json",
  "gate_b_summary_digest": "<sha256 hex of that file (V13)>",

  "patch_hash": "<sha256 hex of exact patch diff (V7)>",       // Pillar 4 element 1
  "proof_of_fix_ref": {                                        // Pillar 4 element 2
    "exploit_id": "<which exploit, now contained>",
    "evidence_path": "/tmp/...",
    "digest": "<sha256 hex — must equal summary's proof_of_fix digest (V8+V13)>"
  },
  "proof_of_regression_ref": {                                 // Pillar 4 element 3
    "suite": "proof_gate_v1",
    "verdict": "GREEN",
    "evidence_path": "/tmp/...",
    "digest": "<sha256 hex — must equal summary's proof_of_regression digest (V8+V13)>"
  },
  "rollback_token_hash": "<sha256 hex of pre-patch known-good state (V9+V15)>",  // Pillar 4 element 4
  "budget_telemetry_snapshot": {                               // Pillar 4 element 5 — copy of summary field
    "run_id": "<must equal summary run_id (V10)>",
    "budget_spent": 0,
    "budget_cap_day": 8000000,
    "budget_cap_hour": 800000,
    "deadman_armed": true,
    "captured_at_ms": 1782000000000
  }
}
```

All numeric fields are integers. Hex digests are 64-char lowercase. Paths must resolve under `/tmp/` evidence roots, never inside the authority repo. `budget_telemetry_snapshot` is the Gate-B-run budget record — a control-envelope artifact, NOT a live dashboard/AFE metric (H9).

### 4.2 Canonical manifest (the ONLY signable object)

Rebuilt server-side from the immutable staged bundle — never accepted wholesale from the client:

```json
{
  "domain": "mmi_console_signoff_v1",
  "bundle_id": "...",
  "bundle_version": "console_evidence_v1",
  "operator_action": "SIGN_PROMOTE",
  "fix_id": "...",
  "patch_hash": "...",
  "proof_of_fix_digest": "...",
  "proof_of_regression_digest": "...",
  "rollback_token_hash": "...",
  "budget_snapshot_digest": "<sha256 of canonical budget_telemetry_snapshot>",
  "gate_b_summary_digest": "...",
  "sign_seq": 42,
  "signed_at_ms": 1782000000000
}
```

**Canonical JSON rules (no drift, deterministic across processes):**
- `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)` → UTF-8 bytes
- Integers only — floats forbidden in any signed structure (V3 rejects)
- **The Ed25519 signature is computed over these canonical bytes directly** (Ed25519 is a full-message scheme; signing raw bytes removes any hash-encoding ambiguity between hex-string vs raw-digest signing). `manifest_hash = sha256(canonical bytes)` hex is used only as a compact identifier in requests, records, and audit lines (S3 checks it; S4 verifies the bytes).
- `domain` field prevents cross-protocol signature reuse against `metadata_ingress_gate` packets or any future signing surface.

### 4.3 Sign request (client → `POST /api/v1/evidence-bundle/sign`)

```json
{
  "bundle_id": "...",
  "sign_seq": 42,
  "signed_at_ms": 1782000000000,
  "manifest_hash": "<hex — client's computed identifier, checked against server recompute (S3)>",
  "signature_b64": "<Ed25519 sig over canonical manifest bytes, base64, ≤ MAX_SIG_B64_BYTES (S8)>",
  "operator_key_id": "matt-ed25519-01"
}
```

The client obtains the exact manifest field values (including next `sign_seq`) from the GET review response (§4.6), rebuilds the canonical bytes locally, displays the hash to the operator, and signs. Server and client computing the same bytes independently is the UI-integrity guarantee: what was displayed is what was signed, or S3/S4 fails.

### 4.4 Signoff record — `SIGNOFF_DIR/console_signoff_record_<bundle_id>.json`

```json
{
  "record_version": "console_signoff_v1",
  "bundle_id": "...",
  "fix_id": "...",
  "manifest": { "<full §4.2 manifest object, verbatim>" : "..." },
  "manifest_hash": "...",
  "signature_b64": "...",
  "operator_key_id": "matt-ed25519-01",
  "sign_seq": 42,
  "signed_at_ms": 1782000000000,
  "verified_at_ms": 1782000000500,
  "verdict": "ACCEPTED",
  "patch_hash": "...",
  "rollback_token_hash": "..."
}
```

Atomic write (temp + rename). The **full manifest is embedded verbatim** so downstream can rebuild canonical bytes and re-verify the signature with zero trust in the console process (H5 steps 2–3). Single-use: consumption tracked in `CONSUMED_SET_PATH` (H5 step 5) — an old ACCEPTED record can never authorize a second promote or a different patch (`patch_hash` equality, H5 step 4).

### 4.5 Audit log — JSONL, append-only, hash-chained (H8)

```json
{"ts_ms":1782000000000,"event":"VALIDATE|SIGN","bundle_id":"...","verdict":"VALID|REJECTED|ACCEPTED","reasons":["GATE_NOT_CLEAN"],"client":"127.0.0.1","sign_seq":42,"manifest_hash":"...","prev_line_hash":"<sha256 of previous line bytes>"}
```

### 4.6 API contract

| Endpoint | Method | Behavior |
|---|---|---|
| `/api/v1/evidence-bundle/validate` | POST | Body = bundle. Read-only against evidence; runs V1–V16. Returns `{verdict: "VALID"\|"REJECTED", reasons: [], bundle_id, manifest_preview, manifest_hash_preview}`. On VALID, stores bundle bytes immutably under `AUDIT_ROOT/staging/<bundle_id>` (V16 governs resubmission). |
| `/api/v1/evidence-bundle/{bundle_id}` | GET | Staging review. Returns `{bundle, gate_b_summary, diff_view: {patch_path, pre_hash, post_hash}, validation: {verdict, checked_at_ms, reasons}, manifest_fields, next_sign_seq, manifest_hash}` — feeds the side-by-side diff UI and gives the client everything needed to rebuild+sign the exact canonical bytes. |
| `/api/v1/evidence-bundle/sign` | POST | Body = §4.3. Runs S1–S8. `ACCEPTED` → writes signoff record + audit line, increments `sign_seq`. Any failure → HTTP 422 `{verdict: "REJECTED", reasons: []}` + audit line. |

No other mutating endpoints exist. No endpoint accepts a signature at validate time, accepts private key material in any field, or accepts a client-supplied manifest object (only the compact `manifest_hash` identifier crosses the wire on sign).

---

## 5. INTEGRATION SKETCH

### 5.1 Call order

```
Gate B run (proof_gate_harness.py --console-bindings)
  └─ proof_gate_summary.json  (suite: proof_gate_v2_console_bindings, overall_gate_status: CLEAN)
        │                          genesis seed (console_fingerprint_seed.py) if first run
        │                          proof_gate CLEAN → append_known_good(authority_hash) to ledger
        ▼
bundle builder (operator CLI step, mirrors generate_proof_bundle())
  └─ console_evidence_v1 bundle
        │
        ▼
POST /validate ──REJECTED──► reasons[] → audit → STOP (fail closed)
        │ VALID  (bundle frozen in staging — V16)
        ▼
GET /evidence-bundle/{id}  → human review UI (side-by-side diff, proofs, budget,
        │                     manifest_hash displayed to operator)
        ▼
operator rebuilds canonical manifest bytes + signs CLIENT-SIDE
  (private key never leaves operator machine)
        │
        ▼
POST /sign ──S1..S8 (full revalidation + manifest rebuild + verify)──REJECTED──► audit → STOP
        │ ACCEPTED
        ▼
console_signoff_record.json (SIGNOFF_DIR, manifest embedded)  +  hash-chained audit line
        │
        ▼
downstream (H5): re-verify sig → check patch_hash → consume-once → only then promote
```

### 5.2 Control envelope adapter (interface only — implementation out of scope)

```
ConsoleAckAdapter (defined in spec, built with console_server.py):
  poll_signoff(action: SIGN_RESUME | SIGN_ACK) -> record | None
      reads SIGNOFF_DIR for ACCEPTED records of that action type
  verify(record) -> bool
      rebuilds canonical manifest bytes from record.manifest,
      re-verifies Ed25519 signature against operator pubkey (H5 — no file trust)
  consume(record) -> envelope-side effect
      SIGN_ACK    → satisfies human_advance_ack (attendance), envelope bumps its own ack_seq
      SIGN_RESUME → satisfies human_clear_* resume path
  idempotency: (bundle_id, sign_seq) appended to CONSUMED_SET_PATH exactly once,
      atomically, before the effect fires; replayed records are inert
```

The envelope's monotonic `ack_seq` semantics from §1.3 are unchanged; the file-based interim writer is replaced by "signed record exists **and re-verifies and is unconsumed**" as the write precondition.

### 5.3 War room relationship

Separate process (decision + justification in §2). War room dashboard renders a read-only view of `AUDIT_LOG_PATH` and links to the console UI for the `[EXECUTE IMMUNIZATION]` flow; it gains no sign or validate capability, holds no operator pubkey, and cannot mint effective records because downstream re-verification (H5) makes unsigned or wrongly-signed records inert. AFE/telemetry values it displays carry zero signoff authority (H9).

---

## 6. FALSIFIABLE TEST SCENARIOS

| ID | Setup | Action | Expected verdict | Expected route |
|---|---|---|---|---|
| **T1 — clean path** | Real Gate B `CLEAN` summary; ledger entry for rollback fingerprint; bundle built with correct digests + cross-bindings; fresh `signed_at_ms`; `sign_seq = counter+1`; signature by operator test key over server-identical canonical manifest bytes | validate → review GET → sign | validate `VALID`; sign `ACCEPTED` | `console_signoff_record_<id>.json` exists with embedded manifest that independently re-verifies; audit log has chained VALIDATE:VALID + SIGN:ACCEPTED lines; `sign_seq` incremented on disk |
| **T2 — bad evidence, valid crypto** | (a) Gate B summary with `overall_gate_status: BLOCKED`; (b) CLEAN summary but one byte of patch file flipped post-hash; (c) **summary substitution:** bundle cites an older CLEAN summary whose `fix_id`/digests don't match this patch; (d) regression ref pointing at an older green evidence file not recorded in the current summary. In all, produce a **cryptographically valid** Ed25519 signature over the attacker-chosen manifest | validate; then sign anyway | validate `REJECTED` (`GATE_NOT_CLEAN` / `HASH_MISMATCH` / `CROSS_BIND_FAIL`); sign `REJECTED` (S1 inherit or `MANIFEST_MISMATCH`) — valid crypto never rescues bad evidence | No signoff record; audit reject lines; proves H2/H3 + V13: signature over intent ≠ signature over evidence |
| **T3 — replay & manifest games** | (a) Re-submit T1's exact accepted sign request; (b) fresh request with `signed_at_ms` older than `REPLAY_WINDOW_MS`; (c) swap `operator_action` SIGN_ACK→SIGN_PROMOTE after signing; (d) re-POST a mutated bundle under T1's `bundle_id` then sign; (e) downstream replay: feed T1's already-consumed signoff record to the adapter a second time | sign ×4 + adapter consume ×1 | (a) `SEQ_NON_MONOTONIC` (+`ALREADY_SIGNED`); (b) `REPLAY_STALE`; (c) `MANIFEST_MISMATCH`/`SIG_INVALID`; (d) `BUNDLE_ID_CONFLICT` at validate, sign never reached; (e) adapter refuses — `(bundle_id, sign_seq)` already in consumed set | No new signoff records; reject audit lines for each; `sign_seq` unchanged; consumed set unchanged after (e) |

Each scenario is falsifiable: a wrong verdict, a missing/extra signoff record, a broken audit hash chain, or a missing audit line is a hard harness failure.

---

## 7. HARNESS SPEC — `scripts/console_server_harness.py` (name fixed)

Mirrors `proof_gate_harness.py` / control-envelope harness patterns:

- Spins up the FastAPI app in-process (TestClient) — no network dependency, loopback semantics preserved.
- Generates an **ephemeral operator Ed25519 keypair** for the run; private key held only in harness memory (satisfies H6 — nothing private under `AUDIT_ROOT`).
- Fabricates Gate B fixtures (CLEAN and BLOCKED summaries + evidence files + fingerprint ledger entries) under `HARNESS_EVIDENCE_DIR`.
- Runs T1, T2(a–d), T3(a–e) plus four structural checks:
  - **H4** — attempted write into an authority-repo path → refused;
  - **H6** — no private key material under `AUDIT_ROOT` after full run;
  - **H8** — audit hash chain verifies end-to-end by linear scan;
  - **H10** — static scan: `console_server.py` source contains no `Ed25519PrivateKey` import / signing primitive, and manifest schema contains no telemetry-denylist field (H9).
- Emits `HARNESS_EVIDENCE_DIR/console_gate_summary.json`:

```json
{
  "suite": "console_gate_v1",
  "timestamp": "<iso>",
  "scenarios": {"T1":"PASS","T2a":"PASS","T2b":"PASS","T2c":"PASS","T2d":"PASS","T3a":"PASS","T3b":"PASS","T3c":"PASS","T3d":"PASS","T3e":"PASS","H4":"PASS","H6":"PASS","H8":"PASS","H10":"PASS"},
  "overall_gate_status": "CLEAN",
  "blockers": [],
  "evidence_dir": "/tmp/mmi_console_server/harness/"
}
```

- **Exit code 0 iff `overall_gate_status == "CLEAN"`** (every scenario PASS). Any scenario failure → `BLOCKED`, blockers listed, exit 1. No partial pass rates, no averaging — un-fakeable binary gate.

---

## 8. NON-GOALS

- `genomic_realignment_loop.py` (AGI step 5) — not designed here.
- `central_brain.py` Phase 2 (AGI step 6) — not designed here.
- Production orchestrator auto-apply — console produces signoff records; it never applies patches. Promote tooling obligations are stated (H5) but its implementation is out of scope.
- Private key storage, key generation, or key escrow on the server — explicitly forbidden (H6/H10), not deferred.
- Replacing `metadata_ingress_gate` agent packet signing — different domain string, different key, untouched.
- Host boundary Go daemon, M4 48h proof, or any PERFECT claim — evolution gate remains OUTSTANDING.
- Multi-operator / role-based signing — single operator key (`matt-ed25519-01`) in v1.⁶
- Any UI framework decision beyond "renders §4.6 GET data model" — dashboard spec owns visuals.

---

## FOOTNOTES (assumptions)

1. Assumes Gate B artifacts are trustworthy at rest under their `/tmp` evidence dir for the validate window; digest + cross-binding + ledger checks (V7–V9, V13–V15) detect post-hoc tampering and substitution, they do not stop a root-level attacker who owns the whole host. Host-level integrity is the Go daemon's future job (out of scope).
2. `CONSOLE_PORT 8767` assumes the kinetic war room server does not occupy it; adjust constant (not behavior) if it collides.
3. `FINGERPRINT_LEDGER_PATH` is written by `chaos/console_fingerprint_ledger.py` per bindings spec §4 — `proof_gate_harness` on CLEAN and `console_fingerprint_seed` for GENESIS. Evolution loop NEVER writes. V15 fails closed until ledger seeded.
4. Public key provisioning is a manual operator step (copy raw 32-byte pubkey to `OPERATOR_PUBKEY_PATH`). Key rotation = replace file + bump `operator_key_id`; old records stay verifiable against the archived key.
5. V9 rollback lineage: `rollback_token_hash` = current run `authority_hash` (pre-patch known-good). `rollback.prior_known_good_digest` must exist in ledger (chains to GENESIS or prior CLEAN run). See bindings spec §3.4.
6. Single-key v1 accepted deliberately: multi-sig/quorum is a doctrine change, not a console feature, and would require an AGI pathway amendment first.
7. **Build prerequisite:** Console build is NOT BUILDABLE until `MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md` implementation is merged or authorized in the same package.

---

## REVISION LOG (r1 → r2, adversarial self-review)

| Finding | Fix |
|---|---|
| Summary substitution / stale-green regression ref could pass r1 V-rules | Added V13 cross-binding (bundle refs must equal digests inside the CLEAN summary), V14 Gate B freshness, V7 tightened to summary-recorded patch hash |
| Forged rollback_token with self-consistent hashes | Added V15 independent fingerprint ledger check (`FINGERPRINT_LEDGER_PATH`, loop cannot write) |
| Bundle mutation between validate and sign (staging swap) | Added V16 staging immutability + `BUNDLE_ID_CONFLICT`; V12 bundle_id recomputation |
| Hash-encoding ambiguity (sign hex string vs digest bytes) | Signature now defined over full canonical manifest bytes; `manifest_hash` demoted to identifier (S3 id-check, S4 byte verify) |
| UI-displayed manifest ≠ signed manifest | GET returns manifest fields + `next_sign_seq` + hash; client rebuilds bytes independently; server never verifies client-supplied manifest content |
| Signoff record replay / copy authorizing new patch | Record embeds full manifest; H5 now mandates downstream re-verify + patch_hash equality + consume-once via `CONSUMED_SET_PATH`; T3(e) added |
| War room as bypass surface | §2/§5.3 hardened: no pubkey, no sign state, no SIGNOFF_DIR route; records inert without operator signature due to H5 re-verification |
| Private key exfil via server code path | H10 added: no signing-primitive imports, harness static scan; `MAX_SIG_B64_BYTES` input bound |
| AFE/telemetry confused with signoff authority | H9 added + §2 AFE boundary row: telemetry fields denylisted from bundle/manifest/rules and from sign-panel UI |
| Audit truncation hides rejected attempts | H8 upgraded to hash-chained JSONL with genesis anchor; harness H8 chain scan |

## REVISION LOG (r2 → r3, Codex plan review NOT BUILDABLE)

| Codex blocker | Fix |
|---|---|
| V7 patch_hash not in Gate B summary | Bindings spec §3.2 `patch` object; V7 triple-bind bundle/summary/file bytes |
| V13 proof digests missing on summary side | Bindings §3.3 `proof_of_fix_digest` / `proof_of_regression_digest` via `canonical_object_digest` |
| V10 run_id absent | Bindings §3.1 `run_id`; V10 field-for-field budget snapshot equality |
| V15 ledger writer undefined | Bindings §4 `console_fingerprint_ledger.py` + proof_gate CLEAN append |
| V9 rollback lineage unverifiable | Bindings §3.4 `rollback` object + ledger chain to GENESIS |
| V14 ISO vs integer ms ambiguity | Bindings §3.1 authoritative `timestamp_ms`; V14 uses integer only |
| v1 Gate B summaries accepted | V0 `BAD_GATE_B_SUITE` requires `proof_gate_v2_console_bindings` |

---

**SIGN-OFF:** `[x] PASS WITH REVISIONS  [ ] PASS  [ ] FAIL` — r3 integrates Codex blockers via bindings prerequisite; cross-binding guarantees preserved (no weakening).
