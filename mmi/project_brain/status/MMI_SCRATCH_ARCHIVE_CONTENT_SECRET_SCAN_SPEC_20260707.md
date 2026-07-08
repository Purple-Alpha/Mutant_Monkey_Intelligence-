# MMI Scratch Archive Content Secret Scan Specification - 2026-07-07

## 1. Specification Verdict

SCRATCH ARCHIVE CONTENT SECRET SCAN SPEC PREPARED - DOC/CONTROL ONLY

Authority class:

SPEC_PREP_ONLY / AUDIT_ONLY

This specification defines the required content-level secret scan boundary for the preserved scratch archive. It does not authorize scan execution, build, cleanup, deletion, archive replacement, kernel testing, minifilter testing, IOCTL fuzzing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

## 2. Scope And Non-Scope

Scope:

- Define the content-level secret scan requirements for the preserved scratch archive.
- Define required scan categories, evidence artifacts, pass/fail criteria, and review gates.
- Preserve the distinction between preservation, cleanliness, and build readiness.
- Support later Gemini Paid API review of the specification and later scan-output review if separately authorized.

Non-scope:

- No scan execution.
- No archive extraction except as a future separately authorized scan operation.
- No build or test execution.
- No cleanup, deletion, pruning, reset, clean, force-push, or history rewrite.
- No clean replacement archive creation.
- No acceptance of content cleanliness.
- No perfect closure.

## 3. Archive Under Review

```text
ARCHIVE: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706.tar.gz
WINDOWS PATH: C:\MMI\mmi_boundary_scratch_BACKUP_20260706.tar.gz
MANIFEST: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706_MANIFEST.txt
HASH: /mnt/c/MMI/mmi_boundary_scratch_BACKUP_20260706.tar.gz.sha256
REPO BRANCH: mmi-phase2-commit
REMOTE: https://github.com/Purple-Alpha/Mutant_Monkey_Intelligence-.git
LATEST AUTHORITY COMMIT AT DRAFT TIME: 19edda6 Record Gemini audit model trial
```

The archive is classified as:

```text
DIRTY_PRESERVATION_BACKUP
```

## 4. Known Preserved Evidence

Preserved evidence currently includes:

- Scratch archive committed to the repository.
- Scratch archive manifest committed to the repository.
- Scratch archive SHA256 hash committed to the repository.
- Gemini audit model trial law committed to the repository.
- Filename-based secret scan on the manifest reported NO HITS.

Preservation status:

```text
PRESERVATION: PROVEN
```

## 5. Known Dirty / Unclean Evidence

The archive is not clean. Known dirty evidence includes:

- Build outputs: `.exe`, `.pdb`, `.obj`, `.iobj`, `.ipdb`.
- Build logs and state: `.tlog`, `.lastbuildstate`, `.recipe`.
- Python caches: `__pycache__`, `.pytest_cache`.
- Absolute Windows path metadata in build and helper files.
- Multiple deployment and build PowerShell scripts.
- Prior live/test scratch markers.

Cleanliness status:

```text
ARCHIVE CLEANLINESS: NOT PROVEN
SECRET CONTENT CLEANLINESS: NOT PROVEN
BUILD READINESS: 0 / 10
PERFECT CLOSURE: BLOCKED
```

## 6. Required Content-Scan Categories

A later separately authorized scan must define coverage for at least these textual content categories:

| Category | Required Coverage | Required Result Form |
|---|---|---|
| Source code | Python, C/C++, headers, project files, INF files, Markdown, text | scanned path count and redacted hits |
| Scripts | PowerShell, shell, batch-like files if present | scanned path count and redacted hits |
| Config/project files | `.vcxproj`, `.props`, `.inf`, `.json`, `.xml`, `.yml`, `.yaml`, `.ini`, `.cfg` | scanned path count and redacted hits |
| Documentation | Markdown, READMEs, handoff notes, research notes | scanned path count and redacted hits |
| Build logs/state | `.tlog`, `.lastbuildstate`, `.recipe`, helper path records | scanned path count and redacted hits |
| Cache text | readable cache files under `.pytest_cache` and similar | scanned path count and redacted hits |

