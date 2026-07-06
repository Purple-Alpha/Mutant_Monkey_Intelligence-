# MMI Concept Inventory and Gaps — 2026-07

**Authority:** Matt (Super)  
**Maintained by:** Cursor PM (inventory only — not doctrine override)  
**Purpose:** Full map of what exists, what was chat-only, what was partially filed, and what conflicts — so Matt can reconcile the mess.

**North star (filed 2026-07-01):** `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md`  
**Operator roadmap (NOW/NEXT/PARKED):** `status/MMI_PROJECT_ROADMAP_2026-07.md` — Matt rule: PARKED concepts are never discarded as fantasy.

---

## How to read this document

| Label | Meaning |
|-------|---------|
| **FILED** | Exists in `mmi/project_brain/` or repo scripts |
| **CHAT-ONLY** | Discussed in agent sessions; never written to project brain |
| **PARTIAL** | Some ideas filed under a different name or scope |
| **BUILT** | Code exists (may or may not match weapon concept) |
| **CONFLICT** | Two docs say opposite things |

---

## A. Your weapon concept (now filed)

| Item | Status | Location |
|------|--------|----------|
| Controlled Chaos Defensive Weapon (full 27-section spec) | **FILED** | `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` |
| Lung / Swarm Respiration (Inhale / Exhale / Return) | **FILED** | Same doc §5 |
| Elastic agent inflation / deflation | **FILED** | Same doc §10–12 |
| Structured control language + token jail | **FILED** | Same doc §7–9 |
| Mirror sandbox, honeytokens, tarpit, critic ring | **FILED** | Same doc §15–18 |
| Business-action integrity + Assume-Click | **FILED** | Same doc §20–21 |
| Destroy clone not brain | **FILED** | Same doc §4 |

---

## B. Chat-only concepts — NOT filed until now

These were discussed, sometimes promised for filing, but **never landed in project brain**.

### B1. Lung v1 original blueprint (Swarm Blueprint)

**Status:** CHAT-ONLY  
**Source:** Matt paste in session — "MMI Swarm Blueprint: Dynamic Instruction Set Randomization & Elastic Scaling"

**Preserved ideas (not in repo as standalone doc):**

| Component | Description |
|-----------|-------------|
| `mmi_encoder.py` | HMAC time-window bytecode compiler (`MMIEncoder`, 30s epoch, magic header) |
| `verify_and_route` | Deserialization gate on `reload_mmi_pipes.py` listener concept |
| `trigger_swarm_respiration_fault` | Breach hook → Exhale |
| 70 baseline nodes | Inhale steady state |
| 70 → 700 fork storm | Exhale — telemetry spies, containment wrappers, honeytoken dirs |
| `test_purple_respiration.py` | Simulated inject-malformed test log |
| Symmetric `secret_seed` | **Rejected** in weapon concept §23 |

**Action needed:** Optional archive doc `lanes/RESEARCH_SWARM_BLUEPRINT_V1_2026-06.md` if Matt wants v1 preserved verbatim for purple team reference.

---

### B2. Lung v2 refactor (Matt + peer-review session)

**Status:** CHAT-ONLY  
**Promised but never filed:**

| Promised path | Content |
|---------------|---------|
| `lanes/RESEARCH_control_plane_ed25519_2026-06.md` | Ed25519 signed envelopes, PyNaCl verify, 5s skew, nonce cache |
| `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` | WFP, ETW/Sysmon, WDAC, Windows ACL on `C:\MMI`, DrvFs reality |
| `architecture/MMI_CONTROL_PLANE_HARDENING_v0.md` | Claude distillation — never created |

**Preserved ideas:**

* Ed25519 verify-only on agents; sign off-box or operator step
* Timestamp inside signed bytes (not outside signature)
* cgroups v2 freeze/throttle for Linux-side rogue PID
* Python as telemetry coordinator, not kernel hook
* Control plane vs delivery plane split (bytecode ≠ HTML smuggling defense)

**Note:** v2 **replaced** clone Exhale with cgroup freeze — Matt later rejected that as "not the lung." Weapon concept §23 remaps v2 pieces; v2 standalone doc still not filed.

---

### B3. Moving Target Defense / rotating dictionary

**Status:** CHAT-ONLY  
**Source:** Assistant research response after Matt asked about randomized binary command language

**Ideas:**

