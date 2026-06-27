"""GatewayController — Phase 6 (Layer 6), the control-plane spine.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D8 + §3.1 + §3.6. Scoreboard row #89.

The gateway is the **single entry point** for every agent action. It owns no
business logic — it enforces the gates in sequence and dispatches. The lifecycle
(§3.6), in order, with no shortcuts (BRC-D8):

    identity and tenant resolution   (Gate 5 — AgentIdentityGateway)
    → ring assignment                (Gate 3 — RingController)
    → session budget check           (Gate 1 — SessionBudgetStore)
    → breaker check                  (Gate 1 — BreakerStore + LoopDetector)
    → mode check                     (Gate 4 — Mode Controller interface, BRC-D10)
    → dispatch
    → telemetry emission

Any gate failure at any step → **deterministic reject + append-only audit
record**. Partial dispatch is forbidden — a rejection never reaches dispatch.

The **mode check** is an *interface only* (BRC-D10): the gateway asks an injected
``ModeCheck`` whether dispatch is allowed for the tenant; it does **not** own mode
transitions, epochs, or quorum — that is the separate Mode Controller contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Protocol

from core.control_plane.reasoning_budget import (
    resolve_reasoning_tier,
    reasoning_token_cap,
)
from core.control_plane.triage_prefilter import TriagePreFilter

from core.control_plane.audit import ControlPlaneAuditTrail, ControlPlaneEvent
from core.control_plane.breaker import BreakerKey, BreakerStore, TripClass
from core.control_plane.budget import SessionBudgetStore
from core.control_plane.identity import AgentIdentityGateway, IdentityError
from core.control_plane.loop_detector import LoopDetector
from core.control_plane.rings import RingController
from core.control_plane.segmentation import (
    SegmentationError,
    TenantSegmentationController,
)


class ModeCheck(Protocol):
    """Gateway-side view of the Mode Controller (BRC-D10, interface only)."""

    def is_dispatch_allowed(self, tenant_id: str) -> bool:
        ...


class AllowAllModeCheck:
    """Default mode check until the Mode Controller contract is built (BRC-D10).

    Dispatch is allowed; this is a placeholder for the separate Mode Controller.
    A single agent can never flip this — the gateway only *reads* the mode.
    """

    def is_dispatch_allowed(self, tenant_id: str) -> bool:  # noqa: D401
        return True


class GatewayRejected(Exception):
    """Raised when a request is rejected at any gate (fail-safe, no dispatch)."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(f"gateway rejected at {stage}: {reason}")
        self.stage = stage
        self.reason = reason


@dataclass(frozen=True)
class GatewayRequest:
    token: str
    claimed_agent_id: str
    tenant_id: str
    tool: str
    session_id: str
    args: Any = None
    candidate_id: str | None = None
    credential: str | None = None


@dataclass(frozen=True)
class GatewayDecision:
    dispatched: bool
    stage_reached: str
    reason: str
    agent_id: str
    tenant_id: str


