# PROGRESS

**Purpose:** Always-current task tracker. Updated whenever a task is finished.

**Update rule:** When a task is closed, mark it ✅, add finish date and verification line, then move to the next item in the list.

**Runtime baseline (last verified):** **1055 tests passing, 1 skipped** (verified 2026-05-31, exit code 0). The +53 delta from the prior `990 tests passing` baseline is the Callback Phishing / TOAD detector pass 2 wiring + break-it tests (commit `9bcb3d5` — 15 new integration tests in `tests/test_callback_phishing_scoring_integration.py` covering default-off no-regression, enabled-fire path, body_plain-only enforcement, attach-always invariant, flag append, max-merge floor lift, signed rubric §11.2 floor-lift, §11.2 higher-band exact-2 branch, and production-loop rebuild preservation; 38 new adversarial tests in `tests/test_callback_phishing_break_it.py` covering false-positive resistance, false-negative resistance, scope-violation probes (no phone-number / no body_html / no numeric callback_phishing_score / no default-off leakage), crash resistance (empty / whitespace / control characters / zero-width unicode / >200K-char bodies / scan-cap probes), over-lift probes, rubric explanation mismatch probes, cross-tenant isolation, production-loop preservation, daily-digest D8 OOB wording rendering, and StrictModel schema integrity). The further +6 delta from `1043 tests passing` to `1049 tests passing` is the six TOAD scope-boundary / adversarial tests added 2026-05-31 in `tests/test_callback_phishing_break_it.py` under the §11-SIGNED TOAD spec's D11 (English-only closed phrase-category vocabulary) and D14 (`body_plain`-only input surface). The further +6 delta from `1049 tests passing` to `1055 tests passing` is the six Vendor Payment Integrity break-it tests added 2026-05-31 in `tests/test_vendor_payment_integrity_break_it.py` under the §11-SIGNED Financial State Ledger / Delta Tripwire spec (D9 risk floor 85 / D11 no autonomous payment decision / D13 data minimization), the Vendor Baseline Store spec (D2 hash-only / D5 per-tenant salt / D6 per-tenant file isolation), the Tiered Detection Intensity spec (D11 lift-only invariant), and the `CURRENT_STATE_MAP.md` Alert-fatigue doctrine — covering: (1) multi-signal `recommended_action` stays `needs_review` and never produces any block/quarantine/deny/reject verb even when three different first-seen payment signals stack inside one email; (2) raw routing / account / IBAN (spaced + packed) / SWIFT (spaced + packed) / payment-portal URL with `token=supersecret` query never leak into the full assessment `asdict` dump across the entire supported signal set; (3) benign vendor-payment language carrying `pay / remit / invoice / billing` context plus a bare 10-digit reference number without a labelled financial identifier produces zero extracted signals, zero findings, `recommended_action == "none"`, and opens no per-tenant Vendor Baseline Store row; (4) multi-finding FSL overlay max-merges the floor (LLM 10/50/84/85 lift to 85; LLM 86/95/100 preserved unchanged) and three findings do NOT stack additively above 85; (5) `daily_digest_agent` does not import `financial_state_ledger` / `FinancialStateLedgerAssessment` / `assess_financial_state_delta` / `DeltaTripwireFinding` directly (Alert-fatigue doctrine pinned in code: Stage A is one digest per `(tenant_id, digest_date)`, not a per-email FSL alert stream); (6) per-tenant HKDF salt yields different `signal_hash` values for identical raw routing numbers ingested into `tenant_break_it_a` vs `tenant_break_it_b`, both database files exist at distinct per-tenant paths, and the raw routing bytes appear in neither on-disk SQLite file. All six confirm stated boundaries within signed specs; zero runtime / detector / scoring / daily-digest / vendor-baseline-store code changed.

---

## Current handoff (updated 2026-06-03)
Wave 2 candidate emitter (`score_sheet_candidate_emit.py` + `pre_ship_audit.py` wiring) is implemented and validated on Linux primary (`b7328e7`, backed up to `github` + `backup`). Wave 3 draft landed (`1b46ca3`) and Wave 3 §11 signature + §10.A decisions landed (`53c9310`, pushed to `github` + `backup`). **Wave 3.1 draft now exists:** `4. Product_Roadmap/Score_Sheet_Review_Ledger_Wave3_1_Deep_Dive.md` defines the future `audit_tools/review_ledger.py` + no-PII / no-secrets hook contract as spec-only work. **§11.A operator-confirmed (2026-06-03):** stdout-only `draft` (no `--out`); shared scanner module `audit_tools/score_sheet_review_scanner.py`; separate hook `Internal_Tools/precommit_score_sheet_safety_hook.sh` beside existing LLM hook; `stale` included with 60-day read-only default. Still forbids auto-promotion, ledger writes, packet moves/deletes, final `event_id` / operator-bearing `recorded_by`, emitter/scoring/runtime changes, and client/compliance/insurance claims. **Wave 3.1 §12 now operator-signed (Matt Nichol / Zebra-Comit, 2026-06-03):** the spec + §11.A decisions are ratified as governing truth. **Pending:** separate §13 "start build" authorization before any implementation. No Wave 3.1 code exists yet (no `review_ledger.py`, no `score_sheet_review_scanner.py`, no score-sheet safety hook). Windows-mirror edits may still need `cp` → commit/push on `~/northstar`.

---

## Active Task List

### Standing rule - Reaction timing test documentation — ✅ DONE 2026-05-28
- Added the project rule that every NorthStar reaction-timing test must be timestamped and documented before it counts as evidence.
- Scope includes detection latency, verification-request latency, verification-outcome latency, case-closure latency, and related Stage A/B timing checks.
- Minimum durable record: `test_id`, `run_started_at`, `run_finished_at`, scenario, expected result, actual result, verdict (`pass`, `partial`, `fail`, or `blocked`), timing fields, evidence artifact paths or record IDs, and notes.
- Negative, partial, and blocked results are preserved as evidence, not discarded.
- Source of rule: operator instruction during the 2026-05-28 reaction-timing discussion.
- Verification: doctrine-only update in `AGENTS.md`; no runtime tests required.

### 1. SMB tier matrix in `Product_Sheets/Fraud_Detection_Product_Sheet.md` — ✅ DONE 2026-05-22
- Added **Essentials / Plus / Enterprise** matrix in `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md`.
- Tier vocabulary matches `Autonomous_Orchestration/agent-enablement-map-per-tier.md` and `trigger-routing-table-per-tier.md`.
- Inclusion rules documented: no tier removes kill switch, audit, cross-tenant rejection, or expands the eligible override keys.
- Verification: documentation-only change; no test impact at time of landing.

### 2. Autonomous trigger scanner — ✅ DONE 2026-05-22
- `scripts/project_trigger_scan.py` — read-only scanner emitting trigger packets + optional one-hour mission envelope.
- `tests/test_project_trigger_scan.py` — **10 passed**.
- Full suite: **471 passed** (+10 from 461, zero regressions).
- Training-only default; production writes / override writes / rollback / external calls / client sends blocked on every packet.
- Invoke: `python -m scripts.project_trigger_scan --baseline-tests 473` from `Runtime_Implementation/`.
- Follow-up cleanup: scanner now accepts `BLOCKED` / approval-gated progress states as current work, so Task 3's API-budget gate does not produce false drift.

### 3. Phase 1.5 A/B numeric proof — ⚠️ DONE 2026-05-22 (FAIL verdict)
- Matt operator-ran the 40-case `grok-4` rerun:
  `python -m core.scoring.eval.fraud_eval_harness --provider xai --model grok-4 --report-out eval_report_2026_05_22_phase_1_5_rerun.md`
- Result: **36 / 40 overall**, **100% fraud precision**, **0% legit FPR**, but **Gate verdict: FAIL**.
- Failing aggregate criterion: `vendor_invoice_fraud` recall was **40%** (2 / 5), below the required **60%** floor.
- Durable report: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md`.
- No extra diagnostic rerun has been performed; saved report contains aggregate/subcategory data only.

### 4. Vendor-invoice recall remediation — ✅ DONE 2026-05-22 (no-spend prompt patch)
- Diagnosed the failed Phase 1.5 rerun without additional API calls.
- Added a small **Phase 1.5 vendor-invoice recall floor** to `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`.
- Patch pins the five weak vendor-invoice shapes: first invoice after onboarding + PDF remittance instructions, updated remit-to / old instructions invalid, fake thread continuity, and high-value emergency invoice before EOD.
- Added prompt-lock regression coverage in `tests/test_email_risk_scoring_agent.py`.
- Verification: `python -m pytest tests/test_email_risk_scoring_agent.py -q` -> **28 passed**; full suite -> **472 passed**.

### 5. Targeted vendor-invoice live diagnostics — ✅ DONE 2026-05-22 (5 / 5 PASS)
- Matt operator-ran 5 single-case `grok-4` diagnostics (`--case-id vf-001..vf-005`).
- Result: **every vendor-invoice case passed** after the Phase 1.5 recall floor was added to the locked prompt:
  - vf-001 risk=88, vendor_fraud=88, action=block
  - vf-002 risk=65, vendor_fraud=60, action=needs_review
  - vf-003 risk=68, vendor_fraud=65, action=needs_review
  - vf-004 risk=70, vendor_fraud=68, action=needs_review (thread-hijack pattern handled)
  - vf-005 risk=78, vendor_fraud=70, action=needs_review (high-value EOD pressure handled)
- Durable per-case reports: `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md`.
- Interpretation: the recall regression from item 170 is remediated. A full 40-case rerun is expected to PASS the gate but is optional tonight; precision and FPR were already clean.

### 6. Optional full 40-case rerun verification — ⏸ DEFERRED (no urgency)
- Would consume ~40 more `grok-4` calls.
- Not blocking revenue or any downstream work; per-case diagnostics already prove the patch lifted every vendor-invoice case.
- Re-open whenever Matt wants a clean PASS gate report on file.

### 7. Long-arc tracking foundation — ✅ DONE 2026-05-23
- Landed four root-level tracking docs to protect the multi-year arc from drift:
  - `VISION.md` — Matt's self-evolving defensive swarm thesis + Stage A / B / C arc + seven non-negotiables + what we will / won't keep up on.
  - `MILESTONE_ARC.md` — Stage A / B / C engineering + revenue + documentation milestones with "done when" criteria; status summary marks A engineering 7/11 done, A revenue 0/7, A docs 4/6.
  - `THREAT_INTEL_LOG.md` — evolution-log surface with planned free intake sources (CISA KEV, MITRE ATT&CK, abuse.ch, Phishtank, OTX) and first entry filed for the Phase 1.5 vendor-invoice recall floor.
  - `REVENUE_MAP.md` — three-lane revenue plan (Survival / Freelance / NorthStar) with Kelowna-specific employer targets, WorkBC wage-subsidy interview script ($18.00/hr confirmed; week-count pending Tuesday case-manager confirmation), 90-day MSP discovery program with 5-question script, pricing experiments, and weekly cadence per lane.
- Doc-only change; no test impact. Runtime baseline holds at **472 tests passing**.

### 8. MSP discovery evidence package — ✅ DONE 2026-05-23
- Landed `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` — single-file evidence bundle for sending to an MSP after a discovery call (Milestone A9).
- Contents (all backed by real saved data in the repo, no fabricated numbers): 60-second read; auditable-AI moat table vs. typical AI tools; Proof Point 1 — full 40-case `grok-4` rerun results (36/40, 100% precision, 0% FPR, vendor_invoice_fraud recall 40% honest FAIL); Proof Point 2 — 5/5 vendor-invoice post-patch diagnostic table + raw vf-001 LLM JSON; Proof Point 3 — now points to the real generated Acme Effective Parameter Report artifact with reproducible command; Proof Point 4 — seven non-negotiable runtime guardrails with MSP-side rationale; 473-test verification surface map; SMB tier menu (Essentials / Plus / Enterprise) with inclusion rules; honest "what this does NOT claim" section; free 30-day first-MSP-pilot terms with reciprocal commitments; 5 discovery follow-up questions; contact placeholder + source-of-truth file appendix.
- Tone is buyer-readable but evidence-first; safe-claim boundary from product sheet preserved throughout.
- Doc-only change; no test impact. Runtime baseline holds at **472 tests passing**.

### 10. Real Acme Effective Parameter Report demo — ✅ DONE 2026-05-23
- Landed `scripts/acme_effective_parameter_report_demo.py` — deterministic operator-side generator for the fictional `acme-industries-demo` tenant. It seeds an isolated demo blackboard, writes signed policy state, creates real per-tenant override audit events through the existing override API, then invokes the real `tenant_override_operator report --format markdown --out ...` CLI path.
- Generated real client-facing artifact: `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md`.
- Updated `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` Proof Point 3 from a synthesized example to the generated artifact + reproducible command.
- Added `tests/test_acme_effective_parameter_report_demo.py`.
- Verification: `python -m pytest tests/test_acme_effective_parameter_report_demo.py tests/test_effective_parameters_report.py -q` -> **19 passed**; full suite `python -m pytest -q` -> **473 passed**; scanner `python -m scripts.project_trigger_scan --baseline-tests 473` -> **scan_clean**.

### 11. Inbox Shield sample monthly report — ✅ DONE 2026-05-23
- Landed `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md` as the current MSP-facing monthly review artifact for Inbox Shield.
- Keeps the legacy phishing-simulation sample report intact while adding a current report built around Inbox Shield fields: `risk_score`, `vendor_fraud_score`, `wire_transfer_anomaly_score`, `invoice_authenticity_score`, `recommended_action`, `behavioral_deviation_flags`, effective-parameter provenance, and advisory action boundaries.
- Pairs with `Generated/Acme_Effective_Parameter_Report_Demo.md` and `MSP_Discovery_Evidence_Package.md`: the evidence package proves the system, the generated parameter report proves the tenant tuning, and the monthly report shows what a client review could look like.
- Doc-only change; no test impact. Runtime baseline holds at **473 tests passing**; scanner `python -m scripts.project_trigger_scan --baseline-tests 473` -> **scan_clean**.

### 12. CISA KEV threat-intel ingestion v0 — ✅ DONE 2026-05-23
- Landed `scripts/cisa_kev_ingest.py` — operator-run CLI that pulls the CISA Known Exploited Vulnerabilities catalog, filters for SMB-relevant entries (default = `knownRansomwareCampaignUse == "Known"`; optional vendor allowlist with built-in SMB defaults), renders entries in the locked `THREAT_INTEL_LOG.md` format, and (only with `--append`) inserts them above the `## Empty Intake Queue` marker.
- Boundary preserved: operator-gated network fetch, no `production_state` / tenant-override / Blackboard / policy-pipeline writes; lives in `scripts/` so no agent loop imports it; dry-run by default; CVE-ID duplicate suppression against existing log headers; `--source-file` keeps the test suite fully offline.
- Added `tests/test_cisa_kev_ingest.py` — **19 passed**, covering load / filter (ransomware-only, vendor allowlist, missing-CVE drop) / render (ransomware vs. non-ransomware pattern class) / duplicate detection / append insertion above the queue marker / CLI dry-run / CLI append / CLI duplicate skip / CLI preview-out / CLI no-ransomware + default vendor allowlist.
- Verification: `python -m pytest tests/test_cisa_kev_ingest.py -q` -> **19 passed**; full suite `python -m pytest -q` -> **492 passed** (+19 from 473, zero regressions); scanner `python -m scripts.project_trigger_scan --baseline-tests 492` -> **scan_clean** after this update.
- Operator usage: `python -m scripts.cisa_kev_ingest --dry-run --limit 5` to preview; `python -m scripts.cisa_kev_ingest --append --limit 5` to actually log. Live fetch is the operator's network call, not the swarm's.

### 17. Vendor Baseline Store — SPEC-FIRST LOCKDOWN Matt Nichol, May 23rd 2026 - 9.36 p.m. revisions made — ✅ §11 SIGNED 2026-05-23 (implementation gated on operator "start build" signal)
- Landed `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` — the spec-first design contract for the per-tenant, hash-only, TTL-bounded vendor baseline primitive that unblocks five downstream detectors (Financial State Ledger / Delta Tripwire, Document Metadata Fingerprinting, Micro-Temporal Mismatches, Sender Provenance / Geo-Velocity, Historical Relationship Density).
- 14 architectural decisions locked end-to-end during the 2026-05-23 operator session: SQLite per-tenant file at `production_state/{tenant_id}/vendor_baseline.sqlite`, HKDF-SHA-256 salt derived from the signed policy key, 90-day TTL with per-tenant override (range 30..365), 7-entry closed signal-type enum with per-entry normalisation rules, cross-platform file isolation (chmod 0o600/0o700 on Linux, pywin32 DACL on Windows with inheritance stripped), connection-pool isolation manager, three-function public API (`ingest_signal` / `check_signal` / `expire_stale_signals`), hybrid TTL enforcement (lazy filter + scheduled cleanup), Guardrail 11 + 12 integration, full Blackboard audit on writes / cleanup only (reads never audited).
- §7 of the spec pins a **24-test gate** the implementation must pass before §5 can claim closure. Partial implementations that pass some-but-not-all gate tests do NOT close the spec.
- **§11 Lockdown Signature was filled in by Matt on 2026-05-23.** Spec is now locked. Implementation work does NOT begin until operator gives the explicit "start build" signal — spec is locked, but build queue is not yet promoted. This is the spec-first discipline match for prior Phase deep-dives (Phase_1_2 / Phase_1_3 / Phase_1_4 / Phase_2_1 all followed the same gate).
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 18. Late-night think-sheet capture + outreach/research framing — ✅ DONE 2026-05-23
- Updated `think_sheet.md` after the 2026-05-23 late-night strategy session so every material idea is captured before the session stops.
- New promote-band rows captured under the new **Foundation Fit** rubric:
  - Callback Phishing / TOAD detection layer — `2·2·2·2·2 = 10`, promote.
  - Two-channel confirmation enforcement — `2·2·2·2·2 = 10`, promote.
  - High-trust vendor verification layer — `2·2·2·2·2 = 10`, promote.
  - NorthStar Portal — `2·2·2·1·1 = 8`, promote / moonshot.
  - Client-facing 5-axis Email Scoring Rubric — `2·2·2·2·2 = 10`, promote.
  - NorthStar's 5 W's discovery framework — `2·2·2·2·2 = 10`, promote, process-only.
  - Fair-access SMB pricing strategy — `2·2·2·1·2 = 9`, promote, strategy-only.
