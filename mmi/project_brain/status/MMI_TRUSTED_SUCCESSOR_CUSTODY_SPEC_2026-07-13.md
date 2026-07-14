# MMI Trusted-Successor Custody Specification — 2026-07-13

## Status and identity

```text
ARTIFACT: mmi/project_brain/status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_2026-07-13.md
LANE: DESIGN
AUTHORITY_CLASS: DESIGN_ONLY / DOC_CONTROL_ONLY
DOCUMENT_STATUS: DRAFT
ACCEPTANCE_STATUS: INDEPENDENT_REVIEW_REQUIRED
PRODUCER_SURFACE: Cursor Composer
SELECTED_MODEL_LABEL_UI: Opus 4.8 (Anthropic Claude Opus 4.8)
MODEL_IDENTITY_GATE: PASS (explicit named Opus model; not Auto/Gemini/Grok)
MODEL_LABEL_EVIDENCE_MODE: Cursor UI/session label — valid session identity evidence, NOT proof of provider internals
CURRENT_REVISION_PRODUCER: Codex, under Matt's exact documentation-only authorization
PRODUCER_CHAIN: Cursor/Opus created initial draft; Codex materially revised R1; revised artifact must be graded independently from both producers
CURSOR_VERSION_HOST_ATTESTED: 3.11.19
CURSOR_EXECUTABLE_SHA256_HOST_ATTESTED: 080e82f52c7e5f825b27f8aa45419861e55337f31e290c3d4cd8d70cfa20fc4d
PROMPT_ID: MMI-CURSOR-OPUS-TRUSTED-SUCCESSOR-DESIGN-20260713-01
PROMPT_VERSION: 1.0
PACKET_PATH: /tmp/mmi_cursor_opus_trusted_successor_design_20260713.xml
PACKET_SHA256: a6809606f856e4820a27e526e130944f492d7f2e37d0f09e68e460a50a1381af
PACKET_EXPIRES_AT: 2026-07-13T19:57:50-07:00
REPOSITORY_ROOT: /mnt/c/MMI (Windows C:\MMI)
LOCAL_BRANCH: mmi-phase2-commit
LOCAL_HEAD: c2d0a55aab9b59cac92a7228a57a509b8dc81af8
ACTIVE_REMOTE_HEAD: c2d0a55aab9b59cac92a7228a57a509b8dc81af8
OUTPUT_PRECONDITION_OBSERVED: ABSENT (tool-verified before write)
GPG_P1_AUTHORIZED: NO
SUCCESSOR_NAMED_OR_AUTHORIZED: NO
```

Evidence-mode note: git HEAD, remote HEAD, worktree status, and the SHA-256 values of the context target and controlling laws are consumed from the packet's `HOST_ATTESTED` host evidence bundle produced by Codex. Cursor did not run git or a hash tool for this DESIGN task (shell is forbidden in this lane) and does not claim to have generated that evidence. The packet SHA-256 above and the output-path absence were the only facts Cursor verified directly (packet hash before binding; absence via editor-native file read).

## Revision history

| Revision | Date | Producer | Prior hash | Reason | Acceptance effect |
|---|---|---|---|---|---|
| R1 | 2026-07-13 | Codex, under Matt's exact documentation-only authorization | `7b3b7dd2442aa583ae1e933e0e2b900f180b170510d2a8d0269c1d8ac1a1ab80` | Close independent-grade defects in share custody, role separation, fallback, post-Matt authority, dead-man activation, legal boundaries, and residual-risk coverage | Prior grade is dead; revised bytes require a fresh independent grade |
| R2 | 2026-07-13 | Codex, under Matt's exact four-finding documentation authorization | `b42a34c944645d5b581317cce740ed64d539528ec74949feedbbe674c87465a7` | Add custodian-unavailability handling, arbitrary collusion bounds, live-Matt activation rationale, and posture-vs-packet clarification | R1 grade is dead; R2 requires a fresh independent grade |

R1 does not expand authority. Cursor's failed provider attempts made no repository change and carry no performance penalty. The abandoned Cursor revision packet is provenance only and grants no instruction power.

## Purpose, scope, and authority

Purpose: design a public-safe, reviewable custody specification for a `TRUSTED_SUCCESSOR` posture that preserves recovery continuity of the MMI protected-backup GPG identity during Matt's incapacity, death, or prolonged unavailability — without weakening any control in the GPG Backup-Key and Recovery-Custody Plan.

In scope:
- Documentation-only roles, states, transitions, gates, rehearsal design, and residual-risk tracking for a future trusted successor.
- Public-safe placeholders and evidence fields Matt can populate later.

Out of scope (and not performed):
- Naming, selecting, contacting, or ranking any actual person.
- Any GPG or cryptographic action; any authorization of GPG-P1 or later phases.
- Legal, estate-planning, medical, or financial advice; this spec only flags where an appropriately licensed professional must decide.
- Any repository change other than creating this one file.

Authority: This spec is produced under Matt's exact bounded one-use authorization and the authority order in the task packet. A lower authority cannot expand a higher one. This spec grants no access, no legal power, and no cryptographic permission. It is `INDEPENDENT_REVIEW_REQUIRED` and must be graded by a reviewer who did not create it.

Posture-selection boundary: Matt's `TRUSTED_SUCCESSOR` selection in the GPG plan chooses the design direction only. It does not accept this specification, designate or authorize a successor, activate any custody role, satisfy the successor-packet gate, or authorize GPG-P1.

Inherited hard constraints (must not be weakened by this design), from `MMI_GPG_BACKUP_KEY_AND_RECOVERY_CUSTODY_PLAN_2026-07-13.md`:
- Phase separation; authority never carries between phases (GPG plan "Phase separation and permits", lines 81–97).
- Passphrase never enters model/repo/env/CLI scope; pinentry-only (lines 128–157).
- Two physically/administratively independent recovery media (lines 176–213).
- Full-fingerprint binding for every key operation (line 126).
- Recurring dual-media verification and annual alternating recovery tests (lines 207–213, GPG-P8 line 95).
- Succession posture must be signed by Matt before GPG-P1; no model/operator signs for Matt (lines 304–316).
- Matt is sole approval authority throughout.

