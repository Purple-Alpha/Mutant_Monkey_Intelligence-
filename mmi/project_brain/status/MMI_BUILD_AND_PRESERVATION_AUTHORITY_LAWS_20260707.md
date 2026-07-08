# MMI Build and Preservation Authority Laws - 2026-07-07

## Verdict

BUILD AND PRESERVATION AUTHORITY LAWS PREPARED - DOC/CONTROL ONLY

Authority class:

SPEC_PREP_ONLY / AUDIT_ONLY

These laws bind build, preservation, backup, model ownership, next-lane selection, and closeout behavior. They do not authorize build, execution, cleanup, deletion, reset, force-push, kernel testing, minifilter testing, IOCTL fuzzing, deployment, or perfect closure.

## Current Standing Snapshot

```text
PROJECT STANDING: GOOD
REMOTE SYNC: CONFIRMED THROUGH 5fcbab5
WORKTREE CLEAN: YES at checkpoint
AUDIT LOG: PRESERVED
SCRATCH ARCHIVE: PRESERVED
MANIFEST: PRESERVED
HASH: PRESERVED
SECRET-FILENAME SCAN: NO HITS
PATH METADATA LEAKAGE: CONFIRMED
SECRET CONTENT CLEANLINESS: NOT PROVEN
PERFECT CLOSURE: BLOCKED
BUILD AUTHORITY: NO
```

## Scoreboard

```text
PRESERVATION SCORE: 8.5 / 10
OWNER: Codex ledger, Matt WSL evidence, Gemini review
EVIDENCE: repo synced; audit log committed; dirty archive committed; manifest committed; hash committed; filename scan no hits
BLOCKERS: content scan not done; dirty path metadata remains
NEXT IMPROVEMENT: content secret scan spec + external review

CLEAN CLOSURE SCORE: 5 / 10
OWNER: Codex spec, Gemini challenge review, Matt acceptance
EVIDENCE: evidence trail is strong; path leak confirmed
BLOCKERS: secret content not proven; clean replacement not planned
NEXT IMPROVEMENT: clean replacement plan after content scan

BUILD READINESS SCORE: 0 / 10
OWNER: Codex build-law spec first
EVIDENCE: no build authority; secret cleanliness unproven; dirty archive unresolved; build laws not accepted yet
NEXT IMPROVEMENT: build and preservation authority laws accepted, then narrow build-readiness review
```

## Law 1 - No Build Without Named Matt Authorization

No build, build-prep, implementation, test execution, kernel work, minifilter work, IOCTL fuzzing, deployment, or runtime wiring may begin unless a named Matt authorization token is recorded.

Required token:

```text
MATT_AUTHORIZES_BUILD_SLICE:<named-slice>:<date>
```

If missing:

```text
BUILD BLOCKED
```

## Law 2 - Build Authority Is Not Inherited

A clean repo, accepted audit, accepted spec, preserved backup, model verdict, or prior task acceptance never grants build authority.

If an artifact implies build authority without explicit Matt authorization:

```text
AUTHORITY DRIFT - REOPEN FOR PATCH
```

## Law 3 - One Build Means One Narrow Slice

A future build authorization must name exactly:

```text
scope, files, forbidden files, allowed commands, expected outputs, evidence bundle, rollback boundary, and review model
```

No broad or implied build lane is valid.

## Law 4 - No Kernel First

User-mode, dummy, non-kernel, and non-enforcing lanes must be exhausted before any kernel, minifilter, IOCTL, driver, or enforcement lane is considered.

## Law 5 - No Silent Tool Action

Cursor, Gemini, Aider, Codex, scripts, agents, or CLIs may not build, test, mutate, commit, push, clean, delete, or restore unless the active lane explicitly grants that action.

## Law 6 - Evidence Or It Did Not Happen

Every allowed action must leave:

```text
command, timestamp/date, output capture, file path, git hash where applicable, and model/operator identity
```

## Law 7 - Failure Stops The Lane

Any unexpected file change, command failure, dirty workspace, secret hit, authority ambiguity, model impersonation, or unclassified generated proposal stops forward movement.

Next allowed action becomes:

```text
AUDIT / TRIAGE ONLY
```

## Law 8 - Build Output Is Quarantine Until Reviewed

Binaries, logs, .pdb, .obj, .iobj, .ipdb, .tlog, caches, generated scripts, generated code proposals, and dirty archives are quarantine artifacts until classified.

## Law 9 - No Cleanup As Build Prep

