# Reaction Timing Test Log
NorthStar + SwarmCommand Venture

## Purpose

Durable timestamped ledger for every NorthStar reaction-timing test. Required by the reaction-timing test documentation rule in `AGENTS.md` section 5 (added 2026-05-28).

A reaction-timing test counts as evidence only when it leaves a record in this ledger with timestamps, verdict, and evidence artifact references. Positive, partial, failed, and blocked results all belong here. Memory of "we ran one" is not evidence.

## Scope

In scope:

- Stage A reaction-timing measurements: time to detection, time to verification request, time to verification outcome, time to case closure.
- Test runs against demo tenants, isolated sandboxes, and, when separately authorized, real-mailbox business data.
- Manual runs by the operator and automated runs by a test harness.

Out of scope:

- Production tenant operational timing. Different surface; needs its own spec before any record lands here.
- Client-facing performance claims, service-level promises, or "we detect in X seconds" outreach copy. This ledger is internal evidence only.
- Stage B / Stage C autonomous-action timing. When those stages ship, a separate timing-evidence spec governs them.

## Authority

- Operator-maintained. Matt is the only authority on which reaction-timing tests run and whether their verdicts are accepted.
- Verdicts are recorded by the runner; acceptance is operator-only.
- A record in this ledger does not by itself authorize any client-facing claim about timing.

## Closed verdict enum

- `pass` — Actual result matched expected result on every required field.
- `partial` — Some expected fields matched; at least one expected field missed or partially met.
- `fail` — Actual result did not match expected result.
- `blocked` — Test could not run (precondition unmet, kill switch engaged, dependency missing, environment unavailable, operator stop, etc.). `blocking_reason` is required.

A test that emits no verdict is not a test. If a verdict cannot be recorded, the run does not count.

## Timing field semantics

- `time_to_detection_ms` — Wall-clock elapsed from the earliest inbound-evidence timestamp the runner can observe (e.g. `EmailInboundPayload.ingested_at`) to the analysis record's `analysis_completed_at`. If no analysis record exists, `null` with reason.
- `time_to_verification_request_ms` — Wall-clock elapsed from analysis completion to the corresponding `TWO_CHANNEL_CONFIRMATION` `pending` event being written. If the scenario does not require verification, `null` with reason `"verification not required by scenario"`.
- `time_to_verification_outcome_ms` — Wall-clock elapsed from the `pending` event to the `outcome` event (any `outcome_status`). If no outcome was recorded inside the test window, `null` with reason `"outcome not recorded inside test window"`.
- `time_to_case_closure_ms` — Wall-clock elapsed from inbound-evidence timestamp to the case-closure artifact reference. If no case-closure artifact, `null` with reason.

Operator time and machine time must not be conflated. If a timing point depends on human action, record `human_in_loop: true` and break out `human_segment_ms`. Hiding human latency inside system latency is a recording fault.

## Record schema

Each test run is one record. New records append to the end of this file under the `## Records` section.

```yaml
test_id: "rxt-2026-05-28-001"             # stable, unique, opaque identifier
scenario_name: ""                          # human-readable scenario label
stage_scope: "Stage A"                    # closed enum; Stage A only in v1
run_started_at: "ISO-8601 UTC"
run_finished_at: "ISO-8601 UTC"
operator_or_runner: ""                     # Matt | test-harness | named runner
environment: ""                            # demo | sandbox | real-mailbox-authorized
input_artifact_path: ""                    # path to scenario input, or null with reason
expected_result: ""                        # free text or structured expectation block
actual_result: ""                          # free text or structured actual block
verdict: "pass | partial | fail | blocked"
blocking_reason: null                      # required when verdict=blocked, else null

time_to_detection_ms: null                 # int milliseconds, or null with reason in notes
time_to_verification_request_ms: null
time_to_verification_outcome_ms: null
time_to_case_closure_ms: null

human_in_loop: false
human_segment_ms: null

email_inbound_record_id: null
email_analysis_record_id: null
two_channel_request_record_id: null
two_channel_outcome_record_id: null
case_closure_artifact_or_record_id: null

evidence_artifact_paths: []                # durable paths or Blackboard record IDs

notes: |
  Free-text notes. Include surprises, deviations from expected, manual
  interventions during the run, and the reason for any null timing field.
```

