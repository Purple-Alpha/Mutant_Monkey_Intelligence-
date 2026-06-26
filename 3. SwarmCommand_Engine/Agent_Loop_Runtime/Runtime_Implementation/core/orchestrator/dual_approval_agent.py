"""Dual-Approval governed-agent wrapper — swarm agent #19.

Evidence Stage 1 (Synthetic) wrapper authorized by the §11-SIGNED
``Dual_Approval_Agent_Design_Contract_Deep_Dive.md`` (MMI-DEC-232). Consumes
read-only ``vpv_evidence_packet_v1`` from the Vendor Payment Verification
workflow and emits closed dual-approval requirement facts only.

Governance boundary:
- Does not re-run Tier A/B detectors or mutate upstream workflows.
- Never approves, blocks, holds, or releases payments.
- Not registered in ``build_default_registry``.
"""

from __future__ import annotations

import hashlib
from typing import Callable

from core.blackboard import GovernanceError
from core.workflows.vendor_payment_verification import (
    SCHEMA_VERSION,
    VPVEvidencePacket,
)

from .agent_contract import AgentContribution, ChallengeResult, MissionContext

DUAL_APPROVAL_AGENT_ID = "dual_approval_001"
DUAL_APPROVAL_LAYER = 3  # Verification
DUAL_APPROVAL_AUTHORITY_LEVEL = 3  # Specialist Agent

PacketReader = Callable[[], VPVEvidencePacket | None]


def digest_packet(packet: VPVEvidencePacket) -> str:
    """Deterministic digest of one upstream evidence packet."""

    raw = "|".join(
        [
            packet.schema_version,
            packet.tenant_id,
            packet.finding_id,
            packet.risk_verdict,
            packet.reproducibility.input_digest,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require_packet(packet: VPVEvidencePacket | None) -> VPVEvidencePacket:
    if packet is None:
        raise GovernanceError("DualApprovalAgent requires an upstream VPV evidence packet")
    return packet


def _validate_packet(packet: VPVEvidencePacket) -> None:
    if packet.schema_version != SCHEMA_VERSION:
        raise GovernanceError(
            f"DualApprovalAgent schema mismatch: expected {SCHEMA_VERSION}, "
            f"got {packet.schema_version!r}"
        )
    if packet.tenant_id.strip() == "":
        raise GovernanceError("DualApprovalAgent requires tenant_id on upstream packet")
    if packet.finding_id.strip() == "":
        raise GovernanceError("DualApprovalAgent requires finding_id on upstream packet")


def _facts_for_packet(packet: VPVEvidencePacket, *, elevated_raises: bool) -> tuple[str, ...]:
    facts: list[str] = [
        f"vpv_schema_version:{packet.schema_version}",
        f"vpv_risk_verdict:{packet.risk_verdict}",
    ]
    if packet.risk_verdict == "HIGH":
        facts.append("dual_approval_required")
    elif packet.risk_verdict == "ELEVATED":
        if elevated_raises:
            facts.append("dual_approval_required")
        else:
            facts.append("dual_approval_not_applicable")
    elif packet.risk_verdict == "CLEAR":
        facts.append("dual_approval_not_applicable")
    else:
        facts.append("dual_approval_required")
    if packet.oob_confirmation in {"absent", "pending"}:
        facts.append("dual_approval_oob_unconfirmed")
    return tuple(facts)


def _verification_outcome_for(packet: VPVEvidencePacket, *, elevated_raises: bool) -> str:
    if packet.risk_verdict == "CLEAR":
        return "confirmed"
    if packet.risk_verdict == "ELEVATED" and not elevated_raises:
        return "confirmed"
    return "unable_to_verify"


class DualApprovalAgent:
    """Governed Layer 3 Verification agent for dual-approval requirement state."""

    agent_id: str = DUAL_APPROVAL_AGENT_ID
    layer: int = DUAL_APPROVAL_LAYER
    authority_level: int = DUAL_APPROVAL_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False

    def __init__(
        self,
        packet: VPVEvidencePacket | None,
        *,
        elevated_raises: bool = True,
        packet_reader: PacketReader | None = None,
    ) -> None:
        self._packet = packet
        self._elevated_raises = elevated_raises
        self._packet_reader = packet_reader

    def _load_packet(self) -> VPVEvidencePacket:
        if self._packet_reader is not None:
            packet = self._packet_reader()
        else:
            packet = self._packet
        packet = _require_packet(packet)
        _validate_packet(packet)
        return packet

    def request_digest(self) -> str:
        return digest_packet(self._load_packet())

    def analyze(self, context: MissionContext) -> AgentContribution:
        packet = self._load_packet()
        if packet.tenant_id != context.tenant_id:
            raise GovernanceError("DualApprovalAgent tenant_id must match upstream packet")

        facts = _facts_for_packet(packet, elevated_raises=self._elevated_raises)
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=facts,
            verification_source=f"vpv_packet:{packet.finding_id}",
            verification_outcome=_verification_outcome_for(
                packet,
                elevated_raises=self._elevated_raises,
            ),
        )

    def challenge(
        self, contributions: tuple[AgentContribution, ...]
    ) -> ChallengeResult | None:
        return None
