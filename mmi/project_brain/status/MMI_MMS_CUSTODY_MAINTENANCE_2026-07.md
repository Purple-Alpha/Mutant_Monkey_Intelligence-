# MMI / MMS Custody Maintenance Ledger — 2026-07

## Authority and purpose

- Operator authority: Matt
- Maintenance start: 2026-07-13
- Repository: `/mnt/c/MMI`
- Maintenance posture: preservation and documentation only until every closure gate is satisfied
- Product feature work: frozen
- Reason: establish durable repository, account, backup, recovery, data-location, and agent-governance truth before further MMI or MMS development

This ledger records observed facts separately from inference. Historical records are not rewritten merely because their former operating roles have changed.

## Current authority map

| Role | Current authority |
|---|---|
| Matt | Sole approval authority |
| Codex | Disk-aware controller, documentation custodian, repository-state verifier, and bounded Git operator after explicit destination verification |
| Claude Code | Read-only design or bounded independent reviewer for an exact Matt-authorized task |
| Cursor | Bounded independent reviewer for an exact Matt-authorized task; PM and repository-control authority remain removed |
| Qwen | Local bounded read-only specialist for deterministic-prechecked drift checks, classification, extraction, and short target comparisons |
| Gemini and Grok | Parked external models; no current invocation, spend, or role until Matt explicitly reactivates one |

## Starting repository custody snapshot

Observed 2026-07-13 before maintenance writes:

```text
repository: /mnt/c/MMI
branch: mmi-phase2-commit
HEAD: bd25c5c7d9244686db31621b2ed17a8c0735ddcd
upstream: origin/mmi-phase2-commit
ahead/behind: +0/-0
origin: https://github.com/Purple-Alpha/Mutant_Monkey_Intelligence-.git
pre-existing worktree state:
 M .gitignore
?? evidence/
```

Remote branch tips verified read-only on 2026-07-13:

```text
bd25c5c7d9244686db31621b2ed17a8c0735ddcd refs/heads/mmi-phase2-commit
3df84024d91dbbb61f1910c8ee68333b1007b039 refs/heads/safety/queue-drift-cleanup-20260528
```

## Worktree classification

### `.gitignore`

- Status: `PRECISE_REPAIR_APPLIED / UNCOMMITTED / REVIEW_PENDING`
- Observed working-tree SHA-256 after repair: `FB8C6A737493338622BAA522FABE5A102C6F6B1D9E29AC285E7044CE3599C028`
- Observed HEAD payload SHA-256: `3F0BAEF58DEEFBED9340688E3EA3C9D1AF8C91D30F7A8295A54FF756E3812440`
- Original structural observation: complete line-ending conversion plus one substantive added rule, `.aider*`
- Operator decision: preserve the `.aider*` rule and undo the accidental whole-file line-ending conversion
- Action performed: restored the original mixed line-ending boundary byte-for-byte and retained only the added `.aider*` line
- Verification: `git diff --numstat -- .gitignore` reports `1 0`; `git diff -- .gitignore` shows only `.aider*`; `git diff --check` passes
- Required disposition: independent review before any commit

### `evidence/`

- Status: `INTENTIONALLY_UNTRACKED_QUARANTINE`
- Source identity: July 11 Windows boundary diagnostic capture
- File count: 6
- Exact payload bytes: 14,454
- Disk allocation observed by `du`: 20 KiB
- Content-secret cleanliness: `NOT_PROVEN`
- Local heuristic content scan: `NO_OBVIOUS_SECRET_PATTERN_FOUND / NOT_A_SECRET-SCAN_CERTIFICATION`
- Host-metadata boundary: Windows minifilter, volume, instance, process, and service diagnostics; opaque host-specific volume/instance identifiers are present
- Publication boundary: `PRIVATE_QUARANTINE / NOT_ELIGIBLE_FOR_GIT_OR_CLOUD_UPLOAD`
- Action performed: metadata and SHA-256 inventory only; payloads not edited
- Required disposition: independent content/boundary review before any deletion; do not commit or upload the raw payloads

Per-file hashes:

| Path | SHA-256 |
|---|---|
| `evidence/boundary_diag_20260711_123413/daemon_process.txt` | `BCF858DBD86DE2D7FA53A1D550D388012D1E1AA3BB6130BBD392EADF791288F3` |
| `evidence/boundary_diag_20260711_123413/fltmc_filters.txt` | `B8F3DDC5F1F14169B54BCE615DE7AFFB66126666DB19C78B42C3D0AE54E8FBA9` |
| `evidence/boundary_diag_20260711_123413/fltmc_instances.txt` | `5609517E2FAC1016E9853632E93C777490BA3BF9E3192E8875B8B27CB25CEBEF` |
| `evidence/boundary_diag_20260711_123413/fltmc_volumes.txt` | `2B82FCE09782ABD19AA13E1FFD73D54783332261366B4B5524DD856FE3A786BD` |
| `evidence/boundary_diag_20260711_123413/related_processes.txt` | `A3160FAC2952255306651393872D8C295F1E48FC0DE60A3143C39AEFD5CC2897` |
| `evidence/boundary_diag_20260711_123413/related_services.txt` | `4963A99FA4A98170CD23D6687E932F3C7BBF9E377C13705149940D83BA2FBDEC` |

