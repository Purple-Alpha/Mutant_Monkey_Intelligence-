# Email Security Testing & Evidence Framework — Deep Dive

**Status:** DRAFT (pre-§11). Authored 2026-05-30 by Cursor (Claude) on Matt Nichol's instruction. No runtime code in this artifact. No test harness implementation in this artifact. §11 signature blank by design; only Matt may sign.

**Scope reminder:** Specifies the **testing, validation, evidence, scoring, failure-analysis, and continuous-improvement framework** for NorthStar's email-security runtime. Wraps and disciplines the existing eval harness (`core/scoring/eval/`), `REACTION_TIMING_TEST_LOG.md`, the Cyber Insurance Evidence Package §14 Stage A test plan, and any future evaluation surface. Does **not** add new runtime detectors, create a new product, or claim NorthStar is compliant, certified, insurer-approved, bulletproof, or prevents fraud.

**Selected by:** Matt Nichol on 2026-05-30 (after TOAD pass 2 tracker-baseline bump `c2ff29f`) to close a correctness gap surfaced during pass-2 review: the existing evaluation surface can silently score a non-observable category as a `0` and thereby mis-report capability. This draft formalises a four-value status discipline that forbids that failure mode. Verbatim operator intent is preserved in the corresponding `PROJECT_ACTIVITY_LOG.md` entry.

---

## §1 Purpose + Scope

### Purpose

Define a single, durable framework that lets NorthStar prove six things about its own email-security runtime — *honestly*:

1. **Detection correctness** — did NorthStar classify the email correctly?
2. **Precision** — when NorthStar flagged something, was it actually suspicious?
3. **Recall** — did NorthStar catch the suspicious emails it was supposed to catch?
4. **Evidence quality** — can every score be traced back to real evidence?
5. **Confidence quality** — was NorthStar appropriately confident, or dangerously overconfident?
6. **Improvement over time** — when it fails, can we fix it, retest it, and prove the fix worked?

It enforces a single rule that the rest of the spec follows from: **a category NorthStar cannot currently observe must be marked `not_supported_yet` or `not_evaluated`, never scored as `0`, never counted against accuracy.**

### In scope (v1)

- Capability registry + four-value category status model (`supported`, `not_supported_yet`, `not_present_in_sample`, `evidence_missing`); five-value verdict enum (`legitimate`, `needs_review`, `high_risk`, `blocked_or_hold_recommended`, `unknown`) with per-case `verdict_match`.
- Four test levels (smoke / regression / adversarial / red-team) with explicit safe-test-data sources and a hard fixtures-only boundary.
- Auto-trigger cadence (§4.5), commit-completeness gate (D19), conjunctive failed-test acceptance rule (D20), v1 path × tier matrix (§4.5.8 / D21), and v1 enforcement authority on `audit_tools/pre_ship_audit.py` (§4.5.9 / D22) so the cadence is operable on a specific gate from day one.
- Metrics — accuracy, precision, recall, FPR, FNR — **computed only over `supported` categories**; companion `capability_coverage` metric for not-supported categories.
- Four-bucket confidence calibration (`low` / `medium` / `high` / `overconfident`).
- Evidence-bundle schema; append-only audit-trail event schema; structured decision-transparency format (no chain-of-thought).
- Failure-analysis card schema (mandatory before retest), retest-and-improvement loop with deterministic linkage, Unknown Discovery Rate as first-class metric, optional / additive / non-overriding reviewer notes, v1 dashboard metric set.

### Out of scope (v1)

- Any new runtime detector — framework consumes detector output, it does not produce it.
- Replacement of `core/scoring/eval/` — existing harness is a building block; this framework wraps it.
- Live email rewriting / blocking / quarantine / any client-facing send action — NorthStar remains advisory in v1.
- LLM-driven test-case generation — v1 uses hand-curated synthetic fixtures only.
- Production telemetry ingestion — v1 reads test fixtures from disk; does not read tenant production data.
- A new spec for test-data generation — v1 reuses `fraud_eval_dataset.jsonl` and existing reaction-timing fixtures.
- Dashboard UI rendering technology — v1 defines metric shape only.
- Cross-product testing (calls / SMS / voice / browser) — out of scope by §1.3 safety boundary.

### §1.3 Safety boundaries (the framework MUST NOT)

- **MUST NOT** execute live malware, real malicious URLs, real credential-harvest pages, or perform unauthorized third-party testing (no probing of vendor systems, no unauthorized phishing of any real person, no scans of external infrastructure) in any environment, including isolated sandboxes, in v1.
- **MUST NOT** ingest, transmit, or persist real customer email content. Test fixtures must be synthetic and live under the runtime test tree. No outbound network calls during test execution — the runtime is offline-by-construction and the framework inherits that boundary.
- **MUST NOT** expose raw chain-of-thought from any LLM call in any evidence bundle, audit-trail event, failure card, reviewer note, or dashboard metric. Structured fields only.
- **MUST NOT** report any aggregate metric (accuracy, precision, recall, FPR, FNR) that includes `not_supported_yet` or `evidence_missing` cases in the denominator without an explicit, named "capability-coverage" framing.
- **MUST NOT** claim NorthStar is "compliant", "certified", "insurer-approved", "bulletproof", "fraud-proof", "AI-proof", "zero-trust certified", or any equivalent forbidden phrase. Forbidden-language scope inherits from `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md`.
- **MUST NOT** be used to authorize a §11 spec signature, a build-queue promotion, or a commit. Test verdicts inform decisions; Matt makes decisions.

---

## §2 Locked Design Decisions

These decisions are advisory until §11 is signed; once §11 is signed they become immutable except by explicit operator-instructed revision.

