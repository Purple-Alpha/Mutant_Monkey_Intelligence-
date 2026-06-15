#!/usr/bin/env python3
"""detect_drift.py - cross-artifact + dispatcher-input integrity detector.

Spec: 4. Product_Roadmap/Project_Drift_Detector_Concept_Doc.md

This is the THIRD truth tool, distinct from the other two:
  - verify_build_truth.py : do committed docs match code/git reality?
  - health_check.py       : passive operational status snapshot
  - detect_drift.py (here): are the artifacts that STEER MMI internally consistent?

The failures it targets are governance-routing failures, not code failures:
  a contract exists but the scoreboard does not know about it; a scoreboard row
  claims evidence that is not present; the dispatcher reads a different project
  state than the human-facing state file describes.

HARD RULES (HR-1 / HR-2 from the spec):
  - HR-1: this detector reveals drift; it is NOT an authority source. It never
    edits, commits, stashes, moves, tracks, promotes, or repairs anything.
  - HR-2: a check only becomes a hard BLOCK (exit 1, eligible to feed
    check_drift) after it is EXPLICITLY promoted in PROMOTED_CHECKS below, which
    is a recorded operator act. Until then every finding is advisory and the
    detector exits 0.

Severity tiers:
  INFO              visibility only
  WARN              worth a glance; never affects exit code
  BLOCK-candidate   would be a blocker, but not promoted -> still exit 0
  BLOCK             a promoted BLOCK-candidate -> exit 1

Usage:
  python3 scripts/detect_drift.py            # full advisory report
  python3 scripts/detect_drift.py --quiet    # only WARN and above
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROADMAP = REPO_ROOT / "4. Product_Roadmap"
SCOREBOARD = REPO_ROOT / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
MMI_STATE = REPO_ROOT / "MMI_CURRENT_STATE.md"
DISPATCHER = REPO_ROOT / "scripts" / "mmi_dispatch.py"

# Severity tiers (ordered).
INFO = "INFO"
WARN = "WARN"
BLOCK_CANDIDATE = "BLOCK-candidate"
BLOCK = "BLOCK"

# HR-2: promotion registry. A check id listed here has been explicitly promoted
# from BLOCK-candidate to BLOCK by recorded operator decision. EMPTY by default:
# nothing gates the dispatcher until an operator promotes it on purpose.
PROMOTED_CHECKS: set[str] = set()

# Files/paths the dispatcher reads by directory listing, so untracked entries
# under them are live routing inputs (D1).
ROUTING_DIRS = [ROADMAP]

# The three files that define routing authority; a dirty/untracked one escalates.
ROUTING_AUTHORITY_FILES = {
    "MMI_CURRENT_STATE.md",
    "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md",
    "scripts/mmi_dispatch.py",
}

_UNTRACKED_AUTHORITY_PATTERNS = (
    re.compile(
        r"\*\*Status:\*\*\s*(?:§\d+\s+)?SIGNED\b|\*\*Status:\*\*.*SIGNED_UNBUILT",
        re.IGNORECASE,
    ),
    re.compile(r"\*\*Status:\*\*.*\bGATED\b", re.IGNORECASE),
    re.compile(r"\bBUILD READY\b", re.IGNORECASE),
    re.compile(r"\bSIGNED_UNBUILT\b"),
    re.compile(r"\bAWAITING_AUDIT\b"),
    re.compile(r"^AUTHORIZED_TASK:", re.MULTILINE),
    re.compile(r"^LAB_VERDICT:\s*(ACCEPT|REVISE|PARK|REJECT|HOLD)", re.MULTILINE),
)

_PARKED_DRAFT_PATTERNS = (
    re.compile(r"\*\*Status:\*\*\s*CONCEPT\b", re.IGNORECASE),
    re.compile(r"\bno build authorization\b", re.IGNORECASE),
)


class Finding:
    def __init__(self, check: str, severity: str, message: str) -> None:
        self.check = check
        self.severity = severity
        self.message = message

    @property
    def effective_severity(self) -> str:
        """BLOCK-candidate becomes BLOCK only if the check is promoted (HR-2)."""
        if self.severity == BLOCK_CANDIDATE and self.check in PROMOTED_CHECKS:
            return BLOCK
        return self.severity


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _git(args: list[str], timeout: int = 30) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)


def _porcelain() -> list[tuple[str, str]]:
    """Return (xy, path) pairs from git status --porcelain. xy='??' is untracked."""
    rc, out = _git(["status", "--porcelain"])
    if rc != 0:
        return []
    entries: list[tuple[str, str]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        xy = line[:2]
        path = line[3:].strip().strip('"')
        # Handle rename "old -> new" by keeping the new path.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((xy, path))
    return entries


def _is_contract_signed(path: Path) -> bool:
    content = _read(path)
    for line in content.splitlines():
        if "**Status:**" not in line:
            continue
        if "UNSIGNED" in line or "DRAFT - unsigned" in line:
            continue
        if "SIGNED" in line:
            return True
    return False


def _untracked_authority_claims(path: Path) -> list[str]:
    content = _read(path)
    claims: list[str] = []
    for pattern in _UNTRACKED_AUTHORITY_PATTERNS:
        match = pattern.search(content)
        if match:
            claims.append(match.group(0).strip())
    return claims


def _is_parked_draft(path: Path) -> bool:
    content = _read(path)
    return any(pattern.search(content) for pattern in _PARKED_DRAFT_PATTERNS)


def _scoreboard_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not re.match(r"^\|\s*#?\d+[A-Za-z]?\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


# --- D1: untracked files that influence routing --------------------------------

def check_d1(findings: list[Finding]) -> None:
    untracked = [p for (xy, p) in _porcelain() if xy == "??"]
    routing_hits: list[str] = []
    parked_drafts: list[str] = []
    authority_claims: list[tuple[str, list[str]]] = []
    for p in untracked:
        abs = (REPO_ROOT / p)
        for rdir in ROUTING_DIRS:
            try:
                abs_resolved = abs.resolve()
            except OSError:
                abs_resolved = abs
            if str(abs_resolved).startswith(str(rdir.resolve())):
                routing_hits.append(p)
                claims = _untracked_authority_claims(abs)
                if claims:
                    authority_claims.append((p, claims))
                elif _is_parked_draft(abs):
                    parked_drafts.append(p)
                break
    if not routing_hits:
        findings.append(Finding("D1", INFO, "no untracked routing-input files"))
        return
    # Escalate any untracked file that is a §11-SIGNED contract.
    signed_untracked = [
        p for p in routing_hits
        if "Contract" in os.path.basename(p) and _is_contract_signed(REPO_ROOT / p)
    ]
    findings.append(Finding(
        "D1", WARN,
        f"{len(routing_hits)} untracked routing-input file(s) in 4. Product_Roadmap/ "
        f"(parallel-session normal): " + ", ".join(os.path.basename(p) for p in routing_hits),
    ))
    if parked_drafts:
        findings.append(Finding(
            "D1", INFO,
            f"{len(parked_drafts)} parked untracked draft(s) explicitly say concept/no build authorization: "
            + ", ".join(os.path.basename(p) for p in parked_drafts),
        ))
    for p, claims in authority_claims:
        findings.append(Finding(
            "D1", BLOCK_CANDIDATE,
            f"untracked roadmap file claims authority: '{p}' ({'; '.join(claims)}) "
            f"-- parallel drafts may exist untracked, but untracked authority is not acceptable",
        ))
    for p in signed_untracked:
        findings.append(Finding(
            "D1", BLOCK_CANDIDATE,
            f"untracked file is a SIGNED contract: '{p}' "
            f"(signed-but-untracked contract = #88/#89/#92/#99 failure class)",
        ))


# --- D2: signed contract with no scoreboard row --------------------------------

# Filenames containing these are not buildable contracts (templates / design
# deep-dives), so they are out of D2 scope even though "Contract" is in the name.
_D2_NON_CONTRACT_MARKERS = ("Template", "Deep_Dive")

# Historical contracts are often represented in the scoreboard by governed agent
# names rather than by contract filename. These aliases keep D2 focused on real
# signed-without-row drift instead of refighting already-gated history.
_D2_SCOREBOARD_ALIASES: dict[str, tuple[str, ...]] = {
    "Blast_Radius_Controller_Contract.md": ("Blast Radius Controller",),
    "Dual_LLM_Contract.md": ("Dual-LLM", "Dual LLM"),
    "Load_Fission_Contract_v2.md": ("Load Fission",),
    "Phase3_Detection_Swarm_Contract_Amendment_1.md": (
        "Phase 3 contract + Amendment 1",
        "Credential Phishing Agent",
        "Payment Change Detection Agent",
        "MFA Manipulation Agent",
        "Verification Outcome Agent",
    ),
    "Phase4_ReconciliationAgent_Contract.md": ("ReconciliationAgent",),
    "Phase5_MutationEngine_Contract.md": ("MutationEngine", "Mutation Engine"),
    "Shadow_Watcher_Swarm_Contract.md": ("Shadow Watcher Swarm",),
    "Specialisation_Fission_Contract_v2.md": ("Specialisation Fission",),
    "Watcher_Agents_Contract.md": ("TimingWatcher", "DriftWatcher", "IntegrityWatcher"),
}

# Signed contracts intentionally governed outside the Northstar scoreboard.
_D2_EXEMPTIONS: dict[str, str] = {
    "Dual_LLM_Contract.md": (
        "architectural law / orchestrator contract; tracked through decision log "
        "and runtime DualLLM tests rather than a standalone scoreboard lifecycle row"
    ),
    "Shadow_Watcher_Swarm_Contract.md": (
        "closed in Swarm Build Map / decision log as Shadow Watcher Swarm Layer 1; "
        "not a direct control-plane scoreboard row"
    ),
    "Threat_Intelligence_Daemon_Design_Contract.md": (
        "external component built under /home/socialarchitect/mutant_monkey_intel/; "
        "tracked as provisionally complete pending independent review/gate"
    ),
}


def _contract_has_scoreboard_row(filename: str, scoreboard: str) -> bool:
    if filename in scoreboard:
        return True
    aliases = _D2_SCOREBOARD_ALIASES.get(filename, ())
    return any(alias in scoreboard for alias in aliases)


def check_d2(findings: list[Finding]) -> None:
    sb = _read(SCOREBOARD)
    if not sb:
        findings.append(Finding("D2", WARN, "scoreboard not readable; D2 skipped"))
        return
    if not ROADMAP.exists():
        findings.append(Finding("D2", WARN, "roadmap dir missing; D2 skipped"))
        return
    contract_files = {
        f for f in os.listdir(ROADMAP) if "Contract" in f and f.endswith(".md")
    }
    missing: list[str] = []
    exempted: list[str] = []
    signed_total = 0
    for f in sorted(contract_files):
        if any(marker in f for marker in _D2_NON_CONTRACT_MARKERS):
            continue  # template / deep-dive, not a buildable contract
        # A v1 contract superseded by a same-stem _v2 sibling is intentionally
        # retired; the v2 carries the live row.
        if not f.endswith("_v2.md") and f[:-3] + "_v2.md" in contract_files:
            continue
        if not _is_contract_signed(ROADMAP / f):
            continue
        signed_total += 1
        if f in _D2_EXEMPTIONS:
            exempted.append(f)
            continue
        if not _contract_has_scoreboard_row(f, sb):
            missing.append(f)
    if not missing:
        findings.append(Finding(
            "D2", INFO,
            f"all {signed_total - len(exempted)} in-scope signed contract(s) "
            f"referenced in scoreboard; {len(exempted)} documented exemption(s)",
        ))
        for f in exempted:
            findings.append(Finding("D2", INFO, f"exempted signed contract '{f}': {_D2_EXEMPTIONS[f]}"))
        return
    for f in missing:
        findings.append(Finding(
            "D2", BLOCK_CANDIDATE,
            f"signed contract '{f}' has NO scoreboard row "
            f"(dispatcher will fall back to generic RESEARCH; false sense of completion)",
        ))


# --- D3: GATED scoreboard row claims evidence that does not exist ---------------

_AUDIT_RE = re.compile(r"audit_outputs/[^\s`)]+\.md")
_HASH_RE = re.compile(r"\bcommit\s+([0-9a-f]{7,40})\b")


def _hash_resolves(h: str) -> bool:
    rc, _ = _git(["rev-parse", "--verify", "--quiet", f"{h}^{{commit}}"])
    return rc == 0


def _path_present(rel: str) -> bool:
    if (REPO_ROOT / rel).exists():
        return True
    rc, _ = _git(["cat-file", "-e", f"HEAD:{rel}"])
    return rc == 0


def check_d3(findings: list[Finding]) -> None:
    sb = _read(SCOREBOARD)
    if not sb:
        findings.append(Finding("D3", WARN, "scoreboard not readable; D3 skipped"))
        return
    problems: list[str] = []
    gated_checked = 0
    for cells in _scoreboard_rows(sb):
        if len(cells) < 3:
            continue
        row_id = cells[0].lstrip("#").strip()
        status_cell = cells[2]
        if not status_cell.strip("`").startswith("GATED"):
            continue
        gated_checked += 1
        for audit in set(_AUDIT_RE.findall(status_cell)):
            if not _path_present(audit):
                problems.append(
                    f"row #{row_id} GATED cites missing audit evidence '{audit}'"
                )
        for h in set(m.group(1) for m in _HASH_RE.finditer(status_cell)):
            if not _hash_resolves(h):
                problems.append(
                    f"row #{row_id} GATED cites commit {h} which does not resolve"
                )
    if not problems:
        findings.append(Finding(
            "D3", INFO, f"{gated_checked} GATED row(s); all cited evidence present",
        ))
        return
    for p in problems:
        findings.append(Finding("D3", BLOCK_CANDIDATE, f"phantom authority: {p}"))


# --- D4: dirty working tree on tracked files -----------------------------------

def check_d4(findings: list[Finding]) -> None:
    dirty = [(xy, p) for (xy, p) in _porcelain() if xy != "??"]
    if not dirty:
        findings.append(Finding("D4", INFO, "no tracked files modified"))
        return
    authority_dirty = [p for (_, p) in dirty if p in ROUTING_AUTHORITY_FILES]
    findings.append(Finding(
        "D4", WARN,
        f"{len(dirty)} tracked file(s) with uncommitted changes",
    ))
    for p in authority_dirty:
        findings.append(Finding(
            "D4", BLOCK_CANDIDATE,
            f"routing-authority file is dirty: '{p}' "
            f"(committed truth and routing truth disagree)",
        ))


# --- D5: MMI_CURRENT_STATE.md vs dispatcher disagreement -----------------------

def _parse_mode_task(text: str) -> tuple[str | None, str | None]:
    mode = re.search(r"(?m)^MODE:\s*(.+)$", text)
    task = re.search(r"(?m)^AUTHORIZED_TASK:\s*(.+)$", text)
    return (
        mode.group(1).strip() if mode else None,
        task.group(1).strip() if task else None,
    )


def check_d5(findings: list[Finding]) -> None:
    if not DISPATCHER.exists():
        findings.append(Finding("D5", INFO, "dispatcher not found; D5 skipped"))
        return
    try:
        proc = subprocess.run(
            [sys.executable, str(DISPATCHER)],
            capture_output=True, text=True, timeout=180, cwd=str(REPO_ROOT), check=False,
        )
        disp_out = proc.stdout or ""
    except (OSError, subprocess.SubprocessError) as exc:
        findings.append(Finding("D5", INFO, f"dispatcher could not run ({exc}); D5 skipped"))
        return
    disp_mode, disp_task = _parse_mode_task(disp_out)
    state_mode, state_task = _parse_mode_task(_read(MMI_STATE))
    if disp_mode is None:
        findings.append(Finding("D5", INFO, "dispatcher emitted no MODE; D5 inconclusive"))
        return
    if state_mode is None:
        findings.append(Finding("D5", WARN, "MMI_CURRENT_STATE.md has no MODE: line"))
        return
    if state_mode != disp_mode:
        findings.append(Finding(
            "D5", WARN,
            f"state file MODE '{state_mode}' != dispatcher MODE '{disp_mode}' "
            f"(dispatcher is operational truth; state file is the human note)",
        ))
    else:
        findings.append(Finding("D5", INFO, f"state file MODE matches dispatcher ('{disp_mode}')"))


# --- D6: scoreboard internal consistency ---------------------------------------

def check_d6(findings: list[Finding]) -> None:
    sb = _read(SCOREBOARD)
    if not sb:
        findings.append(Finding("D6", WARN, "scoreboard not readable; D6 skipped"))
        return
    # Scope to the control-plane governance table (the section parallel sessions
    # append to and where row-id collisions like #100/#101 actually matter).
    # The full scoreboard has multiple tables that legitimately reuse ids, so a
    # whole-file scan would be pure noise.
    marker = "Control Plane — Signed, Unbuilt"
    idx = sb.find(marker)
    region = sb[idx:] if idx != -1 else sb
    scope_note = "control-plane table" if idx != -1 else "whole scoreboard (section marker not found)"
    seen: dict[str, int] = {}
    for cells in _scoreboard_rows(region):
        rid = cells[0].lstrip("#").strip()
        seen[rid] = seen.get(rid, 0) + 1
    dupes = {rid: n for rid, n in seen.items() if n > 1}
    if dupes:
        findings.append(Finding(
            "D6", WARN,
            f"duplicate row id(s) in {scope_note}: "
            + ", ".join(f"#{rid} x{n}" for rid, n in sorted(dupes.items())),
        ))
    else:
        findings.append(Finding("D6", INFO, f"no duplicate row ids in {scope_note}"))


CHECKS = [check_d1, check_d2, check_d3, check_d4, check_d5, check_d6]


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-artifact + dispatcher-input drift detector.")
    ap.add_argument("--quiet", action="store_true", help="only show WARN and above")
    args = ap.parse_args()

    findings: list[Finding] = []
    for check in CHECKS:
        try:
            check(findings)
        except Exception as exc:  # a detector must never crash the caller
            findings.append(Finding(check.__name__, WARN, f"check errored: {exc}"))

    order = {BLOCK: 0, BLOCK_CANDIDATE: 1, WARN: 2, INFO: 3}
    shown = [
        f for f in findings
        if not (args.quiet and f.effective_severity in (INFO,))
    ]
    shown.sort(key=lambda f: (order.get(f.effective_severity, 9), f.check))

    print("=" * 60)
    print("PROJECT DRIFT DETECTOR  (cross-artifact + dispatcher-input integrity)")
    print("=" * 60)
    for f in shown:
        print(f"[{f.effective_severity:>15}] {f.check} {f.message}")
    print("-" * 60)

    counts = {BLOCK: 0, BLOCK_CANDIDATE: 0, WARN: 0, INFO: 0}
    for f in findings:
        counts[f.effective_severity] = counts.get(f.effective_severity, 0) + 1
    print(
        f"SUMMARY: {counts[BLOCK]} BLOCK, {counts[BLOCK_CANDIDATE]} BLOCK-candidate, "
        f"{counts[WARN]} WARN, {counts[INFO]} INFO"
    )
    promoted_block = counts[BLOCK]
    if promoted_block:
        print(f"EXIT: 1  ({promoted_block} promoted BLOCK check(s))")
        return 1
    print("EXIT: 0  (advisory only — no promoted BLOCK checks; HR-2 respected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
