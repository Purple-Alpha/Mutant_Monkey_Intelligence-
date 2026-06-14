# Mutant Monkey Inbox Shield — Thread Handoff
**Date:** June 14 2026
**Reason:** Living document — updated after Collective Immune System build, Codex review, gate, and push.
**Authority:** Matt Nichol — sole signing authority

---

## Current Build State

| Component | Status | Hash |
|---|---|---|
| Phase 1 Infrastructure | GATED | fe355da |
| Phase 2 Knowledge Agents | GATED | 43b5511 |
| Phase 3 Detection Agents | SIGNED — build pending amendment | — |
| Phase 4 ReconciliationAgent | GATED 88 ELITE | 1b2ac0c |
| Phase 5 MutationEngine | GATED | faf963e |
| Blast Radius Controller #89 | GATED 95 ELITE | f1c817e |
| Watcher Agents #85-87 | GATED 95 ELITE | 6da6284 |
| Load Fission #90 | GATED 95 ELITE | 190002f |
| Specialisation Fission #91 | GATED 95 ELITE | c7ef023 |
| Dual LLM Pattern | GATED | 696ee45 |
| Shadow Watcher Swarm Layer 1 | GATED | 03cd7d2 |
| Safe-Stop State Machine #94 | GATED 95 ELITE + Amendment 01 signed | cf3f273 |
| Mode Controller #92 | GATED 95 ELITE | 85b455f |
| Privacy Filter #93 | GATED 95 ELITE | 85b455f |
| Collective Immune System #95 | GATED 95 ELITE | f888ede |

**Test evidence:** CIS focused suite 32 passed / 1 xfailed; related control-plane suites 156 passed / 20 xfailed.

---

## Signed Contracts Waiting For Build

- Load Fission v2 Contract — SIGNED, supersedes #90
- Specialisation Fission v2 Contract — SIGNED, supersedes #91

---

## DEPTH GATE Status

| Pre-condition | Status |
|---|---|
| Blast Radius Controller gated | DONE |
| Watcher Agents gated | DONE |
| Mode Controller signed and gated | DONE |
| Privacy Filter signed and gated | DONE |
| Real tenant onboarded | July 20 — Reatan X8 arrives |

DEPTH GATE is open. Collective Immune System #95 is built, Codex reviewed, Grok-gated 0/0, health-scored 95 ELITE, and pushed.

---

## Push Rule

**AUTO-PUSH IS ON.** Cursor pushes every commit to remote immediately after committing. No hold. No manual push gate.

---

## MMI Update Discipline — MANDATORY

Every session must end with the following before any commit:

1. Cursor writes current state to `MMI_CURRENT_STATE.md`
2. Cursor writes current state to `MMI_THREAD_HANDOFF.md`
3. Both files are included in the final commit of every session
4. If either file is not updated, the session is not complete

Failure to update MMI files = dispatcher drift = wasted build time. This is not optional.

---

## Model Lane Rules

### Research Lane — Dual Model Required

Single-model research is not accepted. Every research pass requires two models so drift can be detected by comparison.

| Step | Model | Role |
|---|---|---|
| Research pass 1 | ChatGPT | First pass — requirements, gap analysis, candidate ranking |
| Research pass 2 | Gemini | Cross-reference ChatGPT output — flag gaps, contradictions, and drift |
| Synthesis | Claude | Receives both outputs, drafts concept doc |

Research loop rule: ChatGPT researches → Gemini cross-references and flags drift → combined output comes to Claude → Claude drafts concept doc. Claude does not draft until both research passes are returned.

### Build Lane — Cursor Builds, Codex Reviews

| Model | Strength | Weakness | Role |
|---|---|---|---|
| Cursor | Strict contract adherence | Under-builds — stays too narrow, misses implied scope | Primary builder — executes the signed contract exactly as written |
| Codex | Broad coverage, catches gaps | Over-builds — adds unrequested scope beyond the contract | Post-build reviewer only — finds what Cursor missed, flags what exceeds contract scope |

Build loop rule: Cursor builds → Codex reviews → anything Codex flags as missing goes back to Cursor to add → anything Codex added beyond contract scope gets stripped before gate.

Codex never builds. Cursor never reviews. They do not swap lanes.

### Design Lane — Claude Only

| Model | Role |
|---|---|
| Claude | Concept docs, contract drafting, governance, spec. Never builds. Never executes. |

### Authority Lane — Matt Nichol Only

- Sole signing authority
- Nothing is built without §11 signature
- Nothing is pushed without commit (auto-push handles the push after commit)
- All operator decisions are Matt's — no model recommends, models inform

---

## Governance Documents Committed

- MUTANT_MONKEY_ORGANISM_DOCTRINE_v1.md — 21 hard invariants, organ boundaries
- ORGANISM_DOCTRINE_GAP_LIST.md — 10 gaps in dependency order
- MMI_CURRENT_STATE.md — command dispatch document
- scripts/mmi_dispatch.py — automated dispatch engine
- scripts/verify_build_truth.py — drift detection, exits non-zero on disagreement
- SWARM_COMMAND_CENTER_PROTOCOL.md — ACTIVE v1.0
- PROJECT_OPERATOR_DELEGATIONS.md — null delegation record
- PROJECT_ACTIVITY_LOG.md — bootstrap and activation entries
- 4. Product_Roadmap/Safe_Stop_State_Machine_Concept_Doc.md — concept doc, June 14 2026
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract_Amendment_01.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Collective_Immune_System_Design_Contract.md — SIGNED June 14th 2026

---

## Open Questions Matt Has Answered

| # | Question | Answer | Locked |
|---|---|---|---|
| OQ-1 | Safe-stop timeout for Mode Controller quorum loss | 120 seconds | YES — in signed contract |
| OQ-2 | Recovery window for two simultaneous CRITICAL watcher events | 300 seconds | YES — in signed contract |
| OQ-3 | Who exits safe-stop | Matt Nichol only | YES — in signed contract |
| OQ-4 | Does Homeostasis stay inside Mode Controller or become a separate contract? | Stays inside Mode Controller. No separate Homeostasis Engine contract this phase. | YES — locked June 14th 2026 |
| OQ-5 | Does baseline ingestion after a closed threat event require operator approval every time or only above a defined risk threshold? | Only above the defined risk threshold. Seven high-impact triggers require approval; below-threshold events go through governed ingestion only after passing all validation gates. | YES — locked June 14th 2026 |

## Open Questions Still Pending

None.

---

## Next Authorized Tasks In Order

1. Run `python3 scripts/mmi_dispatch.py` to confirm current dispatch
2. Phase 3 sender_domain amendment — sign before Phase 3 builds
3. If no signed/build/audit/design item exists, dispatcher routes RESEARCH for the next concept cycle

---

## Repo Location

WSL: /home/socialarchitect/northstar
Branch: safety/queue-drift-cleanup-20260528
GitHub: https://github.com/Purple-Alpha/Mutant_Monkey_Intelligence-.git

---

## Social Architect Project

Completely separate project at C:\Architectapp_clean\intelligence\
Nothing to do with Mutant Monkey.
Do not mix. Do not reference in Mutant Monkey threads.
Leave on top shelf — parked, protected, separate.

---

## How To Start The New Thread

Paste this into the new Claude thread to pick up exactly where we left off:

I am continuing the Mutant Monkey Inbox Shield build session.
The full project context is in the repo at /home/socialarchitect/northstar
Read MMI_THREAD_HANDOFF.md from the repo root and confirm current state before we proceed.
The Social Architect project at C:\Architectapp_clean is a completely separate project — do not mix it with Mutant Monkey under any circumstances.
