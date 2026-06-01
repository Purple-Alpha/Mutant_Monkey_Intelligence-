# NorthStar — Linux Bring-Up Command Checklist

**Status:** Operator playbook only. Copy-paste-ready commands. Not the migration. Not policy. Not a spec.
**Captured:** 2026-05-31 by Cursor (Claude Opus 4.7) at operator request on clean tree after commit `be2b006` (`add linux line ending policy`).
**Pairs with:** `4. Product_Roadmap/Linux_Migration_Readiness_Pass.md` §5 (the wider command sketch). This checklist is the tighter execution sheet.
**Boundary:** This artifact is commands and pass/fail criteria only. It does not authorize migration, does not authorize runtime / signed-spec / git-config changes, does not run renormalization, and does not push.

---

## §1 Prerequisites (Linux box, before clone)

Confirm or install each of these first. Versions in parentheses are what the current Windows dev box runs and what bring-up should match (or exceed within the same major).

| Component | Required | Current Windows version | Verification command |
|---|---|---|---|
| Python | 3.13 minimum; 3.14 preferred | 3.14.4 | `python3 --version` |
| pip | recent | bundled | `python3 -m pip --version` |
| venv module | present | bundled | `python3 -m venv --help` (returns help text) |
| git | 2.30+ | system | `git --version` |
| sqlite3 CLI | 3.30+ (CLI optional, only for inspection) | system | `sqlite3 --version` |
| Build tooling for cryptography wheel fallback | only if wheels missing | system | `gcc --version` |

On Debian / Ubuntu, the one-shot install for the tooling that might be needed for cryptography source builds (only if the pre-built wheel is unavailable for your Python version on your distro) is:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-dev git build-essential libssl-dev libffi-dev sqlite3
```

If you are on Fedora / RHEL: `sudo dnf install python3 python3-pip python3-devel git gcc openssl-devel libffi-devel sqlite`.

If you are on Arch: `sudo pacman -S python python-pip git base-devel openssl libffi sqlite`.

You also need a copy of the `.env` file at the repo root containing:

```env
XAI_API_KEY=xai-...
# Optional: XAI_MODEL=grok-4
```

The `.env` does **not** travel with the repo (it is gitignored, and rightly so). You must transfer the key value manually from the Windows box or your password manager.

---

## §2 Clone or copy the repo

**Option A — clone fresh** (preferred if remote is reachable):

```bash
cd ~/projects     # or wherever you want it
git clone <repo-url> "Unified Folder Structure NorthStar + SwarmCommand Venture"
cd "Unified Folder Structure NorthStar + SwarmCommand Venture"
```

**Option B — copy from Windows** (preferred if remote is not set up or you want byte-identical state):

```bash
# From Linux, pull the entire working tree across via rsync over ssh.
# Replace WINDOWSHOST with your actual Windows host name or IP, and the
# source path with the actual Windows path (escape spaces as appropriate).
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='audit_outputs/decision_audits' \
  user@WINDOWSHOST:'/c/Unified Folder Structure NorthStar + SwarmCommand Venture/' \
  ~/projects/'Unified Folder Structure NorthStar + SwarmCommand Venture/'
cd ~/projects/"Unified Folder Structure NorthStar + SwarmCommand Venture"
```

Confirm `HEAD` matches the Windows box:

```bash
git log -1 --oneline
# Expected: be2b006 add linux line ending policy   (or a later commit if more landed)
```

Confirm `.gitattributes` is in force and the tree is clean:

```bash
git status --short
# Expected output: (empty)
cat .gitattributes | head -5
# Expected: starts with "# NorthStar + SwarmCommand Venture — line-ending policy"
```

If `git status` shows phantom changes immediately after clone on Linux, that is the CRLF/LF policy doing its job — but it should not happen, because `.gitattributes` now pins LF for all text files. If you do see it, **stop and capture** per §10.

---

## §3 Python virtualenv setup

```bash
python3 -m venv .venv
source .venv/bin/activate

# Confirm Python version matches the §1 requirement.
python --version
# Expected: Python 3.13.x or 3.14.x

