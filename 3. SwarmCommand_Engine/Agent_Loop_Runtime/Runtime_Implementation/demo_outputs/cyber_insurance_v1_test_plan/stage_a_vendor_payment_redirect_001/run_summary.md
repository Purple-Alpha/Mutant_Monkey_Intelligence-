# Stage A Precursor-Chain Demo Run — §14 Fictional Case

**Status:** Pre-spec research-input demo run. **Not** a §14-conformant test-plan run. **Not** a §14.4 pass/fail verdict. **No** D10 progress. **No** §13 sign-off. **No** implementation. **No** client-facing copy.

## Run inputs

- Fixture: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json`
- Case ID: `cybins-v1-testplan-vendor-payment-redirect-001`
- Tenant: `bluefin-marine-supplies-demo` (fictional `.example` TLD)
- Sender: `accounts@billing.harborline-marine-services.example` (fictional)
- Auth posture (from fixture): SPF / DKIM / DMARC all pass.
- Scoring mode: `live-xai` (model `grok-4`)
- Digest mode: deterministic fake (cost-cap).
- Demo blackboard: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/blackboard`
- Runtime finding_id: `stage-a:cybins-v1-testplan-vendor-payment-redirect-001`

## Run outputs

- Emails analyzed: 1
- Emails failed: 0
- Digest record id: `33e171e2-28ca-4dd8-a461-a454cb24bfac`
- Workflow trigger id: `5859eaa4-9254-4347-aca9-dadc95a3dc25` (demo blackboard only; no external send)
- Digest top-risks count: 1
- Digest tasks count: 2

## Truthful mappings

- The runtime `TwoChannelOutcomeStatus` enum is `confirmed | rejected | unable_to_verify | expired`. The §14.3.5 operator-authored heading *"Vendor invoice review — payment change reviewed before action."* is **not** a runtime enum value. The outcome was recorded as `outcome_status="confirmed"` with `channel_kind="previously_known_phone"`; the `channel_description` field carries the §14.3.5 heading verbatim.
- The five `cyber_insurance_v1_*` §14.3 record types (Detection / Verification / Evidence / Audit Trail / Outcome Documentation) are **not** produced by this run. They are not implemented in `core/blackboard/models.py::RecordType` today.

## What this run DOES prove (dated / scoped)

- The locked production scoring prompt runs end-to-end against the §14 fictional case.
- The Stage A precursor chain (ingest → score → two-channel confirmation request + outcome → daily digest) is exercisable against the fixture.
- The runtime path produces durable, on-disk records in an isolated demo blackboard.

## What this run does NOT prove

- Does NOT produce the five §14.3 `cyber_insurance_v1_*` record types.
- Does NOT execute a §14.4 pass/fail verdict.
- Does NOT advance D10, §13 sign-off, or implementation authorization.
- Does NOT validate detection accuracy beyond what the saved scoring JSON shows. A single case is not a recall claim.
- Does NOT support any claim of compliance, certification, insurer approval, premium reduction, coverage qualification, or fraud prevention.

## Files produced

- Run summary (this file): `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md`
- Raw scoring response(s): `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/scoring_raw_response.json` (1 call(s))
- Demo blackboard (records on disk): `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/blackboard`

## Suggested PROJECT_ACTIVITY_LOG.md entry shape

```text
## 2026-MM-DD - Stage A precursor-chain demo run against §14 fictional case

**Actor:** operator-Matt (live run authorized).

**Files produced:** 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md, 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/blackboard/...

**Scoring mode:** live-xai (model grok-4)

**Boundary:** Research-input demo only. Not §14-conformant. Not a §14.4 verdict. No D10 progress.

**Next:** operator decides whether to promote the saved scoring response into the internal correction-evidence record set (per `Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` §4 schema) or leave as a one-off precursor demo.
```