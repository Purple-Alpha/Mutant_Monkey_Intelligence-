from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.authority_seal import store_pre_provision_seal
from mmi.m4.boundary_daemon import load_authority_manifest, load_policy_manifest, run_daemon_selftest
from mmi.m4.key_custody import SoftwareStubCustodian


def _fixture_bundle(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "authority"
    root.mkdir()
    (root / "file.txt").write_text("x", encoding="utf-8")
    evidence = tmp_path / "evidence"
    custodian = SoftwareStubCustodian()
    store_pre_provision_seal(evidence, root, custodian)
    return evidence, evidence / "policy_manifest.json", evidence / "authority_manifest.json"


def test_load_policy_and_authority_manifests(tmp_path: Path):
    evidence, policy_path, authority_path = _fixture_bundle(tmp_path)
    policy = load_policy_manifest(policy_path)
    authority = load_authority_manifest(authority_path)
    assert policy.manifest_hash == authority.manifest_hash
    assert len(authority.entries) >= 1


def test_daemon_selftest_arms_and_refuses_bad_manifest(tmp_path: Path):
    evidence, policy_path, authority_path = _fixture_bundle(tmp_path)
    custodian = SoftwareStubCustodian()
    # Re-seal with the same custodian instance used for verify (stub key is per-instance).
    root = tmp_path / "authority"
    store_pre_provision_seal(evidence, root, custodian)
    policy_path = evidence / "policy_manifest.json"
    authority_path = evidence / "authority_manifest.json"
    result = run_daemon_selftest(evidence, policy_path, authority_path, custodian=custodian)
    assert result["armed_on_valid_policy"] is True
    assert result["bad_manifest_refused"] is True
    assert result["heartbeat_visible"] is True
    assert (evidence / "daemon_heartbeat.json").exists()
    hb = json.loads((evidence / "daemon_heartbeat.json").read_text(encoding="utf-8"))
    assert hb["armed"] is True
    assert hb["boundary_deadman_gap_s"] == 30