# Upgrade pip inside the venv (silent on success).
python -m pip install --upgrade pip
```

The `.venv/` directory is gitignored. Do not commit it. Do not name it differently — other tooling (and future automations) assumes `.venv`.

---

## §4 Dependency install

**Important — known gap:** as of commit `be2b006`, `requirements.txt` only declares `pywin32 ; sys_platform == "win32"`. The actual NorthStar runtime depends on pydantic, pytest, cryptography, requests, and httpx, which are currently expected to be system-installed. Until that gap is closed (separate operator-authorized commit to pin dependencies properly), the Linux bring-up uses an explicit install line.

```bash
# Step 4.1 — install the (platform-scoped) requirements.txt file.
pip install -r "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/requirements.txt"

# Step 4.2 — install the explicit runtime / test dependencies that are NOT yet
# in requirements.txt. Versions below match the current Windows dev box at
# commit be2b006; tighten or relax as the dep-pinning commit lands.
pip install \
  "pydantic>=2.13,<3" \
  "pytest>=9.0,<10" \
  "cryptography>=48,<49" \
  "requests>=2.33,<3" \
  "httpx>=0.27,<1"

# Step 4.3 — sanity check that pywin32 was correctly SKIPPED on Linux.
pip list 2>/dev/null | grep -i pywin32 \
  && echo "UNEXPECTED: pywin32 installed on Linux" \
  || echo "OK: pywin32 not installed (expected; platform marker honored)"
```

A future commit titled `pin runtime dependencies in requirements.txt` is the right separate fix; until then, the explicit `pip install` above is the bring-up workaround.

---

## §5 Trigger scan with baseline 1055

This is the first audit-machinery smoke. It does not call any remote service; it inspects the working tree and the recorded baseline only.

```bash
python "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/project_trigger_scan.py" --baseline-tests 1055
```

Pass = a JSON document with `"trigger_class": "scan_clean"`, `"drift_findings": []`, `"baseline_tests_expected": 1055`, `"baseline_tests_recorded": 1055`, and an info-severity packet. Exit code `0`.

Fail = any non-zero exit, any non-empty `drift_findings`, or any baseline mismatch. Capture per §10.

---

## §6 Targeted pytest (the platform-sensitive subset)

Run these first, in this order, before the full suite. Each must pass before continuing. If one fails, capture per §10 and stop — do not paper over with `--continue-on-collection-errors`.

```bash
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"

# §6.1 — Vendor Baseline Store isolation (the most platform-sensitive module).
#        Exercises the POSIX `chmod` branch of `harden_path` on Linux; the
#        Windows DACL branch (pywin32) is gated by sys.platform and will not
#        run.
python -m pytest tests/test_vendor_baseline_isolation_boundary.py -v

# §6.2 — Vendor Baseline Store core (HKDF + SQLite + per-tenant salt).
python -m pytest tests/test_vendor_baseline_store.py -v

# §6.3 — Vendor Payment Integrity break-it (this session's adversarial
#        tests; touches isolation, FSL overlay, daily-digest import boundary,
#        per-tenant salt).
python -m pytest tests/test_vendor_payment_integrity_break_it.py -v

# §6.4 — Fraud eval harness (the cp1252 stdout reconfigure helper; on Linux
#        the reconfigure simply does nothing because stdout is UTF-8 by
#        default — the test's explicit cp1252 TextIOWrapper is portable).
python -m pytest tests/test_fraud_eval_harness.py -v

# §6.5 — Pre-ship audit harness (subprocess + git plumbing).
python -m pytest tests/test_pre_ship_audit.py -v