## Phase-name custody map

The repository uses “Phase 1” for multiple unrelated scopes. These names are separated for maintenance:

| Canonical maintenance name | Meaning | Primary record |
|---|---|---|
| `MMI-PROJECT-P1` | MMI PM/bootstrap phase | `status/MMI_BOOTSTRAP_CLOSEOUT.md` |
| `MMI-PROJECT-P2` | MMI local command-center/build phase | `status/MMI_PHASE2_START.md` |
| `MMI-AGI-P1` | Three-run Tier-4 stability gate | `status/MMI_PHASE1_STABILITY_PASS_2026-07-02.md` |
| `MMI-M4-P1` | M4 static invariant suite | M4 evolution-gate records |
| `SOCIAL-ARCHITECT-P1` | Separate paused legacy project lane | paused task/history only |

`MMI-PROJECT-P1` output is present in the current tree. Its bootstrap payload appears in the current branch from root commit `b65abe2fc380f194966deb9d264260e3b82466e2`, whose commit message begins Phase 2; detailed incremental Phase 1 commit provenance is therefore not established by the current branch.

## Backup custody snapshot

- Tool: `rclone`
- Configured remote name: `matt:`
- Cold-storage path: `matt:mmi-cold-storage/archives/`
- Remote listing access on 2026-07-13: `PASS`
- Remote MMI archives observed: 2026-06-28 through 2026-07-05
- Newest remote archive observed before today's maintenance backup: `mmi_backup_20260705_221254.tar.gz`
- Newest documented restore-proven archive: `mmi_backup_20260701_110548.tar.gz`
- Restore status of newer archives: `NOT_PROVEN`
- Backup access status: `AVAILABLE`

Local archives verified against their sidecar hashes:

| Archive | SHA-256 | Sidecar match |
|---|---|---|
| `mmi/project_brain/backup/mmi_backup_20260703_221342.tar.gz` | `D284A1EF419803BFA94DC3B8EC2A9AC19397121E0B837F791FC260AF371BBBDF` | YES |
| `mmi/project_brain/backup/mmi_backup_20260705_221254.tar.gz` | `45BFE08B24CA8E1076CD8EE78B64B73887A2DB79FA370FE26F502B90012C7DE7` | YES |
| `mmi_boundary_scratch_BACKUP_20260706.tar.gz` | `90EDF9D9D2DF02407C5B51E77A1764CDE8154092C96FAA0350BC03F591A3C9E4` | YES |

The scratch archive's matching sidecar proves preservation identity only. July 7 control records confirm absolute Windows-path/build-residue leakage, while secret-content cleanliness remains `NOT_PROVEN`. It is not a clean archive and is not eligible for latest-good promotion.

Current maintenance backup created and verified 2026-07-13:

| Field | Value |
|---|---|
| Archive | `mmi/project_brain/backup/mmi_backup_20260713_092718.tar.gz` |
| Bytes | 8,247,595 |
| SHA-256 | `470B23F58343AE54D225B36C948D725C54110BEAD0E08BE9AFBB37A31CA3EC0C` |
| Backblaze path | `matt:mmi-cold-storage/archives/mmi_backup_20260713_092718.tar.gz` |
| Push status | PASS |
| Local/remote byte match | YES |
| Local/remote SHA-256 match | YES |
| Remote sidecar match | YES |
| Restore check | PASS AFTER PUSH — isolated scratch, errors `[]` |
| Latest-good promotion | NOT PROMOTED |
| Safe as restore reference | NO — recovery proof remains MNT-008 |
| Quarantined `evidence/` included | NO |
| Working `.gitignore` included | NO |

Post-push isolated recovery check:

| Field | Value |
|---|---|
| Restore scratch | `/tmp/mmi_restore_check_20260713_F8uWW7` |
| Extraction | PASS |
| Repository `--restore-check` | PASS |
| Errors | `[]` |
| Live tree overwritten | NO |
| Scratch removed | NO — cleanup not authorized |
| Recovery boundary | Standard allowlisted MMI control package only |

## Maintenance register

