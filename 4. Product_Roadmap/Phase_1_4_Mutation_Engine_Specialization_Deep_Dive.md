# Phase 1.4 — Mutation Engine Specialisation Deep Dive

**Phase reference:** `Fraud_Ransomware_Specialization_Roadmap.md` §1.4 (Mutation Engine Specialisation).
**Roadmap month:** `12_Month_Specialization_Roadmap.md` Month 5 (October 2026 in calendar terms).
**Status:** **§11 LOCKED by Matt 2026-05-21. Implementation LANDED.** All five decisions approved (with two Matt-side tightenings — see §11); runtime code, schema delta, gate + pipeline parameter-key checks, three production consumer wirings, and the ≥10-test gate suite are live. See §9 implementation receipt.
**Predecessors that must already be in place:** Month 0 mutation engine (`core/mutation/engine.py`), Month 0 signed-policy promotion pipeline (`core/policy/pipeline.py`), Month 0 Guardrail 11 gate (`core/production_state/gate.py`), Month 0 policy rollback primitive (`core/policy/rollback.py`), multi-tenant isolation Phase 2–8, operator kill switch, Phase 1.1 fraud-scoring agent (`grok-4` PASS gate), Phase 1.2 ransomware-precursor overlay (`core/precursor/`), Phase 1.3 Sandbox Training Pit (LANDED 2026-05-21; `core/sandbox/red_battery.py` + four Red profiles + typed `Phase13FailureDetail` substrate).

## §0 Purpose

The mutation-engine infrastructure exists. Phase 1.4 **specialises** it — three fraud-specific mutation kinds, a typed `MutationKind` Literal, per-kind parameter contracts, and a real "close the loop" gate test that proves a Red-battery weakness report drives a signed `policy_update` through the existing Guardrail 11 gate into a `production_state.parameters` change that the next production scoring cycle reads.

Three constraints define Month 5's design:

1. **Do not redo the closed-loop pipeline.** Signing (`core/policy/signing.py`), promotion (`core/policy/pipeline.py`), gate (`core/production_state/gate.py`), rollback (`core/policy/rollback.py`), and the cross-tenant + signature-re-verification defences are all in force at Phase 1.3 closeout. Phase 1.4 extends only the **mutation-kind catalogue** + **parameter contracts** + **consumer wiring on the scoring agent**.
2. **Phase 1.3 substrate is the canonical evidence.** The mutation engine consumes typed `Phase13FailureDetail` records (eight-mode Literal taxonomy + `dynamic_detail`) and per-profile `WEAKNESS_REPORT` records produced by `run_red_battery_cycle`. It does not invent its own evidence channels and does not write to production blackboards.
3. **Operator review load stays bounded.** With four Red profiles × ≥100 cases × Bucket E mirrors, one Red battery can surface dozens of failure-mode buckets. Phase 1.4 introduces a per-cycle promotion cap (§5.4) and per-mutation-kind improvement floors (§5.3) so a single cycle never floods the operator with promotion reviews.

## §1 Fraud-Specialised Mutation Kinds

Three new mutation kinds register in the engine alongside the two legacy kinds. All five are pinned in a closed `MutationKind: TypeAlias = Literal[...]` per §11 Decision 1.

| Mutation kind | Drives | Selection signal | Production-side parameter family |
|---|---|---|---|
| `add_missing_signal_heuristic` *(legacy)* | Generic detector confidence | Per-case `missing_signal:*` failure mode | `confidence_boost: float` (existing) |
| `raise_confidence_weighting` *(legacy)* | Generic detector confidence | Per-case `confidence_below_threshold` failure mode | `confidence_boost: float` (existing) |
| **`fraud_pattern_threshold`** *(new)* | Phase 1.1 vendor / wire / invoice score thresholds | `Phase13FailureMode.risk_score_below_floor` + `Phase13FailureMode.recommended_action_unexpected` on `fake_invoice` / `vendor_update_pivot` archetypes | `fraud_risk_floor_lift: int` (0–25); applied as additive lift to `vendor_fraud_score` / `wire_transfer_anomaly_score` minimums in the scoring agent's overlay path |
| **`attachment_classifier_boost`** *(new)* | Phase 1.2 attachment-precursor sensitivity | `Phase13FailureMode.missing_precursor_indicator` on `malicious_attachment` archetype | `attachment_risk_floor_lift: int` (0–25); applied as additive lift to `EmailAnalysisRansomwarePrecursorAnalysis.attachment_risk_score` minimum + the `recommended_risk_floor` calculation |
| **`url_obfuscation_sensitivity`** *(new)* | Phase 1.2 URL-precursor sensitivity | `Phase13FailureMode.missing_precursor_indicator` on `obfuscated_url` archetype | `url_obfuscation_floor_lift: int` (0–25); applied as additive lift to `EmailAnalysisRansomwarePrecursorAnalysis.url_obfuscation_score` minimum + the `recommended_risk_floor` calculation |

