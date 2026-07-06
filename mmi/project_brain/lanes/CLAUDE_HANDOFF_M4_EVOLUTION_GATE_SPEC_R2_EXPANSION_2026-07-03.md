# Claude Handoff — M4 Evolution Gate Spec R2 (Superset Expansion)

**Task id:** `mmi-m4-evolution-gate-spec-r2`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` + MESSAGE 3: `MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md`

**Trigger:** Codex plan review R1 **NOT BUILDABLE** — 9 blockers (`CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R1_2026-07-03.md`)

**Prior art to preserve:** Narrow spec + MESSAGE 2/3 remediations (V-001..V-011, STAGE_ORDER, EVIDENCE_ROOT off /tmp, OPERATOR_ATTEST, etc.) — file at `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`

**Ground truth (read or paste):** `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` v2.1

**Target output:** Full **17-section superset** replacing `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`

**Workflow (three messages — do not skip):**
1. **MESSAGE 1R** — expand to full superset + resolve all 9 Codex blockers
2. **MESSAGE 2R** — structural adversarial self-review
3. **MESSAGE 3R** — isolation & leak audit
4. Relay final spec → Cursor → Codex plan review **R2**

---

## Before you paste MESSAGE 1R

**If Claude has repo access** (`/mnt/c/MMI`): paste MESSAGE 1R only.

**If Claude has NO repo access:** also paste at the bottom of MESSAGE 1R:
- Full current spec: `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`
- Full research: `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md`

---

## MESSAGE 1R — Superset expansion (paste first)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-r2
ASSIGNEE: Claude (Design)
SCORE: 98
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — M4 evolution gate FULL spec (R2 superset expansion)
Doctrine: Bounded autonomy, deterministic rules, un-fakeable metrics, fail-closed gates
Design lane only — deliver ONE complete markdown spec file. No Python. No build auth.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/MMI

PRIOR SPEC (narrow R1 — PRESERVE all MESSAGE 2/3 remediations; expand, do not regress):
  architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
  Contains: STAGE_ORDER, EVIDENCE_ROOT off /tmp, RUN_NONCE, OPERATOR_ATTEST, H0 pre-provision seal,
  CLONE_IMAGE_DIGEST, FileId enforcement, fail-closed ARM/append, §1.5 ladder table,
  MESSAGE 2 ledger V-1..V-11, MESSAGE 3 ledger V-001..V-011, safety declaration

CODEX R1 VERDICT: NOT BUILDABLE — 9 blockers (must all be resolved in this R2 output):
  lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R1_2026-07-03.md

AUTHORITATIVE RESEARCH (normative — do not contradict):
  lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md — v2.1 adversarial revision
  lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md
  chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md — M4
  architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md — §6, §8
  architecture/MMI_AGI_EVOLUTION_PATHWAY.md — §5, §6 non-goals
  lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md
  status/MMI_PIPE_STAGING.json — evolution_gate OUTSTANDING

ORIGINAL HANDOFF (17-section target):
  lanes/CLAUDE_HANDOFF_M4_EVOLUTION_GATE_2026-07-03.md

Prereqs GATED/CLOSED — do not re-litigate:
  Phase 1, Gate B, control envelope, console Ed25519, genomic CLI v1, client email lanes v1

Built reuse:
  scripts/chaos_lab_provisioner.py, scripts/phase1_stability_harness.py,
  chaos/weapon_battlefield_scoring.py, chaos/mirror_dimension_router.py,
  chaos/mmi_control_envelope.py, chaos/metadata_ingress_gate.py
  chaos/canary_metadata_layer.py — L8 ONLY; M4 must NOT import

OUT OF SCOPE:
  central_brain step 6, genomic v2 24/7, PERFECT/M4-closed claims, build authorization
  /home/socialarchitect/northstar — forbidden path
</current_state_inventory>

<codex_r1_blockers mandatory_resolution="all nine">
BLOCKER 1 — NARROW vs SUPERSET:
  Deliver full 17 sections below. Not a narrow slice. No Footnote [A] deferral.

BLOCKER 2 — M3 MINIMUM DIAGNOSTIC SLICE (new §12 content required):
  Define: stress shape (not full 700-slot), pass criteria, evidence artifact path,
  terminal state, signed exit artifact, relationship to M3_REQUIRED_FOR_M4_ENDURANCE.
  Must gate C3/C4/M4 entry in §17 phasing.

BLOCKER 3 — FORMAL INVARIANT SUITE + FUZZ HARNESS (new §5 + §6):
  Enumerate invariants from research v2.1 §1.6 (authority never writable, production unreachable,
  secrets never cross boundary, budget monotonic, evidence complete/ordered).
  Fuzz targets: parser, FSM, ledger, canary classifier, evidence rollup, restart.
  CLI contract + pass/fail terminal + evidence output path. Must run BEFORE endurance in §17.

BLOCKER 4 — TCB BUILD PHASING (§17 required):
  stage_attestation, KEY_CUSTODY (TPM/HSM), host_boundary/mmi_boundary_daemon must appear
  as explicit build phases BEFORE C3/C4/M4 endurance. Design-only is OK in spec; phasing must be buildable.

BLOCKER 5 — V-009 TESTABLE (new §11 + falsifier):
  Define correlated-failure classification rules for C3/C4 (no diagnostic slicing of critical chains).
  Named constants, fixtures, acceptance criteria, dedicated falsifier scenario (e.g. T12 or T13).

BLOCKER 6 — CANARY TAXONOMY ≥20 IDs (§8):
  Minimum 20 distinct M4-CANARY-* IDs covering research findings §4.2 categories:
  host escape, repo integrity without direct write, evidence tamper, budget games, slow exfil.
  Include blind-spot coverage table: category → canary ID(s). Namespace mmi.m4.canary.* only.

BLOCKER 7 — FALSIFIERS T1–T12 COMPLETE (§14):
  Full table: objective, target, expected terminal, verification method.
  T10 clock manipulation, T11 budget attribution drift, T12 scoped-reset violation on M4 final —
  fully specified (not merely named). Align with research v2.1 §6 T1–T12.

BLOCKER 8 — §17 BUILD PHASING TABLE (mandatory):
  Rows: phase #, deliverable module(s), entry gate, exit gate, blocks endurance until done.
  48h runner (scripts/m4_endurance_runner.py) MUST be LAST phase.
  Phase 1 MUST NOT be 48h runner — H-rule violation if so.

BLOCKER 9 — L8 NAMESPACE ENFORCEMENT (§16 H-rules + harness spec):
  Normative import ban: M4 modules must not import chaos/canary_metadata_layer.py.
  Harness structural check (grep/import test) in §13 or §10.
  Document mmi.m4.* vs mmi.l8.* separation.
</codex_r1_blockers>

<core_doctrine>
From research v2.1 — must appear in spec §2:

Proof object = formal invariant preservation + falsifier coverage + tamper-evident evidence chain + endurance

Staged ladder (build order):
  formal invariants → fuzz harness → sandbox escape tests → C-M4 → C2 → C3 → C4 → M4 (48h LAST)

Typed M3 gates (normative constants):
  M3_REQUIRED_FOR_M4_DRY_RUN = false
  M3_REQUIRED_FOR_M4_ENDURANCE = true
  M3_REQUIRED_FOR_PERFECT_CLAIM = true

Clock-reset:
  Pre-final: scoped diagnostic reset permitted (debug only)
  M4 final: ANY critical-class failure → FULL 48h clock reset; SCOPED_RESET_ON_FINAL = false

Host boundary: Windows-native (WFP + minifilter + Go daemon); WSL-only INSUFFICIENT
EVIDENCE_ROOT: host-side, NOT under /tmp; daemon-write-only
build_authorized: FALSE always in spec runs; OPERATOR_ATTEST required (no soft boolean)
</core_doctrine>

<task_definition>
Author COMPLETE replacement spec: architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
Revision: r2 superset expansion (replaces narrow R1 filing)

REQUIRED 17 SECTIONS (minimum — merge R1 harness/boundary/canary content into appropriate sections):

  1. Purpose & scope — M4 vs step 6 vs genomic v2 vs Gate C vs L8
  2. Normative definitions — proof object, pass lines, terminal states (M4_MET | M4_NOT_MET | HARNESS_READY | CLEAN | BLOCKED | INDETERMINATE)
  3. Staged proof ladder — C-M4, C2, C3, C4, M4 with entry/exit table (preserve §1.5 from R1)
  4. Typed dependency gates — M3 constants, DAG, parallel research vs sequential proof
  5. Formal invariant suite — enumerated + verification method
  6. Deterministic fuzz harness — targets, CLI, evidence, pass/fail
  7. Modular sandbox escape tests — scope before endurance
  8. Host boundary architecture — Windows-native; preserve R1 §2 FileId/9P/raw-volume remediations
  9. M4 canary alert taxonomy — ≥20 IDs + blind-spot table; preserve fail-closed from R1
  10. AFE ledger + hostile attribution audit
  11. Tamper-evident evidence chain + V-009 correlated-failure rules for C3/C4
  12. M3 minimum diagnostic slice — FULL definition (Codex blocker 2)
  13. Harness contracts — CLI, paths, JSON schemas per stage; L8 import ban test
  14. Falsifiable scenarios T1–T12 — complete table (Codex blocker 7)
  15. Observability — explicit required vs optional (FastAPI/ws decision)
  16. Non-goals, H-rules, L8 namespace contract
  17. Build phasing table — deliverable order; 48h runner LAST (Codex blocker 8)

Also include (from R1 — do not drop):
  - Harness state machine pseudo-code or normative FSM (§3 or appendix)
  - Clock-reset LaTeX/formula (§11)
  - MESSAGE 2 adversarial ledger section (or fold into REVISION LOG)
  - MESSAGE 3 isolation ledger section (or fold into REVISION LOG)
  - Safety declaration: FAILS SECURE | FAILS INSECURE | INDETERMINATE
  - REVISION LOG: r1 narrow → r2 superset + Codex blocker resolutions
  - SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL

Schema requirements:
  - EVIDENCE_ROOT host-side only (never sibling to LAB_ROOT under /tmp)
  - STAGE_ORDER cryptographically enforced via stage_attestation signed exits
  - Each stage summary: overall_gate_status, stage_id, RUN_NONCE, chain_verified
  - Named constants for all thresholds
  - perfect_claim: false pinned in M4 summary schema
</task_definition>

<execution_constraints>
1. Output ONE complete markdown spec file only — no chat intro.
2. Resolve ALL 9 Codex R1 blockers explicitly — add § "Codex R1 resolution map" table mapping blocker # → spec §.
3. Preserve R1 MESSAGE 2/3 security remediations — expanding scope must not regress V-001..V-011 fixes.
4. Ground every normative claim in research v2.1 or cited repo paths — mark [UNVERIFIED] only if source truly unavailable.
5. Minimum 20 M4-CANARY-* IDs — grouped taxonomy OK if every findings §4.2 category mapped.
6. T1–T12 fully specified — no "T10 named only" gaps.
7. §17 must make straight-to-48h unbuildable by table structure.
8. H-rule H-L8-001: import of canary_metadata_layer.py in M4 package → BUILD FAIL.
9. Do NOT authorize build, PERFECT, or M4 closed.
10. If repo files unreadable, state in footnote and use pasted inputs below — do not invent northstar paths.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only.
Assumptions in spec footnotes — not chat prose.
</no_explanations_directive>

---

[PASTE architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md HERE IF NO REPO MOUNT]

[PASTE lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md HERE IF NO REPO MOUNT]
```

