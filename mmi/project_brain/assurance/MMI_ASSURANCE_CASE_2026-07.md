# MMI Assurance Case — M4 Evolution Gate

**Status:** LIVING DOCUMENT — Phase 1.5 scaffold  
**Date opened:** 2026-07-04  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17  
**Companion controls (hard layer, 2026-07-04):**
- `MMI_ASSURANCE_GATE_INVALIDATION_ADDENDUM_2026-07.md` (r2 — deterministic outcomes; authoritative for gate closure)
- `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`
- `MMI_REVIEWER_FAILURE_MODEL_2026-07.md`
- `MMI_OPERATOR_SIGNING_THREAT_MODEL_2026-07.md`
- `MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md`
- `MMI_RECOVERY_PROOF_REQUIREMENTS_2026-07.md`
- `MMI_CANARY_BYPASS_ACCEPTANCE_STANDARD_2026-07.md`

**Research:** `RESEARCH_MMI_ASSURANCE_MATURITY_2026-07.md`, `RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md`  
**Companion:** `MMI_RESIDUAL_RISK_LEDGER_2026-07.md`

**Purpose:** Prevent false claims about what each M4 build phase proves.  
**Maturity language:** M4 is **containment-targeting** until `M4_MET` evidence exists — never **containment-proven** from partial phases.

**Phase posture (2026-07-04):** Phases 0–3 Codex CLEAN. Phase 4 **BUILD AUTHORIZED** (Matt 2026-07-04); Codex plan BUILDABLE; build sub-phase **4A** next. No `M4_MET`, `PERFECT`, or GATED claim.

**Claims forbidden using this file alone:** M4_MET, M4 closed, PERFECT tier, containment proven / containment-proven, GATED.

---

## How to read this file

Each §17 phase has one assurance row. A phase **build exit** (Codex CLEAN, gate PASS) updates **Exit status** here. Passing a phase **does not** remove residual risks — those move to the residual-risk ledger until a later phase addresses them.

**Update rule:** When a phase completes, Cursor updates the row + ledger. Codex diff review confirms build; this file confirms **claim scope**.

---

## Phase 1.5 — Assurance case scaffold

| Field | Value |
|-------|-------|
| **Phase** | 1.5 (assurance wrapper — not in §17 build table) |
| **Claim** | M4 ladder phases have explicit Claim/Evidence/Falsifier/Residual-risk rows before endurance work begins; no phase may be oversold. |
| **Evidence artifact** | This file + `MMI_RESIDUAL_RISK_LEDGER_2026-07.md` + `RESEARCH_MMI_ASSURANCE_MATURITY_2026-07.md` |
| **Falsifier** | Any agent claims Phase N proves properties listed only in Phase N+M residual risk without ledger update. |
| **Required negative test** | N/A (doc artifact) |
| **Residual risk after pass** | Assurance rows can drift from code if not updated per phase; does not substitute for build gates. |
| **Authority dependency** | Matt auth 2026-07-04 |
| **Exit status** | **COMPLETE** (scaffold filed 2026-07-04) |

---

## Phase 0 — L8 import ban (H-L8-001)

| Field | Value |
|-------|-------|
| **Phase** | 0 |
| **Claim** | `mmi/m4/*` has zero static coupling to `canary_metadata_layer` / forbidden L8 namespace — M4 package cannot import chaos L8 metadata at build time. |
| **Evidence artifact** | `mmi/m4/import_ban.py`, `scripts/m4_import_ban_test.py`, `tests/test_m4_import_ban.py`, CI gate output |
| **Falsifier** | Any string literal, import, or aliased dynamic import referencing `canary_metadata_layer` in `mmi/m4/*.py` (except checker exempt paths). |
| **Required negative test** | Split-line `importlib.import_module(LAYER)` bypass fixture; aliased string literal fixture |
| **Residual risk after pass** | Does not prove runtime import injection, sandbox escape, host boundary, invariants under assault, or endurance. |
| **Authority dependency** | Matt Phase 0 auth; Codex diff review |
| **Exit status** | **COMPLETE** — Codex CLEAN 2026-07-04 |

---

## Phase 1 — Static invariant suite (INV-1..7)