| ID | Maintenance item | Status | Closure requirement |
|---|---|---|---|
| MNT-001 | Create custody ledger | CREATED / REVIEW_PENDING | Independent review before acceptance |
| MNT-002 | Classify and preserve `.gitignore` and `evidence/` | CLASSIFIED / REVIEW_PENDING | `.gitignore` precisely repaired and review pending; evidence is private quarantine with a heuristic scan only and is ineligible for Git/cloud upload |
| MNT-003 | Identify exactly what constitutes MMS | IDENTITY_BOUNDARY_DEFINED / REVIEW_PENDING | MMI is the self-healing organism with Radar as MMI-Core; MMS is the distinct purple-team defense/assault cost-maximizer; daemon ownership remains unresolved |
| MNT-004 | Complete repository/data-location inventory | PROTECTED_MANIFEST_PREPARED / REVIEW_PENDING | Six unique loose-data roots are inventoried in `MMI_PROTECTED_LOOSE_DATA_BACKUP_MANIFEST_2026-07-13.md`; encryption, destination, M4 sensitive inclusion, and product custody remain unresolved |
| MNT-005 | Create and verify current cold backup | COMPLETE_PUSH_VERIFIED | Archive, sidecar, Backblaze bytes, remote hash, and push log agree; restore proof is MNT-008 |
| MNT-006 | Reconcile GitHub ownership and authentication | CANONICAL_IDENTITY_PROVEN | Purple-Alpha authenticated with ADMIN on the exact public origin; redundant-account disposition remains deferred |
| MNT-007 | Update stale agent-governance documents | CUSTODY_DEFECTS_PATCHED / INDEPENDENT_REVIEW_REQUIRED | Gemini and Grok are parked; Qwen is advisory drift-check only with deterministic packet limits; the revised custody index and Qwen framework require fresh review, and Claude/ChatGPT reconciliation remains open |
| MNT-008 | Prove recovery paths before deletion | PARTIAL_ALLOWLIST_RECOVERY_PROVEN | Current standard MMI archive restore-check PASS; quarantine and loose-data recovery remain unproven; no deletion authorized |
| MNT-009 | Independently audit maintenance result | FIRST_AUDIT_INVALID / NO_SPEND_REAUDIT_REQUIRED | Gemini's historical audit remains `F / Blocked`; when the maintenance target set is stable, Claude or Cursor may perform a new exact bounded audit with verified identity, prompt/output capture, hashes, and required remote evidence; Gemini and Grok remain parked |
| MNT-010 | Resume product work | BLOCKED | MNT-001 through MNT-009 closed and Matt explicitly lifts freeze |

## Current maintenance lane

```text
PRIMARY MODEL: Codex
SECONDARY REVIEW MODEL: Claude or Cursor, selected per exact bounded Matt-authorized task
LOCAL PRECHECK MODEL: Qwen for small deterministic-prechecked read-only packets only
EXECUTION OPERATOR: Codex for bounded documentation and authorized backup; Matt for approval gates
FORBIDDEN ACTIONS: build, test, runtime execution, cleanup, deletion, restore-over-live-tree, account closure, remote change, commit, push, installation
OWNERSHIP REASON: Codex has current disk access; Qwen provides local bounded prechecks; Claude and Cursor provide separated no-spend review when explicitly tasked; Gemini and Grok are parked; Matt is sole authority
```

## Journal entries

### 2026-07-13 — Maintenance opening

**Observed fact:** Local and remote current branch tips match. Historical safety branch remains remote. Backblaze is accessible. The worktree began dirty with `.gitignore` modified and `evidence/` untracked. MMS has no established repository identity.

**Inference:** Project history is substantially preserved, but custody, role, backup-quality, and naming ambiguity make continued product work unsafe.

**Operator authorization:** Matt authorized creation of the custody ledger and execution of the ten-item maintenance program.

**Action performed:** Read-only repository, branch, data-location, and backup inventory; created this ledger and the companion data-location inventory.

**Verified result:** Documentation records disk evidence without modifying the two pre-existing dirty areas.

**Non-claims:** No build, test, product execution, cleanup, deletion, restore, Git commit, Git push, remote change, account change, or product-completion claim.

### 2026-07-13 — Current cold mirror

**Observed fact:** The standard allowlisted backup set includes the MMI project brain and the two new maintenance records. It excludes the working `.gitignore` and quarantined `evidence/` directory.

**Inference:** Uploading the allowlisted control package is within the established cold-storage boundary. Uploading unreviewed host diagnostics would exceed the proven content boundary.

**Operator authorization:** Matt authorized creation and verification of a current cold backup as MNT-005.

**Action performed:** Ran `python3 scripts/mmi_cold_backup.py --backup-and-push` from `/mnt/c/MMI`.

**Verified result:** `mmi_backup_20260713_092718.tar.gz`, 8,247,595 bytes, SHA-256 `470B23F58343AE54D225B36C948D725C54110BEAD0E08BE9AFBB37A31CA3EC0C`; Backblaze push, byte comparison, remote SHA-256, and sidecar comparison all passed. The backup push log was updated by the authorized workflow.

**Non-claims:** No restore was run. The archive was not promoted to latest-good. The quarantined evidence payload and working `.gitignore` were not included. No commit or Git push occurred.

### 2026-07-13 — GitHub identity and governance reconciliation

**Observed fact:** GitHub CLI is authenticated as `Purple-Alpha`. The authenticated viewer has `ADMIN` permission on public repository `Purple-Alpha/Mutant_Monkey_Intelligence-`. Its default branch is `mmi-phase2-commit`; local fetch and push URLs name the same repository.

**Inference:** Purple-Alpha is the evidence-supported canonical owner of the current MMI repository. No Zebra-owned MMI repository is part of the current custody chain.

