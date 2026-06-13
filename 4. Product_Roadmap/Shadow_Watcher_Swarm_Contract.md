# Shadow Watcher Swarm — Agent Design Contract

## Neutral defensive alarm-and-fission system

**Document type:** Agent Design Contract (master contract with layer-specific authorization gates)
**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Build authorization granted for all ten layers per §11 scope, within the synthetic/governed boundaries of this contract and excluding every separately gated capability in §2 and §10.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against `4. Product_Roadmap/Shadow_Watcher_Swarm_Concept_Doc.md` (CONCEPT, June 12 2026).
**Authority:** Matt Nichol — sole signing authority
**Dependencies:** Watcher Agents #85-87 GATED, MutationEngine #88 GATED, Blast Radius Controller #89 GATED, Load Fission #90 GATED, Specialisation Fission #91 GATED, Dual LLM pattern GATED.

---

## §0 — Hard Boundary

**The system's purpose is to preserve evidence and support authorized reporting workflows — not to damage reputation, punish actors, or conduct retaliation.**

This boundary is part of the contract. Any implementation that drifts toward reputation damage, punishment, retaliation, hacking back, private-person identification, doxxing, or autonomous external accusation fails the contract.

The Shadow Watcher Swarm is defensive, neutral, evidence-preserving, and advisory unless a later signed contract explicitly authorizes a narrower live integration.

---

## §1 — Purpose

The Shadow Watcher Swarm makes fraud attempts non-disposable. A suspicious attempt should produce durable evidence, repeat-pattern memory, adversarial tests, and hardening proposals so future attempts face stronger review and higher defensive friction.

It is a **second swarm alongside the first**, not a replacement. It extends the Evidence-to-Friction Loop while feeding the same ReconciliationAgent, MutationEngine, Blast Radius Controller, Watcher Agents, Fission controllers, and evidence infrastructure.

---

## §2 — What This Contract Does NOT Authorize

This contract does not authorize:

- Honeypots or fake vendor portals.
- Market intelligence or builder radar collection.
- Offensive retaliation.
- Autonomous abuse reports.
- Public accusation language.
- Reputation-damage workflows.
- Personal tracking or private-person identification.
- Active scanning or enrichment beyond passive public lookup.
- External interaction with suspected attacker infrastructure.
- Live mailbox, live payment-system, or customer-data external API integrations.

Those require separate concept docs, legal/consent review where applicable, and separate §11 signatures.

---

## §3 — Core Loop

Suspicious attempt detected → Shadow Watchers classify alarm → fission wave launches → child agents investigate → evidence chain locked → containment recommendation issued → hostile indicators stored in memory → repeat-pattern check performed → defensive friction score calculated → report-ready package prepared → adversarial test generated → hardening proposal created → future similar attempts face stronger review.

The loop is evidence-to-friction, not evidence-to-retaliation.

---

## §4 — Alarm Levels

| Level | Name | Fission wave | Output |
|---|---|---|---|
| 0 | Normal | No fission | Normal log only |
| 1 | Watch | 1-2 child agents | Quiet review note |
| 2 | Investigate | 3-5 child agents | Investigation record and evidence snapshot |
| 3 | High Risk | 6-10 child agents | Verification required, case timeline, friction recommendation |
| 4 | Incident | Full response wave | Incident evidence package, remediation checklist, adversarial test generation |

Alarm levels are not final fraud verdicts. They are operational triage states for right-sized investigation waves.

---

## §5 — Locked Decisions

| ID | Decision | Locked Value |
|---|---|---|
| SWS-D1 | Purpose boundary | Preserve evidence and support authorized reporting workflows; never punish, retaliate, or damage reputation. |
| SWS-D2 | Neutrality | Shadow Watchers observe and classify; they are not biased toward safe or attack. |
| SWS-D3 | No final fraud claim | No Shadow Watcher or child agent makes a final fraud determination. |
| SWS-D4 | No unilateral block | No Shadow Watcher or child agent blocks payment, mailbox action, or user action alone. |
| SWS-D5 | Q-class watchers | Shadow Watchers and child investigation agents are Q-class: no tools, no credentials, no action capability. |
| SWS-D6 | P-class recommendations | Reconciliation / recommendation agents are P-class and receive `EvidenceBundle` only; tools through BRC gateway only. |
| SWS-D7 | Fission trigger | Fission waves launch only when thresholded alarm levels are met and BRC/fission gates allow it. |
| SWS-D8 | Indicator memory | Indicator reuse is internal defensive memory, not personal tracking. |
| SWS-D9 | Reporting | ReportDraftAgent drafts only; operator approval required before any external submission. |
| SWS-D10 | Mutation path | Hardening proposals feed MutationEngine through governed amendment/sign-off path only. |
| SWS-D11 | Layer gating | Each layer requires its own §11 layer authorization before build. |
| SWS-D12 | Existing swarm preservation | The first swarm is not replaced or rewritten; this swarm sits alongside it. |

