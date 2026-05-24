"""Eval dataset loader for the Phase 1.1 fraud eval harness.

Dataset format is JSON Lines, one ``EvalCase`` per line, matching the shape
documented in ``4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md``
§4.1. The loader validates each row strictly; an unknown field, an unknown
``subcategory``, or a missing required field raises ``EvalDatasetError`` so
dataset drift is caught at load time, not at run time.

The loader is intentionally schema-strict (no defaults for missing fields
beyond ``expected.*`` bounds which are all optional) so curated cases are
always self-documenting on disk.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, TypeAlias, get_args

from core.blackboard import BehavioralDeviationFlag, EmailInboundPayload

DEFAULT_DATASET_PATH = Path(__file__).parent / "fraud_eval_dataset.jsonl"

EvalLabel: TypeAlias = Literal["fraud", "legit"]

# Subcategory enum from Phase_1_1_Fraud_Prevention_Deep_Dive.md §4.2. Same
# schema-versioned pattern as ``AttachmentClass`` / ``BehavioralDeviationFlag``:
# growing the set requires a deliberate schema change, not a freeform addition.
EvalSubcategory: TypeAlias = Literal[
    "vendor_invoice_fraud",
    "executive_impersonation",
    "wire_transfer_pressure",
    "invoice_authenticity_anomaly",
    "lookalike_sender",
    "header_inconsistency",
    "legit_vendor_invoice",
    "legit_internal",
    "legit_calendar",
    "legit_hr",
    "legit_newsletter",
]

_VALID_LABELS: frozenset[str] = frozenset(("fraud", "legit"))
_VALID_SUBCATEGORIES: frozenset[str] = frozenset(
    (
        "vendor_invoice_fraud",
        "executive_impersonation",
        "wire_transfer_pressure",
        "invoice_authenticity_anomaly",
        "lookalike_sender",
        "header_inconsistency",
        "legit_vendor_invoice",
        "legit_internal",
        "legit_calendar",
        "legit_hr",
        "legit_newsletter",
    )
)
_VALID_RECOMMENDED_ACTIONS: frozenset[str] = frozenset(("safe", "needs_review", "block"))

# Derived from the BehavioralDeviationFlag Literal so the loader stays in
# lockstep with the schema. If the Literal grows or shrinks, the loader
# automatically accepts the new set without an edit here.
_VALID_BEHAVIORAL_DEVIATION_FLAGS: frozenset[str] = frozenset(
    get_args(BehavioralDeviationFlag)
)


class EvalDatasetError(ValueError):
    """Raised on dataset shape / value errors at load time."""


@dataclass(frozen=True)
class EvalCaseExpected:
    """Bounds an eval case asserts against the agent's output.

    All fields are optional. Threshold scores (vendor / wire / risk) use
    ``min_*`` bounds for fraud cases and ``max_*`` bounds for legit cases.
    The inverted ``invoice_authenticity_score`` uses ``max_*`` for fraud
    (low = inauthentic) and ``min_*`` for legit (high = authentic).

    ``recommended_action_in`` is a whitelist; any other recommendation
    counts as failure for the eval case.

    ``behavioral_deviation_flags`` is the **required** set of flags.
    ``None`` (default) means the case does not assert on flags. When a
    tuple is supplied, every flag in the tuple must appear in the
    agent's emitted flag set. Extra flags emitted by the agent do
    **not** fail the case unless they are explicitly listed in
    ``forbidden_behavioral_deviation_flags``. This is the post-Month-2
    calibration of the original strict-equality contract: the
    diagnostic eval showed model over-flagging was not actually
    harmful (precision and FPR were perfect) while the strict-equality
    contract was blocking otherwise correct fraud detections.

    ``forbidden_behavioral_deviation_flags`` is the optional explicit
    forbidden set. ``None`` (default) means the case does not assert on
    forbidden flags. When a tuple is supplied, an emitted flag in the
    forbidden set fails the case. A flag may not appear in both the
    required and the forbidden tuples for the same case; the loader
    rejects that overlap to keep the contract unambiguous.
    """

    min_risk_score: int | None = None
    max_risk_score: int | None = None
    min_vendor_fraud_score: int | None = None
    max_vendor_fraud_score: int | None = None
    min_wire_transfer_anomaly_score: int | None = None
    max_wire_transfer_anomaly_score: int | None = None
    min_invoice_authenticity_score: int | None = None
    max_invoice_authenticity_score: int | None = None
    recommended_action_in: tuple[str, ...] = field(default_factory=tuple)
    behavioral_deviation_flags: tuple[BehavioralDeviationFlag, ...] | None = None
    forbidden_behavioral_deviation_flags: (
        tuple[BehavioralDeviationFlag, ...] | None
    ) = None


@dataclass(frozen=True)
class EvalCase:
    """One eval row: an inbound email + expected output bounds."""

    case_id: str
    label: EvalLabel
    subcategory: EvalSubcategory
    email: EmailInboundPayload
    expected: EvalCaseExpected


_REQUIRED_ROW_KEYS: frozenset[str] = frozenset(
    ("case_id", "label", "subcategory", "email", "expected")
)

_ALLOWED_EXPECTED_KEYS: frozenset[str] = frozenset(
    (
        "min_risk_score",
        "max_risk_score",
        "min_vendor_fraud_score",
        "max_vendor_fraud_score",
        "min_wire_transfer_anomaly_score",
        "max_wire_transfer_anomaly_score",
        "min_invoice_authenticity_score",
        "max_invoice_authenticity_score",
        "recommended_action_in",
        "behavioral_deviation_flags",
        "forbidden_behavioral_deviation_flags",
    )
)


def load_dataset(path: Path | None = None) -> list[EvalCase]:
    """Load and validate the JSONL eval dataset.

    Returns the parsed cases in source order. Raises ``EvalDatasetError``
    for any schema drift, missing field, or unknown enum value.
    """

    resolved = path or DEFAULT_DATASET_PATH
    if not resolved.exists():
        raise EvalDatasetError(f"dataset file not found: {resolved}")

    cases: list[EvalCase] = []
    with resolved.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise EvalDatasetError(
                    f"line {line_number}: invalid JSON ({exc.msg})"
                ) from exc
            cases.append(_build_case(row, line_number=line_number))
    return cases


def iter_dataset(path: Path | None = None) -> Iterable[EvalCase]:
    """Iterator alias for memory-friendly callers (currently same impl)."""

    yield from load_dataset(path)


def _build_case(row: Any, *, line_number: int) -> EvalCase:
    if not isinstance(row, dict):
        raise EvalDatasetError(f"line {line_number}: row must be a JSON object")

    missing = _REQUIRED_ROW_KEYS - row.keys()
    if missing:
        raise EvalDatasetError(
            f"line {line_number}: missing required fields {sorted(missing)}"
        )
    unexpected = row.keys() - _REQUIRED_ROW_KEYS
    if unexpected:
        raise EvalDatasetError(
            f"line {line_number}: unexpected fields {sorted(unexpected)}"
        )

    case_id = row["case_id"]
    if not isinstance(case_id, str) or not case_id:
        raise EvalDatasetError(f"line {line_number}: case_id must be a non-empty string")

    label = row["label"]
    if label not in _VALID_LABELS:
        raise EvalDatasetError(
            f"line {line_number}: label must be one of {sorted(_VALID_LABELS)}, got {label!r}"
        )

    subcategory = row["subcategory"]
    if subcategory not in _VALID_SUBCATEGORIES:
        raise EvalDatasetError(
            f"line {line_number}: subcategory must be one of {sorted(_VALID_SUBCATEGORIES)}, "
            f"got {subcategory!r}"
        )

    try:
        email = EmailInboundPayload.model_validate(row["email"])
    except Exception as exc:
        raise EvalDatasetError(
            f"line {line_number}: email failed EmailInboundPayload validation: {exc}"
        ) from exc

    expected = _build_expected(row["expected"], line_number=line_number)

    return EvalCase(
        case_id=case_id,
        label=label,  # type: ignore[arg-type]
        subcategory=subcategory,  # type: ignore[arg-type]
        email=email,
        expected=expected,
    )


def _build_expected(raw: Any, *, line_number: int) -> EvalCaseExpected:
    if not isinstance(raw, dict):
        raise EvalDatasetError(f"line {line_number}: expected must be a JSON object")
    unexpected = raw.keys() - _ALLOWED_EXPECTED_KEYS
    if unexpected:
        raise EvalDatasetError(
            f"line {line_number}: expected has unexpected fields {sorted(unexpected)}"
        )
    actions_raw = raw.get("recommended_action_in", [])
    if not isinstance(actions_raw, list):
        raise EvalDatasetError(
            f"line {line_number}: expected.recommended_action_in must be a list"
        )
    for action in actions_raw:
        if action not in _VALID_RECOMMENDED_ACTIONS:
            raise EvalDatasetError(
                f"line {line_number}: expected.recommended_action_in contains "
                f"unknown value {action!r}; must be from {sorted(_VALID_RECOMMENDED_ACTIONS)}"
            )

    def _int_bound(key: str) -> int | None:
        value = raw.get(key)
        if value is None:
            return None
        if not isinstance(value, int) or isinstance(value, bool):
            raise EvalDatasetError(
                f"line {line_number}: expected.{key} must be an int, got {type(value).__name__}"
            )
        if not (0 <= value <= 100):
            raise EvalDatasetError(
                f"line {line_number}: expected.{key} must be in [0, 100], got {value}"
            )
        return value

    behavioral_flags = _build_behavioral_flags(
        raw.get("behavioral_deviation_flags", None),
        line_number=line_number,
        field_name="behavioral_deviation_flags",
    )
    forbidden_flags = _build_behavioral_flags(
        raw.get("forbidden_behavioral_deviation_flags", None),
        line_number=line_number,
        field_name="forbidden_behavioral_deviation_flags",
    )
    if behavioral_flags is not None and forbidden_flags is not None:
        overlap = set(behavioral_flags) & set(forbidden_flags)
        if overlap:
            raise EvalDatasetError(
                f"line {line_number}: behavioral_deviation_flags and "
                f"forbidden_behavioral_deviation_flags overlap on "
                f"{sorted(overlap)}; a flag cannot be both required and "
                f"forbidden"
            )

    return EvalCaseExpected(
        min_risk_score=_int_bound("min_risk_score"),
        max_risk_score=_int_bound("max_risk_score"),
        min_vendor_fraud_score=_int_bound("min_vendor_fraud_score"),
        max_vendor_fraud_score=_int_bound("max_vendor_fraud_score"),
        min_wire_transfer_anomaly_score=_int_bound("min_wire_transfer_anomaly_score"),
        max_wire_transfer_anomaly_score=_int_bound("max_wire_transfer_anomaly_score"),
        min_invoice_authenticity_score=_int_bound("min_invoice_authenticity_score"),
        max_invoice_authenticity_score=_int_bound("max_invoice_authenticity_score"),
        recommended_action_in=tuple(actions_raw),
        behavioral_deviation_flags=behavioral_flags,
        forbidden_behavioral_deviation_flags=forbidden_flags,
    )


def _build_behavioral_flags(
    raw: Any,
    *,
    line_number: int,
    field_name: str = "behavioral_deviation_flags",
) -> tuple[BehavioralDeviationFlag, ...] | None:
    """Validate an optional behavioral-flag tuple field.

    Accepts ``None`` / missing (the field is opt-in per case) or a JSON
    list of strings where each string is a value of
    :data:`BehavioralDeviationFlag`. Duplicates are rejected so the
    on-disk dataset stays canonical and subset / intersection checks in
    the runner have no ambiguity. An empty list is allowed; the loader
    preserves it as an empty tuple and the runner treats it as a no-op
    assertion for that field (it neither requires nor forbids anything).

    ``field_name`` is used only to format error messages so callers
    that share this validator for ``behavioral_deviation_flags`` and
    ``forbidden_behavioral_deviation_flags`` get accurate diagnostics.
    """

    if raw is None:
        return None
    if not isinstance(raw, list):
        raise EvalDatasetError(
            f"line {line_number}: expected.{field_name} must be "
            f"a list, got {type(raw).__name__}"
        )

    seen: set[str] = set()
    flags: list[BehavioralDeviationFlag] = []
    for value in raw:
        if not isinstance(value, str):
            raise EvalDatasetError(
                f"line {line_number}: expected.{field_name} entry "
                f"must be a string, got {type(value).__name__}"
            )
        if value not in _VALID_BEHAVIORAL_DEVIATION_FLAGS:
            raise EvalDatasetError(
                f"line {line_number}: expected.{field_name} "
                f"contains unknown value {value!r}; must be from "
                f"{sorted(_VALID_BEHAVIORAL_DEVIATION_FLAGS)}"
            )
        if value in seen:
            raise EvalDatasetError(
                f"line {line_number}: expected.{field_name} "
                f"contains duplicate value {value!r}"
            )
        seen.add(value)
        flags.append(value)  # type: ignore[arg-type]
    return tuple(flags)
