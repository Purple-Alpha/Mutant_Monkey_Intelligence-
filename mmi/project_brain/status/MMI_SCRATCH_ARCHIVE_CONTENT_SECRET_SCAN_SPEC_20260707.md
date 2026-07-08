# MMI Scratch Archive Content Secret Scan Specification - 2026-07-07

## 1. Specification Verdict

SCRATCH ARCHIVE CONTENT SECRET SCAN SPEC PATCHED - READY FOR RE-REVIEW - DOC/CONTROL ONLY

Authority class:

SPEC_PREP_ONLY / AUDIT_ONLY

This specification defines the required content-level secret scan boundary for the preserved scratch archive. It is now patched to bind the minimum scan mechanics, safety controls, redaction rules, access controls, reproducibility requirements, and failure blockers required before any later scan execution can be considered. It does not authorize scan execution, build, cleanup, deletion, archive replacement, kernel testing, minifilter testing, IOCTL fuzzing, deployment, residual-risk closure, falsifier closure, M4 closure, PERFECT closure, or GATED status.

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

## 17. Ceiling-Completeness Patch Requirements

Patch verdict:

```text
CONTENT PATCH APPLIED - SECRET SCAN SPEC READY FOR GEMINI RE-REVIEW - DOC/CONTROL ONLY
```

This patch closes the specification-level blindspots identified by Gemini Paid API. These controls are binding specification mechanics, not optional implementation ideas.

Binding rule:

```text
The later scan execution requirements MUST implement the exact minimum mechanics in this specification. Any unsupported mechanic MUST be reported as BLOCKER_UNSUPPORTED_MECHANIC and prevents PASS.

No scan may receive PASS unless every required rule family, decoder, archive traversal limit, timeout, redaction rule, access-control rule, output-artifact rule, and reproducibility rule defined here is either executed successfully or explicitly recorded as BLOCKER_UNSUPPORTED_MECHANIC.
```

This patch still does not authorize scan execution.

## 18. Regex Safety Requirements

All credential-pattern rules must be ReDoS-resistant.

Forbidden regex constructs:

- nested unbounded quantifiers such as `(.*)+`, `(.+)+`, or `([A-Za-z0-9]+)*`.
- ambiguous alternation over unbounded groups.
- unbounded dot-star before secret capture.
- backreferences in scan rules unless explicitly justified.
- catastrophic lookaround patterns over arbitrary-length input.

Every regex rule must define:

- `rule_id`
- intended secret family
- maximum input window
- maximum match length
- boundary conditions
- capture group used for redaction
- false-positive notes
- ReDoS review status

Any regex without a ReDoS review status is invalid and must be reported as:

```text
BLOCKER_UNREVIEWED_REGEX_RULE
```

## 19. Bounded Scan Windows

Regex scanning must operate on bounded windows.

Required defaults:

```text
MAX_LOGICAL_LINE_LENGTH: 16 KiB
MAX_REGEX_EVALUATION_WINDOW: 64 KiB
MAX_SINGLE_MATCH_LENGTH: 8 KiB
CHUNK_OVERLAP: maximum supported secret length + 32 bytes
```

Files exceeding line/window limits must be chunked with overlap.

Truncated scan windows must be recorded as:

```text
WINDOW_TRUNCATED_SCAN_EVENT
```

Window truncation without a recorded event prevents PASS.

## 20. Minimum Credential Pattern Families

The later scan requirements must include at least these pattern families:

| Family | Minimum Pattern / Handling |
|---|---|
| AWS access key id | `AKIA[0-9A-Z]{16}`, `ASIA[0-9A-Z]{16}` |
| AWS secret candidate | key/value context plus high entropy at configured threshold |
| GitHub classic PAT | `ghp_[A-Za-z0-9_]{36,}` |
| GitHub fine-grained/app/refresh token | `github_pat_[A-Za-z0-9_]{80,}` |
| OpenAI key | `sk-[A-Za-z0-9_-]{20,}`, `sk-proj-[A-Za-z0-9_-]{20,}` |
| Google API key candidate | `AIza[0-9A-Za-z_-]{35}` |
| Anthropic key candidate | `sk-ant-[A-Za-z0-9_-]{20,}` |
| Stripe keys | `sk_live_`, `rk_live_`, `pk_live_` with expected suffix length |
| Slack token | `xox[baprs]-[A-Za-z0-9-]{10,}` |
| JWT | `eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` |
| Private key block | `BEGIN .* PRIVATE KEY` |
| OpenSSH private key | `BEGIN OPENSSH PRIVATE KEY` |
| Database URLs | `postgres://`, `postgresql://`, `mysql://`, `mongodb://`, `redis://` with credential context |
| Windows credential keywords | `password=`, `passwd=`, `pwd=`, `token=`, `api_key=`, `secret=`, `client_secret=` |

