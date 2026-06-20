#!/usr/bin/env python3
"""Acceptance tests T1–T11 for MMI Architect Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_architect.py")
DISPATCH_PATH = os.path.join(REPO, "scripts", "mmi_dispatch.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_architect")

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "mmi/MMI_TASK_REGISTRY.yaml",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
]

FORBIDDEN_TOOL_VERDICTS = frozenset(
    {
        "SELECTED",
        "AUTHORIZED",
        "APPROVED",
        "RECOMMENDED",
        "BUILD_AUTHORIZED",
        "COMPLETE",
        "SIGNED",
        "VERIFIED",
        "PASS",
        "FAIL",
        "PROMOTED",
        "NEXT_DECIDED",
    }
)

SECTION_PARTS = (
    "section: 1 CANDIDATE",
    "section: 2 SOURCE MANIFEST",
    "section: 3 BUILD CONDITIONS",
    "section: 4 FLOW CONTRACT",
    "section: 5 OUT OF SCOPE",
    "section: 6 EVIDENCE REQUIREMENTS",
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_architect(
    fixture_name: str | None = None,
    extra_args: list[str] | None = None,
) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH, "--candidate", "#52"]
    if fixture_name:
        cmd.extend(["--root", os.path.join(FIXTURES, fixture_name)])
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
    spec = importlib.util.spec_from_file_location("mmi_architect", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_architect"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiArchitectModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_t1_selected_only(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("BLUEPRINT"))
        self.assertIn("candidate_id: #52", out)
        self.assertIn("selected_candidate: #52", out)
        self.assertNotRegex(out, r"candidate_id: #1\b")
        self.assertNotRegex(out, r"candidate_id: #3\b")
        self.assertNotIn("selected_candidate: #1", out)
        self.assertNotIn("selected_candidate: #3", out)

    def test_t2_missing_selected_candidate_source(self):
        code, out, _ = _run_architect("missing_contract")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"))
        self.assertIn("missing_source:", out)
        self.assertIn("Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md", out)

    def test_t3_no_invention_missing_flow(self):
        code, out, _ = _run_architect("missing_flow")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"))
        self.assertTrue(
            any(token in out for token in ("missing_flow_contract_field:", "gaps:")),
        )

    def test_t4_blueprint_is_checkable(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        for line in out.splitlines():
            if line.startswith("condition:"):
                payload = line.split(":", 1)[1]
                self.assertIn("CHECK:", payload)
        self.assertIn("output_location:", out)
        self.assertIn("downstream_consumer:", out)

    def test_t5_flow_contract_required(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        self.assertIn("section: 4 FLOW CONTRACT", out)
        for field in (
            "output_location:",
            "output_format:",
            "downstream_consumer:",
            "consumer_usage:",
        ):
            self.assertIn(field, out)

    def test_t6_out_of_scope_carried(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        self.assertIn("section: 5 OUT OF SCOPE", out)
        self.assertIn("boundary:", out)
        self.assertIn("No replacement of existing `risk_score`", out)

        code2, out2, _ = _run_architect("missing_out_of_scope")
        self.assertEqual(code2, 2)
        self.assertIn("missing_out_of_scope_source", out2)

    def test_t7_evidence_requirements(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        self.assertIn("section: 6 EVIDENCE REQUIREMENTS", out)
        self.assertIn("WORKER_COMPLETION_PACKET", out)
        self.assertIn("requirement:", out)

    def test_t8_forbidden_tokens(self):
        for fixture in ("complete", "missing_contract", "missing_flow"):
            _, out, _ = _run_architect(fixture)
            for line in out.splitlines():
                stripped = line.strip()
                if stripped in FORBIDDEN_TOOL_VERDICTS:
                    self.fail(f"forbidden token line in {fixture}: {stripped}")
                if stripped.startswith("VERDICT:"):
                    self.fail(f"forbidden VERDICT line in {fixture}")

    def test_t9_zero_writes(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        code, _, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_t10_no_dispatcher_registry_scoreboard_coupling(self):
        self.assertNotIn("import mmi_dispatch", self.source)
        self.assertNotIn("from mmi_dispatch", self.source)
        self.assertNotIn("import subprocess", self.source)
        self.assertNotRegex(
            self.source,
            r"Blue_Team_Swarm_70_Agent_Scoreboard\.md|MMI_TASK_REGISTRY\.yaml",
        )

    def test_t11_no_research_note_authority(self):
        code, out, _ = _run_architect("research_authority")
        self.assertEqual(code, 2)
        self.assertIn("research_note_authority_forbidden", out)


class TestMmiArchitectEnvelope(unittest.TestCase):
    def test_blueprint_has_all_section_parts(self):
        code, out, _ = _run_architect("complete")
        self.assertEqual(code, 0)
        for part in SECTION_PARTS:
            self.assertIn(part, out)


if __name__ == "__main__":
    unittest.main()
