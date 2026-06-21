# MMI Governance Invariants Testing — Multi-Lane Advisory Brief

**Status:** ACTIVE DESIGN BRIEF · NOT §11 · NOT BUILD AUTHORIZATION  
**Scoreboard:** #105  
**Primary contract:** `4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md`  
**Authority repo:** `/home/socialarchitect/northstar`  
**Operator:** Matt Nichol orchestrates; workers advise only.

**Purpose:** Run **three parallel advisory lanes** on the hardened invariants contract before §11.
Contract-of-record framing: **invariants verification**, not stress/load/chaos testing.

**Parked:** `#67 Rule Improvement` — hold until Matt unparks or invariants contract §11 + Lane 1 build path opens.

**Next gate per contract §16:** Matt may authorize **Codex pre-build review** of the contract before §11.

---

## Shared pre-flight (all lanes)

```text
TASK: Advisory review of MMI Governance Invariants Testing Framework contract (hardened revision).
READ FIRST:
  - 4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md (full contract)
  - mmi/concepts/MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md (domain-clean constraint)
  - scripts/mmi_pm_voice.py + tests/test_mmi_pm_voice.py (PM Voice / LAW 7 surfaces)
  - scripts/mmi_crew_chain.py + tests/test_mmi_crew_chain.py (forbidden conclusions)

FORBIDDEN: Implementation code, §11 signature text by worker, AUTH-5 unlock, forgery-resistance
  claims, live-runtime dual-engine gate, unparking #67 without Matt.

OUTPUT FORMAT (each lane):
  1. Verdict: PASS_REVIEW | PASS_WITH_CHANGES | BLOCK
  2. LAW 1–9 compliance check (cite section if fail)
  3. Section 2.8 honest-scope: is drift-vs-forgery boundary clear enough?
  4. Lane 1 (Authority Escalation Probe): is 6.5 structural rule + 6.6 dual-engine spec buildable?
  5. Top required changes before §16 sign-off
  6. One paragraph plain-language summary for Matt
```

---

## Lane A — Claude (architecture + doctrine)

Focus: LAW 1/2/8, dual-engine independence, structural advisory rule (6.5), lane ordering (LAW 3/4).

---

## Lane B — Gemini (plain language + operator burden)

Focus: Explain LAW 9 / Section 2.8 to Matt without jargon. Where does this add ceremony vs real safety?

---

## Lane C — ChatGPT / MMI Advisor (routing + scope)

Focus: §16 checklist order (approve → Codex gate → §11 → Lane 1 build only). Scoreboard #105 fit.

---

## Matt orchestration checklist

1. Three advisory lanes → capture verdicts in `PROJECT_ACTIVITY_LOG.md`
2. Optional: authorize Codex pre-build gate on the contract (§16 checkbox)
3. Cursor: reconcile authority state-model + fixtures (contract 6.7) before Matt §11
4. §11 signs contract only — Lane 1 build is **separate** authorization after sign

**Supersedes:** `MMI_Governance_Stress_Testing_Advisory_Lane_Brief.md` (stress framing retired).
