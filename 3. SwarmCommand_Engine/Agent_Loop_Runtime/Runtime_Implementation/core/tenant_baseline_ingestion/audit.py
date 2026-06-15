"""Hash-chained audit log for Tenant Baseline Ingestion."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from core.tenant_baseline_ingestion.state import (
    ActorType,
    ApprovalPolicy,
    AuditEventType,
    PromotionDecision,
    RiskTier,
)

GENESIS_HASH = "0" * 64


class BaselineAuditError(Exception):
    """Raised when audit records are malformed or tampered."""


@dataclass(frozen=True)
class BaselineAuditRecord:
    tenant_id: str
    event_type: AuditEventType
    actor_type: ActorType
    actor_id: str
    baseline_key: str
    old_baseline_version: int | None
    new_baseline_version: int | None
    evidence_ids: tuple[str, ...]
    decision: PromotionDecision
    promotion_reason_codes: tuple[str, ...]
    risk_tier: RiskTier
    approval_policy: ApprovalPolicy
    request_context: Mapping[str, Any]
    separation_of_duties: Mapping[str, Any]
    rollback_status: str
    rollback_blast_radius: Mapping[str, Any]
    previous_audit_signature: str
    audit_event_id: str = field(default_factory=lambda: str(uuid4()))
    event_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_signature: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "request_context", MappingProxyType(dict(self.request_context))
        )
        object.__setattr__(
            self, "separation_of_duties", MappingProxyType(dict(self.separation_of_duties))
        )
        object.__setattr__(
            self, "rollback_blast_radius", MappingProxyType(dict(self.rollback_blast_radius))
        )
        if not self.audit_signature:
            object.__setattr__(self, "audit_signature", self.compute_signature())

    def compute_signature(self) -> str:
        payload = {
            "audit_event_id": self.audit_event_id,
            "tenant_id": self.tenant_id,
            "event_time": self.event_time.isoformat(),
            "event_type": self.event_type.value,
            "actor_type": self.actor_type.value,
            "actor_id": self.actor_id,
            "baseline_key": self.baseline_key,
            "old_baseline_version": self.old_baseline_version,
            "new_baseline_version": self.new_baseline_version,
            "evidence_ids": list(self.evidence_ids),
            "decision": self.decision.value,
            "promotion_reason_codes": list(self.promotion_reason_codes),
            "risk_tier": self.risk_tier.value,
            "approval_policy": self.approval_policy.value,
            "request_context": dict(self.request_context),
            "separation_of_duties": dict(self.separation_of_duties),
            "rollback_status": self.rollback_status,
            "rollback_blast_radius": dict(self.rollback_blast_radius),
            "previous_audit_signature": self.previous_audit_signature,
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass
class BaselineAuditLog:
    """Append-only hash-chained audit log; no update/delete API."""

    jsonl_path: Path | None = None
    _records: list[BaselineAuditRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.jsonl_path is not None and Path(self.jsonl_path).exists():
            with Path(self.jsonl_path).open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        self._records.append(_record_from_json(json.loads(line)))

    def record(
        self,
        *,
        tenant_id: str,
        event_type: AuditEventType,
        actor_type: ActorType,
        actor_id: str,
        baseline_key: str,
        old_baseline_version: int | None,
        new_baseline_version: int | None,
        evidence_ids: tuple[str, ...],
        decision: PromotionDecision,
        promotion_reason_codes: tuple[str, ...],
        risk_tier: RiskTier,
        approval_policy: ApprovalPolicy,
        request_context: Mapping[str, Any],
        separation_of_duties: Mapping[str, Any],
        rollback_status: str = "",
        rollback_blast_radius: Mapping[str, Any] | None = None,
    ) -> BaselineAuditRecord:
        previous = self._records[-1].audit_signature if self._records else GENESIS_HASH
        entry = BaselineAuditRecord(
            tenant_id=tenant_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            baseline_key=baseline_key,
            old_baseline_version=old_baseline_version,
            new_baseline_version=new_baseline_version,
            evidence_ids=evidence_ids,
            decision=decision,
            promotion_reason_codes=promotion_reason_codes,
            risk_tier=risk_tier,
            approval_policy=approval_policy,
            request_context=request_context,
            separation_of_duties=separation_of_duties,
            rollback_status=rollback_status,
            rollback_blast_radius=rollback_blast_radius or {},
            previous_audit_signature=previous,
        )
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        self._records.append(entry)
        return entry

    def entries(self) -> tuple[BaselineAuditRecord, ...]:
        return tuple(self._records)

    def validate_chain(self) -> bool:
        previous = GENESIS_HASH
        for record in self._records:
            if record.previous_audit_signature != previous:
                return False
            if record.audit_signature != record.compute_signature():
                return False
            previous = record.audit_signature
        return True

    def _append_jsonl(self, entry: BaselineAuditRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "audit_event_id": entry.audit_event_id,
                        "tenant_id": entry.tenant_id,
                        "event_time": entry.event_time.isoformat(),
                        "event_type": entry.event_type.value,
                        "actor_type": entry.actor_type.value,
                        "actor_id": entry.actor_id,
                        "baseline_key": entry.baseline_key,
                        "old_baseline_version": entry.old_baseline_version,
                        "new_baseline_version": entry.new_baseline_version,
                        "evidence_ids": list(entry.evidence_ids),
                        "decision": entry.decision.value,
                        "promotion_reason_codes": list(entry.promotion_reason_codes),
                        "risk_tier": entry.risk_tier.value,
                        "approval_policy": entry.approval_policy.value,
                        "request_context": dict(entry.request_context),
                        "separation_of_duties": dict(entry.separation_of_duties),
                        "rollback_status": entry.rollback_status,
                        "rollback_blast_radius": dict(entry.rollback_blast_radius),
                        "previous_audit_signature": entry.previous_audit_signature,
                        "audit_signature": entry.audit_signature,
                    },
                    sort_keys=True,
                )
                + "\n"
            )


def _record_from_json(payload: Mapping[str, Any]) -> BaselineAuditRecord:
    return BaselineAuditRecord(
        audit_event_id=str(payload["audit_event_id"]),
        tenant_id=str(payload["tenant_id"]),
        event_time=datetime.fromisoformat(str(payload["event_time"])),
        event_type=AuditEventType(str(payload["event_type"])),
        actor_type=ActorType(str(payload["actor_type"])),
        actor_id=str(payload["actor_id"]),
        baseline_key=str(payload["baseline_key"]),
        old_baseline_version=payload["old_baseline_version"],
        new_baseline_version=payload["new_baseline_version"],
        evidence_ids=tuple(payload["evidence_ids"]),
        decision=PromotionDecision(str(payload["decision"])),
        promotion_reason_codes=tuple(payload["promotion_reason_codes"]),
        risk_tier=RiskTier(str(payload["risk_tier"])),
        approval_policy=ApprovalPolicy(str(payload["approval_policy"])),
        request_context=dict(payload["request_context"]),
        separation_of_duties=dict(payload["separation_of_duties"]),
        rollback_status=str(payload["rollback_status"]),
        rollback_blast_radius=dict(payload["rollback_blast_radius"]),
        previous_audit_signature=str(payload["previous_audit_signature"]),
        audit_signature=str(payload["audit_signature"]),
    )


__all__ = [
    "GENESIS_HASH",
    "BaselineAuditError",
    "BaselineAuditRecord",
    "BaselineAuditLog",
]
