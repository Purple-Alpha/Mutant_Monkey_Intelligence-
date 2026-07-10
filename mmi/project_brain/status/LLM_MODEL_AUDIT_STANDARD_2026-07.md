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
7. Independent grade block, or `INDEPENDENT_GRADE_PENDING` if the audit output itself is the produced artifact awaiting separate review.
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

## Independent Grading Law

Every model/operator artifact must receive an independent grade before it can be accepted.

Producer boundary:

```text
NO SELF-GRADING
NO SELF-AUDIT
NO SELF-PASS
```

The artifact producer may prepare a `GRADE_REQUEST` evidence bundle, but may not assign its own score, letter grade, acceptance verdict, or audit pass. The grading/audit producer must be a separate model, reviewer, or Matt-approved operator from the producer that created or materially edited the artifact.

Required independent grade fields:

```text
ARTIFACT_PRODUCER_ID:
GRADER_ID:
GRADER_INDEPENDENCE_STATEMENT:
LANE:
TASK:
ARTIFACTS_GRADED:
AUTHORITY_CLASS:
TASK_RESULT: COMPLETE / PARTIAL / BLOCKED / INVALID
CRITERION_SCORES:
CRITICAL_CRITERIA:
LOWEST_CRITERION_SCORE:
LETTER_GRADE: A / B / C / D / F_BLOCKED
BLOCK_REASON_CATEGORIES:
LAW_CONFLICTS:
KNOWN_LIMITATIONS:
NEXT_DECISION_OR_LANE:
FORBIDDEN_ACTIONS_RECONFIRMED:
EVIDENCE_LIST:
```

Required criterion score scale:

```text
3 = clean within lane and evidence scope.
2 = adequate but materially weak or bounded by non-blocking limitations.
1 = poor, ambiguous, or materially incomplete but not zeroed.
0 = absent, contradicted, law-conflicting, or hard-gate blocked.
```

Critical criteria must include, at minimum:

- law compliance.
- authority discipline.
- evidence discipline.
- lane obedience.
- artifact hash binding.
- producer/grader independence.
- output completeness.

### A.5 Non-Averaging Lowest-Common-Denominator Grade Law

Overall letter grades must not be computed by averaging rubric scores.

Letter grades are determined strictly by the minimum criterion score:

- `A`: every criterion score is `3`.
- `B`: every criterion score is at least `2`, with no `1`s or `0`s.
- `C`: every criterion score is at least `1`, with no `0`s, and the pattern does not trigger a lane-specific downgrade.
- `D`: at least one criterion is `1`, no criterion is `0`, and the pattern fails the lane's `C` threshold.
- `F / Blocked`: any single criterion is `0`, or any hard-gate condition is triggered.

If any critical criterion is `0`, the artifact is `F / Blocked` regardless of all other scores. This rule overrides any prior or implied averaging logic; averaging is forbidden.

### A.6 Upstream Consumption Discipline Law

Upstream grades are invisible to execution.

Every lane prompt must include these constraints:

```text
You are forbidden from using an upstream quality grade (A-F or rubric scores) as proof of accuracy, safety, or correctness.
Before executing your own work, you must independently ingest and verify the raw evidence_list and artifact content; you may not rely on the upstream grade label.
```

Grade records may be read for orientation only. They may not be cited as evidence of correctness, safety, system behavior, runtime readiness, or authority. Any prompt or output that says or implies "we trust this because it has an A grade" is `law_conflict` and must be treated as `F / Blocked`.

### A.7 Cryptographic State Binding Law

Every grade is a snapshot bound to the exact state of the artifact at grading time.

The `EVIDENCE_LIST` for every grade must include:

- SHA-256 hash, or equivalent cryptographic hash, of the primary artifact file(s) being graded.
- Corresponding artifact path(s).
- Timestamp/date of hash capture.
- Grader identity.

A grade is valid only for that specific hash. If the artifact hash changes by even one character:

- the previous grade record is dead and invalid for the new state.
- any downstream lane that wishes to use the new state must treat it as a new artifact and obtain a new independent grade.

Using a grade whose hash does not match the current artifact is `law_conflict` and must be treated as `F / Blocked`.

### A.8 Three-Strikes Circuit Breaker Law

Consecutive `F / Blocked` grades must be tracked per artifact, or per tightly related artifact series undergoing iterative fixes.

If an artifact triggers `F / Blocked` three consecutive times for the same reason category, including but not limited to `overclaim`, `missing_evidence`, `dirty_or_unknown_state`, `lane_violation`, `hash_mismatch`, or `self_grading`, then:

- the automated MMI loop is severed for that artifact/topic.
- all automated transitions, including auto-routing to RESEARCH, AUDIT, DESIGN, or BUILD, halt.
- Matt intervention is mandatory to decide whether to continue, refactor, or abandon the artifact.
- no further automated work on that topic may resume without explicit Matt authorization.

