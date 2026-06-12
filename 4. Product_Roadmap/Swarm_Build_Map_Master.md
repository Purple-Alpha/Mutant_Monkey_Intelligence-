# Mutant Monkey Inbox Shield — Swarm Build Map
**Status:** Advisory lane — requires §11 signature before build authorization
**Date:** June 9, 2026 (updated — dual dial + Agent Fission added)
**Authority:** Matt Nichol — sole signing authority
**Purpose:** Master build order document. Replaces "what do you want to build next" permanently.
**Companion doc:** `4. Product_Roadmap/The_Lung_Concept_Spec.md`

---

## HOW TO READ THIS MAP

**STATUS CODES:**
- `GOVERNED` — Agent Design Contract signed, spec complete, ready for Cursor
- `GATED` — Built and tested, gate passed
- `UNBLOCKED` — No dependencies outstanding, ready to spec and sign
- `BLOCKED` — Cannot be built until dependency is complete
- `NEW` — Identified in June 9 session, needs Agent Design Contract
- `CONCEPT` — Validated concept, not yet ready to spec — calibration data needed first

**RUBRIC SCORE:** Uses existing Strategic Direction Matrix (max 18, double-weighted Target Completeness)
- 14-18 — Build now
- 9-13 — Matt reviews
- 0-8 — Park

---

## PHASE PROGRESS TRACKER

