# Testing Score Sheet Schema

## §1 Status / boundary header

**Status:** Pre-spec shaping artifact. Research input only. Not §11. Not §13. Not D10 evidence. Not implementation. Not runtime code. Not client-facing copy. Not pricing approval. Not an underwriter / broker / insurer claim.

**Captured:** 2026-06-01 by Cursor at operator request, after the 2026-06-01 correction-evidence-loop doctrine was recorded in `CURRENT_STATE_MAP.md` and after the testing / scoring / correction-evidence research was preserved under `Research/queries/`.

**Authority:** Matt decides. This file defines a proposed internal row shape for recording NorthStar test events. It does not authorize runtime code, a new database table, a buyer-facing report, or any weakening / widening of existing test expectations.

**Boundary at a glance:**

- Pre-spec only: this is a schema discipline sketch, not a signed contract.
- Internal only: no row in this sheet is buyer-facing unless a later signed spec defines a safe render.
- No compliance, certification, insurer-approval, coverage-qualification, premium-reduction, or fraud-prevention claim is made here.
- No test may be weakened, relaxed, or reinterpreted inside this sheet to make a failure disappear.
- False positives, false negatives, partial passes, blocked tests, and successful calibration observations all count as evidence.

---

## §2 Purpose

The Testing Score Sheet exists to make every meaningful test event scannable without stripping away the reason it mattered.

Each row answers:

1. What was tested?
2. What was expected?
3. What actually happened?
4. Did it pass, fail, partially pass, or get blocked?
5. Why does that outcome matter in plain English?
6. If it failed or surfaced calibration evidence, what type of event was it?
7. Was a scoped corrective action applied or deliberately not applied?
8. What retest evidence, diagnostic evidence, or open correction record proves the state of the loop?

The long-term purpose is credibility. NorthStar should be able to show its own learning record: not a marketing summary, not a clean-looking dashboard, but the durable chain of test events, mistakes, corrections, and retests. The accumulated record is also a seed surface for a future internal agent bible: what the system learned, what it must not forget, and which failure patterns must remain visible.

This artifact intentionally records passes too. A successful test can still carry a calibration observation: a model was right for the right reason, a detector stayed quiet on a benign edge case, an authentication-pass email still surfaced content risk, or a known false-positive risk did not materialize.

---

## §3 Source anchors already in repo

### §3.1 Internal project anchors

| Anchor | What this schema borrows |
|---|---|
| `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` | Verdict enums, `verdict_match`, per-case schema, evidence-required rule, failure-card schema, retest linkage, confidence buckets, no chain-of-thought boundary. |
| `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` | Signed §11 client-facing axis vocabulary and the rule that explanation surfaces must be structured, bounded, and not a proxy for operator decision. |
| `REACTION_TIMING_TEST_LOG.md` | Closed `pass` / `partial` / `fail` / `blocked` verdict pattern, timestamp discipline, null-with-reason rule, evidence-artifact-path pattern. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/` | Existing eval harness surface and per-case / aggregate scoring evidence source. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_*.md` | Saved Phase 1.5 failure and recovery evidence: full rerun failure, targeted diagnostics, and vendor-invoice recall correction trail. |
| `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` | Internal correction-evidence shape: false-negative / false-positive preservation, `why_corrective_action_warranted`, scoped correction, retest evidence, proportionality note. |
| `CURRENT_STATE_MAP.md` | False-positive / false-negative correction-evidence-loop doctrine: failures are surfaced, operator decides corrections, tests are never weakened, corrections are scoped / proportionate / retestable, passes can carry calibration observations. |

### §3.2 External research anchors preserved for this task

The companion research file `Research/queries/2026-06-01_testing_scoring_correction_evidence_research.md` validates the direction against external precedent. It is research only, not a source of NorthStar authority.

Useful takeaways:

- Per-event test records are a mature pattern under names like test case execution record, test log, software test report, and QA scorecard.
- Mature records distinguish expected result, actual result, pass/fail status, performer, date, and rationale for decisions.
- Failure-preserving disciplines appear across blameless postmortems, CAPA, incident lessons learned, chaos engineering, adversarial validation, and requirements-based verification.
- External disclosure should be tiered: internal records stay complete; external summaries, if ever authorized, are curated and audience-specific.

