"""Tests for the Received-chain parser foundation.

These tests intentionally stop short of sender-provenance scoring. Option C is
only the safe foundation: preserve repeated ``Received:`` headers and parse
sanitized host/IP metadata for a future signed detector.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import ValidationError

from core.blackboard import EmailInboundPayload
from core.ingest.email_ingest_agent import normalize_raw_email
from core.scoring.received_chain_parser import (
    ReceivedChain,
    ReceivedHop,
    parse_received_chain,
)


def _raw_email(**overrides: object) -> dict[str, object]:
    raw: dict[str, object] = {
        "received_at": datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        "sender": "billing@vendor.example",
        "recipient": "ap@customer.example",
        "subject": "Invoice",
        "body_plain": "Please process the attached invoice.",
        "headers": {},
    }
    raw.update(overrides)
    return raw


def test_email_inbound_payload_defaults_received_headers_to_empty_list() -> None:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@customer.example",
        subject="Invoice",
        body_plain="Please process the attached invoice.",
        headers={},
    )
    assert payload.received_headers == []


def test_email_inbound_payload_preserves_connector_received_headers_order() -> None:
    payload = normalize_raw_email(
        _raw_email(
            received_headers=[
                "from vendor.example (vendor.example [203.0.113.10]) by mx.customer.example;",
                "from relay.vendor.example (relay.vendor.example [198.51.100.7]) by vendor.example;",
            ]
        )
    )
    assert payload.received_headers == [
        "from vendor.example (vendor.example [203.0.113.10]) by mx.customer.example;",
        "from relay.vendor.example (relay.vendor.example [198.51.100.7]) by vendor.example;",
    ]


def test_normalize_raw_email_falls_back_to_single_received_header_value() -> None:
    payload = normalize_raw_email(
        _raw_email(
            headers={
                "Received": "from relay.vendor.example ([203.0.113.10]) by mx.customer.example;",
            }
        )
    )
    assert payload.received_headers == [
        "from relay.vendor.example ([203.0.113.10]) by mx.customer.example;",
    ]


def test_connector_received_headers_list_wins_over_collapsed_header_fallback() -> None:
    payload = normalize_raw_email(
        _raw_email(
            headers={
                "Received": "from collapsed.example ([203.0.113.1]) by mx.customer.example;",
            },
            received_headers=[
                "from first.example ([203.0.113.10]) by mx.customer.example;",
                "from second.example ([198.51.100.20]) by first.example;",
            ],
        )
    )
    assert payload.received_headers == [
        "from first.example ([203.0.113.10]) by mx.customer.example;",
        "from second.example ([198.51.100.20]) by first.example;",
    ]


def test_received_headers_rejects_non_string_entries() -> None:
    try:
        EmailInboundPayload(
            received_at=datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
            sender="billing@vendor.example",
            recipient="ap@customer.example",
            subject="Invoice",
            body_plain="Please process the attached invoice.",
            headers={},
            received_headers=["valid", 123],  # type: ignore[list-item]
        )
    except ValidationError as exc:
        assert "received_headers" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("expected ValidationError for non-string received header")


def test_parse_received_chain_empty_input() -> None:
    assert parse_received_chain(None) == ReceivedChain(hop_count=0, hops=())
    assert parse_received_chain([]) == ReceivedChain(hop_count=0, hops=())


def test_parse_received_chain_extracts_from_by_and_ip_metadata() -> None:
    chain = parse_received_chain(
        [
            "from relay.vendor.example (relay.vendor.example [203.0.113.10]) "
            "by mx.customer.example with ESMTPS id abc123;",
        ]
    )
    assert chain == ReceivedChain(
        hop_count=1,
        hops=(
            ReceivedHop(
                position=0,
                from_host="relay.vendor.example",
                by_host="mx.customer.example",
                ip_addresses=("203.0.113.10",),
            ),
        ),
    )


def test_parse_received_chain_handles_ipv6_and_bare_ipv4() -> None:
    chain = parse_received_chain(
        [
            "from mail.vendor.example ([2001:db8::5]) by mx.customer.example;",
            "from backup.vendor.example (198.51.100.9) by mail.vendor.example;",
        ]
    )
    assert chain.hop_count == 2
    assert chain.hops[0].ip_addresses == ("2001:db8::5",)
    assert chain.hops[1].ip_addresses == ("198.51.100.9",)


def test_parse_received_chain_deduplicates_ip_addresses_per_hop() -> None:
    chain = parse_received_chain(
        [
            "from relay.vendor.example ([203.0.113.10]) "
            "by mx.customer.example (203.0.113.10);",
        ]
    )
    assert chain.hops[0].ip_addresses == ("203.0.113.10",)


def test_parse_received_chain_ignores_malformed_ip_candidates() -> None:
    chain = parse_received_chain(
        [
            "from relay.vendor.example ([999.999.999.999]) by mx.customer.example;",
        ]
    )
    assert chain.hops[0].from_host == "relay.vendor.example"
    assert chain.hops[0].by_host == "mx.customer.example"
    assert chain.hops[0].ip_addresses == ()


def test_parse_received_chain_does_not_emit_raw_header_strings() -> None:
    raw = "from secret.internal.example ([203.0.113.10]) by mx.customer.example;"
    chain = parse_received_chain([raw])
    assert raw not in repr(chain)
    assert all(not hasattr(hop, "raw_header") for hop in chain.hops)
