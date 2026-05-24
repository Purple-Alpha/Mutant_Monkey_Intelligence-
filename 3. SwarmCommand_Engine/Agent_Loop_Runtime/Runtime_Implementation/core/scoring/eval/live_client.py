"""Live-LLM client builders for the Phase 1.1 fraud eval harness.

Three providers are supported out of the box:

- ``anthropic`` via the official ``anthropic`` Python SDK
- ``openai`` via the official ``openai`` Python SDK
- ``xai`` via the ``openai`` Python SDK pointed at xAI's
  OpenAI-compatible Grok endpoint (``https://api.x.ai/v1``)

All SDKs are imported lazily inside the builder so the runtime baseline
test suite never needs them installed. The CLI surface that wires these
in lives in ``fraud_eval_harness.py``; here we only define the call
shape.

Each builder returns a ``Callable[[str, str], str]`` matching the
harness contract: ``(system_prompt, user_prompt) -> raw_json_string``.
The locked scoring prompt is passed by the runner; the wrappers do not
override it. All wrappers strip a single surrounding markdown
code-fence from the response because LLMs commonly wrap JSON in
``` blocks even when asked for raw JSON.
"""

from __future__ import annotations

from typing import Callable

from .llm_safety import strip_markdown_code_fences

LLMClient = Callable[[str, str], str]


class LiveClientImportError(ImportError):
    """Raised when an LLM provider SDK is not installed on the operator machine."""


def build_anthropic_client(
    *,
    model: str,
    api_key: str,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> LLMClient:
    """Return an LLM client backed by the Anthropic Messages API.

    ``model`` is the model id (for example ``claude-sonnet-4-5``).
    ``api_key`` is the Anthropic API key, typically resolved from
    ``ANTHROPIC_API_KEY`` via ``llm_safety.resolve_api_key``.
    ``temperature`` defaults to 0.0 so the eval run is as deterministic
    as the provider allows. ``max_tokens`` is sized to comfortably hold
    the worked-example JSON responses from the deep dive (~600 tokens
    each) with headroom.
    """

    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised on operator machines
        raise LiveClientImportError(
            "The 'anthropic' package is not installed. Install it with "
            "'pip install anthropic' before running the live eval against "
            "Anthropic models."
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)

    def _call(system_prompt: str, user_prompt: str) -> str:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Anthropic returns a list of content blocks; for plain text
        # responses the first block is a TextBlock with .text. We
        # concatenate text blocks so partial / multi-block responses
        # are not silently truncated.
        parts: list[str] = []
        for block in message.content:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(text)
        raw = "".join(parts).strip()
        return strip_markdown_code_fences(raw)

    return _call


def build_openai_client(
    *,
    model: str,
    api_key: str,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> LLMClient:
    """Return an LLM client backed by the OpenAI Chat Completions API.

    Uses ``response_format={"type": "json_object"}`` so the model is
    nudged into emitting valid JSON. The wrapper still defensively
    strips markdown fences from the response.
    """

    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised on operator machines
        raise LiveClientImportError(
            "The 'openai' package is not installed. Install it with "
            "'pip install openai' before running the live eval against "
            "OpenAI models."
        ) from exc

    client = OpenAI(api_key=api_key)

    def _call(system_prompt: str, user_prompt: str) -> str:
        completion = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = completion.choices[0]
        raw = (choice.message.content or "").strip()
        return strip_markdown_code_fences(raw)

    return _call


XAI_DEFAULT_BASE_URL: str = "https://api.x.ai/v1"


def build_xai_client(
    *,
    model: str,
    api_key: str,
    max_tokens: int = 4096,
    temperature: float = 0.0,
    base_url: str = XAI_DEFAULT_BASE_URL,
) -> LLMClient:
    """Return an LLM client backed by xAI's OpenAI-compatible Grok API.

    xAI exposes a wire-compatible OpenAI Chat Completions endpoint at
    ``https://api.x.ai/v1``, so this wrapper reuses the ``openai`` Python
    SDK with a custom ``base_url``. ``response_format`` is intentionally
    **not** sent because not every Grok model supports strict JSON mode
    on this endpoint; the locked system prompt instructs JSON output and
    :func:`strip_markdown_code_fences` handles fenced wrappers.

    ``model`` is the Grok model id (for example ``grok-4`` or
    ``grok-4-fast-reasoning``). ``api_key`` is the xAI API key, typically
    resolved from ``XAI_API_KEY`` via :func:`llm_safety.resolve_api_key`.
    ``temperature`` defaults to 0.0 so the eval run is as deterministic
    as the provider allows.
    """

    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised on operator machines
        raise LiveClientImportError(
            "The 'openai' package is not installed. Install it with "
            "'pip install openai' before running the live eval against "
            "xAI / Grok models (the xai provider uses the OpenAI-compatible "
            "client against https://api.x.ai/v1)."
        ) from exc

    client = OpenAI(api_key=api_key, base_url=base_url)

    def _call(system_prompt: str, user_prompt: str) -> str:
        completion = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        choice = completion.choices[0]
        raw = (choice.message.content or "").strip()
        return strip_markdown_code_fences(raw)

    return _call


SUPPORTED_PROVIDERS: tuple[str, ...] = ("anthropic", "openai", "xai")


def build_live_client(
    provider: str,
    *,
    model: str,
    api_key: str,
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> LLMClient:
    """Dispatch to the per-provider builder.

    Raises ``ValueError`` for any provider outside
    :data:`SUPPORTED_PROVIDERS` so a typo in the CLI surface fails loud.
    """

    if provider == "anthropic":
        return build_anthropic_client(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider == "openai":
        return build_openai_client(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider == "xai":
        return build_xai_client(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    raise ValueError(
        f"Unknown LLM provider {provider!r}. Supported: {SUPPORTED_PROVIDERS}."
    )
