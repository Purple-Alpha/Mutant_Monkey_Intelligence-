# MMI GPG Backup-Key and Recovery-Custody Plan — 2026-07-13

## Status and authority

```text
PLAN_STATUS: DRAFT_FOR_OPERATOR_REVIEW
DOCUMENTATION_ONLY: YES
KEY_GENERATION_AUTHORIZED: NO
GPG_HOME_CREATION_AUTHORIZED: NO
PASSPHRASE_CREATION_AUTHORIZED: NO
SECRET_KEY_EXPORT_AUTHORIZED: NO
RECOVERY_MEDIA_WRITE_AUTHORIZED: NO
RECOVERY_TEST_AUTHORIZED: NO
PROTECTED_ARCHIVE_AUTHORIZED: NO
CLOUD_UPLOAD_AUTHORIZED: NO
```

- Operator authority: Matt
- Prepared by: Codex, disk-aware documentation custodian
- Prepared at: `2026-07-13T12:34:53-07:00`
- Repository: `/mnt/c/MMI`
- Branch: `mmi-phase2-commit`
- HEAD at preparation: `bd25c5c7d9244686db31621b2ed17a8c0735ddcd`
- Installed GPG observed: GnuPG `2.4.4`, libgcrypt `1.10.3`
- Existing GPG identity: none
- Target manifest: `status/MMI_PROTECTED_LOOSE_DATA_BACKUP_MANIFEST_2026-07-13.md`

This plan defines how a future dedicated encryption identity could be created, recovered, and proven before any protected loose-data archive is created. It does not contain a passphrase, private key, executable command packet, or authority to perform any step.

## Controlling boundaries

- `status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md`
- `architecture/MMI_BACKUP_COLD_STORAGE_SPEC.md`
- `architecture/MMI_LOCAL_CLOUD_POLICY.md`
- `opsec/BACKUP_PROTECTED_PATHS.md`
- `status/MMI_PROTECTED_LOOSE_DATA_BACKUP_MANIFEST_2026-07-13.md`
- `status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_2026-07-13.md`
- `status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_ACCEPTANCE_2026-07-13.md`

Official GnuPG references:

