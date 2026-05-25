from __future__ import annotations

import importlib.util
import sys
import urllib.error
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_runner():
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "decision_audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("decision_audit_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_packet() -> str:
    return """# Decision Audit Packet - Test

## 1. Decision Under Review
Choose the next build lane.

## 2. Primary Recommendation
Build the Independent Decision Auditor now.

## 3. Rationale Given
The project needs an anti-drift check before more strategic recommendations.

## 4. Rejected Alternatives
Defer the auditor, or build another detector first.

## 5. Current Project State
Tiered Detection Intensity is implemented and tested; see PROGRESS.md.

## 6. Constraints / Guardrails
No secrets, no raw client data, and no product-runtime imports.
"""


def _report(verdict: str) -> str:
    return f"""A. Recommendation clarity
Clear.

B. Fit to current project state
Fits.

C. Missing alternatives or assumptions
None.

D. Drift / bias risk
Low.

E. Cost, timing, and opportunity cost
Small.

F. Verdict
VERDICT: {verdict}
Proceed with the stated caution.
"""


def test_prompt_lock_contains_required_output_contract() -> None:
    runner = _load_runner()

    for heading in (
        "A. Recommendation clarity",
        "B. Fit to current project state",
        "C. Missing alternatives or assumptions",
        "D. Drift / bias risk",
        "E. Cost, timing, and opportunity cost",
        "F. Verdict",
    ):
        assert heading in runner.DECISION_AUDITOR_PROMPT
    assert (
        "VERDICT: proceed | proceed_with_notes | revise_before_proceeding | "
        "defer | operator_decision_required"
    ) in runner.DECISION_AUDITOR_PROMPT


def test_missing_required_section_fails_before_network_call() -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="missing required section"):
        runner.validate_decision_packet(
            _valid_packet().replace("## 4. Rejected Alternatives", "## 4. Other")
        )


def test_valid_packet_passes_validation() -> None:
    runner = _load_runner()

    runner.validate_decision_packet(_valid_packet())


@pytest.mark.parametrize(
    "marker",
    ["XAI_API_KEY", "BEGIN PRIVATE KEY", "gho_", "YOUR_GITHUB_PAT_HERE"],
)
def test_forbidden_secret_markers_fail_before_network_call(marker: str) -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="forbidden secret marker"):
        runner.validate_decision_packet(_valid_packet() + f"\n{marker}=redacted")


@pytest.mark.parametrize(
    "raw_financial_text",
    ["routing number: 123456789", "account: 123456789012", "123456789/123456789012"],
)
def test_raw_financial_patterns_fail_before_network_call(raw_financial_text: str) -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="raw financial"):
        runner.validate_decision_packet(_valid_packet() + "\n" + raw_financial_text)


def test_output_path_is_confined_and_sanitized(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    output_dir = tmp_path / "audit_outputs" / "decision_audits"
    monkeypatch.setattr(runner, "OUTPUT_DIR", output_dir)

    report_path = runner.write_decision_audit_report(
        packet_path=Path("../../escape packet.md"),
        model="grok-4",
        content=_report("proceed"),
    )

    assert output_dir.resolve() in report_path.resolve().parents
    assert report_path.name.startswith("escape_packet_decision_audit_")


@pytest.mark.parametrize(
    "verdict",
    [
        "proceed",
        "proceed_with_notes",
        "revise_before_proceeding",
        "defer",
        "operator_decision_required",
    ],
)
def test_verdict_parser_accepts_closed_enum_only(verdict: str) -> None:
    runner = _load_runner()

    assert runner.extract_verdict(_report(verdict)) == verdict


def test_verdict_parser_rejects_unknown_verdict() -> None:
    runner = _load_runner()

    with pytest.raises(SystemExit, match="unknown decision-audit verdict"):
        runner.extract_verdict(_report("approve"))


def test_fail_closed_verdicts_exit_nonzero(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    packet = tmp_path / "packet.md"
    packet.write_text(_valid_packet(), encoding="utf-8")
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "reports")
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("defer"))

    assert runner.main([str(packet)]) == 2


def test_proceed_verdicts_exit_zero(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    packet = tmp_path / "packet.md"
    packet.write_text(_valid_packet(), encoding="utf-8")
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "reports")
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("proceed_with_notes"))

    assert runner.main([str(packet)]) == 0


def test_report_only_override_returns_zero_for_blocking_verdict(tmp_path, monkeypatch, capsys) -> None:
    runner = _load_runner()
    packet = tmp_path / "packet.md"
    packet.write_text(_valid_packet(), encoding="utf-8")
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "reports")
    monkeypatch.setattr(
        runner, "call_grok", lambda **_: _report("operator_decision_required")
    )

    assert runner.main([str(packet), "--report-only"]) == 0
    assert "Report-only mode: blocking verdict" in capsys.readouterr().out


