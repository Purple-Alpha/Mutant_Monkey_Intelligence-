"""NorthStar scoring layer agents (LLM-backed, pluggable client)."""

from .email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
    EmailRiskScoringConfig,
    EmailRiskScoringFailure,
    EmailRiskScoringResult,
    EmailRiskScoringSuccess,
    run_email_risk_scoring_cycle,
)
from .email_authentication_detector import (
    EmailAuthenticationAssessment,
    score_email_authentication,
)

__all__ = [
    "EmailAuthenticationAssessment",
    "NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT",
    "EmailRiskScoringConfig",
    "EmailRiskScoringFailure",
    "EmailRiskScoringResult",
    "EmailRiskScoringSuccess",
    "run_email_risk_scoring_cycle",
    "score_email_authentication",
]
