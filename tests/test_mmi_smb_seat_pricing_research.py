#!/usr/bin/env python3
"""Tests for MMI SMB seat pricing research runner."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "mmi_smb_seat_pricing_research.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("mmi_smb_seat_pricing_research", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_smb_seat_pricing_research"] = module
    spec.loader.exec_module(module)
    return module


class SmbSeatPricingResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_build_report_has_vendors_and_federation(self):
        report = self.mod.build_report(Path(REPO))
        self.assertGreaterEqual(len(report.vendors), 10)
        self.assertGreaterEqual(len(report.federation_analogs), 5)
        self.assertEqual(len(report.scenarios), 4)

    def test_render_human_envelope(self):
        report = self.mod.build_report(Path(REPO))
        out = self.mod.render_human(report)
        self.assertIn(self.mod.ENVELOPE, out)
        self.assertIn("Proofpoint", out)
        self.assertIn("Immune Federation", out)
        self.assertIn("NOT build authorization", out)

    def test_render_json_structure(self):
        report = self.mod.build_report(Path(REPO))
        payload = json.loads(self.mod.render_json(report))
        self.assertEqual(payload["envelope"], self.mod.ENVELOPE)
        self.assertIn("vendors", payload)
        self.assertIn("federation_analogs", payload)

    def test_refresh_skips_local_urls(self):
        report = self.mod.build_report(Path(REPO))
        self.mod._refresh_sources(report)
        self.assertTrue(any("Proofpoint" in n or "fetch" in n for n in report.refresh_notes))

    @patch("urllib.request.urlopen")
    def test_refresh_records_fetch_success(self, mock_urlopen):
        mock_resp = mock_urlopen.return_value.__enter__.return_value
        mock_resp.read.return_value = b"Business plan $3.03 per user per month"
        report = self.mod.build_report(Path(REPO))
        self.mod._refresh_sources(report)
        self.assertTrue(any("OK" in n for n in report.refresh_notes))

    def test_cli_run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self.mod.main(["--run"])
        self.assertEqual(rc, 0)
        self.assertIn("SMB_SEAT_PRICING_RESEARCH", buf.getvalue())

    def test_cli_write(self):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = self.mod.main(["--write"])
        self.assertEqual(rc, 0)
        self.assertIn("WROTE:", err.getvalue())
        memo = Path(REPO) / self.mod.MEMO_REL
        self.assertTrue(memo.is_file())


if __name__ == "__main__":
    unittest.main()
