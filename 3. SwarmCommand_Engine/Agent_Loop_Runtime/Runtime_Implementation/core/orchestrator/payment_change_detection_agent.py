"""Payment Change Detection governed-agent wrapper - swarm agent #14.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Payment_Change_Detection_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08). It
wraps the existing §11-signed ``assess_financial_state_delta`` detector
(Financial State Ledger / Delta Tripwire, Layer 2 Detection over payment-
destination signals with per-tenant Vendor Baseline Store check-before-ingest)
and exposes it as an explicitly wired governed agent on the proven ``Agent``
protocol -> ``AgentContribution`` -> Swarm Commander -> ``DecisionEvidenceRecord``
path.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 stateful boundary: the only authorized mutation is the existing signed
  detector's payment-signal baseline ingest in check-before-ingest order, over
  the existing closed financial-signal enum. The wrapper does not call
  ``check_signal`` / ``ingest_signal`` itself.
- D3 detector/store immutability: this wrapper changes no Financial State Ledger
  detector logic, Vendor Baseline Store behavior, enum, schema, normalization,
  TTL, salt/hash derivation, kill switch, audit behavior, risk floor 85, or
  scoring/rubric behavior. The detector function is injected and called
  read-only from the wrapper's perspective.
- D4/D9 facts-only contribution: the contribution carries only closed payment-
  destination indicator names, closed signal-type facts, and bounded non-
  sensitive counts as ``observed_facts``. The numeric ``recommended_risk_floor``
  (85), ``recommended_action``, ``requires_out_of_band_verification``, explanation,
  verification wording, raw financial strings, normalized values, redacted
  displays, signal hashes, and attachment filenames/indexes are intentionally
  NOT emitted.
- D5 input surface: reads exactly one ``EMAIL_INBOUND`` record via
  ``MissionContext.source_record_id``, uses caller-owned ``vendor_domain`` and
  aware ``now``. No payment-execution data and no raw attachment bytes are read
  by the wrapper.
- D6 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record (template §6.2).
- D7 Stage A / no autonomy: ``challenge`` returns ``None``; no disposition,
  no payment decision, no block/quarantine, ``autonomous_action_allowed = False``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import UUID

from core.blackboard import (
    AgentContributionPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.scoring.financial_state_ledger import (
    FinancialStateLedgerAssessment,
    assess_financial_state_delta,
)

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

PAYMENT_CHANGE_DETECTION_AGENT_ID = "payment_change_detection_001"
PAYMENT_CHANGE_DETECTION_LAYER = 2  # Detection
PAYMENT_CHANGE_DETECTION_AUTHORITY_LEVEL = 3  # Specialist Agent

# D4 closed payment-destination indicator vocabulary allowed in Layer 2 facts.
_INDICATOR_BY_STATE = {
    "new": "new_payment_destination_signal",
    "expired": "expired_payment_destination_signal",
}

# D2 closed financial-signal enum mirrored from the signed detector. The wrapper
# only republishes a signal-type fact when the type is in this closed set.
_ALLOWED_SIGNAL_TYPES = frozenset(
    {
        "routing_number",
        "swift_bic_code",
        "iban",
        "account_number",
        "payment_portal_url",
    }
)

FinancialStateAssessor = Callable[..., FinancialStateLedgerAssessment]


def digest_email(payload: EmailInboundPayload) -> str:
    """SHA-256 hex digest of one inbound email for ``MissionContext``."""

    return hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()


def _contribution_facts(assessment: FinancialStateLedgerAssessment) -> tuple[str, ...]:
    """Map a detector assessment to the facts-only Layer 2 contribution tuple.

    Emits only D3/§3 vocabulary: closed payment-destination indicator names,
    closed signal-type facts, and bounded counts. No risk floor, action,
    verification wording, raw financial string, redacted display, or hash.
    """

    facts: list[str] = []
    seen: set[str] = set()
    for finding in assessment.findings:
        indicator = _INDICATOR_BY_STATE.get(finding.baseline_state)
        if indicator is not None and indicator not in seen:
            seen.add(indicator)
            facts.append(indicator)
        if finding.signal_type in _ALLOWED_SIGNAL_TYPES:
            type_fact = f"payment_signal_type:{finding.signal_type}"
            if type_fact not in seen:
                seen.add(type_fact)
                facts.append(type_fact)
    extracted_count = len(assessment.extracted_signals)
    finding_count = len(assessment.findings)
    facts.append(f"payment_signal_extracted_count:{extracted_count}")
    facts.append(f"payment_delta_finding_count:{finding_count}")
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


class PaymentChangeDetectionAgent:
    """Governed Layer 2 Detection agent wrapping payment-destination delta detection."""

    agent_id: str = PAYMENT_CHANGE_DETECTION_AGENT_ID
    layer: int = PAYMENT_CHANGE_DETECTION_LAYER
    authority_level: int = PAYMENT_CHANGE_DETECTION_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        vendor_domain: str,
        now: datetime,
        environment: Environment = Environment.PRODUCTION,
        assessor: FinancialStateAssessor = assess_financial_state_delta,
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
                "PaymentChangeDetectionAgent requires MissionContext.source_record_id "
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
