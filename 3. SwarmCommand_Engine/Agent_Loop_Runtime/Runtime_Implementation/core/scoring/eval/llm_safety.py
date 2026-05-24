"""LLM-safe mode for the Phase 1.1 fraud eval harness.

This module is the runtime side of vector C in
``6. Internal_Strategy/LLM_Workflow_Integration_Plan.md``. It exists so
that any live LLM invocation through ``fraud_eval_harness`` is wrapped in
three procedural guards before the call goes over the wire:

1. The dataset's text content is scanned for the same blocklist used by
   ``Internal_Tools/precommit_llm_safety_hook.sh`` and
   ``.github/workflows/llm_safety_check.yml``. Hits raise
   ``LLMSafetyError`` so a misformatted or accidentally-real dataset
   never reaches the model.
2. The dataset path must pass a deliberate path allowlist check; paths
   whose components look like they may point at real customer or
   production data (``customer``, ``production``, ``real_email``, etc.)
   are rejected unless the caller passes ``allow_unsafe_dataset_path=True``.
3. Every LLM call routed through :func:`build_llm_safe_client` is
   appended to a JSON Lines usage log (default sibling of the dataset)
   with sha256 digests of the prompts and response, the timestamp, and
   the exit status. Real prompt / response bodies are intentionally not
   persisted so the usage log is safe to share.

The shipped :data:`UNSAFE_PATTERNS` list must stay byte-identical to the
two shell scanners (see plan §A↔B↔C synchronization rule). The
synchronization is procedural — there is no shared source of truth that
all three can import.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

LLMClient = Callable[[str, str], str]


class LLMSafetyError(RuntimeError):
    """Raised when an LLM-safe guard refuses to proceed."""


UNSAFE_PATTERNS: tuple[str, ...] = (
    "reverse shell",
    "keylogger",
    "botnet",
    "ddos attack",
    "ransomware payload",
    "ransomware builder",
    "exploit this server",
    "how do i hack",
)
"""Case-insensitive substrings that block an LLM call when found in the dataset.

Kept narrow on purpose so NorthStar's product space (ransomware *defense*)
is not blocked. To add or remove a term, update all three scanners in the
same commit:

- ``Internal_Tools/precommit_llm_safety_hook.sh`` (``UNSAFE_PATTERNS`` array)
- ``.github/workflows/llm_safety_check.yml`` (``UNSAFE_PATTERNS`` array)
- this module (``UNSAFE_PATTERNS`` tuple)

and log the reason in ``PROJECT_ACTIVITY_LOG.md``.
"""

_UNSAFE_PATH_COMPONENTS: tuple[str, ...] = (
    "customer",
    "customers",
    "production",
    "prod_",
    "live_email",
    "live_emails",
    "real_email",
    "real_emails",
    "real-emails",
    "tenant_data",
    "tenant-data",
)
"""Path-segment substrings that flag a dataset path as possibly non-synthetic.

