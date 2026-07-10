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
7. Independent grade block for the target artifact, plus `REVIEW_ARTIFACT_ACCEPTANCE_STATUS: INDEPENDENT_REVIEW_REQUIRED` for the audit output currently being produced.
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

Three-object separation is mandatory:

```text
TARGET_ARTIFACT: the artifact being reviewed or graded.
REVIEW_ARTIFACT: the audit/review/grade output produced by the reviewer.
REVIEW_ARTIFACT_GRADE: a later independent grade of the REVIEW_ARTIFACT by a different reviewer.
```

An auditor may grade a `TARGET_ARTIFACT` only when the auditor did not create or materially edit that target artifact. The auditor must not grade the `REVIEW_ARTIFACT` it is currently producing. Every `REVIEW_ARTIFACT` must end with:

```text
REVIEW_ARTIFACT_ACCEPTANCE_STATUS: INDEPENDENT_REVIEW_REQUIRED
REVIEW_ARTIFACT_MAY_SELF_GRADE: NO
```

If a prompt asks a model to grade the artifact it is currently producing, the prompt is invalid. If an output assigns an acceptance grade to itself, the output is `law_conflict` and must be treated as `F / Blocked`.

Required independent grade fields:

```text
TARGET_ARTIFACT_PRODUCER_ID:
TARGET_ARTIFACT_PRODUCER_EVIDENCE:
GRADER_ID:
GRADER_IDENTITY_EVIDENCE:
GRADER_INDEPENDENCE_STATEMENT:
GRADER_DID_NOT_CREATE_OR_EDIT_TARGET: YES / NO / UNKNOWN
LANE:
TASK:
ARTIFACTS_GRADED:
AUTHORITY_CLASS:
TASK_RESULT: COMPLETE / PARTIAL / BLOCKED / INVALID
CRITERION_SCORES:
CRITERION_FEEDBACK:
CRITICAL_CRITERIA:
LOWEST_CRITERION_SCORE:
LETTER_GRADE: A / B / C / D / F_BLOCKED
LETTER_GRADE_MARK:
TEACHING_SUMMARY:
WHAT_WAS_PERFECT:
WHAT_WAS_GOOD:
WHAT_WAS_WEAK:
WHAT_FAILED:
IMPROVEMENT_TARGETS:
BLOCK_REASON_CATEGORIES:
LAW_CONFLICTS:
KNOWN_LIMITATIONS:
NEXT_DECISION_OR_LANE:
FORBIDDEN_ACTIONS_RECONFIRMED:
EVIDENCE_LIST:
HOST_EVIDENCE_BUNDLE:
VERIFICATION_MODE: TOOL_RECOMPUTED / HOST_ATTESTED / NOT_VERIFIED
REVIEW_ARTIFACT_ACCEPTANCE_STATUS: INDEPENDENT_REVIEW_REQUIRED
REVIEW_ARTIFACT_MAY_SELF_GRADE: NO
```

Identity evidence must be concrete and must come from outside the model's free-text claim wherever possible. Plaintext names alone are not sufficient. At minimum, the grade evidence must include the captured model/operator identity available in the tool transcript, output capture path, commit author/committer where applicable, local operator identity where available, and the evidence used to prove the grader did not create or materially edit the target artifact. If producer/grader separation is `UNKNOWN`, the grade is `F / Blocked`.

When the reviewer has no shell/tool access, the prompt must provide a host evidence bundle produced by Codex, Matt, or another authorized host operator. The model must not pretend it generated that evidence itself.

Required criterion score scale:

```text
3 = PERFECT / CLEAN: fully satisfies the criterion within lane and evidence scope.
2 = GOOD / ADEQUATE: useful and mostly correct, but materially weak, incomplete, or bounded.
1 = WEAK / POOR: present but ambiguous, unreliable, or materially incomplete.
0 = FAILED / BLOCKED: absent, contradicted, law-conflicting, self-grading, or hard-gate blocked.
```

Every criterion must include teaching feedback:

```text
criterion:
score: 0 / 1 / 2 / 3
quality_mark: PERFECT / GOOD / WEAK / FAILED
what_worked:
what_failed_or_was_missing:
improvement_target:
```

The letter grade must be visible as both a machine field and a human teaching mark. A blocked artifact must still receive a clear letter mark, for example:

```text
LETTER_GRADE: F_BLOCKED
LETTER_GRADE_MARK: F / Blocked
TEACHING_SUMMARY: Strong structure, but failed acceptance because evidence discipline and line-reference accuracy were below critical threshold.
```

