#!/usr/bin/env python3
"""verify_build_truth.py - derive build truth from code + git, not hand-maintained docs.

The MMI source-of-truth problem: tracker docs (PROJECT_HANDSHAKE.md, the 70-agent
scoreboard header, MMI_CURRENT_STATE.md) are hand-maintained and drift silently away
from what the code and git history actually say. A behavioural promise does not fix
that; a verifier does. This script derives the real state from authoritative sources
and FAILS LOUD when a tracker disagrees.

Reality sources (never hand-maintained prose):
  - git                      -> actual HEAD commit
  - scoreboard ROW TABLE     -> actual count of GOVERNED_AGENT rows (NOT the header number)
  - decision_cycles_log.md   -> newest entry = actual latest phase/gate + test baseline
  - pytest                   -> actual test count (collected by default; executed with --full)

It compares those realities against the CLAIMS in the hand-maintained trackers.

Exit codes:
  0  BUILD TRUTH VERIFIED  - every checked tracker agrees with reality
  1  DRIFT DETECTED        - at least one tracker disagrees, or a check could not be verified

Usage:
  python scripts/verify_build_truth.py            # git + scoreboard + log + pytest --collect-only
  python scripts/verify_build_truth.py --full     # also run the full pytest suite (slow): passed counts
  python scripts/verify_build_truth.py --no-tests # skip pytest entirely
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "3. SwarmCommand_Engine" / "Agent_Loop_Runtime" / "Runtime_Implementation"
SCOREBOARD = REPO_ROOT / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
DECISION_LOG = REPO_ROOT / "decision_cycles_log.md"
HANDSHAKE = REPO_ROOT / "PROJECT_HANDSHAKE.md"
MMI_STATE = REPO_ROOT / "MMI_CURRENT_STATE.md"


class Finding:
    def __init__(self, check: str, drift: bool, detail: str) -> None:
        self.check = check
        self.drift = drift
        self.detail = detail


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=None if cwd is None else str(cwd),
            capture_output=True, text=True, timeout=timeout,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError as exc:
        return 127, f"command not found: {exc}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"


def _is_ancestor(commit: str) -> bool | None:
    """True if `commit` is an ancestor of HEAD (a commit is its own ancestor);
    False if `commit` is a known object but not on this branch; None if `commit`
    is not a known object."""
    rc, _ = run(["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", commit, "HEAD"])
    if rc == 0:
        return True
    if rc == 1:
        return False
    return None


def _commits_behind_remote() -> int | None:
    """Commits the upstream has that HEAD does not (0 = not behind). None if no
    upstream is configured. Being ahead (unpushed local commits) is not behind."""
    rc, out = run(["git", "-C", str(REPO_ROOT), "rev-list", "--count", "HEAD..@{upstream}"])
    if rc == 0 and out.strip().isdigit():
        return int(out.strip())
    return None


# --- check 1: HEAD --------------------------------------------------------------
# Rule (locked 2026-06-13): a doc hash is OK if it is an ancestor of real HEAD on
# the current branch. It FAILS only if the hash is not on the branch at all, or if
# the branch is behind its remote. Being a few commits behind on a fast-moving
# branch is normal and is not drift. This kills the self-referential refresh loop:
# committing a HEAD-refresh advances HEAD, which previously re-broke an exact match.

def check_head(findings: list[Finding]) -> None:
    rc, out = run(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    if rc != 0:
        findings.append(Finding("HEAD", True, f"could not read git HEAD: {out.strip()}"))
        return
    real = out.strip()

    claims: list[tuple[str, str]] = []
    hs = read(HANDSHAKE)
    m = re.search(r"as of\s+([0-9a-f]{6,40})", hs)
    if m:
        claims.append(("PROJECT_HANDSHAKE.md 'as of'", m.group(1)))
    m = re.search(r"(?m)^HEAD:\s*([0-9a-f]{6,40})", hs)
    if m:
        claims.append(("PROJECT_HANDSHAKE.md 'HEAD:'", m.group(1)))
    m = re.search(r"As of HEAD:\*\*\s*`?([0-9a-f]{6,40})", read(MMI_STATE))
    if m:
        claims.append(("MMI_CURRENT_STATE.md 'As of HEAD'", m.group(1)))

    problems: list[str] = []
    for src, val in claims:
        anc = _is_ancestor(val)
        if anc is True:
            continue
        if anc is False:
            problems.append(f"{src} says {val} which is NOT on this branch (not an ancestor of HEAD)")
        else:
            problems.append(f"{src} says {val} which is not a known commit")

    behind = _commits_behind_remote()
    if behind is not None and behind > 0:
        problems.append(f"branch is BEHIND its remote by {behind} commit(s)")

    if problems:
        findings.append(Finding("HEAD", True, f"real HEAD={real}; " + "; ".join(problems)))
    else:
        note = f"real HEAD={real}; {len(claims)} doc hash(es) are ancestors of HEAD"
        if behind == 0:
            note += "; branch not behind remote"
        findings.append(Finding("HEAD", False, note))


# --- check 2: governed agent count (rows, not header) ---------------------------

def check_governed_count(findings: list[Finding]) -> None:
    sb = read(SCOREBOARD)
    if not sb:
        findings.append(Finding("GOVERNED_COUNT", True, "scoreboard not found/readable"))
        return
    # reality: count table rows whose *Runtime status* cell contains GOVERNED_AGENT.
    # Do not count prose mentions in later cells, e.g. "becomes GOVERNED_AGENT"
    # or "not promoted to GOVERNED_AGENT".
    rows = []
    for line in sb.splitlines():
        if not re.match(r"^\|\s*#?\d+[A-Za-z]?\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[2].startswith("`GOVERNED_AGENT`"):
            rows.append(line)
    real = len(rows)
    # claim: the BREADTH RUNWAY header number
    m = re.search(r"BREADTH RUNWAY[^\d]*(\d+)\s*(?:\*\*)?\s*of\s*70", sb)
    if not m:
        findings.append(Finding("GOVERNED_COUNT", True,
                                f"counted {real} GOVERNED_AGENT row(s); header 'BREADTH RUNWAY ... of 70' not found"))
        return
    header = int(m.group(1))
    if header != real:
        findings.append(Finding("GOVERNED_COUNT", True,
                                f"header says {header} of 70, but {real} GOVERNED_AGENT row(s) exist in the tables"))
    else:
        findings.append(Finding("GOVERNED_COUNT", False,
                                f"header {header} == {real} counted GOVERNED_AGENT row(s)"))


# --- check 3: latest phase/gate from decision_cycles_log.md ---------------------

def newest_log_entry(text: str) -> str | None:
    marker = "\n---\n\n---\n"
    idx = text.find(marker)
    body = text[idx + len(marker):] if idx != -1 else text
    lines = body.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if "[type:" in ln and ln.strip() and not ln.lstrip().startswith("```") and not ln.startswith(" "):
            start = i
            break
    if start is None:
        return None
    block = [lines[start]]
    for ln in lines[start + 1:]:
        if "[type:" in ln and not ln.startswith(" ") and ln.strip():
            break
        block.append(ln)
    return "\n".join(block)


def check_latest_gate(findings: list[Finding]) -> int | None:
    text = read(DECISION_LOG)
    block = newest_log_entry(text) if text else None
    if not block:
        findings.append(Finding("LATEST_GATE", True, "could not parse newest decision_cycles_log.md entry"))
        return None
    header = block.splitlines()[0].strip()
    title = re.match(r"(.+?)\s{2,}\d{4}-\d{2}-\d{2}", header)
    title_txt = title.group(1).strip() if title else header
    gate = re.search(r"GATE:\s*(.+)", block)
    nxt = re.search(r"NEXT:\s*(.+)", block)
    base = re.search(r"Full runtime suite:\s*(\d+)\s+passed", block)
    baseline = int(base.group(1)) if base else None
    detail = (f"latest entry = '{title_txt}'"
              + (f"; gate {gate.group(1).strip()}" if gate else "; gate not stated")
              + (f"; baseline {baseline} passed" if baseline is not None else "; baseline not stated")
              + (f"; next = {nxt.group(1).strip()}" if nxt else ""))
    findings.append(Finding("LATEST_GATE", False, detail))
    return baseline


# --- check 4: tests -------------------------------------------------------------

def check_tests(findings: list[Finding], log_baseline: int | None, mode: str) -> None:
    hs = read(HANDSHAKE)
    m = re.search(r"(\d+)\s+tests passing", hs)
    hs_baseline = int(m.group(1)) if m else None

    # cross-doc consistency (deterministic, always runs)
    if hs_baseline is not None and log_baseline is not None and hs_baseline != log_baseline:
        findings.append(Finding("TEST_BASELINE_DOCS", True,
                                f"PROJECT_HANDSHAKE.md says {hs_baseline} tests passing; "
                                f"newest decision_cycles_log.md says {log_baseline} passed"))
    elif hs_baseline is not None and log_baseline is not None:
        findings.append(Finding("TEST_BASELINE_DOCS", False,
                                f"handshake and decision log agree at {hs_baseline} passing"))

    if mode == "none":
        findings.append(Finding("TEST_RUN", True, "pytest skipped (--no-tests); test count UNVERIFIED against code"))
        return

    if not RUNTIME_DIR.exists():
        findings.append(Finding("TEST_RUN", True, f"runtime dir not found: {RUNTIME_DIR}"))
        return

    if mode == "full":
        rc, out = run([sys.executable, "-m", "pytest", "-q"], cwd=RUNTIME_DIR)
        passed = re.search(r"(\d+)\s+passed", out)
        if passed is None:
            findings.append(Finding("TEST_RUN", True, f"pytest --full produced no parseable summary (rc={rc})"))
            return
        live = int(passed.group(1))
        if log_baseline is not None and live != log_baseline:
            findings.append(Finding("TEST_RUN", True,
                                    f"live pytest = {live} passed, but newest log baseline = {log_baseline}"))
        else:
            findings.append(Finding("TEST_RUN", False, f"live pytest = {live} passed (matches log baseline)"))
        return

    # default: collect-only -> real count of tests that exist in code
    rc, out = run([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=RUNTIME_DIR)
    m = re.search(r"(\d+)\s+tests? collected", out) or re.search(r"collected\s+(\d+)\s+items?", out)
    if m is None:
        findings.append(Finding("TEST_RUN", True,
                                f"pytest --collect-only could not be verified (rc={rc}): {out.strip().splitlines()[-1] if out.strip() else 'no output'}"))
        return
    collected = int(m.group(1))
    note = f"pytest collected {collected} tests from code"
    if log_baseline is not None:
        note += f"; newest log claims {log_baseline} passed (run with --full to verify executed counts)"
    findings.append(Finding("TEST_RUN", False, note))


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify build truth from code+git, not docs.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--full", action="store_true", help="run the full pytest suite (slow)")
    g.add_argument("--no-tests", action="store_true", help="skip pytest entirely")
    args = ap.parse_args()
    mode = "full" if args.full else "none" if args.no_tests else "collect"

    findings: list[Finding] = []
    check_head(findings)
    check_governed_count(findings)
    log_baseline = check_latest_gate(findings)
    check_tests(findings, log_baseline, mode)

    print("=" * 72)
    print("MMI BUILD-TRUTH VERIFIER  (reality from code+git vs hand-maintained docs)")
    print("=" * 72)
    for f in findings:
        flag = "DRIFT" if f.drift else "  ok "
        print(f"[{flag}] {f.check}: {f.detail}")
    print("-" * 72)

    drifted = [f for f in findings if f.drift]
    if drifted:
        print(f"DRIFT DETECTED - {len(drifted)} check(s) disagree with reality or are unverified.")
        print("Reconcile the trackers against code+git before trusting them for direction.")
        return 1
    print("BUILD TRUTH VERIFIED - all checks agree with code+git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
