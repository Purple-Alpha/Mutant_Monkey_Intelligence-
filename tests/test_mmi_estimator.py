#!/usr/bin/env python3
"""Acceptance tests T1–T34 for MMI Estimator Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_estimator.py")
DISPATCH_PATH = os.path.join(REPO, "scripts", "mmi_dispatch.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_estimator")

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

VERIFY_PASS = "drift: 0 BLOCK, 0 BLOCK-candidate, 0 WARN\nVERDICT: PASS"
VERIFY_ALL_CLEAR = (
    "current task: MODE: ALL_CLEAR\n"
    "              No delegable tasks in routing queue\n"
    "drift: 0 BLOCK, 2 BLOCK-candidate, 1 WARN\n"
    "VERDICT: PASS"
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_estimator(
    fixture_name: str | None = None,
    extra_args: list[str] | None = None,
) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH]
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
    spec = importlib.util.spec_from_file_location("mmi_estimator", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_estimator"] = module
    spec.loader.exec_module(module)
    return module


def _candidate_ids(stdout: str) -> list[str]:
    ids: list[str] = []
    in_scored = False
    for line in stdout.splitlines():
        if line.startswith(("SCORED_CANDIDATES", "SCORED_FEEDSTOCK")):
            in_scored = True
            continue
        if line.startswith(("BUILDABILITY_EXCLUSIONS", "NO_BUILDABLE_CANDIDATES", "ADVISORY_ONLY:")):
            in_scored = False
            continue
        if in_scored and line.startswith("candidate_id: "):
            ids.append(line.split(":", 1)[1].strip())
    return ids


class EstimatorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_t1_determinism(self):
        out1 = _run_estimator("clean")[1]
        out2 = _run_estimator("clean")[1]
        self.assertEqual(out1, out2)

    def test_t2_merged_excluded(self):
        _, out, _ = _run_estimator("clean")
        self.assertNotIn("#16", _candidate_ids(out))

    def test_t3_reclassify_excluded(self):
        _, out, _ = _run_estimator("clean")
        self.assertNotIn("#7", _candidate_ids(out))

    def test_t4_blockers_excluded(self):
        _, out, _ = _run_estimator("clean")
        self.assertNotIn("#18", _candidate_ids(out))

    def test_t5_depends_excluded(self):
        _, out, _ = _run_estimator("clean")
        self.assertNotIn("#50", _candidate_ids(out))

    def test_t6_cannot_score_missing(self):
        code, out, _ = _run_estimator("missing_scoreboard")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("STATE_INCOMPLETE_CANNOT_SCORE"))

    def test_t7_cannot_score_conflict(self):
        code, out, _ = _run_estimator("duplicate_id")
        self.assertEqual(code, 2)
        self.assertIn("conflicting_candidate_id", out)

    def test_t8_health_capped(self):
        cand = self.mod.Candidate(
            candidate_id="#99",
            source="scoreboard",
            name="Health Cap",
            runtime_status="DETECTOR_FUNCTION",
            blockers="",
            track="BREADTH",
            health_score=100,
        )
        result = self.mod._f6_health(cand, health_board_present=True)
        self.assertTrue(result.measured)
        self.assertIsNotNone(result.value)
        f6_contrib = result.value * self.mod.WEIGHTS["F6"] / 10
        self.assertLessEqual(f6_contrib, 5.0)

    def test_t9_readiness_ordering(self):
        scored, _, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        by_id = {s.candidate.candidate_id: s for s in scored}
        self.assertGreater(
            by_id["#200"].total_measured_score,
            by_id["#201"].total_measured_score,
        )

    def test_t10_weighted_sum(self):
        scored, _, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertTrue(scored)
        item = scored[0]
        expected = round(
            sum(
                item.factor_results[f"F{i}"].value * self.mod.WEIGHTS[f"F{i}"] / 10
                for i in range(1, 7)
                if item.factor_results[f"F{i}"].measured
                and item.factor_results[f"F{i}"].value is not None
            ),
            2,
        )
        self.assertEqual(item.total_measured_score, expected)

    def test_t11_zero_writes(self):
        digests_before = {p: _file_digest(p) for p in IMMUTABLE_PATHS}
        _run_estimator("clean", ["--verify-text", VERIFY_PASS])
        digests_after = {p: _file_digest(p) for p in IMMUTABLE_PATHS}
        self.assertEqual(digests_before, digests_after)

    def test_t12_no_forbidden_token(self):
        _, out, _ = _run_estimator("clean", ["--verify-text", VERIFY_PASS])
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_TOOL_VERDICTS:
                self.fail(f"forbidden tool verdict line: {stripped}")
            if stripped.startswith("VERDICT:"):
                self.fail(f"forbidden VERDICT envelope line: {stripped}")

    def test_t13_refresh(self):
        clean, _, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        refresh, _, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "refresh")),
            verify_text=VERIFY_PASS,
        )
        self.assertNotEqual(
            [s.total_measured_score for s in clean],
            [s.total_measured_score for s in refresh],
        )

    def test_t13_verify_block_cannot_score(self):
        _, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text="drift: 1 BLOCK, 0 WARN",
        )
        self.assertTrue(errors)

    def test_t14_signed_weights_match_contract_policy(self):
        expected = {"F1": 30, "F2": 25, "F3": 20, "F4": 10, "F5": 10, "F6": 5}
        self.assertEqual(self.mod.SIGNED_WEIGHTS_RECORD, expected)
        self.assertEqual(self.mod.WEIGHTS, self.mod.SIGNED_WEIGHTS_RECORD)

    def test_script_exists_no_dispatcher_coupling(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH))
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("import mmi_dispatch", source)
        self.assertNotIn("scripts/mmi_dispatch", source)
        proc_lines = [
            line
            for line in source.splitlines()
            if "subprocess" in line or "Popen" in line
        ]
        for line in proc_lines:
            self.assertNotIn("mmi_dispatch", line)

    def test_scored_envelope(self):
        code, out, _ = _run_estimator("clean", ["--verify-text", VERIFY_PASS])
        self.assertEqual(code, 0)
        self.assertIn("SCORED_CANDIDATES", out)
        self.assertIn("BUILDABILITY_EXCLUSIONS", out)
        self.assertIn("separation:", out)
        self.assertIn("f5_policy: run_hygiene_only", out)
        self.assertIn("total_measured_score:", out)
        self.assertIn("factor_coverage_summary:", out)

    def test_t15_top_rows_not_collapsed(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "buildability_worth")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(scored), 2)
        top_totals = [s.total_measured_score for s in scored[:2]]
        self.assertGreater(len(set(top_totals)), 1, msg=f"top totals flat: {top_totals}")

    def test_t16_scoreboard_f4_wired(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        by_id = {s.candidate.candidate_id: s for s in scored}
        self.assertGreater(by_id["#200"].factor_results["F4"].value, 0)

    def test_t17_research_paths_excluded(self):
        scored, errors, _, exclusions, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "research_excluded")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        excluded_ids = {x.candidate.candidate_id for x in exclusions}
        self.assertIn("#90", excluded_ids)
        by_id = {s.candidate.candidate_id: s for s in scored}
        self.assertGreater(by_id["#200"].factor_results["F4"].value, 0)

    def test_t18_equivalent_tie_has_separation(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        for item in scored:
            self.assertTrue(item.separation)
            self.assertIn("F1=", item.separation)

    def test_t19_measured_zero_preserved(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "null_f2_measured_zero")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        item = next(s for s in scored if s.candidate.candidate_id == "#200")
        f2 = item.factor_results["F2"]
        self.assertTrue(f2.measured)
        self.assertEqual(f2.value, 0)

    def test_t20_absent_source_emits_null(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "null_f2_null")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        item = scored[0]
        f2 = item.factor_results["F2"]
        self.assertFalse(f2.measured)
        self.assertIn("NULL(no_data:", f2.display())

    def test_t21_null_excluded_from_total(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        item = scored[0]
        for factor_id, result in item.factor_results.items():
            if not result.measured:
                weight_key = f"W{factor_id[1]}"
                self.assertNotIn(weight_key, item.weighted)
        expected = round(sum(item.weighted.values()), 2)
        self.assertEqual(item.total_measured_score, expected)

    def test_t22_dark_factor_report_present(self):
        _, out, _ = _run_estimator("clean", ["--verify-text", VERIFY_PASS])
        self.assertIn("ranking computed with dark factors present", out)
        self.assertIn("dark_factor_causes:", out)
        self.assertIn("NULL(no_data:", out)

    def test_t23_coverage_shown(self):
        _, out, _ = _run_estimator("clean", ["--verify-text", VERIFY_PASS])
        self.assertIn("coverage: ", out)
        self.assertRegex(out, r"coverage: \d/6")

    def test_t24_low_coverage_provisional(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "null_low_coverage")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        item = scored[0]
        self.assertEqual(item.coverage_count, 3)
        self.assertEqual(item.coverage_status, "LOW_COVERAGE_PROVISIONAL")

    def test_t25_locked_weights_unchanged(self):
        expected = {"F1": 30, "F2": 25, "F3": 20, "F4": 10, "F5": 10, "F6": 5}
        self.assertEqual(self.mod.SIGNED_WEIGHTS_RECORD, expected)
        self.assertEqual(self.mod.WEIGHTS, self.mod.SIGNED_WEIGHTS_RECORD)

    def test_t26_no_negative_missing_data_penalty(self):
        scored, errors, _, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        for item in scored:
            for result in item.factor_results.values():
                if result.measured and result.value is not None:
                    self.assertGreaterEqual(result.value, 0)

    def test_t27_deterministic_null_output(self):
        out1 = _run_estimator("null_f2_null", ["--verify-text", VERIFY_PASS])[1]
        out2 = _run_estimator("null_f2_null", ["--verify-text", VERIFY_PASS])[1]
        self.assertEqual(out1, out2)
        self.assertIn("NULL(no_data:", out1)


class EstimatorBuildabilityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_t28_built_excluded(self):
        _, out, _ = _run_estimator(
            "first_use_regression",
            ["--verify-text", VERIFY_ALL_CLEAR],
        )
        ranked = _candidate_ids(out)
        for blocked in ("#72", "#78", "#79", "#80"):
            self.assertNotIn(blocked, ranked)
        self.assertIn("EXCLUDED_ALREADY_BUILT", out)
        self.assertIn("candidate_id: #72", out)

    def test_t29_non_buildable_state_excluded(self):
        _, out, _ = _run_estimator(
            "first_use_regression",
            ["--verify-text", VERIFY_ALL_CLEAR],
        )
        self.assertIn("gates: E13,E14", out)
        self.assertIn("runtime_status_prefix: DETECTOR_FUNCTION", out)
        self.assertIn("candidate_id: #52", out)
        self.assertNotIn("#52", _candidate_ids(out))

    def test_t30_missing_contract_caught(self):
        _, out, _ = _run_estimator(
            "first_use_regression",
            ["--verify-text", VERIFY_ALL_CLEAR],
        )
        self.assertIn("BLOCKED_MISSING_CONTRACT", out)
        self.assertIn(
            "missing_contract: 4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md",
            out,
        )
        self.assertNotEqual(_candidate_ids(out)[:1], ["#52"])

    def test_t31_all_clear_advisory(self):
        _, out, _ = _run_estimator(
            "first_use_regression",
            ["--verify-text", VERIFY_ALL_CLEAR],
        )
        self.assertTrue(out.startswith("ADVISORY_ONLY:"))

    def test_t32_no_buildable_candidates(self):
        _, out, _ = _run_estimator(
            "first_use_regression",
            ["--verify-text", VERIFY_ALL_CLEAR],
        )
        self.assertIn("NO_BUILDABLE_CANDIDATES", out)
        self.assertEqual(_candidate_ids(out), [])

    def test_t33_agreement_check(self):
        scored, errors, _, exclusions, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        closed = set(self.mod.CLOSED_STATE_PREFIXES)
        buildable = set(self.mod.BUILDABLE_STATE_PREFIXES)
        for item in scored:
            prefix = self.mod._runtime_status_prefix_for_candidate(item.candidate)
            self.assertIn(prefix, buildable)
            self.assertNotIn(prefix, closed)
        for item in exclusions:
            if item.candidate.source != "scoreboard":
                continue
            prefix = item.runtime_status_prefix
            self.assertTrue(
                prefix in closed
                or prefix not in buildable
                or item.reason == "BLOCKED_MISSING_CONTRACT"
            )

    def test_t34_worth_unchanged_within_buildable(self):
        root = self.mod.Path(os.path.join(FIXTURES, "buildability_worth"))
        scoreboard = self.mod._read_text(
            root / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
        )
        registry = self.mod._read_text(root / "mmi" / "MMI_TASK_REGISTRY.yaml")
        decision_text = self.mod._read_text(root / "mmi" / "MMI_DECISION_LOG.md")
        health, health_board_present = self.mod._parse_health_board(scoreboard)
        graph_populated = self.mod._dependency_graph_populated(scoreboard)
        candidates = self.mod._parse_scoreboard_rows(scoreboard, health)
        candidates.extend(self.mod._parse_registry_tasks(registry))
        for cand in candidates:
            if cand.source == "scoreboard":
                cand.evidence_count = self.mod._scoreboard_evidence_count(
                    cand, decision_text
                )
        eligible, _ = self.mod._apply_gates(candidates, scoreboard, "BREADTH")
        buildable, _ = self.mod._apply_buildability_gates(eligible, root)
        direct = self.mod._sort_scored(
            [
                self.mod._score_candidate(
                    cand,
                    scoreboard,
                    "PASS",
                    graph_populated=graph_populated,
                    health_board_present=health_board_present,
                )
                for cand in buildable
            ]
        )
        scored, errors, _, _, _ = self.mod.analyze(root, verify_text=VERIFY_PASS)
        self.assertEqual(errors, [])
        self.assertEqual(
            [s.candidate.candidate_id for s in scored],
            [s.candidate.candidate_id for s in direct],
        )
        self.assertEqual(
            [s.total_measured_score for s in scored],
            [s.total_measured_score for s in direct],
        )

    def test_t35_scored_feedstock_from_bor(self):
        _, out, _ = _run_estimator(None, ["--verify-text", VERIFY_ALL_CLEAR])
        self.assertIn("ADVISORY_ONLY:", out)
        self.assertIn("SCORED_FEEDSTOCK", out)
        self.assertIn("candidate_id: #71", out)
        self.assertIn("lane_type: CONTRACT_DRAFT", out)
        self.assertIn("BUILDABILITY_EXCLUSIONS", out)
        self.assertIn("EXCLUDED_NON_BUILDABLE_STATE", out)

    def test_first_use_live_regression(self):
        verify_text = subprocess.run(
            [sys.executable, DISPATCH_PATH, "--verify"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        _, out, _ = _run_estimator(None, ["--verify-text", verify_text])
        if "current task: MODE: ALL_CLEAR" in verify_text:
            self.assertIn("ADVISORY_ONLY:", out)
        for blocked in ("#72", "#78", "#79", "#80"):
            self.assertNotIn(blocked, _candidate_ids(out))
        if "SCORED_FEEDSTOCK" in out:
            self.assertIn("candidate_id: #71", out)
        else:
            self.assertIn("candidate_id: #52", out)
            self.assertIn("BLOCKED_MISSING_CONTRACT", out)
        if "current task: MODE: ALL_CLEAR" in verify_text and _candidate_ids(out) == []:
            self.assertIn("NO_BUILDABLE_CANDIDATES", out)
        if "current task: MODE: ALL_CLEAR" in verify_text and "SCORED_FEEDSTOCK" in out:
            self.assertNotIn("#105", _candidate_ids(out)[:1])


if __name__ == "__main__":
    unittest.main()
