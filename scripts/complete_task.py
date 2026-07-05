#!/usr/bin/env python3
"""Mark an MMI task completed and auto-seed the next pipeline task if dry."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from keep_task_queue_warm import seed_if_dry
from mmi_verify import verify_closeout_outputs, verify_intel_brief


ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "tasks.json"
ARTIFACT_TIER_MARKERS = ("architecture", "verification", "resilience")
INTEL_BRIEF_PREFIX = "mmi/project_brain/intel/briefs/"
CLOSEOUT_CONTRACT_VERSION = "P8_CLOSEOUT_EVIDENCE_CONTRACT_v1"
SIGN_OFF_CHOICES = ("PASS", "PASS WITH REVISIONS", "FAIL")


def load_tasks() -> list[dict[str, Any]]:
    data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("tasks.json must contain a JSON list")
    return data


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    TASK_FILE.write_text(json.dumps(tasks, indent=4) + "\n", encoding="utf-8")


def requires_output(task: dict[str, Any]) -> bool:
    """True for tiers that create artifacts or verification evidence."""
    tier = str(task.get("tier", "")).lower()
    return any(marker in tier for marker in ARTIFACT_TIER_MARKERS)


def load_verify_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": path.as_posix(), "ok": False, "error": "verify JSON file not found"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"path": path.as_posix(), "ok": False, "error": f"invalid JSON: {exc}"}
    if not isinstance(data, dict):
        return {"path": path.as_posix(), "ok": False, "error": "verify JSON must contain an object"}

    if "ok" in data:
        passed = data.get("ok") is True
    elif "status" in data:
        passed = str(data.get("status", "")).upper() == "PASS"
    elif "push_status" in data:
        passed = str(data.get("push_status", "")).upper() == "PASS"
    else:
        return {
            "path": path.as_posix(),
            "ok": False,
            "error": "verify JSON must include ok=true, status=PASS, or push_status=PASS",
            "data": data,
        }

    return {"path": path.as_posix(), "ok": passed, "data": data}


def verify_json_files(root: Path, paths: list[str]) -> dict[str, Any]:
    results = []
    for raw in paths:
        path = Path(raw)
        target = path if path.is_absolute() else root / raw.replace("\\", "/")
        results.append(load_verify_json(target))
    failed = [result for result in results if not result.get("ok")]
    return {
        "check": "verify_json_files",
        "ok": len(failed) == 0,
        "results": results,
        "failed": failed,
    }


def verify_artifact_file(root: Path, raw: str | None) -> dict[str, Any]:
    if not raw:
        return {"path": None, "ok": True, "required": False}
    path = Path(raw)
    target = path if path.is_absolute() else root / raw.replace("\\", "/")
    if not target.exists():
        return {"path": raw, "ok": False, "error": "verification artifact not found"}
    if not target.is_file():
        return {"path": raw, "ok": False, "error": "verification artifact is not a file"}
    if target.suffix.lower() != ".json":
        return {"path": raw, "ok": False, "error": "verification artifact must be a JSON file"}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"path": raw, "ok": False, "error": f"invalid JSON: {exc}"}
    if not isinstance(data, dict):
        return {"path": raw, "ok": False, "error": "verification artifact must contain a JSON object"}
    return {"path": raw, "ok": True, "data": data}


def _normalized_output_path(raw: str) -> str:
    return raw.replace("\\", "/").lstrip("./")


def is_intel_brief_output(raw: str) -> bool:
    normalized = _normalized_output_path(raw)
    name = Path(normalized).name
    return normalized.startswith(INTEL_BRIEF_PREFIX) and name.startswith("INTEL_") and name.endswith(".md")


def verify_intel_outputs(root: Path, paths: list[str]) -> dict[str, Any]:
    intel_paths = [raw for raw in paths if is_intel_brief_output(raw)]
    results = []
    for raw in intel_paths:
        path = Path(raw)
        target = path if path.is_absolute() else root / raw.replace("\\", "/")
        results.append(verify_intel_brief(target))
    failed = [result for result in results if not result.get("ok")]
    return {
        "check": "H2_intel_closeout_gate",
        "ok": len(failed) == 0,
        "intel_outputs": intel_paths,
        "results": results,
        "failed": failed,
    }


def _command_record(label: str, command: str, exit_code: int, ok: bool) -> dict[str, Any]:
    return {
        "label": label,
        "command": command,
        "exit_code": exit_code,
        "ok": ok,
    }


def build_verification_commands(
    outputs: list[str],
    verify_json_paths: list[str],
    intel_paths: list[str],
    artifact_path: str | None,
) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    if outputs:
        quoted = " ".join(outputs)
        commands.append(
            _command_record(
                "H1 closeout outputs",
                f"python scripts/mmi_verify.py closeout {quoted}",
                0,
                True,
            )
        )
    for raw in verify_json_paths:
        commands.append(
            _command_record(
                "verify JSON artifact",
                f"python scripts/complete_task.py --verify-json {raw}",
                0,
                True,
            )
        )
    if intel_paths:
        quoted = " ".join(intel_paths)
        commands.append(
            _command_record(
                "H2 intel closeout gate",
                f"python scripts/mmi_verify.py intel-brief {quoted}",
                0,
                True,
            )
        )
    if artifact_path:
        commands.append(
            _command_record(
                "closeout verification artifact",
                f"python -m json.tool {artifact_path}",
                0,
                True,
            )
        )
    return commands


def format_result_summary(sign_off: str, summary: str) -> str:
    summary = summary.strip()
    if summary.upper().startswith(f"{sign_off} "):
        return summary
    if summary.upper() == sign_off:
        return summary
    return f"{sign_off} - {summary}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id", help="task id to mark completed")
    parser.add_argument("--by", required=True, help="completed_by value")
    parser.add_argument("--summary", required=True, help="result_summary")
    parser.add_argument(
        "--output",
        action="append",
        default=[],
        dest="outputs",
        help="output file path (repeatable)",
    )
    parser.add_argument(
        "--verify-json",
        action="append",
        default=[],
        dest="verify_json",
        help="verification JSON path that must contain ok=true, status=PASS, or push_status=PASS (repeatable)",
    )
    parser.add_argument(
        "--verification-artifact",
        help="optional closeout evidence JSON artifact path to validate and record",
    )
    parser.add_argument(
        "--sign-off",
        choices=SIGN_OFF_CHOICES,
        default="PASS",
        help="closeout sign-off enum recorded with result_summary",
    )
    parser.add_argument(
        "--sign-off-tier",
        help="who accepted closeout caveats; defaults to --by",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="do not auto-seed next pipeline task after completion",
    )
    args = parser.parse_args()

    tasks = load_tasks()
    task = next((item for item in tasks if str(item.get("id")) == args.task_id), None)
    if task is None:
        print(f"Task not found: {args.task_id}")
        return 1

    if requires_output(task) and not args.outputs:
        print("G-CLOSEOUT FAILED — this task tier requires at least one --output path.")
        print(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "tier": task.get("tier", ""),
                    "required_for_tier_markers": list(ARTIFACT_TIER_MARKERS),
                },
                indent=2,
            )
        )
        return 1

    h1 = verify_closeout_outputs(ROOT, args.outputs)
    if not h1["ok"]:
        print("H1 closeout verification FAILED — output_files missing on disk:")
        print(json.dumps(h1, indent=2))
        return 1

    verify_json_result = verify_json_files(ROOT, args.verify_json)
    if not verify_json_result["ok"]:
        print("G-CLOSEOUT verify-json FAILED:")
        print(json.dumps(verify_json_result, indent=2))
        return 1

    h2 = verify_intel_outputs(ROOT, args.outputs)
    if not h2["ok"]:
        print("G-INTEL closeout verification FAILED — intel brief H2 violations:")
        print(json.dumps(h2, indent=2))
        return 1

    verification_artifact_result = verify_artifact_file(ROOT, args.verification_artifact)
    if not verification_artifact_result["ok"]:
        print("G-CLOSEOUT verification-artifact FAILED:")
        print(json.dumps(verification_artifact_result, indent=2))
        return 1

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    sign_off_tier = args.sign_off_tier or args.by
    verification_commands = build_verification_commands(
        args.outputs,
        args.verify_json,
        h2["intel_outputs"],
        args.verification_artifact,
    )
    task["status"] = "completed"
    task["completed_at"] = now
    task["completed_by"] = args.by
    task["result_summary"] = format_result_summary(args.sign_off, args.summary)
    task["sign_off"] = args.sign_off
    task["sign_off_tier"] = sign_off_tier
    task["output_files"] = args.outputs
    task["verification_commands"] = verification_commands
    task["verification_artifact"] = args.verification_artifact
    task["closeout_verification"] = {
        "h1": h1,
        "h2": h2,
        "verify_json": verify_json_result,
        "verification_artifact": verification_artifact_result,
    }
    task["closeout_evidence_contract"] = {
        "version": CLOSEOUT_CONTRACT_VERSION,
        "ok": True,
        "required_fields": [
            "output_files",
            "verification_commands",
            "verification_artifact",
            "result_summary",
            "sign_off",
            "sign_off_tier",
            "closeout_verification",
        ],
        "recover_under_pressure": (
            "Use output_files plus closeout_verification to re-run gates; "
            "use verification_commands and verification_artifact to explain what was checked."
        ),
    }

    save_tasks(tasks)
    print(f"Completed: {args.task_id}")

    if args.no_seed:
        return 0

    result = seed_if_dry()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
