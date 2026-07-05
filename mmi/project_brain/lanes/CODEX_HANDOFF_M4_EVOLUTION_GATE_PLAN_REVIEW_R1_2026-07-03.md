# Codex Plan Review — M4 Evolution Gate

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** PRE-BUILD PLAN REVIEW  
**Date:** 2026-07-03  
**Verdict:** **NOT BUILDABLE**

**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`  
**Handoff:** `lanes/CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_2026-07-03.md`  
**Build auth:** NOT AUTHORIZED  
**Evolution gate:** OUTSTANDING — no PERFECT, no M4 closed

---

## Verdict

```text
NOT BUILDABLE
```

---

## Numbered blockers

| # | Blocker | Required resolution |
|---|---------|---------------------|
| 1 | **Narrow vs superset** — filed spec is Sections 0–6 only; handoff requires 17 sections, ≥20 canaries, T1–T12, §17 build phasing. Footnote [A] requires expansion or explicit Matt narrow-slice build auth. | Expand spec to handoff superset **or** Matt: `authorize build M4 evolution gate narrow slice` with documented scope cut |
| 2 | **M3 minimum diagnostic slice undefined** — referenced before C3/C4/M4; no pass criteria, evidence artifact, or terminal state | Claude spec §: define slice, fixtures, exit artifact |
| 3 | **Formal invariant suite + fuzz harness missing** — research v2.1 requires before endurance; spec only constants/prose | Add normative § with verification method + harness contracts |
| 4 | **TCB unbuilt** — `stage_attestation`, `KEY_CUSTODY`, `host_boundary/mmi_boundary_daemon` design-only | Acceptable in spec; build plan must phase these **before** endurance gates — not BUILDABLE until phased in §17 |
| 5 | **V-009 not testable** — C3/C4 FINAL-grade integrity named but no correlated-failure rules, fixtures, falsifiers | Add classification rules + T-scenario + acceptance criteria |
| 6 | **Canary taxonomy insufficient** — 001..006 vs research §4.2 + handoff ≥20 IDs | Expand closed enum; map blind-spot categories |
| 7 | **Falsifier suite incomplete** — T1–T9; T10/T11 named only; T12 missing | Full T1–T12 with expected terminal states |
| 8 | **No §17 build phasing table** — "48h runner LAST" under-specified | Add deliverable→gate table; enforce staged ladder |
| 9 | **L8 namespace separation not enforceable** — stated but no import/namespace contract or test | Add H-rule + harness check blocking L8 conflation |

---

## Queue note (Codex)

- `python3 scripts/reload_mmi_pipes.py` → PIPE STATUS: DRY
- `python3 scripts/next_task.py` → no active task in `tasks.json`
- No build authorized, no PERFECT claim, no M4 closure

---

## Next steps (Matt)

**Path B — recommended (matches handoff + research v2.1):**

```text
Claude: expand MMI_M4_EVOLUTION_GATE_SPEC to full 17-section superset
→ Codex plan review R2
→ BUILDABLE → authorize build M4 evolution gate
```

**Path C — alternate (explicit scope cut):**

```text
Matt: authorize build M4 evolution gate narrow slice
→ Cursor implements only phased subset per documented cut
→ Not sufficient for PERFECT / M4 closed claims
```

**Do not:** `authorize build M4 evolution gate` on current spec without Path B completion or Path C explicit auth.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| R1 | 2026-07-03 | Codex NOT BUILDABLE — 9 blockers |