| Phase | Status | Gate | Notes |
|---|---|---|---|
| Phase 1 — Infrastructure | §11 SIGNED `fe355da` | GATED | Contract signed June 9 2026; infra built C1/C2/C3; closure entry June 11 2026 |
| Phase 2 — Knowledge Foundation | GATED `43b5511` | 0/0 clean | Six Layer 0 intel agents; phase closed 2026-06-10 (`f5bf3b7`) |
| Phase 3 — Detection Swarm | GATED `c522292` | 0/0 clean | Six Layer 1 detection agents built `6deffd9`; phase closed 2026-06-11 (`ce386f7`); 86 ELITE each |
| Phase 4 — Reconciliation | GATED | — | ReconciliationAgent (#84) built; three-voter ensemble; 88 ELITE; CIRT amendment + verdict surface landed |
| Phase 5 — Mutation Engine | GATED | — | MutationEngine ensemble (#88) built 2026-06-12; six components + named Anomaly Detection Pipeline; 95 ELITE; sandbox-only until operator sign-off; every deploy reversible |
| Phase 6 — Control Plane (Blast Radius Controller) | GATED | — | Blast Radius Controller (#89) built 2026-06-12; eight components walk the §3.6 gateway lifecycle; five gates (breakers / segmentation / rings / graceful degradation iface / zero trust); all five metastasis tests pass; 95 ELITE on Layer 6 Control Plane rubric; Mode Controller + Privacy Filter remain separate signed contracts |
| Phase 7 — The Lung | BLOCKED | — | Needs real tenant data to calibrate; needs own signed contract |
| Phase 8 — Governance Completion | BLOCKED | — | Needs Phase 5 complete; needs own signed contract |
| Phase 9 — The Playhouse | BLOCKED | — | Needs all phases complete; needs own signed contract |

---

## LAYER 0 — THREAT INTELLIGENCE FOUNDATION
*The library. Agents brief Layer 1. No detection. No verdicts.*
*Dependency: Must exist before Layer 1 agents can operate at full capacity*

| Agent | Status | Score | Blocked By | Notes |
|---|---|---|---|---|
| PhishIntelAgent | NEW | TBD | Phase 1 gated | Highest priority — phishing is primary attack vector |
| RansomwareIntelAgent | NEW | TBD | Phase 1 gated | Ransomware delivery via email confirmed real threat |
| BECIntelAgent | NEW | TBD | Phase 1 gated | BEC/fraud is core product use case |
| TrojanDeliveryIntelAgent | NEW | TBD | Phase 1 gated | Trojan via email — confirmed real scenario |
| GeoIntelAgent | NEW | TBD | Phase 1 gated | Feeds GeoVelocityAgent in Layer 1 |
| AIGenContentIntelAgent | NEW | TBD | Phase 1 gated | Newsletter/AI image false positive scenario |

---

## LAYER 1 — DETECTION SWARM
*Active detection. Evidence contributions only. No verdicts. All write to shared evidence ledger.*
*Dependency: Phase 1 infrastructure gated + Layer 0 agents operational*

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
| SenderHistoryAgent | NEW | TBD | Phase 1 gated | Sender relationship mapping — geo context support |

---

## LAYER 2 — RECONCILIATION
*Single agent. Reads full evidence ledger. Produces verdict with full evidence chain attached.*
*Dependency: ALL Layer 1 agents must be operational*

| Agent | Status | Blocked By | Notes |
|---|---|---|---|
| ReconciliationAgent | NEW | All Layer 1 + SharedEvidenceLedger | Only agent that produces a verdict. Needs own contract. |

---

## LAYER 3 — THE LUNG (ELASTIC SCALING + DUAL DIAL)
*Two dials. Elastic scaling. Agent Fission.*
*Dependency: Phases 1-4 complete + real tenant baseline data*

### Dial 1 — Protection Depth (per tenant)

| Setting | Behaviour | Canonical use case |
|---|---|---|
| Light | Inform only. No quarantine. | Defender is down. $50k deal. Tech turns dial, evidence chain confirms sender, email releases. |
| Normal | Quarantine high confidence. Notify on borderline. | Default for most MSP clients. |
| Deep | Hold everything. Require documented override to release. | Law firm. Wire transfer environment. Financial institution. |

### Dial 2 — Threat Focus (per tenant, set at onboarding)

| Focus | Primary agents prioritised | Typical client |
|---|---|---|
| Spam / Bulk | ImageClassifier, ContentAnalyzer, AIGenContentIntelAgent | Marketing agency, newsletter sender |
| Phishing | PhishIntelAgent, URLReceptor, CredentialPhishingAgent | Any SMB — baseline |
| BEC / Fraud | BECIntelAgent, SenderHistoryAgent, GeoVelocityAgent | Professional services, accountant, law firm |
| Ransomware | RansomwareIntelAgent, AttachmentSandbox, TrojanDeliveryIntelAgent | Healthcare, municipal, critical infrastructure |
| Full spectrum | All agents active | Enterprise, high-value target, post-incident client |

### Elastic Scaling Components

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| LungController | CONCEPT | Phases 1-4 + real tenant data | Monitors volume + pattern spikes. Triggers inhale/exhale. |
| ScalingTriggerEngine | CONCEPT | LungController + calibration data | Inhale/exhale thresholds. Cannot be set without real baseline. |
| ProtectionDepthDial | CONCEPT | LungController | Dial 1 — Light/Normal/Deep per tenant |
| ThreatFocusDial | CONCEPT | LungController | Dial 2 — Spam/Phishing/BEC/Ransomware/Full per tenant. NEW — added June 9. |
| BaselineMonitor | CONCEPT | ScalingTriggerEngine | Watches for attack vs normal. Prevents false positives from scaling events. |

### Agent Fission — The True Mutation

**What it is:** One agent divides into two more specialised agents when load or complexity demands it. Not just scaling — differentiating. One PhishIntelAgent becomes PhishIntelAgent-Credential and PhishIntelAgent-Social. Each child is more specialised than the parent.

**Why it matters:** This is biological mutation applied to the swarm. The swarm doesn't just get bigger under pressure — it gets smarter. More specialised. More accurate.

**Status:** CONCEPT — requires its own contract. Phase 5+ territory.

**Governance rules locked for when this is built:**
- Fission requires a signed trigger threshold before it can fire
- Child agents inherit parent's evidence schema — no new output types without signed amendment
- Every fission event logged to governance audit trail with timestamp and reason
- Child agents get their own scoreboard rows after fission
- Matt signs any fission that creates a net-new agent type

**Calibration blockers (honest — these stop the Lung contract, not Phase 1-4):**
- Inhale/exhale threshold numbers require real tenant baseline traffic data
- Fission trigger threshold requires real detection load data
- Infrastructure cost model at scale requires validation before contract is signed

---

## LAYER 4 — COLLECTIVE IMMUNE SYSTEM
*DEPTH GATE CLOSED — not buildable until gate opens*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| PrivacyFilter | CONCEPT | DEPTH GATE CLOSED | Build first when gate opens |
| PatternBroadcastEngine | CONCEPT | DEPTH GATE CLOSED + PrivacyFilter | Abstract indicators only — no PII, no raw content |
| TenantVaccinationReceiver | CONCEPT | DEPTH GATE CLOSED | Receives and applies shared patterns |

---

## LAYER 5 — MUTATION AND EVOLUTION
*3-shot confirmation. Human sign-off. Full rollback.*
*Dependency: Layer 0 knowledge agents operational*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| MutationEngine | NEW | Phase 2 complete | `core/mutation/engine.py` exists sandbox-only — extend, don't rebuild |
| 3ShotConfirmationTracker | NEW | MutationEngine | Pattern confirmed 3x independently before candidacy |
| ValidationGate | NEW | 3ShotConfirmationTracker | Automated test against benign stream before deployment |
| HumanSignOffGate | NEW | ValidationGate | Matt signs every mutation deployment |
| RollbackMechanism | NEW | HumanSignOffGate | Auto-rollback if false positive spike post-deployment |
| ZeroDayCapture | NEW | MutationEngine + AttachmentSandbox | Unknown behaviour → candidate → 3-shot → proposed |
| AgentFissionController | CONCEPT | MutationEngine + Lung contract signed | Governs agent division events — separate from pattern mutation |

---

## LAYER 6 — GOVERNANCE AND AUDIT
*Built in parallel with everything else — not after*

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| AppendOnlyEvidenceLedger (`core/blackboard/`) | §11 SIGNED | Phase 1 gate | Formalised in Phase 1 contract |
| RoleSeparationController | §11 SIGNED | Phase 1 gate | Formalised in Phase 1 contract |
| TokenUsageTracker (#71) | §11 SIGNED | Phase 1 gate | Net-new — Phase 1 contract |
| OperatorOverrideLog | NEW | Playhouse | Every tech override — name, reason, timestamp |
| MutationAuditTrail | NEW | MutationEngine | Full history every proposed and deployed mutation |
| DriftDetectionMonitor | NEW | All agents operational | Agent confidence distribution monitoring |

---

## THE PLAYHOUSE — OPERATOR CONTROL SURFACE

| Component | Status | Blocked By | Notes |
|---|---|---|---|
| ProtectionDepthDial UI | NEW | LungController | Dial 1 — per tenant |
| ThreatFocusDial UI | NEW | LungController | Dial 2 — per tenant, set at onboarding |
| EvidenceChainViewer | NEW | ReconciliationAgent | Plain English evidence chain per flagged email |
| TechOverridePath | NEW | OperatorOverrideLog | Documented release or block with name attached |
| CollectiveImmuneStatusPanel | NEW | PatternBroadcastEngine | DEPTH GATE dependency |
| MutationLogViewer | NEW | MutationAuditTrail | What the swarm learned recently |
| AgentFissionLog | NEW | AgentFissionController | What agents have divided and why |
| CostAttributionDashboard | NEW | TokenUsageTracker | Per-tenant cost breakdown |
| MultiTenantOverview | NEW | All layers | MSP view across all clients |

---

## MASTER BUILD ORDER

```
PHASE 1 — INFRASTRUCTURE ✅ §11 SIGNED fe355da
├── AppendOnlyEvidenceLedger (core/blackboard/)
├── SharedEvidenceLedger
├── RoleSeparationController
└── TokenUsageTracker (#71)

PHASE 2 — KNOWLEDGE FOUNDATION
├── PhishIntelAgent
├── RansomwareIntelAgent
├── BECIntelAgent
├── TrojanDeliveryIntelAgent
├── GeoIntelAgent
└── AIGenContentIntelAgent

PHASE 3 — DETECTION SWARM
├── SenderHistoryAgent
├── GeoVelocityAgent
├── ContentAnalyzer
├── URLReceptor
├── AttachmentSandbox
└── ImageClassifier

PHASE 4 — RECONCILIATION
└── ReconciliationAgent

PHASE 5 — MUTATION ENGINE
├── MutationEngine (extend core/mutation/engine.py)
├── 3ShotConfirmationTracker
├── ValidationGate
├── HumanSignOffGate
├── RollbackMechanism
├── ZeroDayCapture
└── AgentFissionController (CONCEPT — own contract)

PHASE 6 — COLLECTIVE IMMUNE SYSTEM
— DEPTH GATE CLOSED —

PHASE 7 — THE LUNG
— Blocked on real tenant baseline data —
├── BaselineMonitor
├── ScalingTriggerEngine (calibrated from real data)
├── LungController
├── ProtectionDepthDial (Dial 1)
└── ThreatFocusDial (Dial 2) ← NEW June 9

PHASE 8 — GOVERNANCE COMPLETION
├── OperatorOverrideLog
├── MutationAuditTrail
└── DriftDetectionMonitor

PHASE 9 — THE PLAYHOUSE
├── EvidenceChainViewer
├── TechOverridePath
├── ProtectionDepthDial UI
├── ThreatFocusDial UI ← NEW June 9
├── CollectiveImmuneStatusPanel
├── MutationLogViewer
├── AgentFissionLog ← NEW June 9
├── CostAttributionDashboard
└── MultiTenantOverview
```

---

## ALREADY BUILT AND GOVERNED

| Agent | Layer | Status | Commit |
|---|---|---|---|
| HeaderDivergenceAgent | 2 Detection | GATED | 2cefbaf |
| EmailAuthenticationAgent | 2 Detection | GATED | 2cefbaf |
| GhostThreadAgent | 2 Detection | GATED | 2cefbaf |
| Verification Outcome Agent | 3 Verification | §11 SIGNED | 8e2b787 |
| Phase 1 Infrastructure | 6 Governance | §11 SIGNED | fe355da |

---

## GATE REQUIREMENTS BEFORE ANY PHASE IS CLOSED

- `complete_gate.py` must show 0/0
- Three test classes per agent: expected-pass, adversarial, known-gap xfail with written reason
- Matt signs phase closure — sole authority
- No push, no tracker edits without Matt's explicit go-ahead

---

## §11 — SIGNATURE BLOCK
This document requires §11 signature before it becomes the build authority.
Currently advisory — reference only.

**Signed:** ___________________________
**Date:** ___________________________