This table is a minimum. Provider patterns must be versioned and reviewed before execution.

Every token regex must include boundary handling for:

- beginning/end of line.
- quotes.
- whitespace.
- JSON delimiters.
- YAML delimiters.
- shell assignment delimiters.
- URL query delimiters.
- escaped newline and escaped quote contexts.
- concatenated string fragments.

Rules must avoid matching inside longer alphanumeric strings unless the token family explicitly permits it.

## 21. High-Entropy Policy

Minimum candidate lengths:

```text
BASE64_LIKE: 24 characters
HEX_LIKE: 32 characters
URL_SAFE_TOKEN: 24 characters
JWT_SEGMENT: parsed by JWT structure, not entropy alone
```

Entropy thresholds:

```text
BASE64_LIKE: Shannon entropy >= 4.5 bits/char
HEX_LIKE: Shannon entropy >= 3.0 bits/char
URL_SAFE_RANDOM_TOKEN: Shannon entropy >= 4.0 bits/char
```

Entropy hits must be combined with context scoring unless the token family is explicitly known.

Required context keywords:

```text
password, passwd, pwd, token, api_key, apikey, secret, client_secret, bearer, authorization, credential, private_key, access_key, refresh_token
```

Entropy thresholds and context keywords must be recorded in the scan configuration and output.

## 22. Decoded-Content Scan Requirements

The scanner must attempt bounded decoding for:

- Base64.
- Base64URL.
- hex.
- URL percent encoding.
- JSON escaped strings.
- common shell escaped strings.
- PowerShell backtick escapes.
- UTF-16LE text.
- UTF-16BE text.

Decoded content must be scanned with the same credential-pattern and entropy rules.

Every decoded hit must include:

- original file path.
- original offset or line where available.
- decoded buffer location.
- decoding layer.
- redacted decoded evidence.
- redacted original evidence.

If exact source line cannot be mapped, mark:

```text
LOCATION_APPROXIMATE
```

## 23. Multiline And Partial Secret Requirements

Scanner requirements must include multiline detection for:

- PEM private key blocks.
- OpenSSH private key blocks.
- certificate/key pairs.
- YAML block scalars.
- JSON escaped multiline strings.
- PowerShell here-strings.
- shell line continuations.
- C/C++ adjacent string literal concatenation.

Scanner requirements must also flag partial secret indicators:

- prefix-only tokens.
- suffix-only tokens.
- split string concatenation.
- line continuation fragments.
- suspicious adjacent fragments within 5 logical lines.
- token pieces separated by quotes, plus signs, backslashes, or PowerShell backticks.

`TEST_FIXTURE_CANDIDATE` is not a false positive and still requires manual review.

## 24. Archive Safety Requirements

The scanner must treat archives as hostile input.

Required default limits:

```text
MAX_DECOMPRESSED_BYTES: 2 GiB unless separately authorized
MAX_FILES: 250,000
MAX_SINGLE_FILE_SIZE: 256 MiB
MAX_NESTED_ARCHIVE_DEPTH: 3
MAX_DECODING_DEPTH: 3
MAX_COMPRESSION_RATIO: 100:1
MAX_PATH_LENGTH: explicit configured cap
MAX_SYMLINK_COUNT: explicit configured cap
MAX_EXTRACTION_TIME: explicit configured timeout
MAX_MEMORY_USE: explicit configured cap
```

Reject or block:

- absolute archive paths.
- `../` path traversal.
- symlinks escaping scan root.
- hardlinks escaping scan root.
- device files.
- named pipes.
- sparse files exceeding limit.
- nested archives beyond depth limit.
- encrypted or password-protected content without authorized password access.

Any limit hit must be reported as:

```text
ARCHIVE_SAFETY_BLOCKER
```

Encrypted or password-protected content must be classified as:

```text
ENCRYPTED_UNSCANNED_BLOCKER
```

Unsupported nested content must be classified as:

```text
BLOCKER_UNSUPPORTED_NESTED_CONTENT
```

Exceeding any limit prevents PASS unless separately reviewed and documented.

## 25. Safe Extraction / Streaming Boundary

Any future authorized scan must use safe isolated extraction or streaming archive inspection.

Extraction, if used, must occur only inside a temporary isolated scan root with:

- path traversal protection.
- symlink protection.
- hardlink protection.
- quota enforcement.
- least-privilege execution.
- deletion-after-evidence-capture rules.

