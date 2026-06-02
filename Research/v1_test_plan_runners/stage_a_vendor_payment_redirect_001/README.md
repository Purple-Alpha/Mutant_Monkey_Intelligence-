# Stage A Precursor-Chain Demo Runner — §14 Fictional Case

## Status / boundary header

**Status:** Pre-spec research-input runner. Operator-run only. **NOT** a §14-conformant test-plan run. **NOT** implementation. **NOT** runtime code. **NOT** part of any agent loop or CI suite. **NOT** client-facing.

**Captured:** 2026-06-01 by Cursor (Claude Opus 4.7) at operator request, after the V1 Record-Set Sketch (`audit_outputs/cyber_insurance_evidence_package_v1_record_set_sketch_20260601_20260601T225054Z.md`, `blocking=0 warnings=0`) and the Internal Correction-Evidence Record Set (`audit_outputs/cyber_insurance_internal_correction_evidence_record_set_20260601_20260601T233627Z.md`, `blocking=0 warnings=0`) both cleared the gate.

**Authority:** Matt decides. This runner is *prep only* — Cursor drafted it; Matt authorizes any live XAI spend by choosing the `--scoring-mode live-xai` invocation. The default invocation pattern keeps spend explicit.

## What this runner is

A small operator-run Python script that exercises the existing Stage A *precursor chain* end-to-end against the §14.5 fictional fixture:

`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json`

The chain it exercises (all existing runtime entry points; no new code):

1. `ingest_email` — ingest the fictional `bluefin-marine-supplies-demo` payload.
2. `run_email_risk_scoring_cycle` — score it with the locked production prompt.
   - `--scoring-mode live-xai` uses real `grok-4` (one call, small spend).
   - `--scoring-mode fake` uses a deterministic stub (zero spend).
3. `record_confirmation_request` — record the two-channel confirmation request raised against the new banking-detail change.
4. `record_confirmation_outcome` — record the outcome via the previously-known-phone channel.
5. `run_daily_digest_cycle` — render the digest section that closes the case for the day (deterministic fake LLM client; the digest text is not the artifact worth a live call here).

Outputs land under `Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/` — an **isolated demo blackboard**, plus a `run_summary.md` and (if live mode was used) a `scoring_raw_response.json` capturing the model's verbatim output.

## What this runner is NOT

- It does **not** produce the five §14.3 `cyber_insurance_v1_*` record types (Detection / Verification / Evidence / Audit Trail / Outcome Documentation). Those record types are not implemented in `core/blackboard/models.py::RecordType` today; implementing them is gated on §11 sign-off of `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, which is gated on §13 sign-off, which is gated on D10.
- It does **not** evaluate the §14.4 pass/fail criteria. There is no v1 verdict from this run.
- It does **not** write to `production_state`, tenant overrides, the policy pipeline, or any external system.
- It does **not** make any send / mailbox / network call beyond the (operator-authorized) XAI scoring call.
- It does **not** advance D10, §13 sign-off, implementation authorization, pricing, or any client-facing claim of compliance / certification / insurer approval / premium reduction / coverage qualification / fraud prevention.
- It does **not** target the spec-named `audit_outputs/cyber_insurance_v1_test_plan/...` paths reserved for a future §14-conformant run. Outputs go under `demo_outputs/...` so the spec paths stay unclaimed until implementation lands.

## Two truthful mappings the operator should know

1. **Outcome status mapping.** The §14.3.5 spec names the operator-authored outcome heading verbatim: *"Vendor invoice review — payment change reviewed before action."* The runtime `TwoChannelOutcomeStatus` enum (`core/blackboard/models.py`) is the closed set `confirmed | rejected | unable_to_verify | expired`. The runner records `outcome_status="confirmed"` with `channel_kind="previously_known_phone"` and a `channel_description` that ties the runtime outcome to the §14.3.5 heading. This is the most truthful current mapping; a future §14-conformant run would either add a new runtime enum value or render the heading in the §14.3.5 layer, **not** here.

2. **Auth-pass-but-content-risk fixture.** The fixture deliberately has SPF / DKIM / DMARC all passing. The point of running this with real `grok-4` is to capture, on disk, the model's reasoning for a content-risk-driven `needs_review` (or `block`) recommendation despite a clean auth posture. That saved JSON response becomes durable evidence for the central buyer narrative.

## Files in this directory

- `README.md` — this file (boundary + intent).
- `RUN_INSTRUCTIONS.md` — operator steps (venv, env vars, command, expected runtime, post-run inspection, activity-log entry shape).
- `runner.py` — the inline runner. Path-invoked, not module-invoked, so it does not need to live on `PYTHONPATH`.

## Non-authorizations (binding)

- No commits, no pushes, no signed-spec edits.
- No D10 advancement, no §13 sign-off.
- No implementation of the five `cyber_insurance_v1_*` record types.
- No client-facing copy generated from the run's outputs.
- No claim of compliance, certification, insurer approval, premium reduction, coverage qualification, or fraud prevention.
- No test-suite addition; this runner is not a test.

If any phrase in this directory conflicts with a §11- or §13-signed spec, the signed spec wins.