| Term | Mapping |
|------|---------|
| Randomized binary vs `Execute Task #4` | Moving Target Defense (MTD) / protocol obfuscation |
| Dictionary rotates every 60s | Ephemeral session keys |
| Literature cousins | ASLR, port hopping, polymorphic protocols |

**Relation to weapon concept:** Weapon concept §9 says rotate keys/nonces/scopes — **not** command meaning. MTD-as-main-security is rejected; MTD-as-research lane is unfiled.

---

### B4. Bounded v0 slice (assistant proposal — never built)

**Status:** CHAT-ONLY

Proposed minimal build that **was not authorized**:

* `mmi_control_envelope.py` — Ed25519 blob
* Hook in `complete_task.py` — refuse unsigned envelopes
* `test_control_envelope.py` — malformed/replay cases
* Breach response — audit log, stop seeding, optional firewall script

This is **not** the lung. It was the watered-down substitute Matt rejected.

---

### B5. Purple team / attack side (Matt building now)

**Status:** CHAT-ONLY as formal spec

Matt stated intent to build purple team to attack MMI. No doc filed yet.

**Suggested filing:** `chaos/MMI_PURPLE_TEAM_ATTACK_SCOPE_2026-07.md` when Matt defines targets.

**Existing partial overlap:**

* `chaos/MMI_CHAOS_SANDBOX_V2_2026-07.md` — detect-only fixtures
* `chaos/MMI_CHAOS_LEVEL3_PLAN_2026-07.md` — staged fault injection
* `lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md` — war room purple mapping

These are **ops/evidence chaos**, not lung/control-plane attack specs.

---

## C. Partially filed — buried in other docs

| Concept | Where partially lives | What's missing |
|---------|----------------------|----------------|
| **Endpoint agent swarm** (Ingress → Evaluator → Containment) | `lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md` § "Theoretical agentic swarm" | Marked research-only, not build; **different** from Matt's defensive inflation lung |
| **Business-action integrity** | `lanes/REDDIT_VENDOR_EMAIL_ROUTINE_INTAKE_2026-07.md` R3 | Product lane not architecture doc |
| **Human gate / OPSEC-4/5/9** | `intel/drills/OPSEC_HUMAN_GATE_DRILL_2026-06-30.md`, `opsec/OPERATOR_OPSEC_CHECKLIST.md` | Operator habits — not Assume-Click product mode |
| **Interpretation layer failures** | `architecture/MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md`, chaos sandbox | Framed as ops quality — not weapon doctrine |
| **Polyglot lanes** | `status/MMI_LANE_ROUTING.md`, `architecture/MMI_ORCHESTRATOR_SCOPE.md` | Routing for PM work — not polyglot **defense** model |
| **Chaos lab vs authority** | `chaos/MMI_CHAOS_LEVEL3_PLAN_2026-07.md` fixtures v3 | Level 3 = evidence corruption tests; not mirror sandbox / ghost host |
| **War room truth surface** | `mmi/war_room.py` (BUILT), `MMI_WAR_ROOM_SPEC.md` | Read-only ops panel — not liquid routing under attack |
| **Rebuild proof / DNA** | `backup/MMI_LATEST_GOOD_ARCHIVE.md`, restore-check docs | Backup discipline — aligns with weapon §4 but not linked to weapon framing |

---

## D. Built in repo — parallel track (not the weapon)

This is what actually got implemented while the lung stayed in chat.

| Built item | What it does | Relation to weapon concept |
|------------|--------------|----------------------------|
| `scripts/complete_task.py` | H1 closeout gate, H2 intel gate, P8 evidence contract | **Gates** — not signed envelopes or respiration |
| `scripts/mmi_verify.py` | closeout, intel-brief, opsec-checklist, opsec-amend-check | Deterministic critics **partial** — single script, not critic ring |
| `scripts/mmi_cold_backup.py` | Push integrity, restore-check, validate-promotion | DNA/rebuild proof **partial** |
| `mmi/war_room.py` | Pipe, task, backup tail, truth surface | Read-only — no Exhale, no inflation |
| `scripts/reload_mmi_pipes.py` | Queue warmer from `tasks.json` | **Not** a bytecode listener; no lung |
| Intel briefs + OPSEC checklist | Advisory-only security intel | Separate product lane |
| Chaos tabletop + sandbox v2 + L3 fixtures | Detect bad evidence in staging | **Validation chaos** — weapon concept §3 says this may be "fake chaos" if no real damage |
| P1–P8 quality ladder | Block bad evidence before authority | **Ops discipline** — valuable but not defensive weapon |
| Reddit intake R1–R3 | Field evidence for email workflows | Product research input |

