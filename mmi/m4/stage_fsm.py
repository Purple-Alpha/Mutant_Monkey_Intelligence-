"""Harness FSM transition table (§3.1 / §6 FSM fuzz target)."""

from __future__ import annotations

from enum import Enum


class FsmState(str, Enum):
    INIT = "INIT"
    PROVISION = "PROVISION"
    ARMED = "ARMED"
    INTERVAL_RUN = "INTERVAL_RUN"
    INTERVAL_EVAL = "INTERVAL_EVAL"
    RESET = "RESET"
    HALT = "HALT"
    ROLLUP = "ROLLUP"
    DONE = "DONE"


class FsmEvent(str, Enum):
    START_PROVISION = "START_PROVISION"
    PROVISION_DONE = "PROVISION_DONE"
    ARM = "ARM"
    BEGIN_INTERVAL = "BEGIN_INTERVAL"
    END_INTERVAL = "END_INTERVAL"
    END_INTERVAL_PASS = "END_INTERVAL_PASS"
    END_INTERVAL_DIAGNOSTIC = "END_INTERVAL_DIAGNOSTIC"
    END_INTERVAL_CRITICAL = "END_INTERVAL_CRITICAL"
    RESET = "RESET"
    HALT = "HALT"
    BEGIN_ROLLUP = "BEGIN_ROLLUP"
    FINISH = "FINISH"


TERMINAL = frozenset({FsmState.HALT, FsmState.DONE})

LEGAL_TRANSITIONS: dict[tuple[FsmState, FsmEvent], FsmState] = {
    (FsmState.INIT, FsmEvent.START_PROVISION): FsmState.PROVISION,
    (FsmState.PROVISION, FsmEvent.PROVISION_DONE): FsmState.ARMED,
    (FsmState.ARMED, FsmEvent.ARM): FsmState.ARMED,
    (FsmState.ARMED, FsmEvent.BEGIN_INTERVAL): FsmState.INTERVAL_RUN,
    (FsmState.INTERVAL_RUN, FsmEvent.END_INTERVAL): FsmState.INTERVAL_EVAL,
    (FsmState.INTERVAL_EVAL, FsmEvent.END_INTERVAL_PASS): FsmState.ARMED,
    (FsmState.INTERVAL_EVAL, FsmEvent.END_INTERVAL_DIAGNOSTIC): FsmState.RESET,
    (FsmState.INTERVAL_EVAL, FsmEvent.END_INTERVAL_CRITICAL): FsmState.HALT,
    (FsmState.RESET, FsmEvent.RESET): FsmState.ARMED,
    (FsmState.ARMED, FsmEvent.BEGIN_ROLLUP): FsmState.ROLLUP,
    (FsmState.ROLLUP, FsmEvent.FINISH): FsmState.DONE,
    (FsmState.HALT, FsmEvent.FINISH): FsmState.DONE,
}


class FsmError(ValueError):
    """Illegal transition rejected fail-closed."""


def apply_event(state: FsmState, event: FsmEvent) -> FsmState:
    if state in TERMINAL:
        raise FsmError(f"no transitions from terminal state {state.value}")
    key = (state, event)
    if key not in LEGAL_TRANSITIONS:
        raise FsmError(f"illegal transition {state.value} + {event.value}")
    return LEGAL_TRANSITIONS[key]


def credit_pass_allowed(state: FsmState, event: FsmEvent) -> bool:
    """PASS may only be credited from INTERVAL_EVAL via END_INTERVAL_PASS."""
    return state == FsmState.INTERVAL_EVAL and event == FsmEvent.END_INTERVAL_PASS
