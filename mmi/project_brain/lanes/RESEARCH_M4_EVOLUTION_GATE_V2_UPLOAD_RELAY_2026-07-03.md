# M4 Research Packet v2 — Upload Relay

**Date:** 2026-07-03  
**Authorization:** `AUTHORIZE RESEARCH PACKET V2 ONLY` — no spec, no build, no gate closure  
**Task:** `mmi-m4-evolution-gate-research-v2`

---

## ZIP locations (attach actual file to ChatGPT)

| Path | Size |
|------|------|
| `C:\MMI\mmi\project_brain\lanes\m4_research_packet_v2_2026-07-03.zip` | ~790 KB |
| `%TEMP%\m4_research_packet_v2_2026-07-03.zip` | same copy |

**212 files** — includes full `mmi/project_brain/status/`, `tasks.json`, Evolution Matrix M4, Weapon Matrix §6, M4/canary/host-boundary/48h/genomic corpus, harnesses + tests.

**Excluded:** venv, `.venv_kinetic`, `.git`, `node_modules`, `.pytest_cache`, `__pycache__`

---

## Rebuild command

```bash
python C:\MMI\mmi\project_brain\lanes\build_m4_research_packet_v2.py
```

---

## ChatGPT prompt (after attaching ZIP)

```
PROJECT: MMI
TASK: mmi-m4-evolution-gate-research-v2
LANE: Research revision only

Attached: m4_research_packet_v2_2026-07-03.zip (ACTUAL ZIP FILE — not a terminal listing)
Authority repo: C:\MMI

Read directly from ZIP:
1. mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md
2. mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md (M4)
3. mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md (§6)
4. mmi/project_brain/status/MMI_PIPE_STAGING.json + closeouts
5. tasks.json

Revise RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md:
- Remove [UNVERIFIED] where source text was read from ZIP
- Keep §1–§8 structure
- Cite exact repo paths from ZIP
- Do NOT claim PERFECT or M4 closed
- Do NOT authorize spec or build

Deliver complete markdown for Cursor filing at:
mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md
```

---

## After v2 findings accepted

Matt: `authorize spec M4 evolution gate` → Claude (NOT before v2 grounded findings).

---

## v1 vs v2

| | v1 | v2 |
|---|----|----|
| Files | 19 curated | 212 scoped |
| status/ | partial | **full** |
| tasks.json | no | **yes** |
| Topic grep corpus | minimal | M4/PERFECT/canary/48h/genomic expanded |
| Problem | ZIP log uploaded, not file | Attach `.zip` directly |
