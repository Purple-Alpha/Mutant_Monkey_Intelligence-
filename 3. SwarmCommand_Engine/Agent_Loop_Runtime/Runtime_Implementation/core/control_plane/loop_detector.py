"""LoopDetector — Phase 6 (Layer 6), Gate 1: behavioral loop detection.

Governing contract
------------------
``4. Product_Roadmap/Blast_Radius_Controller_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — BRC-D3 + §3.3.

Two behavioral signals only — **no embeddings, no content inspection**:
  - **Identical-argument runs:** the same (tool + args-hash) repeated within a
    window beyond a threshold.
  - **Call-frequency spikes:** calls per unit time above a threshold.

BRC-D3 metastasis test: an agent that **mutates its arguments** to dodge the
identical-run check is still caught by the call-frequency signal — detection is
on behavioral metrics, never on what the arguments *say*.

The args hash is computed structurally (a stable repr hash); the detector never
looks inside the content. The clock is injectable for deterministic tests.
"""

from __future__ import annotations

import hashlib
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

# Launch-conservative defaults (amendment-tunable).
IDENTICAL_RUN_THRESHOLD = 3          # identical (tool, args) within the window
FREQUENCY_WINDOW_SECONDS = 10.0      # sliding window for call-frequency
FREQUENCY_THRESHOLD = 10             # max calls per window before a loop is flagged


def _args_hash(args: Any) -> str:
    """Structural hash of call arguments. Stable, content-opaque (BRC-D3)."""

    return hashlib.sha256(repr(args).encode("utf-8")).hexdigest()


@dataclass
class _AgentCallHistory:
    recent_times: deque[float] = field(default_factory=deque)
    identical_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class LoopDetector:
    """Behavioral loop detection — identical-run + frequency only (BRC-D3)."""

    now: Callable[[], float] = time.monotonic
    identical_run_threshold: int = IDENTICAL_RUN_THRESHOLD
    frequency_window_seconds: float = FREQUENCY_WINDOW_SECONDS
    frequency_threshold: int = FREQUENCY_THRESHOLD
    _history: dict[str, _AgentCallHistory] = field(default_factory=dict)

    def _key(self, agent_id: str, session_id: str) -> str:
        return f"{agent_id}::{session_id}"

    def observe(
        self, *, agent_id: str, session_id: str, tool: str, args: Any
    ) -> bool:
        """Record one call. Returns ``True`` if a loop is detected (caller should
        trip the breaker), ``False`` otherwise. Behavioral metrics only.
        """

        history = self._history.setdefault(
            self._key(agent_id, session_id), _AgentCallHistory()
        )
        now = self.now()

        # Call-frequency signal (catches argument-mutation bypass — BRC-D3).
        history.recent_times.append(now)
        cutoff = now - self.frequency_window_seconds
        while history.recent_times and history.recent_times[0] < cutoff:
            history.recent_times.popleft()
        frequency_loop = len(history.recent_times) > self.frequency_threshold

        # Identical-argument-run signal.
        signature = f"{tool}:{_args_hash(args)}"
        count = history.identical_counts.get(signature, 0) + 1
        history.identical_counts[signature] = count
        identical_loop = count >= self.identical_run_threshold

        return frequency_loop or identical_loop

    def reset(self, *, agent_id: str, session_id: str) -> None:
        self._history.pop(self._key(agent_id, session_id), None)


__all__ = [
    "IDENTICAL_RUN_THRESHOLD",
    "FREQUENCY_WINDOW_SECONDS",
    "FREQUENCY_THRESHOLD",
    "LoopDetector",
]
