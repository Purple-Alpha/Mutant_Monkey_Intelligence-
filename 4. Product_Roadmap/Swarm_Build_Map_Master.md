# Mutant Monkey Inbox Shield — Swarm Build Map
**Status:** Advisory lane — requires §11 signature before build authorization
**Date:** June 9, 2026
**Authority:** Matt Nichol — sole signing authority
**Purpose:** Master build order document. Replaces "what do you want to build next" permanently.

---

## HOW TO READ THIS MAP

**STATUS CODES:**
- `GOVERNED` — Agent Design Contract signed, spec complete, ready for Cursor
- `GATED` — Built and tested, gate passed
- `UNBLOCKED` — No dependencies outstanding, ready to spec and sign
- `BLOCKED` — Cannot be built until dependency is complete
- `NEW` — Identified in June 9 session, needs Agent Design Contract

**RUBRIC SCORE:** Uses existing Strategic Direction Matrix (max 18, double-weighted Target Completeness)
- 14-18 — Build now
- 9-13 — Matt reviews
- 0-8 — Park

---

## LAYER 0 — THREAT INTELLIGENCE FOUNDATION
*The library. Agents brief Layer 1. No detection. No verdicts.*
*Dependency: Must exist before Layer 1 agents can operate at full capacity*

| Agent | Status | Score | Blocked By | Notes |
|---|---|---|---|---|
| PhishIntelAgent | NEW | TBD | Nothing | Highest priority — phishing is primary attack vector |
| RansomwareIntelAgent | NEW | TBD | Nothing | Ransomware delivery via email confirmed real threat |
| BECIntelAgent | NEW | TBD | Nothing | BEC/fraud is core product use case |
| TrojanDeliveryIntelAgent | NEW | TBD | Nothing | Trojan via email — confirmed real scenario today |
| GeoIntelAgent | NEW | TBD | Nothing | Feeds GeoVelocityAgent in Layer 1 |
| AIGenContentIntelAgent | NEW | TBD | Nothing | Newsletter/AI image false positive scenario |

**Layer 0 build order:** All six can be specced in parallel. No internal dependencies.
**Gate requirement:** All Layer 0 agents must have knowledge base seeded before Layer 1 agents are considered production-ready.

---

## LAYER 1 — DETECTION SWARM
*Active detection. Evidence contributions only. No verdicts. All write to shared evidence ledger.*
*Dependency: Shared Evidence Ledger must exist before any Layer 1 agent can operate*

| Agent | Status | Score | Blocked By | Notes |
|---|---|---|---|---|
| HeaderDivergenceAgent | GATED | 17/18 | Nothing | Already built and governed |
| EmailAuthenticationAgent | GATED | 17/18 | Nothing | Already built and governed |
| GhostThreadAgent | GATED | 17/18 | Nothing | Already built and governed |
| GeoVelocityAgent | NEW | TBD | GeoIntelAgent (L0) | Ukraine office scenario — confirmed real |
| ContentAnalyzer | NEW | TBD | PhishIntelAgent + BECIntelAgent (L0) | NLP urgency detection, BEC language patterns |
| URLReceptor | NEW | TBD | PhishIntelAgent (L0) | URL sandbox + redirect chain analysis |
| AttachmentSandbox | NEW | TBD | TrojanDeliveryIntelAgent + RansomwareIntelAgent (L0) | Detonation before delivery — zero-day primary defense |
| ImageClassifier | NEW | TBD | AIGenContentIntelAgent (L0) | Newsletter/AI image false positive scenario |
| SenderHistoryAgent | NEW | TBD | Nothing | Sender relationship mapping — geo context support |
| SharedEvidenceLedger | NEW | TBD | Nothing | **CRITICAL INFRASTRUCTURE** — all agents write here. Must be built first in Layer 1. |

**Layer 1 build order:**
1. SharedEvidenceLedger — everything else depends on this
2. SenderHistoryAgent — no dependencies, feeds geo and content agents
3. GeoVelocityAgent — needs GeoIntelAgent (L0) + SenderHistoryAgent
4. ContentAnalyzer — needs PhishIntelAgent + BECIntelAgent (L0)
5. URLReceptor — needs PhishIntelAgent (L0)
6. AttachmentSandbox — needs TrojanDeliveryIntelAgent + RansomwareIntelAgent (L0)
7. ImageClassifier — needs AIGenContentIntelAgent (L0)

---

## LAYER 2 — RECONCILIATION
*Single agent. Reads full evidence ledger. Produces verdict with full evidence chain attached.*
*Dependency: ALL Layer 1 agents must be operational before this agent is production-ready*

