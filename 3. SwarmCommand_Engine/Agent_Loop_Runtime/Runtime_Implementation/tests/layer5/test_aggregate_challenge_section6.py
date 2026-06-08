"""Layer 5 Aggregate Challenge Pass - Section 6 test discipline.

Implements the §6 documented-failure test discipline of the §11-SIGNED
``4. Product_Roadmap/Layer_5_Aggregate_Challenge_Pass_Deep_Dive.md`` (D7):

  Class 1 - Expected pass (the proven path).
  Class 2 - Adversarial / break-it (probe the boundary; each documented).
  Class 3 - Known gap (``xfail`` with a documented reason + completion path).

The durable failure register that accompanies this test commit lives at
``audit_outputs/failure_register/layer5_section6_failure_register.json`` and
carries the Class 2 ``partial`` finding (ADV-001) and the two Class 3 known
gaps (KG-001, KG-002).

Doubles are redefined locally (not imported from ``test_swarm_commander``) and
match the REAL contract types: ``ChallengeResult`` is a ``StrictModel`` with
``agent_id`` / ``challenge_outcome`` (``confirmed`` | ``contradicted`` |
``inconclusive``) / ``challenge_basis`` (1..160 chars) - there is no ``verdict``
or ``evidence`` field. This spec/section promotes NO Challenge agent; the first
real one is Section 5 under its own signed Agent Design Contract.
"""

from __future__ import annotations

import pytest

from core.blackboard.models import (
    AgentRegistryEntry,
    AgentRole,
    Environment,
    GovernanceError,
    RecordType,
)
from core.orchestrator.agent_contract import (
    AgentContribution,
    ChallengeResult,
    MissionContext,
)
from core.orchestrator.email_authentication_agent import EmailAuthenticationAgent
from core.orchestrator.ghost_thread_agent import GhostThreadAgent
from core.orchestrator.header_divergence_agent import HeaderDivergenceAgent
from core.orchestrator.swarm_commander import SwarmCommander, _determine_disposition


# ---------------------------------------------------------------------------
# Registry-entry builders (match the real AgentRegistryEntry shape)
# ---------------------------------------------------------------------------

def _detection_entry(
    agent_id: str = "blue_detection_001",
    *,
    layer: int = 2,
    authority_level: int = 1,
    stage_allowed: str = "stage_a",
) -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Section 6 Detection Stub",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.DETECTION_RESULT},
        layer=layer,
        authority_level=authority_level,
        stage_allowed=stage_allowed,
    )


def _challenge_entry(
    agent_id: str = "challenge_001",
    *,
    layer: int = 5,
    authority_level: int = 3,
    stage_allowed: str = "stage_a",
) -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=agent_id,
        display_name="Section 6 Challenge Stub",
        role=AgentRole.BLUE,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types=set(),
        layer=layer,
        authority_level=authority_level,
        stage_allowed=stage_allowed,
    )


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)


# ---------------------------------------------------------------------------
# Detection double (Pass 1). challenge() must never be invoked on it.
# ---------------------------------------------------------------------------

class _DetectionStub:
    def __init__(
        self,
        agent_id: str = "blue_detection_001",
        *,
        layer: int = 2,
        authority_level: int = 1,
        stage_allowed: str = "stage_a",
        autonomous_action_allowed: bool = False,
        observed_facts: tuple[str, ...] = ("sender_domain_mismatch",),
        verification_outcome: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.layer = layer
        self.authority_level = authority_level
        self.stage_allowed = stage_allowed
        self.autonomous_action_allowed = autonomous_action_allowed
        self._observed_facts = observed_facts
        self._verification_outcome = verification_outcome

    def analyze(self, context: MissionContext) -> AgentContribution:
        return AgentContribution(
            agent_id=self.agent_id,
            layer=self.layer,
            observed_facts=self._observed_facts,
            verification_outcome=self._verification_outcome,
        )

    def challenge(self, contributions: tuple[AgentContribution, ...]):  # pragma: no cover
        raise AssertionError("challenge() must not be invoked on a Detection agent")


# ---------------------------------------------------------------------------
# Challenge doubles (Layer 5, Pass 2) - all on the aggregate signature.
# ---------------------------------------------------------------------------

class _PassthroughChallengeAgent:
    """Returns a fixed, valid verdict. agent_id is correct."""

    def __init__(
        self,
        agent_id: str = "challenge_001",
        *,
        challenge_outcome: str = "confirmed",
        challenge_basis: str = "passthrough stub basis",
    ) -> None:
        self.agent_id = agent_id
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False
        self._outcome = challenge_outcome
        self._basis = challenge_basis

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome=self._outcome,
            challenge_basis=self._basis,
        )


