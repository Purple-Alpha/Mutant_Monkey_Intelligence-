# MMI Scratch Archive Content Scan Command Plan - 2026-07-07

## 1. Command Plan Verdict

SCRATCH ARCHIVE CONTENT SCAN COMMAND PLAN DRAFTED - DOC/CONTROL ONLY

Authority class:

```text
SPEC_PREP_ONLY / AUDIT_ONLY
```

This artifact defines the proposed future command plan for a passive content scan of the preserved scratch archive. It is a command-plan artifact only. It does not authorize running the commands, extracting the archive, scanning content, cleanup, deletion, reset, clean, force-push, build, kernel testing, minifilter testing, IOCTL fuzzing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

Current state:

```text
REQUIREMENTS: ACCEPTED - DOC/CONTROL ONLY
COMMAND PLAN: DRAFTED - DOC/CONTROL ONLY
SCAN EXECUTION AUTHORITY: NO
ARCHIVE EXTRACTION AUTHORITY: NO
BUILD AUTHORITY: NO
SECRET CONTENT CLEANLINESS: NOT PROVEN
```

## 2. Scope And Non-Scope

Scope:

- Define the exact future command sequence for a separately authorized passive content scan.
- Define terminal capture requirements.
- Define output artifact paths.
- Define operator identity capture.
- Define preflight hash verification.
- Define blocker handling.
- Define post-run evidence checks.
- Define Gemini review handoff requirements.

Non-scope:

- No command execution in this lane.
- No archive extraction in this lane.
- No scan tool implementation in this lane.
- No cleanup, deletion, reset, clean, force-push, or history rewrite.
- No build, kernel, minifilter, IOCTL, deployment, or runtime testing.
- No cleanliness claim.
- No risk closure.

## 3. Preconditions Before Future Execution

The future scan command plan may be executed only after Matt explicitly records:

```text
ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN
```

The following must also remain true at future execution time:

| Gate | Required State |
|---|---|
| Repo root | `/mnt/c/MMI` |
| Branch | `mmi-phase2-commit` |
| Archive present | YES |
| Archive hash file present | YES |
| Requirements accepted | YES |
| Output artifact boundary accepted | YES |
| Redaction policy accepted | YES |
| Operator boundary accepted | YES |
| Gemini review prompt accepted | YES |
| Build authority | NO |
| Cleanup authority | NO |

If any gate is missing, future execution remains blocked.

## 4. Future Output Artifact Names

The proposed future run date placeholder is:

```text
YYYYMMDD
```

Future output artifacts must be:

```text
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_REPORT_YYYYMMDD.json
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_SUMMARY_YYYYMMDD.md
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_COMMAND_LOG_YYYYMMDD.txt
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_REVIEW_PACKET_YYYYMMDD.md
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_FINDINGS_REDACTED_YYYYMMDD.md
mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_OPERATOR_GRADE_YYYYMMDD.md
GEMINI_SCRATCH_CONTENT_SCAN_REVIEW_YYYYMMDD.txt
```

The scan may not overwrite earlier artifacts.

## 5. Proposed Future Terminal Capture Pattern

The future operator must capture the full terminal session.

Primary capture pattern:

```bash
cd /mnt/c/MMI
script -a /mnt/c/MMI/mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_COMMAND_LOG_YYYYMMDD.txt
```

Inside the captured session, the operator must run only the separately accepted future command sequence.

End capture:

```bash
exit
```

Fallback capture pattern if `script` causes terminal instability:

```bash
cd /mnt/c/MMI
# Use a separately accepted non-interactive command with stdout/stderr redirected
# to mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_COMMAND_LOG_YYYYMMDD.txt
```

Fallback capture must be accepted before use.

## 6. Proposed Future Preflight Commands

These commands are proposed for future execution only. They must not be run under this command-plan lane.

```bash
cd /mnt/c/MMI
pwd
date -u
whoami
hostname
git status --branch --short
git log --oneline -5
git remote -v
sha256sum -c mmi_boundary_scratch_BACKUP_20260706.tar.gz.sha256
tar -tzf mmi_boundary_scratch_BACKUP_20260706.tar.gz > /tmp/mmi_scratch_scan_manifest_runtime_YYYYMMDD.txt
wc -l /tmp/mmi_scratch_scan_manifest_runtime_YYYYMMDD.txt
cmp -s /tmp/mmi_scratch_scan_manifest_runtime_YYYYMMDD.txt mmi_boundary_scratch_BACKUP_20260706_MANIFEST.txt
echo "MANIFEST_COMPARE_EXIT_CODE=$?"
```

Preflight blockers:

