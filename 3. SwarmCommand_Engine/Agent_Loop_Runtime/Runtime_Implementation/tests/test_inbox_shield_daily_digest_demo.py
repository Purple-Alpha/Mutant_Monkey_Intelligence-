from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.blackboard import DailyDigestPayload, Environment, RecordType, read_records
from core.orchestrator.routes import blackboard_path
from scripts.inbox_shield_daily_digest_demo import (
    DEMO_TENANT_ID,
    DemoDigestResult,
    demo_digest_llm_client,
    demo_emails,
    demo_scoring_llm_client,
    generate_daily_digest_demo,
    main,
)


def _records(blackboard_root: Path, tenant_id: str = DEMO_TENANT_ID):
    return read_records(blackboard_path(blackboard_root, Environment.PRODUCTION, tenant_id))


def test_demo_emails_are_the_locked_five_email_scenario() -> None:
    now = datetime(2026, 5, 23, 18, 0, tzinfo=timezone.utc)

    emails = demo_emails(now=now)

    assert [email.subject for email in emails] == [
        "Urgent invoice with new wire instructions",
        "Credential reset attachment",
        "Executive request before EOD",
        "Quick check-in",
        "May newsletter",
    ]
    assert emails[0].attachments[0]["attachment_class"] == "invoice"
    assert emails[1].attachments[0]["filename"] == "security_update.iso"


def test_demo_scoring_client_routes_expected_scores() -> None:
    invoice = json.loads(
        demo_scoring_llm_client(
            "NorthStar Inbox Shield",
            json.dumps({"subject": "Urgent invoice with new wire instructions"}),
        )
    )
    credential = json.loads(
        demo_scoring_llm_client(
            "NorthStar Inbox Shield",
            json.dumps({"subject": "Credential reset attachment"}),
        )
    )
    newsletter = json.loads(
        demo_scoring_llm_client(
            "NorthStar Inbox Shield",
            json.dumps({"subject": "May newsletter"}),
        )
    )

    assert invoice["risk_analysis"]["risk_score"] == 91
    assert invoice["recommended_action"] == "block"
    assert "new_banking_instructions" in invoice["risk_analysis"]["behavioral_deviation_flags"]
    assert credential["risk_analysis"]["risk_score"] == 86
    assert credential["recommended_action"] == "block"
    assert newsletter["risk_analysis"]["risk_score"] == 5
    assert newsletter["recommended_action"] == "safe"


def test_demo_digest_client_renders_required_sections() -> None:
    aggregate = {
        "digest_date": "2026-05-23",
        "top_risks": [
            {
                "source_analysis_record_id": "analysis-1",
                "subject": "Urgent invoice with new wire instructions",
                "sender": "billing@vendor-pay.example",
                "risk_score": 91,
                "reason": "vendor invoice fraud",
            }
        ],
        "tasks": [
            {
                "task": "Verify wire instructions",
                "owner": "finance",
                "due_date": "2026-05-24",
                "parent_risk_score": 91,
            }
        ],
        "important_emails": [
            {
                "source_analysis_record_id": "analysis-1",
                "subject": "Urgent invoice with new wire instructions",
                "sender": "billing@vendor-pay.example",
                "risk_score": 91,
            },
            {
                "source_analysis_record_id": "analysis-2",
                "subject": "May newsletter",
                "sender": "news@industry-weekly.example",
                "risk_score": 5,
            },
        ],
    }

    rendered = demo_digest_llm_client("daily digest prompt", json.dumps(aggregate))

    assert rendered.startswith("# Daily Inbox Shield Digest - 2026-05-23")
    assert "## Executive Readout" in rendered
    assert "## Highest-Risk Emails" in rendered
    assert "## Action Queue" in rendered
    assert "## Other Notable Emails" in rendered
    assert "## Operator Guidance" in rendered
    assert "Stage A demo" in rendered


