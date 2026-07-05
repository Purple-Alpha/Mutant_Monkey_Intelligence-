"""Crash/resume latch — fail-closed interval credit (§6 restart fuzz target)."""

from __future__ import annotations

from dataclasses import dataclass


class RestartError(ValueError):
    """Resume rejected — unobserved interval or latch lost."""


@dataclass
class RunCheckpoint:
    state: str
    intervals_credited: int
    fail_closed_latched: bool
    last_observed_interval: int

    def snapshot(self) -> dict:
        return {
            "state": self.state,
            "intervals_credited": self.intervals_credited,
            "fail_closed_latched": self.fail_closed_latched,
            "last_observed_interval": self.last_observed_interval,
        }


@dataclass
class RestartLatch:
    checkpoint: RunCheckpoint | None = None
    latched_halt: bool = False

    def observe_interval(self, interval_id: int, credited: bool) -> None:
        if self.latched_halt:
            raise RestartError("fail-closed latch active")
        if self.checkpoint is None:
            self.checkpoint = RunCheckpoint(
                state="ARMED",
                intervals_credited=0,
                fail_closed_latched=False,
                last_observed_interval=-1,
            )
        cp = self.checkpoint
        if interval_id != cp.last_observed_interval + 1:
            raise RestartError("interval observed out of order")
        cp.last_observed_interval = interval_id
        if credited:
            cp.intervals_credited += 1

    def crash(self) -> dict:
        if self.checkpoint is None:
            raise RestartError("no checkpoint to crash from")
        return self.checkpoint.snapshot()

    def resume(self, snapshot: dict, credit_unobserved: bool = False) -> None:
        if self.latched_halt:
            raise RestartError("fail-closed latch active")
        if credit_unobserved:
            raise RestartError("cannot credit unobserved interval on resume")
        cp = RunCheckpoint(
            state=snapshot.get("state", ""),
            intervals_credited=int(snapshot.get("intervals_credited", -1)),
            fail_closed_latched=bool(snapshot.get("fail_closed_latched", True)),
            last_observed_interval=int(snapshot.get("last_observed_interval", -2)),
        )
        if cp.intervals_credited < 0 or cp.last_observed_interval < -1:
            raise RestartError("corrupt checkpoint")
        if cp.fail_closed_latched and snapshot.get("state") != "HALT":
            raise RestartError("fail-closed latch lost on resume")
        self.checkpoint = cp

    def trip_fail_closed(self) -> None:
        self.latched_halt = True
        if self.checkpoint:
            self.checkpoint.fail_closed_latched = True
            self.checkpoint.state = "HALT"