```text
HASH_MISMATCH = BLOCKER
MANIFEST_MISMATCH = BLOCKER UNLESS FULLY EXPLAINED
DIRTY_GIT_STATE = REVIEW_BLOCKER
MISSING_ARCHIVE = BLOCKER
MISSING_HASH_FILE = BLOCKER
MISSING_MANIFEST = BLOCKER
```

## 7. Proposed Future Workspace Boundary

If extraction is separately authorized, it must use a bounded temporary scan workspace.

Proposed future workspace:

```text
/tmp/mmi_scratch_content_scan_YYYYMMDD
```

Required constraints:

- workspace must be outside the repo.
- workspace must be unique per run.
- workspace must not be reused.
- workspace must not be treated as cleanup-authorized by this plan.
- workspace deletion requires separate cleanup authority.

No extraction is authorized by this draft.

## 8. Proposed Future Passive Scan Phases

The future scan must run as passive inspection only.

Required phases:

1. Archive hash verification.
2. Runtime manifest generation.
3. Manifest comparison.
4. Bounded extraction if separately authorized.
5. File classification.
6. Text content scan.
7. Binary string extraction scan.
8. High-entropy candidate detection.
9. Credential-pattern detection.
10. Unicode/control-character bypass detection.
11. Metadata/path leakage detection.
12. Skip/unreadable/unsupported/encrypted file accounting.
13. Redacted findings generation.
14. Summary generation.
15. Operator grade generation.
16. Review packet generation.

No phase may run binaries from the archive.

## 9. Proposed Future Scan Tool Requirements

Any future scan tool must report:

- tool name.
- tool version.
- rule-set version.
- start time.
- end time.
- exit code.
- archive hash.
- repo head commit.
- files discovered.
- files scanned.
- files skipped.
- files unreadable.
- files unsupported.
- encrypted or nested archive entries.
- findings by severity.
- redaction method.
- blocker list.

Tool output must be deterministic enough for review.

## 10. Required Redaction Behavior

Future output must never include a full suspected secret.

Required format:

```text
<kind>:<prefix 4 chars>...<suffix 4 chars>:<length>:<hmac_prefix_12>
```

The future command plan requires runtime-only HMAC salt handling:

```text
SALT WRITTEN TO DISK: NO
SALT COMMITTED: NO
SALT REUSED: NO
SALT PRINTED: NO
```

Any unredacted secret in output invalidates the scan.

## 11. Required Classifications

Every future finding or file state must use one of these classifications:

```text
SCANNED
SECRET_HIT
PATH_METADATA_HIT
HIGH_ENTROPY_CANDIDATE
UNICODE_CREDENTIAL_CONTEXT_REVIEW
BINARY_STRING_HIT
UNREADABLE_FILE_BLOCKER
UNSUPPORTED_FILE_BLOCKER
ENCRYPTED_UNSCANNED_BLOCKER
NESTED_ARCHIVE_REVIEW_BLOCKER
OVERSIZED_FILE_POLICY_BLOCKER
FALSE_POSITIVE_CANDIDATE
TEST_FIXTURE_CANDIDATE
```

No silent skip is allowed.

## 12. Required Post-Run Checks

After any future authorized scan, the operator must verify:

```bash
cd /mnt/c/MMI
ls -lh mmi/project_brain/status/MMI_SCRATCH_CONTENT_SCAN_*_YYYYMMDD.* GEMINI_SCRATCH_CONTENT_SCAN_REVIEW_YYYYMMDD.txt 2>/dev/null
git status --branch --short
```

The operator must then confirm:

```text
COMMAND_LOG_EXISTS: YES / NO
REPORT_JSON_EXISTS: YES / NO
SUMMARY_MD_EXISTS: YES / NO
REVIEW_PACKET_EXISTS: YES / NO
REDACTED_FINDINGS_EXISTS: YES / NO
OPERATOR_GRADE_EXISTS: YES / NO
GEMINI_REVIEW_EXISTS: YES / NO
UNREDACTED_SECRET_IN_OUTPUT: YES / NO / UNKNOWN
SILENT_SKIPS_DETECTED: YES / NO / UNKNOWN
BLOCKERS_PRESENT: YES / NO
```

Any `NO` for required artifacts is a blocker.

## 13. Gemini Review Handoff Requirements

After future scan artifacts exist, Gemini Paid API must review the scan output as an external audit model.

Gemini must receive:

- this command plan.
- accepted scan execution requirements.
- scan summary.
- redacted findings.
- command log.
- operator grade.
- report JSON if practical.