## Controlling inputs and hash bindings

All hashes below are `HOST_ATTESTED` from the packet's host evidence bundle except where marked. Each inherited requirement is cited to a source heading/line.

| Input | Path | SHA-256 | Verification mode |
|---|---|---|---|
| Context target: GPG custody plan | `status/MMI_GPG_BACKUP_KEY_AND_RECOVERY_CUSTODY_PLAN_2026-07-13.md` | `bb2452925441cf2010bd5b3e69af54f7978013428ddad5f4592cbb6df90a95ce` | HOST_ATTESTED (content read editor-native) |
| Build/preservation laws | `status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md` | `0b2a53a2a5e924b4cec9285e5a954065b0175e1e3d4d084d6b5cee3ca0e38eeb` | HOST_ATTESTED |
| Active scope | `status/MMI_ACTIVE_SCOPE.md` | `83a89bc1d9f6e444b0f21c412813c614b884a270c69f18bfc55674586f60ee50` | HOST_ATTESTED |
| Project laws | `status/LLM_PROJECT_LAWS_2026-07.md` | `637120f97621526afa6fdd5e2aab39d35d2aad39b48bec29dc171ef3c850f741` | HOST_ATTESTED |
| Universal rubric | `status/LLM_UNIVERSAL_PROJECT_RUBRIC_2026-07.md` | `054c4661df34f7f0d741a5e9ccf370f047902e31d8c2a7c5c30ec7cd675a35e4` | HOST_ATTESTED |
| Model audit standard | `status/LLM_MODEL_AUDIT_STANDARD_2026-07.md` | `267106cfc68f8c75c12f9e92c3817ae084d6608ce9ed130428696512f130625d` | HOST_ATTESTED |
| Design laws | `status/LLM_DESIGN_LAWS_2026-07.md` | `8ed8961c77741a43be86e4c79c61f72320d91d0cb8794eb1eb890d0739b63ef8` | HOST_ATTESTED (content read editor-native) |
| Prompt custody index | `lanes/MMI_MODEL_PROMPT_CUSTODY_INDEX_2026-07.md` | `2354c23e262d5878d2311f1d227e3d59b3e359d72e00c757f6665f64f5c74b8e` | HOST_ATTESTED |
| Task packet | `/tmp/mmi_cursor_opus_trusted_successor_design_20260713.xml` | `a6809606f856e4820a27e526e130944f492d7f2e37d0f09e68e460a50a1381af` | TOOL_VERIFIED (before binding) |

## Definitions and public-safe placeholders

Only public-safe labels may ever be written to the repository. Never store a real name, address, credential, or secret.

| Placeholder | Meaning | Example public-safe value |
|---|---|---|
| `SUCCESSOR_ID_REF` | Opaque reference to the designated successor held off-repo by Matt | `SUCC-REF-01` |
| `SUCCESSOR_CANDIDATE_REF` | Opaque reference to a person under evaluation | `CAND-REF-A` |
| `LOCATION_LABEL` | Operator-defined label for a physical location | `LOCATION-C` |
| `AUTHORITY_DOCUMENT_REF` | Reference to an external legal instrument held off-repo | `LEGAL-DOC-REF-01` |
| `PROFESSIONAL_REF` | Reference to a licensed legal/estate/custody professional if engaged | `PRO-REF-01` |
| `REHEARSAL_FIXTURE_REF` | Reference to a harmless non-production rehearsal key/fixture set | `REH-FIX-01` |
| `CONTROL_SHARE_A` / `CONTROL_SHARE_B` | The two split-control elements (secret-key media vs passphrase-recovery path) | labels only |
| `IDENTITY_VERIFIER_REF` | Independent party that verifies successor identity, liveness, and non-coercion; has no release or activation authority | `IDV-REF-01` |
| `SHARE_A_RELEASE_CUSTODIAN_REF` | Off-repo custodian that controls release of Share A under an established instrument | `A-CUST-REF-01` |
| `SHARE_B_RELEASE_CUSTODIAN_REF` | Different off-repo custodian that controls release of Share B under an established instrument | `B-CUST-REF-01` |
| `ACTIVATION_AUTHORITY_REF` | External person, office, institution, or instrument-defined body authorized to approve activation after evidence gates pass | `ACT-AUTH-REF-01` |
| `INDEPENDENT_REVIEWER_REF` | Reviewer that verifies public-safe gate evidence and is separate from successor and release custodians | `REV-REF-01` |
| `ALTERNATE_SUCCESSOR_REF` | Pre-screened and rehearsed alternate successor; never improvised during crisis | `ALT-SUCC-REF-01` |
| `PREARRANGED_ESCROW_REF` | Optional independently reviewed fallback established before dormancy | `ESCROW-REF-01` |

Definitions:
- Successor: a human authorized only after full designation + rehearsal + Matt acceptance to perform recovery on Matt's behalf under defined activation conditions.
- Activation: the fail-closed transition allowing the successor to obtain the second control share and perform recovery.
- Rehearsal: a proof of procedure using non-production fixtures only; never production keys, passphrase, archives, or recovery locations.
- Dormant authority: a designated-but-inactive state that grants no present access.

## Roles and separation of duties

