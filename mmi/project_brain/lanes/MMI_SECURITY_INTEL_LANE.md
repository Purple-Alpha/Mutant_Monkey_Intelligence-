# MMI Security Intel Lane

Date activated: 2026-06-29  
Authority: Matt (Super) — decision **A** for both Gemini research briefs  
Maintained by: Cursor PM

---

## Purpose

A **bounded product lane** for SMB-focused threat research, synthesis, and operator-facing intel — separate from core MMI queue/war room/backbone, but living in the same repo and project brain.

This lane does **not** replace Social Architect, DAX, Trades, or NorthStar.

---

## Lane owners

| Role | Owner | Delivers |
|------|-------|----------|
| Super | Matt | Product direction, build auth, external claims approval |
| PM | Cursor | Research intake, pipeline, scope hygiene |
| Research | Gemini | Primary threat landscape / ATT&CK research — **Canada-first** per `MMI_RESEARCH_RIGOR_PROTOCOL.md` |
| Deep research | ChatGPT | Source verification, counter-evidence — **Canada-first cross-ref** |
| Design | Claude | MVP architecture, intel brief templates |
| Audit | Gemini Paid API | Fact-check pass on stats before publish |
| Backbone | Codex | Local tools only when MVP spec authorizes (e.g. intel index CLI) |

---

## Research inventory

| File | Topic |
|------|--------|
| `lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md` | Polymorphic ransomware / email fraud |
| `lanes/RESEARCH_smb_threat_landscape_2026-06.md` | SMB threat landscape |

All research files are **artifacts** until Evaluator/source pass marks them citation-ready.

**Research rigor (mandatory):** `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — Primary Source Requirement, Confidence Scoring, Crucible Protocol. All research prompts must reference it.

---

## In scope (security intel lane)

- Ingest research into `mmi/project_brain/lanes/`
- Synthesize MVP product scope and architecture docs
- Operator checklists tied to **local-first** recovery (backup, opsec)
- ATT&CK-tagged summaries for SMB operators

---

## Out of scope (hard stops)

- Endpoint Ingress/Evaluator/Containment agent swarm (research only — not build)
- SEG/EDR product integration without Matt auth
- npm / `web/` Social Architect surfaces
- NorthStar bridge
- Presenting unsourced Gemini stats as fact externally

---

## Pipeline sequence (after `mmi-war-room-v1`)

1. `mmi-security-intel-product-scope` — Claude — MVP boundaries doc  
2. `mmi-security-intel-research-verify` — ChatGPT — source verification on stats  
3. Future Codex tasks only after MVP spec + Matt build auth

---

## Authority

If this lane conflicts with `MMI_ACTIVE_SCOPE.md` core MMI ops, **core ops win** unless Matt explicitly reprioritizes.