**Nothing built for:** `mmi_encoder.py`, respiration state machine, agent inflation, mirror sandbox, honeytokens, tarpit, token jail, Assume-Click mode, liquid routing.

---

## E. Doctrine conflicts — need Matt reconciliation

| Topic | Doc A says | Doc B says | Conflict |
|-------|-----------|-----------|----------|
| **Agent spawning** | Weapon concept §10: elastic defensive inflation is core | `MMI_ORCHESTRATOR_SCOPE.md`: "Human-steered tabs — **not auto-spawned bots**" | **YES** — orchestrator scope contradicts lung Exhale unless remapped |
| **MMI identity** | Weapon concept: defensive weapon, controlled chaos | `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`: advisory-only intel briefs | **Partial** — different product faces of same project |
| **Endpoint swarm** | Gemini research: Ingress/Evaluator/Containment on endpoint | Weapon concept §6: lung does not replace EDR; Security Intel lane: swarm not build | **YES** — three different boundaries |
| **Chaos success** | Weapon §3: success may be failure + recovery | P1–P8 ladder: closeout gates should PASS | **Partial** — ops wants clean closeout; weapon wants destructive learning |
| **70→700 clones** | Weapon §23: rejected as-is | Weapon §10–12: inflation from clean templates still required | **Clarify** — numeric fork rejected; topological inflation kept |
| **Mission brief** | `mission/MMI_MISSION_BRIEF.md`: "NEEDS MATT product definition" | Weapon concept: full product doctrine now filed | **Stale** — mission brief predates weapon filing |

---

## F. Files outside MMI brain (contamination risk)

| Path | Project | Risk |
|------|---------|------|
| `project_managment/dual_core_agent.md` | Social Architect / Freedom's Door | Dual-agent healthcare MAS — **not MMI weapon**; do not merge lanes |
| `AGENTS.md`, `CODEX.md` (repo root) | Legacy Social Architect | Old scope rules may conflict with MMI weapon concept |
| NorthStar `/home/socialarchitect/northstar` | Separate repo per Matt directive | Do not treat as MMI authority |

---

## G. Concepts from weapon doc — still need their own specs

Each needs a scoped design doc when Matt authorizes — **none exist yet:**

| # | Topic | Suggested future path |
|---|-------|----------------------|
| 1 | Minimal control-envelope schema v1 | `architecture/MMI_CONTROL_ENVELOPE_SCHEMA_v0.md` |
| 2 | Respiration state machine (implementable FSM) | `architecture/MMI_SWARM_RESPIRATION_FSM.md` |
| 3 | Defensive cell templates (golden images) | `chaos/templates/DEFENSIVE_CELL_CATALOG.md` |
| 4 | Mirror sandbox v1 isolation spec | `chaos/MMI_MIRROR_SANDBOX_v1_SPEC.md` |
| 5 | Honeytoken registry + legal guardrails | `opsec/MMI_HONEYTOKEN_REGISTRY.md` |
| 6 | Tarpit rate limits + sandbox bounds | `chaos/MMI_TARPIT_RULES.md` |
| 7 | Deterministic critic ring rule table | `architecture/MMI_CRITIC_RING_RULES_v1.md` |
| 8 | Assume-Click workflow (email lane) | `architecture/MMI_ASSUME_CLICK_WORKFLOW_v1.md` |
| 9 | Business-action taxonomy | `architecture/MMI_BUSINESS_ACTION_TAXONOMY.md` |
| 10 | Chaos lab clone provisioning | `chaos/MMI_CHAOS_LAB_PROVISIONING.md` |
| 11 | Purple team attack scope | `chaos/MMI_PURPLE_TEAM_ATTACK_SCOPE_2026-07.md` |
| 12 | Safe inflation cap (hardware) | `lanes/RESEARCH_INFLATION_CAP_MINIPC_2026-07.md` |
| 13 | Swarm blueprint v1 archive (verbatim) | `lanes/RESEARCH_SWARM_BLUEPRINT_V1_2026-06.md` |
| 14 | Control plane Ed25519 research | `lanes/RESEARCH_control_plane_ed25519_2026-06.md` |
| 15 | Host boundary WSL/Windows | `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` |

