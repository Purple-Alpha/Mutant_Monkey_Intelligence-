# Claude Handoff — M4 Evolution Gate Spec

**Task id:** `mmi-m4-evolution-gate-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` + MESSAGE 3: `lanes/MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md`

**Evidence basis:** Research v2.1 adversarial findings filed 2026-07-03. AGI §5 steps 1–5 + client email lanes **GATED**. Evolution gate **OUTSTANDING**. Straight-to-48h **REJECTED** — spec must define staged proof ladder first.

**Prerequisite auth (Matt):** `authorize spec M4 evolution gate`

**Workflow (three messages — do not skip):**
1. Paste **MESSAGE 1** into a fresh Claude window — generate spec.
2. Paste **MESSAGE 2** after draft — structural adversarial self-review.
3. Paste **MESSAGE 3** after MESSAGE 2 output — isolation & leak audit (Vulnerability Ledger).
4. Relay **final revised spec** to Cursor for filing.

**Target spec path:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`

**After Claude:** Cursor closeout → `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_2026-07-03.md` → Codex BUILDABLE → Matt `authorize build M4 evolution gate` (staged — not 48h-first).

---

## MESSAGE 1 — Generate spec (paste this first)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec
ASSIGNEE: Claude (Design)
SCORE: 96
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — evolution gate / PERFECT-tier proof architecture
Doctrine: Bounded autonomy, deterministic rules over soft prompts, un-fakeable metrics, fail-closed gates
Design lane only — deliver one bounded markdown spec. No implementation. No scope expansion.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/Architectapp_clean

AUTHORITATIVE RESEARCH (normative for this spec — do not contradict):
  mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md — v2.1 adversarial revision
  mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md — research brief
  mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md — Milestone 4 / component map
  mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md — §6 evolution links, §8 worksheet
  mmi/project_brain/architecture/MMI_AGI_EVOLUTION_PATHWAY.md — §3 Phase 3, §5 build order, §6 non-goals
  mmi/project_brain/status/MMI_PIPE_STAGING.json — evolution_gate OUTSTANDING
  mmi/project_brain/lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md — WSL/Windows boundary reality

Prereqs CLOSED or GATED (do not re-litigate):
  - Phase 1 stability: PASS tiers [4,4,4] — status/MMI_PHASE1_STABILITY_PASS_2026-07-02.md
  - Gate B proof gate: BUILT + Codex CLEAN — scripts/proof_gate_harness.py
  - Control envelope step 3: BUILT + Codex CLEAN — chaos/mmi_control_envelope.py
  - Console Ed25519 step 4: CLOSED — scripts/console_server.py, chaos/console_evidence_gate.py
  - Genomic realignment loop CLI v1 step 5: GATED — ops/genomic_realignment_loop/
  - Client email lanes v1: GATED — ops/client_email_lanes/

Built chaos / lab primitives (reuse patterns):
  - scripts/chaos_lab_provisioner.py — isolated clone provisioning (FILED)
  - scripts/phase1_stability_harness.py — 3× Tier 4 stability
  - chaos/weapon_battlefield_scoring.py — generate_proof_bundle(), tiers, MISSED ledger
  - chaos/mirror_dimension_router.py — M2 mirror route (FILED)
  - chaos/canary_metadata_layer.py — L8 ingress honeytoken ONLY — NOT M4 canary rules
  - chaos/mmi_control_envelope.py — HALT/SUSPEND, budget, dead-man
  - chaos/metadata_ingress_gate.py — fail-closed gate pattern

NOT BUILT (target of this spec — staged, NOT 48h-first):
  - M4 evolution gate harness ladder (Gate C-M4 → C2 → C3 → C4 → M4 final)
  - M4 canary alert rules taxonomy (distinct from L8)
  - Host boundary Windows-native daemon (Go/WFP/ACL)
  - Formal invariant suite + deterministic fuzz harness
  - Tamper-evident evidence hash chain for endurance runs
  - AFE ledger with hostile attribution audit
  - M3 minimum diagnostic slice definition

OUT OF SCOPE (explicit non-goals):
  - AGI §5 step 6 central_brain.py — separate lane, NOT SPEC'D
  - Genomic v2 24/7 autonomous loop — DEFERRED post-M4
  - Claiming PERFECT tier achieved or M4 closed in this spec
  - Client email Response Lane ON as evolution authority
  - Unbounded self-modification or autonomous gate promotion
</current_state_inventory>

<core_doctrine>
M4 is the PERFECT-tier evolution proof — a 48-hour continuous un-throttled assault inside the chaos clone —
but 48h is the FINAL endurance ceremony, NOT the first engineering deliverable.

Proof object (v2.1 — must appear in spec §1):
  formal invariant preservation
  + reproducible falsifier coverage
  + tamper-evident evidence chain
  + endurance under sustained hostile pressure

Staged proof ladder (mandatory build order in spec):
  formal invariants
  → deterministic fault/fuzz harness
  → modular sandbox escape tests
  → Gate C-M4 dry-run (15–60 min) — harness readiness ONLY
  → Gate C2 (4h adversarial replay)
  → Gate C3 (12h overnight clone assault)
  → Gate C4 (24h soak)
  → M4 (48h final endurance proof)

Typed M3 gates (must be normative constants in spec):
  M3_REQUIRED_FOR_M4_DRY_RUN = false
  M3_REQUIRED_FOR_M4_ENDURANCE = true  (minimum diagnostic slice before C3/C4/M4)
  M3_REQUIRED_FOR_PERFECT_CLAIM = true (full mesh proof before PERFECT declaration)

Clock-reset policy (mandatory):
  - Pre-M4 dry runs (C-M4, C2, C3, C4): scoped reset permitted for debugging only
  - M4 final 48h PERFECT claim: ANY critical-class failure resets FULL 48-hour clock
  - Scoped reset on final claim is FORBIDDEN (survivorship laundering)

Host boundary (mandatory scope decision):
  - Windows-native control plane (WFP, ACLs/minifilter on C:\Architectapp_clean)
  - WSL-only boundary INSUFFICIENT for M4 endurance gates
  - 48h assault before host boundary = tests imaginary perimeter — FORBIDDEN

M4 canary rules vs L8:
  - chaos/canary_metadata_layer.py is metadata iceberg L8 — do NOT conflate
  - M4 canary taxonomy must expand beyond coarse M4-CANARY-001..006 cartoon rules
  - Cover blind spots from findings §4.2: host escape, repo integrity without direct writes,
    evidence tampering, budget attribution games, slow-path exfiltration
</core_doctrine>

<existing_implementation_pattern>
Gate B / proof bundle pattern (weapon_battlefield_scoring.py):
  - overall_gate_status: CLEAN | BLOCKED — binary terminal
  - atomic JSON write to evidence_dir outside authority repo (/tmp/mmi_chaos_lab/...)
  - authority fingerprint digest; MISSED ledger published uncut

Control envelope pattern (mmi_control_envelope.py):
  - Fail-closed HALT/SUSPEND; no self-ack
  - Monotonic budget; sticky latch

Phase 1 harness pattern:
  - 3 independent runs; PASS only if all Tier 4, spread 0
  - scripts/phase1_stability_harness.py

Chaos lab provisioner:
  - scripts/chaos_lab_provisioner.py — clone isolation; lab-id under /tmp/mmi_chaos_lab/

Weapon worksheet (matrix §8):
  - Axis A containment + Axis B field discipline → overall tier min(A,B)
  - Evolution gate line: GOOD / GREAT candidate / OUTSTANDING candidate — distinct from M4 PERFECT
</existing_implementation_pattern>

<task_definition>
Author greenfield spec: architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md

Required sections (minimum):
  1. Purpose & scope — M4 vs AGI step 6 vs genomic v2 vs Gate C vs L8 canary
  2. Normative definitions — proof object, pass lines, terminal states (M4_MET | M4_NOT_MET | HARNESS_READY)
  3. Staged proof ladder — Gate C-M4, C2, C3, C4, M4 final with entry/exit criteria per stage
  4. Typed dependency gates — M3 constants §2.1; build order DAG; parallel research vs sequential proof
  5. Formal invariant suite — enumerated invariants + verification method (pre-chaos)
  6. Deterministic fuzz harness — targets: parser, FSM, ledger, canary classifier, evidence rollup, restart
  7. Host boundary architecture — Windows-native daemon scope, WSL clone venue, DrvFs limits
  8. M4 canary alert taxonomy — closed enum expanded beyond 001–006; signal IDs; fail-closed actions;
     blind-spot coverage table mapping findings §4.2 categories to canary IDs
  9. AFE ledger + hostile attribution audit — monotonic burn, replenishment rules, drift detection
  10. Tamper-evident evidence chain — append-only JSONL, hash chain, interval IDs, anti-backfill rules
  11. Clock-reset policy — critical-class vs diagnostic-class; full reset on M4 final
  12. M3 minimum diagnostic slice — what must pass before C3/C4/M4 (not full 700-slot if over-scoped)
  13. Harness contracts — CLI entrypoints, evidence paths, summary JSON schemas per stage
  14. Falsifiable scenarios T1–T12 minimum (include evidence tampering, toolchain poisoning, scoped-reset violation)
  15. Observability — operator visibility requirements (FastAPI/ws optional vs required — decide explicitly)
  16. Non-goals & deferred items
  17. Build phasing table — which deliverables Cursor builds in which order (48h runner LAST)
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL

Schema requirements:
  - Each stage emits summary with overall_gate_status and stage_id
  - M4 final summary: m4_48h_summary.json fields documented
  - Evidence outside authority repo only (/tmp/mmi_chaos_lab/ or /tmp/mmi_m4_evidence/)
  - Named constants for all thresholds — no magic numbers without identifiers
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. First build phase MUST NOT be 48h runner — spec must enforce staged ladder §17.
4. Reject straight-to-48h as valid implementation plan — mark as H-rule violation.
5. Expand canary taxonomy beyond 6 cartoon rules — minimum 20 distinct M4-CANARY-* IDs or equivalent grouped taxonomy with no orphan blind spots from findings §4.2.
6. Host boundary must be Windows-native — document WSL insufficiency explicitly.
7. Gate C-M4 dry-run claims HARNESS_READY only — forbid PERFECT/M4-closed language at that stage.
8. Do not merge genomic v2 24/7 loop into M4 gate.
9. Do not authorize autonomous promotion from any endurance run result.
10. Reference built files by repo path — do not invent modules that do not exist unless spec defines them as new.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only. Assumptions go in spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## MESSAGE 2 — Adversarial self-review (paste after MESSAGE 1 output)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-review
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec revision only

<review_mode>
Act as a hostile distributed-systems architect and red-team auditor reviewing your own
MMI_M4_EVOLUTION_GATE_SPEC draft from MESSAGE 1.

Do NOT praise the draft. Attack it.

Mandatory review axes (fix every finding inline in the revised spec):

1. STAGED LADDER INTEGRITY
   - Does any section still imply 48h runner as first deliverable?
   - Can a careless implementer skip invariants/fuzz/host-boundary and jump to M4?
   - Are entry/exit criteria for C-M4, C2, C3, C4, M4 fail-closed and testable?

2. HIDDEN COUPLING
   - Are M3_REQUIRED_FOR_* gates enforced in build phasing, not just prose?
   - Does parallel proof remain impossible by spec structure?
   - Can a failed 48h run still be diagnosed (variable isolation)?

3. CANARY BLIND SPOTS
   - Does taxonomy cover findings §4.2 categories without hand-waving?
   - Any host escape, repo-integrity-without-write, evidence tampering, budget game, slow exfil gap?
   - Is L8 canary_metadata_layer conflation explicitly blocked?

4. CLOCK HONESTY
   - Is scoped reset on M4 final explicitly forbidden?
   - Is critical-class vs diagnostic-class defined without loopholes?
   - Can engineers classify correlated multi-hour chains as scoped to save a run?

5. EVIDENCE & AFE
   - Is hash chain tamper detection specified (not just append-only prose)?
   - Is budget depletion meaningless without hostile attribution audit — is audit specified?
   - Can evidence be backfilled after failure?

6. HOST BOUNDARY
   - Is Windows-native requirement enforceable, not advisory?
   - Does spec forbid M4 endurance before boundary daemon minimum viable slice?

7. FAKE-PASS PATHS
   - Can overall_gate_status be CLEAN with missing canary, partial evidence, or authority touch?
   - Can HARNESS_READY at C-M4 be mistaken for PERFECT?
   - Any soft prompt or operator discretion bypass?

8. NON-GOALS
   - genomic v2 24/7, central_brain, PERFECT claim, M4 closed — all blocked?

Output ONE complete revised spec file only (architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md).
Include REVISION LOG section documenting material fixes from self-review.
SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL
No chat prose outside the spec file.
</review_mode>
```