class _CountingChallengeAgent:
    """Records how many times challenge() is called and the set size it saw."""

    def __init__(self, agent_id: str = "challenge_001") -> None:
        self.agent_id = agent_id
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False
        self.call_count = 0
        self.seen_lengths: list[int] = []

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:
        self.call_count += 1
        self.seen_lengths.append(len(contributions))
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="confirmed",
            challenge_basis="counting probe verdict",
        )


class _NoneChallengeAgent:
    """Returns None - has no verdict for this case."""

    def __init__(self, agent_id: str = "challenge_001") -> None:
        self.agent_id = agent_id
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult | None:
        return None


class _VoteCountingChallengeAgent:
    """Bad actor (D4): verdict derived purely from len(contributions)."""

    def __init__(self) -> None:
        self.agent_id = "vote_counter_probe"
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:
        # Anti-pattern: signal count alone as the verdict.
        outcome = "confirmed" if len(contributions) >= 2 else "inconclusive"
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome=outcome,
            challenge_basis=f"count={len(contributions)}",
        )


class _AuthorityDriftChallengeAgent:
    """Bad actor (D5): claims autonomous_action_allowed=True."""

    def __init__(self) -> None:
        self.agent_id = "authority_drift_probe"
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = True  # the violation

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:  # pragma: no cover
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="confirmed",
            challenge_basis="should never run - rejected before invocation",
        )


class _ReasoningTraceLeakAgent:
    """Bad actor (D3): tries to read internals off the contributions."""

    def __init__(self) -> None:
        self.agent_id = "trace_leak_probe"
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:
        for contribution in contributions:
            assert not hasattr(contribution, "reasoning_trace"), (
                "AgentContribution must not expose reasoning_trace (D3 violation)"
            )
            assert not hasattr(contribution, "chain_of_thought"), (
                "AgentContribution must not expose chain_of_thought (D3 violation)"
            )
        return ChallengeResult(
            agent_id=self.agent_id,
            challenge_outcome="confirmed",
            challenge_basis="no detector internals exposed to challenge input",
        )


class _WrongIdChallengeAgent:
    """Bad actor: returns a ChallengeResult with a mismatched agent_id."""

    def __init__(self) -> None:
        self.agent_id = "correct_id"
        self.layer = 5
        self.authority_level = 3
        self.stage_allowed = "stage_a"
        self.autonomous_action_allowed = False

    def analyze(self, context: MissionContext) -> AgentContribution:  # pragma: no cover
        raise AssertionError("analyze() must not be invoked for challenge agents")

    def challenge(self, contributions: tuple[AgentContribution, ...]) -> ChallengeResult:
        return ChallengeResult(
            agent_id="WRONG_ID",
            challenge_outcome="confirmed",
            challenge_basis="mismatched id probe",
        )


# ===========================================================================
# Class 1 - Expected pass (the proven path). All green.
# ===========================================================================

