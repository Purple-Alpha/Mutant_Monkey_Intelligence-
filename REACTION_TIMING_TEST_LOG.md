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

No reaction-timing tests have been recorded yet. The first record will be appended here when the operator authorizes the first Stage A test.

## Cross-references

- `AGENTS.md` section 5 — source of the reaction-timing test documentation rule.
- `VISION.md` — Stage A / B / C arc and seven non-negotiables that govern timing semantics.
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` — defines the `pending` and `outcome` event semantics referenced by `time_to_verification_request_ms` and `time_to_verification_outcome_ms`.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` section 5 — forbidden-language boundary that this ledger must respect.
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — future consumer of selected timing records under its own section 11 evidence-record contract.
- `PROJECT_ACTIVITY_LOG.md` — log of changes to this file.
- `MASTER_INDEX.md` — index entry for this ledger under Project Control Files.
