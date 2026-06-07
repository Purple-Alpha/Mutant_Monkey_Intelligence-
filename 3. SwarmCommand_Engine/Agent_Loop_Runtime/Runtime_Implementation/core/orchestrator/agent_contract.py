"""Shared governed-agent contract types for the Blue-Team Swarm.

Build-order step 1 (the Decision Evidence Record + shared agent interface),
per the adopted 6-layer Design Tree and the locked design recorded in
``agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md``.

These types are orchestrator-facing. The Swarm Commander reads an agent's
static metadata to route it (enforcement lives in
``core.orchestrator.routes.validate_agent_dispatch``), invokes ``analyze``
(Pass 1) and, for Verification / Challenge agents, ``challenge`` (Pass 2), and
aggregates the per-agent ``AgentContribution`` records into one client-safe
``DecisionEvidenceRecord`` per case.

Design constraints baked into the schema (not left to convention):
- Per-agent contribution fields are layer-restricted: a Detection-layer agent
  that writes a verification / challenge / evidence field raises
  ``ValidationError``.
- The DER stores facts and outcomes only - never a reasoning trace / chain of
  thought. The client-facing narrative is generated at output time by
  ``core.scoring.client_facing_rubric`` and is NOT stored in the DER.
- ``audit_record_id`` is write-protected to the Final Review Agent (the
  builder-auditor separation constraint; the enforcing validator lands in
  slice 3).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from core.blackboard.models import StrictModel

# Builder-auditor separation: the only agent permitted to write
# ``audit_record_id`` onto a DER. The Evidence Package Agent assembles the DER
# but cannot audit it; the Final Review Agent (Layer 6, read-only) audits it.
FINAL_REVIEW_AGENT_ID = "final_review_001"

# Evidence anchor reuses the existing package-hash convention from
# ``core/evidence_package/package_generator.py`` (``sha256:<64 hex>``); the DER
# stores the anchor, it does not invent new sealing logic.
_EVIDENCE_ANCHOR_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

# Closed vocabularies for one swarm decision. Literal (not Enum) to match the
# dominant recent pattern in core/blackboard/models.py.
SwarmDisposition = Literal[
    "clear", "suspicious", "hold", "escalate", "human_required"
]
HumanState = Literal["not_required", "requested", "pending", "resolved"]
ChallengeOutcome = Literal["confirmed", "contradicted", "inconclusive"]
VerificationOutcome = Literal["confirmed", "contradicted", "unable_to_verify"]

# Client-safe text fields reuse the 160-char cap the 5-axis rubric and the
# TOAD detector already use for stability.
_CLIENT_SAFE_TEXT_MAX = 160


class MissionContext(StrictModel):
    """The framing one swarm decision is made against - the Commander's input
    to every agent's ``analyze`` pass.

    Carries the case identity and a digest of the material under review. Agents
    read the case's detector / analysis records from the Blackboard, so the raw
    email body is intentionally not duplicated here.
    """

    case_id: UUID = Field(default_factory=uuid4)
    tenant_id: str = Field(min_length=1)
    inputs_digest: str = Field(min_length=1)  # SHA-256 of the raw email/package under review
    source_record_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Optional contribution fields permitted per Design-Tree layer. The base fields
# (agent_id, layer, observed_facts) are open to all layers; the fields below are
# layer-restricted and the validator rejects any set by a wrong layer.
#   1 Command | 2 Detection | 3 Verification | 4 Evidence
#   5 Challenge/Red-Team | 6 Learning/Governance
_LAYER_RESTRICTED_FIELDS: dict[int, frozenset[str]] = {
    1: frozenset(),
    2: frozenset(),
    3: frozenset({"verification_source", "verification_outcome"}),
    4: frozenset({"control_mapping", "underwriter_note"}),
    5: frozenset({"challenge_result", "challenge_rationale"}),
    6: frozenset({"control_mapping", "underwriter_note"}),
}
_ALL_RESTRICTED_FIELDS: frozenset[str] = frozenset(
    name for names in _LAYER_RESTRICTED_FIELDS.values() for name in names
)


class AgentContribution(StrictModel):
    """One agent's facts-only contribution to a case decision.

    Layer-restricted: a Detection-layer (or Command-layer) agent may only emit
    ``observed_facts``; verification / challenge / evidence fields are reserved
    for their respective layers and the validator raises on a wrong-layer write.
    No interpretation field is open to a Detection agent - that boundary is the
    Q4 promotion-bar rule turned into a schema constraint.
    """

    agent_id: str = Field(min_length=1)
    layer: int = Field(ge=1, le=6)
    observed_facts: tuple[str, ...] = ()
    # Verification layer (3) only
    verification_source: str | None = Field(default=None, max_length=253)
    verification_outcome: VerificationOutcome | None = None
    # Challenge / Red-Team layer (5) only
    challenge_result: ChallengeOutcome | None = None
    challenge_rationale: str | None = Field(default=None, max_length=_CLIENT_SAFE_TEXT_MAX)
    # Evidence (4) / Learning-Governance (6) layers only
    control_mapping: str | None = Field(default=None, max_length=_CLIENT_SAFE_TEXT_MAX)
    underwriter_note: str | None = Field(default=None, max_length=_CLIENT_SAFE_TEXT_MAX)

    @model_validator(mode="after")
    def enforce_layer_field_boundary(self) -> AgentContribution:
        allowed = _LAYER_RESTRICTED_FIELDS[self.layer]
        for field_name in _ALL_RESTRICTED_FIELDS:
            if getattr(self, field_name) is not None and field_name not in allowed:
                raise ValueError(
                    f"layer {self.layer} agent may not set {field_name!r} "
                    "(layer-restricted contribution field)"
                )
        return self


class ChallengeResult(StrictModel):
    """Pass-2 detect-then-challenge outcome. Facts/outcome only; ``challenge_basis``
    is one client-safe sentence, never a reasoning trace."""

    agent_id: str = Field(min_length=1)
    challenge_outcome: ChallengeOutcome
    challenge_basis: str = Field(min_length=1, max_length=_CLIENT_SAFE_TEXT_MAX)


class DecisionTimestamps(StrictModel):
    """Reaction-timing anchors for one case decision (per AGENTS reaction-timing
    discipline). ``detected_at`` is required; the rest fill in as the case
    progresses through verification and closure."""

    detected_at: datetime
    verification_requested_at: datetime | None = None
    verification_outcome_at: datetime | None = None
    closed_at: datetime | None = None


class DecisionEvidenceRecord(StrictModel):
    """Client-safe aggregation of one swarm decision.

    A thin aggregation type, not a new sealed record: it collects the per-agent
    ``AgentContribution`` records for one ``case_id`` plus the pass-2
    ``challenge_pass`` outcomes and the final disposition. ``evidence_anchor`` is
    the SHA-256 seal applied by the Evidence Package Agent at assembly (reusing
    the existing package hashing - no new sealing logic). ``audit_record_id`` is
    write-protected to the Final Review Agent (slice 3 enforcement).

    No narrative / reasoning trace is stored here; the client-facing explanation
    is generated at output time by ``core.scoring.client_facing_rubric``.
    """

    decision_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    inputs_digest: str = Field(min_length=1)
    contributions: tuple[AgentContribution, ...] = ()
    challenge_pass: tuple[ChallengeResult, ...] = ()
    disposition: SwarmDisposition
    human_state: HumanState = "not_required"
    timestamps: DecisionTimestamps
    evidence_anchor: str | None = None
    audit_record_id: str | None = None
    # Identifies which agent set audit_record_id; the validator below enforces
    # that only the Final Review Agent may do so (builder-auditor separation).
    audit_writer_agent_id: str | None = None

    @model_validator(mode="after")
    def enforce_audit_writer_separation(self) -> DecisionEvidenceRecord:
        # Field-level builder-auditor separation: audit_record_id may only be
        # set when the writer is the Final Review Agent. The assembler (Evidence
        # Package Agent) constructing a DER never claims that writer id, so any
        # attempt by it to set audit_record_id fails validation here.
        if self.audit_record_id is not None and (
            self.audit_writer_agent_id != FINAL_REVIEW_AGENT_ID
        ):
            raise ValueError(
                "audit_record_id may only be set by the Final Review Agent "
                f"(audit_writer_agent_id == {FINAL_REVIEW_AGENT_ID!r}); the "
                "assembler and other agents cannot write it"
            )
        return self

    @model_validator(mode="after")
    def enforce_evidence_anchor_format(self) -> DecisionEvidenceRecord:
        # Reuse the existing package-hash convention; do not invent new sealing.
        if self.evidence_anchor is not None and not _EVIDENCE_ANCHOR_RE.match(
            self.evidence_anchor
        ):
            raise ValueError(
                "evidence_anchor must use the existing package-hash convention "
                "'sha256:<64 lowercase hex>'"
            )
        return self


@runtime_checkable
class Agent(Protocol):
    """The contract every governed swarm agent implements.

    Static metadata is read by the Commander/router for dispatch gating; the
    agent never reads or enforces its own authority. Detection-layer agents
    return ``None`` from ``challenge`` (Pass 2 is a Verification/Challenge-layer
    concern); whether ``challenge`` is invoked is the router's decision.
    """

    agent_id: str
    layer: int
    authority_level: int
    stage_allowed: str
    autonomous_action_allowed: bool

    def analyze(self, context: MissionContext) -> AgentContribution: ...

    def challenge(
        self, contribution: AgentContribution
    ) -> ChallengeResult | None: ...
