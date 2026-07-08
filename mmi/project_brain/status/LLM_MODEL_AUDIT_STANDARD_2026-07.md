# LLM Model Audit Standard - 2026-07

## Verdict

LLM MODEL AUDIT STANDARD PREPARED - DOC/CONTROL ONLY

Authority class:

SPEC_PREP_ONLY / AUDIT_ONLY

This standard applies to Gemini, Perplexity, Grok, ChatGPT, Codex-adjacent review outputs, and any future model used as an auditor, reviewer, judge, or research critic. It does not authorize build, execution, scan execution, cleanup, deletion, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

## Core Standard

Passable audits are failed audits for this project.

Every model audit must be designed to hunt for gaps, not rubber-stamp artifacts.

Required posture:

```text
ASSUME THE ARTIFACT IS WRONG, INCOMPLETE, OR OVERCLAIMING UNTIL PROVEN OTHERWISE.
```

The auditor must prioritize:

- missing fields.
- weak definitions.
- ambiguous authority.
- missing evidence.
- residual risks not tied to claims.
- drift or overclaim language.
- falsifiers and non-claims.
- provenance gaps.
- closure-blocking issues.

## Required Audit Output Shape

Every model audit must include:

1. Rubric table.
2. Gap list.
3. Drift / overclaim list.
4. Non-claims and falsifiers.
5. Residual-risk ledger.
6. Authority drift check.
7. Model self-grade.
8. Binary decision.

Any response that omits one of these sections is classified as:

```text
LLM_AUDIT_INVALID_REQUIRES_REWORK
```

## Required Rubric Dimensions

Each audit must rate these dimensions:

| Dimension | Required Rating |
|---|---|
| Authority boundaries | CLEAN / WEAK / MISSING |
| Residual risk linkage | CLEAN / WEAK / MISSING |
| Evidence and provenance | CLEAN / WEAK / MISSING |
| Non-claims and falsifiers | CLEAN / WEAK / MISSING |
| Drift and overclaim control | CLEAN / WEAK / MISSING |
| Structural rigor | CLEAN / WEAK / MISSING |
| Model-role obedience | CLEAN / WEAK / MISSING |
| Output completeness | CLEAN / WEAK / MISSING |

Every WEAK or MISSING rating must include:

- exact section or quote.
- risk impact.
- required patch.

If a model marks all dimensions CLEAN, it must still explain why no plausible gap survived review.

## Binary Audit Decision

Allowed decisions:

```text
AUDIT_RESULT = FAIL_PATCH_REQUIRED
AUDIT_RESULT = PASS_NO_PATCH_REQUIRED
```

PASS is forbidden if:

- any required section is missing.
- any dimension is MISSING.
- a relevant residual risk is OPEN but not explicitly listed as a blocker to higher claims.
- the audit uses unbounded praise such as "perfect", "zero-gap", "fully safe", "ready", or "trusted" without strict scope limitation.
- the audit implies authority, execution, closure, or trust beyond the lane.

When in doubt:

```text
AUDIT_RESULT = FAIL_PATCH_REQUIRED
```

## Model Self-Grade

Every model audit must grade itself:

| Self-Grade Field | Score |
|---|---:|
| Law compliance | 0-100 |
| Authority discipline | 0-100 |
| Evidence discipline | 0-100 |
| Residual-risk discipline | 0-100 |
| Overclaim discipline | 0-100 |
| Output completeness | 0-100 |
| Usefulness | 0-100 |

Grade bands:

```text
A: 95-100
A-: 90-94
B: 80-89
C: 70-79
FAIL: <70
```

Project acceptance standard:

```text
MINIMUM ACCEPTABLE AUDIT GRADE: A-
ANY B-GRADE AUDIT: REWORK REQUIRED
```

## Model-Specific Trial Discipline

Every audit must identify:

- model name.
- model version if available.
- prompt version or law packet version.
- artifact reviewed.
- lane.
- declared role.
- forbidden actions.
- output artifact path if captured.

Gemini-specific current state:

```text
GEMINI STATUS: ACTIVE TRIAL AUDIT MODEL
TRUST LEVEL: CONDITIONAL
ROLE: EXTERNAL CHALLENGE REVIEW
AUTHORITY: NONE
ACCEPTANCE POWER: NO
BUILD POWER: NO
CLEANUP POWER: NO
LANE OWNERSHIP POWER: NO
```

Other models may be used for calibration, but not as a crutch for individual audit acceptance unless separately authorized.

## Anti-Praise Rule

Praise-heavy language is not evidence.

Forbidden or suspect phrases unless tightly bounded:

- "perfectly complies"
- "zero-gap"
- "ceiling-complete" without scope limiter
- "fully safe"
- "ready" without lane qualifier
- "trusted"
- "clean" without residual-risk caveat

Preferred replacements:

- "no material gaps identified within reviewed scope"
- "no authority drift detected in this review"
- "adequate for doc/control acceptance only"
- "residual risks remain open and block higher claims"

## Audit Trail Observability

Every model audit must be tracked as an auditable event:

```text
MODEL:
MODEL_VERSION:
PROMPT_VERSION:
RUBRIC_VERSION:
LANE:
ARTIFACT_REVIEWED:
AUDIT_RESULT:
ISSUE_COUNT:
ISSUE_CLASSES:
MISSED_ISSUES_LATER_FOUND:
SELF_GRADE:
OUTPUT_CAPTURE_PATH:
```

Missed issues must be fed back into the model-specific prompt discipline.


## Universal Model Task Completion Grade

Every model task must end with a graded mark, regardless of lane.

This applies to:

- audits.
- research summaries.
- design/spec drafts.
- doc/control patches.
- review responses.
- handoff preparation.
- law/rubric updates.
- future build-design work if separately authorized.

Required task-completion grade:

```text
MODEL:
LANE:
TASK:
ARTIFACTS TOUCHED:
AUTHORITY CLASS:
TASK_RESULT: COMPLETE / PARTIAL / BLOCKED / INVALID
SELF_GRADE: A / A- / B / C / FAIL
NUMERIC_SCORE: 0-100
LAW_COMPLIANCE_SCORE: 0-100
AUTHORITY_DISCIPLINE_SCORE: 0-100
EVIDENCE_DISCIPLINE_SCORE: 0-100
OVERCLAIM_DISCIPLINE_SCORE: 0-100
RESIDUAL_RISK_DISCIPLINE_SCORE: 0-100
OUTPUT_COMPLETENESS_SCORE: 0-100
KNOWN_LIMITATIONS:
NEXT_DECISION_OR_LANE:
FORBIDDEN_ACTIONS_RECONFIRMED:
```

Minimum accepted task grade:

```text
A- / 90
```

Any completed model task graded below A- must be treated as:

```text
MODEL_TASK_REQUIRES_REWORK
```

Any completed model task that omits the grade block must be treated as:

```text
MODEL_TASK_INVALID_MISSING_GRADE
```

This grading requirement does not grant authority. A high grade does not prove system behavior, close risk, authorize build, authorize execution, authorize cleanup, or grant trust.
## Final State

```text
MODEL AUDIT STANDARD: INSTALLED
DOC/CONTROL ONLY
BUILD AUTHORITY: NO
EXECUTION AUTHORITY: NO
SCAN EXECUTION AUTHORITY: NO
CLEANUP AUTHORITY: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```