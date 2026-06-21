#!/usr/bin/env python3
"""Acceptance tests for MMI Next Lane Mode A decision menu."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_next_lane.py")

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


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_next_lane(limit: int | None = None, plain: bool = False) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH]
    if limit is not None:
        cmd.extend(["--limit", str(limit)])
    if plain:
        cmd.append("--plain")
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_next_lane", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_next_lane"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiNextLaneModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            cls.source = handle.read()

    def test_emits_decision_menu_when_evidence_exists(self):
        code, out, _ = _run_next_lane()
        self.assertEqual(code, 0)
        self.assertTrue(
            out.startswith("MMI_NEXT_LANE_DECISION_MENU")
            or out.startswith("NO_BUILDABLE_CANDIDATES"),
        )
        if out.startswith("MMI_NEXT_LANE_DECISION_MENU"):
            self.assertIn("candidate_id:", out)

    def test_authority_boundary_present(self):
        _, out, _ = _run_next_lane()
        self.assertIn("Matt chooses", out)
        self.assertIn("no autonomous selection", out)
        self.assertIn("Matt remains authority", out)

    def test_option_fields_present(self):
        code, out, _ = _run_next_lane(limit=3)
        self.assertEqual(code, 0)
        if out.startswith("MMI_NEXT_LANE_DECISION_MENU"):
            self.assertIn("candidate_id:", out)
            self.assertIn("candidate_name:", out)
            self.assertIn("buildability_status:", out)
            self.assertIn("contract_status:", out)
            self.assertIn("recommended_matt_action:", out)

    def test_gated_candidates_hold_already_built(self):
        code, out, _ = _run_next_lane(limit=20)
        self.assertEqual(code, 0)
        if "candidate_id: #47" in out:
            self.assertIn("HOLD_ALREADY_BUILT", out)
            self.assertNotRegex(
                out,
                r"candidate_id: #47[\s\S]*?recommended_matt_action: AUTHORIZE",
            )

    def test_missing_contract_hold(self):
        code, out, _ = _run_next_lane(limit=20)
        self.assertEqual(code, 0)
        if "candidate_id: #52" in out:
            self.assertIn("HOLD_MISSING_CONTRACT", out)
            self.assertIn("contract_status: MISSING", out)

    def test_buildable_advisory_label_not_authorization(self):
        estimator_mod = self.mod._load_estimator_module()
        cand = estimator_mod.Candidate(
            candidate_id="#99T",
            source="scoreboard",
            name="Test Buildable",
            runtime_status="SIGNED_UNBUILT",
            blockers="",
            track="BREADTH",
            status_cell="SIGNED_UNBUILT",
        )
        factor = estimator_mod.FactorResult(True, 5)
        factor_results = {fid: factor for fid in estimator_mod.FACTOR_IDS}
        scored = estimator_mod.ScoredCandidate(
            candidate=cand,
            factor_results=factor_results,
            weighted={fid: 1.0 for fid in estimator_mod.FACTOR_IDS},
            total_measured_score=50.0,
            coverage_count=6,
            coverage_status="full",
            dark_factors=[],
            tie_break="test",
            separation="test",
        )
        with patch.object(self.mod, "build_menu", return_value=(self.mod.ENVELOPE_MENU, [
            self.mod.MenuOption(
                candidate_id="#99T",
                candidate_name="Test Buildable",
                source_lifecycle="SIGNED_UNBUILT",
                buildability_status="BUILDABLE",
                contract_status="PRESENT",
                reason_summary="test",
                recommended_matt_action="AUTHORIZE_ARCHITECT_BLUEPRINT",
            )
        ], [])):
            out = self.mod.format_menu("ALL_CLEAR", [
                self.mod.MenuOption(
                    candidate_id="#99T",
                    candidate_name="Test Buildable",
                    source_lifecycle="SIGNED_UNBUILT",
                    buildability_status="BUILDABLE",
                    contract_status="PRESENT",
                    reason_summary="test",
                    recommended_matt_action="AUTHORIZE_ARCHITECT_BLUEPRINT",
                )
            ])
        self.assertIn("AUTHORIZE_ARCHITECT_BLUEPRINT", out)
        self.assertNotIn("\nAUTHORIZED\n", out)
        for line in out.splitlines():
            if line.strip() in FORBIDDEN_CONCLUSIONS:
                self.fail(f"forbidden conclusion: {line}")

    def test_forbidden_conclusion_tokens_absent(self):
        _, out, _ = _run_next_lane()
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_CONCLUSIONS:
                self.fail(f"forbidden conclusion: {stripped}")

    def test_read_only_no_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_next_lane()
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_insufficient_inputs_envelope(self):
        import io
        from contextlib import redirect_stdout

        with patch.object(
            self.mod,
            "build_menu",
            return_value=(
                self.mod.ENVELOPE_INSUFFICIENT,
                [],
                ["missing_or_unreadable: scoreboard"],
            ),
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = self.mod.main([])
        out = buffer.getvalue()
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("INPUTS_INSUFFICIENT_CANNOT_BUILD_MENU"))

    def test_no_buildable_envelope_when_empty(self):
        import io
        from contextlib import redirect_stdout

        with patch.object(
            self.mod,
            "build_menu",
            return_value=(self.mod.ENVELOPE_NO_BUILDABLE, [], []),
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = self.mod.main([])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("NO_BUILDABLE_CANDIDATES"))

    def test_terminal_command_works(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(
            proc.stdout.startswith("MMI_NEXT_LANE_DECISION_MENU")
            or proc.stdout.startswith("NO_BUILDABLE_CANDIDATES"),
        )


if __name__ == "__main__":
    unittest.main()
