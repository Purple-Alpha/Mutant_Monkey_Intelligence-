"""Pydantic models for the NorthStar Blackboard prototype.

The Blackboard is append-only. These models define the first record envelope,
payloads, and governance checks that every agent write must pass.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Literal, TypeAlias
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Environment(str, Enum):
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class RecordType(str, Enum):
    INGEST_EVENT = "ingest_event"
    DETECTION_RESULT = "detection_result"
    RISK_SCORE = "risk_score"
    WORKFLOW_TRIGGER = "workflow_trigger"
    AUDIT_VERDICT = "audit_verdict"
    WEAKNESS_REPORT = "weakness_report"
    SYNTHETIC_ATTACK_CASE = "synthetic_attack_case"
    SYNTHETIC_EMAIL_ATTACK_CASE = "synthetic_email_attack_case"
    MUTANT_EVALUATION = "mutant_evaluation"
    POLICY_UPDATE = "policy_update"
    EMAIL_INBOUND = "email_inbound"
    EMAIL_ANALYSIS = "email_analysis"
    EMAIL_ANALYSIS_FAILURE = "email_analysis_failure"
    DAILY_DIGEST = "daily_digest"
    EFFECTIVE_PARAMETERS_REPORT = "effective_parameters_report"
    VENDOR_BASELINE_AUDIT = "vendor_baseline_audit"
    TWO_CHANNEL_CONFIRMATION = "two_channel_confirmation"


class AuditStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DETECTION = "detection"
    SCORING = "scoring"
    WORKFLOW = "workflow"
    DRAFTING = "drafting"
    AUDIT = "audit"
    RED = "red"
    BLUE = "blue"
    GOVERNANCE = "governance"


class GovernanceError(ValueError):
    """Raised when a record violates runtime guardrails."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuditMeta(StrictModel):
    status: AuditStatus = AuditStatus.PENDING
    auditor: str | None = None
    signed: bool = False
    signature_id: str | None = None
    reviewed_at: datetime | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def require_signature_id_when_signed(self) -> AuditMeta:
        if self.signed and not self.signature_id:
            raise ValueError("signature_id is required when signed is true")
        return self


