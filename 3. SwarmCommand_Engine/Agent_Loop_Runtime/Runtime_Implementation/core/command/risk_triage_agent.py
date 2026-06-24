"""Risk Triage governed-agent wrapper — swarm agent #3.

Stage A telemetry-scorer wrapper authorized by the §11-SIGNED
``docs/mmi/contracts/003_risk_triage_contract.md`` (MMI-DEC-098/097) and
Matt build authorization (MMI-DEC-115). Emits strict allowlist score telemetry
only — no routing, mitigation, disposition, or narrative.

AUTH-4 boundary (contract):
- #3 scores; #1 routes; #2 classifies.
- Separate ``RiskScoreTelemetry`` envelope (MissionContext schema unchanged).
- v1 scoring rules embedded under ``SCORING_POLICY_VERSION`` until signed
  rubric/policy annex lands.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from core.blackboard.models import GovernanceError
from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext

RISK_TRIAGE_AGENT_ID = "risk_triage_001"
RISK_TRIAGE_LAYER = 1
RISK_TRIAGE_AUTHORITY_LEVEL = 3
SCORING_POLICY_VERSION = "mmi_rt_v1"

ScoringKind = Literal["success", "refusal"]

REFUSAL_PROVENANCE = "INPUT_PROVENANCE_MISSING"
REFUSAL_ROUTING_KEY = "INPUT_ROUTING_KEY_FORBIDDEN"
REFUSAL_POLICY = "INPUT_POLICY_VERSION_MISMATCH"

_REASON_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
_REASON_PROVENANCE_MISSING = "INPUT_PROVENANCE_MISSING"
_REASON_ROUTING_KEY = "INPUT_ROUTING_KEY_FORBIDDEN"

_ROUTING_FORBIDDEN_KEYS = frozenset(
    {
        "target_agent",
        "target_agents",
        "route_to",
        "routing_lane",
        "lane",
        "next_action",
        "next_actions",
        "dispatch",
        "handoff_to",
        "mitigation",
        "quarantine",
        "block",
        "alert",
        "notify",
        "contain",
        "isolate",
        "recommended_action",
        "recommendation",
        "approval",
        "authorized",
        "NEXT_DECIDED",
        "escalate_to",
        "agents",
        "challenge_agents",
    }
)

_FORBIDDEN_TELEMETRY_KEYS = frozenset(
    {
        "target_agent",
        "route_to",
        "recommended_action",
        "plain_english_summary",
        "client_message",
        "verification_instructions",
        "dispatch",
        "next_action",
        "block",
        "quarantine",
        "alert",
    }
)

_AXIS_VENDOR_FRAUD = "vendor_fraud"
_AXIS_WIRE_ANOMALY = "wire_anomaly"
_AXIS_INVOICE_AUTHENTICITY = "invoice_authenticity"
_AXIS_IMPERSONATION = "impersonation"

_SIGNAL_AXIS: dict[str, tuple[str, float]] = {
    "payment_change_detection": (_AXIS_VENDOR_FRAUD, 72.0),
    "vendor_payment": (_AXIS_VENDOR_FRAUD, 68.0),
    "credential_phishing": (_AXIS_IMPERSONATION, 70.0),
    "credential_reset_language": (_AXIS_IMPERSONATION, 65.0),
    "ghost_thread": (_AXIS_VENDOR_FRAUD, 66.0),
    "business_email_compromise": (_AXIS_VENDOR_FRAUD, 74.0),
    "executive_impersonation": (_AXIS_IMPERSONATION, 78.0),
    "language_pressure": (_AXIS_IMPERSONATION, 60.0),
    "pdf_fingerprint": (_AXIS_INVOICE_AUTHENTICITY, 64.0),
    "invoice_fraud": (_AXIS_INVOICE_AUTHENTICITY, 70.0),
    "payroll_diversion": (_AXIS_WIRE_ANOMALY, 75.0),
    "attachment_risk": (_AXIS_WIRE_ANOMALY, 55.0),
    "link_inspection": (_AXIS_IMPERSONATION, 58.0),
    "ransomware_precursor": (_AXIS_WIRE_ANOMALY, 62.0),
    "new_banking_instructions": (_AXIS_VENDOR_FRAUD, 70.0),
    "lookalike_sender_domain": (_AXIS_IMPERSONATION, 68.0),
}

_DEFAULT_AXES: dict[str, float] = {
    _AXIS_VENDOR_FRAUD: 0.0,
    _AXIS_WIRE_ANOMALY: 0.0,
    _AXIS_INVOICE_AUTHENTICITY: 0.0,
    _AXIS_IMPERSONATION: 0.0,
}


@dataclass(frozen=True)
class SourceProvenance:
    detector_id: str
    detector_contract_version: str
    evidence_ref: str


@dataclass(frozen=True)
class DetectorEvidenceRecord:
    detector_id: str
    detector_contract_version: str
    evidence_ref: str
    emitted_at: str
    signal_tags: tuple[str, ...] = ()
    extra_fields: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class RiskTriageInput:
    message_id: str
    tenant_id: str
    detector_outputs: tuple[DetectorEvidenceRecord, ...]
    scoring_policy_version: str


@dataclass(frozen=True)
class RiskScoreTelemetry:
    message_id: str
    tenant_id: str
    aggregate_risk_score: float
    axis_scores: dict[str, float]
    scoring_reason_codes: tuple[str, ...]
    scoring_policy_version: str
    source_provenance: tuple[SourceProvenance, ...]
    score_record_id: uuid.UUID | None = None
    emitted_at: datetime | None = None


@dataclass(frozen=True)
class ScoringResult:
    kind: ScoringKind
    telemetry: RiskScoreTelemetry | None = None
    refusal: str | None = None


def _record_has_routing_keys(record: DetectorEvidenceRecord) -> bool:
    return bool(record.extra_fields & _ROUTING_FORBIDDEN_KEYS)


def _validate_record(record: DetectorEvidenceRecord) -> str | None:
    if _record_has_routing_keys(record):
        return REFUSAL_ROUTING_KEY
    if not record.detector_id.strip():
        return REFUSAL_PROVENANCE
    if not record.detector_contract_version.strip():
        return REFUSAL_PROVENANCE
    if not record.evidence_ref.strip():
        return REFUSAL_PROVENANCE
    if not record.emitted_at.strip():
        return REFUSAL_PROVENANCE
    return None


def _axis_scores_from_tags(
    tags: frozenset[str],
) -> tuple[dict[str, float], tuple[str, ...]]:
    axes = dict(_DEFAULT_AXES)
    reason_codes: list[str] = []
    for tag in sorted(tags):
        mapping = _SIGNAL_AXIS.get(tag.strip().lower())
        if mapping is None:
            continue
        axis_name, value = mapping
        axes[axis_name] = max(axes[axis_name], value)
        reason_codes.append(f"policy_match:{tag}")
    return axes, tuple(reason_codes)


def score_case(payload: RiskTriageInput) -> ScoringResult:
    if payload.scoring_policy_version != SCORING_POLICY_VERSION:
        return ScoringResult(kind="refusal", refusal=REFUSAL_POLICY)
    if not payload.message_id.strip() or not payload.tenant_id.strip():
        return ScoringResult(kind="refusal", refusal=REFUSAL_PROVENANCE)

    accepted: list[DetectorEvidenceRecord] = []
    reason_codes: list[str] = []
    all_tags: set[str] = set()

    for record in payload.detector_outputs:
        refusal = _validate_record(record)
        if refusal == REFUSAL_ROUTING_KEY:
            return ScoringResult(kind="refusal", refusal=REFUSAL_ROUTING_KEY)
        if refusal is not None:
            reason_codes.append(_REASON_PROVENANCE_MISSING)
            continue
        accepted.append(record)
        all_tags.update(tag.strip().lower() for tag in record.signal_tags if tag.strip())

    if not accepted:
        telemetry = RiskScoreTelemetry(
            message_id=payload.message_id.strip(),
            tenant_id=payload.tenant_id.strip(),
            aggregate_risk_score=0.0,
            axis_scores=dict(_DEFAULT_AXES),
            scoring_reason_codes=tuple(
                sorted(set(reason_codes) | {_REASON_INSUFFICIENT_EVIDENCE})
            ),
            scoring_policy_version=SCORING_POLICY_VERSION,
            source_provenance=(),
            score_record_id=uuid.uuid4(),
            emitted_at=datetime.now(timezone.utc),
        )
        return ScoringResult(kind="success", telemetry=telemetry)

    axes, tag_reasons = _axis_scores_from_tags(frozenset(all_tags))
    aggregate = max(axes.values())
    merged_reasons = tuple(sorted(set(reason_codes) | set(tag_reasons)))
    provenance = tuple(
        SourceProvenance(
            detector_id=record.detector_id,
            detector_contract_version=record.detector_contract_version,
            evidence_ref=record.evidence_ref,
        )
        for record in accepted
    )

    telemetry = RiskScoreTelemetry(
        message_id=payload.message_id.strip(),
        tenant_id=payload.tenant_id.strip(),
        aggregate_risk_score=round(aggregate, 4),
        axis_scores={key: round(value, 4) for key, value in axes.items()},
        scoring_reason_codes=merged_reasons,
        scoring_policy_version=SCORING_POLICY_VERSION,
        source_provenance=provenance,
        score_record_id=uuid.uuid4(),
        emitted_at=datetime.now(timezone.utc),
    )
    return ScoringResult(kind="success", telemetry=telemetry)


def assert_telemetry_auth4_compliant(telemetry: RiskScoreTelemetry) -> None:
    serialized = (
        f"{telemetry.message_id}|{telemetry.tenant_id}|"
        f"{telemetry.aggregate_risk_score}|{telemetry.axis_scores}|"
        f"{telemetry.scoring_reason_codes}|{telemetry.scoring_policy_version}|"
        f"{telemetry.source_provenance}"
    )
    lowered = serialized.lower()
    for token in _FORBIDDEN_TELEMETRY_KEYS:
        if token in lowered:
            raise GovernanceError(
                f"telemetry contains forbidden command or narrative token: {token!r}"
            )
    for key in telemetry.axis_scores:
        if key not in _DEFAULT_AXES:
            raise GovernanceError(f"telemetry axis {key!r} is not in closed policy set")


def telemetry_to_observed_facts(telemetry: RiskScoreTelemetry) -> tuple[str, ...]:
    facts: list[str] = [
        f"triage_aggregate_risk_score:{telemetry.aggregate_risk_score:.4f}",
        f"triage_scoring_policy_version:{telemetry.scoring_policy_version}",
    ]
    for axis, value in sorted(telemetry.axis_scores.items()):
        facts.append(f"triage_axis_{axis}:{value:.4f}")
    facts.extend(
        f"triage_scoring_reason_code:{code}" for code in telemetry.scoring_reason_codes
    )
    facts.extend(
        f"triage_source_detector:{item.detector_id}" for item in telemetry.source_provenance
    )
    return tuple(facts)


def input_from_context(
    context: MissionContext,
    *,
    message_id: str,
    detector_outputs: tuple[DetectorEvidenceRecord, ...] = (),
) -> RiskTriageInput:
    return RiskTriageInput(
        message_id=message_id,
        tenant_id=context.tenant_id,
        detector_outputs=detector_outputs,
        scoring_policy_version=SCORING_POLICY_VERSION,
    )


class RiskTriageAgent:
    """Governed Layer 1 Command telemetry scorer — AUTH-4 scores never routes."""

    agent_id: str = RISK_TRIAGE_AGENT_ID
    layer: int = RISK_TRIAGE_LAYER
    authority_level: int = RISK_TRIAGE_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False
    scoring_policy_version: str = SCORING_POLICY_VERSION

    def __init__(
        self,
        *,
        detector_outputs: tuple[DetectorEvidenceRecord, ...] = (),
        message_id: str | None = None,
    ) -> None:
        self._detector_outputs = detector_outputs
        self._message_id = message_id

    def score(self, payload: RiskTriageInput) -> ScoringResult:
        result = score_case(payload)
        if result.kind == "success" and result.telemetry is not None:
            assert_telemetry_auth4_compliant(result.telemetry)
        return result

    def analyze(self, context: MissionContext) -> AgentContribution:
        message_id = self._message_id or str(context.case_id)
        payload = input_from_context(
            context,
            message_id=message_id,
            detector_outputs=self._detector_outputs,
        )
        result = self.score(payload)
        if result.kind == "refusal":
            raise ValueError(result.refusal or REFUSAL_PROVENANCE)
        assert result.telemetry is not None
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=telemetry_to_observed_facts(result.telemetry),
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None
