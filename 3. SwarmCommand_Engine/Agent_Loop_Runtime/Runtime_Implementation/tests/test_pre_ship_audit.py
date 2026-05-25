from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_runner():
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "pre_ship_audit.py"
    )
    spec = importlib.util.spec_from_file_location("pre_ship_audit", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _report(verdict: str) -> str:
    return f"""A. Plan alignment
On plan.

B. Signed spec compliance
Fine.

C. Security and boundary risks
None observed.

D. Test coverage
Adequate.

E. Drift and scope creep
None.

F. Verdict
VERDICT: {verdict}
One paragraph explanation.
"""


def _dummy_change_summary():
    return {
        "diff": "diff content",
        "status": " M file.md\n",
        "untracked": [],
        "changed_files": ["file.md"],
    }


def _safe_change_summary(diff: str = "diff content"):
    return {
        "diff": diff,
        "status": " M file.md\n",
        "untracked": [],
        "changed_files": ["file.md"],
    }


def test_prompt_contains_required_headings_and_verdict_lines() -> None:
    runner = _load_runner()

    for heading in (
        "A. Plan alignment",
        "B. Signed spec compliance",
        "C. Security and boundary risks",
        "D. Test coverage",
        "E. Drift and scope creep",
        "F. Verdict",
    ):
        assert heading in runner.PROMPT

    for verdict_line in ("VERDICT: SHIP", "VERDICT: FIX_FIRST", "VERDICT: STOP"):
        assert verdict_line in runner.PROMPT


@pytest.mark.parametrize("verdict", ["SHIP", "FIX_FIRST", "STOP"])
def test_verdict_parser_accepts_closed_enum(verdict: str) -> None:
    runner = _load_runner()
    assert runner.extract_verdict(_report(verdict)) == verdict


def test_verdict_parser_rejects_unknown() -> None:
    runner = _load_runner()
    with pytest.raises(SystemExit):
        runner.extract_verdict(_report("MAYBE"))


def test_verdict_parser_rejects_multiple_lines() -> None:
    runner = _load_runner()
    bad = _report("SHIP") + "\nVERDICT: STOP\n"
    with pytest.raises(SystemExit):
        runner.extract_verdict(bad)


def test_ship_exits_zero(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(runner, "_collect_change_summary", _dummy_change_summary)
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "state")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("SHIP"))

    assert runner.main([]) == 0


def test_fix_first_exits_blocking(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(runner, "_collect_change_summary", _dummy_change_summary)
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "state")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("FIX_FIRST"))

    assert runner.main([]) == 2


def test_stop_exits_blocking(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(runner, "_collect_change_summary", _dummy_change_summary)
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "state")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("STOP"))

    assert runner.main([]) == 3


def test_report_only_returns_zero_on_block(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(runner, "_collect_change_summary", _dummy_change_summary)
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "state")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("STOP"))

    assert runner.main(["--report-only"]) == 0


def test_no_pending_changes_exits_zero(monkeypatch) -> None:
    runner = _load_runner()
    monkeypatch.setattr(
        runner,
        "_collect_change_summary",
        lambda: {"diff": "", "status": "", "untracked": [], "changed_files": []},
    )
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])

    assert runner.main([]) == 0


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        ".env.local",
        "tenant.sqlite",
        "tenant.sqlite3",
        "tenant.db",
        "audit_outputs/decision_audits/private_report.md",
    ],
)
def test_preflight_blocks_risky_pending_paths(path: str) -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="risky file"):
        runner.preflight_data_leak_check(
            {
                "diff": "",
                "status": f"?? {path}\n",
                "untracked": [],
                "changed_files": [path],
            }
        )


@pytest.mark.parametrize(
    "content",
    [
        "-----BEGIN " + "PRIVATE KEY-----",
        "YOUR_" + "GITHUB_PAT_HERE",
        "gho_" + "a" * 24,
        "XAI_API_KEY=" + "xai-" + "a" * 24,
    ],
)
def test_preflight_blocks_secret_like_content(content: str) -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="secret-like marker"):
        runner.preflight_data_leak_check(_safe_change_summary(diff=content))


def test_preflight_allows_harmless_secret_variable_references() -> None:
    runner = _load_runner()

    runner.preflight_data_leak_check(
        _safe_change_summary(
            diff=(
                'if normalized_key == "XAI_API_KEY":\n'
                'env.write_text("XAI_API_KEY=test-secret\\n")\n'
            )
        )
    )


def test_no_secret_echoed_to_stdout_or_report(tmp_path, monkeypatch, capsys) -> None:
    runner = _load_runner()
    secret = "test-secret-never-echo"
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text(f"XAI_API_KEY={secret}\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "out")
    monkeypatch.setattr(runner, "_collect_change_summary", _dummy_change_summary)
    monkeypatch.setattr(runner, "_collect_project_state", lambda: "state")
    monkeypatch.setattr(runner, "_signed_specs", lambda: [])

    def fake_call(**kwargs):
        assert kwargs["api_key"] == secret
        return _report("SHIP")

    monkeypatch.setattr(runner, "call_grok", fake_call)

    assert runner.main([]) == 0

    captured = capsys.readouterr()
    reports = list((tmp_path / "out").glob("*.md"))
    assert len(reports) == 1
    assert secret not in captured.out
    assert secret not in captured.err
    assert secret not in reports[0].read_text(encoding="utf-8")


def test_no_core_runtime_module_imports_pre_ship_audit() -> None:
    workspace_root = Path(__file__).resolve().parents[4]
    core_root = (
        workspace_root
        / "3. SwarmCommand_Engine"
        / "Agent_Loop_Runtime"
        / "Runtime_Implementation"
        / "core"
    )
    offenders = [
        path
        for path in core_root.rglob("*.py")
        if "pre_ship_audit" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
