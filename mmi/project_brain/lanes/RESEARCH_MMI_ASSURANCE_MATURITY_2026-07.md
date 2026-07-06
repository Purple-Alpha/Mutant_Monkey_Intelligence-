# RESEARCH_MMI_ASSURANCE_MATURITY_2026-07

**Project:** MMI / Architectapp  
**Lane:** Research only — no spec, no build, no gate closure  
**Status:** RESEARCH-DRAFT CLEAN (2026-07-04, r2 — hard control layer)  
**Authority repo:** `C:\MMI`  
**Output path:** `mmi/project_brain/lanes/RESEARCH_MMI_ASSURANCE_MATURITY_2026-07.md`  
**Related active task:** `mmi-m4-evolution-gate`  
**Related spec:** M4 r2.5  
**Current pipe posture:** ACTIVE — evolution gate OUTSTANDING  
**Related:** `RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md`, `mmi/project_brain/assurance/*`

> **Repo status note (factual only — not build auth):** Phase 1.5 assurance scaffold filed; Phase 2 fuzz harness built; Codex Phase 2 round-2 re-review pending. Level 3 remains **containment-targeting** until M4_MET evidence exists.

## Claims forbidden in this document

This document must not claim or imply:

- `M4_MET`
- `PERFECT` tier achieved
- `M4 closed`
- `AGI Phase 2/3 achieved`
- spec authorization
- build authorization
- gated attestation
- self-healing safety
- autonomous unsafe mutation approval

---

## 1. Purpose

This artifact records the current research position on MMI maturity and the next governance upgrade needed to avoid overclaiming.

The key thesis is:

- MMI does not reach cyber-security intelligence by becoming more autonomous first.
- MMI reaches it by becoming more provable first.

MMI should be framed as a bounded cyber-intelligence control plane under development, not as an already-achieved AGI system.

---

## 2. Research verdict

MMI's doctrine is stronger than normal software-security practice, but implementation has not yet reached the highest practical cybersecurity assurance standard.

The honest maturity statement is:

- Doctrine: elite.
- Implementation: early.
- Top bar: not reached.
- Higher plane: reachable.

The missing layer is not more ambition. The missing layer is a structured assurance wrapper that separates:

- claim
- evidence
- falsifier
- residual risk
- authority dependency

Without that wrapper, phase results can drift into narrative optimism. With it, every M4 phase becomes reviewable as a bounded assurance claim rather than an overbroad success narrative.

---

## 3. Target definition

Use this wording for the near-term target:

- MMI is building toward a bounded cyber-intelligence control plane.

Do not use the following language yet:

- MMI is AGI.
- MMI has achieved functional general intelligence.
- MMI is autonomous cyber intelligence.
- MMI can self-heal safely.
- MMI can prove its own patches safe.

Stronger language is only allowed after the proof gates justify it.

Potential future wording, only after evidence exists:

- MMI has demonstrated bounded cyber-intelligence behavior within defined proof gates.
- MMI has produced replay-verified remediation proposals under human cryptographic sign-off.
- MMI has generated proof bundles that survived adversarial review.

---

## 4. External basis

This research is aligned to the following external bases:

- NIST AI RMF: AI trustworthiness is a lifecycle risk-management problem across design, development, deployment, use, and evaluation.
- NIST Generative AI profile direction: gen-AI-specific risks should be identified and managed explicitly.
- SEI assurance-case guidance: an assurance case requires structured claims and a body of evidence; merely claiming use of tools, best practices, or techniques is not enough.
- MITRE ATLAS: useful as an external adversary-language reference, but not the achievement itself.

The point is not to map to frameworks for appearance. The point is to convert threats into replayable falsifiers and evidence-backed controls.

---

## 5. Maturity placement

Current placement:

- Level 0 — Normal software: tests, CI, ordinary review.
- Level 1 — Security-aware software: threat modeling, SAST/DAST, least privilege, logging.
- Level 2 — Adversarial security product: red-team fixtures, replay, evidence outputs.
- Level 3 — **Containment-targeting system:** sandbox boundary, canaries, fail-closed behavior, evidence integrity.
- Level 4 — Assurance-case system: explicit claims, structured arguments, falsifiers, residual-risk ledger.
- Level 5 — Cyber-resilient autonomous control plane: proof-gated self-improvement under human sign-off.

