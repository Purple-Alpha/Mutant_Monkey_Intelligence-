"""Language Pressure governed-agent wrapper - swarm agent #39.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Language_Pressure_Agent_Design_Contract_Deep_Dive.md`` (2026-06-08, the first
agent selected by the LIVE Build Map). It wraps the pure-function
``core.scoring.callback_phishing_detector.detect_callback_phishing`` (a Layer 2
Detection signal over inbound email body language) and exposes it as an
explicitly wired governed agent on the proven ``Agent`` protocol ->
``AgentContribution`` -> Swarm Commander -> ``DecisionEvidenceRecord`` path
already used by Header Analysis, Ghost Thread, Email Authentication, Link
Inspection, Attachment Risk, Credential Phishing, and MFA Manipulation.

Scope / governance boundary (contract D1-D10, deliberate):
- D2 detector immutability: this wrapper changes no callback-phishing phrase
  category, regex pattern, risk-floor band, schema field, feature flag,
  client-facing rubric projection, rendering wording, or pipeline wiring. The
  detector function is called read-only.
- D3 facts-only contribution: the contribution carries only the closed TOAD v1
  category names (``call_now_pressure``, ``do_not_use_known_channel``,
  ``voice_only_finalize``, ``support_line_substitution``,
  ``payment_redirect_call``) as ``observed_facts``. The numeric
  ``recommended_risk_floor_lift``, the ``out_of_band_verification_required``
  flag, the per-category ``why_this_category`` explanations, and every raw
  matched phrase / body substring / phone-number-shaped string are
  intentionally NOT emitted (Layer 2 emits no interpretation/score field;
  enforced by the ``AgentContribution`` layer-field validator).
- D4 input surface: reads exactly one ``EMAIL_INBOUND`` record via
  ``MissionContext.source_record_id`` and passes ``body_plain`` only, matching
  the signed TOAD v1 detector input boundary (D14, body_plain-only).
- D5 rollout: Evidence Stage 1 - intentionally NOT registered in
  ``build_default_registry``; wired only by explicit callers and tests until a
  separate Matt-signed Stage 2 promotion record (template §6.2).
- D6 Stage A / no autonomy: ``challenge`` returns ``None`` (Pass 2 is a
  Verification / Challenge-layer concern); no disposition, no block/quarantine,
  ``autonomous_action_allowed = False``.
- D8 purity: the wrapper performs no baseline/memory write and no network call;
  the callback-phishing detector is a pure string scanner.
- D9 boundary split from #18: this wrapper produces Layer 2 language facts only.
  It does not verify callback legitimacy, inspect phone numbers, or operate the
  Layer 3 #18 Callback Verification workflow.
"""

from __future__ import annotations

import hashlib
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
from core.scoring.callback_phishing_detector import detect_callback_phishing

from .agent_contract import AgentContribution, ChallengeResult, MissionContext
from .routes import RouteContext, RouteResult, blackboard_path, submit_agent_contribution

LANGUAGE_PRESSURE_AGENT_ID = "language_pressure_001"
LANGUAGE_PRESSURE_LAYER = 2  # Detection
LANGUAGE_PRESSURE_AUTHORITY_LEVEL = 3  # Specialist Agent (matches #6/#8/#10/#21/#23/#24/#27/#30)


def digest_email(payload: EmailInboundPayload) -> str:
    """SHA-256 hex digest of one inbound email for ``MissionContext``."""

    return hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()


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


class LanguagePressureAgent:
    """Governed Layer 2 Detection agent wrapping the callback-phishing detector."""

    agent_id: str = LANGUAGE_PRESSURE_AGENT_ID
    layer: int = LANGUAGE_PRESSURE_LAYER
    authority_level: int = LANGUAGE_PRESSURE_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        blackboard_root: Path,
        environment: Environment = Environment.PRODUCTION,
    ) -> None:
        self._blackboard_root = blackboard_root
        self._environment = environment

    def _load_email(self, context: MissionContext) -> EmailInboundPayload:
        # Agents read the case's record from the Blackboard (MissionContext
        # carries the pointer, not the duplicated email body).
        if context.source_record_id is None:
            raise GovernanceError(
                "LanguagePressureAgent requires MissionContext.source_record_id "
                "to locate the email_inbound record"
            )
        path = blackboard_path(self._blackboard_root, self._environment, context.tenant_id)
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
        # D4: the signed TOAD v1 detector reads body_plain only (D14). D2: the
        # detector is a pure string scanner called read-only - no logic change,
        # no state, no I/O.
        assessment = detect_callback_phishing(body_plain=email.body_plain or "")
        # D3 facts-only Detection contribution: the closed callback/body-language
        # category names only - never the recommended_risk_floor_lift, the
        # out_of_band flag, the per-category explanation, or any raw matched
        # phrase / phone number. The detector already emits categories in a
        # fixed, deduped order (_CATEGORY_ORDER), so the fact tuple is
        # deterministic.
        observed_facts = tuple(
            category.category_name for category in assessment.categories
        )
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=observed_facts,
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        # Detection layer does not run Pass 2.
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
