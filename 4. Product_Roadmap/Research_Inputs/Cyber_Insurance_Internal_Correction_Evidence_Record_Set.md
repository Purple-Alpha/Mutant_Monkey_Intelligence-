# Cyber Insurance — Internal Correction-Evidence Record Set (Seed)

## §1 Status / boundary header

**Status:** Pre-spec internal record-set seed. Research / credibility-trail input only. Not §11. Not §13. Not D10 evidence. Not implementation. Not runtime code. Not client-facing copy. Not pricing approval. Not a NorthStar product claim of compliance, certification, insurer approval, premium reduction, coverage qualification, or fraud prevention.

**Captured:** 2026-06-01 by Cursor (Claude Opus 4.7) at operator request, after:

- The Cyber Insurance Evidence Package V1 Synthesis cleared the gate (`audit_outputs/cyber_insurance_evidence_package_v1_synthesis_20260601_20260601T222516Z.md`, `blocking=0 warnings=0`).
- The V1 Record-Set Sketch cleared the gate (`audit_outputs/cyber_insurance_evidence_package_v1_record_set_sketch_20260601_20260601T225054Z.md`, `blocking=0 warnings=0`).
- The 2026-06-01 `CURRENT_STATE_MAP.md` "False-positive / false-negative correction evidence loop" doctrine was added.
- The current research basis was captured at `Research/deep-research-report.md` and identifies the minimum viable Vendor Payment Change Review Packet artifacts (trigger record, known-good contact source record, callback execution note, approval trail, outcome record, exception/status record, supporting attachments).

**Authority:** Matt decides. This file defines the **internal** record format NorthStar uses to preserve false positives, false negatives, and the corrective-action trail behind them. It does not yet authorize any buyer-facing render of the same content.

**Boundary at a glance:**

- Uses only facts that exist in the repo today. No invented vendor IDs, datasets, dollar losses, manual catches, recovery outcomes, or detection rates beyond what the saved eval reports already contain.
- Operationalizes the `CURRENT_STATE_MAP.md` correction-evidence-loop doctrine (verbatim boundary: *"The correction must be scoped, proportionate, and retestable."*).
- Seeded with **one** real anchor — the 2026-05-22 vendor-invoice false-negative recovery (`vendor_invoice_fraud` recall 40% gate failure → no-spend prompt patch → 5/5 vf-001…vf-005 diagnostic pass).
- Forbidden-claim language remains forbidden. The seed record never says "prevented fraud," "stopped loss," "blocked an attack," "insurer-approved," "compliant," "certified," "premium reducer," "coverage-qualifying," or equivalent.

---

## §2 Purpose

The cyber-insurance evidence package will only earn underwriter, broker, and MSP trust if the underlying system can show how it handles its **own mistakes** — not just its successes. The deep-research report frames this directly (`Research/deep-research-report.md` §4): buyers and underwriters care about whether the control was applied, what the exceptions were, and whether corrective action is credible.

The Internal Correction-Evidence Record Set exists to:

1. **Preserve** misses and over-flags, instead of quietly tuning them away.
2. **Classify** each event by failure type (false negative, false positive, expectation-contract issue, fixture issue, prompt issue, detector issue, workflow issue).
3. **Record** why corrective action was warranted (real risk, buyer-trust impact, alert-fatigue risk, evidence gap, signed-spec mismatch, or expectation drift).
4. **Document** the scoped correction applied and the retest that proves it now holds.
5. **Anchor** the credibility narrative without inventing numbers or outcomes.

This record set is the *internal* surface. A possible *buyer-facing* render (sanitized summary, date range, correction count, proportionality note only) is described in §6 of this file, but is **not yet authorized** for external use.

---

## §3 Source anchors already in repo

Every entry in the seed record (§5) traces to one or more of the following paths as they exist in the repo today. The list is the audit trail for "no invented facts" — every numeric, every label, every action item below comes from one of these surfaces.