---

## §6 — Ten Layers and Build Authority

This master contract records the full architecture. **No layer is build-authorized unless its layer-specific §11 block is signed in §11.**

### Layer 1 — Watch Layer

**Agents:** SenderShadowWatcher, PaymentShadowWatcher, LanguageShadowWatcher, AttachmentShadowWatcher, GeoShadowWatcher, VendorHistoryShadowWatcher.

**Authority:** observe only; classify candidate facts for alarm input; explain evidence used; separate observed facts from inference.

**Forbidden:** tools, credentials, final fraud claims, blocking actions, recommendations beyond evidence explanation.

**Class:** Q-class.

### Layer 2 — Alarm Layer

**Agents:** AlarmClassifier, ConfidenceCalibrator, SeverityNormalizer, WaveSizeController.

**Authority:** convert watcher evidence into Level 0-4 alarm state; normalize severity; size fission wave.

**Forbidden:** final verdicts, direct containment, direct external reporting, identity/person tracking.

**Class:** deterministic or Q-class unless a later signed contract proves P-class need.

### Layer 3 — Agent Fission Layer

**Agents:** ChildAgentSpawner, TaskAllocator, BudgetGuard, DuplicateGuard, ScopeGuard.

**Authority:** spawn right-sized child-agent investigation waves under existing Load/Specialisation Fission gates; assign scopes; enforce budgets and duplicate suppression.

**Forbidden:** child privilege inheritance, fission depth > 1, ReconciliationAgent fission, unbounded wave growth, bypassing BRC.

**Class:** deterministic orchestrator / control-plane code.

### Layer 4 — Child Investigation Layer

**Agents:** SenderHistoryAgent, GeoVelocityAgent, PaymentChangeAgent, AttachmentFingerprintAgent, LanguageDriftAgent, VendorRelationshipAgent, VerificationAgent, FrictionAgent, CaseTimelineAgent, RetestAgent.

**Authority:** investigate scoped evidence questions, produce structured evidence, create investigation records, prepare retest facts.

**Forbidden:** tools, credentials, final fraud claims, external interaction, active scanning, sandbox execution of attachment content unless separately signed.

**Class:** Q-class.

### Layer 5 — Reconciliation Layer

**Agents:** EvidenceMerger, ConflictResolver, FinalRiskNarrative, VerificationRecommendation, FrictionRecommendation, HumanActionRecommendation.

**Authority:** merge child evidence, resolve conflicts, produce narrative and recommendations from `EvidenceBundle` only.

**Forbidden:** raw email access, unilateral block, autonomous external report, final confirmed-fraud language without policy + human review.

**Class:** P-class where tool access is required; BRC gateway only.

### Layer 6 — Containment Layer

**Agent:** ContainmentAgent.

**Authority:** recommend proportional defensive containment only.

**Allowed recommendations:** hold payment pending verification, require known-good callback, require second approval, isolate suspicious attachment, mark sender for enhanced review, flag vendor record for verification, create MSP review ticket, preserve original message and evidence.

**Forbidden:** autonomous blocking, payment blocking beyond advisory recommendation, mailbox changes without live-integration signature, policy bypass, retaliation.

**Class:** P-class recommendation agent; BRC gateway only for any tool path.

### Layer 7 — Attacker Cost Memory Layer

**Agents:** AttackerCostMemoryAgent, FrictionScoreAgent.

**Authority:** track indicator reuse and estimate defensive friction imposed on attack paths.

**Forbidden:** private-person identification, doxxing, public reputation scoring, client-facing "attacker cost" language in V1.

**Class:** internal evidence/memory agents; exact class depends on raw-data access in the layer-specific contract.

### Layer 8 — Evidence Chain Layer

**Agent:** EvidenceChainAgent.

**Authority:** maintain evidence-grade chain of custody: what was seen, when, which agent observed it, which tenant was affected, what was inferred vs observed, what human verified, what action was recommended, what action was taken, what test was created afterward.

**Forbidden:** modifying prior evidence, deleting evidence, cross-tenant reads, unverified final claims.

**Class:** deterministic evidence infrastructure / P-class narrative only if raw-free.

### Layer 9 — Hardening Layer

**Agents:** RepeatPatternAgent, HardeningProposalAgent.

**Authority:** recognize repeat infrastructure fingerprints and turn attack lessons into rule changes, baseline updates, tests, and threshold review proposals.

**Forbidden:** autonomous mutation deployment, bypassing 3-shot confirmation, bypassing HumanSignOffGate, using indicator memory as personal tracking.

**Class:** Q-class or deterministic for pattern recognition; proposals feed MutationEngine governed path only.

### Layer 10 — Report-Ready Layer

**Agent:** ReportDraftAgent.

