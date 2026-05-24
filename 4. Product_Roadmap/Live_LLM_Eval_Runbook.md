# Live LLM Eval Runbook (Phase 1.1 Pass Gate)

This is the operator-facing handoff document for the Month 2 / Phase 1.1 live eval pass-gate run. The harness, dataset, pass-gate logic, llm-safe wrapper, and live-client wrappers are all landed. This document tells the operator (Matt or a delegate) exactly how to run the eval against a real LLM and how to capture the resulting markdown report into the activity log.

## Why this is an operator runbook, not an agent task

The eval call goes over a real network to a real LLM provider. An automated agent running inside the Cursor sandbox does not have access to provider API keys and should not be issuing live LLM calls on the operator's behalf — that violates both the LLM Usage Policy (§5: defensive framing, synthetic data only, must begin with the locked system prompt) and the kill-switch ergonomics (an operator should always be the one pulling the trigger on a live eval).

So: an agent prepares the runtime, lands the tests, and writes this runbook. The operator runs the eval.

## Prerequisites

1. **Python 3.10+** (matches what the runtime uses elsewhere).
2. **Pydantic 2** (already used across the runtime).
3. **Provider SDK**, one of:
   - `pip install anthropic` for Claude models, OR
   - `pip install openai` for GPT models, OR
   - `pip install openai` for xAI / Grok models (the `xai` provider uses xAI's OpenAI-compatible endpoint).
4. **API key** exported in the shell that runs the harness:
   - `$env:ANTHROPIC_API_KEY = "sk-ant-..."` (PowerShell), OR
   - `export ANTHROPIC_API_KEY="sk-ant-..."` (bash), OR
   - same with `OPENAI_API_KEY`, OR
   - same with `XAI_API_KEY`.
5. **Cwd** must be the runtime implementation directory:
   ```text
   3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation
   ```

## Pre-flight checklist

Before the live run, confirm:

- [ ] `python -m pytest tests -q` exits 0 (291 passing baseline).
- [ ] `python -m core.scoring.eval.fraud_eval_harness --dry-run` prints a markdown report ending with `**Gate verdict:**` (the dry-run gate verdict will say FAIL because the stub client returns the same scores for every case; this is expected and only verifies plumbing).
- [ ] `Internal_Tools/precommit_llm_safety_hook.sh` and `.github/workflows/llm_safety_check.yml` agree byte-for-byte on `UNSAFE_PATTERNS` (the third copy in `core/scoring/eval/llm_safety.py::UNSAFE_PATTERNS` is unit-tested against the same expected set).
- [ ] You have read the LLM Usage Policy (§5 in particular) and the System Prompt Template. The harness will refuse to forward an LLM call whose `system` prompt does not begin with `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT[:200]`, so the locked scoring prompt is enforced at the wrapper boundary.

## The live run

### Anthropic (Claude)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

python -m core.scoring.eval.fraud_eval_harness `
  --provider anthropic `
  --model claude-sonnet-4-5 `
  --report-out eval_report_2026_05_20.md
```

### OpenAI (GPT)

```powershell
$env:OPENAI_API_KEY = "sk-..."

python -m core.scoring.eval.fraud_eval_harness `
  --provider openai `
  --model gpt-5 `
  --report-out eval_report_2026_05_20.md
```

### xAI (Grok)

```powershell
$env:XAI_API_KEY = "xai-..."

python -m core.scoring.eval.fraud_eval_harness `
  --provider xai `
  --model grok-4 `
  --report-out eval_report_2026_05_20_xai.md
```

Use the exact Grok model id enabled for your xAI account. The `xai` provider uses the OpenAI Python SDK against `https://api.x.ai/v1`, so no separate xAI Python package is required.

The harness will:

1. Load the 40-case dataset at `core/scoring/eval/fraud_eval_dataset.jsonl`.
2. Enforce `--llm-safe` (default ON): dataset path is allowlisted, dataset content is scanned against `UNSAFE_PATTERNS`, sha256 digests of every prompt + response are appended to `core/scoring/eval/operator_state/llm_usage.jsonl`.
3. Call the provider 40 times with the locked `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` (the wrapper refuses to forward any call where the system prompt does not start with the locked prefix — defense in depth).
4. Parse each response, check against the case's expected bounds, including the required-subset `behavioral_deviation_flags` contract on the 20 fraud cases (and the optional `forbidden_behavioral_deviation_flags` contract where pinned), aggregate, compute the §4.5 pass gate, print the markdown report to stdout, and write it to `eval_report_2026_05_20.md`.
5. Exit `0` if the pass gate is met, `1` if any criterion misses, `2` on a safety / configuration error.

## One-case diagnostics

If a live run returns `0 / 40` or otherwise looks structurally wrong, do not rerun the full eval immediately. Capture one synthetic case with raw model output:

```powershell
python -m core.scoring.eval.fraud_eval_harness `
  --provider xai `
  --model grok-4 `
  --case-id vf-001 `
  --show-failure-details `
  --show-raw-response `
  --report-out eval_report_2026_05_20_xai_vf_001_debug.md
```

Use the same provider/model/env-var setup as the full run. The diagnostic flags do not relax the pass gate; they only print the per-case `failure_reason`, failed assertions, and raw LLM response after the normal markdown report. Do **not** combine `--dry-run` with `--provider`: `--dry-run` deliberately skips live-model calls and cannot reveal provider output.

### Pass gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold |
|---|---|
| Precision on fraud cases | >= 80% |
| False positive rate on legit cases | <= 10% |
| Per-fraud-subcategory recall | >= 60% on each of the six fraud subcategories |

A "false positive" is a legit case whose `recommended_action` came back as `"block"`. `"needs_review"` is allowed on legit cases.

## Recording the result

Whatever the gate verdict, append a new entry to `PROJECT_ACTIVITY_LOG.md` with this shape (replace the bracketed bits with real values):

```markdown
## YYYY-MM-DD - Phase 1.1 Live LLM Eval [PASS|FAIL]
**Actor:** Matt (operator) / Claude (filing)

**Action:** Verified

**Files Changed:**
- `PROJECT_ACTIVITY_LOG.md` (this entry)
- `PROJECT_HANDSHAKE.md` (advanced the active build target if PASS)

**Command:**

```text
python -m core.scoring.eval.fraud_eval_harness --provider [anthropic|openai|xai] --model [model-id]
```

**Eval Report:**

[paste the markdown report from --report-out here verbatim]

**Verification:**
- Provider: [anthropic|openai|xai]
- Model: [model-id]
- Dataset sha256: [sha256 of core/scoring/eval/fraud_eval_dataset.jsonl]
- Usage log: core/scoring/eval/operator_state/llm_usage.jsonl, [N] rows appended

**Next Step:**
[On PASS: close Month 2, hand off to Month 3 Phase 1.2 Ransomware Precursor Detection.]
[On FAIL: file follow-up tasks per the failed criteria in the report. Re-run after fixes.]
```

If the run PASSES, also update `PROJECT_HANDSHAKE.md`'s "Current Active Build Track" to mark Month 2 complete and bump the priority order so "Month 3 — Phase 1.2 Ransomware Precursor Detection" becomes #1.

If the run FAILS, do not modify the active build track. File a follow-up under the existing priority #1 ("Live LLM eval pass gate") describing which criterion missed.

## Failure modes the harness handles cleanly

| Failure | Exit code | Where it surfaces |
|---|---|---|
| Provider SDK not installed | 2 | stderr: `failed to build {provider} client: The '{provider}' package is not installed.` (`xai` uses the `openai` SDK) |
| API key env var not set | 2 | stderr: `API key env var 'X' is not set. Export it in the shell before running the live eval.` |
| Unsafe dataset path (e.g. `customer_emails.jsonl`) | 2 | stderr: `llm-safe guard rejected the run: dataset path component '...' matches the unsafe path allowlist substring '...'.` |
| Dataset contains a blocklist term | 2 | stderr: `llm-safe guard rejected the run: unsafe-pattern scan failed on ...` |
| Provider returned non-JSON | 1, per-case | report markdown: case marked `invalid_json:...` |
| Provider returned wrong schema | 1, per-case | report markdown: case marked `schema_mismatch:N_errors` |
| Provider raised mid-run | 1, per-case | report markdown: case marked `llm_client_raised:Name:msg`; subsequent cases continue |
| All cases pass per-case but aggregate gate misses | 1 | report markdown's `**Gate verdict:** FAIL` |
| All criteria met | 0 | report markdown's `**Gate verdict:** PASS` |

## Bypass surfaces (use deliberately)

- `--no-llm-safe` disables the path allowlist + dataset scan + sha256 usage log. Reserved for explicitly-flagged local experimentation. CI must never invoke the harness with this flag (the LLM_Workflow_Integration_Plan §A↔B↔C synchronization rule treats this as out of band).
- `--allow-unsafe-dataset-path` bypasses only the path allowlist. Use for audited extended datasets whose path happens to contain a blocklist substring.
- `--api-key-env <VAR>` reads the API key from a different env var name (default: `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `XAI_API_KEY`).
- `--dataset <path>` runs against an alternate dataset (still subject to all safety checks unless bypassed). The shipped 40-case dataset is the only one with curated expected bounds; pointing at a different file is meaningful only for experimentation.

## Month 2 recall patch — what to expect on the next live run

The `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` carries a small recall patch (landed after the calibrated 40-case Grok run) that adds three targeted rubric refinements plus a false-positive protection block:

1. **Banking-instruction strength.** Any explicit change-of-destination phrase ("new ACH details", "updated remit-to address", "please use the new banking details", "payment details have changed", "remit to the address/account below") OR banking destination details that appear only inside an attached PDF / payment-request attachment forces `vendor_fraud_score ≥ 60` (with any sender anomaly) or `vendor_fraud_score ≥ 45` (in isolation). `new_banking_instructions` must be emitted.
2. **Sender-domain obfuscation.** `lookalike_sender_domain` is emitted for Unicode lookalikes inside the sender domain, punycode (`xn--`), homoglyph substitutions, and near-variant domains of any vendor or brand referenced elsewhere in the email. When Unicode obfuscation is also present in filenames / headers / body, `unusual_unicode_obfuscation` is emitted in addition. A first-time or unknown sender alone is explicitly **not** enough.
3. **Invoice authenticity & PDF-only banking changes.** `invoice_authenticity_score` falls in 0–40 whenever the extracted invoice text names a different vendor than the sender domain, banking details live only inside the attached PDF, or the invoice date is inconsistent with the email's received date. `recommended_action` leans to `needs_review` or `block` (preferring `block` when other fraud cues are layered in). `mismatched_invoice_vendor_name` is emitted on the vendor-name mismatch case.

The patch also adds an explicit **false-positive protection** guardrail block: routine matching-domain invoices stay `safe`; `new_banking_instructions` only fires on actual banking changes; `lookalike_sender_domain` only fires on actual domain anomalies; `vendor_fraud_score` is capped at 40 when there is no payment ask, no banking detail, and no invoice attachment; polite reminders, internal scheduling, calendar invites, HR notices, and newsletters stay `safe`.

The expected effect on the next live run: recall lifts on `vendor_invoice_fraud`, `lookalike_sender`, and `invoice_authenticity_anomaly` without disturbing precision or legit FPR. If the next report shows any legit case slipping to `needs_review` or `block`, that points at the guardrail block (the recall clauses should not fire on legit traffic) and should be diagnosed before any further rubric tuning.

## Known limitations

- Each call is independent; the harness does not maintain conversational state. The locked scoring prompt is the entire system message.
- `behavioral_deviation_flags` is the **required** set on all 20 fraud cases. When the field is present, the harness checks that every listed flag is emitted; extras are allowed unless explicitly listed in `forbidden_behavioral_deviation_flags`. This post-Month-2 calibration replaces the original strict-equality contract. The three Unicode-obfuscation cases (`ia-003`, `ls-001`, `hi-001`) still require `unusual_unicode_obfuscation` because it is in their required set.
- `forbidden_behavioral_deviation_flags` is an optional per-row tuple. A flag may not appear in both required and forbidden tuples for the same case; the loader rejects that overlap.
- Legit cases are not yet pinned to `behavioral_deviation_flags=[]`. The current gate focuses on fraud-case flag emission while the existing false-positive metric controls legit over-blocking. If legit over-flagging becomes noisy in live eval, add explicit `forbidden_behavioral_deviation_flags` pins to selected legit rows in a follow-up.
- `temperature` is fixed at `0.0` for both providers. If you want to measure model variance, run the harness multiple times and diff the resulting reports manually.
- The harness does not retry on transient provider errors; a transient failure on one case will surface in the report as `llm_client_raised:...` and count as a failure for that case.

## Owner

Matt (operator). Agent (filer, runbook author).

## Last Updated

2026-05-20