### §3.1 Saved eval reports (durable test-evidence artifacts)

| Path | What it preserves |
|---|---|
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md` | Full 40-case `grok-4` rerun: **36 / 40 passed**, **precision 100 %**, **FPR 0 %**, gate verdict **FAIL** because `vendor_invoice_fraud` recall was **40 % (2 / 5)** vs the required **60 %** floor. Per-subcategory breakdown saved verbatim. |
| `…/eval_report_2026_05_22_phase_1_5_vf-001_diagnostic.md` | Single-case `grok-4` diagnostic after the no-spend prompt patch — `vf-001` **PASS** (risk 88, vendor_fraud 88, action `block`). Includes raw structured LLM response. |
| `…/eval_report_2026_05_22_phase_1_5_vf-002_diagnostic.md` | `vf-002` **PASS** post-patch. |
| `…/eval_report_2026_05_22_phase_1_5_vf-003_diagnostic.md` | `vf-003` **PASS** post-patch. |
| `…/eval_report_2026_05_22_phase_1_5_vf-004_diagnostic.md` | `vf-004` **PASS** post-patch (thread-hijack pattern). |
| `…/eval_report_2026_05_22_phase_1_5_vf-005_diagnostic.md` | `vf-005` **PASS** post-patch (high-value EOD pressure pattern). |

### §3.2 Regression-coverage anchor

- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned` — pins the new "Phase 1.5 vendor-invoice recall floor" text inside `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`, so the corrective change cannot silently regress. (`PROGRESS.md` Task 4 names the test; the test function exists at line 494 of the file.)

### §3.3 Project-level tracking anchors

- `PROJECT_HANDSHAKE.md` entries **152–158** — the calibration-and-recovery arc that preserved failed cases, separated contract brittleness from model gaps, patched prompt / examples / dataset floors only where warranted, and reran live eval to a gate pass. (Note: entries 152–158 cover the **Bucket A–D calibration + Month 2 live-eval recovery + final recovery** sequence; the specific 2026-05-22 follow-on items live at entries 170–172 of the same file.)
- `PROGRESS.md` Tasks **3 – 6**:
  - Task 3 — Phase 1.5 A/B numeric proof (2026-05-22) FAIL verdict.
  - Task 4 — Vendor-invoice recall remediation (no-spend prompt patch) DONE 2026-05-22.
  - Task 5 — Targeted vendor-invoice live diagnostics, 5 / 5 PASS, DONE 2026-05-22.
  - Task 6 — Optional full rerun (operator decision; not auto-spent).
- `CURRENT_STATE_MAP.md` *False-positive / false-negative correction evidence loop* doctrine (added 2026-06-01) — defines the pattern this record set instantiates.
- `CURRENT_STATE_MAP.md` *Alert-fatigue doctrine* — pins why false positives are not free.
- `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` — draft framework for failure cards, retest linkage, evidence-required scoring, and failed-test acceptance discipline (companion reference; not amended here).
- `Research/deep-research-report.md` — current external research basis for the v1 Vendor Payment Change Review Packet shape.

### §3.4 Patch surface (named, not redescribed)

- `core/scoring/email_risk_scoring_agent.py` — `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` carries the new "Phase 1.5 vendor-invoice recall floor" block (per `PROGRESS.md` Task 4 and `PROJECT_HANDSHAKE.md` entry 171).
- Test-suite delta after patch: **+1 → 472 total tests passing** (per `PROJECT_HANDSHAKE.md` entry 171).

---

## §4 Record schema

Each correction-evidence entry uses the following YAML-shape. The schema is internal-credibility-grade: it is not a runtime contract, not a signed spec, and not a buyer-facing artifact in its raw form.

