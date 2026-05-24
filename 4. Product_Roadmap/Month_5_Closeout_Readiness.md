# Month 5 Closeout Readiness

**Status:** Month 5 (Phase 1.4 Mutation Engine Specialisation) is complete and verified as of 2026-05-21.

**Build track:** SwarmCommand Agent Loop Runtime + NorthStar Inbox Shield + Fraud / Ransomware Specialization.

**Runtime baseline:** **419 tests passing** (exit code 0). **+22 new Phase 1.4 tests** including all seven §7 gate tests + the Month 2 byte-identity-at-v0 regression test.

**Pass-gate dependency:** Month 2 PASS on `grok-4` (xAI) still holds — pinned by `test_phase_1_4_parameters_at_v0_defaults_produce_byte_identical_scoring_output` against drift. Month 3 deterministic precursor overlay still active. Month 4 sandbox training pit still emitting the typed substrate Phase 1.4 consumes.

## Purpose

This file is the Month 5 closeout checkpoint. It exists to keep the team from rushing into Month 6 (Phase 2.1 Fraud Detection Product Sheet + per-tenant parameter overrides) before the Phase 1.4 mutation engine specialisation is verified, indexed, and bounded.

Month 5's job was to close the sandbox-to-production loop for fraud-specialised mutations: typed Phase 1.3 evidence in, signed promotion through the existing pipeline + gate, three production consumer read sites that observably change the next scoring cycle. That loop is now closed.

## Five §11 Decisions — Locked and Landed

All five Matt-approved decisions from `Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md` §11 are implemented and pinned by tests:

| # | Decision | Landing | Test pin |
|---|---|---|---|
| 1 | Strict `MutationKind` Literal with 6 values | `core/blackboard/models.py` | `test_mutation_kind_literal_includes_exact_six_values` |
| 2 | `RESERVED_PARAMETER_KEYS` enforced at BOTH promotion pipeline and Guardrail 11 gate | `core/production_state/parameter_keys.py` + `core/policy/pipeline.py` + `core/production_state/gate.py` | `test_reserved_parameter_keys_frozenset_exact_membership`, `test_unauthorized_parameter_keys_helper_returns_sorted_diff`, `test_promotion_pipeline_rejects_unauthorized_parameter_key_sandbox_side`, `test_apply_signed_policy_rejects_unauthorized_parameter_key_in_requested_parameters` |
| 3 | Wire fraud, attachment, and URL parameter read sites now | `core/precursor/analysis.py` + `core/scoring/email_risk_scoring_agent.py` + `core/production/loop.py` | `test_fraud_lift_only_applies_when_llm_fraud_signal_already_present`, `test_close_the_loop_red_battery_to_next_cycle_effect` |
| 4 | `bucket_e_improvement_floor=0.05` only for matching-axis `bucket_e_regression_probe` evidence | `core/mutation/engine.py::_BUCKET_E_MATCHING_AXIS` + `_resolve_minimum_improvement` | `test_bucket_e_improvement_floor_relaxes_minimum_for_matching_axis_evidence`, `test_bucket_e_floor_does_not_relax_for_cross_axis_evidence` |
| 5 | `per_cycle_promotion_cap=3` | `core/mutation/engine.py::MutationEngineConfig.per_cycle_promotion_cap` + `_apply_per_cycle_cap` | `test_per_cycle_promotion_cap_caps_promotions_to_three_by_default` |

Decisions 2 and 4 are the two Matt-side tightenings vs the spec-recommended defaults:

- **Decision 2 tightening**: spec recommended gate-only enforcement; Matt locked in defense in depth across BOTH the promotion pipeline (sandbox-side reject before crossing the boundary) AND the Guardrail 11 gate (apply-time reject on both signed payload and `requested_parameters` kwarg).
- **Decision 4 tightening**: spec recommended any Bucket E probe relaxes the floor; Matt narrowed to archetype-matching probes only via the `_BUCKET_E_MATCHING_AXIS` table so cross-axis bleed is structurally impossible.

## Month 5 Deliverables

All deliverables from `Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md` §9 are landed:

1. **Schema delta in `core/blackboard/models.py`.**
   - `MutationKind: TypeAlias = Literal[...]` with 6 closed values per §5.1.
   - `MutationCandidate.mutation_kind` retyped from `str` to `MutationKind` (Decision 1).
   - Re-exported from `core/blackboard/__init__.py`.

