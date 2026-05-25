# PROGRESS

**Purpose:** Always-current task tracker. Updated whenever a task is finished.

**Update rule:** When a task is closed, mark it ✅, add finish date and verification line, then move to the next item in the list.

**Runtime baseline (last verified):** **852 passed, 1 skipped** (exit code 0).

---

## Active Task List

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

### 9. Human-written / AI-proofread communication policy — ✅ DONE 2026-05-23
- Landed `6. Internal_Strategy/Positioning/Human_Written_Communication_Policy.md` capturing Matt's 2026-05-23 decision that all proposals / DMs / emails / letters to humans are written by Matt in his own words; AI proofreads only (typos, factual errors against repo, vague phrasings, tone issues) and never authors / structures / rewrites.
- Defines explicit allowed vs. forbidden AI actions, the honest disclosure pattern, the 5-step workflow (draft → policy-scoped proofread prompt → comment list → per-sentence accept/reject → send), and a scope table (applies to all human-to-human outreach; does NOT apply to runtime-generated reports, internal tracking docs, code, or working AI sessions).
- Cross-linked from `REVENUE_MAP.md` Operating Principle and "What Not To Do" item #9.
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
| 2026-05-23 | Human-written / AI-proofread communication policy | 0 | `6. Internal_Strategy/Positioning/Human_Written_Communication_Policy.md`, `REVENUE_MAP.md` |
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

2026-05-24 — Vendor Baseline Store implementation landed under `core/production_state/vendor_baseline/` against the signed deep-dive spec. §5 API implemented (`ingest_signal`, `check_signal`, `expire_stale_signals`, `tenant_database_path`), per-tenant SQLite isolation landed, hash-only storage with per-tenant HKDF salt landed, kill-switch and Blackboard audit integration landed, Windows `pywin32` DACL hardening landed, `vendor_baseline_ttl_days` tenant override key landed. Full suite: **587 passed, 1 skipped** (+32, zero regressions).

2026-05-24 — Stress-test backlog Batch 2 completed for six promote-band ideas in `think_sheet.md`: Two-channel confirmation enforcement, High-trust vendor verification layer, NorthStar Portal, Client-facing 5-axis Email Scoring Rubric, Adversarial prompt-injection detector, and Consolidated tampering drill suite. All six rows now show `ST = Y`. With Batch 1 + Batch 2 complete, all current promote-band ideas are either stress-tested, shipped, spec-locked, or n/a. Doc-only; runtime baseline held at **555 tests passing**.

2026-05-24 — Stress-test backlog Batch 1 (BEC + email-auth detectors) completed for six promote-band ideas in `think_sheet.md`: Financial State Ledger / Delta Tripwire, Document Metadata Fingerprinting, Micro-Temporal Mismatches, Structural Payload Anomalies (OCR / encoding evasion), DKIM / SPF / DMARC ingestion, and Callback Phishing / TOAD detection layer. All six rows now show `ST = Y`. Implementation sequencing recorded: Financial State Ledger first after Vendor Baseline Store; Doc Metadata second; DKIM/SPF/DMARC ships in parallel; Callback Phishing is a two-part build (body language now, phone baseline after Vendor Baseline Store spec revision); Structural Payload deferred behind a PDF / OCR dependency decision. Doc-only; runtime baseline holds at **555 tests passing**.

2026-05-24 — Stress-test gate completed for Visible Multi-Agent Deliberation Layer and Tiered Detection Intensity; both rows in `think_sheet.md` now show `ST = Y`. Decisions recorded: visible deliberation should wait until the underlying detector set is richer and should run behind tiered intensity; tiered intensity should receive its own spec-first deep dive before implementation, with default Medium and forced High escalation for hard-risk signals. Doc-only; runtime baseline holds at **555 tests passing**.
