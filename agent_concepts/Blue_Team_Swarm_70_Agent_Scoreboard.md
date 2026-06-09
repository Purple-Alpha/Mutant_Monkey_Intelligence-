# Blue-Team Swarm — 70-Agent Build Scoreboard (v2 — Build Sequencer)

**Status:** WORKING SCOREBOARD + **BUILD SEQUENCER** (canonical candidate generator). Amendment **LIVE 2026-06-08** — rubric D13-rev §12 SIGNED by Matt Nichol (Option B, `_Build_Sequencer_Adoption_Consequence_Matrix.md`). Authority-free — **builds nothing, authorizes nothing.** A row is status + sequencing input, never build permission (Rule 4). Does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec.

**Authority chain (LIVE 2026-06-08):** this file **generates** actionable-now candidates -> Next-Action Decision Rubric **ranks** -> Matt **selects** -> `decision_cycles_log.md` records. `PROJECT_HANDSHAKE.md` is today's one-screen derived view. `PROJECT_BUILD_AND_AUDIT_QUEUE.md` is **retired** (historical only). AGENTS.md §3.2 Steps 0.5/6.5 are in force.

**Sources reconciled:**
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` — the canonical 70-agent / 10-team inventory (agent IDs #1-#70 come from here).
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` — the adopted canonical 6-layer design shaping.
- Live runtime: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/` + `tests/`.

---

## Build Sequencer — critical path header (read this first)

Updated each session at Step 6.5 (AGENTS.md §3.2). **This is the one-screen answer to "what's next."**

**#1 TARGET:** full 70-agent governed blue-team swarm (non-reducible).

**BREADTH RUNWAY:** **10** of 70 agents at `GOVERNED_AGENT` (Evidence Stage 1 Synthetic): #6, #6A, #8, #10, #23, #24, #27, #30, #39, #46.

**Actionable-now (`BLOCKERS` empty, `TRACK=BREADTH`, dependencies satisfied):** **CYCLE 19 (2026-06-08) — OPERATOR_LOCK:** clean pure-wrap BREADTH runway exhausted; Build Map §6/§7 selected the highest-priority blocked Detection candidate as the named UNBLOCK action. **#31 PDF Fingerprint** boundary contract drafted at `4. Product_Roadmap/PDF_Fingerprint_Agent_Design_Contract_Deep_Dive.md` (commit `863eb93`); §11 signature pending. Scope: stateful Layer 2 Detection boundary around signed `assess_document_metadata_fingerprint`; preserves `check_signal` -> `ingest_signal` ordering for `pdf_producer_fingerprint`; synthetic Stage 1 only; no detector/store behavior change, no PDF byte parsing, no raw metadata/hash/filename leakage, no default registry, no production dispatch, no real-customer-data handling, no Evidence Stage 2/3 promotion, no autonomy. **#23**, **#24**, **#27**, **#30**, **#39**, and **#46** are `GOVERNED_AGENT` awaiting Stage 2 promotion (depth gate CLOSED). Next action: **BLOCKED ON §11 SIGNATURE — PDF_Fingerprint_Agent_Design_Contract_Deep_Dive.md**.

**DEPTH GATE: CLOSED.** Stage 2+ promotion blocked until real-data intake opens (Production Evidence Store infra + controls activation + separate operator authorization). Agents #54-#60 carry `NEEDS_REAL_DATA`.

**STAGE_B GATE: CLOSED.** Autonomy agents (e.g. #38 Containment) blocked until signed Stage B authorization. `#38` carries `NEEDS_STAGE_B_AUTH`.

**Generator -> Rubric -> Select:** scoreboard rows with empty `BLOCKERS` feed the rubric (3-7 candidates, include "do nothing" per D19). Rubric ranks; Matt selects. Scores are never decisions.

---

## Legend + reconciliation rules

**Runtime status (execution-lane verified against code):**
- `GOVERNED_AGENT` — implemented AND carries Agent Design Contract metadata (layer/authority/boundary/evidence/two-pass/DER). Per project state #10 and #21 carry the metadata-only retrofit (#21 has metadata but no detector code), and #6 Header Analysis is the first full per-agent signed contract (2026-06-07, Evidence Stage 1) with both detector code and a governed runtime wrapper.
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