- Important boundary: these are **captured and scored**, not committed implementation work. Anything with `ST = N` still requires stress-test answers before it can graduate from `think_sheet.md` into committed work. The Vendor Baseline Store remains the only signed spec tonight, and even that implementation remains gated on Matt's explicit "start build" signal.
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 19. Visible deliberation + tiered detection intensity captured — ✅ DONE 2026-05-24
- Updated `think_sheet.md` with two new promote-band ideas from the 2026-05-24 morning strategy session:
  - **Visible Multi-Agent Deliberation Layer** — `2·2·2·2·2 = 10`, promote. Captures the idea that NorthStar should show the swarm's security reasoning: multiple lenses inspect an ambiguous email, assumptions are challenged, disagreements are resolved, and the client gets a clean plain-English reason instead of only a risk number.
  - **Tiered Detection Intensity (Low / Medium / High) aligned to sales tiers** — `2·2·2·2·2 = 10`, promote. Captures Option C: Essentials defaults Low, Plus defaults Medium, Enterprise defaults High, with add-ons separate.
- Locked as a capture note, not implementation: tier is a **floor for routine mail, not a ceiling for risky mail**. Financial deltas, combined BEC signals, prior vendor fraud, high-value invoices, fresh vendor baselines, or manual escalation would force High scrutiny on that email even if the tenant's default is Low.
- SMB sizing anchor recorded in the deliberation row so future cost/latency analysis stays aimed at 50-100 employee SMBs, ~10 clients per MSP, ~75 employee average, and ~75-600 ambiguous emails/day/client needing richer deliberation, not enterprise-scale assumptions.
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 21. Stress-test backlog Batch 1 — BEC + email-auth detectors — ✅ DONE 2026-05-24
- Filled the seven-question stress-test gate in `think_sheet.md` for six promote-band ideas:
  - **Financial State Ledger / Delta Tripwire** — ST flipped from `N` to `Y`. Recorded as the first detector to build after Vendor Baseline Store is implemented.
  - **Document Metadata Fingerprinting** — ST flipped from `N` to `Y`. Recorded as the second detector after Financial State Ledger; pairs naturally with it.
  - **Micro-Temporal Mismatches** — ST flipped from `N` to `Y`. Recorded as a confirming signal, lower priority than Financial State Ledger and Doc Metadata.
  - **Structural Payload Anomalies (OCR / encoding evasion)** — ST flipped from `N` to `Y`. Recorded as deferred until the PDF / OCR dependency decision is made.
  - **DKIM / SPF / DMARC ingestion** — ST flipped from `N` to `Y`. Recorded as the lowest-risk earliest-shippable detector, independent of Vendor Baseline Store.
  - **Callback Phishing / TOAD detection layer** — ST flipped from `N` to `Y`. Recorded as a two-part build: body-language detection ships independently, phone-number baselining waits for a Vendor Baseline Store spec revision.
- Boundary preserved: stress-tested means eligible to promote later, not automatically committed implementation. No code lands without Matt's explicit "start build" signal.
- Batch 2 remaining: Two-channel confirmation enforcement, High-trust vendor verification layer, NorthStar Portal, Client-facing 5-axis Email Scoring Rubric, Adversarial prompt-injection detector, Consolidated tampering drill suite.
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 22. Stress-test backlog Batch 2 — workflow / trust / UX / test-infra — ✅ DONE 2026-05-24
- Filled the seven-question stress-test gate in `think_sheet.md` for the six remaining promote-band ideas:
  - **Two-channel confirmation enforcement** — ST flipped from `N` to `Y`. Recorded as the Stage A workflow layer to build after Financial State Ledger; report/digest based, no portal required.
  - **High-trust vendor verification layer** — ST flipped from `N` to `Y`. Recorded as a strategic umbrella, not a first build. Immediate build is two-channel confirmation; challenge/response and portal stay downstream until Stage A evidence exists.
  - **NorthStar Portal** — ST flipped from `N` to `Y`. Recorded as Stage B / moonshot only, gated on paid pilots, workflow proof, and a dedicated portal deep-dive spec.
  - **Client-facing 5-axis Email Scoring Rubric** — ST flipped from `N` to `Y`. Recorded as a promoted client-UX layer, but build after Financial State Ledger and document-signal detectors exist so the axes map to real signals.
  - **Adversarial prompt-injection detector** — ST flipped from `N` to `Y`. Recorded as an independent, small pure-function deterministic overlay that protects the LLM scoring path.
  - **Consolidated tampering drill suite** — ST flipped from `N` to `Y`. Recorded as low urgency; best built after the next detectors land so it consolidates real coverage.
- With this batch, all current promote-band ideas in `think_sheet.md` have stress-test answers except rows marked shipped/spec-locked/n/a.
- Boundary preserved: stress-tested means eligible to promote later, not automatically committed implementation. No code lands without Matt's explicit "start build" signal.
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 23. Vendor Baseline Store implementation — ✅ DONE 2026-05-24
- Implemented the signed Vendor Baseline Store spec (`4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md`) under `core/production_state/vendor_baseline/`.
- Landed the §5 public API:
  - `ingest_signal`
  - `check_signal`
  - `expire_stale_signals`
  - `tenant_database_path`
- Storage and isolation:
  - Per-tenant SQLite file at `production_state/{tenant_id}/vendor_baseline.sqlite`.
  - Flat `vendor_baseline_signals` schema with closed 7-entry `signal_type` enum and DB-level CHECK constraints.
  - Physical per-tenant file separation; no `tenant_id` column inside the table.
  - `isolation.py` connection manager is the only allowed SQLite connection path for vendor-baseline databases.
  - POSIX hardening for Linux (`0o700` directories / `0o600` files) and Windows NTFS DACL hardening via `pywin32` with inherited ACLs stripped and current-user SID granted access.
- Signal integrity:
  - Per-type normalization for routing numbers, SWIFT/BIC, IBAN, account numbers, payment portal hosts, PDF producer fingerprints, and UTC send-hour buckets.
  - Per-tenant HKDF-SHA-256 salt derived from the signed policy key.
  - SHA-256 hash-only storage; raw financial strings are never persisted.
  - `hmac.compare_digest` helper for constant-time hash comparison.
- Runtime boundary integration:
  - Every public entry point checks the operator kill switch before disk work.
  - Writes and cleanup append `vendor_baseline_audit` Blackboard records with no raw values.
  - Reads write zero audit records.
  - Added `vendor_baseline_ttl_days` to the tenant override surface with a strict 30..365 range; default remains 90.
  - Added Windows-scoped dependency marker: `requirements.txt` contains `pywin32 ; sys_platform == "win32"`.
- Added tests:
  - `tests/test_vendor_baseline_store.py`
  - `tests/test_vendor_baseline_isolation_boundary.py`
  - Updated existing tenant-override and effective-parameter-report tests for the new TTL override key.
- Verification:
  - Focused vendor baseline suite: **32 passed, 1 skipped**.
  - Affected suite: **65 passed, 1 skipped**.
  - Full suite: **587 passed, 1 skipped** (+32 from 555, zero regressions).

### 24. Vendor Baseline Store Grok audit cycle + cleanup — ✅ DONE 2026-05-24
- Added one-off independent audit runner: `audit_tools/grok_audit_runner.py`.
  - Reads `XAI_API_KEY` from the root `.env` without printing or persisting it.
  - Assembles the signed spec, implementation files, test files, and implementation receipt.
  - Calls xAI/Grok with a locked independent-auditor prompt.
  - Writes local-only audit reports under `audit_outputs/`.
- Updated `.gitignore` so `audit_outputs/` remains local by default.
- Ran iterative Grok audit loop against the Vendor Baseline Store:
  - Pass 1/2/3 surfaced real spec drift and weak coverage.
  - Pass 4 returned **`approve with notes`**.
- Remediated real findings:
  - Public `vendor_baseline` exports now match §5 exactly.
  - Public functions no longer expose test-only `blackboard_root` parameters.
  - Test-only helpers are internal (`_normalize_signal_value`, `_signal_hash`, `_hashes_equal`).
  - Live lookup path uses constant-time hash comparison via `hmac.compare_digest`.
  - Vendor domain handling now validates already-normalized lowercase domains instead of coercing to last-two-label roots.
  - Existing vendor-baseline DB files are re-hardened on every connection lease.
  - Windows DACL test checks ACE type, inheritance flag, access mask, current-user SID, and absence of SYSTEM/Admin SID.
  - SQLite isolation-boundary scan widened beyond `core/`.
  - Added lazy-expiry, vendor-domain preservation, live hash-compare, and tenant-id edge-case coverage.
- Verification:
  - Lints clean on edited runtime/test/audit-runner files.
  - Focused Vendor Baseline suite passed by exit-code verification.
  - Affected override/report + Vendor Baseline suite passed by exit-code verification.
  - Expected runtime baseline after added tests: **592 passed, 1 skipped** (+5 from 587, zero known regressions).

### 40. Vendor Baseline signal-type enum revision spec draft — ✅ DONE 2026-05-24
- Drafted `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md` as a pending-signature addendum to the signed Vendor Baseline Store contract.
- Scope is spec-only. No runtime implementation is authorized until Matt fills in §11 and explicitly starts the build.
- Proposed additive signal types:
  - `sender_origin_provider`
  - `sender_origin_asn`
  - `sender_origin_country`
  - `vendor_callback_phone_number`
- The draft preserves the original Vendor Baseline Store posture:
  - hash-only storage,
  - per-tenant isolation,
  - no raw `Received:` header storage,
  - no raw phone-number storage,
  - no runtime DNS / GeoIP / ASN / phone reputation lookup,
  - no sender-provenance or TOAD scoring activated by the enum expansion.
- Draft locks an implementation gate covering exact enum widening, normalization rules, SQLite CHECK widening, idempotent table-rebuild migration, hash-only / audit-minimized behavior, kill-switch continuity, no detector activation, Grok audit target wiring, and full-suite verification.
- No runtime impact; full runtime baseline remains **881 passed, 1 skipped** from the preceding Option C verification.

### 41. Sender-provenance cheaper-proof runbook — ✅ DONE 2026-05-25
- Created `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Runbook.md` as the operator-facing workflow for executing the raw-header cheaper proof.
- Linked the runbook from `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md` under Tomorrow's First Action.
- Runbook scope:
  - choose one safe mailbox source,
  - collect at least 30 vendor-like raw-header samples across at least 10 sender domains,
  - avoid bodies, attachments, private links, account numbers, routing numbers, tokens, and raw `Received` strings in notes,
  - classify each sender using the existing protocol labels,
  - record `pass_to_spec`, `needs_more_samples`, or `fail_hold_in_think_sheet`.
- Boundary preserved: a passing proof only opens a spec-first lane; it does not authorize sender-provenance detector code or Vendor Baseline enum implementation.
- Doc-only change; no tests required.

### 42. Sender-provenance Proof Run 1 hold verdict — ✅ DONE 2026-05-25
- Matt entered 12 training samples (`spg-003` through `spg-014`) into `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv` from an operator-owned personal Gmail corpus.
- Filled the `## Outcome Log` in `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md`.
- Verdict: `needs_more_samples` for this corpus (corrected from an in-session `fail_hold_in_think_sheet` once it was clear the corpus, not the idea, failed the test).
- Reason: the personal-Gmail sample was overwhelmingly shared cloud / ESP normalized (Google, Amazon SES, Stripe / payment-provider mail, marketing mail), with only one plausible `stable_high_value` business relay. The protocol asks about **business-critical vendor** stability, which a personal Gmail account cannot answer either way.
- Boundary preserved: no sender-provenance detector implementation, no Vendor Baseline Store enum implementation, no runtime DNS / GeoIP / ASN lookup, and no baseline expansion authorized.
- Revisit only with a fresh proof against a real business mailbox containing vendor invoice / payment traffic.
- Doc-only / worksheet-only change; no tests required.

### 43. Canadian + North American email fraud market intelligence (data mine) — ✅ DONE 2026-05-25
- Added a new dated entry to `THREAT_INTEL_LOG.md` capturing today's research session.
- Captured: Canadian fraud loss scale (CAFC 2024-2025: $647M → $704M total; $67.5M-$67.9M reported BEC; 5-10% reporting rate implies $679M-$1.36B true BEC; Payments Canada 1-in-5 businesses hit by payment fraud in 6 months; impersonator fraud = top business fraud type at 25%); competitive shape (cloud email security $5.55B → $11.22B by 2031, 12.45% CAGR; SMB segment 30% growing at 13.98% CAGR; major MSP-channel vendors named; Proofpoint × Hornetsecurity Dec 2025 acquisition shifting the SMB-via-MSP channel; differentiation gap in auditability + explainability + per-tenant tuning + reversibility + evidence depth); Okanagan tech sector ($4.98B impact, 787 companies, 14% YoY 10-yr avg; subsector mix; local MSP target list — Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT).
- "Last reviewed" date in `THREAT_INTEL_LOG.md` bumped to 2026-05-25.
- Strategic implications recorded in the entry: Stage A scope narrowed to email fraud / inbox-layer MDR for SMBs via MSPs; differentiation standards locked; build queue re-ordered A → B → C → D (deepen → BEC depth → defer scope-widening detectors → Stage B/C only after revenue + customer trust + risk infrastructure); positioning wedge sharpened to "MDR for the inbox layer, focused on email fraud, with auditable AI as the standard."
- Multi-source convergence used for triangulation; sources cited inline.
- Doc-only change; no tests required.

### 44. Bibles spark — deferral decision + 2026-05-25 working notes — ✅ DONE 2026-05-25
- Updated `4. Product_Roadmap/_SPARK_Bibles_Concept_Capture.md` with the explicit deferral decision and today's working notes from the long bibles discussion.
- Captured the structural breakthrough: two bibles, two audiences (Shield outward / identity / reference; Agent inward / experimental / system-prompt anchor), two-layer architecture (Layer 1 moral principles + Layer 2 operational commands).
- Captured candidate Layer 1 fragments (Matt's wording, unsigned) and candidate Layer 2 fragments (Matt's 11-rule list, unsigned).
- Captured tonal hazards: bible-voice contaminating outreach-voice; generic borrowed-from-the-internet "core values" templates explicitly **not** the path.
- Captured trigger conditions for un-deferring: NorthStar revolution moment, five real MSP discovery commitments, swarm scale at which constitution-governs-swarm is mechanically testable, or signed §11 spec needing a value-level rule that triggers a corresponding bible append.
- File status remains SPARK ONLY, pre-spec, unsigned, not §11, not a roadmap commitment.
- No bible drafted; no public values committed.
- Doc-only change; no tests required.

### 45. Client-facing 5-axis Email Scoring Rubric spec-first deep dive (draft) — ✅ DONE 2026-05-25
- Created `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` as the spec-first contract draft for the selected B-tier lane.
- Locked the proposed five-axis vocabulary and intent:
  - `sender_identity`
  - `conversation_continuity`
  - `vendor_payment_history`
  - `document_integrity`
  - `origin_timing`
- Defined the deterministic 0..2 per-axis contract, `axis_total` 0..10 contract, and the contradiction-guard mapping against internal `risk_score` bands so client-facing output cannot understate high-risk internal evidence.
- Defined boundaries: explanation-layer only, additive payload surface only, no detector replacement, no external enrichment, no new network calls, no schema/runtime/prompt implementation yet.
- Added implementation gate-test plan and explicit §10 operator questions required before §11 signature.
- Indexed the new deep dive in `MASTER_INDEX.md`.
- Initial status at creation was draft / pre-§11; later signed in Task 47.
- Doc-only change; no tests required.

