"""Pre-ship audit: one all-seeing review before commit and push.

What this does
--------------
1. Collects everything that would be committed if you ran `git add -A` right now
   (tracked diff + untracked files).
2. Pulls in the current direction from PROJECT_HANDSHAKE.md and PROGRESS.md.
3. Pulls in all signed specs (any spec marked `§11 SIGNED` in the header).
4. Sends the whole packet to xAI/Grok with a senior-reviewer prompt.
5. Prints SHIP / FIX_FIRST / STOP and writes the full report locally.
6. Exits zero on SHIP, non-zero on FIX_FIRST or STOP so it can be wired into
   git hooks later. Pass `--report-only` to suppress the blocking exit.

Boundaries
----------
- Reads `XAI_API_KEY` (and optional `XAI_MODEL`) from `.env` at the workspace
  root. Never prints, logs, persists, or echoes the key.
- Writes reports under `audit_outputs/pre_ship_audits/`, covered by the
  existing `audit_outputs/` gitignore rule.
- Does not touch git, Blackboard, production state, or operator state.

Usage
-----
    python audit_tools/pre_ship_audit.py
    python audit_tools/pre_ship_audit.py --report-only
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = WORKSPACE_ROOT / ".env"
OUTPUT_DIR = WORKSPACE_ROOT / "audit_outputs" / "pre_ship_audits"
XAI_ENDPOINT = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4"
REQUEST_TIMEOUT_SECONDS = 300

MAX_FILE_BYTES = 100_000
MAX_DIFF_BYTES = 400_000

VALID_VERDICTS = ("SHIP", "FIX_FIRST", "STOP")

FORBIDDEN_PENDING_PATH_PATTERNS = (
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "audit_outputs/decision_audits/*",
)

_PRIVATE_KEY_PATTERN = "BEGIN " + r"(?:RSA |EC |OPENSSH )?" + "PRIVATE KEY"
_GITHUB_PAT_PLACEHOLDER = "YOUR_" + "GITHUB_PAT_HERE"
_GITHUB_OAUTH_PREFIX = "gh" + "o_"
_XAI_TOKEN_PREFIX = "xa" + "i-"

FORBIDDEN_CONTENT_PATTERNS = (
    re.compile(_PRIVATE_KEY_PATTERN),
    re.compile(re.escape(_GITHUB_PAT_PLACEHOLDER)),
    re.compile(r"\b" + re.escape(_GITHUB_OAUTH_PREFIX) + r"[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\b" + re.escape(_XAI_TOKEN_PREFIX) + r"[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"\bXAI_API_KEY\s*=\s*(?!(?:test-secret|redacted|example)\b|\.\.\.|\{)"
        r"[^\s'\"#]+"
    ),
)


PROMPT = """You are a senior cybersecurity engineer, software architect, and
drift watchdog for the NorthStar Inbox Shield project. Another AI assistant has
prepared a set of uncommitted changes that the operator (Matt) is about to
commit and push. Your job is to read the change, the signed specs, and the
current project direction, and tell the operator whether to ship it, fix it
first, or stop.

Be blunt. Do not be polite at the cost of accuracy. Your loyalty is to the
operator and the signed specs, not to the implementer.

Produce your report in EXACTLY these six sections, in this order, with these
headings:

  A. Plan alignment
     Does this change match the current project direction documented in
     PROJECT_HANDSHAKE.md and PROGRESS.md? If it adds work that was not
     requested or skips work that was, say so plainly.

  B. Signed spec compliance
     For each signed spec the change touches, does the change match the spec?
     If the change adds a new spec or alters a signed spec, is the change
     coherent and complete? Cite spec section numbers when possible.

  C. Security and boundary risks
     Secrets, raw client data, external API calls, tenant isolation,
     production-state writes, operator-state writes, Git/GitHub mutations,
     file permissions, cross-platform issues, fail-open paths, missing
     validation. Cite the exact file and line/pattern where a risk lives.

  D. Test coverage
     For any new behavior, does at least one test actually prove it? If a
     guard, fail-closed gate, or invariant is claimed in the change, identify
     the test that pins it. If a claim is unproven, say so.

  E. Drift and scope creep
     Anything in this change that does NOT belong - features added on the
     side, abandoned ceremony, accidental refactors, dead code, tracker
     bloat, or scope expansion beyond the stated work.

  F. Verdict
     One machine-readable line, exactly one of:

         VERDICT: SHIP
         VERDICT: FIX_FIRST
         VERDICT: STOP

     Followed by one plain-English paragraph explaining the verdict.

