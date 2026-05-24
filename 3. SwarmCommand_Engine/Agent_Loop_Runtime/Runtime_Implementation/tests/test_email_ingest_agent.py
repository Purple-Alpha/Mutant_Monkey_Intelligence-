from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.blackboard import (
    EmailAttachmentMeta,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.ingest import (
    ATTACHMENT_BODY_BYTES_KEY,
    EMAIL_INGEST_AGENT_ID,
    AttachmentInspector,
    EmailIngestError,
    IngestedEmail,
    ingest_email,
    normalize_raw_email,
    sha256_attachment_inspector,
)
from core.orchestrator import RouteContext
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import blackboard_path

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _raw_email(**overrides):
    raw = {
        "received_at": datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        "sender": "vendor@example.com",
        "recipient": "cfo@northstar.example",
        "subject": "Outstanding invoice",
        "body_plain": "Please pay the attached invoice today.",
    }
    raw.update(overrides)
    return raw


def _production_records(context: RouteContext, tenant: str = TENANT):
    return read_records(
        blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant)
    )


def test_ingest_email_writes_inbound_record_with_default_ingest_agent(tmp_path):
    context = _context(tmp_path)

    result = ingest_email(context, tenant_id=TENANT, raw_email=_raw_email())

    assert isinstance(result, IngestedEmail)
    records = _production_records(context)
    inbound = [r for r in records if r.record_type == RecordType.EMAIL_INBOUND]
    assert len(inbound) == 1
    assert inbound[0].record_id == result.record_id
    assert inbound[0].source_agent == EMAIL_INGEST_AGENT_ID
    payload = EmailInboundPayload.model_validate(inbound[0].payload)
    assert payload.sender == "vendor@example.com"
    assert payload.subject == "Outstanding invoice"


def test_ingest_email_accepts_prebuilt_payload(tmp_path):
    context = _context(tmp_path)
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender="ceo@partner.example",
        recipient="ops@northstar.example",
        subject="Wire request",
        body_plain="See attached.",
    )

    result = ingest_email(context, tenant_id=TENANT, raw_email=payload)

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ]
    assert len(inbound) == 1
    assert inbound[0].record_id == result.record_id
    assert inbound[0].payload["subject"] == "Wire request"


def test_ingest_email_defaults_received_at_when_omitted(tmp_path):
    context = _context(tmp_path)
    before = datetime.now(timezone.utc)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email={
            "sender": "x@example.com",
            "recipient": "y@example.com",
            "body_plain": "hi",
        },
    )

    after = datetime.now(timezone.utc)
    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert before <= payload.received_at <= after


def test_ingest_email_parses_iso_received_at(tmp_path):
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(received_at="2026-05-20T15:30:00+00:00"),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.received_at == datetime(2026, 5, 20, 15, 30, tzinfo=timezone.utc)


def test_ingest_email_treats_naive_datetime_as_utc(tmp_path):
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(received_at=datetime(2026, 5, 20, 8, 0)),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.received_at.tzinfo is not None
    assert payload.received_at == datetime(2026, 5, 20, 8, 0, tzinfo=timezone.utc)


def test_ingest_email_rejects_unparseable_received_at(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(EmailIngestError, match="received_at"):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(received_at="not a date"),
        )


def test_ingest_email_normalizes_attachment_dicts(tmp_path):
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[
                {
                    "filename": "invoice.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 12345,
                }
            ]
        ),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert len(payload.attachments) == 1
    assert payload.attachments[0].filename == "invoice.pdf"


def test_ingest_email_accepts_prebuilt_attachment_meta(tmp_path):
    context = _context(tmp_path)
    meta = EmailAttachmentMeta(filename="doc.pdf", size_bytes=999)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(attachments=[meta]),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].filename == "doc.pdf"
    assert payload.attachments[0].size_bytes == 999


def test_ingest_email_rejects_invalid_attachment_shape(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(EmailIngestError, match="attachments"):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(attachments=["not a dict"]),
        )


def test_ingest_email_rejects_missing_required_field(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(ValidationError):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email={
                "received_at": datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
                "recipient": "x@example.com",
                "body_plain": "hi",
            },
        )

    assert _production_records(context) == []


def test_ingest_email_rejects_unauthorized_extra_field(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(ValidationError):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(some_unknown_field="boom"),
        )


def test_ingest_email_supports_sandbox_environment(tmp_path):
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id="sandbox_default",
        raw_email=_raw_email(),
        environment=Environment.SANDBOX,
    )

    sandbox_records = read_records(
        blackboard_path(context.blackboard_root, Environment.SANDBOX, "sandbox_default")
    )
    assert len(sandbox_records) == 1
    assert sandbox_records[0].record_type == RecordType.EMAIL_INBOUND


