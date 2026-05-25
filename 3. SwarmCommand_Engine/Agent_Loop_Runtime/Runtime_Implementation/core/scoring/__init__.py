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
from .prompt_injection_detector import (
    PromptInjectionAssessment,
    PromptInjectionFamily,
    score_prompt_injection,
)
from .received_chain_parser import (
    ReceivedChain,
    ReceivedHop,
    parse_received_chain,
)

__all__ = [
    "DocumentMetadataAssessment",
    "assess_document_metadata_fingerprint",
    "vendor_domain_from_sender",
    "EmailAuthenticationAssessment",
    "PromptInjectionAssessment",
    "PromptInjectionFamily",
    "ReceivedChain",
    "ReceivedHop",
    "score_prompt_injection",
    "NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT",
    "EmailRiskScoringConfig",
    "EmailRiskScoringFailure",
    "EmailRiskScoringResult",
    "EmailRiskScoringSuccess",
    "run_email_risk_scoring_cycle",
    "score_email_authentication",
    "parse_received_chain",
]
