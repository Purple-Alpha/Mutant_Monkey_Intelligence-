# Shadow Watcher Swarm — Concept Doc

**Status:** CONCEPT — advisory lane only. No build authorization. A signed §11 contract is required before any build, and each layer needs its own signed contract.
**Date:** June 12 2026
**Authority:** Matt Nichol — sole signing authority
**Lane:** Advisory / concept. This document describes and proposes; it authorizes nothing.

---

## §0 — Hard boundary (read this first)

**The system's purpose is to preserve evidence and support authorized reporting workflows — not to damage reputation, punish actors, or conduct retaliation.**

This is the governing constraint on every layer below. Any feature, agent, or recommendation that drifts toward reputation damage, punishment, retaliation, or identification of private individuals is out of scope for this swarm and is rejected at design time, not patched later.

---

## §1 — Mission

The Shadow Watcher Swarm makes fraud attempts **non-disposable**. Every hostile attempt creates durable evidence, improves future detection, raises future friction, and reduces the attacker's ability to reuse the same infrastructure, language, payment path, or deception pattern.

It is a **neutral defensive alarm-and-fission system**. It observes suspicious events, assigns alarm levels, launches right-sized child-agent investigation waves, preserves evidence, supports verification, and turns confirmed patterns into adversarial tests that harden the product.

---

## §2 — What it is NOT

- Not a honeypot.
- Not a fake vendor portal system.
- Not a market intelligence radar.
- Not an offensive retaliation system.
- Not a final fraud judge.
- Not a personal tracking system.

Those are separate concepts with separate legal requirements and separate documents (see §12). They must not be merged into this swarm.

---

## §3 — Core principle: the Evidence-to-Friction Loop

Every fraud attempt becomes evidence. Every evidence record becomes a test. Every test becomes a hardening step. Every hardening step increases attacker cost. The attacker must rebuild, change approach, or burn more infrastructure.

**Core loop:**

Suspicious attempt detected → Shadow Watchers classify alarm → fission wave launches → child agents investigate → evidence chain locked → containment recommendation issued → hostile indicators stored in memory → repeat-pattern check performed → defensive friction score calculated → report-ready package prepared → adversarial test generated → hardening proposal created → future similar attempts face stronger review.

---

## §4 — Five alarm levels (plain names)

| Level | Name | Fission wave | Output |
|---|---|---|---|
| 0 | Normal | No fission | Normal log only |
| 1 | Watch | 1-2 child agents | Quiet review note |
| 2 | Investigate | 3-5 child agents | Investigation record + evidence snapshot |
| 3 | High Risk | 6-10 child agents | Verification required, case timeline, friction recommendation |
| 4 | Incident | Full response wave | Incident evidence package, remediation checklist, adversarial test generation |

---

## §5 — Shadow Watcher rules

- Observe only.
- Classify alarm level.
- Explain the evidence used.
- Separate fact from inference.
- Avoid making final fraud claims.
- Never block actions alone.
- Trigger fission only when thresholds are met.
- Neutral — not biased toward "safe" or "attack."
- **Shadow Watchers are Q-class** — no tools, no credentials, no action capability.

---

## §6 — Ten-layer structure

### Layer 1 — Watch Layer
SenderShadowWatcher, PaymentShadowWatcher, LanguageShadowWatcher, AttachmentShadowWatcher, GeoShadowWatcher, VendorHistoryShadowWatcher.

### Layer 2 — Alarm Layer
AlarmClassifier, ConfidenceCalibrator, SeverityNormalizer, WaveSizeController.

### Layer 3 — Agent Fission Layer
ChildAgentSpawner, TaskAllocator, BudgetGuard, DuplicateGuard, ScopeGuard.

### Layer 4 — Child Investigation Layer
SenderHistoryAgent, GeoVelocityAgent, PaymentChangeAgent, AttachmentFingerprintAgent, LanguageDriftAgent, VendorRelationshipAgent, VerificationAgent, FrictionAgent, CaseTimelineAgent, RetestAgent.

### Layer 5 — Reconciliation Layer
EvidenceMerger, ConflictResolver, FinalRiskNarrative, VerificationRecommendation, FrictionRecommendation, HumanActionRecommendation.

### Layer 6 — Containment Layer
**ContainmentAgent** — recommends proportional defensive containment only. Allowed recommendations: hold payment pending verification, require known-good callback, require second approval, isolate suspicious attachment, mark sender for enhanced review, flag vendor record for verification, create MSP review ticket, preserve original message and evidence. **Recommends only — policy and human layer decides. V1 advisory only.**

### Layer 7 — Attacker Cost Memory Layer
- **AttackerCostMemoryAgent** — tracks indicator reuse across events. Internal reputation memory, not personal tracking.
- **FrictionScoreAgent** — scores how much defensive cost was imposed on the attack path. Internal only at V1. The client-facing version uses "defensive friction" language, never "attacker cost."

