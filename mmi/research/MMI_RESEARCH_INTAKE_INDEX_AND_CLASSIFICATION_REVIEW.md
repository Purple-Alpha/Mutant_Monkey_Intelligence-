# MMI Research Intake Index and Classification Review

**Classification:** `GOVERNANCE_INDEX` · `CLASSIFICATION_REVIEW` · `DRIFT_CONTROL` · `NOT_AUTHORITY` · `NOT_DOCTRINE` · `NOT_SUCCESS_DEFINITION` · `NOT_PATH_SELECTION` · `NOT_BUILD_AUTHORIZATION` · `NEEDS_PERIODIC_RE_REVIEW`

**Status:** Meta-governance register only. Gate read: READY FOR CURSOR PLACEMENT.

**Owner:** MMI governance (human-maintained)

**Created:** 2026-06-19

**Reconciled against disk:** 2026-06-19 via `find mmi/research -maxdepth 1 -type f`

**Concepts register (sibling, not duplicate):** `mmi/concepts/MMI_CONCEPTS_INTAKE_INDEX_AND_CLASSIFICATION_REVIEW.md` (MMI-DEC-113).

---

## 1. Title

MMI Research Intake Index and Classification Review

---

## 2. Authority status

**Gate read:**

```text
MMI_RESEARCH_INTAKE_INDEX_AND_CLASSIFICATION_REVIEW
Status: READY FOR CURSOR PLACEMENT
Authority: governance index / classification review only
Risk control: strong
Build authorization: none
Success definition: none
Path selection: none
```

This file is a **governance index and classification review only**.

It is **not** routing authority, **not** doctrine, **not** an MMI success definition, **not** path selection, and **not** build authorization.

It does **not** promote any research note to authority. It does **not** unlock AUTH-5 or registry-fed routing.

---

## 3. Purpose

`mmi/research/` holds operator and second-opinion **input** — not project truth.

This index:

- registers every file currently under `mmi/research/`
- assigns each note an **influence ceiling** (maximum allowed influence, not current influence)
- pins all listed notes as **input, not authority**
- provides drift-control rules before more research/intake accumulates

**Indexing does not promote.** Listing a note here does not increase its authority.

---

## 4. Influence ceiling vocabulary

| Tag | Meaning |
|---|---|
| `CYBER_INTELLIGENCE_INPUT` | Cyber security intelligence framing only; not detection build authority |
| `SUCCESS_DEFINITION_INPUT` | Candidate success/evolution framing only; not defined success |
| `PROJECT_LINEAGE_INPUT` | Lineage/exploration framing only; not project identity |
| `CONCEPT_INPUT` | Concept capture only; not adoption |
| `EXPLICITLY_NOT_DOCTRINE` | Must not be read as doctrine |
| `NEEDS_FUTURE_REVIEW` | Classification or promotion path unresolved |
| `ZERO_ROUTING_INFLUENCE` | Must not feed dispatcher, registry routing, or scoreboard selection |

Default ceiling for all intake notes: **input only, zero routing influence**.

---

## 5. Drift-control rules

1. **Input stays input.** Placement in `mmi/research/` never implies adoption.
2. **No silent promotion.** A note cannot graduate to doctrine, identity, success, or build scope without explicit operator gate and appropriate signed artifact.
3. **Class is a ceiling.** Tags state maximum allowed influence, not earned influence.
4. **Strength does not equal selection.** Persuasive language in a note does not rank it above other notes or above repo evidence.
5. **Aggregation is not authority.** Multiple related intake notes do not combine into doctrine by accumulation.
6. **Metaphor is not fact.** Organism, brain, immune system, lung, and being language remains conceptual until falsifiable architecture review.
7. **Indexing does not promote.** This register classifies; it does not authorize.
8. **Research convergence requires separate review.** Before any research cluster may influence doctrine, identity, success definition, or build direction, Matt must authorize a separate review gate (consequence matrix / §11-bound process as applicable). No convergence by default.

---

## 6. Live register — reconciled against `mmi/research/`

**Reconciliation command:** `find mmi/research -maxdepth 1 -type f -print | sort`

**Files found at reconciliation (2026-06-19):** 4 intake notes (+ this index file added by this placement)

