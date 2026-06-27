# Trap-Bot / Hack-Bot / Rot-Bot

**Status:** `RESEARCH_DESIGN` | **Component:** Swarm Command Reality Controller  
**Objective:** Active resource degradation and counter-offensive friction.

> **Authority:** Research doctrine only. **Highest liability** in this stack. Not build
> authorization. Requires separate legal/safety contract before any lab work. See `README.md`.

---

## 1. Mission Statement

This module manages the swarm's "Active Engagement" agents. It is the tactical layer
that transforms passive deception into an aggressive "rot" cycle. Its mandate is to
actively infiltrate, confuse, and degrade the attacker's own automated tools and
infrastructure from within the decoy environment — **lab blast-chamber only**.

---

## 2. Operational Tactics

- **Trap-Bot (The Lure):** Maintains highly "tempting" but volatile decoy assets
  (e.g., mock databases with fake "Admin" credentials that trigger identity-poisoning
  sequences on use).
- **Hack-Bot (The Mirror):** Upon detecting an exploit attempt, autonomously generates
  a "mirror" of the attacker's payload — only where legally permitted within the
  honeypot lab, never against real third-party infrastructure.
- **Rot-Bot (The Degradation):** Targets attacker data integrity and tool-chain
  performance via corrupted headers, malformed database responses, and "poisoned"
  credentials that cause automation to error or loop.

---

## 3. Intelligence Outputs (The Data Stream)

- **Attacker's Tool-Chain Resilience:** How many Rot-Bot injections before failure.
- **Exploit-Mirror Feedback:** How attacker infrastructure reacts to mirrored payloads (lab only).
- **Confidence Scores:** Effectiveness of current "Rot" strategy against specific threat actors.

---

## 4. Stealth and Integrity Protocols

- **Controlled Exposure:** All Hack-Bot actions in an isolated "Blast Chamber."
- **Grey-Zone Protocol:** Operates strictly within pre-defined legal bounds; every action logged with a Justification-Trace.
- **Sanitized Return-Fire:** Mirrored exploits are sanitized — diagnostic only, no real system damage.

---

## 5. Integration Architecture

- **Input:** Real-time data from `tarpit-orchestrator` and `network-mutator`.
- **Process:** MMI project brain determines which Bot Profile (Trap, Hack, or Rot) best
  suits the current attacker — **recommendation only**; operator authorizes any enactment.
- **Output:** Records "Time-to-Failure" of attacker tools for after-action reports.

---

## Parked status

Listed under **Parked / High-Liability Ideas** in `purple_translation_layer.md`.
Do not conflate with BREADTH agent builds or #19 / VPV verification lane.

---

## Escalation from Geo-Fence Manager

When `geo_fence_manager.md` emits **Reality Mismatch** or **Entrapment Score ≥71**, the MMI
project brain may recommend a **Hack-Bot (The Mirror)** profile — mirroring attacker tooling
within the blast chamber only.

**Signal path:**

```
geo-fence-manager → Reality Mismatch / Entrapment Score
    → project brain: bot profile recommendation
    → operator authorization (AUTH-5 equivalent for Reality Controller)
    → Hack-Bot MAY engage (lab blast chamber only)
```

Geo-fence **senses**; Hack-Bot **strikes**. No autonomous enactment. No action against real
third-party infrastructure.

**Related:** `geo_fence_manager.md` §5–§6.3, `reality_controller/README.md` hard boundaries.
