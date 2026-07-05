# MMI Canadian IR — Fit Assessment

Date: 2026-06-30  
Authority: Matt (Super)  
Source: Matt quick research + IR conversation (PIPEDA, Law 25, CCCS, 6-section framework)

---

## Does this fit MMI?

**Yes — in the Security Intel / war room artifact lane, not in core queue mechanics.**

| Your work | MMI home | Why |
|-----------|----------|-----|
| Canadian-first IR template | `intel/templates/INCIDENT_RESPONSE_TEMPLATE.md` | Perfect war room artifact — geography-specific, impact-first |
| 6-section IR questions | Template body sections | Standard IR structure; legal section = Canadian |
| Decision gate (if-then) | `intel/INCIDENT_DECISION_GATE.md` | Compliance **checklist** — not automated engine in v1.1 |
| Commander checklist | `opsec/INCIDENT_COMMANDER_CHECKLIST.md` | Role clarity — Commander / Tech / Compliance |
| Local playbook (CCCS, CAFC, PIPEDA) | `intel/LOCAL_INCIDENT_PLAYBOOK.md` | Evidence backer with Canadian primary links |
| Purple team + scoring matrix research | `lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md` | Enterprise reference; MMI-adapted tiers + legal boundary |
| Generic Verizon/IBM stats | Research lane only | Must use `[Global Data — Requires Localization]` |

MMI war room **v1** shows pipe + backup. **v1.1** links to these IR docs when filed — the template is the "what to do in crisis" layer; war room CLI is the "what's happening in the project now" layer.

---

## Is Canada-first vital?

| Area | Canada-first? | Reason |
|------|---------------|--------|
| **Security Intel research** | **Yes — mandatory** | Matt operates in Canada; PIPEDA/Law 25/CCCS/CAFC are the real clocks |
| **IR templates & playbooks** | **Yes — mandatory** | Wrong jurisdiction = wrong legal deadlines and wrong reporting portals |
| **Threat technique mapping (MITRE)** | Global framework OK | Techniques are universal; **impact and legal** sections stay Canadian |
| **Queue, backup, war room CLI** | Neutral | Works the same regardless of geography |
| **Cold B2 backup** | Neutral | Insurance layer — not jurisdiction-specific |

**Bottom line:** Keep the **whole project** as one MMI stack, but keep the **Truth Database and IR lane Canada-first** — that is not optional for Matt. It is the difference between an operator tool and US-vendor cosplay.

---

## What is not filed yet

Matt's IR template content from the conversation is **not on disk**. Next step: Claude or Matt files `intel/templates/INCIDENT_RESPONSE_TEMPLATE.md` using:

- `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` (Canada-first)
- 6-section framework from conversation
- PIPEDA / Law 25 notification triggers
- Impact-first fields (payroll, supply chain, workday)

---

## Recommended pipeline (after intel brief template)

1. `mmi-incident-response-template` — Claude — file IR template  
2. `mmi-incident-decision-gate` — Claude — if-then regulatory matrix  
3. `mmi-incident-commander-checklist` — Claude — roles checklist  
4. `mmi-local-incident-playbook` — Gemini + ChatGPT verify — CCCS/CAFC/PIPEDA links  

Then: war room v1.1 Codex task — add brain links to IR artifacts.

---

## Hard stops

- IR docs are **advisory** — MMI does not file CAFC/OPC reports automatically  
- No SOAR, no live telemetry, no endpoint containment from template  
- All legal claims need Canadian primary source or `NEEDS VERIFY` / `Insufficient Data`
