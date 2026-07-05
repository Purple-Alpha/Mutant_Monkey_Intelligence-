# Codex Handoff — M4 Evolution Gate PLAN REVIEW

**Task id:** `mmi-m4-evolution-gate`  
**Assignee:** Codex (pre-build plan review)  
**Build auth:** NOT AUTHORIZED — spec closeout only  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`  
**SIGN-OFF:** PASS WITH REVISIONS (Claude MESSAGE 2 + MESSAGE 3, 2026-07-03)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: PRE-BUILD PLAN REVIEW
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC:
  mmi/project_brain/architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
  SIGN-OFF: PASS WITH REVISIONS
  Safety: FAILS SECURE (modeled set) — not perfectly closed

AUTHORITATIVE RESEARCH (must not contradict):
  mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md (v2.1)
  mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md
  mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md
  mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md §6

CLAUDE HANDOFF (superset target):
  mmi/project_brain/lanes/CLAUDE_HANDOFF_M4_EVOLUTION_GATE_2026-07-03.md (17 sections, ≥20 canaries, T1–T12, build phasing §17)

CURSOR CLOSEOUT:
  mmi/project_brain/lanes/MMI_M4_EVOLUTION_GATE_SPEC_CLOSEOUT_2026-07-03.md

UPSTREAM GATED (reuse — do not re-litigate):
  Phase 1 stability, Gate B, control envelope, console Ed25519, genomic CLI v1, client email lanes v1
  scripts/chaos_lab_provisioner.py, chaos/mmi_control_envelope.py, chaos/weapon_battlefield_scoring.py

NOT BUILT (spec-defined [NEW]):
  scripts/m4_endurance_runner.py, host_boundary/mmi_boundary_daemon, stage_attestation, M4 canary engine
  formal invariant suite, fuzz harness, Gate C-M4→C4 ladder runners

v1 POSTURE (must hold in build plan):
  evolution_gate OUTSTANDING — no PERFECT, no M4 closed
  48h runner LAST — not first deliverable
  EVIDENCE_ROOT off /tmp, host-side daemon-write-only
  M4 final: full clock reset on critical-class failure
  build_authorized == FALSE always in spec runs

REVIEW FOCUS — scope + fail-closed (fail until resolved):

(A) NARROW vs SUPERSET: Claude filed Sections 0–6 only; handoff requires 17 sections, ≥20 canary IDs, T1–T12, §17 build phasing. Is partial spec BUILDABLE?

(B) M3 minimum diagnostic slice — referenced but undefined

(C) Formal invariant + fuzz harness — research v2.1 requires before endurance; not in spec body

(D) stage_attestation + KEY_CUSTODY + boundary daemon — fail-secure claim depends on unbuilt TCB

(E) Cross-stage laundering guard (V-009) — testable in build plan?

(F) Canary taxonomy — 6 rules vs findings §4.2 expansion requirement

(G) No L8 canary_metadata_layer conflation — verify build plan keeps namespaces separate

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered blockers

Do NOT authorize build. Do NOT claim PERFECT or M4 closed.
```

---

## Expected verdict

**Likely NOT BUILDABLE** until superset expansion or explicit Matt narrow-slice build authorization per closeout scope table.

---

## After Codex

| Verdict | Next |
|---------|------|
| BUILDABLE | Matt: `authorize build M4 evolution gate` → Cursor staged ladder first |
| NOT BUILDABLE | Claude expand spec OR Matt scope decision → re-review |
