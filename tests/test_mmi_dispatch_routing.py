#!/usr/bin/env python3
"""Unit tests for MMI dispatcher routing doctrine (operator decisions 2026-06-16)."""
import importlib.util
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISPATCH_PATH = os.path.join(REPO, "scripts", "mmi_dispatch.py")


def _load_dispatch():
    spec = importlib.util.spec_from_file_location("mmi_dispatch", DISPATCH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MmiDispatchRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mmi = _load_dispatch()

    def test_all_clear_includes_candidates_and_doctrine(self):
        _, lines = self.mmi._build_all_clear_lines("test")
        pairs = dict(lines)
        self.assertEqual(pairs["MODE"], "ALL_CLEAR")
        self.assertIn("CANDIDATES", pairs)
        self.assertIn("CANDIDATES_NOT_AUTHORIZATION", pairs)
        self.assertEqual(pairs["OPERATOR_NAMES_TARGET"], "Matt")
        self.assertEqual(pairs["MMI_ASSIGNS_LANE"], "YES")

    def test_off_scoreboard_contracts_labeled_not_build_ready(self):
        drift = self.mmi.get_off_scoreboard_signed_contracts()
        if not drift:
            self.skipTest("no off-scoreboard signed contracts in this repo snapshot")
        _, lines = self.mmi._build_all_clear_lines("test")
        text = dict(lines).get("CANDIDATES", "")
        self.assertIn("NEEDS_SCOREBOARD_ROW", text)
        self.assertIn("Build implied: NO", text)

    def test_synthetic_build_route_has_pre_build_codex(self):
        pairs = dict(self.mmi._synthetic_build_route())
        self.assertEqual(pairs["PRE_BUILD_REVIEW"], "Codex")
        self.assertIn("Codex", pairs["ASSIGNED_TO"])

    def test_synthetic_review_route_assigns_codex(self):
        pairs = dict(self.mmi._synthetic_review_route())
        self.assertEqual(pairs["ASSIGNED_TO"], "Codex")
        self.assertEqual(pairs["OPERATOR_ACTION_REQUIRED"], "NO")

    def test_doctrine_checks_pass(self):
        results = self.mmi.run_doctrine_checks()
        failures = [label for ok, label in results if not ok]
        self.assertEqual(failures, [], msg="; ".join(failures))


if __name__ == "__main__":
    unittest.main()