---

## MESSAGE 3 — Isolation & leak audit (paste after MESSAGE 2 output)

**Canonical template:** `lanes/MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md` §2

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-isolation-audit
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec audit and revision only

System Prompt Layer: [Adversarial Verification & Leak-Auditing Mode]
User Role: Principal Red-Team Auditor & Isolation Security Engineer

TASK:
Conduct a rigorous, zero-trust audit of the M4 Evolution Gate engineering specifications you generated in the previous step. You must actively search for architectural vulnerabilities, escape vectors, logic flaws, or metadata leaks that would compromise the isolation guarantees of the 48-hour chaos clone runner AND all upstream staged gates (C-M4, C2, C3, C4).

AUTHORITY REPO: C:\Architectapp_clean
FORBIDDEN PATH CITATIONS: /home/socialarchitect/northstar (unless explicitly marked invalid)

INPUT ARCHITECTURE TO AUDIT:
[PASTE THE ENTIRE MMI_M4_EVOLUTION_GATE_SPEC FROM MESSAGE 2 HERE]

CRITICAL SECURITY QUESTIONS TO ANSWER (No fluff, high density):

1. ISOLATION & FILTRATION LEAKS
Inspect the Host Boundary WFP/Go daemon specification. Is there any race condition,
unhandled sub-process escape, symlink manipulation, or DrvFs fallback vector where a
compromised chaos clone could read or touch the authority repo (C:\Architectapp_clean)?
Identify the exact section or logic block that could fail under extreme pressure.

