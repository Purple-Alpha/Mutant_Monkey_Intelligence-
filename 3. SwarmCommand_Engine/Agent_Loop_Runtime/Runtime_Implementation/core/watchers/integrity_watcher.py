"""W3 IntegrityWatcher (#87) — Watcher Agents (Layer 6 Governance).

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — §3.3.

Monitors the evidence ledger for **schema violations**, **circular read
patterns**, and **unauthorized writes**, and catches any agent attempting to
**write outside its assigned evidence type** or **read another tenant's
entries**. Emits ``schema_violation`` and ``circular_dependency`` only.

Critically, IntegrityWatcher **observes and reports** — it does not block, and it
never writes to the ledger or alters it. Enforcement remains where it already
lives (the gateway, role separation, tenant segmentation). Reporting an integrity
event never changes ledger state. Ledger access events are supplied to the
watcher; it inspects the event metadata only, never the evidence content
(WA-D7 — no evidence-chain access).
"""

from __future__ import annotations

from collections import defaultdict

from core.watchers.base import BaseWatcher
from core.watchers.observation import ObservationRecord, ObservationType, Severity, SWARM_SCOPE


class IntegrityWatcher(BaseWatcher):
    """#87 — evidence-ledger integrity observer (observes, never blocks)."""

    ALLOWED_TYPES = frozenset(
        {
            ObservationType.SCHEMA_VIOLATION,
            ObservationType.CIRCULAR_DEPENDENCY,
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Read graph: reader_agent -> set of owner_agents whose region it read.
        # A circular read pattern is a 2-cycle (A read B's region, B read A's).
        self._read_edges: dict[str, set[str]] = defaultdict(set)

    def observe_write(
        self,
        *,
        observed_agent: str,
        assigned_evidence_type: str,
        attempted_evidence_type: str,
        entry_schema_valid: bool,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord | None:
        """Report a schema violation or an unauthorized write (an agent writing
        outside its assigned evidence type). Reports only — never blocks."""

        if not entry_schema_valid:
            return self._observe(
                observation_type=ObservationType.SCHEMA_VIOLATION,
                severity=Severity.WARNING,
                observed_agent=observed_agent,
                details=f"ledger write failed schema validation (type "
                f"{attempted_evidence_type!r})",
                tenant_id=tenant_id,
            )
        if attempted_evidence_type != assigned_evidence_type:
            return self._observe(
                observation_type=ObservationType.SCHEMA_VIOLATION,
                severity=Severity.WARNING,
                observed_agent=observed_agent,
                details=(
                    f"unauthorized write: agent assigned {assigned_evidence_type!r} "
                    f"attempted {attempted_evidence_type!r}"
                ),
                tenant_id=tenant_id,
            )
        return None

    def observe_read(
        self,
        *,
        observed_agent: str,
        owner_agent: str,
        reader_tenant_id: str,
        target_tenant_id: str,
    ) -> ObservationRecord | None:
        """Report a cross-tenant read or a circular read pattern. Reports only.

        - A **cross-tenant read** (``reader_tenant_id != target_tenant_id``) is a
          boundary/schema violation — reported CRITICAL.
        - A **circular read** is a 2-cycle in the read graph: ``observed_agent``
          read ``owner_agent``'s region and ``owner_agent`` previously read
          ``observed_agent``'s region.
        """

        if reader_tenant_id != target_tenant_id:
            return self._observe(
                observation_type=ObservationType.SCHEMA_VIOLATION,
                severity=Severity.CRITICAL,
                observed_agent=observed_agent,
                details=(
                    f"cross-tenant read: {reader_tenant_id!r} attempted to read "
                    f"{target_tenant_id!r}"
                ),
                tenant_id=reader_tenant_id,
            )

        self._read_edges[observed_agent].add(owner_agent)
        # Circular read pattern: owner_agent has already read observed_agent's region.
        if observed_agent != owner_agent and observed_agent in self._read_edges.get(owner_agent, set()):
            return self._observe(
                observation_type=ObservationType.CIRCULAR_DEPENDENCY,
                severity=Severity.WARNING,
                observed_agent=observed_agent,
                details=(
                    f"circular read pattern between {observed_agent!r} and "
                    f"{owner_agent!r}"
                ),
                tenant_id=reader_tenant_id,
            )
        return None

    def report_circular_dependency(
        self, *, agents: list[str], tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord:
        """Explicitly report a detected circular dependency among a set of agents."""

        return self._observe(
            observation_type=ObservationType.CIRCULAR_DEPENDENCY,
            severity=Severity.WARNING,
            observed_agent=agents[0] if agents else SWARM_SCOPE,
            details=f"circular dependency among {agents}",
            tenant_id=tenant_id,
        )


__all__ = ["IntegrityWatcher"]
