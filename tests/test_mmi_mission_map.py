#!/usr/bin/env python3
"""Tests for MMI chain-of-command mission map engine."""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "mmi_mission_map.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_mission_map", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_mission_map"] = module
    spec.loader.exec_module(module)
    return module


class MissionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_post_stage_c_breadth_rollout_complete(self):
        position = self.mod.analyze(self.mod._repo_root())
        self.assertTrue(position.active)
        self.assertTrue(position.all_stages_complete)
        log = self.mod._read_text(self.mod._repo_root() / self.mod.DECISION_LOG_REL)
        self.assertIn("MMI-DEC-182", log)
        self.assertIn("MMI-DEC-179", log)
        self.assertIn("MMI-DEC-181", log)

    def test_analyze_all_stages_complete_after_stage_c(self):
        position = self.mod.analyze(self.mod._repo_root())
        self.assertTrue(position.active)
        self.assertTrue(position.all_stages_complete)
        self.assertEqual(position.reason, "all stages complete per map markers")

    def test_decision_log_match_requires_entry_line_not_mention(self):
        log = self.mod._read_text(self.mod._repo_root() / self.mod.DECISION_LOG_REL)
        self.assertIn("MMI-DEC-150", log)
        position = self.mod.analyze(self.mod._repo_root())
        self.assertTrue(position.all_stages_complete)

    def test_render_stdout_all_stages_complete(self):
        position = self.mod.analyze(self.mod._repo_root())
        out = self.mod.render_stdout(position, self.mod._repo_root())
        self.assertIn("ALL_STAGES_COMPLETE", out)

    def test_cli_position(self):
        import subprocess

        proc = subprocess.run(
            [sys.executable, SCRIPT, "--position"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ALL_STAGES_COMPLETE", proc.stdout)


if __name__ == "__main__":
    unittest.main()
