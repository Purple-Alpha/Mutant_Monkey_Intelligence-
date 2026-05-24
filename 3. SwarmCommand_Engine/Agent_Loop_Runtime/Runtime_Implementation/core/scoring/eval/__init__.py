"""NorthStar Inbox Shield — Phase 1.1 fraud eval harness.

Month 2 completion machinery: the loader, runner, ``EvalReport``,
markdown-table renderer with pass-gate verdict, CLI entry point with
``--provider {anthropic,openai,xai}`` + ``--llm-safe`` mode, the full
40-case ``fraud_eval_dataset.jsonl``, and the live-client wrappers are
all in place. The remaining step is the live LLM eval-pass run itself
(``Phase_1_1_Fraud_Prevention_Deep_Dive.md`` §4.5: >=80% precision on
fraud / <=10% FPR on legit / >=60% per-subcategory recall), executed
offline per the runbook at
``4. Product_Roadmap/Live_LLM_Eval_Runbook.md`` and pasted into
``PROJECT_ACTIVITY_LOG.md``.

The harness is intentionally **not** wired into the pytest suite (would
require a live LLM in CI). Smoke testing is via
``tests/test_fraud_eval_harness.py`` against deterministic fake LLM
clients and against the lazy import surface of the live clients.
"""

from .dataset import (
    DEFAULT_DATASET_PATH,
    EvalCase,
    EvalCaseExpected,
    EvalLabel,
    EvalSubcategory,
    load_dataset,
)
from .live_client import (
    SUPPORTED_PROVIDERS,
    LiveClientImportError,
    build_anthropic_client,
    build_live_client,
    build_openai_client,
    build_xai_client,
)
from .llm_safety import (
    UNSAFE_PATTERNS,
    LLMSafeClientConfig,
    LLMSafetyError,
    LLMUsageLogEntry,
    append_usage_log_entry,
    assert_dataset_path_is_allowlisted,
    build_llm_safe_client,
    default_usage_log_path,
    read_usage_log,
    resolve_api_key,
    scan_dataset_for_unsafe_terms,
    strip_markdown_code_fences,
)
from .runner import (
    PASS_GATE_MAX_FPR_ON_LEGIT,
    PASS_GATE_MIN_PER_SUBCATEGORY_RECALL,
    PASS_GATE_MIN_PRECISION_ON_FRAUD,
    EvalCaseResult,
    EvalReport,
    EvalSubcategoryStats,
    run_eval,
)

__all__ = [
    "DEFAULT_DATASET_PATH",
    "EvalCase",
    "EvalCaseExpected",
    "EvalCaseResult",
    "EvalLabel",
    "EvalReport",
    "EvalSubcategory",
    "EvalSubcategoryStats",
    "LLMSafeClientConfig",
    "LLMSafetyError",
    "LLMUsageLogEntry",
    "LiveClientImportError",
    "PASS_GATE_MAX_FPR_ON_LEGIT",
    "PASS_GATE_MIN_PER_SUBCATEGORY_RECALL",
    "PASS_GATE_MIN_PRECISION_ON_FRAUD",
    "SUPPORTED_PROVIDERS",
    "UNSAFE_PATTERNS",
    "append_usage_log_entry",
    "assert_dataset_path_is_allowlisted",
    "build_anthropic_client",
    "build_live_client",
    "build_llm_safe_client",
    "build_openai_client",
    "build_xai_client",
    "default_usage_log_path",
    "load_dataset",
    "read_usage_log",
    "resolve_api_key",
    "run_eval",
    "scan_dataset_for_unsafe_terms",
    "strip_markdown_code_fences",
]
