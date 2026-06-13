# Dual LLM — Agent Design Contract

## Architectural law: the model that acts never reads, the model that reads never acts

**Document type:** Agent Design Contract (architectural pattern, swarm-wide)
**Status:** SIGNED — §11 signed Matt Nichol June 12th 2026. Build authorized. The signature certifies operator review of a Cursor-authored scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against the June 12 2026 contract session.
**Authority:** Matt Nichol — sole signing authority
**Depends on:** ReconciliationAgent (GATED #84, `1b2ac0c` / closed `1f3d661`) + Blast Radius Controller (GATED #89, `f1c817e`) + Phase 3 detection agents (GATED #78-83, `6deffd9` / closed `ce386f7`). Companion: Dual LLM rubric track amendment (`Agent_Health_Score_Rubric_Amendment_DualLLM.md`).

---

## §0 — Purpose

This contract governs the **Dual LLM pattern across the entire swarm**. It is the structural defense against prompt injection: the swarm processes hostile, attacker-controlled email text every day, and no amount of prompt hardening makes an LLM that *reads* attacker text safe to *also hold tools*. So the pattern removes the question entirely by splitting reading from acting.

It is an **architectural law applied to existing agents**, not a new agent — there is no new scoreboard row. The law constrains which agents may see raw email text, which may hold tools, and how data flows between them through a deterministic, non-LLM orchestrator.

---

## §1 — Core architectural law (two rules, no exceptions)

1. **Rule 1 — The model that can execute actions never sees raw email text.**
2. **Rule 2 — The model that sees raw email text never holds tools.**

These two rules admit **no exceptions** and no threshold. They hold on every email (§5 DL-D1), in every mode, for every agent including fission children (§4).

---

## §2 — Three roles

### §2.1 — Q-class (Quarantined) agents

- **Membership:** all current detection agents (#78-83), the AttachmentSandbox, and **any fission child that touches raw email** (forced Q-class at spawn, §4).
- **Capabilities:** **no tools, no credentials, no action capability.**
- **Trust posture:** **assumed compromised by design.** The system must remain safe even if a Q-class model is fully hijacked by injected instructions.
- **Output:** **strict typed JSON evidence only** — no free-form prose that anything downstream will interpret as instructions.

### §2.2 — P-class (Privileged) agents

- **Membership:** **ReconciliationAgent only** (#84).
- **Input:** **never sees raw email text** — only the structured EvidenceBundle (§3 step 6).
- **Tools:** reached **only via the Blast Radius Controller gateway** (#89), never directly.
- **Output:** proposes actions **as evidence, not as verdicts** — the final disposition is computed by the reconciliation layer, not decided by any LLM (§3 step 8).

### §2.3 — Orchestrator

- **Identity:** the **Blast Radius Controller gateway** — **deterministic, non-LLM code.**
- **Routing:** routes **raw email to Q-class only**; routes **tools from P-class only**.
- **Hard guarantee:** **never passes raw email text to P-class under any condition.**
- It is the only component trusted to move data across the Q→P boundary, precisely because it contains no model that can be talked into breaking the rules.

---

## §3 — Pipeline sequence (locked)

1. **Raw email arrives.**
2. **Attachments → AttachmentSandbox** (existing — code/behavior isolation).
3. **Email text → Q-class agents** (quarantined, no tools).
4. **Schema and policy validation by the orchestrator** — non-conforming Q-output is rejected, never forwarded.
5. **EvidenceBundle assembled** — **no raw email text**; structured fields and hashes only.
6. **ReconciliationAgent (P-class) receives the EvidenceBundle only.**
7. **Tool execution via the Blast Radius Controller gateway.**
8. **Reconciliation layer computes final disposition** — **never decided by any LLM** (2-of-3 voters, §6 Class 2).

No step may be skipped or reordered. The boundary between step 5 and step 6 is the load-bearing one: nothing carrying raw email text crosses it.

---

## §4 — Fission rules

- **Any fission child touching raw email is forced Q-class at spawn time by the orchestrator.**
- **No child inherits Privileged status.**
- **Privilege escalation via fission is explicitly prohibited.**

This closes the obvious attack on the pattern: you cannot fission your way from a reader into an actor. It binds directly to the Load and Specialisation Fission contracts (children are born inside the gateway; the orchestrator assigns Q-class to any child that sees raw email).

---

## §5 — Locked design decisions (confirm at signing)

| # | Decision | Locked value |
|---|---|---|
| DL-D1 | Always-on | Dual LLM activates on **every email** — not just above a threat threshold. |
| DL-D2 | Q-LLM assumed compromised | The Q-LLM is **assumed compromised by design**; the system must be safe even if the Q-LLM is fully hijacked. Safety is structural, not behavioral. |
| DL-D3 | Sentinel string test mandatory | A **sentinel string test** is mandatory — confirms raw email text never reaches P-class. |
| DL-D4 | Canary tool test mandatory | A **canary tool test** is mandatory — confirms Q-class cannot fire any tool. |
| DL-D5 | Compliance reference | **OWASP LLM Top 10 prompt injection defense** is the named compliance reference. |
| DL-D6 | No new scoreboard row | The Dual LLM pattern is applied **across existing agents**; it is not a new agent and takes **no new scoreboard row**. |
| DL-D7 | Disposition is non-LLM | Final disposition is computed by the **reconciliation layer (2-of-3 voters)**, never decided by any single LLM. |

---

## §6 — Test requirements

Three test classes per AGENTS.md §5.

**Class 1 — Expected pass**
- The pipeline sequence (§3) completes correctly, in order.
- The EvidenceBundle contains **no raw email text** — structured fields and hashes only.
- P-class **never receives raw email** — only the EvidenceBundle.

**Class 2 — Adversarial (five named tests)**
1. **Sentinel string test** — inject a marker into raw email; confirm it never appears in any P-class prompt (DL-D3).
2. **Canary tool test** — Q-class attempts a tool call; the canary must not fire (DL-D4).
3. **garak / Augustus injection corpus** — 210+ known injection probes against Q-class; the boundary holds.
4. **Tool syntax injection** — Q-class outputs tool-call syntax; the orchestrator must **not** execute it (treats it as data).
5. **Schema-valid corruption** — adversarial but schema-valid Q-class output **cannot flip the ReconciliationAgent verdict unilaterally** (2-of-3 voters required, DL-D7).

**Class 3 — Known-gap xfail**
- Full garak corpus automation — deferred until the CI pipeline is established. Completion path: CI pipeline stood up.
- Cross-tenant injection testing — deferred to the Phase 6 contract. Completion path: Phase 6 cross-tenant test surface.

ELITE 85+ on the Dual LLM rubric track required for closure.

---

## §7 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Raw email text reaches P-class | Class 2 (sentinel) | Immediate fail — Rule 1 violated |
| Q-class fires a tool | Class 2 (canary) | Immediate fail — Rule 2 violated |
| Orchestrator executes Q-LLM free text | Class 2 (tool syntax) | Immediate fail — orchestrator must treat Q-output as data |
| Unvalidated Q-output reaches the EvidenceBundle | Class 1/2 | Immediate fail — step 4 validation bypassed |
| Schema-valid adversarial output flips the verdict alone | Class 2 | Immediate fail — DL-D7 violated (2-of-3 required) |
| Fission child touching raw email gains Privileged status | Class 2 | Immediate fail — §4 / privilege escalation prohibited |
| Health score below 85 | Rubric | Phase does not close |

---

## §8 — Relationship to signed surfaces

| Signed surface | Relationship |
|---|---|
| Blast Radius Controller (`f1c817e`, #89) | **Is the orchestrator.** Routes raw email to Q-class, tools from P-class; never passes raw email to P-class. Tool execution flows through its gateway. No BRC surface modified — this contract constrains how agents use it. |
| ReconciliationAgent (`1b2ac0c`, #84) | **Is the only P-class agent.** Receives the EvidenceBundle only, never raw email; 2-of-3 voters compute disposition (DL-D7). Verdict surface unchanged. |
| Phase 3 detection agents (`6deffd9`, #78-83) + AttachmentSandbox | **Q-class.** No tools, no credentials; strict typed JSON evidence only. |
| Load / Specialisation Fission (#90 / #91) | Any fission child touching raw email is forced Q-class at spawn; no privilege escalation via fission (§4). |

No signed surface is modified by this contract; it adds an architectural constraint across them.

---

## §9 — Scoreboard

**No new row** (DL-D6). The Dual LLM pattern is applied across existing agents (#78-83 Q-class, #84 P-class, #89 orchestrator). Scored on the Dual LLM rubric track (`Agent_Health_Score_Rubric_Amendment_DualLLM.md`).

---

## §10 — Pre-conditions and closure checklist

**Pre-conditions:** ReconciliationAgent GATED ✓ (#84), Blast Radius Controller GATED ✓ (#89), Phase 3 detection agents GATED ✓ (#78-83). This contract §11-signed.

**Closure checklist:**
- [ ] Gate-clean 0/0 (Grok completion gate clean, 0 warnings)
- [ ] Health score 85+ ELITE on the Dual LLM rubric track
- [ ] Matt signs phase closure
- [ ] `decision_cycles_log.md` PHASE_CLOSURE entry recorded
- [ ] Three test classes pass (Class 1 + Class 2's five named tests; Class 3 documented xfail), including the mandatory sentinel and canary tests

---

## §11 — Operator Sign-Off

**Status:** SIGNED. Operator review complete; build authorized.

**Signed:** Matt Nichol
**Date:** June 12th 2026