- **D1. Category status enum is exactly four values** — `supported`, `not_supported_yet`, `not_present_in_sample`, `evidence_missing`. No fifth value, no collapsing. A category whose runtime support landed yesterday but whose evidence bundle for *this* case is empty is `evidence_missing` — never `supported`.
- **D2. Verdict enum is exactly five values** — `legitimate`, `needs_review`, `high_risk`, `blocked_or_hold_recommended`, `unknown`. The pair `safe`/`unsafe` is forbidden because email fraud is often ambiguous and `needs_review` is the safety-relevant middle band.
- **D3. Accuracy denominators include only `supported` categories.** Accuracy / precision / recall / FPR / FNR are computed strictly over `supported` categories for the case. `not_supported_yet`, `not_present_in_sample`, and `evidence_missing` contribute to capability-coverage, not accuracy.
- **D4. Evidence required for every score.** A score without a referenced evidence-bundle entry is `evidence_missing` and excluded from accuracy denominator. No opt-out.
- **D5. No chain-of-thought exposure.** Decision transparency is structured-fields-only: `rule_fired`, `evidence_tags`, `signals_observed`, `signals_missing`, `decision_path_summary` (≤280 chars). Raw LLM `reasoning` / `thinking` strings forbidden in every framework surface.
- **D6. v1 test-data sources are exactly the operator-listed five** — `.example` domains, fake vendor names, fake URLs / inert attachments, synthetic `.eml` fixtures, lab mailbox only. No real malware, no real credential-phishing pages, no unauthorized third-party testing.
- **D7. v1 implementation scope is exactly the operator-listed eight items** — synthetic-fixture eval harness wrapper, confusion matrix, per-category supported/not-supported scoring, evidence-required validation, failure-report generation, retest linkage, precision/recall/FP/FN metrics, Unknown Discovery Rate counter. Nothing else ships in v1.
- **D8. Verdict vocabulary aligns with `REACTION_TIMING_TEST_LOG.md` where it overlaps.** Per-test record verdicts reuse `pass`, `partial`, `fail`, `blocked`; case-level adds `verdict_match` ∈ {`exact`, `adjacent`, `mismatch`, `unscored`} as the precision/recall pivot.
- **D9. Failure-analysis card is mandatory before retest.** A failing case cannot be retested through the official loop without an attached, completed card; attempts without one are `not_eligible_for_closure`.
- **D10. Forbidden-language enforcement is identical to NorthStar's existing standard.** Inherits the forbidden-vocabulary list from `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` verbatim; dashboard / failure-card / audit-trail / reviewer-note text all in-scope for the same lint.
- **D11. Capability registry is append-only at status level.** Adding a not-supported entry is free. Promoting → `supported` requires citing the §11-signed runtime spec. Demoting `supported` → `not_supported_yet` requires an operator-recorded incident in `PROJECT_ACTIVITY_LOG.md` and is high-severity drift.
- **D12. Confidence calibration uses a four-bucket reliability model** — `low`, `medium`, `high`, `overconfident`. v1 does not ship a continuous probability score; bucket boundaries are in §8.2.
- **D13. Reviewer notes are optional, additive, scope-bounded, never override the verdict.** Fields: `initials` (2-4 chars), `recorded_at_utc`, `scope` ∈ {`evidence`, `verdict_comparison`, `failure_card`, `dashboard_metric`}, `comment` (≤600 chars). Verdict field immutable from the reviewer surface.
- **D14. Unknown Discovery Rate is a first-class metric.** A run that surfaces a failure mode not in the registry increments UDR for the run and emits a single `udr_event` audit record naming the unseen mode. Reported alongside accuracy in v1 dashboards.
- **D15. Framework verdicts do not authorize operator action.** "All green" is not authorization to ship, promote a queue item, or sign a §11 spec. Verdicts inform; Matt decides.
- **D16. Testing is part of the build lifecycle, not an operator reminder.** "Ran the required test tier" is a precondition for commit completeness — not a separate manual step the operator must remember between writing code and `git commit`. Full auto-trigger contract is §4.5.
- **D17. Auto-trigger cadence is closed and enumerated in §4.5.** Smoke / regression / adversarial / eval-corpus paths and conditions are exactly §4.5.1–§4.5.4. Adding or removing a trigger condition requires a §11-revision cycle. Not configurable per-developer or per-branch in v1.
- **D18. Red-team tests do not auto-run live.** Scheduled monthly, controlled / synthetic unless operator-authorized; live third-party probing remains forbidden by §1.3 regardless of schedule.
- **D19. Commit completeness gate.** No detector / scoring / rendering / schema / production-loop / agent-orchestration / evidence-packaging commit may be marked complete unless the required test tier ran and its result is recorded in the audit trail per §9.2. "Marked complete" = passes `audit_tools/pre_ship_audit.py` with `VERDICT: SHIP` (v1 enforcement authority — see D22). Rule itself is locked here; v1 surface is §4.5.9.
- **D20. Failed-test acceptance is conjunctive, not disjunctive.** If a required test fails, the build can still continue only if **all four** of these conditions are met: (a) the failure is recorded in the per-case evidence bundle per §9.1 plus the audit-trail per §9.2; (b) the failure is classified in a failure-analysis card per §9.4 with a named failure-type value from the closed enum `{verdict_mismatch, overconfident, evidence_missing, schema_violation, scope_violation}`; (c) the operator accepts the failure explicitly with a signed acceptance entry in `PROJECT_ACTIVITY_LOG.md` (or via the named-reason override path on `pre_ship_audit.py`); (d) a retest item is created with the failure card's `Decision` field set to `retest_required` and the retest scheduled per the §9.5 loop. Missing any one of the four conditions blocks the commit unconditionally; partial satisfaction is not partial acceptance.
- **D21. v1 Auto-Trigger Path Matrix is locked in §4.5.8.** Resolves Q8. The matrix in §4.5.8 is the authoritative path × tier intersection that decides, for any given diff, which of smoke / regression / adversarial / eval-corpus is required, whether the full pytest suite is required, and whether failure-analysis + retest records are required. Twelve surfaces are enumerated: detector logic, scoring logic, rubric mapping, rendering / digest / reporting, schema / model, production loop, agent orchestration, evidence packaging, test fixtures, prompt / spec-output, signed-spec changes that alter expected runtime behavior, and docs-only. Adding a new surface or changing a tier requirement requires a §11-revision cycle; v1 implementation matches the matrix exactly.
- **D22. v1 enforcement authority for D19 is `audit_tools/pre_ship_audit.py`.** Resolves Q9. `pre_ship_audit.py` is the always-on pre-commit gate that reads the audit trail per §9.2 and refuses `VERDICT: SHIP` when the required test tier for the diff (per the D21 matrix) does not have a `test_run_finished` event matching the commit's `HEAD` SHA or a fast-forward ancestor. `complete_gate.py` audits the work packet for spec / non-negotiable compliance but does **not** replace the cadence gate; the two enforcement layers are independent and additive. CI is future v1.1 / v2 layering, not v1. Operator override of a `pre_ship_audit.py` cadence-gate failure is allowed only with all D20 conjunctive conditions satisfied (recorded reason + failure classification from the closed enum + retest link + signed acceptance entry naming risk owner and hard expiry).
- **D23. Pydantic model is the authoritative v1 per-case shape.** Resolves Q2. v1 implementation defines the per-case record and evidence-bundle shapes as strict Pydantic models matching §7 / §9. Generated JSON Schema may be emitted for docs, downstream validation, or report consumers, but it is derived from the Pydantic models and is not a second source of truth. On-disk JSON / JSONL records must round-trip through the models; a generated-schema mismatch is fixed by changing the model or the generator, not by hand-editing schema.
- **D24. `confidence_bucket` boundaries are locked at `[0,25] / [26,60] / [61,100]` for `low` / `medium` / `high`; `overconfident` is the subset of `high` whose `verdict_match` is not `exact`.** Resolves Q1 (see `think_sheet.md` 7-axis stress test, 2026-05-31). v1 implementation MUST use these exact integer bounds in §8.2. Recalibration of the boundaries requires (a) ≥60 real fixture cases distributed across all four buckets, (b) a §11-revision cycle, and (c) an operator entry in `PROJECT_ACTIVITY_LOG.md` naming the empirical distribution evidence that motivates the change. Pre-§11-signature drift is forbidden; the v1 bounds ship as-drafted regardless of early fixture skew.
- **D25. `adjacent` verdict mismatches contribute zero credit to accuracy denominators.** Resolves Q3 (see `think_sheet.md` 7-axis stress test, 2026-05-31). `accuracy_supported_only` and the derived precision / recall / FPR / FNR treat any `verdict_match` ≠ `exact` as incorrect, matching the §8.1 formula already drafted. `verdict_match_distribution` (§8.5) preserves the four-value breakdown so operators see adjacent-vs-mismatch separately, without averaging it into accuracy. Rationale: partial credit produces a fuzzy denominator that hides calibration drift; the four-value distribution surface preserves the adjacency signal explicitly.
- **D26. Default regression-tolerance is `0` percentage points.** Resolves Q4 (see `think_sheet.md` 7-axis stress test, 2026-05-31). The §4.2 regression-tier rule fails any per-metric drop on a previously-passing case. Per-subcategory widening above 0 is allowed only via an explicit operator entry in `PROJECT_ACTIVITY_LOG.md` naming (a) the subcategory, (b) the tolerance value in percentage points, (c) the named rationale, and (d) a hard expiry date. Tolerance widening is high-severity drift; the default forces a conscious decision rather than silent erosion.
- **D27. Red-team mission file structure is deferred to the first real mission; the eight minimum-required fields are locked here.** Resolves Q5. The first §4.4 mission MAY choose its own organization (e.g., a Markdown narrative, a structured YAML block, or a hybrid) but MUST contain at least: `mission_id`; `scope` (in-scope categories plus explicit out-of-scope boundary); `hypothesis` (what failure mode the mission probes); `threat_model`; `controlled_synthetic_only_acknowledgement` (operator-authored sentence affirming the §1.3 safety boundaries — no live malware, no live phishing pages, no unauthorized third-party testing, synthetic fixtures only); `success_criteria`; `scheduled_for` (UTC date); `operator_authorization` (operator-authored sentence naming Matt as authorizing operator). Field shape is the mission's choice; presence of all eight is mandatory and not configurable per-mission. Field names intentionally avoid `attestation` per the inherited forbidden-language scope (D10).
- **D28. v1 dashboard ships no composite quality score.** Resolves Q6. The v1 dashboard is strictly the §8.5 metric list. No single aggregate score combines accuracy / precision / recall / FPR / FNR / UDR / capability-coverage / confidence-bucket / verdict-match metrics into one number. Rationale: a composite is the exact failure mode §3 warns against — a clean-looking metric that hides capability gaps behind averaging. A composite is deferred to v1.1+ and gated on operator-stated evidence that the §8.5 list is too noisy for monthly buyer reporting; until then the multi-dimensional surface is the contract.
- **D29. Failure cards with `failure_type` ∈ {`schema_violation`, `scope_violation`} are Decision Audit candidates; v1 only locks the trigger condition.** Resolves Q7. v1 marks qualifying cards by recording a non-null `decision_audit_candidate_id` (nullable string) on the failure card and on the corresponding `failure_card_opened` audit-trail event. The packet shape, the runner integration with `audit_tools/decision_audit_runner.py`, and any dashboard surface for outstanding candidates are v1.1 work and require their own §11-signed spec. v1 does not run the integration; v1 only marks candidates and preserves the linkage so downstream consumers can find them.

