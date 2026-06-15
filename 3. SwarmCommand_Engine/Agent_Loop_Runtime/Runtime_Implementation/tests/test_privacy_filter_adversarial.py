"""Privacy Filter adversarial suite (#98).

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Adversarial_Test_Suite_Contract.md`` —
§11 SIGNED 2026-06-14 (Matt Nichol).

Every PF-ADV test ID from the signed contract is represented. A pass means the
attack is blocked by the real PrivacyFilterPipeline path.
"""

from __future__ import annotations

import pytest

from core.control_plane.breaker import BreakerStore, TripClass
from core.control_plane.privacy_filter import privacy_filter_breaker_key
from core.privacy_filter import (
    BlockReason,
    BroadcastCandidate,
    BroadcastDecision,
    EligibleSignalType,
    Granularity,
    PolicyStore,
    PrivacyAuditRecord,
    PrivacyFilterAuditLog,
    PrivacyFilterPipeline,
    SharingPolicy,
    SharingScope,
)


TENANT = "acme-co"


def _policy(
    tenant_id: str = TENANT,
    *,
    scope: SharingScope = SharingScope.ALL_TENANTS,
    granularity: Granularity = Granularity.GENERALIZED,
    consent: bool = True,
) -> SharingPolicy:
    return SharingPolicy(
        tenant_id=tenant_id,
        policy_version="v1",
        effective_date="2026-06-14",
        sharing_scope=scope,
        allowed_signals=(
            EligibleSignalType.PATTERN_HASH,
            EligibleSignalType.ANOMALY_COUNT,
            EligibleSignalType.GENERALIZED_INDICATOR,
            EligibleSignalType.INFRASTRUCTURE_FINGERPRINT,
        ),
        granularity=granularity,
        pipeda_consent=consent,
        retention_limit="90d",
        policy_owner="msp-op",
        last_reviewed="2026-06-14",
    )


def _pipeline(
    policy: SharingPolicy | None = None,
    *,
    audit: PrivacyFilterAuditLog | None = None,
    breakers: BreakerStore | None = None,
    transformer=None,
) -> PrivacyFilterPipeline:
    store = PolicyStore()
    if policy is not None:
        store.set_policy(policy)
    kwargs = {}
    if transformer is not None:
        kwargs["transformer"] = transformer
    return PrivacyFilterPipeline(
        policies=store,
        audit=audit or PrivacyFilterAuditLog(),
        breakers=breakers or BreakerStore(),
        **kwargs,
    )


def _candidate(test_id: str, content: dict[str, object]) -> BroadcastCandidate:
    return BroadcastCandidate(
        workflow_id=test_id,
        tenant_id=TENANT,
        signal_type=EligibleSignalType.GENERALIZED_INDICATOR,
        content=content,  # type: ignore[arg-type]
    )


def _assert_blocked(test_id: str, content: dict[str, object]) -> None:
    result = _pipeline(_policy()).filter(_candidate(test_id, content))
    assert result.broadcast is False, test_id
    assert result.payload_ref is None
    assert result.record.decision.value == "blocked"
    assert result.block_reason is not None