def test_aggregate_challenge_invoked_once_per_case_over_full_set():
    # D1: one invocation per case over the FULL contribution set.
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            "blue_detection_002": _detection_entry(agent_id="blue_detection_002"),
            "challenge_001": _challenge_entry(),
        }
    )
    recorder = _CountingChallengeAgent()
    commander.run_case(
        _context(),
        [
            _DetectionStub(observed_facts=("from_reply_to_divergence",)),
            _DetectionStub(agent_id="blue_detection_002", observed_facts=("dmarc_fail",)),
        ],
        challenge_agents=[recorder],
    )
    assert recorder.call_count == 1
    assert recorder.seen_lengths == [2]


def test_challenge_verdict_flows_into_challenge_pass_tuple():
    # D2: one verdict per challenge agent flows into challenge_pass.
    commander = SwarmCommander(
        {"blue_detection_001": _detection_entry(), "challenge_001": _challenge_entry()}
    )
    der = commander.run_case(
        _context(),
        [_DetectionStub(observed_facts=("from_reply_to_divergence",))],
        challenge_agents=[
            _PassthroughChallengeAgent(challenge_basis="divergence corroborated")
        ],
    )
    assert der.challenge_pass == (
        ChallengeResult(
            agent_id="challenge_001",
            challenge_outcome="confirmed",
            challenge_basis="divergence corroborated",
        ),
    )


def test_disposition_precedence_holds_when_challenge_present():
    # D2/D5: contradicted -> human_required; inconclusive -> hold. Commander
    # owns disposition; the verdict does not bypass _determine_disposition.
    registry = {
        "blue_detection_001": _detection_entry(),
        "challenge_001": _challenge_entry(),
    }
    contradicted = SwarmCommander(registry).run_case(
        _context(),
        [_DetectionStub(observed_facts=("from_reply_to_divergence",))],
        challenge_agents=[
            _PassthroughChallengeAgent(
                challenge_outcome="contradicted",
                challenge_basis="second pass could not reproduce the fact",
            )
        ],
    )
    assert contradicted.disposition == "human_required"
    assert contradicted.human_state == "requested"

    inconclusive = SwarmCommander(registry).run_case(
        _context(),
        [_DetectionStub(observed_facts=("from_reply_to_divergence",))],
        challenge_agents=[
            _PassthroughChallengeAgent(
                challenge_outcome="inconclusive",
                challenge_basis="insufficient corroboration to confirm",
            )
        ],
    )
    assert inconclusive.disposition == "hold"


def test_disposition_precedence_holds_when_challenge_absent():
    # With no challenge agents: facts -> suspicious; empty facts -> clear.
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    suspicious = commander.run_case(
        _context(), [_DetectionStub(observed_facts=("sender_domain_mismatch",))]
    )
    assert suspicious.disposition == "suspicious"
    assert suspicious.challenge_pass == ()

    clear = commander.run_case(_context(), [_DetectionStub(observed_facts=())])
    assert clear.disposition == "clear"


def test_agent_id_guard_raises_governance_error_on_mismatch():
    # The Commander guard rejects a verdict whose agent_id != the agent's id.
    commander = SwarmCommander(
        {"blue_detection_001": _detection_entry(), "correct_id": _challenge_entry(agent_id="correct_id")}
    )
    with pytest.raises(GovernanceError, match="challenge result agent_id"):
        commander.run_case(
            _context(),
            [_DetectionStub()],
            challenge_agents=[_WrongIdChallengeAgent()],
        )


def test_detection_wrappers_return_none_from_challenge(tmp_path):
    # D6: the three governed Detection wrappers still return None from challenge.
    wrappers = [
        HeaderDivergenceAgent(blackboard_root=tmp_path, environment=Environment.PRODUCTION),
        GhostThreadAgent(blackboard_root=tmp_path, environment=Environment.PRODUCTION),
        EmailAuthenticationAgent(blackboard_root=tmp_path, environment=Environment.PRODUCTION),
    ]
    for wrapper in wrappers:
        assert wrapper.challenge(()) is None


def test_none_result_excluded_from_challenge_pass():
    # D2: a None verdict contributes nothing to challenge_pass.
    commander = SwarmCommander(
        {"blue_detection_001": _detection_entry(), "challenge_001": _challenge_entry()}
    )
    der = commander.run_case(
        _context(), [_DetectionStub()], challenge_agents=[_NoneChallengeAgent()]
    )
    assert der.challenge_pass == ()