A match raises ``LLMSafetyError`` unless ``allow_unsafe_dataset_path=True``
is explicitly passed. Matching is case-insensitive and substring-based on
each path component, so ``./customer_emails.jsonl`` and
``/var/data/Production/dataset.jsonl`` both trip.
"""


@dataclass(frozen=True)
class LLMUsageLogEntry:
    """One row in the LLM usage log.

    Prompt and response bodies are NOT persisted — only their sha256
    digests — so the usage log is safe to commit, share, or attach to an
    audit packet without leaking dataset content or model output.
    """

    at: datetime
    case_id: str | None
    system_prompt_sha256: str
    user_prompt_sha256: str
    response_sha256: str | None
    response_bytes: int | None
    status: str
    error: str | None = None


@dataclass(frozen=True)
class LLMSafeClientConfig:
    """Configuration for :func:`build_llm_safe_client`.

    ``required_system_prompt_prefix`` enforces defense-in-depth on the
    runner: even if the runner is ever refactored to drop the locked
    scoring prompt, the wrapper still refuses to forward an LLM call
    that does not begin with the expected prefix.
    """

    usage_log_path: Path
    required_system_prompt_prefix: str
    case_id_provider: Callable[[], str | None] = field(default=lambda: None)


def default_usage_log_path(dataset_path: Path) -> Path:
    """Return the default usage-log location for ``dataset_path``.

    Lands the JSONL log under ``<dataset-dir>/operator_state/llm_usage.jsonl``
    so the eval module owns its own audit trail and the existing
    ``core/operator_state/`` kill-switch audit is untouched.
    """

    return dataset_path.parent / "operator_state" / "llm_usage.jsonl"


def _candidate_dotenv_paths() -> Iterable[Path]:
    """Yield likely project-level ``.env`` files without leaving the workspace."""

    seen: set[Path] = set()
    anchors = (Path.cwd(), Path(__file__).resolve())
    for anchor in anchors:
        current = anchor if anchor.is_dir() else anchor.parent
        for parent in (current, *current.parents):
            path = parent / ".env"
            if path not in seen:
                seen.add(path)
                yield path


def _parse_dotenv_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _resolve_dotenv_key(env_var: str) -> str | None:
    """Return ``env_var`` from the nearest ``.env`` file, if present."""

    if os.environ.get("NORTHSTAR_LLM_DISABLE_DOTENV") == "1":
        return None

    for path in _candidate_dotenv_paths():
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, raw_value = line.split("=", 1)
                if key.strip() == env_var:
                    value = _parse_dotenv_value(raw_value)
                    return value or None
    return None


def assert_dataset_path_is_allowlisted(
    dataset_path: Path,
    *,
    allow_unsafe_dataset_path: bool = False,
) -> None:
    """Raise ``LLMSafetyError`` if ``dataset_path`` looks possibly non-synthetic.

    Allowlist policy: a path is allowed if no path component contains
    any string from :data:`_UNSAFE_PATH_COMPONENTS` (case-insensitive).
    Operators may bypass this with ``allow_unsafe_dataset_path=True`` for
    audited extended datasets.
    """

    if allow_unsafe_dataset_path:
        return

    resolved = dataset_path.expanduser()
    for part in resolved.parts:
        lowered = part.lower()
        for component in _UNSAFE_PATH_COMPONENTS:
            if component in lowered:
                raise LLMSafetyError(
                    f"dataset path component {part!r} matches the unsafe "
                    f"path allowlist substring {component!r}. Pass "
                    "allow_unsafe_dataset_path=True only after confirming "
                    "the dataset is fully synthetic."
                )


def scan_dataset_for_unsafe_terms(
    dataset_path: Path,
    *,
    extra_patterns: Sequence[str] = (),
) -> None:
    """Scan ``dataset_path`` for any of :data:`UNSAFE_PATTERNS` (plus extras).

    Reads the file as UTF-8 text and runs a case-insensitive substring
    search. Raises ``LLMSafetyError`` listing every (line_number, pattern)
    hit. A missing file raises ``LLMSafetyError`` rather than silently
    passing the scan.
    """

    if not dataset_path.exists():
        raise LLMSafetyError(f"dataset path does not exist: {dataset_path}")

    combined_patterns = tuple(UNSAFE_PATTERNS) + tuple(p.lower() for p in extra_patterns)
    hits: list[str] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            lowered = raw_line.lower()
            for pattern in combined_patterns:
                if pattern in lowered:
                    hits.append(f"line {line_number}: pattern {pattern!r}")

    if hits:
        formatted = "; ".join(hits)
        raise LLMSafetyError(
            f"unsafe-pattern scan failed on {dataset_path}: {formatted}"
        )


def append_usage_log_entry(path: Path, entry: LLMUsageLogEntry) -> None:
    """Append one usage-log row as a JSON line.

    Creates the parent directory if missing. Timestamp is serialized via
    ``isoformat()`` to preserve tzinfo (UTC by convention).
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "at": entry.at.isoformat(),
        "case_id": entry.case_id,
        "system_prompt_sha256": entry.system_prompt_sha256,
        "user_prompt_sha256": entry.user_prompt_sha256,
        "response_sha256": entry.response_sha256,
        "response_bytes": entry.response_bytes,
        "status": entry.status,
        "error": entry.error,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_usage_log(path: Path) -> list[dict]:
    """Read the usage log back as a list of dicts (chronological order)."""

    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise LLMSafetyError(
                    f"usage log line {line_number} is not valid JSON: {exc.msg}"
                ) from exc
    return rows