---

## §3 Core Philosophy

The framework follows one design rule: **honesty about capability is more valuable than a clean-looking score**. The operative failure mode the framework prevents: a test surface that quietly scores a non-observable category as `0`, then reports the resulting "97% accuracy" as if NorthStar inspected every category. That metric would be a lie.

Three corollaries: **capability boundaries are surfaced, not hidden** (registry is public, on-disk, version-controlled, appears in every test-run summary); **evidence is the unit of trust** (a score without referenced evidence is `evidence_missing`, enforced at write-time); **improvement is a loop, not a moment** (failure card opens it, fix closes it, retest proves it, audit trail preserves the path). The four-value status enum, the evidence-required rule, and the no-chain-of-thought rule are structural and survive §11 signature unchanged.

---

## §4 Test Levels

v1 defines four test levels. Each has a fixed input source, evidence-bundle requirement, and reviewer expectation.

### §4.1 Smoke tests

- **Purpose:** prove the runtime starts, ingests a known-good fixture, runs the scoring agent, returns a structured analysis payload, and writes the expected audit records.
- **Input source:** a single hand-curated `.eml` fixture per detector with deterministic content.
- **Cadence:** every commit on any branch that touches `core/`.
- **Pass condition:** scoring agent returns a structurally valid `EmailAnalysisPayload` and the expected number of audit records appear in the test blackboard.
- **Evidence-bundle requirement:** minimal — the fixture path and the structural-validation summary.
- **Reviewer expectation:** no human review; CI-only gate.

### §4.2 Regression tests

- **Purpose:** prove that previously-passing cases still pass after a code change. Pin behavior on the closed set of fraud/legit subcategories already covered by `core/scoring/eval/fraud_eval_dataset.jsonl` (40 cases at v1 start).
- **Input source:** the existing JSONL eval dataset plus any new cases formally promoted into the dataset by a separate §11-signed change to the dataset.
- **Cadence:** every PR; full nightly run on the active branch.
- **Pass condition:** confusion matrix matches the recorded baseline within the configured tolerance; per-subcategory recall ≥ the published floor; no new `not_supported_yet`-flagged case silently scored.
- **Evidence-bundle requirement:** per-case evidence bundle (see §9.1).
- **Reviewer expectation:** operator-eyes-on for any matrix delta beyond tolerance.

### §4.3 Adversarial tests

- **Purpose:** intentionally try to break the runtime under input shapes designed to expose failure modes (over-lift, false positives on benign mail, over-confidence on ambiguous mail, schema mismatch, default-off leakage). The TOAD pass-2 break-it suite (`tests/test_callback_phishing_break_it.py`) is the v1 reference shape.
- **Input source:** hand-curated adversarial fixtures grouped by attack pattern; safe-test-data rules in §5 apply unconditionally.
- **Cadence:** triggered manually by the operator before any signed-spec amendment lands and before any pre-release tag.
- **Pass condition:** no test fails; any new failure mode surfaced is filed as a UDR event and a failure-analysis card before the run is declared closed.
- **Evidence-bundle requirement:** per-case evidence bundle plus an adversarial-intent note describing what the case was trying to prove.
- **Reviewer expectation:** operator-eyes-on for every closure.