---

## MESSAGE 2R — Structural adversarial self-review (paste after MESSAGE 1R output)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-r2-review
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec revision only

<review_mode>
Act as a hostile distributed-systems architect reviewing your own R2 superset
MMI_M4_EVOLUTION_GATE_SPEC from MESSAGE 1R.

Do NOT praise the draft. Attack it.

CODEX R1 BLOCKER CHECKLIST — fail if ANY unresolved:
  [ ] 1. Full 17 sections present (not narrow slice)
  [ ] 2. M3 min slice: pass criteria + artifact + terminal state
  [ ] 3. Formal invariants + fuzz harness with CLI contract
  [ ] 4. §17 phases TCB (stage_attestation, KEY_CUSTODY, boundary daemon) before endurance
  [ ] 5. V-009: correlated-failure rules + falsifier + fixtures
  [ ] 6. ≥20 M4-CANARY-* IDs + §4.2 blind-spot table
  [ ] 7. T1–T12 complete (T10 clock, T11 budget, T12 scoped-reset violation)
  [ ] 8. §17 build phasing table; 48h runner LAST
  [ ] 9. L8 import ban enforceable (H-rule + harness check)

MANDATORY REVIEW AXES (fix inline):

1. STAGED LADDER — can implementer skip to M4 via code path or missing §17 gate?
2. HIDDEN COUPLING — M3_REQUIRED_FOR_* enforced in phasing not prose?
3. CANARY BLIND SPOTS — any findings §4.2 category without canary ID?
4. CLOCK HONESTY — scoped reset impossible on M4 final? critical vs diagnostic closed?
5. EVIDENCE & AFE — hash chain anti-backfill? hostile attribution audit specified?
6. HOST BOUNDARY — EVIDENCE_ROOT off /tmp? FileId not path-only? WSL insufficiency stated?
7. FAKE-PASS — HARNESS_READY ≠ PERFECT? INDETERMINATE ≠ CLEAN? build_authorized always FALSE?
8. R1 REGRESSION — any V-001..V-011 or V-1..V-11 remediations dropped during expansion?