Rules:
- SHIP only if you would personally stake your reputation that the change is
  safe, on-plan, spec-compliant, tested, and free of drift.
- FIX_FIRST when the change is on-plan but has concrete issues the
  implementer must fix before commit. List the fixes in section A/B/C/D as
  appropriate.
- STOP when the change is off-plan, violates a signed spec, introduces a
  serious security boundary risk, or adds scope that the operator has not
  signed off on.
- If the change is trivial (typo fix, comment-only, tracker-only, no code),
  you may SHIP it but say explicitly that it is trivial.
- If you cannot tell, say so in section A and choose FIX_FIRST rather than
  SHIP.
"""


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
        raise SystemExit(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def _collect_change_summary() -> dict:
    diff = _run_git(["diff", "HEAD"])
    if len(diff) > MAX_DIFF_BYTES:
        diff = diff[:MAX_DIFF_BYTES] + "\n... [diff truncated] ...\n"

    status = _run_git(["status", "--short"])

    untracked_list = [
        line.strip()
        for line in _run_git(["ls-files", "--others", "--exclude-standard"]).splitlines()
        if line.strip()
    ]

    untracked_blobs: list[tuple[str, str]] = []
    for rel in untracked_list:
        path = WORKSPACE_ROOT / rel
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            untracked_blobs.append((rel, "<binary or unreadable file>"))
            continue
        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            content = content[:MAX_FILE_BYTES] + "\n... [file truncated] ...\n"
        untracked_blobs.append((rel, content))

    changed_files: set[str] = set()
    for line in status.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        rel = line[3:] if len(line) > 3 else line
        rel = rel.strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip().strip('"')
        if rel:
            changed_files.add(rel)

    return {
        "diff": diff,
        "status": status,
        "untracked": untracked_blobs,
        "changed_files": sorted(changed_files),
    }


def _normalize_git_path(path: str) -> str:
    return path.strip().strip('"').replace("\\", "/")


def _matches_forbidden_path(path: str) -> str | None:
    normalized = _normalize_git_path(path)
    lowered = normalized.lower()
    for pattern in FORBIDDEN_PENDING_PATH_PATTERNS:
        if fnmatch.fnmatch(lowered, pattern.lower()):
            return pattern
    return None


def _find_forbidden_content(text: str) -> str | None:
    for pattern in FORBIDDEN_CONTENT_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)[:80]
    return None


def preflight_data_leak_check(change_summary: dict) -> None:
    """Fail before any network call when pending changes look unsafe to send."""

    for path in change_summary["changed_files"]:
        matched_pattern = _matches_forbidden_path(path)
        if matched_pattern:
            raise SystemExit(
                "pre-ship audit refused to send pending risky file "
                f"{path!r} (matched {matched_pattern!r})"
            )

    diff_marker = _find_forbidden_content(change_summary["diff"])
    if diff_marker:
        raise SystemExit(
            "pre-ship audit refused to send diff containing a secret-like marker"
        )

    for path, content in change_summary["untracked"]:
        content_marker = _find_forbidden_content(content)
        if content_marker:
            raise SystemExit(
                "pre-ship audit refused to send untracked file containing a "
                f"secret-like marker: {path}"
            )


def _collect_project_state() -> str:
    parts: list[str] = []
    for tracker in ("PROJECT_HANDSHAKE.md", "PROGRESS.md"):
        path = WORKSPACE_ROOT / tracker
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        excerpt = _extract_current_section(text)
        parts.append(f"=== {tracker} (current-direction excerpt) ===\n{excerpt}\n")
    return "\n".join(parts)


def _extract_current_section(text: str) -> str:
    for marker in ("## Current Next Step", "Current target:", "## Current Target"):
        idx = text.find(marker)
        if idx != -1:
            return text[idx : idx + 6000]
    return text[:4000]


def _signed_specs() -> list[Path]:
    spec_dir = WORKSPACE_ROOT / "4. Product_Roadmap"
    if not spec_dir.exists():
        return []
    signed: list[Path] = []
    for spec_path in sorted(spec_dir.glob("*Deep_Dive*.md")):
        try:
            head = spec_path.read_text(encoding="utf-8")[:1500]
        except OSError:
            continue
        if "§11 SIGNED" in head or "SIGNED " in head and "LOCKED BY" in head:
            signed.append(spec_path)
    return signed


def load_xai_key(env_path: Path) -> tuple[str, str]:
    if not env_path.exists():
        raise SystemExit(
            f"missing .env at {env_path}. Add XAI_API_KEY=... and re-run."
        )
    api_key: str | None = None
    model: str | None = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        normalized_key = key.strip()
        normalized_value = value.strip().strip('"').strip("'")
        if normalized_key == "XAI_API_KEY":
            api_key = normalized_value
        elif normalized_key == "XAI_MODEL":
            model = normalized_value
    if not api_key:
        raise SystemExit("XAI_API_KEY not set in .env.")
    return api_key, model or DEFAULT_MODEL


def call_grok(*, api_key: str, model: str, prompt: str, payload: str) -> str:
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": prompt},
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
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            response_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"xAI request failed: HTTP {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"xAI request failed: network error: {exc.reason}")

    parsed = json.loads(response_body)
    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"unexpected xAI response shape: {exc}")


def extract_verdict(report: str) -> str:
    matches = re.findall(r"^VERDICT:\s*([A-Z_]+)\s*$", report, flags=re.MULTILINE)
    if len(matches) != 1:
        raise SystemExit("audit report must contain exactly one VERDICT line")
    verdict = matches[0]
    if verdict not in VALID_VERDICTS:
        raise SystemExit(f"unknown pre-ship audit verdict: {verdict}")
    return verdict


def _write_report(*, model: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"pre_ship_audit_{timestamp}.md"
    header = (
        "# Pre-Ship Audit\n\n"
        f"- **Model:** `{model}`\n"
        f"- **Run at (UTC):** `{datetime.now(timezone.utc).isoformat()}`\n\n"
        "---\n\n"
    )
    output_path.write_text(header + content + "\n", encoding="utf-8")
    return output_path


def _assemble_payload(
    change_summary: dict,
    project_state: str,
    spec_paths: list[Path],
) -> str:
    parts: list[str] = []

    parts.append("=== CHANGE STATUS (git status --short) ===\n")
    parts.append(change_summary["status"] or "(clean)")
    parts.append("\n\n")

    parts.append("=== CHANGE DIFF (git diff HEAD) ===\n")
    parts.append(change_summary["diff"] or "(no tracked-file diff)")
    parts.append("\n\n")

    if change_summary["untracked"]:
        parts.append("=== UNTRACKED FILES (full content) ===\n")
        for rel, content in change_summary["untracked"]:
            parts.append(f"\n--- {rel} ---\n{content}\n")
        parts.append("\n")

    parts.append("=== CURRENT PROJECT DIRECTION ===\n")
    parts.append(project_state or "(unavailable)")
    parts.append("\n\n")

    if spec_paths:
        parts.append("=== SIGNED SPECS (§11) ===\n")
        for spec_path in spec_paths:
            rel = spec_path.relative_to(WORKSPACE_ROOT)
            text = spec_path.read_text(encoding="utf-8")
            if len(text.encode("utf-8")) > MAX_FILE_BYTES:
                text = text[:MAX_FILE_BYTES] + "\n... [spec truncated] ...\n"
            parts.append(f"\n--- {rel} ---\n{text}\n")

    return "".join(parts)


def _verdict_summary(report: str) -> str:
    match = re.search(
        r"^VERDICT:\s*[A-Z_]+\s*$\s*\n([^\n]+)",
        report,
        flags=re.MULTILINE,
    )
    if not match:
        return ""
    return match.group(1).strip()


def _emit_score_sheet_candidate(
    *,
    verdict: str,
    summary: str,
    report_path: Path,
    dry_run: bool,
) -> None:
    if verdict == "SHIP":
        return

    from audit_tools.score_sheet_candidate_emit import emit

    pass_fail = "fail" if verdict == "FIX_FIRST" else "blocked"
    failure_type = "expectation_contract" if verdict == "FIX_FIRST" else "workflow_issue"
    finding_summary = summary or f"Pre-ship audit returned {verdict}."

    candidate = {
        "event_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "track": "audit_gate",
        "event_type": "fail" if verdict == "FIX_FIRST" else "blocked",
        "source_artifact": str(report_path),
        "test_or_check_name": "pre_ship_audit",
        "pass_fail": pass_fail,
        "failure_type": failure_type,
        "finding_summary": finding_summary,
        "corrective_action": "Review the pre-ship audit report and address findings before committing.",
        "retest_reference": "",
        "notes": "Candidate emitted by pre_ship_audit. Not evidence until operator promotion.",
    }

    written = emit(
        [candidate],
        emitter="pre_ship_audit.py",
        short_context=verdict.lower(),
        source_run={
            "command": "python audit_tools/pre_ship_audit.py",
            "output_reference": str(report_path),
            "git_commit": None,
        },
        dry_run=dry_run,
    )
    if dry_run:
        print("Score-sheet candidate dry-run complete; no candidate file written.")
    elif written:
        print(f"Score-sheet candidate written: {written}")


def _run(report_only: bool = False, emit_score_sheet_candidate: bool = False, write_score_sheet_candidate: bool = False) -> int:
    change_summary = _collect_change_summary()
    has_changes = (
        change_summary["diff"].strip()
        or change_summary["status"].strip()
        or change_summary["untracked"]
    )
    if not has_changes:
        print("No pending changes. Nothing to audit.")
        return 0

    preflight_data_leak_check(change_summary)

    project_state = _collect_project_state()
    spec_paths = _signed_specs()
    payload = _assemble_payload(change_summary, project_state, spec_paths)

    api_key, model = load_xai_key(ENV_PATH)

    print(f"Files changed   : {len(change_summary['changed_files'])}")
    print(f"Signed specs    : {len(spec_paths)}")
    print(f"Payload size    : {len(payload):,} characters")
    print(f"Model           : {model}")
    print("Calling xAI...")

    content = call_grok(api_key=api_key, model=model, prompt=PROMPT, payload=payload)
    report_path = _write_report(model=model, content=content)
    print(f"Audit written   : {report_path}")

    verdict = extract_verdict(content)
    summary = _verdict_summary(content)

    print()
    print(f"VERDICT: {verdict}")
    if summary:
        print(summary)
    print()

    if emit_score_sheet_candidate or write_score_sheet_candidate:
        _emit_score_sheet_candidate(
            verdict=verdict,
            summary=summary,
            report_path=report_path,
            dry_run=not write_score_sheet_candidate,
        )
        print()

    if verdict == "SHIP":
        print("Pre-ship audit returned SHIP. Safe to commit and push.")
        return 0
    if verdict == "FIX_FIRST":
        if report_only:
            print("FIX_FIRST detected; --report-only suppresses the blocking exit.")
            return 0
        print("FIX_FIRST: address the issues above before committing.")
        return 2
    if verdict == "STOP":
        if report_only:
            print("STOP detected; --report-only suppresses the blocking exit.")
            return 0
        print("STOP: do not commit. Direction or scope problem flagged.")
        return 3
    raise SystemExit(f"unexpected verdict path: {verdict}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run an all-seeing pre-ship audit on uncommitted changes."
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Write the report but exit zero even on FIX_FIRST or STOP.",
    )
    parser.add_argument(
        "--emit-score-sheet-candidate",
        action="store_true",
        help="Emit a score-sheet candidate packet in dry-run mode for blocking audit outcomes.",
    )
    parser.add_argument(
        "--write-score-sheet-candidate",
        action="store_true",
        help="Write the score-sheet candidate packet instead of dry-running it.",
    )
    args = parser.parse_args(argv)
    return _run(
        report_only=args.report_only,
        emit_score_sheet_candidate=args.emit_score_sheet_candidate,
        write_score_sheet_candidate=args.write_score_sheet_candidate,
    )


if __name__ == "__main__":
    sys.exit(main())
