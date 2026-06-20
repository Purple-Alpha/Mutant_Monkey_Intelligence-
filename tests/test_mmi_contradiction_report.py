#!/usr/bin/env python3
"""Contract tests for Tier 2C Mode A contradiction / stale-state report."""
import hashlib
import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO, "scripts", "mmi_contradiction_report.py")
DISPATCH_PATH = os.path.join(REPO, "scripts", "mmi_dispatch.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "mmi_contradiction")

ALLOWED_ENVELOPE = frozenset(
    {
        "REPORT_ONLY_FINDINGS",
        "NO_REPORTABLE_FINDINGS",
        "REVIEW_REQUIRED",
    }
)

FORBIDDEN_TOOL_VERDICTS = frozenset(
    {
        "PASS",
        "FAIL",
        "BLOCK",
        "APPROVED",
        "VERIFIED",
        "COMPLETE",
        "BUILD_AUTHORIZED",
        "SIGNED",
        "PROMOTED",
        "SELECTED",
        "DELEGATED",
        "GATED",
        "ACCEPT",
        "REJECT",
        "NEXT_TASK",
        "RECOMMENDED",
        "AUTHORIZED",
    }
)

IMMUTABLE_PATHS = [
    "MMI_CURRENT_STATE.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_INTAKE_RECORDS.md",
    "mmi/MMI_TASK_REGISTRY.yaml",
]


def _file_digest(rel_path: str) -> str:
    path = os.path.join(REPO, rel_path)
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _run_report(fixture_name: str | None = None) -> tuple[int, str, str]:
    cmd = [sys.executable, SCRIPT_PATH]
    if fixture_name:
        cmd.extend(["--root", os.path.join(FIXTURES, fixture_name)])
    proc = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_contradiction_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_contradiction_report"] = module
    spec.loader.exec_module(module)
    return module


def _finding_categories(stdout: str) -> list[str]:
    cats: list[str] = []
    for line in stdout.splitlines():
        if line.startswith("category: "):
            cats.append(line.split(":", 1)[1].strip())
    return cats


def _severities(stdout: str) -> list[str]:
    sevs: list[str] = []
    for line in stdout.splitlines():
        if line.startswith("severity: "):
            sevs.append(line.split(":", 1)[1].strip())
    return sevs


class Tier2CContradictionReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_script_exists_no_dispatcher_coupling(self):
        self.assertTrue(os.path.isfile(SCRIPT_PATH))
        self.assertTrue(os.path.isfile(DISPATCH_PATH))
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

    def test_mode_a_stdout_only_no_file_writes(self):
        digests_before = {p: _file_digest(p) for p in IMMUTABLE_PATHS}
        code, out, _ = _run_report("clean")
        digests_after = {p: _file_digest(p) for p in IMMUTABLE_PATHS}
        self.assertEqual(digests_before, digests_after)
        self.assertEqual(code, 0)
        self.assertTrue(
            out.startswith("NO_REPORTABLE_FINDINGS")
            or out.startswith("REPORT_ONLY_FINDINGS")
        )

    def test_complete_without_closeout_evidence(self):
        code, out, _ = _run_report("complete_without_evidence")
        self.assertEqual(code, 0)
        self.assertIn("REPORT_ONLY_FINDINGS", out)
        self.assertIn("COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE", _finding_categories(out))

    def test_signed_contract_without_registry_row_info(self):
        code, out, _ = _run_report("signed_no_row")
        self.assertEqual(code, 0)
        self.assertIn("SIGNED_CONTRACT_WITHOUT_REGISTRY_ROW", _finding_categories(out))
        self.assertIn("INFO", _severities(out))

    def test_build_accept_registry_stale(self):
        code, out, _ = _run_report("build_stale")
        self.assertEqual(code, 0)
        self.assertIn("BUILD_COMMIT_WITHOUT_REGISTRY_UPDATE", _finding_categories(out))

    def test_do_not_use_cited_as_authority(self):
        code, out, _ = _run_report("do_not_use")
        self.assertEqual(code, 0)
        self.assertIn("DO_NOT_USE_REFERENCED_AS_AUTHORITY", _finding_categories(out))

    def test_legacy_naming_active_governance(self):
        code, out, _ = _run_report("legacy_active")
        self.assertEqual(code, 0)
        self.assertIn("LEGACY_NAMING_DRIFT", _finding_categories(out))

    def test_legacy_naming_historical_carve_out(self):
        code, out, _ = _run_report("legacy_historical")
        self.assertEqual(code, 0)
        self.assertNotIn("LEGACY_NAMING_DRIFT", _finding_categories(out))

    def test_retrospective_hygiene_no_false_complete_finding(self):
        code, out, _ = _run_report("retrospective_ok")
        self.assertEqual(code, 0)
        self.assertNotIn("COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE", _finding_categories(out))

    def test_critical_review_exits_zero(self):
        code, out, _ = _run_report("critical_review")
        self.assertEqual(code, 0)
        self.assertIn("CRITICAL_REVIEW", _severities(out))
        self.assertIn("REVIEW_REQUIRED", out.splitlines())

    def test_forbidden_verdicts_not_emitted_as_tool_verdict(self):
        code, out, _ = _run_report("complete_without_evidence")
        self.assertEqual(code, 0)
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in FORBIDDEN_TOOL_VERDICTS:
                self.fail(f"forbidden tool verdict line: {stripped}")
            if stripped.startswith("VERDICT:"):
                self.fail(f"forbidden VERDICT envelope line: {stripped}")

    def test_evidence_quotation_may_contain_pass_verdict(self):
        findings, errors = self.mod.analyze(
            self.mod.Path(os.path.join(FIXTURES, "complete_without_evidence"))
        )
        self.assertEqual(errors, [])
        note_findings = [f for f in findings if f.note]
        quoted = self.mod.Finding(
            category="TEST",
            severity="INFO",
            summary="fixture",
            evidence=[],
            note="Evidence body may quote VERDICT: PASS verbatim without being tool verdict",
        )
        report = self.mod.format_report([quoted])
        self.assertIn("VERDICT: PASS", report)
        self.assertTrue(report.startswith("REPORT_ONLY_FINDINGS"))

    def test_envelope_vocabulary_only_allowed(self):
        code, out, _ = _run_report("build_stale")
        self.assertEqual(code, 0)
        first = out.splitlines()[0]
        self.assertIn(first, ALLOWED_ENVELOPE)

    def test_no_mmi_reports_directory_created(self):
        reports = os.path.join(REPO, "mmi", "reports")
        self.assertFalse(os.path.isdir(reports))
        _run_report("clean")
        self.assertFalse(os.path.isdir(reports))


if __name__ == "__main__":
    unittest.main()