### §4.4 Red-team tests

- **Purpose:** simulate a coordinated adversary trying to defeat NorthStar end-to-end against a tenant configuration the operator names in advance. v1 red-team tests are **simulation only** — they run against synthetic tenants seeded inside the runtime test tree, never against live tenants, never against live infrastructure.
- **Input source:** an operator-authored red-team mission file naming the tenant fixture, the attack sequence, the expected detection points, and the safety-boundary opt-outs that the simulation honors.
- **Cadence:** operator-scheduled monthly per §4.5.5; not auto-triggered live.
- **Pass condition:** documented per-mission; v1 ships no general red-team pass condition.
- **Evidence-bundle requirement:** mission file + per-step evidence bundle + post-mission failure-card set + UDR summary.
- **Reviewer expectation:** operator-eyes-on for every mission; v1 does not authorise unattended red-team runs.

### §4.5 Auto-Trigger Cadence & Enforcement

**Premise (D16):** Test execution is part of the build lifecycle, not an operator reminder. The framework treats "the required test tier ran and its result was recorded" as a precondition for commit completeness. The four auto-trigger contracts in §4.5.1–§4.5.4 are closed per D17; the path × tier matrix is §4.5.8 (D21); v1 enforcement authority is `pre_ship_audit.py` per §4.5.9 (D22). The cadence is not configurable per-developer or per-branch in v1; adding or removing a trigger condition requires a §11-revision cycle.

**Note:** The §4.5.1–§4.5.4 subsections below define **what each tier runs and how the result is recorded**. The **trigger condition** for each tier — which diffs fire it — is the authoritative §4.5.8 path × tier matrix (locked by D21). If a triggered tier did not run, the commit is `not_eligible_for_closure` per D19 regardless of which tier.

#### §4.5.1 Smoke auto-trigger (D17a)

The §4.1 smoke set runs for every detector whose module is in the diff, plus a structural-integrity smoke on the scoring agent. Result is written as a `test_run_started` + `test_run_finished` pair to the audit-trail JSONL per §9.2.

#### §4.5.2 Regression auto-trigger (D17b)

The §4.2 regression set runs against `core/scoring/eval/fraud_eval_dataset.jsonl` plus any other published regression fixture set. Recording requirement: full per-case record set + audit-trail events + confusion-matrix snapshot persisted under `audit_outputs/testing_framework/runs/<test_run_id>/`.

#### §4.5.3 Adversarial auto-trigger (D17c)

The §4.3 adversarial suite runs for the affected detector (e.g., the TOAD pass-2 `test_callback_phishing_break_it.py` shape), plus any adversarial cases tagged for the changed evidence field. Recording requirement: per-case evidence bundles plus an adversarial-intent note for each adversarial case run.

#### §4.5.4 Eval-corpus auto-trigger (D17d)

The harness at `core/scoring/eval/fraud_eval_harness.py` runs against the full dataset, with per-subcategory recall + per-verdict precision recorded. Recording requirement: full eval report + audit-trail events; the report includes the prior-baseline comparison delta.

#### §4.5.5 Red-team scheduling rule (D18)

Red-team tests do not auto-run live and do not auto-run on any commit. They are scheduled monthly through an operator-authored mission file (see §4.4) and remain controlled / synthetic unless explicitly authorized by the operator in writing in `PROJECT_ACTIVITY_LOG.md` with named scope, reason, authorisation date, and termination condition. Live third-party probing — unauthorized phishing of any real person, probing of real vendor infrastructure, or live-malware execution — remains forbidden by §1.3 regardless of schedule.

#### §4.5.6 Enforcement — commit completeness gate (D19)

For every commit whose diff matches a §4.5.8 matrix row, the corresponding test-tier run must be recorded in the audit trail before `pre_ship_audit.py` can return `VERDICT: SHIP`. The completeness check looks for a `test_run_finished` audit-trail event whose `structured_payload.scoring_agent_version` matches the commit's `HEAD` SHA (or a fast-forward ancestor) and whose `structured_payload.tier` equals the required tier. Missing or stale recorded result → the gate fails closed with a named reason naming which tier did not run and which matrix row was matched. v1 enforcement authority is locked in §4.5.9 (D22).

#### §4.5.7 Failed-test acceptance rule (D20)

A required test that fails blocks the commit by default. Continuation requires **all four** of the following conjunctively — partial satisfaction is not partial acceptance:

- **Recorded** — failure captured in the per-case evidence bundle per §9.1 and emits a `case_evidence_missing` or `failure_card_opened` audit-trail event per §9.2.
- **Classified** — failure-analysis card per §9.4 with `failure_type` from the closed enum `{verdict_mismatch, overconfident, evidence_missing, schema_violation, scope_violation}`. Free-text "other" is forbidden; failures that do not fit the enum open a UDR event per D14 and the enum widens through a §11-revision cycle.
- **Operator-accepted** — operator signs an acceptance entry in `PROJECT_ACTIVITY_LOG.md` naming failure card ID, acceptance reason, risk owner, and hard expiry timestamp; or uses the named-reason override path on `pre_ship_audit.py` with the same fields recorded.
- **Retest-linked** — failure card's `Decision` field reads `retest_required` and a retest item is scheduled per §9.5 with a `prior_failure_card_ref` back-link.

If any condition is missing, the failure blocks unconditionally. If all four hold, the commit may proceed and the card remains open until the retest closes it; an unclosed card past the operator-named expiry is high-severity drift and surfaces in the dashboard per §8.5.

#### §4.5.8 v1 Auto-Trigger Path Matrix (Q8 resolution, locked by D21)

The matrix below is the authoritative path × tier intersection for v1. §4.5.1–§4.5.4 define **what each tier runs and how it is recorded**; §4.5.8 defines **which paths trigger which tiers**. The §4.5.6 gate consumes this matrix verbatim.

Paths are repo-relative; `Runtime_Implementation/` abbreviates `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/`. `S` = smoke, `R` = regression, `A` = adversarial, `E` = eval-corpus; `Y` = required, `O` = optional / conditional (criterion stated), `N` = not required. `Pytest` = full runtime pytest. `FC/RT` = failure card + retest record required when a triggered tier fails.

