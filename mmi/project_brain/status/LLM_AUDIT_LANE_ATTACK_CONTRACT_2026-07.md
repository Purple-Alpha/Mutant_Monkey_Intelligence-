# LLM Audit Lane Attack Contract - 2026-07

## Status

AUDIT LANE ATTACK CONTRACT PATCHED - DOC/CONTROL ONLY

Authority class:

```text
SPEC_PREP_ONLY / AUDIT_ONLY
```

This artifact is specific to audit-lane work. It applies to Gemini, Perplexity, Codex-as-reviewer, any other LLM, and any person/model performing audits for this project.

It does not define build, design, research, implementation, execution, cleanup, or deployment authority.

Core audit posture:

```text
REVIEW THIS: NO
ATTACK THIS: YES
```

Auditors must attack the artifact for gaps, drift, overclaims, missing evidence, weak authority boundaries, residual-risk misalignment, false closure, evasion paths, denial-of-service exposure, leakage paths, malformed input bypasses, and any wording that could let documentation be mistaken for proof or authority.

Self-grading rule:

```text
MODEL SELF-GRADE: REQUIRED BUT NOT TRUSTED
NO MODEL MAY PASS ITSELF
SEPARATE REVIEWER GRADE: REQUIRED
MATT DECISION: FINAL
```

Remote-head rule:

```text
EVERY AUDIT MUST CITE ACTIVE REMOTE HEAD COMMIT AT REVIEW TIME
```

Audit-phase implementation rule:

```text
AUDIT-PHASE CODE GENERATION: NO
IMPLEMENTATION TEMPLATES IN AUDIT OUTPUT: NO
DIAGNOSTIC PATCH REQUIREMENTS ONLY: YES
```

Forbidden authority:

```text
BUILD AUTHORITY: NO
SCAN EXECUTION AUTHORITY: NO
ARCHIVE EXTRACTION AUTHORITY: NO
OUTPUT GENERATION AUTHORITY: NO
CLEANUP AUTHORITY: NO
DELETE AUTHORITY: NO
RESET / CLEAN AUTHORITY: NO
FORCE-PUSH AUTHORITY: NO
KERNEL IMPLEMENTATION AUTHORITY: NO
RUNTIME WIRING: NO
MINIFILTER DRIVER IMPLEMENTATION: NO
PROTECTED COMMAND EXECUTION: NO
DISPATCHER MUTATION: NO
SCOREBOARD MUTATION: NO
M4 CLOSURE: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```

