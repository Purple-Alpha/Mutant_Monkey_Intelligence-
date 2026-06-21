#!/usr/bin/env python3
"""Acceptance tests T1–T7 for MMI handoff signal + PM routing."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDOFF_SCRIPT = os.path.join(REPO, "scripts", "mmi_handoff.py")
PM_VOICE_SCRIPT = os.path.join(REPO, "scripts", "mmi_pm_voice.py")
HANDOFF_LOG = os.path.join(REPO, "mmi", "MMI_HANDOFF_LOG.md")
HEADER_ONLY = os.path.join(REPO, "tests", "fixtures", "mmi_handoff", "header_only")


def _load_handoff():
    spec = importlib.util.spec_from_file_location("mmi_handoff", HANDOFF_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_handoff"] = module
    spec.loader.exec_module(module)
    return module


def _load_pm_voice():
    spec = importlib.util.spec_from_file_location("mmi_pm_voice", PM_VOICE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_pm_voice"] = module
    spec.loader.exec_module(module)
    return module


def _file_digest(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


class TestMmiHandoffAppendOnly(unittest.TestCase):
    def test_t1_append_only_no_edit(self):
        mod = _load_handoff()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "mmi" / "MMI_HANDOFF_LOG.md"
            log_path.parent.mkdir(parents=True)
            log_path.write_text("# header\n\n", encoding="utf-8")
            first = mod.append_handoff(
                root,
                task="TASK_A",
                by="Cursor",
                did="did one",
                state="DONE_AWAITING_CLOSEOUT",
                next_step="close records",
                evidence="abc123",
                ts="2026-06-20T12:00:00Z",
            )
            before = log_path.read_text(encoding="utf-8")
            second = mod.append_handoff(
                root,
                task="TASK_B",
                by="Codex",
                did="did two",
                state="DONE_AWAITING_GATE",
                next_step="run gate",
                evidence="def456",
                ts="2026-06-20T12:01:00Z",
            )
            after = log_path.read_text(encoding="utf-8")
            self.assertTrue(after.startswith(before))
            self.assertIn(first, after)
            self.assertIn(second, after)
            self.assertEqual(after.count("TASK_A"), 1)


class TestMmiHandoffPmRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handoff = _load_handoff()
        cls.pm_voice = _load_pm_voice()

    def test_t2_pm_surfaces_in_flight(self):
        entry = self.handoff.HandoffEntry(
            ts="2026-06-20T12:00:00Z",
            task="ARCHITECT_PARSER_ALIGNMENT_PATCH",
            by="Cursor",
            did="parser patch built",
            state="DONE_AWAITING_CLOSEOUT",
            next_step="close MMI records (DEC + LAST_COMPLETED)",
            evidence="829175b/d53ef03",
        )
        evidence = self.pm_voice.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=0,
        )
        fields = self.pm_voice.compose_voice(evidence, handoff=entry)
        rendered = self.pm_voice.format_voice(fields)
        self.assertIn("IN_FLIGHT:", rendered)
        self.assertIn("ARCHITECT_PARSER_ALIGNMENT_PATCH", rendered)
        self.assertIn("DONE_AWAITING_CLOSEOUT", rendered)

    def test_t3_roster_routing(self):
        self.assertEqual(
            self.pm_voice._route_next_step("draft contract lane"),
            "Claude",
        )
        self.assertEqual(self.pm_voice._route_next_step("build wrapper"), "Cursor")
        self.assertEqual(self.pm_voice._route_next_step("run gate review"), "Codex")
        self.assertEqual(
            self.pm_voice._route_next_step("research cross-check"),
            "Gemini+ChatGPT",
        )
        self.assertEqual(
            self.pm_voice._route_next_step("Matt §11 sign + close"),
            "Matt",
        )

    def test_t4_pm_zero_write_to_handoff_log(self):
        before = _file_digest(HANDOFF_LOG)
        proc = subprocess.run(
            [sys.executable, PM_VOICE_SCRIPT],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        after = _file_digest(HANDOFF_LOG)
        self.assertEqual(before, after)

    def test_t5_no_roster_match_flags_matt(self):
        self.assertEqual(
            self.pm_voice._route_next_step("operator decision required"),
            "Matt",
        )

    def test_t6_fallback_without_open_handoff(self):
        evidence = self.pm_voice.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=0,
            menu_options=[],
        )
        fields = self.pm_voice.compose_voice(evidence, handoff=None)
        self.assertNotIn("IN_FLIGHT", fields)
        self.assertEqual(fields["HAND_IT_TO"], "Claude")

    def test_t7_existing_pm_engine_tests_still_pass(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_mmi_pm_voice",
                "tests.test_mmi_pm_console",
                "tests.test_mmi_next_lane",
                "-q",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
