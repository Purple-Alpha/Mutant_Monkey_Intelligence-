"""Tests for the Acme Effective Parameter Report demo generator."""

from __future__ import annotations

from pathlib import Path

from core.production_state import (
    read_tenant_override_audit_events,
    tenant_override_audit_path,
)
from scripts.acme_effective_parameter_report_demo import (
    DEMO_POLICY_VERSION,
    DEMO_SOURCE,
    DEMO_TENANT_ID,
    generate_demo_report,
)


def test_generate_demo_report_uses_real_cli_report_output(tmp_path: Path) -> None:
    blackboard_root = tmp_path / "blackboard"
    out_path = tmp_path / "Acme_Effective_Parameter_Report_Demo.md"

    generated = generate_demo_report(
        blackboard_root=blackboard_root,
        out_path=out_path,
        reset_existing=False,
    )

    assert generated == out_path
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# NorthStar Inbox Shield — Effective Parameter Report")
    assert f"**Tenant:** {DEMO_TENANT_ID}" in content
    assert f"**Signed policy version:** {DEMO_POLICY_VERSION}" in content
    assert "| `fraud_risk_floor_lift` | `10` | `tenant_override` | `5` | `10` |" in content
    assert "| `attachment_risk_floor_lift` | `0` | `signed_policy` | `0` | `(none)` |" in content
    assert "| `url_obfuscation_floor_lift` | `8` | `tenant_override` | `5` | `8` |" in content
    assert "`vendor_invoice_recall_floor`: `phase_1_5`" in content
    assert "`tenant_parameter_override_updated`" in content
    assert f"`{DEMO_SOURCE}`" in content
    assert "**Override applied for scoring:** yes" in content

    events = read_tenant_override_audit_events(
        tenant_override_audit_path(blackboard_root, DEMO_TENANT_ID)
    )
    assert [event.event_type for event in events] == [
        "tenant_parameter_override_created",
        "tenant_parameter_override_updated",
    ]
