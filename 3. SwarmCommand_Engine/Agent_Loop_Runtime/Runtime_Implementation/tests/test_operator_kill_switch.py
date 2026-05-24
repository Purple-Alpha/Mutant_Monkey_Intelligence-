"""Unit tests for the operator kill switch state / audit / gate primitives.

Mirrors the style of ``tests/test_production_state.py``: tmp_path fixtures,
direct module imports, and one assertion class per scenario. The kill
switch is an entirely separate surface from ``production_state`` (Guardrail
11 is unchanged) so these tests never touch the production policy state.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest

from core.blackboard import GovernanceError
from core.operator_state import (
    KillSwitchEngaged,
    OperatorAuditEntry,
    OperatorControlState,
    append_operator_audit_entry,
    disengage_kill_switch,
    engage_kill_switch,
    is_kill_switch_engaged,
    load_operator_state,
    operator_audit_log_path,
    operator_state_path,
    read_operator_audit_log,
    save_operator_state,
)


def _root(tmp_path):
    return tmp_path / "blackboard"


def test_default_operator_state_is_none_with_no_file_on_disk(tmp_path):
    state = load_operator_state(operator_state_path(_root(tmp_path)))
    assert state == OperatorControlState()
    assert state.kill_switch_scope == "NONE"
    assert state.engaged_at is None
    assert state.engaged_by is None
    assert state.reason is None


def test_engage_with_empty_reason_raises_and_writes_nothing(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(ValueError, match="reason must not be empty"):
        engage_kill_switch(root, scope="ALL", reason="   ", operator="matt")

    assert not operator_state_path(root).exists()
    assert not operator_audit_log_path(root).exists()


def test_engage_with_empty_operator_raises(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(ValueError, match="operator must not be empty"):
        engage_kill_switch(root, scope="ALL", reason="halt all loops", operator="")

    assert not operator_state_path(root).exists()
    assert not operator_audit_log_path(root).exists()


def test_engage_with_scope_none_raises(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(ValueError, match="scope NONE"):
        engage_kill_switch(root, scope="NONE", reason="bogus", operator="matt")

    assert not operator_state_path(root).exists()
    assert not operator_audit_log_path(root).exists()


def test_engage_writes_state_file_and_one_audit_line(tmp_path):
    root = _root(tmp_path)
    before = datetime.now(timezone.utc) - timedelta(seconds=1)

    new_state = engage_kill_switch(
        root, scope="ALL", reason="runaway loop", operator="matt"
    )

    after = datetime.now(timezone.utc) + timedelta(seconds=1)

    assert new_state.kill_switch_scope == "ALL"
    assert new_state.engaged_by == "matt"
    assert new_state.reason == "runaway loop"
    assert new_state.engaged_at is not None
    assert before <= new_state.engaged_at <= after

    on_disk = load_operator_state(operator_state_path(root))
    assert on_disk == new_state

    audit_entries = read_operator_audit_log(operator_audit_log_path(root))
    assert len(audit_entries) == 1
    entry = audit_entries[0]
    assert entry.action == "engage"
    assert entry.scope == "ALL"
    assert entry.previous_scope == "NONE"
    assert entry.operator == "matt"
    assert entry.reason == "runaway loop"
    assert entry.at == new_state.engaged_at


def test_disengage_writes_state_file_and_captures_previous_scope(tmp_path):
    root = _root(tmp_path)
    engage_kill_switch(
        root, scope="PRODUCTION_ONLY", reason="suspected regression", operator="matt"
    )

    new_state = disengage_kill_switch(
        root, reason="incident resolved", operator="matt"
    )

    assert new_state == OperatorControlState()
    assert load_operator_state(operator_state_path(root)) == OperatorControlState()

    audit_entries = read_operator_audit_log(operator_audit_log_path(root))
    assert [entry.action for entry in audit_entries] == ["engage", "disengage"]
    disengage_entry = audit_entries[1]
    assert disengage_entry.scope == "NONE"
    assert disengage_entry.previous_scope == "PRODUCTION_ONLY"
    assert disengage_entry.reason == "incident resolved"
    assert disengage_entry.operator == "matt"


def test_disengage_when_already_disengaged_still_records_operator_intent(tmp_path):
    root = _root(tmp_path)

    new_state = disengage_kill_switch(
        root, reason="confirm clean state", operator="matt"
    )

    assert new_state == OperatorControlState()
    audit_entries = read_operator_audit_log(operator_audit_log_path(root))
    assert len(audit_entries) == 1
    assert audit_entries[0].action == "disengage"
    assert audit_entries[0].previous_scope == "NONE"
    assert audit_entries[0].scope == "NONE"


def test_disengage_with_empty_reason_or_operator_raises(tmp_path):
    root = _root(tmp_path)

    with pytest.raises(ValueError, match="reason must not be empty"):
        disengage_kill_switch(root, reason=" ", operator="matt")
    with pytest.raises(ValueError, match="operator must not be empty"):
        disengage_kill_switch(root, reason="resolved", operator="")

    assert not operator_state_path(root).exists()
    assert not operator_audit_log_path(root).exists()


def test_load_operator_state_rejects_unauthorized_fields(tmp_path):
    path = operator_state_path(_root(tmp_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "kill_switch_scope": "ALL",
                "engaged_at": "2026-05-20T19:00:00+00:00",
                "engaged_by": "matt",
                "reason": "test",
                "rogue_field": "evil",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(GovernanceError, match="unauthorized fields"):
        load_operator_state(path)


def test_load_operator_state_rejects_invalid_scope_literal(tmp_path):
    path = operator_state_path(_root(tmp_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"kill_switch_scope": "EVERYTHING"}), encoding="utf-8"
    )

    with pytest.raises(GovernanceError, match="kill_switch_scope must be one of"):
        load_operator_state(path)


def test_load_operator_state_rejects_non_object_root(tmp_path):
    path = operator_state_path(_root(tmp_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    with pytest.raises(GovernanceError, match="not a JSON object"):
        load_operator_state(path)


def test_is_kill_switch_engaged_for_production_scope(tmp_path):
    root = _root(tmp_path)

    assert is_kill_switch_engaged(root, scope="PRODUCTION") is None

    engage_kill_switch(root, scope="ALL", reason="halt all", operator="matt")
    state = is_kill_switch_engaged(root, scope="PRODUCTION")
    assert state is not None and state.kill_switch_scope == "ALL"

    disengage_kill_switch(root, reason="resume", operator="matt")
    engage_kill_switch(
        root, scope="PRODUCTION_ONLY", reason="halt prod only", operator="matt"
    )
    state = is_kill_switch_engaged(root, scope="PRODUCTION")
    assert state is not None and state.kill_switch_scope == "PRODUCTION_ONLY"

    disengage_kill_switch(root, reason="resume", operator="matt")
    engage_kill_switch(
        root, scope="SANDBOX_ONLY", reason="halt sandbox only", operator="matt"
    )
    assert is_kill_switch_engaged(root, scope="PRODUCTION") is None


def test_is_kill_switch_engaged_for_sandbox_scope(tmp_path):
    root = _root(tmp_path)

    assert is_kill_switch_engaged(root, scope="SANDBOX") is None

    engage_kill_switch(root, scope="ALL", reason="halt all", operator="matt")
    state = is_kill_switch_engaged(root, scope="SANDBOX")
    assert state is not None and state.kill_switch_scope == "ALL"

    disengage_kill_switch(root, reason="resume", operator="matt")
    engage_kill_switch(
        root, scope="SANDBOX_ONLY", reason="halt sandbox only", operator="matt"
    )
    state = is_kill_switch_engaged(root, scope="SANDBOX")
    assert state is not None and state.kill_switch_scope == "SANDBOX_ONLY"

    disengage_kill_switch(root, reason="resume", operator="matt")
    engage_kill_switch(
        root, scope="PRODUCTION_ONLY", reason="halt prod only", operator="matt"
    )
    assert is_kill_switch_engaged(root, scope="SANDBOX") is None


def test_audit_log_is_chronological_and_append_only_across_multiple_flips(tmp_path):
    root = _root(tmp_path)

    engage_kill_switch(root, scope="ALL", reason="first halt", operator="matt")
    disengage_kill_switch(root, reason="first resume", operator="matt")
    engage_kill_switch(
        root, scope="SANDBOX_ONLY", reason="second halt", operator="matt"
    )
    disengage_kill_switch(root, reason="second resume", operator="matt")

    entries = read_operator_audit_log(operator_audit_log_path(root))
    assert [entry.action for entry in entries] == [
        "engage",
        "disengage",
        "engage",
        "disengage",
    ]
    assert [entry.scope for entry in entries] == ["ALL", "NONE", "SANDBOX_ONLY", "NONE"]
    assert [entry.previous_scope for entry in entries] == [
        "NONE",
        "ALL",
        "NONE",
        "SANDBOX_ONLY",
    ]
    for earlier, later in zip(entries, entries[1:]):
        assert earlier.at <= later.at


def test_state_round_trip_survives_atomic_write(tmp_path):
    root = _root(tmp_path)
    engage_kill_switch(root, scope="ALL", reason="atomic test", operator="matt")

    on_disk = load_operator_state(operator_state_path(root))
    assert on_disk.kill_switch_scope == "ALL"
    assert on_disk.engaged_by == "matt"
    assert on_disk.reason == "atomic test"
    assert on_disk.engaged_at is not None
    assert on_disk.engaged_at.tzinfo is not None

    disengage_kill_switch(root, reason="cleanup", operator="matt")
    after_disengage = load_operator_state(operator_state_path(root))
    assert after_disengage == OperatorControlState()


def test_save_operator_state_uses_atomic_tmp_rename(tmp_path):
    """The save path writes to .tmp then renames - matches production_state."""
    root = _root(tmp_path)
    path = operator_state_path(root)
    save_operator_state(
        path,
        OperatorControlState(
            kill_switch_scope="PRODUCTION_ONLY",
            engaged_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
            engaged_by="matt",
            reason="testing",
        ),
    )

    assert path.exists()
    assert not path.with_suffix(path.suffix + ".tmp").exists()
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == {
        "engaged_at": "2026-05-20T00:00:00+00:00",
        "engaged_by": "matt",
        "kill_switch_scope": "PRODUCTION_ONLY",
        "reason": "testing",
    }


def test_kill_switch_engaged_exception_string_contains_scope_and_reason(tmp_path):
    root = _root(tmp_path)
    engage_kill_switch(
        root, scope="ALL", reason="explicit halt", operator="matt"
    )
    state = is_kill_switch_engaged(root, scope="PRODUCTION")
    assert state is not None

    exc = KillSwitchEngaged(state)
    assert "kill switch engaged" in str(exc)
    assert "scope=ALL" in str(exc)
    assert "reason=explicit halt" in str(exc)
    assert "engaged_by=matt" in str(exc)
    assert exc.scope == "ALL"
    assert exc.reason == "explicit halt"
    assert exc.engaged_by == "matt"
    assert exc.engaged_at == state.engaged_at
    assert exc.state is state


def test_append_operator_audit_entry_creates_parent_directory(tmp_path):
    path = operator_audit_log_path(_root(tmp_path))
    assert not path.parent.exists()

    append_operator_audit_entry(
        path,
        OperatorAuditEntry(
            action="engage",
            scope="ALL",
            previous_scope="NONE",
            operator="matt",
            reason="test",
            at=datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc),
        ),
    )
    assert path.exists()
    assert path.parent.is_dir()


def test_read_operator_audit_log_rejects_malformed_json_lines(tmp_path):
    path = operator_audit_log_path(_root(tmp_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("this is not json\n", encoding="utf-8")

    with pytest.raises(GovernanceError, match="not valid JSON"):
        read_operator_audit_log(path)
