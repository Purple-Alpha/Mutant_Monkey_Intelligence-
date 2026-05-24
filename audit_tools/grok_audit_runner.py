"""One-off independent-auditor runner that calls the xAI Grok API.

Purpose
-------
Send a build's signed spec + implementation files + tests + receipt to a
second AI (Grok) so it can audit the work an upstream session produced.
The runner is intentionally minimal: it is a curiosity-grade tool, NOT a
production runtime component. It lives OUTSIDE the runtime tree
(`audit_tools/`, not `core/`) precisely because it makes outbound
network calls to a third party — which the runtime perimeter forbids.

Boundaries
----------
- Reads `XAI_API_KEY` from `.env` at the workspace root.
- The key is loaded into `os.environ` and passed to a single
  `Authorization: Bearer` header. It is never printed, logged, echoed,
  or written to disk.
- Audit outputs land under `audit_outputs/`, which is git-ignored by
  default. Commit individual reports manually if worth preserving.
- The auditor prompt is locked as a constant below. Do not edit it
  casually — prompt drift defeats the point of a reproducible auditor.

Usage
-----
    python audit_tools/grok_audit_runner.py [target]

Supported targets:

- `vendor_baseline` (default)
- `financial_state_ledger`
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = WORKSPACE_ROOT / ".env"
OUTPUT_DIR = WORKSPACE_ROOT / "audit_outputs"
XAI_ENDPOINT = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4"
REQUEST_TIMEOUT_SECONDS = 300


AUDITOR_PROMPT = """You are acting as an independent code auditor. You did
NOT write the code you are about to review. Another AI assistant wrote it
against a signed specification, and your only job is to find what that
implementer missed.

The user is forwarding four inputs to you:
  1. The signed specification document.
  2. The implementation files.
  3. The test files.
  4. The implementer's own receipt of what they claim was built.

Produce your audit in EXACTLY these four sections, in this order, with
these headings:

  A. Spec divergence
     Places where the implementation does not match the specification.
     Cite the spec section number AND the file/function it conflicts
     with. If you find no divergence, say so explicitly.

  B. Coverage gaps
     Items in the specification that should be covered by tests but are
     not, or are tested in a way that does not actually prove the claim.
     Cite the spec requirement and the missing or weak test.

  C. Security and boundary risks
     Any way a tenant, an attacker, a tampered input, a misconfigured
     environment, or a future code change could bypass the protections
     the spec promises. Include cross-platform concerns (Linux vs
     Windows file permissions, SQLite behavior, timezone handling, etc.)
     if relevant.

  D. Verdict
     One of: "approve", "approve with notes", or "reject with required
     fixes". Then one paragraph explaining the verdict in plain language.

Rules:
  - Do NOT propose new features. Only audit what is in front of you.
  - Do NOT rewrite the code. Point to the problem; do not fix it.
  - Do NOT be polite at the cost of being accurate. If something is
    wrong, say it is wrong.
  - If the spec itself is ambiguous, flag the ambiguity in section A.
  - If you do not have enough context to judge a section, say so
    explicitly rather than guessing.
