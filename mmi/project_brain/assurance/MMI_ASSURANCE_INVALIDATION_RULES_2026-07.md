# MMI Assurance Invalidation Rules

**Status:** HARD CONTROL — documentation only, no runtime  
**Date:** 2026-07-04 (aligned to gate addendum r2)  
**Lane:** Assurance control (Phase 1.5+)  
**Authoritative for gate closure:** `MMI_ASSURANCE_GATE_INVALIDATION_ADDENDUM_2026-07.md` (deterministic outcomes)  
**Research:** `RESEARCH_MMI_ASSURANCE_MATURITY_2026-07.md`, `RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md`

**Forbidden claims using this file alone:** M4_MET, PERFECT, GATED, build authorization.

---

## Purpose

Row-level invalidation checks for assurance case entries. **Gate closure, promotion, and GATED** must use the addendum's deterministic outcome table (G-INVAL-001..020).

**Core rule:** every invalidator maps to **exactly one** default outcome. No "reject or downgrade" unless the addendum names a weaker state (only G-INVAL-004 → `WEAK_CLAIM_REQUIRES_REVIEW`).

---

## Row invalidation → deterministic outcomes

| Row check | Maps to | Default outcome |
| --------- | ------- | --------------- |
| No evidence artifact | G-INVAL-001 | `REJECT_CLAIM` |
| No artifact hash / lineage | G-INVAL-002 | `REJECT_CLAIM` |
| No falsifier | G-INVAL-003 | `REJECT_CLAIM` |
| No negative test | G-INVAL-004 | `WEAK_CLAIM_REQUIRES_REVIEW` |
| No residual-risk link | G-INVAL-005 | `REJECT_PHASE_PASS` |
| No authority dependency | G-INVAL-006 | `REJECT_CLAIM` |
| No reviewer identity (gate claims) | G-INVAL-007 | `REJECT_GATE_CLOSURE` |
| No summary-to-artifact path | G-INVAL-008 | `REJECT_SUMMARY` |
| No explicit scope boundary | G-INVAL-009 | `REJECT_CLAIM` |
| Claim exceeds evidence scope | G-INVAL-010 | `REJECT_CLAIM` |
| Cross-lane authority borrow | G-INVAL-011 | `REJECT_CLAIM` |
| Stale evidence | G-INVAL-012 | `STALE_REVIEW_REQUIRED` |
| CLEAN used as broad safety language | G-INVAL-013 | `REJECT_SUMMARY` |
| Residual risk omitted from summary | G-INVAL-014 | `REJECT_SUMMARY` |
| Ambiguous authority metadata | G-INVAL-015 | `REJECT_GATE_CLOSURE` |
| Reviewer conflict | G-INVAL-016 | `REVIEWER_DISAGREEMENT_OPEN` |
| Review path compromise | G-INVAL-017 | `COMPROMISED_REVIEW_PATH` |
| Artifact set changed after claim | G-INVAL-018 | `SCOPE_DRIFT_REVIEW_REQUIRED` |
| Summary text changed after binding | G-INVAL-019 | `REJECT_SUMMARY` |
| Authority lacks evidence set ID | G-INVAL-020 | `REJECT_GATE_CLOSURE` |

---

## Additional control rules

- Claims must be narrow enough to falsify.
- Claims must not be rewritten post-hoc to match evidence.
- Promotion by narrative optimism → `REJECT_CLAIM`.
- A pass in one lane does not imply a pass in another → `REJECT_CLAIM` if implied.
- Tests do not equal assurance without assurance-row structure → `REJECT_PHASE_PASS`.

---

## Application

Before any phase reports CLEAN, BUILT-for-review, or GATED:

1. Verify assurance case row exists with all mandatory fields.
2. Apply G-INVAL-001..020; record **exactly one** outcome per trigger.
3. If `STALE_REVIEW_REQUIRED`, `SCOPE_DRIFT_REVIEW_REQUIRED`, `REVIEWER_DISAGREEMENT_OPEN`, or `COMPROMISED_REVIEW_PATH` — block closure until resolved per addendum §3–§8.
4. Update `MMI_ASSURANCE_CASE_2026-07.md` and `MMI_RESIDUAL_RISK_LEDGER_2026-07.md`.

**Not claimed:** automatic gate closure, runtime enforcement.
