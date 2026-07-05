import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INTEL_OUTPUT = "mmi/project_brain/intel/briefs/INTEL_sample-threat_2026-07.md"


CLEAN_BRIEF = """# INTEL sample threat

## 1. Threat Summary

This brief describes an SMB-relevant ransomware risk using operator-safe language.

## 2. Scope

Local advisory context only.

## 3. ATT&CK Mapping

| Field | Content |
| --- | --- |
| technique_id | T1486 |
| technique_name | Data Encrypted for Impact |
| smb_relevance | SMB operators should maintain tested restores and offline recovery paths. |

## 5. Claims Table

| Claim | Source status |
| --- | --- |
| Verizon reports 88% in a global vendor dataset. | NEEDS VERIFY / quarantined |
"""


FAULT_BRIEF = CLEAN_BRIEF.replace(
    "This brief describes an SMB-relevant ransomware risk using operator-safe language.",
    "Verizon reports 88% of Canadian SMB breaches involve ransomware.",
)


class IntelCloseoutGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scripts = self.root / "scripts"
        self.scripts.mkdir()
        (self.root / "mmi" / "task_pipeline.json").parent.mkdir(parents=True)
        (self.root / "mmi" / "task_pipeline.json").write_text("[]\n", encoding="utf-8")

        for name in ("complete_task.py", "keep_task_queue_warm.py", "mmi_verify.py"):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.scripts / name)

    def tearDown(self):
        self.temp.cleanup()

    @property
    def tasks_path(self):
        return self.root / "tasks.json"

    @property
    def brief_path(self):
        return self.root / INTEL_OUTPUT

    def write_tasks(self):
        tasks = [
            {
                "id": "intel-task",
                "status": "pending",
                "assignee": "Codex",
                "tier": "Verification",
                "work": "test fixture",
            }
        ]
        self.tasks_path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
        return tasks

    def write_brief(self, content):
        self.brief_path.parent.mkdir(parents=True)
        self.brief_path.write_text(content, encoding="utf-8")

    def read_task(self):
        return json.loads(self.tasks_path.read_text(encoding="utf-8"))[0]

    def run_complete(self):
        return subprocess.run(
            [
                sys.executable,
                str(self.scripts / "complete_task.py"),
                "intel-task",
                "--by",
                "test",
                "--summary",
                "test summary",
                "--output",
                INTEL_OUTPUT,
                "--no-seed",
            ],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_h2(self):
        return subprocess.run(
            [sys.executable, str(self.scripts / "mmi_verify.py"), "intel-brief", INTEL_OUTPUT],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_clean_intel_brief_passes_h2(self):
        self.write_brief(CLEAN_BRIEF)

        result = self.run_h2()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_section_1_laundering_fails_h2(self):
        self.write_brief(FAULT_BRIEF)

        result = self.run_h2()

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["violations"][0]["context"], "section_1_threat_summary")

    def test_quarantined_claims_table_stat_passes_h2(self):
        self.write_brief(CLEAN_BRIEF)

        result = self.run_h2()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verizon reports 88%", self.brief_path.read_text(encoding="utf-8"))

    def test_h2_failure_blocks_closeout_without_writing_state(self):
        before = self.write_tasks()
        self.write_brief(FAULT_BRIEF)

        result = self.run_complete()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("G-INTEL closeout verification FAILED", result.stdout)
        self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)

    def test_h2_pass_records_closeout_verification(self):
        self.write_tasks()
        self.write_brief(CLEAN_BRIEF)

        result = self.run_complete()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        task = self.read_task()
        self.assertEqual(task["status"], "completed")
        self.assertTrue(task["closeout_verification"]["h2"]["ok"])
        self.assertEqual(task["closeout_verification"]["h2"]["intel_outputs"], [INTEL_OUTPUT])


if __name__ == "__main__":
    unittest.main()
