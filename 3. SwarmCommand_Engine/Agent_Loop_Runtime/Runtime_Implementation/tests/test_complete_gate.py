"""Tests for the Grok completion gate (audit_tools/complete_gate.py).

The gate must fire only at readiness boundaries, must fail closed on
manifest mismatch / coverage gap / oversize packet / Grok failure /
missing or stale output, and must record an auditable warning when
the operator explicitly overrides.

These tests load the gate via importlib (same pattern as
``test_pre_ship_audit.py``) because ``audit_tools/`` is not a Python
package.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_gate():
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "complete_gate.py"
    )
    spec = importlib.util.spec_from_file_location("complete_gate", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def gate(tmp_path, monkeypatch):
    """Load the gate and point its file-system constants at tmp_path."""

    module = _load_gate()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    audit_outputs = workspace / "audit_outputs"
    audit_outputs.mkdir()
    pending = audit_outputs / "pending"
    pending.mkdir()
    incidents = audit_outputs / "drift_incidents"
    incidents.mkdir()
    env_path = workspace / ".env"
    env_path.write_text("XAI_API_KEY=test-secret-never-echo\n", encoding="utf-8")

    monkeypatch.setattr(module, "WORKSPACE_ROOT", workspace)
    monkeypatch.setattr(module, "ENV_PATH", env_path)
    monkeypatch.setattr(module, "OUTPUT_DIR", audit_outputs)
    monkeypatch.setattr(module, "PENDING_MANIFEST_DIR", pending)
    monkeypatch.setattr(module, "DRIFT_INCIDENT_DIR", incidents)

    def _network_guard(**_):
        raise AssertionError(
            "test reached call_grok without an explicit monkeypatch — "
            "no test must ever contact the live xAI endpoint"
        )

    monkeypatch.setattr(module, "call_grok", _network_guard)

    (workspace / "VISION.md").write_text(
        "# Vision\n\n"
        "## Non-Negotiables (Lock These Forever)\n\n"
        "1. Append-only audit trail.\n"
        "2. Tenant isolation.\n"
        "3. Kill switch always wins.\n\n"
        "## Next Section\n\nUnrelated content.\n",
        encoding="utf-8",
    )

    return module


def _write_manifest(gate_module, *, task_id: str, **fields) -> Path:
    """Write a manifest under the gate's pending dir and return its path."""

    payload = {
        "task_id": task_id,
        "completion_claim": "test completion claim",
        "files_read": [],
        "files_modified": [],
        "files_created": [],
        "commands_run": [],
        "known_unresolved_questions": [],
    }
    payload.update(fields)
    path = gate_module.PENDING_MANIFEST_DIR / f"{task_id}.manifest.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _patch_git(
    gate_module,
    monkeypatch,
    *,
    changed_files: list[str],
    staged_files: list[str] | None = None,
    diff: str = "diff content",
    cached_diff: str | None = None,
    status: str = " M file.md\n",
    ignored: set[str] | None = None,
    untracked: list[str] | None = None,
):
    """Stand in for `_run_git` and `_path_is_git_ignored`.

    ``changed_files`` is the worktree-vs-HEAD set (used by the full
    gate in default mode). ``staged_files`` is the index-vs-HEAD set
    (used by --pre-commit). When ``staged_files`` is None, the
    convention used by most tests, it mirrors ``changed_files`` so
    legacy tests keep working.
    """

    ignored_set = ignored or set()
    staged_files = changed_files if staged_files is None else staged_files
    cached_diff = diff if cached_diff is None else cached_diff
    untracked = untracked or []

    def fake_run_git(args):
        if args[:2] == ["diff", "HEAD"] and len(args) == 2:
            return diff
        if args == ["diff", "HEAD", "--name-only"]:
            return "\n".join(changed_files) + ("\n" if changed_files else "")
        if args == ["diff", "--cached"]:
            return cached_diff
        if args == ["diff", "--cached", "--name-only"]:
            return "\n".join(staged_files) + ("\n" if staged_files else "")
        if args == ["status", "--short"]:
            return status
        if args == ["ls-files", "--others", "--exclude-standard"]:
            return "\n".join(untracked) + ("\n" if untracked else "")
        raise AssertionError(f"unexpected git args: {args}")

    monkeypatch.setattr(gate_module, "_run_git", fake_run_git)
    monkeypatch.setattr(
        gate_module,
        "_path_is_git_ignored",
        lambda path: path in ignored_set,
    )