## Source Packet
You’re right to treat “passable” audits as a fail condition for this project; you need an auditing lane that is explicitly designed to hunt for gaps, not just to rubber-stamp artifacts. [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

Below are concrete moves to make Gemini (or any auditor) behave like a high-intelligence gap-finder instead of a B‑grade reviewer.

## 1. Define a hard audit standard  

### Turn “audit” into a gate spec  
Write a short “AUDIT_STANDARD.md” that every Gemini audit must satisfy. At minimum: [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)
- Scope: “Documentation/control only, no build/authority claims; primary goal is to find gaps, drifts, and overclaims.” [perplexity](https://www.perplexity.ai/search/20236176-c14e-46bc-b247-41ec30bba146)
- Required outputs per audit:  
  - List of suspected gaps (missing fields, weak definitions, ambiguous authority, residual risks not tied to claims). [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)
  - List of overclaims or drift (places where language implies more proof than exists). [perplexity](https://www.perplexity.ai/search/ed76758b-1afd-4c4e-a22a-26fe09ba011b)
  - Explicit non-claims and falsifiers (what this artifact does not prove, where it could still fail). [perplexity](https://www.perplexity.ai/search/8afc382a-afec-467e-a736-a0fec8d7c26d)
  - Binary pass/fail against your rubric (see next section), not “looks okay.” [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)

This makes each Gemini call a test against a specification, not “give me feedback.” [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)

## 2. Build a strict audit rubric  

### Rubric instead of vibes  
Define a scoring rubric that forces the model to work: [watershed](https://watershed.com/blog/a-practical-framework-for-llm-system-evaluations-for-multi-step-processes)
- Dimensions (example):  
  - Authority boundaries: Are DOC/CONTROL vs build/implementation clearly separated? [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)
  - Residual risk: Are open risks listed, linked to claims, and clearly blocking closure? [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)
  - Provenance: Are evidence IDs, hashes, paths, and timestamps present where needed? [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)
  - Non-claims: Does the artifact explicitly say what it does NOT prove? [perplexity](https://www.perplexity.ai/search/ed76758b-1afd-4c4e-a22a-26fe09ba011b)
  - Drift risk: Any language that could be misread as perfect closure, runtime authority, or “safe enough”? [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)

Require Gemini to:  
- Assign each dimension a rating (e.g., “CLEAN / WEAK / MISSING”). [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)
- Provide at least one concrete example per WEAK/MISSING rating. [spkaa](https://www.spkaa.com/blog/best-practices-for-reviewing-and-auditing-llm-generated-code)

Weak audits will show up as “many dimensions marked CLEAN but with shallow examples,” which you can treat as an automatic fail. [watershed](https://watershed.com/blog/a-practical-framework-for-llm-system-evaluations-for-multi-step-processes)

## 3. Change the prompt contract  

### From “review this” to “attack this”  
Gemini is new to your lane, so its default behavior is polite, constructive review—exactly what you don’t want. [cloud.google](https://cloud.google.com/discover/what-is-prompt-engineering)
Shift the contract:  
- Identity: “You are an adversarial, perfection-standard auditor whose job is to prevent false closure and overclaiming.” [cloud.google](https://cloud.google.com/discover/what-is-prompt-engineering)
- Directive:  
  - “Assume the artifact is wrong, incomplete, or overclaiming until proven otherwise.” [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)
  - “Your task is to identify every plausible gap, drift, ambiguity, or missing guardrail that could let documentation be misread as proof or authority.” [perplexity](https://www.perplexity.ai/search/ed76758b-1afd-4c4e-a22a-26fe09ba011b)
- Constraints:  
  - “You must not propose implementation or build steps; stay strictly in documentation/control analysis.” [perplexity](https://www.perplexity.ai/search/20236176-c14e-46bc-b247-41ec30bba146)
  - “If you cannot find issues, explain why, referencing each rubric dimension explicitly.” [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)

This aligns Gemini’s behavior with the same discipline you’re enforcing in your minifilter packet. [perplexity](https://www.perplexity.ai/search/8afc382a-afec-467e-a736-a0fec8d7c26d)

## 4. Require structured output  

### Force a machine-checkable shape  
To avoid “B‑movie prose,” insist on a rigid format: [spkaa](https://www.spkaa.com/blog/best-practices-for-reviewing-and-auditing-llm-generated-code)

For each audit, require:  
- Section 1: Rubric table (dimensions, rating, one example each). [watershed](https://watershed.com/blog/a-practical-framework-for-llm-system-evaluations-for-multi-step-processes)
- Section 2: Gap list (numbered, each with scope, impact, required patch). [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)
- Section 3: Drift/overclaim list (sentences or sections that imply more authority/proof than allowed). [perplexity](https://www.perplexity.ai/search/fa2f6765-3eac-4384-a5d7-adb43a2cc69f)
- Section 4: Non-claims and falsifiers (explicit bullet list of what remains unproven, what would falsify current posture). [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)
- Section 5: Binary decision: “AUDIT_RESULT = FAIL (PATCH REQUIRED)” or “AUDIT_RESULT = PASS (NO PATCH REQUIRED)” with justification per dimension. [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)

You can treat any response that doesn’t fill these sections as an automatic failed audit, regardless of content quality. [launchdarkly](https://launchdarkly.com/blog/llm-observability/)

## 5. Add a residual‑risk lens to every audit  

### Make “what’s still open?” mandatory  
Your own packet already treats residual risk as central; the auditor should mirror that. [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)
For every artifact:  
- Require Gemini to produce a mini residual-risk ledger:  
  - Risk ID, affected claim, current state (OPEN / PARTIALLY MITIGATED / CLOSED), evidence required to close. [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)
- Prohibit any “overall clean” conclusion if any risk remains OPEN or unlinked to a claim. [perplexity](https://www.perplexity.ai/search/338113a2-5e79-417a-87a8-91e1156dd213)

This stops audits from saying “looks strong” while silently ignoring unresolved risks. [perplexity](https://www.perplexity.ai/search/2d835f04-dfd3-4b38-ba92-7cab417ae36f)

## 6. Use multi‑LLM checks strategically, not as a crutch  

### Ensemble as meta‑auditor, not second-opinion  
You don’t want “if another LLM has to audit, Gemini failed,” but you can still use multi‑LLM evaluation in a controlled way: [suprmind](https://suprmind.ai/hub/insights/how-to-run-ai-based-evaluations-across-multiple-llms-at-once/)
- Periodic calibration: Run the same audit prompts through multiple models (Gemini, Perplexity, others) and compare:  
  - Number of gaps found.  
  - Depth of explanation.  
  - Ability to respect your DOC/CONTROL boundary. [suprmind](https://suprmind.ai/hub/insights/how-to-run-ai-based-evaluations-across-multiple-llms-at-once/)
- Use this to tune Gemini prompts and rubric, not to patch individual audits in production. [suprmind](https://suprmind.ai/hub/insights/how-to-run-ai-based-evaluations-across-multiple-llms-at-once/)

Gemini remains your primary auditor; other models act as test harnesses to improve the prompt and rubric until Gemini meets your standard. [launchdarkly](https://launchdarkly.com/blog/llm-observability/)

## 7. Add observability and audit trails for the audits themselves  

### Treat the auditor as a system to be audited  
Track Gemini’s performance just like you track minifilter trust: [launchdarkly](https://launchdarkly.com/blog/llm-observability/)
- Log:  
  - Model version, prompt version, rubric version. [launchdarkly](https://launchdarkly.com/blog/llm-observability/)
  - Audit result (PASS/FAIL), number of issues found, classes of issues (authority drift, missing evidence, residual risk misalignment, etc.). [digicobweb](https://digicobweb.com/how-to-audit-large-language-models/)
- Periodically review:  
  - Where audits missed issues that you or another tool later found.  
  - Patterns (e.g., always weak on provenance or residual risk). [launchdarkly](https://launchdarkly.com/blog/llm-observability/)

Then adjust the prompts, rubric, and required sections to push Gemini toward your “perfect closure discipline” standard. [holisticai](https://www.holisticai.com/blog/framework-for-llm-audits)

## 8. What “A‑grade” audits should feel like  

Given your project, a good audit should:  
- Explicitly restate: “ACCEPTED SPEC DOES NOT EQUAL PROVEN SYSTEM; DOC/CONTROL ONLY; PERFECT CLOSURE REQUIRES SEPARATE GATE + EVIDENCE + Matt approval.” [perplexity](https://www.perplexity.ai/search/ed76758b-1afd-4c4e-a22a-26fe09ba011b)
- Point out every place where wording drifts toward “this is ready,” “this is safe,” or implies runtime authority. [perplexity](https://www.perplexity.ai/search/8afc382a-afec-467e-a736-a0fec8d7c26d)
- Connect artifacts to trust-state semantics, invalidation, re‑attestation, and residual risk, not just plumbing. [perplexity](https://www.perplexity.ai/search/d23d78fd-deee-43f6-97e2-9dea5a662d7b)
- End with a crisp decision: “Packet is directionally strong but not yet audit-complete; here are the specific patches required.” [perplexity](https://www.perplexity.ai/search/8afc382a-afec-467e-a736-a0fec8d7c26d)

If you’d like, I can draft a concrete “GEMINI_AUDIT_PROMPT_SPEC.md” in your usual style (DOC/CONTROL only, with rubric and required sections) that you can plug straight into your auditing pipeline so Gemini stops giving you B‑grade reviews.