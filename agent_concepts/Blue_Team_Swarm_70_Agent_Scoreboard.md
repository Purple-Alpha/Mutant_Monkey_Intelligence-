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

**Layer-reconciliation tiebreaker (from Claude review):** when a SPARK agent maps ambiguously between two 6-layer placements, the **more restrictive (higher-authority / more-gated) layer wins** until Matt resolves it explicitly.

**RECONCILIATION RESOLVED 2026-06-07** — the five open questions were routed to Claude (design/pattern-reconciliation lane per AGENTS §2.1.2) and pinned by Matt. The pins are recorded in full in the "Reconciliation resolved" section at the foot of this file; the layer column below is now pinned (no longer DRAFT) accordingly.

**6 layers (Design Tree):** 1 Command | 2 Detection | 3 Verification | 4 Evidence | 5 Challenge/Red-Team | 6 Learning/Governance.

---

## Team 1 — Swarm command (SPARK #1-#5)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 1 | Swarm Commander Agent | `DETECTOR_FUNCTION` (partial spine) | `core/orchestrator/routes.py`, `registry.py` (router + registry only; no case loop) | 1 Command | A |
| 2 | Mission Context Agent | `NOT_STARTED` | none | 1 Command | A |
| 3 | Risk Triage Agent | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` | 1 Command | A |
| 4 | Human-in-the-Loop Agent | `GOVERNANCE_DOC_ONLY` | VISION non-negotiables 6/7; `core/operator_state/` kill-switch | 1 Command | A |
| 5 | Decision Integrity Agent | `GOVERNANCE_DOC_ONLY` | AGENTS authority model; client-facing rubric contradiction guard | 6 Learning/Governance | A |

## Team 2 — Email identity / sender (SPARK #6-#12)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 6 | Header Analysis | `DETECTOR_FUNCTION` | `core/scoring/header_divergence_detector.py`, `email_authentication_detector.py`, `received_chain_parser.py` | 2 Detection | A |
| 7 | Sender Identity | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` (impersonation_analysis) | 2 Detection | A |
| 8 | Reply-To Mismatch | `DETECTOR_FUNCTION` | `core/scoring/ghost_thread_detector.py` + header divergence | 2 Detection | A |
| 9 | Domain Reputation | `NOT_STARTED` | none | 2 Detection | A |
| 10 | Lookalike Domain | `GOVERNED_AGENT` | `core/scoring/lookalike_domain_detector.py` + signed spec w/ Agent Design Contract wrapper | 2 Detection | A |
| 11 | Known-Good Contact | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 3 Verification | A |
| 12 | Compromised Mailbox Suspicion | `NOT_STARTED` | none | 2 Detection | A |

## Team 3 — Vendor-payment / BEC (SPARK #13-#22)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
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

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 23 | Credential Phishing | `DETECTOR_FUNCTION` | `core/precursor/body_signal_detector.py` (credential-harvest signals) | 2 Detection | A |
| 24 | MFA Manipulation | `DETECTOR_FUNCTION` | `core/precursor/body_signal_detector.py` (mfa-fatigue signals) | 2 Detection | A |
| 25 | Session Theft | `DETECTOR_FUNCTION` (adjacent) | `core/scoring/prompt_injection_detector.py` (adjacent only) | 2 Detection | A |
| 26 | QR Phishing | `NOT_STARTED` | none (flagged in Frontier Intake) | 2 Detection | A |
| 27 | Link Inspection | `DETECTOR_FUNCTION` | `core/precursor/url_obfuscation_detector.py` | 2 Detection | A |
| 28 | Brand Impersonation | `NOT_STARTED` | none | 2 Detection | A |
| 29 | Form Abuse | `NOT_STARTED` | none | 2 Detection | A |

