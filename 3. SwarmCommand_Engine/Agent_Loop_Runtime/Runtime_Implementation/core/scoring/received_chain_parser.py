"""Received-header chain parser foundation for future sender provenance work.

This module intentionally does **not** score, baseline, geolocate, perform DNS,
or call ASN / GeoIP services. It only turns preserved ``Received:`` header
values into bounded metadata that a future §11-signed sender-provenance detector
can consume after the cheaper-proof step passes.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Sequence


_FROM_HOST_RE = re.compile(r"\bfrom\s+(?P<host>[^\s;()]+)", re.IGNORECASE)
_BY_HOST_RE = re.compile(r"\bby\s+(?P<host>[^\s;()]+)", re.IGNORECASE)
_BRACKETED_IP_RE = re.compile(r"\[(?P<ip>[0-9A-Fa-f:.]+)\]")
_BARE_IPV4_RE = re.compile(r"(?<![\w.])(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?![\w.])")


@dataclass(frozen=True)
class ReceivedHop:
    """Sanitized metadata extracted from one ``Received:`` header.

    ``position`` is the index in the preserved header list. The parser does not
    emit the raw header string so downstream analysis cannot accidentally leak
    mailbox infrastructure details in a client-visible report.
    """

    position: int
    from_host: str | None
    by_host: str | None
    ip_addresses: tuple[str, ...]


@dataclass(frozen=True)
class ReceivedChain:
    """Parsed ``Received:`` chain summary.

    ``hop_count`` reflects all non-empty header values supplied. ``hops`` holds
    one sanitized :class:`ReceivedHop` per non-empty header.
    """

    hop_count: int
    hops: tuple[ReceivedHop, ...]


def parse_received_chain(received_headers: Sequence[str] | None) -> ReceivedChain:
    """Parse preserved ``Received:`` values into sanitized hop metadata.

    Inputs are expected to be in the same order the connector preserved them.
    No assumption is made about newest-first vs. oldest-first ordering because
    connector export formats vary. Future sender-provenance logic must make an
    explicit trusted-hop decision in its own signed spec.
    """

    if not received_headers:
        return ReceivedChain(hop_count=0, hops=())

    hops: list[ReceivedHop] = []
    for position, header_value in enumerate(received_headers):
        if not isinstance(header_value, str) or not header_value.strip():
            continue
        hops.append(
            ReceivedHop(
                position=position,
                from_host=_extract_host(_FROM_HOST_RE, header_value),
                by_host=_extract_host(_BY_HOST_RE, header_value),
                ip_addresses=_extract_ip_addresses(header_value),
            )
        )
    return ReceivedChain(hop_count=len(hops), hops=tuple(hops))


def _extract_host(pattern: re.Pattern[str], header_value: str) -> str | None:
    match = pattern.search(header_value)
    if not match:
        return None
    host = _clean_host_token(match.group("host"))
    return host or None


def _clean_host_token(token: str) -> str:
    cleaned = token.strip().strip("[]<>;,").lower()
    return cleaned if cleaned else ""


def _extract_ip_addresses(header_value: str) -> tuple[str, ...]:
    seen: set[str] = set()
    found: list[str] = []

    for candidate in _ip_candidates(header_value):
        try:
            parsed = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        normalized = str(parsed)
        if normalized in seen:
            continue
        seen.add(normalized)
        found.append(normalized)

    return tuple(found)


def _ip_candidates(header_value: str) -> list[str]:
    candidates: list[str] = []
    candidates.extend(match.group("ip") for match in _BRACKETED_IP_RE.finditer(header_value))
    candidates.extend(match.group("ip") for match in _BARE_IPV4_RE.finditer(header_value))
    return candidates


__all__ = [
    "ReceivedChain",
    "ReceivedHop",
    "parse_received_chain",
]
