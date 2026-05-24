"""Phase 1.1 fraud eval harness — runner + report.

Given an injectable ``LLMClient`` callable, ``run_eval`` iterates the
provided cases, prompts the scoring agent's locked system prompt against
each email, parses the response into ``EmailAnalysisPayload``, and checks
the actual fields against each case's ``EvalCaseExpected`` bounds.

Deliberately decoupled from the blackboard / production loop — the eval
harness is offline machinery for measuring scoring quality. It does not
write records, does not require a tenant, and does not run inside the
regular pytest CI suite (see ``__init__.py`` docstring for the rationale).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable
from uuid import uuid4

from pydantic import ValidationError

from core.blackboard import (
    EmailAnalysisPayload,
    EmailInboundPayload,
)
from core.scoring.email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
)

from .dataset import EvalCase, EvalCaseExpected, EvalSubcategory

LLMClient = Callable[[str, str], str]

# Pass-gate thresholds from Phase_1_1_Fraud_Prevention_Deep_Dive.md §4.5.
# Kept as module-level constants so callers (and tests) can reference the
# exact gate the harness evaluates against without scraping the runner.
PASS_GATE_MIN_PRECISION_ON_FRAUD: float = 0.80
PASS_GATE_MAX_FPR_ON_LEGIT: float = 0.10
PASS_GATE_MIN_PER_SUBCATEGORY_RECALL: float = 0.60

# Subcategories that count as "fraud" for the per-subcategory recall gate.
# Mirrors the dataset module's fraud subcategory list. Kept here rather
# than imported so the runner aggregation does not couple to the dataset
# loader's literal definition.
_FRAUD_SUBCATEGORIES: frozenset[str] = frozenset(
    (
        "vendor_invoice_fraud",
        "executive_impersonation",
        "wire_transfer_pressure",
        "invoice_authenticity_anomaly",
        "lookalike_sender",
        "header_inconsistency",
    )
)


@dataclass(frozen=True)
class EvalCaseResult:
    """Outcome of evaluating one case.

    ``actual_analysis`` is ``None`` when the LLM client raised or returned
    something that failed JSON / schema parsing. ``failure_reason`` is set
    in that situation. ``failed_assertions`` is empty when ``passed`` is
    True; it lists every bound that was violated otherwise.
    """

    case: EvalCase
    raw_response: str
    actual_analysis: EmailAnalysisPayload | None
    failure_reason: str | None
    passed: bool
    failed_assertions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvalSubcategoryStats:
    subcategory: EvalSubcategory
    total: int
    passed: int

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def recall(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total


@dataclass(frozen=True)
class EvalReport:
    total: int
    passed: int
    per_subcategory: dict[EvalSubcategory, EvalSubcategoryStats]
    precision_on_fraud: float
    false_positive_rate_on_legit: float
    results: list[EvalCaseResult]

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def precision_gate_met(self) -> bool:
        return self.precision_on_fraud >= PASS_GATE_MIN_PRECISION_ON_FRAUD

    @property
    def fpr_gate_met(self) -> bool:
        return self.false_positive_rate_on_legit <= PASS_GATE_MAX_FPR_ON_LEGIT

    @property
    def per_subcategory_recall_gate_met(self) -> bool:
        """True iff every fraud subcategory present in the report meets the recall floor.

        Subcategories with zero cases in the report (legit subcategories,
        or fraud subcategories that were filtered out for a partial run)
        are excluded from the check. An empty fraud-subcategory set
        returns True (vacuously) so subset runs are not penalized; the
        full 40-case dataset covers all six fraud subcategories so this
        only matters for diagnostic partial runs.
        """

        for subcategory, stats in self.per_subcategory.items():
            if subcategory not in _FRAUD_SUBCATEGORIES:
                continue
            if stats.total == 0:
                continue
            if stats.recall < PASS_GATE_MIN_PER_SUBCATEGORY_RECALL:
                return False
        return True

    @property
    def gate_passed(self) -> bool:
        """All three §4.5 criteria met simultaneously."""

        return (
            self.precision_gate_met
            and self.fpr_gate_met
            and self.per_subcategory_recall_gate_met
        )

    def per_subcategory_recall_failures(self) -> list[tuple[str, float]]:
        """Return ``(subcategory, recall)`` pairs that miss the recall floor."""

        failures: list[tuple[str, float]] = []
        for subcategory in sorted(self.per_subcategory.keys()):
            if subcategory not in _FRAUD_SUBCATEGORIES:
                continue
            stats = self.per_subcategory[subcategory]
            if stats.total == 0:
                continue
            if stats.recall < PASS_GATE_MIN_PER_SUBCATEGORY_RECALL:
                failures.append((subcategory, stats.recall))
        return failures

    def markdown_table(self) -> str:
        """Render the report as a markdown summary suitable for the activity log."""

        lines: list[str] = []
        lines.append(f"## Fraud Eval Report — {self.total} cases")
        lines.append("")
        lines.append(f"- Overall passed: {self.passed} / {self.total}")
        lines.append(f"- Precision on fraud cases: {self.precision_on_fraud:.2%}")
        lines.append(
            f"- False positive rate on legit cases: "
            f"{self.false_positive_rate_on_legit:.2%}"
        )
        lines.append("")
        lines.append("### Pass Gate (Phase 1.1 deep dive §4.5)")
        lines.append("")
        lines.append("| Criterion | Threshold | Actual | Met |")
        lines.append("| --- | --- | --- | --- |")
        lines.append(
            f"| Precision on fraud | >= {PASS_GATE_MIN_PRECISION_ON_FRAUD:.0%} | "
            f"{self.precision_on_fraud:.2%} | "
            f"{'YES' if self.precision_gate_met else 'NO'} |"
        )
        lines.append(
            f"| FPR on legit | <= {PASS_GATE_MAX_FPR_ON_LEGIT:.0%} | "
            f"{self.false_positive_rate_on_legit:.2%} | "
            f"{'YES' if self.fpr_gate_met else 'NO'} |"
        )
        recall_actual = (
            "all fraud subcategories meet floor"
            if self.per_subcategory_recall_gate_met
            else "; ".join(
                f"{name} {recall:.2%}"
                for name, recall in self.per_subcategory_recall_failures()
            )
        )
        lines.append(
            f"| Per-fraud-subcategory recall | "
            f">= {PASS_GATE_MIN_PER_SUBCATEGORY_RECALL:.0%} each | "
            f"{recall_actual} | "
            f"{'YES' if self.per_subcategory_recall_gate_met else 'NO'} |"
        )
        lines.append("")
        lines.append(f"**Gate verdict:** {'PASS' if self.gate_passed else 'FAIL'}")
        lines.append("")
        lines.append("### Per-subcategory breakdown")
        lines.append("")
        lines.append("| Subcategory | Total | Passed | Recall |")
        lines.append("| --- | --- | --- | --- |")
        for subcategory in sorted(self.per_subcategory.keys()):
            stats = self.per_subcategory[subcategory]
            lines.append(
                f"| {subcategory} | {stats.total} | {stats.passed} | "
                f"{stats.recall:.2%} |"
            )
        return "\n".join(lines) + "\n"


def run_eval(
    cases: Iterable[EvalCase],
    *,
    llm_client: LLMClient,
) -> EvalReport:
    """Run the eval harness over ``cases`` against ``llm_client``.

    The harness uses the **locked** scoring system prompt
    (:data:`NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`) so eval results
    correspond exactly to what the production scoring agent would emit.
    """

    cases_list = list(cases)
    results: list[EvalCaseResult] = []
    for case in cases_list:
        results.append(_evaluate_one(case, llm_client=llm_client))

    return _aggregate(results)


def _evaluate_one(case: EvalCase, *, llm_client: LLMClient) -> EvalCaseResult:
    user_prompt = _build_user_prompt(case.email)
    try:
        raw_response = llm_client(NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:  # noqa: BLE001 - eval surface intentionally broad
        return EvalCaseResult(
            case=case,
            raw_response="",
            actual_analysis=None,
            failure_reason=f"llm_client_raised:{type(exc).__name__}:{exc}",
            passed=False,
            failed_assertions=[],
        )

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        return EvalCaseResult(
            case=case,
            raw_response=raw_response,
            actual_analysis=None,
            failure_reason=f"invalid_json:{exc.msg}",
            passed=False,
            failed_assertions=[],
        )

    if not isinstance(parsed, dict):
        return EvalCaseResult(
            case=case,
            raw_response=raw_response,
            actual_analysis=None,
            failure_reason="schema_root_not_object",
            passed=False,
            failed_assertions=[],
        )

    # Eval harness assigns synthetic source_email_record_id / produced_at so the
    # caller's deterministic fake LLM client does not need to know either.
    construction_input = dict(parsed)
    construction_input.setdefault("source_email_record_id", str(uuid4()))
    construction_input.setdefault(
        "produced_at", datetime.now(timezone.utc).isoformat()
    )

    try:
        analysis = EmailAnalysisPayload.model_validate(construction_input)
    except ValidationError as exc:
        return EvalCaseResult(
            case=case,
            raw_response=raw_response,
            actual_analysis=None,
            failure_reason=f"schema_mismatch:{exc.error_count()}_errors",
            passed=False,
            failed_assertions=[],
        )

    failed = _check_expected(case.expected, analysis)
    return EvalCaseResult(
        case=case,
        raw_response=raw_response,
        actual_analysis=analysis,
        failure_reason=None,
        passed=not failed,
        failed_assertions=failed,
    )


def _build_user_prompt(payload: EmailInboundPayload) -> str:
    """Same shape as the scoring agent's user prompt so eval is realistic.

    Mirrors ``core.scoring.email_risk_scoring_agent._build_user_prompt`` —
    the eval harness intentionally does not import that private helper so
    the two can drift independently if the production prompt format
    changes; the eval harness then becomes a forcing function to update
    the dataset.
    """

    return json.dumps(
        {
            "source_email_record_id": "eval-harness",
            "sender": payload.sender,
            "recipient": payload.recipient,
            "subject": payload.subject,
            "received_at": payload.received_at.isoformat(),
            "headers": payload.headers,
            "attachments": [
                attachment.model_dump(mode="json")
                for attachment in payload.attachments
            ],
            "body_plain": payload.body_plain,
            "body_html_present": payload.body_html is not None,
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def _check_expected(
    expected: EvalCaseExpected, analysis: EmailAnalysisPayload
) -> list[str]:
    """Return a list of human-readable assertion failures (empty = passed)."""

    failed: list[str] = []
    risk = analysis.risk_analysis

    if expected.min_risk_score is not None and risk.risk_score < expected.min_risk_score:
        failed.append(
            f"risk_score {risk.risk_score} < min {expected.min_risk_score}"
        )
    if expected.max_risk_score is not None and risk.risk_score > expected.max_risk_score:
        failed.append(
            f"risk_score {risk.risk_score} > max {expected.max_risk_score}"
        )

    if (
        expected.min_vendor_fraud_score is not None
        and risk.vendor_fraud_score < expected.min_vendor_fraud_score
    ):
        failed.append(
            f"vendor_fraud_score {risk.vendor_fraud_score} < min "
            f"{expected.min_vendor_fraud_score}"
        )
    if (
        expected.max_vendor_fraud_score is not None
        and risk.vendor_fraud_score > expected.max_vendor_fraud_score
    ):
        failed.append(
            f"vendor_fraud_score {risk.vendor_fraud_score} > max "
            f"{expected.max_vendor_fraud_score}"
        )

    if (
        expected.min_wire_transfer_anomaly_score is not None
        and risk.wire_transfer_anomaly_score
        < expected.min_wire_transfer_anomaly_score
    ):
        failed.append(
            f"wire_transfer_anomaly_score {risk.wire_transfer_anomaly_score} < min "
            f"{expected.min_wire_transfer_anomaly_score}"
        )
    if (
        expected.max_wire_transfer_anomaly_score is not None
        and risk.wire_transfer_anomaly_score
        > expected.max_wire_transfer_anomaly_score
    ):
        failed.append(
            f"wire_transfer_anomaly_score {risk.wire_transfer_anomaly_score} > max "
            f"{expected.max_wire_transfer_anomaly_score}"
        )

    if expected.min_invoice_authenticity_score is not None:
        actual = risk.invoice_authenticity_score
        if actual is None or actual < expected.min_invoice_authenticity_score:
            failed.append(
                f"invoice_authenticity_score {actual} < min "
                f"{expected.min_invoice_authenticity_score}"
            )
    if expected.max_invoice_authenticity_score is not None:
        actual = risk.invoice_authenticity_score
        if actual is not None and actual > expected.max_invoice_authenticity_score:
            failed.append(
                f"invoice_authenticity_score {actual} > max "
                f"{expected.max_invoice_authenticity_score}"
            )

    if expected.recommended_action_in:
        if analysis.recommended_action not in expected.recommended_action_in:
            failed.append(
                f"recommended_action {analysis.recommended_action!r} not in "
                f"{list(expected.recommended_action_in)}"
            )

    if expected.behavioral_deviation_flags is not None:
        actual_flags = set(risk.behavioral_deviation_flags)
        required_flags = set(expected.behavioral_deviation_flags)
        missing = required_flags - actual_flags
        if missing:
            failed.append(
                "behavioral_deviation_flags missing required "
                f"{sorted(missing)}"
            )

    if expected.forbidden_behavioral_deviation_flags is not None:
        actual_flags = set(risk.behavioral_deviation_flags)
        forbidden_flags = set(expected.forbidden_behavioral_deviation_flags)
        violated = forbidden_flags & actual_flags
        if violated:
            failed.append(
                "behavioral_deviation_flags emitted forbidden "
                f"{sorted(violated)}"
            )

    return failed


def _aggregate(results: list[EvalCaseResult]) -> EvalReport:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    per_sub: dict[EvalSubcategory, EvalSubcategoryStats] = {}

    by_subcategory: dict[EvalSubcategory, list[EvalCaseResult]] = {}
    for result in results:
        by_subcategory.setdefault(result.case.subcategory, []).append(result)

    for subcategory, items in by_subcategory.items():
        per_sub[subcategory] = EvalSubcategoryStats(
            subcategory=subcategory,
            total=len(items),
            passed=sum(1 for r in items if r.passed),
        )

    fraud_results = [r for r in results if r.case.label == "fraud"]
    legit_results = [r for r in results if r.case.label == "legit"]

    fraud_correct = sum(1 for r in fraud_results if r.passed)
    # "False positive" = a legit case whose actual recommended_action is
    # "block" (per deep dive §4.4). "needs_review" is allowed on legit.
    legit_blocked = sum(
        1
        for r in legit_results
        if r.actual_analysis is not None
        and r.actual_analysis.recommended_action == "block"
    )

    precision = (
        fraud_correct / (fraud_correct + legit_blocked)
        if (fraud_correct + legit_blocked) > 0
        else 0.0
    )
    fpr = legit_blocked / len(legit_results) if legit_results else 0.0

    return EvalReport(
        total=total,
        passed=passed,
        per_subcategory=per_sub,
        precision_on_fraud=precision,
        false_positive_rate_on_legit=fpr,
        results=results,
    )
