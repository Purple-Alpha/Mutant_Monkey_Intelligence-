"""NorthStar Inbox Shield — email ingest stub.

The job here is intentionally tiny: accept one raw inbound email (as a dict
from a future webhook / IMAP / Graph API connector, or as a fully-built
``EmailInboundPayload`` for callers that already normalized) and route a
single ``EMAIL_INBOUND`` record onto the tenant's production Blackboard.

Real connectors (Gmail webhook, Outlook Graph subscription, IMAP poller) sit
above this layer and call ``ingest_email``. They are intentionally out of
scope for this stub — the goal is just to unblock end-to-end smoke testing
of ingest -> score -> digest with deterministic fakes.

This module uses its own dedicated ``email_ingest_001`` agent in the
registry so the write surface is narrow: ``EMAIL_INBOUND`` only. The
broader ``orchestrator_001`` agent retains ``EMAIL_INBOUND`` permission as
a safety net (existing tests seed inbound emails through it), but
production callers should use ``ingest_email`` and get the narrower
identity for free.

Conventions matched from the existing scoring / drafting agents:
- frozen config-like result types (``IngestedEmail``);
- callers pass a ``RouteContext`` so governance + storage are reused;
- pydantic validation errors from ``EmailInboundPayload`` are surfaced
  verbatim (callers can catch ``pydantic.ValidationError`` directly);
- ingest-specific normalization failures (e.g. unparseable ``received_at``)
  raise ``EmailIngestError(ValueError)`` so they are distinguishable from
  schema errors.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping
from uuid import UUID

from core.blackboard import (
    EmailAttachmentMeta,
    EmailInboundPayload,
    Environment,
)
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_email_inbound,
)

EMAIL_INGEST_AGENT_ID = "email_ingest_001"

# Optional out-of-band key on raw attachment dicts that carries the
# attachment body bytes for inspector use. Popped before pydantic
# validation so it never reaches the persisted ``EmailAttachmentMeta``
# (the blackboard intentionally stores metadata only).
ATTACHMENT_BODY_BYTES_KEY = "body_bytes"

# Pluggable inspector contract. Receives the raw attachment body (when
# the connector chose to pass it via ``body_bytes`` on the raw dict, or
# ``None`` if the connector only carries metadata) plus the baseline-
# normalized ``EmailAttachmentMeta``. Returns an enriched
# ``EmailAttachmentMeta``. Returning the input unchanged is a valid
# no-op; the inspector layer is opt-in.
#
# Inspectors must not perform I/O the caller has not authorized; they
# operate strictly on the bytes / meta they are handed. Real implementations
# (PDF text extraction, OCR, executable scanning) plug in via this hook
# and produce ``extracted_text`` / ``sha256`` / ``attachment_class``.
AttachmentInspector = Callable[
    [bytes | None, EmailAttachmentMeta],
    EmailAttachmentMeta,
]


class EmailIngestError(ValueError):
    """Raised for ingest-specific normalization failures.

    Distinct from ``pydantic.ValidationError`` so callers can tell the
    difference between "the raw email shape was bad" (this exception) and
    "the schema check rejected the normalized payload" (pydantic raises).
    """


@dataclass(frozen=True)
class IngestedEmail:
    """One inbound email successfully written to the Blackboard.

    ``record_id`` is the convenient handle most callers want;
    ``route_result`` carries the full ``BlackboardRecord`` + on-disk path
    for tests and downstream consumers that need them.
    """

    record_id: UUID
    route_result: RouteResult


def ingest_email(
    context: RouteContext,
    *,
    tenant_id: str,
    raw_email: Mapping[str, Any] | EmailInboundPayload,
    environment: Environment = Environment.PRODUCTION,
    source_agent: str = EMAIL_INGEST_AGENT_ID,
    workflow_id: str | None = None,
    parent_record_id: UUID | None = None,
    attachment_inspector: AttachmentInspector | None = None,
) -> IngestedEmail:
    """Normalize one raw email and append it to the tenant Blackboard.

    ``raw_email`` accepts either:
    - an already-built ``EmailInboundPayload`` (passthrough), or
    - a ``Mapping`` of raw fields (sender / recipient / body_plain / ...)
      that gets normalized via :func:`normalize_raw_email`.

    ``source_agent`` defaults to the dedicated ingest agent. Tests and
    legacy callers may override (e.g. ``"orchestrator_001"``) but
    production callers should rely on the default for a narrow write
    surface.

    ``attachment_inspector`` is an optional hook (see
    :data:`AttachmentInspector`) that is called once per attachment
    *after* baseline meta normalization. The hook can populate the
    deep-inspection fields added in the Month 1 attachment schema
    extension (``extracted_text``, ``sha256``, ``attachment_class``).
    Passing ``raw_email`` as a fully-built ``EmailInboundPayload``
    bypasses the inspector — callers that want inspection on a prebuilt
    payload should normalize through a ``Mapping`` instead.
    """

    payload = (
        raw_email
        if isinstance(raw_email, EmailInboundPayload)
        else normalize_raw_email(raw_email, attachment_inspector=attachment_inspector)
    )

    route_result = submit_email_inbound(
        context,
        tenant_id=tenant_id,
        environment=environment,
        source_agent=source_agent,
        payload=payload,
        workflow_id=workflow_id,
        parent_record_id=parent_record_id,
    )
    return IngestedEmail(
        record_id=route_result.record.record_id,
        route_result=route_result,
    )


def normalize_raw_email(
    raw: Mapping[str, Any],
    *,
    attachment_inspector: AttachmentInspector | None = None,
) -> EmailInboundPayload:
    """Coerce a connector-shaped dict into a strict ``EmailInboundPayload``.

    Performs minimal, deterministic conversions only:
    - ``received_at`` accepts ``datetime`` (naive → UTC), ISO 8601 string,
      or missing (defaults to ``datetime.now(timezone.utc)``).
    - ``attachments`` accepts either a list of dicts (converted into
      ``EmailAttachmentMeta``) or a list of already-built
      ``EmailAttachmentMeta`` instances. Raw attachment dicts may carry
      an out-of-band ``body_bytes`` key; the bytes are popped before
      validation (the blackboard stores metadata only) and forwarded to
      ``attachment_inspector`` when one is provided.
    - ``headers`` defaults to an empty dict when omitted.
    - ``received_headers`` defaults to an empty list. Connectors that can
      preserve repeated ``Received:`` fields should pass them in source order
      through this field; if omitted, a single ``Received`` value in
      ``headers`` is copied into the list as a backwards-compatible fallback.

    All other fields pass through to ``EmailInboundPayload`` and are
    validated by its strict pydantic schema (``extra="forbid"``). Unknown
    fields raise ``pydantic.ValidationError``, not ``EmailIngestError``.
    """

    if not isinstance(raw, Mapping):
        raise EmailIngestError(
            f"raw_email must be a Mapping or EmailInboundPayload, got {type(raw).__name__}"
        )

    fields: dict[str, Any] = dict(raw)

    fields["received_at"] = _normalize_received_at(fields.get("received_at"))

    if "attachments" in fields and fields["attachments"] is not None:
        fields["attachments"] = _normalize_attachments(
            fields["attachments"], inspector=attachment_inspector
        )
    else:
        fields.setdefault("attachments", [])

    fields.setdefault("headers", {})
    fields.setdefault("received_headers", _received_headers_from_headers(fields["headers"]))

    return EmailInboundPayload.model_validate(fields)


def _received_headers_from_headers(headers: Any) -> list[str]:
    """Best-effort fallback for legacy connector-shaped header dictionaries.

    RFC 5322 allows repeated ``Received:`` fields, but the historical
    ``EmailInboundPayload.headers`` shape is a ``dict[str, str]`` and therefore
    cannot preserve duplicates. New connectors should pass the additive
    ``received_headers`` list directly. This fallback only preserves one
    already-collapsed value when present; it never tries to split or interpret
    a connector-specific concatenation format.
    """

    if not isinstance(headers, Mapping):
        return []
    for key, value in headers.items():
        if key.lower() == "received" and isinstance(value, str) and value.strip():
            return [value]
    return []


def sha256_attachment_inspector(
    body_bytes: bytes | None, meta: EmailAttachmentMeta
) -> EmailAttachmentMeta:
    """Reference attachment inspector that fills ``sha256`` from raw bytes.

    Acts as a no-op when ``body_bytes`` is ``None`` (the connector did
    not supply the body) or when ``meta.sha256`` is already populated
    (don't clobber a value the connector trusted). Useful as a starting
    inspector for connectors that ship raw bytes but no other deep-
    inspection logic, and as the default reference implementation for
    end-to-end tests.

    Does not touch ``extracted_text`` or ``attachment_class`` — those
    require format-aware inspection that production callers plug in
    separately.
    """

    if body_bytes is None or meta.sha256 is not None:
        return meta
    digest = hashlib.sha256(body_bytes).hexdigest()
    return meta.model_copy(update={"sha256": digest})


def _normalize_received_at(value: Any) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise EmailIngestError(
                f"received_at is not a valid ISO 8601 timestamp: {value!r}"
            ) from exc
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    raise EmailIngestError(
        f"received_at must be a datetime, ISO 8601 string, or omitted; got "
        f"{type(value).__name__}"
    )


def _normalize_attachments(
    value: Any,
    *,
    inspector: AttachmentInspector | None = None,
) -> list[EmailAttachmentMeta]:
    if not isinstance(value, list):
        raise EmailIngestError(
            f"attachments must be a list, got {type(value).__name__}"
        )
    normalized: list[EmailAttachmentMeta] = []
    for index, item in enumerate(value):
        body_bytes: bytes | None = None
        if isinstance(item, EmailAttachmentMeta):
            meta = item
        elif isinstance(item, Mapping):
            raw_dict = dict(item)
            popped = raw_dict.pop(ATTACHMENT_BODY_BYTES_KEY, None)
            if popped is not None and not isinstance(popped, (bytes, bytearray)):
                raise EmailIngestError(
                    f"attachments[{index}].{ATTACHMENT_BODY_BYTES_KEY} must be "
                    f"bytes if provided, got {type(popped).__name__}"
                )
            body_bytes = bytes(popped) if popped is not None else None
            try:
                meta = EmailAttachmentMeta.model_validate(raw_dict)
            except Exception as exc:
                raise EmailIngestError(
                    f"attachments[{index}] failed validation: {exc}"
                ) from exc
        else:
            raise EmailIngestError(
                f"attachments[{index}] must be a Mapping or EmailAttachmentMeta, "
                f"got {type(item).__name__}"
            )

        if inspector is not None:
            meta = _invoke_inspector(inspector, body_bytes, meta, index=index)

        normalized.append(meta)
    return normalized


def _invoke_inspector(
    inspector: AttachmentInspector,
    body_bytes: bytes | None,
    meta: EmailAttachmentMeta,
    *,
    index: int,
) -> EmailAttachmentMeta:
    """Run one attachment inspector and normalize its failure modes.

    Inspector failures (raised exceptions or returns that don't validate
    against ``EmailAttachmentMeta``) surface as ``EmailIngestError`` so
    callers can distinguish "inspector hook misbehaved" from "raw email
    shape was bad" and from "pydantic rejected the normalized payload".
    """

    try:
        inspected = inspector(body_bytes, meta)
    except EmailIngestError:
        raise
    except Exception as exc:  # noqa: BLE001 - intentionally broad
        raise EmailIngestError(
            f"attachments[{index}] inspector raised {type(exc).__name__}: {exc}"
        ) from exc

    if isinstance(inspected, EmailAttachmentMeta):
        candidate: Any = inspected.model_dump()
    elif isinstance(inspected, Mapping):
        candidate = dict(inspected)
    else:
        raise EmailIngestError(
            f"attachments[{index}] inspector must return EmailAttachmentMeta or a "
            f"Mapping, got {type(inspected).__name__}"
        )

    try:
        return EmailAttachmentMeta.model_validate(candidate)
    except Exception as exc:
        raise EmailIngestError(
            f"attachments[{index}] inspector output failed validation: {exc}"
        ) from exc
