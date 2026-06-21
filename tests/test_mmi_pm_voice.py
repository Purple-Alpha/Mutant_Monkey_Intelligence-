#!/usr/bin/env python3
"""Acceptance tests for MMI PM Voice Layer Mode A."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_pm_voice.py")

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
    "MASTER_INDEX.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "mmi/MMI_TASK_REGISTRY.yaml",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
    "mmi/BLUEPRINT_OF_RECORD.md",
    "mmi/MMI_HANDOFF_LOG.md",
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
        "SELECTED",
    }
)


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_voice(extra: list[str] | None = None) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH]
    if extra:
        cmd.extend(extra)
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_pm_voice", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_pm_voice"] = module
    spec.loader.exec_module(module)
    return module


class TestMmiPmVoiceModeA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_default_emits_pm_voice(self):
        code, out, _ = _run_voice()
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("MMI_PM_VOICE"))

    def test_required_fields_present(self):
        _, out, _ = _run_voice()
        for field in (
            "WHAT_NEEDS_MATT:",
            "HAND_IT_TO:",
            "WHY:",
            "IGNORE_FOR_NOW:",
            "YOU_DO:",
            "SOURCE:",
            "BOUNDARY:",
        ):
            self.assertIn(field, out)

    def test_empty_pipeline_routes_to_claude(self):
        import io
        from contextlib import redirect_stdout

        handoff_stub = type(
            "HandoffStub",
            (),
            {"latest_open_handoff": staticmethod(lambda root: None)},
        )()
        real_load = self.mod._load_module

        def side_effect(name, filename):
            if filename == "mmi_handoff.py":
                return handoff_stub
            return real_load(name, filename)

        with patch.object(self.mod, "_load_module", side_effect=side_effect):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = self.mod.main([])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("HAND_IT_TO:\nClaude", out)
        self.assertIn("contract draft lane", out)
        self.assertNotIn("IN_FLIGHT:", out)

    def test_source_traces_engines(self):
        _, out, _ = _run_voice()
        source = out.split("SOURCE:", 1)[1].split("BOUNDARY:", 1)[0]
        self.assertIn("dispatcher:", source)
        self.assertIn("pm_console:", source)
        self.assertIn("next_lane:", source)
        self.assertIn("estimator:", source)

    def test_ignore_includes_gated_47(self):
        _, out, _ = _run_voice()
        self.assertIn("#47", out)
        self.assertIn("no current action", out)

    def test_you_do_mentions_52_or_hold(self):
        _, out, _ = _run_voice()
        self.assertIn("hold", out.lower())
        if "#52" in out:
            self.assertIn("Plain-English Explanation", out)

    def test_boundary_no_autonomous_auth(self):
        _, out, _ = _run_voice()
        self.assertIn("no autonomous selection", out)
        self.assertIn("no AUTH-5", out)

    def test_forbidden_tokens_absent(self):
        _, out, _ = _run_voice()
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_CONCLUSIONS:
                self.fail(f"forbidden conclusion: {stripped}")

    def test_read_only_no_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_voice()
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_terminal_command_works(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("MMI_PM_VOICE"))

    def test_buildable_relay_uses_estimator_rank_not_pm_selection(self):
        mod = self.mod
        next_lane = mod._load_module("mmi_next_lane", "mmi_next_lane.py")
        option = next_lane.MenuOption(
            candidate_id="#99T",
            candidate_name="Test Buildable",
            source_lifecycle="SIGNED_UNBUILT",
            buildability_status="BUILDABLE",
            contract_status="PRESENT",
            reason_summary="test",
            recommended_matt_action="AUTHORIZE_ARCHITECT_BLUEPRINT",
        )
        evidence = mod.VoiceEvidence(
            dispatcher_mode="BUILD",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=1,
            scored_first="#99T",
            scored_first_name="Test Buildable",
            menu_options=[option],
        )
        fields = mod.compose_voice(evidence)
        self.assertIn("ranked first by the Estimator", fields["WHAT_NEEDS_MATT"])
        self.assertEqual(fields["HAND_IT_TO"], "Matt")

    def test_in_flight_when_open_handoff_present(self):
        _, out, _ = _run_voice()
        if "IN_FLIGHT:" in out:
            self.assertIn("ARCHITECT_PARSER_ALIGNMENT_PATCH", out)
            self.assertIn("HAND_IT_TO:\nMatt", out)

    def test_revision_mode_read_only(self):
        code, out, _ = _run_voice(["--revision"])
        self.assertEqual(code, 0)
        self.assertIn("REVISION_MODE:", out)
        self.assertIn("MMI-DEC-039", out)

    def test_insufficient_when_critical_gaps(self):
        import io
        from contextlib import redirect_stdout

        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="UNKNOWN",
            gaps=["missing_dispatcher_state: MMI_CURRENT_STATE.md"],
        )
        with patch.object(self.mod, "gather_evidence", return_value=evidence):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = self.mod.main([])
        self.assertEqual(code, 2)
        self.assertTrue(buffer.getvalue().startswith("INPUTS_INSUFFICIENT"))


if __name__ == "__main__":
    unittest.main()