| Agent | Status | Score | Blocked By | Notes |
|---|---|---|---|---|
| ReconciliationAgent | NEW | TBD | All Layer 1 agents + SharedEvidenceLedger | Most critical new agent from today. Needs own Agent Design Contract. |

**What ReconciliationAgent does:**
- Reads all evidence contributions from SharedEvidenceLedger
- Weights conflicting signals
- Surfaces agent disagreement as information
- Produces human-readable evidence chain
- Issues the ONLY verdict in the entire swarm
- Attaches full evidence chain to every verdict — no black box

**Gate requirement:** ReconciliationAgent output must be readable by a non-technical MSP operator. Plain English. No jargon.

---

## LAYER 3 — THE LUNG (ELASTIC SCALING)
*Protection depth dial + elastic agent scaling under attack*
*Dependency: Layer 1 and Layer 2 must be operational. Cannot scale agents that don't exist.*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| LungController | NEW | Layer 1 + Layer 2 complete | Monitors volume and pattern spikes. Triggers inhale/exhale. |
| ScalingTriggerEngine | NEW | LungController | Defines inhale/exhale thresholds. Configurable per tenant. |
| ProtectionDepthDial | NEW | LungController | Light / Normal / Deep per tenant. MSP sets per client. |
| BaselineMonitor | NEW | ScalingTriggerEngine | Watches for attack vs normal volume. Prevents false positive spikes from scaling events. |

**The Lung breathing model:**
- **Light breath** — inform only. No quarantine. Flag for operator awareness.
- **Normal breath** — quarantine high confidence. Notify operator on borderline.
- **Deep breath** — hold everything suspicious. Require documented human override to release.
- **Inhale (attack mode)** — 70 agents → 700 → 7000. Triggered by volume + pattern spike.
- **Exhale (return to baseline)** — cooldown period confirmed before scaling down.

---

## LAYER 4 — COLLECTIVE IMMUNE SYSTEM
*Cross-tenant pattern sharing. One tenant attacked = every tenant vaccinated.*
*Dependency: Mutation Engine (Layer 5) must exist to validate patterns before sharing*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| PatternBroadcastEngine | NEW | MutationEngine (L5) | Shares abstract indicators only — never raw email content, never private tenant data |
| TenantVaccinationReceiver | NEW | PatternBroadcastEngine | Each tenant receives and applies shared patterns |
| PrivacyFilter | NEW | PatternBroadcastEngine | **CRITICAL** — strips all private data before broadcast. Only hashes, signatures, abstract patterns leave the tenant. |

**Privacy rule — non-negotiable:**
Only these can be shared across tenants: IP reputation hashes, domain signatures, attachment behaviour patterns, anomaly signatures, URL redirect chain hashes.
Never shared: email content, sender identity, recipient identity, company name, any PII.

---

## LAYER 5 — MUTATION AND EVOLUTION
*How the swarm learns. 3-shot confirmation. Human sign-off required. Full rollback capability.*
*Dependency: Layer 0 knowledge agents must exist to receive mutations*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| MutationEngine | NEW | Layer 0 agents operational | Core learning mechanism |
| 3ShotConfirmationTracker | NEW | MutationEngine | Tracks candidate patterns across independent detection events |
| ValidationGate | NEW | 3ShotConfirmationTracker | Automated testing against benign email stream before deployment |
| HumanSignOffGate | NEW | ValidationGate | **Matt holds authority here.** No mutation deploys without explicit approval. Maps to §11 signature process. |
| RollbackMechanism | NEW | HumanSignOffGate | Monitors false positive rate post-deployment. Auto-rollback if spike detected. |
| ZeroDayCapture | NEW | MutationEngine + AttachmentSandbox | Unknown pattern detected → logged as candidate → 3-shot tracker → mutation proposed |

**Mutation lifecycle:**
Unknown pattern detected → Shot 1 logged → Shot 2 logged → Shot 3 logged → Candidate generated → Automated validation → Human sign-off (Matt) → Deployed to all tenants → False positive monitoring → Stable or rollback

---

## LAYER 6 — GOVERNANCE AND AUDIT
*Every action logged. Every override documented. Every mutation audited. Drift detected.*
*Dependency: Must be built in parallel with everything else — not after*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| AppendOnlyEvidenceLedger | NEW | Nothing — build first | Central log. All agent outputs. Immutable. |
| OperatorOverrideLog | NEW | Playhouse | Every tech override logged with name, reason, timestamp |
| MutationAuditTrail | NEW | MutationEngine | Full history of every proposed and deployed mutation |
| TokenUsageTracker | NEW | Nothing — build early | Per-tenant, per-agent, per-model token tracking. MSP billing transparency. |
| DriftDetectionMonitor | NEW | All agents operational | Watches each agent's confidence distribution. Flags deviation from baseline. |
| RoleSeparationController | NEW | Nothing — build first | Builders ≠ Auditors at credential level. Not just schema — actual access control. |

