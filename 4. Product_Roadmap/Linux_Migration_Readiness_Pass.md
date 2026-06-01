# NorthStar — Linux Migration Readiness Pass

**Status:** Readiness map only. Not the migration. Pre-execution checklist. Operator-facing.
**Captured:** 2026-05-31 by Cursor (Claude Opus 4.7) at operator request, on clean tree after commit `f5b254d` (`land vendor payment integrity tests and discovery notes`).
**Architect:** Matt. The actual migration window, the timing, and the go/no-go call remain operator decisions.
**Source-of-truth links:** `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` §2 "Operational note: Linux migration plan" (already records long-term Linux target); `requirements.txt` (`pywin32 ; sys_platform == "win32"` already platform-scoped); `core/production_state/vendor_baseline/isolation.py` (already cross-platform via `sys.platform == "win32"` branch).

**Authority gate:** Nothing in this readiness pass authorizes runtime code changes, signed-spec edits, queue changes, `.gitattributes` commits, git config writes, file deletions, executable-bit flips, or any destructive git commands. It is a *map*: it inspects the current Windows-first state, names what would need to change before flipping to Linux-first, and stops. The migration itself is a separate operator-authorized execution pass.

---

## §1 Migration Goal

> Move NorthStar development from Windows-first to Linux-first, while preserving the current repo, tests, audit gates, and local-first workflow.

Concretely, after the switch:

- The full 1055-test pytest suite runs cleanly on Linux from `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/`.
- `audit_tools/complete_gate.py` and the related auditors run unchanged.
- `scripts/project_trigger_scan.py` runs unchanged.
- Vendor Baseline Store SQLite files harden via POSIX `chmod` (already implemented), not via pywin32 DACL (which simply does not import on Linux per `requirements.txt`).
- Git no longer emits the constant `LF will be replaced by CRLF` warnings on every status.

---

## §2 Risk Verdict

**LOW risk overall, with two specific mechanical settlements required before the switch.**

Reasoning:

- The runtime is already cross-platform aware by design. `Vendor_Baseline_Store_Deep_Dive.md` D9 explicitly contemplated Linux as the long-term target and `core/production_state/vendor_baseline/isolation.py` already branches on `sys.platform == "win32"`, with pywin32 imported lazily inside the Windows branch only. Linux installs skip pywin32 entirely (`requirements.txt` line 1).
- Path handling is universally `pathlib.Path`; no hardcoded `C:\\` paths, no `\\` separators, no Windows registry reads, no COM/OLE/WMI, no `cmd.exe` invocations, no PowerShell calls from Python.
- Audit tools (`audit_tools/*.py`) use `encoding="utf-8"` everywhere and `subprocess.run` in text-mode; no shell-specific assumptions.
- Scripts (`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/*.py`) are pure Python with no platform-specific code (no `sys.platform`, no `win32`, no `PowerShell`, no `cmd.exe`, no `os.sep`, no `tempfile`-with-Windows-specific-flags, no `cp1252` baked-in).
- The cp1252 Unicode handling in `core/scoring/eval/fraud_eval_harness.py` is a best-effort `stream.reconfigure(encoding="utf-8")` helper that simply does nothing on Linux (Linux stdout is UTF-8 by default); the test that exercises it constructs an explicit `cp1252` `TextIOWrapper` over `BytesIO`, which is portable.
- The pytest `PermissionError [WinError 5]` atexit-cleanup noise visible in this session's test runs is Windows-specific and will simply not occur on Linux (improvement, not risk).

The two real settlements are §6 (CRLF/LF) and §7 item 3 (executable bit on the bash hook). Both are mechanical, both are documented below, neither is a code change.

---

## §3 Known Risks

