"""Base class for Shadow Watcher Swarm Layer 1 agents."""

from __future__ import annotations

from core.orchestrator.dual_llm import AgentClass

from .observation import (
    CandidateAlarmFact,
    ObservedFact,
    ShadowEmailEvent,
    ShadowInference,
    ShadowObservationLog,
    ShadowObservationRecord,
    ShadowWatcherError,
    ShadowWatcherKind,
)


class ShadowWatcherBoundaryError(ShadowWatcherError):
    """Raised when a Shadow Watcher attempts a forbidden Layer 1 action."""


class BaseShadowWatcher:
    """Q-class observe-only watcher.

    It receives raw event data, emits structured alarm-input observations, and
    has no tool, credential, block, verdict, recommendation, or blackboard path.
    """

    WATCHER_ID = "base_shadow_watcher"
    KIND: ShadowWatcherKind

    agent_class = AgentClass.Q_CLASS
    tool_scope = frozenset()
    credentials = frozenset()

    def __init__(self, *, log: ShadowObservationLog | None = None) -> None:
        self._log = log or ShadowObservationLog()

    @property
    def log(self) -> ShadowObservationLog:
        return self._log

    def observe(self, event: ShadowEmailEvent) -> ShadowObservationRecord:
        raise NotImplementedError

    def _record(
        self,
        event: ShadowEmailEvent,
        *,
        observed_facts: tuple[ObservedFact, ...],
        inferences: tuple[ShadowInference, ...],
        evidence_used: tuple[str, ...],
        candidate_alarm_facts: tuple[CandidateAlarmFact, ...],
        confidence: float,
    ) -> ShadowObservationRecord:
        record = ShadowObservationRecord(
            watcher_id=self.WATCHER_ID,
            watcher_kind=self.KIND,
            tenant_id=event.tenant_id,
            email_id=event.email_id,
            observed_facts=observed_facts,
            inferences=inferences,
            evidence_used=evidence_used,
            candidate_alarm_facts=candidate_alarm_facts,
            confidence=confidence,
            raw_text_present=False,
        )
        return self._log.append(record)

    # Hard boundaries: always reject under SWS-D3/SWS-D4/SWS-D5.
    def request_tool(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError("Shadow Watchers are Q-class and cannot request tools")

    def add_credential(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError("Shadow Watchers cannot hold credentials")

    def write_blackboard(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError("Shadow Watchers do not write core/blackboard/")

    def block_action(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError("Shadow Watchers never block actions alone")

    def make_final_fraud_claim(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError("Shadow Watchers never make final fraud claims")

    def make_recommendation(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise ShadowWatcherBoundaryError(
            "Shadow Watchers make no recommendations beyond evidence explanation"
        )


__all__ = ["BaseShadowWatcher", "ShadowWatcherBoundaryError"]
