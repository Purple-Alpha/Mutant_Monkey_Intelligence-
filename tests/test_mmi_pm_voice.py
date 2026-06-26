#!/usr/bin/env python3
"""Acceptance tests for MMI PM Voice Layer Mode A always-routes completion."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_pm_voice.py")
HANDOFF_SCRIPT = os.path.join(REPO, "scripts", "mmi_handoff.py")
HANDOFF_LOG = os.path.join(REPO, "mmi", "MMI_HANDOFF_LOG.md")

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
    else:
        cmd.append("--verbose")
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_pm_voice", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_pm_voice"] = module
    spec.loader.exec_module(module)
    return module


def _load_handoff():
    spec = importlib.util.spec_from_file_location("mmi_handoff", HANDOFF_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_handoff"] = module
    spec.loader.exec_module(module)
    return module


def _menu_option(**kwargs):
    next_lane = _load_module()._load_module("mmi_next_lane", "mmi_next_lane.py")
    defaults = {
        "candidate_id": "#99",
        "candidate_name": "Test Candidate",
        "source_lifecycle": "DETECTOR_FUNCTION",
        "buildability_status": "BLOCKED_MISSING_CONTRACT",
        "contract_status": "MISSING",
        "reason_summary": "test",
        "recommended_matt_action": "HOLD_MISSING_CONTRACT",
    }
    defaults.update(kwargs)
    return next_lane.MenuOption(**defaults)


class TestMmiPmVoiceAlwaysRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _fields(self, evidence, handoff=None, root=None):
        root = root or Path(REPO)
        return self.mod.compose_voice(evidence, handoff=handoff, repo_root=root)

    def test_t1_always_emits_hand_it_to(self):
        _, out, _ = _run_voice()
        self.assertIn("HAND_IT_TO:\n", out)
        handler = out.split("HAND_IT_TO:\n", 1)[1].split("\n", 1)[0].strip()
        self.assertIn(handler, {"Claude", "Cursor", "Codex", "Gemini+ChatGPT", "Matt"})

    def test_t2_always_emits_you_do(self):
        _, out, _ = _run_voice()
        you_do = out.split("YOU_DO:\n", 1)[1].split("\n", 1)[0].strip()
        self.assertTrue(you_do)
        self.assertNotIn("or hold", you_do.lower())

    def test_route_next_step_gate_review_before_draft_keyword(self):
        routed = self.mod._route_next_step(
            "Run pre-build gate review via audit_tools/complete_gate.py on #61 contract draft"
        )
        self.assertEqual(routed, "Codex")

    def test_t3_no_nameless_dead_end_when_candidate_evidence_exists(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=0,
            missing_contract_count=2,
            menu_options=[_menu_option(candidate_id="#61", candidate_name="Test Case Generator")],
        )
        fields = self._fields(evidence)
        self.assertIn("HAND_IT_TO", fields)
        self.assertIn("YOU_DO", fields)
        self.assertIn("contract draft lane", fields["YOU_DO"])

    def test_t4_open_handoff_wins_and_routes_by_roster(self):
        handoff = _load_handoff().HandoffEntry(
            ts="2026-06-21T12:00:00Z",
            task="PM_VOICE_ALWAYS_ROUTES",
            by="Cursor",
            did="always routes built",
            state="DONE_AWAITING_SIGN",
            next_step="Matt sign + close",
            evidence="abc123",
        )
        evidence = self.mod.VoiceEvidence(dispatcher_mode="ALL_CLEAR")
        fields = self._fields(evidence, handoff=handoff)
        self.assertIn("PM_VOICE_ALWAYS_ROUTES", fields["IN_FLIGHT"])
        self.assertEqual(fields["HAND_IT_TO"], "Matt")
        self.assertEqual(fields["YOU_DO"], "Matt sign + close")

    def test_t5_signed_unreconciled_routes_cursor_for_52(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="NO_CURRENT_PLAN",
            menu_options=[
                _menu_option(
                    candidate_id="#52",
                    candidate_name="Plain-English Explanation",
                    source_lifecycle="DETECTOR_FUNCTION",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                    contract_status="PRESENT",
                )
            ],
        )
        fields = self._fields(evidence)
        self.assertEqual(fields["HAND_IT_TO"], "Cursor")
        self.assertEqual(fields["YOU_DO"], "Authorize MMI_52_SIGNED_UNBUILT_RECONCILE_ONLY.")
        self.assertIn("SIGNED_UNBUILT", fields["WHAT_NEEDS_MATT"])

    def test_t6_missing_contract_routes_claude(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="NO_CURRENT_PLAN",
            missing_contract_count=3,
            menu_options=[
                _menu_option(
                    candidate_id="#61",
                    candidate_name="Test Case Generator",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                    contract_status="MISSING",
                )
            ],
        )
        fields = self._fields(evidence)
        self.assertEqual(fields["HAND_IT_TO"], "Claude")
        self.assertIn("#61", fields["YOU_DO"])

    def test_t6b_missing_contract_with_drafted_governance_contract_routes_codex(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            missing_contract_count=1,
            menu_options=[
                _menu_option(
                    candidate_id="#105",
                    candidate_name="MMI Governance Invariants Testing Framework",
                    source_lifecycle="SPEC_DRAFT",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                    contract_status="MISSING",
                )
            ],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=False):
            fields = self.mod.compose_voice(
                evidence,
                repo_root=self.mod._repo_root(),
            )
        self.assertEqual(fields["HAND_IT_TO"], "Codex")
        self.assertIn("pre-build gate review via audit_tools/complete_gate.py", fields["YOU_DO"])
        self.assertIn("#105", fields["YOU_DO"])
        self.assertNotIn("contract draft lane", fields["YOU_DO"].lower())

    def test_t7_buildable_routes_cursor(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="BUILD",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=1,
            menu_options=[
                _menu_option(
                    candidate_id="#99T",
                    candidate_name="Test Buildable",
                    source_lifecycle="SIGNED_UNBUILT",
                    buildability_status="BUILDABLE",
                    contract_status="PRESENT",
                )
            ],
        )
        fields = self._fields(evidence)
        self.assertEqual(fields["HAND_IT_TO"], "Cursor")
        self.assertIn("Authorize build lane", fields["YOU_DO"])

    def test_t7b_awaiting_audit_routes_gated_reconcile(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="AUDIT",
            blueprint_status="NO_CURRENT_PLAN",
            buildable_count=1,
            scored_first="#52",
            menu_options=[
                _menu_option(
                    candidate_id="#52",
                    candidate_name="Plain-English Explanation",
                    source_lifecycle="AWAITING_AUDIT",
                    buildability_status="BUILDABLE",
                    contract_status="PRESENT",
                )
            ],
        )
        fields = self._fields(evidence)
        self.assertEqual(fields["HAND_IT_TO"], "Cursor")
        self.assertEqual(fields["YOU_DO"], "Authorize MMI_52_GATED_RECONCILE_ONLY.")
        self.assertIn("GATED reconcile", fields["WHAT_NEEDS_MATT"])

    def test_t7c_all_clear_feedstock_routes_claude(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            feedstock_first="#61",
            feedstock_first_name="Test Case Generator",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[
                _menu_option(
                    candidate_id="#61",
                    candidate_name="Test Case Generator",
                    source_lifecycle="DETECTOR_FUNCTION",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                    contract_status="MISSING",
                )
            ],
        )
        fields = self.mod.compose_voice(evidence)
        self.assertEqual(fields["HAND_IT_TO"], "Claude")
        self.assertIn("#61", fields["YOU_DO"])
        self.assertIn("estimator feedstock rank", fields["WHY"])

    def test_t7d_unsigned_contract_routes_codex(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            feedstock_first="#61",
            feedstock_first_name="Test Case Generator",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=False):
            fields = self.mod.compose_voice(
                evidence,
                repo_root=self.mod._repo_root(),
            )
        self.assertEqual(fields["HAND_IT_TO"], "Codex")
        self.assertIn("pre-build gate review via audit_tools/complete_gate.py", fields["YOU_DO"])

    def test_t7e2_routing_annex_gate_clean_routes_matt(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            menu_options=[],
        )
        with patch.object(self.mod, "_command_spine_wrappers_gated", return_value=True):
            with patch.object(
                self.mod, "_routing_policy_annex_pending", return_value=True
            ):
                with patch.object(self.mod, "_is_contract_signed", return_value=False):
                    with patch.object(
                        self.mod,
                        "_routing_policy_annex_gate_clean",
                        return_value=(
                            "audit_outputs/routing_policy_annex_pre_build_gate_20260624T015713Z.md"
                        ),
                    ):
                        fields = self.mod.compose_voice(
                            evidence,
                            repo_root=self.mod._repo_root(),
                        )
        self.assertEqual(fields["HAND_IT_TO"], "Matt")
        self.assertIn("Optional Matt §11 signature on #1 routing-policy annex", fields["WHAT_NEEDS_MATT"])
        self.assertIn("Pre-build gate clean 0/0", fields["IN_FLIGHT"])
        self.assertIn("Matt §11 sign routing-policy annex", fields["YOU_DO"])
        self.assertNotIn("Grok pre-build gate", fields["YOU_DO"])

    def test_t7e_signed_105_feedstock_routes_hold_not_gate(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            feedstock_first="#105",
            feedstock_first_name="MMI Governance Invariants Testing Framework",
            feedstock_lane_type="CONTRACT_REVIEW",
            menu_options=[
                _menu_option(
                    candidate_id="#105",
                    candidate_name="MMI Governance Invariants Testing Framework",
                    source_lifecycle="SIGNED_CONTRACT",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                    contract_status="PRESENT",
                )
            ],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=True):
            with patch.object(self.mod, "_command_spine_wrappers_gated", return_value=True):
                with patch.object(
                    self.mod, "_routing_policy_annex_pending", return_value=True
                ):
                    fields = self.mod.compose_voice(
                        evidence,
                        repo_root=self.mod._repo_root(),
                    )
        self.assertEqual(fields["HAND_IT_TO"], "Claude")
        self.assertIn("Chain-of-command next lane", fields["WHAT_NEEDS_MATT"])
        self.assertIn("routing-policy annex", fields["YOU_DO"])
        self.assertNotIn("Grok pre-build gate", fields["YOU_DO"])
        self.assertNotIn("§11 signed", fields["WHAT_NEEDS_MATT"])

    def test_t7f_signed_105_signed_contract_no_feedstock_routes_hold_not_reconcile(
        self,
    ):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            menu_options=[
                _menu_option(
                    candidate_id="#105",
                    candidate_name="MMI Governance Invariants Testing Framework",
                    source_lifecycle="SIGNED_CONTRACT",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                    contract_status="PRESENT",
                )
            ],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=True):
            with patch.object(self.mod, "_command_spine_wrappers_gated", return_value=True):
                with patch.object(
                    self.mod, "_routing_policy_annex_pending", return_value=True
                ):
                    fields = self.mod.compose_voice(
                        evidence,
                        repo_root=self.mod._repo_root(),
                    )
        self.assertEqual(fields["HAND_IT_TO"], "Claude")
        self.assertIn("Chain-of-command next lane", fields["WHAT_NEEDS_MATT"])
        self.assertNotIn("SIGNED_UNBUILT", fields["WHAT_NEEDS_MATT"])
        self.assertNotIn("Authorize reconcile", fields["YOU_DO"])
        self.assertNotIn("§11 signed", fields["WHAT_NEEDS_MATT"])

    def test_t7g_all_clear_hold_relay_dec095_and_3_contract_signed(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            menu_options=[
                _menu_option(
                    candidate_id="#1",
                    candidate_name="Swarm Commander Agent",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                ),
                _menu_option(
                    candidate_id="#3",
                    candidate_name="Risk Triage Agent",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                ),
            ],
        )
        fields = self.mod.compose_voice(
            evidence,
            repo_root=self.mod._repo_root(),
        )
        if self.mod._command_spine_wrappers_gated(self.mod._repo_root()):
            annex = self.mod._repo_root() / self.mod.ROUTING_POLICY_ANNEX_REL
            if annex.is_file() and self.mod._routing_policy_annex_pending(
                self.mod._repo_root()
            ):
                if self.mod._routing_policy_annex_gate_clean(self.mod._repo_root()):
                    self.assertEqual(fields["HAND_IT_TO"], "Matt")
                    self.assertIn(
                        "Optional Matt §11 signature on #1 routing-policy annex",
                        fields["WHAT_NEEDS_MATT"],
                    )
                else:
                    self.assertEqual(fields["HAND_IT_TO"], "Codex")
                    self.assertIn(
                        "routing-policy annex", fields["WHAT_NEEDS_MATT"].lower()
                    )
                    self.assertIn(
                        "pre-build gate review via audit_tools/complete_gate.py",
                        fields["YOU_DO"],
                    )
            else:
                self.assertTrue(
                    "chain-of-command" in fields["WHAT_NEEDS_MATT"].lower()
                    or "mission map authority fork" in fields["WHAT_NEEDS_MATT"].lower()
                    or "contract draft execution" in fields["WHAT_NEEDS_MATT"].lower()
                )
                self.assertIn(
                    "chain:",
                    fields["SOURCE"],
                )
                self.assertTrue(
                    "mission_map" in fields["SOURCE"]
                    or "live_rubric" in fields["SOURCE"]
                    or "estimator feedstock" in fields["WHY"].lower()
                )
            if self.mod._routing_policy_annex_pending(self.mod._repo_root()):
                if self.mod._routing_policy_annex_gate_clean(self.mod._repo_root()):
                    self.assertIn("MMI-DEC-120", fields["WHY"])
                else:
                    self.assertIn("MMI-DEC-116", fields["WHY"])
        else:
            self.assertTrue(
                "estimator feedstock rank" in fields["WHY"].lower()
                or "MMI-DEC-095" in fields["SOURCE"]
            )
        self.assertIn("§11 SIGNED", fields["IGNORE_FOR_NOW"])
        self.assertIn("001_swarm_commander_contract.md", fields["IGNORE_FOR_NOW"])
        self.assertIn("003_risk_triage_contract.md", fields["IGNORE_FOR_NOW"])
        self.assertIn("rubric_calibration: MMI-DEC-095", fields["SOURCE"])

    def test_t7i_all_clear_mission_map_complete_feedstock_or_chain(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=0,
            feedstock_first="#18",
            feedstock_first_name="Callback Verification",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[],
        )
        fields = self.mod.compose_voice(
            evidence,
            repo_root=self.mod._repo_root(),
        )
        if self.mod._contract_gate_clean(self.mod._repo_root(), "#18"):
            self.assertEqual(fields["HAND_IT_TO"], "Matt")
            self.assertIn("§11 sign", fields["YOU_DO"])
        else:
            self.assertEqual(fields["HAND_IT_TO"], "Codex")
            self.assertIn("#18", fields["YOU_DO"])
            self.assertIn("pre-build gate", fields["YOU_DO"].lower())
        self.assertNotIn("Unpark BOR feedstock", fields["YOU_DO"])

    def test_t7h_unparked_3_feedstock_routes_codex_contract_review(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            feedstock_first="#3",
            feedstock_first_name="Risk Triage Agent",
            feedstock_lane_type="CONTRACT_REVIEW",
            menu_options=[
                _menu_option(
                    candidate_id="#3",
                    candidate_name="Risk Triage Agent",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                ),
            ],
        )
        with patch.object(self.mod, "_contract_gate_clean", return_value=None):
            with patch.object(self.mod, "_is_contract_signed", return_value=False):
                fields = self.mod.compose_voice(
                    evidence,
                    repo_root=self.mod._repo_root(),
                )
        self.assertEqual(fields["HAND_IT_TO"], "Codex")
        self.assertIn("Pre-build gate review is needed for #3", fields["WHAT_NEEDS_MATT"])
        self.assertIn("003_risk_triage_contract.md", fields["YOU_DO"])
        self.assertNotIn("Hold until Matt names next lane", fields["YOU_DO"])

    def test_t7i_gate_clean_3_routes_matt_sign(self):
        root = self.mod._repo_root()
        gate_path = root / "audit_outputs" / "mmi_03_contract_gate_test_unit.md"
        gate_path.parent.mkdir(parents=True, exist_ok=True)
        gate_path.write_text(
            "GATE_SUMMARY: blocking=0 warnings=0\n", encoding="utf-8"
        )
        self.addCleanup(lambda: gate_path.unlink(missing_ok=True))
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            feedstock_first="#3",
            feedstock_first_name="Risk Triage Agent",
            feedstock_lane_type="CONTRACT_REVIEW",
            menu_options=[
                _menu_option(
                    candidate_id="#3",
                    candidate_name="Risk Triage Agent",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                ),
            ],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=False):
            fields = self.mod.compose_voice(evidence, repo_root=root)
        self.assertEqual(fields["HAND_IT_TO"], "Matt")
        self.assertIn("§11 sign", fields["YOU_DO"])
        self.assertIn("mmi_03_contract_gate_test_unit.md", fields["YOU_DO"])
        self.assertNotIn("Grok pre-build gate review", fields["YOU_DO"])

    def test_t7j_signed_3_feedstock_routes_hold_not_sign(self):
        root = self.mod._repo_root()
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=2,
            feedstock_first="#3",
            feedstock_first_name="Risk Triage Agent",
            feedstock_lane_type="CONTRACT_REVIEW",
            menu_options=[
                _menu_option(
                    candidate_id="#3",
                    candidate_name="Risk Triage Agent",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                ),
            ],
        )
        fields = self.mod.compose_voice(evidence, repo_root=root)
        if self.mod._command_spine_wrappers_gated(root):
            self.assertEqual(fields["HAND_IT_TO"], "Matt")
            self.assertIn("§11 signed", fields["WHAT_NEEDS_MATT"])
            self.assertIn("MMI-DEC-098", fields["IN_FLIGHT"])
            self.assertNotIn("Matt §11 sign", fields["YOU_DO"])
            self.assertNotIn("SIGNED_UNBUILT", fields["WHAT_NEEDS_MATT"])

    def test_t7k_unparked_1_draft_on_disk_routes_codex_gate(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=0,
            feedstock_first="#1",
            feedstock_first_name="Swarm Commander Agent",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[
                _menu_option(
                    candidate_id="#1",
                    candidate_name="Swarm Commander Agent",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                ),
            ],
        )
        with patch.object(self.mod, "_contract_gate_clean", return_value=None):
            with patch.object(self.mod, "_is_contract_signed", return_value=False):
                fields = self.mod.compose_voice(
                    evidence,
                    repo_root=self.mod._repo_root(),
                )
        self.assertEqual(fields["HAND_IT_TO"], "Codex")
        self.assertIn("Pre-build gate review is needed for #1", fields["WHAT_NEEDS_MATT"])
        self.assertIn("001_swarm_commander_contract.md", fields["YOU_DO"])
        self.assertIn("MMI-DEC-100", fields["WHY"])
        self.assertNotIn("SIGNED_UNBUILT", fields["WHAT_NEEDS_MATT"])

    def test_t7m_gate_clean_1_routes_matt_sign(self):
        root = self.mod._repo_root()
        gate_path = root / "audit_outputs" / "mmi_01_contract_gate_test_unit.md"
        gate_path.parent.mkdir(parents=True, exist_ok=True)
        gate_path.write_text(
            "GATE_SUMMARY: blocking=0 warnings=0\n", encoding="utf-8"
        )
        self.addCleanup(lambda: gate_path.unlink(missing_ok=True))
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=0,
            feedstock_first="#1",
            feedstock_first_name="Swarm Commander Agent",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[
                _menu_option(
                    candidate_id="#1",
                    candidate_name="Swarm Commander Agent",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                ),
            ],
        )
        with patch.object(self.mod, "_is_contract_signed", return_value=False):
            fields = self.mod.compose_voice(evidence, repo_root=root)
        self.assertEqual(fields["HAND_IT_TO"], "Matt")
        self.assertIn("§11 sign", fields["YOU_DO"])
        self.assertIn("mmi_01_contract_gate_test_unit.md", fields["YOU_DO"])
        self.assertIn("MMI-DEC-101", fields["WHY"])
        self.assertNotIn("Grok pre-build gate review", fields["YOU_DO"])

    def test_t7n_signed_1_feedstock_routes_hold_not_sign(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=0,
            feedstock_first="#1",
            feedstock_first_name="Swarm Commander Agent",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[
                _menu_option(
                    candidate_id="#1",
                    candidate_name="Swarm Commander Agent",
                    buildability_status="EXCLUDED_NON_BUILDABLE_STATE",
                ),
            ],
        )
        fields = self.mod.compose_voice(
            evidence,
            repo_root=self.mod._repo_root(),
        )
        root = self.mod._repo_root()
        if self.mod._command_spine_wrappers_gated(root):
            self.assertEqual(fields["HAND_IT_TO"], "Matt")
            self.assertIn("§11 signed", fields["WHAT_NEEDS_MATT"])
            self.assertIn("MMI-DEC-102", fields["IN_FLIGHT"])
            self.assertNotIn("Matt §11 sign", fields["YOU_DO"])
            self.assertNotIn("SIGNED_UNBUILT", fields["WHAT_NEEDS_MATT"])

    def test_t7l_unparked_1_no_draft_routes_claude_contract_draft(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="ALL_CLEAR",
            blueprint_status="CURRENT_PLAN_PRESENT",
            buildable_count=0,
            missing_contract_count=1,
            feedstock_first="#1",
            feedstock_first_name="Swarm Commander Agent",
            feedstock_lane_type="CONTRACT_DRAFT",
            menu_options=[
                _menu_option(
                    candidate_id="#1",
                    candidate_name="Swarm Commander Agent",
                    buildability_status="BLOCKED_MISSING_CONTRACT",
                ),
            ],
        )
        with patch.object(
            self.mod,
            "_contract_rel_for_candidate",
            return_value=None,
        ):
            fields = self.mod.compose_voice(
                evidence,
                repo_root=self.mod._repo_root(),
            )
        self.assertEqual(fields["HAND_IT_TO"], "Claude")
        self.assertIn("contract draft execution", fields["WHAT_NEEDS_MATT"].lower())
        self.assertIn("Draft Agent Design Contract for #1", fields["YOU_DO"])
        self.assertIn("MMI-DEC-099", fields["WHY"])

    def test_t8_read_only_no_mutation(self):
        before = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        _run_voice()
        after = {rel: _file_digest(rel) for rel in IMMUTABLE_PATHS}
        self.assertEqual(before, after)

    def test_t9_handoff_writer_append_only(self):
        mod = _load_handoff()
        with self.subTest("append_only"):
            import tempfile

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
                    state="DONE_AWAITING_SIGN",
                    next_step="sign",
                    evidence="abc",
                    ts="2026-06-21T12:00:00Z",
                )
                before = log_path.read_text(encoding="utf-8")
                second = mod.append_handoff(
                    root,
                    task="TASK_B",
                    by="Cursor",
                    did="did two",
                    state="DONE_AWAITING_CLOSEOUT",
                    next_step="close",
                    evidence="def",
                    ts="2026-06-21T12:01:00Z",
                )
                after = log_path.read_text(encoding="utf-8")
                self.assertTrue(after.startswith(before))
                self.assertIn(first, after)
                self.assertIn(second, after)

    def test_t10_existing_handoff_tests_still_pass(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_mmi_handoff.TestMmiHandoffAppendOnly",
                "tests.test_mmi_handoff.TestMmiHandoffPmRouting.test_t8_done_closed_supersedes_awaiting_sign",
                "-q",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)

    def test_live_open_handoff_when_present(self):
        _, out, _ = _run_voice()
        self.assertTrue(out.startswith("MMI_PM_VOICE"))
        if "PM_VOICE_ALWAYS_ROUTES" in out:
            self.assertIn("DONE_AWAITING_SIGN", out)
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("Matt sign + close", out)

    def test_live_52_gated_or_next_feedstock(self):
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
                code = self.mod.main(["--verbose"])
        out = buffer.getvalue()
        self.assertEqual(code, 0)
        if "Pre-build gate review is needed for #105" in out:
            self.assertIn("HAND_IT_TO:\nCodex", out)
            self.assertIn("pre-build gate review via audit_tools/complete_gate.py", out)
            self.assertIn("Lane 1 probe shipped", out)
        elif "Pre-build gate review is needed for #1 routing-policy annex" in out:
            self.assertIn("HAND_IT_TO:\nCodex", out)
            self.assertIn("001_swarm_commander_routing_policy_annex.md", out)
        elif "Optional Matt §11 signature on #1 routing-policy annex" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("Pre-build gate clean", out)
            self.assertIn("routing_policy_annex_pre_build_gate", out)
        elif "Optional Matt §11 signature on #1" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("Pre-build gate clean", out)
            self.assertIn("mmi_01_contract_gate", out)
        elif "Chain-of-command next lane" in out and "routing-policy annex" in out:
            self.assertIn("HAND_IT_TO:\nClaude", out)
            self.assertIn("001_swarm_commander_routing_policy_annex.md", out)
        elif "Select one ranked lane" in out and "#1 Swarm Commander contract §11 signed" in out:
            pass
        elif "mission map authority fork" in out.lower():
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("chain: mission_map", out)
        elif "Select one ranked lane" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("ranked lane", out.lower())
            self.assertIn("IN_FLIGHT:\nnone", out)
        elif "Pre-build gate review is needed for #65 Correction Evidence" in out:
            self.assertIn("HAND_IT_TO:\nCodex", out)
            self.assertIn("Correction_Evidence_Agent_Design_Contract_Deep_Dive.md", out)
        elif "Optional Matt §11 signature on #65 Correction Evidence" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("mmi_65_contract_gate", out)
        elif "Optional Matt §11 signature on #3" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
            self.assertIn("Pre-build gate clean", out)
        else:
            self.assertIn("IN_FLIGHT:\nnone", out)
        if "MMI_52_GATED_RECONCILE_ONLY" in out:
            self.assertIn("HAND_IT_TO:\nCursor", out)
        elif "#52 Plain-English Explanation is already GATED" in out:
            self.assertNotIn("Authorize build lane for #52", out)
        elif "estimator feedstock rank" in out or "SCORED_FEEDSTOCK" in out:
            if "pre-build gate review via audit_tools/complete_gate.py" in out:
                self.assertIn("HAND_IT_TO:\nCodex", out)
            else:
                self.assertIn("HAND_IT_TO:\nClaude", out)
                self.assertIn("#18", out)
        elif "Pre-build gate review is needed for #18 Callback Verification" in out:
            self.assertIn("HAND_IT_TO:\nCodex", out)
        elif "Pre-build gate review is needed for #71 Token Usage Tracker" in out:
            self.assertIn("HAND_IT_TO:\nCodex", out)
            self.assertIn("Token_Usage_Tracker_Agent_Design_Contract_Deep_Dive.md", out)
        elif "Dispatcher is DELEGATE" in out:
            self.assertIn("HAND_IT_TO:\nMatt", out)
        elif "MMI_52_SIGNED_UNBUILT_RECONCILE_ONLY" in out:
            self.assertIn("HAND_IT_TO:\nCursor", out)
        else:
            self.assertIn("Authorize build lane for #52", out)
            self.assertIn("HAND_IT_TO:\nCursor", out)

    def test_required_fields_present(self):
        _, out, _ = _run_voice()
        for field in (
            "WHAT_NEEDS_MATT:",
            "IN_FLIGHT:",
            "HAND_IT_TO:",
            "YOU_DO:",
            "WHY:",
            "IGNORE_FOR_NOW:",
            "SOURCE:",
            "BOUNDARY:",
        ):
            self.assertIn(field, out)

    def test_source_traces_engines(self):
        _, out, _ = _run_voice()
        source = out.split("SOURCE:", 1)[1].split("BOUNDARY:", 1)[0]
        self.assertIn("dispatcher:", source)
        self.assertIn("pm_console:", source)
        self.assertIn("next_lane:", source)
        self.assertIn("estimator:", source)

    def test_forbidden_tokens_absent(self):
        _, out, _ = _run_voice()
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_CONCLUSIONS:
                self.fail(f"forbidden conclusion: {stripped}")

    def test_pm_voice_default_emits_operator_console(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MMI_OPERATOR_CONSOLE", proc.stdout)
        self.assertIn("task:", proc.stdout)
        self.assertIn("for:", proc.stdout)
        self.assertIn("score:", proc.stdout)
        self.assertNotIn("MMI ACTIVE LANES", proc.stdout)
        self.assertNotIn("MMI_PM_VOICE", proc.stdout)
        self.assertNotIn("Alternate ranked lanes", proc.stdout)
        self.assertNotIn("evidence:", proc.stdout)
        self.assertNotIn("source:", proc.stdout)
        self.assertNotIn("boundary:", proc.stdout)

    def test_operator_console_no_buildable_when_all_clear(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        out = proc.stdout
        if "status: NO_BUILDABLE" in out:
            self.assertIn("task: ", out)
            self.assertIn("for: Matt", out)
            self.assertIn("score: n/a", out)
        else:
            self.assertIn("status: ACTION", out)
            self.assertIn("for:", out)
            self.assertIn("score:", out)
            if "task: Build " in out:
                self.assertIn("score: 100", out)

    def test_project_brain_active_task_loads_for_operator_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active = root / self.mod.PROJECT_BRAIN_ACTIVE_TASK_REL
            active.parent.mkdir(parents=True)
            active.write_text(
                "\n".join(
                    [
                        "status: `ACTION`",
                        "task: `Restore milestone-aware routing`",
                        "for: `Codex`",
                        "score: `8/10`",
                        "milestone: `M1_CONTROL_PLANE_RESTORED`",
                        "lane: `DRIFT_CHECK`",
                    ]
                ),
                encoding="utf-8",
            )

            payload = self.mod._load_project_brain_active_task(root)

        self.assertIsNotNone(payload)
        self.assertEqual(payload["action_label"], "Restore milestone-aware routing")
        self.assertEqual(payload["worker_lane"], "Codex")
        self.assertEqual(payload["score"], "8/10")
        self.assertEqual(payload["milestone"], "M1_CONTROL_PLANE_RESTORED")

    def test_project_brain_active_task_beats_weak_rubric_console(self):
        project_brain = {
            "status": "ACTION",
            "action_label": "Restore milestone-aware routing",
            "worker_lane": "Codex",
            "score": "8/10",
        }
        current = {
            "status": "ACTION",
            "action_label": "Promotion review #10",
            "worker_lane": "Matt",
            "score": "1/10",
        }

        selected = self.mod._prefer_project_brain_console(project_brain, current)

        self.assertEqual(selected["action_label"], "Restore milestone-aware routing")
        self.assertEqual(selected["score"], "8/10")

    def test_pm_voice_lanes_flag_emits_active_lanes(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--lanes"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MMI ACTIVE LANES", proc.stdout)

    def test_pm_voice_verbose_emits_legacy_envelope(self):
        _, out, _ = _run_voice()
        if "status: NO_BUILDABLE" in out:
            self.assertTrue(out.startswith("MMI_OPERATOR_CONSOLE"))
            self.assertNotIn("Alternate ranked lanes", out)
        else:
            self.assertTrue(out.startswith("MMI_PM_VOICE"))

    def test_revision_mode_read_only(self):
        code, out, _ = _run_voice(["--revision"])
        self.assertEqual(code, 0)
        self.assertIn("REVISION_MODE:", out)

    def test_insufficient_when_critical_gaps(self):
        evidence = self.mod.VoiceEvidence(
            dispatcher_mode="UNKNOWN",
            gaps=["missing_dispatcher_state: MMI_CURRENT_STATE.md"],
        )
        with patch.object(self.mod, "gather_evidence", return_value=evidence):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = self.mod.main(["--verbose"])
        self.assertEqual(code, 2)
        self.assertTrue(buffer.getvalue().startswith("INPUTS_INSUFFICIENT"))


if __name__ == "__main__":
    unittest.main()