```yaml
correction_id: "cer-2026-05-22-001"               # stable internal identifier
surface: "scoring_prompt"                          # detector | scoring_prompt | digest | workflow | fixture | dataset_contract | rubric | other
failure_type: "false_negative"                     # false_negative | false_positive | expectation_contract | fixture | prompt | detector | workflow
case_ref:                                          # what was preserved (no raw payloads)
  eval_report_path: "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md"
  case_ids: ["vf-…"]                               # or aggregate metric ref
  metric: "vendor_invoice_fraud recall = 40% (2/5) vs 60% floor"
observed_behavior: |                               # <=240 chars, no raw email body, no real account numbers
  Full 40-case rerun on grok-4 produced 36/40 overall, precision 100%, FPR 0%, but vendor_invoice_fraud
  subcategory recall fell to 40% (2/5) against the 60% gate floor; this is a recall-specific miss, not
  a precision/FPR regression.
why_corrective_action_warranted:                   # one or more named reasons
  - "real_risk"                                    # a real fraud pattern was under-detected
  - "evidence_gap"                                  # signed-policy state could not produce credible package without rerun
  - "alert_fatigue_risk"                            # not the driver here (FPR 0%) — left unchecked
  - "buyer_trust"                                   # MSP / underwriter cannot accept a recall failure as "acceptable noise"
correction_applied:                                 # scoped, named change(s) only
  - kind: "prompt_floor"
    target: "core/scoring/email_risk_scoring_agent.py::NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT"
    change_description: "Added a small Phase 1.5 vendor-invoice recall floor enumerating the five weak fraud shapes seen in the rerun."
    method: "no-spend prompt-only patch (no schema, no dataset, no tenant override, no production_state, no loop change)"
retest_evidence:                                    # named, repo-resident proofs
  - "tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned"
  - "eval_report_2026_05_22_phase_1_5_vf-001_diagnostic.md"
  - "eval_report_2026_05_22_phase_1_5_vf-002_diagnostic.md"
  - "eval_report_2026_05_22_phase_1_5_vf-003_diagnostic.md"
  - "eval_report_2026_05_22_phase_1_5_vf-004_diagnostic.md"
  - "eval_report_2026_05_22_phase_1_5_vf-005_diagnostic.md"
proportionality_note: |                             # <=320 chars; explains why the correction is scoped and is not blanket loosening
  Patch was scoped to the locked system prompt only; no test was weakened, no expectation lowered, no
  dataset row passed by lowering its bounds, and precision / legit FPR were not relaxed. Coverage was
  pinned with a single regression test so the floor cannot silently regress.
recorded_at: "2026-06-01T00:00:00Z"
recorded_by: "operator-Matt + AI-drafted under operator review"
linked_artifacts:                                   # cross-refs for audit
  handshake_entries: [152, 153, 154, 155, 156, 157, 158, 170, 171, 172]
  progress_tasks: [3, 4, 5, 6]
  state_map_doctrines: ["False-positive / false-negative correction evidence loop", "Alert-fatigue doctrine"]
v1_render_handling: "summary_only"                  # summary_only | full_record_referenced | omitted (operator decides per package)
scope_limitations: "Email-fraud and inbox-layer MDR controls only. Does not cover MFA, EDR, backups, IR plans, patch management."
signed_by: null
```

**Field rules:**

- `case_ref` may carry case IDs (`vf-001` etc.) only because those IDs already exist in the saved eval reports. No new case IDs are minted in this file.
- `why_corrective_action_warranted` must include at least one of: `real_risk`, `buyer_trust`, `alert_fatigue_risk`, `evidence_gap`, `spec_mismatch`, `expectation_drift`. Multi-tagging is allowed.
- `correction_applied.method` should explicitly mark **no-spend** vs **spend** when known. The 2026-05-22 patch was no-spend.
- `proportionality_note` must explain why the correction is **not** blanket loosening. The verbatim doctrine boundary applies: *"This loop does not authorize weakening tests to make failures disappear. The correction must be scoped, proportionate, and retestable."*
- `v1_render_handling = summary_only` is the default for buyer-facing rendering. Promoting to `full_record_referenced` requires a separate operator pass.

---

## §5 Seed record — 2026-05-22 vendor-invoice false-negative recovery

