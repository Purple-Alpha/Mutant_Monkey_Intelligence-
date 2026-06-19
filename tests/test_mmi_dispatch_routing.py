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
        self.assertIn(
            pairs["MODE"],
            ("DELEGATE", "PROJECT_DIRECTION_RESEARCH", "ALL_CLEAR"),
        )
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
        elif pairs["MODE"] == "PROJECT_DIRECTION_RESEARCH":
            for field in (
                "WHY_QUEUE_IS_EMPTY",
                "DIRECTION_SCOREBOARD",
                "RECOMMENDED_DIRECTION",
                "RECOMMENDED_NEXT_ACTION",
                "ASSIGNED_WORKER_OR_LANE",
                "WHY_THIS_DIRECTION",
                "DECISION_SCORE",
                "LOWER_SCORE_ALTERNATIVES",
                "SCORE_RUBRIC",
                "SOURCE_EVIDENCE",
                "OWNER_DECISION_NEEDED",
                "NEXT_GATE",
            ):
                self.assertIn(field, pairs, msg=f"missing {field}")

    def test_project_direction_scoring_when_queue_empty(self):
        tasks = self.mmi.collect_delegation_tasks()
        if tasks:
            self.skipTest("delegation queue not empty in this snapshot")
        directions = self.mmi.collect_project_direction_candidates()
        self.assertGreaterEqual(len(directions), 3)
        top = directions[0]
        self.assertGreater(self.mmi._direction_total(top["axis_scores"]), 0)
        names = [d["name"] for d in directions]
        if self.mmi._case_timeline_contract_direction_eligible():
            self.assertIn("Draft #47 Case Timeline Agent Design Contract", names)
            self.assertIn("#47", top["name"])
        _, lines = self.mmi._build_delegation_lines("test")
        pairs = dict(lines)
        self.assertEqual(pairs["MODE"], "PROJECT_DIRECTION_RESEARCH")
        self.assertNotIn("Matt supplies next evidence", pairs.get("CANDIDATES_NOT_AUTHORIZATION", ""))

    def test_case_timeline_contract_direction_scored_when_unblocked(self):
        if not self.mmi._case_timeline_contract_direction_eligible():
            self.skipTest("#47 not in NEEDS_SIGNED_CONTRACT / #48 not GOVERNED_AGENT")
        directions = self.mmi.collect_project_direction_candidates()
        case_timeline = next(
            d for d in directions if d["name"].startswith("Draft #47 Case Timeline")
        )
        self.assertEqual(self.mmi._direction_total(case_timeline["axis_scores"]), 16)
        self.assertEqual(len(case_timeline["axis_scores"]), 10)

    def test_direction_rubric_has_ten_axes(self):
        self.assertEqual(len(self.mmi.DIRECTION_RUBRIC_AXES), 10)
        sample = self.mmi.collect_project_direction_candidates()[0]["axis_scores"]
        self.assertEqual(len(sample), 10)
        self.assertLessEqual(self.mmi._direction_total(sample), 20)

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
