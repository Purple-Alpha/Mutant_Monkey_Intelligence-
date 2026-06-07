# Blue-Team Swarm — 70-Agent Build Scoreboard (v1)

**Status:** WORKING SCOREBOARD, pre-spec, unsigned, NOT §11, authority-free. Created 2026-06-07 by Cursor (execution lane) reconciling the two adopted swarm maps against the live runtime. **Builds nothing, authorizes nothing.** A row here is a status record, never a build authorization (see Rule 4 below). Does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec.

**Sources reconciled:**
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` — the canonical 70-agent / 10-team inventory (agent IDs #1-#70 come from here).
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` — the adopted canonical 6-layer design shaping.
- Live runtime: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/` + `tests/`.

---

## Legend + reconciliation rules

**Runtime status (execution-lane verified against code):**
- `GOVERNED_AGENT` — implemented AND carries Agent Design Contract metadata (layer/authority/boundary/evidence/two-pass/DER). Per project state only #10 and #21 have the retrofit, and #21 has the metadata but no detector code.
- `DETECTOR_FUNCTION` — real, tested code exists, but it is a pipeline function, not a governed swarm agent.
- `GOVERNANCE_DOC_ONLY` — covered by VISION/AGENTS/gate or a signed spec, no dedicated runtime code.
- `SPEC_ONLY` — signed/drafted spec exists, no runtime code yet.
- `NOT_STARTED` — no current spec or runtime surface.

**Verification marks:**
- A cited `code path` = execution-lane verified the file exists. 
- `(file-level)` = verified the file exists; whether it *fully* satisfies the SPARK agent concept is not yet asserted.
- Status with no path = inferred from SPARK tag, **not yet code-verified**.

**Rule 4 (anti-laundering, from Claude review trap 11):** This scoreboard ranks and records status. It NEVER means "approved" or "ready to build." `recommended_*` and build-order are advisory only. Matt selects; the normal Rubric -> spec -> gate -> sign path authorizes each agent. A future session must not read a row as build permission.

**Layer-reconciliation tiebreaker (from Claude review):** when a SPARK agent maps ambiguously between two 6-layer placements, the **more restrictive (higher-authority / more-gated) layer wins** until Matt resolves it explicitly. All `canonical_6layer` values below are **DRAFT pending Claude design review per AGENTS §2.1.2** — pattern-reconciliation is Claude's lane, not the execution lane's.

**6 layers (Design Tree):** 1 Command | 2 Detection | 3 Verification | 4 Evidence | 5 Challenge/Red-Team | 6 Learning/Governance.

---

## Team 1 — Swarm command (SPARK #1-#5)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 1 | Swarm Commander | `DETECTOR_FUNCTION` (partial spine) | `core/orchestrator/routes.py`, `registry.py` (router + registry only; no case loop) | 1 Command | A |
| 2 | Mission Context | `NOT_STARTED` | none | 1 Command | A |
| 3 | Risk Triage | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` | 1 Command / 2 Detection (ambiguous → 1) | A |
| 4 | Human-in-the-Loop | `GOVERNANCE_DOC_ONLY` | VISION non-negotiables 6/7; `core/operator_state/` kill-switch | 1 Command | A |
| 5 | Decision Integrity | `GOVERNANCE_DOC_ONLY` | AGENTS authority model; client-facing rubric contradiction guard | 6 Governance (ambiguous w/ 1) | A |

