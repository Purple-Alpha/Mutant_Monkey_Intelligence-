"""Rule Improvement governed-agent wrapper — swarm agent #67.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Rule_Improvement_Agent_Design_Contract_Deep_Dive.md`` (2026-06-24).
Reads one scoped improvement request and proposes sandbox-evaluated rule
mutation candidates via ``run_mutation_cycle`` only.

Scope / governance boundary (contract D1-D9, deliberate):
- D1 signal-in, proposal-out; one improvement request per invocation.
- D2 sandbox-only engine calls via caller-supplied ``RouteContext``.
- D3 production deploy is always a separate operator act.
- D4 every proposal carries typed sandbox evidence refs when promoted.
- D5 ``#64`` classifications are advisory input only — no auto-routing.
- D6 insufficient signal → ``INPUT_INSUFFICIENT_CANNOT_PROPOSE``.
- D7 engine retires all candidates → ``NO_CANDIDATE_SANDBOX_RETIRED``.
- D8 zero writes to production policy, scoreboard, registry, or AUTH-5.
- D9 failed proposals feed regression hardening downstream — not inline mutation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Callable, Literal

from core.blackboard import GovernanceError
from core.mutation import (
    MutationEngineConfig,
    MutationEngineItemResult,
    MutationEngineResult,
    run_mutation_cycle,
)
from core.orchestrator import RouteContext
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext

RULE_IMPROVEMENT_AGENT_ID = "rule_improvement_001"
RULE_IMPROVEMENT_LAYER = 6
RULE_IMPROVEMENT_AUTHORITY_LEVEL = 3

REFUSAL_ENVELOPE = "INPUT_INSUFFICIENT_CANNOT_PROPOSE"
NO_CANDIDATE_ENVELOPE = "NO_CANDIDATE_SANDBOX_RETIRED"
CONTROL_MAPPING = "rule_improvement:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic rule-improvement proposal only; "
    "candidates are held for operator review and are not deployed."
)

FailureSignalKind = Literal["recorded_failure", "sandbox_weakness", "operator_manual"]
ScopeKind = Literal["detection_rule", "threshold", "signal_heuristic"]
DetectionImpact = Literal["bounded_low", "bounded_medium", "bounded_high", "unknown"]
ProposalKind = Literal["success", "refusal", "no_candidate"]

ALLOWED_SCOPES: frozenset[str] = frozenset(
    {"detection_rule", "threshold", "signal_heuristic"}
)
ALLOWED_SIGNAL_KINDS: frozenset[str] = frozenset(
    {"recorded_failure", "sandbox_weakness", "operator_manual"}
)

DEPLOY_FORBIDDEN_MARKERS = (
    "deploy_mutation",
    "deploy to production",
    "auto-apply",
    "production rule store",
    "default registry",
)

RECOMMENDATION_MARKERS = (
    "recommend deploy",
    "should deploy",
    "approve for production",
    "auto-promote",
)


@dataclass(frozen=True)
class RuleImprovementRequest:
    request_id: str
    failure_signal_kind: FailureSignalKind
    failure_ref: str
    scope: ScopeKind
    tenant_scope: str
    evidence_refs: tuple[str, ...] = ()
    classification_ref: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class RuleImprovementProposal:
    proposal_id: str
    request_ref: str
    mutation_kind: str
    baseline_agent_id: str
    candidate_agent_id: str
    baseline_confidence: float
    candidate_confidence: float
    sandbox_evidence_ids: tuple[str, ...]
    engine_retired_reason: str | None
    estimated_detection_impact: DetectionImpact
    blast_radius_note: str
    rationale: str
    correction_evidence_slot: str = "reserved"


@dataclass(frozen=True)
class ProposalResult:
    kind: ProposalKind
    proposal: RuleImprovementProposal | None = None
    refusal: str | None = None
    no_candidate: str | None = None
    gaps: tuple[str, ...] = ()


MutationRunner = Callable[..., MutationEngineResult]


def validate_request(request: RuleImprovementRequest) -> tuple[str, ...]:
    gaps: list[str] = []
    if not request.request_id.strip():
        gaps.append("request_id is required")
    if not request.failure_ref.strip():
        gaps.append("failure_ref is required")
    if request.failure_signal_kind not in ALLOWED_SIGNAL_KINDS:
        gaps.append("failure_signal_kind must be a closed enum value")
    if request.scope not in ALLOWED_SCOPES:
        gaps.append("scope must be a closed enum value")
    if request.tenant_scope != "sandbox_only":
        gaps.append("tenant_scope must be sandbox_only at Evidence Stage 1")
    notes = (request.notes or "").lower()
    for marker in DEPLOY_FORBIDDEN_MARKERS:
        if marker in notes:
            gaps.append(f"notes contain forbidden deploy language: {marker}")
    return tuple(gaps)


def format_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "Improvement request lacks fields required for sandbox proposal.",
            "BOUNDARY:",
            "advisory only; no proposal emitted; no production deploy; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def format_no_candidate(request_ref: str, retired_reason: str) -> str:
    return "\n".join(
        [
            NO_CANDIDATE_ENVELOPE,
            f"request_ref: {request_ref}",
            f"engine_retired_reason: {retired_reason}",
            "WHY:",
            "Sandbox mutation cycle produced no promoted candidate.",
            "BOUNDARY:",
            "advisory only; no production deploy; no AUTH-5",
        ]
    ) + "\n"


def format_proposal(item: RuleImprovementProposal) -> str:
    evidence = ", ".join(item.sandbox_evidence_ids) if item.sandbox_evidence_ids else ""
    retired = item.engine_retired_reason if item.engine_retired_reason else "null"
    return "\n".join(
        [
            "RULE_IMPROVEMENT_PROPOSAL",
            f"proposal_id: {item.proposal_id}",
            f"request_ref: {item.request_ref}",
            f"mutation_kind: {item.mutation_kind}",
            f"baseline_agent_id: {item.baseline_agent_id}",
            f"candidate_agent_id: {item.candidate_agent_id}",
            f"baseline_confidence: {item.baseline_confidence:.4f}",
            f"candidate_confidence: {item.candidate_confidence:.4f}",
            f"sandbox_evidence_ids: [{evidence}]",
            f"engine_retired_reason: {retired}",
            f"estimated_detection_impact: {item.estimated_detection_impact}",
            f"correction_evidence_slot: {item.correction_evidence_slot}",
            f"blast_radius_note: {item.blast_radius_note}",
            f"rationale: {item.rationale}",
        ]
    )


def estimate_detection_impact(
    baseline_confidence: float, candidate_confidence: float
) -> DetectionImpact:
    improvement = candidate_confidence - baseline_confidence
    if improvement >= 0.15:
        return "bounded_high"
    if improvement >= 0.10:
        return "bounded_medium"
    if improvement > 0.0:
        return "bounded_low"
    return "unknown"


def build_rationale(request: RuleImprovementRequest, item: MutationEngineItemResult) -> str:
    candidate = item.candidate
    return (
        f"Sandbox mutation candidate {candidate.mutation_kind} for failure_ref "
        f"{request.failure_ref} with confidence delta "
        f"{candidate.baseline_confidence:.2f} -> {candidate.candidate_confidence:.2f}"
    )


def blast_radius_note_from_item(item: MutationEngineItemResult) -> str:
    if item.policy_update is None:
        return "no policy payload; sandbox candidate only"
    payload = item.policy_update.record.payload
    if not isinstance(payload, dict):
        return "policy payload present; parameter keys unavailable"
    parameters = payload.get("parameters") or {}
    if not isinstance(parameters, dict) or not parameters:
        return "promoted candidate; no typed parameter keys in payload"
    return "parameter keys: " + ", ".join(sorted(str(key) for key in parameters))


def sandbox_evidence_ids_from_item(item: MutationEngineItemResult) -> tuple[str, ...]:
    if item.policy_update is None:
        return ()
    payload = item.policy_update.record.payload
    if not isinstance(payload, dict):
        return ()
    raw_ids = payload.get("sandbox_evidence_ids") or []
    if not isinstance(raw_ids, list):
        return ()
    return tuple(str(value) for value in raw_ids)


def proposal_from_item(
    request: RuleImprovementRequest, item: MutationEngineItemResult
) -> RuleImprovementProposal:
    candidate = item.candidate
    rationale = build_rationale(request, item)
    lowered = rationale.lower()
    if any(marker in lowered for marker in RECOMMENDATION_MARKERS):
        raise GovernanceError("rationale would contain forbidden deploy language")
    return RuleImprovementProposal(
        proposal_id=f"rip_{uuid.uuid4().hex[:12]}",
        request_ref=request.request_id,
        mutation_kind=str(candidate.mutation_kind),
        baseline_agent_id=candidate.baseline_agent_id,
        candidate_agent_id=candidate.candidate_agent_id,
        baseline_confidence=candidate.baseline_confidence,
        candidate_confidence=candidate.candidate_confidence,
        sandbox_evidence_ids=sandbox_evidence_ids_from_item(item),
        engine_retired_reason=None,
        estimated_detection_impact=estimate_detection_impact(
            candidate.baseline_confidence, candidate.candidate_confidence
        ),
        blast_radius_note=blast_radius_note_from_item(item),
        rationale=rationale,
    )


def dominant_retired_reason(result: MutationEngineResult) -> str:
    reasons = [
        item.candidate.retired_reason
        for item in result.item_results
        if item.candidate.retired_reason
    ]
    if reasons:
        return reasons[0]
    if result.processed_count == 0:
        return "no_mutant_evaluations_in_sandbox"
    return "no_promoted_candidate"


def propose_improvement(
    request: RuleImprovementRequest,
    route_context: RouteContext,
    *,
    mutation_runner: MutationRunner = run_mutation_cycle,
    config: MutationEngineConfig | None = None,
) -> ProposalResult:
    gaps = validate_request(request)
    if gaps:
        return ProposalResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    engine_result = mutation_runner(route_context, config=config or MutationEngineConfig())
    promoted = [item for item in engine_result.item_results if item.candidate.promoted]
    if not promoted:
        reason = dominant_retired_reason(engine_result)
        return ProposalResult(
            kind="no_candidate",
            no_candidate=format_no_candidate(request.request_id, reason),
        )

    proposal = proposal_from_item(request, promoted[0])
    return ProposalResult(kind="success", proposal=proposal)


class RuleImprovementAgent:
    """Governed Layer 6 proposer — improvement request in, sandbox proposal out."""

    __test__ = False

    agent_id: str = RULE_IMPROVEMENT_AGENT_ID
    layer: int = RULE_IMPROVEMENT_LAYER
    authority_level: int = RULE_IMPROVEMENT_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        improvement_request: RuleImprovementRequest | None = None,
        route_context: RouteContext | None = None,
        mutation_runner: MutationRunner = run_mutation_cycle,
        config: MutationEngineConfig | None = None,
    ) -> None:
        self._improvement_request = improvement_request
        self._route_context = route_context
        self._mutation_runner = mutation_runner
        self._config = config

    def propose(
        self,
        improvement_request: RuleImprovementRequest | None = None,
        route_context: RouteContext | None = None,
    ) -> ProposalResult:
        request = improvement_request or self._improvement_request
        context = route_context or self._route_context
        if request is None:
            gaps = ("improvement_request is required",)
            return ProposalResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        if context is None:
            gaps = ("route_context is required",)
            return ProposalResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        return propose_improvement(
            request,
            context,
            mutation_runner=self._mutation_runner,
            config=self._config,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.propose()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        if result.kind == "no_candidate":
            raise GovernanceError(result.no_candidate or NO_CANDIDATE_ENVELOPE)
        item = result.proposal
        assert item is not None
        facts = (
            f"rule_improvement_proposal:{item.proposal_id} "
            f"mutation_kind={item.mutation_kind} request_ref={item.request_ref}"
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=(facts,),
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None


__all__ = [
    "NO_CANDIDATE_ENVELOPE",
    "ProposalResult",
    "REFUSAL_ENVELOPE",
    "RULE_IMPROVEMENT_AGENT_ID",
    "RuleImprovementAgent",
    "RuleImprovementProposal",
    "RuleImprovementRequest",
    "dominant_retired_reason",
    "estimate_detection_impact",
    "format_no_candidate",
    "format_proposal",
    "format_refusal",
    "propose_improvement",
    "proposal_from_item",
    "validate_request",
]
