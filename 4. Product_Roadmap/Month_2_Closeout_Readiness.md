# Month 2 Closeout Readiness

**Status:** Month 2 is complete and verified as of 2026-05-21.

**Build track:** SwarmCommand Agent Loop Runtime + NorthStar Inbox Shield + Fraud / Ransomware Specialization.

**Runtime baseline:** 332+ tests passing (exit code 0).

**Pass-gate baseline model:** `grok-4` (xAI).

## Purpose

This file is the Month 2 closeout checkpoint. It exists to keep the team from
sliding into Month 3 implementation before the Month 2 fraud-detection gate is
clearly verified, indexed, and bounded.

Month 2's job was not to build every fraud detector imaginable. Month 2's job
was to extend the scoring payload with the four new fraud dimensions, lock the
expanded system prompt, build the fraud eval harness, generate the 40-case
dataset, and then drive the live LLM run all the way to the §4.5 pass gate.

## Month 2 Deliverables

All deliverables from `12_Month_Specialization_Roadmap.md` Month 2 are landed:

1. **`EmailAnalysisRiskAnalysis` extended with the four fraud dimensions.**
   - File: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py`
   - Fields added:
     - `vendor_fraud_score` (0–100, required)
     - `wire_transfer_anomaly_score` (0–100, required)
     - `invoice_authenticity_score` (0–100 or `None`, inverted — high means authentic; `None` when no invoice attachment)
     - `behavioral_deviation_flags` (controlled `Literal` with **nine** locked values, schema-versioned)
   - Tests: 9 new schema tests in `tests/test_email_analysis_record.py`.

2. **`NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` rewritten and locked.**
   - File: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py`
   - Anchored to the Fraud + Ransomware specialization pillars.
   - Contains rubrics for the four new scoring dimensions.
   - Embeds **seven** worked examples (1–7) covering: high-confidence vendor invoice fraud, executive impersonation, legit vendor invoice, ambiguous needs_review, thread-hijack vendor invoice, future-dated invoice, and Unicode-hyphen lookalike sender domain.
   - Pinned by `test_scoring_prompt_is_locked_to_fraud_specialization_pillars`, `test_scoring_prompt_embeds_four_worked_examples_with_distinct_labels`, `test_scoring_prompt_embeds_recovery_pass_examples_5_and_6`, and `test_scoring_prompt_embeds_final_recovery_example_7_unicode_hyphen_sender`.

3. **Eval harness landed at `core/scoring/eval/`.**
   - Files:
     - `core/scoring/eval/dataset.py` — strict JSONL loader, required-subset behavioral-flag contract, optional `forbidden_behavioral_deviation_flags`.
     - `core/scoring/eval/runner.py` — `run_eval`, `EvalReport.markdown_table()`, §4.5 Pass-Gate block + `gate_passed` verdict.
     - `core/scoring/eval/llm_safety.py` — `UNSAFE_PATTERNS`, `assert_dataset_path_is_allowlisted`, `scan_dataset_for_unsafe_terms`, `build_llm_safe_client`, `resolve_api_key`, `strip_markdown_code_fences`.
     - `core/scoring/eval/live_client.py` — Anthropic / OpenAI / **xAI (Grok)** live clients with lazy-imported SDKs.
     - `core/scoring/eval/fraud_eval_harness.py` — CLI: `--provider {anthropic, openai, xai}`, `--model`, `--report-out`, `--show-failure-details`, `--show-raw-response`, `--case-id`, UTF-8 stdio reconfiguration for Windows cp1252 consoles.

4. **40-case fraud eval dataset generated.**
   - File: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/fraud_eval_dataset.jsonl`
   - Distribution: 20 fraud / 20 legit; subcategories: `vendor_invoice_fraud=5`, `executive_impersonation=5`, `wire_transfer_pressure=4`, `invoice_authenticity_anomaly=3`, `lookalike_sender=2`, `header_inconsistency=1`, `legit_vendor_invoice=8`, `legit_internal=5`, `legit_calendar=3`, `legit_hr=2`, `legit_newsletter=2`.
   - Design grid: `4. Product_Roadmap/Phase_1_1_Eval_Dataset_Design_Grid.md`.

5. **Live LLM eval pass gate verified on `grok-4`.**
   - Report: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_21_final_recovery_grok4.md`
   - Numbers:
     - Overall: **36 / 40**
     - Fraud precision: **100.00%**
     - Legit FPR: **0.00%**
     - Per-subcategory recall: every fraud subcategory **≥ 60%** (lookalike_sender 100%, invoice_authenticity_anomaly 100%, vendor_invoice_fraud 60%, wire_transfer_pressure 75%, executive_impersonation 80%, header_inconsistency 100%).
   - **Gate verdict: PASS.**

6. **≥ 8 new scoring tests covering the new dimensions.**
   - Evidence: 9 schema tests + 9 scoring tests + 50 eval-harness tests + recall-patch tests + recovery-pass tests + final-recovery Example 7 test.
   - Net delta from Month 1 baseline (196 tests): **+136 tests** as of the final recovery pass.