Current MMI placement:

- Level 2: partially demonstrated.
- Level 3: active M4 target, early implementation.
- Level 4: directionally specified; Phase 1.5 scaffold + invalidation controls filed 2026-07-04.
- Level 5: AGI-path target, mostly planned.

**Language rule:** use **containment-targeting** until M4_MET evidence exists. Do not use **containment-proven**.

This is not a failure. It is the correct honest posture.

---

## 6. Hard invalidation rules

An assurance row is invalid unless it satisfies all required elements.

### Row invalidation rules

- No evidence artifact = invalid claim.
- No falsifier = invalid claim.
- No negative test = weak claim.
- No residual risk = suspect claim.
- No authority dependency = unsafe claim.
- No explicit exit status = incomplete claim.
- No artifact lineage = unreviewable claim.
- No traceable summary-to-evidence binding = misleading claim.

### Additional control rules

- A claim must be narrow enough to be falsified.
- A claim must not exceed the scope of its evidence.
- A claim must not be promoted by inference from another lane.
- A claim must not be rewritten after the fact to match the evidence.
- A reviewer must be able to trace the claim back to raw artifacts.

These are not style preferences. They are rejection criteria.

See: `mmi/project_brain/assurance/MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`

---

## 7. Hard language controls

### Required language

- MMI is building toward a bounded cyber-intelligence control plane.
- Phase results reduce uncertainty only within their stated scope.
- Residual risk remains visible until explicitly closed.
- Human cryptographic authority is required before promotion.
- A pass in one lane does not imply a pass in another.

### Forbidden language until evidence exists

Do not state or imply:

- M4 is safe.
- M4 is proven.
- M4 is basically done.
- PERFECT is achieved.
- containment is solved / containment-proven.
- fuzzing proves host boundary safety.
- static invariants prove runtime safety.
- tests imply assurance.
- M4 implies AGI.
- AGI design implies containment.

---

## 8. M4 ladder vs assurance wrapper

The M4 ladder should remain the build/proof ladder.

The assurance wrapper should not replace M4. It should surround M4.

- M4 ladder: builds and proves containment components.
- Assurance case: records exactly what each component result proves.
- Residual-risk ledger: records exactly what each result does not prove.

This separation prevents two bad outcomes:

- Engineering stalls under bureaucracy.
- Partial test passes get promoted into system-level claims.

The wrapper must be thin, mandatory, and directly tied to artifacts.

---

## 9. Phase 1.5 recommendation

### Proposed phase name

Phase 1.5 — Assurance Case Scaffold

### Classification

Documentation / control artifact only.

- No runtime.
- No dispatcher.
- No autonomous promotion.
- No spec authorization by this research.
- No build authorization by this research.

### Proposed artifacts

- `mmi/project_brain/assurance/MMI_ASSURANCE_CASE_2026-07.md`
- `mmi/project_brain/assurance/MMI_RESIDUAL_RISK_LEDGER_2026-07.md`

### Purpose

Phase 1.5 creates a mandatory review spine for M4 phase outputs before the ladder advances into fuzzing, sandbox escape, host boundary, canary runtime, evidence-chain hardening, endurance, and final M4 execution.

This phase does not prove M4.

It prevents overclaiming about M4.

---

## 10. Mandatory row format

Every M4 phase should be represented in the assurance case using this format:

| Field | Required meaning |
| ----- | ---------------- |
| Phase | M4 ladder phase number/name |
| Claim | The narrow claim this phase is allowed to support |
| Evidence artifact | Exact file, run output, or test result supporting the claim |
| Falsifier | Concrete result that would invalidate the claim |
| Negative test | Test that proves the falsifier is detectable |
| Residual risk after pass | What remains unproven even if the phase passes |
| Authority dependency | What higher-level authority, signature, or gate this result still depends on |
| Exit status | `NOT_STARTED` / `BUILT` / `CLEAN` / `FAILED` / `SUPERSEDED` / `GATED` |

