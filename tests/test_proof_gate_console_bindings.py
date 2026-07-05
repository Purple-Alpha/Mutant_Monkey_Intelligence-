from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CHAOS = Path(__file__).resolve().parents[1] / "mmi" / "project_brain" / "chaos"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
for p in (CHAOS, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from console_fingerprint_ledger import (  # noqa: E402
    append_known_good,
    ledger_contains,
    verify_chain,
)
from mmi_canonical_digest import canonical_object_digest  # noqa: E402
from proof_gate_harness import (  # noqa: E402
    apply_console_bindings,
    materialize_patch_diff,
    _make_run_id,
)


def test_canonical_object_digest_stable() -> None:
    obj = {"b": 2, "a": 1}
    assert canonical_object_digest(obj) == canonical_object_digest({"a": 1, "b": 2})


def test_materialize_patch_from_content(tmp_path: Path) -> None:
    evidence = tmp_path / "EVIDENCE"
    evidence.mkdir()
    ctx = {"patch_content": "diff content\n"}
    path = materialize_patch_diff(evidence, ctx)
    assert path is not None
    assert path.read_text() == "diff content\n"


def test_materialize_patch_missing_returns_none(tmp_path: Path) -> None:
    evidence = tmp_path / "EVIDENCE"
    evidence.mkdir()
    assert materialize_patch_diff(evidence, {}) is None


def test_fingerprint_ledger_append_and_chain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ledger_path = tmp_path / "state" / "fingerprint_ledger.jsonl"
    monkeypatch.setattr("console_fingerprint_ledger.DEFAULT_LEDGER_PATH", ledger_path)
    monkeypatch.setattr("console_fingerprint_ledger.ALLOWED_ROOT", tmp_path / "state")

    append_known_good("GENESIS", "a" * 64, "genesis_seed", 1_700_000_000_000, path=ledger_path)
    append_known_good("pg-run-1", "b" * 64, "proof_gate", 1_700_000_000_001, path=ledger_path)
    assert ledger_contains("a" * 64, ledger_path)
    assert verify_chain(ledger_path)


def test_apply_console_bindings_blocks_without_patch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ledger_path = tmp_path / "state" / "fingerprint_ledger.jsonl"
    monkeypatch.setattr("console_fingerprint_ledger.DEFAULT_LEDGER_PATH", ledger_path)
    monkeypatch.setattr("console_fingerprint_ledger.ALLOWED_ROOT", tmp_path / "state")
    append_known_good("GENESIS", "c" * 64, "genesis_seed", 1, path=ledger_path)

    evidence = tmp_path / "ctx" / "EVIDENCE"
    evidence.mkdir(parents=True)
    summary = {
        "fix_id": "test_fix",
        "authority_hash": "c" * 64,
        "proof_of_fix": {"verdict": "CONTAINED"},
        "proof_of_regression": {"verdict": "PASS"},
        "blockers": [],
    }
    monkeypatch.setattr("proof_gate_harness.capture_budget_snapshot", lambda run_id, ts: {
        "run_id": run_id,
        "budget_spent": 0,
        "budget_cap_day": 8_000_000,
        "budget_cap_hour": 800_000,
        "deadman_armed": True,
        "captured_at_ms": ts,
    })

    out = apply_console_bindings(
        summary,
        evidence=evidence,
        patch_label=tmp_path / "ctx",
        ctx={},
        fix_id="test_fix",
        overall="CLEAN",
    )
    assert out["overall_gate_status"] == "BLOCKED"
    assert any("patch artifact missing" in b for b in out.get("blockers", []))


def test_make_run_id_format() -> None:
    rid = _make_run_id("fix", Path("/tmp/evidence"), 123)
    assert rid.startswith("pg-fix-")
    assert len(rid.split("-")[-1]) == 12


def test_capture_budget_snapshot_without_ledger() -> None:
    from proof_gate_harness import capture_budget_snapshot

    snap = capture_budget_snapshot("pg-test-001", 1_700_000_000_000)
    assert snap is not None
    assert snap["budget_spent"] == 0
    assert snap["budget_cap_day"] == 8_000_000
    assert snap["budget_cap_hour"] == 800_000
    assert snap["run_id"] == "pg-test-001"


def test_console_harness_reruns_on_same_evidence_dir(tmp_path: Path) -> None:
    from console_server_harness import run_harness

    authority = Path(__file__).resolve().parents[1]
    evidence = tmp_path / "harness_rerun"
    first = run_harness(authority, evidence)
    second = run_harness(authority, evidence)
    assert first["overall_gate_status"] == "CLEAN"
    assert second["overall_gate_status"] == "CLEAN"


def test_apply_console_bindings_genomic_episode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from mmi_canonical_digest import patch_context_tree_digest

    ledger_path = tmp_path / "state" / "fingerprint_ledger.jsonl"
    monkeypatch.setattr("console_fingerprint_ledger.DEFAULT_LEDGER_PATH", ledger_path)
    monkeypatch.setattr("console_fingerprint_ledger.ALLOWED_ROOT", tmp_path / "state")
    append_known_good("GENESIS", "d" * 64, "genesis_seed", 1, path=ledger_path)

    ctx_root = tmp_path / "ctx"
    evidence = ctx_root / "EVIDENCE"
    evidence.mkdir(parents=True)
    patch_file = evidence / "patch.diff"
    patch_file.write_text("patch-bytes\n", encoding="utf-8")

    monkeypatch.setattr("proof_gate_harness.capture_budget_snapshot", lambda run_id, ts: {
        "run_id": run_id,
        "budget_spent": 0,
        "budget_cap_day": 8_000_000,
        "budget_cap_hour": 800_000,
        "deadman_armed": True,
        "captured_at_ms": ts,
    })

    constraint_id = "grc-" + "a" * 16
    digest = patch_context_tree_digest(ctx_root)
    out = apply_console_bindings(
        {
            "fix_id": "genomic_fix",
            "authority_hash": "d" * 64,
            "proof_of_fix": {"verdict": "CONTAINED"},
            "proof_of_regression": {"verdict": "PASS"},
            "blockers": [],
        },
        evidence=evidence,
        patch_label=ctx_root,
        ctx={"patch_content": "patch-bytes\n"},
        fix_id="genomic_fix",
        overall="CLEAN",
        genomic_episode={
            "constraint_id": constraint_id,
            "patch_context_digest": digest,
            "episode_id": "gre-001",
        },
    )
    assert out["genomic_episode"]["constraint_id"] == constraint_id
    assert out["genomic_episode"]["patch_context_digest"] == digest
    assert out["genomic_episode"]["episode_id"] == "gre-001"