The grade output must explicitly separate positive performance from failure causes. A grade that only says `F_BLOCKED` without explaining what was done well and what failed is incomplete.

Critical criteria must include, at minimum:

- law compliance.
- authority discipline.
- evidence discipline.
- lane obedience.
- artifact hash binding.
- producer/grader independence.
- output completeness.

Every critical criterion must score `3` for the artifact to receive an accepted grade. Any critical criterion scored `0`, `1`, or `2` makes the artifact `F / Blocked`; weak critical compliance is not acceptable for this project.

### A.5 Non-Averaging Lowest-Common-Denominator Grade Law

Overall letter grades must not be computed by averaging rubric scores.

Letter grades are determined strictly by the minimum criterion score:

- `A`: every criterion score is `3`.
- `B`: every criterion score is at least `2`, with no `1`s or `0`s.
- `C`: every criterion score is at least `1`, with no `0`s, and the pattern does not trigger a lane-specific downgrade.
- `D`: at least one criterion is `1`, no criterion is `0`, and the pattern fails the lane's `C` threshold.
- `F / Blocked`: any single criterion is `0`, or any hard-gate condition is triggered.

If any critical criterion is less than `3`, the artifact is `F / Blocked` regardless of all other scores. This rule overrides any prior or implied averaging logic; averaging is forbidden.

Grade consistency is mandatory:

- If `critical_criteria_results` lists any critical criterion below `3`, `LETTER_GRADE` must be `F_BLOCKED`.
- If `LOWEST_CRITERION_SCORE` is `0`, `LETTER_GRADE` must be `F_BLOCKED`.
- If `LETTER_GRADE`, `LETTER_GRADE_MARK`, `CRITERION_SCORES`, `CRITICAL_CRITERIA`, and `critical_criteria_results` contradict each other, the report card is invalid and must be treated as `F / Blocked`.
- A report card that says `lowest_score_rule_applied: YES` but assigns a non-blocking grade despite a critical criterion below `3` is `law_conflict`.
- Contradictory grade math must be classified as `GRADE_MATH_CONFLICT`.

### A.6 Upstream Consumption Discipline Law

Upstream grades are invisible to execution.

Every lane prompt must include these constraints:

```text
You are forbidden from using an upstream quality grade (A-F or rubric scores) as proof of accuracy, safety, or correctness.
Before executing your own work, you must independently ingest and verify the raw evidence_list and artifact content; you may not rely on the upstream grade label.
Before consuming a grade, you must verify artifact state by one of these modes:
1. TOOL_RECOMPUTED: recompute the current artifact hash using an available shell/tool and compare it to the grade evidence_list.
2. HOST_ATTESTED: if shell/tool access is unavailable, inspect a host evidence bundle containing the host-generated command, output, timestamp, artifact path, and operator identity.
3. NOT_VERIFIED: if neither tool recomputation nor host attestation is available, the grade is invalid for acceptance.
```

Grade records may be read for orientation only. They may not be cited as evidence of correctness, safety, system behavior, runtime readiness, or authority. Any prompt or output that says or implies "we trust this because it has an A grade" is `law_conflict` and must be treated as `F / Blocked`.

### A.7 Cryptographic State Binding Law

Every grade is a snapshot bound to the exact state of the artifact at grading time.

The `EVIDENCE_LIST` for every grade must include:

- SHA-256 hash, or equivalent cryptographic hash, of the primary artifact file(s) being graded.
- Corresponding artifact path(s).
- Timestamp/date of hash capture.
- Grader identity.
- Hash verification mode: `TOOL_RECOMPUTED`, `HOST_ATTESTED`, or `NOT_VERIFIED`.
- Hash recomputation command or host-attestation command.
- Hash comparison result: `MATCH`, `MISMATCH`, or `NOT_VERIFIED`.
- Host evidence bundle path when `HOST_ATTESTED` is used.

A grade is valid only for that specific hash. If the artifact hash changes by even one character:

- the previous grade record is dead and invalid for the new state.
- any downstream lane that wishes to use the new state must treat it as a new artifact and obtain a new independent grade.

Using a grade whose hash does not match the current artifact is `law_conflict` and must be treated as `F / Blocked`. A grade with `NOT_VERIFIED` hash status is invalid for acceptance.

`HOST_ATTESTED` is a fallback evidence mode, not an equivalent replacement for `TOOL_RECOMPUTED`.

Host attestation levels:

