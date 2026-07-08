# MMI Scratch Archive Content Scan Execution Requirements - 2026-07-07

## 1. Requirements Verdict

SCRATCH ARCHIVE CONTENT SCAN EXECUTION REQUIREMENTS DRAFTED - DOC/CONTROL ONLY

Authority class:

```text
SPEC_PREP_ONLY / AUDIT_ONLY
```

This artifact defines the minimum requirements that must be satisfied before any later content scan of the preserved scratch archive can be authorized. It is a requirements artifact only. It does not authorize scan execution, archive extraction, cleanup, deletion, reset, clean, force-push, build, kernel testing, minifilter testing, IOCTL fuzzing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

Current evidence state:

```text
PRESERVATION: PROVEN
ARCHIVE CLEANLINESS: NOT PROVEN
SECRET CONTENT CLEANLINESS: NOT PROVEN
BUILD READINESS: 0 / 10
SCAN EXECUTION AUTHORITY: NO
```

## 2. Scope And Non-Scope

Scope:

- Define the preconditions for a later content-level scan execution lane.
- Define the permitted future scan boundary, evidence capture, operator discipline, redaction, failure handling, and review gates.
- Bind future scan execution to the accepted content secret scan specification.
- Prevent drift from requirements into execution.
- Preserve a clear distinction between preservation, scan evidence, cleanliness, build readiness, and closure.

Non-scope:

- No scan execution in this lane.
- No archive extraction in this lane.
- No archive cleanup or replacement in this lane.
- No deletion, reset, clean, force-push, history rewrite, or pruning.
- No build or test execution.
- No kernel, minifilter, driver, IOCTL, deployment, or enforcement testing.
- No acceptance of content cleanliness.
- No residual-risk closure.
- No PERFECT closure.

## 3. Governing Inputs

A future scan execution lane must use these governing inputs:

```text
ARCHIVE: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706.tar.gz
MANIFEST: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706_MANIFEST.txt
HASH: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706.tar.gz.sha256
SPEC: mmi/project_brain/status/MMI_SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_SPEC_20260707.md
MODEL STANDARD: mmi/project_brain/status/LLM_MODEL_AUDIT_STANDARD_2026-07.md
AUTHORITY LAWS: mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md
LANE LAWS INDEX: mmi/project_brain/status/LLM_LANE_LAWS_INDEX_2026-07.md
```

The future scan must be evaluated against the exact archive hash committed in the repo. A hash mismatch is a blocker, not a warning.

## 4. Execution Preconditions

A future scan execution may be considered only after all of the following are explicitly accepted by Matt:

| Requirement | Status Required Before Execution |
|---|---|
| Requirements artifact accepted | ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS |
| Scan command plan drafted | ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN |
| Output artifact names fixed | ACCEPT_SCAN_OUTPUT_ARTIFACT_BOUNDARY |
| Redaction policy accepted | ACCEPT_SCAN_REDACTION_POLICY |
| Operator boundary accepted | ACCEPT_SCAN_OPERATOR_BOUNDARY |
| Gemini review prompt accepted | ACCEPT_GEMINI_SCAN_OUTPUT_REVIEW_PROMPT |
| No-build/no-cleanup reconfirmed | REQUIRED |

If any item is missing, the future scan lane remains blocked.

## 5. Future Execution Boundary

A future scan, if separately authorized, must remain:

```text
PASSIVE_INSPECTION_ONLY
NON_BUILD
NON_KERNEL
NON_RUNTIME
NON_ENFORCING
NON_CLEANUP
NON_DESTRUCTIVE
AUDIT_EVIDENCE_ONLY
```

Allowed future actions after separate authorization:

- Read the committed archive.
- Verify the archive hash.
- Enumerate archive members.
- Extract to a bounded temporary scan workspace only if the command plan explicitly authorizes it.
- Perform text scanning, binary string extraction, high-entropy detection, credential-pattern checks, metadata/path leakage checks, and unreadable-file accounting.
- Produce redacted evidence artifacts.

Forbidden future actions unless separately authorized in a later lane:

