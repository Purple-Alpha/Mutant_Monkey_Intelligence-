"""Final Review governed-agent wrapper — swarm agent #70 (Slice B).

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Final_Review_Agent_Design_Contract_Deep_Dive.md`` (MMI-DEC-244).

Two explicit entry modes (contract D6):
- **FR-DER:** read-only coherence audit on an assembled ``DecisionEvidenceRecord``;
  sole ``audit_record_id`` writer when checks pass.
- **FR-GOV:** assemble ``FINAL_REVIEW_PACKET_v1`` for governance finalization
  candidates; ``READY-FOR-§11`` is never authorization.

Slice A infrastructure (``complete_gate.py``, ``package_auditor.py``) is
deliberately **not** invoked or absorbed by this wrapper.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from core.blackboard import GovernanceError

from .agent_contract import (
    FINAL_REVIEW_AGENT_ID,
    AgentContribution,
    ChallengeResult,
    DecisionEvidenceRecord,
    MissionContext,
)

FINAL_REVIEW_LAYER = 6
FINAL_REVIEW_AUTHORITY_LEVEL = 6
AGENT_VERSION = "final_review_es1_v1"
CONTROL_MAPPING = "final_review:stage_a_synthetic"
STAGE1_UNDERWRITER_NOTE = (
    "Internal Stage 1 synthetic final review only; "
    "READY-FOR-§11 is not authorization and does not sign or promote."
)

CandidateKind = Literal[
    "agent_build", "contract_sign", "gated_reconcile", "governed_promotion"
]
CheckStatus = Literal["PASS", "FAIL", "N/A"]
ReadinessVerdict = Literal["READY-FOR-§11", "NOT-READY"]

_FORBIDDEN_PACKET_TOKENS = frozenset(
    {"APPROVED", "SIGN NOW", "CLEAR TO SHIP", "AUTHORIZED", "GOVERNED_AGENT"}
)

CHECK_IDS = tuple(f"C{i}" for i in range(1, 15))


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    sha256: str | None = None
    attested_present: bool | None = None


@dataclass(frozen=True)
class GovCheckResult:
    check_id: str
    status: CheckStatus
    evidence_ref: str


@dataclass(frozen=True)
class GovernanceFinalizationCandidate:
    candidate_kind: CandidateKind
    candidate_id: str
    manifest: tuple[ManifestEntry, ...] = ()
    check_results: tuple[GovCheckResult, ...] = ()
    tenant_id: str | None = None


@dataclass(frozen=True)
class FinalReviewPacket:
    schema_version: str
    candidate_kind: CandidateKind
    candidate_id: str
    tenant_id: str | None
    submitted_at: str
    agent_version: str
    checks: tuple[GovCheckResult, ...]
    could_not_verify: tuple[str, ...]
    readiness_verdict: ReadinessVerdict
    blocking_check_ids: tuple[str, ...]
    input_manifest_hash: str
    packet_hash: str


def digest_der_review(*, case_id: UUID, inputs_digest: str, decision_id: UUID) -> str:
    raw = "|".join([str(case_id), inputs_digest, str(decision_id), AGENT_VERSION])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def derive_audit_record_id(decision_id: UUID) -> str:
    return f"audit:{hashlib.sha256(str(decision_id).encode()).hexdigest()[:32]}"


def evaluate_der_coherence(
    der: DecisionEvidenceRecord,
    *,
    context: MissionContext,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (facts, gap_ids) for FR-DER C13 coherence."""

    facts: list[str] = []
    gaps: list[str] = []

    if der.case_id != context.case_id:
        gaps.append("case_id_mismatch")
    else:
        facts.append("coherence_case_id_ok")

    if der.inputs_digest != context.inputs_digest:
        gaps.append("inputs_digest_mismatch")
    else:
        facts.append("coherence_inputs_digest_ok")

    if der.audit_record_id is not None and der.audit_writer_agent_id not in (
        None,
        FINAL_REVIEW_AGENT_ID,
    ):
        gaps.append("builder_auditor_violation")
    elif der.audit_record_id is not None:
        gaps.append("audit_record_pre_set")
    else:
        facts.append("coherence_audit_slot_clear")

    if der.disposition in ("suspicious", "hold", "escalate", "human_required"):
        if not der.contributions:
            gaps.append("missing_contributions_for_disposition")
        else:
            facts.append("coherence_contributions_present")

    if der.disposition != "clear" and der.evidence_anchor is None:
        gaps.append("missing_evidence_anchor")
    elif der.evidence_anchor is not None:
        facts.append("coherence_evidence_anchor_present")

    if der.disposition == "human_required" and der.human_state == "not_required":
        gaps.append("human_state_mismatch")
    else:
        facts.append("coherence_human_state_ok")

    if gaps:
        facts.append("coherence_gap")
        for gap in gaps:
            facts.append(f"coherence_gap:{gap}")
    else:
        facts.append("coherence_ok")

    return tuple(facts), tuple(gaps)


def evaluate_gov_checks(
    candidate: GovernanceFinalizationCandidate,
) -> tuple[tuple[GovCheckResult, ...], tuple[str, ...]]:
    """Build check table; caller may pre-supply ``check_results`` at ES1."""

    if candidate.check_results:
        checks = candidate.check_results
    else:
        checks = tuple(
            GovCheckResult(
                check_id=check_id,
                status="N/A",
                evidence_ref="es1_synthetic_not_evaluated",
            )
            for check_id in CHECK_IDS
        )

    blind_spots: list[str] = []
    for entry in candidate.manifest:
        if entry.attested_present is None:
            blind_spots.append(f"manifest_unverified:{entry.path}")
        elif entry.attested_present is False:
            blind_spots.append(f"manifest_missing:{entry.path}")

    return checks, tuple(blind_spots)