def _clean_grok_response(blocking: int = 0, warnings: int = 0) -> str:
    body = "No deviations identified.\n" if blocking == 0 and warnings == 0 else ""
    return (
        body
        + f"\nGATE_SUMMARY: blocking={blocking} warnings={warnings}\n"
    )


# ---------------------------------------------------------------------------
# Prompt and module shape
# ---------------------------------------------------------------------------

def test_negative_feedback_prompt_locked_text() -> None:
    module = _load_gate()
    for fragment in (
        "Identify any deviations",
        "Do not score",
        "Do not approve",
        "blocking = the work cannot ship as complete",
        "warning = work can ship but the deviation is recorded",
    ):
        assert fragment in module.NEGATIVE_FEEDBACK_PROMPT

    for fragment in (
        "GATE_SUMMARY: blocking=<N> warnings=<M>",
        "allowed",
        "non-scope",
        "forbidden-language",
    ):
        assert fragment in module.OUTPUT_FORMAT_INSTRUCTION


def test_request_timeout_is_60_seconds() -> None:
    module = _load_gate()
    assert module.REQUEST_TIMEOUT_SECONDS == 60
    assert module.REQUEST_RETRIES == 1


def test_packet_caps_are_50k_and_200k() -> None:
    module = _load_gate()
    assert module.PER_FILE_CAP_BYTES == 50_000
    assert module.TOTAL_PACKET_CAP_BYTES == 200_000


def test_audit_tools_in_scope_from_v1_1_onward() -> None:
    module = _load_gate()
    assert module.INCLUDE_AUDIT_TOOLS_IN_SCOPE is True


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def test_missing_manifest_is_not_a_hard_fail(gate, monkeypatch) -> None:
    _patch_git(gate, monkeypatch, changed_files=[])

    assert gate.load_manifest("nonexistent_task") is None


def test_manifest_with_mismatched_task_id_fails(gate) -> None:
    _write_manifest(gate, task_id="real_task", task_id_in_body="not_real")
    path = gate.PENDING_MANIFEST_DIR / "real_task.manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["task_id"] = "other_task"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(gate.ManifestVerificationError):
        gate.load_manifest("real_task")


def test_manifest_without_completion_claim_fails(gate) -> None:
    path = gate.PENDING_MANIFEST_DIR / "t.manifest.json"
    path.write_text(json.dumps({"task_id": "t", "completion_claim": ""}), "utf-8")

    with pytest.raises(gate.ManifestVerificationError):
        gate.load_manifest("t")


def test_manifest_with_bad_list_type_fails(gate) -> None:
    path = gate.PENDING_MANIFEST_DIR / "t.manifest.json"
    path.write_text(
        json.dumps(
            {
                "task_id": "t",
                "completion_claim": "claim",
                "files_modified": "not_a_list",
            }
        ),
        "utf-8",
    )

    with pytest.raises(gate.ManifestVerificationError):
        gate.load_manifest("t")


# ---------------------------------------------------------------------------
# Manifest verification cross-check
# ---------------------------------------------------------------------------