## Team 5 — Attachment / ransomware precursor (SPARK #30-#38)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
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

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 39 | Language Pressure | `DETECTOR_FUNCTION` | `core/scoring/callback_phishing_detector.py` (TOAD vocabulary) | 2 Detection | A |
| 40 | Tone Drift | `NOT_STARTED` | none | 2 Detection | A |
| 41 | Behavioral Baseline | `NOT_STARTED` | none | 2 Detection | A |
| 42 | Timing Anomaly | `NOT_STARTED` | none | 2 Detection | A |
| 43 | Geo-Context | `SPEC_ONLY` | Sender Provenance / Geo-Velocity proof protocol; `received_chain_parser.py` foundation only | 2 Detection | A |
| 44 | Social Engineering | `DETECTOR_FUNCTION` (partial) | `core/scoring/callback_phishing_detector.py` | 2 Detection | A |
| 45 | Process Bypass | `NOT_STARTED` | none | 2 Detection | A |

## Team 7 — Evidence / audit (SPARK #46-#53)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
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

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 54 | Cyber Insurance Evidence | `DETECTOR_FUNCTION` | `core/evidence_package/` (signed Cyber Insurance Evidence Package) | 4 Evidence | A |
| 55 | Control Mapping | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 56 | Renewal Readiness | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 57 | Underwriter Summary | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A |
| 58 | Claim Support | `NOT_STARTED` | none | 4 Evidence | A |
| 59 | Exception Tracking | `NOT_STARTED` | none | 4 Evidence | A |
| 60 | Evidence Freshness | `SPEC_ONLY` | freshness policy in cyber-insurance spec §6.1 | 4 Evidence | A |

## Team 9 — Learning / testing (SPARK #61-#68)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
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

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage |
|---|---|---|---|---|---|
| 69 | Swarm Health | `NOT_STARTED` | none | 6 Governance | A |
| 70 | Final Review Agent | `GOVERNANCE_DOC_ONLY` (partial) | `complete_gate.py` + `core/evidence_package/package_auditor.py` | 6 Learning/Governance | A |

---

## Tally (execution-lane verified, file-level)