Higher-risk / less-settled research claims should not be copied into signed specs without a separate verification pass.

---

## §4 Row schema

The Testing Score Sheet row has exactly 12 columns:

| # | Column | Type / rule |
|---:|---|---|
| 1 | `test_id` | Stable internal identifier, e.g. `tss-2026-05-22-001`. Unique within the sheet. |
| 2 | `event_type` | Closed enum: `smoke`, `regression`, `adversarial`, `red_team`, `eval_subcategory`, `eval_full`, `live_diagnostic`, `live_runtime_case`, `calibration_observation`. |
| 3 | `what_was_tested` | Short plain-English description of the surface under test. |
| 4 | `expected_outcome` | Expected verdict, score band, behavior, invariant, or record shape. |
| 5 | `actual_outcome` | Actual verdict, score band, behavior, invariant result, or record shape. |
| 6 | `pass_fail` | Closed enum: `pass`, `fail`, `partial`, `blocked`. Mirrors `REACTION_TIMING_TEST_LOG.md`. |
| 7 | `why_plain_english` | <= 280 chars. No raw payloads, no secret material, no real tenant identifiers other than fictional `bluefin-marine-supplies-demo` or `acme-industries-demo`. |
| 8 | `failure_type` | Nullable closed enum: `false_negative`, `false_positive`, `expectation_contract`, `fixture`, `prompt`, `detector`, `workflow`, `schema_violation`, `scope_violation`, `calibration_observation`. Null when `pass_fail == pass` and no calibration note is needed. |
| 9 | `corrective_action` | Nullable. Named scoped change, `null`, or explicit `no_action` explanation when no action is warranted. |
| 10 | `retest_evidence` | Nullable list of named repo-resident proofs: test paths, eval report paths, diagnostic paths, activity-log entries, or open correction references. |
| 11 | `recorded_at` | ISO-8601 UTC timestamp. |
| 12 | `recorded_by` | Closed enum: `operator-Matt`, `operator-Matt + AI-drafted under operator review`, `AI-drafted`. The `AI-drafted` value requires operator review before the row counts. |

### §4.1 Field rules

- A pass row may have non-null `why_plain_english`. Calibration observations on successful runs are first-class evidence per `CURRENT_STATE_MAP.md`; record passes too, not just failures.
- A fail row MUST link to a correction-evidence record entry (`cer-*`) through `retest_evidence` OR explicitly state `open — no correction yet, see <reference>`.
- A blocked row MUST explain the block in `actual_outcome` or `why_plain_english`; missing dependency, environment unavailable, operator stop, and precondition unmet are valid blocked reasons.
- No row may weaken or lower an existing expectation bound. If a corrective action loosens a bound, the proportionality reasoning must live in the linked `cer-*` entry, not hidden in this sheet.
- `corrective_action` is nullable because not every observation warrants a change. If set to `no_action`, it must say why no action is appropriate.
- `retest_evidence` must name repo-resident evidence whenever possible. Temporary local paths alone are not enough for closure.
- The sheet stores structured summaries only. It must not store raw email bodies, raw headers, account numbers, routing numbers, secrets, chain-of-thought, or production tenant data.

---

## §5 Seed rows

The rows below are seed examples, not a complete historical backfill. They show the intended level of specificity.

### §5.1 Seed row — 2026-05-22 vendor-invoice false-negative recovery

```yaml
test_id: "tss-2026-05-22-001"
event_type: "eval_full"
what_was_tested: "Phase 1.5 full grok-4 eval rerun across the 40-case fraud dataset, with focus on vendor_invoice_fraud recall."
expected_outcome: "Overall gate passes; vendor_invoice_fraud recall meets the 60% floor."
actual_outcome: "Full rerun produced 36/40 overall, 100% precision, 0% FPR, but vendor_invoice_fraud recall was 40% (2/5), so the gate failed."
pass_fail: "fail"
why_plain_english: "The system was not over-flagging legit mail; it under-detected a specific vendor-invoice fraud cluster that matters for payment-change evidence."
failure_type: "false_negative"
corrective_action: "Scoped no-spend prompt-floor correction in NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT; no schema, dataset, tenant-override, production_state, or loop change."
retest_evidence:
  - "4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md#cer-2026-05-22-001"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-001_diagnostic.md"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-002_diagnostic.md"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-003_diagnostic.md"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-004_diagnostic.md"
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-005_diagnostic.md"
recorded_at: "2026-06-01T00:00:00Z"
recorded_by: "operator-Matt + AI-drafted under operator review"
```