def test_manifest_omits_file_git_shows_changed(gate, monkeypatch) -> None:
    _write_manifest(
        gate,
        task_id="omit_task",
        files_modified=["VISION.md"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=["VISION.md", "PROGRESS.md"],
    )

    outcome = gate.run_gate(
        task_id="omit_task",
        completion_claim="trying to ship",
    )

    assert outcome.exit_code == gate.EXIT_MANIFEST_VERIFICATION
    assert "PROGRESS.md" in outcome.message
    assert "manifest omits" in outcome.message.lower() or "coverage-gap" in outcome.message


def test_manifest_claims_modified_but_git_shows_no_change(
    gate, monkeypatch
) -> None:
    (gate.WORKSPACE_ROOT / "fake.md").write_text("hi", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="ghost_task",
        files_modified=["fake.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=[])

    outcome = gate.run_gate(
        task_id="ghost_task",
        completion_claim="trying to ship",
    )

    assert outcome.exit_code == gate.EXIT_MANIFEST_VERIFICATION
    assert "fake.md" in outcome.message


def test_git_ignored_manifest_file_is_kept_in_touched_set(
    gate, monkeypatch
) -> None:
    """Files git ignores but the worker touched should land in the packet."""

    (gate.WORKSPACE_ROOT / "production_state").mkdir()
    ignored_file = gate.WORKSPACE_ROOT / "production_state" / "live.json"
    ignored_file.write_text("{}", encoding="utf-8")

    _write_manifest(
        gate,
        task_id="ignored_task",
        files_modified=["production_state/live.json"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=[],
        ignored={"production_state/live.json"},
    )

    manifest = gate.load_manifest("ignored_task")
    git_summary = gate.collect_git_changed_files()
    gate.verify_manifest(manifest, git_summary)
    touched = gate.build_touched_files_set(manifest, git_summary)
    assert "production_state/live.json" in touched


# ---------------------------------------------------------------------------
# Packet assembly: size cap + coverage
# ---------------------------------------------------------------------------

def test_packet_exceeds_size_cap_fails_with_audit_packet_too_large(
    gate, monkeypatch
) -> None:
    monkeypatch.setattr(gate, "TOTAL_PACKET_CAP_BYTES", 4_096)

    (gate.WORKSPACE_ROOT / "big.md").write_text(
        "Y" * 8_000, encoding="utf-8"
    )
    _write_manifest(
        gate,
        task_id="huge_task",
        files_modified=["big.md"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=["big.md"],
        diff="Y" * 4_000,
    )

    outcome = gate.run_gate(
        task_id="huge_task",
        completion_claim="trying to ship a giant commit",
    )

    assert outcome.exit_code == gate.EXIT_PACKET_TOO_LARGE
    assert "audit_packet_too_large" in outcome.message


def test_touched_file_not_in_packet_is_hard_fail(gate, monkeypatch) -> None:
    """Belt-and-braces: if the assembler ever fails to include a touched
    file, verify_packet_coverage must catch it.
    """

    git_summary = gate.GitChangeSummary(
        changed_files=("VISION.md",),
        diff="diff",
        status=" M VISION.md\n",
    )
    bogus_packet = gate.AuditPacket(
        text="=== empty packet, no section markers ===",
        packet_hash="0" * 64,
        size_bytes=40,
        touched_files=("VISION.md",),
        relevant_contracts=(),
    )
    with pytest.raises(gate.PacketCoverageError) as exc_info:
        gate.verify_packet_coverage(bogus_packet)

    assert "VISION.md" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Clean Grok audit (happy path)
# ---------------------------------------------------------------------------

def test_clean_grok_audit_exits_ok_and_writes_output(
    gate, monkeypatch
) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="clean_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=["PROGRESS.md"],
    )

    monkeypatch.setattr(
        gate,
        "call_grok",
        lambda **_: _clean_grok_response(blocking=0, warnings=0),
    )

    outcome = gate.run_gate(
        task_id="clean_task",
        completion_claim="cleanup pass complete",
    )

    assert outcome.exit_code == gate.EXIT_OK
    assert outcome.audit_output_path is not None
    assert outcome.audit_output_path.exists()
    written = outcome.audit_output_path.read_text(encoding="utf-8")
    assert "Grok Completion Audit" in written
    assert "Packet-SHA256" in written
    assert "blocking=0 warnings=0" in written


def test_blocking_grok_finding_blocks_with_exit_2(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="blocking_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])
    monkeypatch.setattr(
        gate,
        "call_grok",
        lambda **_: (
            "BLOCKING: forbidden phrase appears outside boundary section.\n"
            "WARNING: vocabulary translation list missing one entry.\n"
            "GATE_SUMMARY: blocking=1 warnings=1\n"
        ),
    )

    outcome = gate.run_gate(
        task_id="blocking_task",
        completion_claim="cleanup ready",
    )

    assert outcome.exit_code == gate.EXIT_BLOCKING_DEVIATION
    assert "blocking deviation" in outcome.message.lower()


def test_grok_output_missing_summary_line_fails(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="bad_grok_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])
    monkeypatch.setattr(
        gate,
        "call_grok",
        lambda **_: "I have audited and found nothing. No summary line provided.\n",
    )

    outcome = gate.run_gate(
        task_id="bad_grok_task",
        completion_claim="cleanup ready",
    )

    assert outcome.exit_code == gate.EXIT_GROK_OUTPUT_INVALID
    assert "grok_output_missing_summary" in outcome.message


def test_grok_output_multiple_summary_lines_fails(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="multi_grok_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])
    monkeypatch.setattr(
        gate,
        "call_grok",
        lambda **_: (
            "GATE_SUMMARY: blocking=0 warnings=0\n"
            "Some extra text.\n"
            "GATE_SUMMARY: blocking=1 warnings=0\n"
        ),
    )

    outcome = gate.run_gate(
        task_id="multi_grok_task",
        completion_claim="cleanup ready",
    )

    assert outcome.exit_code == gate.EXIT_GROK_OUTPUT_INVALID
    assert "grok_output_multiple_summaries" in outcome.message


# ---------------------------------------------------------------------------
# Cached audit reuse (packet hash freshness)
# ---------------------------------------------------------------------------

def test_cached_audit_with_matching_packet_hash_is_reused(
    gate, monkeypatch
) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="cache_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    call_count = {"n": 0}

    def counting_call(**_):
        call_count["n"] += 1
        return _clean_grok_response()

    monkeypatch.setattr(gate, "call_grok", counting_call)

    first = gate.run_gate(task_id="cache_task", completion_claim="first run")
    assert first.exit_code == gate.EXIT_OK
    assert call_count["n"] == 1

    second = gate.run_gate(task_id="cache_task", completion_claim="first run")
    assert second.exit_code == gate.EXIT_OK
    assert second.cached is True
    assert call_count["n"] == 1, "second run should have reused cache, not re-called Grok"


def test_audit_output_with_stale_hash_is_not_reused(gate, monkeypatch) -> None:
    """If working tree changes after an audit, the gate must re-run Grok."""

    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("v1\n", encoding="utf-8")
    _write_manifest(gate, task_id="stale_task", files_modified=["PROGRESS.md"])
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    call_count = {"n": 0}

    def counting_call(**_):
        call_count["n"] += 1
        return _clean_grok_response()

    monkeypatch.setattr(gate, "call_grok", counting_call)

    first = gate.run_gate(task_id="stale_task", completion_claim="v1 run")
    assert first.exit_code == gate.EXIT_OK
    assert call_count["n"] == 1
    assert first.cached is False

    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("v2 different\n", encoding="utf-8")

    second = gate.run_gate(task_id="stale_task", completion_claim="v1 run")
    assert second.exit_code == gate.EXIT_OK
    assert second.cached is False
    assert call_count["n"] == 2, (
        "second run must call Grok because packet hash changed"
    )


# ---------------------------------------------------------------------------
# Operator override
# ---------------------------------------------------------------------------

def test_operator_override_creates_warning_drift_incident_and_exits_ok(
    gate, monkeypatch
) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="override_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    def failing_call(**_):  # pragma: no cover - should not be called
        raise AssertionError("Grok must not be called when override is set")

    monkeypatch.setattr(gate, "call_grok", failing_call)

    outcome = gate.run_gate(
        task_id="override_task",
        completion_claim="shipping despite no fresh audit",
        operator_override="Grok endpoint unreachable; Matt approves bypass",
    )

    assert outcome.exit_code == gate.EXIT_OK
    assert len(outcome.drift_incidents) == 1
    incident_path = outcome.drift_incidents[0]
    assert incident_path.exists()
    record = json.loads(incident_path.read_text(encoding="utf-8"))
    assert record["severity"] == "warning"
    assert record["finding_type"] == "operator_override"
    assert "Grok endpoint unreachable" in record["reason"]
    assert record["task_id"] == "override_task"


# ---------------------------------------------------------------------------
# Grok call failure (no override)
# ---------------------------------------------------------------------------

def test_grok_call_failure_without_override_blocks(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="netfail_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    def raise_network(**_):
        raise gate.GrokCallError("grok_call_network_error: simulated")

    monkeypatch.setattr(gate, "call_grok", raise_network)

    outcome = gate.run_gate(
        task_id="netfail_task",
        completion_claim="trying to ship",
    )

    assert outcome.exit_code == gate.EXIT_GROK_CALL_FAILED
    assert "grok_call_network_error" in outcome.message


# ---------------------------------------------------------------------------
# Secret hygiene
# ---------------------------------------------------------------------------

def test_no_xai_key_echoed_to_stdout_or_audit_output(
    gate, monkeypatch, capsys
) -> None:
    secret = "test-secret-never-echo"
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="secret_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    received_key: dict[str, str] = {}

    def capture_call(*, api_key, model, payload):
        received_key["k"] = api_key
        return _clean_grok_response()

    monkeypatch.setattr(gate, "call_grok", capture_call)

    outcome = gate.run_gate(
        task_id="secret_task",
        completion_claim="audit me",
    )

    assert outcome.exit_code == gate.EXIT_OK
    assert received_key["k"] == secret

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err
    assert outcome.audit_output_path is not None
    assert secret not in outcome.audit_output_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Hook scope
# ---------------------------------------------------------------------------

def test_pre_commit_with_no_scoped_files_exits_zero_without_grok(
    gate, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(gate, "_run_git", lambda args: "" if args == [
        "diff", "--cached", "--name-only"
    ] else "")

    def must_not_call(**_):  # pragma: no cover - should not be called
        raise AssertionError("Grok must not be called when scope is empty")

    monkeypatch.setattr(gate, "call_grok", must_not_call)

    rc = gate.main(["--pre-commit"])
    out = capsys.readouterr().out
    assert rc == gate.EXIT_OK
    assert "no staged files in hook scope" in out


def test_scope_matches_core_scoring_directory(gate) -> None:
    assert gate._matches_hook_scope(
        "3. SwarmCommand_Engine/Agent_Loop_Runtime/"
        "Runtime_Implementation/core/scoring/foo.py"
    )


def test_scope_matches_evidence_package_authorized_code_home(gate) -> None:
    # The §18.3 authorized code home must be in hook scope so the gate fires
    # on it and --pre-commit mode cannot false-pass it (loop-review Fix B).
    assert gate._matches_hook_scope(
        "3. SwarmCommand_Engine/Agent_Loop_Runtime/"
        "Runtime_Implementation/core/evidence_package/audit_packet.py"
    ) is True


def test_scope_matches_audit_tools_from_v1_1_onward(gate) -> None:
    assert gate._matches_hook_scope("audit_tools/complete_gate.py") is True
    assert gate._matches_hook_scope("audit_tools/grok_audit_runner.py") is True
    # Path outside audit_tools/ must still be evaluated by its own rules.
    assert gate._matches_hook_scope("random_other_dir/file.py") is False


def test_scope_matches_signed_spec_only(gate, monkeypatch) -> None:
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()

    signed = spec_dir / "Signed_Spec_Deep_Dive.md"
    signed.write_text(
        "# Signed Spec\n\n**Status:** §11 SIGNED 2026-05-25 by Matt\n",
        encoding="utf-8",
    )

    draft = spec_dir / "Draft_Deep_Dive.md"
    draft.write_text(
        "# Draft\n\n**Status:** DRAFT pre-§11.\n",
        encoding="utf-8",
    )

    assert gate._matches_hook_scope("4. Product_Roadmap/Signed_Spec_Deep_Dive.md") is True
    assert gate._matches_hook_scope("4. Product_Roadmap/Draft_Deep_Dive.md") is False


# ---------------------------------------------------------------------------
# Bootstrap exception sanity
# ---------------------------------------------------------------------------

def test_bootstrap_exception_documented_in_module_docstring() -> None:
    module = _load_gate()
    assert module.__doc__ is not None
    assert "Bootstrap exception" in module.__doc__
    assert "operator-authorized" in module.__doc__


# ---------------------------------------------------------------------------
# CLI argument plumbing
# ---------------------------------------------------------------------------

def test_main_requires_task_and_claim_when_not_pre_commit(
    gate, capsys
) -> None:
    rc = gate.main([])
    assert rc == gate.EXIT_USAGE


# ---------------------------------------------------------------------------
# Pre-commit staged-only audit (fix #1)
# ---------------------------------------------------------------------------

def test_pre_commit_mode_audits_staged_set_not_unstaged(gate, monkeypatch) -> None:
    """An unstaged worktree edit must not leak into the pre-commit audit."""

    (gate.WORKSPACE_ROOT / "staged.md").write_text("staged content\n", encoding="utf-8")
    (gate.WORKSPACE_ROOT / "unstaged.md").write_text("unstaged content\n", encoding="utf-8")

    # Hook scope is hit via a fake signed spec so the pre-commit path
    # actually fires the full gate.
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    spec = spec_dir / "Signed_Spec_Deep_Dive.md"
    spec.write_text(
        "# Signed Spec\n\n**Status:** §11 SIGNED 2026-05-25 by Matt\n",
        encoding="utf-8",
    )

    _write_manifest(
        gate,
        task_id="pre_commit",
        files_modified=["4. Product_Roadmap/Signed_Spec_Deep_Dive.md"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=[
            "4. Product_Roadmap/Signed_Spec_Deep_Dive.md",
            "unstaged.md",
        ],
        staged_files=["4. Product_Roadmap/Signed_Spec_Deep_Dive.md"],
    )

    captured_payload: dict[str, str] = {}

    def capture_call(*, api_key, model, payload):
        captured_payload["p"] = payload
        return _clean_grok_response()

    monkeypatch.setattr(gate, "call_grok", capture_call)

    rc = gate.main(["--pre-commit"])
    assert rc == gate.EXIT_OK

    packet = captured_payload["p"]
    assert "Signed_Spec_Deep_Dive.md" in packet
    assert "unstaged.md" not in packet, (
        "unstaged worktree edits must not leak into a pre-commit audit"
    )


def test_pre_commit_manifest_must_match_staged_not_worktree(
    gate, monkeypatch
) -> None:
    """If the manifest omits a *staged* file, the pre-commit gate must fail
    even if the manifest matches the wider worktree."""

    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    spec = spec_dir / "Signed_Spec_Deep_Dive.md"
    spec.write_text(
        "# Signed Spec\n\n**Status:** §11 SIGNED 2026-05-25 by Matt\n",
        encoding="utf-8",
    )
    other = spec_dir / "Other_Deep_Dive.md"
    other.write_text(
        "# Other\n\n**Status:** §11 SIGNED 2026-05-25 by Matt\n",
        encoding="utf-8",
    )

    _write_manifest(
        gate,
        task_id="pre_commit",
        files_modified=["4. Product_Roadmap/Other_Deep_Dive.md"],
    )
    _patch_git(
        gate,
        monkeypatch,
        changed_files=["4. Product_Roadmap/Other_Deep_Dive.md"],
        staged_files=[
            "4. Product_Roadmap/Signed_Spec_Deep_Dive.md",
            "4. Product_Roadmap/Other_Deep_Dive.md",
        ],
    )

    rc = gate.main(["--pre-commit"])
    assert rc == gate.EXIT_MANIFEST_VERIFICATION


# ---------------------------------------------------------------------------
# Referenced-contract hard-fails (fix #3)
# ---------------------------------------------------------------------------

def test_referenced_contract_missing_is_hard_fail(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="missing_contract_task",
        files_modified=["PROGRESS.md"],
        relevant_contracts=["4. Product_Roadmap/Does_Not_Exist_Deep_Dive.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    outcome = gate.run_gate(
        task_id="missing_contract_task",
        completion_claim="ship",
    )

    assert outcome.exit_code == gate.EXIT_MANIFEST_VERIFICATION
    assert "do not exist on disk" in outcome.message
    assert "Does_Not_Exist_Deep_Dive.md" in outcome.message


def test_referenced_contract_unsigned_is_hard_fail(gate, monkeypatch) -> None:
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    draft = spec_dir / "Draft_Deep_Dive.md"
    draft.write_text(
        "# Draft Spec\n\n**Status:** DRAFT pre-§11.\n",
        encoding="utf-8",
    )

    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="unsigned_contract_task",
        files_modified=["PROGRESS.md"],
        relevant_contracts=["4. Product_Roadmap/Draft_Deep_Dive.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    outcome = gate.run_gate(
        task_id="unsigned_contract_task",
        completion_claim="ship",
    )

    assert outcome.exit_code == gate.EXIT_MANIFEST_VERIFICATION
    assert "not §11-signed" in outcome.message
    assert "Draft_Deep_Dive.md" in outcome.message


def test_referenced_contract_signed_is_accepted(gate, monkeypatch) -> None:
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    signed = spec_dir / "Signed_Deep_Dive.md"
    signed.write_text(
        "# Signed Spec\n\n**Status:** §11 SIGNED 2026-05-25 by Matt\n"
        "\n## §11 Done Criteria\n\n1. Test it.\n",
        encoding="utf-8",
    )

    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="signed_contract_task",
        files_modified=["PROGRESS.md"],
        relevant_contracts=["4. Product_Roadmap/Signed_Deep_Dive.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])

    captured: dict[str, str] = {}

    def capture(*, api_key, model, payload):
        captured["p"] = payload
        return _clean_grok_response()

    monkeypatch.setattr(gate, "call_grok", capture)

    outcome = gate.run_gate(
        task_id="signed_contract_task",
        completion_claim="ship",
    )

    assert outcome.exit_code == gate.EXIT_OK
    assert "Signed_Deep_Dive.md" in captured["p"]
    assert "§11 Done Criteria" in captured["p"]


# ---------------------------------------------------------------------------
# Scope boundary extraction (fix #2)
# ---------------------------------------------------------------------------

def test_scope_boundary_extracted_verbatim_from_deep_dive(
    gate, monkeypatch
) -> None:
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    exact_quote = (
        '> *"This package covers NorthStar Inbox Shield\'s email-fraud and '
        "inbox-layer MDR control surface only. Other controls in your "
        "security stack — including MFA, EDR, backups, incident response "
        "plans, and patch management — are not in this package's scope "
        "and must be evidenced by your MSP or other vendors. This package "
        "does not guarantee underwriting approval or premium reduction; "
        "it provides auditable evidence of one control surface for your "
        'underwriter\'s review."*'
    )
    spec_path = spec_dir / "Cyber_Insurance_Evidence_Package_Deep_Dive.md"
    spec_path.write_text(
        "# Header\n\n"
        "## §2 Scope\n\n"
        "### Required boundary statement (printed in the generated package)\n\n"
        f"{exact_quote}\n\n"
        "This statement is part of the contract. Removing it is a drift "
        "incident.\n\n"
        "---\n\n"
        "## §3 Buyer Chain\n",
        encoding="utf-8",
    )

    extracted = gate.extract_scope_boundary()
    assert exact_quote in extracted
    assert "Required boundary statement" in extracted
    assert "## §3" not in extracted, "extraction must stop at next section"


def test_scope_boundary_missing_file_surfaces_sentinel(gate) -> None:
    extracted = gate.extract_scope_boundary()
    assert extracted.startswith("<scope-boundary"), (
        "missing deep-dive must surface a clearly-marked sentinel so Grok "
        "raises it as a blocking deviation"
    )
    assert "not found" in extracted


def test_scope_boundary_missing_anchor_surfaces_sentinel(gate) -> None:
    spec_dir = gate.WORKSPACE_ROOT / "4. Product_Roadmap"
    spec_dir.mkdir()
    spec_path = spec_dir / "Cyber_Insurance_Evidence_Package_Deep_Dive.md"
    spec_path.write_text("# Header\n\nNo anchor here.\n", encoding="utf-8")

    extracted = gate.extract_scope_boundary()
    assert "not found" in extracted
    assert "drifted" in extracted


# ---------------------------------------------------------------------------
# Byte-honest truncation (fix #4)
# ---------------------------------------------------------------------------

def test_truncate_to_byte_cap_respects_byte_boundary_for_multibyte_text(
    gate,
) -> None:
    # U+00E9 ("LATIN SMALL LETTER E WITH ACUTE") is 2 UTF-8 bytes.
    # A 1,000-char string is 2,000 bytes. With a 5-byte cap, char-slicing
    # would yield 10 bytes — the byte cap must produce <= 5 bytes.
    e_acute = "\u00e9"
    assert len(e_acute.encode("utf-8")) == 2

    multibyte = e_acute * 1_000
    truncated = gate._truncate_to_byte_cap(multibyte, cap_bytes=5)
    body, _, _ = truncated.partition(gate.TRUNCATION_MARKER)
    assert len(body.encode("utf-8")) <= 5
    assert truncated.endswith(gate.TRUNCATION_MARKER)


def test_truncate_to_byte_cap_drops_partial_codepoint_at_boundary(gate) -> None:
    # Build "h" + é (U+00E9, 2 UTF-8 bytes) + "llo" explicitly so the
    # source-file encoding cannot affect what's being tested. Total
    # bytes: 1 + 2 + 3 = 6. cap_bytes=2 leaves only the first byte of
    # é, which `errors='ignore'` must drop entirely (no U+FFFD).
    text = "h" + "\u00e9" + "llo"
    raw = text.encode("utf-8")
    assert raw == b"h\xc3\xa9llo"

    truncated = gate._truncate_to_byte_cap(text, cap_bytes=2)
    body, _, _ = truncated.partition(gate.TRUNCATION_MARKER)
    assert body == "h"
    assert "\ufffd" not in body, (
        "errors='ignore' must drop the partial codepoint, not replace it"
    )
    body.encode("utf-8")


def test_truncate_to_byte_cap_keeps_complete_codepoint_at_boundary(gate) -> None:
    # cap_bytes=3 retains the complete é (h=1, é=2 → 3 bytes total).
    text = "h" + "\u00e9" + "llo"
    truncated = gate._truncate_to_byte_cap(text, cap_bytes=3)
    body, _, _ = truncated.partition(gate.TRUNCATION_MARKER)
    assert body == "h\u00e9"


def test_truncate_to_byte_cap_passes_through_when_under_cap(gate) -> None:
    short = "hello world"
    assert gate._truncate_to_byte_cap(short, cap_bytes=4_096) == short
    assert gate.TRUNCATION_MARKER not in gate._truncate_to_byte_cap(
        short, cap_bytes=4_096
    )


# ---------------------------------------------------------------------------
# CLI argument plumbing
# ---------------------------------------------------------------------------

def test_main_propagates_outcome_exit_code(gate, monkeypatch) -> None:
    (gate.WORKSPACE_ROOT / "PROGRESS.md").write_text("progress\n", encoding="utf-8")
    _write_manifest(
        gate,
        task_id="cli_task",
        files_modified=["PROGRESS.md"],
    )
    _patch_git(gate, monkeypatch, changed_files=["PROGRESS.md"])
    monkeypatch.setattr(
        gate,
        "call_grok",
        lambda **_: (
            "BLOCKING: simulated finding.\n"
            "GATE_SUMMARY: blocking=1 warnings=0\n"
        ),
    )

    rc = gate.main([
        "--task", "cli_task",
        "--claim", "cli invocation",
    ])
    assert rc == gate.EXIT_BLOCKING_DEVIATION
