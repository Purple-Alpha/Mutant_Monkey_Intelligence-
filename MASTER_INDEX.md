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
- LINUX_WORKFLOW_QUICKSTART.md - operator-facing quickstart for the 2026-06-01 WSL2 cutover. Explains PowerShell vs Ubuntu prompts, the primary Linux repo path (`/home/socialarchitect/northstar`), Windows backup/reference path, venv activation, standard trigger-scan / pytest commands, gate smoke command, commit-history meaning, and secret-handling caution. Not a spec and not §11; practical daily-use orientation only.
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
- 4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md - **DRAFT (pre-§11), authored 2026-06-03 by Cursor (Claude) on Matt Nichol's instruction; no runtime code, no workflow-engine implementation; §11 signature blank by design; six §10 open questions remain operator-only.** Spec-first contract for the operator-side disposition workflow that records what a human did after NorthStar flagged a vendor-payment change for out-of-band verification. Closes the single formal open gap in `CURRENT_STATE_MAP.md` and supplies the workflow state machine `Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` §1 explicitly deferred. Locks D1–D12: a closed four-value disposition enum (`verified` / `unresolved` / `false_positive` / `follow_up_needed`) with `verified`/`false_positive` terminal and `unresolved`/`follow_up_needed` non-terminal (must spawn a follow-up with `prior_disposition_ref`), one open disposition per `(tenant_id, finding_id)` with append-only revisions, mandatory structured evidence (closed `verification_channel` enum + `what_was_confirmed` <=280 chars + `recorded_by` + `recorded_at_utc`), no raw financial strings / no PII / no chain-of-thought ever (inherits FSL D13), no autonomous payment action (inherits FSL D11), `false_positive` linkage into the false-positive / false-negative correction evidence loop via `correction_loop_ref`, disposition never authorizes operator action / payment release / ship / sign, append-only audit-trail events (open / revise / close / reopen / follow-up-created / follow-up-expired), tenant isolation preserved (Guardrail 11), forbidden-language inherited from `Compliance_and_Trend_Watch_Process.md`, kill-switch read-only precedence (Guardrail 12). Defines §3 state model, §4 five-step lifecycle, §5 record + evidence schema + verification-channel closed enum, §6 audit events, §7 digest/report rendering boundary (Alert-fatigue doctrine: batched per-tenant, not per-event), §8 relationship boundaries to FSL / Two-Channel Confirmation / Email Security Testing & Evidence Framework / Reaction Timing Log / Cyber Insurance §14, §9 failure modes, §10 six open questions (follow-up expiry/SLA, relationship to Two-Channel outcome enum, on-disk surface, false_positive correction-loop auto-open behaviour, who may record a disposition, idempotency key). Implementation does NOT begin until §11 is signed, every §10 question is resolved, and a separate explicit operator start-build instruction is issued.
- 4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md - **§11 SIGNED 2026-05-30 by Matt Nichol (commit `6c4b28f` resolved §10 stress test; commit `0a0c3c0` landed §11 signature + status-text cleanup); implementation pending Matt's explicit start-build instruction; rubric §11.1 amendment per D13 deferred to a separate revision cycle of `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`.** Spec-first contract for the Part 1 body-language slice of the Callback Phishing / TOAD detection layer; pure deterministic detector matching `header_divergence_detector` / `prompt_injection_detector` shape; explicitly excludes Part 2 phone-number baselining (gated on Vendor Baseline Store enum revision). Locks D1–D9 + D11–D15 (D10 superseded by D15 per the §10 Q5 verdict): the closed five-category phrase vocabulary (`call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, `payment_redirect_call` — no `mfa_bypass_call` in v1), lift-only invariant, default-OFF activation flag, mandatory out-of-band verification wording on hit, no numeric `callback_phishing_score` field in v1 (flag + categories + `recommended_risk_floor_lift` only), 1/2 `origin_timing` rubric mapping (present → ≥1; present AND (`risk_score ≥ 50` OR `recommended_risk_floor_lift ≥ 70`) → 2; D13 originally promised the §11.1 rubric amendment would land **with** the TOAD §11 signature, but the rubric amendment was deferred to a separate follow-up revision cycle — transient state: the rubric spec remains §11-SIGNED 2026-05-25 at its current text and does not yet carry the `callback_phishing_pattern` evidence-tag mapping), `body_plain`-only input surface in v1 (`body_html` deferred to v1.1+ on real-traffic evidence), `phone_number_assessment` slot omitted from the v1 schema entirely (Part 2 adds it through its own §11-signed spec via the Vendor Baseline Store `vendor_callback_phone_number` enum revision path), and a 14-test §8 closure gate. Implementation does **not** begin until Matt's explicit start-build instruction; pre-ship gate must complete before commit of any runtime code.
- audit_tools/grok_audit_runner.py - local one-off independent xAI/Grok auditor for spec-vs-code review; reads `XAI_API_KEY` from root `.env`, writes local-only reports to gitignored `audit_outputs/`.
- audit_tools/decision_audit_runner.py - local independent xAI/Grok decision-auditor for anti-drift governance; reads one operator-reviewed packet from `decision_audit_inputs/`, validates the locked six-section packet contract and secret/financial-data boundaries before network calls, writes reports to `audit_outputs/decision_audits/`, and fail-closes on blocking verdicts unless `--report-only` is explicitly used.
- audit_tools/pre_ship_audit.py - all-seeing pre-commit gatekeeper. Reads the current `git diff HEAD` + untracked files + all `§11 SIGNED` specs + the current direction from `PROJECT_HANDSHAKE.md` / `PROGRESS.md`, sends them to Grok with a senior-reviewer prompt, prints `VERDICT: SHIP | FIX_FIRST | STOP`, and writes the full report under `audit_outputs/pre_ship_audits/`. Exits zero on SHIP, non-zero on FIX_FIRST/STOP so it can act as a real gate; `--report-only` suppresses the blocking exit. This is the single check that runs before commit/push - it folds the code-audit and decision-audit patterns into one tool so the operator never has to re-issue ceremony phrases.
- audit_tools/score_sheet_review_scanner.py - Wave 3.1 shared no-PII / no-secrets / raw-payload scanner imported by both `audit_tools/review_ledger.py` and `Internal_Tools/precommit_score_sheet_safety_hook.sh`. Owns the single pattern source and no-echo formatter for scanner findings (`BLOCK` / `WARN`) across score-sheet candidate/review surfaces. Blocks secrets, raw financial identifiers, raw payload leakage, live tokenized URLs, and chain-of-thought labels; warns on ambiguous PII markers; allows explicit placeholders and `.example` domains.
- audit_tools/review_ledger.py - Wave 3.1 operator-run, read-only score-sheet candidate review helper. Implements only `list`, `inspect`, `check`, `draft`, and `stale`; lists unresolved `*.candidate.jsonl` packets, parses packet headers/rows, runs the shared scanner and Wave 3 checklist, emits stdout-only non-canonical 13-column draft rows with `OPERATOR_TO_ASSIGN`, `OPERATOR_TO_SET`, and `DRAFT_NOT_CANONICAL`, and reports stale unresolved packets older than 60 days. Never promotes, rejects, moves, deletes, rewrites packets, writes the canonical score sheet, assigns final `event_id`, sets operator-bearing `recorded_by`, imports `pre_ship_audit.py`, or touches runtime/tenant state.
- Internal_Tools/precommit_score_sheet_safety_hook.sh - Wave 3.1 separate local pre-commit hook beside the existing LLM safety hook. Scans only staged score-sheet evidence/review surfaces through `audit_tools/score_sheet_review_scanner.py`; blocks scanner `BLOCK` findings without echoing sensitive values; does not replace `precommit_llm_safety_hook.sh` and does not scan unstaged or gitignored local-only files.
- 4. Product_Roadmap/Linux_Bringup_Command_Checklist.md - **Operator playbook only. Copy-paste-ready commands. Not the migration. Not policy. Not a spec.** Authored 2026-05-31 by Cursor (Claude Opus 4.7) at operator request on clean tree after commit `be2b006` (`add linux line ending policy`). Pairs with `Linux_Migration_Readiness_Pass.md` §5 (the wider command sketch); this is the tighter execution sheet. Locks the Linux verification sequence into twelve sections: §1 prerequisites (Python 3.13+/3.14, pip, venv, git, sqlite3 CLI, build-essential for cryptography wheel fallback; Debian/Fedora/Arch one-shot install lines; `.env` with `XAI_API_KEY` does NOT travel with repo and must be transferred manually), §2 clone-or-rsync (Option A `git clone`, Option B `rsync` from Windows over ssh with `.venv` / `__pycache__` / `.pytest_cache` / `audit_outputs/decision_audits` excluded; HEAD-match and `.gitattributes`-in-force verification), §3 virtualenv setup (`python3 -m venv .venv`; `pip install --upgrade pip`; gitignored), §4 dependency install (single primary path `pip install -r requirements.txt` after the dependency-declaration gap was closed by the follow-up `pin linux bringup dependencies` commit pinning `pydantic==2.13.4`, `cryptography==48.0.0`, `requests==2.33.1`, `httpx==0.27.2`, `pytest==9.0.3` alongside the existing `pywin32 ; sys_platform == "win32"`; pywin32-NOT-installed-on-Linux sanity check; pin-change discipline — any pin bump is a separate operator-authorized commit with a fresh full pytest pass and trigger scan, never a bring-up improvisation), §5 trigger scan (baseline 1055, expected `scan_clean` + empty `drift_findings`), §6 targeted pytest in five-test order (vendor_baseline_isolation_boundary → vendor_baseline_store → vendor_payment_integrity_break_it → fraud_eval_harness → pre_ship_audit; stop on first failure, do NOT paper over with `--continue-on-collection-errors`), §7 full pytest (expected `1055 passed, 1 skipped` or higher; explicit note that Windows-only atexit `PermissionError [WinError 5]` traceback will vanish on Linux — feature, not regression), §8 audit-gate smoke using a doc-only `PROJECT_ACTIVITY_LOG.md` entry as both the smoke and the durable record (matching the `cd1d5d5` / `5662872` / `be2b006` pattern; one Grok API call ~$0.01), §9 PASS criteria (six conjunctive checks; no papering over), §10 FAIL capture bundle (six numbered diagnostic captures: pip freeze, git state and config, system+locale facts, failing command stdout+stderr, first-failing pytest with `-x --tb=long`, gate audit report), §11 what-NOT-to-do during bring-up (no renormalization, no git config flips, no signed-spec edits to silence failures, no runtime-code edits to silence failures, no push, no manual pywin32 install, no `.gitattributes` modifications), §12 operator decision points enabled by a green bring-up (renormalization commit, primary-dev-surface switch, CI provisioning; the `requirements.txt` dep-pinning item that originally appeared here was closed in advance of bring-up by the `pin linux bringup dependencies` commit). Does not authorize migration; the operator decides the window. Does not edit any §11-SIGNED spec.
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
- Moved 2026-06-03 to `4. Product_Roadmap/Roadmap_Docs_Index.md` (verbatim) to keep this index within the audit-gate packet cap. See that file for the full per-doc roadmap listing. No entries deleted.

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