2. **`RESERVED_PARAMETER_KEYS` module + dual-boundary enforcement.**
   - New file `core/production_state/parameter_keys.py` with the `frozenset` + `unauthorized_parameter_keys` helper.
   - Promotion pipeline (`core/policy/pipeline.py::run_policy_promotion_cycle`) writes a sandbox-side REJECTED `audit_verdict` with `findings=["unauthorized_parameter_key=<key>"]` and refuses to emit the production-side audit + workflow trigger when a signed `POLICY_UPDATE` carries an unauthorized key.
   - Guardrail 11 gate (`core/production_state/gate.py::apply_signed_policy`) raises `GovernanceError("unauthorized parameter key: ...")` on both the signed payload's `parameters` dict AND the caller's `requested_parameters` kwarg.

3. **Mutation engine extensions in `core/mutation/engine.py`.**
   - `select_mutation_kind(...)` pure function maps `(Phase13CaseArchetype, Counter[Phase13FailureMode])` → `MutationKind | None` per §2.2.
   - `MutationEngineConfig` extended with `enable_phase_1_4_mutation_kinds`, `bucket_e_improvement_floor=0.05`, `per_cycle_promotion_cap=3`, `fraud_pattern_dominance_threshold=0.30`, `precursor_dominance_threshold=0.20`.
   - `_resolve_minimum_improvement` enforces the matching-axis Bucket E relaxation via `_BUCKET_E_MATCHING_AXIS`.
   - `_apply_per_cycle_cap` sorts promoted candidates by improvement and demotes overflow with `retired_reason="cycle_promotion_cap_reached"`.
   - `_build_evidence_chain` populates `sandbox_evidence_ids` per §5.5 with weakness report + top-N failed mutant evaluations + matching Bucket E case ids, capped at `MAX_EVIDENCE_IDS_PER_PROMOTION = 20`.
   - Loaders join `MUTANT_EVALUATION → SYNTHETIC_EMAIL_ATTACK_CASE → WEAKNESS_REPORT` so per-Red-profile aggregation is correct.
   - Legacy Month 0 sandbox-loop evals (no `phase_1_3_failure_details`) take the unchanged Month 0 candidate path.
   - Drift catcher at import time: `_BUCKET_E_MATCHING_AXIS` membership must match the Phase 1.4 `MutationKind` values; missing or extra entries raise at import.

4. **Production consumer wiring (Decision 3 — all three sites).**
   - `core/precursor/analysis.py::build_precursor_overlay` accepts optional `attachment_floor_lift: int = 0` and `url_obfuscation_floor_lift: int = 0` kwargs that additively lift the respective precursor sub-scores (clamped 0–25 in, clamped 0–100 out).
   - `core/scoring/email_risk_scoring_agent.py::EmailRiskScoringConfig` gains three new fields (`fraud_risk_floor_lift`, `attachment_risk_floor_lift`, `url_obfuscation_floor_lift`), all default 0. `_overlay_ransomware_precursor` threads them through; the fraud lift only applies when `vendor_fraud_score >= 40` OR `wire_transfer_anomaly_score >= 40` (never raises a safe-rated email).
   - `core/production/loop.py::run_production_cycle` reads the three reserved parameter keys from `policy_state.parameters` on cycle entry and injects them into a fresh scoring-agent config. Coercion + clamping in `_coerce_int_parameter` keeps the read robust against a corrupt state file.

5. **Test suite.**
   - File: `tests/test_phase_1_4_mutation_engine_specialization.py`.
   - 22 tests covering: closed `MutationKind` Literal drift (1), `RESERVED_PARAMETER_KEYS` drift + dual-boundary enforcement (4), `select_mutation_kind` routing for all three new kinds + hard non-selection modes + no-dominance retreat (7), signed `POLICY_UPDATE` parameter-key typing (1), Month 2 byte-identity-at-v0 protection (1), fraud-lift gating on LLM-side fraud signal (1), close-the-loop end-to-end gate (1), per-cycle cap (1), matching-axis Bucket E relaxation positive case (1), matching-axis Bucket E table structural pin (1), evidence chain shape (1), sandbox-only promotion (1), legacy Month 0 fallback (1).
   - All seven §7 gate tests present and green:
     1. `test_select_mutation_kind_maps_fake_invoice_archetype_to_fraud_pattern_threshold`.
     2. `test_select_mutation_kind_maps_malicious_attachment_archetype_to_attachment_classifier_boost`.
     3. `test_select_mutation_kind_maps_obfuscated_url_archetype_to_url_obfuscation_sensitivity`.
     4. `test_mutation_engine_emits_signed_policy_update_with_typed_parameter_key` (loops over all three Phase 1.4 kinds).
     5. `test_apply_signed_policy_rejects_unauthorized_parameter_key_in_requested_parameters` (mirror: `test_promotion_pipeline_rejects_unauthorized_parameter_key_sandbox_side`).
     6. `test_phase_1_4_parameters_at_v0_defaults_produce_byte_identical_scoring_output` — **the Month 2 PASS gate protection**.
     7. `test_close_the_loop_red_battery_to_next_cycle_effect` — **the roadmap-mandated Month 5 gate**.

