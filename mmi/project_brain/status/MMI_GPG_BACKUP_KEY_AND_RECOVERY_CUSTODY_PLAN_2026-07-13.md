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
- Use at least seven randomly selected words or an equivalently strong randomly generated value.
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
2. one entry in a trusted password manager or a second sealed paper record stored separately from Recovery Media B.

Neither recovery medium may be stored together with its corresponding passphrase copy. The custody record may document locations using operator-defined labels such as `LOCATION-A` and `LOCATION-B`; it must not publish home addresses, banking locations, safe combinations, or the passphrase.

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
- any skipped, failed, or inaccessible step;
- confirmation that no passphrase, secret material, personal location, or user ID entered the evidence record.

No phase may grade or accept itself. Codex may verify public metadata mechanically; an independent reviewer grades the resulting custody evidence; Matt decides acceptance.

## Static acceptance checklist for this plan

Before GPG-P1 can be requested, this plan must receive independent review confirming:

- dedicated backup-only identity and prohibited uses are explicit;
- primary/subkey algorithms, purposes, and expiries are unambiguous;
- passphrase never enters model, repository, environment, or command-line scope;
- two independent recovery media and two separate passphrase recovery paths are required;
- revocation certificate is protected and not imported during ordinary testing;
- recovery uses Copy B and a new isolated GPG home;
- full fingerprints, not short IDs, bind every key operation;
- archive creation is blocked until recovery passes;
- old decryption keys remain preserved for retained archives;
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
PUBLIC_KEY_ONLY_ENVIRONMENT: NOT_CREATED
PROTECTED_ARCHIVE: BLOCKED
NEXT_LANE: INDEPENDENT READ-ONLY REVIEW OF THIS EXACT PLAN HASH
```

## Non-claims

- No GPG home, public key, private key, encryption subkey, passphrase, revocation certificate, export, fixture, recovery medium, archive, or remote was created.
- No identity, email address, user ID, keygrip, passphrase, private-key material, or sensitive value was read, printed, stored, or transmitted.
- No source file outside maintenance documentation was changed, copied, moved, deleted, executed, imported, built, or tested.
- No encryption, decryption, signing, keyserver, cloud, rclone, commit, push, cleanup, or restore action occurred.
- This plan does not prove key security, recoverability, archive safety, secret cleanliness, backup completion, or maintenance closure.