class BlackboardRecord(StrictModel):
    record_id: UUID = Field(default_factory=uuid4)
    tenant_id: str = Field(min_length=1)
    environment: Environment
    record_type: RecordType
    source_agent: str = Field(min_length=1)
    workflow_id: str | None = None
    parent_record_id: UUID | None = None
    hop_count: int = Field(default=0, ge=0, le=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: str = "v1"
    payload: dict[str, Any]
    audit: AuditMeta = Field(default_factory=AuditMeta)


class IngestEventPayload(StrictModel):
    source: str
    event_kind: str
    subject: str | None = None
    sender_domain: str | None = None
    received_at: datetime
    raw_ref: str | None = None


class DetectionResultPayload(StrictModel):
    detection_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    signals: list[str] = Field(default_factory=list)
    explanation: str | None = None


class RiskScorePayload(StrictModel):
    score: int = Field(ge=0, le=100)
    risk_level: str
    factors: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


class WorkflowTriggerPayload(StrictModel):
    workflow_name: str
    reason: str
    priority: str = "normal"
    target_agent_role: AgentRole | None = None


class AuditVerdictPayload(StrictModel):
    target_record_id: UUID
    verdict: AuditStatus
    findings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class VendorBaselineAuditPayload(StrictModel):
    event_type: Literal["vendor_baseline_signal_ingested", "vendor_baseline_cleanup"]
    vendor_domain: str | None = None
    signal_type: str | None = None
    signal_hash: str | None = None
    rows_affected: int = Field(default=0, ge=0)
    reason: str


TwoChannelEventType = Literal["pending", "outcome"]
TwoChannelOutcomeStatus = Literal[
    "confirmed", "rejected", "unable_to_verify", "expired"
]
TwoChannelChannelKind = Literal[
    "previously_known_phone",
    "previously_known_in_person",
    "previously_known_video_call",
    "previously_known_internal_system",
    "other_documented",
]


class TwoChannelConfirmationPayload(StrictModel):
    """Append-only two-channel confirmation event.

    Two values of ``event_type``:
    - ``pending``: written when a detector raises a finding that requires
      out-of-band verification.
    - ``outcome``: written exactly once per ``finding_id`` after the operator
      records the result of the verification attempt.
    """

    event_type: TwoChannelEventType
    finding_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    detector: str = Field(min_length=1, max_length=128)
    recommended_action: Literal["needs_review"]
    risk_floor: int = Field(ge=0, le=100)
    requested_at: datetime | None = None
    requested_by: str | None = Field(default=None, max_length=128)
    outcome_at: datetime | None = None
    outcome_by: str | None = Field(default=None, max_length=128)
    outcome_status: TwoChannelOutcomeStatus | None = None
    channel_kind: TwoChannelChannelKind | None = None
    channel_description: str | None = Field(default=None, max_length=256)
    reason: str | None = Field(default=None, max_length=512)


class WeaknessReportPayload(StrictModel):
    weakness_kind: str
    anonymized_pattern: str
    confidence_gap: float = Field(ge=0.0, le=1.0)
    source_record_ids: list[UUID] = Field(default_factory=list)
    raw_tenant_data_removed: bool = True

    @model_validator(mode="after")
    def require_tenant_data_removal(self) -> WeaknessReportPayload:
        if not self.raw_tenant_data_removed:
            raise ValueError("weakness reports must remove raw tenant data")
        return self


class SyntheticAttackCasePayload(StrictModel):
    attack_kind: str
    generated_from_weakness_id: UUID
    synthetic_subject: str
    synthetic_sender_domain: str
    expected_detection_signals: list[str] = Field(default_factory=list)
    raw_tenant_data_removed: bool = True

    @model_validator(mode="after")
    def require_tenant_data_removal(self) -> SyntheticAttackCasePayload:
        if not self.raw_tenant_data_removed:
            raise ValueError("synthetic attack cases must remove raw tenant data")
        return self


class Phase13FailureDetail(StrictModel):
    """One Phase 1.3 typed failure record.

    ``failure_mode`` is one of the eight canonical strings in
    ``Phase13FailureMode``. ``dynamic_detail`` carries the per-case
    specifics (e.g. the missing ``BehavioralDeviationFlag`` value, the
    unexpected recommended action, or a ``"<actual><cmp><bound>"`` string
    for numerical comparisons). Storing the dynamic detail separately from
    the mode keeps the enum strict while preserving the diagnostic value
    that the Month 0 freeform tag list previously provided.
    """

    failure_mode: Phase13FailureMode
    dynamic_detail: str | None = None


class MutantEvaluationPayload(StrictModel):
    """Per-case Blue evaluation result against one synthetic attack case.

    ``failure_modes`` is the legacy freeform tag list used by the Month 0
    sandbox loop (still in use for the Bucket E backlog work). Phase 1.3
    (Month 4) layers a strict, enum-typed view on top via
    ``phase_1_3_failure_details``: every entry there carries a closed
    ``Phase13FailureMode`` plus an optional ``dynamic_detail`` field, so the
    eight canonical mode strings stay drift-free while the diagnostic
    payload (the specific missing flag, indicator, action, etc.) lives on
    a sibling field — per Matt's 2026-05-21 §11 decision 4.

    The two views coexist intentionally: Month 5 mutation planning consumes
    ``phase_1_3_failure_details`` for typed bucket counts; legacy sandbox
    code paths keep working with ``failure_modes``. Phase 1.3 Red battery
    cycles populate both (the freeform list mirrors the typed details so
    older log readers still see something useful).
    """

    baseline_agent_id: str
    candidate_agent_id: str | None = None
    source_attack_case_id: UUID
    blue_detected: bool
    baseline_confidence: float = Field(ge=0.0, le=1.0)
    failure_modes: list[str] = Field(default_factory=list)
    mutation_recommended: bool = False
    phase_1_3_failure_details: list[Phase13FailureDetail] = Field(default_factory=list)


class PolicyUpdatePayload(StrictModel):
    policy_name: str
    change_summary: str
    sandbox_evidence_ids: list[UUID] = Field(default_factory=list)
    rollout_scope: str = "manual_review"
    rollback_plan: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    is_rollback: bool = False
    # The production tenant this signed update is allowed to promote into.
    # Signed alongside the rest of the payload so any tamper is caught by
    # the promotion-pipeline + Guardrail 11 gate signature re-verification.
    # Default ``"tenant_demo"`` keeps the legacy demo flow unchanged; new
    # tenants set this explicitly via the mutation engine / rollback module
    # / submission helper.
    target_production_tenant_id: str = Field(default="tenant_demo", min_length=1)


# ---------------------------------------------------------------------------
# NorthStar Inbox Shield record types
#
# These payloads are the locked schema for the NorthStar Inbox Shield product
# slotted on top of the existing Blue loop. They follow the same convention as
# every other payload in this module: pydantic StrictModel (extra forbidden)
# so disk-load rejects unauthorized fields, JSON-friendly types only, and the
# Blackboard envelope (BlackboardRecord) carries tenant_id / record_id rather
# than duplicating them inside the payload.
#
# Naming note: the source brief refers to these as "Record" types
# (EmailInboundRecord, EmailAnalysisRecord, ...). We name them "*Payload" to
# match the long-standing pattern in this file (IngestEventPayload,
# DetectionResultPayload, ...). The BlackboardRecord envelope plus payload
# together constitute the record-on-disk.
#
# NORTHSTAR_MAX_SUMMARY_CHARS is the soft cap consistent with the system
# prompt rule "Keep summaries under 3 sentences." ~600 characters is the
# operational ceiling we enforce; downstream agents may further trim.
# ---------------------------------------------------------------------------

NORTHSTAR_MAX_SUMMARY_CHARS = 600
NORTHSTAR_MAX_ACTION_ITEMS = 5

# Soft cap on per-attachment extracted text. Picked to comfortably hold an
# invoice / short letter (~1-2 pages) while keeping the JSONL blackboard
# small. Deep-inspection agents that produce more text must truncate at
# this boundary themselves so this validator only ever fires as a guard.
NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS = 8000

FinancialRiskLevel: TypeAlias = Literal["low", "medium", "high"]
RecommendedEmailAction: TypeAlias = Literal["safe", "needs_review", "block"]
EffectiveParameterSource: TypeAlias = Literal["signed_policy", "tenant_override"]

# Attachment classes used by Phase 1.2 Ransomware Precursor Detection and
# Phase 1.1 Vendor / Invoice fraud detection. Kept deliberately small; we
# can grow this set only by changing the schema, which forces a versioned
# rollout and prevents agents from inventing freeform classes.
AttachmentClass: TypeAlias = Literal[
    "invoice",
    "payment_request",
    "credential_lure",
    "payload_carrier",
    "executable_doc",
    "unknown",
]

# Behavioral deviation flags surfaced by the Inbox Shield scoring agent under
# Phase 1.1 Vendor / Invoice fraud detection. Same schema-versioned pattern
# as ``AttachmentClass``: the agent cannot invent freeform flags, the set
# can only grow via a deliberate schema change. The first eight values
# match Phase_1_1_Fraud_Prevention_Deep_Dive.md §2.4 verbatim; the
# ninth value was added after the 40-case eval dataset design grid surfaced
# three Unicode-obfuscation cases that needed a locked-enum home.
BehavioralDeviationFlag: TypeAlias = Literal[
    "new_banking_instructions",
    "out_of_band_pressure",
    "unusual_dollar_amount",
    "lookalike_sender_domain",
    "reply_to_diverges_from_from",
    "mismatched_invoice_vendor_name",
    "first_time_sender_with_financial_ask",
    "urgency_paired_with_finance",
    "unusual_unicode_obfuscation",
]

# Ransomware precursor indicators surfaced by the deterministic detectors in
# ``core/precursor/`` under Phase 1.2 Ransomware Precursor Detection. Same
# schema-versioned pattern as ``BehavioralDeviationFlag`` and
# ``AttachmentClass``: the detectors cannot invent freeform indicators, and
# the set can only grow via a deliberate schema change.
#
# Detector mapping (one of the four sub-scores can emit each indicator):
# - attachment_classifier:
#   "macro_enabled_office_document", "executable_attachment",
#   "iso_or_disk_image_attachment", "double_extension_attachment",
#   "encrypted_archive_attachment", "html_smuggling_attachment"
# - url_obfuscation_detector:
#   "credential_bearing_url", "url_shortener_present", "punycode_url_present",
#   "homoglyph_url_present", "suspicious_tld_present",
#   "ip_address_url_present", "login_path_url_present"
# - body_signal_detector (credential harvesting):
#   "credential_reset_language", "account_verification_language"
# - body_signal_detector (mfa fatigue):
#   "mfa_push_language", "verification_code_language"
PrecursorIndicator: TypeAlias = Literal[
    "macro_enabled_office_document",
    "executable_attachment",
    "iso_or_disk_image_attachment",
    "double_extension_attachment",
    "encrypted_archive_attachment",
    "html_smuggling_attachment",
    "credential_bearing_url",
    "url_shortener_present",
    "punycode_url_present",
    "homoglyph_url_present",
    "suspicious_tld_present",
    "ip_address_url_present",
    "login_path_url_present",
    "credential_reset_language",
    "account_verification_language",
    "mfa_push_language",
    "verification_code_language",
]


# Phase 1.3 Sandbox Training Pit (Month 4). Same schema-versioning discipline
# as ``BehavioralDeviationFlag`` / ``PrecursorIndicator``: the eight canonical
# failure modes are pinned in a closed ``Literal`` so weakness-report bucket
# counts stay typed end-to-end. Per Matt's 2026-05-21 §11 decision 4, the
# dynamic part of a failure (the specific missing flag, missing indicator,
# unexpected action, or numerical comparison) lives on
# ``Phase13FailureDetail.dynamic_detail``, **not** glued onto the mode string.
# See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` §5.3.
Phase13FailureMode: TypeAlias = Literal[
    "analysis_failure_record_written",
    "unexpected_blue_exception",
    "risk_score_below_floor",
    "risk_score_above_ceiling",
    "missing_behavioral_flag",
    "missing_precursor_indicator",
    "recommended_action_unexpected",
    "precursor_block_missing",
]

# Phase 1.3 case tags. Closed Literal so Red profiles cannot invent freeform
# tag strings. Initial set is the single Bucket E mirror tag approved by Matt
# in §11 decision 5; the Literal is intentionally growable (additive only) so
# later mutation passes can introduce additional regression-probe tags
# without losing typing.
Phase13CaseTag: TypeAlias = Literal["bucket_e_regression_probe"]

# Phase 1.3 archetype, pinned to the four Red profiles from
# Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md §1.
Phase13CaseArchetype: TypeAlias = Literal[
    "fake_invoice",
    "vendor_update_pivot",
    "malicious_attachment",
    "obfuscated_url",
]

# Phase 1.4 Mutation Engine Specialisation (Month 5). Six-value closed
# ``Literal`` per Matt's 2026-05-21 §11 decision 1. The first two values
# (``add_missing_signal_heuristic``, ``raise_confidence_weighting``) are
# the Month 0 legacy kinds and remain unchanged so the legacy
# ``run_mutation_cycle`` path keeps emitting the same signed payloads.
# The next three (``fraud_pattern_threshold``,
# ``attachment_classifier_boost``, ``url_obfuscation_sensitivity``) are
# the Phase 1.4 fraud-specialised kinds, each gated on the matching
# ``Phase13CaseArchetype`` per §2.2 of the Phase 1.4 deep dive. The
# sentinel ``no_mutation`` value preserves the existing
# "no_supported_failure_mode" retirement path on the legacy code path so
# the legacy mutation-engine tests do not regress. See
# ``4. Product_Roadmap/Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md`` §5.1.
MutationKind: TypeAlias = Literal[
    "add_missing_signal_heuristic",
    "raise_confidence_weighting",
    "fraud_pattern_threshold",
    "attachment_classifier_boost",
    "url_obfuscation_sensitivity",
    "no_mutation",
]

# Reserved namespaces used by every Phase 1.3 synthetic case. The
# ``SyntheticEmailAttackCasePayload`` validator below rejects any sender or
# recipient address that does not live in one of these TLDs, so the sandbox
# can never generate plausibly-real identifiers. See deep dive §2.5.
_PHASE_1_3_RESERVED_TLDS: tuple[str, ...] = (".example", ".test", ".invalid")


class PdfAttachmentMetadata(StrictModel):
    """Bounded PDF document metadata from an upstream safe extractor.

    v1 Document Metadata Fingerprinting consumes only these fields. The
    runtime does not parse PDF bytes in this lane.
    """

    producer: str | None = Field(default=None, max_length=512)
    creator: str | None = Field(default=None, max_length=512)


class EmailAttachmentMeta(StrictModel):
    """Per-attachment metadata captured by the email ingest stub.

    Body bytes are intentionally not stored here; this is metadata only so
    the JSONL blackboard stays small. A future attachment sandbox can be
    referenced by ``content_ref`` (e.g. opaque storage key).

    ``extracted_text`` is the safely-extracted text body of the attachment
    (e.g. text layer of a PDF, plain-text content of a .docx, OCR output).
    It is bounded by ``NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS`` so a single
    pathological attachment cannot inflate the blackboard. Deep inspection
    is opt-in: the ingest stub leaves this ``None`` and a downstream
    inspector populates it.

    ``pdf_metadata`` is populated by an upstream PDF metadata extractor
    (outside product runtime in v1). Document Metadata Fingerprinting reads
    Producer/Creator only; no raw PDF bytes are stored on the blackboard.

    ``attachment_class`` is the coarse classification used by Inbox Shield
    scoring and the daily digest to drive Fraud + Ransomware reasoning
    (vendor invoice fraud, credential lures, executable payloads, etc.).
    Defaults to ``"unknown"`` so the ingest stub does not have to guess.
    """

    filename: str
    content_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    content_ref: str | None = None
    sha256: str | None = None
    extracted_text: str | None = None
    pdf_metadata: PdfAttachmentMetadata | None = None
    attachment_class: AttachmentClass = "unknown"

    @model_validator(mode="after")
    def cap_extracted_text_length(self) -> "EmailAttachmentMeta":
        if (
            self.extracted_text is not None
            and len(self.extracted_text) > NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS
        ):
            raise ValueError(
                "extracted_text exceeds soft cap "
                f"({len(self.extracted_text)} > "
                f"{NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS} characters)"
            )
        return self


class EmailInboundPayload(StrictModel):
    """One inbound email captured by the (future) ingest path.

    The Blackboard envelope already carries ``tenant_id`` and ``record_id``;
    they are not duplicated here. ``received_at`` distinguishes when the
    sender's MTA stamped the message from when the Blackboard wrote it
    (``BlackboardRecord.created_at``).
    """

    received_at: datetime
    sender: str = Field(min_length=1)
    recipient: str = Field(min_length=1)
    subject: str | None = None
    body_plain: str
    body_html: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    received_headers: list[str] = Field(default_factory=list)
    attachments: list[EmailAttachmentMeta] = Field(default_factory=list)


class EmailAnalysisActionItem(StrictModel):
    """One action item extracted from an email by Inbox Shield."""

    task: str = Field(min_length=1)
    owner: str | None = None
    due_date: date | None = None


class EmailAnalysisRiskAnalysis(StrictModel):
    """Scored risk dimensions produced by the Inbox Shield scoring agent.

    The first five fields (``risk_score`` through ``financial_risk``) are the
    Month 1 baseline. The four trailing fields landed in Month 2 (Phase 1.1
    Vendor / Invoice fraud detection) per
    ``4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md`` §2:

    - ``vendor_fraud_score``: 0–100; higher means more vendor-fraud signal.
    - ``wire_transfer_anomaly_score``: 0–100; higher means more wire-fraud
      signal.
    - ``invoice_authenticity_score``: 0–100 **or** ``None``. Inverted vs the
      others — high means *more* authentic. ``None`` when no invoice
      attachment is present (the agent must not guess).
    - ``behavioral_deviation_flags``: schema-versioned controlled enum list
      (see :data:`BehavioralDeviationFlag`).

    All four new fields are part of the strict ``extra="forbid"`` schema, so
    an agent that emits an unknown behavioral flag or an out-of-range score
    fails validation rather than silently writing it onto the blackboard.
    """

    risk_score: int = Field(ge=0, le=100)
    risk_factors: list[str] = Field(default_factory=list)
    phishing_signals: list[str] = Field(default_factory=list)
    urgency_signals: list[str] = Field(default_factory=list)
    financial_risk: FinancialRiskLevel
    vendor_fraud_score: int = Field(ge=0, le=100)
    wire_transfer_anomaly_score: int = Field(ge=0, le=100)
    invoice_authenticity_score: int | None = Field(default=None, ge=0, le=100)
    behavioral_deviation_flags: list[BehavioralDeviationFlag] = Field(
        default_factory=list
    )


class EmailAnalysisImpersonationAnalysis(StrictModel):
    impersonation_likelihood: int = Field(ge=0, le=100)
    suspicious_elements: list[str] = Field(default_factory=list)
    sender_legitimacy_notes: str | None = None


class EmailAnalysisRansomwarePrecursorAnalysis(StrictModel):
    """Deterministic ransomware-precursor scoring overlay.

    Landed in Month 3 (Phase 1.2 Ransomware Precursor Detection) per
    ``4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md``. Unlike
    ``EmailAnalysisRiskAnalysis``, this block is **not** produced by the LLM —
    it is computed by the deterministic detectors in ``core/precursor/`` and
    overlaid onto the LLM analysis by ``run_email_risk_scoring_cycle`` post
    LLM validation.

    Sub-scores are 0–100 and additive: zero means "no signal of this kind".
    ``precursor_indicators`` is the controlled-enum list explaining which
    individual signals fired. Same schema-versioning discipline as
    ``BehavioralDeviationFlag``: detectors cannot invent freeform indicators.

    The block is optional on ``EmailAnalysisPayload`` so existing Month 1 /
    Month 2 fixtures that construct payloads directly without precursor data
    continue to validate. Production paths going forward always overlay a
    non-``None`` block (zero sub-scores when there is no precursor signal).
    """

    attachment_risk_score: int = Field(ge=0, le=100)
    url_obfuscation_score: int = Field(ge=0, le=100)
    credential_harvesting_score: int = Field(ge=0, le=100)
    mfa_fatigue_score: int = Field(ge=0, le=100)
    precursor_indicators: list[PrecursorIndicator] = Field(default_factory=list)


class EmailAnalysisPayload(StrictModel):
    """Structured output of the NorthStar Inbox Shield scoring agent.

    ``source_email_record_id`` is the foreign key to the ``EmailInboundPayload``
    record this analysis was produced from. Cross-record integrity is enforced
    by the scoring agent, not by this payload schema.

    ``ransomware_precursor_analysis`` is the Phase 1.2 deterministic overlay
    (see :class:`EmailAnalysisRansomwarePrecursorAnalysis`). Optional to keep
    backward compatibility with Month 1 / Month 2 fixtures that did not carry
    the field; production scoring overlays it after LLM validation.
    """

    source_email_record_id: UUID
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: str | None = None
    action_items: list[EmailAnalysisActionItem] = Field(
        default_factory=list, max_length=NORTHSTAR_MAX_ACTION_ITEMS
    )
    risk_analysis: EmailAnalysisRiskAnalysis
    impersonation_analysis: EmailAnalysisImpersonationAnalysis
    recommended_action: RecommendedEmailAction
    ransomware_precursor_analysis: EmailAnalysisRansomwarePrecursorAnalysis | None = (
        None
    )
    tenant_default_profile: Literal["low", "medium", "high"] | None = None
    effective_profile: Literal["low", "medium", "high"] | None = None
    forced_escalation_triggers: list[
        Literal[
            "llm_high_risk_score",
            "header_divergence_strong",
            "ghost_thread_detected",
            "manual_operator_escalation",
        ]
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def cap_summary_length(self) -> EmailAnalysisPayload:
        if self.summary is not None and len(self.summary) > NORTHSTAR_MAX_SUMMARY_CHARS:
            raise ValueError(
                "summary exceeds soft cap "
                f"({len(self.summary)} > {NORTHSTAR_MAX_SUMMARY_CHARS} characters)"
            )
        return self


class EmailAnalysisFailurePayload(StrictModel):
    """Failure record written when the LLM produced output that failed schema validation.

    ``raw_output`` is preserved verbatim so a human or downstream automation
    can later inspect what went wrong without round-tripping through the LLM
    again. ``failure_reason`` is a short machine-friendly tag (e.g.
    ``invalid_json``, ``schema_mismatch``).
    """

    source_email_record_id: UUID
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_output: str
    failure_reason: str = Field(min_length=1)


class DailyDigestEmailEntry(StrictModel):
    """One row of the ``important_emails`` section of a daily digest."""

    source_email_record_id: UUID
    source_analysis_record_id: UUID
    subject: str | None = None
    sender: str | None = None
    summary: str | None = None
    action_items: list[EmailAnalysisActionItem] = Field(default_factory=list)
    risk_score: int = Field(ge=0, le=100)
    tenant_default_profile: Literal["low", "medium", "high"] | None = None
    effective_profile: Literal["low", "medium", "high"] | None = None
    forced_escalation_triggers: list[
        Literal[
            "llm_high_risk_score",
            "header_divergence_strong",
            "ghost_thread_detected",
            "manual_operator_escalation",
        ]
    ] = Field(default_factory=list)


class DailyDigestRiskEntry(StrictModel):
    """One row of the ``top_risks`` section of a daily digest."""

    source_email_record_id: UUID
    source_analysis_record_id: UUID
    subject: str | None = None
    sender: str | None = None
    risk_score: int = Field(ge=0, le=100)
    reason: str | None = None
    tenant_default_profile: Literal["low", "medium", "high"] | None = None
    effective_profile: Literal["low", "medium", "high"] | None = None
    forced_escalation_triggers: list[
        Literal[
            "llm_high_risk_score",
            "header_divergence_strong",
            "ghost_thread_detected",
            "manual_operator_escalation",
        ]
    ] = Field(default_factory=list)


class DailyDigestTaskEntry(StrictModel):
    """One row of the ``tasks`` section of a daily digest."""

    task: str = Field(min_length=1)
    owner: str | None = None
    due_date: date | None = None
    parent_subject: str | None = None
    parent_sender: str | None = None
    parent_risk_score: int = Field(ge=0, le=100)
    source_email_record_id: UUID | None = None
    source_analysis_record_id: UUID | None = None


class DailyDigestPayload(StrictModel):
    """Aggregate daily digest produced by the NorthStar drafting layer.

    Stores both the structured aggregate (so downstream consumers can reuse
    the data) and the LLM-rendered ``digest_markdown`` (so the eventual
    delivery integration just needs to embed the markdown body).
    """

    digest_date: date
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    important_emails: list[DailyDigestEmailEntry] = Field(default_factory=list)
    top_risks: list[DailyDigestRiskEntry] = Field(default_factory=list)
    tasks: list[DailyDigestTaskEntry] = Field(default_factory=list)
    digest_markdown: str | None = None


class EffectiveParameterProvenance(StrictModel):
    """Per-parameter source trace for evidence-package visibility."""

    parameter_name: str = Field(min_length=1)
    signed_policy_value: Any | None = None
    override_value: int | None = None
    effective_value: Any | None = None
    source: EffectiveParameterSource


class EffectiveParametersReportPayload(StrictModel):
    """Read-only report of signed baseline vs tenant override overlay."""

    tenant_id: str = Field(min_length=1)
    evaluated_at: datetime
    policy_active_version: str = Field(min_length=1)
    override_status: str | None = None
    override_applied: bool = False
    override_reason: str | None = None
    override_requested_by: str | None = None
    override_approved_by: str | None = None
    override_created_at: datetime | None = None
    override_expires_at: datetime | None = None
    latest_audit_event_type: str | None = None
    latest_audit_event_timestamp: datetime | None = None
    latest_audit_event_source: str | None = None
    parameter_provenance: list[EffectiveParameterProvenance] = Field(default_factory=list)
    client_summary: str = Field(min_length=1)


class SyntheticEmailAttackCasePayload(StrictModel):
    """One Phase 1.3 sandbox-only synthetic email attack case.

    Carries a fully-formed ``EmailInboundPayload`` (so Blue scoring is a
    pure function call on the same shape as production) plus the typed
    expectations that the per-case Blue evaluation will check against.
    Expectations are intentionally an optional subset: an empty
    ``expected_behavioral_flags`` tuple means "no required flag for this
    case"; ``expected_max_risk_score is None`` means "no ceiling".

    All identifiers in ``inbound.sender`` and ``inbound.recipient`` must
    live in the reserved ``.example`` / ``.test`` / ``.invalid``
    namespace per the deep dive §2.5 sandbox-safety boundary; the
    ``require_reserved_namespace`` validator enforces this so a misbehaving
    Red profile cannot smuggle a real-looking domain onto the blackboard.

    ``case_tags`` is the controlled tag list. Empty by default; a Bucket E
    mirror case carries ``("bucket_e_regression_probe",)`` per Matt's
    2026-05-21 §11 decision 5.
    """

    case_id: str = Field(min_length=1)
    red_profile_id: str = Field(min_length=1)
    archetype: Phase13CaseArchetype
    attack_pattern: str = Field(min_length=1)
    inbound: EmailInboundPayload
    case_tags: tuple[Phase13CaseTag, ...] = ()
    expected_min_risk_score: int | None = Field(default=None, ge=0, le=100)
    expected_max_risk_score: int | None = Field(default=None, ge=0, le=100)
    expected_recommended_actions: tuple[RecommendedEmailAction, ...] = ()
    expected_behavioral_flags: tuple[BehavioralDeviationFlag, ...] = ()
    expected_precursor_indicators: tuple[PrecursorIndicator, ...] = ()
    expects_precursor_block: bool = False
    raw_tenant_data_removed: bool = True

    @model_validator(mode="after")
    def require_tenant_data_removal(self) -> SyntheticEmailAttackCasePayload:
        if not self.raw_tenant_data_removed:
            raise ValueError(
                "synthetic email attack cases must remove raw tenant data"
            )
        return self

    @model_validator(mode="after")
    def require_reserved_namespace(self) -> SyntheticEmailAttackCasePayload:
        for field_name, value in (
            ("sender", self.inbound.sender),
            ("recipient", self.inbound.recipient),
        ):
            host = value.rsplit("@", 1)[-1].strip().lower().rstrip(">")
            if not any(host.endswith(tld) for tld in _PHASE_1_3_RESERVED_TLDS):
                raise ValueError(
                    f"synthetic case {field_name!r} must live in the reserved"
                    f" .example / .test / .invalid namespace; got {value!r}"
                )
        return self

    @model_validator(mode="after")
    def require_consistent_score_bounds(self) -> SyntheticEmailAttackCasePayload:
        lo = self.expected_min_risk_score
        hi = self.expected_max_risk_score
        if lo is not None and hi is not None and lo > hi:
            raise ValueError(
                "expected_min_risk_score cannot exceed expected_max_risk_score"
            )
        return self


PayloadModel: TypeAlias = (
    IngestEventPayload
    | DetectionResultPayload
    | RiskScorePayload
    | WorkflowTriggerPayload
    | AuditVerdictPayload
    | WeaknessReportPayload
    | SyntheticAttackCasePayload
    | SyntheticEmailAttackCasePayload
    | MutantEvaluationPayload
    | PolicyUpdatePayload
    | EmailInboundPayload
    | EmailAnalysisPayload
    | EmailAnalysisFailurePayload
    | DailyDigestPayload
    | EffectiveParametersReportPayload
    | VendorBaselineAuditPayload
    | TwoChannelConfirmationPayload
)


PAYLOAD_MODELS: dict[RecordType, type[BaseModel]] = {
    RecordType.INGEST_EVENT: IngestEventPayload,
    RecordType.DETECTION_RESULT: DetectionResultPayload,
    RecordType.RISK_SCORE: RiskScorePayload,
    RecordType.WORKFLOW_TRIGGER: WorkflowTriggerPayload,
    RecordType.AUDIT_VERDICT: AuditVerdictPayload,
    RecordType.WEAKNESS_REPORT: WeaknessReportPayload,
    RecordType.SYNTHETIC_ATTACK_CASE: SyntheticAttackCasePayload,
    RecordType.SYNTHETIC_EMAIL_ATTACK_CASE: SyntheticEmailAttackCasePayload,
    RecordType.MUTANT_EVALUATION: MutantEvaluationPayload,
    RecordType.POLICY_UPDATE: PolicyUpdatePayload,
    RecordType.EMAIL_INBOUND: EmailInboundPayload,
    RecordType.EMAIL_ANALYSIS: EmailAnalysisPayload,
    RecordType.EMAIL_ANALYSIS_FAILURE: EmailAnalysisFailurePayload,
    RecordType.DAILY_DIGEST: DailyDigestPayload,
    RecordType.EFFECTIVE_PARAMETERS_REPORT: EffectiveParametersReportPayload,
    RecordType.VENDOR_BASELINE_AUDIT: VendorBaselineAuditPayload,
    RecordType.TWO_CHANNEL_CONFIRMATION: TwoChannelConfirmationPayload,
}


class AgentRegistryEntry(StrictModel):
    agent_id: str
    display_name: str
    role: AgentRole
    allowed_environments: set[Environment]
    allowed_write_types: set[RecordType]
    can_mutate: bool = False
    can_access_production_data: bool = False
    max_hops: int = Field(default=10, ge=1, le=10)

    @model_validator(mode="after")
    def enforce_agent_safety(self) -> AgentRegistryEntry:
        if self.role == AgentRole.RED and Environment.PRODUCTION in self.allowed_environments:
            raise ValueError("Red agents are sandbox-only")
        if self.can_mutate and Environment.PRODUCTION in self.allowed_environments:
            raise ValueError("Mutation-capable agents are sandbox-only")
        return self


def validate_record_payload(record: BlackboardRecord) -> PayloadModel:
    """Validate a record payload against its record_type-specific payload model."""

    payload_model = PAYLOAD_MODELS[record.record_type]
    return payload_model.model_validate(record.payload)


def validate_record_against_registry(
    record: BlackboardRecord,
    agent: AgentRegistryEntry,
) -> PayloadModel:
    """Validate schema, payload, and agent permissions for one Blackboard write."""

    if record.source_agent != agent.agent_id:
        raise GovernanceError("record source_agent does not match registry entry")

    if record.environment not in agent.allowed_environments:
        raise GovernanceError("agent cannot write to this environment")

    if record.record_type not in agent.allowed_write_types:
        raise GovernanceError("agent cannot write this record type")

    if agent.role == AgentRole.RED and record.environment == Environment.PRODUCTION:
        raise GovernanceError("Red agents cannot access production")

    if agent.can_mutate and record.environment == Environment.PRODUCTION:
        raise GovernanceError("mutation is sandbox-only")

    if record.hop_count > agent.max_hops:
        raise GovernanceError("hop count exceeded")

    payload = validate_record_payload(record)

    if record.record_type == RecordType.POLICY_UPDATE:
        if record.environment != Environment.SANDBOX:
            raise GovernanceError("policy updates must originate in sandbox")
        if not record.audit.signed:
            raise GovernanceError("policy updates must be signed")

    if record.record_type in {
        RecordType.SYNTHETIC_ATTACK_CASE,
        RecordType.SYNTHETIC_EMAIL_ATTACK_CASE,
        RecordType.MUTANT_EVALUATION,
    } and record.environment != Environment.SANDBOX:
        raise GovernanceError("sandbox training records must stay in sandbox")

    return payload