No delete, clean, reset, restore, force-push, or history rewrite may be hidden inside build preparation.

Cleanup requires its own Matt authorization and evidence trail.

## Law 10 - Matt Decision Required At Every Gate

No agent may infer acceptance from silence, confidence, prior acceptance, green status, or a model saying something is safe.

## Law 11 - Daily Backup Before Build Work

No build-prep, implementation, cleanup, or test lane may begin unless the day's backup state is recorded.

Required evidence:

```text
backup path, backup hash if available, backup manifest if available, git commit hash, push confirmation, remote head confirmation
```

If missing:

```text
PRESERVATION BLOCKED - BACKUP FIRST
```

## Law 12 - Commit Before Context Switch

Before leaving a completed audit/control lane, all accepted audit artifacts must be either:

```text
committed and pushed, or explicitly listed as intentionally untracked/quarantine
```

No silent loose files.

If unexplained untracked files exist:

```text
CLOSEOUT BLOCKED
```

## Law 13 - Push Is Part Of Preservation

A local commit is not enough for preservation closure.

A preservation artifact is protected only after:

```text
git commit exists, git push succeeds, remote head equals local head
```

Required evidence:

```text
git status --branch --short
git log --oneline -5
git ls-remote origin refs/heads/mmi-phase2-commit
```

## Law 14 - Daily End-Of-Session Standing Check

Every session ends with:

```text
repo state, remote state, untracked/quarantine list, backup state, next lane, primary model, secondary model, and forbidden actions
```

## Law 15 - Backup Does Not Equal Clean

A backup may preserve a dirty state.

Every backup must be labeled as one of:

```text
CLEAN_BACKUP
DIRTY_PRESERVATION_BACKUP
QUARANTINE_BACKUP
UNKNOWN_BACKUP
```

If unlabeled:

```text
BACKUP QUALITY UNKNOWN
```

## Law 16 - No Work On Top Of Unknown State

Before any new lane starts, repo state must be known.

If `git status --branch --short` has unexplained changes:

```text
NO NEW LANE
```

The only allowed next action is:

```text
CLASSIFY_WORKTREE_STATE
```

## Law 17 - Evidence Decides The Next Lane

Matt is not asked to pick between options when the rubric, score, or decision matrix already determines the next safe lane.

If evidence is sufficient:

```text
STATE THE NEXT LANE, SCORE, EVIDENCE, OWNER MODEL, REVIEW MODEL, AND BLOCKED ALTERNATIVES
```

If evidence is insufficient:

```text
STATE THE MISSING EVIDENCE AND OPEN A REQUIREMENTS/AUDIT LANE
```

## Law 18 - Model Role Separation

```text
CODEX: repo state, documentation/control artifacts, git evidence, local verification, law enforcement
GEMINI PAID API: external audit/challenge review where separately invoked and output-captured
CURSOR: editor/operator only unless explicitly assigned a lane
AIDER: read-only assistant by default; no edit authority unless separately authorized
MATT: final authority gate and explicit authorization source
```

No model may impersonate another model's audit role.

No audit is accepted without captured tool identity and output log.

## Law 19 - Every Next Lane Must Name The Model

No next lane is valid unless it states:

```text
PRIMARY MODEL:
SECONDARY REVIEW MODEL:
EXECUTION OPERATOR:
FORBIDDEN TOOLS/ACTIONS:
OWNERSHIP REASON:
```

## Current Evidence-Determined Next Lane

```text
NEXT LANE: SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_SPEC
PRIMARY MODEL: Codex
SECONDARY REVIEW MODEL: Gemini Paid API
EXECUTION OPERATOR: Matt / WSL terminal after boundary acceptance
CURSOR ROLE: None unless explicitly reopened
AIDER ROLE: None
WHY: secret content cleanliness is NOT_PROVEN; filename scan had no hits; dirty path metadata remains confirmed
```

Blocked alternatives:

```text
BUILD: BLOCKED
CLEANUP: BLOCKED
DELETE: BLOCKED
KERNEL TESTING: BLOCKED
MINIFILTER TESTING: BLOCKED
RESTORE-CHECK SCRIPT EXECUTION: BLOCKED UNTIL CLASSIFIED
```

## Final State

```text
BUILD AND PRESERVATION AUTHORITY LAWS: ESTABLISHED
DOC/CONTROL ONLY
BUILD AUTHORITY: NO
EXECUTION AUTHORITY: NO
CLEANUP AUTHORITY: NO
DELETE AUTHORITY: NO
PERFECT CLOSURE: NO
```
