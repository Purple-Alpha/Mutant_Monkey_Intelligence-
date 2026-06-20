# MMI Autonomous Brain — Tier 1 Foundation Implementation Contract (Draft)

**Status:** `DRAFT — NOT SIGNED — NOT IMPLEMENTATION AUTHORIZATION`

**Classification:** `NEEDS_MMI_REVIEW` · `CONTRACT_DRAFT` · Tier 1 passive foundation only

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` (review material — not signed)

**Draft authorization:** `MMI_AUTONOMOUS_BRAIN_REVIEW_HARDENING_AND_TIER1_CONTRACT_DRAFT` only

**Date:** 2026-06-19

---

## 1. Executive summary

This contract defines the **first safe implementation slice** for MMI Autonomous Brain Foundation: **Tier 1 passive foundation records only**.

Tier 1 may create **documentation, schema, and template artifacts** under `mmi/` that describe approved repo surfaces, task registry shape, worker completion packets, decision audit appendix shape, and Stage 1 doctrine-vs-code gaps.

Tier 1 does **not** authorize dispatcher edits, registry population, write automation, prompts, contradiction tooling, dashboards, autonomy, hooks, or scoreboard changes.

Signing this contract (future §11) would authorize **only** creating the five named passive artifacts. It would **not** authorize Tier 2 or Tier 3 capabilities.

---

## 2. Files to create (authorized only after Matt §11 signature on this contract)

| # | File | Type |
|---|---|---|
| F1 | `mmi/MMI_REPO_SURFACE_REGISTRY.md` | Doctrine registry |
| F2 | `mmi/MMI_TASK_REGISTRY_SCHEMA.md` | Schema-only |
| F3 | `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` | Template |
| F4 | `mmi/MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md` | Schema-only |
| F5 | `mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md` | Gap callout |

No other files may be created under this Tier 1 slice without contract revision.

---

## 3. Purpose of each file

### F1 — `MMI_REPO_SURFACE_REGISTRY.md`

- Closed list of **approved repo surfaces** MMI may cite as evidence (aligned with review material §1).
- For each surface: path, authority role, read-only vs routing-authority, whether dispatcher-derived.
- Explicit **exclusions:** Architectapp, unpromoted parked drafts, chat transcripts.

### F2 — `mmi/MMI_TASK_REGISTRY_SCHEMA.md`

- **Schema-only** definition for future `MMI_TASK_REGISTRY` (field names, closed enums, status vocabulary).
- **Empty** — no populated task rows, no JSON/YAML instance file with live tasks.
- Must repeat registry negative authority (§4 of review material): not contract/build/git/scoreboard/dispatcher input authority.

### F3 — `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md`

- Closed template matching invariant I15: files changed, scope check, tests/gates run, deviations, verify output, git status, no-out-of-scope confirmations.
- Example empty template only — not filled completion packets.

### F4 — `mmi/MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md`

- Schema for append-only decision audit records: selection event id, timestamp, candidates, scores, reasoning, `decided_by`, non-selected alternatives.
- Selection event definition from review material §6.
- No live appendix file populated in Tier 1 unless explicitly listed — schema + empty example only.

### F5 — `mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md`

- Mirrors review material §14: doctrine-only capabilities not enforced in code.
- Updated at Tier 1 build close to reflect which gaps remain after artifact creation.

---

## 4. Authority boundaries

| Boundary | Tier 1 posture |
|---|---|
| AUTH-1 passive records | Artifacts are passive doctrine/schema — no automation |
| AUTH-2 | Dispatcher respect-only — **no** `scripts/mmi_dispatch.py` changes |
| AUTH-2-EDIT | **Not authorized** |
| AUTH-3A | Schema file only — **no** populated registry |
| AUTH-3B | **Not authorized** — no write automation |
| AUTH-4–7, AUTH-5 | **Not authorized** |
| Registry as dispatcher input | **Forbidden** — schema must state dispatcher unchanged |
| Scoreboard / gate registry | **Read-only reference** in prose — no edits |
| #47 / #48 | **Out of scope** |
| Architectapp | **Out of scope** |
| Matt authority | Unchanged — signing this contract does not grant AUTH-5 or dispatcher edits |

---

## 5. Non-goals / must-not-build

Tier 1 implementation (post-signature) must **not**:

- edit `scripts/mmi_dispatch.py` or any dispatcher output behavior
- create or populate `MMI_TASK_REGISTRY.json` / `.yaml` with live tasks
- wire registry into `collect_delegation_tasks()` or routing
- create MMI write automation (AUTH-3B)
- create auto-prompt generation code (AUTH-4)
- create contradiction-detection code or automation (AUTH-7)
- create dashboard, UI, or owner brief runtime (AUTH-6)
- create always-on sync daemons, hooks, watchers, or background `--sync`
- change scoreboard schema or rows
- touch `#47 Case Timeline` or `#48 Verification Outcome Agent`
- promote or git-track parked roadmap drafts
- integrate Architectapp
- push (operator instruction required separately)
- implement AUTH-5 autonomous selection