The single seed entry follows. Every field is anchored to repo facts captured in §3; nothing is invented.

```yaml
correction_id: "cer-2026-05-22-001"
surface: "scoring_prompt"
failure_type: "false_negative"
case_ref:
  eval_report_path: "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md"
  case_ids: ["vf-001", "vf-002", "vf-003", "vf-004", "vf-005"]
  metric: "vendor_invoice_fraud subcategory recall = 40% (2/5) vs Phase 1.1 deep-dive §4.5 floor of 60%"
  related_subcategory_results:
    - "executive_impersonation 4/5 (80%) — passed floor"
    - "header_inconsistency 1/1 (100%) — passed floor"
    - "invoice_authenticity_anomaly 3/3 (100%) — passed floor"
    - "legit_calendar 3/3 — FPR clean"
    - "legit_hr 2/2 — FPR clean"
    - "legit_internal 5/5 — FPR clean"
    - "legit_newsletter 2/2 — FPR clean"
    - "legit_vendor_invoice 8/8 — FPR clean"
    - "lookalike_sender 2/2 (100%) — passed floor"
    - "wire_transfer_pressure 4/4 (100%) — passed floor"
  rerun_aggregate: "36/40 overall, precision 100%, FPR 0%, gate verdict FAIL"

observed_behavior: |
  The 2026-05-22 full Phase 1.5 grok-4 rerun produced 36/40 overall with precision 100% and FPR 0%,
  but vendor_invoice_fraud subcategory recall fell to 40% (2/5) against the required 60% floor.
  Precision and legit FPR stayed clean, so the failure is a recall-specific miss — the system was
  not over-flagging legit traffic; it was under-detecting a specific cluster of vendor-invoice
  fraud shapes.

why_corrective_action_warranted:
  - "real_risk"      # vendor_invoice_fraud is the densest payment-redirect attack shape in the dataset;
                     # missing 3/5 cases means the runtime would under-explain real-world variants.
  - "evidence_gap"   # the cyber-insurance evidence package depends on the runtime producing credible
                     # recall on vendor-invoice fraud; a recall failure leaves the v1 package without
                     # a defensible Detection-stage anchor.
  - "buyer_trust"    # an MSP, broker, or underwriter cannot accept a recall failure as "acceptable
                     # noise" — false-negative behaviour is the failure mode the package most needs
                     # to be honest about.
  # alert_fatigue_risk: not the driver (FPR 0%); recorded as monitored, not as a trigger.

correction_applied:
  - kind: "prompt_floor"
    target: "core/scoring/email_risk_scoring_agent.py::NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT"
    change_description: |
      Added a compact "Phase 1.5 vendor-invoice recall floor" block to the locked system prompt.
      The block pins the five weak vendor-invoice fraud shapes the rerun missed:
        1. Explicit new ACH / banking details with urgency.
        2. First invoice after onboarding, with remittance instructions only in the attached PDF.
        3. Updated remit-to address with old instructions invalid.
        4. Fake thread continuity (Re:, "following up as discussed below", or "as discussed" with
           no quoted history).
        5. High-value emergency invoice approval before EOD tied to shipment / operations pressure.
    method: "no-spend prompt-only patch (no schema change, no dataset change, no tenant override,
             no production_state change, no production-loop change, no additional provider calls)"
    test_baseline_delta: "+1 -> 472 passing (was 471)"

retest_evidence:
  - description: "Prompt-lock regression test pins the new floor text so it cannot silently regress."
    path: "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned"
  - description: "Single-case live grok-4 diagnostic after the patch — vf-001 PASS."
    path: "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-001_diagnostic.md"
    saved_result: "risk_score 88, vendor_fraud_score 88, recommended_action block"
  - description: "vf-002 PASS post-patch."
    path: "…/eval_report_2026_05_22_phase_1_5_vf-002_diagnostic.md"
    saved_result: "risk_score 65, vendor_fraud_score 60, recommended_action needs_review"
  - description: "vf-003 PASS post-patch."
    path: "…/eval_report_2026_05_22_phase_1_5_vf-003_diagnostic.md"
    saved_result: "risk_score 68, vendor_fraud_score 65, recommended_action needs_review"
  - description: "vf-004 PASS post-patch (thread-hijack pattern handled)."
    path: "…/eval_report_2026_05_22_phase_1_5_vf-004_diagnostic.md"
    saved_result: "risk_score 70, vendor_fraud_score 68, recommended_action needs_review"
  - description: "vf-005 PASS post-patch (high-value EOD pressure handled)."
    path: "…/eval_report_2026_05_22_phase_1_5_vf-005_diagnostic.md"
    saved_result: "risk_score 78, vendor_fraud_score 70, recommended_action needs_review"

proportionality_note: |
  The patch was scoped to the locked system prompt only. No test was weakened to make a failure
  disappear. No dataset row passed by lowering its bounds. No expectation contract was loosened.
  Precision and legit FPR were not relaxed (rerun and diagnostic reports both held 100% precision
  and 0% FPR on the surfaces they exercised). Coverage was pinned with a single regression test so
  the corrective change cannot silently regress, and the full rerun (`PROGRESS.md` Task 6) is
  preserved as an explicit operator-decision item rather than auto-spent.

what_this_record_does_NOT_claim:
  - "It does not claim NorthStar prevented an attack, blocked fraud, or stopped a loss."
  - "It does not claim the five vf-001..vf-005 diagnostics replace a full 40-case rerun; the full
     rerun is preserved as an operator decision (PROGRESS.md Task 6)."
  - "It does not claim the prompt floor will catch every vendor-invoice fraud variant; it pins the
     five weak shapes observed in the 2026-05-22 rerun and adds regression coverage so they cannot
     silently regress."
  - "It does not claim compliance, certification, insurer approval, premium reduction, or coverage
     qualification."
  - "It does not claim that detection layer recall alone is sufficient for an underwriter; the
     downstream Verification, Evidence, Audit Trail, and Outcome Documentation stages (see
     Cyber_Insurance_Evidence_Package_V1_Record_Set_Sketch.md §3) remain required."

recorded_at: "2026-06-01T00:00:00Z"
recorded_by: "operator-Matt + AI-drafted under operator review"

linked_artifacts:
  handshake_entries:
    description: "Calibration / recovery arc preserving failed cases, contract brittleness diagnosis, and recovery to gate pass; plus the 2026-05-22 follow-on items."
    entries: [152, 153, 154, 155, 156, 157, 158, 170, 171, 172]
  progress_tasks:
    description: "Phase 1.5 fail verdict, no-spend prompt patch, 5/5 vendor-invoice diagnostic recovery, optional full rerun deferral."
    tasks: [3, 4, 5, 6]
  state_map_doctrines:
    - "False-positive / false-negative correction evidence loop (2026-06-01)"
    - "Alert-fatigue doctrine (false positives matter even when not the current driver)"
  companion_research_inputs:
    - "4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Evidence_Pain_Points_Research_Map.md"
    - "4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Evidence_Package_V1_Synthesis.md"
    - "4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Evidence_Package_V1_Record_Set_Sketch.md"
  research_basis:
    - "Research/deep-research-report.md"

v1_render_handling: "summary_only"
scope_limitations: "Email-fraud and inbox-layer MDR controls only. Does not cover MFA, EDR, backups, IR plans, patch management."
signed_by: null
```

