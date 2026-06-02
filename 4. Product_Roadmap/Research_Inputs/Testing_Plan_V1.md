# Testing Plan V1

## §1 Status / boundary header

**Status:** Pre-spec testing plan. Research / shaping input only. Not §11. Not §13. Not D10 evidence. Not implementation. Not runtime code. Not client-facing copy. Not pricing approval.

**Captured:** 2026-06-01 by Cursor at operator request, immediately after `Testing_Score_Sheet_Schema.md` was drafted.

**Authority:** Matt decides. This file defines the first internal testing plan that uses `Testing_Score_Sheet_Schema.md` as the row contract. It does not authorize test weakening, runtime edits, new infrastructure, new buyer-facing output, or any automatic promotion decision.

**Boundary at a glance:**

- V1 uses existing evidence surfaces only: saved eval reports, existing regression tests, the §14 fictional fixture path, the 2026-06-01 pre-spec runner, and the live grok-4 run output already captured.
- V1 records failures, passes, partials, blocked attempts, and calibration observations.
- V1 does not create a production ledger, database, dashboard, portal, CI gate, or scoring-sheet writer.
- V1 does not satisfy Cyber Insurance D10, §13 sign-off, or implementation readiness.
- V1 does not claim compliance, certification, insurer approval, coverage qualification, premium reduction, or fraud prevention.

---

## §2 Purpose

Testing Plan V1 turns the score-sheet discipline into an ordered internal plan:

1. Identify the first bounded set of test events worth recording.
2. Map each event to the 12-column `Testing_Score_Sheet_Schema.md` row.
3. Preserve both failures and passes as evidence.
4. Make blocked attempts visible instead of forgetting them.
5. Link any failure to a correction-evidence record or an explicit open correction state.
6. Prove that no test expectation was weakened to create a pass.

The plan is intentionally small. It starts with the strongest evidence already in the repo: the 2026-05-22 Phase 1.5 vendor-invoice recall failure and recovery, and the 2026-06-01 fictional Stage A vendor-payment-redirect runner / live grok-4 calibration observation.

---

## §3 Source anchors

| Anchor | Role in V1 |
|---|---|
| `4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md` | Row contract and field rules. |
| `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` | Correction-evidence seed record `cer-2026-05-22-001`. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md` | Full 40-case eval failure anchor. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` | Post-correction diagnostic pass evidence. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned` | Regression pin for the prompt-floor correction. |
| `Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/` | Operator-run pre-spec runner surface for the fictional §14 case. |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md` | Live grok-4 run summary from 2026-06-01. |
| `CURRENT_STATE_MAP.md` | False-positive / false-negative correction-evidence-loop doctrine. |
| `REACTION_TIMING_TEST_LOG.md` | Closed pass / partial / fail / blocked vocabulary pattern. |

---

## §4 V1 scope

### §4.1 In scope

V1 covers five initial test-event classes:

1. **Historical eval failure**: the 2026-05-22 full Phase 1.5 rerun failure on `vendor_invoice_fraud` recall.
2. **Historical correction retest**: the five saved `vf-001` through `vf-005` live diagnostics after the no-spend prompt-floor correction.
3. **Blocked attempt recording**: the 2026-06-01 live-run dependency block where the venv was missing `openai`.
4. **Live runtime calibration**: the 2026-06-01 live grok-4 auth-pass / content-risk case producing `needs_review`.
5. **Future regression rerun hook**: the next operator-authorized full eval rerun, if Matt chooses to spend the calls later.

### §4.2 Out of scope

V1 does not cover:

- A new test harness implementation.
- A new score-sheet storage file beyond the pre-spec examples already in `Testing_Score_Sheet_Schema.md`.
- Any production tenant data.
- Any real mailbox replay.
- Any new LLM call unless Matt explicitly authorizes it.
- Any weakening of Phase 1.5 thresholds, §14 expectations, or signed-spec boundaries.
- Any buyer-facing summary.

---

## §5 Ordered V1 test-event plan

Each row below describes the event that should be recorded under the 12-column score-sheet schema. `score_sheet_row_id` is the proposed `test_id`.

| Order | score_sheet_row_id | event_type | What is tested | Expected outcome | Current status |
|---:|---|---|---|---|---|
| 1 | `tss-2026-05-22-001` | `eval_full` | Phase 1.5 full grok-4 rerun, focused on whether `vendor_invoice_fraud` recall met the existing floor. | Gate should pass; vendor-invoice recall should meet 60% floor. | Existing evidence says **fail**; row seeded in schema. |
| 2 | `tss-2026-05-22-002` | `live_diagnostic` | `vf-001` through `vf-005` targeted diagnostics after the no-spend prompt-floor correction. | Each targeted vendor-invoice case should pass after correction. | Existing evidence says **pass** for 5/5; should be recorded as retest evidence linked to `cer-2026-05-22-001`. |
| 3 | `tss-2026-06-01-000` | `live_runtime_case` | First 2026-06-01 attempt to run the pre-spec Stage A vendor-payment-redirect runner. | Runner starts with required dependencies present. | Existing evidence says **blocked** because `openai` was missing from the venv; record as blocked, not erased. |
| 4 | `tss-2026-06-01-001` | `live_runtime_case` | Live grok-4 run against the fictional auth-pass / content-risk vendor-payment-redirect fixture after `openai` was installed. | Auth pass should not suppress content-risk review; output should surface payment-change risk for human review. | Existing evidence says **pass** with calibration observation; row seeded in schema. |
| 5 | `tss-next-full-eval-rerun-001` | `eval_full` | Optional future full 40-case rerun after the vendor-invoice prompt-floor correction. | Full gate should pass without relaxing thresholds; precision and FPR should remain clean. | Not run. Operator-spend decision only; open future row. |

