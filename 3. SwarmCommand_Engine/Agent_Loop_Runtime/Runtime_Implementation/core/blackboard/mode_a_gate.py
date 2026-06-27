"""Mode A schema gate — Blackboard-Mesh BM-D1 / BM-D2 / BM-D3.

Structural: closed Phase 1 top-level keys only; reject forbidden and writer metadata.
Semantic: authority-shadow token scan inside ``details`` and nested strings.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PHASE1_ALLOWED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "agent_id",
        "tenant_id",
        "email_id",
        "evidence_type",
        "details",
        "confidence",
        "timestamp",
        "stage",
    }
)

FORBIDDEN_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "verdict",
        "conclusion",
        "decision",
        "outcome",
        "final",
        "action",
        "route",
        "block",
        "release",
        "approved",
        "authorized",
        "cleared",
        "safe",
        "disposition",
    }
)

WRITER_METADATA_KEYS: frozenset[str] = frozenset({"entry_id", "schema_version"})

DEFAULT_SHADOW_TOKEN_CONFIG = (
    Path(__file__).resolve().parents[5] / "mmi" / "config" / "authority_shadow_tokens_v1.json"
)

RECONCILIATION_WRITER_AGENT_ID = "reconciliation_agent_001"


class ModeAGateError(ValueError):
    """Evidence or verdict write failed Mode A governance checks."""


def load_authority_shadow_tokens(config_path: Path | None = None) -> frozenset[str]:
    path = config_path or DEFAULT_SHADOW_TOKEN_CONFIG
    payload = json.loads(path.read_text(encoding="utf-8"))
    tokens = payload.get("evidence_tokens", payload.get("tokens", []))
    return frozenset(str(token).lower() for token in tokens)


def load_verdict_narrative_shadow_tokens(config_path: Path | None = None) -> frozenset[str]:
    path = config_path or DEFAULT_SHADOW_TOKEN_CONFIG
    payload = json.loads(path.read_text(encoding="utf-8"))
    tokens = payload.get("verdict_narrative_tokens", [])
    return frozenset(str(token).lower() for token in tokens)


def _token_hits(text: str, tokens: frozenset[str]) -> list[str]:
    lowered = text.lower()
    hits: list[str] = []
    for token in tokens:
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            hits.append(token)
    return hits


def scan_value_for_shadow_tokens(value: Any, tokens: frozenset[str], *, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        for token in _token_hits(value, tokens):
            hits.append(f"{path}:{token}" if path else token)
    elif isinstance(value, dict):
        for key, nested in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if str(key).lower() in tokens:
                hits.append(child_path)
            hits.extend(scan_value_for_shadow_tokens(nested, tokens, path=child_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            hits.extend(scan_value_for_shadow_tokens(nested, tokens, path=child_path))
    return hits


def validate_raw_evidence_dict(
    data: dict[str, Any],
    *,
    shadow_tokens: frozenset[str] | None = None,
) -> None:
    """Fail-closed structural + semantic checks for dict writes (BM-D1–D3, BM-D8)."""

    if not isinstance(data, dict):
        raise ModeAGateError("evidence write rejected: payload must be a dict")

    keys = {str(key) for key in data}
    lowered_keys = {key.lower() for key in keys}

    forbidden = lowered_keys & {k.lower() for k in FORBIDDEN_TOP_LEVEL_KEYS}
    if forbidden:
        raise ModeAGateError(
            f"evidence write rejected: forbidden top-level key(s): {sorted(forbidden)}"
        )

    metadata = keys & WRITER_METADATA_KEYS
    if metadata:
        raise ModeAGateError(
            f"evidence write rejected: writer metadata not allowed at this layer: {sorted(metadata)}"
        )

    extra = keys - PHASE1_ALLOWED_TOP_LEVEL_KEYS
    if extra:
        raise ModeAGateError(
            f"evidence write rejected: unknown top-level key(s): {sorted(extra)}"
        )

    tokens = shadow_tokens if shadow_tokens is not None else load_authority_shadow_tokens()
    details = data.get("details", {})
    shadow_hits = scan_value_for_shadow_tokens(details, tokens, path="details")
    if shadow_hits:
        agent_id = str(data.get("agent_id", "unknown"))
        raise ModeAGateError(
            f"evidence write rejected: authority-shadow token(s) for agent_id={agent_id}: "
            f"{shadow_hits}"
        )


def validate_evidence_entry_semantics(
    entry: Any,
    *,
    shadow_tokens: frozenset[str] | None = None,
) -> None:
    """Semantic scan for validated model instances (details may contain shadow tokens)."""

    tokens = shadow_tokens if shadow_tokens is not None else load_authority_shadow_tokens()
    details = getattr(entry, "details", {})
    shadow_hits = scan_value_for_shadow_tokens(details, tokens, path="details")
    if shadow_hits:
        agent_id = getattr(entry, "agent_id", "unknown")
        raise ModeAGateError(
            f"evidence write rejected: authority-shadow token(s) for agent_id={agent_id}: "
            f"{shadow_hits}"
        )


def validate_verdict_semantics(
    verdict: Any,
    *,
    shadow_tokens: frozenset[str] | None = None,
) -> None:
    """Semantic scan for verdict narrative fields (BM-D5)."""

    tokens = (
        shadow_tokens
        if shadow_tokens is not None
        else load_verdict_narrative_shadow_tokens()
    )
    hits: list[str] = []
    for field in ("plain_english_chain", "minority_opinion", "cirt_individual"):
        value = getattr(verdict, field, "")
        if isinstance(value, str) and value:
            hits.extend(scan_value_for_shadow_tokens(value, tokens, path=field))
    contributing = getattr(verdict, "contributing_evidence", [])
    hits.extend(scan_value_for_shadow_tokens(contributing, tokens, path="contributing_evidence"))
    if hits:
        raise ModeAGateError(
            f"verdict write rejected: authority-shadow token(s): {hits}"
        )


def assert_verdict_writer_allowed(writer_agent_id: str) -> None:
    if writer_agent_id != RECONCILIATION_WRITER_AGENT_ID:
        raise ModeAGateError(
            "verdict write rejected: only reconciliation_agent_001 may append to VerdictLedger"
        )
