#!/usr/bin/env python3
"""Tests for MMI Active Lane Console Mode A."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "mmi_active_lanes.py")
PMV_SCRIPT = os.path.join(REPO, "scripts", "mmi_pm_voice.py")
FIXTURE = os.path.join(REPO, "tests", "fixtures", "mmi_active_lanes", "minimal_repo")


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_active_lanes", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_active_lanes"] = module
    spec.loader.exec_module(module)
    return module


class ActiveLaneConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_five_lanes_on_live_repo(self):
        lanes = self.mod.gather_lanes(self.mod._repo_root())
        self.assertEqual(len(lanes), 5)
        self.assertEqual([lane.lane for lane in lanes], list(self.mod.LANES))

    def test_each_lane_has_required_fields(self):
        for view in self.mod.gather_lanes(self.mod._repo_root()):
            self.assertTrue(view.active)
            self.assertIn(view.state, self.mod.LANE_STATES)
            self.assertTrue(view.evidence)
            self.assertTrue(view.next_action)
            self.assertTrue(view.actor)
            self.assertTrue(view.authority)

    def test_build_lane_blocked_without_signed_unbuilt(self):
        build = next(
            lane for lane in self.mod.gather_lanes(self.mod._repo_root()) if lane.lane == "BUILD"
        )
        self.assertEqual(build.state, "BLOCKED")
        self.assertEqual(build.authority, self.mod.BUILD_FORBIDDEN)

    def test_research_lane_mesh_closeout(self):
        research = next(
            lane
            for lane in self.mod.gather_lanes(self.mod._repo_root())
            if lane.lane == "RESEARCH"
        )
        self.assertIn("MMI-DEC-131", research.active)
        self.assertEqual(research.state, "COMPLETED")

    def test_design_lane_mesh_contract(self):
        design = next(
            lane for lane in self.mod.gather_lanes(self.mod._repo_root()) if lane.lane == "DESIGN"
        )
        self.assertIn("MMI-DEC-140", design.active)
        self.assertEqual(design.state, "COMPLETED")
        self.assertIn("§13", design.next_action)
        self.assertNotIn("Review Immune Federation Mesh contract addendum", design.next_action)

    def test_research_lane_no_fork_after_ifm_signed(self):
        research = next(
            lane
            for lane in self.mod.gather_lanes(self.mod._repo_root())
            if lane.lane == "RESEARCH"
        )
        self.assertEqual(research.state, "COMPLETED")
        self.assertIn("MMI-DEC-140", research.next_action)
        self.assertNotIn("advance to DESIGN review", research.next_action)

    def test_design_lane_unsigned_draft_stays_ready_for_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "mmi" / "contracts").mkdir(parents=True)
            (root / "mmi").mkdir(parents=True)
            (root / "docs" / "mmi" / "contracts" / "004_immune_federation_mesh_contract.md").write_text(
                "CONTRACT_DRAFT\nNOT BUILD AUTHORIZED\n",
                encoding="utf-8",
            )
            (root / "mmi" / "MMI_DECISION_LOG.md").write_text(
                "MMI-DEC-134 | draft only\n",
                encoding="utf-8",
            )
            design = next(
                lane for lane in self.mod.gather_lanes(root) if lane.lane == "DESIGN"
            )
            self.assertEqual(design.state, "READY_FOR_REVIEW")
            self.assertIn("Matt §11 review", design.next_action)

    def test_pugh_forbidden_auto_build(self):
        pugh, risk = self.mod._classify_pugh("Auto-run build after research evidence appears", "BUILD")
        self.assertEqual(pugh, "-")
        self.assertIn("RISK_ALERT", risk)

    def test_pugh_positive_active_console(self):
        pugh, _ = self.mod._classify_pugh(
            "Use python3 scripts/mmi_active_lanes.py as default operator feed", "REVISE"
        )
        self.assertEqual(pugh, "+")

    def test_pugh_zero_hides_maintenance(self):
        pugh, _ = self.mod._classify_pugh("Run mmi_lane_board_sync.py and refresh ranked board", "REVISE")
        self.assertEqual(pugh, "0")

    def test_missing_evidence_graceful(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "MMI_CURRENT_STATE.md").write_text(
                "MODE: ALL_CLEAR\n0 SIGNED_UNBUILT, 0 AWAITING_AUDIT, 0 GATED\n",
                encoding="utf-8",
            )
            lanes = self.mod.gather_lanes(root)
            research = next(l for l in lanes if l.lane == "RESEARCH")
            self.assertEqual(research.state, "EVIDENCE_MISSING")
            self.assertEqual(research.evidence, "missing")

    def test_cli_stdout_envelope(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MMI ACTIVE LANES", proc.stdout)
        for lane in self.mod.LANES:
            self.assertIn(f"[{lane}]", proc.stdout)

    def test_pm_voice_lanes_flag(self):
        proc = subprocess.run(
            [sys.executable, PMV_SCRIPT],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MMI ACTIVE LANES", proc.stdout)
        self.assertNotIn("MMI_PM_VOICE", proc.stdout)

    def test_pm_voice_explicit_lanes_flag(self):
        proc = subprocess.run(
            [sys.executable, PMV_SCRIPT, "--lanes"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MMI ACTIVE LANES", proc.stdout)

    def test_does_not_mutate_immutable_paths(self):
        before = {
            rel: Path(REPO, rel).read_bytes()
            for rel in (
                "MMI_CURRENT_STATE.md",
                "mmi/MMI_DECISION_LOG.md",
                "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
            )
            if Path(REPO, rel).is_file()
        }
        subprocess.run([sys.executable, SCRIPT], cwd=REPO, check=False)
        for rel, content in before.items():
            self.assertEqual(Path(REPO, rel).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
