#!/usr/bin/env python3
"""Contract tests T2A-T1 through T2A-T12 for Tier 2A Mode A packet intake validator."""
import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_packet_intake.py")
DISPATCH_PATH = os.path.join(REPO, "scripts", "mmi_dispatch.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_packets")

FORBIDDEN_STDOUT = (
    "PASS",
    "FAIL",
    "APPROVED",
    "VERIFIED",
    "COMPLETE",
    "BUILD_AUTHORIZED",
    "SIGNED",
    "PROMOTED",
)

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "mmi/MMI_GATE_REGISTRY.md",
    "mmi/MMI_TASK_REGISTRY_SCHEMA.md",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
    "scripts/mmi_dispatch.py",
]


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_cli(packet_rel: str) -> tuple[int, str]:
    packet_path = os.path.join(REPO, packet_rel)
    proc = subprocess.run(
        [sys.executable, SCRIPT_PATH, packet_path],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_packet_intake", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Tier2APacketIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_t2a_t1_script_exists_dispatcher_untouched(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH))
        self.assertTrue(os.path.isfile(DISPATCH_PATH))
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("spec_from_file_location(\"mmi_dispatch\"", source)

    def test_t2a_t2_mode_a_stdout_only_no_file_writes(self):
        before_intake = _file_digest("mmi/MMI_INTAKE_RECORDS.md")
        code, out = _run_cli("tests/fixtures/mmi_packets/valid_no_routing_files.md")
        after_intake = _file_digest("mmi/MMI_INTAKE_RECORDS.md")
        self.assertEqual(before_intake, after_intake)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("ACCEPT_FOR_MMI_REVIEW"))

    def test_t2a_t3_valid_packet_accept(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/valid_no_routing_files.md")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[0], "ACCEPT_FOR_MMI_REVIEW")

    def test_t2a_t3_valid_with_routing_and_verify(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/valid_with_routing_files.md")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[0], "ACCEPT_FOR_MMI_REVIEW")

    def test_t2a_t4_missing_verify_output_rejects(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/missing_verify_output.md")
        self.assertNotEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "REJECT_INCOMPLETE_PACKET")
        self.assertIn("MISSING_MMI_VERIFY_OUTPUT", lines)

    def test_t2a_t4_missing_deviations_heading(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/missing_deviations.md")
        self.assertNotEqual(code, 0)
        self.assertIn("MISSING_DEVIATIONS_FROM_CONTRACT", out)

    def test_t2a_t4_blank_deviations_rejects(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/blank_deviations.md")
        self.assertNotEqual(code, 0)
        self.assertIn("BLANK_DEVIATIONS_FROM_CONTRACT", out)

    def test_t2a_t4_deviations_none_accepted(self):
        fixture_path = os.path.join(FIXTURES, "valid_no_routing_files.md")
        with open(fixture_path, encoding="utf-8") as handle:
            text = handle.read()
        verdict, codes = self.mod.validate_packet_text(text)
        self.assertEqual(verdict, "ACCEPT_FOR_MMI_REVIEW")
        self.assertEqual(codes, [])

    def test_t2a_t4_empty_files_changed_rejects(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/empty_files_changed.md")
        self.assertNotEqual(code, 0)
        self.assertIn("EMPTY_FILES_CHANGED", out)

    def test_t2a_t4_missing_oos_rejects(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/missing_oos.md")
        self.assertNotEqual(code, 0)
        self.assertIn("MISSING_NO_OUT_OF_SCOPE_CONFIRMATIONS", out)

    def test_t2a_t4_missing_git_status_rejects(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/missing_git_status.md")
        self.assertNotEqual(code, 0)
        self.assertIn("MISSING_GIT_STATUS_SHORT", out)

    def test_t2a_t5_mode_b_not_implemented(self):
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("write_text(", source)
        self.assertNotIn("write_bytes(", source)
        self.assertNotIn("Mode B", source)

    def test_t2a_t6_no_routing_advance_from_validator(self):
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            source = handle.read().lower()
        self.assertNotIn("--sync", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("spec_from_file_location(\"mmi_dispatch\"", source)

    def test_t2a_t8_forbidden_vocabulary_never_on_stdout(self):
        for name in os.listdir(FIXTURES):
            if not name.endswith(".md"):
                continue
            _, out = _run_cli(f"tests/fixtures/mmi_packets/{name}")
            lines = [line.strip() for line in out.strip().splitlines()]
            self.assertTrue(lines[0] in ("ACCEPT_FOR_MMI_REVIEW", "REJECT_INCOMPLETE_PACKET"))
            for line in lines:
                self.assertNotEqual(line, "REJECT")
                for token in FORBIDDEN_STDOUT:
                    self.assertNotEqual(line, token)
                    self.assertFalse(line.startswith(token + " "))

    def test_t2a_t9_multi_field_rejection_all_codes(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/multi_missing_fields.md")
        self.assertNotEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "REJECT_INCOMPLETE_PACKET")
        self.assertIn("MISSING_AUTHORIZATION_REF", lines)
        self.assertIn("MISSING_OPERATOR_ACTION_REQUIRED", lines)
        self.assertIn("MISSING_TASK_OR_CONTRACT_REF", lines)

    def test_t2a_t10_accept_side_immutability(self):
        digests_before = {path: _file_digest(path) for path in IMMUTABLE_PATHS}
        code, out = _run_cli("tests/fixtures/mmi_packets/valid_with_routing_files.md")
        digests_after = {path: _file_digest(path) for path in IMMUTABLE_PATHS}
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[0], "ACCEPT_FOR_MMI_REVIEW")
        self.assertEqual(digests_before, digests_after)

    def test_t2a_t11_write_containment_mode_a(self):
        targets = [
            "MMI_CURRENT_STATE.md",
            "mmi/MMI_INTAKE_RECORDS.md",
            "mmi/MMI_DECISION_LOG.md",
            "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
        ]
        before = {t: _file_digest(t) for t in targets}
        _run_cli("tests/fixtures/mmi_packets/valid_with_routing_files.md")
        after = {t: _file_digest(t) for t in targets}
        self.assertEqual(before, after)

    def test_t2a_t12_no_git_mutation(self):
        with open(SCRIPT_PATH, encoding="utf-8") as handle:
            source = handle.read().lower()
        self.assertNotIn("git ", source)
        self.assertNotIn("git_commit", source)
        self.assertNotIn("subprocess", source)

    def test_nonzero_exit_is_packet_inadmissibility_only_language(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/missing_git_status.md")
        self.assertNotEqual(code, 0)
        lowered = out.lower()
        self.assertNotIn("build failure", lowered)
        self.assertNotIn("worker failure", lowered)
        self.assertNotIn("verify failure", lowered)
        self.assertEqual(out.strip().splitlines()[0], "REJECT_INCOMPLETE_PACKET")

    def test_pasted_verdict_pass_in_packet_allowed(self):
        code, out = _run_cli("tests/fixtures/mmi_packets/valid_with_routing_files.md")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[0], "ACCEPT_FOR_MMI_REVIEW")
        self.assertNotIn("VERDICT: PASS", out)


if __name__ == "__main__":
    unittest.main()
