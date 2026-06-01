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
- REACTION_TIMING_TEST_LOG.md - durable timestamped ledger for every NorthStar reaction-timing test. Required by the `AGENTS.md` section 5 reaction-timing test documentation rule (added 2026-05-28). Captures Stage A time-to-detection, time-to-verification-request, time-to-verification-outcome, and time-to-case-closure with a closed verdict enum (`pass`, `partial`, `fail`, `blocked`) and explicit `null`-with-reason discipline. Internal evidence ledger only; not a service-level agreement, client-facing performance claim, or buyer-facing certification.
- PROJECT_AUDIT_REPORT_2026-05-20.md - latest runtime audit report after policy pipeline verification.
- PROGRESS.md - always-current weekly task tracker. Updated whenever a task closes.
- CURRENT_STATE_MAP.md - **operator-authored compressed snapshot of doctrines and open gaps that already exist as designed concepts across multiple specs but are not captured anywhere as a single one-line reference. Pre-spec, unsigned, not §11. Floor reference, not floor doctrine.** Prevents future sessions from re-litigating settled design (or re-discovering known gaps) by re-assembling them from scattered specs. Authored 2026-05-31 by Matt Nichol with two seed entries: (1) **Alert-fatigue doctrine** — NorthStar reduces operator fatigue by batching risk into daily digests, tiering detection intensity by tenant plan/posture, escalating only on conservative high-signal triggers, explaining findings through action-first evidence, and allowing per-tenant tuning; Stage A is decision-support and evidence, not a per-email alert stream — anchored across `core/drafting/daily_digest_agent.py`, `Tiered_Detection_Intensity_Deep_Dive.md`, `Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`, the per-tenant override CLI, and `VISION.md` Stage A framing. (2) **Open gap: verification workflow ergonomics for vendor-payment changes** — four-value enum sketch (`verified` / `unresolved` / `false-positive` / `follow-up-needed`) with evidence + retest linkage; operator-acknowledged open work, not on any current build queue. Entries are operator-authored prose captured verbatim; the file does not introduce D-decisions, new gates, or new requirements. If an entry ever conflicts with a §11-signed spec, the signed spec wins.
- VISION.md - long-arc product thesis (Stage A Analyze + Recommend → Stage B Auto-Defend Obvious / Escalate Ambiguous → Stage C Self-Evolving Defense Swarm) + seven non-negotiables + what we will / won't keep up on.
- MILESTONE_ARC.md - multi-year milestone tracker (Stage A / B / C engineering + revenue + documentation milestones, each with a "done when" criterion + stage-crossing watchlist).
- THREAT_INTEL_LOG.md - swarm-evolution log: every threat pattern ingested + policy update that resulted. Seeded with eight planned free intake sources and the Phase 1.5 vendor-invoice recall floor as first entry.
- Frontier_Intake_Log.md - operator-driven log capturing emerging AI / agent / threat patterns observed during periodic frontier intake reviews. Cadence rule (locked 2026-05-25): 0-1 candidates surfaced per review → defer recurring discipline; 2-3 → quarterly cadence; 4+ → monthly cadence. Review #1 surfaced 5 candidates → monthly cadence committed (refinement flag at 90-day mark). Discovery layer only; formal gating happens separately in `think_sheet.md`.
- THIRTY_DAY_PLAN.md - 2026-05-23 to 2026-06-22 revenue plan for turning Inbox Shield proof into first paid AI engineering work.
- think_sheet.md - scoring rubric + stress-test gate that ideas pass through before they're allowed to touch the project plan.
- 4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md - operator-facing MSP discovery runbook for the Cyber Insurance Evidence Package D10 cheaper-proof gate; defines the 2-of-3 relevant-MSP conversation go bar, named SMB + named insurance/underwriting anchor requirement, call guide, privacy boundary, and outcome rule. Does not authorize §13 sign-off, implementation spec drafting, runtime code, pricing, or client-facing copy.
- 4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv - three-row worksheet for logging the D10 MSP discovery conversations (`cybins-discovery-001` through `003`) with fields for relevance, named SMB anchor, named underwriting anchor, D10 yes/partial/no, buyer pain, evidence gap, pricing signal, follow-up, and notes.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md - pre-build proof protocol for the promoted sender-provenance / geo-velocity BEC detector idea. Defines the real-mailbox raw-header proof required before any spec-first runtime implementation may begin.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Runbook.md - operator-facing collection runbook for executing the sender-provenance cheaper proof safely against raw headers only.
- 4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv - sample classification worksheet for the raw-header proof run, with example `cloud_normalized` and `stable_high_value` rows.
- 4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md - pending-signature addendum to widen the Vendor Baseline Store closed signal enum for future sender-origin and callback-phone baselines. Spec-only; no implementation until §11 is signed.
- 4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md - **§11 SIGNED 2026-05-25 by Matt Nichol; Pass 1 + Pass 2 + Activation + post-Grok remediation landed; 905 / 905 pytest green at rubric signature (current global runtime baseline is 1043 / 1043 + 1 skipped verified 2026-05-30 per commits `014a163` + `82a7490` + `9bcb3d5`); §11.1 amendment 2026-05-25 SIGNED added `rubric_status` for D12 sentinel + audit-marker contract; §11.2 amendment 2026-05-30 SIGNED by Matt Nichol — adds the `callback_phishing_pattern` → `origin_timing` evidence-tag mapping per TOAD D13 (floor-lift to ≥1 on presence; exact 2 when also `risk_score >= 50` OR `recommended_risk_floor_lift >= 70`). Mapper code changes to `core/scoring/client_facing_rubric.py` are authorized only inside TOAD pass 2 scope and still require the normal gate / scan / operator commit authorization.** Spec-first contract for a deterministic client-facing 5-axis explanation layer (`sender_identity`, `conversation_continuity`, `vendor_payment_history`, `document_integrity`, `origin_timing`) that maps existing analysis evidence into a stable 0-10 rubric without replacing the internal 0-100 runtime score. Locks D1-D20, the 160-char explanation cap, report-only / monthly digest v1 surface, contradiction guard (high-risk lift + low-risk trim), rendering contract, gate-test plan, and the D12 unavailable failure sentinel.
- 4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md - **DRAFT (pre-§11), authored 2026-05-30 by Cursor (Claude) on Matt Nichol's instruction; no runtime code, no test harness implementation; §11 signature blank by design. All §10 sub-questions now resolved pre-§11 (Q2 RESOLVED 2026-05-31 → D23; Q8 / Q9 RESOLVED 2026-05-30 → D21 / D22; Q1 / Q3 / Q4 RESOLVED 2026-05-31 → D24 / D25 / D26 via 7-axis stress test recorded in `think_sheet.md`; Q5 / Q6 / Q7 RESOLVED 2026-05-31 → D27 / D28 / D29 via lighter verdicts in same think_sheet entry). Framework is close to §11-signable; signature remains operator-only.** Spec-first contract for NorthStar's email-security testing, validation, evidence, scoring, failure-analysis, and continuous-improvement framework. Wraps and disciplines the existing `core/scoring/eval/` harness, the `REACTION_TIMING_TEST_LOG.md` discipline, and the Cyber Insurance Evidence Package §14 Stage A test plan; does not replace them. Locks D1–D29: four-value category status enum (`supported` / `not_supported_yet` / `not_present_in_sample` / `evidence_missing`), five-value verdict enum (`legitimate` / `needs_review` / `high_risk` / `blocked_or_hold_recommended` / `unknown` — `safe`/`unsafe` forbidden), accuracy denominators include only `supported` categories (not-supported categories never scored as zero, never count against accuracy), evidence required for every score (else `evidence_missing` excludes case from accuracy), no chain-of-thought exposure (structured fields only — `rule_fired`, `evidence_tags`, `signals_observed`, `signals_missing`, `decision_path_summary` cap 280 chars), v1 test-data sources locked to `.example` domains / fake vendors / fake URLs / inert attachments / synthetic `.eml` / lab mailbox only (no live malware, no live phishing, no unauthorized third-party testing), v1 implementation surface locked to the operator-listed eight items (synthetic-fixture eval harness wrapper, confusion matrix, per-category supported/not-supported scoring, evidence-required validation, failure-report generation, retest linkage, precision/recall/FP/FN metrics, Unknown Discovery Rate counter), verdict vocabulary aligned with `REACTION_TIMING_TEST_LOG.md`, failure-analysis card mandatory before retest, forbidden-language inherited from `Compliance_and_Trend_Watch_Process.md`, capability registry append-only at status level, confidence calibration is four-bucket (`low` / `medium` / `high` / `overconfident`), reviewer notes optional and never override verdict, Unknown Discovery Rate first-class metric reported alongside accuracy, framework verdicts never authorise operator action, **testing is part of the build lifecycle not an operator reminder (D16), auto-trigger cadence closed and enumerated in §4.5 with smoke / regression / adversarial / eval-corpus paths (D17), red-team tests do not auto-run live and remain monthly-scheduled / controlled / synthetic (D18), commit-completeness gate requires the matched test tier to have run and recorded its result before `pre_ship_audit.py` may return SHIP (D19), failed-test acceptance is conjunctive — recorded + classified (named failure-type enum) + operator-accepted (signed acceptance entry with named risk owner + hard expiry) + retest-linked, all four or the commit blocks (D20), v1 Auto-Trigger Path Matrix locked in §4.5.8 as a twelve-row path × tier table covering detector / scoring / rubric / rendering / schema / production-loop / orchestration / evidence-packaging / fixtures / prompt+spec-output / signed-spec-with-runtime / docs-only surfaces (D21, resolves Q8), v1 enforcement authority for the commit-completeness gate is `audit_tools/pre_ship_audit.py` — `complete_gate.py` audits the work packet but does not replace the cadence gate (two independent enforcement layers), CI is future v1.1 / v2 layering, missing required test evidence fails the gate closed with a named reason, operator override requires all four D20 conjunctive conditions (D22, resolves Q9), **Pydantic models are the authoritative v1 per-case and evidence-bundle shape while generated JSON Schema is derived only (D23, resolves Q2)**, **v1 `confidence_bucket` boundaries are exactly `[0,25] / [26,60] / [61,100]` for `low/medium/high` with `overconfident` carved from `high` by `verdict_match ≠ exact`; recalibration requires ≥60 real fixture cases, §11-revision, and operator log entry naming evidence (D24, resolves Q1)**, **`adjacent` verdict mismatches contribute zero credit to accuracy denominators; `verdict_match_distribution` preserves the four-value breakdown so adjacency stays visible without averaging into accuracy (D25, resolves Q3)**, **default regression-tolerance is `0` percentage points strict; per-subcategory widening requires operator `PROJECT_ACTIVITY_LOG.md` entry naming subcategory, value, rationale, hard expiry (D26, resolves Q4)**, **red-team mission file structure is deferred to first real mission but eight minimum required fields are locked (`mission_id`, `scope`, `hypothesis`, `threat_model`, `controlled_synthetic_only_acknowledgement`, `success_criteria`, `scheduled_for`, `operator_authorization`); field names intentionally avoid `attestation` per the D10 forbidden-language inheritance (D27, resolves Q5)**, **v1 dashboard ships no composite quality score; §8.5 metric list is the dashboard; composite deferred to v1.1+ gated on operator-stated evidence (D28, resolves Q6)**, **failure cards with `failure_type` ∈ {`schema_violation`, `scope_violation`} are Decision Audit candidates and MUST carry `decision_audit_candidate_id` linkage field; runner integration / packet shape / dashboard surface are v1.1 with own signed spec (D29, resolves Q7)**. Defines four test levels (smoke / regression / adversarial / red-team with simulation-only boundary), §4.5 auto-trigger cadence + commit-completeness gate + failed-test acceptance rule + §4.5.8 v1 trigger matrix + §4.5.9 v1 enforcement authority, per-case record shape, audit-trail event schema, evidence bundle schema, failure card shape (now including the D29 `decision_audit_candidate_id` linkage), retest loop steps, and v1 dashboard metric set. §10 now has all nine sub-questions RESOLVED with cross-refs to D21–D29 / §4.5.8 / §4.5.9 / §7.2 / §8.1 / §8.2 / §8.5 / §9.4; §11 signature blank. Implementation of the v1 surface does NOT begin until §11 is signed and a separate explicit operator start-build instruction is issued.
- 4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md - **§11 SIGNED 2026-05-30 by Matt Nichol (commit `6c4b28f` resolved §10 stress test; commit `0a0c3c0` landed §11 signature + status-text cleanup); implementation pending Matt's explicit start-build instruction; rubric §11.1 amendment per D13 deferred to a separate revision cycle of `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`.** Spec-first contract for the Part 1 body-language slice of the Callback Phishing / TOAD detection layer; pure deterministic detector matching `header_divergence_detector` / `prompt_injection_detector` shape; explicitly excludes Part 2 phone-number baselining (gated on Vendor Baseline Store enum revision). Locks D1–D9 + D11–D15 (D10 superseded by D15 per the §10 Q5 verdict): the closed five-category phrase vocabulary (`call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, `payment_redirect_call` — no `mfa_bypass_call` in v1), lift-only invariant, default-OFF activation flag, mandatory out-of-band verification wording on hit, no numeric `callback_phishing_score` field in v1 (flag + categories + `recommended_risk_floor_lift` only), 1/2 `origin_timing` rubric mapping (present → ≥1; present AND (`risk_score ≥ 50` OR `recommended_risk_floor_lift ≥ 70`) → 2; D13 originally promised the §11.1 rubric amendment would land **with** the TOAD §11 signature, but the rubric amendment was deferred to a separate follow-up revision cycle — transient state: the rubric spec remains §11-SIGNED 2026-05-25 at its current text and does not yet carry the `callback_phishing_pattern` evidence-tag mapping), `body_plain`-only input surface in v1 (`body_html` deferred to v1.1+ on real-traffic evidence), `phone_number_assessment` slot omitted from the v1 schema entirely (Part 2 adds it through its own §11-signed spec via the Vendor Baseline Store `vendor_callback_phone_number` enum revision path), and a 14-test §8 closure gate. Implementation does **not** begin until Matt's explicit start-build instruction; pre-ship gate must complete before commit of any runtime code.
- audit_tools/grok_audit_runner.py - local one-off independent xAI/Grok auditor for spec-vs-code review; reads `XAI_API_KEY` from root `.env`, writes local-only reports to gitignored `audit_outputs/`.
- audit_tools/decision_audit_runner.py - local independent xAI/Grok decision-auditor for anti-drift governance; reads one operator-reviewed packet from `decision_audit_inputs/`, validates the locked six-section packet contract and secret/financial-data boundaries before network calls, writes reports to `audit_outputs/decision_audits/`, and fail-closes on blocking verdicts unless `--report-only` is explicitly used.
- audit_tools/pre_ship_audit.py - all-seeing pre-commit gatekeeper. Reads the current `git diff HEAD` + untracked files + all `§11 SIGNED` specs + the current direction from `PROJECT_HANDSHAKE.md` / `PROGRESS.md`, sends them to Grok with a senior-reviewer prompt, prints `VERDICT: SHIP | FIX_FIRST | STOP`, and writes the full report under `audit_outputs/pre_ship_audits/`. Exits zero on SHIP, non-zero on FIX_FIRST/STOP so it can act as a real gate; `--report-only` suppresses the blocking exit. This is the single check that runs before commit/push - it folds the code-audit and decision-audit patterns into one tool so the operator never has to re-issue ceremony phrases.
- 4. Product_Roadmap/Linux_Migration_Readiness_Pass.md - **Readiness map only. Not the migration. Pre-execution checklist. Operator-facing.** Authored 2026-05-31 by Cursor (Claude Opus 4.7) at operator request on clean tree after commit `f5b254d`. Inspects the current Windows-first state for what must be fixed before flipping to Linux-first; produces no code changes, no git config writes, no `.gitattributes` creation, no destructive commands. Reports overall risk verdict **LOW** with two specific mechanical settlements required (CRLF/LF settlement via §6 plan; optional `chmod +x` for the bash hook in §7) and one structural gate-cap interaction (R7, unchanged by migration). Locks the migration goal (move dev from Windows-first to Linux-first while preserving repo, tests, audit gates, local-first workflow), ten enumerated risks (R1 autocrlf noise / R2 case-insensitive filesystem / R3 filemode tracking / R4 single PowerShell legacy script / R5 SQLite POSIX hardening / R6 lazy pywin32 import / R7 200KB gate cap unchanged by migration / R8 Python version drift / R9 cryptography wheels / R10 negative-risk pytest tempfile cleanup), comprehensive files-affected map (everything inspected requires zero code change because the runtime is already cross-platform-aware by design per `requirements.txt` `pywin32 ; sys_platform == "win32"` + `core/production_state/vendor_baseline/isolation.py` cross-platform branch), §5.1 smoke commands (venv + requirements + targeted vendor-baseline + targeted vendor-payment-integrity), §5.2 full verification (full pytest 1055 / 1 skipped, trigger scan at baseline 1055, audit-gate end-to-end smoke, demo run), §5.3 optional case-collision check, §6 CRLF / LF plan (proposed `.gitattributes` content + `core.autocrlf=false` flip + standalone normalization commit), §7 enumerated Windows-only assumptions found (six items) + verified-absent list (no `cmd.exe` / `powershell` invocations / registry reads / COM-OLE-WMI / hardcoded `C:\\` / backslash path separators / Windows env vars), §8 migration checklist, §9 rollback plan (Windows box stays as-is; rollback is `git revert` on the one normalization commit), §10 what-not-to-touch-yet boundary, §11 anti-drift footer, §12 named failure modes (migration drama drift, CRLF normalization bundled with content commit, operator-override abuse, pywin32 reinstall drift, case-collision blindness, demo-script obsession, authority drift via readiness map). Does not authorize the migration; the operator decides the window. Does not edit any §11-SIGNED spec; consistent with the existing `Vendor_Baseline_Store_Deep_Dive.md` §2 "Operational note: Linux migration plan".

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
- MSP_Discovery_Evidence_Package.md - single-file evidence bundle for sending to an MSP owner after a discovery call; bundles the real 40-case `grok-4` eval result (honest about the FAIL), the 5/5 vendor-invoice post-patch diagnostic recovery (with raw vf-001 LLM JSON inlined), the real generated Acme Effective Parameter Report demo, the seven runtime non-negotiables, the SMB tier menu, an honest "what this does NOT claim" section, and a free 30-day first-MSP-pilot offer with reciprocal commitments. Pairs with `MILESTONE_ARC.md` A9 (the original Lane 3 cross-reference to `REVENUE_MAP.md` was removed when `REVENUE_MAP.md` was discarded in commit `cd1d5d5`).
- Cyber_Insurance_Vendor_Payment_Integrity_MSP_Call_Pack.md - operator-facing discovery call pack for the Cyber Insurance / Vendor Payment Integrity MSP cheaper-proof lane. Compresses the existing runbook into a 10-minute call flow, seven discovery questions, D10 strong-yes / partial / no criteria, safe wording replacements, worksheet logging instructions, and follow-up email template. Not client-facing copy, not a spec, not a signed claim, not pricing approval; active queue remains the three-MSP D10 discovery proof.
- Cyber_Insurance_Vendor_Payment_Integrity_Discovery_Call_Sheet.md - operator-facing target/contact sheet for the first Cyber Insurance / Vendor Payment Integrity discovery attempts. Prioritizes COEDC / Access Kelowna as the warm referral door, then local MSP and broker fallback paths with source URLs, contact paths, discovery angles, safe outreach templates, tomorrow sequence, result labels, and boundary language. Does not count as D10 evidence and does not authorize client-facing claims.
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
- Runtime_Implementation/tests/fixtures/reaction_timing/stage_a_vendor_payment_change.json - fictional vendor-payment-change email fixture used by `REACTION_TIMING_TEST_LOG.md` record `rxt-2026-05-29-003` to prove the Stage A reaction-timing scenario can run from a tracked input artifact instead of inline-only construction.
- Runtime_Implementation/tests/fixtures/reaction_timing/stage_a_lab_mailbox_authpass.json - lab-mailbox auth-pass reaction-timing fixture used by `REACTION_TIMING_TEST_LOG.md` record `rxt-2026-05-30-001`; sender identifier and `Authentication-Results` values are grounded in the real 2026-05-30 Microsoft 365 lab mailbox baseline (commit `f712066`), body / subject / attachment / recipient are synthetic, and a `limitations` block records lab-only scope, fixture-fixed timing, and the intentionally empty `received_headers`.
- Runtime_Implementation/tests/fixtures/lab_mailbox_baselines/microsoft_365_lab_mailbox_authentication_baseline.json - sanitized derived-evidence baseline distilled from the 2026-05-30 `Microsoft Lab Mailbox Header Test Recorded` activity-log entry (commit `f712066`); stores only derived auth-result fields (SPF/DKIM/DMARC selectors), the ARC observation, the assembled `Authentication-Results` header value consumed by the runtime SPF/DKIM/DMARC detector, Microsoft outbound classification (`SCL:1`, `SFV:NSPM`), Gmail first-send placement, reply-path success, and explicit `consumable_as` / `not_consumable_as` lists; no raw header bulk; lab-only.
- Runtime_Implementation/tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json - fictional Stage A vendor payment-redirect fixture for Cyber Insurance Evidence Package Deep Dive §14; tenant `bluefin-marine-supplies-demo`, fictional `.example` sender/recipient/vendor, SPF/DKIM/DMARC pass auth posture, synthetic payment-change body and invoice metadata, and a fictional tenant override used to exercise the Detection → Verification → Evidence → Audit Trail → Outcome Documentation dry-run path.

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
- `_NorthStar_Strategy_Matrix_Discipline_SPARK.md` - **SPARK only — pre-spec, unsigned, not §11. Not pricing approval. Not client-facing copy. Not a product sheet. Not a build authorization. Not a new required gate.** Idea-preservation file captured 2026-05-31 after a late-night chat run that produced six different matrices (Pain, Revenue, Strategic Relevance, Fear, Competitive Moat, Trust Layer) plus a proposed Quarterly Trend Review. Records the operator's discipline conclusion: adopt **three lightweight aids now** — (1) Pain Matrix (protects against feature creep), (2) Revenue Matrix (protects against unpaid "cool" features), (3) Strategic Relevance Score (four 0-10 questions covering mission fit / MSP sell value / evidence quality / trust + provability — protects the authenticated-deception mission); **park three as SPARK** — Fear Matrix, Competitive Moat Matrix, Trust Layer Matrix, each with explicit un-defer triggers; and **schedule via the existing process** — Quarterly Trend Review is not a new process; it is a reminder that the §11 SIGNED `Compliance_and_Trend_Watch_Process.md` already runs a monthly Frontier Intake Review with a quarterly deep-review every third month. Locks the boundary that matrices do not decide / do not replace Matt's authority / do not replace the Next-Action Decision Rubric / do not create a new gate / if a matrix conflicts with a signed spec the signed spec wins / if a matrix creates build friction simplify or remove it. Records named failure modes (matrix proliferation, decision laundering through matrix scores, fake progress through re-scoring, calibration drift, adjacent-surface drift, free-work perception, sycophancy / praise-stacking) and explicit trigger conditions for un-deferring each parked matrix. Companion to the pending `_NorthStar_Business_Positioning_SPARK.md` (separate operator-authorized capture of the moat-shape conclusion). Held, not buried — do not promote without Matt's lead.
- `_NorthStar_Eval_Harness_v1_Sketch_SPARK.md` - **SPARK only — pre-spec, unsigned, not §11. Not implementation authorization. Not a build start. Not pricing. Not client-facing copy. Not a contract. Not a new required gate.** Shape-sketch file captured 2026-05-31 (commit `9e14f8a` closed all nine §10 sub-questions of the Email Security Testing & Evidence Framework pre-§11). Records a five-surface sketch — (1) fixture format (per-case JSON under `core/scoring/eval/fixtures/<category>/<case_id>.json` with `case_id`, `category`, `expected_status`, `expected_verdict`, `fixture_source`, `fixture_source_sha256`, `expected_signals[]`, `expected_categories[]`, optional `adversarial_intent` / `mission_id` / `red_team_mission_ref`, `authored_by`, `notes` — JSONL aggregation is derived, not source of truth), (2) expected verdict (single-value from the D2 five-value enum; ambiguous cases use `needs_review`; per-case `verdict_match` matches §7.3; per-case `confidence_bucket` matches D12 / D24 boundaries `[0,25] / [26,60] / [61,100]` with `overconfident` carved from `high` by `verdict_match ≠ exact`), (3) evidence bundle (per-case `evidence_bundle.json` under `audit_outputs/testing_framework/runs/<test_run_id>/cases/<case_id>/` matching §9.1 schema with Pydantic-as-source-of-truth per D23; companion `decision_path.json` for structured-fields-only decision transparency per §9.3; optional `failure_card.md` and `reviewer_notes.json` only when present), (4) failure card (Markdown template matching §9.4 with D29 `decision_audit_candidate_id` linkage field mandatory when `failure_type` ∈ {`schema_violation`, `scope_violation`}; written automatically by harness on §9.4 failure trigger; D22 enforcement by `audit_tools/pre_ship_audit.py`), (5) precision / recall output (per-run `run_summary.json` + deterministic `run_summary.md` rendering — both emit the §8.5 metric set with no composite per D28; regression-tolerance enforcement against pinned baseline run named in audit-trail event, `0` pp default per D26). Anchors every shape decision to existing framework D-decisions (D1, D2, D3, D4, D5, D6, D7, D8, D9, D11, D12, D14, D18, D20, D22, D23, D24, D25, D26, D27, D28, D29, plus §6.2 / §7.3 / §8.1 / §8.5 / §9.1 / §9.2 / §9.3 / §9.4 / §9.5). Introduces no new D-decisions. Flags five open questions for the future spec pass (JSONL deprecation vs co-existence, `confidence_calibration_delta` v1 vs v1.1, `bundle_sha256` integrity field at write-and-read, failure-card auto-population scope, baseline-pinning mechanism) without locking any of them. Records eight items the real spec pass would have to cover beyond the sketch (test-run identifier discipline, audit-trail event emission rules, fixture promotion path, baseline-pinning mechanism, failure-card auto-population scope, `pre_ship_audit.py` integration contract, fixture authorship safety-source check, §11 sign-off placeholder). Implementation gate is conjunctive: BOTH `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` §11 signature AND a separate explicit operator start-build instruction are required before any code touches `core/scoring/eval/`. Named failure modes recorded (sketch-as-spec drift, pre-implementation lock-in, schema bypass, composite-score creep, auto-populated failure-card root cause). Companion to `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` (DRAFT pre-§11); flagged as candidate seed for a future `Email_Security_Eval_Harness_v1_Deep_Dive.md` only by explicit operator direction. Held, not buried — do not promote without Matt's lead.
- `_NorthStar_Cyber_Insurance_Vendor_Payment_Integrity_SPARK.md` - **SPARK only — pre-spec, unsigned, not §11. Not client-facing copy. Not pricing approval. Not a broker / insurer claim. Not implementation authorization.** Direction-capture file authored 2026-05-31 by Cursor (Claude Opus 4.7) at operator request, after commit `7faa86b` (`seed current state map with alert fatigue doctrine`). Records the operator's strategic-direction conclusion that the cyber-insurance discovery lane is a **buyer-pressure / evidence-readiness wedge** for a **Vendor Payment Integrity Evidence** business spine — *while* translating risky `compliance` / `certification` / `premium reduction` / `approved by` language into NorthStar-safe wording before any of it reaches a buyer surface. §1 core thesis (Vendor Payment Integrity Evidence as the spine; cyber-insurance lane as the wedge giving commercial pull; NorthStar does not become a cyber-insurance product). §2 keep / rewrite table (KEEP: insurance readiness as discovery wedge / Vendor Payment Integrity as strongest control story / evidence trail as product asset / carrier-agnostic reports per `Cyber_Insurance_Evidence_Package_Deep_Dive.md` D4 / MSP + broker discovery as future channel test gated on D10 / no warranty / no guarantee. REWRITE: `Compliance Engine` → **Evidence Readiness Engine** *or* **Cyber Insurance Evidence Support**; `Integrity Certificate` → **Monthly Evidence Summary**; `Premium Reducer` → **Insurance Conversation Support**; `NorthStar Verified` → **Verified Review Recorded** *or* **NorthStar Evidence Available**; `required by carriers` → **structured around common underwriting evidence requests**; `approve coverage` → **support underwriting conversations**). §3 NorthStar-safe positioning sentence (operator-authored, internal-only until separate operator pass clears it for buyer-facing surfaces; Authorship Rule applies). §4 explicit boundary (no claims of compliance with any framework, no certification, no insurer / carrier / underwriter approval, no premium reduction or pricing-outcome promise, no policy eligibility, no fraud-prevention absolute, no coverage approval; no runtime code, no signed-spec edits, no alteration of `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, no promotion to `PROJECT_BUILD_AND_AUDIT_QUEUE.md`; active queue remains MSP discovery — 3 relevant MSP conversations, looking for 2 strong yeses with named SMB anchor + named upcoming insurance / underwriting conversation per `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` D10 + `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`). §5 future trigger conditions (primary trigger: MSP discovery evidence with named MSP + named SMB + concrete request shape; parallel trigger: broker / underwriter / carrier-side primary-source evidence per `Compliance_and_Trend_Watch_Process.md` §2.6; reactive trigger: real post-incident review surfacing the same demand; explicitly named non-triggers: internal enthusiasm, single-source vendor research, AI-side argument, signed spec elsewhere). §6 anti-drift boundary footer (does not decide; does not authorize buyer-facing copy / broker or carrier outreach / pricing / signed-spec edits / new §5.1 forbidden-language addition; signed spec wins on conflict). §7 named failure modes (wedge-as-product drift, forbidden-language slip via wedge framing, decision laundering through matrix scores, pre-discovery promotion, free-work perception, authority drift via positioning sentence, Authorship Rule violation, sycophancy / praise-stacking). Held, not buried — promotion requires both an operator-recorded §5 trigger and Matt's explicit decision.
- `_NorthStar_Railbridge_Post_Invoice_Payment_Operations_SPARK.md` - **SPARK only — pre-spec, unsigned, not §11. Not a product spec. Not pricing approval. Not a banking / lending / compliance / insurance / money-movement authorization. Not client-facing copy. Not validated market proof — operator-observed product-discovery signal only.** Separate-venture / adjacent-product capture for **Railbridge**, an operating-layer-after-the-invoice-is-sent product targeting service businesses with payment-tracking detective-work pain (e-transfers, emails, screenshots, partial payments, follow-ups). Authored 2026-05-31 by Cursor (Claude Opus 4.7) at operator request after the Vendor Payment Integrity break-it test pass (working-tree baseline `1055 passed, 1 skipped`). Captures the source signal, the problem (payment truth, not invoicing), the V1 wedge (payment requests + tracking + follow-ups + bank-payment workflows), the long-term directional sketch (receivables → operations → business bank accounts → movement of funds → cash-flow visibility → access to capital — none authorized by this SPARK), the NorthStar-vs-Railbridge relationship (adjacent, not merged — shared operator + spec-first habit + honesty discipline + authority model only; codebases / brands / customer evidence are NOT shared), the §8 non-authorization list (no banking / lending / money-movement / compliance / insurance / runtime / signed-spec / queue / D10 advancement), and the §9 open questions (vertical fit, pilot signal quality, channel mix, minimum V1 shape, venture relationship). Pilot status: early; free pilots running; website `railbridgepay.com`. Does NOT advance NorthStar Cyber Insurance Evidence Package D10 (D10 requires named NorthStar-relevant MSP + named SMB + named upcoming insurance / underwriting conversation; Railbridge service-business pilot evidence does not satisfy that bar). Held, not buried — promotion to anything more substantive requires a separate operator decision and a separate spec.
- `_Cross_Channel_Fraud_Shield_Concept_Capture.md` - **SPARK only — pre-spec, unsigned, not §11. Not a product. Not a brand. Not a revenue plan.** Idea-preservation file capturing a three-stage "email-to-phone fraud handoff protection" framing that surfaced 2026-05-30 in a separate proposal block alongside (and unrelated to) the TOAD §10 commit `6c4b28f`. Stage A = the existing TOAD email body-language detector (already specified pre-§11 in `Callback_Phishing_TOAD_Detector_Deep_Dive.md`); Stage B = a deferred per-tenant known-channel phone-number baseline, gated on the existing pending-signature `Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md` (`vendor_callback_phone_number` enum entry); Stage C = any phone-system / live-call integration of any kind, parked behind a hard legal / consent review covering Canadian PIPEDA, US two-party-consent states, UK / EU GDPR Art. 6 + Art. 9, and any sectoral overlay. Records what the SPARK explicitly does NOT include (no product name, no sub-brand, no revenue matrix, no Stage B schema, no Stage C technical design, no legal opinion), the parked failure modes (wiretap / consent risk, forbidden-language slip, identity drift, decision laundering, free-work perception, scope creep into the signed-pending TOAD spec, sycophancy / praise-stacking of D11–D15), and explicit trigger conditions for un-deferring Stage B only — Stage C never auto-triggers. Held, not buried; do not promote without Matt's lead.
- `External_Model_Brief_Template.md` - **DRAFT (pre-§11) authored 2026-05-27 by Matt Nichol.** Trust-gate / anti-sycophancy doctrine and paste-and-go template for talking to external cloud LLMs (Gemini, Perplexity, ChatGPT, Claude.ai, future additions) about NorthStar without sycophancy drift, hallucinated project facts, or data-hygiene breaches. Locks D1-D10 covering external-model role (advisory consultants, not approvers), trust-gate primacy (the §3 ruleset is non-negotiable), inherits the Compliance_and_Trend_Watch_Process.md §1.1 advisory supersession extended to external models, data-hygiene boundary (no client-identifying data, no raw emails/headers from production tenants, no `production_state/`, no `1. Business_Operations/Client_Documents/`, no Financial State Ledger, no Vendor Baseline Store, no secrets), agreement-by-default forbidden, confidence labels required on substantive claims, knowledge-cutoff disclosure required, push-back-on-premise duty, no proxy decisions, paste-and-go (not auto-injected). Includes a load-bearing 10-rule trust-gate ruleset (§3), a paste-and-go project-context block (§4), two role blocks (deep research for Gemini/Perplexity, strategic reasoning / second-opinion for ChatGPT/Claude.ai), an output contract requiring "opening / body with confidence labels / options / what-I-might-be-missing" shape, and eight named external-model-specific failure modes (sycophancy by default, plausible hallucination, knowledge-cutoff extrapolation, data leakage to cloud LLMs, authority drift via the back door, premise laundering, doctrine bypass via external model, code-as-back-door). §10 holds six open questions for operator resolution before §11 sign-off (template structure one-file vs per-model, whether Grok prompts adopt §3 verbatim, logging persistence, additional forbidden topics, stronger data-hygiene mitigation beyond prompt warning, external-model output review cadence).
- `Next_Action_Decision_Rubric_Deep_Dive.md` - **DRAFT (pre-§11) authored 2026-05-27 by Matt Nichol.** Tactical-layer scoring rubric for ranking 3-7 next-action candidates inside an active session. Distinct from `think_sheet.md` (strategic / idea-level) and `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (buyer-facing / email-level). Five axes (`leverage`, `risk_reduction`, `evidence_strength`, `future_cost` inverted, `reversibility`), 0-2 each, max 10. 10-step decision loop (OBSERVE → GENERATE → SCORE → RANK → PRESENT → HUMAN DECISION → EXECUTE → AUDIT → LOG → UPDATE SIGNALS) with hard rules forbidding multi-action execution, step-skipping, mid-cycle structural changes, and autonomous rule mutation. Locks D1-D12 covering authority model (rubric ranks, human decides), naming (canonical name forbids "5-axis rubric" label to avoid collision), calibration scope (mismatch-logging only), pre-execution expectation capture, operator override path, and forbidden self-modification. §10 holds seven open questions for operator resolution before §11 sign-off (option-source / queue relationship, mode formalization, cycle-log persistence, calibration cadence, Grok-audit boundary, compressed system-prompt build, "do nothing" scoring guidance). Inherits `Compliance_and_Trend_Watch_Process.md` §1.1 supersession (rubrics are advisory only).
- `Consequence_Matrix_Process.md` - **DRAFT (pre-§11) created 2026-05-30 from Matt's "butterfly effect" decision discussion.** Operator-triggered process for path-setting decisions whose consequences may compound across revenue, architecture, legal / insurance posture, buyer trust, product identity, signed specs, or future autonomy. Distinct from `think_sheet.md` and the Next-Action Decision Rubric: it does not score or decide; it surfaces short-term and long-term consequences. Includes trigger criteria, non-trigger boundaries, a 15-minute time-box, template tables, column definitions, failure modes, and the rule that agents may flag trigger criteria but do not run the matrix without Matt's explicit instruction.

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