The scan must classify unreadable or unsupported files as explicit evidence entries, not silent skips.

## 7. Required Binary-String Scan Categories

A later separately authorized scan must define binary string extraction requirements for:

- `.exe`
- `.pdb`
- `.obj`
- `.iobj`
- `.ipdb`
- `.pyc`
- other binary-like files detected by file type or extension

Required checks:

- Embedded absolute paths.
- Embedded usernames or profile paths.
- Embedded command lines.
- Embedded URLs.
- Embedded tokens or credential-like strings.
- Embedded private-key or certificate markers.
- Embedded build machine identifiers.

Binary scanning must not execute binaries or load drivers. It must be passive inspection only.

## 8. Required High-Entropy Detection Categories

A later separately authorized scan must specify high-entropy checks for:

- Long base64-like strings.
- Hex-encoded secrets.
- JWT-like structures.
- Randomized API-token-like values.
- Private-key-like material.
- Encoded blobs in source, config, logs, project files, and binary strings.

The specification must require a documented threshold policy, including:

```text
minimum string length
entropy threshold
file categories included
redaction format
false-positive handling
```

No allowlist may suppress a hit unless the allowlist entry is explicit, path-scoped, reasoned, and reviewable.

## 9. Required Credential-Pattern Categories

A later separately authorized scan must include pattern coverage for common secret families, including at minimum:

- Generic passwords, passphrases, tokens, API keys, bearer tokens, and auth headers.
- Private key block markers.
- SSH keys and known key file indicators.
- Cloud/service credentials.
- GitHub tokens and common repository tokens.
- OpenAI, Google/Gemini, Anthropic, Stripe, Supabase, Twilio, AWS, Azure, and GCP style token patterns where applicable.
- Certificate or PFX/P12 references.
- Windows path and user-profile leakage markers.
- Connection strings and database URLs.
- Rclone or backup-provider config references.

The scan report must distinguish:

```text
SECRET_HIT
PATH_METADATA_HIT
TEST_FIXTURE_CANDIDATE
FALSE_POSITIVE_CANDIDATE
UNREADABLE_FILE
UNSCANNED_FILE
```

## 10. Required Path / Metadata Leakage Checks

The scan must explicitly check for:

