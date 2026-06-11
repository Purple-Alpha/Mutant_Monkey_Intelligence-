"""Phase 1 Infrastructure — Component 3 (Token Usage Tracker) tests.

Three test classes per AGENTS.md §5 and Phase1_Infrastructure_Agent_Design_Contract §5:
  Class 1 — expected pass
  Class 2 — adversarial / break-it
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.blackboard import (
    TOKEN_USAGE_TRACKER_CONTRACT,
    TokenActionType,
    TokenUsageError,
    TokenUsageRecord,
    TokenUsageSchemaError,
    TokenUsageTracker,
)


def _rec(**overrides) -> dict:
    base = dict(
        tenant_id="tenant_a",
        agent_id="header_analysis",
        model_id="claude-sonnet-4",
        token_count=1200,
        action_type="detection",
        session_id="sess_001",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Class 1 — Expected pass
# ---------------------------------------------------------------------------


def test_record_writes_and_reads_back(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    written = tracker.record(_rec())
    rows = tracker.read_for_tenant("tenant_a")
    assert len(rows) == 1
    assert rows[0].record_id == written.record_id
    assert rows[0].action_type is TokenActionType.DETECTION
    assert rows[0].token_count == 1200


def test_tenant_isolation_on_read_and_aggregate(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    tracker.record(_rec(tenant_id="tenant_a", token_count=100))
    tracker.record(_rec(tenant_id="tenant_b", token_count=999))
    tracker.record(_rec(tenant_id="tenant_a", token_count=50, agent_id="ghost_thread"))

    a_rows = tracker.read_for_tenant("tenant_a")
    assert {r.token_count for r in a_rows} == {100, 50}
    assert all(r.tenant_id == "tenant_a" for r in a_rows)

    summary = tracker.aggregate_for_tenant("tenant_a")
    assert summary.total_tokens == 150
    assert summary.record_count == 2
    assert summary.tokens_by_agent == {"header_analysis": 100, "ghost_thread": 50}
    assert summary.tokens_by_model == {"claude-sonnet-4": 150}
    assert summary.tokens_by_action_type == {"detection": 150}
    # tenant_b's 999 never leaks into tenant_a's aggregate
    assert 999 not in summary.tokens_by_agent.values()


def test_aggregate_breaks_out_by_model_and_action(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    tracker.record(_rec(model_id="claude-sonnet-4", action_type="detection", token_count=10))
    tracker.record(_rec(model_id="gpt-4o", action_type="audit", token_count=20))
    summary = tracker.aggregate_for_tenant("tenant_a")
    assert summary.tokens_by_model == {"claude-sonnet-4": 10, "gpt-4o": 20}
    assert summary.tokens_by_action_type == {"detection": 10, "audit": 20}


def test_contract_metadata_present():
    assert TOKEN_USAGE_TRACKER_CONTRACT["scoreboard_row"] == "#71"
    assert TOKEN_USAGE_TRACKER_CONTRACT["authorizing_commit"] == "fe355da"
    assert "P1-D6" in TOKEN_USAGE_TRACKER_CONTRACT["locked_decisions"]


# ---------------------------------------------------------------------------
# Class 2 — Adversarial / break-it
# ---------------------------------------------------------------------------


def test_no_modify_delete_or_gate_api(tmp_path):
    # P1-D5 append-only AND P1-D6 reporting-only: no mutate/delete and no
    # allow/block/gate surface may exist.
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    for forbidden in (
        "update", "delete", "modify", "remove", "overwrite",
        "gate", "block", "allow", "authorize", "decide",
    ):
        assert not hasattr(tracker, forbidden), f"invariant violated: {forbidden}"


def test_append_never_overwrites(tmp_path):
    path = tmp_path / "tokens.jsonl"
    tracker = TokenUsageTracker(path)
    tracker.record(_rec(token_count=1))
    after_first = path.read_text(encoding="utf-8")
    tracker.record(_rec(token_count=2))
    after_second = path.read_text(encoding="utf-8")
    assert after_second.startswith(after_first)
    assert after_second.count("\n") == 2


def test_missing_tenant_id_rejected_and_logged(tmp_path):
    path = tmp_path / "tokens.jsonl"
    tracker = TokenUsageTracker(path)
    with pytest.raises(TokenUsageSchemaError):
        tracker.record(_rec(tenant_id=""))
    assert not path.exists() or path.read_text(encoding="utf-8").strip() == ""
    assert "token_usage_write_rejected" in tracker.governance_audit_path.read_text(
        encoding="utf-8"
    )


def test_unknown_action_type_rejected(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    with pytest.raises(TokenUsageSchemaError):
        tracker.record(_rec(action_type="exfiltration"))


def test_negative_token_count_rejected(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    with pytest.raises(TokenUsageSchemaError):
        tracker.record(_rec(token_count=-5))


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        TokenUsageRecord(
            tenant_id="tenant_a",
            agent_id="header_analysis",
            model_id="claude-sonnet-4",
            token_count=10,
            action_type=TokenActionType.DETECTION,
            session_id="sess_001",
            smuggled="x",
        )


def test_cross_tenant_read_returns_empty_not_error(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    tracker.record(_rec(tenant_id="tenant_a"))
    assert tracker.read_for_tenant("tenant_zzz") == []
    empty_summary = tracker.aggregate_for_tenant("tenant_zzz")
    assert empty_summary.total_tokens == 0
    assert empty_summary.record_count == 0


def test_empty_tenant_id_read_raises(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    with pytest.raises(TokenUsageError):
        tracker.read_for_tenant("")


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (documented; completion path per contract §5)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Real-time streaming aggregation is deferred (contract §5 Class 3): "
        "batch reporting via aggregate_for_tenant is sufficient for Phase 1. "
        "Completion path: Playhouse dashboard contract."
    ),
    strict=True,
)
def test_real_time_streaming_aggregation(tmp_path):
    tracker = TokenUsageTracker(tmp_path / "tokens.jsonl")
    # No streaming/subscription API exists at Phase 1; only batch aggregation.
    assert hasattr(tracker, "stream_aggregate"), (
        "real-time streaming aggregation not implemented at Phase 1 (batch only)"
    )
