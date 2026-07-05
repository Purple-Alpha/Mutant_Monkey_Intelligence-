from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from weapon_battlefield_scoring import fingerprint_digest, generate_proof_bundle


def test_generate_proof_bundle_atomic_write(tmp_path: Path) -> None:
    evidence = tmp_path / "EVIDENCE"
    bundle = generate_proof_bundle(
        {
            "fix_id": "demo_fix",
            "timestamp": "2026-07-02T00:00:00+00:00",
            "authority_hash": "abc",
            "regression_verdict": "PASS",
            "fix_verdict": "CONTAINED",
            "overall_gate_status": "CLEAN",
        },
        evidence,
    )
    path = evidence / "proof_gate_summary.json"
    assert path.exists()
    assert bundle["suite"] == "proof_gate_v1"
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["overall_gate_status"] == "CLEAN"
    assert not (evidence / "proof_gate_summary.json.tmp").exists()


def test_after_digest_persisted_on_disk(tmp_path: Path) -> None:
    evidence = tmp_path / "EVIDENCE"
    bundle = generate_proof_bundle(
        {
            "fix_id": "demo_fix",
            "authority_fingerprint_after_digest": "deadbeef",
            "overall_gate_status": "CLEAN",
        },
        evidence,
    )
    on_disk = json.loads((evidence / "proof_gate_summary.json").read_text(encoding="utf-8"))
    assert on_disk["authority_fingerprint_after_digest"] == "deadbeef"
    assert bundle["authority_fingerprint_after_digest"] == "deadbeef"


def test_rejects_patch_context_inside_authority(tmp_path: Path) -> None:
    import pytest

    authority = tmp_path / "authority"
    authority.mkdir()
    inside = authority / "proof_gate"
    inside.mkdir()

    from proof_gate_harness import assert_patch_context_outside_authority

    with pytest.raises(SystemExit, match="must not be inside authority"):
        assert_patch_context_outside_authority(inside, authority)


def test_rejects_mismatched_proof_context(tmp_path: Path) -> None:
    import pytest

    from proof_gate_harness import _assert_context_matches_fix_id

    auto = {"proof_type": "purple_scenario", "scenario_id": "purple_inj_policy_rewrite"}
    ctx = {"proof_type": "provisioner", "command": "mesh-smash"}
    with pytest.raises(SystemExit, match="does not match"):
        _assert_context_matches_fix_id("purple_inj_policy_rewrite", auto, ctx)


def test_rejects_expect_verdict_override(tmp_path: Path) -> None:
    import pytest

    from proof_gate_harness import resolve_proof_target

    ctx = {
        "fix_id": "mesh-smash",
        "proof_type": "provisioner",
        "command": "mesh-smash",
        "expect_verdict": "FAILED",
    }
    with pytest.raises(SystemExit, match="expect_verdict"):
        resolve_proof_target("mesh-smash", ctx)


def test_run_regression_check_shape(tmp_path: Path) -> None:
    import sys

    authority = tmp_path / "authority"
    authority.mkdir()
    scripts = authority / "scripts"
    scripts.mkdir()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

    with patch("phase1_stability_harness.run_harness") as mock_harness:
        mock_harness.return_value = {
            "verdict": "PASS",
            "decision": {"pass": True, "tiers": [4]},
            "summary_path": "/tmp/x/phase1_stability_summary.json",
        }
        from phase1_stability_harness import run_regression_check

        result = run_regression_check(authority, tmp_path / "lab", runs=1)
        assert result["pass"] is True
        assert result["verdict"] == "PASS"
