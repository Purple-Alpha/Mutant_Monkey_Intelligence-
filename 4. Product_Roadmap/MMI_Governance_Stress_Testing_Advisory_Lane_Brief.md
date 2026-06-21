# MMI Governance Stress Testing — Multi-Lane Advisory Brief

> **SUPERSEDED.** Use `4. Product_Roadmap/MMI_Governance_Invariants_Testing_Advisory_Lane_Brief.md`.

**Status:** SUPERSEDED — stress framing retired  
**Scoreboard:** #105  
**Primary spec:** `4. Product_Roadmap/MMI_Governance_Stress_Testing_Framework_Deep_Dive.md`  
**Authority repo:** `/home/socialarchitect/northstar`  
**Operator:** Matt Nichol orchestrates; workers advise only.

**Purpose:** Run **three parallel advisory lanes** on the GSTF draft before §11. Each lane uses `agent_concepts/Mutant_Monkey_Architecture_Directive.md` master template + lane modifier below.

**Parked:** `#67 Rule Improvement` Claude contract-draft — do not resume until Matt unparks or GSTF reaches §11-ready per GSTF-D9.

---

## Shared pre-flight (all lanes)

```text
TASK: Advisory review of MMI Governance Stress Testing Framework draft.
READ FIRST:
  - 4. Product_Roadmap/MMI_Governance_Stress_Testing_Framework_Deep_Dive.md
  - mmi/concepts/MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md (domain-clean constraint)
  - scripts/mmi_crew_chain.py + tests/test_mmi_crew_chain.py (current co-sim baseline)
  - scripts/mmi_contradiction_report.py + tests/test_mmi_contradiction_report.py

FORBIDDEN: Implementation code, scoreboard promotion, §11 signature text, AUTH-5 unlock,
  unparking #67 without Matt, claiming "approved" or "authorized".

OUTPUT FORMAT (each lane):
  1. Verdict: PASS_REVIEW | PASS_WITH_CHANGES | BLOCK
  2. Top 3 strengths (evidence-cited)
  3. Top 5 required changes before §11 (specific section refs)
  4. Overengineering check (what to cut for v1)
  5. Audit integration gaps vs complete_gate.py discipline
  6. One paragraph plain-language summary for Matt
```

---

## Lane A — Claude (architecture + doctrine)

**Modifier:** Architecture critique, overengineering checks, doctrine clarity. Leanest design that meets requirement.

**Focus questions:**

1. Are P1–P4 the right pillar split, or should epistemic drift and authority rebellion merge?
2. Is Mode B pipeline halt correctly deferred from Tier 2C?
3. Does GSTF-D9 (park #67) create a deadlock with build momentum rule?
4. What is the smallest pytest harness that proves governance stress without simulating 50 concurrent LLM agents?
5. Does anything violate domain-clean separation from the multi-domain concept sheet?

**Deliver to:** Matt + Cursor execution lane (for spec edits only after Matt authorizes).

---

## Lane B — Gemini (plain language + operator burden)

**Modifier:** Listening-first explainer per `MUTANT_MONKEY_GEMINI_BRIEFING.md`. No jargon without translation.

**Focus questions:**

1. Explain to Matt in plain language what each pillar protects against and what a "pass" means.
2. Where will this add operator burden Matt will hate? Propose cuts.
3. Is the three-lane review before §11 worth the time, or ceremony drift?
4. What would Matt regret signing if Phase 3 harness is harder than expected?
5. Forbidden-language check on any client-facing leakage (should be none).

**Deliver to:** Matt (plain-language summary for activity log).

---

## Lane C — ChatGPT / MMI Advisor (routing + scope)

**Modifier:** Route, tighten scope, construct next safe move. Do not invent repo state.

**Focus questions:**

1. Is scoreboard #105 the right home, or should GSTF be infrastructure-only without a row?
2. Does BOR `ADVISORY_MULTI_LANE_DESIGN` lane type route correctly for PM Voice?
3. Sequencing: GSTF §11 before Email Testing Framework §11, or parallel?
4. What is the single next operator action after this brief lands?
5. What must appear in `PROJECT_ACTIVITY_LOG.md` to satisfy GSTF §5.3?

**Deliver to:** Matt (orchestration checklist).

---

## Matt orchestration checklist (suggested order)

1. Paste **Lane A** prompt to Claude with draft attached → capture output.
2. Paste **Lane B** prompt to Gemini → capture plain-language summary.
3. Paste **Lane C** prompt to ChatGPT → capture routing checklist.
4. If any lane returns `BLOCK`, stop §11 path; authorize Cursor spec revision only.
5. Record one activity-log entry with three verdicts → then decide §11 timing.

**This brief does not authorize §11.** Matt decides.

---

## Audit record requirement (GSTF §5.3)

After three lanes complete, activity log entry must include:

- Date
- Verdict per lane (PASS_REVIEW / PASS_WITH_CHANGES / BLOCK)
- Whether #67 remains parked
- Explicit note: "GSTF design review complete — §11 decision pending Matt"

Cursor may draft activity-log text; Matt authors acceptance.
