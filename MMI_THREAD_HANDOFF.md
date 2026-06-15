# Mutant Monkey Inbox Shield — Thread Handoff
**Date:** June 14 2026
**Reason:** Living document — MMI credit-free rule added, TI Daemon signed, adversarial loop locked.
**Authority:** Matt Nichol — sole signing authority

---

## CRITICAL — MMI CREDIT-FREE RULE

**Claude never reads MMI files via MCP. Claude never writes MMI files via MCP.**

The correct flow is:

1. Run `python3 scripts/mmi_dispatch.py` locally — it reads all MMI files and prints current state
2. Paste the dispatcher output into the Claude chat at the start of each session
3. Claude reads it as conversation text — zero MCP calls, zero credits burned on file reads
4. When Claude produces updated MMI content, it outputs the text in chat
5. You paste that text to Cursor — Cursor writes it to disk
6. Cursor commits and pushes

Claude touching MMI files directly via MCP = wasted credits on a text file. This rule is permanent.

---

## Current Build State

| Component | Status | Adversarial Suite | Hash |
|---|---|---|---|
| Phase 1 Infrastructure | GATED | NOT YET RUN | fe355da |
| Phase 2 Knowledge Agents | GATED | NOT YET RUN | 43b5511 |
| Phase 3 Detection Agents | SIGNED — build pending amendment | NOT YET RUN | — |
| Phase 4 ReconciliationAgent | GATED 88 ELITE | NOT YET RUN | 1b2ac0c |
| Phase 5 MutationEngine | GATED | NOT YET RUN | faf963e |
| Blast Radius Controller #89 | GATED 95 ELITE | NOT YET RUN | f1c817e |
| Watcher Agents #85-87 | GATED 95 ELITE | NOT YET RUN | 6da6284 |
| Load Fission #90 | GATED 95 ELITE | NOT YET RUN | 190002f |
| Specialisation Fission #91 | GATED 95 ELITE | NOT YET RUN | c7ef023 |
| Dual LLM Pattern | GATED | NOT YET RUN | 696ee45 |
| Shadow Watcher Swarm Layer 1 | GATED | NOT YET RUN | 03cd7d2 |
| Safe-Stop State Machine #94 | GATED 95 ELITE + Amendment 01 SIGNED | NOT YET RUN | cf3f273 |
| Mode Controller #92 | GATED 95 ELITE | NEXT IN ADVERSARIAL QUEUE | 85b455f |
| Privacy Filter #93 | GATED 95 ELITE — ADVERSARIALLY HARDENED | PASSED 0/0 | 47b33dd |
| Privacy Filter Adversarial Suite #98 | GATED 95 ELITE | PASSED 0/0 | 47b33dd |
| Collective Immune System #95 | GATED 95 ELITE | NOT YET RUN | f888ede |
| Cortex / Immune Interface #96 | GATED 95 ELITE | NOT YET RUN | 656b282 |
| Memory Consolidation #97 | GATED 95 ELITE | NOT YET RUN | e102965 |

---

## Signed Contracts Waiting For Build

- Load Fission v2 — SIGNED, supersedes #90
- Specialisation Fission v2 — SIGNED, supersedes #91
- Threat Intelligence Daemon — SIGNED June 14th 2026 — builds to `/home/socialarchitect/mutant_monkey_intel/`

---

## DEPTH GATE Status

DEPTH GATE is open. Mode Controller and Privacy Filter both gated.

---

## Push Rule

**AUTO-PUSH IS ON.** Cursor pushes every commit immediately after committing.

---

## MMI Update Discipline — MANDATORY

Every session must end with:
1. Cursor writes current state to `MMI_CURRENT_STATE.md`
2. Cursor writes current state to `MMI_THREAD_HANDOFF.md`
3. Both files included in final commit
4. If either file not updated, session is not complete

---

## Model Lane Rules

### Research Lane — Three Passes Required

| Step | Model | Role |
|---|---|---|
| Research pass 1 | ChatGPT | First pass — requirements, gap analysis, candidate ranking |
| Research pass 2 | Gemini | Cross-reference ChatGPT — flag gaps, contradictions, drift |
| Concept red-team | Gemini | Adversarial pass — attack the concept, find bypasses, poisoning vectors, blind spots |
| Synthesis | Claude | Drafts concept doc only after all three passes returned |

### Build Lane