### §1.1 Why exactly three new kinds

The three new kinds are one-to-one with the three Phase 1.1 / 1.2 fraud-and-ransomware sensitivity dials that the production scoring agent currently has no closed-loop way to tune:

- `fraud_pattern_threshold` → tunes Phase 1.1's vendor / wire / invoice score floors.
- `attachment_classifier_boost` → tunes Phase 1.2's attachment-precursor floor in the overlay.
- `url_obfuscation_sensitivity` → tunes Phase 1.2's URL-precursor floor in the overlay.

The two legacy kinds (`add_missing_signal_heuristic`, `raise_confidence_weighting`) stay in the catalogue unchanged. They are still used by the Month 0 sandbox loop (`core/sandbox/loop.py::run_sandbox_cycle`) which consumes generic `WeaknessReportPayload.weakness_kind=="low_confidence_detection"` patterns. Phase 1.4 does not deprecate them; it only adds three siblings.

### §1.2 What Phase 1.4 is NOT

- **Not a new detector module.** The three fraud-specialised parameters are read by the existing `core/precursor/` overlay + the existing `core/scoring/email_risk_scoring_agent.py`. No new files under `core/precursor/`.
- **Not a new promotion pipeline.** Signed `POLICY_UPDATE` records flow through the existing `run_policy_promotion_cycle` and the existing `apply_signed_policy` gate. Cross-tenant rejection, signature re-verification, rollback target-in-history check all unchanged.
- **Not a re-architecture of `MutantEvaluationPayload`.** Phase 1.3 already added the `phase_1_3_failure_details` field; Phase 1.4 consumes it but does not extend the payload further.
- **Not Phase 2.1.** The Month 5 roadmap pairs Phase 1.4 with Phase 2.1's *Fraud Detection Product Sheet*. The product sheet is content-only and out of scope for this deep dive; it is tracked separately in `Month_5_Closeout_Readiness.md` once that ships.

## §2 Mutation-Selection Boundary

Phase 1.4 must be deterministic and parametric, just like Phase 1.3. The selection function is a pure mapping from typed evidence to typed mutation kind.

### §2.1 Input evidence

The engine reads **two** sandbox record classes:

1. **Per-case `MUTANT_EVALUATION`** — already a Phase 1.3 output. Carries `phase_1_3_failure_details: list[Phase13FailureDetail]` (eight-mode Literal + `dynamic_detail`), `source_attack_case_id` (for evidence chain), `baseline_confidence`.
2. **Per-profile `WEAKNESS_REPORT`** — already a Phase 1.3 output. Carries `weakness_kind: "phase_1_3_red_profile:<id>"`, `anonymized_pattern: "phase_1_3:<archetype>:cases=N:failures=M:buckets=[mode=count,...]"`, `confidence_gap` (failure rate), `source_record_ids` (list of per-case sandbox record ids).

The engine consumes both: weakness reports drive **mutation-kind selection** (which archetype is failing most, which buckets dominate) and per-case mutant evaluations drive **confidence math** + **evidence chain** for the signed `POLICY_UPDATE`.

### §2.2 Selection rules — typed

A new pure function `select_mutation_kind(...)` maps `(Phase13CaseArchetype, Counter[Phase13FailureMode])` → `MutationKind | None`:

| Archetype + dominant failure mode | Mutation kind |
|---|---|
| `fake_invoice` + `risk_score_below_floor` ≥ 30 % of failures | `fraud_pattern_threshold` |
| `vendor_update_pivot` + (`risk_score_below_floor` OR `missing_behavioral_flag`) ≥ 30 % | `fraud_pattern_threshold` |
| `malicious_attachment` + `missing_precursor_indicator` ≥ 20 % | `attachment_classifier_boost` |
| `obfuscated_url` + `missing_precursor_indicator` ≥ 20 % | `url_obfuscation_sensitivity` |
| any archetype + `precursor_block_missing` ≥ 20 % | (no mutation; gate-level overlay is correctly disabled or a Phase 1.2 bug — surface as `audit_verdict` for operator review, not a parameter mutation) |
| any other distribution | `None` (retire the cycle's mutation attempt with `retired_reason="no_dominant_pattern"`) |

The 30 % / 20 % thresholds are baked into the engine as named constants (`FRAUD_PATTERN_DOMINANCE_THRESHOLD`, `PRECURSOR_DOMINANCE_THRESHOLD`) so tests can pin them and a future operator-controlled override is a one-line change.

### §2.3 Bucket E priority — matching-axis only

Per Matt's Phase 1.3 §11 Decision 5, the four Month 2 honest gaps mirrored as `bucket_e_regression_probe` cases are first-class Phase 1.3 substrate. Phase 1.4 prioritises them at the **improvement-floor** layer (§5.3) with the **matching-axis tightening** Matt locked in §11 Decision 4: the relaxed floor only applies when the Bucket E probe's archetype matches the axis the mutation kind tunes:

| Mutation kind | Archetypes whose Bucket E probes relax the floor |
|---|---|
| `fraud_pattern_threshold` | `fake_invoice`, `vendor_update_pivot` |
| `attachment_classifier_boost` | `malicious_attachment` |
| `url_obfuscation_sensitivity` | `obfuscated_url` |

This stops cross-axis bleed: a `fake_invoice` Bucket E probe (e.g. `bucket-e-vf-002-mirror`) can never lower the bar for an `attachment_classifier_boost` mutation. Current Phase 1.3 Bucket E coverage carries probes for `fake_invoice` + `vendor_update_pivot` only; `attachment_classifier_boost` and `url_obfuscation_sensitivity` mutations would only benefit from the relaxation if a future Bucket E expansion adds probes in those archetypes.

### §2.4 Hard non-selection cases

The engine never promotes when:

1. `Phase13FailureMode.unexpected_blue_exception` dominates → operator escalation (`audit_verdict` only), not a parameter mutation.
2. `Phase13FailureMode.analysis_failure_record_written` dominates → likely an LLM client issue (provider outage, schema-breaking response), not a parameter mutation.
3. The mutant evaluation chain references no `source_attack_case_id` → can't build the evidence chain, refuse to promote.
4. A weakness report carries `raw_tenant_data_removed=False` → refuse to consume; spec violation upstream.

All four cases are pinned by tests in §7.

## §3 Per-Kind Parameter Contracts

Per §11 Decision 2, each new mutation kind owns a single typed parameter key (or short keyset) and an explicit value range. The keys are also pinned in code so the production-side consumer (§4) cannot drift.

| Mutation kind | Parameter key | Type | Range | Default at `v0` |
|---|---|---|---|---|
| `fraud_pattern_threshold` | `fraud_risk_floor_lift` | `int` | 0–25 | 0 |
| `attachment_classifier_boost` | `attachment_risk_floor_lift` | `int` | 0–25 | 0 |
| `url_obfuscation_sensitivity` | `url_obfuscation_floor_lift` | `int` | 0–25 | 0 |

### §3.1 Why integer 0–25

The four Phase 1.2 sub-scores plus the Phase 1.1 fraud sub-scores are all 0–100. A 0–25 additive lift caps the engine at a quarter of the available headroom in any one promotion — enough to materially shift a borderline failure case without ever overpowering the LLM-derived analysis. Multiple promotions are additive (capped at 100 by the final clamp in the consumer), so the engine can still escalate sensitivity over several cycles if Red battery evidence keeps showing the same archetype failing.

### §3.2 Parameter consumer contract — typed

The `ProductionPolicyState.parameters` dict already has one key in use today (`confidence_boost`). Phase 1.4 adds three more reserved keys. A new module-level constant pins the full set:

```python
# core/production_state/parameter_keys.py (new)
RESERVED_PARAMETER_KEYS: frozenset[str] = frozenset({
    "confidence_boost",                # Month 0 legacy
    "fraud_risk_floor_lift",           # Phase 1.4 — fraud_pattern_threshold
    "attachment_risk_floor_lift",      # Phase 1.4 — attachment_classifier_boost
    "url_obfuscation_floor_lift",      # Phase 1.4 — url_obfuscation_sensitivity
})
```

Per Matt's §11 Decision 2 tightening — **the unauthorized-parameter-key check is enforced at BOTH boundaries**:

1. **Promotion pipeline** (`core/policy/pipeline.py::run_policy_promotion_cycle`). When the pipeline loads a signed `POLICY_UPDATE` whose `parameters` dict contains a key outside `RESERVED_PARAMETER_KEYS`, the pipeline writes a sandbox-side `audit_verdict` with `verdict=REJECTED` and `findings=["unauthorized parameter key: <key>"]` and never emits the production-side `audit_verdict` / `workflow_trigger`. Defense-in-depth: the unauthorized key is stopped *before* it crosses the production boundary.
2. **Guardrail 11 gate** (`core/production_state/gate.py::apply_signed_policy`). The gate also rejects with `GovernanceError("unauthorized parameter key: ...")` if the signed payload's `parameters` or the caller's `requested_parameters` kwarg contains any key outside `RESERVED_PARAMETER_KEYS`. This is the inner check, after signature re-verification and after the cross-tenant defence.

Both checks are additive and never relax the existing pipeline / gate validation; they only catch one new class of misuse. Pinned by separate tests at each layer.

### §3.3 Parameter shape sketch (`PolicyUpdatePayload.parameters`)

```jsonc
// fraud_pattern_threshold
{ "fraud_risk_floor_lift": 8 }

// attachment_classifier_boost
{ "attachment_risk_floor_lift": 12 }

// url_obfuscation_sensitivity
{ "url_obfuscation_floor_lift": 6 }
```

Single-key payloads on purpose. Multi-key parameter dicts are allowed (the gate accepts any subset of reserved keys), but each mutation kind only ever writes one key. This keeps the diff per promotion narrow and the rollback math trivial.

## §4 Production Consumer Wiring — In-Scope for Phase 1.4

Per §11 Decision 3, the Month 5 gate is **"sandbox → sign → promote → apply → next-cycle effect"**. That requires real consumer wiring on the production scoring agent, not just blackboard plumbing. Phase 1.4 wires three minimum read sites:

| Production read site | File | Reads parameter | Effect on next scoring cycle |
|---|---|---|---|
| Email risk scoring overlay | `core/scoring/email_risk_scoring_agent.py::_overlay_ransomware_precursor` | `fraud_risk_floor_lift` | After LLM validation, lifts `risk_score` floor by the configured int (clamped to 0–100) when the LLM-derived `vendor_fraud_score` or `wire_transfer_anomaly_score` ≥ 40 (i.e. there is already a fraud signal — never lifts safe-rated emails) |
| Precursor overlay floor | `core/precursor/analysis.py::build_precursor_overlay` | `attachment_risk_floor_lift` + `url_obfuscation_floor_lift` | Adds the respective lifts to `recommended_risk_floor` calculation. Pure-function signature is preserved: lifts are passed in as kwargs from the calling scoring agent, not read from disk inside `core/precursor/` |
| Production state load on cycle entry | `core/production/loop.py::run_production_cycle` | All three new keys | Reads `policy_state.parameters` once per cycle, threads the three lifts into the scoring agent + precursor overlay configuration; no per-email disk read |

### §4.1 What stays the same

- The LLM system prompt and rubrics are **not** touched. Phase 1.4 only adds deterministic floor lifts after LLM validation.
- The Month 2 `grok-4` PASS gate is preserved by an explicit safeguard: when all three Phase 1.4 lifts are at their `v0=0` defaults, the scoring agent's per-email output is byte-identical to the current Phase 1.2 + Phase 1.1 path. This is pinned by a regression test (§7 gate test #6).
- The Phase 1.2 overlay's one-directional `risk_score = max(llm_risk, precursor_floor)` rule still applies — Phase 1.4 only changes the *value* of `precursor_floor`, never the direction.

### §4.2 What does NOT get wired in Phase 1.4

- Per-tenant override surface (different lifts per tenant). Deferred to Phase 1.5 / Month 6 if customer evidence demands it.
- A/B comparison harness (run Phase 1.4-lifted scoring against the 40-case fraud-eval dataset to numerically prove improvement). Deferred to Phase 1.5; the Month 5 gate test proves *effect*, not *eval-numeric improvement*.
- A UI surface for operators to view the current `production_state.parameters` values. Deferred to Phase 2.3 (Evidence & Reporting Layer).

## §5 Mutation-Engine Updates

### §5.1 `MutationKind` Literal (new)

```python
# core/blackboard/models.py (additive)
MutationKind: TypeAlias = Literal[
    "add_missing_signal_heuristic",        # legacy
    "raise_confidence_weighting",          # legacy
    "fraud_pattern_threshold",             # Phase 1.4
    "attachment_classifier_boost",         # Phase 1.4
    "url_obfuscation_sensitivity",         # Phase 1.4
    "no_mutation",                         # sentinel — never emitted as a promotion
]
```

`MutationCandidate.mutation_kind` is retyped from `str` to `MutationKind`. This is a strict additive type narrowing; the engine's existing two legacy kinds are kept verbatim so the Month 0 sandbox loop's tests stay green.

### §5.2 `MutationEngineConfig` extension

```python
@dataclass(frozen=True)
class MutationEngineConfig:
    sandbox_tenant_id: str = "sandbox_default"
    governance_agent_id: str = "governance_001"
    minimum_improvement: float = 0.10
    promoted_confidence_cap: float = 0.95
    signing_key: SigningKey | None = None
    production_tenant_id: str = "tenant_demo"
    # --- Phase 1.4 additions (additive; all default-on) -----------------
    enable_phase_1_4_mutation_kinds: bool = True
    bucket_e_improvement_floor: float = 0.05
    per_cycle_promotion_cap: int = 3
    fraud_pattern_dominance_threshold: float = 0.30
    precursor_dominance_threshold: float = 0.20
```

### §5.3 Per-kind `minimum_improvement` resolution — matching-axis only

Per Matt's §11 Decision 4 tightening, the Bucket E floor relaxation only fires when the probe's archetype matches the axis the mutation kind tunes (see §2.3 table):

```python
def _resolve_minimum_improvement(
    config: MutationEngineConfig,
    *,
    mutation_kind: MutationKind,
    bucket_e_archetypes_in_evidence: frozenset[Phase13CaseArchetype],
) -> float:
    matching = _BUCKET_E_MATCHING_AXIS.get(mutation_kind, frozenset())
    if matching & bucket_e_archetypes_in_evidence:
        return min(config.minimum_improvement, config.bucket_e_improvement_floor)
    return config.minimum_improvement
```

Where `_BUCKET_E_MATCHING_AXIS` is the module-level constant matching §2.3's table. A `fraud_pattern_threshold` mutation whose evidence chain includes a `fake_invoice` Bucket E probe gets the relaxed 0.05 floor; an `attachment_classifier_boost` mutation whose evidence chain only includes `fake_invoice` Bucket E probes does **not** — the cross-axis case is intentionally excluded.

### §5.4 Per-cycle promotion cap

Across all four Red profiles in one battery, the engine sorts candidate mutations by `(candidate_confidence - baseline_confidence)` descending, then keeps only the top `config.per_cycle_promotion_cap`. Lower-ranked candidates are retired with `retired_reason="cycle_promotion_cap_reached"`. This keeps operator review bounded even when several archetypes regress at once.

### §5.5 Evidence chain — typed

Every signed `POLICY_UPDATE` Phase 1.4 emits carries a `sandbox_evidence_ids: list[UUID]` populated with:

1. The aggregated per-profile `WEAKNESS_REPORT` record id (one entry).
2. The per-case `MUTANT_EVALUATION` record ids that drove the chosen mutation kind (one or more entries; bounded by §5.6).
3. The originating `SYNTHETIC_EMAIL_ATTACK_CASE` record ids (one per per-case eval; only included for `bucket_e_regression_probe`-tagged cases to keep the list small).

This list is signed as part of the payload so the Guardrail 11 gate's existing signature re-verification covers it.

### §5.6 Evidence cap

`sandbox_evidence_ids` length is capped at `MAX_EVIDENCE_IDS_PER_PROMOTION = 20` so a runaway Red battery cannot bloat the production blackboard. Per-profile weakness reports plus the top-N per-case evaluations (ranked by `confidence_gap` descending) fit inside that bound for any plausible battery size.

## §6 Promotion Boundary — Unchanged

Phase 1.4 changes no boundary code. The signing → promotion → gate → consumer chain works as today:

| Step | Module | Phase 1.4 change |
|---|---|---|
| Sign sandbox policy update | `core/policy/signing.py::sign` | none |
| Submit signed `POLICY_UPDATE` | `core/orchestrator.submit_policy_update` | none |
| Run promotion pipeline | `core/policy/pipeline.py::run_policy_promotion_cycle` | none |
| Cross-tenant rejection | `core/policy/pipeline.py` (existing) | none |
| Promotion pipeline parameter-key check | `core/policy/pipeline.py::run_policy_promotion_cycle` | **+ unauthorized-parameter-key sandbox-side rejection** (per §3.2 Decision 2 tightening — defense in depth, stops the unauthorized key before it crosses the production boundary) |
| Guardrail 11 gate | `core/production_state/gate.py::apply_signed_policy` | **+ unauthorized-parameter-key rejection** on both signed `parameters` and `requested_parameters` kwarg (per §3.2) |
| Production state mutation | `core/production_state/state.py` | none |
| Production cycle reads new state | `core/production/loop.py::run_production_cycle` | **+ reads three new parameter keys and threads them to the scoring agent** (per §4) |
| Rollback primitive | `core/policy/rollback.py` | none — rollback for a Phase 1.4 parameter promotion uses the existing target-in-history check |

The one gate-side addition (unauthorized-key rejection) is the smallest change that prevents drift: any future module attempting to write a non-reserved key into `production_state.parameters` is rejected with `GovernanceError`, no matter how the key got into the signed payload.

## §7 Month 5 Gate Criteria

Per the 12-month roadmap, Month 5's gate is:

> "Mutation engine closes the loop on a vendor-fraud sensitivity boost (sandbox → sign → promote → apply → next-cycle effect)."

Phase 1.4 lands ≥ 10 new tests. The seven gate tests below are the minimum to certify the gate is closed:

1. **`test_select_mutation_kind_maps_fake_invoice_archetype_to_fraud_pattern_threshold`** — Given a `WEAKNESS_REPORT` whose `anonymized_pattern` shows `risk_score_below_floor` ≥ 30 % on `fake_invoice`, the selection function returns `MutationKind.fraud_pattern_threshold`.
2. **`test_select_mutation_kind_maps_malicious_attachment_archetype_to_attachment_classifier_boost`** — Same shape for the attachment archetype with `missing_precursor_indicator` ≥ 20 %.
3. **`test_select_mutation_kind_maps_obfuscated_url_archetype_to_url_obfuscation_sensitivity`** — Same shape for the URL archetype.
4. **`test_mutation_engine_emits_signed_policy_update_with_typed_parameter_key`** — For each of the three new mutation kinds, the signed `POLICY_UPDATE` carries exactly one of the three reserved keys (no key drift, no freeform key).
5. **`test_apply_signed_policy_rejects_unauthorized_parameter_key`** — Defense in depth: a signed policy carrying e.g. `parameters={"random_key": 1}` is rejected with `GovernanceError("unauthorized parameter key: ...")`.
6. **`test_phase_1_4_parameters_at_v0_defaults_produce_byte_identical_scoring_output`** — Regression catch: with all three lifts at 0, scoring agent output for the Month 2 fraud-eval dataset (subset) is byte-identical to the current Phase 1.2 + 1.1 baseline. **Pins the Month 2 PASS gate against drift.**
7. **`test_close_the_loop_red_battery_to_next_cycle_effect`** — Full end-to-end: run one Red battery, run mutation engine, run promotion pipeline, apply the signed policy through the gate, run one production scoring cycle on a synthetic email matching the mutation's archetype, assert the new `risk_score` is strictly greater than the pre-promotion baseline. **This is the roadmap-mandated Month 5 gate test.**

Supporting tests (additional ≥ 3 toward the ≥ 10 target):

8. **`test_per_cycle_promotion_cap_caps_promotions_to_three_by_default`**.
9. **`test_bucket_e_improvement_floor_relaxes_minimum_for_probe_evidence`**.
10. **`test_evidence_chain_includes_weakness_report_and_top_n_mutant_evaluations`**.

Additional drift catchers (recommended, not strictly gate):

- `test_mutation_kind_literal_includes_exact_six_values` (closed-enum drift catcher; mirrors the Phase 1.3 §7 pattern).
- `test_reserved_parameter_keys_frozenset_exact_membership` (parameter-key drift catcher).
- `test_unexpected_blue_exception_failure_mode_does_not_trigger_mutation` (§2.4 case 1).
- `test_analysis_failure_record_written_mode_does_not_trigger_mutation` (§2.4 case 2).
- `test_mutation_engine_never_writes_outside_sandbox_environment` (matches Phase 1.3 §7 gate test #5 pattern).

## §8 Out-of-Scope Deferrals

Locked here so they do not silently creep back in via implementation:

- **Per-tenant parameter overrides.** Phase 1.4 keeps a single global `production_state.parameters` per tenant. Per-tenant differentiation in promotion (e.g. `tenant_acme_corp` gets a higher `attachment_risk_floor_lift`) is Phase 1.5 / Month 6 territory.
- **A/B numeric improvement proof against the 40-case eval dataset.** The Month 5 gate test proves *effect* on one synthetic case. Numeric improvement on the full dataset is Phase 1.5 — that work needs a real LLM run, which costs API budget.
- **Operator UI for parameter inspection.** Phase 2.3 (Evidence & Reporting Layer) work.
- **Automatic rollback on regression.** The rollback primitive (`core/policy/rollback.py`) is wired and usable; Phase 1.4 does not add an *automatic* trigger. Operator-initiated rollback through the existing pipeline is sufficient for Month 5.
- **More than three new mutation kinds.** Header-inconsistency, executive-impersonation, etc. mutation kinds can be added in additive future phases via the same `MutationKind` Literal-expand pattern (Phase 1.3 §5.3 dynamic-detail discipline applies).
- **Mutating the LLM system prompt.** Out of scope by hard rule — prompt changes go through the same review path that produced the Month 2 PASS gate, not the mutation engine.
- **Mutating the `BehavioralDeviationFlag` / `PrecursorIndicator` Literals.** Out of scope by hard rule — those are schema-versioned controlled enums.

## §9 Implementation Receipt — LANDED

Implementation complete 2026-05-21 against the §11 lockdown. Files landed:

| Path | Change |
|---|---|
| `core/blackboard/models.py` | Added `MutationKind: TypeAlias = Literal[...]` (6 values per §5.1); retyped `MutationCandidate.mutation_kind` from `str` to `MutationKind` per Decision 1 |
| `core/blackboard/__init__.py` | Re-exported `MutationKind` |
| `core/production_state/parameter_keys.py` (NEW) | `RESERVED_PARAMETER_KEYS: frozenset[str]` per §3.2 |
| `core/production_state/__init__.py` | Re-exported `RESERVED_PARAMETER_KEYS` |
| `core/production_state/gate.py` | Extended `apply_signed_policy` to reject unauthorized parameter keys on both the signed `parameters` and `requested_parameters` kwarg with `GovernanceError("unauthorized parameter key: ...")` |
| `core/policy/pipeline.py` | Extended `run_policy_promotion_cycle` to write a sandbox-side `audit_verdict` REJECTED for any signed `POLICY_UPDATE` whose `parameters` contains an unauthorized key — defense in depth per Decision 2 (stops the key before it crosses the production boundary) |
| `core/mutation/engine.py` | Added `select_mutation_kind(...)` consuming Phase 1.3 typed evidence; extended `_mutation_kind` / `_mutation_parameters` to cover the three new kinds; per-cycle promotion cap (default 3); per-kind `_resolve_minimum_improvement` with matching-axis Bucket E check (Decision 4 tightening); expanded `MutationEngineConfig` per §5.2; populated `sandbox_evidence_ids` per §5.5 with cap 20 |
| `core/precursor/analysis.py` | `build_precursor_overlay(payload, *, attachment_floor_lift=0, url_obfuscation_floor_lift=0)` — pure-function additive lifts on `recommended_risk_floor` (clamp 0–100); default-zero kwargs preserve backward compat |
| `core/scoring/email_risk_scoring_agent.py` | Added `fraud_risk_floor_lift` / `attachment_risk_floor_lift` / `url_obfuscation_floor_lift` to `EmailRiskScoringConfig`; threaded through `_overlay_ransomware_precursor`; fraud lift only applies when LLM-derived `vendor_fraud_score >= 40` or `wire_transfer_anomaly_score >= 40` (never lifts safe-rated emails) |
| `core/production/loop.py` | Reads the three new parameter keys from `policy_state.parameters` on cycle entry and injects them into the scoring-agent config |
| `tests/test_phase_1_4_mutation_engine_specialization.py` (NEW) | 24 tests including all seven §7 gate tests + the Month 2 PASS-gate-protect byte-identity-at-v0 regression test + drift catchers + matching-axis tightening verification |
| `4. Product_Roadmap/Month_5_Closeout_Readiness.md` (NEW) | Month 5 closeout doc |
| `MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` | Indexed + Completed item 161 + 2026-05-21 entry |

### §9.1 Five §11 Decisions as Locked

1. **Mutation-kind enum strictness** — landed as `MutationKind: TypeAlias = Literal[...]` (6 values); `MutationCandidate.mutation_kind` retyped from `str` to `MutationKind`.
2. **`RESERVED_PARAMETER_KEYS` enforcement at BOTH boundaries** — landed at both `run_policy_promotion_cycle` (sandbox-side REJECTED audit) AND `apply_signed_policy` (`GovernanceError`). Either layer alone is sufficient; both together is the defense-in-depth Matt locked in.
3. **Production consumer wiring — all three sites** — landed in `_overlay_ransomware_precursor` (fraud lift), `build_precursor_overlay` (attachment + URL lifts), and `run_production_cycle` (parameter-load + thread into scoring-agent config). Close-the-loop §7 gate test #7 proves "next-cycle effect" end to end.
4. **`bucket_e_improvement_floor=0.05` matching-axis only** — landed via `_BUCKET_E_MATCHING_AXIS` module-level map; `fraud_pattern_threshold` only relaxes on `fake_invoice` / `vendor_update_pivot` probes; `attachment_classifier_boost` only on `malicious_attachment` probes; `url_obfuscation_sensitivity` only on `obfuscated_url` probes. Cross-axis bleed pinned out by the dedicated `test_bucket_e_floor_does_not_relax_for_cross_axis_evidence` test.
5. **`per_cycle_promotion_cap=3`** — landed as `MutationEngineConfig.per_cycle_promotion_cap` default 3; lower-ranked candidates retire with `retired_reason="cycle_promotion_cap_reached"`.

## §10 Cross-References

- Strategic: `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md` §1.4.
- Operational: `4. Product_Roadmap/12_Month_Specialization_Roadmap.md` Month 5.
- Direct predecessors:
  - `4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md` (the four fraud sub-scores Phase 1.4 lifts).
  - `4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md` (the four precursor sub-scores Phase 1.4 lifts).
  - `4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md` (the typed substrate Phase 1.4 consumes).
  - `4. Product_Roadmap/Month_4_Closeout_Readiness.md` (the conditions for starting Phase 1.4).
- Runtime grounding:
  - `core/mutation/engine.py` (existing engine surface Phase 1.4 specialises).
  - `core/policy/pipeline.py` (existing promotion pipeline Phase 1.4 reuses unchanged).
  - `core/production_state/gate.py` (existing Guardrail 11 gate Phase 1.4 extends only with the parameter-key check).
  - `core/sandbox/red_battery.py` (Phase 1.3 substrate Phase 1.4 consumes).
- Guardrails:
  - `3. SwarmCommand_Engine/Agent_Loop_Runtime/Governance_Constitution/governance-constitution-loop.md` (Guardrail 11 + Rollback).
  - `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/multi-tenant-isolation-hardening.md` (cross-tenant rejection still in force).
  - `3. SwarmCommand_Engine/Agent_Loop_Runtime/Policy_Pipeline/operator-kill-switch.md` (outermost check still in force).

## §11 Decisions — LOCKED 2026-05-21

All five decisions approved by Matt; implementation landed per §9. Matt tightened two of the recommendations (Decision 2 expanded to both layers; Decision 4 narrowed to matching-axis only).

| # | Decision | Matt's call | Tightening vs spec recommendation |
|---|---|---|---|
| 1 | Mutation-kind enum strictness | **Strict `MutationKind: Literal[...]`** with 6 values + retype `MutationCandidate.mutation_kind` from `str` | none — matches spec recommendation |
| 2 | `RESERVED_PARAMETER_KEYS` enforcement | **Enforced at BOTH promotion pipeline AND Guardrail 11 gate** | **Tightened**: spec recommended gate-only; Matt locked in defense in depth across both boundaries |
| 3 | Production consumer wiring | **Wire fraud, attachment, and URL parameter read sites now** | none — matches spec recommendation |
| 4 | Bucket E priority mechanism | **`bucket_e_improvement_floor=0.05` only for matching-axis `bucket_e_regression_probe` evidence** | **Tightened**: spec recommended any Bucket E evidence; Matt restricted to archetype-matching evidence only (no cross-axis bleed) |
| 5 | Per-cycle promotion cap | **`per_cycle_promotion_cap=3`** | none — matches spec recommendation |

## Last Updated

2026-05-21 (§11 locked; implementation landed; **419 / 419 pytest green**)