def test_multiple_challenge_agents_each_invoked_once():
    # D1: with two challenge agents, each is invoked exactly once per case.
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            "challenge_001": _challenge_entry(),
            "challenge_002": _challenge_entry(agent_id="challenge_002"),
        }
    )
    a = _CountingChallengeAgent(agent_id="challenge_001")
    b = _CountingChallengeAgent(agent_id="challenge_002")
    der = commander.run_case(
        _context(), [_DetectionStub()], challenge_agents=[a, b]
    )
    assert a.call_count == 1
    assert b.call_count == 1
    assert len(der.challenge_pass) == 2
    assert {r.agent_id for r in der.challenge_pass} == {"challenge_001", "challenge_002"}


def test_empty_challenge_agents_produces_empty_challenge_pass():
    commander = SwarmCommander({"blue_detection_001": _detection_entry()})
    der = commander.run_case(_context(), [_DetectionStub()])
    assert der.challenge_pass == ()


# ===========================================================================
# Class 2 - Adversarial / break-it. Each documents what the mechanism does.
# ===========================================================================

def test_adversarial_vote_counting_probe():
    # D4 / ADV-001: the Commander does NOT inspect verdict *reasoning*, so a
    # count-only verdict still flows through. This test makes the gap visible
    # and named (failure register ADV-001): D4 is an agent-contract-level
    # constraint enforced by the Section 5 Agent Design Contract, not by the
    # spine. The probe asserts the count-only verdict is collected, not blocked.
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            "blue_detection_002": _detection_entry(agent_id="blue_detection_002"),
            "vote_counter_probe": _challenge_entry(agent_id="vote_counter_probe"),
        }
    )
    der = commander.run_case(
        _context(),
        [
            _DetectionStub(observed_facts=("from_reply_to_divergence",)),
            _DetectionStub(agent_id="blue_detection_002", observed_facts=("dmarc_fail",)),
        ],
        challenge_agents=[_VoteCountingChallengeAgent()],
    )
    result = der.challenge_pass[0]
    assert result.agent_id == "vote_counter_probe"
    # Verdict was derived from count alone (the anti-pattern), and the spine
    # collected it without inspecting reasoning - the documented D4 gap.
    assert result.challenge_outcome == "confirmed"
    assert result.challenge_basis.startswith("count=")


def test_adversarial_authority_drift_blocked():
    # D5: a challenge agent claiming autonomous_action_allowed=True diverges
    # from its registry entry (registry cannot hold autonomy) and is rejected
    # before invocation.
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            "authority_drift_probe": _challenge_entry(agent_id="authority_drift_probe"),
        }
    )
    with pytest.raises(GovernanceError, match="metadata diverges"):
        commander.run_case(
            _context(),
            [_DetectionStub()],
            challenge_agents=[_AuthorityDriftChallengeAgent()],
        )


def test_adversarial_reasoning_trace_not_exposed_on_contribution():
    # D3: AgentContribution exposes no reasoning trace / chain-of-thought. The
    # leak-probe agent's internal assertions hold, and we assert it directly.
    contribution = AgentContribution(
        agent_id="blue_detection_001", layer=2, observed_facts=("dmarc_fail",)
    )
    assert not hasattr(contribution, "reasoning_trace")
    assert not hasattr(contribution, "chain_of_thought")

    commander = SwarmCommander(
        {"blue_detection_001": _detection_entry(), "trace_leak_probe": _challenge_entry(agent_id="trace_leak_probe")}
    )
    der = commander.run_case(
        _context(), [_DetectionStub()], challenge_agents=[_ReasoningTraceLeakAgent()]
    )
    assert der.challenge_pass[0].agent_id == "trace_leak_probe"