---

## 6. Lifecycle impact

Tier 1 artifacts are **reference doctrine** for future tiers. They do **not** change lifecycle §7 ordering today.

After Tier 1 build (if signed and implemented):

- Workers should use F3 packet template for MMI completions.
- F1 surfaces constrain evidence citations in MMI records.
- F2/F4 schemas constrain future AUTH-3A appendix/registry work.
- F5 documents remaining doctrine-vs-code gaps — no false claim that BLOCK-on-conflict is enforced.

**Routing state advance:** Creating Tier 1 files alone does not constitute routing state advance (review material §7).

---

## 7. Verification plan

Post-implementation (only after §11 signature + separate build authorization):

1. **File existence:** All five files present at named paths; no extra files under `mmi/` from this slice.
2. **Git diff scope:** Only the five files + `MASTER_INDEX.md` entry (if required by project discipline) + MMI records for build close — no dispatcher/scoreboard/runtime paths.
3. **`python3 scripts/mmi_dispatch.py --verify`** — must PASS after MMI record update and commit.
4. **`git status --short`** — clean; no untracked registry instance files.
5. **Grok gate** — if Matt authorizes gate on Tier 1 doc slice: `complete_gate.py` 0/0 with manifest listing all five artifacts and this contract.
6. **Manual review:** Matt confirms F2 has no populated tasks; F3/F4 are templates/schemas only; F5 lists §14 gaps accurately.

---

## 8. Failure modes

| Failure mode | Mitigation |
|---|---|
| Schema file mistaken for live registry | F2 must say "schema only"; no `.json`/`.yaml` instance in Tier 1 |
| Dispatcher accidentally wired to registry | Verification plan checks `mmi_dispatch.py` untouched |
| Template treated as authorization | F3 header: template ≠ completion acceptance |
| Gap doc claims runtime enforcement | F5 must list doctrine-only items explicitly |
| Tier creep into AUTH-3B writes | Contract scope locked to five files; gate required for writes |
| Builder self-audit | Grok gate on doc slice if authorized; Matt acceptance |

---

## 9. Rollback / demotion plan

- **Rollback:** Revert commit(s) that added the five Tier 1 artifacts; restore prior `mmi/` state; run `--verify` PASS.
- **Demotion:** If artifacts drift into authority without signature, classify as `CONTRADICTION` in MMI intake; Matt reverts or revises contract.
- **No runtime demotion** — Tier 1 has no runtime surface to demote.

---

## 10. Falsifiable acceptance tests (Tier 1 build — after signature)

| Test ID | Name | Pass condition |
|---|---|---|
| T1-T1 | Five files only | Exactly F1–F5 exist; no sixth Tier 1 artifact |
| T1-T2 | No dispatcher diff | `git diff` shows zero changes under `scripts/mmi_dispatch.py` |
| T1-T3 | No registry instance | No `MMI_TASK_REGISTRY.json`/`.yaml` with task rows |
| T1-T4 | Schema disclaims dispatcher input | F2 contains explicit not-dispatcher-input rule |
| T1-T5 | Packet template complete | F3 lists all I15 fields |
| T1-T6 | Appendix schema + decided_by | F4 defines selection event and `decided_by` rules |
| T1-T7 | Gaps documented | F5 matches review material §14 gap table |
| T1-T8 | Surfaces match §1 | F1 surfaces align with review material approved list |
| T1-T9 | verify PASS | `mmi_dispatch.py --verify` after MMI update |
| T1-T10 | No scoreboard/runtime | No changes under `agent_concepts/`, `core/`, Architectapp |

---

## 11. Sign-off (unsigned)

**UNSIGNED — NOT IMPLEMENTATION AUTHORIZATION.**

Signing would authorize **only** creating the five passive Tier 1 artifacts listed in §2. Signing would authorize **no** dispatcher edits, registry population, write automation, prompts, contradiction tooling, dashboard, autonomy, hooks, scoreboard changes, #47/#48 work, or Architectapp work.

Tier 2 tooling requires Tier 1 stable + separate AUTH gates per review material §2.

> Matt Nichol ____________________  Date __________

---

**End of Tier 1 contract draft. This file does not authorize implementation.**
