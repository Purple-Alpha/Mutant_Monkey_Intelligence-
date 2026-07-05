# Research Control Stack Closeout — Assurance Doctrine

**Date:** 2026-07-04  
**Status:** RESEARCH-DRAFT CLEAN — **NOT SPEC, NOT BUILD, NOT GATE CLOSURE**  
**Lane:** Research / assurance control documentation only

---

## Stack filed (Phase 1.5 doctrine ceiling)

1. `lanes/RESEARCH_MMI_ASSURANCE_MATURITY_2026-07.md`
2. `lanes/RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md`
3. `assurance/MMI_ASSURANCE_CASE_2026-07.md`
4. `assurance/MMI_RESIDUAL_RISK_LEDGER_2026-07.md`
5. `assurance/MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`
6. `assurance/MMI_ASSURANCE_GATE_INVALIDATION_ADDENDUM_2026-07.md` (r2 deterministic outcomes)
7. `assurance/MMI_REVIEWER_FAILURE_MODEL_2026-07.md`
8. `assurance/MMI_OPERATOR_SIGNING_THREAT_MODEL_2026-07.md`
9. `assurance/MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md`
10. `assurance/MMI_RECOVERY_PROOF_REQUIREMENTS_2026-07.md`
11. `assurance/MMI_CANARY_BYPASS_ACCEPTANCE_STANDARD_2026-07.md`

---

## Current vs next ceiling

| State | Description |
| ----- | ----------- |
| **Now** | Policy-defined assurance controls |
| **Next** | Machine-checkable assurance controls (schemas + validator) — **requires separate Matt spec/build auth** |

Future path (not authorized): `MMI_ASSURANCE_SCHEMA_AND_VALIDATOR_SPEC_2026-07.md`, `scripts/mmi_assurance_validate.py`.

---

## Matt decisions outstanding

None required for the current gate. Evidence chain dictates the next move.

---

## Evidence-driven next step (sole build-ladder blocker)

| Step | Owner | Action |
| ---- | ----- | ------ |
| **1** | Codex | Phase 2 round-2 diff review — `CODEX_HANDOFF_M4_EVOLUTION_GATE_DIFF_REVIEW_PHASE2_2026-07-04.md` (EVIDENCE_ROOT fix) |
| **2** | Cursor | Phase 3 build **only after** Codex CLEAN on Phase 2 (§17 sequence) |
| **3** | — | Machine enforcement spec/build — **not** next; deferred until authorized |

Research-control lane: **closed**. No further assurance prose until enforceability spec is authorized.

---

## Previously resolved (not open decisions)

- Phase 1.5 scaffold: filed and complete.
- Phase 2 build: authorized and built; fix applied for Codex finding #1.

## Forbidden claims

M4_MET, PERFECT, GATED, build authorization from this closeout, containment-proven, AGI advancement.

**MMI remains containment-targeting until M4_MET evidence exists.**
