#!/usr/bin/env python3
"""Acceptance tests for MMI Crew Chain Mode A terminal runner."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_crew_chain.py")

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

CHAIN_SECTION_ORDER = (
    "section: 1 DISPATCHER",
    "section: 2 ESTIMATOR",
    "section: 3 ARCHITECT",
    "section: 4 SUPERINTENDENT",
    "section: 5 PROJECT_MANAGER",
    "section: 6 MATT_ADVISORY_SUMMARY",
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_chain(
    candidate: str = "#47",
    plain: bool = False,
) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH, "--candidate", candidate]
    if plain:
        cmd.append("--plain")
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


class TestMmiCrewChainModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_47_emits_crew_chain_report(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("MMI_CREW_CHAIN_REPORT"))

    def test_report_order_dispatcher_to_pm(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        positions = [out.index(section) for section in CHAIN_SECTION_ORDER]
        self.assertEqual(positions, sorted(positions))

    def test_47_includes_architect_blueprint(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        self.assertIn("section: 3 ARCHITECT", out)
        self.assertIn("crew_status: BLUEPRINT", out)

    def test_47_includes_superintendent_matches(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        self.assertIn("section: 4 SUPERINTENDENT", out)
        self.assertIn("MATCHES_BLUEPRINT", out)

    def test_47_includes_pm_proceed(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        self.assertIn("section: 5 PROJECT_MANAGER", out)
        self.assertIn("PROCEED_FOR_MATT_REVIEW", out)

    def test_47_summary_no_autonomous_matt_authority(self):
        code, out, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        self.assertIn("section: 6 MATT_ADVISORY_SUMMARY", out)
        self.assertIn("No autonomous next action is taken", out)
        self.assertIn("Matt remains authority", out)

    def test_missing_candidate_insufficient(self):
        code, out, _ = _run_chain("#99")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_RUN_CHAIN"))
        self.assertIn("unknown_candidate", out)

    def test_read_only_no_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        code, _, _ = _run_chain("#47")
        self.assertEqual(code, 0)
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_forbidden_conclusion_tokens_absent(self):
        for candidate in ("#47", "#99"):
            _, out, _ = _run_chain(candidate)
            for line in out.splitlines():
                stripped = line.strip()
                if stripped in FORBIDDEN_CONCLUSIONS:
                    self.fail(f"forbidden conclusion in {candidate}: {stripped}")
                if stripped.startswith("VERDICT:"):
                    self.fail(f"forbidden VERDICT in {candidate}")

    def test_terminal_command_works(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--candidate", "#47"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("MMI_CREW_CHAIN_REPORT"))
        self.assertIn("dispatcher_mode: ALL_CLEAR", proc.stdout)


if __name__ == "__main__":
    unittest.main()
