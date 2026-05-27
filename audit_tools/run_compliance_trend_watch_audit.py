"""One-shot Grok audit runner for the Compliance and Trend Watch Process spec.

Purpose
-------
Fire the §11-signature audit defined in
``audit_outputs/compliance_trend_watch_signoff_audit_packet_README.md``
without having to extend ``grok_audit_runner.py`` (whose targets are
all code-audit shapes — spec + impl + tests + receipt) or stash the
whole worktree to satisfy ``complete_gate.py``'s manifest verification.

This is a process-spec audit. There is no implementation, no test
suite, and no receipt. The packet is four documents:

  F1. The spec under audit:
      ``4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md``
  F2. The operational artifact the spec governs:
      ``Frontier_Intake_Log.md``
  F3. The seven non-negotiables block from ``VISION.md``.
  F4. ``§9 Redaction / Secret Handling`` from
      ``4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md``
      (the spec under audit claims canonical inheritance over §9's
      forbidden-language and vocabulary-translation lists).

Authority and bootstrap
-----------------------
This runner is operator-authorized infrastructure for a single audit
event. ``audit_tools/`` is in ``complete_gate.py``'s hook scope from
v1.1 onward, so the *next* run of ``complete_gate.py`` will see this
file as a tracked change and audit it. That is the intended pattern —
this runner exists to enable the audit; it is not itself an
unaudited backdoor. The bootstrap exception is the same shape as the
2026-05-26 ``complete_gate.py`` v1.0 bootstrap:

  - operator-authorized
  - single-purpose
  - never marks anything complete by itself
  - never persists or echoes the API key
  - emits its output under ``audit_outputs/``, which is git-ignored

Boundaries
----------
- Reads ``XAI_API_KEY`` (and optional ``XAI_MODEL``) from ``.env`` at
  the workspace root using the same loader shape as
  ``grok_audit_runner.py``. Never prints, logs, or persists the key.
- Reads the four source files from disk every run. There is no caching.
- Writes only to
  ``audit_outputs/compliance_trend_watch_signoff_<timestamp>.md``.
- Does not touch any runtime surface (Blackboard, production state,
  operator state, scoring, drafting).
- Does not modify the spec under audit, ``Frontier_Intake_Log.md``,
  ``VISION.md``, or the cyber-insurance package.

Usage
-----
Dry run (assembles the packet, reports size, does not call xAI)::

    python audit_tools/run_compliance_trend_watch_audit.py --dry-run

Full run (calls xAI, saves output)::

    python audit_tools/run_compliance_trend_watch_audit.py

Exit codes
----------
- 0 on a clean audit write (or clean dry run).
- Non-zero ``SystemExit`` with a clear message on missing files,
  missing key, network/HTTP errors, or unexpected response shape.
  These are *fail-closed* errors — the operator should not treat a
  missing audit output as compliant under the
  ``PROJECT_BUILD_AND_AUDIT_QUEUE.md`` default operating rule.
"""

from __future__ import annotations

import argparse
import json
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

TASK_ID = "compliance_trend_watch_signoff_sharp"


