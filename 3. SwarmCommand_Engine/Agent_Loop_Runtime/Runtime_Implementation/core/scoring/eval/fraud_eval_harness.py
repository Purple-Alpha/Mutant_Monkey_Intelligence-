"""CLI entry point for the Phase 1.1 fraud eval harness.

Run with: ``python -m core.scoring.eval.fraud_eval_harness``

The harness loads the shipped ``fraud_eval_dataset.jsonl``, prompts the
scoring agent's locked system prompt against each case via the
configured LLM client, computes pass/fail per case, evaluates the
Phase 1.1 deep dive §4.5 pass gate, and prints the report's markdown
table to stdout (suitable for pasting into a ``PROJECT_ACTIVITY_LOG.md``
entry per the §7.3 eval landing requirement).

The harness is intentionally not part of the regular pytest suite — it
needs a live LLM. ``--dry-run`` short-circuits the LLM call and emits a
stub passing result for each case so the harness can exercise the full
pipeline (loader -> runner -> report -> gate -> markdown) without a
live model. ``--provider {anthropic,openai,xai}`` enables the live path;
operator workflow is documented in
``4. Product_Roadmap/Live_LLM_Eval_Runbook.md``.

LLM-safe mode (default ON when ``--provider`` is set) layers three
guards on top of every live call: a dataset path allowlist check, a
dataset content scan against the same unsafe-pattern list used by the
pre-commit hook and CI workflow, and a per-call sha256 usage log under
``<dataset-dir>/operator_state/llm_usage.jsonl``. See
``6. Internal_Strategy/LLM_Workflow_Integration_Plan.md`` §C.

Diagnostic flags (``--case-id``, ``--show-failure-details``, and
``--show-raw-response``) let an operator inspect one live-model response
without spending a full 40-case run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from core.scoring.email_risk_scoring_agent import (
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
)

from .dataset import DEFAULT_DATASET_PATH, EvalCase, load_dataset
from .live_client import SUPPORTED_PROVIDERS, build_live_client
from .llm_safety import (
    LLMSafeClientConfig,
    LLMSafetyError,
    assert_dataset_path_is_allowlisted,
    build_llm_safe_client,
    default_usage_log_path,
    resolve_api_key,
    scan_dataset_for_unsafe_terms,
)
from .runner import EvalReport, run_eval

LLMClient = Callable[[str, str], str]

# Default API key env var per provider. Operators may override with
# --api-key-env if they store the key under a different name.
_DEFAULT_API_KEY_ENV: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "xai": "XAI_API_KEY",
}


def _reconfigure_stdio_to_utf8() -> None:
    """Make stdout / stderr UTF-8 so Unicode raw responses do not crash.

    Windows consoles default to cp1252; raw LLM responses for the Unicode
    obfuscation cases (`ia-003`, `ls-001`, `hi-001`) contain non-cp1252
    codepoints such as ``U+2011`` and ``U+200B``. Writing those through
    ``sys.stdout.write`` raises ``UnicodeEncodeError`` after the markdown
    table has already been emitted, truncating the raw-response block and
    obscuring exactly the data an operator needs for diagnostics.

    This helper is a best-effort fix: it calls
    ``stream.reconfigure(encoding="utf-8")`` on stdout and stderr when the
    underlying stream supports it (Python 3.7+ TextIOWrapper streams do).
    Streams that do not support reconfigure (e.g. captured streams in some
    test runners, IO wrappers, or pipes attached to non-text consumers)
    are left untouched and the original cp1252 behavior is preserved.
    """

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            # Some captured streams report a reconfigure attribute but
            # refuse the call; we silently leave those alone.
            continue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fraud_eval_harness",
        description="Run the Phase 1.1 fraud eval harness over the shipped dataset.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help=f"Path to the JSONL dataset (default: {DEFAULT_DATASET_PATH}).",
    )
    parser.add_argument(
        "--case-id",
        type=str,
        default=None,
        help=(
            "Optional single case id to run (for example vf-001). Useful for "
            "diagnosing live-model schema mismatches without running all cases."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Skip the LLM call; emit a stub passing analysis per case. Useful "
            "for verifying the harness machinery without a live model. "
            "Mutually exclusive with --provider."
        ),
    )
    parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        default=None,
        help=(
            "Live LLM provider to call (default: none, raises NotImplementedError "
            "per case). Requires the corresponding SDK to be installed."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=(
            "Model id for --provider (for example claude-sonnet-4-5, gpt-5, "
            "or grok-4). "
            "Required when --provider is set."
        ),
    )
    parser.add_argument(
        "--api-key-env",
        type=str,
        default=None,
        help=(
            "Environment variable holding the LLM API key. Defaults to "
            "ANTHROPIC_API_KEY for anthropic, OPENAI_API_KEY for openai, "
            "and XAI_API_KEY for xai."
        ),
    )
    parser.add_argument(
        "--llm-safe",
        dest="llm_safe",
        action="store_true",
        default=True,
        help=(
            "Enable LLM-safe mode (default ON): dataset path allowlist, unsafe-"
            "pattern scan, sha256 usage log."
        ),
    )
    parser.add_argument(
        "--no-llm-safe",
        dest="llm_safe",
        action="store_false",
        help=(
            "Disable LLM-safe mode. Use only for explicitly-flagged local "
            "experimentation; CI must never invoke the harness with this flag."
        ),
    )
    parser.add_argument(
        "--allow-unsafe-dataset-path",
        action="store_true",
        default=False,
        help=(
            "Bypass the dataset path allowlist. Pass only after confirming the "
            "dataset is fully synthetic."
        ),
    )
    parser.add_argument(
        "--usage-log",
        type=Path,
        default=None,
        help=(
            "Path for the LLM-safe usage log (default: "
            "<dataset-dir>/operator_state/llm_usage.jsonl)."
        ),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=None,
        help=(
            "Optional path to write the markdown report in addition to stdout. "
            "Use this to capture the report for pasting into PROJECT_ACTIVITY_LOG.md."
        ),
    )
    parser.add_argument(
        "--show-failure-details",
        action="store_true",
        default=False,
        help=(
            "Print per-case failure_reason and failed_assertions after the "
            "markdown report. Useful for diagnosing schema/parse failures."
        ),
    )
    parser.add_argument(
        "--show-raw-response",
        action="store_true",
        default=False,
        help=(
            "Print each evaluated case's raw LLM response after the report. "
            "Intended for one-case synthetic eval diagnostics; prefer with "
            "--case-id."
        ),
    )
    args = parser.parse_args(argv)

    _reconfigure_stdio_to_utf8()

    if args.dry_run and args.provider is not None:
        parser.error("--dry-run and --provider are mutually exclusive")
    if args.provider is not None and args.model is None:
        parser.error("--provider requires --model")

    try:
        cases = load_dataset(args.dataset)
    except Exception as exc:  # noqa: BLE001 - surface dataset errors clearly
        print(f"error: failed to load dataset {args.dataset}: {exc}", file=sys.stderr)
        return 2

    if args.case_id is not None:
        matching_cases = [case for case in cases if case.case_id == args.case_id]
        if not matching_cases:
            print(
                f"error: case id {args.case_id!r} not found in dataset {args.dataset}",
                file=sys.stderr,
            )
            return 2
        cases = matching_cases

    client = _resolve_client(args, cases)
    if client is None:
        return 2

    report = run_eval(cases, llm_client=client)
    markdown = report.markdown_table()
    sys.stdout.write(markdown)
    if args.show_failure_details:
        sys.stdout.write(_render_failure_details(report))
    if args.show_raw_response:
        sys.stdout.write(_render_raw_responses(report))

    if args.report_out is not None:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        report_text = markdown
        if args.show_failure_details:
            report_text += _render_failure_details(report)
        if args.show_raw_response:
            report_text += _render_raw_responses(report)
        args.report_out.write_text(report_text, encoding="utf-8")

    # Exit code semantics:
    #   0 - pass gate met (precision, FPR, per-subcategory recall)
    #   1 - pass gate failed; the report's gate verdict line says FAIL
    #   2 - configuration / safety error (printed to stderr, no report)
    return 0 if report.gate_passed else 1


def _resolve_client(
    args: argparse.Namespace, cases: list[EvalCase]
) -> LLMClient | None:
    """Build the LLM client per CLI args. Returns None on safety error."""

    if args.dry_run:
        return _build_dry_run_client()

    if args.provider is None:
        return _build_default_client()

    # Live provider path.
    if args.llm_safe:
        try:
            assert_dataset_path_is_allowlisted(
                args.dataset,
                allow_unsafe_dataset_path=args.allow_unsafe_dataset_path,
            )
            scan_dataset_for_unsafe_terms(args.dataset)
        except LLMSafetyError as exc:
            print(f"error: llm-safe guard rejected the run: {exc}", file=sys.stderr)
            return None

    env_var = args.api_key_env or _DEFAULT_API_KEY_ENV[args.provider]
    try:
        api_key = resolve_api_key(env_var)
    except LLMSafetyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None

    try:
        live_client = build_live_client(
            args.provider,
            model=args.model,
            api_key=api_key,
        )
    except Exception as exc:  # noqa: BLE001 - SDK import or builder error
        print(f"error: failed to build {args.provider} client: {exc}", file=sys.stderr)
        return None

    if not args.llm_safe:
        return live_client

    # Wrap with the LLM-safe client. The case-id provider is a closure
    # over current_case[0]; the runner does not know about the wrapper,
    # so we update the cell from a thin per-case wrapper around the
    # safe client. Keeps the runner unchanged.
    current_case: list[str | None] = [None]
    usage_log_path = args.usage_log or default_usage_log_path(args.dataset)
    config = LLMSafeClientConfig(
        usage_log_path=usage_log_path,
        required_system_prompt_prefix=NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT[:200],
        case_id_provider=lambda: current_case[0],
    )
    safe_client = build_llm_safe_client(live_client, config=config)

    # Build a tracking iterator that updates current_case in order.
    case_iter = iter(cases)

    def _tracked(system_prompt: str, user_prompt: str) -> str:
        try:
            current_case[0] = next(case_iter).case_id
        except StopIteration:
            current_case[0] = None
        return safe_client(system_prompt, user_prompt)

    return _tracked


def _build_default_client() -> LLMClient:
    """Real-LLM client placeholder when --provider is not set.

    Intentionally raises with a clear message: there is no default LLM
    provider wired in. Operators select a provider via --provider, or
    inject their own client by importing ``run_eval`` directly.
    """

    def _missing(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        raise NotImplementedError(
            "No default LLM client is wired into the fraud eval harness CLI. "
            "Use --provider {anthropic,openai,xai} --model <id>, --dry-run "
            "for a stub run, or import run_eval and inject a real client "
            "from a separate script."
        )

    return _missing


def _render_failure_details(report: EvalReport) -> str:
    """Render per-case failure details for operator diagnostics."""

    lines: list[str] = ["", "### Case Failure Details", ""]
    for result in report.results:
        lines.append(f"- `{result.case.case_id}`: {'PASS' if result.passed else 'FAIL'}")
        if result.failure_reason is not None:
            lines.append(f"  - failure_reason: `{result.failure_reason}`")
        for assertion in result.failed_assertions:
            lines.append(f"  - assertion: `{assertion}`")
    return "\n".join(lines) + "\n"


def _render_raw_responses(report: EvalReport) -> str:
    """Render raw LLM responses for inspected synthetic eval cases."""

    lines: list[str] = ["", "### Raw LLM Responses", ""]
    for result in report.results:
        lines.append(f"#### {result.case.case_id}")
        lines.append("")
        lines.append("```json")
        lines.append(result.raw_response)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def _build_dry_run_client() -> LLMClient:
    """Stub client that returns a valid passing analysis for any input."""

    stub = {
        "summary": "dry-run stub analysis",
        "action_items": [],
        "risk_analysis": {
            "risk_score": 50,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "medium",
            "vendor_fraud_score": 50,
            "wire_transfer_anomaly_score": 50,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [],
        },
        "impersonation_analysis": {
            "impersonation_likelihood": 50,
            "suspicious_elements": [],
            "sender_legitimacy_notes": None,
        },
        "recommended_action": "needs_review",
    }
    payload = json.dumps(stub)

    def _client(system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        return payload

    return _client


def _case_summary(case: EvalCase) -> str:  # pragma: no cover - helper
    return f"{case.case_id} ({case.label}/{case.subcategory})"


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