| Role | Allowed | Forbidden |
|---|---|---|
| Matt | Sole MMI project approval authority while alive and able; nominate/screen/designate/revoke; sign succession posture; establish external instruments and custodians | Personally co-locate both shares; delegate project approval authority to a model; store passphrase/secret in repo/model/chat |
| Successor (`SUCCESSOR_ID_REF`) | After activation only: receive separately released shares and perform recovery per accepted instructions | Custody or access either production share before valid activation; alter laws; self-activate |
| Codex | Prepare public-safe documentation/permits; verify public hashes, counts, states; maintain the custody manifest | Receive/store/infer passphrase or secret-key material; grade its own work; name or select the successor |
| Independent reviewer (`INDEPENDENT_REVIEWER_REF`) | Grade this spec and later public-safe custody evidence; confirm separation and fail-closed behavior | Access secret material; approve its own review; act as successor, custodian, or activation authority |
| Legal/estate professional (`PROFESSIONAL_REF`, if engaged) | Advise on, prepare, witness, or review instruments within the professional's lawful role | Claim that this specification itself establishes legal validity; substitute model judgment for applicable law or institutions |
| Identity verifier (`IDENTITY_VERIFIER_REF`) | Confirm successor identity, liveness, and non-coercion at activation | Hold/release either share; authorize activation; be successor |
| Share A release custodian (`SHARE_A_RELEASE_CUSTODIAN_REF`) | Hold and release Share A only after valid activation authorization | Hold Share B; verify itself; be successor or sole activation authority |
| Share B release custodian (`SHARE_B_RELEASE_CUSTODIAN_REF`) | Hold and release Share B only after valid activation authorization | Hold Share A; verify itself; be successor or sole activation authority |
| Activation authority (`ACTIVATION_AUTHORITY_REF`) | Apply an externally established instrument to authorize or deny release after required evidence passes | Hold either share; act as identity verifier or successor; invent authority during crisis |
| Alternate successor (`ALTERNATE_SUCCESSOR_REF`) | Serve only if pre-screened, rehearsed, accepted, and activated through the same gates | Become fallback through an improvised crisis-time decision |
| GPG/pinentry tooling | Perform future cryptographic operations under a separate permit only | Persist passphrase in files/env/args/logs |

Core separation invariants:

- No person or institution other than Matt acting during an explicitly authorized recovery test may combine both production shares before `ACTIVATED`.
- The successor has no production-share custody or access before `ACTIVATED`.
- Identity verification, activation authorization, Share A release, and Share B release are distinct functions. No single non-Matt role may perform more than one of those functions for the same activation.
- Each release custodian validates the same activation authorization independently; neither custodian's release causes or authorizes the other release.

## Nominee eligibility scoring matrix

Score each criterion 0–3 (`3 CLEAN`, `2 ADEQUATE`, `1 WEAK`, `0 FAILED`). Critical criteria marked `YES`; any critical criterion below 3 makes the nominee `F_BLOCKED` regardless of totals. Use the lowest non-critical score next; the weighted percentage is an advisory tie-break only, computed only after all critical criteria are 3. `UNKNOWN` is never a 3. This matrix does not name or rank a real person.