---

## THE PLAYHOUSE — OPERATOR CONTROL SURFACE
*What the MSP and tech person see and use.*
*Dependency: Everything below must exist before Playhouse is meaningful*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| LungDial | NEW | LungController (L3) | Per-tenant protection depth. Light/Normal/Deep. |
| EvidenceChainViewer | NEW | ReconciliationAgent (L2) | Drill into any flagged email. See full agent evidence chain in plain English. |
| TechOverridePath | NEW | OperatorOverrideLog (L6) | Documented release or block. Name attached. Reason required. Logged. |
| CollectiveImmuneStatusPanel | NEW | PatternBroadcastEngine (L4) | Shows recent cross-tenant learning events |
| MutationLogViewer | NEW | MutationAuditTrail (L6) | What the swarm learned recently. Human readable. |
| CostAttributionDashboard | NEW | TokenUsageTracker (L6) | Per-tenant cost breakdown. Which agents ran. What it cost. |
| MultiTenantOverview | NEW | All layers operational | MSP view across all clients. Global threat trends. |

---

## MASTER BUILD ORDER
*Dependency-driven. Not opinion. This is the sequence.*

```
PHASE 1 — INFRASTRUCTURE (nothing works without these)
├── AppendOnlyEvidenceLedger
├── SharedEvidenceLedger  
├── RoleSeparationController
└── TokenUsageTracker

PHASE 2 — KNOWLEDGE FOUNDATION (Layer 0)
├── PhishIntelAgent
├── RansomwareIntelAgent
├── BECIntelAgent
├── TrojanDeliveryIntelAgent
├── GeoIntelAgent
└── AIGenContentIntelAgent

PHASE 3 — DETECTION SWARM (Layer 1)
├── SenderHistoryAgent (no L0 dependency)
├── GeoVelocityAgent (needs GeoIntelAgent)
├── ContentAnalyzer (needs PhishIntel + BECIntel)
├── URLReceptor (needs PhishIntelAgent)
├── AttachmentSandbox (needs Trojan + Ransomware Intel)
└── ImageClassifier (needs AIGenContentIntelAgent)

PHASE 4 — RECONCILIATION (Layer 2)
└── ReconciliationAgent (needs all Layer 1 complete)

PHASE 5 — MUTATION ENGINE (Layer 5)
├── MutationEngine
├── 3ShotConfirmationTracker
├── ValidationGate
├── HumanSignOffGate (Matt signs)
├── RollbackMechanism
└── ZeroDayCapture

PHASE 6 — COLLECTIVE IMMUNE SYSTEM (Layer 4)
├── PrivacyFilter (build first)
├── PatternBroadcastEngine
└── TenantVaccinationReceiver

PHASE 7 — THE LUNG (Layer 3)
├── BaselineMonitor
├── ScalingTriggerEngine
├── LungController
└── ProtectionDepthDial

PHASE 8 — GOVERNANCE COMPLETION (Layer 6)
├── OperatorOverrideLog
├── MutationAuditTrail
└── DriftDetectionMonitor

PHASE 9 — THE PLAYHOUSE
├── EvidenceChainViewer
├── TechOverridePath
├── LungDial
├── CollectiveImmuneStatusPanel
├── MutationLogViewer
├── CostAttributionDashboard
└── MultiTenantOverview
```

---

## WHAT IS ALREADY BUILT AND GOVERNED

| Agent | Layer | Status |
|---|---|---|
| HeaderDivergenceAgent | 1 | GATED |
| EmailAuthenticationAgent | 1 | GATED |
| GhostThreadAgent | 1 | GATED |
| Verification Outcome Agent | 2 | §11 SIGNED |

---

## GATE REQUIREMENTS BEFORE ANY PHASE IS CLOSED

- `complete_gate.py` must show 0/0
- All agents in phase must have passing tests across 3 classes: expected-pass, adversarial, known-gap xfail with written reason
- Matt signs phase closure — sole authority
- No push, no tracker edits without Matt's explicit go-ahead

---

## SIGNATURE BLOCK
This document requires §11 signature before any build authorization is granted against it.

**Signed:** ___________________________
**Date:** ___________________________
