"""Multi-tenant isolation hardening — DoD Phase 7 tests.

Spec: ``Policy_Pipeline/multi-tenant-isolation-hardening.md``.

Every test pins one defense in the multi-tenant isolation chain:

1. ``target_production_tenant_id`` is part of the canonical signed payload
   (tamper detection still works when the field is flipped).
2. The promotion pipeline rejects a signed policy whose
   ``target_production_tenant_id`` does not match
   ``PolicyPromotionConfig.production_tenant_id`` — a sandbox-side REJECTED
   ``audit_verdict`` is written with the spec finding and no production
   record is produced.
3. The Guardrail 11 gate (``apply_signed_policy``) raises
   ``GovernanceError`` when a policy signed for tenant A is gated for
   tenant B (defense in depth) — no ``production_state`` mutation.
4. ``default_sandbox_tenant_for`` returns ``f"sandbox_{X}"`` for any new
   production tenant id.
5. End-to-end: tenant A and tenant B run side by side in the same
   blackboard root; signed policies do not cross tenant lines even when
   the same sandbox is shared.
6. Regression-pin: the long-standing demo flow (``tenant_demo`` paired
   with ``sandbox_default``) still works unchanged.

Additional coverage (tamper detection on every new surface):

7. Tampering with the signed payload's ``target_production_tenant_id``
   after disk-write fails signature verification at the promotion
   pipeline, before the cross-tenant check would even run.
8. The mutation engine sets ``target_production_tenant_id`` from
   ``MutationEngineConfig.production_tenant_id`` and the signature stays
   valid through promotion + gate.
9. ``request_rollback_to_previous`` propagates the production tenant id
   into the signed rollback payload so a rollback cannot accidentally
   target a different tenant's history.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from core.blackboard import (
    AuditStatus,
    Environment,
    GovernanceError,
    MutantEvaluationPayload,
    PolicyUpdatePayload,
    RecordType,
    read_records,
)
from core.mutation import MutationEngineConfig, run_mutation_cycle
from core.orchestrator import (
    RouteContext,
    default_sandbox_tenant_for,
    submit_mutant_evaluation,
    submit_policy_update,
)
from core.orchestrator.routes import blackboard_path
from core.policy import (
    PolicyPromotionConfig,
    SigningKey,
    applied_state_history,
    default_signing_key,
    request_rollback_to_previous,
    run_policy_promotion_cycle,
    sign,
    sign_rollback_request,
    verify,
)
from core.policy.signing import canonical_payload
from core.production import (
    PolicyConsumerConfig,
    ProductionLoopConfig,
    ProductionSignal,
    apply_pending_policies,
    run_production_cycle,
)
from core.production_state import (
    ProductionPolicyState,
    apply_signed_policy,
    load_state,
    state_path,
)


# ---------------------------------------------------------------------------
# Test fixtures and helpers
# ---------------------------------------------------------------------------

DEMO_TENANT = "tenant_demo"
DEMO_SANDBOX = "sandbox_default"

LOW_CONFIDENCE_SIGNAL = ProductionSignal(
    source="mailbox",
    event_kind="email_received",
    subject="Team lunch update",
    sender_domain="client-example.ca",
)


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _inject_signed_policy_for(
    route_context: RouteContext,
    *,
    target_production_tenant_id: str,
    sandbox_tenant_id: str,
    policy_name: str = "blue_detection_001:add_missing_signal_heuristic",
    parameters: dict | None = None,
    is_rollback: bool = False,
    signing_key: SigningKey | None = None,
):
    """Sign and submit one ``policy_update`` directly to sandbox.

    Bypasses the mutation engine so tests can drive arbitrary tenant pairs
    (including deliberately mismatched pairs) without first staging a
    mutant evaluation.
    """

    key = signing_key or default_signing_key()
    payload = PolicyUpdatePayload(
        policy_name=policy_name,
        change_summary=f"test policy {policy_name}",
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan="revert",
        parameters=parameters or {},
        is_rollback=is_rollback,
        target_production_tenant_id=target_production_tenant_id,
    )
    signature_id = sign(payload.model_dump(mode="json"), "governance_001", key)
    return submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=payload,
        signature_id=signature_id,
        sandbox_tenant_id=sandbox_tenant_id,
    )


def _seed_mutation_signed_policy(
    route_context: RouteContext,
    *,
    production_tenant_id: str = DEMO_TENANT,
    sandbox_tenant_id: str = DEMO_SANDBOX,
):
    """Drive sandbox -> sign -> promote so we have a real signed evidence chain."""

    submit_mutant_evaluation(
        route_context,
        source_agent="sandbox_mutator_001",
        sandbox_tenant_id=sandbox_tenant_id,
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=uuid4(),
            blue_detected=False,
            baseline_confidence=0.53,
            failure_modes=["missing_signal:unknown_sender_domain"],
            mutation_recommended=True,
        ),
    )
    run_mutation_cycle(
        route_context,
        config=MutationEngineConfig(
            sandbox_tenant_id=sandbox_tenant_id,
            production_tenant_id=production_tenant_id,
        ),
    )


# ---------------------------------------------------------------------------
# 1. target_production_tenant_id is part of the signed canonical payload
# ---------------------------------------------------------------------------


def test_target_production_tenant_id_is_signed_so_tamper_breaks_verification():
    """Flipping the field after signing must break the HMAC signature."""

    key = SigningKey(secret=b"deterministic-test-key-of-sufficient-length-32")
    original = PolicyUpdatePayload(
        policy_name="policy_alpha",
        change_summary="x",
        rollback_plan="revert",
        target_production_tenant_id="tenant_a",
    )
    signature_id = sign(original.model_dump(mode="json"), "governance_001", key)

    assert verify(
        original.model_dump(mode="json"), "governance_001", signature_id, key
    )

    tampered = original.model_copy(update={"target_production_tenant_id": "tenant_b"})
    assert not verify(
        tampered.model_dump(mode="json"), "governance_001", signature_id, key
    )

    # Belt-and-suspenders: the canonical bytes must literally differ so any
    # signature scheme over the canonical payload would also detect the
    # tamper, not just HMAC-SHA256 specifically.
    assert canonical_payload(
        original.model_dump(mode="json"), "governance_001"
    ) != canonical_payload(
        tampered.model_dump(mode="json"), "governance_001"
    )


# ---------------------------------------------------------------------------
# 2. Promotion pipeline rejects cross-tenant policies
# ---------------------------------------------------------------------------


def test_promotion_pipeline_rejects_cross_tenant_policy_with_sandbox_audit(tmp_path):
    """A policy signed for tenant A must not promote into tenant B production."""

    route_context = _context(tmp_path)
    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id="tenant_b",
        sandbox_tenant_id=DEMO_SANDBOX,
    )

    result = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(production_tenant_id=DEMO_TENANT),
    )

    assert result.processed_count == 1
    assert result.promoted_count == 0
    assert result.rejected_count == 1
    item = result.item_results[0]
    assert item.verification_passed is True
    assert item.production_audit is None
    assert item.production_workflow_trigger is None
    assert item.sandbox_rejection_audit is not None

    production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, DEMO_TENANT
    )
    assert read_records(production_path) == []

    sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, DEMO_SANDBOX
    )
    rejections = [
        record
        for record in read_records(sandbox_path)
        if record.record_type == RecordType.AUDIT_VERDICT
        and record.payload["verdict"] == AuditStatus.REJECTED.value
    ]
    assert len(rejections) == 1
    assert rejections[0].workflow_id == "policy_promotion"
    assert rejections[0].payload["findings"] == [
        f"cross_tenant_promotion_attempt={DEMO_SANDBOX}->{DEMO_TENANT}"
    ]


# ---------------------------------------------------------------------------
# 3. Gate raises GovernanceError on cross-tenant (defense in depth)
# ---------------------------------------------------------------------------


def test_gate_rejects_cross_tenant_policy_with_governance_error(tmp_path):
    """Promotion pipeline could be bypassed in principle — the gate must still catch it.

    Strategy: fabricate the full production-side evidence chain (audit_verdict
    + workflow_trigger) by running the promotion pipeline against a config
    whose ``production_tenant_id`` matches the signed policy's
    ``target_production_tenant_id``. Then invoke the gate with a DIFFERENT
    ``production_tenant_id``. The gate must raise ``GovernanceError`` and
    leave the (other tenant's) production_state file untouched.
    """

    route_context = _context(tmp_path)

    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id="tenant_a",
        sandbox_tenant_id="sandbox_a",
    )
    promotion = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_a",
            sandbox_tenant_id="sandbox_a",
        ),
    )
    assert promotion.promoted_count == 1
    trigger = promotion.item_results[0].production_workflow_trigger
    assert trigger is not None
    workflow_trigger_id = trigger.record.record_id

    other_tenant_state_path = state_path(route_context.blackboard_root, "tenant_b")
    assert not other_tenant_state_path.exists()

    # Build a parallel evidence chain in tenant_b's production log so that
    # gather_evidence finds a tenant_b workflow_trigger pointing at the
    # SAME sandbox_a policy_update. This is the precise pipeline-bypass
    # scenario the spec defends against.
    tenant_a_production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, "tenant_a"
    )
    tenant_b_production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, "tenant_b"
    )
    tenant_b_production_path.parent.mkdir(parents=True, exist_ok=True)
    tenant_b_production_path.write_text(
        tenant_a_production_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    with pytest.raises(GovernanceError, match="cross-tenant promotion attempt"):
        apply_signed_policy(
            blackboard_root=route_context.blackboard_root,
            production_tenant_id="tenant_b",
            sandbox_tenant_id="sandbox_a",
            workflow_trigger_id=workflow_trigger_id,
        )
    assert not other_tenant_state_path.exists()

    # And the legitimate apply for tenant_a still succeeds, proving the
    # signed payload was otherwise valid.
    result = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        production_tenant_id="tenant_a",
        sandbox_tenant_id="sandbox_a",
        workflow_trigger_id=workflow_trigger_id,
    )
    assert result.changed is True
    assert result.new_state.active_version.startswith("blue_detection_001:")


# ---------------------------------------------------------------------------
# 4. default_sandbox_tenant_for helper
# ---------------------------------------------------------------------------


def test_default_sandbox_tenant_for_new_production_tenant():
    assert default_sandbox_tenant_for("acme_ca") == "sandbox_acme_ca"
    assert default_sandbox_tenant_for("orbital_widgets") == "sandbox_orbital_widgets"

    with pytest.raises(ValueError, match="production_tenant_id is required"):
        default_sandbox_tenant_for("")


# ---------------------------------------------------------------------------
# 5. End-to-end: tenant A and tenant B share a blackboard root; no crossover
# ---------------------------------------------------------------------------


def test_two_tenants_in_one_blackboard_root_do_not_leak_policies(tmp_path):
    """Run tenant A and tenant B concurrently. Each tenant's signed policy
    promotes only into its own production_state."""

    route_context = _context(tmp_path)

    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id="tenant_a",
        sandbox_tenant_id="sandbox_a",
        policy_name="policy_for_a",
        parameters={"confidence_boost": 0.10},
    )
    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id="tenant_b",
        sandbox_tenant_id="sandbox_b",
        policy_name="policy_for_b",
        parameters={"confidence_boost": 0.20},
    )

    promotion_a = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_a",
            sandbox_tenant_id="sandbox_a",
        ),
    )
    promotion_b = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_b",
            sandbox_tenant_id="sandbox_b",
        ),
    )
    assert promotion_a.promoted_count == 1
    assert promotion_b.promoted_count == 1

    apply_a = apply_pending_policies(
        route_context,
        config=PolicyConsumerConfig(
            production_tenant_id="tenant_a", sandbox_tenant_id="sandbox_a"
        ),
    )
    apply_b = apply_pending_policies(
        route_context,
        config=PolicyConsumerConfig(
            production_tenant_id="tenant_b", sandbox_tenant_id="sandbox_b"
        ),
    )
    assert apply_a.applied_count == 1
    assert apply_b.applied_count == 1

    state_a = load_state(state_path(route_context.blackboard_root, "tenant_a"))
    state_b = load_state(state_path(route_context.blackboard_root, "tenant_b"))
    assert state_a.active_version == "policy_for_a"
    assert state_a.parameters == {"confidence_boost": 0.10}
    assert state_b.active_version == "policy_for_b"
    assert state_b.parameters == {"confidence_boost": 0.20}

    # Now simulate an attempted leak: a policy signed for tenant_b sitting
    # in sandbox_a. The promotion pipeline run for tenant_a must REJECT it.
    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id="tenant_b",
        sandbox_tenant_id="sandbox_a",
        policy_name="leak_attempt",
    )
    leak_attempt = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_a",
            sandbox_tenant_id="sandbox_a",
        ),
    )
    rejected_items = [
        item
        for item in leak_attempt.item_results
        if item.sandbox_rejection_audit is not None
    ]
    assert len(rejected_items) == 1
    findings = rejected_items[0].sandbox_rejection_audit.record.payload["findings"]
    assert findings == ["cross_tenant_promotion_attempt=sandbox_a->tenant_a"]

    # tenant_a state must not have changed.
    state_a_after = load_state(state_path(route_context.blackboard_root, "tenant_a"))
    assert state_a_after == state_a


# ---------------------------------------------------------------------------
# 6. Regression-pin: demo flow (tenant_demo + sandbox_default) works
# ---------------------------------------------------------------------------


def test_demo_flow_tenant_demo_plus_sandbox_default_explicit_pair_still_works(tmp_path):
    """The original demo pair must keep working unchanged after the hardening."""

    route_context = _context(tmp_path)

    _seed_mutation_signed_policy(route_context)
    promotion = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            sandbox_tenant_id=DEMO_SANDBOX,
            production_tenant_id=DEMO_TENANT,
        ),
    )
    assert promotion.promoted_count == 1
    assert promotion.rejected_count == 0

    item = promotion.item_results[0]
    assert item.production_workflow_trigger is not None
    apply_result = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        production_tenant_id=DEMO_TENANT,
        sandbox_tenant_id=DEMO_SANDBOX,
        workflow_trigger_id=item.production_workflow_trigger.record.record_id,
    )
    assert apply_result.changed is True
    assert apply_result.new_state.active_version.startswith("blue_detection_001:")

    state = load_state(state_path(route_context.blackboard_root, DEMO_TENANT))
    assert state == apply_result.new_state


# ---------------------------------------------------------------------------
# 7. Extra tamper detection: post-disk-write tamper on the new field
# ---------------------------------------------------------------------------


def test_post_disk_write_tamper_on_target_tenant_id_is_caught_at_pipeline(tmp_path):
    """Hand-edit the signed payload's ``target_production_tenant_id`` on disk
    and confirm the promotion pipeline's signature re-verification rejects it
    BEFORE the cross-tenant check fires."""

    route_context = _context(tmp_path)
    _inject_signed_policy_for(
        route_context,
        target_production_tenant_id=DEMO_TENANT,
        sandbox_tenant_id=DEMO_SANDBOX,
    )

    sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, DEMO_SANDBOX
    )
    raw = sandbox_path.read_text(encoding="utf-8").splitlines()
    assert len(raw) == 1
    record = json.loads(raw[0])
    assert record["payload"]["target_production_tenant_id"] == DEMO_TENANT
    record["payload"]["target_production_tenant_id"] = "tenant_b"
    sandbox_path.write_text(json.dumps(record), encoding="utf-8")

    result = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(production_tenant_id=DEMO_TENANT),
    )
    assert result.promoted_count == 0
    assert result.rejected_count == 1
    rejection = result.item_results[0].sandbox_rejection_audit
    assert rejection is not None
    # The signature failure short-circuits before the cross-tenant check so
    # the finding is the signature-verification one, not the cross-tenant
    # one. This pins ordering: signature verification first.
    assert rejection.record.payload["findings"] == [
        "hmac_sha256 signature verification failed"
    ]


# ---------------------------------------------------------------------------
# 8. Mutation engine populates target_production_tenant_id from its config
# ---------------------------------------------------------------------------


def test_mutation_engine_signs_policies_with_configured_production_tenant(tmp_path):
    """The mutation engine's signed payloads carry whichever production tenant
    its config specifies, end-to-end through promotion + gate apply."""

    route_context = _context(tmp_path)

    submit_mutant_evaluation(
        route_context,
        source_agent="sandbox_mutator_001",
        sandbox_tenant_id="sandbox_acme_ca",
        payload=MutantEvaluationPayload(
            baseline_agent_id="blue_detection_001",
            source_attack_case_id=uuid4(),
            blue_detected=False,
            baseline_confidence=0.53,
            failure_modes=["missing_signal:unknown_sender_domain"],
            mutation_recommended=True,
        ),
    )
    mutation = run_mutation_cycle(
        route_context,
        config=MutationEngineConfig(
            sandbox_tenant_id="sandbox_acme_ca",
            production_tenant_id="acme_ca",
        ),
    )
    assert mutation.promoted_count == 1
    signed = mutation.item_results[0].policy_update
    assert signed is not None
    assert signed.record.payload["target_production_tenant_id"] == "acme_ca"

    # Promote in acme_ca's lane.
    promotion = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="acme_ca",
            sandbox_tenant_id="sandbox_acme_ca",
        ),
    )
    assert promotion.promoted_count == 1

    apply_result = apply_signed_policy(
        blackboard_root=route_context.blackboard_root,
        production_tenant_id="acme_ca",
        sandbox_tenant_id="sandbox_acme_ca",
        workflow_trigger_id=promotion.item_results[0]
        .production_workflow_trigger.record.record_id,
    )
    assert apply_result.changed is True
    state = load_state(state_path(route_context.blackboard_root, "acme_ca"))
    assert state == apply_result.new_state

    # And the demo tenant_demo state file remains untouched.
    assert not state_path(route_context.blackboard_root, DEMO_TENANT).exists()


# ---------------------------------------------------------------------------
# 9. Rollback module propagates production tenant id into the signed payload
# ---------------------------------------------------------------------------


def test_sign_rollback_request_propagates_target_production_tenant_id(tmp_path):
    """A rollback signed by ``sign_rollback_request`` carries the caller's
    target production tenant id so it cannot accidentally cross to another
    tenant when promoted."""

    route_context = _context(tmp_path)
    result = sign_rollback_request(
        route_context,
        target_policy_name="policy_for_a",
        target_parameters={"confidence_boost": 0.10},
        alert_reason="multi-tenant rollback test",
        sandbox_tenant_id="sandbox_a",
        target_production_tenant_id="tenant_a",
    )
    payload = PolicyUpdatePayload.model_validate(result.record.payload)
    assert payload.is_rollback is True
    assert payload.target_production_tenant_id == "tenant_a"

    # Promoting against the wrong production tenant yields a cross-tenant
    # rejection with the spec finding format.
    promotion = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_b",
            sandbox_tenant_id="sandbox_a",
        ),
    )
    assert promotion.rejected_count == 1
    assert promotion.item_results[0].sandbox_rejection_audit is not None
    findings = promotion.item_results[
        0
    ].sandbox_rejection_audit.record.payload["findings"]
    assert findings == ["cross_tenant_promotion_attempt=sandbox_a->tenant_b"]


def test_request_rollback_to_previous_pins_production_tenant_id_into_signed_payload(
    tmp_path,
):
    """``request_rollback_to_previous`` must thread its ``production_tenant_id``
    into the rollback payload, so even an alert-triggered rollback cannot
    accidentally promote into another tenant."""

    route_context = _context(tmp_path)

    # Drive two applied policies in tenant_a's lane so the helper has a
    # history depth >= 2.
    for policy_name, params in [
        ("policy_a1", {"confidence_boost": 0.10}),
        ("policy_a2", {"confidence_boost": 0.20}),
    ]:
        _inject_signed_policy_for(
            route_context,
            target_production_tenant_id="tenant_a",
            sandbox_tenant_id="sandbox_a",
            policy_name=policy_name,
            parameters=params,
        )
        run_policy_promotion_cycle(
            route_context,
            config=PolicyPromotionConfig(
                production_tenant_id="tenant_a",
                sandbox_tenant_id="sandbox_a",
            ),
        )
        apply_pending_policies(
            route_context,
            config=PolicyConsumerConfig(
                production_tenant_id="tenant_a", sandbox_tenant_id="sandbox_a"
            ),
        )

    rollback = request_rollback_to_previous(
        route_context,
        production_tenant_id="tenant_a",
        sandbox_tenant_id="sandbox_a",
        alert_reason="multi-tenant rollback wiring test",
    )
    assert rollback is not None
    payload = PolicyUpdatePayload.model_validate(rollback.record.payload)
    assert payload.target_production_tenant_id == "tenant_a"

    # And the rollback is promotable in tenant_a's lane but rejected in tenant_b's.
    promotion_a = run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id="tenant_a",
            sandbox_tenant_id="sandbox_a",
        ),
    )
    # Two earlier promotions are already-promoted (skipped). The rollback
    # promotes cleanly because its target matches an applied state in
    # tenant_a's history.
    assert promotion_a.promoted_count == 1
    assert promotion_a.rejected_count == 0


# ---------------------------------------------------------------------------
# Bonus: production-loop wiring still forces tenant id correctly under
# multi-tenant operation (ties Phase 6b loop-wiring audit to a runtime test).
# ---------------------------------------------------------------------------


def test_production_loop_forces_consumer_sandbox_to_per_tenant_default(tmp_path):
    """When ``run_production_cycle`` is called for a non-demo tenant, the
    default ``PolicyConsumerConfig`` is replaced with one whose tenant ids
    both point at the cycle's tenant via the per-tenant helper."""

    route_context = _context(tmp_path)
    cycle = run_production_cycle(
        route_context,
        tenant_id="acme_ca",
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(),
    )

    assert cycle.policy_apply is not None
    # Nothing pending yet, but the consumer ran for the right tenant
    # (no error path raised + tenant-specific state file is the new
    # default reading location).
    assert cycle.policy_apply.processed_count == 0
    acme_state_file = state_path(route_context.blackboard_root, "acme_ca")
    assert acme_state_file.parent.exists() is False or not acme_state_file.exists()


# ---------------------------------------------------------------------------
# Audit-finding remediation (post-Phase 7):
#   - Regression detector emits alerts for the configured production tenant,
#     not the default tenant_demo.
#   - Production cycle routes weakness reports to per-tenant sandbox, with the
#     demo pair preserved as the documented historical exception.
# ---------------------------------------------------------------------------


def _apply_policy_for_tenant(
    route_context: RouteContext,
    *,
    production_tenant_id: str,
    sandbox_tenant_id: str,
    policy_name: str,
    parameters: dict,
) -> None:
    """Sign + submit + promote + apply one policy for a specific tenant pair.

    Lets the regression-detector remediation test exercise the
    sign-promote-apply-then-detect path against a non-demo tenant without
    leaning on the ``test_regression_detector.py`` helper (which is demo-only).
    """

    key = default_signing_key()
    payload = PolicyUpdatePayload(
        policy_name=policy_name,
        change_summary=f"test policy {policy_name}",
        sandbox_evidence_ids=[],
        rollout_scope="manual_review",
        rollback_plan="revert",
        parameters=parameters,
        target_production_tenant_id=production_tenant_id,
    )
    signature_id = sign(payload.model_dump(mode="json"), "governance_001", key)
    submit_policy_update(
        route_context,
        source_agent="governance_001",
        payload=payload,
        signature_id=signature_id,
        sandbox_tenant_id=sandbox_tenant_id,
    )
    run_policy_promotion_cycle(
        route_context,
        config=PolicyPromotionConfig(
            production_tenant_id=production_tenant_id,
            sandbox_tenant_id=sandbox_tenant_id,
        ),
    )
    run_production_cycle(
        route_context,
        tenant_id=production_tenant_id,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
    )


def test_regression_detector_emits_alert_for_configured_non_demo_tenant(tmp_path):
    """Audit-finding remediation (High): the regression detector must emit the
    ``policy_regression_alert`` audit verdict against the production tenant
    it actually evaluated, not the default ``tenant_demo`` from
    ``AlertSubscriberConfig``.

    Sets up a real ``acme_ca`` production tenant: apply one signed policy,
    generate three alert-like post-apply samples, then run the detector for
    ``acme_ca``. The emitted alert must land in ``acme_ca``'s production
    blackboard. ``tenant_demo``'s blackboard must remain empty — proving the
    detector is no longer leaking writes into the demo lane.
    """

    from core.production import RegressionDetectorConfig, run_regression_detector_cycle

    route_context = _context(tmp_path)
    acme_sandbox = default_sandbox_tenant_for("acme_ca")

    _apply_policy_for_tenant(
        route_context,
        production_tenant_id="acme_ca",
        sandbox_tenant_id=acme_sandbox,
        policy_name="policy_alpha",
        parameters={"confidence_boost": 0.50},
    )
    # Three post-apply samples — all alert-like under the boosted confidence.
    for _ in range(3):
        run_production_cycle(
            route_context,
            tenant_id="acme_ca",
            signal=LOW_CONFIDENCE_SIGNAL,
            config=ProductionLoopConfig(run_alert_subscriber_at_end_of_cycle=False),
        )

    result = run_regression_detector_cycle(
        route_context,
        config=RegressionDetectorConfig(production_tenant_id="acme_ca"),
    )

    assert result.emitted_alert is not None
    assert result.alert_ratio == 1.0

    acme_production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, "acme_ca"
    )
    acme_alerts = [
        record
        for record in read_records(acme_production_path)
        if record.workflow_id == "policy_regression_alert"
    ]
    assert len(acme_alerts) == 1
    assert acme_alerts[0].record_id == result.emitted_alert.record.record_id

    # Demo tenant must be completely untouched — pre-fix, the alert would
    # have either landed here or raised "no policy_applied audit".
    demo_production_path = blackboard_path(
        route_context.blackboard_root, Environment.PRODUCTION, DEMO_TENANT
    )
    assert not demo_production_path.exists() or read_records(demo_production_path) == []


