# MMI Purple Team Attack Scope & Tactics — 2026-07

**Status:** SCOPE DRAFT — NOT BUILD AUTH  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  
**Purpose:** Define purple team attack lane against MMI — Track A weapon concepts and Track B ops runtime — inside owned chaos lab only.

**Matt directive (verbatim):**

> well now i am building my purple team to attack now haha that is on you

**Hard boundary:** Owned systems only. Chaos lab clone only. **Destroy the clone, not the brain.** No hack-back. No external targets.

**Related:**

* `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` §2–4
* `architecture/MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md`
* `chaos/MMI_SWARM_BLUEPRINT_LUNG_V1_2026-06.md`
* `lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md`
* `intel/WAR_ROOM_SCORING_MATRIX_v2.md`

---

## 1. Mission

Force **real failure pressure** against MMI — not validation theater.

Success = MMI detects, contains blast radius, preserves evidence, recovers cleanly, converts lesson into hardening (weapon concept §1, §3).

A successful purple test **may produce failure**. That is valid.

---

## 2. Battlefield rules

| Rule | Meaning |
|------|---------|
| **Chaos lab only** | Isolated clone of authority repo — max damage allowed here |
| **Authority repo read-only** | Live `/mnt/c/MMI` brain not the primary attack surface |
| **No B2 mutation** | Cold mirror not corrupted during purple runs |
| **Evidence preserved** | Attack artifacts logged for mirror sandbox / human-reviewed patches |
| **Matt owns go/no-go** | Purple run authorization separate from build auth |

---

## 3. Attack surfaces — Track B (what exists today)

Initial target list for purple team — **Matt may revise:**

| Target | Attack class | What we're testing |
|--------|--------------|-------------------|
| `tasks.json` | Control-plane injection | Unsigned task enqueue, assignee spoof, build_auth flip |
| `scripts/complete_task.py` | Closeout bypass | Closeout without outputs, forged evidence JSON |
| `scripts/reload_mmi_pipes.py` | Pipe confusion | Stale pipe vs live queue contradiction |
| `mmi/war_room.py` | Truth lie | Panel shows safe while clone is corrupted |
| `--validate-promotion` | Promotion bypass | ALLOWED without restore-check evidence |
| H2 intel gate | Headline laundering | Global stat into §1 / smb_relevance |
| L3-06 class | OPSEC false-DONE | Checklist DONE without habit evidence |
| P1–P8 guardrails | Friendly fire | Defensive inflation flagged as internal threat (blocker §3) |

---

## 4. Attack surfaces — Track A (weapon concepts not built)

Purple team tests **design pressure** until code exists:

| Concept | Attack class | What we're testing |
|---------|--------------|-------------------|
| Lung v1 bytecode pipe | Injection / replay | Raw shell in pipe, stale HMAC window, malformed magic |
| Exhale inflation | Resource weaponization | Trigger inflation → self-DoS, provider rate limits (blocker §2) |
| Token jail | Schema bypass | Markdown/prompt injection inside signed envelope payload |
| Evidence harvesting | Log poisoning | Malicious log → draft patch embeds exploit (blocker §4) |
| Mirror sandbox | Boundary escape | Hostile payload reaches authority repo or real secrets |
| Air-lock pool wake | Sleep→wake abuse | Wake wrong container, stream contaminated context |
| Host daemon boundary | Privilege abuse | Compromised Python agent commands daemon to over-contain |

Reference blueprints: `chaos/MMI_SWARM_BLUEPRINT_LUNG_V1_2026-06.md`, `lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md`

---

## 5. Tactics classes (purple, not red team)

| Class | Description | Allowed |
|-------|-------------|---------|
| **Injection** | Malformed control messages, task spoof, pipe pollution | Yes — chaos lab |
| **Contradiction** | Stale war room, DRY confusion, false DONE | Yes — chaos lab |
| **Overload** | Inflation cap test, API rate pressure, container wake storm | Yes — measure, don't brick live box |
| **Deception** | Honeytoken probe, mirror path simulation | Yes — owned sandbox |
| **Recovery** | Destroy clone, rebuild from latest-good DNA | Required every run |
| **External** | Scanning, attacking third-party infra | **No** |

---

## 6. Runtime blockers purple team must stress-test

From `architecture/MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md`:

1. **Kernel vs user-space** — Can Python agents trigger containment without corrupt agent holding SYSTEM?
2. **Multi-model asynchrony** — Does 700-agent inflation lock provider accounts?
3. **Doctrine mutex** — Does P1–P8 fight Exhale / air-lock wake?
4. **Evidence sanitizer** — Does log poisoning reach patch-generation LLM?

---

## 7. Required outputs per purple run

* Attack scenario ID + chaos lab clone SHA
* Fault injected (what broke / what lied)
* Detection result (detected / missed / false positive)
* Blast radius (contained / spread)
* Evidence artifact paths
* Recovery proof (`--restore-check` or rebuild log)
* Draft hardening diff — **human-reviewed only** (weapon §19)

---

## 8. Open questions (Matt fills)

* First chaos-lab clone provisioning method?
* First attack scenario ID and owner?
* Inflation cap for Mini PC purple runs?
* Which commercial APIs in polyglot ring vs local shards only?

---

## 9. Current status

**DRAFT SCOPE** — tactics list initial; Matt revises.

Not build authorization. Not permission to attack live authority repo.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Initial scope — Matt purple team directive + Track A/B targets + runtime blockers |