def test_ingest_email_with_orchestrator_001_override_still_works(tmp_path):
    """Existing tests / migration callers can still pin source_agent explicitly."""
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(),
        source_agent="orchestrator_001",
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    assert inbound.source_agent == "orchestrator_001"


def test_email_ingest_agent_is_registered_with_narrow_surface():
    registry = build_default_registry()
    agent = registry[EMAIL_INGEST_AGENT_ID]
    assert agent.allowed_write_types == {RecordType.EMAIL_INBOUND}
    assert Environment.PRODUCTION in agent.allowed_environments
    assert Environment.SANDBOX in agent.allowed_environments


def test_email_ingest_agent_cannot_write_email_analysis(tmp_path):
    """Defense-in-depth: even if someone hands the ingest agent's id to a
    non-ingest route, the registry rejects record types outside its surface.
    """
    from core.blackboard import (
        BlackboardRecord,
        EmailAnalysisImpersonationAnalysis,
        EmailAnalysisPayload,
        EmailAnalysisRiskAnalysis,
    )
    from uuid import uuid4

    analysis = EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        summary="test",
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=10,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0,
            suspicious_elements=[],
        ),
        recommended_action="safe",
    )
    record = BlackboardRecord(
        tenant_id=TENANT,
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_ANALYSIS,
        source_agent=EMAIL_INGEST_AGENT_ID,
        payload=analysis.model_dump(mode="json"),
    )

    from core.blackboard import validate_record_against_registry

    registry = build_default_registry()
    with pytest.raises(GovernanceError, match="record type"):
        validate_record_against_registry(record, registry[EMAIL_INGEST_AGENT_ID])


def test_normalize_raw_email_returns_email_inbound_payload():
    payload = normalize_raw_email(_raw_email())
    assert isinstance(payload, EmailInboundPayload)
    assert payload.headers == {}
    assert payload.attachments == []


def test_normalize_raw_email_rejects_non_mapping():
    with pytest.raises(EmailIngestError, match="Mapping"):
        normalize_raw_email("not a dict")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Attachment inspector hook (Month 1.5 — foundation for Phase 1.2 ransomware
# precursor detection). The inspector contract is opt-in: omitting it must
# preserve the prior behavior, and providing one must let real connectors
# populate extracted_text / sha256 / attachment_class without changing the
# blackboard schema or the ingest agent's write surface.
# ---------------------------------------------------------------------------


def _classifying_inspector() -> AttachmentInspector:
    """Inspector that fills attachment_class + extracted_text from filename."""

    def _inspector(body_bytes, meta):
        del body_bytes
        if meta.filename.lower().endswith(".pdf"):
            return meta.model_copy(
                update={
                    "attachment_class": "invoice",
                    "extracted_text": "Invoice #4471 total due $48,920.",
                }
            )
        return meta

    return _inspector


def test_ingest_email_without_inspector_preserves_existing_attachment_behavior(tmp_path):
    """No inspector -> attachment_class stays 'unknown', extracted_text stays None."""
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[{"filename": "invoice.pdf", "content_type": "application/pdf"}]
        ),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].attachment_class == "unknown"
    assert payload.attachments[0].extracted_text is None


def test_ingest_email_inspector_populates_attachment_class_and_extracted_text(tmp_path):
    context = _context(tmp_path)

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[{"filename": "invoice.pdf", "content_type": "application/pdf"}]
        ),
        attachment_inspector=_classifying_inspector(),
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].attachment_class == "invoice"
    assert payload.attachments[0].extracted_text == "Invoice #4471 total due $48,920."


def test_ingest_email_inspector_runs_once_per_attachment_with_in_order_indices(tmp_path):
    context = _context(tmp_path)
    seen: list[str] = []

    def _recording_inspector(body_bytes, meta):
        del body_bytes
        seen.append(meta.filename)
        return meta

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[
                {"filename": "a.pdf"},
                {"filename": "b.zip"},
                {"filename": "c.docx"},
            ]
        ),
        attachment_inspector=_recording_inspector,
    )

    assert seen == ["a.pdf", "b.zip", "c.docx"]


def test_ingest_email_inspector_receives_body_bytes_when_supplied(tmp_path):
    context = _context(tmp_path)
    received: dict[str, bytes | None] = {}

    def _byte_capture_inspector(body_bytes, meta):
        received[meta.filename] = body_bytes
        return meta

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[
                {
                    "filename": "with_bytes.pdf",
                    ATTACHMENT_BODY_BYTES_KEY: b"%PDF-1.4 fake bytes",
                },
                {"filename": "no_bytes.pdf"},
            ]
        ),
        attachment_inspector=_byte_capture_inspector,
    )

    assert received == {
        "with_bytes.pdf": b"%PDF-1.4 fake bytes",
        "no_bytes.pdf": None,
    }

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert ATTACHMENT_BODY_BYTES_KEY not in inbound.payload["attachments"][0]
    assert payload.attachments[0].filename == "with_bytes.pdf"


