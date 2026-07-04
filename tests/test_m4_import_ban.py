from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.import_ban import scan_m4_package


def test_phase0_package_passes_import_ban():
    result = scan_m4_package(REPO)
    assert result.passed, result.violations


def test_canary_metadata_layer_import_fails(tmp_path: Path):
    pkg = tmp_path / "mmi" / "m4"
    pkg.mkdir(parents=True)
    (pkg / "bad.py").write_text("from canary_metadata_layer import X\n", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    result = scan_m4_package(tmp_path)
    assert not result.passed
    assert any(v.rule == "H-L8-001-canary_metadata_layer" for v in result.violations)


def test_mmi_l8_symbol_reference_fails(tmp_path: Path):
    pkg = tmp_path / "mmi" / "m4"
    pkg.mkdir(parents=True)
    (pkg / "bad.py").write_text('SIGNAL = "mmi.l8.metadata.foo"\n', encoding="utf-8")

    result = scan_m4_package(tmp_path)
    assert not result.passed
    assert any(v.rule == "H-L8-001-mmi_l8_symbol" for v in result.violations)


@pytest.mark.parametrize(
    "source",
    [
        'importlib.import_module("chaos.canary_metadata_layer")\n',
        '__import__("chaos.canary_metadata_layer")\n',
        'getattr(importlib, "import_module")("chaos.canary_metadata_layer")\n',
    ],
)
def test_dynamic_canary_metadata_layer_import_fails(tmp_path: Path, source: str):
    pkg = tmp_path / "mmi" / "m4"
    pkg.mkdir(parents=True)
    (pkg / "bad.py").write_text(source, encoding="utf-8")

    result = scan_m4_package(tmp_path)
    assert not result.passed
    assert any(v.rule == "H-L8-001-canary_metadata_layer" for v in result.violations)
