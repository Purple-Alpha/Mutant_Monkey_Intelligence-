from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_module(module_name: str, path: Path):
    audit_tools = _workspace_root() / "audit_tools"
    if str(audit_tools) not in sys.path:
        sys.path.insert(0, str(audit_tools))
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_review_ledger():
    return _load_module("review_ledger", _workspace_root() / "audit_tools" / "review_ledger.py")


def _load_scanner():
    return _load_module(
        "score_sheet_review_scanner",
        _workspace_root() / "audit_tools" / "score_sheet_review_scanner.py",
    )


def _candidate_row(**overrides):
    row = {
        "record_type": "candidate",
        "candidate_ref": "packet-001#1",
        "event_id": None,
        "event_date": "2026-06-03",
        "track": "audit_gate",
        "event_type": "fail",
        "source_artifact": "audit_outputs/example.md",
        "test_or_check_name": "example_check",
        "pass_fail": "fail",
        "failure_type": "expectation_contract",
        "finding_summary": "Example finding.",
        "corrective_action": "",
        "retest_reference": "",
        "recorded_by": "tool_candidate",
        "notes": "",
    }
    row.update(overrides)
    return row


def _write_packet(
    directory: Path,
    *,
    name: str = "packet-001.candidate.jsonl",
    emitted_at: str = "2026-06-03T00:00:00+00:00",
    rows: list[dict] | None = None,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    header = {
        "record_type": "packet_header",
        "candidate_packet_id": name.removesuffix(".candidate.jsonl"),
        "emitter": "pre_ship_audit.py",
        "emitted_at": emitted_at,
        "status": "AI-drafted",
        "promotion_status": "not_reviewed",
    }
    packet_rows = rows if rows is not None else [_candidate_row()]
    path.write_text(
        "\n".join(json.dumps(line) for line in [header, *packet_rows]) + "\n",
        encoding="utf-8",
    )
    return path


def test_list_ignores_promoted_and_rejected_packets(tmp_path, capsys):
    review = _load_review_ledger()
    root = tmp_path / "candidates"
    active = _write_packet(root, name="active.candidate.jsonl")
    _write_packet(root / "promoted", name="promoted.candidate.jsonl")
    _write_packet(root / "rejected", name="rejected.candidate.jsonl")

    assert review.main(["--candidate-dir", str(root), "list"]) == 0
    output = capsys.readouterr().out
    assert str(active.name) in output
    assert "promoted.candidate.jsonl" not in output
    assert "rejected.candidate.jsonl" not in output


def test_inspect_parses_valid_packet_and_malformed_header_fails(tmp_path, capsys):
    review = _load_review_ledger()
    packet = _write_packet(tmp_path)

    assert review.main(["inspect", str(packet)]) == 0
    output = capsys.readouterr().out
    assert "rows=1" in output
    assert "packet_id=packet-001" in output

    malformed = tmp_path / "bad.candidate.jsonl"
    malformed.write_text(json.dumps({"record_type": "candidate"}) + "\n", encoding="utf-8")
    assert review.main(["inspect", str(malformed)]) == 2


def test_check_blocks_draft_when_scanner_block_findings_exist(tmp_path, capsys):
    review = _load_review_ledger()
    packet = _write_packet(
        tmp_path,
        rows=[_candidate_row(finding_summary="XAI_API_KEY=xai-" + "a" * 24)],
    )

    assert review.main(["check", str(packet)]) == 1
    output = capsys.readouterr().out
    assert "BLOCK secret" in output
    assert "xai-" + "a" * 24 not in output


def test_check_blocks_candidate_with_canonical_event_id(tmp_path, capsys):
    review = _load_review_ledger()
    packet = _write_packet(tmp_path, rows=[_candidate_row(event_id="TE-20260603-audit_gate-0001")])

    assert review.main(["check", str(packet)]) == 1
    output = capsys.readouterr().out
    assert "event_id_laundering" in output


def test_draft_emits_operator_placeholders_and_noncanonical_marker(tmp_path, capsys):
    review = _load_review_ledger()
    packet = _write_packet(tmp_path)

    assert review.main(["draft", str(packet), "--row", "1"]) == 0
    output = capsys.readouterr().out
    assert "OPERATOR_TO_ASSIGN" in output
    assert "OPERATOR_TO_SET" in output
    assert "DRAFT_NOT_CANONICAL" in output
    assert "candidate_packet_id=packet-001" in output


def test_draft_parser_has_no_out_flag():
    review = _load_review_ledger()
    help_text = review.build_parser().format_help()
    assert "--out" not in help_text


def test_draft_writes_nothing_to_disk(tmp_path):
    review = _load_review_ledger()
    packet = _write_packet(tmp_path)
    before = sorted(path.name for path in tmp_path.iterdir())

    assert review.main(["draft", str(packet), "--row", "1"]) == 0
    after = sorted(path.name for path in tmp_path.iterdir())
    assert after == before


def test_scanner_does_not_echo_secret_or_raw_financial_value():
    scanner = _load_scanner()
    secret = "ghp_" + "b" * 24
    account = "account number 123456789012"

    findings = scanner.scan_text(
        f"{secret} and {account}",
        path="audit_outputs/score_sheet_candidates/example.candidate.jsonl",
        field="finding_summary",
    )
    formatted = scanner.format_findings(findings)
    assert scanner.has_blocking_findings(findings)
    assert secret not in formatted
    assert "123456789012" not in formatted
    assert "BLOCK" in formatted


def test_scanner_allows_placeholders_and_example_domains():
    scanner = _load_scanner()
    findings = scanner.scan_text(
        "Contact reviewer@example.com with ACCOUNT_PLACEHOLDER and XAI_API_KEY=test-secret",
        path="example",
        field="notes",
    )
    assert findings == []


def test_shared_scanner_is_only_pattern_source_for_helper_and_hook():
    root = _workspace_root()
    helper_text = (root / "audit_tools" / "review_ledger.py").read_text(encoding="utf-8")
    hook_text = (root / "Internal_Tools" / "precommit_score_sheet_safety_hook.sh").read_text(
        encoding="utf-8"
    )

    assert "score_sheet_review_scanner" in helper_text
    assert "score_sheet_review_scanner.py" in hook_text
    assert "UNSAFE_PATTERNS" not in hook_text
    assert "PRIVATE KEY" not in hook_text


def test_score_sheet_safety_hook_blocks_staged_fake_secret(tmp_path):
    root = _workspace_root()
    if shutil.which("git") is None:
        return
    repo = tmp_path / "repo"
    shutil.copytree(root / "audit_tools", repo / "audit_tools")
    (repo / "Internal_Tools").mkdir()
    shutil.copy2(
        root / "Internal_Tools" / "precommit_score_sheet_safety_hook.sh",
        repo / "Internal_Tools" / "precommit_score_sheet_safety_hook.sh",
    )
    (repo / "PROJECT_ACTIVITY_LOG.md").write_text(
        "XAI_API_KEY=xai-" + "c" * 24 + "\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "PROJECT_ACTIVITY_LOG.md"], cwd=repo, check=True)
    result = subprocess.run(
        ["bash", "Internal_Tools/precommit_score_sheet_safety_hook.sh"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "BLOCK secret" in result.stdout
    assert "xai-" + "c" * 24 not in result.stdout


def test_score_sheet_safety_hook_does_not_scan_unstaged_files(tmp_path):
    root = _workspace_root()
    if shutil.which("git") is None:
        return
    repo = tmp_path / "repo"
    shutil.copytree(root / "audit_tools", repo / "audit_tools")
    (repo / "Internal_Tools").mkdir()
    shutil.copy2(
        root / "Internal_Tools" / "precommit_score_sheet_safety_hook.sh",
        repo / "Internal_Tools" / "precommit_score_sheet_safety_hook.sh",
    )
    (repo / "PROJECT_ACTIVITY_LOG.md").write_text(
        "XAI_API_KEY=xai-" + "d" * 24 + "\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    result = subprocess.run(
        ["bash", "Internal_Tools/precommit_score_sheet_safety_hook.sh"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0


def test_stale_flags_old_packets_without_mutating(tmp_path, capsys):
    review = _load_review_ledger()
    old = _write_packet(tmp_path, name="old.candidate.jsonl", emitted_at="2026-01-01T00:00:00+00:00")
    before = old.read_text(encoding="utf-8")

    assert review.main(["--candidate-dir", str(tmp_path), "stale"]) == 0
    output = capsys.readouterr().out
    assert "STALE_REVIEW_NEEDED" in output
    assert old.read_text(encoding="utf-8") == before


def test_no_command_moves_deletes_or_rewrites_packets(tmp_path):
    review = _load_review_ledger()
    packet = _write_packet(tmp_path)
    before = packet.read_text(encoding="utf-8")

    for command in (["inspect", str(packet)], ["check", str(packet)], ["draft", str(packet), "--row", "1"]):
        assert review.main(command) == 0
        assert packet.exists()
        assert packet.read_text(encoding="utf-8") == before


def test_review_ledger_does_not_import_pre_ship_audit():
    root = _workspace_root()
    text = (root / "audit_tools" / "review_ledger.py").read_text(encoding="utf-8")
    assert "pre_ship_audit" not in text


def test_stale_threshold_default_is_60_days():
    review = _load_review_ledger()
    assert review.STALE_THRESHOLD_DAYS == 60


def test_cli_commands_are_closed_to_wave31_surface():
    review = _load_review_ledger()
    parser = review.build_parser()
    commands = set(parser._subparsers._group_actions[0].choices)
    assert commands == {"list", "inspect", "check", "draft", "stale"}
    assert "promote" not in commands
    assert "reject" not in commands
    assert "delete" not in commands
