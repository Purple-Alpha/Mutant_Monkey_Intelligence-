#!/usr/bin/env python3
"""Acceptance tests for MMI Superintendent Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_superintendent.py")
ARCHITECT_FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_architect")
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
        "APPROVED",
        "AUTHORIZED",
        "BUILD_AUTHORIZED",
        "PROMOTED",
        "GATED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "PASS",
        "FAIL",
        "NEXT_DECIDED",
    }
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_superintendent(
    candidate: str = "#47",
    fixture_name: str | None = None,
    extra_args: list[str] | None = None,
) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH, "--candidate", candidate]
    if fixture_name:
        cmd.extend(["--root", os.path.join(SUPERINTENDENT_FIXTURES, fixture_name)])
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_superintendent", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_superintendent"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiSuperintendentModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_47_happy_path_emits_report(self):
        code, out, _ = _run_superintendent("#47")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("SUPERINTENDENT_REPORT"))

    def test_47_checks_cover_contract_blueprint_impl_tests_gate(self):
        code, out, _ = _run_superintendent("#47")
        self.assertEqual(code, 0)
        self.assertIn("contract_status: PRESENT", out)
        self.assertIn("blueprint_status: PRESENT", out)
        self.assertIn("case_timeline_agent.py", out)
        self.assertIn("test_case_timeline_agent.py", out)
        self.assertIn("id: contract_exists", out)
        self.assertIn("id: architect_blueprint", out)
        self.assertIn("gate_artifact:", out)
        self.assertIn("case_timeline_20260620T233212Z.md", out)

    def test_47_matches_blueprint_when_files_exist(self):
        code, out, _ = _run_superintendent("#47")
        self.assertEqual(code, 0)
        self.assertIn("advisory_result: MATCHES_BLUEPRINT", out)
        self.assertIn("summary:", out)
        self.assertIn("deviations: 0", out)

    def test_missing_impl_deviates(self):
        code, out, _ = _run_superintendent("#47", fixture_name="missing_impl")
        self.assertEqual(code, 0)
        self.assertTrue(
            out.startswith("SUPERINTENDENT_REPORT")
            or out.startswith("INPUTS_INSUFFICIENT_CANNOT_CHECK"),
        )
        self.assertIn(
            "advisory_result: DEVIATES_FROM_BLUEPRINT",
            out,
        )
        self.assertIn("case_timeline_agent.py", out)

    def test_missing_build_conditions_insufficient(self):
        cmd = [
            sys.executable,
            SCRIPT_PATH,
            "--candidate",
            "#52",
            "--root",
            os.path.join(ARCHITECT_FIXTURES, "missing_build_conditions"),
        ]
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertTrue(
            proc.stdout.startswith("INPUTS_INSUFFICIENT_CANNOT_CHECK"),
        )
        self.assertIn("missing_build_conditions_section", proc.stdout)
        self.assertIn("advisory_result: INPUTS_INSUFFICIENT", proc.stdout)

    def test_candidate_specific_no_bleed(self):
        code, out, _ = _run_superintendent("#47")
        self.assertEqual(code, 0)
        self.assertNotIn("Plain-English Explanation", out)
        self.assertNotIn("tests.test_client_facing_rubric", out)
        self.assertIn("id: blueprint_candidate_specific", out)

        cmd = [
            sys.executable,
            SCRIPT_PATH,
            "--candidate",
            "#52",
            "--root",
            os.path.join(ARCHITECT_FIXTURES, "complete"),
        ]
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("test_case_timeline_agent", proc.stdout)

    def test_read_only_no_blueprint_of_record(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        code, _, _ = _run_superintendent("#47")
        self.assertEqual(code, 0)
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_no_scoreboard_registry_dispatcher_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_superintendent("#47")
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)
        self.assertNotIn("import mmi_dispatch", self.source)
        self.assertNotRegex(
            self.source,
            r"write_text|open\([^)]*,\s*['\"]w",
        )

    def test_forbidden_conclusion_tokens_absent(self):
        for candidate in ("#47", "#52", "#99"):
            code, out, _ = _run_superintendent(candidate)
            for line in out.splitlines():
                stripped = line.strip()
                if stripped in FORBIDDEN_CONCLUSIONS:
                    self.fail(f"forbidden conclusion in {candidate}: {stripped}")
                if stripped.startswith("advisory_result:"):
                    value = stripped.split(":", 1)[1].strip()
                    if value in FORBIDDEN_CONCLUSIONS:
                        self.fail(f"forbidden advisory_result in {candidate}: {value}")
                if stripped.startswith("VERDICT:"):
                    self.fail(f"forbidden VERDICT in {candidate}")

    def test_unknown_candidate_insufficient(self):
        code, out, _ = _run_superintendent("#99")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_CHECK"))
        self.assertIn("unknown_candidate", out)
        self.assertIn("advisory_result: INPUTS_INSUFFICIENT", out)


if __name__ == "__main__":
    unittest.main()