A field that does not apply to the scenario is recorded as `null` with a reason in `notes`. A field that is missing because the runner failed to capture it is the same — record `null` and name what was not captured. Omission is not allowed. The point of this rule is to keep fake-clean data out of the ledger.

## Boundary statement

This ledger is internal evidence. It is not a service-level agreement, not a client-facing performance claim, not an underwriter-facing or carrier-facing claim, and not a forecast of future detection, verification, or case-closure timing in production. Timing recorded here describes a specific test run, against a specific scenario, in a specific environment, on a specific date.

The Cyber Insurance Evidence Package and any other buyer-facing surface may, when its own section 11 contract allows, reference selected records here as evidence that a particular test was run. It may not paraphrase records into a performance promise.

## First-run template (empty)

Use this template verbatim for the first reaction-timing test. Fill every field. Use `null` plus a reason in `notes` when a value does not exist; do not omit fields.

```yaml
test_id: "rxt-YYYY-MM-DD-001"
scenario_name: ""
stage_scope: "Stage A"
run_started_at: ""
run_finished_at: ""
operator_or_runner: ""
environment: ""
input_artifact_path: ""
expected_result: ""
actual_result: ""
verdict: ""
blocking_reason: null

time_to_detection_ms: null
time_to_verification_request_ms: null
time_to_verification_outcome_ms: null
time_to_case_closure_ms: null

human_in_loop: false
human_segment_ms: null

email_inbound_record_id: null
email_analysis_record_id: null
two_channel_request_record_id: null
two_channel_outcome_record_id: null
case_closure_artifact_or_record_id: null

evidence_artifact_paths: []

notes: |

```

## Records

```yaml
test_id: "rxt-2026-05-29-001"
scenario_name: "Fictional vendor-payment-change Stage A evidence case"
stage_scope: "Stage A"
run_started_at: "2026-05-29T18:53:13.775150+00:00"
run_finished_at: "2026-05-29T18:53:13.819553+00:00"
operator_or_runner: "Cursor inline test runner"
environment: "demo"
input_artifact_path: null
expected_result: "One fictional vendor-payment-change email produces one inbound record, one high-risk analysis, a two-channel pending event, a two-channel confirmed outcome, one daily digest, one send_daily_digest workflow trigger, and all four timing fields are captured."
actual_result: "One inbound record, one analysis record, two two-channel confirmation records, one daily digest record, and one send_daily_digest workflow trigger were produced. Analysis risk_score=91, vendor_fraud_score=92, recommended_action=block, behavioral_deviation_flags=[new_banking_instructions, mismatched_invoice_vendor_name, urgency_paired_with_finance], verification_outcome_status=confirmed."
verdict: "pass"
blocking_reason: null

time_to_detection_ms: 9
time_to_verification_request_ms: 9
time_to_verification_outcome_ms: 0
time_to_case_closure_ms: 35

human_in_loop: false
human_segment_ms: null

email_inbound_record_id: "42e39560-8c30-4cfe-a335-f26c88a69ad3"
email_analysis_record_id: "910cac32-1b0e-4c13-8204-d7ea481a8717"
two_channel_request_record_id: "d51493d0-dd90-45c4-9b4a-211554d2b0b1"
two_channel_outcome_record_id: "619bcffd-d24c-4e50-bf22-c32d0accaf1b"
case_closure_artifact_or_record_id: "bdd75c92-b62e-4d0c-aa18-24c64ea21239"

evidence_artifact_paths:
  - "C:\\Users\\mattn\\AppData\\Local\\Temp\\northstar_reaction_timing\\rxt-2026-05-29-001\\case_closure_digest.md"

notes: |
  Authorized one-hour bounded Stage A system test using fictional/demo data only.
  The test used existing ingest, scoring, two-channel confirmation, and daily-digest APIs from the runtime with deterministic fake LLM clients. No runtime code was edited.
  The fictional input email was constructed inside the one-shot inline runner, so no repository input fixture was created. The generated case-closure digest was written outside the repository under the local temp path named in evidence_artifact_paths; the durable project record is this ledger entry plus the Blackboard record IDs above.
  time_to_detection_ms uses EmailInboundPayload.received_at to EmailAnalysisPayload.produced_at.
  time_to_verification_request_ms uses EmailAnalysisPayload.produced_at to the two-channel pending requested_at.
  time_to_verification_outcome_ms uses pending requested_at to outcome outcome_at. The measured value rounded to 0 ms because the demo outcome was recorded immediately after the pending event.
  time_to_case_closure_ms uses EmailInboundPayload.received_at to the DailyDigest Blackboard record created_at.
  No real client data, real mailbox, external sending, production action, or live LLM call was used.
```

