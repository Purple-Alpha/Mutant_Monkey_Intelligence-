"""Tenant-id conventions used across the runtime.

Per-tenant sandbox routing keeps signed policy updates produced by tenant A
from leaking into tenant B. This module is the canonical home for the
convention that maps a production tenant id to its default sandbox tenant
id, plus any future tenant-naming utilities.

The helper is intentionally tiny and stateless. Callers that already know
the production tenant id (loop wirings, multi-tenant fixtures, future
orchestration code) should call ``default_sandbox_tenant_for`` rather than
hard-coding a literal sandbox tenant id.
"""

from __future__ import annotations


def default_sandbox_tenant_for(production_tenant_id: str) -> str:
    """Return the default sandbox tenant id for ``production_tenant_id``.

    Convention: the sandbox tenant that hosts mutation evaluations, signed
    policy updates, and rollback proposals for production tenant ``X`` is
    named ``sandbox_X``. New tenants get a per-tenant sandbox by default;
    callers may still override with an explicit sandbox tenant id if they
    want a shared sandbox (the long-standing ``tenant_demo`` /
    ``sandbox_default`` demo pair is the canonical example of that).
    """

    if not production_tenant_id:
        raise ValueError("production_tenant_id is required")
    return f"sandbox_{production_tenant_id}"


__all__ = ["default_sandbox_tenant_for"]
