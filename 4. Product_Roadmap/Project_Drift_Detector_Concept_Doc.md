# Project Drift Detector — Concept Doc / Detection Spec (v0, design only)

**Status:** DRAFT — design/spec artifact only. No build authorization. Not wired into
`check_drift()` or dispatcher gating. Preserved for later read-only implementation.

**Authority note:** This document describes a *detector*. The detector reveals drift.
It does not decide project direction, repair files, rewrite scoreboard rows, track
untracked files, or promote contracts. See Hard Rule HR-1.

---

## 1. Purpose

Catch the drift categories that have actually caused failures in this project —
primarily **parallel-workflow drift**, where a second session (or MCP) writes
contracts/docs/scoreboard rows that fall out of sync with each other and silently
steer the dispatcher.

These are not normal code failures. They are **governance-routing failures**:

- a contract exists but the scoreboard does not know about it,
- a scoreboard row claims evidence that is not actually present,
- the dispatcher reads a different project state than the human-facing state file
  describes.

`verify_build_truth.py` checks whether committed *documentation claims* match
*code/git reality*. This detector checks whether the *artifacts that steer MMI* are
internally consistent with each other.

## 2. Truth-layer separation (why this is a third tool, not an edit to the others)

| Tool | Question it answers | Gates dispatcher? |
|---|---|---|
| `verify_build_truth.py` | Do committed docs match code/git reality? | Yes (via `check_drift`) |
| `health_check.py` | What is the passive operational status? | No |
| **`detect_drift.py` (proposed)** | Are the MMI-steering artifacts internally consistent? | **No** (advisory until a check is explicitly promoted) |

## 3. Design principles

1. **Read-only.** Detects and reports. Never edits, commits, stashes, or moves files.
2. **Advisory by default.** Does not feed `check_drift()` / the dispatcher hard-stop
   unless a specific check is explicitly promoted (see §5, §7).
3. **Severity-tiered, not binary.** Untracked roadmap files are a normal side effect
   of parallel sessions; they are only dangerous when they become
   **routing-relevant**, **authority-relevant**, or **evidence-relevant**.
4. **Falsifiable.** Each check states its reality source, its claim source, and the
   exact disagreement that triggers it.
5. **No new dependencies.** stdlib + git only, matching `verify_build_truth.py`.

## 4. Severity tiers

Two axes: intrinsic severity, and enforcement status.

- `INFO` — visibility only.
- `WARN` — worth a human glance; never affects exit code.
- `BLOCK-candidate` — *would* be a blocker, but the check has **not** been formally
  promoted. Reported in text; the detector still **exits 0**. This is the key tier:
  it prevents advisory detection from silently becoming governance authority.
- `BLOCK` — a check that has been explicitly promoted from BLOCK-candidate. Only a
  promoted check can cause `exit 1` and become eligible to feed `check_drift()`.

A check's intrinsic danger does not change its enforcement. D2 and D3 are the most
dangerous categories, but until promoted they report as **BLOCK-candidate** and the
detector exits 0.

## 5. Hard rules

- **HR-1 — Detector is not an authority source.** `detect_drift.py` may report
  authority inconsistencies, but it must not become an authority source itself. It
  must not repair files, rewrite rows, promote contracts, or decide direction.
- **HR-2 — Promotion is a recorded operator act (PROPOSAL — needs Matt sign-off).**
  Moving a check from BLOCK-candidate to BLOCK must be an explicit, recorded operator
  decision, not a code default and not a script's choice. Otherwise promotion becomes
  an ungoverned side-door that contradicts HR-1. *This rule is proposed, not settled.*

## 6. Detection checks (priority order)

### D2 — Signed contract with no scoreboard row  — HIGHEST PRIORITY
- **Reality source:** every `4. Product_Roadmap/*Contract*.md` whose status line reads `§11 SIGNED`.
- **Claim source:** rows in `Blue_Team_Swarm_70_Agent_Scoreboard.md`.
- **Rule:** each signed contract must have a scoreboard row referencing its filename
  (or known alias). A signed contract with no matching row → dispatcher falls back to
  generic RESEARCH; the human sees a signed artifact but MMI cannot route it. False
  sense of completion.
- **Severity:** `BLOCK-candidate` (most dangerous; first to promote).

### D3 — Scoreboard row claims evidence that does not exist  — BLOCKER-CLASS
- **Reality source:** filesystem + `git rev-parse` / `git cat-file`.
- **Claim source:** `GATED` row cells citing `audit_outputs/....md` paths and commit hashes.
- **Rule:** for each `GATED` row, the cited audit-output path must exist (or be a
  committed object) and each cited short hash must resolve. Missing file or unknown
  hash → phantom authority: the system appears governed but the proof chain is broken.
- **Severity:** `BLOCK-candidate` for `GATED` rows; `WARN` for non-gated.

