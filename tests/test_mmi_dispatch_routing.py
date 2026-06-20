#!/usr/bin/env python3
"""Unit tests for MMI dispatcher routing doctrine."""
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

    def test_delegate_mode_includes_scoring_fields(self):
        _, lines = self.mmi._build_delegation_lines("test")
        pairs = dict(lines)
        self.assertIn(pairs["MODE"], ("DELEGATE", "ALL_CLEAR"))
        self.assertIn("CURRENT_PROJECT_TRUTH", pairs)
        self.assertIn("REQUIRED_UPDATE_AFTER_COMPLETION", pairs)
        self.assertEqual(pairs["OPERATOR_NAMES_TARGET"], "Matt")
        self.assertEqual(pairs["MMI_ASSIGNS_LANE"], "YES")
        if pairs["MODE"] == "DELEGATE":
            self.assertIn("TASK_SCOREBOARD", pairs)
            self.assertIn("NEXT_DELEGATED_TASK", pairs)
            self.assertIn("TASK_SCORE", pairs)
            self.assertIn("WHY_THIS_TASK", pairs)
            self.assertIn("LOWER_SCORE_ALTERNATIVES", pairs)
            self.assertNotEqual(pairs["ASSIGNED_TO"], "Matt")
        else:
            self.assertEqual(pairs["MODE"], "ALL_CLEAR")
            self.assertIn("WHY_QUEUE_IS_EMPTY", pairs)
            self.assertIn("CANDIDATES_NOT_AUTHORIZATION", pairs)
            self.assertEqual(pairs["BUILD_AUTHORIZATION_IMPLIED"], "NO")

    def test_all_clear_when_queue_empty(self):
        tasks = self.mmi.collect_delegation_tasks()
        if tasks:
            self.skipTest("delegation queue not empty in this snapshot")
        _, lines = self.mmi._build_delegation_lines("test")
        pairs = dict(lines)
        self.assertEqual(pairs["MODE"], "ALL_CLEAR")
        self.assertNotIn("RECOMMENDED_DIRECTION", pairs)
        self.assertNotIn("DIRECTION_SCOREBOARD", pairs)
        self.assertNotIn("DECISION_SCORE", pairs)

    def test_project_direction_scorer_removed_from_dispatcher(self):
        self.assertFalse(hasattr(self.mmi, "collect_project_direction_candidates"))
        self.assertFalse(hasattr(self.mmi, "_build_project_direction_lines"))
        self.assertFalse(hasattr(self.mmi, "DIRECTION_RUBRIC_AXES"))

    def test_build_route_empty_queue_is_all_clear_not_direction_research(self):
        tasks = self.mmi.collect_delegation_tasks()
        if tasks:
            self.skipTest("delegation queue not empty in this snapshot")
        if self.mmi.get_awaiting_audit() or self.mmi.get_signed_unbuilt():
            self.skipTest(
                "scoreboard has SIGNED_UNBUILT/AWAITING_AUDIT lifecycle feedstock"
            )
        _, lines = self.mmi.build_route_lines()
        pairs = dict(lines)
        self.assertEqual(pairs["MODE"], "ALL_CLEAR")
        self.assertNotIn("RECOMMENDED_DIRECTION", pairs)
        self.assertEqual(pairs.get("BUILD_AUTHORIZATION_IMPLIED"), "NO")

    def test_intake_batch_ranks_above_external_lane(self):
        tasks = self.mmi.collect_delegation_tasks()
        if len(tasks) < 2:
            self.skipTest("need multiple delegation tasks in this repo snapshot")
        classifications = [t["classification"] for t in tasks]
        if (
            "INTAKE_CLASSIFY_BATCH" in classifications
            and "EXTERNAL_LANE" in classifications
        ):
            intake = next(t for t in tasks if t["classification"] == "INTAKE_CLASSIFY_BATCH")
            external = next(t for t in tasks if t["classification"] == "EXTERNAL_LANE")
            self.assertGreater(intake["score"], external["score"])
            self.assertEqual(tasks[0]["classification"], "INTAKE_CLASSIFY_BATCH")

    def test_tid_is_external_lane_not_scoreboard_row(self):
        tasks = self.mmi.collect_delegation_tasks()
        names = [t["name"] for t in tasks]
        if not any("Threat Intelligence" in n for n in names):
            self.skipTest("Threat Intelligence task not surfaced")
        tid = next(t for t in tasks if "Threat Intelligence" in t["name"])
        self.assertEqual(tid["classification"], "EXTERNAL_LANE")
        off_board = self.mmi.get_off_scoreboard_signed_contracts()
        self.assertEqual(off_board, [])

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
