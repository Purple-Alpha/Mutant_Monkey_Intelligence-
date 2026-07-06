# MMI Assurance Gate Invalidation Addendum

**Project:** MMI / Architectapp  
**Artifact role:** Assurance hardening — gate-level invalidation (authoritative for closure/promotion)  
**Lane:** Documentation/control only — no spec, no build, no gate closure  
**Status:** r2 HARDENING (2026-07-04)  
**Authority repo:** `C:\MMI`  
**Applies to:** All `mmi/project_brain/assurance/MMI_*_2026-07.md`  
**Supersedes for gate closure:** ambiguous outcomes in `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md` §Downgrade where this addendum defines a default  
**Research-control ceiling:** RESEARCH-DRAFT CLEAN — machine enforcement is a **future spec/build path**, not this lane

**Forbidden claims:** M4_MET, PERFECT, GATED, build authorization, containment-proven.

---

## r1 baseline (summary)

r1 converted assurance expectations into hard rejection rules. Row-level checks live in `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`. **r2 below** is authoritative for gate closure, promotion, stale evidence, scope freeze, reviewer disagreement, and review-chain compromise.

**Core r2 rule:**

```text
Every invalidator must map to exactly one default outcome.
Downgrade is allowed only where this file explicitly defines downgrade as the default outcome.
```

---

# r2 HARDENING PATCH

## r2 purpose

This patch removes ambiguity from the assurance invalidation model.

The r1 addendum converted assurance expectations into hard rejection rules. r2 tightens the model further by requiring deterministic outcomes, explicit stale-evidence handling, scope freeze, reviewer-disagreement states, and review-chain compromise states.

---

## 1. Deterministic invalidation outcomes

Allowed outcomes:

| Outcome | Meaning |
| ------- | ------- |
| `REJECT_CLAIM` | Claim cannot be used, cited, summarized, or promoted. |
| `REJECT_PHASE_PASS` | Phase cannot be marked pass/clean/closed. |
| `REJECT_GATE_CLOSURE` | Gate cannot close. |
| `REJECT_SUMMARY` | Human-readable summary cannot stand. |
| `REOPEN_RISK` | Previously closed/reduced risk must be reopened. |
| `STALE_REVIEW_REQUIRED` | Evidence is not rejected yet, but cannot support new claim until reviewed. |
| `WEAK_CLAIM_REQUIRES_REVIEW` | Claim may be retained only as weak/non-closing research note. |
| `COMPROMISED_REVIEW_PATH` | Review chain is suspect; all dependent claims freeze pending operator review. |
| `REVIEWER_DISAGREEMENT_OPEN` | Conflicting reviewer conclusions block closure. |
| `SCOPE_DRIFT_REVIEW_REQUIRED` | Claim scope changed or artifact set changed; old claim cannot carry forward. |

Forbidden ambiguous outcomes:

```text
reject or downgrade
reject if severe
needs review maybe
acceptable with caution
probably okay
directionally valid
```

If severity judgment is required, the default outcome is:

```text
REJECT_CLAIM
```

unless this addendum explicitly permits a weaker state.

---

## 2. Updated global invalidator table

| ID | Invalidator | Default outcome |
| -- | ----------- | --------------- |
| G-INVAL-001 | No raw evidence artifact | `REJECT_CLAIM` |
| G-INVAL-002 | No artifact hash or lineage | `REJECT_CLAIM` |
| G-INVAL-003 | No falsifier | `REJECT_CLAIM` |
| G-INVAL-004 | No negative test for falsifier | `WEAK_CLAIM_REQUIRES_REVIEW` |
| G-INVAL-005 | No residual-risk link | `REJECT_PHASE_PASS` |
| G-INVAL-006 | No authority dependency | `REJECT_CLAIM` |
| G-INVAL-007 | No reviewer identity | `REJECT_GATE_CLOSURE` |
| G-INVAL-008 | No summary-to-artifact reconstruction path | `REJECT_SUMMARY` |
| G-INVAL-009 | No explicit scope boundary | `REJECT_CLAIM` |
| G-INVAL-010 | Claim exceeds evidence scope | `REJECT_CLAIM` |
| G-INVAL-011 | Claim borrows authority from another lane | `REJECT_CLAIM` |
| G-INVAL-012 | Claim relies on stale evidence | `STALE_REVIEW_REQUIRED` |
| G-INVAL-013 | Claim uses `CLEAN` as broad safety language | `REJECT_SUMMARY` |
| G-INVAL-014 | Claim omits remaining residual risk | `REJECT_SUMMARY` |
| G-INVAL-015 | Missing or ambiguous human authority metadata | `REJECT_GATE_CLOSURE` |
| G-INVAL-016 | Reviewer conclusions conflict | `REVIEWER_DISAGREEMENT_OPEN` |
| G-INVAL-017 | Review path suspected compromised | `COMPROMISED_REVIEW_PATH` |
| G-INVAL-018 | Artifact set changed after claim | `SCOPE_DRIFT_REVIEW_REQUIRED` |
| G-INVAL-019 | Summary text changed after binding | `REJECT_SUMMARY` |
| G-INVAL-020 | Authority metadata lacks exact evidence set ID | `REJECT_GATE_CLOSURE` |