"""


@dataclass(frozen=True)
class AuditFile:
    """One file included in the audit package."""

    label: str
    relative_path: str


@dataclass(frozen=True)
class AuditPackage:
    """A named audit target — spec + code + tests + receipt."""

    name: str
    files: tuple[AuditFile, ...]
    receipt_label: str
    receipt_files: tuple[AuditFile, ...]
    receipt_anchors: tuple[tuple[str, str, str], ...]


VENDOR_BASELINE_PACKAGE = AuditPackage(
    name="vendor_baseline",
    files=(
        AuditFile(
            label="1. SIGNED SPECIFICATION",
            relative_path="4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md",
        ),
        AuditFile(
            label="2. IMPLEMENTATION FILE: core/production_state/vendor_baseline/isolation.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/production_state/vendor_baseline/isolation.py"
            ),
        ),
        AuditFile(
            label="2. IMPLEMENTATION FILE: core/production_state/vendor_baseline/store.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/production_state/vendor_baseline/store.py"
            ),
        ),
        AuditFile(
            label="2. IMPLEMENTATION FILE: core/production_state/vendor_baseline/__init__.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/production_state/vendor_baseline/__init__.py"
            ),
        ),
        AuditFile(
            label="3. TEST FILE: tests/test_vendor_baseline_store.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "tests/test_vendor_baseline_store.py"
            ),
        ),
        AuditFile(
            label="3. TEST FILE: tests/test_vendor_baseline_isolation_boundary.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "tests/test_vendor_baseline_isolation_boundary.py"
            ),
        ),
    ),
    receipt_label="4. IMPLEMENTER RECEIPT",
    receipt_files=(
        AuditFile(label="PROGRESS.md (Task 23 only)", relative_path="PROGRESS.md"),
        AuditFile(
            label="PROJECT_ACTIVITY_LOG.md (Vendor Baseline entry only)",
            relative_path="PROJECT_ACTIVITY_LOG.md",
        ),
    ),
    receipt_anchors=(
        ("PROGRESS.md", "### 23. Vendor Baseline Store implementation", "### 20."),
        (
            "PROJECT_ACTIVITY_LOG.md",
            "## 2026-05-24 - Vendor Baseline Store Implementation Landed",
            "## 2026-05-24 - Stress-Test Backlog Batch 2",
        ),
    ),
)


FINANCIAL_STATE_LEDGER_PACKAGE = AuditPackage(
    name="financial_state_ledger",
    files=(
        AuditFile(
            label="1. SIGNED SPECIFICATION",
            relative_path=(
                "4. Product_Roadmap/"
                "Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md"
            ),
        ),
        AuditFile(
            label="2. IMPLEMENTATION FILE: core/scoring/financial_state_ledger.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/scoring/financial_state_ledger.py"
            ),
        ),
        AuditFile(
            label="2. IMPLEMENTATION FILE: core/scoring/email_risk_scoring_agent.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/scoring/email_risk_scoring_agent.py"
            ),
        ),
        AuditFile(
            label="2. BASELINE API FILE: core/production_state/vendor_baseline/store.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/production_state/vendor_baseline/store.py"
            ),
        ),
        AuditFile(
            label="3. TEST FILE: tests/test_financial_state_ledger.py",
            relative_path=(
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "tests/test_financial_state_ledger.py"
            ),
        ),
    ),
    receipt_label="4. IMPLEMENTER RECEIPT",
    receipt_files=(
        AuditFile(label="PROGRESS.md (Task 26 only)", relative_path="PROGRESS.md"),
        AuditFile(
            label="PROJECT_ACTIVITY_LOG.md (Financial State Ledger implementation entry only)",
            relative_path="PROJECT_ACTIVITY_LOG.md",
        ),
    ),
    receipt_anchors=(
        (
            "PROGRESS.md",
            "### 26. Financial State Ledger / Delta Tripwire implementation",
            "### 25.",
        ),
        (
            "PROJECT_ACTIVITY_LOG.md",
            "## 2026-05-24 - Financial State Ledger Implementation Landed",
            "## 2026-05-24 - Financial State Ledger §11 LOCKDOWN SIGNED",
        ),
    ),
)


AUDIT_PACKAGES: dict[str, AuditPackage] = {
    "vendor_baseline": VENDOR_BASELINE_PACKAGE,
    "financial_state_ledger": FINANCIAL_STATE_LEDGER_PACKAGE,
}


def load_xai_key(env_path: Path) -> tuple[str, str]:
    """Load only XAI_API_KEY (and optional XAI_MODEL) from .env.

    Other variables in the file are intentionally ignored — this runner
    must never echo or otherwise touch secrets it does not need.
    """

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
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "XAI_API_KEY":
            api_key = value
        elif key == "XAI_MODEL":
            model = value

    if not api_key:
        raise SystemExit(
            "XAI_API_KEY not set in .env. Add a line like\n"
            "    XAI_API_KEY=xai-...\n"
            "and re-run. Do not paste the key into chat."
        )
    return api_key, model or DEFAULT_MODEL


def extract_anchor_section(text: str, start_anchor: str, stop_anchor: str) -> str:
    """Return the slice of `text` starting at `start_anchor` and ending
    just before the next occurrence of `stop_anchor`.

    Used to pull only the Vendor Baseline Store sections out of the
    long-form tracker files, instead of dragging the entire file.
    """

    start = text.find(start_anchor)
    if start == -1:
        return f"<anchor {start_anchor!r} not found>"
    tail = text[start:]
    stop = tail.find(stop_anchor, len(start_anchor))
    if stop == -1:
        return tail.strip()
    return tail[:stop].strip()


def assemble_audit_payload(package: AuditPackage) -> str:
    """Build the full audit-input text that becomes the user message."""

    parts: list[str] = [
        "You are receiving the four audit inputs requested by the "
        "independent-auditor prompt. Audit only these inputs.\n",
    ]

    for entry in package.files:
        path = WORKSPACE_ROOT / entry.relative_path
        parts.append(f"\n=== {entry.label} ===\nPATH: {entry.relative_path}\n\n")
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("\n")

    parts.append(f"\n=== {package.receipt_label} ===\n")
    for path_name, start_anchor, stop_anchor in package.receipt_anchors:
        path = WORKSPACE_ROOT / path_name
        body = path.read_text(encoding="utf-8")
        excerpt = extract_anchor_section(body, start_anchor, stop_anchor)
        parts.append(f"\n--- {path_name} ---\n{excerpt}\n")

    return "".join(parts)


def call_grok(*, api_key: str, model: str, prompt: str, audit_payload: str) -> str:
    """POST a single chat-completion request to xAI and return the
    assistant message content. The key is read once and never echoed.
    """

    request_body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": audit_payload},
        ],
    }
    encoded = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        url=XAI_ENDPOINT,
        data=encoded,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise SystemExit(
            f"xAI request failed: HTTP {exc.code} {exc.reason}\n{detail}"
        )
    except urllib.error.URLError as exc:
        raise SystemExit(f"xAI request failed: network error: {exc.reason}")

    parsed = json.loads(response_body)
    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(
            f"unexpected xAI response shape: {exc}\nraw: {response_body[:1000]}"
        )


def write_report(*, target_name: str, model: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"{target_name}_grok_audit_{timestamp}.md"
    header = (
        f"# Grok Audit — {target_name}\n\n"
        f"- **Model:** `{model}`\n"
        f"- **Run at (UTC):** `{datetime.now(timezone.utc).isoformat()}`\n"
        f"- **Workspace:** `{WORKSPACE_ROOT}`\n\n"
        "---\n\n"
    )
    output_path.write_text(header + content + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    target_name = sys.argv[1] if len(sys.argv) > 1 else "vendor_baseline"
    package = AUDIT_PACKAGES.get(target_name)
    if package is None:
        raise SystemExit(
            f"unknown audit target {target_name!r}. "
            f"Known targets: {sorted(AUDIT_PACKAGES)}"
        )

    api_key, model = load_xai_key(ENV_PATH)
    audit_payload = assemble_audit_payload(package)

    print(f"Audit target : {target_name}")
    print(f"Model        : {model}")
    print(f"Payload size : {len(audit_payload):,} characters")
    print("Calling xAI…")

    audit_content = call_grok(
        api_key=api_key,
        model=model,
        prompt=AUDITOR_PROMPT,
        audit_payload=audit_payload,
    )

    output_path = write_report(
        target_name=target_name,
        model=model,
        content=audit_content,
    )
    print(f"Audit written: {output_path}")


if __name__ == "__main__":
    main()
