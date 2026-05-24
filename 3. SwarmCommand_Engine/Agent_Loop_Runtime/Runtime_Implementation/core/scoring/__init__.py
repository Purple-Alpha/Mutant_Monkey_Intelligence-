"""NorthStar scoring layer agents (LLM-backed, pluggable client)."""

from .email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
    EmailRiskScoringConfig,
    EmailRiskScoringFailure,
    EmailRiskScoringResult,
    EmailRiskScoringSuccess,
    run_email_risk_scoring_cycle,
)

__all__ = [
    "NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT",
    "EmailRiskScoringConfig",
    "EmailRiskScoringFailure",
    "EmailRiskScoringResult",
    "EmailRiskScoringSuccess",
    "run_email_risk_scoring_cycle",
]
