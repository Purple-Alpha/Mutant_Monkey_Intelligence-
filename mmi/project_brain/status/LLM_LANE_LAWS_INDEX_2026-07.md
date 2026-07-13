# LLM Lane Laws Index - 2026-07

## Verdict

LLM LANE LAWS INDEX PREPARED - DOC/CONTROL ONLY

Authority class:

SPEC_PREP_ONLY / AUDIT_ONLY

This index binds the project-wide LLM review rubric and lane-specific LLM laws into the MMI law stack. It does not authorize build, execution, cleanup, deletion, scan execution, runtime wiring, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

## Mandatory Law Stack

All research, audit, review, judge, synthesis, design, or build-design LLM calls must obey these artifacts in order:

```text
1. Matt explicit decision
2. MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md
3. LLM_PROJECT_LAWS_2026-07.md
4. LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md
5. LLM_MODEL_AUDIT_STANDARD_2026-07.md
6. Lane-specific LLM law file
7. Current lane packet
8. Older routing docs and prior model outputs
```

If these documents conflict, the higher item in the stack wins.

## Universal Grading And Audit Discipline

Every project step, artifact, lane output, review, and build-design proposal requires independent grading before acceptance.

Binding rules:

- no model, operator, or lane may grade, audit, pass, or accept its own work.
- a reviewer may grade only a target artifact produced by another model/operator; the review artifact itself remains `INDEPENDENT_REVIEW_REQUIRED`.
- every completed task must have a report card with letter grade mark, rubric scores, criterion feedback, strengths, failures, and improvement targets.
- missing report card blocks task completion and commit/push closure, except quarantine commits that preserve failed or blocked evidence.
- every grade must use the non-averaging lowest-common-denominator rule in `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.
- every critical criterion must score `3`; any critical criterion below `3` is `F / Blocked`.
- every grade must be cryptographically bound to the exact artifact hash reviewed.
- every grade consumer must verify artifact hashes before relying on the grade record for routing, using `TOOL_RECOMPUTED` when tools are available or `HOST_ATTESTED` evidence bundles when tools are unavailable.
- unsealed host attestation is fallback evidence only; it cannot fully close critical hash-binding, evidence-discipline, or identity criteria unless upgraded to `HOST_ATTESTED_SEALED`.
- upstream grades are invisible to execution and may not be used as proof of accuracy, safety, correctness, readiness, or authority.
- three consecutive `F / Blocked` grades for the same artifact/topic and same reason category, tracked in `MMI_GRADING_STRIKE_LEDGER.json`, halt automated routing until Matt intervenes.

Any violation is `law_conflict` and must be treated as `F / Blocked`.

## Universal Prompt Construction Discipline

Every future MMI lane prompt must use the structured XML prompt shape in `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.

Required invariant pattern:

- one `<system_role>` block.
- one invariant `<project_laws>` block.
- exactly one lane-specific `<lane>` block.
- one `<context>` block containing artifact text, paths, hashes, diffs, or evidence.
- one `<instructions>` block that keeps work inside the declared lane.
- one `<output_format>` block with exact Markdown sections.
- one `<response_start>` block that preloads the correct first heading.

AUDIT prompts must use the high-intensity attack posture in `LLM_AUDIT_LAWS_2026-07.md`: ruthless, precise, evidence-bound gap exposure with mandatory `Identity`, `Attack_summary`, `Findings`, `Residual_risks`, `Evidence_list`, `Grade`, and `Boundaries` sections.

Prompts that drift into generic freeform prose, omit the lane boundary, omit build authorization state, omit evidence/hash requirements, omit the no-self-grade rule, or fail to state forbidden actions are invalid for accepted lane work.

## Artifact Set

| Artifact | Purpose | Required When |
|---|---|---|
| `LLM_PROJECT_LAWS_2026-07.md` | Project-wide binding laws for all LLM outputs | Every LLM research/review/audit/design call |
| `LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md` | Universal scoring rubric and required output structure | Every LLM judgment/review call |
| `LLM_AUDIT_LAWS_2026-07.md` | AUDIT lane laws | `LANE = AUDIT` |
| `LLM_BUILD_LAWS_2026-07.md` | BUILD lane laws | `LANE = BUILD` or build-design review |
| `LLM_DESIGN_LAWS_2026-07.md` | DESIGN lane laws | `LANE = DESIGN` |
| `LLM_RESEARCH_LAWS_2026-07.md` | RESEARCH lane laws | `LANE = RESEARCH` |

## Research Lane Discipline

Research outputs must distinguish:

```text
ESTABLISHED FACT
INFORMED HYPOTHESIS
SPECULATION
UNKNOWN
OPEN QUESTION
OPTIONAL_RECOMMENDATION_NOT_AUTHORITY
```

Research may inform later decisions. It does not prove system correctness, safety, production readiness, implementation readiness, clean closure, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

## Historical Model Trial Boundary — Superseded 2026-07-13

The following Gemini trial record is historical evidence only. Its instruction power and current routing authority are zero. Current model routing is controlled by `MMI_ACTIVE_SCOPE.md` and `MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md`.

```text
GEMINI STATUS AT THE TIME: ACTIVE TRIAL AUDIT MODEL
CURRENT STATUS: PARKED / HISTORICAL_ONLY
TRUST LEVEL: CONDITIONAL
ROLE: EXTERNAL CHALLENGE REVIEW
AUTHORITY: NONE
LANE OWNERSHIP POWER: NO
BUILD POWER: NO
CLEANUP POWER: NO
ACCEPTANCE POWER: NO
CURRENT INVOCATION POWER: NO
```

## Failure Handling

If an LLM output violates the universal laws or lane-specific laws, the only valid classification is:

```text
LLM_OUTPUT_INVALID_REQUIRES_REWORK
```

Invalid LLM output may be preserved as quarantine/advisory evidence, but it may not be treated as accepted review or authority.

## Final State

```text
LLM RESEARCH / REVIEW LAW STACK: INSTALLED
DOC/CONTROL ONLY
BUILD AUTHORITY: NO
EXECUTION AUTHORITY: NO
SCAN EXECUTION AUTHORITY: NO
CLEANUP AUTHORITY: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```
## Audit Lane Attack Contract

`LLM_AUDIT_LANE_ATTACK_CONTRACT_2026-07.md` is the required audit-lane contract for Gemini, Perplexity, Codex-as-reviewer, any other LLM, and any person/model performing audits.

It is audit-lane specific. It does not replace `LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md` for general multi-lane formatting.