```yaml
test_id: "rxt-2026-05-29-003"
scenario_name: "Fixture-backed vendor-payment-change Stage A evidence case"
stage_scope: "Stage A"
run_started_at: "2026-05-29T19:00:10.060955+00:00"
run_finished_at: "2026-05-29T19:00:10.110914+00:00"
operator_or_runner: "Codex fixture test runner"
environment: "demo"
input_artifact_path: "3. SwarmCommand_Engine\\Agent_Loop_Runtime\\Runtime_Implementation\\tests\\fixtures\\reaction_timing\\stage_a_vendor_payment_change.json"
expected_result: "Fixture-driven run produces one inbound record, one high-risk analysis, a two-channel pending event, a confirmed two-channel outcome, one daily digest case-closure artifact, and all four reaction-timing fields."
actual_result: "Fixture-backed run produced one inbound record, one analysis record, two two-channel confirmation records, one daily digest record, and one send_daily_digest workflow trigger. Analysis risk_score=91, vendor_fraud_score=92, recommended_action=block."
verdict: "pass"
blocking_reason: null

time_to_detection_ms: 130071
time_to_verification_request_ms: 0
time_to_verification_outcome_ms: 12
time_to_case_closure_ms: 130101

human_in_loop: false
human_segment_ms: null

email_inbound_record_id: "d45e6711-f387-458b-a090-65de130a5a0f"
email_analysis_record_id: "8bb20efd-7672-486c-a8a7-e958b9e3fa82"
two_channel_request_record_id: "3a7f306c-3394-4212-9519-7eb6c79a2417"
two_channel_outcome_record_id: "1bd19f0d-3361-4f58-be62-605470469d4a"
case_closure_artifact_or_record_id: "f7120fd7-6d95-4d12-8ec3-88588d7c421f"

evidence_artifact_paths:
  - "3. SwarmCommand_Engine\\Agent_Loop_Runtime\\Runtime_Implementation\\tests\\fixtures\\reaction_timing\\stage_a_vendor_payment_change.json"
  - "C:\\Users\\mattn\\AppData\\Local\\Temp\\northstar_reaction_timing\\rxt-2026-05-29-003\\case_closure_digest.md"

notes: |
  Authorized follow-up test for the gap surfaced by rxt-2026-05-29-001: the original input email was constructed inline, so no repository fixture existed.
  This run used the tracked fixture at input_artifact_path and carried the fictional case through the same Stage A chain with no runtime code edits.
  The first fixture-backed attempt during this work failed before a ledger record was captured because the runner used an invalid two-channel channel_kind value (`known_phone_number`). The corrected run used the signed workflow enum value `previously_known_phone`. This mistake is recorded here because repeatability requires runner inputs to respect the closed enum contract.
  time_to_detection_ms and time_to_case_closure_ms are larger than rxt-2026-05-29-001 because they measure from the fixture's fixed EmailInboundPayload.received_at value (`2026-05-29T18:58:00+00:00`) rather than from the wall-clock run start. The timing is valid for this fixture but should not be read as production latency.
  time_to_verification_request_ms is 0 because the pending verification event reused the analysis produced_at timestamp as its requested_at.
  No real client data, real mailbox, external sending, production action, runtime code edit, or live LLM call was used.
```

## Cross-references

- `AGENTS.md` section 5 — source of the reaction-timing test documentation rule.
- `VISION.md` — Stage A / B / C arc and seven non-negotiables that govern timing semantics.
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` — defines the `pending` and `outcome` event semantics referenced by `time_to_verification_request_ms` and `time_to_verification_outcome_ms`.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` section 5 — forbidden-language boundary that this ledger must respect.
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — future consumer of selected timing records under its own section 11 evidence-record contract.
- `PROJECT_ACTIVITY_LOG.md` — log of changes to this file.
- `MASTER_INDEX.md` — index entry for this ledger under Project Control Files.
