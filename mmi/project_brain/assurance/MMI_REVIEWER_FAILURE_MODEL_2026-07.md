# MMI Reviewer Failure Model

**Status:** HARD CONTROL — documentation only  
**Date:** 2026-07-04  
**Related:** RR-M4-007, RR-M4-008

**Forbidden claims:** M4_MET, PERFECT, GATED.

---

## Thesis

Reviewers (human and agent) are part of the **trusted computing surface**. Their failure modes must be modeled explicitly — not assumed away.

---

## Modeled failure modes

| ID | Failure | Example |
| -- | ------- | ------- |
| RF-01 | Misses critical implementation gap | Same-line-only check while multi-line bypass exists |
| RF-02 | Misreads scope boundary | Codex CLEAN treated as containment proof |
| RF-03 | Accepts CLEAN label with incomplete evidence | Summary without raw artifact |
| RF-04 | Reviewer fatigue / time pressure | Rubber-stamp handoff packet |
| RF-05 | Social pressure / near-pass coercion | "Almost CLEAN" → ship |
| RF-06 | Deceived by polished wording | Narrative optimism in handoff |
| RF-07 | Trusts summary not bound to raw evidence | Report says PASS; logs disagree |
| RF-08 | Wrong-lane review substituted | Research packet treated as build auth |
| RF-09 | Completion gate substitutes for diff review | Gate PASS without Codex |

---

## Counter-checks (mandatory)

- **Lane separation:** Codex ≠ completion gate ≠ Matt GATED ≠ research.
- **Cross-review:** NOT CLEAN → fix → re-review (Phase 0–2 pattern).
- **Raw artifact inspection:** reviewer must cite file paths + commands run.
- **Invalidation rules:** apply `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`.
- **Narrow claims:** assurance row residual risk must list what reviewer did **not** check.
- **Independent review (future):** external adversarial review post C-M4 dry-run (RR-M4-024).

---

## Who reviews whom (blind-spot map)

| Reviewer | Reviews | Does not replace |
| -------- | ------- | ---------------- |
| Codex | Plan, diff, spec alignment | Runtime assault, external pentest |
| Claude | Spec adversarial | Implementation tests |
| Research | Maturity, doctrine, framework mapping | BUILDABLE/CLEAN |
| Matt | Auth, GATED, scope rulings | Line-by-line code audit |
| pytest/harness | Falsifier fixtures | Unknown unknowns |
| External (future) | Claims vs reality | Internal velocity |

**No single checker eliminates all blind spots.** The residual-risk ledger records what remains open after each review.
