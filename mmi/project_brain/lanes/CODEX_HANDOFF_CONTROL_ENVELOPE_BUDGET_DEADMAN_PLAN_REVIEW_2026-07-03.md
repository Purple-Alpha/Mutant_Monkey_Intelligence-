# Codex Handoff — Control Envelope Budget + Dead-Man PLAN REVIEW

**Task id:** `mmi-control-envelope-budget-deadman-build`  
**Assignee:** Codex (pre-build plan review)  
**Build auth:** NOT_AUTHORIZED — plan review only until BUILDABLE + Matt `authorize build`  
**Spec:** `architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md` (REV A, SIGN-OFF PASS WITH REVISIONS)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-control-envelope-budget-deadman-build
REVIEW TYPE: PRE-BUILD PLAN REVIEW (not diff review)
ASSIGNEE: Codex
BUILD AUTHORIZATION: NOT_AUTHORIZED
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC (authoritative):
  mmi/project_brain/architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md
  SIGN-OFF: PASS WITH REVISIONS (REV A)

IMPLEMENTATION TARGETS (if BUILDABLE):
  1. mmi/project_brain/chaos/mmi_control_envelope.py — EXTEND (additive; preserve v0 enforce_boundary)
  2. scripts/control_envelope_harness.py — NEW (mirror proof_gate_harness.py pattern)
  3. tests for T1–T3 scenarios (pytest)

CURSOR PM VERIFICATION (residual #2 closed):
  - v0 signature verified against source
  - metadata_ingress_gate.py: docstring only, no runtime import

OPEN RESIDUALS (do not fake-close):
  - Root-level consistent state forge → host boundary (non-goal)
  - Ack file permission isolation from loop identity (deployment prerequisite [^2])
  - Cap figures: DEFAULT_PER_HOUR_CAP=500000, DEFAULT_PER_DAY_CAP=5000000 — pending Matt economic sign-off

PREREQS CLOSED:
  - Phase 1 PASS (3× Tier 4)
  - Gate B proof_gate_harness BUILT + Codex CLEAN
  - Do NOT re-litigate Gate B

HARD STOPS:
  - Do not modify enforce_boundary() behavior
  - Do not read kinetic_telemetry.py for enforcement
  - Evidence/state only under /tmp/mmi_control_envelope/
  - record_heartbeat() must NOT accept ack argument
  - pre_iteration_gate honors STOP_LATCH first
  - Production must ignore caller-supplied now_ms

REQUIRED OUTPUT:
  Verdict: BUILDABLE | NOT BUILDABLE
  If NOT BUILDABLE: numbered blockers with spec section references
  If BUILDABLE: ordered implementation checklist (files, methods, tests, harness CLI)
  Do not write code — plan review only
```

---

## After Codex returns BUILDABLE

Matt → `authorize build` → Cursor implements → Codex diff review packet (separate handoff after code lands).