This specification does not authorize extraction.

Streaming or bounded chunk scanning is required for files larger than 16 MiB.

Full-file memory loading is prohibited unless file size is below the configured threshold.

Binary string extraction must be streaming and capped.

## 26. Timeout Requirements

Timeouts are required for:

- per-file scan.
- per-archive scan.
- per-regex evaluation where the engine supports it.
- per-decoder operation.
- binary string extraction.
- whole-scan runtime.

Timeout events must be reported as:

```text
SCAN_TIMEOUT_BLOCKER
```

Timeout events prevent PASS unless separately reviewed.

## 27. File Classification And Entry Identity

File classification must use both extension and content sniffing/magic detection where feasible.

Extension-only classification is insufficient.

Archive entry identity must include:

- raw path.
- normalized path.
- archive entry index.
- file hash where available.
- duplicate/collision marker.

Duplicate paths, case collisions, Unicode-normalized path collisions, and repeated files must be reported.

Symlinks and hardlinks must be recorded as metadata entries. Link targets must not be followed unless explicitly allowed by scan policy.

## 28. Unicode And Control Character Handling

Text normalization requirements:

- detect UTF-8, UTF-16LE, and UTF-16BE where possible.
- normalize Unicode to NFC for scanning copy.
- preserve original bytes for evidence.
- flag zero-width/control characters in credential contexts.
- scan both normalized text and original text when feasible.

Zero-width or control-character credential bypass indicators must be reported as:

```text
UNICODE_CREDENTIAL_CONTEXT_REVIEW
```

## 29. Redaction HMAC Policy

Secret fingerprinting must use HMAC-SHA256 with a scan-run secret salt stored outside any public report.

Public report format:

```text
<kind>:<prefix 2 chars>...<suffix 2 chars>:<length>:<hmac_prefix_12>
```

For high-risk secrets, prefix/suffix may be reduced to 0 chars:

```text
<kind>:<redacted>:<length>:<hmac_prefix_12>
```

Raw hashes of secrets are prohibited in public artifacts.

Binary evidence snippets must be bounded:

```text
MAX_BINARY_CONTEXT_BEFORE: 32 bytes
MAX_BINARY_CONTEXT_AFTER: 32 bytes
RAW_SECRET_BYTES: PROHIBITED
OFFSET_REQUIRED_WHERE_AVAILABLE: YES
EXTRACTION_METHOD_REQUIRED: YES
```

## 30. Scan Artifact Access Control And Storage

Scan outputs must be classified by sensitivity.

Required access model:

```text
RAW_SCAN_OUTPUT: restricted operator-only
REDACTED_FINDINGS_REPORT: restricted security-review only
SUMMARY_REPORT: shareable only after redaction review
COMMAND_LOG: redacted before sharing
```

Scan output artifacts must not be committed to the repository unless explicitly authorized after redaction review.

Default storage:

```text
QUARANTINED_LOCAL_EVIDENCE_ONLY
```

Any commit, upload, or share action requires a separate Matt decision.

## 31. Command Log Redaction

Command logs must be redacted before final artifact creation.

The command log must not include:

- environment variable values.
- raw secrets.
- authentication headers.
- API keys.
- full private user paths unless required and redacted.

Before any report is accepted, a redaction validation pass must scan output artifacts for raw secret patterns and high-entropy values.

If the report contains unredacted secret material:

```text
FAIL
```

## 32. Operator Identity And Tool Integrity Metadata

Operator identity record must include:

- operator name or handle.
- host identifier.
- OS/environment.
- timestamp with timezone.
- command invocation.
- working directory.
- tool hash.
- output artifact hashes.
- manual review signature or approval note.

This does not prove identity. It is audit metadata only.

Tool identity must include:

- tool name.
- version.
- source path.
- executable/script hash.
- ruleset hash.
- dependency lockfile hash where applicable.
- command line.
- runtime version.

Missing tool integrity metadata prevents PASS.

## 33. Deterministic Reproducibility

The scan must be reproducible.

Required:

- immutable archive hash.
- immutable ruleset hash.
- tool hash.
- deterministic scan configuration.
- deterministic file traversal order.
- recorded timezone.
- recorded locale/encoding policy.
- recorded include/exclude policy.

Non-deterministic scan behavior must be recorded as:

```text
REVIEW_BLOCKER
```

## 34. Include / Exclude Policy

Default policy:

```text
INCLUDE_ALL_ARCHIVE_ENTRIES
```

Exclusion requires:

- path.
- rule_id.
- reason.
- reviewer.
- blocker/non-blocker status.
- residual-risk linkage.

Silent exclusion prevents PASS.

