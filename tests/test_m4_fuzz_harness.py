from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.afe_ledger import AfeLedger, LedgerError, ReplenishEvent
from mmi.m4.evidence_chain import ChainError, EvidenceChain
from mmi.m4.fuzz_runner import (
    VALID_CANARY_RULES,
    VALID_SUMMARY,
    run_all_targets,
    run_fuzz_target,
)
from mmi.m4.parser_surface import ParseSurfaceError, parse_evidence_json, parse_summary_json
from mmi.m4.stage_fsm import FsmError, FsmEvent, FsmState, apply_event


def test_phase2_fuzz_all_targets_pass_default_seed():
    failures = run_all_targets(seed=1, iters=50)
    assert failures == [], failures


def test_parser_rejects_trailing_garbage():
    with pytest.raises(ParseSurfaceError):
        parse_evidence_json('{"a": 1} trailing')


def test_summary_requires_perfect_claim_false():
    bad = json.loads(VALID_SUMMARY)
    bad["perfect_claim"] = True
    with pytest.raises(ParseSurfaceError):
        parse_summary_json(json.dumps(bad))


def test_fsm_rejects_pass_from_wrong_state():
    state = FsmState.INIT
    with pytest.raises(FsmError):
        apply_event(state, FsmEvent.END_INTERVAL_PASS)


def test_ledger_rejects_unattributed_burn():
    ledger = AfeLedger(balance=100)
    with pytest.raises(LedgerError):
        ledger.apply_burn("", 10)


def test_evidence_chain_rejects_gap():
    chain = EvidenceChain(stage_id="C-M4", run_nonce="n1")
    chain.append(0, {"result": "PASS"})
    with pytest.raises(ChainError):
        chain.append(2, {"result": "PASS"})


def test_fuzz_target_parser_isolated():
    assert run_fuzz_target("parser", seed=42, iters=30) == []


def test_harness_rejects_evidence_under_authority(tmp_path, monkeypatch):
    import scripts.m4_fuzz_harness as harness

    bad_evidence = tmp_path / "authority" / "mmi" / "project_brain" / "evidence" / "fuzz"
    authority = tmp_path / "authority"
    authority.mkdir(parents=True)
    bad_evidence.mkdir(parents=True)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "m4_fuzz_harness.py",
            "--target",
            "parser",
            "--seed",
            "1",
            "--iters",
            "5",
            "--evidence",
            str(bad_evidence),
            "--authority",
            str(authority),
        ],
    )
    assert harness.main() == 2


def test_resolve_fuzz_evidence_default_outside_repo(tmp_path, monkeypatch):
    from mmi.m4.evidence_paths import is_under_authority, resolve_fuzz_evidence_dir

    authority = tmp_path / "authority"
    authority.mkdir()
    external = tmp_path / "external_evidence"
    monkeypatch.setenv("MMI_EVIDENCE_ROOT", str(external))

    fuzz_dir = resolve_fuzz_evidence_dir(None, authority)
    assert fuzz_dir == (external / "fuzz").resolve()
    assert not is_under_authority(fuzz_dir, authority)
    assert fuzz_dir.is_dir()


def test_harness_default_evidence_resolves_without_explicit_flag(tmp_path, monkeypatch):
    import scripts.m4_fuzz_harness as harness

    external = tmp_path / "external_evidence"
    monkeypatch.setenv("MMI_EVIDENCE_ROOT", str(external))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "m4_fuzz_harness.py",
            "--target",
            "parser",
            "--seed",
            "1",
            "--iters",
            "5",
            "--authority",
            str(REPO),
        ],
    )
    assert harness.main() == 0
    assert (external / "fuzz" / "fuzz_summary.json").is_file()


def test_resolve_fuzz_evidence_fallback_when_host_default_readonly(tmp_path, monkeypatch):
    from mmi.m4 import evidence_paths

    authority = tmp_path / "authority"
    authority.mkdir()
    fallback_root = tmp_path / "fallback_evidence"
    monkeypatch.delenv("MMI_EVIDENCE_ROOT", raising=False)

    def fake_candidates():
        return [Path("/var/mmi_m4_evidence"), fallback_root]

    monkeypatch.setattr(evidence_paths, "evidence_root_candidates", fake_candidates)
    monkeypatch.setattr(
        evidence_paths,
        "is_writable_dir",
        lambda p: p.resolve().as_posix().startswith(fallback_root.resolve().as_posix()),
    )

    fuzz_dir = evidence_paths.resolve_fuzz_evidence_dir(None, authority)
    assert fuzz_dir == (fallback_root / "fuzz").resolve()
    assert not evidence_paths.is_under_authority(fuzz_dir, authority)


def test_harness_cli_all_passes(tmp_path, monkeypatch):
    import scripts.m4_fuzz_harness as harness

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "m4_fuzz_harness.py",
            "--target",
            "all",
            "--seed",
            "1",
            "--iters",
            "20",
            "--evidence",
            str(tmp_path / "fuzz"),
            "--authority",
            str(REPO),
        ],
    )
    assert harness.main() == 0
    assert (tmp_path / "fuzz" / "fuzz_summary.json").is_file()


def test_fuzz_runner_fails_on_broken_fsm(monkeypatch):
    from mmi.m4 import fuzz_runner

    def broken_fsm(rng, iters, seed):
        return [fuzz_runner.FuzzFailure("fsm", 0, seed, "injected")]

    monkeypatch.setitem(fuzz_runner._TARGET_RUNNERS, "fsm", broken_fsm)
    failures = run_fuzz_target("fsm", seed=1, iters=1)
    assert failures