cd ../../../..
```

Pass per file = `=== N passed in X.YZs ===` with no warnings about platform mismatch or import errors. Exit code `0`.

---

## §7 Full pytest

Once the §6 targeted subset is green, run the full suite:

```bash
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
python -m pytest -q
cd ../../../..
```

Pass = `1055 passed, 1 skipped in X.YZs` (or higher if new tests have landed since commit `be2b006`) with no errors, no platform-specific failures, no `cp1252` `UnicodeEncodeError` (Linux defaults to UTF-8), and **no Windows-only atexit `PermissionError [WinError 5]` traceback** (that noise vanishes on Linux — that is a feature, not a regression).

Acceptable on Linux but not on Windows: the test run will complete cleanly without the atexit traceback that has been visible at the end of every Windows test run this development cycle.

Fail = anything other than `N passed` with N ≥ 1055 and S = 1 (or possibly higher if new skips have been added). Capture per §10.

---

## §8 Audit-gate smoke (doc-only manifest)

This is the final and most important smoke: it verifies that the audit gate's full pipeline (git diff collection, manifest verification, packet generation, Grok API call, response parsing, audit-report writing) functions end-to-end on Linux. It costs one Grok API call (~$0.01).

The pattern that works without modifying any tracked file or signed spec: write a tiny operator-facing note to `PROJECT_ACTIVITY_LOG.md` recording the Linux bring-up smoke itself, then gate that single-file edit. The smoke and the durable record are the same artifact, which matches how `cd1d5d5`, `5662872`, and `be2b006` were structured.

```bash
# §8.1 — Make the smoke entry. Replace the date and HEAD hash with actual
#        values from your bring-up run.
cat >> PROJECT_ACTIVITY_LOG.md <<'EOF'

---

## YYYY-MM-DD - Linux Bring-Up Smoke

**Actor:** Matt (Linux box, first verification pass).

**Action:** Reviewed

**Files Changed:**
- PROJECT_ACTIVITY_LOG.md (this entry)