**Operator authorization:** Matt confirmed the public Purple-Alpha repository is the main repository and removed Cursor from the PM role.

**Action performed:** Performed read-only identity and permission checks. Updated current authority documents and added a supersession notice to the historical lane-routing record. The Phase 2 architecture record was left byte-for-byte unchanged after a formatting-preservation check.

**Verified result:** Current operating authority now names Matt as sole approver and Codex as disk-aware controller. Historical records remain identifiable as historical.

**Non-claims:** No login, logout, token change, account closure, remote change, commit, push, or permission mutation occurred. Redundant GitHub account closure is not authorized.

### 2026-07-13 — Isolated recovery proof

**Observed fact:** The current archive extracted into `/tmp/mmi_restore_check_20260713_F8uWW7`. The repository restore checker found every required file, parsed `tasks.json` as a JSON list, and successfully syntax-compiled its restore-critical Python files.

**Inference:** The standard allowlisted MMI control package has a currently demonstrated recovery path. This evidence does not extend to payloads excluded by the allowlist.

**Operator authorization:** Matt authorized proving recovery paths as MNT-008. The operation was bounded to an isolated temporary directory.

**Action performed:** Extracted `mmi_backup_20260713_092718.tar.gz` into a new `/tmp` directory and ran the repository `--restore-check` against that directory.

**Verified result:** `status: PASS`, `errors: []`; the live repository was not overwritten. The scratch directory was left intact because cleanup was not authorized.

**Non-claims:** No latest-good promotion occurred. Recovery of `.gitignore`, quarantined `evidence/`, MMS candidates, external MMI evidence, or deletion-sensitive directories is not proven. No deletion or cleanup is authorized.

### 2026-07-13 — Precise ignore-file repair and provisional product boundary

**Observed fact:** The working `.gitignore` contained one intended rule, `.aider*`, plus an accidental conversion of the existing mixed line endings. Disk evidence identifies Mutant Monkey Radar and the Threat Intelligence Daemon, but neither component names itself MMS.

**Inference:** Retaining only `.aider*` avoids unrelated formatting churn. The loose Threat Intelligence Daemon remains best treated as an unassigned intelligence input until Matt makes a separate custody decision.

**Operator authorization:** Matt authorized the precise `.gitignore` repair and defined MMI and MMS as distinguishing identities: MMI is the self-healing organism with Radar as MMI-Core; MMS is the purple-team defense and assault cost-maximizer.

**Action performed:** Restored every pre-existing `.gitignore` byte and retained one added LF-terminated `.aider*` rule. Patched the active scope with the operator-defined MMI/MMS boundary and a defensive, non-retaliatory definition of fracturing.

**Verified result:** The `.gitignore` diff is one insertion and zero deletions; `git diff --check` passes. Radar is classified as MMI-Core. No MMS repository or canonical root was created or inferred.

**Non-claims:** This does not settle ownership of the Threat Intelligence Daemon, accept the maintenance package, authorize product work, or authorize commit or push.

### 2026-07-13 — Gemini maintenance audit and Codex report card

**Observed fact:** Gemini CLI 0.50.0 returned a read-only maintenance audit after one denied helper-agent attempt and one direct-tools retry. It identified present-tense Cursor commands inside the superseded routing record. The audit stated that it used host-attested hashes but scored evidence discipline and artifact hash binding as 3.

**Inference:** The routing observation is a valid agent-parsing drift risk. The audit itself cannot close MNT-009 because its critical hash-binding scores conflict with the unsealed host-attestation law and because it did not substantively cover the full target set.

**Operator authorization:** Matt authorized Gemini step 3 under the strict audit laws, required zero self-grading of the returned audit, and assigned Codex to grade Gemini's review and document the grading method.

**Action performed:** Invoked Gemini in read-only plan mode using a hash-bound XML prompt; captured its exact returned Markdown; Codex independently recomputed the audit hash, checked the cited routing lines, graded the Gemini audit `F / Blocked`, and recorded strike 1 for the audit series. The complete legacy routing body was then enclosed in an explicit historical/non-authoritative boundary without deleting it.

**Verified result:** Gemini audit SHA-256 `F25B78C3DCD0135B28BD60DE55C2A40BF5BBD3B4B1B66CC0FE0CDC6B13B137D2`; prompt SHA-256 `C9604C1A28C9A66A440878A6D37362AF364CED7D3788FEA5997614D1D98767AB`. Report card path: `status/MMI_MMS_MAINTENANCE_GEMINI_AUDIT_REPORT_CARD_2026-07-13.md`. MNT-009 remains open for re-audit.

**Non-claims:** Gemini's finding does not accept the maintenance package. Codex's report card does not grade itself. No build, test, cleanup, commit, push, product execution, or maintenance closure occurred.

### 2026-07-13 — Specialized model-prompt custody discovery

**Observed fact:** The repository contains canonical Claude engineering and adversarial-spec frameworks, a canonical ChatGPT adversarial-research framework, a mandatory cross-model research-rigor protocol, and an older root Gemini scratch-audit authority packet. No canonical general Gemini audit framework or Qwen framework was found. The Claude and lane-scope documents still contain Cursor-era routing and self-review language that predates the current independent-grading laws.

