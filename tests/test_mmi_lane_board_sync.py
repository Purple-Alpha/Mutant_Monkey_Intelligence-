#!/usr/bin/env python3
"""Tests for ranked lane board sync."""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load():
    script = os.path.join(REPO, "scripts", "mmi_lane_board_sync.py")
    spec = importlib.util.spec_from_file_location("mmi_lane_board_sync", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_lane_board_sync"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiLaneBoardSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def test_writes_ranked_board_under_mmi(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agent_concepts").mkdir()
            (root / "mmi").mkdir()
            scoreboard = Path(REPO) / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
            bor = Path(REPO) / "mmi" / "BLUEPRINT_OF_RECORD.md"
            (root / "agent_concepts").joinpath(
                "Blue_Team_Swarm_70_Agent_Scoreboard.md"
            ).write_text(scoreboard.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "mmi" / "BLUEPRINT_OF_RECORD.md").write_text(
                bor.read_text(encoding="utf-8"), encoding="utf-8"
            )
            ranked_path, top_label, top_total = self.mod.sync(
                root, handshake=False
            )
            self.assertTrue(ranked_path.is_file())
            self.assertTrue(top_label)
            self.assertTrue(top_total)


if __name__ == "__main__":
    unittest.main()