2. TELEMETRY & SIDE-CHANNEL OVERFLOWS
Look at the 48h harness state machine and upstream stage runners. If an exploit causes
a massive logging loop or telemetry/evidence buffer overflow during an assault interval,
can it blind M4 canary alert rules or cause the runner to fail-open?

3. CLOCK-RESET EXPLOIT CHAINS
Critically evaluate the clock-reset honesty policy and any elapsed-time / interval state
formulas. Is there a mathematical loophole or unhandled edge case where state-transition
delay, clock skew, hang conditions, or scoped diagnostic classification could trick the
harness into tracking a failed interval as pass or avoiding a full T_elapsed reset on M4 final?

4. FALSIFIER GAP ANALYSIS (T1–T12+)
Look closely at all declared falsifier scenarios. What vector is completely missing?
(e.g. memory injection into the runner daemon, credential harvesting from environment,
toolchain poisoning, evidence backfill, slow-path exfiltration)
Propose at least one new falsifier (e.g. T13) that closes the largest remaining blind spot.

5. ESCAPE FROM COUPLING
Does any part of this design inadvertently reference, rely on, or import metadata schemas
from the L8 canary layer or the forbidden /home/socialarchitect/northstar directory?
Is M4 canary taxonomy kept distinct from chaos/canary_metadata_layer.py?
Check for implicit dependencies on genomic v2 24/7 or central_brain.

