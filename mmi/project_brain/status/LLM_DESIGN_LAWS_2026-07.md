# LLM_DESIGN_LAWS_2026-07.md

**Artifact:** `LLM_DESIGN_LAWS_2026-07.md`
**Role:** Lane-specific laws for the DESIGN lane
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Parent:** `LLM_PROJECT_LAWS_2026-07.md` (supreme)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

These laws apply only when `LANE = DESIGN`. They are in addition to, and must not contradict, `LLM_PROJECT_LAWS_2026-07.md`.

***

## Law D1 — Design Purpose and Boundary

The DESIGN lane shall propose or refine architectures, roles, interfaces, and state machines consistent with existing guardrails and non-claims.

- The DESIGN lane shall not claim that its outputs are approved, implementation-ready, or safe for production.
- Any DESIGN output that implies implementation authority or system readiness without a separate gate is a violation of this law.

***

## Law D2 — Structural Rigor and State Discipline

Every DESIGN output shall prioritize structural rigor and clear state semantics.

- It shall define states, transitions, roles, and invariants explicitly.
- It shall make misreading, relabeling, and authority drift structurally difficult.
- Any DESIGN output that relies on vague or implicit state behavior is a violation of this law.

***

## Law D3 — Constraint and Law Supremacy

Every DESIGN output shall explicitly respect and reference existing laws, guardrails, and non-claims.

- It shall not contradict or weaken established controls, risk ledgers, or authority boundaries.
- It shall call out any tension between its proposals and existing constraints, rather than silently overriding them.
- Any DESIGN output that ignores or contradicts known laws or guardrails is invalid.

***

## Law D4 — Risk and Failure Mode Awareness

Every DESIGN output shall address risk and failure implications of its choices.

- It shall identify at least one plausible failure mode for each major design decision.
- It shall describe how each decision affects residual risks (new, modified, or unchanged).
- Any DESIGN output that presents a design as risk-free or failure-proof is a violation of this law.

***

## Law D5 — Design Review Verdict Discipline

Every DESIGN output shall end with a binary verdict: `DESIGN_REVIEW_VERDICT = ADEQUATE_DRAFT` or `DESIGN_REVIEW_VERDICT = INADEQUATE_DRAFT`.

- ADEQUATE_DRAFT is forbidden if:
  - Any universal dimension is `MISSING`.
  - Known laws, guardrails, or risk controls are violated or ignored.
- When in doubt, the DESIGN lane shall choose `INADEQUATE_DRAFT`.
- No DESIGN output may imply that ADEQUATE_DRAFT equals approval to implement or operate.

***

## Law D6 — Design-Only Nature of This Document

This document is documentation/control only.

- It does not prove any design behavior.
- It does not grant implementation or runtime authority.
- It does not by itself justify perfect closure, gated status, or M4 closure.

***
