"""Layer 1 — Detection Swarm (Phase 3).

Governing contract
------------------
``4. Product_Roadmap/Phase3_Detection_Swarm_Agent_Design_Contract.md`` —
§11 SIGNED 2026-06-10 (Matt Nichol), commit ``c522292`` — plus
``Phase3_Detection_Swarm_Contract_Amendment_1.md`` — §11 SIGNED 2026-06-11
(Matt Nichol), commit ``56e8b33``. Depends on Phase 1 Infrastructure
(``fe355da``) and Phase 2 Knowledge Foundation (``43b5511``).

Six Layer 1 detection agents. Each inspects one dimension of an inbound email and
writes a single structured evidence contribution to the Phase 1
``CanonicalEvidenceLedger``. No agent produces a verdict (P3-D1). Each queries its
mandatory Layer 0 briefing before contributing (P3-D3). Every write carries
``tenant_id`` (P3-D5). ``SenderHistoryAgent`` and ``GeoVelocityAgent`` share the
canonical ``sender_domain`` normalization (Amendment §B) so Phase 4 has a join
key. ``ContentAnalyzer`` and ``AttachmentSandbox`` attribute token cost per tenant
(Amendment §C); the other four are lookup-only and consume no tokens.
"""

from .attachment_sandbox import AttachmentSandbox
from .content_analyzer import ContentAnalyzer
from .geo_velocity_agent import GeoVelocityAgent
from .image_classifier import ImageClassifier
from .sender_domain import normalize_sender_domain
from .sender_history_agent import SenderHistoryAgent, SenderHistoryStore
from .url_receptor import URLReceptor
from ._common import (
    AttachmentInput,
    DetectionError,
    EmailContext,
    require_email,
    write_contribution,
)

__all__ = [
    "AttachmentInput",
    "AttachmentSandbox",
    "ContentAnalyzer",
    "DetectionError",
    "EmailContext",
    "GeoVelocityAgent",
    "ImageClassifier",
    "SenderHistoryAgent",
    "SenderHistoryStore",
    "URLReceptor",
    "normalize_sender_domain",
    "require_email",
    "write_contribution",
]