Gemini must grade itself using `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.

Required Gemini verdict options:

```text
GEMINI_SCAN_REVIEW_PASS_AS_EVIDENCE_ONLY
GEMINI_SCAN_REVIEW_FAIL_PATCH_REQUIRED
GEMINI_SCAN_REVIEW_INVALID_MISSING_EVIDENCE
```

Gemini may not grant build authority, cleanup authority, closure, or trust.

## 14. Acceptance And Reopen Criteria

This command plan may be accepted only as documentation/control.

Acceptance means:

```text
THE FUTURE COMMAND PLAN IS STRUCTURALLY ACCEPTABLE.
```

Acceptance does not mean:

```text
RUN THE SCAN.
EXTRACT THE ARCHIVE.
CLEAN THE ARCHIVE.
BUILD ANYTHING.
CLOSE CLEANLINESS.
CLOSE RESIDUAL RISK.
```

Reopen is required if:

- command capture is ambiguous.
- output artifacts are missing or poorly named.
- redaction policy is incomplete.
- blocker handling is incomplete.
- Gemini review handoff is missing.
- operator/model grading is missing.
- any wording implies execution authority.

## 15. Build-Blocking Findings

The following remain build-blocking:

```text
SECRET CONTENT CLEANLINESS: NOT PROVEN
ARCHIVE CLEANLINESS: NOT PROVEN
SCAN COMMAND PLAN: DRAFTED ONLY
SCAN EXECUTION: NOT AUTHORIZED
SCAN OUTPUT: DOES NOT EXIST
GEMINI SCAN OUTPUT REVIEW: DOES NOT EXIST
RESIDUAL RISKS: OPEN
FALSIFIERS: OPEN
BUILD READINESS: 0 / 10
```

## 16. Explicit Non-Claims

This command plan does not prove:

- archive cleanliness.
- secret content cleanliness.
- runtime integrity.
- command authenticity.
- containment.
- enforcement safety.
- production readiness.
- implementation readiness.
- M4 closure.
- PERFECT closure.
- GATED status.

This command plan does not authorize:

- scan execution.
- archive extraction.
- cleanup.
- deletion.
- reset.
- clean.
- force-push.
- build.
- kernel implementation.
- runtime wiring.
- minifilter implementation.
- IOCTL testing.
- dispatcher mutation.
- scoreboard mutation.
- production altitude assignment.
- deployment.
- residual-risk closure.
- falsifier closure.

## 17. Next Required Matt Decision

Next required Matt decision:

```text
ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN
```

or

```text
REOPEN_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN_FOR_PATCH
```

After acceptance, the next evidence-determined lane is:

```text
DRAFT_SCAN_OUTPUT_ARTIFACT_BOUNDARY
```

That next lane remains documentation/control only.

## 18. Final State

```text
SPEC_PREP_ONLY / AUDIT_ONLY
BUILD AUTHORITY: NO
SCAN EXECUTION AUTHORITY: NO
ARCHIVE EXTRACTION AUTHORITY: NO
CLEANUP AUTHORITY: NO
DELETE AUTHORITY: NO
RESET / CLEAN AUTHORITY: NO
FORCE-PUSH AUTHORITY: NO
KERNEL IMPLEMENTATION AUTHORITY: NO
RUNTIME WIRING: NO
MINIFILTER DRIVER IMPLEMENTATION: NO
PROTECTED COMMAND EXECUTION: NO
DISPATCHER MUTATION: NO
SCOREBOARD MUTATION: NO
M4 CLOSURE: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```

## 19. Model Task Grade

```text
MODEL: Codex
LANE: DOC/CONTROL
TASK: Draft scratch archive content scan command plan
ARTIFACTS TOUCHED: MMI_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN_20260707.md
AUTHORITY CLASS: SPEC_PREP_ONLY / AUDIT_ONLY
TASK_RESULT: COMPLETE
SELF_GRADE: A-
NUMERIC_SCORE: 93
LAW_COMPLIANCE_SCORE: 95
AUTHORITY_DISCIPLINE_SCORE: 98
EVIDENCE_DISCIPLINE_SCORE: 93
OVERCLAIM_DISCIPLINE_SCORE: 96
RESIDUAL_RISK_DISCIPLINE_SCORE: 92
OUTPUT_COMPLETENESS_SCORE: 91
KNOWN_LIMITATIONS: Command plan only; no command execution, no extraction, no scan output, no Gemini output review.
NEXT_DECISION_OR_LANE: ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN or REOPEN_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN_FOR_PATCH
FORBIDDEN_ACTIONS_RECONFIRMED: build, scan execution, archive extraction, cleanup, delete, reset, clean, force-push, kernel/minifilter/IOCTL testing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, and GATED status remain NO.
```