| Field | Value |
|-------|-------|
| **Phase** | 1 |
| **Claim** | M4 source files (`mmi/m4/*`, `scripts/m4_*.py`) pass static structural checks for INV-1..7: no authority write paths (incl. multi-line/alias taint), no prod endpoint hints, no secret patterns, no budget bypass hints, no forbidden evidence paths, no promotion bypass patterns, ladder structural prerequisites. |
| **Evidence artifact** | `mmi/m4/invariants.py`, `scripts/m4_invariant_check.py`, `tests/test_m4_invariant_check.py`, static gate JSON |
| **Falsifier** | Multi-line `AUTHORITY_ROOT → alias → write_text()` passes INV-1; module-scope alias taint into function write passes INV-1; `BUILD_AUTHORIZED = True` passes INV-6; `/tmp/mmi_evidence` passes INV-5. |
| **Required negative test** | `test_inv1_fails_multiline_indirect_authority_write`; `test_inv1_fails_module_scope_indirect_write_via_alias`; `test_inv5_fails_on_tmp_evidence_root`; `test_inv6_fails_on_build_authorized_true` |
| **Residual risk after pass** | Static only — does not prove live WFP/minifilter deny, runtime secret egress, live budget monotonicity, live evidence chain integrity, signed exit enforcement, or 48h behavior. |
| **Authority dependency** | Matt Phase 1 auth; Codex diff review |
| **Exit status** | **COMPLETE** — Codex CLEAN 2026-07-04 |

---

## Phase 2 — Deterministic fuzz harness

| Field | Value |
|-------|-------|
| **Phase** | 2 |
| **Claim** | M4 parser, FSM, AFE ledger, canary classifier, evidence rollup, and restart/resume paths survive deterministic adversarial mutation (recorded seed) without crash, silent truncation, fail-open, non-monotonic ledger acceptance, or verify() pass on tampered chain. |
| **Evidence artifact** | `scripts/m4_fuzz_harness.py`, per-target `fuzz_summary.json` under `EVIDENCE_ROOT/fuzz/`, seed list, failure ledger, replay command |
| **Falsifier** | Any mutation causes crash, unenumerated FSM state, unattributed burn accepted, canary misclassification, `verify()` true on incomplete chain, or resume crediting unobserved interval. |
| **Required negative test** | Corpus fixtures per §6 target table; zero failures across all targets for gate PASS |
| **Residual risk after pass** | Does **not** prove sandbox escape resistance, host boundary enforcement, canary **runtime** firing under live assault, evidence anti-forgery under operator attack, replay remediation, M3 slice, or 48h endurance. **Do not oversell.** |
| **Authority dependency** | Matt Phase 2 auth; Codex plan + diff review |
| **Exit status** | **CLEAN** — Codex 2026-07-04 (round 4) |

---

## Phase 3 — Sandbox escape suite (policy-model scope)

| Field | Value |
|-------|-------|
| **Phase** | 3 |
| **Claim** | **Policy-model only:** SE-FS..SE-KEY modular escape vectors classify as DENY or CONTAINED under the Phase 3 boundary policy model — not live host enforcement. |
| **Evidence artifact** | `mmi/m4/sandbox_escape.py`, `scripts/m4_sandbox_escape_suite.py`, `sandbox_escape_summary.json`, Codex CLEAN review |
| **Falsifier** | Any §7 module returns ALLOW; missing module; evidence under `AUTHORITY_ROOT`. |
| **Required negative test** | `test_module_fails_on_allow`; SE-9P vectors present; per-module DENY/CONTAINED in summary |
| **Residual risk after pass** | **R-001, R-008, R-031 remain OPEN.** Does not prove live Windows WFP/minifilter, TCB/`KEY_CUSTODY`, authority-root protection under real host conditions, PC2→PC1 write isolation, daemon dead-man, or fail-closed under assault. |
| **Authority dependency** | Phase 2 Codex CLEAN; Matt Phase 3 auth; Codex diff review — does not authorize Phase 4 |
| **Exit status** | **CLEAN** — Codex 2026-07-04 (policy-model scope only) |

**Forbidden inference after Phase 3:** live containment proven; host boundary safe; M4 materially safer under real assault.

