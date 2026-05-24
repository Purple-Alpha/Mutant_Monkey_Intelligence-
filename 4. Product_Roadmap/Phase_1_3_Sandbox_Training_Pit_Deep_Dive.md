# Phase 1.3 — Sandbox Training Pit Deep Dive

**Phase reference:** `Fraud_Ransomware_Specialization_Roadmap.md` §1.3 (Expand the Sandbox Training Pit).
**Roadmap month:** `12_Month_Specialization_Roadmap.md` Month 4 (September 2026 in calendar terms).
**Status:** **§11 LOCKED by Matt 2026-05-21. Implementation LANDED.** All five decisions approved; runtime code, schema delta, and ≥10-test gate suite are live. See §9 implementation receipt.
**Predecessors that must already be in place:** Month 0 sandbox loop (`core/sandbox/loop.py`), Month 0 weakness-report + synthetic-attack-case + mutant-evaluation record types, Guardrail 11 Blue-loop write surface, multi-tenant isolation Phase 2–8, operator kill switch, Phase 1.1 fraud-scoring agent (`grok-4` PASS gate), Phase 1.2 ransomware-precursor overlay (`core/precursor/`).

## §0 Purpose

Phase 1.1 + Phase 1.2 produced a scoring surface. Phase 1.3 stress-tests it. The sandbox loop already has the Red → Blue → Mutation Evaluation → Audit chain wired with the correct record types and Guardrail 11 boundaries; what is missing is the **fraud-specialized adversarial generation** that exercises the actual production scoring path with synthetic Inbox Shield emails.

Three constraints define Month 4's design:

1. **The Month 2 gate must not regress.** The Phase 1.1 prompt and the 40-case fraud-eval dataset are frozen. The sandbox runs in a separate environment + tenant pair and produces its own Blackboard records; it never writes into production.
2. **Sandbox tenants are evaluation-only.** No real customer email ever enters the sandbox. Every synthetic email is generated from constant seed data plus randomised parameters per the boundaries in §2.
3. **Promotion stays through the existing signed pipeline.** Phase 1.3 produces weakness reports; nothing from this phase mutates production policy. Month 5 (Phase 1.4) is the mutation-engine specialisation that consumes Phase 1.3 weakness reports through the existing `apply_signed_policy` gate.

## §1 Fraud-Specialised Red Agent Roles

Four new Red profiles register in `core/orchestrator/registry.py` with `role=AgentRole.RED` (or equivalent) and tightly scoped `allowed_write_types = {RecordType.SYNTHETIC_ATTACK_CASE}` (or the new `SYNTHETIC_EMAIL_ATTACK_CASE` type proposed in §3.2 if Matt approves that path). They never have write access to `EMAIL_INBOUND`, `EMAIL_ANALYSIS`, or any production-shaped record.

| Red agent id | Profile name | Attack class | Generation focus |
|---|---|---|---|
| `fake_invoice_red_001` | Fake invoice generator | Vendor-invoice fraud | Synthetic vendor invoices with lookalike sender domains, new-banking-instructions language, urgent payment requests, and matching-vendor-name traps |
| `vendor_update_red_001` | Vendor banking-update generator | Vendor banking-change fraud | "We've updated our remit-to address" emails, PDF-only banking changes, thread-hijack patterns from Phase 1.1 Example 5, future-dated invoices from Example 6 |
| `malicious_attachment_red_001` | Malicious attachment generator | Ransomware-attachment precursor | Emails with `.iso` / `.exe` / `.docm` / `.pdf.exe` / encrypted-archive attachments; covers every Phase 1.2 attachment indicator at least once per battery |
| `obfuscated_url_red_001` | Obfuscated URL generator | URL-obfuscation / credential-harvest precursor | Emails with punycode hosts, Cyrillic homoglyphs, URL shorteners, credential-bearing URLs, suspicious TLDs, IP-host URLs, login-path URLs; combined with credential-reset / MFA-push body language to exercise the Phase 1.2 cross-detector path |

### §1.1 Why exactly four

The four profiles are one-to-one with the four signal axes Phase 1.1 + Phase 1.2 produce:

