# Codex Handoff — Client Email Lanes PLAN REVIEW

**Task id:** `mmi-client-email-lanes`  
**Assignee:** Codex (pre-build plan review)  
**Build auth:** NOT AUTHORIZED — spec closeout only  
**Spec:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` (r1, PASS WITH REVISIONS)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-client-email-lanes
REVIEW TYPE: PRE-BUILD PLAN REVIEW
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/MMI

SPEC:
  mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md (r1)
  SIGN-OFF: PASS WITH REVISIONS (Claude Design, 2026-07-03)

AUTHORITATIVE HANDOFF:
  mmi/project_brain/lanes/MMI_EMAIL_DRAFTING_RESPONSE_CONTAINMENT_HANDOFF_2026-07-03.md

UPSTREAM (BUILT + CLEAN — reuse patterns, do not re-litigate):
  AGI §5 step 2: proof_gate_harness, console bindings r2
  AGI §5 step 3: mmi_control_envelope.py — fail-closed HALT/SUSPEND
  AGI §5 step 4: console_server Ed25519 gate — H5 re-verify, consume-once
  chaos/action_integrity_gate.py — bounded schema validation pattern

PARALLEL (NOT email build auth):
  Genomic loop step 5: BUILDABLE — Matt has NOT authorized step 5 build

TARGET BUILD (NOT BUILT — await BUILDABLE):
  chaos/email_lanes_policy_engine.py (or equivalent — Policy Engine module)
  chaos/email_lanes_orchestrator.py (proposer only)
  scripts/email_lanes_harness.py — T1–T7 + structural H checks

v1 DEFAULT POSTURE (must hold in build plan):
  Drafting ON, Response OFF, AUTONOMOUS_SEND DISABLED, no mailbox mutation

REVIEW FOCUS — r1 open items (fail-closed until specified):
  (a) VERIFIED out-of-band promotion surface (spec footnote 3)
  (b) TENANT QUARANTINE → GLOBAL_EMERGENCY_HALT escalation constants (H14)
  (c) Versioned region-aware canonical normalizer (H7 / footnote 5)

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered blockers
```

---

## Closeout notes (Cursor PM)

| Item | Status |
|------|--------|
| Spec filed | `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` r1 |
| SIGN-OFF | PASS WITH REVISIONS |
| H-rules | H1–H20 |
| Scenarios | T1–T7 |
| Harness name | `scripts/email_lanes_harness.py` (per spec) |

**After Codex BUILDABLE:** Matt `authorize build client email lanes v1` → Cursor implementation → Codex diff review.

**Parallel:** Genomic loop remains independent BUILDABLE gate.

---

## Codex verdict (2026-07-03 R1)

**NOT BUILDABLE**

| # | Blocker | Resolution required |
|---|---------|---------------------|
| 1 | VERIFIED promotion surface unspecified | Confirmation event schema, writer, signature/log, storage path, verifier, API — H2 needs falsifiable valid path |
| 2 | H14 escalation policy-only | Named constants: severity classes, count/window thresholds, control-plane compromise criteria — T7(b) must be falsifiable |
| 3 | H7 normalizer not pinned | `NORMALIZER_VERSION`, supported regions/fields, canonicalization rules, rejection rules |

**R2 handoff:** `lanes/CLAUDE_HANDOFF_CLIENT_EMAIL_LANES_SPEC_R2_2026-07-03.md`
