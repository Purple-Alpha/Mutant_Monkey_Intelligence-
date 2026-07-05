# M4 Evolution Gate Spec — Cursor Closeout

**Date:** 2026-07-03  
**Source:** Claude Design — MESSAGE 2 + MESSAGE 3 relay (Matt)  
**Spec path:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`  
**SIGN-OFF:** PASS WITH REVISIONS  
**Build auth:** NOT AUTHORIZED

---

## Filed artifacts

| Artifact | Path |
|----------|------|
| Spec (Claude) | `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` |
| Codex handoff | `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_2026-07-03.md` |
| Research v2.1 | `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` |
| Claude handoff | `lanes/CLAUDE_HANDOFF_M4_EVOLUTION_GATE_2026-07-03.md` |

---

## Scope reconciliation (Footnote [A] — critical)

Claude delivered a **narrow executable slice** (Sections 0–6 + footnotes), not the full **17-section MESSAGE 1 superset**.

| Handoff requirement | In filed spec | Status |
|---------------------|---------------|--------|
| Staged ladder C-M4→C2→C3→C4→M4 | §1.5 + STAGE_ORDER | **Present** (MESSAGE 3) |
| 48h runner LAST in build phasing | Implied; no §17 table | **Partial** |
| ≥20 M4 canary IDs | Only 001–006 | **GAP** |
| T1–T12 falsifiers | T1–T9; T10/T11 named | **GAP** |
| Formal invariant suite § | Constants in §0 only | **Partial** |
| Fuzz harness § | Not rendered | **GAP** |
| Host boundary §2 | Present | **Present** |
| AFE hostile audit | M4-CANARY-004 + envelope | **Partial** |
| M3 min slice definition | Referenced, not specified | **GAP** |
| Observability decision | Not explicit | **GAP** |

**Cursor ground-truth vs research v2.1 (repo read):**

| v2.1 finding | Spec alignment |
|--------------|----------------|
| Staged ladder before 48h | Aligned — §1.5, straight-to-48h forbidden in prose |
| Full clock reset on M4 final | Aligned — §1.2, SCOPED_RESET_ON_FINAL=false |
| EVIDENCE off clone reach | Aligned — V-001 remediation |
| Typed M3 gates | Constants present; M3 slice undefined |
| Expanded canary blind spots | Partial — 6 rules map categories; not ≥20 IDs |
| Windows-native boundary | Aligned — §2 |
| No L8 / northstar coupling | Aligned — explicit exclusions |
| No PERFECT / M4 closed claim | Aligned |

**Recommendation:** Codex plan review should return **NOT BUILDABLE** until either (a) Claude expands to full 17-section superset, or (b) Matt explicitly authorizes **narrow-slice phased build** with documented scope cut.

---

## Claude audit summary (preserved)

**MESSAGE 2:** V-1..V-11 — four Critical fake-pass paths remediated (path→FileId, fail-closed append, TCB/T9, etc.)

**MESSAGE 3:** V-001..V-011 — four Critical on prior draft (evidence under /tmp, skippable ladder, poisoned image, unsigned H0) remediated inline.

**Safety declaration:** As-revised = **FAILS SECURE** over modeled set — not perfectly closed; daemon/minifilter/stage_attestation unbuilt.

---

## Next steps

1. Matt → Codex: paste `CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_2026-07-03.md`
2. If NOT BUILDABLE (expected): expand spec OR narrow-build auth decision
3. If BUILDABLE: `authorize build M4 evolution gate` — **staged ladder first**, not 48h runner

**Do not claim:** PERFECT, M4 closed, GATED.
