import tempfile
import unittest
from pathlib import Path

from scripts import mmi_verify


CHECKLIST_HEADER = """# Draft OPSEC checklist

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
"""


def row(item_id, cadence, state, last_done="", verify_method=""):
    return f"| {item_id} | control | PHISH | why | {cadence} | {state} | {last_done} | {verify_method} |\n"


class OpsecAmendHelperTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / "draft.md"

    def tearDown(self):
        self.temp.cleanup()

    def write_checklist(self, body):
        self.path.write_text(CHECKLIST_HEADER + body, encoding="utf-8")

    def test_amend_helper_allows_not_started_rows(self):
        self.write_checklist(
            row("OPSEC-4", "daily (habit)", "NOT_STARTED")
            + row("OPSEC-5", "one-time (habit, re-affirm quarterly)", "NOT_STARTED")
            + row("OPSEC-9", "one-time (habit, re-affirm quarterly)", "NOT_STARTED")
        )

        result = mmi_verify.opsec_amend_helper(self.path, live_path=None)

        self.assertEqual(result["decision"], "ALLOW_AMEND")
        self.assertTrue(result["ok"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["mutated_files"], [])

    def test_amend_helper_blocks_false_done_class(self):
        self.write_checklist(
            row("OPSEC-4", "daily (habit)", "DONE", "", "worksheet exists only")
            + row("OPSEC-5", "one-time (habit, re-affirm quarterly)", "DONE", "2026-06-30", "dry-run only")
            + row("OPSEC-9", "one-time (habit, re-affirm quarterly)", "NOT_STARTED")
        )

        result = mmi_verify.opsec_amend_helper(self.path, live_path=None)

        self.assertEqual(result["decision"], "BLOCK_AMEND")
        reasons = {item["reason"] for item in result["violations"]}
        self.assertIn("DONE without last_done", reasons)
        self.assertIn("DONE with worksheet-only verify_method", reasons)
        self.assertIn("DONE with dry-run-only verify_method", reasons)

    def test_amend_helper_blocks_stale_done(self):
        self.write_checklist(
            row("OPSEC-4", "daily (habit)", "DONE", "2000-01-01", "real weekly spot-check note")
            + row("OPSEC-5", "one-time (habit, re-affirm quarterly)", "NOT_STARTED")
            + row("OPSEC-9", "one-time (habit, re-affirm quarterly)", "NOT_STARTED")
        )

        result = mmi_verify.opsec_amend_helper(self.path, live_path=None)

        self.assertEqual(result["decision"], "BLOCK_AMEND")
        self.assertIn(
            "DONE with stale daily-habit last_done",
            {item["reason"] for item in result["violations"]},
        )


if __name__ == "__main__":
    unittest.main()
