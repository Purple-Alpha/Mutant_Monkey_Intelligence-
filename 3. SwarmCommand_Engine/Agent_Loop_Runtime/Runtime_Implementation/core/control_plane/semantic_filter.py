"""SemanticFilter — gateway-side DER payload hardening (detect-not-enact)."""

from __future__ import annotations

import re
from typing import Any

_FORBIDDEN_DER_TOKENS: frozenset[str] = frozenset(
    {
        "approved",
        "authorized",
        "safe_to_process",
        "gate_satisfied",
    }
)

_FORBIDDEN_VERDICT_TOKENS: frozenset[str] = frozenset(
    {
        "low_risk",
        "safe",
        "suppression_applied",
        "approval_recommended",
    }
)

_FORBIDDEN_AUTHORITY_KEYS: frozenset[str] = frozenset(
    {
        "authority",
        "verdict",
        "disposition",
        "human_state",
        "swarm_disposition",
    }
)

_DER_ROOT_KEYS: frozenset[str] = frozenset(
    {
        "contributions",
        "disposition",
        "human_state",
        "decision_id",
        "inputs_digest",
        "decision_evidence_record",
        "observed_facts",
    }
)


def requires_der_scan(value: Any) -> bool:
    if isinstance(value, dict):
        keys = {str(key).lower() for key in value}
        if keys & _DER_ROOT_KEYS:
            return True
    return False


class SemanticFilterViolation(ValueError):
    """Payload contains forbidden enactment or verdict language."""


class SemanticFilter:
    """Scan DecisionEvidenceRecords and nested gateway payloads."""

    def _token_hits(self, text: str, tokens: frozenset[str], prefix: str) -> list[str]:
        lowered = text.lower()
        hits: list[str] = []
        for token in tokens:
            if re.search(rf"\b{re.escape(token)}\b", lowered):
                hits.append(f"{prefix}:{token}")
        return hits

    def scan_text(self, text: str) -> tuple[str, ...]:
        hits = self._token_hits(text, _FORBIDDEN_DER_TOKENS, "forbidden_der_token")
        hits.extend(
            self._token_hits(text, _FORBIDDEN_VERDICT_TOKENS, "forbidden_verdict_token")
        )
        return tuple(hits)

    def scan_value(self, value: Any, *, path: str = "") -> tuple[str, ...]:
        hits: list[str] = []
        if isinstance(value, str):
            for hit in self.scan_text(value):
                hits.append(f"{path}:{hit}" if path else hit)
        elif isinstance(value, dict):
            for key, nested in value.items():
                key_str = str(key)
                if key_str.lower() in _FORBIDDEN_AUTHORITY_KEYS:
                    hits.append(f"{path}.{key_str}:forbidden_authority_key")
                child_path = f"{path}.{key_str}" if path else key_str
                hits.extend(self.scan_value(nested, path=child_path))
        elif isinstance(value, (list, tuple, set)):
            for index, item in enumerate(value):
                child_path = f"{path}[{index}]" if path else f"[{index}]"
                hits.extend(self.scan_value(item, path=child_path))
        return tuple(hits)

    def scan_decision_evidence_record(self, record) -> tuple[str, ...]:
        payload = record.model_dump(mode="json")
        return self.scan_value(payload, path="der")

    def reject_if_forbidden(self, value: Any) -> None:
        violations = self.scan_value(value)
        if violations:
            raise SemanticFilterViolation(
                "semantic filter rejected payload: " + "; ".join(violations)
            )


__all__ = ["SemanticFilter", "SemanticFilterViolation", "requires_der_scan"]