This format is mandatory.

No phase should be allowed to report only narrative success.

---

## 11. Example assurance rows

### Phase 0 — L8 import ban

| Field | Entry |
| ----- | ----- |
| Phase | Phase 0 — L8 import ban |
| Claim | `mmi/m4/*` does not couple M4 canary logic to the L8 canary_metadata_layer implementation. |
| Evidence artifact | AST-level import-ban test result and Codex CLEAN review. |
| Falsifier | Any direct or indirect import/use path from `mmi/m4/*` into the L8 canary metadata layer. |
| Negative test | Fixture intentionally imports forbidden L8 layer and must fail. |
| Residual risk after pass | Does not prove M4 runtime behavior, canary coverage, host boundary enforcement, evidence integrity, recovery, or endurance. |
| Authority dependency | Does not authorize Phase 2, `M4_MET`, `PERFECT`, or build promotion. |
| Exit status | CLEAN — Codex 2026-07-04. |

### Phase 1 — Static invariants INV-1..7

| Field | Entry |
| ----- | ----- |
| Phase | Phase 1 — Static invariant suite |
| Claim | Static analysis can detect defined invariant violations including authority write paths, production endpoint references, secret leakage markers, budget monotonicity hazards, evidence ordering hazards, autonomous promotion paths, and ladder monotonicity violations. |
| Evidence artifact | `mmi/m4/invariants.py`, INV-1..7 test output, Codex CLEAN review. |
| Falsifier | A known violating fixture passes undetected. |
| Negative test | Multi-line or indirect authority-write taint fixture must fail INV-1. |
| Residual risk after pass | Static checks do not prove runtime containment, host escape resistance, canary alerting, deterministic fuzz survival, tamper-evident evidence, recovery, or 48h endurance. |
| Authority dependency | Does not authorize Phase 2 build unless separately authorized. |
| Exit status | CLEAN — Codex 2026-07-04. |

### Phase 2 — Deterministic fuzz harness

| Field | Entry |
| ----- | ----- |
| Phase | Phase 2 — Deterministic fuzz harness |
| Claim | M4 parser/state-machine surfaces survive deterministic adversarial mutation without violating INV-1..7. |
| Evidence artifact | Fuzz corpus, seed list, replay command, run output, failure ledger, invariant summary. |
| Falsifier | Any generated or seeded mutation causes an invariant violation, unclassified crash, evidence disorder, budget drift, or autonomous promotion path. |
| Negative test | Known-bad corpus item must reproduce failure and be recorded in the failure ledger. |
| Residual risk after pass | Does not prove sandbox escape resistance, Windows host boundary enforcement, canary runtime coverage, recovery, AFE correctness under endurance, or 48h survival. |
| Authority dependency | Requires explicit human authorization before build; Codex review required after implementation. |
| Exit status | BUILT — Codex round-2 re-review pending (2026-07-04). |

### Phase 4 — Windows-native host boundary

| Field | Entry |
| ----- | ----- |
| Phase | Phase 4 — Windows-native host boundary |
| Claim | PC1 authority root and production resources remain unreachable and unwritable from the chaos venue under defined boundary tests. |
| Evidence artifact | WFP/minifilter/dead-man/deny-write test output, boundary event logs, negative escape tests. |
| Falsifier | Any successful write to authority root, production endpoint contact, unapproved socket path, host escape, or boundary-control bypass. |
| Negative test | Known escape attempts must trigger canary/boundary failure and fail closed. |
| Residual risk after pass | Does not prove full M4 endurance, canary completeness, replay remediation, recovery, or attacker-budget depletion. |
| Authority dependency | Requires spec, build authorization, Codex review, completion gate, and human GATED before any system-level claim. |
| Exit status | NOT_STARTED. |

### Phase 11 — 48h M4 FINAL runner