---

## Phase 4 pre-build gate — TCB / host-boundary min-viable slice (COMPLETE)

**Status:** `COMPLETE` — P4-Q1..Q10 answered; Codex plan **BUILDABLE** (2026-07-04); Matt **`matt_auth_phase4`** (2026-07-04). Build in progress from sub-phase **4A**.

Phase 4 is a **ceiling test** — live TCB and host-boundary mechanics, materially more dangerous than Phase 3 policy model. The assurance case required these answers **before** any Phase 4 build exists:

| # | Pre-build question | Spec anchor | Answer status |
|---|-------------------|-------------|---------------|
| P4-Q1 | What is inside the TCB? | §8, §17 P4 | **ANSWERED (plan)** — PC1 KEY_CUSTODY, stage_attestation, Go daemon, minifilter, WFP, EVIDENCE_ROOT, H0 seal, dead-man, clock witness |
| P4-Q2 | What is outside the TCB? | §8, dual-PC decision | **ANSWERED (plan)** — clone/PC2 forge, LAB_ROOT, runner (no keys), read-only snapshot, read-only observability |
| P4-Q3 | Which keys exist and where do they live? | `KEY_CUSTODY` | **ANSWERED (plan)** — TPM/HSM on PC1 only; ENFORCEMENT_KEY = FileId set not crypto; stub cannot satisfy exit |
| P4-Q4 | What signs stage exits? | §3.1, `stage_attestation` | **ANSWERED (plan)** — KEY_CUSTODY over full tuple incl. signed_H0 + parent_exit_hash; emit_none on non-promoting |
| P4-Q5 | What validates stage exits? | `verify_exit`, `EXIT_BINDS_H0` | **ANSWERED (plan)** — verify_exit + current H0 match + single C-M4 lineage; CANARY-023 on forgery |
| P4-Q6 | What can the chaos side read? | §8, `AUTHORITY_MOUNT_DEFAULT` | **ANSWERED (plan)** — read-only snapshot only; no live authority mount; no keys/evidence/production |
| P4-Q7 | What can the chaos side write? | §8 minifilter FileId deny | **ANSWERED (plan)** — default deny authority FileIds + link-create; LAB_ROOT only; 9P FileId closure |
| P4-Q8 | What happens on daemon death? | CANARY-005, dead-man T4 | **ANSWERED (plan)** — gap >30s → CANARY-005 → HALT `unpoliced_perimeter`; interval uncredited |
| P4-Q9 | What happens on WFP or minifilter failure? | fail-closed, T7 | **ANSWERED (plan)** — fail-closed HALT; no monitor-only; manifest mismatch refuses arm |
| P4-Q10 | What proves PC2 cannot mutate PC1 authority? | dual-PC network rules, R-030 | **ANSWERED (plan)** — layered network ops + T1/T2/FileId + fingerprint; **R-030 OPEN until PC2 ops proof** |

**Plan artifact:** `mmi/project_brain/lanes/MMI_M4_PHASE4_TCB_HOST_BOUNDARY_PLAN_2026-07-04.md`  
**Codex handoff:** `mmi/project_brain/lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_PHASE4_2026-07-04.md`

**Min-viable slice exit (when built):** deny-write T1/T2, WFP default-deny T7, dead-man T4, signed-manifest refusal, clock-witness live (§8). Absent → `host_boundary_min_viable = false` → M4 entry refused.

**Next lane:** Codex plan review → BUILDABLE \| NOT BUILDABLE → Matt `matt_auth_phase4` → Cursor build 4A→4G → Codex diff review. Not authorized from this document.

---

## Phase 4 — TCB + host boundary min-viable (build row — NOT STARTED)

