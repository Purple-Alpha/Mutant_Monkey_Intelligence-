import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CompleteTaskGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scripts = self.root / "scripts"
        self.scripts.mkdir()
        (self.root / "mmi").mkdir()
        (self.root / "mmi" / "task_pipeline.json").write_text("[]\n", encoding="utf-8")

        for name in ("complete_task.py", "keep_task_queue_warm.py", "mmi_verify.py", "validate_report_card.py"):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.scripts / name)

    def tearDown(self):
        self.temp.cleanup()

    def write_tasks(self, tier="Architecture / Verification", status="pending"):
        tasks = [
            {
                "id": "gate-task",
                "status": status,
                "assignee": "Codex",
                "tier": tier,
                "work": "test fixture",
            }
        ]
        self.tasks_path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
        return tasks

    @property
    def tasks_path(self):
        return self.root / "tasks.json"

    def read_task(self):
        return json.loads(self.tasks_path.read_text(encoding="utf-8"))[0]

    def write_report_card(self, grade="A", critical="law compliance = 3, evidence discipline = 3"):
        path = self.root / "report_card.md"
        path.write_text(
            f"""## Identity
- target_artifact: fixture artifact
- grader_id: independent-test-reviewer
- hash_verification_mode: TOOL_RECOMPUTED

## Target_artifact_report_card
- target_artifact_grade_label: {grade}
- letter_grade_mark: {grade}
- rubric_scores: [law compliance: 3, evidence discipline: 3, lane obedience: 3]
- criterion_feedback:
    - criterion: law compliance
      score: 3
      quality_mark: PERFECT
      what_worked: Complete.
      what_failed_or_was_missing: None.
      improvement_target: Maintain.
- improvement_targets: Maintain current fixture discipline.
- critical_criteria_results: {critical}
- lowest_score_rule_applied: YES
- averaging_used: NO

## Review_artifact_status
- review_artifact_acceptance_status: INDEPENDENT_REVIEW_REQUIRED
""",
            encoding="utf-8",
        )
        return path

    def run_complete(self, *args):
        report_card = self.write_report_card()
        return subprocess.run(
            [
                sys.executable,
                str(self.scripts / "complete_task.py"),
                "gate-task",
                "--by",
                "test",
                "--summary",
                "test summary",
                "--report-card",
                str(report_card.relative_to(self.root)),
                "--no-seed",
                *args,
            ],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_h1_artifact_tiers_require_output_path(self):
        for tier in ("Architecture", "Verification", "Resilience"):
            with self.subTest(tier=tier):
                before = self.write_tasks(tier=tier)

                result = self.run_complete()

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("requires at least one --output", result.stdout)
                self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)

    def test_missing_output_blocks_closeout_without_writing_state(self):
        before = self.write_tasks()

        result = self.run_complete("--output", "missing.md")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("H1 closeout verification FAILED", result.stdout)
        self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)

    def test_valid_output_allows_closeout(self):
        self.write_tasks()
        output = self.root / "mmi" / "project_brain" / "architecture" / "SPEC.md"
        output.parent.mkdir(parents=True)
        output.write_text("# spec\n", encoding="utf-8")

        result = self.run_complete("--output", "mmi/project_brain/architecture/SPEC.md")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        task = self.read_task()
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["output_files"], ["mmi/project_brain/architecture/SPEC.md"])
        self.assertTrue(task["closeout_verification"]["h1"]["ok"])
        self.assertEqual(task["sign_off"], "PASS")
        self.assertEqual(task["sign_off_tier"], "test")
        self.assertTrue(task["result_summary"].startswith("PASS - "))
        self.assertIn("verification_commands", task)
        self.assertIn("verification_artifact", task)
        self.assertEqual(task["report_card"], "report_card.md")
        self.assertTrue(task["closeout_verification"]["report_card"]["ok"])
        self.assertEqual(
            task["closeout_evidence_contract"]["version"],
            "P8_CLOSEOUT_EVIDENCE_CONTRACT_v1",
        )

    def test_verify_json_failure_blocks_closeout_without_writing_state(self):
        before = self.write_tasks()
        output = self.root / "artifact.md"
        verify = self.root / "verify.json"
        output.write_text("# artifact\n", encoding="utf-8")
        verify.write_text('{"ok": false}\n', encoding="utf-8")

        result = self.run_complete("--output", "artifact.md", "--verify-json", "verify.json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("G-CLOSEOUT verify-json FAILED", result.stdout)
        self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)

    def test_verify_json_pass_allows_closeout(self):
        self.write_tasks()
        output = self.root / "artifact.md"
        verify = self.root / "verify.json"
        output.write_text("# artifact\n", encoding="utf-8")
        verify.write_text('{"status": "PASS"}\n', encoding="utf-8")

        result = self.run_complete("--output", "artifact.md", "--verify-json", "verify.json")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        task = self.read_task()
        self.assertEqual(task["status"], "completed")
        self.assertTrue(task["closeout_verification"]["verify_json"]["ok"])

    def test_verification_artifact_records_contract_evidence(self):
        self.write_tasks()
        output = self.root / "artifact.md"
        evidence = self.root / "mmi" / "project_brain" / "status" / "verify" / "gate-task.json"
        evidence.parent.mkdir(parents=True)
        output.write_text("# artifact\n", encoding="utf-8")
        evidence.write_text('{"ok": true, "check": "fixture"}\n', encoding="utf-8")

        result = self.run_complete(
            "--output",
            "artifact.md",
            "--verification-artifact",
            "mmi/project_brain/status/verify/gate-task.json",
            "--sign-off",
            "PASS WITH REVISIONS",
            "--sign-off-tier",
            "Matt",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        task = self.read_task()
        self.assertEqual(task["sign_off"], "PASS WITH REVISIONS")
        self.assertEqual(task["sign_off_tier"], "Matt")
        self.assertTrue(task["closeout_verification"]["verification_artifact"]["ok"])
        self.assertEqual(
            task["verification_artifact"],
            "mmi/project_brain/status/verify/gate-task.json",
        )
        self.assertTrue(
            any(command["label"] == "closeout verification artifact" for command in task["verification_commands"])
        )

    def test_bad_verification_artifact_blocks_without_writing_state(self):
        before = self.write_tasks()
        output = self.root / "artifact.md"
        evidence = self.root / "bad.txt"
        output.write_text("# artifact\n", encoding="utf-8")
        evidence.write_text("not json\n", encoding="utf-8")

        result = self.run_complete(
            "--output",
            "artifact.md",
            "--verification-artifact",
            "bad.txt",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verification-artifact FAILED", result.stdout)
        self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)

    def test_grade_math_conflict_blocks_closeout_without_writing_state(self):
        before = self.write_tasks()
        output = self.root / "artifact.md"
        output.write_text("# artifact\n", encoding="utf-8")
        bad_card = self.write_report_card(grade="B", critical="law compliance = 3, evidence discipline = 2")

        result = subprocess.run(
            [
                sys.executable,
                str(self.scripts / "complete_task.py"),
                "gate-task",
                "--by",
                "test",
                "--summary",
                "test summary",
                "--output",
                "artifact.md",
                "--report-card",
                str(bad_card.relative_to(self.root)),
                "--no-seed",
            ],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("G-REPORT-CARD closeout verification FAILED", result.stdout)
        self.assertIn("GRADE_MATH_CONFLICT", result.stdout)
        self.assertEqual(json.loads(self.tasks_path.read_text(encoding="utf-8")), before)


if __name__ == "__main__":
    unittest.main()