```text
HOST_ATTESTED_UNSEALED: single-host/operator markdown evidence; useful for orientation but cannot fully close critical hash-binding or identity criteria.
HOST_ATTESTED_SEALED: host evidence bundle is bound to immutable commit state, includes its own bundle hash, records clean/dirty repo status, names target hashes, includes freshness timestamp, and is either signed by a Matt-approved operator or independently cross-attested by a second non-producing host/operator.
TOOL_RECOMPUTED: reviewer directly recomputed with available tools.
```

Acceptance rules:

- `HOST_ATTESTED_UNSEALED` must be marked as a limitation and cannot score `artifact hash binding`, `producer/grader independence`, or `evidence discipline` above `2`.
- `HOST_ATTESTED_SEALED` may score critical criteria as `3` only if the seal, freshness, target artifact hashes, bundle hash, producer identity evidence, and independent attestation are present.
- A stale host evidence bundle, missing bundle hash, dirty unclassified repo state, missing freshness timestamp, or single-operator unsealed identity claim is `F / Blocked` for acceptance.
- Any output that treats host-attested evidence as absolute truth, rather than fallback evidence with explicit limitations, is `law_conflict`.

### A.8 Three-Strikes Circuit Breaker Law

Consecutive `F / Blocked` grades must be tracked per artifact, or per tightly related artifact series undergoing iterative fixes.

The authoritative strike ledger path is:

```text
mmi/project_brain/status/MMI_GRADING_STRIKE_LEDGER.json
```

Every `F / Blocked` grade must append or update a ledger entry with:

```text
artifact_key:
artifact_path:
artifact_hash:
artifact_series_id:
block_reason_category:
grader_id:
grade_artifact_path:
timestamp:
consecutive_count:
next_allowed_state:
```

If an artifact triggers `F / Blocked` three consecutive times for the same reason category, including but not limited to `overclaim`, `missing_evidence`, `dirty_or_unknown_state`, `lane_violation`, `hash_mismatch`, or `self_grading`, then:

- the automated MMI loop is severed for that artifact/topic.
- all automated transitions, including auto-routing to RESEARCH, AUDIT, DESIGN, or BUILD, halt.
- Matt intervention is mandatory to decide whether to continue, refactor, or abandon the artifact.
- no further automated work on that topic may resume without explicit Matt authorization.

Any pipeline that continues automated work after three consecutive Blocks for the same reason category is in `law_conflict`. If the strike ledger is missing, stale, unreadable, or not checked before routing, automated routing is blocked until the ledger is repaired or Matt explicitly authorizes a one-off manual lane.

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

Every model/operator task must also receive a human-readable report card before the task may be marked completed, accepted, committed as completed work, or used to route the next lane.

This applies to:

- audits.
- research summaries.
- design/spec drafts.
- doc/control patches.
- review responses.
- handoff preparation.
- law/rubric updates.
- future build-design work if separately authorized.

Required completion gate:

```text
REPORT_CARD_REQUIRED: YES
REPORT_CARD_STATUS: PRESENT / MISSING / INDEPENDENT_REVIEW_REQUIRED
TASK_COMPLETION_ALLOWED: YES / NO
COMMIT_ALLOWED: YES / NO
```

Rules:

- `REPORT_CARD_STATUS: MISSING` means `TASK_COMPLETION_ALLOWED: NO` and `COMMIT_ALLOWED: NO`, except for quarantine commits whose only purpose is preserving failed or blocked evidence.
- The report card must be produced by a separate reviewer from the artifact producer.
- The report card must include a visible letter grade mark, rubric scores, criterion feedback, what was done well, what failed, and improvement targets.
- A task cannot be marked `completed` in `tasks.json` unless its output artifact or closeout record names the report card path, reviewer identity, grade mark, and acceptance status.
- `scripts/complete_task.py` must validate the report card with `scripts/validate_report_card.py` before writing `completed` state.
- `scripts/validate_report_card.py` is the deterministic grade-math enforcer. If the validator reports `GRADE_MATH_CONFLICT`, `REPORT_CARD_REQUIRED`, missing critical criteria, missing rubric scores, or missing required report-card fields, task completion is blocked.
- A commit that closes or completes work must include the report card artifact or explicitly classify the work as `QUARANTINE / BLOCKED_EVIDENCE_ONLY`.

Required task-completion grade request from the artifact producer:

```text
MODEL:
LANE:
TASK:
ARTIFACTS TOUCHED:
AUTHORITY CLASS:
TASK_RESULT: COMPLETE / PARTIAL / BLOCKED / INVALID
GRADE_STATUS: INDEPENDENT_GRADE_REQUIRED
REPORT_CARD_REQUIRED: YES
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

Every lane prompt must be written in the structured XML style below, followed by exactly one lane-specific `<lane>` block, one `<context>` block, one `<instructions>` block, one `<output_format>` block, and one `<response_start>` block for the active task.

Freeform prompts are invalid for accepted MMI lane work unless Matt explicitly authorizes a one-off exception. The prompt must be high-intensity, exact, lane-bounded, evidence-bound, and hostile to gaps, drift, blind spots, weak assumptions, and overclaims. Aggressive wording is required for AUDIT prompts and allowed for other lanes when it improves rigor, but severity must remain evidence-bound.

Mandatory prompt sections:

```text
system_role
project_laws
lane
context
instructions
output_format
response_start
```

The `<project_laws>` block must remain invariant across lanes except for later Matt-approved law amendments. The `<lane>` block is the only section that changes lane identity, lane role, allowed actions, forbidden actions, scope, and task target.

```xml
<system_role>
Act as a ruthlessly precise, hyper-vigilant operator for a high-assurance, multi-model project.
Your mandate is to expose flaws, gaps, blind spots, weak assumptions, unresolved risks, and overclaims within the declared lane.
You operate strictly within the active lane and the project's grading, evidence, and lane laws.
</system_role>

<project_laws>
<grading_law>
- Every model/operator step must be graded by an independent reviewer before acceptance.
- No producer may grade, audit, pass, or accept its own work.
- An auditor may grade only the target artifact produced by someone else; the audit artifact it produces remains INDEPENDENT_REVIEW_REQUIRED.
- Grades are artifacts about quality within a lane, not permissions to build or safety verdicts.
- A high grade does not prove system safety, runtime behavior, correctness, or readiness to build.
- Letter grades A-F are determined by the lowest criterion score; averaging is forbidden.
- A = all 3s; B = all non-critical criteria >=2 with no 1s or 0s and all critical criteria = 3; C = all non-critical criteria >=1 with no 0s, all critical criteria = 3, and no downgrade trigger; D = at least one non-critical 1 and no 0s but not C; F / Blocked = any 0, any critical criterion below 3, or any hard-gate violation.
- Upstream grades are invisible to execution and may not be used as proof of accuracy, safety, or correctness.
- Grades are cryptographically bound to artifact hashes; if a hash changes, the grade is dead.
- Tool-restricted reviewers must use HOST_ATTESTED evidence bundles instead of hallucinating shell, git, or hash operations.
- Three consecutive Blocks for the same reason category in MMI_GRADING_STRIKE_LEDGER.json sever automated work until Matt intervenes.
</grading_law>

<evidence_law>
- Evidence or it did not happen.
- All claims must be tied to paths, commands, hashes, dates, and identities where applicable.
- Every grade evidence list must include the SHA-256 hash or equivalent cryptographic hash of the primary artifact(s), corresponding paths, timestamp/date, grader identity, identity evidence, verification mode, hash verification method, and hash comparison result.
</evidence_law>

<shared_lane_rules>
- You must stay in your declared lane.
- You must not claim safety, runtime correctness, system truth, build readiness, or closure unless the active lane, evidence, and laws explicitly allow it.
- You must include required output sections: Identity, Evidence_list, Risks_and_unknowns or Residual_risks, Boundaries, and lane-specific work output.
- Before using any upstream artifact, independently inspect the raw artifact content and evidence_list; do not rely on upstream grade labels.
- Before using any grade, verify artifact hashes by TOOL_RECOMPUTED or HOST_ATTESTED mode and check MMI_GRADING_STRIKE_LEDGER.json for active three-strike blocks.
- If you detect any law conflict, mark the work F / Blocked and explain the conflict.
</shared_lane_rules>
</project_laws>

<lane>
<name>[AUDIT | DESIGN | RESEARCH | BUILD | OTHER_APPROVED_LANE]</name>
<role>[lane-specific role]</role>
<allowed>
[lane-specific allowed actions]
</allowed>
<forbidden>
[lane-specific forbidden actions]
</forbidden>
<scope>
[target artifact, commit, paths, authorization state, required output path, and task boundary]
</scope>
</lane>

<context>
[Insert full artifact text, diff, paths, hashes, prior relevant laws, and evidence required for the lane.]
</context>

<instructions>
Using the <project_laws>, <lane>, and <scope> above, perform only the declared lane task.
Tie claims to evidence. Mark unknowns instead of inventing facts. If a law conflict is detected, stop escalation by marking F / Blocked.
</instructions>

<output_format>
Produce Markdown with the required lane-specific sections, including Identity, Evidence_list, Grade or grade-request status, and Boundaries.
</output_format>

<response_start>
[Prefill the first required heading so the model starts in the correct structure.]
</response_start>
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