## 35. Allowlist Validation Schema

Allowlist entries must include:

- allowlist_id.
- exact path scope.
- exact rule_id scope.
- exact value fingerprint using HMAC.
- reason.
- expiry/review date.
- reviewer.
- justification why non-secret or accepted fixture.

Broad allowlists by directory, extension, or keyword are prohibited unless marked:

```text
REVIEW_BLOCKER
```

## 36. Severity Taxonomy

Required severity taxonomy:

```text
CRITICAL: private keys, live cloud/service credentials, auth tokens, database URLs with credentials
HIGH: high-confidence token patterns, JWTs, secret-like connection strings
MEDIUM: path metadata with username/machine/toolchain leakage, suspicious entropy with context
LOW: likely examples, non-sensitive paths, false-positive candidates
BLOCKER: unscanned/unreadable/unsupported content affecting coverage
```

Path metadata severity must be assigned as:

```text
HIGH: username, machine name, private repo paths, backup paths, build host identifiers
MEDIUM: generic toolchain paths
LOW: non-private common system paths
```

## 37. Secret Hit Triage Requirements

If `SECRET_HIT` is found, scan report must mark:

```text
CLEAN CLOSURE BLOCKED
```

and require a separate:

```text
SECRET_TRIAGE_AND_ROTATION_PLAN
```

The scan itself must not rotate or revoke secrets unless separately authorized.

Required triage fields:

- secret family.
- likely provider.
- exposure location.
- commit/archive context.
- whether value appears complete.
- recommended rotation/revocation action.
- owner decision required.

## 38. Gemini Redaction Boundary

Gemini review input must be redacted and minimized.

Forbidden in Gemini review input:

- raw secrets.
- full secret hashes.
- full private paths.
- complete usernames or machine names unless explicitly approved.
- raw archive contents.
- full binary strings.

Gemini review is advisory only and cannot receive unrestricted scan artifacts without separate Matt authorization.

## 39. Compliance Mapping Requirements

The scan lane must map evidence to:

- SOC 2 CC6 logical access controls.
- SOC 2 CC7 monitoring and incident handling.
- SOC 2 CC8 change management.
- ISO 27001 Annex A access control, logging, secure development, and incident management controls.

This mapping is informational only and does not claim compliance or certification.

## 40. Retention Policy Requirements

Retention policy is required before scan execution.

The policy must define:

- raw scan evidence retention period.
- redacted report retention period.
- deletion/quarantine decision owner.
- storage location.
- access list.
- destruction log requirement.

No deletion is authorized by this specification.

## 41. Least-Privilege And Network-Isolated Scan Boundary

Future scan execution must run least-privilege:

- no admin/root unless separately justified.
- no network access by default.
- read-only archive input.
- write-only isolated output directory.
- no execution of archive contents.
- no driver loading.
- no script execution from archive.

Any network-enabled review step, including external API review, requires separate explicit authorization and redacted/minimized inputs.

## 42. Zero-Hit Statement Rules

Zero-hit statements must be category-scoped and must include blocker context.

Required phrase:

```text
ZERO HITS IN SCANNED CONTENT ONLY - DOES NOT PROVE SECRET ABSENCE.
```

Zero hits with skipped files, unsupported files, encrypted files, unreadable files, timeout files, or unsupported mechanics cannot support clean closure.

## 43. Scanner Output Is Evidence, Not Authority

Scan output is evidence only.

It does not authorize:

```text
BUILD: NO
CLEANUP: NO
DELETE: NO
ARCHIVE REPLACEMENT: NO
RESIDUAL-RISK CLOSURE: NO
FALSIFIER CLOSURE: NO
M4 CLOSURE: NO
PERFECT CLOSURE: NO
GATED STATUS: NO
```

## 44. Post-Scan Disposition Schema

Post-scan disposition must be one of:

```text
ACCEPT_QUARANTINED_DIRTY_PRESERVATION_BACKUP
PREPARE_CLEAN_REPLACEMENT_ARCHIVE_PLAN
REOPEN_SCAN_FOR_MISSING_COVERAGE
TRIGGER_SECRET_TRIAGE_PLAN
```

No disposition authorizes deletion, cleanup, archive replacement, or history rewrite without a separate Matt decision.
## 45. Gemini Review Requirements

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

## 46. Next Required Matt Decision

Next required Matt decision:

```text
ACCEPT_SCRATCH_ARCHIVE_CONTENT_SECRET_SCAN_SPEC_PATCHED_RE_REVIEW
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
SCRATCH ARCHIVE CONTENT SECRET SCAN SPEC: PATCHED - READY FOR RE-REVIEW
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