AUDITOR_PROMPT = """You are an independent auditor. You did not write the document you are about to review. The operator (Matt Nichol) is preparing to sign §11 on the Compliance and Trend Watch Process spec, and your only job is to find what is wrong with it before he signs.

The packet contains four documents:

1. The spec under audit: 4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md (DRAFT pre-§11).
2. The operational artifact this spec governs: Frontier_Intake_Log.md.
3. The seven non-negotiables block from VISION.md.
4. The Cyber Insurance Evidence Package deep-dive §9 (forbidden-language list and vocabulary-translation list), because the spec under audit claims canonical inheritance over those lists (§5.5).

Identify deviations and gaps in the spec under audit against the following corners:

A. Internal coherence. The spec contradicting itself across sections. Pay specific attention to:
   - The seven \"resolved 2026-05-26 by operator (pending §11 lock as Dn)\" entries in §10 (Q1, Q3, Q4, Q7, Q8, Q10, Q11). Each summary must match the inline encoding in §2.6 / §2.7 / §3 Calendar rhythm / §5.5 / §7 P1 / §9 / §9.1. Mismatches between the §10 summary and the inline body are deviations.
   - The §9 done-criteria checklist against §3 cadence, §4 trend-signal criteria, §6 / §7 trigger taxonomy, §8 Grok audit posture. Any criterion that cannot actually be checked from the cited sections is a gap.
   - The §9 machine-checkable JSON sidecar against the §9.1 rolling-quarter rule. Schema fields must support what §9.1 requires.

B. Seven non-negotiables (VISION.md). Any clause in the spec that, if interpreted reasonably, could weaken or contradict any of the seven non-negotiables — kill switch, full audit, reversibility, tenant isolation, signed promotion, adversarial-suspicious human review, operator approval for client-facing actions. Pay attention to §8 audit packet contents and §9 done declaration: they must not authorize anything that would touch a runtime non-negotiable.

C. Inherited boundaries (Cyber Insurance Evidence Package §9). The spec under audit claims canonical authority over the forbidden-language list (§5.1) and vocabulary-translation list (§5.5) at the project level, with the cyber-insurance §9 named as the buyer-surface application. Verify: (i) the §5.1 forbidden-language list in the spec under audit is consistent with §9 of the cyber-insurance package; (ii) the §5.5 vocabulary-translation list (v1, canonical) matches the cyber-insurance §9 list; (iii) the §5.5 inheritance order does not orphan the cyber-insurance package §9 — i.e. §5.5 names the buyer-surface application clearly enough that the cyber-insurance §9 still has an assigned role.

D. Frontier_Intake_Log.md governance. The spec's §1.1 supersession statement claims authority over the Log's prior rubric-sniff language. Verify: (i) the supersession does not contradict the locked cadence rule in the Log (0–1 / 2–3 / 4+ tiers); (ii) the spec's §3 Review Cadence (and §3 Calendar rhythm subsection) does not double-count or re-derive that locked cadence rule in a way that diverges from the Log's authoritative wording; (iii) the §2 watched-sources lists are consistent with the source list actually used in Frontier_Intake_Log.md Review #1.

E. Authority drift. Anywhere in the spec where a rubric, score, or AI tool is given decision authority instead of operator authority. Specifically: §1.1, §6 spec-update workflow, §7 pivot workflow, §9 done criteria, §10/§11 sign-off mechanics. Any clause that lets a non-operator entity (rubric, gate, Grok itself, Cursor, automation) make a decision is a blocking deviation. The doctrine is \"operator decides; gate enforces evidence; Grok identifies deviations.\" Anything that conflates these roles is a deviation.

F. Compliance-claim boundary leakage. Any §5.1 phrase used inside the spec under audit *outside* an allowed-context carve-out (§5.3). The spec is itself subject to its own boundary.

G. Done-criteria gameability. Anywhere in §9 / §9.1 / the JSON sidecar shape where an operator could (intentionally or by negligence) tick a criterion as met without producing the evidence the criterion claims. Specifically: criterion 9 (\"audit packet covers entry\"), criterion 10 (\"Grok audit run\"), criterion 11 (\"blocking deviations resolved or accepted\"), criterion 13 (\"operator signature in his own words\"). For each, name the specific gameability path or confirm it is structurally closed.

Do not score. Do not approve. Do not assess strategic merit, product-market fit, commercial viability, or whether the spec is \"a good idea.\" Do not propose new features. Do not rewrite the spec; point to the problem and let the operator decide what to do with it.

Categorise every deviation and gap as one of:

- Blocking — the spec cannot ship as v1 with this issue present. The operator should not sign §11 until this is resolved or explicitly accepted with a written rationale.
- Warning — the spec can ship at §11 but the issue is recorded for v1.x or §10 follow-up.

Use exactly these section headings in your output, in this order:

1. Internal coherence findings (A above)
2. Non-negotiable contradiction findings (B above)
3. Inherited-boundary findings (C above)
4. Frontier_Intake_Log governance findings (D above)
5. Authority-drift findings (E above)
6. Compliance-claim boundary leakage findings (F above)
7. Done-criteria gameability findings (G above)
8. Summary — total Blocking count, total Warning count, and one paragraph naming the single most important Blocking finding (or \"no Blocking findings\" if there are none).

If you have zero findings in any section, say so explicitly under that heading. If you do not have enough context to judge a section, say so explicitly under that heading rather than guessing. The operator will treat \"I don't know\" as cleaner signal than a confident misread.

Evidence requirement for this rerun:

- For each of the seven findings sections, you must name at least two exact spec sections, source-document headings, or clauses you examined.
- If you report \"zero findings\" in a section, explain in 2-4 sentences why the examined sections passed that check.
- Do not answer with only \"Zero findings.\" A bare zero-finding statement is non-compliant with this prompt because it is not audit evidence.
- If the packet is too large or you cannot inspect enough of it to support a section, say \"insufficient context\" under that section and name what context is missing.
- In the Summary, include a short \"Evidence quality\" paragraph that states whether your own review was comprehensive, partial, or limited, and why.
"""