**Inference:** The universal law packet alone is insufficient as a durable model-routing system. Existing specialized prompt assets must be inventoried, reconciled with current authority, and either reaffirmed, superseded, or archived before automated reuse. The old Gemini scratch packet must not be reused as a current general audit prompt.

**Operator authorization:** Matt identified that specialized model prompts existed and required their use to be considered during maintenance.

**Action performed:** Performed read-only prompt discovery and reviewed the complete Claude frameworks, ChatGPT framework, Gemini task-specific packet, and research-rigor protocol. No framework was rewritten or executed.

**Verified result:** Prompt custody is now an explicit MNT-007 blocker. Current known framework status is recorded in the data-location inventory.

**Non-claims:** No specialized framework is accepted as current merely because it exists. No Gemini re-audit, model invocation, build, test, commit, push, or product action was performed during this discovery step.

### 2026-07-13 — Prompt custody and Gemini/Qwen framework drafts

**Observed fact:** No current general Gemini audit framework or Qwen read-only framework existed. Existing specialized frameworks had no single custody index tying lifecycle, hashes, authority order, evidence modes, and review separation together.

**Inference:** A custody index and model-specific read-only wrappers are required before either model can be used consistently for accepted maintenance review.

**Operator authorization:** Matt authorized creation of the prompt custody index and draft Gemini and Qwen frameworks as documentation only, with no invocation, build, test, commit, or push.

**Action performed:** Created `lanes/MMI_MODEL_PROMPT_CUSTODY_INDEX_2026-07.md`, `lanes/MMI_GEMINI_AUDIT_PROMPT_FRAMEWORK_2026-07.md`, and `lanes/MMI_QWEN_READ_ONLY_CROSS_CHECK_PROMPT_FRAMEWORK_2026-07.md`. Added a maintenance authority notice and draft links to `lanes/README.md`.

**Verified result:** All three artifacts mark themselves `DRAFT`, `INDEPENDENT_REVIEW_REQUIRED`, non-executable, and non-self-grading. Exact hashes are recorded in the active task handoff and must be recomputed by the independent reviewer.

**Non-claims:** Mechanical verification by the producer is not an independent grade. The drafts are not active and may not be invoked for accepted work until independently reviewed and explicitly accepted by Matt.

### 2026-07-13 — Advisory second-eye prompt review and revision

**Observed fact:** Matt supplied a second-eye critique covering the custody index, Gemini framework, and Qwen framework. The pasted review did not identify its producing model or provide tool-transcript identity evidence. It used averaged percentage scores even though current project law requires non-averaging lowest-score grading; its own Gemini and Qwen critical-criterion tables contained scores of 2.

**Inference:** The review is not a valid activation grade, but its source-level observations can be preserved as advisory defect evidence. Under the project rubric, critical scores below 3 would be `F / Blocked` regardless of the reported percentages.

**Operator authorization:** Matt requested a second set of eyes for drift checking and supplied the returned critique for use in the documentation revision cycle.

**Action performed:** Applied supported findings: formal exception records, freshness/invalidation, same-level conflict handling, tamper/truncation rules, review-reuse limits, boundary cases, minimum evidence gates, deterministic decision mappings, canonical attack coverage, framework/prompt capture binding, Qwen read-only proof requirements, and disagreement severity. Rejected the claim that Qwen drift mode lacked a grading boundary because the draft already stated that `DRIFT_CHECK` may not grade the target.

**Verified result:** Revised drafts remain `DRAFT / INDEPENDENT_REVIEW_REQUIRED`. Their prior hashes are invalidated; new hashes must be supplied to a formal reviewer.

**Non-claims:** The unknown reviewer is not attributed to a model. The averaged scores are not accepted as project grades. Codex's revision is not self-graded. No model invocation, build, test, commit, push, or activation occurred.

### 2026-07-13 — Quarantined evidence content-boundary classification

**Observed fact:** The six July 11 diagnostic files are UTF-16LE Windows command outputs totaling 14,454 bytes. A local pattern scan found no known API-key prefix, private-key marker, credential label, email address, IPv4 address, Windows absolute-path marker, or Windows user-profile marker. Three long identifier-like values were present across the filter-instance and volume outputs, including one UUID-shaped value. Neither TruffleHog nor Gitleaks is installed.

**Inference:** The scan reduces the likelihood of an obvious text credential but cannot prove secret cleanliness. The filter, volume, instance, process, and service data expose host-specific defensive metadata and therefore remain unsuitable for public Git or cloud backup.

**Operator authorization:** Matt authorized maintenance classification and preservation of `.gitignore` and `evidence/` under MNT-002.

**Action performed:** Read file types, byte/line counts, and pattern-category counts without rewriting, transcoding, moving, uploading, deleting, or printing opaque values.

**Verified result:** `evidence/` remains intentionally untracked private quarantine. Raw payload hashes and bytes remain those recorded above. MNT-002 is classified but still requires independent review before closure.

