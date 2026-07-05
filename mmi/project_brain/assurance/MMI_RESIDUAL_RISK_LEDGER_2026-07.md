# MMI Residual Risk Ledger — M4 Evolution Gate

**Status:** LIVING DOCUMENT — Phase 1.5 scaffold  
**Date opened:** 2026-07-04  
**Companion:** `MMI_ASSURANCE_CASE_2026-07.md`  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5)

**Purpose:** Inventory what remains **unproven** after each phase passes. Elite systems do not hide uncertainty — they record it.

**Update rule:** When a phase completes, mark addressed risks **MITIGATED (phase N)** only for the scope that phase actually proved. Leave all other rows **OPEN**.

**Claims forbidden using this file alone:** M4_MET, containment proven / containment-proven, PERFECT, GATED.

---

## Risk severity key

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Could invalidate M4_MET if unaddressed at FINAL |
| **HIGH** | Could produce false confidence or silent promotion |
| **MEDIUM** | Known gap with planned §17 phase owner |
| **LOW** | Out of M4 scope or post-M4 |

---

## Open risks (master inventory)

| ID | Risk | Severity | Owner phase | Status | Last verified |
|----|------|----------|-------------|--------|---------------|
| R-001 | Runtime authority write via host boundary bypass (not static AST) | CRITICAL | 4, 11 | OPEN | 2026-07-04 |
| R-002 | Production endpoint reachable from clone at runtime | CRITICAL | 4, 11 | OPEN | 2026-07-04 |
| R-003 | Secret material crosses clone boundary at runtime | CRITICAL | 4, 6, 11 | OPEN | 2026-07-04 |
| R-004 | AFE budget non-monotonic or unattributed under assault | CRITICAL | 6, 11 | OPEN | 2026-07-04 |
| R-005 | Evidence chain gap, backfill, or reorder under live run | CRITICAL | 6, 11 | OPEN | 2026-07-04 |
| R-006 | Autonomous stage promotion without signed exit + operator attest | CRITICAL | 4, 7–11 | OPEN | 2026-07-04 |
| R-007 | Ladder skip or stale exit admits wrong stage | CRITICAL | 4, 7–11 | OPEN | 2026-07-04 |
| R-008 | Sandbox escape to authority surface (live host boundary) | CRITICAL | 3, 4, 11 | **OPEN** — Phase 3 policy-model CLEAN does not close | 2026-07-04 |
| R-009 | Parser/FSM/ledger fail-open under mutation | HIGH | 2 | **MITIGATED (P2 fuzz scope)** | 2026-07-04 |
| R-010 | Canary blind-spot — known hostile signal does not fire | CRITICAL | 6, 11 | OPEN | 2026-07-04 |
| R-011 | Capture-only exploit evidence without replay remediation | CRITICAL | 10, 11 | OPEN | 2026-07-04 |
| R-012 | Sanitizer bypass (CANARY-026 path) | CRITICAL | 10, 11 | OPEN | 2026-07-04 |
| R-013 | 48h clock reset or diagnostic laundering on FINAL | CRITICAL | 11 | OPEN | 2026-07-04 |
| R-014 | Attacker budget not depleted at ROLLUP (T13) | CRITICAL | 11 | OPEN | 2026-07-04 |
| R-015 | L8 namespace coupling in `mmi/m4/*` | HIGH | 0 | **MITIGATED (P0)** | 2026-07-04 |
| R-016 | Static authority write paths in M4 source (incl. multi-line) | HIGH | 1 | **MITIGATED (P1 static)** | 2026-07-04 |
| R-017 | Static promotion bypass patterns in M4 source | HIGH | 1 | **MITIGATED (P1 static)** | 2026-07-04 |
| R-018 | Forbidden `/tmp` evidence root in M4 source | HIGH | 1 | **MITIGATED (P1 static)** | 2026-07-04 |
| R-019 | Assurance rows drift from actual build state | MEDIUM | 1.5 | **MITIGATED (P1.5 scaffold)** | 2026-07-04 |
| R-020 | Phase exit oversold as broader containment proof | HIGH | 1.5 | OPEN — discipline ongoing | 2026-07-04 |
| R-021 | Recovery / rollback proof after breach | HIGH | AGI P3 | OPEN — not in §17 | 2026-07-04 |
| R-022 | Clone destruction proof post-assault | MEDIUM | ops / dual-PC | OPEN | 2026-07-04 |
| R-023 | Credential rotation proof after incident | MEDIUM | future | OPEN | 2026-07-04 |
| R-024 | Independent external adversarial review | MEDIUM | post C-M4 | OPEN | 2026-07-04 |
| R-025 | Real-world tenant / pilot evidence | LOW | out of M4 | OPEN | 2026-07-04 |
| R-026 | Full 700-slot M3 mesh (PERFECT claim) | LOW | AGI / M3 | OPEN — explicit non-goal for M4 | 2026-07-04 |
| R-027 | AGI Phase 2 `central_brain.py` self-schema compilation | LOW | AGI | OPEN — out of M4 scope | 2026-07-04 |
| R-028 | AGI Phase 3 30-day continuous proof | LOW | AGI | OPEN — out of M4 scope | 2026-07-04 |
| R-029 | Formal threat model document | MEDIUM | cross-cutting | OPEN | 2026-07-04 |
| R-030 | PC2 chaos forge isolation — no write path to AUTHORITY_ROOT | HIGH | dual-PC ops | OPEN — decision filed, not proven | 2026-07-04 |
| R-031 | 9P/DrvFs relay write attribution bypass | CRITICAL | 3, 4 | OPEN | 2026-07-04 |
| R-032 | Raw volume access bypassing FS filters | CRITICAL | 4 | OPEN | 2026-07-04 |
| R-033 | Reviewer lane failure (wrong scope CLEAN, summary-only review) | HIGH | cross-lane | OPEN — see reviewer failure model | 2026-07-04 |
| R-034 | Operator signing under fatigue/coercion without evidence binding | HIGH | GATED | OPEN — see signing threat model | 2026-07-04 |
| R-035 | Summary/report diverges from raw evidence | HIGH | all phases | OPEN — see evidence-summary binding | 2026-07-04 |
| R-036 | Recovery/rollback not proven on failure | HIGH | 5, AGI P3 | OPEN — see recovery proof requirements | 2026-07-04 |
| R-037 | Canary defined without bypass negative test | HIGH | 6 | OPEN — see canary bypass standard | 2026-07-04 |