---

## §6 Recording rules for V1 execution

### §6.1 Failure rows

If `pass_fail = fail`, the row must do one of two things:

1. Link to a `cer-*` correction-evidence record through `retest_evidence`.
2. State `open — no correction yet` with a repo-resident reference where the open failure is tracked.

No failure row can be closed by changing the expected outcome to match the actual outcome.

### §6.2 Pass rows

A pass row may still carry `failure_type = calibration_observation` when the pass teaches something useful. Examples:

- Auth passed, but content risk still surfaced.
- A benign edge case stayed quiet.
- A detector fired for the intended reason, not just the right final score.
- A prior failure stayed fixed under retest.

### §6.3 Blocked rows

A blocked attempt is evidence. It must name:

- What precondition failed.
- Whether the block was environment, dependency, operator stop, missing fixture, missing key, or other.
- Whether a correction was applied before retry.
- Which later row, if any, proves the block was cleared.

The 2026-06-01 missing-`openai` event is the V1 example: record the block, then link the successful live run after installation.

### §6.4 Partial rows

Use `partial` when:

- The run executed, but only some required fields were produced.
- A test passed functionally but missed evidence fields.
- A runner produced outputs but not enough to claim the intended row closure.

Partial is not a softer pass. It is an evidence state that must name the missing part.

---

## §7 Minimum row content for V1

Every V1 row must fill all 12 score-sheet columns. Nullable fields still appear.

Required handling:

- `failure_type = null` only when the row is a clean pass and no calibration observation is being recorded.
- `corrective_action = null` only when no action is needed and no block/failure was involved.
- `corrective_action = no_action — <reason>` when the operator intentionally decides no correction is warranted.
- `retest_evidence = null` only when there is no retest or proof artifact yet; failures should instead point to an open correction reference.
- `recorded_by = AI-drafted` does not count until Matt reviews the row.

---

## §8 V1 execution sequence

1. **Backfill the two historical rows already seeded in `Testing_Score_Sheet_Schema.md`.**
   - `tss-2026-05-22-001`
   - `tss-2026-06-01-001`

2. **Add the missing blocked-dependency row.**
   - `tss-2026-06-01-000`
   - Event: `openai` package missing from the venv before the live run.
   - Expected outcome: dependency available.
   - Actual outcome: blocked until `pip install openai`.
   - Corrective action: dependency installed.
   - Retest evidence: successful `tss-2026-06-01-001` live run.

3. **Add the historical post-correction diagnostic row.**
   - `tss-2026-05-22-002`
   - Event: `vf-001` through `vf-005` targeted diagnostics after the prompt-floor correction.
   - Expected outcome: all five pass.
   - Actual outcome: all five pass.
   - Corrective action: no new action; verifies `cer-2026-05-22-001`.

4. **Leave the optional full eval rerun open.**
   - `tss-next-full-eval-rerun-001`
   - Do not run automatically.
   - Do not spend provider calls without operator authorization.
   - Do not treat the absence of this rerun as a failure, because `PROGRESS.md` Task 6 explicitly preserved it as an operator decision.

5. **Gate only after Linux-primary sync.**
   - This plan was drafted in the Windows mirror because this Cursor environment could not access the Linux repo through file tools.
   - Before any ready/done/commit claim, replay the artifact into `/home/socialarchitect/northstar`, create the manifest, and run the normal gate.

---

## §9 V1 completion criteria

Testing Plan V1 is execution-complete only when all of the following are true:

1. The plan and schema exist in the Linux primary repo.
2. The score-sheet rows named in §8 steps 1-3 are represented in a durable internal artifact or explicitly left as examples in the schema with operator acceptance.
3. Every fail / blocked row has either correction linkage or open-correction linkage.
4. No expected outcome was weakened after seeing actual output.
5. `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md`, and `PROGRESS.md` identify the plan state accurately.
6. The gate packet returns clean before any commit / ready / done claim.

---

## §10 Non-authorizations

This plan does **not**:

- Authorize new runtime code.
- Authorize a score-sheet implementation.
- Authorize another live LLM call.
- Authorize a full 40-case rerun.
- Authorize weakening or lowering any test expectation.
- Authorize editing signed specs.
- Authorize buyer-facing wording.
- Advance D10.
- Satisfy §13.
- Claim that NorthStar prevented fraud, blocked fraud, reduced premiums, qualified coverage, passed an insurer review, achieved compliance, or earned certification.

If any statement here conflicts with a §11- or §13-signed spec, the signed spec wins.

---

**End of Testing Plan V1.**
