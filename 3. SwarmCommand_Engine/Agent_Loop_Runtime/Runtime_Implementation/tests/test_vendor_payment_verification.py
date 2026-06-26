"""Evidence Stage 1 proof for Vendor Payment Verification workflow (Tier A ES1)."""

from __future__ import annotations

import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.blackboard import GovernanceError
from core.workflows import two_channel_confirmation as tcc
from core.workflows.vendor_payment_verification import (
    ENGINE_VERSION,
    SCHEMA_VERSION,
    TIER_B_UNAVAILABLE,
    VPVPaymentRequest,
    digest_request,
    run_vendor_payment_verification,
)

TENANT = "tenant_vpv_demo"
FINDING_ID = "vendor_payment:case-001"
NOW = datetime(2026, 6, 26, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _request(
    *,
    sender: str = "billing@vendor.example",
    headers: dict[str, str] | None = None,
    body_plain: str = "Please process invoice 1001.",
    subject: str | None = "Invoice 1001",
    known_good_domains: tuple[str, ...] = ("vendor.example",),
) -> VPVPaymentRequest:
    return VPVPaymentRequest(
        tenant_id=TENANT,
        finding_id=FINDING_ID,
        sender=sender,
        headers=headers or {},
        body_plain=body_plain,
        subject=subject,
        known_good_domains=known_good_domains,
        blackboard_root=Path("blackboard"),
    )


def test_emits_schema_locked_packet_with_tier_b_unavailable():
    packet = run_vendor_payment_verification(_request())
    assert packet.schema_version == SCHEMA_VERSION
    assert packet.banking_delta == TIER_B_UNAVAILABLE
    assert packet.vendor_known == TIER_B_UNAVAILABLE
    assert packet.payment_pattern_anomaly == TIER_B_UNAVAILABLE
    assert packet.reproducibility.engine_version == ENGINE_VERSION


def test_benign_message_can_clear_when_checks_pass():
    headers = {
        "Authentication-Results": (
            "example.com; spf=pass; dkim=pass; dmarc=pass"
        ),
    }
    tcc.record_confirmation_request(
        tenant_id=TENANT,
        finding_id=FINDING_ID,
        detector="vpv_test",
        risk_floor=70,
        requested_by="operator:test",
        requested_at=NOW,
        blackboard_root=Path("blackboard"),
    )
    tcc.record_confirmation_outcome(
        tenant_id=TENANT,
        finding_id=FINDING_ID,
        outcome_status="confirmed",
        outcome_by="operator:test",
        outcome_at=NOW,
        channel_kind="previously_known_phone",
        channel_description="called vendor main line",
        reason="verified banking change",
        blackboard_root=Path("blackboard"),
    )
    packet = run_vendor_payment_verification(
        _request(headers=headers, body_plain="Updated remittance details attached.")
    )
    assert packet.oob_confirmation == "present"
    assert packet.risk_verdict == "CLEAR"


def test_ghost_thread_and_failed_auth_raise_high():
    headers = {
        "Authentication-Results": "example.com; spf=fail; dkim=fail; dmarc=fail",
    }
    packet = run_vendor_payment_verification(
        _request(
            headers=headers,
            subject="Re: Updated wire instructions",
            body_plain="Use the new account immediately.",
        )
    )
    assert packet.thread_integrity == "forged"
    assert packet.sender_auth == "fail"
    assert packet.risk_verdict == "HIGH"


def test_lookalike_domain_high_band_raises_high():
    packet = run_vendor_payment_verification(
        _request(
            sender="billing@vend0r.example",
            known_good_domains=("vendor.example",),
        )
    )
    assert packet.domain_similarity == "high"
    assert packet.risk_verdict == "HIGH"


def test_urgency_without_oob_raises_high():
    packet = run_vendor_payment_verification(
        _request(
            body_plain=(
                "Please call us immediately to finalize payment. "
                "Do not use email for payment instructions."
            ),
        )
    )
    assert packet.urgency_markers
    assert packet.oob_confirmation == "absent"
    assert packet.risk_verdict == "HIGH"


def test_oob_pending_is_distinct_from_absent():
    tcc.record_confirmation_request(
        tenant_id=TENANT,
        finding_id=FINDING_ID,
        detector="vpv_test",
        risk_floor=70,
        requested_by="operator:test",
        requested_at=NOW,
        blackboard_root=Path("blackboard"),
    )
    packet = run_vendor_payment_verification(_request())
    assert packet.oob_confirmation == "pending"
    assert packet.risk_verdict == "ELEVATED"


def test_digest_is_stable_for_same_inputs():
    request = _request()
    assert digest_request(request) == digest_request(request)


def test_rejects_invalid_finding_id():
    request = _request()
    bad = VPVPaymentRequest(
        tenant_id=request.tenant_id,
        finding_id="../escape",
        sender=request.sender,
        headers=request.headers,
        body_plain=request.body_plain,
        subject=request.subject,
        known_good_domains=request.known_good_domains,
    )
    with pytest.raises(GovernanceError):
        run_vendor_payment_verification(bad)


def test_no_network_or_subprocess_calls():
    source = Path(__file__).parents[1] / "core/workflows/vendor_payment_verification.py"
    text = source.read_text(encoding="utf-8")
    assert "socket" not in text
    assert "subprocess" not in text
    assert "requests" not in text

    with pytest.MonkeyPatch.context() as mp:
        def _blocked(*_args, **_kwargs):
            raise AssertionError("network call attempted")

        mp.setattr(socket, "socket", _blocked)
        run_vendor_payment_verification(_request())

    proc = subprocess.run(
        [
            "python3",
            "-c",
            "import pathlib; t=pathlib.Path('core/workflows/vendor_payment_verification.py').read_text(); "
            "assert 'subprocess' not in t",
        ],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