OUTPUT FORMAT REQUIREMENTS:
- Vulnerability & Gap Ledger (V-001+)
- For each gap: exact Remediation Specification (normative spec text to add or change)
- Apply remediations → output ONE revised architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
- REVISION LOG entry: MESSAGE 3 isolation audit
- Safety declaration: FAILS SECURE | FAILS INSECURE | INDETERMINATE (conditions listed)
- Do NOT declare the system "perfectly closed" or PERFECT tier achieved
- SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL

No conversational filler outside the ledger and spec revisions.

---

[PASTE ENTIRE SPEC HERE]
```

---

## Closeout checklist (Cursor PM — after Matt relays design)

- [ ] Spec path: `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`
- [ ] MESSAGE 3 isolation audit completed — Vulnerability Ledger addressed
- [ ] Safety declaration present (not "perfectly closed")
- [ ] Staged ladder present — 48h runner LAST in build phasing
- [ ] Typed M3 gates normative (dry-run / endurance / PERFECT)
- [ ] Full 48h clock reset on M4 final; scoped reset dry-run only
- [ ] M4 canary taxonomy expanded; L8 conflation blocked
- [ ] Host boundary Windows-native; WSL-only rejected for endurance
- [ ] Tamper-evident evidence chain + AFE hostile audit specified
- [ ] T1–T12+ falsifiers with terminal states
- [ ] Non-goals: no PERFECT claim, no genomic v2, no central_brain merge
- [ ] Codex plan review handoff filed
- [ ] Does NOT authorize build or claim M4 closed

**After Codex BUILDABLE:** Matt `authorize build M4 evolution gate` → Cursor implements **staged ladder first** → Codex diff review per phase.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | Spec handoff from research v2.1 adversarial findings |
| 1.1 | 2026-07-03 | MESSAGE 3 isolation audit — adversarial spec verification framework |
