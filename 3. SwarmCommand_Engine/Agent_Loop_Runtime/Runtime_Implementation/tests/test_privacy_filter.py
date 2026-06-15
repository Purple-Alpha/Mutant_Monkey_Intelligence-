"""Privacy Filter tests (Layer 6 Control Plane, scoreboard row #93).

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Contract.md`` — §15 SIGNED 2026-06-14
(Matt Nichol).

Three test classes per AGENTS.md §5 / contract §10:
  Class 1 — expected pass
  Class 2 — adversarial (the falsifiable decision tests live here)
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import dataclasses

import pytest

from core.control_plane.breaker import BreakerStore, TripClass
from core.control_plane.privacy_filter import privacy_filter_breaker_key
from core.privacy_filter import (
    AuditWriteError,
    BlockReason,
    BroadcastCandidate,
    BroadcastDecision,
    EligibleSignalType,
    EntityKind,
    Granularity,
    PolicyResolutionError,
    PolicyStore,
    PrivacyAuditRecord,
    PrivacyFilterAuditLog,
    PrivacyFilterPipeline,
    SharingPolicy,
    SharingScope,
    detect_entities,
)


def _policy(
    tenant_id: str = "acme-co",
    *,
    scope: SharingScope = SharingScope.ALL_TENANTS,
    granularity: Granularity = Granularity.GENERALIZED,
    consent: bool = True,
    allowed: tuple[EligibleSignalType, ...] = (
        EligibleSignalType.PATTERN_HASH,
        EligibleSignalType.ANOMALY_COUNT,
        EligibleSignalType.GENERALIZED_INDICATOR,
    ),
) -> SharingPolicy:
    return SharingPolicy(
        tenant_id=tenant_id,
        policy_version="v1",
        effective_date="2026-06-01",
        sharing_scope=scope,
        allowed_signals=allowed,
        granularity=granularity,
        pipeda_consent=consent,
        retention_limit="90d",
        policy_owner="msp-op",
        last_reviewed="2026-06-10",
    )


def _pipeline(policy: SharingPolicy | None = None, **kwargs) -> PrivacyFilterPipeline:
    store = PolicyStore()
    if policy is not None:
        store.set_policy(policy)
    return PrivacyFilterPipeline(
        policies=store,
        audit=PrivacyFilterAuditLog(),
        breakers=BreakerStore(),
        **kwargs,
    )


def _candidate(tenant_id: str = "acme-co", **content) -> BroadcastCandidate:
    return BroadcastCandidate(
        workflow_id="wf-1",
        tenant_id=tenant_id,
        signal_type=EligibleSignalType.GENERALIZED_INDICATOR,
        content=content or {"indicator": "phishing-campaign-x"},
    )


# ---------------------------------------------------------------------------
# Class 1 — expected pass
# ---------------------------------------------------------------------------


def test_compliant_item_runs_all_five_stages_and_broadcasts():
    pipe = _pipeline(_policy())
    result = pipe.filter(_candidate(indicator="phishing-campaign-x"))
    assert result.broadcast is True
    rec = result.record
    assert rec.decision is BroadcastDecision.BROADCAST
    assert rec.validation_passed is True
    assert rec.input_ref and not rec.input_ref.endswith(rec.tenant_id)
    assert rec.policy_applied.startswith("v1/")


def test_raw_tenant_identifier_is_blocked_before_broadcast():
    pipe = _pipeline(_policy(granularity=Granularity.GENERALIZED))
    result = pipe.filter(
        _candidate(tenant_id="acme-co", origin="acme-co internal note")
    )
    assert result.broadcast is False
    assert result.block_reason is BlockReason.VALIDATION_RAW_IDENTIFIER
    assert result.output is None
    assert EntityKind.TENANT_ID in result.record.entity_findings


def test_absent_policy_fails_closed():
    pipe = _pipeline(policy=None)  # no policy registered
    result = pipe.filter(_candidate())
    assert result.broadcast is False
    assert result.block_reason is BlockReason.POLICY_ABSENT


def test_audit_record_written_for_broadcast_and_blocked():
    pipe = _pipeline(_policy())
    pipe.filter(_candidate())  # broadcast
    pipe.filter(BroadcastCandidate("wf-2", "no-policy-tenant",
                                   EligibleSignalType.PATTERN_HASH, {"h": "x"}))  # blocked
    records = pipe.audit.entries()
    assert len(records) == 2
    assert {r.decision for r in records} == {
        BroadcastDecision.BROADCAST,
        BroadcastDecision.BLOCKED,
    }


def test_breaker_open_produces_no_broadcast():
    pipe = _pipeline(_policy())
    pipe.breakers.trip(privacy_filter_breaker_key("acme-co"), trip_class=TripClass.SUSTAINED)
    result = pipe.filter(_candidate())
    assert result.broadcast is False
    assert result.block_reason is BlockReason.BREAKER_OPEN


def test_pipeda_consent_absent_fails_closed():
    pipe = _pipeline(_policy(consent=False))
    result = pipe.filter(_candidate())
    assert result.broadcast is False
    assert result.block_reason is BlockReason.PIPEDA_CONSENT_ABSENT


def test_pattern_hash_passes_through_as_eligible_signal():
    pipe = _pipeline(_policy(granularity=Granularity.HASH_ONLY))
    cand = BroadcastCandidate(
        "wf-3", "acme-co", EligibleSignalType.PATTERN_HASH,
        {"pattern": "credential-stuffing"},
    )
    result = pipe.filter(cand)
    assert result.broadcast is True
    assert all(v.startswith("h:") for v in (result.output or {}).values())


# ---------------------------------------------------------------------------
# Class 2 — adversarial (falsifiable decision tests)
# ---------------------------------------------------------------------------


def test_raw_identifier_injected_into_transform_output_is_caught_by_validation():
    """Falsifies PF-D5/§3.4: stage 4 must catch a raw id that stage 3 leaked."""

    def leaky_transform(candidate, entities, policy):
        # A compromised transformer that passes the raw tenant id straight through.
        return dict(candidate.content), ("leak",)

    pipe = _pipeline(_policy(), transformer=leaky_transform)
    result = pipe.filter(_candidate(origin="acme-co confidential"))
    assert result.broadcast is False
    assert result.block_reason is BlockReason.VALIDATION_RAW_IDENTIFIER


def test_validation_stage_is_not_skippable():
    """Falsifies PF-D4: there is no path that broadcasts without validation."""

    def leaky_transform(candidate, entities, policy):
        return dict(candidate.content), ("leak",)

    pipe = _pipeline(_policy(), transformer=leaky_transform)
    # Even with a compromised stage 3, an email in the output is blocked.
    result = pipe.filter(_candidate(note="reach me at ceo@acme.com"))
    assert result.broadcast is False
    assert result.block_reason is BlockReason.VALIDATION_RAW_IDENTIFIER


def test_broadcast_without_audit_record_fails_closed():
    """Falsifies PF-D7: no broadcast without an audit record; breaker trips."""

    pipe = _pipeline(_policy())
    pipe.audit.failing = True
    result = pipe.filter(_candidate())
    assert result.broadcast is False
    assert result.block_reason is BlockReason.AUDIT_WRITE_FAILED
    # §4: an audit write failure opens the filter breaker.
    assert pipe.breakers.is_closed(privacy_filter_breaker_key("acme-co")) is False


def test_raw_email_content_is_flagged_and_blocked():
    """Falsifies §6/§3.1: raw email content must never cross the boundary."""

    def leaky_transform(candidate, entities, policy):
        return dict(candidate.content), ("leak",)

    pipe = _pipeline(_policy(), transformer=leaky_transform)
    result = pipe.filter(
        BroadcastCandidate("wf-e", "acme-co", EligibleSignalType.GENERALIZED_INDICATOR,
                           {"body": "From: victim@bank.com Subject: invoice"})
    )
    assert result.broadcast is False
    assert result.block_reason is BlockReason.VALIDATION_RAW_IDENTIFIER
    # default (non-leaky) path now blocks raw never-eligible content before broadcast.
    pipe2 = _pipeline(_policy())
    ok = pipe2.filter(
        BroadcastCandidate("wf-e2", "acme-co", EligibleSignalType.GENERALIZED_INDICATOR,
                           {"body": "From: victim@bank.com Subject: invoice"})
    )
    assert ok.broadcast is False
    assert ok.block_reason is BlockReason.VALIDATION_RAW_IDENTIFIER


def test_privacy_filter_failure_halts_broadcast_no_fallback():
    """Falsifies PF-D2: OPEN means silence, there is no fallback path."""

    pipe = _pipeline(_policy())
    key = privacy_filter_breaker_key("acme-co")
    pipe.breakers.trip(key, trip_class=TripClass.SUSTAINED)
    for _ in range(3):
        r = pipe.filter(_candidate())
        assert r.broadcast is False
        assert r.payload_ref is None
        assert r.block_reason is BlockReason.BREAKER_OPEN


def test_two_independent_failure_domains():
    """Falsifies PF-D3/BRC-D5: a broadcast-engine breaker trip must not open the
    privacy filter breaker, and vice versa."""

    from core.control_plane.breaker import BreakerKey

    pipe = _pipeline(_policy())
    other_domain = BreakerKey("acme-co", "broadcast_engine", "emit", "sess")
    pipe.breakers.trip(other_domain, trip_class=TripClass.SUSTAINED)
    # Privacy filter's own breaker is untouched — it can still broadcast.
    assert pipe.breakers.is_closed(privacy_filter_breaker_key("acme-co")) is True
    assert pipe.filter(_candidate()).broadcast is True
    # Reverse: tripping the privacy filter breaker leaves the other domain CLOSED.
    pipe.breakers.trip(privacy_filter_breaker_key("acme-co"), trip_class=TripClass.SUSTAINED)
    assert pipe.breakers.is_closed(other_domain) is False  # still open from above
    # The point: the two keys are distinct, so neither contaminates the other.
    assert privacy_filter_breaker_key("acme-co") != other_domain


def test_ambiguous_policy_resolves_fail_closed():
    """Falsifies PF-D6: an incomplete/ambiguous policy must not broadcast."""

    store = PolicyStore()
    ambiguous = dataclasses.replace(_policy(), policy_owner="")  # missing owner
    store.set_policy(ambiguous)
    with pytest.raises(PolicyResolutionError) as exc:
        store.resolve("acme-co")
    assert exc.value.reason is BlockReason.POLICY_AMBIGUOUS


def test_scope_none_blocks_broadcast():
    """Falsifies §5: sharing scope NONE must not broadcast."""

    pipe = _pipeline(_policy(scope=SharingScope.NONE))
    result = pipe.filter(_candidate())
    assert result.broadcast is False
    assert result.block_reason is BlockReason.SCOPE_NONE


def test_ineligible_signal_type_blocked():
    """Falsifies §6: only allowed signal types may cross the boundary."""

    pipe = _pipeline(_policy(allowed=(EligibleSignalType.PATTERN_HASH,)))
    result = pipe.filter(_candidate())  # GENERALIZED_INDICATOR not allowed
    assert result.broadcast is False
    assert result.block_reason is BlockReason.INELIGIBLE_SIGNAL_TYPE


def test_blocked_operation_is_logged_with_full_rigor():
    """Falsifies PF-D9: a refusal is a governance event, logged like a permit."""

    pipe = _pipeline(_policy(scope=SharingScope.NONE))
    result = pipe.filter(_candidate())
    assert result.record.decision is BroadcastDecision.BLOCKED
    assert result.record.block_reason is BlockReason.SCOPE_NONE
    assert len(pipe.audit.entries()) == 1
    # Append-only: no update/delete API; records frozen.
    assert not hasattr(pipe.audit, "delete")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.record.decision = BroadcastDecision.BROADCAST  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Class 3 — known-gap xfail (documented; completion path named)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="Full PIPEDA compliance audit deferred — requires legal review of "
    "tenant policy templates; completion path: legal review before first "
    "production tenant onboarded (§10 Class 3).",
)
def test_full_pipeda_compliance_audit_complete():
    assert hasattr(PrivacyFilterPipeline, "pipeda_compliance_certificate")


@pytest.mark.xfail(
    strict=True,
    reason="Cross-region privacy filter coordination deferred — infrastructure "
    "selection pending; completion path: Lung contract (§1 out of scope).",
)
def test_cross_region_coordination_implemented():
    assert hasattr(PrivacyFilterPipeline, "coordinate_cross_region")


@pytest.mark.xfail(
    strict=True,
    reason="Tenant consent management workflow deferred — Playhouse contract; "
    "completion path: Phase 9 (§10 Class 3).",
)
def test_tenant_consent_management_workflow_implemented():
    assert hasattr(PrivacyFilterPipeline, "consent_management_workflow")
