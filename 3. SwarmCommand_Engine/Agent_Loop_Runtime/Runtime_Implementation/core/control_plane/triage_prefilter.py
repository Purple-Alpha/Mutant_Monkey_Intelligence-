"""Gateway triage pre-filter — #3 RiskTriage read-only (flag-not-drop)."""

from __future__ import annotations

from typing import Any, Protocol


class TriagePreFilter(Protocol):
    """Read-only triage seam for GatewayController."""

    def score_gateway_request(self, request: Any, tenant_id: str) -> Any | None: ...


class RiskTriageGatewayPreFilter:
    """#3 RiskTriageAgent as gateway edge scorer — detect-not-enact."""

    def __init__(self, triage_agent: Any | None = None) -> None:
        self._triage = triage_agent

    def score_gateway_request(self, request: Any, tenant_id: str) -> Any | None:
        from core.command.risk_triage_agent import (
            DetectorEvidenceRecord,
            RiskTriageAgent,
            RiskTriageInput,
            SCORING_POLICY_VERSION,
        )

        triage = self._triage or RiskTriageAgent()
        payload = _payload_from_gateway_args(
            getattr(request, "args", None),
            tenant_id=tenant_id,
            detector_record_type=DetectorEvidenceRecord,
            input_type=RiskTriageInput,
            policy_version=SCORING_POLICY_VERSION,
        )
        if payload is None:
            return None
        result = triage.score(payload)
        if result.kind != "success" or result.telemetry is None:
            return None
        return result.telemetry


def _payload_from_gateway_args(
    args: Any,
    *,
    tenant_id: str,
    detector_record_type,
    input_type,
    policy_version,
):
    if not isinstance(args, dict):
        return None
    block = args.get("risk_triage_prefilter")
    if block is None:
        return None
    if not isinstance(block, dict):
        raise ValueError("risk_triage_prefilter must be a dict when present")
    message_id = str(block.get("message_id", "")).strip()
    if not message_id:
        return None
    outputs_raw = block.get("detector_outputs", ())
    outputs: list = []
    if isinstance(outputs_raw, (list, tuple)):
        for item in outputs_raw:
            if isinstance(item, detector_record_type):
                outputs.append(item)
            elif isinstance(item, dict):
                outputs.append(
                    detector_record_type(
                        detector_id=str(item.get("detector_id", "")),
                        detector_contract_version=str(
                            item.get("detector_contract_version", "")
                        ),
                        evidence_ref=str(item.get("evidence_ref", "")),
                        emitted_at=str(item.get("emitted_at", "")),
                        signal_tags=tuple(item.get("signal_tags", ()) or ()),
                        extra_fields=frozenset(item.get("extra_fields", ()) or ()),
                    )
                )
    policy = str(block.get("scoring_policy_version", policy_version))
    return input_type(
        message_id=message_id,
        tenant_id=tenant_id,
        detector_outputs=tuple(outputs),
        scoring_policy_version=policy,
    )


__all__ = ["TriagePreFilter", "RiskTriageGatewayPreFilter"]