- Building anything.
- Running binaries from the archive.
- Loading drivers.
- Running kernel tests.
- Running minifilter tests.
- Running IOCTL fuzzing.
- Deleting, cleaning, pruning, resetting, or replacing the archive.
- Force-pushing or rewriting history.
- Closing residual risks or falsifiers.

## 6. Required Command Capture

A future scan must be captured in a reproducible terminal log. The required capture pattern is:

```bash
cd /mnt/c/MMI
pwd
date -u
git status --branch --short
git log --oneline -5
sha256sum -c mmi_boundary_scratch_BACKUP_20260706.tar.gz.sha256
# run only the separately accepted scan command plan
```

The future command log must include:

- exact working directory.
- UTC timestamp.
- git branch and head commit.
- archive hash verification result.
- tool name and version.
- operator identity.
- complete command line.
- start and end time.
- exit code.
- generated artifact list.

No future scan result may be accepted if the command log is missing.

## 7. Required Output Artifacts

A future scan execution, if separately authorized, must produce all of these artifacts:

```text
MMI_SCRATCH_CONTENT_SCAN_REPORT_YYYYMMDD.json
MMI_SCRATCH_CONTENT_SCAN_SUMMARY_YYYYMMDD.md
MMI_SCRATCH_CONTENT_SCAN_COMMAND_LOG_YYYYMMDD.txt
MMI_SCRATCH_CONTENT_SCAN_REVIEW_PACKET_YYYYMMDD.md
MMI_SCRATCH_CONTENT_SCAN_FINDINGS_REDACTED_YYYYMMDD.md
MMI_SCRATCH_CONTENT_SCAN_OPERATOR_GRADE_YYYYMMDD.md
GEMINI_SCRATCH_CONTENT_SCAN_REVIEW_YYYYMMDD.txt
```

Missing artifact handling:

```text
MISSING_REQUIRED_SCAN_ARTIFACT = BLOCKER
```

## 8. Required Scan Coverage

A future scan must cover at minimum:

| Coverage Area | Required Handling |
|---|---|
| Text files | source, scripts, configs, docs, logs, build state, caches |
| Binary strings | exe, pdb, obj, iobj, ipdb, pyc, unknown binary-like files |
| High entropy | base64-like, hex-like, JWT-like, random token-like strings |
| Credential patterns | common API keys, passwords, bearer tokens, private-key markers, cloud tokens, provider tokens |
| Metadata leakage | Windows paths, WSL paths, usernames, machine names, toolchain paths, temp/cache paths |
| Unicode bypass | zero-width, control-character, homoglyph, adjacent string literal risks |
| Archive risks | nested archives, encrypted entries, unsupported compression, unreadable entries |
| Redaction safety | no full secret value printed in any public artifact |

No silent skips are allowed.

## 9. Skip And Error Handling

Every skipped, unreadable, unsupported, encrypted, oversized, nested, malformed, or binary-limited item must be listed as evidence.

Required classifications:

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

Any silent skip invalidates the scan report.

## 10. Redaction Requirements

Future scan artifacts must never disclose full suspected secrets.

Required redaction format:

```text
<kind>:<prefix 4 chars>...<suffix 4 chars>:<length>:<hmac_prefix_12>
```

HMAC requirements:

- The HMAC salt must be generated at scan runtime.
- The salt must be held in memory only.
- The salt must not be written to public artifacts.
- The salt must not be committed.
- The salt must not be reused across reports.

If a future tool cannot support safe redaction, scan execution remains blocked.

## 11. Required Failure Conditions

A future scan result must be classified as failed if any of the following occur:

- archive hash mismatch.
- manifest mismatch not explained as blocker.
- missing command log.
- missing operator identity.
- missing tool identity/version.
- unredacted secret in output.
- silent skipped file.
- unreadable file not listed.
- encrypted file not blocker-classified.
- binary artifacts excluded without blocker status.
- high-entropy checks omitted.
- credential-pattern checks omitted.
- metadata/path leakage minimized or hidden.
- Gemini review missing.
- model/operator grade missing.

Failure means the scan evidence is not acceptable for cleanliness claims.

## 12. Required Review Gates

A future scan output must pass these gates before any later cleanliness discussion:

1. Operator self-review.
2. Codex doc/control review.
3. Gemini Paid API external audit review.
4. Matt acceptance decision.

Allowed Matt decisions after future scan review:

```text
ACCEPT_SCAN_OUTPUT_AS_EVIDENCE_ONLY
REOPEN_SCAN_OUTPUT_FOR_PATCH
REJECT_SCAN_OUTPUT_AS_INVALID
```

Forbidden conclusions after scan output acceptance:

```text
BUILD_READY
PERFECT_CLOSURE
GATED_STATUS
RESIDUAL_RISK_CLOSED
FALSIFIER_CLOSED
```

## 13. Model And Operator Grading

Every model and operator output associated with the future scan lane must include the universal grade block required by `LLM_MODEL_AUDIT_STANDARD_2026-07.md`.

Minimum accepted grade:

```text
A- / 90
```

Missing grade block:

```text
MODEL_TASK_INVALID_MISSING_GRADE
```

Grade below A-:

```text
MODEL_TASK_REQUIRES_REWORK
```

A high grade does not grant authority, close risk, or prove cleanliness.

## 14. Build-Blocking Findings

The following remain build-blocking after this requirements draft:

```text
SECRET CONTENT CLEANLINESS: NOT PROVEN
ARCHIVE CLEANLINESS: NOT PROVEN
CONTENT SCAN EXECUTION: NOT AUTHORIZED
SCAN OUTPUT: DOES NOT EXIST
GEMINI SCAN OUTPUT REVIEW: DOES NOT EXIST
RESIDUAL RISKS: OPEN
FALSIFIERS: OPEN
BUILD READINESS: 0 / 10
```

## 15. Explicit Non-Claims

This requirements artifact does not prove:

- secret cleanliness.
- trusted-agent identity.
- runtime integrity.
- command authenticity.
- replay resistance.
- recovery proof.
- containment.
- enforcement safety.
- production readiness.
- implementation readiness.
- M4 closure.
- PERFECT closure.
- GATED status.

This requirements artifact does not authorize:

- build.
- scan execution.
- archive extraction.
- cleanup.
- deletion.
- reset.
- clean.
- force-push.
- kernel implementation.
- runtime wiring.
- dispatcher mutation.
- scoreboard mutation.
- minifilter implementation.
- protected command execution.
- production altitude assignment.
- operational deployment.
- residual-risk closure.
- falsifier closure.

## 16. Next Required Matt Decision

Next required Matt decision:

```text
ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS
```

or

```text
REOPEN_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS_FOR_PATCH
```

After acceptance, the next evidence-determined lane is:

```text
DRAFT_SCRATCH_ARCHIVE_CONTENT_SCAN_COMMAND_PLAN
```

That next lane remains documentation/control only until separately accepted.

## 17. Final State

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

## 18. Model Task Grade

```text
MODEL: Codex
LANE: DOC/CONTROL
TASK: Draft scratch archive content scan execution requirements
ARTIFACTS TOUCHED: MMI_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS_20260707.md
AUTHORITY CLASS: SPEC_PREP_ONLY / AUDIT_ONLY
TASK_RESULT: COMPLETE
SELF_GRADE: A-
NUMERIC_SCORE: 93
LAW_COMPLIANCE_SCORE: 95
AUTHORITY_DISCIPLINE_SCORE: 97
EVIDENCE_DISCIPLINE_SCORE: 93
OVERCLAIM_DISCIPLINE_SCORE: 96
RESIDUAL_RISK_DISCIPLINE_SCORE: 92
OUTPUT_COMPLETENESS_SCORE: 91
KNOWN_LIMITATIONS: Requirements only; no scan command plan, no scan execution, no scan report, no Gemini output review.
NEXT_DECISION_OR_LANE: ACCEPT_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS or REOPEN_SCRATCH_ARCHIVE_CONTENT_SCAN_EXECUTION_REQUIREMENTS_FOR_PATCH
FORBIDDEN_ACTIONS_RECONFIRMED: build, scan execution, archive extraction, cleanup, delete, reset, clean, force-push, kernel/minifilter/IOCTL testing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, and GATED status remain NO.
```