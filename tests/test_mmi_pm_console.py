#!/usr/bin/env python3
"""Acceptance tests for MMI PM Console Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_pm_console.py")
NEXT_LANE_PATH = os.path.join(REPO, "scripts", "mmi_next_lane.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_pm_console")

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
    "MASTER_INDEX.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "mmi/MMI_TASK_REGISTRY.yaml",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
    "mmi/BLUEPRINT_OF_RECORD.md",
]

FORBIDDEN_CONCLUSIONS = frozenset(
    {
        "AUTHORIZED",
        "APPROVED",
        "BUILD_AUTHORIZED",
        "PROMOTED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "NEXT_DECIDED",
        "AUTONOMOUSLY_SELECTED",
    }
)

REQUIRED_SECTIONS = (
    "NOW:",
    "NEXT:",
    "BLOCKED:",
    "MATT_DECISION:",
    "ACTIVE_BLUEPRINT:",
    "DETAIL_COMMANDS:",
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_console(details: bool = False, plain: bool = False) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH]
    if details:
        cmd.append("--details")
    if plain:
        cmd.append("--plain")
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_pm_console", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_pm_console"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiPmConsoleModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_default_emits_pm_console(self):
        code, out, _ = _run_console()
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("MMI_PM_CONSOLE"))

    def test_required_sections_present(self):
        _, out, _ = _run_console()
        for section in REQUIRED_SECTIONS:
            self.assertIn(section, out)

    def test_default_shorter_than_next_lane(self):
        _, pm_out, _ = _run_console()
        proc = subprocess.run(
            [sys.executable, NEXT_LANE_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertLess(len(pm_out), len(proc.stdout))
        self.assertLessEqual(pm_out.count("candidate_id:"), 3)

    def test_reports_all_clear_no_active_build(self):
        _, out, _ = _run_console()
        self.assertIn("ALL_CLEAR", out)
        self.assertIn("No active build in progress", out)

    def test_reports_no_buildable_candidates(self):
        _, out, _ = _run_console()
        self.assertIn("No buildable candidates are currently available", out)

    def test_reports_missing_contract_blockers(self):
        _, out, _ = _run_console()
        self.assertIn("signed Agent Design Contracts are missing", out)

    def test_blueprint_status_fixtures(self):
        mod = self.mod
        current = mod._read_text(
            Path(os.path.join(FIXTURES, "blueprint_current", "mmi", "BLUEPRINT_OF_RECORD.md"))
        )
        status, _ = mod._parse_blueprint_status(current, True)
        self.assertEqual(status, "CURRENT_PLAN_PRESENT")

        draft = mod._read_text(
            Path(os.path.join(FIXTURES, "blueprint_draft", "mmi", "BLUEPRINT_OF_RECORD.md"))
        )
        status, _ = mod._parse_blueprint_status(draft, True)
        self.assertEqual(status, "DRAFT_PLAN_PRESENT_NOT_ACTIVE")

        multiple = mod._read_text(
            Path(os.path.join(FIXTURES, "blueprint_multiple", "mmi", "BLUEPRINT_OF_RECORD.md"))
        )
        status, _ = mod._parse_blueprint_status(multiple, True)
        self.assertEqual(status, "MULTIPLE_CURRENT_PLANS_VIOLATION")

        status, _ = mod._parse_blueprint_status("", False)
        self.assertEqual(status, "BLUEPRINT_FILE_MISSING")

    def test_no_current_plan_on_live_placeholder(self):
        _, out, _ = _run_console()
        self.assertIn("NO_CURRENT_PLAN", out)

    def test_read_only_no_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_console()
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_forbidden_tokens_absent(self):
        _, out, _ = _run_console(details=True)
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_CONCLUSIONS:
                self.fail(f"forbidden conclusion: {stripped}")

    def test_terminal_command_works(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("MMI_PM_CONSOLE"))

    def test_details_mode_includes_context(self):
        _, out, _ = _run_console(details=True)
        self.assertIn("details:", out)
        self.assertIn("mmi_next_lane.py", out)
        self.assertIn("mmi_crew_chain.py", out)
        self.assertIn("buildable_count:", out)


if __name__ == "__main__":
    unittest.main()
