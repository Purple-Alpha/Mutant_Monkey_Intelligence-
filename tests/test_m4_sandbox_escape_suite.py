from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.sandbox_escape import (
    EscapeOutcome,
    SANDBOX_MODULES,
    SandboxBoundaryPolicy,
    SandboxContext,
    module_specs,
    run_all_modules,
    run_module,
    suite_passed,
)


def test_all_sandbox_modules_deny_or_contained():
    ctx = SandboxContext(
        authority_root=REPO,
        lab_root=Path("/tmp/mmi_chaos_lab/sim"),
        evidence_root=Path("/tmp/m4_evidence_root"),
    )
    results = run_all_modules(ctx)
    assert len(results) == len(SANDBOX_MODULES)
    assert suite_passed(results), [(r.module, r.result) for r in results if not r.passed]


def test_se_9p_vectors_present():
    spec = module_specs()["SE-9P"]
    assert "9p" in spec.escape_attempted.lower() or any("9p" in v.vector_id for v in spec.vectors)


def test_module_fails_on_allow(monkeypatch):
    class AllowPolicy(SandboxBoundaryPolicy):
        def _decide(self, module_id, vector, ctx):
            return EscapeOutcome.ALLOW

    ctx = SandboxContext(REPO, Path("/tmp/lab"), Path("/tmp/evidence"))
    result = run_module("SE-FS", ctx, AllowPolicy())
    assert result.result == EscapeOutcome.ALLOW
    assert not result.passed


def test_suite_cli_passes(tmp_path, monkeypatch):
    import scripts.m4_sandbox_escape_suite as suite

    monkeypatch.setenv("MMI_EVIDENCE_ROOT", str(tmp_path / "evidence_root"))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "m4_sandbox_escape_suite.py",
            "--authority",
            str(REPO),
        ],
    )
    assert suite.main() == 0
    assert (tmp_path / "evidence_root" / "sandbox" / "sandbox_escape_summary.json").is_file()


def test_suite_rejects_evidence_under_authority(tmp_path, monkeypatch):
    import scripts.m4_sandbox_escape_suite as suite

    authority = tmp_path / "authority"
    authority.mkdir()
    bad = authority / "mmi" / "project_brain" / "evidence" / "sandbox"
    bad.mkdir(parents=True)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "m4_sandbox_escape_suite.py",
            "--evidence",
            str(bad),
            "--authority",
            str(authority),
        ],
    )
    assert suite.main() == 2
