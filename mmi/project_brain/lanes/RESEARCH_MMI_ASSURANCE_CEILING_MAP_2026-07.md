# RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07

**Project:** MMI / Architectapp  
**Lane:** Research only — no spec, no build, no gate closure  
**Status:** RESEARCH-DRAFT CLEAN (2026-07-04)  
**Authority repo:** `C:\Architectapp_clean`  
**Output path:** `mmi/project_brain/lanes/RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md`  
**Related active task:** `mmi-m4-evolution-gate`  
**Related spec:** M4 r2.5  
**Current pipe posture:** ACTIVE — evolution gate OUTSTANDING  
**Companion controls:** `mmi/project_brain/assurance/MMI_*_2026-07.md`

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
- "complete perfection" in an absolute philosophical sense

---

## 1. Purpose

This artifact defines the highest practical assurance ceiling for MMI in this lane.

The purpose is not to describe the next feature.

The purpose is to define the maximum standard this lane can defend with evidence.

The core thesis is:

- MMI becomes stronger by being more provable before it becomes more autonomous.
- Every claim must be bound to falsifiable evidence.
- Every promotion must be authority-bound.
- Every reviewer path must be treated as part of the trusted surface.

---

## 2. Ceiling definition

The ceiling in this lane is not "M4 passes."

The ceiling is:

- MMI becomes a cyber-assurance control plane where every claim, every patch proposal, every exploit capture, every risk reduction, and every promotion request is traceable to falsifiable evidence.

This is the strongest defensible perfection standard for a real system — not absolute philosophical perfection.

---

## 3. Current maturity location

| Ceiling | Meaning | MMI posture |
| ------- | ------- | ----------- |
| 1 — Test discipline | Repeatable tests, preserved failures | Partial |
| 2 — Containment discipline | Block, isolate, log, fail-closed | Active target |
| 3 — Evidence discipline | Tamper-evident lineage, summary binding | Active target |
| 4 — Assurance discipline | Claim/evidence/falsifier/residual risk | Under construction |
| 5 — Recovery discipline | Quarantine, rollback, no-promotion-after-failure | Incomplete |
| 6 — Self-improvement discipline | Proof-gated patches, human co-sign | Planned (AGI path) |
| 7 — Cyber-intelligence discipline | Bounded reasoning inside authority | Future target |
| 8 — Market-grade trust | External/pilot validation | Not reached |

---

## 4–11. Ceiling ladder detail

Full ceiling definitions, falsifiers, and forbidden claims for Ceilings 1–8 are implemented as mandatory companion controls:

| Section | Control artifact |
| ------- | ---------------- |
| §5.1 Invalidation registry | `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md` |
| §7 Reviewer failure | `MMI_REVIEWER_FAILURE_MODEL_2026-07.md` |
| §8 Operator signing | `MMI_OPERATOR_SIGNING_THREAT_MODEL_2026-07.md` |
| §9 Evidence-summary binding | `MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md` |
| §10 Recovery proof | `MMI_RECOVERY_PROOF_REQUIREMENTS_2026-07.md` |
| §11 Canary bypass | `MMI_CANARY_BYPASS_ACCEPTANCE_STANDARD_2026-07.md` |

---

## 12. Who checks blind spots (lane map)

No single reviewer catches everything. Blind-spot coverage is **distributed by lane** with explicit gaps recorded in the residual-risk ledger.

| Checker | What they catch | Blind spots they do **not** cover |
| ------- | --------------- | --------------------------------- |
| **Matt (authority)** | Scope, build auth, GATED, product/commercial direction, no-shortcuts rulings | Implementation bugs, full technical exhaust |
| **Codex** | Plan BUILDABLE, diff review, spec/implementation alignment | Runtime assault, market validation, operator psychology |
| **Claude** | Adversarial spec/contract review, architecture throw-back | Code-level bypasses, test execution |
| **ChatGPT / Gemini (research)** | Maturity framing, framework mapping, assurance doctrine | Build correctness, gate execution |
| **Cursor** | Implementation, tests, git — **not** self-approve assurance | Own implementation blind spots; requires Codex |
| **Completion gate (Grok/Gemini)** | Checklist gate closure — **not** Codex substitute | Novel adversarial vectors |
| **pytest / harness falsifiers** | Known-bad fixtures, regression | Unknown unknowns, social engineering |
| **Residual-risk ledger** | Inventory of **documented** open risks | Risks not yet inventoried |
| **External adversarial review** | Independent attack on claims | **Not scheduled yet** (RR-M4-024) |

**Rule:** a CLEAN in one lane is not CLEAN in all lanes. Reviewer failure modes are modeled explicitly because **reviewers are part of the attack surface**.

---

## 13. Lane-correct next moves

Control artifacts (filed 2026-07-04):

1. `RESEARCH_MMI_ASSURANCE_CEILING_MAP_2026-07.md` (this file)
2. `MMI_ASSURANCE_INVALIDATION_RULES_2026-07.md`
3. `MMI_REVIEWER_FAILURE_MODEL_2026-07.md`
4. `MMI_OPERATOR_SIGNING_THREAT_MODEL_2026-07.md`
5. `MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md`
6. `MMI_RECOVERY_PROOF_REQUIREMENTS_2026-07.md`
7. `MMI_CANARY_BYPASS_ACCEPTANCE_STANDARD_2026-07.md`

No runtime. No build authorization from this packet.

---

## 14. Final disposition

The ceiling path requires:

- no claim without evidence
- no evidence without lineage
- no promotion without human cryptographic authority
- no review without reviewer-failure controls
- no canary without bypass tests
- no summary without raw-artifact binding

That is the line between a strong test program and a defensible assurance system.

**Not claimed:** M4_MET, PERFECT, GATED, build authorization.