@dataclass(frozen=True)
class PacketFile:
    """One file included in the audit packet."""

    label: str
    relative_path: str


PACKET_FILES: tuple[PacketFile, ...] = (
    PacketFile(
        label="F1. SPEC UNDER AUDIT",
        relative_path="4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md",
    ),
    PacketFile(
        label="F2. OPERATIONAL ARTIFACT",
        relative_path="Frontier_Intake_Log.md",
    ),
    PacketFile(
        label="F3. SEVEN NON-NEGOTIABLES (VISION.md, full file)",
        relative_path="VISION.md",
    ),
    PacketFile(
        label=(
            "F4. CYBER INSURANCE EVIDENCE PACKAGE — full file "
            "(audit reference: §9 Redaction / Secret Handling)"
        ),
        relative_path=(
            "4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md"
        ),
    ),
)


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


def assemble_audit_payload() -> str:
    """Build the user-message payload by reading the four source files."""

    parts: list[str] = [
        "You are receiving the four audit inputs requested by the "
        "independent-auditor prompt. Audit only these inputs.\n",
    ]

    for entry in PACKET_FILES:
        path = WORKSPACE_ROOT / entry.relative_path
        if not path.exists():
            raise SystemExit(
                f"missing packet file: {entry.relative_path} "
                f"(expected at {path})"
            )
        parts.append(f"\n===== {entry.label} =====\n")
        parts.append(f"PATH: {entry.relative_path}\n\n")
        parts.append(path.read_text(encoding="utf-8"))
        parts.append(f"\n===== END {entry.label} =====\n")

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


def write_report(*, model: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"{TASK_ID}_{timestamp}.md"
    header = (
        f"# Grok Audit — {TASK_ID}\n\n"
        f"- **Model:** `{model}`\n"
        f"- **Run at (UTC):** `{datetime.now(timezone.utc).isoformat()}`\n"
        f"- **Workspace:** `{WORKSPACE_ROOT}`\n"
        f"- **Packet contract:** "
        f"`audit_outputs/compliance_trend_watch_signoff_audit_packet_README.md`\n"
        f"- **Manifest:** "
        f"`audit_outputs/compliance_trend_watch_signoff.manifest.json`\n\n"
        "---\n\n"
    )
    output_path.write_text(header + content + "\n", encoding="utf-8")
    return output_path


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot Grok audit runner for the Compliance and Trend "
            "Watch Process spec §11-signature audit."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Assemble the packet and report its size, but do not call "
            "xAI. Useful for verifying setup before spending the API call."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)

    audit_payload = assemble_audit_payload()
    print(f"Task ID      : {TASK_ID}")
    print(f"Packet files : {len(PACKET_FILES)}")
    print(f"Payload size : {len(audit_payload):,} characters")

    if args.dry_run:
        print("Dry run: skipping xAI call. No output written.")
        return 0

    api_key, model = load_xai_key(ENV_PATH)
    print(f"Model        : {model}")
    print("Calling xAI…")

    audit_content = call_grok(
        api_key=api_key,
        model=model,
        prompt=AUDITOR_PROMPT,
        audit_payload=audit_payload,
    )

    output_path = write_report(model=model, content=audit_content)
    print(f"Audit written: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