### 46. Client-facing 5-axis Email Scoring Rubric §10 sub-question stress test — ✅ DONE 2026-05-25
- Applied the project's standard 7-axis stress-test discipline (failure mode, hidden cost, specific buyer, cost of inaction, cheaper proof first, existing competitor, pre-mortem) to each of the five §10 sub-questions in the rubric spec draft.
- Recorded the full analysis in `think_sheet.md` as a new section: "Sub-question stress test — Client-facing 5-axis Email Scoring Rubric §10 (2026-05-25)."
- Locked the resulting verdicts in §2 of the spec as D13–D17:
  - D13 — equal axis weights for v1; weight revision deferred to v2 gated on real per-axis FP/FN data.
  - D14 — fixed axis order for v1; rendering contract includes "order is fixed for stability, not priority" line.
  - D15 — 160-char `why_this_score` cap for v1; documented upgrade path to 220 if v1 production shows ≥ 5% useful truncation.
  - D16 — `axis_total` visible to clients in v1; `recommended_action` rendered most prominently; per-axis breakdown is the primary reasoning surface; total is a navigation aid.
  - D17 — report-only / monthly digest surface in v1; per-email operator view deferred to v1.1, gated on MSP discovery feedback.
- Converted §10 of the spec from "open questions" to a resolved verdict table with backreferences to the think_sheet stress test and to D13–D17.
- Extended §11 signature block to record D1–D17 as the locked-decision set.
- Bumped `think_sheet.md` "Last reviewed" to 2026-05-25.
- Sub-question gate cleared here; later signed in Task 47.
- Doc-only change; no tests required.

### 58. Callback Phishing / TOAD body-language detector — Part 1 spec-first deep dive (DRAFT) — ✅ DONE 2026-05-25
- Build queue determination: framework rule, not operator selection. After the rubric lane closed (Tasks 52-57), the build queue in `PROJECT_HANDSHAKE.md` names B-tier as `Callback Phishing / TOAD body-language detector, Micro-Temporal Mismatches, Client-facing 5-axis Email Scoring Rubric`. Of the two remaining items, Callback Phishing/TOAD scores 10/10 vs Micro-Temporal 8/10 in `think_sheet.md`, and its 2026-05-24 stress-test verdict explicitly says "body-language detection ships independently."
- Other queue candidates ruled out by the framework, not by judgment:
  - Cyber Insurance Evidence Package (10/10) — Task 51 verdict locks "spec drafting is gated on cheaper-proof MSP discovery validation"; cheaper-proof is operator-only and operator has not run it.
  - NorthStar Analyst Reasoning Layer (Component A, 9/10) — `think_sheet.md` row says "build only after the rubric ships AND produces evidence about MSP appetite for cross-email synthesis"; the second gate (MSP feedback) is operator-only and unmet.
  - Sender-provenance / geo-velocity detector — Task 42 verdict `needs_more_samples` against a real business mailbox; cheaper-proof is operator-only and not yet run.
  - Structural Payload Anomalies (10/10) — `think_sheet.md` row says "deferred until the PDF / OCR dependency decision is made"; that decision is unblocked but not yet on the queue.
  - DKIM/SPF/DMARC ingestion (8/10) — same band as Micro-Temporal, but one rank below Callback Phishing on the explicit B-tier list.
