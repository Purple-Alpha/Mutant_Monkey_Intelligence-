"""PrivacyFilterPipeline — the mandatory five-stage broadcast safety gate.

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Contract.md`` — §15 SIGNED 2026-06-14
(Matt Nichol). Scoreboard row #93 (Layer 6 Control Plane).

Every item bound for cross-tenant broadcast passes through all five stages in
order (PF-D4): entity detection → policy lookup → transformation → validation →
audit record. No stage is skippable and there is no shortcut path. Every failure
condition fails closed (PF-D2): on any failure nothing broadcasts — not a
filtered version, not a degraded version, nothing. The no-raw-identifier
invariant (PF-D5) is enforced by transformation (stage 3) and *proven* by
validation (stage 4) before anything is released. The audit record (stage 5) is
part of the pipeline (PF-D7): an operation that cannot be audited does not
complete.

The filter has its own circuit breaker (PF-D3 / BRC-D5) keyed by
``privacy_filter_breaker_key`` — an independent failure domain, never shared with
any tenant/agent/tool breaker.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import html
import json
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import unquote

from core.control_plane.breaker import BreakerStore, TripClass
from core.control_plane.privacy_filter import privacy_filter_breaker_key
from core.privacy_filter.log import (
    AuditWriteError,
    PrivacyAuditRecord,
    PrivacyFilterAuditLog,
)
from core.privacy_filter.policy import PolicyResolutionError, PolicyStore
from core.privacy_filter.state import (
    NEVER_RAW_IN_OUTPUT,
    BlockReason,
    BroadcastCandidate,
    BroadcastDecision,
    DetectedEntity,
    EntityKind,
    Granularity,
    SharingPolicy,
    SharingScope,
)

# Derived-value prefixes: a value carrying one of these is already a privacy-safe
# one-way hash / generalized category, never raw content (so detection skips it).
HASH_PREFIX = "h:"
GEN_PREFIX = "g:"

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_ACCT_RE = re.compile(r"\b\d{6,}\b")
_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\ufeff\x00]")
_GEO_RE = re.compile(r"\b-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}\b")
_EXACT_TS_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})?\b")
_TENANT_HINT_RE = re.compile(
    r"(tenant|client|vendor|account|routing|iban|bank|invoice|mailbox|"
    r"embedding|baseline|allowlist|suppression|debug|trace|correlation|"
    r"partition|topic|queue|cache|tooltip|breadcrumb|sentry|apm|blob|"
    r"filename|path|backfill|training|model|vector|token|receipt|ack|"
    r"authorization)",
    re.IGNORECASE,
)
_OPAQUE_HINT_RE = re.compile(r"(compressed|encrypted|signed_blob|opaque|base64_blob)")
_RAW_EMAIL_FIELDS = frozenset(
    {"raw_email", "email_body", "headers", "subject", "body", "raw_content"}
)
_SAFE_FIELD_NAMES = frozenset(
    {
        "indicator",
        "pattern",
        "category",
        "count",
        "cohort_size",
        "event_type",
        "signal",
        "confidence",
        "reason",
        "summary",
    }
)


def _hash(value: str) -> str:
    return HASH_PREFIX + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _canonical_forms(value: object) -> tuple[str, ...]:
    if isinstance(value, (dict, list, tuple, set)):
        raw = json.dumps(value, sort_keys=True, default=str)
    else:
        raw = str(value)
    forms: set[str] = {raw}
    normalized = unicodedata.normalize("NFKC", raw)
    forms.add(normalized)
    forms.add(_ZERO_WIDTH_RE.sub("", normalized))
    forms.add(unquote(normalized))
    forms.add(html.unescape(normalized))
    try:
        forms.add(normalized.encode("ascii").decode("idna"))
    except (UnicodeError, ValueError):
        pass
    try:
        decoded = base64.b64decode(normalized, validate=True).decode("utf-8")
        forms.add(decoded)
        forms.add(unicodedata.normalize("NFKC", decoded))
    except (binascii.Error, UnicodeDecodeError, ValueError):
        pass
    return tuple(forms)


def _contains_tenant_marker(value: object, tenant_id: str) -> bool:
    tenant_forms = {f.lower() for f in _canonical_forms(tenant_id)}
    for form in _canonical_forms(value):
        lowered = form.lower()
        if any(marker and marker in lowered for marker in tenant_forms):
            return True
    return False


def detect_entities(content: dict[str, str], tenant_id: str) -> list[DetectedEntity]:
    """Stage 1 + the validation re-scan: flag tenant-identifying / sensitive
    entities (§3.1). Values already in derived (hashed/generalized) form are
    privacy-safe by construction and are not flagged."""

    found: list[DetectedEntity] = []
    aggregate_value = ""
    for fname, raw in content.items():
        aggregate_value += "".join(_canonical_forms(raw))
        value = str(raw)
        forms = _canonical_forms(raw)
        key_forms = _canonical_forms(fname)
        lf = fname.lower()
        if (
            value.startswith((HASH_PREFIX, GEN_PREFIX))
            and lf in _SAFE_FIELD_NAMES
            and not _contains_tenant_marker(fname, tenant_id)
        ):
            continue
        joined_forms = "\n".join(forms + key_forms)
        if tenant_id and (
            _contains_tenant_marker(raw, tenant_id)
            or _contains_tenant_marker(fname, tenant_id)
        ):
            found.append(DetectedEntity(EntityKind.TENANT_ID, fname, value))
        if _EMAIL_RE.search(joined_forms):
            found.append(DetectedEntity(EntityKind.EMAIL, fname, value))
        if _IP_RE.search(joined_forms):
            found.append(DetectedEntity(EntityKind.IP_ADDRESS, fname, value))
        if "name" in lf:
            found.append(DetectedEntity(EntityKind.NAME, fname, value))
        if "address" in lf:
            found.append(DetectedEntity(EntityKind.ADDRESS, fname, value))
        if lf in _RAW_EMAIL_FIELDS:
            found.append(DetectedEntity(EntityKind.RAW_EMAIL_CONTENT, fname, value))
        if _ACCT_RE.search(joined_forms) and not _IP_RE.search(joined_forms):
            found.append(DetectedEntity(EntityKind.ACCOUNT_NUMBER, fname, value))
        if _GEO_RE.search(joined_forms) or _EXACT_TS_RE.search(joined_forms):
            found.append(DetectedEntity(EntityKind.INFRA_FINGERPRINT, fname, value))
        if (
            lf not in _SAFE_FIELD_NAMES
            and _TENANT_HINT_RE.search(lf)
        ):
            found.append(DetectedEntity(EntityKind.INFRA_FINGERPRINT, fname, value))
        if _OPAQUE_HINT_RE.search(lf) or _OPAQUE_HINT_RE.search(value):
            found.append(DetectedEntity(EntityKind.INFRA_FINGERPRINT, fname, value))
    if tenant_id and _contains_tenant_marker(aggregate_value, tenant_id):
        found.append(DetectedEntity(EntityKind.TENANT_ID, "__aggregate__", aggregate_value))
    return found


def default_transform(
    candidate: BroadcastCandidate,
    entities: list[DetectedEntity],
    policy: SharingPolicy,
) -> tuple[dict[str, str], tuple[str, ...]]:
    """Stage 3 transformation (§3.3). Applies the resolved policy granularity and
    always enforces the PF-D5 invariant: no raw never-eligible entity survives,
    regardless of granularity (even FULL strips raw tenant identifiers)."""

    entity_fields = {e.field_name for e in entities if e.kind in NEVER_RAW_IN_OUTPUT}
    actions: list[str] = []
    output: dict[str, str] = {}

    for fname, raw in candidate.content.items():
        value = str(raw)
        if policy.granularity is Granularity.HASH_ONLY:
            output[fname] = _hash(value)
            actions.append(f"hash:{fname}")
            continue
        if fname in entity_fields:
            if policy.granularity is Granularity.GENERALIZED:
                output[fname] = GEN_PREFIX + "category"
                actions.append(f"generalize:{fname}")
            else:  # FULL — invariant still strips raw identifiers
                actions.append(f"strip:{fname}")
            continue
        output[fname] = value
        actions.append(f"passthrough:{fname}")

    return output, tuple(actions)


@dataclass(frozen=True)
class FilterResult:
    """Outcome of one pipeline run."""

    decision: BroadcastDecision
    payload_ref: str | None
    block_reason: BlockReason | None
    record: PrivacyAuditRecord
    output: dict[str, str] | None = None

    @property
    def broadcast(self) -> bool:
        return self.decision is BroadcastDecision.BROADCAST


Transformer = Callable[
    [BroadcastCandidate, list[DetectedEntity], SharingPolicy],
    "tuple[dict[str, str], tuple[str, ...]]",
]


@dataclass
class PrivacyFilterPipeline:
    """The separate Privacy Filter service (PF-D1): own pipeline, own breaker.

    ``transformer`` is injectable only so tests can simulate a compromised
    transformation stage and prove stage 4 validation is a real, non-skippable
    backstop (PF-D4). Production uses ``default_transform``.
    """

    policies: PolicyStore
    audit: PrivacyFilterAuditLog
    breakers: BreakerStore = field(default_factory=BreakerStore)
    transformer: Transformer = default_transform

    def _input_ref(self, candidate: BroadcastCandidate) -> str:
        blob = json.dumps(
            {
                "workflow_id": candidate.workflow_id,
                "tenant_id": candidate.tenant_id,
                "signal_type": candidate.signal_type.value,
                "content": candidate.content,
            },
            sort_keys=True,
        )
        return _hash(blob)

    def _audit(
        self,
        candidate: BroadcastCandidate,
        *,
        entry_ts,
        entities: list[DetectedEntity],
        policy_applied: str,
        transformation_applied: tuple[str, ...],
        validation_passed: bool,
        decision: BroadcastDecision,
        block_reason: BlockReason | None,
    ) -> PrivacyAuditRecord:
        return self.audit.record(
            PrivacyAuditRecord(
                workflow_id=candidate.workflow_id,
                input_ref=self._input_ref(candidate),
                tenant_id=candidate.tenant_id,
                entry_timestamp=entry_ts,
                exit_timestamp=self.audit.now(),
                entity_findings=tuple(e.kind for e in entities),
                policy_applied=policy_applied,
                transformation_applied=transformation_applied,
                validation_passed=validation_passed,
                decision=decision,
                block_reason=block_reason,
            )
        )

    def filter(self, candidate: BroadcastCandidate) -> FilterResult:
        """Run the full mandatory five-stage pipeline. Returns a FilterResult.

        Fails closed at the first failing stage; an audit record is written for
        every outcome (PF-D7/PF-D9). If the audit write itself fails, the filter
        breaker trips and nothing broadcasts.
        """

        entry_ts = self.audit.now()
        pf_key = privacy_filter_breaker_key(candidate.tenant_id)

        # --- Stage 0: independent breaker gate (PF-D2/PF-D3, §4) -------------
        if not self.breakers.is_closed(pf_key):
            return self._blocked(
                candidate, entry_ts, [], "n/a", (), BlockReason.BREAKER_OPEN
            )

        # --- Stage 1: entity detection (§3.1) -------------------------------
        entities = detect_entities(candidate.content, candidate.tenant_id)
        if any(e.kind in NEVER_RAW_IN_OUTPUT for e in entities):
            return self._blocked(
                candidate,
                entry_ts,
                entities,
                "n/a",
                (),
                BlockReason.VALIDATION_RAW_IDENTIFIER,
            )

        # --- Stage 2: policy lookup (§3.2, PF-D6) ---------------------------
        try:
            policy = self.policies.resolve(candidate.tenant_id)
        except PolicyResolutionError as exc:
            return self._blocked(candidate, entry_ts, entities, "n/a", (), exc.reason)

        policy_applied = f"{policy.policy_version}/{policy.granularity.value}"

        if not policy.pipeda_consent:  # PF-D8 / §7
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, (),
                BlockReason.PIPEDA_CONSENT_ABSENT,
            )
        if policy.sharing_scope is SharingScope.NONE:
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, (),
                BlockReason.SCOPE_NONE,
            )
        if policy.granularity is Granularity.BLOCKED:
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, (),
                BlockReason.GRANULARITY_BLOCKED,
            )
        if candidate.signal_type not in policy.allowed_signals:  # §6
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, (),
                BlockReason.INELIGIBLE_SIGNAL_TYPE,
            )

        # --- Stage 3: transformation (§3.3) ---------------------------------
        output, actions = self.transformer(candidate, entities, policy)

        # --- Stage 4: validation (§3.4) — the no-raw-identifier proof -------
        survivors = [
            e for e in detect_entities(output, candidate.tenant_id)
            if e.kind in NEVER_RAW_IN_OUTPUT
        ]
        if survivors:
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, actions,
                BlockReason.VALIDATION_RAW_IDENTIFIER,
            )
        if not self._granularity_satisfied(output, actions, policy):
            return self._blocked(
                candidate, entry_ts, entities, policy_applied, actions,
                BlockReason.VALIDATION_POLICY_MISMATCH,
            )

        # --- Stage 5: audit record (§3.5, PF-D7) ----------------------------
        try:
            record = self._audit(
                candidate, entry_ts=entry_ts, entities=entities,
                policy_applied=policy_applied, transformation_applied=actions,
                validation_passed=True, decision=BroadcastDecision.BROADCAST,
                block_reason=None,
            )
        except AuditWriteError:
            # No broadcast without an audit record (PF-D7). Trip the filter's own
            # breaker (§4 "audit write failure" opens the breaker).
            self.breakers.trip(pf_key, trip_class=TripClass.SUSTAINED)
            return FilterResult(
                decision=BroadcastDecision.BLOCKED,
                payload_ref=None,
                block_reason=BlockReason.AUDIT_WRITE_FAILED,
                record=PrivacyAuditRecord(
                    workflow_id=candidate.workflow_id,
                    input_ref=self._input_ref(candidate),
                    tenant_id=candidate.tenant_id,
                    entry_timestamp=entry_ts,
                    exit_timestamp=self.audit.now(),
                    entity_findings=tuple(e.kind for e in entities),
                    policy_applied=policy_applied,
                    transformation_applied=actions,
                    validation_passed=True,
                    decision=BroadcastDecision.BLOCKED,
                    block_reason=BlockReason.AUDIT_WRITE_FAILED,
                ),
                output=None,
            )

        return FilterResult(
            decision=BroadcastDecision.BROADCAST,
            payload_ref=record.input_ref,
            block_reason=None,
            record=record,
            output=output,
        )

    @staticmethod
    def _granularity_satisfied(
        output: dict[str, str], actions: tuple[str, ...], policy: SharingPolicy
    ) -> bool:
        """Stage 4: the transformation matches the resolved policy (§3.4)."""

        if policy.granularity is Granularity.HASH_ONLY:
            return all(v.startswith(HASH_PREFIX) for v in output.values())
        return True

    def _blocked(
        self,
        candidate: BroadcastCandidate,
        entry_ts,
        entities: list[DetectedEntity],
        policy_applied: str,
        actions: tuple[str, ...],
        reason: BlockReason,
    ) -> FilterResult:
        """Fail-closed result. The block is itself audited (PF-D9). If even the
        block cannot be audited, the breaker trips and the refusal still holds."""

        try:
            record = self._audit(
                candidate, entry_ts=entry_ts, entities=entities,
                policy_applied=policy_applied, transformation_applied=actions,
                validation_passed=False, decision=BroadcastDecision.BLOCKED,
                block_reason=reason,
            )
        except AuditWriteError:
            self.breakers.trip(
                privacy_filter_breaker_key(candidate.tenant_id),
                trip_class=TripClass.SUSTAINED,
            )
            record = PrivacyAuditRecord(
                workflow_id=candidate.workflow_id,
                input_ref=self._input_ref(candidate),
                tenant_id=candidate.tenant_id,
                entry_timestamp=entry_ts,
                exit_timestamp=self.audit.now(),
                entity_findings=tuple(e.kind for e in entities),
                policy_applied=policy_applied,
                transformation_applied=actions,
                validation_passed=False,
                decision=BroadcastDecision.BLOCKED,
                block_reason=BlockReason.AUDIT_WRITE_FAILED,
            )
        return FilterResult(
            decision=BroadcastDecision.BLOCKED,
            payload_ref=None,
            block_reason=record.block_reason,
            record=record,
            output=None,
        )


__all__ = [
    "HASH_PREFIX",
    "GEN_PREFIX",
    "detect_entities",
    "default_transform",
    "FilterResult",
    "Transformer",
    "PrivacyFilterPipeline",
]