**Non-claims:** This heuristic scan is not secret-scan certification. No evidence payload was committed, uploaded, deleted, cleaned, or modified. No scanner was installed. No build, test, execution, commit, or push occurred.

### 2026-07-13 — Bounded external-review availability checks

**Observed fact:** Local Qwen 14B produced no review within a bounded 300-second CPU-only request. Claude Code recognized the externally stored Anthropic API credential, but the first tool-disabled, no-persistence custody-index review was rejected before inference because the account credit balance was too low. Claude reported zero input tokens, zero output tokens, and USD 0.00 cost.

**Inference:** Neither attempt produced independent review evidence. Qwen remains optional for smaller bounded inputs; Claude remains available only after account funding and should be used sparingly under a per-request budget cap.

**Operator authorization:** Matt authorized continued maintenance work and sparing use of Claude as an independent reviewer.

**Action performed:** Attempted one raw local Qwen advisory review and one Claude review capped at USD 0.25 with all Claude tools disabled. Both attempts were stopped or rejected without a returned review.

**Verified result:** The three prompt-governance drafts remain `DRAFT / INDEPENDENT_REVIEW_REQUIRED`; MNT-007 and MNT-009 remain open.

**Non-claims:** No reviewer passed or failed the drafts. No credential value was copied into the repository or printed. No repository mutation by an external model, build, test, commit, or push occurred.

### 2026-07-13 — Deletion-sensitive directory boundary correction

**Observed fact:** `/mnt/c/_delete_after_mmi_audit_20260705` contains nine files. Six are readable ISO Base Media MP4 files beneath a CapCut temporary-export directory and total 102,936,955 bytes. The other three total 135,168 bytes, have mode `111`, and are `.parc` files beneath `.cache/AMD/DxcCache`; their contents remain unreadable.

**Inference:** The `.parc` paths identify generated AMD DirectX shader-cache artifacts, but unreadable contents are not verified. The directory is a mixed non-MMI holding location containing unrelated user media and must not be handled as an MMI cleanup or deletion target.

**Operator authorization:** Matt authorized completion of the repository/data-location inventory and required recovery proof before any deletion.

**Action performed:** Read filesystem metadata, aggregate byte counts, and MP4 container identification only. No media was played or content-reviewed.

**Verified result:** The previously unexplained unreadable items are metadata-classified. MNT-004 remains open for other loose-data and product-custody decisions, but this directory is removed from any presumed MMI deletion scope.

**Non-claims:** No file was read through a permission bypass, opened for playback, copied, hashed, changed, moved, deleted, cleaned, or backed up. No build, test, commit, or push occurred.

### 2026-07-13 — Loose M4 evidence preservation boundary

**Observed fact:** `/mnt/c/mmi_m4_evidence` contains 32 files totaling 18,240,594 bytes, including boundary, WFP, minifilter, fuzz, sandbox, falsifier, and tampered-policy artifacts dated July 4–5. No same-named payloads exist in the current repository tree, and none are members of the verified 2026-07-13 cold archive. Two 32-byte `.mmi_dev_custody_stub.key` files have different payloads. A category-only scan identified credential-shaped text in `boundary/tampered_policy.json`, secret-related labels in two files, Windows absolute-path markers in nine files, and IPv4-like values in six files.

**Inference:** The directory is unique loose M4 evidence at risk of loss. Credential-shaped data may be an intentional tampered-policy fixture, but that is not proven and does not make it safe to publish. The directory requires a private protected-evidence archive boundary separate from public Git and the ordinary allowlisted cold package.

**Operator authorization:** Matt authorized complete data-location inventory and recovery-first maintenance. No protected-evidence upload or archive creation was authorized by this inspection.

**Action performed:** Read filenames, metadata, file types, archive membership, equality of the two stub-key payloads, and pattern-category counts. No credential-shaped value or stub-key content was printed.

**Verified result:** MNT-004 now records a concrete preservation blocker rather than treating `/mnt/c/mmi_m4_evidence` as generic loose data.

**Non-claims:** No secret is classified as genuine or synthetic. No evidence was accepted, copied, archived, uploaded, committed, deleted, or changed. No build, test, execution, commit, or push occurred.

### 2026-07-13 — Operator-authorized CapCut temporary-folder removal

**Observed fact:** The CapCut temporary-export folder contained exactly six regular MP4 files totaling 102,936,955 bytes and no subdirectories or other entries. The adjacent AMD cache subtree contained three separate unreadable `.parc` files totaling 135,168 bytes.

**Inference:** Removing only the known CapCut temporary-export folder satisfies Matt's bounded cleanup decision without expanding authority to AMD caches or any other personal data.

**Operator authorization:** Matt explicitly authorized deletion of the known CapCut material and expressed uncertainty about the AMD caches. The authorization was therefore bounded to `/mnt/c/_delete_after_mmi_audit_20260705/.__capcut_export_temp_folder_1773534424__` only.