### Layer 8 — Evidence Chain Layer
**EvidenceChainAgent** — maintains an evidence-grade chain of custody. Records: what was seen, when, which agent observed it, which tenant was affected, what was inferred versus observed, what a human verified, what action was recommended, what action was taken, and what test was created afterward.

### Layer 9 — Hardening Layer
- **RepeatPatternAgent** — recognizes when a new event shares infrastructure fingerprints with prior suspicious events. Pattern tracking, not personal tracking.
- **HardeningProposalAgent** — turns attack lessons into product-improvement proposals (rule changes, baseline updates, new tests, threshold reviews). Feeds the MutationEngine through the governed amendment path only.

### Layer 10 — Report-Ready Layer
**ReportDraftAgent** — prepares structured evidence packages for legitimate abuse-reporting channels, MSP incident documentation, client review, and cyber-insurance claim support. **Draft only. Operator approval required before any external submission. No autonomous reporting. No public-accusation language. No reputation-damage language. No retaliation framing. No claim that fraud is confirmed unless confirmed by policy and human review.**

---

## §7 — Defensive indicator tracking

**What is tracked (internal indicator memory):** domain reuse, reply-to reuse, URL and redirect reuse, invoice template reuse, phone-number reuse, payment-destination / bank-routing reuse, PDF fingerprint reuse, language-pattern reuse, urgency/secrecy-pressure reuse, timing-pattern reuse, vendor impersonation reuse, executive impersonation reuse, IP/ASN metadata, verification-failure history, tenant exposure history.

**What tracking never means:** no doxxing, no personal retaliation, no unauthorized access, no hacking back, no stalking real people, no scanning or attacking infrastructure, no identifying private individuals. This is internal indicator memory — not personal tracking, not individual identification.

---

## §8 — Dual LLM mapping

- **Shadow Watchers (Layer 1) and child investigation agents (Layer 4) are Q-class** — they observe raw signals and produce structured evidence only; no tools, no credentials, no action capability.
- **Reconciliation and recommendation agents (Layers 5, 6, 10) are P-class** — they receive the `EvidenceBundle` only, never raw email text, and reach tools only through the Blast Radius Controller gateway.
- **The orchestrator is deterministic non-LLM code** — it routes raw signals to Q-class only and tools from P-class only, and never passes raw email text to P-class.

This swarm is built **under the signed Dual LLM contract** (`Dual_LLM_Contract.md`); it inherits the two laws (the model that acts never reads; the model that reads never acts) and the fission rule that any child touching raw email is forced Q-class with no privileged inheritance.

---

## §9 — Relationship to the existing swarm

A **second swarm alongside the first — not a replacement.** It feeds into the same ReconciliationAgent (#84), MutationEngine (#88), Blast Radius Controller (#89), Watcher Agents (#85-87), Load/Specialisation Fission (#90/#91), and the Phase 1 evidence infrastructure. **Nothing in the first swarm changes.** The Shadow Watcher Swarm sits alongside it and extends the Evidence-to-Friction Loop.

---

## §10 — §11 required before build (explicit list)

A signed §11 contract is required before any build, and each of the following capabilities is a hard signature gate — none may be built or enabled without an explicit signed authorization:

- Any external interaction with suspected attacker infrastructure.
- Any active scanning or enrichment beyond passive public lookup.
- Any honeypot or deception environment.
- Any autonomous abuse-report submission.
- Any sandbox execution of attachments.
- Any feature that attempts to identify private individuals.
- Any customer-facing confirmed-incident language without human approval.
- Any payment blocking beyond advisory recommendation.
- Any integration touching live mailboxes or payment systems.
- Any external threat-intel API that stores or transmits customer data.

---

## §11 — Dependencies

- Watcher Agents contract signed and gated (#85-87 GATED).
- Load Fission and Specialisation Fission contracts signed (#90 / #91 GATED).
- Blast Radius Controller gated (#89 GATED).
- MutationEngine gated (#88 GATED).
- Dual LLM pattern gated (built 2026-06-12, no new row, DL-D6).

All current dependencies are satisfied; the gate to build is operator authorization plus per-layer signed contracts, not a missing surface.

---

## §12 — Three separate concept docs — do not merge

1. **Shadow Watcher Swarm** — this document.
2. **Builder Radar / Market Intelligence** — separate, parked.
3. **Honeypot / Deception Environment** — separate; requires a legal and consent framework first.

---

## §13 — Next action

When Matt authorizes: **draft the Shadow Watcher Swarm contract.** Each layer needs its own signed contract before build. Matt is in the loop from the start. No build until signed.