## Team 2 — Email identity / sender (SPARK #6-#12)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 6 | Header Analysis | `DETECTOR_FUNCTION` | `core/scoring/header_divergence_detector.py`, `email_authentication_detector.py`, `received_chain_parser.py` | 2 Detection | A |
| 7 | Sender Identity | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` (impersonation_analysis) | 2 Detection | A |
| 8 | Reply-To Mismatch | `DETECTOR_FUNCTION` | `core/scoring/ghost_thread_detector.py` + header divergence | 2 Detection | A |
| 9 | Domain Reputation | `NOT_STARTED` | none | 2 Detection | A |
| 10 | Lookalike Domain | `GOVERNED_AGENT` | `core/scoring/lookalike_domain_detector.py` + signed spec w/ Agent Design Contract wrapper | 2 Detection | A |
| 11 | Known-Good Contact | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 3 Verification | A |
| 12 | Compromised Mailbox Suspicion | `NOT_STARTED` | none | 2 Detection | A |

## Team 3 — Vendor-payment / BEC (SPARK #13-#22)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 13 | Vendor Relationship Intelligence | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 2 Detection | A |
| 14 | Payment Change Detection | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` | 2 Detection | A |
| 15 | Invoice Fraud | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` (invoice_authenticity_score) | 2 Detection | A |
| 16 | Bank Detail Drift | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` + vendor baseline | 2 Detection | A |
| 17 | Vendor Master Record | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 3 Verification | A |
| 18 | Callback Verification | `DETECTOR_FUNCTION` | `core/scoring/callback_phishing_detector.py` + `core/workflows/two_channel_confirmation.py` | 3 Verification | A |
| 19 | Dual-Approval | `SPEC_ONLY` | Vendor Payment Verification Workflow (draft) | 3 Verification | A |
| 20 | Financial Exposure | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` | 2 Detection | A |
| 21 | Executive Impersonation | `SPEC_ONLY` | signed spec + Agent Design Contract metadata; **no detector code** | 2 Detection | A |
| 22 | Payroll Diversion | `NOT_STARTED` | none | 2 Detection | A |

## Team 4 — Phishing / credential (SPARK #23-#29)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 23 | Credential Phishing | `DETECTOR_FUNCTION` | `core/precursor/body_signal_detector.py` (credential-harvest signals) | 2 Detection | A |
| 24 | MFA Manipulation | `DETECTOR_FUNCTION` | `core/precursor/body_signal_detector.py` (mfa-fatigue signals) | 2 Detection | A |
| 25 | Session Theft | `DETECTOR_FUNCTION` (adjacent) | `core/scoring/prompt_injection_detector.py` (adjacent only) | 2 Detection | A |
| 26 | QR Phishing | `NOT_STARTED` | none (flagged in Frontier Intake) | 2 Detection | A |
| 27 | Link Inspection | `DETECTOR_FUNCTION` | `core/precursor/url_obfuscation_detector.py` | 2 Detection | A |
| 28 | Brand Impersonation | `NOT_STARTED` | none | 2 Detection | A |
| 29 | Form Abuse | `NOT_STARTED` | none | 2 Detection | A |

## Team 5 — Attachment / ransomware precursor (SPARK #30-#38)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 30 | Attachment Risk | `DETECTOR_FUNCTION` | `core/precursor/attachment_classifier.py` | 2 Detection | A |
| 31 | PDF Fingerprint | `DETECTOR_FUNCTION` | `core/scoring/document_metadata_detector.py` | 2 Detection | A |
| 32 | Macro/Script Risk | `DETECTOR_FUNCTION` (partial) | `core/precursor/attachment_classifier.py` (class subset) | 2 Detection | A |
| 33 | Payload Delivery | `NOT_STARTED` | none | 2 Detection | A |
| 34 | Remote Access Abuse | `NOT_STARTED` | none | 2 Detection | A |
| 35 | Inbox Rule Abuse | `NOT_STARTED` | none | 2 Detection | A |
| 36 | Account Takeover | `NOT_STARTED` | none | 2 Detection | A |
| 37 | Ransomware Precursor | `DETECTOR_FUNCTION` | `core/precursor/analysis.py` (overlay builder) | 2 Detection | A |
| 38 | Containment Recommendation | `NOT_STARTED` | none — **Stage B (autonomy-gated)** | 2 Detection | B |

## Team 6 — Language / behavior / deception (SPARK #39-#45)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 39 | Language Pressure | `DETECTOR_FUNCTION` | `core/scoring/callback_phishing_detector.py` (TOAD vocabulary) | 2 Detection | A |
| 40 | Tone Drift | `NOT_STARTED` | none | 2 Detection | A |
| 41 | Behavioral Baseline | `NOT_STARTED` | none | 2 Detection | A |
| 42 | Timing Anomaly | `NOT_STARTED` | none | 2 Detection | A |
| 43 | Geo-Context | `SPEC_ONLY` | Sender Provenance / Geo-Velocity proof protocol; `received_chain_parser.py` foundation only | 2 Detection | A |
| 44 | Social Engineering | `DETECTOR_FUNCTION` (partial) | `core/scoring/callback_phishing_detector.py` | 2 Detection | A |
| 45 | Process Bypass | `NOT_STARTED` | none | 2 Detection | A |

## Team 7 — Evidence / audit (SPARK #46-#53)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 46 | Evidence Package | `DETECTOR_FUNCTION` | `core/evidence_package/package_generator.py` | 4 Evidence | A |
| 47 | Case Timeline | `DETECTOR_FUNCTION` (partial) | Reaction Timing Log + `audit_trail` in evidence package | 4 Evidence | A |
| 48 | Verification Outcome | `DETECTOR_FUNCTION` | `core/workflows/two_channel_confirmation.py` (outcome events) | 3 Verification | A |
| 49 | Audit Trail | `DETECTOR_FUNCTION` | `core/blackboard/` append-only + `evidence_package/audit_packet.py` | 4 Evidence | A |
| 50 | Evidence Strength | `SPEC_ONLY` | Email Security Testing framework (draft) | 4 Evidence | A |
| 51 | Assumption Control | `GOVERNANCE_DOC_ONLY` | claim-boundary discipline; not a runtime module | 4 Evidence | A |
| 52 | Plain-English Explanation | `DETECTOR_FUNCTION` | `core/scoring/client_facing_rubric.py` (signed 5-axis rubric, why_this_score) | 4 Evidence | A |
| 53 | Safe Language | `GOVERNANCE_DOC_ONLY` | `Compliance_and_Trend_Watch_Process.md` §5 + `complete_gate.py` forbidden-language | 6 Governance | A |

## Team 8 — Cyber insurance (SPARK #54-#60)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 54 | Cyber Insurance Evidence | `DETECTOR_FUNCTION` | `core/evidence_package/` (signed Cyber Insurance Evidence Package) | 4 Evidence | A |
| 55 | Control Mapping | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 56 | Renewal Readiness | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 57 | Underwriter Summary | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 58 | Claim Support | `NOT_STARTED` | none | 4 Evidence | A |
| 59 | Exception Tracking | `NOT_STARTED` | none | 4 Evidence | A |
| 60 | Evidence Freshness | `SPEC_ONLY` | freshness policy in cyber-insurance spec §6.1 | 4 Evidence | A |

## Team 9 — Learning / testing (SPARK #61-#68)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 61 | Test Case Generator | `DETECTOR_FUNCTION` | `core/sandbox/red_agents/` (synthetic case generators) | 5 Challenge/Red-Team | A |
| 62 | Regression Test | `DETECTOR_FUNCTION` | `tests/` pytest suite + cadence gate | 5 Challenge/Red-Team | A |
| 63 | Adversarial Test | `DETECTOR_FUNCTION` | `core/sandbox/red_battery.py` | 5 Challenge/Red-Team | A |
| 64 | Failure Classification | `SPEC_ONLY` | Email Security Testing failure cards (draft) | 5 Challenge/Red-Team | A |
| 65 | Correction Evidence | `GOVERNANCE_DOC_ONLY` | CURRENT_STATE_MAP FP/FN correction loop | 6 Governance | A |
| 66 | Drift Watch | `GOVERNANCE_DOC_ONLY` | `Compliance_and_Trend_Watch_Process.md` (signed) | 6 Governance | A |
| 67 | Rule Improvement | `DETECTOR_FUNCTION` (sandbox) | `core/mutation/engine.py` (sandbox-only, signed promotion) | 6 Governance | A |
| 68 | Swarm Memory | `NOT_STARTED` | none | 6 Governance | A |

## Team 10 — Review / decision integrity (SPARK #69-#70)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (DRAFT) | Stage |
|---|---|---|---|---|---|
| 69 | Swarm Health | `NOT_STARTED` | none | 6 Governance | A |
| 70 | Final Review | `GOVERNANCE_DOC_ONLY` (partial) | `complete_gate.py` + `core/evidence_package/package_auditor.py` | 1 Command / 6 Governance | A |

---

## Tally (execution-lane verified, file-level)

- `GOVERNED_AGENT`: **1** (#10).
- `DETECTOR_FUNCTION`: **~28** (the scoring/precursor/vendor-baseline/evidence/sandbox/blackboard surfaces).
- `GOVERNANCE_DOC_ONLY`: **7** (#4, #5, #51, #53, #65, #66, #70-partial).
- `SPEC_ONLY`: **7** (#19, #21, #43, #50, #55, #56, #57, #60 — note #21 has metadata but no code).
- `NOT_STARTED`: **~22** (the net-new detection + orchestration + memory/health agents).

**Headline:** the swarm is currently a **detector stack, not a governed swarm**. Exactly one agent (#10) is a governed agent; everything else that "exists" is a detector function inside the scoring pipeline. The orchestration spine (#1 Commander case loop, #2 Mission Context) is the critical gap — a router + registry exist, but no case loop assembles agents into one governed decision with a Decision Evidence Record.

---

## Open reconciliation questions — ROUTED TO CLAUDE (AGENTS §2.1.2, design/pattern-reconciliation lane)

The execution lane built the verified-status columns above. The following are design/reconciliation decisions and are **not** the execution lane's to finalize:

1. **Canonical 6-layer placement for the ambiguous agents** — #3 (Command vs Detection), #5 (Command vs Governance), #11/#17 (Detection vs Verification), #70 (Command vs Governance). Apply the more-restrictive-layer tiebreaker until Matt resolves.
2. **Canonical agent names per slot** — the Command layer differs between maps (Risk Triage + Decision Integrity vs Severity Commander + Final Review). Pin one name per agent.
3. **The ~36 agents in SPARK but not in the Design Tree's ~34-agent canonical tree** — confirm each is in-scope for the full 70, or explicitly parked.
4. **"Done = governed agent" definition per layer** — what fields/tests/DER contribution make a DETECTOR_FUNCTION count as a GOVERNED_AGENT for its layer.
5. **Build order** — recommended: spine first (#1 case loop, #2 Mission Context, the DER record type, the agent interface), then wrap existing DETECTOR_FUNCTIONs into governed agents, then net-new detectors, then Stage B (#38). Confirm/resequence.
