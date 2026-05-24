# Month 4 Closeout Readiness

**Status:** Month 4 (Phase 1.3 Sandbox Training Pit) is complete and verified as of 2026-05-21.

**Build track:** SwarmCommand Agent Loop Runtime + NorthStar Inbox Shield + Fraud / Ransomware Specialization.

**Runtime baseline:** **397 tests passing** (exit code 0). **+38 new Phase 1.3 tests** including all seven §7 gate tests.

**Pass-gate dependency:** Month 2 PASS on `grok-4` (xAI) still holds; Month 3 deterministic precursor overlay still active; Month 4 introduces no production-side runtime changes.

## Purpose

This file is the Month 4 closeout checkpoint. It exists to keep the team from rushing into Month 5 (mutation engine + promotion pipeline) before the Phase 1.3 sandbox training pit is verified, indexed, and bounded.

Month 4's job was not to ship mutation, promotion, or any production-facing change. Month 4's job was to stand up a sandbox-only training substrate so Month 5 mutation reasoning has typed, deterministic Blue-failure evidence to work from. That substrate is now live.

## Five §11 Decisions — Locked and Landed

All five Matt-approved decisions from `Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md` §11 are implemented and pinned by tests:

| # | Decision | Landing | Test pin |
|---|---|---|---|
| 1 | New `SyntheticEmailAttackCasePayload` + `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE` | `core/blackboard/models.py` | `test_record_type_includes_synthetic_email_attack_case`, `test_synthetic_email_attack_case_round_trips_through_pydantic_validation` |
| 2 | In-memory `score_one_email_payload(...)` helper | `core/scoring/email_risk_scoring_agent.py` | `test_score_one_email_payload_never_writes_to_blackboard`, `test_red_battery_never_writes_email_inbound_records` |
| 3 | ≥ 100 cases per Red profile per battery | Four generators under `core/sandbox/red_agents/` | `test_each_red_profile_emits_at_least_100_cases_per_battery`, `test_each_red_profile_has_unique_case_ids` |
| 4 | Eight-mode failure taxonomy with dynamic detail stored separately | `Phase13FailureMode` Literal + `Phase13FailureDetail` model | `test_phase_13_failure_mode_literal_exact_eight_values`, `test_phase_13_failure_detail_separates_mode_from_dynamic_detail`, `test_red_battery_failure_details_carry_typed_mode_and_dynamic_detail_separately` |
| 5 | Bucket E mirrored cases tagged `bucket_e_regression_probe` | `core/sandbox/red_agents/bucket_e_probes.py` | `test_bucket_e_probes_are_all_tagged_bucket_e_regression_probe`, `test_bucket_e_probes_distribute_across_red_profiles`, `test_red_battery_includes_bucket_e_probes_when_enabled` |

## Month 4 Deliverables

All deliverables from `Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md` §9 are landed:

1. **Schema delta in `core/blackboard/models.py`.**
   - `RecordType.SYNTHETIC_EMAIL_ATTACK_CASE` added.
   - `Phase13FailureMode` Literal (8 closed values).
   - `Phase13CaseTag` Literal (1 value, additive-growable).
   - `Phase13CaseArchetype` Literal (4 values pinned to Red profile families).
   - `Phase13FailureDetail` model (mode + optional dynamic detail).
   - `SyntheticEmailAttackCasePayload` model with three validators:
     - `raw_tenant_data_removed` always True.
     - Sender / recipient must live in `.example` / `.test` / `.invalid` namespace.
     - `expected_min_risk_score <= expected_max_risk_score` when both set.
   - `MutantEvaluationPayload` extended with `phase_1_3_failure_details: list[Phase13FailureDetail]` (additive; legacy `failure_modes: list[str]` preserved).
   - `PAYLOAD_MODELS` + `validate_record_against_registry` updated; sandbox-only enforcement on the new record type.

2. **Orchestrator route + registry registrations.**
   - `submit_synthetic_email_attack_case` route in `core/orchestrator/routes.py`.
   - Five new agents in `core/orchestrator/registry.py`:
     - `fake_invoice_red_001`, `vendor_update_red_001`, `malicious_attachment_red_001`, `obfuscated_url_red_001` — sandbox-only Red profiles, `allowed_write_types = {SYNTHETIC_EMAIL_ATTACK_CASE}` only.
     - `phase_1_3_sandbox_mutator_001` — sandbox-only Blue mutator, `allowed_write_types = {MUTANT_EVALUATION, WEAKNESS_REPORT}`.

3. **In-memory `score_one_email_payload(...)` helper.**
   - File: `core/scoring/email_risk_scoring_agent.py`.
   - Shares system prompt + schema validator + precursor overlay with the production scoring agent.
   - Returns `EmailAnalysisPayload | EmailRiskScoringInMemoryFailure`.
   - Never touches a `RouteContext` so cannot accidentally write to a real blackboard.

