# NorthStar LLM Workflow Integration Plan (v1.0)

## Purpose

This document is the design pass and tracking surface for the engineering controls that operationalize the [LLM Usage Policy](LLM_Usage_Policy.md) and the [Defensive Security System Prompt](LLM_System_Prompt_Template.md).

Four enforcement vectors are scoped here. Three are **implemented** and live in the repository today (A pre-commit hook, B CI scanner, C `--llm-safe` mode in the fraud eval harness); one remains **planned** (D onboarding) and lands after §C so the walkthrough reflects what is actually enforced.

## Scope Map

| Vector | Surface | Status | Artifact |
|---|---|---|---|
| A. Local pre-commit hook | Developer machine | IMPLEMENTED | `Internal_Tools/precommit_llm_safety_hook.sh` |
| B. CI safety scan | GitHub Actions on push / PR to `main` / `master` | IMPLEMENTED | `.github/workflows/llm_safety_check.yml` |
| C. `--llm-safe` mode for internal tools | Internal CLIs that call live LLMs | IMPLEMENTED | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/llm_safety.py` (+ wired into `fraud_eval_harness.py`) |
| D. Onboarding "LLM Usage" section | Operator training docs | PLANNED | (target: `New_Operator_Training_Guide.md`) |

## A. Pre-commit Hook (IMPLEMENTED)

- File: `Internal_Tools/precommit_llm_safety_hook.sh`
- Scans staged content of `*.md`, `*.prompt`, `*.txt`, `*.jsonl`, `*.yaml`, `*.yml` for an explicitly tuned blocklist of offensive-framing terms.
- Whitelists `6. Internal_Strategy/LLM_*` and `Internal_Strategy/LLM_*` so the policy and system prompt template themselves are allowed to discuss the very terms they prohibit elsewhere.
- Install: see `Internal_Tools/README.md` for the symlink / copy instructions.
- Exit codes: `0` clean, `1` one or more files contain blocked terms (commit aborted, file + matched term printed).

## B. CI Safety Scan (IMPLEMENTED)

- File: `.github/workflows/llm_safety_check.yml`
- Triggers: `push` and `pull_request` against `main` or `master`.
- Pattern list intentionally kept **byte-identical** to the pre-commit hook so a local pass implies a CI pass (and vice versa). If you add a pattern to one, add it to the other in the same change.
- Uses `git ls-files` rather than `git diff --cached` because CI scans the full tree, not just staged content.

### A↔B↔C Synchronization Rule

Three copies of the `UNSAFE_PATTERNS` list now exist and must stay in lockstep. The maintenance protocol is:

1. Edit the `UNSAFE_PATTERNS` array in `Internal_Tools/precommit_llm_safety_hook.sh`.
2. Mirror the exact same change in `.github/workflows/llm_safety_check.yml`.
3. Mirror the exact same change in `core/scoring/eval/llm_safety.py::UNSAFE_PATTERNS` (tuple form).
4. Mirror the `6. Internal_Strategy/LLM_*` / `Internal_Strategy/LLM_*` whitelist in the two shell scanners (vectors A and B); vector C does not need the whitelist because it scans only the dataset file passed to the harness, not the strategy folder.
5. Update `tests/test_fraud_eval_harness.py::test_unsafe_patterns_are_lowercase_and_synced_with_shell_hook` to match the new expected set so any future drift in any one of the three locations fails CI on the runtime test side as well.
6. Record the change in `PROJECT_ACTIVITY_LOG.md` with the reason a term was added or removed.

### Pattern Extension Policy

- **Add a pattern** when the team observes a real false negative — content that should have been flagged but slipped through.
- **Remove a pattern** only when it produces repeated false positives that legitimate defensive content cannot reasonably rephrase around. Document the removal in `PROJECT_ACTIVITY_LOG.md`.
- Patterns are intentionally narrow phrases (e.g., `"ransomware payload"`, not `"ransomware"`) so the NorthStar product space (ransomware *defense*) is not blocked.

## C. `--llm-safe` Mode for Internal Tools (IMPLEMENTED)

- File: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/llm_safety.py`
- Wired into: `core/scoring/eval/fraud_eval_harness.py` (CLI entry) via the `--llm-safe` / `--no-llm-safe` flags.
- Default: `--llm-safe` is **ON** when `--provider` is set. Operators must pass `--no-llm-safe` to disable, and CI must never invoke the harness with that flag.