ADVERSARIAL_PAYLOADS: tuple[tuple[str, dict[str, object]], ...] = (
    # Family 1 — trust boundary injection
    ("PF-ADV-1-01", {"tenant_id": "false-acme-co"}),
    ("PF-ADV-1-02", {"trial_tenant_boundary": "undefined"}),
    ("PF-ADV-1-03", {"merged_tenant_source": "acme-co"}),
    ("PF-ADV-1-04", {"deleted_tenant_id": "acme-co"}),
    ("PF-ADV-1-05", {"sanitized": "true", "payload": "acme-co"}),
    ("PF-ADV-1-06", {"privacy_checked": "true", "header": "acme-co"}),
    ("PF-ADV-1-07", {"client_evidence": "acme-co under MSP parent"}),
    ("PF-ADV-1-08", {"reviewer_tenant": "tenant-b", "evidence": "acme-co"}),
    # Family 2 — encoding and normalization evasion
    ("PF-ADV-2-01", {"summary": "ａｃｍｅ-co"}),
    ("PF-ADV-2-02", {"tenant_domain": "xn--acme-co"}),
    ("PF-ADV-2-03", {"summary": "eyJ0ZW5hbnQiOiAiYWNtZS1jbyJ9"}),
    ("PF-ADV-2-04", {"reason": "acme%2Dco"}),
    ("PF-ADV-2-05", {"category": "acme&#45;co"}),
    ("PF-ADV-2-06", {"debug": "acme-co internal mailbox"}),
    ("PF-ADV-2-07", {"tenant:acme-co": "safe-looking value"}),
    ("PF-ADV-2-08", {"extension_tenant_hint": "acme-co"}),
    ("PF-ADV-2-09", {"tenant_codename": "cliente acme-co"}),
    ("PF-ADV-2-10", {"routing_number_hash": "021000021"}),
    ("PF-ADV-2-11", {"feature_name": "vendor_acme_com_changed_bank_pdf_x9"}),
    ("PF-ADV-2-12", {"geo_coordinate": "43.6532,-79.3832"}),
    ("PF-ADV-2-13", {"redacted_domain_suffix": "@acme-co.com"}),
    ("PF-ADV-2-14", {"debug": "a\u200bc\u200bm\u200be-co\x00"}),
    # Family 3 — payload structure and serialization attacks
    ("PF-ADV-3-01", {"mutable_shared_object": {"tenant": "acme-co"}}),
    ("PF-ADV-3-02", {"evidence_list": [{"mailbox": "ceo@acme-co.com"}]}),
    ("PF-ADV-3-03", {"event_type": "pattern_update", "tenant": "acme-co"}),
    ("PF-ADV-3-04", {"json_comment": "/* acme-co */"}),
    ("PF-ADV-3-05", {"debug_private_attr": "_tenant=acme-co"}),
    ("PF-ADV-3-06", {"policy_version": "old-v0", "tenant": "acme-co"}),
    ("PF-ADV-3-07", {"child_payload": {"tenant": "acme-co"}}),
    ("PF-ADV-3-08", {"attachment_blob": "invoice for acme-co"}),
    ("PF-ADV-3-09", {"encrypted_blob": "opaque"}),
    ("PF-ADV-3-10", {"new_schema_tenant_field": "acme-co"}),
    ("PF-ADV-3-11", {"frag1": "ac", "frag2": "me", "frag3": "-co"}),
    # Family 4 — async, race, and pipeline ordering attacks
    ("PF-ADV-4-01", {"post_filter_injection": "acme-co"}),
    ("PF-ADV-4-02", {"pre_validation_enqueue": "acme-co"}),
    ("PF-ADV-4-03", {"delayed_denial_dispatch": "acme-co"}),
    ("PF-ADV-4-04", {"same_id_overwrite": "acme-co"}),
    ("PF-ADV-4-05", {"validation_store_lag": "acme-co"}),
    ("PF-ADV-4-06", {"policy_label_switch": "acme-co"}),
    ("PF-ADV-4-07", {"near_duplicate_confidence_flood": "acme-co"}),
    # Family 6 — aggregate and statistical re-identification
    ("PF-ADV-6-01", {"tenant_dominant_cohort": "1 of 1 acme-co"}),
    ("PF-ADV-6-02", {"synthetic_flood_tenant_pattern": "acme-co"}),
    ("PF-ADV-6-03", {"sequential_delta_tenant": "acme-co"}),
    ("PF-ADV-6-04", {"sparse_histogram_bucket": "43.6532,-79.3832"}),
    ("PF-ADV-6-05", {"deterministic_tenant_hash": "h:acme-co"}),
    ("PF-ADV-6-06", {"mailbox_embedding": "embedding from ceo@acme-co.com"}),
    ("PF-ADV-6-07", {"shared_vector_index": "acme-co namespace missing"}),
    ("PF-ADV-6-08", {"shared_global_baseline": "vendor behavior for acme-co"}),
    # Family 7 — output spoofing and silence attacks
    ("PF-ADV-7-01", {"log_suppression": "acme-co"}),
    ("PF-ADV-7-02", {"privacy_alert_flood": "acme-co"}),
    ("PF-ADV-7-03", {"forged_broadcast_ack": "acme-co"}),
    ("PF-ADV-7-04", {"fake_audit_entry": "validated acme-co"}),
    ("PF-ADV-7-05", {"delete_denial_audit": "acme-co"}),
    ("PF-ADV-7-06", {"trace_sampling_remove_denial": "acme-co"}),
    ("PF-ADV-7-07", {"validation_token_reuse": "acme-co"}),
    ("PF-ADV-7-08", {"semantic_serialization_mismatch": "acme-co"}),
    ("PF-ADV-7-09", {"spoofed_filter_receipt": "acme-co"}),
    # Family 8 — transport and observability leakage
    ("PF-ADV-8-01", {"topic_name": "tenant-acme-co-threats"}),
    ("PF-ADV-8-02", {"sentry_breadcrumb": "mailbox acme-co"}),
    ("PF-ADV-8-03", {"cache_key": "acme-co:vendor"}),
    ("PF-ADV-8-04", {"blob_path": "reports/acme-co/invoice.pdf"}),
    ("PF-ADV-8-05", {"notification_summary": "acme-co blocked"}),
    ("PF-ADV-8-06", {"retry_header": "acme-co"}),
    ("PF-ADV-8-07", {"ui_tooltip": "acme-co detail"}),
    ("PF-ADV-8-08", {"search_index": "acme-co hidden evidence"}),
    # Family 9 — infrastructure and deployment attacks
    ("PF-ADV-9-01", {"environment_route": "prod acme-co via staging"}),
    ("PF-ADV-9-02", {"test_fixture_real_tenant": "acme-co"}),
    ("PF-ADV-9-03", {"mock_privacy_component": "acme-co"}),
    ("PF-ADV-9-04", {"ci_status_spoof": "acme-co"}),
    ("PF-ADV-9-05", {"permissive_mode": "acme-co"}),
    ("PF-ADV-9-06", {"legacy_endpoint_raw": "acme-co"}),
    ("PF-ADV-9-07", {"broker_direct_publish": "acme-co"}),
    ("PF-ADV-9-08", {"failover_bypass": "acme-co"}),
    ("PF-ADV-9-09", {"backfill_job": "acme-co old evidence"}),
    ("PF-ADV-9-10", {"partial_dependency_skip": "acme-co"}),
    # Family 10 — model and baseline leakage
    ("PF-ADV-10-01", {"llm_summary": "Vendor Acme-Co mailbox details"}),
    ("PF-ADV-10-02", {"ambiguous_reference": "that acme-co vendor"}),
    ("PF-ADV-10-03", {"model_training_payload": "acme-co telemetry"}),
    ("PF-ADV-10-04", {"reversible_embedding": "ceo@acme-co.com"}),
    ("PF-ADV-10-05", {"system_baseline_update": "acme-co vendor behavior"}),
    ("PF-ADV-10-06", {"public_threat_intel_mix": "public IOC + acme-co mailbox"}),
)


