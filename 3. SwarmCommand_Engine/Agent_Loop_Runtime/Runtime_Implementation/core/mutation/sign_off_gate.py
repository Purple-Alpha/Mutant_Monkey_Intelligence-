"""HumanSignOffGate — Phase 5 (Layer 5), no autonomous production deployment.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D4 + §3.4 (stage 5 of the Anomaly Detection Pipeline).

No mutation reaches production without an explicit human signature. The gate
delegates the actual authority check to the signed Phase 1
``RoleSeparationController``: deployment requires the ``DEPLOY_MUTATION``
capability, which the §3 capability map reserves for the ``OPERATOR`` role, and
``OPERATOR`` is reserved for Matt only (rule 4). There is no timeout and no
auto-approve — an unsigned proposal stays a proposal forever.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.operator_state.role_separation import (
    Capability,
    Role,
    RoleSeparationController,
    RoleSeparationError,
)

DEPLOY_SURFACE = "mutation.deploy"


class SignOffError(Exception):
    """Raised when a deployment is attempted without valid human sign-off."""


@dataclass(frozen=True)
class MutationProposal:
    """A candidate that has cleared validation and is awaiting human sign-off."""

    candidate_id: str
    tenant_scope: str
    validation_summary: str
    evidence_chain: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignOffRecord:
    """Proof that a named human authorized one deployment."""

    candidate_id: str
    signer_id: str
    signed_at: datetime


@dataclass
class HumanSignOffGate:
    """Operator-signature gate in front of production deployment (P5-D4)."""

    controller: RoleSeparationController
    _signed: dict[str, SignOffRecord] = field(default_factory=dict)

    def sign_off(self, proposal: MutationProposal, *, actor_id: str) -> SignOffRecord:
        """Record a human sign-off for ``proposal``.

        Delegates authority to the RoleSeparationController: ``actor_id`` must be
        able to exercise ``DEPLOY_MUTATION`` as ``OPERATOR``. Any non-operator,
        or a missing/empty signer, is rejected — fail safe, no deployment.
        """

        if not proposal.candidate_id:
            raise SignOffError("proposal requires a candidate_id")
        try:
            self.controller.authorize(
                actor_id=actor_id,
                role=Role.OPERATOR,
                capability=Capability.DEPLOY_MUTATION,
                surface=DEPLOY_SURFACE,
            )
        except RoleSeparationError as exc:
            raise SignOffError(
                f"deployment sign-off denied: {exc}"
            ) from exc

        record = SignOffRecord(
            candidate_id=proposal.candidate_id,
            signer_id=actor_id,
            signed_at=datetime.now(timezone.utc),
        )
        self._signed[proposal.candidate_id] = record
        return record

    def is_signed_off(self, candidate_id: str) -> bool:
        return candidate_id in self._signed

    def require_sign_off(self, candidate_id: str) -> SignOffRecord:
        """Return the sign-off record or raise — the production deploy guard."""

        record = self._signed.get(candidate_id)
        if record is None:
            raise SignOffError(
                f"candidate {candidate_id!r} has no human sign-off; "
                "production deployment refused (P5-D4)"
            )
        return record