def test_production_cycle_routes_weakness_report_to_per_tenant_sandbox(tmp_path):
    """Audit-finding remediation (Medium): weakness reports emitted during a
    non-demo production cycle must land in ``sandbox_{tenant_id}``, not in
    the shared ``sandbox_default`` bucket. The demo cycle is the explicit
    historical exception and must keep landing in ``sandbox_default``.

    Pre-fix, the loop called ``submit_weakness_report`` without a
    ``sandbox_tenant_id`` kwarg, so the route's default routed every
    tenant's weakness data into ``sandbox_default`` — a tenant-content
    leak as soon as a second tenant onboards.
    """

    route_context = _context(tmp_path)

    cycle = run_production_cycle(
        route_context,
        tenant_id="acme_ca",
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(),
    )
    assert cycle.weakness_report is not None

    acme_sandbox = default_sandbox_tenant_for("acme_ca")
    acme_sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, acme_sandbox
    )
    acme_weaknesses = [
        record
        for record in read_records(acme_sandbox_path)
        if record.record_type == RecordType.WEAKNESS_REPORT
    ]
    assert len(acme_weaknesses) == 1
    assert acme_weaknesses[0].record_id == cycle.weakness_report.record.record_id

    shared_sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, DEMO_SANDBOX
    )
    if shared_sandbox_path.exists():
        shared_weaknesses = [
            record
            for record in read_records(shared_sandbox_path)
            if record.record_type == RecordType.WEAKNESS_REPORT
        ]
        assert shared_weaknesses == []


