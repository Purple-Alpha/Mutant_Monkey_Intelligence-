"""Canary threshold classifier — fail-closed (§9 / §6 canary fuzz target)."""

from __future__ import annotations

from enum import Enum

from mmi.m4.parser_surface import CanaryRule


class CanaryOutcome(str, Enum):
    OK = "OK"
    TRIP = "TRIP"


class ClassifierError(ValueError):
    """Unknown rule or signal — fail-closed."""


def _compare(value: float, threshold: float, comparator: str) -> bool:
    if comparator == "gt":
        return value > threshold
    if comparator == "gte":
        return value >= threshold
    if comparator == "lt":
        return value < threshold
    if comparator == "lte":
        return value <= threshold
    if comparator == "eq":
        return value == threshold
    raise ClassifierError(f"unknown comparator: {comparator}")


def classify_signal(value: float, rules: list[CanaryRule]) -> CanaryOutcome:
    if not rules:
        raise ClassifierError("no rules loaded")
    for rule in rules:
        if _compare(value, rule.threshold, rule.comparator):
            return CanaryOutcome.TRIP
    return CanaryOutcome.OK
