from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.authority_seal import store_pre_provision_seal
from mmi.m4.key_custody import SoftwareStubCustodian
from mmi.m4.minifilter_policy import (
    FilterDecision,
    FilterOperation,
    MinifilterPolicyEngine,
    run_minifilter_selftest,
)


def _bundle(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "authority"
    root.mkdir()
    (root / "README.md").write_text("x", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    evidence = tmp_path / "evidence"
    store_pre_provision_seal(evidence, root, SoftwareStubCustodian())
    return evidence, evidence / "authority_manifest.json", scratch


def test_t1_t2_contract_denies_authority_mutations(tmp_path: Path):
    evidence, manifest_path, scratch = _bundle(tmp_path)
    engine = MinifilterPolicyEngine.from_manifest_file(manifest_path)
    t1 = engine.evaluate(
        FilterOperation.WRITE,
        engine.authority_root / "probe.txt",
        fixture_id="T1",
    )
    t2 = engine.evaluate(
        FilterOperation.LINK_CREATE,
        scratch / "link",
        fixture_id="T2",
        link_target=engine.authority_root / ".git" / "config",
    )
    allow = engine.evaluate(FilterOperation.WRITE, scratch / "ok.txt", fixture_id="F10")
    assert t1.decision == FilterDecision.DENY
    assert t2.decision == FilterDecision.DENY
    assert allow.decision == FilterDecision.ALLOW


def test_minifilter_selftest_contract_passes(tmp_path: Path):
    evidence, manifest_path, scratch = _bundle(tmp_path)
    result = run_minifilter_selftest(
        evidence,
        manifest_path,
        scratch_root=scratch,
        h0_fingerprint="sha256:test",
        live=False,
    )
    assert result["contract_pass"] is True
    assert result["verify_fingerprint_ok"] is True
    assert (evidence / "minifilter_denies.jsonl").exists()
