"""Correction Evidence governed-agent wrapper — swarm agent #65.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Correction_Evidence_Agent_Design_Contract_Deep_Dive.md`` (2026-06-24).
Reads one scoped correction validation request and validates four proof bars
(fix, no-regression, blast-radius, reproducibility) inside sandbox-only
evaluation. Emits ``CORRECTION_EVIDENCE_PACKET`` or explicit insufficient
outcomes only.

Scope / governance boundary (contract D1-D9, deliberate):
- D1 request-in, evidence-packet-out; one validation request per invocation.
- D2 sandbox-only evaluation via caller-supplied ``RouteContext``.
- D3 detect-not-enact: verdict surfaces evidence; never promotes or applies.
- D4 four proof bars mandatory — missing any bar → ``INSUFFICIENT``.
- D5 ``#64`` / ``#67`` inputs are advisory structured envelopes only.
- D6 insufficient request → ``INPUT_INSUFFICIENT_CANNOT_VALIDATE``.
- D7 ``correction_evidence_slot`` populated only on ``SUFFICIENT``.
- D8 zero writes to production policy, scoreboard, registry, or AUTH-5.
- D9 false-clear guard feeds ``#62`` downstream — not inline mutation.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, replace
from typing import Callable, Literal
from uuid import uuid4

from core.blackboard import GovernanceError, SyntheticAttackCasePayload
from core.orchestrator import RouteContext
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext
from core.sandbox.failure_classification_agent import FailureClassification
from core.sandbox.loop import SandboxLoopConfig, _blue_detect, run_sandbox_cycle
from core.sandbox.rule_improvement_agent import RuleImprovementProposal

CORRECTION_EVIDENCE_AGENT_ID = "correction_evidence_001"
CORRECTION_EVIDENCE_LAYER = 6
CORRECTION_EVIDENCE_AUTHORITY_LEVEL = 3
HARNESS_VERSION = "correction_evidence_es1_v1"

REFUSAL_ENVELOPE = "INPUT_INSUFFICIENT_CANNOT_VALIDATE"
CONTROL_MAPPING = "correction_evidence:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic correction evidence only; "
    "SUFFICIENT verdicts queue for operator review and do not promote or apply."
)

Verdict = Literal["SUFFICIENT", "INSUFFICIENT"]
ValidationKind = Literal["success", "refusal"]

PROMOTION_CATEGORIES = frozenset({"REGRESSION", "FUNCTIONAL", "UNCLASSIFIED"})
PROMOTION_MIN_SEVERITY = frozenset({"MEDIUM", "HIGH", "CRITICAL"})
BOUNDED_IMPACTS = frozenset({"bounded_low", "bounded_medium", "bounded_high"})

PROMOTE_FORBIDDEN_MARKERS = (
    "deploy_mutation",
    "deploy to production",
    "auto-apply",
    "auto-promote",
    "§11 signed",
    "promote to production",
    "apply the rule",
)


@dataclass(frozen=True)
class CorrectionValidationRequest:
    request_id: str
    failure_ref: str
    proposal_ref: str
    tenant_scope: str
    classification_ref: str | None = None
    target_category: str | None = None
    corpus_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    notes: str | None = None


@dataclass(frozen=True)
class RegressionCorpusCase:
    case_id: str
    subject: str
    sender_domain: str
    expected_signals: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    fix_passed: bool
    fix_proof: str
    no_regression_passed: bool
    no_regression_proof: str
    regression_new_misses: tuple[str, ...]
    blast_radius_passed: bool
    blast_radius_estimate: str
    sandbox_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class CorrectionEvidencePacket:
    packet_id: str
    request_ref: str
    proposal_ref: str
    classification_ref: str | None
    verdict: Verdict
    fix_proof: str
    no_regression_proof: str
    blast_radius_estimate: str
    reproducibility: str
    sandbox_evidence_ids: tuple[str, ...]
    gaps: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ValidationResult:
    kind: ValidationKind
    packet: CorrectionEvidencePacket | None = None
    refusal: str | None = None
    gaps: tuple[str, ...] = ()


EvaluationRunner = Callable[
    [
        CorrectionValidationRequest,
        RuleImprovementProposal,
        RouteContext,
        tuple[RegressionCorpusCase, ...],
    ],
    EvaluationResult,
]


def validate_request(request: CorrectionValidationRequest) -> tuple[str, ...]:
    gaps: list[str] = []
    if not request.request_id.strip():
        gaps.append("request_id is required")
    if not request.failure_ref.strip():
        gaps.append("failure_ref is required")
    if not request.proposal_ref.strip():
        gaps.append("proposal_ref is required")
    if request.tenant_scope != "sandbox_only":
        gaps.append("tenant_scope must be sandbox_only at Evidence Stage 1")
    notes = (request.notes or "").lower()
    for marker in PROMOTE_FORBIDDEN_MARKERS:
        if marker in notes:
            gaps.append(f"notes contain forbidden promote/apply language: {marker}")
    return tuple(gaps)


def format_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "Correction validation request lacks fields required for evidence assembly.",
            "BOUNDARY:",
            "advisory only; no packet emitted; no promotion; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def _inputs_digest(
    request: CorrectionValidationRequest,
    proposal: RuleImprovementProposal,
    corpus_cases: tuple[RegressionCorpusCase, ...],
) -> str:
    payload = {
        "request_id": request.request_id,
        "failure_ref": request.failure_ref,
        "proposal_ref": request.proposal_ref,
        "proposal_id": proposal.proposal_id,
        "corpus_case_ids": [case.case_id for case in corpus_cases],
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _corpus_hash(corpus_cases: tuple[RegressionCorpusCase, ...]) -> str:
    payload = [
        {
            "case_id": case.case_id,
            "subject": case.subject,
            "sender_domain": case.sender_domain,
            "expected_signals": list(case.expected_signals),
        }
        for case in corpus_cases
    ]
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _corpus_case_passes(
    case: RegressionCorpusCase, config: SandboxLoopConfig
) -> bool:
    payload = SyntheticAttackCasePayload(
        attack_kind=f"synthetic_{case.case_id}",
        generated_from_weakness_id=uuid4(),
        synthetic_subject=case.subject,
        synthetic_sender_domain=case.sender_domain,
        expected_detection_signals=list(case.expected_signals),
        raw_tenant_data_removed=True,
    )
    detection = _blue_detect(payload)
    missing = [
        signal for signal in case.expected_signals if signal not in detection.signals
    ]
    return (
        detection.confidence >= config.detection_confidence_threshold and not missing
    )


def _target_corpus_cases(
    request: CorrectionValidationRequest,
    corpus_cases: tuple[RegressionCorpusCase, ...],
) -> tuple[RegressionCorpusCase, ...]:
    if request.corpus_refs:
        by_id = {case.case_id: case for case in corpus_cases}
        selected = tuple(by_id[ref] for ref in request.corpus_refs if ref in by_id)
        if selected:
            return selected
    return corpus_cases[:1]


def _reproducibility_line(
    request: CorrectionValidationRequest,
    proposal: RuleImprovementProposal,
    corpus_cases: tuple[RegressionCorpusCase, ...],
) -> str:
    return (
        f"corpus_hash={_corpus_hash(corpus_cases)} "
        f"harness_version={HARNESS_VERSION} "
        f"inputs_digest={_inputs_digest(request, proposal, corpus_cases)}"
    )


def _classification_promotion_gaps(
    classification: FailureClassification | None,
    request: CorrectionValidationRequest,
) -> tuple[str, ...]:
    if classification is None:
        return ()
    gaps: list[str] = []
    if classification.failure_ref != request.failure_ref:
        gaps.append("classification failure_ref does not match request failure_ref")
    if classification.category not in PROMOTION_CATEGORIES:
        gaps.append(
            f"classification category {classification.category} outside promotion path"
        )
    if classification.severity not in PROMOTION_MIN_SEVERITY:
        gaps.append(
            f"classification severity {classification.severity} below MEDIUM promotion floor"
        )
    if request.target_category and request.target_category != classification.category:
        gaps.append("target_category does not match classification category")
    return tuple(gaps)


def default_evaluation_runner(
    request: CorrectionValidationRequest,
    proposal: RuleImprovementProposal,
    route_context: RouteContext,
    corpus_cases: tuple[RegressionCorpusCase, ...],
) -> EvaluationResult:
    config = SandboxLoopConfig(sandbox_tenant_id="sandbox_default")
    cycle_result = run_sandbox_cycle(route_context, config=config)
    cycle_evidence_ids = tuple(
        str(item.mutant_evaluation.record.record_id)
        for item in cycle_result.item_results
    )

    target_cases = _target_corpus_cases(request, corpus_cases)
    target_results = {
        case.case_id: _corpus_case_passes(case, config) for case in target_cases
    }
    failure_ref_bound = request.failure_ref in proposal.rationale
    fix_passed = (
        proposal.proposal_id == request.proposal_ref
        and failure_ref_bound
        and cycle_result.processed_count > 0
        and bool(target_cases)
        and all(target_results.values())
        and proposal.candidate_confidence > proposal.baseline_confidence
        and bool(proposal.sandbox_evidence_ids)
    )
    target_summary = ", ".join(
        f"{case_id}={'pass' if passed else 'miss'}"
        for case_id, passed in target_results.items()
    )
    fix_proof = (
        f"failure_ref {request.failure_ref} bound in proposal rationale; "
        f"target corpus replay {target_summary}; "
        f"sandbox cycle processed {cycle_result.processed_count} weakness case(s); "
        f"confidence {proposal.baseline_confidence:.4f} -> "
        f"{proposal.candidate_confidence:.4f}"
        if fix_passed
        else (
            "fix proof failed: target corpus miss, failure_ref not bound, "
            "sandbox replay empty, or missing confidence delta / sandbox evidence ids"
        )
    )

    regression_results = {
        case.case_id: _corpus_case_passes(case, config) for case in corpus_cases
    }
    new_misses = tuple(
        case_id for case_id, passed in regression_results.items() if not passed
    )
    no_regression_passed = len(corpus_cases) >= 4 and not new_misses
    listed = ", ".join(
        f"{case.case_id}={'pass' if regression_results[case.case_id] else 'miss'}"
        for case in corpus_cases
    )
    no_regression_proof = (
        f"corpus sandbox replay zero new misses; cases: {listed}"
        if no_regression_passed
        else f"corpus sandbox replay misses: {', '.join(new_misses) or 'insufficient corpus'}"
    )

    blast_radius_passed = (
        proposal.estimated_detection_impact in BOUNDED_IMPACTS
        and bool(proposal.blast_radius_note.strip())
        and proposal.blast_radius_note.strip().lower() != "unbounded"
    )
    blast_radius_estimate = (
        f"{proposal.estimated_detection_impact}; {proposal.blast_radius_note}"
        if blast_radius_passed
        else "blast radius unbounded or missing bounded estimate"
    )

    return EvaluationResult(
        fix_passed=fix_passed,
        fix_proof=fix_proof,
        no_regression_passed=no_regression_passed,
        no_regression_proof=no_regression_proof,
        regression_new_misses=new_misses,
        blast_radius_passed=blast_radius_passed,
        blast_radius_estimate=blast_radius_estimate,
        sandbox_evidence_ids=proposal.sandbox_evidence_ids + cycle_evidence_ids,
    )


def _proof_bar_gaps(evaluation: EvaluationResult) -> tuple[str, ...]:
    gaps: list[str] = []
    if not evaluation.fix_passed:
        gaps.append("fix proof bar not satisfied")
    if not evaluation.no_regression_passed:
        gaps.append("no-regression proof bar not satisfied")
    if not evaluation.blast_radius_passed:
        gaps.append("blast-radius proof bar not satisfied")
    return tuple(gaps)


def build_rationale(verdict: Verdict, gaps: tuple[str, ...]) -> str:
    if verdict == "SUFFICIENT":
        rationale = (
            "Sandbox validation satisfied fix, no-regression, blast-radius, "
            "and reproducibility proof bars for the scoped correction request."
        )
    else:
        rationale = (
            "Sandbox validation did not satisfy all proof bars; "
            f"named gaps: {', '.join(gaps) if gaps else 'unspecified'}."
        )
    lowered = rationale.lower()
    if any(marker in lowered for marker in PROMOTE_FORBIDDEN_MARKERS):
        raise GovernanceError("rationale would contain forbidden promote/apply language")
    return rationale


def format_packet(packet: CorrectionEvidencePacket) -> str:
    evidence = ", ".join(packet.sandbox_evidence_ids) if packet.sandbox_evidence_ids else ""
    gap_lines = ", ".join(packet.gaps) if packet.gaps else ""
    classification = packet.classification_ref if packet.classification_ref else "null"
    return "\n".join(
        [
            "CORRECTION_EVIDENCE_PACKET",
            f"packet_id: {packet.packet_id}",
            f"request_ref: {packet.request_ref}",
            f"proposal_ref: {packet.proposal_ref}",
            f"classification_ref: {classification}",
            f"verdict: {packet.verdict}",
            f"fix_proof: {packet.fix_proof}",
            f"no_regression_proof: {packet.no_regression_proof}",
            f"blast_radius_estimate: {packet.blast_radius_estimate}",
            f"reproducibility: {packet.reproducibility}",
            f"sandbox_evidence_ids: [{evidence}]",
            f"gaps: [{gap_lines}]",
            f"rationale: {packet.rationale}",
        ]
    )


def attach_correction_evidence_slot(
    proposal: RuleImprovementProposal,
    packet: CorrectionEvidencePacket,
) -> RuleImprovementProposal:
    if packet.verdict != "SUFFICIENT":
        return proposal
    return replace(proposal, correction_evidence_slot=packet.packet_id)


def validate_correction_evidence(
    request: CorrectionValidationRequest,
    proposal: RuleImprovementProposal,
    route_context: RouteContext,
    *,
    classification: FailureClassification | None = None,
    corpus_cases: tuple[RegressionCorpusCase, ...] = (),
    evaluation_runner: EvaluationRunner = default_evaluation_runner,
) -> ValidationResult:
    gaps = validate_request(request)
    if gaps:
        return ValidationResult(kind="refusal", refusal=format_refusal(gaps), gaps=gaps)

    if proposal.proposal_id != request.proposal_ref:
        gaps = ("proposal_ref does not match supplied proposal_id",)
        return ValidationResult(kind="refusal", refusal=format_refusal(gaps), gaps=gaps)

    evaluation = evaluation_runner(request, proposal, route_context, corpus_cases)
    proof_gaps = _proof_bar_gaps(evaluation)
    classification_gaps = _classification_promotion_gaps(classification, request)
    all_gaps = proof_gaps + classification_gaps

    verdict: Verdict = "SUFFICIENT" if not all_gaps else "INSUFFICIENT"
    reproducibility = _reproducibility_line(request, proposal, corpus_cases)
    if not reproducibility.strip():
        all_gaps = all_gaps + ("reproducibility proof bar not satisfied",)
        verdict = "INSUFFICIENT"

    packet = CorrectionEvidencePacket(
        packet_id=f"cep_{uuid.uuid4().hex[:12]}",
        request_ref=request.request_id,
        proposal_ref=proposal.proposal_id,
        classification_ref=classification.id if classification else request.classification_ref,
        verdict=verdict,
        fix_proof=evaluation.fix_proof,
        no_regression_proof=evaluation.no_regression_proof,
        blast_radius_estimate=evaluation.blast_radius_estimate,
        reproducibility=reproducibility,
        sandbox_evidence_ids=evaluation.sandbox_evidence_ids,
        gaps=all_gaps,
        rationale=build_rationale(verdict, all_gaps),
    )
    return ValidationResult(kind="success", packet=packet)


class CorrectionEvidenceAgent:
    """Governed Layer 6 validator — correction request in, evidence packet out."""

    __test__ = False

    agent_id: str = CORRECTION_EVIDENCE_AGENT_ID
    layer: int = CORRECTION_EVIDENCE_LAYER
    authority_level: int = CORRECTION_EVIDENCE_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        validation_request: CorrectionValidationRequest | None = None,
        proposal: RuleImprovementProposal | None = None,
        route_context: RouteContext | None = None,
        classification: FailureClassification | None = None,
        corpus_cases: tuple[RegressionCorpusCase, ...] = (),
        evaluation_runner: EvaluationRunner = default_evaluation_runner,
    ) -> None:
        self._validation_request = validation_request
        self._proposal = proposal
        self._route_context = route_context
        self._classification = classification
        self._corpus_cases = corpus_cases
        self._evaluation_runner = evaluation_runner

    def validate(
        self,
        validation_request: CorrectionValidationRequest | None = None,
        proposal: RuleImprovementProposal | None = None,
        route_context: RouteContext | None = None,
    ) -> ValidationResult:
        request = validation_request or self._validation_request
        item = proposal or self._proposal
        context = route_context or self._route_context
        if request is None:
            gaps = ("validation_request is required",)
            return ValidationResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        if item is None:
            gaps = ("proposal is required",)
            return ValidationResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        if context is None:
            gaps = ("route_context is required",)
            return ValidationResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        return validate_correction_evidence(
            request,
            item,
            context,
            classification=self._classification,
            corpus_cases=self._corpus_cases,
            evaluation_runner=self._evaluation_runner,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.validate()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        packet = result.packet
        assert packet is not None
        facts = (
            f"correction_evidence_packet:{packet.packet_id} "
            f"verdict={packet.verdict} proposal_ref={packet.proposal_ref}"
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
    "CORRECTION_EVIDENCE_AGENT_ID",
    "CorrectionEvidenceAgent",
    "CorrectionEvidencePacket",
    "CorrectionValidationRequest",
    "EvaluationResult",
    "EvaluationRunner",
    "REFUSAL_ENVELOPE",
    "RegressionCorpusCase",
    "ValidationResult",
    "attach_correction_evidence_slot",
    "default_evaluation_runner",
    "format_packet",
    "format_refusal",
    "validate_correction_evidence",
    "validate_request",
]