---

## §6 Buyer-facing / non-buyer-facing boundary

The full `why_corrective_action_warranted` rationale is **internal by default**. This protects three things at once: NorthStar's credibility (the operator can see exactly why a correction was applied), the SMB and MSP (they are not handed raw model-failure analytics they do not need), and the underwriter (they are not offered a noise channel that would dilute the actual control claim).

### §6.1 Internal (default — what stays in this record set)

Everything above. Full `case_ref`, full `observed_behavior`, full `why_corrective_action_warranted` reasoning, full `correction_applied` detail, full `retest_evidence` paths, full `proportionality_note`, full `linked_artifacts`. No buyer touches this record raw.

### §6.2 Buyer-facing render (only if the operator later authorizes it)

A sanitized summary may be added to a future package's audit-trail surface. The render rules are:

| Field | Buyer render |
|---|---|
| Date range | The period covered by the corrections being summarized (e.g. *"2026-05 to 2026-06"*). |
| Correction count | The number of correction-evidence records in scope (e.g. *"1 internal correction record on file for this period."*). |
| Proportionality note | A short paraphrase confirming the correction was scoped, retested, and not a test-weakening (e.g. *"corrective change scoped to the system-prompt layer; pinned with a regression test"*). |
| Coverage statement | A repeat of the §2 scope statement from the V1 Record-Set Sketch (email-fraud and inbox-layer MDR controls only). |
| Forbidden in buyer render | Raw `case_ids`, raw eval scores, raw subcategory recall percentages, raw vendor / tenant identifiers, raw `observed_behavior` text, and the unrendered `why_corrective_action_warranted` array. |

