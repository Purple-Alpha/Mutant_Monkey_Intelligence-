#!/usr/bin/env python3
"""Tier 2A Mode A — structural worker completion packet intake validator.

Stdout only. No file writes. Does not run mmi_dispatch.py or judge work quality.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERDICT_ACCEPT = "ACCEPT_FOR_MMI_REVIEW"
VERDICT_REJECT = "REJECT_INCOMPLETE_PACKET"

FORBIDDEN_STDOUT_TOKENS = frozenset(
    {
        "PASS",
        "FAIL",
        "APPROVED",
        "VERIFIED",
        "COMPLETE",
        "BUILD_AUTHORIZED",
        "SIGNED",
        "PROMOTED",
    }
)

ROUTING_AUTHORITY_FRAGMENTS = (
    "MMI_CURRENT_STATE.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "MASTER_INDEX.md",
)

REQUIRED_OOS_SUBSTRINGS = (
    "dispatcher/code/runtime/scoreboard unchanged",
    "no registry population",
    "no Architectapp",
    "no #47/#48 changes",
    "no parked draft promotion",
    "no push",
)

FIELD_ORDER = (
    "task_or_contract_ref",
    "worker_lane",
    "authorization_ref",
    "files_changed",
    "exact_commit_hash",
    "scope_confirmation",
    "tests_gates_run",
    "deviations_from_contract",
    "mmi_verify_output",
    "git_status_short",
    "no_out_of_scope_confirmations",
    "operator_action_required",
    "notes",
)

_HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")


def _strip_packet_value(value: str) -> str:
    return value.strip()


def _parse_packet(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not any(line.strip() == "WORKER_COMPLETION_PACKET" for line in lines[:3]):
        return {}

    fields: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current_key, buffer
        if current_key is not None:
            fields[current_key] = "\n".join(buffer).rstrip()
        buffer = []

    for line in lines:
        if line.strip() == "WORKER_COMPLETION_PACKET":
            continue
        matched = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if matched and matched.group(1) in FIELD_ORDER:
            flush()
            current_key = matched.group(1)
            rest = matched.group(2)
            buffer = [rest] if rest else []
        elif current_key is not None:
            buffer.append(line)
        elif line.strip():
            flush()
            current_key = None

    flush()
    return fields


def _list_items(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped.startswith("-") and len(stripped) > 1:
            items.append(stripped[1:].strip())
    return items


def _routing_authority_files_changed(files_block: str) -> bool:
    for item in _list_items(files_block):
        for fragment in ROUTING_AUTHORITY_FRAGMENTS:
            if fragment in item:
                return True
    return False


def _validate_fields(fields: dict[str, str]) -> list[str]:
    codes: list[str] = []

    if not fields:
        codes.append("MISSING_WORKER_COMPLETION_PACKET_MARKER")
        return codes

    def require_scalar(key: str, code: str) -> str | None:
        if key not in fields:
            codes.append(code)
            return None
        value = _strip_packet_value(fields[key])
        if not value:
            codes.append(code)
            return None
        return value

    require_scalar("task_or_contract_ref", "MISSING_TASK_OR_CONTRACT_REF")
    require_scalar("worker_lane", "MISSING_WORKER_LANE")
    require_scalar("authorization_ref", "MISSING_AUTHORIZATION_REF")

    if "files_changed" not in fields:
        codes.append("MISSING_FILES_CHANGED")
    else:
        file_items = _list_items(fields["files_changed"])
        if not file_items:
            codes.append("EMPTY_FILES_CHANGED")
        elif all(not item or item == "-" for item in file_items):
            codes.append("EMPTY_FILES_CHANGED")

    commit_raw = fields.get("exact_commit_hash")
    if commit_raw is None:
        codes.append("MISSING_EXACT_COMMIT_HASH")
    else:
        commit = _strip_packet_value(commit_raw)
        if not commit:
            codes.append("MISSING_EXACT_COMMIT_HASH")
        elif commit.upper() != "PENDING" and not _HEX40.match(commit):
            codes.append("INVALID_EXACT_COMMIT_HASH_FORMAT")

    require_scalar("scope_confirmation", "MISSING_SCOPE_CONFIRMATION")

    if "tests_gates_run" not in fields:
        codes.append("MISSING_TESTS_GATES_RUN")
    else:
        tests_block = _strip_packet_value(fields["tests_gates_run"])
        if not tests_block:
            codes.append("MISSING_TESTS_GATES_RUN")

    if "deviations_from_contract" not in fields:
        codes.append("MISSING_DEVIATIONS_FROM_CONTRACT")
    else:
        dev_block = fields["deviations_from_contract"]
        dev_stripped = _strip_packet_value(dev_block)
        if not dev_stripped:
            codes.append("BLANK_DEVIATIONS_FROM_CONTRACT")
        else:
            dev_items = _list_items(dev_block)
            dev_lower = dev_stripped.lower()
            if dev_lower in {"n/a", "na", "etc.", "etc"}:
                codes.append("VAGUE_DEVIATIONS_FROM_CONTRACT")
            elif dev_items:
                if all(item.lower() == "none" for item in dev_items):
                    pass
                elif any(
                    not item or item.lower() in {"n/a", "na", "etc.", "etc"}
                    for item in dev_items
                ):
                    codes.append("VAGUE_DEVIATIONS_FROM_CONTRACT")
            elif dev_lower != "none":
                codes.append("VAGUE_DEVIATIONS_FROM_CONTRACT")

    files_block = fields.get("files_changed", "")
    needs_verify = _routing_authority_files_changed(files_block)
    if needs_verify:
        if "mmi_verify_output" not in fields:
            codes.append("MISSING_MMI_VERIFY_OUTPUT")
        elif not _strip_packet_value(fields["mmi_verify_output"]):
            codes.append("MISSING_MMI_VERIFY_OUTPUT")

    if "git_status_short" not in fields:
        codes.append("MISSING_GIT_STATUS_SHORT")
    elif not _strip_packet_value(fields["git_status_short"]):
        codes.append("MISSING_GIT_STATUS_SHORT")

    if "no_out_of_scope_confirmations" not in fields:
        codes.append("MISSING_NO_OUT_OF_SCOPE_CONFIRMATIONS")
    else:
        oos_block = fields["no_out_of_scope_confirmations"]
        oos_lines = [line.strip() for line in oos_block.splitlines() if line.strip()]
        if not oos_lines:
            codes.append("MISSING_NO_OUT_OF_SCOPE_CONFIRMATIONS")
        else:
            joined = "\n".join(oos_lines).lower()
            for required in REQUIRED_OOS_SUBSTRINGS:
                if required.lower() not in joined:
                    codes.append("INCOMPLETE_NO_OUT_OF_SCOPE_CONFIRMATIONS")
                    break
            for line in oos_lines:
                if ":" in line:
                    _, after = line.split(":", 1)
                    if not after.strip():
                        codes.append("INCOMPLETE_NO_OUT_OF_SCOPE_CONFIRMATIONS")
                        break

    require_scalar("operator_action_required", "MISSING_OPERATOR_ACTION_REQUIRED")

    return sorted(set(codes))


def validate_packet_text(text: str) -> tuple[str, list[str]]:
    codes = _validate_fields(_parse_packet(text))
    if codes:
        return VERDICT_REJECT, codes
    return VERDICT_ACCEPT, []


def format_stdout(verdict: str, codes: list[str]) -> str:
    lines = [verdict]
    if codes:
        lines.extend(codes)
    output = "\n".join(lines) + "\n"
    for token in FORBIDDEN_STDOUT_TOKENS:
        for line in lines:
            if line == token or line.startswith(token + " "):
                raise RuntimeError(f"forbidden stdout token would be emitted: {token}")
    if any(line == "REJECT" for line in lines):
        raise RuntimeError("forbidden standalone REJECT on stdout")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tier 2A Mode A structural worker completion packet validator (stdout only)."
    )
    parser.add_argument(
        "packet_path",
        help="Path to worker completion packet text file",
    )
    args = parser.parse_args(argv)

    path = Path(args.packet_path)
    if not path.is_file():
        verdict, codes = VERDICT_REJECT, ["PACKET_FILE_NOT_FOUND"]
        sys.stdout.write(format_stdout(verdict, codes))
        return 1

    text = path.read_text(encoding="utf-8")
    verdict, codes = validate_packet_text(text)
    sys.stdout.write(format_stdout(verdict, codes))
    return 0 if verdict == VERDICT_ACCEPT else 1


if __name__ == "__main__":
    raise SystemExit(main())
