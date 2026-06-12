"""Layer 4 — ReconciliationAgent ensemble (Phase 4).

Governing contract
------------------
``4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md`` — §11 SIGNED
2026-06-11 (Matt Nichol), commit ``d0cc849``. Pre-build amendments (``f2219e3``):
the named CIRT role (RoleSeparationController) and the Layer 4 scoring track
(Agent Health Score Rubric). Depends on Phase 1 (``fe355da``), Phase 2
(``43b5511``), Phase 3 (``6deffd9`` / closed ``ce386f7``).

The ReconciliationAgent is the swarm's only verdict producer (P4-D5). One row
(#84) covers the agent and its three internal voters R1/R2/R3 (§9). The verdict
surface itself lives in ``core/blackboard/verdict_ledger.py`` (§13).
"""

from .reconciliation_agent import ReconciliationAgent, ReconciliationError
from .voters import (
    LungState,
    R1SignalWeightVoter,
    R2PatternMatchVoter,
    R3ConflictResolutionVoter,
    VoterVote,
)

__all__ = [
    "ReconciliationAgent",
    "ReconciliationError",
    "LungState",
    "R1SignalWeightVoter",
    "R2PatternMatchVoter",
    "R3ConflictResolutionVoter",
    "VoterVote",
]