def test_adversarial_split_signature_single_invocation_not_per_contribution():
    # D8 (observable guarantee): there is exactly one challenge() shape and the
    # Commander invokes it ONCE per case over the full set - never once per
    # contribution. With three contributions, a per-contribution loop would
    # call challenge() three times; the contract guarantees one call.
    commander = SwarmCommander(
        {
            "blue_detection_001": _detection_entry(),
            "blue_detection_002": _detection_entry(agent_id="blue_detection_002"),
            "blue_detection_003": _detection_entry(agent_id="blue_detection_003"),
            "challenge_001": _challenge_entry(),
        }
    )
    recorder = _CountingChallengeAgent()
    commander.run_case(
        _context(),
        [
            _DetectionStub(observed_facts=("from_reply_to_divergence",)),
            _DetectionStub(agent_id="blue_detection_002", observed_facts=("dmarc_fail",)),
            _DetectionStub(agent_id="blue_detection_003", observed_facts=("ghost_thread_subject",)),
        ],
        challenge_agents=[recorder],
    )
    assert recorder.call_count == 1
    assert recorder.seen_lengths == [3]


def test_adversarial_agent_id_mismatch_raises_governance_error():
    # The agent_id guard rejects a forged result id (mirrors the Class 1 guard
    # test via the dedicated wrong-id probe double).
    commander = SwarmCommander(
        {"blue_detection_001": _detection_entry(), "correct_id": _challenge_entry(agent_id="correct_id")}
    )
    with pytest.raises(GovernanceError, match="challenge result agent_id"):
        commander.run_case(
            _context(), [_DetectionStub()], challenge_agents=[_WrongIdChallengeAgent()]
        )


# ===========================================================================
# Class 3 - Known gap (expected to FAIL at v1, documented as xfail).
# Each maps to a failure-register entry (KG-001, KG-002) with a completion path.
# ===========================================================================

@pytest.mark.xfail(
    reason=(
        "KG-001: real-email corroboration quality cannot be validated until "
        "Stage 2 real samples exist. Completion path: Stage 2 real-sample data "
        "intake gate, then re-run this class against live data."
    ),
    strict=False,
)
def test_known_gap_real_email_corroboration_quality():
    # Stage A runs on synthetic/stub data only; corroboration quality on real
    # adversarial samples is unknowable here. Documented, not hidden.
    real_stage2_samples_available = False
    assert real_stage2_samples_available, (
        "KG-001: needs Stage 2 real samples (see failure register)"
    )


@pytest.mark.xfail(
    reason=(
        "KG-002: multi-Challenge-agent cross-arbitration is deferred to §10 Q1. "
        "No arbitration logic exists; the Commander collects all verdicts into "
        "challenge_pass with no conflict resolution. Completion path: §10 Q1 "
        "resolution + a signed Agent Design Contract before any build."
    ),
    strict=False,
)
def test_known_gap_multi_challenge_agent_cross_arbitration():
    # When two challenge agents disagree there is no defined arbitration; the
    # existing precedence (any contradicted -> human; any inconclusive -> hold)
    # is conservative but not true arbitration. Named here before Section 5.
    cross_arbitration_logic_exists = False
    assert cross_arbitration_logic_exists, (
        "KG-002: arbitration deferred to §10 Q1 (see failure register)"
    )


def test_determine_disposition_is_unchanged_by_section6():
    # Guard: Section 6 adds tests only; the disposition rule is untouched.
    facts = (AgentContribution(agent_id="a", layer=2, observed_facts=("x",)),)
    contradicted = (
        ChallengeResult(agent_id="c", challenge_outcome="contradicted", challenge_basis="x"),
    )
    inconclusive = (
        ChallengeResult(agent_id="c", challenge_outcome="inconclusive", challenge_basis="x"),
    )
    assert _determine_disposition((), ()) == "human_required"
    assert _determine_disposition(facts, contradicted) == "human_required"
    assert _determine_disposition(facts, inconclusive) == "hold"
    assert _determine_disposition(facts, ()) == "suspicious"