4. **Four fraud-specialized Red profile generators.**
   - `core/sandbox/red_agents/fake_invoice_red.py` — 100 cases per battery (10 vendors × 5 domain variants × 2 urgency tiers).
   - `core/sandbox/red_agents/vendor_update_red.py` — 128 cases (8 vendors × 4 update patterns × 4 stylistic variants).
   - `core/sandbox/red_agents/malicious_attachment_red.py` — 112 cases (7 attachment kinds × 8 sender variants × 2 body variants).
   - `core/sandbox/red_agents/obfuscated_url_red.py` — 108 cases (6 URL kinds × 9 path fragments × 2 body variants).
   - Shared seed data in `core/sandbox/red_agents/_seed_data.py`; all identifiers in the reserved `.example` / `.test` / `.invalid` namespace.

5. **Bucket E mirror cases.**
   - `core/sandbox/red_agents/bucket_e_probes.py`.
   - Four mirrors of the Month 2 honest gaps (`vf-002`, `vf-005`, `ei-005`, `wt-004`), distributed across `fake_invoice_red_001` (2) and `vendor_update_red_001` (2), all tagged `bucket_e_regression_probe`.

6. **Red battery cycle.**
   - File: `core/sandbox/red_battery.py`.
   - Kill-switch check at the sandbox boundary (one cheap read; raise on engaged).
   - Per-profile loop: write `SYNTHETIC_EMAIL_ATTACK_CASE`, invoke Blue via `score_one_email_payload`, write typed `MUTANT_EVALUATION` (with both the new `phase_1_3_failure_details` and the legacy `failure_modes` view), write `AUDIT_VERDICT` (quarantined when Blue missed anything; requires human review).
   - Per-profile aggregated `WEAKNESS_REPORT` with bucket-counted failure-mode summary, `raw_tenant_data_removed=True`.

7. **Test suite.**
   - File: `tests/test_phase_1_3_sandbox_training_pit.py`.
   - 38 tests covering: schema delta (9), in-memory helper (5), per-profile case counts + determinism (3), per-archetype enum-coverage drift catchers (4), Bucket E mirroring (3), Red battery cycle end-to-end (14).
   - All seven §7 gate tests present and green:
     1. Red battery produces full four-record signature per profile.
     2. Failure details carry typed mode + dynamic detail separately.
     3. Generation is byte-deterministic across runs.
     4. Sandbox kill-switch aborts before any record is written.
     5. No record ever leaves the sandbox environment.
     6. No `POLICY_UPDATE` records emitted (promotion stays in Month 5).
     7. Weakness reports carry `raw_tenant_data_removed=True`.

## Sandbox-safety Boundary — Verified

The Red battery cycle is sandbox-only by construction. Every layer enforces it:

- `SyntheticEmailAttackCasePayload.require_reserved_namespace` rejects any case carrying a real-looking domain at validation time.
- `submit_synthetic_email_attack_case` hard-codes `Environment.SANDBOX`.
- The four Red profile agents in the registry only have `Environment.SANDBOX` in their `allowed_environments`.
- `validate_record_against_registry` adds `SYNTHETIC_EMAIL_ATTACK_CASE` to the existing sandbox-only set (alongside `SYNTHETIC_ATTACK_CASE` and `MUTANT_EVALUATION`).
- `run_red_battery_cycle` calls `is_kill_switch_engaged(scope="SANDBOX")` before any work.
- `test_red_battery_never_writes_outside_sandbox_environment` and `test_red_battery_does_not_emit_policy_update_records` keep this drift-catched.

## Promotion Boundary — Held

Phase 1.3 does **not** write `POLICY_UPDATE` records, does **not** mutate any production-side configuration, and does **not** invoke the mutation engine. Promotion remains entirely the Month 5 surface. Phase 1.3 only produces the diagnostic substrate (typed `WEAKNESS_REPORT` + per-case `MUTANT_EVALUATION` + per-case `AUDIT_VERDICT`) that Month 5 mutation planning will consume.

## Conditions for Starting Month 5

Month 5 (mutation engine + promotion pipeline + Guardrail 11 verification on the new substrate) can begin when:

1. ☑ Month 4 (this doc) is signed off.
2. ☑ All five §11 decisions are landed and test-pinned.
3. ☑ Runtime baseline holds (397 / 397 pytest green).
4. ☑ Phase 1.3 Red battery is reproducible end-to-end on `tmp_path` blackboards.
5. ☐ Matt approval: explicit "begin Month 5 — Mutation Engine" decision.

The Q1 checkpoint already pre-staged Bucket E as the obvious first mutation target. Phase 1.3 now makes those four cases first-class, tagged sandbox cases (`bucket_e_regression_probe`), so Month 5 can begin against a stable, typed substrate without needing to re-derive the gaps from the Month 2 eval reports.

## Last Updated

2026-05-21
