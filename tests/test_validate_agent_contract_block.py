#!/usr/bin/env python3
"""Tests for Step 00 Agent Design Contract §3 validator."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "validate_agent_contract_block.py")
CONTRACT_71 = os.path.join(
    REPO,
    "4. Product_Roadmap",
    "Token_Usage_Tracker_Agent_Design_Contract_Deep_Dive.md",
)


def _load():
    spec = importlib.util.spec_from_file_location("validate_agent_contract_block", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["validate_agent_contract_block"] = mod
    spec.loader.exec_module(mod)
    return mod


def _run(path: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, SCRIPT, path],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ValidateAgentContractBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()
        cls.root = cls.mod._repo_root()
        cls.required = cls.mod.load_required_fields(cls.root / cls.mod.TEMPLATE_REL)

    def test_template_field_count_matches_section_three(self):
        self.assertGreaterEqual(len(self.required), 26)
        self.assertIn("Agent name", self.required)
        self.assertIn("Build Authorization dependency", self.required)

    def test_broken_eleven_field_table_fails(self):
        snippet = """
## Agent Design Contract block

| Field | Value |
|---|---|
| Component name | Token Usage Tracker |
| Swarm inventory ID | #71 |
| Canonical layer | 6 |
| Authority level | infra |
| Stage posture | Stage A |
| Evidence Stage (current) | ES1 |
| Role | ledger |
| Boundary | reporting only |
| Inputs | records |
| Outputs | summaries |
| Explicit non-authorities | no gate |
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(snippet)
            path = handle.name
        try:
            result = self.mod.validate_contract(self.root / path, self.required)
            self.assertFalse(result.passed)
            self.assertGreater(len(result.missing_fields), 0)
        finally:
            os.unlink(path)

    def test_token_usage_tracker_contract_passes_after_repair(self):
        result = self.mod.validate_contract(self.root / CONTRACT_71, self.required)
        self.assertTrue(result.passed, msg=", ".join(result.missing_fields))
        self.assertEqual(result.found_count, result.required_count)

    def test_cli_json_exit_codes(self):
        code, _, _ = _run(CONTRACT_71)
        self.assertEqual(code, 0)
        proc = subprocess.run(
            [sys.executable, SCRIPT, CONTRACT_71, "--json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("contract_fields_found", proc.stdout)


if __name__ == "__main__":
    unittest.main()