- `fake_invoice_red_001` → exercises Phase 1.1 `vendor_fraud_score` + `behavioral_deviation_flags`.
- `vendor_update_red_001` → exercises Phase 1.1 `invoice_authenticity_score` + `behavioral_deviation_flags` including the recall-patch surfaces (`new_banking_instructions`, `mismatched_invoice_vendor_name`).
- `malicious_attachment_red_001` → exercises Phase 1.2 `attachment_risk_score` + matching `PrecursorIndicator` values.
- `obfuscated_url_red_001` → exercises Phase 1.2 `url_obfuscation_score` + `credential_harvesting_score` + `mfa_fatigue_score`.

Each Red profile must, by spec, produce at least one synthetic case per locked enum value it can drive. This keeps coverage tied to the schema, so adding a new `BehavioralDeviationFlag` or `PrecursorIndicator` forces a Red-side coverage extension before the Month 4 gate test can pass.

### §1.2 What Red is NOT

- Red profiles do **not** call an LLM. They are purely deterministic synthetic generators. (Cost, reproducibility, governance — same logic as the Phase 1.2 deterministic detectors.)
- Red profiles do **not** observe the real Inbox Shield prompt, dataset, or any tenant data. The seed data is fixed strings + parametric variations defined inside each Red module.
- Red profiles do **not** evolve, self-improve, or rewrite themselves. Mutation is exclusively a Blue-side concept for Month 5; Red stays static within a battery, change-controlled like any other module.

## §2 Synthetic Scenario Generation Boundaries

Every Red profile generates **≥ 100 unique adversarial cases per profile per battery run** (per roadmap Month 4 spec) under these hard boundaries:

1. **Constant seed data only.** Sender domains, vendor names, dollar amounts, recipient inboxes, attachment filenames, URL hosts, body templates are drawn from per-profile constant tables compiled into the Red module. **No filesystem reads of tenant data, no network calls, no LLM generation.**
2. **Parametric variation, not free-form sampling.** Variation is bounded by enumerated dimensions: which sender domain (from the profile's 10–20-entry table), which vendor name (from the profile's table), which dollar-amount band, which urgency phrase, which behavioural-flag combination. The cross-product of the dimensions gives ≥ 100 cases per profile without random text generation.
3. **Determinism is a hard requirement.** Each synthetic case carries a `seed: int` and a `case_index: int`. Same seed + same case index → byte-identical synthetic payload. CI must be able to reproduce a specific failing case from its id.
4. **No real customer data, ever.** A `raw_tenant_data_removed: bool = True` validator (already present on `SyntheticAttackCasePayload` and `WeaknessReportPayload`) is the schema-level guarantee. Phase 1.3's Red modules carry zero strings that resemble a tenant identifier.
5. **Synthetic identifiers stay in the `.example` / `.test` namespace.** All sender / recipient / vendor domains end in `.example`, `.test`, or `.invalid` (RFC 2606 / 6761 reserved). Anything else fails validation. This protects against ever accidentally sending one of these emails out.
6. **Bounded toxicity.** Synthetic bodies must contain no real malware text, no real exploit strings, no shell commands. Attachments are metadata only (filename, content type, optional sha256) — Phase 1.3 never produces actual binary attachment content. Same sandbox-safe boundary as Phase 1.2 detectors.
7. **No outbound side effects.** No file writes outside `Environment.SANDBOX` paths, no network, no subprocess, no system calls. The Red modules are pure functions of (config, seed, case_index) → synthetic payload.

## §3 Safe / Evaluation-Only Sandbox Rules

### §3.1 Environment isolation

The existing multi-tenant isolation enforcement applies:

- All Phase 1.3 activity happens under `Environment.SANDBOX` with `sandbox_tenant_id` per the existing `SandboxLoopConfig` field. Default for development continues to be `sandbox_default`; per-tenant sandboxes use `default_sandbox_tenant_for(production_tenant_id)` from `core/orchestrator/tenants.py`.
- No Phase 1.3 code may write into `Environment.PRODUCTION` for any tenant, under any condition. The Guardrail 11 surface list is intentionally unchanged.
- The operator kill switch already gates `run_sandbox_cycle` (`KillSwitchEngaged` raised on entry). Phase 1.3 inherits this; the Month 4 entry point must remain a `run_*_cycle`-style function so the kill-switch check fires at the same boundary.

