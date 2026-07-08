Here is a project-wide, plug-and-play rubric spec you can use for all current and future lanes to keep everything at the same highest standard.

***

# LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md

**Artifact:** `LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md`
**Role:** Project-wide quality and audit rubric for all LLM outputs
**Authority class:** SPEC_PREP_ONLY / AUDIT_ONLY
**Scope:** All lanes (AUDIT, BUILD-DESIGN, RESEARCH, plus any future lane)

Accepted spec does not equal proven system.
Good documentation does not equal closed risk.
Coverage does not equal closure.
Confidence does not equal authority. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

This rubric defines how every LLM in the project must judge and structure its own outputs so that “passable” work cannot silently become “accepted.” [twine](https://www.twine.net/blog/llm-evaluation-rubrics/)

***

## 1. Purpose and global scope

- This rubric is mandatory for all LLM judge/review/audit calls across the project. [promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/)
- It applies to every lane (AUDIT, BUILD-DESIGN, RESEARCH, and any new lane you define) and every model (Gemini, Perplexity, others). [galtea](https://galtea.ai/blog/llm-as-a-judge-prompts-templates-rubrics-and-best-practices)
- It does not grant build authority, runtime authority, trust, or closure by itself; it is a documentation/control artifact only. [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)

If an LLM output deviates from this rubric, the result is invalid and must be treated as FAILED review. [twine](https://www.twine.net/blog/llm-evaluation-rubrics/)

***

## 2. Lane declaration (required for every call)

Every LLM call that produces a judgment or review must declare a lane: [galtea](https://galtea.ai/blog/llm-as-a-judge-prompts-templates-rubrics-and-best-practices)

- `LANE = AUDIT`
  - Goal: Find gaps, drifts, overclaims, missing evidence, and residual risks in an artifact or design.
  - Prohibited: Implementation plans, “this is ready” statements, or authority grants. [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)

- `LANE = BUILD-DESIGN`
  - Goal: Propose or refine designs/specs consistent with guardrails and non-claims.
  - Prohibited: Treating design as approved or build-ready without a separate gate. [perplexity](https://www.perplexity.ai/search/20236176-c14e-46bc-b247-41ec30bba146)

- `LANE = RESEARCH`
  - Goal: Gather and synthesize information, map options, highlight uncertainty and open questions.
  - Prohibited: Asserting system correctness, safety, or closure. [perplexity](https://www.perplexity.ai/hub/blog)

- `LANE = OTHER_<NAME>` (for future lanes)
  - Must define goal, allowed actions, and explicit prohibitions before use. [twine](https://www.twine.net/blog/llm-evaluation-rubrics/)

No LLM call may run in an undefined lane.

***

## 3. Universal rubric dimensions

Every LLM judgment output, regardless of lane, must score the artifact against these six dimensions: [confident-ai](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)

1. **Scope and boundaries**
   - Does the artifact clearly state what it covers and what it does NOT cover (system, environment, authority, evidence)? [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)

2. **Authority and non-claims**
   - Does it separate documentation/control from build, runtime, and trust authority?
   - Are explicit non-claims present (what is not proved, what cannot be inferred)? [perplexity](https://www.perplexity.ai/search/ed76758b-1afd-4c4e-a22a-26fe09ba011b)

3. **Evidence and provenance**
   - Are evidence sets, IDs, hashes, timestamps, and paths specified where needed?
   - Is it clear what counts as proof versus hypothesis or design intent? [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)

4. **Residual risk and blockers**
   - Are open risks listed, linked to specific claims, and clearly blocking higher-level closure or authority? [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)

5. **Drift and overclaim risk**
   - Does any language imply more certainty, safety, or readiness than the documented evidence supports? [promptbuilder](https://promptbuilder.cc/blog/prompt-engineering-best-practices-2025)

6. **Structural rigor**
   - Are states, transitions, roles, gates, and invariants defined so misreading or authority drift becomes structurally hard? [perplexity](https://www.perplexity.ai/search/d23d78fd-deee-43f6-97e2-9dea5a662d7b)

These dimensions are universal; additional lane-specific dimensions can be added but not substituted. [confident-ai](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)

***

## 4. Scoring scale

For each dimension, every LLM must assign one of these ratings: [teaching.uic](https://teaching.uic.edu/cate-teaching-guides/assessment-grading-practices/rubrics/)

- `CLEAN` – Meets the standard; no material issues.
- `WEAK` – Present but underspecified, ambiguous, or missing guardrails.
- `MISSING` – Absent, misleading, or contradicts the lane’s intent.

Rules:
- Each dimension must have a rating and a one-sentence rationale. [galtea](https://galtea.ai/blog/llm-as-a-judge-prompts-templates-rubrics-and-best-practices)
- Every `WEAK` or `MISSING` rating must include at least one concrete example (quote or section reference) and a short explanation of the risk or impact. [confident-ai](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)

***

## 5. Required output structure (for all models)

Every LLM review/judgment output must follow this shape exactly: [promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/)

### Section 1 – Rubric table

A simple table listing: dimension, rating (CLEAN/WEAK/MISSING), one-sentence rationale. [promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/)

### Section 2 – Gap list

Numbered items describing concrete gaps: [spkaa](https://www.spkaa.com/blog/best-practices-for-reviewing-and-auditing-llm-generated-code)
For each gap:
- `Gap ID`
- Dimension affected
- Description (what is missing or unclear)
- Scope/impact (where it matters)
- Required patch or clarification

### Section 3 – Drift / overclaim list

List any sentences or sections that: [promptbuilder](https://promptbuilder.cc/blog/prompt-engineering-best-practices-2025)
- Overstate certainty or safety.
- Imply authority, closure, or “ready” status beyond the defined lane.

For each, the model must:
- Quote or identify the text.
- Suggest a bounded rewrite (adding non-claims, qualifiers, or explicit limits).

### Section 4 – Residual-risk ledger (AUDIT lane only)

If `LANE = AUDIT`, the output must include a mini residual-risk ledger: [launchdarkly](https://launchdarkly.com/blog/llm-observability/)
- `Risk ID`
- Affected claim or artifact section
- State: `OPEN`, `PARTIAL`, `CLOSED`
- Evidence required to move from OPEN/PARTIAL to CLOSED

No “overall clean” statement is allowed if any relevant risk remains OPEN without an explicit blocker. [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)

### Section 5 – Binary verdict

The model must end with: [watershed](https://watershed.com/blog/a-practical-framework-for-llm-system-evaluations-for-multi-step-processes)

- `AUDIT_VERDICT = PASS` or `AUDIT_VERDICT = FAIL` (for AUDIT lane), or
- `REVIEW_VERDICT = ADEQUATE_DRAFT` or `REVIEW_VERDICT = INADEQUATE_DRAFT` (for other lanes).

Rules:
- PASS / ADEQUATE_DRAFT is allowed only if:
  - No dimension is `MISSING`.
  - All critical residual risks are either CLOSED or explicitly recognized as blockers to higher claims. [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)
- If in doubt, the model must choose FAIL / INADEQUATE_DRAFT.

***

## 6. Universal judge prompt skeleton

This is the generic prompt you can reuse for any LLM and any lane:

> **Role:** You are a perfection-standard LLM auditor operating in the `<LANE>` lane. Your job is to apply `LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07` to the given artifact/output. You must prioritize finding gaps, drifts, overclaims, missing evidence, and residual risks over being polite or optimistic. [promptbuilder](https://promptbuilder.cc/blog/prompt-engineering-best-practices-2025)
>
> **Inputs:**
> - `LANE` = `<AUDIT | BUILD-DESIGN | RESEARCH | OTHER_<NAME>>`
> - Artifact or output text
> - Any residual-risk ledger or evidence context, if available
>
> **Tasks:**
> 1. Evaluate the artifact against all six universal rubric dimensions. [twine](https://www.twine.net/blog/llm-evaluation-rubrics/)
> 2. Assign CLEAN/WEAK/MISSING to each dimension with a brief rationale.
> 3. Produce the required sections: Rubric table, Gap list, Drift/overclaim list, Residual-risk ledger (if AUDIT), Binary verdict. [galtea](https://galtea.ai/blog/llm-as-a-judge-prompts-templates-rubrics-and-best-practices)
> 4. Assume the artifact is incomplete or overclaiming until shown otherwise; do not propose implementation or grant authority beyond the declared lane. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

You can embed this skeleton inside each model-specific prompt without changing the rubric itself. [promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/)

***

## 7. Lane-specific extensions (empty lanes ready)

For now, your empty lanes can simply adopt this universal rubric and add one or two dimensions as needed:

- **AUDIT lane extension**
  - Add “Test coverage of risk scenarios” as a dimension if you introduce test artifacts later. [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)

- **BUILD-DESIGN lane extension**
  - Add “Design completeness” (interfaces, roles, failure modes) and “Constraint respect” (does the design obey existing guardrails and non-claims). [perplexity](https://www.perplexity.ai/search/20236176-c14e-46bc-b247-41ec30bba146)

- **RESEARCH lane extension**
  - Add “Coverage of options” and “Uncertainty mapping” (does it clearly state what is unknown or speculative). [perplexity](https://www.perplexity.ai/hub/blog)

Until you specialize a lane, the universal six dimensions + structure + binary verdict are enough to prevent soft, drift-prone outputs from being treated as acceptable. [scale.stanford](https://scale.stanford.edu/ai/repository/autorubric-unified-framework-rubric-based-llm-evaluation)

***

You can now drop this file into your repo as the project-wide standard, and point every model (Gemini, Perplexity, others) at it whenever they act as a judge, reviewer, or auditor. If you want, the next step can be a very short companion file like `LLM_RUBRIC_USAGE_GUIDE.md` that explains in 1–2 pages how agents and humans are expected to use this rubric in day-to-day work.