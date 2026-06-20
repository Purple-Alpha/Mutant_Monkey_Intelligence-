#!/usr/bin/env python3
"""Acceptance tests T1–T13 for MMI Estimator Mode A."""
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
    for line in stdout.splitlines():
        if line.startswith("candidate_id: "):
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
        scored, errors, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        for item in scored:
            f6_contrib = item.factors["F6"] * self.mod.WEIGHTS["F6"] / 10
            self.assertLessEqual(f6_contrib, 5.0)

    def test_t9_readiness_ordering(self):
        scored, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        registry = [s for s in scored if s.candidate.source == "registry"]
        if len(registry) >= 2:
            self.assertGreaterEqual(registry[0].factors["F1"], registry[1].factors["F1"])

    def test_t10_weighted_sum(self):
        scored, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertTrue(scored)
        item = scored[0]
        expected = round(
            sum(item.factors[f"F{i}"] * self.mod.WEIGHTS[f"F{i}"] / 10 for i in range(1, 7)),
            2,
        )
        self.assertEqual(item.total, expected)

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
        clean, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        refresh, _, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "refresh")),
            verify_text=VERIFY_PASS,
        )
        self.assertNotEqual(
            [s.total for s in clean],
            [s.total for s in refresh],
        )

    def test_t13_verify_block_cannot_score(self):
        _, errors, _ = self.mod.analyze(
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
        self.assertTrue(out.startswith("SCORED_CANDIDATES"))
        self.assertIn("separation:", out)
        self.assertIn("f5_policy: run_hygiene_only", out)

    def test_t15_top_rows_not_collapsed(self):
        scored, errors, _ = self.mod.analyze(
            self.mod.Path(REPO),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(scored), 5)
        top_totals = [s.total for s in scored[:5]]
        self.assertGreater(
            len(set(top_totals)),
            1,
            msg=f"top-five totals still flat: {top_totals}",
        )
        for item in scored[:5]:
            self.assertFalse(
                item.factors["F1"] == 6 and item.factors["F5"] == 10 and item.factors["F4"] == 0,
                msg=f"{item.candidate.candidate_id} still on old collapse pattern",
            )

    def test_t16_scoreboard_f4_wired(self):
        scored, errors, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        by_id = {s.candidate.candidate_id: s for s in scored}
        self.assertGreater(by_id["#1"].factors["F4"], 0)
        self.assertGreater(by_id["#52"].factors["F4"], 0)

    def test_t17_research_paths_excluded(self):
        scored, errors, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "research_excluded")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        by_id = {s.candidate.candidate_id: s for s in scored}
        self.assertEqual(by_id["#90"].factors["F4"], 0)
        self.assertGreater(by_id["#91"].factors["F4"], 0)

    def test_t18_equivalent_tie_has_separation(self):
        scored, errors, _ = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "clean")),
            verify_text=VERIFY_PASS,
        )
        self.assertEqual(errors, [])
        for item in scored:
            self.assertTrue(item.separation)
            self.assertIn("F1=", item.separation)


if __name__ == "__main__":
    unittest.main()