- `C:\` Windows paths.
- `/mnt/c/` WSL paths.
- user profile paths.
- machine names.
- Visual Studio build paths.
- SDK/toolchain paths.
- temp/cache paths.
- absolute include or library paths.

Known path metadata leakage is already confirmed. A later scan must quantify location and severity; it must not claim discovery as new proof of cleanliness.

## 11. Required Redaction Rules

A later scan report must never print full secrets. Required redaction form:

```text
<kind>:<prefix 4 chars>...<suffix 4 chars>:<length>:<hash prefix>
```

For path metadata, the report may show enough path context to prove the issue while avoiding unnecessary exposure of user-private directory details.

Required output must include:

- Rule identifier.
- File path within archive.
- Line number or binary offset when available.
- Redacted evidence snippet.
- Severity.
- Classification.
- Whether manual review is required.

## 12. Required Output Artifacts

If later scan execution is separately authorized, the output must include:

```text
MMI_SCRATCH_CONTENT_SCAN_REPORT_YYYYMMDD.json
MMI_SCRATCH_CONTENT_SCAN_SUMMARY_YYYYMMDD.md
MMI_SCRATCH_CONTENT_SCAN_COMMAND_LOG_YYYYMMDD.txt
MMI_SCRATCH_CONTENT_SCAN_REVIEW_PACKET_YYYYMMDD.md
```

The report must include:

- Archive path.
- Archive SHA256.
- Manifest path.
- Scan start/end timestamp.
- Operator identity.
- Tool identity and version.
- Rule-set version.
- File counts by category.
- Scanned file count.
- Skipped/unreadable file count.
- Hit count by severity.
- Full redacted findings list.
- Explicit zero-hit statement only if true for each category.

## 13. Pass / Fail Criteria

PASS requires all of the following:

- Archive hash matches the committed hash at scan time.
- Manifest matches the archive at scan time or mismatch is reported as a blocker.
- Textual content categories scanned or explicitly marked unsupported with blocker status.
- Binary strings scanned or explicitly marked unsupported with blocker status.
- High-entropy detection run or explicitly marked unsupported with blocker status.
- Credential-pattern checks run or explicitly marked unsupported with blocker status.
- Path/metadata leakage checks run and reported.
- No unredacted secrets in the scan output.
- No silent skipped files.
- Gemini Paid API review accepts the report as audit evidence.

FAIL occurs if any of the following are true:

- Secret hit remains unresolved.
- Unredacted secret appears in output.
- Archive hash mismatch is unexplained.
- Files are silently skipped.
- Binary artifacts are excluded without blocker status.
- Path metadata is hidden or minimized instead of reported.
- Scan tool identity is missing.
- Operator identity is missing.
- Output is not captured.

INCONCLUSIVE occurs if evidence is incomplete but no confirmed secret hit is present.

## 14. Blockers To Clean Closure

Clean closure remains blocked until:

- Content scan report exists.
- Gemini Paid API review of the scan report exists.
- Dirty archive classification is resolved into either accepted quarantine or clean replacement plan.
- Path metadata leakage is quantified and addressed by a separately authorized plan.
- All secret hits, if any, are triaged.
- Untracked/quarantine files are classified.

Current clean closure state:

```text
CLEAN CLOSURE: BLOCKED
```

## 15. Blockers To Build Readiness

Build readiness remains blocked because:

- The preserved scratch archive is dirty.
- Secret content cleanliness is not proven.
- Path metadata leakage is confirmed.
- Build output residue remains in preserved history.
- No build authority exists.
- No scan execution authority exists from this specification.

Current build readiness state:

```text
BUILD READINESS: 0 / 10
BUILD AUTHORITY: NO
```

## 16. Authority Boundaries

This specification does not authorize:

```text
BUILD: NO
EXECUTION: NO
SCAN EXECUTION: NO
CLEANUP: NO
DELETE: NO
GIT RESET: NO
GIT CLEAN: NO
FORCE-PUSH: NO
HISTORY REWRITE: NO
KERNEL TESTING: NO
MINIFILTER TESTING: NO
IOCTL FUZZING: NO
DEPLOYMENT: NO
RESIDUAL-RISK CLOSURE: NO
FALSIFIER CLOSURE: NO
M4 CLOSURE: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```

Any later scan execution requires a separate Matt decision.

## 17. Gemini Review Requirements

Gemini Paid API must review this specification as the secondary audit model before the lane can be accepted.

Required Gemini review output:

```text
AUDIT VERDICT:
ACCEPTED FACTS:
NOT_PROVEN ITEMS:
OPEN BLOCKERS:
AUTHORITY DRIFT CHECK:
FINDINGS TABLE:
NEXT LANE RECOMMENDATION USING CURRENT AUTHORITY:
EXPLICIT NON-AUTHORIZATIONS:
```

Gemini must not reassign ownership unless explicitly framed as:

```text
OPTIONAL_RECOMMENDATION_NOT_AUTHORITY
```

## 18. Next Required Matt Decision

Next required Matt decision:

```text
ACCEPT_SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_SPEC
```

or

```text
REOPEN_SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_SPEC_FOR_PATCH
```

No scan execution follows from acceptance unless Matt separately authorizes:

```text
TRIGGER_SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_EXECUTION_REQUIREMENTS
```

## Final State

```text
SCRATCH ARCHIVE CONTENT SECRET SCAN SPEC: PREPARED
DOC/CONTROL ONLY
PRESERVATION: PROVEN
ARCHIVE CLEANLINESS: NOT PROVEN
SECRET CONTENT CLEANLINESS: NOT PROVEN
CLEAN CLOSURE: BLOCKED
BUILD READINESS: 0 / 10
BUILD AUTHORITY: NO
EXECUTION AUTHORITY: NO
SCAN EXECUTION AUTHORITY: NO
CLEANUP AUTHORITY: NO
PERFECT CLOSURE: NO
```