from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.authority_seal import WfpPolicyConfig, store_pre_provision_seal
from mmi.m4.key_custody import SoftwareStubCustodian
from mmi.m4.wfp_policy import (
    EgressDecision,
    WfpPolicyEngine,
    append_wfp_deny_event,
    manifest_requires_clone_probe,
    run_wfp_selftest,
    source_context_matches_policy,
)


def _bundle(tmp_path: Path, *, clone_sid: str | None = None) -> tuple[Path, Path]:
    root = tmp_path / "authority"
    root.mkdir()
    (root / "README.md").write_text("x", encoding="utf-8")
    evidence = tmp_path / "evidence"
    wfp = WfpPolicyConfig.default_dev()
    if clone_sid:
        wfp = WfpPolicyConfig(
            telemetry_egress_allowlist=wfp.telemetry_egress_allowlist,
            clone_sid=clone_sid,
            probe_account_name="MmiWfpProbe",
        )
    store_pre_provision_seal(evidence, root, SoftwareStubCustodian(), wfp_policy=wfp)
    return evidence, evidence / "policy_manifest.json"


def test_t7_contract_allowlist(tmp_path: Path):
    evidence, manifest_path = _bundle(tmp_path)
    engine = WfpPolicyEngine.from_manifest_file(manifest_path)
    deny = engine.evaluate_egress("127.0.0.1", 19998, fixture_id="T7-C1")
    allow = engine.evaluate_egress("127.0.0.1", 9443, fixture_id="T7-C2")
    loopback_deny = engine.evaluate_egress("127.0.0.1", 19999, fixture_id="T7-C3")
    assert deny.decision == EgressDecision.DENY
    assert allow.decision == EgressDecision.ALLOW
    assert loopback_deny.decision == EgressDecision.DENY


def test_wfp_selftest_contract_passes(tmp_path: Path):
    evidence, manifest_path = _bundle(tmp_path)
    result = run_wfp_selftest(evidence, manifest_path, live=False)
    assert result["contract_pass"] is True
    assert result["min_viable_live_t7"] is False
    assert result["source_context_ok"] is None


def test_source_context_uses_signed_manifest_only(tmp_path: Path):
    evidence, manifest_path = _bundle(tmp_path, clone_sid="S-1-5-21-1")
    engine = WfpPolicyEngine.from_manifest_file(manifest_path)
    observed = {"sid": "S-1-5-21-1", "app_container_name": None}
    assert source_context_matches_policy(observed, engine.policy) is True
    assert source_context_matches_policy({"sid": "S-1-5-21-2"}, engine.policy) is False
    assert manifest_requires_clone_probe(engine.policy) is True


def test_live_fail_closed_without_signed_clone_target(tmp_path: Path):
    evidence, manifest_path = _bundle(tmp_path)
    result = run_wfp_selftest(evidence, manifest_path, live=True)
    assert result["source_context_ok"] is False
    assert result["min_viable_live_t7"] is False


def test_wfp_deny_log_schema(tmp_path: Path):
    evidence, manifest_path = _bundle(tmp_path)
    engine = WfpPolicyEngine.from_manifest_file(manifest_path)
    append_wfp_deny_event(
        evidence,
        test_id="T7-C1",
        policy_hash=engine.policy_hash,
        active_rule_snapshot="M4-WFP-001-T7",
        source_process="clone_probe",
        source_namespace_or_context="MmiWfpProbe@S-1-5-21-1",
        destination="127.0.0.1:19998",
        protocol="TCP",
        expected_action="DENY",
        observed_action="DENY",
        rule_id="M4-WFP-001-T7",
        pass_fail="PASS",
        timestamp_source="wfp_audit_timestamp",
    )
    line = (evidence / "wfp_denies.jsonl").read_text(encoding="utf-8").strip()
    payload = json.loads(line)
    for key in (
        "source_namespace_or_context",
        "event_log_pointer",
        "timestamp_source",
        "timestamp_utc",
    ):
        assert key in payload


def test_wfp_helper_does_not_accept_timeout_as_deny_proof():
    helper = REPO / "host_boundary" / "mmi_wfp" / "mmi_wfp_helper.cpp"
    text = helper.read_text(encoding="utf-8")
    deny_line = next(line for line in text.splitlines() if "wfpDenyProven =" in line)
    assert "WSAETIMEDOUT" not in deny_line
    assert "IsAccessDenied(win32Error)" in deny_line