### D1 — Untracked files that influence routing  — WARN BY DEFAULT
- **Reality source:** `git status --porcelain` (untracked entries).
- **Why:** `get_next_concept_without_contract()` does a raw `os.listdir()` of
  `4. Product_Roadmap/`, so untracked `*Concept_Doc*` / `*Contract*` files are live
  dispatcher inputs.
- **Rule:** list untracked files under paths the dispatcher reads by directory listing.
- **Parallel-draft rule:** parallel roadmap drafts may exist untracked, but they
  cannot become authoritative while untracked. An untracked concept/doctrine draft
  is acceptable only while it explicitly remains non-authoritative (for example,
  `CONCEPT — no build authorization`). If an untracked file claims signed status,
  build readiness, gated status, dispatcher authority, lab verdict authority, or
  evidence authority, it becomes a BLOCK-candidate.
- **Severity:** `WARN` for concept docs (parallel sessions create these on purpose —
  treating them as blockers would punish the workflow the project depends on).
  Escalates to `BLOCK-candidate` only when an untracked file is a `*Contract*` that is
  `§11 SIGNED` on disk or any roadmap file claims authority while untracked
  (a signed/build-ready/gated-but-untracked artifact = the #88/#89/#92/#99 failure).

### D4 — Dirty working tree on tracked files  — WARN, NARROW ESCALATION
- **Reality source:** `git status --porcelain` (modified/staged tracked entries).
- **Why:** dispatcher and gates read files off disk; uncommitted edits mean committed
  truth and routing truth disagree.
- **Rule:** report tracked files with uncommitted modifications (staged vs unstaged).
- **Severity:** `WARN` (normal during active work). Escalates to `BLOCK-candidate`
  only if the dirty file is `MMI_CURRENT_STATE.md`, the scoreboard, or the dispatcher
  itself — the three files that define routing authority.

### D5 — `MMI_CURRENT_STATE.md` vs dispatcher disagreement  — VISIBLE, NOT FATAL
- **Reality source:** parsed output of `python3 scripts/mmi_dispatch.py` (`MODE` / `AUTHORIZED_TASK`).
- **Claim source:** `MODE:` / `AUTHORIZED_TASK:` headers in `MMI_CURRENT_STATE.md`.
- **Rule:** flag when the human-readable state file names a different mode/task than
  the dispatcher computes.
- **Severity:** `WARN`. The state file is a human-readable artifact; the dispatcher is
  operational routing truth. Mismatch should be visible but not automatically fatal
  unless the project later decides the state file is also authoritative.

### D6 — Scoreboard internal consistency  — SECONDARY HYGIENE
- **Reality source:** the row table.
- **Claim source:** the `BREADTH RUNWAY ... of 70` header.
- **Rule:** detect duplicate row IDs (parallel sessions appending the same number) and
  header/row-count mismatch beyond what `verify_build_truth.py` already covers.
- **Severity:** `WARN`. Good hygiene, less dangerous than D2/D3.

## 7. Output format

```
============================================================
PROJECT DRIFT DETECTOR  (cross-artifact + dispatcher-input integrity)
============================================================
[BLOCK-candidate] D2 signed-contract-no-row: '<file>' is §11 SIGNED but has no scoreboard row
[ WARN] D1 untracked-routing-input: N untracked docs in 4. Product_Roadmap/ (parallel-session normal)
[ INFO] D4 dirty-tree: 0 tracked files modified
------------------------------------------------------------
SUMMARY: 0 BLOCK, 1 BLOCK-candidate, 1 WARN, 1 INFO
EXIT: 0  (no promoted BLOCK checks)
```

## 8. Exit codes

- `0` — no **promoted** `BLOCK` findings. BLOCK-candidate / WARN / INFO all allow exit 0.
- `1` — at least one **promoted** `BLOCK` finding.

This keeps the detector safe to run anywhere and lets the project later wire only
`exit == 1` into `check_drift()` — without dragging benign parallel-session WARNs or
un-promoted BLOCK-candidates into a hard dispatcher stop.

## 9. Build order (when authorized)

1. Read-only `scripts/detect_drift.py`.
2. Implement **D2** and **D3** first (highest track-record danger), as BLOCK-candidate.
3. D1, D4, D5 as WARN radar.
4. D6 last.
5. **Do not** wire into `check_drift()` / dispatcher gating until specific checks are
   explicitly promoted per HR-2.

## 10. Explicit non-authorizations / anti-overbuild

- No auto-fixing (no auto-adding rows, no auto-tracking files, no auto-stashing).
- No file watchers / daemons / background processes.
- No modification of the dispatcher's hard-stop behavior in this artifact.
- No semantic analysis of contract *content* — existence/consistency only.
- No build authorization is implied by this document.
