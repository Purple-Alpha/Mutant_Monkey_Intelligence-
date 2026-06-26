"""Vendor Payment Verification workflow — Evidence Stage 1 (Synthetic), Tier A only.

§11-SIGNED ``Vendor_Payment_Verification_Workflow_Design_Contract_Deep_Dive.md``
(MMI-DEC-231). Orchestrates read-only Tier A checks and emits
``vpv_evidence_packet_v1`` for downstream ``#19`` Dual-Approval.

Governance boundary:
- Read-only calls into existing detectors and ``summarize_confirmation_status``.
- No payment movement, approval, hold, or block.
- Tier B fields emit ``not_available_at_stage`` until baseline governance opens.
- Not registered in ``build_default_registry``.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from core.blackboard import GovernanceError
from core.scoring.callback_phishing_detector import detect_callback_phishing
from core.scoring.email_authentication_detector import score_email_authentication
from core.scoring.ghost_thread_detector import score_ghost_thread
from core.scoring.header_divergence_detector import score_header_divergence
from core.scoring.lookalike_domain_detector import detect_lookalike_domains
from core.workflows.two_channel_confirmation import summarize_confirmation_status

SCHEMA_VERSION = "vpv_evidence_packet_v1"
ENGINE_VERSION = "vendor_payment_verification_es1_v1"
TIER_B_UNAVAILABLE = "not_available_at_stage"

_SENDER_AUTH_FAIL_INDICATORS = frozenset(
    {"spf_fail", "dkim_fail", "dmarc_fail", "spf_permerror", "dkim_permerror"}
)
_SENDER_AUTH_PARTIAL_INDICATORS = frozenset(
    {
        "spf_softfail",
        "spf_temperror",
        "dkim_none",
        "dkim_temperror",
        "dmarc_none",
        "dmarc_temperror",
    }
)
_URGENCY_CATEGORY_NAMES = frozenset(
    {
        "call_now_pressure",
        "do_not_use_known_channel",
        "voice_only_finalize",
        "support_line_substitution",
        "payment_redirect_call",
    }
)
_FINDING_ID_RE = re.compile(r"^[A-Za-z0-9_\-:.]+$")
_MAX_FINDING_ID_LENGTH = 128
_MAX_TENANT_ID_LENGTH = 128
_MAX_KNOWN_GOOD_DOMAINS = 32


@dataclass(frozen=True)
class VPVReproducibility:
    run_id: str
    input_digest: str
    engine_version: str
    check_versions: tuple[str, ...]


@dataclass(frozen=True)
class VPVEvidencePacket:
    schema_version: str
    tenant_id: str
    finding_id: str
    sender_auth: str
    domain_similarity: str
    thread_integrity: str
    banking_delta: str
    vendor_known: str
    payment_pattern_anomaly: str
    oob_confirmation: str
    urgency_markers: tuple[str, ...]
    risk_verdict: str
    reproducibility: VPVReproducibility


@dataclass(frozen=True)
class VPVPaymentRequest:
    """Explicit caller-owned payment-verification input (Tier A ES1)."""

    tenant_id: str
    finding_id: str
    sender: str
    headers: Mapping[str, str]
    body_plain: str
    subject: str | None
    known_good_domains: Sequence[str]
    blackboard_root: Path | None = None


def digest_request(request: VPVPaymentRequest) -> str:
    """Deterministic digest of explicit verification inputs (no raw body in packet)."""

    domains = ",".join(sorted(request.known_good_domains))
    header_blob = "|".join(
        f"{key.lower()}={value}"
        for key, value in sorted((request.headers or {}).items(), key=lambda item: item[0].lower())
    )
    raw = "|".join(
        [
            request.tenant_id,
            request.finding_id,
            request.sender,
            request.subject or "",
            domains,
            header_blob,
            hashlib.sha256((request.body_plain or "").encode("utf-8")).hexdigest(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run_vendor_payment_verification(request: VPVPaymentRequest) -> VPVEvidencePacket:
    """Run Tier A checks and emit ``vpv_evidence_packet_v1``."""

    tenant_id = _require_tenant_id(request.tenant_id)
    finding_id = _require_finding_id(request.finding_id)
    headers = dict(request.headers or {})
    known_good = _normalize_known_good_domains(request.known_good_domains)

    sender_auth = _assess_sender_auth(sender=request.sender, headers=headers)
    domain_similarity = _assess_domain_similarity(
        sender=request.sender,
        headers=headers,
        known_good_domains=known_good,
    )
    thread_integrity = _assess_thread_integrity(
        sender=request.sender,
        headers=headers,
        subject=request.subject,
    )
    urgency_markers = _assess_urgency_markers(body_plain=request.body_plain or "")
    oob_confirmation = _assess_oob_confirmation(
        tenant_id=tenant_id,
        finding_id=finding_id,
        blackboard_root=request.blackboard_root,
    )
    risk_verdict = _derive_risk_verdict(
        sender_auth=sender_auth,
        domain_similarity=domain_similarity,
        thread_integrity=thread_integrity,
        urgency_markers=urgency_markers,
        oob_confirmation=oob_confirmation,
    )
    input_digest = digest_request(request)
    return VPVEvidencePacket(
        schema_version=SCHEMA_VERSION,
        tenant_id=tenant_id,
        finding_id=finding_id,
        sender_auth=sender_auth,
        domain_similarity=domain_similarity,
        thread_integrity=thread_integrity,
        banking_delta=TIER_B_UNAVAILABLE,
        vendor_known=TIER_B_UNAVAILABLE,
        payment_pattern_anomaly=TIER_B_UNAVAILABLE,
        oob_confirmation=oob_confirmation,
        urgency_markers=urgency_markers,
        risk_verdict=risk_verdict,
        reproducibility=VPVReproducibility(
            run_id=uuid.uuid5(uuid.NAMESPACE_URL, f"{tenant_id}:{finding_id}:{input_digest}").hex,
            input_digest=input_digest,
            engine_version=ENGINE_VERSION,
            check_versions=(
                "email_authentication:v1",
                "lookalike_domain:v1",
                "header_divergence:v1",
                "ghost_thread:v1",
                "callback_phishing:v1",
                "two_channel_summary:v1",
            ),
        ),
    )


def _require_tenant_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > _MAX_TENANT_ID_LENGTH:
        raise GovernanceError("vendor_payment_verification requires a valid tenant_id")
    return value.strip()


def _require_finding_id(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise GovernanceError("vendor_payment_verification requires a non-empty finding_id")
    if len(value) > _MAX_FINDING_ID_LENGTH:
        raise GovernanceError(
            f"vendor_payment_verification finding_id must be <= {_MAX_FINDING_ID_LENGTH} characters"
        )
    if not _FINDING_ID_RE.match(value):
        raise GovernanceError(
            "vendor_payment_verification finding_id may only contain [A-Za-z0-9_-:.] characters"
        )
    return value


def _normalize_known_good_domains(domains: Sequence[str]) -> tuple[str, ...]:
    if not domains:
        return ()
    normalized: list[str] = []
    seen: set[str] = set()
    for domain in domains:
        if not isinstance(domain, str):
            continue
        candidate = domain.strip().lower()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
        if len(normalized) >= _MAX_KNOWN_GOOD_DOMAINS:
            break
    return tuple(normalized)


def _assess_sender_auth(*, sender: str, headers: Mapping[str, str]) -> str:
    assessment = score_email_authentication(sender=sender, headers=headers)
    indicators = set(assessment.indicators)
    if indicators & _SENDER_AUTH_FAIL_INDICATORS:
        return "fail"
    if indicators & _SENDER_AUTH_PARTIAL_INDICATORS:
        return "partial"
    if assessment.score > 0:
        return "partial"
    if not assessment.from_domain:
        return "unknown"
    return "pass"


def _assess_domain_similarity(
    *,
    sender: str,
    headers: Mapping[str, str],
    known_good_domains: Sequence[str],
) -> str:
    if not known_good_domains:
        return "none"
    assessment = detect_lookalike_domains(
        from_address=sender,
        headers=dict(headers),
        known_good_domains=known_good_domains,
    )
    if not assessment.fired:
        return "none"
    score = assessment.lookalike_domain_score
    if score >= 71:
        return "high"
    if score >= 41:
        return "medium"
    if score >= 1:
        return "low"
    return "none"


def _assess_thread_integrity(
    *,
    sender: str,
    headers: Mapping[str, str],
    subject: str | None,
) -> str:
    ghost = score_ghost_thread(subject=subject, headers=headers)
    divergence = score_header_divergence(sender=sender, headers=headers)
    if ghost.indicators:
        return "forged"
    if divergence.score >= 55:
        return "forged"
    if divergence.indicators:
        return "suspicious"
    return "intact"


def _assess_urgency_markers(*, body_plain: str) -> tuple[str, ...]:
    assessment = detect_callback_phishing(body_plain=body_plain)
    if not assessment.fired:
        return ()
    names = tuple(
        sorted(
            {
                category.category_name
                for category in assessment.categories
                if category.category_name in _URGENCY_CATEGORY_NAMES
            }
        )
    )
    return names


def _assess_oob_confirmation(
    *,
    tenant_id: str,
    finding_id: str,
    blackboard_root: Path | None,
) -> str:
    record = summarize_confirmation_status(
        tenant_id=tenant_id,
        finding_id=finding_id,
        blackboard_root=blackboard_root,
    )
    if record is None:
        return "absent"
    if record.outcome_status is None:
        return "pending"
    if record.outcome_status == "confirmed":
        return "present"
    return "absent"


def _derive_risk_verdict(
    *,
    sender_auth: str,
    domain_similarity: str,
    thread_integrity: str,
    urgency_markers: Sequence[str],
    oob_confirmation: str,
) -> str:
    """Conservative ES1 Tier A policy (OQ-2 default: ELEVATED also raises downstream)."""

    if thread_integrity == "forged":
        return "HIGH"
    if domain_similarity == "high":
        return "HIGH"
    if urgency_markers and oob_confirmation in {"absent", "pending"}:
        return "HIGH"
    if sender_auth == "fail" and (
        domain_similarity in {"medium", "high"} or thread_integrity == "suspicious"
    ):
        return "HIGH"

    if sender_auth in {"fail", "partial", "unknown"}:
        return "ELEVATED"
    if domain_similarity in {"low", "medium"}:
        return "ELEVATED"
    if thread_integrity == "suspicious":
        return "ELEVATED"
    if urgency_markers:
        return "ELEVATED"
    if oob_confirmation in {"absent", "pending"}:
        return "ELEVATED"
    return "CLEAR"