def test_ingest_email_inspector_body_bytes_must_be_bytes(tmp_path):
    context = _context(tmp_path)

    with pytest.raises(EmailIngestError, match=ATTACHMENT_BODY_BYTES_KEY):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(
                attachments=[
                    {
                        "filename": "bad.pdf",
                        ATTACHMENT_BODY_BYTES_KEY: "this is a string not bytes",
                    }
                ]
            ),
            attachment_inspector=_classifying_inspector(),
        )

    assert _production_records(context) == []


def test_ingest_email_inspector_exception_surfaces_as_email_ingest_error(tmp_path):
    context = _context(tmp_path)

    def _exploding_inspector(body_bytes, meta):
        del body_bytes, meta
        raise RuntimeError("inspector blew up")

    with pytest.raises(EmailIngestError, match="inspector raised RuntimeError"):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(attachments=[{"filename": "x.pdf"}]),
            attachment_inspector=_exploding_inspector,
        )

    assert _production_records(context) == []


def test_ingest_email_inspector_invalid_return_type_surfaces_as_email_ingest_error(tmp_path):
    context = _context(tmp_path)

    def _wrong_return_inspector(body_bytes, meta):
        del body_bytes, meta
        return 42

    with pytest.raises(EmailIngestError, match="must return EmailAttachmentMeta"):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(attachments=[{"filename": "x.pdf"}]),
            attachment_inspector=_wrong_return_inspector,  # type: ignore[arg-type]
        )

    assert _production_records(context) == []


def test_ingest_email_inspector_may_return_mapping(tmp_path):
    """Inspectors that build a fresh dict are accepted as long as the dict
    validates against EmailAttachmentMeta. This keeps simple inspectors
    that don't want to import the model importable."""
    context = _context(tmp_path)

    def _dict_inspector(body_bytes, meta):
        del body_bytes
        return {
            "filename": meta.filename,
            "attachment_class": "credential_lure",
        }

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(attachments=[{"filename": "reset.html"}]),
        attachment_inspector=_dict_inspector,
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].attachment_class == "credential_lure"


def test_ingest_email_inspector_output_still_enforces_extracted_text_soft_cap(tmp_path):
    """Inspector returns must still pass the schema's soft cap. Pathological
    inspectors cannot inflate the blackboard."""
    from core.blackboard import NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS

    context = _context(tmp_path)
    over_cap = "z" * (NORTHSTAR_MAX_EXTRACTED_TEXT_CHARS + 1)

    def _overflow_inspector(body_bytes, meta):
        del body_bytes
        return meta.model_copy(update={"extracted_text": over_cap})

    with pytest.raises(EmailIngestError, match="failed validation"):
        ingest_email(
            context,
            tenant_id=TENANT,
            raw_email=_raw_email(attachments=[{"filename": "huge.pdf"}]),
            attachment_inspector=_overflow_inspector,
        )

    assert _production_records(context) == []


def test_ingest_email_prebuilt_payload_bypasses_inspector(tmp_path):
    """Documented contract: callers that hand in a fully-built EmailInboundPayload
    are responsible for inspection themselves; the inspector hook is skipped."""
    context = _context(tmp_path)
    calls: list[str] = []

    def _recording_inspector(body_bytes, meta):
        del body_bytes
        calls.append(meta.filename)
        return meta

    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender="a@b.example",
        recipient="c@d.example",
        body_plain="hi",
        attachments=[EmailAttachmentMeta(filename="prebuilt.pdf")],
    )

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=payload,
        attachment_inspector=_recording_inspector,
    )

    assert calls == []


def test_sha256_attachment_inspector_fills_sha256_when_bytes_present(tmp_path):
    context = _context(tmp_path)
    body = b"hello world"
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[
                {"filename": "hello.txt", ATTACHMENT_BODY_BYTES_KEY: body},
                {"filename": "no_bytes.txt"},
            ]
        ),
        attachment_inspector=sha256_attachment_inspector,
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].sha256 == expected
    assert payload.attachments[1].sha256 is None


def test_sha256_attachment_inspector_does_not_clobber_existing_sha256(tmp_path):
    context = _context(tmp_path)
    trusted_sha = "a" * 64

    ingest_email(
        context,
        tenant_id=TENANT,
        raw_email=_raw_email(
            attachments=[
                {
                    "filename": "preset.pdf",
                    "sha256": trusted_sha,
                    ATTACHMENT_BODY_BYTES_KEY: b"different bytes",
                }
            ]
        ),
        attachment_inspector=sha256_attachment_inspector,
    )

    inbound = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_INBOUND
    ][0]
    payload = EmailInboundPayload.model_validate(inbound.payload)
    assert payload.attachments[0].sha256 == trusted_sha