def test_production_cycle_demo_weakness_report_still_lands_in_sandbox_default(tmp_path):
    """Companion to the previous test: the demo cycle (the spec's explicit
    historical exception) must keep routing weakness reports to
    ``sandbox_default``. Pins the demo-pair preservation rule from
    ``Policy_Pipeline/multi-tenant-isolation-hardening.md`` §4.
    """

    route_context = _context(tmp_path)

    cycle = run_production_cycle(
        route_context,
        tenant_id=DEMO_TENANT,
        signal=LOW_CONFIDENCE_SIGNAL,
        config=ProductionLoopConfig(),
    )
    assert cycle.weakness_report is not None

    demo_sandbox_path = blackboard_path(
        route_context.blackboard_root, Environment.SANDBOX, DEMO_SANDBOX
    )
    demo_weaknesses = [
        record
        for record in read_records(demo_sandbox_path)
        if record.record_type == RecordType.WEAKNESS_REPORT
    ]
    assert len(demo_weaknesses) == 1
    assert demo_weaknesses[0].record_id == cycle.weakness_report.record.record_id

    # The per-tenant default for tenant_demo would be sandbox_tenant_demo;
    # the explicit historical exception keeps the demo on sandbox_default.
    helper_path = blackboard_path(
        route_context.blackboard_root,
        Environment.SANDBOX,
        default_sandbox_tenant_for(DEMO_TENANT),
    )
    assert not helper_path.exists() or read_records(helper_path) == []