- `GOVERNED_AGENT`: **1** (#10).
- `DETECTOR_FUNCTION`: **~28** (the scoring/precursor/vendor-baseline/evidence/sandbox/blackboard surfaces).
- `GOVERNANCE_DOC_ONLY`: **7** (#4, #5, #51, #53, #65, #66, #70-partial).
- `SPEC_ONLY`: **7** (#19, #21, #43, #50, #55, #56, #57, #60 — note #21 has metadata but no code).
- `NOT_STARTED`: **~22** (the net-new detection + orchestration + memory/health agents).

**Headline:** the swarm is currently a **detector stack, not a governed swarm**. Exactly one agent (#10) is a governed agent; everything else that "exists" is a detector function inside the scoring pipeline. The orchestration spine (#1 Commander case loop, #2 Mission Context) is the critical gap — a router + registry exist, but no case loop assembles agents into one governed decision with a Decision Evidence Record.

---

## Reconciliation resolved (2026-06-07) — Claude design lane, pinned by Matt

The execution lane built the verified-status columns above. The five reconciliation questions were routed to Claude per AGENTS §2.1.2 and pinned by Matt. Decisions, verbatim in effect:

### Q1 — Canonical layer placement (pinned in the tables above)
- **#3 Risk Triage Agent → Layer 1 Command.** It scores and routes incoming signals to the right detection agents — orchestration, not detection. A detection agent observes; Risk Triage decides who observes.
- **#5 Decision Integrity Agent → Layer 6 Learning/Governance.** Restrictive tiebreaker applies hard: it audits whether decisions were made correctly. Placing it in Command would let it sit inside the loop it audits — violates builder-auditor separation.
- **#11 Known-Good Contact → Layer 3 Verification.** Confirms identity through a pre-registered out-of-band source; detection flags the anomaly, Known-Good Contact resolves it.
- **#17 Vendor Master Record → Layer 3 Verification.** A baseline reference used during verification; feeds Verification agents, does not detect independently.
- **#70 Final Review Agent → Layer 6 Learning/Governance.** Restrictive tiebreaker: it audits whether swarm output was correct. In Command it could authorize its own outputs.

### Q2 — Canonical names (pinned in the tables above)
| # | Canonical name | Reason |
|---|---|---|
| 1 | Swarm Commander Agent | Design Tree name, more precise |
| 2 | Mission Context Agent | exact match |
| 3 | Risk Triage Agent | SPARK name; "Severity Commander" implies Stage-A authority it must not hold |
| 4 | Human-in-the-Loop Agent | exact match |
| 5 | Decision Integrity Agent | exact match, now Layer 6 |
| 70 | Final Review Agent | "Final Review" correctly implies audit, not command |

### Q3 — SPARK-only agent scope (default in-scope; mark blockers, never silent exclusion)
Full 70 unless Matt explicitly parks. No agent is marked out-of-scope without Matt's call — the scoreboard marks the **blocker**, not the exclusion. Three blocker tags:
- `park_stage_b_c` — any agent whose primary function requires autonomous action (send a callback, block a payment, isolate a mailbox). In-scope conceptually, cannot be built until a Stage B authorization is signed. (e.g. #38 Containment.)
- `real_data_blocker` — cyber-insurance agents #54–#60 inherit the Compliance §5 claim-sensitive flag; not built until real-data controls (D9 calibration et al.) are in place.
- `merged` — any agent duplicating a function already covered by a governed agent at another layer: not parked, marked `merged` with a note on which agent absorbs it.

### Q4 — Promotion bar per layer (this is the "done = governed agent" definition)
A detector function becomes a `GOVERNED_AGENT` only when it clears the bar for its layer; until then it stays `DETECTOR_FUNCTION` no matter how much code exists.
- **L1 Command:** signed agent contract w/ routing rules + escalation conditions; explicit declaration of what it cannot authorize unilaterally; must NOT hold a Detection/Verification function in the same contract. Bar: contract + authority ceiling + documented human escalation path.
- **L2 Detection:** signed contract w/ data surface, trigger condition, output schema; ≥1 test proving it fires on a known-bad input and does not fire on a known-good input; Decision Evidence Record contribution declared (observed facts only — no interpretation at this layer without a separate pass). Bar: contract + passing known-input tests + DER fields declared.
- **L3 Verification:** signed contract; explicit declaration it uses only pre-registered known-good sources, NEVER data from the suspicious event; callback/confirmation outcome logged to the evidence chain. Bar: contract + written source-restriction rule + verified evidence-chain contribution.
- **L4 Evidence:** signed contract; builder-auditor separation enforced structurally (the agent that assembles a packet cannot audit it); sealed-bundle schema w/ SHA-256 anchor + immutability guarantee. Bar: contract + structural separation + signed bundle schema.
- **L5 Challenge/Red-Team:** signed contract; ≥1 documented failure mode it is designed to catch w/ a regression test proving the catch; Retest Evidence contribution (every challenge result logged, pass or fail). Bar: contract + failure mode + regression test + retest log.
- **L6 Learning/Governance:** signed contract; explicit declaration of NO write access to anything it audits; promotion/demotion conditions in writing; signed record of ≥1 decision it audited. Bar: contract + structural read-only constraint + written promotion conditions + one audited decision on record.

### Q5 — Build order (confirmed, spine-first, with one adjustment)
1. **Shared agent interface + Decision Evidence Record type first.** Everything builds against this; building governed agents before the DER type exists forces a retrofit of all of them.
2. **#1 Swarm Commander case loop + #2 Mission Context** — the orchestration spine; nothing routes correctly without them.
3. **Metadata-only retrofit for #10 Lookalike and #21 Executive Impersonation** — already closest to governed; add wrapper fields without touching signed detector contracts.
4. **Wrap existing detector functions into governed agents**, Detection-layer order, starting with highest evidence-value score.
5. **Net-new detectors** (no existing code), in build-order rank.
6. **Stage B autonomy agents** — #38 Containment and any `park_stage_b_c` agent — gated behind explicit signed Stage B authorization. Do not sequence until the Stage B spec is signed.

**Spine drift trap (watch during build):** the Swarm Commander case loop must be built as a **router, not a decision-maker.** It routes to Risk Triage; Risk Triage scores and routes to Detection. If the Commander starts absorbing Risk Triage's function, a Command agent is making detection-level decisions — the first drift trap.

**Authority note:** these pins resolve the SPARK↔Design-Tree ambiguity; they do not create or expand signed scope, and they do not authorize any agent build (Rule 4). The per-agent Rubric → spec → gate → sign path still governs each promotion.
