"""Mission Context governed-agent wrapper — swarm agent #2.

Stage A classify-only wrapper authorized by the §11-SIGNED
``docs/mmi/contracts/002_mission_context_contract.md`` (MMI-DEC-105/107) and
Matt build authorization (MMI-DEC-108). Emits closed-vocabulary case
classification envelopes (case_type, review_depth, required_evidence manifest)
only — no routing, scoring, disposition, or narrative.

MC-AUTH boundary (contract):
- #2 classifies; #1 routes; #3 scores.
- Separate ``MissionClassification`` envelope (MissionContext schema unchanged).
- v1 taxonomy rules are embedded under ``CLASSIFICATION_POLICY_VERSION`` until
  a signed classification-policy annex lands.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from core.blackboard import EvidenceLedgerEntry, EvidenceStage, EvidenceType

from core.orchestrator.agent_contract import AgentContribution, ChallengeResult, MissionContext

MISSION_CONTEXT_AGENT_ID = "mission_context_001"
MISSION_CONTEXT_LAYER = 1
MISSION_CONTEXT_AUTHORITY_LEVEL = 3
CLASSIFICATION_POLICY_VERSION = "mmi_mc_v1"

CaseType = Literal[
    "phishing",
    "vendor_payment_fraud",
    "business_email_compromise",
    "executive_impersonation",
    "invoice_fraud",
    "payroll_diversion",
    "ransomware_precursor",
    "cyber_insurance_evidence",
    "unknown",
]

ReviewDepth = Literal["standard", "enhanced", "human_required"]

ClassificationKind = Literal["success", "refusal"]

REFUSAL_PROVENANCE = "INPUT_PROVENANCE_MISSING"
REFUSAL_ROUTING_KEY = "INPUT_ROUTING_KEY_FORBIDDEN"

_ROUTING_FORBIDDEN_KEYS = frozenset(
    {
        "agents",
        "challenge_agents",
        "target_agent",
        "route_to",
        "dispatch",
        "lane",
        "handoff_to",
        "disposition",
        "human_state",
        "escalate",
        "aggregate_risk_score",
        "axis_scores",
        "scoring_reason_codes",
    }
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


ES1_EVIDENCE_LEDGER_RECORD_KIND = "Evidence"

_LEDGER_FORBIDDEN_DETAIL_KEYS = frozenset(
    {
        "authority",
        "verdict",
        "disposition",
        "human_state",
        "swarm_disposition",
        "recommended_action",
        "gate_satisfied",
        "approved",
        "authorized",
    }
)


def es1_observation_details(observed_facts: tuple[str, ...]) -> dict[str, Any]:
    return {
        "record_kind": ES1_EVIDENCE_LEDGER_RECORD_KIND,
        "observations": list(observed_facts),
    }


def map_es1_observations_to_evidence_ledger_entry(
    *,
    agent_id: str,
    tenant_id: str,
    email_id: str,
    observed_facts: tuple[str, ...],
    confidence: float = 0.5,
    stage: EvidenceStage = EvidenceStage.ES1,
) -> EvidenceLedgerEntry:
    """Map ES1 observations to ledger Evidence entries only (no Authority/Verdict)."""

    details = es1_observation_details(observed_facts)
    for key in details:
        if key.lower() in _LEDGER_FORBIDDEN_DETAIL_KEYS:
            raise ValueError(f"forbidden ledger detail key: {key}")
    return EvidenceLedgerEntry(
        agent_id=agent_id,
        tenant_id=tenant_id,
        email_id=email_id,
        evidence_type=EvidenceType.CONTENT_SIGNAL,
        details=details,
        confidence=confidence,
        stage=stage,
    )


CASE_EVIDENCE: dict[CaseType, tuple[str, ...]] = {
    "phishing": ("header_analysis", "link_inspection", "credential_phishing"),
    "vendor_payment_fraud": (
        "payment_change_detection",
        "verification_outcome",
    ),
    "business_email_compromise": (
        "ghost_thread",
        "header_analysis",
        "verification_outcome",
    ),
    "executive_impersonation": (
        "header_analysis",
        "language_pressure",
        "verification_outcome",
    ),
    "invoice_fraud": (
        "pdf_fingerprint",
        "payment_change_detection",
        "verification_outcome",
    ),
    "payroll_diversion": (
        "payroll_diversion_detection",
        "verification_outcome",
    ),
    "ransomware_precursor": (
        "attachment_risk",
        "link_inspection",
        "language_pressure",
    ),
    "cyber_insurance_evidence": ("evidence_package", "verification_outcome"),
    "unknown": ("header_analysis",),
}


@dataclass(frozen=True)
class MissionClassificationInput:
    tenant_id: str
    inputs_digest: str
    source_record_id: uuid.UUID
    classification_policy_version: str
    detector_summary_refs: tuple[str, ...] = ()
    message_id: str | None = None
    forbidden_keys_present: tuple[str, ...] = ()


@dataclass(frozen=True)
class MissionClassification:
    tenant_id: str
    inputs_digest: str
    source_record_id: uuid.UUID
    case_type: CaseType
    review_depth: ReviewDepth
    required_evidence: tuple[str, ...]
    classification_reason_codes: tuple[str, ...]
    classification_policy_version: str
    case_type_confidence: float | None = None
    classification_record_id: uuid.UUID | None = None


@dataclass(frozen=True)
class ClassificationResult:
    kind: ClassificationKind
    classification: MissionClassification | None = None
    refusal: str | None = None


def _normalize_refs(refs: tuple[str, ...]) -> frozenset[str]:
    return frozenset(ref.strip().lower() for ref in refs if ref.strip())


def _case_type_from_refs(refs: frozenset[str]) -> tuple[CaseType, tuple[str, ...]]:
    if "payment_change_detection" in refs or "vendor_payment" in refs:
        return "vendor_payment_fraud", ("policy_match:payment_change_detection",)
    if "credential_phishing" in refs or "credential_reset_language" in refs:
        return "phishing", ("policy_match:credential_phishing",)
    if "ghost_thread" in refs or "business_email_compromise" in refs:
        return "business_email_compromise", ("policy_match:ghost_thread",)
    if "executive_impersonation" in refs or "language_pressure" in refs:
        return "executive_impersonation", ("policy_match:executive_impersonation",)
    if "pdf_fingerprint" in refs or "invoice_fraud" in refs:
        return "invoice_fraud", ("policy_match:pdf_fingerprint",)
    if "payroll_diversion_detection" in refs or "payroll_diversion" in refs:
        return "payroll_diversion", ("policy_match:payroll_diversion",)
    if "attachment_risk" in refs or "ransomware_precursor" in refs:
        return "ransomware_precursor", ("policy_match:ransomware_precursor",)
    if "evidence_package" in refs or "cyber_insurance_evidence" in refs:
        return "cyber_insurance_evidence", ("policy_match:evidence_package",)
    if not refs:
        return "unknown", ("policy_match:insufficient_signal",)
    return "unknown", ("policy_match:unmapped_refs",)


def _review_depth_for(case_type: CaseType) -> ReviewDepth:
    if case_type == "unknown":
        return "human_required"
    if case_type == "ransomware_precursor":
        return "enhanced"
    return "standard"


def _validate_inbound(payload: MissionClassificationInput) -> ClassificationResult | None:
    if payload.forbidden_keys_present:
        return ClassificationResult(kind="refusal", refusal=REFUSAL_ROUTING_KEY)
    if not payload.tenant_id.strip():
        return ClassificationResult(kind="refusal", refusal=REFUSAL_PROVENANCE)
    if not _DIGEST_RE.fullmatch(payload.inputs_digest):
        return ClassificationResult(kind="refusal", refusal=REFUSAL_PROVENANCE)
    if payload.classification_policy_version != CLASSIFICATION_POLICY_VERSION:
        return ClassificationResult(kind="refusal", refusal=REFUSAL_PROVENANCE)
    return None


def classify_case(payload: MissionClassificationInput) -> ClassificationResult:
    refusal = _validate_inbound(payload)
    if refusal is not None:
        return refusal

    refs = _normalize_refs(payload.detector_summary_refs)
    case_type, reason_codes = _case_type_from_refs(refs)
    review_depth = _review_depth_for(case_type)
    confidence = 0.55 if case_type == "unknown" else 0.85

    classification = MissionClassification(
        tenant_id=payload.tenant_id.strip(),
        inputs_digest=payload.inputs_digest,
        source_record_id=payload.source_record_id,
        case_type=case_type,
        review_depth=review_depth,
        required_evidence=CASE_EVIDENCE[case_type],
        classification_reason_codes=reason_codes,
        classification_policy_version=CLASSIFICATION_POLICY_VERSION,
        case_type_confidence=confidence,
        classification_record_id=uuid.uuid4(),
    )
    return ClassificationResult(kind="success", classification=classification)


def format_classification(classification: MissionClassification) -> str:
    evidence = ",".join(classification.required_evidence)
    return (
        f"MISSION_CLASSIFICATION case_type={classification.case_type} "
        f"review_depth={classification.review_depth} "
        f"required_evidence={evidence} "
        f"policy={classification.classification_policy_version}"
    )


def classification_to_observed_facts(
    classification: MissionClassification,
) -> tuple[str, ...]:
    facts: list[str] = [
        f"classification_case_type:{classification.case_type}",
        f"classification_review_depth:{classification.review_depth}",
        f"classification_policy_version:{classification.classification_policy_version}",
    ]
    facts.extend(
        f"classification_required_evidence:{tag}"
        for tag in classification.required_evidence
    )
    facts.extend(
        f"classification_reason_code:{code}"
        for code in classification.classification_reason_codes
    )
    if classification.case_type_confidence is not None:
        facts.append(
            "classification_case_type_confidence:"
            f"{classification.case_type_confidence:.4f}"
        )
    return tuple(facts)


def input_from_context(
    context: MissionContext,
    *,
    detector_summary_refs: tuple[str, ...] = (),
    forbidden_keys_present: tuple[str, ...] = (),
) -> MissionClassificationInput:
    if context.source_record_id is None:
        raise ValueError("MissionContext.source_record_id is required for classification")
    return MissionClassificationInput(
        tenant_id=context.tenant_id,
        inputs_digest=context.inputs_digest,
        source_record_id=context.source_record_id,
        classification_policy_version=CLASSIFICATION_POLICY_VERSION,
        detector_summary_refs=detector_summary_refs,
        forbidden_keys_present=forbidden_keys_present,
    )


class MissionContextAgent:
    """Governed Layer 1 Command classifier — MC-AUTH classify-only."""

    agent_id: str = MISSION_CONTEXT_AGENT_ID
    layer: int = MISSION_CONTEXT_LAYER
    authority_level: int = MISSION_CONTEXT_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        detector_summary_refs: tuple[str, ...] = (),
        forbidden_keys_present: tuple[str, ...] = (),
    ) -> None:
        self._detector_summary_refs = detector_summary_refs
        self._forbidden_keys_present = forbidden_keys_present

    def classify(self, payload: MissionClassificationInput) -> ClassificationResult:
        return classify_case(payload)

    def analyze(self, context: MissionContext) -> AgentContribution:
        payload = input_from_context(
            context,
            detector_summary_refs=self._detector_summary_refs,
            forbidden_keys_present=self._forbidden_keys_present,
        )
        result = self.classify(payload)
        if result.kind == "refusal":
            raise ValueError(result.refusal or REFUSAL_PROVENANCE)
        assert result.classification is not None
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=classification_to_observed_facts(result.classification),
        )

    def map_observations_to_evidence_ledger(
        self,
        *,
        tenant_id: str,
        email_id: str,
        observed_facts: tuple[str, ...],
        confidence: float = 0.5,
    ) -> EvidenceLedgerEntry:
        return map_es1_observations_to_evidence_ledger_entry(
            agent_id=self.agent_id,
            tenant_id=tenant_id,
            email_id=email_id,
            observed_facts=observed_facts,
            confidence=confidence,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None
