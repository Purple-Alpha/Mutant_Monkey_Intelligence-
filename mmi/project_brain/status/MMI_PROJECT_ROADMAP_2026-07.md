# MMI Project Roadmap — Operator Memory Surface

**Authority:** Matt (Super)  
**Maintained by:** Cursor PM (inventory + queue sync — not doctrine override)  
**Date filed:** 2026-07-02  
**Purpose:** One place to see where we are, what runs next, what is parked, and what must never be “forgotten because it sounds like fantasy.”

**Execution still flows through:** `tasks.json` → `scripts/next_task.py` → Matt `authorize build`.  
**This doc is memory, not a second queue.**

---

## 0. Matt rule — concepts are never discarded as fantasy

> **PARKED ≠ rejected.** An idea that feels unrealistic stays on the map until we try it in the chaos lab and it fails a falsifiable test — or until Matt explicitly retires it.
>
> Build order controls **when** we attempt something, not **whether** it belongs on the list.
>
> **Agents:** Before seeding or closing work, skim this roadmap **and** `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md`. Do not drop concepts for sounding too ambitious. Route them to PARKED or RESEARCH — never silent delete.

---

## 1. Where we are right now

*Synced from `status/MMI_PIPE_STAGING.json` — update when pipe moves.*

| Field | Value |
|-------|--------|
| **Pipe** | LOADED |
| **Active task** | `mmi-iceberg-l9-provenance-chain-depth-spec` (Claude — spec only) |
| **Last completed** | `mmi-iceberg-l7-temporal-rhythm-build` — PASS (28/28 pytest) |
| **Phase 1 stability** | **PASS** (3× Tier 4, recorded) |
| **Iceberg** | Tip + L8 + L6 + L4 + L5 + L7 **BUILT** · L9 spec **seeded** |
| **Maintenance freeze** | **ACTIVE** — GPG-P0 custody plan accepted at `faae3ae4…`; GPG-P1 and remaining MNT closure gates are still blocked |

**Spec:** `architecture/MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md`  
**Moat doc:** `architecture/MMI_DIFFERENTIATOR_2026-07.md`

---

## 2. Dependency ladder (do not skip)

Two nested orders — macro (AGI) wraps micro (iceberg). Both are filed doctrine.

### Macro — `architecture/MMI_AGI_EVOLUTION_PATHWAY.md` §5

```text
1. Phase 1 stable Tier 4          ← DONE (PASS on record)
2. Proof gate                     ← NEXT macro gate (before self-patch)
3. Budget ceiling + dead-man      ← mmi_control_envelope.py
4. console_server.py Ed25519      ← human signs evidence bundle
5. genomic_realignment_loop       ← self-heal (only after 2–4)
6. central_brain.py               ← Phase 2 bounded synthesis
```

### Micro — `architecture/MMI_METADATA_ICEBERG_2026-07.md` §5 (current track)

```text
Tip (streams 1–3)  ← DONE
L8 canary          ← DONE
L6 graph           ← DONE
L4 fingerprint     ← DONE
L5 correlation     ← DONE
L7 rhythm          ← DONE
L9 chain depth     ← NEXT
```

**Rule:** Finish iceberg L5→L7→L9 on the ingress gate **before** treating depth as complete. Proof gate (macro step 2) comes **before** any self-patching loop — even if weapon concepts feel ready earlier.

---

## 3. NOW / NEXT / LATER / PARKED

### NOW — active deployer work

| Item | Owner | Gate |
|------|-------|------|
| L9 provenance chain depth **spec** | Claude | Design lane — adversarial self-review required |

### NEXT — same track, dependency-correct (seed one at a time)

| Item | Notes |
|------|--------|
| L9 provenance chain depth **build** | Codex — after spec PASS + Matt `authorize build` |
| Option B — metadata-ingress provisioner wire | Held; not lost — seed when Matt says |
| **Proof gate** harness | proof-of-fix + proof-of-no-regression on `purple_evasion_suite.py` |
| Full iceberg depth in chaos lab | Re-run Phase 1 stack after L7/L9 |

### LATER — filed doctrine, not in active queue

| Item | Why later |
|------|-----------|
| Polyglot / dual-LLM critic ring | Needs `MMI_CRITIC_RING_RULES_v1` spec; runtime asynchrony blocker open |
| Governed agent-improvement / evolution loop | Future design investigation: bind task, prompt, output, independent grade, accepted correction, comparable before/after evaluation, regression evidence, Matt promotion, and rollback; agents may propose changes but may not approve their own evolution |
| Protected loose-data encryption execution | GPG-P0 documentation plan accepted; GPG-P1 still requires the real nominee/custody packet and Matt's separate explicit permit |
| `central_brain.py` bounded synthesis | Phase 2 AGI — after proof gate |
| `genomic_realignment_loop.py` | Phase 3 — after console + proof gate |
| Mirror sandbox full isolation | Router exists; sandbox v1 spec still needed |
| Assume-Click product lane | Business-action product — separate from weapon hot path |
| Kinetic dashboard / war-room websocket | Filed specs; not ingress-critical |