@dataclass
class GatewayController:
    """Row #89 spine — enforces the §3.6 lifecycle over the eight components."""

    identity: AgentIdentityGateway
    rings: RingController
    budgets: SessionBudgetStore
    breakers: BreakerStore
    loop_detector: LoopDetector
    segmentation: TenantSegmentationController
    audit: ControlPlaneAuditTrail
    mode_check: ModeCheck = field(default_factory=AllowAllModeCheck)
    triage_prefilter: TriagePreFilter | None = None

    _CONTROL_AUTHORITY_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "bypass",
            "direct_tool_invocation",
            "entrypoint_signed_by_gateway",
            "epoch",
            "gate_failure",
            "gateway_pid_signature",
            "identity_verified",
            "ipc_channel",
            "mode",
            "mode_config",
            "mode_epoch",
            "previous_signal",
            "signed_by",
            "state_hash",
            "suppress_telemetry",
            "telemetry_frame",
            "telemetry_replay",
            "thread_fork",
        }
    )

    def _contains_control_authority_claim(self, value: Any) -> bool:
        """Agent payloads may not assert control-plane authority.

        The gateway owns lifecycle authority. Payloads that carry forged PID,
        epoch/mode, bypass, or telemetry-control fields are rejected before any
        downstream dispatch rather than ignored as harmless content.
        """

        if isinstance(value, dict):
            for key, nested in value.items():
                if str(key) in self._CONTROL_AUTHORITY_KEYS:
                    return True
                if self._contains_control_authority_claim(nested):
                    return True
        elif isinstance(value, (list, tuple, set)):
            return any(self._contains_control_authority_claim(item) for item in value)
        return False

    def handle(self, request: GatewayRequest) -> GatewayDecision:
        """Walk the full lifecycle. Returns a dispatched decision, or raises
        ``GatewayRejected`` at the first failing gate — never partial dispatch.
        """

        # --- Gate 5: identity and tenant resolution --------------------------
        try:
            resolved = self.identity.resolve(
                token=request.token,
                claimed_agent_id=request.claimed_agent_id,
                tenant_id=request.tenant_id,
                tool=request.tool,
            )
        except IdentityError as exc:
            self.audit.record(
                ControlPlaneEvent.IDENTITY_REJECTED,
                str(exc),
                tenant_id=request.tenant_id,
                agent_id=request.claimed_agent_id,
            )
            raise GatewayRejected("identity", str(exc)) from exc

        if self._contains_control_authority_claim(request.args):
            reason = "agent payload claims control-plane authority"
            self.audit.record(
                ControlPlaneEvent.GATEWAY_REJECTED,
                reason,
                tenant_id=resolved.tenant_id,
                agent_id=resolved.agent_id,
            )
            raise GatewayRejected("authority_payload", reason)

        # Forged-tenant guard (BRC-D4): resolved tenant must match the segment
        # binding when a credential is presented.
        if request.credential is not None:
            try:
                self.segmentation.verify_tenant_binding(
                    resolved_tenant_id=resolved.tenant_id,
                    claimed_tenant_id=request.tenant_id,
                    credential=request.credential,
                )
            except SegmentationError as exc:
                self.audit.record(
                    ControlPlaneEvent.SEGMENTATION_REJECTED,
                    str(exc),
                    tenant_id=request.tenant_id,
                    agent_id=resolved.agent_id,
                )
                raise GatewayRejected("segmentation", str(exc)) from exc

        # --- Gate 3: ring assignment ----------------------------------------
        if request.candidate_id is not None:
            try:
                self.rings.ring_of(request.candidate_id)
            except Exception:
                self.rings.assign(request.candidate_id)

        # --- Gate 1a: session budget check ----------------------------------
        if not self.budgets.may_issue_decision(request.session_id):
            reason = "session budget exhausted (incomplete_budget_exhausted)"
            self.audit.record(
                ControlPlaneEvent.GATEWAY_REJECTED,
                reason,
                tenant_id=resolved.tenant_id,
                agent_id=resolved.agent_id,
            )
            raise GatewayRejected("budget", reason)

        if isinstance(request.args, dict) and "estimated_max_tokens" in request.args:
            estimated = request.args["estimated_max_tokens"]
            if not isinstance(estimated, int) or estimated <= 0:
                reason = "invalid estimated_max_tokens pre-dispatch lock"
                self.audit.record(
                    ControlPlaneEvent.GATEWAY_REJECTED,
                    reason,
                    tenant_id=resolved.tenant_id,
                    agent_id=resolved.agent_id,
                )
                raise GatewayRejected("budget", reason)
            if not self.budgets.charge(request.session_id, tokens=estimated):
                reason = "pre-dispatch token budget lock failed"
                self.audit.record(
                    ControlPlaneEvent.GATEWAY_REJECTED,
                    reason,
                    tenant_id=resolved.tenant_id,
                    agent_id=resolved.agent_id,
                )
                raise GatewayRejected("budget", reason)

        # --- Gate 1b: breaker check (+ behavioral loop detection) -----------
        key = BreakerKey(
            tenant_id=resolved.tenant_id,
            agent_id=resolved.agent_id,
            tool=resolved.tool,
            session_id=request.session_id,
        )
        if not self.breakers.is_closed(key):
            reason = f"breaker not closed for {resolved.agent_id}/{resolved.tool}"
            self.audit.record(
                ControlPlaneEvent.GATEWAY_REJECTED,
                reason,
                tenant_id=resolved.tenant_id,
                agent_id=resolved.agent_id,
            )
            raise GatewayRejected("breaker", reason)

        loop = self.loop_detector.observe(
            agent_id=resolved.agent_id,
            session_id=request.session_id,
            tool=resolved.tool,
            args=request.args,
        )
        if loop:
            # Behavioral loop → trip the breaker (transient; sustained for the
            # ReconciliationAgent per BRC-D13) and reject this action.
            self.breakers.trip(key, trip_class=TripClass.TRANSIENT)
            reason = "behavioral loop detected (identical-run or frequency)"
            self.audit.record(
                ControlPlaneEvent.BREAKER_TRIPPED,
                reason,
                tenant_id=resolved.tenant_id,
                agent_id=resolved.agent_id,
            )
            raise GatewayRejected("breaker", reason)

        # --- Gate 4: mode check (interface only, BRC-D10) -------------------
        if not self.mode_check.is_dispatch_allowed(resolved.tenant_id):
            reason = f"mode controller disallows dispatch for {resolved.tenant_id}"
            self.audit.record(
                ControlPlaneEvent.GATEWAY_REJECTED,
                reason,
                tenant_id=resolved.tenant_id,
                agent_id=resolved.agent_id,
            )
            raise GatewayRejected("mode", reason)


        # --- Brain Acceleration: reasoning tier (audit only; verdict path HIGH) ---
        reasoning_tier = resolve_reasoning_tier(resolved.agent_id, resolved.tool)
        reasoning_cap = reasoning_token_cap(reasoning_tier)
        if isinstance(request.args, dict):
            requested_tier = request.args.get("reasoning_tier")
            if requested_tier is not None and str(requested_tier) != reasoning_tier.value:
                reason = (
                    f"reasoning tier mismatch: requested {requested_tier!r} "
                    f"resolved {reasoning_tier.value}"
                )
                self.audit.record(
                    ControlPlaneEvent.GATEWAY_REJECTED,
                    reason,
                    tenant_id=resolved.tenant_id,
                    agent_id=resolved.agent_id,
                )
                raise GatewayRejected("reasoning_tier", reason)

        # --- Brain Acceleration: triage pre-filter (flag-not-drop) ------------
        if self.triage_prefilter is not None:
            telemetry = self.triage_prefilter.score_gateway_request(
                request, resolved.tenant_id
            )
            if telemetry is not None:
                self.audit.record(
                    ControlPlaneEvent.TRIAGE_SCORED,
                    f"aggregate_risk_score={telemetry.aggregate_risk_score}",
                    tenant_id=resolved.tenant_id,
                    agent_id=resolved.agent_id,
                )

        # --- dispatch + telemetry -------------------------------------------
        self.audit.record(
            ControlPlaneEvent.GATEWAY_DISPATCHED,
            f"{resolved.agent_id} → {resolved.tool}",
            tenant_id=resolved.tenant_id,
            agent_id=resolved.agent_id,
        )
        return GatewayDecision(
            dispatched=True,
            stage_reached="dispatch",
            reason="all gates passed",
            agent_id=resolved.agent_id,
            tenant_id=resolved.tenant_id,
        )


__all__ = [
    "ModeCheck",
    "AllowAllModeCheck",
    "GatewayRejected",
    "GatewayRequest",
    "GatewayDecision",
    "GatewayController",
]
