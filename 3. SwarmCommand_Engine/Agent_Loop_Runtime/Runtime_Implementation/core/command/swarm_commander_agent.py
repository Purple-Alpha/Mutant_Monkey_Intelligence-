"""Swarm Commander governed-agent wrapper — swarm agent #1.

Stage A route-commander wrapper authorized by the §11-SIGNED
``docs/mmi/contracts/001_swarm_commander_contract.md`` (MMI-DEC-102/101) and
Matt build authorization (MMI-DEC-111). Delegates registry-first dispatch and
DER assembly to the legacy ``SwarmCommander`` spine while enforcing RC-AUTH
boundaries on outbound records — routes never scores.

RC-AUTH boundary (contract):
- #1 routes; #3 scores.
- Registry-validated dispatch + conservative disposition assembly only.
- Optional #3 telemetry may be supplied for future routing-policy annex use;
  v1 ignores score-only hints and rejects routing-by-score patterns.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from core.blackboard.models import AgentRegistryEntry, GovernanceError
from core.orchestrator.agent_contract import (
    Agent,
    DecisionEvidenceRecord,
    MissionContext,
    SwarmDisposition,
)
from core.orchestrator.swarm_commander import SwarmCommander

SWARM_COMMANDER_AGENT_ID = "swarm_commander_001"
SWARM_COMMANDER_LAYER = 1
SWARM_COMMANDER_AUTHORITY_LEVEL = 4
DISPOSITION_POLICY_VERSION = "mmi_sc_v1"

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

_FORBIDDEN_DER_TOKENS = (
    "aggregate_risk_score",
    "axis_scores",
    "scoring_reason_codes",
    "recommended_action",
    "plain_english_summary",
    "client_message",
    "verification_instructions",
)


def _reject_routing_by_score(telemetry: Mapping[str, Any] | None) -> None:
    if not telemetry:
        return
    forbidden = sorted(key for key in telemetry if key in _ROUTING_BY_SCORE_KEYS)
    if forbidden:
        raise GovernanceError(
            "risk_triage_telemetry contains forbidden routing-by-score keys: "
            + ", ".join(forbidden)
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
) -> str:
    return (
        f"ROUTE_SUMMARY disposition={der.disposition} "
        f"human_state={der.human_state} "
        f"contributions={len(der.contributions)} "
        f"challenge_pass={len(der.challenge_pass)} "
        f"policy={disposition_policy_version}"
    )


class SwarmCommanderAgent:
    """Governed Layer 1 Command route commander — RC-AUTH routes never scores."""

    agent_id: str = SWARM_COMMANDER_AGENT_ID
    layer: int = SWARM_COMMANDER_LAYER
    authority_level: int = SWARM_COMMANDER_AUTHORITY_LEVEL
    stage_allowed: str = "stage_a"
    autonomous_action_allowed: bool = False
    disposition_policy_version: str = DISPOSITION_POLICY_VERSION

    def __init__(self, registry: dict[str, AgentRegistryEntry]) -> None:
        self._registry = registry
        self._commander = SwarmCommander(registry)

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
        _reject_routing_by_score(risk_triage_telemetry)
        der = self._commander.run_case(
            context,
            agents,
            stage=stage,
            challenge_agents=challenge_agents,
            anchor_provider=anchor_provider,
        )
        assert_der_rc_auth_compliant(der)
        return der
