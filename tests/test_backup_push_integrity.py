import os
import stat
import tempfile
import unittest
from pathlib import Path

from scripts import mmi_cold_backup


FAKE_RCLONE = r'''#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

remote_dir = Path(os.environ["FAKE_RCLONE_REMOTE_DIR"])
remote_dir.mkdir(parents=True, exist_ok=True)

args = sys.argv[1:]
cmd = args[0]

def remote_path(raw):
    name = raw.rstrip("/").split("/")[-1]
    return remote_dir / name

if cmd == "copy":
    src = Path(args[1])
    target = remote_dir / src.name
    shutil.copy2(src, target)
    if os.environ.get("FAKE_RCLONE_CORRUPT_ARCHIVE") == "1" and not src.name.endswith(".sha256"):
        target.write_bytes(target.read_bytes() + b"corrupt")
    sys.exit(0)

if cmd == "size":
    target = remote_path(args[1])
    print(json.dumps({"bytes": target.stat().st_size}))
    sys.exit(0)

if cmd == "hashsum":
    target = remote_path(args[2])
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"{digest}  {target.name}")
    sys.exit(0)

if cmd == "cat":
    target = remote_path(args[1])
    print(target.read_text(encoding="utf-8"), end="")
    sys.exit(0)

if cmd == "lsf":
    for item in sorted(remote_dir.iterdir()):
        if item.is_file():
            print(item.name)
    sys.exit(0)

print("unsupported fake rclone command", args, file=sys.stderr)
sys.exit(2)
'''


class BackupPushIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.rclone = self.bin / "rclone"
        self.rclone.write_text(FAKE_RCLONE, encoding="utf-8")
        self.rclone.chmod(self.rclone.stat().st_mode | stat.S_IXUSR)
        self.archive = self.root / "mmi_backup_test.tar.gz"
        self.archive.write_bytes(b"archive bytes")
        self.old_path = os.environ.get("PATH", "")
        self.old_remote = os.environ.get("FAKE_RCLONE_REMOTE_DIR")
        self.old_corrupt = os.environ.get("FAKE_RCLONE_CORRUPT_ARCHIVE")
        os.environ["PATH"] = f"{self.bin}{os.pathsep}{self.old_path}"
        os.environ["FAKE_RCLONE_REMOTE_DIR"] = str(self.remote)

    def tearDown(self):
        os.environ["PATH"] = self.old_path
        if self.old_remote is None:
            os.environ.pop("FAKE_RCLONE_REMOTE_DIR", None)
        else:
            os.environ["FAKE_RCLONE_REMOTE_DIR"] = self.old_remote
        if self.old_corrupt is None:
            os.environ.pop("FAKE_RCLONE_CORRUPT_ARCHIVE", None)
        else:
            os.environ["FAKE_RCLONE_CORRUPT_ARCHIVE"] = self.old_corrupt
        self.temp.cleanup()

    def test_push_pass_requires_remote_byte_and_sha_match(self):
        result = mmi_cold_backup.push_archive(self.archive, "matt:mmi-cold-storage/archives/")

        self.assertEqual(result["push_status"], "PASS")
        self.assertTrue(result["byte_match"])
        self.assertTrue(result["sha256_match"])
        self.assertTrue(result["sidecar_sha256_match"])
        self.assertEqual(result["archive_sha256"], result["remote_sha256"])
        self.assertEqual(result["restore_check_status"], "NOT_RUN")
        self.assertEqual(result["latest_good_promotion"], "NOT_PROMOTED")
        self.assertFalse(result["safe_for_restore_reference"])

    def test_push_fails_when_remote_archive_hash_differs(self):
        os.environ["FAKE_RCLONE_CORRUPT_ARCHIVE"] = "1"

        result = mmi_cold_backup.push_archive(self.archive, "matt:mmi-cold-storage/archives/")

        self.assertEqual(result["push_status"], "FAIL")
        self.assertFalse(result["sha256_match"])
        self.assertFalse(result["safe_for_restore_reference"])
        self.assertTrue(any("remote sha256" in error for error in result["push_errors"]))

    def write_push_log(self, archive_name, restore_status="NOT_RUN"):
        record = {
            "archive": f"/tmp/{archive_name}",
            "push_file": archive_name,
            "push_status": "PASS",
            "integrity_status": "PASS",
            "byte_match": True,
            "sha256_match": True,
            "sidecar_sha256_match": True,
            "restore_check_status": restore_status,
            "files": [
                {"path": "tasks.json"},
                {"path": "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md"},
                {"path": "mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md"},
                {"path": "mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md"},
                {"path": "mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md"},
                {"path": "mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md"},
                {"path": "scripts/mmi_cold_backup.py"},
                {"path": "scripts/mmi_verify.py"},
                {"path": "mmi/war_room.py"},
            ],
        }
        path = self.root / "push_log.json"
        path.write_text(__import__("json").dumps([record]), encoding="utf-8")
        return path

    def test_promotion_helper_blocks_without_restore_check_pass(self):
        archive_name = "mmi_backup_20260701_103517.tar.gz"
        push_log = self.write_push_log(archive_name, restore_status="NOT_RUN")
        latest_good = self.root / "MMI_LATEST_GOOD_ARCHIVE.md"
        validation = self.root / "VALIDATION.md"
        latest_good.write_text("restore-proven `mmi_backup_20260630_163709.tar.gz`\n", encoding="utf-8")
        validation.write_text("No restore-check PASS for candidate.\n", encoding="utf-8")

        result = mmi_cold_backup.validate_latest_good_promotion(
            archive_name,
            push_log_path=push_log,
            latest_good_path=latest_good,
            validation_path=validation,
        )

        self.assertEqual(result["promotion"], "BLOCKED")
        self.assertFalse(result["allowed"])
        self.assertIn("restore-check PASS evidence is missing for this archive", result["blockers"])
        self.assertEqual(result["mutated_files"], [])

    def test_promotion_helper_allows_with_restore_check_pass(self):
        archive_name = "mmi_backup_20260701_103517.tar.gz"
        push_log = self.write_push_log(archive_name, restore_status="PASS")
        latest_good = self.root / "MMI_LATEST_GOOD_ARCHIVE.md"
        validation = self.root / "VALIDATION.md"
        latest_good.write_text("restore-proven `mmi_backup_20260630_163709.tar.gz`\n", encoding="utf-8")
        validation.write_text(f"Restore-check PASS for `{archive_name}`.\n", encoding="utf-8")

        result = mmi_cold_backup.validate_latest_good_promotion(
            archive_name,
            push_log_path=push_log,
            latest_good_path=latest_good,
            validation_path=validation,
        )

        self.assertEqual(result["promotion"], "ALLOWED")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["blockers"], [])
        self.assertIn("Matt may manually update", result["action"])


if __name__ == "__main__":
    unittest.main()
