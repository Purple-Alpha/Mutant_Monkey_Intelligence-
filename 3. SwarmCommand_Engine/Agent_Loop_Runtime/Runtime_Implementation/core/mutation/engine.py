"""Sandbox-only mutation engine.

Month 0 baseline: the engine consumes mutant evaluations, creates
controlled defensive candidates, and emits signed policy update
candidates only when promotion rules pass. It never writes to production.

Month 5 (Phase 1.4 Mutation Engine Specialisation) extends this with:

* ``MutationKind`` typed Literal (six values per §5.1 of the Phase 1.4
  deep dive, locked by Matt's 2026-05-21 §11 decision 1).
* Fraud-specialised mutation kinds selected from Phase 1.3 typed
  ``Phase13FailureDetail`` evidence (``fraud_pattern_threshold``,
  ``attachment_classifier_boost``, ``url_obfuscation_sensitivity``).
* Per-kind ``minimum_improvement`` resolution with the matching-axis
  Bucket E relaxation per §11 decision 4.
* Per-cycle promotion cap (default 3) per §11 decision 5.
* Typed evidence chain (per-profile WEAKNESS_REPORT + top-N
  per-case MUTANT_EVALUATION + matching Bucket E synthetic-case ids)
  capped at ``MAX_EVIDENCE_IDS_PER_PROMOTION`` (20).

Legacy ``run_mutation_cycle`` callers that submit mutant evaluations
without a populated ``phase_1_3_failure_details`` list still take the
Month 0 path; the new logic only activates per Red-profile group when
typed failure details are present.

See ``4. Product_Roadmap/Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md``.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, get_args
from uuid import UUID

from core.blackboard import (
    BlackboardRecord,
    Environment,
    MutantEvaluationPayload,
    MutationKind,
    Phase13CaseArchetype,
    Phase13FailureDetail,
    Phase13FailureMode,
    PolicyUpdatePayload,
    RecordType,
    SyntheticEmailAttackCasePayload,
    WeaknessReportPayload,
    read_records,
)
from core.orchestrator import RouteContext, RouteResult, submit_policy_update
from core.orchestrator.routes import blackboard_path
from core.policy.signing import SigningKey, default_signing_key, sign


# Phase 1.4 §2.3 / §5.3 — matching-axis Bucket E table. A
# ``bucket_e_regression_probe`` case relaxes the improvement floor for
# a mutation kind only when the probe's archetype matches the axis the
# kind tunes. Cross-axis bleed is intentionally forbidden per Matt's
# §11 decision 4 tightening.
_BUCKET_E_MATCHING_AXIS: dict[MutationKind, frozenset[Phase13CaseArchetype]] = {
    "fraud_pattern_threshold": frozenset({"fake_invoice", "vendor_update_pivot"}),
    "attachment_classifier_boost": frozenset({"malicious_attachment"}),
    "url_obfuscation_sensitivity": frozenset({"obfuscated_url"}),
}

# Phase 1.4 §5.6 — evidence cap. Per-profile weakness report plus the
# top-N failed evals plus any matching Bucket E case ids must fit
# inside this bound. Keeps the production blackboard small even if a
# runaway Red battery emits hundreds of failed evals per profile.
MAX_EVIDENCE_IDS_PER_PROMOTION = 20


@dataclass(frozen=True)
class MutationEngineConfig:
    sandbox_tenant_id: str = "sandbox_default"
    governance_agent_id: str = "governance_001"
    minimum_improvement: float = 0.10
    promoted_confidence_cap: float = 0.95
    signing_key: SigningKey | None = None
    # Production tenant this sandbox cycle is producing signed policy
    # updates for. Embedded as ``target_production_tenant_id`` in the
    # signed payload so the promotion pipeline and Guardrail 11 gate can
    # reject cross-tenant promotions. Defaults to ``"tenant_demo"`` to
    # match the long-standing demo pair.
    production_tenant_id: str = "tenant_demo"
    # -- Phase 1.4 additions (additive; all default-on) ----------------
    enable_phase_1_4_mutation_kinds: bool = True
    bucket_e_improvement_floor: float = 0.05
    per_cycle_promotion_cap: int = 3
    fraud_pattern_dominance_threshold: float = 0.30
    precursor_dominance_threshold: float = 0.20


@dataclass(frozen=True)
class MutationCandidate:
    candidate_agent_id: str
    baseline_agent_id: str
    source_evaluation_id: str
    mutation_kind: MutationKind
    baseline_confidence: float
    candidate_confidence: float
    promoted: bool
    retired_reason: str | None = None


@dataclass(frozen=True)
class MutationEngineItemResult:
    evaluation_record_id: str
    candidate: MutationCandidate
    policy_update: RouteResult | None


@dataclass(frozen=True)
class MutationEngineResult:
    processed_count: int
    promoted_count: int
    retired_count: int
    item_results: list[MutationEngineItemResult]


# ---------------------------------------------------------------------------
# Loaders (sandbox-only reads)
# ---------------------------------------------------------------------------


def _load_sandbox_records(
    context: RouteContext, config: MutationEngineConfig
) -> list[BlackboardRecord]:
    path = blackboard_path(
        context.blackboard_root,
        Environment.SANDBOX,
        config.sandbox_tenant_id,
    )
    return read_records(path)


@dataclass(frozen=True)
class _Phase14CaseMeta:
    archetype: Phase13CaseArchetype
    red_profile_id: str
    is_bucket_e_probe: bool


def _index_synthetic_cases(
    records: Iterable[BlackboardRecord],
) -> dict[UUID, _Phase14CaseMeta]:
    """Build a ``case_record_id -> (archetype, red_profile_id, is_bucket_e_probe)`` map.

    The mutation engine needs the archetype + Red profile of every case
    that a Phase 1.3 mutant evaluation references in order to group the
    evals by Red profile and to enforce the matching-axis Bucket E
    relaxation. Cases that fail to parse are skipped silently rather
    than aborting the cycle so a single corrupt record cannot break
    promotion for the whole battery.
    """

    out: dict[UUID, _Phase14CaseMeta] = {}
    for record in records:
        if record.record_type != RecordType.SYNTHETIC_EMAIL_ATTACK_CASE:
            continue
        try:
            payload = SyntheticEmailAttackCasePayload.model_validate(record.payload)
        except Exception:
            continue
        out[record.record_id] = _Phase14CaseMeta(
            archetype=payload.archetype,
            red_profile_id=payload.red_profile_id,
            is_bucket_e_probe="bucket_e_regression_probe" in payload.case_tags,
        )
    return out


def _index_weakness_reports_by_profile(
    records: Iterable[BlackboardRecord],
) -> dict[str, UUID]:
    """Return the latest ``WEAKNESS_REPORT`` record id per Phase 1.3 Red profile.

    Phase 1.3 writes one weakness report per Red profile per battery
    cycle with ``weakness_kind=f"phase_1_3_red_profile:{red_profile_id}"``.
    The latest one wins so reruns get the most recent aggregate.
    Reports from older (Month 0) sandbox loop runs are ignored — they
    do not carry a Phase 1.3 prefix.
    """

    out: dict[str, BlackboardRecord] = {}
    for record in records:
        if record.record_type != RecordType.WEAKNESS_REPORT:
            continue
        try:
            payload = WeaknessReportPayload.model_validate(record.payload)
        except Exception:
            continue
        prefix = "phase_1_3_red_profile:"
        if not payload.weakness_kind.startswith(prefix):
            continue
        profile_id = payload.weakness_kind[len(prefix) :]
        existing = out.get(profile_id)
        if existing is None or record.created_at > existing.created_at:
            out[profile_id] = record
    return {pid: rec.record_id for pid, rec in out.items()}


# ---------------------------------------------------------------------------
# Legacy (Month 0) candidate construction — unchanged shape, only the
# ``mutation_kind`` field type narrowed from ``str`` to ``MutationKind``.
# ---------------------------------------------------------------------------


def _legacy_mutation_kind(failure_modes: list[str]) -> MutationKind:
    if any(mode.startswith("missing_signal:") for mode in failure_modes):
        return "add_missing_signal_heuristic"
    if "confidence_below_threshold" in failure_modes:
        return "raise_confidence_weighting"
    return "no_mutation"


def _legacy_candidate_confidence(
    evaluation: MutantEvaluationPayload, mutation_kind: MutationKind
) -> float:
    if mutation_kind == "add_missing_signal_heuristic":
        improvement = 0.18
    elif mutation_kind == "raise_confidence_weighting":
        improvement = 0.12
    else:
        improvement = 0.0
    return min(evaluation.baseline_confidence + improvement, 0.95)


def _create_legacy_candidate(
    evaluation: MutantEvaluationPayload,
    evaluation_record_id: str,
    config: MutationEngineConfig,
) -> MutationCandidate:
    mutation_kind = _legacy_mutation_kind(evaluation.failure_modes)
    candidate_confidence = _legacy_candidate_confidence(evaluation, mutation_kind)
    improvement = candidate_confidence - evaluation.baseline_confidence

    if not evaluation.mutation_recommended:
        return MutationCandidate(
            candidate_agent_id=f"{evaluation.baseline_agent_id}__retired_no_mutation_needed",
            baseline_agent_id=evaluation.baseline_agent_id,
            source_evaluation_id=evaluation_record_id,
            mutation_kind="no_mutation",
            baseline_confidence=evaluation.baseline_confidence,
            candidate_confidence=evaluation.baseline_confidence,
            promoted=False,
            retired_reason="mutation_not_recommended",
        )

    if mutation_kind == "no_mutation":
        return MutationCandidate(
            candidate_agent_id=f"{evaluation.baseline_agent_id}__retired_no_failure_mode",
            baseline_agent_id=evaluation.baseline_agent_id,
            source_evaluation_id=evaluation_record_id,
            mutation_kind=mutation_kind,
            baseline_confidence=evaluation.baseline_confidence,
            candidate_confidence=candidate_confidence,
            promoted=False,
            retired_reason="no_supported_failure_mode",
        )

    if improvement < config.minimum_improvement:
        return MutationCandidate(
            candidate_agent_id=f"{evaluation.baseline_agent_id}__retired_low_improvement",
            baseline_agent_id=evaluation.baseline_agent_id,
            source_evaluation_id=evaluation_record_id,
            mutation_kind=mutation_kind,
            baseline_confidence=evaluation.baseline_confidence,
            candidate_confidence=candidate_confidence,
            promoted=False,
            retired_reason="candidate_did_not_clear_improvement_threshold",
        )

    return MutationCandidate(
        candidate_agent_id=f"{evaluation.baseline_agent_id}__candidate_{mutation_kind}",
        baseline_agent_id=evaluation.baseline_agent_id,
        source_evaluation_id=evaluation_record_id,
        mutation_kind=mutation_kind,
        baseline_confidence=evaluation.baseline_confidence,
        candidate_confidence=candidate_confidence,
        promoted=True,
    )


def _legacy_mutation_parameters(candidate: MutationCandidate) -> dict[str, float]:
    """Translate a legacy mutation kind into concrete detection parameters.

    Month 0 contract: the only key written is ``confidence_boost``, which
    is in ``RESERVED_PARAMETER_KEYS`` so the new gate-side and
    pipeline-side reservation checks still accept it. The Phase 1.4
    kinds write their own typed keys via ``_phase14_mutation_parameters``.
    """

    improvement = max(0.0, candidate.candidate_confidence - candidate.baseline_confidence)
    if candidate.mutation_kind == "add_missing_signal_heuristic":
        return {"confidence_boost": round(improvement, 4)}
    if candidate.mutation_kind == "raise_confidence_weighting":
        return {"confidence_boost": round(improvement, 4)}
    return {}


# ---------------------------------------------------------------------------
# Phase 1.4 selection + candidate construction
# ---------------------------------------------------------------------------


def select_mutation_kind(
    *,
    archetype: Phase13CaseArchetype,
    failure_mode_counter: Counter[Phase13FailureMode],
    total_failures: int,
    fraud_pattern_dominance_threshold: float = 0.30,
    precursor_dominance_threshold: float = 0.20,
) -> MutationKind | None:
    """Map (archetype, dominant failure mode) -> MutationKind per §2.2.

    Pure function. Returns ``None`` when no dominant pattern is found or
    when the dominant pattern is one of the §2.4 hard non-selection
    modes (``unexpected_blue_exception``, ``analysis_failure_record_written``,
    ``precursor_block_missing`` — operator escalation only, never a
    parameter mutation).

    The thresholds are passed in so the engine config can tune them
    without touching this function.
    """

    if total_failures <= 0:
        return None

    # §2.4 hard non-selection: if the dominant mode is one of these,
    # don't try to mutate — operator escalation territory.
    forbidden_dominant_modes: frozenset[Phase13FailureMode] = frozenset(
        {
            "unexpected_blue_exception",
            "analysis_failure_record_written",
            "precursor_block_missing",
        }
    )

    def rate(mode: Phase13FailureMode) -> float:
        return failure_mode_counter.get(mode, 0) / total_failures

    # Reject if any forbidden mode is the strict majority.
    for forbidden in forbidden_dominant_modes:
        if rate(forbidden) > 0.50:
            return None

    if archetype == "fake_invoice":
        if rate("risk_score_below_floor") >= fraud_pattern_dominance_threshold:
            return "fraud_pattern_threshold"
        return None

    if archetype == "vendor_update_pivot":
        combined = rate("risk_score_below_floor") + rate("missing_behavioral_flag")
        if combined >= fraud_pattern_dominance_threshold:
            return "fraud_pattern_threshold"
        return None

    if archetype == "malicious_attachment":
        if rate("missing_precursor_indicator") >= precursor_dominance_threshold:
            return "attachment_classifier_boost"
        return None

    if archetype == "obfuscated_url":
        if rate("missing_precursor_indicator") >= precursor_dominance_threshold:
            return "url_obfuscation_sensitivity"
        return None

    return None


@dataclass(frozen=True)
class _Phase14ProfileGroup:
    """All MUTANT_EVAL records for one Red profile in one cycle."""

    red_profile_id: str
    archetype: Phase13CaseArchetype
    eval_records: list[BlackboardRecord] = field(default_factory=list)
    failed_eval_records: list[BlackboardRecord] = field(default_factory=list)
    failure_mode_counter: Counter[Phase13FailureMode] = field(default_factory=Counter)
    total_failures: int = 0
    average_baseline_confidence: float = 0.0
    bucket_e_archetypes_in_evidence: frozenset[Phase13CaseArchetype] = frozenset()
    bucket_e_case_ids: tuple[UUID, ...] = ()
    weakness_report_id: UUID | None = None


def _phase14_floor_lift_for(kind: MutationKind, dominant_rate: float) -> int:
    """Translate a dominance rate (0.0–1.0) into the 0–25 integer lift.

    Linear scale; clamped to [1, 25] when a mutation kind is being
    written so the operator always sees a non-zero lift in the signed
    payload. ``v0`` defaults remain 0 because the engine only writes
    this key when a candidate is actually being promoted.
    """

    if kind not in {
        "fraud_pattern_threshold",
        "attachment_classifier_boost",
        "url_obfuscation_sensitivity",
    }:
        return 0
    raw = round(dominant_rate * 25.0)
    return max(1, min(25, int(raw)))


def _phase14_dominant_rate(
    kind: MutationKind,
    counter: Counter[Phase13FailureMode],
    total_failures: int,
) -> float:
    """Per-kind dominance rate used for both lift sizing and improvement math.

    For ``fraud_pattern_threshold`` we sum ``risk_score_below_floor`` and
    ``missing_behavioral_flag`` because both are first-class signals that
    Blue's vendor-fraud detection is undersized. The sum is bounded by 1.0
    because ``total_failures == sum(counter.values())``. For the two
    precursor-axis kinds we use the per-axis ``missing_precursor_indicator``
    rate directly (the selector already enforced the 20% threshold).
    """

    if total_failures <= 0:
        return 0.0
    if kind == "fraud_pattern_threshold":
        return (
            counter.get("risk_score_below_floor", 0)
            + counter.get("missing_behavioral_flag", 0)
        ) / total_failures
    if kind in {"attachment_classifier_boost", "url_obfuscation_sensitivity"}:
        return counter.get("missing_precursor_indicator", 0) / total_failures
    return 0.0


def _phase14_mutation_parameters(
    kind: MutationKind, dominant_rate: float
) -> dict[str, int]:
    lift = _phase14_floor_lift_for(kind, dominant_rate)
    if kind == "fraud_pattern_threshold":
        return {"fraud_risk_floor_lift": lift}
    if kind == "attachment_classifier_boost":
        return {"attachment_risk_floor_lift": lift}
    if kind == "url_obfuscation_sensitivity":
        return {"url_obfuscation_floor_lift": lift}
    return {}


def _resolve_minimum_improvement(
    config: MutationEngineConfig,
    *,
    mutation_kind: MutationKind,
    bucket_e_archetypes_in_evidence: frozenset[Phase13CaseArchetype],
) -> float:
    """Bucket E matching-axis floor relaxation per §5.3.

    The relaxed floor (default 0.05) only applies when the mutation
    kind's matching-axis set intersects the archetypes of Bucket E
    probes actually present in this group's evidence chain. Cross-axis
    Bucket E evidence (e.g. a fake_invoice probe under an
    attachment_classifier_boost candidate) does NOT relax the floor.
    """

    matching = _BUCKET_E_MATCHING_AXIS.get(mutation_kind, frozenset())
    if matching & bucket_e_archetypes_in_evidence:
        return min(config.minimum_improvement, config.bucket_e_improvement_floor)
    return config.minimum_improvement


def _build_evidence_chain(
    *,
    group: _Phase14ProfileGroup,
    cap: int = MAX_EVIDENCE_IDS_PER_PROMOTION,
) -> list[UUID]:
    """Build the typed evidence chain per §5.5.

    Order: weakness report id, then top-(cap-1-N_bucket_e) failed
    per-case eval ids ranked by ascending baseline_confidence (worst
    Blue performance first), then any matching Bucket E probe case ids.
    Total length is capped at ``cap`` per §5.6.
    """

    chain: list[UUID] = []
    if group.weakness_report_id is not None:
        chain.append(group.weakness_report_id)

    remaining = cap - len(chain) - len(group.bucket_e_case_ids)
    if remaining < 0:
        remaining = 0

    failed_sorted = sorted(
        group.failed_eval_records,
        key=lambda r: (
            float(r.payload.get("baseline_confidence", 1.0)),
            str(r.record_id),
        ),
    )
    for record in failed_sorted[:remaining]:
        chain.append(record.record_id)

    for case_id in group.bucket_e_case_ids:
        if len(chain) >= cap:
            break
        chain.append(case_id)

    return chain


def _create_phase14_candidate(
    *,
    group: _Phase14ProfileGroup,
    config: MutationEngineConfig,
) -> MutationCandidate:
    """Translate one Red profile's typed failure aggregate into a candidate.

    Returns a retired candidate when:
    - the group has no failures (``no_failures_in_profile_group``)
    - ``select_mutation_kind`` returns None (``no_dominant_pattern``)
    - the per-kind improvement floor (with matching-axis Bucket E
      relaxation) is not cleared (``candidate_did_not_clear_improvement_threshold``)
    """

    baseline_id = f"phase_1_3_blue_via:{group.red_profile_id}"
    source_eval_id = (
        str(group.eval_records[0].record_id)
        if group.eval_records
        else f"phase_1_4:no_evals:{group.red_profile_id}"
    )

    if group.total_failures <= 0:
        return MutationCandidate(
            candidate_agent_id=f"{baseline_id}__retired_no_failures",
            baseline_agent_id=baseline_id,
            source_evaluation_id=source_eval_id,
            mutation_kind="no_mutation",
            baseline_confidence=group.average_baseline_confidence,
            candidate_confidence=group.average_baseline_confidence,
            promoted=False,
            retired_reason="no_failures_in_profile_group",
        )

    kind = select_mutation_kind(
        archetype=group.archetype,
        failure_mode_counter=group.failure_mode_counter,
        total_failures=group.total_failures,
        fraud_pattern_dominance_threshold=config.fraud_pattern_dominance_threshold,
        precursor_dominance_threshold=config.precursor_dominance_threshold,
    )
    if kind is None:
        return MutationCandidate(
            candidate_agent_id=f"{baseline_id}__retired_no_dominant_pattern",
            baseline_agent_id=baseline_id,
            source_evaluation_id=source_eval_id,
            mutation_kind="no_mutation",
            baseline_confidence=group.average_baseline_confidence,
            candidate_confidence=group.average_baseline_confidence,
            promoted=False,
            retired_reason="no_dominant_pattern",
        )

    dominant_rate = _phase14_dominant_rate(
        kind, group.failure_mode_counter, group.total_failures
    )
    improvement = round(dominant_rate * 0.5, 4)
    candidate_confidence = min(
        group.average_baseline_confidence + improvement,
        config.promoted_confidence_cap,
    )
    actual_improvement = candidate_confidence - group.average_baseline_confidence

    floor = _resolve_minimum_improvement(
        config,
        mutation_kind=kind,
        bucket_e_archetypes_in_evidence=group.bucket_e_archetypes_in_evidence,
    )
    if actual_improvement < floor:
        return MutationCandidate(
            candidate_agent_id=f"{baseline_id}__retired_low_improvement",
            baseline_agent_id=baseline_id,
            source_evaluation_id=source_eval_id,
            mutation_kind=kind,
            baseline_confidence=group.average_baseline_confidence,
            candidate_confidence=candidate_confidence,
            promoted=False,
            retired_reason="candidate_did_not_clear_improvement_threshold",
        )

    return MutationCandidate(
        candidate_agent_id=f"{baseline_id}__candidate_{kind}",
        baseline_agent_id=baseline_id,
        source_evaluation_id=source_eval_id,
        mutation_kind=kind,
        baseline_confidence=group.average_baseline_confidence,
        candidate_confidence=candidate_confidence,
        promoted=True,
    )


# ---------------------------------------------------------------------------
# Payload + cycle
# ---------------------------------------------------------------------------


def _policy_payload(
    *,
    candidate: MutationCandidate,
    production_tenant_id: str,
    parameters: dict[str, float | int],
    evidence_ids: list[UUID],
) -> PolicyUpdatePayload:
    return PolicyUpdatePayload(
        policy_name=f"{candidate.baseline_agent_id}:{candidate.mutation_kind}",
        change_summary=(
            "Promote sandbox defensive mutation "
            f"{candidate.candidate_agent_id} for {candidate.mutation_kind}. "
            f"Baseline confidence {candidate.baseline_confidence:.2f}; "
            f"candidate confidence {candidate.candidate_confidence:.2f}."
        ),
        sandbox_evidence_ids=evidence_ids,
        rollout_scope="manual_review",
        rollback_plan=(
            "Revert to previous baseline agent configuration and disable "
            f"{candidate.candidate_agent_id}."
        ),
        parameters=dict(parameters),
        target_production_tenant_id=production_tenant_id,
    )


def _classify_evals(
    *,
    eval_records: list[BlackboardRecord],
    case_index: dict[UUID, _Phase14CaseMeta],
    weakness_report_by_profile: dict[str, UUID],
) -> tuple[list[BlackboardRecord], dict[str, _Phase14ProfileGroup]]:
    """Split evals into (legacy, phase14_groups_by_red_profile_id).

    A mutant evaluation is treated as Phase 1.4 substrate iff
    ``phase_1_3_failure_details`` is non-empty AND its
    ``source_attack_case_id`` resolves to an indexed synthetic email
    attack case. Everything else falls back to the Month 0 legacy
    path so existing sandbox-loop callers stay unchanged.
    """

    legacy: list[BlackboardRecord] = []
    groups: dict[str, _Phase14ProfileGroup] = {}
    confidence_sums: dict[str, float] = defaultdict(float)
    confidence_counts: dict[str, int] = defaultdict(int)
    bucket_e_axes: dict[str, set[Phase13CaseArchetype]] = defaultdict(set)
    bucket_e_case_ids: dict[str, list[UUID]] = defaultdict(list)

    for record in eval_records:
        try:
            payload = MutantEvaluationPayload.model_validate(record.payload)
        except Exception:
            legacy.append(record)
            continue
        if not payload.phase_1_3_failure_details:
            legacy.append(record)
            continue

        case_meta = case_index.get(payload.source_attack_case_id)
        if case_meta is None:
            legacy.append(record)
            continue

        profile_id = case_meta.red_profile_id
        group = groups.get(profile_id)
        if group is None:
            group = _Phase14ProfileGroup(
                red_profile_id=profile_id,
                archetype=case_meta.archetype,
            )
            groups[profile_id] = group

        group.eval_records.append(record)
        confidence_sums[profile_id] += payload.baseline_confidence
        confidence_counts[profile_id] += 1

        if payload.phase_1_3_failure_details:
            group.failed_eval_records.append(record)
            for detail in payload.phase_1_3_failure_details:
                group.failure_mode_counter[detail.failure_mode] += 1

        if case_meta.is_bucket_e_probe:
            bucket_e_axes[profile_id].add(case_meta.archetype)
            bucket_e_case_ids[profile_id].append(payload.source_attack_case_id)

    finalized: dict[str, _Phase14ProfileGroup] = {}
    for profile_id, group in groups.items():
        count = confidence_counts[profile_id]
        avg_conf = (
            confidence_sums[profile_id] / count if count > 0 else 0.0
        )
        finalized[profile_id] = _Phase14ProfileGroup(
            red_profile_id=group.red_profile_id,
            archetype=group.archetype,
            eval_records=group.eval_records,
            failed_eval_records=group.failed_eval_records,
            failure_mode_counter=group.failure_mode_counter,
            total_failures=sum(group.failure_mode_counter.values()),
            average_baseline_confidence=avg_conf,
            bucket_e_archetypes_in_evidence=frozenset(bucket_e_axes[profile_id]),
            bucket_e_case_ids=tuple(bucket_e_case_ids[profile_id]),
            weakness_report_id=weakness_report_by_profile.get(profile_id),
        )
    return legacy, finalized


def _apply_per_cycle_cap(
    items: list[MutationEngineItemResult],
    *,
    cap: int,
) -> list[MutationEngineItemResult]:
    """Sort promoted items by improvement DESC; demote overflow to retired.

    Retired items keep their original ``MutationCandidate`` but with a
    ``cycle_promotion_cap_reached`` ``retired_reason``. The promoted
    items are returned in original (input) order to keep test
    determinism; only the *set* of promoted items is changed by the cap.
    """

    if cap < 0:
        cap = 0

    promoted_with_index = [
        (idx, item)
        for idx, item in enumerate(items)
        if item.candidate.promoted
    ]
    if len(promoted_with_index) <= cap:
        return items

    def improvement(item: MutationEngineItemResult) -> float:
        return item.candidate.candidate_confidence - item.candidate.baseline_confidence

    ranked = sorted(
        promoted_with_index,
        key=lambda pair: (-improvement(pair[1]), pair[0]),
    )
    keep_indices = {idx for idx, _ in ranked[:cap]}

    out: list[MutationEngineItemResult] = []
    for idx, item in enumerate(items):
        if not item.candidate.promoted or idx in keep_indices:
            out.append(item)
            continue
        demoted = MutationCandidate(
            candidate_agent_id=item.candidate.candidate_agent_id,
            baseline_agent_id=item.candidate.baseline_agent_id,
            source_evaluation_id=item.candidate.source_evaluation_id,
            mutation_kind=item.candidate.mutation_kind,
            baseline_confidence=item.candidate.baseline_confidence,
            candidate_confidence=item.candidate.candidate_confidence,
            promoted=False,
            retired_reason="cycle_promotion_cap_reached",
        )
        out.append(
            MutationEngineItemResult(
                evaluation_record_id=item.evaluation_record_id,
                candidate=demoted,
                policy_update=None,
            )
        )
    return out


def run_mutation_cycle(
    context: RouteContext,
    *,
    config: MutationEngineConfig | None = None,
) -> MutationEngineResult:
    """Run one sandbox-only mutation cycle over current mutant evaluations.

    Legacy Month 0 evaluations (no ``phase_1_3_failure_details``) take
    the original per-eval candidate path. Phase 1.3 evaluations (with
    typed failure details) are grouped per Red profile and pass through
    the Phase 1.4 selector / improvement-floor / per-cycle-cap pipeline.
    Both populations contribute to the same per-cycle cap so the
    operator review surface stays bounded across mixed workloads.
    """

    config = config or MutationEngineConfig()
    records = _load_sandbox_records(context, config)
    eval_records = [
        record for record in records if record.record_type == RecordType.MUTANT_EVALUATION
    ]

    case_index = _index_synthetic_cases(records)
    weakness_report_by_profile = _index_weakness_reports_by_profile(records)

    legacy_evals, phase14_groups = _classify_evals(
        eval_records=eval_records,
        case_index=case_index,
        weakness_report_by_profile=weakness_report_by_profile,
    )

    legacy_items = _build_legacy_items(legacy_evals, config)
    phase14_items: list[MutationEngineItemResult] = []
    if config.enable_phase_1_4_mutation_kinds:
        for profile_id in sorted(phase14_groups.keys()):
            group = phase14_groups[profile_id]
            phase14_items.append(_build_phase14_item(group, config))

    items_before_cap = legacy_items + phase14_items
    items = _apply_per_cycle_cap(
        items_before_cap, cap=config.per_cycle_promotion_cap
    )

    signing_key = config.signing_key or default_signing_key()
    final_items: list[MutationEngineItemResult] = []
    for item in items:
        if not item.candidate.promoted:
            final_items.append(item)
            continue

        eval_record = _find_record(eval_records, item.evaluation_record_id)
        if item.candidate.mutation_kind in {
            "fraud_pattern_threshold",
            "attachment_classifier_boost",
            "url_obfuscation_sensitivity",
        }:
            group = phase14_groups[_red_profile_for_item(item, phase14_groups)]
            dominant_rate = _phase14_dominant_rate(
                item.candidate.mutation_kind,
                group.failure_mode_counter,
                group.total_failures,
            )
            parameters: dict[str, float | int] = dict(
                _phase14_mutation_parameters(
                    item.candidate.mutation_kind, dominant_rate
                )
            )
            evidence_ids = _build_evidence_chain(group=group)
        else:
            parameters = dict(_legacy_mutation_parameters(item.candidate))
            evidence_ids = []

        policy_payload = _policy_payload(
            candidate=item.candidate,
            production_tenant_id=config.production_tenant_id,
            parameters=parameters,
            evidence_ids=evidence_ids,
        )
        signature_id = sign(
            policy_payload.model_dump(mode="json"),
            config.governance_agent_id,
            signing_key,
        )
        parent_record_id = (
            eval_record.record_id if eval_record is not None else None
        )
        policy_update = submit_policy_update(
            context,
            source_agent=config.governance_agent_id,
            sandbox_tenant_id=config.sandbox_tenant_id,
            parent_record_id=parent_record_id,
            signature_id=signature_id,
            payload=policy_payload,
        )
        final_items.append(
            MutationEngineItemResult(
                evaluation_record_id=item.evaluation_record_id,
                candidate=item.candidate,
                policy_update=policy_update,
            )
        )

    promoted_count = sum(1 for item in final_items if item.candidate.promoted)
    return MutationEngineResult(
        processed_count=len(final_items),
        promoted_count=promoted_count,
        retired_count=len(final_items) - promoted_count,
        item_results=final_items,
    )


def _find_record(
    eval_records: list[BlackboardRecord], evaluation_record_id: str
) -> BlackboardRecord | None:
    for record in eval_records:
        if str(record.record_id) == evaluation_record_id:
            return record
    return None


def _red_profile_for_item(
    item: MutationEngineItemResult,
    phase14_groups: dict[str, _Phase14ProfileGroup],
) -> str:
    """Resolve the Phase 1.4 profile id from a candidate's baseline_agent_id.

    Phase 1.4 candidates are constructed with
    ``baseline_agent_id = f"phase_1_3_blue_via:{red_profile_id}"``; we
    reverse that here so the cycle can look up the candidate's group
    without threading the id through the result type.
    """

    prefix = "phase_1_3_blue_via:"
    baseline = item.candidate.baseline_agent_id
    if baseline.startswith(prefix):
        candidate_profile = baseline[len(prefix) :]
        if candidate_profile in phase14_groups:
            return candidate_profile
    raise KeyError(
        f"phase 1.4 candidate {item.candidate.candidate_agent_id} could not "
        f"be matched to a profile group"
    )


def _build_legacy_items(
    legacy_evals: list[BlackboardRecord],
    config: MutationEngineConfig,
) -> list[MutationEngineItemResult]:
    items: list[MutationEngineItemResult] = []
    for record in legacy_evals:
        try:
            evaluation = MutantEvaluationPayload.model_validate(record.payload)
        except Exception:
            continue
        candidate = _create_legacy_candidate(
            evaluation, str(record.record_id), config
        )
        items.append(
            MutationEngineItemResult(
                evaluation_record_id=str(record.record_id),
                candidate=candidate,
                policy_update=None,
            )
        )
    return items


def _build_phase14_item(
    group: _Phase14ProfileGroup,
    config: MutationEngineConfig,
) -> MutationEngineItemResult:
    candidate = _create_phase14_candidate(group=group, config=config)
    primary_eval_id = (
        str(group.eval_records[0].record_id) if group.eval_records else ""
    )
    return MutationEngineItemResult(
        evaluation_record_id=primary_eval_id,
        candidate=candidate,
        policy_update=None,
    )


__all__ = [
    "MAX_EVIDENCE_IDS_PER_PROMOTION",
    "MutationCandidate",
    "MutationEngineConfig",
    "MutationEngineItemResult",
    "MutationEngineResult",
    "run_mutation_cycle",
    "select_mutation_kind",
]


# Drift catcher: keep the engine's matching-axis table consistent with the
# closed ``MutationKind`` Literal. If a new Phase 1.4 kind is added, this
# assertion fires at import time and forces the developer to register the
# matching archetypes (or explicitly exclude the kind from the table).
_PHASE_1_4_KINDS_REGISTERED = frozenset(_BUCKET_E_MATCHING_AXIS.keys())
_PHASE_1_4_KINDS_KNOWN = frozenset(
    {
        "fraud_pattern_threshold",
        "attachment_classifier_boost",
        "url_obfuscation_sensitivity",
    }
)
assert _PHASE_1_4_KINDS_REGISTERED == _PHASE_1_4_KINDS_KNOWN, (
    "Phase 1.4 matching-axis table is out of sync with the implemented "
    "Phase 1.4 MutationKind values. Update _BUCKET_E_MATCHING_AXIS."
)
_MUTATION_KIND_VALUES = frozenset(get_args(MutationKind))
assert _PHASE_1_4_KINDS_REGISTERED <= _MUTATION_KIND_VALUES, (
    "Phase 1.4 matching-axis table references an unknown MutationKind. "
    "Update core.blackboard.MutationKind."
)