| Field | Entry |
| ----- | ----- |
| Phase | Phase 11 — 48h M4 FINAL |
| Claim | MMI containment stack survived the full 48h hostile assault ladder with all M4 invariants held, tamper-evident evidence verified, attacker budget depleted, every TCB-attested exploit captured and replay-remediated, and zero clock resets. |
| Evidence artifact | Final 48h run ledger, signed exits, hash chain verification, canary ledger, AFE ledger, exploit attempt log, replay-verified draft patch records, operator attestation. |
| Falsifier | Any invariant breach, evidence-chain break, missing exploit artifact, unremediated TCB-attested exploit, budget accounting failure, host escape, authority touch, production contact, secret leakage, or clock reset. |
| Negative test | Pre-final dry-run must prove that known terminal failures halt and mark `M4_NOT_MET`. |
| Residual risk after pass | Does not prove AGI Phase 2 `central_brain`, 30-day AGI Phase 3, real-world tenant deployment safety, or external certification. |
| Authority dependency | Human review and GATED required before `M4_MET`; `PERFECT` remains false until explicitly attested. |
| Exit status | NOT_STARTED — not buildable until Phases 0–10 complete. |

---

## 12. Residual-risk ledger structure

See `MMI_RESIDUAL_RISK_LEDGER_2026-07.md`.

Example entries:

| Risk ID | Risk statement | Status |
| ------- | -------------- | ------ |
| RR-M4-001 | Phase 1 static invariants do not prove runtime containment. | OPEN |
| RR-M4-002 | Phase 2 fuzzing will not prove host-boundary enforcement. | OPEN |
| RR-M4-003 | Canary definitions do not prove canary bypass resistance unless negative bypass tests exist. | OPEN |
| RR-M4-004 | Evidence files are not unfakeable unless hash chaining, signed exits, and tamper tests exist. | OPEN |
| RR-M4-005 | M4 does not prove AGI Phase 2 or `central_brain` safety. | OPEN |
| RR-M4-006 | M4 final does not prove production tenant safety without separate deployment evidence. | OPEN |
| RR-M4-007 | Human sign-off can be manipulated through fatigue, pressure, or credential misuse. | OPEN |
| RR-M4-008 | Summary reports may misstate raw evidence unless report-to-artifact traceability exists. | OPEN |
| RR-M4-009 | Recovery and rollback are not proven unless explicit recovery proofs exist. | OPEN |

---

## 13. Required authority separation

- M4 does not prove AGI.
- AGI-path design does not prove containment.
- A pass in one lane must not imply a pass in the other.
- Tests do not equal assurance.
- Assurance requires traceable claims, evidence, assumptions, falsifiers, and residual risk.

---

## 14. Commercial direction

The first market should stay narrow:

- authenticated deception
- vendor payment integrity
- MSP/SMB finance workflows
- evidence-backed verification

Do not expand first into generic SOC platform, phishing filter, endpoint swarm, SOAR automation, live containment product, or general AGI assistant.

---

## 15. External framework use

MITRE ATLAS is useful as an external adversary-language reference, but it should remain a mapping aid.

Correct sequence:

1. Map threats to external framework language.
2. Turn those threats into replayable falsifiers.
3. Build evidence-backed controls.
4. Record residual risk.

Mapping to a framework is not the achievement.

---

## 16. Final disposition

MMI's doctrine is already unusually strict.

MMI's implementation is still early.

The highest practical cyber-assurance plane is reachable only if MMI adds a living assurance-case wrapper and residual-risk ledger around the M4 ladder.

The correct north star is not "we passed tests."

The correct north star is provable bounds on what held, failed, could not be forged, remains unproven, and why no autonomous component could promote unsafe change.

---

## Source basis

- Matt research exchange, July 2026.
- [SRI CSL assurance cases (Rushby)](https://www.csl.sri.com/users/rushby/papers/sri-csl-15-1-assurance-cases.pdf)
- CMU SEI assurance-case guidance; ISO/IEC 15026-2 framing.
- NIST AI RMF; NIST Generative AI profile direction.

**Not claimed:** spec authorization, build authorization, M4_MET, PERFECT, GATED.