def readiness_from_checks(
    checks: tuple[GovCheckResult, ...],
    *,
    blind_spots: tuple[str, ...],
) -> tuple[ReadinessVerdict, tuple[str, ...]]:
    blocking = tuple(
        c.check_id for c in checks if c.status == "FAIL"
    )
    if blocking or blind_spots:
        return "NOT-READY", blocking
    applicable = [c for c in checks if c.status != "N/A"]
    if applicable and all(c.status == "PASS" for c in applicable):
        return "READY-FOR-§11", ()
    if not applicable:
        return "NOT-READY", ("no_applicable_checks",)
    return "NOT-READY", blocking


def assemble_final_review_packet(
    candidate: GovernanceFinalizationCandidate,
) -> FinalReviewPacket:
    checks, blind_spots = evaluate_gov_checks(candidate)
    verdict, blocking = readiness_from_checks(checks, blind_spots=blind_spots)

    manifest_raw = json.dumps(
        [
            {"path": e.path, "sha256": e.sha256, "attested_present": e.attested_present}
            for e in candidate.manifest
        ],
        sort_keys=True,
    )
    input_hash = hashlib.sha256(manifest_raw.encode("utf-8")).hexdigest()
    submitted_at = datetime.now(timezone.utc).isoformat()

    packet_body = {
        "schema_version": "FINAL_REVIEW_PACKET_v1",
        "candidate_kind": candidate.candidate_kind,
        "candidate_id": candidate.candidate_id,
        "checks": [(c.check_id, c.status, c.evidence_ref) for c in checks],
        "readiness_verdict": verdict,
        "blocking_check_ids": list(blocking),
        "input_manifest_hash": input_hash,
        "agent_version": AGENT_VERSION,
    }
    packet_hash = hashlib.sha256(
        json.dumps(packet_body, sort_keys=True).encode("utf-8")
    ).hexdigest()

    _assert_no_forbidden_tokens(json.dumps(packet_body))

    return FinalReviewPacket(
        schema_version="FINAL_REVIEW_PACKET_v1",
        candidate_kind=candidate.candidate_kind,
        candidate_id=candidate.candidate_id,
        tenant_id=candidate.tenant_id,
        submitted_at=submitted_at,
        agent_version=AGENT_VERSION,
        checks=checks,
        could_not_verify=blind_spots,
        readiness_verdict=verdict,
        blocking_check_ids=blocking,
        input_manifest_hash=input_hash,
        packet_hash=packet_hash,
    )


def _assert_no_forbidden_tokens(text: str) -> None:
    upper = text.upper()
    for token in _FORBIDDEN_PACKET_TOKENS:
        if token in upper:
            raise GovernanceError(f"forbidden final-review token: {token}")


class FinalReviewAgent:
    """Governed Layer 6 Final Review agent (FR-DER + FR-GOV at ES1)."""

    agent_id: str = FINAL_REVIEW_AGENT_ID
    layer: int = FINAL_REVIEW_LAYER
    authority_level: int = FINAL_REVIEW_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        *,
        der: DecisionEvidenceRecord | None = None,
        gov_candidate: GovernanceFinalizationCandidate | None = None,
    ) -> None:
        if der is not None and gov_candidate is not None:
            raise GovernanceError(
                "FinalReviewAgent accepts exactly one of der or gov_candidate"
            )
        if der is None and gov_candidate is None:
            raise GovernanceError(
                "FinalReviewAgent requires der (FR-DER) or gov_candidate (FR-GOV)"
            )
        self._der = der
        self._gov_candidate = gov_candidate
        self._last_gaps: tuple[str, ...] = ()

    @property
    def mode(self) -> Literal["der", "gov"]:
        return "der" if self._der is not None else "gov"

    def analyze(self, context: MissionContext) -> AgentContribution:
        if self._der is None:
            raise GovernanceError("analyze() requires FR-DER mode; use assemble_gov_packet() for FR-GOV")
        if not context.tenant_id.strip():
            raise GovernanceError("FinalReviewAgent requires tenant_id on MissionContext")

        facts, gaps = evaluate_der_coherence(self._der, context=context)
        self._last_gaps = gaps
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=facts,
            control_mapping=CONTROL_MAPPING,
            underwriter_note=STAGE1_UNDERWRITER_NOTE,
        )

    def audited_der(self) -> DecisionEvidenceRecord | None:
        """Return DER with ``audit_record_id`` only when coherence checks pass."""

        if self._der is None:
            raise GovernanceError("audited_der() requires FR-DER mode")
        if self._last_gaps:
            return None
        audit_id = derive_audit_record_id(self._der.decision_id)
        return self._der.model_copy(
            update={
                "audit_record_id": audit_id,
                "audit_writer_agent_id": FINAL_REVIEW_AGENT_ID,
            }
        )

    def assemble_gov_packet(self) -> FinalReviewPacket:
        if self._gov_candidate is None:
            raise GovernanceError("assemble_gov_packet() requires FR-GOV mode")
        return assemble_final_review_packet(self._gov_candidate)

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None


__all__ = [
    "AGENT_VERSION",
    "CONTROL_MAPPING",
    "FINAL_REVIEW_AUTHORITY_LEVEL",
    "FINAL_REVIEW_LAYER",
    "FinalReviewAgent",
    "FinalReviewPacket",
    "GovCheckResult",
    "GovernanceFinalizationCandidate",
    "ManifestEntry",
    "assemble_final_review_packet",
    "derive_audit_record_id",
    "digest_der_review",
    "evaluate_der_coherence",
    "evaluate_gov_checks",
    "readiness_from_checks",
]
