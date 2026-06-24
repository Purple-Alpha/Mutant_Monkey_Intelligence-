"""Swarm Commander governed-agent wrapper — swarm agent #1.

Stage A route-commander wrapper authorized by the §11-SIGNED
``docs/mmi/contracts/001_swarm_commander_contract.md`` (MMI-DEC-102/101),
Matt build authorization (MMI-DEC-111), and routing-policy annex §6 wiring
(MMI-DEC-121/122). Delegates registry-first dispatch and DER assembly to the
legacy ``SwarmCommander`` spine while enforcing RC-AUTH boundaries on outbound
records — routes never scores.

RC-AUTH boundary (contract):
- #1 routes; #3 scores.
- Registry-validated dispatch + conservative disposition assembly only.
- Optional #3 ``RiskScoreTelemetry`` may inform ``mmi_rp_v1`` disposition hints
  only; score-only routing keys are rejected and hints never lower caution.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from core.blackboard.models import AgentRegistryEntry, GovernanceError
from core.command.risk_triage_agent import SCORING_POLICY_VERSION, _ROUTING_FORBIDDEN_KEYS
from core.orchestrator.agent_contract import (
    Agent,
    DecisionEvidenceRecord,
    HumanState,
    MissionContext,
    SwarmDisposition,
)
from core.orchestrator.swarm_commander import SwarmCommander

SWARM_COMMANDER_AGENT_ID = "swarm_commander_001"
SWARM_COMMANDER_LAYER = 1
SWARM_COMMANDER_AUTHORITY_LEVEL = 4
DISPOSITION_POLICY_VERSION = "mmi_sc_v1"
ROUTING_POLICY_VERSION = "mmi_rp_v1"

_ROUTING_BY_SCORE_KEYS = frozenset(
    {
        "auto_select_agents",
        "auto_route",
        "route_by_score",
        "skip_human_review",
        "select_agents",
        "dispatch_hint",
        "target_agent",
    }
)

_TELEMETRY_FORBIDDEN_ROUTING_KEYS = _ROUTING_BY_SCORE_KEYS | _ROUTING_FORBIDDEN_KEYS

_FORBIDDEN_DER_TOKENS = (
    "aggregate_risk_score",
    "axis_scores",
    "scoring_reason_codes",
    "recommended_action",
    "plain_english_summary",
    "client_message",
    "verification_instructions",
)

_DISPOSITION_RANK: dict[SwarmDisposition, int] = {
    "clear": 0,
    "suspicious": 1,
    "hold": 2,
    "escalate": 3,
    "human_required": 4,
}

_CAUTION_STEP: dict[SwarmDisposition, SwarmDisposition] = {
    "clear": "suspicious",
    "suspicious": "hold",
    "hold": "human_required",
    "human_required": "human_required",
    "escalate": "escalate",
}


def _reject_forbidden_telemetry_keys(telemetry: Mapping[str, Any] | None) -> None:
    if not telemetry:
        return
    forbidden = sorted(key for key in telemetry if key in _TELEMETRY_FORBIDDEN_ROUTING_KEYS)
    if forbidden:
        raise GovernanceError(
            "risk_triage_telemetry contains forbidden routing-by-score keys: "
            + ", ".join(forbidden)
        )


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _max_disposition(*dispositions: SwarmDisposition) -> SwarmDisposition:
    return max(dispositions, key=lambda item: _DISPOSITION_RANK[item])


def _human_state_for_disposition(disposition: SwarmDisposition) -> HumanState:
    return "requested" if disposition == "human_required" else "not_required"


@dataclass(frozen=True)
class RoutePolicyAudit:
    routing_policy_version: str
    base_disposition: SwarmDisposition
    final_disposition: SwarmDisposition
    hints_applied: tuple[str, ...]


def apply_routing_policy_hints(
    base_disposition: SwarmDisposition,
    telemetry: Mapping[str, Any] | None,
) -> tuple[SwarmDisposition, tuple[str, ...]]:
    """Apply signed annex §4 conservative disposition hints after base disposition."""

    if not telemetry:
        return base_disposition, ()

    if telemetry.get("scoring_policy_version") != SCORING_POLICY_VERSION:
        return base_disposition, ()

    candidates: list[SwarmDisposition] = [base_disposition]
    hints_applied: list[str] = []

    aggregate = _numeric(telemetry.get("aggregate_risk_score"))
    if aggregate is not None:
        if base_disposition in ("clear", "suspicious") and aggregate >= 85:
            candidates.append("hold")
            hints_applied.append("aggregate_risk_score>=85->hold")
        if base_disposition in ("clear", "suspicious", "hold") and aggregate >= 95:
            candidates.append("human_required")
            hints_applied.append("aggregate_risk_score>=95->human_required")

    axis_scores = telemetry.get("axis_scores")
    if isinstance(axis_scores, Mapping):
        for value in axis_scores.values():
            axis_value = _numeric(value)
            if axis_value is not None and axis_value >= 90:
                stepped = _CAUTION_STEP[base_disposition]
                candidates.append(stepped)
                hints_applied.append("axis_score>=90->step_up")
                break

    final = _max_disposition(*candidates)
    if final == base_disposition:
        return base_disposition, ()
    return final, tuple(hints_applied)


def build_route_policy_audit(
    base_disposition: SwarmDisposition,
    final_disposition: SwarmDisposition,
    hints_applied: tuple[str, ...],
) -> RoutePolicyAudit:
    return RoutePolicyAudit(
        routing_policy_version=ROUTING_POLICY_VERSION,
        base_disposition=base_disposition,
        final_disposition=final_disposition,
        hints_applied=hints_applied,
    )


def assert_der_rc_auth_compliant(der: DecisionEvidenceRecord) -> None:
    """Authority probe helper — DER must stay within RC-AUTH allowlist."""

    if der.audit_record_id is not None or der.audit_writer_agent_id is not None:
        raise GovernanceError("DER must not carry audit fields from Commander path")

    if der.disposition == "human_required" and der.human_state != "requested":
        raise GovernanceError(
            "human_required disposition must map to human_state=requested"
        )
    if der.disposition != "human_required" and der.human_state == "requested":
        raise GovernanceError(
            "human_state=requested requires human_required disposition"
        )

    serialized = der.model_dump_json()
    for token in _FORBIDDEN_DER_TOKENS:
        if token in serialized:
            raise GovernanceError(
                f"DER contains forbidden scorer or narrative token: {token!r}"
            )


def format_route_summary(
    der: DecisionEvidenceRecord,
    *,
    disposition_policy_version: str = DISPOSITION_POLICY_VERSION,
    routing_policy_version: str | None = None,
) -> str:
    parts = [
        f"ROUTE_SUMMARY disposition={der.disposition}",
        f"human_state={der.human_state}",
        f"contributions={len(der.contributions)}",
        f"challenge_pass={len(der.challenge_pass)}",
        f"policy={disposition_policy_version}",
    ]
    if routing_policy_version is not None:
        parts.append(f"routing_policy={routing_policy_version}")
    return " ".join(parts)


class SwarmCommanderAgent:
    """Governed Layer 1 Command route commander — RC-AUTH routes never scores."""

    agent_id: str = SWARM_COMMANDER_AGENT_ID
    layer: int = SWARM_COMMANDER_LAYER
    authority_level: int = SWARM_COMMANDER_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False
    disposition_policy_version: str = DISPOSITION_POLICY_VERSION
    routing_policy_version: str = ROUTING_POLICY_VERSION

    def __init__(self, registry: dict[str, AgentRegistryEntry]) -> None:
        self._registry = registry
        self._commander = SwarmCommander(registry)
        self.last_route_policy_audit: RoutePolicyAudit | None = None

    def run_case(
        self,
        context: MissionContext,
        agents: Iterable[Agent],
        *,
        stage: str = "stage_a",
        challenge_agents: Iterable[Agent] = (),
        anchor_provider: Callable[[], str | None] | None = None,
        risk_triage_telemetry: Mapping[str, Any] | None = None,
    ) -> DecisionEvidenceRecord:
        _reject_forbidden_telemetry_keys(risk_triage_telemetry)
        der = self._commander.run_case(
            context,
            agents,
            stage=stage,
            challenge_agents=challenge_agents,
            anchor_provider=anchor_provider,
        )
        base_disposition = der.disposition
        final_disposition, hints_applied = apply_routing_policy_hints(
            base_disposition,
            risk_triage_telemetry,
        )
        self.last_route_policy_audit = build_route_policy_audit(
            base_disposition,
            final_disposition,
            hints_applied,
        )
        if final_disposition != base_disposition:
            der = der.model_copy(
                update={
                    "disposition": final_disposition,
                    "human_state": _human_state_for_disposition(final_disposition),
                }
            )
        assert_der_rc_auth_compliant(der)
        return der
