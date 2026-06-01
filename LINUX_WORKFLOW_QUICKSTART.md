# Linux Workflow Quickstart
NorthStar + SwarmCommand Venture

**Status:** Operator quickstart. Not a spec. Not §11. This file exists to prevent Windows-vs-Linux path confusion after the 2026-06-01 WSL2 cutover.

---

## Current Rule

Use Linux / WSL2 as the primary development surface:

```bash
/home/socialarchitect/northstar
```

The old Windows repo path remains backup / reference only:

```text
C:\Unified Folder Structure NorthStar + SwarmCommand Venture
```

If the two copies ever show different commit hashes, stop and reconcile before editing.

---

## How To Enter The Project

From PowerShell:

```powershell
wsl -d Ubuntu
```

Then inside Ubuntu:

```bash
cd ~/northstar
pwd
git status --short
git rev-parse --short HEAD
```

`git status --short` should print nothing when the tree is clean.

---

## Prompt Cheat Sheet

PowerShell prompt example:

```text
PS C:\Architectapp_clean>
```

That is Windows. `cd ~/northstar` will look for:

```text
C:\Users\mattn\northstar
```

Ubuntu / WSL prompt example:

```text
socialarchitect@MINIPC-WVNIP:~/northstar$
```

That is Linux. `cd ~/northstar` means:

```text
/home/socialarchitect/northstar
```

Runtime venv-active prompt example:

```text
(.venv) socialarchitect@MINIPC-WVNIP:~/northstar/3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation$
```

That means Python commands run inside the project virtual environment.

---

## Runtime Work

Go to runtime and activate the virtual environment:

```bash
cd ~/northstar/3.\ SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation
source .venv/bin/activate
```

Run the normal health checks:

```bash
python -m scripts.project_trigger_scan --baseline-tests 1055
python -m pytest tests/test_vendor_payment_integrity_break_it.py -q
python -m pytest -q
```

Expected:

```text
scan_clean
6 passed
1055 passed, 1 skipped
```

Leave the virtual environment:

```bash
deactivate
```

---

## Git Work

From repo root:

```bash
cd ~/northstar
git status --short
git log --oneline -5
```

`git log --oneline -5` prints recent commits. Each line is:

```text
short_hash commit_message
```

Example:

```text
793b6e0 pin linux bringup dependencies
5c77748 add linux bringup command checklist
be2b006 add linux line ending policy
```

That is not an error. It is commit history.

---

## Gate Smoke

From repo root, with the runtime venv active:

```bash
cd ~/northstar
source "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/.venv/bin/activate"
python audit_tools/complete_gate.py --pre-commit
```

If nothing is staged, expected output:

```text
complete_gate: no staged files in hook scope; nothing to audit.
```

---

## What Changed After The Move

Use:

```text
Ubuntu terminal + /home/socialarchitect/northstar
```

Instead of:

```text
PowerShell + C:\Unified Folder Structure NorthStar + SwarmCommand Venture
```

Benefits:

- No Windows pytest temp-cleanup noise.
- Cleaner Python environment.
- Better Git / line-ending behavior.
- Closer to production-style Linux.
- Fewer Windows path and permission interruptions.

What did not change:

- Same repo.
- Same branch.
- Same tests.
- Same audit gates.
- Same no-push / no-sign / no-proxy-decision rules.

---

## Secrets

Do not paste API keys directly into the terminal.

Use `.env` or shell environment variables, and never commit secrets.

If a key is pasted into chat or terminal, treat it as exposed and rotate it before using that provider again.

---

## Shut Down WSL

From PowerShell:

```powershell
wsl --shutdown
```

This is optional. Closing the Ubuntu terminal is usually enough.
