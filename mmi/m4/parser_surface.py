"""Strict parser surfaces for M4 evidence, manifest, and canary rules (§6 parser target)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


class ParseSurfaceError(ValueError):
    """Malformed input rejected fail-closed."""


REQUIRED_SUMMARY_FIELDS = frozenset(
    {
        "schema",
        "stage_id",
        "run_mode",
        "overall_gate_status",
        "chain_verified",
        "perfect_claim",
    }
)


def _reject_trailing_garbage(text: str, end: int) -> None:
    tail = text[end:].strip()
    if tail:
        raise ParseSurfaceError("trailing garbage after JSON document")


def parse_evidence_json(text: str) -> dict[str, Any]:
    """Parse evidence/summary JSON; reject truncation and trailing bytes."""
    if not text or not text.strip():
        raise ParseSurfaceError("empty document")
    try:
        obj, end = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError as exc:
        raise ParseSurfaceError(f"invalid JSON: {exc}") from exc
    _reject_trailing_garbage(text, end)
    if not isinstance(obj, dict):
        raise ParseSurfaceError("root must be object")
    return obj


def parse_summary_json(text: str) -> dict[str, Any]:
    obj = parse_evidence_json(text)
    missing = REQUIRED_SUMMARY_FIELDS - obj.keys()
    if missing:
        raise ParseSurfaceError(f"missing required summary fields: {sorted(missing)}")
    if obj.get("perfect_claim") is not False:
        raise ParseSurfaceError("perfect_claim must be false")
    return obj


def parse_manifest(text: str) -> dict[str, Any]:
    obj = parse_evidence_json(text)
    if "manifest_version" not in obj:
        raise ParseSurfaceError("manifest_version required")
    if not isinstance(obj["manifest_version"], (str, int)):
        raise ParseSurfaceError("manifest_version must be string or int")
    return obj


@dataclass(frozen=True)
class CanaryRule:
    rule_id: str
    threshold: float
    comparator: str  # gt, gte, lt, lte, eq


def parse_canary_rules(text: str) -> list[CanaryRule]:
    obj = parse_evidence_json(text)
    raw = obj.get("rules")
    if not isinstance(raw, list) or not raw:
        raise ParseSurfaceError("rules must be non-empty list")
    rules: list[CanaryRule] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ParseSurfaceError(f"rule[{idx}] must be object")
        rule_id = item.get("rule_id")
        threshold = item.get("threshold")
        comparator = item.get("comparator")
        if not isinstance(rule_id, str) or not rule_id:
            raise ParseSurfaceError(f"rule[{idx}] rule_id invalid")
        if not isinstance(threshold, (int, float)):
            raise ParseSurfaceError(f"rule[{idx}] threshold invalid")
        if comparator not in {"gt", "gte", "lt", "lte", "eq"}:
            raise ParseSurfaceError(f"rule[{idx}] comparator invalid")
        rules.append(CanaryRule(rule_id, float(threshold), comparator))
    return rules
