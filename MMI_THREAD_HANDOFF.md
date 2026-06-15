# Mutant Monkey Inbox Shield — Thread Handoff
**Date:** June 14 2026
**Reason:** Living document — adversarial testing loop added, retroactive stress test queue opened.
**Authority:** Matt Nichol — sole signing authority

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
| Mode Controller #92 | GATED 95 ELITE | NOT YET RUN | 85b455f |
| Privacy Filter #93 | GATED 95 ELITE | NOT YET RUN | 85b455f |
| Collective Immune System #95 | GATED 95 ELITE | NOT YET RUN | f888ede |
| Cortex / Immune Interface #96 | GATED 95 ELITE | NOT YET RUN | 656b282 |
| Memory Consolidation / Tenant Baseline Ingestion #97 | GATED 95 ELITE | NOT YET RUN | e102965 |

**Test evidence:** Gap 5 Tenant Baseline Ingestion focused suite 30 passed / 1 xfailed; related baseline/boundary suites 167 passed / 1 skipped / 10 xfailed.

---

## Signed Contracts Waiting For Build

- Load Fission v2 Contract — SIGNED, supersedes #90
- Specialisation Fission v2 Contract — SIGNED, supersedes #91

---

## DEPTH GATE Status

DEPTH GATE is open. Mode Controller and Privacy Filter both gated.

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

Single-model research is not accepted. Every research pass requires two models.

| Step | Model | Role |
|---|---|---|
| Research pass 1 | ChatGPT | First pass — requirements, gap analysis, candidate ranking |
| Research pass 2 | Gemini | Cross-reference ChatGPT output — flag gaps, contradictions, drift |
| Concept red-team | Gemini | Second Gemini pass with adversarial prompt — attack the concept, find bypasses, poisoning vectors, doctrine drift, blind spots |
| Synthesis | Claude | Receives all three outputs, drafts concept doc. Does not draft until research and red-team passes are both returned. |

### Build Lane — Cursor Builds, Codex Reviews, Adversarial Suite Gates

| Model | Strength | Weakness | Role |
|---|---|---|---|
| Cursor | Strict contract adherence | Under-builds — misses implied scope | Primary builder — executes signed contract exactly |
| Codex | Broad coverage, catches gaps | Over-builds — adds unrequested scope | Post-build reviewer only — finds gaps, flags over-scope |

Build loop rule:
1. Cursor builds against signed contract
2. Codex reviews — gaps go back to Cursor, over-scope stripped
3. Adversarial test suite runs — finds bypasses, poisoning vectors, weaknesses
4. Any adversarial failures go back to Cursor
5. `complete_gate.py 0/0` on both functional tests AND adversarial suite
6. Component is GATED only when both pass

**A component cannot be GATED without a passing adversarial test suite. No exceptions.**

### Design Lane — Claude Only

| Model | Role |
|---|---|
| Claude | Concept docs, contract drafting, governance, spec. Never builds. Never executes. |

### Authority Lane — Matt Nichol Only

- Sole signing authority
- All operator decisions are Matt's — no model recommends, models inform

---

## Adversarial Test Suite Rules

Every adversarial suite asks exactly three questions against its component:

1. **What does this component trust — and can that trust be abused?**
   Test every input, signal, and assumption the component depends on. Inject poisoned inputs. Spoof trusted sources. Exceed stated limits.

2. **What does this component block — and can that block be bypassed?**
   Attempt every forbidden action from every angle. Try legitimate-looking payloads that smuggle forbidden content. Try timing attacks. Try partial compliance.

3. **What does this component produce — and can that output be poisoned or spoofed?**
   Verify that outputs cannot be forged. Verify that a compromised upstream cannot produce outputs that look valid. Verify that high-confidence outputs on poisoned inputs are caught.

Each adversarial suite must include at minimum:
- Boundary violation attempts (every hard invariant tested from the attacker side)
- Poisoned input injection
- Trust assumption abuse
- Bypass attempts on every forbidden action
- Output spoofing attempts
- Cascade failure simulation (what happens if this component is compromised)

---

## Retroactive Adversarial Stress Test Queue

All previously gated components need adversarial suites run against them immediately. Priority order is by attack surface and downstream blast radius if compromised.

