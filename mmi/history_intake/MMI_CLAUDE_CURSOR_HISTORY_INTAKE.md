# MMI_CLAUDE_CURSOR_HISTORY_INTAKE.md — Claude/Cursor Session Material

> **NON-AUTHORITATIVE INTAKE — EVIDENCE, NOT AUTHORITY.**
> Classifies pasted Claude/Cursor session material (including an "Authoritative System
> Compendium" and CIS adversarial research) into **golden / parked / overclaim** buckets.
> Does **not** authorize build, routing, dispatcher, scoreboard, or automation changes.

**Source type:** Claude/Cursor/Matt pasted outputs in chat sessions  
**Authority:** Evidence only until repo verified  
**Primary classification:** `NEEDS_MMI_REVIEW`  
**Secondary:** `RESEARCH_INPUT`, `CONTRADICTION`, `DO_NOT_USE`  
**Compiled:** 2026-06-16  
**Note:** No standalone compendium file is committed in the repo; this intake captures
the classification decision for that material.

---

## Intake entry

```
Item:
Claude/Cursor "Authoritative System Compendium" + CIS adversarial attack-vector list

Classification:
NEEDS_MMI_REVIEW / RESEARCH_INPUT (CIS list)

Golden candidate themes:
- Facts-only detector discipline
- Three-tier test doctrine
- Safe-Stop trigger concepts
- Gap 5 (tenant baseline / memory consolidation) design ideas

Overclaim / quarantine:
- DEPLOYED_GATED or production-infrastructure claims without repo evidence
- Any status that implies runtime MMI automation is live

Repo verification required:
Cross-check each compendium claim against mmi/MMI_GATE_REGISTRY.md, scoreboard,
scripts/verify_build_truth.py, and committed code paths.

Do not promote:
Compendium title "Authoritative" — title is overclaim; file is RESEARCH_INPUT until verified.
```

---

## Bucket A — Golden (preserve; `NEEDS_MMI_REVIEW`)

Ideas worth keeping for MMI/Matt review; align with existing doctrine where noted:

| Idea | Why golden | Repo touchpoint |
|---|---|---|
| Facts-only detector discipline | Separates detection trigger from trust decision | `AGENTS.md`, detector agent specs |
| Three-tier test doctrine | Unit / integration / adversarial layering | Adversarial suite contracts #98–#102 |
| Safe-Stop trigger concepts | Halt/recovery governance | Safe-Stop #94, adversarial #102 |
| Gap 5 tenant baseline / memory consolidation concepts | Organism gap after control plane | #97 GATED; `Gap5_*` contracts |
| MMI reduces routing burden, not Matt's authority | Matches §2.2 worker routing | See `MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md` |

**Promotion gate:** Matt review + repo evidence + (for build) §11-signed contract.

---

## Bucket B — Parked (`RESEARCH_INPUT` / `PARKED_DRAFT`)

Good ideas, wrong time or missing prerequisites:

| Idea | Park reason |
|---|---|
| Full production deployment narrative | Stage 1 = file-based MMI; runtime not active per handshake |
| Broad "system compendium" as single authority doc | Conflicts with distributed repo authority model |
| Infra choices locked early (Raft/etcd, Spinnaker, mTLS stacks) | `DO_NOT_USE` until signed spec — see master §12 |
| CIS full adversarial suite build | Design/research input until §11 contract + Matt authorization |

---

## Bucket C — Overclaim / quarantine (`CONTRADICTION` / `DO_NOT_USE`)

Must **not** become authority without fresh repo proof:

| Claim pattern | Classification | Action |
|---|---|---|
| Title or prose: "Authoritative System Compendium" | `DO_NOT_USE` as authority label | Quarantine; treat body as research input only |
| `DEPLOYED_GATED` or "production infrastructure live" | `CONTRADICTION` vs Stage 1 MMI | Verify against gate registry; reject if unproven |
| Runtime MMI integration / automation active | `CONTRADICTION` | `PROJECT_HANDSHAKE.md` says NOT active |
| Pasted test/commit counts without terminal output | `BUILT_NEEDS_VERIFICATION` | Require live rerun per `AGENTS.md` |
| Self-approval or model-as-authority framing | `DO_NOT_USE` | Conflicts with MMI protocol |

---

## CIS adversarial attack-vector list

**Source:** Pasted markdown research (e.g. "markdown 13" CIS attack vectors)  
**Classification:** `RESEARCH_INPUT` — not authority  
**Use:** Feed future Collective Immune System adversarial suite design **after** Matt
authorizes CIS adversarial contract work. Does not modify CIS #95 built scope or scoreboard.

---

## Cross-references

- ChatGPT repo intake: `MMI_CHATGPT_HISTORY_INTAKE.md`
- Windows master index: `MMI_CHATGPT_HISTORY_MASTER_INDEX.md`
- Dispatcher doctrine (separate intake; not accepted authority): `MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md`
- Folder rules: `README.md`

---

## Final rule

This intake preserves Claude/Cursor session material as **classified evidence**. It does not
promote compendium claims, does not execute dispatcher changes, and does not choose the
next build/research/design target. Matt must explicitly authorize any next phase.