---

## 3. Stale evidence rule

Evidence becomes stale if any of the following occur:

| Staleness trigger | Outcome |
| ----------------- | ------- |
| Branch changed after evidence was produced | `STALE_REVIEW_REQUIRED` |
| Artifact content changed after review | `STALE_REVIEW_REQUIRED` |
| Artifact hash no longer matches bound claim | `REJECT_CLAIM` |
| Dependency changed after test/review | `STALE_REVIEW_REQUIRED` |
| Spec section changed after claim was made | `SCOPE_DRIFT_REVIEW_REQUIRED` |
| Test fixture changed after result was cited | `STALE_REVIEW_REQUIRED` |
| Review output references superseded artifact | `STALE_REVIEW_REQUIRED` |
| Evidence time window does not cover claim window | `REJECT_CLAIM` |

Rule:

```text
Stale evidence may remain historical evidence.
Stale evidence may not support a new, current, closing, gate, or promotion claim.
```

---

## 4. Scope freeze rule

Every assurance claim must bind to a frozen scope.

Required scope fields:

| Field | Required |
| ----- | -------- |
| Claim ID | Yes |
| Evidence set ID | Yes |
| Artifact paths | Yes |
| Artifact hashes | Yes |
| Branch/ref | Yes |
| Spec section/version | Yes |
| Test command/run ID | Yes, where applicable |
| Reviewer identity | Yes, where applicable |
| Residual-risk snapshot ID | Yes |
| Authority metadata ID | Yes, for gate/promotion claims |

Hard rule:

```text
If the artifact set changes, the old claim does not silently carry forward.
```

Outcome:

```text
SCOPE_DRIFT_REVIEW_REQUIRED
```

Scope drift examples:

```text
same test name, changed fixture
same artifact path, changed file hash
same phase label, changed spec requirement
same review label, different artifact set
same summary, different raw evidence
```

---

## 5. Evidence set ID requirement

Gate, closure, and promotion claims must reference an exact evidence set ID.

Minimum evidence set fields:

| Field | Required |
| ----- | -------- |
| Evidence set ID | Yes |
| Included artifact paths | Yes |
| Artifact hashes | Yes |
| Run/test IDs | Yes, where applicable |
| Time window | Yes |
| Branch/ref | Yes |
| Spec version | Yes |
| Reviewer outputs | Yes, where applicable |
| Residual-risk snapshot | Yes |
| Summary binding ID | Yes, if summarized |
| Authority metadata ID | Yes, for gate/promotion |

Invalid authority pattern:

```text
Matt approved the phase.
```

Valid authority pattern:

```text
Matt approved evidence set EV-M4-PHASE2-2026-07-XX under scope SCOPE-M4-PHASE2-STATIC-FUZZ-ONLY with residual-risk snapshot RR-SNAP-2026-07-XX. Approval does not imply M4_MET, PERFECT, containment proof, AGI proof, or production readiness.
```

---

## 6. Reviewer disagreement state

Reviewer disagreement is not a nuisance. It is a first-class assurance state.

Trigger:

```text
Two or more reviewers produce conflicting conclusions about the same claim, artifact set, scope, or residual risk.
```

Outcome:

```text
REVIEWER_DISAGREEMENT_OPEN
```

While this state is open:

- no gate closure
- no GATED claim
- no phase closure
- no promotion
- no summary may present the issue as resolved
- residual-risk ledger must record the disagreement

Required disagreement record:

| Field | Required |
| ----- | -------- |
| Disagreement ID | Yes |
| Claim ID | Yes |
| Evidence set ID | Yes |
| Reviewer A conclusion | Yes |
| Reviewer B conclusion | Yes |
| Conflict summary | Yes |
| Blocking effect | Yes |
| Required resolution evidence | Yes |
| Matt ruling, if resolved | Required for closure |

Allowed resolution paths:

```text
additional evidence
narrowed claim
residual risk reopened
Matt ruling with explicit scope
external review
claim rejection
```

Forbidden resolution path:

```text
choose the more optimistic reviewer because it preserves momentum
```

---

## 7. Review-chain compromise state

The review chain itself is part of the attack surface.

Triggers for suspected compromise:

| Trigger | Outcome |
| ------- | ------- |
| Review output lacks identity/scope/artifact set | `COMPROMISED_REVIEW_PATH` |
| Review result references missing artifacts | `COMPROMISED_REVIEW_PATH` |
| Review result contradicts raw evidence | `COMPROMISED_REVIEW_PATH` |
| Review result appears copied from summary without raw artifact review | `COMPROMISED_REVIEW_PATH` |
| Reviewer approves outside assigned lane | `COMPROMISED_REVIEW_PATH` |
| Review result changes after publication without trace | `COMPROMISED_REVIEW_PATH` |
| Gate relies on single reviewer where cross-review is required | `REJECT_GATE_CLOSURE` |
| Suspicious operator pressure, fatigue, spoofing, or credential anomaly | `COMPROMISED_REVIEW_PATH` |

