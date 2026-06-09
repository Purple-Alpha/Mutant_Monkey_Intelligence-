"""PDF Fingerprint governed-agent wrapper - swarm agent #31.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``PDF_Fingerprint_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It wraps
the existing signed ``assess_document_metadata_fingerprint`` detector (Layer 2
Detection over upstream PDF Producer/Creator metadata with per-tenant Vendor
Baseline Store check-before-ingest) and exposes it as an explicitly wired
governed agent on the proven ``Agent`` protocol ->
``AgentContribution`` -> Swarm Commander -> ``DecisionEvidenceRecord`` path.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 stateful boundary: the only authorized mutation is the existing signed
  detector's ``pdf_producer_fingerprint`` baseline ingest in check-before-ingest
  order. The wrapper does not call ``check_signal`` / ``ingest_signal`` itself.
- D3 detector/store immutability: this wrapper changes no document-metadata
  detector logic, Vendor Baseline Store behavior, enum, schema, normalization,
  TTL, salt/hash derivation, kill switch, audit behavior, scoring/rubric
  behavior, or pipeline wiring. The detector function is injected and called
  read-only from the wrapper's perspective.
- D4 facts-only contribution: the contribution carries only closed document-
  metadata indicator names and bounded non-sensitive counts as
  ``observed_facts``. The numeric ``recommended_risk_floor``, ``recommended_action``,
  explanation, verification wording, raw Producer/Creator values, redacted
  display, filenames, attachment indexes, and signal hashes are intentionally
  NOT emitted.
- D5 input surface: reads exactly one ``EMAIL_INBOUND`` record via
  ``MissionContext.source_record_id``, uses caller-owned ``vendor_domain`` and
  aware ``now``. No raw PDF bytes are read by the wrapper.
- D6 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record (template §6.2).
- D7 Stage A / no autonomy: ``challenge`` returns ``None``; no disposition,
  no block/quarantine, ``autonomous_action_allowed = False``.
- D9 metadata-only inspection: the wrapper never parses PDF bytes, fetches
  files, OCRs, detonates, uses reputation, or performs network/subprocess
  calls; it relies only on upstream bounded ``pdf_metadata``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from uuid import UUID

from core.blackboard import (
    AgentContributionPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.scoring.document_metadata_detector import (
    DocumentMetadataAssessment,
    assess_document_metadata_fingerprint,
)

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

PDF_FINGERPRINT_AGENT_ID = "pdf_fingerprint_001"
PDF_FINGERPRINT_LAYER = 2  # Detection
PDF_FINGERPRINT_AUTHORITY_LEVEL = 3  # Specialist Agent

# D4 closed document-metadata indicator vocabulary allowed in Layer 2 facts.
_ALLOWED_INDICATORS = frozenset(
    {
        "new_pdf_producer_fingerprint",
        "expired_pdf_producer_fingerprint",
    }
)

DocumentMetadataAssessor = type(assess_document_metadata_fingerprint)


def digest_email(payload: EmailInboundPayload) -> str:
    """SHA-256 hex digest of one inbound email for ``MissionContext``."""

    return hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()


def _contribution_facts(assessment: DocumentMetadataAssessment) -> tuple[str, ...]:
    """Map a detector assessment to the facts-only Layer 2 contribution tuple."""

    facts: list[str] = []
    seen: set[str] = set()
    for indicator in assessment.indicators:
        if indicator not in _ALLOWED_INDICATORS or indicator in seen:
            continue
        seen.add(indicator)
        facts.append(indicator)
    extracted_count = len(assessment.extracted_fingerprints)
    finding_count = len(assessment.findings)
    facts.append(f"document_metadata_extracted_count:{extracted_count}")
    facts.append(f"document_metadata_finding_count:{finding_count}")
    return tuple(facts)


def contribution_payload_from(
    contribution: AgentContribution,
    *,
    case_id: UUID,
    inputs_digest: str,
) -> AgentContributionPayload:
    """Map an already-validated ``AgentContribution`` to its persistence payload."""

    return AgentContributionPayload(
        case_id=case_id,
        inputs_digest=inputs_digest,
        agent_id=contribution.agent_id,
        layer=contribution.layer,
        observed_facts=list(contribution.observed_facts),
        verification_source=contribution.verification_source,
        verification_outcome=contribution.verification_outcome,
        challenge_result=contribution.challenge_result,
        challenge_rationale=contribution.challenge_rationale,
        control_mapping=contribution.control_mapping,
        underwriter_note=contribution.underwriter_note,
    )


class PDFFingerprintAgent:
    """Governed Layer 2 Detection agent wrapping document-metadata fingerprinting."""

    agent_id: str = PDF_FINGERPRINT_AGENT_ID
    layer: int = PDF_FINGERPRINT_LAYER
    authority_level: int = PDF_FINGERPRINT_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        vendor_domain: str,
        now: datetime,
        environment: Environment = Environment.PRODUCTION,
        assessor: DocumentMetadataAssessor = assess_document_metadata_fingerprint,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._vendor_domain = vendor_domain
        self._now = now
        self._environment = environment
        # Injected so the read-only detector dependency is explicit and the
        # check-before-ingest / purity tests can substitute it.
        self._assessor = assessor

    def _load_email(self, context: MissionContext) -> EmailInboundPayload:
        if context.source_record_id is None:
            raise GovernanceError(
                "PDFFingerprintAgent requires MissionContext.source_record_id "
                "to locate the email_inbound record"
            )
        path = blackboard_path(
            self._blackboard_root, self._environment, context.tenant_id
        )
        for record in read_records(path):
            if record.record_id == context.source_record_id:
                if record.record_type != RecordType.EMAIL_INBOUND:
                    raise GovernanceError(
                        f"source record {context.source_record_id} is "
                        f"{record.record_type.value!r}, not an email_inbound record"
                    )
                return EmailInboundPayload.model_validate(record.payload)
        raise GovernanceError(
            f"email_inbound record {context.source_record_id} not found for "
            f"tenant {context.tenant_id!r}"
        )

    def analyze(self, context: MissionContext) -> AgentContribution:
        email = self._load_email(context)
        assessment = self._assessor(
            tenant_id=context.tenant_id,
            vendor_domain=self._vendor_domain,
            email=email,
            now=self._now,
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=_contribution_facts(assessment),
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None

    def persist_contribution(
        self,
        route_context: RouteContext,
        context: MissionContext,
        contribution: AgentContribution,
    ) -> RouteResult:
        """Write this agent's contribution via the approved registry-gated route."""

        payload = contribution_payload_from(
            contribution,
            case_id=context.case_id,
            inputs_digest=context.inputs_digest,
        )
        return submit_agent_contribution(
            route_context,
            tenant_id=context.tenant_id,
            environment=self._environment,
            source_agent=self.agent_id,
            payload=payload,
            parent_record_id=context.source_record_id,
        )