**Action performed:** Sent the exact CapCut folder to the Windows Recycle Bin using the Windows filesystem API. Two earlier attempts failed before deletion because of quoting and assembly-loading errors; source verification proved the folder remained after both failures. The final attempt loaded the required standard assembly, stopped on errors, and verified source absence.

**Verified result:** The CapCut source folder is absent. All three AMD cache files remain at their original paths with their original observed sizes. The Recycle Bin was not emptied.

**Non-claims:** Permanent erasure and Recycle Bin recovery were not tested. No AMD cache, MMI file, repository file outside maintenance documentation, personal education data, banking data, or other user data was deleted or moved. No build, test, commit, or push occurred.

### 2026-07-13 — Loose component identity and sensitivity classification

**Observed fact:** Radar contains source plus SQLite/log/report state and generated bytecode. The Threat Intelligence Daemon contains source, configuration, tests, a 1.2 MB log, and approximately 2.5 MB of collected watch data; it declares itself independent of NorthStar but does not declare MMI or MMS ownership. The adjacent test set imports that daemon. `mmi_holding` contains one “Mutant Monkey Inbox Shield” Blast Radius Controller adversarial-test contract. None of these loose payloads is present in the current cold archive.

**Inference:** Radar is MMI-Core by Matt's decision and needs a future canonical custody root. The daemon is a potentially shared intelligence-input component whose ownership cannot be inferred from disk. Inbox Shield is a distinct unassigned component and must not be silently absorbed into MMI or MMS. All are unique loose data at preservation risk.

**Operator authorization:** Matt authorized complete repository/data-location inventory and required ambiguity removal before further product progress.

**Action performed:** Read filenames, metadata, explicit identity statements, configuration key names, archive membership, and credential-pattern categories. No loose component was executed or imported.

**Verified result:** The inventory now distinguishes Radar, Threat Intelligence Daemon, its companion tests/data record, and Inbox Shield rather than grouping them under an assumed MMS identity. A heuristic scan found no known secret prefix or key file in these locations, but the daemon's collected data requires private review because it contains secret-related language and an email-like value.

**Non-claims:** Heuristic scanning does not prove secret cleanliness. No component was accepted, assigned, moved, copied, archived, uploaded, committed, deleted, built, tested, or executed.

### 2026-07-13 — Protected loose-data backup manifest

**Observed fact:** The six operator-named source roots currently contain 76 readable regular files totaling 22,252,812 bytes, with no symlinks. Only the plaintext `matt:` rclone remote is configured. The documented `matt-crypt:` remote is absent. GPG and OpenSSL are installed; no encryption recipient, key-recovery boundary, protected destination, or M4 sensitive-item inclusion decision is approved.

**Inference:** Unique loose data is at preservation risk, but packaging it through the normal plaintext MMI backup would violate the secret and encrypted-sync boundaries. A protected quarantine manifest is required before any archive or upload action.

**Operator authorization:** Matt explicitly authorized preparation of a protected-backup manifest for the six named source roots.

**Action performed:** Created `status/MMI_PROTECTED_LOOSE_DATA_BACKUP_MANIFEST_2026-07-13.md` with exact roots, counts, bytes, portable fingerprints, sensitivity classes, encryption requirements, execution permit fields, logical archive layout, and restore gates.

**Verified result:** The manifest covers all six requested roots and records an aggregate package fingerprint of `0822EEC339DC73587ED246439C4D29621EA78EFE1ED52489911353BBF3406404`. Execution remains blocked pending encryption, destination, and sensitive-inclusion decisions.

**Non-claims:** No archive, copy, encryption, key operation, cloud upload, restore, source deletion, build, test, commit, or push occurred.

### 2026-07-13 — Read-only GPG key-custody inventory

**Observed fact:** WSL has `/usr/bin/gpg`, but `GNUPGHOME` is unset, the GPG-configured default home does not exist, and no alternate WSL keyring file was found under the operator home. The Windows roaming GPG home and `gpg.exe` were also absent. Primary keys, encryption subkeys, local private-material files, revocation certificates, fingerprints, and expiry records all count as zero or not applicable.

**Inference:** No existing recoverable GPG encryption identity can protect the loose-data package. Tool availability alone is not a custody control. Backup execution remains blocked until an encryption identity or encrypted-sync design includes independent key recovery.

**Operator authorization:** Matt authorized a read-only GPG key-custody inventory limited to key counts, fingerprints, and expiry status.

**Action performed:** Checked configured/default GPG locations, alternate WSL keyring presence, Windows GPG-home presence, executable presence, private-material-file count, and revocation-certificate count. No key generation, listing of identities, export, signing, encryption, decryption, unlock, or passphrase operation occurred.

**Verified result:** `EXISTING_RECOVERABLE_ENCRYPTION_IDENTITY: NO`; fingerprints `NONE`; expiry status `NOT_APPLICABLE`.

**Non-claims:** No GPG home, keyring, key, certificate, archive, remote, credential, or configuration was created or modified. No backup, upload, restore, commit, or push occurred.

