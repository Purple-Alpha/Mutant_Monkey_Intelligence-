# Codex Handoff — Console Server Ed25519 Evidence Gate PLAN REVIEW

**Task id:** `mmi-console-server-ed25519-evidence-gate-build`  
**Assignee:** Codex (pre-build plan review)  
**Build auth:** NOT_AUTHORIZED — plan review only until BUILDABLE + Matt `authorize build`  
**Spec:** `architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md` (r2, SIGN-OFF PASS WITH REVISIONS)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-console-server-ed25519-evidence-gate-build
REVIEW TYPE: PRE-BUILD PLAN REVIEW (not diff review)
ASSIGNEE: Codex
BUILD AUTHORIZATION: NOT_AUTHORIZED
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC (authoritative):
  mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md
  SIGN-OFF: PASS WITH REVISIONS (r2)

IMPLEMENTATION TARGETS (if BUILDABLE):
  1. scripts/console_server.py — NEW (FastAPI, verify-only Ed25519, 127.0.0.1:8767)
  2. scripts/console_server_harness.py — NEW (T1, T2a–d, T3a–e, H4/H6/H8/H10)
  3. tests/test_console_server.py — pytest for validate/sign rules + adapter stubs
  4. chaos/console_ack_adapter.py (or equivalent) — ConsoleAckAdapter per §5.2
  5. Minimal bundle-builder CLI or harness helper (operator step before POST /validate)

PREREQS CLOSED:
  - Phase 1 PASS (3× Tier 4)
  - Gate B proof_gate_harness BUILT + Codex CLEAN
  - Control envelope budget/dead-man BUILT + Codex CLEAN
  - Do NOT re-litigate steps 1–3

PATTERN SOURCES (mirror, do not replace):
  - scripts/kinetic_war_room_server.py — FastAPI loopback bind (port 8765; console uses 8767)
  - chaos/metadata_ingress_gate.py — Ed25519 verify idiom (verify-only server)
  - scripts/proof_gate_harness.py — harness summary + exit-code gate pattern
  - scripts/control_envelope_harness.py — T1–T3 scenario structure

HARD STOPS:
  - console_server.py MUST NOT import Ed25519PrivateKey or any signing primitive (H10)
  - All writes under /tmp/mmi_console_server/ only — authority repo read-only (H4)
  - No promote/apply in console process (H5)
  - Signature over canonical manifest bytes, not hash string (§4.2, S4)
  - Separate process from kinetic_war_room_server — no shared sign state
  - Telemetry/AFE fields denylisted from bundle/manifest (H9)

OPEN RESIDUALS (Codex must resolve or block):
  1. FINGERPRINT_LEDGER_PATH (V15) — spec says control-envelope known-good capture writes it; path does NOT exist in mmi_control_envelope.py today. Plan must define who writes ledger entries and when (proof_gate fp_before digest? human_advance_ack path?).
  2. V13 digest extraction — Gate B proof_of_fix is a nested dict object, not a flat digest field. Plan must define canonical digest of proof_of_fix / proof_of_regression for cross-binding.
  3. V7 patch_hash — Gate B summary has authority_hash / authority_fingerprint_after_digest but no explicit patch_hash field today. Plan must define patch file location + hash source (patch_context? separate artifact?).
  4. V10 run_id — proof_gate_summary has no run_id field today. Plan must define run_id derivation or spec amendment.
  5. V9 rollback lineage — footnote 5 ties rollback_token to prior known-good fingerprint; Gate B only snapshots fp_before via authority_hash. Plan must define chain lookup or fail-closed default.
  6. Gate B timestamp is ISO string; V14 uses GATE_B_MAX_AGE_MS on integer ms — plan must define parse rule.

REQUIRED OUTPUT:
  Verdict: BUILDABLE | NOT BUILDABLE
  If NOT BUILDABLE: numbered blockers with spec section references + proposed spec patches
  If BUILDABLE: ordered implementation checklist (files, methods, tests, harness CLI, digest canonicalization rules)
  Do not write code — plan review only
```

---

## After Codex returns BUILDABLE

Matt → `authorize build` → Cursor implements → Codex diff review packet (separate handoff after code lands).