### §5.2 Seed row — 2026-06-01 live grok-4 auth-pass / content-risk calibration

```yaml
test_id: "tss-2026-06-01-001"
event_type: "live_runtime_case"
what_was_tested: "Live grok-4 scoring run against the fictional §14 vendor-payment-redirect fixture after the runner dependency issue was fixed."
expected_outcome: "Authenticated sender posture does not suppress content-risk review; risky payment-change cues should still surface for human review."
actual_outcome: "Run completed with recommended_action=needs_review, risk_score=72, vendor_fraud_score=65, and behavioral flags for new banking instructions plus urgency paired with finance."
pass_fail: "pass"
why_plain_english: "Good calibration: authentication pass did not become a false sense of safety; content-side vendor-payment risk still surfaced without claiming fraud was blocked."
failure_type: "calibration_observation"
corrective_action: "no_action — successful calibration observation; dependency issue (`openai` missing from venv) was fixed before the live run and is noted separately in the run context."
retest_evidence:
  - "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md"
  - "Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/RUN_INSTRUCTIONS.md"
recorded_at: "2026-06-01T00:00:00Z"
recorded_by: "operator-Matt + AI-drafted under operator review"
```

---

## §6 Internal / external boundary

The Testing Score Sheet is internal by default. Its rows can include failures, false positives, false negatives, blocked runs, calibration notes, and correction references that would be too raw for a buyer-facing surface.

If a future signed spec authorizes external rendering, the safe pattern should be:

| Internal row field | External handling, if ever authorized |
|---|---|
| `test_id` | May render as an opaque reference ID. |
| `event_type` | May render as broad category, e.g. "regression test" or "diagnostic run." |
| `what_was_tested` | May render if it does not expose exploit steps or internal-only implementation details. |
| `expected_outcome` / `actual_outcome` | Summarize at a high level; avoid raw scores unless the signed render contract allows them. |
| `pass_fail` | May render only with scope context; never as a blanket product-quality claim. |
| `why_plain_english` | Requires review for safe language, no raw payloads, and no forbidden claims. |
| `failure_type` | Usually internal-only; external summaries may say "correction record on file" without exposing raw failure taxonomy. |
| `corrective_action` | May render as scoped category only, e.g. "prompt-level correction retested." |
| `retest_evidence` | May render as count / date / artifact class, not raw path dump, unless the reader is in a controlled audit channel. |
| `recorded_at` / `recorded_by` | May render as date / role; named operator identity only if authorized. |

This boundary follows the same direction as `Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md`: complete internal record first; curated external abstraction later, only if separately authorized.

---

## §7 Non-authorizations

This file does **not**:

- Authorize implementation of a score-sheet writer, database table, dashboard, renderer, portal, or CI gate.
- Authorize editing `audit_tools/pre_ship_audit.py`, `audit_tools/complete_gate.py`, or the eval harness.
- Authorize weakening, lowering, or deleting any test expectation.
- Authorize a buyer-facing correction summary or disclosure surface.
- Advance Cyber Insurance D10 discovery progress.
- Satisfy §13 sign-off for the Cyber Insurance Evidence Package.
- Change the signed Client-Facing 5-Axis Email Scoring Rubric.
- Change `REACTION_TIMING_TEST_LOG.md` or replace its timing-specific ledger.
- Invent new eval outcomes, detection rates, vendor IDs, buyer outcomes, prevented-loss narratives, or production claims.

If any statement here conflicts with a §11- or §13-signed spec, the signed spec wins.

---

**End of pre-spec score-sheet schema.**