The buyer render is **not authorized here**. Any decision to surface a sanitized summary requires:

1. An explicit operator pass that names the package, period, and intended reader (broker, underwriter, MSP, SMB leadership).
2. A pass through the `Compliance_and_Trend_Watch_Process.md` §5 forbidden-language check.
3. A check against the V1 Record-Set Sketch §3.5 outcome-heading rules (no drift phrases like "prevented," "blocked," "stopped fraud").
4. A logged decision in `PROJECT_ACTIVITY_LOG.md` explaining what was rendered and why.

### §6.3 Doctrine boundary applied

From `CURRENT_STATE_MAP.md` (verbatim): *"This loop does not authorize weakening tests to make failures disappear. A false negative or false positive may justify a detector/prompt/workflow correction, a dataset-contract correction, or an expectation correction, but the reason must be recorded. The correction must be scoped, proportionate, and retestable."*

The seed record above meets that boundary: scoped to one prompt block, proportionate (single-floor addition addressing five named weak shapes), retestable (one prompt-lock regression test plus five saved diagnostic reports).

---

## §7 Non-authorizations

This record set does **not**:

- Authorize implementation, runtime code changes, runtime contract changes, schema changes, dataset changes, eval-harness changes, or production-loop changes.
- Advance D10. Discovery progress remains tracked solely in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv` per the cheaper-proof runbook bar.
- Authorize §13 sign-off, signature drafting, or signature wording for the Cyber Insurance Evidence Package Deep Dive.
- Authorize buyer-facing copy, MSP-facing copy, broker-facing copy, carrier-facing copy, or any external communication. The §6.2 buyer-render shape is described, not approved for use.
- Make any claim that NorthStar is **compliant**, **certified**, **insurer-approved**, **coverage-qualifying**, **premium-reducing**, or **fraud-preventing**. The runtime identifies and reports; corrective actions improve identification quality; nothing in this record asserts prevention.
- Weaken any existing test, lower any existing expectation bound, or otherwise tune away a failure. The doctrine boundary in §6.3 is binding here.
- Edit `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, the cheaper-proof runbook, the MSP discovery worksheet schema, the signed Client-Facing 5-Axis Email Scoring Rubric (§11 / §11.1 / §11.2), `Compliance_and_Trend_Watch_Process.md` §5, or any other §11- or §13-signed spec.
- Invent vendor IDs, datasets, dollar losses, manual-catch narratives, recovery outcomes, or detection rates that are not already preserved in the saved eval reports listed in §3.

If any phrase in this record set conflicts with a §11- or §13-signed spec, the signed spec wins.

---

**End of seed record set. One correction-evidence record on file (cer-2026-05-22-001). Operator decides whether to add additional anchors as further failures or over-flags are preserved.**