## Sandbox-to-Production Loop — Verified Closed

The end-to-end loop is exercised by `test_close_the_loop_red_battery_to_next_cycle_effect`:

1. Seed 40 `fake_invoice` Phase 1.3 mutant evaluations dominated by `risk_score_below_floor`.
2. `run_mutation_cycle` selects `fraud_pattern_threshold` and emits a signed `POLICY_UPDATE` carrying `{"fraud_risk_floor_lift": 25}` and a typed evidence chain.
3. `run_policy_promotion_cycle` verifies the signature, accepts the reserved key, emits the production-side `audit_verdict` + `workflow_trigger`.
4. `apply_pending_policies` walks the chain, calls `apply_signed_policy` with the signed payload's parameters as `requested_parameters`. The gate's signature re-verification + reserved-key check + cross-tenant check all pass; `production_state.parameters["fraud_risk_floor_lift"]` is now `25`.
5. A fresh `score_one_email_payload` call on a synthetic moderate-fraud email (LLM-side `vendor_fraud_score=55`) yields a higher `risk_score` than the pre-promotion baseline because the overlay now applies the +25 lift.

The same chain proves all three Phase 1.4 read sites are live; the §7 gate-test-#4 family proves each of the three mutation kinds writes the right reserved key.

## Sandbox-safety + Promotion Boundary — Held

Phase 1.4 changes no sandbox-safety boundary. The mutation engine still:

- Reads only from the sandbox blackboard (`_load_sandbox_records`).
- Writes only signed `POLICY_UPDATE` records into the sandbox (`submit_policy_update` with `sandbox_tenant_id=...`).
- Never opens or writes to a production blackboard directly.

Phase 1.4 also changes no promotion-boundary plumbing:

- Signing (`core/policy/signing.py`), promotion pipeline shape (`run_policy_promotion_cycle`), and Guardrail 11 gate (`apply_signed_policy`) keep all their pre-Phase-1.4 invariants. The two additions (pipeline + gate reservation check) are purely additive — they catch one new failure class without weakening any existing check.

## What Phase 1.4 Did NOT Touch

Locked here so it stays out of scope:

- The LLM system prompt and Month 2 scoring rubric. Phase 1.4 only adds deterministic floor lifts after LLM validation.
- The `core/precursor/` detector internals (only `analysis.py::build_precursor_overlay`'s call signature changed; the four sub-detectors are unchanged).
- The Month 4 Red profile generators, `score_one_email_payload`, and the Red battery cycle. Phase 1.4 consumes their output without mutating their behaviour.
- Per-tenant parameter overrides (deferred to Phase 1.5 / Month 6 per §8).
- A/B numeric improvement proofs on the full 40-case eval dataset (deferred to Phase 1.5).
- Operator UI for parameter inspection (deferred to Phase 2.3 — Evidence & Reporting Layer).
- Automatic rollback on regression (the rollback primitive is wired and usable; Phase 1.4 leaves operator-initiated rollback as the only trigger).

## Conditions for Starting Month 6

Month 6 (Phase 2.1 Fraud Detection Product Sheet + per-tenant override surface) can begin when:

1. ☑ Month 5 (this doc) is signed off.
2. ☑ All five §11 decisions are landed and test-pinned.
3. ☑ Runtime baseline holds (419 / 419 pytest green).
4. ☑ Close-the-loop end-to-end test reproducible on `tmp_path` blackboards.
5. ☑ Month 2 PASS-gate byte-identity protected by `test_phase_1_4_parameters_at_v0_defaults_produce_byte_identical_scoring_output`.
6. ☐ Matt approval: explicit "begin Month 6 — Fraud Detection Product Sheet + per-tenant overrides" decision.

The mutation engine is now specialised, the parameter contract is locked at both boundaries, and the production scoring path observably responds to promoted policy state. Month 6 inherits a fully closed loop; the next work is product-surface (operator-facing parameter visibility, per-tenant differentiation, and the customer-facing product sheet for the fraud-defence specialisation).

## Last Updated

2026-05-21
