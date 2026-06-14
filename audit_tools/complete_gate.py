"""Grok completion gate — fires at readiness boundaries only.

Purpose
-------
Grok audit must trigger when an AI worker (or the operator) claims that
work is ready, done, signed-off, or ready to ship/commit — and not during
normal exploration or operator-directed work in progress. This gate is
the enforced choke point for that claim.

The shape of the failure mode this prevents is the 2026-05-23 weekend
"Pass-1 wiring bug": a file was touched during a build but was not in
the audit packet given to Grok, so the audit silently approved a
package that had a real defect in an unreviewed file. The fix is
structural: the gate, not the worker, decides what goes in the audit
packet, and any touched file outside the packet is a hard failure.

Authority model
---------------
- Matt decides.
- Cursor / Claude / Codex build.
- Grok is a *negative-feedback auditor* (find deviations; do not score,
  do not approve, do not assess strategy).
- This script is *infrastructure*. It does not change product behaviour
  and it does not mark anything complete by itself.

Bootstrap exception (historical record)
---------------------------------------
The v1.0 creation of this file was an operator-authorized bootstrap
action accepted manually by Matt on 2026-05-26. The bootstrap itself
was therefore not audited by this gate.

v1.1 transition (2026-05-26): ``INCLUDE_AUDIT_TOOLS_IN_SCOPE`` is now
``True``. Changes to ``audit_tools/`` from this point onward fall
inside the gate's hook scope and will trigger the gate when invoked
in ``--pre-commit`` mode (or in any explicit ``--task`` run that
touches files under ``audit_tools/``).

Usage
-----
Full gate run::

    python audit_tools/complete_gate.py \\
        --task cyber_insurance_evidence_package \\
        --claim "spec cleanup pass ready for review"

Pre-commit wrapper (checks scope first, runs the gate only on scoped paths)::

    python audit_tools/complete_gate.py --pre-commit

Operator override (auditable, generates a warning-level drift incident)::

    python audit_tools/complete_gate.py \\
        --task <task> --claim "<claim>" \\
        --operator-override "<reason>"

A ``.git/hooks/pre-commit`` snippet that wires this into git is in the
README block at the bottom of this file. The hook is *not* installed by
this script (no mutation of git config); the operator installs it
manually if desired.

Boundaries
----------
- Reads ``XAI_API_KEY`` (and optional ``XAI_MODEL``) from ``.env`` at
  the workspace root. Never prints, logs, persists, or echoes the key.
- Writes outputs under ``audit_outputs/``, which is git-ignored.
- Does not touch Blackboard, production state, operator state, or any
  runtime surface. The gate only reads existing files and writes audit
  records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = WORKSPACE_ROOT / ".env"
OUTPUT_DIR = WORKSPACE_ROOT / "audit_outputs"
PENDING_MANIFEST_DIR = OUTPUT_DIR / "pending"
DRIFT_INCIDENT_DIR = OUTPUT_DIR / "drift_incidents"

XAI_ENDPOINT = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4"
REQUEST_TIMEOUT_SECONDS = 60
REQUEST_RETRIES = 1

PER_FILE_CAP_BYTES = 50_000
TOTAL_PACKET_CAP_BYTES = 200_000
TRUNCATION_MARKER = "\n... [TRUNCATED at 50KB per per-file cap] ...\n"

# v1.1 onward: audit_tools/ is in the gate's hook scope. The 2026-05-26
# v1.0 bootstrap (initial creation of complete_gate.py + tests) was
# operator-authorized by Matt directly and not audited by this gate;
# every revision after that bootstrap, including this v1.1 transition,
# is in scope.
INCLUDE_AUDIT_TOOLS_IN_SCOPE = True

# Hook scope prefixes are evaluated against workspace-relative paths
# using forward-slash separators.
HOOK_SCOPE_PREFIXES_ALWAYS: tuple[str, ...] = (
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/",
    # Cyber Insurance Evidence Package generator: the §18.3 authorized code
    # home. Added 2026-06-04 (loop-review Fix B) so this code path actually
    # auto-fires the gate and --pre-commit mode cannot false-pass it.
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/",
    # Layer 6 Control Plane + governed-ensemble build homes. Added 2026-06-14
    # so control-plane builds (Safe-Stop, Mode Controller, Privacy Filter,
    # Watchers, Fission, Mutation, Reconciliation) auto-fire the gate and
    # --pre-commit mode cannot false-pass them.
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/safe_stop/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/control_plane/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/watchers/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/fission/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/mutation/",
    "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/reconciliation/",
    "production_state/",
    "1. Business_Operations/Client_Documents/",
)

# 4. Product_Roadmap/*.md is conditional: only signed-§11 specs fire
# the gate. Pre-§11 drafts can be iterated without ceremony.
PRODUCT_ROADMAP_PREFIX = "4. Product_Roadmap/"
AUDIT_TOOLS_PREFIX = "audit_tools/"

# §11 SIGNED marker convention: a signed spec includes this exact
# string near the top of the file (matches pre_ship_audit.py).
SIGNED_SPEC_MARKER_PRIMARY = "§11 SIGNED"
SIGNED_SPEC_MARKER_SECONDARY = "LOCKED BY"
# Some signed contracts state the status as "SIGNED — §11 ..." (dash form)
# rather than the canonical "§11 SIGNED" token. Accept that phrasing too so a
# signed contract is not mis-read as unsigned by the gate. The em dash is the
# one used in the contract status lines.
SIGNED_SPEC_MARKER_DASH = "SIGNED — §11"
SIGNED_SPEC_HEAD_BYTES = 1500

# Canonical forbidden-language list — enforcement form.
#
# Source-of-truth (per §11 SIGNED 2026-05-26, decisions D6 / D7 in
# `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md`):
#   - `Compliance_and_Trend_Watch_Process.md` §5.1 (prose form) is the
#     project-wide canonical compliance-claim boundary.
#   - `Cyber_Insurance_Evidence_Package_Deep_Dive.md` §9 is the
#     buyer-surface application of that boundary, in enforcement-phrase
#     form. On any future divergence between the two, §5.1 wins and the
#     buyer-surface artifact updates to match.
#   - This constant is the runtime *enforcement* mirror of those lists.
#     Values stay in sync with the §5.1 / §9 phrase set; only the
#     cited-as-canonical authority changed at the 2026-05-26 sign-off.
#
# Allowed contexts (boundary, non-scope, forbidden-language, bad-example)
# are mentioned to the auditor in the prompt — the gate itself does not
# parse contexts, it surfaces them to Grok.
FORBIDDEN_LANGUAGE_LIST: tuple[str, ...] = (
    "guaranteed",
    "guarantee",
    "bulletproof",
    "fully secure",
    "100% secure",
    "complete security",
    "compliant",
    "compliance",
    "SOC 2",
    "SOC2",
    "ISO 27001",
    "HIPAA",
    "PCI",
    "attestation",
    "prevents all",
    "stops all",
    "eliminates all",
    "replaces your",
)

# Canonical vocabulary-translation list — enforcement form.
#
# Source-of-truth: `Compliance_and_Trend_Watch_Process.md` §5.5
# "Vocabulary-translation list (v1, canonical)" per D6 (2026-05-26
# §11 sign-off). The Cyber Insurance Evidence Package §9 carries the
# buyer-surface rendering of the same list. Values match the §5.5
# v1 canonical mapping; only the cited authority changed at the
# 2026-05-26 sign-off.
VOCABULARY_TRANSLATION_LIST: tuple[tuple[str, str], ...] = (
    ("control efficacy", "how well this control works in practice"),
    ("regulatory mapping", "cross-reference to specific underwriting questions"),
    ("compensating control", "a different control that addresses the same risk"),
    (
        "control attestation framework",
        "the way we record what each control does",
    ),
    ("material weakness", "a meaningful gap"),
)


# ---------------------------------------------------------------------------
# Grok prompt — split into the fixed negative-feedback contract and a
# small output-format instruction the gate uses to parse the response.
# The contract text is the prompt Matt locked; do not edit it casually.
# ---------------------------------------------------------------------------

NEGATIVE_FEEDBACK_PROMPT = (
    "Identify any deviations from the supplied contracts, signed specs, "
    "project non-negotiables, touched-file coverage rule, scope boundary, "
    "forbidden-language list, vocabulary-translation list, and done "
    "criteria. Do not score. Do not approve. Do not assess "
    "product-market fit or strategic alignment. Report only deviations "
    "and gaps. Categorize each deviation as blocking or warning using "
    "the Drift Incident Report schema: blocking = the work cannot ship "
    "as complete; warning = work can ship but the deviation is recorded."
)

OUTPUT_FORMAT_INSTRUCTION = (
    "\n\nOutput format:\n"
    "  - For each deviation, write one paragraph beginning with either "
    "`BLOCKING:` or `WARNING:` followed by a one-line summary, then the "
    "supporting evidence. Include the file path and the contract that "
    "was deviated from.\n"
    "  - Forbidden-language phrases (e.g. `SOC 2`, `attestation`, "
    "`guaranteed`) are *allowed* inside the spec's own non-scope, "
    "forbidden-language list, boundary, and bad-example contexts. Only "
    "flag them when they appear as actual NorthStar claims outside "
    "those contexts.\n"
    "\n"
    "Evidence requirement (mandatory; the operator treats output that "
    "skips this as a rubber-stamp signal, not a clean audit):\n"
    "  - If you report no deviations, you must not answer with only "
    "`no deviations found.` A bare zero-finding statement is "
    "non-compliant with this prompt because it is not audit evidence. "
    "Instead, write a short paragraph that names at least three of: "
    "(a) the staged or touched files you examined, (b) the contract "
    "clauses or signed-spec sections you cross-checked, (c) the "
    "non-negotiables you confirmed were not contradicted, "
    "(d) the forbidden-language / vocabulary lists you scanned. Be "
    "concrete — name the file path and the section anchor.\n"
    "  - If the packet is too large or you cannot inspect enough of it "
    "to make a judgement on any of those checks, say "
    "`insufficient context` and name what context is missing rather "
    "than confidently reporting clean. The operator treats "
    "`I don't know` as cleaner signal than a confident misread.\n"
    "  - Before the machine-readable summary line, include one short "
    "`Evidence quality:` paragraph stating whether your review was "
    "comprehensive, partial, or limited, and why.\n"
    "\n"
    "Machine-readable summary (always last line of the response):\n"
    "  - End your response with exactly one summary line in this form:\n"
    "        GATE_SUMMARY: blocking=<N> warnings=<M>\n"
    "    where N and M are integers. N=0 and M=0 means a clean audit."
)


# ---------------------------------------------------------------------------
# Errors — each category gets a distinct exit code so a shell wrapper can
# distinguish "the gate refused because of coverage" from "Grok is down".
# ---------------------------------------------------------------------------

EXIT_OK = 0
EXIT_BLOCKING_DEVIATION = 2
EXIT_MANIFEST_VERIFICATION = 3
EXIT_PACKET_COVERAGE = 4
EXIT_PACKET_TOO_LARGE = 5
EXIT_GROK_CALL_FAILED = 6
EXIT_GROK_OUTPUT_INVALID = 7
EXIT_USAGE = 64


class GateError(Exception):
    """Raised when the gate refuses to ship."""

    exit_code = EXIT_BLOCKING_DEVIATION

    def __init__(self, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class ManifestVerificationError(GateError):
    exit_code = EXIT_MANIFEST_VERIFICATION


class PacketCoverageError(GateError):
    exit_code = EXIT_PACKET_COVERAGE


class PacketTooLargeError(GateError):
    exit_code = EXIT_PACKET_TOO_LARGE


class GrokCallError(GateError):
    exit_code = EXIT_GROK_CALL_FAILED


class GrokOutputError(GateError):
    exit_code = EXIT_GROK_OUTPUT_INVALID


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Manifest:
    task_id: str
    completion_claim: str
    files_read: tuple[str, ...] = ()
    files_modified: tuple[str, ...] = ()
    files_created: tuple[str, ...] = ()
    commands_run: tuple[str, ...] = ()
    known_unresolved_questions: tuple[str, ...] = ()
    relevant_contracts: tuple[str, ...] = ()


@dataclass(frozen=True)
class GitChangeSummary:
    changed_files: tuple[str, ...]
    diff: str
    status: str


@dataclass(frozen=True)
class AuditPacket:
    text: str
    packet_hash: str
    size_bytes: int
    touched_files: tuple[str, ...]
    relevant_contracts: tuple[str, ...]


@dataclass(frozen=True)
class GrokAuditResult:
    content: str
    blocking_count: int
    warning_count: int
    summary_line: str


@dataclass(frozen=True)
class CachedAudit:
    path: Path
    packet_hash: str


# ---------------------------------------------------------------------------
# Manifest handling
# ---------------------------------------------------------------------------

def manifest_path_for(task_id: str) -> Path:
    return PENDING_MANIFEST_DIR / f"{task_id}.manifest.json"


def load_manifest(task_id: str) -> Manifest | None:
    """Return the worker manifest for ``task_id`` if present, else None."""

    path = manifest_path_for(task_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestVerificationError(
            f"manifest at {path} is unreadable or not JSON: {exc}"
        )
    if not isinstance(data, dict):
        raise ManifestVerificationError(
            f"manifest at {path} must be a JSON object"
        )

    if data.get("task_id") and data["task_id"] != task_id:
        raise ManifestVerificationError(
            f"manifest task_id {data['task_id']!r} does not match invoked "
            f"task_id {task_id!r}"
        )

    def _tuple(key: str) -> tuple[str, ...]:
        value = data.get(key, [])
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ManifestVerificationError(
                f"manifest field {key!r} must be a list of strings"
            )
        return tuple(value)

    completion_claim = data.get("completion_claim", "")
    if not isinstance(completion_claim, str) or not completion_claim.strip():
        raise ManifestVerificationError(
            "manifest must include a non-empty `completion_claim`"
        )

    return Manifest(
        task_id=task_id,
        completion_claim=completion_claim,
        files_read=_tuple("files_read"),
        files_modified=_tuple("files_modified"),
        files_created=_tuple("files_created"),
        commands_run=_tuple("commands_run"),
        known_unresolved_questions=_tuple("known_unresolved_questions"),
        relevant_contracts=_tuple("relevant_contracts"),
    )


# ---------------------------------------------------------------------------
# Git discovery
# ---------------------------------------------------------------------------

def _normalise_git_path(raw: str) -> str:
    cleaned = raw.strip().strip('"').replace("\\", "/")
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1].strip().strip('"')
    return cleaned


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise GateError(
            f"git {' '.join(args)} failed: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def collect_git_changed_files(*, staged_only: bool = False) -> GitChangeSummary:
    """Collect changed files visible to git.

    Includes:
      - Tracked diff vs HEAD (or vs index if staged_only).
      - Untracked files not in .gitignore.

    Git-ignored files are deliberately excluded from this set — they are
    handled by the manifest's ``files_modified`` / ``files_created`` lists
    (see ``build_touched_files_set``).
    """

    if staged_only:
        diff = _run_git(["diff", "--cached"])
        name_only = _run_git(["diff", "--cached", "--name-only"])
        status = _run_git(["status", "--short"])
    else:
        diff = _run_git(["diff", "HEAD"])
        name_only = _run_git(["diff", "HEAD", "--name-only"])
        status = _run_git(["status", "--short"])

    changed: set[str] = set()
    for line in name_only.splitlines():
        cleaned = _normalise_git_path(line)
        if cleaned:
            changed.add(cleaned)

    if not staged_only:
        untracked = _run_git(
            ["ls-files", "--others", "--exclude-standard"]
        ).splitlines()
        for line in untracked:
            cleaned = _normalise_git_path(line)
            if cleaned:
                changed.add(cleaned)

    return GitChangeSummary(
        changed_files=tuple(sorted(changed)),
        diff=diff,
        status=status,
    )


# ---------------------------------------------------------------------------
# Manifest verification + touched-files set
# ---------------------------------------------------------------------------

def _path_is_git_ignored(path: str) -> bool:
    """Return True if git itself says the path is ignored."""

    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def verify_manifest(manifest: Manifest, git_summary: GitChangeSummary) -> None:
    """Cross-check the manifest against git.

    Rules:
      - Every git-changed file must appear in manifest files_modified
        or files_created (so the worker cannot quietly omit a file the
        gate would catch as a coverage gap).
      - Every manifest-claimed modified/created file must either show
        up in git, or be a git-ignored path. Anything else means the
        manifest is lying about what changed.
      - files_read is manifest-exclusive (git cannot observe reads),
        so it is not cross-checked here.
    """

    git_set = set(git_summary.changed_files)
    manifest_set = set(manifest.files_modified) | set(manifest.files_created)
    manifest_set_normalised = {p.replace("\\", "/") for p in manifest_set}

    missing_from_manifest = sorted(git_set - manifest_set_normalised)
    if missing_from_manifest:
        raise ManifestVerificationError(
            "git shows files changed that the worker manifest omits "
            "(coverage-gap risk; the worker must list every modified "
            "file):\n  - " + "\n  - ".join(missing_from_manifest)
        )

    extra_from_manifest = sorted(manifest_set_normalised - git_set)
    bogus: list[str] = []
    for path in extra_from_manifest:
        full = WORKSPACE_ROOT / path
        if not full.exists():
            bogus.append(f"{path} (does not exist on disk)")
        elif not _path_is_git_ignored(path):
            bogus.append(f"{path} (git shows no change and path is not ignored)")
    if bogus:
        raise ManifestVerificationError(
            "manifest claims files were modified/created that git cannot "
            "see and that are not git-ignored:\n  - " + "\n  - ".join(bogus)
        )


def build_touched_files_set(
    manifest: Manifest | None,
    git_summary: GitChangeSummary,
) -> tuple[str, ...]:
    """Touched-files set per the deep-dive contract.

    Touched = git changed + manifest files_modified + manifest files_created
            + manifest files_read.
    """

    touched: set[str] = set(git_summary.changed_files)
    if manifest is not None:
        for path in manifest.files_modified:
            touched.add(path.replace("\\", "/"))
        for path in manifest.files_created:
            touched.add(path.replace("\\", "/"))
        for path in manifest.files_read:
            touched.add(path.replace("\\", "/"))
    return tuple(sorted(touched))


# ---------------------------------------------------------------------------
# Contract extraction
# ---------------------------------------------------------------------------

def extract_vision_non_negotiables() -> str:
    """Return the Non-Negotiables section from VISION.md, or a sentinel."""

    path = WORKSPACE_ROOT / "VISION.md"
    if not path.exists():
        return "<VISION.md not found>"
    text = path.read_text(encoding="utf-8")
    anchor = "## Non-Negotiables"
    start = text.find(anchor)
    if start == -1:
        return "<Non-Negotiables anchor not found in VISION.md>"
    tail = text[start:]
    next_section = tail.find("\n## ", len(anchor))
    if next_section == -1:
        return tail.strip()
    return tail[:next_section].strip()


def _is_signed_spec(path: Path) -> bool:
    """Return True if ``path`` carries a §11-signed marker near its top."""

    try:
        head = path.read_text(encoding="utf-8")[:SIGNED_SPEC_HEAD_BYTES]
    except OSError:
        return False
    if SIGNED_SPEC_MARKER_PRIMARY in head:
        return True
    if SIGNED_SPEC_MARKER_DASH in head:
        return True
    if SIGNED_SPEC_MARKER_SECONDARY in head and "SIGNED" in head:
        return True
    return False


def collect_relevant_signed_specs(
    manifest: Manifest | None,
    touched_files: Iterable[str],
) -> list[Path]:
    """Return signed §11 specs relevant to this task.

    Resolution order:
      1. If the manifest names ``relevant_contracts``, every named entry
         must exist on disk and carry a signed-§11 marker. Missing files
         and unsigned files are hard failures (``ManifestVerificationError``)
         because the manifest claims a contract that cannot be audited
         against.
      2. Else, any signed spec that appears in the touched-files set.
      3. Else, no specs (the gate still runs, but Grok audits against
         the always-included contracts: VISION non-negotiables, scope
         boundary, forbidden language, vocabulary).
    """

    spec_dir = WORKSPACE_ROOT / "4. Product_Roadmap"

    if manifest is not None and manifest.relevant_contracts:
        named: list[Path] = []
        missing: list[str] = []
        unsigned: list[str] = []
        for relpath in manifest.relevant_contracts:
            candidate = WORKSPACE_ROOT / relpath
            if not candidate.exists() or not candidate.is_file():
                missing.append(relpath)
                continue
            if not _is_signed_spec(candidate):
                unsigned.append(relpath)
                continue
            named.append(candidate)
        problems: list[str] = []
        if missing:
            problems.append(
                "manifest names relevant_contracts that do not exist on "
                "disk:\n  - " + "\n  - ".join(missing)
            )
        if unsigned:
            problems.append(
                "manifest names relevant_contracts that are not §11-signed "
                "(an unsigned spec cannot be audited against — sign the "
                "spec, or remove it from relevant_contracts):\n  - "
                + "\n  - ".join(unsigned)
            )
        if problems:
            raise ManifestVerificationError("\n\n".join(problems))
        return named

    if not spec_dir.exists():
        return []

    touched_norm = {p.replace("\\", "/") for p in touched_files}
    discovered: list[Path] = []
    for spec_path in sorted(spec_dir.glob("*Deep_Dive*.md")):
        rel = spec_path.relative_to(WORKSPACE_ROOT).as_posix()
        if rel in touched_norm and _is_signed_spec(spec_path):
            discovered.append(spec_path)
    return discovered


# The Cyber Insurance Evidence Package deep-dive is the canonical source
# of the scope-boundary statement. The gate must surface the EXACT quoted
# boundary text (not a paraphrase) so Grok can detect any drift between
# the contract in the spec and the boundary in a generated artifact.
SCOPE_BOUNDARY_SPEC_PATH = (
    "4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md"
)
SCOPE_BOUNDARY_ANCHOR = "### Required boundary statement"


def extract_scope_boundary() -> str:
    """Return the exact §2 scope-boundary text from the deep-dive.

    Returns a clearly-marked sentinel string on missing-file or missing-anchor
    so Grok can see the gap and raise it as a blocking deviation.
    """

    spec_path = WORKSPACE_ROOT / SCOPE_BOUNDARY_SPEC_PATH
    if not spec_path.exists():
        return (
            f"<scope-boundary contract file not found at "
            f"{SCOPE_BOUNDARY_SPEC_PATH}; deep-dive must be present>"
        )
    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"<scope-boundary contract file unreadable: {exc}>"

    anchor_idx = text.find(SCOPE_BOUNDARY_ANCHOR)
    if anchor_idx == -1:
        return (
            f"<scope-boundary anchor {SCOPE_BOUNDARY_ANCHOR!r} not found in "
            f"{SCOPE_BOUNDARY_SPEC_PATH}; spec has drifted>"
        )

    # Slice from the anchor to the next "###" or "---" delimiter so we
    # carry the full block (anchor heading + blockquote + any commentary
    # immediately under it). Grok then reads the contractual text in
    # context, not paraphrased.
    tail = text[anchor_idx:]
    candidates: list[int] = []
    for delim in ("\n### ", "\n---\n", "\n## "):
        idx = tail.find(delim, len(SCOPE_BOUNDARY_ANCHOR))
        if idx != -1:
            candidates.append(idx)
    if candidates:
        return tail[: min(candidates)].strip()
    return tail.strip()


def extract_done_criteria(spec_text: str) -> str:
    """Pull the Done Criteria section from a deep-dive, if present."""

    for anchor in ("§11 Done Criteria", "## §11 Done Criteria", "## Done Criteria"):
        start = spec_text.find(anchor)
        if start == -1:
            continue
        tail = spec_text[start:]
        next_section = tail.find("\n## §", len(anchor))
        if next_section == -1:
            next_section = tail.find("\n## ", len(anchor))
        if next_section == -1:
            return tail.strip()
        return tail[:next_section].strip()
    return ""


# ---------------------------------------------------------------------------
# Audit packet
# ---------------------------------------------------------------------------

def _truncate_to_byte_cap(text: str, cap_bytes: int) -> str:
    """Return ``text`` truncated to at most ``cap_bytes`` UTF-8 bytes.

    Slicing on the encoded bytes guarantees the byte cap is honoured
    even for multi-byte UTF-8 sequences. ``errors='ignore'`` drops any
    partial multi-byte character at the boundary so the returned string
    is always valid UTF-8.
    """

    encoded = text.encode("utf-8")
    if len(encoded) <= cap_bytes:
        return text
    truncated = encoded[:cap_bytes].decode("utf-8", errors="ignore")
    return truncated + TRUNCATION_MARKER


def _read_file_capped(path: Path) -> str:
    try:
        data = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "<binary or non-utf8 file omitted from packet>"
    except OSError as exc:
        return f"<unreadable: {exc}>"
    return _truncate_to_byte_cap(data, PER_FILE_CAP_BYTES)


def _format_forbidden_language() -> str:
    return "\n".join(f"  - {phrase}" for phrase in FORBIDDEN_LANGUAGE_LIST)


def _format_vocabulary_translation() -> str:
    return "\n".join(
        f"  - {jargon} → {plain}"
        for jargon, plain in VOCABULARY_TRANSLATION_LIST
    )


def assemble_audit_packet(
    *,
    task_id: str,
    completion_claim: str,
    manifest: Manifest | None,
    git_summary: GitChangeSummary,
    touched_files: tuple[str, ...],
    relevant_specs: list[Path],
) -> AuditPacket:
    """Build the audit packet text + hash + size."""

    parts: list[str] = []

    parts.append(f"=== TASK ===\ntask_id: {task_id}\n")
    parts.append(f"completion_claim: {completion_claim}\n\n")

    if manifest is not None:
        parts.append("=== WORKER MANIFEST ===\n")
        parts.append(
            json.dumps(
                {
                    "task_id": manifest.task_id,
                    "completion_claim": manifest.completion_claim,
                    "files_read": list(manifest.files_read),
                    "files_modified": list(manifest.files_modified),
                    "files_created": list(manifest.files_created),
                    "commands_run": list(manifest.commands_run),
                    "known_unresolved_questions": list(
                        manifest.known_unresolved_questions
                    ),
                    "relevant_contracts": list(manifest.relevant_contracts),
                },
                indent=2,
            )
        )
        parts.append("\n\n")
    else:
        parts.append("=== WORKER MANIFEST ===\n(no manifest supplied; "
                     "manifest path checked at "
                     f"{manifest_path_for(task_id).as_posix()})\n\n")

    parts.append("=== TOUCHED FILES (git + manifest union) ===\n")
    for path in touched_files:
        parts.append(f"  - {path}\n")
    parts.append("\n")

    parts.append("=== GIT STATUS ===\n")
    parts.append(git_summary.status or "(clean)")
    parts.append("\n\n")

    parts.append("=== GIT DIFF (truncated to per-file cap) ===\n")
    diff = _truncate_to_byte_cap(git_summary.diff, PER_FILE_CAP_BYTES)
    parts.append(diff or "(no tracked-file diff)")
    parts.append("\n\n")

    parts.append("=== VISION.md NON-NEGOTIABLES ===\n")
    parts.append(extract_vision_non_negotiables())
    parts.append("\n\n")

    parts.append(
        "=== SCOPE BOUNDARY (exact extract from Cyber Insurance Evidence "
        "Package deep-dive) ===\n"
    )
    parts.append(extract_scope_boundary())
    parts.append("\n\n")

    parts.append("=== FORBIDDEN-LANGUAGE LIST ===\n")
    parts.append(_format_forbidden_language())
    parts.append(
        "\n\n(Allowed inside the spec's own non-scope, forbidden-language, "
        "boundary, and bad-example contexts. Only flag as a deviation when "
        "any of these phrases appears as an actual NorthStar claim outside "
        "those contexts.)\n\n"
    )

    parts.append("=== VOCABULARY-TRANSLATION LIST ===\n")
    parts.append(_format_vocabulary_translation())
    parts.append("\n\n")

    if relevant_specs:
        parts.append("=== RELEVANT SIGNED §11 SPECS ===\n")
        for spec_path in relevant_specs:
            rel = spec_path.relative_to(WORKSPACE_ROOT).as_posix()
            parts.append(f"\n--- {rel} ---\n")
            parts.append(_read_file_capped(spec_path))
            parts.append("\n")
            done = extract_done_criteria(spec_path.read_text(encoding="utf-8"))
            if done:
                parts.append(f"\n--- {rel} : Done Criteria excerpt ---\n")
                parts.append(_truncate_to_byte_cap(done, PER_FILE_CAP_BYTES))
                parts.append("\n")
        parts.append("\n")
    else:
        parts.append("=== RELEVANT SIGNED §11 SPECS ===\n(none signed "
                     "for this task; auditor reviews against non-negotiables "
                     "and scope boundary only)\n\n")

    parts.append("=== FULL CONTENTS OF TOUCHED FILES ===\n")
    for path in touched_files:
        full = WORKSPACE_ROOT / path
        if not full.exists():
            parts.append(f"\n--- {path} ---\n<file does not exist>\n")
            continue
        if not full.is_file():
            parts.append(f"\n--- {path} ---\n<not a regular file>\n")
            continue
        parts.append(f"\n--- {path} ---\n")
        parts.append(_read_file_capped(full))
        parts.append("\n")

    if manifest is not None and manifest.known_unresolved_questions:
        parts.append("\n=== KNOWN UNRESOLVED QUESTIONS ===\n")
        for question in manifest.known_unresolved_questions:
            parts.append(f"  - {question}\n")

    text = "".join(parts)
    size_bytes = len(text.encode("utf-8"))

    if size_bytes > TOTAL_PACKET_CAP_BYTES:
        raise PacketTooLargeError(
            f"audit_packet_too_large: packet is {size_bytes:,} bytes "
            f"(cap {TOTAL_PACKET_CAP_BYTES:,}). Split this work into "
            "smaller commits and re-run the gate on each piece."
        )

    packet_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return AuditPacket(
        text=text,
        packet_hash=packet_hash,
        size_bytes=size_bytes,
        touched_files=touched_files,
        relevant_contracts=tuple(
            spec.relative_to(WORKSPACE_ROOT).as_posix() for spec in relevant_specs
        ),
    )


# ---------------------------------------------------------------------------
# Packet coverage check (post-assemble sanity)
# ---------------------------------------------------------------------------

def verify_packet_coverage(packet: AuditPacket) -> None:
    """Confirm every touched file appears as a section header in the packet."""

    missing: list[str] = []
    for path in packet.touched_files:
        marker = f"--- {path} ---"
        if marker not in packet.text:
            missing.append(path)
    if missing:
        raise PacketCoverageError(
            "audit packet is missing sections for touched files "
            "(the 2026-05-23 wiring-bug failure shape):\n  - "
            + "\n  - ".join(missing)
        )


# ---------------------------------------------------------------------------
# Cached-audit lookup
# ---------------------------------------------------------------------------

PACKET_HASH_HEADER_KEY = "Packet-SHA256"


def find_cached_audit(task_id: str, packet_hash: str) -> CachedAudit | None:
    """Return an existing audit output file matching this packet hash."""

    if not OUTPUT_DIR.exists():
        return None
    for candidate in sorted(OUTPUT_DIR.glob(f"{task_id}_*.md")):
        try:
            head = candidate.read_text(encoding="utf-8")[:2000]
        except OSError:
            continue
        match = re.search(
            rf"{re.escape(PACKET_HASH_HEADER_KEY)}.*?`([0-9a-f]{{64}})`",
            head,
        )
        if match and match.group(1) == packet_hash:
            return CachedAudit(path=candidate, packet_hash=packet_hash)
    return None


# ---------------------------------------------------------------------------
# Grok call
# ---------------------------------------------------------------------------

def load_xai_credentials(env_path: Path) -> tuple[str, str]:
    """Load XAI_API_KEY and optional XAI_MODEL from .env.

    The key is read once and never echoed. Other env variables are
    intentionally ignored.
    """

    if not env_path.exists():
        raise GrokCallError(
            f"missing .env at {env_path}. Add XAI_API_KEY=... and re-run, "
            "or pass --operator-override <reason>."
        )

    api_key: str | None = None
    model: str | None = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "XAI_API_KEY":
            api_key = value
        elif key == "XAI_MODEL":
            model = value
    if not api_key:
        raise GrokCallError(
            "XAI_API_KEY not set in .env. Add a line like\n"
            "    XAI_API_KEY=xai-...\n"
            "and re-run. Do not paste the key into chat."
        )
    return api_key, model or DEFAULT_MODEL


def _categorize_http_failure(status: int, reason: str, detail: str) -> str:
    if status in (401, 403):
        return f"grok_call_auth_failed: HTTP {status} {reason}"
    if status == 429:
        return f"grok_call_rate_limited: HTTP {status} {reason}"
    if 500 <= status < 600:
        return f"grok_call_server_error: HTTP {status} {reason}: {detail[:200]}"
    return f"grok_call_http_error: HTTP {status} {reason}: {detail[:200]}"


def call_grok(*, api_key: str, model: str, payload: str) -> str:
    """POST a single request to xAI with 60s timeout + one retry.

    Distinct error messages for each failure category so a wrapper can
    decide whether to retry, escalate, or pass through.
    """

    full_prompt = NEGATIVE_FEEDBACK_PROMPT + OUTPUT_FORMAT_INSTRUCTION

    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": payload},
        ],
    }
    request = urllib.request.Request(
        url=XAI_ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    last_error: GrokCallError | None = None
    for attempt in range(REQUEST_RETRIES + 1):
        try:
            with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT_SECONDS
            ) as resp:
                response_body = resp.read().decode("utf-8")
            parsed = json.loads(response_body)
            return parsed["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - detail is best-effort
                detail = ""
            message = _categorize_http_failure(exc.code, exc.reason, detail)
            last_error = GrokCallError(message)
            if exc.code in (401, 403) or 400 <= exc.code < 500 and exc.code != 429:
                # Auth failures and 4xx (non-429) are not retryable.
                break
        except urllib.error.URLError as exc:
            reason = str(exc.reason)
            if "timed out" in reason.lower():
                last_error = GrokCallError(
                    f"grok_call_timeout: request exceeded "
                    f"{REQUEST_TIMEOUT_SECONDS}s ({reason})"
                )
            else:
                last_error = GrokCallError(
                    f"grok_call_network_error: {reason}"
                )
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            last_error = GrokCallError(
                f"grok_call_unexpected_response_shape: {exc}"
            )
            break

    assert last_error is not None  # noqa: S101 - logic guard
    raise last_error


# ---------------------------------------------------------------------------
# Grok response parsing
# ---------------------------------------------------------------------------

GATE_SUMMARY_RE = re.compile(
    r"^GATE_SUMMARY:\s*blocking\s*=\s*(\d+)\s+warnings\s*=\s*(\d+)\s*$",
    re.MULTILINE,
)


def parse_gate_summary(content: str) -> GrokAuditResult:
    """Extract blocking/warning counts from a Grok response."""

    matches = list(GATE_SUMMARY_RE.finditer(content))
    if not matches:
        raise GrokOutputError(
            "grok_output_missing_summary: no `GATE_SUMMARY: blocking=N "
            "warnings=M` line found in Grok response. Auditor may have "
            "ignored the output-format instruction."
        )
    if len(matches) > 1:
        raise GrokOutputError(
            "grok_output_multiple_summaries: Grok response contains "
            f"{len(matches)} GATE_SUMMARY lines; expected exactly one."
        )
    blocking = int(matches[0].group(1))
    warnings = int(matches[0].group(2))
    return GrokAuditResult(
        content=content,
        blocking_count=blocking,
        warning_count=warnings,
        summary_line=matches[0].group(0).strip(),
    )


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_grok_output(
    *,
    task_id: str,
    model: str,
    packet: AuditPacket,
    result: GrokAuditResult,
) -> Path:
    """Write the Grok response to disk with the packet hash in the header.

    The packet hash is the freshness anchor: a future run with the same
    touched files + same contents will hit this same file via
    ``find_cached_audit`` and skip the Grok call.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _utc_timestamp()
    output_path = OUTPUT_DIR / f"{task_id}_{timestamp}.md"
    header = (
        f"# Grok Completion Audit — {task_id}\n\n"
        f"- **Model:** `{model}`\n"
        f"- **Run at (UTC):** `{datetime.now(timezone.utc).isoformat()}`\n"
        f"- **{PACKET_HASH_HEADER_KEY}:** `{packet.packet_hash}`\n"
        f"- **Packet size (bytes):** `{packet.size_bytes:,}`\n"
        f"- **Touched files:** `{len(packet.touched_files)}`\n"
        f"- **Blocking deviations:** `{result.blocking_count}`\n"
        f"- **Warnings:** `{result.warning_count}`\n\n"
        "---\n\n"
    )
    output_path.write_text(header + result.content + "\n", encoding="utf-8")
    return output_path


