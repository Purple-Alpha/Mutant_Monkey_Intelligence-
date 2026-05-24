"""NorthStar Inbox Shield — email ingest layer."""

from .email_ingest_agent import (
    ATTACHMENT_BODY_BYTES_KEY,
    EMAIL_INGEST_AGENT_ID,
    AttachmentInspector,
    EmailIngestError,
    IngestedEmail,
    ingest_email,
    normalize_raw_email,
    sha256_attachment_inspector,
)

__all__ = [
    "ATTACHMENT_BODY_BYTES_KEY",
    "EMAIL_INGEST_AGENT_ID",
    "AttachmentInspector",
    "EmailIngestError",
    "IngestedEmail",
    "ingest_email",
    "normalize_raw_email",
    "sha256_attachment_inspector",
]
