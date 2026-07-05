# M4 Evolution Gate Spec R2 — Cursor Closeout

**Date:** 2026-07-03  
**Source:** Claude Design — R2 superset relay (Matt) — MESSAGE 1R + MESSAGE 2R inline  
**Spec path:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`  
**SIGN-OFF:** PASS WITH REVISIONS  
**Build auth:** NOT AUTHORIZED

---

## Filed artifacts

| Artifact | Path |
|----------|------|
| Spec (R2 superset) | `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` |
| R1 narrow spec (replaced) | superseded by R2 filing |
| Codex handoff R2 | `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R2_2026-07-03.md` |
| Codex R1 verdict | `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_R1_2026-07-03.md` |
| Research v2.1 | `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` |
| Claude R2 handoff | `lanes/CLAUDE_HANDOFF_M4_EVOLUTION_GATE_SPEC_R2_EXPANSION_2026-07-03.md` |

---

## Scope reconciliation (R1 narrow → R2 superset)

| Handoff requirement | R2 spec | Status |
|---------------------|---------|--------|
| Full 17 sections | §1–§17 | **Present** |
| Staged ladder C-M4→C2→C3→C4→M4 | §3 + STAGE_ORDER | **Present** |
| 48h runner LAST | §17 Phase 11 | **Present** |
| ≥20 M4 canary IDs | 25 IDs §9 | **Present** |
| T1–T13 falsifiers | §14 complete + T13 | **Present** |
| Formal invariant suite | INV-1..7 §5 | **Present** |
| Fuzz harness | §6 CLI + terminal | **Present** |
| Sandbox escape | §7 modules | **Present** |
| Host boundary Windows-native | §8 | **Present** |
| AFE hostile audit | §10 | **Present** |
| M3 min slice | §12 (5 slots + stack named) | **Present** |
| Observability decision | §15 required vs optional | **Present** |
| §17 build phasing | 12 phases 0–11 | **Present** |
| L8 import ban enforceable | H-L8-001 + §13 test | **Present** |
| Codex R1 resolution map | end of spec | **Present** |

---

## Cursor ground-truth vs research v2.1 (repo read)

| v2.1 finding | R2 alignment |
|--------------|--------------|
| 48h is final ceremony, not first step | Aligned — §3, §17 |
| Staged proof ladder §1.6 | Aligned — §3 table + DAG §4 |
| Proof object = 4 conjuncts | Aligned — §2 |
| Full clock reset on M4 final | Aligned — §11, H-FINAL-001 |
| EVIDENCE off clone reach | Aligned — §2, H-EVID-001 |
| Expanded canary blind spots §4.2 | Aligned — §9 table maps categories |
| Windows-native boundary §5 | Aligned — §8, Footnote [B] |
| T1–T13 falsifiers §6 | §14 + §14.1 traceability; T13 closes research T4 | **Aligned** (T8 draft-patch deferred to build) |
| No L8 / northstar coupling | Aligned — §16 H-L8-001 |
| No PERFECT / M4 closed claim | Aligned — pinned `perfect_claim: false` |
| M3 min slice before endurance | §12 — 5 slots from `chaos_lab_provisioner.py` | **Aligned** |
| Research §6 T1–T12 | §14 + §14.1 traceability; T13 closes T4 | **Aligned** (T8 draft-patch deferred to build) |

---

## Cursor r2.1 grounding pass (2026-07-03)

Repo read on `C:\Architectapp_clean`:

- **`M3_MIN_SLOTS`:** 5 named slots + `M3_MIN_STACK` (`mesh-smash`, `purple-evasion`, `action-integrity`) from implemented provisioner mesh model (70 baseline + 40 air-lock wakes; not full 700-slot mesh).
- **Research §6:** §14.1 traceability table added; **T13** + `M4_BUDGET_DEPLETION_REQUIRED` closes research T4 (budget not depleted at 48h).
- **Residual (honest):** research T8 / §1.3 #7 draft-patch per-interval evidence — matrix doctrine, no repo module; flagged for build lane, not spec blocker for Codex plan review.

Spec revision pinned: **r2.1**.

---

## Workflow gaps

| Item | Status |
|------|--------|
| MESSAGE 1R superset | Relayed and filed |
| MESSAGE 2R adversarial self-review | Inline in spec revision log (7 fixes R-01..R-07) |
| MESSAGE 3R isolation audit | **NOT relayed** — optional before Codex R2; paste `CLAUDE_PASTE_M4_SPEC_R2_MESSAGE_3R_2026-07-03.txt` if Matt wants third pass |

---

## Claude audit summary (preserved in spec)

**MESSAGE 2R fixes:** R-01 stale-authority admission (EXIT_BINDS_H0), R-02 DIAGNOSTIC_or_CRITICAL, R-03 AFE_DRIFT_TOLERANCE, R-04 BOUNDARY_DEADMAN_GAP_S, R-05 CANARY-025, R-06 reset_count/M4_MET, R-07 lineage.

**Safety declaration:** FAILS SECURE over modeled set — not perfectly closed; TCB unbuilt.

---

## Next steps

1. ~~Matt → Codex R2~~ — **BUILDABLE** (2026-07-03, 0 blockers)
2. Matt: `authorize build M4 evolution gate` → Cursor **§17 Phase 0** first
3. After build: Codex diff review → completion gate → Matt GATED

**Do not claim:** PERFECT, M4 closed, GATED, BUILD AUTHORIZED (until Matt auth).
