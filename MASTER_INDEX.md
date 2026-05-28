# NorthStar + SwarmCommand Venture - Master Index

## Purpose
This master index provides a complete, top-level map of the unified venture.
Use it to navigate all folders, subfolders, and key files across the system.

## Core Principle
NorthStar is the commercial business.
SwarmCommand is the internal automation engine.
The 60-agent platform is the long-term product vision.

## Primary Blueprint
- Business_Operations_Guide.md - the day-to-day operating guide and current project blueprint for running NorthStar Security.
- New_Operator_Training_Guide.md - the onboarding manual for contractors, VAs, junior analysts, and future operators.

## Project Control Files
- AGENTS.md - **Floor doctrine, authored 2026-05-27 by Matt Nichol.** Read every session before doing anything. Defines session-start read order, authority model (Matt decides / agents build / Grok audits / rubrics advisory), tone and behavior rules (no sycophancy, no rubber-stamp, low typing burden, ASCII-only), proxy-decision prohibitions (no auto-commit, no signing §11 in Matt's voice, no rubric-as-decision), audit-gate discipline (worker manifest required for "comprehensive" evidence quality), spec-first discipline (pre-§11 vs post-§11), the Next-Action Decision Rubric pointer, forbidden-language reference, operator context (one-handed typing, 14-Day Operating Doctrine Trial active), and the eight named failure modes from the existing specs (authority drift, Pass-1 wiring bug, decision laundering, calibration drift, naming collision, rubber-stamp audit, free-work perception, forbidden-language slip, Authorship Rule violation). Pre-§11 floor; will be superseded section-by-section by the forthcoming `4. Product_Roadmap/Operator_Companion_Agent_Deep_Dive.md` once signed.
- PROJECT_HANDSHAKE.md - the resume point and current active build target.
- PROJECT_BUILD_AND_AUDIT_QUEUE.md - one-page operator-readable queue artifact. Forward-only Build List + Audit List + named Next Action. Canonical for *ordering* across multiple items; PROJECT_HANDSHAKE.md remains canonical for the current single active focus; Matt's current instruction overrides both. No scoring, no progress markers, no completion claims.
- PROJECT_GUARDRAILS.md - the rules for keeping the project traceable and safe.
- PROJECT_ACTIVITY_LOG.md - the always-on update log for file and folder changes.
- PROJECT_AUDIT_REPORT_2026-05-20.md - latest runtime audit report after policy pipeline verification.
- PROGRESS.md - always-current weekly task tracker. Updated whenever a task closes.
- VISION.md - long-arc product thesis (Stage A Analyze + Recommend → Stage B Auto-Defend Obvious / Escalate Ambiguous → Stage C Self-Evolving Defense Swarm) + seven non-negotiables + what we will / won't keep up on.
- MILESTONE_ARC.md - multi-year milestone tracker (Stage A / B / C engineering + revenue + documentation milestones, each with a "done when" criterion + stage-crossing watchlist).
- THREAT_INTEL_LOG.md - swarm-evolution log: every threat pattern ingested + policy update that resulted. Seeded with eight planned free intake sources and the Phase 1.5 vendor-invoice recall floor as first entry.
- Frontier_Intake_Log.md - operator-driven log capturing emerging AI / agent / threat patterns observed during periodic frontier intake reviews. Cadence rule (locked 2026-05-25): 0-1 candidates surfaced per review → defer recurring discipline; 2-3 → quarterly cadence; 4+ → monthly cadence. Review #1 surfaced 5 candidates → monthly cadence committed (refinement flag at 90-day mark). Discovery layer only; formal gating happens separately in `think_sheet.md`.
- REVENUE_MAP.md - three-lane revenue plan (Lane 1 Survival Income via Kelowna employment + wage subsidy; Lane 2 Freelance via Contra/Upwork; Lane 3 NorthStar Revenue via 90-day MSP discovery program with 5-question discovery script + pricing experiments + sales-skills resources).
- THIRTY_DAY_PLAN.md - 2026-05-23 to 2026-06-22 revenue plan for turning Inbox Shield proof into first paid AI engineering work. Lane 2 detail of `REVENUE_MAP.md`.
- think_sheet.md - scoring rubric + stress-test gate that ideas pass through before they're allowed to touch the project plan.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md - pre-build proof protocol for the promoted sender-provenance / geo-velocity BEC detector idea. Defines the real-mailbox raw-header proof required before any spec-first runtime implementation may begin.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Runbook.md - operator-facing collection runbook for executing the sender-provenance cheaper proof safely against raw headers only.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv - sample classification worksheet for the raw-header proof run, with example `cloud_normalized` and `stable_high_value` rows.
- 4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md - pending-signature addendum to widen the Vendor Baseline Store closed signal enum for future sender-origin and callback-phone baselines. Spec-only; no implementation until §11 is signed.
- 4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md - **§11 SIGNED 2026-05-25 by Matt Nichol; Pass 1 + Pass 2 + Activation + post-Grok remediation landed; 905 / 905 pytest green, 1 skipped; §11.1 amendment 2026-05-25 added `rubric_status` for D12 sentinel + audit-marker contract.** Spec-first contract for a deterministic client-facing 5-axis explanation layer (`sender_identity`, `conversation_continuity`, `vendor_payment_history`, `document_integrity`, `origin_timing`) that maps existing analysis evidence into a stable 0-10 rubric without replacing the internal 0-100 runtime score. Locks D1-D19, the 160-char explanation cap, report-only / monthly digest v1 surface, contradiction guard (high-risk lift + low-risk trim), rendering contract, gate-test plan, and the D12 unavailable failure sentinel.
- 4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md - **DRAFT (pre-§11) 2026-05-25.** Spec-first contract draft for the Part 1 body-language slice of the Callback Phishing / TOAD detection layer; pure deterministic detector matching `header_divergence_detector` / `prompt_injection_detector` shape; explicitly excludes Part 2 phone-number baselining (gated on Vendor Baseline Store enum revision). Locks D1-D10, the closed phrase-category vocabulary, lift-only invariant, default-OFF activation flag, mandatory out-of-band verification wording on hit, forward-compat `phone_number_assessment` slot for Part 2, and a 14-test §8 closure gate. §10 sub-questions still open and require the standard 7-axis stress-test discipline before §11 signature.
- audit_tools/grok_audit_runner.py - local one-off independent xAI/Grok auditor for spec-vs-code review; reads `XAI_API_KEY` from root `.env`, writes local-only reports to gitignored `audit_outputs/`.
- audit_tools/decision_audit_runner.py - local independent xAI/Grok decision-auditor for anti-drift governance; reads one operator-reviewed packet from `decision_audit_inputs/`, validates the locked six-section packet contract and secret/financial-data boundaries before network calls, writes reports to `audit_outputs/decision_audits/`, and fail-closes on blocking verdicts unless `--report-only` is explicitly used.
- audit_tools/pre_ship_audit.py - all-seeing pre-commit gatekeeper. Reads the current `git diff HEAD` + untracked files + all `§11 SIGNED` specs + the current direction from `PROJECT_HANDSHAKE.md` / `PROGRESS.md`, sends them to Grok with a senior-reviewer prompt, prints `VERDICT: SHIP | FIX_FIRST | STOP`, and writes the full report under `audit_outputs/pre_ship_audits/`. Exits zero on SHIP, non-zero on FIX_FIRST/STOP so it can act as a real gate; `--report-only` suppresses the blocking exit. This is the single check that runs before commit/push - it folds the code-audit and decision-audit patterns into one tool so the operator never has to re-issue ceremony phrases.

## Active Business Project Folders
- AI_Phishing_Simulation_Business/ - active NorthStar Inbox Shield / AI Phishing Essentials business-facing PoC and sample eval workspace.
- AI_Phishing_Simulation_Business/Inbox_Shield/README.md
- AI_Phishing_Simulation_Business/Inbox_Shield/inbox_shield_langgraph.py
- AI_Phishing_Simulation_Business/Inbox_Shield/run_against_folder.py
- AI_Phishing_Simulation_Business/Inbox_Shield/check_eval.py
- AI_Phishing_Simulation_Business/Inbox_Shield/samples/expected_results.csv

---

# 1. Business_Operations

## 1.1 Core Business Files
- AI_Phishing_Essentials_Offer_Sheet.md
- AI_Phishing_Essentials_Offer_Sheet_Notion_Export.md
- Add_Ons_Pricing.md
- Business_Operations_Batch_1_Printable.md
- Cold_Email_Sequence_AI_Phishing.md
- Discovery_Questionnaire.md
- FAQ_NorthStar_Security.md
- Landing_Page_Copy_NorthStar_Security.md
- LinkedIn_Outreach_Scripts.md
- Local_SMB_Target_List_Template.md
- Onboarding_Checklist.md
- Phishing_Simulation_Authorization.md
- README.md
- Renewal_Workflow.md
- Service_Menu.md
- Service_Menu_Notion_Export.md
- Services_Page_Copy_NorthStar_Security.md
- Simulation_Policy_Boundaries.md

## 1.2 Client_Documents
- Authorization_Scope_Template.md
- FILE 1 - Sample_Monthly_Report.md
- Inbox_Shield_Sample_Monthly_Report.md - current MSP-facing monthly review artifact for NorthStar Inbox Shield. Uses current scoring/reporting concepts (`risk_score`, `vendor_fraud_score`, `wire_transfer_anomaly_score`, `invoice_authenticity_score`, `recommended_action`, `behavioral_deviation_flags`, effective-parameter provenance, advisory action boundaries) and pairs with the generated Acme Effective Parameter Report demo.
- MSP_Discovery_Evidence_Package.md - single-file evidence bundle for sending to an MSP owner after a discovery call; bundles the real 40-case `grok-4` eval result (honest about the FAIL), the 5/5 vendor-invoice post-patch diagnostic recovery (with raw vf-001 LLM JSON inlined), the real generated Acme Effective Parameter Report demo, the seven runtime non-negotiables, the SMB tier menu, an honest "what this does NOT claim" section, and a free 30-day first-MSP-pilot offer with reciprocal commitments. Pairs with `REVENUE_MAP.md` Lane 3 and `MILESTONE_ARC.md` A9.
- Generated/Acme_Effective_Parameter_Report_Demo.md - generated MSP-facing Effective Parameter Report for fictional `acme-industries-demo`, produced by `python -m scripts.acme_effective_parameter_report_demo` through the real `tenant_override_operator report --format markdown --out ...` path.
- Generated/Inbox_Shield_Daily_Digest_Demo.md - generated MSP-facing five-email daily digest demo for fictional `acme-industries-demo`, produced by `python -m scripts.inbox_shield_daily_digest_demo` through the real Inbox Shield `ingest_email` -> `run_email_risk_scoring_cycle` -> `run_daily_digest_cycle` path with deterministic fake LLM clients.

## 1.3 Outreach Cold_Email_Sequence
- cold-email-4.md
- cold-email-breakup.md
- cold-email-bump-1.md
- cold-email-bump-2.md
- follow-up-opened-no-reply.md

## 1.4 Reports
- FILE 1 - Sample_Monthly_Report.md
- FILE 2 - Report_Cover_Page.md
- FILE 3 - Leadership_Summary_Template.md
- FILE 4 - Report_Notes_Internal.md
- FILE 5 - Evidence_Package_Cover.md

## 1.5 Website
- FILE 1 - landing-page.md
- FILE 2 - services-page.md
- FILE 3 - about-page.md

## 1.6 Lead_Generation
- README.md
- clutch_msp_canada_scraper.py
- saved_clutch_pages/
- output/

---

# 2. Delivery_Engine

## 2.1 Overview
- README.md

## 2.2 Phishing Simulations
Located in `Delivery_Engine/Phishing_Simulations`.

- Monthly_Campaign_Workflow.md
- Simulation_Execution_Checklist.md
- Tool_Stack_Notes.md

## 2.3 Campaign Examples
Located in `Delivery_Engine/Phishing_Simulations/Campaign_Examples`.

- Safe Phishing Template - Business
- Safe Phishing Template - Executive
- Safe Phishing Template - Invoice
- Safe Phishing Template - Password
- Safe Phishing Template - Training

## 2.4 Reporting
- Dashboard Guide
- Evidence Collection Guide
- Internal_Report_Notes.md
- Leadership_Evidence_Package.md
- Leadership_Summary.md
- Monthly Human-Risk Report
- NorthStar_Security_Report_Template.md
- Risk Scoring Model

## 2.5 Training
- Safe_Template_Business_Update.md
- Safe_Template_Executive_Request.md
- Safe_Template_Invoice_Review.md
- Safe_Template_Password_Expiry.md
- Safe_Template_Training_Confirmation.md

## 2.6 Micro Training Scripts
- Micro_Training_Click_Awareness.md
- Micro_Training_Executive_Impersonation.md
- Micro_Training_Link_Safety.md

---

# 3. SwarmCommand_Engine

## 3.1 Overview
- README.md

## 3.2 Experiments

### Detection_Sandbox
- FILE 1 - sandbox-overview.md
- FILE 2 - signal-library-experiments.md
- FILE 3 - prototype-detection-agent.md
- FILE 4 - sandbox-test-cases.md
- FILE 5 - experimental-findings-log.md

## 3.3 Agent_Loop_Runtime
- README.md
- NorthStar_Agent_Loop.md
- Blackboard_Engine/blackboard-loop.md
- Blackboard_Engine/blackboard-data-model.md
- Blackboard_Engine/python-blackboard-models.md
- Production_Swarm_Loop/production-swarm-loop.md
- Sandbox_Swarm_Loop/sandbox-swarm-loop.md
- Mutation_Engine/mutation-engine-loop.md
- Autonomous_Workflows/one-hour-agent-training-loop.md - spec-first protocol for bounded one-hour multi-agent training sessions with mission envelope, checkpoints, debate contract, forbidden actions, and stop conditions.
- Autonomous_Triggers/autonomous-defensive-triggers.md - spec-first trigger layer for threat-detected / project-drift defensive responses; starts training or audit loops, not production mutation.
- Autonomous_Orchestration/swarm-orchestrator-agent.md - spec-first master supervisor contract for trigger routing, execution-contract enforcement, drift monitoring, tenant slicing, and escalation.
- Autonomous_Orchestration/execution-contracts.md - mission-packet discipline layer for one-hour focus windows, task anchors, drift thresholds, retry/fallback, RBAC, tenant boundary, quotas, and kill-switch conditions.
- Autonomous_Orchestration/trigger-routing-table-per-tier.md - tier-aware routing table for Essentials, Plus, and Enterprise trigger dispatch.
- Autonomous_Orchestration/swarm-slice-descriptors.md - product-tier slice descriptors defining enabled agents, triggers, contract defaults, quotas, and overrides.
- Autonomous_Orchestration/agent-enablement-map-per-tier.md - canonical 60-agent enablement matrix across Essentials, Plus, and Enterprise.
- Policy_Pipeline/policy-promotion-pipeline.md
- Policy_Pipeline/policy-rollback-primitive.md
- Policy_Pipeline/policy-regression-alert-subscriber.md
- Policy_Pipeline/policy-regression-detector.md
- Policy_Pipeline/multi-tenant-isolation-hardening.md
- Policy_Pipeline/operator-kill-switch.md
- Policy_Pipeline/inbox-shield-llm-detection-bridge.md - bridge spec from business-facing LangGraph PoC to governed sandbox producer agent (`llm_detection_001`)
- Governance_Constitution/governance-constitution-loop.md
- Runtime_Implementation/implementation-roadmap.md
- Runtime_Implementation/core/blackboard/models.py - includes additive `EmailInboundPayload.received_headers` for preserving repeated `Received:` headers as a first-class list while keeping legacy `headers: dict[str, str]` intact.
- Runtime_Implementation/core/blackboard/storage.py
- Runtime_Implementation/core/orchestrator/registry.py
- Runtime_Implementation/core/orchestrator/routes.py
- Runtime_Implementation/core/orchestrator/tenants.py
- Runtime_Implementation/core/production/loop.py
- Runtime_Implementation/core/sandbox/loop.py
- Runtime_Implementation/core/mutation/engine.py - Phase 1.4: `select_mutation_kind`, `_BUCKET_E_MATCHING_AXIS`, per-cycle promotion cap, typed evidence chain
- Runtime_Implementation/core/production_state/parameter_keys.py - `RESERVED_PARAMETER_KEYS` frozenset + `unauthorized_parameter_keys` helper (Phase 1.4 §11 Decision 2)
- Runtime_Implementation/core/production_state/tenant_overrides.py - Phase 2.1 per-tenant override module: local JSON current-state files, append-only audit JSONL events, write-time validation, expiry/status handling, effective-parameter resolver.
- Runtime_Implementation/core/production_state/effective_parameters_report.py - Phase 2.1 evidence visibility builder: read-only signed baseline vs tenant override vs effective-value report with per-parameter provenance and recent audit events.
- Runtime_Implementation/core/production_state/tenant_override_operator.py - Phase 2.1 operator CLI (`python -m core.production_state.tenant_override_operator`): create, pause, revoke, effective, report, audit, show; operator-only (not imported by loops).
- Runtime_Implementation/core/production_state/vendor_baseline/ - Vendor Baseline Store primitive: per-tenant SQLite baseline, hash-only storage, TTL cleanup, constant-time live hash comparison, tenant path isolation, Windows/POSIX file hardening, and Blackboard audit writes. Grok-audited 2026-05-24 with final verdict `approve with notes`.
- Runtime_Implementation/scripts/__init__.py - Operator-tooling package marker; forbidden from being imported by agents or production / sandbox loops.
- Runtime_Implementation/scripts/project_trigger_scan.py - Autonomous defensive trigger scanner v1 (read-only, offline). Compares workspace tracking + provided baseline against expectations, emits §6 trigger packets with full forbidden-action list and `requires_operator_approval=true`, optionally produces a §5 one-hour mission envelope. CLI: `python -m scripts.project_trigger_scan --baseline-tests N [--with-mission-envelope]`.
- Runtime_Implementation/scripts/acme_effective_parameter_report_demo.py - deterministic operator-side generator for the fictional `acme-industries-demo` Effective Parameter Report. Seeds an isolated demo blackboard under `Runtime_Implementation/demo_outputs/`, writes demo signed policy state, creates real override audit events through the existing per-tenant override API, and invokes `tenant_override_operator report --format markdown --out` to produce `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md`.
- Runtime_Implementation/scripts/cisa_kev_ingest.py - operator-run CISA KEV threat-intel ingestion v0 (first half of MILESTONE C1). Pulls the CISA Known Exploited Vulnerabilities catalog (live HTTPS or local `--source-file` for offline), filters for SMB-relevant entries (default = `knownRansomwareCampaignUse == "Known"`; optional `--vendor-allowlist default` enables the built-in SMB vendor list), renders entries in the locked `THREAT_INTEL_LOG.md` format, and (only with `--append`) inserts them above the `## Empty Intake Queue` marker. Dry-run by default; CVE-ID duplicate suppression against existing log headers; writes nothing to production_state / tenant overrides / Blackboard / policy pipeline.
- Runtime_Implementation/scripts/inbox_shield_daily_digest_demo.py - deterministic operator-side generator for the fictional `acme-industries-demo` Inbox Shield daily digest. Seeds five demo emails into an isolated demo blackboard, runs the real ingest -> score -> digest runtime path with fake LLM clients, and writes `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md`. No live mailbox, no live LLM, no email send, no production_state / tenant override / policy-pipeline writes.
- Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md - Phase 1.5 full `grok-4` rerun diagnostic report: 36/40 overall, 100% fraud precision, 0% legit FPR, **FAIL** on vendor_invoice_fraud recall (40% vs required 60%).
- Runtime_Implementation/core/policy/signing.py
- Runtime_Implementation/core/policy/pipeline.py
- Runtime_Implementation/core/policy/rollback.py
- Runtime_Implementation/core/production_state/state.py
- Runtime_Implementation/core/production_state/gate.py
- Runtime_Implementation/core/production/policy_consumer.py
- Runtime_Implementation/core/production/alert_subscriber.py
- Runtime_Implementation/core/production/regression_detector.py
- Runtime_Implementation/core/operator_state/state.py
- Runtime_Implementation/core/operator_state/gate.py
- Runtime_Implementation/core/operator_state/audit.py
- Runtime_Implementation/core/ingest/email_ingest_agent.py
- Runtime_Implementation/core/scoring/email_risk_scoring_agent.py - NorthStar Inbox Shield scoring agent and locked prompt; includes Phase 1.5 vendor-invoice recall floor after the 2026-05-22 rerun failed vendor_invoice_fraud recall.
- Runtime_Implementation/core/scoring/email_authentication_detector.py - pure SPF/DKIM/DMARC ingestion detector for gateway `Authentication-Results` headers; no DNS, no crypto, no network. Produces lift-only auth-failure signals consumed by the scoring overlay for MEDIUM/HIGH profiles while LOW skips the check.
- Runtime_Implementation/core/scoring/received_chain_parser.py - foundation-only parser for preserved `Received:` header chains. Extracts sanitized from-host / by-host / IP metadata into frozen dataclasses; no scoring, no GeoIP/ASN/DNS lookup, no baseline write, and no raw-header emission.
- Runtime_Implementation/core/scoring/document_metadata_detector.py - metadata-only Document Metadata Fingerprinting v1 detector; reads bounded `EmailAttachmentMeta.pdf_metadata` Producer/Creator strings, compares against Vendor Baseline Store `pdf_producer_fingerprint` signals (check-then-ingest), and overlays lift-only document-integrity floors in the scoring agent (LOW skips, MEDIUM floor 75, HIGH +10 cap 95). No PDF byte parsing, OCR, or network in v1.
- Runtime_Implementation/core/scoring/prompt_injection_detector.py - Adversarial Prompt-Injection Detector v1; pure-function deterministic scanner over `EmailInboundPayload.body_plain` and `EmailAttachmentMeta.extracted_text` against five closed families (instruction_marker, override_imperative, role_impersonation, output_control, hidden_text). Returns lift-only family tags only (no raw substrings). Overlay applies LOW skip / MEDIUM floor / HIGH +10 cap 95.
- Runtime_Implementation/core/workflows/__init__.py - public surface for the workflow/audit primitives package (v1 contains Two-Channel Confirmation Enforcement).
- Runtime_Implementation/core/workflows/two_channel_confirmation.py - Stage-A Two-Channel Confirmation Enforcement workflow; appends `pending` and `outcome` events of `RecordType.TWO_CHANNEL_CONFIRMATION` to the per-tenant Blackboard, enforces append-only / no-whitewashing / closed-enum / kill-switch / data-minimization invariants, and lists pending confirmations for the daily digest. No scoring effect (lift-only audit trail).
- Runtime_Implementation/core/scoring/financial_state_ledger.py - Financial State Ledger / Delta Tripwire detector; extracts labelled payment-destination signals, checks Vendor Baseline Store before ingesting, returns redacted/hash-only frozen dataclass assessment, and recommends risk floor 85 + out-of-band verification on `new` / `expired` signals.
- Runtime_Implementation/core/scoring/eval/__init__.py
- Runtime_Implementation/core/scoring/eval/dataset.py
- Runtime_Implementation/core/scoring/eval/runner.py - eval runner + EvalReport with pass-gate properties (precision >= 80%, FPR <= 10%, per-fraud-subcategory recall >= 60%) and pass-gate-aware markdown table
- Runtime_Implementation/core/scoring/eval/fraud_eval_harness.py - CLI entry point with --provider {anthropic,openai}, --model, --api-key-env, --llm-safe / --no-llm-safe, --allow-unsafe-dataset-path, --usage-log, --report-out, --dry-run
- Runtime_Implementation/core/scoring/eval/fraud_eval_dataset.jsonl
- Runtime_Implementation/core/scoring/eval/llm_safety.py - workflow plan §C runtime: UNSAFE_PATTERNS (synced with the two shell scanners), dataset path allowlist, dataset content scan, sha256 usage log, build_llm_safe_client wrapper that enforces the locked NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT prefix
- Runtime_Implementation/core/scoring/eval/live_client.py - lazy-imported Anthropic / OpenAI client builders matching the harness LLMClient contract; strips markdown code fences from responses
- Runtime_Implementation/core/precursor/__init__.py - Month 3 Phase 1.2 ransomware precursor detection module bootstrap + re-exports
- Runtime_Implementation/core/precursor/attachment_classifier.py - sandbox-safe static attachment classifier + `AttachmentInspector` for the ingest hook + per-attachment ransomware risk scorer
- Runtime_Implementation/core/precursor/url_obfuscation_detector.py - URL parser + obfuscation scorer (punycode / homoglyph / shortener / credential-bearing / suspicious-TLD / IP-host / login-path)
- Runtime_Implementation/core/precursor/body_signal_detector.py - body-language credential-harvest + MFA-fatigue scorer
- Runtime_Implementation/core/precursor/analysis.py - overlay builder that combines the three detectors into `EmailAnalysisRansomwarePrecursorAnalysis` + a recommended `risk_score` floor for the scoring agent
- Runtime_Implementation/core/sandbox/red_agents/__init__.py - Month 4 Phase 1.3 Red profile module bootstrap; exposes `RED_PROFILE_MODULES` tuple
- Runtime_Implementation/core/sandbox/red_agents/_seed_data.py - shared constant tables (vendor names, sender-domain variants, dollar bands, urgency phrases, attachment kinds, URL hosts) - all identifiers in the reserved `.example` / `.test` / `.invalid` namespace
- Runtime_Implementation/core/sandbox/red_agents/fake_invoice_red.py - `fake_invoice_red_001` generator (100 cases per battery; 10 vendors × 5 sender-domain variants × 2 urgency tiers)
- Runtime_Implementation/core/sandbox/red_agents/vendor_update_red.py - `vendor_update_red_001` generator (128 cases; 8 vendors × 4 update patterns × 4 stylistic variants)
- Runtime_Implementation/core/sandbox/red_agents/malicious_attachment_red.py - `malicious_attachment_red_001` generator (112 cases; 7 attachment kinds × 8 sender variants × 2 body variants)
- Runtime_Implementation/core/sandbox/red_agents/obfuscated_url_red.py - `obfuscated_url_red_001` generator (108 cases; 6 URL obfuscation kinds × 9 path fragments × 2 body variants)
- Runtime_Implementation/core/sandbox/red_agents/bucket_e_probes.py - four Bucket E mirror cases (`vf-002`, `vf-005`, `ei-005`, `wt-004`) tagged `bucket_e_regression_probe` per Matt's §11 decision 5
- Runtime_Implementation/core/sandbox/red_battery.py - `run_red_battery_cycle(...)` entry point: kill-switch boundary, per-profile loop, in-memory Blue invocation via `score_one_email_payload`, per-case `MUTANT_EVALUATION` + `AUDIT_VERDICT`, per-profile aggregated `WEAKNESS_REPORT` with bucket-counted failure-mode summary
- Runtime_Implementation/core/drafting/daily_digest_agent.py
- Runtime_Implementation/tests/test_blackboard_models.py
- Runtime_Implementation/tests/test_mutation_engine.py
- Runtime_Implementation/tests/test_orchestrator_routes.py
- Runtime_Implementation/tests/test_production_loop.py
- Runtime_Implementation/tests/test_sandbox_loop.py
- Runtime_Implementation/tests/test_policy_pipeline.py
- Runtime_Implementation/tests/test_policy_rollback.py
- Runtime_Implementation/tests/test_production_state.py
- Runtime_Implementation/tests/test_production_loop_integration.py
- Runtime_Implementation/tests/test_alert_subscriber.py
- Runtime_Implementation/tests/test_regression_detector.py
- Runtime_Implementation/tests/test_operator_kill_switch.py
- Runtime_Implementation/tests/test_kill_switch_loop_integration.py
- Runtime_Implementation/tests/test_kill_switch_e2e.py
- Runtime_Implementation/tests/test_multi_tenant_isolation.py
- Runtime_Implementation/tests/test_email_analysis_record.py
- Runtime_Implementation/tests/test_email_risk_scoring_agent.py - Inbox Shield scoring-agent test suite, including prompt lock, Phase 1.5 vendor-invoice recall floor pin, and scoring-loop persistence coverage.
- Runtime_Implementation/tests/test_financial_state_ledger.py - §7 gate suite for Financial State Ledger / Delta Tripwire; 28 tests covering extraction, baseline states, check-before-ingest, data minimization, kill-switch inheritance, tenant isolation, overlay merge, and audit-target wiring.
- Runtime_Implementation/tests/test_daily_digest_agent.py
- Runtime_Implementation/tests/test_email_ingest_agent.py
- Runtime_Implementation/tests/test_e2e_inbox_shield_smoke.py
- Runtime_Implementation/tests/test_fraud_eval_harness.py
- Runtime_Implementation/tests/test_ransomware_precursor.py - Month 3 Phase 1.2 test suite (27 tests: schema-delta, attachment classifier, URL detector, body-language detector, overlay builder, scoring-agent integration, **Month 3 gate** synthetic ransomware-precursor email scoring >=85, floor-direction protection, and overlay opt-out)
- Runtime_Implementation/tests/test_phase_1_3_sandbox_training_pit.py - Month 4 Phase 1.3 test suite (38 tests: schema delta for the new `SyntheticEmailAttackCasePayload` + `Phase13FailureMode` 8-value `Literal` + `Phase13CaseTag` + `Phase13CaseArchetype`; reserved-namespace sender / recipient validator pins; in-memory `score_one_email_payload` helper success / failure / overlay-disabled paths; per-Red-profile >=100 cases + byte-determinism + per-archetype enum-coverage drift catchers; Bucket E mirror tags + distribution; **all seven §7 gate tests** — full per-profile record signature, typed eight-mode failure taxonomy with `dynamic_detail` split, byte-deterministic generation, sandbox kill-switch abort, sandbox-only environment, no `POLICY_UPDATE` emission, `WeaknessReportPayload.raw_tenant_data_removed=True`)
- Runtime_Implementation/tests/test_phase_1_4_mutation_engine_specialization.py - Month 5 Phase 1.4 test suite (22 tests: `MutationKind` Literal drift; `RESERVED_PARAMETER_KEYS` dual-boundary enforcement; `select_mutation_kind` routing for all three new kinds + hard non-selection modes; signed `POLICY_UPDATE` typed parameter keys; Month 2 byte-identity-at-v0 regression; fraud-lift gating; **all seven §7 gate tests** including close-the-loop end-to-end; per-cycle cap=3; matching-axis Bucket E relaxation; evidence chain shape; sandbox-only promotion; legacy Month 0 fallback)
- Runtime_Implementation/tests/test_tenant_parameter_overrides.py - Month 6 Phase 2.1 test suite (15 tests: exposed-key drift, local JSON + append-only audit, update audit, write-time rejection/no silent clamp, separate requester/approver, tenant isolation, expiry/revoked/invalid fallback auditing, no-override byte-identity to policy state, and production-loop scoring effect).
- Runtime_Implementation/tests/test_tenant_override_operator_cli.py - Month 6 operator CLI test suite (9 tests: create/pause/revoke, effective review, audit listing, show, governance errors).
- Runtime_Implementation/tests/test_effective_parameters_report.py - Month 6 evidence visibility test suite (18 tests: report builder provenance, no-override fallback, expired/invalid handling, Markdown/JSON CLI report, payload validation, route append).
- Runtime_Implementation/tests/test_project_trigger_scan.py - Autonomous trigger scanner test suite (10 tests: clean scan, baseline drift, missing PROGRESS.md, blocked / approval-gated PROGRESS.md accepted as current work, handshake-vs-MASTER_INDEX drift, missing tracking files, full forbidden-action list on every packet, one-hour mission envelope construction, JSON CLI write, mission-envelope CLI write).
- Runtime_Implementation/tests/test_acme_effective_parameter_report_demo.py - Acme Effective Parameter Report demo test (1 test): generator writes a real markdown report through the CLI path, preserves expected provenance rows, writes two deterministic override audit events, and marks the override as applied.
- Runtime_Implementation/tests/test_cisa_kev_ingest.py - CISA KEV threat-intel ingestion test suite (19 tests): load from file, filter default ransomware-only, filter without ransomware filter, filter with default SMB vendor allowlist, filter with explicit case-insensitive allowlist, drop missing-CVE entries, build_log_entry locked-field coverage (ransomware + non-ransomware pattern class), render_entries separator + empty-list behavior, existing_cve_ids level-3-header scoping, append inserts above queue marker, append raises on missing marker, append no-op on empty block, CLI dry-run summary + body without write, CLI append with `--limit`, CLI append skips duplicates, CLI `--out` preview file, CLI `--no-ransomware-only --vendor-allowlist default`.
- Runtime_Implementation/tests/test_inbox_shield_daily_digest_demo.py - Inbox Shield daily digest demo test suite (7 tests): locked five-email scenario, deterministic scoring client routing, deterministic digest renderer sections, generated artifact content, runtime record counts, non-demo blackboard deletion guard, and CLI summary.

## 3.4 Future_Platform_Agents
- FILE 1 - future-platform-overview.md
- FILE 2 - agent-roles-master-list.md
- FILE 3 - agent-design-template.md
- FILE 4 - agent-collaboration-map.md
- FILE 5 - future-roadmap-notes.md

## 3.5 Drafting_Agents
Located in `SwarmCommand_Engine/Agents/Drafting_Agents`.

- drafting-agents-overview.md
- monthly-report-drafting-agent.md
- leadership-summary-drafting-agent.md
- training-script-drafting-agent.md
- template-drafting-agent.md
- executive-briefing-drafting-agent.md

## 3.6 Scoring_Agents
- department-risk-scoring-agent.md
- email-risk-scoring-agent.md
- insurance-evidence-scoring-agent.md
- repeat-clicker-scoring-agent.md
- trend-scoring-agent.md

## 3.7 Workflow_Agents
- campaign-optimizer-agent.md
- evidence-packaging-agent.md
- report-assembly-agent.md
- simulation-scheduler-agent.md
- template-selector-agent.md
- training-delivery-agent.md

## 3.8 Workflows
- FILE 1 - workflow-overview.md
- FILE 2 - workflow-monthly-simulation.md
- FILE 3 - workflow-training-delivery.md
- FILE 4 - workflow-monthly-reporting.md
- FILE 5 - workflow-evidence-package.md
- FILE 6 - workflow-optimization-cycle.md

---

# 4. Product_Roadmap

## 4.1 Overview
- README.md

## 4.2 Architecture_Diagrams
- FILE 1 - northstar-system-architecture.md
- FILE 2 - swarmcommand-high-level-architecture.md
- FILE 3 - data-flow-architecture.md
- FILE 4 - future-platform-architecture.md
- FILE 5 - integration-architecture.md

## 4.3 Roadmap Docs
- `12_Week_Timeline.md` - 12-week build timeline (annotated with current status of each item).
- `Fraud_Ransomware_Specialization_Roadmap.md` - Strategic specialization roadmap (Fraud Detection + Ransomware Defense). Four phases: Foundation, Capability Expansion, Market Positioning, Monetization & Scale. Approved 2026-05-20.
- `12_Month_Specialization_Roadmap.md` - Operational unfold of the strategic specialization into a month-by-month build + GTM plan (June 2026 - May 2027). One gate per month, four quarterly checkpoints. Approved 2026-05-20.
- `Phase_1_1_Fraud_Prevention_Deep_Dive.md` - Phase 1.1 implementation contract for Month 2. Sections: fraud signal taxonomy (6 archetypes), four new EmailAnalysisRiskAnalysis scoring dimensions with rubrics, worked examples for the NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT rewrite, eval harness design + 80%-precision / 10%-FPR gate, explicit out-of-scope boundary, strategic agent-evolution section (fitness model + swarm evolution engine + identity persistence), and the Month 2 implementation contract. Closes the Month 1 gate of the 12-month roadmap. Authored 2026-05-20.
- `Live_LLM_Eval_Runbook.md` - operator-facing handoff for the Phase 1.1 live LLM eval pass-gate run. Covers prerequisites, pre-flight checklist, anthropic + openai invocation, pass-gate criteria (>=80% precision on fraud / <=10% FPR on legit / >=60% per-fraud-subcategory recall), activity-log entry template, failure-mode table, and bypass-surface guidance. Authored 2026-05-20.
- `Phase_1_1_Eval_Dataset_Design_Grid.md` - Month 2 eval dataset design pass. Defines all 40 eval case slots (20 fraud / 20 legit), with per-case patterns, expected flags, score bounds, and generation notes. The Unicode-obfuscation schema gap it surfaced is resolved via `unusual_unicode_obfuscation`; the full JSONL dataset is generated at `Runtime_Implementation/core/scoring/eval/fraud_eval_dataset.jsonl`.
- `Month_1_Closeout_Readiness.md` - Month 1 closeout checkpoint. Lists all five Month 1 deliverables, source files, evidence, the dedicated five-email E2E gate test, 196-test baseline, explicit boundaries, and conditions to confirm before any next-phase runtime work.
- `Month_2_Closeout_Readiness.md` - Month 2 closeout checkpoint. Records the §4.5 pass-gate verdict (PASS on `grok-4`, 36/40, 100% fraud precision, 0% legit FPR, all six fraud subcategories >=60% recall), durable report path, list of remaining Bucket E honest gaps, and conditions to confirm before starting Month 3 runtime work.
- `Phase_1_2_Ransomware_Precursor_Deep_Dive.md` - Phase 1.2 implementation contract for Month 3. Sections: threat coverage (attachments / URLs / credential harvest / MFA fatigue), schema delta (`PrecursorIndicator` 17-value `Literal` + `EmailAnalysisRansomwarePrecursorAnalysis` block), detector architecture under `core/precursor/`, hard sandbox-safe boundary (no execution / no DNS / no fetch), sub-score bands, scoring-agent overlay design with one-directional `risk_score` floor, explicit out-of-scope deferrals, Month 3 gate verification (deterministic synthetic-email test passes), and Month 3 implementation receipt (files changed + 359-test baseline).
- `Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md` - **§11 LOCKED 2026-05-21 by Matt; implementation landed; 397 / 397 pytest green.** Phase 1.3 implementation contract for Month 4 (fraud-specialised Red agents). Sections: four Red profile roles tied one-to-one to the Phase 1.1 / 1.2 signal axes (`fake_invoice_red_001`, `vendor_update_red_001`, `malicious_attachment_red_001`, `obfuscated_url_red_001`), synthetic-scenario generation boundaries (deterministic + parametric + RFC-2606/6761 namespace only + no real customer data + sandbox-safe), evaluation-only sandbox rules (multi-tenant isolation + kill-switch boundary inheritance), new `SyntheticEmailAttackCasePayload` + `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE` schema delta, Red-vs-Blue expected Blackboard record chain (case -> analysis -> mutant evaluation -> audit -> per-profile weakness report), Blue-agent evaluation contract (production scoring agent + Phase 1.2 overlay run against deterministic fake LLM client via the new in-memory `score_one_email_payload(...)` helper; required-subset semantics; eight-mode failure taxonomy with `dynamic_detail` stored separately on `Phase13FailureDetail`), promotion boundary (no direct policy emission; Phase 1.3 produces weakness-report evidence, Month 5 mutation engine consumes), Month 4 gate criteria (7 gate tests + 31 supporting tests, >=100 cases per profile, byte-determinism, enum-coverage drift catchers, sandbox-isolation negatives, policy-update negative), out-of-scope deferrals, §9 implementation receipt with full file table, and §11 five-decision lockdown summary.
- `Month_4_Closeout_Readiness.md` - Month 4 closeout checkpoint. Documents the §11-decisions landing per row (each test-pinned), six-deliverable receipt (schema delta / route + registry / in-memory helper / four Red profiles / Bucket E mirrors / Red battery cycle), sandbox-safety boundary five-layer verification, promotion-boundary confirmation (no `POLICY_UPDATE` writes), and the conditions for starting Month 5 (mutation engine + promotion pipeline).
- `Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md` - **§11 LOCKED 2026-05-21 by Matt; implementation landed; 419 / 419 pytest green.** Phase 1.4 implementation contract for Month 5 (mutation-engine specialisation). Sections: §1 three fraud-specialised `MutationKind` values; §2 mutation-selection boundary (`select_mutation_kind` + matching-axis Bucket E floor relaxation); §3 per-kind parameter contracts (`RESERVED_PARAMETER_KEYS` enforced at BOTH promotion pipeline and Guardrail 11 gate per Matt's Decision 2 tightening); §4 production consumer wiring (three read sites landed); §5 mutation engine updates (Literal, expanded config, per-cycle cap=3, evidence chain cap=20); §6 promotion boundary unchanged except dual-boundary parameter-key checks; §7 Month 5 gate criteria (22 tests, all seven gate tests green including close-the-loop end-to-end); §8 out-of-scope deferrals; §9 implementation receipt LANDED; §11 five-decision lockdown summary with two Matt-side tightenings documented.
- `Month_5_Closeout_Readiness.md` - Month 5 closeout checkpoint. Documents the §11-decisions landing per row (each test-pinned, including Decision 2 dual-boundary and Decision 4 matching-axis tightening), five-deliverable receipt, sandbox-to-production loop closed by `test_close_the_loop_red_battery_to_next_cycle_effect`, Month 2 PASS-gate byte-identity protection, and conditions for starting Month 6 (Phase 2.1 product sheet + per-tenant overrides).
- `Phase_2_1_Fraud_Detection_Product_Sheet_And_Tenant_Overrides.md` - **§11 LOCKED 2026-05-21 by Matt; implementation + operator CLI + evidence visibility landed; 461 / 461 pytest green.** Month 6 Phase 2.1 contract. Covers the fraud-detection product-sheet claim boundary, approved proof points from the Month 2 `grok-4` PASS gate and Month 5 closed mutation loop, the per-tenant parameter override problem, policy-baseline-plus-operator-overlay model, override schema, guardrails, audit trail, safe default behavior, evidence-report visibility, implementation receipt, gate criteria, and locked §11 decisions: local JSON per tenant + append-only audit, write-time rejection, optional expiry, separate requester/approver, and only the three Phase 1.4 lift keys exposed.
- `Vendor_Baseline_Store_Deep_Dive.md` - **§11 SIGNED 2026-05-23 by Matt; implementation landed 2026-05-24; 587 / 587 pytest green.** Spec-first contract for the per-tenant, hash-only, TTL-bounded Vendor Baseline Store. Locks SQLite per-tenant files, HKDF-derived per-tenant salt, 90-day TTL default, closed signal-type enum, cross-platform file isolation (POSIX chmod on Linux + pywin32 DACL on Windows), isolation-manager connection scoping, three-function public API, Guardrail 11 / 12 integration, and a §7 closure gate.
- `Product_Sheets/Fraud_Detection_Product_Sheet.md` - Customer-facing v1 product sheet for NorthStar Inbox Shield fraud detection. Plain-English offer for SMB / MSP buyers, current-runtime capabilities, explicit non-goals (no blocking / quarantine / remediation / portal in MVP), proof points, MSP positioning, recommended first package, discovery questions, and safe claim boundary.
- `Month_6_Closeout_Readiness.md` - Month 6 closeout checkpoint. Documents the product sheet, per-tenant override implementation, operator CLI workflow, evidence visibility report, five §11 decisions test-pinned, runtime deliverables, **461-test verification**, **Q2 (Months 4–6) HIT 3/3**, held boundary, and likely next phase options.
- `Tenant_Override_Operator_Runbook.md` - Operator command reference for `tenant_override_operator` CLI (create, pause, revoke, effective, report, audit, show).
- `Q1_Checkpoint_2026.md` - Q1 (Months 1-3) and Q2 (Months 4-6) checkpoint document. Records Q1 gate outcomes (HIT / HIT / HIT), **Q2 gate outcomes (HIT / HIT / HIT as of 2026-05-21)**, cumulative runtime surfaces shipped, eval + harness coverage, test counts, documentation status, intentionally-deferred scope, four Bucket E honest gaps, and a drift-check note that work shipped ahead of the conservative calendar.
- `NorthStar_MVP_Dashboard_Design.md` - MVP dashboard design specification for Inbox Shield reporting. Covers current-runtime scope, explicit non-goals, schema field mapping, executive summary, risk metrics, fraud categories, risk signals, recommendations, evidence status, trend view, leadership summary, operator notes, role-specific views, and future enhancements.
- `Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` - **§11 SIGNED 2026-05-24 by Matt; implementation landed; 621 / 621 pytest green; Grok audit approved.** Contract and receipt for the first detector built on Vendor Baseline Store: extracts labelled payment-destination signals from email body / attachment text, checks baseline before ingesting, flags `new` or `expired` routing / SWIFT / IBAN / account / payment-portal signals, recommends `needs_review` with mandatory out-of-band verification, and forbids raw financial values in returned findings. Runtime implementation: `core/scoring/financial_state_ledger.py`; tests: `tests/test_financial_state_ledger.py`; Grok audit report: `audit_outputs/financial_state_ledger_grok_audit_20260524T224143Z.md` (verdict: approve).
- `Tiered_Detection_Intensity_Deep_Dive.md` - **§11 SIGNED 2026-05-24 by Matt; implementation landed; 658 / 658 pytest green; Grok audit approved.** Spec-first contract and receipt for the Low / Medium / High Security Profile policy system. Locks the three-tier closed enum, default = MEDIUM, the five-detector v1 `DetectorIdentity` enum that mirrors the existing scoring-agent overlay, MEDIUM-tier minimum for Financial State Ledger, the four-trigger v1 `ForcedEscalationTrigger` enum (LLM ≥ 80, header divergence ≥ 80, ghost thread > 0, manual operator escalation), the lift-only invariant for both forced escalation and per-tenant add-ons, the sales-plan default mapping (Essentials → LOW, Plus → MEDIUM, Enterprise → HIGH; Option C), per-tenant state at `blackboard_root/operator_state/security_profiles/<tenant>.json` (Guardrail 12 separation), audit-row emission on every profile change, kill-switch precedence preserved, backward compatibility with `enable_ransomware_precursor_overlay=False`, analysis + daily-digest profile metadata, malformed JSON -> `GovernanceError`, and a 36-test implementation gate including cost-monotonicity / cost-ceiling-under-escalation pins. Runtime implementation: `core/operator_state/security_profile.py` + scoring-agent/daily-digest integration; tests: `tests/test_security_profile.py`; Grok audit report: `audit_outputs/tiered_detection_intensity_grok_audit_20260525T001951Z.md` (verdict: approve).
- `Independent_Decision_Auditor_Deep_Dive.md` - **§11 SIGNED 2026-05-24 by Matt Nichol; implementation landed; 688 / 688 pytest green, 1 skipped; first self-audit verdict `proceed`.** Spec-first contract and receipt for the anti-drift decision-auditor lane. Defines when major recommendations require a second-model decision audit (next build lane, new §11 specs for subsystems/state surfaces, Guardrail 8-12 changes, data-egress decisions, persistent-state surfaces, gold-plating vs necessary-quality calls, and explicit Matt requests), a Markdown decision-packet format under `decision_audit_inputs/`, local reports under `audit_outputs/decision_audits/`, a closed verdict enum (`proceed`, `proceed_with_notes`, `revise_before_proceeding`, `defer`, `operator_decision_required`), fail-closed handling for blocking verdicts, operator override rules, data-minimization boundaries, and a 20-test §7 closure gate. Runtime implementation: `audit_tools/decision_audit_runner.py`; template: `decision_audit_inputs/TEMPLATE.md`; first packet: `decision_audit_inputs/20260524_1741_decision_auditor_next.md`; first report: `audit_outputs/decision_audits/20260524_1741_decision_auditor_next_decision_audit_20260525T004700Z.md`.
- `_SPARK_Bibles_Concept_Capture.md` - **SPARK only — pre-spec, unsigned, not §11.** Late-night idea-preservation file capturing Matt's 2026-05-24 / 2026-05-25 thinking on two future bibles: Shield Bible (outward-facing client identity / trust covenant) and Agent Bible (inward-facing internal constitution / system-prompt anchor). Records the Layer 1 (moral principles) + Layer 2 (operational commands) split, candidate fragments (not endorsed), tonal hazards, and explicit trigger conditions for un-deferring. Held, not buried — do not promote without Matt's lead. Cross-referenced from `PROJECT_HANDSHAKE.md` 2026-05-25 bibles deferral entry.
- `External_Model_Brief_Template.md` - **DRAFT (pre-§11) authored 2026-05-27 by Matt Nichol.** Trust-gate / anti-sycophancy doctrine and paste-and-go template for talking to external cloud LLMs (Gemini, Perplexity, ChatGPT, Claude.ai, future additions) about NorthStar without sycophancy drift, hallucinated project facts, or data-hygiene breaches. Locks D1-D10 covering external-model role (advisory consultants, not approvers), trust-gate primacy (the §3 ruleset is non-negotiable), inherits the Compliance_and_Trend_Watch_Process.md §1.1 advisory supersession extended to external models, data-hygiene boundary (no client-identifying data, no raw emails/headers from production tenants, no `production_state/`, no `1. Business_Operations/Client_Documents/`, no Financial State Ledger, no Vendor Baseline Store, no secrets), agreement-by-default forbidden, confidence labels required on substantive claims, knowledge-cutoff disclosure required, push-back-on-premise duty, no proxy decisions, paste-and-go (not auto-injected). Includes a load-bearing 10-rule trust-gate ruleset (§3), a paste-and-go project-context block (§4), two role blocks (deep research for Gemini/Perplexity, strategic reasoning / second-opinion for ChatGPT/Claude.ai), an output contract requiring "opening / body with confidence labels / options / what-I-might-be-missing" shape, and eight named external-model-specific failure modes (sycophancy by default, plausible hallucination, knowledge-cutoff extrapolation, data leakage to cloud LLMs, authority drift via the back door, premise laundering, doctrine bypass via external model, code-as-back-door). §10 holds six open questions for operator resolution before §11 sign-off (template structure one-file vs per-model, whether Grok prompts adopt §3 verbatim, logging persistence, additional forbidden topics, stronger data-hygiene mitigation beyond prompt warning, external-model output review cadence).
- `Next_Action_Decision_Rubric_Deep_Dive.md` - **DRAFT (pre-§11) authored 2026-05-27 by Matt Nichol.** Tactical-layer scoring rubric for ranking 3-7 next-action candidates inside an active session. Distinct from `think_sheet.md` (strategic / idea-level) and `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (buyer-facing / email-level). Five axes (`leverage`, `risk_reduction`, `evidence_strength`, `future_cost` inverted, `reversibility`), 0-2 each, max 10. 10-step decision loop (OBSERVE → GENERATE → SCORE → RANK → PRESENT → HUMAN DECISION → EXECUTE → AUDIT → LOG → UPDATE SIGNALS) with hard rules forbidding multi-action execution, step-skipping, mid-cycle structural changes, and autonomous rule mutation. Locks D1-D12 covering authority model (rubric ranks, human decides), naming (canonical name forbids "5-axis rubric" label to avoid collision), calibration scope (mismatch-logging only), pre-execution expectation capture, operator override path, and forbidden self-modification. §10 holds seven open questions for operator resolution before §11 sign-off (option-source / queue relationship, mode formalization, cycle-log persistence, calibration cadence, Grok-audit boundary, compressed system-prompt build, "do nothing" scoring guidance). Inherits `Compliance_and_Trend_Watch_Process.md` §1.1 supersession (rubrics are advisory only).

Use this folder for:
- Q1-Q4 roadmap
- Feature backlog
- Platform evolution notes
- Launch plan
- Product assumptions

---

# 5. Clients

## 5.1 Overview
- clients-overview.md

## 5.2 Client_Template
- client-template-overview.md
- Onboarding/onboarding-checklist.md
- Notes/client-notes.md
- Reports/reports-readme.md
- Evidence/evidence-readme.md

## 5.3 Client Folders
- ClientName_01
- ClientName_02

Duplicate `Client_Template` for each new client.

---

# 6. Internal_Strategy

## 6.1 Overview
- internal-strategy-overview.md

## 6.2 Market_Research
- market-research-template.md

## 6.3 Positioning
- positioning-statement.md
- value-proposition-map.md

## 6.4 Pricing_Strategy
- pricing-model.md

## 6.5 Competitive_Intel
- competitive-landscape.md

## 6.6 Internal_Notes
- internal-decisions-log.md

## 6.7 LLM_Governance
- LLM_Usage_Policy.md - formal allowed / prohibited LLM uses, synthetic-data requirement, defensive framing, violations + escalation
- LLM_System_Prompt_Template.md - drop-in defensive security system prompt for any external LLM session used for NorthStar work
- LLM_Workflow_Integration_Plan.md - design pass tying the policy + prompt to the pre-commit hook, CI scanner, planned `--llm-safe` mode, and planned onboarding section
- Governance_Traceability_Summary.md - audit-facing matrix linking LLM governance claims to file paths, line numbers, and verification status

---

# 7. Admin

## 7.1 Overview
- admin-overview.md

## 7.2 Legal
- msa-template.md
- privacy-overview.md

## 7.3 Finance
- invoice-template.md
- financial-model.md

## 7.4 Branding
- brand-guidelines.md
- logo-usage.md
- Logo/

## 7.5 HR
- contractor-onboarding.md

## 7.6 Operations
- ops-playbook.md

---

# NorthStar Certification + Licensing + Partner Ecosystem

## Overview
- README.md
- MASTER_FRAMEWORK.md

## Certification Program
- Certification_Handbook.md
- Certification_Syllabus.md
- Full_Training_Curriculum.md
- Exam/Certification_Exam.md
- Exam/Certification_Exam_Answer_Key.md
- Badge_Certificate/Badge_And_Certificate_Text.md

## Licensing Program
- Licensee_Onboarding_Kit.md
- License_Agreement_Draft.md

## Partner Program
- Partner_Program_Handbook.md
- Sales_Deck/Partner_Sales_Deck_Outline.md

## Monetization and Portal
- Ecosystem_Monetization_Model.md
- Partner_Portal_Structure.md

---

# Internal_Tools

- README.md - install instructions for the pre-commit hook, false-positive policy, and pointer to the workflow integration plan
- precommit_llm_safety_hook.sh - local pre-commit scanner that blocks unsafe LLM-framing terms (mirrors `.github/workflows/llm_safety_check.yml`)

---

# GitHub Workflows

- .github/workflows/llm_safety_check.yml - CI-side LLM safety scan triggered on push/PR to `main`/`master` (mirrors `Internal_Tools/precommit_llm_safety_hook.sh`)
- .github/workflows/llm_governance_verification.yml - CI-side governance integrity check for required LLM governance files, sections, cross-references, and scanner synchronization

---

# How to Use This System

1. Start with `6. Internal_Strategy` to understand the venture.
2. Use `1. Business_Operations` for day-to-day sales, outreach, offers, and client-facing assets.
3. Use `2. Delivery_Engine` for simulations, training, and reporting.
4. Use `3. SwarmCommand_Engine` for automation, agent design, experiments, and future platform development.
5. Use `4. Product_Roadmap` to track product direction and architecture.
6. Use `5. Clients` to onboard and manage customers.
7. Use `7. Admin` for legal, finance, branding, HR, and operations.
8. Use `NorthStar Certification + Licensing + Partner Ecosystem` when building operator training, licensed delivery, and partner channels.

---

# Operating Standard

Only add new items if they directly support:
- one offer
- one buyer
- one outreach motion
- one delivery workflow
- first paying clients

This keeps the system focused on building revenue and repeatable delivery before expanding the platform.
