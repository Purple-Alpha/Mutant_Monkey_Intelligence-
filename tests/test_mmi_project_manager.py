#!/usr/bin/env python3
"""Acceptance tests for MMI Project Manager Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_project_manager.py")
PM_FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_project_manager")
SUPERINTENDENT_FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_superintendent")

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
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
        "GATED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "PASS",
        "FAIL",
        "NEXT_DECIDED",
        "AUTONOMOUSLY_SELECTED",
    }
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_pm(
    candidate: str = "#47",
    fixture_name: str | None = None,
) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH, "--candidate", candidate]
    if fixture_name:
        cmd.extend(["--root", os.path.join(PM_FIXTURES, fixture_name)])
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_project_manager", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_project_manager"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiProjectManagerModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_47_emits_report(self):
        code, out, _ = _run_pm("#47")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("PROJECT_MANAGER_REPORT"))

    def test_47_proceed_when_crew_aligned(self):
        code, out, _ = _run_pm("#47")
        self.assertEqual(code, 0)
        self.assertIn("advisory_result: PROCEED_FOR_MATT_REVIEW", out)
        self.assertIn("architect_status: BLUEPRINT", out)
        self.assertIn("superintendent_status: MATCHES_BLUEPRINT", out)
        self.assertIn("dispatcher_mode: ALL_CLEAR", out)

    def test_missing_candidate_insufficient(self):
        code, out, _ = _run_pm("#99")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_SUMMARIZE"))
        self.assertIn("unknown_candidate", out)

    def test_hold_when_evidence_missing(self):
        code, out, _ = _run_pm("#47", fixture_name="hold_missing_contract")
        self.assertIn(
            "advisory_result: HOLD_FOR_MISSING_INPUTS",
            out,
        )
        self.assertIn("architect_cannot_blueprint", out)

    def test_revise_when_superintendent_deviates(self):
        code, out, _ = _run_pm("#47", fixture_name="deviates_impl")
        self.assertEqual(code, 0)
        self.assertIn("advisory_result: REVISE_BEFORE_MATT_REVIEW", out)
        self.assertIn("DEVIATES_FROM_BLUEPRINT", out)

    def test_missing_gate_prevents_proceed(self):
        code, out, _ = _run_pm("#47", fixture_name="gated_missing_gate")
        self.assertNotIn("advisory_result: PROCEED_FOR_MATT_REVIEW", out)
        self.assertIn("HOLD_FOR_MISSING_INPUTS", out)

    def test_blocked_gate_prevents_proceed(self):
        code, out, _ = _run_pm("#47", fixture_name="gate_blocked")
        self.assertNotIn("advisory_result: PROCEED_FOR_MATT_REVIEW", out)
        self.assertIn("REVISE_BEFORE_MATT_REVIEW", out)

    def test_boundary_no_autonomous_authority(self):
        code, out, _ = _run_pm("#47")
        self.assertEqual(code, 0)
        self.assertIn("no autonomous", out.lower())
        self.assertIn("AUTH-5 blocked", out)
        self.assertIn("not GOVERNED_AGENT", out)

    def test_read_only_no_blueprint_of_record(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        code, _, _ = _run_pm("#47")
        self.assertEqual(code, 0)
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_no_scoreboard_registry_dispatcher_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_pm("#47")
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)
        self.assertNotIn("import mmi_dispatch", self.source)
        self.assertNotRegex(self.source, r"write_text|open\([^)]*,\s*['\"]w")

    def test_forbidden_conclusion_tokens_absent(self):
        for candidate in ("#47", "#99"):
            _, out, _ = _run_pm(candidate)
            for line in out.splitlines():
                stripped = line.strip()
                if stripped in FORBIDDEN_CONCLUSIONS:
                    self.fail(f"forbidden conclusion in {candidate}: {stripped}")
                if stripped.startswith("advisory_result:"):
                    value = stripped.split(":", 1)[1].strip()
                    if value in FORBIDDEN_CONCLUSIONS:
                        self.fail(f"forbidden advisory_result in {candidate}: {value}")


if __name__ == "__main__":
    unittest.main()
