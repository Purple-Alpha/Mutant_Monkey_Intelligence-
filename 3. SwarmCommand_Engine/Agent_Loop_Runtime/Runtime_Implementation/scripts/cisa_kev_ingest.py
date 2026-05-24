"""CISA KEV threat-intel ingestion v0 (operator-run).

Implements the first half of MILESTONE C1 (threat-intel ingestion) as a
narrow, read-only-by-default CLI. It pulls the CISA Known Exploited
Vulnerabilities (KEV) catalog, filters for SMB-relevant entries, renders
them in the locked ``THREAT_INTEL_LOG.md`` entry format, and (only when
``--append`` is passed by the operator) appends them to the log.

Boundary:

* Operator-run only. Not autonomous, not invoked by any agent loop.
* Touches **only** the threat-intel tracking log. It does not write to
  ``production_state``, tenant overrides, the policy pipeline, the
  Blackboard, the sandbox, or any external system.
* Network access is gated on the operator running the command. Tests
  must use ``--source-file`` so the suite stays offline.
* This module must not be imported by any agent, sandbox loop, or
  production pipeline. It lives in ``scripts/`` for that reason.

Invoke from ``Runtime_Implementation/``::

    # Preview today's SMB-relevant KEV entries from the live CISA feed.
    python -m scripts.cisa_kev_ingest --dry-run --limit 5

    # Actually append (operator decision).
    python -m scripts.cisa_kev_ingest --append --limit 5

    # Offline preview against a saved snapshot (used by tests).
    python -m scripts.cisa_kev_ingest --source-file snapshot.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LOG_PATH = DEFAULT_REPO_ROOT / "THREAT_INTEL_LOG.md"

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)

# Default vendor allowlist used when --vendor-allowlist is requested but no
# explicit list is provided. Kept conservative on purpose: these are the
# vendors whose products are most commonly found in SMB and MSP-managed
# environments. Operators can override at the CLI.
DEFAULT_SMB_VENDORS = (
    "Microsoft",
    "Google",
    "Apple",
    "Cisco",
    "Fortinet",
    "SonicWall",
    "WatchGuard",
    "Citrix",
    "VMware",
    "Ivanti",
    "Atlassian",
    "Adobe",
    "Apache",
    "Progress",  # MOVEit
    "Veeam",
    "ConnectWise",
    "Kaseya",
    "Zoho",
    "GitLab",
    "Mozilla",
    "Oracle",
)

# Pattern class used in the locked log entry format for KEV-sourced
# entries. Matches the taxonomy described in THREAT_INTEL_LOG.md.
KEV_PATTERN_CLASS = "Exploitable vulnerability (known ransomware campaign use)"
KEV_PATTERN_CLASS_NON_RANSOMWARE = "Exploitable vulnerability"

# Locked markers we use when inserting entries.
INTAKE_QUEUE_MARKER = "## Empty Intake Queue"

# Locked regex for finding existing CVE IDs in entry headers. We only
# look at level-3 headers (`### ...`) so casual mentions of a CVE in
# body text do not block a re-add.
_HEADER_CVE_REGEX = re.compile(
    r"^###\s.*?(CVE-\d{4}-\d{4,7})", re.IGNORECASE | re.MULTILINE
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_kev_from_file(path: Path) -> dict[str, Any]:
    """Load a CISA KEV catalog JSON snapshot from disk."""

    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def fetch_kev_catalog(url: str = CISA_KEV_URL, *, timeout: float = 30.0) -> dict[str, Any]:
    """Fetch the CISA KEV catalog over HTTPS.

    Operator-gated: only invoked when the operator runs the CLI without
    ``--source-file``. Returns the parsed JSON document.
    """

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NorthStar-KEV-Ingest/0.1 (operator-run)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 — operator-gated
        payload = response.read()
    return json.loads(payload.decode("utf-8"))


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def filter_smb_relevant(
    catalog: dict[str, Any],
    *,
    ransomware_only: bool = True,
    vendor_allowlist: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter the KEV catalog down to SMB-relevant entries.

    ``ransomware_only`` (default ``True``) keeps only entries whose
    ``knownRansomwareCampaignUse`` field is ``"Known"`` — the strongest
    SMB-relevance signal in the KEV feed.

    ``vendor_allowlist`` (optional) further restricts entries to vendors
    matched case-insensitively. Pass an empty sequence to apply no
    vendor filter; pass ``None`` to skip vendor filtering entirely.
    """

    raw_entries = catalog.get("vulnerabilities", [])
    if not isinstance(raw_entries, list):
        return []

    allow = None
    if vendor_allowlist is not None:
        allow = {v.strip().lower() for v in vendor_allowlist if v.strip()}
        if not allow:
            allow = None

    out: list[dict[str, Any]] = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            continue
        if ransomware_only and entry.get("knownRansomwareCampaignUse") != "Known":
            continue
        if allow is not None:
            vendor = str(entry.get("vendorProject", "")).strip().lower()
            if vendor not in allow:
                continue
        if not entry.get("cveID"):
            continue
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def build_log_entry(
    kev_entry: dict[str, Any],
    *,
    today: date,
    source_url: str = CISA_KEV_URL,
) -> str:
    """Render a single KEV entry as a locked-format log block."""

    cve_id = str(kev_entry.get("cveID", "")).strip() or "CVE-UNKNOWN"
    vendor = str(kev_entry.get("vendorProject", "")).strip() or "Unknown vendor"
    product = str(kev_entry.get("product", "")).strip() or "Unknown product"
    vuln_name = str(kev_entry.get("vulnerabilityName", "")).strip()
    short_desc = str(kev_entry.get("shortDescription", "")).strip()
    required_action = str(kev_entry.get("requiredAction", "")).strip()
    due_date = str(kev_entry.get("dueDate", "")).strip() or "(none)"
    date_added = str(kev_entry.get("dateAdded", "")).strip() or "(unknown)"
    ransomware_use = str(kev_entry.get("knownRansomwareCampaignUse", "")).strip() or "Unknown"

    pattern_class = (
        KEV_PATTERN_CLASS if ransomware_use == "Known" else KEV_PATTERN_CLASS_NON_RANSOMWARE
    )

    title_bits = [cve_id, f"{vendor} {product}".strip()]
    if vuln_name:
        title_bits.append(vuln_name)
    title = " — ".join(b for b in title_bits if b)

    shape_lines: list[str] = []
    if short_desc:
        shape_lines.append(short_desc)
    if required_action:
        shape_lines.append(f"Required action: {required_action}")
    shape_lines.append(f"Due date: {due_date}.")
    pattern_shape = " ".join(shape_lines)

    evidence_bits = [
        cve_id,
        f"dateAdded {date_added}",
        f"knownRansomwareCampaignUse={ransomware_use}",
    ]
    evidence = "; ".join(evidence_bits)

    lines = [
        f"### {today.isoformat()} — CISA KEV: {title}",
        "",
        f"**Source:** CISA KEV catalog (`{source_url}`)",
        f"**Pattern class:** {pattern_class}",
        f"**Pattern shape:** {pattern_shape}",
        f"**Evidence:** {evidence}",
        "**Action taken:** None (ingestion only — operator review required)",
        "**Policy update link:** (none)",
        "**Verification:** (none)",
    ]
    return "\n".join(lines)


