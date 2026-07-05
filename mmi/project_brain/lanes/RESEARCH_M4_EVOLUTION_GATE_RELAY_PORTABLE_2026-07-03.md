# M4 Evolution Gate — Portable Research Relay (no repo mount required)

**For:** ChatGPT + Gemini research lane  
**From:** Matt via Cursor relay  
**Date:** 2026-07-03  
**Status:** RESEARCH AUTHORIZED — deliver findings as paste-back markdown

---

## Path correction (read this first)

| Path | Valid here? | Notes |
|------|-------------|-------|
| `/home/socialarchitect/northstar` | **NO** in ChatGPT/Gemini runtime | Legacy/alternate MMI authority path — **not mounted** in your session |
| `C:\Architectapp_clean` | **YES** — Matt's Windows authority repo | Cursor lane has full tree |
| `/mnt/c/Architectapp_clean` | **YES** — WSL view of same repo | Use if Matt gives you WSL file access |
| `mmi/project_brain/...` | **YES** — relative paths below | All paths relative to authority repo root |

**Do not guess file contents.** If you cannot read the repo, use **§ Embedded doctrine** below + deliver **`RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md`** as a complete markdown artifact Matt will paste into:

`mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md`

Cursor will file it. Mark any unverified claims as `[UNVERIFIED — repo not read]`.

---

## Current pipe snapshot (2026-07-03)

```json
{
  "evolution_gate": "RESEARCH_AUTHORIZED",
  "evolution_gate_research": "IN_PROGRESS",
  "agi_pathway_step5_genomic_loop": "GATED",
  "client_email_lanes_gated": "GATED",
  "genomic_v2_24_7": "DEFERRED_POST_M4",
  "central_brain_step6": "NOT_SPECIFIED"
}
```

---

## Task id

`mmi-m4-evolution-gate-research`

**Deliverable:** `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` with all items in § Required deliverables.

**Forbidden in output:** PERFECT closed, evolution gate GATED, build authorization, 24/7 genomic v2 bundled into M4.

---

## Embedded doctrine (authoritative excerpts — repo not required)

### A. What M4 is

M4 = **PERFECT** tier on the Destructive Evolution Matrix — **not** AGI §5 step 6.

From `MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md` Milestone 4:

> Run an aggressive, un-throttled automated hacking framework inside the **chaos clone** for **48 hours straight**. Jailbreaks, formatting exploits, timing attacks, memory extraction. Result: never drop a real production database request, never leak a real secret, generate draft patches for every exploit tried, drain 100% of attacker's simulated token wealth.

From `MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md` §6:

> **To advance to PERFECT:** Un-throttled 48-hour automated assault, **zero critical-class misses**, **zero authority touch**, attacker token budget depleted (**M4 — not built**).

Evolution ladder:

```text
Tier 1–2  → GOOD
Tier 3    → GREAT candidate (M2 tarpit verified)
Tier 4    → OUTSTANDING candidate (M3 mesh — not built)
Continuous 48h → PERFECT (M4 — not built)
```

### B. Component map (Evolution matrix — status as of 2026-07-03)

| Milestone | Required | Status |
|-----------|----------|--------|
| M1 | Token jail / signed envelope edge | Concept — control envelope **BUILT** |
| M2 | Mirror router + cryptolalia tarpit | Router **BUILT** |
| M3 | Air-Lock mesh, sanitizer, dashboard telemetry | Partial |
| **M4** | **48h chaos clone run, Canary alert rules, AFE metrics** | **Canary rules NOT FILED** |
| All | Chaos Lab Provisioner | **BUILT** — `scripts/chaos_lab_provisioner.py` |

### C. Already GATED (do not re-open)

| Item | Status |
|------|--------|
| Phase 1 stability (3× Tier 4) | CLOSED |
| Gate B proof gate | CLOSED |
| Control envelope budget/dead-man (AGI §5 step 3) | CLOSED |
| Console Ed25519 gate (step 4) | CLOSED |
| Genomic realignment loop CLI v1 (step 5) | GATED |
| Client email lanes v1 | GATED |

### D. Known blockers research must resolve

1. **48h assault runner** — harness shape, evidence JSON, where state lives (`/tmp/mmi_chaos_lab/` pattern)
2. **M4 canary alert rules** — NOT the same as L8 `canary_metadata_layer.py` (honeytoken pre-signature hard-drop); M4 rules **not filed**
3. **Host boundary daemon** — `purple_exfil_socket_path` scenario; Windows host vs WSL — see prior research `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` if accessible
4. **M3 mesh** — hard prereq for M4 or parallel?
5. **Gate C** — 15-min soak vs 48h M4 relationship
6. **AFE ledger** — what exists vs must be instrumented
7. **Genomic v2 24/7** — explicitly **deferred post-M4** — do not merge

### E. Non-goals (AGI pathway §6 — paraphrase)

- No unbounded self-authored runtime code
- No autonomy without budget + kill-switch
- No human sign-off on intent alone (evidence bundle required)
- No "AGI achieved" marketing claim
- No Phase 3 / PERFECT claim until all falsifiers survived on record

---

## Required deliverables (findings doc sections)

1. **Normative definition** — operational paragraph + numbered pass lines
2. **Component dependency DAG** — M4 vs M3 vs host boundary vs canary vs Gate C vs AFE
3. **48h harness sketch** — runner, cadence, `overall_gate_status` JSON schema
4. **Canary alert rules draft** — closed signal enum, destinations, fail-closed actions
5. **Host boundary scope** — Windows-native vs WSL for Matt's dev host
6. **Falsifier table** — ≥8 scenarios (T1–T8), expected terminals
7. **Honest gaps** — research-only vs needs Claude spec
8. **Next authorization string** — e.g. `authorize spec M4 evolution gate` (NOT build)

---

## Copy-paste prompt (Matt → ChatGPT/Gemini)

```
PROJECT: MMI
TASK: mmi-m4-evolution-gate-research
LANE: Research only — NOT build

PATH NOTE: /home/socialarchitect/northstar is NOT available in your runtime.
Authority repo on Matt's machine: C:\Architectapp_clean (WSL: /mnt/c/Architectapp_clean).
Use the portable relay below — do NOT invent repo file contents.

READ: (embedded in relay) M4 = 48h PERFECT proof in chaos clone; canary alert rules NOT FILED;
host boundary OUTSTANDING; steps 1–5 + email lanes GATED; genomic v2 deferred post-M4.

DELIVER: Complete markdown file RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md
with 8 sections listed in relay. Mark unverified items explicitly.
Do NOT claim PERFECT or evolution gate closed.
```

---

## After research

Matt pastes findings → Cursor files at `mmi/project_brain/lanes/` → Claude spec lane → Codex BUILDABLE → separate build auth.

---

## File index (for Matt / connectors with repo access)

If your connector CAN reach `C:\Architectapp_clean` or `/mnt/c/Architectapp_clean`, read in order:

1. `mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md`
2. `mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md`
3. `mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md` (§6)
4. `mmi/project_brain/architecture/MMI_AGI_EVOLUTION_PATHWAY.md` (§3 Phase 3, §5, §6)
5. `mmi/project_brain/lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md`
6. `mmi/project_brain/status/MMI_PIPE_STAGING.json`
