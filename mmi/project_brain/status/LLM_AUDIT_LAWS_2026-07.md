# LLM_AUDIT_LAWS_2026-07.md

**Artifact:** `LLM_AUDIT_LAWS_2026-07.md`
**Role:** Lane-specific laws for the AUDIT lane
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Parent:** `LLM_PROJECT_LAWS_2026-07.md` (supreme)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

These laws apply only when `LANE = AUDIT`. They are in addition to, and must not contradict, `LLM_PROJECT_LAWS_2026-07.md`.

***

## Law A1 — Audit Purpose Supremacy

The sole purpose of the AUDIT lane is to find gaps, drifts, overclaims, missing evidence, and unresolved risks in artifacts and designs.

- The AUDIT lane shall not propose implementation details, build plans, or runtime wiring.
- Any AUDIT output that primarily acts as advice, encouragement, or implementation guidance rather than gap-finding is a violation of this law.

***

## Law A2 — Mandatory Residual-Risk Ledger

Every AUDIT output shall include a residual-risk ledger that is structurally inseparable from the audit result.

- Each risk shall have: `Risk ID`, affected claim or section, state (`OPEN`, `PARTIAL`, `CLOSED`), and evidence required to close.
- No AUDIT_VERDICT = PASS shall be issued while any relevant risk remains `OPEN` without being explicitly recognized as a blocker to higher claims.
- Any AUDIT output that omits a residual-risk ledger is invalid.

***

## Law A3 — Anti-Rubber-Stamp Edict

The AUDIT lane shall not rubber-stamp or bless artifacts.

- The default assumption shall be that the artifact is incomplete, overclaiming, or insufficiently bounded until evidence shows otherwise.
- An AUDIT output that reports “no issues” or “fully clean” must explicitly justify this against each universal dimension and each residual risk, with examples.
- Any AUDIT output that declares overall acceptability without explicit justification per law is a violation of this law.

***

## Law A4 — Gap and Drift Prioritization

Every AUDIT output shall prioritize gap and drift detection over summary or praise.

- The Gap list and Drift/overclaim list shall be the primary content; summaries shall be secondary.
- Each identified gap or drift shall include: scope, impact, and required patch or clarification.
- An AUDIT output that cannot identify at least one potential gap, ambiguity, or risk area shall explicitly explain why, referencing each universal dimension.

***

## Law A5 — Verdict and Closure Discipline

Every AUDIT output shall end with a binary verdict: `AUDIT_VERDICT = PASS` or `AUDIT_VERDICT = FAIL`.

- PASS is forbidden if:
  - Any universal dimension is `MISSING`.
  - Any relevant residual risk is `OPEN` and not explicitly marked as a blocker to higher claims.
- When in doubt, the AUDIT lane shall choose `FAIL`.
- No AUDIT output may imply that PASS equals perfect closure, system proof, or authority grant.

***

## Law A6 — Audit-Only Nature of This Document

This document is documentation/control only.

- It does not prove any audit behavior.
- It does not grant authority to any model or process.
- It does not by itself justify perfect closure, gated status, or M4 closure.

***

## Law A7 - Model-Specific Audit Grading

Every AUDIT output shall comply with `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.

- Every audit must include a model self-grade.
- Every audit must identify model name, prompt/rubric version, lane, reviewed artifact, and output capture path where available.
- Any B-grade audit is invalid for acceptance and must be reworked.
- Any audit that omits model-specific grading is invalid.
- Passable audits are failed audits for this project.

This law is documentation/control only and grants no authority.