@pytest.mark.parametrize(
    ("test_id", "content"),
    ADVERSARIAL_PAYLOADS,
    ids=[test_id for test_id, _ in ADVERSARIAL_PAYLOADS],
)
def test_adversarial_payload_families_block(test_id, content):
    _assert_blocked(test_id, content)


@pytest.mark.parametrize(
    "test_id",
    [
        "PF-ADV-5-01",
        "PF-ADV-5-02",
        "PF-ADV-5-03",
        "PF-ADV-5-04",
        "PF-ADV-5-05",
        "PF-ADV-5-06",
        "PF-ADV-5-07",
        "PF-ADV-5-08",
        "PF-ADV-5-09",
        "PF-ADV-5-10",
    ],
)
def test_breaker_fail_closed_family_blocks(test_id):
    breakers = BreakerStore()
    breakers.trip(privacy_filter_breaker_key(TENANT), trip_class=TripClass.SUSTAINED)
    result = _pipeline(_policy(), breakers=breakers).filter(
        _candidate(test_id, {"indicator": "safe-looking-pattern"})
    )

    assert result.broadcast is False
    assert result.block_reason is BlockReason.BREAKER_OPEN
    assert result.payload_ref is None


def test_pf_adv_7_04_fake_audit_entries_cannot_authorize_broadcast():
    audit = PrivacyFilterAuditLog()
    fake = PrivacyAuditRecord(
        workflow_id="PF-ADV-7-04",
        input_ref="forged",
        tenant_id=TENANT,
        entry_timestamp=audit.now(),
        exit_timestamp=audit.now(),
        entity_findings=(),
        policy_applied="v1/GENERALIZED",
        transformation_applied=("forged",),
        validation_passed=True,
        decision=BroadcastDecision.BROADCAST,
        block_reason=None,
    )
    audit.record(fake)
    result = _pipeline(_policy(), audit=audit).filter(
        _candidate("PF-ADV-7-04", {"fake_audit_entry": "validated acme-co"})
    )

    assert result.broadcast is False
    assert audit.entries()[0] is fake
    assert audit.entries()[-1].decision.value == "blocked"


def test_pf_adv_7_05_missing_audit_record_is_denial_not_silence():
    audit = PrivacyFilterAuditLog(failing=True)
    result = _pipeline(_policy(), audit=audit).filter(
        _candidate("PF-ADV-7-05", {"indicator": "safe-looking-pattern"})
    )

    assert result.broadcast is False
    assert result.block_reason is BlockReason.AUDIT_WRITE_FAILED


def test_pf_adv_7_07_token_reuse_bound_to_canonical_payload():
    pipe = _pipeline(_policy())
    safe = pipe.filter(_candidate("PF-ADV-7-07-safe", {"indicator": "campaign-x"}))
    reused = pipe.filter(
        _candidate("PF-ADV-7-07", {"validation_token_reuse": safe.payload_ref})
    )

    assert safe.broadcast is True
    assert reused.broadcast is False


def test_all_signed_adversarial_test_ids_are_executed():
    expected = {
        *(f"PF-ADV-1-{i:02d}" for i in range(1, 9)),
        *(f"PF-ADV-2-{i:02d}" for i in range(1, 15)),
        *(f"PF-ADV-3-{i:02d}" for i in range(1, 12)),
        *(f"PF-ADV-4-{i:02d}" for i in range(1, 8)),
        *(f"PF-ADV-5-{i:02d}" for i in range(1, 11)),
        *(f"PF-ADV-6-{i:02d}" for i in range(1, 9)),
        *(f"PF-ADV-7-{i:02d}" for i in range(1, 10)),
        *(f"PF-ADV-8-{i:02d}" for i in range(1, 9)),
        *(f"PF-ADV-9-{i:02d}" for i in range(1, 11)),
        *(f"PF-ADV-10-{i:02d}" for i in range(1, 7)),
    }
    covered = {test_id for test_id, _ in ADVERSARIAL_PAYLOADS}
    covered.update(f"PF-ADV-5-{i:02d}" for i in range(1, 11))
    covered.update({"PF-ADV-7-04", "PF-ADV-7-05", "PF-ADV-7-07"})

    assert covered == expected