| Model | Role |
|---|---|
| Cursor | Primary builder — executes signed contract exactly |
| Codex | Post-build reviewer — finds gaps, flags over-scope. Never builds. |

Build loop: Cursor builds → Codex reviews → adversarial suite runs → failures patched → `complete_gate.py 0/0` on functional AND adversarial → GATED.

**No component is GATED without a passing adversarial suite.**

### Design Lane

| Model | Role |
|---|---|
| Claude | Concept docs, contracts, governance, spec. Never builds. Never reads/writes MMI via MCP. |

### Authority Lane

Matt Nichol — sole signing authority. All decisions are Matt's.

---

## Adversarial Suite Rules

Three questions every suite must answer:
1. What does this component trust — and can that trust be abused?
2. What does this component block — and can those blocks be bypassed?
3. What does this component produce — and can that output be spoofed?

Every test must be able to fail. A test that cannot fail is not a test.

---

## Retroactive Adversarial Queue

| Priority | Component | Status |
|---|---|---|
| 1 | Privacy Filter #93 | DONE — HARDENED |
| 2 | Mode Controller #92 | NEXT — send contract to Gemini |
| 3 | ReconciliationAgent #88 | PENDING |
| 4 | Blast Radius Controller #89 | PENDING |
| 5 | Safe-Stop State Machine #94 | PENDING |
| 6 | Collective Immune System #95 | PENDING |
| 7 | Cortex / Immune Interface #96 | PENDING |
| 8 | Watcher Agents #85-87 | PENDING |
| 9 | Fission v2 #90/#91 | PENDING |
| 10 | Mutation Engine | PENDING |
| 11 | Phase 1 Infrastructure | PENDING |
| 12 | Phase 2 Knowledge Agents | PENDING |
| 13 | Shadow Watcher Swarm Layer 1 | PENDING |
| 14 | Dual LLM Pattern | PENDING |
| 15 | Memory Consolidation #97 | PENDING |

---

## Governance Documents Committed

- MUTANT_MONKEY_ORGANISM_DOCTRINE_v1.md
- ORGANISM_DOCTRINE_GAP_LIST.md
- MMI_CURRENT_STATE.md + MMI_THREAD_HANDOFF.md
- scripts/mmi_dispatch.py + scripts/verify_build_truth.py
- SWARM_COMMAND_CENTER_PROTOCOL.md v1.0
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md — SIGNED
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract_Amendment_01.md — SIGNED
- 4. Product_Roadmap/Collective_Immune_System_Design_Contract.md — SIGNED
- 4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md — SIGNED
- 4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Concept_Doc.md
- 4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md — SIGNED
- 4. Product_Roadmap/Privacy_Filter_Adversarial_Test_Suite_Contract.md — SIGNED — GATED 0/0
- 4. Product_Roadmap/Threat_Intelligence_Daemon_Concept_Doc.md
- 4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md — SIGNED June 14th 2026

---

## Open Questions

All answered and locked. None pending.

---

## Next Authorized Tasks In Order

1. Paste `mmi_dispatch.py` output at session start — do not read via MCP
2. Send Mode Controller #92 signed contract to Gemini with adversarial attack prompt
3. Claude drafts Mode Controller adversarial test suite after Gemini returns
4. Matt signs — Cursor builds — Codex reviews — gate
5. Build Threat Intelligence Daemon to `/home/socialarchitect/mutant_monkey_intel/`
6. Build Load Fission v2 — SIGNED
7. Build Specialisation Fission v2 — SIGNED
8. Continue gap contracts — gaps 6, 7, 8, 9, 10

---

## Repo Location

WSL: /home/socialarchitect/northstar
Branch: safety/queue-drift-cleanup-20260528
GitHub: https://github.com/Purple-Alpha/Mutant_Monkey_Intelligence-.git

TI Daemon: /home/socialarchitect/mutant_monkey_intel/ — separate, not committed to Northstar

---

## Social Architect Project

Separate project at C:\Architectapp_clean\intelligence\
Do not mix with Mutant Monkey. Ever.

---

## How To Start The New Thread

Paste this into the new Claude thread:

I am continuing the Mutant Monkey Inbox Shield build session.
Run python3 scripts/mmi_dispatch.py and paste the output here so Claude can read state without burning credits on MCP file reads.
The Social Architect project at C:\Architectapp_clean is a completely separate project — do not mix it with Mutant Monkey under any circumstances.
