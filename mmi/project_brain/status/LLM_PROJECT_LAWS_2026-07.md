Here is a set of laws version of your project-wide rubric, written so you can drop it directly into your documentation as binding constraints.

***

# LLM_PROJECT_LAWS_2026-07.md

**Artifact:** `LLM_PROJECT_LAWS_2026-07.md`
**Role:** Project-wide binding laws for all LLM outputs
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Scope:** All lanes (AUDIT, BUILD-DESIGN, RESEARCH, and any future lane)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

Any LLM output that violates these laws is invalid and must be treated as failed work.

***

## Law 1 — Lane Sovereignty

Every LLM call that produces a judgment, review, or audit shall declare a lane: `AUDIT`, `BUILD-DESIGN`, `RESEARCH`, or `OTHER_<NAME>`.
An undefined lane shall be treated as a violation of this law.

- The declared lane shall govern what the LLM is allowed to do and what it is forbidden to do.
- No LLM output may claim authority, build readiness, or system trust based solely on its own text.
- Lane drift (acting as if the lane is different from what was declared) is prohibited.

***

## Law 2 — Boundary and Non-Claim Supremacy

Every LLM output shall explicitly state its scope, boundaries, and non-claims.

- It shall declare what it covers and what it does not cover (system, environment, authority, evidence).
- It shall separate documentation/control from build, runtime, and trust authority.
- It shall explicitly list what it does not prove and what cannot be inferred from it.
- Any language that implies certainty, safety, or readiness beyond the stated scope and lane is a violation of this law.

***

## Law 3 — Evidence and Provenance Mandate

Every LLM output that addresses proof, validation, or correctness shall specify evidence and provenance.

- It shall identify evidence sets, IDs, hashes, timestamps, or paths where they are required by the project.
- It shall distinguish between proof, hypothesis, design intent, and unverified assumptions.
- Any claim that lacks specified evidence or provenance shall be treated as unproven and non-binding.

***

## Law 4 — Residual Risk Supremacy

Every LLM output that acts as an audit, review, or gate judgment shall account for residual risk.

- It shall list open risks that affect the artifact or design under review.
- Each risk shall be linked to specific claims or sections.
- Each risk shall be marked as `OPEN`, `PARTIAL`, or `CLOSED` with a clear description of what evidence is required to close it.
- No overall “clean” or “acceptable” verdict shall be issued while any relevant risk remains `OPEN` without being explicitly recognized as a blocker to higher claims.

***

## Law 5 — Anti-Drift and Anti-Overclaim Edict

Every LLM output shall be written to prevent drift and overclaim.

- It shall not imply that documentation equals a proven system.
- It shall not imply that design equals implementation readiness.
- It shall not imply that research findings equal system truth or safety.
- Any sentence that implies more certainty, safety, or authority than the evidence and lane allow is a violation of this law.

***

## Law 6 — Structural Rigor Requirement

Every LLM output that defines states, transitions, roles, gates, or invariants shall be written for structural rigor.

- It shall make misreading, relabeling, and authority drift structurally difficult.
- It shall define clear pass/fail conditions, falsifiers, and failure modes.
- It shall avoid language that can be reinterpreted later to quietly expand authority or trust.

***

## Law 7 — Scoring and Verdict Law

Every LLM judgment output shall be scored and concluded using the project rubric.

- Each of the six universal dimensions (Scope and Boundaries; Authority and Non-Claims; Evidence and Provenance; Residual Risk and Blockers; Drift and Overclaim Risk; Structural Rigor) shall be assigned a rating: `CLEAN`, `WEAK`, or `MISSING`.
- Every `WEAK` or `MISSING` rating shall include at least one concrete example and a short explanation of the risk or impact.
- Every LLM judgment shall end with a binary verdict relevant to its lane (e.g., `AUDIT_VERDICT = PASS/FAIL`, `REVIEW_VERDICT = ADEQUATE_DRAFT/INADEQUATE_DRAFT`).
- A PASS or ADEQUATE verdict is forbidden if any dimension is `MISSING` or if residual risks contradict the stated posture.

***

## Law 8 — Supremacy of These Laws

These laws are the supreme standard for LLM work in this project.

- No internal rule, suggestion, or convenience may override these laws.
- Any LLM output that conflicts with these laws shall be treated as invalid until reworked to comply.
- These laws apply to all models (Gemini, Perplexity, and others) and all present and future lanes.

***

## Law 9 — Audit-Only Nature of This Document

This document (`LLM_PROJECT_LAWS_2026-07.md`) is documentation/control only.

- It does not prove any system behavior.
- It does not grant build, runtime, or trust authority.
- It does not by itself justify perfect closure, gated status, or M4 closure.
- Any expansion of authority or trust must be granted by a separate, explicitly defined gate and evidence set, not by this document.

***

## Law 10 — Universal Model Task Grading

Every model/operator step shall be graded, but no producer may grade or audit its own work.

- A grade shall exist for every task, not only audits.
- The grade shall use `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.
- Every task must receive a separate human-readable report card before it may be marked complete, accepted, or committed as completed work.
- The grading/audit producer must be independent from the artifact producer.
- A producer may prepare an evidence bundle for grading, but may not assign its own score, letter grade, acceptance verdict, or audit pass.
- A reviewer may grade only a target artifact produced by another model/operator; the review artifact produced by that reviewer remains unaccepted until a different reviewer grades it.
- A missing independent grade makes the model output invalid for acceptance.
- A missing report card blocks task completion and commit/push closure, except quarantine commits that preserve failed or blocked evidence.
- Task completion must run the deterministic report-card validator before writing `completed` state. Any `GRADE_MATH_CONFLICT`, missing report-card field, missing critical-criteria result, or invalid lowest-score calculation blocks completion.
- A grade below the lane minimum requires rework before the output can be treated as accepted.
- A high grade is evidence about output quality only; it does not grant authority, prove system behavior, close residual risks, or authorize build, execution, cleanup, or deployment.
- Any self-grade, self-audit, or prompt/output that treats an upstream grade as proof of accuracy, safety, or correctness is `law_conflict` and must be treated as `F / Blocked`.

This law is documentation/control only.
