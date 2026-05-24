"""Build the Inbox Shield daily digest demo.

This operator-side script creates an isolated demo blackboard, seeds five
fictional inbound emails, runs the real Inbox Shield ingest -> score -> digest
path with deterministic fake LLM clients, and writes a client-readable markdown
digest artifact.

Boundary:

* Operator-run only. Not autonomous, not invoked by any agent loop.
* Uses an isolated demo blackboard under ``Runtime_Implementation/demo_outputs``
  by default.
* Makes no live LLM calls, no mailbox API calls, and no send action. The
  ``send_daily_digest`` workflow trigger is written only inside the demo
  blackboard as proof that the runtime route fired.
* Does not write to ``production_state``, tenant overrides, the policy pipeline,
  or any external system.

Invoke from ``Runtime_Implementation/``::

    python -m scripts.inbox_shield_daily_digest_demo
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

from core.blackboard import DailyDigestPayload, Environment, RecordType, read_records
from core.drafting import DailyDigestConfig, run_daily_digest_cycle
from core.ingest import ingest_email, sha256_attachment_inspector
from core.orchestrator import RouteContext
from core.orchestrator.routes import blackboard_path
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ROOT = Path(__file__).resolve().parents[1]

DEMO_TENANT_ID = "acme-industries-demo"
DEMO_NOW = datetime(2026, 5, 23, 18, 0, tzinfo=timezone.utc)

DEFAULT_DEMO_DIR = RUNTIME_ROOT / "demo_outputs" / "inbox_shield_daily_digest"
DEFAULT_BLACKBOARD_ROOT = DEFAULT_DEMO_DIR / "blackboard"
DEFAULT_DIGEST_OUT = (
    REPO_ROOT
    / "1. Business_Operations"
    / "Client_Documents"
    / "Generated"
    / "Inbox_Shield_Daily_Digest_Demo.md"
)


@dataclass(frozen=True)
class DemoDigestResult:
    """Summary returned by ``generate_daily_digest_demo``."""

    out_path: Path
    blackboard_root: Path
    tenant_id: str
    digest_record_id: str
    workflow_trigger_id: str
    inbound_count: int
    analyzed_count: int
    failed_count: int
    important_emails_count: int
    top_risks_count: int
    tasks_count: int


@dataclass(frozen=True)
class DemoEmail:
    sender: str
    recipient: str
    subject: str
    body_plain: str
    received_at: datetime
    attachments: list[dict[str, Any]]


def generate_daily_digest_demo(
    *,
    blackboard_root: Path = DEFAULT_BLACKBOARD_ROOT,
    out_path: Path = DEFAULT_DIGEST_OUT,
    tenant_id: str = DEMO_TENANT_ID,
    now: datetime = DEMO_NOW,
    reset_existing: bool = True,
) -> DemoDigestResult:
    """Run the deterministic five-email digest demo and write markdown output."""

    if reset_existing and blackboard_root.exists():
        _remove_demo_blackboard(blackboard_root)

    context = RouteContext(blackboard_root=blackboard_root)

    for email in demo_emails(now=now):
        ingest_email(
            context,
            tenant_id=tenant_id,
            raw_email={
                "received_at": email.received_at,
                "sender": email.sender,
                "recipient": email.recipient,
                "subject": email.subject,
                "body_plain": email.body_plain,
                "attachments": email.attachments,
            },
            attachment_inspector=sha256_attachment_inspector,
        )

    scoring_result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=demo_scoring_llm_client,
            production_tenant_id=tenant_id,
        ),
    )
    if scoring_result.failed:
        raise RuntimeError(
            f"daily digest demo scoring failed for {scoring_result.failed} email(s)"
        )

    digest_result = run_daily_digest_cycle(
        context,
        config=DailyDigestConfig(
            llm_client=demo_digest_llm_client,
            production_tenant_id=tenant_id,
            now_provider=_fixed_now(now),
        ),
    )
    if digest_result.digest_record_id is None or digest_result.workflow_trigger_id is None:
        raise RuntimeError(f"daily digest demo did not produce a digest: {digest_result}")

    digest_payload = _load_digest_payload(
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
    )
    if not digest_payload.digest_markdown:
        raise RuntimeError("daily digest demo produced no markdown body")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        _artifact_markdown(
            markdown=digest_payload.digest_markdown,
            tenant_id=tenant_id,
            digest_record_id=str(digest_result.digest_record_id),
            workflow_trigger_id=str(digest_result.workflow_trigger_id),
            blackboard_root=blackboard_root,
        ),
        encoding="utf-8",
    )

    return DemoDigestResult(
        out_path=out_path,
        blackboard_root=blackboard_root,
        tenant_id=tenant_id,
        digest_record_id=str(digest_result.digest_record_id),
        workflow_trigger_id=str(digest_result.workflow_trigger_id),
        inbound_count=len(demo_emails(now=now)),
        analyzed_count=scoring_result.analyzed,
        failed_count=scoring_result.failed,
        important_emails_count=digest_result.important_emails_count,
        top_risks_count=digest_result.top_risks_count,
        tasks_count=digest_result.tasks_count,
    )


def demo_emails(*, now: datetime = DEMO_NOW) -> list[DemoEmail]:
    """Return the five deterministic emails used in the demo."""

    recipient = "ops@acme-industries.example"
    return [
        DemoEmail(
            sender="billing@vendor-pay.example",
            recipient=recipient,
            subject="Urgent invoice with new wire instructions",
            body_plain=(
                "Please process invoice 1048 today. We changed banks, so use the "
                "new ACH instructions in the attached PDF and disregard the old "
                "remit-to details."
            ),
            received_at=now - timedelta(hours=5),
            attachments=[
                {
                    "filename": "invoice_1048_remit_update.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 184_000,
                    "attachment_class": "invoice",
                    "extracted_text": "Invoice 1048. New ACH routing instructions.",
                    "body_bytes": b"invoice 1048 new ach routing instructions",
                }
            ],
        ),
        DemoEmail(
            sender="security@identity-reset.example",
            recipient=recipient,
            subject="Credential reset attachment",
            body_plain=(
                "Your account will be disabled today. Open the attached security "
                "package and confirm your password to keep access."
            ),
            received_at=now - timedelta(hours=4),
            attachments=[
                {
                    "filename": "security_update.iso",
                    "content_type": "application/octet-stream",
                    "size_bytes": 4_194_304,
                    "attachment_class": "payload_carrier",
                    "body_bytes": b"fake iso bytes for demo",
                }
            ],
        ),
        DemoEmail(
            sender="ceo@acme-industries.co",
            recipient=recipient,
            subject="Executive request before EOD",
            body_plain=(
                "I need you to handle this before EOD. Do not loop anyone else in "
                "yet; I will explain later."
            ),
            received_at=now - timedelta(hours=3),
            attachments=[],
        ),
        DemoEmail(
            sender="ops@trusted-partner.example",
            recipient=recipient,
            subject="Quick check-in",
            body_plain="Can you confirm tomorrow's delivery window still works?",
            received_at=now - timedelta(hours=2),
            attachments=[],
        ),
        DemoEmail(
            sender="news@industry-weekly.example",
            recipient=recipient,
            subject="May newsletter",
            body_plain="This month's supplier operations newsletter is attached.",
            received_at=now - timedelta(hours=1),
            attachments=[],
        ),
    ]


def demo_scoring_llm_client(system_prompt: str, user_prompt: str) -> str:
    """Deterministic scoring fake that routes on inbound subject."""

    if "NorthStar Inbox Shield" not in system_prompt:
        raise AssertionError("demo scoring client received unexpected prompt")

    parsed_input = json.loads(user_prompt)
    subject = (parsed_input.get("subject") or "").lower()

    if "invoice" in subject:
        return json.dumps(
            {
                "summary": (
                    "Vendor invoice request includes new ACH instructions, old "
                    "remit-to details declared invalid, and same-day pressure."
                ),
                "action_items": [
                    {
                        "task": "Verify the new ACH instructions by phone using the known vendor contact",
                        "owner": "finance",
                        "due_date": "2026-05-24",
                    },
                    {
                        "task": "Pause payment until the remittance change is confirmed",
                        "owner": "ops",
                        "due_date": None,
                    },
                ],
                "risk_analysis": {
                    "risk_score": 91,
                    "risk_factors": [
                        "vendor invoice fraud",
                        "new banking instructions",
                        "same-day payment pressure",
                    ],
                    "phishing_signals": ["sender_mismatch"],
                    "urgency_signals": ["process today"],
                    "financial_risk": "high",
                    "vendor_fraud_score": 92,
                    "wire_transfer_anomaly_score": 88,
                    "invoice_authenticity_score": 25,
                    "behavioral_deviation_flags": [
                        "new_banking_instructions",
                        "mismatched_invoice_vendor_name",
                        "urgency_paired_with_finance",
                    ],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 62,
                    "suspicious_elements": ["vendor payment rail change"],
                    "sender_legitimacy_notes": "Sender asks to replace existing remit-to instructions.",
                },
                "recommended_action": "block",
            }
        )

    if "credential" in subject:
        return json.dumps(
            {
                "summary": (
                    "Credential reset lure uses urgent account-disabling language "
                    "and asks the user to open an attachment."
                ),
                "action_items": [
                    {
                        "task": "Do not open the attachment; verify the account notice through the identity portal",
                        "owner": "ops",
                        "due_date": None,
                    }
                ],
                "risk_analysis": {
                    "risk_score": 86,
                    "risk_factors": [
                        "ransomware precursor",
                        "payload-carrier attachment",
                        "credential harvesting lure",
                    ],
                    "phishing_signals": ["credential_harvesting"],
                    "urgency_signals": ["account disabled today"],
                    "financial_risk": "medium",
                    "vendor_fraud_score": 15,
                    "wire_transfer_anomaly_score": 5,
                    "invoice_authenticity_score": None,
                    "behavioral_deviation_flags": ["out_of_band_pressure"],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 45,
                    "suspicious_elements": ["security-brand pressure"],
                    "sender_legitimacy_notes": "Sender domain is not the tenant's real identity provider.",
                },
                "recommended_action": "block",
            }
        )

    if "executive" in subject:
        return json.dumps(
            {
                "summary": "Executive-style request applies time pressure and asks the operator to avoid normal review.",
                "action_items": [
                    {
                        "task": "Confirm the executive request through a known internal channel",
                        "owner": "ops",
                        "due_date": None,
                    }
                ],
                "risk_analysis": {
                    "risk_score": 72,
                    "risk_factors": ["executive impersonation"],
                    "phishing_signals": ["lookalike_sender"],
                    "urgency_signals": ["before EOD"],
                    "financial_risk": "medium",
                    "vendor_fraud_score": 20,
                    "wire_transfer_anomaly_score": 65,
                    "invoice_authenticity_score": None,
                    "behavioral_deviation_flags": [
                        "lookalike_sender_domain",
                        "out_of_band_pressure",
                    ],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 82,
                    "suspicious_elements": ["lookalike executive sender"],
                    "sender_legitimacy_notes": "Domain resembles the tenant but is not exact.",
                },
                "recommended_action": "needs_review",
            }
        )

    if "newsletter" in subject:
        return json.dumps(
            {
                "summary": "Routine supplier operations newsletter with no operational action required.",
                "action_items": [],
                "risk_analysis": {
                    "risk_score": 5,
                    "risk_factors": [],
                    "phishing_signals": [],
                    "urgency_signals": [],
                    "financial_risk": "low",
                    "vendor_fraud_score": 0,
                    "wire_transfer_anomaly_score": 0,
                    "invoice_authenticity_score": None,
                    "behavioral_deviation_flags": [],
                },
                "impersonation_analysis": {
                    "impersonation_likelihood": 0,
                    "suspicious_elements": [],
                    "sender_legitimacy_notes": None,
                },
                "recommended_action": "safe",
            }
        )

    return json.dumps(
        {
            "summary": "Routine operational check-in with no severe fraud indicators.",
            "action_items": [
                {"task": "Acknowledge sender", "owner": None, "due_date": None}
            ],
            "risk_analysis": {
                "risk_score": 35,
                "risk_factors": ["unknown sender"],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 10,
                "wire_transfer_anomaly_score": 5,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 10,
                "suspicious_elements": [],
                "sender_legitimacy_notes": None,
            },
            "recommended_action": "safe",
        }
    )


def demo_digest_llm_client(system_prompt: str, user_prompt: str) -> str:
    """Deterministic digest fake that renders markdown from the aggregate JSON."""

    if "daily digest" not in system_prompt.lower():
        raise AssertionError("demo digest client received unexpected prompt")

    parsed = json.loads(user_prompt)
    digest_date = parsed["digest_date"]
    top_risks = parsed["top_risks"]
    tasks = parsed["tasks"]
    important = parsed["important_emails"]
    top_risk_ids = {item["source_analysis_record_id"] for item in top_risks}

    lines = [
        f"# Daily Inbox Shield Digest - {digest_date}",
        "",
        "## Executive Readout",
        "- Fraud starts in the inbox: the highest-risk item is a vendor invoice asking for new ACH instructions under same-day pressure.",
        "- Ransomware starts with a click: the credential-reset email carries a payload-style attachment and account-disabling pressure.",
        "- One executive-style request needs out-of-band confirmation before normal workflow continues.",
        "",
        "## Highest-Risk Emails",
    ]

    for item in top_risks:
        reason = item.get("reason") or "review recommended"
        lines.extend(
            [
                (
                    f"- **{item.get('subject') or '(no subject)'}** from "
                    f"`{item.get('sender') or 'unknown sender'}` - "
                    f"risk `{item['risk_score']}` - {reason}. "
                    "Immediate action: verify through a known channel before acting."
                )
            ]
        )

    if tasks:
        lines.extend(["", "## Action Queue"])
        for task in tasks:
            owner = task.get("owner") or "unassigned"
            due = task.get("due_date") or "no due date"
            lines.append(
                f"- `{owner}` - {task['task']} ({due}); parent risk `{task['parent_risk_score']}`."
            )

    other = [
        item
        for item in important
        if item["source_analysis_record_id"] not in top_risk_ids
    ]
    if other:
        lines.extend(["", "## Other Notable Emails"])
        for item in other:
            lines.append(
                (
                    f"- **{item.get('subject') or '(no subject)'}** from "
                    f"`{item.get('sender') or 'unknown sender'}` - "
                    f"risk `{item['risk_score']}`."
                )
            )

    lines.extend(
        [
            "",
            "## Operator Guidance",
            "- Treat `block` as an advisory label in this Stage A demo; no mailbox quarantine or deletion happened.",
            "- Verify payment changes and executive requests out-of-band using known contacts.",
            "- Do not open credential-reset attachments; check the identity portal directly.",
        ]
    )
    return "\n".join(lines)


def _load_digest_payload(*, blackboard_root: Path, tenant_id: str) -> DailyDigestPayload:
    records = read_records(blackboard_path(blackboard_root, Environment.PRODUCTION, tenant_id))
    digests = [record for record in records if record.record_type == RecordType.DAILY_DIGEST]
    if len(digests) != 1:
        raise RuntimeError(f"expected exactly one demo digest, found {len(digests)}")
    return DailyDigestPayload.model_validate(digests[0].payload)


def _artifact_markdown(
    *,
    markdown: str,
    tenant_id: str,
    digest_record_id: str,
    workflow_trigger_id: str,
    blackboard_root: Path,
) -> str:
    return (
        markdown.rstrip()
        + "\n\n---\n\n"
        + "## Demo Provenance\n"
        + f"- Tenant: `{tenant_id}`\n"
        + f"- Digest record: `{digest_record_id}`\n"
        + f"- Workflow trigger: `{workflow_trigger_id}` (`send_daily_digest`, demo blackboard only)\n"
        + f"- Demo blackboard root: `{blackboard_root}`\n"
        + "- Boundary: deterministic demo data only; no live mailbox, no live LLM, no email send, no production-state write.\n"
    )


def _remove_demo_blackboard(path: Path) -> None:
    resolved = path.resolve()
    allowed_parent = DEFAULT_DEMO_DIR.resolve()
    if resolved == allowed_parent or allowed_parent not in resolved.parents:
        raise RuntimeError(f"refusing to remove non-demo blackboard path: {path}")
    shutil.rmtree(resolved)


def _fixed_now(when: datetime):
    def _now() -> datetime:
        return when

    return _now


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inbox_shield_daily_digest_demo",
        description="Generate the deterministic Inbox Shield daily digest demo.",
    )
    parser.add_argument(
        "--blackboard-root",
        type=Path,
        default=DEFAULT_BLACKBOARD_ROOT,
        help="Demo blackboard root (default: Runtime_Implementation/demo_outputs/...).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_DIGEST_OUT,
        help="Markdown output path for the generated demo digest.",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default=DEMO_TENANT_ID,
        help="Fictional demo tenant id.",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not delete the existing demo blackboard before generating.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    result = generate_daily_digest_demo(
        blackboard_root=args.blackboard_root,
        out_path=args.out,
        tenant_id=args.tenant_id,
        reset_existing=not args.no_reset,
    )
    summary = result.__dict__ | {
        "out_path": str(result.out_path),
        "blackboard_root": str(result.blackboard_root),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