### §3.2 Schema decision (recommended path)

The existing `SyntheticAttackCasePayload` is intentionally generic (`attack_kind`, `synthetic_subject`, `synthetic_sender_domain`, `expected_detection_signals`). Inbox Shield Red cases need a richer shape: body, attachments, expected behavioural-flag subset, expected precursor-indicator subset, expected risk-score band.

**Recommendation:** add a new locked payload type `SyntheticEmailAttackCasePayload` and a new `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE`. Keeping the original `SyntheticAttackCasePayload` untouched preserves the Month 0 sandbox-loop tests and gives Phase 1.3 a strict schema dedicated to Inbox Shield Red emails.

Proposed shape (subject to Matt's lockdown):

```text
class SyntheticEmailAttackCasePayload(StrictModel):
    attack_kind: Literal[
        "fake_invoice",
        "vendor_banking_update",
        "malicious_attachment",
        "obfuscated_url",
    ]
    red_agent_id: str = Field(min_length=1)
    seed: int
    case_index: int = Field(ge=0)
    synthetic_email: EmailInboundPayload    # reuses the locked Inbox Shield ingest payload
    expected_behavioral_deviation_flags_subset: tuple[
        BehavioralDeviationFlag, ...
    ] = ()
    expected_precursor_indicators_subset: tuple[PrecursorIndicator, ...] = ()
    expected_min_risk_score: int = Field(ge=0, le=100)
    expected_max_risk_score: int | None = Field(default=None, ge=0, le=100)
    expected_recommended_action_in: tuple[RecommendedEmailAction, ...] = (
        "needs_review",
        "block",
    )
    raw_tenant_data_removed: bool = True
```

Required-subset semantics match the Phase 1.1 eval-contract calibration landed under item 152 / 153: every listed flag / indicator must be emitted by the Blue agent, but extras are allowed unless an optional `forbidden_*` tuple is added later. `expected_min_risk_score` is the Month 4 analogue of the Phase 1.1 dataset score floors.

If Matt prefers the lower-risk path of extending the existing payload instead, the spec falls back to: add `synthetic_email: EmailInboundPayload | None = None` and the four `expected_*` fields to `SyntheticAttackCasePayload`, with a validator that requires `synthetic_email` to be present when `attack_kind` is one of the four new values. **Recommendation stands at: add a new payload type.**

### §3.3 No side-channel into production

Three protective rules:

- The Phase 1.3 generator runs only inside `run_sandbox_cycle` (or a new `run_red_battery_cycle` that lives inside `core/sandbox/`). No production loop calls Red generators.
- Red agents never read from production blackboards. Their inputs are config + seed + case_index, period.
- The synthetic emails are never re-routed through the production email-ingest agent. They are written directly to `Environment.SANDBOX` via the existing `submit_synthetic_email_attack_case` route (to be added; see §4.2).

## §4 Expected Blackboard Records

Each Red-vs-Blue battery cycle for one Red profile produces this record chain per case:

```text
SYNTHETIC_EMAIL_ATTACK_CASE  (Red writes; carries the synthetic EmailInboundPayload)
        │
        ▼
EMAIL_ANALYSIS               (Blue writes; produced by the actual Phase 1.1 + 1.2 scoring agent)
        │
        ▼
MUTANT_EVALUATION            (Sandbox mutator evaluates Blue's output vs expectations)
        │
        ▼
AUDIT_VERDICT                (audit_001 verdict on the cycle; requires_human_review when Blue under-detected)
```

The per-case chain feeds into a per-profile aggregate:

```text
WEAKNESS_REPORT              (one per Red profile per battery run; categorised failure modes only;
                              raw_tenant_data_removed = True is structurally guaranteed because the
                              inputs are synthetic to begin with)
```

### §4.1 SYNTHETIC_EMAIL_ATTACK_CASE writes

- Source agent: the Red profile (`fake_invoice_red_001` / `vendor_update_red_001` / `malicious_attachment_red_001` / `obfuscated_url_red_001`).
- Parent record: the `WeaknessReportPayload` that seeded this battery cycle (when the cycle is triggered from a prior weakness), or `None` (when the cycle is a clean baseline run from a fresh seed).
- Tenant: the sandbox tenant id.
- Schema: `SyntheticEmailAttackCasePayload` (§3.2).

### §4.2 EMAIL_ANALYSIS writes (the contract change)

Phase 1.3's Blue side is the **actual production scoring agent** (`run_email_risk_scoring_cycle` from `core/scoring/email_risk_scoring_agent.py`), invoked under `Environment.SANDBOX`. The existing Month 0 `_blue_detect` stub in `core/sandbox/loop.py` is **intentionally retired** for Inbox Shield Red cases — only the real agent stays representative of production.

- Source agent: `email_risk_scoring_001`.
- Parent record: the `SYNTHETIC_EMAIL_ATTACK_CASE` record id.
- Schema: existing `EmailAnalysisPayload` (now includes the optional Phase 1.2 `ransomware_precursor_analysis` block).
- The synthetic email is first written to the sandbox as an `EMAIL_INBOUND` record by a thin adapter (`materialise_synthetic_email`) so the scoring agent's existing read path is unchanged; **or** the scoring agent gains an "evaluate one in-memory `EmailInboundPayload`" entry point (e.g. `score_one_email_payload(...)`) that does not require a Blackboard hop. The spec recommends the latter to keep the sandbox blackboard from filling up with synthetic `EMAIL_INBOUND` records; final call belongs to Matt at lockdown time.

The kill switch is checked on every cycle entry (already inherited from `run_sandbox_cycle`).

### §4.3 MUTANT_EVALUATION writes

The sandbox mutator evaluates the Blue analysis against the per-case expectations and writes one `MutantEvaluationPayload` per case. The existing fields apply, with sharper semantics:

- `baseline_agent_id` = `"email_risk_scoring_001"`.
- `candidate_agent_id` = `None` (Phase 1.3 has no candidate agent; Month 5 mutation engine fills it).
- `source_attack_case_id` = the `SYNTHETIC_EMAIL_ATTACK_CASE` record id.
- `blue_detected` = `True` iff: `risk_score >= expected_min_risk_score`, expected behavioural-flag subset present, expected precursor-indicator subset present, recommended_action in expected set.
- `baseline_confidence` = a 0–1 derived value (proposed: normalised `risk_score / 100`).
- `failure_modes` = explicit list of named modes (proposed initial set in §5).
- `mutation_recommended` = `True` when `blue_detected is False`.

### §4.4 WEAKNESS_REPORT writes

One per Red profile per battery run, written **after** the per-case chain completes. Carries a **categorised** failure-modes summary (the Month 4 gate language) so Month 5 mutation work has structured input rather than a flat aggregate.

- `weakness_kind` = `f"phase_1_3_red_{red_profile}_battery"`.
- `anonymized_pattern` = an aggregated text summary that names each failure-mode bucket and its count (e.g. `"missing_attachment_indicator:8; risk_score_below_floor:5; missing_behavioral_flag:3"`).
- `confidence_gap` = `1.0 - (mean blue_detected score across cases)`.
- `source_record_ids` = list of `MUTANT_EVALUATION` record ids in this battery.
- `raw_tenant_data_removed = True` (structurally guaranteed; synthetic-only inputs).

The per-profile weakness report is the artefact Month 5's mutation-engine specialisation consumes; the existing sandbox-loop flow that turns a weakness into a signed `POLICY_UPDATE` is unchanged.

## §5 Blue-Agent Evaluation Contract

### §5.1 The Blue agent is the production agent

Phase 1.3 evaluates the actual `run_email_risk_scoring_cycle` plus the Phase 1.2 `build_precursor_overlay`. No alternate "sandbox Blue" code path. The LLM client used by Blue inside the sandbox is the **deterministic fake LLM client** used by Month 1 / Month 2 E2E tests, not a live xAI / Anthropic call.

Rationale: Phase 1.3's job is to stress-test the **deterministic** parts of the system (Phase 1.2 detectors + agent wiring + schema contract) at scale. Live-LLM stress testing is Month 2's harness (which has its own 40-case dataset + cost story); Phase 1.3 is for runtime regression detection at sandbox speed and cost.

### §5.2 Per-case pass / fail decision

A case passes when **all** of the following hold:

1. The Blue agent successfully produces an `EmailAnalysisPayload` (no `EMAIL_ANALYSIS_FAILURE` record).
2. `risk_score >= expected_min_risk_score` and (when set) `risk_score <= expected_max_risk_score`.
3. Every flag in `expected_behavioral_deviation_flags_subset` is present in `risk_analysis.behavioral_deviation_flags`.
4. Every indicator in `expected_precursor_indicators_subset` is present in `ransomware_precursor_analysis.precursor_indicators`.
5. `recommended_action in expected_recommended_action_in`.

Required-subset semantics across all expectations (extras are not failure unless an optional `forbidden_*` tuple is added later in a follow-up calibration pass).

### §5.3 Failure-mode taxonomy

Per Matt's §11 decision 4: enum-typed failure mode + **dynamic detail stored separately**. The eight canonical mode strings live in `Phase13FailureMode: TypeAlias = Literal[...]`; the dynamic detail (the specific missing flag / indicator / action / etc.) lives on `Phase13FailureDetail.dynamic_detail: str | None`. Sandboxing the dynamic part keeps the enum strict while keeping the diagnostic information intact.

| `failure_mode` (Literal) | `dynamic_detail` when set | Meaning |
|---|---|---|
| `analysis_failure_record_written` | reason tag from `EmailAnalysisFailurePayload.failure_reason` | Blue could not produce a valid `EmailAnalysisPayload` for this synthetic case |
| `unexpected_blue_exception` | `type(exc).__name__` | Blue raised an unhandled exception (defensive; scoring agent normally catches LLM errors into a failure record) |
| `risk_score_below_floor` | `f"{actual}<{floor}"` | `risk_score < expected_min_risk_score` |
| `risk_score_above_ceiling` | `f"{actual}>{ceiling}"` | `risk_score > expected_max_risk_score` when ceiling is set |
| `missing_behavioral_flag` | the missing `BehavioralDeviationFlag` value | One expected `BehavioralDeviationFlag` not emitted |
| `missing_precursor_indicator` | the missing `PrecursorIndicator` value | One expected `PrecursorIndicator` not emitted |
| `recommended_action_unexpected` | the actual emitted action | Recommended action outside expected set |
| `precursor_block_missing` | (None) | `ransomware_precursor_analysis is None` when a precursor indicator was expected |

These eight modes map one-to-one into the `WeaknessReportPayload.anonymized_pattern` bucket-count summary, which keeps Month 5 mutation reasoning narrowly typed without losing the dynamic detail when diagnostics need it.

### §5.4 Determinism contract

`run_red_battery_cycle(red_profile=..., seed=...)` is deterministic. Same Red profile + same seed → byte-identical sequence of `SYNTHETIC_EMAIL_ATTACK_CASE` + `MUTANT_EVALUATION` + `WEAKNESS_REPORT` records.

(Implementation note for Month 4: avoid any `datetime.now()` calls inside Red generation; the cases use `received_at = base_clock + timedelta(seconds=case_index)` from a base clock passed in via config, the same pattern Phase 1.1 uses with `now_provider`.)

## §6 Promotion Boundary Back Into Policy Updates

Phase 1.3 **does not** mutate production policy. It produces evidence.

The full promotion chain is:

```text
Phase 1.3 WEAKNESS_REPORT
        │
        ▼  (Month 5 — Phase 1.4 mutation engine specialisation; out of Month 4 scope)
        ▼
Mutation engine reads WEAKNESS_REPORT in sandbox,
generates a candidate POLICY_UPDATE (signed),
signs target_production_tenant_id explicitly,
emits sandbox audit_verdict APPROVED.
        │
        ▼
Promotion pipeline (core/policy/pipeline.py) re-validates signature,
cross-tenant check, audit chain integrity.
        │
        ▼
apply_signed_policy gate (Guardrail 11):
kill-switch (outermost) -> signature re-verify -> cross-tenant defence
-> rollback-history -> policy applied.
        │
        ▼
Next production cycle reads the new ProductionPolicyState.
```

Three rules that Phase 1.3 must honour:

1. **No direct policy emission from Red profiles.** Red writes only `SYNTHETIC_EMAIL_ATTACK_CASE`. Period.
2. **No new signing key, no new gate, no new write surface.** Phase 1.3 reuses every existing security surface; the Guardrail 11 surface list stays at the same four entries it has had since the multi-tenant Phase 2 work.
3. **Sandbox WeaknessReports tagged distinctively.** `weakness_kind = "phase_1_3_red_<profile>_battery"` so the Month 5 mutation engine can distinguish Phase 1.3 battery reports from production-loop regression reports (those have `weakness_kind = "production_regression_..."` style identifiers). Without this tag, Month 5 might mutate based on synthetic Red performance against a synthetic Red, which is a cycle that does not improve production.

## §7 Month 4 Gate Criteria

Roadmap gate from `12_Month_Specialization_Roadmap.md` Month 4:

> Red × Blue battery runs end-to-end producing a weakness report with **concrete, documented failure modes per Red profile** (not a flat aggregate — categorised).

The gate is **HIT** when all of the following pass deterministically in CI:

1. `tests/test_phase_1_3_sandbox_training_pit.py::test_red_battery_produces_per_profile_weakness_reports`
   - Runs all four Red profiles end-to-end with a fixed seed.
   - Asserts exactly four `WEAKNESS_REPORT` records exist, one per profile.
   - Asserts each report's `weakness_kind` matches the `phase_1_3_red_<profile>_battery` convention.
   - Asserts each report's `anonymized_pattern` contains **at least two distinct failure-mode bucket strings** (i.e. categorisation is real, not aggregate).
   - Asserts each report's `source_record_ids` cardinality matches the per-profile case count.
2. `tests/test_phase_1_3_sandbox_training_pit.py::test_each_red_profile_emits_at_least_100_cases_per_battery`
   - For each Red profile, at least 100 `SYNTHETIC_EMAIL_ATTACK_CASE` records produced per battery run.
3. `tests/test_phase_1_3_sandbox_training_pit.py::test_red_battery_is_byte_deterministic_across_runs`
   - Two `run_red_battery_cycle(seed=42)` runs produce byte-identical record sequences (case_index order, payload contents).
4. `tests/test_phase_1_3_sandbox_training_pit.py::test_each_red_profile_covers_every_locked_enum_value_it_drives`
   - `fake_invoice_red_001` + `vendor_update_red_001` together emit at least one case per `BehavioralDeviationFlag` value.
   - `malicious_attachment_red_001` emits at least one case per attachment-class `PrecursorIndicator`.
   - `obfuscated_url_red_001` emits at least one case per URL / body-language `PrecursorIndicator`.
   - Catches schema drift: a newly added enum value forces a Red-side coverage extension before the gate test can pass.
5. `tests/test_phase_1_3_sandbox_training_pit.py::test_red_profiles_never_write_outside_sandbox_environment`
   - Negative assertion: no production tenant blackboard contains any record produced during a Red-battery run.
6. `tests/test_phase_1_3_sandbox_training_pit.py::test_phase_1_3_does_not_emit_policy_update_records`
   - Negative assertion: zero `POLICY_UPDATE` records produced by Phase 1.3 (those belong to Month 5).
7. `tests/test_phase_1_3_sandbox_training_pit.py::test_weakness_reports_are_raw_tenant_data_removed`
   - Pin the structural guarantee (already enforced by the schema, but the test makes the intent explicit).

Acceptance count target: **≥ 10 new tests** total (roadmap minimum), including the seven gate tests above plus at least three coverage-detail tests (one per Red profile's per-axis correctness).

### §7.1 What the gate does NOT require

- Phase 1.3's gate does **not** require Blue to detect every Red case. The whole point is to surface gaps; the gate only requires that the gaps be **categorised** and persisted as `WEAKNESS_REPORT` records.
- Phase 1.3's gate does **not** require Month 5's mutation engine to be live. The promotion path documented in §6 is the receiving end; Month 5 wires it.
- Phase 1.3's gate does **not** require a live LLM call. The Blue agent runs with the deterministic fake LLM client (see §5.1).

## §8 Out of Scope (Deferred to Later Months / Years)

These are intentionally **not** in Phase 1.3 scope:

- Mutation-engine specialisation (`fraud_pattern_threshold`, `attachment_classifier_boost`, `url_obfuscation_sensitivity` mutation kinds) — **Month 5 (Phase 1.4)**.
- Closed-loop "Red finds gap → mutation engine fixes → next battery clears the gap" demo — **Month 5**.
- LLM-side Red generation (using an LLM to generate fraud emails) — out of Year 1. Phase 1.3 stays deterministic for cost, reproducibility, and governance.
- Tenant-aware Red personalisation (Red profiles that target a specific tenant's vendor list) — Year 2+ (requires the tenant-memory model that is itself deferred).
- HTML-rendered attachment content, real binary attachments, real malware corpus — out of Year 1. Phase 1.3 is metadata-only, same boundary as Phase 1.2.
- Blue mutation candidates (`MutantEvaluationPayload.candidate_agent_id`) — Month 5.
- Cross-tenant adversarial sharing (sandbox findings shared across tenant boundaries) — explicit non-goal; multi-tenant isolation Phase 2–8 forbids it.

## §9 Implementation Receipt — LANDED

Implementation complete 2026-05-21 against the §11 lockdown. Files landed:

| Path | Change |
|---|---|
| `core/blackboard/models.py` | Added `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE`, `Phase13FailureMode` (8-value `Literal`), `Phase13CaseTag` (1-value `Literal`, growable), `Phase13FailureDetail` (mode + optional `dynamic_detail`), `SyntheticEmailAttackCasePayload` (reserved-namespace validator on sender / recipient), wired into `PAYLOAD_MODELS` |
| `core/blackboard/__init__.py` | Re-exported the five new symbols |
| `core/orchestrator/routes.py` + `core/orchestrator/__init__.py` | New route `submit_synthetic_email_attack_case` writing under `Environment.SANDBOX` only |
| `core/orchestrator/registry.py` | Registered four Red profile agents (`fake_invoice_red_001`, `vendor_update_red_001`, `malicious_attachment_red_001`, `obfuscated_url_red_001`) with `Environment.SANDBOX` only and `allowed_write_types={RecordType.SYNTHETIC_EMAIL_ATTACK_CASE}` only; registered a dedicated `phase_1_3_sandbox_mutator_001` Blue role with `allowed_write_types={MUTANT_EVALUATION, WEAKNESS_REPORT}` |
| `core/scoring/email_risk_scoring_agent.py` | Added `score_one_email_payload(...)` in-memory helper returning either an `EmailAnalysisPayload` (with optional Phase 1.2 overlay) or a fully-typed `EmailRiskScoringFailureReason` dataclass; never writes to the Blackboard |
| `core/sandbox/red_agents/_seed_data.py` | Constant tables: vendor names, sender-domain variants, dollar-amount bands, urgency phrases, attachment filenames, URL hosts; all identifiers in `.example` / `.test` / `.invalid` |
| `core/sandbox/red_agents/fake_invoice_red.py` | `generate_cases(seed, count)` — 10 vendors × 5 domain-variant kinds × 2 urgency tiers → 100 deterministic cases per seed |
| `core/sandbox/red_agents/vendor_update_red.py` | 8 vendors × 4 update patterns × ~4 variants → ~128 cases |
| `core/sandbox/red_agents/malicious_attachment_red.py` | 8 sender variants × 7 attachment kinds × 2 body variants → 112 cases |
| `core/sandbox/red_agents/obfuscated_url_red.py` | 6 URL obfuscation kinds × 9 path variants × 2 body variants → 108 cases |
| `core/sandbox/red_agents/bucket_e_probes.py` | Four explicit mirrors of `vf-002`, `vf-005`, `ei-005`, `wt-004` tagged `bucket_e_regression_probe`, distributed across Red profiles by archetype |
| `core/sandbox/red_agents/__init__.py` | Re-exports |
| `core/sandbox/red_battery.py` | `run_red_battery_cycle(...)` entry point: kill-switch check at boundary, per-profile loop, in-memory Blue invocation via `score_one_email_payload`, per-case `MUTANT_EVALUATION` + `AUDIT_VERDICT`, per-profile aggregated `WEAKNESS_REPORT` with categorised failure-mode counts |
| `tests/test_phase_1_3_sandbox_training_pit.py` | 20 tests including the seven §7 gate tests and Decision 5 Bucket E verification |
| `4. Product_Roadmap/Month_4_Closeout_Readiness.md` | Month 4 closeout doc |
| `MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` | Indexed + Completed item 160 + 2026-05-21 entry |

### §9.1 Five §11 Decisions as Locked

1. **Schema** — landed as new `SyntheticEmailAttackCasePayload` + new `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE` (Matt's preferred path).
2. **Sandbox Blue invocation** — landed as in-memory `score_one_email_payload(inbound_payload, *, llm_client, enable_ransomware_precursor_overlay=True, source_email_record_id=None)` helper on the scoring agent module; battery cycles call it directly and never write `EMAIL_INBOUND` records to the sandbox blackboard.
3. **Per-battery case count** — every Red profile generates ≥ 100 unique cases per battery run; current counts after the cross-product layouts are 100 / 128 / 112 / 108. Pinned in `test_each_red_profile_emits_at_least_100_cases_per_battery`.
4. **Failure-mode taxonomy** — eight canonical strings in `Phase13FailureMode` Literal; the dynamic detail (specific flag / indicator / action / numerics) lives on `Phase13FailureDetail.dynamic_detail: str | None`. Phase 1.3 never stores dynamic detail inside the mode string itself.
5. **Bucket E mirroring** — four cases (`vf-002`, `vf-005`, `ei-005`, `wt-004`) explicitly mirrored in `bucket_e_probes.py`, tagged `bucket_e_regression_probe`, surfaced through the appropriate Red profile so Month 5 mutation work can pin them.

## §10 Cross-References

- `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md` §1.3 — strategic intent.
- `4. Product_Roadmap/12_Month_Specialization_Roadmap.md` Month 4 — operational gate.
- `4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md` — Blue-side fraud-scoring contract Red exercises.
- `4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md` — deterministic precursor overlay Red exercises.
- `4. Product_Roadmap/Q1_Checkpoint_2026.md` — Months 1–3 baseline this builds on.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/loop.py` — existing Month 0 sandbox loop scaffold.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py` — existing `WeaknessReportPayload`, `SyntheticAttackCasePayload`, `MutantEvaluationPayload`, `PolicyUpdatePayload` definitions.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/policy-promotion-pipeline.md` — promotion mechanics Phase 1.3 hands off to.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/multi-tenant-isolation-hardening.md` — isolation rules Phase 1.3 inherits.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/operator-kill-switch.md` — kill-switch contract Phase 1.3 inherits.

## §11 Decisions — LOCKED 2026-05-21

All five decisions approved by Matt; implementation landed per §9.

| # | Decision | Matt's call |
|---|---|---|
| 1 | New `SyntheticEmailAttackCasePayload` + `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE` vs extend existing | **New payload + new record type** |
| 2 | Sandbox Blue invocation: in-memory `score_one_email_payload(...)` vs full `EMAIL_INBOUND → EMAIL_ANALYSIS` chain | **In-memory helper** |
| 3 | Per-battery case count | **≥ 100 per profile per battery** (current counts: 100 / 128 / 112 / 108) |
| 4 | Failure-mode taxonomy stability | **Eight-mode taxonomy** with dynamic detail stored separately on `Phase13FailureDetail.dynamic_detail` |
| 5 | Bucket E mirror cases | **Include**, tagged `bucket_e_regression_probe` per the `Phase13CaseTag` Literal |

## Last Updated

2026-05-21 (§11 locked; implementation landed; **runtime baseline GREEN — 397 / 397 pytest, zero regressions, +38 Phase 1.3 tests including all seven §7 gate tests**)
