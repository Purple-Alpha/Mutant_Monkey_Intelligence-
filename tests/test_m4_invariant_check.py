from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.invariants import run_static_suite, suite_passed


def test_phase1_static_invariants_pass_on_authority_repo():
    results = run_static_suite(REPO)
    assert suite_passed(results), [
        (r.invariant_id, r.violations) for r in results if not r.passed
    ]


def test_inv6_fails_on_build_authorized_true(tmp_path: Path):
    pkg = tmp_path / "mmi" / "m4"
    pkg.mkdir(parents=True)
    (pkg / "bad.py").write_text("BUILD_AUTHORIZED = True\n", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    results = run_static_suite(tmp_path)
    inv6 = next(r for r in results if r.invariant_id == "INV-6")
    assert not inv6.passed


def test_inv5_fails_on_tmp_evidence_root(tmp_path: Path):
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "m4_bad.py").write_text('EVIDENCE_ROOT = "/tmp/mmi_evidence"\n', encoding="utf-8")

    results = run_static_suite(tmp_path)
    inv5 = next(r for r in results if r.invariant_id == "INV-5")
    assert not inv5.passed


def test_inv1_fails_multiline_indirect_authority_write(tmp_path: Path):
    pkg = tmp_path / "mmi" / "m4"
    pkg.mkdir(parents=True)
    (pkg / "bad.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                'AUTHORITY_ROOT = Path("C:/Architectapp_clean")',
                "target = AUTHORITY_ROOT",
                'target.write_text("x")',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    results = run_static_suite(tmp_path)
    inv1 = next(r for r in results if r.invariant_id == "INV-1")
    assert not inv1.passed


def test_inv1_fails_module_scope_indirect_write_via_alias(tmp_path: Path):
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "m4_bad.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                'ROOT = Path("C:/Architectapp_clean")',
                "",
                "def touch_authority():",
                "    handle = ROOT",
                "    handle.write_bytes(b'x')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    results = run_static_suite(tmp_path)
    inv1 = next(r for r in results if r.invariant_id == "INV-1")
    assert not inv1.passed
