# Codex Handoff — Console Server Step 4 Package DIFF REVIEW

**Task id:** `mmi-console-server-step4-package`  
**Assignee:** Codex (post-build diff review)  
**Build auth:** IMPLEMENTED — pending Codex CLEAN  
**Specs:** bindings r1 + console r3

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-console-server-step4-package
REVIEW TYPE: POST-BUILD DIFF REVIEW
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPECS:
  mmi/project_brain/architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md (r1)
  mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md (r3)

FILES CHANGED/ADDED:
  chaos/mmi_canonical_digest.py — NEW
  chaos/console_fingerprint_ledger.py — NEW
  chaos/console_evidence_gate.py — NEW (V0-V16, S1-S8 core)
  chaos/console_ack_adapter.py — NEW
  scripts/console_fingerprint_seed.py — NEW
  scripts/console_bundle_builder.py — NEW
  scripts/console_server.py — NEW (FastAPI verify-only, H10 compliant)
  scripts/console_server_harness.py — NEW
  scripts/proof_gate_harness.py — EXTEND (--console-bindings v2 schema)
  tests/test_proof_gate_console_bindings.py — NEW
  tests/test_console_server.py — NEW

CURSOR VERIFICATION (R1 fixes for NOT CLEAN):
  pytest tests/test_proof_gate_console_bindings.py tests/test_console_server.py — 15/15 PASS
  python3 scripts/console_server_harness.py --evidence-dir /tmp/mmi_console_server/harness_r2 — CLEAN (T1,T2a-d,T3a-e,H4,H6,H8,H10)

R2 FIX (harness hermeticity):
  - console_server_harness.py resets --evidence-dir at start of each run (signoff/staging/state/audit/keys + scenario dirs)
  - test_console_harness_reruns_on_same_evidence_dir verifies double-run CLEAN
  1. V15: rollback_token_hash AND prior_known_good_digest both required in ledger
  2. S2: sign path checks VALIDATE_TTL before revalidate; validate_bundle(update_cache=False) on sign
  3. console_server.py: refuses non-loopback --host; always binds CONSOLE_BIND 127.0.0.1
  4. harness: full T2a-d, T3a-e scenarios added

CODEX R1 RESOLUTIONS IMPLEMENTED:
  - Ledger ordering: read tail → set rollback.prior_* → append on CLEAN
  - patch.diff: fail BLOCKED if not materialized (no placeholder)
  - budget snapshot: fail closed if envelope ledger unavailable in console-bindings mode
  - V15: requires GENESIS seed / prior ledger entry

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered blockers
```

---

## After Codex CLEAN

Update `MMI_PIPE_STAGING.json` → `console_server_step4_build: CODEX_CLEAN`

**R3 verification (TestClient hang fix — 2026-07-03):**

- Replaced Starlette `TestClient` with `httpx.AsyncClient` + `ASGITransport` (`asgi_http()` in harness)
- Route `body_field` inspection proves `Body(...)` wiring
- `test_console_server_http_via_uvicorn_subprocess` — live loopback HTTP with bounded shutdown
- Harness T2e (GET `/health`) + T2f (POST validate bad body) both PASS
- `create_app()` authority resolves from repo root / `MMI_AUTHORITY_ROOT` (not hardcoded WSL only)

**Codex re-run (CLEAN):**

```text
pytest tests/test_console_server.py -v                    → 11 passed
console_server_harness.py --evidence-dir .../harness_r2   → CLEAN ×2 (T2e/T2f PASS)
```

Closeout: `status/MMI_CONSOLE_SERVER_STEP4_CLOSEOUT_2026-07-03.md`
