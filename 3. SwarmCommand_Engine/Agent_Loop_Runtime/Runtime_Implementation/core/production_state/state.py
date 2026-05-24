"""Mutable production policy state for the Blue (production) loop.

The Blackboard is append-only by design and stores *evidence*. The active
defensive policy in production, however, must be a single source of truth a
detection cycle can read each tick. That single source of truth is this
module.

Only ``core.production_state.gate.apply_signed_policy`` may modify this
state. Every other writer is a governance violation per Guardrail 11.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from core.blackboard import GovernanceError


@dataclass(frozen=True)
class ProductionPolicyState:
    """Frozen snapshot of the active production defensive policy.

    Frozen so the object cannot be mutated in place; new versions are created
    only through the gate. ``parameters`` is stored as a plain dict for
    JSON-round-trip simplicity; callers should treat it as read-only.
    """

    active_version: str = "v0"
    parameters: dict[str, Any] = field(default_factory=dict)


def state_path(blackboard_root: Path, tenant_id: str) -> Path:
    """Return the on-disk path for a tenant's production policy state."""

    safe = "".join(c if c.isalnum() or c in "_.-" else "_" for c in tenant_id.strip())
    if not safe:
        raise GovernanceError("tenant_id resolves to empty state filename")
    return blackboard_root / "production_state" / f"{safe}.policy.json"


def load_state(path: Path) -> ProductionPolicyState:
    """Load the current production policy state for a tenant.

    Returns the default ``ProductionPolicyState()`` if no state file exists.
    """

    if not path.exists():
        return ProductionPolicyState()
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GovernanceError("production state file is not a JSON object")
    allowed = {"active_version", "parameters"}
    unknown = set(raw.keys()) - allowed
    if unknown:
        raise GovernanceError(
            f"production state file contains unauthorized fields: {sorted(unknown)}"
        )
    active_version = raw.get("active_version", "v0")
    parameters = raw.get("parameters", {})
    if not isinstance(active_version, str):
        raise GovernanceError("active_version must be a string")
    if not isinstance(parameters, dict):
        raise GovernanceError("parameters must be a JSON object")
    return ProductionPolicyState(active_version=active_version, parameters=parameters)


def save_state(path: Path, state: ProductionPolicyState) -> None:
    """Atomically persist the production policy state.

    The write goes to a sibling ``.tmp`` file and is then renamed so a crash
    mid-write cannot leave the production loop staring at a corrupted file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "active_version": state.active_version,
        "parameters": state.parameters,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    tmp.replace(path)


def with_changes(
    state: ProductionPolicyState,
    *,
    active_version: str | None = None,
    parameters: dict[str, Any] | None = None,
) -> ProductionPolicyState:
    """Return a new state with only ``active_version`` / ``parameters`` updated.

    This function exists so the gate can produce a new state object without
    importing ``dataclasses.replace`` everywhere. It does *not* enforce the
    governance surface — that is the gate's job.
    """

    return replace(
        state,
        **(
            {"active_version": active_version} if active_version is not None else {}
        ),
        **({"parameters": parameters} if parameters is not None else {}),
    )
