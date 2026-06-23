#!/usr/bin/env python3
"""Tests for Next-Action Rubric read-only scorer."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "mmi_next_action_rubric.py")

FORBIDDEN = frozenset(
    {"RECOMMENDED", "SELECTED", "NEXT_DECIDED", "AUTHORIZED", "BUILD_AUTHORIZED"}
)


def _load():
    spec = importlib.util.spec_from_file_location("mmi_next_action_rubric", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_next_action_rubric"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiNextActionRubric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def test_stdout_envelope(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("SCORED_NEXT_ACTIONS"))
        self.assertIn("TOTAL:", proc.stdout)
        self.assertIn("hold_all_clear", proc.stdout)

    def test_candidate_count_between_3_and_7(self):
        scored = self.mod.analyze(self.mod._repo_root())
        self.assertGreaterEqual(len(scored), 3)
        self.assertLessEqual(len(scored), 7)

    def test_forbidden_tokens_absent(self):
        scored = self.mod.analyze(self.mod._repo_root())
        out = self.mod.format_stdout(scored)
        for token in FORBIDDEN:
            self.assertNotIn(token, out)

    def test_hold_candidate_scored_per_d19(self):
        scored = self.mod.analyze(self.mod._repo_root())
        hold = next(
            (item for item in scored if item.candidate.action_id == "hold_all_clear"),
            None,
        )
        self.assertIsNotNone(hold)
        self.assertEqual(hold.axes.leverage, 0)
        self.assertEqual(hold.axes.future_cost, 1)
        self.assertEqual(hold.axes.reversibility, 2)

    def test_signed_spine_contract_2_excludes_draft_candidate(self):
        root = self.mod._repo_root()
        if not self.mod._spine_contract_signed(root, "#2"):
            self.skipTest("#2 contract not §11 signed on disk")
        candidates = self.mod.generate_candidates(root)
        ids = {c.action_id for c in candidates}
        self.assertNotIn("draft_contract_2", ids)
        self.assertIn("build_auth_#2", ids)


if __name__ == "__main__":
    unittest.main()
