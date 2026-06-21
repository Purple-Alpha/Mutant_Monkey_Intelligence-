"""Plain-English Explanation governed-agent wrapper - swarm agent #52.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md`` (2026-06-20).
Projects one validated ``EmailAnalysisPayload`` through the signed deterministic
rubric mapper ``project_client_facing_rubric()`` and returns the explanation
surface on an in-memory analysis copy only.

Scope / governance boundary (contract D1-D15, deliberate):
- D2/D3 explain-only: projection via ``project_client_facing_rubric``; no detect,
  score, advise-beyond-input, raw-source read, or send/transmit path.
- D13 Stage 1 persistence: in-memory ``client_facing_rubric`` on analysis copy
  returned to explicit caller/test; no Blackboard write; no default registry.
- D11 missing-input refusal: ``INPUT_INSUFFICIENT_CANNOT_EXPLAIN`` with named
  ``missing_fields``.
- D12 per-line traceability: every ``why_this_score`` line comes solely from the
  signed mapper over supplied validated payload fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from core.blackboard import (
    EmailAnalysisPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.scoring.client_facing_rubric import project_client_facing_rubric

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, blackboard_path

PLAIN_ENGLISH_EXPLANATION_AGENT_ID = "plain_english_explanation_001"
PLAIN_ENGLISH_EXPLANATION_LAYER = 4  # Evidence
PLAIN_ENGLISH_EXPLANATION_AUTHORITY_LEVEL = 3  # Specialist Agent

REFUSAL_ENVELOPE = "INPUT_INSUFFICIENT_CANNOT_EXPLAIN"
CONTROL_MAPPING = "plain_english_explanation:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic plain-English explanation only; "
    "not buyer-released and not transmitted."
)

ExplanationKind = Literal["explanation", "refusal"]


@dataclass(frozen=True)
class PlainEnglishExplanationResult:
    kind: ExplanationKind
    analysis: EmailAnalysisPayload | None = None
    refusal: str | None = None
    missing_fields: tuple[str, ...] = ()


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise GovernanceError("PlainEnglishExplanationAgent requires a valid tenant_id")
    return value


def format_insufficient_refusal(missing_fields: tuple[str, ...]) -> str:
    lines = [REFUSAL_ENVELOPE, "missing_fields:"]
    for field_name in missing_fields:
        lines.append(f"- {field_name}")
    lines.extend(
        [
            "WHY:",
            "Required input fields are missing or not traceable, so #52 refuses "
            "to produce a plain-English explanation and names the missing field(s).",
            "BOUNDARY:",
            "advisory only; no explanation emitted; no scoring/action mutation; "
            "no send/transmit; no AUTH-5",
        ]
    )
    return "\n".join(lines) + "\n"


def collect_missing_fields(
    analysis: EmailAnalysisPayload | None,
    *,
    require_source_record: bool = False,
    source_record_id: UUID | None = None,
) -> tuple[str, ...]:
    missing: list[str] = []
    if require_source_record and source_record_id is None:
        missing.append("source_record_id")
    if analysis is None:
        missing.append("email_analysis_payload")
        return tuple(missing)
    if analysis.risk_analysis is None:
        missing.append("risk_analysis")
    if analysis.impersonation_analysis is None:
        missing.append("impersonation_analysis")
    return tuple(missing)


def attach_plain_english_explanation(
    analysis: EmailAnalysisPayload,
) -> EmailAnalysisPayload:
    rubric = project_client_facing_rubric(analysis)
    return analysis.model_copy(update={"client_facing_rubric": rubric})


def explain_payload(
    analysis: EmailAnalysisPayload | None,
    *,
    require_source_record: bool = False,
    source_record_id: UUID | None = None,
) -> PlainEnglishExplanationResult:
    missing = collect_missing_fields(
        analysis,
        require_source_record=require_source_record,
        source_record_id=source_record_id,
    )
    if missing:
        return PlainEnglishExplanationResult(
            kind="refusal",
            refusal=format_insufficient_refusal(missing),
            missing_fields=missing,
        )
    updated = attach_plain_english_explanation(analysis)
    return PlainEnglishExplanationResult(kind="explanation", analysis=updated)


def load_email_analysis_for_context(
    route_context: RouteContext,
    context: MissionContext,
    environment: Environment,
) -> EmailAnalysisPayload | None:
    if context.source_record_id is None:
        return None
    path = blackboard_path(
        route_context.blackboard_root, environment, context.tenant_id
    )
    for record in read_records(path):
        if record.record_id != context.source_record_id:
            continue
        if record.record_type != RecordType.EMAIL_ANALYSIS:
            return None
        if record.tenant_id != context.tenant_id:
            return None
        return EmailAnalysisPayload.model_validate(record.payload)
    return None


class PlainEnglishExplanationAgent:
    """Governed Layer 4 Evidence agent for plain-English rubric projection."""

    agent_id: str = PLAIN_ENGLISH_EXPLANATION_AGENT_ID
    layer: int = PLAIN_ENGLISH_EXPLANATION_LAYER
    authority_level: int = PLAIN_ENGLISH_EXPLANATION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        analysis: EmailAnalysisPayload | None = None,
        route_context: RouteContext | None = None,
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._analysis = analysis
        self._route_context = route_context
        self._environment = environment

    def explain_for_mission(
        self, context: MissionContext
    ) -> PlainEnglishExplanationResult:
        _require_tenant_id(context.tenant_id)
        if self._analysis is not None:
            return explain_payload(self._analysis, require_source_record=False)
        if context.source_record_id is None:
            return explain_payload(
                None,
                require_source_record=True,
                source_record_id=context.source_record_id,
            )
        if self._route_context is None:
            return explain_payload(
                None,
                require_source_record=True,
                source_record_id=context.source_record_id,
            )
        analysis = load_email_analysis_for_context(
            self._route_context, context, self._environment
        )
        return explain_payload(
            analysis,
            require_source_record=True,
            source_record_id=context.source_record_id,
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        result = self.explain_for_mission(context)
        if result.kind == "refusal":
            raise GovernanceError(result.refusal or REFUSAL_ENVELOPE)
        rubric = result.analysis.client_facing_rubric
        if rubric is None or rubric.rubric_status != "available":
            raise GovernanceError("PlainEnglishExplanationAgent requires available rubric")
        facts = tuple(
            f"plain_english_why:{axis.axis_name}={axis.why_this_score}"
            for axis in rubric.axes
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=facts,
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None


__all__ = [
    "PLAIN_ENGLISH_EXPLANATION_AGENT_ID",
    "PlainEnglishExplanationAgent",
    "PlainEnglishExplanationResult",
    "REFUSAL_ENVELOPE",
    "attach_plain_english_explanation",
    "collect_missing_fields",
    "explain_payload",
    "format_insufficient_refusal",
    "load_email_analysis_for_context",
]