**Reason:**
Recording first successful NorthStar bring-up on Linux. All §6 targeted tests passed, full §7 pytest hit 1055 passed / 1 skipped, audit gate machinery exercised end-to-end on Linux (this very entry's gate run).

**No runtime test count change** (baseline remains 1055 passed / 1 skipped).

EOF

# §8.2 — Write the matching manifest.
mkdir -p audit_outputs/pending
cat > audit_outputs/pending/linux-bringup-smoke.manifest.json <<'EOF'
{
  "task_id": "linux-bringup-smoke",
  "completion_claim": "Linux bring-up smoke recording the first successful NorthStar verification pass on Linux per `4. Product_Roadmap/Linux_Bringup_Command_Checklist.md`. Single-file edit appending one new entry to `PROJECT_ACTIVITY_LOG.md`. No runtime code, no signed spec, no git config writes, no renormalization, no push.",
  "files_modified": ["PROJECT_ACTIVITY_LOG.md"],
  "files_created": [],
  "files_read": [],
  "relevant_contracts": []
}
EOF

# §8.3 — Run the gate.
python audit_tools/complete_gate.py \
  --task linux-bringup-smoke \
  --claim "Linux bring-up smoke; single-file PROJECT_ACTIVITY_LOG.md entry only; no runtime/spec/git-config changes."
```

Pass = `clean audit. 0 warning(s).` and exit code `0`. The audit report at `audit_outputs/linux-bringup-smoke_<timestamp>.md` should show `Blocking deviations: 0`, `Warnings: 0`.

Fail = any blocking deviation, any network error talking to `api.x.ai`, any missing-`.env` error, any packet-too-large error. Capture per §10.

If the gate passes, the smoke entry can be committed as `add linux bringup smoke` (separate operator decision). Or it can be discarded with `git checkout -- PROJECT_ACTIVITY_LOG.md && rm audit_outputs/pending/linux-bringup-smoke.manifest.json` if you would rather not land it.

---

## §9 What outputs count as PASS

Whole bring-up is green when **all six** of these hold simultaneously:

1. `python --version` reports 3.13.x or 3.14.x inside the venv.
2. `pip list | grep -i pywin32` returns empty (pywin32 NOT installed on Linux).
3. `project_trigger_scan.py --baseline-tests 1055` exits 0 with `scan_clean` and empty `drift_findings`.
4. All five §6 targeted pytest runs pass with no platform-mismatch warnings, no import errors.
5. Full §7 pytest reports `1055 passed, 1 skipped` (or higher if new tests have landed) and no atexit Windows-specific traceback.
6. §8 gate smoke reports `clean audit. 0 warning(s).` exit 0.

If any single one of those fails, the bring-up is **not** green. Do not paper over individual failures by skipping the step.

---

## §10 What to capture on FAIL

If any §3–§8 step fails, do not retry blindly. Capture this diagnostic bundle, then stop and report:

```bash
# 10.1 — Python and dep versions inside the venv.
python --version
pip freeze > /tmp/linux-bringup-pip-freeze.txt

# 10.2 — git state and config.
git --version
git status --short
git log -1 --oneline
git config --get core.autocrlf
git config --get core.eol
git config --get core.filemode
git config --get core.ignorecase

# 10.3 — System / locale facts that often surface platform diffs.
uname -a
locale
echo "${LANG:-unset}" "${LC_ALL:-unset}" "${PYTHONIOENCODING:-unset}"

# 10.4 — The full stdout+stderr of the failing command (re-run it here).
#        Replace <FAILING_COMMAND> with the exact command that failed in
#        §3-§8 above; do not summarise.
<FAILING_COMMAND> 2>&1 | tee /tmp/linux-bringup-failure.txt

# 10.5 — If a pytest run failed, also capture the full traceback for the
#        first failing test only (additional failures usually cascade from
#        the first).
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
python -m pytest -x --tb=long -v 2>&1 | tee /tmp/linux-bringup-pytest-first-failure.txt
cd ../../../..

# 10.6 — If the gate smoke failed, also capture the most recent audit
#        report, which contains the Grok packet hash and structured
#        verdict.
ls -t audit_outputs/linux-bringup-smoke_*.md | head -1 | xargs cat \
  > /tmp/linux-bringup-gate-failure.txt
```

Then report to the operator (or open a Cursor session) with:

- `/tmp/linux-bringup-pip-freeze.txt`
- `/tmp/linux-bringup-failure.txt`
- `/tmp/linux-bringup-pytest-first-failure.txt` (if pytest failed)
- `/tmp/linux-bringup-gate-failure.txt` (if gate failed)
- The output of 10.1, 10.2, and 10.3 inline.

That bundle is enough for a remote diagnosis without further round-trips.

---

## §11 What NOT to do during bring-up

- Do **not** run `git add --renormalize .`. That is a separately-authorized whole-repo normalization commit per readiness pass §6.1.
- Do **not** flip `core.autocrlf`, `core.eol`, `core.filemode`, or `core.ignorecase` yet. Those flips happen in the renormalization commit pass.
- Do **not** edit signed specs to silence platform-specific test failures. If a test fails because the spec is wrong, the spec needs an operator-authorized revision cycle; if a test fails because of an environment issue, fix the environment.
- Do **not** edit runtime code to silence platform-specific test failures during bring-up. Surface the failure per §10 first.
- Do **not** push from the Linux box. Bring-up is local-first; pushing is a separate operator decision.
- Do **not** install `pywin32` manually with `pip install pywin32`. The platform marker in `requirements.txt` is the discipline; defeating it makes the next clean Linux install harder.
- Do **not** modify `.gitattributes` during bring-up to "fix" any line-ending observation. The policy is in force per commit `be2b006`; if `git status` shows phantom CRLF/LF changes after clone, that is signal worth investigating, not a typo to fix.

---

## §12 Operator decision points after bring-up

These are NOT part of the bring-up itself; they are the explicit operator decisions enabled by a green bring-up.

1. **Renormalization commit** (per readiness pass §6.1) — flip `core.autocrlf=false` + `core.eol=lf` per-repo, run `git add --renormalize .` as its own atomic commit. Will likely need `--operator-override` at the gate because of size.
2. **`requirements.txt` dep pinning commit** — close the §4 gap so `pip install -r requirements.txt` works without the explicit `pip install` step. Separate operator-authorized commit.
3. **Primary development surface switch** — once Linux bring-up is green, decide whether to switch the primary dev box to Linux now or run both in parallel for a week.
4. **CI provisioning** — if Linux bring-up is green and stable, a Linux-only CI workflow becomes possible. That is its own separate spec.

---

**End of checklist. Commands and pass/fail criteria only. The migration window and timing remain operator decisions.**