## Month 2 Gate

Roadmap gate (`12_Month_Specialization_Roadmap.md` Month 2):

> Eval shows ≥80% precision on the fraud-emails set with ≤10% false-positive
> rate on the legit set. Document where it underperforms; capture as Q2
> backlog.

Pass-gate criteria from `Phase_1_1_Fraud_Prevention_Deep_Dive.md` §4.5:

| Criterion | Threshold | Actual on `grok-4` | Met |
|---|---|---|---|
| Precision on fraud | ≥ 80% | 100.00% | YES |
| FPR on legit | ≤ 10% | 0.00% | YES |
| Per-fraud-subcategory recall | ≥ 60% each | all six fraud subcategories ≥ 60% | YES |

**Gate verdict: PASS on `grok-4`.**

Gate evidence:

- Durable report: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_21_final_recovery_grok4.md`
- Activity log entry: `PROJECT_ACTIVITY_LOG.md` → "2026-05-21 - Month 2 Final Live-Eval Recovery Pass (Gate PASS on grok-4)".
- Handshake summary: `PROJECT_HANDSHAKE.md` → Completed item 158.

Verification command (operator-runnable):

```powershell
python -m core.scoring.eval.fraud_eval_harness --provider xai --model grok-4 --report-out eval_report_2026_05_21_final_recovery_grok4.md --show-failure-details
```

Result:

```text
Overall passed: 36 / 40
Precision on fraud cases: 100.00%
False positive rate on legit cases: 0.00%
Gate verdict: PASS
```

Test suite:

```powershell
python -m pytest tests -q
```

Result: exit code 0.

## Remaining Known Gaps (Q2 Backlog, NOT Gate Blockers)

The four cases below failed individual assertions on the post-fix `grok-4` run
but do not block the gate. Per-subcategory recall remains ≥ 60% on every fraud
subcategory. These are honest model gaps, not contract brittleness.

| case_id | Subcategory | Failure summary | Disposition |
|---|---|---|---|
| `vf-002` | vendor_invoice_fraud | Missing required `first_time_sender_with_financial_ask` | Future prompt refinement or required-flag review |
| `vf-005` | vendor_invoice_fraud | Large score gap (risk 52 vs min 75; invoice_authenticity_score 68 vs max 50) | Honest model gap on a hard case; queue for Bucket E diagnostic if needed |
| `ei-005` | executive_impersonation | risk 78 vs min 80 (2-pt near-miss) | Acceptable near-miss; no patch |
| `wt-004` | wire_transfer_pressure | risk 42 vs min 45; wire_transfer_anomaly_score 38 vs min 40 | Intentionally ambiguous case; acceptable near-miss |

These four cases are intentionally **NOT** patched as part of Month 2 closeout.
Touching them risks regressing the 100% precision / 0% FPR result.

## Month 2 Boundaries

Month 2 is complete, but these are intentionally **not** in Month 2 scope:

- No ransomware precursor analysis block yet (`attachment_risk_score`,
  `url_obfuscation_score`, `credential_harvesting_score`, `mfa_fatigue_score`,
  `precursor_indicators`) — Month 3.
- No `core/precursor/` module yet (attachment classifier, URL obfuscation
  detector, credential / MFA detectors) — Month 3.
- No sandbox training pit with fraud-specialized Red agents — Month 4.
- No mutation-engine specialization for fraud-pattern thresholds — Month 5.
- No tenant memory model for known vendors / known banking details / invoice
  history — explicitly out of Q1 scope.
- No multi-language fraud detection — Year 2+.
- No threat-intel feed integration — Year 2+.
- No outbound email scanning — Year 2+.

These are not gaps in Month 2. They are next-phase scope.

## Do Not Start Month 3 Runtime Work Until

Before starting Month 3 Phase 1.2 runtime work, confirm:

1. This file's closeout state still matches `PROJECT_HANDSHAKE.md` and the
   most recent `PROJECT_ACTIVITY_LOG.md` entry.
2. The runtime test baseline is still exit code 0.
3. The `grok-4` gate-PASS report is still on disk at
   `eval_report_2026_05_21_final_recovery_grok4.md`.
4. The operator agrees that Month 3 Phase 1.2 (ransomware precursor detection)
   is the next runtime move, not a Bucket E patch on `vf-002` / `vf-005` /
   `ei-005` / `wt-004`.

## Source-of-Truth Files

Read these before starting Month 3 runtime work:

- `PROJECT_HANDSHAKE.md`
- `PROJECT_ACTIVITY_LOG.md`
- `MASTER_INDEX.md`
- `4. Product_Roadmap/12_Month_Specialization_Roadmap.md`
- `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md`
- `4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md`
- `4. Product_Roadmap/Phase_1_1_Eval_Dataset_Design_Grid.md`
- `4. Product_Roadmap/Live_LLM_Eval_Runbook.md`
- `4. Product_Roadmap/Month_1_Closeout_Readiness.md`
- `4. Product_Roadmap/Month_2_Closeout_Readiness.md` (this file)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_21_final_recovery_grok4.md`
