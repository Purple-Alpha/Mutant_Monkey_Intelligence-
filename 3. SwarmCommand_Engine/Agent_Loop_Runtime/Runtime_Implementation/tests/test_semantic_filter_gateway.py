"""Gateway SemanticFilter tests — DER hardening."""

import pytest

from core.control_plane import (
    AgentIdentityGateway,
    ControlPlaneAuditTrail,
    GatewayController,
    GatewayRejected,
    GatewayRequest,
    LoopDetector,
    BreakerStore,
    RingController,
    SessionBudgetStore,
    TenantSegmentationController,
    SemanticFilterViolation,
)
from core.control_plane.budget import RoleTier


def _gateway() -> GatewayController:
    audit = ControlPlaneAuditTrail()
    identity = AgentIdentityGateway()
    gw = GatewayController(
        identity=identity,
        rings=RingController(audit=audit),
        budgets=SessionBudgetStore(audit=audit),
        breakers=BreakerStore(),
        loop_detector=LoopDetector(),
        segmentation=TenantSegmentationController(),
        audit=audit,
    )
    identity.issue(
        token="tok",
        agent_id="blue_detection_001",
        tenant_id="tenant_a",
        tool_scope={"scan"},
    )
    gw.budgets.open_session("s1", tier=RoleTier.DETECTION)
    return gw


def _request(args):
    return GatewayRequest(
        token="tok",
        claimed_agent_id="blue_detection_001",
        tenant_id="tenant_a",
        tool="scan",
        session_id="s1",
        args=args,
    )


def test_gateway_rejects_approved_in_der_payload():
    gw = _gateway()
    with pytest.raises(GatewayRejected) as exc:
        gw.handle(
            _request(
                {
                    "disposition": "clear",
                    "note": "payment approved for processing",
                }
            )
        )
    assert exc.value.stage == "semantic_filter"


def test_gateway_rejects_authority_key_in_payload():
    gw = _gateway()
    with pytest.raises(GatewayRejected):
        gw.handle(
            _request({"disposition": "suspicious", "verdict": "HIGH_RISK"})
        )


def test_gateway_allows_observation_payload():
    gw = _gateway()
    decision = gw.handle(
        _request(
            {
                "observations": [
                    "payroll_diversion_pattern",
                    "payroll_vocabulary_signal",
                ]
            }
        )
    )
    assert decision.dispatched


def test_gateway_skips_non_der_payload_with_safe_word():
    gw = _gateway()
    decision = gw.handle(_request({"payload": "safe"}))
    assert decision.dispatched


def test_semantic_filter_allows_unauthorized_without_authorized_token():
    from core.control_plane.semantic_filter import SemanticFilter

    hits = SemanticFilter().scan_text("unauthorized payroll destination change")
    assert "forbidden_der_token:authorized" not in hits
