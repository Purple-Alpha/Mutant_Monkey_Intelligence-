# Stage A Precursor-Chain Demo — Run Instructions

> **Read `README.md` first** for the boundary statement. This file is operator instructions only.

## 0. Prerequisites

- Linux primary repo: `/home/socialarchitect/northstar` (do not run from the Windows backup copy).
- The runtime venv already in use today:

  ```text
  3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/.venv
  ```

- `.env` at `/home/socialarchitect/northstar/.env` already carries `XAI_API_KEY` (you set this earlier today; the V1 Synthesis gate confirmed it).
- The `openai` Python package must be installed in the venv (used as the OpenAI-compatible client wire for xAI). If not present:

  ```bash
  pip install openai
  ```

  This is the same dependency the existing `core.scoring.eval.fraud_eval_harness --provider xai` path uses. No new dependency is being introduced.

## 1. Activate the venv

```bash
cd /home/socialarchitect/northstar
source "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/.venv/bin/activate"
```

## 2. Export the API key (only for the live-xai mode)

```bash
export XAI_API_KEY=$(grep -E '^XAI_API_KEY=' .env | head -n1 | cut -d= -f2-)
[ -n "$XAI_API_KEY" ] && echo "XAI_API_KEY ok" || echo "XAI_API_KEY MISSING"
```

If you see `XAI_API_KEY MISSING`, stop and either fix `.env` or pass `--scoring-mode fake` below.

## 3. Smoke-test with zero spend first (recommended)

```bash
python "Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/runner.py" \
    --scoring-mode fake
```

Expected: ~5 second runtime, no API call. Inspect the outputs:

```bash
cat "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md"
ls -la "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/blackboard/"
```

If the summary looks right and the blackboard contains records, you have confirmed the route works on your machine before any spend.

## 4. Authorized live run (the one that costs)

```bash
python "Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/runner.py" \
    --scoring-mode live-xai \
    --model grok-4
```

Expected:

- One real `grok-4` API call (~5–15 seconds wall time; cost is in the same band as a single `vf-001` diagnostic from 2026-05-22).
- The previous demo blackboard is wiped and rebuilt.
- A new `scoring_raw_response.json` is written next to the summary; it captures the verbatim model output for the §14 fictional case.

Inspect:

```bash
cat "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/run_summary.md"
python -c "import json,sys; print(json.dumps(json.loads(open('3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/demo_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/scoring_raw_response.json').read()), indent=2)[:4000])"
```

## 5. What to check on the live response (no gate, just inspection)

The fixture is the deliberate auth-pass-but-content-risk case. A *useful* model response would:

- Recognize the SPF / DKIM / DMARC pass posture explicitly.
- Still treat the content (new ACH instructions + end-of-week urgency) as elevated risk.
- Recommend `needs_review` or `block`, not `safe`.
- Cite `new_banking_instructions` and `urgency_paired_with_finance` (or equivalents) in `behavioral_deviation_flags`.

If the response misses these, that is itself evidence — capture it as a new entry in the Internal Correction-Evidence Record Set (§4 schema in `Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md`). **Do not** tune the prompt to make the failure disappear; the doctrine boundary applies (`CURRENT_STATE_MAP.md` correction-evidence loop).

## 6. After-run housekeeping

1. **Activity-log entry.** Append to `PROJECT_ACTIVITY_LOG.md` using the template at the bottom of the generated `run_summary.md`. Note the date, scoring mode, and whether the captured scoring response will be promoted into the correction-evidence record set.

2. **Do not commit `demo_outputs/`.** The directory is `.gitignore`d by convention (mirrors the precedent `inbox_shield_daily_digest_demo` outputs). If you want to keep a copy of the saved scoring JSON, copy it to a path outside `demo_outputs/` and reference it explicitly in the activity-log entry.

3. **Do not invoke `complete_gate.py`** on the activity-log update alone. Bundle it with the next pre-spec gate-able change. (This run is operator-side execution, not a Cursor pre-spec artifact, so it does not need a per-run gate audit.)

## 7. Failure modes and what to do

| Symptom | What it means | What to do |
|---|---|---|
| `XAI_API_KEY is not set` | Env var missing in this shell | Re-run §2 of these instructions, or use `--scoring-mode fake`. |
| `The 'openai' package is not installed` | `openai` not in venv | `pip install openai` inside the activated venv. |
| `fixture missing at …` | Path drift | Check the fixture is at the expected location; do not rename it. |
| `scoring failed for 1 email(s)` | Live response did not parse against the locked scoring schema | Inspect `demo_outputs/.../blackboard/` for the failure record; this is a useful diagnostic — capture it as a correction-evidence entry per the doctrine. |
| `two_channel_confirmation: …` GovernanceError | Schema / contract violation in the runner's call | Stop. Do not edit the runtime to make it pass. Report the exact error so the runner can be adjusted (this is a runner bug, not a runtime bug). |
| Cost surprise | Live call exceeded a single-call budget | Stop. Re-run with `--scoring-mode fake` while you diagnose. The runner only calls the LLM once per invocation. |

## 8. Boundary reminder

- This is **not** a §14 run.
- This is **not** D10 evidence.
- This is **not** §13 sign-off.
- This is **not** client-facing copy.
- This **is** a small, repeatable, operator-authorized demo that captures a real-model response on the central buyer narrative case, so the project has an anchor that's better than words.