| # | Surface | Path patterns | S | R | A | E | Pytest | FC/RT on fail |
|---|---------|--------------|---|---|---|---|--------|----------------|
| 1 | Detector logic | `Runtime_Implementation/core/scoring/*_detector.py`; `core/precursor/**`; any new top-level detector module | Y | Y | Y | Y | Y | Y |
| 2 | Scoring logic | `core/scoring/email_risk_scoring_agent.py`; overlay modules under `core/scoring/`; recommended-action enum mapping | Y | Y | Y | Y | Y | Y |
| 3 | Rubric mapping | `core/scoring/client_facing_rubric.py` (axis mappers, evidence-tag mappers, dedup helpers) | Y | Y | Y | Y | Y | Y |
| 4 | Rendering / digest / reporting | `core/drafting/**`; `scripts/inbox_shield_daily_digest_demo.py`; future renderer modules under `core/` | Y | Y | O (only when evidence-field interaction or D8 OOB wording surface changes) | O (only when prompt-driven expected output changes) | Y | Y |
| 5 | Schema / model | `core/blackboard/models.py`; additive payload models consumed downstream | Y | Y | Y | Y | Y | Y |
| 6 | Production loop | `core/production/**` | Y | Y | O (only when a detector or scoring path is in the same diff) | O (only when a detector or scoring path is in the same diff) | Y | Y |
| 7 | Agent orchestration | scoring-agent, daily-digest-agent, decision-auditor runner modules; `audit_tools/decision_audit_runner.py` integration shapes | Y | Y | Y | Y | Y | Y |
| 8 | Evidence packaging | evidence-bundle builders; audit-trail writers; reporting modules; `audit_outputs/testing_framework/**` schema writers | Y | Y | O (only when evidence field set changes) | O (only when evidence field set changes) | Y | Y |
| 9 | Test fixtures | `Runtime_Implementation/tests/fixtures/**` (synthetic `.eml` / JSON / lab-baseline fixtures); `core/scoring/eval/fraud_eval_dataset.jsonl` | N | Y (when fixture is consumed by a regression test) | O (when fixture targets an adversarial case) | Y (when fixture is in the eval dataset) | Y (when any test consumes the fixture) | Y |
| 10 | Prompt / spec-output | locked LLM prompts (`NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`, `DAILY_DIGEST_SYSTEM_PROMPT`); fixture `expected.*` bound edits; locked-prompt hash changes | Y | Y | Y | Y | Y | Y |
| 11a | Signed-spec change — spec-only edit (no runtime code in same commit) | `4. Product_Roadmap/*_Deep_Dive.md` post-§11 amendments without any runtime-code change in the diff | N | N | N | N | N | N |
| 11b | Signed-spec change — paired with runtime code in same commit | Same `*_Deep_Dive.md` paths above **plus** at least one path in rows 1–10 | Match the row(s) fired by the runtime path; spec-amendment text alone does not lift tier requirements | — | — | — | — | — |
| 12 | Docs-only | `*.md` outside `Runtime_Implementation/`; `MASTER_INDEX.md`; `PROJECT_HANDSHAKE.md`; `PROJECT_ACTIVITY_LOG.md`; `PROGRESS.md`; `think_sheet.md`; `*.csv` / `*.txt` analyst notes; `4. Product_Roadmap/*` pre-§11 drafts | N | N | N | N | N | N |

Matrix application rules:

- **Union** — a diff hitting multiple rows requires the union of their tier requirements; maximal tier set wins.
- **`O` entries** require an explicit decision recorded in the failure card or commit-message footer when the optional tier was skipped. Default is "skip unless criterion met", not "run always".
- **Row 11a** is the only path that lets a spec edit ship without a test-tier run. A signed-spec amendment that genuinely alters runtime behavior must be followed by a row-1-through-10 commit; that follow-up re-fires the matrix per its own diff.
- **Row 12** is the explicit "no false-positive trigger" lane. Pre-§11 drafts in `4. Product_Roadmap/` are intentionally row 12 — draft artifacts, not contracts. Once signed, the same file becomes row 11a/11b on the next edit.
- **Capability registry changes** (`audit_outputs/testing_framework/capability_registry.{yaml|json}` once it lands) are row 8 until v1 defines a dedicated row; D11 promotions / demotions separately require operator-recorded activity-log entries regardless of matrix triggering.
- **The matrix may be cached** at `audit_outputs/testing_framework/auto_trigger_path_matrix.{yaml|json}` for fast lookup; spec text in §4.5.8 is the source of truth and the cache must be regenerated from it, never authored independently.

#### §4.5.9 v1 Enforcement Authority (Q9 resolution, locked by D22)

v1 enforcement of the §4.5.6 commit-completeness gate is assigned to `audit_tools/pre_ship_audit.py`. Rationale: `pre_ship_audit.py` is already the always-on pre-commit / pre-ship gate authorised by Matt (PROJECT_HANDSHAKE.md 2026-05-24 entry) for material commits, so reusing it avoids new infrastructure and matches the cheapest-cheaper-proof-first discipline. Five locked rules:

- **`pre_ship_audit.py` is the v1 enforcement point.** It consumes the §4.5.8 matrix at run time, inspects the staged diff, computes the required tier set, reads the audit trail per §9.2, and returns `VERDICT: SHIP | FIX_FIRST | STOP` per its existing contract.
- **`complete_gate.py` audits the work packet but does not replace the cadence gate.** `complete_gate.py` answers "does this work packet match its signed contracts and the project's non-negotiables?"; `pre_ship_audit.py` answers "did the required test tier run and record its result before this commit is allowed?" Two independent enforcement layers — a commit must pass both, neither subsumes the other.
- **CI is future v1.1 / v2 layering, not v1.** Intended future shape: `CI → pre_ship_audit.py → release tagging`. v1 ships `pre_ship_audit.py` alone so the rule is enforceable on the operator's local machine first. A CI job under `.github/workflows/` may later mirror the gate for branch protection.
- **Missing required test evidence → `pre_ship_audit.py` fails closed.** Returns `VERDICT: STOP` (or `FIX_FIRST` when the missing tier could be re-run cheaply) with a named reason naming which tier did not run, which D21 matrix row fired, and which audit-trail event would have satisfied the gate. Ambiguous diffs default to the broader tier set, not the narrower one — false-positive triggers are recoverable, false-negative misses are not.
- **Operator override requires all four D20 conjunctive conditions.** A `VERDICT: STOP` cadence-gate failure may be overridden only by an operator-recorded entry satisfying D20: recorded reason + failure classification from the closed `{verdict_mismatch, overconfident, evidence_missing, schema_violation, scope_violation}` enum + retest link + signed acceptance entry in `PROJECT_ACTIVITY_LOG.md` naming risk owner and hard expiry. The override entry must cite both the failed cadence tier and the underlying test failure (if any); a cadence override without a backing failure is `not_eligible_for_override` because there is no failure to classify or retest.