Output ONE complete revised spec (architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md).
Add REVISION LOG: MESSAGE 2R adversarial pass.
Add "Codex R1 resolution map" table if missing.
SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL
No chat prose outside the spec file.
</review_mode>
```

---

## MESSAGE 3R — Isolation & leak audit (paste after MESSAGE 2R output)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-r2-isolation-audit
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec audit and revision only
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md

System Prompt Layer: [Adversarial Verification & Leak-Auditing Mode]
User Role: Principal Red-Team Auditor & Isolation Security Engineer

TASK:
Zero-trust audit of the R2 superset MMI_M4_EVOLUTION_GATE_SPEC (MESSAGE 2R output).
Scope: M4 final 48h runner AND upstream staged gates C-M4, C2, C3, C4 AND new §5/§6/§7 pre-endurance layers.

AUTHORITY REPO: C:\MMI
FORBIDDEN: /home/socialarchitect/northstar

INPUT ARCHITECTURE TO AUDIT:
[PASTE ENTIRE R2 SPEC FROM MESSAGE 2R HERE]

CRITICAL SECURITY QUESTIONS (answer all):

1. ISOLATION & FILTRATION LEAKS — WFP/minifilter/DrvFs/FileId/9P/raw-volume; evidence off /tmp?
2. TELEMETRY OVERFLOWS — can flood blind canaries or fail-open append?
3. CLOCK-RESET EXPLOIT CHAINS — survivorship laundering on M4 final? C3/C4 upstream laundering (V-009)?
4. FALSIFIER GAPS — T1–T12 sufficient? propose T13 if largest gap remains.
5. ESCAPE FROM COUPLING — L8 conflation? genomic v2? central_brain?

CODEX R1 CROSS-CHECK:
Confirm blockers 1–9 remain resolved AFTER isolation fixes.
If a fix breaks a Codex resolution, re-resolve inline.

OUTPUT FORMAT:
- Vulnerability & Gap Ledger (V-001+ for this pass — new numbering OK)
- Remediation Specification per gap
- ONE revised architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
- REVISION LOG: MESSAGE 3R isolation audit
- Codex R1 resolution map (updated if needed)
- Safety declaration: FAILS SECURE | FAILS INSECURE | INDETERMINATE
- Do NOT declare PERFECT or M4 closed
- SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL

No filler outside ledger + spec.
```

---

## After Claude — Cursor closeout checklist

- [ ] Replace `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` with R2 superset
- [ ] Verify 17 sections + Codex R1 resolution map
- [ ] Verify ≥20 canaries, T1–T12, §17 phasing, M3 slice, fuzz/invariants
- [ ] Verify R1 remediations preserved (EVIDENCE_ROOT, STAGE_ORDER, etc.)
- [ ] File `CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R2_2026-07-03.md`
- [ ] Matt → Codex R2 → BUILDABLE before any build auth

---

## Quick open (Win+R)

```text
notepad "C:\MMI\mmi\project_brain\lanes\CLAUDE_HANDOFF_M4_EVOLUTION_GATE_SPEC_R2_EXPANSION_2026-07-03.md"
```

Also attach or paste before MESSAGE 1R if no repo mount:
- `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`
- `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md`

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | R2 superset expansion handoff — resolves Codex R1 9 blockers |
