"""Criterion 14 operator-signature evidence for evidence packages.

This module builds the *mechanism* for Criterion 14. It never signs on Matt's
behalf and never generates signature wording. The caller must provide
operator-authored wording and a scope acknowledgment; this module validates that
the required fields are present, writes a `signed_by_operator` evidence record,
and returns its evidence id for Done Criteria evaluation.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

SIGNATURE_RECORD_FILENAME = "signed_by_operator.json"
SIGNATURE_RECORD_KIND = "signed_by_operator"


class OperatorSignatureError(ValueError):
    """Raised when operator-signature evidence is missing required fields."""


@dataclass(frozen=True)
class OperatorSignatureRecord:
    evidence_id: str
    package_id: str
    tenant_id: str
    signed_at: str
    path: Path


def record_operator_signature(
    *,
    package_dir: Path,
    package_id: str,
    package_version: str,
    tenant_id: str,
    rendered_package_path: Path,
    operator_wording: str,
    scope_acknowledgment: str,
    signed_at: datetime | None = None,
) -> OperatorSignatureRecord:
    """Persist a Matt-authored package sign-off evidence record.

    Criterion 14 requires Matt's own wording plus a scope acknowledgment. This
    function enforces presence and records the evidence; it does not produce or
    alter the operator wording.
    """

    signed_at_utc = _aware_utc(signed_at or datetime.now(timezone.utc))
    wording = _require_non_empty(operator_wording, "operator_wording")
    acknowledgment = _require_non_empty(scope_acknowledgment, "scope_acknowledgment")
    if not rendered_package_path.exists():
        raise OperatorSignatureError(
            f"rendered_package_path does not exist: {rendered_package_path}"
        )

    evidence_id = _evidence_id(
        package_id=package_id,
        tenant_id=tenant_id,
        signed_at=signed_at_utc,
        operator_wording=wording,
        scope_acknowledgment=acknowledgment,
    )
    record = {
        "record_kind": SIGNATURE_RECORD_KIND,
        "evidence_id": evidence_id,
        "package_id": package_id,
        "package_version": package_version,
        "tenant_id": tenant_id,
        "signed_at": signed_at_utc.isoformat(),
        "reviewed_artifact_path": str(rendered_package_path),
        "scope_acknowledgment": acknowledgment,
        "operator_wording": wording,
        "authorship_rule": (
            "Operator wording is supplied by Matt; AI-authored sign-off text is forbidden."
        ),
    }
    record_path = package_dir / "records" / SIGNATURE_RECORD_FILENAME
    _atomic_write_json(record_path, record)
    return OperatorSignatureRecord(
        evidence_id=evidence_id,
        package_id=package_id,
        tenant_id=tenant_id,
        signed_at=signed_at_utc.isoformat(),
        path=record_path,
    )


def load_operator_signature_evidence_id(package_dir: Path) -> str | None:
    """Return the recorded operator-signature evidence id, if present and valid."""

    path = package_dir / "records" / SIGNATURE_RECORD_FILENAME
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("record_kind") != SIGNATURE_RECORD_KIND:
        return None
    evidence_id = payload.get("evidence_id")
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        return None
    if not payload.get("operator_wording") or not payload.get("scope_acknowledgment"):
        return None
    return evidence_id


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorSignatureError(f"{field_name} is required")
    return value.strip()


def _evidence_id(
    *,
    package_id: str,
    tenant_id: str,
    signed_at: datetime,
    operator_wording: str,
    scope_acknowledgment: str,
) -> str:
    payload = "|".join(
        [package_id, tenant_id, signed_at.isoformat(), operator_wording, scope_acknowledgment]
    )
    return f"evd-operator-signature-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "wb") as handle:
        handle.write(content)
    Path(temp_name).replace(path)