Any pipeline that continues automated work after three consecutive Blocks for the same reason category is in `law_conflict`.

Project acceptance standard:

```text
MINIMUM ACCEPTABLE INDEPENDENT GRADE: A unless the active lane packet explicitly defines a stricter or different Matt-approved threshold.
B / C / D / F_BLOCKED: REWORK OR MATT DECISION REQUIRED
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
INDEPENDENT_GRADE:
GRADER_ID:
OUTPUT_CAPTURE_PATH:
```

Missed issues must be fed back into the model-specific prompt discipline.


## Universal Model Task Completion Grade

Every model task must be followed by an independent graded mark, regardless of lane.

This applies to:

- audits.
- research summaries.
- design/spec drafts.
- doc/control patches.
- review responses.
- handoff preparation.
- law/rubric updates.
- future build-design work if separately authorized.

Required task-completion grade request from the artifact producer:

```text
MODEL:
LANE:
TASK:
ARTIFACTS TOUCHED:
AUTHORITY CLASS:
TASK_RESULT: COMPLETE / PARTIAL / BLOCKED / INVALID
GRADE_STATUS: INDEPENDENT_GRADE_REQUIRED
PRODUCER_MUST_NOT_GRADE: YES
PRIMARY_ARTIFACT_HASHES:
EVIDENCE_LIST:
KNOWN_LIMITATIONS:
NEXT_DECISION_OR_LANE:
FORBIDDEN_ACTIONS_RECONFIRMED:
```

Minimum accepted independent task grade:

```text
A
```

Any completed model task with no independent grade must be treated as:

```text
MODEL_TASK_INVALID_MISSING_INDEPENDENT_GRADE
```

Any completed model task graded below the active lane's threshold must be treated as:

```text
MODEL_TASK_REQUIRES_REWORK_OR_MATT_DECISION
```

This grading requirement does not grant authority. A high grade does not prove system behavior, close risk, authorize build, authorize execution, authorize cleanup, or grant trust.

## Mandatory Master Prompt Law Block

Every lane prompt should include this invariant block, followed by exactly one lane-specific block for the active task.

```xml
<project_laws>
<grading_law>
- Every model/operator step must be graded by an independent reviewer before acceptance.
- No producer may grade, audit, pass, or accept its own work.
- Grades are artifacts about quality within a lane, not permissions to build or safety verdicts.
- A high grade does not prove system safety, runtime behavior, correctness, or readiness to build.
- Letter grades A-F are determined by the lowest criterion score; averaging is forbidden.
- A = all 3s; B = all >=2 with no 1s or 0s; C = all >=1 with no 0s and no downgrade trigger; D = at least one 1 and no 0s but not C; F / Blocked = any 0 or hard-gate violation.
- Upstream grades are invisible to execution and may not be used as proof of accuracy, safety, or correctness.
- Grades are cryptographically bound to artifact hashes; if a hash changes, the grade is dead.
- Three consecutive Blocks for the same reason category sever automated work until Matt intervenes.
</grading_law>

<evidence_law>
- Evidence or it did not happen.
- All claims must be tied to paths, commands, hashes, dates, and identities where applicable.
- Every grade evidence list must include the SHA-256 hash or equivalent cryptographic hash of the primary artifact(s), corresponding paths, timestamp/date, and grader identity.
</evidence_law>

<shared_lane_rules>
- You must stay in your declared lane.
- You must not claim safety, runtime correctness, system truth, build readiness, or closure unless the active lane, evidence, and laws explicitly allow it.
- You must include required output sections: Identity, Evidence_list, Risks_and_unknowns or Residual_risks, Boundaries, and lane-specific work output.
- Before using any upstream artifact, independently inspect the raw artifact content and evidence_list; do not rely on upstream grade labels.
- If you detect any law conflict, mark the work F / Blocked and explain the conflict.
</shared_lane_rules>
</project_laws>
```
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
## Audit Lane Attack Contract Binding

For audit-lane work, `LLM_AUDIT_LANE_ATTACK_CONTRACT_2026-07.md` is binding.

Audit posture:

```text
REVIEW THIS: NO
ATTACK THIS: YES
```

The model must assume the artifact is wrong, incomplete, overclaiming, stale, or authority-drifting until evidence proves otherwise within the accepted lane.

When auditing codebase specifications, command plans, scan plans, or safety/control artifacts, the audit must include adversarial checks where applicable:

- denial-of-service exposure.
- malformed input handling.
- evasion or bypass vectors.
- leakage paths.
- stale evidence or stale commit references.
- missing blocker states.
- silent skip paths.
- false-closure paths.

Self-grading is forbidden. No model may pass itself.
