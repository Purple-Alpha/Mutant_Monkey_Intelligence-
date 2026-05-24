"""Tests for ``scripts/cisa_kev_ingest.py``.

These tests are intentionally offline. They drive every code path through
``--source-file`` fixtures so they can run inside the sandbox without
touching the live CISA feed.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from scripts.cisa_kev_ingest import (
    CISA_KEV_URL,
    DEFAULT_SMB_VENDORS,
    INTAKE_QUEUE_MARKER,
    KEV_PATTERN_CLASS,
    KEV_PATTERN_CLASS_NON_RANSOMWARE,
    append_entries_to_log,
    build_log_entry,
    existing_cve_ids,
    filter_smb_relevant,
    load_kev_from_file,
    main,
    render_entries,
)


def _sample_catalog() -> dict[str, Any]:
    return {
        "title": "CISA Catalog of Known Exploited Vulnerabilities",
        "catalogVersion": "2026.05.23",
        "dateReleased": "2026-05-23T00:00:00.000Z",
        "count": 4,
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-0001",
                "vendorProject": "Microsoft",
                "product": "Windows",
                "vulnerabilityName": "Microsoft Windows Elevation of Privilege",
                "dateAdded": "2026-05-20",
                "shortDescription": "EoP via crafted local request.",
                "requiredAction": "Apply mitigations per vendor instructions.",
                "dueDate": "2026-06-10",
                "knownRansomwareCampaignUse": "Known",
                "notes": "",
            },
            {
                "cveID": "CVE-2026-0002",
                "vendorProject": "Progress",
                "product": "MOVEit Transfer",
                "vulnerabilityName": "MOVEit Transfer SQL Injection",
                "dateAdded": "2026-05-19",
                "shortDescription": "SQL injection in MOVEit Transfer web interface.",
                "requiredAction": "Apply patches per vendor advisory.",
                "dueDate": "2026-06-09",
                "knownRansomwareCampaignUse": "Known",
                "notes": "",
            },
            {
                "cveID": "CVE-2026-0003",
                "vendorProject": "SomeNicheVendor",
                "product": "Niche Appliance",
                "vulnerabilityName": "Niche Appliance Auth Bypass",
                "dateAdded": "2026-05-18",
                "shortDescription": "Authentication bypass in niche appliance.",
                "requiredAction": "Apply mitigations per vendor instructions.",
                "dueDate": "2026-06-08",
                "knownRansomwareCampaignUse": "Unknown",
                "notes": "",
            },
            {
                "cveID": "CVE-2026-0004",
                "vendorProject": "Cisco",
                "product": "IOS XE",
                "vulnerabilityName": "Cisco IOS XE Web UI Privilege Escalation",
                "dateAdded": "2026-05-17",
                "shortDescription": "Privilege escalation via web UI.",
                "requiredAction": "Apply patches.",
                "dueDate": "2026-06-07",
                "knownRansomwareCampaignUse": "Known",
                "notes": "",
            },
        ],
    }


def _write_catalog(tmp_path: Path) -> Path:
    path = tmp_path / "kev_snapshot.json"
    path.write_text(json.dumps(_sample_catalog()), encoding="utf-8")
    return path


def _seed_log(tmp_path: Path, extra_entries: str = "") -> Path:
    log_path = tmp_path / "THREAT_INTEL_LOG.md"
    body = (
        "# Threat Intel Log\n"
        "\n"
        "## Entries\n"
        "\n"
        "### 2026-05-22 — Vendor-invoice fraud recall floor (5 weak shapes)\n"
        "\n"
        "**Source:** Phase 1.5 rerun.\n"
        "\n"
        f"{extra_entries}"
        "---\n"
        "\n"
        f"{INTAKE_QUEUE_MARKER}\n"
        "\n"
        "Future entries land below this line as new threat patterns are ingested.\n"
        "\n"
        "(none yet)\n"
    )
    log_path.write_text(body, encoding="utf-8")
    return log_path


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def test_load_kev_from_file_returns_catalog_dict(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path)

    catalog = load_kev_from_file(path)

    assert catalog["count"] == 4
    assert len(catalog["vulnerabilities"]) == 4
    assert catalog["vulnerabilities"][0]["cveID"] == "CVE-2026-0001"


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_smb_relevant_defaults_to_ransomware_only() -> None:
    catalog = _sample_catalog()

    entries = filter_smb_relevant(catalog)

    cve_ids = {e["cveID"] for e in entries}
    assert cve_ids == {"CVE-2026-0001", "CVE-2026-0002", "CVE-2026-0004"}


def test_filter_smb_relevant_no_ransomware_filter_keeps_all_valid_entries() -> None:
    catalog = _sample_catalog()

    entries = filter_smb_relevant(catalog, ransomware_only=False)

    cve_ids = {e["cveID"] for e in entries}
    assert cve_ids == {
        "CVE-2026-0001",
        "CVE-2026-0002",
        "CVE-2026-0003",
        "CVE-2026-0004",
    }


def test_filter_smb_relevant_with_default_vendor_allowlist_drops_niche_vendor() -> None:
    catalog = _sample_catalog()

    entries = filter_smb_relevant(
        catalog,
        ransomware_only=False,
        vendor_allowlist=list(DEFAULT_SMB_VENDORS),
    )

    cve_ids = {e["cveID"] for e in entries}
    assert "CVE-2026-0003" not in cve_ids
    assert {"CVE-2026-0001", "CVE-2026-0002", "CVE-2026-0004"}.issubset(cve_ids)


def test_filter_smb_relevant_with_explicit_vendor_allowlist_is_case_insensitive() -> None:
    catalog = _sample_catalog()

    entries = filter_smb_relevant(
        catalog,
        ransomware_only=False,
        vendor_allowlist=["microsoft"],
    )

    assert [e["cveID"] for e in entries] == ["CVE-2026-0001"]


def test_filter_smb_relevant_drops_entries_missing_cve_id() -> None:
    catalog = {
        "vulnerabilities": [
            {"cveID": "", "knownRansomwareCampaignUse": "Known"},
            {"knownRansomwareCampaignUse": "Known"},
            {"cveID": "CVE-2026-9999", "knownRansomwareCampaignUse": "Known"},
        ]
    }

    entries = filter_smb_relevant(catalog)

    assert [e["cveID"] for e in entries] == ["CVE-2026-9999"]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_build_log_entry_includes_locked_fields_and_marks_ransomware_class() -> None:
    entry = _sample_catalog()["vulnerabilities"][0]

    rendered = build_log_entry(entry, today=date(2026, 5, 23))

    assert rendered.startswith(
        "### 2026-05-23 — CISA KEV: CVE-2026-0001 — Microsoft Windows — "
        "Microsoft Windows Elevation of Privilege"
    )
    assert f"**Pattern class:** {KEV_PATTERN_CLASS}" in rendered
    assert "**Source:** CISA KEV catalog (`" in rendered
    assert CISA_KEV_URL in rendered
    assert "EoP via crafted local request." in rendered
    assert "Required action: Apply mitigations per vendor instructions." in rendered
    assert "Due date: 2026-06-10." in rendered
    assert "CVE-2026-0001; dateAdded 2026-05-20; knownRansomwareCampaignUse=Known" in rendered
    assert "**Action taken:** None (ingestion only" in rendered
    assert "**Policy update link:** (none)" in rendered
    assert "**Verification:** (none)" in rendered


def test_build_log_entry_uses_non_ransomware_class_for_unknown_use() -> None:
    entry = _sample_catalog()["vulnerabilities"][2]

    rendered = build_log_entry(entry, today=date(2026, 5, 23))

    assert f"**Pattern class:** {KEV_PATTERN_CLASS_NON_RANSOMWARE}" in rendered
    assert KEV_PATTERN_CLASS not in rendered


def test_render_entries_joins_with_horizontal_rule_separator() -> None:
    catalog = _sample_catalog()
    entries = filter_smb_relevant(catalog)[:2]

    rendered = render_entries(entries, today=date(2026, 5, 23))

    assert rendered.count("### 2026-05-23 — CISA KEV:") == 2
    assert "\n\n---\n\n" in rendered


def test_render_entries_returns_empty_string_for_no_entries() -> None:
    assert render_entries([], today=date(2026, 5, 23)) == ""


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------


def test_existing_cve_ids_only_picks_up_level_3_headers(tmp_path: Path) -> None:
    log_path = _seed_log(
        tmp_path,
        extra_entries=(
            "### 2026-05-22 — CISA KEV: CVE-2025-9999 — Acme Widget\n"
            "\n"
            "Body mentions CVE-2024-1111 but it is not a header.\n"
            "\n"
            "---\n"
            "\n"
        ),
    )

    found = existing_cve_ids(log_path)

    assert found == {"CVE-2025-9999"}


# ---------------------------------------------------------------------------
# Append
# ---------------------------------------------------------------------------


def test_append_entries_to_log_inserts_above_intake_queue_marker(tmp_path: Path) -> None:
    log_path = _seed_log(tmp_path)
    entry = build_log_entry(
        _sample_catalog()["vulnerabilities"][0], today=date(2026, 5, 23)
    )

    append_entries_to_log(log_path, entry)

    text = log_path.read_text(encoding="utf-8")
    queue_pos = text.find(INTAKE_QUEUE_MARKER)
    new_pos = text.find("### 2026-05-23 — CISA KEV: CVE-2026-0001")
    assert new_pos != -1
    assert new_pos < queue_pos
    assert "(none yet)" in text  # marker section preserved


def test_append_entries_to_log_raises_when_marker_missing(tmp_path: Path) -> None:
    log_path = tmp_path / "no_marker.md"
    log_path.write_text("# Log\n\nNo marker here.\n", encoding="utf-8")

    with pytest.raises(ValueError):
        append_entries_to_log(log_path, "### dummy")


def test_append_entries_to_log_noop_for_empty_block(tmp_path: Path) -> None:
    log_path = _seed_log(tmp_path)
    original = log_path.read_text(encoding="utf-8")

    append_entries_to_log(log_path, "   \n  ")

    assert log_path.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _run_cli(argv: list[str]) -> tuple[int, dict[str, Any], str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        rc = main(argv)
    out = buffer.getvalue()
    summary_raw, _, rest = out.partition("\n\n")
    summary = json.loads(summary_raw)
    return rc, summary, rest


def test_cli_dry_run_prints_summary_and_entries_without_writing(tmp_path: Path) -> None:
    source = _write_catalog(tmp_path)
    log_path = _seed_log(tmp_path)
    original = log_path.read_text(encoding="utf-8")

    rc, summary, body = _run_cli(
        [
            "--source-file",
            str(source),
            "--log-path",
            str(log_path),
            "--today",
            "2026-05-23",
        ]
    )

    assert rc == 0
    assert summary["fetched_total"] == 4
    assert summary["filtered_count"] == 3
    assert summary["appended"] is False
    assert summary["ransomware_only"] is True
    assert "### 2026-05-23 — CISA KEV: CVE-2026-0001" in body
    assert log_path.read_text(encoding="utf-8") == original


def test_cli_append_writes_filtered_entries_to_log(tmp_path: Path) -> None:
    source = _write_catalog(tmp_path)
    log_path = _seed_log(tmp_path)

    rc, summary, _ = _run_cli(
        [
            "--source-file",
            str(source),
            "--log-path",
            str(log_path),
            "--today",
            "2026-05-23",
            "--append",
            "--limit",
            "2",
        ]
    )

    assert rc == 0
    assert summary["appended"] is True
    assert summary["filtered_count"] == 2

    text = log_path.read_text(encoding="utf-8")
    assert text.count("### 2026-05-23 — CISA KEV:") == 2
    assert "CVE-2026-0001" in text
    assert "CVE-2026-0002" in text
    assert "CVE-2026-0004" not in text  # capped by --limit 2
    assert text.find("### 2026-05-23") < text.find(INTAKE_QUEUE_MARKER)


def test_cli_append_skips_duplicates_against_existing_log(tmp_path: Path) -> None:
    source = _write_catalog(tmp_path)
    log_path = _seed_log(
        tmp_path,
        extra_entries=(
            "### 2026-05-22 — CISA KEV: CVE-2026-0001 — Microsoft Windows\n"
            "\n"
            "Already logged yesterday.\n"
            "\n"
            "---\n"
            "\n"
        ),
    )

    rc, summary, body = _run_cli(
        [
            "--source-file",
            str(source),
            "--log-path",
            str(log_path),
            "--today",
            "2026-05-23",
            "--append",
        ]
    )

    assert rc == 0
    assert summary["filtered_count"] == 2  # 3 ransomware-only minus 1 duplicate
    text = log_path.read_text(encoding="utf-8")
    assert text.count("CVE-2026-0001") == 1  # not duplicated
    assert "CVE-2026-0002" in text
    assert "CVE-2026-0004" in text


def test_cli_out_writes_preview_file_without_modifying_log(tmp_path: Path) -> None:
    source = _write_catalog(tmp_path)
    log_path = _seed_log(tmp_path)
    out_path = tmp_path / "preview" / "kev_preview.md"
    original = log_path.read_text(encoding="utf-8")

    rc, summary, _ = _run_cli(
        [
            "--source-file",
            str(source),
            "--log-path",
            str(log_path),
            "--today",
            "2026-05-23",
            "--out",
            str(out_path),
        ]
    )

    assert rc == 0
    assert summary["out_path"] == str(out_path)
    assert summary["appended"] is False
    assert out_path.exists()
    preview = out_path.read_text(encoding="utf-8")
    assert "### 2026-05-23 — CISA KEV: CVE-2026-0001" in preview
    assert log_path.read_text(encoding="utf-8") == original


def test_cli_no_ransomware_filter_with_default_vendor_allowlist(tmp_path: Path) -> None:
    source = _write_catalog(tmp_path)
    log_path = _seed_log(tmp_path)

    rc, summary, _ = _run_cli(
        [
            "--source-file",
            str(source),
            "--log-path",
            str(log_path),
            "--today",
            "2026-05-23",
            "--no-ransomware-only",
            "--vendor-allowlist",
            "default",
        ]
    )

    assert rc == 0
    assert summary["ransomware_only"] is False
    assert summary["vendor_allowlist"] == list(DEFAULT_SMB_VENDORS)
    assert summary["filtered_count"] == 3
