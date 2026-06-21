"""Failure Classification governed-agent wrapper — swarm agent #64.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Failure_Classification_Agent_Design_Contract_Deep_Dive.md`` (2026-06-21).
Reads one recorded failure record and emits a taxonomy-bound classification
(category + severity + evidence_ref + rationale) only.

Scope / governance boundary (contract D1-D9, deliberate):
- D1 record-in, classification-out; one failure record per invocation.
- D2 fixed taxonomy; no-match → ``UNCLASSIFIED``, never guess.
- D3 severity grounded in category mapping + record evidence.
- D4 every label carries ``evidence_ref``.
- D5 rationale is explanatory only — no recommendation or next-step language.
- D6 recorded failure text only — no implementation-code reads.
- D7 insufficient record → ``INPUT_INSUFFICIENT_CANNOT_CLASSIFY``.
- D8 zero writes; no scoreboard/registry/state mutation at Stage 1.
- D9 no autonomy / AUTH-5 blocked; not in ``build_default_registry``.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.blackboard import GovernanceError
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext

FAILURE_CLASSIFICATION_AGENT_ID = "failure_classification_001"
FAILURE_CLASSIFICATION_LAYER = 5
FAILURE_CLASSIFICATION_AUTHORITY_LEVEL = 3

REFUSAL_ENVELOPE = "INPUT_INSUFFICIENT_CANNOT_CLASSIFY"
CONTROL_MAPPING = "failure_classification:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic failure classification only; "
    "labels are triage inputs and do not route or remediate."
)

Category = Literal[
    "FLAKE",
    "REGRESSION",
    "AUTHORITY_BOUNDARY",
    "EPISTEMIC_DRIFT",
    "HANDOFF_INTEGRITY",
    "CONTRACT_ALIGNMENT",
    "GATE_EVIDENCE_MISSING",
    "FUNCTIONAL",
    "UNCLASSIFIED",
]

Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

ClassificationKind = Literal["success", "refusal"]

CATEGORY_SEVERITY: dict[Category, Severity] = {
    "AUTHORITY_BOUNDARY": "CRITICAL",
    "EPISTEMIC_DRIFT": "HIGH",
    "HANDOFF_INTEGRITY": "HIGH",
    "GATE_EVIDENCE_MISSING": "HIGH",
    "CONTRACT_ALIGNMENT": "MEDIUM",
    "REGRESSION": "MEDIUM",
    "FUNCTIONAL": "MEDIUM",
    "UNCLASSIFIED": "MEDIUM",
    "FLAKE": "LOW",
}

RECOMMENDATION_MARKERS = (
    "recommend",
    "should fix",
    "retry",
    "escalate",
    "route to",
    "block the",
    "remediate",
    "re-run the",
    "next step:",
)

FORBIDDEN_READ_SUFFIXES = (".py", ".pyc")


@dataclass(frozen=True)
class FailureRecord:
    failure_ref: str
    body: str
    source_kind: str | None = None


@dataclass(frozen=True)
class FailureClassification:
    id: str
    failure_ref: str
    category: Category
    severity: Severity
    evidence_ref: str
    rationale: str


@dataclass(frozen=True)
class ClassificationResult:
    kind: ClassificationKind
    classification: FailureClassification | None = None
    refusal: str | None = None
    gaps: tuple[str, ...] = ()


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def _evidence_snippet(body: str, needle: str, *, window: int = 120) -> str:
    lowered = body.lower()
    idx = lowered.find(needle.lower())
    if idx < 0:
        snippet = body[:window].strip()
    else:
        start = max(0, idx - 20)
        snippet = body[start : start + window].strip()
    return " ".join(snippet.split())


def _match_first(
    body: str, rules: tuple[tuple[Category, tuple[str, ...]], ...]
) -> tuple[Category, str] | None:
    lowered = body.lower()
    for category, needles in rules:
        for needle in needles:
            if needle.lower() in lowered:
                return category, _evidence_snippet(body, needle)
    return None


def detect_category(body: str) -> tuple[Category, str]:
    rules: tuple[tuple[Category, tuple[str, ...]], ...] = (
        (
            "AUTHORITY_BOUNDARY",
            (
                "authority_invariant_breach",
                "auth-5 found",
                "authority invariant breach",
                "forbidden authority",
            ),
        ),
        (
            "EPISTEMIC_DRIFT",
            (
                "report_only_findings",
                "review_required",
                "conflicting_candidate_id",
                "epistemic_drift",
                "contradiction between",
                "drift:",
            ),
        ),
        (
            "HANDOFF_INTEGRITY",
            (
                "stale handoff",
                "duplicate handoff",
                "lost handoff",
                "misrouted handoff",
                "handoff integrity",
            ),
        ),
        (
            "GATE_EVIDENCE_MISSING",
            (
                "gate evidence missing",
                "gated without gate",
                "missing gate artifact",
                "completion gate required",
                "awaiting_audit without gate",
            ),
        ),
        (
            "CONTRACT_ALIGNMENT",
            (
                "blocked_missing_contract",
                "contract alignment",
                "parser mismatch",
                "architect mismatch",
                "missing contract",
            ),
        ),
        (
            "FLAKE",
            (
                "non-deterministic",
                "passes on identical re-run",
                "flake",
                "transient failure",
            ),
        ),
        (
            "REGRESSION",
            (
                "regression",
                "previously-passing",
                "baseline compare",
                "baseline mismatch",
            ),
        ),
        (
            "FUNCTIONAL",
            (
                "assertionerror",
                "assert ",
                "failed tests/",
                "e       assert",
                "pytest failure",
            ),
        ),
    )
    matched = _match_first(body, rules)
    if matched is not None:
        return matched
    if len(body.strip()) >= 20:
        return "UNCLASSIFIED", body[:120].strip()
    return "UNCLASSIFIED", body.strip() or "record body present but thin"


def build_rationale(category: Category, evidence_ref: str) -> str:
    return (
        f"Category {category} assigned because the failure record contains "
        f"evidence matching the fixed taxonomy: {evidence_ref}"
    )


def validate_failure_record(record: FailureRecord) -> tuple[str, ...]:
    gaps: list[str] = []
    if not _normalize_text(record.failure_ref):
        gaps.append("failure_ref is required")
    body = _normalize_text(record.body)
    if not body:
        gaps.append("failure record body is empty")
    if record.failure_ref and any(
        record.failure_ref.endswith(suffix) for suffix in FORBIDDEN_READ_SUFFIXES
    ):
        gaps.append("failure_ref must not point at implementation modules")
    return tuple(gaps)


def format_refusal(gaps: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "gaps:"]
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "WHY:",
            "Recorded failure lacks evidence required to classify.",
            "BOUNDARY:",
            "advisory only; no classification emitted; no remediation; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def format_classification(item: FailureClassification) -> str:
    return "\n".join(
        [
            "FAILURE_CLASSIFICATION",
            f"id: {item.id}",
            f"failure_ref: {item.failure_ref}",
            f"category: {item.category}",
            f"severity: {item.severity}",
            f"evidence_ref: {item.evidence_ref}",
            f"rationale: {item.rationale}",
        ]
    )


def classify_failure_record(record: FailureRecord) -> ClassificationResult:
    gaps = validate_failure_record(record)
    if gaps:
        return ClassificationResult(
            kind="refusal",
            refusal=format_refusal(gaps),
            gaps=gaps,
        )

    body = _normalize_text(record.body)
    category, evidence_ref = detect_category(body)
    severity = CATEGORY_SEVERITY[category]
    rationale = build_rationale(category, evidence_ref)
    lowered_rationale = rationale.lower()
    if any(marker in lowered_rationale for marker in RECOMMENDATION_MARKERS):
        return ClassificationResult(
            kind="refusal",
            refusal=format_refusal(("rationale would contain forbidden response language",)),
            gaps=("rationale_contains_response_language",),
        )

    classification = FailureClassification(
        id=f"fc_{uuid.uuid4().hex[:12]}",
        failure_ref=record.failure_ref,
        category=category,
        severity=severity,
        evidence_ref=evidence_ref,
        rationale=rationale,
    )
    return ClassificationResult(kind="success", classification=classification)


class FailureClassificationAgent:
    """Governed Layer 5 classifier — recorded failure in, label out."""

    __test__ = False

    agent_id: str = FAILURE_CLASSIFICATION_AGENT_ID
    layer: int = FAILURE_CLASSIFICATION_LAYER
    authority_level: int = FAILURE_CLASSIFICATION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        failure_record: FailureRecord | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._failure_record = failure_record
        self._repo_root = repo_root

    def classify(self, failure_record: FailureRecord | None = None) -> ClassificationResult:
        record = failure_record or self._failure_record
        if record is None:
            gaps = ("failure_record is required",)
            return ClassificationResult(
                kind="refusal",
                refusal=format_refusal(gaps),
                gaps=gaps,
            )
        return classify_failure_record(record)

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.classify()
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        item = result.classification
        assert item is not None
        facts = (
            f"failure_classification:{item.id} category={item.category} "
            f"severity={item.severity} failure_ref={item.failure_ref}"
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
    "CATEGORY_SEVERITY",
    "ClassificationResult",
    "FAILURE_CLASSIFICATION_AGENT_ID",
    "FailureClassification",
    "FailureClassificationAgent",
    "FailureRecord",
    "REFUSAL_ENVELOPE",
    "build_rationale",
    "classify_failure_record",
    "detect_category",
    "format_classification",
    "format_refusal",
    "validate_failure_record",
]