---

## H. What Cursor PM did wrong (audit trail)

For Matt's trust repair — explicit record:

1. Peer-reviewed lung v1 and reframed Exhale as cgroup freeze — **contradicted lung definition**
2. Proposed `mmi_control_envelope.py` v0 as substitute — **not the lung**
3. Said "file v2 research docs" — **never filed**
4. Built P1–P8 ops ladder extensively while weapon concept stayed **chat-only**
5. Did not surface doctrine conflict with `MMI_ORCHESTRATOR_SCOPE.md` until this inventory
6. Used "lung" language after v2 removed agent multiplication

---

## I. Suggested reconciliation order (Matt decides)

1. **Confirm** weapon concept as north star (filed — done)
2. **Update or supersede** `MMI_ORCHESTRATOR_SCOPE.md` § agent spawning to allow defensive inflation under Exhale
3. **Archive** swarm blueprint v1 + v2 refactor as research lanes (verbatim — no dilution)
4. **Mark** P1–P8 track as "ops immune system" subordinate to weapon concept — or separate lane
5. **Stale doc sweep:** `MMI_MISSION_BRIEF.md`, `MMI_PHASE2_MVP_ARCHITECTURE.md`
6. **Purple team scope** — Matt defines attack targets against chaos lab clone
7. **First build slice** — only when Matt authorizes; weapon doc §27 is explicit NOT BUILD AUTH

---

## J. Quick reference — two MMI tracks today

```text
TRACK A — WEAPON (Matt's learning lab)          TRACK B — OPS (what got built)
────────────────────────────────────            ─────────────────────────────
Controlled chaos                                Closeout gates H1/H2
Lung inhale/exhale/inflation                    Backup + restore-check
Mirror sandbox / honeytokens                    War room truth surface
Token jail / control language                   Intel briefs + OPSEC checklist
Purple team attack                              Chaos sandbox detect-only
Assume-Click product                            Reddit field intake
Status: CONCEPT FILED                           Status: BUILT P1–P8
```

**They are not the same project face.** Track B does not replace Track A. Track A was never implemented.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Initial inventory after weapon concept filing; chat-only and conflict audit |
| 1.1 | 2026-07-01 | Lung v1/v2, host boundary, runtime blockers, purple team scope filed — see §K |

---

## K. Filed since v1.0 (2026-07-01)

| File | Status |
|------|--------|
| `chaos/MMI_SWARM_BLUEPRINT_LUNG_V1_2026-06.md` | **FILED** — verbatim v1 |
| `lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md` | **FILED** — verbatim v2 |
| `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` | **FILED** — v2 §3 extract |
| `architecture/MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md` | **FILED** — Matt blocker analysis |
| `architecture/MMI_PURPLE_TEAM_ATTACK_SCOPE_2026-07.md` | **FILED** — scope draft |
| `architecture/MMI_ORCHESTRATOR_SCOPE.md` Addendum 04 | **FILED** — Air-Lock Exception |
| `chaos/RESEARCH_MOVING_TARGET_DEFENSE_2026-07.md` | **FILED** — MTD research lane |
| `chaos/mmi_control_envelope.py` | **FILED** — bounded v0 archive |
| `chaos/deterministic_sanitizer.py` | **FILED** — evidence harvesting sanitizer |
| `chaos/war_room_dashboard_api.py` | **FILED** — kinetic dashboard API concept |
| `architecture/MMI_KINETIC_WARFARE_DASHBOARD_SPEC_2026-07.md` | **FILED** — dashboard UI spec |
| `chaos/MMI_CRYPTOLALIA_TARPIT_2026-07.md` | **FILED** — cryptolalia trap doctrine |
| `chaos/adversarial_cryptolalia_tarpit.py` | **FILED** — cryptolalia generator |

**Still chat-only:** Canary token network alert rules; Mirror Dimension Router integration spec; FastAPI websocket wrapper; **Chaos Lab Provisioner** (prerequisite for evolution matrix).

**Evolution doctrine filed:** `chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md`

**Mirror router filed:** `chaos/MMI_MIRROR_DIMENSION_ROUTER_SPEC_2026-07.md`, `chaos/mirror_dimension_router.py`, `scripts/mirror_dimension_router.py`