The v1 implementation pass that builds the gate extension into `pre_ship_audit.py` is a separate work item, gated on §11 signature plus a separate operator start-build instruction. §4.5.9 is the policy contract that v1 implementation must honour exactly.

---

## §5 Safe Test-Data Sources (v1)

v1 test-data sources are exactly these and only these:

- **`.example` domains** (RFC 2606 / RFC 6761) for every sender, recipient, and URL host in fixtures.
- **Fake vendor names** — Bluefin Marine Supplies, Acme Industries Demo, Coastal Marine, the `*-demo` tenant convention. Operator may add new fake vendors; real customer names are forbidden.
- **Fake URLs** — all URL fixtures use `.example` hosts. No real domains, no shortened links, no tracking pixels.
- **Inert attachments** — fixtures may carry filename, content-type, size, and `pdf_metadata` Producer/Creator strings already consumed by `document_metadata_detector`. No real payloads, no executable content, never byte-parsed in v1.
- **Synthetic `.eml` fixtures** under `Runtime_Implementation/tests/fixtures/`, git-tracked, hand-curated.
- **Lab mailbox only** — derived artifacts from real mailbox observations (e.g., the 2026-05-30 Microsoft 365 lab mailbox authentication baseline) store only sanitised structured fields. Raw header bulk is never committed.

Disallowed in v1: live malware, live phishing pages, real credential-harvest infrastructure, third-party probing, any browser automation that loads real-world hostile content.

---

## §6 Capability Registry & Category Status Model

### §6.1 Status enum (D1)

Every category, for every test case, carries exactly one of these four status values:

- **`supported`** — runtime actively observes the category for this case, evidence bundle entry present.
- **`not_supported_yet`** — runtime does not observe this category in v1; known capability gap, not a failure.
- **`not_present_in_sample`** — runtime observes the category but the fixture does not contain the signal (e.g., a benign email with no attachment cannot be scored on attachment metadata).
- **`evidence_missing`** — runtime observes the category and the fixture contains the signal, but the evidence bundle is empty or unreferenced. Hard failure; excludes the case from accuracy.

### §6.2 Initial capability registry (illustrative, v1 starting state)

The full registry lives in v1 implementation as a structured YAML or JSON file under `audit_outputs/testing_framework/capability_registry.{yaml|json}`, read at run start. Below is illustrative; the on-disk file is the authoritative source, kept in sync with signed runtime specs.

**Status: `supported` (representative entries; not exhaustive):** SPF / DKIM / DMARC ingestion (`email_authentication_detector`); ARC chain observation (read-only); header divergence (`header_divergence_detector`); received-chain metadata extraction (`received_chain_parser`, foundation-only, no scoring); email-body plain-text scanning (TOAD, prompt-injection, unicode-obfuscation, behavioral-flag emission); behavioral deviation flags (10-value `BehavioralDeviationFlag` Literal); document metadata fingerprinting (PDF Producer/Creator strings only; `document_metadata_detector`); vendor baseline check (hash-only per-tenant SQLite, TTL-bounded); financial state ledger / delta tripwire; ransomware-precursor indicator analysis (attachment metadata + URL token surface); Callback Phishing / TOAD body-language detection (`body_plain` only); risk score (0-100); recommended action enum; client-facing 5-axis rubric projection (when activated); effective parameter resolution (tenant override + signed policy state).

**Status: `not_supported_yet` (representative entries; not exhaustive):** attachment payload sandbox execution; URL redirect resolution / fetching / reputation lookup; domain age / WHOIS lookup; geo / device / login-context inspection; sender-provenance / geo-velocity scoring (parser foundation exists; scoring layer not built); TOAD phone-number assessment (gated on Vendor Baseline Store enum revision); TOAD `body_html` parsing (deferred to v1.1+); PDF byte parsing / OCR / image-content analysis; voice-call / SIP / speech-to-text inspection (Cross-Channel Fraud Shield SPARK only); live email rewriting / blocking / quarantine; multi-factor authentication context; CRM / billing system cross-reference.

### §6.3 Registry update rule (D11)

Adding a `not_supported_yet` entry is operator-discretion (no spec needed). Promoting `not_supported_yet` → `supported` requires citing the §11-signed runtime spec that landed the capability (e.g., signed TOAD spec for `callback_phishing_pattern`). Demoting `supported` → `not_supported_yet` is high-severity drift: requires an operator-recorded incident entry in `PROJECT_ACTIVITY_LOG.md`, a failure-analysis card explaining the regression, and explicit operator authorisation in the same entry. Removing a registry entry entirely is forbidden once it has appeared in any closed test run.

---

## §7 Test-Case Schema & Verdict Comparison

### §7.1 Verdict enum (D2)

Per-case verdicts use exactly these five values: **`legitimate`** (benign, pass through without lift); **`needs_review`** (ambiguous, surface for human review without auto-blocking); **`high_risk`** (suspicious enough that the operator-facing surface should escalate prominently); **`blocked_or_hold_recommended`** (recommendation only — v1 is advisory); **`unknown`** (insufficient evidence to issue any of the above — a real value, recorded distinctly so it does not pollute the other four buckets).

### §7.2 Per-case record shape

Every test case carries the following structured fields:

```text
case_id                  string, kebab-case, unique within the dataset
fixture_path             repo-relative path to the .eml or JSON fixture
description              one-line human description
expected_verdict         one of the five verdict values
expected_categories[]    list of (category_name, status, expected_signal) tuples
actual_verdict           one of the five verdict values (populated at run time)
actual_categories[]      list of (category_name, status, observed_signal) tuples
verdict_match            one of {exact, adjacent, mismatch, unscored}
confidence_bucket        one of {low, medium, high, overconfident}
evidence_present         bool, true iff every supported category has a non-empty evidence entry
evidence_bundle_ref      string, repo-relative path to the per-case evidence bundle
reviewer_notes[]         list of structured reviewer notes (may be empty)
udr_events[]             list of (failure_mode_name, observed_at_utc) tuples
test_run_id              FK into the run-level audit record
recorded_at_utc          ISO-8601 UTC timestamp
```

v1 authority rule (D23 / Q2): the list above is implemented as strict Pydantic models. Generated JSON Schema is a derived artifact for consumers, not the source of truth; fixture and run-output JSON must validate by round-tripping through the models.

### §7.3 verdict_match semantics

- **`exact`** — `actual_verdict == expected_verdict`. Positive in verdict-precision/recall denominator.
- **`adjacent`** — actual and expected are one step apart on the severity ladder (`legitimate` ↔ `needs_review`, `needs_review` ↔ `high_risk`, `high_risk` ↔ `blocked_or_hold_recommended`). Counted separately so adjacency drift is visible; not collapsed into either pass or fail.
- **`mismatch`** — actual and expected are two or more steps apart or actual is `unknown` while expected is not. Always counted against accuracy.
- **`unscored`** — case is `evidence_missing` or `not_supported_yet`-dominant. Excluded from accuracy; reported under capability coverage.