| # | Risk | Severity | Source | Mitigation |
|---|---|---|---|---|
| R1 | Git `core.autocrlf=true` on Windows will fight a Linux working tree if no `.gitattributes` pins line endings; cross-platform diffs will be noisy and gate packets will inflate from line-ending churn. | MEDIUM | `git config --get core.autocrlf` → `true`; no `.gitattributes` file present in repo. | §6 plan below. |
| R2 | Git `core.ignorecase=true` (Windows default). On Linux, the filesystem is case-sensitive. If any two tracked paths differ only by case, Linux would treat them as separate files and the Windows tree would have hidden one of them. | LOW | `git config --get core.ignorecase` → `true`. | §7 checklist item 2 below — pre-switch audit. |
| R3 | Git `core.filemode=false` (Windows default). Executable bits not tracked. `Internal_Tools/precommit_llm_safety_hook.sh` would need `chmod +x` + `git update-index --chmod=+x` after switch if it is ever installed as an actual git hook. | LOW | `git config --get core.filemode` → `false`. | §7 checklist item 3 below. |
| R4 | `AI_Phishing_Simulation_Business/Inbox_Shield/run_demo.ps1` is the one PowerShell-only script in the repo. Lives in the pre-NorthStar PoC workspace, not the runtime critical path. | LOW | `Glob **/*.ps1` → exactly 1 result. | §7 checklist item 4 below — mirror as `run_demo.sh` only if the demo is still in use. |
| R5 | Vendor Baseline Store per-tenant SQLite paths use `pathlib.Path` with relative `production_state/{tenant_id}/vendor_baseline.sqlite`. On Linux these paths inherit umask defaults until `harden_path` runs `chmod 0o600`. The `chmod` happens immediately after file creation in `leased_connection`; tests already exercise the POSIX path. | LOW | Reviewed `core/production_state/vendor_baseline/isolation.py` lines 48-77. | None required — already correct by design. |
| R6 | Vendor Baseline Store `pywin32` import. If a Linux contributor pip-installs without the platform marker honored (rare, e.g. `pip install pywin32` directly), the Windows DACL branch is still gated by `sys.platform == "win32"` and never runs. | LOW | Reviewed `_harden_path_windows` import sequence. | None required. |
| R7 | The audit gate's 200 KB packet cap is unrelated to platform but interacts with the four giant tracker files (`PROJECT_ACTIVITY_LOG.md` ~700 KB, `PROJECT_HANDSHAKE.md` ~155 KB, `PROGRESS.md` ~143 KB, `MASTER_INDEX.md` ~83 KB). Linux migration neither helps nor hurts this; it is a separate operator concern. | UNCHANGED BY MIGRATION | Earlier this session: gate failed with 298 KB after a tracker-heavy pass. | Out of scope for this readiness pass. |
| R8 | Python version drift. Development is on Python 3.14.4 on Windows. Linux distros vary (Debian/Ubuntu ship 3.11/3.12 by default; recent Fedora/Arch ship 3.13/3.14). | LOW | Observed from `pytest` session header. | §7 checklist item 1 below — pin or document the Python version. |
| R9 | `cryptography` package (used for HKDF in Vendor Baseline Store) has prebuilt wheels for both Windows and Linux on Python 3.14. No source build required on standard Linux distros. | LOW | Standard `cryptography` distribution. | None required. |
| R10 | Pytest tempfile cleanup PermissionError on Windows (visible as atexit traceback in every test run) is Windows-only and will silently go away on Linux. | NEGATIVE RISK (i.e. improvement) | Observed during the Vendor Payment Integrity break-it pass. | None — this is a free win. |

---

## §4 Files / Scripts Likely Affected

Inspected, **no code change required**:

- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/requirements.txt` — already platform-scoped (`pywin32 ; sys_platform == "win32"`).
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/isolation.py` — already cross-platform.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/store.py` — pure SQLite + HKDF + `pathlib`.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/fraud_eval_harness.py` — cp1252 reconfigure is best-effort, Linux ignores it.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/*.py` — all pure Python.
- `audit_tools/*.py` — all UTF-8, all subprocess.run text-mode, no shell-specific assumptions.
- `Internal_Tools/precommit_llm_safety_hook.sh` — already bash, already POSIX.

Inspected, **mechanical attention needed at migration time** (no code change in this readiness pass):

- `(repo root)/.gitattributes` — does not exist. Will be created during the migration pass per §6.
- `(repo root)/.gitignore` — verify it ignores OS-specific clutter (`Thumbs.db`, `Desktop.ini`, `.DS_Store`, `__pycache__/`, `.pytest_cache/`). Quick verification, not a blocker.
- `AI_Phishing_Simulation_Business/Inbox_Shield/run_demo.ps1` — optional `run_demo.sh` mirror if the demo is still in use. Not on NorthStar critical path.

---

## §5 Required Commands

### §5.1 Smoke commands (Linux, post-clone, before full verification)

Order matters; each one must pass before the next:

```bash
# 1. Confirm Python version on the Linux box (3.13+ recommended, 3.14 matches dev).
python3 --version

# 2. Create an isolated virtualenv (do NOT install system-wide).
python3 -m venv .venv
source .venv/bin/activate

# 3. Install requirements; pywin32 should be silently skipped by the platform marker.
pip install --upgrade pip
pip install -r "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/requirements.txt"

# 4. Confirm pywin32 is NOT installed on Linux (sanity).
pip list 2>/dev/null | grep -i pywin32 && echo "UNEXPECTED: pywin32 installed on Linux" || echo "OK: pywin32 not installed (expected)"

# 5. Single-test smoke: Vendor Baseline Store isolation (the most platform-sensitive module).
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
python -m pytest tests/test_vendor_baseline_isolation_boundary.py -v

# 6. Single-test smoke: Vendor Payment Integrity break-it (this session's new tests).
python -m pytest tests/test_vendor_payment_integrity_break_it.py -v
```

Expected outcome: every command returns clean; tests pass.

### §5.2 Full verification commands (Linux, after smoke passes)

```bash
# 1. Full runtime suite — must hit 1055 passed / 1 skipped (or higher if new tests have landed).
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
python -m pytest -q

# 2. Trigger scan against the recorded baseline.
python scripts/project_trigger_scan.py --baseline-tests 1055

# 3. Audit gate smoke — run with a tiny no-op manifest to confirm the gate executes
#    end-to-end on Linux (does not need to land an audit; --report-only would be
#    used if a real audit is in flight). The gate's git diff + manifest + Grok
#    call paths all need to function on Linux.
cd ../../../..    # back to repo root
python audit_tools/complete_gate.py --task migration-smoke-noop --claim "Linux smoke after migration. No code change. Verifying gate executes end-to-end."
# If this returns audit_packet_too_large because the working tree is dirty, that
# is the tracker-size ceiling (R7), not a migration issue.

# 4. Run one demo end-to-end to exercise the operator-facing CLI surface.
cd "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
python -m scripts.acme_effective_parameter_report_demo
python -m scripts.inbox_shield_daily_digest_demo
```

Expected outcome: full suite green; trigger scan clean; gate executes (pass/fail depending on tree state, but no Python or platform errors); demos produce their generated artifacts.

### §5.3 Optional cross-platform parity check

```bash
# Quick sanity: confirm there are no hidden case-only path collisions that
# would silently break on Linux's case-sensitive filesystem (R2).
find . -type f | awk -F/ '{print tolower($0)"\t"$0}' | sort | awk -F'\t' '{ if (last==$1 && prev!=$2) print prev"\n"$2; last=$1; prev=$2 }'
```

If this prints any pairs, audit them before commit. No output = no collisions.

---

## §6 CRLF / LF Plan

The repo currently has `core.autocrlf=true` and **no `.gitattributes`**. This is the source of the constant `LF will be replaced by CRLF the next time Git touches it` warnings on every `git status` / `git add` in this session.

### §6.1 During the migration pass (not in this readiness pass)

1. Create a `.gitattributes` file at the repo root with at minimum:

   ```gitattributes
   # Default: text auto-detected, normalize to LF in the repo.
   * text=auto eol=lf

   # Explicit binary types - never touch line endings.
   *.png binary
   *.jpg binary
   *.jpeg binary
   *.gif binary
   *.pdf binary
   *.sqlite binary
   *.db binary
   *.jsonl binary
   *.ico binary
   *.zip binary

   # Shell scripts: LF always, regardless of platform.
   *.sh text eol=lf

   # PowerShell + Windows batch: CRLF when checked out on Windows.
   *.ps1 text eol=crlf
   *.bat text eol=crlf
   *.cmd text eol=crlf
   ```

2. Flip the per-repo git config (operator decision, not auto-applied by this readiness pass):

   ```bash
   git config core.autocrlf false
   git config core.eol lf
   ```

3. Run a controlled normalization commit:

   ```bash
   # Snapshot, then re-normalize per the new .gitattributes.
   git add --renormalize .
   git status --short    # inspect what would change
   git commit -m "normalize line endings to lf per .gitattributes"
   ```

   This is the only commit in the entire migration that will touch a large number of files. Schedule it as its own commit, no other content piggybacking. Audit gate may struggle with packet size on this commit — operator override is acceptable here because it is a known-safe one-off normalization (this is one of the few legitimate uses of `--operator-override` per `complete_gate.py`'s contract).

### §6.2 What this readiness pass deliberately does NOT do

- Does not create `.gitattributes`.
- Does not flip `core.autocrlf`.
- Does not run `git add --renormalize`.

All of those are migration-execution steps, not readiness-map steps.

---

## §7 Windows-Only Assumptions Found

Comprehensive list from inspection:

1. **Python version** — current dev is Python 3.14.4 on Windows. Linux target should match or be a minor version older (3.13 is safe; 3.11/3.12 from older distros need explicit verification of `from __future__ import annotations` behavior in the test suite). Document the version pin during migration.
2. **Git case-insensitive filesystem** — `core.ignorecase=true`. Run §5.3 collision check before switch.
3. **Executable bit not tracked** — `core.filemode=false`. `Internal_Tools/precommit_llm_safety_hook.sh` would need `chmod +x` + `git update-index --chmod=+x` after the switch if installed as a real hook.
4. **`AI_Phishing_Simulation_Business/Inbox_Shield/run_demo.ps1`** — PowerShell-only; mirror as `run_demo.sh` during migration only if the demo is still in use.
5. **Pytest tempfile cleanup PermissionError** — Windows-only quirk visible as atexit traceback. Vanishes on Linux. No action needed.
6. **`fraud_eval_harness.py` cp1252 reconfigure** — Windows-console-aware; harmless on Linux. No action needed.

What was NOT found (verified absent during inspection):

- No `os.system("cmd.exe ...")` calls.
- No `os.system("powershell ...")` calls.
- No `subprocess.run(["cmd", ...])` calls.
- No `subprocess.run(["powershell", ...])` calls.
- No registry reads.
- No COM/OLE/WMI dependencies.
- No hardcoded `C:\\` paths in Python sources.
- No backslash path separators outside of regex character classes.
- No reliance on `os.sep` for portability shims (everything uses `pathlib.Path`).
- No Windows-only environment variables.

---

## §8 Migration Checklist

Run in order. Each step is operator-authorized individually; this list does not authorize anything by itself.

- [ ] **Pre-flight (Windows side)**
  - [ ] Confirm working tree is clean (`git status --short` returns empty).
  - [ ] Confirm `f5b254d` or later is current `HEAD` (the last known-green Windows baseline).
  - [ ] Run §5.3 case-collision check on Windows; if any pairs appear, resolve before switch.
  - [ ] Record the Python version pin (`python --version`) for the Linux box to match.
- [ ] **Linux box setup**
  - [ ] Install matching Python version (target: 3.14, acceptable: 3.13).
  - [ ] Install `git`, `sqlite3` (CLI is useful for inspection but not required by the runtime), and standard build tooling for `cryptography` wheel fallback (`build-essential` / `python3-dev` on Debian-derived).
  - [ ] Clone the repo to the Linux box.
- [ ] **CRLF / LF settlement** (per §6)
  - [ ] Create `.gitattributes` at repo root.
  - [ ] `git config core.autocrlf false` + `git config core.eol lf` per-repo.
  - [ ] `git add --renormalize .` and commit as a standalone normalization commit.
- [ ] **Linux smoke** (per §5.1)
  - [ ] Virtualenv + `pip install -r requirements.txt`.
  - [ ] Confirm `pywin32` is NOT installed.
  - [ ] Run targeted Vendor Baseline Store isolation test.
  - [ ] Run targeted Vendor Payment Integrity break-it tests.
- [ ] **Linux full verification** (per §5.2)
  - [ ] Full pytest: must hit 1055 passed / 1 skipped (or higher).
  - [ ] Trigger scan against baseline 1055: must return `scan_clean`.
  - [ ] Audit gate end-to-end smoke.
  - [ ] One demo runs (e.g. `acme_effective_parameter_report_demo`).
- [ ] **Optional polish**
  - [ ] Add `chmod +x` + `git update-index --chmod=+x` for `Internal_Tools/precommit_llm_safety_hook.sh` if the hook is being installed.
  - [ ] Mirror `run_demo.ps1` as `run_demo.sh` if the PoC demo is still in use.
- [ ] **Operator sign-off**
  - [ ] Update `PROJECT_HANDSHAKE.md` with new development platform note.
  - [ ] Append a `PROJECT_ACTIVITY_LOG.md` entry recording the migration outcome and Linux verification baseline.

---

## §9 Rollback Plan

The migration is local-first and revertible. Rollback is straightforward because:

1. **The Windows box stays as-is.** The migration is a *clone-and-set-up-on-Linux* pass, not a *destroy-Windows-and-rebuild* pass. If Linux verification fails, Windows continues to work unchanged.
2. **No runtime code changes during migration.** The only commit landed during a clean migration is the `.gitattributes` + `core.autocrlf=false` normalization commit. That commit is fully revertible with `git revert <hash>`.
3. **Per-tenant Vendor Baseline Store files** are stored under `production_state/{tenant_id}/`. These are gitignored runtime artifacts (or should be; verify against `.gitignore` during migration). They are tenant data, not source, and do not need to migrate.

If Linux verification fails:

1. Stop the migration.
2. Continue developing on Windows as before.
3. If the `.gitattributes` + normalization commit landed before failure, revert it locally on Windows with `git revert <normalization-commit-hash>` and resume.
4. Capture the failure mode in `PROJECT_ACTIVITY_LOG.md` so the next attempt has evidence to work from.

There is no scenario in which a failed Linux migration corrupts the Windows working state, because the Windows box does not participate in the migration except as the source clone.

---

## §10 What NOT To Touch Yet

This readiness pass deliberately does not:

- Create `.gitattributes` (§6 is a plan; the file gets created during the migration, not now).
- Run `git config` writes (autocrlf, eol, filemode — operator decision, executed during migration).
- Run `git add --renormalize` (operator decision, executed during migration).
- Touch runtime code, signed specs, or the Vendor Payment Integrity break-it tests.
- Touch `requirements.txt` (already platform-scoped correctly).
- Mirror `run_demo.ps1` as `run_demo.sh` (optional polish, not a migration blocker).
- `chmod +x` any shell script (operator decision during migration).
- Edit `Internal_Tools/precommit_llm_safety_hook.sh` (already POSIX-correct).
- Address the gate's 200 KB packet cap (R7 — unrelated to migration).
- Promote anything to `PROJECT_BUILD_AND_AUDIT_QUEUE.md`.
- Commit or push anything other than the artifacts created in this readiness pass.

---

## §11 Boundaries footer (anti-drift)

- This pass does not decide. It maps.
- This pass does not authorize the migration. The operator decides the window.
- This pass does not authorize buyer-facing claims. Linux migration is an internal infrastructure choice; no customer-facing positioning attaches to it.
- This pass does not edit any §11-SIGNED spec. The Vendor Baseline Store spec's "Operational note: Linux migration plan" remains the authoritative architectural statement; this readiness pass is consistent with it, not a replacement for it.
- This pass does not promote anything to `PROJECT_BUILD_AND_AUDIT_QUEUE.md`. Migration scheduling is operator-driven.
- If any guidance here conflicts with a §11-SIGNED spec, the signed spec wins.

---

## §12 Named failure modes to recognize by name

- **Migration drama drift.** Turning a one-week mechanical pass into a multi-week rewrite. Stop scope creep at the §8 checklist boundary.
- **CRLF normalization bundled with content commit.** Mixing the normalization commit with a substantive content change makes the diff impossible to review. Normalization gets its own commit.
- **Operator-override abuse.** Using `complete_gate.py --operator-override` for anything other than the documented one-off cases (e.g. the line-ending normalization commit). The override is not a workaround for the tracker-size ceiling (R7).
- **pywin32 reinstall drift.** Manually `pip install pywin32` on Linux defeats the platform marker. The `requirements.txt` discipline is the source of truth.
- **Case-collision blindness.** Skipping the §5.3 collision check before switch. Linux will silently see what Windows hid.
- **Demo-script obsession.** Spending the migration window on `run_demo.ps1 → run_demo.sh` parity when the PoC demo is not on the NorthStar critical path.
- **Authority drift via readiness map.** Treating this readiness map as approval to start the migration. The map is signal; the operator decides the window.

---

**End of readiness pass. Map only. No migration executed.**
