# Internal Tools

Lightweight repository tooling for the NorthStar + SwarmCommand venture.

These are local-developer helpers, not part of the runtime. Anything that the production loop, scoring agent, or daily digest depends on lives under `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/`.

## Inventory

| File | Purpose |
|---|---|
| `precommit_llm_safety_hook.sh` | Pre-commit scanner that blocks obviously unsafe LLM-framing terms from being committed in docs, prompts, or datasets. |
| `precommit_score_sheet_safety_hook.sh` | Wave 3.1 score-sheet safety hook that calls `audit_tools/score_sheet_review_scanner.py` to block staged score-sheet evidence/review surfaces containing secrets, raw financial identifiers, raw payload leakage, or chain-of-thought labels. |

For the full design of the LLM safety tooling — including its CI counterpart at `.github/workflows/llm_safety_check.yml` and the planned `--llm-safe` mode + onboarding section — see `6. Internal_Strategy/LLM_Workflow_Integration_Plan.md`.

## Installing the Pre-commit Hook

The script is intentionally not auto-installed. Each contributor opts in once per clone.

### Bash / WSL / Linux / macOS

```bash
ln -sf "../../Internal_Tools/precommit_llm_safety_hook.sh" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

To install the Wave 3.1 score-sheet hook instead, or to chain it from an existing pre-commit hook:

```bash
ln -sf "../../Internal_Tools/precommit_score_sheet_safety_hook.sh" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

If both hooks are needed in the same clone, create a small `.git/hooks/pre-commit` wrapper that calls both scripts in sequence.

### PowerShell (Windows)

Symlinks require admin or developer-mode, so copy the script instead:

```powershell
Copy-Item "Internal_Tools/precommit_llm_safety_hook.sh" ".git/hooks/pre-commit" -Force
```

Then ensure Git for Windows can execute the script (the default install includes a bundled `bash.exe` that runs `.sh` hooks transparently — no further action needed in most setups).

### Verifying the install

After installing, run the hook against the current index to confirm it is wired up:

```bash
.git/hooks/pre-commit
```

A clean tree exits `0`. A staged file containing a blocked term exits `1` and prints the file + matched pattern.
The score-sheet hook follows the same convention, but its findings do not echo the matched secret, PII, raw financial value, or raw payload.

## Maintenance Rules

- The pre-commit hook's `UNSAFE_PATTERNS` array and whitelist must stay byte-identical to `.github/workflows/llm_safety_check.yml`. Any change to one requires the same change to the other in the same commit (see `LLM_Workflow_Integration_Plan.md` §A↔B Synchronization Rule).
- The whitelist explicitly allows `6. Internal_Strategy/LLM_*` and `Internal_Strategy/LLM_*` so the policy and system prompt template themselves can discuss the very terms they prohibit elsewhere. Do not narrow that whitelist without updating both files and the plan doc.
- The score-sheet safety hook must import `audit_tools/score_sheet_review_scanner.py` as its only pattern source. Do not duplicate the scanner pattern list in shell.
- Pattern additions or removals are logged in `PROJECT_ACTIVITY_LOG.md` with the reason.

## False Positives

If the hook blocks legitimate defensive content:

1. First, try rephrasing into defensive / test-scenario framing per the system prompt template's principle 3.
2. If the content genuinely belongs in the policy or system prompt template, move it under `6. Internal_Strategy/LLM_*` (which is whitelisted).
3. If neither applies and the pattern is producing repeated false positives, follow the plan doc's pattern-extension policy to remove the pattern in both scanners.

## Last Updated

2026-05-20