def render_entries(
    entries: Iterable[dict[str, Any]],
    *,
    today: date,
    source_url: str = CISA_KEV_URL,
) -> str:
    """Render a sequence of KEV entries joined with the standard separator."""

    rendered = [build_log_entry(e, today=today, source_url=source_url) for e in entries]
    if not rendered:
        return ""
    return "\n\n---\n\n".join(rendered)


# ---------------------------------------------------------------------------
# Duplicate detection and append
# ---------------------------------------------------------------------------


def existing_cve_ids(log_path: Path) -> set[str]:
    """Return the set of CVE IDs already present in log entry headers."""

    text = Path(log_path).read_text(encoding="utf-8")
    return {match.group(1).upper() for match in _HEADER_CVE_REGEX.finditer(text)}


def append_entries_to_log(log_path: Path, rendered_block: str) -> None:
    """Insert a rendered entry block above the ``Empty Intake Queue`` marker.

    Raises ``FileNotFoundError`` if the log does not exist and
    ``ValueError`` if the queue marker is missing.
    """

    if not rendered_block.strip():
        return

    path = Path(log_path)
    text = path.read_text(encoding="utf-8")
    marker_pos = text.find(INTAKE_QUEUE_MARKER)
    if marker_pos == -1:
        raise ValueError(
            f"Could not find '{INTAKE_QUEUE_MARKER}' marker in {path}"
        )

    before = text[:marker_pos].rstrip() + "\n\n"
    after = text[marker_pos:]
    new_block = rendered_block.strip() + "\n\n---\n\n"
    path.write_text(before + new_block + after, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_today(value: str | None) -> date:
    if value is None:
        return datetime.now(timezone.utc).date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_allowlist(value: str | None) -> list[str] | None:
    if value is None:
        return None
    tokens = [t.strip() for t in value.split(",") if t.strip()]
    return tokens or None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cisa_kev_ingest",
        description=(
            "Ingest SMB-relevant CISA KEV entries into THREAT_INTEL_LOG.md."
        ),
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument(
        "--source-file",
        type=Path,
        default=None,
        help="Load the KEV catalog from a local JSON file (offline mode).",
    )
    src.add_argument(
        "--url",
        type=str,
        default=CISA_KEV_URL,
        help="URL to fetch the KEV catalog from (default: CISA live feed).",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Path to THREAT_INTEL_LOG.md (default: repo root).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write the rendered entries to (preview file).",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append the rendered entries to the log. Default is dry-run.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of entries kept after filtering.",
    )
    parser.add_argument(
        "--no-ransomware-only",
        dest="ransomware_only",
        action="store_false",
        help=(
            "Disable the default knownRansomwareCampaignUse=Known filter. "
            "Use with caution — recall is high without it."
        ),
    )
    parser.set_defaults(ransomware_only=True)
    parser.add_argument(
        "--vendor-allowlist",
        type=str,
        default=None,
        help=(
            "Comma-separated vendor allowlist. Pass 'default' to use the "
            "built-in SMB vendor list."
        ),
    )
    parser.add_argument(
        "--no-skip-duplicates",
        dest="skip_duplicates",
        action="store_false",
        help="Do not skip CVE IDs already present in the log.",
    )
    parser.set_defaults(skip_duplicates=True)
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout (seconds) for live fetch.",
    )
    parser.add_argument(
        "--today",
        type=str,
        default=None,
        help="Override today's date (YYYY-MM-DD) for deterministic output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.source_file is not None:
        catalog = load_kev_from_file(args.source_file)
        source_url = f"file://{Path(args.source_file).resolve().as_posix()}"
    else:
        catalog = fetch_kev_catalog(args.url, timeout=args.timeout)
        source_url = args.url

    vendor_arg = args.vendor_allowlist
    if vendor_arg == "default":
        vendor_allowlist: list[str] | None = list(DEFAULT_SMB_VENDORS)
    else:
        vendor_allowlist = _parse_allowlist(vendor_arg)

    filtered = filter_smb_relevant(
        catalog,
        ransomware_only=args.ransomware_only,
        vendor_allowlist=vendor_allowlist,
    )

    if args.skip_duplicates and args.log_path.exists():
        existing = existing_cve_ids(args.log_path)
        filtered = [e for e in filtered if str(e.get("cveID", "")).upper() not in existing]

    if args.limit is not None:
        filtered = filtered[: max(args.limit, 0)]

    today = _parse_today(args.today)
    rendered = render_entries(filtered, today=today, source_url=source_url)

    summary = {
        "fetched_total": len(catalog.get("vulnerabilities", []) or []),
        "filtered_count": len(filtered),
        "ransomware_only": args.ransomware_only,
        "vendor_allowlist": vendor_allowlist,
        "skip_duplicates": args.skip_duplicates,
        "appended": False,
        "log_path": str(args.log_path),
        "out_path": str(args.out) if args.out is not None else None,
        "source": source_url,
    }

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + ("\n" if rendered else ""), encoding="utf-8")

    if args.append and filtered:
        append_entries_to_log(args.log_path, rendered)
        summary["appended"] = True

    print(json.dumps(summary, indent=2, sort_keys=True))
    if not args.append:
        print()
        if rendered:
            print(rendered)
        else:
            print("(no SMB-relevant KEV entries matched the current filters)")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main(sys.argv[1:]))