| Priority | Component | Why first |
|---|---|---|
| 1 | Privacy Filter #93 | Cross-tenant data leak is the highest blast radius failure |
| 2 | Mode Controller #92 | Epoch/mode authority — compromise creates split-brain or false NORMAL state |
| 3 | ReconciliationAgent #88 | Sole verdict producer — poisoned verdict poisons all downstream decisions |
| 4 | Blast Radius Controller #89 | Gateway lifecycle — bypass means uncontained dispatch |
| 5 | Safe-Stop State Machine #94 | If safe-stop can be prevented or faked, organism cannot halt safely |
| 6 | Collective Immune System #95 | Coordination layer — compromise means immune components work against each other |
| 7 | Cortex / Immune Interface #96 | Hidden channel creation bypasses organ boundary |
| 8 | Watcher Agents #85-87 | False CRITICAL or suppressed CRITICAL both cause downstream failures |
| 9 | Fission v2 #90/#91 | Unauthorized fission = uncontrolled child spawning |
| 10 | Mutation Engine #95 | Unauthorized mutation = uncontrolled runtime change |
| 11 | Phase 1 Infrastructure | Foundation — compromise undermines everything above |
| 12 | Phase 2 Knowledge Agents | Evidence poisoning at source layer |
| 13 | Shadow Watcher Swarm Layer 1 | Observation suppression or false escalation |
| 14 | Dual LLM Pattern | False agreement between models |
| 15 | Gap 5 Baseline Ingestion | Evidence-to-baseline poisoning — covered extensively in contract but needs red-team |

### Retroactive Adversarial Process

For each component in the queue:
1. Gemini receives the signed contract and the built code summary
2. Gemini prompt: "Attack this component. Find every way it fails, gets bypassed, gets poisoned, produces false outputs, or makes Mutant Monkey blind. Do not find design improvements. Find attack surfaces."
3. Gemini output comes to Claude
4. Claude drafts the adversarial test suite as a signed addendum to the component's contract
5. Matt signs
6. Cursor implements the adversarial tests
7. Tests run — any failure is a real vulnerability, not a test failure
8. Vulnerabilities patched before component is considered adversarially hardened

### Concept Validation Red-Team

All previously signed concept docs also need adversarial passes. Priority:

| Priority | Concept Doc |
|---|---|
| 1 | Gap 5 Memory Consolidation — baseline poisoning is the highest risk |
| 2 | Collective Immune System — coordination layer failures |
| 3 | Cortex / Immune Interface — hidden channel risks |
| 4 | Safe-Stop State Machine — safe-stop prevention or bypass |

---

## Governance Documents Committed

- MUTANT_MONKEY_ORGANISM_DOCTRINE_v1.md
- ORGANISM_DOCTRINE_GAP_LIST.md
- MMI_CURRENT_STATE.md
- scripts/mmi_dispatch.py
- scripts/verify_build_truth.py
- SWARM_COMMAND_CENTER_PROTOCOL.md — ACTIVE v1.0
- PROJECT_OPERATOR_DELEGATIONS.md
- PROJECT_ACTIVITY_LOG.md
- 4. Product_Roadmap/Safe_Stop_State_Machine_Concept_Doc.md
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract_Amendment_01.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Collective_Immune_System_Design_Contract.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md — SIGNED June 14th 2026
- 4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Concept_Doc.md
- 4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md — SIGNED June 14th 2026

---

## Open Questions Matt Has Answered

| # | Question | Answer | Locked |
|---|---|---|---|
| OQ-1 | Safe-stop timeout for Mode Controller quorum loss | 120 seconds | YES |
| OQ-2 | Recovery window for two simultaneous CRITICAL watcher events | 300 seconds | YES |
| OQ-3 | Who exits safe-stop | Matt Nichol only | YES |
| OQ-4 | Does Homeostasis stay inside Mode Controller or become a separate contract? | Stays inside Mode Controller | YES |
| OQ-5 | Baseline ingestion operator approval threshold | Only above defined risk threshold — seven triggers | YES |

## Open Questions Still Pending

None.

---

## Next Authorized Tasks In Order

1. Run `python3 scripts/mmi_dispatch.py` to confirm current dispatch
2. **IMMEDIATE: Start retroactive adversarial stress test queue — Privacy Filter first**
3. Build Load Fission v2 — contract SIGNED
4. Build Specialisation Fission v2 — contract SIGNED
5. Continue gap contract cycle for remaining gaps (6, 7, 8, 9, 10)

---

## Repo Location

WSL: /home/socialarchitect/northstar
Branch: safety/queue-drift-cleanup-20260528
GitHub: https://github.com/Purple-Alpha/Mutant_Monkey_Intelligence-.git

---

## Social Architect Project

Completely separate project at C:\Architectapp_clean\intelligence\
Nothing to do with Mutant Monkey. Do not mix.

---

## How To Start The New Thread

Paste this into the new Claude thread to pick up exactly where we left off:

I am continuing the Mutant Monkey Inbox Shield build session.
The full project context is in the repo at /home/socialarchitect/northstar
Read MMI_THREAD_HANDOFF.md from the repo root and confirm current state before we proceed.
The Social Architect project at C:\Architectapp_clean is a completely separate project — do not mix it with Mutant Monkey under any circumstances.
