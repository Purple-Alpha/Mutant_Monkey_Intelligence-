"""Reasoning-tier budgets — Brain Acceleration Branch (advisory wiring).

Separate from token ``TIER_BUDGETS`` in ``budget.py``. Defines Low/High reasoning
caps for orchestration paths. **Verdict path (#84 ReconciliationAgent) is exempt**
from Low-tier reduction — dangerous threats often look routine.

Status: read-only policy slice — not §11 signed as standalone contract yet.
Enactment paths remain ``REQUIRES_§11_GATE``.
"""

from __future__ import annotations

from enum import Enum

RECONCILIATION_AGENT_ID = "reconciliation_agent"
RISK_TRIAGE_AGENT_ID = "risk_triage_001"
SWARM_COMMANDER_AGENT_ID = "swarm_commander_001"

# Agents/tools that must never receive a forced Low reasoning tier.
VERDICT_PATH_AGENT_IDS = frozenset({RECONCILIATION_AGENT_ID})
VERDICT_PATH_TOOL_PREFIXES = ("reconcile", "verdict", "ensemble_vote")


class ReasoningTier(str, Enum):
    LOW = "low"
    HIGH = "high"


# Read-only caps (thinking-depth budget — not session token TIER_BUDGETS).
REASONING_TOKEN_CAPS: dict[ReasoningTier, int] = {
    ReasoningTier.LOW: 8_000,
    ReasoningTier.HIGH: 32_000,
}


def resolve_reasoning_tier(agent_id: str, tool: str) -> ReasoningTier:
    """Assign reasoning tier for a gateway dispatch. Verdict path always HIGH."""

    if agent_id in VERDICT_PATH_AGENT_IDS:
        return ReasoningTier.HIGH
    tool_lower = tool.lower()
    if any(tool_lower.startswith(prefix) for prefix in VERDICT_PATH_TOOL_PREFIXES):
        return ReasoningTier.HIGH
    return ReasoningTier.LOW


def reasoning_token_cap(tier: ReasoningTier) -> int:
    return REASONING_TOKEN_CAPS[tier]


__all__ = [
    "RECONCILIATION_AGENT_ID",
    "RISK_TRIAGE_AGENT_ID",
    "SWARM_COMMANDER_AGENT_ID",
    "VERDICT_PATH_AGENT_IDS",
    "VERDICT_PATH_TOOL_PREFIXES",
    "ReasoningTier",
    "REASONING_TOKEN_CAPS",
    "resolve_reasoning_tier",
    "reasoning_token_cap",
]