def create_drift_incident(
    *,
    task_id: str,
    completion_claim: str,
    finding_type: str,
    severity: str,
    reason: str,
    extra: dict | None = None,
) -> Path:
    """Write a structured drift-incident record."""

    DRIFT_INCIDENT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _utc_timestamp()
    short_hash = hashlib.sha256(
        f"{task_id}{completion_claim}{reason}{timestamp}".encode("utf-8")
    ).hexdigest()[:12]
    incident_id = f"drift-{timestamp}-{short_hash}"
    output_path = DRIFT_INCIDENT_DIR / f"{incident_id}.json"
    record: dict = {
        "incident_id": incident_id,
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "detector": "complete_gate",
        "finding_type": finding_type,
        "severity": severity,
        "task_id": task_id,
        "completion_claim": completion_claim,
        "reason": reason,
    }
    if extra:
        record.update(extra)
    output_path.write_text(
        json.dumps(record, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


# ---------------------------------------------------------------------------
# Hook scope check
# ---------------------------------------------------------------------------

def _matches_hook_scope(path: str) -> bool:
    normalised = path.replace("\\", "/")
    for prefix in HOOK_SCOPE_PREFIXES_ALWAYS:
        if normalised.startswith(prefix):
            return True
    if INCLUDE_AUDIT_TOOLS_IN_SCOPE and normalised.startswith(AUDIT_TOOLS_PREFIX):
        return True
    if normalised.startswith(PRODUCT_ROADMAP_PREFIX) and normalised.endswith(".md"):
        full = WORKSPACE_ROOT / normalised
        if full.exists() and _is_signed_spec(full):
            return True
    return False


def staged_files_in_scope() -> list[str]:
    """Return staged files (vs HEAD index) that match the hook scope."""

    name_only = _run_git(["diff", "--cached", "--name-only"])
    scoped: list[str] = []
    for line in name_only.splitlines():
        cleaned = _normalise_git_path(line)
        if cleaned and _matches_hook_scope(cleaned):
            scoped.append(cleaned)
    return scoped


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class GateRunOutcome:
    exit_code: int
    message: str
    audit_output_path: Path | None = None
    drift_incidents: list[Path] = field(default_factory=list)
    cached: bool = False


def run_gate(
    *,
    task_id: str,
    completion_claim: str,
    operator_override: str | None = None,
    staged_only: bool = False,
) -> GateRunOutcome:
    """Run the gate end-to-end. Returns an outcome; never raises GateError.

    When ``staged_only`` is True (pre-commit mode), the gate audits the
    git index (``git diff --cached``) — unstaged working-tree edits are
    excluded from the packet and from manifest verification. This keeps
    pre-commit audits scoped to the exact set the operator is about to
    commit; unrelated dirty files in the worktree do not leak in.
    """

    try:
        manifest = load_manifest(task_id)
    except ManifestVerificationError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    git_summary = collect_git_changed_files(staged_only=staged_only)

    if manifest is not None:
        try:
            verify_manifest(manifest, git_summary)
        except ManifestVerificationError as exc:
            return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    touched_files = build_touched_files_set(manifest, git_summary)
    try:
        relevant_specs = collect_relevant_signed_specs(manifest, touched_files)
    except ManifestVerificationError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    try:
        packet = assemble_audit_packet(
            task_id=task_id,
            completion_claim=completion_claim,
            manifest=manifest,
            git_summary=git_summary,
            touched_files=touched_files,
            relevant_specs=relevant_specs,
        )
    except PacketTooLargeError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    try:
        verify_packet_coverage(packet)
    except PacketCoverageError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    if operator_override is not None:
        incident = create_drift_incident(
            task_id=task_id,
            completion_claim=completion_claim,
            finding_type="operator_override",
            severity="warning",
            reason=operator_override,
            extra={
                "touched_files": list(touched_files),
                "packet_hash": packet.packet_hash,
                "packet_size_bytes": packet.size_bytes,
            },
        )
        return GateRunOutcome(
            exit_code=EXIT_OK,
            message=(
                "operator override applied; Grok call skipped. "
                "Warning-level drift incident recorded."
            ),
            drift_incidents=[incident],
        )

    cached = find_cached_audit(task_id, packet.packet_hash)
    if cached is not None:
        try:
            cached_content = cached.path.read_text(encoding="utf-8")
        except OSError as exc:
            return GateRunOutcome(
                exit_code=EXIT_GROK_OUTPUT_INVALID,
                message=f"grok_output_unreadable_cache: {exc}",
            )
        try:
            result = parse_gate_summary(cached_content)
        except GrokOutputError as exc:
            return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))
        if result.blocking_count > 0:
            return GateRunOutcome(
                exit_code=EXIT_BLOCKING_DEVIATION,
                message=(
                    f"cached audit ({cached.path.name}) reports "
                    f"{result.blocking_count} blocking deviation(s); "
                    "resolve and re-run."
                ),
                audit_output_path=cached.path,
                cached=True,
            )
        return GateRunOutcome(
            exit_code=EXIT_OK,
            message=(
                f"cached audit matches current packet hash; reused "
                f"{cached.path.name}. {result.warning_count} warning(s)."
            ),
            audit_output_path=cached.path,
            cached=True,
        )

    try:
        api_key, model = load_xai_credentials(ENV_PATH)
    except GrokCallError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    try:
        content = call_grok(api_key=api_key, model=model, payload=packet.text)
    except GrokCallError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    try:
        result = parse_gate_summary(content)
    except GrokOutputError as exc:
        return GateRunOutcome(exit_code=exc.exit_code, message=str(exc))

    output_path = save_grok_output(
        task_id=task_id,
        model=model,
        packet=packet,
        result=result,
    )

    if result.blocking_count > 0:
        return GateRunOutcome(
            exit_code=EXIT_BLOCKING_DEVIATION,
            message=(
                f"Grok reported {result.blocking_count} blocking "
                f"deviation(s) and {result.warning_count} warning(s). "
                f"See {output_path.name}."
            ),
            audit_output_path=output_path,
        )

    return GateRunOutcome(
        exit_code=EXIT_OK,
        message=(
            f"clean audit. {result.warning_count} warning(s). "
            f"See {output_path.name}."
        ),
        audit_output_path=output_path,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Grok completion gate. Fires only at readiness boundaries "
            "(commit / ship / sign-off / mark-complete)."
        ),
    )
    parser.add_argument(
        "--task",
        help="Task identifier (matches the worker manifest filename).",
    )
    parser.add_argument(
        "--claim",
        help="Completion claim text. Required unless --pre-commit.",
    )
    parser.add_argument(
        "--operator-override",
        help=(
            "Bypass the Grok call, generate a warning-level drift "
            "incident, and exit zero. Use only when Matt explicitly "
            "decides to ship without a fresh Grok audit."
        ),
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help=(
            "Pre-commit wrapper mode. Inspects staged files; runs the "
            "full gate only when staged files fall inside the hook scope. "
            "Exits zero with a 'nothing to audit' message if no staged "
            "file is in scope."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)

    if args.pre_commit:
        scoped = staged_files_in_scope()
        if not scoped:
            print("complete_gate: no staged files in hook scope; nothing to audit.")
            return EXIT_OK
        task_id = args.task or "pre_commit"
        claim = (
            args.claim
            or f"pre-commit auto-trigger ({len(scoped)} scoped file(s))"
        )
        print(
            f"complete_gate: pre-commit gate firing on {len(scoped)} "
            f"scoped file(s); task={task_id}."
        )
        outcome = run_gate(
            task_id=task_id,
            completion_claim=claim,
            operator_override=args.operator_override,
            staged_only=True,
        )
    else:
        if not args.task or not args.claim:
            print(
                "complete_gate: --task and --claim are required outside "
                "--pre-commit mode.",
                file=sys.stderr,
            )
            return EXIT_USAGE
        outcome = run_gate(
            task_id=args.task,
            completion_claim=args.claim,
            operator_override=args.operator_override,
        )

    print(outcome.message)
    if outcome.audit_output_path is not None:
        print(f"audit output: {outcome.audit_output_path}")
    for incident in outcome.drift_incidents:
        print(f"drift incident: {incident}")
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------------
# Pre-commit hook snippet (for the operator to install manually)
# ---------------------------------------------------------------------------
#
# Save the following as `.git/hooks/pre-commit` and `chmod +x` it. This
# script does not install the hook itself — installing into .git/ is an
# explicit operator action.
#
#     #!/bin/sh
#     # NorthStar — Grok completion gate (pre-commit wrapper)
#     python audit_tools/complete_gate.py --pre-commit
#     status=$?
#     if [ "$status" -ne 0 ]; then
#       echo "complete_gate refused: exit code $status" >&2
#       exit "$status"
#     fi
#