---

## Mitigated risks — scope statements (do not oversell)

### R-015 — MITIGATED (Phase 0)

**Proved:** Static AST/string scan — zero `canary_metadata_layer` coupling in `mmi/m4/*`.  
**Still open:** Runtime import injection, dynamic code load, non-Python coupling paths.

### R-016 — MITIGATED (Phase 1 static)

**Proved:** Static AST taint — no authority write paths in scanned M4 sources incl. multi-line/alias flows.  
**Still open:** Runtime writes via boundary bypass, out-of-tree scripts, live minifilter misconfiguration.

### R-017 — MITIGATED (Phase 1 static)

**Proved:** Static scan rejects `BUILD_AUTHORIZED = True`, `perfect_claim: true`, promotion bypass patterns in M4 sources.  
**Still open:** Runtime config override, unsigned exit replay, operator bypass outside scanned files.

### R-018 — MITIGATED (Phase 1 static)

**Proved:** Static scan rejects `/tmp/mmi_evidence` and forbidden evidence root patterns in M4 sources.  
**Still open:** Runtime evidence path misconfiguration, off-repo evidence writes.

### R-019 — MITIGATED (Phase 1.5 scaffold)

**Proved:** Assurance case + residual ledger exist with per-phase rows.  
**Still open:** Rows must be updated each phase or drift becomes R-020.

### R-009 — MITIGATED (Phase 2 fuzz scope)

**Proved:** Deterministic fuzz (seed recorded) over §6 targets — parser, FSM, ledger, canary classifier, evidence rollup, restart — zero failures at default corpus; INV static re-check passes after fuzz.  
**Still open:** Live assault paths, host boundary, runtime canaries, 48h endurance, novel out-of-corpus mutations.

---

## Phase completion — risk retirement checklist

When a phase exits green, update this ledger:

| Phase complete | Retire / mitigate (scoped) | Must remain OPEN |
|----------------|---------------------------|------------------|
| 0 | R-015 | R-001–R-014, R-020+ |
| 1 | R-016, R-017, R-018 | All runtime CRITICAL rows |
| 2 | R-009 (fuzz scope only) | R-001–R-008, R-010–R-014 |
| 3 | Policy-model SE-FS..SE-KEY classification only — **does not retire CRITICAL rows** | **R-001, R-008, R-031 OPEN**; all live boundary / TCB rows |
| 4 | R-001, R-002, R-031, R-032 (min-viable) | Endurance-scale behavior |
| 5 | M3 min slice subset only | R-026 full mesh |
| 6 | R-004, R-005, R-010 (unit scope) | Live 48h scale |
| 7–9 | Harness + duration partial | Full 48h, §13.1 |
| 10 | R-011, R-012 (min-viable) | 48h FINAL unbroken |
| 11 | M4_MET pass-line bundle | R-024–R-028, AGI, external |

---

## Anti-oversell register (mandatory language)

| After phase | Do NOT say | DO say |
|-------------|-----------|--------|
| 2 fuzz PASS | "Containment proven" / "Containment-targeting complete" | "Deterministic fuzz targets passed under recorded seeds; M4 remains containment-targeting until FINAL evidence; see R-001–R-014 still OPEN" |
| 3 sandbox CLEAN | "M4 is safe" / "containment proven" / "live boundary holds" | "Phase 3 policy-model sandbox escape coverage only — SE-FS..SE-KEY DENY/CONTAINED in model; R-001, R-008, R-031 OPEN; MMI remains containment-targeting" |
| 4 boundary PASS | "Authority is untouchable" | "Min-viable boundary slice proven T1/T2/T4/T7; endurance not yet run" |
| 10 C4 PASS | "PERFECT is close" | "24h CLEAN + §13.1 min-viable; 48h FINAL and GATED still required" |
| 11 M4_MET | "PERFECT tier achieved" | "M4_MET matrix pass-line satisfied; `perfect_claim` pinned until operator GATED" |

---

## Revision log

| Date | Change |
|------|--------|
| 2026-07-04 | Ledger opened; R-015–R-019 mitigated scoped; R-001–R-014, R-020+ OPEN |
| 2026-07-04 | Phase 3 Codex CLEAN — R-001/R-008/R-031 remain OPEN; Phase 4 pre-build gate added to assurance case |

**Not claimed:** M4_MET, PERFECT, GATED, all risks closed.