### PARKED — on the map, try when Matt authorizes a slice

*Full inventory:* `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md` (§A–G, §K).  
*These are not fantasy — they are unscheduled.*

| Concept | Status | Pointer |
|---------|--------|---------|
| Lung / swarm respiration (Inhale/Exhale/Return) | Filed doctrine, not built | Weapon concept §5; `chaos/MMI_SWARM_BLUEPRINT_LUNG_V1_2026-06.md` |
| Elastic defensive inflation (70→700) | Filed; numeric fork rejected | Weapon concept §10–12 |
| `mmi_encoder.py` time-window bytecode | Research / chat heritage | Inventory §B1 |
| Token jail + control language | Filed | Weapon concept §7–9 |
| Honeytoken registry (beyond L8 canary) | Needs spec | Inventory §G #5 |
| Tarpit + cryptolalia | Partial build | `adversarial_cryptolalia_tarpit.py`, router spec |
| Moving Target Defense / rotating dictionary | Research lane | `chaos/RESEARCH_MOVING_TARGET_DEFENSE_2026-07.md` |
| Host boundary WSL/Windows | Filed research | `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` |
| Control plane Ed25519 research | Filed research | Lung v2 refactor doc |
| Defensive cell golden images | Needs catalog spec | Inventory §G #3 |
| Safe inflation cap (minipc hardware) | Research | Inventory §G #12 |
| Canary token network alert rules | Chat-only | Inventory §K “still chat-only” |
| FastAPI websocket kinetic wrapper | Chat-only | Inventory §K |

**Matt reconciliation still open** (inventory §I): orchestrator scope vs defensive inflation, stale mission brief sweep, Track A vs Track B naming.

---

## 4. Two tracks (do not merge mentally)

```text
TRACK A — WEAPON (learning lab)              TRACK B — OPS (what got built)
──────────────────────────────               ─────────────────────────────
Controlled chaos, lung, mirror             Closeout gates H1/H2
Polyglot defense, purple attack            Backup + restore-check
Assume-Click product                       War room, intel briefs, OPSEC
Status: CONCEPT + PARTIAL CHAOS            Status: BUILT P1–P8
```

Track B does **not** replace Track A. Today's iceberg work is **weapon ingress depth** — correct Track A slice, built with Track B discipline (tests, evidence, deployer).

---

## 5. Recently completed (audit trail — nothing vanished)

| Milestone | Evidence |
|-----------|----------|
| Phase 1 stability harness | `status/MMI_PHASE1_STABILITY_PASS_2026-07-02.md` |
| Harness §7.4 hash rule fix | Same-lab rerun only |
| Promotion stub `110548` | latest-good archive |
| Iceberg L4 spec + build | 25/25 pytest ingress+fingerprint |
| Iceberg L8, L6 (earlier) | `test_metadata_ingress_gate.py` |
| Action integrity gate v1 | chaos lab provisioner stack |
| Mirror dimension router | filed + partial code |

---

## 6. Canonical doc map

| Question | Read |
|----------|------|
| Why is MMI different? | `architecture/MMI_DIFFERENTIATOR_2026-07.md` |
| What do I run today? | `python scripts/next_task.py` |
| What is the full concept list? | `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md` |
| What is the weapon? | `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` |
| AGI phases + falsification | `architecture/MMI_AGI_EVOLUTION_PATHWAY.md` |
| Ingress depth layers | `architecture/MMI_METADATA_ICEBERG_2026-07.md` |
| Roles + hard stops | `status/MMI_ACTIVE_SCOPE.md` |
| Pipe state | `status/MMI_PIPE_STAGING.json` |
| Queue tail | `mmi/task_pipeline.json` |

---

## 7. Operator checklist (when worried something was missed)

1. Run `python scripts/next_task.py` — only one thing should be active.
2. Open this file — check NOW vs PARKED.
3. Open concept inventory §G — anything there is **waiting for Matt seed**, not forgotten.
4. If an idea feels like fantasy — add to PARKED with a chaos-lab falsification line; **do not delete**.
5. New bounded work → append **one** task to `tasks.json` / pipeline; Matt authorizes builds.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.2 | 2026-07-13 | Recorded documentation-only GPG-P0 plan acceptance; maintenance freeze and GPG-P1 block remain |
| 1.1 | 2026-07-13 | Parked a future governed agent-improvement/evolution-loop investigation with independent review, regression, Matt-promotion, and rollback boundaries |
| 1.0 | 2026-07-02 | Initial operator roadmap; Matt rule §0 (concepts never discarded as fantasy); synced post L4 build + L5 seed |
