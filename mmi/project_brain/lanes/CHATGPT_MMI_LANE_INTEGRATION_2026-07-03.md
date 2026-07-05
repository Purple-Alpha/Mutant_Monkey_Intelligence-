# Adding ChatGPT to the MMI Lane Mix

**Status:** OPERATOR GUIDE — not build auth  
**Authority:** Matt (Super)  
**Date:** 2026-07-03  

---

## Lane map (do not blur)

| Lane | Tool | Does | Does NOT |
|------|------|------|----------|
| **Research** | **ChatGPT + Gemini** | Read doctrine, threat landscape, falsifiers, findings docs | Spec, code, GATED |
| **Spec / architecture** | Claude | Normative specs, handoffs, § schemas | Implement, claim GATED |
| **Plan + diff review** | Codex | BUILDABLE / NOT BUILDABLE; CLEAN / NOT CLEAN | Write repo code |
| **Implement + test** | Cursor | Build, pytest, harness, file handoffs | GATED closeout alone |
| **GATED** | Matt | `authorize build`, `authorize research`, final GATED | — |

ChatGPT belongs in **research only** unless you explicitly change lane rules.

---

## Recommended workflow (M4 example)

```text
Matt: authorize research M4 evolution gate
        ↓
Cursor: files RESEARCH brief + portable relay + builds ZIP
        ↓
Matt: uploads ZIP to ChatGPT (or Gemini)
        ↓
ChatGPT: reads packet → writes FINDINGS markdown
        ↓
Matt: paste findings → Cursor files at mmi/project_brain/lanes/
        ↓
Matt: authorize spec M4 evolution gate → Claude
        ↓
Codex plan review → BUILDABLE
        ↓
Matt: authorize build → Cursor
        ↓
Codex diff review → CLEAN → completion gate → Matt GATED
```

**One model, one lane per hop.** Matt relays prose between tools.

---

## Three ways to feed ChatGPT repo truth

### 1. Targeted ZIP upload (recommended now)

**Best for:** private repo, no GitHub connector, M4-sized research.

```powershell
# Already built for you:
# C:\Users\mattn\AppData\Local\Temp\m4_research_packet_targeted_2026-07-03.zip

# Rebuild anytime:
powershell -NoProfile -File C:\Architectapp_clean\mmi\project_brain\lanes\build_m4_research_packet.ps1
```

Upload ZIP into ChatGPT chat → prompt with task id `mmi-m4-evolution-gate-research`.

### 2. GitHub connector

**Best for:** ongoing search across full repo without re-zipping.

Requirements:
- Repo pushed to GitHub (private OK if ChatGPT authorized)
- ChatGPT **Settings → Connectors → GitHub** enabled for `Architectapp_clean` (or org repo name)
- Repo name must match what connector indexes — **not** `northstar` unless that is the actual GitHub repo name

If connector cannot find repo: wrong name, wrong org, or token scope.

### 3. Portable relay only (fallback)

Use `RESEARCH_M4_EVOLUTION_GATE_RELAY_PORTABLE_2026-07-03.md` when ZIP upload fails. Findings may carry `[UNVERIFIED]` markers — acceptable for first pass, not for spec lane.

---

## Path hygiene (avoid northstar confusion)

| Path | Use |
|------|-----|
| `C:\Architectapp_clean` | Windows authority repo (Cursor) |
| `/mnt/c/Architectapp_clean` | WSL view of same repo |
| `/home/socialarchitect/northstar` | **Different machine/path** — do not cite unless that tree is actually mounted |

Always tell ChatGPT: **authority repo is Architectapp_clean**.

---

## ChatGPT prompt templates

### Pass 1 — Ground findings (paste after ZIP upload)

```
PROJECT: MMI
TASK: mmi-m4-evolution-gate-research-v2
LANE: Research only — NOT spec, NOT build, NOT GATED

Attached: mmi_m4_research_packet_v2_2026-07-03.zip (~791 KB, 212 files)
Authority repo: C:\Architectapp_clean

Read RESEARCH_M4_EVOLUTION_GATE_2026-07.md first.
Deliver complete markdown: RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md
Sections: (1) normative definition (2) component DAG (3) harness sketch
(4) canary alert rules draft (5) host boundary scope (6) falsifier table
(7) honest gaps (8) next auth string e.g. authorize spec M4 evolution gate

Cite paths inside the ZIP. Remove [UNVERIFIED] only where read from ZIP.
Do NOT claim PERFECT closed.
```

### Pass 2 — Adversarial critique (mandatory before spec)

**Canonical template:** `lanes/MMI_CHATGPT_ADVERSARIAL_RESEARCH_PROMPT_FRAMEWORK_2026-07.md`

Copy **SINGLE PASTE** from that file after pasting (or attaching) the full findings document. Covers:

1. Alternative paths (formal verification, fuzz, sandbox vs endurance chaos)
2. Hidden coupling (parallel vs sequential dependency risks)
3. Canary blind spots (evasion, host escape, evidence tampering)
4. Clock honesty flush (scoped reset vs full reset statistical risk)
5. Compliance & safety rating (readiness score + missing interim milestones)

**Do not** `authorize spec` until Pass 2 output is incorporated into findings (Cursor filing).

---

## Gemini pairing

Per MMI routing: **ChatGPT + Gemini = research**. Options:
- Same ZIP to both; merge findings (Matt picks conflicts)
- Split: ChatGPT → component DAG + falsifiers; Gemini → host boundary + canary research
- One primary writer, one reviewer pass

Do not run Gemini on build or Codex review lanes.

---

## What not to do

- Do not ask ChatGPT to `authorize build` or close GATED
- Do not ask ChatGPT to edit `ops/` or run harnesses — Cursor lane
- Do not ask Cursor to write research findings without Matt paste-back (or file drop)
- Do not use `/home/socialarchitect/northstar` in prompts unless that mount exists on the research machine

---

## Next action (M4, today)

1. Findings v2.1 already filed at `lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md` (includes adversarial revision)  
2. For future research lanes: Pass 1 ZIP → Pass 2 adversarial (`MMI_CHATGPT_ADVERSARIAL_RESEARCH_PROMPT_FRAMEWORK_2026-07.md`) → Cursor filing  
3. Then: `authorize spec M4 evolution gate` → Claude  