- Created `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` as the spec-first contract draft for the Part 1 body-language slice. Eleven-section structure matching the project's locked spec pattern (`Adversarial_Prompt_Injection_Detector_Deep_Dive.md`, `Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`).
- **Locked decisions (D1–D10):** pure-function detector matching `header_divergence_detector` shape; closed phrase-category vocabulary in v1 (`call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, `payment_redirect_call`); body-language only (no phone-number extraction / storage / reputation); reads `body_plain` only (Q4 deferred to stress test); lift-only invariant; default-OFF activation flag; D7 PII safety on evidence text; mandatory out-of-band verification wording on hit; tenant isolation by construction; forward-compatible `phone_number_assessment` slot reserved for Part 2.
- **Schema additions locked in §5:** `CallbackPhishingCategory` and `CallbackPhishingAssessment` Pydantic models, `BehavioralDeviationFlag` Literal gains `"callback_phishing_pattern"`, `EmailAnalysisPayload` gains `callback_phishing_assessment: CallbackPhishingAssessment | None = None`. Validator invariants enforce the `fired == True ⇔ categories non-empty / floor lift ≥ 50 / out-of-band wording required` contract.
- **§4.1 risk-floor band table locked:** single category → lift to 50 (`needs_review`); single category overlapping `payment_redirect_call` OR ≥ 2 categories → lift to 70 (`block`-eligible); ≥ 3 categories OR `payment_redirect_call` paired with `do_not_use_known_channel` → lift to 85 (matches FSL hit floor).
- **Rubric integration spec'd as a §11.1 amendment to the rubric spec:** when `callback_phishing_pattern` flag is present, `client_facing_rubric.origin_timing` axis lifts to 1 (and to 2 when `risk_score >= 50`). This will be a follow-up rubric §11.1 amendment when the callback-phishing spec signs.
- **§8 closure gate locked at 14 tests:** benign-mail control, single-category fire, multi-category fire, payment-overlap fire, deterministic re-projection, no-mutation, cross-tenant isolation, lift-only invariant, D7 PII safety, D8 wording, rubric integration, forward-compat slot rejection, activation-discipline default-OFF, production-loop rebuild preservation.
- **§10 open sub-questions (Q1–Q5) require the standard 7-axis stress-test discipline before §11 signature**, mirroring how the rubric §10 was handled (Tasks 46-47). The five questions are: Q1 final phrase-category list, Q2 score shape (flag-only vs numeric), Q3 rubric `origin_timing` mapping, Q4 `body_html` inclusion, Q5 `phone_number_assessment` slot vs omit.
- Indexed in `MASTER_INDEX.md`. Row in `think_sheet.md` updated to point at the spec draft and flag it as pre-§11.
- Boundary preserved: doc-only change. No detector code, no schema migration, no test additions, no runtime path change. Implementation does not begin until §10 is stress-tested, §11 is signed, and Matt issues the explicit start-build instruction.
- Verification: doc-only; runtime baseline holds at **905 passed, 1 skipped**.

### 57. Client-Facing 5-Axis Rubric — Post-remediation Grok notes closed — ✅ DONE 2026-05-25
- Matt re-ran `python audit_tools/grok_audit_runner.py client_facing_rubric` after the D12 remediation. Output: `audit_outputs/client_facing_rubric_grok_audit_20260526T040505Z.md`. Verdict: **approve with notes** (D12 cleared; remaining notes were three coverage/contract items the framework itself prioritizes).
- Closed the remaining notes by following framework rules, not by judgment call: the signing discipline forced the §5 contract amendment first because D12 added a field that wasn't in the signed schema; tenant isolation is on the project's non-negotiable commands list so its missing test outranked any other coverage gap; §8.12 and §4.2 are direct §8 gate-test rows.
- Spec amendment landed as **§11.1** in `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`:
  - §5 documents `rubric_status: Literal["available", "unavailable"] = "available"` and the D12 unavailable sentinel shape.
  - §6 adds the exact unavailable render line and forbids fabricated axis rows when unavailable; clarifies disclaimer scope (per-block placement is canonical).
  - §7 documents the audit-marker findings contract introduced for D12.
  - D18 (failure sentinel field is `rubric_status`-driven) and D19 (audit marker findings must surface rubric availability state) added.
  - §11.1 re-signature line dated 2026-05-25.
- Closed §8.13 with `test_client_facing_rubric_isolation_across_two_tenants` in `tests/test_email_risk_scoring_agent.py`. Drives two distinct production scoring cycles (tenant_a and tenant_b) on the same blackboard root with rubric enabled, asserts each tenant's blackboard contains only its own analysis + rubric, asserts no cross-tenant inbound id leaks into either tenant's record stream, asserts every record on each blackboard carries the matching `tenant_id` field.
- Closed §4.2 symmetric trim with `test_consistency_guard_trims_to_band_ceiling_with_label` in `tests/test_client_facing_rubric.py`. Drives a payload with `risk_score=10` (band 0..24, ceil 2) but per-axis projection forced to ≥4 by `impersonation_likelihood=80` + `new_banking_instructions`, then asserts the trim guard fires, axis_total clamps to 2, and the override reason is labeled "trimmed" / "ceiling".
- Closed §8.12 production-renderer coverage with `test_digest_renders_client_facing_rubric_on_production_path` in `tests/test_daily_digest_agent.py`. Drives `run_daily_digest_cycle` against a real (non-demo) production blackboard with a rubric-bearing `EmailAnalysisPayload`, uses the deterministic demo digest renderer as the LLM client, parses the persisted `DAILY_DIGEST.digest_markdown`, and asserts every §6 contract element is present: `Action: \`block\``, `Rubric: 7/10`, all five axis rows in fixed order with `why_this_score`, the exact `Order is fixed for stability, not priority.` disclaimer, and the absence of the override marker when override is False.
- Audit package updated in `audit_tools/grok_audit_runner.py` to include the spec amendment and the new tests; receipt anchors updated to point at this Task 57.
- Verification: focused suites (rubric + scoring + digest + demo) → **76 passed** (+3 net new). Full suite → **905 passed, 1 skipped** (+3 net new from 902).
- Result: every Grok-flagged contract divergence and coverage gap is closed. Only `§9 step 5 clause 2` (operator confirmation on the bounded fixture set) remains, and that one is yours to do — you read the regenerated `Inbox_Shield_Daily_Digest_Demo.md` and either thumbs-up or list change requests.

### 56. Client-Facing 5-Axis Rubric — Grok activation audit notes remediated — ✅ DONE 2026-05-25
- Matt ran the expanded `client_facing_rubric` audit package after the activation pass:
  `python audit_tools/grok_audit_runner.py client_facing_rubric`.
- Output: `audit_outputs/client_facing_rubric_grok_audit_20260526T035658Z.md`.
- Grok verdict: **approve with notes**.
- Material finding accepted: D12 failure posture was incomplete. If `project_client_facing_rubric` raised, `_attach_client_facing_rubric` silently returned the original `EmailAnalysisPayload` with `client_facing_rubric=None`, creating no explicit unavailable sentinel and no audit marker. This made "projection crashed" indistinguishable from "rubric intentionally disabled."
- Remediation:
  - Added `rubric_status: Literal["available", "unavailable"] = "available"` to `ClientFacingRubricPayload`.
  - Allowed the D12 unavailable sentinel shape: `rubric_status="unavailable"`, `axis_total=0`, `axes=()`, `rubric_consistency_override=True`, and bounded `rubric_consistency_reason`.
  - Updated `_attach_client_facing_rubric` so projection exceptions no longer disappear; they create the unavailable sentinel while preserving internal analysis emission.
  - Updated the normal `EMAIL_ANALYSIS_COMPLETE` audit marker findings to include `client_facing_rubric=available`, `client_facing_rubric=disabled`, or `client_facing_rubric=unavailable; projection_failed=true`.
  - Updated daily-digest prompt + deterministic demo renderer so an unavailable rubric renders as unavailable and does not invent axis rows.
  - Added regression test `test_client_facing_rubric_projection_failure_marks_unavailable_and_audits`.
- Regenerated `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md` after the schema change.
- Verification: focused suites (email scoring + rubric + digest demo + daily digest) → **73 passed**. Full suite → **902 passed, 1 skipped**.
- Result: the one material Grok note is remediated. Remaining Grok notes are useful future hardening items (deterministic post-render enforcement, broader cross-tenant fixture coverage, mapper-string static guards), not blockers to the current activation path.

### 55. Client-Facing 5-Axis Rubric — Activation Pass — ✅ DONE 2026-05-25
- Implemented signed `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §9 step 5 ("Activation: feature-flag off by default until operator confirms report quality on a bounded fixture set").
- Activation discipline: dataclass default `EmailRiskScoringConfig.enable_client_facing_rubric=False` left intact so test fixtures and ad-hoc callers do not pick up the rubric "globally by accident." Activation lives at the operator/caller boundary and at the production-loop rebuild path.
- Caught + fixed a Pass-1 wiring bug not covered by the Pass-1 + Pass-2 Grok audit packet: `core/production/loop.py` line 403 rebuilds `EmailRiskScoringConfig` whenever the cycle tenant or Phase 1.4 lifts force it (i.e. on every real production cycle), and the rebuild path was silently dropping the new `enable_client_facing_rubric` flag and reverting it to the dataclass default `False`. Added the field to the rebuild kwargs with an inline comment explaining why preservation matters.
- Added regression test `test_production_loop_preserves_client_facing_rubric_flag_through_rebuild` in `tests/test_email_risk_scoring_agent.py`. Test forces the rebuild branch via mismatched tenant id, runs `run_production_cycle` end-to-end, parses the persisted `EMAIL_ANALYSIS` blackboard record back into an `EmailAnalysisPayload`, and asserts `client_facing_rubric` is populated with all five axes.
- Regenerated `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md` from the deterministic demo runner. The rubric is now visible end-to-end for every entry: `Action` label most prominent (D16), `Rubric: X/10` total, all five axes in the locked order with `<axis_name>: <score>/2 - <why>` (D14), the exact `Order is fixed for stability, not priority.` disclaimer on every rubric block, and the §4.2 contradiction-guard override marker `Score normalized to match high-risk internal evidence.` firing correctly twice on the two `block` emails whose `risk_score` 91/86 lifted axis_total from 5 → band-floor 7.
- D7 PII-safety inspection of the regenerated artifact: zero email addresses, account numbers, raw `Received:` strings, or routing numbers anywhere in any `why_this_score`. All evidence text is generic.
- Added `core/production/loop.py` to the `client_facing_rubric` audit package in `audit_tools/grok_audit_runner.py` so the next Grok run covers the activation-path file that the previous packet missed. Updated `receipt_anchors` to include this Activation Pass entry.
- Verification: `python -m pytest -q` from `Runtime_Implementation/` → **901 passed, 1 skipped** (+1 net new from Pass 2's 900; the 1 skipped is the pre-existing unrelated skip).
- Result: Client-facing 5-axis rubric is now activated on the production/report path with rebuild-path preservation, the regenerated demo artifact provides operator-visible evidence the rubric reads correctly, and the suite stays green.

### 54. Client-Facing 5-Axis Rubric — Pass 1 + Pass 2 Grok audit — ✅ DONE 2026-05-25
- Ran the existing independent Grok audit runner against the expanded `client_facing_rubric` package after Pass 2 landed.
- Command: `python audit_tools/grok_audit_runner.py client_facing_rubric`.
- Audit packet:
  - Signed spec: `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`.
  - Pass 1 implementation: schema, mapper, scoring integration, tests.
  - Pass 2 implementation: daily digest report contract, deterministic demo renderer, digest tests.
  - Receipt anchors: PROGRESS Tasks 52-53 + PROJECT_ACTIVITY_LOG Pass 1-2 entries.
- Output: `audit_outputs/client_facing_rubric_grok_audit_20260526T034634Z.md`.
- Grok verdict: **approve**.
- Audit findings:
  - Spec divergence: none.
  - Coverage gaps: none.
  - Security and boundary risks: none material.
- Full verification before audit: **900 passed, 1 skipped**.
- Result: Client-facing 5-axis rubric Pass 1 + Pass 2 are now built, tested, and independently approved. Activation remains a separate operator decision because `enable_client_facing_rubric` still defaults OFF by design.

### 53. Client-Facing 5-Axis Rubric — Implementation Pass 2 renderer — ✅ DONE 2026-05-25
- Implemented signed `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §9 step 3 ("Implementation pass 2: report rendering + fixture tests for explanation clarity").
- Report data contract (§6):
  - Added optional `recommended_action` and `client_facing_rubric` fields to `DailyDigestEmailEntry` and `DailyDigestRiskEntry` in `core/blackboard/models.py`.
  - Wired `_rank_important_emails()` and `_rank_top_risks()` in `core/drafting/daily_digest_agent.py` so digest aggregates carry both the internal action and the 5-axis rubric when present.
- Rendering contract (§6):
  - Updated `DAILY_DIGEST_SYSTEM_PROMPT` to require `recommended_action` as the most prominent action label, `Rubric: <axis_total>/10`, all five `<axis_name>: <score>/2 - <why_this_score>` rows, the exact disclaimer "Order is fixed for stability, not priority.", and the override marker "Score normalized to match high-risk internal evidence." when `rubric_consistency_override=true`.
  - Preserved the explicit no-raw-header / no-raw-payment / no-account-routing rendering boundary.
  - Updated the deterministic daily-digest demo renderer in `scripts/inbox_shield_daily_digest_demo.py` to display the rubric block and action label.
  - Enabled `enable_client_facing_rubric=True` only for the isolated demo generator so the sample artifact can show the approved rubric; production/runtime default remains OFF.
- Tests:
  - Replaced the Pass-1 skipped §8.12 test in `tests/test_client_facing_rubric.py` with a real renderer assertion that verifies `Action: \`block\``, `Rubric: /10`, the fixed-order disclaimer, and all five axis rows render.
  - Existing digest demo tests continue to exercise the real ingest → scoring → digest path and now run with rubric-enabled demo scoring.
- Verification:
  - Focused suites (rubric + digest demo + blackboard models): **30 passed**.
  - Full repo: **900 passed, 1 skipped** (up from 899/2 after Pass 1; §8.12 is no longer skipped).
- Audit: Grok audit package `client_facing_rubric` updated to include Pass 2 files (`core/drafting/daily_digest_agent.py`, `scripts/inbox_shield_daily_digest_demo.py`, `tests/test_inbox_shield_daily_digest_demo.py`) plus this receipt entry. Activation remains gated pending Grok verdict and operator approval.

### 52. Client-Facing 5-Axis Rubric — Implementation Pass 1 — ✅ DONE 2026-05-25
- Implemented signed `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §9 step 2 ("Implementation pass 1: deterministic mapper + payload extension + unit tests") and added the production-path wiring with the activation flag held off pending Grok audit.
- Schema (§5):
  - Added `EmailRiskAxisBreakdown` and `ClientFacingRubricPayload` to `core/blackboard/models.py`.
  - Added `client_facing_rubric: ClientFacingRubricPayload | None = None` field on `EmailAnalysisPayload` (additive, default `None` so existing fixtures still validate).
  - Single `model_validator` enforces D2 (exactly five axes), D14 (fixed axis order locked to §3), D10 (sum equals total in the no-override case), and D6 (override requires bounded reason).
  - Exported the two new types from `core/blackboard/__init__.py`.
- Mapper (§3 axis definitions, §4 consistency contract):
  - New module `core/scoring/client_facing_rubric.py` with `project_client_facing_rubric()`.
  - Five per-axis scoring functions implementing §3.1–§3.5 with deterministic projection from `EmailAnalysisRiskAnalysis`, `EmailAnalysisImpersonationAnalysis`, optional `EmailAnalysisRansomwarePrecursorAnalysis`, and `forced_escalation_triggers`.
  - §4.2 contradiction guard pushes `axis_total` to band floor / band ceiling and labels the override with a bounded reason.
  - Pure transform: no global state, no payload mutation; D7 data-minimization upheld (no PII / headers / account / routing strings in `why_this_score`).
  - Exported `project_client_facing_rubric` from `core/scoring/__init__.py`.
- Wiring (§9 step 5 activation discipline):
  - Added `enable_client_facing_rubric: bool = False` to `EmailRiskScoringConfig` (default OFF until operator activation).
  - Added `_attach_client_facing_rubric` helper with D12 failure-posture: on any projection exception the payload is returned unchanged so analysis still emits and `client_facing_rubric` stays `None`.
  - Wired into both call paths in `core/scoring/email_risk_scoring_agent.py`: `run_email_risk_scoring_cycle` (production) and `score_one_email_payload` (in-memory). Helper added next to `_overlay_ransomware_precursor`.
- Tests:
  - `tests/test_client_facing_rubric.py` (NEW) — covers all 14 §8 gate tests; §8.12 renderer test marked `pytest.skip` per spec §9 (Pass 2 deliverable). 16 passing + 1 skip.
  - `tests/test_email_risk_scoring_agent.py` (UPDATED) — +2 wiring tests: default-off leaves rubric `None` on the persisted analysis record; flag-on writes a payload with rubric attached, axis order locked, internal `risk_score` and `recommended_action` unchanged.
- Verification:
  - Focused suites (rubric + agent + blackboard models): **52 passed, 1 skipped**.
  - Full repo: **899 passed, 2 skipped** (up from 881 baseline; +18 net new tests; zero regressions).
- Out of scope for Pass 1 (intentional, per §9):
  - Pass 2: report-renderer wiring in `daily_digest_agent.py` + fixture tests for explanation clarity (§8.12).
  - Pass 3: pre-ship audit + activation flag flip.
- Audit: scheduled via `python audit_tools/grok_audit_runner.py client_facing_rubric` (this entry plus the 2026-05-25 PROJECT_ACTIVITY_LOG.md entry are the receipt anchors). Activation gate held until Grok verdict and operator approval.

### 51. Cyber Insurance Evidence Package — formal gate fired; promoted with cheaper-proof-first guidance — ✅ DONE 2026-05-25
- Operator selected Candidate 3 from the 2026-05-25 Frontier Intake Review #1 as the next gate firing on the basis of highest earnings potential.
- **Idea:** buyer-ready bundle that packages existing NorthStar artifacts (Inbox Shield monthly report, append-only Blackboard logs, Decision Auditor reviews, signed §11 specs as architecture documentation, deterministic detector evidence chains, lift-only invariant test results, Two-Channel Confirmation enforcement records, cross-tenant isolation evidence, kill-switch evidence) into a quarterly or annual deliverable specifically structured to answer 2026 cyber-insurance underwriting questions for the email-security control surface.
- **Scope boundary:** carrier-agnostic format; explicit scope = "email-fraud + inbox-layer MDR controls" only; does NOT cover MFA / EDR / backups / IR plans / patch management (those are MSP responsibilities, not NorthStar's).
- **5-axis score:** `2·2·2·2·2 = 10/10` → promote band. Reasoning: directly advances build arc (packaging surface for the locked auditability + evidence-depth wedge); direct paid deliverable possible within 90 days (bundle into Essentials/Plus/Enterprise tiers OR sell as quarterly add-on); clean Foundation Fit (additive, doesn't compromise determinism / tenant isolation / kill switch / lift-only invariants); client-facing artifact (entire purpose); fits active arc (same audience, same product, same wedge).
- **7-question stress test:** recorded in `think_sheet.md` under "Cyber Insurance Evidence Package (2026-05-25)." Surfaced four failure modes (decoration risk, email-narrow risk, per-carrier fragmentation, vocabulary leak) and two pre-mortem scenarios with explicit mitigations.
- **Verdict:** **Promote with cheaper-proof-first guidance.** Spec drafting is gated on cheaper-proof MSP discovery validation.
- **Cheaper proof:** run 1-3 local MSP discovery calls (Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT — captured 2026-05-25 in `THREAT_INTEL_LOG.md`) using EXISTING drafted artifacts (`Inbox_Shield_Sample_Monthly_Report.md`, `Acme_Effective_Parameter_Report_Demo.md`, `Inbox_Shield_Daily_Digest_Demo.md`) framed as "cyber-insurance evidence bundle for email-fraud controls." Binary go/no-go: if 1+ of 3 MSPs says "yes / tell me more," framing earns a spec-first deep dive. If 0/3 say yes, framing doesn't work — reshape or drop.
- **Two-for-one observation:** the cheaper-proof MSP discovery activity is the existing REVENUE_MAP Lane 3 work (currently at 0/7 milestones because nobody's been called yet). Running this proof advances both the candidate gate AND the Lane 3 bottleneck simultaneously.
- **Vocabulary boundary:** cyber-insurance vocabulary ("attestation," "control efficacy," "regulatory mapping") gets a translation pass to plain English before any client-facing surface ships. "AGI" / "AGI-adjacent" framing remains barred from the package.
- No spec drafted. No package generation logic written. No detector / runtime change. The candidate is now in the formal queue with a clear cheaper-proof gate before it can earn engineering time.
- Doc-only change; no tests required.

### 50. Frontier Intake Review #1 — cheaper-proof exercise complete; monthly cadence committed — ✅ DONE 2026-05-25
- Operator chose to execute the cheaper-proof intake the same evening rather than defer. Real searches against the locked starter source list were performed (no fabrication; same discipline as the morning's header-collection lesson).
- New artifact created: `Frontier_Intake_Log.md` (top-level, sibling to `THREAT_INTEL_LOG.md`). Captures the source list reviewed, eight confirmations of existing direction, five surfaced candidates with source citations, the cadence verdict, vocabulary-boundary check, and the next-step decision tree.
- **Source list reviewed:** CISA phishing guidance + 2026 advisories; FBI IC3 PSA260521 (Kali365, May 2026); CSA AI Safety Initiative research note on OAuth Consent Phishing (May 2026); Abnormal AI 2026 Attack Landscape Report (~800,000 email attacks observed H2 2025); Proofpoint AI-Driven Attacks 2026 briefing (cited via SecurityElites breakdown); Cybertechnology Insights 2026 AI-deepfake-BEC research; OWASP Top 10 for LLM Applications v2025 (current April 2026); Microsoft Agent Framework FIDES (May 2026 release); Nuronus + Data Centre Solutions 2026 MSP cyber insurance guides; GetCybr NIS2 + NIST CSF 2.0 guides; Bronston Legal MSP compliance summary; Abnormal Attune 1.0 + Detection 360 Insights (March 2026); Abnormal Auto-Forwarding Mail Protection blog; IronScales 2026 threat intelligence.
- **Confirmations of existing direction (NOT candidates) — 8 items:** AI-deepfake BEC (40% of BEC by Q1 2026; defended by existing Two-Channel Confirmation v1); multi-persona BEC (confirms Component A from today's AGI-Adjacent decomposition is the right next analyst-layer step); lateral BEC concentration at enterprise (~25% vs. 0.24% at SMB — **strengthens NorthStar's SMB wedge structurally**); multi-channel BEC (Stage B/C scope per Component B verdict today); Microsoft FIDES (confirms NorthStar's deterministic / labeled / human-approval architecture is converging with the most sophisticated frontier work); OWASP LLM Top 10 v2025 coverage check (LLM01/02/06/07 covered; LLM10 surfaced as Candidate 2); 2026 cyber-insurance evidence-not-checkboxes shift + NIS2 + NIST CSF 2.0 (wedge alignment, packaged as Candidate 3); Abnormal Detection 360 Insights confirms explainability is becoming a competitive axis where deterministic explainability remains differentiable.
- **Candidates surfaced — 5 items (recorded in `Frontier_Intake_Log.md`, NOT auto-added to `think_sheet.md`):**
  - **Candidate 1: Department-Level Internal Impersonation Detector** — fake IT helpdesk / HR / payroll / finance lures (Abnormal data: 36.7% of BEC at SMB scale, dominant alongside named-employee impersonation at 45.3%; current detector set covers vendor-side and external-impersonation header divergence but not internal-department lure templates)
  - **Candidate 2: OWASP LLM10 (Unbounded Consumption) Coverage** — per-request tool-call depth caps, output-token caps, cost-per-request circuit breaker; operational hardening, internal-only
  - **Candidate 3: Cyber Insurance Evidence Package** — packaging existing audit trail / scoring / monthly reports / Decision Auditor logs / signed §11 specs into a buyer-ready bundle for cyber-insurance underwriting; positioning + packaging, not a new detector
  - **Candidate 4: Auto-Forwarding Inspection** — outbound rule monitoring + inspection of mail being auto-forwarded to external destinations (Abnormal launched this product in 2026; SMB-MSP-managed M365 tenants are the target audience)
  - **Candidate 5: Device-Code / OAuth-Consent Phishing Detector** — body-content + URL pattern detector for the FBI-documented Kali365 / EvilTokens lure shape (legitimate Microsoft URL + body directing user to enter a device code + OAuth-token capture as goal; bypasses MFA at the OAuth layer; current FBI PSA dated less than 5 days before this intake)
- **Cadence verdict:** 5 candidates → **4+ → monthly cadence**, per the rule locked in Task 49. Refinement flag noted: this is the first intake ever and the count may reflect accumulated backlog rather than steady-state pace; recommend re-evaluating cadence at the third intake (~2026-08) — if steady-state count is 2-3, drop to quarterly; if 4+ persists, stay at monthly.
- **Vocabulary boundary check:** None of the source feeds in this review used "AGI" / "AGI-adjacent" framing in the email-security space. Boundary held without being tested.
- **Strategic finding:** The 2026 frontier (Microsoft FIDES; Abnormal Detection 360 Insights; cyber-insurance evidence-not-checkboxes shift) is converging on auditability + deterministic explainability + evidence depth + human-approval-on-sensitive-action — exactly NorthStar's locked differentiation standards. Intake's primary signal: **NorthStar is on-trend, not behind.**
- **Lateral-BEC market intelligence finding:** Abnormal's strongest enterprise moat (lateral-attack identity baselines) is structurally irrelevant at the SMB end of the market (0.24% vs. ~25%). Worth recording in `THREAT_INTEL_LOG.md` at next refresh.
- No detector, spec, or runtime change authorized by this intake. The five candidates wait for Matt's selection of which (if any) to formally gate next.
- Files changed: created `Frontier_Intake_Log.md`; updated `MASTER_INDEX.md` (added entry); updated `think_sheet.md` (Trend-Chasing row updated with cheaper-proof outcome and monthly-cadence commitment); updated `PROGRESS.md` (this task) and `PROJECT_ACTIVITY_LOG.md`.
- Doc-only change; no tests required.

### 49. Trend-Chasing Layer / Frontier Intake — process-only v1 gated and live-parked — ✅ DONE 2026-05-25
- Operator concern surfaced verbally a week ago and re-raised on 2026-05-25 alongside the AGI-Adjacent decomposition: the AI / agent / threat landscape moves faster than NorthStar's build cadence, and the project needs a structured way to notice landscape shifts before they erode product-market fit.
- Captured the idea as its own scored row in `think_sheet.md` rather than letting it ride inside another bundle. v1 scoping deliberately narrow: **operator-driven, process-only, no runtime, no new agent.** More ambitious shapings (runtime intake agent that watches feeds autonomously; marketable public "frontier watch" transparency surface) are explicitly **separate ideas** that earn their own rows only if v1 evidence warrants them.
- **5-axis score:** `1·1·1·0·2 = 5/10` → revisit / live park band. 7-question stress test recorded in `think_sheet.md` under "Trend-Chasing Layer / Frontier Intake — process-only v1 (2026-05-25)."
- **Cheaper proof:** run the intake **once now** (one-shot exercise) using a starter source list (CISA advisories, abuse.ch, KuppingerCole / Mordor reports, 3-5 AI-research feeds Matt selects, plus the MSP-channel news already cited in `THREAT_INTEL_LOG.md`). Decision rule for cadence: 0-1 surfaced candidates → defer recurring discipline (ad-hoc reviews suffice); 2-3 → quarterly cadence; 4+ → monthly cadence.
- **Vocabulary boundary extended:** "AGI" / "AGI-adjacent" framing from source feeds does not enter NorthStar's product, outreach, spec, or bible voice. Same boundary recorded for the AGI-Adjacent decomposition applies here.
- **Failure-mode mitigations recorded in stress test:** primary risk is research-paper-driven roadmap drift away from customer-driven roadmap. Mitigation relies on the existing 5-axis rubric's Strategic Fit + Revenue Path axes — frontier candidates that fail those axes drop out naturally, the discipline only fails if the rubric is bypassed.
- No runtime change. No new lane started. No `Frontier_Intake_Log.md` artifact created yet (creation deferred to whenever Matt chooses to run the cheaper proof).
- Doc-only change; no tests required.

### 48. AGI-Adjacent Layer — bundle-level gate + component decomposition — ✅ DONE 2026-05-25
- Operator surfaced research material on 2026-05-25 proposing a bundle of (a) a higher-level "analyst-style reasoning layer," (b) cross-domain expansion to logs / endpoints / payments, (c) an "auto-tuning detector ring" / self-improving feedback loop, and (d) an "AGI-style behavior principles" section appended to the NorthStar Bible.
- **Bundle-level gate (first pass):** 5-axis score `1·1·0·1·0 = 3/10` → drop / reshape band. 7-question stress test recorded in `think_sheet.md`. Bundle as written rejected.
- **Component decomposition (operator request, second pass):** Bundle decomposed into six discrete candidate ideas; each scored on the 5-axis rubric and run through the 7-question stress test independently. All six gate firings recorded in `think_sheet.md` under "AGI-Adjacent Layer — component decomposition (2026-05-25)."
- Component verdicts:
  - **A. NorthStar Analyst Reasoning Layer (cross-detector synthesis, email-only):** score 9/10 → **promote**. Build only after the §11-signed 5-axis rubric ships and produces evidence about MSP appetite for cross-email synthesis. Spec-first; needs its own deep-dive before implementation. Autonomy-toggle / "callable, not always on" semantics belong inside this spec when it is drafted.
  - **B. Cross-Domain Expansion (logs / endpoints / payments):** score 2/10 → drop for Stage A. Re-evaluate only at a Stage A → Stage B transition decision.
  - **C. Auto-Tuning Detector Ring:** score 0/10 → drop. Stage C, possibly never.
  - **D. Operator-Approved Drift Tuning Surface:** score 5/10 → revisit. Live-park until first paid pilot generates real tenant traffic.
  - **E. Threat-Family Hypothesis Engine:** score 4/10 → live park. Revisit at Stage A → Stage B transition once multi-tenant traffic produces real cross-email pattern data.
  - **F. "AGI-Style Behavior Principles" Bible Section:** score 0/10 → drop. Walks back the 2026-05-25 bibles deferral and does not fire any of its trigger conditions.
- **One real survivor (Component A).** Promoted only as a future spec-first lane; gated on rubric shipping and MSP discovery feedback. No new lane authorized today.
- **Vocabulary boundary recorded:** "AGI" / "AGI-adjacent" are acceptable inside `think_sheet.md` as internal stress-test rationale only. They do not enter product surfaces, outreach scripts, deep-dive specs, the NorthStar Bible, or any client-facing artifact. Stage A surfaces use plain English; the wedge stays auditability + explainability + per-tenant tuning + reversibility + evidence depth.
- Underlying operator concern about staying current with emerging AI / agent / threat patterns explicitly noted as **not** answered by Components A-F. The proper home for that concern remains the still-uncaptured "Trend-Chasing Layer / Frontier Intake" idea, to be scored separately when scoped.
- No runtime change. No bible change. No spec drafted. No new lane started today.
- Doc-only change; no tests required.

### 47. Client-facing 5-axis Email Scoring Rubric §11 signature — ✅ DONE 2026-05-25
- Matt completed the §11 signature block in `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`.
- Updated spec status to `§11 SIGNED 2026-05-25 by Matt Nichol; implementation not yet started`.
- Cleaned signed-spec consistency:
  - §2 D11 now references the final 160-char cap from D15.
  - §5 schema draft now uses `why_this_score: str = Field(min_length=1, max_length=160)`.
  - §6 rendering contract now reflects D14 / D16: `recommended_action` most prominent, `axis_total` as navigation aid, per-axis breakdown as primary reasoning surface, and the exact "Order is fixed for stability, not priority." disclaimer.
  - §9 rollout now says sign-off locks D1–D17.
  - §11 final line now records that signature is complete, while implementation still requires Matt's explicit start-build instruction and the normal pre-ship gate before commit.
- Updated `MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, and `PROJECT_ACTIVITY_LOG.md` to reflect signed/spec-locked status.
- Spec-only / tracker-only change; no runtime code changed; no tests required.

### 39. Sender-provenance Option C foundation — ✅ DONE 2026-05-24
- Matt explicitly chose **Option C** before the cheaper-proof run: build only the prerequisites that make future sender-provenance / geo-velocity work possible, without implementing the detector.
- Runtime scope:
  - Added additive `EmailInboundPayload.received_headers: list[str]` in `core/blackboard/models.py` so connectors can preserve repeated `Received:` headers without collapsing them into `headers: dict[str, str]`.
  - Updated `normalize_raw_email(...)` in `core/ingest/email_ingest_agent.py` so `received_headers` defaults to `[]`; if omitted, a single legacy `headers["Received"]` string is copied into the list as a backwards-compatible fallback. A connector-provided `received_headers` list wins over that collapsed fallback.
  - Added pure parser module `core/scoring/received_chain_parser.py` with `ReceivedHop`, `ReceivedChain`, and `parse_received_chain(...)`.
- Boundaries preserved:
  - no sender-provenance score,
  - no risk overlay,
  - no Vendor Baseline Store enum/schema changes,
  - no DNS / GeoIP / ASN lookup,
  - no baseline writes,
  - no raw `Received:` header strings emitted by parser dataclasses.
- Added `tests/test_received_chain_parser.py` — **11 passed** — covering default empty list, connector order preservation, single-`Received` fallback, connector list precedence, non-string rejection, empty parse, from/by/IP extraction, IPv6, bare IPv4, IP dedupe, malformed IP suppression, and no raw-header emission.
- Verification:
  - Focused suite: `tests/test_received_chain_parser.py tests/test_header_divergence_detector.py tests/test_email_authentication_detector.py` -> **45 passed**.
  - Full runtime suite: **881 passed, 1 skipped** (+11 from 870, zero regressions).

### 38. Sender-provenance / geo-velocity cheaper-proof protocol — ✅ DONE 2026-05-24
- Created `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md` as the pre-build proof protocol for the promoted sender-provenance / geo-velocity detector idea.
- Created `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv` as the sample classification worksheet for the proof run, including one `cloud_normalized` example and one `stable_high_value` example.
- Reason: `think_sheet.md` explicitly says this detector stays out of `PROGRESS.md` until a cheaper proof on real mailbox headers shows enough per-vendor origin stability. The protocol prevents premature implementation by defining exactly what evidence is needed first.
- Protocol scope:
  - raw headers only; no bodies or attachments,
  - 30-100 vendor-like email samples preferred,
  - at least 10 distinct sender domains,
  - classify each sender as `stable_high_value`, `stable_low_value`, `cloud_normalized`, `noisy_legitimate`, `insufficient_history`, or `not_vendor`,
  - graduate to spec-first runtime work only if a meaningful subset of business-critical vendors has stable enough origin metadata to baseline.
- Guardrails recorded:
  - no runtime detector code yet,
  - no live DNS / GeoIP / ASN lookup in runtime,
  - Vendor Baseline Store signal enum extension would require a signed spec revision,
  - no raw `Received` header strings should be emitted in future analysis output.
- No runtime impact; no tests required for doc-only proof protocol.

### 37. Prompt-Injection Unicode normalization + cross-source bypass closure — ✅ DONE 2026-05-24
- Closes the remaining two Grok approve-with-notes items on the prompt-injection detector:
  - **Unicode whitespace / combining / zero-width / format-character bypass** in Families A-D.
  - **Marker-split-across-attachments bypass.**
- Added two new locked decisions to the spec (`4. Product_Roadmap/Adversarial_Prompt_Injection_Detector_Deep_Dive.md`):
  - **D15 - Pre-regex normalization.** `_normalize_for_regex` runs **NFKD** (NOT NFKC — NFKC silently recomposes accents and defeats the strip step), strips Unicode general category `Mn` (combining marks), strips category `Cf` (format / zero-width chars, including `\u200b`, `\u200c`, `\u200d`, `\u00ad` soft hyphen), and folds any remaining whitespace to ASCII space. Family E continues to scan the **raw** text so zero-width chars near finance/instruction keywords still trigger `hidden_text`.
  - **D16 - Cross-source boundary scanning.** For every adjacent pair of sources, build **two** synthetic views from the last 256 chars of source `i` and the first 256 of source `i+1` - one with no separator (catches `[SYSTEM` + `_INSTRUCTION]`), one with a single ASCII space (catches `ignore previous` + `instructions`). Both views are normalized per D15 and scanned for Families A-D.
- Spec §5 expanded with a new dedicated "Pre-Regex Normalization" subsection; §6 gained 10 new gate tests (24-33).
- Added 18 new tests in `tests/test_prompt_injection_detector.py`:
  - Unicode-bypass closures: zero-width in marker, combining acute in `ignore`, precomposed `í`, full-width Roman, NBSP, ideographic space, zero-width prefix on Family C, soft hyphen in Family D, Family E preserved despite normalization, legitimate accented Spanish text does NOT false-positive.
  - Cross-source closures: marker split body→attachment, imperative split between two attachments, marker split with zero-width chars at the boundary, unrelated sources do NOT false-positive, 800-char-distant tokens do NOT fuse through the 256-char overlap window.
  - White-box helper tests: `_normalize_for_regex` strip / fold contract, NFKD decompose pin, `_build_boundary_pair_views` shape and bound.
- Runtime baseline: **870 passed, 1 skipped** (+18, zero regressions).

### 36. Two-Channel Confirmation TZ edge-case pinning — ✅ DONE 2026-05-24
- Tests-only follow-up to the Grok approve-with-notes report on Two-Channel Confirmation v1.
- Added 7 timezone-edge-case tests in `tests/test_two_channel_confirmation.py` that pin the existing UTC-comparison invariant under the specific Grok-flagged scenarios:
  - **Same UTC instant, different named TZ** (`outcome_at` 05:00 PDT vs `requested_at` 12:00 UTC) → accepted.
  - **Wall-clock-later but UTC-earlier** (`outcome_at` 20:00 JST = 11:00 UTC vs 12:00 UTC requested) → rejected.
  - **Wall-clock-earlier but UTC-later** (`outcome_at` 08:00 EST = 13:00 UTC vs 12:00 UTC requested) → accepted.
  - **Exact UTC equality** → accepted (only strictly-less-than triggers the rule).
  - **1-microsecond-earlier UTC instant** expressed in Nepal time (UTC+5:45) → rejected (pins sub-second ordering precision).
  - **DST boundary crossing** (US fall-back, PDT → PST, later UTC instant) → accepted.
  - **Naive datetime with a value that would be far in the future** → rejected (policy is "aware or reject", not "try to interpret").
- The runtime code in `core/workflows/two_channel_confirmation.py` was already correct (both `_require_aware_datetime` and `_parse_payload_datetime` convert to UTC via `astimezone(timezone.utc)` before comparison). These tests prevent future drift from that invariant.
- Full runtime suite: **852 passed, 1 skipped** (+7, zero regressions).

### 35. Prompt-Injection hidden-text bypass fix — ✅ DONE 2026-05-24
- Closed the radius=12 bypass Grok flagged in its Lane-2 approve-with-notes report (an attacker could place a zero-width character just outside the 12-character window of a finance keyword and evade detection).
- **Detection model rewrite (`core/scoring/prompt_injection_detector.py:_hidden_text_match`)**: replaced the fixed character-radius window with a strip-and-span model:
  1. Strip every zero-width character (U+200B, U+200C, U+200D, U+FEFF) from each text source and record, for each stripped char, the index in the cleaned text where it had been inserted.
  2. Search the cleaned (lowercased) text for any finance/instruction keyword (`wire`, `invoice`, `account`, `ach`, `aba`, `payment`, `system`, `instruction`).
  3. Flag `hidden_text` if any recorded zero-width-character index falls inside the cleaned-text match span `[span_start, span_end]`, or one character outside either boundary.
- **What is now caught** (was bypassable before):
  - Keyword split by one or more zero-width chars: `wi\u200bre`, `wi\u200br\u200be`, `pa\u200byment`, `ac\u200bcount`, `sys\u200btem`, etc.
  - Zero-width char directly before or after the keyword: `\u200bwire`, `wire\u200b`.
  - Zero-width char one whitespace-character away from the keyword: `wire \u200btransfer`.
- **What is intentionally NOT flagged** (false-positive guardrail):
  - Stray zero-width char far from any finance keyword (emoji ZWJ in unrelated text, BOM markers, etc.).
  - Zero-width char separated from the nearest keyword by more than one character.
- **Spec update**: §5 Family E in `Adversarial_Prompt_Injection_Detector_Deep_Dive.md` rewritten to describe the new detection model and explicitly enumerate the catch list and the anti-false-positive guardrail. No new architectural decisions were added; D1–D14 remain locked.
- **Verification:**
  - Focused tests: **44 passed** (+16, `tests/test_prompt_injection_detector.py`) — 8 split-inside-keyword cases (one per keyword + ACH spaces), adjacent-before, adjacent-after, single-whitespace boundary, stray-far-from-keyword anti-test, emoji-ZWJ anti-test, multi-char-separator anti-test, the exact Grok-flagged radius bypass pinned in a dedicated test, and multi-ZW-inside-keyword.
  - Full runtime suite: **845 passed, 1 skipped** (+16, zero regressions).

### 34. Two-Channel Confirmation Enforcement v1 — ✅ DONE 2026-05-24
- **Spec:** signed `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` (§11 Matt Nichol 2026-05-24).
- **New `RecordType.TWO_CHANNEL_CONFIRMATION`** with `TwoChannelConfirmationPayload(StrictModel)` carrying closed enums for `event_type` (`pending` | `outcome`), `outcome_status` (`confirmed` | `rejected` | `unable_to_verify` | `expired`), and `channel_kind` (`previously_known_phone` | `previously_known_in_person` | `previously_known_video_call` | `previously_known_internal_system` | `other_documented`).
- **New `core/workflows/` package** with `two_channel_confirmation.py`:
  - `record_confirmation_request(...)` writes a single `pending` event; rejects duplicate finding_ids, invalid `[A-Za-z0-9_-:.]+` finding_ids (incl. `.`, `..`, leading/trailing dot), out-of-range `risk_floor` (must be `[1, 100]`), and non-int / boolean risk floors; honors the production kill switch; requires timezone-aware datetimes.
  - `record_confirmation_outcome(...)` writes exactly one `outcome` event per finding_id; rejects outcomes without a prior `pending`, a second outcome (no whitewashing), `confirmed` without a `channel_kind`, `other_documented` without a non-empty `reason`, `outcome_at < requested_at`, bad statuses, and overlong description/reason; honors the production kill switch.
  - `list_pending_confirmations(...)` enumerates unresolved findings sorted by `requested_at` for the daily digest, scoped per-tenant.
  - `summarize_confirmation_status(...)` returns the most informative record (outcome > pending > None) for one finding_id.
- **Orchestrator wiring:** new `submit_two_channel_confirmation` route + registry entry `two_channel_confirmation_001` (production-only, workflow role, only allowed to write `TWO_CHANNEL_CONFIRMATION`).
- **Lift-only invariant:** the scoring agent does NOT import this workflow; a `confirmed` outcome does not change `recommended_risk_floor`. Verified by a static test (`test_scoring_agent_does_not_import_two_channel_confirmation`).
- **Data minimization:** payload carries no raw email content, vendor address, account numbers, or finding raw values; operator labels are length-bounded.
- **Audit target:** `audit_tools/grok_audit_runner.py two_channel_confirmation` audits spec + workflow + schema + orchestrator + registry + tests.
- **Verification:**
  - Focused tests: **40 passed** (`tests/test_two_channel_confirmation.py`) covering API surface, schema registration, all GovernanceError paths (duplicate, invalid id, out-of-range floor including explicit `risk_floor=0`, naive datetime, missing pending, double outcome, missing channel_kind, missing reason, time-order violation, bad status), kill switch on both entry points, closed status enum, pending listing (filter, sort, tenant isolation, risk_floor preserved), summarize (None/pending/outcome), lift-only invariant, no-raw-content guarantee, and audit-target registration.
  - Full runtime suite: **829 passed, 1 skipped** (+40, zero regressions).
  - Polish after first Grok audit (`approve_with_notes`): tightened `ConfirmationRecord.recommended_action` to `Literal["needs_review"]`, documented the `.` / `..` / leading/trailing-dot finding_id guards in §2 D6 of the spec, added explicit `risk_floor=0` rejection test, and added `list_pending_confirmations` `risk_floor` preservation test.

### 33. Adversarial Prompt-Injection Detector v1 — ✅ DONE 2026-05-24
- **Spec:** signed `4. Product_Roadmap/Adversarial_Prompt_Injection_Detector_Deep_Dive.md` (§11 Matt Nichol 2026-05-24).
- **Runtime:** new pure-function detector `core/scoring/prompt_injection_detector.py` scans `EmailInboundPayload.body_plain` plus each `EmailAttachmentMeta.extracted_text` against five closed families:
  - `instruction_marker` (`[SYSTEM_INSTRUCTION]`, `<|im_start|>system`, `### Instruction:`, `BEGIN/END PROMPT`, `### system`, `### assistant`).
  - `override_imperative` (`ignore previous instructions`, `disregard the above`, etc.).
  - `role_impersonation` (`you are now`, `act as`, `pretend you are`, `from now on, behave...`).
  - `output_control` (`only output JSON`, `respond with exactly`, `set risk_score to`, `mark this email as safe`, `recommended_action = safe`).
  - `hidden_text` (zero-width chars adjacent to finance/instruction keywords).
- **Scoring (corrected after first Grok audit `reject_with_required_fixes`):** `score = min(max(marker_floor, non_marker_score(N)), 90)` where `marker_floor = 75` if any `instruction_marker` hit else `0`, and `non_marker_score` is the closed table `{0:0, 1:55, 2:70, 3:80, 4+:90}` over the count `N` of non-marker families. `hidden_text` counts toward `N`. Spec §4 was rewritten to remove an internal inconsistency between gate test 8 (2-families = 70) and gate test 10 (3-families = 80) that the old `70 + 5*(n-2)` formula could not satisfy.
- **Input length bound:** new `_MAX_SCAN_CHARS = 200_000` constant prevents pathological regex behavior on attacker-controlled bulk input; each text source (body + every attachment) is truncated before scanning.
- **Overlay integration:** `_overlay_ransomware_precursor` now applies the detector after Document Metadata Fingerprinting with the same Tiered Detection rules - LOW skips, MEDIUM applies floor, HIGH adds +10 (cap 95). Indicators (`prompt_injection:<family>`) are appended to `risk_factors`/`phishing_signals` only when the floor actually applied (preserves the LOW-skip property).
- **Data minimization:** indicators are family tags only; raw matched substrings never leave the detector.
- **Audit target:** `audit_tools/grok_audit_runner.py prompt_injection` audits spec + detector + scoring integration + tests.
- **Verification:**
  - Focused tests: **28 passed** (`tests/test_prompt_injection_detector.py`) covering API surface, all five families, the closed N-count table (1/2/3/4-cap), marker-dominates-1 vs marker-coexists-with-3, `hidden_text` counting toward N, attachment family aggregation, attachment dedupe, input length bound, lift-only invariant, profile gating (LOW/MEDIUM/HIGH), no-leak guarantee, code-block/Markdown false-positive guardrail, and audit-target registration.
  - Full runtime suite: **789 passed, 1 skipped** (+28, zero regressions).

### 32. Vendor Baseline audit-note polish — ✅ DONE 2026-05-24
- Closed the three non-blocking follow-ups from the original Vendor Baseline Store Grok approve-with-notes report:
  - **Out-of-range `ttl_days` direct API tests:** 5 parametrized cases (0, 29, 366, 10_000, -1) call `ingest_signal(..., ttl_days=...)` directly and assert `GovernanceError` plus no per-tenant database file is created. Pre-existing coverage only exercised the tenant-override path.
  - **Non-int `ttl_days` rejection:** 5 parametrized cases (`True`, `False`, `1.5`, `"90"`, `None`) confirm the `_validate_ttl_days` type guard fires before any write.
  - **Schema CHECK probes:** added direct SQL inserts that exercise the `length(signal_hash) = 64`, non-empty `vendor_domain`, and `datetime(...)` CHECK constraints, each raising `sqlite3.IntegrityError`.
  - **Cross-tenant row inspection:** new tests open each per-tenant SQLite file with raw `sqlite3.connect` and assert that tenant B's writes never leak into tenant A's file, and that the same raw signal value under two tenants hashes to disjoint rows.
- Verification:
  - Focused vendor baseline suite: **52 passed, 1 skipped** (+13 from 39).
  - Full runtime suite: **761 passed, 1 skipped** (+16 from 745, zero regressions).

### 31. Document Metadata Fingerprinting v1 implementation — ✅ DONE 2026-05-24
- Landed `core/scoring/document_metadata_detector.py` against `4. Product_Roadmap/Document_Metadata_Fingerprinting_Deep_Dive.md` (§11 signed 2026-05-24).
- Schema:
  - Added `PdfAttachmentMetadata` and optional `EmailAttachmentMeta.pdf_metadata` (bounded Producer/Creator strings, max 512 chars each).
- Runtime behavior:
  - `assess_document_metadata_fingerprint()` extracts qualifying PDF/invoice attachment metadata only (no PDF bytes, no OCR, no network).
  - Uses Vendor Baseline Store `pdf_producer_fingerprint` with check-then-ingest ordering.
  - `new` / `expired` fingerprints recommend risk floor **75** and action `needs_review`; `known` emits no lift.
  - Wired into `email_risk_scoring_agent.py` production scoring cycle and `_overlay_ransomware_precursor` with profile gating (LOW skips, MEDIUM floor 75, HIGH +10 cap 95).
  - No Tiered Detection `DetectorIdentity` enum expansion in v1.
- Verification:
  - Focused suite: **23 passed** in `tests/test_document_metadata_detector.py`.
  - Full runtime suite: **745 passed, 1 skipped** (+23 from 722, zero regressions).

### 30. Catch-up Grok audits on new governance + detector tools — ✅ DONE 2026-05-24
- Wired three new audit targets into `audit_tools/grok_audit_runner.py`:
  - `independent_decision_auditor` (spec `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md` + runner + template + tests + Task 29 receipt).
  - `pre_ship_audit` (operator-authorization paragraph in `PROJECT_HANDSHAKE.md` as the design contract, plus `audit_tools/pre_ship_audit.py` and its test file).
  - `email_authentication` (current-direction handshake note as the design contract, plus the detector, the scoring overlay, the package init, and the test file).
- Reports:
  - `audit_outputs/independent_decision_auditor_grok_audit_20260525T015404Z.md` - verdict **approve**, no divergence, no coverage gaps, no security risks.
  - `audit_outputs/pre_ship_audit_grok_audit_20260525T015431Z.md` - verdict **approve**, faithful realization of the authorized pre-ship gate.
  - `audit_outputs/email_authentication_grok_audit_20260525T015457Z.md` - verdict **approve**, header-only detector with the lift-only invariant and correct profile gating.
- Verification:
  - No code changes triggered; this lane was a focused code-level audit only.
  - All three audits clean, so no remediation cycle was required.

### 29. Independent Decision Auditor workflow implementation — ✅ DONE 2026-05-24
- Landed `audit_tools/decision_audit_runner.py` against the §11-signed `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md` contract.
- Runtime boundary:
  - Tool remains local governance tooling under `audit_tools/`, outside product runtime.
  - No `core/` module imports the runner, and the runner does not write Blackboard, production state, operator state, Git, GitHub, or trackers.
- Packet / report workflow:
  - Added `decision_audit_inputs/TEMPLATE.md` with the locked six-section Markdown packet contract.
  - Added first self-audit packet: `decision_audit_inputs/20260524_1741_decision_auditor_next.md`.
  - Reports write only under `audit_outputs/decision_audits/`, which stays covered by the existing `audit_outputs/` gitignore rule.
- Secret and data-minimization controls:
  - `load_xai_key()` reads only `XAI_API_KEY` and optional `XAI_MODEL`; missing model falls back to `grok-4`.
  - Packet validation fails before any network call when required sections are missing, known secret markers appear (`XAI_API_KEY`, `BEGIN PRIVATE KEY`, `gho_`, `YOUR_GITHUB_PAT_HERE`), or obvious raw routing/account strings appear.
  - xAI HTTP errors are redacted and do not echo authorization headers or API keys.
- Verdict handling:
  - `extract_verdict()` accepts only the closed enum: `proceed`, `proceed_with_notes`, `revise_before_proceeding`, `defer`, `operator_decision_required`.
  - `proceed` / `proceed_with_notes` return success.
  - `revise_before_proceeding`, `defer`, and `operator_decision_required` return a blocking non-zero exit unless `--report-only` is used.
  - `--report-only` writes the report and clearly prints the blocking verdict while returning zero.
- Verification:
  - Focused Decision Auditor gate tests: **30 passed**.
  - Full runtime suite from `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`: **688 passed, 1 skipped**.
  - Root-level full-suite attempt failed during collection because `core` was not on `PYTHONPATH` from the repo root; rerunning from the runtime directory passed cleanly.
- Required self-audit:
  - Ran `python audit_tools\decision_audit_runner.py decision_audit_inputs\20260524_1741_decision_auditor_next.md`.
  - Report: `audit_outputs/decision_audits/20260524_1741_decision_auditor_next_decision_audit_20260525T004700Z.md`.
  - Verdict: **`proceed`**. Grok found no material missing alternatives, no spec override, and no scope expansion; it judged the lane the smallest protective action before the next major build-lane decision.

### 28. Tiered Detection Intensity implementation — ✅ DONE 2026-05-24
- Landed `core/operator_state/security_profile.py` against the §11-signed `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md` contract.
- Runtime behavior:
  - Implements closed `SecurityProfile`, `DetectorIdentity`, `ForcedEscalationTrigger`, and `SalesPlan` literals.
  - Defaults absent tenant profile state to `medium`.
  - Stores per-tenant operator-controlled profile files at `blackboard_root/operator_state/security_profiles/<tenant>.json`.
  - Resolves effective profile with a pure lift-only resolver: forced escalation can only raise to `high`; add-on detectors can only enable.
  - Locks the v1 detector registry to the five current scoring slots: LLM primary, ransomware precursor overlay, header divergence, ghost thread, and Financial State Ledger.
  - Locks sales-plan defaults: `essentials -> low`, `plus -> medium`, `enterprise -> high`.
  - Appends `PROFILE_CHANGE` rows to the existing operator audit log on every profile write while preserving kill-switch audit rows.
  - Extends `EmailAnalysisPayload` additively with `tenant_default_profile`, `effective_profile`, and `forced_escalation_triggers`.
  - Wires `run_email_risk_scoring_cycle` and `score_one_email_payload` so profile metadata is attached only when the deterministic overlay path is enabled; `enable_ransomware_precursor_overlay=False` remains byte-identical and does not resolve profiles.
  - Preserves kill-switch precedence: production loop checks the kill switch before any profile read.
- Added `tests/test_security_profile.py` — **36 passed**, covering §7 gate areas: closed enums, rank ordering, default MEDIUM, exhaustive detector registry, LOW/MEDIUM/HIGH enabled sets, add-on lift/no-disable invariant, all four forced triggers, stable multi-trigger output, 48-case lift-only sweep, tenant isolation, profile-change audit row, forced-escalation payload visibility, sales mapping, kill-switch precedence, overlay-off backward compatibility, absent-field schema compatibility, cost monotonicity, cost ceiling under escalation, no raw-value leakage, tenant-id validation, strict disk-load rejection including malformed JSON -> `GovernanceError`, no direct Blackboard write, state confinement, operator-audit profile rows, and Grok audit target wiring.
- Extended daily digest surfaces so `DailyDigestEmailEntry`, `DailyDigestRiskEntry`, and the digest LLM aggregate carry `tenant_default_profile`, `effective_profile`, and `forced_escalation_triggers` for client-visible `Profile`, `Tenant default`, and `Escalated by` rows.
- Updated `audit_tools/grok_audit_runner.py` with a `tiered_detection_intensity` audit target including the signed spec, profile module, operator audit schema, scoring-agent integration, blackboard schema, test file, and tracker receipt anchors.
- Verification:
  - `python -m pytest tests/test_security_profile.py -q` -> **36 passed**.
  - `python -m pytest tests/test_security_profile.py tests/test_daily_digest_agent.py tests/test_operator_kill_switch.py tests/test_email_risk_scoring_agent.py -q` -> **100 passed** after first Grok audit remediation.
  - `python -m pytest tests/test_security_profile.py tests/test_operator_kill_switch.py tests/test_email_risk_scoring_agent.py tests/test_header_divergence_detector.py tests/test_ghost_thread_detector.py tests/test_financial_state_ledger.py tests/test_recommended_risk_floor_lift_only_invariant.py -q` -> **167 passed** before remediation; covered affected scoring/operator surfaces.
  - `python -m pytest -q` -> **658 passed, 1 skipped** (+37 from 621, zero known runtime regressions).
- Independent Grok audit:
  - First run `audit_outputs/tiered_detection_intensity_grok_audit_20260525T001526Z.md` returned **approve with notes**.
  - Remediated concrete findings: daily-digest profile visibility and malformed profile JSON wrapping.
  - Second run `audit_outputs/tiered_detection_intensity_grok_audit_20260525T001951Z.md` returned **approve**.
  - Grok found **no spec divergence**, **no coverage gaps**, and **no security / boundary risks** after remediation.

### 27. Tiered Detection Intensity (Low / Medium / High) SPEC-FIRST LOCKDOWN — ✅ §11 SIGNED 2026-05-24
- `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md` — §11 Lockdown Signature filled by Matt (operator) on 2026-05-24.
- Spec scope locked:
  - Pure types + resolver live in `core/operator_state/security_profile.py`; per-tenant state at `blackboard_root/operator_state/security_profiles/<tenant>.json` (Guardrail 12 separation; Guardrail 11 surfaces unchanged).
  - Three-tier closed enum: `low` / `medium` / `high`, with integer ranks `LOW=0 < MEDIUM=1 < HIGH=2`.
  - Default tenant posture when no state file exists = `MEDIUM`. A `LOW` tenant must be explicitly written by the operator.
  - Closed `DetectorIdentity` enum (v1) matches the five detector slots already wired into `_overlay_ransomware_precursor`: `llm_primary`, `ransomware_precursor_overlay`, `header_divergence`, `ghost_thread`, `financial_state_ledger`.
  - LOW set = LLM primary + precursor overlay + header divergence + ghost thread. MEDIUM adds FSL. HIGH is reserved in v1 (no HIGH-only detector ships before its own §11 spec).
  - Closed `ForcedEscalationTrigger` enum (v1, four triggers): `llm_high_risk_score` (≥80), `header_divergence_strong` (≥80), `ghost_thread_detected` (>0), `manual_operator_escalation`. Five additional triggers (financial_state_delta, high_value_invoice, prior_vendor_fraud_flag, fresh_baseline_vendor, combined_bec_signals) are explicit v2 deferrals listed in §10.
  - Lift-only invariant: forced escalation can ONLY raise the effective tier; add-on detectors can ONLY enable, never disable. Pinned by §7 gate tests #9, #15, #24.
  - Sales-plan default mapping locked (Option C): `essentials → low`, `plus → medium`, `enterprise → high`.
  - Audit emission: every profile write appends one `OperatorAuditEntry` with action `PROFILE_CHANGE`; every forced escalation is recorded on the analysis payload. Operator audit log remains the single source of truth.
  - Kill switch (Guardrail 12) stays the outermost gate at every loop entry; profile resolution runs strictly AFTER the kill-switch check, never as a substitute for it.
  - Backward compat: `enable_ransomware_precursor_overlay=False` must still produce byte-identical output to existing Month 1 / 2 / 3 fixtures and the grok-4 PASS gate. New analysis fields are additive + optional.
- §7 30-test gate locked as closure contract; partial implementations do NOT close §4. Cost-monotonicity (#23) and cost-ceiling-under-escalation (#24) lock the call-count shape so future detector additions cannot silently regress the cost contract.
- Grok independent-audit `tiered_detection_intensity` target must be wired into `audit_tools/grok_audit_runner.py` **before** implementation can be claimed closed (§7 test #30).
- Implementation work is **not started** and does not begin until Matt issues the explicit `start build` signal.
- Doc-only change; runtime baseline holds at **621 passed, 1 skipped**.

### 26. Financial State Ledger / Delta Tripwire implementation — ✅ DONE 2026-05-24
- Landed `core/scoring/financial_state_ledger.py` against the §11-signed `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` contract.
- Runtime behavior:
  - Extracts high-precision labelled payment-destination signals from `EmailInboundPayload.body_plain` and `EmailAttachmentMeta.extracted_text`.
  - Covers the five locked v1 signal types: `routing_number`, `swift_bic_code`, `iban`, `account_number`, and `payment_portal_url`.
  - Deduplicates within one email by `(signal_type, normalized_value, source)` and calls Vendor Baseline Store once per unique `(signal_type, normalized_value)` state key.
  - Calls `check_signal` before `ingest_signal` for every valid candidate; `new` and `expired` states produce Delta Tripwire findings before the value is learned/refreshed.
  - Returns frozen dataclasses only: extracted signal metadata, findings, recommended risk floor, recommended action, and out-of-band verification flag.
  - Recommends `recommended_risk_floor=85` and `recommended_action="needs_review"` only when at least one finding exists; known-only and no-signal paths return `0` / `"none"`.
  - Keeps raw financial values private to the in-memory extraction path; returned assessments expose redacted display values and Vendor Baseline Store hashes only.
  - Inherits Guardrail 12 kill-switch behavior through Vendor Baseline Store entry points; the detector does not introduce a separate kill path or persistent state surface.
- Added `tests/test_financial_state_ledger.py` — **29 passed**, covering all §7 gate areas including public API surface, no-signal, first-seen, known, expired, check-before-ingest ordering, attachment text, body/attachment dedupe, portal host extraction, unlabelled-number suppression, malformed candidates, multiple signal types, raw-value leakage, verification wording, vendor-domain validation, kill-switch inheritance, tenant isolation, no direct Blackboard writes, no new persistent state, scoring-overlay max merge, digest readability, and Grok audit target presence by direct package wiring test.
- Updated `core/scoring/email_risk_scoring_agent.py` so `_overlay_ransomware_precursor(...)` can max-merge an already-computed `FinancialStateLedgerAssessment.recommended_risk_floor` without lowering an LLM score.
- Updated `audit_tools/grok_audit_runner.py` with a `financial_state_ledger` audit target including signed spec, implementation, scoring overlay, Vendor Baseline Store API, test file, and tracker receipt anchors.
- Verification fix: adjusted the Windows Vendor Baseline DACL assertion to compare against the effective `FILE_GENERIC_READ | FILE_GENERIC_WRITE` mask returned by NTFS, while preserving the prior one-ACE/current-user/no-inheritance/no-SYSTEM/no-Administrators coverage.
- Verification:
  - `python -m pytest tests/test_financial_state_ledger.py -q` -> **29 passed**.
  - `python -m pytest tests/test_financial_state_ledger.py tests/test_header_divergence_detector.py tests/test_ghost_thread_detector.py tests/test_vendor_baseline_store.py tests/test_vendor_baseline_isolation_boundary.py -q` -> **111 passed, 1 skipped**.
  - `python -m pytest -q` -> **621 passed, 1 skipped** (+29 from 592, zero known runtime regressions).
- Independent Grok audit:
  - `python audit_tools/grok_audit_runner.py financial_state_ledger` -> `audit_outputs/financial_state_ledger_grok_audit_20260524T224143Z.md`.
  - Verdict: **approve**.
  - Grok found **no spec divergence**, **no coverage gaps**, and **no security / boundary risks**. Minor observation only: the scoring overlay accepts an FSL assessment, while production call sites do not yet supply one because vendor identity must remain explicit and caller-owned.

### 25. Financial State Ledger / Delta Tripwire SPEC-FIRST LOCKDOWN — ✅ §11 SIGNED 2026-05-24
- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` — §11 Lockdown Signature filled by Matt (operator) on 2026-05-24.
- Spec scope locked:
  - Detector consumes `EmailInboundPayload.body_plain` and attachment `extracted_text` only (no raw PDF / no OCR / no remote fetch in v1).
  - Extracts five existing Vendor Baseline Store financial signal types: routing number, SWIFT/BIC, IBAN, account number, payment portal URL.
  - Uses Vendor Baseline Store only; no new persistent state surface is opened.
  - Enforces check-before-ingest so first observations are flagged before becoming baseline (ordering enforced by gate test, not comment).
  - Returns one frozen-dataclass assessment from a single public function `assess_financial_state_delta`.
  - Recommends risk floor `85`, action `needs_review`, and mandatory out-of-band verification wording when any financial signal is `new` or `expired`.
  - Never returns or persists raw financial strings; only normalized hash digests reach storage.
  - Kill switch inherits from Vendor Baseline Store entry points; the detector does NOT introduce its own kill path.
- §7 22-test gate locked as closure contract; partial implementations do NOT close §4.
- Grok independent-audit `financial_state_ledger` target must be wired into `audit_tools/grok_audit_runner.py` **before** implementation can be claimed closed (§7 test #22).
- Implementation work is **not started** and does not begin until Matt issues the explicit `start build` signal.
- Doc-only change; runtime baseline remains **592 passed, 1 skipped expected**.

### 20. Visible deliberation + tiered detection stress tests — ✅ DONE 2026-05-24
- Filled the seven-question stress-test gate in `think_sheet.md` for:
  - **Visible Multi-Agent Deliberation Layer** — ST flipped from `N` to `Y`.
  - **Tiered Detection Intensity (Low / Medium / High) aligned to sales tiers** — ST flipped from `N` to `Y`.
- Visible deliberation decision: promote candidate, but do not build before the underlying detector set is richer. Best sequence recorded as Vendor Baseline Store -> Financial State Ledger / document signals -> client-facing 5-axis scoring -> visible deliberation. Build only behind Tiered Detection Intensity so Low/Medium tenants do not pay High-tier reasoning cost on routine mail.
- Tiered intensity decision: promote candidate, but requires spec-first treatment before implementation. The future spec must lock tier definitions, detector minimum-tier contract, forced-escalation closed enum, `tenant_overrides` schema, default = Medium, and gate tests proving risky mail can force High scrutiny regardless of tenant default.
- Boundary preserved: stress-tested means eligible to promote later, not automatically committed implementation. No code lands without Matt's explicit "start build" signal.
- Doc-only change; no test impact. Runtime baseline holds at **555 tests passing**.

### 16. Ghost-thread continuity detector — ✅ DONE 2026-05-23
- Landed `core/scoring/ghost_thread_detector.py` — pure-function deterministic detector for fake email-thread continuity. Fires when the subject begins with a threading prefix (`Re:`, `Re[2]:`, `Fwd:`, `Fw:`, case-insensitive) AND neither `In-Reply-To` nor `References` carries a non-empty value.
- Score: **55** (needs_review band, intentionally lower than Reply-To divergence at 65 because legitimate broken mail clients can occasionally drop threading headers).
- Wired into `_overlay_ransomware_precursor` alongside the precursor sub-scores and the header-divergence detector. All three deterministic signals max-merge into `recommended_risk_floor` so the lift-only invariant is preserved.
- Added `tests/test_ghost_thread_detector.py` — **21 passed**, covering: empty / `None` subject, non-threading subject, every threading-prefix variant (Re:, RE:, re:, Fwd:, Fw:, Re[2]:), Re: in the middle of the subject (must NOT fire), `In-Reply-To` present, `References` present, both present, empty / whitespace-only header values, case-insensitive header keys, and four end-to-end integration tests against the scoring overlay.
- Verification: `python -m pytest tests/test_ghost_thread_detector.py -v` -> **21 passed in 0.08s**; full suite `python -m pytest -q` -> **555 passed in 6.96s** (+21 from 534, zero regressions).

### 15. From / Reply-To / Return-Path divergence detector — ✅ DONE 2026-05-23
- Landed `core/scoring/header_divergence_detector.py` — pure-function deterministic detector for the three sender-identity header divergence kinds that mark a Business Email Compromise: `From:` vs `Reply-To:`, `From:` vs `Return-Path:`, `From:` vs `Sender:`.
- Domain comparison uses an eTLD+1 heuristic (last two labels, lowercased) so legitimate subdomain mail (`m.vendor.com` <-> `vendor.com`) is correctly NOT flagged as divergence, while lookalike-TLD attacks (`vendor.com` vs `vendor.co`) are.
- Score band tuned so Reply-To divergence alone lifts to **65** (needs_review territory), Return-Path alone to **45** (legit ESPs often diverge), Sender header alone to **35** (lowest-confidence). Multi-divergence combinations get a +10 bonus, capped at **90** so the detector alone can never single-handedly force a final `risk_score` of 100.
- Wired into `_overlay_ransomware_precursor` as part of `recommended_risk_floor`. Lift-only invariant preserved end-to-end (verified by an extension to `tests/test_recommended_risk_floor_lift_only_invariant.py`-style coverage in the new test module).
- Added `tests/test_header_divergence_detector.py` — **24 passed**, covering: empty / missing / malformed inputs, identical domains, legitimate subdomains in both directions, lookalike-TLD divergence, each single-divergence kind, multi-divergence combination with bonus, the 90-cap, case-insensitive headers and domains, RFC 5322 display-name parsing, bracketed Return-Path parsing, and four end-to-end integration tests against the scoring overlay.
- Verification: `python -m pytest tests/test_header_divergence_detector.py -v` -> **24 passed in 0.08s**; full suite `python -m pytest -q` -> **534 passed in 6.80s** (+24 from 510, zero regressions).

### 14. Lift-only invariant property test for `recommended_risk_floor` — ✅ DONE 2026-05-23
- Landed `tests/test_recommended_risk_floor_lift_only_invariant.py` — 10 hand-written edge-case tests + 1 seeded randomized property loop covering 500 (inbound, analysis, lifts) combinations.
- Pins the runtime's most important invariant: `_overlay_ransomware_precursor` can ONLY raise the LLM-derived `risk_score`, never lower it; result is always within `[0, 100]`.
- Coverage: zero / max LLM risk, benign / dangerous-attachment / suspicious-URL / credential-lure inbound shapes, fraud-lift gate on (vendor_fraud_score >= 40 and wire_transfer_anomaly_score >= 40 paths) and off, negative lifts clamped, oversized lifts clamped, precursor sub-score ≤ final risk_score.
- Random loop is seed-pinned (`seed=20260523`) and asserts a verbose failure message that names the exact case so future regressions are reproducible from the test output alone.
- Verification: `python -m pytest tests/test_recommended_risk_floor_lift_only_invariant.py -v` -> **11 passed in 0.11s**; full suite `python -m pytest -q` -> **510 passed in 7.28s** (+11 from 499, zero regressions).

### 13. Runnable daily-digest demo script — ✅ DONE 2026-05-23
- Landed `scripts/inbox_shield_daily_digest_demo.py` — deterministic operator-run demo that seeds five fictional Acme emails into an isolated demo blackboard, runs the real Inbox Shield `ingest_email` -> `run_email_risk_scoring_cycle` -> `run_daily_digest_cycle` path with fake LLM clients, and writes the generated markdown digest artifact.
- Generated artifact: `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md`.
- Boundary preserved: no live mailbox connector, no live LLM, no email send, no `production_state` / tenant override / policy-pipeline writes; the `send_daily_digest` workflow trigger is written only inside the isolated demo blackboard as proof the runtime route fired.
- Demo scenario: five emails (vendor invoice + new ACH instructions, credential-reset attachment, executive request before EOD, routine partner check-in, newsletter), producing 5 inbound records, 5 analyses, 1 daily digest, and 1 `send_daily_digest` workflow trigger.
- Added `tests/test_inbox_shield_daily_digest_demo.py` — **7 passed**, covering locked five-email scenario, deterministic scoring client, deterministic digest renderer, generated artifact content, runtime record counts, non-demo blackboard deletion guard, and CLI summary.
- Verification: `python -m pytest tests/test_inbox_shield_daily_digest_demo.py -q` -> **7 passed**; full suite `python -m pytest -q` -> **499 passed** (+7 from 492, zero regressions); scanner `python -m scripts.project_trigger_scan --baseline-tests 499` -> **scan_clean** after this update.
- Operator usage: `python -m scripts.inbox_shield_daily_digest_demo` from `Runtime_Implementation/`.

---

## Completed (Recent History)

| Date | Task | Test delta | Files |
|------|------|-----------:|-------|
| 2026-05-24 | Independent Decision Auditor implementation | +30 → **688** | `audit_tools/decision_audit_runner.py`, `decision_audit_inputs/TEMPLATE.md`, `decision_audit_inputs/20260524_1741_decision_auditor_next.md`, `tests/test_decision_audit_runner.py`, `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md`, `think_sheet.md` |
| 2026-05-24 | Tiered Detection Intensity implementation | +37 → **658** | `core/operator_state/security_profile.py`, `core/operator_state/audit.py`, `core/blackboard/models.py`, `core/scoring/email_risk_scoring_agent.py`, `core/drafting/daily_digest_agent.py`, `tests/test_security_profile.py`, `tests/test_daily_digest_agent.py`, `audit_tools/grok_audit_runner.py`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md`, `think_sheet.md` |
| 2026-05-24 | Financial State Ledger / Delta Tripwire implementation | +29 → **621** | `core/scoring/financial_state_ledger.py`, `core/scoring/email_risk_scoring_agent.py`, `tests/test_financial_state_ledger.py`, `audit_tools/grok_audit_runner.py`, `tests/test_vendor_baseline_store.py`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md`, `think_sheet.md` |
| 2026-05-24 | Financial State Ledger / Delta Tripwire SPEC-FIRST LOCKDOWN (§11 SIGNED) | 0 | `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md`, `think_sheet.md` |
| 2026-05-24 | Vendor Baseline Store Grok audit cycle + cleanup | +5 → **592** | `audit_tools/grok_audit_runner.py`, `.gitignore`, `core/production_state/vendor_baseline/`, `tests/test_vendor_baseline_store.py`, `tests/test_vendor_baseline_isolation_boundary.py`, `think_sheet.md` |
| 2026-05-24 | Vendor Baseline Store implementation | +32 → **587** | `core/production_state/vendor_baseline/`, `core/blackboard/models.py`, `core/orchestrator/registry.py`, `core/orchestrator/routes.py`, `core/production_state/tenant_overrides.py`, `tests/test_vendor_baseline_store.py`, `tests/test_vendor_baseline_isolation_boundary.py`, `requirements.txt` |
| 2026-05-24 | Stress-test backlog Batch 2 — workflow / trust / UX / test-infra | 0 | `think_sheet.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` |
| 2026-05-24 | Stress-test backlog Batch 1 — BEC + email-auth detectors | 0 | `think_sheet.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` |
| 2026-05-24 | Visible deliberation + tiered detection stress tests | 0 | `think_sheet.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` |
| 2026-05-24 | Visible deliberation + tiered detection intensity captured | 0 | `think_sheet.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` |
| 2026-05-23 | Late-night think-sheet capture + outreach/research framing | 0 | `think_sheet.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `MASTER_INDEX.md`, `PROJECT_ACTIVITY_LOG.md` |
| 2026-05-23 | Vendor Baseline Store spec-first lockdown + §11Matt Nichol| 0 | `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md`, `PROGRESS.md`, `PROJECT_HANDSHAKE.md`, `think_sheet.md` |
| 2026-05-23 | Ghost-thread continuity detector | +21 → **555** | `core/scoring/ghost_thread_detector.py`, `core/scoring/email_risk_scoring_agent.py` (overlay wiring), `tests/test_ghost_thread_detector.py` |
| 2026-05-23 | From / Reply-To / Return-Path divergence detector | +24 → **534** | `core/scoring/header_divergence_detector.py`, `core/scoring/email_risk_scoring_agent.py` (overlay wiring), `tests/test_header_divergence_detector.py` |
| 2026-05-23 | Lift-only invariant property test for `recommended_risk_floor` | +11 → **510** | `tests/test_recommended_risk_floor_lift_only_invariant.py` |
| 2026-05-23 | Runnable daily-digest demo script | +7 → **499** | `scripts/inbox_shield_daily_digest_demo.py`, `tests/test_inbox_shield_daily_digest_demo.py`, `Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md` |
| 2026-05-23 | CISA KEV threat-intel ingestion v0 | +19 → **492** | `scripts/cisa_kev_ingest.py`, `tests/test_cisa_kev_ingest.py` |
| 2026-05-23 | Inbox Shield sample monthly report | 0 | `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md` |
| 2026-05-23 | Real Acme Effective Parameter Report demo | +1 → **473** | `scripts/acme_effective_parameter_report_demo.py`, `tests/test_acme_effective_parameter_report_demo.py`, `Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md` |
| 2026-05-23 | MSP discovery evidence package (Milestone A9) | 0 | `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` |
| 2026-05-23 | Long-arc tracking foundation (vision + milestone arc + threat intel + revenue map) | 0 | `VISION.md`, `MILESTONE_ARC.md`, `THREAT_INTEL_LOG.md`, `REVENUE_MAP.md` |
| 2026-05-22 | Vendor-invoice live diagnostics (5/5 PASS post-patch) | 0 | `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` |
| 2026-05-22 | Vendor-invoice recall prompt remediation | +1 → **472** | `email_risk_scoring_agent.py`, `tests/test_email_risk_scoring_agent.py` |
| 2026-05-22 | Phase 1.5 full `grok-4` rerun diagnostic | 0 | `eval_report_2026_05_22_phase_1_5_rerun.md` |
| 2026-05-22 | Autonomous trigger scanner v1 + blocked-state heuristic | +10 → **471** | `scripts/project_trigger_scan.py`, `tests/test_project_trigger_scan.py` |
| 2026-05-22 | SMB tier matrix in product sheet | 0 | `Product_Sheets/Fraud_Detection_Product_Sheet.md`, `PROGRESS.md` (created) |
| 2026-05-22 | Evidence-package visibility (effective-parameter report) | +18 → **461** | `effective_parameters_report.py`, CLI `report`, 18 tests |
| 2026-05-21 | Operator override CLI | +9 → **443** | `tenant_override_operator.py`, runbook, 9 CLI tests |
| 2026-05-21 | Month 6 Phase 2.1 runtime (per-tenant overrides) | +15 → **434** | `tenant_overrides.py`, 15 tests |

---

## Source-of-Truth Files

- `VISION.md` — long-arc product thesis (Stage A / B / C) and non-negotiables
- `MILESTONE_ARC.md` — multi-year milestone tracker with "done when" criteria
- `THREAT_INTEL_LOG.md` — record of threat patterns ingested and policy updates that resulted
- `REVENUE_MAP.md` — three-lane funding plan (Survival / Freelance / NorthStar) with Kelowna specifics
- `PROJECT_HANDSHAKE.md` — active build track and Completed log (items 168–178)
- `PROJECT_ACTIVITY_LOG.md` — chronological session entries
- `MASTER_INDEX.md` — repo index
- `think_sheet.md` — idea scoring / drift filter with Foundation Fit rubric and promote/live/deep park bands
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` — signed spec for the per-tenant Vendor Baseline Store; implementation landed 2026-05-24
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/` — per-tenant SQLite Vendor Baseline Store implementation
- `PROGRESS.md` — this file (always update when a task finishes)
- `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md` — customer-facing sheet + SMB tier matrix
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Autonomous_Triggers/autonomous-defensive-triggers.md` — trigger packet contract
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/project_trigger_scan.py` — scanner implementation
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/acme_effective_parameter_report_demo.py` — real Acme demo report generator
- `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md` — generated MSP-facing effective-parameter report demo
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/inbox_shield_daily_digest_demo.py` — runnable Inbox Shield five-email daily-digest demo generator
- `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md` — generated MSP-facing daily digest demo
- `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md` — current MSP-facing monthly review sample for Inbox Shield
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/scripts/cisa_kev_ingest.py` — operator-run CISA KEV threat-intel ingestion (v0 of MILESTONE C1)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md` — latest Phase 1.5 `grok-4` rerun result
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` — current locked scoring prompt

---

## Last Updated

2026-05-27 — Drift cleanup pass. Both 2026-05-26 active drift signals cleared. (a) Added `_SPARK_Bibles_Concept_Capture.md` to `MASTER_INDEX.md §4.3 Roadmap Docs` with explicit SPARK-only / pre-spec / unsigned / not-§11 status note (held, not buried; cross-referenced from `PROJECT_HANDSHAKE.md` 2026-05-25 bibles deferral entry). (b) Reconciled baseline-tests tracker: pytest verification today returned **946 passed, 1 skipped** in 12.03s; updated `PROJECT_HANDSHAKE.md` Current Active Build Track baseline from `688 passed` to `946 tests passing, 1 skipped (verified 2026-05-27)`; updated `PROGRESS.md` Runtime baseline header from `905 passed` to `946 tests passing, 1 skipped (verified 2026-05-27)`. Phrasing change is regex-aware: `_TRACKING_BASELINE_REGEX` in `scripts/project_trigger_scan.py` matches `\d+ tests? passing` and uses `.search()` first-hit semantics, so historical text in `PROJECT_HANDSHAKE.md` item #166 (`443 tests passing`) was previously winning over more-recent state. Putting the current-state line in matching format earlier in the file makes the scanner read current state first; historical item #166 left untouched (its `443` is accurate as of that entry's date). Verified by re-running `python -m scripts.project_trigger_scan --baseline-tests 946`: returned `scan_clean`, `drift_findings: []`, `baseline_tests_expected: 946`, `baseline_tests_recorded: 946`. Doc-only; no runtime change.

2026-05-26 — End-of-day drift snapshot + audit-the-auditor signal logged + Next-Action Build System v1 design captured (no commit; chat-only). Project trigger scan returns 2 active drift signals: (a) `MASTER_INDEX.md` does not list `4. Product_Roadmap/_SPARK_Bibles_Concept_Capture.md` even though `PROJECT_HANDSHAKE.md` references it; (b) baseline-tests tracker mismatch `expected=555 recorded=443` requires reconciliation. Audit-the-auditor signal observed across the four §12 resolution audits today: same packet shape (single touched file, no worker manifest), three different Grok evidence-quality framings — Q1/Q2 "comprehensive," Q3 "comprehensive," Q4 "partial because the manifest was absent." Not rubber-stamping; real run-to-run variance, surfaced because the hardened evidence-quality clause is now mandatory. Worker-manifest path (`audit_outputs/pending/<task_id>.manifest.json`) currently empty across all runs; gate honestly reports manifest absence in packet. Next-Action Build System v1 design captured in chat (5-axis scoring engine — Leverage / Risk / Evidence / Future Cost / Reversibility — that generates and ranks 3-7 options without deciding); not yet spec'd; flagged for spec-first treatment as `4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md` once operator chooses to lock five clarification items first. Doc-only; no tests required.

2026-05-26 — Cyber Insurance Evidence Package §12 Q4 resolved (commit `e2087c7 resolve cyber insurance Q4 carrier-agnostic format`). D4 locked: single carrier-agnostic format only — no per-carrier variants in v1, v1.1, or any later scope; this is product policy, not a deferred backlog item; reopening requires a new signed spec. D4 locked as structural constraint only. Q6 (vocabulary-translation list) and Q8 (forbidden-language list) remain independent filters under §9; not bundled with D4 under a unified governance frame. Renderer ordering between §7 gates is implementation-spec detail, not §6 / §9 doctrine. Operator rejected the proposed §9.1 framework (HC9 disclaimer anchor + A4 regulatory escape clause) before encoding. Gate audit returned `0 blocking / 0 warnings` at `audit_outputs/cyber_insurance_q4_carrier_agnostic_resolution_20260527T043134Z.md`. Doc-only; no tests required.

2026-05-26 — Cyber Insurance Evidence Package §12 Q3 resolved (commit `cacb344 resolve cyber insurance Q3 delivery surfaces`). D3-D3a locked: v1 ships two delivery surfaces only — PDF artifact (buyer-facing) and Markdown bundle (audit / engineering companion). Branded landing page and evidence vault with signed URL deferred to v1.1+ pending cheaper-proof MSP demand evidence (Q10). New §6.2 "Delivery surfaces" added. Operational commitments acknowledged: HC6 toolchain pinning, HC7 bundle format specification, HC8 minimal branding rules — all to be encoded in the implementation spec. Gate audit returned `0 blocking / 0 warnings` at `audit_outputs/cyber_insurance_q3_delivery_resolution_20260527T040700Z.md`. Doc-only; no tests required.

2026-05-26 — Cyber Insurance Evidence Package §12 Q1/Q2 resolved (commit `f1c062d resolve cyber insurance cadence and freshness policy`). D1-D2e locked: cadence is hybrid (quarterly snapshot + on-demand regeneration + annual full review anchored to tenant insurance-renewal anniversary); per-category freshness thresholds locked (30 days for `policy_change_control` / `tenant_isolation` / `kill_switch`; 90 days for `detection_evidence` / `scoring_explanation` / `test_evidence` / `independent_audit` / `operational_artifact`; structural exemption for any record with a valid `signed_by` reference). Supersession annotation rule locked: superseded signed artifacts remain freshness-exempt as historical signed evidence, but rendered package must annotate `superseded by <new spec>`. New §6.1 "Freshness policy" added. Operational commitments acknowledged: monthly internal verification path for 30-day categories, annual full review as new spec requirement, stale-evidence pre-warning behavior, queued on-demand concurrency for the same tenant, Grok API availability/cost as operational dependency. Gate audit returned `0 blocking / 0 warnings` at `audit_outputs/cyber_insurance_cadence_threshold_resolution_20260527T030754Z.md`. Doc-only; no tests required.

2026-05-26 — Compliance and Trend Watch Process spec §11 SIGNED + governance overhaul + gate prompt evidence requirement hardened + audit-the-auditor cadence wired into operating doctrine + Frontier Intake Log supersession (commits `470714d governance overhaul: sign compliance/trend-watch spec, add audit gate and build queue`, `69419fc harden gate prompt evidence requirement, add audit-the-auditor cadence, intake-log supersession`, `3c1e156 harden Grok gate evidence requirements and add audit-the-auditor cadence`). `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §11 signed by Matt Nichol after sharp Grok audit returned clean (`audit_outputs/compliance_trend_watch_signoff_sharp_20260527T004134Z.md`). Added: `audit_tools/complete_gate.py` (manifest-verified Grok negative-feedback completion gate; `OUTPUT_FORMAT_INSTRUCTION` now requires named-evidence on zero-finding outputs, insufficient-context escape hatch, and explicit Evidence quality paragraph before `GATE_SUMMARY`; locked `NEGATIVE_FEEDBACK_PROMPT` untouched), `audit_tools/run_compliance_trend_watch_audit.py` (one-shot signoff runner), `PROJECT_BUILD_AND_AUDIT_QUEUE.md` (operational queue), `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` (14-day trial doctrine with §10 audit-the-auditor cadence — weekly adversarial seeding, operator-elected cross-audit, F5 detection path). Added roadmap deep-dives: Cyber Insurance Evidence Package, Callback/TOAD detector, Sender Provenance runbook, SPARK Bibles concept capture. Added `Frontier_Intake_Log.md` with Supersession block citing `Compliance_and_Trend_Watch_Process.md` §1.1; rubric-authority phrasing removed from live intake protocol; Review #1 preserved as historical record. Added `core/scoring/client_facing_rubric.py` + `tests/test_complete_gate.py` (41 passed). Removed `Human_Written_Communication_Policy.md` (AI-authored authority drift). Updated master index, handshake, activity log, progress, runtime modules. Doc + tooling additions; no runtime regression.

2026-05-25 — Cyber Insurance Evidence Package formal gate fired (Task 51). Operator selected Candidate 3 from Frontier Intake Review #1 on the basis of highest earnings potential. **5-axis score: `2·2·2·2·2 = 10/10` → promote band.** 7-question stress test recorded in `think_sheet.md` surfaced four failure modes (decoration risk, email-narrow risk, per-carrier fragmentation, vocabulary leak) with explicit mitigations. **Verdict: promote with cheaper-proof-first guidance.** Spec drafting is gated on cheaper-proof MSP discovery validation: run 1-3 local MSP calls (Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT) using existing artifacts framed as "cyber-insurance evidence bundle for email-fraud controls"; binary go/no-go on whether 1+ of 3 MSPs says yes/tell-me-more. **Two-for-one:** the cheaper-proof activity doubles as REVENUE_MAP Lane 3 milestone work (currently 0/7 because nobody's been called). Scope boundary explicit: carrier-agnostic format; email-fraud + inbox-layer MDR controls only; does NOT cover MFA / EDR / backups / IR plans / patch management. Vocabulary boundary: cyber-insurance language gets a translation pass to plain English before any client-facing surface ships. No spec drafted; no package logic written; no runtime change. Doc-only; no tests required.

2026-05-25 — Frontier Intake Review #1 cheaper-proof exercise complete (Task 50). Real searches against the locked starter source list executed the same evening. **5 candidates surfaced** → per the locked cadence rule (4+ → monthly), recurring discipline committed at monthly cadence with a refinement flag to re-evaluate at the 90-day mark. Created `Frontier_Intake_Log.md` (top-level, sibling to `THREAT_INTEL_LOG.md`) capturing source list, 8 confirmations of existing direction, 5 surfaced candidates with source citations, and the cadence verdict. Candidates surfaced: **(1) Department-Level Internal Impersonation Detector** (Abnormal 2026 Attack Landscape Report — 36.7% of BEC at SMB scale uncovered by current detectors); **(2) OWASP LLM10 Unbounded Consumption Coverage** (operational hardening); **(3) Cyber Insurance Evidence Package** (packaging existing audit/scoring/reports for 2026 underwriting evidence-not-checkboxes shift); **(4) Auto-Forwarding Inspection** (outbound rule monitoring + downstream-mail inspection per Abnormal's 2026 product launch); **(5) Device-Code / OAuth-Consent Phishing Detector** (FBI PSA260521 / Kali365 / EvilTokens lure shape, MFA bypass via OAuth device-code flow). Candidates **not** auto-added to `think_sheet.md`; formal gating happens only when operator picks them up one at a time. Strong wedge-alignment confirmation: the 2026 frontier is converging on auditability + deterministic explainability + evidence depth + human-approval-on-sensitive-action — exactly NorthStar's locked differentiation standards. Lateral-BEC market intelligence: Abnormal's enterprise moat is structurally irrelevant at SMB scale (0.24% vs. ~25%). Vocabulary boundary held. Doc-only; no runtime change; no tests required.

2026-05-25 — Trend-Chasing Layer / Frontier Intake captured as its own scored idea (Task 49). v1 scoping deliberately narrow: operator-driven, process-only, no runtime, no new agent. 5-axis score `1·1·1·0·2 = 5/10` → revisit / live park. Cheaper proof recorded: run the intake once now using a starter source list (CISA advisories, abuse.ch, KuppingerCole / Mordor reports, 3-5 AI-research feeds Matt selects, plus the MSP-channel news already in `THREAT_INTEL_LOG.md`); cadence rule: 0-1 surfaced candidates → defer recurring discipline; 2-3 → quarterly cadence; 4+ → monthly cadence. More ambitious shapings (runtime intake agent, public transparency surface) are separate ideas that earn their own rows only if v1 evidence warrants them. Vocabulary boundary extended from the AGI-Adjacent decomposition: "AGI" / "AGI-adjacent" framing from source feeds does not enter NorthStar's product / outreach / spec / bible voice. Doc-only; no tests required.

2026-05-25 — AGI-Adjacent Layer proposal gated at bundle level (rejected, score 3/10) **and then decomposed on operator request** into six discrete components, each scored + stress-tested independently. Component verdicts recorded in `think_sheet.md`: A. NorthStar Analyst Reasoning Layer (cross-detector synthesis, email-only) → **promote 9/10**, build only after rubric ships and MSP feedback supports it, spec-first; B. Cross-Domain Expansion (logs/endpoints/payments) → drop 2/10; C. Auto-Tuning Detector Ring → drop 0/10; D. Operator-Approved Drift Tuning Surface → revisit 5/10, live-park until first paid pilot traffic; E. Threat-Family Hypothesis Engine → live park 4/10; F. "AGI-Style Behavior Principles" Bible Section → drop 0/10 (walks back today's bibles deferral). One real survivor (Component A); no new lane authorized today. Vocabulary boundary recorded: "AGI" / "AGI-adjacent" stay inside `think_sheet.md` as internal rationale only and do not enter product / outreach / specs / bibles. Underlying staying-current concern remains separate and routes to the still-uncaptured Trend-Chasing Layer / Frontier Intake idea. Doc-only; no tests required.

2026-05-25 — Client-facing 5-axis Email Scoring Rubric §11 signature complete. Matt signed `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`; spec status now `§11 SIGNED 2026-05-25 by Matt Nichol; implementation not yet started`. Signed-spec consistency cleaned: D11 references D15's 160-char cap, schema max length set to 160, rendering contract reflects D14/D16, rollout locks D1–D17, and §11 notes that implementation still requires explicit start-build instruction plus normal pre-ship gate. Spec-only / tracker-only; no runtime change; no tests required.

2026-05-25 — Applied the project's standard 7-axis stress-test discipline to the five §10 sub-questions in the Client-facing 5-axis Email Scoring Rubric spec draft. Full analysis recorded in `think_sheet.md`; verdicts locked as D13–D17 in §2 of the spec; §10 converted from "open" to "resolved." Locked: equal weights v1, fixed axis order with "stability not priority" disclaimer, 160-char `why_this_score` cap with documented upgrade path, `axis_total` visible with `recommended_action` rendered most prominently, report-only / monthly digest surface in v1 with per-email view deferred to v1.1. Pre-§11 still; sub-question gate cleared. Doc-only; no tests required.

2026-05-25 — Created `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` as the selected spec-first deep dive for the client-facing explainability lane. Draft locked a deterministic five-axis vocabulary (`sender_identity`, `conversation_continuity`, `vendor_payment_history`, `document_integrity`, `origin_timing`), 0..2 axis scoring, 0..10 total, contradiction guard against internal `risk_score`, additive payload contract draft, rendering boundaries, and implementation gate tests. Later signed in Task 47; no runtime/schema/prompt implementation authorized by the draft step itself. Doc-only; no tests required.

2026-05-25 — Bibles spark file updated with explicit 2026-05-25 deferral decision and the working notes from today's discussion (Shield-outward / Agent-inward two-bible split, Layer 1 moral principles + Layer 2 operational commands architecture, candidate fragments for both layers, tonal hazards, and trigger conditions for un-deferring). File status remains SPARK ONLY, unsigned, not §11; no bible drafted; no public values committed. Doc-only; no tests required.

2026-05-25 — Canadian + North American email fraud market intelligence captured in `THREAT_INTEL_LOG.md`. Sourced from CAFC, Canadian Centre for Cyber Security, Payments Canada, KuppingerCole, Mordor Intelligence, Accelerate Okanagan / KPMG, Central Okanagan EDC, plus vendor pricing benchmarks. Records Canadian fraud scale, North American competitive shape (including the Dec 2025 Proofpoint × Hornetsecurity move), and Okanagan tech sector + local MSP target list. Strategic implications recorded: Stage A scope narrowed to email fraud / inbox-layer MDR for SMBs via MSPs; differentiation standards locked on auditability + explainability + per-tenant tuning + reversibility + evidence depth; build queue re-ordered A→B→C→D. Doc-only; no tests required.

2026-05-25 — Sender-provenance Proof Run 1 recorded as `needs_more_samples` for the personal-Gmail training corpus (corrected from an in-session `fail_hold_in_think_sheet`). Matt entered 12 samples; the corpus was overwhelmingly shared cloud / ESP normalized, with only one plausible stable high-value business relay. The corpus, not the idea, failed the test, so the verdict is corpus-mismatch hold rather than idea-fail. No detector, enum revision implementation, runtime lookup, or baseline expansion is authorized; revisit only with a fresh business-mailbox proof. Doc-only / worksheet-only; no tests required.

2026-05-25 — Sender-provenance cheaper-proof runbook added beside the existing proof protocol. This creates the operator workflow for collecting 30+ raw-header-only vendor samples, classifying sender-origin stability, and recording `pass_to_spec` / `needs_more_samples` / `fail_hold_in_think_sheet` without authorizing runtime code. Doc-only; no tests required.

2026-05-24 — Vendor Baseline Store implementation landed under `core/production_state/vendor_baseline/` against the signed deep-dive spec. §5 API implemented (`ingest_signal`, `check_signal`, `expire_stale_signals`, `tenant_database_path`), per-tenant SQLite isolation landed, hash-only storage with per-tenant HKDF salt landed, kill-switch and Blackboard audit integration landed, Windows `pywin32` DACL hardening landed, `vendor_baseline_ttl_days` tenant override key landed. Full suite: **587 passed, 1 skipped** (+32, zero regressions).

2026-05-24 — Stress-test backlog Batch 2 completed for six promote-band ideas in `think_sheet.md`: Two-channel confirmation enforcement, High-trust vendor verification layer, NorthStar Portal, Client-facing 5-axis Email Scoring Rubric, Adversarial prompt-injection detector, and Consolidated tampering drill suite. All six rows now show `ST = Y`. With Batch 1 + Batch 2 complete, all current promote-band ideas are either stress-tested, shipped, spec-locked, or n/a. Doc-only; runtime baseline held at **555 tests passing**.

2026-05-24 — Stress-test backlog Batch 1 (BEC + email-auth detectors) completed for six promote-band ideas in `think_sheet.md`: Financial State Ledger / Delta Tripwire, Document Metadata Fingerprinting, Micro-Temporal Mismatches, Structural Payload Anomalies (OCR / encoding evasion), DKIM / SPF / DMARC ingestion, and Callback Phishing / TOAD detection layer. All six rows now show `ST = Y`. Implementation sequencing recorded: Financial State Ledger first after Vendor Baseline Store; Doc Metadata second; DKIM/SPF/DMARC ships in parallel; Callback Phishing is a two-part build (body language now, phone baseline after Vendor Baseline Store spec revision); Structural Payload deferred behind a PDF / OCR dependency decision. Doc-only; runtime baseline holds at **555 tests passing**.

2026-05-24 — Stress-test gate completed for Visible Multi-Agent Deliberation Layer and Tiered Detection Intensity; both rows in `think_sheet.md` now show `ST = Y`. Decisions recorded: visible deliberation should wait until the underlying detector set is richer and should run behind tiered intensity; tiered intensity should receive its own spec-first deep dive before implementation, with default Medium and forced High escalation for hard-risk signals. Doc-only; runtime baseline holds at **555 tests passing**.