| File | MMI record | Classification tags | Influence ceiling | Summary |
|---|---|---|---|---|
| `MMI_CYBER_SECURITY_INTELLIGENCE_INPUT_APT29_ENVYSCOUT.md` | MMI-DEC-033; INTAKE-2026-06-19-013 | `CYBER_INTELLIGENCE_INPUT` · `CONCEPT_INPUT` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_FUTURE_REVIEW` | Input only; zero routing influence | APT29/EnvyScout example: data vs indicator vs intelligence; behavior durability |
| `MMI_SUCCESS_EVOLUTION_ROADMAP_INTAKE.md` | MMI-DEC-034; INTAKE-2026-06-19-014 | `SUCCESS_DEFINITION_INPUT` · `PROJECT_LINEAGE_INPUT` · `CONCEPT_INPUT` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_FUTURE_REVIEW` | Input only; zero routing influence | Candidate phased roadmap; Phase 1–4 not authorized; success deferred |
| `MMI_ADAPTIVE_CYBER_INTELLIGENCE_ORGANISM_CONCEPT_INTAKE.md` | MMI-DEC-035; INTAKE-2026-06-19-015 | `CONCEPT_INPUT` · `CYBER_INTELLIGENCE_INPUT` · `PROJECT_LINEAGE_INPUT` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_FUTURE_REVIEW` | Input only; zero routing influence | Second-opinion organism framing; Capture ≠ adoption |
| `MMI_PROJECT_LINEAGE_AND_EXPLORATION_INTAKE.md` | MMI-DEC-036; INTAKE-2026-06-19-016 | `PROJECT_LINEAGE_INPUT` · `SUCCESS_DEFINITION_INPUT` · `CONCEPT_INPUT` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_FUTURE_REVIEW` | Input only; zero routing influence | 8-step lineage; cybersecurity/insurance not whole-project labels; exploration mode |
| `MMI_RESEARCH_INTAKE_INDEX_AND_CLASSIFICATION_REVIEW.md` | MMI-DEC-037; INTAKE-2026-06-19-017 | `GOVERNANCE_INDEX` · `CLASSIFICATION_REVIEW` · `DRIFT_CONTROL` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_PERIODIC_RE_REVIEW` | Meta only; zero routing influence | This register; classifies other notes; does not promote them |
| `MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md` | MMI-DEC-131; INTAKE-2026-06-24-004 | `RESEARCH_INPUT` · `ADVISORY_MEMO` · `EXPLICITLY_NOT_DOCTRINE` · `ZERO_ROUTING_INFLUENCE` | Input only; zero routing influence | Stage A a05 mesh hardening closeout; federation addendum research gaps closed; not build authority |
| `MMI_ELASTIC_ORGANISM_SCALING_RESEARCH_ABSORPTION.md` | MMI-RES-2026-06-24 | `RESEARCH_INPUT` · `ADVISORY_MEMO` · `EXPLICITLY_NOT_DOCTRINE` · `ZERO_ROUTING_INFLUENCE` | Input only; zero routing influence | External scaling paradigms triage: KEEP topology morphing + tenant context-folding; DISCARD stigmergy + holonic; no spine pivot |
| `MMI_STAGE_C_GOVERNED_ORGANISM_CLOSEOUT_MMI-DEC-150.md` | MMI-DEC-150 · §11 signed 2026-06-24 | `CLOSEOUT_RECORD` · `STAGE_END` · `OPERATOR_FORK` | Stage C end; not build authorization | Narrow ACCEPT: program direction yes, production organism no; c01 PARK + c02 plan acknowledged; hybrid depth-first execution |

**Reconciliation rule:** On every update to this index, re-run the `find` command and ensure every `mmi/research/*.md` intake or governance file is listed. Do not ship a partial register.

**Notes with uncertain classification:** None at reconciliation time. If a future file cannot be confidently classified, tag `NEEDS_FUTURE_REVIEW` and set influence ceiling to zero.

---

## 7. Promotion boundaries (none authorized)

No note in Section 6 may, by virtue of being listed here:

- become doctrine or §11-bound spec text
- define MMI or project success
- select scoreboard or dispatcher path
- authorize build, AUTH-5, or registry-fed routing
- mutate `mmi/MMI_TASK_REGISTRY.yaml`
- override signed Tier 1–2C contracts

Promotion requires **separate explicit operator authorization** and the appropriate signed artifact.

---

## 8. Periodic re-review requirement

This index carries `NEEDS_PERIODIC_RE_REVIEW`.

Re-review triggers:

- any new file added under `mmi/research/`
- any change to an existing intake note's stated classification header
- any operator request to evaluate research convergence
- before any claim that research inputs have "aligned" into a single direction

Re-review updates this file only. It does not auto-promote notes.

---

## 9. Relationship to current MMI state

| Item | State |
|---|---|
| Tier 1 foundation | Complete (passive scaffolding) |
| Tier 2A packet intake | Mode A complete |
| Tier 2B passive registry | Mode A complete |
| Tier 2C contradiction report | Mode A complete |
| Research/intake notes | 4 notes + this index (after placement) |
| AUTH-5 | **Blocked** |
| Registry-fed routing | **Forbidden** |

Research notes and this index do **not** complete any tier or unlock autonomy.

---

## 10. What must not be inferred from this index

- That research inputs have converged into one project direction
- That Matt has adopted any single intake note as identity
- That success is defined or deferred success is resolved
- That cybersecurity or insurance is or is not the whole project (see lineage intake for Matt's exploration position)
- That a future build is authorized because notes are well-classified

---

## 11. Explicit non-authority footer

**NOT AUTHORITY.** This file is `GOVERNANCE_INDEX` and `CLASSIFICATION_REVIEW` only.

All listed intake notes remain **input, not authority**.

AUTH-5 remains blocked. Registry-fed routing remains forbidden. Task registry is unchanged.

Matt selects any future review, promotion, or build path. Rubrics rank; Matt decides.