### §7.4 Evidence-required validation (D4)

At write time, for every `supported`-status category in `actual_categories[]`, a non-empty entry must exist in `evidence_bundle_ref`. Missing entries auto-mark the case `evidence_missing` and exclude it from accuracy denominators; the harness emits a `case_evidence_missing` audit record so the gap is visible.

---

## §8 Metrics

All v1 metrics are deterministic functions of the per-case record set defined in §7.

### §8.1 Accuracy / precision / recall / FPR / FNR (D3)

- **Accuracy** = `exact_verdict_count / (exact_count + adjacent_count + mismatch_count)`. `unscored` excluded.
- **Precision (per verdict bucket)** = `tp / (tp + fp)`, with positives defined per the verdict's severity meaning (e.g., for `high_risk`, a false positive is a `legitimate` case scored `high_risk`).
- **Recall (per verdict bucket)** = `tp / (tp + fn)`.
- **FPR** = `legitimate_cases_scored_above_needs_review / legitimate_case_count`.
- **FNR** = `suspicious_cases_scored_legitimate_or_unknown / suspicious_case_count`.

All denominators include only categories whose status is `supported`. `not_supported_yet`, `not_present_in_sample`, and `evidence_missing` cases are excluded by construction.

### §8.2 Confidence calibration (D12)

Each case is bucketed at run time: **`low`** (`risk_score` in `[0,25]`, "NorthStar declined a strong position"); **`medium`** (`[26,60]`, "moderate position"); **`high`** (`[61,100]` and `verdict_match` ∈ {`exact`, `adjacent`}, "confident and correct or near-correct"); **`overconfident`** (`[61,100]` and `verdict_match == mismatch`, *priority signal* — a confident wrong answer is worse than a hedged wrong answer and surfaces separately in the dashboard). v1 does not ship continuous reliability diagrams; thresholds may be revised post-§11.

### §8.3 Unknown Discovery Rate (D14)

`udr = total_udr_events_across_cases / total_cases_in_run`. A `udr_event` is emitted when a case surfaces a failure mode not currently in the capability registry (§6.2). Reported alongside accuracy in every dashboard surface; sustained `udr > 0` across runs is a registry-incompleteness signal.

### §8.4 Capability-coverage metric (companion to D3)

`capability_coverage = supported_category_count / total_known_category_count`. Reported alongside accuracy so the operator can see at a glance: "NorthStar scored 96% on the supported surface (which covers 64% of the known category space)."

### §8.5 Dashboard metric set (v1)

Per test run, the v1 dashboard renders: `accuracy_supported_only` (with sample size); `precision_per_verdict` and `recall_per_verdict` (tables of five values); `false_positive_rate`, `false_negative_rate`; `confidence_bucket_distribution`; `overconfident_case_list` (links); `evidence_missing_case_count`; `udr` (with the list of new failure modes observed); `capability_coverage` (with the list of `not_supported_yet` categories); `verdict_match_distribution` (exact / adjacent / mismatch / unscored counts); `regression_delta_vs_baseline` (per-subcategory recall change vs recorded baseline). Metric-shape only in this spec; rendering surface (Markdown report, JSON file, Cursor canvas, eventual portal) is a separate operator decision and explicitly out of scope.

---

## §9 Evidence, Audit Trail, Failure-Analysis & Retest Loop

### §9.1 Evidence bundle schema (D4)

Per-case bundle, on-disk under `audit_outputs/testing_framework/runs/<test_run_id>/cases/<case_id>/`:

```text
evidence_bundle.json
  schema_version            string, semver
  case_id                   FK back to the case record
  generated_at_utc          ISO-8601 UTC
  fixture_sha256            sha256 of the input fixture
  scoring_agent_version     string (commit hash + locked-prompt hash)
  per_category[]:
    - category_name         string (must appear in the capability registry)
    - status                one of the four status values
    - signals_observed[]    list of structured signal records
    - signals_missing[]     list of expected-but-absent signal names
    - rule_fired            string identifier of the deterministic rule that produced the signal (or `null` for LLM-only)
    - evidence_tags[]       list of evidence-tag strings (subset of the rubric evidence-tag vocabulary)
    - decision_path_summary string, capped at 280 chars (no chain-of-thought)
  bundle_sha256             sha256 of the rest of the bundle, computed last for integrity
```

### §9.2 Audit trail event shape

Append-only JSONL stream at `audit_outputs/testing_framework/audit_trail.jsonl`:

```text
{
  "event_type": one of {test_run_started, test_run_finished, case_scored,
                        case_evidence_missing, udr_event, failure_card_opened,
                        failure_card_closed, retest_started, retest_finished,
                        registry_status_change, dashboard_published},
  "event_id": uuid v4,
  "occurred_at_utc": ISO-8601,
  "test_run_id": string,
  "case_id": optional string,
  "actor": operator identifier or "automated",
  "structured_payload": { ... event-specific structured fields ... }
}
```

No raw email content, no raw LLM output, no chain-of-thought, no PII in `structured_payload`. Lint inherits the existing project audit-record discipline.

### §9.3 Decision transparency format (D5)

Every score exposes: `rule_fired` (deterministic rule identifier or `null` for LLM-only paths); `evidence_tags[]` (vocabulary-bounded strings shared with the rubric and dashboard); `signals_observed[]` (typed records: signal name, value-or-hash, source-field); `signals_missing[]` (expected-but-absent signal names that informed the score, e.g., `dkim_pass:absent`); `decision_path_summary` (≤280 chars, never reproducing raw LLM `reasoning` / `thinking` content). LLM reasoning / thinking strings are dropped at the framework boundary and never persisted — enforced by schema, not convention.

### §9.4 Failure-analysis card (D9)

Every failing case (where `verdict_match` is `mismatch`, or `confidence_bucket` is `overconfident`, or `evidence_present` is `false`) generates a failure-analysis card on disk at `audit_outputs/testing_framework/runs/<test_run_id>/cases/<case_id>/failure_card.md`:

```text
# Failure card — <case_id>

- Test run: <test_run_id>
- Case ID: <case_id>
- Failure type: one of {verdict_mismatch, overconfident, evidence_missing}
- Expected verdict / actual verdict / verdict_match
- Hypothesised root cause (operator or analyst free text, capped at 1200 chars)
- Affected capability registry entries
- Proposed fix scope (which detector, which rubric mapper, which fixture)
- Decision: {file_only, retest_required, spec_change_required, registry_demote_required}
- decision_audit_candidate_id: nullable string; non-null and MUST be populated when failure_type ∈ {schema_violation, scope_violation} (D29)
- Linked PR or commit (populated when the fix lands)
- Retest record reference (populated when the retest closes the loop)
- Signed off by / signed off at UTC (operator-only fields; blank in draft)
```

