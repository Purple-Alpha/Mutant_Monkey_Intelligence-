#!/usr/bin/env python3
"""Local cold backup helper for MMI.

Default behavior is local-only. Cloud upload happens only when --push or
--backup-and-push is explicitly passed (Matt-authorized cold mirror).

Never mutates tasks.json or reads NorthStar.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
from hashlib import sha256
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUSH_LOG_FILE = ROOT / "mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json"
LATEST_GOOD_FILE = ROOT / "mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md"
LATEST_GOOD_VALIDATION_FILE = ROOT / "mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md"
DEFAULT_PUSH_REMOTE = "matt:mmi-cold-storage/archives/"
SHA256_SIDECAR_SUFFIX = ".sha256"

BACKUP_ALLOWLIST = [
    "tasks.json",
    "mmi/project_brain",
    "mmi/task_pipeline.json",
    "CODEX.md",
    "AGENTS.md",
    "scripts/next_task.py",
    "scripts/reload_mmi_pipes.py",
    "scripts/keep_task_queue_warm.py",
    "scripts/complete_task.py",
    "scripts/mmi_verify.py",
    "scripts/mmi_cold_backup.py",
    "scripts/console_server.py",
    "scripts/console_server_harness.py",
    "scripts/console_bundle_builder.py",
    "scripts/console_sign_client.py",
    "scripts/console_fingerprint_seed.py",
    "scripts/proof_gate_harness.py",
    "tests/test_console_server.py",
    "tests/test_proof_gate_console_bindings.py",
    "tests/test_genomic_constraint_validator.py",
    "chaos/genomic_constraint_validator.py",
    "chaos/genomic_constraint_synth.py",
    "requirements_kinetic_console.txt",
    "tests/test_intel_closeout_gate.py",
    "tests/test_backup_push_integrity.py",
    "tests/test_opsec_amend_helper.py",
    "mmi/command_center.py",
    "mmi/war_room.py",
    "mmi/__init__.py",
    "mmi/m4/",
    "scripts/m4_import_ban_test.py",
    "tests/test_m4_import_ban.py",
]

DENY_PATTERNS = [
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    ".env",
    ".env.*",
    "*api_key*",
    "*apikey*",
    "*secret*",
    "*token*",
    "*twilio*",
    "*claude_api*",
    "*bland_key*",
    "*northstar*",
    "rclone.conf",
]

RESTORE_REQUIRED_FILES = [
    "tasks.json",
    "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md",
    "mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md",
    "mmi/command_center.py",
    "scripts/next_task.py",
    "scripts/reload_mmi_pipes.py",
    "scripts/keep_task_queue_warm.py",
    "scripts/mmi_cold_backup.py",
]

RESTORE_PYTHON_FILES = [
    "mmi/command_center.py",
    "scripts/next_task.py",
    "scripts/reload_mmi_pipes.py",
    "scripts/keep_task_queue_warm.py",
    "scripts/complete_task.py",
    "scripts/mmi_verify.py",
    "scripts/mmi_cold_backup.py",
    "scripts/m4_import_ban_test.py",
    "mmi/m4/import_ban.py",
]


@dataclass(frozen=True)
class BackupFile:
    path: str
    sha256: str
    bytes: int


def backup_paths() -> list[str]:
    return list(BACKUP_ALLOWLIST)


def excluded_paths() -> list[str]:
    return list(DENY_PATTERNS)


def is_denied(path: Path) -> bool:
    normalized = path.as_posix().lower()
    name = path.name.lower()
    return any(fnmatch(name, pattern.lower()) or fnmatch(normalized, pattern.lower()) for pattern in DENY_PATTERNS)


def walk_backup_set(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for rel in BACKUP_ALLOWLIST:
        target = root / rel
        if not target.exists():
            continue
        if target.is_file():
            if not target.is_symlink() and not is_denied(Path(rel)):
                files.append(target)
            continue
        if target.is_dir():
            for item in sorted(target.rglob("*")):
                if item.is_file() and not item.is_symlink():
                    rel_item = item.relative_to(root)
                    if not is_denied(rel_item):
                        files.append(item)
    return sorted(set(files), key=lambda item: item.relative_to(root).as_posix())


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_sha256_sidecar(archive: Path, digest: str) -> Path:
    sidecar = archive.with_name(f"{archive.name}{SHA256_SIDECAR_SUFFIX}")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return sidecar


def build_manifest(files: list[Path], root: Path = ROOT, mode: str = "dry-run") -> dict[str, Any]:
    entries = [
        BackupFile(
            path=file.relative_to(root).as_posix(),
            sha256=sha256_file(file),
            bytes=file.stat().st_size,
        )
        for file in files
    ]
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_root": root.as_posix(),
        "mode": mode,
        "files": [entry.__dict__ for entry in entries],
    }


def write_archive(files: list[Path], output: Path, root: Path = ROOT) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for file in files:
            archive.add(file, arcname=file.relative_to(root).as_posix(), recursive=False)
    manifest = build_manifest(files, root=root, mode="archive")
    manifest["archive"] = output.as_posix()
    manifest["archive_bytes"] = output.stat().st_size
    manifest["archive_sha256"] = sha256_file(output)
    return manifest


def validate_push_remote(remote: str) -> str | None:
    if not remote or ":" not in remote:
        return "push remote must look like matt:mmi-cold-storage/archives/"
    remote_name, _, path = remote.partition(":")
    if not remote_name or not path:
        return "push remote must include bucket path after colon"
    if remote_name not in {"matt", "matt-crypt"}:
        return f"push remote name {remote_name!r} is not in allowlist (matt, matt-crypt)"
    return None


def find_rclone() -> str | None:
    if shutil.which("rclone"):
        return "rclone"
    if shutil.which("wsl"):
        return "wsl"
    return None


def rclone_command(rclone: str, *args: str) -> list[str]:
    if rclone == "wsl":
        return ["wsl", "rclone", *args]
    return [rclone, *args]


def rclone_local_path(rclone: str, path: Path) -> str:
    if rclone != "wsl":
        return str(path)
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix()
    rest = resolved.as_posix().split(":", 1)[-1]
    return f"/mnt/{drive}{rest}"


def push_archive(archive: Path, remote: str, checksum: bool = True) -> dict[str, Any]:
    remote_error = validate_push_remote(remote)
    if remote_error:
        return {"push_status": "FAIL", "push_errors": [remote_error]}

    rclone = find_rclone()
    if not rclone:
        return {"push_status": "FAIL", "push_errors": ["rclone not found in PATH"]}

    if not archive.exists() or archive.stat().st_size == 0:
        return {"push_status": "FAIL", "push_errors": [f"archive missing or empty: {archive}"]}

    local_bytes = archive.stat().st_size
    local_hash = sha256_file(archive)
    sidecar = write_sha256_sidecar(archive, local_hash)
    dest = remote if remote.endswith("/") else f"{remote}/"

    copy_cmd = rclone_command(rclone, "copy", rclone_local_path(rclone, archive), dest)
    if checksum:
        copy_cmd.append("--checksum")

    copy_result = subprocess.run(copy_cmd, capture_output=True, text=True)
    if copy_result.returncode != 0:
        return {
            "push_status": "FAIL",
            "push_errors": [
                "rclone copy failed",
                copy_result.stderr.strip() or copy_result.stdout.strip() or f"exit {copy_result.returncode}",
            ],
            "push_remote": dest,
            "archive_sha256": local_hash,
            "local_sha256": local_hash,
        }

    sidecar_copy_cmd = rclone_command(rclone, "copy", rclone_local_path(rclone, sidecar), dest)
    sidecar_copy_result = subprocess.run(sidecar_copy_cmd, capture_output=True, text=True)
    if sidecar_copy_result.returncode != 0:
        return {
            "push_status": "FAIL",
            "push_errors": [
                "rclone sidecar copy failed",
                sidecar_copy_result.stderr.strip()
                or sidecar_copy_result.stdout.strip()
                or f"exit {sidecar_copy_result.returncode}",
            ],
            "push_remote": dest,
            "push_file": archive.name,
            "archive_sha256": local_hash,
            "local_sha256": local_hash,
            "local_bytes": local_bytes,
            "rclone_copy_exit": copy_result.returncode,
            "rclone_sidecar_copy_exit": sidecar_copy_result.returncode,
        }

    remote_file = f"{dest}{archive.name}"
    size_cmd = rclone_command(rclone, "size", remote_file, "--json")
    size_result = subprocess.run(size_cmd, capture_output=True, text=True)
    remote_bytes: int | None = None
    if size_result.returncode == 0 and size_result.stdout.strip():
        try:
            remote_bytes = int(json.loads(size_result.stdout).get("bytes", 0))
        except json.JSONDecodeError:
            remote_bytes = None

    errors: list[str] = []
    byte_match = False
    if remote_bytes is None:
        list_cmd = rclone_command(rclone, "lsf", dest, "--files-only")
        list_result = subprocess.run(list_cmd, capture_output=True, text=True)
        if archive.name not in (list_result.stdout or ""):
            errors.append(f"remote listing did not show {archive.name}")
    elif remote_bytes != local_bytes:
        errors.append(f"remote size {remote_bytes} != local size {local_bytes}")
    else:
        byte_match = True

    remote_sha256: str | None = None
    hash_cmd = rclone_command(rclone, "hashsum", "SHA-256", remote_file, "--download")
    hash_result = subprocess.run(hash_cmd, capture_output=True, text=True)
    if hash_result.returncode == 0 and hash_result.stdout.strip():
        remote_sha256 = hash_result.stdout.strip().split()[0]
    else:
        errors.append(
            "remote SHA-256 check failed: "
            + (hash_result.stderr.strip() or hash_result.stdout.strip() or f"exit {hash_result.returncode}")
        )

    sha_match = remote_sha256 == local_hash
    if remote_sha256 and not sha_match:
        errors.append(f"remote sha256 {remote_sha256} != local sha256 {local_hash}")

    remote_sidecar = f"{dest}{sidecar.name}"
    sidecar_cmd = rclone_command(rclone, "cat", remote_sidecar)
    sidecar_result = subprocess.run(sidecar_cmd, capture_output=True, text=True)
    sidecar_sha256: str | None = None
    if sidecar_result.returncode == 0 and sidecar_result.stdout.strip():
        sidecar_sha256 = sidecar_result.stdout.strip().split()[0]
    else:
        errors.append(
            "remote sha256 sidecar check failed: "
            + (sidecar_result.stderr.strip() or sidecar_result.stdout.strip() or f"exit {sidecar_result.returncode}")
        )

    sidecar_match = sidecar_sha256 == local_hash
    if sidecar_sha256 and not sidecar_match:
        errors.append(f"remote sidecar sha256 {sidecar_sha256} != local sha256 {local_hash}")

    status = "PASS" if not errors else "FAIL"
    return {
        "push_status": status,
        "integrity_status": status,
        "push_remote": dest,
        "push_file": archive.name,
        "local_bytes": local_bytes,
        "archive_sha256": local_hash,
        "local_sha256": local_hash,
        "remote_bytes": remote_bytes,
        "remote_sha256": remote_sha256,
        "remote_sha256_sidecar": sidecar.name,
        "remote_sha256_sidecar_value": sidecar_sha256,
        "byte_match": byte_match,
        "sha256_match": sha_match,
        "sidecar_sha256_match": sidecar_match,
        "restore_check_status": "NOT_RUN",
        "latest_b2_mirror": archive.name,
        "restore_proven_archive": None,
        "latest_good_promotion": "NOT_PROMOTED",
        "safe_for_restore_reference": False,
        "promotion_rule": "Latest B2 mirror is not restore-proven until --restore-check passes for this archive.",
        "push_errors": errors,
        "rclone_copy_exit": copy_result.returncode,
        "rclone_sidecar_copy_exit": sidecar_copy_result.returncode,
        "rclone_hashsum_exit": hash_result.returncode,
        "rclone_sidecar_cat_exit": sidecar_result.returncode,
    }


def append_push_log(record: dict[str, Any]) -> None:
    PUSH_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if PUSH_LOG_FILE.exists() and PUSH_LOG_FILE.read_text(encoding="utf-8").strip():
        try:
            data = json.loads(PUSH_LOG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                existing = data
        except json.JSONDecodeError:
            existing = []
    existing.append(record)
    PUSH_LOG_FILE.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")


def load_push_log(path: Path = PUSH_LOG_FILE) -> list[dict[str, Any]]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def find_push_record(archive_name: str, log_path: Path = PUSH_LOG_FILE) -> dict[str, Any] | None:
    for entry in reversed(load_push_log(log_path)):
        names = {
            Path(str(entry.get("archive", ""))).name,
            str(entry.get("push_file", "")),
            str(entry.get("latest_b2_mirror", "")),
        }
        if archive_name in names:
            return entry
    return None


def _markdown_mentions_pass_for_archive(text: str, archive_name: str) -> bool:
    if archive_name not in text:
        return False
    lowered = text.lower()
    return "pass" in lowered and ("restore-check" in lowered or "--restore-check" in lowered)


def required_manifest_paths_present(record: dict[str, Any]) -> dict[str, Any]:
    required = [
        "tasks.json",
        "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md",
        "mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md",
        "mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md",
        "mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md",
        "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md",
        "scripts/mmi_cold_backup.py",
        "scripts/mmi_verify.py",
        "mmi/war_room.py",
    ]
    files = record.get("files") if isinstance(record.get("files"), list) else []
    present = {str(item.get("path", "")) for item in files if isinstance(item, dict)}
    missing = [path for path in required if path not in present]
    return {
        "ok": len(missing) == 0,
        "required": required,
        "missing": missing,
        "present_count": len(present),
    }


def validate_latest_good_promotion(
    archive_name: str,
    push_log_path: Path = PUSH_LOG_FILE,
    latest_good_path: Path = LATEST_GOOD_FILE,
    validation_path: Path = LATEST_GOOD_VALIDATION_FILE,
) -> dict[str, Any]:
    """Read-only H3 promotion helper; never updates latest-good files."""
    record = find_push_record(archive_name, push_log_path)
    checks: dict[str, Any] = {
        "push_record_found": record is not None,
        "push_integrity_pass": False,
        "manifest_required_paths": {"ok": False, "missing": []},
        "restore_check_pass": False,
        "latest_good_already_points_to_candidate": False,
        "human_gated": True,
    }
    blockers: list[str] = []

    if record is None:
        blockers.append(f"no push log record found for {archive_name}")
    else:
        checks["push_integrity_pass"] = (
            record.get("push_status") == "PASS"
            and record.get("integrity_status", record.get("push_status")) == "PASS"
            and record.get("byte_match") is True
            and record.get("sha256_match") is True
            and record.get("sidecar_sha256_match") is True
        )
        checks["manifest_required_paths"] = required_manifest_paths_present(record)
        restore_status = str(record.get("restore_check_status", "NOT_RUN")).upper()
        checks["restore_check_status"] = restore_status
        checks["restore_check_pass"] = restore_status == "PASS"
        if not checks["push_integrity_pass"]:
            blockers.append("push integrity is not PASS")
        if not checks["manifest_required_paths"]["ok"]:
            blockers.append("manifest is missing required high-signal paths")
        if not checks["restore_check_pass"]:
            blockers.append("restore-check PASS evidence is missing for this archive")

    latest_good_text = latest_good_path.read_text(encoding="utf-8") if latest_good_path.exists() else ""
    validation_text = validation_path.read_text(encoding="utf-8") if validation_path.exists() else ""
    checks["latest_good_already_points_to_candidate"] = archive_name in latest_good_text
    checks["validation_doc_mentions_pass"] = _markdown_mentions_pass_for_archive(validation_text, archive_name)
    if checks["validation_doc_mentions_pass"]:
        checks["restore_check_pass"] = True
        if "restore-check PASS evidence is missing for this archive" in blockers:
            blockers.remove("restore-check PASS evidence is missing for this archive")

    verdict = "ALLOWED" if not blockers else "BLOCKED"
    return {
        "check": "H3_latest_good_promotion_helper",
        "archive": archive_name,
        "promotion": verdict,
        "allowed": verdict == "ALLOWED",
        "blockers": blockers,
        "checks": checks,
        "action": (
            "Matt may manually update MMI_LATEST_GOOD_ARCHIVE.md after reviewing this evidence."
            if verdict == "ALLOWED"
            else "Do not promote latest-good; run isolated --restore-check and record PASS evidence first."
        ),
        "human_gated_workflow": [
            "1. Confirm push log integrity PASS for the candidate archive.",
            "2. Run isolated restore-check for that exact archive.",
            "3. Record PASS evidence in validation notes.",
            "4. Matt manually updates MMI_LATEST_GOOD_ARCHIVE.md if promotion is still desired.",
        ],
        "mutated_files": [],
    }


def validate_tasks_json(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"tasks.json invalid: {exc}"
    if not isinstance(data, list):
        return "tasks.json must contain a JSON list"
    return None


def restore_check(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    root = path.resolve()

    for rel in RESTORE_REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    tasks_path = root / "tasks.json"
    if tasks_path.exists():
        task_error = validate_tasks_json(tasks_path)
        if task_error:
            errors.append(task_error)

    for rel in RESTORE_PYTHON_FILES:
        file = root / rel
        if not file.exists():
            continue
        try:
            py_compile.compile(str(file), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"syntax check failed for {rel}: {exc.msg}")

    return {
        "restore_root": root.as_posix(),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show selected files without writing")
    parser.add_argument("--manifest", action="store_true", help="print backup manifest JSON")
    parser.add_argument("--archive", type=Path, help="write local tar.gz archive to this path")
    parser.add_argument(
        "--push",
        metavar="REMOTE",
        help=f"push archive to rclone destination (default with --backup-and-push: {DEFAULT_PUSH_REMOTE})",
    )
    parser.add_argument(
        "--push-archive",
        type=Path,
        help="push an existing archive (requires --push); does not rebuild",
    )
    parser.add_argument(
        "--backup-and-push",
        action="store_true",
        help="timestamped local archive then push to default B2 cold path",
    )
    parser.add_argument("--no-checksum", action="store_true", help="omit rclone --checksum on push")
    parser.add_argument("--restore-check", type=Path, help="validate a restored local MMI copy")
    parser.add_argument(
        "--validate-promotion",
        metavar="ARCHIVE_NAME",
        help="read-only H3 helper: report whether an archive may be manually promoted to latest-good",
    )
    args = parser.parse_args()

    if args.validate_promotion:
        result = validate_latest_good_promotion(args.validate_promotion)
        print_json(result)
        return 0 if result["allowed"] else 1

    if args.restore_check:
        result = restore_check(args.restore_check)
        print_json(result)
        return 0 if result["status"] == "PASS" else 1

    push_remote = args.push
    archive_path = args.archive

    if args.backup_and_push:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_archive = ROOT / "mmi" / "project_brain" / "backup" / f"mmi_backup_{stamp}.tar.gz"
        archive_path = archive_path or default_archive
        push_remote = push_remote or DEFAULT_PUSH_REMOTE

    if args.push_archive:
        if not push_remote:
            raise SystemExit("--push-archive requires --push REMOTE")
        archive_path = args.push_archive
        if not archive_path.exists():
            raise SystemExit(f"archive not found: {archive_path}")
        push_result = push_archive(archive_path, push_remote, checksum=not args.no_checksum)
        record = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "mode": "push-archive",
            "archive": archive_path.as_posix(),
            **push_result,
        }
        append_push_log(record)
        print_json(record)
        return 0 if push_result["push_status"] == "PASS" else 1

    if archive_path and push_remote:
        files = walk_backup_set(ROOT)
        manifest = write_archive(files, archive_path, ROOT)
        push_result = push_archive(archive_path, push_remote, checksum=not args.no_checksum)
        manifest["mode"] = "archive-and-push"
        manifest.update(push_result)
        append_push_log(manifest)
        print_json(manifest)
        return 0 if push_result["push_status"] == "PASS" else 1

    if archive_path:
        print_json(write_archive(walk_backup_set(ROOT), archive_path, ROOT))
        return 0

    inspect_actions = [args.dry_run, args.manifest, bool(push_remote)]
    if sum(1 for action in inspect_actions if action) > 1:
        raise SystemExit("Choose one inspect action: --dry-run or --manifest")
    if push_remote and not archive_path:
        raise SystemExit("--push requires --archive or use --backup-and-push / --push-archive")

    files = walk_backup_set(ROOT)
    mode = "manifest" if args.manifest else "dry-run"
    manifest = build_manifest(files, ROOT, mode)
    if args.dry_run or not args.manifest:
        manifest["allowlist"] = backup_paths()
        manifest["excluded_patterns"] = excluded_paths()
    print_json(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