---

# Recent Indexed Addendum

- `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Section13_Readiness_Packet_20260603.md` - **Operator-review packet only — not §13 sign-off, not implementation authorization, not client-facing copy, not pricing approval.** Assembled 2026-06-03 after Matt signed the D10 cheaper-proof override in `PROJECT_ACTIVITY_LOG.md`. Summarizes the §13 review question, current gate state, override basis, spec surfaces under review, minimum audit-packet inputs, split-audit warning for the 200 KB cap, and the exact boundary that D10 is **overridden, not met**. Does not draft Matt's §13 signature wording and does not claim cheaper-proof validation or market proof.
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Implementation_Deep_Dive.md` - **DRAFT pre-§11 — not signed, not implementation authorization, not code, not client-facing copy.** Drafted 2026-06-03 as Build List item 3 after the §13 sign-off of the Cyber Insurance Evidence Package Deep-Dive. Defines the build-layer HOW: generation pipeline (§3), module/authority boundaries (§4), on-disk artifact layout (§5), evidence collection + freshness (§6), the nine §7 gate implementations, redaction/forbidden-language/vocabulary/D11 vendor-name mechanics (§8), render surfaces + HC6/HC7/HC8 (§9), Grok audit-packet coverage (§10), done declaration (§11), drift handling (§12), determinism pins parked here by HC7 (§13), the §14 test-plan runner, commercial-boundary commitments HC10–HC13 (§15), open questions IQ1–IQ7 (§16), and an unsigned §11 placeholder (§17). Implements the signed deep-dive without re-opening any D1–D11 decision; D10 remains overridden, not met.