A failing case without a populated failure card cannot be retested through the official loop. A retest attempted without an attached card is marked `not_eligible_for_closure`. Cards with `failure_type` ∈ `{schema_violation, scope_violation}` are Decision Audit candidates per D29; the v1 obligation is to populate `decision_audit_candidate_id` and mirror it on the `failure_card_opened` audit-trail event so downstream v1.1 integration can locate the candidate set without re-scanning every card.

### §9.5 Retest-and-improvement loop

Deterministic six-step loop: (1) failure surfaced → test run produces a failure card; (2) root cause hypothesised → operator (or analyst with operator sign-off) writes the hypothesis section; (3) fix proposed → scope recorded; if a §11-signed spec change is required, the loop pauses until that revision lands; (4) fix lands → commits link the failure card by ID in the commit-message footer; (5) retest run → same fixture set including the failing case; retest's `case_id` carries `prior_failure_card_ref` linking back; (6) loop closure → operator signs off if retest passes; if it fails again, a follow-up card is opened linking the prior card. Audit trail records `failure_card_opened`, `retest_started`, `retest_finished`, `failure_card_closed` events so the loop is reconstructible from the audit-trail alone.

### §9.6 Reviewer notes (D13)

Additive, optional, structured per-case field: `reviewer_initials` (2-4 chars), `recorded_at_utc` (ISO-8601), `scope` ∈ `{evidence, verdict_comparison, failure_card, dashboard_metric}`, `comment` (≤600 chars, no chain-of-thought, no PII). Reviewer notes never override the verdict. They surface alongside the verdict in dashboard and per-case page, not in place of it.

---

## §10 Open Questions

All numbered sub-questions are now resolved pre-§11. The stress-test verdicts that produced Q1 / Q3 / Q4 are recorded in `think_sheet.md` (entry "Sub-question stress test — Email Security Testing & Evidence Framework §10 (2026-05-31)"). Q5 / Q6 / Q7 carry lighter verdicts recorded in the same think_sheet entry. None of these resolutions sign the spec — §11 signature remains operator-only.

- **Q1. RESOLVED 2026-05-31 — see D24 and §8.2.** Lock the draft `[0,25] / [26,60] / [61,100]` boundaries with `overconfident` carved from `high` by `verdict_match ≠ exact`. Recalibration requires ≥60 real fixture cases distributed across all four buckets, a §11-revision cycle, and an operator log entry naming the empirical distribution evidence.
- **Q2. RESOLVED 2026-05-31 — see D23 and §7.2.** Pydantic models are the authoritative v1 per-case and evidence-bundle shape. Generated JSON Schema is allowed only as a derived artifact for docs / consumers / downstream validation; on-disk JSON / JSONL must round-trip through the models.
- **Q3. RESOLVED 2026-05-31 — see D25 and §8.1.** Strict exclusion. `adjacent` verdict mismatches contribute zero credit to `accuracy_supported_only` (and the derived precision / recall / FPR / FNR). `verdict_match_distribution` (§8.5) preserves the four-value breakdown so adjacency stays visible without averaging into accuracy.
- **Q4. RESOLVED 2026-05-31 — see D26 and §4.2.** Default regression-tolerance is `0` percentage points strict. Per-subcategory widening above 0 requires an operator entry in `PROJECT_ACTIVITY_LOG.md` naming subcategory, tolerance value (pp), rationale, and hard expiry.
- **Q5. RESOLVED 2026-05-31 — see D27 and §4.4.** Defer red-team mission file structure to the first real mission, but lock eight minimum required fields: `mission_id`, `scope`, `hypothesis`, `threat_model`, `controlled_synthetic_only_acknowledgement`, `success_criteria`, `scheduled_for`, `operator_authorization`. Field names intentionally avoid `attestation` per the D10 forbidden-language inheritance.
- **Q6. RESOLVED 2026-05-31 — see D28 and §8.5.** No composite quality score in v1. The §8.5 metric list is the dashboard. A composite is deferred to v1.1+ gated on operator-stated evidence that the §8.5 list is too noisy for monthly buyer reporting.
- **Q7. RESOLVED 2026-05-31 — see D29 and §9.4.** Lock the Decision Auditor trigger condition only: failure cards with `failure_type` ∈ {`schema_violation`, `scope_violation`} are Decision Audit candidates and MUST carry a non-null `decision_audit_candidate_id` linkage field. Runner integration, packet shape, and dashboard surface are v1.1 work requiring their own §11-signed spec.
- **Q8. RESOLVED 2026-05-30 — see §4.5.8, locked by D21.** The authoritative path-pattern matcher is the twelve-row matrix in §4.5.8. The matrix may be cached at `audit_outputs/testing_framework/auto_trigger_path_matrix.{yaml|json}` for fast lookup, but the spec text in §4.5.8 is the source of truth and the cache must be regenerated from it, not authored independently.
- **Q9. RESOLVED 2026-05-30 — see §4.5.9, locked by D22.** v1 enforcement authority for D19 is `audit_tools/pre_ship_audit.py`. `complete_gate.py` audits the work packet but does not replace the cadence gate. CI is future v1.1 / v2 layering. Missing required test evidence fails the gate closed with a named reason; operator override requires all four D20 conjunctive conditions.

---

## §11 Sign-Off Placeholder

**Status:** UNSIGNED. This draft is pre-§11. The decisions in §2 are advisory until Matt signs.

**Locked decisions covered by this signature, once given:** D1–D29 as drafted in §2, plus the §4.5 auto-trigger cadence contract referenced by D16–D20, the §4.5.8 v1 trigger matrix locked by D21 (Q8 resolution), the §4.5.9 v1 enforcement authority locked by D22 (Q9 resolution), the Pydantic-model authority rule locked by D23 (Q2 resolution), the v1 `confidence_bucket` boundaries locked by D24 (Q1 resolution), the strict-exclusion accuracy rule locked by D25 (Q3 resolution), the `0` pp regression-tolerance default locked by D26 (Q4 resolution), the red-team mission minimum-fields floor locked by D27 (Q5 resolution), the no-composite dashboard rule locked by D28 (Q6 resolution), and the Decision Auditor trigger-only v1 scope locked by D29 (Q7 resolution). The full text of each D-decision is authoritative in §2; this section is the signature placeholder, not a re-statement.

**Signed by:** ____________________________________

**Date:** ____________________________________

**Signature is incomplete.** Implementation of the v1 surface (D7) does **not** begin until §11 is signed and a separate explicit operator start-build instruction is issued.