**Build Sequencer columns (closed vocabulary):**
- **`BLOCKERS`** — empty = actionable-now. Values: `NEEDS_SIGNED_CONTRACT`, `NEEDS_BUILD_AUTH`, `NEEDS_REAL_DATA`, `NEEDS_STAGE_B_AUTH`, `NEEDS_DRIFT_WATCH`, `DEPENDS_ON:[agent_id]`, `merged`.
- **`TRACK`** — `BREADTH` (Stage 1 wrap / synthetic path, unblocked), `DEPTH` (Stage 2+ / real-data gate), `STAGE_B` (autonomy gate).
- **`LAST_RUBRIC_SCORE`** — total from last rubric cycle when this row was a candidate (`—` if never).
- **`LAST_UPDATED`** — commit hash when row last touched (`adoption` = backfilled 2026-06-08).

---

## Team 1 — Swarm command (SPARK #1-#5)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Swarm Commander Agent | `DETECTOR_FUNCTION` (partial spine) | `core/orchestrator/routes.py`, `registry.py`, `swarm_commander.py` (router + registry + Stage A case loop + in-memory DER assembly + Layer 5 challenge pass over real `AgentContribution` objects; not a formally promoted governed agent) | 1 Command | A |  | BREADTH | — | adoption |
| 2 | Mission Context Agent | `NOT_STARTED` | none | 1 Command | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 3 | Risk Triage Agent | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` | 1 Command | A |  | BREADTH | — | adoption |
| 4 | Human-in-the-Loop Agent | `GOVERNANCE_DOC_ONLY` | VISION non-negotiables 6/7; `core/operator_state/` kill-switch | 1 Command | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 5 | Decision Integrity Agent | `GOVERNANCE_DOC_ONLY` | AGENTS authority model; client-facing rubric contradiction guard | 6 Learning/Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 2 — Email identity / sender (SPARK #6-#12)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 6 | Header Analysis | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-07 `4. Product_Roadmap/Header_Analysis_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/scoring/header_divergence_detector.py`, `received_chain_parser.py`; governed wrapper `core/orchestrator/header_divergence_agent.py` (`HeaderDivergenceAgent`, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | — | 2cefbaf |
| 6A | Email Authentication (SPF/DKIM/DMARC) — net-new governed agent, split from #6 code evidence at contract signing 2026-06-07 (§10 Q1; gateway authentication posture, NOT domain divergence) | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-07 `4. Product_Roadmap/Email_Authentication_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/scoring/email_authentication_detector.py` (gateway SPF/DKIM/DMARC posture parsed from `Authentication-Results`; lift-only, never lowers risk on pass); governed wrapper `core/orchestrator/email_authentication_agent.py` (`EmailAuthenticationAgent`, committed `8e3df20`, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER -> Layer 5 challenge pass) | 2 Detection | A |  | BREADTH | — | 2cefbaf |
| 7 | Sender Identity | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` (impersonation_analysis) | 2 Detection | A |  | BREADTH | — | adoption |
| 8 | Ghost Thread Agent (renamed from "Reply-To Mismatch" 2026-06-07; Reply-To divergence is #6's signal, not #8's) | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-07 `4. Product_Roadmap/Ghost_Thread_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/scoring/ghost_thread_detector.py` (fake thread continuity: Re/Fw/Fwd subject prefix + missing non-empty In-Reply-To/References — NOT Reply-To divergence); governed wrapper `core/orchestrator/ghost_thread_agent.py` (`GhostThreadAgent`, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER -> Layer 5 challenge pass) | 2 Detection | A |  | BREADTH | — | 2cefbaf |
| 9 | Domain Reputation | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 10 | Lookalike Domain | `GOVERNED_AGENT` | `core/scoring/lookalike_domain_detector.py` + signed spec w/ Agent Design Contract wrapper | 2 Detection | A |  | BREADTH | — | 2cefbaf |
| 11 | Known-Good Contact | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 3 Verification | A |  | BREADTH | — | adoption |
| 12 | Compromised Mailbox Suspicion | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 3 — Vendor-payment / BEC (SPARK #13-#22)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 13 | Vendor Relationship Intelligence | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 2 Detection | A |  | BREADTH | — | adoption |
| 14 | Payment Change Detection | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` | 2 Detection | A |  | BREADTH | — | adoption |
| 15 | Invoice Fraud | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` (invoice_authenticity_score) | 2 Detection | A |  | BREADTH | — | adoption |
| 16 | Bank Detail Drift | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` + vendor baseline | 2 Detection | A |  | BREADTH | — | adoption |
| 17 | Vendor Master Record | `DETECTOR_FUNCTION` | `core/production_state/vendor_baseline/store.py` | 3 Verification | A |  | BREADTH | — | adoption |
| 18 | Callback Verification | `DETECTOR_FUNCTION` | `core/scoring/callback_phishing_detector.py` + `core/workflows/two_channel_confirmation.py` (detector/workflow split requires signed boundary before a governed wrapper) | 3 Verification | A | NEEDS_SIGNED_CONTRACT | BREADTH | 7 | cycle12 |
| 19 | Dual-Approval | `SPEC_ONLY` | Vendor Payment Verification Workflow (draft) | 3 Verification | A | NEEDS_SIGNED_CONTRACT | BREADTH | — | adoption |
| 20 | Financial Exposure | `DETECTOR_FUNCTION` | `core/scoring/financial_state_ledger.py` | 2 Detection | A |  | BREADTH | — | adoption |
| 21 | Executive Impersonation | `SPEC_ONLY` | signed spec + Agent Design Contract metadata; **no detector code** | 2 Detection | A | NEEDS_SIGNED_CONTRACT | BREADTH | — | adoption |
| 22 | Payroll Diversion | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 4 — Phishing / credential (SPARK #23-#29)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 23 | Credential Phishing | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/Credential_Phishing_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/precursor/body_signal_detector.py` (`score_credential_harvesting`, immutable pure detector called read-only); governed wrapper `core/orchestrator/credential_phishing_agent.py` (`CredentialPhishingAgent`, committed `75affc6`, facts-only closed credential-harvesting indicator names from body_plain/body_html/subject, 17 focused tests incl. purity guard, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | 10 | 75affc6 |
| 24 | MFA Manipulation | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/MFA_Manipulation_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/precursor/body_signal_detector.py` (`score_mfa_fatigue`, immutable pure detector called read-only); governed wrapper `core/orchestrator/mfa_manipulation_agent.py` (`MFAManipulationAgent`, committed `09c5425`, facts-only closed MFA-manipulation indicator names from body_plain/body_html/subject, 18 focused tests incl. purity + one-time-code no-leak guards, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | 10 | 09c5425 |
| 25 | Session Theft | `RECLASSIFY` (Build Map TRIAGE 2026-06-08) | **RECLASSIFY:** expected OAuth/session-token / device-code theft detector; actual cited file is `core/scoring/prompt_injection_detector.py` — an LLM prompt-injection detector (different agent concept). No standalone session-theft detector exists. Re-triage trigger: Frontier Intake Candidate 5 device-code/OAuth detector built OR row split to a separate Prompt Injection agent entry. | 2 Detection | A |  | BREADTH | — | 4987da6 |
| 26 | QR Phishing | `NOT_STARTED` | none (flagged in Frontier Intake) | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 27 | Link Inspection | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/Link_Inspection_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/precursor/url_obfuscation_detector.py` (immutable, called read-only); governed wrapper `core/orchestrator/link_inspection_agent.py` (`LinkInspectionAgent`, committed `463cb4e`, facts-only closed URL indicator names, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | 9 | 463cb4e |
| 28 | Brand Impersonation | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 29 | Form Abuse | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 5 — Attachment / ransomware precursor (SPARK #30-#38)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 30 | Attachment Risk | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/Attachment_Risk_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/precursor/attachment_classifier.py` (immutable static detector, called read-only); governed wrapper `core/orchestrator/attachment_risk_agent.py` (`AttachmentRiskAgent`, committed `0f7fd56`, facts-only closed attachment indicator names, source-order dedupe, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | 10 | 0f7fd56 |
| 31 | PDF Fingerprint | `SPEC_ONLY` (draft boundary Agent Design Contract; §11 signature pending) | `core/scoring/document_metadata_detector.py` (`assess_document_metadata_fingerprint`, §11-signed metadata-only detector that mutates per-tenant Vendor Baseline Store via `check_signal` -> `ingest_signal` for `pdf_producer_fingerprint`); draft boundary contract `4. Product_Roadmap/PDF_Fingerprint_Agent_Design_Contract_Deep_Dive.md` committed `863eb93`. State boundary: synthetic Stage 1 wrapper only, facts-only indicator/count contribution, no detector/store behavior change, no PDF byte parsing, no raw metadata/hash/filename leakage. | 2 Detection | A | NEEDS_SIGNED_CONTRACT | BREADTH | 10 | 863eb93 |
| 32 | Macro/Script Risk | `merged` (Build Map TRIAGE 2026-06-08) | **merged into #30 Attachment Risk:** same underlying `core/precursor/attachment_classifier.py` surface; #30 already governs `score_attachment_risk` facts including `macro_enabled_office_document`. Re-triage trigger: a distinct macro/script detector surface exists outside #30's signed boundary. | 2 Detection | A | merged | BREADTH | — | 626295f |
| 33 | Payload Delivery | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 34 | Remote Access Abuse | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 35 | Inbox Rule Abuse | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 36 | Account Takeover | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 37 | Ransomware Precursor | `RECLASSIFY` (Build Map TRIAGE 2026-06-08) | **RECLASSIFY:** `core/precursor/analysis.py` is an overlay/aggregate builder over already-governed #30 Attachment Risk, #27 Link Inspection, #23 Credential Phishing, and #24 MFA Manipulation detector surfaces; not a clean one-agent Layer 2 detector wrap. Re-triage trigger: signed aggregate/boundary contract defining whether this belongs as Evidence/Challenge synthesis rather than Layer 2. | 2 Detection | A |  | BREADTH | — | 626295f |
| 38 | Containment Recommendation | `NOT_STARTED` | none — **Stage B (autonomy-gated)** | 2 Detection | B | NEEDS_STAGE_B_AUTH | STAGE_B | — | adoption |

## Team 6 — Language / behavior / deception (SPARK #39-#45)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 39 | Language Pressure | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/Language_Pressure_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/scoring/callback_phishing_detector.py` (`detect_callback_phishing`, immutable pure detector called read-only); governed wrapper `core/orchestrator/language_pressure_agent.py` (`LanguagePressureAgent`, committed `4987da6`, facts-only closed TOAD v1 category names from body_plain only, 18 focused tests incl. body_plain-only boundary + no risk-floor/phrase/phone leakage + purity guard, tested end-to-end through the Agent contract -> AgentContribution -> blackboard -> DER) | 2 Detection | A |  | BREADTH | 10 | 4987da6 |
| 40 | Tone Drift | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 41 | Behavioral Baseline | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 42 | Timing Anomaly | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 43 | Geo-Context | `SPEC_ONLY` | Sender Provenance / Geo-Velocity proof protocol; `received_chain_parser.py` foundation only | 2 Detection | A | NEEDS_SIGNED_CONTRACT | BREADTH | — | adoption |
| 44 | Social Engineering | `merged` (Build Map TRIAGE 2026-06-08) | **merged into #39 Language Pressure:** same `core/scoring/callback_phishing_detector.py` TOAD/body-language surface now governed by `LanguagePressureAgent`. Re-triage trigger: a distinct social-engineering detector exists outside #39's signed TOAD v1 boundary. | 2 Detection | A | merged | BREADTH | — | 626295f |
| 45 | Process Bypass | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 7 — Evidence / audit (SPARK #46-#53)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 46 | Evidence Package | `GOVERNED_AGENT` (Evidence Stage 1 — Synthetic; **§11-signed Agent Design Contract 2026-06-08 `4. Product_Roadmap/Evidence_Package_Agent_Design_Contract_Deep_Dive.md`**; not in `build_default_registry` / no production dispatch at Stage 1) | `core/evidence_package/package_generator.py` (`generate_package_from_test_plan`, signed Pass 1 internal assembler, called read-only); governed wrapper `core/orchestrator/evidence_package_agent.py` (`EvidencePackageAgent`, committed `fdac7db`, **first Layer 4 Evidence agent**, facts-only closed package-metadata key set + `control_mapping` + bounded Stage 1 `underwriter_note`, 16 focused tests incl. builder/auditor separation, no Grok/PDF/done declaration, no default registry, purity + no-source-leak guards, tested through the Agent contract -> AgentContribution -> blackboard) | 4 Evidence | A |  | BREADTH | 10 | fdac7db |
| 47 | Case Timeline | `DETECTOR_FUNCTION` (partial) | Reaction Timing Log + `audit_trail` in evidence package | 4 Evidence | A |  | BREADTH | — | adoption |
| 48 | Verification Outcome | `DETECTOR_FUNCTION` | `core/workflows/two_channel_confirmation.py` (outcome events) | 3 Verification | A |  | BREADTH | — | adoption |
| 49 | Audit Trail | `DETECTOR_FUNCTION` | `core/blackboard/` append-only + `evidence_package/audit_packet.py` | 4 Evidence | A |  | BREADTH | — | adoption |
| 50 | Evidence Strength | `SPEC_ONLY` | Email Security Testing framework (draft) | 4 Evidence | A | NEEDS_SIGNED_CONTRACT | BREADTH | — | adoption |
| 51 | Assumption Control | `GOVERNANCE_DOC_ONLY` | claim-boundary discipline; not a runtime module | 4 Evidence | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 52 | Plain-English Explanation | `DETECTOR_FUNCTION` | `core/scoring/client_facing_rubric.py` (signed 5-axis rubric, why_this_score) | 4 Evidence | A |  | BREADTH | — | adoption |
| 53 | Safe Language | `GOVERNANCE_DOC_ONLY` | `Compliance_and_Trend_Watch_Process.md` §5 + `complete_gate.py` forbidden-language | 6 Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 8 — Cyber insurance (SPARK #54-#60)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 54 | Cyber Insurance Evidence | `DETECTOR_FUNCTION` | `core/evidence_package/` (signed Cyber Insurance Evidence Package) | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 55 | Control Mapping | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 56 | Renewal Readiness | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 57 | Underwriter Summary | `SPEC_ONLY` | cyber-insurance spec partial | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 58 | Claim Support | `NOT_STARTED` | none | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 59 | Exception Tracking | `NOT_STARTED` | none | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |
| 60 | Evidence Freshness | `SPEC_ONLY` | freshness policy in cyber-insurance spec §6.1 | 4 Evidence | A | NEEDS_REAL_DATA | DEPTH | — | adoption |

## Team 9 — Learning / testing (SPARK #61-#68)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 61 | Test Case Generator | `DETECTOR_FUNCTION` | `core/sandbox/red_agents/` (synthetic case generators) | 5 Challenge/Red-Team | A |  | BREADTH | — | adoption |
| 62 | Regression Test | `DETECTOR_FUNCTION` | `tests/` pytest suite + cadence gate | 5 Challenge/Red-Team | A |  | BREADTH | — | adoption |
| 63 | Adversarial Test | `DETECTOR_FUNCTION` | `core/sandbox/red_battery.py` | 5 Challenge/Red-Team | A |  | BREADTH | — | adoption |
| 64 | Failure Classification | `SPEC_ONLY` | Email Security Testing failure cards (draft) | 5 Challenge/Red-Team | A | NEEDS_SIGNED_CONTRACT | BREADTH | — | adoption |
| 65 | Correction Evidence | `GOVERNANCE_DOC_ONLY` | CURRENT_STATE_MAP FP/FN correction loop | 6 Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 66 | Drift Watch | `GOVERNANCE_DOC_ONLY` | `Compliance_and_Trend_Watch_Process.md` (signed) | 6 Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 67 | Rule Improvement | `DETECTOR_FUNCTION` (sandbox) | `core/mutation/engine.py` (sandbox-only, signed promotion) | 6 Governance | A |  | BREADTH | — | adoption |
| 68 | Swarm Memory | `NOT_STARTED` | none | 6 Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

## Team 10 — Review / decision integrity (SPARK #69-#70)

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer (pinned) | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 69 | Swarm Health | `NOT_STARTED` | none | 6 Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
| 70 | Final Review Agent | `GOVERNANCE_DOC_ONLY` (partial) | `complete_gate.py` + `core/evidence_package/package_auditor.py` | 6 Learning/Governance | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |

---

## Tally (execution-lane verified, file-level)

- `GOVERNED_AGENT`: **10** (#10; #6 Header Analysis, #8 Ghost Thread, and #6A Email Authentication at Evidence Stage 1, §11-signed 2026-06-07; #27 Link Inspection, #30 Attachment Risk, #23 Credential Phishing, #24 MFA Manipulation, #39 Language Pressure, and #46 Evidence Package at Evidence Stage 1, §11-signed 2026-06-08; #46 is the first Layer 4 Evidence agent).
- `DETECTOR_FUNCTION`: **~22** (the scoring/precursor/vendor-baseline/evidence/sandbox/blackboard surfaces; #6 and #8 promoted out on 2026-06-07, #27, #30, #23, and #24 on 2026-06-08, #39 on 2026-06-08; #31 PDF Fingerprint carries NEEDS_SIGNED_CONTRACT; #25 Session Theft marked RECLASSIFY by Build Map triage).
- `GOVERNANCE_DOC_ONLY`: **7** (#4, #5, #51, #53, #65, #66, #70-partial).
- `SPEC_ONLY`: **7** (#19, #21, #43, #50, #55, #56, #57, #60 — note #21 has metadata but no code).
- `NOT_STARTED`: **~22** (the net-new detection + orchestration + memory/health agents).

**Headline:** the swarm is currently a **detector stack plus a partially wired governance spine, not yet a governed swarm**. Ten agents (#10 Lookalike, #6 Header Analysis, #8 Ghost Thread, #6A Email Authentication, #27 Link Inspection, #30 Attachment Risk, #23 Credential Phishing, #24 MFA Manipulation, #39 Language Pressure, #46 Evidence Package) are now governed agents at Evidence Stage 1 Synthetic; #39 and #46 were selected by the LIVE Build Map and #46 is the first Layer 4 Evidence agent (now spanning Detection and Evidence layers). Everything else that "exists" is either a detector function inside the scoring pipeline or a spine component that still lacks a formal per-agent contract. Build Map triage marked #25 Session Theft RECLASSIFY (mislabeled — its cited detector is the prompt-injection detector) and merged #32 into #30 and #44 into #39. The orchestration spine has a router + registry + Stage A case loop + in-memory Decision Evidence Record assembly + Layer 5 aggregate challenge pass + one Layer 5 Challenge agent at Evidence Stage 1.

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

---

## Build Sequencer amendment — locked decisions (LIVE 2026-06-08)

Governance rules for this file as canonical candidate generator. Rubric D13-rev §12 SIGNED 2026-06-08 by Matt Nichol on `Next_Action_Decision_Rubric_Deep_Dive.md`.

| # | Decision | Locked value |
|---|---|---|
| BS-D1 | Four columns | `BLOCKERS`, `TRACK`, `LAST_RUBRIC_SCORE`, `LAST_UPDATED` — closed vocabularies per Legend above. |
| BS-D2 | Critical-path header | Header section above updated every session at Build Loop Step 6.5. |
| BS-D3 | Generator rule | (1) Rows with empty `BLOCKERS` are actionable-now. (2) Exclude rows whose `DEPENDS_ON:[id]` dependency is not `GOVERNED_AGENT`. (3) `TRACK=DEPTH` candidates only when depth gate explicitly open (operator butterfly decision logged). (4) `TRACK=STAGE_B` only after signed Stage B authorization. (5) Trim to 3-7 by layer order (Command -> Detection -> Verification -> Evidence -> Challenge -> Learning) per Q5 build order. (6) Always allow "do nothing" as a rubric candidate (D19). |
| BS-D4 | Queue retirement | `PROJECT_BUILD_AND_AUDIT_QUEUE.md` retired as ordering authority; historical read-only. |
| BS-D5 | Build Loop integration | AGENTS.md §3.2 Steps 0.5 (freshness check) and 6.5 (row update) mandatory for swarm-map slices. Doctrine-enforced; gate automation deferred. |
| BS-D6 | Authority-free | Generator output is never build permission. Rule 4 extended to new columns. Matt selects; rubric ranks. |

**Row additions** require operator scope decision or signed scoreboard amendment. **Row updates** within adoption are execution-lane under §2.1.1.B when gated clean.

**Status:** rubric D13-rev §12 SIGNED 2026-06-08; this amendment is live across signed specs.