While `COMPROMISED_REVIEW_PATH` is open:

- freeze dependent claims
- no gate closure
- no GATED claim
- no promotion
- no summary may cite compromised review as valid
- residual-risk ledger must record the compromise suspicion
- Matt must rule before dependent claims can be used again

Required compromise record:

| Field | Required |
| ----- | -------- |
| Compromise ID | Yes |
| Affected reviewer/lane | Yes |
| Affected claim IDs | Yes |
| Affected evidence set IDs | Yes |
| Trigger | Yes |
| Blocking effect | Yes |
| Required cleanup evidence | Yes |
| Matt ruling | Required for resolution |

---

## 8. Cross-review default rule

Gate-level closure requires cross-review by default.

Minimum cross-review for gate closure:

```text
one implementation/diff reviewer
one adversarial/spec reviewer
one authority/operator ruling
```

Typical lane mapping:

| Role | Function |
| ---- | -------- |
| Codex | implementation/diff/plan bounded review |
| Claude or research lane | adversarial/spec/claim critique |
| Matt | authority and no-shortcuts ruling |

Waiver rule:

```text
Cross-review may be waived only by explicit Matt ruling with recorded justification, exact scope, residual-risk snapshot, and forbidden implied claims.
```

A waiver without recorded justification is invalid.

Outcome:

```text
REJECT_GATE_CLOSURE
```

---

## 9. Summary text hash binding

The summary itself must be bound, not only the raw evidence.

Required summary-binding fields:

| Field | Required |
| ----- | -------- |
| Summary ID | Yes |
| Summary text hash | Yes |
| Raw artifact evidence set ID | Yes |
| Artifact hashes | Yes |
| Claim IDs summarized | Yes |
| Residual-risk snapshot ID | Yes |
| Scope boundary | Yes |
| Author/reviewer | Yes |
| Timestamp | Yes |

Hard rule:

```text
If the summary text changes, the summary binding is invalid until rehashed and re-reviewed.
```

Outcome:

```text
REJECT_SUMMARY
```

This prevents later rewriting of a cautious summary into a stronger claim while keeping the same evidence references.

See also: `MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md`

---

## 10. Recovery not-triggered evidence

Recovery proof has two valid states:

```text
RECOVERY_TRIGGERED_PROVEN
RECOVERY_NOT_TRIGGERED_ATTESTED
```

Invalid state:

```text
recovery not mentioned
```

For any endurance or hostile-assault run, the record must state whether recovery was triggered.

If recovery was triggered, required proof includes:

- quarantine proof
- rollback/reset proof
- credential handling proof, where applicable
- evidence preservation proof
- dead-man/no-promotion proof
- post-failure state proof

If recovery was not triggered, required evidence includes:

- run ID
- time window
- monitored recovery triggers
- assertion that no trigger fired
- evidence artifact supporting no trigger
- reviewer identity

Hard rule:

```text
No recovery triggered/not-triggered record, no endurance claim.
```

Outcome:

```text
REJECT_CLAIM
```

See also: `MMI_RECOVERY_PROOF_REQUIREMENTS_2026-07.md`

---

## 11. Internal proof / external trust placement

Internal proof, external reviewer confidence, and customer proof are separate.

| Lane | Supports | Does not support |
| ---- | -------- | ---------------- |
| Internal M4 proof | clone-scope containment/evidence claims | customer value, external certification, production trust |
| External adversarial review | independent confidence in reviewed claims | customer usefulness, market fit |
| MSP/customer pilot | workflow usefulness and evidence-package value | M4 containment, AGI safety, host-boundary proof |

Hard rule:

```text
Internal proof does not equal external trust.
External review does not equal customer value.
Customer value does not equal containment proof.
```

Any summary that collapses these lanes is rejected.

Outcome:

```text
REJECT_SUMMARY
```

---

## 12. Final r2 disposition

This r2 patch hardens the addendum from:

```text
required fields plus rejection rules
```

to:

```text
deterministic failure states with frozen scope, exact evidence sets, stale-evidence handling, reviewer-disagreement handling, and review-chain compromise handling
```

The highest standard remains:

```text
MMI can prove exactly what held,
exactly what failed,
exactly what could not be forged,
exactly what remains unproven,
and exactly why no autonomous component could promote unsafe change.
```

Until repo evidence satisfies these rules, MMI remains **containment-targeting**, not containment-proven.

---

## Next gap (not this lane)

Policy-defined controls end here. **Machine-checkability** (schemas, `mmi_assurance_validate.py`) requires separate Matt spec/build authorization — e.g. `MMI_ASSURANCE_SCHEMA_AND_VALIDATOR_SPEC_2026-07.md`.

**Not claimed:** spec authorization, build authorization, gate closure, M4_MET, PERFECT, GATED.
