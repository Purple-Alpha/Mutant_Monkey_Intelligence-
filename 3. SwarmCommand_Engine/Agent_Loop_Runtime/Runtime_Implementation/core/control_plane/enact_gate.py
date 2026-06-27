"""Enactment gate stubs — Brain Acceleration detect-not-enact boundary.

Any function that would block, drop, contain, or mutate production state must
pass Matt §11 before implementation. Callers receive ``EnactmentBlockedError``.
"""

from __future__ import annotations


class EnactmentBlockedError(RuntimeError):
    """REQUIRES_§11_GATE — enactment not authorized."""


def enact_block(*_args, **_kwargs) -> None:
    raise EnactmentBlockedError(
        "REQUIRES_§11_GATE: block/drop enactment is not implemented"
    )


def enact_contain(*_args, **_kwargs) -> None:
    raise EnactmentBlockedError(
        "REQUIRES_§11_GATE: containment enactment is not implemented"
    )


__all__ = ["EnactmentBlockedError", "enact_block", "enact_contain"]