def test_no_secret_echo_to_stdout_stderr_or_report(tmp_path, monkeypatch, capsys) -> None:
    runner = _load_runner()
    packet = tmp_path / "packet.md"
    packet.write_text(_valid_packet(), encoding="utf-8")
    monkeypatch.setattr(runner, "ENV_PATH", tmp_path / ".env")
    secret = "test-secret-never-echo"
    runner.ENV_PATH.write_text(f"XAI_API_KEY={secret}\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", tmp_path / "reports")

    def fake_call_grok(**kwargs):
        assert kwargs["api_key"] == secret
        return _report("proceed")

    monkeypatch.setattr(runner, "call_grok", fake_call_grok)

    assert runner.main([str(packet)]) == 0
    captured = capsys.readouterr()
    reports = list((tmp_path / "reports").glob("*.md"))
    assert len(reports) == 1
    assert secret not in captured.out
    assert secret not in captured.err
    assert secret not in reports[0].read_text(encoding="utf-8")


def test_no_core_runtime_module_imports_decision_audit_runner() -> None:
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
        if "decision_audit_runner" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_runner_does_not_write_blackboard_or_state() -> None:
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "decision_audit_runner.py"
    )
    source = runner_path.read_text(encoding="utf-8")

    assert "submit_" not in source
    assert "write_records" not in source
    assert "append_operator_audit_entry" not in source
    assert "save_tenant_profile_state" not in source
    assert "production_state" not in source
    assert "blackboard" not in source.lower()


def test_tracker_paths_are_allowed_but_runner_does_not_mutate_trackers() -> None:
    runner = _load_runner()
    packet = _valid_packet() + "\nReferences: PROGRESS.md and PROJECT_ACTIVITY_LOG.md\n"
    runner_path = (
        Path(__file__).resolve().parents[4]
        / "audit_tools"
        / "decision_audit_runner.py"
    )
    source = runner_path.read_text(encoding="utf-8")

    runner.validate_decision_packet(packet)
    assert "PROGRESS.md" not in source
    assert "PROJECT_ACTIVITY_LOG.md" not in source


def test_windows_paths_with_spaces_are_accepted(tmp_path, monkeypatch) -> None:
    runner = _load_runner()
    spaced_root = tmp_path / "Root With Spaces"
    packet = spaced_root / "decision_audit_inputs" / "packet with spaces.md"
    packet.parent.mkdir(parents=True)
    packet.write_text(_valid_packet(), encoding="utf-8")
    monkeypatch.setattr(runner, "ENV_PATH", spaced_root / ".env")
    runner.ENV_PATH.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")
    monkeypatch.setattr(runner, "OUTPUT_DIR", spaced_root / "audit_outputs" / "decision_audits")
    monkeypatch.setattr(runner, "call_grok", lambda **_: _report("proceed"))

    assert runner.main([str(packet)]) == 0


def test_missing_model_falls_back_to_grok_4(tmp_path) -> None:
    runner = _load_runner()
    env_path = tmp_path / ".env"
    env_path.write_text("XAI_API_KEY=test-secret\n", encoding="utf-8")

    assert runner.load_xai_key(env_path) == ("test-secret", "grok-4")


def test_http_errors_are_redacted(monkeypatch) -> None:
    runner = _load_runner()

    def fail_urlopen(*_, **__):
        raise urllib.error.HTTPError(
            url=runner.XAI_ENDPOINT,
            code=401,
            msg="Unauthorized",
            hdrs={"Authorization": "Bearer test-secret-never-echo"},
            fp=None,
        )

    monkeypatch.setattr(runner.urllib.request, "urlopen", fail_urlopen)

    with pytest.raises(SystemExit) as exc_info:
        runner.call_grok(
            api_key="test-secret-never-echo",
            model="grok-4",
            prompt=runner.DECISION_AUDITOR_PROMPT,
            decision_packet=_valid_packet(),
        )

    message = str(exc_info.value)
    assert "401" in message
    assert "test-secret-never-echo" not in message
    assert "Authorization" not in message


def test_decision_packet_template_exists_and_validates() -> None:
    runner = _load_runner()
    template_path = Path(__file__).resolve().parents[4] / "decision_audit_inputs" / "TEMPLATE.md"

    assert template_path.exists()
    runner.validate_decision_packet(template_path.read_text(encoding="utf-8"))


def test_grok_audit_runner_still_imports_and_has_existing_targets() -> None:
    runner_path = Path(__file__).resolve().parents[4] / "audit_tools" / "grok_audit_runner.py"
    spec = importlib.util.spec_from_file_location("grok_audit_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    assert {"vendor_baseline", "financial_state_ledger", "tiered_detection_intensity"} <= set(
        module.AUDIT_PACKAGES
    )


def test_self_audit_packet_exists_for_decision_auditor_next() -> None:
    runner = _load_runner()
    packet_path = (
        Path(__file__).resolve().parents[4]
        / "decision_audit_inputs"
        / "20260524_1741_decision_auditor_next.md"
    )

    assert packet_path.exists()
    text = packet_path.read_text(encoding="utf-8")
    assert "Decision Auditor next" in text
    runner.validate_decision_packet(text)
