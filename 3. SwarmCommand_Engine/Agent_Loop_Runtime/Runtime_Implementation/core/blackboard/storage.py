"""Append-only JSONL storage adapter for Blackboard records."""

from __future__ import annotations

from pathlib import Path

from .models import BlackboardRecord


def append_record(path: Path, record: BlackboardRecord) -> None:
    """Append one Blackboard record to a JSONL file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(record.model_dump_json() + "\n")


def read_records(path: Path) -> list[BlackboardRecord]:
    """Read Blackboard records from a JSONL file."""

    if not path.exists():
        return []

    records: list[BlackboardRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(BlackboardRecord.model_validate_json(line))
    return records
