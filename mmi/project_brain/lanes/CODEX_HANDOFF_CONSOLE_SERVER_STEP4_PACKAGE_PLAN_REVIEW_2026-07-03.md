# Codex Handoff — Console Server Step 4 Package PLAN REVIEW (r2)

**Task id:** `mmi-console-server-step4-package`  
**Assignee:** Codex (pre-build plan review — re-review after NOT BUILDABLE)  
**Build auth:** NOT_AUTHORIZED  
**Prior verdict:** NOT BUILDABLE (6 blockers) — resolved in spec r3 + bindings r1

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-console-server-step4-package
REVIEW TYPE: PRE-BUILD PLAN REVIEW (re-review after NOT BUILDABLE)
ASSIGNEE: Codex
BUILD AUTHORIZATION: NOT_AUTHORIZED
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPECS (authoritative — both required):
  1. mmi/project_brain/architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md (r1)
  2. mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md (r3)

PRIOR NOT BUILDABLE BLOCKERS — RESOLUTION STATUS:
  1. V7 patch_hash — bindings §3.2 patch object + V7 triple-bind in console r3
  2. V13 proof digests — bindings §3.3 canonical_object_digest fields
  3. V10 run_id — bindings §3.1 + §3.5 budget snapshot
  4. V15 ledger writer — bindings §4 console_fingerprint_ledger.py
  5. V9 rollback lineage — bindings §3.4 rollback object + GENESIS seed
  6. V14 timestamp — bindings §3.1 timestamp_ms authoritative integer

IMPLEMENTATION PACKAGE (if BUILDABLE):
  BINDINGS (prerequisite):
    - chaos/mmi_canonical_digest.py — NEW
    - chaos/console_fingerprint_ledger.py — NEW
    - scripts/console_fingerprint_seed.py — NEW
    - scripts/proof_gate_harness.py — EXTEND (--console-bindings, v2 summary)
    - tests/test_proof_gate_console_bindings.py — NEW
  CONSOLE:
    - scripts/console_server.py — NEW
    - scripts/console_server_harness.py — NEW
    - chaos/console_ack_adapter.py — NEW (§5.2)
    - tests/test_console_server.py — NEW

PREREQS CLOSED: Phase 1 PASS, Gate B CLEAN, control envelope CLEAN
HARD STOPS: unchanged from prior handoff (H4, H5, H6, H9, H10, verify-only, separate from kinetic)

REQUIRED OUTPUT:
  Verdict: BUILDABLE | NOT BUILDABLE
  If BUILDABLE: ordered checklist — bindings first, then console; note any remaining ambiguities
  If NOT BUILDABLE: numbered blockers with spec section refs
  Do not write code
```

---

## After BUILDABLE

Matt: `authorize build step4 package` → Cursor implements bindings then console → Codex diff review.
