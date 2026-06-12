"""SessionBudgetStore — Phase 6 (Layer 6), Gate 1: role-tiered session budgets.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D2 + BRC-D14 + BRC-D15 + §3.3.

Budgets are **role-tiered** (BRC-D14), enforced **at the gateway**, and
**opaque to agents** (an agent cannot read or negotiate its own budget):

  - Detection agents: 50K tokens, 30 tool calls, 15 min.
  - ReconciliationAgent ensemble: 150K tokens, 90 tool calls, 20 min — with
    **per-voter sub-budgets of 50K each** (R1/R2/R3); no voter borrows from
    another without controller approval.
  - Control-plane components: 25K tokens, 20 tool calls, 10 min.

Budget exhaustion is **not a pass** (BRC-D15): it produces
``incomplete_budget_exhausted`` status. No final reconciliation, blocking
recommendation, or signed decision may be issued from exhausted output, and
every exhaustion event creates an append-only governance record.

All tiers are amendment-tunable after Ring 0 + Ring 1 baseline data (BRC-D14).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from core.control_plane.audit import ControlPlaneAuditTrail, ControlPlaneEvent

INCOMPLETE_BUDGET_EXHAUSTED = "incomplete_budget_exhausted"


class RoleTier(str, Enum):
    DETECTION = "detection"
    RECONCILIATION = "reconciliation"
    CONTROL_PLANE = "control_plane"


class BudgetError(Exception):
    """Raised on malformed budget operations (fail-safe)."""


@dataclass(frozen=True)
class Budget:
    max_tokens: int
    max_tool_calls: int
    max_wall_clock_seconds: float


# BRC-D14 launch-conservative role-tiered defaults (amendment-tunable).
TIER_BUDGETS: dict[RoleTier, Budget] = {
    RoleTier.DETECTION: Budget(50_000, 30, 15 * 60),
    RoleTier.RECONCILIATION: Budget(150_000, 90, 20 * 60),
    RoleTier.CONTROL_PLANE: Budget(25_000, 20, 10 * 60),
}

# Per-voter sub-budget for the ReconciliationAgent ensemble (BRC-D14).
RECONCILIATION_VOTER_TOKEN_SUBBUDGET = 50_000
RECONCILIATION_VOTERS = ("R1", "R2", "R3")


@dataclass
class _SessionUsage:
    tier: RoleTier
    tokens: int = 0
    tool_calls: int = 0
    wall_clock_seconds: float = 0.0
    exhausted: bool = False
    # Per-voter token usage (reconciliation tier only).
    voter_tokens: dict[str, int] = field(default_factory=dict)


@dataclass
class SessionBudgetStore:
    """Role-tiered, gateway-enforced, agent-opaque session budgets (Gate 1)."""

    audit: ControlPlaneAuditTrail = field(default_factory=ControlPlaneAuditTrail)
    _sessions: dict[str, _SessionUsage] = field(default_factory=dict)

    def open_session(self, session_id: str, *, tier: RoleTier) -> None:
        if not session_id:
            raise BudgetError("session_id is required")
        self._sessions[session_id] = _SessionUsage(tier=tier)

    def _usage(self, session_id: str) -> _SessionUsage:
        usage = self._sessions.get(session_id)
        if usage is None:
            raise BudgetError(f"unknown session {session_id!r}; open_session first")
        return usage

    def is_exhausted(self, session_id: str) -> bool:
        return self._usage(session_id).exhausted

    def _exhaust(self, session_id: str, usage: _SessionUsage, reason: str) -> None:
        usage.exhausted = True
        self.audit.record(
            ControlPlaneEvent.BUDGET_EXHAUSTED,
            f"session {session_id}: {reason}",
        )

    def charge(
        self,
        session_id: str,
        *,
        tokens: int = 0,
        tool_calls: int = 0,
        wall_clock_seconds: float = 0.0,
        voter: str | None = None,
        controller_approved_borrow: bool = False,
    ) -> bool:
        """Charge usage against a session. Returns ``True`` while the session is
        within budget; on first breach it flips the session to exhausted, writes
        a governance record, and returns ``False`` for this and every later
        charge. Agents never see the numbers — only the gateway calls this.
        """

        usage = self._usage(session_id)
        if usage.exhausted:
            return False

        budget = TIER_BUDGETS[usage.tier]

        # Per-voter sub-budget enforcement (BRC-D14), reconciliation tier only.
        if voter is not None:
            if usage.tier is not RoleTier.RECONCILIATION:
                raise BudgetError("voter sub-budgets apply to the reconciliation tier only")
            if voter not in RECONCILIATION_VOTERS:
                raise BudgetError(f"unknown voter {voter!r}")
            projected = usage.voter_tokens.get(voter, 0) + tokens
            if projected > RECONCILIATION_VOTER_TOKEN_SUBBUDGET and not controller_approved_borrow:
                # A voter cannot borrow from another's sub-budget without
                # controller approval (BRC-D14).
                self._exhaust(
                    session_id,
                    usage,
                    f"voter {voter} exceeded 50K sub-budget without controller approval",
                )
                return False
            usage.voter_tokens[voter] = projected

        usage.tokens += tokens
        usage.tool_calls += tool_calls
        usage.wall_clock_seconds += wall_clock_seconds

        if usage.tokens > budget.max_tokens:
            self._exhaust(session_id, usage, "max_tokens exceeded")
            return False
        if usage.tool_calls > budget.max_tool_calls:
            self._exhaust(session_id, usage, "max_tool_calls exceeded")
            return False
        if usage.wall_clock_seconds > budget.max_wall_clock_seconds:
            self._exhaust(session_id, usage, "max_wall_clock exceeded")
            return False
        return True

    def status(self, session_id: str) -> str:
        """Return the session's decision status. Exhausted sessions return
        ``incomplete_budget_exhausted`` (BRC-D15) — never a normal pass.
        """

        return (
            INCOMPLETE_BUDGET_EXHAUSTED
            if self._usage(session_id).exhausted
            else "ok"
        )

    def may_issue_decision(self, session_id: str) -> bool:
        """A signed decision / verdict / blocking recommendation may be issued
        only from a non-exhausted session (BRC-D15).
        """

        return not self._usage(session_id).exhausted


__all__ = [
    "INCOMPLETE_BUDGET_EXHAUSTED",
    "RoleTier",
    "BudgetError",
    "Budget",
    "TIER_BUDGETS",
    "RECONCILIATION_VOTER_TOKEN_SUBBUDGET",
    "RECONCILIATION_VOTERS",
    "SessionBudgetStore",
]
