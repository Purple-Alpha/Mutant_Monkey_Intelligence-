from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.authority_seal import (
    AuthoritySealError,
    build_enforcement_manifest,
    daemon_may_arm,
    seal_fingerprint,
    sign_h0_seal,
    sign_policy_manifest,
    store_pre_provision_seal,
    verify_fingerprint,
    verify_h0_seal,
    verify_policy_manifest,
)
from mmi.m4.key_custody import SoftwareStubCustodian


def _mini_authority(tmp_path: Path) -> Path:
    root = tmp_path / "authority"
    root.mkdir()
    (root / "README.md").write_text("authority\n", encoding="utf-8")
    git = root / ".git"
    git.mkdir()
    (git / "config").write_text("[core]\n", encoding="utf-8")
    hooks = git / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit.sample").write_text("# sample\n", encoding="utf-8")
    return root


def test_build_manifest_lists_entries_with_fileids(tmp_path: Path):
    root = _mini_authority(tmp_path)
    manifest = build_enforcement_manifest(root)
    assert len(manifest.entries) >= 4
    assert all(entry.volume_guid and entry.file_reference_number for entry in manifest.entries)
    assert any(entry.relative_path == ".git/config" for entry in manifest.entries)


def test_seal_fingerprint_stable_for_unchanged_tree(tmp_path: Path):
    root = _mini_authority(tmp_path)
    h0_a = seal_fingerprint(root)
    h0_b = seal_fingerprint(root)
    assert h0_a == h0_b
    assert h0_a.startswith("sha256:")


def test_h0_signed_before_provision(tmp_path: Path):
    root = _mini_authority(tmp_path)
    custodian = SoftwareStubCustodian()
    manifest = build_enforcement_manifest(root)
    seal = sign_h0_seal(manifest, custodian)
    assert seal.h0_signed_before_provision is True
    verify_h0_seal(seal, custodian)


def test_policy_hash_mismatch_refused(tmp_path: Path):
    root = _mini_authority(tmp_path)
    custodian = SoftwareStubCustodian()
    manifest = build_enforcement_manifest(root)
    policy = sign_policy_manifest(manifest, custodian)
    verify_policy_manifest(policy, custodian, current_manifest=manifest)

    from mmi.m4.authority_seal import SignedPolicyManifest

    tampered = SignedPolicyManifest(
        schema_v=policy.schema_v,
        authority_root=policy.authority_root,
        enforcement_key=policy.enforcement_key,
        manifest_hash="sha256:deadbeef",
        entry_count=policy.entry_count,
        entries=policy.entries,
        custody_key_id=policy.custody_key_id,
        policy_signature=policy.policy_signature,
    )

    with pytest.raises(AuthoritySealError):
        verify_policy_manifest(tampered, custodian, current_manifest=manifest)


def test_daemon_refuses_arm_on_tampered_policy(tmp_path: Path):
    root = _mini_authority(tmp_path)
    custodian = SoftwareStubCustodian()
    manifest = build_enforcement_manifest(root)
    policy = sign_policy_manifest(manifest, custodian)

    ok, _ = daemon_may_arm(policy, custodian, manifest)
    assert ok is True

    (root / "mutated.txt").write_text("changed\n", encoding="utf-8")
    bad_manifest = build_enforcement_manifest(root)
    bad, reason = daemon_may_arm(policy, custodian, bad_manifest)
    assert bad is False
    assert reason


def test_store_pre_provision_writes_evidence_files(tmp_path: Path):
    root = _mini_authority(tmp_path)
    custodian = SoftwareStubCustodian()
    evidence = tmp_path / "evidence" / "boundary"
    result = store_pre_provision_seal(evidence, root, custodian)
    assert result["h0_signed_before_provision"] is True
    assert (evidence / "h0_pre_provision_seal.json").exists()
    assert (evidence / "policy_manifest.json").exists()
    assert (evidence / "authority_manifest.json").exists()

    policy = json.loads((evidence / "policy_manifest.json").read_text(encoding="utf-8"))
    assert policy["manifest_hash"].startswith("sha256:")


def test_verify_fingerprint_detects_mutation(tmp_path: Path):
    root = _mini_authority(tmp_path)
    h0 = seal_fingerprint(root)
    assert verify_fingerprint(root, h0) is True
    (root / "new.txt").write_text("x", encoding="utf-8")
    assert verify_fingerprint(root, h0) is False