**Authority:** draft structured evidence packages for legitimate abuse-reporting channels, MSP incident documentation, client review, and cyber-insurance claim support.

**Forbidden:** autonomous reporting, public accusation language, reputation-damage language, retaliation framing, confirmed-fraud claims without policy + human review, external submission without operator approval.

**Class:** P-class draft agent; raw-free `EvidenceBundle` only.

---

## §7 — Dual LLM Mapping

This swarm is governed by the signed Dual LLM pattern:

- Q-class: Shadow Watchers and child investigation agents that touch raw signals.
- P-class: Reconciliation and recommendation agents that receive `EvidenceBundle` only.
- Orchestrator: deterministic non-LLM code that routes raw signals to Q-class only and tool-capable requests from P-class only.

The two laws hold without exception:

1. The model that can execute actions never sees raw email text.
2. The model that sees raw email text never holds tools.

Any fission child touching raw email is forced Q-class at spawn time and cannot inherit Privileged status.

---

## §8 — Defensive Indicator Memory

Tracked indicators are defensive, internal, and tenant-governed:

- Domain reuse.
- Reply-to reuse.
- URL and redirect reuse.
- Invoice template reuse.
- Phone-number reuse.
- Payment-destination / bank-routing reuse.
- PDF fingerprint reuse.
- Language-pattern reuse.
- Urgency/secrecy-pressure reuse.
- Timing-pattern reuse.
- Vendor impersonation reuse.
- Executive impersonation reuse.
- IP/ASN metadata.
- Verification-failure history.
- Tenant exposure history.

Tracking never means doxxing, personal retaliation, unauthorized access, hacking back, stalking real people, scanning/attacking infrastructure, or identifying private individuals.

---

## §9 — Required Tests

Every authorized layer must ship three test classes:

1. **Expected pass:** normal layer behavior and correct outputs.
2. **Adversarial:** boundary violations, privilege attempts, alarm/fission overreach, raw-text leakage, cross-tenant misuse, and unauthorized external-action attempts.
3. **Known-gap xfail:** explicitly deferred live integrations or legal-dependent capabilities with completion path.

Master adversarial requirements:

- Watcher cannot block or decide fraud.
- Q-class agent cannot fire any tool.
- P-class agent cannot receive raw email text.
- Alarm level cannot be inflated by a single untrusted child output.
- Fission wave cannot exceed the Level 0-4 wave bounds.
- Child cannot inherit Privileged status.
- ReportDraftAgent cannot submit externally.
- ContainmentAgent cannot execute a block.
- Indicator memory cannot store personal-identification claims.
- HardeningProposalAgent cannot deploy a mutation without MutationEngine sign-off path.

---

## §10 — Dependencies

Satisfied dependencies:

- Watcher Agents contract signed and gated (#85-87).
- MutationEngine gated (#88).
- Blast Radius Controller gated (#89).
- Load Fission gated (#90).
- Specialisation Fission gated (#91).
- Dual LLM pattern gated (no new row, DL-D6).

Deferred dependencies / later contracts:

- Live mailbox integration.
- Live payment-system integration.
- External threat-intel API use with customer data.
- Abuse-report submission workflow.
- Honeypot / deception environment.
- Active scanning or enrichment.
- Attachment execution sandbox beyond existing signed boundaries.

---

## §11 — Layer Authorization and Operator Sign-Off

**Status:** SIGNED — all ten layer blocks signed Matt Nichol June 12th 2026.

Signing one layer authorizes only that layer and only within the limits of this contract. Signing all layers authorizes the full Shadow Watcher Swarm build within synthetic / governed boundaries, excluding every separately gated capability in §2 and §10.

### Layer 1 — Watch Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 2 — Alarm Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 3 — Agent Fission Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 4 — Child Investigation Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 5 — Reconciliation Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 6 — Containment Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 7 — Attacker Cost Memory Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 8 — Evidence Chain Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 9 — Hardening Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

### Layer 10 — Report-Ready Layer
**Status:** SIGNED  
**Signed:** Matt Nichol  
**Date:** June 12th 2026

---

## §12 — Closure Checklist

For each signed layer:

- [ ] Contract layer block signed.
- [ ] Implementation stays inside signed layer scope.
- [ ] Three test classes pass, with known-gap xfails documented.
- [ ] Dual LLM boundary tests pass where applicable.
- [ ] BRC gateway tests pass where any tool path exists.
- [ ] Fission bounds tested where wave spawning exists.
- [ ] Grok completion gate 0/0.
- [ ] Health score ELITE 85+ on the appropriate rubric track or a signed Shadow Watcher rubric amendment.
- [ ] Build Map updated.
- [ ] Decision log closure entry recorded.

---

## §13 — Next Action

Matt reviews and signs the layer blocks he wants authorized. After signature, Rule 1 applies only to the signed layers: Cursor builds those layers straight through, gates 0/0, updates trackers, commits, and holds before push.