| Criterion | Critical | Weight | Scoring guidance |
|---|:--:|--:|---|
| Trustworthiness and integrity (no conflict of interest) | YES | 20 | Evidence of reliability; no incentive to misuse archives |
| Can satisfy identity + anti-impersonation at activation | YES | 15 | Able to complete `IDENTITY_VERIFIER_REF` liveness/identity checks |
| Access separation maintainable (won't hold both shares early) | YES | 20 | Storage/relationship keeps shares independent until activation |
| Willing and informed consent to the role | YES | 10 | Documented consent; understands burden and limits |
| Able to complete rehearsal without exposing production secrets | YES | 10 | Can follow fixture rehearsal reliably |
| Technical capability (guided recovery) | NO | 10 | Can follow public-safe recovery instructions, possibly assisted |
| Long-term availability / likely reachable when needed | NO | 5 | Reasonable continuity horizon |
| Jurisdiction / legal-instrument feasibility | NO | 10 | An `AUTHORITY_DOCUMENT_REF` can be validly established |

Disqualifiers (automatic `F_BLOCKED`): unwillingness/withdrawn consent; unresolved conflict of interest; inability to be independently identity-verified; inability to keep the two control shares separate; any request to hold both shares "for convenience"; evidence of coercion risk.

Re-evaluation cadence: at least annually, and immediately on any disqualifier trigger, relationship change, relocation, or capability change.

```text
NOMINEE_SCORE_RECORD (public-safe):
CANDIDATE_REF:
CRITICAL_GATE_RESULT: PASS | F_BLOCKED
CRITICAL_SCORES: {trust:, identity:, separation:, consent:, rehearsal:}
LOWEST_NONCRITICAL_SCORE:
WEIGHTED_TIE_BREAK_PERCENT:
DISQUALIFIERS_TRIGGERED: [NONE|LIST]
EVALUATION_DATE:
NEXT_REEVALUATION_DUE:
```

## Custody state machine

States (exactly these):

```text
CANDIDATE            → under initial consideration; no authority, no access
SCREENED             → eligibility matrix scored PASS; still no authority/access
DESIGNATED_PENDING   → Matt intends to designate; awaiting rehearsal + acceptance
REHEARSAL_AUTHORIZED → rehearsal permitted with fixtures only
REHEARSAL_PASSED     → fixture rehearsal proven; still no production access
ACTIVE_DORMANT       → designated + accepted; holds no present access; awaits activation event
ACTIVATION_PENDING   → a claimed activation condition is under independent verification
ACTIVATED            → activation verified; successor may obtain second control share and recover
SUSPENDED            → authority frozen pending review (fail-closed)
REVOKED              → authority permanently withdrawn for this successor
REPLACED             → superseded by a different designated successor
```

Invariants:
- No state before `ACTIVATED` grants any access to a second control share or to production secret material.
- `ACTIVE_DORMANT` is the normal long-lived resting state and confers dormant authority only.
- Any anomaly defaults to `SUSPENDED` (fail-closed), never to `ACTIVATED`.
- `REVOKED` and `REPLACED` are terminal for that `SUCCESSOR_ID_REF`.

## Transition table and authorization gates

| From → To | Authority | Required evidence | Expiry / fail-closed |
|---|---|---|---|
| CANDIDATE → SCREENED | Matt | Eligibility matrix PASS; documented consent | Screening older than 12 months lapses to CANDIDATE |
| SCREENED → DESIGNATED_PENDING | Matt | Recorded intent; posture already `TRUSTED_SUCCESSOR` | — |
| DESIGNATED_PENDING → REHEARSAL_AUTHORIZED | Matt | Fixture set `REHEARSAL_FIXTURE_REF` prepared; independent reviewer confirms fixtures are non-production | No production material referenced or fail-closed to SUSPENDED |
| REHEARSAL_AUTHORIZED → REHEARSAL_PASSED | Matt + independent reviewer | Rehearsal evidence: fixture fingerprint + plaintext-hash match; no production secret touched | Any exposure → SUSPENDED |
| REHEARSAL_PASSED → ACTIVE_DORMANT | Matt | Matt acceptance of exact spec + successor packet hash; manifest updated | — |
| ACTIVE_DORMANT → ACTIVATION_PENDING | Matt (explicit) OR `ACTIVATION_AUTHORITY_REF` acting under a pre-established instrument | Activation instrument reference; trigger evidence logged; fallback already established | Unverified or contradictory claim → SUSPENDED |
| ACTIVATION_PENDING → ACTIVATED | `ACTIVATION_AUTHORITY_REF`; identity verifier and independent reviewer provide evidence but do not authorize | Identity/liveness/non-coercion PASS; trigger evidence PASS; cancellation window expired without abort; external determination where required | Any failed, missing, stale, or ambiguous evidence → SUSPENDED |
| any → SUSPENDED | Matt, or automatic on anomaly | Anomaly/incident note | Default on doubt |
| any nonterminal state → SUSPENDED on Share A/B custodian failure | Automatic; no discretionary approval required | Custodian unavailable, refuses, loses material, loses independence, or fails required verification | Both custodians freeze; no release; continuity/replacement terms reviewed |
| SUSPENDED → ACTIVE_DORMANT | Matt while able; otherwise `ACTIVATION_AUTHORITY_REF` under the pre-established instrument + independent review | Incident resolved; roles, instruments, and controls re-verified | No crisis-time invention of authority |
| SUSPENDED → prior safe state after custodian replacement | Matt while able; otherwise pre-established replacement mechanism + independent reviewer concurrence | Replacement custodian qualified; custody transferred under separately authorized preservation procedure; hashes/independence re-verified | If either share or authority chain remains uncertain, stay SUSPENDED |
| any → REVOKED | Matt while able; otherwise `ACTIVATION_AUTHORITY_REF` under the pre-established instrument + independent reviewer concurrence | Revocation evidence | Terminal |
| any → REPLACED | Matt while able; otherwise pre-authorized alternate/fallback mechanism under the established instrument + independent reviewer concurrence | Alternate was screened, rehearsed, dormant, and accepted before the crisis | Terminal for prior ref; absent eligible fallback → SUSPENDED |

No transition may be executed by a model; models may only prepare public-safe documentation and verify public metadata.

## Activation-condition design

Activation is fail-closed and evidence-bound. This spec defines *procedure and evidence gates only*; it does not adjudicate legal or medical status.

Activation triggers (each requires the stated external authority, not model judgment):
- Explicit Matt activation: Matt directly authorizes activation while able. Evidence: signed activation instrument reference.
- Incapacity: requires a determination by an appropriate licensed authority (`PROFESSIONAL_REF` / medical/legal), referenced as `AUTHORITY_DOCUMENT_REF`. The model/Codex must mark medical/legal determination `MATT_INPUT_REQUIRED` / external-authority-required and must not infer it.
- Death: requires a legally recognized instrument/record referenced off-repo; external authority required.
- Prolonged unavailability: requires a pre-agreed, documented dead-man threshold (e.g., a defined no-contact interval `UNAVAILABILITY_INTERVAL_REF`) plus independent verification; the threshold value is a `MATT_INPUT_REQUIRED` decision.

Prolonged unavailability may not rely on elapsed time alone. It requires all of the following:

1. At least two non-derivative signals from separate evidence families, such as failed contact through multiple pre-registered channels plus confirmation from a separate authorized human/institution. Copies, forwarded messages, or multiple observations from one account are one signal.
2. Repeated contact attempts through the pre-registered channels and cadence defined off-repo.
3. A public-safe activation-attempt record with unique nonce/ID, timestamps, signal-family labels, and evidence references.
4. An explicit waiting and cancellation window beginning only after the second independent signal. Matt may abort through a pre-registered cancellation method; contradictory evidence or successful contact immediately forces `SUSPENDED` and resets the attempt.
5. Identity-verifier and independent-reviewer confirmation that the signals are independent and current.
6. Final authorization only by `ACTIVATION_AUTHORITY_REF` under the pre-established instrument after the cancellation window expires.

Travel, hospitalization, communications outage, lost devices, account compromise, delayed messages, or a single third-party assertion are explicit false-positive scenarios. Urgency never shortens the cancellation window.

Mandatory verification before `ACTIVATED`:
1. Identity verifier `IDENTITY_VERIFIER_REF` (not the successor, custodian, or activation authority) confirms successor identity and liveness.
2. Non-coercion / duress check passes (see next section).
3. The activation instrument reference and asserted authority are confirmed present and parseable; the model makes no legal-validity determination.
4. For incapacity/death, the external legal/medical authority requirement is satisfied off-model.

Even when Matt is alive and able and explicitly initiates activation, final release still passes through `ACTIVATION_AUTHORITY_REF`, `IDENTITY_VERIFIER_REF`, and the two independent release custodians. This is deliberate coercion resistance and separation of duties: possession of Matt's instruction, device, account, signature channel, or coerced cooperation must not permit one-party release of both shares. Matt retains sole MMI approval authority, while the pre-established release process independently verifies that approval and enforces the accepted custody controls.

Applicable law, executed instruments, relevant institutions, and—where applicable—courts determine legal effect. Professionals may advise, prepare, witness, or review within their lawful roles; they do not make this document legally sufficient by declaration.

If any check is missing or ambiguous → `SUSPENDED`. Activation never proceeds on inference, urgency, a single signal, or a newly invented authority.

## Split-control and secret-separation design

Two independent control shares, never both held by a non-Matt party before `ACTIVATED`:

- `CONTROL_SHARE_A` — the GPG secret-key recovery media (Recovery Media A or B), passphrase-protected. Held per the GPG plan's independent-media rules.
- `CONTROL_SHARE_B` — the passphrase-recovery path (sealed offline record and/or the plan's permitted zero-knowledge E2EE password-manager path).

Required mechanism:

1. `CONTROL_SHARE_A` remains with `SHARE_A_RELEASE_CUSTODIAN_REF` and `CONTROL_SHARE_B` remains with the distinct `SHARE_B_RELEASE_CUSTODIAN_REF` until `ACTIVATED`.
2. Both custodians require the same current authorization from `ACTIVATION_AUTHORITY_REF`, but independently validate it and release only their own share.
3. `IDENTITY_VERIFIER_REF` and `INDEPENDENT_REVIEWER_REF` provide evidence; neither releases a share or authorizes activation.
4. Optional M-of-N control may further protect a share only under a separately reviewed design; it does not replace the two-custodian separation or place any secret in repo/model scope.

Invariants:
- Possession of one share alone must not enable decryption (mirrors GPG plan lines 201–202).
- No mechanism may place any secret into the repository, a model, chat, or an unencrypted cloud object.
- The successor obtaining both shares before a valid activation is a hard failure → `SUSPENDED` + incident review.

### State-by-state production-share custody map

| State | Share A custodian | Share B custodian | Successor access | Release authority | Verifier/reviewer | Allowed release | Fail-closed result |
|---|---|---|---|---|---|---|---|
| CANDIDATE | A custodian; no candidate-linked release | B custodian; no candidate-linked release | None | None | Screening reviewer only | None | Remain CANDIDATE |
| SCREENED | A custodian | B custodian | None | None | Independent reviewer | None | Return to CANDIDATE/SUSPENDED |
| DESIGNATED_PENDING | A custodian | B custodian | None | Matt only for designation, not share release | Independent reviewer | None | SUSPENDED |
| REHEARSAL_AUTHORIZED | A custodian; production share untouched | B custodian; production share untouched | Rehearsal fixtures only | Matt authorizes fixture rehearsal only | Independent reviewer | No production release | SUSPENDED |
| REHEARSAL_PASSED | A custodian | B custodian | None | None | Independent reviewer records result | None | SUSPENDED |
| ACTIVE_DORMANT | A custodian | B custodian | None | Pre-established instrument exists but is inactive | Annual independent review | None | SUSPENDED |
| ACTIVATION_PENDING | A custodian | B custodian | None | Activation authority evaluates evidence; cannot release | Identity verifier + independent reviewer | None during cancellation window | SUSPENDED on doubt/contradiction |
| ACTIVATED | A custodian until separate release | B custodian until separate release | Receives each share only after separate valid releases | Activation authority under established instrument | Identity verifier + independent reviewer | A custodian releases A; B custodian releases B | SUSPENDED; unreleased share remains held |
| SUSPENDED | A custodian; frozen | B custodian; frozen | None; previously released material handled under incident plan | None until authorized resolution | Independent incident review | None | Remain SUSPENDED |
| REVOKED | A custodian; prior successor release prohibited | B custodian; prior successor release prohibited | None | Matt while able or established post-Matt authority | Independent reviewer | None to revoked successor | Terminal |
| REPLACED | A custodian rebound to accepted alternate packet | B custodian rebound to accepted alternate packet | Prior successor none; alternate none until its activation | Pre-authorized fallback mechanism | Independent reviewer | None until alternate validly ACTIVATED | SUSPENDED if fallback incomplete |

No table entry transfers physical custody merely by changing a state label. Custody or release changes require separately evidenced action under the accepted instrument.

### Pre-authorized fallback requirement

Before `ACTIVE_DORMANT`, Matt must establish at least one fallback: a fully screened, consented, fixture-rehearsed, independently accepted `ALTERNATE_SUCCESSOR_REF`, or an independently reviewed `PREARRANGED_ESCROW_REF`. The fallback has its own custodians and cannot share a release single point of failure with the primary path where avoidable.

A candidate identified only after Matt becomes unavailable is not an eligible fallback. If the primary successor refuses, disappears, is compromised, or fails identity checks and no pre-authorized fallback is usable, the state is `SUSPENDED`; no crisis-time escrow selection or improvised replacement is permitted.

## Identity, anti-impersonation, coercion, and replay controls

- Identity: at activation, `IDENTITY_VERIFIER_REF` (independent of the successor, custodians, and activation authority) performs a documented identity + liveness check; single self-asserted identity is insufficient.
- Anti-impersonation: activation instrument references must match pre-registered public-safe references; unmatched references → `SUSPENDED`.
- Coercion/duress: define a private, off-repo duress signal or safeword protocol held by Matt/verifier (value never stored in repo/model); a duress indication forces `SUSPENDED` and incident handling, not activation.
- Social-engineering resistance: no activation via chat, email, model, or phone alone; requires the pre-defined multi-party verification.
- Replay resistance: each activation attempt is uniquely logged (public-safe attempt ID, timestamp); a reused or stale instrument reference is rejected. Rehearsal artifacts are labeled non-production so they can never be replayed as a real activation.
- No secret in verification: identity/coercion checks must not require revealing the passphrase or secret key.

## Harmless-fixture rehearsal design

Purpose: prove the successor can execute recovery *procedure* without ever touching production secrets.

- Use a dedicated non-production fixture key set `REHEARSAL_FIXTURE_REF` generated solely for rehearsal (a separate, clearly labeled test identity), never the production MMI backup identity.
- Encrypt a harmless fixture (fixed UTF-8 content, recorded byte count and SHA-256; no secrets, no personal data) to the rehearsal key — mirroring GPG plan lines 233–242, but with rehearsal-only material.
- Rehearsal proves: media reading, guided import into an isolated home, pinentry entry of a rehearsal-only passphrase, fingerprint match, fixture decryption, and plaintext-hash match.
- Absolute rules: never rehearse with the production passphrase, production secret key, real archives, or real recovery locations; never enter any real passphrase into chat, Cursor, repository, or ordinary documentation.
- Record only public-safe rehearsal evidence (fixture fingerprint, plaintext-hash match, pass/fail, tested medium reference, date).
- Rehearsal cadence: on designation and at least annually; a failed rehearsal blocks `ACTIVE_DORMANT` / forces `SUSPENDED`.

## Suspension, revocation, replacement, and incident handling

| Scenario | Required response | Resulting state |
|---|---|---|
| Anomaly / unverified activation claim | Freeze; independent review | SUSPENDED |
| Successor withdraws consent | Revoke; use only a pre-authorized fallback | REVOKED → REPLACED, or SUSPENDED if none |
| Successor loses contact / unreachable | Attempt re-verification; if unresolved, invoke only a pre-authorized fallback | SUSPENDED → REPLACED, or remain SUSPENDED |
| Conflict of interest emerges | Re-score matrix; likely disqualify | SUSPENDED/REVOKED |
| Suspected coercion at activation | Duress protocol; do not activate | SUSPENDED + incident |
| Suspected share compromise (either share) | Follow GPG plan compromise handling (lines 410–420); block new archives to identity; evaluate re-key | SUSPENDED + incident |
| Successor refuses at activation time | Record; invoke accepted alternate/escrow already established before dormancy | SUSPENDED → REPLACED, or remain SUSPENDED |
| Primary successor compromised after Matt unavailable | Established activation authority + independent reviewer revoke; custodians freeze; invoke pre-authorized fallback | REVOKED/SUSPENDED → REPLACED |
| Activation authority unavailable or deadlocked | Custodians release nothing; invoke pre-established alternate authority only if instrument already defines it | SUSPENDED |
| Share A or Share B custodian unavailable, refuses, loses material, or loses independence | Both custodians freeze; release nothing; use only pre-established custodian continuity/replacement terms and separately authorized preservation handling | SUSPENDED; return to prior safe state only after independent re-verification |
| Replacement activated | Verify the alternate was screened, rehearsed, dormant, and accepted before crisis; supersede prior ref | prior → REPLACED |

Emergency revocation is always available to Matt and defaults fail-closed. Revocation of the successor role is distinct from GPG key revocation; the latter uses the GPG plan's revocation-certificate custody (lines 159–174) and its own incident authorization.

## Review cadence and invalidation triggers

Scheduled:
- Annual nominee re-evaluation (matrix re-score).
- Annual rehearsal (fixtures only).
- Alignment with GPG plan GPG-P8 annual dual-media verification and alternating A/B recovery tests (GPG plan lines 207–213, 95).

Event-driven invalidation (any triggers re-review; several force `SUSPENDED`):
- Change of successor relationship, capability, jurisdiction, or location.
- Withdrawn/uncertain consent.
- Any control-share co-location or early combination.
- Change to the password-manager posture backing `CONTROL_SHARE_B`.
- Material GnuPG/OS/export-format drift (defer to GPG plan compatibility review, lines 214–219).
- Change to repository authority, laws, or the GPG plan hash (this spec's inherited citations must be re-verified).
- Any suspected compromise, coercion, or impersonation attempt.
- Any custodian, activation authority, verifier, reviewer, alternate, or escrow role becoming unavailable, conflicted, merged, or no longer independent.
- Any change to the external activation/release instrument or its asserted legal effect.

## Public-safe custody manifest schema

Only public-safe values; never a name, address, credential, or secret.

```text
SUCCESSION_POSTURE: TRUSTED_SUCCESSOR
SPEC_HASH: <sha256 of this artifact, host-computed after serialization>
SUCCESSOR_ID_REF:
CURRENT_STATE: CANDIDATE|SCREENED|DESIGNATED_PENDING|REHEARSAL_AUTHORIZED|REHEARSAL_PASSED|ACTIVE_DORMANT|ACTIVATION_PENDING|ACTIVATED|SUSPENDED|REVOKED|REPLACED
NOMINEE_MATRIX_RESULT: PASS|F_BLOCKED
LAST_SCREENING_DATE:
CONSENT_ON_FILE: YES|NO
CONTROL_SHARE_A_LABEL:
CONTROL_SHARE_B_LABEL:
SHARE_SEPARATION_CONFIRMED: YES|NO
LAST_REHEARSAL_DATE:
LAST_REHEARSAL_RESULT: PASS|FAIL
ACTIVATION_INSTRUMENT_REF: <AUTHORITY_DOCUMENT_REF or NONE>
IDENTITY_VERIFIER_REF:
SHARE_A_RELEASE_CUSTODIAN_REF:
SHARE_B_RELEASE_CUSTODIAN_REF:
ACTIVATION_AUTHORITY_REF:
INDEPENDENT_REVIEWER_REF:
ALTERNATE_SUCCESSOR_REF:
PREARRANGED_ESCROW_REF_OR_NONE:
FALLBACK_ACCEPTED_BEFORE_DORMANCY: YES|NO
DEADMAN_SIGNAL_FAMILIES_REQUIRED: 2_OR_MORE
CANCELLATION_WINDOW_REF:
LAST_REVIEW_DATE:
NEXT_REVIEW_DUE:
GPG_PLAN_HASH_BOUND: bb2452925441cf2010bd5b3e69af54f7978013428ddad5f4592cbb6df90a95ce
OPEN_RESIDUAL_RISKS: [IDS]
NOTES: public-safe only
```

## Failure modes and falsifiers

| Decision | Failure mode | Falsifier (evidence that would prove it unsafe) |
|---|---|---|
| Split control (two shares) | Both shares end up with the successor early | Any manifest/observation showing share co-location before ACTIVATED |
| Fail-closed activation | System activates on an unverified claim | Any ACTIVATED transition lacking `IDENTITY_VERIFIER_REF` evidence + activation-authority instrument evidence |
| Rehearsal isolation | Rehearsal touches production secret | Any rehearsal record referencing the production identity/passphrase/archive |
| Identity/coercion controls | Impersonator or coerced successor activates | Activation without independent verifier or with a triggered duress signal |
| External-authority gating | Model infers incapacity/death | Any state advance citing model judgment instead of `PROFESSIONAL_REF`/legal instrument |
| Manifest is public-safe | A secret/name/address leaks into repo | Any manifest field containing a real name, location, or secret |
| Compatibility with GPG plan | Successor path weakens a GPG control | Any conflict between this spec and GPG plan lines cited above |
| Separate release custodians | One custodian controls or releases both shares | Any role/custody record showing one custodian controls A and B |
| Role incompatibility | Successor/verifier/authority/custodian roles merge | Any person/reference occupying incompatible roles for one activation |
| Post-Matt authority | Crisis requires a new Matt decision | Any transition that cannot proceed or fail closed under the pre-established instrument |
| Pre-authorized fallback | Alternate is chosen only after crisis begins | Alternate/escrow acceptance timestamp later than ACTIVATION_PENDING |
| Multi-signal unavailability | Timer or one account triggers activation | Attempt lacks two non-derivative evidence families |
| Cancellation window | False-positive signal cannot be aborted | Activation occurs before window expiry or despite valid cancellation/contradiction |
| Bounded legal role | Document/professional assertion is treated as conclusive legal validity | Activation evidence relies only on this spec or a professional's unsupported declaration |

## Residual-risk ledger

| Risk ID | Risk | State | Blocking effect | Evidence/decision to close |
|---|---|---|---|---|
| TS-RR-001 | No suitable, willing, trustworthy successor may exist | OPEN / MATT_INPUT_REQUIRED | Blocks TRUSTED_SUCCESSOR activation | Nominee matrix PASS + documented consent |
| TS-RR-002 | Successor could obtain both control shares before activation | PARTIAL | Weakens separation | Custodian separation design chosen + verified; manifest `SHARE_SEPARATION_CONFIRMED: YES` |
| TS-RR-003 | Activation on impersonation/coercion | OPEN | Unsafe activation | Independent verifier + duress protocol tested |
| TS-RR-004 | Legal validity of incapacity/death/authority instrument | OPEN / EXTERNAL_AUTHORITY_REQUIRED | Blocks lawful activation | `PROFESSIONAL_REF` review; `AUTHORITY_DOCUMENT_REF` established |
| TS-RR-005 | Successor availability/capability lapses over time | OPEN | Erodes continuity | Annual re-evaluation + replacement path |
| TS-RR-006 | `CONTROL_SHARE_B` password-manager posture changes | OPEN when that path used | Breaks passphrase recovery | Annual provider/control review (GPG plan lines 151–153) |
| TS-RR-007 | Rehearsal proves procedure, not every future real activation | OPEN / INHERENT | Blocks "proven" activation claim | Recurring rehearsal + real activation verification at event time |
| TS-RR-008 | This spec is a draft, not implemented or legally sufficient | OPEN | Blocks reliance | Independent grade + Matt acceptance + professional review |
| TS-RR-009 | Share-release custodian becomes unavailable, loses material, or refuses | OPEN | Can deadlock recovery or lose a share | Two independently reviewed custodians, continuity/replacement terms, annual confirmation |
| TS-RR-010 | Custodian colludes with successor or another custodian | OPEN / INHERENT | May enable premature combination | Role incompatibility, separate institutions where feasible, independent logs, incident detection; cannot be fully eliminated |
| TS-RR-011 | Custodian colludes with activation authority | OPEN / INHERENT | May bypass release gate for one share | Separate second custodian, identity verification, reviewer evidence, anomaly suspension |
| TS-RR-012 | Activation authority is unavailable, conflicted, or deadlocked | OPEN | Blocks activation | Pre-established alternate authority in the external instrument; annual rehearsal; otherwise SUSPENDED |
| TS-RR-013 | Alternate successor or escrow fallback also fails | OPEN | Blocks continuity after primary failure | Independently screened/rehearsed fallback with distinct failure dependencies |
| TS-RR-014 | False dead-man signals trigger an activation attempt | PARTIAL | Risks unauthorized release | Two independent signal families, cancellation window, contradiction reset, no release while pending |
| TS-RR-015 | External instrument is invalid, stale, disputed, or unenforceable | OPEN / EXTERNAL_AUTHORITY_REQUIRED | Blocks lawful release | Periodic qualified professional review and institution/court handling where applicable; no model closure |
| TS-RR-016 | Arbitrary multi-party collusion, including activation-authority + identity-verifier, activation-authority + reviewer, both custodians, or three-or-more-role coalitions | OPEN / INHERENT | May forge evidence, bypass gates, or combine shares | Role incompatibility, organizational separation where feasible, independent event logs, periodic role re-screening, contradiction detection, and incident suspension; no finite role design eliminates coordinated collusion |

No zero-risk claim is made. This ledger must be kept current; a silent "closed" state is prohibited without cited evidence.

## Matt input required

Only decisions that cannot be derived from evidence (prefer defaults/matrix over open questions):

1. `MATT_INPUT_REQUIRED` — Whether to designate a specific person at all, and their opaque `SUCCESSOR_ID_REF` (held off-repo). The model must not name or choose.
2. `MATT_INPUT_REQUIRED` — Prolonged-unavailability threshold value (`UNAVAILABILITY_INTERVAL_REF`).
3. `MATT_INPUT_REQUIRED` — Select two distinct qualified release custodians under the mandatory two-custodian design; decide only whether a separately reviewed M-of-N control additionally protects either share.
4. `MATT_INPUT_REQUIRED` — Establish the external activation/release instrument and obtain appropriately qualified professional review; models cannot determine legal sufficiency.
5. `MATT_INPUT_REQUIRED` — Select distinct off-repo references for identity verifier, Share A custodian, Share B custodian, activation authority, independent reviewer, and alternate/fallback, subject to the incompatibility rules.
6. `MATT_INPUT_REQUIRED` — Define at least two acceptable prolonged-unavailability signal families, the contact cadence, cancellation window, and pre-registered cancellation method.
7. `MATT_INPUT_REQUIRED` — Establish an alternate successor and/or governed escrow before `ACTIVE_DORMANT`.
8. `EXTERNAL_AUTHORITY_REQUIRED` — Applicable law, executed instruments, institutions, and possibly courts determine the legal effect of incapacity/death/authority arrangements. This spec only flags the need.

## Static acceptance checklist

Before this spec can support any successor designation, independent review must confirm:
- posture is `TRUSTED_SUCCESSOR` and does not weaken any cited GPG plan control;
- eligibility matrix uses 0–3 scoring, critical gates, lowest-score rule, and disqualifiers;
- the state machine contains exactly the required states with fail-closed defaults;
- transitions name authority, evidence, and expiry; no model executes a transition;
- activation is fail-closed and defers legal/medical determinations to external authority;
- split-control prevents early possession of both shares;
- every state maps both share custodians, successor access, release authority, verifier, permitted release, and fail-closed result;
- identity verification, activation authority, Share A release, and Share B release are distinct incompatible roles;
- a pre-authorized alternate or escrow fallback exists before ACTIVE_DORMANT;
- post-Matt suspension, revocation, refusal, compromise, and replacement use a pre-established external instrument rather than a new Matt decision;
- prolonged-unavailability activation uses at least two independent signal families and an abortable cancellation window;
- professional/legal language does not claim this document or one professional determines legal validity;
- Share A/B custodian unavailability, refusal, lost material, or lost independence has an explicit fail-closed transition and incident response;
- arbitrary two-party and multi-party collusion remains explicitly recognized as an inherent residual risk;
- live-able-Matt activation retains independent release gates for documented coercion resistance and separation of duties;
- posture selection is not misrepresented as acceptance or activation of this packet;
- identity/anti-impersonation/coercion/replay controls are present and testable;
- rehearsal uses only non-production fixtures and never a real passphrase;
- suspension/revocation/replacement/incident paths are defined;
- annual review/rehearsal cadence and event-driven invalidation triggers are defined;
- the custody manifest schema is public-safe only;
- failure modes, falsifiers, and a current residual-risk ledger are present;
- non-claims are explicit; GPG-P1 remains unauthorized.

## Independent grade request

```text
PRODUCER_IDENTITY: Cursor Composer / Opus 4.8 created the initial draft; Codex materially produced R1 under Matt's exact authorization
PRODUCER_ROLE: DESIGN-lane producer chain; neither Cursor nor Codex may independently grade or accept R1
ARTIFACT_PATH: mmi/project_brain/status/MMI_TRUSTED_SUCCESSOR_CUSTODY_SPEC_2026-07-13.md
ARTIFACT_HASH: HOST_COMPUTED_AFTER_SERIALIZATION (bind exact output SHA-256 at grade time)
PRIOR_ARTIFACT_HASH_INVALIDATED_BY_R1: 7b3b7dd2442aa583ae1e933e0e2b900f180b170510d2a8d0269c1d8ac1a1ab80
R1_ARTIFACT_HASH_INVALIDATED_BY_R2: b42a34c944645d5b581317cce740ed64d539528ec74949feedbbe674c87465a7
CONTEXT_TARGET_HASH: bb2452925441cf2010bd5b3e69af54f7978013428ddad5f4592cbb6df90a95ce (GPG plan, HOST_ATTESTED)
PACKET_HASH: a6809606f856e4820a27e526e130944f492d7f2e37d0f09e68e460a50a1381af
LANE: DESIGN
GRADING_STANDARD: LLM_MODEL_AUDIT_STANDARD_2026-07.md + LLM_DESIGN_LAWS_2026-07.md (Law D5) + universal rubric
REQUIRED_REVIEWER_SEPARATION: reviewer must not have created or materially edited this artifact; Cursor may not self-grade
KNOWN_LIMITATIONS:
- git HEAD/remote/worktree and controlling-law hashes are HOST_ATTESTED (Codex bundle), not TOOL_RECOMPUTED by Cursor;
- model label is UI/session evidence, not provider-internal proof;
- design is documentation only; not implemented, not rehearsed, not legally reviewed;
- no successor named; several decisions are MATT_INPUT_REQUIRED / EXTERNAL_AUTHORITY_REQUIRED.
PRODUCER_COMPLETENESS_STATEMENT: all required output_format sections present; no cited law knowingly violated (this is not a self-grade).
```

## Boundaries and non-claims

- This spec is DESIGN/DOC-CONTROL only. It does not implement, test, rehearse, or legally establish anything.
- It does not name, select, contact, or rank any real successor, and requests no private information.
- It grants no access, no cryptographic permission, and does not authorize GPG-P1 or any later GPG phase.
- It does not weaken the GPG plan's phase separation, passphrase boundary, two-media independence, full-fingerprint rules, recurring tests, compatibility controls, or Matt-only authority.
- It does not provide legal, estate-planning, medical, or financial advice; it flags where a licensed professional and external legal authority are required.
- It does not prove recoverability, legal sufficiency, safety, or continuity.
- Cursor used no shell, subprocess, model delegation, or secret access in the initial design run. Codex used read-only shell verification for hashes, git state, and consistency while producing R1; no cryptographic operation, secret access, execution of project code, or write to another repository file occurred.
- This artifact is `INDEPENDENT_REVIEW_REQUIRED` and may not be self-graded, self-accepted, or promoted by its producer.

## Design verdict

This section is a producer completeness statement under Law D5, not an independent grade or acceptance.

Rationale: all required sections are present; the design respects and cites the controlling GPG plan and laws; it defines explicit roles, the required states, transitions with authority/evidence/expiry, fail-closed activation deferring legal/medical judgment to external authority, split control, anti-impersonation/coercion/replay controls, fixture-only rehearsal, incident handling, cadence, a public-safe manifest, failure modes/falsifiers, and a current residual-risk ledger. No universal dimension is MISSING and no cited law is knowingly violated, so the producer records ADEQUATE_DRAFT while leaving acceptance to an independent grader and Matt.

DESIGN_REVIEW_VERDICT = ADEQUATE_DRAFT
ARTIFACT_STATUS = DRAFT
ARTIFACT_ACCEPTANCE_STATUS = INDEPENDENT_REVIEW_REQUIRED
ARTIFACT_MAY_SELF_GRADE = NO
GPG_P1_AUTHORIZED = NO
SUCCESSOR_NAMED_OR_AUTHORIZED = NO
NEXT_DECISION_OR_LANE = INDEPENDENT_READ_ONLY_GRADE_OF_EXACT_OUTPUT_HASH
FORBIDDEN_ACTIONS_RECONFIRMED = YES
