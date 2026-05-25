"""NorthStar scoring layer agents (LLM-backed, pluggable client)."""

from .email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
    EmailRiskScoringConfig,
    EmailRiskScoringFailure,
    EmailRiskScoringResult,
    EmailRiskScoringSuccess,
    run_email_risk_scoring_cycle,
)
from .document_metadata_detector import (
    DocumentMetadataAssessment,
    assess_document_metadata_fingerprint,
    vendor_domain_from_sender,
)
from .email_authentication_detector import (
    EmailAuthenticationAssessment,
    score_email_authentication,
)

__all__ = [
    "DocumentMetadataAssessment",
    "assess_document_metadata_fingerprint",
    "vendor_domain_from_sender",
    "EmailAuthenticationAssessment",
    "NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT",
    "EmailRiskScoringConfig",
    "EmailRiskScoringFailure",
    "EmailRiskScoringResult",
    "EmailRiskScoringSuccess",
    "run_email_risk_scoring_cycle",
    "score_email_authentication",
]
