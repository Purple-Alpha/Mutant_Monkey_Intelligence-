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

    def test_analyze_post_stage_c_d02_hold_after_dec157(self):
        position = self.mod.analyze(self.mod._repo_root())
        self.assertTrue(position.active)
        self.assertEqual(position.stage_id, "post_stage_c")
        self.assertIsNotNone(position.next_waypoint)
        self.assertEqual(position.next_waypoint.waypoint_id, "d02")
        self.assertEqual(position.next_waypoint.hand_to, "Matt")
        self.assertTrue(position.next_waypoint.requires_matt_escalation)
        self.assertEqual(len(position.completed_waypoints), 1)
        self.assertEqual(position.completed_waypoints[0].waypoint_id, "d01")

    def test_decision_log_match_requires_entry_line_not_mention(self):
        log = self.mod._read_text(self.mod._repo_root() / self.mod.DECISION_LOG_REL)
        self.assertIn("MMI-DEC-157", log)
        position = self.mod.analyze(self.mod._repo_root())
        self.assertEqual(position.next_waypoint.waypoint_id, "d02")

    def test_render_stdout_envelope(self):
        position = self.mod.analyze(self.mod._repo_root())
        out = self.mod.render_stdout(position, self.mod._repo_root())
        self.assertIn(self.mod.ENVELOPE, out)
        self.assertIn("stage_id: post_stage_c", out)
        self.assertIn("next_waypoint:", out)
        self.assertIn("d02", out)

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
        self.assertIn("MISSION_MAP_POSITION", proc.stdout)
        self.assertIn("stage_id: post_stage_c", proc.stdout)


if __name__ == "__main__":
    unittest.main()
