# LLM_BUILD_LAWS_2026-07.md

**Artifact:** `LLM_BUILD_LAWS_2026-07.md`
**Role:** Lane-specific laws for the BUILD lane
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Parent:** `LLM_PROJECT_LAWS_2026-07.md` (supreme)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

These laws apply only when `LANE = BUILD`. They are in addition to, and must not contradict, `LLM_PROJECT_LAWS_2026-07.md`.

***

## Law B1 — Build Lane Purpose and Boundary

The BUILD lane shall propose or refine concrete structures, interfaces, and mechanisms consistent with existing guardrails and non-claims.

- The BUILD lane shall not claim that its outputs are approved, build-ready, or safe for production.
- Any BUILD output that implies implementation authority or system readiness without a separate gate is a violation of this law.

***

## Law B2 — Constraint and Guardrail Supremacy

Every BUILD output shall explicitly acknowledge and respect existing guardrails, non-claims, and authority boundaries.

- It shall not contradict or weaken established laws, rubrics, or risk controls.
- It shall call out any tension between its proposals and existing constraints, rather than silently overriding them.
- Any BUILD output that ignores or contradicts known guardrails is invalid.

***

## Law B3 — Failure Mode and Risk Awareness

Every BUILD output shall address failure modes and risk implications of its proposals.

- It shall describe at least one plausible failure mode for each major design choice.
- It shall identify which risks are affected (new, modified, or unchanged) and how.
- Any BUILD output that presents a design as risk-free or failure-proof is a violation of this law.

***

## Law B4 — No Silent Authority Expansion

The BUILD lane shall not expand authority, trust, or closure by implication.

- It shall not treat design acceptance as proof of system behavior.
- It shall not treat clean structure as evidence of safety or readiness.
- Any BUILD output that implies “this is now safe to build/run” without an explicit, separate authorization gate is a violation of this law.

***

## Law B5 — Review Verdict Discipline

Every BUILD output shall end with a binary verdict: `BUILD_REVIEW_VERDICT = ADEQUATE_DRAFT` or `BUILD_REVIEW_VERDICT = INADEQUATE_DRAFT`.

- ADEQUATE_DRAFT is forbidden if:
  - Any universal dimension is `MISSING`.
  - Known guardrails or laws are violated or ignored.
- When in doubt, the BUILD lane shall choose `INADEQUATE_DRAFT`.
- No BUILD output may imply that ADEQUATE_DRAFT equals approval to build or run.

***

## Law B6 — Build-Only Nature of This Document

This document is documentation/control only.

- It does not prove any build behavior.
- It does not grant build or runtime authority.
- It does not by itself justify perfect closure, gated status, or M4 closure.

***
