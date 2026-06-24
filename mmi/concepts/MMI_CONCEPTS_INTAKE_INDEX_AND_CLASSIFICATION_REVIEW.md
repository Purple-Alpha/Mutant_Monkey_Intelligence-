# MMI Concepts Intake Index and Classification Review

**Classification:** `GOVERNANCE_INDEX` · `CLASSIFICATION_REVIEW` · `DRIFT_CONTROL` · `NOT_AUTHORITY` · `NOT_DOCTRINE` · `NOT_BUILD_AUTHORIZATION` · `NEEDS_PERIODIC_RE_REVIEW`

**Status:** Meta-governance register for `mmi/concepts/` only.

**Owner:** MMI governance (human-maintained)

**Created:** 2026-06-23

**Reconciled against disk:** 2026-06-23 via `find mmi/concepts -maxdepth 1 -type f`

---

## 1. Purpose

`mmi/concepts/` holds operator concept sheets and addenda — **not** project truth, **not** §11 specs.

This index:

- registers every file under `mmi/concepts/`
- assigns each an **influence ceiling**
- pins all entries as **concept only, zero routing influence**
- prevents metaphor accumulation from becoming silent build authority

**Indexing does not promote.**

---

## 2. Influence ceiling vocabulary

| Tag | Meaning |
|---|---|
| `CONCEPT_INPUT` | Concept capture only; not adoption |
| `BRIDGE_TRACK` | Domain-bridge narrative; does not select Domain 2 |
| `CONTROL_PLANE_METAPHOR` | Lung/brain/immune language; must map to signed contracts before build |
| `EXPLICITLY_NOT_DOCTRINE` | Must not be read as doctrine |
| `NEEDS_FUTURE_REVIEW` | Promotion path unresolved |
| `ZERO_ROUTING_INFLUENCE` | Must not feed dispatcher, registry, or scoreboard selection |

Default ceiling: **concept only, zero routing influence**.

---

## 3. Drift-control rules

1. **Concept stays concept.** Placement here never implies build authorization.
2. **Metaphor is not fact.** Lung/brain/immune language requires explicit mapping to on-disk contracts (see Lung Multiplier addendum → Load Fission `#90`/`#103`).
3. **No silent promotion.** §11 + operator build lane required for any implementation.
4. **Sibling addenda do not supersede** unless a DEC record says so.
5. **Research vs concepts:** cyber intel / lineage notes live in `mmi/research/`; strategic product metaphors live here.

---

## 4. Live register — reconciled against `mmi/concepts/`

**Reconciliation command:** `find mmi/concepts -maxdepth 1 -type f -print | sort`

| File | Doc ID / record | Classification tags | Influence ceiling | Summary |
|---|---|---|---|---|
| `MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md` | MMI-CON-2026-06-21; commit lineage `mmi/concepts/` | `CONCEPT_INPUT` · `EXPLICITLY_NOT_DOCTRINE` · `NEEDS_FUTURE_REVIEW` | Zero routing | Domain-agnostic governance brain thesis; Domain 1 = email; no branch selected |
| `MMI_EXECUTIVE_PERIMETER_ASM_CONCEPT_ADDENDUM.md` | MMI-CON-2026-06-22; MMI-DEC-113 intake | `CONCEPT_INPUT` · `BRIDGE_TRACK` · `EXPLICITLY_NOT_DOCTRINE` | Zero routing | Domain 1→2 identity/API bridge; front-lines scout; no hardware code |
| `MMI_LUNG_MULTIPLIER_VS_FISSION_GOVERNANCE_ADDENDUM.md` | MMI-CON-2026-06-23; MMI-DEC-113 intake | `CONCEPT_INPUT` · `CONTROL_PLANE_METAPHOR` · `EXPLICITLY_NOT_DOCTRINE` | Zero routing | Pins Multiplier vs autonomous fission; maps to Load Fission GATED rows |
| `MMI_BRAIN_IMMUNE_LUNG_ZERO_TRUST_CONTROL_LOOP_CONCEPT.md` | PARKED 2026-06-18; Manus research input | `CONCEPT_INPUT` · `CONTROL_PLANE_METAPHOR` · `NEEDS_MMI_REVIEW` · `PARKED_DRAFT` | Zero routing | Broad homeostasis research; superseded for build by signed fission/safe-stop rows |
| `MMI_BOARD_ADVISORY_LAYER_CONCEPT.md` | CONCEPT_LOCK 2026-06-16 | `CONCEPT_INPUT` · `NEEDS_MMI_REVIEW` · `PARKED_DRAFT` | Zero routing | Board advisory layer doctrine; parked until requirements research |
| `MMI_CONCEPTS_INTAKE_INDEX_AND_CLASSIFICATION_REVIEW.md` | MMI-DEC-113 | `GOVERNANCE_INDEX` · `CLASSIFICATION_REVIEW` | Meta only | This register |

**Reconciliation rule:** Re-run `find` on every concepts-folder change. Do not ship a partial register.

---

## 5. Relationship to `mmi/research/`

| Folder | Holds |
|---|---|
| `mmi/research/` | External intel, lineage, organism framing — see `MMI_RESEARCH_INTAKE_INDEX_AND_CLASSIFICATION_REVIEW.md` |
| `mmi/concepts/` | Operator product/control-plane concept sheets and governance addenda — this index |

Cross-folder references are allowed; **neither folder promotes** the other.

---

## 6. Explicit non-authority footer

**NOT AUTHORITY.** AUTH-5 blocked. Registry-fed routing forbidden. Matt selects any future review or build path.