def build_llm_safe_client(
    inner_client: LLMClient,
    *,
    config: LLMSafeClientConfig,
) -> LLMClient:
    """Wrap ``inner_client`` so every call is guarded and audit-logged.

    The wrapper:

    1. Asserts ``system_prompt`` starts with
       ``config.required_system_prompt_prefix`` (defense in depth — if
       the runner is ever changed to drop the locked scoring prompt,
       the wrapper still refuses).
    2. Forwards the call to ``inner_client``.
    3. Appends a row to ``config.usage_log_path`` with sha256 digests
       (not raw content) of the prompts and response, the timestamp,
       the case id from ``config.case_id_provider()`` if available, and
       the resulting status (``ok`` / ``error:<name>``).
    4. Re-raises any exception from ``inner_client`` after logging.

    The case-id provider is a callable so the runner can update it once
    per case via a closure-bound variable; the wrapper itself stays
    case-agnostic.
    """

    usage_log = config.usage_log_path
    prefix = config.required_system_prompt_prefix
    case_id_provider = config.case_id_provider

    def _safe(system_prompt: str, user_prompt: str) -> str:
        if not system_prompt.startswith(prefix):
            raise LLMSafetyError(
                "system prompt does not start with the required locked-prefix; "
                "refusing to forward LLM call. The runner must pass "
                "NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT verbatim."
            )

        system_sha = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
        user_sha = hashlib.sha256(user_prompt.encode("utf-8")).hexdigest()
        case_id = case_id_provider()

        try:
            response = inner_client(system_prompt, user_prompt)
        except Exception as exc:  # noqa: BLE001 - intentional broad logging surface
            append_usage_log_entry(
                usage_log,
                LLMUsageLogEntry(
                    at=datetime.now(timezone.utc),
                    case_id=case_id,
                    system_prompt_sha256=system_sha,
                    user_prompt_sha256=user_sha,
                    response_sha256=None,
                    response_bytes=None,
                    status=f"error:{type(exc).__name__}",
                    error=str(exc),
                ),
            )
            raise

        response_bytes = len(response.encode("utf-8"))
        response_sha = hashlib.sha256(response.encode("utf-8")).hexdigest()
        append_usage_log_entry(
            usage_log,
            LLMUsageLogEntry(
                at=datetime.now(timezone.utc),
                case_id=case_id,
                system_prompt_sha256=system_sha,
                user_prompt_sha256=user_sha,
                response_sha256=response_sha,
                response_bytes=response_bytes,
                status="ok",
                error=None,
            ),
        )
        return response

    return _safe


# Markdown code-fence stripping helper. LLMs commonly wrap JSON output in
# ``` blocks even when asked for raw JSON; the eval runner expects raw
# JSON, so we strip leading / trailing fences before handing the body
# back. Kept here (rather than in live_client.py) because it is reused
# by any client wrapper that wants to be defensive.
_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json|JSON)?\s*\n?(?P<body>.*?)\n?\s*```\s*$",
    flags=re.DOTALL,
)


def strip_markdown_code_fences(text: str) -> str:
    """Return ``text`` with one leading / trailing triple-backtick fence stripped.

    If no fence is found, returns ``text`` unchanged. Only a single
    surrounding fence is removed; nested fences are left alone so the
    eval reports them as schema_mismatch rather than silently swallowing
    structure.
    """

    match = _FENCE_PATTERN.match(text)
    if match is None:
        return text
    return match.group("body")


def resolve_api_key(env_var: str) -> str:
    """Return the API key in ``env_var`` or raise ``LLMSafetyError``.

    Centralized so callers do not silently send empty-string keys
    upstream and so the failure message names the env var the operator
    should set.
    """

    value = os.environ.get(env_var) or _resolve_dotenv_key(env_var)
    if not value:
        raise LLMSafetyError(
            f"API key env var {env_var!r} is not set. Export it in the "
            "shell or place it in the workspace root .env before running "
            "the live eval."
        )
    return value


def iter_unsafe_patterns() -> Iterable[str]:
    """Iterate the locked unsafe-pattern list (helper for tests / docs)."""

    return iter(UNSAFE_PATTERNS)