### 2026-07-13 — GPG encryption-identity and recovery-custody plan

**Observed fact:** No existing GPG identity or recovery material exists. GnuPG 2.4.4 is installed. Official GnuPG documentation treats secret-key export as security-sensitive, supports distinct key capabilities and expiries, creates a revocation certificate during key generation, and requires importing that certificate to perform revocation.

**Inference:** Protected backup cannot safely begin with key generation alone. Passphrase separation, two independent secret-key recovery copies, revocation-certificate custody, and a recovery test from the second copy must be specified and proven first.

**Operator authorization:** Matt authorized preparation of a documentation-only encryption identity and recovery-custody plan defining key creation, passphrase handling, revocation custody, independent recovery copy, and recovery testing before archive creation.

**Action performed:** Created `status/MMI_GPG_BACKUP_KEY_AND_RECOVERY_CUSTODY_PLAN_2026-07-13.md`. The plan defines a dedicated certification-only Ed25519 primary identity, a cv25519 encryption subkey, separate expiries, local pinentry-only passphrase handling, two physically independent recovery media, separate passphrase recovery paths, revocation custody, a Recovery Copy B test, public-key-only operating posture, rotation, compromise handling, phase permits, and fail-closed acceptance gates.

**Verified result:** Key generation, recovery-copy creation, recovery testing, archive creation, and upload are separated into independently authorized phases. Protected archive creation remains blocked until the recovery test passes.

**Non-claims:** No key, GPG home, passphrase, revocation certificate, export, recovery copy, fixture, archive, encryption, upload, restore, commit, or push was created or performed.

### 2026-07-13 — Audit-model cost routing and bounded Qwen doctrine

**Observed fact:** Matt directed that Gemini no longer be used after prior credits were consumed correcting Gemini mistakes. Claude returned a useful but freeform advisory review of the prompt-custody draft set; Codex graded the supplied excerpt `F / Blocked` because the prompt, capture, model-identity, completeness, and review-artifact hash gates were not satisfied. Matt identified Qwen's best role as a bounded specialist for small local prechecks rather than a general authority-heavy reviewer.

**Inference:** No Grok spend is needed during local deterministic prechecks or documentation repair. Grok becomes necessary only if a formal independent maintenance audit or review-artifact grade remains required after the exact target set is stable and no already-authorized no-additional-cost reviewer can satisfy project-law gates.

**Operator authorization:** Matt authorized a documentation-only patch assigning Grok as the current independent auditor, parking Gemini, preserving historical evidence, correcting the Qwen placeholder, and recording Claude's findings as advisory evidence only.

**Action performed:** Updated current model-role routing, parked the Gemini general-audit draft without deleting or rewriting it, added bounded-use doctrine to the Qwen draft, and corrected Qwen's machine-readable populated-prompt placeholder. Recorded a reminder that the current Claude access key expires on 2026-07-20 and must be renewed before later Claude use; no credential value is stored here.

**Verified result:** Current governance distinguishes Qwen's no-spend local specialist role from Grok's cost-gated independent-audit role. Claude's review remains advisory and does not activate a framework or close MNT-007/MNT-009.

**Non-claims:** This patch does not invoke Qwen, Grok, Gemini, or Claude; authorize model spend; accept a prompt framework; grade the revised artifacts; close maintenance; or authorize build, test, execution, cleanup, commit, push, or deletion.

### 2026-07-13 — No-spend team routing and Cursor custody review

**Observed fact:** Cursor completed the one-file, hash-bound review task without changing either target. The review artifact is `status/MMI_CURSOR_QWEN_CUSTODY_REVIEW_2026-07-13.md`, SHA-256 `E82EDEFBA2318B75781022DA15385C93DB09694FDA31AD0948EE31F99B4A82AE`. Codex independently graded it `F / Blocked` because Cursor version/model identity and Audit Law A8 remote-head evidence were not verified, while confirming that its core target findings were materially useful. Matt then set the current team to Codex, Claude, Cursor, and local Qwen and parked both Gemini and Grok until explicit later reactivation.

**Inference:** The review's acceptance failure does not erase source-grounded findings. Those findings support a bounded documentation correction, while the current team can continue maintenance without paid Gemini or Grok use.

**Operator authorization:** Matt authorized the documentation-only maintenance patch and explicitly did not authorize build work.

**Action performed:** Marked stale Gemini trial language historical, routed bounded independent review to Claude or Cursor per exact task, parked both paid external models, constrained Qwen to advisory drift-check work, and patched the reviewed custody defects.

**Verified result:** Current role documents no longer require Gemini or Grok. The Cursor review remains immutable advisory evidence at its recorded hash and is not represented as accepted.

**Non-claims:** No model was invoked, no spend occurred, and no build, test, product execution, install, cleanup, delete, commit, push, remote query, or maintenance closure was authorized or performed by this patch.

## Closure rule

Maintenance closure requires a clean or fully classified worktree, current verified backup and recovery evidence, canonical GitHub custody, updated controlling governance, an independently reviewed ledger, and explicit Matt authorization to resume product work.
