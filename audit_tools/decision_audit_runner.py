"""Independent decision-auditor runner for anti-drift governance.

This tool is deliberately outside product runtime. It reads one
operator-reviewed Markdown decision packet, validates the packet for the
locked contract and obvious secret/data leaks, sends it to xAI, and writes a
local report under ``audit_outputs/decision_audits/``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = WORKSPACE_ROOT / ".env"
DECISION_PACKET_DIR = WORKSPACE_ROOT / "decision_audit_inputs"
OUTPUT_DIR = WORKSPACE_ROOT / "audit_outputs" / "decision_audits"
XAI_ENDPOINT = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4"
REQUEST_TIMEOUT_SECONDS = 300

VALID_VERDICTS = frozenset(
    {
        "proceed",
        "proceed_with_notes",
        "revise_before_proceeding",
        "defer",
        "operator_decision_required",
    }
)
BLOCKING_VERDICTS = frozenset(
    {"revise_before_proceeding", "defer", "operator_decision_required"}
)
PROCEED_VERDICTS = frozenset({"proceed", "proceed_with_notes"})

REQUIRED_PACKET_SECTIONS = (
    "## 1. Decision Under Review",
    "## 2. Primary Recommendation",
    "## 3. Rationale Given",
    "## 4. Rejected Alternatives",
    "## 5. Current Project State",
    "## 6. Constraints / Guardrails",
)

FORBIDDEN_SECRET_MARKERS = (
    "XAI_API_KEY",
    "BEGIN PRIVATE KEY",
    "gho_",
    "YOUR_GITHUB_PAT_HERE",
)

RAW_FINANCIAL_PATTERNS = (
    re.compile(
        r"\b(?:routing(?:\s+number)?|account(?:\s+number)?|acct)\b"
        r"\s*[:#=-]?\s*\d{6,}\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d{9}\s*/\s*\d{6,}\b"),
)

DECISION_AUDITOR_PROMPT = """You are acting as an independent decision auditor.
You did NOT make the recommendation you are reviewing. Your job is to
challenge decision quality before the project commits to a direction.

The user is forwarding one operator-reviewed decision packet. Audit only
that packet. Do not infer hidden context, do not reward novelty, and do not
propose unrelated features.

Produce your report in EXACTLY these six sections, in this order, with
these headings:

A. Recommendation clarity
B. Fit to current project state
C. Missing alternatives or assumptions
D. Drift / bias risk
E. Cost, timing, and opportunity cost
F. Verdict

The F. Verdict section must contain exactly one machine-readable line:

VERDICT: proceed | proceed_with_notes | revise_before_proceeding | defer | operator_decision_required

Then include one plain-English paragraph explaining the verdict.

Rules:
- Do not propose unrelated features.
- Do not judge by novelty or excitement.
- Prefer the smallest action that protects the current project direction.
- Flag if the packet lacks enough context.
- Treat Matt's stated constraints as first-class inputs.
- Do not override signed specs unless the decision under review is itself a spec revision.
"""


def load_xai_key(env_path: Path) -> tuple[str, str]:
    """Load XAI_API_KEY and optional XAI_MODEL from .env without printing secrets."""

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
        raise SystemExit(
            "XAI_API_KEY not set in .env. Add XAI_API_KEY=... and re-run."
        )
    return api_key, model or DEFAULT_MODEL


def validate_decision_packet(text: str) -> None:
    """Raise SystemExit if the packet misses required sections or leaks data."""

    missing = [section for section in REQUIRED_PACKET_SECTIONS if section not in text]
    if missing:
        raise SystemExit(
            "decision packet missing required section(s): " + ", ".join(missing)
        )

    for marker in FORBIDDEN_SECRET_MARKERS:
        if marker in text:
            raise SystemExit(
                "decision packet contains forbidden secret marker; redact before audit"
            )

    for pattern in RAW_FINANCIAL_PATTERNS:
        if pattern.search(text):
            raise SystemExit(
                "decision packet appears to contain raw financial account/routing data; "
                "replace it with redacted placeholders before audit"
            )


def extract_verdict(report: str) -> str:
    """Return the machine-readable verdict; fail on missing or unknown verdicts."""

    matches = re.findall(r"^VERDICT:\s*([a-z_]+)\s*$", report, flags=re.MULTILINE)
    if len(matches) != 1:
        raise SystemExit("audit report must contain exactly one VERDICT line")

    verdict = matches[0]
    if verdict not in VALID_VERDICTS:
        raise SystemExit(f"unknown decision-audit verdict: {verdict}")
    return verdict


def call_grok(*, api_key: str, model: str, prompt: str, decision_packet: str) -> str:
    """Call xAI chat completions with the locked decision-auditor prompt."""

    request_body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": decision_packet},
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
        raise SystemExit(f"xAI request failed: HTTP {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"xAI request failed: network error: {exc.reason}")

    parsed = json.loads(response_body)
    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"unexpected xAI response shape: {exc}")


def _safe_packet_stem(packet_path: Path) -> str:
    stem = Path(packet_path).stem
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._-")
    return sanitized or "decision_packet"


def write_decision_audit_report(*, packet_path: Path, model: str, content: str) -> Path:
    """Write report under audit_outputs/decision_audits/."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / (
        f"{_safe_packet_stem(packet_path)}_decision_audit_{timestamp}.md"
    )

    output_dir_resolved = OUTPUT_DIR.resolve()
    output_path_resolved = output_path.resolve()
    if output_dir_resolved not in output_path_resolved.parents:
        raise SystemExit("refusing to write decision audit outside output directory")

    header = (
        f"# Decision Audit - {Path(packet_path).name}\n\n"
        f"- **Model:** `{model}`\n"
        f"- **Run at (UTC):** `{datetime.now(timezone.utc).isoformat()}`\n"
        f"- **Packet:** `{packet_path}`\n\n"
        "---\n\n"
    )
    output_path.write_text(header + content + "\n", encoding="utf-8")
    return output_path


def _run(packet_path: Path, *, report_only: bool = False) -> int:
    if not packet_path.exists():
        raise SystemExit(f"missing decision packet: {packet_path}")
    if not packet_path.is_file():
        raise SystemExit(f"decision packet is not a file: {packet_path}")

    packet_text = packet_path.read_text(encoding="utf-8")
    validate_decision_packet(packet_text)
    api_key, model = load_xai_key(ENV_PATH)

    print(f"Decision packet : {packet_path}")
    print(f"Model           : {model}")
    print(f"Packet size     : {len(packet_text):,} characters")
    print("Calling xAI...")

    report_content = call_grok(
        api_key=api_key,
        model=model,
        prompt=DECISION_AUDITOR_PROMPT,
        decision_packet=packet_text,
    )
    output_path = write_decision_audit_report(
        packet_path=packet_path,
        model=model,
        content=report_content,
    )
    print(f"Audit written   : {output_path}")

    verdict = extract_verdict(report_content)
    print(f"Verdict         : {verdict}")

    if verdict in BLOCKING_VERDICTS and not report_only:
        print(
            "Blocking verdict: implementation remains blocked until Matt "
            "explicitly resolves the audit."
        )
        return 2
    if verdict in BLOCKING_VERDICTS and report_only:
        print("Report-only mode: blocking verdict reported without failing the command.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an independent decision audit.")
    parser.add_argument("packet", type=Path, help="Path to a decision audit packet")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Write the report but return zero even for blocking verdicts.",
    )
    args = parser.parse_args(argv)
    return _run(args.packet, report_only=args.report_only)


if __name__ == "__main__":
    sys.exit(main())
