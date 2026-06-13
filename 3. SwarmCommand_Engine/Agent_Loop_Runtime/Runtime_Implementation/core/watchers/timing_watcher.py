"""W1 TimingWatcher (#85) — Watcher Agents (Layer 6 Governance).

Governing contract
------------------
``4. Product_Roadmap/Watcher_Agents_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — §3.1.

Monitors agent completion times against **signed baseline windows**, flags agents
that exceed their window (catching stuck agents before they create backlog), and
watches for **loop signatures** — the same tool called with identical arguments
repeatedly (behavioral, consistent with BRC-D3). Emits ``timing_anomaly``,
``loop_detected``, ``inactivity_flag`` only.

Facts only (WA-D7): completion times and call signatures are supplied to the
watcher; it never reaches into the agents it observes.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict

from core.watchers.base import BaseWatcher
from core.watchers.observation import ObservationRecord, ObservationType, Severity, SWARM_SCOPE

# Launch-conservative defaults (WA-D11; amendment-tunable after tenant baselines).
DEFAULT_LOOP_THRESHOLD = 3  # identical (tool, args) repeats before loop_detected


def _args_signature(tool: str, args: object) -> str:
    return f"{tool}:{hashlib.sha256(repr(args).encode('utf-8')).hexdigest()}"


class TimingWatcher(BaseWatcher):
    """#85 — completion-window and loop-signature observer."""

    ALLOWED_TYPES = frozenset(
        {
            ObservationType.TIMING_ANOMALY,
            ObservationType.LOOP_DETECTED,
            ObservationType.INACTIVITY_FLAG,
        }
    )

    def __init__(self, *args, loop_threshold: int = DEFAULT_LOOP_THRESHOLD, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop_threshold = loop_threshold
        self._call_counts: dict[tuple[str, str], int] = defaultdict(int)

    def observe_completion(
        self,
        *,
        observed_agent: str,
        elapsed_seconds: float,
        baseline_window_seconds: float,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord | None:
        """Flag an agent that exceeds its signed baseline completion window."""

        if elapsed_seconds <= baseline_window_seconds:
            return None
        overage = elapsed_seconds - baseline_window_seconds
        severity = (
            Severity.WARNING
            if overage <= baseline_window_seconds
            else Severity.CRITICAL
        )
        return self._observe(
            observation_type=ObservationType.TIMING_ANOMALY,
            severity=severity,
            observed_agent=observed_agent,
            details=(
                f"completion {elapsed_seconds:.1f}s exceeds baseline window "
                f"{baseline_window_seconds:.1f}s by {overage:.1f}s"
            ),
            tenant_id=tenant_id,
        )

    def observe_inactivity(
        self, *, observed_agent: str, idle_seconds: float, max_idle_seconds: float,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord | None:
        """Flag an agent that has gone silent past its allowed idle window."""

        if idle_seconds <= max_idle_seconds:
            return None
        return self._observe(
            observation_type=ObservationType.INACTIVITY_FLAG,
            severity=Severity.WARNING,
            observed_agent=observed_agent,
            details=f"idle {idle_seconds:.1f}s exceeds max {max_idle_seconds:.1f}s",
            tenant_id=tenant_id,
        )

    def observe_call(
        self, *, observed_agent: str, tool: str, args: object,
        tenant_id: str = SWARM_SCOPE,
    ) -> ObservationRecord | None:
        """Record a tool call; emit ``loop_detected`` when an identical (tool,
        args) signature repeats past the threshold. Behavioral, not content."""

        signature = _args_signature(tool, args)
        key = (observed_agent, signature)
        self._call_counts[key] += 1
        if self._call_counts[key] >= self.loop_threshold:
            return self._observe(
                observation_type=ObservationType.LOOP_DETECTED,
                severity=Severity.WARNING,
                observed_agent=observed_agent,
                details=(
                    f"tool {tool!r} called with identical arguments "
                    f"{self._call_counts[key]} times (loop signature)"
                ),
                tenant_id=tenant_id,
            )
        return None


__all__ = ["DEFAULT_LOOP_THRESHOLD", "TimingWatcher"]