| Field | Value |
|-------|-------|
| **Phase** | 4 |
| **Claim** | `KEY_CUSTODY`, `stage_attestation`, and `host_boundary/mmi_boundary_daemon` (WFP + minifilter) prove min-viable slice: deny-write under T1/T2, WFP default-deny under T7, dead-man under T4, signed-manifest refusal, clock-witness live. |
| **Evidence artifact** | Boundary daemon logs, WFP/minifilter deny captures, `KEY_CUSTODY` non-export proof, stage attestation unit tests, T1/T2/T4/T7 fixture results |
| **Falsifier** | ALLOW-write to authority FileId; production egress from clone SID; dead-man fails to halt; stale signed exit admits next stage (`EXIT_BINDS_H0` violation). |
| **Required negative test** | T1/T2/T4/T7 falsifiers; FileId-not-SID 9P relay case (§8) |
| **Residual risk after pass** | Does not prove full canary taxonomy runtime, AFE under hostile attribution audit, endurance clock, or §13.1 replay remediation. |
| **Authority dependency** | Phase 3 Codex CLEAN; pre-build gate complete; Matt Phase 4 auth 2026-07-04; Codex diff review after 4G |
| **Exit status** | **IN PROGRESS** — build 4A→4G authorized; not CLEAN until Codex diff review |

---

## Phase 5 — M3 minimum diagnostic slice

| Field | Value |
|-------|-------|
| **Phase** | 5 |
| **Claim** | M4-relevant M3 mesh subset (`m3_min_slice.py`) passes bounded diagnostic and emits signed `m3_min_slice_exit` binding repo fingerprint + `M3_MIN_SLOTS_V`. |
| **Evidence artifact** | `scripts/m3_min_slice.py`, signed `m3_min_slice_exit`, slot pass log |
| **Falsifier** | FAIL with no artifact; exit binds wrong fingerprint; slot pass without actual mesh execution. |
| **Required negative test** | Slot failure fixture; fingerprint mismatch rejection |
| **Residual risk after pass** | Does **not** satisfy `M3_REQUIRED_FOR_PERFECT_CLAIM` (full 700-slot mesh). Gates C3+ only. |
| **Authority dependency** | Phase 4 exit; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 6 — Canary engine + evidence chain + AFE ledger

| Field | Value |
|-------|-------|
| **Phase** | 6 |
| **Claim** | 26 canary IDs (§9) fire on breach signals; append-only hash evidence chain verifies; AFE ledger burn is monotonic and attributed; unit + fuzz PASS. |
| **Evidence artifact** | `m4_canary_engine`, `evidence_chain`, AFE ledger modules, canary blind-spot table, unit test + fuzz results |
| **Falsifier** | CANARY fail-open; chain gap/backfill accepted; unattributed budget delta; blind-spot canary never fires on known hostile signal |
| **Required negative test** | Per-canary threshold boundary inputs; CANARY-011 link mismatch; CANARY-015/016 budget cases |
| **Residual risk after pass** | Does not prove live 4h/12h/24h/48h endurance, §13.1 capture/replay, or operator GATED attestation. |
| **Authority dependency** | Phase 5 exit; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 7 — Endurance dry-run (C-M4)

| Field | Value |
|-------|-------|
| **Phase** | 7 |
| **Claim** | `m4_endurance_runner.py --stage C-M4` reaches `HARNESS_READY` — harness wiring, FSM, interval credit, and pre-flight gates function without claiming CLEAN or M4_MET. |
| **Evidence artifact** | C-M4 summary JSON, chain tip, `HARNESS_READY` status, dry-run telemetry |
| **Falsifier** | HARNESS_READY without prior phase exits; cold-start to M4 path exists; `perfect_claim: true` in summary |
| **Required negative test** | Entry refused without Phase 6 exit; BLOCKED emits no downstream-admissible artifact |
| **Residual risk after pass** | Dry-run only — no duration proof, no assault budget depletion, no draft-patch evidence. |
| **Authority dependency** | Phase 6 exit; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 8 — C2 endurance (4h)

| Field | Value |
|-------|-------|
| **Phase** | 8 |
| **Claim** | 4h staged assault inside clone completes with `CLEAN` exit, signed over authority baseline, parent lineage intact. |
| **Evidence artifact** | C2 signed exit, 4h summary, chain verify output, invariant rollup |
| **Falsifier** | CRITICAL without BLOCKED; CLEAN without prior C-M4 exit; clock reset on FINAL-grade run (if misconfigured) |
| **Required negative test** | Correlated-failure T12; V-009 upstream chain integrity |
| **Residual risk after pass** | 4h only — does not prove 12h/24h/48h; scoped reset permitted for pre-M4 debugging only. |
| **Authority dependency** | Phase 7 HARNESS_READY; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 9 — C3 endurance (12h)