- [OpenPGP key management](https://gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html)
- [Operational GPG commands](https://gnupg.org/documentation/manuals/gnupg/Operational-GPG-Commands.html)
- [GPG manual](https://gnupg.org/documentation/manuals/gnupg26/gpg.1.html)

GnuPG documents that key generation creates a revocation certificate, that revocation takes effect only after the certificate is imported, and that secret-key export is a security-sensitive operation. Those properties drive the custody gates below.

## Identity design

The proposed identity is dedicated to MMI protected-backup encryption only.

```text
IDENTITY_LABEL: MMI Protected Backup 2026
PERSONAL_EMAIL_IN_USER_ID: NO
PRIMARY_KEY_PURPOSE: CERTIFICATION ONLY
PRIMARY_KEY_ALGORITHM: ED25519
PRIMARY_KEY_EXPIRY: 5 YEARS FROM CREATION
SUBKEY_PURPOSE: ENCRYPTION ONLY
ENCRYPTION_SUBKEY_ALGORITHM: CV25519
ENCRYPTION_SUBKEY_EXPIRY: 2 YEARS FROM CREATION
SIGNING_USE: PROHIBITED
AUTHENTICATION_USE: PROHIBITED
GIT_SIGNING_USE: PROHIBITED
EMAIL_USE: PROHIBITED
PUBLIC_KEYSERVER_UPLOAD: PROHIBITED UNLESS SEPARATELY AUTHORIZED
```

The certification-only primary key permits future encryption-subkey rotation without turning this identity into a general signing identity. The encryption subkey performs recipient encryption. Exact algorithms, capabilities, creation times, expiry times, and full fingerprints must be captured from machine-readable GPG output immediately after generation.

Expiry does not replace revocation or recovery. Old private encryption subkeys must be retained for as long as any archive encrypted to them must remain recoverable.

## Role separation

| Role | Allowed responsibility | Forbidden responsibility |
|---|---|---|
| Matt | Approve each phase; create and retain passphrase; control physical recovery media; authorize recovery test | Paste passphrase or secret material into chat, repository, terminal arguments, or documentation |
| Codex | Prepare command packet after permit; verify public fingerprints, hashes, counts, file boundaries, and recorded results | Receive, display, store, infer, or grade passphrase/secret-key content |
| Independent reviewer | Review public-safe custody evidence and recovery-test results | Access passphrase or secret-key payload; self-approve its review |
| GPG/pinentry | Perform future key and cryptographic operations after permit | Persist passphrase in project files, environment variables, shell arguments, or logs |

No model, prompt, transcript, repository file, environment file, command-line argument, or cloud object may contain the passphrase or unencrypted secret-key material.

## Phase separation and permits

Authority never carries from one phase to another.

| Phase | Purpose | Writes or sensitive operations | Required result before next phase |
|---|---|---|---|
| GPG-P0 | Review and accept this plan | Documentation only | Matt accepts exact plan hash |
| GPG-P1 | Create dedicated identity in an isolated GPG home | Creates keyring, private material, and revocation certificate | Fingerprints, algorithms, capabilities, and expiry verified |
| GPG-P2 | Create two independent recovery copies | Exports public/secret material and copies revocation certificate | Both media hashes match; passphrase stored separately |
| GPG-P3 | Prove independent recovery | Imports from Recovery Copy B into a new isolated GPG home and decrypts a harmless fixture | Exact fingerprint and plaintext-hash match |
| GPG-P4 | Establish public-key-only encryption environment | Imports public key only into future backup environment | No secret material present; encryption recipient verified |
| GPG-P5 | Create protected archive | Creates plaintext staging only within approved boundary and encrypts to exact subkey fingerprint | Ciphertext hash/bytes recorded; plaintext disposition separately controlled |
| GPG-P6 | Upload ciphertext and verify remote | Uses separately approved encrypted destination | Remote bytes/hash match; no plaintext remote object |
| GPG-P7 | Isolated protected-archive restore | Decrypts and verifies full internal manifest outside live roots | Full restore evidence passes |
| GPG-P8 | Recurring custody verification | Reads recovery media and, on the scheduled alternating cycle, performs an isolated recovery test | Media integrity, compatibility, and recovery evidence remain current |

No protected archive may be created before GPG-P3 passes. No source deletion may be authorized merely because any GPG phase passes.

## GPG-P1 — Key-creation requirements

Key creation must occur only after a permit names:

- the exact isolated GPG home path outside the repository;
- its required owner-only directory and file permissions;
- the identity label;
- primary and subkey algorithms, purposes, and expiries from this plan;
- the approved pinentry method;
- the expected public outputs and forbidden secret outputs;
- the execution operator;
- the evidence destination;
- the cleanup boundary, which remains separately authorized.

Creation rules:

1. Use an isolated GPG home that did not previously exist.
2. Do not use the default personal GPG home.
3. Do not include Matt's personal email address in the key user ID.
4. Create one certification-only Ed25519 primary key expiring five years from creation.
5. Add one cv25519 encryption-only subkey expiring two years from creation.
6. Enter the passphrase only through local pinentry.
7. Disable network/keyserver publication during creation and verification.
8. Capture only public-safe machine-readable evidence: full fingerprints, algorithms, capabilities, creation/expiry timestamps, and revocation-certificate presence.
9. Confirm the encryption subkey is current, encryption-capable, and bound to the expected primary fingerprint.
10. Stop on any unexpected extra key, user ID, subkey, missing expiry, missing revocation certificate, permission mismatch, or tool error.

The future reviewed command packet must identify keys by full fingerprint, never by short key ID, email address, or ambiguous name.

## Passphrase custody

### Generation standard

- Create one unique passphrase used only for this backup identity.
- Generate it locally using a trusted offline random-word or password-generator method.
- Use at least seven words selected independently and uniformly from a documented list containing at least 7,776 entries (approximately 90 bits of entropy), or a locally generated value providing at least 90 bits of entropy by a documented calculation.
- Record only the generation method, word-list identifier and size or entropy calculation, and pass/fail result; never record the selected words or generated value.
- Do not derive it from project names, personal facts, reused passwords, quotations, dates, or keyboard patterns.
- Do not let Codex, Claude, Gemini, Grok, Qwen, Aider, a browser chat, or a repository script generate or receive the final passphrase.

### Entry and handling

- Enter it only into local GPG pinentry prompts.
- Never pass it through command-line arguments, environment variables, `.env` files, shell history, clipboard-sync services, screenshots, terminal transcripts, or repository files.
- Do not echo it for verification.
- If a prompt or command would expose it outside pinentry, stop the phase.

### Recovery copies of the passphrase

Maintain two independent passphrase recovery paths:

1. one sealed paper record stored separately from Recovery Media A; and
2. either a second sealed paper record or one entry in a reputable zero-knowledge, end-to-end-encrypted password manager with strong MFA and a separately tested account-recovery path, stored separately from Recovery Media B.

Password-manager selection must document, without storing secrets, the encryption posture, MFA method, account-recovery test date, and the fact that neither the password-manager credentials nor its MFA recovery material depend solely on either GPG recovery medium. A synced password manager is not automatically prohibited, but ordinary provider access, account takeover, or provider-side plaintext recovery must not expose the stored passphrase.

Neither recovery medium may be stored together with its corresponding passphrase copy. The custody record may document locations using operator-defined labels such as `LOCATION-A` and `LOCATION-B`; it must not publish home addresses, banking locations, safe combinations, password-manager recovery material, or the passphrase.

Passphrase recovery remains `UNPROVEN` until GPG-P3 successfully uses one approved recovery copy without relying on the original creation session.

## Revocation-certificate custody

The revocation certificate cannot decrypt archives, but possession may allow an actor to revoke the public identity. Treat it as integrity-sensitive recovery material.

Required custody:

- verify that the certificate names the exact full primary fingerprint;
- calculate its SHA-256 without publishing its contents;
- place a copy on Recovery Media A and Recovery Media B;
- retain one additional sealed paper or offline digital copy if operationally practical;
- never place it in public Git, chat, an unencrypted cloud object, or the archive it governs;
- record only its SHA-256, byte count, and custody labels in the public-safe ledger;
- test only that the certificate is present and parseable during GPG-P3;
- do not import it into the active keyring during a normal recovery test, because import performs the actual revocation action.

Revocation use requires its own incident authorization. Suspected private-key or passphrase compromise immediately blocks new archive encryption to that identity.

## Independent recovery copies

Two physically and administratively independent recovery copies are mandatory.

### Recovery Media A

Contains:

- passphrase-protected full secret-key export;
- public-key export;
- revocation certificate;
- public-safe custody metadata containing fingerprints, algorithms, expiry, byte counts, and SHA-256 values;
- a plain-text recovery instruction that contains no passphrase.

Store offline in `LOCATION-A`, outside the Mini PC and outside Backblaze.

### Recovery Media B

Contains the same logical payload, independently copied and hash-verified. Store offline in `LOCATION-B`, physically separate from the Mini PC and Recovery Media A.

### Independence rules

- Two folders or partitions on one physical disk do not count as two copies.
- Two copies in the same room do not establish disaster independence.
- Backblaze and the Mini PC do not constitute the two private-key recovery copies.
- A password-manager entry without the secret-key export is not a key recovery copy.
- A secret-key export without the passphrase is not a proven recovery path.
- Cloud storage of secret-key exports is prohibited unless separately approved with an additional encryption and account-recovery layer.

The secret-key export is a security risk even when passphrase protected; official GnuPG documentation warns against insecure secret-key export channels. No temporary plaintext or unprotected export may remain on internal storage after the separately authorized custody phase closes.

### Initial and recurring media verification

- GPG-P2 must independently read and SHA-256 verify every governed file on both Recovery Media A and Recovery Media B after the final copy operation; source-side hashes alone are insufficient.
- At least once every 12 months, and after any storage incident, media replacement, custody-location change, or material GnuPG compatibility change, verify every governed file on both recovery media against the custody ledger.
- Perform a full isolated fixture-recovery test at least once every 12 months, alternating the tested medium between A and B. A material hash mismatch, unreadable file, fingerprint mismatch, or failed recovery immediately blocks new archive creation.
- Media verification does not authorize repair, overwrite, reformatting, disposal, or replacement. Those actions require a separately reviewed preservation permit.

### Long-term recovery compatibility

- Record the exact GnuPG version, operating-system family, secret-key export format, algorithms, and import/decrypt options proven during each recovery test.
- Use only an export format that the designated recovery environment has successfully imported. A protected export format requiring GnuPG 2.4 or later must not be the sole recovery representation unless every designated recovery environment is compatibility-proven.
- Preserve public-safe recovery instructions and the checksums or acquisition references needed to recreate a compatible recovery toolchain; do not store executable installers on recovery media unless separately reviewed and hash-governed.
- Before a major GnuPG upgrade, algorithm deprecation, operating-system retirement, or recovery-tool migration, run a separately authorized compatibility review and recovery test. Preserve all historical encryption subkeys while any dependent archive remains retained.

## GPG-P3 — Mandatory recovery test

The recovery test must occur before any protected archive is created.

### Isolation

- Use a brand-new isolated temporary GPG home outside the repository and all live source roots.
- Do not use the creation GPG home or default personal home.
- Use Recovery Media B, not the working keyring or Recovery Media A.
- Keep networking and keyserver access disabled.
- Do not touch the six protected source roots.

### Test fixture

Before destroying or removing any creation environment, prepare one harmless, non-secret fixture with:

- fixed documented UTF-8 content;
- recorded byte count;
- recorded SHA-256;
- no project source, credential, personal data, or operational configuration.

Encrypt the fixture to the exact encryption-subkey fingerprint using public material only.

### Recovery procedure

1. Verify Recovery Media B file hashes against the custody record.
2. Import the public and passphrase-protected secret-key export into the isolated recovery home.
3. Enter the passphrase through pinentry only.
4. Recompute and compare the full primary and encryption-subkey fingerprints.
5. Confirm algorithms, capabilities, creation times, and expiry times match GPG-P1 evidence.
6. Confirm the revocation certificate is present and hash-matching without importing it.
7. Decrypt the harmless fixture into the isolated scratch boundary.
8. Compare recovered plaintext byte count and SHA-256 to the pre-encryption values.
9. List secret-key availability using machine-readable output without printing user IDs or sensitive material.
10. Record exact commands, timestamps, tool version, operator, paths, hashes, and pass/fail results with passphrase and secret material redacted.
11. Record which recovery medium was tested so the next annual GPG-P8 test uses the alternate medium.

### Pass criteria

```text
RECOVERY_MEDIA_HASHES: MATCH
PRIMARY_FINGERPRINT: MATCH
ENCRYPTION_SUBKEY_FINGERPRINT: MATCH
ENCRYPTION_CAPABILITY: PRESENT
PRIVATE_DECRYPTION_MATERIAL: AVAILABLE
EXPIRY_STATUS: CURRENT
REVOCATION_CERTIFICATE_HASH: MATCH
FIXTURE_DECRYPTION: PASS
FIXTURE_PLAINTEXT_SHA256: MATCH
LIVE_SOURCE_CONTACT: NONE
SECRET_DISCLOSURE: NONE
```

Any mismatch or missing evidence yields:

```text
GPG_RECOVERY_CUSTODY: FAIL_BLOCKED
PROTECTED_ARCHIVE_CREATION: BLOCKED
```

## Public-key-only operating posture

After GPG-P3 passes and only under a separate permit:

- install only the public key in the backup-encryption environment;
- verify that no secret-key file exists in that environment;
- encrypt only to the exact full encryption-subkey fingerprint;
- retain the primary and encryption-subkey secret material only on the two recovery media;
- preserve all retired encryption subkeys needed for historical archives;
- do not delete the creation GPG home until Recovery Media A and B and the recovery test have passed, and cleanup is separately authorized.

This posture allows future archive encryption without keeping decryption material on the working host.

## Rotation and expiry

- Review primary and encryption-subkey expiry every quarter.
- Open a rotation lane no later than 90 days before encryption-subkey expiry.
- Stop creating archives to an expired or revoked subkey.
- Add a replacement encryption subkey only through the offline primary-key custody path.
- Preserve the old private subkey while any archive encrypted to it remains retained.
- Record the recipient fingerprint used by every archive.
- Do not re-encrypt or delete historical archives merely because a key expires; handle migration under a separate preservation permit.

## Succession and operator-unavailability decision gate

Before GPG-P1, Matt must select and sign one of these mutually exclusive custody postures for the exact plan hash:

```text
SUCCESSION_POSTURE: TRUSTED_SUCCESSOR | GOVERNED_PROFESSIONAL_ESCROW | SOLE_OPERATOR_RISK_ACCEPTED
```

- `TRUSTED_SUCCESSOR` requires a separate, independently reviewed custody packet defining the authorized person, activation conditions, identity verification, access separation, revocation/replacement, rehearsal cadence, and evidence boundaries. This plan does not name or authorize a successor.
- `GOVERNED_PROFESSIONAL_ESCROW` requires a separate legal/custody review of the provider or professional arrangement, jurisdiction, access conditions, provider continuity, confidentiality, account recovery, termination/export, rehearsal, and replacement. Paying for storage or naming a professional does not by itself establish escrow fitness.
- `SOLE_OPERATOR_RISK_ACCEPTED` records that Matt intentionally accepts permanent archive unrecoverability during death, incapacity, prolonged unavailability, or loss of personal recovery knowledge. It is a residual-risk acceptance, not evidence that recovery is adequate.
- An unset, ambiguous, or unsigned succession posture blocks GPG-P1. No model or operator may sign the posture for Matt.

### Succession decision matrix

This matrix turns the posture decision into a repeatable evidence exercise. It does not average away a critical weakness.

Score each criterion from 0 to 3:

```text
3 = CLEAN: control is explicit, testable, and supported by evidence
2 = ADEQUATE: viable but has a material limitation or recurring operator burden
1 = WEAK: substantial ambiguity, dependency, or untested assumption
0 = FAILED: absent, contradicted, or unable to meet the recovery objective
```

Critical criteria are marked `YES`. Any critical criterion below 3 makes the option `F_BLOCKED`, regardless of totals. Among options with all critical criteria at 3, use the lowest non-critical score first; use the weighted total only as a tie-breaker. Unknown evidence is not a 3.

| Criterion | Critical | Weight | Sole operator | Trusted successor after accepted custody packet | Professional escrow after accepted legal/custody review |
|---|---:|---:|---:|---:|---:|
| Authorized recovery during Matt's incapacity | YES | 25 | 0 | 3 | 3 |
| Confidentiality and separation of key/passphrase access | YES | 25 | 3 | 3 | 3 |
| Identity, activation, and anti-impersonation controls | YES | 15 | 0 | 3 | 3 |
| Recovery path can be rehearsed without exposing production secrets | YES | 10 | 2 | 3 | 3 |
| Independence from one person, device, account, or provider | NO | 10 | 0 | 3 | 2 |
| Revocation, replacement, and exit control | NO | 5 | 3 | 2 | 2 |
| Ongoing administrative and financial burden | NO | 5 | 3 | 2 | 1 |
| Long-term availability and continuity | NO | 5 | 0 | 2 | 2 |

Weighted tie-break calculation:

```text
WEIGHTED_SCORE_PERCENT = sum(score × weight) / 3
```

The percentage is advisory and is calculated only after every critical criterion scores 3. It never rescues a blocked option.

Provisional design result, assuming the named prerequisite packet/review is later completed exactly as stated:

| Option | Critical gate | Lowest score | Weighted tie-break | Provisional result |
|---|---|---:|---:|---|
| Sole operator | FAIL — incapacity recovery and activation controls score 0 | 0 | NOT_APPLICABLE | `F_BLOCKED` when continued authorized recovery is an objective |
| Trusted successor | PASS only after an accepted successor-custody packet and rehearsal | 2 | 95.0% | `B / RECOMMENDED_DEFAULT` if a suitable trusted person exists |
| Governed professional escrow | PASS only after accepted legal/custody review and rehearsal | 1 | 90.0% | `C / FALLBACK` when no suitable trusted successor exists |

Decision rule:

1. If the archives should remain recoverable during Matt's incapacity and a suitable trusted person can satisfy the critical controls, the matrix recommends `TRUSTED_SUCCESSOR`.
2. If continuity is required but no suitable trusted person can satisfy those controls, evaluate `GOVERNED_PROFESSIONAL_ESCROW`; do not select a provider until its evidence changes every critical score to 3.
3. Select `SOLE_OPERATOR_RISK_ACCEPTED` only when permanent unrecoverability during Matt's unavailability is the intended outcome, not merely because it is simpler.
4. Matt records the objective and signs the matrix result; Matt does not need to override a higher-scoring eligible option without recording the reason.

Required decision record:

```text
RECOVERY_DURING_MATT_UNAVAILABILITY_REQUIRED: YES | NO
OPTIONS_SCORED_AT:
EVIDENCE_REFERENCES:
CRITICAL_GATE_RESULT:
LOWEST_SCORE:
WEIGHTED_TIE_BREAK_PERCENT:
MATRIX_RECOMMENDATION:
MATT_SELECTED_POSTURE:
VARIANCE_REASON_IF_NOT_RECOMMENDED:
MATT_ACCEPTANCE_DATE:
```

Current operator direction:

```text
RECOVERY_DURING_MATT_UNAVAILABILITY_REQUIRED: YES
OPTIONS_SCORED_AT: 2026-07-13
EVIDENCE_REFERENCES: SUCCESSION DECISION MATRIX IN THIS PLAN
CRITICAL_GATE_RESULT: PENDING — SUCCESSOR-CUSTODY PACKET AND REHEARSAL NOT YET ESTABLISHED
LOWEST_SCORE: 2 — PROVISIONAL DESIGN SCORE ONLY
WEIGHTED_TIE_BREAK_PERCENT: 95.0%
MATRIX_RECOMMENDATION: TRUSTED_SUCCESSOR
MATT_SELECTED_POSTURE: TRUSTED_SUCCESSOR
VARIANCE_REASON_IF_NOT_RECOMMENDED: NOT_APPLICABLE
MATT_ACCEPTANCE_DATE: 2026-07-13
```

This selection establishes design direction only. It does not name a successor, grant access, establish legal authority, satisfy any critical gate, or authorize GPG-P1. The trusted-successor option remains `PENDING` until its separate custody packet and rehearsal evidence receive independent review and Matt acceptance.

### Accepted trusted-successor design binding

Matt accepted the trusted-successor custody specification as a documentation-only design framework:

```text
ACCEPTED_SPECIFICATION_PATH: status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_2026-07-13.md
ACCEPTED_SPECIFICATION_SHA256: 2971ba7563027e15ca5ca2639394da502776a785be1c17906365c4ac75d7e38a
CLAUDE_REVIEW_MESSAGE_UUID: 0eb041b9-a4e0-4e3c-bd2c-e232dea4ed8b
CLAUDE_REVIEW_SHA256: 8a9a2c57dcfac81f5ea3977361c29abadb9dc0b468f9877e9f89f3523a381da2
CLAUDE_TARGET_GRADE: A
CODEX_REVIEW_ARTIFACT_GRADE: A
MATT_ACCEPTANCE_SCOPE: DOCUMENTATION_ONLY
ACCEPTANCE_RECORD_PATH: status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_ACCEPTANCE_2026-07-13.md
SUCCESSOR_NAMED_OR_AUTHORIZED: NO
GPG_P1_AUTHORIZED: NO
```

The accepted design bytes must remain unchanged. Acceptance of the generic design does not satisfy nominee selection, consent, critical eligibility scoring, role assignment, external-instrument review, fixture rehearsal, nominee-packet review, or Matt's separate acceptance of a completed real-world custody arrangement. Those gates remain blocking before GPG-P1.

## Residual-risk ledger

| Risk ID | Risk | State | Blocking effect | Evidence or decision required |
|---|---|---|---|---|
| GPG-RR-001 | Recovery depends on secret-key media and a separate passphrase path remaining available | OPEN | Blocks recoverability claims | GPG-P2 plus successful GPG-P3/P8 evidence |
| GPG-RR-002 | Physical media can degrade, disappear, or become unreadable | OPEN | Blocks long-term recovery claims | Annual dual-media hash verification and alternating recovery tests |
| GPG-RR-003 | Password-manager, MFA, or account-recovery behavior can change | OPEN when that option is selected | Blocks reliance on that passphrase path | Annual provider/control review and tested account recovery |
| GPG-RR-004 | GnuPG versions, export formats, algorithms, and operating systems can drift | OPEN | Blocks durable compatibility claims | Recorded toolchain plus recurring compatibility-proven recovery |
| GPG-RR-005 | Matt may be unavailable when recovery is required | PARTIAL — POSTURE AND DESIGN ACCEPTED; REAL ARRANGEMENT ABSENT | Blocks GPG-P1 | Qualified nominee, consent, distinct roles, reviewed external instrument, rehearsal, accepted designation/custody packet, and separate GPG-P1 permit |
| GPG-RR-006 | Possession of protected secret export plus passphrase may enable decryption | OPEN / INHERENT | Blocks zero-risk claims | Physical separation, strong passphrase, access controls, incident response; cannot be fully eliminated |
| GPG-RR-007 | A successful fixture test does not prove every future archive is restorable | OPEN / INHERENT | Blocks general restore claims | Per-archive manifests and separately authorized GPG-P7 restore evidence |

## Compromise and loss handling

| Condition | Required response |
|---|---|
| Passphrase suspected exposed | Stop new encryption; open incident review; evaluate revocation and new identity |
| Secret-key media lost | Stop and inventory remaining independent copy; do not claim recoverability |
| Both recovery media unavailable | Protected backup recovery is failed; do not create additional archives to the key |
| Revocation certificate exposed | Treat as integrity incident; verify key status before new use |
| Fingerprint mismatch | Stop immediately; do not encrypt, import, or overwrite |
| Encryption subkey expired | Stop new archive creation; retain key for old-archive decryption and rotate separately |
| Recovery test fails | Preserve all evidence and source data; do not clean temporary or creation state without review |

## Evidence records required

The following public-safe metadata must be recorded after each authorized phase:

- phase permit and operator;
- GPG version;
- full primary and encryption-subkey fingerprints;
- algorithms, capabilities, creation times, and expiry times;
- public export, secret export, and revocation-certificate byte counts and SHA-256 values;
- Recovery Media A and B custody labels;
- fixture ciphertext and recovered-plaintext hashes;
- recovery-test result;
- exact export format and recovery-tool compatibility evidence;
- annual dual-media verification result and next alternating recovery medium;
- signed succession posture and any separately accepted successor/escrow packet reference;
- accepted trusted-successor design path/hash, review UUID/hash, acceptance-record path/hash, and remaining nominee-arrangement gates;
- current residual-risk states and accepted risks;
- any skipped, failed, or inaccessible step;
- confirmation that no passphrase, secret material, personal location, or user ID entered the evidence record.

No phase may grade or accept itself. Codex may verify public metadata mechanically; an independent reviewer grades the resulting custody evidence; Matt decides acceptance.

## Static acceptance checklist for this plan

Before GPG-P1 can be requested, this plan must receive independent review confirming:

- dedicated backup-only identity and prohibited uses are explicit;
- primary/subkey algorithms, purposes, and expiries are unambiguous;
- passphrase never enters model, repository, environment, or command-line scope;
- two independent recovery media and two separate passphrase recovery paths are required;
- the passphrase generation method provides a documented minimum of 90 bits of entropy without recording the secret;
- any password-manager path is zero-knowledge, end-to-end encrypted, strong-MFA protected, and account-recovery tested;
- revocation certificate is protected and not imported during ordinary testing;
- recovery uses Copy B and a new isolated GPG home;
- full fingerprints, not short IDs, bind every key operation;
- archive creation is blocked until recovery passes;
- old decryption keys remain preserved for retained archives;
- both media receive initial and annual hash verification, with full isolated recovery tests alternating annually;
- the proven GnuPG/export compatibility profile is recorded and reviewed before material toolchain drift;
- Matt has signed exactly one succession posture and accepted the generic trusted-successor design; the real nominee/designation custody packet is separately reviewed and accepted before GPG-P1;
- the residual-risk ledger is current and does not silently imply zero risk;
- cleanup, archive creation, upload, and source deletion each require separate authority;
- failure behavior is fail-closed.

## Current decision

```text
GPG_IDENTITY: NOT_CREATED
PASSPHRASE: NOT_CREATED
REVOCATION_CERTIFICATE: NOT_CREATED
RECOVERY_MEDIA_A: NOT_CREATED
RECOVERY_MEDIA_B: NOT_CREATED
RECOVERY_TEST: NOT_PERFORMED
SUCCESSION_POSTURE: TRUSTED_SUCCESSOR_DESIGN_ACCEPTED / NOMINEE_CUSTODY_PACKET_REQUIRED
PUBLIC_KEY_ONLY_ENVIRONMENT: NOT_CREATED
PROTECTED_ARCHIVE: BLOCKED
NEXT_LANE: RECOMPUTE PLAN HASH; INDEPENDENT READ-ONLY REVIEW; MATT SUCCESSION DECISION
```

## Non-claims

- No GPG home, public key, private key, encryption subkey, passphrase, revocation certificate, export, fixture, recovery medium, archive, or remote was created.
- No identity, email address, user ID, keygrip, passphrase, private-key material, or sensitive value was read, printed, stored, or transmitted.
- No source file outside maintenance documentation was changed, copied, moved, deleted, executed, imported, built, or tested.
- No encryption, decryption, signing, keyserver, cloud, rclone, commit, push, cleanup, or restore action occurred.
- This plan does not prove key security, recoverability, archive safety, secret cleanliness, backup completion, or maintenance closure.