def test_generate_daily_digest_demo_uses_real_runtime_path(tmp_path: Path) -> None:
    blackboard_root = tmp_path / "blackboard"
    out_path = tmp_path / "Inbox_Shield_Daily_Digest_Demo.md"

    result = generate_daily_digest_demo(
        blackboard_root=blackboard_root,
        out_path=out_path,
        reset_existing=False,
    )

    assert isinstance(result, DemoDigestResult)
    assert result.out_path == out_path
    assert result.tenant_id == DEMO_TENANT_ID
    assert result.inbound_count == 5
    assert result.analyzed_count == 5
    assert result.failed_count == 0
    assert result.important_emails_count == 5
    assert result.top_risks_count == 3
    assert result.tasks_count == 5
    assert result.digest_record_id
    assert result.workflow_trigger_id

    content = out_path.read_text(encoding="utf-8")
    assert "# Daily Inbox Shield Digest - 2026-05-23" in content
    assert "Fraud starts in the inbox" in content
    assert "Ransomware starts with a click" in content
    assert "Urgent invoice with new wire instructions" in content
    assert "Credential reset attachment" in content
    assert "Executive request before EOD" in content
    assert "## Demo Provenance" in content
    assert "no live mailbox, no live LLM, no email send, no production-state write" in content


def test_generate_daily_digest_demo_writes_expected_blackboard_records(tmp_path: Path) -> None:
    blackboard_root = tmp_path / "blackboard"
    out_path = tmp_path / "digest.md"

    generate_daily_digest_demo(
        blackboard_root=blackboard_root,
        out_path=out_path,
        reset_existing=False,
    )

    records = _records(blackboard_root)
    assert len([r for r in records if r.record_type == RecordType.EMAIL_INBOUND]) == 5
    assert len([r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]) == 5
    assert len([r for r in records if r.record_type == RecordType.DAILY_DIGEST]) == 1
    triggers = [
        r
        for r in records
        if r.record_type == RecordType.WORKFLOW_TRIGGER
        and r.workflow_id == "send_daily_digest"
    ]
    assert len(triggers) == 1

    digest = next(r for r in records if r.record_type == RecordType.DAILY_DIGEST)
    payload = DailyDigestPayload.model_validate(digest.payload)
    assert [entry.subject for entry in payload.important_emails] == [
        "Urgent invoice with new wire instructions",
        "Credential reset attachment",
        "Executive request before EOD",
        "Quick check-in",
        "May newsletter",
    ]
    assert [entry.subject for entry in payload.top_risks] == [
        "Urgent invoice with new wire instructions",
        "Credential reset attachment",
        "Executive request before EOD",
    ]
    assert payload.digest_markdown is not None
    assert "Treat `block` as an advisory label" in payload.digest_markdown


def test_generate_daily_digest_demo_refuses_to_delete_non_demo_blackboard(tmp_path: Path) -> None:
    blackboard_root = tmp_path / "existing-blackboard"
    blackboard_root.mkdir()

    with pytest.raises(RuntimeError, match="refusing to remove non-demo blackboard"):
        generate_daily_digest_demo(
            blackboard_root=blackboard_root,
            out_path=tmp_path / "digest.md",
            reset_existing=True,
        )


def test_cli_prints_summary_and_writes_artifact(tmp_path: Path) -> None:
    blackboard_root = tmp_path / "blackboard"
    out_path = tmp_path / "digest.md"
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = main(
            [
                "--blackboard-root",
                str(blackboard_root),
                "--out",
                str(out_path),
                "--no-reset",
            ]
        )

    assert rc == 0
    summary = json.loads(buffer.getvalue())
    assert summary["out_path"] == str(out_path)
    assert summary["blackboard_root"] == str(blackboard_root)
    assert summary["inbound_count"] == 5
    assert summary["analyzed_count"] == 5
    assert summary["failed_count"] == 0
    assert summary["top_risks_count"] == 3
    assert out_path.exists()