| Field | Value |
|-------|-------|
| **Phase** | 9 |
| **Claim** | 12h staged assault completes `CLEAN` with M3 min slice validated at entry; FINAL-grade correlated-failure rules apply. |
| **Evidence artifact** | C3 signed exit, 12h summary, M3 slice pass flag, chain verify |
| **Falsifier** | M3 slice bypass at entry; diagnostic laundering of critical chain (§11) |
| **Required negative test** | Entry refused without valid `m3_min_slice_exit`; T12 correlated failure |
| **Residual risk after pass** | 12h only — not 24h/48h; no §13.1 replay remediation yet. |
| **Authority dependency** | Phase 8 CLEAN + M3 slice; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 10 — C4 endurance (24h) + §13.1 min-viable

| Field | Value |
|-------|-------|
| **Phase** | 10 |
| **Claim** | 24h assault completes `CLEAN` with `draft_patch_evidence.min_viable == true`: exploit attempt log inline, sanitizer fail-closed, `complete()` + `replay_complete()` fuzz PASS, CANARY-026 registered. |
| **Evidence artifact** | C4 signed exit, 24h summary, `exploit_attempt_log`, sanitized captures, replay verifier output, T15/T16 fixture results |
| **Falsifier** | Capture without replay; sanitizer bypass (CANARY-026); T15 replay failure still credits interval |
| **Required negative test** | T15 replay failure → M4_NOT_MET path; T16 inline attempt log missing |
| **Residual risk after pass** | 24h dress rehearsal — **not** 48h FINAL; `perfect_claim` still pinned false; operator GATED not issued. |
| **Authority dependency** | Phase 9 CLEAN + M3 + boundary min-viable; Matt auth; Codex |
| **Exit status** | **NOT STARTED** |

---

## Phase 11 — M4 FINAL (48h)

| Field | Value |
|-------|-------|
| **Phase** | 11 |
| **Claim** | Single unbroken 48h assault satisfies `M4_MET` pass line: duration, all invariants held, chain verified, `reset_count == 0`, budget depleted, `draft_ok` (capture + replay per exploit), signed exit. `perfect_gate_remaining == []` iff M4_MET. |
| **Evidence artifact** | `m4_48h_summary.json`, full evidence chain, AFE final ledger, per-exploit capture + replay records, operator attest slot (unfilled until GATED) |
| **Falsifier** | Any CRITICAL; clock reset on FINAL; capture-only without replay; `perfect_claim: true` without operator GATED |
| **Required negative test** | T13 budget-not-depleted at ROLLUP; reset_count > 0 → M4_NOT_MET cap |
| **Residual risk after pass** | M4_MET is matrix-aligned terminal — **not** full AGI Phase 3, **not** full 700-slot M3 PERFECT claim, **not** external market attestation unless separately scheduled. |
| **Authority dependency** | Phase 10 exit + M3 + boundary; Matt operator GATED for promotional claims |
| **Exit status** | **NOT STARTED** — not buildable until Phases 0–10 complete |

---

## Cross-cutting assurance rules

1. **No double-counting:** Phase N evidence cannot satisfy Phase N+M claims without Phase N+M exit.
2. **No silent promotion:** `INV-6` — BUILD_AUTHORIZED remains false; operator attest required for GATED.
3. **No capture-only shortcut:** §13.1 Matt ruling — replay-verified draft patch required for M4_MET.
4. **No ladder skip:** H-LADDER-001 — 48h runner is Phase 11, last.
5. **Ledger sync:** Every exit status change here must update `MMI_RESIDUAL_RISK_LEDGER_2026-07.md`.

---

## Revision log

| Date | Change |
|------|--------|
| 2026-07-04 | Phase 1.5 scaffold opened; Phases 0–1 COMPLETE; Phases 2–11 NOT STARTED |
| 2026-07-04 | Phase 3 CLEAN (policy-model scope); Phase 4 pre-build gate P4-Q1..Q10; blocked `matt_auth_phase4` |

**Not claimed:** M4_MET, PERFECT, GATED, spec amendment.