Behavior when `--llm-safe` is active:

1. Dataset path allowlist — the dataset path is rejected if any component contains a substring like `customer`, `production`, `real_emails`, `tenant_data`. Bypass with `--allow-unsafe-dataset-path` only after confirming the dataset is fully synthetic.
2. Unsafe-pattern scan — the dataset file is scanned against `UNSAFE_PATTERNS` (same list as the shell scanners; A↔B↔C sync rule above). Any hit raises `LLMSafetyError` and exits the CLI with code 2 before any LLM call is issued.
3. Defense-in-depth prompt prefix check — `build_llm_safe_client` refuses to forward any LLM call whose `system_prompt` does not start with `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT[:200]`. Even if the runner is ever refactored to drop the locked scoring prompt, the wrapper still refuses.
4. Sha256 usage log — every LLM call appends one JSON line to `<dataset-dir>/operator_state/llm_usage.jsonl` containing the timestamp, the case id, sha256 digests of the system prompt / user prompt / response, the response byte count, the status (`ok` / `error:<ExceptionName>`), and any error message. Raw prompt and response bodies are NOT persisted, so the usage log is safe to commit, share, or attach to an audit packet.

The operator runbook for actually invoking the harness against a live provider lives at `4. Product_Roadmap/Live_LLM_Eval_Runbook.md`.

### Synthetic-data marker (deferred)

The original §C plan called for "enforce a synthetic-data marker on every input row". This was deliberately deferred during the IMPLEMENTED landing because:

- The shipped 40-case dataset uses fictional but realistic Canadian small-business domains (`acme-manufacturing.ca`, `coastal-marine.ca`, etc.) rather than `.example` / `.test` / `.invalid` TLDs, so a naive marker check would either reject the shipped dataset or be too weak to mean anything.
- The path allowlist + unsafe-pattern scan + sha256 usage log together provide stronger procedural guarantees than a free-text marker would.

When a second curated dataset lands (e.g. a ransomware-precursor dataset for Month 3), the marker discussion will be reopened.

## D. Onboarding "LLM Usage" Section (PLANNED)

Target: `New_Operator_Training_Guide.md` gains an "LLM Usage" section that:

- Links the [system prompt template](LLM_System_Prompt_Template.md) and the [usage policy](LLM_Usage_Policy.md).
- Provides one safe-vs-unsafe phrasing pair per principle in the system prompt.
- Walks the new engineer through a five-minute test scenario using `--llm-safe` against a synthetic email payload from `core/scoring/eval/fraud_eval_dataset.jsonl`.
- Documents the escalation path on suspected misuse (project lead → access restriction, per policy §9).

Sequencing dependency: lands after §C so the documented walkthrough reflects what's actually enforced rather than aspirational.

## Out of Scope for v1

- ML-based prompt-injection detection or deep linguistic safety classification.
- LLM-provider audit (proving the upstream provider does not log, retain, or train on NorthStar prompts).
- Multi-tenant LLM call separation. This will need its own spec once more than one tenant runs live LLM scoring.
- Automated rewriting of flagged content. The scanners flag and block; humans decide how to rephrase.

## Out-of-Repo Surfaces

- External LLM chat sessions (Claude, ChatGPT, Cursor inline, etc.) used for NorthStar design or evaluation work. These cannot be enforced by repository tooling; the policy + system prompt template are the only governance lever. The pre-commit hook catches the case where unsafe text is later pasted *into* the repo.

## Owner

Matt

## Last Updated

2026-05-20
