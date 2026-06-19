# Parked Draft Classifications — MMI Intake

**Authority:** Cursor intake lane per `MODE: DELEGATE` (2026-06-18)
**Status:** CLASSIFIED — not promoted, not tracked, not build-authorized
**Evidence:** git status `??` on four `4. Product_Roadmap/` files; file headers read 2026-06-18

---

## Classified files (dispatcher registry)

These filenames are intake-classified. They remain **untracked** until Matt explicitly
authorizes `git add` + commit on a named file. Classification does not imply promotion.

- Builder_Radar_Concept_Doc.md
- Honeypot_Deception_Concept_Doc.md
- Mutant_Monkey_Radar_Concept_Doc.md
- Purple_Team_Attacker_Cost_Doctrine.md

---

## Per-file classification

| File | MMI class | Routing outcome | Build implied | Promotion gate |
|---|---|---|---|---|
| `Builder_Radar_Concept_Doc.md` | `PARKED_DRAFT` / `CONCEPT_ADVISORY` | **PARK** — dual-LLM market intel concept; separate from Shadow Watcher Swarm (§12) | NO | Matt: authorize track + research lane before any contract |
| `Honeypot_Deception_Concept_Doc.md` | `PARKED_DRAFT` / `CONCEPT_ADVISORY` / `LEGAL_GATE` | **PARK** — explicitly excluded by `Shadow_Watcher_Swarm_Contract.md` §2/§10; legal/consent framework required | NO | Matt: legal review + separate §11 contract before any build |
| `Mutant_Monkey_Radar_Concept_Doc.md` | `PARKED_DRAFT` / `CONCEPT_ADVISORY` | **PARK** — public-signal pipeline concept; companion to Builder Radar; not scoreboard-ready | NO | Matt: authorize track + paired research with Builder Radar before contract |
| `Purple_Team_Attacker_Cost_Doctrine.md` | `PARKED_DRAFT` / `DOCTRINE_ADVISORY` | **PARK** — defensive-friction doctrine; informs Shadow Watcher Layer 7 / Specialisation v2 context; not a build contract | NO | Matt: authorize track if doctrine should enter repo; no Northstar build queue |

---

## Batch verdict

- **NOT_AUTHORIZED** for build, scoreboard row, or contract promotion.
- **No silent promotion** — files stay `??` in git until Matt names a promotion action.
- **Next delegable lane after intake:** `EXTERNAL_LANE` Threat Intelligence Daemon (if still top scored).
