# LLM_RESEARCH_LAWS_2026-07.md

**Artifact:** `LLM_RESEARCH_LAWS_2026-07.md`
**Role:** Lane-specific laws for the RESEARCH lane
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Parent:** `LLM_PROJECT_LAWS_2026-07.md` (supreme)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

These laws apply only when `LANE = RESEARCH`. They are in addition to, and must not contradict, `LLM_PROJECT_LAWS_2026-07.md`.

***

## Law R1 — Research Purpose and Boundary

The RESEARCH lane shall gather, synthesize, and map information, options, and uncertainties relevant to the project.

- The RESEARCH lane shall not assert system correctness, safety, or closure.
- Any RESEARCH output that presents findings as proven system truth is a violation of this law.

***

## Law R2 — Uncertainty and Option Mapping

Every RESEARCH output shall explicitly map uncertainties and options.

- It shall distinguish between: established facts, informed hypotheses, and speculation.
- It shall list key unknowns and open questions that affect decisions.
- Any RESEARCH output that presents a single view as the only valid interpretation without acknowledging uncertainty is a violation of this law.

***

## Law R3 — Non-Claim and Authority Discipline

The RESEARCH lane shall not expand authority, trust, or closure by implication.

- It shall not treat summaries or syntheses as proof of system behavior.
- It shall not imply that research coverage equals design completeness or safety.
- Any RESEARCH output that implies “this is now proven” or “this is safe” without a separate, explicit gate is a violation of this law.

***

## Law R4 — Coverage and Source Awareness

Every RESEARCH output shall address coverage and source limitations.

- It shall state what areas are well-covered and what areas are weak or missing.
- It shall note major source limitations (e.g., outdated, narrow, or conflicting sources) where relevant.
- Any RESEARCH output that presents itself as comprehensively exhaustive without justification is a violation of this law.

***

## Law R5 — Research Review Verdict Discipline

Every RESEARCH output shall end with a binary verdict: `RESEARCH_REVIEW_VERDICT = ADEQUATE_DRAFT` or `RESEARCH_REVIEW_VERDICT = INADEQUATE_DRAFT`.

- ADEQUATE_DRAFT is forbidden if:
  - Any universal dimension is `MISSING`.
  - Known laws, guardrails, or non-claims are violated or ignored.
- When in doubt, the RESEARCH lane shall choose `INADEQUATE_DRAFT`.
- No RESEARCH output may imply that ADEQUATE_DRAFT equals truth, safety, or closure.

***

## Law R6 — Research-Only Nature of This Document

This document is documentation/control only.

- It does not prove any research behavior.
- It does not grant authority or trust.
- It does not by itself justify perfect closure, gated status, or M4 closure.

***

If you’d like, the next step can be a tiny index file (e.g., `LLM_LANES_INDEX.md`) that lists all four lane law artifacts and briefly states when each one must be used.
